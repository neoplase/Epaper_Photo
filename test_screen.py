#!/usr/bin/env python3
"""
test_screen.py - Standalone Hardware Diagnostic & Test Card Utility for E-Paper Displays.
Specifically tailored for Raspberry Pi Zero / Zero 2 with Pimoroni Inky Impression & Waveshare.

Usage:
    python3 test_screen.py                      # Run diagnostics & display test card on active screen
    python3 test_screen.py --clear              # Clear screen to blank
    python3 test_screen.py --info               # Check hardware/drivers without updating screen
    python3 test_screen.py --screen inky_impression_7_3  # Test specific screen ID
"""

import os
import sys
import time
import argparse
from datetime import datetime

# ANSI Color formatting
C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_CYAN = "\033[96m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def print_ok(msg):
    print(f" {C_GREEN}[✓]{C_RESET} {msg}")

def print_warn(msg):
    print(f" {C_YELLOW}[!]{C_RESET} {msg}")

def print_fail(msg):
    print(f" {C_RED}[✗]{C_RESET} {msg}")

def print_header(title):
    print(f"\n{C_BOLD}{C_CYAN}=== {title} ==={C_RESET}")

def check_system():
    print_header("1. Raspberry Pi Hardware & Interfaces")

    # 1.1 Check Pi model
    model = "Unknown Device"
    if os.path.exists("/proc/device-tree/model"):
        try:
            with open("/proc/device-tree/model", "r") as f:
                model = f.read().strip("\x00 \n")
        except Exception:
            pass
    print_ok(f"Hardware Model: {model}")

    # 1.2 Check SPI
    has_spi = os.path.exists("/dev/spidev0.0") or os.path.exists("/dev/spidev0.1")
    if has_spi:
        print_ok("SPI Interface: Enabled (/dev/spidev0.* detected)")
    else:
        print_fail("SPI Interface: NOT FOUND (/dev/spidev0.0 missing)")
        print(f"    {C_YELLOW}→ Fix: Run 'sudo raspi-config' > Interface Options > SPI > Enable, then reboot.{C_RESET}")

    # 1.3 Check I2C
    has_i2c = os.path.exists("/dev/i2c-1")
    if has_i2c:
        print_ok("I2C Interface: Enabled (/dev/i2c-1 detected)")
    else:
        print_warn("I2C Interface: NOT FOUND (/dev/i2c-1 missing)")
        print(f"    {C_YELLOW}→ Inky auto-detection requires I2C to read the onboard EEPROM.{C_RESET}")
        print(f"    {C_YELLOW}→ Fix: Run 'sudo raspi-config' > Interface Options > I2C > Enable, then reboot.{C_RESET}")

    # 1.4 Check SPI CS0 pin conflict overlay (Pi OS Bookworm)
    cfg_files = ["/boot/firmware/config.txt", "/boot/config.txt"]
    overlay_found = False
    for cfg in cfg_files:
        if os.path.exists(cfg):
            try:
                with open(cfg, "r") as f:
                    content = f.read()
                    if "dtoverlay=spi0-0cs" in content or "dtoverlay=spi0-1cs" in content:
                        overlay_found = True
                        print_ok(f"SPI CS0 Overlay: Present in {cfg}")
                        break
            except Exception:
                pass
    if not overlay_found:
        print_warn("SPI CS0 Overlay: 'dtoverlay=spi0-0cs' not detected in config.txt")
        print(f"    {C_YELLOW}→ On Raspberry Pi OS Bookworm, kernel locks GPIO 8 unless 'dtoverlay=spi0-0cs' is set.{C_RESET}")

    return has_spi

def check_python_dependencies():
    print_header("2. Python Libraries")
    all_ok = True

    # Pillow
    try:
        import PIL
        from PIL import Image, ImageDraw, ImageFont
        print_ok(f"Pillow (PIL): Installed (v{PIL.__version__})")
    except ImportError:
        print_fail("Pillow is NOT installed (run: sudo apt install python3-pil)")
        all_ok = False

    # Inky
    has_inky = False
    try:
        import inky
        print_ok(f"Pimoroni Inky library: Installed (v{getattr(inky, '__version__', 'unknown')})")
        has_inky = True
    except ImportError:
        print_fail("Pimoroni 'inky' library is NOT installed!")
        print(f"    {C_YELLOW}→ Fix: pip3 install inky --break-system-packages{C_RESET}")
        all_ok = False

    # spidev
    try:
        import spidev
        print_ok("spidev: Installed")
    except ImportError:
        print_warn("spidev is NOT installed (run: sudo apt install python3-spidev)")

    return has_inky

def generate_test_pattern(width=800, height=480, screen_title="Inky Impression 7.3\""):
    """Creates a vivid 7-color test card with color bars and diagnostic text."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # 7-Color ACeP Test Bars
    colors = [
        ("BLACK", (0, 0, 0)),
        ("WHITE", (255, 255, 255)),
        ("GREEN", (0, 180, 0)),
        ("BLUE", (0, 0, 220)),
        ("RED", (220, 0, 0)),
        ("YELLOW", (255, 220, 0)),
        ("ORANGE", (255, 128, 0)),
    ]

    # Draw color stripes at the top half
    bar_width = width // len(colors)
    bar_height = int(height * 0.45)
    for i, (name, rgb) in enumerate(colors):
        x0 = i * bar_width
        x1 = width if i == len(colors) - 1 else (i + 1) * bar_width
        draw.rectangle([x0, 0, x1, bar_height], fill=rgb)
        # Label each bar (white text for dark colors, black for light)
        text_color = (0, 0, 0) if name in ("WHITE", "YELLOW") else (255, 255, 255)
        draw.text((x0 + 8, bar_height - 24), name[:3], fill=text_color)

    # Decorative dividing border
    draw.line([(0, bar_height), (width, bar_height)], fill=(0, 0, 0), width=3)

    # Bottom Area: Information box
    info_y = bar_height + 15
    draw.rectangle([10, info_y, width - 10, height - 10], outline=(0, 0, 0), width=2)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Text lines
    lines = [
        f"HARDWARE TEST: {screen_title}",
        f"Resolution: {width} x {height}  |  Palette: 7-Color ACeP",
        f"Timestamp:  {timestamp}",
        "Status:     SPI Communication Active & Working!",
    ]

    cur_y = info_y + 15
    for idx, line in enumerate(lines):
        color = (220, 0, 0) if idx == 0 else ((0, 120, 0) if idx == 3 else (0, 0, 0))
        draw.text((30, cur_y), line, fill=color)
        cur_y += 24

    return img

def test_inky_screen(clear_only=False):
    print_header("3. Pimoroni Inky Hardware Initialization")

    device = None
    # Attempt 1: inky.auto()
    try:
        from inky.auto import auto
        print(" [*] Probing hardware via inky.auto()...")
        device = auto()
        print_ok(f"Auto-detected Inky display: {getattr(device, 'colour', 'Color')} ({device.resolution[0]}x{device.resolution[1]})")
    except Exception as e:
        print_warn(f"inky.auto() detection did not succeed: {e}")
        print(" [*] Attempting direct manual initialization for Inky Impression 7.3\" (inky_ac073tc1a)...")
        try:
            from inky.inky_ac073tc1a import Inky as Inky73
            device = Inky73()
            print_ok("Initialized Inky 7.3\" driver directly via 'inky.inky_ac073tc1a'!")
        except Exception as ex:
            print_fail(f"Direct Inky 7.3\" initialization failed: {ex}")
            if "claim" in str(ex).lower() or "pins" in str(ex).lower() or "gpio" in str(ex).lower():
                print(f"\n{C_RED}{C_BOLD}--> PIN CONFLICT DETECTED:{C_RESET}")
                print("    Add 'dtoverlay=spi0-0cs' to /boot/firmware/config.txt and reboot:")
                print("    echo 'dtoverlay=spi0-0cs' | sudo tee -a /boot/firmware/config.txt && sudo reboot\n")
            return False

    width, height = device.resolution
    print_ok(f"Target Display Resolution: {width}x{height}")

    if clear_only:
        print_header("4. Clearing Display to White")
        from PIL import Image
        blank = Image.new("P", (width, height), 0)
        device.set_image(blank)
        print(" [*] Sending clear command (refresh takes ~20s)...")
        start = time.time()
        device.show()
        elapsed = round(time.time() - start, 1)
        print_ok(f"Screen cleared successfully in {elapsed} seconds!")
        return True

    print_header("4. Rendering & Pushing Test Pattern")
    print(" [*] Generating 7-color test card...")
    test_img = generate_test_pattern(width, height, "Inky Impression 7.3\"")

    print(f" [*] Sending image buffer to Inky Impression (refresh cycle in progress, please wait ~20-30s)...")
    start = time.time()
    try:
        device.set_image(test_img)
        device.show()
        elapsed = round(time.time() - start, 1)
        print_ok(f"Hardware refresh completed successfully in {elapsed} seconds!")
        print(f"\n{C_GREEN}{C_BOLD}SUCCESS: Your Inky Impression 7.3\" is working perfectly!{C_RESET}\n")
        return True
    except Exception as e:
        print_fail(f"Failed during device.show(): {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Test and diagnose E-Paper screen hardware.")
    parser.add_argument("--clear", action="store_true", help="Clear the display to blank white.")
    parser.add_argument("--info", action="store_true", help="Only check interfaces and drivers without pushing to screen.")
    parser.add_argument("--screen", default="inky_impression_7_3", help="Screen identifier from catalog (default: inky_impression_7_3)")
    args = parser.parse_args()

    print(f"\n{C_BOLD}Universal E-Paper Photo Frame — Screen Diagnostic Tool{C_RESET}")
    print(f"Target Screen: {args.screen}")

    has_spi = check_system()
    has_dep = check_python_dependencies()

    if args.info:
        print("\n[+] Diagnostic info check finished.")
        return

    if not has_spi:
        print(f"\n{C_RED}[!] Cannot proceed with display test: SPI hardware interface is missing.{C_RESET}")
        print("Please enable SPI in raspi-config and reboot first.")
        sys.exit(1)

    if not has_dep:
        print(f"\n{C_RED}[!] Cannot proceed: Missing required Python libraries.{C_RESET}")
        sys.exit(1)

    # Test Inky display
    if "inky" in args.screen.lower():
        success = test_inky_screen(clear_only=args.clear)
        if not success:
            sys.exit(1)
    else:
        # Generic / Waveshare test through DriverFactory
        print_header("3. Driver Factory Test")
        try:
            from core.driver_factory import get_driver
            driver = get_driver(args.screen, force_refresh=True)
            print_ok(f"Loaded driver: {driver.name} (type: {type(driver).__name__})")
            if args.clear:
                driver.clear()
                print_ok("Screen cleared.")
            else:
                test_img = generate_test_pattern(driver.width, driver.height, driver.name)
                driver.display(test_img)
                print_ok("Display updated.")
        except Exception as e:
            print_fail(f"Driver execution failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
