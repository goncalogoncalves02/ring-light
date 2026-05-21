from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.core.monitors import enumerate_monitors
from ringlight_overlay.core.storage import DebouncedSaver, load_config, save_config
from ringlight_overlay.overlay.overlay_manager import OverlayManager
from ringlight_overlay.ui.main_window import MainWindow
from ringlight_overlay.ui.tray import TrayIcon

_log = logging.getLogger(__name__)


def _configure_logging() -> None:
    import os
    from pathlib import Path

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


# ── Pure config-manipulation helpers ────────────────────────────────────────────


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
    new_lights = [
        Light(
            id=lt.id,
            enabled=not any_enabled,
            monitor_name=lt.monitor_name,
            monitor_index=lt.monitor_index,
            shape=lt.shape,
            position=lt.position,
            size=lt.size,
            color_mode=lt.color_mode,
            color_rgb=lt.color_rgb,
            color_kelvin=lt.color_kelvin,
            brightness=lt.brightness,
            opacity=lt.opacity,
            feather=lt.feather,
            shape_params=lt.shape_params,
        )
        for lt in profile.lights
    ]
    new_profile = Profile(id=profile.id, name=profile.name, lights=new_lights)
    new_profiles = [new_profile if p.id == profile.id else p for p in config.profiles]
    return ConfigData(
        version=config.version,
        active_profile_id=config.active_profile_id,
        profiles=new_profiles,
        settings=config.settings,
    )


# ── App entry point ────────────────────────────────────────────────────────────────────────────


def main() -> int:
    _configure_logging()
    _log.info("startup OK")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        _log.error("No system tray available — cannot run")
        return 1

    config = load_config()
    monitors = enumerate_monitors()

    overlay_mgr = OverlayManager()
    profile = _active_profile(config)
    if profile is not None:
        overlay_mgr.apply_profile(profile, monitors)

    tray = TrayIcon(profiles=config.profiles, active_profile_id=config.active_profile_id)
    win = MainWindow(config)
    saver = DebouncedSaver(save_config)

    def _reapply(new_config: ConfigData) -> None:
        nonlocal config
        config = new_config
        p = _active_profile(config)
        tray.update_profiles(config.profiles, config.active_profile_id)
        if p is not None:
            overlay_mgr.apply_profile(p, enumerate_monitors())

    def _on_config_changed(new_config: ConfigData) -> None:
        _reapply(new_config)
        _log.debug("Config changed via settings window")

    def _on_profile_selected(profile_id: str) -> None:
        nonlocal config
        config = ConfigData(
            version=config.version,
            active_profile_id=profile_id,
            profiles=config.profiles,
            settings=config.settings,
        )
        saver.request_save(config)
        _reapply(config)

    def _on_toggle_all() -> None:
        nonlocal config
        config = _toggle_all_lights(config)
        saver.request_save(config)
        _reapply(config)

    def _quit() -> None:
        saver.flush()
        overlay_mgr.close_all()
        app.quit()

    win.config_changed.connect(_on_config_changed)
    tray.profile_selected.connect(_on_profile_selected)
    tray.show_settings_requested.connect(win.show)
    tray.toggle_all_requested.connect(_on_toggle_all)
    tray.quit_requested.connect(_quit)

    tray.show()
    _log.info("Tray icon ready — entering event loop")

    return app.exec()
