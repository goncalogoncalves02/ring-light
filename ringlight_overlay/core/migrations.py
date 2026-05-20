from __future__ import annotations

from typing import Callable

CURRENT_VERSION = 1

# Registry maps FROM-version → callable that returns the payload at version+1.
MIGRATIONS: dict[int, Callable[[dict], dict]] = {}


def migrate(raw: dict) -> dict:
    """Apply migrations in sequence until ``raw['version'] == CURRENT_VERSION``.

    Raises ValueError if:
      * the payload has no ``version`` field,
      * the payload reports a version newer than CURRENT_VERSION,
      * a required migration is not registered.
    """
    version = raw.get("version")
    if version is None:
        raise ValueError("Config payload is missing required 'version' field.")
    if version > CURRENT_VERSION:
        raise ValueError(
            f"Config version {version} is newer than current "
            f"{CURRENT_VERSION}; downgrade is not supported."
        )
    while version < CURRENT_VERSION:
        migration = MIGRATIONS.get(version)
        if migration is None:
            raise ValueError(
                f"No migration registered from version {version} to {version + 1}."
            )
        raw = migration(raw)
        version = raw.get("version")
    return raw
