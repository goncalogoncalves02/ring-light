from __future__ import annotations

from unittest.mock import MagicMock

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

from ringlight_overlay.ui.theme import apply_theme, build_dark_palette, build_light_palette


def test_dark_palette_has_high_contrast_between_window_and_text():
    palette = build_dark_palette()
    window = palette.color(QPalette.ColorRole.Window)
    text = palette.color(QPalette.ColorRole.WindowText)
    assert abs(window.lightness() - text.lightness()) > 100


def test_dark_palette_window_is_dark():
    palette = build_dark_palette()
    window = palette.color(QPalette.ColorRole.Window)
    assert window.lightness() < 100


def test_light_palette_has_high_contrast_between_window_and_text():
    palette = build_light_palette()
    window = palette.color(QPalette.ColorRole.Window)
    text = palette.color(QPalette.ColorRole.WindowText)
    assert abs(window.lightness() - text.lightness()) > 100


def test_light_palette_window_is_light():
    palette = build_light_palette()
    window = palette.color(QPalette.ColorRole.Window)
    assert window.lightness() > 200


def test_dark_palette_tooltip_text_is_readable_against_tooltip_base():
    # Regression: ToolTipBase and ToolTipText were both set to the same
    # white color, making every tooltip render white-on-white under dark
    # mode — the exact class of bug this module exists to prevent.
    palette = build_dark_palette()
    tooltip_base = palette.color(QPalette.ColorRole.ToolTipBase)
    tooltip_text = palette.color(QPalette.ColorRole.ToolTipText)
    assert abs(tooltip_base.lightness() - tooltip_text.lightness()) > 100


def test_disabled_text_is_visible_but_dimmer_than_active_text_dark():
    palette = build_dark_palette()
    active = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText)
    disabled = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
    window = palette.color(QPalette.ColorRole.Window)
    assert disabled.lightness() < active.lightness()
    assert abs(disabled.lightness() - window.lightness()) > 40


def _make_app(scheme: Qt.ColorScheme) -> MagicMock:
    app = MagicMock()
    app.styleHints.return_value.colorScheme.return_value = scheme
    return app


def test_apply_theme_forces_fusion_style():
    app = _make_app(Qt.ColorScheme.Light)
    apply_theme(app)
    app.setStyle.assert_called_once_with("Fusion")


def test_apply_theme_dark_scheme_applies_dark_palette():
    app = _make_app(Qt.ColorScheme.Dark)
    apply_theme(app)
    applied = app.setPalette.call_args.args[0]
    expected = build_dark_palette()
    assert applied.color(QPalette.ColorRole.Window) == expected.color(QPalette.ColorRole.Window)
    assert applied.color(QPalette.ColorRole.WindowText) == expected.color(
        QPalette.ColorRole.WindowText
    )


def test_apply_theme_light_scheme_applies_light_palette():
    app = _make_app(Qt.ColorScheme.Light)
    apply_theme(app)
    applied = app.setPalette.call_args.args[0]
    expected = build_light_palette()
    assert applied.color(QPalette.ColorRole.Window) == expected.color(QPalette.ColorRole.Window)


def test_apply_theme_unknown_scheme_falls_back_to_light():
    app = _make_app(Qt.ColorScheme.Unknown)
    apply_theme(app)
    applied = app.setPalette.call_args.args[0]
    expected = build_light_palette()
    assert applied.color(QPalette.ColorRole.Window) == expected.color(QPalette.ColorRole.Window)
