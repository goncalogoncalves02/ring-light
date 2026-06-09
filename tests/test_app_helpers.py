from __future__ import annotations

import uuid
from dataclasses import replace

from ringlight_overlay.app import _active_profile, _scale_profile_brightness, _toggle_all_lights
from ringlight_overlay.core.models import ConfigData, Light, Profile


def _light(enabled: bool = True) -> Light:
    return Light(
        id=str(uuid.uuid4()),
        enabled=enabled,
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


def _config(lights: list | None = None) -> ConfigData:
    p = Profile(id="p-1", name="Test", lights=lights or [_light()])
    return ConfigData(version=1, active_profile_id="p-1", profiles=[p])


def test_active_profile_returns_active(qapp) -> None:
    p1 = Profile(id="p-1", name="A")
    p2 = Profile(id="p-2", name="B")
    config = ConfigData(version=1, active_profile_id="p-2", profiles=[p1, p2])
    assert _active_profile(config).id == "p-2"


def test_active_profile_falls_back_to_first(qapp) -> None:
    p1 = Profile(id="p-1", name="A")
    config = ConfigData(version=1, active_profile_id="missing", profiles=[p1])
    assert _active_profile(config).id == "p-1"


def test_active_profile_returns_none_when_empty(qapp) -> None:
    config = ConfigData(version=1, active_profile_id="", profiles=[])
    assert _active_profile(config) is None


def test_toggle_all_lights_disables_all_enabled(qapp) -> None:
    config = _config([_light(enabled=True), _light(enabled=True)])
    result = _toggle_all_lights(config)
    active = _active_profile(result)
    assert all(not lt.enabled for lt in active.lights)


def test_toggle_all_lights_enables_all_disabled(qapp) -> None:
    config = _config([_light(enabled=False), _light(enabled=False)])
    result = _toggle_all_lights(config)
    active = _active_profile(result)
    assert all(lt.enabled for lt in active.lights)


def test_toggle_all_lights_mixed_disables_all(qapp) -> None:
    config = _config([_light(enabled=True), _light(enabled=False)])
    result = _toggle_all_lights(config)
    active = _active_profile(result)
    assert all(not lt.enabled for lt in active.lights)


def test_toggle_all_lights_returns_new_config(qapp) -> None:
    config = _config([_light(enabled=True)])
    result = _toggle_all_lights(config)
    assert result is not config


def test_toggle_all_lights_noop_on_empty_profile(qapp) -> None:
    config = _config(lights=[])
    result = _toggle_all_lights(config)
    assert result.active_profile_id == config.active_profile_id


# --- _scale_profile_brightness ---


def _make_profile_with_brightness(brightness: float) -> Profile:
    return Profile(id=str(uuid.uuid4()), name="Test", lights=[replace(_light(), brightness=brightness)])


def test_scale_profile_brightness_scales_lights() -> None:
    profile = _make_profile_with_brightness(0.8)
    scaled = _scale_profile_brightness(profile, 0.5)
    assert abs(scaled.lights[0].brightness - 0.4) < 1e-9


def test_scale_profile_brightness_clamps_above_one() -> None:
    profile = _make_profile_with_brightness(0.9)
    scaled = _scale_profile_brightness(profile, 2.0)
    assert scaled.lights[0].brightness == 1.0


def test_scale_profile_brightness_clamps_to_zero() -> None:
    profile = _make_profile_with_brightness(0.8)
    scaled = _scale_profile_brightness(profile, 0.0)
    assert scaled.lights[0].brightness == 0.0


def test_scale_profile_brightness_returns_new_object() -> None:
    profile = _make_profile_with_brightness(0.8)
    scaled = _scale_profile_brightness(profile, 0.5)
    assert scaled is not profile
    assert scaled.lights[0] is not profile.lights[0]
    assert profile.lights[0].brightness == 0.8  # original unchanged


def test_scale_profile_brightness_preserves_id_and_name() -> None:
    profile = _make_profile_with_brightness(0.8)
    scaled = _scale_profile_brightness(profile, 0.5)
    assert scaled.id == profile.id
    assert scaled.name == profile.name
