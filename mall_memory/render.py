from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
from proglog import ProgressBarLogger
from moviepy import (
    AudioFileClip,
    VideoClip,
    VideoFileClip,
    concatenate_audioclips,
    concatenate_videoclips,
)
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut
from moviepy.video.fx import CrossFadeIn

from mall_memory.effects import (
    PRESETS,
    KenBurnsSlide,
    StylePreset,
    apply_grade,
    load_image_rgb,
)
from mall_memory.ffmpeg_slides import render_slide_video
from mall_memory.images import discover_images
from mall_memory.log_config import get_logger
from mall_memory.music import resolve_music_paths

log = get_logger("render")

ProgressCallback = Callable[[str, float], None]


class _EncodeProgressLogger(ProgressBarLogger):
    """Feeds moviepy/ffmpeg encode progress into a 0–1 float callback."""

    def __init__(self, on_fraction: Callable[[float], None]) -> None:
        super().__init__()
        self._on_fraction = on_fraction
        self._last_logged_pct = -1

    def bars_callback(self, bar, attr, value, old_value=None) -> None:
        total = self.bars[bar].get("total")
        if not total:
            return
        if attr not in ("index", "value"):
            return
        frac = min(1.0, max(0.0, float(value) / float(total)))
        pct = int(frac * 100)
        if pct >= self._last_logged_pct + 5 or pct == 100:
            log.info("Encoding: %d%% (%s)", pct, bar)
            self._last_logged_pct = pct
        self._on_fraction(frac)


def build_video(
    images_dir: Path,
    music_path: Path,
    output_path: Path,
    *,
    style: str = "proper-people",
    sort: str = "name",
    music_sort: str = "name",
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
    seconds_per_image: float | None = None,
    crossfade_seconds: float | None = None,
    on_progress: ProgressCallback | None = None,
) -> Path:
    last_phase = ""

    def progress(phase: str, amount: float) -> None:
        nonlocal last_phase
        if phase != last_phase:
            log.info("Phase: %s (%d%%)", phase, int(min(1.0, max(0.0, amount)) * 100))
            last_phase = phase
        if on_progress:
            on_progress(phase, min(1.0, max(0.0, amount)))

    log.info(
        "Starting export → %s (%dx%d @ %d fps, style=%s)",
        output_path,
        width,
        height,
        fps,
        style,
    )
    log.info("Images: %s | Music: %s", images_dir, music_path)

    preset = PRESETS.get(style, PRESETS["proper-people"])
    duration = seconds_per_image if seconds_per_image is not None else preset.seconds_per_image
    crossfade = crossfade_seconds if crossfade_seconds is not None else preset.crossfade_seconds

    progress("loading", 0.02)
    image_paths = discover_images(images_dir, sort=sort)
    log.info(
        "Found %d photos (sort=%s, %.2fs each, %.2fs crossfade)",
        len(image_paths),
        sort,
        duration,
        crossfade,
    )
    clips: list[VideoClip] = []
    temp_dir = Path(tempfile.mkdtemp(prefix="mall-memory-slides-"))
    log.info("Rendering slides with ffmpeg (temp: %s)", temp_dir)

    try:
        for index, path in enumerate(image_paths):
            log.info("Slide %d/%d: %s", index + 1, len(image_paths), path.name)
            progress("slides", 0.05 + 0.55 * (index / max(1, len(image_paths))))
            seed = index * 131 + hash(path.name) % 10_000
            segment = temp_dir / f"slide_{index:04d}.mp4"
            try:
                render_slide_video(
                    path,
                    segment,
                    duration=duration,
                    fps=fps,
                    width=width,
                    height=height,
                    zoom_end=preset.zoom_end,
                    seed=seed,
                )
                clip = VideoFileClip(str(segment))
            except (subprocess.CalledProcessError, OSError) as exc:
                log.warning("ffmpeg failed for %s (%s), using Python renderer", path.name, exc)
                clip = _python_slide_clip(
                    path, index, duration, fps, width, height, preset, seed
                )
            if index > 0 and crossfade > 0:
                clip = clip.with_effects([CrossFadeIn(crossfade)])
            clips.append(clip)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

    progress("slides", 0.62)
    log.info("Concatenating %d clips", len(clips))
    video = concatenate_videoclips(clips, method="compose", padding=-crossfade)
    log.info("Video timeline: %.2fs", video.duration)
    progress("audio", 0.68)
    audio = _prepare_audio(music_path, video.duration, sort=music_sort)
    final = video.with_audio(audio)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame_count = max(1, int(round(video.duration * fps)))
    log.info(
        "Encoding H.264/AAC -> %s (~%d frames, %.1f min of video; may take several minutes)",
        output_path,
        frame_count,
        video.duration / 60.0,
    )
    encode_logger = _EncodeProgressLogger(
        lambda frac: progress("encoding", 0.7 + 0.3 * frac)
    )
    progress("encoding", 0.7)

    stop_heartbeat = threading.Event()

    def _encoding_heartbeat() -> None:
        started = time.monotonic()
        while not stop_heartbeat.wait(20.0):
            elapsed = time.monotonic() - started
            log.info("Still encoding… %.1f min elapsed", elapsed / 60.0)

    heartbeat = threading.Thread(target=_encoding_heartbeat, daemon=True)
    heartbeat.start()
    try:
        final.write_videofile(
            str(output_path),
            fps=fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4,
            logger=encode_logger,
        )
    finally:
        stop_heartbeat.set()
    progress("done", 1.0)
    log.info("Finished: %s (%.2fs)", output_path, video.duration)

    video.close()
    audio.close()
    final.close()
    for clip in clips:
        clip.close()
    shutil.rmtree(temp_dir, ignore_errors=True)

    return output_path


def _python_slide_clip(
    path: Path,
    index: int,
    duration: float,
    fps: int,
    width: int,
    height: int,
    preset: StylePreset,
    seed: int,
) -> VideoClip:
    base = load_image_rgb(path)
    slide = KenBurnsSlide.from_image(
        base, duration, width, height, preset.zoom_end, seed
    )

    def make_frame(t, kb=slide, idx=index):
        frame = kb.frame_at(t)
        frame_index = int(t * fps) + idx * 10_000
        graded = apply_grade(
            frame,
            preset.saturation,
            preset.warmth,
            preset.shadow_lift,
            preset.vignette,
            preset.grain,
            frame_index,
        )
        return (np.clip(graded, 0.0, 1.0) * 255).astype(np.uint8)

    return VideoClip(make_frame, duration=duration).with_fps(fps)


def _prepare_audio(music_source: Path, video_duration: float, *, sort: str = "name") -> AudioFileClip:
    track_paths = resolve_music_paths(music_source, sort=sort)
    if music_source.is_dir():
        log.info("Music folder: %d track(s) (sort=%s)", len(track_paths), sort)
    else:
        log.info("Music file: %s", track_paths[0].name)

    parts: list[AudioFileClip] = []
    total = 0.0
    playlist_pass = 0

    # Play tracks in order; repeat the playlist if the slideshow runs longer.
    while total < video_duration:
        playlist_pass += 1
        if playlist_pass > 1:
            log.info("Playlist pass %d (audio %.1fs / video %.1fs)", playlist_pass, total, video_duration)
        progressed = False
        for path in track_paths:
            clip = AudioFileClip(str(path))
            parts.append(clip)
            log.info("  + %s (%.1fs)", path.name, clip.duration)
            total += clip.duration
            progressed = True
            if total >= video_duration:
                break
        if not progressed:
            break

    if not parts:
        raise ValueError(f"No playable audio at: {music_source}")

    log.info("Audio timeline: %.2fs for %.2fs video", total, video_duration)
    audio = concatenate_audioclips(parts)
    if audio.duration > video_duration:
        audio = audio.subclipped(0, video_duration)

    fade_in = min(2.5, video_duration * 0.08)
    fade_out = min(4.0, video_duration * 0.12)
    audio = audio.with_effects([AudioFadeIn(fade_in), AudioFadeOut(fade_out)])
    return audio.with_volume_scaled(0.85)


def list_presets() -> list[StylePreset]:
    return list(PRESETS.values())
