#!/bin/sh
# E032: every comparison the plan quotes, re-made on the committed logs with the fail-closed compare.py,
# each with its expected seed family and expectation. It generates nothing, so no stale output can stand in
# for a run (round 2's R1/R2 class); every input must exist and validate (a missing file or a malformed record
# is compare.py's exit 2). Prints every exit code; exits non-zero when a comparison quoted as passing does not
# pass, or when one quoted as a result (removable or not) is malformed (exit 2).
# Usage: sh experiments/E032-match-engine-inventory/recheck.sh
O=experiments/E032-match-engine-inventory/out
C="python3 -B experiments/E032-match-engine-inventory/compare.py"
TWO=0x1234,0x2345
EIGHT=0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719
fail=0
quoted() { echo "== $1 (quoted as passing)"; shift; $C "$@"; rc=$?; echo "exit $rc"; [ $rc -eq 0 ] || fail=1; }
result() { echo "== $1 (a result either way)"; shift; $C "$@"; rc=$?; echo "exit $rc"; [ $rc -le 1 ] || fail=1; }
SKIPS="0791-8F10 0791-9079 0791-0481 0791-1829 0791-0425 0791-0441 0791-94E8 0791-9372"
for stamp in 20261015 review1; do
  for r in $SKIPS; do
    quoted "skip $r ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-$r-$stamp.jsonl --seeds $TWO
  done
  quoted "skip the display set ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-display-set-$stamp.jsonl --seeds $TWO
  result "skip 0791-8537 ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8537-$stamp.jsonl --seeds $TWO
  result "skip 0791-8E24 ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8E24-$stamp.jsonl --seeds $TWO
  quoted "pilot exact, 8 seeds ($stamp)" $O/timing-delay20-8seeds-20261015.jsonl $O/pilot-exact-8seeds-$stamp.jsonl --seeds $EIGHT
  for v in coin-swapped bound-36 no-picture; do
    quoted "falsifier $v caught ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/pilot-$v-$stamp.jsonl --seeds 0x1234 --expect differ
  done
done
quoted "delay count at kick-off, 2 seeds" $O/timing-plain-20261015.jsonl $O/timing-delay20-kickoff-20261015.jsonl --seeds $TWO
quoted "delay count at kick-off, 8 seeds" $O/timing-plain-8seeds-20261015.jsonl $O/timing-delay20-8seeds-20261015.jsonl --seeds $EIGHT
quoted "delay count written at the start, 1 seed" $O/timing-plain-20261015.jsonl $O/timing-delay20-20261015.jsonl --seeds 0x1234
result "skip 8E24 with the display set (20261015)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8E24_0791-9079_0791-0481_0791-1829_0791-0425_0791-0441_0791-94E8-20261015.jsonl --seeds $TWO
quoted "pilot exact, first try" $O/timing-delay20-kickoff-20261015.jsonl $O/pilot-exact-try1-20261015.jsonl --seeds $TWO
echo "recheck exit $fail"
exit $fail
