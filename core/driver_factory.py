"""
driver_factory.py - Factory for instantiating e-paper display drivers with safe fallback.
"""

import logging
from core.screen_catalog import get_screen, SCREEN_CATALOG
from core.drivers.base import BaseDisplayDriver
from core.drivers.mock_driver import MockDisplayDriver
from core.drivers.inky_driver import InkyDisplayDriver
from core.drivers.waveshare_driver import WaveshareDisplayDriver

logger = logging.getLogger("epaper.driver_factory")

_active_driver = None
_active_screen_id = None

def get_driver(screen_id: str = None, force_refresh: bool = False) -> BaseDisplayDriver:
    """
    Returns an initialized driver for the given screen_id.
    Falls back gracefully to MockDisplayDriver if physical hardware is absent.
    """
    global _active_driver, _active_screen_id

    if screen_id is None:
        from core.config_manager import get_config
        screen_id = get_config().get("active_screen", "inky_impression_7_3")

    if not force_refresh and _active_driver is not None and _active_screen_id == screen_id:
        return _active_driver

    screen_info = get_screen(screen_id)
    driver_type = screen_info.get("driver_type", "mock")

    logger.info(f"[DriverFactory] Loading driver for '{screen_info.get('model_name')}' (Type: {driver_type})")

    driver = None
    if driver_type == "mock":
        driver = MockDisplayDriver(screen_info)
        driver.init()
    elif driver_type == "inky":
        driver = InkyDisplayDriver(screen_info)
        success = driver.init()
        if not success:
            logger.warning("[DriverFactory] Physical Inky hardware not detected. Using Virtual Mock Driver for preview.")
            driver = MockDisplayDriver(screen_info)
            driver.init()
    elif driver_type == "waveshare":
        driver = WaveshareDisplayDriver(screen_info)
        success = driver.init()
        if not success:
            logger.warning(f"[DriverFactory] Physical Waveshare hardware not detected for {screen_id}. Using Virtual Mock Driver for preview.")
            driver = MockDisplayDriver(screen_info)
            driver.init()
    else:
        driver = MockDisplayDriver(screen_info)
        driver.init()

    _active_driver = driver
    _active_screen_id = screen_id
    return _active_driver
