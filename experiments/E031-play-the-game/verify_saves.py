#!/usr/bin/env python3
"""Download the saved games of release `play-the-game-saves` and check each against out/saves.tsv
(name, bytes, sha256). Exit 0 when every listed save is on the release with its hash.
Usage: python3 experiments/E031-play-the-game/verify_saves.py [--dir DIR]"""
import argparse
import csv
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RELEASE = "play-the-game-saves"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="download here (default: a temporary folder)")
    a = ap.parse_args()
    rows = list(csv.DictReader((HERE / "out" / "saves.tsv").open(), delimiter="\t"))
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(a.dir or tmp)
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gh", "release", "download", RELEASE, "--dir", str(d), "--clobber"], check=True)
        bad = 0
        for r in rows:
            p = d / r["file"]
            if not p.exists():
                print(f"MISSING {r['file']}")
                bad += 1
                continue
            data = p.read_bytes()
            ok = hashlib.sha256(data).hexdigest() == r["sha256"] and len(data) == int(r["bytes"])
            bad += not ok
            print(f"{'ok' if ok else 'BAD'} {r['file']} {r['what']}")
    print(f"{len(rows) - bad} of {len(rows)} saves verified")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
