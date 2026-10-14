"""E024 (rework 1): does the ORIGINAL 0791:B11F always bench an unavailable starter? (F024 guarantee test)

    python3 -B experiments/E024-computer-managers/probe_stays.py

On E010-r0001's half-time state, country = DS:9B34:
case 1: every bench player (slots 12..20) gets energy 0 (+0xE) and the player of slot 3 gets energy 0 (injured);
case 2: only the slot-3 player gets energy 0 (a bench exists);
case 3: tiredness only: every starter's energy 1, every bench player's 32 (nobody injured).
Prints the eleven before and after the original B11F, and whether the injured starter is still among them.
Log: new file out/probe-stays-<UTC time>.log (never overwritten), echoed.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "experiments/E010-q010-quick-engine"))
import check_model  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR  # noqa: E402
from unicorn.x86_const import (UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_DS, UC_X86_REG_ES,  # noqa: E402
                               UC_X86_REG_CS, UC_X86_REG_BP)

MEM = savestate.MEM_BASE
lines = []


def out(s):
    lines.append(s)
    print(s, flush=True)


def b11f(st, mem, c):
    prog = st.program()
    seg = prog.ds_base // 16 - 0x2581 + 0x791
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(0, bytes(mem[MEM:MEM + 0x110000]))
    sp = 0x6FF0
    for r, v in ((UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, sp), (UC_X86_REG_DS, prog.ds_base // 16),
                 (UC_X86_REG_ES, prog.ds_base // 16), (UC_X86_REG_CS, seg), (UC_X86_REG_BP, 0)):
        mu.reg_write(r, v)
    mu.mem_write(0x70000 + sp, (0x10).to_bytes(2, "little") + seg.to_bytes(2, "little") + c.to_bytes(2, "little"))
    mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
    mu.emu_start(seg * 16 + 0xB11F, seg * 16 + 0x10, timeout=20 * 1000000, count=2000000)
    return mu


record = json.loads((ROOT / "runs/E010/E010-r0001.json").read_text())
entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
st = savestate.Savestate(check_model.halftime_sav(entry))
pa = players.far_pointer(st, players.PLAYERS_PTR)[2]
ca = players.far_pointer(st, players.COUNTRIES_PTR)[2]
c = st.ds_word(0x9B34)


def squad(mem_or_mu, mu=False):
    if mu:
        raw = bytes(mem_or_mu.mem_read(ca + 0xBF * c, 40))
    else:
        raw = bytes(mem_or_mu[MEM + ca + 0xBF * c:MEM + ca + 0xBF * c + 40])
    return [int.from_bytes(raw[2 * i:2 * i + 2], "little") for i in range(20)]


for name in ("1 injured starter, every bench player injured", "2 injured starter, bench available",
             "3 tiredness only (starters energy 1, bench 32)"):
    mem = bytearray(st.mem)
    sq = squad(mem)
    victim = sq[2]
    if name[0] == "1":
        for w in sq[11:]:
            mem[MEM + pa + 20 * w + 0xE] = 0
        mem[MEM + pa + 20 * victim + 0xE] = 0
    elif name[0] == "2":
        mem[MEM + pa + 20 * victim + 0xE] = 0
    else:
        for w in sq[:11]:
            mem[MEM + pa + 20 * w + 0xE] = 1
        for w in sq[11:]:
            mem[MEM + pa + 20 * w + 0xE] = 32
    mu = b11f(st, mem, c)
    after = squad(mu, True)
    out(f"case {name}: country {c}; eleven before {sorted(sq[:11])}; after {sorted(after[:11])}; "
        f"slot-3 player {victim} {'STILL among the eleven' if victim in after[:11] else 'out of the eleven'}; "
        f"players changed {sorted(set(sq[:11]) ^ set(after[:11]))}")
fn = HERE / "out" / f"probe-stays-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines) + "\n")
print("log:", fn)
