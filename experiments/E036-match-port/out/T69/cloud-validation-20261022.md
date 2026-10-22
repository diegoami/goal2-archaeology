# T69 validation, 2026-10-22 (cloud session and GitHub Actions)

Head: T69 with main merged (T62 #340, T63 #345, T64 #348, #356, #358, #360, #362). Done-when:

1. own: the committed recovered `own-final-20261020.jsonl` re-compared 62/62 identical
   (`compare-own-final-20261020-cloud-20261022.txt`). Integrated `--ports all` (with frame, ball, motion, positioning
   and the earlier ports): Actions run 39771597101 (#361), 31 shards of 2 matches, joined by `shards.py collect`
   (`all-actions-39771597101/`): 62/62 identical (`compare-all-actions-39771597101.txt`), no error record.
2. Falsifiers on O8: clock-reload re-compared 8/8 differ; rating-sign and possession-swapped (the two missing ones) run in
   the cloud session, 8/8 differ each (`compare-falsifier-{rating-sign,possession-swapped}-cloud-20261022.txt`).
3. `check.py --ports frame`: engine, interactive, goals, knockout PASS, on the pre-merge head
   (`check-frame-cloud-20261022.txt`) and on the merged head (`check-frame-merged-20261022.txt`).
4. 14/14 routines: port calls equal the counted entries in every match of own and integrated
   (`count-check-20261022.txt`); test_port_frame 65 OK, check_annotations ok (`focused-checks-20261022.txt`); named view
   regenerated after the merge (`named-cloud-20261022.txt`). Full suite `full-suite-cloud-20261022.txt`: only the
   environment-only non-passes of #354.

Cost of the Actions run: `all-actions-39771597101-cost.json`.
