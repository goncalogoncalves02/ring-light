# RingLight Overlay

Transparent click-through overlay windows that simulate ring lights and softboxes on your
secondary monitors — ideal for streaming, video calls, and photography.

## Screenshots

| Settings window | Overlay on monitor |
|---|---|
| ![Settings](docs/screenshots/settings.png) | ![Overlay](docs/screenshots/overlay.png) |

*(Screenshots captured during the Windows smoke test; added when available.)*

## Features

- Transparent, click-through overlay rings and shapes rendered on any connected monitor
- Per-profile light configuration: color temperature (Kelvin), size, brightness, feather
- Multiple profiles with instant switching from the system tray
- **Hotkey reconfiguration UI** — rebind any of the 6 global hotkeys via key capture with inline conflict detection
- **Import / export profiles** — share profiles as standalone JSON files; IDs are regenerated on import
- **First-run wizard** — guided monitor + shape + size setup on first launch
- **About dialog** — version, description, MIT license, and repository link (tray → About… or Settings → About)
- Global hotkeys that work while any other app has focus
- Debounced JSON config auto-save — settings persist across restarts
- Close-to-tray behavior; graceful shutdown with state flush
- Distributable one-folder build — no Python installation required on end-user machines

## Requirements

- Windows 11 x64 (Windows 10 may work; not officially tested)
- No Python installation needed when using the packaged build

## Run from source

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ringlight_overlay
```

## Build a standalone package

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pyinstaller --noconfirm RingLightOverlay.spec
# or use the helper script:
.\scripts\build.ps1
```

The output is in `dist\RingLightOverlay\`. Zip it for distribution or run
`RingLightOverlay.exe` directly. Target install size is under 130 MB (full PySide6 bundle).

A pre-built zip artifact is produced automatically by the [build workflow](.github/workflows/build.yml)
on every `v*` tag push and is downloadable from the GitHub Actions run page.

## Default hotkeys

| Action | Default shortcut |
|---|---|
| Toggle all lights on/off | `Ctrl+Alt+L` |
| Brightness up (+5%) | `Ctrl+Alt+Up` |
| Brightness down (−5%) | `Ctrl+Alt+Down` |
| Next profile | `Ctrl+Alt+Right` |
| Previous profile | `Ctrl+Alt+Left` |
| Show settings window | `Ctrl+Alt+S` |

Hotkeys fire globally — they work while any other application has focus.

Open **Settings → Hotkeys** tab to rebind any shortcut via key capture. Conflicts are flagged inline.

## Import / export profiles

Use the **Export Profile…** button in the Settings window to save the active profile as a JSON file.
Use **Import Profile…** to load a profile from a file — the profile is added with a fresh ID so it never
collides with existing ones.

## First-run wizard

On first launch a guided wizard appears: pick the target monitor, choose a shape and size, then click
Finish. The overlay is created in an **enabled** state on the chosen monitor. Cancel the wizard to skip
and start with the silent default "Daylight" profile instead.

## About

Tray menu → **About…** or Settings → **About** button opens the About dialog showing the app version,
description, MIT license notice, and a link to the repository.

## License

MIT License — see [LICENSE](LICENSE).
