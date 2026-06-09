from __future__ import annotations

import logging
import os
import sys
from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from ringlight_overlay.core.models import ConfigData, Profile
from ringlight_overlay.core.monitors import enumerate_monitors
from ringlight_overlay.core.storage import DebouncedSaver, load_config, save_config
from ringlight_overlay.hotkeys.manager import HotkeyManager
from ringlight_overlay.overlay.overlay_manager import OverlayManager
from ringlight_overlay.ui.main_window import MainWindow
from ringlight_overlay.ui.tray import TrayIcon

_log = logging.getLogger(__name__)


def _configure_logging() -> None:
    log_dir = Path(os.environ.get("APPDATA", Path.home())) / "RingLightOverlay"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# -- Pure config-manipulation helpers --------------------------------------------


def _active_profile(config: ConfigData) -> Profile | None:
    return next(
        (p for p in config.profiles if p.id == config.active_profile_id),
        config.profiles[0] if config.profiles else None,
    )


def _toggle_all_lights(config: ConfigData) -> ConfigData:
    """Return new config with every light in the active profile toggled."""
    profile = _active_profile(config)
    if profile is None:
        return config
    any_enabled = any(lt.enabled for lt in profile.lights)
    new_lights = [replace(lt, enabled=not any_enabled) for lt in profile.lights]
    new_profile = replace(profile, lights=new_lights)
    new_profiles = [new_profile if p.id == profile.id else p for p in config.profiles]
    return replace(config, profiles=new_profiles)


_BRIGHTNESS_STEP = 0.05
_BRIGHTNESS_MIN = 0.05
_BRIGHTNESS_MAX = 2.0


def _scale_profile_brightness(profile: Profile, multiplier: float) -> Profile:
    """Return profile copy with per-light brightness scaled, clamped to [0, 1]."""
    scaled = [
        replace(lt, brightness=max(0.0, min(1.0, lt.brightness * multiplier)))
        for lt in profile.lights
    ]
    return replace(profile, lights=scaled)


# -- App entry point -------------------------------------------------------------


def main() -> int:
    _configure_logging()
    _log.info("startup OK")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        _log.error("No system tray available -- cannot run")
        return 1

    config = load_config()
    monitors = enumerate_monitors()

    overlay_mgr = OverlayManager()
    tray = TrayIcon(profiles=config.profiles, active_profile_id=config.active_profile_id)
    win = MainWindow(config)
    saver = DebouncedSaver(save_config)

    brightness_multiplier: float = 1.0
    hotkey_manager = HotkeyManager(config, parent=app)

    profile = _active_profile(config)
    if profile is not None:
        overlay_mgr.apply_profile(
            _scale_profile_brightness(profile, brightness_multiplier), monitors
        )

    def _reapply(new_config: ConfigData) -> None:
        nonlocal config
        config = new_config
        p = _active_profile(config)
        tray.update_profiles(config.profiles, config.active_profile_id)
        if p is not None:
            overlay_mgr.apply_profile(
                _scale_profile_brightness(p, brightness_multiplier),
                enumerate_monitors(),
            )

    def _on_config_changed(new_config: ConfigData) -> None:
        nonlocal brightness_multiplier
        brightness_multiplier = 1.0
        _reapply(new_config)
        hotkey_manager.reload(new_config)
        _log.debug("Config changed via settings window")

    def _on_profile_selected(profile_id: str) -> None:
        nonlocal config
        config = replace(config, active_profile_id=profile_id)
        saver.request_save(config)
        _reapply(config)

    def _on_toggle_all() -> None:
        nonlocal config
        config = _toggle_all_lights(config)
        saver.request_save(config)
        _reapply(config)

    def _on_brightness_up() -> None:
        nonlocal brightness_multiplier
        brightness_multiplier = min(_BRIGHTNESS_MAX, brightness_multiplier + _BRIGHTNESS_STEP)
        _reapply(config)

    def _on_brightness_down() -> None:
        nonlocal brightness_multiplier
        brightness_multiplier = max(_BRIGHTNESS_MIN, brightness_multiplier - _BRIGHTNESS_STEP)
        _reapply(config)

    def _on_next_profile() -> None:
        nonlocal config
        if not config.profiles:
            return
        ids = [p.id for p in config.profiles]
        idx = ids.index(config.active_profile_id) if config.active_profile_id in ids else -1
        config = replace(config, active_profile_id=ids[(idx + 1) % len(ids)])
        saver.request_save(config)
        _reapply(config)

    def _on_prev_profile() -> None:
        nonlocal config
        if not config.profiles:
            return
        ids = [p.id for p in config.profiles]
        idx = ids.index(config.active_profile_id) if config.active_profile_id in ids else -1
        config = replace(config, active_profile_id=ids[(idx - 1) % len(ids)])
        saver.request_save(config)
        _reapply(config)

    def _on_show_settings() -> None:
        win.show()
        win.activateWindow()
        win.raise_()

    def _quit() -> None:
        hotkey_manager.shutdown()
        saver.flush()
        overlay_mgr.close_all()
        app.quit()

    win.config_changed.connect(_on_config_changed)
    tray.profile_selected.connect(_on_profile_selected)
    tray.show_settings_requested.connect(_on_show_settings)
    tray.toggle_all_requested.connect(_on_toggle_all)
    tray.quit_requested.connect(_quit)
    tray.brightness_up_requested.connect(_on_brightness_up)
    tray.brightness_down_requested.connect(_on_brightness_down)
    tray.next_profile_requested.connect(_on_next_profile)
    tray.prev_profile_requested.connect(_on_prev_profile)

    hotkey_manager.toggle_all_requested.connect(_on_toggle_all, Qt.ConnectionType.QueuedConnection)
    hotkey_manager.brightness_up_requested.connect(
        _on_brightness_up, Qt.ConnectionType.QueuedConnection
    )
    hotkey_manager.brightness_down_requested.connect(
        _on_brightness_down, Qt.ConnectionType.QueuedConnection
    )
    hotkey_manager.next_profile_requested.connect(
        _on_next_profile, Qt.ConnectionType.QueuedConnection
    )
    hotkey_manager.prev_profile_requested.connect(
        _on_prev_profile, Qt.ConnectionType.QueuedConnection
    )
    hotkey_manager.show_settings_requested.connect(
        _on_show_settings, Qt.ConnectionType.QueuedConnection
    )

    tray.show()
    _log.info("Tray icon ready -- entering event loop")

    return app.exec()
