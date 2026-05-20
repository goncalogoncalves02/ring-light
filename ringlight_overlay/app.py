from __future__ import annotations

import logging
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def _log_dir() -> Path:
    base = os.environ.get("APPDATA")
    if not base:
        raise RuntimeError("APPDATA environment variable is required on Windows.")
    return Path(base) / "RingLightOverlay"


def _configure_logging() -> logging.Logger:
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Replace any pre-existing handlers so re-runs don't duplicate output.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(file_handler)

    return logging.getLogger("ringlight_overlay.app")


def main() -> int:
    """Bootstrap entry point used by `python -m ringlight_overlay`.

    S0 scope: initialize logging + QApplication and exit cleanly. The Qt event
    loop is intentionally NOT started here — that arrives in a later sprint
    (S4) when the system tray gives the app something to keep running for.
    """
    log = _configure_logging()
    log.info("startup OK")

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    log.info("shutdown OK")
    return 0
