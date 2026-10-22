# T63 validation in the cloud session (2026-10-22)

Head: T63 with main merged (T62 #340, #356, #358). Done-when:

1. own: the committed `own-rework-cbbfb28.jsonl` (positioning.py sha256 6a8feb43..., unchanged since) re-compared
   62/62 identical (`compare-own-rework-cbbfb28-cloud-20261022.txt`); a fresh cloud own run was stopped at 24/62 to
   free cores (`own-cloud-20261022*`). Integrated `--ports all` (attributes, geometry, motion, pilot, positioning,
   restarts, runtime) after merging main with T62: `all-cloud-20261022-final.jsonl`, 62/62 identical
   (`compare-all-cloud-20261022-final.txt`). It is assembled per match from the completed records of the cloud runs
   (`all-cloud-20261022-final-sources.json`): head and tail shards (59 completed; the container restart is in their
   logs), retakes a and b (S/ko-53-quick, S/ko-42-sudden-death), retake c with `--stretch-limit 600` (S/ko-9-quick).
   The three first attempts, and S/ko-9-quick's first retake, stopped on the kit's fixed 60 s watchdog per stretch
   (a wall-clock limit; a retake stopped at another address): #357, fixed by #358. Those records stay in their files.
2. Falsifiers: the committed `falsifier-final-{depth-plus-one,marking-no-copy,keeper-no-state}-F40.jsonl` re-compared,
   40/40 differ each.
3. 16/16 routines: port calls equal the counted entries in every match of both runs (`count-check-cloud-20261022.txt`).
4. test_port_positioning, check_annotations, citations: `focused-checks-cloud-20261022*.txt`; named view regenerated
   after the merge (`named-cloud-20261022.txt`). Full suite `full-suite-cloud-20261022.txt`: 1624 tests, the 24
   environment-only non-passes of #354 and none other (test_driver_terminate's failure here was "no DOSBox-X window
   within 15 s" under load; its retake passes, `full-suite-cloud-20261022-retake-terminate.txt`).
