# E003 q001-inputs

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T08 (#21)
- **Question**: What inputs beyond the start state and the keys does GOAL2 use, and how can each be fixed or recorded? (G5 Q001)
- **Hypotheses**:
  - H0: the DOS time read at launch (hour and minute) seeds the game: fresh launches with the same keys reach the same main screen when the DOS time agrees to the minute and different ones when it differs; `DS:7B62`, the word the leads name as the seed, follows the DOS time — distinguished by the main-screen digests and the `DS:7B62` and `DS:7B64` words of the `d0` records, fixed and over five minutes
  - H1: something other than the DOS time differs between launches (main screens differ at one fixed DOS time) — distinguished by the same fields
  - H2 (D3): a quick result from one savestate differs between batches only when a named input differs; the seed words before `r` tell whether the restored state or what happens after it differs — distinguished by the result screen digests and the three seed words before and after `r` of the `d3` records, DOS time fixed and free, in batches at least 20 minutes apart
- **Artifact**: set `goal2-a949da2f`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on Ubuntu 24.04 in WSL2, `cycles=auto` (F001's determinism probes ran at `auto`); maximum intervention level I3: the DOS date and time set by the DOSBox-X `date` and `time` commands in the autoexec before GOAL runs (`vocabulary/interventions.md`: setting the clock is I3)
- **Design**:
  - start states: `d0`: a fresh launch, nothing restored (the config sha256 is the start state's); `d3`: `main` (F001's `main.sav`: a fresh launch with the DOS time set to 10:00:00 on 10-04-2026, then the keys `n Enter Enter b o b Enter Enter Enter Enter`; made by `run.py make-main`, kept in `.cache/states/driver/`, git-ignored; sha256 in every record), restored with Host+L after the title screen of a fresh process
  - controls: the DOS time fixed (I3) against free; within and across minutes; batches at least 20 minutes apart
  - arms: `d0-time-100000`: fresh launch at DOS time 10:00:00, then F001's D0 keys (`TO_MAIN` + `Esc`); `d0-time-HHMMSS` at five other minutes; `d3-time-100000` and `d3-time-free`: restore `main`, then F001's D3 keys (`Esc Up Enter Enter Enter c` [2.0 s] `r Enter Enter r`)
  - n per arm: `d0-time-100000` 10; five minutes × 2 (10:01, 10:02, 13:37, 21:00, 23:58); `d3`: 3 per batch, two batches per arm, at least 20 minutes apart; stopping rule: those records written (an aborted run is kept and repeated)
- **Measurements**: per read (a savestate after each key's settle poll, or after the 2.0 s delay after `c`): host UTC and local time (log); text screen digest and text (screen, ui-text); BIOS video mode byte and timer tick count (memory, I1); the words at `DS:7B62`, `DS:7B64`, `DS:8336` of GOAL.EXE (memory, I1). Once per record: GOAL.EXE's MCB, PSP, load segment and data segment base, and the bytes at `DS:0024` and `DS:00C0` against the listing's data segment (memory). Per record: launch time, config and its sha256, the batch label, DOSBox-X output lines, process exit, every wait (log).
- **Outputs**:
  - run records: `runs/E003/`;
  - evidence manifests: none (savestates hold the game's memory and stay in `scratch/` and `.cache/`);
  - `findings/F004-*.md`, status `proposed`.

## Scripts

`run.py` (arms `d0`, `d3`, and `make-main` for the start state) and `summarise.py` (tabulates the records; interprets nothing beyond the recorded values and the LCG of `214B:0688`). The data segment is located by `runtime/driver/savestate.py` (`find_program`): the MCB whose owner is the next segment and whose name is `GOAL`, its PSP (CD 20), load segment = PSP + 10h, DS = load segment + 2581h (static/goal-exe/README.md).

```
python3 experiments/E003-q001-inputs/run.py make-main --dos-time 10:00:00
python3 experiments/E003-q001-inputs/run.py d0 --runs 10 --dos-time 10:00:00 --batch fixed
python3 experiments/E003-q001-inputs/run.py d0 --runs 2 --dos-time 10:01:00 --batch minutes   # and 10:02, 13:37, 21:00, 23:58
python3 experiments/E003-q001-inputs/run.py d3 --runs 3 --dos-time 10:00:00 --batch A
python3 experiments/E003-q001-inputs/run.py d3 --runs 3 --batch A
# 20 minutes later: the same two with --batch B
python3 experiments/E003-q001-inputs/summarise.py
```
