"""T73 display boundary: initial all-at-once removal candidate, under classification.

Return cleanup is transcribed from each routine's listing (the independent inventory
is out/T73/static-inventory.json). This first candidate deliberately removes all
88 bodies together; acceptance requires independently justified masking and ports
for every state-bearing operation. It is not an accepted classification yet.
The match-summary key site remains the kit's semantic board boundary.
"""
from . import Registry
from .contests import ss16, ss8, pop
from .geometry import cbw, cwd, mul, imul
from .mem import s16, s8
from .postmatch import half
from .restarts import _end, idiv_by
from .runtime import Regs
from .setup import guest, member, farg, w8, w16, rb, rw, squad_of, player_of

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
    if address not in {"1771:4D8A", "1771:4E22", "1771:8A87", "1771:5AC4", "1771:0FB1", "1771:76FA", "1771:77C3", "1771:8E9A", "1771:8CA2", "1771:958D", "1771:8939", "0791:0441", "214B:1EF1", "214B:1F87", "214B:1E8D", "214B:1EBC", "0791:C50C", "214B:1E09", "0791:0481", "0791:04C9", "0791:054C", "0791:1829", "0791:0106", "0791:05C6", "0791:0691", "0791:8F10", "0791:9079", "0791:A699", "0791:94C9", "0791:94E8", "0791:0C65", "0791:0712", "214B:00FF", "214B:0123", "214B:01A3", "214B:0205", "214B:026D", "214B:02C8", "0791:15B9", "0791:0000", "0791:006C", "214B:00DB", "214B:0625", "214B:0643", "1771:3827", "1771:2EE5", "1771:2F37", "1771:0F58", "214B:0350", "0791:A75D", "1771:3947", "1771:3AE2", "1771:3B3F", "1771:3BD3", "1771:42BC", "214B:13C5"}:
        PORTS.stub(address, ret=ret, value=None, why="initial all-at-once display-removal candidate; classification pending")


def write_buffer_text(mem, r, source, row, column, target, ret, colour=None, held=0):
    """The listing's Pascal text call; held words were already pushed before formatting its result."""
    r.di = 0xA96E
    r.sp = r.sp + held
    args = ((colour,) if colour is not None else ()) + (*source, row, column, mem.DS, r.di)
    return (yield from guest(mem, r, target, *args, ret=ret))


@PORTS.port("0791:0106", ret="retf 2")
def summary_boundary(mem, variant):
    """0106-0422: keep the board's concrete buffer/ABI effects and its original key site."""
    r = Regs(mem)
    r.enter(0x108)
    flag = ss16(mem, r, r.bp + 6) & 255
    r.di = 0x276E if flag else 0x27A0
    r = yield from guest(mem, r, 'A699', mem.DS, r.di, ret='011B' if flag else '0125', far=False)
    r.di = 0xA96E
    r = yield from guest(mem, r, '214B:0329', mem.DS, 0x414A, mem.DS, r.di, ret='0134')
    r.di = 0xA96E
    r = yield from guest(mem, r, '0712', mem.DS, r.di, ret='013D')
    if mem.ds8(0x9A3F):
        r.di = 0xA96E
        r = yield from guest(mem, r, '214B:0329', mem.DS, 0x1B58, mem.DS, r.di, ret='0153')
    else:
        r = yield from guest(mem, r, '0000', ret='0159', far=False)
        if mem.ds16(0x7C3A):
            r.di = 0xA96E
            r = yield from guest(mem, r, '214B:0329', mem.DS, 0x14C8, mem.DS, r.di, ret='016F')
            word = mem.ds16(0x7C3A)
            player_of(mem, r, word)
            r.al = rb(mem, r, 6)
            r.ah = 0
            r = yield from guest(mem, r, '1771:2E20', word, r.ax, ret='018D')
            colour = r.ax
            r.push(colour)
            r.di = (r.bp - 0x104) & 65535
            temp = r.di
            r.push(r.ss); r.push(temp)
            r.ax = mem.ds16(0x7C3A)
            r.di, r.es = mem.ds16(0x9B70), mem.ds16(0x9B72)
            r.di = r.di + r.ax
            r.al = rb(mem, r, 0)
            r = yield from guest(mem, r, '23E4:075A', r.ax, ret='01A6')
            r.al = 0x16
            row = r.ax
            r.al = 0x2B
            r = yield from write_buffer_text(mem, r, (r.ss,temp), row, r.ax, '214B:02C8', '01B6', colour, 6)
            r.ax, r.dx = mem.ds16(0x7C3A), 11
            mul(r, r.dx)
            r.di, r.es = mem.ds16(0x9B6C), mem.ds16(0x9B6E)
            r.di = r.di + r.ax
            source = r.es, r.di
            r.al = 0x16
            row = r.ax
            r.al = 0x2D
            r = yield from write_buffer_text(mem, r, source, row, r.ax, '214B:026D', '01D6')
        for side in range(2):
            r.local8(-4, side)
            for index in range(9):
                r.local8(-3, index)
                r.al = index
                cbw(r)
                r.di = r.ax
                r.al = mem.ds8((r.di + 0x674) & 65535)
                colour = r.ax
                r.push(colour)
                r.di = (r.bp - 0x104) & 65535
                temp = r.di
                r.push(r.ss); r.push(temp)
                r.al = index
                cbw(r)
                r.cx = r.ax
                r.al = side
                cbw(r)
                r.dx = 10
                mul(r, r.dx)
                r.di = r.ax + r.cx
                r.al = mem.ds8((r.di + 0x7B7E) & 65535)
                r.ah = 0
                r.dx = 0
                r = yield from guest(mem, r, '214B:09DA', r.dx, r.ax, ret='021B')
                r.al = index
                r.ah = 0
                r.ax = r.ax + 9
                row = r.ax
                r.al = side
                cbw(r)
                r.di = r.ax
                r.al = mem.ds8((r.di + 0x672) & 65535)
                r = yield from write_buffer_text(mem, r, (r.ss,temp), row, r.ax, '214B:0205','0239',colour,6)
        for pair,row,ret in ((0x80F2,19,'0252'),(0x80F6,20,'025F')):
            r.di, r.ax = pair, row
            r = yield from guest(mem,r,'006C',mem.DS,r.di,r.ax,r.bp,ret=ret,far=False)
    for side in range(2):
        r.local8(-4,side)
        r.al = side
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((r.di + 0x832E) & 65535)
        colour = r.ax
        r.push(colour)
        r.al = side
        cbw(r)
        r.di = r.ax << 1
        r.ax = mem.ds16((r.di + 0x9B34) & 65535)
        half(r,'cx',4)
        r.ax = r.ax << 4
        r.di,r.es = mem.ds16(0x9B68),mem.ds16(0x9B6A)
        r.di = r.di + r.ax
        source = r.es,r.di
        r.al = 7
        row = r.ax
        r.al = side
        cbw(r)
        r.di = r.ax
        r.al = mem.ds8((r.di + 0x66E) & 65535)
        r = yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','02A3',colour,2)
        for slot in range(1,12):
            r.local16(-2,slot)
            r.ax,r.dx = slot,3
            mul(r,r.dx)
            r.cx = r.ax
            r.al = side
            cbw(r)
            r.dx = 33
            mul(r,r.dx)
            r.di = r.ax + r.cx + 0x7BD1
            scorer = r.di
            r.local16(-8,scorer);r.local16(-6,mem.DS)
            r.es,r.di = mem.DS,scorer
            if not rw(mem,r,0):continue
            word = rw(mem,r,0)
            r.ax = slot + 11
            row = r.ax
            r.al = side
            cbw(r)
            r.di = r.ax
            r.al = mem.ds8((r.di + 0x670) & 65535)
            r.ah = 0
            r = yield from guest(mem,r,'1771:2EE5',word,row,r.ax,ret='02F9')
            mem.wds8(0xAAB2,4,'0791:02F9')
            r.es,r.di = mem.DS,scorer
            marked = rb(mem,r,2) > 0x80
            if marked:
                word = rw(mem,r,0)
                r.al = side
                cbw(r)
                r.di = r.ax << 1
                r = yield from guest(mem,r,'1771:3A82',word,mem.ds16((r.di + 0x9B34)&65535),ret='035B')
                found = bool(r.ax)
                r.di = 0x101 if found else 0x103
                source = mem.seg(0x0791),r.di
                r.ax = slot + 11
                row = r.ax
                r.al = side
                cbw(r)
                r.di = r.ax
                r.al = mem.ds8((r.di + 0x670)&65535)
                r.ah = 0
                r.ax = r.ax + (14 if found else 13)
                r = yield from write_buffer_text(mem,r,source,row,r.ax,'214B:026D','0385' if found else '03AD')
            r.di = (r.bp - 0x108)&65535
            temp = r.di
            r.push(r.ss);r.push(temp)
            r.es,r.di = mem.DS,scorer
            r.al = rb(mem,r,2)
            r.ah = 0
            if marked:
                r.ax = r.ax - 0x80
                cwd(r)
            else:r.dx = 0
            r = yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='03C7' if marked else '0320')
            r.ax = slot + 11
            row = r.ax
            r.al = side
            cbw(r)
            r.di = r.ax
            r.al = mem.ds8((r.di + 0x670)&65535)
            r.ah = 0
            r.ax = r.ax + 18
            r = yield from write_buffer_text(mem,r,(r.ss,temp),row,r.ax,'214B:01A3','03E8' if marked else '0341',held=4)
    r.di,r.es = mem.ds16(0xA96E),mem.ds16(0xA970)
    source = r.es,r.di
    r.di,r.es = mem.ds16(0xA96A),mem.ds16(0xA96C)
    r.ax = 4000
    r = yield from guest(mem,r,'23E4:025D',*source,r.es,r.di,r.ax,ret='040F')
    if flag:r = yield from guest(mem,r,'214B:08DD',ret='041A')
    mem.wds8(0xA976,0,'0791:041A')
    return _end(r)


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
    """0C65/0C6B/0C87: retain the original No-question path and its local memory effects."""
    r=Regs(mem);r.enter(8)
    mem.wds8(0x9B55,0,"0791:0C6B")
    r.di,r.es=mem.ds16(0xA923),mem.ds16(0xA925)
    if rb(mem,r,0x41):
        if not mem.ds8(0xC1E):
            from .mem import PortError
            raise PortError("automatic replay is outside the kit's No-replay boundary")
        r.di=0xC42
        r=yield from guest(mem,r,'0B7C',mem.seg(0x0791),r.di,ret='0C8A',far=False)
        if r.al:
            from .mem import PortError
            raise PortError("accepted replay is outside the kit's No-replay boundary")
    return _end(r)


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


@PORTS.port('0791:15B9', ret='ret')
def snapshot_state(mem, variant):
    """15B9-1826: preserve the snapshot's concrete copies; no blanket snapshot mask is assumed."""
    r = Regs(mem)
    r.enter(8)
    r.di = 0x8439
    r.ax = 0x7FB
    r = yield from guest(mem, r, '23E4:025D', mem.DS, 0x7C3E, mem.DS, r.di, r.ax, ret='15D2')
    for side in range(2):
        r.local8(-1, side)
        r.al = side
        cbw(r)
        r.di = r.ax << 1
        sqseg, sqoff = squad_of(mem, r, mem.ds16((0x9B34 + r.di) & 65535))
        r.local16(-7, sqoff)
        r.local16(-5, sqseg)
        r.al = side
        cbw(r)
        r.di = r.ax << 1
        squad_of(mem, r, mem.ds16((0x9B34 + r.di) & 65535))
        source = r.es, r.di
        r.al = side
        cbw(r)
        r.dx = 0xBF
        mul(r, r.dx)
        r.di = r.ax + 0x8C34
        r.ax = 0xBF
        r = yield from guest(mem, r, '23E4:025D', *source, mem.DS, r.di, r.ax, ret='162B')
        for pointer, stride, base, length, target, ret in ((0xA91F, 3, 0x9930, 3, '23E4:025D', '165B'),
                (0x9B74, 13, 0x993C, 12, '23E4:0644', '168B')):
            r.es, r.di = sqseg, sqoff
            r.al = rb(mem, r, 0x2E)
            r.ah = 0
            r.dx = stride
            mul(r, r.dx)
            r.di, r.es = mem.ds16(pointer), mem.ds16(pointer + 2)
            r.di = r.di + r.ax
            source = r.es, r.di
            r.al = side
            cbw(r)
            r.dx = stride
            mul(r, r.dx)
            r.di = r.ax + base
            r.ax = length
            r = yield from guest(mem, r, target, *source, mem.DS, r.di, r.ax, ret=ret)
        r.es, r.di = sqseg, sqoff
        r.al = rb(mem, r, 0x2E)
        r.ah = 0
        r.di, r.es = mem.ds16(0x9B78), mem.ds16(0x9B7A)
        r.di = r.di + r.ax
        half(r, 'dx', rb(mem, r, 0))
        r.al = side
        cbw(r)
        r.di = r.ax
        mem.wds8((r.di + 0x9970) & 65535, r.dx & 255, '0791:16A3')
        for slot in range(1, 21):
            r.local16(-3, slot)
            def squad_player():
                r.ax = slot << 1
                r.es, r.di = sqseg, sqoff + r.ax
                r.ax = rw(mem, r, -2)
                return r.ax
            player_of(mem, r, squad_player())
            source = r.es, r.di
            r.ax, r.dx = slot, 20
            mul(r, r.dx)
            r.cx = r.ax
            r.al = side
            cbw(r)
            r.dx = 400
            mul(r, r.dx)
            r.di = r.ax + r.cx + 0x8F1C
            r.ax = 20
            r = yield from guest(mem, r, '23E4:025D', *source, mem.DS, r.di, r.ax, ret='16F2')
            squad_player()
            r.dx = 11
            mul(r, r.dx)
            r.di, r.es = mem.ds16(0x9B6C), mem.ds16(0x9B6E)
            r.di = r.di + r.ax
            source = r.es, r.di
            r.ax, r.dx = slot, 11
            mul(r, r.dx)
            r.cx = r.ax
            r.al = side
            cbw(r)
            r.dx = 220
            mul(r, r.dx)
            r.di = r.ax + r.cx + 0x9565
            r.ax = 10
            r = yield from guest(mem, r, '23E4:0644', *source, mem.DS, r.di, r.ax, ret='1733')
            squad_player()
            r.di, r.es = mem.ds16(0x9B70), mem.ds16(0x9B72)
            r.di = r.di + r.ax
            half(r, 'bx', rb(mem, r, 0))
            r.ax, r.cx = slot, slot
            r.al = side
            cbw(r)
            r.dx = 20
            mul(r, r.dx)
            r.di = r.ax + r.cx
            mem.wds8((r.di + 0x98DF) & 65535, r.bx & 255, '0791:175C')
    for source, dest, length, ret in ((0x7B7E, 0x7B6A, 20, '1785'), (0x7BD4, 0x7B92, 66, '1798')):
        r.di, r.ax = dest, length
        r = yield from guest(mem, r, '23E4:025D', mem.DS, source, mem.DS, dest, r.ax, ret=ret)
    r.di, r.es = mem.ds16(0x7C2A), mem.ds16(0x7C2C)
    source = r.es, r.di
    r.di, r.ax = 0x7C2E, 8
    r = yield from guest(mem, r, '23E4:025D', *source, mem.DS, r.di, r.ax, ret='17AC')
    r.al = mem.ds8(0x9A3D)
    mem.wds8(0x9A3C, r.al, '0791:17AF')
    for source, dest, length, ret in ((0x9A40, 0x9A90, 80, '17C5'), (0x9B08, 0x9AE0, 40, '17D8')):
        r.di, r.ax = dest, length
        r = yield from guest(mem, r, '23E4:025D', mem.DS, source, mem.DS, dest, r.ax, ret=ret)
    r.ax, r.es = mem.ds16(0x9B34), mem.ds16(0x9B36)
    r.dx = r.es
    mem.wds16(0x9B30, r.ax, '0791:17DE')
    mem.wds16(0x9B32, r.dx, '0791:17E1')
    for source, dest, at in ((0x9B3A, 0x9B38, '17E8'), (0x9B3C, 0x9B3E, '17EE')):
        r.ax = mem.ds16(source)
        mem.wds16(dest, r.ax, '0791:' + at)
    r.al = mem.ds8(0x9B41)
    mem.wds8(0x9B42, r.al, '0791:17F4')
    r.di, r.es = mem.ds16(0xA978), mem.ds16(0xA97A)
    r.ax = rw(mem, r, 0)
    mem.wds16(0x9974, r.ax, '0791:17FE')
    r.di, r.ax = 0x998C, 20
    r = yield from guest(mem, r, '23E4:025D', mem.DS, 0x9978, mem.DS, r.di, r.ax, ret='1814')
    r.di = 0xA96A
    r = yield from guest(mem, r, '214B:0329', mem.DS, 0x6120, mem.DS, r.di, ret='1823')
    return _end(r)


@PORTS.port('0791:0000', ret='ret')
def shootout_board_numbers(mem, variant):
    r=Regs(mem);r.enter(0x100)
    if mem.ds8(0x832D)!=0xFF:
        r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',mem.DS,0x5B10,mem.DS,r.di,ret='001D')
        r.al=7;colour=r.ax;r.push(colour)
        r.di=(r.bp-0x100)&65535;temporary=r.di
        r.push(r.ss);r.push(temporary)
        r.al=mem.ds8(0x832D);r.ah=0;r.dx=0
        r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='0034')
        r.al=6;row=r.ax;r.al=14
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:0205','0044',colour,6)
        r.di=(r.bp-0x100)&65535;temporary=r.di
        r.push(r.ss);r.push(temporary)
        r.al=mem.ds8(0x832C);r.ah=0;r.dx=0
        r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='0058')
        r.al=6;row=r.ax;r.al=16
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:026D','0068',held=4)
    return _end(r)


@PORTS.port('0791:006C',ret='ret 8')
def board_bar_attributes(mem,variant):
    r=Regs(mem);r.enter(2)
    seg,off=farg(mem,r,8)
    r.ax=rw(mem,r,2)+rw(mem,r,0)
    if r.ax:
        r.ax=rw(mem,r,2)+rw(mem,r,0);r.bx=r.ax
        r.ax=rw(mem,r,2);r.cx=24;mul(r,r.cx)
        r.dx=0;r.ax=r.ax//r.bx;amount=r.ax;r.local16(-2,amount)
        r.ax=ss16(mem,r,r.bp+6);r.dx=160;mul(r,r.dx)
        r.di,r.es=mem.ds16(0xA96E),mem.ds16(0xA970)
        r.di=r.di+r.ax-0x5C;destination=r.es,r.di
        r.al=mem.ds8(0x832F);r.ah=0
        r=yield from guest(mem,r,'214B:00DB',*destination,r.ax,amount,ret='00C9')
        r.ax=(amount+35)<<1;r.cx=r.ax
        r.ax=ss16(mem,r,r.bp+6);r.dx=160;mul(r,r.dx)
        r.di,r.es=mem.ds16(0xA96E),mem.ds16(0xA970)
        r.di=r.di+r.ax+r.cx-0xA2;destination=r.es,r.di
        r.al=mem.ds8(0x832E);r.ah=0;colour=r.ax
        r.ax=24-amount
        r=yield from guest(mem,r,'214B:00DB',*destination,colour,r.ax,ret='00FB')
    return _end(r)


@PORTS.port('214B:00DB',ret='retf 8')
def attribute_cells(mem,variant):
    r=Regs(mem);r.enter()
    if s16(ss16(mem,r,r.bp+6))>0:
        r.push(mem.DS)
        farg(mem,r,10)
        r.ax=ss16(mem,r,r.bp+8)
        r.cx=ss16(mem,r,r.bp+6)
        r.cld()
        while r.cx:
            r.di=r.di+1
            w8(mem,r,0,r.al,'214B:00F5')
            r.di=r.di+1;r.cx=r.cx-1
    return _end(r)


@PORTS.port('214B:0625',ret='retf')
def save_bottom_line(mem,variant):
    r=Regs(mem);r.enter()
    r.di,r.es=mem.ds16(0xA96A),mem.ds16(0xA96C)
    r.di=r.di+0xF00;source=r.es,r.di
    r.di=0xAA04;r.ax=160
    r=yield from guest(mem,r,'214B:003C',*source,mem.DS,r.di,r.ax,ret='214B:063F')
    return _end(r)


@PORTS.port('214B:0643',ret='retf')
def restore_bottom_line(mem,variant):
    r=Regs(mem);r.enter();r.di=0xAA04
    source=mem.DS,r.di
    r.di,r.es=mem.ds16(0xA96A),mem.ds16(0xA96C)
    r.di=r.di+0xF00;r.ax=160
    r=yield from guest(mem,r,'214B:003C',*source,r.es,r.di,r.ax,ret='214B:065D')
    return _end(r)


@PORTS.port('1771:3827',ret='ret 6')
def performance_text_state(mem,variant):
    r=Regs(mem);r.enter(8)
    word=ss16(mem,r,r.bp+8)
    pseg,poff=player_of(mem,r,word)
    r.local16(-8,poff);r.local16(-6,pseg)
    r.ax=rw(mem,r,0x12);value=r.ax;r.local16(-4,value)
    if value!=0x7FFF:
        if s16(value)>5000:
            value=(value-10000)&65535;r.local16(-4,value)
        value=(value-55)&65535;r.local16(-4,value)
        bucket=9
        for bound,index in ((-50,1),(0,2),(50,3),(100,4),(150,5),(200,6),(300,7),(400,8)):
            if s16(value)<bound:bucket=index;break
        r.local16(-2,bucket);r.al=bucket
        mem.wds8(0xE86,r.al,'1771:38D9')
        bright=False
        if mem.ds8(0xC1F):
            r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0
            r=yield from guest(mem,r,'1771:3A82',word,r.ax,ret='1771:38F3')
            bright=r.ax<12
            if not bright:
                r.ax=3;r.es,r.di=pseg,poff;r.al=rb(mem,r,0x10);r.ah=0
                r=yield from guest(mem,r,'214B:0C57',3,r.ax,ret='1771:390B')
                bright=bool(r.al)
        if bright:mem.wds8(0xAAB2,15,'1771:390F')
        else:
            r.es,r.di=pseg,poff;r.al=rb(mem,r,6);r.ah=0
            r=yield from guest(mem,r,'1771:2E20',word,r.ax,ret='1771:3927')
            mem.wds8(0xAAB2,r.al,'1771:3927')
        r.di=0xE86;source=mem.DS,r.di
        r.al=ss16(mem,r,r.bp+6)&255;row=r.ax
        r.al=ss16(mem,r,r.bp+4)&255
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:01A3','1771:3941')
    return _end(r)


@PORTS.port('1771:2EE5',ret='retf 6')
def player_name_memory(mem,variant):
    r=Regs(mem);r.enter(0x104)
    word=ss16(mem,r,r.bp+10)
    player_of(mem,r,word)
    r.local16(-4,r.di);r.local16(-2,r.es)
    r.al=rb(mem,r,6);r.ah=0
    r=yield from guest(mem,r,'1771:2E20',word,r.ax,ret='1771:2F11')
    colour=r.ax;r.push(colour)
    r.di=(r.bp-0x104)&65535;temporary=r.di
    r.push(r.ss);r.push(temporary)
    r=yield from guest(mem,r,'1771:2E93',word,ret='1771:2F1F')
    r.al=ss16(mem,r,r.bp+8)&255;row=r.ax
    r.al=ss16(mem,r,r.bp+6)&255
    r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:02C8','1771:2F31',colour,6)
    return _end(r)


@PORTS.port('1771:2F37',ret='retf 6')
def squad_row_memory(mem,variant):
    r=Regs(mem);r.enter(0x104)
    word=ss16(mem,r,r.bp+10)
    pseg,poff=player_of(mem,r,word)
    r.local16(-4,poff);r.local16(-2,pseg)
    if word:
        r=yield from guest(mem,r,'1771:2EE5',word,ss16(mem,r,r.bp+8),ss16(mem,r,r.bp+6),ret='1771:2F67')
        r.es,r.di=pseg,poff;r.al=rb(mem,r,6);r.ah=0;r.di=r.ax
        r.al=mem.ds8((r.di+0x699A)&65535);colour=r.ax;r.push(colour)
        r.di=(r.bp-0x104)&65535;temporary=r.di
        r.push(r.ss);r.push(temporary)
        r.es,r.di=pseg,poff;r.al=rb(mem,r,6);r.ah=0;r.di=r.ax
        r.al=mem.ds8((r.di+0x69A8)&65535)
        r=yield from guest(mem,r,'23E4:075A',r.ax,ret='1771:2F92')
        r.al=ss16(mem,r,r.bp+8)&255;row=r.ax
        r.ax=ss16(mem,r,r.bp+6)+13
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:02C8','1771:2FA7',colour,6)
    return _end(r)


@PORTS.port('1771:0F58',ret='retf 6')
def country_name_memory(mem,variant):
    r=Regs(mem);r.enter()
    word=ss16(mem,r,r.bp+10)
    r.al=mem.ds8(0xA964);cbw(r);r.di=r.ax
    r.al=mem.ds8((r.di+0xD7A)&65535);colour=r.ax
    r.di=0xD6A;source=mem.DS,r.di
    r.al=ss16(mem,r,r.bp+8)&255;row=r.ax
    r.al=ss16(mem,r,r.bp+6)&255
    r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','1771:0F7D',colour)
    if word:
        r=yield from guest(mem,r,'1771:0E24',word,ret='1771:0F89',far=False)
        colour=r.ax;r.push(colour)
        r.ax=word;half(r,'cx',4);r.ax=r.ax<<4
        r.di,r.es=mem.ds16(0x9B68),mem.ds16(0x9B6A);r.di=r.di+r.ax
        source=r.es,r.di
        r.al=ss16(mem,r,r.bp+8)&255;row=r.ax
        r.al=ss16(mem,r,r.bp+6)&255
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','1771:0FAB',colour,2)
    return _end(r)


@PORTS.port('214B:0350',ret='retf 10')
def message_line_memory(mem,variant):
    r=Regs(mem);r.enter(0x15A)
    seg,off=farg(mem,r,10)
    r.di=(r.bp-0x51)&65535;line=r.di;r.ax=80
    r=yield from guest(mem,r,'23E4:0644',seg,off,r.ss,line,r.ax,ret='214B:036A')
    expression=(r.bp-0x159)&65535
    if mem.u8(mem.ss_lin(r.bp-0x50))!=32:
        r.di=expression;r.push(r.ss);r.push(r.di)
        r.di=0x343
        r=yield from guest(mem,r,'23E4:062A',mem.seg(0x214B),r.di,ret='214B:0380')
        r.di=line
        r=yield from guest(mem,r,'23E4:06B7',r.ss,r.di,ret='214B:038A')
        r.di=line;r.ax=80;r.sp=r.sp+4
        r=yield from guest(mem,r,'23E4:0644',r.ss,expression,r.ss,line,r.ax,ret='214B:0398')
    r.di=expression;r.push(r.ss);r.push(r.di)
    r.di=line
    r=yield from guest(mem,r,'23E4:062A',r.ss,r.di,ret='214B:03A8')
    r.di=0x343
    r=yield from guest(mem,r,'23E4:06B7',mem.seg(0x214B),r.di,ret='214B:03B2')
    r.di=line;r.ax=80;r.sp=r.sp+4
    r=yield from guest(mem,r,'23E4:0644',r.ss,expression,r.ss,line,r.ax,ret='214B:03C0')
    r.al=mem.u8(mem.ss_lin(line));r.ah=0;length=r.ax;r.local16(-0x53,length)
    r.ax=length+1;r.di=r.ax;r.di=r.bp+r.di-0x51;destination=r.ss,r.di
    r.ax=80-length;count=r.ax;r.ax=0xFE
    r=yield from guest(mem,r,'214B:0018',*destination,count,r.ax,ret='214B:03E2')
    r.ax=80-length;r.dx=0;r.cx=2
    dividend=r.ax;r.ax,r.dx=dividend//2,dividend%2;r.ax=r.ax+1
    centre=r.ax;r.local16(-0x55,centre)
    r.di=(r.bp-0x50)&65535;source=r.ss,r.di
    r.di=r.bp+centre-0x51
    r=yield from guest(mem,r,'214B:003C',*source,r.ss,r.di,length,ret='214B:0407')
    r.di=(r.bp-0x50)&65535;destination=r.ss,r.di
    r.ax=centre-1;count=r.ax;r.ax=0xFE
    r=yield from guest(mem,r,'214B:0018',*destination,count,r.ax,ret='214B:0419')
    r.local8(-0x51,80)
    r.di=line
    r=yield from guest(mem,r,'23E4:06E3',mem.seg(0x214B),0x345,r.ss,r.di,ret='214B:042C')
    matched=bool(r.ax)
    r.al=0x82 if matched else mem.ds8(0x7922);colour=r.ax
    r.di=line;source=r.ss,r.di
    r.al=ss16(mem,r,r.bp+14)&255;row=r.ax;r.al=1;column=r.ax
    seg,off=farg(mem,r,6)
    r=yield from guest(mem,r,'214B:02C8',colour,*source,row,column,seg,off,
                       ret='214B:0463' if matched else '214B:0449')
    r.di=line
    r=yield from guest(mem,r,'23E4:06E3',mem.seg(0x214B),0x348,r.ss,r.di,ret='214B:0472')
    found=r.ax;r.local16(-0x57,found)
    if found:
        for extra,ret in ((3,'214B:04AF'),(5,'214B:04E1')):
            r.ax=(found+extra)<<1;r.cx=r.ax
            r.al=ss16(mem,r,r.bp+14)&255;r.ah=0;r.dx=160;mul(r,r.dx)
            farg(mem,r,6);ptr=mem.addr(r.es,r.di);r.di,r.es=mem.u16(ptr),mem.u16(ptr+2)
            r.di=r.di+r.ax+r.cx-0xA2;destination=r.es,r.di
            r.al=mem.ds8(0x7923);r.ah=0;colour=r.ax;r.ax=1
            r=yield from guest(mem,r,'214B:00DB',*destination,colour,r.ax,ret=ret)
    return _end(r)


@PORTS.port('0791:A75D',ret='ret')
def lineup_memory(mem,variant):
    """A75D-A840: the team menu's concrete buffer/ABI effects, without a user-facing backend."""
    r=Regs(mem);r.enter(0x108);r.di=0x534A
    r=yield from guest(mem,r,'A699',mem.DS,r.di,ret='A76C',far=False)
    for side in range(2):
        r.local8(-1,side)
        r.al=side;cbw(r);r.di=r.ax<<1
        sqseg,sqoff=squad_of(mem,r,mem.ds16((r.di+0x9B34)&65535))
        r.local16(-7,sqoff);r.local16(-5,sqseg)
        r.al=side;cbw(r);r.di=r.ax<<1;country=mem.ds16((r.di+0x9B34)&65535)
        r.ax=8;row=r.ax;r.al=side;cbw(r);r.di=r.ax
        r.al=mem.ds8((r.di+0x8C6)&65535);r.ah=0
        r=yield from guest(mem,r,'1771:0F58',country,row,r.ax,ret='A7B4')
        r.al=7;colour=r.ax;r.push(colour)
        r.di=(r.bp-0x107)&65535;temporary=r.di;r.push(r.ss);r.push(temporary)
        r.al=side;cbw(r);r.di=r.ax<<1
        country=mem.ds16((r.di+0x9B34)&65535)
        r=yield from guest(mem,r,'1771:0E6C',country,ret='A7CE')
        r.al=11;row=r.ax;r.al=side;cbw(r);r.di=r.ax
        r.al=mem.ds8((r.di+0x8CA)&65535)
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:0205','A7E6',colour,6)
        for slot in range(1,12):
            r.local16(-3,slot)
            r.ax=slot<<1;r.es,r.di=sqseg,sqoff+r.ax;word=rw(mem,r,-2)
            r.ax=slot+12;row=r.ax;r.al=side;cbw(r);r.di=r.ax
            r.al=mem.ds8((r.di+0x8C8)&65535);r.ah=0
            r=yield from guest(mem,r,'1771:2F37',word,row,r.ax,ret='A817')
    r.di,r.es=mem.ds16(0x7C2A),mem.ds16(0x7C2C)
    r=yield from guest(mem,r,'A6E4',r.es,r.di,ret='A82F',far=False)
    country=r.ax;r.ax=7;row=r.ax;r.ax=38
    r=yield from guest(mem,r,'1771:0F58',country,row,r.ax,ret='A83D')
    return _end(r)


@PORTS.port('214B:13C5',ret='retf 6')
def highlight_memory(mem,variant):
    r=Regs(mem);r.enter()
    r.ax=ss16(mem,r,r.bp+8)<<1;r.cx=r.ax
    r.ax=ss16(mem,r,r.bp+10);r.dx=160;mul(r,r.dx)
    r.di,r.es=mem.ds16(0xA96E),mem.ds16(0xA970)
    r.di=r.di+r.ax+r.cx-0xA2;destination=r.es,r.di;r.ax=0x70
    r=yield from guest(mem,r,'214B:00DB',*destination,r.ax,ss16(mem,r,r.bp+6),ret='214B:13F0')
    return _end(r)


@PORTS.port('1771:3947',ret='ret 6')
def skill_bars_memory(mem,variant):
    r=Regs(mem);r.enter(10)
    pseg,poff=player_of(mem,r,ss16(mem,r,r.bp+8))
    r.local16(-10,poff);r.local16(-8,pseg)
    mem.wds8(0xAAB2,0x70,'1771:3961')
    r.al=rb(mem,r,4);r.ah=0;ability=r.ax;r.local16(-4,ability)
    ability=(ability+1)&65535;r.local16(-4,ability)
    for skill in range(1,13):
        r.local16(-2,skill);r.ax=skill;r.cx=r.ax
        r.es,r.di=pseg,poff;r.al=rb(mem,r,7);r.ah=0;r.dx=12;mul(r,r.dx)
        r.di=r.ax+r.cx;r.al=mem.ds8((r.di+0x6D25)&65535);r.ah=0;r.cx=r.ax
        r.es,r.di=pseg,poff;r.al=rb(mem,r,5);r.ah=0;r.dx=12;mul(r,r.dx)
        r.di=r.ax+r.cx;r.al=mem.ds8((r.di+0x6DCD)&65535);r.ah=0
        value=r.ax;r.local16(-6,value);mul(r,ability)
        r.dx=0;r.cx=256;dividend=r.ax;r.ax,r.dx=dividend//256,dividend%256
        amount=r.ax;r.local16(-6,amount)
        r.ax=ss16(mem,r,r.bp+4)<<1;r.cx=r.ax
        r.ax=ss16(mem,r,r.bp+6)+skill;r.dx=160;mul(r,r.dx)
        r.di,r.es=mem.ds16(0xA96E),mem.ds16(0xA970)
        r.di=r.di+r.ax+r.cx-0xA2;destination=r.es,r.di
        r.al=mem.ds8(0xAAB2);r.ah=0
        r=yield from guest(mem,r,'214B:00DB',*destination,r.ax,amount,ret='1771:39F7')
    return _end(r)


@PORTS.port('1771:3AE2',ret='ret 4')
def mark_text_memory(mem,variant):
    r=Regs(mem);r.enter();flag=ss16(mem,r,r.bp+6)&255
    if mem.ds8(0xC1E) and flag:
        r.di=0x3AD5;source=mem.seg(0x1771),r.di
        r.al=16;row=r.ax;r.al=61
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:01A3','1771:3B07')
    else:
        r.al=flag;cbw(r);r.dx=11;mul(r,r.dx);r.di=r.ax+0xE90;source=mem.DS,r.di
        r.al=16;row=r.ax;r.al=61
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:01A3','1771:3B2A')
    return _end(r)


@PORTS.port('1771:3B3F',ret='ret 2')
def mark_row_memory(mem,variant):
    r=Regs(mem);r.enter(8);r.di=ss16(mem,r,r.bp+4)
    pseg,poff=player_of(mem,r,ss16(mem,r,r.di+4))
    r.local16(-4,poff);r.local16(-2,pseg)
    if rb(mem,r,6)>=2:
        r.ax=7;r.al=rb(mem,r,0x10);r.ah=0
        r=yield from guest(mem,r,'214B:0C57',7,r.ax,ret='1771:3B7C')
        if r.al:
            r.di=0x3B30;source=mem.seg(0x1771),r.di;r.al=16;row=r.ax;r.al=61
            r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:01A3','1771:3B95')
        else:
            r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0
            squad_of(mem,r,r.ax);r.local16(-8,r.di);r.local16(-6,r.es)
            r.ax=8;r.al=rb(mem,r,0x2D);r.ah=0
            r=yield from guest(mem,r,'214B:0C57',8,r.ax,ret='1771:3BC3')
            r=yield from guest(mem,r,'1771:3AE2',r.ax,r.bp,ret='1771:3BC8',far=False)
    return _end(r)


@PORTS.port('1771:3BD3',ret='ret 2')
def tactics_panel_memory(mem,variant):
    r=Regs(mem);r.enter(0x20E);word=ss16(mem,r,r.bp+4)
    pseg,poff=player_of(mem,r,word)
    r.local16(-0x10D,poff);r.local16(-0x10B,pseg)
    keeper=rb(mem,r,6)==0
    saved=(r.bp-0x108)&65535
    if keeper:
        r.di=saved;r.ax=256
        r=yield from guest(mem,r,'214B:003C',mem.DS,0x6AC0,r.ss,r.di,r.ax,ret='1771:3C0F')
        for source,dest,ret in ((0xEA6,0x6AC0,'1771:3C22'),(0xEC6,0x6B00,'1771:3C35')):
            r.di=dest;r.ax=32
            r=yield from guest(mem,r,'214B:003C',mem.DS,source,mem.DS,r.di,r.ax,ret=ret)
    for tactic in range(1,5):
        r.local16(-2,tactic);r.ax=tactic+4
        r.es,r.di=pseg,poff;r.al=rb(mem,r,0xF);r.ah=0
        r=yield from guest(mem,r,'214B:0C57',tactic+4,r.ax,ret='1771:3C56')
        override=bool(r.al)
        if override:
            r.di=(r.bp-0x20D)&65535;temporary=r.di;r.push(r.ss);r.push(temporary)
            r.es,r.di=pseg,poff;r.al=rb(mem,r,0xF);r.ah=0
            r=yield from guest(mem,r,'214B:0C57',tactic,r.ax,ret='1771:3C73')
            cbw(r);half(r,'cx',4);r.ax=r.ax<<4
            r.di=tactic;half(r,'cx',5);r.di=(r.di<<5)+r.ax+0x6AA0
            r=yield from guest(mem,r,'23E4:062A',mem.DS,r.di,ret='1771:3C8C')
            r.di=0x3BCE
            r=yield from guest(mem,r,'23E4:06B7',mem.seg(0x1771),r.di,ret='1771:3C96')
            r.ax=tactic+11;row=r.ax;r.al=61
            r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:01A3','1771:3CAA',held=4)
        else:
            r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0
            squad_of(mem,r,r.ax);r.local16(-0x111,r.di);r.local16(-0x10F,r.es)
            r.al=rb(mem,r,0x2D);r.ah=0
            r=yield from guest(mem,r,'214B:0C57',tactic,r.ax,ret='1771:3CDB')
            cbw(r);half(r,'cx',4);r.ax=r.ax<<4
            r.di=tactic;half(r,'cx',5);r.di=(r.di<<5)+r.ax+0x6AA0;source=mem.DS,r.di
            r.ax=tactic+11;row=r.ax;r.al=61
            r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:01A3','1771:3D03')
    r.ax=0;slot=0;r.local16(-6,slot)
    if not mem.ds8(0xC1E):
        r=yield from guest(mem,r,'1771:3B3F',r.bp,ret='1771:3D1C',far=False)
    else:
        r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0
        r=yield from guest(mem,r,'1771:3A82',word,r.ax,ret='1771:3D30')
        slot=r.ax;r.local16(-6,slot)
        r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0;r.al=int(r.ax==mem.ds16(0x9B36))
        side=r.al;r.local8(-0x109,side)
        marked=0
        if slot:
            r.ax=slot<<1;r.cx=r.ax;r.al=side;cbw(r);r.dx=40;mul(r,r.dx)
            r.di=r.ax+r.cx;marked=mem.ds16((r.di+0x9A3E)&65535)
        if not slot or not marked:
            r=yield from guest(mem,r,'1771:3B3F',r.bp,ret='1771:3D72',far=False)
        else:
            r.al=mem.ds8(0xAAB2);r.ah=0;attribute=r.ax;r.local16(-4,attribute)
            r.ax=slot<<1;r.cx=r.ax;r.al=side;cbw(r);r.dx=40;mul(r,r.dx)
            r.di=r.ax+r.cx;r.ax=mem.ds16((r.di+0x9A3E)&65535);marked=r.ax;r.local16(-8,marked)
            r.ax=16;row=r.ax;r.ax=43
            r=yield from guest(mem,r,'1771:2EE5',marked,row,r.ax,ret='1771:3DA8')
            player_of(mem,r,marked);r.al=rb(mem,r,6);r.ah=0;r.dx=19;mul(r,r.dx)
            r.di=r.ax+0x69B6;source=mem.DS,r.di;r.al=17;row=r.ax;r.al=43
            r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:026D','1771:3DD9')
            r.ax=7;r.es,r.di=pseg,poff;r.al=rb(mem,r,0x10);r.ah=0
            r=yield from guest(mem,r,'214B:0C57',7,r.ax,ret='1771:3DED')
            if r.al:
                r.al=attribute&255;colour=r.ax;r.di=0x3BD1;source=mem.seg(0x1771),r.di
                r.al=16;row=r.ax;r.al=61
                r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','1771:3E0A',colour)
    r.es,r.di=pseg,poff
    if rb(mem,r,6)==0:
        r.di=0x6AC0;r.ax=256
        r=yield from guest(mem,r,'214B:003C',r.ss,saved,mem.DS,r.di,r.ax,ret='1771:3E29')
    return _end(r)


@PORTS.port('1771:42BC',ret='retf 2')
def player_card_memory(mem,variant):
    """42BC-4856: compatibility memory effects of the original card, not a UI/backend."""
    r=Regs(mem);r.enter(0x108);r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',mem.DS,0x486E,mem.DS,r.di,ret='1771:42D2')
    word=ss16(mem,r,r.bp+6)
    if not word:return _end(r)
    pseg,poff=player_of(mem,r,word);r.local16(-8,poff);r.local16(-6,pseg)
    r.ax=8;row=r.ax;r.ax=2
    r=yield from guest(mem,r,'1771:2EE5',word,row,r.ax,ret='1771:42FE')
    for field,byte,column,formatted,written in ((1,True,19,'4316','4326'),(8,False,24,'433C','434C'),
                                               (10,False,30,'4362','4372')):
        r.di=(r.bp-0x108)&65535;temporary=r.di;r.push(r.ss);r.push(temporary)
        r.es,r.di=pseg,poff
        if byte:r.al=rb(mem,r,field);r.ah=0
        else:r.ax=rw(mem,r,field)
        r.dx=0
        r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='1771:'+formatted)
        r.al=8;row=r.ax;r.al=column
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:01A3','1771:'+written,held=4)
    for remainder,column,height_ret,formatted,written,target in (
            (False,33,'437F','438F','439F','214B:026D'),(True,36,'43AC','43BD','43CD','214B:01A3')):
        r.di=(r.bp-0x108)&65535;temporary=r.di;r.push(r.ss);r.push(temporary)
        r=yield from guest(mem,r,'1771:2FAD',word,ret='1771:'+height_ret)
        r.dx=0;r.cx=12;dividend=r.ax;r.ax,r.dx=dividend//12,dividend%12
        if remainder:r.ax,r.dx=r.dx,r.ax
        r.dx=0
        r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='1771:'+formatted)
        r.al=8;row=r.ax;r.al=column
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,target,'1771:'+written,held=4)
    r=yield from guest(mem,r,'1771:3041',word,ret='1771:43D4')
    if r.al:
        r.di=0x425D;source=mem.seg(0x1771),r.di;r.al=8;row=r.ax;r.al=40
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:026D','1771:43ED')
    else:
        r=yield from guest(mem,r,'1771:3088',word,ret='1771:43F6')
        cbw(r);r.di=r.ax<<1;r.si=r.di;r.di=(r.di<<1)+r.si+0xF2C
        source=mem.DS,r.di;r.al=8;row=r.ax;r.al=40
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:026D','1771:4417')
    for field,column,ret in ((6,2,'1771:443D'),(7,21,'1771:4463')):
        r.es,r.di=pseg,poff;r.al=rb(mem,r,field);r.ah=0;r.dx=19;mul(r,r.dx)
        r.di=r.ax+0x69B6;source=mem.DS,r.di;r.al=10;row=r.ax;r.al=column
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:026D',ret)

    def label(table,row,ret):
        r.di=r.ax;r.al=mem.ds8((r.di+table)&65535);r.ah=0;r.di=r.ax
        half(r,'cx',4);r.di=(r.di<<4)+0x6EB4;source=mem.DS,r.di
        r.al=row;rowword=r.ax;r.al=48
        return (yield from write_buffer_text(mem,r,source,rowword,r.ax,'214B:026D',ret))

    r=yield from guest(mem,r,'1771:2FFB',word,ret='1771:446A');r.ah=0
    r=yield from label(0x78C4,19,'1771:4490')
    r.es,r.di=pseg,poff;injured=rb(mem,r,14)==0
    r.al=rb(mem,r,14 if injured else 13);cbw(r)
    r=yield from label(0x78D5,20,'1771:44C6' if injured else '1771:44F4')
    r.es,r.di=pseg,poff;r.al=rb(mem,r,14);cbw(r)
    r=yield from label(0x78F6,21,'1771:4520')
    r.es,r.di=pseg,poff;r.al=rb(mem,r,12);cbw(r);cwd(r);high,low=r.dx,r.ax
    r.ax=32;r.dx=0
    r=yield from guest(mem,r,'214B:0D1C',high,low,r.dx,r.ax,ret='1771:4537')
    r=yield from label(0x78A3,22,'1771:455B')
    r=yield from guest(mem,r,'1771:30D9',word,ret='1771:4562')
    r=yield from label(0x7917,23,'1771:4586')
    r.es,r.di=pseg,poff
    if s8(rb(mem,r,12))<32:
        r.ax=48;r.al=rb(mem,r,12);cbw(r);r.cx=14;imul(r,r.cx);idiv_by(r,32)
        r=yield from guest(mem,r,'214B:13C5',22,48,r.ax,ret='1771:45B1')
    r.es,r.di=pseg,poff
    if rb(mem,r,14)!=0:
        r.ax=48;r.al=rb(mem,r,13);cbw(r);r.cx=14;imul(r,r.cx);idiv_by(r,32)
        r=yield from guest(mem,r,'214B:13C5',20,48,r.ax,ret='1771:45DC')
    r.ax=48;r.es,r.di=pseg,poff;r.al=rb(mem,r,14);cbw(r);r.cx=14;imul(r,r.cx);idiv_by(r,32)
    r=yield from guest(mem,r,'214B:13C5',21,48,r.ax,ret='1771:45FD')
    r.ax=19;r.push(r.ax);r.ax=48;r.push(r.ax)
    r=yield from guest(mem,r,'1771:2FFB',word,ret='1771:460C')
    r.ah=0;r.cx=14;imul(r,r.cx);idiv_by(r,16);r.sp=r.sp+4
    r=yield from guest(mem,r,'214B:13C5',19,48,r.ax,ret='1771:461F')
    r.ax=23;r.push(r.ax);r.ax=48;r.push(r.ax)
    r=yield from guest(mem,r,'1771:30D9',word,ret='1771:462E')
    r.cx=14;mul(r,r.cx);r.dx=0;r.cx=7;dividend=r.ax;r.ax,r.dx=dividend//7,dividend%7;r.sp=r.sp+4
    r=yield from guest(mem,r,'214B:13C5',23,48,r.ax,ret='1771:4640')
    r=yield from guest(mem,r,'1771:3BD3',word,ret='1771:4646',far=False)
    r.ax=11
    r=yield from guest(mem,r,'1771:3947',word,r.ax,r.ax,ret='1771:4654',far=False)
    for bit,colour,column,checked,written in ((4,14,40,'4667','4683'),(5,14,42,'4696','46B2'),(6,4,44,'46C5','46E1')):
        r.ax=bit;r.es,r.di=pseg,poff;r.al=rb(mem,r,16);r.ah=0
        r=yield from guest(mem,r,'214B:0C57',bit,r.ax,ret='1771:'+checked)
        if r.al:
            r.al=colour;attribute=r.ax;r.di=0x4268;source=mem.seg(0x1771),r.di
            r.al=10;row=r.ax;r.al=column
            r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','1771:'+written,attribute)
    r.ax=8;r.es,r.di=pseg,poff;r.al=rb(mem,r,16);r.ah=0
    r=yield from guest(mem,r,'214B:0C57',8,r.ax,ret='1771:46F4')
    if r.al:
        r.al=4;attribute=r.ax;r.di=0x426A;source=mem.seg(0x1771),r.di
        r.al=10;row=r.ax;r.al=61
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:0205','1771:4710',attribute)
    else:
        r.es,r.di=pseg,poff
        if rb(mem,r,14)==0:
            r.al=6;attribute=r.ax;r.di=0x4274;source=mem.seg(0x1771),r.di
            r.al=10;row=r.ax;r.al=61
            r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:0205','1771:4735',attribute)
        else:
            handled=False
            for bit,colour,text,checked,written in ((5,5,0x427C,'474B','4767'),(6,4,0x4283,'477D','4799'),(3,15,0x428C,'47AF','47CB')):
                r.ax=bit;r.es,r.di=pseg,poff;r.al=rb(mem,r,16);r.ah=0
                r=yield from guest(mem,r,'214B:0C57',bit,r.ax,ret='1771:'+checked)
                if r.al:
                    r.al=colour;attribute=r.ax;r.di=text;source=mem.seg(0x1771),r.di
                    r.al=10;row=r.ax;r.al=61
                    r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:0205','1771:'+written,attribute)
                    handled=True;break
            if not handled:
                mem.wds8(0xAAB2,15,'1771:47CD')
                r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0
                r=yield from guest(mem,r,'1771:3A82',word,r.ax,ret='1771:47E2')
                if r.ax:
                    if not mem.ds8(0xC1E):text,ret=0x4298,'1771:4802'
                    else:
                        r.es,r.di=pseg,poff;r.al=rb(mem,r,0);r.ah=0
                        r=yield from guest(mem,r,'1771:3A82',word,r.ax,ret='1771:4814')
                        text,ret=(0x42A6,'1771:482E') if r.ax<12 else (0x42AF,'1771:4845')
                    r.di=text;source=mem.seg(0x1771),r.di;r.al=10;row=r.ax;r.al=61
                    r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:01A3',ret)
    r.ax=8;row=r.ax;r.ax=60
    r=yield from guest(mem,r,'1771:3827',word,row,r.ax,ret='1771:4853',far=False)
    return _end(r)


@PORTS.port('0791:1829',ret='ret 6')
def commentary_line_memory(mem,variant):
    """1829-19E3: expand the commentary record, preserving its local and buffer writes."""
    r=Regs(mem);r.enter(0x128)
    r.di=ss16(mem,r,r.bp+8)*6+0x7C38;record=r.di
    r.local16(-0x28,r.di);r.local16(-0x26,mem.DS)
    r.es=mem.DS
    if mem.ds8(record)==255:
        return _end(r)
    r.al=mem.ds8(record);cbw(r);r.dx=21;mul(r,r.dx);r.di=r.ax+0xBE
    source=mem.DS,r.di
    line=(r.bp-0x24)&65535;expression=(r.bp-0x128)&65535
    r.di=line;r.ax=35
    r=yield from guest(mem,r,'23E4:0644',*source,r.ss,line,r.ax,ret='0791:1873')
    if mem.u8(mem.ss_lin(line)):
        if mem.u8(mem.ss_lin(line+1))==1:
            r.local8(-0x23,32)
            r.di=expression;r.push(r.ss);r.push(r.di)
            r.ax=mem.ds16(record+1);r.dx=11;mul(r,r.dx)
            r.di=mem.ds16(0x9B6C)+r.ax;r.es=mem.ds16(0x9B6E)
            r=yield from guest(mem,r,'23E4:062A',r.es,r.di,ret='0791:18A5')
            r.di=line
            r=yield from guest(mem,r,'23E4:06B7',r.ss,r.di,ret='0791:18AF')
            r.di=line;r.ax=35;r.sp=r.sp+4
            r=yield from guest(mem,r,'23E4:0644',r.ss,expression,r.ss,line,r.ax,ret='0791:18BD')
        for marker,field,store_ret,concat_ret,name_ret,end_ret in (
                (1,1,'0791:18DD','0791:18E7','0791:1900','0791:190E'),
                (2,3,'0791:192E','0791:1938','0791:1951','0791:195F')):
            r.al=mem.u8(mem.ss_lin(line));r.ah=0;r.di=r.ax
            if mem.u8(mem.ss_lin(line+r.di))==marker:
                r.local8(-0x24,(mem.u8(mem.ss_lin(line))-1)&255)
                r.di=expression;r.push(r.ss);r.push(r.di)
                r.di=line
                r=yield from guest(mem,r,'23E4:062A',r.ss,r.di,ret=store_ret)
                r.di=0x1827
                r=yield from guest(mem,r,'23E4:06B7',mem.seg(0x0791),r.di,ret=concat_ret)
                r.ax=mem.ds16(record+field);r.dx=11;mul(r,r.dx)
                r.di=mem.ds16(0x9B6C)+r.ax;r.es=mem.ds16(0x9B6E)
                r=yield from guest(mem,r,'23E4:06B7',r.es,r.di,ret=name_ret)
                r.di=line;r.ax=35;r.sp=r.sp+4
                r=yield from guest(mem,r,'23E4:0644',r.ss,expression,r.ss,line,r.ax,ret=end_ret)
    length=mem.u8(mem.ss_lin(line))
    if length<30:
        r.al=length;r.ah=0;r.ax=r.ax+1;r.di=r.bp+r.ax-0x24
        destination=r.ss,r.di;r.al=length;r.ah=0;r.dx=r.ax;r.ax=30-r.dx
        count=r.ax;r.ax=32
        r=yield from guest(mem,r,'214B:0018',*destination,count,r.ax,ret='0791:1988')
    r.local8(-0x24,30)
    for pointer,ret in ((0xA96A,'0791:19B2'),(0xA972,'0791:19DE')):
        if pointer==0xA972 and ss16(mem,r,r.bp+6)>4:
            break
        r.al=mem.ds8(record+5);cbw(r);r.di=r.ax;r.al=mem.ds8(0x832E+r.di);colour=r.ax
        r.di=line;source=r.ss,r.di
        r.al=ss16(mem,r,r.bp+6)&255;row=r.ax
        r.al=ss16(mem,r,r.bp+4)&255;column=r.ax;r.di=pointer
        r=yield from guest(mem,r,'214B:02C8',colour,*source,row,column,mem.DS,r.di,ret=ret)
    return _end(r)


@PORTS.port('0791:0481',ret='ret 4')
def digit_vertical_memory(mem,variant):
    r=Regs(mem);r.enter(0)
    parent=ss16(mem,r,r.bp+4)
    for delta,glyph,at in ((0,0xDC,'049E'),(80,0xDB,'04BF')):
        r.di=parent;r.ax=ss16(mem,r,parent+4)+glyph;r.dx=r.ax
        r.ax=ss16(mem,r,r.bp+6)+delta;r.ax=r.ax<<1
        r.di=parent;r.es=ss16(mem,r,parent-8);r.di=ss16(mem,r,parent-10)+r.ax
        w16(mem,r,-2,r.dx,at)
    return _end(r)


@PORTS.port('0791:04C9',ret='ret 6')
def digit_segments_memory(mem,variant):
    r=Regs(mem);r.enter(2);r.local16(-2,1)
    parent=ss16(mem,r,r.bp+4)
    for index in range(1,8):
        if index!=1:r.local16(-2,index)
        r.al=ss16(mem,r,r.bp+8)&255;r.ah=0;r.cx=r.ax
        r.ax=index;r.dx=10;mul(r,r.dx);r.di=r.ax+r.cx
        if mem.ds8(r.di+0x644):
            r.ax=ss16(mem,r,r.bp+6);r.di=index<<1;r.ax=r.ax+mem.ds16(r.di+0x6C2)
            if index<4:
                r.ax=(r.ax+1)<<1
                r.di=parent;r.es=ss16(mem,r,parent-8);r.di=ss16(mem,r,parent-10)+r.ax-2
                destination=r.es,r.di;r.ax=4;count=r.ax;r.di=parent
                r.ax=ss16(mem,r,parent+4)+0xDF
                r=yield from guest(mem,r,'214B:0000',*destination,count,r.ax,ret='0791:052B')
            else:
                r=yield from guest(mem,r,'0791:0481',r.ax,parent,ret='0791:0540',far=False)
    return _end(r)


@PORTS.port('0791:054C',ret='ret 4')
def big_digits_memory(mem,variant):
    r=Regs(mem);r.enter(0x10C)
    r.di=mem.ds16(0xA96A);r.es=mem.ds16(0xA96C);r.ax=r.di;r.dx=r.es
    r.local16(-10,r.ax);r.local16(-8,r.dx)
    r.ax=ss16(mem,r,r.bp+4);r.cx=8;r.ax=r.ax<<8;r.local16(4,r.ax)
    r.di=0x613E;source=mem.DS,r.di;r.di=0xA96A
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='0791:057B')
    expression=(r.bp-0x10B)&65535;line=(r.bp-6)&65535
    r.di=expression;r.push(r.ss);r.push(r.di)
    r.ax=ss16(mem,r,r.bp+6);r.dx=0
    r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='0791:058D')
    r.di=line;r.ax=5;r.sp=r.sp+4
    r=yield from guest(mem,r,'23E4:0644',r.ss,expression,r.ss,line,r.ax,ret='0791:059B')
    if mem.u8(mem.ss_lin(line))==2:
        r.al=mem.u8(mem.ss_lin(line+1));digit=r.ax;r.ax=0x45
        r=yield from guest(mem,r,'0791:04C9',digit,r.ax,r.bp,ret='0791:05AD',far=False)
    r.al=mem.u8(mem.ss_lin(line));r.ah=0;r.di=r.ax
    r.al=mem.u8(mem.ss_lin(line+r.di));digit=r.ax;r.ax=0x4B
    r=yield from guest(mem,r,'0791:04C9',digit,r.ax,r.bp,ret='0791:05C0',far=False)
    return _end(r)


@PORTS.port('214B:1E09',ret='retf 2')
def delay_frame_memory(mem,variant):
    """1E09-1E57: omit elapsed busy-wait work, retain its exact completed frame."""
    r=Regs(mem);r.enter(8)
    count=ss16(mem,r,r.bp+6)
    if count:
        r.ax=count;r.local16(-8,r.ax)
        r.local16(-2,count)
        r.ax=mem.ds16(0xA9FF);r.dx=mem.ds16(0xAA01)
        r.local16(-6,r.ax);r.local16(-4,r.dx);r.es=r.dx
        r.ax=count
    return _end(r)


@PORTS.port('0791:C50C',ret='ret 4')
def substitution_notice_memory(mem,variant):
    """C50C-C5DB: preserve the notice's buffer/ABI effects and original no-key path."""
    r=Regs(mem);r.enter(0)
    r=yield from guest(mem,r,'214B:0625',ret='0791:C514')
    r.di=0x5F8C;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='0791:C523')
    for field,column,colour_ret,text_target,text_ret in (
            (6,29,'0791:C540','214B:0205','0791:C561'),
            (4,38,'0791:C57E','214B:02C8','0791:C59F')):
        word=ss16(mem,r,r.bp+field)
        player_of(mem,r,word);r.al=rb(mem,r,6);r.ah=0
        r=yield from guest(mem,r,'1771:2E20',word,r.ax,ret=colour_ret)
        colour=r.ax
        r.ax=word;r.dx=11;mul(r,r.dx)
        r.di=mem.ds16(0x9B6C)+r.ax;r.es=mem.ds16(0x9B6E);source=r.es,r.di
        r.al=25;row=r.ax;r.al=column;col=r.ax;r.di=0xA96E
        r=yield from guest(mem,r,text_target,colour,*source,row,col,mem.DS,r.di,ret=text_ret)
    r.es=mem.ds16(0xA96E+2);r.di=mem.ds16(0xA96E)+0xF00;source=r.es,r.di
    r.es=mem.ds16(0xA96A+2);r.di=mem.ds16(0xA96A)+0xF00;destination=r.es,r.di;r.ax=160
    r=yield from guest(mem,r,'214B:003C',*source,*destination,r.ax,ret='0791:C5BC')
    r.ax=300
    r=yield from guest(mem,r,'0791:CC2E',r.ax,ret='0791:C5C3',far=False)
    r=yield from guest(mem,r,'214B:0723',ret='0791:C5C8')
    if r.al:
        r=yield from guest(mem,r,'214B:08DD',ret='0791:C5D1')
    r=yield from guest(mem,r,'214B:0643',ret='0791:C5D6')
    return _end(r)


@PORTS.port('214B:1EBC',ret='retf 2')
def tone_frequency_memory(mem,variant):
    """1EBC-1EF0: keep the PIT divisor's argument/frame writes; omit device output."""
    r=Regs(mem);r.enter()
    if not mem.ds8(0xA9FC):
        r=yield from guest(mem,r,'214B:1E75',ret='214B:1ECA')
        r.ax=ss16(mem,r,r.bp+6);r.dx=0;r.cx=r.ax;r.bx=r.dx
        r.ax=0x34DD;r.dx=0x12
        r=yield from guest(mem,r,'23E4:0294',ret='214B:1EDE')
        r.local16(6,r.ax)
        r.al=ss16(mem,r,r.bp+6)&255
        r.al=(ss16(mem,r,r.bp+6)>>8)&255
    return _end(r)


@PORTS.port('0791:0441',ret='ret 2')
def whistle_memory(mem,variant):
    r=Regs(mem);r.enter()
    r.es,r.di=mem.ds16(0xA923+2),mem.ds16(0xA923)
    if rb(mem,r,0x3F)>0:
        r=yield from guest(mem,r,'214B:1F87',ss16(mem,r,r.bp+4),ret='0791:0457')
    return _end(r)


@PORTS.port('214B:1E8D',ret='retf')
def speaker_off_frame(mem,variant):
    """1E8D-1EA0: frame and AL on the kit's port61-read-zero path; device output removed."""
    r=Regs(mem);r.enter()
    if not mem.ds8(0xA9FC):
        # Original kit return-register probe: speaker-returns-1.txt (IN61 is zero).
        r.al=0
    return _end(r)


@PORTS.port('214B:1EF1',ret='retf 6')
def note_memory(mem,variant):
    """1EF1-1F86: preserve transposition, real-library calls and note/delay frames."""
    r=Regs(mem);r.enter(2)
    if not mem.ds8(0xA9FC):
        r.al=mem.ds8(0x7968);r.ah=0
        note=(ss16(mem,r,r.bp+8)+r.ax)&65535;r.local16(8,note)
        while note>11:
            r.local16(10,ss16(mem,r,r.bp+10)+1)
            note=(note-12)&65535;r.local16(8,note)
        r.ax=11-note;r.dx=0
        r=yield from guest(mem,r,'23E4:0CB9',ret='214B:1F22')
        r.cx=0x84;r.si=0;r.di=0x4000
        r=yield from guest(mem,r,'23E4:0CAB',ret='214B:1F2F')
        r.push(r.dx);r.push(r.bx);r.push(r.ax)
        r.ax=15-ss16(mem,r,r.bp+10);r.dx=0
        r=yield from guest(mem,r,'23E4:0CB9',ret='214B:1F3F')
        r.cx=pop(mem,r);r.si=pop(mem,r);r.di=pop(mem,r)
        r=yield from guest(mem,r,'23E4:0C93',ret='214B:1F47')
        r.push(r.dx);r.push(r.bx);r.push(r.ax)
        r.ax=0x82;r.bx=0;r.dx=0
        r=yield from guest(mem,r,'23E4:0E67',ret='214B:1F56')
        r.cx=pop(mem,r);r.si=pop(mem,r);r.di=pop(mem,r)
        r=yield from guest(mem,r,'23E4:0CA5',ret='214B:1F5E')
        r=yield from guest(mem,r,'23E4:0F10',ret='214B:1F63')
        r=yield from guest(mem,r,'23E4:0CC5',ret='214B:1F68')
        r.local16(-2,r.ax)
        r.al=ss16(mem,r,r.bp-2)&255
        r.al=(ss16(mem,r,r.bp-2)>>8)&255
    r.ax=ss16(mem,r,r.bp+6);mul(r,mem.ds16(0x7966))
    r=yield from guest(mem,r,'214B:1E09',r.ax,ret='214B:1F81')
    return _end(r)


@PORTS.port('214B:1F87',ret='retf 2')
def jingle_memory(mem,variant):
    """1F87-1FFF: calibration-scaled note pairs, tempo and frame writes, without hardware output."""
    r=Regs(mem);r.enter(10)
    r=yield from guest(mem,r,'214B:1E75',ret='214B:1F91')
    r.ax=mem.ds16(0xA9FF);r.es=mem.ds16(0xAA01);r.dx=r.es;r.cx=10;r.bx=0
    r=yield from guest(mem,r,'23E4:0294',ret='214B:1FA1')
    r.cx=r.ax;r.bx=r.dx;r.ax=ss16(mem,r,r.bp+6);r.dx=0
    r=yield from guest(mem,r,'23E4:0279',ret='214B:1FAF')
    r.local16(6,r.ax);mem.wds16(0x7966,1,'214B:1FB2')
    count=ss16(mem,r,r.bp+6);r.ax=count;r.local16(-10,count);r.ax=1
    if count:
        r.local16(-2,1)
        for index in range(1,count+1):
            if index!=1:r.local16(-2,index)
            r.ax=1
            r=yield from guest(mem,r,'214B:1EF1',6,9,r.ax,ret='214B:1FDE')
            r.ax=1
            r=yield from guest(mem,r,'214B:1EF1',6,7,r.ax,ret='214B:1FEE')
            r.ax=index
    r=yield from guest(mem,r,'214B:1E8D',ret='214B:1FFA')
    return _end(r)


@PORTS.port('1771:8939',ret='ret 2')
def competition_header_memory(mem,variant):
    r=Regs(mem);r.enter(4)
    r.es,r.di=mem.ds16(0xA925),mem.ds16(0xA923)
    r.local16(-4,r.di);r.local16(-2,r.es)
    r=yield from guest(mem,r,'214B:05DB',ret='1771:894E')
    r.di=0x26F2;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:895D')
    parent=ss16(mem,r,r.bp+4)
    if not ss8(mem,r,parent+10):
        source,ret=0x14A6,'1771:8976'
        r.di=source;source_ptr=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source_ptr,mem.DS,r.di,ret=ret)
    else:
        r.di=0x2E36;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:8987')
        r.es=ss16(mem,r,r.bp-2);r.di=ss16(mem,r,r.bp-4)
        if rw(mem,r,0x38)>0:
            source,ret=(0x2E0C,'1771:89AA') if ss8(mem,r,parent-9) else (0x2DE4,'1771:89BB')
            r.di=source;source_ptr=mem.DS,r.di;r.di=0xA96E
            r=yield from guest(mem,r,'214B:0329',*source_ptr,mem.DS,r.di,ret=ret)
    return _end(r)


@PORTS.port('1771:958D',ret='retf 6')
def competition_view_memory(mem,variant):
    """958D-96D2: preserve table selection/frame effects and its original key-driven callees."""
    r=Regs(mem);r.enter(14)
    r.es,r.di=mem.ds16(0xA925),mem.ds16(0xA923);game=r.es,r.di
    r.local16(-13,r.di);r.local16(-11,r.es)
    r.ax=ss16(mem,r,r.bp+6);country=r.ax;r.local16(-8,r.ax)
    if rb(mem,r,0x3C)>=7:r.local16(-8,1)
    continent_special=False
    if rb(mem,r,0x3C)==6:
        squad_of(mem,r,country)
        continent_special=rb(mem,r,0x2C)>2
    if continent_special:r.local16(-4,9)
    elif not ss16(mem,r,r.bp+8):r.local16(-4,1)
    else:
        r.ax=ss16(mem,r,r.bp+8);r.local16(-4,r.ax)
    r.ax=country;r.local16(-6,r.ax);r.es,r.di=game;r.al=rb(mem,r,0x3C);stageword=r.ax
    r.di=0x956D
    r=yield from guest(mem,r,'23E4:08DF',stageword,mem.seg(0x1771),r.di,ret='1771:9603')
    r.al=int(member(mem));r.ah=0;r.push(r.ax)
    r=yield from guest(mem,r,'1771:59D8',ret='1771:9612')
    r.ah=0;r.ax=r.ax+1;r.dx=pop(mem,r);r.ax=r.ax+r.dx;r.local16(-2,r.ax)
    r.es,r.di=game;r.al=rb(mem,r,0x40);r.local8(-9,r.al)
    while True:
        r=yield from guest(mem,r,'1771:8939',r.bp,ret='1771:9629',far=False)
        r.ax=ss16(mem,r,r.bp-2)
        if r.ax==1:r=yield from guest(mem,r,'1771:8E9A',r.bp,ret='1771:9635',far=False)
        elif r.ax==2:r=yield from guest(mem,r,'1771:9028',r.bp,ret='1771:9640',far=False)
        elif r.ax==3:r=yield from guest(mem,r,'1771:9509',r.bp,ret='1771:964B',far=False)
        r.al=mem.ds8(0xA976)
        if r.al==32:
            r.di=(r.bp-8)&65535;destination=r.ss,r.di;r.ax=1;lo=r.ax;r.ax=128;hi=r.ax;r.ax=32
            r=yield from guest(mem,r,'214B:1C86',*destination,lo,hi,r.ax,ret='1771:9668')
        elif r.al in (0xAE,0xAF):
            r.di=(r.bp-2)&65535;destination=r.ss,r.di;r.ax=1;lo=r.ax;r.ax=3;hi=r.ax
            r.al=int(mem.ds8(0xA976)==0xAF);cbw(r);r.di=r.ax;r.al=mem.ds8(0x7920+r.di);cbw(r)
            r=yield from guest(mem,r,'214B:1C86',*destination,lo,hi,r.ax,ret='1771:969A')
        elif r.al in (0xB6,0xB7):
            r.es,r.di=game
            if rw(mem,r,0x38)>0:
                r.al=int(not ss8(mem,r,r.bp-9));r.local8(-9,r.al)
        if not ss8(mem,r,r.bp+10) or mem.ds8(0xA976)==27:break
    return _end(r)


@PORTS.port('1771:8CA2',ret='ret 8')
def competition_fixture_memory(mem,variant):
    r=Regs(mem);r.enter()
    fixture=ss16(mem,r,r.bp+10)
    if fixture>0:
        r.ax=fixture;half(r,'cx',3);r.ax=r.ax<<3
        r.es,r.di=mem.ds16(0xA92D),mem.ds16(0xA92B);r.di=r.di+r.ax-8
        r=yield from guest(mem,r,'1771:77C3',r.es,r.di,ss16(mem,r,r.bp+8),ss16(mem,r,r.bp+6),ret='1771:8CC7',far=False)
    return _end(r)


@PORTS.port('1771:8E9A',ret='ret 2')
def competition_groups_memory(mem,variant):
    """8E9A-9027: group table/fixtures and the original one-key selector boundary."""
    r=Regs(mem);r.enter(6);parent=ss16(mem,r,r.bp+4)
    squad_of(mem,r,ss16(mem,r,parent-8));country=r.es,r.di
    r.local16(-6,r.di);r.local16(-4,r.es)
    if ss16(mem,r,parent-4)>8:
        if rb(mem,r,0x2C)<3 or not ss8(mem,r,parent-9):
            mem.w16(mem.ss_lin(parent-4),1,'1771:8ED9')
    group=ss16(mem,r,parent-4)
    template=0x36F2 if group==9 else 0x351E;r.di=template;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:8EF8' if group==9 else '1771:8F22')
    if ss8(mem,r,parent+10):
        r.di=0x2D3C if group==9 else 0x2D5A;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:8F11' if group==9 else '1771:8F3B')
    if ss8(mem,r,parent+10):
        r.al=1
        r=yield from guest(mem,r,'1771:8A5D',r.ax,parent,ret='1771:8F4E',far=False)
    r.al=0;flag=r.ax;r.al=ss8(mem,r,parent-9);snapshot=r.ax
    r.es,r.di=country;r.al=rb(mem,r,0x2C);r.ah=0
    r=yield from guest(mem,r,'1771:5AC4',flag,snapshot,r.ax,ret='1771:8F66',far=False)
    r.di=0x142A;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:8F75')
    if ss16(mem,r,parent-4)==9:
        r=yield from guest(mem,r,'1771:8D84',parent,ret='1771:8F85',far=False)
    else:
        r.al=0
        r=yield from guest(mem,r,'1771:8A87',r.ax,parent,ret='1771:8F90',far=False)
        r.local16(-2,1)
        for index in range(1,13):
            if index!=1:r.local16(-2,index)
            r.ax=index<<1;r.push(r.ax)
            r.ax=ss16(mem,r,parent-4);r.dx=56;mul(r,r.dx);r.bx=r.ax
            r.es,r.di=country;r.al=rb(mem,r,0x2C);r.ah=0;r.dx=0x1C0;mul(r,r.dx);r.cx=r.ax
            r.al=ss8(mem,r,parent-9);cbw(r);r.dx=0xE00;mul(r,r.dx)
            r.es,r.di=mem.ds16(0xA935),mem.ds16(0xA933);r.di=r.di+r.ax+r.cx+r.bx
            r.ax=pop(mem,r);r.di=r.di+r.ax;fixture=rw(mem,r,-0x1DA)
            r.ax=index+7;row=r.ax;r.ax=58
            r=yield from guest(mem,r,'1771:8CA2',fixture,row,r.ax,parent,ret='1771:8FEE',far=False)
    r.di=(parent-4)&65535;destination=r.ss,r.di
    r.al=0
    if ss8(mem,r,parent-9):
        r.es,r.di=country;r.al=int(rb(mem,r,0x2C)>2)
    r.ah=0;r.ax=r.ax+8
    r=yield from guest(mem,r,'214B:1560',*destination,r.ax,ret='1771:9022')
    return _end(r)


@PORTS.port('1771:0FB1',ret='ret 6')
def country_name_right_memory(mem,variant):
    r=Regs(mem);r.enter();word=ss16(mem,r,r.bp+8)
    r.al=mem.ds8(0xA964);cbw(r);r.di=r.ax;r.al=mem.ds8((r.di+0xD7A)&65535);colour=r.ax
    r.di=0xD6A;source=mem.DS,r.di;r.al=ss8(mem,r,r.bp+6);row=r.ax;r.al=ss8(mem,r,r.bp+4)
    r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:0205','1771:0FD6',colour)
    if word:
        r=yield from guest(mem,r,'1771:0E24',word,ret='1771:0FE2',far=False)
        colour=r.ax;r.push(colour);r.ax=word;half(r,'cx',4);r.ax=r.ax<<4
        r.di,r.es=mem.ds16(0x9B68),mem.ds16(0x9B6A);r.di=r.di+r.ax;source=r.es,r.di
        r.al=ss8(mem,r,r.bp+6);row=r.ax;r.al=ss8(mem,r,r.bp+4)
        r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:0205','1771:1004',colour,2)
    return _end(r)


@PORTS.port('1771:76FA',ret='retf 8')
def fixture_score_memory(mem,variant):
    r=Regs(mem);r.enter(0x104);fixture=farg(mem,r,10)
    r.local16(-4,r.di);r.local16(-2,r.es)
    r.al=5;colour=r.ax;r.di=0x76F8;source=mem.seg(0x1771),r.di
    r.al=ss8(mem,r,r.bp+8);row=r.ax;r.al=ss8(mem,r,r.bp+6)
    r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','1771:7724',colour)
    r.es,r.di=fixture
    if rb(mem,r,2) and rb(mem,r,0)<254:
        if rb(mem,r,3)==2:mem.wds8(0xAAB2,6,'1771:7747')
        else:
            r.al=int(rb(mem,r,3)==1);cbw(r);r.di=r.ax;r.al=mem.ds8(0x1108+r.di)
            mem.wds8(0xAAB2,r.al,'1771:7765')
        for field,delta,formatted,written,target in ((1,-1,'7780','7793','214B:01A3'),(0,1,'77AA','77BD','214B:026D')):
            r.di=(r.bp-0x104)&65535;temporary=r.di;r.push(r.ss);r.push(temporary)
            r.es,r.di=fixture;r.al=rb(mem,r,field);r.ah=0;r.dx=0
            r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='1771:'+formatted)
            r.al=ss8(mem,r,r.bp+8);row=r.ax;r.ax=ss16(mem,r,r.bp+6)+delta
            r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,target,'1771:'+written,held=4)
    return _end(r)


@PORTS.port('1771:77C3',ret='ret 8')
def fixture_row_memory(mem,variant):
    r=Regs(mem);r.enter(4);fixture=farg(mem,r,8)
    r.local16(-4,r.di);r.local16(-2,r.es)
    country=rw(mem,r,6);row=ss16(mem,r,r.bp+6);r.ax=ss16(mem,r,r.bp+4)-4
    r=yield from guest(mem,r,'1771:0FB1',country,row,r.ax,ret='1771:77E6',far=False)
    r.es,r.di=fixture;country=rw(mem,r,4);row=ss16(mem,r,r.bp+6);r.ax=ss16(mem,r,r.bp+4)+4
    r=yield from guest(mem,r,'1771:0F58',country,row,r.ax,ret='1771:77FB')
    fixture=farg(mem,r,8)
    r=yield from guest(mem,r,'1771:76FA',*fixture,ss16(mem,r,r.bp+6),ss16(mem,r,r.bp+4),ret='1771:780A')
    return _end(r)


@PORTS.port('1771:8A87',ret='ret 4')
def group_rows_memory(mem,variant):
    """8A87-8CA1: four group records and their exact string temporaries."""
    r=Regs(mem);r.enter(0x10A);parent=ss16(mem,r,r.bp+4)
    squad_of(mem,r,ss16(mem,r,parent-8));country=r.es,r.di
    r.local16(-6,r.di);r.local16(-4,r.es)
    r.al=7;colour=r.ax;r.push(colour)
    header=(r.bp-0x106)&65535;r.di=header;r.push(r.ss);r.push(r.di)
    r.ax=ss16(mem,r,parent-4)+0x40
    r=yield from guest(mem,r,'23E4:075A',r.ax,ret='1771:8ABF')
    r.al=9;row=r.ax;r.al=11
    r=yield from write_buffer_text(mem,r,(r.ss,header),row,r.ax,'214B:02C8','1771:8ACF',colour,6)
    temporary=(r.bp-0x10A)&65535;r.local16(-2,1)
    for index in range(1,5):
        if index!=1:r.local16(-2,index)
        r.ax=index;half(r,'cx',3);r.ax=r.ax<<3;r.push(r.ax)
        r.ax=ss16(mem,r,parent-4);r.dx=56;mul(r,r.dx);r.push(r.ax)
        r.es,r.di=country;r.al=rb(mem,r,0x2C);r.ah=0;r.dx=0x1C0;mul(r,r.dx);r.bx=r.ax
        r.al=ss8(mem,r,r.bp+6);cbw(r);r.dx=0x700;mul(r,r.dx);r.cx=r.ax
        r.al=ss8(mem,r,parent-9);cbw(r);r.dx=0xE00;mul(r,r.dx)
        r.es,r.di=mem.ds16(0xA935),mem.ds16(0xA933);r.di=r.di+r.ax+r.cx+r.bx
        r.ax=pop(mem,r);r.di=r.di+r.ax;r.ax=pop(mem,r);r.di=r.di+r.ax-0x200;record=r.es,r.di
        r.local16(-10,r.di);r.local16(-8,r.es)
        word=rw(mem,r,0);r.ax=index+10;row=r.ax;r.ax=4
        r=yield from guest(mem,r,'1771:0F58',word,row,r.ax,ret='1771:8B45')
        r.di=temporary;r.push(r.ss);r.push(r.di)
        r.es,r.di=record;r.al=rb(mem,r,4);r.ah=0;r.cx=r.ax
        r.al=rb(mem,r,3);r.ah=0;r.dx=r.ax;r.al=rb(mem,r,2);r.ah=0;r.ax=r.ax+r.dx+r.cx+0x30
        r=yield from guest(mem,r,'23E4:075A',r.ax,ret='1771:8B77')
        r.ax=index+10;row=r.ax;r.al=20
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:026D','1771:8B8B',held=4)
        for field,column,formatted,written in ((2,22,'8BA3','8BB7'),(3,24,'8BCF','8BE3'),(4,26,'8BFB','8C0F')):
            r.di=temporary;r.push(r.ss);r.push(r.di);r.es,r.di=record;r.al=rb(mem,r,field);r.ah=0;r.ax=r.ax+0x30
            r=yield from guest(mem,r,'23E4:075A',r.ax,ret='1771:'+formatted)
            r.ax=index+10;row=r.ax;r.al=column
            r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:026D','1771:'+written,held=4)
        for field,column,formatted,written in ((5,29,'8C27','8C3B'),(6,32,'8C53','8C67'),(7,35,'8C7F','8C93')):
            r.di=temporary;r.push(r.ss);r.push(r.di);r.es,r.di=record;r.al=rb(mem,r,field);r.ah=0;r.dx=0
            r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='1771:'+formatted)
            r.ax=index+10;row=r.ax;r.al=column
            r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:01A3','1771:'+written,held=4)
    return _end(r)


@PORTS.port('1771:5AC4',ret='ret 6')
def competition_stage_header_memory(mem,variant):
    r=Regs(mem);r.enter(0x106);r.es,r.di=mem.ds16(0xA925),mem.ds16(0xA923);game=r.es,r.di
    r.local16(-6,r.di);r.local16(-4,r.es)
    r.di=0x1726;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:5AE4')
    snapshot=ss8(mem,r,r.bp+6)
    if snapshot:
        r.di=0x1190;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:5AF9')
    else:
        r.ax=ss16(mem,r,r.bp+4);r.dx=101;mul(r,r.dx);r.di=r.ax+0x1231;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:5B15')
        r.di=0x1230;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:5B24')
    r.al=14;colour=r.ax;r.al=ss8(mem,r,r.bp+8);cbw(r);r.dx=11;mul(r,r.dx);r.di=r.ax+0xF5E;source=mem.DS,r.di
    r.al=snapshot;cbw(r);r.di=r.ax;r.al=mem.ds8((r.di+0xF74)&65535);row=r.ax;r.al=30
    r=yield from write_buffer_text(mem,r,source,row,r.ax,'214B:02C8','1771:5B50',colour)
    r.al=15;colour=r.ax;r.push(colour);temporary=(r.bp-0x106)&65535;r.di=temporary;r.push(r.ss);r.push(r.di)
    r.es,r.di=game;r.al=int(rb(mem,r,0x40)!=snapshot);r.ah=0;r.ax=r.ax<<1;r.dx=r.ax
    r.ax=rw(mem,r,0x38);r.ax=r.ax<<1;r.ax=r.ax+rw(mem,r,0x3A)-r.dx;r.dx=0
    r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='1771:5B8C')
    r.al=snapshot;r.ah=0;r.dx=r.ax;r.ax=2-r.dx;row=r.ax
    r.al=snapshot;r.ah=0;r.ax=r.ax<<1;r.dx=r.ax;r.ax=49-r.dx
    r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:02C8','1771:5BB2',colour,6)
    if snapshot:r.local16(-2,5)
    else:
        r.ax=ss16(mem,r,r.bp+4);r.local16(-2,r.ax)
    r.ax=ss16(mem,r,r.bp-2);r.ax=r.ax<<1;r.es,r.di=game;r.di=r.di+r.ax
    if rw(mem,r,0x2C)>0:
        r.ax=ss16(mem,r,r.bp-2);r.ax=r.ax<<1;r.es,r.di=game;r.di=r.di+r.ax;word=rw(mem,r,0x2C)
        r.ax=1;row=r.ax;r.ax=19
        r=yield from guest(mem,r,'1771:0F58',word,row,r.ax,ret='1771:5BF0')
    return _end(r)


@PORTS.port('1771:4D8A',ret='retf 2')
def squad_list_memory(mem,variant):
    """4D8A-4E21: all twenty squad rows and the gap before the reserves."""
    r=Regs(mem);r.enter(6);country=ss16(mem,r,r.bp+6)
    squad_of(mem,r,country);squad=r.es,r.di
    r.local16(-6,r.di);r.local16(-4,r.es)
    r.di=0x15A4;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:4DB3')
    r.ax=1;row=r.ax;r.ax=65
    r=yield from guest(mem,r,'1771:0F58',country,row,r.ax,ret='1771:4DC2')
    for slot in range(1,21):
        r.local16(-2,slot);r.ax=slot<<1;r.es,r.di=squad;r.di=r.di+r.ax;word=rw(mem,r,-2)
        r.ax=slot+(2 if slot<=11 else 3);row=r.ax;r.ax=65
        r=yield from guest(mem,r,'1771:2F37',word,row,r.ax,ret='1771:4DE9' if slot<=11 else '1771:4E16')
    return _end(r)


@PORTS.port('1771:4E22',ret='retf 4')
def squad_screen_memory(mem,variant):
    """4E22-4F71: squad/card templates and selection, preserving the original caller ABI."""
    r=Regs(mem);r.enter(0x106);country=ss16(mem,r,r.bp+8);mode=ss16(mem,r,r.bp+6)
    squad_of(mem,r,country);squad=r.es,r.di;r.local16(-6,r.di);r.local16(-4,r.es)
    r=yield from guest(mem,r,'1771:4D8A',country,ret='1771:4E44')
    r.di=0x26F2;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:4E53')
    r.al=0
    if mode==2:
        r.di=0x269C;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:4E6E')
    r.di=0x268A;source=mem.DS,r.di;r.di=0xA96E
    r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:4E7D')
    if mode==1:
        r.di=0x1AF6;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:4E92')
    if not mem.ds8(0xC1F):
        managed=False
        if mode!=1:
            r=yield from guest(mem,r,'1771:0B77',country,ret='1771:4EA6')
            managed=bool(r.al)
        r.di=0x57F0 if managed else 0x5A1A;source=mem.DS,r.di;r.di=0xA96E
        r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret='1771:4ECA' if managed else '1771:4EB9')
    else:
        for template,ret in ((0x5A1A,'1771:4EDB'),(0x1704,'1771:4EEA'),(0x47CC,'1771:4EF9')):
            r.di=template;source=mem.DS,r.di;r.di=0xA96E
            r=yield from guest(mem,r,'214B:0329',*source,mem.DS,r.di,ret=ret)
        r.al=15;colour=r.ax;r.push(colour);temporary=(r.bp-0x106)&65535;r.di=temporary;r.push(r.ss);r.push(r.di)
        r.ax=country;r.al=int(r.ax==mem.ds16(0x9B36));cbw(r);r.di=r.ax;r.al=mem.ds8(0x9B3A+r.di);r.ah=0;r.dx=0
        r=yield from guest(mem,r,'214B:09DA',r.dx,r.ax,ret='1771:4F23')
        r.al=5;row=r.ax;r.al=60
        r=yield from write_buffer_text(mem,r,(r.ss,temporary),row,r.ax,'214B:02C8','1771:4F33',colour,6)
    selected=mem.ds16(0xC1B);r.ax=selected<<1;r.es,r.di=squad;r.di=r.di+r.ax;word=rw(mem,r,-2)
    r=yield from guest(mem,r,'1771:42BC',word,ret='1771:4F45')
    r.al=int(mem.ds16(0xC1B)>11);r.ah=0;r.dx=r.ax;r.ax=mem.ds16(0xC1B)+2+r.dx;row=r.ax
    r.ax=65;column=r.ax;r.ax=12
    r=yield from guest(mem,r,'214B:13C5',row,column,r.ax,ret='1771:4F6C')
    return _end(r)
