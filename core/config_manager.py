"""
config_manager.py - Thread-safe configuration storage and retrieval.
"""

import os
import json
import threading
import logging

logger = logging.getLogger("epaper.config")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
_lock = threading.Lock()

DEFAULT_CONFIG = {
    "active_screen": "inky_impression_7_3",
    "slideshow_interval_minutes": 60,
    "slideshow_enabled": True,
    "slideshow_shuffle": True,
    "saturation": 1.3,
    "contrast": 1.15,
    "brightness": 1.05,
    "fit_mode": "cover",  # 'cover' (crop to fill), 'contain' (letterbox), 'stretch'
    "orientation": "auto", # 'auto', 'landscape', 'portrait'
    "deep_sleep_enabled": True
}

def get_config() -> dict:
    """Returns the current configuration dictionary, initialized with defaults if missing."""
    with _lock:
        if not os.path.exists(CONFIG_PATH):
            save_config_internal(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()

        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge defaults for any missing keys
                merged = DEFAULT_CONFIG.copy()
                merged.update(data)
                return merged
        except Exception as e:
            logger.error(f"Error reading {CONFIG_PATH}: {e}. Returning defaults.")
            return DEFAULT_CONFIG.copy()

def update_config(new_values: dict) -> dict:
    """Updates configuration with new key-value pairs and writes to file."""
    with _lock:
        current = DEFAULT_CONFIG.copy()
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    current.update(json.load(f))
            except Exception as e:
                logger.error(f"Error reading existing config: {e}")

        current.update(new_values)
        save_config_internal(current)
        return current.copy()

def save_config_internal(data: dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error writing to {CONFIG_PATH}: {e}")
