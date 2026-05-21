from __future__ import annotations

import uuid

from ringlight_overlay.core.models import Light, Profile
from ringlight_overlay.core.monitors import MonitorInfo
from ringlight_overlay.overlay.overlay_manager import OverlayManager


def _monitor() -> MonitorInfo:
    return MonitorInfo(
        index=0,
        name="\\\\.\\DISPLAY1",
        geometry=(0, 0, 1920, 1080),
        primary=True,
    )


def _light(enabled: bool = True, shape: str = "ring") -> Light:
    return Light(
        id=str(uuid.uuid4()),
        enabled=enabled,
        monitor_name="\\\\.\\DISPLAY1",
        monitor_index=0,
        shape=shape,
        position=(0.5, 0.5),
        size=(400, 400),
        color_mode="kelvin",
        color_rgb=(255, 240, 220),
        color_kelvin=5600,
        brightness=0.85,
        opacity=0.95,
        feather=12,
        shape_params={"thickness": 80} if shape == "ring" else {},
    )


def test_apply_profile_creates_windows(qapp) -> None:
    manager = OverlayManager()
    light = _light()
    profile = Profile(id="p-1", name="Test", lights=[light])
    manager.apply_profile(profile, [_monitor()])
    assert manager.window_count == 1
    manager.close_all()


def test_apply_profile_removes_old_windows_on_update(qapp) -> None:
    manager = OverlayManager()
    light_a = _light()
    light_b = _light()
    profile_a = Profile(id="p-1", name="A", lights=[light_a, light_b])
    manager.apply_profile(profile_a, [_monitor()])
    assert manager.window_count == 2

    profile_b = Profile(id="p-1", name="A", lights=[light_b])
    manager.apply_profile(profile_b, [_monitor()])
    assert manager.window_count == 1
    manager.close_all()


def test_disabled_light_window_is_hidden(qapp) -> None:
    manager = OverlayManager()
    light = _light(enabled=False)
    profile = Profile(id="p-1", name="Test", lights=[light])
    manager.apply_profile(profile, [_monitor()])
    win = manager.get_window(light.id)
    assert win is not None
    assert not win.isVisible()
    manager.close_all()


def test_close_all_removes_all_windows(qapp) -> None:
    manager = OverlayManager()
    lights = [_light() for _ in range(3)]
    profile = Profile(id="p-1", name="T", lights=lights)
    manager.apply_profile(profile, [_monitor()])
    assert manager.window_count == 3
    manager.close_all()
    assert manager.window_count == 0
