"""E024: write the SHA-256 of every file under out/ that is not listed in an earlier manifest.

    python3 -B experiments/E024-computer-managers/hashes.py

Writes out/SHA256SUMS-<UTC time>.txt (a new file, never overwritten) with one `<sha256>  <name>` line for
each out/ file that no earlier SHA256SUMS-*.txt names and that is not itself a manifest. The originals stay
where they were written; the manifest only records them (docs/process.md section 4, L40).
"""
import hashlib
from datetime import datetime, timezone
from pathlib import Path

out = Path(__file__).resolve().parent / "out"
done = set()
for m in sorted(out.glob("SHA256SUMS-*.txt")):
    for line in m.read_text().splitlines():
        if line.strip():
            done.add(line.split(None, 1)[1].strip())
lines = []
for f in sorted(out.iterdir()):
    if f.name.startswith("SHA256SUMS-") or f.name in done or not f.is_file():
        continue
    lines.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}")
if lines:
    fn = out / f"SHA256SUMS-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.txt"
    fn.write_text("\n".join(lines) + "\n")
    print(fn, len(lines), "files")
else:
    print("nothing new")
