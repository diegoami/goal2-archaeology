#!/usr/bin/env python3
"""Name a state's screen kind from its fixed text, never from its digest.

    python3 tools/screens/identify.py <record|run id> [state ...]     the kind of each state
    python3 tools/screens/identify.py <record|run id> --summary       kinds and the unknown count
    python3 tools/screens/identify.py --savestate <file.sav>          the kind of a savestate's screen

The rules are in static/screens/kinds.tsv (and are copied into the catalogue). A screen no rule
matches is `unknown`; it goes to the owner as a PNG (docs/screens.md).
"""
import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402


def identify_record(rec, kinds=None):
    """{state: kind}; a state whose text the record does not hold is `unknown`."""
    kinds = common.load_kinds() if kinds is None else kinds
    return {n: (common.identify_text(s["text"], kinds) if s["text"] is not None else "unknown")
            for n, s in rec["states"].items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("record", nargs="?")
    ap.add_argument("states", nargs="*", type=int)
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--savestate", type=Path)
    a = ap.parse_args(argv)
    if a.savestate:
        sys.path.insert(0, str(common.ROOT / "runtime" / "driver"))
        import savestate
        print(common.identify_text(savestate.Savestate(a.savestate).screen().text()))
        return 0
    if not a.record:
        ap.error("a record or --savestate")
    rec = common.read_record(a.record)
    kinds = identify_record(rec)
    if a.summary:
        count = collections.Counter(kinds.values())
        for kind, n in sorted(count.items()):
            print(f"{n:5d} {kind}")
        print(f"{rec['run_id']}: states {len(kinds)}, unknown {count.get('unknown', 0)}")
        return 0
    for n, kind in kinds.items():
        if not a.states or n in a.states:
            print(f"{rec['run_id']} state {n}: {kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
