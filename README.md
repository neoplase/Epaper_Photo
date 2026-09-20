# Universal E-Paper Photo Frame Hub

A high-performance, mobile-responsive photo frame controller built for **Raspberry Pi Zero W v1.3 (ARMv6)** and **Pi Zero 2 W (ARMv8)**, supporting the **entire catalog of Pimoroni Inky and Waveshare e-paper displays**.

![E-Paper Studio](server/static/img/preview_banner.png)

---

## Key Features

* **Universal Screen Support**: 1-click selection across **all Pimoroni Inky displays** (Impression 7.3", 5.7", 4.0", wHAT, pHAT) and **all Waveshare panels** (13.3" IT8951, 10.3", 9.7", 7.5" V2/3-color, 7.3" Spectra 6/ACeP, 5.83", 4.2", 2.9", 2.13", 1.54").
* **Zero Guesswork / Web Selection**: Switch screens on the fly from the Web GUI; aspect ratios, framing tools, and color dithering engines adapt instantly.
* **Dual Pi Zero Architecture**: Extremely lightweight Python backend that runs smoothly on both 32-bit single-core ARMv6 (Pi Zero W) and 64-bit quad-core ARMv8 (Pi Zero 2 W).
* **Client-Side E-Ink Dithering Simulator**: Instant real-time preview of Floyd-Steinberg error diffusion in your phone's browser, offloading heavy calculations from the Pi Zero.
* **5 Palette Engines**:
  * **7-Color**: Black, White, Green, Blue, Red, Yellow, Orange (ACeP / Spectra 6).
  * **3-Color Red (BWR)**: Black, White, Red.
  * **3-Color Yellow (BWY)**: Black, White, Yellow.
  * **16-Level Grayscale**: Smooth photographic gradients for large panels (13.3", 10.3", 9.7").
  * **Monochrome**: Crisp 1-bit Black & White.
* **Smart Slideshow Scheduler**: Automatic periodic photo rotation with hardware deep-sleep to prevent DC voltage degradation and eliminate screen burn-in.

---

## Hardware Connection Guide

All e-paper HATs plug onto the Raspberry Pi 40-pin GPIO header:

| Display Model | Interface | Pi GPIO Header Connection |
| :--- | :--- | :--- |
| **Pimoroni Inky Impression 7.3"** | SPI + I2C | Plugs directly onto 40-pin header |
| **Waveshare 7.3" Color (F / G)** | SPI | Standard Waveshare HAT onto 40-pin header |
| **Waveshare 13.3" E-Paper** | SPI (IT8951) | Connect IT8951 driver HAT to 40-pin header |

---

## Quick Start on Raspberry Pi

1. **Clone or copy this repository onto your Raspberry Pi**:
   ```bash
   git clone https://github.com/your-username/Epaper_Photo.git
   cd Epaper_Photo
   ```

2. **Run the automated installer**:
   ```bash
   sudo bash install.sh
   ```
   *This script enables SPI & I2C, installs dependencies, fetches drivers, and configures an auto-starting systemd service.*

3. **Open the Web GUI**:
   Open a browser on your smartphone, tablet, or PC connected to the same Wi-Fi:
   ```
   http://raspberrypi.local:5000
   ```
   *(or `http://<your-pi-ip>:5000`)*

---

## Development & Local Testing (PC / Mac / Linux)

You can run and test the complete system locally without physical e-paper hardware using the built-in **Virtual Mock Driver**:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python server/app.py
   ```

3. Open `http://localhost:5000` in your browser. Rendered frames are saved to `data/current_display.png`.

---

## Project Structure

```
Epaper_Photo/
├── core/
│   ├── screen_catalog.py      # Complete registry of all Pimoroni & Waveshare screens
│   ├── driver_factory.py      # Instantiates active driver with safe fallback
│   ├── image_engine.py        # Cropping, saturation boost, & Floyd-Steinberg dithering
│   ├── config_manager.py      # Thread-safe config storage (config.json)
│   ├── slideshow.py           # Background rotation daemon & sleep manager
│   └── drivers/
│       ├── base.py            # Abstract driver interface
│       ├── mock_driver.py     # Virtual display simulator
│       ├── inky_driver.py     # Pimoroni Inky wrapper
│       └── waveshare_driver.py# Waveshare EPD dynamic dispatcher
├── server/
│   ├── app.py                 # Flask REST API & Web server
│   ├── templates/
│   │   └── index.html         # Responsive web studio UI
│   └── static/
│       ├── css/style.css      # Dark-mode glassmorphic design system
│       └── js/
│           ├── dither_simulator.js # Client-side pure JS Floyd-Steinberg canvas simulator
│           └── app.js         # Interactive cropper, screen selector & photo manager
├── data/
│   ├── photos/                # Uploaded photos
│   └── thumbs/                # Auto-generated thumbnails
├── install.sh                 # 1-click Raspberry Pi OS installer & systemd service
├── requirements.txt           # Python dependencies
└── config.json                # User settings (screen profile, intervals, etc.)
```
