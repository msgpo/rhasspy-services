# -*- mode: python -*-
import os
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

venv = os.path.join(os.getcwd(), ".venv")

a = Analysis(
    [os.path.join(os.getcwd(), "voice_command/webrtcvad/__main__.py")],
    pathex=["."],
    binaries=[
        (
            os.path.join(
                venv,
                "lib/python3.6/site-packages/_webrtcvad.cpython-36m-x86_64-linux-gnu.so",
            ),
            ".",
        )
    ],
    datas=copy_metadata("webrtcvad"),
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="webrtcvad",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="webrtcvad"
)
