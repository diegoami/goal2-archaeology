"""T73 display boundary: initial all-at-once removal candidate, under classification.

Return cleanup is transcribed from each routine's listing (the independent inventory
is out/T73/static-inventory.json). This first candidate deliberately removes all
88 bodies together; acceptance requires independently justified masking and ports
for every state-bearing operation. It is not an accepted classification yet.
The match-summary key site remains the kit's semantic board boundary.
"""
from . import Registry
from .contests import ss16, pop
from .geometry import cbw, cwd, mul
from .mem import s16, s8
from .postmatch import half
from .restarts import _end
from .runtime import Regs
from .setup import guest, member, farg, w8, w16, rb, rw

PORTS = Registry("display", "the 88-routine display boundary (T73)")

# Explicit listing return forms, not guessed ABI cleanup.
RETURNS = {
    "0791:0000": "ret",
    "0791:006C": "ret 8",
    "0791:0106": "retf 2",
    "0791:0425": "ret 2",
    "0791:0441": "ret 2",
    "0791:0481": "ret 4",
    "0791:04C9": "ret 6",
    "0791:054C": "ret 4",
    "0791:05C6": "ret 2",
    "0791:0691": "ret",
    "0791:0712": "retf 4",
    "0791:0C65": "ret",
    "0791:15B9": "ret",
    "0791:1829": "ret 6",
    "0791:8F10": "retf 4",
    "0791:9079": "retf 4",
    "0791:94C9": "ret 2",
    "0791:94E8": "ret",
    "0791:A699": "ret 4",
    "0791:A75D": "ret",
    "0791:C50C": "ret 4",
    "1771:0947": "retf 2",
    "1771:0AF8": "retf 6",
    "1771:0F58": "retf 6",
    "1771:0FB1": "ret 6",
    "1771:11E1": "ret 2",
    "1771:1289": "ret 2",
    "1771:13D0": "ret 2",
    "1771:1527": "ret 6",
    "1771:157D": "ret 2",
    "1771:2EE5": "retf 6",
    "1771:2F37": "retf 6",
    "1771:3827": "ret 6",
    "1771:3947": "ret 6",
    "1771:3AE2": "ret 4",
    "1771:3B3F": "ret 2",
    "1771:3BD3": "ret 2",
    "1771:42BC": "retf 2",
    "1771:4D8A": "retf 2",
    "1771:4E22": "retf 4",
    "1771:50F1": "retf 4",
    "1771:5AC4": "ret 6",
    "1771:5C94": "retf 4",
    "1771:5CCB": "retf 4",
    "1771:76FA": "retf 8",
    "1771:77C3": "ret 8",
    "1771:883F": "ret 2",
    "1771:8939": "ret 2",
    "1771:89C1": "ret 2",
    "1771:89FE": "ret 2",
    "1771:8A5D": "ret 4",
    "1771:8A87": "ret 4",
    "1771:8CA2": "ret 8",
    "1771:8CCF": "ret 12",
    "1771:8D84": "ret 2",
    "1771:8E9A": "ret 2",
    "1771:9028": "ret 2",
    "1771:91CE": "ret 2",
    "1771:937C": "ret 2",
    "1771:9509": "ret 2",
    "1771:958D": "retf 6",
    "214B:00DB": "retf 8",
    "214B:00FF": "retf 12",
    "214B:0123": "ret 12",
    "214B:01A3": "retf 12",
    "214B:0205": "retf 14",
    "214B:026D": "retf 12",
    "214B:02C8": "retf 14",
    "214B:0350": "retf 10",
    "214B:0625": "retf",
    "214B:0643": "retf",
    "214B:0661": "retf",
    "214B:0755": "ret",
    "214B:13C5": "retf 6",
    "214B:1E09": "retf 2",
    "214B:1E5A": "retf",
    "214B:1E75": "retf",
    "214B:1E8D": "retf",
    "214B:1EA1": "retf 4",
    "214B:1EBC": "retf 2",
    "214B:1EF1": "retf 6",
    "214B:1F87": "retf 2",
    "2382:0099": "ret",
    "2382:00E7": "ret",
    "2382:016D": "retf 2",
    "2382:0215": "retf 4",
    "2382:04FC": "ret",
    "2382:0608": "ret",
}
for address, ret in RETURNS.items():
    if address not in {"0791:0106", "0791:05C6", "0791:0691", "0791:8F10", "0791:9079", "0791:A699", "0791:94C9", "0791:94E8", "0791:0C65", "0791:0712", "214B:00FF", "214B:0123", "214B:01A3", "214B:0205", "214B:026D", "214B:02C8"}:
        PORTS.stub(address, ret=ret, value=None, why="initial all-at-once display-removal candidate; classification pending")


@PORTS.port("0791:0106", ret="retf 2")
def summary_boundary(mem, variant):
    """0106/0415/041A: preserve the kit's key/board boundary and original key clearing."""
    flag = mem.arg(0) & 0xFF
    mem.enter(0x108, "0791:0106")
    if flag:
        mem.read_key("0791:041A")
    mem.wds8(0xA976, 0, "0791:041A")


@PORTS.port("0791:05C6", ret="ret 2")
def pitch_glyph(mem, variant):
    """05C6-068E: glyph used by0691, reading0691's slot through the static link."""
    r = Regs(mem)
    r.enter(2)
    r.al = mem.ds8(0x66A)
    mode = r.al
    if mode == 0:
        value = 1
        r.local8(-1, value)
    elif mode == 1:
        r.di = ss16(mem, r, r.bp + 4)
        r.ax = ss16(mem, r, r.di - 2)
        r.dx = 0x16
        mul(r, r.dx)
        r.di = r.ax
        r.ax = mem.ds16((r.di + 0x80F5) & 65535)
        r.dx = 0x14
        mul(r, r.dx)
        r.di, r.es = mem.ds16(0xA91B), mem.ds16(0xA91D)
        r.di = r.di + r.ax
        r.al = rb(mem, r, 6)
        r.ah = 0
        r.di = r.ax
        r.al = mem.ds8((r.di + 0x69A8) & 65535)
        value = r.al
        r.local8(-1, value)
    elif mode == 2:
        r.al = mem.ds8(0x8319)
        cbw(r)
        cwd(r)
        r.cx, r.bx = r.ax, r.dx
        r.ax, r.dx = mem.ds16(0x831B), 0
        later = s16(r.dx) > s16(r.bx) or (r.dx == r.bx and r.ax > r.cx)
        r.al = int(later)
        half(r, 'dx', r.al)
        r.di = ss16(mem, r, r.bp + 4)
        r.al = int(ss16(mem, r, r.di - 2) < 12)
        r.al = r.al ^ (r.dx & 255)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((r.di + 0x6D4) & 65535)
        value = r.al
        r.local8(-1, value)
    elif mode == 3:
        r.di = ss16(mem, r, r.bp + 4)
        r.al = int(ss16(mem, r, r.di - 2) < 12)
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((r.di + 0x6D2) & 65535)
        value = r.al
        r.local8(-1, value)
    elif mode == 4:
        r.di = ss16(mem, r, r.bp + 4)
        r.ax = ss16(mem, r, r.di - 2) - 1
        r.dx, r.cx = 0, 11
        dividend = r.ax
        r.ax, r.dx = dividend // 11, dividend % 11
        r.ax, r.dx = r.dx, r.ax
        r.ax = r.ax + 0x2F
        value = r.al
        r.local8(-1, value)
    else:
        # The listing leaves this local untouched for unsupported modes; retain the guest's byte.
        r.flush()
        value = mem.u8(mem.ss_lin(r.bp - 1))
    r.al = value
    return _end(r, value=True)


@PORTS.port("0791:0691", ret="ret")
def refresh_pitch_glyphs(mem, variant):
    """0691-0711: glyph/colour words +4 of the22 engine pitch records."""
    r = Regs(mem)
    r.enter(6)
    for slot in range(1, 23):
        r.local16(-2, slot)
        r.ax, r.dx = slot, 0x16
        mul(r, r.dx)
        r.di = r.ax + 0x80E8
        poff = r.di
        r.local16(-6, poff)
        r.local16(-4, mem.DS)
        r = yield from guest(mem, r, '045D', slot, ret='06BB', far=False)
        if r.al:
            r.es, r.di = mem.DS, poff
            r = yield from guest(mem, r, '2974', r.es, r.di, ret='06C8')
            cbw(r)
            r.di = r.ax
            r.al = mem.ds8((r.di + 0x8330) & 65535)
            r.ah = 0
            r.cx = 8
            r.ax = (r.ax << 8) + 1
            r.es, r.di = mem.DS, poff
            w16(mem, r, 4, r.ax, '06DA')
        else:
            r = yield from guest(mem, r, '05C6', r.bp, ret='06E4', far=False)
            r.ah = 0
            r.push(r.ax)
            r.es, r.di = mem.DS, poff
            r = yield from guest(mem, r, '2974', r.es, r.di, ret='06F0')
            cbw(r)
            r.di = r.ax
            r.al = mem.ds8((r.di + 0x832E) & 65535)
            r.ah = 0
            r.cx = 8
            r.ax = r.ax << 8
            r.dx = pop(mem, r)
            r.ax = r.ax + r.dx
            r.es, r.di = mem.DS, poff
            w16(mem, r, 4, r.ax, '0704')
    return _end(r)


def grid_cell(mem, r, seg, off, row, column, pointer):
    """8F35 and repeats: signed column*2 + signed row*160 + screen pointer; +090E is used by the caller."""
    r.es, r.di = seg, off
    r.al = rb(mem, r, column)
    cbw(r)
    r.ax = r.ax << 1
    r.cx = r.ax
    r.es, r.di = seg, off
    r.al = rb(mem, r, row)
    cbw(r)
    r.dx = 0xA0
    mul(r, r.dx)
    r.di, r.es = mem.ds16(pointer), mem.ds16(pointer + 2)
    r.di = r.di + r.ax + r.cx


@PORTS.port("0791:8F10", ret="retf 4")
def draw_ball_state(mem, variant):
    """8F10-9076: ball previous-position/glyph and all occupancy-picture writes remain."""
    r = Regs(mem)
    r.enter()
    pseg, poff = farg(mem, r, 6)
    r.ax = rw(mem, r, 2)
    if r.ax != mem.ds16(0x640):
        r.es, r.di = pseg, poff
        r.ax = rw(mem, r, 2)
        if r.ax != rw(mem, r, 0):
            grid_cell(mem, r, pseg, poff, 2, 3, 0x7C16)
            r.al = rb(mem, r, 0x90E)
            arg = r.ax
            r.di = 0x8EF0
            r = yield from guest(mem, r, '23E4:08DF', arg, mem.seg(0x0791), r.di, ret='8F66')
            if member(mem):
                grid_cell(mem, r, pseg, poff, 2, 3, 0x7C1E)
                r.bx = rw(mem, r, 0x90E)
                grid_cell(mem, r, pseg, poff, 2, 3, 0x7C16)
                w16(mem, r, 0x90E, r.bx, '8FAF')
    r.es, r.di = pseg, poff
    r.ax = rw(mem, r, 0)
    w16(mem, r, 2, r.ax, '8FBD')
    high = False
    if rb(mem, r, 0xD) != 0:
        r = yield from guest(mem, r, '835F', pseg, poff, ret='8FD4')
        high = r.ax > 2
    r.al = int(high)
    cbw(r)
    r.di = r.ax
    r.al = mem.ds8((r.di + 0x880) & 65535)
    r.es, r.di = pseg, poff
    w8(mem, r, 4, r.al, '8FE9')
    r.ax = rw(mem, r, 0)
    if r.ax != mem.ds16(0x640):
        grid_cell(mem, r, pseg, poff, 0, 1, 0x7C1E)
        r.bx = rw(mem, r, 0x90E)
        grid_cell(mem, r, pseg, poff, 0, 1, 0x7C16)
        r.ax = rw(mem, r, 0x90E)
        if r.ax == r.bx:
            r.es, r.di = pseg, poff
            r.bx = rw(mem, r, 4)
            grid_cell(mem, r, pseg, poff, 0, 1, 0x7C16)
            w16(mem, r, 0x90E, r.bx, '906E')
    return _end(r)


@PORTS.port("0791:9079", ret="retf 4")
def reset_sprite_state(mem, variant):
    """9079-90C2: reset its record and restore the occupancy cell even though rendering is removed."""
    r = Regs(mem)
    r.enter()
    r.ax = mem.ds16(0x644)
    seg, off = farg(mem, r, 6)
    w16(mem, r, 0, r.ax, '9082')
    if mem.ds8(0x9A3E) == 0:
        r = yield from guest(mem, r, '8E24', seg, off, ret='9097')
        r.al = mem.ds8(0x644)
        cbw(r)
        r.dx = 0xA0
        mul(r, r.dx)
        r.di, r.es = mem.ds16(0x7C1E), mem.ds16(0x7C20)
        r.di = r.di + r.ax
        r.cx = rw(mem, r, 0x90E)
        r.al = mem.ds8(0x644)
        cbw(r)
        r.dx = 0xA0
        mul(r, r.dx)
        r.di, r.es = mem.ds16(0x7C16), mem.ds16(0x7C18)
        r.di = r.di + r.ax
        w16(mem, r, 0x90E, r.cx, '90BA')
    return _end(r)


@PORTS.port("0791:A699", ret="ret 4")
def save_pitch_copy(mem, variant):
    """A699-A6E1: the menu's saved pitch copy is engine state, including all4000 bytes."""
    r = Regs(mem)
    r.enter()
    src = 0x7C22 if mem.ds8(0xC1F) else 0x7C1E
    r.di, r.es = mem.ds16(src), mem.ds16(src + 2)
    source = r.es, r.di
    r.di, r.es = mem.ds16(0x7C1A), mem.ds16(0x7C1C)
    r.ax = 0xFA0
    r = yield from guest(mem, r, '23E4:025D', *source, r.es, r.di, r.ax,
                         ret='A6B8' if src == 0x7C22 else 'A6CF')
    seg, off = farg(mem, r, 4)
    r.di = 0xA96E
    r = yield from guest(mem, r, '214B:0329', seg, off, mem.DS, r.di, ret='A6DE')
    return _end(r)


@PORTS.port("0791:94C9", ret="ret 2")
def speaker_seed_step(mem, variant):
    """94C9-94E5: retain the second seed until original-reader evidence permits any display mask."""
    r = Regs(mem)
    r.enter(2)
    r.di = 0x8336
    r = yield from guest(mem, r, '214B:0688', mem.DS, r.di, ss16(mem, r, r.bp + 4), ret='94DC')
    r.local16(-2, r.ax)
    return _end(r, value=True)


@PORTS.port("0791:94E8", ret="ret")
def speaker_noise_state(mem, variant):
    """94E8-9543: retain RNG calls and their ordering; speaker output/delay are separate callees."""
    r = Regs(mem)
    r.enter()
    tone = False
    if mem.ds16(0x832A) > 0:
        r.ax = 0x32
        r = yield from guest(mem, r, '94C9', r.ax, ret='94F9', far=False)
        cwd(r)
        r.cx, r.bx = r.ax, r.dx
        r.ax, r.dx = mem.ds16(0x832A), 0
        larger = s16(r.dx) > s16(r.bx) or (r.dx == r.bx and r.ax > r.cx)
        if larger:
            r.di, r.es = mem.ds16(0xA923), mem.ds16(0xA925)
            tone = rb(mem, r, 0x3F) > 0
            if tone:
                r.ax = mem.ds16(0x832A) + 300
                r = yield from guest(mem, r, '94C9', r.ax, ret='9522', far=False)
                r.ax = r.ax + 100
                r = yield from guest(mem, r, '214B:1EBC', r.ax, ret='952B')
    if not tone:
        r = yield from guest(mem, r, '214B:1E8D', ret='9532')
    r.di, r.es = mem.ds16(0xA923), mem.ds16(0xA925)
    r.al = rb(mem, r, 0x3F)
    r.ah = 0
    r = yield from guest(mem, r, '0425', r.ax, ret='9540', far=False)
    return _end(r)


@PORTS.port("0791:0C65", ret="ret")
def replay_no_boundary(mem, variant):
    """0C65: retain the live pending-change clear; the kit's display policy requests no replay."""
    mem.wds8(0x9B55, 0, "0791:0C6B")


def _text_cells(mem, reverse):
    """214B:00FF/0123: these writes also feed A841's engine-background copy, so remain exact."""
    r = Regs(mem)
    r.enter()
    r.push(mem.DS)
    k = 4 if reverse else 6
    r.si = ss16(mem, r, r.bp + k + 4)
    source_seg = ss16(mem, r, r.bp + k + 6)
    if reverse:
        r.std()
    else:
        r.cld()
    r.cx = ss16(mem, r, r.bp + k)
    if r.cx:
        r.di = ss16(mem, r, r.bp + k + 8)
        r.es = ss16(mem, r, r.bp + k + 10)
        r.ax = ss16(mem, r, r.bp + k + 2)
        r.ax = ((r.ax & 255) << 8) | (r.ax >> 8)
        while r.cx:
            r.al = mem.u8(mem.addr(source_seg, r.si))
            r.si = r.si + (-1 if reverse else 1)
            w16(mem, r, 0, r.ax, '214B:013D' if reverse else '214B:0119')
            r.di = r.di + (-2 if reverse else 2)
            r.cx = r.cx - 1
    return _end(r)


@PORTS.port('214B:00FF', ret='retf 12')
def text_cells_forward(mem, variant):
    return _text_cells(mem, False)


@PORTS.port('214B:0123', ret='ret 12')
def text_cells_backward(mem, variant):
    return _text_cells(mem, True)


def _string_cells(mem, backwards, set_attr, copied_ret, written_ret, attr_at):
    r = Regs(mem)
    r.enter(0x100)
    seg, off = farg(mem, r, 0xE)
    r.di = (r.bp - 0x100) & 65535
    temporary = r.di
    r.ax = 0xFF
    r = yield from guest(mem, r, '23E4:0644', seg, off, r.ss, temporary, r.ax, ret=copied_ret)
    if set_attr:
        r.al = ss16(mem, r, r.bp + 0x12) & 255
        mem.wds8(0xAAB2, r.al, attr_at)
    r.al = ss16(mem, r, r.bp + 0xA) & 255
    r.ah = 0
    r.ax = r.ax << 1
    r.cx = r.ax
    r.al = ss16(mem, r, r.bp + 0xC) & 255
    r.ah = 0
    r.dx = 0xA0
    mul(r, r.dx)
    farg(mem, r, 6)
    ptr = mem.addr(r.es, r.di)
    r.di, r.es = mem.u16(ptr), mem.u16(ptr + 2)
    r.di = r.di + r.ax + r.cx - 0xA2
    destination = r.es, r.di
    r.flush()
    length = mem.u8(mem.ss_lin(temporary))
    if backwards:
        r.al = length
        r.ah = 0
        r.di = r.ax
        r.di = r.bp + r.di - 0x100
    else:
        r.di = r.bp - 0xFF
    source = r.ss, r.di
    r.al = mem.ds8(0xAAB2)
    r.ah = 0
    colour = r.ax
    r.al = length
    r.ah = 0
    r = yield from guest(mem, r, '214B:0123' if backwards else '214B:00FF',
                         *destination, *source, colour, r.ax, ret=written_ret, far=not backwards)
    return _end(r)


@PORTS.port('214B:01A3', ret='retf 12')
def string_at_attr(mem, variant):
    return (yield from _string_cells(mem, True, False, '214B:01BE', '214B:01FF', None))


@PORTS.port('214B:0205', ret='retf 14')
def string_at_set_attr(mem, variant):
    return (yield from _string_cells(mem, True, True, '214B:0220', '214B:0267', '214B:0223'))


@PORTS.port('214B:026D', ret='retf 12')
def string_forward_attr(mem, variant):
    return (yield from _string_cells(mem, False, False, '214B:0288', '214B:02C2', None))


@PORTS.port('214B:02C8', ret='retf 14')
def string_forward_set_attr(mem, variant):
    return (yield from _string_cells(mem, False, True, '214B:02E3', '214B:0323', '214B:02E6'))


@PORTS.port('0791:0712', ret='retf 4')
def score_into_buffer(mem, variant):
    """0712-0773: the setup's score is copied into the engine background; keep the exact string writes."""
    r = Regs(mem)
    r.enter(0x104)
    seg, off = farg(mem, r, 6)
    r.local16(-4, off)
    r.local16(-2, seg)
    for score, row, formatted, written in ((0x9B3D, 2, '0739', '0749'), (0x9B3C, 4, '0760', '0770')):
        r.al = 0x70
        colour = r.ax
        r.push(colour)
        r.di = (r.bp - 0x104) & 65535
        temporary = r.di
        r.push(r.ss)
        r.push(temporary)
        r.al = mem.ds8(score)
        r.ah = 0
        r.dx = 0
        r = yield from guest(mem, r, '214B:09DA', r.dx, r.ax, ret=formatted)
        r.al = row
        row_word = r.ax
        r.al = 0x1F
        column_word = r.ax
        r.es, r.di = seg, off
        r.sp = r.sp + 6
        r = yield from guest(mem, r, '214B:0205', colour, r.ss, temporary, row_word, column_word,
                             seg, off, ret=written)
    return _end(r)
