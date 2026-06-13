from __future__ import annotations

import ringlight_overlay
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ringlight_overlay.core.resources import app_icon_path

_REPO_URL = "https://github.com/goncalogoncalves02/ring-light"
_APP_NAME = "RingLight Overlay"
_DESCRIPTION = "Transparent click-through overlay windows simulating ring/softbox lights on secondary monitors."
_LICENSE_TEXT = "MIT License"


class AboutDialog(QDialog):
    """Dialog showing version, description, license, and repository link."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"About {_APP_NAME}")
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # App icon (optional — silently absent when file is missing)
        icon_path = app_icon_path()
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QIcon(str(icon_path)).pixmap(48, 48)
            icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)

        name_label = QLabel(f"<b>{_APP_NAME}</b>")
        layout.addWidget(name_label)

        version_label = QLabel(f"Version {ringlight_overlay.__version__}")
        version_label.setObjectName("version_label")
        layout.addWidget(version_label)

        desc_label = QLabel(_DESCRIPTION)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        license_label = QLabel(_LICENSE_TEXT)
        layout.addWidget(license_label)

        repo_btn = QPushButton("Open Repository")
        repo_btn.clicked.connect(self._open_repo)
        layout.addWidget(repo_btn)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _open_repo(self) -> None:
        QDesktopServices.openUrl(QUrl(_REPO_URL))
