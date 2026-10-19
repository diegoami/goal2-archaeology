"""Ball, passing and shooting routines from the segment0791 listing (T64).

Calls, including calls between routines in this module, remain guest calls.
Only routines whose complete assembly has been read are registered here.
"""
from . import Registry
from .guest import call
from .mem import s16
from .runtime import Regs
from .geometry import cbw, mul, imul

PORTS = Registry("ball", "ball, passing and shooting (T64)")
M16 = 0xFFFF


def local8(mem, r, offset):
    return mem.u8(mem.ss_lin((r.bp + offset) & M16))


def local16(mem, r, offset):
    return mem.u16(mem.ss_lin((r.bp + offset) & M16))


def load_local_pitch(mem, r):
    r.di = local16(mem, r, -0xD)
    r.es = local16(mem, r, -0xB)


@PORTS.port("0791:2FB1", ret="ret")
def find_nearest_to_ball(mem, variant):
    """2FB1–30E9: nearest available slot and nearest goal-side slot per side."""
    r = Regs(mem)
    r.enter(0xE)                                               # 2FB1–2FB4
    r.local8(-1, 0)                                            # 2FB7
    while True:
        r.al = local8(mem, r, -1)
        cbw(r)
        r.di = r.ax
        mem.wds8((0x8311 + r.di) & M16, 0, "0791:2FC6")
        r.al = local8(mem, r, -1)
        cbw(r)
        r.di = r.ax
        mem.wds8((0x830F + r.di) & M16, 0, "0791:2FD1")
        r.local16(-5, 100)                                     # 2FD6
        r.local16(-7, 100)                                     # 2FDB
        r.local16(-3, 2)                                       # 2FE0
        while True:
            r.al = local8(mem, r, -1)
            cbw(r)
            r.di = r.ax
            r.al = mem.ds8((0x668 + r.di) & M16)
            r.ah = 0
            r.ax = r.ax + local16(mem, r, -3)
            r.dx = 0x16
            mul(r, r.dx)
            r.di = r.ax + 0x80E8
            r.local16(-0xD, r.di)                              # 3004
            r.local16(-0xB, mem.DS)                             # 3007
            load_local_pitch(mem, r)
            r.store(stack=True)
            yield call("0791:2956", r.es, r.di, ret_to="0791:3013", far=True)
            r = Regs(mem, resumed=True)
            if r.al == 0:
                r.al = mem.ds8(0x830B)
                load_local_pitch(mem, r)
                if r.al != mem.u8(mem.addr(r.es, r.di + 6)):
                    load_local_pitch(mem, r)
                    if mem.u8(mem.addr(r.es, r.di + 0x12)) != 0xD:
                        r.al = mem.ds8(0x82F6)
                        cbw(r)
                        r.dx = r.ax
                        load_local_pitch(mem, r)
                        r.al = mem.u8(mem.addr(r.es, r.di))
                        cbw(r)
                        r.ax = r.ax - r.dx
                        if s16(r.ax) < 0:
                            r.ax = -r.ax
                        r.cx = r.ax
                        r.al = mem.ds8(0x82F7)
                        cbw(r)
                        r.dx = r.ax
                        load_local_pitch(mem, r)
                        r.al = mem.u8(mem.addr(r.es, r.di + 1))
                        cbw(r)
                        r.ax = r.ax - r.dx
                        if s16(r.ax) < 0:
                            r.ax = -r.ax
                        r.ax = r.ax + r.cx
                        r.local16(-9, r.ax)                    # 3065
                        if r.ax < local16(mem, r, -5):
                            load_local_pitch(mem, r)
                            r.dx = (r.dx & 0xFF00) | mem.u8(mem.addr(r.es, r.di + 6))
                            r.al = local8(mem, r, -1)
                            cbw(r)
                            r.di = r.ax
                            mem.wds8((0x8311 + r.di) & M16, r.dx & 0xFF, "0791:307D")
                            r.ax = local16(mem, r, -9)
                            r.local16(-5, r.ax)                 # 3084
                        load_local_pitch(mem, r)
                        r.store(stack=True)
                        yield call("0791:2BE5", r.es, r.di, ret_to="0791:3090", far=True)
                        r = Regs(mem, resumed=True)
                        cbw(r)
                        r.dx = r.ax
                        r.al = mem.ds8(0x82F7)
                        cbw(r)
                        imul(r, r.dx)
                        r.push(r.ax)                           # 3099: live across the next call
                        load_local_pitch(mem, r)
                        r.store(stack=True)
                        yield call("0791:2BE5", r.es, r.di, ret_to="0791:30A3", far=True)
                        r = Regs(mem, resumed=True)
                        cbw(r)
                        r.dx = r.ax
                        load_local_pitch(mem, r)
                        r.al = mem.u8(mem.addr(r.es, r.di + 1))
                        cbw(r)
                        imul(r, r.dx)
                        r.dx = mem.u16(mem.ss_lin(r.sp))        # 30B0 pop dx
                        r.sp = r.sp + 2
                        if s16(r.ax) < s16(r.dx):
                            r.ax = local16(mem, r, -9)
                            if r.ax < local16(mem, r, -7):
                                load_local_pitch(mem, r)
                                r.dx = (r.dx & 0xFF00) | mem.u8(mem.addr(r.es, r.di + 6))
                                r.al = local8(mem, r, -1)
                                cbw(r)
                                r.di = r.ax
                                mem.wds8((0x830F + r.di) & M16, r.dx & 0xFF, "0791:30CA")
                                r.ax = local16(mem, r, -9)
                                r.local16(-7, r.ax)             # 30D1
            if local16(mem, r, -3) == 0xB:
                break
            r.local16(-3, local16(mem, r, -3) + 1)               # 2FE7
        if local8(mem, r, -1) == 1:
            break
        r.local8(-1, local8(mem, r, -1) + 1)                    # 2FBD
    r.leave()
    r.store()


@PORTS.port("0791:30EA", ret="retf 6")
def slot_in_record_side(mem, variant):
    """30EA–310E: side base selected by2974 plus the caller's relative slot."""
    off, seg, index = mem.arg(0), mem.arg(1), mem.arg(2)
    r = Regs(mem)
    r.enter(2)
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:2974", r.es, r.di, ret_to="0791:30F9", far=True)
    r = Regs(mem, resumed=True)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x668 + r.di) & M16)
    r.ah = 0
    r.ax = r.ax + index
    r.local16(-2, r.ax)
    r.leave()
    r.store()
