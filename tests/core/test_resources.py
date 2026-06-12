from __future__ import annotations

import sys
from pathlib import Path

import pytest


def test_resource_path_non_frozen_ends_with_expected_suffix() -> None:
    """Non-frozen: resource_path resolves under the package resources dir."""
    from ringlight_overlay.core.resources import resource_path

    result = resource_path("icons", "favicon.ico")
    expected_suffix = Path("resources") / "icons" / "favicon.ico"
    assert str(result).endswith(str(expected_suffix))
    assert result.is_absolute()


def test_resource_path_non_frozen_is_under_package() -> None:
    """Non-frozen: result is anchored under the package directory."""
    import ringlight_overlay.core.resources as resources_module
    from ringlight_overlay.core.resources import resource_path

    result = resource_path("icons", "favicon.ico")
    package_root = Path(resources_module.__file__).resolve().parent.parent
    assert str(result).startswith(str(package_root))


def test_resource_path_frozen(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Frozen path: result uses sys._MEIPASS as base."""
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    # Re-import to pick up module-level changes if any, but resource_path reads sys dynamically
    from ringlight_overlay.core.resources import resource_path

    result = resource_path("icons", "favicon.ico")
    expected = tmp_path / "ringlight_overlay" / "resources" / "icons" / "favicon.ico"
    assert result == expected


def test_app_icon_path_returns_favicon_ico() -> None:
    """app_icon_path() returns a path ending with icons/favicon.ico."""
    from ringlight_overlay.core.resources import app_icon_path

    result = app_icon_path()
    assert result.name == "favicon.ico"
    assert result.parent.name == "icons"


def test_favicon_ico_exists() -> None:
    """The generated favicon.ico asset must be present."""
    from ringlight_overlay.core.resources import app_icon_path

    path = app_icon_path()
    assert path.exists(), f"favicon.ico not found at {path}"


def test_favicon_ico_has_ico_magic() -> None:
    """favicon.ico must start with the ICO magic bytes 00 00 01 00."""
    from ringlight_overlay.core.resources import app_icon_path

    data = app_icon_path().read_bytes()
    assert data[:4] == b"\x00\x00\x01\x00", "File does not start with ICO magic bytes"


def test_favicon_ico_embeds_six_images() -> None:
    """favicon.ico must embed exactly 6 icon images (16/32/48/64/128/256)."""
    from ringlight_overlay.core.resources import app_icon_path

    data = app_icon_path().read_bytes()
    count = int.from_bytes(data[4:6], "little")
    assert count == 6, f"Expected 6 embedded images, got {count}"
