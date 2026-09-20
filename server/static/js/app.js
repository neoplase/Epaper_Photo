/**
 * app.js - Main Client-Side Controller for E-Paper Photo Studio.
 */

let activeScreen = null;
let allScreens = [];
let cropper = null;
let currentSourceCanvas = null; // Un-dithered cropped canvas cache
let ditherDebounceTimer = null;

// =========================================================================
// Initialization
// =========================================================================

document.addEventListener("DOMContentLoaded", () => {
    initDropzone();
    loadStatus();
    loadScreens();
    loadGallery();

    // Poll status every 8 seconds
    setInterval(loadStatus, 8000);
});

// =========================================================================
// Navigation / Tab Switching
// =========================================================================

function switchTab(tabId) {
    document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
    document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

    const targetTab = document.getElementById(tabId);
    if (targetTab) targetTab.classList.add("active");

    const targetBtn = document.getElementById("btn-" + tabId);
    if (targetBtn) targetBtn.classList.add("active");

    if (tabId === "tab-gallery") {
        loadGallery();
    } else if (tabId === "tab-frame") {
        refreshDisplayImage();
    }
}

// =========================================================================
// Status & Diagnostics
// =========================================================================

async function loadStatus() {
    try {
        const res = await fetch("/api/status");
        if (!res.ok) return;
        const data = await res.json();

        activeScreen = data.active_screen;

        // Update Header Badge
        document.getElementById("headerScreenName").textContent = activeScreen.model_name;
        document.getElementById("headerScreenRes").textContent = `(${activeScreen.width}x${activeScreen.height})`;

        // Update Aspect description in crop tab
        const cropDesc = document.getElementById("cropAspectDesc");
        if (cropDesc) {
            cropDesc.textContent = `Aspect ratio locked to ${activeScreen.width}x${activeScreen.height} (${activeScreen.model_name})`;
        }

        // Diagnostics
        const tempEl = document.getElementById("statCpuTemp");
        if (tempEl) tempEl.textContent = data.system.cpu_temp !== null ? `${data.system.cpu_temp}°C` : "N/A";

        const diskEl = document.getElementById("statDiskFree");
        if (diskEl) diskEl.textContent = `${data.system.disk_free_mb} MB`;

        const photoCountEl = document.getElementById("statPhotoCount");
        if (photoCountEl) photoCountEl.textContent = data.photo_count;

        // Schedule info
        const checkEl = document.getElementById("slideshowEnabledCheck");
        if (checkEl) checkEl.checked = data.slideshow_enabled;

        const intervalRange = document.getElementById("intervalRange");
        const intervalText = document.getElementById("intervalValText");
        if (intervalRange && !intervalRange.matches(':active')) {
            intervalRange.value = data.slideshow_interval_minutes;
            if (intervalText) intervalText.textContent = `${data.slideshow_interval_minutes} mins`;
        }

        const lastUpdatedEl = document.getElementById("lastUpdatedText");
        if (lastUpdatedEl) lastUpdatedEl.textContent = data.current_photo_time || "None";

        const nextRefreshEl = document.getElementById("nextRefreshText");
        if (nextRefreshEl) nextRefreshEl.textContent = data.next_refresh_time || "Paused";

        // Frame status overlay
        const overlay = document.getElementById("frameOverlayStatus");
        if (overlay) {
            if (data.is_refreshing) {
                overlay.innerHTML = '<span class="status-dot" style="background: #f59e0b; box-shadow: 0 0 8px #f59e0b;"></span> Refreshing Display...';
            } else {
                overlay.innerHTML = '<span class="status-dot"></span> Screen Asleep (0W Power)';
            }
        }

    } catch (err) {
        console.error("Status load error:", err);
    }
}

function refreshDisplayImage() {
    const img = document.getElementById("activeFrameImg");
    if (img) {
        img.src = `/api/current-display?t=${Date.now()}`;
    }
}

async function triggerNextPhoto() {
    const overlay = document.getElementById("frameOverlayStatus");
    if (overlay) overlay.textContent = "Triggering next photo...";
    try {
        await fetch("/api/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({}) // triggers daemon wake
        });
        setTimeout(refreshDisplayImage, 1500);
    } catch (e) {
        console.error(e);
    }
}

async function toggleSlideshowEnabled(enabled) {
    await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slideshow_enabled: enabled })
    });
    loadStatus();
}

async function updateIntervalSetting(minutes) {
    await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ slideshow_interval_minutes: parseInt(minutes) })
    });
    loadStatus();
}

// =========================================================================
// Screen Catalog & Selection
// =========================================================================

async function loadScreens() {
    try {
        const res = await fetch("/api/screens");
        allScreens = await res.json();
        renderScreenCatalog();
    } catch (e) {
        console.error("Failed to load screens:", e);
    }
}

function renderScreenCatalog() {
    const grid = document.getElementById("screenCardsGrid");
    if (!grid) return;

    const brand = document.getElementById("screenBrandFilter").value;
    const palette = document.getElementById("screenPaletteFilter").value;
    const search = document.getElementById("screenSearchInput").value.toLowerCase().trim();

    const filtered = allScreens.filter(s => {
        if (brand !== "all" && s.brand.toLowerCase() !== brand.toLowerCase()) return false;
        if (palette !== "all" && s.palette_type.toLowerCase() !== palette.toLowerCase()) return false;
        if (search) {
            const haystack = `${s.model_name} ${s.brand} ${s.width}x${s.height} ${s.colors_desc} ${s.notes}`.toLowerCase();
            if (!haystack.includes(search)) return false;
        }
        return true;
    });

    grid.innerHTML = filtered.map(screen => {
        const isActive = activeScreen && activeScreen.id === screen.id;
        const brandBadgeClass = screen.brand === "Pimoroni" ? "badge-pimoroni" : (screen.brand === "Waveshare" ? "badge-waveshare" : "badge-virtual");
        
        return `
            <div class="screen-item-card ${isActive ? 'active' : ''}" onclick="selectScreen('${screen.id}')">
                <div class="screen-item-header">
                    <div class="screen-item-title">${screen.model_name}</div>
                    <span class="badge-tag ${brandBadgeClass}">${screen.brand}</span>
                </div>
                <div class="screen-item-meta">
                    <div><strong>Resolution:</strong> ${screen.width} × ${screen.height} px</div>
                    <div><strong>Palette:</strong> ${screen.colors_desc}</div>
                    <div style="margin-top: 0.35rem; font-size: 0.75rem; color: var(--text-dim);">${screen.notes || ''}</div>
                </div>
                <div class="screen-item-tags">
                    <span class="badge-tag" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">${screen.palette_type.toUpperCase()}</span>
                    <span class="badge-tag" style="background: rgba(255,255,255,0.06); color: var(--text-muted);">${screen.size_category}</span>
                    ${isActive ? '<span class="badge-tag" style="background: var(--accent-amber); color: #000; font-weight: 700; margin-left: auto;">ACTIVE</span>' : ''}
                </div>
            </div>
        `;
    }).join("");
}

async function selectScreen(screenId) {
    try {
        const res = await fetch("/api/screen/select", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ screen_id: screenId })
        });
        const data = await res.json();
        if (data.success) {
            activeScreen = data.active_screen;
            renderScreenCatalog();
            loadStatus();

            // If cropper is open, update its aspect ratio
            if (cropper) {
                cropper.setAspectRatio(activeScreen.width / activeScreen.height);
            }

            alert(`Active display switched to: ${activeScreen.model_name} (${activeScreen.width}x${activeScreen.height})`);
        }
    } catch (e) {
        console.error("Screen select failed:", e);
    }
}

// =========================================================================
// Image Upload & Interactive Cropper
// =========================================================================

function initDropzone() {
    const dropzone = document.getElementById("dropzone");
    if (!dropzone) return;

    ['dragenter', 'dragover'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
            e.preventDefault();
            dropzone.classList.add("drag-over");
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
            e.preventDefault();
            dropzone.classList.remove("drag-over");
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            loadImageForCrop(files[0]);
        }
    });
}

function handleFileSelect(event) {
    const files = event.target.files;
    if (files.length > 0) {
        loadImageForCrop(files[0]);
    }
}

function loadImageForCrop(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = document.getElementById("cropperImage");
        const placeholder = document.getElementById("cropperPlaceholder");
        img.src = e.target.result;
        img.style.display = "block";
        if (placeholder) placeholder.style.display = "none";

        if (cropper) {
            cropper.destroy();
        }

        const aspect = activeScreen ? (activeScreen.width / activeScreen.height) : (800 / 480);
        cropper = new Cropper(img, {
            aspectRatio: aspect,
            viewMode: 2,
            autoCropArea: 1,
            responsive: true,
            background: false
        });

        document.getElementById("btnGoToDither").disabled = false;
    };
    reader.readAsDataURL(file);
}

function rotateCropper() {
    if (cropper) {
        cropper.rotate(90);
    }
}

function proceedToDitherStudio() {
    if (!cropper) return;

    const targetW = activeScreen ? activeScreen.width : 800;
    const targetH = activeScreen ? activeScreen.height : 480;

    // Get cropped canvas scaled to screen resolution
    currentSourceCanvas = cropper.getCroppedCanvas({
        width: targetW,
        height: targetH,
        imageSmoothingEnabled: true,
        imageSmoothingQuality: "high"
    });

    switchTab("tab-dither");

    // Update dither mode title
    const paletteType = getEffectivePaletteType();
    document.getElementById("ditherModeTitle").textContent = 
        `Simulating ${activeScreen.model_name} (${paletteType.toUpperCase()} Palette, ${targetW}x${targetH})`;

    renderLiveDitherPreview();
}

// =========================================================================
// Client-Side Dither Simulation (Canvas Floyd-Steinberg)
// =========================================================================

function getEffectivePaletteType() {
    const override = document.getElementById("selectPaletteOverride").value;
    if (override && override !== "auto") return override;
    return activeScreen ? activeScreen.palette_type : "7color";
}

function onAdjustmentSliderChange() {
    const sat = parseFloat(document.getElementById("sliderSaturation").value);
    const ct = parseFloat(document.getElementById("sliderContrast").value);
    const br = parseFloat(document.getElementById("sliderBrightness").value);

    document.getElementById("valSaturation").textContent = `${sat.toFixed(2)}x`;
    document.getElementById("valContrast").textContent = `${ct.toFixed(2)}x`;
    document.getElementById("valBrightness").textContent = `${br.toFixed(2)}x`;

    clearTimeout(ditherDebounceTimer);
    ditherDebounceTimer = setTimeout(renderLiveDitherPreview, 60);
}

function renderLiveDitherPreview() {
    if (!currentSourceCanvas) return;

    const canvas = document.getElementById("ditherCanvas");
    canvas.width = currentSourceCanvas.width;
    canvas.height = currentSourceCanvas.height;

    const ctx = canvas.getContext("2d");
    // Draw clean cropped source first
    ctx.drawImage(currentSourceCanvas, 0, 0);

    const sat = parseFloat(document.getElementById("sliderSaturation").value);
    const ct = parseFloat(document.getElementById("sliderContrast").value);
    const br = parseFloat(document.getElementById("sliderBrightness").value);
    const paletteType = getEffectivePaletteType();

    // Run client-side dithering simulation
    simulateEInkDithering(canvas, paletteType, {
        saturation: sat,
        contrast: ct,
        brightness: br
    });
}

// =========================================================================
// Pushing to E-Paper & Library
// =========================================================================

async function pushDitheredToFrame() {
    const canvas = document.getElementById("ditherCanvas");
    const btn = document.getElementById("btnPushToFrame");
    btn.disabled = true;
    btn.innerHTML = '<span class="status-dot" style="background: #000;"></span> Sending to Frame...';

    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("photo", blob, "studio_photo.png");
        formData.append("display_now", "true");

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (data.success) {
                switchTab("tab-frame");
                setTimeout(refreshDisplayImage, 1000);
            } else {
                alert("Upload failed: " + (data.error || "Unknown error"));
            }
        } catch (e) {
            console.error("Push to frame error:", e);
            alert("Error sending photo to frame.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14"/><path d="M12 5l7 7-7 7"/></svg> Send to E-Paper Frame Now';
        }
    }, "image/png");
}

async function saveToGalleryOnly() {
    const canvas = document.getElementById("ditherCanvas");
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append("photo", blob, "photo.png");
        formData.append("display_now", "false");

        try {
            const res = await fetch("/api/upload", { method: "POST", body: formData });
            const data = await res.json();
            if (data.success) {
                alert("Photo saved to library successfully!");
                switchTab("tab-gallery");
            }
        } catch (e) {
            console.error(e);
        }
    }, "image/png");
}

// =========================================================================
// Gallery Management
// =========================================================================

async function loadGallery() {
    const container = document.getElementById("galleryContainer");
    if (!container) return;

    try {
        const res = await fetch("/api/photos");
        const photos = await res.json();

        if (photos.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-dim);">
                    No photos in library yet. Click "+ Upload Photo" to add your first photo!
                </div>
            `;
            return;
        }

        container.innerHTML = photos.map(p => `
            <div class="gallery-card ${p.is_current ? 'current-active' : ''}">
                <img src="${p.thumb_url}" class="gallery-thumb" alt="${p.filename}">
                <div class="gallery-info">
                    <div class="gallery-name" title="${p.filename}">${p.filename}</div>
                    <div style="font-size: 0.75rem; color: var(--text-dim);">${p.size_kb} KB • ${p.upload_time}</div>
                    <div class="gallery-actions">
                        <button class="btn btn-primary" onclick="displayPhoto('${p.filename}')" style="flex: 1; padding: 0.4rem 0.6rem; font-size: 0.78rem;">
                            ${p.is_current ? 'Showing' : 'Display'}
                        </button>
                        <button class="btn btn-danger" onclick="deletePhoto('${p.filename}')" style="padding: 0.4rem 0.6rem; font-size: 0.78rem;">
                            Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join("");
    } catch (e) {
        console.error("Gallery load error:", e);
    }
}

async function displayPhoto(filename) {
    try {
        const res = await fetch(`/api/display/${filename}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
            switchTab("tab-frame");
            setTimeout(refreshDisplayImage, 1000);
        }
    } catch (e) {
        console.error("Display photo error:", e);
    }
}

async function deletePhoto(filename) {
    if (!confirm(`Delete ${filename}?`)) return;
    try {
        await fetch(`/api/photo/${filename}`, { method: "DELETE" });
        loadGallery();
        loadStatus();
    } catch (e) {
        console.error("Delete photo error:", e);
    }
}
