"""
waveshare_driver.py - Universal driver wrapper for Waveshare E-Paper displays.
Dynamically loads and dispatches to the correct waveshare_epd module.
"""

import sys
import os
import importlib
import logging
from PIL import Image
from core.drivers.base import BaseDisplayDriver

logger = logging.getLogger("epaper.waveshare_driver")

class WaveshareDisplayDriver(BaseDisplayDriver):
    def __init__(self, screen_info: dict):
        super().__init__(screen_info)
        self.driver_module_name = screen_info.get("driver_module", "epd7in3f")
        self.epd = None

    def _import_epd_module(self):
        """Attempts to import the Waveshare module from system or local paths."""
        # Try direct import from waveshare_epd package
        module_path = f"waveshare_epd.{self.driver_module_name}"
        try:
            return importlib.import_module(module_path)
        except Exception as e:
            logger.debug(f"[WaveshareDriver] Could not load {module_path}: {e}")

        # Try direct import by module name (e.g. if installed in site-packages directly)
        try:
            return importlib.import_module(self.driver_module_name)
        except Exception as e:
            logger.debug(f"[WaveshareDriver] Could not load {self.driver_module_name}: {e}")

        return None

    def init(self) -> bool:
        logger.info(f"[WaveshareDriver] Loading module '{self.driver_module_name}' for {self.name}...")
        mod = self._import_epd_module()
        if mod is None:
            logger.warning(
                f"[WaveshareDriver] Waveshare module '{self.driver_module_name}' not found. "
                "Ensure waveshare-epd is installed on your Raspberry Pi."
            )
            return False

        try:
            if hasattr(mod, "EPD"):
                self.epd = mod.EPD()
            else:
                logger.error(f"[WaveshareDriver] Module {self.driver_module_name} does not have an EPD class.")
                return False

            logger.info(f"[WaveshareDriver] Initializing EPD hardware...")
            self.epd.init()
            if hasattr(self.epd, "width") and hasattr(self.epd, "height"):
                self.width = self.epd.width
                self.height = self.epd.height
            self.is_initialized = True
            logger.info(f"[WaveshareDriver] Successfully initialized {self.name} ({self.width}x{self.height})")
            return True
        except Exception as e:
            logger.error(f"[WaveshareDriver] Failed to initialize hardware for {self.name}: {e}")
            return False

    def display(self, image: Image.Image) -> bool:
        if not self.is_initialized:
            if not self.init():
                logger.error("[WaveshareDriver] Hardware initialization failed.")
                return False

        try:
            # Match screen dimensions
            if image.size != (self.width, self.height):
                logger.info(f"[WaveshareDriver] Resizing image to match panel {self.width}x{self.height}")
                image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

            logger.info(f"[WaveshareDriver] Preparing image buffer ({self.palette_type})...")

            # Case 1: 3-Color displays (Black, White, Red or Yellow)
            if self.palette_type in ("bwr", "bwy"):
                # Split image into black/white channel and red/yellow channel
                # Waveshare 3-color drivers usually take (black_buffer, red_buffer)
                if hasattr(self.epd, "getbuffer"):
                    # Extract black and red components
                    black_img = Image.new("1", (self.width, self.height), 255)
                    color_img = Image.new("1", (self.width, self.height), 255)
                    
                    rgb_img = image.convert("RGB")
                    for y in range(self.height):
                        for x in range(self.width):
                            r, g, b = rgb_img.getpixel((x, y))
                            if r > 180 and g < 100 and b < 100: # Red
                                color_img.putpixel((x, y), 0)
                            elif r > 180 and g > 180 and b < 100: # Yellow
                                color_img.putpixel((x, y), 0)
                            elif r < 120 and g < 120 and b < 120: # Black
                                black_img.putpixel((x, y), 0)
                                
                    buf_black = self.epd.getbuffer(black_img)
                    buf_color = self.epd.getbuffer(color_img)
                    logger.info("[WaveshareDriver] Sending 3-color frame to display...")
                    self.epd.display(buf_black, buf_color)
                else:
                    logger.error("[WaveshareDriver] getbuffer method missing for 3-color display.")
                    return False

            # Case 2: 16-level grayscale (13.3", 10.3", 9.7" IT8951)
            elif self.palette_type == "grayscale16":
                if hasattr(self.epd, "getbuffer_4Gray"):
                    buf = self.epd.getbuffer_4Gray(image)
                    if hasattr(self.epd, "display_4Gray"):
                        self.epd.display_4Gray(buf)
                    else:
                        self.epd.display(buf)
                elif hasattr(self.epd, "getbuffer"):
                    buf = self.epd.getbuffer(image)
                    self.epd.display(buf)
                else:
                    self.epd.display(image)

            # Case 3: 7-Color ACeP / Spectra 6 or Monochrome
            else:
                if hasattr(self.epd, "getbuffer"):
                    buf = self.epd.getbuffer(image)
                    logger.info("[WaveshareDriver] Sending buffer to display (refresh taking place)...")
                    self.epd.display(buf)
                elif hasattr(self.epd, "display"):
                    self.epd.display(image)

            logger.info("[WaveshareDriver] Display refresh completed successfully.")
            return True

        except Exception as e:
            logger.error(f"[WaveshareDriver] Error during display refresh: {e}")
            return False

    def clear(self) -> bool:
        if not self.is_initialized:
            if not self.init():
                return False
        try:
            if hasattr(self.epd, "Clear"):
                self.epd.Clear()
            elif hasattr(self.epd, "clear"):
                self.epd.clear()
            logger.info("[WaveshareDriver] Display cleared.")
            return True
        except Exception as e:
            logger.error(f"[WaveshareDriver] Clear failed: {e}")
            return False

    def sleep(self) -> bool:
        if self.epd and hasattr(self.epd, "sleep"):
            try:
                self.epd.sleep()
                logger.info("[WaveshareDriver] Display in deep sleep mode.")
                return True
            except Exception as e:
                logger.warning(f"[WaveshareDriver] Could not enter sleep: {e}")
        return True
