#!/usr/bin/env python3
"""Record what a session's game folder holds now (the files GOAL wrote: .GL, .HIL, .SUM, and any
shipped file it changed): name, bytes, sha256, the file time, and whether it equals the release copy.
Writes nothing to the game; prints a table. Usage: folder.py S"""
import hashlib
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
game = ROOT / "scratch" / "driver" / "play" / sys.argv[1] / "game"
release = ROOT / ".cache" / "goal2"
print("file\tbytes\tsha256\tfile time (local, as DOS wrote it)\tagainst the release copy")
for p in sorted(game.iterdir()):
    data = p.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    orig = release / p.name
    if orig.exists():
        same = "same as the release" if hashlib.sha256(orig.read_bytes()).hexdigest() == digest else \
            f"CHANGED (release sha256 {hashlib.sha256(orig.read_bytes()).hexdigest()})"
    else:
        same = "written by the game or copied in by --gl"
    print(f"{p.name}\t{len(data)}\t{digest}\t{datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec='seconds')}\t{same}")
