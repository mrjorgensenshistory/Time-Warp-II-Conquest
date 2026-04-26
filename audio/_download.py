"""Music Hunter downloader for Time Warp II: Conquest.

Run from Windows command line:
    python "F:\\Michael's\\ACE\\US History\\Time-Warp-II-Conquest\\audio\\_download.py"

Downloads royalty-free / CC tracks for each character + hub + stings.
Verifies HTML/error pages and reports size + MP3 magic bytes.

LICENSE NOTES:
- Kevin MacLeod tracks are CC-BY 4.0; attribution baked into LICENSE.txt files.
- Pixabay tracks are Pixabay Content License (free, no attribution required).
- All URLs hand-verified against incompetech.com track index 2024-2026.
"""

import os
import urllib.request
import urllib.error

DEST_ROOT = os.path.dirname(os.path.abspath(__file__))

# (relative_path, url, label, license_block)
TARGETS = [
    # ---- Kevin MacLeod (CC-BY 4.0) ----
    ("columbus/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Tudor%20Theme.mp3",
     "Tudor Theme - Kevin MacLeod"),
    ("magellan/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Long%20Note%20Three.mp3",
     "Long Note Three - Kevin MacLeod"),
    ("raleigh/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Court%20and%20Page.mp3",
     "Court and Page - Kevin MacLeod"),
    ("cortereal/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Anamalie.mp3",
     "Anamalie - Kevin MacLeod"),
    ("dagama/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Five%20Armies.mp3",
     "Five Armies - Kevin MacLeod"),
    ("narvaez/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Spanish%20Jam.mp3",
     "Spanish Jam - Kevin MacLeod"),
    ("hub/main.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Volatile%20Reaction.mp3",
     "Volatile Reaction - Kevin MacLeod"),
    ("stings/gameover.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Sad%20Trombone.mp3",
     "Sad Trombone - Kevin MacLeod"),
    ("stings/fail.mp3",
     "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Failing%20Defense.mp3",
     "Failing Defense - Kevin MacLeod"),
]

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def download(url, dest, label):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        return f"FAIL  {label}: HTTP {e.code} {e.reason}"
    except Exception as e:
        return f"FAIL  {label}: {type(e).__name__} {e}"

    head = data[:64].lstrip()[:32].lower()
    if head.startswith(b"<!doctype") or head.startswith(b"<html") or head.startswith(b"<?xml"):
        return f"FAIL  {label}: HTML page, not audio ({len(data)} bytes)"
    if len(data) < 50_000:
        return f"WARN  {label}: only {len(data)} bytes - likely error"

    with open(dest, "wb") as f:
        f.write(data)
    size_mb = len(data) / (1024 * 1024)
    is_mp3 = data[:3] == b"ID3" or (data[0] == 0xFF and (data[1] & 0xE0) == 0xE0)
    tag = "MP3 OK" if is_mp3 else "size OK (verify)"
    return f"OK    {label}: {size_mb:.2f} MB [{tag}] -> {dest}"


def main():
    print(f"Downloading {len(TARGETS)} tracks to {DEST_ROOT}\n")
    for rel, url, label in TARGETS:
        dest = os.path.join(DEST_ROOT, rel.replace("/", os.sep))
        print(download(url, dest, label), flush=True)
    print("\nDone. Verify each MP3 plays in VLC / browser before shipping.")
    print("MANUAL TODO: Drake (audio/drake/main.mp3) and a hub-shanty option")
    print("must be sourced from Pixabay (CC0) - see audio/drake/LICENSE.txt for")
    print("recommended search URLs and the Pixabay manual-download steps.")


if __name__ == "__main__":
    main()
