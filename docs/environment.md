# Environment

[designed: owner, 2026-10-22] What a session needs to run the original and the static tools. The
review harness's sections (OpenCode 2 and its guard, provider logins, quota tracking, the old
reviewer's permissions and data directory, the old session hook) were removed with it; they are on
the branch `local`. A cloud session is set up by `tools/cloud_setup.sh` ([cloud.md](cloud.md)).

Locally you need `python3` (3.11 or later) with `tools/static/requirements.txt` and
`runtime/emul/requirements.txt`, `gh` logged in, and the tools below. Reviews run any CLI directly
(`tools/review_pr.sh`, `tools/milestone_review.sh`); the reviewer agents post their own reviews.

## DOSBox-X 2024.03.01, for every run of the original

The project is calibrated to DOSBox-X **2024.03.01** (F001, `runtime/driver/savestate.py`): Ubuntu
24.04's apt package. Ubuntu 26.04's apt offers only 2026.01.02, whose savestates store `Vga` raw
and write a save in 3 events instead of 53-54, so no reader works on it (#117). On such a machine,
`bash setup/dosbox-x-2024.03.01.sh` unpacks Ubuntu 24.04's packages (checksums pinned in the
script; no sudo, nothing installed system-wide) into `~/tools/dosbox-x-2024.03.01`, with a
`bin/dosbox-x` wrapper that supplies the libFLAC 12 26.04 lacks. The system package stays for other
projects.
- `runtime/driver/driver.py`'s `dosbox_x()` picks the binary: `$DOSBOX_X`, else that bundle, else
  `dosbox-x` on PATH. The driver, the cycle fingerprint and the recorder (launch and version
  check) use it; `setup/goal2-runtime.sh` resolves it the same way and refuses another version.
- `experiments/E015-human-playthrough/scripted_keys.py` refuses another version before any display
  or emulator starts. `runtime/spike/` (F001's frozen spike) still runs `dosbox-x` from PATH: put
  `~/tools/dosbox-x-2024.03.01/bin` first on PATH for it.
- An OpenCode run of the original needs the same: pass `--env "PATH=$HOME/tools/dosbox-x-2024.03.01/bin:$PATH"`
  only for `runtime/spike/`; the driver and the recorder find the bundle themselves.
- The driver's keys (issue 244): `runtime/driver/xkeys.py` sends every key as a raw XTEST keycode
  with no modifier, and the driver's savestate and load are Scroll Lock and Print Screen through a
  mapper file it writes into the session folder, so the host key F12 is never pressed. On Ubuntu 26.04
  (xdotool 3.20160805.1 with Xvfb 21.1.22) xdotool sent Left Alt with every function key (F10 reached the
  game as Alt+F10) and left Left Alt held in the guest from the launch on; the 458 records made on
  Ubuntu 24.04 show none of that (34 published savestates checked), only a plain F12 pressed into the
  guest at each read. Two independent settings: `legacy_keys` is the transport (raw XTEST or xdotool),
  `mapper` is what the savestate and load keys are (`"nohost"` Scroll Lock / Print Screen, `"dosbox"` the F12
  chord, or a mapper file); the driver presses what the mapper in effect binds and refuses, when it is made, a
  mapper whose savestate, load and screenshot binds are not usable as a set (one key for two actions, an empty or
  unreadable bind, a modifier other than host, the host key F12 itself, differing duplicate lines, a key that
  is no X keysym: `ValueError`), and, before DOSBox-X starts, a key the raw transport cannot send. The old driver is `Driver(legacy_keys=True, mapper="dosbox")`. E031's `play.py` takes
  them as `--keys`, `--fkeys` (function keys and a chord's F12; default as `--keys`) and `--mapper`
  (`experiments/fix-244-driver-keys/README.md` has the table).
- **Read pace**: the savestate key is held `save_hold` seconds, default `SAVE_HOLD` = 0.52 s, so a read takes
  about 0.53 s as it did with the F12 chord (the chord held 3 steps of 0.15 s and made four xdotool calls;
  measured 0.512-0.764 s between chords in E003-r0047/r0049). Scripts whose `settle` waits for two equal
  reads stop earlier on a transient screen at 0.15 s and then do not reproduce their records (E003 d3b);
  at the default they do (`experiments/fix-244-driver-keys/README.md`). Pass `save_hold=` to change it.
- **Start states** (`.cache/states/driver/*.sav`, `main`, `title`, `e004-*`, `e006-*`) made with the old driver
  on a machine where xdotool adds Alt (Ubuntu 26.04) carry Left Alt held in their saved BIOS data
  (`0040:0017` bit 3 set; `python3 experiments/E031-play-the-game/lastkey.py <file.sav>` prints it), and a
  restore from one starts the guest with Alt held. Remake those: `python3 runtime/driver/driver.py make-state title`,
  `python3 experiments/E003-q001-inputs/run.py make-main --dos-time 10:00:00 --dos-date 10/04/2026`, and the
  experiment's own `make-state`. The published driver savestates (release assets named in `evidence/E005`,
  `E006`, `E010`, `E011`, `E013`, `E014`, `E018`) were made on Ubuntu 24.04 and show no Alt held
  (`experiments/fix-244-driver-keys/out/published-states.tsv`).
- **Do not press F1 in a driver run**: the help viewer makes every later savestate crash DOSBox-X
  2024.03.01 (buffer overflow detected, exit -6), even after Esc (E031, `docs/play-guide.md` section 2).

## Ghidra, for the decompiled and named views

`tools/static/decompile.sh` (T18; with `--annotations`, T20's named view) needs these, outside the
repository; nothing else does:
- Ghidra 12.1.4 (release `Ghidra_12.1.4_build`, unpacked to `~/tools/ghidra_12.1.4_PUBLIC`, or set
  `GHIDRA_HOME`). The script refuses another version.
- A JDK 21: Temurin 21.0.12.1 (`~/tools/jdk-21.0.12.1+1`, or set `JAVA_HOME`). The script refuses
  another major version, and the output's README records the exact one.
- [designed: owner, 2026-10-20] `bash setup/ghidra-12.1.4.sh` installs both on demand (official
  GitHub releases, sha256 pinned, about 780 MB, under a minute on a fast link) into `~/tools`, or
  `$TOOLS`; a cloud session runs it when a task regenerates `decompiled/` or `named/`.

Ghidra refuses a project path with an element that starts with `.` ("Path element starting with '.'
is not permitted"), and the harness's isolated worktrees are under `<repo>/.claude/worktrees/`. So
Ghidra's project, input and temporary files never go under the repository or `TMPDIR`: the wrapper and
`GhidraMappingTests` make `$HOME/goal2-ghidra-work/<unit>-<random>` (`tools/static/ghidra_work.py`;
`GOAL2_GHIDRA_WORK` names another absolute base), set `TMPDIR`, `TMP` and `TEMP` to it for Ghidra, and
remove it afterwards (`KEEP_WORK=1` keeps it). A base whose resolved path has a dot element (a `HOME`
under `.something`, a link into one) stops the run with that reason (fix #315). No manual `TMPDIR` is
needed in an agent worktree.

Ghidra runs headless with `-max-cpu 2`, one instance at a time (the machine is shared). Without
them, `tests/static/test_decompile.py` skips its Ghidra tests and says why. One run takes about
six minutes on two CPUs: start it in the background.

## A shared machine

Isle-wars' sessions run DOSBox-X and Xvfb on the same machine. Use another display than `:99` (a
stray `Xvfb :99` belongs to neither project), and stop only processes you started, by PID: never
`pkill dosbox-x` or `pkill Xvfb`.

## Heavy jobs

Up to four agents and three reviews ran at once on 2026-10-17: load average 6.8 to 7, reviews of 62-match
runs took one to two hours, one hit its limits, and the idle watch fired "possibly stuck" for work that was only
slow. "At most one match process at a time" was only a line in briefs; since #318 a lock enforces it.

`tools/heavy.sh <name> -- <command>` takes one of N slots (four, set in the script, since the owner's decision of 2026-10-18, two before; the four is a policy, not yet measured for throughput or memory with four matches at once; why a 1 s poll and a 5 s stale-ticket age: measurements and sources in `notes/318-heavy/README.md`; the
environment variable `HARNESS_HEAVY_SLOTS` overrides it. N is read once, when `heavy.sh` starts: a job already queued keeps the N it started with, so a change of the value reaches new invocations only and a new job queues behind older ones that still use the old N), then runs the command in place of itself (its exit status
and output are the command's). With every slot taken it queues, first come first served, and prints
`heavy: <name>: waiting for a slot (k ahead)` on stderr, k being the jobs queued before it. The slots and the queue
are files in `~/.cache/goal2-heavy` (`HARNESS_HEAVY_DIR`), locked with `flock`, so they are shared by every
worktree and every process of the machine, and a job that dies, even killed with SIGKILL, frees its slot at once.
`heavy.sh --status` lists the slots and the queue; `--weight K` holds K slots (a job that runs K processes).
A `heavy.sh` started inside a heavy job (`HARNESS_HEAVY_HELD` is set) runs its command at once and takes no
second slot, so `check.py` called by the unit suite cannot deadlock a full machine.

Who uses it: `experiments/E036-match-port/family.py` (weight = the match processes it runs at once: `--workers`, but at most the matches still to run, and 1 for `--find-ranges`, which runs its matches one after another), `runtime/original_match/check.py` and
`tools/ci_gate.py run-tests` queue themselves when run as scripts (`runtime/heavy_slot.py`; each reads its slot weight and whether to queue at all with the same argparse parser its `main()` uses, `heavy_slot.parsed`, so a repeated `--workers`, `--workers=2` or an abbreviation weighs what the run uses, and a command line `main()` refuses holds no slot and is answered at once, whether argparse or the entry point's one validation refuses it (`ci_gate.refusal`, `family.prepare`, `check.validate`: `main()` and the slot step both call it, #328). That includes every path option: `--image`, `--mask`, `--json`, `--find-ranges`, `--out` and `--cache` are checked by `runtime/original_match/fileopts.py`, the same helper the run opens them with (an input is a regular file that opens for reading; a new output has nothing at its path, even a broken link, and an existing, writable folder; `--out` is a readable, writable file or has a writable folder above it; the `--cache` reference is readable or its folder can be made), so a missing, unreadable or unwritable path is refused before the queue. What only the run can know is not checked and can still fail after the queue: the reference image's SHA-256, its download (`gh`, the network), a match that does not complete, and a file system that changes between the check and the run; `check.py` is one process in every mode; the unit suite is one job, and a test of it that starts its own processes (the two-workers test, the human recorder's display stack) is not counted again; not in CI, where the
runner is not this machine, nor when `HARNESS_HEAVY_OFF` is set). The unit suite run by hand is
`tools/heavy.sh unit-suite -- python3 -m unittest discover -s tests`.
A review holds no slot of its own; a reviewer's heavy commands queue like any other. `tests/test_heavy_slot.py` tests it.

## Raw sittings and other git-ignored data (what is not in the repository, and where it lives)

The owner's recorder sittings (`scratch/human/sessions/<date-time>/`: savestates, `keys.jsonl`, `notes.jsonl`,
`meta.json`, the game copy with its saves, the video) are git-ignored by design (CLAUDE.md rule 18: a savestate is
the game's memory; the key log is the owner's typing; a sitting is about 100-400 MB). What the repository holds
instead: the run records `runs/E015/E015-r0007..r0017` (screens, game state, diffs, the owner's notes), and for
r0001-r0012 the savestates on release `E015` (manifests under `evidence/E015/`).

- **Nothing in the tests, the tools or CI needs a sitting.** A new computer needs a clone and
  `bash setup/goal2-runtime.sh` (it fetches the original game and the saved games from the private releases by hash).
- **Two jobs do need a raw sitting:** T39c's check (`python3 experiments/E022-video-screens/check.py <session folder>`,
  the sitting `20261011-161003`) and re-extracting a run record with `experiments/E015-human-playthrough/extract.py
  <session folder>` (other countries, a fixed extractor).
- **Where the raw sittings are (2026-10-16): an interim backup, one zip per sitting** in
  `~/projects/goal2-archaeology-keep/sessions/` (with `SHA256SUMS` and a README that maps each sitting to its
  record), outside the repository, on the owner's main computer. To use one on another computer, copy the folder
  (or one zip), check it with `sha256sum -c SHA256SUMS`, and `unzip` it into `scratch/human/sessions/`
  (each zip holds the session folder at its top level). **A session that needs a raw sitting and cannot find it
  in `scratch/human/sessions/` says so to the owner and asks for that backup folder; it does not guess.**
- The proper home is a release, one zip per run (issue 224, not done): then a clone and `gh` access are enough.
- Also git-ignored and not backed up: the black videos of old sittings (nothing to decode), small test sessions
  made by agents, `.cache/` (re-created by `setup/goal2-runtime.sh`).
- Released and verified: the owner's saved games (`goal2-saves`, `artifacts/saves.json`), the play-the-game
  milestone saves (`play-the-game-saves`) and its kept savestate (`play-the-game-states`,
  `experiments/E031-play-the-game/out/states.tsv`).

## Third-party tools kept outside the repository (Turbo Pascal compilers, 7-Zip)

Needed only to redo E035 (`experiments/E035-tp-version/`, which compilers built `GOAL.EXE`: Turbo Pascal 5.5) or to
check a decompiled routine by compiling a Pascal transcription of it with the same compiler. Nothing else needs them.

- **The compilers** are the owner's downloads from WinWorldPC (old DOS floppy images; the owner treats them as
  abandonware, as the game, rule 18). They are third-party software: **never committed, run only inside DOSBox-X**.
  They live in `~/projects/goal2-archaeology-keep/tools/turbo-pascal/` on the owner's main computer: `archives/`
  (the 7z files, including the 5.0 manuals), `extracted/` (the floppy images of Turbo Pascal 4.0, 5.0, 5.5, 6.0, 7.0
  and 7.01), a README, and `SHA256SUMS` (hashes the archives only). Copy the folder to another computer and check it
  with `cd tools/turbo-pascal && sha256sum -c SHA256SUMS` (7 lines, all OK); if the
  folder is missing, a session says so to the owner and asks for it; it does not download them itself (the
  WinWorldPC pages need a browser).
- **7-Zip:** the Python reader `py7zr` cannot read Turbo Pascal 7.0's archive (BCJ2 filter). The official 7-Zip
  Linux binary does: `7zz` 23.01 from `https://www.7-zip.org/a/7z2301-linux-x64.tar.xz` (sha256
  `23babcab045b78016e443f862363e4ab63c77d75bc715c0b3463f6134cbcf318`), unpacked to `~/.local/bin/7zz`, no sudo.
- **Reko** (0.12.5, a decompiler tried on a few routines and not adopted, `experiments/E035-tp-version/README.md`)
  is not a requirement; the excerpts it produced are committed.
