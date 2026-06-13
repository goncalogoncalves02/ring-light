from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ringlight_overlay.core.models import ConfigData
from ringlight_overlay.hotkeys.keymap import qt_to_hotkey_string, validate_hotkeys
from ringlight_overlay.hotkeys.manager import _ACTIONS

_log = logging.getLogger(__name__)

_ACTION_LABELS: dict[str, str] = {
    "toggle_all": "Toggle All",
    "brightness_up": "Brightness Up",
    "brightness_down": "Brightness Down",
    "next_profile": "Next Profile",
    "prev_profile": "Previous Profile",
    "show_settings": "Show Settings",
}


_IDLE_PLACEHOLDER = "Click to set…"
_LISTENING_PLACEHOLDER = "Press keys…"


class _CaptureField(QLineEdit):
    """Read-only key capture field that only listens after the user clicks it.

    Capture is *armed* on click (or programmatically via ``_start_listening``).
    While armed, the next chord is converted via ``qt_to_hotkey_string`` and
    emitted on ``chord_captured``. Merely receiving focus (e.g. the first field
    on a tab) does NOT capture — that prevents stray keystrokes from rebinding.
    Tab/Backtab/Escape cancel listening; losing focus restores the prior value.
    """

    chord_captured = Signal(object)  # str | None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText(_IDLE_PLACEHOLDER)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._listening = False
        self._previous = ""

    def set_chord(self, chord: str) -> None:
        """Set the displayed chord without triggering a capture signal."""
        self.setText(chord)

    def _start_listening(self) -> None:
        self._previous = self.text()
        self._listening = True
        self.clear()
        self.setPlaceholderText(_LISTENING_PLACEHOLDER)

    def _stop_listening(self) -> None:
        self._listening = False
        self.setPlaceholderText(_IDLE_PLACEHOLDER)

    def _cancel_listening(self) -> None:
        self.setText(self._previous)
        self._stop_listening()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if not self._listening:
            self._start_listening()
        super().mousePressEvent(event)

    def focusOutEvent(self, event) -> None:  # type: ignore[override]
        if self._listening:
            self._cancel_listening()
        super().focusOutEvent(event)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if not self._listening:
            # Idle: never capture; let navigation keys behave normally.
            super().keyPressEvent(event)
            return
        key = Qt.Key(event.key())
        # Tab/Backtab move focus, Escape aborts — cancel capture and pass through.
        if key in (Qt.Key.Key_Tab, Qt.Key.Key_Backtab, Qt.Key.Key_Escape):
            self._cancel_listening()
            super().keyPressEvent(event)
            return
        chord = qt_to_hotkey_string(event.modifiers(), key)
        if chord is not None:
            self.setText(chord)
            self._stop_listening()
            self.chord_captured.emit(chord)
        # else: bare modifier — stay armed, keep waiting for the full chord.


class HotkeyEditor(QWidget):
    """Widget listing all 6 hotkey actions with capture fields.

    Emits ``hotkeys_changed(dict)`` when any binding changes and there are no
    conflicts. When conflicts exist the signal is NOT emitted and the conflict
    label turns red.
    """

    hotkeys_changed = Signal(object)  # dict[str, str]

    def __init__(self, config: ConfigData, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._hotkeys: dict[str, str] = dict(config.settings.get("hotkeys", {}))
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        group = QGroupBox("Global Hotkeys")
        form = QFormLayout(group)

        self._fields: dict[str, _CaptureField] = {}
        self._conflict_label = QLabel()
        self._conflict_label.setStyleSheet("color: red;")
        self._conflict_label.setWordWrap(True)
        self._conflict_label.hide()

        for action in _ACTIONS:
            field = _CaptureField()
            current = self._hotkeys.get(action, "")
            field.set_chord(current)
            field.chord_captured.connect(lambda chord, a=action: self._on_chord_captured(a, chord))
            label = _ACTION_LABELS.get(action, action)
            form.addRow(label + ":", field)
            self._fields[action] = field

        root.addWidget(group)
        root.addWidget(self._conflict_label)

    def _on_chord_captured(self, action: str, chord: str) -> None:
        self._hotkeys[action] = chord
        problems = validate_hotkeys(self._hotkeys)
        if problems:
            self._conflict_label.setText("\n".join(problems))
            self._conflict_label.show()
            _log.debug("Hotkey conflict: %s", problems)
        else:
            self._conflict_label.hide()
            self.hotkeys_changed.emit(dict(self._hotkeys))

    def set_binding(self, action: str, chord: str) -> None:
        """Programmatically set a binding (test helper / external update)."""
        if action not in self._fields:
            return
        self._fields[action].set_chord(chord)
        self._on_chord_captured(action, chord)

    def current_hotkeys(self) -> dict[str, str]:
        """Return a copy of the current hotkey mapping."""
        return dict(self._hotkeys)

    def has_conflicts(self) -> bool:
        """Return True if the current mapping has any conflicts."""
        return bool(validate_hotkeys(self._hotkeys))
