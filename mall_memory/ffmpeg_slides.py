from __future__ import annotations

import subprocess
from pathlib import Path

from mall_memory.log_config import get_logger

log = get_logger("ffmpeg")


def render_slide_video(
    image_path: Path,
    output_path: Path,
    *,
    duration: float,
    fps: int,
    width: int,
    height: int,
) -> None:
    """Static hold — scale to fit frame, no zoom, color, or motion."""
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-loop",
        "1",
        "-i",
        str(image_path),
        "-vf",
        vf,
        "-t",
        f"{duration:.3f}",
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(output_path),
    ]
    log.debug("ffmpeg slide: %s", image_path.name)
    subprocess.run(cmd, check=True, capture_output=True)
