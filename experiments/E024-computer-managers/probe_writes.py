"""E024 (rework 1): what the ORIGINAL routines write, by running them unhooked in Unicorn on synthetic input.

    python3 -B experiments/E024-computer-managers/probe_writes.py [scenarios per team]

A. 0791:B11F on the ten E010 half-time savestates (both teams, scenario 0 as saved plus S seeded patches as in
   diff_b11f.py): every guest byte that differs after the call is classified: squad words of the country,
   +6 of the country's squad players, DS:99A2 (the 14-byte table), the scratch stack (SS 0x7000), anything else.
   "anything else" must be empty for F024's statement that B11F exchanges squad words and sets +6 only.
B. 1771:33CD and 1771:3431 on one player of E010-r0001: for every position (+6) 0..13, skill profile (+5)
   in {1, 10, 16}, and initial +0xF in {0x00, 0x08, 0x80, 0x88, 0xFF}, the +0xF the original leaves.
C. 1771:34E7 (country) on the same state: which bytes it writes (same classification, plus all +0xF).
Log: a new file out/probe-writes-<UTC time>.log (never overwritten), echoed.
"""
import json
import random
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "runtime/model"))
sys.path.insert(0, str(ROOT / "experiments/E010-q010-quick-engine"))
import check_model  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR  # noqa: E402
from unicorn.x86_const import (UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_DS, UC_X86_REG_ES,  # noqa: E402
                               UC_X86_REG_CS, UC_X86_REG_BP)

S = int(sys.argv[1]) if len(sys.argv) > 1 else 20
MEM = savestate.MEM_BASE
lines = []


def out(s):
    lines.append(s)
    print(s, flush=True)


def call_far(st, mem, seg_name, entry, arg):
    """Run the far routine CODE:entry (segment 0791 or 1771) with one word argument; returns the Uc."""
    prog = st.program()
    load = prog.ds_base // 16 - 0x2581
    seg = {"0791": load + 0x791, "1771": load + 0x1771}[seg_name]
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(0, bytes(mem[MEM:MEM + 0x110000]))
    sp = 0x6FF0
    for r, v in ((UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, sp), (UC_X86_REG_DS, prog.ds_base // 16),
                 (UC_X86_REG_ES, prog.ds_base // 16), (UC_X86_REG_CS, seg), (UC_X86_REG_BP, 0)):
        mu.reg_write(r, v)
    ret_off = 0x0010
    mu.mem_write(0x70000 + sp, ret_off.to_bytes(2, "little") + seg.to_bytes(2, "little") + arg.to_bytes(2, "little"))
    mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
    mu.emu_start(seg * 16 + entry, seg * 16 + ret_off, timeout=20 * 1000000, count=2000000)
    return mu


def squad_of(mem, ca, c):
    b = MEM + ca + 0xBF * c
    return [int.from_bytes(mem[b + 2 * i:b + 2 * i + 2], "little") for i in range(20)]


def classify(before, after, st, c, sq):
    pa = players.far_pointer(st, players.PLAYERS_PTR)[2]
    ca = players.far_pointer(st, players.COUNTRIES_PTR)[2]
    ds = st.program().ds_base
    cnt = Counter()
    other = []
    diffs = []
    for off in range(0, 0x110000, 256):                      # chunks first: only differing chunks are scanned
        if before[off:off + 256] != after[off:off + 256]:
            diffs += [i for i in range(off, off + 256) if before[i] != after[i]]
    for i in diffs:
        if 0x70000 <= i < 0x80000:
            cnt["scratch stack"] += 1
        elif ca + 0xBF * c <= i < ca + 0xBF * c + 40:
            cnt["squad words of the country"] += 1
        elif any(pa + 20 * w + 6 == i for w in sq):
            cnt["+6 of a squad player"] += 1
        elif any(pa + 20 * w + 0xF == i for w in sq):
            cnt["+0xF of a squad player"] += 1
        elif ds + 0x99A2 <= i < ds + 0x99A2 + 14:
            cnt["DS:99A2"] += 1
        else:
            cnt["OTHER"] += 1
            other.append(hex(i))
    return cnt, other


def perturb(mem, st, c, rng):
    pa = players.far_pointer(st, players.PLAYERS_PTR)[2]
    for w in squad_of(mem, players.far_pointer(st, players.COUNTRIES_PTR)[2], c):
        b = MEM + pa + 20 * w
        if rng.random() < 0.12:
            mem[b + 0xE] = 0
        elif rng.random() < 0.25:
            mem[b + 0xE] = rng.randint(1, 32)
        if rng.random() < 0.06:
            mem[b + 0x10] |= 1 << rng.choice((7, 5, 2))
        if rng.random() < 0.15:
            mem[b + 6] = rng.randint(0, 13)
        if rng.random() < 0.08:
            mem[b + 7] = rng.randint(0, 13)


records = sorted((ROOT / "runs/E010").glob("E010-r*.json"))
total = Counter()
others = []
st1 = None
for p in records:
    record = json.loads(p.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    st = savestate.Savestate(check_model.halftime_sav(entry))
    st1 = st1 or st
    ca = players.far_pointer(st, players.COUNTRIES_PTR)[2]
    for team in (0, 1):
        c = st.ds_word(0x9B34 + 2 * team)
        for scen in range(S + 1):
            mem = bytearray(st.mem)
            if scen:
                perturb(mem, st, c, random.Random(f"w/{record['run_id']}/{team}/{scen}"))
            sq = squad_of(mem, ca, c)
            mu = call_far(st, mem, "0791", 0xB11F, c)
            after = bytearray(mu.mem_read(0, 0x110000))
            cnt, other = classify(bytes(mem[MEM:MEM + 0x110000]), after, st, c, sq)
            total.update(cnt)
            others += other
out("A. bytes the original 0791:B11F changed, over all cases (class: count):")
for k in sorted(total):
    out(f"   {k}: {total[k]}")
out(f"   OTHER addresses: {sorted(set(others))[:20]}")

# B. 33CD and 3431 on one player
st = st1
pa = players.far_pointer(st, players.PLAYERS_PTR)[2]
ca = players.far_pointer(st, players.COUNTRIES_PTR)[2]
c = st.ds_word(0x9B34)
w = squad_of(st.mem, ca, c)[3]
out(f"B. player {w} of country {c} of E010-r0001's state; initial +0xF -> +0xF after the original routine")
for name, entry in (("1771:33CD", 0x33CD), ("1771:3431", 0x3431)):
    for pos in range(14):
        for prof in (1, 10, 16):
            res = []
            for f0 in (0x00, 0x08, 0x80, 0x88, 0xFF):
                mem = bytearray(st.mem)
                b = MEM + pa + 20 * w
                mem[b + 6], mem[b + 5], mem[b + 0xF] = pos, prof, f0
                mu = call_far(st, mem, "1771", entry, w)
                res.append((f0, bytes(mu.mem_read(pa + 20 * w + 0xF, 1))[0]))
            if name == "1771:33CD" and pos == 0 and prof == 1 or name == "1771:3431":
                out(f"   {name} pos {pos:2d} +5={prof:2d}: " + " ".join(f"{a:02X}->{b:02X}" for a, b in res))
# C. 34E7
mem = bytearray(st.mem)
sq = squad_of(mem, ca, c)
mu = call_far(st, mem, "1771", 0x34E7, c)
after = bytearray(mu.mem_read(0, 0x110000))
cnt, other = classify(bytes(mem[MEM:MEM + 0x110000]), after, st, c, sq)
out(f"C. 1771:34E7({c}) changed: {dict(cnt)} other {other[:10]}")
d = HERE / "out"
fn = d / f"probe-writes-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines) + "\n")
print("log:", fn)
