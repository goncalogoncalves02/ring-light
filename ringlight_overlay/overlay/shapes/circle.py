from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QRadialGradient

from ringlight_overlay.core.color import apply_brightness, kelvin_to_rgb
from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay.shapes.base import Shape


class CircleShape(Shape):
    """Solid circle with optional radial feather."""

    @classmethod
    def default_params(cls) -> dict:
        return {}

    def paint(self, painter: QPainter, rect: QRectF, light: Light) -> None:
        feather = light.feather

        if light.color_mode == "kelvin":
            rgb = apply_brightness(kelvin_to_rgb(light.color_kelvin), light.brightness)
        else:
            rgb = apply_brightness(light.color_rgb, light.brightness)

        color = QColor(*rgb)
        cx = rect.center().x()
        cy = rect.center().y()
        radius = min(rect.width(), rect.height()) / 2.0

        path = QPainterPath()
        path.addEllipse(rect)

        if feather > 0:
            grad = QRadialGradient(QPointF(cx, cy), radius)
            feather_frac = min(feather / radius, 0.4)
            alpha_color = QColor(color)
            alpha_color.setAlpha(0)
            grad.setColorAt(0.0, color)
            grad.setColorAt(max(0.0, 1.0 - feather_frac), color)
            grad.setColorAt(1.0, alpha_color)
            painter.fillPath(path, grad)
        else:
            painter.fillPath(path, color)
