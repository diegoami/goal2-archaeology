# F001 GOAL2 can be launched, keyed, read as text, terminated and restored under DOSBox-X 2024.03.01 on this machine without a person

- **Status**: proposed
- **Question**: Can GOAL2 be launched unattended under DOSBox-X, given one keystroke, its text screen read, and be terminated and reset to a known start state; what does the game write; does a start state replay identically; how fast can it run? (T02, G1)
- **Tests claims**: none (no spec row exists yet); bears on G-M1 of `docs/plan.md` and on `runtime_writes` of `artifacts/known.json`
- **Experiment and runs**: E001; E001-r0001 … E001-r0006 (the cycle). The probes' raw outputs are `runtime/spike/measurements/*.json`, cited as M:<file name without `.json`>; they are measurements, not run records, so the five bullets that rest on them cite no run id and sit under `## Claims resting on probe measurements, with no run record`, outside the sections `tools/check_citations.py` checks; turning probes into `run/1` records belongs to the reusable driver, not this spike.
- **Artifact**: set `goal2-a949da2f`, variant none
- **Max intervention**: I2 (a savestate is written at every read; `vocabulary/interventions.md` lists a save-state as I2, the task text calls reading one I1; the records declare both)
- **Tier reached**: V2
- **Confidence**: unreviewed (status `proposed`) — behavioural only; launch, observe, act and terminate agree in 6 of 6 cycle records (two sessions, code `fc00e8c` and `c8fffd9`); the restore of a savestate was verified by screen digest in 44 of 44 restores (M:determinism, M:determinism-b, M:timing, M:match-speed); determinism: identical within each batch, different between batches (Observations); the alternatives below are not excluded

## Answer

- Best route: **A**, Xvfb + DOSBox-X (`output=surface`) + xdotool (XTEST keys), the text screen read from a DOSBox-X savestate (Host+S), cross-checked against DOSBox-X's PNG capture (Host+P). (E001-r0001 … r0006)
- Unattended launch to the title screen worked in 6 of 6 cycles; every `before` screen has sha256 `cd7f15fb…`, every `after` screen (key `n`) `487df15f…`. The video mode read from the BIOS data area is 03, 80 columns, 25 rows, in all 12 reads. (E001-r0001 … r0006)
- Reset: a fresh launch gives the same title screen (6 of 6, E001-r0001 … E001-r0006); Host+L restores a savestate in a fresh process, and the restored screen digest equals the saved one in 44 of 44 restores, 1.03 to 1.05 s after the key (M:determinism, M:determinism-b; also M:timing, M:match-speed).

## Method

- Machine: Ubuntu 24.04 in WSL2, kernel 6.18.40.1-microsoft-standard-WSL2; DOSBox-X 2024.03.01 SDL2 (apt), xdotool 3.20160805.1, Xvfb 2:21.1.12-1ubuntu1.8, Python 3.12.3 (standard library only); each measurement file and record names its versions and the commit of the code that ran (`versions`, `code_commit`). Code: `runtime/spike/` (`dbx.py`, `cycle.py`, `probe.py`, `routes.py`).
- The game ran from a copy of the ten release files (verified against `artifacts/known.json` by `setup/goal2-runtime.sh` and by `cycle.py`), never from the owner's folder; each sessgition copied them into a folder under `scratch/` (git-ignored).
- Config: machine `svga_s3`, memsize 16, cycles `auto` unless a probe sets it, core and cputype `auto`, `output=surface`, sound off; autoexec mounts the copy, runs `goal`, then `exit`.
- Delays: key held 0.08 s, DOSBox-X host key (F12) combinations held 0.15 s; savestate file polled every 0.05 s. In the cycle (E001) and in the `determinism`, `timing`, `speed` and `layout` probes every wait for a screen is a bounded poll or a delay written into the record or measurement (the waits of each run are in its `log` observation; `timing` writes its extra wait of 0, 0.3, 0.6 or 0.9 s after a verified restore). Not every wait is a poll: the `writes`, `terminate` and `match` probes also used the fixed delays in the table below, which their measurement files do not record; `machines` used a delay of 3.0 s before each capture, recorded as `delay_seconds_before_capture`.

| Fixed delay | Where (`probe.py`) | Measurement affected |
| --- | --- | --- |
| 0.15 s after each typed character, then 0.3 s before the screen read | `probe_writes`, session w2 (typing `zz`) | M:writes |
| 1.0 s after the last key, before the folder is listed (`after`) | `probe_writes`, sessions w0 … w4 | M:writes |
| 1.5 s after each Enter while looking for the summary prompt, 1.5 s after `y`, 1.5 s after the final Enter before the folder is listed | `probe_writes`, session w5 | M:writes |
| 1.0 s after each of F10, y, n | `probe_terminate`, the in-game quit row | M:terminate (its `seconds_after_last_key` includes the last 1.0 s) |
| 1.5 s after each Enter after FULL TIME, before the screen is sampled | `probe_match` | M:match-speed (`after_full_time`, `folder_changes`) |

From this round the code writes these values into each new measurement as `fixed_delays_seconds`; the files above were not re-run.

- Screen read: Host+S writes a zip; its component `Vga` (one zlib stream) holds the text page at stream offset 0x86024, 8 bytes per cell (character, attribute, other planes); component `Memory` holds guest memory from offset 0x78 (BIOS data area). The offset was found by matching a DOSBox-X PNG capture (M:layout `base`, `mem_header`). This layout is specific to DOSBox-X 2024.03.01.
- Start state of the E001 records: a fresh process, nothing restored (`start_state.sha256` is that of the configuration with paths replaced). The probes' start states are `title.sav` (title screen) and `main.sav` (after the keys `TO_MAIN` of `probe.py`), kept under `.cache/states/` (git-ignored, never committed); their sha256 and screen digests are in the `states` field of M:determinism, M:determinism-b, M:timing and M:match-speed.
- During the probes of 2026-10-04 another project's DOSBox-X and Xvfb sessions ran on the same machine (seen at 08:31); wall-clock times may carry that load.

## Observations

### Routes

| Route | launch | known screen | observe | input | terminate | reset |
| --- | --- | --- | --- | --- | --- | --- |
| A. Xvfb + xdotool + savestate read | works (E001-r0001 … r0006, 6 of 6) | works (title text `cd7f15fb`, 6 of 6) | works (text, mode 03 80x25; PNG cross-check 0 cells differ in 10 of 12 reads, 2 cells in the `before` reads of r0004 and r0006) | works (`n` changes the screen, 6 of 6) | works: SIGTERM to the process groups, dosbox-x return code 1 after 0.02 s (M:terminate); in-game F10, y, n: DOSBox-X exits by itself with code 0 (M:terminate, M:writes w4) | works: fresh launch (6 of 6 the same title); Host+L in a fresh process, 44 of 44 restored digests equal (M:determinism, M:determinism-b, M:timing, M:match-speed) |
| B. SDL dummy driver, no X; `autotype`; `autosave` savestates | works (3 of 3, return code 0, `-time-limit 14`) (M:routes `b-headless`) | works (first autosave `cd7f15fb`, 3 of 3) | works (autosave every 2 s, the same parser; mode 03 80x25) | works, open loop only (`autotype -w 2 -p 0.5 n`: the autosave at 2 s is `487df15f`, 3 of 3) | works (`-time-limit`) | not tried: Host+L needs the mapper hotkey, which a dummy driver cannot receive; no other load control was found |
| C. `/proc/<pid>/mem` scan | works | works | fails with `/usr/bin/dosbox-x`: `Permission denied` on `/proc/<pid>/maps` (2 of 2; the binary carries `cap_net_raw=ep`); works with a byte-identical copy without the capability (2 of 2, the screen equal to the savestate read, 0.12 s) (M:routes `c-procmem`) | as A | as A | as A |
| D. DOSBox-X debugger | not tried: no debugger | not tried | fails: the binary has no `Breakpoint` or `MEMDUMP` string (it has `Enter Debugger Command` once and `debugger` 4 times); `-break-start` under a pty printed 2,836 bytes in 9 s, no line other than `LOG:` lines, no escape sequence, no prompt (M:routes `debugger`) | not tried | not tried | not tried |
| E. PNG capture only (Host+P) | works | works (PNG sha256 identical in 3 of 3 launches, 720x400) (M:routes `f-png`) | pixels only, no text | as A | as A | as A |
| F. Clipboard (DOSBox-X copy-all) read through X | not tried: no xclip, xsel or other selection reader is installed, and the task installs nothing | not tried | not tried | not tried | not tried | not tried |

Route E's PNG had 811 lit cells in M:routes and 813 in M:machines; the title carries two blinking cells (below), not checked as the cause.

### Machine types and memory (M:machines, M:layout)

`svga_s3`, `vgaonly`, `svga_et4000` (memsize 16): 720x400 capture, the same lit-cell mask on the title, and a key changes it; `vgaonly` with memsize 1, 2, 4: the same. `ega` (640x350), `cga` and `tandy` (640x400): launch, and a key changes the capture; text not compared. `hercules`: fails, `no capture within 10s` (not diagnosed). The savestate screen digest is `cd7f15fb…` on `svga_s3` (memsize 8, 16, 32), `vgaonly` (4, 16) and `svga_et4000` (16), mode 03 80x25 in each; PNG and text differ by 2 cells in 4 of these 6 reads and by 0 in the others (M:layout `cells_differing`). That the 2 cells are the `Y` and `N` of the title prompt, which carry the blink attribute, is an inference: the cell positions are not in the measurement.

### Writes (M:writes; code `fc00e8c`; each session from a restored `main.sav`, the game folder compared by sha256 before and after)

| Session | Files new or changed |
| --- | --- |
| w0 Esc only, no save | none |
| w1 F7, default name | `SAVED.GL` 169,553 B, sha256 `2f5bdbc5…` |
| w2 F7, name `zz` typed | `ZZ.GL` 169,553 B, the same sha256 (the name is upper-cased) |
| w3 F10, y, y, default name | `SAVED.GL` 169,553 B, the same sha256; DOSBox-X exited by itself (code 0) |
| w4 F10, y, n | none; DOSBox-X exited by itself (code 0) |
| w5 a match played at `cycles=10000`, then the prompt "Do you want to save the match summary to disk? (Y/N)", y, default name | `S-1.SUM` 3,989 B, sha256 `18fde813…` |

The ten release files were unchanged in the game folder after the sessions (M:writes `release_files_unchanged_in_cache`). The release file `Y.HIL` has the same size as `S-1.SUM` (3,989 B; sha256 `fdeb0064…`, different). In the 12 matches of M:match-speed the folder did not change (`folder_changes` empty in 12 of 12): the summary prompt was among the sampled screens, and was answered with Enter, in the 6 runs at 10000, 5000 and `auto`; at 30000, 60000 and `max` it was not among the sampled screens.

### Determinism (M:determinism, code `b508a61`; M:determinism-b, code `f8cdb14`; three repetitions per experiment; the same `title.sav` and `main.sav` in both)

| Experiment | within batch a | within batch b | a vs b |
| --- | --- | --- | --- |
| D0 fresh launch, the same 11 keys to the main menu | final screen identical 3 of 3; row 9 (the name prompt's cursor cell) differs at 2 steps | final identical 3 of 3; row 9 differs at 3 steps | final screens differ: the next opponent (Holland / Austria) and the numbers beside "World" (14 / 20) and "Europe" (3 / 27) |
| D2 restore `main.sav`, Esc Up Enter (results of the other matches) | identical 3 of 3 at every step | identical 3 of 3 | identical (`065ad6c4`) |
| D3 restore `main.sav`, the D2 keys, then into a match, `c`, quick result `r`, Enter Enter `r` | identical 3 of 3 at every step | identical 3 of 3 | differ from the key `r` on: a: Denmark 0, France 1, FULL TIME, scorer Boli 47; b: Denmark 1, France 0 (a goal by Piechnik), and the last screen is the half-time team screen |
| D4 restore `title.sav`, the D0 keys | final identical 3 of 3; row 9 differs at 4 steps | final identical 3 of 3; row 9 differs at 2 steps | identical (`fa8613ef`) |

D1 (restore `main.sav`, no keys) has no steps to compare; its restores matched the saved digest (3 of 3 per batch). M:timing (8 runs: the D2 keys after 0, 0.3, 0.6 or 0.9 s of extra wait, twice each): the three screens identical in 8 of 8, with the digests of D2 (`fa8613ef`, `536079ad`, `065ad6c4`).

### Speed (M:speed, code `fc00e8c`; M:match-speed, code `6959db9`)

| cycles | seconds to title (M:speed) | title and main digests = reference (M:speed) | match, kick-off to HALF TIME, s (2 runs) | kick-off to FULL TIME, s (2 runs) |
| --- | --- | --- | --- | --- |
| auto | 1.87 | yes, yes | 89.07, 87.90 | 185.23, 182.04 |
| max | 1.86 | yes, yes | 0.93, 0.94 | 9.34, 9.37 |
| 60000 | 0.77 | yes, yes | 0.92, 0.93 | 12.49, 12.58 |
| 30000 | 0.78 | yes, yes | 9.43, 9.46 | 20.27, 20.35 |
| 10000 | 1.32 | yes, yes | 28.24, 28.17 | 58.42, 59.69 |
| 5000 | 1.30 | yes, yes | 55.30, 55.19 | 114.40, 115.08 |
| 3000 | 1.85 | yes, yes | not measured | not measured |

The key-paced path from the title to the main screen took 13.6 to 14.7 s at every setting (M:speed `seconds_title_to_check_out_screen`): it is bounded by the settle polls, not by the game. At `max` and 60000 the first half took under 1 s and the second 6.5 to 9.7 s (M:match-speed `second_half_started_after_s`, `full_time_after_s`); not explained.

### Anomalies

- In an earlier round of this task (raw output not kept), DOSBox-X aborted once with `*** buffer overflow detected ***: terminated` while writing a savestate, and one F7 was not acted on within the poll; neither recurred in the re-run measurements (every row of M:determinism, M:determinism-b, M:timing and M:match-speed finished without `error`). `dbx.py` now fails at once when the process is gone and sends Host+S again when no savestate appears within 3 s.
- A savestate keeps the host folder drive C: was mounted from: restoring one in a session that mounted another folder made the game write into the old folder (found when saves vanished in that earlier round). The probes mount one fixed folder (`scratch/probe/game`, recreated per session).

## Inferences

- Route A is the best: closed loop (poll for a screen, no fixed sleeps), restorable, no state outside Xvfb and the process, and a text read exact enough to hash (E001-r0001 … E001-r0006). Route B needs no X server but is open loop and cannot restore; route C needs a launch from a modified copy of the binary.
- The identical `before` hashes of E001-r0001 … E001-r0006 say only that the title screen is static; they say nothing about randomness.

## Claims resting on probe measurements, with no run record

These bullets rest on `runtime/spike/measurements/*.json` (cited as M:file-name), which are measurements, not run records; no run id exists to cite. They were `## Answer` and `## Inferences` bullets and are unchanged except that `<NAME>` is written `NAME` (U26).

- Proposed `runtime_writes`: `NAME.GL` (169,553 bytes; default name `SAVED.GL`), written by F7 or by F10 with save, and `NAME.SUM` (3,989 bytes; default name `S-1.SUM`), written when the match summary is saved after a match. (M:writes)
- Determinism: from one start state, the same keys gave identical screens within a batch of three (except a blinking cursor cell on the name prompt), but a quick result from the same restored savestate gave a different match in two batches about 20 minutes apart, and fresh launches gave a different main screen in the two batches. Something that is neither the start state nor the key sequence is an input. (M:determinism, M:determinism-b)
- Speed: with the game's own speed raised, a match from kick-off to FULL TIME took about 184 s at `cycles=auto`, 115 s at 5000, 59 s at 10000, 20 s at 30000, 12.5 s at 60000 and 9.4 s at `max`; all 12 matches finished and the menus answered at every setting. (M:match-speed)
- From the determinism table: neither a savestate nor a fresh launch pins everything the game uses. Restoring `title.sav` gave the same main screen in both batches while fresh launches did not, and restoring `main.sav` gave the same quick result within a batch but not across batches. An input that changes slowly (minutes) and is not in the savestate is consistent with this, for example the host clock read through DOS; not tested. A driver that needs reproducible matches must control that input (I3) or record it.
- `max` is usable for driving: every match finished, the menus answered, and the screens of M:speed matched the reference at every setting. Whether a match's outcome depends on the cycles setting was not measured.

## Alternatives considered

- "The between-batch differences come from the host clock": consistent, not tested (no run with a fixed DOS date and time).
- "They come from timing jitter of the keys": not supported within a batch (8 of 8 identical over four extra waits in M:timing, 3 of 3 per experiment), not excluded across batches; the batches ran under different machine load (Method).
- "Savestate polling changes the game": not excluded; the neutrality of I2 was not tested.
- "The slow default speed is DOSBox-X's `auto`, not the game": consistent with the speed table, not separated by a test.
- "`Y.HIL` is a match summary": not shown; it only has the same size as `S-1.SUM`.

## What this does not establish

- **Untried routes**: F (the clipboard read through X; no selection reader installed); B's reset (no load control without a mapper hotkey); D in any build with a debugger (only apt's build was tried); other DOSBox-X versions, a Windows DOSBox-X, `output` values other than `surface`, other `core` and `cputype` values; `hercules` was not diagnosed; text equality on `ega`, `cga` and `tandy` was not compared.
- **Observations made once only**: each write session w0 … w5 (one session each, M:writes), so the file sizes and names of `runtime_writes` rest on one save per kind; routes B to E (one probe run, M:routes, with 2 or 3 repetitions inside it); the time to the title and the key path per cycles setting (one run per setting, M:speed); each machine and memory configuration (one run each, M:machines, M:layout); SIGTERM and in-game quit termination (one each, M:terminate); the DOSBox-X abort and the unacted F7 (one each, earlier round, no raw file); the drive-folder behaviour of a savestate (one session, earlier round, no raw file).
- **Observed in two batches only**: determinism (M:determinism, M:determinism-b) and the match times (2 runs per setting, M:match-speed). What varies between batches, and its source, is not established.
- Whether the outcomes of M:writes, M:terminate and the post-full-time screens of M:match-speed hold at other values of the fixed delays listed under Method: each was measured at one value only (for example, whether a save is complete 1.0 s after the key, or whether the summary prompt at 30000, 60000 and `max` was passed within one 1.5 s step).
- Whether the quick result and a played match depend on `cycles`, on the savestate polling, or on wall-clock time.
- The format and content of `.GL` and `.SUM` files, and whether other paths (replays F3, summaries F4, printing F5, the editor `ALTER.EXE`, the end of a tournament) write other files: `runtime_writes` is complete only for the sessions in the Writes table.

## What changed against the earlier round's notes

The earlier round's raw files for these probes were lost; the re-run measurements replace its notes:

- Match times at `auto` 184 s (notes: about 205), 5000 115 s (125), 10000 59 s (65), 30000 20 s (22), 60000 12.5 s (13), `max` 9.4 s (8 to 14) (M:match-speed).
- The quick result from one restored savestate was identical 3 of 3 within each batch (notes: different in 1 to 3 of 3) and differed between the two batches (M:determinism, M:determinism-b).
- Fresh launches with the same keys: identical 3 of 3 in each batch (notes: 3 of 3 in one batch, 2 of 3 in another), different between batches.
- The PNG cross-check of the cycle: 2 cells differ in 2 of 12 reads (notes: 0 in 6 of 6) (E001-r0004, r0006).

## Where the evidence is

`runs/E001/E001-r0001.json` … `E001-r0006.json`; `runtime/spike/measurements/` (`determinism.json`, `determinism-b.json`, `layout.json`, `machines.json`, `match-speed.json`, `routes.json`, `speed.json`, `terminate.json`, `timing.json`, `writes.json`). No evidence bundle and no release: the savestates and captures stay in `scratch/` and `.cache/` (git-ignored), since they hold the game's files.

## Reproduction

`bash setup/goal2-runtime.sh` (prints `ready`), then `python3 runtime/spike/cycle.py` (one record per run, refused while `runtime/spike/` has uncommitted changes), `python3 runtime/spike/probe.py <probe>` (`determinism`, `timing`, `match`, `speed`, `writes`, `machines`, `layout`, `terminate`; `--tag=-b` names a second batch; a run never overwrites an earlier measurement file) and `python3 runtime/spike/routes.py`. Validate the records with `python3 tools/validate_runs.py runs/E001`.
