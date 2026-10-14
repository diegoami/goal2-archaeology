#!/usr/bin/env python3
"""E026: read the two squads' tactic bytes out of the start state (E011-r0001's watchstart state),
no run: for each of the two countries on engine sides 0/1 the +0x2D byte, and for each of the 20
squad players the position (+6), the override byte +0xF and the status byte +0x10. Writes one JSON
file under out/ (never overwritten) and prints the table."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E021-m0-whole-match"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
from check import asset  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402

record = json.loads((ROOT / "runs/E011/E011-r0001.json").read_text())
entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
m = WatchedMatch(asset(entry))
out = {"start_state": entry["name"], "sha256": entry["sha256"], "sides": m.sides(), "countries": {}}
for side, c in enumerate(m.sides()):
    t = m.mem(m.country_lin(c) + 0x2D, 1)[0]
    squad = m.squad(c)
    players = []
    for w in squad:
        lin = m.player_lin(w)
        players.append({"word": w, "position": m.mem(lin + 6, 1)[0], "own_tactic_set_0F": m.mem(lin + 0xF, 1)[0],
                        "status_10": m.mem(lin + 0x10, 1)[0], "energy_0E": m.mem(lin + 0xE, 1)[0]})
    out["countries"][str(c)] = {"side": side, "tactic_byte_2D": t, "players": players}
    print(f"side {side} country {c}: +0x2D = {t:#04x}")
    for i, p in enumerate(players, 1):
        print(f"  slot {i:2d} word {p['word']:4d} pos {p['position']:2d} +0xF {p['own_tactic_set_0F']:#04x} +0x10 {p['status_10']:#04x}")
path = HERE / "out" / "start-state.json"
if path.exists():
    raise SystemExit(f"{path} exists")
path.write_text(json.dumps(out, indent=1))
