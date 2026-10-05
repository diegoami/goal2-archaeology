# E008 q005-r008-tactics

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T19 (#59)
- **Question**: What does R008 (country byte +0x2D) set, does it reach a match, and do continental
  means of the rating `1771:10E7` fall in the help file's order? (G5 Q005, its open part)
- **Static first** (CLAUDE.md rule 22): the answer is read from the decompiled view
  (`static/goal-exe/decompiled/`) and the listing (`static/goal-exe/code/`); `readers.py` lists the
  routines that access +0x2D and player +0xF, `summarise.py` computes the rating per continent from
  `GOAL.DAT` and compares it with E006's measured +3. The runs below corroborate one static claim
  only: that the quick result `0791:D733` reads the managed team's +0x2D (directly at
  `seg_0791_21.asm:867`, `:897`, and through `1771:0BC4` and `0791:B19D`).
- **Hypotheses**:
  - H0: the quick result does not depend on +0x2D: from one captain-screen savestate, the arm with
    +0x2D edited gives the same score and the same seed words at full time as the arm without
  - H1: it does: the edited arm differs in the score or the seed words, while the unchanged arm
    repeated from the same state gives the same score and seed words (F006: the same state gives the
    same result)
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on
  Ubuntu 24.04 in WSL2, `cycles=30000` (E004's and E006's value); maximum intervention level I3 (one
  byte of guest memory edited, in the `edited` arm only)
- **Design**:
  - start states: E006's published main-screen states `e006-1000-r0001` and `e006-1337-r0004`
    (release E006; adopted by E007's `run.py adopt`, which checks the sha256 against the manifest)
  - per run (`run.py quick`): a fresh launch, Host+L of the start state, E004's keys
    `Esc Up Enter Enter` to the captain screen (an Enter on the team screen if it comes first),
    Host+S there; then Host+L of the arm's state: `unchanged` the captain-screen savestate as saved,
    `edited` the same savestate with Denmark's (country 7, managed) +0x2D XOR 0x31 (elements 1, 5, 6:
    the ones `1771:0BC4` reads; 1 and 5 also read by `0791:D733`), written into the savestate's Memory
    component; the byte read back after the load; then E004's quick result (`Enter r`) to full time
  - arms per start state, in order: `unchanged`, `edited`, `unchanged` (the repeat shows the save and
    load path is deterministic here); 2 start states, 6 runs (the task's bound is 5 states x 2 arms)
  - stopping rule: those records written; an aborted run is kept and repeated once
- **Measurements**: at the main screen, the captain screen, after the arm's load and at full time:
  the screen, `DS:7B62` and the word at the far pointer `DS:A978` (the seed words), the score bytes
  `DS:9B3C`, `DS:9B3D`; during the match E004's compact reads; the edited byte before and after, and
  the sha256 of both savestates
- **Analysis** (`summarise.py`): the per-continent table; the reader table; per start state and arm,
  the score and the seed words at full time
- **Outputs**: run records `runs/E008/`; evidence manifests none (the start states are E006's,
  published; the captain-screen savestates are made again by each run and stay in `scratch/`);
  `findings/F010-*.md`, status `proposed`

## Scripts

```
bash setup/goal2-runtime.sh
python3 experiments/E007-q009-player-screen/run.py adopt --from E006-r0001
python3 experiments/E007-q009-player-screen/run.py adopt --from E006-r0004
python3 experiments/E008-q005-r008-tactics/run.py quick --state e006-1000-r0001 --arms unchanged,edited,unchanged --batch b1
python3 experiments/E008-q005-r008-tactics/run.py quick --state e006-1337-r0004 --arms unchanged,edited,unchanged --batch b1
python3 experiments/E008-q005-r008-tactics/summarise.py
```

## Amendment 1 (2026-10-05, after E008-r0006)

- E008-r0001 carries the batch label `b0`: it was run alone, as a first check of the runner, and is
  the first `unchanged` arm of `e006-1000-r0001` as designed; r0002 and r0003 (batch `b1`) are that
  state's `edited` and repeated `unchanged` arms.
- On `e006-1000-r0001` the edited arm differs from both unchanged arms (score and seed word); on
  `e006-1337-r0004` it gives the same score and seed word as both. One state each way does not show
  how often the edit changes a quick result, so two more of E006's published states are run, each
  `unchanged` then `edited` (no repeat: the four runs above already show the unchanged arm
  repeating): `e006-2100-r0005` and `e006-0630-r0008`. Batch `b2`. With them the experiment has 4
  start states and 10 runs, inside the task's bound of 5 states x 2 arms.
