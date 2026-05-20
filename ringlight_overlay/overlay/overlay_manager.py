from __future__ import annotations

import logging

from ringlight_overlay.core.models import Light, Profile
from ringlight_overlay.core.monitors import MonitorInfo, match_monitor
from ringlight_overlay.overlay.overlay_window import OverlayWindow

_log = logging.getLogger(__name__)


class OverlayManager:
    """Manages OverlayWindow instances — one per Light in the active profile."""

    def __init__(self) -> None:
        self._windows: dict[str, OverlayWindow] = {}

    @property
    def window_count(self) -> int:
        return len(self._windows)

    def get_window(self, light_id: str) -> OverlayWindow | None:
        return self._windows.get(light_id)

    def apply_profile(self, profile: Profile, monitors: list[MonitorInfo]) -> None:
        """Reconcile windows to match *profile* on the given *monitors*."""
        current_ids = set(self._windows.keys())
        new_ids = {light.id for light in profile.lights}

        for lid in current_ids - new_ids:
            win = self._windows.pop(lid)
            win.close()
            _log.debug("Closed overlay window for removed light %s", lid)

        for light in profile.lights:
            if light.id not in self._windows:
                win = OverlayWindow(light)
                self._windows[light.id] = win
                _log.debug("Created overlay window for light %s", light.id)
            else:
                self._windows[light.id].update_light(light)

            win = self._windows[light.id]
            self._position_window(win, light, monitors)

            if light.enabled:
                win.show()
            else:
                win.hide()

    def _position_window(
        self,
        win: OverlayWindow,
        light: Light,
        monitors: list[MonitorInfo],
    ) -> None:
        if not monitors:
            _log.warning("No monitors available — skipping position for light %s", light.id)
            return
        monitor, level = match_monitor(light.monitor_name, light.monitor_index, monitors)
        if level > 0:
            _log.warning(
                "Monitor fallback level %d for light %s (name=%r, index=%d)",
                level,
                light.id,
                light.monitor_name,
                light.monitor_index,
            )
        geo = monitor.geometry
        x = geo[0] + int(light.position[0] * geo[2]) - light.size[0] // 2
        y = geo[1] + int(light.position[1] * geo[3]) - light.size[1] // 2
        win.setGeometry(x, y, light.size[0], light.size[1])

    def close_all(self) -> None:
        for win in self._windows.values():
            win.close()
        self._windows.clear()
        _log.debug("All overlay windows closed")
