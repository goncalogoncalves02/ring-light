from __future__ import annotations

import os

import pytest

# Force the offscreen Qt platform so the test suite never needs a display
# server. Harmless on Windows where the native plugin would also work.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication for tests that need Qt initialised."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture(autouse=True)
def _cleanup_qt_widgets():
    """Close and delete any top-level widgets a test leaves behind.

    Without this, PySide6 widgets linger until interpreter shutdown, where
    destroying them alongside the QApplication intermittently segfaults on
    windows-latest (exit code 0xC0000005). Runs after every test; a no-op when
    no QApplication exists (pure non-Qt tests never instantiate one).
    """
    yield
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        return
    for widget in list(app.topLevelWidgets()):
        widget.close()
        widget.deleteLater()
    app.processEvents()
