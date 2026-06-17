from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw


def main() -> int:
    os.environ.setdefault("NO_ALBUMENTATIONS_UPDATE", "1")

    from pix2tex.cli import LatexOCR
    import pix2tex

    model = LatexOCR()

    image = Image.new("RGB", (220, 80), "white")
    draw = ImageDraw.Draw(image)
    draw.text((24, 24), "x^2 + epsilon", fill="black")
    result = str(model(image)).strip()

    if not result:
        raise RuntimeError("pix2tex returned an empty result while preparing the model cache.")

    model_dir = Path(pix2tex.__file__).resolve().parent / "model"
    required_files = [
        model_dir / "settings" / "config.yaml",
        model_dir / "checkpoints" / "weights.pth",
        model_dir / "checkpoints" / "image_resizer.pth",
        model_dir / "dataset" / "tokenizer.json",
    ]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise RuntimeError("pix2tex model files are missing:\n" + "\n".join(missing))

    print(f"Prepared pix2tex model directory: {model_dir}")
    print(f"Smoke result: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
