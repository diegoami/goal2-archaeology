#!/usr/bin/env python3
"""T59: the SHA-256 of every file of out/T59 (but this script's own output) into a new file named on the command line.

    python3 -B experiments/E036-match-port/out/T59/hashes.py experiments/E036-match-port/out/T59/sha256-<stamp>.tsv"""
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = Path(sys.argv[1])
lines = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}\t{p.name}" for p in sorted(HERE.iterdir())
         if p.is_file() and p.resolve() != out.resolve() and p.suffix != ".pyc"]
with open(out, "x") as f:
    f.write("\n".join(lines) + "\n")
print(f"{len(lines)} files hashed into {out}")
