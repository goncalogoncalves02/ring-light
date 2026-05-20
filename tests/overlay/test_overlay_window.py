from __future__ import annotations

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
