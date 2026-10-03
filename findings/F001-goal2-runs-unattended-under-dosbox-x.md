# F001 GOAL2 can be launched, keyed, read as text and restarted under DOSBox-X 2024.03.01 on this machine without a person (DRAFT, work in progress)

- **Status**: proposed (draft: the "Not done yet" section lists what is open)
- **Question**: Can GOAL2 be launched unattended under DOSBox-X, given one keystroke, its text screen read, and be terminated and reset to a known start state; what does the game write; does a start state replay identically; how fast can it run?
- **Tests claims**: none (no spec row exists yet); bears on G-M1 of `docs/plan.md` and on `runtime_writes` of `artifacts/known.json`
- **Experiment and runs**: E001; E001-r0001, E001-r0002, E001-r0003 (the cycle). The probes' raw outputs are `runtime/spike/measurements/*.json` (cited as M:<name>); they are not run records.
- **Artifact**: set `goal2-a949da2f`, variant none
- **Max intervention**: I2 (a savestate is written at every read; `vocabulary/interventions.md` lists a save-state as I2, the task text calls reading one I1; the records declare both)
- **Tier reached**: V2
- **Confidence**: draft, not yet stated. Launch, observe, act, terminate: 3 of 3 cycle records agree. Determinism: measured earlier in this session but the raw files were lost (see "Not done yet").

## Answer

- Best route so far: Xvfb + DOSBox-X (output=surface) + xdotool (XTEST keys) + the text screen read from a DOSBox-X savestate (Host+S), cross-checked against DOSBox-X's own PNG capture. (E001-r0001..3)
- Unattended launch to the title screen worked in 3 of 3 cycles; every `before` screen has the same sha256 (`cd7f15fb...`), and so does every `after` screen (`487df15f...`) after the key `n`. (E001-r0001, r0002, r0003)
- The video mode read from the BIOS data area is 03, 80 columns, 25 rows, in all six screen observations. (E001-r0001..3)
- The game wrote three kinds of file in the sessions tried: `SAVED.GL` or `<NAME>.GL` (169,553 bytes) on F7 or on F10 with save, and `S-1.SUM` (3,989 bytes) when a watched match is saved as a summary. (M:writes)
- The default `cycles=auto` runs the game slowly; from 3000 to 60000 cycles and `max` the title and the key-paced path to the next screens gave the same screen hashes. (M:speed)

## Method

- Machine: Ubuntu 24.04 in WSL2, kernel 6.18.40.1-microsoft-standard-WSL2; DOSBox-X 2024.03.01 SDL2 (Commit 02f36ba, apt), SDL 2.30.0; Xvfb 2:21.1.12-1ubuntu1.8; xdotool 3.20160805.1; Python 3.12.3 (standard library only). Code: `runtime/spike/` (`dbx.py`, `cycle.py`, `probe.py`, `routes.py`) at the commit named in each record or measurement.
- The game ran from a copy of the ten release files (verified against `artifacts/known.json`), never from the owner's folder.
- Config: machine `svga_s3`, memsize 16, cycles `auto`, core and cputype `auto`, `output=surface`, sound off; autoexec mounts the copy, runs `goal`, then `exit`.
- Recorded delays: key held 0.08 s, DOSBox-X host key (F12) combinations held 0.15 s; savestate file polled every 0.05 s; every wait for a screen is a bounded poll (a savestate read takes about 0.55 s) and the waits of each run are in its `log` observation.
- Screen read: Host+S writes a zip; its component `Vga` (one zlib stream) holds the text page at stream offset 0x86024 with 8 bytes per cell (character, attribute, other planes); component `Memory` holds guest memory from offset 0x78 (BIOS data area). The offset was found by matching a DOSBox-X PNG capture: 0 cells differ. This layout is specific to DOSBox-X 2024.03.01.
- Start state of the E001 records: a fresh process, nothing restored (`start_state.sha256` is that of the configuration with paths replaced).

## Observations

### Routes

| Route | launch | known screen | observe | input | terminate | reset |
| --- | --- | --- | --- | --- | --- | --- |
| A. Xvfb + xdotool + savestate read | works (E001 3 of 3) | works (title text, `cd7f15fb`) | works (text, mode 3 80x25; PNG cross-check 0 cells differ in 6 of 6 E001 reads) | works (`n` changes the screen in 3 of 3) | works (SIGTERM to the process groups, M:terminate; or in-game F10, y, n, DOSBox-X exits with code 0 by itself, M:writes w4) | works (fresh launch gives the same title hash; Host+L restored a savestate in a fresh process, see Not done yet) |
| B. SDL dummy driver, no X; AUTOTYPE; `autosave` savestates | works (3 of 3, seen in this session) | works (same title hash) | works (autosave every 2 s, same parser, same `before` and `after` hashes) | works, open loop only (AUTOTYPE `n` before `goal`) | works (`-time-limit`) | not tried: Host+L needs the mapper hotkey, which a dummy driver cannot receive; no other load control found |
| C. `/proc/<pid>/mem` scan | works | works | fails with `/usr/bin/dosbox-x`: Permission denied on `/proc/<pid>/maps` (the binary has file capability `cap_net_raw`, which makes the process non-dumpable); works with a byte-identical copy without the capability (screen equal to the savestate read, 0.2 s) | as A | as A | as A |
| D. DOSBox-X debugger | n/a | n/a | fails: no debugger in this build (no breakpoint strings in the binary; `-break-start` under a pty printed only log lines, no prompt) | n/a | n/a | n/a |
| E. PNG capture only (Host+P) | works | works (PNG identical across 3 launches) | pixels only, no text | as A | as A | as A |
| F. Clipboard (Ctrl+F5 copy-all) read through X | not tried: no xclip, xsel or other selection reader installed and none may be installed | not tried | not tried | not tried | not tried | not tried |

Routes B, C and E were measured in this session; their raw output (`routes.json`) was lost, see Not done yet.

### Machine types and memory (M:machines, M:layout)

`svga_s3`, `vgaonly`, `svga_et4000`: 720x400 capture, same lit-cell mask; `vgaonly` with memsize 1, 2, 4: same. `ega` (640x350), `cga` and `tandy` (640x400): launch, a key changes the capture, text not compared. `hercules`: fails, no capture within 10 s (not diagnosed). Savestate screen digest equal on `svga_s3` (8, 16, 32), `vgaonly` (4, 16), `svga_et4000` (M:layout); PNG and text differ by 2 cells in 4 of 6 of these reads (the cells `Y` and `N` of the title carry the blink attribute; the other two reads: 0 differ).

### Writes (M:writes; each session from a restored start state, folder compared by sha256)

| Session | Files new or changed |
| --- | --- |
| w0 Esc only | none |
| w1 F7, default name | `SAVED.GL` 169,553 B, sha256 `2f5bdbc5...` |
| w2 F7, name `zz` typed | `ZZ.GL` 169,553 B, same sha256 (name upper-cased) |
| w3 F10, y, y, default name | `SAVED.GL`, same sha256; DOSBox-X exited by itself (code 0) |
| w4 F10, y, n | none; exit code 0 |
| w5 watched match, summary saved, default name | `S-1.SUM` 3,989 B (the release file `Y.HIL` is also 3,989 B) |

The ten release files were unchanged in `.cache/goal2`.

### Speed (M:speed)

| cycles | seconds to title (poll step about 0.55) | title hash = reference | key-paced path to the next screens: seconds, hash = reference |
| --- | --- | --- | --- |
| auto | 1.87 | yes | 14.7, yes |
| max | 1.86 | yes | 13.6, yes |
| 60000 | 0.77 | yes | 13.6, yes |
| 30000 | 0.78 | yes | 13.6, yes |
| 10000 | 1.32 | yes | 13.6, yes |
| 5000 | 1.30 | yes | 14.7, yes |
| 3000 | 1.85 | yes | 14.0, yes |

Seen earlier in this session (raw file lost): a watched match played to full time with the game's own speed key raised took about 205 s at `auto`, 125 s at 5000, 65 s at 10000, 22 s at 30000, 13 s at 60000 and 8 to 14 s at `max`.

### Anomalies

- One DOSBox-X abort (`*** buffer overflow detected ***: terminated`) during a savestate, in about 700 savestates (earlier run, `cycles=auto`). `dbx.py` now fails at once when the process is gone and sends Host+S again after 3 s.
- One F7 not acted on within 1.5 s in one exploratory session; not reproduced in 4 later sessions.
- A savestate keeps the host folder drive C: was mounted from: restoring one in a session that mounted another folder made the game write into the old folder (found when saves vanished). The probes now mount one fixed folder.

## Inferences

- Route A is the best: closed loop (poll for a screen, no fixed sleeps), no state outside Xvfb and the process, a text read exact enough to hash. Route B needs no X server but is open loop and cannot restore a state; route C needs a modified launch.
- The `before` hashes are identical because the title screen has no changing content; this says nothing about randomness (E001-r0001..3).

## Alternatives considered

- "Identical before hashes show a controlled start": not excluded; the title screen is static.
- "Savestate polling changes the game": not excluded; neutrality of I2 was not tested.
- "The slow default speed is DOSBox-X's `auto`, not the game": consistent with the speed table, not separated by a test.

## What this does not establish

See "Not done yet": all untried routes (F, hercules diagnosis, other DOSBox-X versions, other `output` values than `surface`, Windows DOSBox-X) and every observation made once (the abort, the lost F7, hercules, each write session, the 2-cell blink differences, the match timings).

## Not done yet (resume here)

Open Done-when lines: 1 (route table needs the restore and routes B, C, E re-measured with kept raw files), 4 (write sessions done; the finding must still be finished and the diff checks pasted), 6 (list to be completed after the probes below).
Probes to re-run (each `python3 runtime/spike/probe.py <name>`; the chain was stopped when the owner shut the machine down, and the raw files of the earlier batches were deleted by mistake before the final chain):
- `match --cycles max 60000 30000 10000 5000 auto --reps 2 --timeout 420` (about 15 min)
- `timing` (restore delay 0 to 0.9 s then the same keys: earlier, all 8 results screens had the same hash)
- `determinism --reps 3` and `determinism --reps 3 --tag -b` (about 7 min each). Earlier results, not kept: restoring a title state and typing the same keys gave identical screens 3 of 3 except a blinking glyph on the name prompt; restoring a menu state and the keys to the results screen of the other matches gave identical screens 3 of 3 (two batches); the same plus a quick result (R) in a match gave different screens in 1 to 3 of 3 (scoreboard, commentary); fresh launches with the same keys gave identical screens in one batch and 2 of 3 in another.
- `python3 runtime/spike/routes.py` (routes B, C, E, D evidence).
- Then: write Method details, Confidence, the proposed `runtime_writes` (`SAVED.GL`, `<NAME>.GL`, `S-1.SUM`), Reproduction; paste the Done-when outputs into `scratch/pr-body.md`; open the PR.

## Where the evidence is

`runs/E001/E001-r0001.json`, `E001-r0002.json`, `E001-r0003.json`; `runtime/spike/measurements/`. No evidence bundle and no release: nothing here is a save or capture of the game's files.

## Reproduction

`bash setup/goal2-runtime.sh`, then `python3 runtime/spike/cycle.py` (three times) and `python3 runtime/spike/probe.py <probe>`.
