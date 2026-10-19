from __future__ import annotations

import argparse
import sys
from pathlib import Path

from mall_memory import __version__
from mall_memory.effects import PRESETS
from mall_memory.render import build_video


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a slow, cinematic mall slideshow with music — "
            "documentary / urban-exploration pacing."
        )
    )
    parser.add_argument(
        "--images",
        "-i",
        type=Path,
        help="Folder containing your mall photos (jpg, png, webp, …)",
    )
    parser.add_argument(
        "--music",
        "-m",
        type=Path,
        help="Background music track (mp3, wav, m4a, …)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output") / "mall-memory.mp4",
        help="Output video path (default: output/mall-memory.mp4)",
    )
    parser.add_argument(
        "--style",
        choices=sorted(PRESETS.keys()),
        default="proper-people",
        help="Visual pacing preset (default: proper-people)",
    )
    parser.add_argument(
        "--sort",
        choices=("name", "date"),
        default="name",
        help="Image order: filename or EXIF/mtime date",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Output width (default: 1920)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Output height (default: 1080)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="Frames per second (default: 24, filmic)",
    )
    parser.add_argument(
        "--seconds-per-image",
        type=float,
        default=None,
        help="Override preset hold time per photo",
    )
    parser.add_argument(
        "--crossfade",
        type=float,
        default=None,
        help="Override preset crossfade duration in seconds",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Open the desktop UI instead of running from the command line",
    )

    args = parser.parse_args(argv)

    launch_gui = args.gui or (argv is None and len(sys.argv) == 1)
    if launch_gui:
        from mall_memory.gui import run

        run()
        return 0

    if args.images is None or args.music is None:
        parser.error("the following arguments are required: --images/-i, --music/-m (or use --gui)")

    try:
        out = build_video(
            args.images,
            args.music,
            args.output,
            style=args.style,
            sort=args.sort,
            width=args.width,
            height=args.height,
            fps=args.fps,
            seconds_per_image=args.seconds_per_image,
            crossfade_seconds=args.crossfade,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
