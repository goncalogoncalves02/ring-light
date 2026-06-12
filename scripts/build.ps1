# scripts/build.ps1 — Build RingLight Overlay with PyInstaller.
# Run from the repo root in a Windows PowerShell with the venv activated.
#
# Usage:
#   .\venv\Scripts\Activate.ps1
#   .\scripts\build.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Activating virtual environment..."
& "$PSScriptRoot\..\venv\Scripts\Activate.ps1"

Write-Host "Running PyInstaller..."
pyinstaller --noconfirm RingLightOverlay.spec

$distDir = Join-Path $PSScriptRoot "..\dist\RingLightOverlay"
if (Test-Path $distDir) {
    $sizeMb = [math]::Round(
        (Get-ChildItem -Recurse -Force $distDir | Measure-Object -Property Length -Sum).Sum / 1MB,
        1
    )
    Write-Host "dist/RingLightOverlay size: $sizeMb MB"
    if ($sizeMb -ge 130) {
        Write-Warning "Size exceeds the 130 MB target ($sizeMb MB). Consider excluding unused Qt modules."
    } else {
        Write-Host "Size is within the 130 MB limit."
    }
} else {
    Write-Error "dist/RingLightOverlay not found — PyInstaller may have failed."
}
