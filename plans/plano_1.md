# plano_1 — Sprint S0: Bootstrap

> **Executor:** Gemini. Read `GEMINI.md` (especially §3 workflow, §10 verification, §11 escalation, §12 forbidden) before starting. Run one checkbox at a time. TDD strictly.

## Goal

Produce a runnable empty `ringlight_overlay` package with the tooling baseline locked. After this sprint:

- `python -m ringlight_overlay` exits with code 0 and writes a startup line to `%APPDATA%\RingLightOverlay\app.log`.
- `pytest` reports at least one green test.
- `black --check .` reports no diff.

## Exit criteria (from `plans/roadmap.md` S0)

1. `python -m ringlight_overlay` opens & cleanly exits with code 0.
2. `pytest` runs at least one green test.
3. `black --check .` produces no diff.
4. `%APPDATA%\RingLightOverlay\app.log` exists and contains a startup INFO line.

## Context7 — mandatory lookups before Task 5

Before writing any PySide6 code (Task 7), run:

```powershell
npx ctx7@latest library "PySide6"
# Pick the /org/project id with highest snippet count and High source reputation.
npx ctx7@latest docs <libraryId> "QApplication lifecycle and setQuitOnLastWindowClosed"
```

Confirm the `QApplication` constructor signature and the `setQuitOnLastWindowClosed` semantics match what Task 7 codes. If the docs show a different signature, STOP and ask (escalation per GEMINI.md §11).

## Files in scope

- **Create:** `pyproject.toml`, `ringlight_overlay/__init__.py`, `ringlight_overlay/__main__.py`, `ringlight_overlay/app.py`, `tests/__init__.py`, `tests/conftest.py`, `tests/test_smoke.py`, `tasks/todo.md`, `tasks/lessons.md`.
- **Modify:** `.gitignore`.
- Touching any other file → escalate per GEMINI.md §11.

## Pre-flight

Activate venv at the start of the session and at the start of any new shell:

```powershell
.\venv\Scripts\Activate.ps1
```

Confirm `(venv)` appears in the prompt. Confirm `python --version` reports `3.13.7`.

Install dev deps once:

```powershell
pip install -r requirements-dev.txt
```

---

## Task 1 — Workflow files + .gitignore hygiene

**Files:**
- Create: `tasks/todo.md`, `tasks/lessons.md`
- Modify: `.gitignore`

- [x] **Step 1: Create `tasks/todo.md`** with exactly:

```markdown
# RingLight Overlay — Active TODO

_(empty — sprint S0 in progress)_
```

- [x] **Step 2: Create `tasks/lessons.md`** with exactly:

```markdown
# RingLight Overlay — Error patterns & lessons

_(empty)_
```

- [x] **Step 3: Append to `.gitignore`** (preserve existing lines, append the block below):

```gitignore

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.eggs/

# Build artifacts
dist/
build/

# Test / coverage
.pytest_cache/
.coverage
.coverage.*
htmlcov/

# AI workflow (local only)
tasks/
```

- [x] **Step 4: Commit**

```powershell
git add tasks .gitignore
git commit -m "chore: add tasks workflow files and python gitignore"
```

---

## Task 2 — `pyproject.toml`

**Files:** Create `pyproject.toml`.

- [x] **Step 1: Write `pyproject.toml`** with exactly this content:

```toml
[project]
name = "ringlight-overlay"
version = "0.0.1"
description = "Windows transparent overlay app simulating ring/softbox lights on secondary monitors."
requires-python = ">=3.13"

[tool.black]
line-length = 100
target-version = ["py313"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [x] **Step 2: Verify TOML parses**

```powershell
python -c "import tomllib, pathlib; tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8')); print('ok')"
```

Expected stdout: `ok`. Exit code 0.

- [x] **Step 3: Commit**

```powershell
git add pyproject.toml
git commit -m "chore: pin tooling config in pyproject.toml"
```

---

## Task 3 — Package skeleton

**Files:** Create `ringlight_overlay/__init__.py`.

- [x] **Step 1: Write `ringlight_overlay/__init__.py`** with exactly:

```python
from __future__ import annotations

__version__ = "0.0.1"
```

- [x] **Step 2: Verify importable**

```powershell
python -c "import ringlight_overlay; print(ringlight_overlay.__version__)"
```

Expected stdout: `0.0.1`. Exit code 0.

- [x] **Step 3: Commit**

```powershell
git add ringlight_overlay/__init__.py
git commit -m "feat: scaffold ringlight_overlay package"
```

---

## Task 4 — Smoke test (TDD red → green for `__version__`)

**Files:** Create `tests/__init__.py`, `tests/conftest.py`, `tests/test_smoke.py`.

- [x] **Step 1: Create `tests/__init__.py`** — empty file (zero bytes).

- [x] **Step 2: Create `tests/conftest.py`** with exactly:

```python
from __future__ import annotations

# Shared fixtures will live here as future sprints add them.
```

- [x] **Step 3: Create `tests/test_smoke.py`** with exactly:

```python
from __future__ import annotations

import ringlight_overlay


def test_version_is_set() -> None:
    assert ringlight_overlay.__version__ == "0.0.1"
```

- [x] **Step 4: Run pytest**

```powershell
pytest
```

Expected: `1 passed`. Exit code 0.

- [x] **Step 5: Commit**

```powershell
git add tests
git commit -m "test: add package smoke test"
```

---

## Task 5 — Context7 lookup gate (read-only)

- [x] **Step 1:** Run the Context7 commands from the "Context7 — mandatory lookups" section above. Read the result.

- [x] **Step 2:** Confirm the `QApplication` constructor accepts a `list[str]` (commonly `[]` or `sys.argv`), and that `setQuitOnLastWindowClosed(False)` is a method on the `QApplication` instance. If anything diverges from what Task 7 codes, STOP and escalate (GEMINI.md §11).

- [x] **Step 3:** No commit. This task produces no code.

---

## Task 6 — Failing test for the runnable entry point

**Files:** Modify `tests/test_smoke.py`.

- [x] **Step 1: Append to `tests/test_smoke.py`** so the file becomes exactly:

```python
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import ringlight_overlay


def test_version_is_set() -> None:
    assert ringlight_overlay.__version__ == "0.0.1"


def test_module_runs_and_writes_startup_log(tmp_path: Path) -> None:
    appdata = Path(os.environ["APPDATA"]) / "RingLightOverlay"
    log_path = appdata / "app.log"
    if log_path.exists():
        log_path.unlink()

    result = subprocess.run(
        [sys.executable, "-m", "ringlight_overlay"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert log_path.exists(), f"expected log at {log_path}"
    content = log_path.read_text(encoding="utf-8")
    assert "startup OK" in content, f"log content: {content!r}"
```

- [x] **Step 2: Run pytest — expect the new test to FAIL**

```powershell
pytest
```

Expected: `1 passed, 1 failed`. The failure must be in `test_module_runs_and_writes_startup_log` with a non-zero `returncode` (because the `__main__` / `app` modules do not exist yet).

- [x] **Step 3:** Do NOT commit. Proceed to Task 7.

---

## Task 7 — `app.py` + `__main__.py` (minimal implementation to make the test pass)

**Files:** Create `ringlight_overlay/app.py`, `ringlight_overlay/__main__.py`.

- [x] **Step 1: Create `ringlight_overlay/app.py`** with exactly:

```python
from __future__ import annotations

import logging
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def _log_dir() -> Path:
    base = os.environ.get("APPDATA")
    if not base:
        raise RuntimeError("APPDATA environment variable is required on Windows.")
    return Path(base) / "RingLightOverlay"


def _configure_logging() -> logging.Logger:
    log_dir = _log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Replace any pre-existing handlers so re-runs don't duplicate output.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(file_handler)

    return logging.getLogger("ringlight_overlay.app")


def main() -> int:
    """Bootstrap entry point used by `python -m ringlight_overlay`.

    S0 scope: initialize logging + QApplication and exit cleanly. The Qt event
    loop is intentionally NOT started here — that arrives in a later sprint
    (S4) when the system tray gives the app something to keep running for.
    """
    log = _configure_logging()
    log.info("startup OK")

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    log.info("shutdown OK")
    return 0
```

- [x] **Step 2: Create `ringlight_overlay/__main__.py`** with exactly:

```python
from __future__ import annotations

from ringlight_overlay.app import main

raise SystemExit(main())
```

- [x] **Step 3: Run the module manually**

```powershell
python -m ringlight_overlay
echo "exit=$LASTEXITCODE"
Get-Content "$env:APPDATA\RingLightOverlay\app.log" -Tail 3
```

Expected: `exit=0`, and the log tail shows a line ending in `startup OK` and a line ending in `shutdown OK`.

- [x] **Step 4: Run pytest — expect both tests green**

```powershell
pytest
```

Expected: `2 passed`. Exit code 0.

- [x] **Step 5: Commit**

```powershell
git add ringlight_overlay tests
git commit -m "feat: bootstrap app entry point with logging"
```

---

## Task 8 — Black format pass

- [x] **Step 1:** `black .`

- [x] **Step 2:** `black --check .`

Expected: `All done! ✨ 🍰 ✨` (or the no-emoji equivalent) and exit code 0 with no files needing reformat.

- [x] **Step 3:** If Step 1 modified any file, commit:

```powershell
git add -u
git commit -m "style: apply black"
```

If nothing changed, skip the commit.

---

## Task 9 — Sprint exit verification

- [x] **Step 1: Run every exit-criterion command and paste the real output into the sprint completion report.**

```powershell
python -m ringlight_overlay; echo "exit=$LASTEXITCODE"
pytest
black --check .
Test-Path "$env:APPDATA\RingLightOverlay\app.log"
Get-Content "$env:APPDATA\RingLightOverlay\app.log" -Tail 1
```

All four must succeed:
- `exit=0`
- `pytest` → `2 passed`
- `black --check .` → exit 0
- `Test-Path` → `True`, log tail line ends in `shutdown OK` or `startup OK`.

- [x] **Step 2: Append one line to the "Last 5 fixes" block in `CLAUDE.md`.** Drop the oldest if already at 5. New line:

```
- S0 — scaffold + `python -m ringlight_overlay` entry point + logging baseline
```

(This is the ONE exception to the "no editing CLAUDE.md" rule — only this single rolling block per GEMINI.md §3.)

- [x] **Step 3: Tick every `[ ]` in this file to `[x]`.** Update `tasks/todo.md`:

```markdown
# RingLight Overlay — Active TODO

- [x] S0 — Bootstrap (plano_1.md complete)
```

- [x] **Step 4: Final commit**

```powershell
git add CLAUDE.md plans/plano_1.md tasks/todo.md
git commit -m "chore: close sprint S0"
```

---

## Sprint complete when

- All four exit-criteria commands above pass.
- `tasks/todo.md` reflects S0 done.
- `tasks/lessons.md` has a dated entry for any gotcha you hit (see GEMINI.md §3). If nothing surprised you, leave it empty.
- All checkboxes in this file ticked.

When this is done, hand back to the planner for `plano_2.md` (Sprint S1 — Core layer). Do not start S1 on your own.
