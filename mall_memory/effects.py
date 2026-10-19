from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps


@dataclass(frozen=True)
class StylePreset:
    name: str
    seconds_per_image: float
    crossfade_seconds: float
    zoom_end: float
    saturation: float
    warmth: float
    shadow_lift: float
    vignette: float
    grain: float


PRESETS: dict[str, StylePreset] = {
    "proper-people": StylePreset(
        name="proper-people",
        seconds_per_image=6.5,
        crossfade_seconds=1.25,
        zoom_end=1.09,
        saturation=0.82,
        warmth=-0.03,
        shadow_lift=0.06,
        vignette=0.35,
        grain=0.018,
    ),
    "neon-mall": StylePreset(
        name="neon-mall",
        seconds_per_image=5.0,
        crossfade_seconds=0.9,
        zoom_end=1.12,
        saturation=0.95,
        warmth=0.02,
        shadow_lift=0.04,
        vignette=0.28,
        grain=0.012,
    ),
}


def load_image_rgb(path) -> np.ndarray:
    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGB")
        return np.asarray(img, dtype=np.float32) / 255.0


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def ken_burns_crop(
    image: np.ndarray,
    t: float,
    duration: float,
    out_w: int,
    out_h: int,
    zoom_end: float,
    seed: int,
) -> np.ndarray:
    rng = random.Random(seed)
    ih, iw = image.shape[:2]

    pan_x = rng.uniform(-0.04, 0.04)
    pan_y = rng.uniform(-0.03, 0.03)
    progress = 0.0 if duration <= 0 else min(1.0, max(0.0, t / duration))

    scale = _lerp(1.0, zoom_end, progress)
    crop_w = out_w / scale
    crop_h = out_h / scale

    max_x = max(0.0, iw - crop_w)
    max_y = max(0.0, ih - crop_h)
    start_x = max_x * (0.5 + pan_x)
    start_y = max_y * (0.5 + pan_y)
    end_x = max_x * (0.5 - pan_x * 0.6)
    end_y = max_y * (0.5 - pan_y * 0.6)

    x0 = int(_lerp(start_x, end_x, progress))
    y0 = int(_lerp(start_y, end_y, progress))
    x1 = int(min(iw, x0 + crop_w))
    y1 = int(min(ih, y0 + crop_h))

    crop = image[y0:y1, x0:x1]
    if crop.size == 0:
        crop = image

    pil = Image.fromarray((crop * 255).astype(np.uint8))
    pil = pil.resize((out_w, out_h), Image.Resampling.LANCZOS)
    return np.asarray(pil, dtype=np.float32) / 255.0


def apply_grade(
    frame: np.ndarray,
    saturation: float,
    warmth: float,
    shadow_lift: float,
    vignette: float,
    grain: float,
    frame_index: int,
) -> np.ndarray:
    out = frame.copy()

    gray = out.mean(axis=2, keepdims=True)
    out = gray + (out - gray) * saturation

    out[..., 0] = np.clip(out[..., 0] + warmth, 0.0, 1.0)
    out[..., 2] = np.clip(out[..., 2] - warmth * 0.7, 0.0, 1.0)

    out = out * (1.0 - shadow_lift) + shadow_lift

    h, w = out.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dist = np.sqrt(((xx - cx) / w) ** 2 + ((yy - cy) / h) ** 2)
    vig = 1.0 - vignette * np.clip(dist * 1.35, 0.0, 1.0) ** 2
    out *= vig[..., None]

    if grain > 0:
        noise = np.random.default_rng(frame_index * 9973).normal(0.0, grain, out.shape)
        out = np.clip(out + noise, 0.0, 1.0)

    return out
