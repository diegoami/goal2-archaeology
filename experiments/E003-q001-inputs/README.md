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

## Amendment (2026-10-04, after E003-r0026)

Added arms, appended here; the design above is unchanged. The d3 records of batch A (r0001 … r0006) showed the seed word before `r` differing between runs of one batch, and two screens after the key that starts the match (the kick-off pause, or a later moment of the live match, depending on when the settle poll found two equal reads); the static route found the in-match key poll `0791:9372` and GetDate's year at `DS:A9FD`. To test those leads:

- `d3b-time-free` (`run.py d3b`): as `d3`, but the Enter on the captain screen that starts the match and `r` are sent together (`Enter+r`: two key presses, no poll between), then the settle poll; the remaining keys `Enter Enter r`. n: 3 in batch A and 3 in batch B.
- `d0-time-100000-date-10041993`: as `d0-time-100000` with the DOS date 10-04-1993 instead of 10-04-2026 (the year GetDate gives at `214B:1C63`). n: 2.
- `d0-time-free`: as `d0`, DOS date and time not set (F001's D0 condition), as a control. n: 2.

## Amendment 2 (2026-10-04, after E003-r0033)

DOSBox-X 2024.03.01's `DATE` takes `MM/DD/YYYY` only: given `10-04-1993` (the form `run.py` passed in r0001 … r0033 and in `make-main`) it prints the current date and changes nothing (a check outside the records: `date 10-04-1993`, then `date /t`, printed `10/04/2026`; `date /?` names the form `MM/DD/YYYY`). So in r0001 … r0033 and in the `main` state the DOS date was not set: it was the host's date, 2026-10-04 (each record's launch time), and the records' I3 text naming the date is wrong about the date; their DOS time was set (read back from the BIOS ticks). The arm `d0-time-100000-date-10041993` (r0030, r0031) therefore did not test the date. From r0034 the date is passed as `MM/DD/YYYY` (`runtime/driver/driver.py` refuses other forms), and each read also records the word at `DS:A9FD` (the year GetDate returned, `214B:1C63`). Added arm: `d0-time-100000-date-10041993` repeated with `--dos-date 10/04/1993`, n: 2.

## Amendment 3 (2026-10-04, after E003-r0044)

Added script: `static_refs.py <unpacked GOAL.EXE>` (the static route's search for every reference to the Dos unit's clock routines in segment 235C, through the relocation table, and for every `mov ah, 2Ch`); it writes no record. No run follows.

## Amendment 4 (2026-10-04, review rework round, after E003-r0044)

Review R1 showed that a date with the right form but no meaning (`99/99/1993`, a local run of the reviewer, numbered 51, not in this repository) was accepted and declared set, while DOS kept the host's date. From E003-r0045:

- `runtime/driver/driver.py` refuses a date or time that no calendar or DOS has (a real date, years 1980–2099; a real time), before any run (`run.py` checks first).
- After `date` and `time`, the autoexec writes DOS's own `date /t` and `time /t` to `CLOCK.TXT` on a drive D: mounted from the session folder (not the game folder); `Driver.launch` reads it back when the title screen is up and raises `ClockNotApplied` unless the date is equal and the time is within −1 … +5 s of the one set. The record carries the read-back (`file` observation "DOS clock read back"), and its I3 text says either "applied: DOS reported date … and time …" or "NOT verified as applied: …", and the run is aborted in the second case.
- `summarise.py` prints the clock requested and the clock applied: the read-back where a record has one; else the year at `DS:A9FD` (r0034 … r0044), or "date not applied (host's)" for the `MM-DD-YYYY` records (r0001 … r0033).
- E003-r0045 and r0046 (arm `d0-time-100000-date-10041993`) aborted on the first version of the check: DOS read 10:00:00 back as `9:59:59` (DOS time is BIOS ticks, and `time /t` truncates; the 10:00:00 ticks `0x000A004A` are 35999.98 s), outside the 0 … +5 s first allowed; their I3 text says "NOT verified as applied". The check now allows 1 s early. E003-r0047 and r0048 (same arm) completed with the read-back `10/04/1993 9:59:59`.
- The `main` start state is unchanged (made with the ignored `10-04-2026`, so with the host's date, 2026-10-04, and a DOS time read back from its ticks); d3 and d3b runs from it set no clock that matters, since the restore brings its own ticks.

## Amendment 5 (2026-10-04, review rework round 3, after E003-r0048)

- Drive D: and the clock read-back are now in every launch, clock option or not, so a savestate's drives do not depend on it: a `main` state made with the clock option crashed DOSBox-X when restored with the clock free (review round 2 R1, the reviewer's local runs). Every record from E003-r0049 carries the read-back; free launches' read-back is the host clock.
- The read-back may be from 1 s before to 2 s after the time set (was +5 s, amendment 4): the read-back is written before `goal`, and the clock at the title is 0.7 … 1.1 s past the time set in every fixed launch (E003-r0007 … r0026, r0030, r0031, r0043, r0044, r0047, r0048), so +1 s at most; one more second is a designed margin, not measured.
- Real dates and times in another form (`1/1/1993`, `9:00:00`) are refused, as the form rule always said.
- The `main` state was made again with the documented command, `run.py make-main --dos-time 10:00:00 --dos-date 10/04/2026` (sha256 `813cf85f…`, screen `18190236…`); the earlier one (`20c5bd8b…`, cited by E003-r0001 … r0006, r0027 … r0029, r0034 … r0042) is kept aside in `.cache/states/driver/pre-rework3/`. Then `run.py d3b --runs 2 --batch rework3`: E003-r0049, r0050.

## Amendment 6 (2026-10-04, review rework round 4, after E003-r0050)

Start states now carry their drive layout (`drive_layout` in `<name>.json`: `mount c <game>`, `mount d <work>/dosclock`), written by `run.py make-main` and `driver.py make-state`; `run.py d3`/`d3b` (and `cycle.py`, `Driver.launch`) refuse, before DOSBox-X restores anything, a state whose layout differs or is missing: a state made without D: stalled the restore under the driver that mounts D: (review round 3). The `main` state of E003-r0049, r0050 (`813cf85f…`) has no layout recorded and is refused; it is kept aside in `.cache/states/driver/pre-rework4/`. To run d3 or d3b again: `python3 experiments/E003-q001-inputs/run.py make-main --dos-time 10:00:00 --dos-date 10/04/2026` first. No E003 run follows.
