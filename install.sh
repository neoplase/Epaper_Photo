#!/usr/bin/env bash
# =========================================================================
# install.sh - Automated Installer for Universal E-Paper Photo Frame
# Compatible with Raspberry Pi Zero W v1.3 (ARMv6) and Pi Zero 2 W (ARMv8)
# =========================================================================

set -e

echo "========================================================"
echo "   E-Paper Photo Frame Hub - Raspberry Pi Installer    "
echo "========================================================"

# Detect root or sudo
if [ "$EUID" -ne 0 ]; then
  echo "[!] Please run as root or with sudo: sudo bash install.sh"
  exit 1
fi

CURRENT_USER=${SUDO_USER:-$(whoami)}
INSTALL_DIR=$(pwd)

echo "[*] Target Installation Directory: $INSTALL_DIR"
echo "[*] Running as User: $CURRENT_USER"

# 1. Enable Hardware Interfaces (SPI & I2C)
echo "[*] Enabling SPI and I2C hardware interfaces..."
if command -v raspi-config >/dev/null 2>&1; then
    raspi-config nonint do_spi 0
    raspi-config nonint do_i2c 0
    echo "[+] SPI and I2C enabled successfully."
else
    echo "[!] raspi-config not found. Please ensure SPI and I2C are enabled in /boot/config.txt"
fi

# 2. Update and install system dependencies via APT (compatible with Bullseye & Bookworm)
echo "[*] Updating apt package cache and installing system libraries..."
apt-get update -y
apt-get install -y \
    python3 \
    python3-pip \
    python3-pil \
    python3-numpy \
    python3-flask \
    python3-spidev \
    python3-smbus \
    python3-gpiozero \
    git \
    libopenjp2-7 \
    libjpeg-dev \
    zlib1g-dev

# 3. Install Python requirements
echo "[*] Installing Python packages..."
sudo -u "$CURRENT_USER" pip3 install -r requirements.txt --break-system-packages 2>/dev/null || \
sudo -u "$CURRENT_USER" pip3 install -r requirements.txt 2>/dev/null || true

# 4. Install Pimoroni Inky library
echo "[*] Installing Pimoroni Inky library..."
sudo -u "$CURRENT_USER" pip3 install inky --break-system-packages 2>/dev/null || \
sudo -u "$CURRENT_USER" pip3 install inky || true

# 5. Waveshare E-Paper library
echo "[*] Waveshare E-Paper drivers bundled and ready."
if [ -d "$INSTALL_DIR/waveshare_epd" ]; then
    chown -R "$CURRENT_USER:$CURRENT_USER" "$INSTALL_DIR/waveshare_epd"
    echo "[+] Bundled Waveshare drivers configured."
fi

# 6. Ensure data directories exist with proper ownership
echo "[*] Creating data and photo directories..."
mkdir -p "$INSTALL_DIR/data/photos" "$INSTALL_DIR/data/thumbs"
chown -R "$CURRENT_USER:$CURRENT_USER" "$INSTALL_DIR/data"

# 7. Create and install systemd service for auto-start
SERVICE_FILE="/etc/systemd/system/epaper-frame.service"
echo "[*] Installing systemd service at $SERVICE_FILE..."

cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=Universal E-Paper Photo Frame Web Hub & Slideshow
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/server/app.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable epaper-frame.service
systemctl restart epaper-frame.service

IP_ADDR=$(hostname -I | awk '{print $1}')

echo ""
echo "========================================================"
echo "   Installation Completed Successfully!                "
echo "========================================================"
echo " The E-Paper Photo Frame Hub service is now active."
echo ""
echo " Access the Web GUI from your phone or computer at:"
echo "   http://$IP_ADDR:5000"
echo "   or http://$(hostname).local:5000"
echo ""
echo " Check service logs with: sudo journalctl -u epaper-frame -f"
echo "========================================================"
