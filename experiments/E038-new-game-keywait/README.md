# E038 new-game-keywait

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T82 (#367, a request from goal2)
- **Question**: (1) a savestate at each new-game screen with the CPU inside 214B:08DD's INT 16h key read, for goal2's core; (2) every interrupt between the title's load prompt and the first manager menu, with its call site and what it reads or writes; (3) the key-read sites and caller frames of the new-game screens.
- **Hypotheses**:
  - H0 (static, T82): the title 1771:080C draws its prompt, runs an animation (1771:07B4 → 06F3) that polls 214B:0723 and waits in CRT `Delay` 214B:1E09, then calls 214B:08DD at 1771:085A; so a state taken after the animation is in 08DD's INT 16h read (Intr 235C:000B returning to 214B:0904), and the `title.sav` checkpoints (CPU at 214B:1E3E–1E44) were taken during the animation;
  - H1: the interrupts between the load prompt and the first manager menu are reached both by `int` instructions and by Turbo Pascal's `Intr`/`MsDos` (235C:000B/0000), which jump to the vector by a far return; a Unicorn run of the original's code from the title state, served only the interrupts the trace logs, reaches the same manager-menu screen, seed words and game arrays as DOSBox-X — distinguished by comparing the trace's end with the DOSBox-X run's manager-menu state.
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb in a Linux cloud session (`docs/cloud.md`), `cycles=max` (the driver's default and the `title.sav` checkpoints'; `cycles=30000` crashed DOSBox-X at the first savestate in this session, a scratch probe, not a record); maximum intervention level I3 (DOS date and time in the autoexec, as E006-r0001).
- **Design**:
  - `run.py`: one fresh launch at DOS time 10:00:00 on 10/04/2026; F001's keys `n Enter Enter b o b Enter Enter Enter`; at each screen savestates are polled until the screen is the expected one and, where the screen reads its key through 08DD, the CPU is in 08DD's INT 16h call; one state per screen kept as `.cache/states/driver/e038-<screen>-r<nnnn>.sav`, named in the record, stored on the owner's Drive under `goal2-archaeology/E038/`;
  - `trace.py` (no record: an emulation of the original's code, a static method): from the kept `title-load-prompt` state, the same keys answered at 08DD (and at the name entry's "key pressed?" poll 214B:0DB9, which never waits in the read), every interrupt logged and served; its log is committed under `out/`;
  - stopping rule: one completed record; an aborted run is kept and repeated once.
- **Measurements**: per kept state: the screen, BIOS mode byte and tick count, CPU registers, 08DD's frame and callers' return addresses, `DS:7B62`, `DS:7B64`. Trace: every 08DD read (site, callers, seed words), every "key pressed?" poll site and count, every interrupt (vector, AH/AL, registers in, call site, callers, what was served); the end screen and seed words compared with the record's `manager-menu` state, and the game arrays (F007) and data segment compared byte for byte.
- **Outputs**: run records `runs/E038/`; trace logs `experiments/E038-new-game-keywait/out/`; `findings/F032-*.md`, status `proposed`.

## Scripts

```
source .cache/cloud.env
python3 experiments/E038-new-game-keywait/run.py --batch b1
python3 experiments/E038-new-game-keywait/trace.py .cache/states/driver/e038-title-load-prompt-r0001.sav --keys 6E,0D,0D,62,6F,62,0D,0D,0D --key-polls 214B:0DB9 --out experiments/E038-new-game-keywait/out/trace-r0001.json
```
