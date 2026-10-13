#!/usr/bin/env python3
"""The quick engine's second half with the non-friendly gate open: counts of D5C1 and what it reaches (T53, Scope 2).

    python3 experiments/E027-discipline-rules/quick_second_half.py [N] [first_seed] [random-table]

With `random-table` one more declared input is written: DS:8337+1..255 (the foul draw table 2648 fills at set-up) :=
Python's random 0..15 (seeded by seed*7919+13), because the savestate's table is one fixed table that every seed reads in
the same order (seeds 1..20 of the first logs: 7EEF's draws repeat from seed to seed, so their card and injury counts are
not independent samples of the table; the 20 halves there still check the clock, the cap and the budget).

D5C1 is entered 0 times in every recorded state (E011 is watched; the E010 quick records are friendlies, where
DS:9A3D = 0 closes the gate at DAC8-DAD0). No recorded state is a non-friendly quick result. This script runs the
published half-time savestate of E010-r0010 (sha256 3c7983fa4869d327..., a friendly) through the ORIGINAL second half
(0791:97D3..983C, the loop E010's emu_full_loop.py replays seed-exactly), with these DECLARED INPUTS (I3, a stand-in
for a non-friendly fixture, NOT a recorded non-friendly state):
  - DS:9A3D := 1                  (what A4A1 writes at A554 for a fixture byte +2 != 1)
  - DS:9B3A[0], DS:9B3A[1] := 2   (what A4A1 writes at A605 from DS:066C, the value DS:066B/066C index by DS:9A3D)
  - DS:7B62 := seed               (the main seed word; the savestate's own value is replaced to get N different halves)
The inherited resume set-up (emu_full_loop.py, E010) also writes, as WORDS through wr(): DS:830B (the kick-off slot; a word, so it
also clears DS:830C), DS:832A := 0x50, DS:9B55 := 1 (a word: it also clears DS:9B56), DS:0C20 := 0, DS:7C37 := 0, DS:8302 := 0
(each a word, so each also clears the next byte), and the stack frame word at SS:SP+4 := 0 and BP; the original stores are bytes
in several of these places. Two kinds of hook exist: observation hooks (the counters at D5C1, 7A43, 7EEF, 798D, 7B77, 7D56, 8062,
C88D, C5DC) only read registers and memory; emulation infrastructure hooks change registers: 214B:0723 (the key check) returns
'no key', the 000E wait family (05F6, 0572, 04F5, 045D) is skipped by returning, and interrupts are swallowed. Per seed it prints the entries of D5C1, 7A43, 7EEF, 798D, 7B77,
7D56, 8062, C88D and C5DC, DS:7B7E+side*10+k at the end, DS:9B3A and DS:8321. A summary follows.
The half-time savestate belongs to a friendly: the first half (not run) had none of these events (F005), so DS:7B84..87
and DS:8321 start at 0; this is stated, not assumed away.
The log is written to a new file out/quick-second-half-<UTC>.log (never overwritten).
"""
import hashlib
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from logs import open_new, stamped  # noqa: E402
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import *  # noqa: E402

SAV = ROOT / ".cache/dl/3c7983fa4869d327-E010-r0010-halftime.sav"
HOOKS = ["D5C1", "7A43", "7EEF", "798D", "7B77", "7D56", "8062", "C88D", "C5DC"]


def one(raw, seed, kind_nonfriendly=True, random_table=False):
    st = savestate.Savestate(raw)
    load = st.program().ds_base // 16 - 0x2581
    CODE, DS = load + 0x791, load + 0x2581
    SEG214B, SEG000E = load + 0x214B, load + 0x00E
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(0, bytes(st.mem[0x78:0x78 + 0x110000]))
    for r, v in ((UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, 0x6FF4), (UC_X86_REG_DS, DS), (UC_X86_REG_ES, DS),
                 (UC_X86_REG_CS, CODE)):
        mu.reg_write(r, v)

    def rd(off, n=2):
        return int.from_bytes(mu.mem_read(DS * 16 + off, n), "little")

    def wr(off, v, n=2):
        mu.mem_write(DS * 16 + off, v.to_bytes(n, "little"))

    counts = Counter()
    a43 = []

    def ret_ip(uc):
        sp = uc.reg_read(UC_X86_REG_SP)
        ss = uc.reg_read(UC_X86_REG_SS) * 16
        return int.from_bytes(uc.mem_read(ss + sp, 2), "little"), ss + sp

    def skip_keychk(uc, addr, size, data):
        sp = uc.reg_read(UC_X86_REG_SP)
        ss = uc.reg_read(UC_X86_REG_SS) * 16
        rip = int.from_bytes(uc.mem_read(ss + sp, 2), "little")
        rcs = int.from_bytes(uc.mem_read(ss + sp + 2, 2), "little")
        uc.reg_write(UC_X86_REG_SP, sp + 4)
        uc.reg_write(UC_X86_REG_AX, uc.reg_read(UC_X86_REG_AX) & 0xFF00)
        uc.reg_write(UC_X86_REG_CS, rcs)
        uc.reg_write(UC_X86_REG_EIP, rip)

    strays = []

    def skip_ret(nbytes):
        def hook(uc, addr, size, data):
            rip, spl = ret_ip(uc)
            rcs = int.from_bytes(uc.mem_read(spl + 2, 2), "little")
            strays.append(addr - SEG000E * 16)
            uc.reg_write(UC_X86_REG_SP, uc.reg_read(UC_X86_REG_SP) + 2 + nbytes)
            uc.reg_write(UC_X86_REG_CS, rcs)
            uc.reg_write(UC_X86_REG_EIP, rip)
        return hook

    mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
    mu.hook_add(UC_HOOK_CODE, skip_keychk, begin=SEG214B * 16 + 0x723, end=SEG214B * 16 + 0x723)
    for off, nb in ((0x5F6, 6), (0x572, 2), (0x4F5, 4), (0x45D, 4)):
        mu.hook_add(UC_HOOK_CODE, skip_ret(nb), begin=SEG000E * 16 + off, end=SEG000E * 16 + off)

    def at(name):
        def fn(uc, addr, size, data):
            counts[name] += 1
            if name == "7A43":
                ip, spl = ret_ip(uc)
                side = int.from_bytes(uc.mem_read(spl + 2, 2), "little") & 0xFF
                a43.append((side, rd(0x7B86 + side * 10, 1), rd(0x7B87 + side * 10, 1)))
        return fn

    for h in HOOKS:
        lin = CODE * 16 + int(h, 16)
        mu.hook_add(UC_HOOK_CODE, at(h), begin=lin, end=lin)

    # the E010 emulation's own resume constants (emu_full_loop.py, 9A32's tail)
    wr(0x830B, (0 if rd(0x831A, 1) == 0 else 11) + 10)
    wr(0x832A, 0x50)
    wr(0x9B55, 1)
    wr(0x0C20, 0)
    wr(0x7C37, 0)
    wr(0x8302, 0)
    start = {"9A3D": rd(0x9A3D, 1), "9B3A": (rd(0x9B3A, 1), rd(0x9B3B, 1)), "8321": rd(0x8321),
             "7B84": list(mu.mem_read(DS * 16 + 0x7B84, 4)), "seed": rd(0x7B62)}
    # declared inputs
    if kind_nonfriendly:
        wr(0x9A3D, 1, 1)
        wr(0x9B3A, 2, 1)
        wr(0x9B3B, 2, 1)
    wr(0x7B62, seed)
    table_sha = None
    if random_table:
        # DS:8337 + 1..255 := Python's random 0..15 (2648 draws rand(16) - 1 at each match set-up; the savestate's table
        # is one fixed table, read in the same order by every seed, so the seeds would not be independent samples of it)
        rng = random.Random(seed * 7919 + 13)
        body = bytes(rng.randrange(16) for _ in range(255))
        mu.mem_write(DS * 16 + 0x8337 + 1, body)
        table_sha = hashlib.sha256(body).hexdigest()[:16]
    sp = 0x6FF4
    mu.mem_write(0x70000 + sp + 4, (0).to_bytes(2, "little"))
    mu.reg_write(UC_X86_REG_BP, sp)
    mu.emu_start(CODE * 16 + 0x97D3, CODE * 16 + 0x983C, timeout=600 * 1000000)
    stats = [list(mu.mem_read(DS * 16 + 0x7B7E + s * 10, 10)) for s in (0, 1)]
    return {"seed": seed, "start": start, "table": table_sha, "counts": dict(counts), "a43": a43, "stats": stats,
            "9B3A": (rd(0x9B3A, 1), rd(0x9B3B, 1)), "8321": rd(0x8321), "831F": rd(0x831F), "831B": rd(0x831B),
            "score": (rd(0x9B3C, 1), rd(0x9B3D, 1)), "strays": strays}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    first = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    raw = SAV.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if not digest.startswith("3c7983fa4869d327"):
        raise SystemExit(f"{SAV}: sha256 {digest} is not E010-r0010's half-time savestate")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (HERE / "out").mkdir(exist_ok=True)
    log, logf = open_new(stamped(HERE / "out", "quick-second-half"))   # exclusive creation: launches never mix
    lines = []

    def say(s):
        print(s, flush=True)
        lines.append(s)
        logf.write(s + "\n")      # per line, flushed: a killed run leaves its seeds
        logf.flush()

    rt = len(sys.argv) > 3 and sys.argv[3] == "random-table"
    say(f"E027 quick second half, nonfriendly gate open by declared inputs (9A3D:=1, 9B3A:=2,2, 7B62:=seed"
        + (", DS:8337+1..255 := Python random 0..15 seeded by seed*7919+13" if rt else "")
        + f"); savestate sha256 {digest}; seeds {first}..{first + n - 1}")
    tot = Counter()
    for seed in range(first, first + n):
        r = one(raw, seed, random_table=rt)
        say(f"seed {seed}: table {r['table']} start {r['start']} counts {r['counts']} stats(side0) {r['stats'][0]} stats(side1) "
            f"{r['stats'][1]} 9B3A {r['9B3A']} 8321 {r['8321']} 831F {r['831F']} score {r['score']} "
            f"strays {r['strays']} 7A43 {r['a43']}")
        for k, v in r["counts"].items():
            tot[k] += v
        tot["halves"] += 1
        for s in (0, 1):
            tot[f"booked_s{s}"] += r["stats"][s][7]
            tot[f"sentoff_s{s}"] += r["stats"][s][8]
            tot[f"injured_s{s}"] += r["stats"][s][9]
    say("TOTAL " + str(dict(tot)))
    print(f"log: {log}")


if __name__ == "__main__":
    main()
