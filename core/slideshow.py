"""
slideshow.py - Background photo slideshow daemon and schedule manager.
"""

import os
import time
import random
import logging
import threading
from typing import Optional
from PIL import Image

from core.config_manager import get_config
from core.screen_catalog import get_screen
from core.driver_factory import get_driver
from core.image_engine import process_image

logger = logging.getLogger("epaper.slideshow")

class SlideshowDaemon:
    def __init__(self, photo_dir: str = "data/photos", status_file: str = "data/status.json"):
        self.photo_dir = photo_dir
        self.status_file = status_file
        os.makedirs(self.photo_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)

        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.current_photo: Optional[str] = None
        self.current_photo_time: Optional[str] = None
        self.next_refresh_time: Optional[str] = None
        self.is_refreshing: bool = False
        self._photo_index: int = 0

    def start(self):
        """Starts the background slideshow thread."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True, name="SlideshowWorker")
            self._thread.start()
            logger.info("[Slideshow] Background slideshow service started.")

    def stop(self):
        """Stops the background thread."""
        with self._lock:
            self._stop_event.set()
            self._wake_event.set()
            if self._thread:
                self._thread.join(timeout=3)
                self._thread = None
                logger.info("[Slideshow] Background slideshow service stopped.")

    def trigger_next(self, specific_photo: Optional[str] = None):
        """Manually trigger immediate refresh, optionally displaying a specific file."""
        if specific_photo:
            self._display_single_photo(specific_photo)
        else:
            self._wake_event.set()

    def get_photos(self) -> list:
        """Returns sorted list of image filenames in photo directory."""
        supported_exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
        if not os.path.exists(self.photo_dir):
            return []
        files = [f for f in os.listdir(self.photo_dir) if f.lower().endswith(supported_exts)]
        files.sort()
        return files

    def _display_single_photo(self, filename: str) -> bool:
        """Loads, processes, and pushes a specific photo to the active screen."""
        photo_path = os.path.join(self.photo_dir, filename)
        if not os.path.exists(photo_path):
            logger.error(f"[Slideshow] File {photo_path} does not exist.")
            return False

        config = get_config()
        screen_id = config.get("active_screen", "inky_impression_7_3")
        screen_info = get_screen(screen_id)

        try:
            self.is_refreshing = True
            logger.info(f"[Slideshow] Processing '{filename}' for screen {screen_info.get('model_name')}...")

            with Image.open(photo_path) as raw_img:
                processed = process_image(
                    raw_img,
                    target_width=screen_info.get("width", 800),
                    target_height=screen_info.get("height", 480),
                    palette_type=screen_info.get("palette_type", "7color"),
                    saturation=config.get("saturation", 1.3),
                    contrast=config.get("contrast", 1.15),
                    brightness=config.get("brightness", 1.05),
                    fit_mode=config.get("fit_mode", "cover")
                )

            # Push to active driver
            driver = get_driver(screen_id)
            success = driver.display(processed)

            # Deep sleep to protect e-paper hardware
            if config.get("deep_sleep_enabled", True):
                driver.sleep()

            if success:
                self.current_photo = filename
                self.current_photo_time = time.strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f"[Slideshow] Displayed '{filename}' successfully.")
            return success

        except Exception as e:
            logger.error(f"[Slideshow] Failed to render '{filename}': {e}")
            return False
        finally:
            self.is_refreshing = False

    def _run_loop(self):
        """Main periodic refresh loop."""
        # Display first photo shortly after boot
        time.sleep(2)

        while not self._stop_event.is_set():
            config = get_config()
            enabled = config.get("slideshow_enabled", True)
            interval_min = max(1, config.get("slideshow_interval_minutes", 60))
            interval_sec = interval_min * 60

            if enabled:
                photos = self.get_photos()
                if photos:
                    # Choose photo
                    if config.get("slideshow_shuffle", True):
                        selected = random.choice(photos)
                    else:
                        selected = photos[self._photo_index % len(photos)]
                        self._photo_index += 1

                    self._display_single_photo(selected)
                    next_timestamp = time.time() + interval_sec
                    self.next_refresh_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_timestamp))
                else:
                    logger.debug("[Slideshow] No photos available in library.")
                    self.next_refresh_time = None
            else:
                self.next_refresh_time = None

            # Wait for interval or until manually triggered
            self._wake_event.wait(timeout=interval_sec)
            self._wake_event.clear()

# Global singleton daemon instance
slideshow_daemon = SlideshowDaemon()
