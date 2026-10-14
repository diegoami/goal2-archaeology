# E026 tactics effect — reproduction and provenance

The listing answered the mechanism questions before the measurements. F026 cites each
reader and preserves `read`/`inferred` distinctions. Whole watched matches use the original
bytes in the E021 Unicorn harness, with no substitution hook; runs quantify one team byte
flip at a time on Denmark against country 19. Per-player overrides in the saved squad limit
which players a team flip reaches. The other team's tactics are unchanged at the start.

The watchstart savestate is E011-r0001's released output, SHA-256
`d68e48c734a742a63e707a8c451b9011ef03b452ebd91f239d86f875464e07a9`;
`asset()` verifies the full hash in the run record before emulation. Packed GOAL.EXE is
set `goal2-a949da2f`, SHA-256
`a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`.
Neither original bytes nor savestates are committed.

Primary logs contain 270 attempted matches: 30 successful seeds per arm except e7,
where seed 54168 stopped at an undeclared key wait, leaving 29 successful matches.
That original record remains in `out/e7-s0-9.jsonl`; it is excluded, never replaced.
No extra seed was introduced to compensate. The summary reports the actual N.

A complete e3 arm was reproduced on 2026-10-14 with Python 3.12, Unicorn 2.1.4:

```sh
python3 -B experiments/E026-tactics-effect/arm.py --arm e3 --first 0 --count 30 --log experiments/E026-tactics-effect/out/repro-e3-s0-29-20261014.jsonl
python3 -B experiments/E026-tactics-effect/verify.py
python3 -B experiments/E026-tactics-effect/analyze.py experiments/E026-tactics-effect/out/analysis-full-repro-20261014.md
```

For another re-run, choose a new log filename and give it to `verify.py --repro PATH`.
Every writer refuses an existing output. The logged scores, raw counters, final clock,
board and draw digests, scorers and declared inputs agree for all 30 seeds. All 40
repeated pairs in the summary logs agree in every deterministic field. A changed shots
counter is rejected by the verifier. Timing is not deterministic. The original N, means
and intervals remain byte-for-byte identical after ignoring the repeated-pair count.
The first detached attempt used system Python without Unicorn and failed before running
any match; its log remains as `out/repro-e3-full-20261014.err`.

The original 275 CPU-timed attempts sum to 24,175.1 seconds; the resumed 30-match arm
adds 1,237.8, for 25,412.9 recorded seconds (7.059 hours). Seven early attempts and the
separate final-tactics match have no CPU timer. Estimating those eight at the original
87.9-second recorded mean puts the whole experiment near 7.3 hours, within the task's
approximate 8-hour budget. Nine primary arms cover one direction of each team-byte flip;
reverse directions, combinations, other pairs and mid-match changes are unmeasured.

The real Ghidra union regeneration is retained in `out/ghidra-full-20261014.log` and
`out/ghidra-resume-20261014.err`: 729 functions, 726 decompiled, three failures whose
addresses and messages match the prior main view (0000:0000, 0791:1A04, 214B:05F0).
`out/evidence-sha256-20261014.tsv` records the hashes of the completed scripts and
experiment outputs at that checkpoint. Later evidence is added in new files or appended
match rows; existing rows and committed evidence are preserved.
