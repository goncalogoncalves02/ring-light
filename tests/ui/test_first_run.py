from __future__ import annotations

import pytest
from PySide6.QtWidgets import QComboBox, QLabel

from ringlight_overlay.core.monitors import MonitorInfo
from ringlight_overlay.core.storage import default_config
from ringlight_overlay.ui.dialogs.first_run import (
    FirstRunWizard,
    apply_wizard_result,
    build_first_run_light,
)
from ringlight_overlay.ui.theme import build_dark_palette


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


class TestWizardLegibilityUnderDarkPalette:
    def test_monitor_page_text_is_legible_under_dark_palette(self, qapp):
        # Regression test for the bug reported after #17: the wizard's first
        # page rendered with invisible/blank text on real Windows dark mode
        # even after forcing QWizard.ClassicStyle. Forcing Fusion + an
        # explicit dark palette (see ui/theme.py) must produce visibly
        # bright text pixels under the label and combo box, not just a
        # dark-on-dark or blank render.
        original_palette = qapp.palette()
        original_style_name = qapp.style().objectName()
        qapp.setStyle("Fusion")
        qapp.setPalette(build_dark_palette())

        wizard = None
        try:
            monitors = [_monitor()]
            wizard = FirstRunWizard(monitors=monitors)
            wizard.resize(600, 400)
            wizard.show()
            qapp.processEvents()

            image = wizard.grab().toImage()

            monitor_label = next(w for w in wizard.findChildren(QLabel) if w.text() == "Monitor:")
            combo = wizard.findChildren(QComboBox)[0]

            label_pos = monitor_label.mapTo(wizard, monitor_label.rect().topLeft())
            combo_pos = combo.mapTo(wizard, combo.rect().topLeft())

            def max_lightness(x0: int, y0: int, width: int, height: int) -> int:
                best = 0
                for y in range(y0, y0 + height):
                    for x in range(x0, x0 + width):
                        best = max(best, image.pixelColor(x, y).lightness())
                return best

            label_brightness = max_lightness(
                label_pos.x(), label_pos.y(), monitor_label.width(), monitor_label.height()
            )
            combo_brightness = max_lightness(
                combo_pos.x(), combo_pos.y(), combo.width(), combo.height()
            )

            # Dark palette background is ~lightness 35-71; legible white/light
            # text glyphs must push well above that. A white-on-white or
            # blank-content regression collapses both to the background level.
            assert label_brightness > 140
            assert combo_brightness > 140
        finally:
            if wizard is not None:
                wizard.close()
                wizard.deleteLater()
            qapp.setPalette(original_palette)
            qapp.setStyle(original_style_name)
            qapp.processEvents()
