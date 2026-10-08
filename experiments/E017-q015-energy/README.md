# E017 energy comparisons

Run `python3 experiments/E017-q015-energy/check_energy.py` from the repository
root. Comparisons use player words and all three final bytes, never player names.
Empty comparison sets fail.

## Superseded by, and why

The machine-readable declaration is `supersessions.json` in this directory.
The checker validates that both named records exist and that the successor is
not itself superseded, prints each superseded record and its reason, and checks
every comparison in all remaining records. Original captures remain unchanged.

| Record | Superseded by | Why |
| --- | --- | --- |
| `records/recovery-001.json` | `records/recovery-002.json` | Missing healing draw: 214B:06D0 calls 0688 directly, bypassing the initial 06B1 hook (`static/goal-exe/code/seg_214B_01.asm:913–935`). The repeat captures the draw at 0688 for the same cases. |

## Constant sensitivity (DW2)

`mutate_energy.py` edits the real `runtime/model/energy.py` once per declared
numeric constant, clears its bytecode, runs the named unittest module with a
30-second timeout, and restores the original in a `finally`. Supply a new
in-worktree log filename; existing measurements cannot be overwritten.

The immutable `mutations-001.log` records 14/16 kills: increasing REST_DRAW and
HEAL_DRAW from 3 to 4 survived. Two literal out-of-range transcript tests were
added. `mutations-002.log` records the new tests **failing on those in-place
mutants**, then passing with the original listing constants restored; all
16 declared constants kill. The model itself was not changed to accommodate
the tests. Each log includes the exact failing tests, not just a kill count.

| Constant | In-place change | Result in mutations-002.log |
| --- | --- | --- |
| RECORD_SIZE | 20 -> 21 | killed |
| FORM | 12 -> 13 | killed |
| FITNESS | 13 -> 14 | killed |
| ENERGY | 14 -> 15 | killed |
| QUICK_PERIOD | 5 -> 6 | killed |
| ACTIVITY_THRESHOLD | 180 -> 181 | killed |
| DECREMENT | 1 -> 2 | killed |
| FLOOR | 1 -> 2 | killed |
| REST_THRESHOLD | 16 -> 17 | killed |
| REST_BONUS | 1 -> 2 | killed |
| AGE_MARGIN | 3 -> 4 | killed |
| SMALL_DRAW | 2 -> 3 | killed |
| LARGE_DRAW | 8 -> 9 | killed |
| REST_DRAW | 3 -> 4 | killed (new literal rest-bound test) |
| HEAL_DRAW | 3 -> 4 | killed (new literal healing-bound test) |
| FORM_MAX | 255 -> 256 | killed |

## Annotation regression proof

`annotations-red-001.log` records the two F018 annotation tests against the
pre-annotation TSVs from commit `2948249`: the routine test fails for the absent
or non-F018-backed rows, and the field test fails because fitness, energy and
activity are still `likely`. Both pass against the new TSVs. These tests check
the annotations, not generated `named/`; generation is the main session's
`decompile.sh --annotations` line under L57.
