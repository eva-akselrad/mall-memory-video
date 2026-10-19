from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


@dataclass(frozen=True)
class ImageItem:
    path: Path
    sort_key: datetime | str


def discover_images(folder: Path, sort: str = "name") -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Image folder not found: {folder}")

    paths = [
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]
    if not paths:
        raise ValueError(f"No images found in {folder}")

    if sort == "name":
        return sorted(paths, key=lambda p: p.name.lower())

    if sort == "date":
        return sorted(paths, key=_image_datetime)

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
