#!/bin/sh
# E032 pilot: the three falsifiers on one seed (each must be caught: the match differs or does not complete),
# then the exact port on eight more seeds (each must be identical). Every comparison is compare.py's
# fail-closed check with its expected seed family.
#
# A generator that fails (it refuses an existing output, an import fails, it crashes) makes the batch fail:
# its output is NEVER compared, so a stale log of an earlier run cannot pass (PR 243 review round 2, R1).
# Exit: 0 every generator ran and every comparison passed; 1 a comparison failed its expectation; 2 a
# generator failed or a comparison found a malformed log (the batch measured nothing it can stand on).
# Usage: sh experiments/E032-match-engine-inventory/pilot_batch.sh <stamp>   (a stamp not used before)
D=experiments/E032-match-engine-inventory
O=${E032_OUT:-$D/out}
EIGHT=0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719
infra=0
cmp_fail=0
compare() {
  python3 -B $D/compare.py "$@"
  rc=$?
  echo "compare exit $rc"
  if [ $rc -eq 1 ]; then cmp_fail=1; elif [ $rc -ne 0 ]; then infra=1; fi
}
for v in coin-swapped bound-36 no-picture; do
  echo "== falsifier $v"
  if python3 -B $D/pilot_movement.py --seeds 0x1234 --variant "$v" --log "$O/pilot-$v-$1.jsonl" > /dev/null; then
    compare $D/out/timing-delay20-kickoff-20261015.jsonl "$O/pilot-$v-$1.jsonl" --seeds 0x1234 --expect differ \
      --field "variant=\"$v\"" --field 'ported=["0791:8889", "0791:86D0"]'
  else
    echo "GENERATOR FAILED (falsifier $v): its output is not compared"
    infra=1
  fi
done
echo "== exact port, eight seeds"
if python3 -B $D/pilot_movement.py --seeds $EIGHT --log "$O/pilot-exact-8seeds-$1.jsonl" > /dev/null; then
  compare $D/out/timing-delay20-8seeds-20261015.jsonl "$O/pilot-exact-8seeds-$1.jsonl" --seeds $EIGHT \
    --field 'variant="exact"' --field 'ported=["0791:8889", "0791:86D0"]'
else
  echo "GENERATOR FAILED (exact port): its output is not compared"
  infra=1
fi
if [ $infra -ne 0 ]; then rc=2; elif [ $cmp_fail -ne 0 ]; then rc=1; else rc=0; fi
echo "batch exit $rc"
exit $rc
