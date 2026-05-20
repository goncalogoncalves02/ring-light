from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import ringlight_overlay


def test_version_is_set() -> None:
    assert ringlight_overlay.__version__ == "0.0.1"


def test_module_runs_and_writes_startup_log(tmp_path: Path) -> None:
    appdata = Path(os.environ["APPDATA"]) / "RingLightOverlay"
    log_path = appdata / "app.log"
    if log_path.exists():
        log_path.unlink()

    result = subprocess.run(
        [sys.executable, "-m", "ringlight_overlay"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert log_path.exists(), f"expected log at {log_path}"
    content = log_path.read_text(encoding="utf-8")
    assert "startup OK" in content, f"log content: {content!r}"
