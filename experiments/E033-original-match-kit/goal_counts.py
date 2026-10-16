#!/usr/bin/env python3
"""E033 (PR 251 review round 2): the original's own goal count DS:80F0 + side (record_goal 6443) at play_match's
return (F2E3) and after the post-match update, against the board and the kit's result goals, in three matches.

    python3 -B experiments/E033-original-match-kit/goal_counts.py > experiments/E033-original-match-kit/out/<new>.txt"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(1, str(ROOT / "experiments/E033-original-match-kit"))
import original_match as kit
import stamps

img = kit.Image.from_savestate((ROOT / ".cache/dl/e0afff6751747233-e006-1000-r0001.sav").read_bytes())
for name, kw in [("R1", {"policy": stamps.quick(3), "pause_at": (30,)}),
                 ("seed70 dec", {"seed": 70, "policy": stamps.decisions, "pause_at": (20, 60)}),
                 ("seed C3C3", {"seed": 0xC3C3})]:
    m = kit.Match(img, kit.Fixture(7, 19, index=21), managed=7, seed=kw.get("seed"))
    at = {}

    def grab(replay, m=m):
        if not replay:
            at["c"] = [m.m.rd(0x80F0, 1), m.m.rd(0x80F1, 1)]
    m.m.at("0791:F2E3", grab)
    paused = set()
    for ev in m.events():
        if ev.kind == "minute" and ev.minute in kw.get("pause_at", ()) and ev.minute not in paused:
            paused.add(ev.minute)
            m.pause()
        if ev.kind == "decision":
            kw.get("policy", lambda m, d: m.answer())(m, ev.data)
    r = m.result()
    print(name, r["score"], "80F0 at F2E3", at.get("c"), "after", [m.m.rd(0x80F0, 1), m.m.rd(0x80F1, 1)],
          "goals", [(g["team"], g["player"], g["minute"], g["minute_byte"]) for g in r["goals"]],
          "disallowed", len(m.st["log"]["goals_disallowed"]))
