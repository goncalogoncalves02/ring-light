from __future__ import annotations

import uuid

import pytest
from PySide6.QtCore import Qt

from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay.overlay_window import OverlayWindow


def _valid_light() -> Light:
    return Light(
        id="light-1",
        enabled=True,
        monitor_name="\\\\.\\DISPLAY1",
        monitor_index=0,
        shape="ring",
        position=(0.5, 0.5),
        size=(400, 400),
        color_mode="kelvin",
        color_rgb=(255, 240, 220),
        color_kelvin=5600,
        brightness=0.85,
        opacity=0.95,
        feather=12,
        shape_params={"thickness": 80},
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


def test_overlay_window_has_frameless_hint(qapp) -> None:
    win = OverlayWindow(_valid_light())
    flags = win.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint


def test_overlay_window_has_stays_on_top_hint(qapp) -> None:
    win = OverlayWindow(_valid_light())
    assert win.windowFlags() & Qt.WindowType.WindowStaysOnTopHint


def test_overlay_window_has_translucent_background(qapp) -> None:
    win = OverlayWindow(_valid_light())
    assert win.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


def test_update_light_changes_opacity(qapp) -> None:
    light = _valid_light()
    win = OverlayWindow(light)
    new_light = Light(
        id=light.id,
        enabled=light.enabled,
        monitor_name=light.monitor_name,
        monitor_index=light.monitor_index,
        shape=light.shape,
        position=light.position,
        size=light.size,
        color_mode=light.color_mode,
        color_rgb=light.color_rgb,
        color_kelvin=light.color_kelvin,
        brightness=light.brightness,
        opacity=0.5,
        feather=light.feather,
        shape_params=light.shape_params,
    )
    win.update_light(new_light)
    assert abs(win.windowOpacity() - 0.5) < 0.01


def test_update_light_stores_new_light(qapp) -> None:
    light = _valid_light()
    win = OverlayWindow(light)
    new_light = Light(
        id=light.id,
        enabled=light.enabled,
        monitor_name=light.monitor_name,
        monitor_index=light.monitor_index,
        shape="circle",
        position=light.position,
        size=light.size,
        color_mode=light.color_mode,
        color_rgb=light.color_rgb,
        color_kelvin=light.color_kelvin,
        brightness=light.brightness,
        opacity=light.opacity,
        feather=light.feather,
        shape_params={},
    )
    win.update_light(new_light)
    assert win.light.shape == "circle"


def test_apply_placement_sets_geometry(qapp) -> None:
    from PySide6.QtCore import QRect

    win = OverlayWindow(_light())
    win.apply_placement(None, QRect(100, 200, 400, 400))
    assert win.geometry() == QRect(100, 200, 400, 400)
    win.close()


def test_apply_placement_anchors_to_screen_when_different(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    win = OverlayWindow(_light())
    calls: list[object] = []
    monkeypatch.setattr(OverlayWindow, "setScreen", lambda self, s: calls.append(s))

    fake_screen = Mock()
    fake_screen.name.return_value = "\\\\.\\DISPLAY2"
    win.apply_placement(fake_screen, QRect(0, 0, 400, 400))

    assert calls == [fake_screen]
    assert win._target_screen_name == "\\\\.\\DISPLAY2"
    win.close()


def test_apply_placement_skips_setscreen_when_already_on_target(qapp, monkeypatch) -> None:
    from PySide6.QtCore import QRect

    win = OverlayWindow(_light())
    calls: list[object] = []
    monkeypatch.setattr(OverlayWindow, "setScreen", lambda self, s: calls.append(s))

    win.apply_placement(win.screen(), QRect(0, 0, 400, 400))
    assert calls == []
    win.close()


def test_apply_placement_reapplies_click_through_when_visible(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_window as ow_module

    win = OverlayWindow(_light())
    win.show()
    hwnds: list[int] = []
    monkeypatch.setattr(ow_module, "apply_click_through", lambda hwnd: hwnds.append(hwnd))

    fake_screen = Mock()
    fake_screen.name.return_value = "\\\\.\\DISPLAY2"
    monkeypatch.setattr(OverlayWindow, "setScreen", lambda self, s: None)
    win.apply_placement(fake_screen, QRect(0, 0, 400, 400))

    assert len(hwnds) == 1
    win.close()
