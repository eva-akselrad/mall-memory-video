from __future__ import annotations

import random
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
    zoom_end: float,
    seed: int,
) -> None:
    """Fast Ken Burns segment via ffmpeg zoompan (much faster than Python per-frame)."""
    frames = max(1, int(round(duration * fps)))
    z_step = (zoom_end - 1.0) / max(1, frames - 1)
    rng = random.Random(seed)
    pan_px = int(rng.uniform(-30, 30))

    # Cover-scale, then zoompan from 1.0 → zoom_end with slight horizontal pan.
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan=z='min(zoom+{z_step:.6f},{zoom_end})':"
        f"x='iw/2-(iw/zoom/2)+{pan_px}*on/{frames}':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={width}x{height}:fps={fps},"
        f"eq=brightness=0.03:saturation=0.85"
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
