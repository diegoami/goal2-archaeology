#!/bin/sh
# E032: one skip.py log per candidate display/sound/delay routine, then the removable ones together, on two
# seeds; each compared with the timing log of the same seeds (delay count 20 at kick-off, nothing skipped)
# by compare.py's fail-closed check.
#
# Per probe: compare exit 0 = removable, 1 = NOT removable (a measured result: the match changed or did not
# complete), 2 = malformed evidence. A generator that fails (it refuses an existing output, an import fails,
# it crashes) is an infrastructure failure: its output is NEVER compared, so a stale log of an earlier run
# cannot pass (PR 243 review round 2, R2).
# Exit: 0 every generator ran, every probe was measured and the joint set is removable; 1 every probe was
# measured but the joint set is not removable; 2 a generator failed or a log was malformed.
# Usage: sh experiments/E032-match-engine-inventory/skip_batch.sh <stamp>   (a stamp not used before)
D=experiments/E032-match-engine-inventory
O=${E032_OUT:-$D/out}
REF=$D/out/timing-delay20-kickoff-20261015.jsonl
infra=0
probe() {   # probe <label> <routines> <log>
  echo "== skip $1"
  if python3 -B $D/skip.py --skip "$2" --seeds 0x1234,0x2345 --log "$3" > /dev/null; then
    skipped=$(echo "$2" | sed 's/[^,]*/"&"/g; s/^/[/; s/$/]/')     # the routines skipped, as a JSON list
    python3 -B $D/compare.py "$REF" "$3" --seeds 0x1234,0x2345 --field "skipped=$skipped" --field "delay_count=20"
    rc=$?
    case $rc in
      0) echo "result: removable ($1)";;
      1) echo "result: NOT removable ($1)";;
      *) echo "MALFORMED EVIDENCE ($1)"; infra=1;;
    esac
  else
    echo "GENERATOR FAILED ($1): its output is not compared"
    infra=1
    rc=2
  fi
}
for r in 0791:8537 0791:8E24 0791:8F10 0791:9079 0791:0481 0791:1829 0791:0425 0791:0441 0791:94E8 0791:9372; do
  name=$(echo "$r" | tr ':,' '-_')
  probe "$r" "$r" "$O/skip-$name-$1.jsonl"
done
SET=0791:8F10,0791:9079,0791:0481,0791:1829,0791:0425,0791:0441,0791:94E8,0791:9372
probe "the joint set $SET" "$SET" "$O/skip-display-set-$1.jsonl"
joint=$rc
if [ $infra -ne 0 ]; then out=2; elif [ $joint -ne 0 ]; then out=1; else out=0; fi
echo "batch exit $out"
exit $out
