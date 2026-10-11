"""
inky_driver.py - Driver wrapper for Pimoroni Inky series e-paper displays.
Supports Inky Impression (7.3\", 5.7\", 4.0\"), Inky wHAT (4.2\"), and Inky pHAT (2.13\").
"""

import logging
from PIL import Image
from core.drivers.base import BaseDisplayDriver

logger = logging.getLogger("epaper.inky_driver")

class InkyDisplayDriver(BaseDisplayDriver):
    def __init__(self, screen_info: dict):
        super().__init__(screen_info)
        self.device = None

    def init(self) -> bool:
        try:
            # Check if inky auto can detect the connected Inky HAT
            from inky.auto import auto
            logger.info(f"[InkyDriver] Initializing Inky display via inky.auto() for {self.name}...")
            self.device = auto()
            self.width = self.device.resolution[0]
            self.height = self.device.resolution[1]
            self.is_initialized = True
            logger.info(f"[InkyDriver] Successfully initialized Inky {self.device.colour} ({self.width}x{self.height})")
            return True
        except ImportError:
            logger.warning("[InkyDriver] 'inky' Python library is not installed. (Hardware SPI driver unavailable)")
            return False
        except Exception as e:
            logger.warning(f"[InkyDriver] Failed to auto-initialize Inky hardware ({e}). Trying model-specific fallback...")
            try:
                # Specific initialization for Impression 7.3"
                if "impression_7_3" in self.screen_id or "7_3" in self.screen_id:
                    from inky.inky_ac073tc1a import Inky as Inky73
                    self.device = Inky73()
                    self.width, self.height = self.device.resolution
                    self.is_initialized = True
                    logger.info(f"[InkyDriver] Initialized Inky 7.3\" via inky_ac073tc1a ({self.width}x{self.height})")
                    return True
                elif "impression_5_7" in self.screen_id or "impression_4_0" in self.screen_id:
                    from inky.inky_uc8159 import Inky as InkyUC8159
                    self.device = InkyUC8159()
                    self.width, self.height = self.device.resolution
                    self.is_initialized = True
                    logger.info(f"[InkyDriver] Initialized Inky UC8159 ({self.width}x{self.height})")
                    return True
                elif "what" in self.screen_id:
                    from inky.inky_what import InkyWHAT
                    color = "red" if "bwr" in self.palette_type else ("yellow" if "bwy" in self.palette_type else "black")
                    self.device = InkyWHAT(color)
                    self.width, self.height = self.device.resolution
                    self.is_initialized = True
                    return True
                elif "phat" in self.screen_id:
                    from inky.inky_phat import InkyPHAT
                    color = "red" if "bwr" in self.palette_type else ("yellow" if "bwy" in self.palette_type else "black")
                    self.device = InkyPHAT(color)
                    self.width, self.height = self.device.resolution
                    self.is_initialized = True
                    return True
                else:
                    logger.error(f"[InkyDriver] Unsupported Inky model variant: {self.screen_id}")
                    return False
            except Exception as ex:
                logger.error(f"[InkyDriver] Inky hardware fallback failed: {ex}")
                if "claim" in str(ex).lower() or "pins" in str(ex).lower():
                    logger.error("[InkyDriver] SPI Pin conflict detected. Add 'dtoverlay=spi0-0cs' to /boot/firmware/config.txt and reboot.")
                return False

    def display(self, image: Image.Image) -> bool:
        if not self.is_initialized:
            if not self.init():
                logger.error("[InkyDriver] Cannot display: Inky hardware not initialized.")
                return False

        try:
            if image.size != (self.width, self.height):
                logger.info(f"[InkyDriver] Resizing image {image.size} to match Inky resolution ({self.width}x{self.height})")
                image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

            # Inky library handles setting image and pushing to SPI
            self.device.set_image(image)
            logger.info("[InkyDriver] Sending image to Inky display (refresh may take ~15-30s)...")
            self.device.show()
            logger.info("[InkyDriver] Refresh complete.")
            return True
        except Exception as e:
            logger.error(f"[InkyDriver] Error sending image to Inky display: {e}")
            return False

    def clear(self) -> bool:
        if not self.is_initialized:
            if not self.init():
                return False
        try:
            blank = Image.new("P", (self.width, self.height), 0)
            self.device.set_image(blank)
            self.device.show()
            logger.info("[InkyDriver] Inky display cleared.")
            return True
        except Exception as e:
            logger.error(f"[InkyDriver] Error clearing Inky display: {e}")
            return False

    def sleep(self) -> bool:
        # Inky library automatically handles power-down after show()
        logger.info("[InkyDriver] Inky display in sleep state.")
        return True
