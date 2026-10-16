#!/usr/bin/env python3
"""E033 (PR 251 review round 2): the instruction of every write, in play (play_match F098 to F2E3), of the bookings,
red-card and injury counts (STATS + 10t + 7..9), substitutions left DS:9B3A, the minute DS:831F and the commentary
ring counter DS:80EE, over five matches; counts per (what, writer).

    python3 -B experiments/E033-original-match-kit/writers.py > experiments/E033-original-match-kit/out/<new>.txt"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(1, str(ROOT / "experiments/E033-original-match-kit"))
import original_match as kit
import stamps
from unicorn import UC_HOOK_MEM_WRITE, UC_HOOK_CODE

img = kit.Image.from_savestate((ROOT / ".cache/dl/e0afff6751747233-e006-1000-r0001.sav").read_bytes())
WATCH = {"cards0": (0x7B7E + 7, 3), "cards1": (0x7B7E + 17, 3), "subs": (0x9B3A, 2), "minute": (0x831F, 2),
         "ring": (0x80EE, 2)}
total = {}
for name, kw in [("go in hard", {"seed": 4, "go_in_hard": True}), ("injury", {"seed": 70}),
                 ("decisions", {"seed": 70, "policy": stamps.decisions, "pause_at": (20, 60)}),
                 ("quick 30", {"policy": stamps.quick(3), "pause_at": (30,)}),
                 ("quick 1", {"policy": stamps.quick(0), "pause_at": (1,)})]:
    countries = None
    if kw.get("go_in_hard"):
        countries = img.countries()
        rec = bytearray(countries[7])
        rec[0x2D] |= 1 << 3
        countries[7] = bytes(rec)
    m = kit.Match(img, kit.Fixture(7, 19, index=21), managed=7, seed=kw.get("seed"), countries=countries)
    mm = m.m
    ds, cs = mm.DS * 16, mm.seg(0x0791) * 16
    live = {"on": False}
    mm.uc.hook_add(UC_HOOK_CODE, lambda *a: live.update(on=True), begin=cs + 0xF098, end=cs + 0xF098)
    mm.uc.hook_add(UC_HOOK_CODE, lambda *a: live.update(on=False), begin=cs + 0xF2E3, end=cs + 0xF2E3)
    for key, (off, size) in WATCH.items():
        def hook(uc, access, address, wsize, value, data, key=key, off=off, size=size):
            if not live["on"] or address + wsize <= ds + off or address >= ds + off + size:
                return
            pc = mm.pc()
            seg = (pc - cs) if 0 <= pc - cs < 0x10000 else None
            tag = (key, "0791:%04X" % seg if seg is not None else "lin %05X" % pc)
            total[tag] = total.get(tag, 0) + 1
        mm.uc.hook_add(UC_HOOK_MEM_WRITE, hook, begin=ds + off - 3, end=ds + off + size - 1)
    paused = set()
    for ev in m.events():
        if ev.kind == "minute" and ev.minute in kw.get("pause_at", ()) and ev.minute not in paused:
            paused.add(ev.minute)
            m.pause()
        if ev.kind == "decision":
            kw.get("policy", lambda m, d: m.answer())(m, ev.data)
for k in sorted(total):
    print(k, total[k])
