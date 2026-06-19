from __future__ import annotations

import logging
import uuid
from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
    QWizard,
    QWizardPage,
)

from ringlight_overlay.core.models import ConfigData, Light, Profile
from ringlight_overlay.core.monitors import MonitorInfo
from ringlight_overlay.core.storage import default_config

_log = logging.getLogger(__name__)

_SHAPES = ["ring", "circle", "rectangle"]
_DEFAULT_SIZE = 800


def build_first_run_light(
    monitor: MonitorInfo,
    shape: str = "ring",
    size: tuple[int, int] = (800, 800),
) -> Light:
    """Return an enabled Light targeting *monitor* with sensible defaults.

    Mirrors the default_config() light values except ``enabled=True`` and
    the monitor fields are set from *monitor*.
    """
    seed = default_config().profiles[0].lights[0]
    return Light(
        id=str(uuid.uuid4()),
        enabled=True,
        monitor_name=monitor.name,
        monitor_index=monitor.index,
        shape=shape,
        position=seed.position,
        size=size,
        color_mode=seed.color_mode,
        color_rgb=seed.color_rgb,
        color_kelvin=seed.color_kelvin,
        brightness=seed.brightness,
        opacity=seed.opacity,
        feather=seed.feather,
        shape_params=seed.shape_params,
    )


def apply_wizard_result(config: ConfigData, light: Light) -> ConfigData:
    """Return a new ConfigData with the active profile's lights replaced by *light*.

    All other settings (hotkeys, minimize_to_tray_on_close, etc.) are preserved.
    """
    active_id = config.active_profile_id
    new_profiles: list[Profile] = []
    for profile in config.profiles:
        if profile.id == active_id:
            new_profiles.append(replace(profile, lights=[light]))
        else:
            new_profiles.append(profile)
    return replace(config, profiles=new_profiles)


# ---------------------------------------------------------------------------
# QWizard pages
# ---------------------------------------------------------------------------


class _MonitorPage(QWizardPage):
    """Page 0: pick which monitor to target."""

    def __init__(self, monitors: list[MonitorInfo], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("Choose a Monitor")
        self.setSubTitle("Select the monitor where the overlay light will appear.")
        self._monitors = monitors

        layout = QVBoxLayout(self)
        self._combo = QComboBox()
        for m in monitors:
            label = f"{m.name} (primary)" if m.primary else m.name
            self._combo.addItem(label)
        layout.addWidget(QLabel("Monitor:"))
        layout.addWidget(self._combo)

    def selected_monitor(self) -> MonitorInfo:
        """Return the MonitorInfo chosen by the user."""
        idx = self._combo.currentIndex()
        return self._monitors[max(0, min(idx, len(self._monitors) - 1))]


class _ShapePage(QWizardPage):
    """Page 1: pick shape and size."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("Shape & Size")
        self.setSubTitle("Choose the overlay shape and approximate size.")

        layout = QVBoxLayout(self)

        self._shape_combo = QComboBox()
        for s in _SHAPES:
            self._shape_combo.addItem(s.capitalize(), s)
        layout.addWidget(QLabel("Shape:"))
        layout.addWidget(self._shape_combo)

        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(200, 1400)
        self._size_slider.setValue(_DEFAULT_SIZE)
        self._size_label = QLabel(f"Size: {_DEFAULT_SIZE} px")
        self._size_slider.valueChanged.connect(lambda v: self._size_label.setText(f"Size: {v} px"))
        layout.addWidget(QLabel("Size:"))
        layout.addWidget(self._size_slider)
        layout.addWidget(self._size_label)

    def selected_shape(self) -> str:
        return _SHAPES[self._shape_combo.currentIndex()]

    def selected_size(self) -> tuple[int, int]:
        v = self._size_slider.value()
        return (v, v)


class _EnablePage(QWizardPage):
    """Page 2: summary / enable confirmation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("Ready to Go")
        self.setSubTitle(
            "Click Finish to create an enabled overlay light on the chosen monitor.\n"
            "You can adjust all settings from the Settings window at any time."
        )
        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                "The overlay will be enabled immediately.\n"
                "Use the tray icon to toggle it or open Settings."
            )
        )


# ---------------------------------------------------------------------------
# Wizard
# ---------------------------------------------------------------------------

_PAGE_MONITOR = 0
_PAGE_SHAPE = 1
_PAGE_ENABLE = 2


class FirstRunWizard(QWizard):
    """Guided multi-step setup wizard shown on first launch.

    After ``exec()`` returns ``QDialog.Accepted``, call ``result_config(base)``
    to obtain the updated ``ConfigData``.
    """

    def __init__(
        self,
        monitors: list[MonitorInfo],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("RingLight Overlay — Setup")
        self.setMinimumSize(500, 300)
        # The Windows default (AeroStyle) paints a fixed light header/background
        # that ignores the system dark-mode palette, leaving the wizard rendered
        # white-on-white. ClassicStyle follows the standard widget palette, so it
        # stays readable in both light and dark mode.
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)

        self._monitor_page = _MonitorPage(monitors)
        self._shape_page = _ShapePage()
        self._enable_page = _EnablePage()

        self.addPage(self._monitor_page)
        self.addPage(self._shape_page)
        self.addPage(self._enable_page)

    def result_config(self, base_config: ConfigData) -> ConfigData:
        """Return a new ConfigData reflecting the wizard selections applied to *base_config*."""
        monitor = self._monitor_page.selected_monitor()
        shape = self._shape_page.selected_shape()
        size = self._shape_page.selected_size()
        light = build_first_run_light(monitor, shape=shape, size=size)
        return apply_wizard_result(base_config, light)
