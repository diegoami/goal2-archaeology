#!/usr/bin/env python3
"""Run compare.py over the pairs the README tabulates and write the output to out/compare.txt.
    python3 experiments/fix-244-driver-keys/compare_all.py"""
import contextlib
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import compare  # noqa: E402

OUT = HERE / "out"
PAIRS = [
    ("E003 d0 10:00:00 on 10/04/1993: default pace (save_hold 0.52 s); r0003 aborted (exit -6 in a savestate)", "runs/E003/E003-r0047.json",
     [f"out/rerun-default/E003/E003-r000{n}.json" for n in (4, 5, 6, 7)]),
    ("E003 d0: control, game keys new, savestate key the old way, 4 more runs", "runs/E003/E003-r0047.json",
     [f"out/rerun-legacy-only-save/E003/E003-r000{n}.json" for n in (3, 4, 5)]),
    ("E003 d0: control, default pace + a plain F12 pressed into the guest before each read", "runs/E003/E003-r0047.json",
     [f"out/rerun-f12-per-read/E003/E003-r000{n}.json" for n in (1, 2, 3)]),
    ("E006 games 10:00 on 10/04/2026: default pace", "runs/E006/E006-r0001.json", ["out/rerun-default/E006/E006-r0002.json"]),
    ("E003 d3b (a remade main.sav): default pace", "runs/E003/E003-r0049.json",
     [f"out/rerun-default/E003/E003-r000{n}.json" for n in (1, 2)]),
    ("E003 d3b (a remade main.sav): default pace, after the review's change of the key code (R1)", "runs/E003/E003-r0049.json",
     [f"out/rerun-default/E003/E003-r000{n}.json" for n in (8, 9)]),
    ("E003 d0 10:00:00 on 10/04/1993: save key held 0.15 s", "runs/E003/E003-r0047.json",
     [f"out/rerun/E003/E003-r000{n}.json" for n in (3, 4, 5, 6, 7)]),
    ("E003 d0: control, legacy keys on the fixed driver", "runs/E003/E003-r0047.json",
     [f"out/rerun-legacy-keys/E003/E003-r000{n}.json" for n in (1, 2, 3, 4)]),
    ("E003 d0: control, game keys the old way, savestate key new", "runs/E003/E003-r0047.json",
     [f"out/rerun-legacy-only-keys/E003/E003-r000{n}.json" for n in (1, 2)]),
    ("E003 d0: control, game keys new, savestate key the old way", "runs/E003/E003-r0047.json",
     ["out/rerun-legacy-only-save/E003/E003-r0001.json"]),
    ("E003 d0: control, save key held 0.6 s", "runs/E003/E003-r0047.json",
     [f"out/rerun-save-key-hold-0.6/E003/E003-r000{n}.json" for n in (1, 2)]),
    ("E006 games 10:00 on 10/04/2026: save key held 0.15 s", "runs/E006/E006-r0001.json", ["out/rerun/E006/E006-r0001.json"]),
    ("E003 d3b (a remade main.sav): save key held 0.15 s", "runs/E003/E003-r0049.json",
     [f"out/rerun/E003/E003-r000{n}.json" for n in (8, 9)]),
    ("E003 d3b: control, save key held 0.6 s", "runs/E003/E003-r0049.json",
     [f"out/rerun-save-key-hold-0.6/E003/E003-r000{n}.json" for n in (3, 4)]),
]
lines = []
for title, orig, news in PAIRS:
    lines.append(f"##### {title}; original {orig}")
    for n in news:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            compare.main(str(ROOT / orig), str(HERE / n))
        text = buf.getvalue().splitlines()
        lines.append(f"--- {n}")
        lines.extend(l for l in text if " same " not in l or l.startswith("VERDICT"))
(OUT / "compare.txt").write_text("\n".join(lines) + "\n")
print("\n".join(l for l in lines if l.startswith(("#", "---", "VERDICT"))))
