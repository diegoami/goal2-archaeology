# E017 energy comparisons

Run `python3 experiments/E017-q015-energy/check_energy.py` from the repository
root. Comparisons use player words and all three final bytes, never player names.
Empty comparison sets fail.

## Superseded by, and why

The machine-readable declaration is `supersessions.json` in this directory.
Each entry names the defect: `differs_only_in` (the case and operation fields the missing input
concerns) and `fails_alone_with` (the error the superseded record raises on its own). The
checker omits a record only when Done-when 1's conditions hold (review round 1 R1): both records
exist; the successor is not itself superseded and comes later; it holds the same cases, identical
outside the declared fields; and the superseded record really is incomplete — at least one of its
cases fails alone, and every failure is the declared one. Anything else is a failure, never a
silent omission. It prints each superseded record and its reason, and checks every comparison in
all remaining records. Original captures remain unchanged. Tests: `tests/test_model_energy.py`
`Supersession` (an unrelated successor, a complete record, an earlier successor, a difference
outside the fields, fewer cases, a different failure, a missing successor — each rejected).

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

That sweep tried +1 only, and missed REST_THRESHOLD 16 -> 15 (review round 1 R2): no test
reached the intermediate value 15 below the `jge 0x10` at 1771:36D7. `mutations-003.log` is the
sweep after the review: every constant by +1 AND -1, plus the review's operator mutants (the
watched and quick floors made unsigned or `>=`, review R3; the draw lower bound 1 -> 0, R4):
**37/37 killed**, with the new literal tests (intermediate 15; energy 1/128/255 at the watched
step's edge; a draw of 0).

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
