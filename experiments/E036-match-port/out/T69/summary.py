#!/usr/bin/env python3
"""T69: per address, the executions per match (the record's `counts`) by family: min-max, the sum and the matches with
none; with `--ports` records also each ported routine's calls (`port_calls`) against the counted entries.

    python3 -B experiments/E036-match-port/out/T69/summary.py LOG.jsonl [LOG2.jsonl]   (a second log is compared with the first)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments/E036-match-port"))
sys.path.insert(0, str(ROOT / "runtime"))
import records  # noqa: E402


def load(path):
    return {r["id"]: r for r in records.read_log(path)}


def main(argv):
    logs = [load(p) for p in argv]
    first = logs[0]
    families = sorted({mid.split("/")[0] for mid in first})
    addresses = sorted({a for r in first.values() for a in r["counts"]})
    print(f"{'address':10} " + " ".join(f"{f:>22}" for f in families) + "   total   matches with none")
    for a in addresses:
        cells, total, none = [], 0, []
        for f in families:
            vals = [r["counts"].get(a, 0) for mid, r in first.items() if mid.startswith(f + "/")]
            cells.append(f"{min(vals)}-{max(vals)} ({sum(vals)})")
            total += sum(vals)
        for mid, r in sorted(first.items()):
            if r["counts"].get(a, 0) == 0:
                none.append(mid)
        print(f"{a:10} " + " ".join(f"{c:>22}" for c in cells) + f"   {total:>9}   " + (", ".join(none) if none else "-"))
    if len(logs) > 1:
        second = logs[1]
        shared = lambda r, other: {a: n for a, n in r["counts"].items() if a in other["counts"]}      # noqa: E731
        bad = [mid for mid in first if mid in second and shared(first[mid], second[mid]) != shared(second[mid], first[mid])]
        print("counts equal in the second log (the addresses both counted):", "all" if not bad else f"NOT for {bad}")
    for mid, r in sorted(first.items()):
        calls = r.get("port_calls")
        if calls:
            off = {a: (n, r["counts"].get(a)) for a, n in calls.items() if r["counts"].get(a) != n}
            if off:
                print(f"{mid}: port calls differ from the counted entries: {off}")


if __name__ == "__main__":
    main(sys.argv[1:])
