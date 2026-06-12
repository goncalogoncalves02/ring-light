from __future__ import annotations

import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Return an absolute path to a bundled resource.

    Works both in a normal Python environment and when frozen by PyInstaller.
    When frozen, ``sys._MEIPASS`` is the extraction directory and the package
    tree lives under ``ringlight_overlay/resources/`` relative to it.
    """
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS")) / "ringlight_overlay" / "resources"
    else:
        base = Path(__file__).resolve().parent.parent / "resources"
    return base.joinpath(*parts)


def app_icon_path() -> Path:
    """Return the absolute path to the application icon (favicon.ico)."""
    return resource_path("icons", "favicon.ico")
