from __future__ import annotations

import pytest

from ringlight_overlay.core.monitors import MonitorInfo, match_monitor


def _make_monitors() -> list[MonitorInfo]:
    return [
        MonitorInfo(
            index=0,
            name="\\\\.\\DISPLAY1",
            geometry=(0, 0, 1920, 1080),
            primary=True,
        ),
        MonitorInfo(
            index=1,
            name="\\\\.\\DISPLAY2",
            geometry=(1920, 0, 1920, 1080),
            primary=False,
        ),
    ]


def test_match_by_name_returns_level_zero() -> None:
    monitors = _make_monitors()
    monitor, level = match_monitor("\\\\.\\DISPLAY2", 0, monitors)
    assert monitor.index == 1
    assert level == 0


def test_match_falls_back_to_index_when_name_missing() -> None:
    monitors = _make_monitors()
    monitor, level = match_monitor("\\\\.\\DISPLAY99", 1, monitors)
    assert monitor.index == 1
    assert level == 1


def test_match_falls_back_to_primary_when_name_and_index_miss() -> None:
    monitors = _make_monitors()
    monitor, level = match_monitor("\\\\.\\DISPLAY99", 9, monitors)
    assert monitor.primary is True
    assert level == 2


def test_match_raises_when_no_monitors() -> None:
    with pytest.raises(RuntimeError):
        match_monitor("anything", 0, [])


def test_enumerate_monitors_returns_at_least_one(qapp) -> None:
    from ringlight_overlay.core.monitors import enumerate_monitors

    monitors = enumerate_monitors()
    assert len(monitors) >= 1
    assert all(isinstance(m, MonitorInfo) for m in monitors)


def test_qscreen_by_name_finds_live_screen(qapp) -> None:
    from PySide6.QtGui import QGuiApplication

    from ringlight_overlay.core.monitors import qscreen_by_name

    screen = QGuiApplication.screens()[0]
    assert qscreen_by_name(screen.name()) is screen


def test_qscreen_by_name_returns_none_for_unknown(qapp) -> None:
    from ringlight_overlay.core.monitors import qscreen_by_name

    assert qscreen_by_name("\\\\.\\NOPE99") is None


def test_qscreen_for_matches_by_name(qapp) -> None:
    from PySide6.QtGui import QGuiApplication

    from ringlight_overlay.core.monitors import MonitorInfo, qscreen_for

    screen = QGuiApplication.screens()[0]
    monitor = MonitorInfo(index=5, name=screen.name(), geometry=(0, 0, 100, 100), primary=True)
    # name wins even though index 5 is out of range
    assert qscreen_for(monitor) is screen


def test_qscreen_for_falls_back_to_index(qapp) -> None:
    from PySide6.QtGui import QGuiApplication

    from ringlight_overlay.core.monitors import MonitorInfo, qscreen_for

    monitor = MonitorInfo(index=0, name="\\\\.\\NOPE99", geometry=(0, 0, 100, 100), primary=True)
    assert qscreen_for(monitor) is QGuiApplication.screens()[0]


def test_qscreen_for_returns_none_when_unresolvable(qapp) -> None:
    from ringlight_overlay.core.monitors import MonitorInfo, qscreen_for

    monitor = MonitorInfo(index=99, name="\\\\.\\NOPE99", geometry=(0, 0, 100, 100), primary=False)
    assert qscreen_for(monitor) is None
