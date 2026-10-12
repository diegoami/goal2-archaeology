# E022 m2a-contests — notes (T45, milestone M2a)

Addresses are `segment:offset` (image paragraphs); listings are `static/goal-exe/code/seg_0791_*.asm`. Append-only.

## 1. What was run

`python3 experiments/E022-m2a-contests/probe.py` replays E011-r0001 and E011-r0002 from their watchstart savestates (E021's `WatchedMatch`, unhooked) with code hooks that only read. About 4 minutes. Each hook address is checked to be an instruction start of the listing before the run; the log prints the listing line beside every branch hook.

## 2. Logs (never overwritten)

- `out/probe-20261012T185044Z.log` (SHA-256 `eec1cc38df6a7d993a8eac3bf30368839e3ddb859a452c74e288ce9da461ea8d`): first run. Counts are valid. Three labels were wrong: `5613` (reached from many early exits, not "287C returned 0": 69352), `5616` (also reached by 55FC's `jle` when the product is 0 or below) and `5D99`. It lacks the per-element result table.
- `out/probe-20261012T185316Z.log` (SHA-256 `7aa08112c096cc0b347748b9c3a4683670cf4fb42a3019bd9434639da223ebde`): second run. Labels `3A0F`/`3A16` (a signed byte `[bp-2]`, not a word), `3C63` (the comparison before the DS:8324 branch) and `53EC` (the CHALLENGER's pitch record through the frame chain, not the holder) were imprecise; counts valid.
- `out/probe-20261012T193547Z.log` (SHA-256 `bf29ff30fd0856e1047eb435db03409ac4165acd7aff62e1315ba54c20f4c3a0`): third run after review round 1, labels corrected, hooks added at `3CCB`, `3CD2`, `3CE7`, `3B82`, `3B86`, `3F99`, `3FA1`; the run F022 cites. Its branch counts equal the second run's. r0001 and r0002 are identical line for line.

## 3. Checks

- 278A's calls by return address equal the task's Evidence in both records (288E 545, 368D 7, 3B35 3, 3F4B 5, 54A1 120, 54F2 120, 5D69 13); the script exits non-zero otherwise.
- The sum of `287C` calls by return address is 545 = the calls at 288E.
- 5B36's entries (14) all return to 61C6; none from 5565 (5649).

## 4. Where static reading was enough and where it was not

The listing gave every rule, element table (data image) and comparison. It could not give how often a branch is taken or which table values the running game holds; the probe's element counts match the data image's values at every reached site.

## 5. Entry counts of 9ED3 and D5C1

Not measured by E022's probe. Their zero entry counts are in `experiments/E021-m0-whole-match/out/t45-reach-contests.log` (lines 12-13, 38-39), made before T45 was written.

## 6. Full test suite

`out/unittest-full-rework1.log`: `python3 -B -m unittest discover -s tests`.
`out/unittest-full-rework1.log`: 900 tests, 1 failure, `test_human_keys.GuardTests.test_scripted_sitting_produces_one_burst_snapshot_per_key_group` (DOSBox-X exited with code -6 during a savestate; unrelated to this PR's files; not the TLS flake). `out/unittest-human-keys-rerun.log`: `python3 -B -m unittest tests.test_human_keys` alone: 70 tests OK.
