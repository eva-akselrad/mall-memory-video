from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


@dataclass(frozen=True)
class ImageItem:
    path: Path
    sort_key: datetime | str


DEFAULT_ORDER_FILENAME = "order.txt"


def _list_images(folder: Path) -> list[Path]:
    paths = [
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if not paths:
        raise ValueError(f"No images found in {folder}")
    return paths


def _read_order_names(order_path: Path) -> list[str]:
    names: list[str] = []
    for line in order_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        names.append(Path(stripped).name)
    if not names:
        raise ValueError(f"Order file is empty: {order_path}")
    return names


def _sort_by_order_file(paths: list[Path], order_path: Path) -> list[Path]:
    by_name = {p.name.lower(): p for p in paths}
    by_name.update({p.name: p for p in paths})

    ordered: list[Path] = []
    seen: set[Path] = set()
    for name in _read_order_names(order_path):
        match = by_name.get(name) or by_name.get(name.lower())
        if match is None:
            raise ValueError(f"Order file lists missing image: {name}")
        if match not in seen:
            ordered.append(match)
            seen.add(match)

    remaining = sorted(
        [p for p in paths if p not in seen],
        key=lambda p: p.name.lower(),
    )
    if remaining:
        ordered.extend(remaining)
    return ordered


def discover_images(
    folder: Path,
    sort: str = "name",
    order_file: Path | None = None,
) -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Image folder not found: {folder}")

    paths = _list_images(folder)

    if sort == "name":
        return sorted(paths, key=lambda p: p.name.lower())

    if sort == "date":
        return sorted(paths, key=_image_datetime)

    if sort == "file":
        order_path = order_file or (folder / DEFAULT_ORDER_FILENAME)
        if not order_path.is_file():
            raise FileNotFoundError(
                f"Custom order file not found: {order_path} "
                f"(create it with one image filename per line)"
            )
        return _sort_by_order_file(paths, order_path)

    raise ValueError(f"Unknown sort mode: {sort}")


def _image_datetime(path: Path) -> datetime:
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS

        with Image.open(path) as img:
            exif = img.getexif()
            if exif:
                for tag_id, value in exif.items():
                    if TAGS.get(tag_id) == "DateTimeOriginal" and value:
                        return datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
    except Exception:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)
