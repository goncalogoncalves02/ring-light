from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtCore import QRectF
    from PySide6.QtGui import QPainter

    from ringlight_overlay.core.models import Light


class Shape(ABC):
    """Abstract base for overlay shape painters."""

    @abstractmethod
    def paint(self, painter: QPainter, rect: QRectF, light: Light) -> None:
        """Paint this shape into *rect* using *painter* with settings from *light*."""

    @classmethod
    @abstractmethod
    def default_params(cls) -> dict:
        """Return default shape_params for this shape type."""
