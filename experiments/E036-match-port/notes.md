# E036 the match port: notes and provenance

Route C of [`docs/match-engine-plan.md`](../../docs/match-engine-plan.md): the watched engine translated from the listing into
Python, memory-faithful, plugged into the original-match kit (`runtime/original_match/`, issues 250 and 252) in place of the
original's routines through the same hooks, and accepted when whole matches stay identical draw for draw. The end state is a
pure-Python engine that equals the original over the seed families with no GOAL.EXE bytes needed at run time (the owner's
decision, restated in the brief of 2026-10-17). The work is the backlog `docs/tasks/T57.md` to `T80.md`; this page holds no
status (the issues' labels do).

## Layout

- The ports: `runtime/original_match/port/`, one module per task (vendored with the kit, standard library only, no byte of
  the original). Each module registers its own ports, so tasks that run at the same time own different files.
- The scripts of this experiment (T57, T59): `family.py` (run a family through the kit, with or without ports), `compare.py`
  (fail closed), `locate.py` (the first differing minute, then the first differing call), the family definitions.
- Each task's outputs: `out/T<nn>/`, never deleted or overwritten; each task's notes: `notes/T<nn>.md`.
- Records hold counts and digests only: no commentary text, no player name, no byte of the image (rule 18).

## The acceptance rule every porting task uses

A porting task is accepted when, with its ports hooked, every match of the families equals the unhooked reference that T57
commits (score, ticks, every main-RNG draw by its digest and per minute, the board, the commentary's templates, the result,
the events, the records after the post-match update), and the same holds with every port merged on `main`; and when each of
three falsifiers (a one-line mutation of a ported routine on a branch the families reach, the reach counted first, L105)
changes or stops a match. A routine that stays non-exact after an hour of locating is accepted non-exact with its
divergence recorded (the plan's one-hour rule); two such in one task go to the main session.

The families (T57; T77 adds R): F40 (the reference fixture, Denmark v country 19 at calendar number 21 from E006-r0001: 20
seeds as they are and the same 20 with declared edits), O8 (other country pairs), S (the kit's scenarios from E033 and E034:
decisions at pauses and half time, an injury, sendings off, quick results, extra time, shoot-outs with sudden death, a
qualifier), R (states that reach the frontier). ALL is their union.

## The sizes of the backlog (static, no run)

`sizes.py` assigns every routine of the static call closure of run_match `0791:F1F6` and the post-match update `0791:B7FA`
(what the kit runs as the original's code) to one task or to OUT with a reason, and fails on any routine left over; it
counts each task's static instructions (`static/goal-exe/routines.tsv`) and turns them into hours at the plan's three rates
of the E032 pilot's pace, with every other figure a named assumption. E032's six coverage runs say which routines a match
reaches between kick-off and full time.

- `out/backlog/sizes-20261017.md` and `.json` (2026-10-17, from `c7e1969`): 540 routines, 37,618 static instructions in the
  universe; 442 routines (33,299 instructions) in 24 tasks, 98 (4,319) OUT; 0 problems. SHA-256
  `099228de86c7383b97e6e509c74807923e25588e079fa4791b1fda80f5102d3d` (`.md`),
  `c7d92f4f4915e8fc8d032864ac3eb48564d2eeb7a40e89a52a648c3e351b0099` (`.json`).

What the sizing found that the plan did not count:
- The plan's steps call each other's routines (for example `2AA3` calls `emit_commentary 1EB5`, `move_ball 83A2` calls the
  dead-ball routines and `82EB`, `dead_ball_throw_in 6E11` calls `check_substitutions 8062`, which opens the team menu), so
  a port must be able to call a routine that is still the original's (T59).
- The kit runs more than kick-off to full time: the set-up's own callees (`2648`, the computer's lineup `B11F` and its
  helpers, the sorts), run_match's tail (`CAB0`, `CB7D`, `update_group_tables 1771:8757`, `D050`, `BC5D`), the post-match
  update `B7FA` and `BA4E`, the menus and prompts a decision goes through, and the quick result `D733` from a pause.
- Runtime routines the engine calls beyond the RNG, sets and longs: min and max, clamps, fills, moves, Pascal strings
  (Turbo Pascal 5.5's, E035).
- The pitch picture `[DS:7C16]` is engine state (E032 notes, "Why 8537 and 8E24 stay"); every write to it stays, whatever
  routine makes it.
