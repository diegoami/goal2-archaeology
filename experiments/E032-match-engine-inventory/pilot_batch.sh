#!/bin/sh
# E032 pilot: the three falsifiers on one seed (each must be caught: the match differs or does not complete),
# then the exact port on eight more seeds (each must be identical). Every comparison is compare.py's
# fail-closed check with its expected seed family; each prints its exit code, and the script exits non-zero
# when any comparison fails. (Changed after PR 243's review, R1/R2: the 20261015 run used the comparator
# that compared only the seeds both logs held.)
# Usage: sh experiments/E032-match-engine-inventory/pilot_batch.sh <stamp>
D=experiments/E032-match-engine-inventory
EIGHT=0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719
fail=0
for v in coin-swapped bound-36 no-picture; do
  python3 -B $D/pilot_movement.py --seeds 0x1234 --variant "$v" --log "$D/out/pilot-$v-$1.jsonl" > /dev/null
  echo "== falsifier $v"
  python3 -B $D/compare.py $D/out/timing-delay20-kickoff-20261015.jsonl "$D/out/pilot-$v-$1.jsonl" --seeds 0x1234 --expect differ || fail=1
done
python3 -B $D/pilot_movement.py --seeds $EIGHT --log "$D/out/pilot-exact-8seeds-$1.jsonl" > /dev/null
echo "== exact port, eight seeds"
python3 -B $D/compare.py $D/out/timing-delay20-8seeds-20261015.jsonl "$D/out/pilot-exact-8seeds-$1.jsonl" --seeds $EIGHT || fail=1
echo "batch exit $fail"
exit $fail
