# -*- mode: python ; coding: utf-8 -*-


# block_cipher = pyi_crypto.PyiBlockCipher(key='477b9a1dc5f7372d8140459626bd1bf3')

SETUP_DIR = ''

a = Analysis(
    ['Security_window.py',
    'Security_Firmware_Window.py',
    'Write2MySQL_update2.py',
    'HTTP_MES.py',
    'Pass_station_Win.py',
    'Sequence_Window_Security.py',
    'Setting_Window_Security.py',
    'Serial_Security.py',
    SETUP_DIR+'UI\\connect_setting_Security.py',
    SETUP_DIR+'UI\\firmware_setting_Security.py',
    SETUP_DIR+'UI\\Security_win.py',
    SETUP_DIR+'UI\\Pass_station_Security.py'
    ],
    pathex=[SETUP_DIR[:-2]],
    binaries=[],
    datas=[
    (SETUP_DIR+'Picture','Picture'),
    (SETUP_DIR+'file.json','.'),
    (SETUP_DIR+'1.json','.'),
    (SETUP_DIR+'config_Security.ini','.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Security',
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
    icon=SETUP_DIR+'Picture\\logo.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Security',
)
