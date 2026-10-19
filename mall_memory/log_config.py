from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_DATE = "%H:%M:%S"


class _GuiLogHandler(logging.Handler):
    def __init__(self, append_line: Callable[[str], None]) -> None:
        super().__init__()
        self._append_line = append_line

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._append_line(self.format(record))
        except Exception:
            self.handleError(record)


def setup_logging(
    *,
    level: int = logging.INFO,
    gui_append: Callable[[str], None] | None = None,
    log_file: Path | None = None,
) -> logging.Logger:
    """Configure the mall_memory logger tree (console, optional GUI + file)."""
    root = logging.getLogger("mall_memory")
    root.setLevel(level)
    root.handlers.clear()
    root.propagate = False

    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE)

    if gui_append is not None:
        gui_handler = _GuiLogHandler(gui_append)
        gui_handler.setFormatter(formatter)
        root.addHandler(gui_handler)
    else:
        stream = logging.StreamHandler(sys.stderr)
        stream.setFormatter(formatter)
        root.addHandler(stream)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    return root


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"mall_memory.{name}")
