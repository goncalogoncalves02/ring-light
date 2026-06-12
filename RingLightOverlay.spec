# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for RingLight Overlay — one-folder, windowed build.
# Build with:  pyinstaller --noconfirm RingLightOverlay.spec

a = Analysis(
    ['ringlight_overlay/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ringlight_overlay/resources', 'ringlight_overlay/resources'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='RingLightOverlay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ringlight_overlay/resources/icons/favicon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='RingLightOverlay',
)
