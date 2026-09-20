"""
screen_catalog.py - Universal Screen Registry for all Pimoroni and Waveshare E-Paper displays.
"""

from typing import Dict, Any, List, Optional

# Palette types:
# - '7color': Black, White, Green, Blue, Red, Yellow, Orange (ACeP / Spectra 6)
# - 'bwr': Black, White, Red (3-color)
# - 'bwy': Black, White, Yellow (3-color)
# - 'grayscale16': 16 levels of gray (IT8951 and large grayscale panels)
# - 'mono': 2 levels (Black & White)

SCREEN_CATALOG: Dict[str, Dict[str, Any]] = {
    # ==========================================
    # VIRTUAL / MOCK DISPLAY
    # ==========================================
    "mock_7_3": {
        "id": "mock_7_3",
        "brand": "Virtual",
        "model_name": "Virtual 7.3\" Color (Dev Mode)",
        "width": 800,
        "height": 480,
        "palette_type": "7color",
        "colors_desc": "7-Color (ACeP / Spectra 6 Simulation)",
        "driver_type": "mock",
        "driver_module": "mock_driver",
        "size_category": "large",
        "notes": "Generates real-time preview image file (data/current_display.png) for testing without physical screen."
    },
    "mock_13_3": {
        "id": "mock_13_3",
        "brand": "Virtual",
        "model_name": "Virtual 13.3\" Grayscale (Dev Mode)",
        "width": 1600,
        "height": 1200,
        "palette_type": "grayscale16",
        "colors_desc": "16-level Grayscale Simulation",
        "driver_type": "mock",
        "driver_module": "mock_driver",
        "size_category": "large",
        "notes": "1600x1200 high-resolution virtual screen for testing large-format grayscale."
    },

    # ==========================================
    # PIMORONI INKY SERIES
    # ==========================================
    "inky_impression_7_3": {
        "id": "inky_impression_7_3",
        "brand": "Pimoroni",
        "model_name": "Inky Impression 7.3\" (7-Color)",
        "width": 800,
        "height": 480,
        "palette_type": "7color",
        "colors_desc": "7-Color ACeP (Black, White, Green, Blue, Red, Yellow, Orange)",
        "driver_type": "inky",
        "driver_module": "inky_7_3",
        "size_category": "large",
        "notes": "Pimoroni 7.3\" 7-colour e-paper HAT with I2C EEPROM and SPI interface."
    },
    "inky_impression_5_7": {
        "id": "inky_impression_5_7",
        "brand": "Pimoroni",
        "model_name": "Inky Impression 5.7\" (7-Color)",
        "width": 600,
        "height": 448,
        "palette_type": "7color",
        "colors_desc": "7-Color ACeP",
        "driver_type": "inky",
        "driver_module": "inky_5_7",
        "size_category": "medium",
        "notes": "Pimoroni 5.7\" 7-colour e-paper display HAT."
    },
    "inky_impression_4_0": {
        "id": "inky_impression_4_0",
        "brand": "Pimoroni",
        "model_name": "Inky Impression 4.0\" (7-Color)",
        "width": 640,
        "height": 400,
        "palette_type": "7color",
        "colors_desc": "7-Color ACeP",
        "driver_type": "inky",
        "driver_module": "inky_4_0",
        "size_category": "medium",
        "notes": "Pimoroni 4.0\" 7-colour e-paper display HAT."
    },
    "inky_what_bwr": {
        "id": "inky_what_bwr",
        "brand": "Pimoroni",
        "model_name": "Inky wHAT 4.2\" (Red/Black/White)",
        "width": 400,
        "height": 300,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "inky",
        "driver_module": "inky_what_red",
        "size_category": "medium",
        "notes": "400x300 e-paper HAT with vivid red highlights."
    },
    "inky_what_bwy": {
        "id": "inky_what_bwy",
        "brand": "Pimoroni",
        "model_name": "Inky wHAT 4.2\" (Yellow/Black/White)",
        "width": 400,
        "height": 300,
        "palette_type": "bwy",
        "colors_desc": "3-Color (Black, White, Yellow)",
        "driver_type": "inky",
        "driver_module": "inky_what_yellow",
        "size_category": "medium",
        "notes": "400x300 e-paper HAT with yellow highlights."
    },
    "inky_what_mono": {
        "id": "inky_what_mono",
        "brand": "Pimoroni",
        "model_name": "Inky wHAT 4.2\" (Black/White)",
        "width": 400,
        "height": 300,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "inky",
        "driver_module": "inky_what_mono",
        "size_category": "medium",
        "notes": "400x300 high contrast monochrome display."
    },
    "inky_phat_bwr": {
        "id": "inky_phat_bwr",
        "brand": "Pimoroni",
        "model_name": "Inky pHAT 2.13\" (Red/Black/White)",
        "width": 250,
        "height": 122,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "inky",
        "driver_module": "inky_phat_red",
        "size_category": "small",
        "notes": "Compact pHAT format for Raspberry Pi Zero."
    },
    "inky_phat_bwy": {
        "id": "inky_phat_bwy",
        "brand": "Pimoroni",
        "model_name": "Inky pHAT 2.13\" (Yellow/Black/White)",
        "width": 250,
        "height": 122,
        "palette_type": "bwy",
        "colors_desc": "3-Color (Black, White, Yellow)",
        "driver_type": "inky",
        "driver_module": "inky_phat_yellow",
        "size_category": "small",
        "notes": "Compact pHAT format for Raspberry Pi Zero with yellow accent."
    },
    "inky_phat_mono": {
        "id": "inky_phat_mono",
        "brand": "Pimoroni",
        "model_name": "Inky pHAT 2.13\" (Black/White)",
        "width": 250,
        "height": 122,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "inky",
        "driver_module": "inky_phat_mono",
        "size_category": "small",
        "notes": "Compact pHAT format for Raspberry Pi Zero monochrome."
    },

    # ==========================================
    # WAVESHARE LARGE PANELS (13.3", 10.3", 9.7")
    # ==========================================
    "waveshare_13_3_k": {
        "id": "waveshare_13_3_k",
        "brand": "Waveshare",
        "model_name": "Waveshare 13.3\" (1600x1200 IT8951)",
        "width": 1600,
        "height": 1200,
        "palette_type": "grayscale16",
        "colors_desc": "16-level Grayscale / High-Res",
        "driver_type": "waveshare",
        "driver_module": "epd13in3k",
        "size_category": "large",
        "notes": "13.3-inch large e-paper display with IT8951 controller driver HAT via SPI."
    },
    "waveshare_10_3": {
        "id": "waveshare_10_3",
        "brand": "Waveshare",
        "model_name": "Waveshare 10.3\" (1872x1404 IT8951)",
        "width": 1872,
        "height": 1404,
        "palette_type": "grayscale16",
        "colors_desc": "16-level Grayscale",
        "driver_type": "waveshare",
        "driver_module": "epd10in3",
        "size_category": "large",
        "notes": "10.3-inch ultra high resolution e-paper with IT8951 driver."
    },
    "waveshare_9_7": {
        "id": "waveshare_9_7",
        "brand": "Waveshare",
        "model_name": "Waveshare 9.7\" (1200x825 IT8951)",
        "width": 1200,
        "height": 825,
        "palette_type": "grayscale16",
        "colors_desc": "16-level Grayscale",
        "driver_type": "waveshare",
        "driver_module": "epd9in7",
        "size_category": "large",
        "notes": "9.7-inch e-paper display with IT8951 driver."
    },

    # ==========================================
    # WAVESHARE 7.X" PANELS
    # ==========================================
    "waveshare_7_3_spectra6": {
        "id": "waveshare_7_3_spectra6",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.3\" Spectra 6 Color",
        "width": 800,
        "height": 480,
        "palette_type": "spectra6",
        "colors_desc": "Spectra 6 (Black, White, Yellow, Red, Blue, Green)",
        "driver_type": "waveshare",
        "driver_module": "epd7in3e",
        "size_category": "large",
        "notes": "Waveshare 7.3inch E-Ink Spectra 6 6-color display (uses epd7in3e driver)."
    },
    "waveshare_7_3_e": {
        "id": "waveshare_7_3_e",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.3\" (E) Spectra 6 Color",
        "width": 800,
        "height": 480,
        "palette_type": "spectra6",
        "colors_desc": "Spectra 6 (Black, White, Yellow, Red, Blue, Green)",
        "driver_type": "waveshare",
        "driver_module": "epd7in3e",
        "size_category": "large",
        "notes": "Waveshare 7.3inch e-Paper (E), E-Ink Spectra 6 6-color display."
    },
    "waveshare_7_3_f": {
        "id": "waveshare_7_3_f",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.3\" (F) 7-Color ACeP",
        "width": 800,
        "height": 480,
        "palette_type": "7color",
        "colors_desc": "7-Color (Black, White, Green, Blue, Red, Yellow, Orange)",
        "driver_type": "waveshare",
        "driver_module": "epd7in3f",
        "size_category": "large",
        "notes": "Waveshare 7.3inch e-Paper (F), 800x480 ACeP 7-color e-Paper HAT."
    },
    "waveshare_7_3_g": {
        "id": "waveshare_7_3_g",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.3\" (G) 4-Color (Red/Yellow/Black/White)",
        "width": 800,
        "height": 480,
        "palette_type": "4color",
        "colors_desc": "4-Color (Black, White, Yellow, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd7in3g",
        "size_category": "large",
        "notes": "Waveshare 7.3inch e-Paper (G), 800x480 4-color display (uses epd7in3g driver)."
    },
    "waveshare_7_5_v2": {
        "id": "waveshare_7_5_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.5\" V2 (Black/White)",
        "width": 800,
        "height": 480,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd7in5_V2",
        "size_category": "large",
        "notes": "Standard Waveshare 7.5inch e-Paper HAT V2."
    },
    "waveshare_7_5_b_v2": {
        "id": "waveshare_7_5_b_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.5\" (B) V2 (Red/Black/White)",
        "width": 800,
        "height": 480,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd7in5b_V2",
        "size_category": "large",
        "notes": "Waveshare 7.5inch 3-color e-Paper HAT (B) V2."
    },
    "waveshare_7_5_c": {
        "id": "waveshare_7_5_c",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.5\" (C) (Yellow/Black/White)",
        "width": 640,
        "height": 384,
        "palette_type": "bwy",
        "colors_desc": "3-Color (Black, White, Yellow)",
        "driver_type": "waveshare",
        "driver_module": "epd7in5c",
        "size_category": "large",
        "notes": "Waveshare 7.5inch 3-color e-Paper HAT (C)."
    },
    "waveshare_7_5_hd": {
        "id": "waveshare_7_5_hd",
        "brand": "Waveshare",
        "model_name": "Waveshare 7.5\" HD (880x528)",
        "width": 880,
        "height": 528,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd7in5_HD",
        "size_category": "large",
        "notes": "High Definition 880x528 7.5inch e-Paper HAT."
    },

    # ==========================================
    # WAVESHARE MEDIUM PANELS (4.0" - 5.83")
    # ==========================================
    "waveshare_5_83_v2": {
        "id": "waveshare_5_83_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 5.83\" V2 (Black/White)",
        "width": 648,
        "height": 480,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd5in83_V2",
        "size_category": "medium",
        "notes": "Waveshare 5.83inch e-Paper HAT V2."
    },
    "waveshare_5_83_b_v2": {
        "id": "waveshare_5_83_b_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 5.83\" (B) V2 (Red/Black/White)",
        "width": 648,
        "height": 480,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd5in83b_V2",
        "size_category": "medium",
        "notes": "Waveshare 5.83inch 3-color e-Paper HAT (B) V2."
    },
    "waveshare_5_65_f": {
        "id": "waveshare_5_65_f",
        "brand": "Waveshare",
        "model_name": "Waveshare 5.65\" (F) 7-Color ACeP",
        "width": 600,
        "height": 448,
        "palette_type": "7color",
        "colors_desc": "7-Color (Black, White, Green, Blue, Red, Yellow, Orange)",
        "driver_type": "waveshare",
        "driver_module": "epd5in65f",
        "size_category": "medium",
        "notes": "Waveshare 5.65inch 7-color e-Paper HAT (F)."
    },
    "waveshare_4_2": {
        "id": "waveshare_4_2",
        "brand": "Waveshare",
        "model_name": "Waveshare 4.2\" (Black/White)",
        "width": 400,
        "height": 300,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd4in2",
        "size_category": "medium",
        "notes": "Popular 4.2inch 400x300 e-paper HAT."
    },
    "waveshare_4_2_b": {
        "id": "waveshare_4_2_b",
        "brand": "Waveshare",
        "model_name": "Waveshare 4.2\" (B) (Red/Black/White)",
        "width": 400,
        "height": 300,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd4in2b_V2",
        "size_category": "medium",
        "notes": "Waveshare 4.2inch 3-color e-Paper HAT (B)."
    },
    "waveshare_4_01_f": {
        "id": "waveshare_4_01_f",
        "brand": "Waveshare",
        "model_name": "Waveshare 4.01\" (F) 7-Color ACeP",
        "width": 640,
        "height": 400,
        "palette_type": "7color",
        "colors_desc": "7-Color ACeP",
        "driver_type": "waveshare",
        "driver_module": "epd4in01f",
        "size_category": "medium",
        "notes": "Compact 4.01-inch 7-color e-Paper HAT."
    },

    # ==========================================
    # WAVESHARE COMPACT PANELS (1.54" - 3.7")
    # ==========================================
    "waveshare_3_7": {
        "id": "waveshare_3_7",
        "brand": "Waveshare",
        "model_name": "Waveshare 3.7\" (480x280)",
        "width": 480,
        "height": 280,
        "palette_type": "grayscale16",
        "colors_desc": "5-level Grayscale / Monochrome",
        "driver_type": "waveshare",
        "driver_module": "epd3in7",
        "size_category": "small",
        "notes": "3.7inch 480x280 e-Paper HAT with partial refresh."
    },
    "waveshare_2_9_v2": {
        "id": "waveshare_2_9_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 2.9\" V2 (Black/White)",
        "width": 296,
        "height": 128,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd2in9_V2",
        "size_category": "small",
        "notes": "Waveshare 2.9inch e-Paper module V2."
    },
    "waveshare_2_9_b_v3": {
        "id": "waveshare_2_9_b_v3",
        "brand": "Waveshare",
        "model_name": "Waveshare 2.9\" (B) V3 (Red/Black/White)",
        "width": 296,
        "height": 128,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd2in9b_V3",
        "size_category": "small",
        "notes": "Waveshare 2.9inch 3-color e-Paper module."
    },
    "waveshare_2_7_v2": {
        "id": "waveshare_2_7_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 2.7\" V2 (Black/White)",
        "width": 264,
        "height": 176,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd2in7_V2",
        "size_category": "small",
        "notes": "Waveshare 2.7inch e-Paper HAT V2."
    },
    "waveshare_2_7_b_v2": {
        "id": "waveshare_2_7_b_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 2.7\" (B) V2 (Red/Black/White)",
        "width": 264,
        "height": 176,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd2in7b_V2",
        "size_category": "small",
        "notes": "Waveshare 2.7inch 3-color e-Paper HAT."
    },
    "waveshare_2_13_v3": {
        "id": "waveshare_2_13_v3",
        "brand": "Waveshare",
        "model_name": "Waveshare 2.13\" V3 (Black/White)",
        "width": 250,
        "height": 122,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd2in13_V3",
        "size_category": "small",
        "notes": "Popular 2.13inch e-Paper HAT for Pi Zero."
    },
    "waveshare_2_13_b_v4": {
        "id": "waveshare_2_13_b_v4",
        "brand": "Waveshare",
        "model_name": "Waveshare 2.13\" (B) V4 (Red/Black/White)",
        "width": 250,
        "height": 122,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd2in13b_V4",
        "size_category": "small",
        "notes": "2.13inch 3-color e-Paper HAT for Pi Zero."
    },
    "waveshare_1_54_v2": {
        "id": "waveshare_1_54_v2",
        "brand": "Waveshare",
        "model_name": "Waveshare 1.54\" V2 (200x200)",
        "width": 200,
        "height": 200,
        "palette_type": "mono",
        "colors_desc": "Monochrome (Black, White)",
        "driver_type": "waveshare",
        "driver_module": "epd1in54_V2",
        "size_category": "small",
        "notes": "1.54inch square 200x200 e-Paper module."
    },
    "waveshare_1_54_b": {
        "id": "waveshare_1_54_b",
        "brand": "Waveshare",
        "model_name": "Waveshare 1.54\" (B) (Red/Black/White)",
        "width": 200,
        "height": 200,
        "palette_type": "bwr",
        "colors_desc": "3-Color (Black, White, Red)",
        "driver_type": "waveshare",
        "driver_module": "epd1in54b",
        "size_category": "small",
        "notes": "1.54inch square 3-color 200x200 e-Paper module."
    },
}

def get_screen(screen_id: str) -> Dict[str, Any]:
    """Retrieve screen metadata by screen ID. Fallbacks to mock_7_3 if not found."""
    return SCREEN_CATALOG.get(screen_id, SCREEN_CATALOG["mock_7_3"])

def list_screens(
    brand: Optional[str] = None,
    palette_type: Optional[str] = None,
    size_category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter and list screens from the catalog."""
    results = []
    for screen in SCREEN_CATALOG.values():
        if brand and brand.lower() != "all" and screen["brand"].lower() != brand.lower():
            continue
        if palette_type and palette_type.lower() != "all" and screen["palette_type"].lower() != palette_type.lower():
            continue
        if size_category and size_category.lower() != "all" and screen["size_category"].lower() != size_category.lower():
            continue
        results.append(screen)
    return results
