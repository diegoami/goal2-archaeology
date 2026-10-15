#!/bin/sh
# E032: one skip.py log per candidate display/sound/delay routine, then all the removable ones together, on
# two seeds; each compared with the timing log of the same seeds (delay count 20 at kick-off, nothing
# skipped) by compare.py's fail-closed check. A routine is removable when its comparison exits 0; the
# script prints every exit code and exits 0 only when the joint set is removable (single routines that are
# not removable are a result, not a failure of the batch). (Changed after PR 243's review, R1/R2: the
# 20261015 run used the comparator that compared only the seeds both logs held; the joint set now excludes
# 8537 and 8E24, which that run showed not removable.)
# Usage: sh experiments/E032-match-engine-inventory/skip_batch.sh <stamp>
D=experiments/E032-match-engine-inventory
REF=$D/out/timing-delay20-kickoff-20261015.jsonl
for r in 0791:8537 0791:8E24 0791:8F10 0791:9079 0791:0481 0791:1829 0791:0425 0791:0441 0791:94E8 0791:9372; do
  name=$(echo "$r" | tr ':,' '-_')
  python3 -B $D/skip.py --skip "$r" --seeds 0x1234,0x2345 --log "$D/out/skip-$name-$1.jsonl" > /dev/null
  echo "== skip $r"
  python3 -B $D/compare.py "$REF" "$D/out/skip-$name-$1.jsonl" --seeds 0x1234,0x2345
  echo "exit $? (skip $r)"
done
SET=0791:8F10,0791:9079,0791:0481,0791:1829,0791:0425,0791:0441,0791:94E8,0791:9372
python3 -B $D/skip.py --skip "$SET" --seeds 0x1234,0x2345 --log "$D/out/skip-display-set-$1.jsonl" > /dev/null
echo "== skip the joint set $SET"
python3 -B $D/compare.py "$REF" "$D/out/skip-display-set-$1.jsonl" --seeds 0x1234,0x2345
rc=$?
echo "batch exit $rc"
exit $rc
