from __future__ import annotations

import logging
import sys
from typing import Callable

import keyboard  # type: ignore[import-untyped]
from PySide6.QtCore import QObject, Signal

from ringlight_overlay.core.models import ConfigData

_log = logging.getLogger(__name__)
_IS_WINDOWS = sys.platform == "win32"

_ACTIONS = (
    "toggle_all",
    "brightness_up",
    "brightness_down",
    "next_profile",
    "prev_profile",
    "show_settings",
)


class HotkeyManager(QObject):
    """Registers global hotkeys and re-emits them as Qt signals."""

    toggle_all_requested = Signal()
    brightness_up_requested = Signal()
    brightness_down_requested = Signal()
    next_profile_requested = Signal()
    prev_profile_requested = Signal()
    show_settings_requested = Signal()

    def __init__(self, config: ConfigData, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._handles: dict[str, object] = {}
        self._register_all(config)

    def reload(self, config: ConfigData) -> None:
        """Unregister all current hotkeys then register from new config."""
        self._unregister_all()
        self._register_all(config)

    def shutdown(self) -> None:
        """Unregister all hotkeys; call on app exit."""
        self._unregister_all()

    def _register_all(self, config: ConfigData) -> None:
        if not _IS_WINDOWS:
            _log.warning("HotkeyManager: off Windows (%s) — skipped", sys.platform)
            return
        hotkeys: dict[str, str] = config.settings.get("hotkeys", {})
        signal_map = {
            "toggle_all": self.toggle_all_requested,
            "brightness_up": self.brightness_up_requested,
            "brightness_down": self.brightness_down_requested,
            "next_profile": self.next_profile_requested,
            "prev_profile": self.prev_profile_requested,
            "show_settings": self.show_settings_requested,
        }
        for action in _ACTIONS:
            hotkey_str = hotkeys.get(action)
            if not hotkey_str:
                _log.warning("HotkeyManager: no binding for %r", action)
                continue
            self._register_one(action, hotkey_str, signal_map[action].emit)

    def _register_one(self, action: str, hotkey_str: str, callback: Callable[[], None]) -> None:
        try:
            handle = keyboard.add_hotkey(hotkey_str, callback, suppress=False)
            self._handles[action] = handle
            _log.debug("registered %r → %r", action, hotkey_str)
        except Exception as exc:
            _log.warning("failed to register %r (%r): %s", action, hotkey_str, exc)

    def _unregister_all(self) -> None:
        if not _IS_WINDOWS:
            return
        for action, handle in list(self._handles.items()):
            try:
                keyboard.remove_hotkey(handle)
            except Exception as exc:
                _log.warning("failed to unregister %r: %s", action, exc)
        self._handles.clear()
