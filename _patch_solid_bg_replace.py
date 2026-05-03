"""Replace solid-color backgrounds on lazy PPTX slides with thematic backdrops.

The source PPTX uses solid colors (pink, black, white) on certain slides, leaving
the rendered JPG looking bare. This script:

1. Detects whether a slide is "lazy" — i.e. a single dominant color fills most
   of the canvas.
2. Generates a thematic backdrop for that character (procedural gradient with
   color choices that match the character's vibe — Atlantic fog for
   Corte-Real, dark sea for Drake, etc.).
3. Replaces the solid-color pixels with the backdrop while keeping the text /
   button boxes intact.
4. Saves the JPG back in place. The HTML doesn't change — it still references
   the same path.

Idempotent via a sidecar marker file: writes `.solid_bg_patched` next to a
fixed JPG so re-runs skip it.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SLIDES_ROOT = os.path.join(ROOT, "slides")

# Per-character backdrop palette — pairs of colors for a vertical gradient.
# Tuned to evoke the character's theme without being literal.
BACKDROPS = {
    "columbus":  [(35, 60, 95),   (70, 110, 150)],   # Spanish ocean blue
    "cortereal": [(70, 90, 110),  (130, 145, 160)],  # Foggy North Atlantic
    "dagama":    [(40, 80, 100),  (120, 100, 70)],   # Indian Ocean trade winds
    "drake":     [(20, 30, 50),   (60, 80, 110)],    # Stormy English night sea
    "magellan":  [(30, 50, 90),   (110, 130, 170)],  # Epic Pacific blue
    "narvaez":   [(60, 70, 50),   (130, 110, 70)],   # Florida swamp tan/olive
    "raleigh":   [(40, 50, 70),   (100, 90, 110)],   # Elizabethan dusk
    "analyzer":  [(15, 25, 40),   (40, 55, 80)],
}

# Lazy-slide detection threshold — a slide where >55% of pixels match the
# corner pixel within tolerance is "lazy" and gets a backdrop swap.
LAZY_DOMINANT_PCT = 0.55
COLOR_TOLERANCE = 30


def make_gradient_backdrop(width, height, top_rgb, bottom_rgb, seed=0):
    """Build a soft vertical gradient with a hint of horizontal noise so it
    doesn't look flat. Layered with a subtle vignette."""
    grad = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(top_rgb[0] * (1 - t) + bottom_rgb[0] * t)
        g = int(top_rgb[1] * (1 - t) + bottom_rgb[1] * t)
        b = int(top_rgb[2] * (1 - t) + bottom_rgb[2] * t)
        grad[y, :] = (r, g, b)

    # Add gentle noise for texture
    rng = np.random.default_rng(seed)
    noise = rng.integers(-12, 12, size=(height, width, 3), dtype=np.int16)
    out = np.clip(grad.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    img = Image.fromarray(out)
    # Soft vignette
    vignette = Image.new("L", (width, height), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse([(-width//4, -height//4), (width + width//4, height + height//4)],
               fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=min(width, height)//6))
    dark = Image.new("RGB", (width, height), (0, 0, 0))
    img = Image.composite(img, dark, vignette)
    return img


def is_lazy_slide(img_arr, corner_color, tolerance=COLOR_TOLERANCE):
    """Returns True if dominant solid color fills more than LAZY_DOMINANT_PCT
    of the slide."""
    diff = np.abs(img_arr.astype(np.int16) - np.array(corner_color, dtype=np.int16))
    mask = np.all(diff < tolerance, axis=2)
    return mask.mean() >= LAZY_DOMINANT_PCT, mask


def patch_slide(jpg_path, char_key):
    marker = jpg_path + ".solid_bg_patched"
    if os.path.exists(marker):
        return "SKIP (already patched)"

    img = Image.open(jpg_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # Sample multiple corner pixels — average to find dominant color
    corner_samples = [
        arr[5, 5], arr[5, w - 6], arr[h - 6, 5], arr[h - 6, w - 6],
    ]
    dominant = np.median(np.array(corner_samples), axis=0).astype(np.uint8)

    is_lazy, mask = is_lazy_slide(arr, dominant)
    if not is_lazy:
        return f"SKIP (not lazy — corner color={tuple(dominant)} fills only {mask.mean()*100:.0f}%)"

    # Generate themed backdrop
    palette = BACKDROPS.get(char_key, BACKDROPS["columbus"])
    backdrop = np.array(make_gradient_backdrop(w, h, palette[0], palette[1],
                                               seed=hash(jpg_path) & 0xFFFF))

    # Replace solid-color pixels with backdrop
    arr[mask] = backdrop[mask]
    Image.fromarray(arr).save(jpg_path, "JPEG", quality=85, optimize=True)

    # Drop marker
    open(marker, "w").write("ok")
    return f"OK (replaced {mask.mean()*100:.0f}% solid {tuple(dominant)} with {char_key} backdrop)"


def main():
    if not os.path.isdir(SLIDES_ROOT):
        print(f"FAIL  no slides/ folder at {SLIDES_ROOT}")
        return

    for char_dir in sorted(os.listdir(SLIDES_ROOT)):
        char_path = os.path.join(SLIDES_ROOT, char_dir)
        if not os.path.isdir(char_path):
            continue
        char_key = char_dir.lower()
        print(f"\n--- {char_dir} ---")
        for fname in sorted(os.listdir(char_path)):
            if not fname.lower().endswith(".jpg"):
                continue
            path = os.path.join(char_path, fname)
            try:
                result = patch_slide(path, char_key)
                # Only print interesting results
                if "OK" in result:
                    print(f"  {fname}: {result}")
                elif "SKIP (not lazy" in result and "fills 0%" not in result:
                    pass  # Don't spam non-lazy slides
            except Exception as e:
                print(f"  {fname}: ERR {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
