# E039 start-year

Copied from the research task's contract when the experiment is created. After the first record this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T83 (#369, a request from goal2, follow-up to #367 / F032)
- **Question**: (1) where and how the original reads the DOS date, where it keeps the result, and how the start year and opening stage follow from it; (2) a state goal2's core can resume before that read; (3) every interrupt from there to the title's key read, and proof by two dates that serving only those reproduces DOSBox-X.
- **Hypotheses** (static, T83):
  - H0: the only date read is `214B:1C63` → `GetDate` `235C:006C` (`int 21h` AH=2Ah at `235C:0071`), the last step of unit start-up `214B:206A`; the year goes to `DS:A9FD`, read only by `init_new_game` `1771:9B85` after the title's `n`: start year `[DS:A923]+0x3A` = year + 1, made even; `+0x40` = (start year mod 4 = 2); stage `+0x3C` = `DS:118E[+0x40]` (2 or 5);
  - H1: no key read precedes the date read, so the state is caught in DOSBox-X during start-up (before `DS:A9FD` is written) and carried to `235C:0071` under Unicorn (`derive.py`); from there, served the date and only the interrupts the trace logs, the original reaches the title's read and the first manager menu as DOSBox-X does at the same date: distinguished by comparing screens, `DS:A9FD`, the game record's `+0x3A`, `+0x3C`, `+0x40`, and `DS:7B62`, `DS:7B64` at the title, the bulletins and the manager menu, for DOS years 1990 (start 1992, stage 2) and 1992 (start 1994, stage 5).
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: as E038, `cycles=30000` (fixed: the start-up calibration `DS:A9FF` is then not host-dependent).
- **Design**:
  - `run.py --dos-date 10/04/YYYY`: E038's new game at DOS time 10:00:00 on that date; first savestate 0.2 s after the window appears (savestates during DOSBox-X's boot crash this build at fixed cycles); the first savestate before the title with the CPU in GOAL.EXE's code and `DS:A9FD` = 0 kept as `pre-date`; then E038's states (title … manager menu); one record per date, years 1990 and 1992;
  - `derive.py`: from a `pre-date` state to `235C:0071`, the BIOS tick modelled as one per 1,647,750 instructions (30000 × 54.925 ms), the interrupts served as its docstring says; the derived state written and put on the owner's Drive; its log under `out/`;
  - `trace.py`: from the derived state, the date served (each of the two), E038's keys, every interrupt logged and served; compared with the record of the same date; logs under `out/`;
  - stopping rule: one completed record per date; an aborted run is kept and repeated once.
- **Outputs**: `runs/E039/`; `experiments/E039-start-year/out/`; `findings/F033-*.md`, status `proposed`.

## Before the first record (2026-10-22)

The first invocation (`--dos-date 10/04/1990`, then 1992, at the commit that added `run.py`) wrote no record: the
title's read was not reached within the then 60 s wait, and the record writer then refused the record for a host
path in it (which field was not printed; `run.py` now names it). Its `pre-date` state was written before the abort:
kept, renamed `.cache/states/driver/e039-1990-pre-date-aborted-1.sav` (sha256 `2306bd25…`, CPU load+2382:02BE), and
used only to develop `derive.py` (not cited by any finding). The 1992 invocation did not start (the dirty-tree check
refused it).

## Amendment 1 (2026-10-22, after E039-r0002)

E039-r0001 (1990) and r0002 (1992) completed without a `pre-date` catch: the savestate polls, 0.58 s apart, fell
before GOAL was loaded and then at the title (the start-up before the date read lasts less than one poll interval
at `cycles=30000`). `run.py` gains `--catch-only` (launch, the pre-date check on every read before the title, stop at
the title: no new-game keys) and `--first-save S` (the delay before the first savestate, to move the polls' phase).
Catch attempts are run with `--dos-date 10/04/1990 --catch-only` and `--first-save` stepped from 0.2 s by 0.1 s until
one record keeps a `pre-date` state; each attempt is a record (arm `start-year-1990-catch`). The derived state is made
from that record's state.
