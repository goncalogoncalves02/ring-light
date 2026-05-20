from __future__ import annotations

import ctypes

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

_CLICK_THROUGH_FLAGS = WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE

_user32 = ctypes.windll.user32


def apply_click_through(hwnd: int) -> None:
    """Apply click-through extended window styles via SetWindowLongPtrW.

    Must be called from showEvent() — the HWND does not exist until the
    window is shown. Silently skips when hwnd is 0 (offscreen Qt platform).
    """
    if not hwnd:
        return
    current: int = _user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    _user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, current | _CLICK_THROUGH_FLAGS)
