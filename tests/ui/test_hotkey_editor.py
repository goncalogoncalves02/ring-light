from __future__ import annotations

import pytest
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QKeyEvent

from ringlight_overlay.core.storage import default_config
from ringlight_overlay.hotkeys.manager import _ACTIONS
from ringlight_overlay.ui.widgets.hotkey_editor import HotkeyEditor


def _config():
    return default_config()


def _key_event(key: Qt.Key, modifiers: Qt.KeyboardModifier) -> QKeyEvent:
    return QKeyEvent(QEvent.Type.KeyPress, key, modifiers)


_CTRL_ALT = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier


class TestCaptureFieldArming:
    def test_focused_field_does_not_capture_until_armed(self, qapp):
        editor = HotkeyEditor(_config())
        field = editor._fields["toggle_all"]
        original = field.text()
        captured: list = []
        field.chord_captured.connect(captured.append)

        # Merely having focus must NOT capture — the field is idle until clicked.
        field.keyPressEvent(_key_event(Qt.Key.Key_L, _CTRL_ALT))
        assert captured == []
        assert field.text() == original

    def test_captures_after_arming(self, qapp):
        editor = HotkeyEditor(_config())
        field = editor._fields["toggle_all"]
        captured: list = []
        field.chord_captured.connect(captured.append)

        field._start_listening()  # simulates a click into the field
        field.keyPressEvent(_key_event(Qt.Key.Key_L, _CTRL_ALT))
        assert captured == ["ctrl+alt+l"]
        assert field.text() == "ctrl+alt+l"

    def test_escape_cancels_and_restores_previous(self, qapp):
        editor = HotkeyEditor(_config())
        field = editor._fields["toggle_all"]
        original = field.text()
        captured: list = []
        field.chord_captured.connect(captured.append)

        field._start_listening()
        field.keyPressEvent(_key_event(Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier))
        assert captured == []
        assert field.text() == original


class TestHotkeyEditorConstruction:
    def test_constructs(self, qapp):
        editor = HotkeyEditor(_config())
        assert editor is not None

    def test_has_one_row_per_action(self, qapp):
        editor = HotkeyEditor(_config())
        # Each action should have a _CaptureField registered
        assert set(editor._fields.keys()) == set(_ACTIONS)
        assert len(editor._fields) == len(_ACTIONS)

    def test_prefilled_from_config(self, qapp):
        config = _config()
        editor = HotkeyEditor(config)
        hotkeys = config.settings["hotkeys"]
        for action, binding in hotkeys.items():
            assert editor._fields[action].text() == binding


class TestHotkeyEditorEmission:
    def test_emits_hotkeys_changed_on_clean_capture(self, qapp):
        editor = HotkeyEditor(_config())
        received: list[dict] = []
        editor.hotkeys_changed.connect(received.append)

        # Change toggle_all to a unique binding
        editor.set_binding("toggle_all", "ctrl+alt+z")
        assert len(received) == 1
        assert received[0]["toggle_all"] == "ctrl+alt+z"

    def test_emitted_dict_contains_all_actions(self, qapp):
        editor = HotkeyEditor(_config())
        received: list[dict] = []
        editor.hotkeys_changed.connect(received.append)

        editor.set_binding("show_settings", "ctrl+alt+p")
        assert len(received) == 1
        assert set(received[0].keys()) == set(_ACTIONS)

    def test_does_not_emit_on_conflict(self, qapp):
        editor = HotkeyEditor(_config())
        received: list[dict] = []
        editor.hotkeys_changed.connect(received.append)

        # Assign a duplicate binding
        editor.set_binding("toggle_all", "ctrl+alt+up")  # same as brightness_up default
        # Should NOT emit because of conflict
        assert len(received) == 0

    def test_conflict_shows_conflict_label(self, qapp):
        editor = HotkeyEditor(_config())
        editor.set_binding("toggle_all", "ctrl+alt+up")  # duplicate
        # Label is shown (not hidden) when a conflict exists
        assert not editor._conflict_label.isHidden()

    def test_conflict_resolved_hides_label(self, qapp):
        editor = HotkeyEditor(_config())
        # Create conflict
        editor.set_binding("toggle_all", "ctrl+alt+up")
        assert not editor._conflict_label.isHidden()
        # Resolve by assigning unique binding
        editor.set_binding("toggle_all", "ctrl+alt+z")
        assert editor._conflict_label.isHidden()

    def test_has_conflicts_method(self, qapp):
        editor = HotkeyEditor(_config())
        assert not editor.has_conflicts()
        editor.set_binding("toggle_all", "ctrl+alt+up")
        assert editor.has_conflicts()
