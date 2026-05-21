from __future__ import annotations

import uuid

from ringlight_overlay.core.models import Light
from ringlight_overlay.ui.widgets.light_editor import LightEditor


def _light(shape: str = "ring") -> Light:
    return Light(
        id=str(uuid.uuid4()),
        enabled=True,
        monitor_name="\\\\.\\DISPLAY1",
        monitor_index=0,
        shape=shape,
        position=(0.5, 0.5),
        size=(800, 800),
        color_mode="kelvin",
        color_rgb=(255, 240, 220),
        color_kelvin=5600,
        brightness=0.85,
        opacity=0.95,
        feather=12,
        shape_params={"thickness": 80} if shape == "ring" else {},
    )


def test_light_editor_constructs(qapp) -> None:
    editor = LightEditor()
    assert editor is not None


def test_light_editor_has_light_changed_signal(qapp) -> None:
    editor = LightEditor()
    assert hasattr(editor, "light_changed")


def test_light_editor_load_light_does_not_crash(qapp) -> None:
    editor = LightEditor()
    editor.load_light(_light("ring"))


def test_light_editor_load_light_sets_shape(qapp) -> None:
    editor = LightEditor()
    editor.load_light(_light("circle"))
    assert editor.current_shape() == "circle"


def test_light_editor_load_light_sets_feather(qapp) -> None:
    editor = LightEditor()
    light = _light()
    editor.load_light(light)
    assert editor.current_feather() == light.feather


def test_light_editor_clear_does_not_crash(qapp) -> None:
    editor = LightEditor()
    editor.load_light(_light())
    editor.clear()
