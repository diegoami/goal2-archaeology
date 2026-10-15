#!/bin/sh
# E032: every comparison the plan quotes, re-made on the committed 20261015 logs with the fail-closed
# compare.py (PR 243's review, R1/R2), each with its expected seed family and expectation. Prints every
# exit code; exits non-zero when a comparison the plan quotes as passing does not pass.
# Usage: sh experiments/E032-match-engine-inventory/recheck.sh
O=experiments/E032-match-engine-inventory/out
C="python3 -B experiments/E032-match-engine-inventory/compare.py"
TWO=0x1234,0x2345
EIGHT=0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719
fail=0
quoted() { echo "== $1 (quoted as passing)"; shift; $C "$@"; rc=$?; echo "exit $rc"; [ $rc -eq 0 ] || fail=1; }
result() { echo "== $1 (a result either way)"; shift; $C "$@"; echo "exit $?"; }
quoted "delay count at kick-off, 2 seeds" $O/timing-plain-20261015.jsonl $O/timing-delay20-kickoff-20261015.jsonl --seeds $TWO
quoted "delay count at kick-off, 8 seeds" $O/timing-plain-8seeds-20261015.jsonl $O/timing-delay20-8seeds-20261015.jsonl --seeds $EIGHT
quoted "delay count written at the start, 1 seed" $O/timing-plain-20261015.jsonl $O/timing-delay20-20261015.jsonl --seeds 0x1234
for r in 0791-8F10 0791-9079 0791-0481 0791-1829 0791-0425 0791-0441 0791-94E8 0791-9372; do
  quoted "skip $r" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-$r-20261015.jsonl --seeds $TWO
done
quoted "skip the display set" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-display-set-20261015.jsonl --seeds $TWO
result "skip 0791-8537" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8537-20261015.jsonl --seeds $TWO
result "skip 0791-8E24" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8E24-20261015.jsonl --seeds $TWO
result "skip 8E24 with the display set" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8E24_0791-9079_0791-0481_0791-1829_0791-0425_0791-0441_0791-94E8-20261015.jsonl --seeds $TWO
quoted "pilot exact, first try" $O/timing-delay20-kickoff-20261015.jsonl $O/pilot-exact-try1-20261015.jsonl --seeds $TWO
quoted "pilot exact, 8 seeds" $O/timing-delay20-8seeds-20261015.jsonl $O/pilot-exact-8seeds-20261015.jsonl --seeds $EIGHT
for v in coin-swapped bound-36 no-picture; do
  quoted "falsifier $v caught" $O/timing-delay20-kickoff-20261015.jsonl $O/pilot-$v-20261015.jsonl --seeds 0x1234 --expect differ
done
echo "recheck exit $fail"
exit $fail
