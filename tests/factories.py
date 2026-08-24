"""Shared builders for test objects. Override any field by keyword."""

from __future__ import annotations

import uuid

from ringlight_overlay.core.models import Light
from ringlight_overlay.core.monitors import MonitorInfo


def make_light(**overrides) -> Light:
    shape = overrides.get("shape", "ring")
    defaults: dict = dict(
        id=str(uuid.uuid4()),
        enabled=True,
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
    defaults.update(overrides)
    return Light(**defaults)


def make_monitor(**overrides) -> MonitorInfo:
    defaults: dict = dict(
        index=0,
        name="\\\\.\\DISPLAY1",
        geometry=(0, 0, 1920, 1080),
        primary=True,
    )
    defaults.update(overrides)
    return MonitorInfo(**defaults)
