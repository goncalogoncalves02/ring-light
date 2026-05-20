from __future__ import annotations

import uuid

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.ui.widgets.profile_list import ProfileList


def _light() -> Light:
    return Light(
        id=str(uuid.uuid4()),
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


def _config() -> ConfigData:
    p1 = Profile(id=str(uuid.uuid4()), name="Daylight", lights=[_light()])
    p2 = Profile(id=str(uuid.uuid4()), name="Night", lights=[])
    return ConfigData(version=1, active_profile_id=p1.id, profiles=[p1, p2])


def test_profile_list_constructs(qapp) -> None:
    config = _config()
    widget = ProfileList(config)
    assert widget is not None


def test_profile_list_shows_profiles(qapp) -> None:
    config = _config()
    widget = ProfileList(config)
    profile_names = [
        widget._profile_list.item(i).text() for i in range(widget._profile_list.count())
    ]
    assert "Daylight" in profile_names
    assert "Night" in profile_names


def test_profile_list_shows_lights_for_selected_profile(qapp) -> None:
    config = _config()
    widget = ProfileList(config)
    widget._profile_list.setCurrentRow(0)
    assert widget._light_list.count() == 1


def test_profile_list_has_required_signals(qapp) -> None:
    config = _config()
    widget = ProfileList(config)
    assert hasattr(widget, "profile_selected")
    assert hasattr(widget, "light_selected")
    assert hasattr(widget, "config_changed")
