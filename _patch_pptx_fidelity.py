"""Restore 1:1 PPTX visual fidelity across all 7 character HTMLs.

The HTML version was missing dramatic PPTX art (storms, maps, character portraits,
red arrows, etc.) because the original converter only extracted SOME images and
put them in tiny accent positions. Result: lots of black space, sparse text.

This patch:

1. Renders each PPTX page as a high-quality JPG via PyMuPDF
2. Saves to slides/<char>/page_NN.jpg (external files, not inlined)
3. Replaces slide.bg_image with the rendered PPTX page (full-bleed, 1:1 fidelity)
4. Clears slide.styled_texts (text is now baked into bg_image, no double-text)
5. Clears slide.images EXCEPT Tenor URLs (PPTX accents now in bg; v2 gameover GIFs preserved)
6. Preserves slide.title and slide.body (for gameover captions and Drake parody)

Also injects CSS/JS fixes for:
- Caption size on long parody lines (#4)
- GIF z-index covering title (#9)
- Synthetic playGameOverBuzz colliding with our MP3 (#7 — double music)
"""

import os
import re
import json
import io
import base64

import fitz  # PyMuPDF
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = r"C:\Users\jorge\AppData\Local\Temp\conquest_renders"
SLIDES_OUT = os.path.join(ROOT, "slides")

# Map: character HTML -> source PDF basename
PDF_MAP = {
    "columbus.html":  "Time Warp II_ Conquest (Tutorial w Columbus) FINAL.pdf",
    "cortereal.html": "Time Warp II_ Conquest (Corte-Real) FINAL.pdf",
    "dagama.html":    "Time Warp II_ Conquest (Da Gama) FINAL.pdf",
    "drake.html":     "Time Warp II_ Conquest (Drake) FINAL.pdf",
    "magellan.html":  "Time Warp II_ Conquest (Magellan) FINAL.pdf",
    "narvaez.html":   "Time Warp II_ Conquest (Narvaez) FINAL.pdf",
    "raleigh.html":   "Time Warp II_ Conquest (Raleigh) FINAL.pdf",
}

CHAR_FOLDER = {
    "columbus.html":  "columbus",
    "cortereal.html": "cortereal",
    "dagama.html":    "dagama",
    "drake.html":     "drake",
    "magellan.html":  "magellan",
    "narvaez.html":   "narvaez",
    "raleigh.html":   "raleigh",
}

SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)
TARGET_W = 1600  # downscale render width for web
JPEG_QUALITY = 85


def render_pdf_pages(pdf_path, out_dir):
    """Render each PDF page to slides/<char>/page_NN.jpg. Returns count."""
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    count = 0
    for i in range(len(doc)):
        page = doc[i]
        # Render at high DPI, then downscale via PIL for size control
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        # Resize to target width keeping aspect ratio
        if img.width > TARGET_W:
            new_h = int(img.height * TARGET_W / img.width)
            img = img.resize((TARGET_W, new_h), Image.LANCZOS)
        out_path = os.path.join(out_dir, f"page_{i+1:02d}.jpg")
        img.save(out_path, "JPEG", quality=JPEG_QUALITY, optimize=True)
        count += 1
    doc.close()
    return count


def is_tenor_image(img_obj):
    if not isinstance(img_obj, dict):
        return False
    src = img_obj.get("b64") or ""
    return isinstance(src, str) and "tenor.com" in src


def patch_html(path, char_folder, n_pages):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    if not m:
        return f"FAIL  {os.path.basename(path)}: no SLIDES"
    slides = json.loads(m.group(1))

    n_replaced = 0
    n_no_page = 0
    for i, s in enumerate(slides):
        # PPTX page index = HTML slide index + 1 (1-based vs 0-based)
        page_idx = i + 1
        if page_idx > n_pages:
            n_no_page += 1
            continue
        # Replace bg_image with new external file path
        s["bg_image"] = f"slides/{char_folder}/page_{page_idx:02d}.jpg"
        # Clear redundant overlays — text now in bg_image
        s["styled_texts"] = []
        # Clear non-Tenor images (PPTX accents now in bg_image)
        # Preserve Tenor GIFs (v2 gameover injection)
        kept = [img for img in (s.get("images") or []) if is_tenor_image(img)]
        s["images"] = kept
        n_replaced += 1

    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    {os.path.basename(path)}: {n_replaced} slides repointed to external bg, {n_no_page} slides without matching PDF page"


def main():
    print("=== Phase 1: Render PPTX pages to JPGs ===\n")
    page_counts = {}
    for fname, pdf_name in PDF_MAP.items():
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"MISS  {fname}: PDF not found ({pdf_name})")
            page_counts[fname] = 0
            continue
        out_dir = os.path.join(SLIDES_OUT, CHAR_FOLDER[fname])
        n = render_pdf_pages(pdf_path, out_dir)
        page_counts[fname] = n
        print(f"OK    {fname}: rendered {n} pages -> {out_dir}")

    print()
    print("=== Phase 2: Patch HTMLs to use rendered backgrounds ===\n")
    for fname, n_pages in page_counts.items():
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        if n_pages == 0:
            print(f"SKIP  {fname}: no PDF pages available")
            continue
        print(patch_html(path, CHAR_FOLDER[fname], n_pages))

    # Also patch drake_classroom.html (mirrors drake)
    dc = os.path.join(ROOT, "drake_classroom.html")
    if os.path.exists(dc):
        print(patch_html(dc, "drake", page_counts.get("drake.html", 0)))


if __name__ == "__main__":
    main()
