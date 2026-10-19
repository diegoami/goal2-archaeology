"""Ball, passing and shooting routines from the segment0791 listing (T64).

Calls, including calls between routines in this module, remain guest calls.
Only routines whose complete assembly has been read are registered here.
"""
from . import Registry
from .guest import call
from .mem import s8, s16
from .runtime import Regs
from .geometry import cbw, cwd, mul, imul

PORTS = Registry("ball", "ball, passing and shooting (T64)")
M16 = 0xFFFF


def local8(mem, r, offset):
    return mem.u8(mem.ss_lin((r.bp + offset) & M16))


def local16(mem, r, offset):
    return mem.u16(mem.ss_lin((r.bp + offset) & M16))


def load_local_pitch(mem, r):
    r.di = local16(mem, r, -0xD)
    r.es = local16(mem, r, -0xB)


def pop_word(mem, r):
    value = mem.u16(mem.ss_lin(r.sp))
    r.sp = r.sp + 2
    return value


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


@PORTS.port("0791:3323", ret="retf 4")
def pass_to_selected_receiver(mem, variant):
    """3323–333C: select a receiver, then pass with the full returned AX."""
    off, seg = mem.arg(0), mem.arg(1)
    r = Regs(mem)
    r.enter()
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:3111", seg, off, ret_to="0791:332F", far=True)
    r = Regs(mem, resumed=True)
    receiver = r.ax
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:384C", receiver, seg, off, ret_to="0791:3339", far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:3BEE", ret="retf 4")
def choose_pass_or_long_ball(mem, variant):
    """3BEE–3C1D: existing offside goes to82EB without drawing."""
    off, seg = mem.arg(0), mem.arg(1)
    r = Regs(mem)
    r.enter()
    if mem.ds8(0x830E) != 0:
        r.store(stack=True)
        yield call("0791:82EB", ret_to="0791:3BFB", far=False)
    else:
        r.store(stack=True)
        yield call("214B:06FA", ret_to="0791:3C02", far=True)
        r = Regs(mem, resumed=True)
        target, ret = ("0791:3B15", "0791:3C0F") if r.al else ("0791:3323", "0791:3C1A")
        r.es, r.di = seg, off
        r.store(stack=True)
        yield call(target, seg, off, ret_to=ret, far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:3C20", ret="ret 2")
def count_on_target(mem, variant):
    """3C20–3C3C: increment the side's statistic only outside8326 mode."""
    side = mem.arg(0)
    r = Regs(mem)
    r.enter()
    if mem.ds8(0x8326) == 0:
        r.al = side
        cbw(r)
        r.dx = 10
        mul(r, r.dx)
        r.di = r.ax
        off = (r.di + 0x7B82) & M16
        mem.wds8(off, mem.ds8(off) + 1, "0791:3C35")
    r.leave()
    r.store()


@PORTS.port("0791:3EC5", ret="retf 6")
def take_shot(mem, variant):
    """3EC5–3EDC: event1 with the caller's low-byte commentary template."""
    off, seg, template = mem.arg(0), mem.arg(1), mem.arg(2)
    r = Regs(mem)
    r.enter()
    r.al = template                                          # 3EC8 mov al; preserve incoming AH
    template_word = r.ax
    r.ax = 1
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:3C3F", template_word, 1, seg, off, ret_to="0791:3ED9", far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:3EDF", ret="retf 4")
def take_header(mem, variant):
    """3EDF–3EF5: event2, commentary14h, with incoming AH preserved."""
    off, seg = mem.arg(0), mem.arg(1)
    r = Regs(mem)
    r.enter()
    r.al = 0x14
    template_word = r.ax
    r.ax = 2
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:3C3F", template_word, 2, seg, off, ret_to="0791:3EF2", far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:408E", ret="retf 4")
def choose_clearance(mem, variant):
    """408E–40B9: coin chooses either long clearance with event11."""
    off, seg = mem.arg(0), mem.arg(1)
    r = Regs(mem)
    r.enter()
    r.store(stack=True)
    yield call("214B:06FA", ret_to="0791:4096", far=True)
    r = Regs(mem, resumed=True)
    target, ret = ("0791:3FAD", "0791:40A7") if r.al else ("0791:3EF8", "0791:40B6")
    r.ax = 11
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call(target, 11, seg, off, ret_to=ret, far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:4151", ret="ret")
def keeper_clearance_if_in_strip(mem, variant):
    """4151–419B: test the ball holder's strip, optionally clear with event9."""
    r = Regs(mem)
    r.enter(6)
    r.al = mem.ds8(0x830B)
    r.ah = 0
    r.dx = 0x16
    mul(r, r.dx)
    r.di = r.ax + 0x80E8
    r.local16(-5, r.di)
    r.local16(-3, mem.DS)
    r.local8(-1, 0)
    off, seg = r.di, mem.DS
    point = mem.u16(mem.addr(seg, off))
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:2EB8", point, seg, off, ret_to="0791:4180", far=True)
    r = Regs(mem, resumed=True)
    if r.al != 0:
        r.ax = 9
        r.es, r.di = seg, off
        r.store(stack=True)
        yield call("0791:3FAD", 9, seg, off, ret_to="0791:4191", far=True)
        r = Regs(mem, resumed=True)
        r.local8(-1, 1)
    r.al = local8(mem, r, -1)                                  # 4195: preserve returned AH
    r.leave()
    r.store()


@PORTS.port("0791:3B15", ret="retf 4")
def long_ball_target(mem, variant):
    """3B15–3B9B: kicking draw with floor30, signed by attack direction."""
    off, seg = mem.arg(0), mem.arg(1)
    r = Regs(mem)
    r.enter(2)
    r.ax = mem.ds16(0x82F6)
    r.local16(-2, r.ax)
    r.ax, r.dx = 30, 0
    r.push(r.dx)                                              # 3B26–3B27: floor held under skill/RNG calls
    r.push(r.ax)
    r.ax = 2
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:278A", 2, seg, off, ret_to="0791:3B35", far=True)
    r = Regs(mem, resumed=True)
    r.dx, r.cx = 0, 4
    r.ax, r.dx = r.ax // r.cx, r.ax % r.cx
    r.store(stack=True)
    yield call("214B:06B1", r.ax, ret_to="0791:3B42", far=True)
    r = Regs(mem, resumed=True)
    cwd(r)
    # The floor was live across both calls. Re-present all four words to Call
    # at the same addresses, so its Pascal-return accounting includes them.
    floor_lo, floor_hi = pop_word(mem, r), pop_word(mem, r)
    r.store(stack=True)
    yield call("214B:0D56", floor_hi, floor_lo, r.dx, r.ax, ret_to="0791:3B4A", far=True)
    r = Regs(mem, resumed=True)
    r.push(r.dx)                                              # 3B4A–3B4B: full long held under direction call
    r.push(r.ax)
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:2BE5", seg, off, ret_to="0791:3B55", far=True)
    r = Regs(mem, resumed=True)
    cbw(r)
    cwd(r)
    r.cx, r.bx = pop_word(mem, r), pop_word(mem, r)
    r.store(stack=True)
    yield call("23E4:0279", ret_to="0791:3B5E", far=True)
    r = Regs(mem, resumed=True)
    r.local8(-1, local8(mem, r, -1) + r.al)
    mem.wds8(0x830C, 0xFF, "0791:3B61")
    point = local16(mem, r, -2)
    r.ax = 10
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:34C1", point, 10, seg, off, ret_to="0791:3B76", far=True)
    r = Regs(mem, resumed=True)
    mem.wds8(0x8303, 1, "0791:3B76")
    r.al = int(mem.ds8(0x830C) == 0)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x78A + r.di) & M16)
    r.store(stack=True)
    yield call("0791:2AA3", r.ax, ret_to="0791:3B93", far=False)
    r = Regs(mem, resumed=True)
    mem.wds8(0x830C, 0, "0791:3B93")
    r.leave()
    r.store()


@PORTS.port("0791:3B9E", ret="retf 6")
def launch_to_slot_with_half_event(mem, variant):
    """3B9E–3BEB: target slot point, event selected by the passer's half."""
    off, seg, slot = mem.arg(0), mem.arg(1), mem.arg(2)
    r = Regs(mem)
    r.enter()
    r.al = slot
    mem.wds8(0x830C, r.al, "0791:3BA4")
    r.ax, r.dx = slot, 0x16
    mul(r, r.dx)
    r.di = r.ax
    r.push(mem.ds16((0x80E8 + r.di) & M16))                   # 3BB1: target point survives2C54
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:2C54", seg, off, ret_to="0791:3BBE", far=True)
    r = Regs(mem, resumed=True)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x78C + r.di) & M16)
    r.ah = 0
    event = r.ax
    point = pop_word(mem, r)
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:34C1", point, event, seg, off, ret_to="0791:3BD1", far=True)
    r = Regs(mem, resumed=True)
    r.al = 3
    r.store(stack=True)
    yield call("0791:2AA3", r.ax, ret_to="0791:3BD7", far=False)
    r = Regs(mem, resumed=True)
    r.store(stack=True)
    yield call("214B:06FA", ret_to="0791:3BDC", far=True)
    r = Regs(mem, resumed=True)
    mem.wds8(0x8303, r.al, "0791:3BDC")
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:4D3F", seg, off, ret_to="0791:3BE8", far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:3EF8", ret="retf 6")
def long_kick_target(mem, variant):
    """3EF8–3FAA: mode9 selects the parallel skill/divisor/floor/event rows."""
    off, seg, event = mem.arg(0), mem.arg(1), mem.arg(2)
    r = Regs(mem)
    r.enter(4)
    mem.wds8(0x830C, 0, "0791:3EFE")
    r.ax = mem.ds16(0x82F6)
    r.local16(-2, r.ax)
    r.al = int(event == 9)
    r.local8(-3, r.al)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x79C + r.di) & M16)
    r.ah, r.dx = 0, 0
    r.push(r.dx)
    r.push(r.ax)
    r.al = local8(mem, r, -3)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x798 + r.di) & M16)
    r.ah = 0
    r.push(r.ax)                                              # 3F34: divisor survives skill call
    r.al = local8(mem, r, -3)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x796 + r.di) & M16)
    r.ah = 0
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:278A", r.ax, seg, off, ret_to="0791:3F4B", far=True)
    r = Regs(mem, resumed=True)
    r.cx = pop_word(mem, r)
    r.dx = 0
    r.ax, r.dx = r.ax // r.cx, r.ax % r.cx
    r.store(stack=True)
    yield call("214B:06B1", r.ax, ret_to="0791:3F56", far=True)
    r = Regs(mem, resumed=True)
    cwd(r)
    floor_lo, floor_hi = pop_word(mem, r), pop_word(mem, r)
    r.store(stack=True)
    yield call("214B:0D56", floor_hi, floor_lo, r.dx, r.ax, ret_to="0791:3F5E", far=True)
    r = Regs(mem, resumed=True)
    r.push(r.dx)
    r.push(r.ax)
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:2BE5", seg, off, ret_to="0791:3F69", far=True)
    r = Regs(mem, resumed=True)
    cbw(r)
    cwd(r)
    r.cx, r.bx = pop_word(mem, r), pop_word(mem, r)
    r.store(stack=True)
    yield call("23E4:0279", ret_to="0791:3F72", far=True)
    r = Regs(mem, resumed=True)
    r.local8(-1, local8(mem, r, -1) + r.al)
    point = local16(mem, r, -2)
    r.al = local8(mem, r, -3)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x79A + r.di) & M16)
    r.ah = 0
    chosen_event = r.ax
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:34C1", point, chosen_event, seg, off, ret_to="0791:3F8E", far=True)
    r = Regs(mem, resumed=True)
    mem.wds8(0x8303, 1, "0791:3F8E")
    mode = local8(mem, r, -3)
    r.al = 0x17 if mode else 0x18
    r.store(stack=True)
    yield call("0791:2AA3", r.ax, ret_to="0791:3F9F" if mode else "0791:3FA7", far=False)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:40BC", ret="ret")
def holder_in_advanced_central_strip(mem, variant):
    """40BC–4150: ahead of opposing marker, |y|<35 and |x|<4, outside own half."""
    r = Regs(mem)
    r.enter(6)
    r.al = mem.ds8(0x830B)
    r.ah = 0
    r.dx = 0x16
    mul(r, r.dx)
    r.di = r.ax + 0x80E8
    r.local16(-5, r.di)
    r.local16(-3, mem.DS)
    off, seg = r.di, mem.DS
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:2C54", seg, off, ret_to="0791:40E1", far=True)
    r = Regs(mem, resumed=True)
    result = False
    if r.al == 0:
        r.store(stack=True)
        yield call("0791:2996", ret_to="0791:40E8", far=False)
        r = Regs(mem, resumed=True)
        r.al = int(r.al == 0)
        cbw(r)
        r.di = r.ax
        r.di = r.di << 1
        r.si = r.di
        r.di = (r.di << 1) + r.si
        r.al = mem.ds8((0x82E3 + r.di) & M16)
        cbw(r)
        if s16(r.ax) < 0:
            r.ax = -r.ax
        r.dx = r.ax
        r.es, r.di = seg, off
        r.al = mem.u8(mem.addr(seg, off + 1))
        cbw(r)
        if s16(r.ax) < 0:
            r.ax = -r.ax
        if s16(r.ax) > s16(r.dx):
            r.es, r.di = seg, off
            r.al = mem.u8(mem.addr(seg, off + 1))
            cbw(r)
            if s16(r.ax) < 0:
                r.ax = -r.ax
            if s16(r.ax) < 35:
                r.es, r.di = seg, off
                r.al = mem.u8(mem.addr(seg, off))
                cbw(r)
                if s16(r.ax) < 0:
                    r.ax = -r.ax
                result = s16(r.ax) < 4
    r.al = int(result)
    r.local8(-1, r.al)
    r.al = local8(mem, r, -1)
    r.leave()
    r.store()


@PORTS.port("0791:3FAD", ret="retf 6")
def clear_to_random_target(mem, variant):
    """3FAD–408B: narrow long clearance or wide random target, preserving draws."""
    off, seg, event = mem.arg(0), mem.arg(1), mem.arg(2)
    r = Regs(mem)
    r.enter(2)
    r.store(stack=True)
    yield call("214B:06FA", ret_to="0791:3FB8", far=True)
    r = Regs(mem, resumed=True)
    wide = r.al != 0
    if not wide:
        r.es, r.di = seg, off
        r.al = mem.u8(mem.addr(seg, off + 6))
        r.ah = 0
        r.store(stack=True)
        yield call("0791:045D", r.ax, ret_to="0791:3FC9", far=False)
        r = Regs(mem, resumed=True)
        wide = r.al != 0
    if wide:
        r.es, r.di = seg, off
        r.al = int(s8(mem.u8(mem.addr(seg, off))) > 0)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((0x7920 + r.di) & M16)
        cbw(r)
        r.cx = 12
        imul(r, r.cx)
        r.local8(-2, r.al)
        r.ax = 40
        r.store(stack=True)
        yield call("214B:06B1", 40, ret_to="0791:3FF5", far=True)
        r = Regs(mem, resumed=True)
        r.dx = r.ax
        r.es, r.di = seg, off
        r.al = int(s8(mem.u8(mem.addr(seg, off + 1))) > 0)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((0x7920 + r.di) & M16)
        cbw(r)
        imul(r, r.dx)
        r.local8(-1, r.al)
    else:
        r.ax = 8
        r.store(stack=True)
        yield call("214B:06B1", 8, ret_to="0791:401F", far=True)
        r = Regs(mem, resumed=True)
        r.ax = r.ax + 2
        r.dx = r.ax
        r.es, r.di = seg, off
        r.al = int(s8(mem.u8(mem.addr(seg, off))) > 0)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((0x7920 + r.di) & M16)
        cbw(r)
        imul(r, r.dx)
        r.local8(-2, r.al)
        r.es, r.di = seg, off
        r.al = int(s8(mem.u8(mem.addr(seg, off + 1))) > 0)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((0x7920 + r.di) & M16)
        cbw(r)
        r.cx = 50
        imul(r, r.cx)
        r.local8(-1, r.al)
    point = local16(mem, r, -2)
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:34C1", point, event, seg, off, ret_to="0791:406F", far=True)
    r = Regs(mem, resumed=True)
    mem.wds8(0x8303, 1, "0791:406F")
    r.al = 0x16 if event == 11 else 0x15
    r.store(stack=True)
    yield call("0791:2AA3", r.ax, ret_to="0791:4080" if event == 11 else "0791:4088", far=False)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()


@PORTS.port("0791:3DF6", ret="retf 4")
def cross_to_candidate_or_random_point(mem, variant):
    """3DF6–3EC2: use3D38's output point, drawing a target only if zero."""
    off, seg = mem.arg(0), mem.arg(1)
    r = Regs(mem)
    r.enter(2)
    r.ax = 0
    r.local16(-2, r.ax)
    outoff = (r.bp - 2) & M16
    r.di = outoff
    r.es, r.di = seg, off
    r.al = mem.u8(mem.addr(seg, off + 6))
    r.ah = 0
    r.store(stack=True)
    yield call("0791:3D38", r.ss, outoff, r.ax, ret_to="0791:3E13", far=False)
    r = Regs(mem, resumed=True)
    if local16(mem, r, -2) == 0:
        r.store(stack=True)
        yield call("0791:261A", ret_to="0791:3E1C", far=False)
        r = Regs(mem, resumed=True)
        cwd(r)
        r.cx = 4
        dividend = s16(r.ax)
        quotient = abs(dividend) // 4
        if dividend < 0:
            quotient = -quotient
        r.ax, r.dx = quotient, dividend - quotient * 4
        r.ax = r.ax + 4
        r.dx = r.ax
        r.es, r.di = seg, off
        r.al = int(s8(mem.u8(mem.addr(seg, off))) < 0)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((0x7920 + r.di) & M16)
        cbw(r)
        imul(r, r.dx)
        r.local8(-2, r.al)
        r.ax = 10
        r.store(stack=True)
        yield call("214B:06B1", 10, ret_to="0791:3E4C", far=True)
        r = Regs(mem, resumed=True)
        r.ax = r.ax + 24
        r.dx = r.ax
        r.es, r.di = seg, off
        r.al = int(s8(mem.u8(mem.addr(seg, off + 1))) > 0)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((0x7920 + r.di) & M16)
        cbw(r)
        imul(r, r.dx)
        r.local8(-1, r.al)
    mem.wds8(0x830C, 0xFF, "0791:3E6E")
    point = local16(mem, r, -2)
    r.ax = 5
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:34C1", point, 5, seg, off, ret_to="0791:3E83", far=True)
    r = Regs(mem, resumed=True)
    r.al = int(mem.ds8(0x830C) == 0)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((0x794 + r.di) & M16)
    r.store(stack=True)
    yield call("0791:2AA3", r.ax, ret_to="0791:3E9B", far=False)
    r = Regs(mem, resumed=True)
    mem.wds8(0x830C, 0, "0791:3E9B")
    r.ax = 8
    r.store(stack=True)
    yield call("214B:06D0", 8, ret_to="0791:3EA9", far=True)
    r = Regs(mem, resumed=True)
    r.al = int(r.al == 0)
    mem.wds8(0x8303, r.al, "0791:3EB3")
    r.es, r.di = seg, off
    r.store(stack=True)
    yield call("0791:4D3F", seg, off, ret_to="0791:3EBF", far=True)
    r = Regs(mem, resumed=True)
    r.leave()
    r.store()
