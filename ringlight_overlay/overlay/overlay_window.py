from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay import shapes
from ringlight_overlay.overlay.win32_helpers import apply_click_through


class OverlayWindow(QWidget):
    """Transparent, topmost, click-through overlay window for one Light."""

    def __init__(self, light: Light, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._light = light
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setWindowOpacity(light.opacity)

    @property
    def light(self) -> Light:
        return self._light

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        apply_click_through(int(self.winId()))

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        shape = shapes.get_shape(self._light.shape)
        rect = QRectF(self.rect())
        shape.paint(painter, rect, self._light)
        painter.end()

    def update_light(self, light: Light) -> None:
        self._light = light
        self.setWindowOpacity(light.opacity)
        self.update()
