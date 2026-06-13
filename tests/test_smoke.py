from __future__ import annotations

import logging
from pathlib import Path

import pytest

import ringlight_overlay
from ringlight_overlay.app import _configure_logging


def test_version_is_set() -> None:
    assert ringlight_overlay.__version__ == "0.2.0"


def test_configure_logging_writes_startup_log(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APPDATA", str(tmp_path))
    log_path = tmp_path / "RingLightOverlay" / "app.log"

    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level
    root.handlers.clear()
    try:
        _configure_logging()
        logging.getLogger("ringlight_overlay.app").info("startup OK")
        for handler in root.handlers:
            handler.flush()

        assert log_path.exists(), f"expected log at {log_path}"
        assert "startup OK" in log_path.read_text(encoding="utf-8")
    finally:
        for handler in root.handlers:
            handler.close()
        root.handlers[:] = saved_handlers
        root.setLevel(saved_level)
