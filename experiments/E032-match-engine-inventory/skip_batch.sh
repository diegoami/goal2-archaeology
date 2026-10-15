#!/bin/sh
# E032: one skip.py log per candidate display/sound/delay routine, then all of them together, on two seeds;
# each compared with the timing log of the same seeds (delay count 20 at kick-off, nothing skipped).
# Usage: sh experiments/E032-match-engine-inventory/skip_batch.sh <stamp>
D=experiments/E032-match-engine-inventory
REF=$D/out/timing-delay20-kickoff-20261015.jsonl
for r in 0791:8537 0791:8E24 0791:8F10 0791:9079 0791:0481 0791:1829 0791:0425 0791:0441 0791:94E8 \
         0791:8E24,0791:9079,0791:0481,0791:1829,0791:0425,0791:0441,0791:94E8; do
  name=$(echo "$r" | tr ':,' '-_')
  python3 -B $D/skip.py --skip "$r" --seeds 0x1234,0x2345 --log "$D/out/skip-$name-$1.jsonl"
  python3 -B $D/compare.py "$REF" "$D/out/skip-$name-$1.jsonl" | sed "s|^|$r: |"
done
