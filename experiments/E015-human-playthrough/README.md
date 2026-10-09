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
20 s and after 0.5 s of quiet, through the same single-writer capture gate.
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
