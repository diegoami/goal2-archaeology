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
