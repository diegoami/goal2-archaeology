#!/usr/bin/env python3
"""E032: compare timing logs match by match (same seed): score, ticks, draws, the draws digest, the board's
raw statistics and the commentary's template counts must agree; CPU seconds are reported.

    python3 -B experiments/E032-match-engine-inventory/compare.py <reference.jsonl> <other.jsonl>

Exits 1 when any deterministic field differs for a seed present in both."""
import json
import sys

FIELDS = ("score", "ticks", "draws", "draws_digest", "statistics_raw", "templates")


def load(path):
    return {r["seed"]: r for r in map(json.loads, open(path))}


def main():
    ref, other = load(sys.argv[1]), load(sys.argv[2])
    bad = 0
    for seed in sorted(set(ref) & set(other)):
        a, b = ref[seed], other[seed]
        diff = [f for f in FIELDS if a.get(f) != b.get(f)]
        bad += bool(diff)
        print(f"seed 0x{seed:04x}: score {a['score']} ticks {a['ticks']} draws {a['draws']} "
              f"cpu {a['cpu_s']} s -> {b['cpu_s']} s; {'DIFFER: ' + ', '.join(diff) if diff else 'identical'}")
    print(f"{len(set(ref) & set(other))} seeds compared, {bad} differ")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
