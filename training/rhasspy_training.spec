# -*- mode: python -*-

block_cipher = None


a = Analysis(
    ["rhasspy_training/__main__.py"],
    pathex=["."],
    binaries=[
        (
            ".venv/lib/python3.6/site-packages/pywrapfst.cpython-36m-x86_64-linux-gnu.so",
            ".",
        ),
        (".venv/lib/libfstfarscript.so.13", "."),
        (".venv/lib/libfstscript.so.13", "."),
        (".venv/lib/libfst.so.13", "."),
        (".venv/lib/libngramhist.so.134", "."),
        (".venv/lib/libngram.so.134", "."),
        (".venv/bin/fstminimize", "."),
        (".venv/lib/libsphinxbase.so.3", "."),
        (".venv/bin/sphinx_jsgf2fsg", "."),
        (".venv/bin/phonetisaurus-apply", "."),
    ],
    datas=[],
    hiddenimports=[],
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
    name="rhasspy_training",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="rhasspy_training"
)
