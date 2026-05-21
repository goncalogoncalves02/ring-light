from __future__ import annotations

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSplitter, QVBoxLayout, QWidget

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.core.storage import DebouncedSaver, save_config
from ringlight_overlay.ui.widgets.light_editor import LightEditor
from ringlight_overlay.ui.widgets.profile_list import ProfileList

_log = logging.getLogger(__name__)


class MainWindow(QWidget):
    """Settings window: profile + light sidebar on left, editor on right."""

    config_changed = Signal(object)

    def __init__(self, config: ConfigData, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._config = config
        self._saver = DebouncedSaver(save_config)
        self._build_ui()
        self.setWindowTitle("RingLight Overlay — Settings")
        self.setMinimumSize(800, 500)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._profile_list = ProfileList(self._config)
        splitter.addWidget(self._profile_list)
        splitter.setStretchFactor(0, 1)

        self._light_editor = LightEditor()
        splitter.addWidget(self._light_editor)
        splitter.setStretchFactor(1, 3)

        root.addWidget(splitter)

        self._profile_list.light_selected.connect(self._on_light_selected)
        self._profile_list.config_changed.connect(self._on_config_changed)
        self._light_editor.light_changed.connect(self._on_light_changed)

    def config(self) -> ConfigData:
        return self._config

    def closeEvent(self, event) -> None:  # type: ignore[override]
        event.ignore()
        self.hide()

    def _on_light_selected(self, light_id: str) -> None:
        light = self._find_light(light_id)
        if light is not None:
            self._light_editor.load_light(light)
        else:
            self._light_editor.clear()

    def _on_config_changed(self, config: ConfigData) -> None:
        self._config = config
        self._saver.request_save(config)
        self.config_changed.emit(config)
        _log.debug("Config updated via profile list")

    def _on_light_changed(self, light: Light) -> None:
        new_profiles = []
        for profile in self._config.profiles:
            new_lights = [light if l.id == light.id else l for l in profile.lights]
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

    def _find_light(self, light_id: str) -> Light | None:
        for profile in self._config.profiles:
            for light in profile.lights:
                if light.id == light_id:
                    return light
        return None
