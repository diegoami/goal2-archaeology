# Tasks

One file per task, `T<nn>.md`, from [`TEMPLATE.md`](TEMPLATE.md). This index carries no status:
the issue's `status:*` label is the status (`gh issue list --label task --label status:ready`).
Each title ends with the task's plan label (G0, G1, …) from `docs/plan.md` once it
exists.

| Task | Title | Issue | Merge after |
| --- | --- | --- | --- |
| T01 | The GOAL2 research repository: layout, the artifact by hash, the plan (G0) | #1 | — |
| T02 | Runtime feasibility: launch, act, observe, reset GOAL2 under DOSBox-X (G1) | #3 | T01 |
| T03 | The record tools, adapted from toy-archaeology (G2) | #4 | T01 |
| T04 | Static inventory: unpack GOAL.EXE, map its code, propose GOAL.DAT's structure (G3) | #5 | T01 |
| T05 | The documentation map: GOAL.HLP passages as sources (G4) | #6 | T01 |
| T06 | The research backlog: falsifiable questions per area (G5) | #15 | T02, T04, T05 |
| T07 | The G1 driver: launch, act, observe, reset, with run records (G1) | #16 | T02 |
| T08 | Q001: what inputs beyond the start state and the keys does GOAL2 use (G5 Q001) | #21 | T06, T07 |
| T09 | Use game-archaeologist's pinned validator and register_artifact.py (ADR-009) | #22 | T08 |
| T10 | Q002: does the quick result run the same engine as a watched match (G5 Q002) | #26 | T08 |
| T11 | Register the successor of goal2-a949da2f that declares the runtime writes (U21) | #14 | T09 |
| T12 | Q003: do `cycles`, the host speed or wall-clock time change a match (G5 Q003) | #33 | T10 |
| T13 | Savestates as evidence bundles: publish start states to a release (ADR-008) | #37 | T12 |
| T14 | Use game-archaeologist's shared verify_evidence.py and check_citations.py (ADR-009) | #36 | T13 |
| T15 | Q004: where and how are player skills and attributes made (G5 Q004) | #43 | T12, T13 |
| T16 | Q009: which skills the player screen shows, on what scale, from which fields (G5 Q009) | #48 | T15 |
| T17 | Findings pass the pinned citation checker, with no claim changed | #50 | T14 |
| T18 | Decompile GOAL.EXE with Ghidra: pseudo-C per routine, checked against the listing (G3) | #52 | T04 |
| T19 | Q005: what R008 sets, and the continental order of country strength (G5 Q005) | #59 | T18 |
| T20 | The named view: annotations applied to the decompiled GOAL.EXE, improved by each task (G3) | #60 | T18 |
| T21 | F010's fields and routines into the named view's annotations | #66 | T19, T20 |
| T22 | Q007: the squad pool, 100 players and which (G5 Q007) | #67 | T20 |
| T23 | Q010 (quick engine): how strengths and tactics meet in the quick result's contests (G5 Q010) | #68 | T20, T21 |
| T24 | Q010 (quick engine) milestone 2: r0010's divergence, model tests, F012 and the annotations | #75 | T23 |
| T25 | Q010 (watched engine `9564`) milestone 1: the tick map, the Unicorn ground truth and F013 | #81 | T24 |
| T26 | Q011: how performance ratings and the man of the match are computed | 83 | T24 |
| T27 | Q012: where keeping is read (only the keeper), and where penalties are read (only in `A10A`) | 88 | T26 |
| T28 | Q013: how skills change with age, and what is a player's peak age (G5 Q004) | opened at dispatch | T27 |
| T29 | recorder: the owner's playthrough as a complete behavioural record | opened at dispatch | T28 |
