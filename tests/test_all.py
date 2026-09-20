"""
test_all.py - Automated Test Suite for E-Paper Photo Frame Hub.
Verifies catalog integrity, image processing pipeline, driver switching, and REST API endpoints.
"""

import os
import sys
import io

# Ensure workspace root is in python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from PIL import Image
from core.screen_catalog import SCREEN_CATALOG, get_screen, list_screens
from core.image_engine import process_image, dither_for_palette, crop_and_resize, enhance_colors
from core.driver_factory import get_driver
from core.config_manager import get_config, update_config
from server.app import app

# =========================================================================
# 1. Screen Catalog Tests
# =========================================================================

def test_screen_catalog_structure():
    assert len(SCREEN_CATALOG) >= 20, f"Expected at least 20 screens, got {len(SCREEN_CATALOG)}"

    valid_palettes = {"7color", "bwr", "bwy", "grayscale16", "mono", "4color", "spectra6"}
    valid_drivers = {"inky", "waveshare", "mock"}

    for screen_id, s in SCREEN_CATALOG.items():
        assert s["id"] == screen_id
        assert s["width"] > 0
        assert s["height"] > 0
        assert s["palette_type"] in valid_palettes, f"Invalid palette: {s['palette_type']} in {screen_id}"
        assert s["driver_type"] in valid_drivers, f"Invalid driver: {s['driver_type']} in {screen_id}"
        assert len(s["model_name"]) > 0

def test_screen_filtering():
    pimoroni_screens = list_screens(brand="Pimoroni")
    assert len(pimoroni_screens) >= 7
    for s in pimoroni_screens:
        assert s["brand"] == "Pimoroni"

    waveshare_screens = list_screens(brand="Waveshare")
    assert len(waveshare_screens) >= 12
    for s in waveshare_screens:
        assert s["brand"] == "Waveshare"

    large_screens = list_screens(size_category="large")
    assert len(large_screens) >= 5
    for s in large_screens:
        assert s["size_category"] == "large"

# =========================================================================
# 2. Image Processing & Dithering Tests
# =========================================================================

def test_image_resizing_and_framing():
    # Create test 1920x1080 image
    src = Image.new("RGB", (1920, 1080), (100, 150, 200))
    # Target 7.3" screen (800x480)
    out_cover = crop_and_resize(src, 800, 480, fit_mode="cover")
    assert out_cover.size == (800, 480)

    # Target 13.3" screen (1600x1200)
    out_13_3 = crop_and_resize(src, 1600, 1200, fit_mode="contain")
    assert out_13_3.size == (1600, 1200)

def test_dithering_palettes():
    src = Image.new("RGB", (100, 100), (180, 50, 50))

    # Test 7-color
    d7 = dither_for_palette(src, "7color")
    assert d7.size == (100, 100)
    assert d7.mode == "RGB"

    # Test 4-color (Waveshare 7.3 G)
    d4 = dither_for_palette(src, "4color")
    assert d4.size == (100, 100)
    assert d4.mode == "RGB"

    # Test Spectra 6 (Waveshare 7.3 E)
    ds6 = dither_for_palette(src, "spectra6")
    assert ds6.size == (100, 100)
    assert ds6.mode == "RGB"

    # Test BWR
    dbwr = dither_for_palette(src, "bwr")
    assert dbwr.size == (100, 100)

    # Test BWY
    dbwy = dither_for_palette(src, "bwy")
    assert dbwy.size == (100, 100)

    # Test Grayscale 16
    dgray = dither_for_palette(src, "grayscale16")
    assert dgray.size == (100, 100)

    # Test Mono
    dmono = dither_for_palette(src, "mono")
    assert dmono.size == (100, 100)

def test_full_pipeline_process_image():
    src = Image.new("RGB", (1000, 800), (220, 180, 60))
    result = process_image(
        src,
        target_width=800,
        target_height=480,
        palette_type="7color",
        saturation=1.4,
        contrast=1.2,
        brightness=1.05
    )
    assert result.size == (800, 480)
    assert result.mode == "RGB"

# =========================================================================
# 3. Driver Switching & Fallback Tests
# =========================================================================

def test_driver_switching():
    # Switching to Inky 7.3" (falls back to mock safely if not on Pi)
    d_inky = get_driver("inky_impression_7_3", force_refresh=True)
    assert d_inky is not None
    assert d_inky.width == 800
    assert d_inky.height == 480

    # Switching to Waveshare 13.3"
    d_ws = get_driver("waveshare_13_3_k", force_refresh=True)
    assert d_ws is not None
    assert d_ws.width == 1600
    assert d_ws.height == 1200

# =========================================================================
# 4. REST API Endpoint Tests
# =========================================================================

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_api_status(client):
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "online"
    assert "active_screen" in data
    assert "system" in data

def test_api_screens(client):
    res = client.get("/api/screens")
    assert res.status_code == 200
    screens = res.get_json()
    assert len(screens) >= 20

def test_api_screen_selection(client):
    res = client.post("/api/screen/select", json={"screen_id": "waveshare_13_3_k"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["active_screen"]["id"] == "waveshare_13_3_k"
    assert data["active_screen"]["width"] == 1600

    # Switch back to Inky 7.3"
    res2 = client.post("/api/screen/select", json={"screen_id": "inky_impression_7_3"})
    assert res2.status_code == 200
    assert res2.get_json()["active_screen"]["id"] == "inky_impression_7_3"

def test_api_upload_and_display(client):
    # Generate test image in memory
    img_byte_arr = io.BytesIO()
    test_img = Image.new("RGB", (400, 300), (255, 100, 50))
    test_img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Upload with display_now=true
    res = client.post(
        "/api/upload",
        data={
            "photo": (img_byte_arr, "test_upload.png"),
            "display_now": "true"
        },
        content_type="multipart/form-data"
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "filename" in data

    # Verify photo appears in /api/photos
    res_photos = client.get("/api/photos")
    assert res_photos.status_code == 200
    photos = res_photos.get_json()
    assert any(p["filename"] == data["filename"] for p in photos)

    # Verify current display image endpoint returns valid PNG
    res_display = client.get("/api/current-display")
    assert res_display.status_code == 200
    assert res_display.mimetype == "image/png"

    # Cleanup uploaded test file
    res_del = client.delete(f"/api/photo/{data['filename']}")
    assert res_del.status_code == 200
