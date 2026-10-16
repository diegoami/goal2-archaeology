#!/usr/bin/env python3
"""E033: record the SHA-256 of every file under out/ (L40), in a new TSV that must not exist (E032's hashes.py).

    python3 -B experiments/E033-original-match-kit/hashes.py experiments/E033-original-match-kit/out/sha256-<stamp>.tsv"""
import hashlib
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"


def main():
    dest = Path(sys.argv[1])
    if dest.exists():
        sys.exit(f"refused: {dest} exists")
    rows = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}\t{p.name}" for p in sorted(OUT.iterdir())
            if p.is_file() and p.resolve() != dest.resolve()]
    dest.write_text("sha256\tfile\n" + "\n".join(rows) + "\n")
    print(f"{len(rows)} files hashed into {dest}")


if __name__ == "__main__":
    main()
