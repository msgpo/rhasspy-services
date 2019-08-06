# -*- mode: python -*-
import os

block_cipher = None

venv = os.path.join(os.getcwd(), ".venv")

a = Analysis(
    [os.path.join(os.getcwd(), "installer/training/vocab_g2p.py")],
    pathex=["."],
    binaries=[
        (os.path.join(venv, "lib/libfst.so.13"), "."),
        (os.path.join(venv, "bin/phonetisaurus-apply"), "."),
    ],
    datas=[],
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
    name="vocab_g2p",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="vocab_g2p"
)
