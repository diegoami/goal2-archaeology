# Brief: a plan to recreate the real match engine (not the quick result)

For an Opus agent at high effort. Written 2026-10-15 at the owner's request. This brief asks for a **plan**,
not for the engine: the deliverable is `docs/match-engine-plan.md`, plus a small pilot that prices the plan.

## The goal, in the owner's words

"The point is to understand how players behave and play based on their skills, form and tactics, and
replicate the match engine": the **watched match** engine (`0791:9564` and its loop), not the quick result
(`0791:D733`, already modelled seed-exactly, F012). The remaster (repository `goal2`) will play matches with a
model built from our findings. It must be **practical**: the owner rejects long sessions and proofs that cost
more than they are worth (L113, `docs/wide-pass.md` "Grading the unknowns"). Decisions about the remaster are
goal2's; this repository explores the original and delivers findings and models (L112).

Success is the rebuild's own acceptance test, **G-M4** (`docs/plan.md`): on matched start states the model's
distributions (goals, shots, possession, fouls, bookings, injuries) agree with the original's within stated
tolerances over a stated n. Tick-exact replay (M0-M2 of `docs/plan.md`) is the stricter route; the owner
accepts distribution-level fidelity where an exact proof is expensive.

## What already exists (read it first; do not redo it)

- The plan's ladder M0-M6 in `docs/plan.md` ("the watched engine"); M0 (whole matches, a substitution hook),
  M1 (skill reader `278A`, strength `377E`), M2 (contests `287C`, `5474`, `5D69`, the draw wrappers, the long
  helpers: T43-T48) are done and exact.
- Findings: F005 (the quick result is another engine), F006 (cycles and host speed do not change a match, so a
  match can run at `cycles=max`), F010 (R008 and the 8 team tactics), F012 (the quick engine), F013 (the
  watched engine's tick map), F014 (performance ratings), F015 (keeper and penalties), F018-F021 (energy,
  confidence, morale; energy and form set strength, fitness is never read), F022 (contest sites), F024 (the
  computer's lineup), F026 (what each team tactic changes), F027 (discipline, substitutions, added time),
  F028 (formations, positions, out-of-position cost), F029 (a substitution persists), F030 (prompts).
- Spec rows `spec/match-engine.md`, `spec/tactics.md`, `spec/discipline.md`; the backlog `docs/backlog.md`.
- Tools: the driver (`runtime/driver/`: launch, keys, screen read, savestates, memory pokes declared as I3
  interventions), the Unicorn harness `runtime/emul/watched.py` (the original's second half emulated from
  half-time states), the models `runtime/model/*.py` with tests, the named static view
  `static/goal-exe/named/`, run records `runs/E0xx`. Static first (CLAUDE.md rule 22).
- The owner's sittings are NOT a source of work: the driver plays by itself.

## What to produce: `docs/match-engine-plan.md`

1. **A model of how a player acts**, as far as the findings and a short reading give it: per tick, what each
   player's decision depends on: the 12 derived skills, form and energy (F021), morale/confidence, the team
   tactics (8 bits), the player's own tactic bits, marking, the formation and positions, the ball's state and
   the opponents. A diagram or table of the decision structure with each edge marked `known (finding)`,
   `read (listing, not run)` or `unknown`.
2. **The unknowns, graded** exactly as `docs/wide-pass.md` says: importance (H/M/L to the remaster) and cost
   to evaluate (S/M/L) and the decision (investigate / assume / drop). An unknown whose only evidence is a
   long run becomes an assumption now. Say which assumptions you would make and their risk.
3. **A ladder of milestones** from here to a model that passes G-M4, replacing or extending M3-M6: each with
   its exit check (a statistical check over n seeded matches with the tolerance stated, not an eyeballed one),
   its inputs, its cost in agent-hours and wall time, and the order (what blocks what). Mark what stays
   tick-exact (M0-M2) and what is validated at distribution level.
4. **Sensitivity experiments on the original** (the behavioural route, cheap because a match runs unattended
   at `cycles=max`): designs that vary one input at a time through the driver (a skill byte, form/energy, one
   tactic bit, formation, marking, the seed) from a fixed kick-off or half-time state, run N matches, and
   measure goals, shots, possession, fouls, cards. For each: the bytes poked (the offsets from F008/F010/F028),
   N, the expected wall time, and what the result says about the decision structure. Prefer designs that
   isolate an effect in a few hundred matches, not thousands.
5. **Where the model lives and how it is validated**: models in `runtime/model/` with tests (a test proves
   behaviour only if it fails without it, rule 9); the validation harness (seeded batch vs the original,
   the statistical test and tolerance); how goal2 vendors it (goal2's `PROVENANCE.md`, state adapter).
6. **A work breakdown** into tasks `T<nn>` the main session can file, with size, kind (research or build),
   suggested model tier, reviewer family, and dependencies. At most 12 tasks for the first stage; later stages
   as one line each.
7. **Risks and the cheap exits**: what would make the plan too expensive, and the fallback (a coarser model
   plus an assumption) for each.

## The pilot (at most 2 hours; it prices the plan)

Run the driver on the original and report real numbers: wall time to play one full watched match unattended
at `cycles=max` from a kick-off state, matches per hour on this machine (single and parallel on private
displays; the machine has about 14 GB free and one shared CPU), whether a fixed seed and fixed inputs give the
same result every time, and the cost of poking one skill byte and re-running. Commit the logs under
`experiments/E031-engine-pilot/out/` (L40: tracked, never deleted). Do not make claims the pilot does not
support.

## Constraints

- Practicality first (L113). Nothing here requires a session of the owner, years of game time, or a proof
  per routine unless the plan says why that routine decides what the player sees.
- Static first (rule 22); a run only when static reading cannot answer, or cheaply corroborates (rule 19).
- Never commit anything of the original (CLAUDE.md rule 18): derived tables under `static/` only.
- Work in a worktree on branch `docs/match-engine-plan`; commit and push after each step; open a draft PR,
  mark it ready when done. Do not merge. Wait for jobs inside a tool call; never end a turn to wait (L110).
- Keep each file you write under about 20k tokens; use tables.
- Report: the plan's path, the pilot's numbers, the three biggest uncertainties, and the first task you would
  start.
