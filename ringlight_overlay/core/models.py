from __future__ import annotations

from dataclasses import dataclass, field

VALID_SHAPES = frozenset({"ring", "circle", "rectangle"})
VALID_COLOR_MODES = frozenset({"rgb", "kelvin"})


def _check_range(name: str, value: float, low: float, high: float) -> None:
    if not (low <= value <= high):
        raise ValueError(f"{name} must be in [{low}, {high}], got {value!r}")


def _check_rgb_component(name: str, value: int) -> None:
    if not isinstance(value, int) or not (0 <= value <= 255):
        raise ValueError(f"{name} must be int in [0, 255], got {value!r}")


@dataclass(slots=True)
class Light:
    id: str
    enabled: bool
    monitor_name: str
    monitor_index: int
    shape: str
    position: tuple[float, float]
    size: tuple[int, int]
    color_mode: str
    color_rgb: tuple[int, int, int]
    color_kelvin: int
    brightness: float
    opacity: float
    feather: int
    shape_params: dict

    def __post_init__(self) -> None:
        if self.shape not in VALID_SHAPES:
            raise ValueError(
                f"shape must be one of {sorted(VALID_SHAPES)}, got {self.shape!r}"
            )
        if self.color_mode not in VALID_COLOR_MODES:
            raise ValueError(
                f"color_mode must be one of {sorted(VALID_COLOR_MODES)}, "
                f"got {self.color_mode!r}"
            )
        _check_range("position[0]", self.position[0], 0.0, 1.0)
        _check_range("position[1]", self.position[1], 0.0, 1.0)
        if self.size[0] <= 0 or self.size[1] <= 0:
            raise ValueError(f"size components must be positive, got {self.size!r}")
        for i, component in enumerate(self.color_rgb):
            _check_rgb_component(f"color_rgb[{i}]", component)
        _check_range("color_kelvin", self.color_kelvin, 1000, 40000)
        _check_range("brightness", self.brightness, 0.0, 1.0)
        _check_range("opacity", self.opacity, 0.0, 1.0)
        if self.feather < 0:
            raise ValueError(f"feather must be >= 0, got {self.feather!r}")
        if self.monitor_index < 0:
            raise ValueError(
                f"monitor_index must be >= 0, got {self.monitor_index!r}"
            )


@dataclass(slots=True)
class Profile:
    id: str
    name: str
    lights: list[Light] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Profile.name must be non-empty")


@dataclass(slots=True)
class ConfigData:
    version: int
    active_profile_id: str
    profiles: list[Profile] = field(default_factory=list)
    settings: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError(f"version must be >= 1, got {self.version!r}")
