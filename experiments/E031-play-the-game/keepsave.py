#!/usr/bin/env python3
"""Keep a saved game (.GL) a session wrote: copy it from the session's game folder to
.cache/kept/E031/saves/ (git-ignored; never overwritten) and append its name, size and sha256 to
out/saves.tsv (tracked). Usage: keepsave.py SESSION NAME.GL "what it is" """
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
session, name, what = sys.argv[1], sys.argv[2], sys.argv[3]
src = ROOT / "scratch" / "driver" / "play" / session / "game" / name
dst_dir = ROOT / ".cache" / "kept" / "E031" / "saves"
dst_dir.mkdir(parents=True, exist_ok=True)
dst = dst_dir / name
data = src.read_bytes()
if dst.exists():
    raise SystemExit(f"{dst} exists; saves are never overwritten: save under a new name")
dst.write_bytes(data)
digest = hashlib.sha256(data).hexdigest()
line = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\t{session}\t{name}\t{len(data)}\t{digest}\t{what}\n"
tsv = HERE / "out" / "saves.tsv"
if not tsv.exists():
    tsv.write_text("utc\tsession\tfile\tbytes\tsha256\twhat\n")
with tsv.open("a") as f:
    f.write(line)
print(line, end="")
