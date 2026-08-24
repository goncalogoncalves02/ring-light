from __future__ import annotations

from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from ringlight_overlay.core.models import Light
from ringlight_overlay.core.monitors import qscreen_by_name
from ringlight_overlay.overlay import shapes
from ringlight_overlay.overlay.win32_helpers import apply_click_through


class OverlayWindow(QWidget):
    """Transparent, topmost, click-through overlay window for one Light."""

    def __init__(self, light: Light, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._light = light
        self._target_screen_name: str | None = None
        self._target_rect: QRect | None = None
        self._screen_watch_connected = False
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
        handle = self.windowHandle()
        if handle is not None and not self._screen_watch_connected:
            handle.screenChanged.connect(self._on_screen_changed)
            self._screen_watch_connected = True

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

    def _on_screen_changed(self, screen) -> None:
        """Undo unsolicited screen moves (e.g. DPI-change fallout on Windows).

        Loop-safe without a re-entrancy guard: re-asserting moves us back to
        the target, so the follow-up screenChanged(target) matches the name
        and no-ops. If the target screen vanished (monitor unplugged), do
        nothing — the next apply_profile() will re-home the light.
        """
        target = self._target_screen_name
        if not target or self._target_rect is None:
            return
        if screen is not None and screen.name() == target:
            return
        restored = qscreen_by_name(target)
        if restored is None:
            return
        self.apply_placement(restored, self._target_rect)
