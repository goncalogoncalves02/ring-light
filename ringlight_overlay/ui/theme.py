from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


def build_dark_palette() -> QPalette:
    """Return an explicit dark QPalette for the Fusion style.

    Qt's native Windows style only partially propagates OS dark-mode into
    palette-driven chrome (QWizard readability regressed twice — see the
    fix history around #17). Fusion draws every widget strictly from the
    QPalette, so pairing it with an explicit palette guarantees consistent
    contrast everywhere, independent of the native style's own dark-mode
    detection.
    """
    palette = QPalette()
    window = QColor("#353535")
    base = QColor("#232323")
    text = QColor("#ffffff")
    disabled_text = QColor("#7f7f7f")
    highlight = QColor("#2a82da")

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, window)
    palette.setColor(QPalette.ColorRole.ToolTipBase, text)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, window)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff5555"))
    palette.setColor(QPalette.ColorRole.Link, highlight)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, text)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
    return palette


def build_light_palette() -> QPalette:
    """Return an explicit light QPalette matching Fusion's own default look.

    Values measured from Fusion's actual default palette so light mode is
    visually unchanged from today; the point is to stop relying on the
    style's *implicit* default and own the palette explicitly instead.
    """
    palette = QPalette()
    window = QColor("#efefef")
    base = QColor("#ffffff")
    text = QColor("#000000")
    disabled_text = QColor("#a0a0a0")
    highlight = QColor("#2a82da")

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, window)
    palette.setColor(QPalette.ColorRole.ToolTipBase, window)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, window)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ff0000"))
    palette.setColor(QPalette.ColorRole.Link, highlight)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, text)

    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled_text)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled_text)
    return palette


def apply_theme(app: QApplication) -> None:
    """Force the Fusion style and an explicit palette matching the OS color scheme.

    Detected once at startup; does not react to the OS theme changing while
    the app is running (a restart is required to pick up a new theme).
    """
    app.setStyle("Fusion")
    scheme = app.styleHints().colorScheme()
    if scheme == Qt.ColorScheme.Dark:
        app.setPalette(build_dark_palette())
    else:
        app.setPalette(build_light_palette())
