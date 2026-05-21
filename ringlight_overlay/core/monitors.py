from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class MonitorInfo:
    """Snapshot of a connected display at enumeration time."""

    index: int
    name: str
    geometry: tuple[int, int, int, int]
    primary: bool


def enumerate_monitors() -> list[MonitorInfo]:
    """Enumerate connected screens via the active QGuiApplication.

    Requires a QGuiApplication (or QApplication) to be alive. Raises
    RuntimeError otherwise so callers fail loud rather than silently
    returning an empty list.
    """
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance()
    if app is None:
        raise RuntimeError("QGuiApplication must exist before calling enumerate_monitors().")

    primary = app.primaryScreen()
    monitors: list[MonitorInfo] = []
    for i, screen in enumerate(app.screens()):
        geo = screen.geometry()
        monitors.append(
            MonitorInfo(
                index=i,
                name=screen.name(),
                geometry=(geo.x(), geo.y(), geo.width(), geo.height()),
                primary=(screen is primary),
            )
        )
    return monitors


def match_monitor(name: str, index: int, monitors: list[MonitorInfo]) -> tuple[MonitorInfo, int]:
    """Resolve a stored (name, index) reference to a current MonitorInfo.

    Returns ``(monitor, fallback_level)`` where ``fallback_level`` is:
      * 0 — matched by name
      * 1 — name missed, matched by index
      * 2 — both missed, returned primary (or first monitor if no primary)
    Callers should log a warning when the level is 1 or 2.
    """
    if not monitors:
        raise RuntimeError("No monitors available.")

    for monitor in monitors:
        if monitor.name == name:
            return monitor, 0

    if 0 <= index < len(monitors):
        return monitors[index], 1

    for monitor in monitors:
        if monitor.primary:
            return monitor, 2

    return monitors[0], 2
