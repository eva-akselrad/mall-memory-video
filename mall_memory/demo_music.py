"""Generate a simple royalty-free ambient demo track (synthetic, no samples)."""

from __future__ import annotations

import argparse
import subprocess
import wave
from pathlib import Path

import numpy as np

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = PACKAGE_ROOT / "assets" / "demo-mall-ambient.mp3"


def bundled_demo_path() -> Path:
    return DEFAULT_OUTPUT


def generate_wav(path: Path, seconds: float = 150.0, sample_rate: int = 44100) -> Path:
    """Slow ambient drone + soft shimmer — mall-atrium documentary mood."""
    n = int(sample_rate * seconds)
    t = np.linspace(0, seconds, n, endpoint=False)

    audio = np.zeros(n, dtype=np.float64)
    roots = (55.0, 82.41, 110.0, 146.83, 196.0)
    for i, freq in enumerate(roots):
        breathe = 0.55 + 0.45 * np.sin(2 * np.pi * (0.018 + i * 0.004) * t + i * 0.7)
        drift = np.sin(2 * np.pi * freq * t + 0.35 * np.sin(2 * np.pi * 0.05 * t))
        audio += breathe * drift * (0.11 / (i + 1))

    haze = np.sin(2 * np.pi * 329.63 * t) * (0.35 + 0.65 * np.sin(2 * np.pi * 0.031 * t))
    audio += 0.025 * haze

    # Very soft filtered noise bed (air / HVAC hum)
    rng = np.random.default_rng(42)
    noise = rng.normal(0, 1, n)
    kernel = np.ones(800) / 800
    noise = np.convolve(noise, kernel, mode="same")
    audio += noise * 0.012

    fade = int(sample_rate * 4)
    ramp = np.ones(n)
    ramp[:fade] = np.linspace(0, 1, fade)
    ramp[-fade:] = np.linspace(1, 0, fade)
    audio *= ramp

    peak = np.max(np.abs(audio)) or 1.0
    audio = (audio / peak * 0.82).astype(np.float32)

    delay = int(sample_rate * 0.018)
    stereo = np.column_stack([audio, np.roll(audio, delay) * 0.96])
    pcm = (stereo * 32767).astype(np.int16)

    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return path


def generate_mp3(
    output: Path = DEFAULT_OUTPUT,
    seconds: float = 150.0,
    keep_wav: bool = False,
) -> Path:
    wav_path = output.with_suffix(".wav")
    generate_wav(wav_path, seconds=seconds)
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "4",
            str(output),
        ],
        check=True,
        capture_output=True,
    )
    if not keep_wav:
        wav_path.unlink(missing_ok=True)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate bundled demo ambient music.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output MP3 path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=150.0,
        help="Track length in seconds (default: 150)",
    )
    parser.add_argument("--keep-wav", action="store_true", help="Keep intermediate WAV file")
    args = parser.parse_args(argv)

    out = generate_mp3(args.output, seconds=args.seconds, keep_wav=args.keep_wav)
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
