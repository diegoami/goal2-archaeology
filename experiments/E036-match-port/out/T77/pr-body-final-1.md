Closes #288

Ports the quick result from a pause and the rare penalty, sending-off, scorer-table and computer-removal paths. All 74 cases match with `quick,rare`, then again with all 21 port modules under the strict display profile. **Milestone: 16 routines reached and exact; C24D remains READ**, with its real first-available/no-candidate body and branch-sensitive units. No impossibility claim is made for that unreached keeper path.

Scope: new `quick.py`/`rare.py` and behavioral tests; R's ten declared start states, immutable raw references and independently recorded original display projection; precise family/comparator tests; 17 annotation rows, regenerated named views and necessary citation moves. The committed generator/source map accounts for all 1,910 instructions (27 immediate CS pushes use the existing far-call mechanism); isolated regeneration reproduces both ports byte-for-byte. Every old 64 scenario digest/raw reference byte and the display prefix is preserved. The DS mask remains empty; every DS block and other protected field remains compared.

The zero-budget competitive quick seed 28 reaches C2A8 and C406 through actual injuries. The bounded original search completes 258 diagnostic executions in under one hour; C24D stays unreached. Per-routine/per-match counts, assumptions and evidence links are in [T77 notes](https://github.com/diegoami/goal2-archaeology/blob/task/T77-port-rare-quick/experiments/E036-match-port/notes/T77.md).

Done-when results, run with Python 3.12:

```text
python3 -B experiments/E036-match-port/out/T77/run_own_2.py
# family.py --family ALL --ports quick,rare, three two-worker shards
# accepted own.jsonl substitute: out/T77/own-2/own.jsonl
python3 -B experiments/E036-match-port/compare.py --family ALL --candidate experiments/E036-match-port/out/T77/own-2/own.jsonl
74 matches expected identical, 74 pass, 0 fail

# family.py --family ALL --ports all, Actions 37 shards
python3 -B experiments/E036-match-port/compare.py --family ALL --candidate experiments/E036-match-port/out/T77/all-actions-1-40090586451/all-actions-1.jsonl --no-screen
74 matches expected identical, 74 pass, 0 fail
2,516 native-entry / physical-entry / Python-call checks agree across both modes

PYTHONPATH=runtime python3 -B -m original_match.check --cache .cache/dl --ports quick,rare
engine PASS; interactive PASS; goals PASS; knockout PASS

# three completed family.py variants, selected declared S/quick-1:
# quick.trial-no-goal; quick.energy-no-decay; quick.stats-no-shot
python3 -B experiments/E036-match-port/out/T77/compare_selected.py experiments/E036-match-port/out/T77/mutant-trial-1.jsonl differ
python3 -B experiments/E036-match-port/out/T77/compare_selected.py experiments/E036-match-port/out/T77/mutant-energy-1.jsonl differ
python3 -B experiments/E036-match-port/out/T77/compare_selected.py experiments/E036-match-port/out/T77/mutant-stats-1.jsonl differ
Each: 1 matches expected differ, 1 pass, 0 fail
Original B261 / DAC1 / D805 reach: 109 / 413 / 5
Fixed actual pre-task 186f08cf + 11 behavioral mutations: all caught

python3 -B -m unittest tests.test_port_quick tests.test_port_rare tests.test_e036_family tests.test_e036_compare
134 tests PASS (all 21 quick/rare tests included)
python3 tools/static/check_annotations.py
PASS; 47 static tests PASS
python3 -B -m unittest discover -s tests -v
2065 tests in 1165.986s; 16 inherited skips; 0 T77 skips; PASS
```

The real GUI burst-snapshot test passes first attempt. Before/after/current/Git source bindings agree; dispatch/current production inputs remain identical. Own1's diagnostic test-fingerprint failure and all rejected/intermediate evidence are preserved; own2 repeats the full family on frozen inputs. The [final acceptance audit](https://github.com/diegoami/goal2-archaeology/blob/task/T77-port-rare-quick/experiments/E036-match-port/out/T77/acceptance-audit-final-1.json) binds the comparisons, controls, references, full validation and cost.

[Actions 40090586451](https://github.com/diegoami/goal2-archaeology/actions/runs/40090586451), dispatch f90dada5, finishes all 39 jobs successfully. Actual intervals total **47,113 runner-seconds = 785.2167 runner-minutes; billable 0ms**. Full jobs/timing/run APIs are retained. Main independently verifies shard 15 and frontier shard 28 ZIP digests, all four strict comparisons, and byte identity with collector records/logs. Integrated candidate SHA-256: `6ce5d83a0c04ef0123bdc84eaa3c7a25578333ca2014194b11de9e90bdeedc3a`.

Docs changed: T77 notes, annotations/named views, and 15 citation moves preserving 200 endpoint texts; 18 inherited citation problems remain unchanged. Current main is integrated. The next step is the independent port-stage milestone; T78 is untouched.
