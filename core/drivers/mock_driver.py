"""
mock_driver.py - Virtual / Mock display driver for local development and testing.
Saves rendered output to data/current_display.png.
"""

import os
import time
import logging
from PIL import Image
from core.drivers.base import BaseDisplayDriver

logger = logging.getLogger("epaper.mock_driver")

class MockDisplayDriver(BaseDisplayDriver):
    def __init__(self, screen_info: dict, output_dir: str = "data"):
        super().__init__(screen_info)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_path = os.path.join(self.output_dir, "current_display.png")
        self.last_update_time = None
        self.is_sleeping = False

    def init(self) -> bool:
        logger.info(f"[MockDriver] Initialized virtual display '{self.name}' ({self.width}x{self.height}, {self.palette_type})")
        self.is_initialized = True
        self.is_sleeping = False
        return True

    def display(self, image: Image.Image) -> bool:
        if not self.is_initialized:
            self.init()

        # Ensure image matches target dimensions
        if image.size != (self.width, self.height):
            logger.warning(f"[MockDriver] Image size {image.size} does not match screen ({self.width}x{self.height}). Resizing...")
            image = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

        # Save to disk as PNG
        try:
            image.save(self.output_path, "PNG")
            self.last_update_time = time.strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[MockDriver] Rendered frame successfully to {self.output_path} at {self.last_update_time}")
            return True
        except Exception as e:
            logger.error(f"[MockDriver] Error saving mock display image: {e}")
            return False

    def clear(self) -> bool:
        logger.info("[MockDriver] Screen cleared (blank white)")
        blank = Image.new("RGB", (self.width, self.height), (255, 255, 255))
        return self.display(blank)

    def sleep(self) -> bool:
        logger.info("[MockDriver] Screen entered deep sleep.")
        self.is_sleeping = True
        return True
