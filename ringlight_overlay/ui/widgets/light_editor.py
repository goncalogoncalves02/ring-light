from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ringlight_overlay.core.models import Light
from ringlight_overlay.core.monitors import MonitorInfo
from ringlight_overlay.ui.widgets.color_picker import ColorPicker

_SHAPES = ["ring", "circle", "rectangle"]


class LightEditor(QWidget):
    """Property editor for a single Light. Emits light_changed on any change."""

    light_changed = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._light: Light | None = None
        self._loading = False
        self._monitors: list[MonitorInfo] = []
        self._build_ui()
        self.setEnabled(False)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        form = QFormLayout()

        self._shape_combo = QComboBox()
        self._shape_combo.addItems(_SHAPES)
        form.addRow("Shape:", self._shape_combo)

        self._monitor_combo = QComboBox()
        form.addRow("Monitor:", self._monitor_combo)

        self._pos_x = QDoubleSpinBox()
        self._pos_x.setRange(0.0, 1.0)
        self._pos_x.setSingleStep(0.05)
        self._pos_x.setDecimals(2)
        form.addRow("Position X:", self._pos_x)

        self._pos_y = QDoubleSpinBox()
        self._pos_y.setRange(0.0, 1.0)
        self._pos_y.setSingleStep(0.05)
        self._pos_y.setDecimals(2)
        form.addRow("Position Y:", self._pos_y)

        self._size_w = QSpinBox()
        self._size_w.setRange(1, 9999)
        form.addRow("Width (px):", self._size_w)

        self._size_h = QSpinBox()
        self._size_h.setRange(1, 9999)
        form.addRow("Height (px):", self._size_h)

        self._feather = QSpinBox()
        self._feather.setRange(0, 500)
        form.addRow("Feather (px):", self._feather)

        self._thickness_label = QLabel("Thickness (px):")
        self._thickness = QSpinBox()
        self._thickness.setRange(1, 9999)
        form.addRow(self._thickness_label, self._thickness)

        root.addLayout(form)

        self._color_picker = ColorPicker()
        group = QGroupBox("Color")
        g_layout = QVBoxLayout(group)
        g_layout.addWidget(self._color_picker)
        root.addWidget(group)

        self._shape_combo.currentTextChanged.connect(self._on_shape_changed)
        self._monitor_combo.currentIndexChanged.connect(self._emit_changed)
        self._pos_x.valueChanged.connect(self._emit_changed)
        self._pos_y.valueChanged.connect(self._emit_changed)
        self._size_w.valueChanged.connect(self._emit_changed)
        self._size_h.valueChanged.connect(self._emit_changed)
        self._feather.valueChanged.connect(self._emit_changed)
        self._thickness.valueChanged.connect(self._emit_changed)
        self._color_picker.color_changed.connect(self._emit_changed)

    def load_monitors(self, monitors: list[MonitorInfo]) -> None:
        self._monitors = monitors
        self._monitor_combo.clear()
        for m in monitors:
            self._monitor_combo.addItem(m.name, userData=m.index)

    def load_light(self, light: Light) -> None:
        self._loading = True
        self._light = light
        self.setEnabled(True)

        idx = _SHAPES.index(light.shape) if light.shape in _SHAPES else 0
        self._shape_combo.setCurrentIndex(idx)
        self._update_thickness_visibility(light.shape)

        monitor_idx = next(
            (i for i, m in enumerate(self._monitors) if m.name == light.monitor_name),
            0,
        )
        self._monitor_combo.setCurrentIndex(monitor_idx)

        self._pos_x.setValue(light.position[0])
        self._pos_y.setValue(light.position[1])
        self._size_w.setValue(light.size[0])
        self._size_h.setValue(light.size[1])
        self._feather.setValue(light.feather)
        self._thickness.setValue(int(light.shape_params.get("thickness", 80)))

        self._color_picker.set_values(
            color_mode=light.color_mode,
            color_rgb=light.color_rgb,
            color_kelvin=light.color_kelvin,
            brightness=light.brightness,
            opacity=light.opacity,
        )
        self._loading = False

    def clear(self) -> None:
        self._light = None
        self.setEnabled(False)

    def current_light_id(self) -> str | None:
        return self._light.id if self._light is not None else None

    def current_shape(self) -> str:
        return self._shape_combo.currentText()

    def current_feather(self) -> int:
        return self._feather.value()

    def _update_thickness_visibility(self, shape: str) -> None:
        visible = shape == "ring"
        self._thickness_label.setVisible(visible)
        self._thickness.setVisible(visible)

    def _on_shape_changed(self, shape: str) -> None:
        self._update_thickness_visibility(shape)
        self._emit_changed()

    def _emit_changed(self, *_args) -> None:
        if self._loading or self._light is None:
            return
        shape = self._shape_combo.currentText()
        shape_params: dict = {}
        if shape == "ring":
            shape_params = {"thickness": self._thickness.value()}

        monitor_name = ""
        monitor_index = 0
        if self._monitors:
            mi = self._monitor_combo.currentIndex()
            if 0 <= mi < len(self._monitors):
                monitor_name = self._monitors[mi].name
                monitor_index = self._monitors[mi].index

        new_light = Light(
            id=self._light.id,
            enabled=self._light.enabled,
            monitor_name=monitor_name,
            monitor_index=monitor_index,
            shape=shape,
            position=(self._pos_x.value(), self._pos_y.value()),
            size=(self._size_w.value(), self._size_h.value()),
            color_mode=self._color_picker.color_mode(),
            color_rgb=self._color_picker.color_rgb(),
            color_kelvin=self._color_picker.color_kelvin(),
            brightness=self._color_picker.brightness(),
            opacity=self._color_picker.opacity(),
            feather=self._feather.value(),
            shape_params=shape_params,
        )
        self.light_changed.emit(new_light)
