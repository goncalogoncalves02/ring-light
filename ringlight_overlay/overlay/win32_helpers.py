from __future__ import annotations

import ctypes
import ctypes.wintypes
import sys

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

_CLICK_THROUGH_FLAGS = WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE

# ctypes.windll exists only on Windows; guard so the module imports on any
# platform (CI/dev on Linux) — the Win32 calls then no-op off Windows.
_IS_WINDOWS = sys.platform == "win32"

if _IS_WINDOWS:
    _user32 = ctypes.windll.user32
    _user32.GetWindowLongPtrW.restype = ctypes.c_ssize_t
    _user32.GetWindowLongPtrW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int]
    _user32.SetWindowLongPtrW.restype = ctypes.c_ssize_t
    _user32.SetWindowLongPtrW.argtypes = [ctypes.wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t]


def apply_click_through(hwnd: int) -> None:
    """Apply click-through extended window styles via SetWindowLongPtrW.

    Must be called from showEvent() — the HWND does not exist until the
    window is shown. Silently skips when hwnd is 0 (offscreen Qt platform)
    or when running off Windows.
    """
    if not hwnd or not _IS_WINDOWS:
        return
    current: int = _user32.GetWindowLongPtrW(hwnd, GWL_EXSTYLE)
    _user32.SetWindowLongPtrW(hwnd, GWL_EXSTYLE, current | _CLICK_THROUGH_FLAGS)


def set_app_user_model_id(app_id: str) -> None:
    """Set an explicit AppUserModelID for this process.

    Without it, a Python-hosted app is grouped under the interpreter and the
    taskbar shows python.exe's icon instead of the window icon. Must be called
    before the first window is created. No-op (and never raises) off Windows.
    """
    if not _IS_WINDOWS:
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:  # pragma: no cover - defensive, Windows-only path
        pass
