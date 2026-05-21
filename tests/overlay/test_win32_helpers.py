from __future__ import annotations

from ringlight_overlay.overlay.win32_helpers import (
    GWL_EXSTYLE,
    WS_EX_LAYERED,
    WS_EX_NOACTIVATE,
    WS_EX_TOOLWINDOW,
    WS_EX_TRANSPARENT,
    apply_click_through,
)


def test_win32_constants_have_correct_values() -> None:
    assert GWL_EXSTYLE == -20
    assert WS_EX_LAYERED == 0x00080000
    assert WS_EX_TRANSPARENT == 0x00000020
    assert WS_EX_TOOLWINDOW == 0x00000080
    assert WS_EX_NOACTIVATE == 0x08000000


def test_apply_click_through_accepts_zero_hwnd_as_noop() -> None:
    # On offscreen Qt (CI), winId() returns 0 — must not raise.
    apply_click_through(0)


def test_apply_click_through_is_callable() -> None:
    assert callable(apply_click_through)
