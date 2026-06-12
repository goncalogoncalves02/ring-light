from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from ringlight_overlay.core.migrations import migrate
from ringlight_overlay.core.models import ConfigData, Light, Profile

CONFIG_VERSION = 1


def config_path() -> Path:
    """Return the config.json path under %APPDATA%\\RingLightOverlay.

    Read at call time so tests can override APPDATA via monkeypatch.
    """
    base = os.environ.get("APPDATA")
    if not base:
        raise RuntimeError("APPDATA environment variable is required on Windows.")
    return Path(base) / "RingLightOverlay" / "config.json"


def is_first_run(path: Path | None = None) -> bool:
    """Return True when no config file exists (i.e. the app has never saved state)."""
    return not (path or config_path()).exists()


def default_config() -> ConfigData:
    """First-run config: one Daylight profile with one disabled ring."""
    light = Light(
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
    profile = Profile(id=str(uuid.uuid4()), name="Daylight", lights=[light])
    return ConfigData(
        version=CONFIG_VERSION,
        active_profile_id=profile.id,
        profiles=[profile],
        settings={
            "start_with_windows": False,
            "minimize_to_tray_on_close": True,
            "hotkeys": {
                "toggle_all": "ctrl+alt+l",
                "brightness_up": "ctrl+alt+up",
                "brightness_down": "ctrl+alt+down",
                "next_profile": "ctrl+alt+right",
                "prev_profile": "ctrl+alt+left",
                "show_settings": "ctrl+alt+s",
            },
        },
    )


def _light_from_dict(raw: dict) -> Light:
    return Light(
        id=raw["id"],
        enabled=raw["enabled"],
        monitor_name=raw["monitor_name"],
        monitor_index=raw["monitor_index"],
        shape=raw["shape"],
        position=(float(raw["position"][0]), float(raw["position"][1])),
        size=(int(raw["size"][0]), int(raw["size"][1])),
        color_mode=raw["color_mode"],
        color_rgb=(
            int(raw["color_rgb"][0]),
            int(raw["color_rgb"][1]),
            int(raw["color_rgb"][2]),
        ),
        color_kelvin=raw["color_kelvin"],
        brightness=raw["brightness"],
        opacity=raw["opacity"],
        feather=raw["feather"],
        shape_params=dict(raw["shape_params"]),
    )


def _profile_from_dict(raw: dict) -> Profile:
    return Profile(
        id=raw["id"],
        name=raw["name"],
        lights=[_light_from_dict(light) for light in raw["lights"]],
    )


def _config_from_raw(raw: dict) -> ConfigData:
    raw = migrate(raw)
    return ConfigData(
        version=raw["version"],
        active_profile_id=raw["active_profile_id"],
        profiles=[_profile_from_dict(p) for p in raw["profiles"]],
        settings=dict(raw["settings"]),
    )


def load_config(path: Path | None = None) -> ConfigData:
    """Load config from disk; return ``default_config()`` if missing."""
    target = path or config_path()
    if not target.exists():
        return default_config()
    raw = json.loads(target.read_text(encoding="utf-8"))
    return _config_from_raw(raw)


def save_config(data: ConfigData, path: Path | None = None) -> None:
    """Write config atomically (write to .tmp, then ``os.replace``)."""
    target = path or config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    payload = {
        "version": data.version,
        "active_profile_id": data.active_profile_id,
        "profiles": [
            {
                "id": profile.id,
                "name": profile.name,
                "lights": [asdict(light) for light in profile.lights],
            }
            for profile in data.profiles
        ],
        "settings": data.settings,
    }
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp, target)


class DebouncedSaver:
    """Coalesce rapid save requests into a single delayed write.

    Backed by ``threading.Timer`` so it remains usable without the Qt event
    loop and is trivially unit-testable. Callers MUST call ``flush()`` on
    application shutdown to guarantee any pending data is written.
    """

    def __init__(
        self,
        save_fn: Callable[[ConfigData], None],
        delay: float = 0.5,
    ) -> None:
        self._save_fn = save_fn
        self._delay = delay
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None
        self._pending: ConfigData | None = None

    def request_save(self, data: ConfigData) -> None:
        with self._lock:
            self._pending = data
            if self._timer is not None:
                self._timer.cancel()
            timer = threading.Timer(self._delay, self._fire)
            timer.daemon = True
            self._timer = timer
        timer.start()

    def flush(self) -> None:
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            data = self._pending
            self._pending = None
        if data is not None:
            self._save_fn(data)

    def _fire(self) -> None:
        with self._lock:
            self._timer = None
            data = self._pending
            self._pending = None
        if data is not None:
            self._save_fn(data)
