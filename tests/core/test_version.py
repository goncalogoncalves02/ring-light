from __future__ import annotations

import tomllib
from pathlib import Path


def test_versions_in_sync():
    """__init__.py and pyproject.toml must report the same version."""
    import ringlight_overlay

    toml_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with toml_path.open("rb") as f:
        data = tomllib.load(f)

    toml_version = data["project"]["version"]
    assert ringlight_overlay.__version__ == toml_version, (
        f"ringlight_overlay.__version__ ({ringlight_overlay.__version__!r}) "
        f"does not match pyproject.toml version ({toml_version!r})"
    )
