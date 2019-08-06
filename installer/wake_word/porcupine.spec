# -*- mode: python -*-
import os

block_cipher = None

venv = os.path.join(os.getcwd(), ".venv")
porcupine = os.path.join(os.getcwd(), "wake_word/porcupine")

a = Analysis(
    [os.path.join(os.getcwd(), "wake_word/porcupine/__main__.py")],
    pathex=["."],
    binaries=[],
    datas=[
        (
            os.path.join(
                porcupine, "porcupine_rhasspy/porcupine.py"
            ),
            ".",
        ),
        (os.path.join(porcupine, "lib"), "lib"),
        (os.path.join(porcupine, "resources"), "resources"),
    ],
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
    name="porcupine",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="porcupine"
)
