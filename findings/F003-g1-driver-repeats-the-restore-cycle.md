# F003 The G1 driver repeats restore → key → screen read → reset from one savestate with the same before-screen, a verified restore and an I1 memory read in each record

- **Status**: proposed
- **Question**: Can the reusable driver repeat restore → key → screen read → reset 10 times from one stored savestate, with the same `before` screen each time, a verified restore, and an I1 memory read of the BIOS video mode and timer tick count in every record (G-M1's exit check, `docs/plan.md`)?
- **Tests claims**: none (no spec row exists yet); bears on G-M1 of `docs/plan.md`
- **Experiment and runs**: E002; E002-r0001 … E002-r0030 (three batches of 10: r0001 … r0010 at code `980e905`, r0011 … r0020 at `9f01cf9`, r0021 … r0030 at `f8c32f3`)
- **Artifact**: set `goal2-a949da2f`, variant none
- **Max intervention**: I2 (a savestate written at every read, and loaded at every restore; the reads of screen and memory from it are I1)
- **Tier reached**: V2
- **Confidence**: unreviewed (status `proposed`) — behavioural only; 29 of 30 records completed, every completed one with the stored screen digest after both restores; one record aborted (E002-r0009); the alternatives below are not excluded

## Answer

- G-M1's cycle repeats: in the batch E002-r0021 … E002-r0030 (the final code), 10 of 10 records completed; the 10 `before` screen digests are identical (`cd7f15fb…`, F001's title screen), and so are the 10 `start_state.sha256` (`5bd22b20…`). Batch E002-r0011 … E002-r0020 gives the same, 10 of 10.
- Restore is verified by screen: in 30 of 30 records `start_state.restore` names Host+L, and in the 29 completed ones (E002-r0001 … r0008, r0010 … r0030) the screen digest read after the first Host+L and after the reset Host+L equals the digest stored with the savestate, while the read just before the first Host+L was another screen (`487df15f…`).
- Memory is read as I1 in every completed record (E002-r0001 … r0008, r0010 … r0030): the byte at 0040:0049 is `03` at each of the three reads after the restore, and the dword at 0040:006C is recorded at each of the four reads, each with the host UTC time and the host local time with its UTC offset and zone name.
- One cycle of 30 aborted (E002-r0009): after Host+L no savestate was written within 15 s (four Host+S resent); it was the only launch whose title screen took 13.1 s instead of 1.80 … 1.87 s. Its record has no memory read: it was written by the code before `f8c32f3`, which now keeps an aborted record's launch time and reads.

## Method

- Machine: Ubuntu 24.04 in WSL2, kernel 6.18.40.1-microsoft-standard-WSL2; DOSBox-X 2024.03.01 SDL2 (apt), xdotool 3.20160805.1, Xvfb 2:21.1.12-1ubuntu1.8, Python 3.12.3, standard library only (each record's `runtime.fingerprint`). Driver: `runtime/driver/driver.py` (library), `runtime/driver/savestate.py` (the savestate parser), `runtime/driver/cycle.py` (the cycle, one `run/1` record per cycle); its route and constants are F001's (route A: Xvfb + DOSBox-X `output=surface` + xdotool; text page at `Vga` stream offset 0x86024, guest memory at `Memory` offset 0x78).
- Config (each record, with host paths replaced by `<work>` and `<game>`, and its sha256 `31a26168…`): `svga_s3`, memsize 16, `cycles=max`, core and cputype `auto`, sound off; autoexec mounts the game folder as C:, runs `goal`, then `exit`.
- Start state `title`: made once by `python3 runtime/driver/driver.py make-state title` at 2026-10-04T07:14:45Z (a fresh launch polled to the title screen, Host+S); sha256 `5bd22b20…`, screen `cd7f15fb…`, ticks at 0040:006C in the file `0x00093e73`. Kept in `.cache/states/driver/` (git-ignored) with the folder C: was mounted from; a launch refuses a state made with another folder (F001, Anomalies), and recreates that folder from the verified release copy.
- One cycle (arm `restore-title-key-n`, args `--start-state title --key n`): a fresh Xvfb (display 200 … 899, never `:99`) and DOSBox-X; poll for the title screen; key `n` and poll until the screen settles on another digest (so the restore must change the screen); Host+L, poll until the screen digest equals the stored one (`before`); key `n`, poll until settled (`after`); Host+L again, poll (`reset`); SIGTERM to the two process groups the driver started, SIGKILL after 10 s. Every read takes a savestate (Host+S, polled every 0.05 s); key holds 0.08 s, host-key steps 0.15 s, each logged with every poll count in the record's `log` observation.
- During development (not a run record): restoring into a session booted to the DOS prompt without starting GOAL failed once, DOSBox-X logging `Save state corrupted! Program in inconsistent state! - Memory_Size` and writing no savestate afterwards; the driver therefore restores after the title screen. Not investigated further.

## Observations

| Records | code | completed | `before` digest | stored digest | `after` digest | `reset` digest | mode b/a/r | ticks after restore (`before`, `reset`) | ticks `after` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E002-r0001 … r0010 | `980e905` | 9 of 10 (r0009 aborted) | `cd7f15fb` (9) | `cd7f15fb` | `487df15f` (9) | `cd7f15fb` (9) | 03/03/03 (9) | `0x00093e7b` or `0x00093e7c` | `0x00093e8c` … `0x00093e8d` |
| E002-r0011 … r0020 | `9f01cf9` | 10 of 10 | `cd7f15fb` (10) | `cd7f15fb` | `487df15f` (10) | `cd7f15fb` (10) | 03/03/03 (10) | `0x00093e7b` or `0x00093e7c` | `0x00093e8b` … `0x00093e8d` |
| E002-r0021 … r0030 | `f8c32f3` | 10 of 10 | `cd7f15fb` (10) | `cd7f15fb` | `487df15f` (10) | `cd7f15fb` (10) | 03/03/03 (10) | `0x00093e7b` or `0x00093e7c` | `0x00093e8d` … `0x00093e8e` |

- The tick count read just before the first Host+L (the displaced screen) grows from record to record: `0x000959de` in E002-r0001 (launch 07:20:58Z, 09:20:58+02:00 CEST) to `0x00098972` in E002-r0030 (launch 07:32:07Z, 09:32:07+02:00 CEST). Every record's host UTC and local times are in its `log` observations.
- Timings (from the `log` observations of the 29 completed records): title screen after 1.80 … 1.87 s; the first restore's digest matched at the first savestate poll, 4.00 … 4.11 s after launch; the reset matched at the first poll too. In 30 of 30 records dosbox-x was still running 10 s after SIGTERM and was ended by SIGKILL to its group; both processes were gone afterwards in 30 of 30 (`process` observation).
- E002-r0009: title screen after 13.07 s (17 savestate polls), `n` and its settle, Host+L at 15.34 s, then no savestate in four Host+S over 15 s; aborted. DOSBox-X's own output for that session was overwritten by the next record (the scratch folder was shared until `9f01cf9`); from r0011 each record carries DOSBox-X's save and load log lines, and none of r0011 … r0030 contains `corrupt`.
- `python3 tools/validate_runs.py runs/E002`: `ok: 30 document(s) valid`.

## Inferences

- G-M1's exit check is met by the driver at `f8c32f3` (E002-r0021 … E002-r0030) and at `9f01cf9` (E002-r0011 … E002-r0020): ten cycles each, one start-state hash, one before-state hash, a savestate restore verified by screen, a memory read recorded as I1.
- The restore is not instant in every session: one of 59 Host+L attempts (E002-r0009) left DOSBox-X writing no savestate. The slow launch in that record (13 s to the title against 1.8 s elsewhere) is consistent with machine load (another project's DOSBox-X runs on this machine), not tested.
- The ticks read after a restore are within 9 ticks of the value in the savestate file (`0x00093e73`) in every completed record, so they come from the restored state, while those read before it follow the host clock of the launch (E002-r0001 … E002-r0030). What the game derives from the clock is G5's question (Q001), not this finding's; the main session's static reading for T06 points at a DOS time call seeding the game's random generator (a lead, not a finding).
- DOSBox-X ignoring SIGTERM in every E002 record, against an exit 0.02 s after SIGTERM in F001's M:terminate, differs from F001; the difference between the sessions (a restored savestate here, none in M:terminate) is a candidate, not tested (E002-r0001 … E002-r0030).

## Alternatives considered

- "The `before` digest matches because the restore did nothing and the title was still shown": excluded by the read before the restore, `487df15f` in every completed record, and by the after-restore ticks, which are the savestate's and not the host clock's (E002-r0001 … r0030).
- "E002-r0009's failure is a driver defect (Host+L sent too early)": not excluded; the Host+L followed a settled screen, as in the other 29 records.
- "Taking a savestate at every read changes what the game does": not excluded; the neutrality of I2 is not tested (F001).

## What this does not establish

- Repeatability of anything beyond the title screen and the key `n`: no other start state, no other key, no match.
- That a restore reproduces game outcomes: F001's determinism observations stand; the clock is recorded here, not controlled (no I3).
- The cause of E002-r0009's abort, of the DOS-prompt restore failure, or of SIGTERM being ignored.
- Other DOSBox-X versions, machines, cycles settings; `runtime_writes` (game-archaeologist#19) is not registered here.

## Where the evidence is

`runs/E002/E002-r0001.json` … `E002-r0030.json`; `python3 experiments/E002-g1-driver-cycle/summarise.py` tabulates them. No evidence bundle and no release: the savestates hold the game's memory and stay in `.cache/` and `scratch/`.

## Reproduction

`bash setup/goal2-runtime.sh` (prints `ready`), then `python3 runtime/driver/cycle.py --runs 10 --start-state title` (makes the start state first if `.cache/states/driver/title.sav` is absent; a new start state has another sha256), `python3 tools/validate_runs.py runs/E002`, `python3 experiments/E002-g1-driver-cycle/summarise.py`.
