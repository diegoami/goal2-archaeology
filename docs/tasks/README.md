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
