"""
app.py - Lightweight Flask Web Application & REST API for E-Paper Photo Frame.
Compatible with Raspberry Pi Zero W v1.3 (ARMv6) and Pi Zero 2 W (ARMv8).
"""

import os
import sys
import time
import shutil
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from werkzeug.utils import secure_filename
from PIL import Image

from core.config_manager import get_config, update_config
from core.screen_catalog import SCREEN_CATALOG, get_screen, list_screens
from core.driver_factory import get_driver
from core.slideshow import slideshow_daemon
from core.image_engine import process_image

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("epaper.server")

DATA_DIR = os.path.join(BASE_DIR, "data")
PHOTOS_DIR = os.path.join(DATA_DIR, "photos")
THUMBS_DIR = os.path.join(DATA_DIR, "thumbs")

os.makedirs(PHOTOS_DIR, exist_ok=True)
os.makedirs(THUMBS_DIR, exist_ok=True)

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "server", "templates"),
    static_folder=os.path.join(BASE_DIR, "server", "static")
)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32MB max upload

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_system_stats() -> dict:
    """Returns Pi CPU temperature, memory, and disk stats."""
    cpu_temp = None
    # Check Raspberry Pi thermal zone
    thermal_path = "/sys/class/thermal/thermal_zone0/temp"
    if os.path.exists(thermal_path):
        try:
            with open(thermal_path, "r") as f:
                cpu_temp = round(int(f.read().strip()) / 1000.0, 1)
        except Exception:
            pass

    # Disk usage
    disk_total_mb = 0
    disk_free_mb = 0
    try:
        total, used, free = shutil.disk_usage(BASE_DIR)
        disk_total_mb = round(total / (1024 * 1024))
        disk_free_mb = round(free / (1024 * 1024))
    except Exception:
        pass

    return {
        "cpu_temp": cpu_temp,
        "disk_free_mb": disk_free_mb,
        "disk_total_mb": disk_total_mb
    }

# =========================================================================
# WEB PAGES
# =========================================================================

@app.route("/")
def index():
    return render_template("index.html")

# =========================================================================
# API ENDPOINTS
# =========================================================================

@app.route("/api/status", methods=["GET"])
def api_status():
    config = get_config()
    screen_id = config.get("active_screen", "inky_impression_7_3")
    screen_info = get_screen(screen_id)
    system_stats = get_system_stats()

    return jsonify({
        "status": "online",
        "active_screen": screen_info,
        "current_photo": slideshow_daemon.current_photo,
        "current_photo_time": slideshow_daemon.current_photo_time,
        "next_refresh_time": slideshow_daemon.next_refresh_time,
        "is_refreshing": slideshow_daemon.is_refreshing,
        "slideshow_enabled": config.get("slideshow_enabled", True),
        "slideshow_interval_minutes": config.get("slideshow_interval_minutes", 60),
        "photo_count": len(slideshow_daemon.get_photos()),
        "system": system_stats
    })

@app.route("/api/screens", methods=["GET"])
def api_screens():
    brand = request.args.get("brand")
    palette = request.args.get("palette")
    size = request.args.get("size")
    screens = list_screens(brand=brand, palette_type=palette, size_category=size)
    return jsonify(screens)

@app.route("/api/screen/select", methods=["POST"])
def api_select_screen():
    data = request.get_json() or {}
    screen_id = data.get("screen_id")
    if not screen_id or screen_id not in SCREEN_CATALOG:
        return jsonify({"error": "Invalid screen_id"}), 400

    update_config({"active_screen": screen_id})
    # Force driver reload
    driver = get_driver(screen_id, force_refresh=True)
    screen_info = get_screen(screen_id)

    # If there's an existing displayed photo, re-render it for new screen dimensions
    if slideshow_daemon.current_photo:
        slideshow_daemon.trigger_next(slideshow_daemon.current_photo)

    return jsonify({
        "success": True,
        "active_screen": screen_info,
        "driver": driver.name
    })

@app.route("/api/photos", methods=["GET"])
def api_get_photos():
    files = slideshow_daemon.get_photos()
    items = []
    for f in files:
        full_path = os.path.join(PHOTOS_DIR, f)
        stats = os.stat(full_path)
        thumb_file = f"thumb_{f}"
        thumb_path = os.path.join(THUMBS_DIR, thumb_file)

        # Generate thumbnail on demand if missing
        if not os.path.exists(thumb_path):
            try:
                with Image.open(full_path) as img:
                    img.thumbnail((320, 240))
                    img.save(thumb_path, "JPEG", quality=85)
            except Exception as e:
                logger.warning(f"Could not make thumbnail for {f}: {e}")

        items.append({
            "filename": f,
            "size_kb": round(stats.st_size / 1024, 1),
            "upload_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
            "url": f"/photos/{f}",
            "thumb_url": f"/thumbs/{thumb_file}" if os.path.exists(thumb_path) else f"/photos/{f}",
            "is_current": (f == slideshow_daemon.current_photo)
        })

    return jsonify(items)

@app.route("/api/upload", methods=["POST"])
def api_upload():
    if "photo" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["photo"]
    if file.filename == "" or not allowed_file(file.filename):
        return jsonify({"error": "Invalid image file type"}), 400

    sec_name = secure_filename(file.filename)
    timestamp = int(time.time())
    final_filename = f"{timestamp}_{sec_name}"
    save_path = os.path.join(PHOTOS_DIR, final_filename)

    file.save(save_path)
    logger.info(f"Saved uploaded image to {save_path}")

    # Generate thumbnail
    thumb_path = os.path.join(THUMBS_DIR, f"thumb_{final_filename}")
    try:
        with Image.open(save_path) as img:
            img.thumbnail((320, 240))
            img.save(thumb_path, "JPEG", quality=85)
    except Exception as e:
        logger.warning(f"Failed to generate thumbnail: {e}")

    # Optional: Display immediately if requested
    display_now = request.form.get("display_now", "false").lower() == "true"
    if display_now:
        slideshow_daemon.trigger_next(final_filename)

    return jsonify({
        "success": True,
        "filename": final_filename,
        "url": f"/photos/{final_filename}"
    })

@app.route("/api/display/<filename>", methods=["POST"])
def api_display_photo(filename):
    if not os.path.exists(os.path.join(PHOTOS_DIR, filename)):
        return jsonify({"error": "Photo not found"}), 404

    success = slideshow_daemon._display_single_photo(filename)
    return jsonify({"success": success, "current_photo": filename})

@app.route("/api/photo/<filename>", methods=["DELETE"])
def api_delete_photo(filename):
    photo_path = os.path.join(PHOTOS_DIR, filename)
    thumb_path = os.path.join(THUMBS_DIR, f"thumb_{filename}")

    if os.path.exists(photo_path):
        os.remove(photo_path)
    if os.path.exists(thumb_path):
        os.remove(thumb_path)

    return jsonify({"success": True})

@app.route("/api/settings", methods=["GET", "POST"])
def api_settings():
    if request.method == "POST":
        new_settings = request.get_json() or {}
        updated = update_config(new_settings)
        # If slideshow settings changed, wake daemon
        slideshow_daemon._wake_event.set()
        return jsonify({"success": True, "settings": updated})
    return jsonify(get_config())

@app.route("/api/current-display", methods=["GET"])
def api_current_display():
    """Serves the latest rendered image for the active screen."""
    display_path = os.path.join(DATA_DIR, "current_display.png")
    if os.path.exists(display_path):
        return send_file(display_path, mimetype="image/png")
    # Return placeholder if not yet rendered
    config = get_config()
    screen = get_screen(config.get("active_screen", "inky_impression_7_3"))
    img = Image.new("RGB", (screen["width"], screen["height"]), (240, 240, 240))
    img.save(display_path)
    return send_file(display_path, mimetype="image/png")

# File Serving routes
@app.route("/photos/<path:filename>")
def serve_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)

@app.route("/thumbs/<path:filename>")
def serve_thumb(filename):
    return send_from_directory(THUMBS_DIR, filename)

def run_server(host="0.0.0.0", port=5000, debug=False):
    slideshow_daemon.start()
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_server()
