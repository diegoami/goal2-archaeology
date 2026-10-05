# E007 q009-player-screen

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T16 (#48)
- **Question**: Which skills does the player screen show, on what scale, and from which record fields? (G5 Q009)
- **Hypotheses**:
  - H0 (backlog Q009): the screen shows 12 named skills (`GOAL.HLP` 39, 92) on one numeric or word scale, and `kicking` and `goal kicking` are one skill or two — distinguished by the labels and the scale on the screens of at least 40 players, and by the routine that prints them
  - H1: each shown value is a byte or word of the 20-byte record at `[DS:A91B]` (F007), or a formula over its fields (and the player number), or comes from somewhere else — distinguished by transcribing every shown value of each screen and matching it with the record read from the same savestate
  - static: the routine that prints the names at `DS:4979..4E78` (the template at `DS:486E`) and what each printed value is computed from
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on Ubuntu 24.04 in WSL2, `cycles=30000` (E004's and E006's value; no match is played); maximum intervention level I2 (a savestate written at every screen and one loaded at the start; the DOS clock of the session is not set, the restore brings the state's own)
- **Design**:
  - one start state: E006's main-screen savestate of the new game made at DOS time 10:00 (E006-r0001, release E006, checked against its evidence manifest by sha256). Player values are the same in every new game (F007), so one state serves every comparison;
  - one record per country: a fresh launch, the state restored (Host+L), Down as many times as the country's position in the main screen's country list (Denmark, the managed country, 0; Germany 1; Holland 2), Space (the country's player list: its first player's screen), then Down once per player, with a savestate (Host+S) at every screen; 20 players (a squad) per country;
  - three countries, 60 players, a goalkeeper among the first two of each squad (the screens say so);
  - stopping rule: those 3 records written, then one more list position (3, 4, 5 in turn) for as long as a position code of the 14 (0..13) has not appeared in the 60 players; an aborted record is kept and its position repeated once.
- **Measurements**: at every player screen: the host clock, the text page (characters and attributes, 4000 bytes), the BIOS mode byte and tick count, the player the screen names (found by the name `1771:2E93` builds from `[DS:9B70]` and `[DS:9B6C]`, narrowed by the shown age) and that player's 20 bytes at `[DS:A91B]`; once per record: the data-segment tables the screen's routines index (`DS:0E40..0E8F`, `0F20..0F7F`, `6990..6ABF`, `6D20..6E8F`, `6EB4..793F`). Per record: launch time, config and its sha256, the keys sent, every wait (log).
- **Analysis** (`summarise.py`): per shown value, its name, its scale (numbers or words, the range seen) and its source: a record field, a formula over fields with its match count over all transcribed players, or "not found". The formulas are the listing's (`1771:42BC` and its callees), evaluated on the record bytes and the tables of the same record.
- **Outputs**:
  - run records: `runs/E007/`;
  - `findings/F008-*.md`, status `proposed`.

## Scripts

```
bash setup/goal2-runtime.sh
python3 experiments/E007-q009-player-screen/run.py adopt --from E006-r0001
python3 experiments/E007-q009-player-screen/run.py countries --state e006-1000-r0001 --list-positions 0,1,2 --batch b1
python3 experiments/E007-q009-player-screen/summarise.py
```
