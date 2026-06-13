from __future__ import annotations

import pytest

from ringlight_overlay.core.migrations import CURRENT_VERSION, migrate


def test_migrate_current_version_is_noop() -> None:
    raw = {"version": CURRENT_VERSION, "active_profile_id": "p", "profiles": []}
    assert migrate(raw) == raw


def test_migrate_missing_version_raises() -> None:
    with pytest.raises(ValueError):
        migrate({"active_profile_id": "p", "profiles": []})


def test_migrate_future_version_raises() -> None:
    with pytest.raises(ValueError):
        migrate({"version": CURRENT_VERSION + 1})


def test_migrate_unknown_old_version_raises() -> None:
    with pytest.raises(ValueError):
        migrate({"version": 0})


def test_migrate_non_int_version_raises_value_error() -> None:
    # A corrupted/hand-edited file with a string version must raise ValueError,
    # not a TypeError from comparing str > int.
    with pytest.raises(ValueError):
        migrate({"version": "1", "active_profile_id": "p", "profiles": []})
