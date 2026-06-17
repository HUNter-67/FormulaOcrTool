# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

import importlib.util

from PyInstaller.utils.hooks import collect_all, collect_submodules


block_cipher = None
project_root = Path.cwd()


def tree_datas(source: Path, dest: str):
    if not source.exists():
        return []

    datas = []
    for path in source.rglob("*"):
        if path.is_file():
            target_dir = Path(dest) / path.parent.relative_to(source)
            datas.append((str(path), str(target_dir)))
    return datas


datas = []
binaries = []
hiddenimports = []

pix2tex_spec = importlib.util.find_spec("pix2tex")
if pix2tex_spec and pix2tex_spec.origin:
    pix2tex_root = Path(pix2tex_spec.origin).resolve().parent
    datas += tree_datas(pix2tex_root / "model", "pix2tex/model")

for package in (
    "pix2tex",
    "transformers",
    "tokenizers",
    "torch",
    "torchvision",
    "PIL",
    "matplotlib",
):
    package_datas, package_binaries, package_hiddenimports = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

hiddenimports += collect_submodules("app")
hiddenimports += [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
]


a = Analysis(
    ["app/main.py"],
    pathex=[str(project_root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "IPython",
        "jupyter",
        "notebook",
        "tkinter",
        "pytest",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="FormulaOcrTool",
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
)
