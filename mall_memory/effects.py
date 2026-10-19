from __future__ import annotations

import random
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps

_VIGNETTE_CACHE: dict[tuple[int, int, float], np.ndarray] = {}


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


def _vignette_mask(h: int, w: int, vignette: float) -> np.ndarray:
    key = (h, w, vignette)
    cached = _VIGNETTE_CACHE.get(key)
    if cached is not None:
        return cached
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dist = np.sqrt(((xx - cx) / w) ** 2 + ((yy - cy) / h) ** 2)
    mask = 1.0 - vignette * np.clip(dist * 1.35, 0.0, 1.0) ** 2
    _VIGNETTE_CACHE[key] = mask.astype(np.float32)
    return _VIGNETTE_CACHE[key]


@dataclass
class KenBurnsSlide:
    """Pre-scaled image + fixed pan path — avoids per-frame full-image work."""

    canvas: np.ndarray
    out_w: int
    out_h: int
    zoom_end: float
    duration: float
    pan_x: float
    pan_y: float

    @classmethod
    def from_image(
        cls,
        image: np.ndarray,
        duration: float,
        out_w: int,
        out_h: int,
        zoom_end: float,
        seed: int,
    ) -> KenBurnsSlide:
        rng = random.Random(seed)
        ih, iw = image.shape[:2]
        pan_x = rng.uniform(-0.04, 0.04)
        pan_y = rng.uniform(-0.03, 0.03)

        cover = max(out_w / iw, out_h / ih) * zoom_end
        cw = max(1, int(round(iw * cover)))
        ch = max(1, int(round(ih * cover)))
        pil = Image.fromarray((image * 255).astype(np.uint8))
        canvas = np.asarray(
            pil.resize((cw, ch), Image.Resampling.BILINEAR), dtype=np.float32
        ) / 255.0

        return cls(
            canvas=canvas,
            out_w=out_w,
            out_h=out_h,
            zoom_end=zoom_end,
            duration=duration,
            pan_x=pan_x,
            pan_y=pan_y,
        )

    def frame_at(self, t: float) -> np.ndarray:
        progress = 0.0 if self.duration <= 0 else min(1.0, max(0.0, t / self.duration))
        scale = _lerp(1.0, self.zoom_end, progress)
        crop_w = self.out_w / scale
        crop_h = self.out_h / scale

        ch, cw = self.canvas.shape[:2]
        max_x = max(0.0, cw - crop_w)
        max_y = max(0.0, ch - crop_h)
        start_x = max_x * (0.5 + self.pan_x)
        start_y = max_y * (0.5 + self.pan_y)
        end_x = max_x * (0.5 - self.pan_x * 0.6)
        end_y = max_y * (0.5 - self.pan_y * 0.6)
        x0 = int(_lerp(start_x, end_x, progress))
        y0 = int(_lerp(start_y, end_y, progress))
        x1 = min(cw, int(round(x0 + crop_w)))
        y1 = min(ch, int(round(y0 + crop_h)))

        crop = self.canvas[y0:y1, x0:x1]
        if crop.size == 0:
            crop = self.canvas

        if crop.shape[0] == self.out_h and crop.shape[1] == self.out_w:
            return crop

        pil = Image.fromarray((crop * 255).astype(np.uint8))
        pil = pil.resize((self.out_w, self.out_h), Image.Resampling.BILINEAR)
        return np.asarray(pil, dtype=np.float32) / 255.0


def ken_burns_crop(
    image: np.ndarray,
    t: float,
    duration: float,
    out_w: int,
    out_h: int,
    zoom_end: float,
    seed: int,
) -> np.ndarray:
    """Backward-compatible helper; prefer KenBurnsSlide for slideshows."""
    slide = KenBurnsSlide.from_image(image, duration, out_w, out_h, zoom_end, seed)
    return slide.frame_at(t)


def apply_grade(
    frame: np.ndarray,
    saturation: float,
    warmth: float,
    shadow_lift: float,
    vignette: float,
    grain: float,
    frame_index: int,
) -> np.ndarray:
    out = frame

    gray = out.mean(axis=2, keepdims=True)
    out = gray + (out - gray) * saturation

    out[..., 0] = np.clip(out[..., 0] + warmth, 0.0, 1.0)
    out[..., 2] = np.clip(out[..., 2] - warmth * 0.7, 0.0, 1.0)

    out = out * (1.0 - shadow_lift) + shadow_lift

    h, w = out.shape[:2]
    out *= _vignette_mask(h, w, vignette)[..., None]

    if grain > 0:
        noise = np.random.default_rng(frame_index * 9973).normal(0.0, grain, out.shape)
        out = np.clip(out + noise, 0.0, 1.0)

    return out
