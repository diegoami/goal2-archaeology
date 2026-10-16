#!/usr/bin/env python3
"""Tabulate DS:7B62 (the game's random seed, low word) at some steps of E003 d0 records at 10:00:00 on
10/04/1993: the originals in runs/E003/ and the re-runs under out/rerun/ (fixed driver) and
out/rerun-legacy-keys/ (control: the fixed driver with its old xdotool keys).
    python3 experiments/fix-244-driver-keys/seeds.py"""
import glob
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STEPS = (1, 2, 3, 4, 5, 8, 11)
ARM = "d0-time-100000-date-10041993"


def row(p):
    r = json.load(open(p))
    d = {int(o["step"]): o["value"].split()[0] for o in r["observations"]
         if o.get("source") == "memory" and "word at DS:7B62 " in o["field"]}
    return r["arm"], [d.get(i, "-") for i in STEPS]


print("DS:7B62 at steps", STEPS)
for label, pat in (("original (old driver)", "runs/E003/E003-r00[34]*.json"),
                   ("fixed driver", "experiments/fix-244-driver-keys/out/rerun/E003/*.json"),
                   ("fixed driver, legacy keys (control)", "experiments/fix-244-driver-keys/out/rerun-legacy-keys/E003/*.json"),
                   ("fixed driver, save key held 0.6 s", "experiments/fix-244-driver-keys/out/rerun-save-key-hold-0.6/E003/*.json"),
                   ("game keys old way, savestate key new", "experiments/fix-244-driver-keys/out/rerun-legacy-only-keys/E003/*.json"),
                   ("game keys new, savestate key old way", "experiments/fix-244-driver-keys/out/rerun-legacy-only-save/E003/*.json")):
    for p in sorted(glob.glob(str(ROOT / pat))):
        arm, vals = row(p)
        if arm == ARM:
            print(f"{label:<38} {Path(p).stem} {' '.join(vals)}")
