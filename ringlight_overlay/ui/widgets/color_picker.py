from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

_KELVIN_PRESETS = [
    ("Warm", 2700),
    ("Neutral", 4000),
    ("Daylight", 5600),
    ("Cool", 6500),
]


class ColorPicker(QWidget):
    """Color mode selector, brightness and opacity controls."""

    color_changed = Signal(str, tuple, int, float, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._building = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        mode_row = QHBoxLayout()
        self._rb_rgb = QRadioButton("RGB")
        self._rb_kelvin = QRadioButton("Kelvin")
        self._rb_rgb.setChecked(True)
        self._mode_group = QButtonGroup(self)
        self._mode_group.addButton(self._rb_rgb, 0)
        self._mode_group.addButton(self._rb_kelvin, 1)
        mode_row.addWidget(self._rb_rgb)
        mode_row.addWidget(self._rb_kelvin)
        mode_row.addStretch()
        root.addLayout(mode_row)

        self._stack = QStackedWidget()
        root.addWidget(self._stack)

        rgb_widget = QWidget()
        rgb_form = QFormLayout(rgb_widget)
        self._spin_r = QSpinBox()
        self._spin_r.setRange(0, 255)
        self._spin_g = QSpinBox()
        self._spin_g.setRange(0, 255)
        self._spin_b = QSpinBox()
        self._spin_b.setRange(0, 255)
        rgb_form.addRow("R:", self._spin_r)
        rgb_form.addRow("G:", self._spin_g)
        rgb_form.addRow("B:", self._spin_b)
        self._stack.addWidget(rgb_widget)

        kelvin_widget = QWidget()
        kelvin_layout = QVBoxLayout(kelvin_widget)
        kelvin_layout.setContentsMargins(0, 0, 0, 0)

        self._kelvin_slider = QSlider(Qt.Orientation.Horizontal)
        self._kelvin_slider.setRange(1000, 40000)
        self._kelvin_slider.setValue(5600)
        self._kelvin_label = QLabel("5600 K")
        kelvin_layout.addWidget(self._kelvin_slider)
        kelvin_layout.addWidget(self._kelvin_label)

        presets_row = QHBoxLayout()
        for name, k in _KELVIN_PRESETS:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _=False, kv=k: self._set_kelvin(kv))
            presets_row.addWidget(btn)
        kelvin_layout.addLayout(presets_row)
        self._stack.addWidget(kelvin_widget)

        extra_form = QFormLayout()

        self._brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self._brightness_slider.setRange(0, 100)
        self._brightness_slider.setValue(100)
        self._brightness_label = QLabel("100%")
        brow = QHBoxLayout()
        brow.addWidget(self._brightness_slider)
        brow.addWidget(self._brightness_label)
        extra_form.addRow("Brightness:", brow)

        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(0, 100)
        self._opacity_slider.setValue(100)
        self._opacity_label = QLabel("100%")
        orow = QHBoxLayout()
        orow.addWidget(self._opacity_slider)
        orow.addWidget(self._opacity_label)
        extra_form.addRow("Opacity:", orow)

        root.addLayout(extra_form)

        self._mode_group.idClicked.connect(self._on_mode_changed)
        self._kelvin_slider.valueChanged.connect(self._on_kelvin_slider_changed)
        self._brightness_slider.valueChanged.connect(self._on_brightness_changed)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        self._spin_r.valueChanged.connect(self._notify_change)
        self._spin_g.valueChanged.connect(self._notify_change)
        self._spin_b.valueChanged.connect(self._notify_change)

    def set_values(
        self,
        color_mode: str,
        color_rgb: tuple[int, int, int],
        color_kelvin: int,
        brightness: float,
        opacity: float,
    ) -> None:
        self._building = True
        is_kelvin = color_mode == "kelvin"
        self._rb_kelvin.setChecked(is_kelvin)
        self._rb_rgb.setChecked(not is_kelvin)
        self._stack.setCurrentIndex(1 if is_kelvin else 0)

        self._spin_r.setValue(color_rgb[0])
        self._spin_g.setValue(color_rgb[1])
        self._spin_b.setValue(color_rgb[2])

        self._kelvin_slider.setValue(color_kelvin)
        self._kelvin_label.setText(f"{color_kelvin} K")

        b_pct = int(round(brightness * 100))
        self._brightness_slider.setValue(b_pct)
        self._brightness_label.setText(f"{b_pct}%")

        o_pct = int(round(opacity * 100))
        self._opacity_slider.setValue(o_pct)
        self._opacity_label.setText(f"{o_pct}%")

        self._building = False

    def color_mode(self) -> str:
        return "kelvin" if self._rb_kelvin.isChecked() else "rgb"

    def color_rgb(self) -> tuple[int, int, int]:
        return (self._spin_r.value(), self._spin_g.value(), self._spin_b.value())

    def color_kelvin(self) -> int:
        return self._kelvin_slider.value()

    def brightness(self) -> float:
        return self._brightness_slider.value() / 100.0

    def opacity(self) -> float:
        return self._opacity_slider.value() / 100.0

    def _set_kelvin(self, kelvin: int) -> None:
        self._kelvin_slider.setValue(kelvin)

    def _on_mode_changed(self, btn_id: int) -> None:
        self._stack.setCurrentIndex(btn_id)
        self._notify_change()

    def _on_kelvin_slider_changed(self, value: int) -> None:
        self._kelvin_label.setText(f"{value} K")
        self._notify_change()

    def _on_brightness_changed(self, value: int) -> None:
        self._brightness_label.setText(f"{value}%")
        self._notify_change()

    def _on_opacity_changed(self, value: int) -> None:
        self._opacity_label.setText(f"{value}%")
        self._notify_change()

    def _notify_change(self, *_args) -> None:
        if self._building:
            return
        self.color_changed.emit(
            self.color_mode(),
            self.color_rgb(),
            self.color_kelvin(),
            self.brightness(),
            self.opacity(),
        )
