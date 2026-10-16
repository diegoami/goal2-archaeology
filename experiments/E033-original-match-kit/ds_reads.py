#!/usr/bin/env python3
"""E033 (PR 251 review R1): the initialised data a match reads and never writes, the data half of the build guard.

    python3 -B experiments/E033-original-match-kit/ds_reads.py --log experiments/E033-original-match-kit/out/<new>.json

The initialised data segment is DS:0000..7B6F (image 25810..2D37F, static/goal-exe/data). For each scenario a match
runs with read and write hooks over it: a byte read before any write in that run is an input; a byte written in any
run is a variable. The guard's data is the union of inputs that no run writes. Scenarios cover the engine and the
screens the kit drives: the reference fixture; two of E032's seeds; a pause with tactics, positions, marking, own
tactics and a substitution asked for; a half-time substitution and a refused eleven; seed 70 (an injury notice);
the quick result; goal2 managing country 19."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, Match, Fixture  # noqa: E402
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE  # noqa: E402

IMAGE = ("e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d", "e006-1000-r0001.sav")
INIT = 0x7B70        # initialised data: DS:0000..7B6F


def pause_at(*minutes):
    def f(m, minute, done=set()):
        if minute in minutes and minute not in done:
            done.add(minute)
            m.pause()
    return f


def players(m, d):
    if d["context"] == "pause":
        pos = dict(d["positions"])
        other = m._squad(19)[:11]
        m.answer(tactics={4: True, 8: False}, positions={d["eleven"][5]: (pos[d["eleven"][5]] + 2) % 14},
                 marking={d["eleven"][3]: other[9]}, own_tactics={d["eleven"][7]: {1: True, 2: None}},
                 substitutions=[(d["eleven"][10], d["bench"][7])])
    elif d["context"] == "half_time" and not d.get("refused"):
        m.answer(substitutions=[(d["eleven"][9], 132)])       # the reserve keeper: refused
    elif d["context"] == "half_time":
        m.answer(substitutions=[(121, d["bench"][1])])
    else:
        m.answer()


def injured(m, d):
    if d["context"] == "substitution" and d["injured"]:
        m.answer(substitutions=[(d["injured"][0], d["bench"][1])])
    else:
        m.answer()


def quick(m, d):
    m.answer(quick=True, speed=3) if d["context"] == "pause" else m.answer()


SCENARIOS = [
    ("reference", {}, None, None),
    ("seed 0x1234", {"seed": 0x1234}, None, None),
    ("seed 0xE719", {"seed": 0xE719}, None, None),
    ("pause: tactics, positions, marking, own tactics, a substitution asked for; half time refused then made",
     {}, pause_at(15), players),
    ("seed 70: an injury notice answered", {"seed": 70}, None, injured),
    ("quick result and speed from a pause", {}, pause_at(30), quick),
    ("goal2 manages country 19", {"managed": 19}, None, None),
    ("Denmark's tactics all set (offside trap, man to man, full pitch, ...)", {"tactics": 0xFF}, None, None),
    ("Denmark's tactics all clear", {"tactics": 0x00}, None, None),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    data = (ROOT / ".cache/dl" / f"{IMAGE[0][:16]}-{IMAGE[1]}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == IMAGE[0]
    img = Image.from_savestate(data)
    union_read, union_written, runs = bytearray(INIT), bytearray(INIT), []
    for name, kw, on_minute, policy in SCENARIOS:
        kw = {"managed": 7} | kw
        if "tactics" in kw:
            countries = img.countries()
            rec = bytearray(countries[7])
            rec[0x2D] = kw.pop("tactics")
            countries[7] = bytes(rec)
            kw["countries"] = countries
        m = Match(img, Fixture(7, 19, index=21), **kw)
        base = m.m.DS * 16
        reads, writes = bytearray(INIT), bytearray(INIT)

        def on_read(uc, access, address, size, value, d):
            for i in range(size):
                j = address + i - base
                if 0 <= j < INIT and not writes[j]:
                    reads[j] = 1

        def on_write(uc, access, address, size, value, d):
            for i in range(size):
                j = address + i - base
                if 0 <= j < INIT:
                    writes[j] = 1
        m.m.uc.hook_add(UC_HOOK_MEM_READ, on_read, begin=base, end=base + INIT - 1)
        m.m.uc.hook_add(UC_HOOK_MEM_WRITE, on_write, begin=base - 3, end=base + INIT - 1)
        t = time.time()
        for ev in m.events():
            if ev.kind == "minute" and on_minute:
                on_minute(m, ev.minute)
            if ev.kind == "decision":
                (policy or (lambda mm, d: mm.answer()))(m, ev.data)
        r = m.result()
        for i in range(INIT):
            union_read[i] |= reads[i]
            union_written[i] |= writes[i]
        runs.append({"scenario": name, "score": r["score"], "inputs": sum(reads), "written": sum(writes),
                     "decisions": [d["context"] for d in r["decisions"]], "wall_s": round(time.time() - t, 1)})
        print(json.dumps(runs[-1]), flush=True)
    covered = [i for i in range(INIT) if union_read[i] and not union_written[i]]
    ranges, start = [], None
    for i in range(INIT + 1):
        inside = i < INIT and union_read[i] and not union_written[i]
        if inside and start is None:
            start = i
        elif not inside and start is not None:
            ranges.append([start, i - start])
            start = None
    rec = {"image_sha256": IMAGE[0], "runs": runs, "read_and_never_written": len(covered),
           "written": sum(union_written), "read_but_written": sum(1 for i in range(INIT) if union_read[i] and union_written[i]),
           "ranges": ranges}
    with open(log, "x") as f:
        json.dump(rec, f)
    print(f"{len(covered)} bytes in {len(ranges)} ranges read and never written; {sum(union_written)} written")


if __name__ == "__main__":
    main()
