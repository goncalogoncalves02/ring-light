# CLAUDE.md — RingLight Overlay

Windows desktop app: transparent click-through overlay windows simulating ring/softbox lights on secondary monitors. Full spec: `SPEC.md`.

## Environment
- **OS:** Windows 11 x64 | **Shell:** PowerShell 7 (`pwsh`)
- **Python:** 3.13.7 in `./venv` (spec asks 3.11+, fine)
- **Activate venv before ANY python/pip command:** `.\venv\Scripts\Activate.ps1`
- Prompt shows `(venv)` when active. If blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## Tool gotchas (learned this session)
- **Bash tool mangles Windows paths** — `.\venv\Scripts\activate` becomes `.venvScriptsactivate`. Use PowerShell tool for venv/pwsh commands.
- **PowerShell syntax:** `$null` not `/dev/null`, `$env:VAR` not `$VAR`, backtick `` ` `` for line continuation, `&&` works in pwsh 7.
- **Use context7** (`mcp__context7__*` or `npx ctx7`) for library docs before assuming API — training data lags.

## Stack
PySide6 6.11.1 (Qt6 GUI) · `keyboard` 0.13.5 (global hotkeys) · `ctypes` (Win32 `SetWindowLongPtrW` for click-through) · JSON in `%APPDATA%\RingLightOverlay\` · PyInstaller (one-folder `--windowed`) · pytest · black (line 100)

## Project layout (from SPEC §4 — not yet scaffolded)
```
ringlight_overlay/
  main.py · app.py
  core/        models.py · color.py · monitors.py · storage.py
  overlay/     overlay_window.py · overlay_manager.py · win32_helpers.py · shapes/{ring,circle,rectangle}.py
  ui/          main_window.py · tray.py · widgets/{light_editor,profile_list,color_picker}.py
  hotkeys/     manager.py
  resources/   icons/ · styles.qss
```

## Current state
- Files: `SPEC.md`, `CLAUDE.md`, `requirements.txt` (runtime), `requirements-dev.txt` (dev), `venv/`
- **No code yet.** Next: scaffold + `OverlayWindow` translucent click-through validated on Win10/11.

## Code conventions (SPEC §13)
- `from __future__ import annotations` top of every module · type hints everywhere
- `@dataclass(slots=True)` for models — no pydantic
- `pathlib.Path` not `os.path` · stdlib `logging` → `%APPDATA%\RingLightOverlay\app.log`
- Qt signals/slots for cross-component — no global state
- Modules ≤300 lines · docstrings only on public APIs
- **English everywhere** — code, identifiers, comments, commits, docs, **and all user-facing UI strings**. No Portuguese inside the app or in any artifact (plans, specs, README, etc.).

## Critical technical notes
- **Click-through (SPEC §7.1):** apply `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE` in `showEvent`, NOT `__init__` (HWND doesn't exist yet). Use `*Ptr*W` variants for 64-bit. Cast `winId()` to `int` before ctypes. `WA_TranslucentBackground` requires `FramelessWindowHint`.
- **keyboard lib:** callbacks run on its own thread → re-emit Qt signal with `Qt.QueuedConnection` before touching UI. `suppress=True` blocks hotkey from other apps (Windows only). May need Admin for some low-level hooks.
- **Qt tray:** check `QSystemTrayIcon.isSystemTrayAvailable()` first. `QApplication.setQuitOnLastWindowClosed(False)` mandatory — else app dies when settings window closes.
- **Known limit:** exclusive-fullscreen DirectX/Vulkan apps cannot be overlaid without API hooking — out of MVP scope. Borderless fullscreen works.

## Common commands (always activate venv first)
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt              # runtime only
pip install -r requirements-dev.txt          # dev (pyinstaller, pytest, black)
python -m ringlight_overlay                  # run (once scaffolded)
pytest                                       # tests
black .                                      # format
pyinstaller --noconfirm --windowed --name RingLightOverlay --icon resources/icons/app.ico --add-data "resources;resources" main.py
```

## Workflow rules (from user global CLAUDE.md)
- Plan non-trivial tasks in `tasks/todo.md` before coding · log error patterns in `tasks/lessons.md`
- Verify with real command output before claiming done · no `// TODO: fix later` · root-cause fixes only
- Trigger `project-update` skill after significant work
- **Numbered plans in `plans/`** — every new plan saves as `plans/plano_N.md` (N = next sequential integer). Another agent consumes these plans to generate code, so the file must be self-contained: context, files to touch, steps, verification criteria.
- **Always use Context7** — before writing code that uses PySide6, `keyboard`, ctypes Win32, PyInstaller or any external lib, query context7 (`mcp__context7__*` or `npx ctx7@latest`) for current docs. Do not trust training data for API signatures.
- **CLAUDE.md is always English** — all content in this file must be written in English, regardless of conversation language.

## Last 5 fixes
- S0 — scaffold + `python -m ringlight_overlay` entry point + logging baseline


## References
PySide6 docs: https://doc.qt.io/qtforpython-6/ · Qt window flags: https://doc.qt.io/qt-6/qt.html#WindowType-enum · keyboard lib: https://github.com/boppreh/keyboard
