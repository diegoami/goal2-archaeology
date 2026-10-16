# fix-244 driver keys

Issue 244: `runtime/driver/driver.py` sent keys with xdotool, which (on this machine, Ubuntu 26.04) pressed
Left Alt around every function key, and its F12+S savestate chord left Left Alt held in the guest from the
launch on. Not a research experiment: the logs below are the fix's evidence (CLAUDE.md rule 20 for measured
outputs: committed, never overwritten). Runner: DOSBox-X 2024.03.01, Xvfb on a private display the driver
picks, the verified release `goal2-67cf27d6`, Ubuntu 26.04 WSL2, Python 3.14.

## The fault, reproduced on the driver as it was (origin/main 0084491)

`probe.py` launches GOAL, sends `n Enter Enter Enter Enter Enter` and `F10`, and reads the BIOS keyboard
flags (0040:0017, 0040:0018, 0040:0096) and the last key the game read (DS:A976) from the savestates the
driver takes anyway.

| log | driver | 0040:0017 | 0040:0018 | Alt held | DS:A976 after F10 |
| --- | --- | --- | --- | --- | --- |
| `out/old-driver.jsonl` | the old one (a copy of origin/main) | `00001000` at all 4 reads | `00000010` | yes, at all 4 reads | `d5` (0x71 + 0x64: Alt+F10) |
| `out/legacy-keys-on-fixed-driver.jsonl` | the fixed driver, `legacy_keys=True, mapper="dosbox"` | `00001000` | `00000010` | yes | `d5` |
| `out/new-driver.jsonl` (hold 0.15 s) and `out/new-driver-default-pace.jsonl` (default 0.52 s) | the fixed driver | `00000000` at all 4 reads | `00000000` | no | `a8` (0x44 + 0x64: F10), `4400` in the BIOS buffer |

The four reads: the savestate that showed the title (the launch), after `n Enter x5`, after F10, and after F10
with another savestate key sent. An xinput capture on a bare Xvfb shows why: `xdotool keydown F10` sends
Alt_L (keycode 64) press, F10 press, Alt_L release, F10 release; the F12 chord sends Alt_L with F12
(`out/test-on-old-driver.txt`).

### The fault is this machine's, not the earlier records'

xdotool 3.20160805.1 and Xvfb 21.1.22 were installed here on 2026-10-10 (Ubuntu 26.04). The 458 driver records
of E001-E015 were made on Ubuntu 24.04 WSL2, Python 3.12 (`machine` in the records). The 34 published
savestates of the driver's experiments (E005, E006, E010, E011, E013, E014, E018; `published_states.py`
downloaded each, the sha256 matched the manifest) show **no Alt held** (`out/published-states.tsv`:
`0040:0017` and `0040:0018` zero in all 34), but 11-16 of the 16 BIOS buffer words are a plain F12 (`0x8600`):
the old chord pressed F12 into the guest at every read. So earlier results carry no Alt-held bias, and carry a
plain F12 key per read; the fixed driver puts no key into the guest at a read.

## The fix

`runtime/driver/xkeys.py`: a key is the one X keycode of its keysym, pressed and released as XTEST events with
no modifier (E031's `xtest.py` approach; an upper-case letter is sent with Left Shift around it, a keysym that
would need another modifier is refused). The savestate and load keys are Scroll Lock and Print Screen, alone,
through a mapper file the driver writes (`xkeys.mapper_text`, byte-identical to E031's `mapper-nohost.map`).
Two independent settings (review R1 of the PR: the first version tied them together):

- `legacy_keys`: the **transport**, raw XTEST keycodes (default) or xdotool.
- `mapper`: what the savestate and load keys **are**: `"nohost"` (default; the driver writes the mapper that binds
  them to Scroll Lock and Print Screen), `"dosbox"` (no mapper file: DOSBox-X's own binds, the F12 chord), or a
  mapper file. The driver reads the savestate, load and screenshot binds of the mapper in effect
  (`xkeys.hostkeys`) and presses those keys, so the mapper and the keys cannot disagree. A bind it cannot read
  (another modifier, no such bind, a scancode with no name) is a `ValueError` when the driver is made, and
  `play.py serve` exits with `play.py serve: <reason>` before launching anything.

`Driver(legacy_keys=True, mapper="dosbox")` is the old driver, kept to reproduce the fault. In E031's `play.py` the
settings are `--keys {raw,xdotool}`, `--fkeys {raw,xdotool}` (function keys and the F12 of a chord; default as
`--keys`) and `--mapper FILE|''`. The savestate `s` of each combination (`tests/test_driver_keys.py` `KeyCalls`
asserts the calls; `out/combos.jsonl` ran each once in the emulator):

| transport | mapper | keys pressed for the savestate | in the emulator (`out/combos.jsonl`) |
| --- | --- | --- | --- |
| raw (default) | `nohost` / `mapper-nohost.map` (default) | Scroll Lock, raw | no Alt, F10 = `a8` |
| raw, `--fkeys xdotool` | `mapper-nohost.map` | Scroll Lock, raw; F-keys by xdotool | no Alt held, F10 = `d5` (Alt+F10) |
| xdotool (`--keys xdotool`) | `mapper-nohost.map` | Scroll Lock, xdotool | no Alt held, F10 = `d5` |
| raw | `dosbox` / `--mapper ''` / a file with the F12 chords | F12 + s, raw (no Alt) | no Alt, F10 = `a8` |
| raw, `--fkeys xdotool` | `--mapper ''` (the guide's reproduction) | F12 by xdotool, s raw | Alt held, F10 = `d5` |
| xdotool (`--keys xdotool`) | `--mapper ''` | F12 + s, xdotool (the old driver) | Alt held, F10 = `d5` |
| any | a file whose binds are not usable as a set (below) | refused (`ValueError`) | not launched |

The whole bind set is validated when the driver is made (`xkeys.hostkeys`; review round 2), and `ValueError` names the
reason for: the same key or chord bound to two of savestate, load and screenshot (they could not be told apart);
a savestate or load line that is missing, has no bind, or has an unreadable bind (`joy 1`, `key abc`, a scancode
with no name) on any of its binds; a modifier other than `host`; the host key F12 itself bound to an action
(`key 69`, `key 69 host`); two lines of one action with different binds (which applies is ambiguous; identical
repeats are accepted); a key name that is no X keysym. Before DOSBox-X starts, `launch` checks that each key the raw
transport sends has a keycode on the display and needs no modifier (`xkeys.check_sendable`). `play.py serve` exits
non-zero with `play.py serve: <reason>` in both cases. `tests/test_driver_keys.py` `MapperSets` (no emulator, no X)
has a test for each refusal and for the valid sets; on c9ce10f 9 of its tests fail and the keycode check errors
(`out/test-mapper-sets-on-c9ce10f.txt`), the ambiguous savestate/load mapper among them.

In the review's two failing cases: with a mapper other than `mapper-nohost.map` the first version pressed Scroll Lock
raw whatever the file bound, and with `--fkeys xdotool` under the normal mapper it sent F10 raw. Both fail on
88edbd2 (`out/test-keycalls-on-88edbd2.txt`: the two `play_` tests that named them, and the other combination tests).

**Read pace** (`Driver(save_hold=...)`, default `SAVE_HOLD` = 0.52 s). The old chord held 3 steps of
`HOSTKEY_HOLD` = 0.15 s (0.45 s) and made 4 xdotool calls: the gap between consecutive chords logged in
E003-r0047 and r0049 has median 0.536 s and 0.534 s (min 0.512; 29 and 30 gaps). A single key held h takes
h + 0.013 s (median 0.163 s at h = 0.15), so h = 0.52 s gives the old 0.53 s per read. At 0.15 s the first
re-runs of E003 d3b diverged from their record (below); the default keeps the old pace so earlier
experiments reproduce. The coordinator's suggested 0.6 s also reproduces d3b (36 of 36, 2 of 2); 0.52 s is the
measured pace.

## Tests

`tests/test_driver_keys.py` (38 tests): key sending on a bare Xvfb recorded by `xinput test-xi2` (no emulator),
the key calls of each combination of transport and mapper (`KeyCalls`, no X at all),
the mapper, the default hold and a custom `save_hold`, and one end to end run with the emulator (`probe.py`).
- `out/test-on-old-driver.txt`: against origin/main's `driver.py` (plus `xkeys.py`, which that tree lacks): the
  Alt tests fail, 6 failures and 2 errors (12 tests then).
- `out/test-on-previous-commit-dee1d1a.txt`: the new hold tests on the commit before `save_hold` existed: 2 errors
  (`unexpected keyword argument 'save_hold'`, `no attribute 'SAVE_HOLD'`).
- `out/test-with-save-hold-0.15-mutation.txt`: `SAVE_HOLD` mutated to 0.15: the default-pace test fails
  (`0.52 != 0.15`).

## Earlier results, three checks (`rerun.py` runs an earlier script unchanged into `out/rerun*/`, `compare.py` compares its record with the original, `compare_all.py` wrote `out/compare.txt`)

At the default pace (`out/rerun-default/`):

| check | original | on the fixed driver, default pace | result |
| --- | --- | --- | --- |
| E003 `d0`, fresh launch at DOS 10:00:00 on 10/04/1993, letter keys, Enter, Esc | r0047, r0048 (and 0030/31, 0043/44) | 4 runs completed (`rerun-default/E003/` r0004-r0007; r0003 aborted, DOSBox-X exit -6 in a savestate) | the outcome E003 reports is the same in 4 of 4: main-screen digest `f64826f4...`, DS:7B62 `0xee42`, `0xf5db` at steps 3-5, DS:A9FD. **One recorded intermediate observation still differs**: DS:7B62 at step 2 (`0x18bc` in all 28 completed originals) is `0x27d3`, `0x6be3`, `0x2bcd`, `0x2bcd`. |
| E006 `games`, one new game at 10:00 on 10/04/2026 | r0001 | 1 run (`rerun-default/E006/E006-r0002.json`) | same: main digest, player array and country array (sha256), DS:7B62; 10 of 10 values |
| E003 `d3b`, restore `main`, `Esc Up Enter Enter Enter+r Enter Enter r` (a remade `main.sav`, screen digest `18190236...` as the recorded second `main`) | r0049 (also r0050, r0027-29, r0040-42) | 2 runs (`rerun-default/E003/` r0001, r0002) | same: 36 of 36 values, last read `641ecfc6...` in both |

Why d0 step 2 differs, from the controls (tabulated by `seeds.py`, `out/compare.txt`): at step 2 the game is making
the squads and shows the "HANG ON" screen. With the old chord (a function key pressed into the guest at every
read) the settle never accepted that screen and read the finished country screen: seed `0x18bc`. A plain F12
pressed into the guest before each read on the fixed driver (`--f12-per-read`, `out/rerun-f12-per-read/`) gives
`0x18bc` in 3 of 3; the old chord on the fixed game keys (`--legacy-only save`) gives `0x18bc` in 4 of 4; the old
game keys with the new savestate key vary (`0xc411`, `0x7c38`); holding the new key longer (0.6 s) varies
(`0x9b8b`, `0x6275`). So the step-2 value in the records is a product of the key the old read pressed into the
guest, not of the pace. The fixed driver does not press it, and does not reproduce that one intermediate value.
`F007` cites `0x18bc` ("the last squad leaves `0x18bc`"): that is what the old driver read at that step.
Intermediate screen digests of `d0` steps 3-6 also differ between runs with the old keys on the fixed driver (an
animated glyph on the country screen, `W` or a smiley), so they are not compared as outcomes.
A control that held Left Alt down at the X level (`--hold-alt`, `out/rerun-alt-held/`) aborted: Alt+Enter is
DOSBox-X's fullscreen key, so it is not a stand-in for the guest-only Alt of the fault; no conclusion from it.

First re-runs, made when the savestate key was held 0.15 s (`out/rerun/`, kept): d0 outcome same and step 2 varied;
E006 same; d3b **different** from step 5 (36 values: 26 equal): a read took 0.163 s, `settle` stopped on the kick-off
pitch where the original read the half-time board, so the record's after-`r` screen came two reads later and the
last read was `a814ba65...` instead of `641ecfc6...`. This is what the default pace fixes.

Also found, not fixed: E003's `Run.add` skips a read whose `id()` it has seen; under Python 3.14 (this machine) a
new read gets a freed read's id, so records lose steps (`out/rerun/E003/` r0001, r0002 are such runs, kept); the
originals ran on Python 3.12 and are complete. `rerun.py` keeps the reads alive. DOSBox-X exited with -6 during a
savestate twice (the default-pace d0 r0003 and one control that used the old chord), not after F1.

Not tested: the matches, squads and tactics of E004-E014 (arrow keys, Insert, Space) under the fixed driver.
