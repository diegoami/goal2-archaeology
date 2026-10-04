# E002 g1-driver-cycle

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T07 (#16)
- **Question**: Can the reusable driver repeat restore → key → screen read → reset 10 times from one stored savestate, with the same `before` screen each time, a verified restore, and an I1 memory read of the BIOS video mode and timer tick count in every record (G-M1's exit check)?
- **Hypotheses**:
  - H0: the cycle is repeatable: 10 of 10 records complete, the 10 `before` screen digests and the 10 `start_state.sha256` are identical, and the digest after each Host+L equals the one stored with the savestate — distinguished by those fields of the records
  - H1: the cycle is not repeatable (an aborted cycle, a `before` digest that differs, or a restore that never reaches the stored digest) — distinguished by `status`, the `before` digests and the `log` observation
- **Artifact**: set `goal2-a949da2f`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, python 3 on Ubuntu 24.04 in WSL2, DOSBox-X 2024.03.01, Xvfb, xdotool; maximum intervention level I2, because each read writes a savestate and each restore loads one (`vocabulary/interventions.md`)
- **Design**:
  - start state: `title` (the title screen of a fresh launch, `python3 runtime/driver/driver.py make-state title`; kept in `.cache/states/driver/`, git-ignored; sha256 in every record), restored by a fresh DOSBox-X process with C: mounted from the folder the state was made with, recreated from the verified release copy, GOAL run to its title, the key `n` to change the screen, then Host+L, polled until the stored screen digest returns
  - control: none (the host clock and the seed are recorded, not controlled)
  - arms: `restore-title-key-n`: after the restore, key `n`, poll until the screen settles, then Host+L again (the reset)
  - n per arm: 10; stopping rule: 10 records written
- **Measurements**: per read (before restore, `before`, `after`, `reset`): host UTC time and host local time with UTC offset and zone name (log); text screen digest (screen) and text (ui-text) from savestate component `Vga`; 1 byte at 0040:0049 and 4 bytes at 0040:006C from component `Memory` (memory, I1). Per record: host UTC and local time at launch (log); the DOSBox-X config with host paths replaced, and its sha256 (file); the cycles setting and config sha256 (`runtime.fingerprint`); the start state's sha256; whether dosbox-x and Xvfb exited (process); every wait, poll and key hold (log).
- **Outputs**:
  - run records: `runs/E002/`;
  - evidence manifests: none (the savestates hold the game's memory and stay in `scratch/` and `.cache/`);
  - `findings/F003-*.md`, status `proposed`.

## Scripts

`runtime/driver/cycle.py` (the driver is `runtime/driver/driver.py`, the savestate parser `runtime/driver/savestate.py`). The arm: `python3 runtime/driver/cycle.py --runs 10 --start-state title` (key `n` by default). The start state is made by the first run if `.cache/states/driver/title.sav` is absent.
