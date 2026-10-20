from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps


@dataclass(frozen=True)
class StylePreset:
    """Timing presets only — images are shown as-is (no zoom, grade, or shake)."""

    name: str
    seconds_per_image: float
    crossfade_seconds: float


PRESETS: dict[str, StylePreset] = {
    "proper-people": StylePreset(
        name="proper-people",
        seconds_per_image=6.5,
        crossfade_seconds=1.25,
    ),
    "neon-mall": StylePreset(
        name="neon-mall",
        seconds_per_image=5.0,
        crossfade_seconds=0.9,
    ),
}


def load_image_rgb(path) -> np.ndarray:
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        return np.asarray(img, dtype=np.uint8)


def fit_image_to_frame(image: np.ndarray, out_w: int, out_h: int) -> np.ndarray:
    """Letterbox to output size — no crop, no color changes."""
    ih, iw = image.shape[:2]
    scale = min(out_w / iw, out_h / ih)
    nw = max(1, int(round(iw * scale)))
    nh = max(1, int(round(ih * scale)))
    pil = Image.fromarray(image)
    resized = pil.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (out_w, out_h), (0, 0, 0))
    canvas.paste(resized, ((out_w - nw) // 2, (out_h - nh) // 2))
    return np.asarray(canvas, dtype=np.uint8)
