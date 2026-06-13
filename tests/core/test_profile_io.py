from __future__ import annotations

import json

import pytest

from ringlight_overlay.core.migrations import CURRENT_VERSION
from ringlight_overlay.core.models import Light, Profile
from ringlight_overlay.core.profile_io import export_profile, import_profile
from ringlight_overlay.core.storage import default_config


def _make_profile() -> Profile:
    config = default_config()
    return config.profiles[0]


class TestExportProfile:
    def test_returns_version_and_profile_keys(self):
        p = _make_profile()
        result = export_profile(p)
        assert "version" in result
        assert "profile" in result

    def test_version_matches_current(self):
        p = _make_profile()
        result = export_profile(p)
        assert result["version"] == CURRENT_VERSION

    def test_json_serializable(self):
        p = _make_profile()
        result = export_profile(p)
        # Should not raise
        serialized = json.dumps(result)
        assert len(serialized) > 0

    def test_profile_name_preserved(self):
        p = _make_profile()
        result = export_profile(p)
        assert result["profile"]["name"] == p.name

    def test_lights_serialized(self):
        p = _make_profile()
        result = export_profile(p)
        assert isinstance(result["profile"]["lights"], list)
        assert len(result["profile"]["lights"]) == len(p.lights)


class TestImportProfile:
    def test_roundtrip_content_preserved(self):
        p = _make_profile()
        envelope = export_profile(p)
        imported = import_profile(envelope)
        assert imported.name == p.name
        assert len(imported.lights) == len(p.lights)

    def test_profile_id_regenerated(self):
        p = _make_profile()
        envelope = export_profile(p)
        imported = import_profile(envelope)
        assert imported.id != p.id

    def test_light_ids_regenerated(self):
        p = _make_profile()
        original_light_ids = {lt.id for lt in p.lights}
        envelope = export_profile(p)
        imported = import_profile(envelope)
        imported_light_ids = {lt.id for lt in imported.lights}
        assert imported_light_ids.isdisjoint(original_light_ids)

    def test_two_imports_get_different_ids(self):
        p = _make_profile()
        envelope = export_profile(p)
        imported1 = import_profile(envelope)
        imported2 = import_profile(envelope)
        assert imported1.id != imported2.id

    def test_raises_on_missing_version(self):
        p = _make_profile()
        envelope = export_profile(p)
        del envelope["version"]
        with pytest.raises(ValueError, match="version"):
            import_profile(envelope)

    def test_raises_on_newer_version(self):
        p = _make_profile()
        envelope = export_profile(p)
        envelope["version"] = CURRENT_VERSION + 99
        with pytest.raises(ValueError):
            import_profile(envelope)

    def test_raises_on_missing_profile_key(self):
        with pytest.raises(ValueError, match="profile"):
            import_profile({"version": CURRENT_VERSION})

    def test_raises_on_malformed_profile(self):
        with pytest.raises(ValueError):
            import_profile({"version": CURRENT_VERSION, "profile": {"name": "X"}})

    def test_raises_on_non_dict_input(self):
        with pytest.raises(ValueError):
            import_profile("not a dict")  # type: ignore[arg-type]

    def test_raises_value_error_on_non_int_version(self):
        p = _make_profile()
        envelope = export_profile(p)
        envelope["version"] = "1"  # corrupted file: string instead of int
        with pytest.raises(ValueError):
            import_profile(envelope)

    def test_light_data_preserved(self):
        p = _make_profile()
        envelope = export_profile(p)
        imported = import_profile(envelope)
        orig_light = p.lights[0]
        imp_light = imported.lights[0]
        assert imp_light.shape == orig_light.shape
        assert imp_light.brightness == orig_light.brightness
        assert imp_light.color_rgb == orig_light.color_rgb
