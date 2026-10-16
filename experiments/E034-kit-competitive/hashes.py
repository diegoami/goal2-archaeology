#!/usr/bin/env python3
"""E034: record the SHA-256 of every file under out/ (L40), in a new TSV that must not exist (E033's hashes.py).

    python3 -B experiments/E034-kit-competitive/hashes.py experiments/E034-kit-competitive/out/sha256-<stamp>.tsv

The originals used (never in the tree): E006-r0001 e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d
(release E006), E031 g1 step 3874 3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc (release
play-the-game-states); both checked by hash where they are read."""
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
