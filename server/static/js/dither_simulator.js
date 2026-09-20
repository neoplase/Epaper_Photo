/**
 * dither_simulator.js - Pure JavaScript Floyd-Steinberg Dithering Simulator.
 * Runs instantly in the client browser to preview e-paper appearance without burdening the Pi Zero.
 */

const EInkPalettes = {
    // 7-Color ACeP / Spectra 6
    "7color": [
        [0, 0, 0],         // Black
        [255, 255, 255],   // White
        [0, 160, 50],      // Green
        [0, 60, 200],      // Blue
        [220, 25, 25],     // Red
        [255, 225, 0],     // Yellow
        [255, 120, 0]      // Orange
    ],

    // 3-Color Red (Black, White, Red)
    "bwr": [
        [0, 0, 0],         // Black
        [255, 255, 255],   // White
        [220, 20, 20]      // Red
    ],

    // 3-Color Yellow (Black, White, Yellow)
    "bwy": [
        [0, 0, 0],         // Black
        [255, 255, 255],   // White
        [255, 220, 0]      // Yellow
    ],

    // 4-Color (Black, White, Yellow, Red) for Waveshare 7.3 (G)
    "4color": [
        [0, 0, 0],         // Black
        [255, 255, 255],   // White
        [255, 255, 0],     // Yellow
        [255, 0, 0]        // Red
    ],

    // Spectra 6 (Black, White, Yellow, Red, Blue, Green) for Waveshare 7.3 (E)
    "spectra6": [
        [0, 0, 0],         // Black
        [255, 255, 255],   // White
        [255, 255, 0],     // Yellow
        [255, 0, 0],       // Red
        [0, 0, 255],       // Blue
        [0, 255, 0]        // Green
    ],

    // 1-Bit Monochrome
    "mono": [
        [0, 0, 0],         // Black
        [255, 255, 255]    // White
    ],

    // 16-Level Grayscale
    "grayscale16": (function() {
        const pal = [];
        for (let i = 0; i < 16; i++) {
            const v = Math.round(i * 255 / 15);
            pal.push([v, v, v]);
        }
        return pal;
    })()
};

/**
 * Finds the closest RGB color in the target palette using Euclidean distance in weighted RGB space.
 */
function findClosestColor(r, g, b, palette) {
    let bestDist = Infinity;
    let bestColor = palette[0];

    for (let i = 0; i < palette.length; i++) {
        const pr = palette[i][0];
        const pg = palette[i][1];
        const pb = palette[i][2];

        // Human eye perception weighting: 0.3 R, 0.59 G, 0.11 B
        const dr = (r - pr) * 0.30;
        const dg = (g - pg) * 0.59;
        const db = (b - pb) * 0.11;
        const dist = dr * dr + dg * dg + db * db;

        if (dist < bestDist) {
            bestDist = dist;
            bestColor = palette[i];
        }
    }
    return bestColor;
}

/**
 * Applies color enhancement (brightness, contrast, saturation) to ImageData in-place.
 */
function applyColorEnhancements(data, width, height, brightness = 1.05, contrast = 1.15, saturation = 1.3) {
    const len = width * height * 4;
    const factor = (259 * (contrast * 255 - 255 + 255)) / (255 * (259 - (contrast * 255 - 255)));

    for (let i = 0; i < len; i += 4) {
        let r = data[i];
        let g = data[i + 1];
        let b = data[i + 2];

        // 1. Brightness
        r = r * brightness;
        g = g * brightness;
        b = b * brightness;

        // 2. Contrast
        r = factor * (r - 128) + 128;
        g = factor * (g - 128) + 128;
        b = factor * (b - 128) + 128;

        // 3. Saturation
        const gray = 0.2989 * r + 0.5870 * g + 0.1140 * b;
        r = gray + saturation * (r - gray);
        g = gray + saturation * (g - gray);
        b = gray + saturation * (b - gray);

        // Clamp
        data[i] = Math.max(0, Math.min(255, r));
        data[i + 1] = Math.max(0, Math.min(255, g));
        data[i + 2] = Math.max(0, Math.min(255, b));
    }
}

/**
 * Runs Floyd-Steinberg Error Diffusion Dithering over an HTML5 Canvas.
 * @param {HTMLCanvasElement} canvas
 * @param {string} paletteType - '7color', 'bwr', 'bwy', 'grayscale16', or 'mono'
 * @param {object} adjustments - { brightness, contrast, saturation }
 */
function simulateEInkDithering(canvas, paletteType = "7color", adjustments = {}) {
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    const imgData = ctx.getImageData(0, 0, width, height);
    const data = imgData.data;

    // Apply color boosts first
    const br = adjustments.brightness !== undefined ? adjustments.brightness : 1.05;
    const ct = adjustments.contrast !== undefined ? adjustments.contrast : 1.15;
    const sat = adjustments.saturation !== undefined ? adjustments.saturation : 1.30;
    applyColorEnhancements(data, width, height, br, ct, sat);

    const palette = EInkPalettes[paletteType] || EInkPalettes["7color"];

    // Floyd-Steinberg error diffusion
    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const idx = (y * width + x) * 4;
            const oldR = data[idx];
            const oldG = data[idx + 1];
            const oldB = data[idx + 2];

            const [newR, newG, newB] = findClosestColor(oldR, oldG, oldB, palette);

            data[idx] = newR;
            data[idx + 1] = newG;
            data[idx + 2] = newB;

            const errR = oldR - newR;
            const errG = oldG - newG;
            const errB = oldB - newB;

            // Distribute error to neighbors:
            // (x+1, y)   += 7/16
            // (x-1, y+1) += 3/16
            // (x,   y+1) += 5/16
            // (x+1, y+1) += 1/16
            if (x + 1 < width) {
                const i = (y * width + (x + 1)) * 4;
                data[i]     += (errR * 7) >> 4;
                data[i + 1] += (errG * 7) >> 4;
                data[i + 2] += (errB * 7) >> 4;
            }
            if (y + 1 < height) {
                if (x - 1 >= 0) {
                    const i = ((y + 1) * width + (x - 1)) * 4;
                    data[i]     += (errR * 3) >> 4;
                    data[i + 1] += (errG * 3) >> 4;
                    data[i + 2] += (errB * 3) >> 4;
                }
                const i = ((y + 1) * width + x) * 4;
                data[i]     += (errR * 5) >> 4;
                data[i + 1] += (errG * 5) >> 4;
                data[i + 2] += (errB * 5) >> 4;

                if (x + 1 < width) {
                    const i = ((y + 1) * width + (x + 1)) * 4;
                    data[i]     += (errR * 1) >> 4;
                    data[i + 1] += (errG * 1) >> 4;
                    data[i + 2] += (errB * 1) >> 4;
                }
            }
        }
    }

    ctx.putImageData(imgData, 0, 0);
}
