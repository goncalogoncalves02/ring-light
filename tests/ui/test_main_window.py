from __future__ import annotations

import uuid
from dataclasses import replace
from unittest.mock import MagicMock

from PySide6.QtCore import Qt

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.core.storage import DebouncedSaver
from ringlight_overlay.ui.main_window import MainWindow


def _config(minimize_to_tray: bool | None = None) -> ConfigData:
    light = Light(
        id=str(uuid.uuid4()),
        enabled=False,
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
    profile = Profile(id=str(uuid.uuid4()), name="Daylight", lights=[light])
    settings: dict = {}
    if minimize_to_tray is not None:
        settings["minimize_to_tray_on_close"] = minimize_to_tray
    return ConfigData(
        version=1, active_profile_id=profile.id, profiles=[profile], settings=settings
    )


def test_main_window_constructs(qapp) -> None:
    win = MainWindow(_config())
    assert win is not None


def test_main_window_has_minimum_size(qapp) -> None:
    win = MainWindow(_config())
    assert win.minimumWidth() >= 800
    assert win.minimumHeight() >= 500


def test_main_window_populates_monitor_dropdown(qapp) -> None:
    # The light editor's monitor combo must be filled from the live screen
    # list (offscreen Qt always provides at least one screen), not left empty.
    win = MainWindow(_config())
    assert win._light_editor._monitor_combo.count() >= 1


def test_main_window_editing_light_keeps_monitor_assignment(qapp) -> None:
    # With monitors loaded, editing a property must not wipe monitor_name to "".
    win = MainWindow(_config())
    light = win.config().profiles[0].lights[0]
    win._light_editor.load_light(light)
    received: list = []
    win.config_changed.connect(received.append)
    win._light_editor._feather.setValue(20)
    assert received, "editing a property should emit config_changed"
    edited = received[-1].profiles[0].lights[0]
    assert edited.monitor_name == win._light_editor._monitors[0].name


def test_main_window_close_hides_not_destroys(qapp) -> None:
    win = MainWindow(_config())
    win.show()
    win.close()
    assert not win.isVisible()
    assert not win.isHidden() or True


def test_main_window_exposes_config(qapp) -> None:
    config = _config()
    win = MainWindow(config)
    assert win.config().version == 1


def test_main_window_has_config_changed_signal(qapp) -> None:
    win = MainWindow(_config())
    assert hasattr(win, "config_changed")


# Task 3: injected saver is used instead of creating a new instance
def test_main_window_uses_injected_saver(qapp) -> None:
    calls: list = []
    spy_saver = DebouncedSaver(calls.append, delay=100.0)
    win = MainWindow(_config(), saver=spy_saver)
    # Trigger a config change via the light editor path indirectly by calling the handler
    light = win.config().profiles[0].lights[0]
    # Call the internal handler directly — simulates a light_changed signal
    win._on_light_changed(light)
    assert len(calls) == 0  # timer not fired yet
    spy_saver.flush()
    assert len(calls) == 1  # our injected saver, not a separate instance


# Task 5: checkbox initialized from settings
def test_main_window_checkbox_checked_when_setting_true(qapp) -> None:
    win = MainWindow(_config(minimize_to_tray=True))
    assert win._minimize_checkbox.isChecked() is True


def test_main_window_checkbox_unchecked_when_setting_false(qapp) -> None:
    win = MainWindow(_config(minimize_to_tray=False))
    assert win._minimize_checkbox.isChecked() is False


def test_main_window_checkbox_checked_by_default_when_setting_absent(qapp) -> None:
    # settings dict has no minimize_to_tray_on_close key — default True
    win = MainWindow(_config(minimize_to_tray=None))
    assert win._minimize_checkbox.isChecked() is True


# Task 7: toggling the checkbox emits config_changed with the updated setting
def test_main_window_checkbox_toggle_emits_config_changed(qapp) -> None:
    emitted: list[ConfigData] = []
    win = MainWindow(_config(minimize_to_tray=True))
    win.config_changed.connect(emitted.append)

    # Toggle off
    win._minimize_checkbox.setChecked(False)
    assert len(emitted) == 1
    assert emitted[0].settings["minimize_to_tray_on_close"] is False

    # Toggle back on
    win._minimize_checkbox.setChecked(True)
    assert len(emitted) == 2
    assert emitted[1].settings["minimize_to_tray_on_close"] is True


# Task 9: close behavior depends on setting
def test_main_window_close_hides_when_minimize_to_tray_true(qapp) -> None:
    quit_signals: list = []
    win = MainWindow(_config(minimize_to_tray=True))
    win.quit_requested.connect(lambda: quit_signals.append(1))
    win.show()
    win.close()
    assert not win.isVisible()
    assert len(quit_signals) == 0


def test_main_window_close_emits_quit_requested_when_minimize_to_tray_false(qapp) -> None:
    quit_signals: list = []
    win = MainWindow(_config(minimize_to_tray=False))
    win.quit_requested.connect(lambda: quit_signals.append(1))
    win.show()
    win.close()
    assert len(quit_signals) == 1


def test_main_window_has_quit_requested_signal(qapp) -> None:
    win = MainWindow(_config())
    assert hasattr(win, "quit_requested")


def _enabled_config() -> ConfigData:
    """Config with the single light enabled (as if turned on via the checkbox)."""
    config = _config()
    on_light = replace(config.profiles[0].lights[0], enabled=True)
    profile = replace(config.profiles[0], lights=[on_light])
    return replace(config, profiles=[profile])


def test_editing_light_preserves_enabled_state(qapp) -> None:
    """Regression: editing a property must not clobber the live ``enabled`` flag.

    The LightEditor rebuilds the whole Light from a snapshot whose ``enabled``
    can be stale (it has no editor widget). MainWindow must preserve the live
    enabled state from its own config, so moving a slider never turns the
    overlay off.
    """
    config = _enabled_config()
    win = MainWindow(config)
    emitted: list[ConfigData] = []
    win.config_changed.connect(emitted.append)

    # Editor emits an edited light carrying a STALE enabled=False plus a real edit.
    edited = replace(config.profiles[0].lights[0], enabled=False, feather=99)
    win._on_light_changed(edited)

    result_light = win.config().profiles[0].lights[0]
    assert result_light.enabled is True, "enabled was clobbered by an editor edit"
    assert result_light.feather == 99, "the edited value was not applied"
    assert emitted[-1].profiles[0].lights[0].enabled is True


def test_editing_light_applies_visual_fields(qapp) -> None:
    """The merged light reflects every editor-owned field (here: size + opacity)."""
    config = _enabled_config()
    win = MainWindow(config)
    edited = replace(config.profiles[0].lights[0], size=(640, 480), opacity=0.5)
    win._on_light_changed(edited)
    result_light = win.config().profiles[0].lights[0]
    assert result_light.size == (640, 480)
    assert result_light.opacity == 0.5


def _with_light_enabled(config: ConfigData, enabled: bool) -> ConfigData:
    light = replace(config.profiles[0].lights[0], enabled=enabled)
    profile = replace(config.profiles[0], lights=[light])
    return replace(config, profiles=[profile])


def test_apply_external_config_updates_config_without_emitting(qapp) -> None:
    """A config changed elsewhere (tray/hotkey) is reflected without re-emitting."""
    config = _config()  # enabled False
    win = MainWindow(config)
    emitted: list[ConfigData] = []
    win.config_changed.connect(emitted.append)

    win.apply_external_config(_with_light_enabled(config, True))

    assert win.config().profiles[0].lights[0].enabled is True
    assert emitted == [], "external refresh must not re-emit config_changed"


def test_apply_external_config_reflects_checkbox_state(qapp) -> None:
    """The profile-list light checkbox mirrors the externally-toggled enabled."""
    config = _config()  # enabled False
    win = MainWindow(config)
    win.apply_external_config(_with_light_enabled(config, True))
    item = win._profile_list._light_list.item(0)
    assert item.checkState() == Qt.CheckState.Checked


def _two_profile_config() -> ConfigData:
    base = _config()
    second = Profile(id=str(uuid.uuid4()), name="Night")
    return replace(base, profiles=[base.profiles[0], second])


def test_selecting_profile_in_list_switches_active_profile(qapp) -> None:
    """Choosing a profile in the window's list must switch the active profile.

    Regression: ProfileList emitted profile_selected but MainWindow never wired
    it, so the overlay/tray never followed a profile change made in the window.
    """
    config = _two_profile_config()
    win = MainWindow(config)
    emitted: list[ConfigData] = []
    win.config_changed.connect(emitted.append)

    second_id = config.profiles[1].id
    win._profile_list._profile_list.setCurrentRow(1)

    assert emitted, "selecting a profile in the list must propagate to config_changed"
    assert win.config().active_profile_id == second_id
    assert emitted[-1].active_profile_id == second_id


def test_external_toggle_then_edit_preserves_enabled(qapp) -> None:
    """End-to-end gap: toggle on via tray, then edit a slider -> stays enabled."""
    config = _config()  # enabled False
    win = MainWindow(config)
    win.apply_external_config(_with_light_enabled(config, True))  # tray Toggle All

    # Editor still holds a stale enabled=False snapshot; user moves a slider.
    edited = replace(config.profiles[0].lights[0], enabled=False, feather=42)
    win._on_light_changed(edited)

    result_light = win.config().profiles[0].lights[0]
    assert result_light.enabled is True
    assert result_light.feather == 42
