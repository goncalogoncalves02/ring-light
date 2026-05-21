from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from ringlight_overlay.core.models import Profile


def _placeholder_icon() -> QIcon:
    pixmap = QPixmap(16, 16)
    pixmap.fill(QColor(255, 200, 50))
    return QIcon(pixmap)


class TrayIcon(QSystemTrayIcon):
    """System tray icon with profile switcher and overlay controls."""

    profile_selected = Signal(str)
    toggle_all_requested = Signal()
    brightness_up_requested = Signal()
    brightness_down_requested = Signal()
    show_settings_requested = Signal()
    quit_requested = Signal()

    def __init__(
        self,
        profiles: list[Profile],
        active_profile_id: str,
        parent=None,
    ) -> None:
        super().__init__(_placeholder_icon(), parent)
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
        menu.addAction("Quit").triggered.connect(self.quit_requested)
        if old := self.contextMenu():
            old.deleteLater()
        self.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_settings_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_all_requested.emit()
