"""Fix dead-end info slides across all character HTMLs.

PPTX-to-HTML converter dropped navigation buttons on info slides. Result:
- slide_1 (TIME WARP splash) has 0 buttons -> player frozen on splash screen
- terminal info slide (recap) has 0 buttons -> player can't return to hub

Fix: For info slides with empty buttons:
  - If NOT the last slide -> add "Continue" button targeting next slide_<n+1>
  - If IS the last slide -> add "Back to Hub" button targeting HOME
"""

import os
import re
import json

ROOT = os.path.dirname(os.path.abspath(__file__))

CHAR_HTMLS = [
    "columbus.html", "cortereal.html", "dagama.html",
    "drake.html", "magellan.html", "narvaez.html", "raleigh.html",
]

SLIDES_RE = re.compile(r"const SLIDES = (\[.*?\]);", re.DOTALL)


def patch(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    m = SLIDES_RE.search(html)
    if not m:
        return f"FAIL  {os.path.basename(path)}: no SLIDES"
    slides = json.loads(m.group(1))

    # Build slide_id -> array index map for "next slide" logic
    id_to_idx = {s.get("id"): i for i, s in enumerate(slides)}
    last_idx = len(slides) - 1

    n_continue = 0
    n_home = 0
    for i, s in enumerate(slides):
        if s.get("type") != "info":
            continue
        if s.get("buttons"):
            continue  # Already has buttons; leave alone

        if i == last_idx:
            # Terminal info slide -> back to hub
            s["buttons"] = [{"text": "Back to Hub", "target": "HOME"}]
            n_home += 1
        else:
            # Mid-game info slide -> continue to next
            next_id = slides[i + 1].get("id")
            s["buttons"] = [{"text": "Continue", "target": next_id}]
            n_continue += 1

    new_json = json.dumps(slides, ensure_ascii=False, separators=(", ", ": "))
    new_html = html[:m.start(1)] + new_json + html[m.end(1):]
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)

    return f"OK    {os.path.basename(path)}: +{n_continue} Continue, +{n_home} Hub"


def main():
    print("Patching dead-end info slides\n")
    for fname in CHAR_HTMLS:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            print(f"MISS  {fname}")
            continue
        print(patch(path))

    # Also patch drake_classroom.html if present (mirrors drake)
    classroom = os.path.join(ROOT, "drake_classroom.html")
    if os.path.exists(classroom):
        print(patch(classroom))


if __name__ == "__main__":
    main()
