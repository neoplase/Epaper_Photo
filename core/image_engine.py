"""
image_engine.py - High-efficiency image processing, color enhancement, and e-paper dithering engine.
Optimized for low RAM and CPU usage on Raspberry Pi Zero (ARMv6 & ARMv8).
"""

import logging
from typing import Tuple, Optional
from PIL import Image, ImageEnhance, ImageOps

logger = logging.getLogger("epaper.image_engine")

# Defined E-Paper Color Palettes
PALETTE_7COLOR = [
    0, 0, 0,        # Black
    255, 255, 255,  # White
    0, 160, 50,     # Green
    0, 60, 200,     # Blue
    220, 25, 25,    # Red
    255, 225, 0,    # Yellow
    255, 120, 0     # Orange
]

PALETTE_BWR = [
    0, 0, 0,        # Black
    255, 255, 255,  # White
    220, 20, 20     # Red
]

PALETTE_BWY = [
    0, 0, 0,        # Black
    255, 255, 255,  # White
    255, 220, 0     # Yellow
]

def _create_palette_image(rgb_list: list) -> Image.Image:
    """Creates an indexed 8-bit palette image for Pillow quantization."""
    pal_img = Image.new("P", (1, 1))
    full_palette = rgb_list + [0] * (768 - len(rgb_list))
    pal_img.putpalette(full_palette)
    return pal_img

# Pre-created palette images
_PAL_IMG_7COLOR = _create_palette_image(PALETTE_7COLOR)
_PAL_IMG_BWR = _create_palette_image(PALETTE_BWR)
_PAL_IMG_BWY = _create_palette_image(PALETTE_BWY)

# 16-level grayscale palette
_GRAY16_LIST = []
for i in range(16):
    val = int(i * 255 / 15)
    _GRAY16_LIST.extend([val, val, val])
_PAL_IMG_GRAY16 = _create_palette_image(_GRAY16_LIST)

def enhance_colors(image: Image.Image, saturation: float = 1.3, contrast: float = 1.15, brightness: float = 1.05) -> Image.Image:
    """
    Applies saturation, contrast, and brightness boosts calibrated for reflective e-paper pigments.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(brightness)

    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)

    if saturation != 1.0:
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation)

    return image

def crop_and_resize(
    image: Image.Image,
    target_width: int,
    target_height: int,
    fit_mode: str = "cover",
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> Image.Image:
    """
    Resizes and fits image to target dimensions.
    - crop_box: (x, y, w, h) in original image coordinates if provided from web UI.
    - fit_mode: 'cover' (fills entire screen, cropping edges), 'contain' (letterbox), 'stretch'.
    """
    # 1. Apply user crop box if supplied
    if crop_box:
        x, y, w, h = crop_box
        image = image.crop((x, y, x + w, y + h))

    orig_w, orig_h = image.size

    # 2. Stretch mode
    if fit_mode == "stretch":
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # 3. Contain mode (letterbox)
    if fit_mode == "contain":
        scale = min(target_width / orig_w, target_height / orig_h)
        new_w = max(1, int(orig_w * scale))
        new_h = max(1, int(orig_h * scale))
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (target_width, target_height), (255, 255, 255))
        offset_x = (target_width - new_w) // 2
        offset_y = (target_height - new_h) // 2
        canvas.paste(resized, (offset_x, offset_y))
        return canvas

    # 4. Cover mode (default: center crop to fill exact aspect ratio)
    target_ratio = target_width / target_height
    orig_ratio = orig_w / orig_h

    if orig_ratio > target_ratio:
        # Source is wider: crop left and right
        crop_w = int(orig_h * target_ratio)
        offset_x = (orig_w - crop_w) // 2
        image = image.crop((offset_x, 0, offset_x + crop_w, orig_h))
    else:
        # Source is taller: crop top and bottom
        crop_h = int(orig_w / target_ratio)
        offset_y = (orig_h - crop_h) // 2
        image = image.crop((0, offset_y, orig_w, offset_y + crop_h))

    return image.resize((target_width, target_height), Image.Resampling.LANCZOS)

def dither_for_palette(image: Image.Image, palette_type: str) -> Image.Image:
    """
    Dithers the image using Floyd-Steinberg quantization according to the e-paper pigment profile.
    Returns RGB image suitable for display driver.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")

    dither_flag = Image.Dither.FLOYDSTEINBERG

    if palette_type == "7color":
        # ACeP / Spectra 6 7-color quantization
        quantized = image.quantize(palette=_PAL_IMG_7COLOR, dither=dither_flag)
        return quantized.convert("RGB")

    elif palette_type == "bwr":
        # 3-color (Black, White, Red)
        quantized = image.quantize(palette=_PAL_IMG_BWR, dither=dither_flag)
        return quantized.convert("RGB")

    elif palette_type == "bwy":
        # 3-color (Black, White, Yellow)
        quantized = image.quantize(palette=_PAL_IMG_BWY, dither=dither_flag)
        return quantized.convert("RGB")

    elif palette_type == "grayscale16":
        # 16-level grayscale
        gray = image.convert("L")
        quantized = gray.quantize(palette=_PAL_IMG_GRAY16, dither=dither_flag)
        return quantized.convert("RGB")

    elif palette_type == "mono":
        # Pure 1-bit Monochrome (Black & White)
        gray = image.convert("L")
        mono = gray.convert("1", dither=dither_flag)
        return mono.convert("RGB")

    # Fallback: return image as RGB
    return image

def process_image(
    input_image: Image.Image,
    target_width: int,
    target_height: int,
    palette_type: str = "7color",
    saturation: float = 1.3,
    contrast: float = 1.15,
    brightness: float = 1.05,
    fit_mode: str = "cover",
    crop_box: Optional[Tuple[int, int, int, int]] = None
) -> Image.Image:
    """
    Full processing pipeline:
    1. Framing (Crop & Resize to exact screen dimensions)
    2. Color & contrast boost for e-paper reflective pigments
    3. Floyd-Steinberg error diffusion quantization
    """
    # Step 1: Crop and resize to target screen dimensions
    framed = crop_and_resize(input_image, target_width, target_height, fit_mode, crop_box)

    # Step 2: Color and contrast enhancement
    enhanced = enhance_colors(framed, saturation=saturation, contrast=contrast, brightness=brightness)

    # Step 3: Hardware-specific dithering
    dithered = dither_for_palette(enhanced, palette_type=palette_type)

    return dithered
