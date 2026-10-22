# T64 validation, 2026-10-22 (cloud session and GitHub Actions)

Head: T64 with main merged (T62 #340, T63 #345, #356, #358, #360, #362). Done-when:

1. own: the committed `own.jsonl` (ball port unchanged since) re-compared 62/62 identical
   (`compare-own-cloud-20261022.txt`). Integrated `--ports all` (attributes, ball, geometry, motion, pilot, positioning,
   restarts, runtime) after merging main with T62 and T63: Actions run 39760200442 (#361), 31 shards of 2 matches on
   ubuntu-latest, joined by `shards.py collect` (`all-actions-39760200442/`, manifest and every shard's log there):
   62/62 identical (`compare-all-actions-39760200442.txt`), no error record. A first integrated run in the cloud session
   (`all-cloud-20261022-{a,b}*`, interrupted by a container restart and then stopped for the Actions run) holds 8 records.
2. Falsifiers: launch-reverse-x and pass-always-replace re-compared, 40/40 differ each; shot-skip-jitter completed in the
   cloud (32 missing cases), 40/40 differ (`compare-falsifier-shot-skip-jitter-cloud-20261021.txt`).
3. 21/21 routines: port calls equal the counted entries in every match of own and integrated (`count-check-20261022.txt`).
4. test_port_ball 33 OK, check_annotations ok (`focused-checks-20261022.txt`); named view regenerated after the merge
   (`named-cloud-20261022.txt`). Full suite `full-suite-cloud-20261022.txt`: only the environment-only non-passes of #354.

Cost of the Actions run: `all-actions-39760200442-cost.json` (runner minutes; billable 0 on a public repository).
