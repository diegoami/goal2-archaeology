# E015 human-playthrough

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T29 (#93)
- **Question**: Can one human playthrough yield every fact the project needs, as a complete
  behavioural record any later question is mined from without new play? (the owner's direction,
  2026-10-07; G5 rows Q013–Q017, #40, #65, F015's shoot-out arm, the bot's World Cup path)
- **Hypotheses**:
  - a timestamped chain of whole-machine savestates (one every ~20 s, host key sent directly to
    the game window) plus the screens they carry is such a record: every savestate holds the
    screen, the game state `[A923]`, the player and country arrays, and the commentary ring, so
    any later question reads the chain instead of replaying the sitting;
  - consecutive-state diffs (records, stage, squad) surface exactly the moments the open
    questions need (year-ends, transfers, watched matches) without new play.
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/human/recorder.py@<commit in each record>` — windowed DOSBox-X
  2024.03.01 on the player's display, the G1 driver's config family (`nosound=true`); maximum
  intervention level I2 (the watcher's F12+S savestate writes; the player's own keys are the
  experiment's subject, not an intervention of the project)
- **Design**:
  - the recorder `runtime/human/play.sh`: one command; the watcher stages a timestamped
    savestate every 20 s (the focus gate: keys only with `xdotool key --window <wid>`, never a
    global keystroke; the staging gate: copy only a complete, size-stable zip, never touch the
    live file), indexes them with sha256, optional screen video of the game window (mkv);
  - the sitting follows `protocol.md` (unscripted; partial chains are valid records);
  - the extraction `extract.py` walks one session's chain and emits one immutable `run/1`
    record per session in `runs/E015/`: per state the screen text, the game state
    (`[A923]`, 0x10E bytes per `2139:0000`), the chosen countries' country and player records;
    per consecutive pair a structured diff (records, stage, squad); every file read named with
    sha256.
- **Measurements**: per state: screen digest and CP437 text, `[A923]` bytes with named raw
  fields (managers, fixture index/count, year, stage, delay), `players.check`'s verdict, the
  country record and the 20 player records of each chosen country; per consecutive pair: changed
  bytes of `[A923]`, squad changes, changed bytes per player record.
- **Analysis**: none in this experiment: each open question is mined by its own task
  (`protocol.md`'s map says what in the chain answers it).
- **Outputs**:
  - run records: `runs/E015/` (one per session);
  - evidence bundles: the session's staged savestates, release `E015`.

## Scripts

```
bash setup/goal2-runtime.sh
bash runtime/human/play.sh --self-test
bash runtime/human/play.sh [--video]
python3 experiments/E015-human-playthrough/extract.py scratch/human/sessions/<date-time> --countries 1
python3 tools/validate_runs.py runs/E015
python3 tools/publish_evidence.py E015 --run E015-r0001 --file <snapshot> ...
python3 tools/verify_evidence.py E015
```

## Records

All three records are extractions of the same scripted sitting, `20261007-174403`, whose four
savestates are published on release `E015`. Records are never rewritten (L207), so a defective
record stays where it is and a later record supersedes it:

| Record | Extraction pass | Superseded by, and why |
| --- | --- | --- |
| `E015-r0001` | round 1 (before review) | `E015-r0003`: it reads interrupt-vector bytes as the game state when `[A923]` is 0000:0000, and puts country records one record off (review round 1, R8 and R9) |
| `E015-r0002` | round 2 | `E015-r0003`: its `run_id` reads `E015-r0001` because it was extracted into a scratch directory and copied in (review round 2, R5) |
| `E015-r0003` | round 3 (`claim_record`: the id is the slot claimed) | — |

## T34 recorder extension and scripted acceptance

T34 (#105) extends the T29 recorder without changing the sitting's research
question. The current invocation and design are in [protocol.md](protocol.md):
DOSBox-X and an XInput2 raw-key logger share a private nested Xephyr display;
other desktop applications are structurally outside it. The watcher saves every
20 s and 0.05 s (`EVENT_SETTLE_S`) after each settled key episode, through the
same single-writer capture gate.
Its save keys now use explicit window-targeted XSendEvent rather than xdotool's
raw input path, preventing recursive burst captures. Optional video covers the
Xephyr window. This paragraph supersedes the original Runtime/Design wording
above; the original experiment description is retained append-only.

The map is a JSON observation in run/1, never a top-level property. Screen
identity is SHA256 of decoded UTF-8 text, ignoring attributes; ordered bursts
associate the nearest earlier snapshot with the first snapshot after quiet.
Neither boot progress nor a multi-key burst proves individual-key causality.
A snapshot's screen is bracketed by its save-request window
(`request_s`..`sent_s` plus the 50 ms delivery margin measured in
[T34-probe-20261009-05.log](T34-probe-20261009-05.log)), never by its staging
time; a key inside that window is ambiguous and its burst unmapped.

The key logger attaches to the nested display only and is started **before**
DOSBox-X is launched (T34 review R6): the startup window between the logger and
the emulator cannot swallow a key, because there is no such window — the only
gap is before the logger itself, when nothing of the game exists yet.

| Record | Scripted sitting | Map |
| --- | --- | --- |
| `E015-r0004` | `20261009-004935`, re-extracted with the schema-valid observation | [table](E015-r0004-keymap.md) |
| `E015-r0005` | `20261009-010044`, fresh acceptance sitting | [table](E015-r0005-keymap.md) |
| `E015-r0006` | `20261009-100804`, human-paced gaps (0.5–1.5 s) and the focused-XTEST privacy proof | [table](E015-r0006-keymap.md) |

The first two sittings logged only game `a/b` press/release events, not `x/y/z` sent to an
xev application window on the outer display, and staged two burst snapshots each.
`E015-r0006`'s sitting (`scripted_keys.py --keys a;b;c` with gaps drawn from 0.5–1.5 s)
adds the real-key half of the privacy proof: while the xev window held the outer focus,
`y`/`z` were typed on the outer display as real XTEST keys — an outer raw reader saw them
and xev received them, so a logger on the outer display would have leaked them, yet
`keys.jsonl` holds only the game's `a`/`b`/`c`. Their savestates are published on release
E015, indexed by the corresponding manifests in `evidence/E015/`.

The earlier schema-invalid records were removed by the main session in c5000af
before this extraction. Their original derived tables are retained unchanged as
`T34-original-r0004-keymap.md`, `T34-original-r0005-keymap.md` and
`T34-original-r0006-keymap.md`; those names do not refer to the new valid records.
The first scripted failure and the successful earlier sitting remain in
`T34-scripted-20261009-01.log` and `-02.log`; the fresh sitting is `-03.log`.

### Method and regression proofs

Static first: `static/goal-exe/named/seg_0791_11.c` already names the SELECT TEAM
handler and its Insert assistant path. No new game handler claim or annotation
is established here: static analysis cannot prove host display isolation,
logger delivery or snapshot scheduling. The scripted runs test those tooling
properties, not the unvisited `C/N/Insert` controls. Coverage is limited to the
rows explicitly added in the protocol.

`T34-tests-20261009-04.log` records 62 passing combined recorder/map tests.
`mutate_keys.py` makes one mutation at a time **in place**, tests, then restores
the source in a `finally` block. The `-03` mutation log retains the first sweep,
including its survivors. The new boundary/order/count fixture fails with those
surviving rules removed and passes with them restored, as `-04` shows: all 20
selected mutations fail. These include display restriction and burst removal,
both quiet constants at +1 and -1, text identity, headline, invalid-snapshot
filtering, sample/event ordering, grouping, release filtering, before/after
choice and boundaries, missing-bracket counts, repeated-transition counts and
press counts. No mutated source is committed.

The `-05` sweep re-runs the whole current mutation list against the reworked
sources: the R1 request-window rules, the R2 gap and skipped-request rules, the
R3 privacy mutations (the focused-XTEST one is killed only by the real-key
`y`/`z` path, the XSendEvent keys alone generate no raw events to leak), the R4
window-bind rules, the constants, the R8 save-event rule and the R9 host-path
rule. `T34-mutations-20261009-05.log` is its record. The delivery latency the
50 ms margin bounds was measured by the probe kept as
[T34-probe-20261009-05.log](T34-probe-20261009-05.log) (a probe log, not a
finding).

The `-07` sweep (Sol delta rework) fixes the two scheduler/guard defects the
delta found at human pace and extends the sweep to 52 mutations, all killed
(`T34-mutations-20261009-07.log`, survivors `[]`). The recorder's burst
scheduler is now a queue of key groups — each group separated by at least
`BURST_QUIET_S` gets its own burst snapshot, one per loop pass, instead of the
four snapshots ten groups produced when one `Burst.last` was overwritten during
a capture. The acceptance guard (`scripted_keys.check_bursts`) now requires
exactly one distinct, correctly timed burst snapshot per key group, not "any
later snapshot", and the privacy proof's positive control is explicit: the
foreign application's own `xev` log is parsed (`recorder.xev_presses`) and its
`x`/`y`/`z` asserted, written as `foreign-keys.jsonl` beside the session. The
three new mutations remove the focused-XTEST foreign sends (R1), merge every
key back into one group (R2), and let the guard accept fewer snapshots (R3).
The end-to-end scripted sitting (10 keys at 0.51 s → 10 burst snapshots) is the
manual acceptance; the same sitting runs once in the full suite as a regression
test, skipped per-mutation by the sweep (`MUTATION_SWEEP=1`).

## Sol delta r2 addendum (2026-10-09)

The `-07` scheduler still sent each group's save request at its due time (last
key + `BURST_QUIET_S`, 0.5 s) and staged it on the loop: at the delta review's
reproduction (keys slept 0.51 s apart, 0.525-0.529 s on the wire) only 4 of 10
presses mapped. Two facts make a due-time window impossible there: it is
~0.08 s wide (send ~26 ms + 50 ms margin) and must fit between keys spaced
0.527 s apart with 0.5 s of that already consumed by the quiet — it needs
spacing >= ~0.58 s. The fix (commit `82c501d`): the request for each settled
key episode goes out `EVENT_SETTLE_S` (0.05 s, ~4x the measured 12 ms
press-release lag) after the episode's newest event, and staging runs on a
capture pipeline off the loop, whose fast path takes the kernel's write-event
count (inotify close past the pre-send count) as the write-completed evidence —
the 0.75 s stability polls cannot fit between savestate writes 0.53 s apart;
every other gate check is unchanged. `BURST_QUIET_S` (0.5 s) stays the grouping
quiet the map reads. The acceptance guard now also verifies request-window
timing per group (`check_request_windows`: never clustered after every group)
and mapped coverage (`check_mapped`: every press mapped, else exit 1). The
reproduction now reports `screens: 2, transitions: 10, keys: 10; every press
mapped` (`T34-scripted-20261009-05.log`); three new mutations cover the r2 code
(`T34-mutations-20261009-08.log`, survivors `[]`).

## T39b addendum: pause, notes and live view (2026-10-11)

T39b (#138) adds the coaching kit to the recorder without changing the research question:
DOSBox-X's own pause on F12+P (resumed with the Pause key), `pauses.jsonl`, coaching notes
(`runtime/human/note.py`, `notes.jsonl`) and a read-only live view (`runtime/human/live.py`).
The design is in [docs/recorder-architecture.md](../../docs/recorder-architecture.md) and the
sitting's side in [protocol.md](protocol.md). The record (`extract.py`) carries each note and
each pause and resume between the two states whose screens it falls between, and the key log's
press count beside the map's.

Method. No game fact is established, so there is no annotation row and no static question:
the pause is DOSBox-X's, not GOAL.EXE's. What DOSBox-X 2024.03.01 does around it was measured on
a private Xvfb at the DOS prompt by `probe_pause.py`
([T39b-probe-pause-20261011-01.log](T39b-probe-pause-20261011-01.log)): F12+P pauses and the
title says `PAUSED`; a save request while paused is dropped, not deferred; keys typed while
paused never reach DOS; only the Pause key resumes; F12+P on `hand_pauseints` instead changes no
title and pauses nothing visible at the prompt; a mapper file holding the pause bind alone leaves
F12+S unbound (a mapper file replaces the default binds).

Tests and proofs: `tests/test_human_pause.py` and `tests/test_human_coach.py`;
`mutate_pause.py` makes each mutation in place and restores the source in `finally`
([T39b-mutations-20261011-02.log](T39b-mutations-20261011-02.log): 26 mutations, survivors
`[]`); `mutate_pause.py --before` runs the new tests on origin/main's sources, every one failing
([T39b-failbefore-20261011-02.log](T39b-failbefore-20261011-02.log)). `scripted_pause.py`
rehearses the owner's test sitting on private displays (two pauses, the second in the middle of
a key burst, a key typed while paused, two notes, two live views):
[-01](T39b-scripted-pause-20261011-01.log) failed its own check on xdotool's added `Alt_L`
before F12 (a modifier no keyboard sends), [-02](T39b-scripted-pause-20261011-02.log) passed and
showed a burst request sent after the P press being dropped as DOSBox-X paused — the shape the
post-resume guard now refuses — and [-03](T39b-scripted-pause-20261011-03.log) passed with the
guard. Rehearsals are extracted into scratch only; they are not E015 records.

### The owner's test sitting and the amendment (2026-10-11)

| Record | Sitting | Map |
| --- | --- | --- |
| `E015-r0009` | `20261011-215411`, the owner's T39b test sitting: Italy (`--countries 16`), from the owner's saved game, three pauses, four notes | [table](E015-r0009-keymap.md) |

`extract_215411.py` made it, declaring what the session folder does not record: the main
session's copy of the owner's `1.GL` into the game copy before launch (I3) and the Pause keys it
pressed for the owner, who has no Pause key (I2). Its 42 snapshots are on release E015
(`evidence/E015/E015-r0009.manifest.json`). It shows the first two pauses with their resumes
and the snapshots on both sides, the four notes in place, and 310 presses in the record as in
`keys.jsonl`. The third pause has no resume: `keys.jsonl` ends at +237.9 s and the main session's
Pause at about 19:58:40Z is in neither file, so the recorder no longer read keys or the title by
then; the sitting's terminal output, which would say why, was not kept. live.py ran once on it
([T39b-live-20261011-01.log](T39b-live-20261011-01.log)).

The task was amended after that sitting (Scope 5-8). Findings behind the changes:
[T39b-repro-215411-20261011-01.log](T39b-repro-215411-20261011-01.log) replays the third pause's
keys and the window closing on private displays: the third resume is logged there, and closing
the window ends the key logger first, which the loop raised past `play()`'s meta write — the
missing `ended` and `stop_reason`. [T39b-probe-resume-20261011-01.log](T39b-probe-resume-20261011-01.log):
an XTEST Pause with the window focused and an XSendEvent Pause end the pause in a plain Xvfb;
focus changes, clicks, F12+P, an unfocused XTEST Pause and a save request do not (the sitting's
second resume, at +145.8 s with no key in `keys.jsonl`, fits an XSendEvent Pause). The recorder
now resumes on F12+P with its own marked XTEST Pause, ends cleanly on a closed window, writes
`ended` on any error, never crashes on an unanswered title read, and copies the saved game
(`--load`, `--fresh`). Tests: `tests/test_human_resume.py`;
[T39b-mutations-20261011-04.log](T39b-mutations-20261011-04.log) (52 mutations, survivors `[]`),
[T39b-failbefore-20261011-04.log](T39b-failbefore-20261011-04.log) (every new test fails on
origin/main's sources; `-03` found one that did not, fixed in `-04`). Rehearsal
[-04](T39b-scripted-pause-20261011-04.log): two F12+P resumes, `--load`, and the window closed
(`stop_reason: window-closed`).

### The owner's second sittings (2026-10-11)

| Record | Sitting | Map |
| --- | --- | --- |
| `E015-r0010` | `20261011-224811`: `--load 1.GL` (sha256 `4a0f9bc0…`), Italy into the Belgium qualifier; 39 snapshots, 170 owner presses and 6 Pause presses by the recorder; 5 pauses, 4 resumed by F12+P (the last pause ended when the window closed), `stop_reason: window-closed` | [table](E015-r0010-keymap.md) |
| `E015-r0011` | `20261011-225621`: the newest `.GL` copied by default; 19 snapshots, 38 owner presses and 2 by the recorder; 2 pauses, each resumed by F12+P, a note and a live view in each (`T39b-live-20261011-03.log`), `stop_reason: window-closed` | [table](E015-r0011-keymap.md) |

`extract_224811_225621.py` made both. The saved-game copy (I3) and the recorder's Pause keys (I2)
come from the sessions themselves; the main session's notes and live views are declared (I0).
E015-r0010's one note and second live view came after the window closed (20:52:35Z), so the note
lies after the last state.

The owner's question A3 (does the match start with the stored eleven or the original one?):
**the stored one.** In E015-r0010 Italy's squad words never change. The first eleven stays the
stored order from the loaded save: Vierchowod (314), Stroppa (315) and Baggio (318) are in it,
and Maldini (303) and Di Chiara (305) are among the substitutes. The Belgium qualifier's
pre-match screen (state 12) and its match (state 16, "Baggio intercepts") use that eleven: the
game did not restore the original one when the match started.
