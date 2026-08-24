from __future__ import annotations

from ringlight_overlay.core.models import Profile
from ringlight_overlay.overlay.overlay_manager import OverlayManager
from tests.factories import make_light, make_monitor


def test_apply_profile_creates_windows(qapp) -> None:
    manager = OverlayManager()
    light = make_light()
    profile = Profile(id="p-1", name="Test", lights=[light])
    manager.apply_profile(profile, [make_monitor()])
    assert manager.window_count == 1
    manager.close_all()


def test_apply_profile_removes_old_windows_on_update(qapp) -> None:
    manager = OverlayManager()
    light_a = make_light()
    light_b = make_light()
    profile_a = Profile(id="p-1", name="A", lights=[light_a, light_b])
    manager.apply_profile(profile_a, [make_monitor()])
    assert manager.window_count == 2

    profile_b = Profile(id="p-1", name="A", lights=[light_b])
    manager.apply_profile(profile_b, [make_monitor()])
    assert manager.window_count == 1
    manager.close_all()


def test_disabled_light_window_is_hidden(qapp) -> None:
    manager = OverlayManager()
    light = make_light(enabled=False)
    profile = Profile(id="p-1", name="Test", lights=[light])
    manager.apply_profile(profile, [make_monitor()])
    win = manager.get_window(light.id)
    assert win is not None
    assert not win.isVisible()
    manager.close_all()


def test_close_all_removes_all_windows(qapp) -> None:
    manager = OverlayManager()
    lights = [make_light() for _ in range(3)]
    profile = Profile(id="p-1", name="T", lights=lights)
    manager.apply_profile(profile, [make_monitor()])
    assert manager.window_count == 3
    manager.close_all()
    assert manager.window_count == 0


def test_position_window_uses_screen_anchored_placement(qapp, monkeypatch) -> None:
    from unittest.mock import Mock

    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_manager as om_module
    from ringlight_overlay.overlay.overlay_window import OverlayWindow

    sentinel_screen = Mock()
    sentinel_screen.name.return_value = "\\\\.\\DISPLAY1"
    monkeypatch.setattr(om_module, "qscreen_for", lambda monitor: sentinel_screen)

    placements: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: placements.append((s, r))
    )

    manager = OverlayManager()
    light = (
        make_light()
    )  # position (0.5, 0.5), size 400x400, monitor \\.\DISPLAY1 @ (0,0,1920,1080)
    profile = Profile(id="p-1", name="T", lights=[light])
    manager.apply_profile(profile, [make_monitor()])

    assert placements == [(sentinel_screen, QRect(760, 340, 400, 400))]
    manager.close_all()


def test_position_window_with_unresolvable_screen_still_places(qapp, monkeypatch) -> None:
    from PySide6.QtCore import QRect

    import ringlight_overlay.overlay.overlay_manager as om_module
    from ringlight_overlay.overlay.overlay_window import OverlayWindow

    monkeypatch.setattr(om_module, "qscreen_for", lambda monitor: None)

    placements: list[tuple] = []
    monkeypatch.setattr(
        OverlayWindow, "apply_placement", lambda self, s, r: placements.append((s, r))
    )

    manager = OverlayManager()
    light = make_light()
    profile = Profile(id="p-1", name="T", lights=[light])
    manager.apply_profile(profile, [make_monitor()])

    assert placements == [(None, QRect(760, 340, 400, 400))]
    manager.close_all()
