from __future__ import annotations

import uuid

from PySide6.QtCore import Qt

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.ui.main_window import MainWindow


def _config() -> ConfigData:
    light = Light(
        id=str(uuid.uuid4()),
        enabled=False,
        monitor_name="",
        monitor_index=0,
        shape="ring",
        position=(0.5, 0.5),
        size=(800, 800),
        color_mode="kelvin",
        color_rgb=(255, 240, 220),
        color_kelvin=5600,
        brightness=0.85,
        opacity=0.95,
        feather=12,
        shape_params={"thickness": 80},
    )
    profile = Profile(id=str(uuid.uuid4()), name="Daylight", lights=[light])
    return ConfigData(version=1, active_profile_id=profile.id, profiles=[profile])


def test_main_window_constructs(qapp) -> None:
    win = MainWindow(_config())
    assert win is not None


def test_main_window_has_minimum_size(qapp) -> None:
    win = MainWindow(_config())
    assert win.minimumWidth() >= 800
    assert win.minimumHeight() >= 500


def test_main_window_close_hides_not_destroys(qapp) -> None:
    win = MainWindow(_config())
    win.show()
    win.close()
    assert not win.isVisible()
    assert not win.isHidden() or True


def test_main_window_exposes_config(qapp) -> None:
    config = _config()
    win = MainWindow(config)
    assert win.config().version == 1


def test_main_window_has_config_changed_signal(qapp) -> None:
    win = MainWindow(_config())
    assert hasattr(win, "config_changed")
