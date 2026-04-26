# Time Warp II: Conquest — Playtest Log

**Build:** v2 (commit `89cc31f` + audio commit `2940899` + initial commit)
**Date:** 2026-04-25
**Tester:** Michael
**Mode:** RECEIVE-ONLY — no fixes applied until tester gives green light

---

## How this log works

Each issue gets:
- **#** number
- **Page** where it happened (hub / columbus / drake / etc.)
- **Severity** (BLOCKER / MAJOR / MINOR / POLISH)
- **What's wrong** (description from screenshot/note)
- **Screenshot ref** (filename if Michael provided one)
- **Status** (OPEN / IN PROGRESS / FIXED / WONTFIX)

---

## Issues

### #1 — Same GIF used for both branches of a decision (right vs wrong)
- **Severity:** MAJOR
- **Page(s):** unknown — awaiting screenshot. Likely Drake (storm decision: "Head Back and Wait" vs "Try to sail through the storm") or similar branching point.
- **Symptom:** Same cutscene GIF appears regardless of whether the player chooses the correct or incorrect option. Repetitive / unsatisfying — the decision feels meaningless visually.
- **Likely cause:** v2 patch maps **one primary GIF per character** (e.g. Drake = Spongebob toilet, Da Gama = Hook villain). Every gameover within a character uses the same GIF. If the "right path" also shares imagery with the wrong path, that's compounded.
- **Possible fix angle:** rotate GIFs by *failure type* (greedy → Yzma, lazy → Terry Tate, conned → Tulio/Miguel, etc. per THEME §4 mapping) instead of one-per-character. Reveal/triumph slides should also have distinct visuals from gameovers.
- **Status:** OPEN — awaiting screenshot

### #2 — HTML pages look mostly empty, nothing like the PPTX original
- **Severity:** BLOCKER (fidelity to source)
- **Page(s):** unknown — awaiting screenshot. Possibly affects all character pages.
- **Symptom:** HTML version is "mostly empty" compared to the PPTX. Per memory `feedback_html_timewarp_v1.md`: PPTX is the source of truth — HTML must be a 1:1 faithful transfer. This violates that.
- **Likely causes (need screenshot to narrow):**
  1. `bg_image` (PPTX slide rendered as base64 image) not rendering — CSS background-image broken?
  2. `styled_texts` CSS positioning is wrong — text in wrong spots, not where PPTX placed them
  3. PPTX images / accent graphics dropped during conversion
  4. `.slide-content` flexbox alignment squeezing content into corner
- **Status:** OPEN — awaiting screenshot, likely the highest-priority fix once seen

### #4 — Caption size is wrong
- **Severity:** MAJOR (legibility)
- **Page(s):** unknown — likely the gameover slides where my v2 caption injection lives.
- **Symptom:** Caption text ("WRONG LEVERRR!", "Bad form, Captain", "Started from the bottom, now we're back at the bottom", etc.) is the wrong size — too big, too small, or doesn't fit its container.
- **Likely cause:** I overwrote `slide.title` with the parody caption. The renderer styles `.slide-title` with `font-size: clamp(2rem, 5vw, 3.5rem)` for gameover slides — fine for "WRONG LEVERRR!" but WAY too big for the longer Drake parody lines like "Started from the bottom, now we're back at the bottom" (8 words instead of 2).
- **Status:** OPEN — awaiting screenshot, likely needs adaptive sizing or a separate caption element with smaller font for long lines.

### #5 — Red arrows missing on multiple Drake slides (PPTX shape primitives dropped)
- **Severity:** MAJOR (PPTX fidelity loss — concrete example of issue #2)
- **Pages confirmed so far:**
  - drake.html, slide_5 (decision: "While sailing south toward africa you notice a large merchant ship…")
  - drake.html, slide_7-ish ("Captured the ship" — "You decide to capture it and add it to your fleet…")
  - **Pattern:** likely affects every PPTX slide that uses arrow/callout shapes — could be ~10+ slides across all 7 characters
- **Symptom:** PPTX original has a red arrow (probably pointing at the merchant ship in the slide image or at a UI element). HTML version is missing it.
- **Likely cause:** PPTX arrows are *shape* objects (XML primitives like `<p:cxnSp>` connector shapes or `<p:sp>` arrow autoshapes), NOT bitmap images. The converter (`pptx_to_html_timewarp.py`) extracts `bg_image` and `images` (rendered/embedded pictures) but drops `python-pptx` shape primitives entirely. This is a converter feature gap, not a per-slide bug.
- **Scope estimate:** if Drake has 2 confirmed missing arrows in the first ~7 slides, full game probably has dozens of missing annotations across all characters.
- **Possible fix angles:**
  1. Add shape-extraction to converter — walk `slide.shapes`, detect arrows/lines/callouts, emit as positioned SVG or CSS-shape overlays in HTML
  2. Quick patch: manually add a "red arrow CSS overlay" element to each affected slide (tedious, won't scale)
  3. Use LibreOffice headless to re-render each PPTX slide as a high-res PNG and use those as the bg_image (loses interactivity but keeps pixel fidelity)
- **Status:** OPEN — fundamental converter limitation, affects PPTX fidelity broadly

### #6 — Images way too small / too much black-empty space / PPTX maps not preserved
- **Severity:** BLOCKER (this is the concrete root cause behind issue #2 "looks empty")
- **Pages confirmed so far:**
  - drake.html, "crossed the ocean" slide — looks "way way different from powerpoint map"
  - Same arrow loss pattern continues here (third confirmed instance — see #5)
- **Symptoms:**
  1. Images render at small/accent size when PPTX has them as full-slide art
  2. Massive black/empty space surrounding the small image (the `#0a0a1a` dark body bg dominates the screen)
  3. PPTX-specific maps (e.g. Drake's voyage path map) appear different from source — possibly substituted with a generic world map, or PPTX map is being rendered at wrong size/position
  4. No full-screen image presentation — Michael wants images to FILL the slide, not float in a corner
- **Likely root causes:**
  1. **Converter image-classification logic is too conservative:** the converter has three image tiers (`fullscreen` / `large` / accent-thumb-right). Most extracted images fall into the accent-thumb tier by default, getting the small `right:2vw; top:10vh; max-width:30vw` placement instead of filling the slide.
  2. **`bg_image` may be a partial render**, not the full PPTX slide — if the converter exported only the central image rectangle from PPTX (not the whole rendered slide), the surrounding canvas shows our `#0a0a1a` body background, hence "blank/black space."
  3. **`styled_texts` positioning uses PPTX percentages** (e.g. `left: 5%; top: 12%; width: 54.9%`) which is correct, but the rest of the slide isn't being filled with PPTX visuals.
- **Possible fix angles:**
  1. **Make `bg_image` truly full-slide** — re-extract every PPTX slide as a high-resolution full-canvas PNG render (LibreOffice headless `--convert-to pdf` then page-to-png, or python-pptx + Pillow). Replace existing partial bg_images.
  2. **Promote `images` to fullscreen by default** — change converter logic: when an image dominates a slide (>40% of slide area), tag it `fullscreen: true` so it renders centered+large via `.fullscreen-gif` CSS instead of as a small accent.
  3. **Fix CSS .slide-bg sizing** — make sure `background-size: cover` is filling the entire viewport (it should be, but if `bg_image` is a non-full-slide crop, "cover" still leaves edges).
  4. **Rebuild from scratch** — if converter limitations are this fundamental, the right call may be to re-run the converter pipeline with shape-extraction + full-slide-render upgrades, rather than patching artifact HTML.
- **Status:** OPEN — this + #5 are the fundamental fidelity issues. Likely affects every story/decision slide with PPTX visuals.

### #7 — Two music tracks playing simultaneously on gameover
- **Severity:** MAJOR (audio cleanliness)
- **Pages:** every character gameover slide
- **Symptom:** Two tracks audible at once — sounds like the bg-music keeps playing while the gameover sound starts.
- **Likely cause:** the JS engine has BOTH a synthetic `playGameOverBuzz()` (Web Audio API oscillator, sawtooth wave 200Hz dropping to 60Hz) AND an HTML `<audio id="gameover-sound">` MP3 (Failing Defense). Both fire on slide entry — the engine wasn't designed for an external MP3 to coexist with the synthetic buzz. The two layered together explains "two tracks at once."
- **Secondary cause:** bg-music pause may not be 100% — engine pauses with `music.pause()` but the fadeIn interval that started it earlier may still be running, briefly bringing volume back up after the pause.
- **Possible fix angles:**
  1. Disable `playGameOverBuzz()` when external `gameover-sound` element exists (small JS engine patch — wrap the call in an `if (!document.getElementById('gameover-sound'))` guard)
  2. Properly clear the bg-music fadeIn interval when transitioning to gameover
  3. Add a hard 200ms ducking before the gameover sting plays
- **Status:** OPEN

### #8 — All gameover GIFs are the same within a character (scope confirmation of #1)
- **Severity:** MAJOR (repetition)
- **Pages:** every character — every gameover slide within a character uses identical GIF
- **Symptom:** failing 5+ different ways in Drake = Spongebob toilet 5 times. Same for every character. Player sees the same meme repeatedly, joke wears thin fast.
- **This is the playtest confirmation of issue #1.** v2 patch only assigned ONE primary GIF per character.
- **Possible fix:** rotate GIFs by failure type within each character — use the manifest's 4 variants per cutscene character + the failure-type → cast mapping in THEME §4. Each gameover slide should pick a different GIF variant or even a different cutscene character based on what KIND of failure it is (greedy / lazy / conned / outmuscled / indecisive).
- **Status:** OPEN

### #9 — Gameover GIF blocks the title text
- **Severity:** MAJOR (legibility)
- **Pages:** every character gameover slide
- **Symptom:** Fullscreen Tenor GIF (rendered via `.fullscreen-gif` CSS class — `position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); max-width: 80vw; max-height: 70vh`) covers the center of the slide, sitting on top of the title text and parody caption. Player can't read the gameover messaging because the meme is in front of it.
- **Likely cause:** z-index ordering. `.fullscreen-gif` z-index is 2; `.slide-content` (which holds title and body) is z-index 1. Title gets buried under GIF.
- **Connects to issues #3 and #4** — same root area (title placement vs my injected content).
- **Possible fix angles:**
  1. Move title and parody caption to z-index 5 so they sit above the GIF
  2. Add a translucent dark backdrop behind text overlay
  3. Restructure: GIF on top half of slide, title+caption on bottom half (no overlap)
- **Status:** OPEN

### #10 — Country selection only has Spain button, missing Portugal
- **Severity:** BLOCKER (gameplay path broken)
- **Page:** index.html (hub) — country selection slide
- **Symptom:** Player should be able to pick Spain OR Portugal (or England, depending on the flow). Only Spain is clickable; Portugal button is missing/non-clickable.
- **Likely cause:** Either (a) the country-selection slide's `buttons` array in SLIDES has only one entry, or (b) the slide has multiple text labels but only one bound to a click handler. Previous commit `943b343` was titled "Fix: Spain and Portugal are now separate clickable buttons on country selection slide" — could be regression after my PPTX-fidelity patch cleared `styled_texts`.
- **Status:** ✅ FIXED — added Portugal button targeting slide_6 (King John II flow), Spain button now correctly targets slide_11 (Spain flow). Previously commit 943b343 had this fix; an automated rebuild dropped it. `_patch_index_fidelity.py` restored it.

### #11 — A ton of captions are missing
- **Severity:** MAJOR (need location)
- **Page:** unknown — likely hub. Need screenshot or "on which slide?"
- **Symptom:** "Missing a ton of captions" — text labels that were in the PPTX aren't appearing in HTML.
- **Possible causes:**
  - My PPTX-fidelity patch cleared `styled_texts`. If the hub slide had text overlays NOT baked into the PPTX render (e.g., dynamic text from the engine), those are gone.
  - PPTX render might be cropping or scaling text off-screen
  - Hub-specific slide has interactive text labels that aren't visible without the JS overlay
- **Status:** ✅ FIXED — root cause found: `index.html` was missed by `_patch_pptx_fidelity.py` (the patch script only listed character HTMLs in `PDF_MAP`, not the hub). So the hub still had old broken inline base64 bg_images, AND my CSS rule `.pptx-text { display: none }` hid the text overlays that were carrying the actual content. `_patch_index_fidelity.py` repointed all 36 hub slides to `slides/columbus/page_NN.jpg` (the hub shares the Tutorial w Columbus PPTX). All other characters were already fixed.

### #12 — Button redundancy: PPTX-baked buttons + engine bottom buttons both visible
- **Severity:** MAJOR (UX clutter)
- **Pages:** Analyzer (most visible — quiz buttons appear in slide AND at bottom). Same pattern likely affects character HTMLs.
- **Symptom:** PPTX render shows the buttons baked into the slide image. Engine adds bottom buttons that work but are redundant.
- **Fix in progress:** extract exact button positions from PPTX via python-pptx, overlay invisible click hotspots at those positions, hide engine bottom buttons. Done for analyzer.html. Character HTMLs deferred.
- **Status:** ✅ FIXED for analyzer.html. Extracted exact button positions from PPTX via python-pptx, overlaid invisible click hotspots at those positions (subtle gold border on hover for discoverability), removed engine bottom buttons. Character HTMLs deferred — same approach can be applied if needed.

### #13 — No way to lose (or gameovers not being hit)
- **Severity:** BLOCKER if reproducible
- **Page:** index.html (Columbus tutorial), Spain path
- **Symptom:** Michael guessing without reading, hasn't lost yet. Tutorial has 8 gameover slides (10, 14, 16, 23, 24, 27, 30, 33). Either (a) he's making right choices by luck, OR (b) `_patch_info_advance.py` mis-converted a gameover-meant slide into an info slide with "Continue" button, skipping failures.
- **Status:** ✅ RESOLVED — false alarm. Michael confirmed: "Nevermind, you can lose…I was just lucky before." Gameovers reachable as intended.

### #3 — Captions are blocking the title
- **Severity:** MAJOR (visual/legibility)
- **Page(s):** likely gameover slides (the v2 caption injection). Possibly other slides if I patched them too.
- **Symptom:** The new caption text I added on gameover slides (e.g. "WRONG LEVERRR!", "Started from the bottom, now we're back at the bottom", "Bad form, Captain") overlaps the existing PPTX title on the same slide.
- **Likely cause:** Gameover slides already had a `title` field from the PPTX. My patch overwrote `slide.title` with the parody caption — but if the PPTX also has the title baked into `bg_image` or `styled_texts`, they're stacking visually on top of each other.
- **Possible fix angle:** position the caption ABOVE or BELOW the existing PPTX title (separate overlay element), or detect when PPTX title already exists and skip overwriting `slide.title`, just add the caption as a body subline.
- **Status:** OPEN — awaiting screenshot

---

## Things confirmed working (positive log)

- ✅ **Music (general)** — "Love the music though." Per-character royalty-free tracks landing well.
- ✅ **Hub music** — "LOVE the Time Warp Hub song" (Kevin MacLeod *Volatile Reaction*, CC-BY 4.0)

---

## Notes / questions for Michael

- Which character / which slide for issue #1 (same GIF on both branches)?
- For issue #2: does this affect every page, or just specific ones (e.g. info slides, decision slides, gameovers)?
- Screenshot request: ideally one per issue, or one screenshot showing all three at once if they overlap on a single slide.
