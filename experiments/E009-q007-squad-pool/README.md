# E009 q007-squad-pool

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T22 (#67)
- **Question**: Which records does the pool (selection) screen list for a managed country, in what
  order, and how many? (G5 Q007)
- **Hypotheses**:
  - the pool is the squad's 20 (records `(c-1)*20+1 .. c*20`, R012) plus the 80 records `1771:98C4`
    makes (`make_managed_pool`), numbered 2561..2640 for the first managed country and held in
    `DS:A927[base .. base+79]` — distinguished by reading `DS:A927` and the pool records from a
    savestate, and by matching the pool screen's names to `GOAL.DAT` records;
  - each manager gets its own 80 at a consecutive block: manager `m` at records
    `2561+80(m-1) .. 2640+80(m-1)`, from the base table `DS:6D18 + 2m` — distinguished by reading
    the base table.
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on
  Ubuntu 24.04 in WSL2, `cycles=30000` (E006's and E007's value; no match is played); maximum
  intervention level I2 (a savestate written at every read and one loaded at the start; the DOS
  clock of the session is not set, the restore brings the state's own)
- **Design**:
  - one start state: E006's main-screen savestate of the new game made at DOS time 10:00 (E006-r0001,
    release E006, checked against its evidence manifest by sha256). Player values are the same in
    every new game (F007), so one state serves every comparison;
  - one record: a fresh launch, the state restored (Host+L), then Esc (the main menu `000E:7439`,
    where "select squad" is an item), Space (the SELECT TEAM screen `0791:E44F` in its squad view),
    Left (toggle to the pool view, `0791:E2E6`). Each screen is read; from the restored state's
    savestate the pool index array `DS:A927`, the base table `DS:6D18`, the name arrays `[DS:9B6C]`
    and `[DS:9B70]`, the 80 pool records (2561..2640) and the two records just past them (2641, 2642)
    are read.
- **Measurements**: at the restored state: `DS:A927` (word[481]), `DS:6D18..6D27`, the name arrays,
  and the 20-byte records 2561..2642; at each screen: the host clock, the text page (characters and
  attributes). Per record: launch time, config and its sha256, the keys sent, every wait (log).
- **Analysis** (`summarise.py`): per record, checks that `DS:A927[0]` is 0, `DS:A927[1..80]` is
  exactly the set 2561..2640, `DS:A927[81..480]` is all 0, `DS:6D18` words 1..6 are
  1, 81, 161, 241, 321, 401, the pool records hold country 7 (Denmark) in byte 0, the two records
  past the pool are all zero, the pool view lists the names of `DS:A927[1..20]`, and the squad view
  lists Denmark's 20 squad records (121..140). The names are `1771:2E93`'s (`players.full_name`).
- **Outputs**:
  - run records: `runs/E009/`;
  - `findings/F011-*.md`, status `proposed`.

## Scripts

```
bash setup/goal2-runtime.sh
python3 experiments/E009-q007-squad-pool/run.py adopt --from E006-r0001
python3 experiments/E009-q007-squad-pool/run.py pool --state e006-1000-r0001 --batch b1
python3 experiments/E009-q007-squad-pool/summarise.py
python3 tools/verify_evidence.py E006
```
