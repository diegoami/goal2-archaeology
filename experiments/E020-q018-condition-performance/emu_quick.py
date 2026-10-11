#!/usr/bin/env python3
"""The original binary's quick-result second half in Unicorn, on an edited half-time savestate.

`run_half(savestate_bytes)` emulates `0791:97D3..983C` (the tick loop: D733, 970C, 054C, 0712, 9372
as real guest code) exactly as T24's `experiments/E010-q010-quick-engine/emu_full_loop.py` does
(same interventions: `214B:0723` returns "no key", interrupts swallowed, the `000E` wait family
skipped and LOGGED in `strays`, which must stay empty; the half-time resume writes of the model's
own constants), but as a function of the savestate bytes so a caller can edit the players first
(E020: +0xC and +0xE of literal player words). Returns the final score bytes, the main seed, the
number of main-seed draws and the strays. Nothing of the guest's code or data is changed here.

The inputs are the E010 half-time savestates (release E010, sha256-checked by the caller)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import (UC_X86_REG_SS, UC_X86_REG_SP, UC_X86_REG_DS, UC_X86_REG_ES,  # noqa: E402
                               UC_X86_REG_CS, UC_X86_REG_BP, UC_X86_REG_AX, UC_X86_REG_EIP)

LOOP_START, LOOP_END = 0x97D3, 0x983C       # 0791: the tick loop body and its end (seg_0791_16.asm)
KEY_THUNK = 0x723                           # 214B:0723, the BIOS keypressed thunk
WAIT_FAMILY = ((0x5F6, 6), (0x572, 2), (0x4F5, 4), (0x45D, 4))   # 000E, (offset, ret bytes)
RNG = (0x6B1, 0x6D0, 0x6FA)                 # 214B wrappers around 0688


def run_half(data, timeout_s=600):
    st = savestate.Savestate(data)
    load = st.program().ds_base // 16 - 0x2581
    code, ds = load + 0x791, load + 0x2581
    seg214b, seg000e = load + 0x214B, load + 0x00E
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(0, bytes(st.mem[0x78:0x78 + 0x110000]))
    mu.reg_write(UC_X86_REG_SS, 0x7000)
    mu.reg_write(UC_X86_REG_SP, 0x6FF4)
    mu.reg_write(UC_X86_REG_DS, ds)
    mu.reg_write(UC_X86_REG_ES, ds)
    mu.reg_write(UC_X86_REG_CS, code)
    draws = [0]
    strays = []

    def rd(off, n=2):
        return int.from_bytes(mu.mem_read(ds * 16 + off, n), "little")

    def wr(off, v):
        mu.mem_write(ds * 16 + off, v.to_bytes(2, "little"))

    def count_draw(uc, addr, size, user):
        draws[0] += 1

    def ret_addr(uc):
        sp = uc.reg_read(UC_X86_REG_SP)
        ss = uc.reg_read(UC_X86_REG_SS) * 16
        return (int.from_bytes(uc.mem_read(ss + sp + 2, 2), "little"),
                int.from_bytes(uc.mem_read(ss + sp, 2), "little"))

    def skip_keychk(uc, addr, size, user):
        sp = uc.reg_read(UC_X86_REG_SP)
        rcs, rip = ret_addr(uc)
        uc.reg_write(UC_X86_REG_SP, sp + 4)
        uc.reg_write(UC_X86_REG_AX, uc.reg_read(UC_X86_REG_AX) & 0xFF00)
        uc.reg_write(UC_X86_REG_CS, rcs)
        uc.reg_write(UC_X86_REG_EIP, rip)

    def skip_ret(nbytes):
        def hook(uc, addr, size, user):
            seg, off = ret_addr(uc)
            strays.append("000E:%04X from %04X:%04X" % (addr - seg000e * 16, seg, off))
            uc.reg_write(UC_X86_REG_SP, uc.reg_read(UC_X86_REG_SP) + 2 + nbytes)
            uc.reg_write(UC_X86_REG_CS, seg)
            uc.reg_write(UC_X86_REG_EIP, off)
        return hook

    mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
    mu.hook_add(UC_HOOK_CODE, skip_keychk, begin=seg214b * 16 + KEY_THUNK, end=seg214b * 16 + KEY_THUNK)
    for off, nb in WAIT_FAMILY:
        mu.hook_add(UC_HOOK_CODE, skip_ret(nb), begin=seg000e * 16 + off, end=seg000e * 16 + off)
    for w in RNG:
        mu.hook_add(UC_HOOK_CODE, count_draw, begin=seg214b * 16 + w, end=seg214b * 16 + w)
    # 9A32's tail and the resume flags, as emu_full_loop.py (the quick model's own resume constants)
    wr(0x830B, (0 if rd(0x831A, 1) == 0 else 11) + 10)
    wr(0x832A, 0x50)
    wr(0x9B55, 1)
    wr(0x0C20, 0)
    wr(0x7C37, 0)
    wr(0x8302, 0)
    sp = 0x6FF4
    mu.mem_write(0x70000 + sp + 4, (0).to_bytes(2, "little"))
    mu.reg_write(UC_X86_REG_BP, sp)
    mu.emu_start(code * 16 + LOOP_START, code * 16 + LOOP_END, timeout=timeout_s * 1000000)
    return {"score": (rd(0x9B3C, 1), rd(0x9B3D, 1)), "seed": rd(0x7B62), "draws": draws[0],
            "minute_831F": rd(0x831F), "strays": strays}
