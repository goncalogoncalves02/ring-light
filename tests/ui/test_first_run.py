from __future__ import annotations

import pytest

from ringlight_overlay.core.monitors import MonitorInfo
from ringlight_overlay.core.storage import default_config
from ringlight_overlay.ui.dialogs.first_run import (
    FirstRunWizard,
    apply_wizard_result,
    build_first_run_light,
)


def _monitor(index: int = 0, primary: bool = True) -> MonitorInfo:
    return MonitorInfo(
        index=index,
        name=f"Screen{index}",
        geometry=(0, 0, 1920, 1080),
        primary=primary,
    )


class TestBuildFirstRunLight:
    def test_returns_enabled_light(self):
        m = _monitor()
        light = build_first_run_light(m)
        assert light.enabled is True

    def test_monitor_name_set(self):
        m = _monitor(index=1)
        m2 = MonitorInfo(index=1, name="HDMI-2", geometry=(1920, 0, 1920, 1080), primary=False)
        light = build_first_run_light(m2)
        assert light.monitor_name == "HDMI-2"

    def test_monitor_index_set(self):
        m = MonitorInfo(index=2, name="X", geometry=(0, 0, 1920, 1080), primary=False)
        light = build_first_run_light(m)
        assert light.monitor_index == 2

    def test_shape_parameter(self):
        m = _monitor()
        light = build_first_run_light(m, shape="circle")
        assert light.shape == "circle"

    def test_size_parameter(self):
        m = _monitor()
        light = build_first_run_light(m, size=(600, 600))
        assert light.size == (600, 600)

    def test_default_shape_is_ring(self):
        m = _monitor()
        light = build_first_run_light(m)
        assert light.shape == "ring"

    def test_has_sensible_brightness(self):
        m = _monitor()
        light = build_first_run_light(m)
        assert 0.0 < light.brightness <= 1.0

    def test_has_unique_id(self):
        m = _monitor()
        l1 = build_first_run_light(m)
        l2 = build_first_run_light(m)
        assert l1.id != l2.id


class TestApplyWizardResult:
    def test_active_profile_light_replaced(self):
        config = default_config()
        m = _monitor()
        new_light = build_first_run_light(m)
        result = apply_wizard_result(config, new_light)
        active = next(p for p in result.profiles if p.id == result.active_profile_id)
        assert len(active.lights) == 1
        assert active.lights[0].id == new_light.id

    def test_hotkeys_preserved(self):
        config = default_config()
        m = _monitor()
        new_light = build_first_run_light(m)
        result = apply_wizard_result(config, new_light)
        assert result.settings["hotkeys"] == config.settings["hotkeys"]

    def test_other_settings_preserved(self):
        config = default_config()
        m = _monitor()
        new_light = build_first_run_light(m)
        result = apply_wizard_result(config, new_light)
        assert (
            result.settings["minimize_to_tray_on_close"]
            == config.settings["minimize_to_tray_on_close"]
        )

    def test_version_preserved(self):
        config = default_config()
        m = _monitor()
        new_light = build_first_run_light(m)
        result = apply_wizard_result(config, new_light)
        assert result.version == config.version


class TestFirstRunWizard:
    def test_constructs_with_monitors(self, qapp):
        monitors = [_monitor(0, primary=True), _monitor(1, primary=False)]
        wizard = FirstRunWizard(monitors=monitors)
        assert wizard is not None

    def test_has_three_pages(self, qapp):
        monitors = [_monitor()]
        wizard = FirstRunWizard(monitors=monitors)
        assert wizard.pageIds() == [0, 1, 2]

    def test_result_config_returns_config_data(self, qapp):
        monitors = [_monitor()]
        wizard = FirstRunWizard(monitors=monitors)
        config = default_config()
        result = wizard.result_config(config)
        from ringlight_overlay.core.models import ConfigData

        assert isinstance(result, ConfigData)

    def test_result_config_produces_enabled_light(self, qapp):
        monitors = [_monitor()]
        wizard = FirstRunWizard(monitors=monitors)
        config = default_config()
        result = wizard.result_config(config)
        active = next(p for p in result.profiles if p.id == result.active_profile_id)
        assert active.lights[0].enabled is True

    def test_single_monitor(self, qapp):
        monitors = [_monitor()]
        wizard = FirstRunWizard(monitors=monitors)
        assert wizard is not None

    def test_explicitly_sets_palette_faithful_style(self, qapp):
        # The Windows default is AeroStyle, which paints a fixed light
        # header/background that ignores the system dark-mode palette, rendering
        # the wizard text white-on-white. The wizard must *explicitly* select a
        # palette-faithful style (ClassicStyle) so it is never left on the
        # platform default. Asserting the final style is not enough — on Linux
        # the default is already ClassicStyle — so we verify the explicit call.
        from unittest.mock import patch

        from PySide6.QtWidgets import QWizard

        monitors = [_monitor()]
        with patch.object(QWizard, "setWizardStyle") as mock_set_style:
            FirstRunWizard(monitors=monitors)

        passed_styles = [arg for call in mock_set_style.call_args_list for arg in call.args]
        assert QWizard.WizardStyle.ClassicStyle in passed_styles
