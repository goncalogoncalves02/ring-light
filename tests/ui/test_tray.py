from __future__ import annotations

import uuid

from PySide6.QtWidgets import QSystemTrayIcon

from ringlight_overlay.core.models import Profile
from ringlight_overlay.ui.tray import TrayIcon


def _profiles() -> list[Profile]:
    return [
        Profile(id=str(uuid.uuid4()), name="Daylight"),
        Profile(id=str(uuid.uuid4()), name="Night"),
    ]


def test_tray_icon_can_be_constructed(qapp) -> None:
    profiles = _profiles()
    tray = TrayIcon(profiles=profiles, active_profile_id=profiles[0].id)
    assert tray is not None


def test_tray_icon_has_context_menu(qapp) -> None:
    profiles = _profiles()
    tray = TrayIcon(profiles=profiles, active_profile_id=profiles[0].id)
    assert tray.contextMenu() is not None


def test_tray_icon_menu_has_profile_actions(qapp) -> None:
    profiles = _profiles()
    tray = TrayIcon(profiles=profiles, active_profile_id=profiles[0].id)
    menu = tray.contextMenu()
    action_texts = [a.text() for a in menu.actions() if not a.isSeparator()]
    assert "Daylight" in action_texts
    assert "Night" in action_texts


def test_tray_icon_has_required_signals(qapp) -> None:
    profiles = _profiles()
    tray = TrayIcon(profiles=profiles, active_profile_id=profiles[0].id)
    assert hasattr(tray, "profile_selected")
    assert hasattr(tray, "toggle_all_requested")
    assert hasattr(tray, "show_settings_requested")
    assert hasattr(tray, "quit_requested")


def test_tray_update_profiles_replaces_menu(qapp) -> None:
    profiles = _profiles()
    tray = TrayIcon(profiles=profiles, active_profile_id=profiles[0].id)
    new_profile = Profile(id=str(uuid.uuid4()), name="Studio")
    tray.update_profiles([new_profile], new_profile.id)
    menu = tray.contextMenu()
    action_texts = [a.text() for a in menu.actions() if not a.isSeparator()]
    assert "Studio" in action_texts
    assert "Daylight" not in action_texts
