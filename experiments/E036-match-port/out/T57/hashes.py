#!/usr/bin/env python3
"""T57 (L40): record the SHA-256 of every file in this folder in a new TSV, which must not exist.

    python3 -B experiments/E036-match-port/out/T57/hashes.py sha256-<stamp>.tsv"""
import hashlib
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent


def main():
    dest = OUT / sys.argv[1]
    if dest.exists():
        sys.exit(f"refused: {dest} exists")
    rows = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}\t{p.name}" for p in sorted(OUT.iterdir()) if p.is_file()]
    dest.write_text("sha256\tfile\n" + "\n".join(rows) + "\n")
    print(f"{len(rows)} files hashed into {dest.name}")


if __name__ == "__main__":
    main()
