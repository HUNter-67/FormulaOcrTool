from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from app.image_preprocess import preprocess_formula_variants
from app.latex_postprocess import normalize_latex_output, score_latex_candidate


@dataclass
class RecognitionResult:
    latex: str
    image: Image.Image


class FormulaRecognizer:
    def __init__(self) -> None:
        self._model = None

    def load(self, offline: bool = False) -> None:
        if self._model is not None:
            return

        if offline:
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            os.environ.setdefault("HF_HUB_OFFLINE", "1")

        try:
            from pix2tex.cli import LatexOCR
        except Exception as exc:
            raise RuntimeError(
                "pix2tex 未安装或无法导入。请先运行 setup_env.ps1，或重新打包 exe。"
            ) from exc

        try:
            self._model = LatexOCR()
        except Exception as exc:
            if offline:
                raise RuntimeError(
                    "离线模式下没有找到可用的 pix2tex 模型缓存。"
                    "请重新运行 build_exe.ps1，让脚本先下载并打包模型。"
                ) from exc
            raise RuntimeError(
                "模型加载失败。首次源码运行需要联网下载 pix2tex 模型。"
            ) from exc

    def recognize_path(self, path: str | Path, offline: bool = False) -> RecognitionResult:
        image = Image.open(path)
        return self.recognize_image(image, offline=offline)

    def recognize_image(self, image: Image.Image, offline: bool = False) -> RecognitionResult:
        variants = preprocess_formula_variants(image)
        prepared = variants[0]
        self.load(offline=offline)
        assert self._model is not None

        candidates: list[str] = []
        try:
            for variant in variants:
                latex = normalize_latex_output(str(self._model(variant)))
                if latex and latex not in candidates:
                    candidates.append(latex)
        except RuntimeError as exc:
            message = str(exc).lower()
            if "cuda" in message or "out of memory" in message:
                raise RuntimeError(
                    "GPU 显存不足或 CUDA 推理失败。请关闭占用显卡的软件后重试，"
                    "或改用 CPU 版 PyTorch。"
                ) from exc
            raise

        latex = max(candidates, key=score_latex_candidate) if candidates else ""
        return RecognitionResult(latex=latex, image=prepared)
