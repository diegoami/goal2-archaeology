"""E024 (rework 3): the ORIGINAL 0791:D47E, unhooked in Unicorn, on synthetic fixtures: how many B19D rounds?

    python3 -B experiments/E024-computer-managers/probe_d47e.py [opponents per competition code]   (default 100)

On E010-r0001's half-time memory, for competition codes 0 (a friendly), 4 and 10 (both in the set DS:693A,
4 and 8..203) and for N opponents (country 27 against countries 1..N+1 except 27), the 8-byte fixture record
(+0/+1 scores 0, +2 the code, +4 country 27, +6 the opponent) is passed to the original D47E, with [DS:A923]
bytes +0x26 = 4 and +0x40 = 0. A read-only code hook at the entry of 0791:B19D logs each call's argument. The
seed word DS:7B62 is NOT varied: D47E's set-up leaves the same seed whatever it held (a first version of this
script varied it and every case gave the same record; its log, probe-d47e-20261013T170827Z.log, is kept), so
the variation is the opponent.
Per code it prints the B19D call argument lists, and for the cases with a second round the final scores and
the result byte +3 (2 = draw; otherwise 1 when the second team scored more, else 0; a coin when level).
Log: new file out/probe-d47e-<UTC time>.log (never overwritten), echoed.
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "experiments/E010-q010-quick-engine"))
import check_model  # noqa: E402
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import (UC_X86_REG_IP, UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_DS,  # noqa: E402
                               UC_X86_REG_ES, UC_X86_REG_CS, UC_X86_REG_BP)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
MEM = savestate.MEM_BASE
lines = []


def out(s):
    lines.append(s)
    print(s, flush=True)


record = json.loads((ROOT / "runs/E010/E010-r0001.json").read_text())
entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
st = savestate.Savestate(check_model.halftime_sav(entry))
prog = st.program()
DSSEG = prog.ds_base // 16
CODE = DSSEG - 0x2581 + 0x791
FIX = 0x7E000          # linear address of the synthetic fixture record (inside the scratch stack segment)
a923 = st.ds_bytes(0xA923, 4)
ctx = int.from_bytes(a923[0:2], "little") + int.from_bytes(a923[2:4], "little") * 16


def run(code, opp):
    mem = bytearray(st.mem)
    mem[MEM + ctx + 0x26] = 4
    mem[MEM + ctx + 0x40] = 0
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(0, bytes(mem[MEM:MEM + 0x110000]))
    mu.mem_write(FIX, bytes([0, 0, code, 0]) + (27).to_bytes(2, "little") + opp.to_bytes(2, "little"))
    sp = 0x6FF0
    for r, v in ((UC_X86_REG_SS, 0x7000), (UC_X86_REG_SP, sp), (UC_X86_REG_DS, DSSEG), (UC_X86_REG_ES, DSSEG),
                 (UC_X86_REG_CS, CODE), (UC_X86_REG_BP, 0)):
        mu.reg_write(r, v)
    mu.mem_write(0x70000 + sp, (0x10).to_bytes(2, "little") + CODE.to_bytes(2, "little")
                 + (0).to_bytes(2, "little") + (FIX // 16).to_bytes(2, "little"))
    calls = []

    def hook(uc, addr, size, data):
        ss = uc.reg_read(UC_X86_REG_SS) * 16
        spv = uc.reg_read(UC_X86_REG_SP)
        calls.append(int.from_bytes(uc.mem_read(ss + spv + 2, 2), "little"))
    mu.hook_add(UC_HOOK_CODE, hook, begin=CODE * 16 + 0xB19D, end=CODE * 16 + 0xB19D)
    mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
    mu.emu_start(CODE * 16 + 0xD47E, CODE * 16 + 0x10, timeout=20 * 1000000, count=3000000)
    reached = mu.reg_read(UC_X86_REG_CS) * 16 + mu.reg_read(UC_X86_REG_IP) == CODE * 16 + 0x10
    return calls, bytes(mu.mem_read(FIX, 8)), reached


opps = [x for x in range(1, N + 2) if x != 27][:N]
for code in (0, 4, 10):
    byargs, finals, firsts = Counter(), Counter(), Counter()
    for opp in opps:
        calls, rec, reached = run(code, opp)
        assert reached, f"D47E did not return to the sentinel (code {code}, opponent {opp})"
        byargs[tuple(calls)] += 1
        finals[(rec[0], rec[1], rec[3], len(calls))] += 1
    out(f"competition code {code}, opponents {opps[0]}..{opps[-1]} (not 27), {len(opps)} fixtures: "
        f"B19D call argument lists {dict((str(list(k)), v) for k, v in byargs.items())}")
    out(f"   final (score0, score1, +3, B19D calls) -> count {dict((str(k), v) for k, v in sorted(finals.items()))}")
fn = HERE / "out" / f"probe-d47e-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines) + "\n")
print("log:", fn)
