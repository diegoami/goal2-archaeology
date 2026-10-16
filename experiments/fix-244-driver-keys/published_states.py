#!/usr/bin/env python3
"""Which published savestates made by the driver carry Alt held in their saved BIOS data (issue 244)?
For each evidence manifest of the driver's experiments, download the savestate asset from its release into
a scratch folder (not the repository), verify its sha256 against the manifest, and print the BIOS keyboard flags
(0040:0017, 0040:0018, 0040:0096) as lastkey.py reads them. Nothing is remade or published.

    python3 experiments/fix-244-driver-keys/published_states.py DOWNLOAD_DIR [--out out/published-states.tsv]"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402

DRIVER_EXPERIMENTS = ("E005", "E006", "E010", "E011", "E013", "E014", "E018")
REPO = "diegoami/goal2-archaeology"

ap = argparse.ArgumentParser()
ap.add_argument("dest")
ap.add_argument("--out", default=str(HERE / "out" / "published-states.tsv"))
a = ap.parse_args()
dest = Path(a.dest)
dest.mkdir(parents=True, exist_ok=True)
rows, seen = [], set()
for exp in DRIVER_EXPERIMENTS:
    for mp in sorted((ROOT / "evidence" / exp).glob("*.manifest.json")):
        m = json.loads(mp.read_text())
        release = m["store"].split(":", 1)[1]
        for f in m["files"]:
            if f["class"] != "save" or f["asset"] in seen:
                continue
            seen.add(f["asset"])
            path = dest / f["asset"]
            if not path.exists():
                subprocess.run(["gh", "release", "download", release, "--repo", REPO, "--pattern", f["asset"],
                                "--dir", str(dest)], check=True, capture_output=True)
            data = path.read_bytes()
            ok = hashlib.sha256(data).hexdigest() == f["sha256"]
            s = savestate.Savestate(data)
            f1, f2 = s.memory(0x417, 2)
            f3 = s.memory(0x496, 1)[0]
            bda = s.memory(0x41A, 0x24)
            words = [int.from_bytes(bda[4 + i:6 + i], "little") for i in range(0, 32, 2)]
            alt = bool(f1 & 8 or f2 & 2 or f3 & 8)
            rows.append((exp, m["run_id"], f["name"], f["sha256"][:16], "yes" if ok else "NO", f"{f1:08b}", f"{f2:08b}", f"{f3:08b}", "alt held" if alt else "no alt",
                         f"F12 0x8600 x{words.count(0x8600)}, Alt+F12 0x8c00 x{words.count(0x8C00)}"))
header = ("experiment", "run", "file", "sha256[:16]", "hash ok", "0040:0017", "0040:0018", "0040:0096", "alt", "BIOS buffer (16 words)")
Path(a.out).write_text("\n".join("\t".join(r) for r in (header, *rows)) + "\n")
print(f"{len(rows)} states; alt held in {sum(r[-1] == 'alt held' for r in rows)}; hash mismatches {sum(r[4] != 'yes' for r in rows)}")
