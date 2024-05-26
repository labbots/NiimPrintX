# -*- mode: python ; coding: utf-8 -*-
import os

# Determine the current path and the source path for the CLI application
current_path = os.getcwd()
if os.path.basename(current_path) == "cli_app":
    src_path = os.path.join(current_path, '..', '..', 'NiimPrintX', 'cli')
elif os.path.basename(current_path) == "NiimPrintX":
    src_path = os.path.join(current_path, 'NiimPrintX', 'cli')
else:
    src_path = os.path.join(current_path, 'cli')

# Analysis step
a = Analysis(
    [os.path.join(src_path, '__main__.py')],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
    strip=True,
)

# PYZ step
pyz = PYZ(a.pure)

# EXE step
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='niimprintx',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have an icon
)

# COLLECT step for onefile build
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='niimprintx',
)

# BUNDLE step for creating onefile executable
app = BUNDLE(
    coll,
    name='niimprintx.exe',
    icon=None,  # Add path to .ico file if you have an icon
    onefile=True,  # Ensure the onefile mode is enabled
    console=True,
)
