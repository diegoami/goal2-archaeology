#!/bin/sh
# E032: every comparison the plan quotes, re-made on the committed logs with the fail-closed compare.py,
# each with its expected seed family, its expectation and the run its candidate must be (--field: the
# skipped routines, the pilot's variant and ported routines, the delay count). It generates nothing, so no
# stale output can stand in for a run; every input must exist and validate (a missing file or a malformed
# record is compare.py's exit 2). Prints every exit code; exits non-zero when a comparison quoted as passing
# does not pass, or when one quoted as a result (removable or not) is malformed (exit 2).
# Usage: sh experiments/E032-match-engine-inventory/recheck.sh
O=experiments/E032-match-engine-inventory/out
C="python3 -B experiments/E032-match-engine-inventory/compare.py"
TWO=0x1234,0x2345
EIGHT=0x0101,0x2b7e,0x4c1d,0x6a33,0x8e05,0xa1f0,0xc3c3,0xe719
PORTED='ported=["0791:8889", "0791:86D0"]'
fail=0
quoted() { echo "== $1 (quoted as passing)"; shift; $C "$@"; rc=$?; echo "exit $rc"; [ $rc -eq 0 ] || fail=1; }
result() { echo "== $1 (a result either way)"; shift; $C "$@"; rc=$?; echo "exit $rc"; [ $rc -le 1 ] || fail=1; }
skips() { echo "$1" | sed 's/[^,]*/"&"/g; s/^/[/; s/$/]/'; }
SET7=0791:8F10,0791:9079,0791:0481,0791:1829,0791:0425,0791:0441,0791:94E8
SET8=$SET7,0791:9372
for stamp in 20261015 review1 review2 review3 review4; do
  [ -f $O/pilot-batch-$stamp.txt ] || continue        # a stamp whose batches were not run
  for r in 0791:8F10 0791:9079 0791:0481 0791:1829 0791:0425 0791:0441 0791:94E8 0791:9372; do
    f=$O/skip-$(echo $r | tr ':' '-')-$stamp.jsonl
    quoted "skip $r ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $f --seeds $TWO --field "skipped=$(skips $r)"
  done
  set=$SET8
  [ $stamp = 20261015 ] && set=$SET7
  quoted "skip the display set ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-display-set-$stamp.jsonl --seeds $TWO --field "skipped=$(skips $set)"
  result "skip 0791:8537 ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8537-$stamp.jsonl --seeds $TWO --field 'skipped=["0791:8537"]'
  result "skip 0791:8E24 ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8E24-$stamp.jsonl --seeds $TWO --field 'skipped=["0791:8E24"]'
  quoted "pilot exact, 8 seeds ($stamp)" $O/timing-delay20-8seeds-20261015.jsonl $O/pilot-exact-8seeds-$stamp.jsonl --seeds $EIGHT --field 'variant="exact"' --field "$PORTED"
  for v in coin-swapped bound-36 no-picture; do
    quoted "falsifier $v caught ($stamp)" $O/timing-delay20-kickoff-20261015.jsonl $O/pilot-$v-$stamp.jsonl --seeds 0x1234 --expect differ --field "variant=\"$v\"" --field "$PORTED"
  done
done
quoted "delay count at kick-off, 2 seeds" $O/timing-plain-20261015.jsonl $O/timing-delay20-kickoff-20261015.jsonl --seeds $TWO --field delay_count=20
quoted "delay count at kick-off, 8 seeds" $O/timing-plain-8seeds-20261015.jsonl $O/timing-delay20-8seeds-20261015.jsonl --seeds $EIGHT --field delay_count=20
quoted "delay count written at the start, 1 seed" $O/timing-plain-20261015.jsonl $O/timing-delay20-20261015.jsonl --seeds 0x1234 --field delay_count=20
result "skip 8E24 with the display set (20261015)" $O/timing-delay20-kickoff-20261015.jsonl $O/skip-0791-8E24_0791-9079_0791-0481_0791-1829_0791-0425_0791-0441_0791-94E8-20261015.jsonl --seeds $TWO --field "skipped=$(skips 0791:8E24,0791:9079,0791:0481,0791:1829,0791:0425,0791:0441,0791:94E8)"
quoted "pilot exact, first try" $O/timing-delay20-kickoff-20261015.jsonl $O/pilot-exact-try1-20261015.jsonl --seeds $TWO --field 'variant="exact"' --field "$PORTED"
echo "recheck exit $fail"
exit $fail
