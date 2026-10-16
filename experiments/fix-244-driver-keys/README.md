# fix-244 driver keys

Issue 244: `runtime/driver/driver.py` sent keys with xdotool, which pressed Left Alt around every function
key, and its F12+S savestate chord left Left Alt held in the guest from the launch on. Not a research
experiment: the logs below are the fix's evidence (CLAUDE.md rule 20 for measured outputs: committed, never
overwritten). Runner: DOSBox-X 2024.03.01, Xvfb on a private display the driver picks, the verified release
`goal2-67cf27d6`.

## The fault, reproduced on the driver as it was (origin/main 0084491)

`probe.py` launches GOAL, sends `n Enter Enter Enter Enter Enter` and `F10`, and reads the BIOS keyboard
flags (0040:0017, 0040:0018, 0040:0096) and the last key the game read (DS:A976) from the savestates the
driver takes anyway.

| log | driver | 0040:0017 | 0040:0018 | Alt held | DS:A976 after F10 | BIOS buffer word |
| --- | --- | --- | --- | --- | --- | --- |
| `out/old-driver.jsonl` | the old one (a copy of origin/main) | `00001000` at all 4 reads | `00000010` | yes, at all 4 reads | `d5` (0x71 + 0x64: Alt+F10) | `7100` |
| `out/legacy-keys-on-fixed-driver.jsonl` | the fixed driver, `legacy_keys=True` | `00001000` | `00000010` | yes | `d5` | `7100` |
| `out/new-driver.jsonl` | the fixed driver | `00000000` at all 4 reads | `00000000` | no | `a8` (0x44 + 0x64: F10) | `4400` |

The four reads: the savestate that showed the title (the launch), after `n Enter x5`, after F10, and after F10
with another savestate key sent. An xinput capture on a bare Xvfb shows why: `xdotool keydown F10` sends
Alt_L (keycode 64) press, F10 press, Alt_L release, F10 release; the F12 chord sends Alt_L with F12
(`out/test-on-old-driver.txt`, the test that records raw events).

## The fix

`runtime/driver/xkeys.py`: a key is the one X keycode of its keysym, pressed and released as XTEST events with
no modifier (E031's `xtest.py` approach; an upper-case letter is sent with Left Shift around it, a keysym that
would need another modifier is refused). The savestate and load keys are Scroll Lock and Print Screen, alone,
through a mapper file the driver writes (`xkeys.mapper_text`, byte-identical to E031's `mapper-nohost.map`).
`Driver(legacy_keys=True)` keeps the old behaviour so the fault can be reproduced.

## Tests

`tests/test_driver_keys.py` (12 tests): key sending on a bare Xvfb recorded by `xinput test-xi2` (no emulator),
the mapper, and one end to end run with the emulator (`probe.py`). `out/test-on-old-driver.txt`: the same file
against the old `driver.py` (plus `xkeys.py`, which the old tree lacks): 6 failures, 2 errors (the two tests of
`legacy_keys`, which the old driver does not have); the end to end test fails with "Alt held at launch ...
00001000 00000010". `out/test-on-fixed-driver.txt`: 12 OK.

## Earlier results, three checks (`rerun.py` runs an earlier script unchanged into `out/rerun*/`, `compare.py` compares its record with the original, `compare_all.py` wrote `out/compare.txt`)

| check | original | on the fixed driver | result |
| --- | --- | --- | --- |
| E003 `d0`, fresh launch at DOS 10:00:00 on 10/04/1993, keys `n Enter Enter b o b Enter Enter Enter Enter Esc` | r0047, r0048 (and 0030/31, 0043/44) | 5 runs (`out/rerun/E003/` r0003-r0007) | the outcome E003 reports is the same in 5 of 5: main-screen digest `f64826f4...`, DS:7B62 `0xee42`, `0xf5db` at steps 3-5, DS:A9FD `0x07c9`, steps 5-11. Two intermediate observations differ, see below. |
| E006 `games`, one new game at 10:00 on 10/04/2026, same keys | r0001 | 1 run (`out/rerun/E006/E006-r0001.json`) | same: main-screen digest, the 0xEF24-byte player array and the 0x603F-byte country array (sha256 compared), DS:7B62 `0xee42`. 10 of 10 values. |
| E003 `d3b`, restore `main`, then `Esc Up Enter Enter Enter+r Enter Enter r` (letter and Enter keys through a restore) | r0049 (also r0050, r0027-29, r0040-42) | `main.sav` remade with the fixed driver (screen digest `18190236...`, the same as the recorded second `main`), 2 runs (`out/rerun/E003/` r0008, r0009) | DIFFERENT from step 5: the recorded after-`r` screen (`2e282d3e...`, seed `0xa797`) appears two reads later (step 7), and the last read is `a814ba65...` (the recorded step 6) where the original has `641ecfc6...`. Control: with the savestate key held 0.6 s (the old chord's pace) the same 2 runs are 36 of 36 values equal (`out/rerun-save-key-hold-0.6/`). |

What differs, and why (the controls are in `out/rerun-*` and tabulated by `seeds.py`, `out/compare.txt`):

- **d3b**: the fixed driver reads a screen in about 0.15 s, the F12 chord took about 0.6 s. E003's `settle`
  accepts a screen when it changed and two consecutive reads agree, so with fast reads it stops on a transient
  screen (the kick-off pitch, step 5, where the original read the half-time board), and the next key lands earlier
  than in the original. The match itself runs the same (the screen and seeds equal the recorded step 5, two reads later). Slowing only the savestate key to 0.6 s
  reproduces the record exactly. This is read pacing, not Alt.
- **d0, step 2** (`DS:7B62` after the first Enter, while the game makes the squads): `0x18bc` in all 28
  completed originals and in 4 of 4 runs with the old keys on the fixed driver; 5 of 5 distinct values with the
  fixed driver (`0x365e`, `0xdffa`, `0xf439`, `0xed0c`, `0x3055`), because the read caught the "HANG ON" screen
  (the squads still being made) where the original caught the finished country screen. Game keys the old way and
  the savestate key new: varies (`0xc411`, `0x7c38`); game keys new and the savestate key the old way: `0x18bc`;
  savestate key held 0.6 s: varies (`0x9b8b`, `0x6275`). So the old chord (with its Alt+F12 keys reaching the
  guest at every read) is what held the settle at the HANG ON screen; read pacing alone did not do it.
  F007 cites `0x18bc` as "the last squad leaves 0x18bc": that is what the old driver read at that step.
- Intermediate screen digests of `d0` steps 3-6 also differ between runs with the old keys on the fixed driver
  (an animated glyph on the country screen: `W` or a smiley), so they are not compared as outcomes.
- A defect found on the way, not fixed here: E003's `Run.add` skips a read whose `id()` it has seen, and under
  Python 3.14 a new read gets a freed read's id, so records lack steps (`out/rerun/E003/` r0001, r0002 are such
  runs, kept). `rerun.py` keeps the reads alive; the original records ran on another Python and are complete.

Not tested: E004-E014's matches, squad and tactics keys (arrow keys, Insert, Space) under the fixed driver; the
record `main` and `title` start states made with the old driver carry Alt held in their saved BIOS data, so a
restore from one still starts the guest with Alt held (the repository has none locally; remake them with the
fixed driver, `driver.py make-state title`, `E003 run.py make-main`).
