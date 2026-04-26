"""Game-over meme injection patch for Time Warp II: Conquest.

Parses the SLIDES JSON array embedded in each character HTML, finds slides with
type=="gameover", and adds:
  - A fullscreen Tenor GIF (the themed cutscene meme)
  - A caption-style title override ("WRONG LEVERRRR!", "MAMA SAYS PIRATES...", etc.)

Idempotent: skips slides that already have a Tenor URL injected.
"""

import os
import re
import json
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Failure-type -> cast mapping per THEME spec §4
# Each character gets a primary meme + caption pairing
CHAR_GAMEOVER_MAP = {
    "columbus.html": {
        "gif": "https://media.tenor.com/mcS-PaTlDawAAAAM/pull-the-lever-wrong-lever.gif",
        "caption": "WRONG LEVERRRR!",
        "subline": "Columbus made a poor call. The voyage is over.",
    },
    "cortereal.html": {
        "gif": "https://media.tenor.com/x8v1oNUOmg4AAAAM/rickroll-roll.gif",
        "caption": "Never gonna give you up… to scurvy.",
        "subline": "Corte-Real sailed into the fog. He never sailed back out.",
    },
    "dagama.html": {
        "gif": "https://media.tenor.com/Qqy__Lb6qIMAAAAM/tackle-running.gif",
        "caption": "MAMA SAYS PIRATES IS THE DEVIL!",
        "subline": "Da Gama burned bridges. The locals burned back.",
    },
    "drake.html": {
        "gif": "https://media.tenor.com/hED6DgiSGCYAAAAM/spongebob-toilet.gif",
        "caption": "Started from the bottom, now we're back at the bottom.",
        "subline": "Sir Francis Drake died of dysentery on the voyage home. We are not joking.",
    },
    "magellan.html": {
        "gif": "https://media.tenor.com/Qqy__Lb6qIMAAAAM/tackle-running.gif",
        "caption": "Lapulapu had something to say about that.",
        "subline": "Magellan made it most of the way around the world. Most.",
    },
    "narvaez.html": {
        "gif": "https://media.tenor.com/Qqy__Lb6qIMAAAAM/tackle-running.gif",
        "caption": "The swamp had other plans.",
        "subline": "300 men entered Florida. Four came out.",
    },
    "raleigh.html": {
        "gif": "https://media.tenor.com/mcS-PaTlDawAAAAM/pull-the-lever-wrong-lever.gif",
        "caption": "The queen was not amused.",
        "subline": "Raleigh charmed a queen. The next king sent him to the block.",
    },
}

# Regex to find: const SLIDES = [...];
# Greedy matching - the array is one long line ending in ];
SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)


def patch_html(path, gif_url, caption, subline):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    m = SLIDES_RE.search(html)
    if not m:
        return f"FAIL  {os.path.basename(path)}: no SLIDES array found"

    slides_json = m.group(1)
    try:
        slides = json.loads(slides_json)
    except json.JSONDecodeError as e:
        return f"FAIL  {os.path.basename(path)}: JSON parse error at pos {e.pos}"

    n_gameover = 0
    n_patched = 0
    n_skipped = 0
    for s in slides:
        if s.get("type") != "gameover":
            continue
        n_gameover += 1
        # Check if already has our cutscene injected
        existing_imgs = s.get("images") or []
        already = any(
            isinstance(img, dict) and img.get("b64", "").startswith("https://media.tenor.com")
            for img in existing_imgs
        )
        if already:
            n_skipped += 1
            continue
        # Inject the cutscene GIF as a fullscreen image
        new_img = {"b64": gif_url, "fullscreen": True}
        s["images"] = existing_imgs + [new_img]
        # Override the title with the parody caption (red+shake handled by .gameover-slide CSS)
        s["title"] = caption
        # Append the subline to the body so it shows below the meme
        body = s.get("body", "") or ""
        if subline and subline not in body:
            s["body"] = subline + ("\n\n" + body if body else "")
        n_patched += 1

    if n_patched == 0 and n_skipped == 0 and n_gameover == 0:
        return f"WARN  {os.path.basename(path)}: 0 gameover slides found"

    # Reserialize and write back. ensure_ascii=False keeps emoji/unicode intact.
    new_slides_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_slides_json + html[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)

    return (f"OK    {os.path.basename(path)}: {n_gameover} gameover slides, "
            f"{n_patched} patched, {n_skipped} already done")


def main():
    print(f"Patching gameover memes into {len(CHAR_GAMEOVER_MAP)} character HTMLs\n")
    for fname, cfg in CHAR_GAMEOVER_MAP.items():
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            print(f"MISS  {fname}: file not found")
            continue
        result = patch_html(path, cfg["gif"], cfg["caption"], cfg["subline"])
        print(result)
    print("\nDone.")


if __name__ == "__main__":
    main()
