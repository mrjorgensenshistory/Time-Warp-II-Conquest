"""V2: Differentiate per-character gameover GIFs + Drake full pirate theme.

Three things:

1. **Per-character GIF variety.** v1 used Bobby Boucher tackle for da Gama / Magellan /
   Narváez — same GIF three times. v2 gives each character a unique cutscene character
   with nationality flavor. Da Gama gets Captain Hook (1991 movie) — he was the villain
   of his own story. Narváez gets Tulio & Miguel (got conned). Raleigh gets "Both is
   good" Chel (English vs Spanish double-dealing). Hook movie added to the cast.

2. **Drake bonus reveal cutscene.** The "BANGARANG!" Rufio GIF lands on Drake's
   triumph reveal slide as the Hook-movie pirate-energy victory cherry.

3. **Drake full parody injection** — the remaining 4 lines from THEME §5:
   - slide_2 (mid-voyage choice): "OVO = Old Voyaging Outfit."
   - slide_5 (Spanish ship decision): "In my feelings… about the Spanish."
   - slide_15 (cannon battle): "Hotline Bling? Try Cannon Bling."
   - slide_19 (treasure greed): "God's Plan? More like Queen's Plan."
   - slide_25 (circumnavigation reveal): "Took care of the whole world, on God."

All injections are ADDITIONS to body text or images arrays — never replacements.
"""

import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))

# Per-character v2 mapping — each character gets a UNIQUE cast assignment
CHAR_GAMEOVER_V2 = {
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
        # Captain Hook villain — Da Gama WAS the bad guy of his own voyage
        "gif": "https://media.tenor.com/U3ad7iq1DrkAAAAM/captain-hook-hook.gif",
        "caption": "Bad form, Captain.",
        "subline": "Da Gama burned bridges. The locals burned back. You became the villain of the story.",
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
        # Tulio & Miguel — Narváez got conned by his own greed and the New World
        "gif": "https://media.tenor.com/4t8g4q3M4UAAAAM/el-dorado-road-to-miguel.gif",
        "caption": "It's tough to be a god…",
        "subline": "Narváez landed in Florida looking for gold. He found a swamp. 300 men entered. Four came out.",
    },
    "raleigh.html": {
        # "Both is good" Chel — Raleigh tried to play both sides, neither side amused
        "gif": "https://media.tenor.com/-1IhKbqXsg8AAAAM/the-road-to-el-dorado-both-is-good.gif",
        "caption": "Both? Both. The queen was not amused.",
        "subline": "Raleigh charmed Elizabeth. The next king sent him to the block.",
    },
}

# Drake bonus: Hook BANGARANG on triumph reveal (slide_25)
DRAKE_REVEAL_GIF = "https://media.tenor.com/o-xhn7XDyckAAAAM/hook-bangarang.gif"
DRAKE_REVEAL_SLIDE_ID = "slide_25"  # confirmed via earlier scan

# Drake full parody injections per THEME §5
DRAKE_PARODY_LINES = {
    "slide_2": "\n\n— OVO = Old Voyaging Outfit.",
    "slide_5": "\n\n— In my feelings… about the Spanish.",
    "slide_15": "\n\n— Hotline Bling? Try Cannon Bling.",
    "slide_19": "\n\n— God's Plan? More like Queen's Plan.",
    "slide_25": "\n\n— Took care of the whole world, on God.",
}

SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)

V2_MARKER_TEXT = "BANGARANG"  # Used to detect drake reveal already patched


def patch_character_gameovers(path, gif_url, caption, subline):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    slides = json.loads(m.group(1))

    n_replaced = 0
    for s in slides:
        if s.get("type") != "gameover":
            continue
        # Replace existing Tenor image with v2 URL (or add if none)
        imgs = s.get("images") or []
        non_tenor = [i for i in imgs if not (isinstance(i, dict) and
                                              isinstance(i.get("b64", ""), str) and
                                              i.get("b64", "").startswith("https://media.tenor.com"))]
        new_img = {"b64": gif_url, "fullscreen": True}
        s["images"] = non_tenor + [new_img]
        s["title"] = caption
        # Replace the v1 subline if present, else append the v2 subline
        body = s.get("body") or ""
        # Strip prior subline patterns we know we wrote
        for prior in ["Columbus made a poor call.", "Corte-Real sailed into the fog.",
                      "Da Gama burned bridges.", "Sir Francis Drake died of dysentery",
                      "Magellan made it most of the way", "The swamp had other plans",
                      "Raleigh charmed a queen.", "300 men entered Florida. Four came out."]:
            if prior in body:
                # Remove paragraph containing the prior subline
                body = re.sub(r"^[^\n]*" + re.escape(prior) + r"[^\n]*\n*", "", body, count=1)
        if subline.strip() not in body:
            s["body"] = subline + ("\n\n" + body if body else "")
        else:
            s["body"] = body
        n_replaced += 1

    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    {os.path.basename(path)}: {n_replaced} gameover slides updated"


def patch_drake_full(path):
    """Add reveal-slide BANGARANG GIF + 5 mid-game parody lines to drake."""
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    slides = json.loads(m.group(1))

    n_parody = 0
    n_reveal_gif = 0
    for s in slides:
        sid = s.get("id")
        # Add BANGARANG GIF to reveal slide
        if sid == DRAKE_REVEAL_SLIDE_ID and s.get("type") == "reveal":
            imgs = s.get("images") or []
            already = any(isinstance(i, dict) and DRAKE_REVEAL_GIF in (i.get("b64") or "") for i in imgs)
            if not already:
                s["images"] = imgs + [{"b64": DRAKE_REVEAL_GIF, "fullscreen": True}]
                n_reveal_gif += 1

        # Inject parody lines on specific slides
        if sid in DRAKE_PARODY_LINES:
            line = DRAKE_PARODY_LINES[sid]
            body = s.get("body") or ""
            if line.strip() not in body:
                s["body"] = body + line
                n_parody += 1

    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    drake full parody: {n_parody} parody lines, {n_reveal_gif} reveal GIF"


def main():
    print("=== v2 per-character gameover differentiation ===\n")
    for fname, cfg in CHAR_GAMEOVER_V2.items():
        path = os.path.join(ROOT, fname)
        if os.path.exists(path):
            print(patch_character_gameovers(path, cfg["gif"], cfg["caption"], cfg["subline"]))

    # Apply same v2 mapping to drake_classroom.html
    dc = os.path.join(ROOT, "drake_classroom.html")
    if os.path.exists(dc):
        cfg = CHAR_GAMEOVER_V2["drake.html"]
        print(patch_character_gameovers(dc, cfg["gif"], cfg["caption"], cfg["subline"]))

    print()
    print("=== Drake full pirate theme ===\n")
    print(patch_drake_full(os.path.join(ROOT, "drake.html")))
    if os.path.exists(dc):
        print(patch_drake_full(dc))


if __name__ == "__main__":
    main()
