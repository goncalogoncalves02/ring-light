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
