"""CSS/JS overlay fixes for the remaining playtest issues.

Injects a <style> + <script> block before </body> on all 8 HTMLs:

- Issue #4: Long parody captions overflow `.slide-title` font-size.
  Reduce gameover title font-size; auto-shrink for very long captions.
- Issue #7: Synthetic Web-Audio gameover buzz collides with our MP3.
  Override window.playGameOverBuzz() to no-op when <audio id="gameover-sound"> exists.
- Issue #9: Fullscreen Tenor GIF (z-index 2) covers title text (z-index 1).
  Raise .slide-content (title + body) above the GIF, add semi-transparent dark
  backdrop behind text for readability over the GIF.
- Issue #3 follow-up: Hide .pptx-text overlays (text is now baked into PPTX render).

Idempotent — skips if the marker is already present.
"""

import os

ROOT = os.path.dirname(os.path.abspath(__file__))

ALL_HTMLS = [
    "index.html", "columbus.html", "cortereal.html", "dagama.html",
    "drake.html", "drake_classroom.html", "magellan.html", "narvaez.html", "raleigh.html",
]

PATCH_MARKER = "<!-- TW2-CSSJS-FIX-V1 -->"

PATCH_BLOCK = """
<!-- TW2-CSSJS-FIX-V1 -->
<style>
/* Issue #3 follow-up: PPTX text now baked into bg_image, hide JS overlay */
.pptx-text { display: none !important; }

/* Issue #4 + #9: Smaller gameover title that won't get covered by GIF */
.gameover-slide .slide-title {
  font-size: clamp(1rem, 2.6vw, 1.7rem) !important;
  position: relative;
  z-index: 10 !important;
  background: rgba(0,0,0,0.78);
  padding: 1.2vh 2vw;
  margin: 0 auto;
  max-width: 80%;
  text-align: center;
  border: 2px solid rgba(255,80,80,0.6);
  text-shadow: 2px 2px 6px rgba(0,0,0,0.95);
  letter-spacing: 0.5px;
}

/* Issue #9: Raise text content above the fullscreen GIF */
.gameover-slide .slide-content {
  z-index: 10 !important;
  position: relative;
}
.gameover-slide .text-box,
.gameover-slide .text-box-dark {
  background: rgba(255,255,255,0.92) !important;
  position: relative;
  z-index: 9;
  margin-top: 1vh;
  font-size: clamp(0.85rem, 1.6vw, 1.1rem) !important;
}

/* Push fullscreen-gif lower so caption stays visible above */
.gameover-slide .fullscreen-gif {
  top: 60% !important;
  max-height: 50vh !important;
  max-width: 60vw !important;
  z-index: 5 !important;
}

/* Bring buttons above GIF */
.gameover-slide .buttons {
  z-index: 12 !important;
  bottom: 4vh !important;
  top: auto !important;
  transform: translate(-50%, 0) !important;
}
</style>
<script>
// Issue #7: Suppress synthetic gameover buzz when external MP3 exists
(function() {
  if (typeof window.playGameOverBuzz === 'function') {
    var orig = window.playGameOverBuzz;
    window.playGameOverBuzz = function() {
      if (document.getElementById('gameover-sound')) return;  // MP3 will play instead
      try { orig(); } catch(e) {}
    };
  }
  // Also: if we have an external bg-music + the engine started a fadeIn interval
  // before the user clicked into a gameover, ensure the music actually pauses.
  // Watch for type=gameover slides being shown and force-pause bg-music.
  var observer = new MutationObserver(function(muts) {
    for (var i = 0; i < muts.length; i++) {
      var added = muts[i].addedNodes;
      for (var j = 0; j < added.length; j++) {
        var n = added[j];
        if (n.nodeType === 1 && n.classList && n.classList.contains('gameover-slide')) {
          var bg = document.getElementById('bg-music');
          if (bg && !bg.paused) {
            try { bg.pause(); bg.volume = 0; } catch(e) {}
          }
        }
      }
    }
  });
  if (document.getElementById('game')) {
    observer.observe(document.getElementById('game'), { childList: true });
  }
})();
</script>
"""


def patch(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    if PATCH_MARKER in html:
        return f"SKIP  {os.path.basename(path)} (already patched)"
    if "</body>" not in html:
        return f"FAIL  {os.path.basename(path)}: no </body>"
    new_html = html.replace("</body>", PATCH_BLOCK + "\n</body>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    {os.path.basename(path)}"


def main():
    print("Injecting CSS/JS fixes\n")
    for fname in ALL_HTMLS:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            print(f"MISS  {fname}")
            continue
        print(patch(path))


if __name__ == "__main__":
    main()
