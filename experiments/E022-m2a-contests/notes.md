# E022 m2a-contests — notes (T45, milestone M2a)

Addresses are `segment:offset` (image paragraphs); listings are `static/goal-exe/code/seg_0791_*.asm`. Append-only.

## 1. What was run

`python3 experiments/E022-m2a-contests/probe.py` replays E011-r0001 and E011-r0002 from their watchstart savestates (E021's `WatchedMatch`, unhooked) with code hooks that only read. About 4 minutes. Each hook address is checked to be an instruction start of the listing before the run; the log prints the listing line beside every branch hook.

## 2. Logs (never overwritten)

- `out/probe-20261012T185044Z.log` (SHA-256 `eec1cc38df6a7d993a8eac3bf30368839e3ddb859a452c74e288ce9da461ea8d`): first run. Counts are valid. Three labels were wrong: `5613` (reached from many early exits, not "287C returned 0": 69352), `5616` (also reached by 55FC's `jle` when the product is 0 or below) and `5D99`. It lacks the per-element result table.
- `out/probe-20261012T185316Z.log` (SHA-256 `7aa08112c096cc0b347748b9c3a4683670cf4fb42a3019bd9434639da223ebde`): the run F022 cites. r0001 and r0002 are identical line for line.

## 3. Checks

- 278A's calls by return address equal the task's Evidence in both records (288E 545, 368D 7, 3B35 3, 3F4B 5, 54A1 120, 54F2 120, 5D69 13); the script exits non-zero otherwise.
- The sum of `287C` calls by return address is 545 = the calls at 288E.
- 5B36's entries (14) all return to 61C6; none from 5565 (5649).

## 4. Where static reading was enough and where it was not

The listing gave every rule, element table (data image) and comparison. It could not give how often a branch is taken or which table values the running game holds; the probe's element counts match the data image's values at every reached site.
