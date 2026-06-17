from __future__ import annotations

from PIL import Image, ImageChops, ImageEnhance, ImageOps


def preprocess_formula_image(image: Image.Image) -> Image.Image:
    """Prepare a white-background formula crop for pix2tex."""
    return preprocess_formula_variants(image)[0]


def preprocess_formula_variants(image: Image.Image) -> list[Image.Image]:
    """Return several safe variants; tiny Greek glyphs often benefit from this."""
    image = image.convert("RGB")
    image = _trim_white_margin(image)

    gray = ImageOps.grayscale(image)
    normal = ImageOps.autocontrast(ImageEnhance.Contrast(gray).enhance(1.8)).convert("RGB")
    strong = ImageOps.autocontrast(ImageEnhance.Contrast(gray).enhance(2.4)).convert("RGB")
    binary = gray.point(lambda value: 0 if value < 185 else 255, mode="1").convert("RGB")

    return [_resize_for_ocr(variant) for variant in (normal, _scale_if_small(strong), binary)]


def _scale_if_small(image: Image.Image) -> Image.Image:
    width, height = image.size
    if max(width, height) >= 600:
        return image
    return image.resize((width * 2, height * 2), Image.Resampling.LANCZOS)


def _resize_for_ocr(image: Image.Image) -> Image.Image:
    max_side = 1600
    width, height = image.size
    longest = max(width, height)
    if longest <= max_side:
        return image

    ratio = max_side / longest
    return image.resize((int(width * ratio), int(height * ratio)), Image.Resampling.LANCZOS)


def _trim_white_margin(image: Image.Image) -> Image.Image:
    bg = Image.new(image.mode, image.size, (255, 255, 255))
    diff = ImageChops.difference(image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -20)
    bbox = diff.getbbox()
    if not bbox:
        return image

    left, top, right, bottom = bbox
    pad = 12
    left = max(left - pad, 0)
    top = max(top - pad, 0)
    right = min(right + pad, image.width)
    bottom = min(bottom + pad, image.height)
    return image.crop((left, top, right, bottom))
