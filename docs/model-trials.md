# Model trials

How each reviewer and implementer model did on this project's tasks, one row per review or run that
taught something. Used with game-archaeologist `docs/models.md` when routing; it records outcomes, not
task status.

| Date | Task / PR | Role | Model | What happened | Lesson |
| --- | --- | --- | --- | --- | --- |
| 2026-10-04 | T06 / #17 | reviewer | zai-glm-5.3 | Round 1: found a static route searching an empty caller set (R1, blocking) and a wrong "once per launch" lead (R2, proven from the listing, rated non-blocking); round 2 verified the fixes | thorough on evidence; R2 was a factual error in the deliverable and arguably blocking |
| 2026-10-04 | T07 / #18 | reviewer | zai-glm-5.3 | Approved with R1 (an edge comment with no test, rule 10) and R2 (timeouts without a source note), both non-blocking; ran 10 live cycles itself | under the "Blocking means" rule (L47, adopted 2026-10-04) R1 would be blocking (project item: edge comment without a test); not a bypass of what T07 protects, so merged; fixed in #20 |
| 2026-10-04 | T07 / #18 | implementer | claude opus | Met 6 of 7 Done-when lines; one aborted record under early code; 144k tokens, 27 min | stopped and reported correctly on the failing line |
