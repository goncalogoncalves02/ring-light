from __future__ import annotations

import uuid

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ringlight_overlay.core.models import ConfigData, Light, Profile


class ProfileList(QWidget):
    """Left sidebar: profile CRUD + lights list for the active profile."""

    profile_selected = Signal(str)
    light_selected = Signal(str)
    config_changed = Signal(object)

    def __init__(self, config: ConfigData, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._build_ui()
        self._populate_profiles()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        root.addWidget(QLabel("Profiles"))
        self._profile_list = QListWidget()
        root.addWidget(self._profile_list)

        profile_btns = QHBoxLayout()
        self._btn_add_profile = QPushButton("+")
        self._btn_remove_profile = QPushButton("-")
        self._btn_rename_profile = QPushButton("Rename")
        profile_btns.addWidget(self._btn_add_profile)
        profile_btns.addWidget(self._btn_remove_profile)
        profile_btns.addWidget(self._btn_rename_profile)
        root.addLayout(profile_btns)

        root.addWidget(QLabel("Lights"))
        self._light_list = QListWidget()
        root.addWidget(self._light_list)

        light_btns = QHBoxLayout()
        self._btn_add_light = QPushButton("+")
        self._btn_remove_light = QPushButton("-")
        light_btns.addWidget(self._btn_add_light)
        light_btns.addWidget(self._btn_remove_light)
        root.addLayout(light_btns)

        self._profile_list.currentRowChanged.connect(self._on_profile_row_changed)
        self._light_list.currentRowChanged.connect(self._on_light_row_changed)
        self._light_list.itemChanged.connect(self._on_light_item_changed)
        self._btn_add_profile.clicked.connect(self._add_profile)
        self._btn_remove_profile.clicked.connect(self._remove_profile)
        self._btn_rename_profile.clicked.connect(self._rename_profile)
        self._btn_add_light.clicked.connect(self._add_light)
        self._btn_remove_light.clicked.connect(self._remove_light)

    def apply_external_config(self, config: ConfigData) -> None:
        """Refresh the sidebar to reflect a config changed elsewhere (tray/hotkey).

        Repopulates with signals blocked so no handler fires and nothing is
        re-emitted — the external source already persisted the change.
        """
        self._config = config
        self._profile_list.blockSignals(True)
        self._light_list.blockSignals(True)
        try:
            self._populate_profiles()
            active = self._active_profile()
            if active is not None:
                self._populate_lights(active)
        finally:
            self._profile_list.blockSignals(False)
            self._light_list.blockSignals(False)

    def _populate_profiles(self) -> None:
        self._profile_list.clear()
        for profile in self._config.profiles:
            item = QListWidgetItem(profile.name)
            item.setData(Qt.ItemDataRole.UserRole, profile.id)
            self._profile_list.addItem(item)
        active_row = next(
            (
                i
                for i, p in enumerate(self._config.profiles)
                if p.id == self._config.active_profile_id
            ),
            0,
        )
        self._profile_list.setCurrentRow(active_row)

    def _populate_lights(self, profile: Profile) -> None:
        self._light_list.clear()
        for light in profile.lights:
            item = QListWidgetItem(f"Light ({light.shape})")
            item.setData(Qt.ItemDataRole.UserRole, light.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked if light.enabled else Qt.CheckState.Unchecked)
            self._light_list.addItem(item)

    def _active_profile(self) -> Profile | None:
        row = self._profile_list.currentRow()
        if row < 0 or row >= len(self._config.profiles):
            return None
        return self._config.profiles[row]

    def _on_profile_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(self._config.profiles):
            return
        profile = self._config.profiles[row]
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=profile.id,
            profiles=self._config.profiles,
            settings=self._config.settings,
        )
        self._populate_lights(profile)
        self.profile_selected.emit(profile.id)

    def _on_light_row_changed(self, row: int) -> None:
        profile = self._active_profile()
        if profile is None or row < 0 or row >= len(profile.lights):
            return
        self.light_selected.emit(profile.lights[row].id)

    def _on_light_item_changed(self, item: QListWidgetItem) -> None:
        profile = self._active_profile()
        if profile is None:
            return
        row = self._light_list.row(item)
        if row < 0 or row >= len(profile.lights):
            return
        light = profile.lights[row]
        enabled = item.checkState() == Qt.CheckState.Checked
        if light.enabled != enabled:
            new_light = Light(
                id=light.id,
                enabled=enabled,
                monitor_name=light.monitor_name,
                monitor_index=light.monitor_index,
                shape=light.shape,
                position=light.position,
                size=light.size,
                color_mode=light.color_mode,
                color_rgb=light.color_rgb,
                color_kelvin=light.color_kelvin,
                brightness=light.brightness,
                opacity=light.opacity,
                feather=light.feather,
                shape_params=light.shape_params,
            )
            new_lights = list(profile.lights)
            new_lights[row] = new_light
            self._replace_profile(Profile(id=profile.id, name=profile.name, lights=new_lights))

    def _replace_profile(self, new_profile: Profile) -> None:
        new_profiles = [new_profile if p.id == new_profile.id else p for p in self._config.profiles]
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=self._config.active_profile_id,
            profiles=new_profiles,
            settings=self._config.settings,
        )
        self.config_changed.emit(self._config)

    def _add_profile(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Profile", "Profile name:")
        if not ok or not name.strip():
            return
        new_profile = Profile(id=str(uuid.uuid4()), name=name.strip())
        new_profiles = list(self._config.profiles) + [new_profile]
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=self._config.active_profile_id,
            profiles=new_profiles,
            settings=self._config.settings,
        )
        self._populate_profiles()
        self.config_changed.emit(self._config)

    def _remove_profile(self) -> None:
        profile = self._active_profile()
        if profile is None or len(self._config.profiles) <= 1:
            return
        new_profiles = [p for p in self._config.profiles if p.id != profile.id]
        new_active = new_profiles[0].id if new_profiles else ""
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=new_active,
            profiles=new_profiles,
            settings=self._config.settings,
        )
        self._populate_profiles()
        self.config_changed.emit(self._config)

    def _rename_profile(self) -> None:
        profile = self._active_profile()
        if profile is None:
            return
        name, ok = QInputDialog.getText(self, "Rename Profile", "New name:", text=profile.name)
        if not ok or not name.strip():
            return
        new_profile = Profile(id=profile.id, name=name.strip(), lights=profile.lights)
        self._replace_profile(new_profile)
        self._populate_profiles()

    def _add_light(self) -> None:
        profile = self._active_profile()
        if profile is None:
            return
        new_light = Light(
            id=str(uuid.uuid4()),
            enabled=False,
            monitor_name="",
            monitor_index=0,
            shape="ring",
            position=(0.5, 0.5),
            size=(800, 800),
            color_mode="kelvin",
            color_rgb=(255, 240, 220),
            color_kelvin=5600,
            brightness=0.85,
            opacity=0.95,
            feather=12,
            shape_params={"thickness": 80},
        )
        new_lights = list(profile.lights) + [new_light]
        self._replace_profile(Profile(id=profile.id, name=profile.name, lights=new_lights))
        self._populate_lights(self._active_profile())

    def _remove_light(self) -> None:
        profile = self._active_profile()
        if profile is None:
            return
        row = self._light_list.currentRow()
        if row < 0 or row >= len(profile.lights):
            return
        new_lights = [lt for i, lt in enumerate(profile.lights) if i != row]
        self._replace_profile(Profile(id=profile.id, name=profile.name, lights=new_lights))
        self._populate_lights(self._active_profile())

    def config(self) -> ConfigData:
        return self._config
