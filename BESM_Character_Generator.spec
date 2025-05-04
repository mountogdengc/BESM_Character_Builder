# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['besm_app.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\data', 'data'), ('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\style.qss', '.'), ('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\project-logo.jpg', '.'), ('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\dialogs', 'dialogs'), ('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\tools', 'tools'), ('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\tabs', 'tabs'), ('C:\\Users\\david\\OneDrive\\Desktop\\Apps\\Legendmasters_Character_Generator-old\\templates', 'templates')],
    hiddenimports=['PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'reportlab'],
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
    a.binaries,
    a.datas,
    [],
    name='BESM_Character_Generator',
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
    icon=['project-logo.jpg'],
)
