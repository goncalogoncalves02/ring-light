from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from ringlight_overlay.core.models import Profile
from ringlight_overlay.core.resources import app_icon_path


def _placeholder_icon() -> QIcon:
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(255, 200, 50))
    return QIcon(pixmap)


def _app_icon() -> QIcon:
    """Return the app icon loaded from the bundled favicon.ico, or the
    placeholder when the file is absent or the icon cannot be loaded."""
    path = app_icon_path()
    if path.exists():
        icon = QIcon(str(path))
        if not icon.isNull():
            return icon
    return _placeholder_icon()


class TrayIcon(QSystemTrayIcon):
    """System tray icon with profile switcher and overlay controls."""

    profile_selected = Signal(str)
    toggle_all_requested = Signal()
    brightness_up_requested = Signal()
    brightness_down_requested = Signal()
    next_profile_requested = Signal()
    prev_profile_requested = Signal()
    show_settings_requested = Signal()
    about_requested = Signal()
    quit_requested = Signal()

    def __init__(
        self,
        profiles: list[Profile],
        active_profile_id: str,
        parent=None,
    ) -> None:
        super().__init__(_app_icon(), parent)
        self.setToolTip("RingLight Overlay")
        self._build_menu(profiles, active_profile_id)
        self.activated.connect(self._on_activated)

    def update_profiles(self, profiles: list[Profile], active_profile_id: str) -> None:
        """Rebuild context menu with updated profile list."""
        self._build_menu(profiles, active_profile_id)

    def _build_menu(self, profiles: list[Profile], active_profile_id: str) -> None:
        menu = QMenu()
        for profile in profiles:
            action = menu.addAction(profile.name)
            action.setCheckable(True)
            action.setChecked(profile.id == active_profile_id)
            action.triggered.connect(
                lambda _checked, pid=profile.id: self.profile_selected.emit(pid)
            )
        menu.addSeparator()
        menu.addAction("Toggle All").triggered.connect(self.toggle_all_requested)
        menu.addAction("Brightness +").triggered.connect(self.brightness_up_requested)
        menu.addAction("Brightness -").triggered.connect(self.brightness_down_requested)
        menu.addSeparator()
        menu.addAction("Settings...").triggered.connect(self.show_settings_requested)
        menu.addAction("About...").triggered.connect(self.about_requested)
        menu.addAction("Quit").triggered.connect(self.quit_requested)
        if old := self.contextMenu():
            old.deleteLater()
        self.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_settings_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_all_requested.emit()
