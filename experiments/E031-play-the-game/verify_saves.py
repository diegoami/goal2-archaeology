#!/usr/bin/env python3
"""Download the saved games of release `play-the-game-saves` and check them against out/saves.tsv,
failing closed: the table must have rows, every row's file must be on the release with its bytes and
sha256, and the release must hold no file the table does not list. Exit 0 only then.
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


def read_table(path):
    return list(csv.DictReader(Path(path).open(), delimiter="\t"))


def compare(rows, folder):
    """Problems (empty when every row matches a downloaded file and nothing else was downloaded)."""
    folder = Path(folder)
    problems = []
    if not rows:
        problems.append("saves.tsv has no rows")
    names = {r["file"] for r in rows}
    for r in rows:
        p = folder / r["file"]
        if not p.is_file():
            problems.append(f"MISSING {r['file']}")
            continue
        data = p.read_bytes()
        if len(data) != int(r["bytes"]) or hashlib.sha256(data).hexdigest() != r["sha256"]:
            problems.append(f"BAD {r['file']}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    for p in sorted(folder.iterdir()):
        if p.name not in names:
            problems.append(f"UNLISTED {p.name} is on the release but not in saves.tsv")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", help="download here (default: a temporary folder)")
    ap.add_argument("--table", default=str(HERE / "out" / "saves.tsv"))
    a = ap.parse_args(argv)
    rows = read_table(a.table)
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(a.dir or tmp)
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gh", "release", "download", RELEASE, "--dir", str(d), "--clobber"], check=True)
        problems = compare(rows, d)
    for p in problems:
        print(p)
    print(f"{len(rows) - sum(1 for p in problems if p.startswith(('MISSING', 'BAD')))} of {len(rows)} saves "
          f"verified, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
