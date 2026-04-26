"""Add Mr. Roughton credit footer to all HTMLs + build classroom Drake variant.

Per memory `reference_mrroughton.md`: Conquest IS Time Warp II of the original
I-VII series, so Mr. Roughton credit is REQUIRED.

Also creates drake_classroom.html — a copy of drake.html with the audio source
swapped to point at a (gitignored) classroom-only audio file. The .gitignore
already prevents this file and audio/drake_classroom/ from being pushed.
"""

import os
import re
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))

CREDIT_MARKER = "<!-- TW2-CREDIT-FOOTER-V1 -->"
CREDIT_BLOCK = f"""{CREDIT_MARKER}
<div id="mr-roughton-credit"
  style="position:fixed;bottom:6px;right:10px;z-index:998;
         font-family:'Share Tech',Arial,sans-serif;font-size:0.7rem;
         color:rgba(255,255,255,0.55);text-shadow:1px 1px 2px rgba(0,0,0,0.8);
         pointer-events:auto;letter-spacing:0.5px;">
  Time Warp by Mr. Jorgensen &mdash; original concept
  <a href="https://www.mrroughton.com" target="_blank" rel="noopener"
     style="color:rgba(255,215,0,0.85);text-decoration:none;">mrroughton.com</a>
</div>"""

ALL_HTMLS = [
    "index.html", "columbus.html", "cortereal.html", "dagama.html",
    "drake.html", "magellan.html", "narvaez.html", "raleigh.html",
]


def add_credit(path):
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    if CREDIT_MARKER in html:
        return f"SKIP  {os.path.basename(path)} (credit already present)"
    if "</body>" not in html:
        return f"FAIL  {os.path.basename(path)}: no </body>"
    new_html = html.replace("</body>", CREDIT_BLOCK + "\n</body>", 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_html)
    return f"OK    {os.path.basename(path)}: credit added"


def build_classroom_drake():
    src = os.path.join(ROOT, "drake.html")
    dst = os.path.join(ROOT, "drake_classroom.html")

    with open(src, "r", encoding="utf-8") as f:
        html = f.read()

    # Swap the audio source from public path to classroom-only path
    classroom_html = html.replace(
        'src="audio/drake/main.mp3"',
        'src="audio/drake_classroom/drake_real.mp3"'
    )

    # Add a visible classroom-only badge in the corner
    badge = """
<!-- TW2-CLASSROOM-VARIANT -->
<div id="classroom-badge" style="position:fixed;top:1vh;left:1vw;z-index:999;
     background:rgba(122,31,31,0.95);color:#fff;padding:0.4vh 1vw;
     font-family:'Bangers',Arial,sans-serif;font-size:0.85rem;letter-spacing:1px;
     border:1px solid rgba(255,255,255,0.4);">
  CLASSROOM ONLY &mdash; §110(1)
</div>"""
    classroom_html = classroom_html.replace("</body>", badge + "\n</body>", 1)

    # Update title to flag the variant
    classroom_html = classroom_html.replace(
        "<title>Time Warp - Sir Francis Drake</title>",
        "<title>Time Warp - Sir Francis Drake [CLASSROOM]</title>"
    )

    with open(dst, "w", encoding="utf-8") as f:
        f.write(classroom_html)

    # Create the classroom audio folder + readme placeholder
    classroom_audio_dir = os.path.join(ROOT, "audio", "drake_classroom")
    os.makedirs(classroom_audio_dir, exist_ok=True)
    readme = os.path.join(classroom_audio_dir, "README.txt")
    if not os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write(
                "CLASSROOM-ONLY AUDIO FOLDER\n"
                "===========================\n\n"
                "Place a copy of the real Drake track here as `drake_real.mp3`.\n"
                "Suggested track: 'Started From the Bottom' or 'Hotline Bling'.\n\n"
                "This folder + drake_classroom.html are GITIGNORED.\n"
                "They are NEVER pushed to the public GitHub repo.\n\n"
                "Use only in physical classroom presentation under\n"
                "17 U.S.C. §110(1) face-to-face teaching exception.\n"
            )

    return f"OK    drake_classroom.html created (audio swapped, badge added, title flagged)"


def main():
    print("=== Mr. Roughton credit footer ===")
    for fname in ALL_HTMLS:
        path = os.path.join(ROOT, fname)
        if os.path.exists(path):
            print(add_credit(path))
        else:
            print(f"MISS  {fname}")
    print()
    print("=== Drake classroom variant ===")
    print(build_classroom_drake())


if __name__ == "__main__":
    main()
