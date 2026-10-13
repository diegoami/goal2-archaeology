# E027 discipline-rules — notes (T53, F027)

Append-only. Addresses are `segment:offset` (image paragraphs); listings are `static/goal-exe/code/seg_*.asm`.

## 1 What was run

All runs are the original code in Unicorn (`runtime/emul/watched_match.py`, E010's second-half loop), each as its own systemd unit (`goal2-t53-*`) with its output in `out/`. No DOSBox-X run.

- `probe.py` (no argument): E011-r0001 and r0002 from their watchstart savestates, unhooked, code hooks that only read. Declared input: the delay byte (`WatchedMatch.run()`'s standard). Logs: `out/probe-20261013T142940Z.log` (first hook set, run 1), `out/probe-20261013T143505Z.log` (adds the foul funnel, the dead-ball callers; the log F027 cites). The two records are one match: identical line for line.
- `probe.py --seeds N FIRST`: E011-r0001's start state with `DS:7B62 := seed` (declared input). `out/probe-seeds-20261013T143727Z.log` (seed 1001 complete, stopped by me during seed 1002 to add the whistle hooks: the partial seed 1002 is not used), `out/probe-seeds-20261013T144123Z.log` (seeds 2001..2016 with the whistle hooks; 16 of 16 complete). `summarise_seeds.py` -> `out/seeds-summary-20261013T151204Z.log` (17 complete matches).
- `quick_second_half.py`: E010-r0010's half-time savestate (sha256 3c7983fa4869d32700000000... see the log header) through the original second half with the declared inputs `DS:9A3D := 1`, `DS:9B3A := 2, 2`, `DS:7B62 := seed`. Not a recorded non-friendly state. Logs: `out/quick-second-half-20261013T143148Z.log` (seeds 1, 2; a trial), `out/quick-second-half-20261013T143455Z.log` (seeds 101..; stopped by me after 18 seeds because the savestate's foul table is one fixed table that every seed reads in the same order), `out/quick-second-half-20261013T144248Z.log` (seeds 301..340 with `random-table`: `DS:8337+1..255` := Python random 0..15, a further declared input). `analyse.py` -> `out/analysis-20261013T144153Z.log` (seeds 1-2 and 101-118: the 20 halves of F027's first stand-in counts) and `out/analysis-20261013T145855Z.log` (the 40 random-table halves).
- `out/run-*.stdout/.stderr` are each unit's streams (the stdout of a unit equals its log). `out/run-named-regen.*` is the Ghidra regeneration of `static/goal-exe/named/` (the 3 known failures: main_program, 1A04, 5F0 of 7000).
- `out/tests-static-*.log/.err` are suite runs (see the PR body for the final one).

## 2 SHA-256 of the logs at the commit that added this file

See `out/` and `git log`; the hashes at the time of writing:

- analysis-20261013T144153Z.log ae9ebc32ef24f507c3ce62d48abf3f159840386fe653f5cde099530a63409f8c
- analysis-20261013T145855Z.log 4eb3de8dbd92ef2a6a2dcf181e23220becb77bbe1ab6b777f57a3eaf9a1b55df
- probe-20261013T142940Z.log fa5b8f539f68b1e19fd46e456cdd6b84578a7b6595cc8c202f0d6c260f57911e
- probe-20261013T143505Z.log 560c82fe5c6909490db6d7abc62e937835cdb14333809c1070beaa9526e02f48
- probe-seeds-20261013T143727Z.log 748f576f39b2b4630868c2e8e2d207519ec2a39d89fdd5aad59fd03e63ac244a
- probe-seeds-20261013T144123Z.log c238571268a7a8bbf7e80725820a11ef76f715b4fada78aecde420aa411b7eea
- quick-second-half-20261013T143148Z.log b523a4e0f0e590beb088c05d695edbd5d670cde7fd7911b161b9644a1a01daa1
- quick-second-half-20261013T143455Z.log 765c3065e313ebd4e21e2eb7cfb02d70cfeec6c62d47f2287532f5c281f48f03
- quick-second-half-20261013T144248Z.log f1bef5a60fd3376ecce2754a56ce6bd406805af3097a787b10556417b73f83f5
- seeds-summary-20261013T151204Z.log 456c5af7a2d77db5fb97da85b7e92fd919525ab0fb21d2ec87f23a059132b13c

Input assets (release assets, by hash): E011-r0001 watchstart d68e48c734a742a63e707a8c451b9011ef03b452ebd91f239d86f875464e07a9; E011-r0002 watchstart 9d475dcbec7822232aa7877c46e09ab9447520fc3e01fbc351d50ecb3155e100; E010-r0010 half-time 3c7983fa4869d327 (full hash in the quick logs' headers).

## 3 Checks

- Each hook address is checked to be an instruction start of the listing before the run (`probe.py` prints the listing line beside it).
- `8206` entries equal the Fouls statistic `DS:7B84` summed over both sides in 17 of 17 watched matches; `DS:831F` at full time equals 91 + min(5, events) in 17 of 17 watched matches, 20 of 20 and 40 of 40 stand-in halves; the half-time whistle is at 46 in 16 of 16 logged.
- Not checked: `B27F`, `B7FA`, `5A8F`, `3651`, `3558` (no fixture end in any state).

## 4 Where static analysis was enough and where it was not

The listing gave every rule. Runs were needed only to count (asks of `8062`, the foul funnel, fouls per match) and to check the clock, the budget and the cap's polarity by the original's code. A non-friendly quick result could not be had from a recorded state (section 1).

## 5 A surprise

F005's rates imply about 6 fouls a match at the table's frequencies; 17 seeded replays of E011's start state give 3.06 (se 0.30), with 0.65 bookings and 0.29 injuries. Unreconciled; F027 says so.
