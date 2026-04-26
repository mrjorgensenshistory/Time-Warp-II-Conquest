================================================================
Time Warp II: Conquest - Audio Manifest
================================================================

STATUS: Manifest + license files prepped. Downloads BLOCKED in the
agent session by sandbox (no outbound HTTP). Run _download.py
yourself from a Windows command line to fetch the 9 Kevin MacLeod
tracks. Drake + cannon SFX are manual-Pixabay downloads.

----------------------------------------------------------------
TO FINISH THE AUDIO PASS
----------------------------------------------------------------

1) Open Command Prompt or PowerShell and run:

   python "F:\Michael's\ACE\US History\Time-Warp-II-Conquest\audio\_download.py"

   This grabs all 9 Kevin MacLeod tracks (about 45-60 MB total) and
   reports OK/FAIL per file with size + MP3-magic verification.

2) Manually source the Drake track from Pixabay. See:
   audio\drake\LICENSE.txt for search URLs and decision criteria.
   Save as: audio\drake\main.mp3
   Then fill in the ATTRIBUTION block in that LICENSE.txt.

3) Manually source the cannon SFX from Freesound or Pixabay. See:
   audio\stings\LICENSE.txt for URLs.
   Save as: audio\stings\cannon.mp3

4) Audition each track in VLC or browser. If any sound wrong for
   their slot, swap to the ALT IF MISS option listed in that
   folder's LICENSE.txt.

----------------------------------------------------------------
TRACK MAP
----------------------------------------------------------------

Slot               File                          Track / Source
-----------------  ----------------------------  ------------------------------------
Hub                audio/hub/main.mp3            Volatile Reaction (K. MacLeod, CC-BY)
Columbus           audio/columbus/main.mp3       Tudor Theme (K. MacLeod, CC-BY)
Corte-Real         audio/cortereal/main.mp3      Anamalie (K. MacLeod, CC-BY)
Da Gama            audio/dagama/main.mp3         Five Armies (K. MacLeod, CC-BY)
Drake (PUBLIC)     audio/drake/main.mp3          [TBD - Pixabay trap, manual DL]
Magellan           audio/magellan/main.mp3       Long Note Three (K. MacLeod, CC-BY)
Narvaez            audio/narvaez/main.mp3        Spanish Jam (K. MacLeod, CC-BY)
Raleigh            audio/raleigh/main.mp3        Court and Page (K. MacLeod, CC-BY)
Game-over sting    audio/stings/gameover.mp3     Sad Trombone (K. MacLeod, CC-BY)
Fail sting (long)  audio/stings/fail.mp3         Failing Defense (K. MacLeod, CC-BY)
Cannon SFX         audio/stings/cannon.mp3       [TBD - Freesound CC0, manual DL]

----------------------------------------------------------------
CREDITS PAGE BLOCK (paste into hub credits)
----------------------------------------------------------------

MUSIC
-----
"Tudor Theme", "Anamalie", "Five Armies", "Long Note Three",
"Spanish Jam", "Court and Page", "Volatile Reaction",
"Sad Trombone", and "Failing Defense" by Kevin MacLeod
(incompetech.com), licensed under Creative Commons Attribution 4.0:
http://creativecommons.org/licenses/by/4.0/

[Drake slot - fill after manual download]
Music by [Pixabay Uploader] from Pixabay (pixabay.com),
Pixabay Content License.

SOUND EFFECTS
-------------
Cannon SFX: [fill after manual download]
  Source: Freesound.org / Pixabay (CC0)

----------------------------------------------------------------
HARD NOs (must hold true after download)
----------------------------------------------------------------
[ ] No Pirates of the Caribbean / Hans Zimmer
[ ] No Master & Commander / Black Sails / commercial soundtracks
[ ] No Drake (rapper) actual recordings or samples on PUBLIC repo
[ ] Every file <= a verified license in its folder's LICENSE.txt
[ ] drake_classroom.html and audio/drake_classroom/ are gitignored
