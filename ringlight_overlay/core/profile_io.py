from __future__ import annotations

import uuid
from dataclasses import asdict

from ringlight_overlay.core.migrations import CURRENT_VERSION, migrate
from ringlight_overlay.core.models import Light, Profile
from ringlight_overlay.core.storage import _profile_from_dict


def export_profile(profile: Profile) -> dict:
    """Serialize a Profile to an export envelope dict.

    The envelope contains ``version`` and ``profile`` keys.
    The result is always JSON-serializable.
    """
    return {
        "version": CURRENT_VERSION,
        "profile": {
            "id": profile.id,
            "name": profile.name,
            "lights": [asdict(light) for light in profile.lights],
        },
    }


def import_profile(raw: dict) -> Profile:
    """Parse an export envelope and return a Profile with regenerated IDs.

    The imported profile receives a fresh ``id`` and each ``Light`` gets a
    fresh ``id`` so collisions with existing profiles are impossible.

    Raises ``ValueError`` if the envelope is malformed, missing ``version``,
    or contains a version newer than ``CURRENT_VERSION``.
    """
    if not isinstance(raw, dict):
        raise ValueError("Import data must be a JSON object.")

    # Reuse migrate() to validate version field and apply any upgrades.
    # We need a config-shaped envelope for migrate() — wrap the profile in a
    # minimal valid envelope that migrate() will accept.
    version = raw.get("version")
    if version is None:
        raise ValueError("Export envelope is missing required 'version' field.")

    # Validate version via migrate() by constructing a minimal config envelope
    try:
        migrate({"version": version, "active_profile_id": "", "profiles": [], "settings": {}})
    except ValueError:
        raise

    profile_raw = raw.get("profile")
    if not isinstance(profile_raw, dict):
        raise ValueError("Export envelope is missing or malformed 'profile' field.")

    # Parse with existing storage helper (validates field presence)
    try:
        profile = _profile_from_dict(profile_raw)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Malformed profile data: {exc}") from exc

    # Regenerate all IDs to avoid collisions
    new_lights = [
        Light(
            id=str(uuid.uuid4()),
            enabled=light.enabled,
            monitor_name=light.monitor_name,
            monitor_index=light.monitor_index,
            shape=light.shape,
            position=light.position,
            size=light.size,
            color_mode=light.color_mode,
            color_rgb=light.color_rgb,
            color_kelvin=light.color_kelvin,
            brightness=light.brightness,
            opacity=light.opacity,
            feather=light.feather,
            shape_params=light.shape_params,
        )
        for light in profile.lights
    ]
    return Profile(id=str(uuid.uuid4()), name=profile.name, lights=new_lights)
