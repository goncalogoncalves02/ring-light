from __future__ import annotations

import pytest
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPixmap

from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay.shapes.base import Shape
from ringlight_overlay.overlay.shapes.circle import CircleShape
from ringlight_overlay.overlay.shapes.rectangle import RectangleShape
from ringlight_overlay.overlay.shapes.ring import RingShape
from tests.factories import make_light


def _paint_on_pixmap(shape: Shape, light: Light) -> None:
    pixmap = QPixmap(400, 400)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    shape.paint(painter, QRectF(0, 0, 400, 400), light)
    painter.end()


def test_shape_is_abstract() -> None:
    with pytest.raises(TypeError):
        Shape()  # type: ignore[abstract]


def test_ring_default_params_has_thickness() -> None:
    params = RingShape.default_params()
    assert "thickness" in params
    assert isinstance(params["thickness"], int)
    assert params["thickness"] > 0


def test_ring_paint_smoke(qapp) -> None:
    _paint_on_pixmap(RingShape(), make_light(shape="ring"))


def test_circle_default_params_returns_dict(qapp) -> None:
    assert isinstance(CircleShape.default_params(), dict)


def test_circle_paint_smoke(qapp) -> None:
    _paint_on_pixmap(CircleShape(), make_light(shape="circle"))


def test_rectangle_default_params_returns_dict(qapp) -> None:
    assert isinstance(RectangleShape.default_params(), dict)


def test_rectangle_paint_smoke(qapp) -> None:
    _paint_on_pixmap(RectangleShape(), make_light(shape="rectangle"))
