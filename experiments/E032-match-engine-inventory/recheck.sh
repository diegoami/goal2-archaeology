#!/bin/sh
# E032: every comparison the plan quotes, re-made on the committed logs. The work is recheck.py's: one
# explicit manifest of stamps, transcripts, logs and 80 comparisons, each with its expected exit code; a
# missing or extra input, a transcript without 'batch exit 0', a wrong exit code or a different number of
# comparisons is exit 2 (PR 243 review round 5: the round-4 version skipped a whole stamp when its pilot
# transcript was missing). Nothing here is optional and nothing is skipped.
# Usage: sh experiments/E032-match-engine-inventory/recheck.sh [--out DIR]
exec python3 -B experiments/E032-match-engine-inventory/recheck.py "$@"
