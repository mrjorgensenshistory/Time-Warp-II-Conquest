"""Audio injection patch for Time Warp II: Conquest.

Adds <audio> elements + mute button to all character HTMLs and the hub.
External MP3 references (cleaner than CW's inline base64 — keeps HTMLs small,
lets us swap tracks without regenerating slides).

Idempotent: detects existing injection markers and skips if already patched.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Map: HTML filename -> character audio folder (None = hub)
CHAR_MAP = {
    "index.html":      None,           # hub
    "columbus.html":   "columbus",
    "cortereal.html":  "cortereal",
    "dagama.html":     "dagama",
    "drake.html":      "drake",
    "magellan.html":   "magellan",
    "narvaez.html":    "narvaez",
    "raleigh.html":    "raleigh",
}

PATCH_MARKER = "<!-- TW2-AUDIO-PATCH-V1 -->"

MUTE_BUTTON_HTML = """
<button id="mute-btn" onclick="toggleMute()" title="Toggle music"
  style="position:fixed;top:1vh;right:8vw;z-index:999;background:rgba(0,0,0,0.6);color:#fff;
         border:1px solid rgba(255,255,255,0.3);border-radius:5px;padding:0.5vh 1vw;
         font-size:0.8rem;cursor:pointer;opacity:0.5;font-family:Arial,sans-serif;"
  onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.5'">&#x1F50A; Mute</button>
<script>
function toggleMute() {
  var m = document.getElementById('bg-music');
  var h = document.getElementById('hub-music');
  var btn = document.getElementById('mute-btn');
  var target = m || h;
  if (!target) return;
  target.muted = !target.muted;
  btn.innerHTML = target.muted ? '\\u{1F507} Muted' : '\\u{1F50A} Mute';
}
// Auto-start music on first user interaction (Chrome autoplay policy)
document.addEventListener('click', function startMusic() {
  var m = document.getElementById('bg-music') || document.getElementById('hub-music');
  if (m && m.paused) { m.volume = 0.45; m.play().catch(function(){}); }
}, { once: true });
</script>"""


def make_audio_block(audio_folder):
    """Build audio + mute injection block.
    audio_folder=None means hub (uses hub-music + cannon SFX).
    """
    if audio_folder is None:
        # Hub: one track + cannon for the HOIST THE COLORS button
        return PATCH_MARKER + """
<audio id="hub-music" loop preload="auto"><source src="audio/hub/main.mp3" type="audio/mpeg"></audio>
<audio id="cannon-sfx" preload="auto"><source src="audio/stings/cannon.mp3" type="audio/mpeg"></audio>
""" + MUTE_BUTTON_HTML
    # Character: bg-music + gameover sting + universal fail sting
    return PATCH_MARKER + f"""
<audio id="bg-music" loop preload="auto"><source src="audio/{audio_folder}/main.mp3" type="audio/mpeg"></audio>
<audio id="gameover-sound" preload="auto"><source src="audio/stings/gameover.mp3" type="audio/mpeg"></audio>
<audio id="fail-sting" preload="auto"><source src="audio/stings/fail.mp3" type="audio/mpeg"></audio>
""" + MUTE_BUTTON_HTML


def patch_file(path, audio_folder):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    if PATCH_MARKER in html:
        return f"SKIP  {os.path.basename(path)} (already patched)"

    block = make_audio_block(audio_folder)
    # Insert just before </body>
    if "</body>" not in html:
        return f"FAIL  {os.path.basename(path)}: no </body> tag found"

    new_html = html.replace("</body>", block + "\n</body>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)

    label = audio_folder if audio_folder else "HUB"
    return f"OK    {os.path.basename(path)} <- {label}"


def main():
    print(f"Patching audio into {len(CHAR_MAP)} HTML files at {ROOT}\n")
    for fname, folder in CHAR_MAP.items():
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            print(f"MISS  {fname}: file not found")
            continue
        # Verify the audio file exists too
        if folder is not None:
            audio_path = os.path.join(ROOT, "audio", folder, "main.mp3")
            if not os.path.exists(audio_path):
                print(f"WARN  {fname}: audio/{folder}/main.mp3 missing — patch references it anyway")
        print(patch_file(path, folder))
    print("\nDone. Each HTML now has <audio> + mute button before </body>.")
    print("Next: open one HTML in browser, click anywhere, music should fade in.")


if __name__ == "__main__":
    main()
