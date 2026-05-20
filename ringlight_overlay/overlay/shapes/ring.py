from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QRadialGradient

from ringlight_overlay.core.color import apply_brightness, kelvin_to_rgb
from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay.shapes.base import Shape


class RingShape(Shape):
    """Ring (donut) shape — outer ellipse minus inner ellipse."""

    @classmethod
    def default_params(cls) -> dict:
        return {"thickness": 80}

    def paint(self, painter: QPainter, rect: QRectF, light: Light) -> None:
        thickness = int(light.shape_params.get("thickness", 80))
        feather = light.feather

        if light.color_mode == "kelvin":
            rgb = apply_brightness(kelvin_to_rgb(light.color_kelvin), light.brightness)
        else:
            rgb = apply_brightness(light.color_rgb, light.brightness)

        color = QColor(*rgb)

        cx = rect.center().x()
        cy = rect.center().y()
        rx = rect.width() / 2.0
        ry = rect.height() / 2.0

        outer = QPainterPath()
        outer.addEllipse(rect)

        inset = max(0, min(thickness, int(min(rx, ry)) - 1))
        inner_rect = QRectF(
            rect.x() + inset,
            rect.y() + inset,
            rect.width() - 2 * inset,
            rect.height() - 2 * inset,
        )
        inner = QPainterPath()
        inner.addEllipse(inner_rect)
        ring = outer.subtracted(inner)

        painter.save()
        painter.setClipPath(ring)

        if feather > 0:
            grad = QRadialGradient(QPointF(cx, cy), max(rx, ry))
            mid = 1.0 - (inset / max(rx, ry))
            max_feather_frac = (1.0 - mid) / 2.0
            feather_frac = min(feather / max(rx, ry), 0.15, max_feather_frac)
            alpha_color = QColor(color)
            alpha_color.setAlpha(0)
            grad.setColorAt(0.0, alpha_color)
            grad.setColorAt(max(0.0, mid - feather_frac), alpha_color)
            grad.setColorAt(min(1.0, mid), color)
            grad.setColorAt(min(1.0, 1.0 - feather_frac), color)
            grad.setColorAt(1.0, alpha_color)
            painter.fillPath(ring, grad)
        else:
            painter.fillPath(ring, color)

        painter.restore()
