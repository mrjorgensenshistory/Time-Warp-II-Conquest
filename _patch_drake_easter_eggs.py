"""Drake-specific parody-text easter eggs.

Adds the safe Drake-the-rapper homage lines from THEME §5 to drake.html:
- Slide 0 (intro): append 'Started from the bottom, now we're on a ship.' marker
- Reveal slides: append 'Best I Ever Had. (The voyage, not the loot.)' tag

These are ADDITIONS to body text, never REPLACEMENTS of PPTX educational content.
"""

import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
DRAKE = os.path.join(ROOT, "drake.html")

INTRO_TAG = "\n\n— Started from the bottom, now we're on a ship 🏴‍☠️"
REVEAL_TAG = "\n\n— Best I Ever Had. (The voyage, not the loot.)"

SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)


def main():
    with open(DRAKE, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    slides = json.loads(m.group(1))

    n_intro = 0
    n_reveal = 0

    for s in slides:
        sid = s.get("id", "")
        stype = s.get("type", "")
        body = s.get("body", "") or ""

        # Slide 0: intro
        if sid == "slide_0":
            if INTRO_TAG.strip() not in body:
                s["body"] = body + INTRO_TAG
                n_intro += 1

        # Reveal slides: triumph closer
        elif stype == "reveal":
            if REVEAL_TAG.strip() not in body:
                s["body"] = body + REVEAL_TAG
                n_reveal += 1

    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(DRAKE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print(f"Drake easter eggs: {n_intro} intro tag(s), {n_reveal} reveal tag(s)")


if __name__ == "__main__":
    main()
