# -*- mode: python -*-
import os

block_cipher = None

venv = os.path.join(os.getcwd(), ".venv")

a = Analysis(
    [os.path.join(os.getcwd(), "installer/intent_recognition/fsticuffs.py")],
    pathex=["."],
    binaries=[
        (
            os.path.join(venv, "lib/python3.6/site-packages/pywrapfst.cpython-36m-x86_64-linux-gnu.so"),
            ".",
        ),
        (os.path.join(venv, "lib/libfstfarscript.so.13"), "."),
        (os.path.join(venv, "lib/libfstscript.so.13"), "."),
        (os.path.join(venv, "lib/libfstfar.so.13"), "."),
        (os.path.join(venv, "lib/libfst.so.13"), "."),
    ],
    datas=[],
    hiddenimports=["fsticuffs", "numbers", "jsgf2fst"],
    hookspath=[],
    runtime_hooks=[],
    excludes=["pywrapfst"],
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
    name="fsticuffs",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="fsticuffs"
)
