# E005 q003-cycles

Copied from the research task's contract when the experiment is created. After the first run this
file is append-only. A changed design is a new experiment, or `v2/`.

- **Task**: T12 (#33)
- **Question**: Do `cycles`, the host speed or wall-clock time change a match, and why are the halves so unequal at `max`? (G5 Q003)
- **Hypotheses**:
  - H0: from one seeded start state, the same arm (quick or watched, `match.py`) gives the same final score, the same commentary lines and the same `DS:7B62` at full time at `cycles` 5000, 30000 and `max`, whether the state is restored (its delay calibration `DS:A9FF` made at 30000) or the game is launched afresh at the state's DOS time (calibrated anew); `cycles` changes only the host time a match takes — distinguished by comparing every run with the same arm's first restore at 30000
  - H1: some run differs; then the time source through which `cycles` reaches the match is sought in the listing
  - the halves: F001's first half under 1 s and second half 6.5 … 9.7 s at `max` and 60000 come from the delay calibration and DOSBox-X's `max`, not from the engine — distinguished by the guest BIOS ticks and the host seconds of each half, with `DS:A9FF` read in every run, and by F001's own probe re-run at `max` with every poll's ticks, `DS:A9FF` and delay byte read
  - static: `214B:1DA7` runs only at start-up; the only delay of a match is the calibrated busy-wait `214B:1E09`, and no time source reachable from a match writes game state — distinguished by the callers of `1DA7`, every reader of the BIOS tick (0x46C), INT 1Ah, INT 21h AH=2Ch, the PIT ports 0x40–0x43, and the delay routines of `0791`
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Runtime**: `runtime/driver/driver.py@<commit in each record>`, DOSBox-X 2024.03.01 in Xvfb on Ubuntu 24.04 in WSL2; `cycles` 5000, 30000 or `max`, a controlled input named in each record (arm, `actions.args`, an observation, `runtime.fingerprint.cycles`); maximum intervention level I3 (the DOS date and time set in the autoexec before GOAL runs, verified by DOS's read-back, F004) in the fresh launches; the restores do not set the clock (the state brings its own BIOS ticks)
- **Design**:
  - start states: E004's recipes `e004-1001` (Denmark v England, DOS 10:01 on 10/04/2026) and `e004-1337` (Sweden v Denmark, DOS 13:37), remade at `cycles=30000` with `experiments/E004-q002-quick-result/run.py make-state` (git-ignored; sha256 in every record). Their `DS:7B62` at the captain screen is E004's (`0xf3ab`, `0xfabd`), their `DS:A9FF` 0x10b3
  - routes (`run.py`): `restore`: a fresh DOSBox-X process at the run's `cycles`, Host+L of the state, then the arm's match; `fresh`: a fresh launch at the run's `cycles` with the DOS clock set to the state's DOS time (I3), E004's keys to the captain screen (the team screen's Enter where it comes first), then the arm's match
  - arms (`runtime/driver/match.py`, unchanged): `quick`: Enter and `r` in one burst; `watched`: Enter and Right ×5 in one burst; then an Enter only on a stable `hit any key` screen before full time or on the team screen; no other key between kick-off and full time; each key, its moment and its reason in the record
  - per state and `cycles` setting: 3 restores of each arm (`run.py restores --reps 3`: quick then watched, three times) and 1 fresh launch of each arm (`run.py fresh`); 2 states × 3 settings × 2 arms × 4 = 48 match records
  - calibration (`run.py calibrate`): 3 fresh launches to the title screen per setting, `DS:A9FF` read there
  - F001's probe (`probe_f001.py`): `runtime/spike/probe.py match --cycles max --reps 1` as F001 ran it (its `main.sav` made at `cycles=auto`, its keys `c` and Right ×5, its Enter at every half-time poll), unchanged, with each of its polls' savestate also read for the BIOS ticks, `DS:A9FF`, the delay byte and the commentary rows; its output written under this folder (`measurements/`), never over an earlier file
  - order: the restores and fresh launches at 30000 and 5000 first; the runs at `max` with no other run of this experiment going; F001's probe last
  - stopping rule: those records written; an aborted run is kept and its run repeated once
- **Measurements**: E004's (per read: host UTC time, screen digest, commentary rows, `DS:80EE`, `DS:7B62`, score bytes; the commentary records from the ring `DS:7C38`; at the restore, title, main screen, captain screen and full time: the full screen, BIOS mode byte and ticks, `DS:7B62`, `DS:7B64`, `DS:8336`, `DS:A9FD`, score bytes, delay byte), and in addition: at every read during the match, the host seconds since the starting burst (monotonic clock, the same `match.play` measures with), the BIOS tick count and the dword `DS:A9FF`; at every full read, `DS:A9FF`; per record, the `cycles` setting, the other DOSBox-X and Xvfb processes on the host (pid, seconds running, name; not started by this run) and `/proc/loadavg`, at launch and at the end
- **Analysis** (`summarise.py`): per run the route, `cycles`, arm, final score, events, `DS:7B62` at full time and `DS:A9FF`, and whether it is identical (score, events, every commentary line, `DS:7B62`) to the same state's and arm's first restore at 30000; for every watched run the host seconds from the starting burst to the first read holding `HALF TIME` and from there to the first read holding `FULL TIME` (and from the team-screen Enter to full time), the guest seconds of the same spans from the BIOS ticks (18.2065 ticks/s), and the ratio first half / second half (host; the second half from the team-screen Enter, as F001's `second_half_started_after_s`); F001's unequal halves count as reproduced when that ratio is under 0.5 at `max` [designed: F001's M:match-speed gives 0.10 and 0.14 at 60000 and `max`, 0.93 … 0.96 at `auto`, 5000, 10000 and 30000]; per restore, the cycles in effect implied by the guest seconds against the 30000 restores of the same state and arm (the state's delay count is fixed, so guest time scales as 1/cycles); checks: every record names its `cycles`, every record that sets the clock declares I3
- **Outputs**:
  - run records: `runs/E005/`;
  - F001's probe re-run: `experiments/E005-q003-cycles/measurements/`;
  - evidence manifests: none (savestates hold the game's memory and stay in `scratch/` and `.cache/`);
  - `findings/F006-*.md`, status `proposed`.

## Scripts

```
bash setup/goal2-runtime.sh
python3 experiments/E004-q002-quick-result/run.py make-state --dos-time 10:01:00   # and 13:37:00
python3 experiments/E005-q003-cycles/run.py calibrate --cycles 5000 --reps 3 --batch c1   # and 30000, max
python3 experiments/E005-q003-cycles/run.py restores --state e004-1001 --cycles 30000 --reps 3 --batch b1
python3 experiments/E005-q003-cycles/run.py fresh --state e004-1001 --cycles 30000 --slot 1 --batch b1
python3 experiments/E005-q003-cycles/probe_f001.py
python3 experiments/E005-q003-cycles/summarise.py
python3 tools/validate_runs.py runs/E005
```

## Amendment 1 (2026-10-04, after E005-r0011)

- **One observation per match read.** T07's Done-when 7 keeps every tracked file under 1 MB. A watched match at 5000 makes thousands of reads, and E004's five observations a read (about 1.2 KB) would pass that. From the commit after `e5280ff`, each read is one observation: a JSON list of host UTC time, host seconds since the starting burst, BIOS ticks, `DS:A9FF`, screen sha256, `DS:80EE`, `DS:7B62`, the score bytes and the commentary rows (`run.py` `read_observation`). The values measured are E004's, plus the timing ones; only their form changes.
- **The savestate lines of DOSBox-X's output.** Every savestate writes two lines to `dosbox.out` (`LOG: File : <work>/IntTimer10 is N bytes`, `Saved. (Slot 1)`). They are now counted in their own observation rather than copied.
- **Records before the change.** The records written by processes started from `e5280ff` keep the first form: calibration E005-r0001 … r0009 and the first b1 runs. `summarise.py` reads both forms.

## Amendment 2 (2026-10-04, after E005-r0031)

- **E005-r0031 is 1.48 MB.** It is the first watched restore at 5000: 2253 reads in 1254.9 host s, one observation per read (amendment 1). T07's Done-when 7 keeps every tracked file under 1 MB. The record is kept as written (L207). From the commit after `6eb517d`, a match's reads are one observation: a JSON list with one list per read (`run.py` `read_row`, `reads_observation`; the fields as in amendment 1, with the read's step first). That is about 250 bytes a read.
- **The invocation that wrote it was stopped.** `restores --state e004-1001 --cycles 5000 --reps 3` (batch b3) was stopped by SIGINT to its process once E005-r0032 was written, before its next watched run could write a record of the same size. The driver ends its DOSBox-X and Xvfb when interrupted, and no record is written for the run it was in. That run's id is reserved and not used. The rest of e004-1001 at 5000 is a new invocation with `--reps 2`. It adds 2 quick and 2 watched restores, so e004-1001 has 4 quick restores at 5000 (E005-r0030, r0032 and the two new ones) and 3 watched.
- `summarise.py` reads all three forms.
