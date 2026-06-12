from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import patch

import pytest
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

from ringlight_overlay.core.models import Profile
from ringlight_overlay.ui.tray import TrayIcon, _app_icon


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


def test_tray_icon_uses_placeholder_when_file_absent(qapp, tmp_path: Path) -> None:
    """When app_icon_path() points to a non-existent file, TrayIcon still
    constructs successfully and its icon() is non-null (placeholder fallback)."""
    absent = tmp_path / "nonexistent.ico"
    with patch("ringlight_overlay.ui.tray.app_icon_path", return_value=absent):
        profiles = _profiles()
        tray = TrayIcon(profiles=profiles, active_profile_id=profiles[0].id)
        assert tray is not None
        assert not tray.icon().isNull()


def test_app_icon_returns_qicon_instance(qapp) -> None:
    """_app_icon() returns a QIcon regardless of whether the file is loadable."""
    result = _app_icon()
    assert isinstance(result, QIcon)
