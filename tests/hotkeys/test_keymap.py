from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from ringlight_overlay.hotkeys.keymap import qt_to_hotkey_string, validate_hotkeys


class TestQtToHotkeyString:
    def test_ctrl_alt_l(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_L,
        )
        assert result == "ctrl+alt+l"

    def test_ctrl_alt_up(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_Up,
        )
        assert result == "ctrl+alt+up"

    def test_ctrl_alt_down(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_Down,
        )
        assert result == "ctrl+alt+down"

    def test_ctrl_alt_left(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_Left,
        )
        assert result == "ctrl+alt+left"

    def test_ctrl_alt_right(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_Right,
        )
        assert result == "ctrl+alt+right"

    def test_bare_modifier_returns_none(self):
        # Pressing only Ctrl — no real key
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier,
            Qt.Key.Key_Control,
        )
        assert result is None

    def test_bare_alt_returns_none(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.AltModifier,
            Qt.Key.Key_Alt,
        )
        assert result is None

    def test_bare_shift_returns_none(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ShiftModifier,
            Qt.Key.Key_Shift,
        )
        assert result is None

    def test_shift_included_in_output(self):
        result = qt_to_hotkey_string(
            Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier,
            Qt.Key.Key_K,
        )
        assert result == "ctrl+shift+k"

    def test_no_modifiers(self):
        result = qt_to_hotkey_string(Qt.KeyboardModifier.NoModifier, Qt.Key.Key_F5)
        assert result == "f5"

    def test_uppercase_key_lowercased(self):
        # Qt.Key_A == ord('A') == 65; result should be lowercase
        result = qt_to_hotkey_string(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_A)
        assert result == "ctrl+a"

    def test_digit_key(self):
        result = qt_to_hotkey_string(Qt.KeyboardModifier.ControlModifier, Qt.Key.Key_1)
        assert result == "ctrl+1"


class TestValidateHotkeys:
    def test_clean_mapping_returns_empty(self):
        mapping = {
            "toggle_all": "ctrl+alt+l",
            "brightness_up": "ctrl+alt+up",
            "brightness_down": "ctrl+alt+down",
            "next_profile": "ctrl+alt+right",
            "prev_profile": "ctrl+alt+left",
            "show_settings": "ctrl+alt+s",
        }
        assert validate_hotkeys(mapping) == []

    def test_duplicate_binding_reported(self):
        mapping = {
            "toggle_all": "ctrl+alt+l",
            "next_profile": "ctrl+alt+l",
        }
        problems = validate_hotkeys(mapping)
        assert len(problems) == 1
        assert "ctrl+alt+l" in problems[0]

    def test_blank_binding_reported(self):
        mapping = {"toggle_all": "", "brightness_up": "ctrl+alt+up"}
        problems = validate_hotkeys(mapping)
        assert any("toggle_all" in p for p in problems)

    def test_whitespace_only_reported(self):
        mapping = {"toggle_all": "   "}
        problems = validate_hotkeys(mapping)
        assert any("toggle_all" in p for p in problems)

    def test_case_insensitive_duplicate_detection(self):
        mapping = {"a": "Ctrl+Alt+L", "b": "ctrl+alt+l"}
        problems = validate_hotkeys(mapping)
        assert len(problems) == 1

    def test_multiple_problems(self):
        mapping = {"a": "", "b": "ctrl+x", "c": "ctrl+x"}
        problems = validate_hotkeys(mapping)
        # blank + duplicate
        assert len(problems) == 2
