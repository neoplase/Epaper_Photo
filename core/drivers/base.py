"""
base.py - Abstract Base Class for E-Paper Display Drivers.
"""

from abc import ABC, abstractmethod
from PIL import Image

class BaseDisplayDriver(ABC):
    def __init__(self, screen_info: dict):
        self.screen_info = screen_info
        self.screen_id = screen_info.get("id", "unknown")
        self.name = screen_info.get("model_name", "E-Paper Display")
        self.width = screen_info.get("width", 800)
        self.height = screen_info.get("height", 480)
        self.palette_type = screen_info.get("palette_type", "7color")
        self.is_initialized = False

    @abstractmethod
    def init(self) -> bool:
        """Initialize the hardware interface (SPI/I2C/GPIO)."""
        pass

    @abstractmethod
    def display(self, image: Image.Image) -> bool:
        """Render and send an image to the display."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear the screen to white."""
        pass

    @abstractmethod
    def sleep(self) -> bool:
        """Put display into deep sleep to eliminate voltage stress."""
        pass
