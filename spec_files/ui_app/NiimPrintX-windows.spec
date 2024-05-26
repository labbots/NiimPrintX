# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess

# Function to collect files and adjust their target directory
def collect_and_adjust_files(base_path, target_dir):
    collected_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            full_path = os.path.join(root, file)
            # We only need the relative path without the filename
            rel_path = os.path.relpath(root, base_path)
            target_path = os.path.join(target_dir, rel_path)
            collected_files.append((full_path, target_path))
    return collected_files

# Path to the extracted ImageMagick directory
imagemagick_path = os.path.abspath('./resources/ImageMagick')

# Collect the ImageMagick binaries and libraries and specify the target directory
datas = collect_and_adjust_files(imagemagick_path, 'imagemagick')

current_path = os.getcwd()
if os.path.basename(current_path) == "ui_app":
    src_path = os.path.join(current_path, '..', '..', 'NiimPrintX', 'ui')
    hook_path = os.path.join(current_path,'..', '..', 'runtime_hooks', 'windows')
if os.path.basename(current_path) == "NiimPrintX":
    src_path = os.path.join(current_path, 'NiimPrintX', 'ui')
    hook_path = os.path.join(current_path, 'runtime_hooks', 'windows')

# Add custom assets
datas += [
    (os.path.join(src_path, 'icons'), 'NiimPrintX/ui/icons'),
    (os.path.join(src_path, 'assets'), 'NiimPrintX/ui/assets')
]


a = Analysis(
    [os.path.join(src_path, '__main__.py')],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=['tkinter'],
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
    [],
    exclude_binaries=True,
    name='NiimPrintX',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for a GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(src_path, 'assets', 'icon.ico'),  # Use .ico for Windows
    onefile=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NiimPrintX',
)

app = BUNDLE(
    coll,
    name='NiimPrintX',
    icon=os.path.join(src_path, 'assets', 'icon.ico'),  # Use .ico for Windows
    bundle_identifier=None,
)
