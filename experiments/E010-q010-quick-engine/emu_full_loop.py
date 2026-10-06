#!/usr/bin/env python3
"""Unicorn ground truth (T24 round 3): the WHOLE second half (minutes 46..91) of the quick
match, from the published half-time savestate of E010-r0010 (sha256
3c7983fa4869d3278fe9f1f6140e5ca1b84f602e97b5862f547c6332d086e1e6), running the ORIGINAL
binary's 0791:97D0 tick loop — D733, 970C, 054C, 0712, 9372 all as real guest code.
Interventions: 214B:0723 (the BIOS key check) stubbed `no key`, interrupts swallowed, the
000E wait family (05F6/0572/04F5/045D) skipped (it never runs inside a quick half — the
skip log stays empty). The result reproduces the original's recorded trajectory exactly:
3617 draws, final DS:7B62 = 0x543a, score [0,1] — the record's own full-time seed.

Generates the per-minute table emu-r0010-secondhalf-minbymin.txt (this directory).
Requirements: python3-unicorn (import unicorn), the half-time savestate (downloaded by
check_model.py into .cache/dl/, or scratch/e010-halftime/)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import *  # noqa: E402

st = savestate.Savestate(open(ROOT / ".cache/dl/3c7983fa4869d327-E010-r0010-halftime.sav" if (ROOT / ".cache/dl/3c7983fa4869d327-E010-r0010-halftime.sav").is_file() else ROOT / "scratch/e010-halftime/E010-r0010-halftime.sav",
                              "rb").read())
load = st.program().ds_base // 16 - 0x2581
CODE, DS = load + 0x791, load + 0x2581
SEG214B, SEG000E = load + 0x214B, load + 0x00E

mu = Uc(UC_ARCH_X86, UC_MODE_16)
mu.mem_map(0, 0x110000)
mu.mem_write(0, bytes(st.mem[0x78:0x78 + 0x110000]))
mu.reg_write(UC_X86_REG_SS, 0x7000)
mu.reg_write(UC_X86_REG_SP, 0x6FF4)
mu.reg_write(UC_X86_REG_DS, DS)
mu.reg_write(UC_X86_REG_ES, DS)
mu.reg_write(UC_X86_REG_CS, CODE)

draws = []
minutes = []
strays = []


def rd(off, n=2):
    return int.from_bytes(mu.mem_read(DS * 16 + off, n), "little")


def wr(off, v):
    mu.mem_write(DS * 16 + off, v.to_bytes(2, "little"))


def ret_addr(uc):
    sp = uc.reg_read(UC_X86_REG_SP)
    ss = uc.reg_read(UC_X86_REG_SS) * 16
    off = int.from_bytes(uc.mem_read(ss + sp, 2), "little")
    seg = int.from_bytes(uc.mem_read(ss + sp + 2, 2), "little")
    return seg, off, sp


WRAPPER = {0x6B1: "06B1", 0x6D0: "06D0", 0x6FA: "06FA"}


def wrapper_hook(uc, addr, size, data):
    seg, off, _ = ret_addr(uc)
    sp = uc.reg_read(UC_X86_REG_SP)
    ss = uc.reg_read(UC_X86_REG_SS) * 16
    n = int.from_bytes(uc.mem_read(ss + sp + 4, 2), "little")
    seed = rd(0x7B62)
    step = (seed * 0x7ABD + 0x1B0F) & 0xFFFF
    draws.append({"caller": "%04X:%04X" % (seg, off), "wrapper": WRAPPER[addr - SEG214B * 16],
                  "n": n, "value": (((step * n) & 0xFFFFFFFF) >> 16) + 1})


def skip_keychk(uc, addr, size, data):
    sp = uc.reg_read(UC_X86_REG_SP)
    ss = uc.reg_read(UC_X86_REG_SS) * 16
    rip = int.from_bytes(uc.mem_read(ss + sp, 2), "little")
    rcs = int.from_bytes(uc.mem_read(ss + sp + 2, 2), "little")
    uc.reg_write(UC_X86_REG_SP, sp + 4)
    uc.reg_write(UC_X86_REG_AX, uc.reg_read(UC_X86_REG_AX) & 0xFF00)
    uc.reg_write(UC_X86_REG_CS, rcs)
    uc.reg_write(UC_X86_REG_EIP, rip)   # 16-bit mode: EIP is the OFFSET in CS


def skip_ret(nbytes):
    def hook(uc, addr, size, data):
        seg, off, _ = ret_addr(uc)
        strays.append({"routine": "000E:%04X" % (addr - SEG000E * 16),
                       "caller": "%04X:%04X" % (seg, off)})
        uc.reg_write(UC_X86_REG_SP, uc.reg_read(UC_X86_REG_SP) + 2 + nbytes)
        uc.reg_write(UC_X86_REG_CS, seg)
        uc.reg_write(UC_X86_REG_EIP, off)
    return hook


mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
mu.hook_add(UC_HOOK_CODE, skip_keychk, begin=SEG214B * 16 + 0x723, end=SEG214B * 16 + 0x723)
for off, nb in ((0x5F6, 6), (0x572, 2), (0x4F5, 4), (0x45D, 4)):
    mu.hook_add(UC_HOOK_CODE, skip_ret(nb), begin=SEG000E * 16 + off, end=SEG000E * 16 + off)
for w in (0x6B1, 0x6D0, 0x6FA):
    mu.hook_add(UC_HOOK_CODE, wrapper_hook, begin=SEG214B * 16 + w, end=SEG214B * 16 + w)
mu.hook_add(UC_HOOK_CODE,
            lambda uc, a, s, d: minutes.append({"at_draw": len(draws), "831f": rd(0x831F),
                                                "831b": rd(0x831B), "seed": "%04x" % rd(0x7B62)}),
            begin=CODE * 16 + 0xD733, end=CODE * 16 + 0xD733)

# 9A32's tail: kick-off slot and the 0x50 restart (the model's own resume constants)
wr(0x830B, (0 if rd(0x831A, 1) == 0 else 11) + 10)
wr(0x832A, 0x50)
wr(0x9B55, 1)
wr(0x0C20, 0)
wr(0x7C37, 0)
wr(0x8302, 0)

# the loop body 97D3..983C with 97D0's frame (guard [bp+4]=0: run to the half's end)
sp = 0x6FF4
mu.mem_write(0x70000 + sp + 4, (0).to_bytes(2, "little"))
mu.reg_write(UC_X86_REG_BP, sp)
mu.emu_start(CODE * 16 + 0x97D3, CODE * 16 + 0x983C, timeout=600 * 1000000)
print("loop done: 831F=%d 831B=%d seed=%04x draws=%d score=[%d,%d]" %
      (rd(0x831F), rd(0x831B), rd(0x7B62), len(draws), rd(0x9B3C, 1), rd(0x9B3D, 1)), flush=True)
for m in minutes:
    print("  minute %2d (831B=%2d) at draw %4d seed %s" % (m["831f"], m["831b"], m["at_draw"], m["seed"]))
out = ROOT / "scratch/t24/emu4-draws.json"
out.write_text(json.dumps({"draws": draws, "minutes": minutes, "strays": strays}))
print("strays:", strays[:10])
print("draw log:", out)
