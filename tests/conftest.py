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
