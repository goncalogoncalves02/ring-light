from __future__ import annotations

from PySide6.QtCore import QRect, QRectF, Qt
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
        self._target_screen_name: str | None = None
        self._target_rect: QRect | None = None
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

    def apply_placement(self, screen, rect: QRect) -> None:
        """Anchor this window to *screen* and apply *rect* (global coords).

        Anchoring matters: with per-monitor DPI, global logical coordinates
        are ambiguous across screens — Qt disambiguates via the window's
        screen association and may silently re-assign an unanchored window.
        setScreen() may recreate the native window, dropping the Win32
        click-through styles applied in showEvent, so re-apply them here
        when already visible.
        """
        self._target_screen_name = screen.name() if screen is not None else None
        self._target_rect = QRect(rect)
        if screen is not None and self.screen() is not screen:
            self.setScreen(screen)
        self.setGeometry(rect)
        if self.isVisible():
            apply_click_through(int(self.winId()))
