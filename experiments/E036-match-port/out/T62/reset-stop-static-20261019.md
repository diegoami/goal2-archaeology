# Completed-tick reset candidates: static progress for #336

This is a **proposed, static-only working report**, folded into T62's existing
reading. It is not a reviewed finding, a complete answer to #336, a runtime
classifier or a claim that any supplied seed exercises every restart class.
T67's complete restart/caller audit and the requested bounded corroboration
remain outstanding. No new game run or downstream presentation work was started.

## Pins and method

The requested kit pin is `424d5998076da1e4efc399c2715689ddb44d3e1a`.
The read checkout is approved archaeology main
`53d7ef5ec445aebc5f20d053f05d1db008db771e`. The adjacent JSON records
SHA256s for all 24 segment-0791 raw listing files and verifies their bytes are
identical at the requested pin. It also hashes the requested pin's entire
`runtime/original_match/match.py` and retains its `_on_tick` function.

Read the named view first: `2929`, `65A4`, `69BD`, `6BF1`, `6E11`, `6E6E`,
`6F01`, `6F3E`, `83A2`, `97D0`, `983F`, `998C`, `9A32` and `A2E6` in
`static/goal-exe/named/seg_0791_02.c`, `_05.c`, `_06.c`, `_07.c`, `_08.c`.
The raw assembly decides the claims below; named routine labels do not establish
the meaning or observability of a candidate. Read the actual sampling callback
at the requested kit pin, rather than assuming a frame boundary from its name.

The adjacent method inventories 45 **direct literal `mov` writes to five selected
globals** across the segment-0791 listing. It is deliberately not an exhaustive
write analysis: indirect stores, other write instructions and other globals can
matter. Each retained row names the containing routine, exact instruction,
listing path/line and value expression. No runtime code is imported or changed.

## What the completed-tick stop means here

Static-only: the kit hooks `0791:970C` at entry. `_on_tick` flushes pending events,
optionally emits a tick with the current subtick and stops when events are queued.
In the watched tick loop, assembly `0791:97D0` calls the player/ball sweep at
`980B`, tracks the offside line at `9815`, moves the referee at `9821`, and then
calls the clock at `9825`. The sampling callback therefore occurs after that
sweep, before the clock routine's body runs. A menu/decision stop inside the sweep
is a different stop; it is not a completed tick.

The same loop consumes snapshot/replay requests before the sweep. In particular,
`9801` clears `DS:9B55`, and `9806` clears `DS:7C37`. A request raised during the
sweep may consequently be present at its following tick stop, but an earlier
request can already have been consumed. This static ordering is not a guarantee
that a particular candidate survives every relevant path to a stop.

## Candidate constraints established by the reads

| Candidate | Exact static path | Consequence and remaining limit |
| --- | --- | --- |
| `DS:9B55` snapshot request | `983F:986A` sets it before entering the tick loop; `97D0:9801` clears it before the first sweep. `6BF1:6C2B` conditionally sets it; `C5DC:C7E0` sets it after a substitution-related update; `ED8A:F004` also writes it. | The setup write alone does not survive to the first completed tick. Multiple writers preclude treating a nonzero byte as a unique goal, kickoff or halftime tag without a fuller path/observation proof. |
| `DS:9B41` menu/control flag | `9A32:9A90` sets it in the pre-half sequence, but `8062:80DB` also sets it before a substitution/menu path and `8062:8103` clears it afterward. `983F:9845` clears it before running the half. | It is not a unique halftime predicate, and a menu-time value need not survive to the subsequent completed tick. |
| `DS:8302` launch/ball-control flag | `6BF1:6C0A` and `34C1:34D5` set it. `69BD:6A92` clears it at the kickoff-placement transition, but ordinary possession routine `869F:86BB` clears it too. `983F:9865` clears it before the half loop. | Neither the value nor an observed clear alone identifies a positional reset. The named handlers and their callers matter. |
| `DS:8325` play/control flag | Out-of-bounds handling `83A2:8483` clears it before dispatching the restart. `65FE:6604` sets it; ball helper `333F:334C` also sets it. `983F:98B6` and `9955:9958` clear it. | Several classes share writes. Presence at a sampling stop, and separation of ordinary play from each restart class, remain unproved. |
| `DS:7C39` | `698E:69B1` sets it before calling `690C`; setup `A4A1:A573` clears it, as do other direct writers retained in the JSON. | This is a candidate input to a goal-related path, not an established fresh-per-tick reset event. Its complete lifetime and consumers are not yet audited. |
| Pitch record state `+0x12` | `2929:2946` fills all 22 state bytes with its argument. `983F:985F` calls it with 1. `6BF1:6C18` calls the same helper with a restart-state argument. | Filling state bytes is not itself a write of all coordinates or evidence that all players reset at a sampled boundary. Do not equate a movement-handler state with a reset event. |
| Pitch identity/coordinate initialization | `A2E6:A2F2` binds a player through `A260`; `A2FB` writes the current coordinate word from `DS:0644`, and `A307` copies it to the previous-coordinate word. The routine also resets direction/activity fields. | Identity rebinding can accompany coordinate initialization. A reliable report must separate this path from ordinary movement and whole-pitch repositioning rather than classify distance alone. |

## Restart dispatch, not a reset predicate

Static-only: T62's `83A2` out-of-bounds path clears `830C`, `830A`, `830D` and
`8325` at `8474`–`8483`, then dispatches by the ball's position and holder-side
direction. The explicit guest-call returns in T62 identify the paths: `698E`
or `690C` at `84C1`/`84C6`, throw-in `6E11` at `84DE`, corner `6E6E` at `850A`,
or `6F01` at `8520`. On the common tail, `8528` clears the ball timer and `852C`
clears `8327`. The earlier `830E` branch can instead return through `82EB`.
These are proved instruction paths, not a demonstration that their distinguishing
inputs remain visible when the later tick callback fires.

For example, `6E11` and `6E6E` both clear `830E`, call substitution checking and
choose a restart; `6F01` distinguishes its printed goal-kick/free-kick message
using arguments. Caller arguments and intermediate program counters are not
automatically durable fields of the completed-tick sample. This report does not
guess replacements for them. Existing commentary/score events may help correlate
some cases, but their sufficiency for every requested boundary is unproved here.

## What remains before answering downstream

1. Complete T67's write/caller audit for each kickoff, goal, out-of-play/set-piece
   and halftime path; distinguish actual coordinate writes from destination or
   state changes and pitch-player rebinding. Extend the selected writer inventory
   where indirect stores and other instructions matter.
2. Trace every proposed predicate through the remainder of the sweep to the
   actual `970C` entry. State whether it is persistent, overwritten, consumed
   before the sample, or ambiguous with ordinary play.
3. Only if needed after that reading, corroborate with a bounded diagnostic that
   demonstrates separate initial kickoff, halftime and goal/out-of-play coverage.
   Reuse the requested fixture/seeds where applicable without assuming coverage;
   preserve before/after records, inputs and unchanged outcomes/memory/RNG.
4. Obtain independent review before linking a result or negative finding as the
   answer to #336. No original assets or downstream vendored changes are needed.

The current downstream assumption remains **no proved complete reset/restart
classifier at these stops**. Retain discrete samples and their observed
discontinuities. This static progress neither authorizes interpolation nor delays
the route-C port acceptance work.
