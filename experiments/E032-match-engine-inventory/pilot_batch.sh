#!/bin/sh
# E032 pilot: the three falsifiers on one seed (each must differ from the unhooked match), then the exact
# port on eight more seeds (each must be identical). Usage: sh experiments/E032-match-engine-inventory/pilot_batch.sh <stamp>
D=experiments/E032-match-engine-inventory
for v in coin-swapped bound-36 no-picture; do
  python3 -B $D/pilot_movement.py --seeds 0x1234 --variant "$v" --log "$D/out/pilot-$v-$1.jsonl" > /dev/null
  python3 -B $D/compare.py $D/out/timing-delay20-kickoff-20261015.jsonl "$D/out/pilot-$v-$1.jsonl" | sed "s/^/$v: /"
done
python3 -B $D/pilot_movement.py --seeds 0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719 --log "$D/out/pilot-exact-8seeds-$1.jsonl" > /dev/null
python3 -B $D/compare.py $D/out/timing-delay20-8seeds-20261015.jsonl "$D/out/pilot-exact-8seeds-$1.jsonl" | sed "s/^/exact: /"
