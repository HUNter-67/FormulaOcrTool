from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path


def _status(name: str, ok: bool, detail: str = "") -> None:
    mark = "OK" if ok else "FAIL"
    line = f"[{mark}] {name}"
    if detail:
        line += f": {detail}"
    print(line)


def _has_module(module: str) -> bool:
    return importlib.util.find_spec(module) is not None


def main() -> int:
    print("== 本地公式识别工具：环境检查 ==")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Executable: {sys.executable}")
    print(f"Working dir: {Path.cwd()}")
    print("")

    ok = True

    for module in ("PySide6", "PIL", "pix2tex", "matplotlib"):
        present = _has_module(module)
        _status(module, present)
        ok = ok and present

    if _has_module("torch"):
        import torch

        cuda_ok = torch.cuda.is_available()
        cuda_detail = "available" if cuda_ok else "not available; will use CPU"
        if cuda_ok:
            try:
                cuda_detail += f", device={torch.cuda.get_device_name(0)}"
            except Exception:
                pass
        _status("torch", True, f"{torch.__version__}, CUDA {cuda_detail}")
    else:
        _status("torch", False, "not installed")
        ok = False

    cache_candidates = [
        Path.cwd() / "build_assets" / "hf_home",
        Path.home() / ".cache" / "pix2tex",
        Path.home() / ".pix2tex",
        Path(os.environ.get("LOCALAPPDATA", "")) / "pix2tex",
        Path(os.environ.get("USERPROFILE", "")) / ".cache" / "huggingface",
    ]
    existing = [str(path) for path in cache_candidates if path.exists()]
    if existing:
        _status("model/cache", True, "; ".join(existing))
    else:
        _status("model/cache", False, "not found yet; first recognition may download model")

    print("")
    if ok:
        print("基础依赖可用。可以运行 run.bat 启动工具。")
        return 0

    print("依赖不完整。请先运行 setup_env.ps1。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
