from __future__ import annotations

from pathlib import Path

import numpy as np
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
) -> Path:
    preset = PRESETS.get(style, PRESETS["proper-people"])
    duration = seconds_per_image if seconds_per_image is not None else preset.seconds_per_image
    crossfade = crossfade_seconds if crossfade_seconds is not None else preset.crossfade_seconds

    image_paths = discover_images(images_dir, sort=sort)
    clips: list[VideoClip] = []

    for index, path in enumerate(image_paths):
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

    video = concatenate_videoclips(clips, method="compose", padding=-crossfade)
    audio = _prepare_audio(music_path, video.duration)
    final = video.with_audio(audio)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )

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
