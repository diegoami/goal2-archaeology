# E006 q004-skills

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T15 (#43)
- **Question**: Where and how are player skills and attributes made, and does a new game's seed change them? (G5 Q004)
- **Hypotheses**:
  - H0 (backlog Q004): the fields are drawn at a new game from the seed the DOS hour:minute gives (F004), so two new games at different DOS minutes give the same names but different values, equal within one minute; the draw is scaled by a per-country value (R007 or R008) — distinguished by comparing the player array field by field across minutes and within a minute, and per-country means against R007 and R008
  - H1: a field is equal across minutes: it is not drawn from the time seed (fixed data, or a draw from a fixed seed) — distinguished by the same comparison, and on the static route by what `1771:96D3` and its callers write and with which seed
  - static: `1771:96D3`'s writes into each field of the 20-byte record at `[A91B]`, their inputs (draws of `214B:06B1` and their ranges, the position byte, the country record), and when it runs (start-up, new game, or both)
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on Ubuntu 24.04 in WSL2, `cycles=30000` (E004's value; no match is played); maximum intervention level I3 (the DOS date and time set in the autoexec before GOAL runs, verified by DOS's read-back, F004)
- **Design**:
  - one new game per record (`run.py games --times …`): a fresh launch at the DOS time given on 10/04/2026 (I3), F001's keys to the main screen (`n Enter Enter b o b Enter Enter Enter Enter`, each followed by a settle poll), Host+S;
  - DOS minutes: 10 distinct (00:00, 06:30, 10:00, 10:01, 10:02, 12:00, 13:37, 17:45, 21:00, 23:58) and 10:00 twice more (3 games at one minute);
  - the main-screen savestate is kept as `.cache/states/driver/e006-HHMM-r<nnnn>.sav` with its `.json` (the drive layout, as E004's start states), named in the record's `outputs`, and published to release `E006` with `tools/publish_evidence.py E006`;
  - stopping rule: those 12 records written; an aborted run is kept and its minute repeated once.
- **Measurements**: at the title and at the main screen: the screen, BIOS mode byte and tick count, `DS:7B62`, `DS:7B64`, `DS:8336`, `DS:A9FD` (I1); at the main screen: the far pointers `DS:A91B` and `DS:A917`, the 0xEF24 bytes of the player array and the 0x603F bytes of the country array as hex, and `players.check` (the arrays' lengths, the squad words of countries 1..128, byte 0 of their players: the array located on known values before any field is used). Per record: launch time, config and its sha256, the DOS clock read back, every wait (log).
- **Analysis** (`summarise.py`): per field of the 20-byte record (bytes +0x00..+0x13; +0x12 as a word too): whether it differs across DOS minutes and whether it is equal within the repeated minute (players 1..2560 compared by number; players 2561..3060 too); its range over all 3061 players; for a field that varies between players, the Pearson correlation and least-squares line of its per-country mean (players of squads 1..128, n = 128) against each of R007's three bytes (`DS:9D80 + 3c`, from `GOAL.DAT` block 6) and R008 (`DS:9B7C + c`, block 7), and against the country rank the static route names (`1771:10E7`).
- **Outputs**:
  - run records: `runs/E006/`;
  - evidence manifests: `evidence/E006/` (the main-screen savestates, release `E006`);
  - `findings/F007-*.md`, status `proposed`.

## Scripts

```
bash setup/goal2-runtime.sh
python3 experiments/E006-q004-skills/run.py games --times 10:00,10:01,10:02,13:37,21:00,23:58,00:00,06:30,12:00,17:45,10:00,10:00 --batch b1
python3 experiments/E006-q004-skills/summarise.py
```

## Amendment 1 (2026-10-05, after E006-r0012; review round 1 of PR #45, R1)

- **The recorded invocation.** E006-r0001 … r0012 record `actions.args` as `games --dos-time HH:MM:SS --dos-date 10/04/2026 --batch b1`, an invocation `run.py` cannot accept: its parser has `--times`, and no `--dos-time`. The records are kept as written (L207). Here is what each one actually ran, at `code_commit` `c1edac2`:
  - E006-r0001: `games --times 10:00 --batch b1`.
  - E006-r0002 … r0012: one process, `games --times 10:01,10:02,13:37,21:00,23:58,00:00,06:30,12:00,17:45,10:00,10:00 --batch b1`. The k-th record is the k-th entry, so its recorded `--dos-time` is that entry plus `:00`.
- **What it does not affect.** The DOS time and date each game ran with are as recorded: the I3 intervention text and DOS's read-back in every record show them. Each record's `actions.sha256` is the hash of `run.py` as loaded (`6de8e102…`) and is correct. The measured arrays, screens, seed words and savestates are unaffected.
- **From the commit after this amendment**, `actions.args` is the argv the process ran (`record_args`, `sys.argv[1:]`). `tests/test_driver_e006.py` (`RecordedInvocation`) parses a record's `actions.args` with the script's own `parser()`.
