from __future__ import annotations

import pytest
from PySide6.QtCore import Qt

from ringlight_overlay.core.models import Light
from ringlight_overlay.overlay.overlay_window import OverlayWindow
from tests.factories import make_light


def test_overlay_window_has_frameless_hint(qapp) -> None:
    win = OverlayWindow(make_light())
    flags = win.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint


def test_overlay_window_has_stays_on_top_hint(qapp) -> None:
    win = OverlayWindow(make_light())
    assert win.windowFlags() & Qt.WindowType.WindowStaysOnTopHint


def test_overlay_window_has_translucent_background(qapp) -> None:
    win = OverlayWindow(make_light())
    assert win.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)


def test_update_light_changes_opacity(qapp) -> None:
    light = make_light()
    win = OverlayWindow(light)
    new_light = Light(
        id=light.id,
        enabled=light.enabled,
        monitor_name=light.monitor_name,
        monitor_index=light.monitor_index,
        shape=light.shape,
        position=light.position,
        size=light.size,
        color_mode=light.color_mode,
        color_rgb=light.color_rgb,
        color_kelvin=light.color_kelvin,
        brightness=light.brightness,
        opacity=0.5,
        feather=light.feather,
        shape_params=light.shape_params,
    )
    win.update_light(new_light)
    assert abs(win.windowOpacity() - 0.5) < 0.01


def test_update_light_stores_new_light(qapp) -> None:
    light = make_light()
    win = OverlayWindow(light)
    new_light = Light(
        id=light.id,
        enabled=light.enabled,
        monitor_name=light.monitor_name,
        monitor_index=light.monitor_index,
        shape="circle",
        position=light.position,
        size=light.size,
        color_mode=light.color_mode,
        color_rgb=light.color_rgb,
        color_kelvin=light.color_kelvin,
        brightness=light.brightness,
        opacity=light.opacity,
        feather=light.feather,
        shape_params={},
    )
    win.update_light(new_light)
    assert win.light.shape == "circle"


def test_apply_placement_sets_geometry(qapp) -> None:
    from PySide6.QtCore import QRect

    win = OverlayWindow(make_light())
    win.apply_placement(None, QRect(100, 200, 400, 400))
    assert win.geometry() == QRect(100, 200, 400, 400)
    win.close()


def test_apply_placement_anchors_to_screen_when_different(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    win = OverlayWindow(make_light())
    calls: list[object] = []
    monkeypatch.setattr(OverlayWindow, "setScreen", lambda self, s: calls.append(s))

    fake_screen = Mock()
    fake_screen.name.return_value = "\\\\.\\DISPLAY2"
    win.apply_placement(fake_screen, QRect(0, 0, 400, 400))

    assert calls == [fake_screen]
    assert win._target_screen_name == "\\\\.\\DISPLAY2"
    win.close()


def test_apply_placement_skips_setscreen_when_already_on_target(qapp, monkeypatch) -> None:
    from PySide6.QtCore import QRect

    win = OverlayWindow(make_light())
    calls: list[object] = []
    monkeypatch.setattr(OverlayWindow, "setScreen", lambda self, s: calls.append(s))

    win.apply_placement(win.screen(), QRect(0, 0, 400, 400))
    assert calls == []
    win.close()


def test_apply_placement_reapplies_click_through_when_visible(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_window as ow_module

    win = OverlayWindow(make_light())
    win.show()
    hwnds: list[int] = []
    monkeypatch.setattr(ow_module, "apply_click_through", lambda hwnd: hwnds.append(hwnd))

    fake_screen = Mock()
    fake_screen.name.return_value = "\\\\.\\DISPLAY2"
    monkeypatch.setattr(OverlayWindow, "setScreen", lambda self, s: None)
    win.apply_placement(fake_screen, QRect(0, 0, 400, 400))

    assert hwnds == [int(win.winId())]
    win.close()


def test_screen_changed_to_wrong_screen_reasserts_placement(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_window as ow_module

    win = OverlayWindow(make_light())
    win._target_screen_name = "\\\\.\\DISPLAY2"
    win._target_rect = QRect(1920, 0, 400, 400)

    restored_screen = Mock()
    restored_screen.name.return_value = "\\\\.\\DISPLAY2"
    monkeypatch.setattr(ow_module, "qscreen_by_name", lambda name: restored_screen)

    reasserted: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: reasserted.append((s, r))
    )

    wrong_screen = Mock()
    wrong_screen.name.return_value = "\\\\.\\DISPLAY1"
    win._on_screen_changed(wrong_screen)

    assert reasserted == [(restored_screen, QRect(1920, 0, 400, 400))]
    win.close()


def test_screen_changed_to_target_screen_is_noop(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    win = OverlayWindow(make_light())
    win._target_screen_name = "\\\\.\\DISPLAY2"
    win._target_rect = QRect(1920, 0, 400, 400)

    reasserted: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: reasserted.append((s, r))
    )

    same_screen = Mock()
    same_screen.name.return_value = "\\\\.\\DISPLAY2"
    win._on_screen_changed(same_screen)

    assert reasserted == []
    win.close()


def test_screen_changed_with_no_target_is_noop(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    win = OverlayWindow(make_light())
    reasserted: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: reasserted.append((s, r))
    )
    win._on_screen_changed(Mock())
    assert reasserted == []
    win.close()


def test_screen_changed_when_target_screen_missing_is_noop(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_window as ow_module

    win = OverlayWindow(make_light())
    win._target_screen_name = "\\\\.\\GONE"
    win._target_rect = QRect(0, 0, 400, 400)
    monkeypatch.setattr(ow_module, "qscreen_by_name", lambda name: None)

    reasserted: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: reasserted.append((s, r))
    )

    other = Mock()
    other.name.return_value = "\\\\.\\DISPLAY1"
    win._on_screen_changed(other)
    assert reasserted == []
    win.close()


def test_on_screen_changed_reentrancy_guard_blocks_call(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_window as ow_module

    win = OverlayWindow(make_light())
    win._target_screen_name = "\\\\.\\DISPLAY2"
    win._target_rect = QRect(1920, 0, 400, 400)
    win._reasserting = True

    # qscreen_by_name resolves fine here — without the guard this would go
    # on to call apply_placement, proving the early return is what stops it.
    restored_screen = Mock()
    restored_screen.name.return_value = "\\\\.\\DISPLAY2"
    monkeypatch.setattr(ow_module, "qscreen_by_name", lambda name: restored_screen)

    reasserted: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: reasserted.append((s, r))
    )

    wrong_screen = Mock()
    wrong_screen.name.return_value = "\\\\.\\DISPLAY1"
    win._on_screen_changed(wrong_screen)

    assert reasserted == []
    win.close()


def test_on_screen_changed_does_not_recurse_when_reassert_reenters(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_window as ow_module

    win = OverlayWindow(make_light())
    win._target_screen_name = "\\\\.\\DISPLAY2"
    win._target_rect = QRect(1920, 0, 400, 400)

    restored_screen = Mock()
    restored_screen.name.return_value = "\\\\.\\DISPLAY2"
    monkeypatch.setattr(ow_module, "qscreen_by_name", lambda name: restored_screen)

    wrong_screen = Mock()
    wrong_screen.name.return_value = "\\\\.\\DISPLAY1"

    calls: list[object] = []

    def fake_apply_placement(self, screen, rect):
        calls.append(screen)
        # Simulate setGeometry() inside the real apply_placement landing the
        # window back on the wrong screen mid-reassert — this must not
        # recurse into another apply_placement call.
        self._on_screen_changed(wrong_screen)

    monkeypatch.setattr(OverlayWindow, "apply_placement", fake_apply_placement)

    win._on_screen_changed(wrong_screen)  # must not raise RecursionError

    assert calls == [restored_screen]  # the re-entrant call was dropped by the guard
    win.close()


def test_show_connects_screen_watch_once(qapp, monkeypatch) -> None:
    win = OverlayWindow(make_light())

    observed: list[object] = []
    monkeypatch.setattr(OverlayWindow, "_on_screen_changed", lambda self, s: observed.append(s))

    win.show()
    assert win._watched_handle is win.windowHandle()
    win.hide()
    win.show()  # second show with the same handle must not double-connect
    assert win._watched_handle is win.windowHandle()

    sentinel = win.screen()
    win.windowHandle().screenChanged.emit(sentinel)
    assert observed == [sentinel]  # exactly one call — proves single connection, not zero or two
    win.close()
