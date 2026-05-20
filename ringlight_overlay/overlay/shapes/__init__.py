from __future__ import annotations

from ringlight_overlay.overlay.shapes.base import Shape
from ringlight_overlay.overlay.shapes.circle import CircleShape
from ringlight_overlay.overlay.shapes.rectangle import RectangleShape
from ringlight_overlay.overlay.shapes.ring import RingShape

_REGISTRY: dict[str, Shape] = {
    "ring": RingShape(),
    "circle": CircleShape(),
    "rectangle": RectangleShape(),
}


def get_shape(name: str) -> Shape:
    """Return the singleton Shape instance for *name*.

    Raises KeyError if the shape name is not registered.
    """
    try:
        return _REGISTRY[name]
    except KeyError:
        raise KeyError(f"Unknown shape: {name!r}. Valid shapes: {sorted(_REGISTRY)}")
