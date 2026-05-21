from __future__ import annotations

from ringlight_overlay.ui.widgets.color_picker import ColorPicker


def test_color_picker_constructs_in_rgb_mode(qapp) -> None:
    picker = ColorPicker()
    picker.set_values(
        color_mode="rgb",
        color_rgb=(255, 128, 0),
        color_kelvin=5600,
        brightness=0.8,
        opacity=0.9,
    )
    assert picker.color_mode() == "rgb"


def test_color_picker_constructs_in_kelvin_mode(qapp) -> None:
    picker = ColorPicker()
    picker.set_values(
        color_mode="kelvin",
        color_rgb=(255, 255, 255),
        color_kelvin=4000,
        brightness=1.0,
        opacity=1.0,
    )
    assert picker.color_mode() == "kelvin"


def test_color_picker_returns_rgb_values(qapp) -> None:
    picker = ColorPicker()
    picker.set_values(
        color_mode="rgb",
        color_rgb=(100, 150, 200),
        color_kelvin=5600,
        brightness=0.5,
        opacity=0.7,
    )
    assert picker.color_rgb() == (100, 150, 200)


def test_color_picker_returns_kelvin_value(qapp) -> None:
    picker = ColorPicker()
    picker.set_values(
        color_mode="kelvin",
        color_rgb=(255, 255, 255),
        color_kelvin=3200,
        brightness=1.0,
        opacity=1.0,
    )
    assert picker.color_kelvin() == 3200


def test_color_picker_returns_brightness_and_opacity(qapp) -> None:
    picker = ColorPicker()
    picker.set_values(
        color_mode="rgb",
        color_rgb=(255, 255, 255),
        color_kelvin=5600,
        brightness=0.6,
        opacity=0.4,
    )
    assert abs(picker.brightness() - 0.6) < 0.01
    assert abs(picker.opacity() - 0.4) < 0.01


def test_color_picker_emits_color_changed_signal(qapp) -> None:
    from PySide6.QtCore import Qt

    picker = ColorPicker()
    picker.set_values(
        color_mode="rgb",
        color_rgb=(255, 255, 255),
        color_kelvin=5600,
        brightness=1.0,
        opacity=1.0,
    )

    received: list = []
    picker.color_changed.connect(lambda *args: received.append(args))
    picker._notify_change()
    assert len(received) == 1
