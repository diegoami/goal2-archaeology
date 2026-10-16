#!/usr/bin/env python3
"""Compare a re-run record (rerun.py, fixed driver) with an original record (runs/E0xx/, old driver):
the text-screen digest after each step, the data-segment words DS:7B62, DS:8336 and DS:A9FD of every step
(DS:7B64 is left out: it differs between runs of one arm in the originals, E003's summary shows it), and
a sha256 of each player or country array (E006). Prints one line per compared value and a verdict.

    python3 experiments/fix-244-driver-keys/compare.py runs/E003/E003-r0047.json out/rerun/E003/E003-r0001.json
Exit 0 when every compared value is equal, 1 when any differs, 2 when nothing could be compared."""
import hashlib
import json
import re
import sys

WORDS = ("DS:7B62", "DS:8336", "DS:A9FD")


def values(path):
    out = {}
    for o in json.load(open(path))["observations"]:
        step, field, value = o.get("step"), o.get("field", ""), str(o.get("value", ""))
        if o.get("source") == "screen":
            out[(int(step), "screen digest")] = value
        for w in WORDS:
            if o.get("source") == "memory" and f"word at {w} " in field:
                out[(int(step), w)] = value.split()[0]
        for kind in ("player array", "country array"):
            if field.startswith(kind) or f" {kind}:" in field:
                out[(int(step), kind + " sha256")] = hashlib.sha256(value.encode()).hexdigest()
    return out


def main(orig, new):
    a, b = values(orig), values(new)
    keys = sorted(set(a) & set(b))
    differ = [k for k in keys if a[k] != b[k]]
    for k in keys:
        print(f"step {k[0]:>2} {k[1]:<22} {'same     ' if a[k] == b[k] else 'DIFFERENT'} {str(a[k])[:20]} | {str(b[k])[:20]}")
    only = sorted(set(a) ^ set(b))
    if only:
        print("not in both:", only)
    if not keys:
        print("VERDICT nothing compared")
        return 2
    print(f"VERDICT {'same' if not differ and not only else 'DIFFERENT'}: {len(keys) - len(differ)} of {len(keys)} compared values equal")
    return 1 if differ or only else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
