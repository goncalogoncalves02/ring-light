from __future__ import annotations

import json
import logging
from dataclasses import replace
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt, Signal

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.core.monitors import enumerate_monitors
from ringlight_overlay.core.profile_io import export_profile, import_profile
from ringlight_overlay.core.storage import DebouncedSaver, save_config
from ringlight_overlay.ui.widgets.hotkey_editor import HotkeyEditor
from ringlight_overlay.ui.widgets.light_editor import LightEditor
from ringlight_overlay.ui.widgets.profile_list import ProfileList

_log = logging.getLogger(__name__)


class MainWindow(QWidget):
    """Settings window: profile + light sidebar on left, editor on right."""

    config_changed = Signal(object)
    quit_requested = Signal()
    about_requested = Signal()

    def __init__(
        self,
        config: ConfigData,
        saver: DebouncedSaver | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._config = config
        self._saver = saver if saver is not None else DebouncedSaver(save_config)
        self._build_ui()
        self.setWindowTitle("RingLight Overlay — Settings")
        self.setMinimumSize(800, 500)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)

        tabs = QTabWidget()

        # --- Lights tab ---
        lights_widget = QWidget()
        lights_layout = QVBoxLayout(lights_widget)
        lights_layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._profile_list = ProfileList(self._config)
        splitter.addWidget(self._profile_list)
        splitter.setStretchFactor(0, 1)

        self._light_editor = LightEditor()
        splitter.addWidget(self._light_editor)
        splitter.setStretchFactor(1, 3)
        lights_layout.addWidget(splitter)

        tabs.addTab(lights_widget, "Lights")

        # --- Hotkeys tab ---
        self._hotkey_editor = HotkeyEditor(self._config)
        tabs.addTab(self._hotkey_editor, "Hotkeys")

        root.addWidget(tabs)

        # --- Bottom row ---
        bottom = QHBoxLayout()

        checked = self._config.settings.get("minimize_to_tray_on_close", True)
        self._minimize_checkbox = QCheckBox("Minimize to tray on close")
        self._minimize_checkbox.setChecked(bool(checked))
        bottom.addWidget(self._minimize_checkbox)

        bottom.addStretch()

        import_btn = QPushButton("Import Profile…")
        import_btn.clicked.connect(self._on_import_profile)
        bottom.addWidget(import_btn)

        export_btn = QPushButton("Export Profile…")
        export_btn.clicked.connect(self._on_export_profile)
        bottom.addWidget(export_btn)

        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.about_requested)
        bottom.addWidget(about_btn)

        root.addLayout(bottom)

        self._profile_list.light_selected.connect(self._on_light_selected)
        self._profile_list.profile_selected.connect(self._on_profile_selected)
        self._profile_list.config_changed.connect(self._on_config_changed)
        self._light_editor.light_changed.connect(self._on_light_changed)
        self._minimize_checkbox.toggled.connect(self._on_minimize_toggled)
        self._hotkey_editor.hotkeys_changed.connect(self._on_hotkeys_changed)

        self._refresh_monitors()

    def _refresh_monitors(self) -> None:
        """Populate the light editor's monitor dropdown from the live screens.

        Called at build time and on every show so a monitor connected or
        disconnected while the window was hidden is reflected. Re-loads the
        current light afterwards so its monitor stays selected (``load_light``
        suppresses signals, so this never triggers a spurious save).
        """
        self._light_editor.load_monitors(enumerate_monitors())
        light_id = self._light_editor.current_light_id()
        if light_id is not None:
            light = self._find_light(light_id)
            if light is not None:
                self._light_editor.load_light(light)

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._refresh_monitors()
        super().showEvent(event)

    def config(self) -> ConfigData:
        return self._config

    def apply_external_config(self, config: ConfigData) -> None:
        """Reflect a config changed outside the window (tray/hotkey) in the UI.

        Updates the held config and child widgets without emitting
        ``config_changed`` or saving — the external source already did both.
        Keeps ``_on_light_changed`` merges (which preserve ``enabled``) anchored
        on the live state regardless of where a toggle came from.
        """
        self._config = config

        checked = bool(config.settings.get("minimize_to_tray_on_close", True))
        self._minimize_checkbox.blockSignals(True)
        self._minimize_checkbox.setChecked(checked)
        self._minimize_checkbox.blockSignals(False)

        self._profile_list.apply_external_config(config)

        light_id = self._light_editor.current_light_id()
        if light_id is not None:
            light = self._find_light(light_id)
            if light is not None:
                self._light_editor.load_light(light)
            else:
                self._light_editor.clear()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        event.ignore()
        if self._config.settings.get("minimize_to_tray_on_close", True):
            self.hide()
        else:
            self.quit_requested.emit()

    def _on_light_selected(self, light_id: str) -> None:
        light = self._find_light(light_id)
        if light is not None:
            self._light_editor.load_light(light)
        else:
            self._light_editor.clear()

    def _on_profile_selected(self, profile_id: str) -> None:
        if profile_id == self._config.active_profile_id:
            return
        self._config = replace(self._config, active_profile_id=profile_id)
        self._saver.request_save(self._config)
        self.config_changed.emit(self._config)
        _log.debug("Active profile changed via profile list — %s", profile_id)

    def _on_config_changed(self, config: ConfigData) -> None:
        self._config = config
        self._saver.request_save(config)
        self.config_changed.emit(config)
        _log.debug("Config updated via profile list")

    def _on_light_changed(self, light: Light) -> None:
        new_profiles = []
        for profile in self._config.profiles:
            new_lights = []
            for current in profile.lights:
                if current.id == light.id:
                    # `enabled` is owned by the profile-list checkbox, not the editor
                    # (it has no editor widget). Preserve the live value so editing a
                    # property never toggles the overlay off.
                    new_lights.append(replace(light, enabled=current.enabled))
                else:
                    new_lights.append(current)
            new_profiles.append(Profile(id=profile.id, name=profile.name, lights=new_lights))
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=self._config.active_profile_id,
            profiles=new_profiles,
            settings=self._config.settings,
        )
        self._saver.request_save(self._config)
        self.config_changed.emit(self._config)
        _log.debug("Config updated via light editor — light %s", light.id)

    def _on_minimize_toggled(self, checked: bool) -> None:
        new_settings = {**self._config.settings, "minimize_to_tray_on_close": checked}
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=self._config.active_profile_id,
            profiles=self._config.profiles,
            settings=new_settings,
        )
        self._saver.request_save(self._config)
        self.config_changed.emit(self._config)
        _log.debug("minimize_to_tray_on_close toggled to %s", checked)

    def _on_hotkeys_changed(self, hotkeys: dict) -> None:
        new_settings = {**self._config.settings, "hotkeys": hotkeys}
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=self._config.active_profile_id,
            profiles=self._config.profiles,
            settings=new_settings,
        )
        self._saver.request_save(self._config)
        self.config_changed.emit(self._config)
        _log.debug("Hotkeys updated via hotkey editor")

    def _on_export_profile(self) -> None:
        active = self._find_active_profile()
        if active is None:
            QMessageBox.warning(self, "Export Profile", "No active profile to export.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Profile",
            f"{active.name}.json",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            data = export_profile(active)
            Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
            _log.info("Exported profile %r to %s", active.name, path)
        except Exception as exc:
            QMessageBox.critical(self, "Export Failed", f"Could not export profile:\n{exc}")
            _log.error("Profile export failed: %s", exc)

    def _on_import_profile(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Profile",
            "",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            raw = json.loads(Path(path).read_text(encoding="utf-8"))
            profile = import_profile(raw)
        except (ValueError, json.JSONDecodeError, OSError) as exc:
            QMessageBox.critical(self, "Import Failed", f"Could not import profile:\n{exc}")
            _log.error("Profile import failed: %s", exc)
            return

        new_profiles = list(self._config.profiles) + [profile]
        self._config = ConfigData(
            version=self._config.version,
            active_profile_id=self._config.active_profile_id,
            profiles=new_profiles,
            settings=self._config.settings,
        )
        self._profile_list.apply_external_config(self._config)
        self._saver.request_save(self._config)
        self.config_changed.emit(self._config)
        _log.info("Imported profile %r (id=%s)", profile.name, profile.id)

    def _find_active_profile(self) -> Profile | None:
        for profile in self._config.profiles:
            if profile.id == self._config.active_profile_id:
                return profile
        return self._config.profiles[0] if self._config.profiles else None

    def _find_light(self, light_id: str) -> Light | None:
        for profile in self._config.profiles:
            for light in profile.lights:
                if light.id == light_id:
                    return light
        return None
