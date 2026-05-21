from __future__ import annotations

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath

from ringlight_overlay.core.color import apply_brightness, kelvin_to_rgb
from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay.shapes.base import Shape

_CORNER_RADIUS = 12.0


class RectangleShape(Shape):
    """Rounded rectangle with optional edge feather."""

    @classmethod
    def default_params(cls) -> dict:
        return {}

    def paint(self, painter: QPainter, rect: QRectF, light: Light) -> None:
        if light.color_mode == "kelvin":
            rgb = apply_brightness(kelvin_to_rgb(light.color_kelvin), light.brightness)
        else:
            rgb = apply_brightness(light.color_rgb, light.brightness)

        color = QColor(*rgb)
        path = QPainterPath()
        path.addRoundedRect(rect, _CORNER_RADIUS, _CORNER_RADIUS)

        feather = light.feather
        if feather > 0:
            # Simple vertical linear gradient to simulate edge softness
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            alpha_color = QColor(color)
            alpha_color.setAlpha(0)
            feather_frac = min(feather / max(rect.height(), 1), 0.3)
            grad.setColorAt(0.0, alpha_color)
            grad.setColorAt(feather_frac, color)
            grad.setColorAt(1.0 - feather_frac, color)
            grad.setColorAt(1.0, alpha_color)
            painter.fillPath(path, grad)
        else:
            painter.fillPath(path, color)
