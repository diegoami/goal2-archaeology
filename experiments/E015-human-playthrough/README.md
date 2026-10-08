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
