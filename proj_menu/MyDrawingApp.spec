# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['menu_reg.py'],
    pathex=[],
    binaries=[],
    datas=[('style.qss', '.'), ('icon.png', '.'), ('gear.png', '.'), ('icon1.png', '.'), ('icon2.png', '.'), ('icon3.png', '.'), ('icon4.png', '.'), ('icon5.png', '.'), ('icon6.png', '.'), ('8.png', '.'), ('9.png', '.'), ('settings.ini', '.'), ('users.db', '.'), ('lang', 'lang')],
    hiddenimports=['db_main', 'common', 'grid_main', 'settings_qmenu', 'language_values', 'tray_icon', 'canvas', 'path_helper', 'sqlite3'],
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
    name='MyDrawingApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MyDrawingApp',
)
