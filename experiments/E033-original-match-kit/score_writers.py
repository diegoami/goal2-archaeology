#!/usr/bin/env python3
"""E033 (PR 251 review round 2, R1 and R2): the instruction of every score write (DS:9B3C/9B3D) and the kit's goal
and goal_disallowed events and result goals, in the review's two cases: the reference fixture with a quick result
from a pause at minute 30 (speed 3), and seed 70 with stamps.py's decisions at pauses 20 and 60.

    python3 -B experiments/E033-original-match-kit/score_writers.py [KIT_DIR] > experiments/E033-original-match-kit/out/<new>.txt

KIT_DIR imports original_match from there (old_kit.py's export of an earlier commit); default runtime/."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "runtime"))
sys.path.insert(1, str(ROOT / "experiments/E033-original-match-kit"))
import original_match as kit
import stamps
from unicorn import UC_HOOK_MEM_WRITE

img = kit.Image.from_savestate((ROOT / ".cache/dl/e0afff6751747233-e006-1000-r0001.sav").read_bytes())


def probe(name, m, on_event):
    mm = m.m
    ds = mm.DS * 16
    cs = mm.seg(0x0791)
    pcs = {}

    def hook(uc, access, address, size, value, data):
        if address + size <= ds + 0x9B3C or address >= ds + 0x9B3E:
            return
        pc = mm.pc() - cs * 16
        pcs[pc] = pcs.get(pc, 0) + 1
    mm.uc.hook_add(UC_HOOK_MEM_WRITE, hook, begin=ds + 0x9B3C - 3, end=ds + 0x9B3D)
    kinds = {}
    for ev in m.events():
        kinds[ev.kind] = kinds.get(ev.kind, 0) + 1
        on_event(m, ev)
    r = m.result()
    print(name, "score", r["score"], "goals", len(r["goals"]), "events", {k: kinds.get(k) for k in ("goal", "goal_disallowed")})
    print("  score-write PCs (offset in 0791):", {("%04X" % k): v for k, v in sorted(pcs.items())})


def quick_at(minute, speed=3):
    def f(m, ev):
        if ev.kind == "minute" and ev.minute == minute and not m.waiting:
            m.pause()
        if ev.kind == "decision":
            m.answer(quick=True, speed=speed) if ev.data["context"] == "pause" else m.answer()
    return f


probe("R1 quick at 30", kit.Match(img, kit.Fixture(7, 19, index=21), managed=7), quick_at(30))
paused = set()


def r2(m, ev):
    if ev.kind == "minute" and ev.minute in (20, 60) and ev.minute not in paused:
        paused.add(ev.minute)
        m.pause()
    if ev.kind == "decision":
        stamps.decisions(m, ev.data)


probe("R2 seed 70 decisions", kit.Match(img, kit.Fixture(7, 19, index=21), managed=7, seed=70), r2)
