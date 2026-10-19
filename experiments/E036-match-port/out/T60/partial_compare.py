#!/usr/bin/env python3
"""T60: compare.py's per-match comparison for the matches a partial log holds (compare.py wants a whole family; a smoke
or falsifier run holds a few matches). Prints, per match, 'identical' or the first differing field.

    python3 -B experiments/E036-match-port/out/T60/partial_compare.py CANDIDATE.jsonl [--expect differ]

Exit 0 when every match is as expected (identical by default; with --expect differ: differs or did not complete)."""
import json
import sys
from pathlib import Path

E036 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(E036))
sys.path.insert(0, str(E036.parents[1] / "runtime"))
import compare  # noqa: E402
import families  # noqa: E402


def main():
    path = sys.argv[1]
    expect = "differ" if "--expect" in sys.argv and sys.argv[sys.argv.index("--expect") + 1] == "differ" else "identical"
    refs = {}
    for fam in families.discover().values():
        refs.update(compare.load(str(E036.parents[1] / fam.reference)))
    bad = 0
    for line in open(path):
        cand = json.loads(line)
        ref = refs[cand["id"]]
        if compare.completed(cand) is not None:
            verdict = "did not complete: " + compare.completed(cand)
            ok = expect == "differ"
        else:
            diffs = compare.differences(ref, cand)
            verdict = "identical" if not diffs else "differs: " + compare.describe(diffs)
            ok = (not diffs) if expect == "identical" else bool(diffs)
        bad += 0 if ok else 1
        print(f"{cand['id']}: {verdict}")
    print(f"{'all as expected' if not bad else str(bad) + ' not as expected'} ({expect})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
