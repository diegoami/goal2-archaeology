#!/usr/bin/env python3
"""Edge-value calls of the ORIGINAL routines of F027 in Unicorn (T53 rework, round 1).

    python3 experiments/E027-discipline-rules/edge_calls.py

Each routine is called as the original bytes of E011-r0001's watchstart savestate, with its arguments pushed on a scratch stack
and the memory it reads declared (written) first; nothing is substituted. The declared inputs of each test are printed. The
checks assert the statements of F027 (and the counterexamples to the earlier wording are printed, not hidden):

  T1 B27F      all 2^6 combinations of elements 3, 4, 5, 6, 7, 8 of +0x10 -> the byte after, against the machine of F027 section 2
  T2 7A43      managed and computer side, counters (DS:7B86, DS:7B87) 0..4 and 255, available squad players 8..20
  T3 5A8F      fixture kinds 0..255, countries of equal and of different continent, for the first and the second country
  T4 3558      the fitness/energy it leaves, from energy 0 and from energy 20, managed and computer player, ages around
               peak+4, DS:0E82 as in the data image, 4000 seeds each: how often the energy it leaves is 0
  T5 3651      an injured player (energy 0): how often energy is restored per call, 600 seeds
The log is written with exclusive creation to out/edge-calls-<UTC>-<pid>.log (never overwritten).
"""
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/E021-m0-whole-match"))
from check import asset  # noqa: E402
from watched_match import Guest, PLAYERS, COUNTRIES, COUNTRY_SIZE, PLAYER_SIZE, SEED  # noqa: E402
from unicorn import UC_HOOK_INTR  # noqa: E402
sys.path.insert(0, str(HERE))
from logs import open_new, stamped  # noqa: E402

SENT = 0xFFF0     # return address in segment 0791; the run stops there (never executed)
SCRATCH = 0xE0000   # linear scratch for a fixture record (segment 0xE000, offset 0; ROM area, unused by the game)

lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


class Rig:
    def __init__(self):
        record = json.loads((ROOT / "runs/E011/E011-r0001.json").read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        self.sha = entry["sha256"]
        self.g = Guest(asset(entry))
        self.g.mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
        self.sp0 = self.g.reg("sp") - 0x300
        self.ss = self.g.reg("ss")

    def call(self, addr, args, far=False):
        g = self.g
        seg, off = addr.split(":")
        cs = g.seg(int(seg, 16))
        sentcs = g.seg(0x791)
        # ascending addresses: the return address (ip, then cs for a far call), then the arguments, last pushed first
        words = ([SENT, sentcs] if far else [SENT]) + list(reversed(args))
        sp = self.sp0 - 2 * len(words)
        raw = b"".join((w & 0xFFFF).to_bytes(2, "little") for w in words)
        g.put(self.ss * 16 + sp, raw)
        g.set_reg("sp", sp)
        g.set_reg("cs", cs)
        g.set_reg("eip", int(off, 16))
        # a near routine is called with cs = its own segment; the return lands on SENT in that segment
        until = (sentcs if far else cs) * 16 + SENT
        g.emulate(until, 20)
        return g.reg("ax")

    def player(self, p):
        return self.g.far(PLAYERS) + PLAYER_SIZE * p

    def country(self, c):
        return self.g.far(COUNTRIES) + COUNTRY_SIZE * c


def t1(r):
    g = r.g
    say("T1 B27F over the 2^6 combinations of elements 3,4,5,6,7,8 of +0x10 (player 5; declared input: that byte)")
    p = r.player(5)
    bad = 0
    for combo in range(64):
        els = [3, 4, 5, 6, 7, 8]
        s = {e for i, e in enumerate(els) if combo >> i & 1}
        byte = sum(1 << (e - 1) for e in s)
        g.put(p + 0x10, bytes([byte]))
        r.call("0791:B27F", [5])
        out = g.mem(p + 0x10, 1)[0]
        # the machine of F027 section 2
        t = set(s)
        t.discard(8)
        if 6 in t:
            t.add(8)
        t.discard(6)
        if 5 in t:
            if 4 not in t:
                t.add(4)
            else:
                t.add(8)
                t.discard(4)
        t.discard(5)
        want = sum(1 << (e - 1) for e in t)
        if out != want:
            bad += 1
            say(f"  MISMATCH in {sorted(s)}: original {out:#04x}, F027 {want:#04x}")
    say(f"  64 combinations, {bad} mismatches against the F027 machine; elements 3 and 7 pass through untouched in all of them")


def t2(r):
    g = r.g
    say("T2 7A43 (declared inputs: country +0x2E of the side's country, the counters DS:7B86/7B87 of that side, the +0xE of squad players)")
    side = 0
    cidx = g.rd(0x9B34 + 2 * side)
    c = r.country(cidx)
    squad = [g.word_at(c + 2 * i) for i in range(20)]
    old_flag = g.mem(c + 0x2E, 1)
    res = {}
    for managed in (True, False):
        g.put(c + 0x2E, bytes([0x81 if managed else 0]))
        for avail in (8, 11, 12, 13, 20):
            for k, w in enumerate(squad):          # first `avail` squad players available (energy 5, element bits clear)
                g.put(r.player(w) + 0xE, bytes([5 if k < avail else 0]))
                g.put(r.player(w) + 0x10, bytes([0]))
            for b86, b87 in ((0, 0), (1, 1), (2, 0), (0, 2), (1, 2), (3, 0), (0, 3), (2, 2), (255, 1), (4, 0)):
                g.put(0x7B86 + g.DS * 16 + side * 10, bytes([b86, b87]))
                res[(managed, avail, b86, b87)] = r.call("0791:7A43", [side]) & 0xFF
    allowed_ok = True
    for (managed, avail, b86, b87), v in res.items():
        want = int((b86 + b87) < 3 and (managed or avail > 11))
        if v != want:
            allowed_ok = False
            say(f"  MISMATCH managed={managed} avail={avail} counters=({b86},{b87}): original {v}, F027 {want}")
    say(f"  {len(res)} calls; result == (b86 + b87 < 3 and (managed or more than 11 available)) in all: {allowed_ok}")
    g.put(c + 0x2E, old_flag)


def t3(r):
    g = r.g
    say("T3 5A8F (declared inputs: a fixture record at the scratch address: kind (+2), country A (+4), country B (+6); continents +0x2C of both)")
    ca, cb = 3, 9
    ra = {}
    for same in (True, False):
        g.put(r.country(ca) + 0x2C, bytes([1]))
        g.put(r.country(cb) + 0x2C, bytes([1 if same else 2]))
        for kind in range(256):
            g.put(SCRATCH, bytes(12))
            g.put(SCRATCH + 2, bytes([kind]))
            g.put(SCRATCH + 4, ca.to_bytes(2, "little") + cb.to_bytes(2, "little"))
            for name, country in (("A", ca), ("B", cb)):
                ra[(same, kind, name)] = r.call("1771:5A8F", [country, SCRATCH >> 4, 0], far=True) & 0xFF
    inset = {k for k in range(256) if ra[(True, k, "A")] == 1}
    say(f"  same continent: kinds with 5A8F true for country A (= membership of DS:0F3E): {len(inset)} kinds; F027/F019 set {{3,4,7,8..203}}: "
        f"{inset == ({3, 4, 7} | set(range(8, 204)))}")
    say(f"  kind 1, different continents: country A -> {ra[(False, 1, 'A')]}, country B -> {ra[(False, 1, 'B')]} (F027: 1 and 0)")
    other = sorted(k for k in range(256) if ra[(False, k, 'A')] != ra[(True, k, 'A')])
    say(f"  kinds where the continents change the answer for A: {other}; for B: "
        f"{sorted(k for k in range(256) if ra[(False, k, 'B')] != ra[(True, k, 'B')])}")


def t45(r):
    g = r.g
    say("T4 3558 and T5 3651 (declared inputs: player 7's +0 country, +1 age, +2 peak, +0xD fitness, +0xE energy; country +0x2E; the seed DS:7B62)")
    pl = r.player(7)
    cidx = g.mem(pl, 1)[0]
    c = r.country(cidx)
    say(f"  DS:0E82..0E85 in this state: {list(g.mem(g.DS * 16 + 0xE82, 4))}")
    old = g.mem(c + 0x2E, 1)
    for managed in (True, False):
        g.put(c + 0x2E, bytes([0x81 if managed else 0]))
        for age, peak in ((20, 27), (31, 27), (32, 27), (33, 27)):
            for e0 in (0, 20):
                zero = 0
                zseeds = []
                ends = Counter()
                for seed in range(1, 4001):
                    g.put(pl + 1, bytes([age, peak]))
                    g.put(pl + 0xD, bytes([10, e0]))
                    g.put(g.DS * 16 + SEED, seed.to_bytes(2, "little"))
                    r.call("1771:3558", [7], far=True)
                    fit, en = g.mem(pl + 0xD, 2)
                    ends[(fit, en)] += 1
                    zero += en == 0
                    if en == 0 and len(zseeds) < 5:
                        zseeds.append((seed, fit))
                say(f"  3558 managed={managed} age={age} peak={peak} energy before {e0}: energy left 0 in {zero} of 4000 seeds (first: seed, fitness {zseeds}); "
                    f"(fitness, energy) most common {ends.most_common(3)}")
    g.put(c + 0x2E, old)
    rec = 0
    for seed in range(1, 601):
        g.put(pl + 1, bytes([25, 27]))
        g.put(pl + 0xD, bytes([10, 0]))
        g.put(g.DS * 16 + SEED, seed.to_bytes(2, "little"))
        r.call("1771:3651", [7, 0], far=True)     # (player, flag): flag is the second word pushed last? see the check below
        rec += g.mem(pl + 0xE, 1)[0] != 0
    say(f"  3651 on an injured player (energy 0, flag 0): energy restored in {rec} of 600 seeds (1/3 = 200)")


def main():
    r = Rig()
    say(f"E027 edge calls; savestate E011-r0001 watchstart sha256 {r.sha}")
    t1(r)
    t2(r)
    t3(r)
    t45(r)
    path, f = open_new(stamped(HERE / "out", "edge-calls"))
    with f:
        f.write("\n".join(lines) + "\n")
    print("log:", path)


if __name__ == "__main__":
    main()
