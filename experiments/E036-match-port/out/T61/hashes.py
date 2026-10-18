#!/usr/bin/env python3
"""T61: the SHA-256 of every output under out/T61 (not this list), to stdout as `hash<TAB>path`.

    python3 -B experiments/E036-match-port/out/T61/hashes.py > experiments/E036-match-port/out/T61/sha256-<commit>.tsv"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
for path in sorted(HERE.iterdir()):
    if path.is_file() and not path.name.startswith("sha256-") and path.suffix != ".pyc":
        print(hashlib.sha256(path.read_bytes()).hexdigest() + "\t" + path.name)
