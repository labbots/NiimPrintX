# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

current_path = os.getcwd()
if os.path.basename(current_path) == "ui_app":
    src_path = os.path.join(current_path, '..', '..', 'NiimPrintX', 'ui')
if os.path.basename(current_path) == "NiimPrintX":
    src_path = os.path.join(current_path, 'NiimPrintX', 'ui')

# Add custom assets
datas = [
    (os.path.join(src_path, 'icons'), 'NiimPrintX/ui/icons'),
    (os.path.join(src_path, 'assets'), 'NiimPrintX/ui/assets')
]

# Include all submodules from PIL and tkinter
hidden_imports = collect_submodules('PIL')
hidden_imports += collect_submodules('tkinter')

tcl_library = os.environ.get('TCL_LIBRARY', '/usr/share/tcltk/tcl8.6')
tk_library = os.environ.get('TK_LIBRARY', '/usr/share/tcltk/tk8.6')

datas += [
    (tcl_library, 'tcl'),
    (tk_library, 'tk')
]

a = Analysis(
    [os.path.join(src_path, '__main__.py')],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='NiimPrintX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(src_path, 'assets', 'icon.ico'),
)
