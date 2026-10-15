#!/usr/bin/env python3
"""E026: does the tactic byte survive to full time? One match of an arm (default e3, seed index 0):
read country +0x2D of both engine sides before the run (after the declared write) and at the
board. The managed side 0 should keep its byte; the unmanaged side 1 is reset/changed by 0791:C173
after goals (F010), which is what this reads. Writes out/final-tactics.json (never overwritten)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import arm  # noqa: E402
from check import asset, emulate  # noqa: E402

name = sys.argv[1] if len(sys.argv) > 1 else "e3"
idx = int(sys.argv[2]) if len(sys.argv) > 2 else 0
out = HERE / "out" / f"final-tactics-{name}-i{idx}.json"
if out.exists():
    raise SystemExit(f"{out} exists")
record = json.loads((ROOT / "runs/E011/E011-r0001.json").read_text())
entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
data = asset(entry)
seen = {}


def write(m):
    c = m.sides()
    seen["before_write"] = {str(x): m.mem(m.country_lin(x) + 0x2D, 1)[0] for x in c}
    m.set_seed(arm.SEEDS[idx])
    if arm.ARMS[name]:
        m.set_country_tactics(c[0], seen["before_write"][str(c[0])] ^ arm.ARMS[name])
    seen["after_write"] = {str(x): m.mem(m.country_lin(x) + 0x2D, 1)[0] for x in c}
    seen["machine"] = m


m, err, secs = emulate(data, "none", inputs=[write])
c = m.sides()
rec = {"arm": name, "seed": arm.SEEDS[idx], "error": err, "score": m.final["score"],
       "before_write": seen["before_write"], "after_write": seen["after_write"],
       "at_full_time": {str(x): m.mem(m.country_lin(x) + 0x2D, 1)[0] for x in c}}
out.write_text(json.dumps(rec, indent=1))
print(rec)
