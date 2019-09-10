# -*- mode: python -*-
import os

block_cipher = None

venv = os.path.join(os.getcwd(), ".venv")

a = Analysis(
    [os.path.join(os.getcwd(), "intent_recognition/fstrtext/fstrtext_train/__main__.py")],
    pathex=["."],
    binaries=[
        (os.path.join(venv, "bin/fasttext"), "."),
        (os.path.join(venv, "bin/fstprint-all"), "."),
        (
            os.path.join(
                venv,
                "lib/python3.6/site-packages/pywrapfst.cpython-36m-x86_64-linux-gnu.so",
            ),
            ".",
        ),
        (os.path.join(venv, "lib/libfstfarscript.so.13"), "."),
        (os.path.join(venv, "lib/libfstscript.so.13"), "."),
        (os.path.join(venv, "lib/libfstfar.so.13"), "."),
        (os.path.join(venv, "lib/libfst.so.13"), "."),
    ],
    datas=[],
    hiddenimports=["numbers"],
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
    name="fstrtext-train",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="fstrtext-train"
)
