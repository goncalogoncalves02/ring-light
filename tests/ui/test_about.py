from __future__ import annotations

import ringlight_overlay
from ringlight_overlay.ui.dialogs.about import AboutDialog


class TestAboutDialog:
    def test_constructs(self, qapp):
        dlg = AboutDialog()
        assert dlg is not None

    def test_window_title_contains_app_name(self, qapp):
        dlg = AboutDialog()
        assert "RingLight Overlay" in dlg.windowTitle()

    def test_version_label_contains_version(self, qapp):
        dlg = AboutDialog()
        version_label = dlg.findChild(type(None).__mro__[0], "version_label")
        # Find by scanning children for the version string
        from PySide6.QtWidgets import QLabel

        labels = dlg.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        version = ringlight_overlay.__version__
        assert any(version in t for t in texts), f"Version {version!r} not found in labels: {texts}"

    def test_version_is_0_2_2(self, qapp):
        assert ringlight_overlay.__version__ == "0.2.2"
