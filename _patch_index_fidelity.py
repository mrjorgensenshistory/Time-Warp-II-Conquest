"""Patch index.html with PPTX-render fidelity + fix country selection.

Two fixes:
1. index.html was missed by `_patch_pptx_fidelity.py`. It still has old broken
   inline base64 bg_images, and the new `.pptx-text { display: none }` CSS rule
   hides the text overlays. Net effect: blank screens, no captions.

   index.html shares the same source PPTX as columbus.html (Tutorial w Columbus),
   so we can reuse the already-rendered slides/columbus/page_NN.jpg files.

2. slide_5 country selection is missing the Portugal button. Per the storyline:
   - Portugal -> slide_6 (King John II rejects Columbus)
   - Spain    -> slide_11 (try Spain instead)

   The current slide has only "Spain -> slide_6" which is wrong on both counts
   (label says Spain, target is the Portugal flow). The git log shows commit
   943b343 fixed this previously; it was overwritten by a subsequent rebuild.
"""

import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(ROOT, "index.html")

SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)


def is_tenor_image(img):
    return isinstance(img, dict) and "tenor.com" in (img.get("b64") or "")


def main():
    with open(HTML, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    slides = json.loads(m.group(1))

    n_repointed = 0
    for i, s in enumerate(slides):
        page_idx = i + 1
        # index.html shares slides with columbus.html
        s["bg_image"] = f"slides/columbus/page_{page_idx:02d}.jpg"
        s["styled_texts"] = []
        s["images"] = [img for img in (s.get("images") or []) if is_tenor_image(img)]
        n_repointed += 1

    # Fix country selection on slide_5
    s5 = next((s for s in slides if s.get("id") == "slide_5"), None)
    if s5:
        s5["buttons"] = [
            {"text": "Portugal", "target": "slide_6"},
            {"text": "Spain",    "target": "slide_11"},
        ]
        print(f"OK    slide_5 country buttons: Portugal->slide_6, Spain->slide_11")

    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"OK    index.html: {n_repointed} slides repointed to slides/columbus/*")


if __name__ == "__main__":
    main()
