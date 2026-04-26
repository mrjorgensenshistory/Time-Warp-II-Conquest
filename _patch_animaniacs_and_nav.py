"""Three integrated patches:

1. ANIMANIACS YT EMBEDS — Michael's request: Columbus + Magellan info pages
   should play their iconic Animaniacs songs.
   - Columbus (https://youtu.be/nxPRTQX1QjM) -> columbus.html slide_0 + index.html slide_3
   - Magellan (https://youtu.be/NFb5moTKs4I) -> magellan.html slide_0
   YouTube EMBEDS (not downloads) — YT hosts the audio under fair-use embed
   semantics, so no DMCA risk on our public repo.

2. ENGINE EXTENSION — adds a JS shim that wraps `goToSlide()`. When entering
   a slide that has `youtube_embed` set in its data, render an iframe overlay
   (centered, large, autoplay) and mute bg-music. When leaving, remove the
   iframe and unmute. Slide content (PPTX bg + buttons) still visible behind.

3. NAVIGATION REWIRE — HOME action now goes to analyzer.html instead of
   index.html. So:
   - End of Columbus tutorial -> analyzer.html
   - Each character's last-slide / gameover Try-Again-to-Hub -> analyzer.html

Idempotent: marker checks prevent double-application.
"""

import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))

ALL_CHAR_HTMLS = [
    "index.html", "columbus.html", "cortereal.html", "dagama.html",
    "drake.html", "drake_classroom.html", "magellan.html", "narvaez.html", "raleigh.html",
]

SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)

# YT video IDs
COLUMBUS_VID = "nxPRTQX1QjM"
MAGELLAN_VID = "NFb5moTKs4I"

# Map: HTML file -> { slide_id: video_id }
EMBED_MAP = {
    "columbus.html": { "slide_0": COLUMBUS_VID },
    "index.html":    { "slide_3": COLUMBUS_VID },  # tutorial reveal slide
    "magellan.html": { "slide_0": MAGELLAN_VID },
}

YT_ENGINE_MARKER = "<!-- TW2-YT-ENGINE-V1 -->"
YT_ENGINE_BLOCK = """
<!-- TW2-YT-ENGINE-V1 -->
<style>
.yt-overlay {
  position: absolute;
  top: 8vh; left: 50%;
  transform: translateX(-50%);
  width: 70vw;
  max-width: 900px;
  aspect-ratio: 16/9;
  z-index: 20;
  background: #000;
  border: 3px solid #c9a14a;
  box-shadow: 0 8px 30px rgba(0,0,0,0.7);
}
.yt-overlay iframe {
  width: 100%; height: 100%; border: 0;
}
.yt-overlay .yt-label {
  position: absolute;
  top: -3vh; left: 0;
  font-family: 'Bangers', Arial, sans-serif;
  font-size: clamp(0.8rem, 1.2vw, 1.1rem);
  color: #c9a14a;
  letter-spacing: 1px;
  text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
}
</style>
<script>
(function() {
  if (typeof window.goToSlide !== 'function') return;
  var _origGoToSlide = window.goToSlide;
  window.goToSlide = function(id) {
    // Tear down any existing YT iframe before navigating
    document.querySelectorAll('.yt-overlay').forEach(function(el){ el.remove(); });
    var bg = document.getElementById('bg-music');
    if (bg) bg.muted = false;

    _origGoToSlide(id);

    if (id === 'HOME' || (id || '').endsWith('.html')) return;
    if (typeof SLIDES === 'undefined') return;
    var slide = SLIDES.find(function(s){ return s.id === id; });
    if (!slide || !slide.youtube_embed) return;

    // Render YT overlay
    setTimeout(function() {
      var active = document.querySelector('.slide.active');
      if (!active) return;
      var ov = document.createElement('div');
      ov.className = 'yt-overlay';
      ov.innerHTML =
        '<div class="yt-label">▶ Play before continuing</div>' +
        '<iframe src="https://www.youtube.com/embed/' + slide.youtube_embed + '?autoplay=1&rel=0&modestbranding=1" ' +
        'allow="autoplay; encrypted-media" allowfullscreen></iframe>';
      active.appendChild(ov);
      if (bg) bg.muted = true;
    }, 100);
  };
})();
</script>
"""


def patch_slides_with_embeds(path, embed_map):
    """Add youtube_embed field to specific slides."""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    if not m:
        return f"FAIL  {os.path.basename(path)}: no SLIDES"
    slides = json.loads(m.group(1))
    n_added = 0
    for s in slides:
        if s.get("id") in embed_map:
            s["youtube_embed"] = embed_map[s["id"]]
            n_added += 1
    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    {os.path.basename(path)}: +{n_added} youtube_embed field(s)"


def inject_yt_engine(path):
    """Add the YT engine extension before </body> if not already present."""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    if YT_ENGINE_MARKER in html:
        return f"SKIP  {os.path.basename(path)} (YT engine already present)"
    if "</body>" not in html:
        return f"FAIL  {os.path.basename(path)}: no </body>"
    new_html = html.replace("</body>", YT_ENGINE_BLOCK + "\n</body>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    {os.path.basename(path)}: YT engine injected"


def rewire_home_to_analyzer(path):
    """Replace `hub_url` literal 'index.html' with 'analyzer.html'.
    The engine has: `if (id === 'HOME') { window.location.href = 'index.html'; }`
    Change that to point at analyzer.html.
    """
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    # Find the goToSlide HOME handler and replace 'index.html'
    # Pattern: window.location.href = 'index.html'
    patterns = [
        ("window.location.href = 'index.html'",  "window.location.href = 'analyzer.html'"),
        ('window.location.href = "index.html"',  'window.location.href = "analyzer.html"'),
    ]
    n = 0
    for old, new in patterns:
        if old in html:
            html = html.replace(old, new)
            n += 1
    if n == 0:
        return f"SKIP  {os.path.basename(path)} (no HOME literal to rewire)"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return f"OK    {os.path.basename(path)}: HOME -> analyzer.html"


def main():
    print("=== Phase 1: Animaniacs YT embeds ===\n")
    for fname, embed_map in EMBED_MAP.items():
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            print(f"MISS  {fname}")
            continue
        print(patch_slides_with_embeds(path, embed_map))

    print()
    print("=== Phase 2: YT engine extension on all HTMLs ===\n")
    for fname in ALL_CHAR_HTMLS:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        print(inject_yt_engine(path))

    print()
    print("=== Phase 3: Rewire HOME -> analyzer.html ===\n")
    for fname in ALL_CHAR_HTMLS:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        print(rewire_home_to_analyzer(path))


if __name__ == "__main__":
    main()
