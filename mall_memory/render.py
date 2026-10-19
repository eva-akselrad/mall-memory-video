from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
from proglog import ProgressBarLogger
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips
from moviepy.audio.fx import AudioFadeIn, AudioFadeOut
from moviepy.video.fx import CrossFadeIn

from mall_memory.effects import (
    PRESETS,
    StylePreset,
    apply_grade,
    ken_burns_crop,
    load_image_rgb,
)
from mall_memory.images import discover_images

ProgressCallback = Callable[[str, float], None]


class _EncodeProgressLogger(ProgressBarLogger):
    """Feeds moviepy/ffmpeg encode progress into a 0–1 float callback."""

    def __init__(self, on_fraction: Callable[[float], None]) -> None:
        super().__init__()
        self._on_fraction = on_fraction

    def bars_callback(self, bar, attr, value, old_value=None) -> None:
        total = self.bars[bar].get("total")
        if total and attr == "index":
            self._on_fraction(min(1.0, max(0.0, float(value) / float(total))))


def build_video(
    images_dir: Path,
    music_path: Path,
    output_path: Path,
    *,
    style: str = "proper-people",
    sort: str = "name",
    width: int = 1920,
    height: int = 1080,
    fps: int = 24,
    seconds_per_image: float | None = None,
    crossfade_seconds: float | None = None,
    on_progress: ProgressCallback | None = None,
) -> Path:
    def progress(phase: str, amount: float) -> None:
        if on_progress:
            on_progress(phase, min(1.0, max(0.0, amount)))

    preset = PRESETS.get(style, PRESETS["proper-people"])
    duration = seconds_per_image if seconds_per_image is not None else preset.seconds_per_image
    crossfade = crossfade_seconds if crossfade_seconds is not None else preset.crossfade_seconds

    progress("loading", 0.02)
    image_paths = discover_images(images_dir, sort=sort)
    clips: list[VideoClip] = []

    for index, path in enumerate(image_paths):
        progress("slides", 0.05 + 0.55 * (index / max(1, len(image_paths))))
        base = load_image_rgb(path)
        seed = index * 131 + hash(path.name) % 10_000

        def make_frame(t, img=base, idx=index):
            frame = ken_burns_crop(
                img,
                t,
                duration,
                width,
                height,
                preset.zoom_end,
                seed,
            )
            frame_index = int(t * fps) + idx * 10_000
            return apply_grade(
                frame,
                preset.saturation,
                preset.warmth,
                preset.shadow_lift,
                preset.vignette,
                preset.grain,
                frame_index,
            )

        clip = VideoClip(make_frame, duration=duration).with_fps(fps)
        if index > 0 and crossfade > 0:
            clip = clip.with_effects([CrossFadeIn(crossfade)])
        clips.append(clip)

    progress("slides", 0.62)
    video = concatenate_videoclips(clips, method="compose", padding=-crossfade)
    progress("audio", 0.68)
    audio = _prepare_audio(music_path, video.duration)
    final = video.with_audio(audio)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    encode_logger = _EncodeProgressLogger(
        lambda frac: progress("encoding", 0.7 + 0.3 * frac)
    )
    progress("encoding", 0.7)
    final.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=encode_logger,
    )
    progress("done", 1.0)

    video.close()
    audio.close()
    final.close()
    for clip in clips:
        clip.close()

    return output_path


def _prepare_audio(music_path: Path, video_duration: float) -> AudioFileClip:
    if not music_path.is_file():
        raise FileNotFoundError(f"Music file not found: {music_path}")

    audio = AudioFileClip(str(music_path))
    if audio.duration > video_duration:
        audio = audio.subclipped(0, video_duration)
    elif audio.duration < video_duration:
        loops = int(np.ceil(video_duration / audio.duration))
        from moviepy import concatenate_audioclips

        audio = concatenate_audioclips([audio] * loops).subclipped(0, video_duration)

    fade_in = min(2.5, video_duration * 0.08)
    fade_out = min(4.0, video_duration * 0.12)
    audio = audio.with_effects([AudioFadeIn(fade_in), AudioFadeOut(fade_out)])
    return audio.with_volume_scaled(0.85)


def list_presets() -> list[StylePreset]:
    return list(PRESETS.values())
