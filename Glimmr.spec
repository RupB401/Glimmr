# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Path definitions
project_root = os.path.abspath('.')
src_path = os.path.join(project_root, 'src')
icon_path = os.path.join(project_root, 'Glimmr_App_Logo.ico')

# Collect all data files and hidden imports
datas = []
hidden_imports = []

# Add PyQt6 hidden imports
hidden_imports.extend([
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.QtNetwork',
    'requests',
    'json',
    'pathlib',
    'threading',
    'time'
])

# Add config.json if it exists
config_path = os.path.join(project_root, 'config.json')
if os.path.exists(config_path):
    datas.append((config_path, '.'))

# Add GIFs folder if it exists
gifs_path = os.path.join(project_root, 'Gifs')
if os.path.exists(gifs_path):
    for root, dirs, files in os.walk(gifs_path):
        for file in files:
            if file.lower().endswith('.gif'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_root)
                dest_dir = os.path.dirname(rel_path)
                datas.append((file_path, dest_dir))

a = Analysis(
    [os.path.join(src_path, 'main.py')],
    pathex=[project_root, src_path],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Glimmr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,  # Custom icon
)
