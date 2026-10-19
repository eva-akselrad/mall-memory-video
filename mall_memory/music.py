from __future__ import annotations

from datetime import datetime
from pathlib import Path

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".wma", ".opus"}


def discover_music(folder: Path, sort: str = "name") -> list[Path]:
    if not folder.is_dir():
        raise FileNotFoundError(f"Music folder not found: {folder}")

    paths = [
        p
        for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() in AUDIO_EXTENSIONS
    ]
    if not paths:
        raise ValueError(f"No audio files found in {folder}")

    if sort == "name":
        return sorted(paths, key=lambda p: p.name.lower())
    if sort == "date":
        return sorted(paths, key=lambda p: datetime.fromtimestamp(p.stat().st_mtime))
    raise ValueError(f"Unknown sort mode: {sort}")


def resolve_music_paths(source: Path, sort: str = "name") -> list[Path]:
    """Single audio file or a folder of tracks (played in order)."""
    if source.is_file():
        return [source]
    if source.is_dir():
        return discover_music(source, sort=sort)
    raise FileNotFoundError(f"Music not found: {source}")
