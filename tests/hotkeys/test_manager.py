from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from ringlight_overlay.core.storage import default_config
from ringlight_overlay.hotkeys.manager import HotkeyManager


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_registers_six_hotkeys_on_init(mock_kb, qapp) -> None:
    cfg = default_config()
    mgr = HotkeyManager(cfg)
    assert mock_kb.add_hotkey.call_count == 6
    mgr.shutdown()


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_registers_correct_hotkey_strings(mock_kb, qapp) -> None:
    cfg = default_config()
    mgr = HotkeyManager(cfg)
    registered = {call.args[0] for call in mock_kb.add_hotkey.call_args_list}
    hotkeys = cfg.settings["hotkeys"]
    for key in hotkeys.values():
        assert key in registered
    mgr.shutdown()


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_reload_unregisters_and_reregisters(mock_kb, qapp) -> None:
    cfg = default_config()
    mock_kb.add_hotkey.side_effect = [object() for _ in range(12)]
    mgr = HotkeyManager(cfg)
    assert mock_kb.add_hotkey.call_count == 6
    mgr.reload(cfg)
    assert mock_kb.remove_hotkey.call_count == 6
    assert mock_kb.add_hotkey.call_count == 12
    mgr.shutdown()


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_shutdown_unregisters_all(mock_kb, qapp) -> None:
    cfg = default_config()
    mock_kb.add_hotkey.side_effect = [object() for _ in range(6)]
    mgr = HotkeyManager(cfg)
    mgr.shutdown()
    assert mock_kb.remove_hotkey.call_count == 6
    assert len(mgr._handles) == 0


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_shutdown_twice_is_safe(mock_kb, qapp) -> None:
    cfg = default_config()
    mgr = HotkeyManager(cfg)
    mgr.shutdown()
    count_after_first = mock_kb.remove_hotkey.call_count
    mgr.shutdown()
    assert mock_kb.remove_hotkey.call_count == count_after_first


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_callback_emits_signal(mock_kb, qapp) -> None:
    cfg = default_config()
    mgr = HotkeyManager(cfg)

    received: list[None] = []
    mgr.toggle_all_requested.connect(lambda: received.append(None))

    toggle_str = cfg.settings["hotkeys"]["toggle_all"]
    callback = None
    for call in mock_kb.add_hotkey.call_args_list:
        if call.args[0] == toggle_str:
            callback = call.args[1]
            break

    assert callback is not None
    callback()
    QApplication.processEvents()

    assert len(received) == 1
    mgr.shutdown()


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", False)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_no_registration_off_windows(mock_kb, qapp) -> None:
    cfg = default_config()
    mgr = HotkeyManager(cfg)
    mock_kb.add_hotkey.assert_not_called()
    mgr.shutdown()


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", False)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_reload_noop_off_windows(mock_kb, qapp) -> None:
    cfg = default_config()
    mgr = HotkeyManager(cfg)
    mgr.reload(cfg)
    mock_kb.add_hotkey.assert_not_called()
    mock_kb.remove_hotkey.assert_not_called()


@patch("ringlight_overlay.hotkeys.manager._IS_WINDOWS", True)
@patch("ringlight_overlay.hotkeys.manager.keyboard")
def test_registration_failure_does_not_raise(mock_kb, qapp) -> None:
    mock_kb.add_hotkey.side_effect = Exception("access denied")
    cfg = default_config()
    mgr = HotkeyManager(cfg)
    assert len(mgr._handles) == 0
    mgr.shutdown()
