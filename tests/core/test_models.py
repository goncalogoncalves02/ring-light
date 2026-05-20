from __future__ import annotations

import pytest

from ringlight_overlay.core.models import ConfigData, Light, Profile


def _valid_light_kwargs() -> dict:
    return dict(
        id="light-1",
        enabled=True,
        monitor_name="\\\\.\\DISPLAY1",
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


def test_light_accepts_valid_inputs() -> None:
    light = Light(**_valid_light_kwargs())
    assert light.shape == "ring"
    assert light.brightness == pytest.approx(0.85)


@pytest.mark.parametrize(
    "field,value",
    [
        ("shape", "polygon"),
        ("color_mode", "hsv"),
        ("brightness", 1.5),
        ("brightness", -0.1),
        ("opacity", 2.0),
        ("color_kelvin", 500),
        ("color_kelvin", 50000),
        ("feather", -1),
        ("monitor_index", -2),
        ("position", (1.5, 0.5)),
        ("size", (0, 800)),
        ("color_rgb", (300, 0, 0)),
    ],
)
def test_light_rejects_out_of_range(field: str, value: object) -> None:
    kwargs = _valid_light_kwargs()
    kwargs[field] = value
    with pytest.raises(ValueError):
        Light(**kwargs)


def test_profile_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        Profile(id="p-1", name="", lights=[])


def test_profile_accepts_empty_lights_list() -> None:
    profile = Profile(id="p-1", name="Daylight", lights=[])
    assert profile.lights == []


def test_config_data_rejects_version_below_one() -> None:
    with pytest.raises(ValueError):
        ConfigData(version=0, active_profile_id="p-1")


def test_config_data_holds_profiles() -> None:
    profile = Profile(id="p-1", name="Daylight")
    config = ConfigData(version=1, active_profile_id="p-1", profiles=[profile])
    assert config.profiles[0].name == "Daylight"
