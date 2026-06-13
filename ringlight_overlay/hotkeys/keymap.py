from __future__ import annotations

from PySide6.QtCore import Qt

# Modifier keys — pressing only these should not commit a chord
_MODIFIER_KEYS = frozenset(
    {
        Qt.Key.Key_Control,
        Qt.Key.Key_Shift,
        Qt.Key.Key_Alt,
        Qt.Key.Key_Meta,
        Qt.Key.Key_AltGr,
        Qt.Key.Key_Super_L,
        Qt.Key.Key_Super_R,
    }
)

# Qt.Key → keyboard-lib name for non-printable / special keys
_KEY_NAME_MAP: dict[Qt.Key, str] = {
    Qt.Key.Key_Up: "up",
    Qt.Key.Key_Down: "down",
    Qt.Key.Key_Left: "left",
    Qt.Key.Key_Right: "right",
    Qt.Key.Key_Return: "enter",
    Qt.Key.Key_Enter: "enter",
    Qt.Key.Key_Escape: "esc",
    Qt.Key.Key_Tab: "tab",
    Qt.Key.Key_Backspace: "backspace",
    Qt.Key.Key_Delete: "delete",
    Qt.Key.Key_Insert: "insert",
    Qt.Key.Key_Home: "home",
    Qt.Key.Key_End: "end",
    Qt.Key.Key_PageUp: "page up",
    Qt.Key.Key_PageDown: "page down",
    Qt.Key.Key_Space: "space",
    Qt.Key.Key_F1: "f1",
    Qt.Key.Key_F2: "f2",
    Qt.Key.Key_F3: "f3",
    Qt.Key.Key_F4: "f4",
    Qt.Key.Key_F5: "f5",
    Qt.Key.Key_F6: "f6",
    Qt.Key.Key_F7: "f7",
    Qt.Key.Key_F8: "f8",
    Qt.Key.Key_F9: "f9",
    Qt.Key.Key_F10: "f10",
    Qt.Key.Key_F11: "f11",
    Qt.Key.Key_F12: "f12",
}


def qt_to_hotkey_string(
    modifiers: Qt.KeyboardModifier,
    key: Qt.Key,
) -> str | None:
    """Convert a Qt key event's modifiers + key to a keyboard-lib hotkey string.

    Returns a string like ``"ctrl+alt+l"`` or ``"ctrl+alt+up"``.
    Returns ``None`` when the key itself is a modifier (bare modifier chord).
    """
    if key in _MODIFIER_KEYS:
        return None

    parts: list[str] = []
    if modifiers & Qt.KeyboardModifier.ControlModifier:
        parts.append("ctrl")
    if modifiers & Qt.KeyboardModifier.AltModifier:
        parts.append("alt")
    if modifiers & Qt.KeyboardModifier.ShiftModifier:
        parts.append("shift")
    if modifiers & Qt.KeyboardModifier.MetaModifier:
        parts.append("meta")

    key_name = _KEY_NAME_MAP.get(key)
    if key_name is None:
        # For printable keys Qt.Key_A–Qt.Key_Z / digits, the enum value equals
        # the ASCII/Unicode code point — chr() gives the right character.
        ch = chr(int(key))
        if ch.isprintable() and ch.strip():
            key_name = ch.lower()
        else:
            # Unknown or non-printable key — cannot represent
            return None

    parts.append(key_name)
    return "+".join(parts)


def validate_hotkeys(mapping: dict[str, str]) -> list[str]:
    """Check a hotkey mapping for conflicts and blank entries.

    Returns a list of human-readable problem strings (English).
    Returns an empty list when the mapping is clean.
    """
    problems: list[str] = []

    # Detect blank entries
    for action, binding in mapping.items():
        if not binding or not binding.strip():
            problems.append(f"Action '{action}' has no binding assigned.")

    # Detect duplicates (same non-empty binding used by more than one action)
    seen: dict[str, str] = {}
    for action, binding in mapping.items():
        if not binding or not binding.strip():
            continue
        normalized = binding.strip().lower()
        if normalized in seen:
            problems.append(
                f"Conflict: '{action}' and '{seen[normalized]}' " f"both use '{binding}'."
            )
        else:
            seen[normalized] = action

    return problems
