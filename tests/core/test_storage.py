from __future__ import annotations

from pathlib import Path

import pytest

from ringlight_overlay.core.models import ConfigData
from ringlight_overlay.core.storage import (
    DebouncedSaver,
    config_path,
    default_config,
    load_config,
    save_config,
)


def test_default_config_has_one_disabled_daylight_ring() -> None:
    config = default_config()
    assert config.version == 1
    assert len(config.profiles) == 1
    profile = config.profiles[0]
    assert profile.name == "Daylight"
    assert config.active_profile_id == profile.id
    assert len(profile.lights) == 1
    light = profile.lights[0]
    assert light.enabled is False
    assert light.shape == "ring"
    assert light.monitor_index == 0
    assert light.color_kelvin == 5600
    assert light.shape_params == {"thickness": 80}


def test_config_path_uses_appdata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPDATA", str(tmp_path))
    expected = tmp_path / "RingLightOverlay" / "config.json"
    assert config_path() == expected


def test_save_and_load_roundtrip_equals_original(tmp_path: Path) -> None:
    target = tmp_path / "config.json"
    original = default_config()
    save_config(original, path=target)
    loaded = load_config(path=target)
    assert loaded == original


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    missing = tmp_path / "does-not-exist.json"
    config = load_config(path=missing)
    assert isinstance(config, ConfigData)
    assert config.version == 1


def test_debounced_saver_fires_after_delay() -> None:
    import time

    calls: list[ConfigData] = []
    saver = DebouncedSaver(calls.append, delay=0.05)
    saver.request_save(default_config())
    time.sleep(0.2)
    assert len(calls) == 1


def test_debounced_saver_coalesces_rapid_requests() -> None:
    import time

    calls: list[ConfigData] = []
    saver = DebouncedSaver(calls.append, delay=0.1)
    for _ in range(5):
        saver.request_save(default_config())
        time.sleep(0.02)
    time.sleep(0.3)
    assert len(calls) == 1


def test_debounced_saver_flush_writes_immediately_and_clears_pending() -> None:
    import time

    calls: list[ConfigData] = []
    saver = DebouncedSaver(calls.append, delay=10.0)
    saver.request_save(default_config())
    saver.flush()
    assert len(calls) == 1
    time.sleep(0.1)
    assert len(calls) == 1


def test_debounced_saver_flush_without_pending_is_noop() -> None:
    calls: list[ConfigData] = []
    saver = DebouncedSaver(calls.append, delay=0.05)
    saver.flush()
    assert calls == []
