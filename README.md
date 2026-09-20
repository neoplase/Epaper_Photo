# 🖼️ Universal E-Paper Photo Frame Hub

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%20(Zero%20W%20%7C%20Zero%202%20W)-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Raspberry Pi">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Hardware-Pimoroni%20Inky%20%26%20Waveshare-F59E0B?style=for-the-badge" alt="Hardware">
  <img src="https://img.shields.io/badge/Architecture-ARMv6%20%2F%20ARMv8-0EA5E9?style=for-the-badge" alt="Architecture">
  <img src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge" alt="License">
</p>

<p align="center">
  A high-performance, mobile-responsive photo frame system designed for <b>Raspberry Pi Zero W v1.3 (ARMv6)</b> and <b>Pi Zero 2 W (ARMv8)</b>, supporting the <b>entire catalog of Pimoroni Inky and Waveshare e-paper displays</b>.
</p>

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Supported Displays](#-supported-displays)
- [Hardware & Connections](#-hardware--connections)
- [Installation Guide](#-installation-guide)
  - [Automated 1-Line Setup (Recommended)](#1-automated-1-line-setup-recommended)
  - [Manual Step-by-Step Installation](#2-manual-step-by-step-installation)
  - [Auto-Start on Boot (Systemd Service)](#3-auto-start-on-boot-systemd-service)
- [Web GUI User Guide](#-web-gui-user-guide)
  - [Now Showing](#1-now-showing-dashboard)
  - [Upload & Crop](#2-upload--crop)
  - [Live Dither Studio](#3-live-dither-studio-client-side-simulation)
  - [Gallery & Rotation Schedule](#4-gallery--rotation-schedule)
  - [Screen Profiles](#5-screen-profiles-catalog)
- [Configuration Reference](#-configuration-reference)
- [REST API Endpoints](#-rest-api-endpoints)
- [Local Development & PC Simulation](#-local-development--pc-simulation)
- [Troubleshooting & FAQs](#-troubleshooting--faqs)
- [License](#-license)

---

## ⚡ Key Features

* **Universal Screen Support**: 1-click selection across **all Pimoroni Inky models** (Impression 7.3", 5.7", 4.0", wHAT 4.2", pHAT 2.13") and **all Waveshare panels** (13.3" IT8951, 10.3", 9.7", 7.5" V2/3-Color, 7.3" Spectra 6/ACeP, 5.83", 4.2", 2.9", 2.13", 1.54").
* **Web-Driven Configuration**: No hardware guessing or code modification. Switch screens directly from the Web GUI; crop aspect ratios, preview dithering, and driver backends update dynamically.
* **Dual Pi Zero Architecture**: Extremely lightweight Python + Flask backend optimized for both 32-bit single-core ARMv6 (`Pi Zero W v1.3`) and 64-bit quad-core ARMv8 (`Pi Zero 2 W`).
* **Client-Side Live E-Ink Dithering Simulator**: Instant real-time preview of Floyd-Steinberg error diffusion in your phone's browser canvas, offloading heavy calculations from the Pi Zero.
* **5 Palette Engines**:
  * **7-Color**: Black, White, Green, Blue, Red, Yellow, Orange (ACeP / Spectra 6).
  * **3-Color Red (BWR)**: Black, White, Red.
  * **3-Color Yellow (BWY)**: Black, White, Yellow.
  * **16-Level Grayscale**: Smooth photographic gradients for large panels (13.3", 10.3", 9.7").
  * **Monochrome**: High-contrast 1-bit Black & White.
* **Smart Slideshow Scheduler**: Automatic periodic photo rotation with hardware deep-sleep to eliminate continuous DC bias and protect e-paper micro-capsules from burn-in.

---

## 📺 Supported Displays

| Brand | Model Name | Resolution | Color Capabilities | Driver Backend |
| :--- | :--- | :--- | :--- | :--- |
| **Pimoroni** | Inky Impression 7.3" | 800 × 480 | 7-Color ACeP / Spectra 6 | `inky.auto()` |
| **Pimoroni** | Inky Impression 5.7" | 600 × 448 | 7-Color ACeP | `inky` |
| **Pimoroni** | Inky Impression 4.0" | 640 × 400 | 7-Color ACeP | `inky` |
| **Pimoroni** | Inky wHAT 4.2" | 400 × 300 | 3-Color (Red/Yellow) & Mono | `inky` |
| **Pimoroni** | Inky pHAT 2.13" | 250 × 122 | 3-Color (Red/Yellow) & Mono | `inky` |
| **Waveshare** | Waveshare 13.3" (IT8951) | 1600 × 1200 | 16-Level Grayscale | `epd13in3k` |
| **Waveshare** | Waveshare 10.3" / 9.7" | 1872×1404 / 1200×825 | 16-Level Grayscale | `epd10in3` / `epd9in7` |
| **Waveshare** | Waveshare 7.3" (F) / (G) Spectra 6 | 800 × 480 | 7-Color (ACeP / Spectra 6) | `epd7in3f` / `epd7in3g` |
| **Waveshare** | Waveshare 7.5" V2 / HD / (B) 3-Color | 800 × 480 / 880 × 528 | Monochrome / 3-Color Red | `epd7in5_V2` / `epd7in5b_V2` |
| **Waveshare** | Waveshare 5.83" / 5.65" (F) | 648 × 480 / 600 × 448 | Monochrome / 7-Color | `epd5in83` / `epd5in65f` |
| **Waveshare** | Waveshare 4.2" / 4.01" (F) | 400 × 300 / 640 × 400 | Monochrome, 3-Color, 7-Color | `epd4in2` / `epd4in01f` |
| **Waveshare** | Waveshare 2.9" / 2.7" / 2.13" / 1.54" | Various (e.g. 296×128, 250×122) | Monochrome, 3-Color Red/Yellow | `epd2in9`, `epd2in13_V3` |
| **Virtual** | Virtual / Mock Display | Dynamic (e.g. 800×480 or 1600×1200) | Full Color / Dithered PNG Preview | `mock_driver` |

---

## 🔌 Hardware & Connections

E-Paper HATs connect directly onto the Raspberry Pi 40-pin GPIO header:

```
Raspberry Pi 40-Pin Header
┌──────────────────────────────────────────────┐
│ (3.3V) (5V)   (GND)                          │
│  [Pin 1]   [Pin 2]                           │
│  ...                                         │
│  [Pin 19]  MOSI  ──────> E-Paper DIN / MOSI  │
│  [Pin 23]  SCLK  ──────> E-Paper CLK / SCLK  │
│  [Pin 24]  CE0   ──────> E-Paper CS          │
│  [Pin 22]  GPIO25 ─────> E-Paper D/C (Data)  │
│  [Pin 11]  GPIO17 ─────> E-Paper RST (Reset) │
│  [Pin 18]  GPIO24 ─────> E-Paper BUSY        │
│  [Pin 3]   SDA   ──────> Inky EEPROM (I2C)   │
│  [Pin 5]   SCL   ──────> Inky EEPROM (I2C)   │
└──────────────────────────────────────────────┘
```

* **Pimoroni Inky Impression 7.3" / wHAT / pHAT**: Simply slide the HAT directly onto the 40-pin GPIO header.
* **Waveshare 7.3" Color / 7.5" / 4.2" / 2.13"**: Mount the Waveshare e-Paper HAT directly onto the 40-pin header.
* **Waveshare 13.3" (IT8951)**: Connect the IT8951 e-Paper Driver HAT to the Pi 40-pin header and connect the ribbon cable to the 13.3" panel.

---

## 🚀 Installation Guide

### 1. Automated 1-Line Setup (Recommended)

1. Connect your Raspberry Pi to Wi-Fi and open a terminal via SSH:
   ```bash
   ssh pi@raspberrypi.local
   ```

2. Clone this repository:
   ```bash
   git clone https://github.com/neoplase/Epaper_Photo.git
   cd Epaper_Photo
   ```

3. Run the installer script:
   ```bash
   sudo bash install.sh
   ```

The script automatically:
* Enables **SPI** and **I2C** interfaces on the Raspberry Pi.
* Installs all system dependencies via `apt` (`python3-pil`, `python3-numpy`, `python3-spidev`, `python3-smbus`).
* Installs Pimoroni `inky` and Waveshare `waveshare-epd` drivers.
* Configures and starts the `epaper-frame.service` systemd background daemon.

Once complete, open your phone or computer browser at:
```
http://raspberrypi.local:5000
```
*(or `http://<your-pi-ip>:5000`)*

---

### 2. Manual Step-by-Step Installation

If you prefer to configure everything manually without the installer script:

1. **Enable Hardware Interfaces**:
   ```bash
   sudo raspi-config nonint do_spi 0
   sudo raspi-config nonint do_i2c 0
   ```

2. **Install System Dependencies**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3 python3-pip python3-pil python3-numpy python3-spidev python3-smbus git
   ```

3. **Install Python Packages**:
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Install Display Drivers**:
   * For Pimoroni Inky:
     ```bash
     pip3 install inky
     ```
   * For Waveshare:
     ```bash
     git clone --depth 1 https://github.com/waveshareteam/e-Paper.git /tmp/waveshare
     cp -r /tmp/waveshare/RaspberryPi_JetsonNano/python/lib/waveshare_epd ./
     rm -rf /tmp/waveshare
     ```

5. **Start the Hub**:
   ```bash
   python3 server/app.py
   ```

---

### 3. Auto-Start on Boot (Systemd Service)

To run the photo frame hub as a persistent background service that automatically launches when the Raspberry Pi boots:

1. Create the systemd service file:
   ```bash
   sudo nano /etc/systemd/system/epaper-frame.service
   ```

2. Paste the following configuration (replace `/home/pi/Epaper_Photo` with your actual path if different):
   ```ini
   [Unit]
   Description=Universal E-Paper Photo Frame Web Hub & Slideshow
   After=network.target network-online.target
   Wants=network-online.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/Epaper_Photo
   ExecStart=/usr/bin/python3 /home/pi/Epaper_Photo/server/app.py
   Restart=always
   RestartSec=5
   Environment=PYTHONUNBUFFERED=1

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable epaper-frame.service
   sudo systemctl start epaper-frame.service
   ```

4. Check service status and live logs:
   ```bash
   sudo systemctl status epaper-frame.service
   sudo journalctl -u epaper-frame.service -f
   ```

---

## 📱 Web GUI User Guide

Open `http://<your-pi-ip>:5000` on your smartphone, tablet, or PC to access the interface.

```
┌─────────────────────────────────────────────────────────────────┐
│ [Frame Icon] E-Paper Studio     [● Inky Impression 7.3" 800x480]│
├─────────────────────────────────────────────────────────────────┤
│ [Now Showing]  [Upload & Crop]  [Dither Studio]  [Gallery] [...]│
│                                                                 │
│  ┌───────────────────────────┐   ┌───────────────────────────┐  │
│  │ Virtual E-Paper Frame     │   │ Diagnostics & Schedule    │  │
│  │                           │   │ • Pi CPU Temp: 39.4°C     │  │
│  │                           │   │ • Storage Free: 14,210 MB │  │
│  │                           │   │ • Refresh: Every 60 mins  │  │
│  │ [● Screen Asleep (0W)]    │   │ • Next Update: 14:00      │  │
│  └───────────────────────────┘   └───────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Now Showing Dashboard
* **Live Frame Preview**: Shows the photo currently displayed on the e-paper screen.
* **Power & Sleep Indicator**: Confirms when the screen is in deep sleep (drawing zero power).
* **Pi Diagnostics**: Real-time Pi CPU temperature, available storage, and total photos in library.
* **Instant Refresh Controls**: "Next Photo" button triggers immediate screen refresh on demand.

### 2. Upload & Crop
* **Drag & Drop Upload**: Upload photos directly from your phone camera roll or computer (supports JPG, PNG, WEBP, BMP up to 32MB).
* **Locked Aspect Ratio Cropper**: The cropping box automatically matches the active screen's exact pixel dimensions (e.g. 800×480 for 7.3" or 1600×1200 for 13.3").
* **90° Rotate Button**: Rotate portrait or landscape photos to fit frame orientation.

### 3. Live Dither Studio (Client-Side Simulation)
* **Real-Time Canvas Dithering**: Floyd-Steinberg error diffusion renders instantly on your device's browser canvas.
* **Saturation Boost Slider (+0% to +150%)**: E-paper reflective pigments have lower saturation than illuminated phone screens; boost saturation to make colors pop.
* **Contrast & Brightness Sliders**: Fine-tune dynamic range to prevent dark shadows.
* **Palette Switcher**: Preview in 7-Color, 3-Color Red, 3-Color Yellow, Grayscale, or Monochrome.
* **Send to E-Paper Frame Now**: Sends the processed image to the physical screen immediately.

### 4. Gallery & Rotation Schedule
* **Photo Library Grid**: View all uploaded photos with metadata and thumbnails.
* **Manual Display**: Click "Display" on any card to push it immediately to the screen.
* **Slideshow Timer**: Adjust automatic rotation interval (from 5 minutes up to 12 hours).
* **Shuffle vs Sequential**: Toggle random shuffle or ordered playback.

### 5. Screen Profiles Catalog
* **Search & Filter**: Search by screen size (e.g. `7.3`, `13.3`), filter by brand (`Pimoroni` vs `Waveshare`), or color capability (`7-Color`, `Grayscale`, `Mono`).
* **1-Click Switching**: Click any screen card to activate it. The system automatically updates the crop tool, dithering palette, and loads the hardware driver.

---

## ⚙️ Configuration Reference

Settings are stored in [`config.json`](file:///c:/usr/Projects/Epaper_Photo/config.json) and can be modified via the Web GUI or edited directly:

```json
{
    "active_screen": "inky_impression_7_3",
    "slideshow_interval_minutes": 60,
    "slideshow_enabled": true,
    "slideshow_shuffle": true,
    "saturation": 1.3,
    "contrast": 1.15,
    "brightness": 1.05,
    "fit_mode": "cover",
    "deep_sleep_enabled": true
}
```

* `active_screen`: Active display ID from `core/screen_catalog.py` (e.g. `inky_impression_7_3`, `waveshare_13_3_k`, `waveshare_7_3_f`, `mock_7_3`).
* `slideshow_interval_minutes`: Time in minutes between automatic photo changes.
* `slideshow_enabled`: Enable or disable background rotation.
* `slideshow_shuffle`: Set `true` for random order, `false` for sequential.
* `saturation`: Default saturation multiplier (`1.0` = normal, `1.3` = recommended +30% boost).
* `contrast`: Default contrast multiplier (`1.15` = recommended +15% boost).
* `fit_mode`: Framing mode (`cover` = fill screen, `contain` = letterbox, `stretch`).
* `deep_sleep_enabled`: Powers down screen controller after refresh to eliminate DC voltage stress.

---

## 🌐 REST API Endpoints

The built-in Flask REST API allows integration with Home Assistant, Node-RED, or custom scripts:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/status` | Returns active screen, Pi CPU temp, storage, slideshow state, and current photo |
| `GET` | `/api/screens` | Returns all available screen profiles with filter query params (`brand`, `palette`) |
| `POST` | `/api/screen/select` | Switches active screen: `{"screen_id": "waveshare_13_3_k"}` |
| `POST` | `/api/upload` | Uploads photo multipart form (`photo`, optional `display_now=true`) |
| `GET` | `/api/photos` | Returns list of all stored photos with thumbnail URLs |
| `POST` | `/api/display/<filename>` | Immediately displays the specified photo file on the screen |
| `DELETE` | `/api/photo/<filename>` | Deletes photo and its thumbnail |
| `GET` | `/api/current-display` | Returns the latest rendered PNG image |
| `GET` / `POST`| `/api/settings` | Gets or updates configuration parameters |

---

## 💻 Local Development & PC Simulation

You can run and test the complete system on Windows, macOS, or Linux without physical hardware:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the local server:
   ```bash
   python server/app.py
   ```

3. Open `http://localhost:5000` in your browser.
   * If physical hardware is not detected, the system safely falls back to the **Virtual Mock Driver**.
   * Rendered frames are saved to `data/current_display.png` for instant visual inspection.

4. Run the automated test suite:
   ```bash
   pytest tests/test_all.py -v
   ```

---

## ❓ Troubleshooting & FAQs

### The screen is not refreshing or showing an error
* Ensure SPI and I2C are enabled in `/boot/config.txt` (or via `sudo raspi-config nonint do_spi 0`).
* Check that your user has permission to access GPIO and SPI:
  ```bash
  sudo usermod -a -G spi,i2c,gpio pi
  ```
* Verify pin connections: Inky and Waveshare HATs must be seated firmly onto all 40 GPIO pins.

### Colors look dull or dark on the 7-color e-paper
* E-paper does not emit light; it relies on reflected ambient light.
* In the **Dither Studio** tab, increase the **Saturation Boost** to `1.4x` - `1.6x` and **Brightness** to `1.10x` before sending the photo to the frame.

### Refresh takes 20-30 seconds with flashing
* This is normal behavior for multi-pigment e-paper displays (ACeP and Spectra 6). The particles require voltage pulses to migrate to the surface. Refreshing every 1 to 4 hours is recommended.

### Checking service logs
* View live output from the background slideshow daemon:
  ```bash
  sudo journalctl -u epaper-frame.service -f
  ```

---

## 📄 License

This project is open-source and released under the [MIT License](LICENSE).
Feel free to use, modify, and distribute it for personal and commercial photo frame projects!
