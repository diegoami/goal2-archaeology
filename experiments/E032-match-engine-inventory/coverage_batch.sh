#!/bin/sh
# E032: coverage of five whole matches (delay count 20 at kick-off), for the union of code reached by a seed
# family. A generator that fails (it refuses an existing output, it crashes) fails the batch (exit 2), so a
# union is never made from a missing or stale run (PR 243 review round 2's class; union.py also refuses
# incomplete runs). Usage: sh experiments/E032-match-engine-inventory/coverage_batch.sh <stamp>
D=experiments/E032-match-engine-inventory
fail=0
for s in 0x1234 0x2345 0x4c1d 0xc3c3 0xe719; do
  python3 -B $D/coverage.py --seed "$s" --delay-count 20 --out "$D/out/cov-d20-$s-$1.json" || { echo "GENERATOR FAILED ($s)"; fail=2; }
done
echo "batch exit $fail"
exit $fail
