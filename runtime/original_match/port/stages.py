"""T124a (#427): the round's end frame: stage_end 1771:8208 (its own part: the rounds byte, the stage wrap and the ageing
gate), run_stage 1771:76B1's dispatch and the stage builders' shared helpers append_country_fixture 5D02, add_fixture
5D94, add_fixture_with_bonus 5E3A, set_manager_groups 5E99 and mark_group_fixtures_managed 6617.

From the listing (static/goal-exe/code/seg_1771_09.asm, _11.asm and _12.asm), read after the named view
(named/seg_1771_*.c); the line comments are the listing's offsets. Each routine is written as its instructions, in the
registers they work in (port/runtime.py `Regs`), so that what it leaves in AX and DX (the proof compares them,
port/prove.py) is the original's too, and its memory is written in the listing's order, each write naming its
instruction. Every call the routine makes is the listing's guest call (port/guest.py): the stage builders (6730, 6B55,
6E59, 7090, 71B2, 74BE: T124b-d), yearly_ageing 80DA (U4) and the library 214B:003C, 214B:1D6F and 23E4:08DF run as the
original's, or as their own ports where those are installed.

fixture_winner 5C94 and fixture_loser 5CCB are ported already, listing for listing, in display (T73, #419,
port/_display_finals.py); a routine has one port (port.install refuses two), so this module does not port them again:
`display_helpers()` gives those two of display's entries alone, for a proof of the round's end that installs them
without display's 86 other entries (its display stubs) [designed: T124a].

The far pointers [designed: from globals.tsv]: DS:A917 the countries (0xBF a record), DS:A91F the managers (3 bytes,
from index 0x80), DS:A923 the game record, DS:A92B the fixtures (8 bytes, 1-based), DS:A92F the countries' fixture
lists (0x48 bytes), DS:A933 the group tables."""
from . import Registry
from .contests import ss16, ss8, pop
from .geometry import cbw, mul, imul
from .restarts import _end
from .runtime import Regs
from .setup import guest, member, w8, w16, rb, rw

PORTS = Registry("stages", "the round's end: stage_end 8208's own part, run_stage 76B1's dispatch and the stage "
                           "builders' shared helpers 5D02, 5D94, 5E3A, 5E99, 6617 (T124a)")
PORTS.variant("ageing-gate-skipped", "8268: the ageing gate's member branch never calls 1771:80DA")
PORTS.variant("playoff-flag-from-4", "8270: +0x40 := (stage >= 4), not (stage >= 5)")
PORTS.variant("stage-4-one-round", "82A0: +0x3D drops the (stage == 4) term: stage 4 gets one round, not two")
PORTS.variant("three-builds-four", "76C9: stage 3 dispatched to 6E59 (stage 4's builder), not 6B55")
PORTS.variant("four-builds-three", "76D2: stage 4 dispatched to 6B55 (stage 3's builder), not 6E59")
PORTS.variant("list-not-shifted", "5D44: the country's fixture list is not shifted down (no 214B:003C)")
PORTS.variant("kind-not-raised", "5D7B: the country's +0x3B is never raised to the fixture kind")
PORTS.variant("managed-not-marked", "5E1E: a fixture with a managed side keeps +0 = 0xFF, not 0xFE")
PORTS.variant("group-not-written", "5DE5: the fixture's group byte +1 is not written")
PORTS.variant("bonus-on-every-kind", "5E65: the 200 to +0x2F is added for kind 1 too")
PORTS.variant("sides-not-swapped", "5E43: the first side is always [bp+0xC] (the swap on [bp+0xA] == [bp+4] dropped)")
PORTS.variant("group-plus-one", "5ECF: the manager's group byte is written plus one")
PORTS.variant("mark-ff", "6712: the group's fixtures get +0 = 0xFF, not 0xFE")
PORTS.variant("rounds-of-next-param", "669E: the round count read at DS:1105 + param, not DS:1104 + param")

M16 = 0xFFFF
GAME, COUNTRIES, MANAGERS, FIXTURES, LISTS, TABLES = 0xA923, 0xA917, 0xA91F, 0xA92B, 0xA92F, 0xA933


def _far(mem, r, ptr):
    """`les di, ptr [ptr]` of a DS far pointer."""
    r.di, r.es = mem.ds16(ptr), mem.ds16(ptr + 2)
    return r.es, r.di


def _local_far(mem, r, off):
    """`les di, ptr [bp + off]`: a far pointer the routine keeps in its frame."""
    r.di, r.es = ss16(mem, r, r.bp + off), ss16(mem, r, r.bp + off + 2)
    return r.es, r.di


def _keep(r, off):
    """`mov [bp + off], di; mov [bp + off + 2], es`."""
    r.local16(off, r.di)
    r.local16(off + 2, r.es)


def _set_dl(r, value):
    r.dx = (r.dx & 0xFF00) | (value & 0xFF)


def _set_cl(r, value):
    r.cx = (r.cx & 0xFF00) | (value & 0xFF)


# -- the round's end ---------------------------------------------------------------------------------------------------
@PORTS.port("1771:8208", ret="retf")
def stage_end(mem, variant):
    """The rounds byte +0x3D counts down; at 0 the stage byte +0x3C advances, wrapped into [2, 8] by 214B:1D6F, a new
    stage in CS:81E8 = {2, 3, 5, 7} calls yearly_ageing 80DA (U4: the original's), +0x40 := (stage >= 5) and +0x3D :=
    1 + (stage == 4) + 3 * (stage == 8). The build constant at 822C (`mov al, 0; or al, al; je`) always skips 8232's
    stage-8 stop [confirmed: seg_1771_12.asm 8208-82BC; F016, F025]."""
    r = Regs(mem)
    r.enter(4)                                                      # 8208-820B
    _far(mem, r, GAME)                                              # 820E
    _keep(r, -4)                                                    # 8212, 8215
    _local_far(mem, r, -4)                                          # 8218
    rounds = (rb(mem, r, 0x3D) - 1) & 0xFF
    w8(mem, r, 0x3D, rounds, "1771:821B")                           # 821B dec byte es:[di + 0x3d]
    _local_far(mem, r, -4)                                          # 821F; 8222 cmp ..., 0; 8227 jbe 822c
    if rounds != 0:
        return _end(r)                                              # 8229 jmp 82b9
    r.al = 0                                                        # 822C mov al, 0; 822E or al, al; 8230 je 823e
    _local_far(mem, r, -4)                                          # 823E
    r.di = r.di + 0x3C                                              # 8241
    seg, off = r.es, r.di
    r.al = 2                                                        # 8247
    lo = r.ax
    r.al = 8                                                        # 824A
    hi = r.ax
    r.ax = 1                                                        # 824D
    r = yield from guest(mem, r, "214B:1D6F", seg, off, lo, hi, 1, ret="1771:8256")   # 8245-8251
    _local_far(mem, r, -4)                                          # 8256
    r.al = rb(mem, r, 0x3C)                                         # 8259
    r.di = 0x81E8                                                   # 825E
    r = yield from guest(mem, r, "23E4:08DF", r.ax, mem.seg(0x1771), r.di, ret="1771:8268")   # 825D-8263
    if member(mem) and variant != "ageing-gate-skipped":            # 8268 je 826d
        r = yield from guest(mem, r, "1771:80DA", ret="1771:826D", far=False)          # 826A call 0x80da
    _local_far(mem, r, -4)                                          # 826D
    stage = rb(mem, r, 0x3C)                                        # 8270 cmp ..., 5; 8275 jae 827b
    r.al = int(stage >= (4 if variant == "playoff-flag-from-4" else 5))   # 8277 / 827B
    _local_far(mem, r, -4)                                          # 827D
    w8(mem, r, 0x40, r.al, "1771:8280")                             # 8280
    _local_far(mem, r, -4)                                          # 8284
    r.al = int(rb(mem, r, 0x3C) == 8)                               # 8287-8292
    r.ah = 0                                                        # 8294
    r.cx = 3                                                        # 8296
    imul(r, r.cx)                                                   # 8299
    r.dx = r.ax                                                     # 829B
    _local_far(mem, r, -4)                                          # 829D
    r.al = int(rb(mem, r, 0x3C) == 4 and variant != "stage-4-one-round")   # 82A0-82AB
    r.ah = 0                                                        # 82AD
    r.ax = r.ax + 1                                                 # 82AF
    r.ax = r.ax + r.dx                                              # 82B0
    _local_far(mem, r, -4)                                          # 82B2
    w8(mem, r, 0x3D, r.al, "1771:82B5")                             # 82B5
    return _end(r)                                                  # 82B9-82BC


# The stage builders run_stage calls, by the stage byte (seg_1771_11.asm 76BC-76F1): near calls, each returning to the
# instruction after its call.
BUILDERS = {2: ("1771:6730", "1771:76C7"), 5: ("1771:6730", "1771:76C7"), 3: ("1771:6B55", "1771:76D0"),
            4: ("1771:6E59", "1771:76D9"), 6: ("1771:7090", "1771:76E2"), 7: ("1771:71B2", "1771:76EB"),
            8: ("1771:74BE", "1771:76F4")}


@PORTS.port("1771:76B1", ret="retf")
def run_stage(mem, variant):
    """The stage byte +0x3C picks the builder: 2 and 5 stage_qualifying 6730, 3 6B55, 4 6E59, 6 7090, 7 71B2, 8 74BE;
    any other stage none [confirmed: seg_1771_11.asm 76B1-76F7; F004, F023]."""
    r = Regs(mem)
    r.enter(0)                                                      # 76B1-76B2
    _far(mem, r, GAME)                                              # 76B4
    r.al = rb(mem, r, 0x3C)                                         # 76B8
    stage = r.al
    if variant == "three-builds-four" and stage == 3:
        stage = 4
    elif variant == "four-builds-three" and stage == 4:
        stage = 3
    if stage in BUILDERS:                                           # 76BC-76EF, the compares
        target, ret = BUILDERS[stage]
        r = yield from guest(mem, r, target, ret=ret, far=False)
    return _end(r)                                                  # 76F4-76F7


# -- the builders' shared helpers --------------------------------------------------------------------------------------
@PORTS.port("1771:5D02", ret="ret 4")
def append_country_fixture(mem, variant):
    """A nested procedure of add_fixture 5D94 ([bp + 4] its frame link, [bp + 6] the country): the country's list of
    36 words at [A92F] + 0x48 * country shifts down one word (214B:003C), fixture number [A923]+0x28 goes last, and
    the country's +0x3B is raised to the parent's kind (ss:[link + 6]) [confirmed: seg_1771_09.asm 5D02-5D91; F023]."""
    r = Regs(mem)
    r.enter(8)                                                      # 5D02-5D05
    r.ax = ss16(mem, r, r.bp + 6)                                   # 5D08
    r.dx = 0xBF                                                     # 5D0B
    mul(r, r.dx)                                                    # 5D0E
    _far(mem, r, COUNTRIES)                                         # 5D10
    r.di = r.di + r.ax                                              # 5D14
    _keep(r, -4)                                                    # 5D16, 5D19
    r.ax = ss16(mem, r, r.bp + 6)                                   # 5D1C
    r.dx = 0x48
    mul(r, r.dx)                                                    # 5D1F-5D22
    _far(mem, r, LISTS)                                             # 5D24
    r.di = r.di + r.ax + 2                                          # 5D28, 5D2A
    src = (r.es, r.di)                                              # 5D2E push es; 5D2F push di
    r.ax = ss16(mem, r, r.bp + 6)                                   # 5D30
    r.dx = 0x48
    mul(r, r.dx)                                                    # 5D33-5D36
    _far(mem, r, LISTS)                                             # 5D38
    r.di = r.di + r.ax                                              # 5D3C
    dst = (r.es, r.di)                                              # 5D3E, 5D3F
    r.ax = 0x46                                                     # 5D40
    if variant != "list-not-shifted":
        r = yield from guest(mem, r, "214B:003C", *src, *dst, r.ax, ret="1771:5D49")   # 5D43-5D44
    _far(mem, r, GAME)                                              # 5D49
    r.cx = rw(mem, r, 0x28)                                         # 5D4D
    r.ax = ss16(mem, r, r.bp + 6)                                   # 5D51
    r.dx = 0x48
    mul(r, r.dx)                                                    # 5D54-5D57
    _far(mem, r, LISTS)                                             # 5D59
    r.di = r.di + r.ax                                              # 5D5D
    w16(mem, r, 0x46, r.cx, "1771:5D5F")                            # 5D5F
    _local_far(mem, r, -4)                                          # 5D63
    r.di = r.di + 0x3B                                              # 5D66
    _keep(r, -8)                                                    # 5D6A, 5D6D
    _local_far(mem, r, -8)                                          # 5D70
    r.al = rb(mem, r, 0)                                            # 5D73
    r.ah = 0                                                        # 5D76
    link = ss16(mem, r, r.bp + 4)
    r.di = link                                                     # 5D78
    if r.ax < ss16(mem, r, link + 6) and variant != "kind-not-raised":   # 5D7B cmp ax, ss:[di + 6]; 5D7F jae
        r.di = link                                                 # 5D81
        r.al = ss8(mem, r, link + 6)                                # 5D84
        _local_far(mem, r, -8)                                      # 5D88
        w8(mem, r, 0, r.al, "1771:5D8B")                            # 5D8B
    return _end(r)                                                  # 5D8E-5D91 ret 4


@PORTS.port("1771:5D94", ret="ret 8")
def add_fixture(mem, variant):
    """add_fixture(B [bp + 0xA], A [bp + 8], kind [bp + 6], group [bp + 4]): fixture [A923]+0x28 (DS:A92B + 8n - 8)
    gets +6 := B and +4 := A, each through append_country_fixture 5D02, +0 := 0xFF, or 0xFE when either country's
    +0x2E is above 0x80 (managed), +1 := group, +2 := kind; then [A923]+0x28 += 1 [confirmed: seg_1771_09.asm
    5D94-5E37; F023]."""
    r = Regs(mem)
    r.enter(6)                                                      # 5D94-5D97
    _far(mem, r, GAME)                                              # 5D9A
    r.ax = rw(mem, r, 0x28)                                         # 5D9E
    _set_cl(r, 3)                                                   # 5DA2
    r.ax = r.ax << 3                                                # 5DA4
    _far(mem, r, FIXTURES)                                          # 5DA6
    r.di = r.di + r.ax                                              # 5DAA
    r.di = r.di + 0xFFF8                                            # 5DAC
    _keep(r, -6)                                                    # 5DB0, 5DB3
    r.ax = ss16(mem, r, r.bp + 0xA)                                 # 5DB6
    _local_far(mem, r, -6)                                          # 5DB9
    w16(mem, r, 6, r.ax, "1771:5DBC")                               # 5DBC
    r = yield from guest(mem, r, "1771:5D02", ss16(mem, r, r.bp + 0xA), r.bp, ret="1771:5DC7", far=False)  # 5DC0-5DC4
    r.ax = ss16(mem, r, r.bp + 8)                                   # 5DC7
    _local_far(mem, r, -6)                                          # 5DCA
    w16(mem, r, 4, r.ax, "1771:5DCD")                               # 5DCD
    r = yield from guest(mem, r, "1771:5D02", ss16(mem, r, r.bp + 8), r.bp, ret="1771:5DD8", far=False)    # 5DD1-5DD5
    _local_far(mem, r, -6)                                          # 5DD8
    w8(mem, r, 0, 0xFF, "1771:5DDB")                                # 5DDB
    r.al = ss8(mem, r, r.bp + 4)                                    # 5DDF
    _local_far(mem, r, -6)                                          # 5DE2
    if variant != "group-not-written":
        w8(mem, r, 1, r.al, "1771:5DE5")                            # 5DE5
    managed = False
    for k in (4, 6):                                                # 5DE9-5E00 (side +4), 5E02-5E19 (side +6)
        _local_far(mem, r, -6)
        r.ax = rw(mem, r, k)
        r.dx = 0xBF
        mul(r, r.dx)
        _far(mem, r, COUNTRIES)
        r.di = r.di + r.ax
        if rb(mem, r, 0x2E) > 0x80:                                 # 5E00 ja 5e1b; 5E19 jbe 5e22
            managed = True
            break
    if managed:
        _local_far(mem, r, -6)                                      # 5E1B
        if variant != "managed-not-marked":
            w8(mem, r, 0, 0xFE, "1771:5E1E")                        # 5E1E
    r.al = ss8(mem, r, r.bp + 6)                                    # 5E22
    _local_far(mem, r, -6)                                          # 5E25
    w8(mem, r, 2, r.al, "1771:5E28")                                # 5E28
    _far(mem, r, GAME)                                              # 5E2C
    w16(mem, r, 0x28, rw(mem, r, 0x28) + 1, "1771:5E30")            # 5E30 inc word es:[di + 0x28]
    return _end(r)                                                  # 5E34-5E37 ret 8


@PORTS.port("1771:5E3A", ret="ret 0xa")
def add_fixture_with_bonus(mem, variant):
    """add_fixture_with_bonus(Y [bp + 0xC], X [bp + 0xA], kind [bp + 8], group [bp + 6], P [bp + 4]): add_fixture
    with X second (+6) when X == P, else with Y second; unless the kind is 1, 200 more to both countries' +0x2F
    [confirmed: seg_1771_09.asm 5E3A-5E96; F017]."""
    r = Regs(mem)
    r.enter(0)                                                      # 5E3A-5E3B
    r.ax = ss16(mem, r, r.bp + 0xA)                                 # 5E3D
    y, x = ss16(mem, r, r.bp + 0xC), r.ax
    kind, group = ss16(mem, r, r.bp + 8), ss16(mem, r, r.bp + 6)
    if r.ax == ss16(mem, r, r.bp + 4) and variant != "sides-not-swapped":   # 5E40 cmp ax, [bp + 4]; 5E43 jne
        r = yield from guest(mem, r, "1771:5D94", x, y, kind, group, ret="1771:5E54", far=False)   # 5E45-5E51
    else:
        r = yield from guest(mem, r, "1771:5D94", y, x, kind, group, ret="1771:5E65", far=False)   # 5E56-5E62
    if ss16(mem, r, r.bp + 8) != 1 or variant == "bonus-on-every-kind":    # 5E65 cmp word [bp + 8], 1; je 5e93
        for k, at in ((0xA, "1771:5E79"), (0xC, "1771:5E8D")):     # 5E6B-5E79, 5E7F-5E8D
            r.ax = ss16(mem, r, r.bp + k)
            r.dx = 0xBF
            mul(r, r.dx)
            _far(mem, r, COUNTRIES)
            r.di = r.di + r.ax
            w16(mem, r, 0x2F, rw(mem, r, 0x2F) + 0xC8, at)          # add word es:[di + 0x2f], 0xc8
    return _end(r)                                                  # 5E93-5E96 ret 0xa


@PORTS.port("1771:5E99", ret="ret 2")
def set_manager_groups(mem, variant):
    """[A923]+1+m := the byte argument for every manager m = 1..[A923]+0 (the manager's group in the stage; 0 none)
    [confirmed: seg_1771_09.asm 5E99-5EDE; F023]."""
    r = Regs(mem)
    r.enter(8)                                                      # 5E99-5E9C
    _far(mem, r, GAME)                                              # 5E9F
    _keep(r, -6)                                                    # 5EA3, 5EA6
    _local_far(mem, r, -6)                                          # 5EA9
    r.al = rb(mem, r, 0)                                            # 5EAC
    r.ah = 0                                                        # 5EAF
    count = r.ax
    r.local16(-8, count)                                            # 5EB1
    r.ax = 1                                                        # 5EB4
    if not 1 > count:                                               # 5EB7 cmp ax, [bp - 8]; 5EBA ja 5edb
        n = 1
        r.local16(-2, n)                                            # 5EBC
        while True:
            _set_dl(r, ss8(mem, r, r.bp + 4) + (1 if variant == "group-plus-one" else 0))   # 5EC4
            r.ax = n                                                # 5EC7
            _local_far(mem, r, -6)                                  # 5ECA
            r.di = r.di + r.ax                                      # 5ECD
            w8(mem, r, 1, r.dx & 0xFF, "1771:5ECF")                 # 5ECF
            r.ax = n                                                # 5ED3
            if n == count:                                          # 5ED6 cmp; 5ED9 jne 5ec1
                break
            n = (n + 1) & M16
            r.local16(-2, n)                                        # 5EC1 inc word [bp - 2]
    return _end(r)                                                  # 5EDB-5EDE ret 2


@PORTS.port("1771:6617", ret="ret 2")
def mark_group_fixtures_managed(mem, variant):
    """For each manager m with a group g = [A923]+1+m: every fixture of g's round list in the group tables gets +0 :=
    0xFE. The list: [A933] + 0xE00 * [A923]+0x40 + 0x700 * param + 0x1C0 * c + 0x38 * g + 2 * k - 0x1DA, for
    k = 1..DS:1104[param], where c is 1 when param and +0x40 are both nonzero (the World Cup), else the continent +0x2C
    of the manager's country [confirmed: seg_1771_09.asm 6617-672D; F023]."""
    r = Regs(mem)
    r.enter(0xE)                                                    # 6617-661A
    _far(mem, r, GAME)                                              # 661D
    _keep(r, -0xA)                                                  # 6621, 6624
    _local_far(mem, r, -0xA)                                        # 6627
    r.al = rb(mem, r, 0)                                            # 662A
    r.ah = 0
    count = r.ax
    r.local16(-0xC, count)                                          # 662F
    r.ax = 1                                                        # 6632
    if not 1 <= count:                                              # 6635 cmp ax, [bp - 0xc]; 6638 jbe 663d
        return _end(r)                                              # 663A jmp 672a
    m = 1
    r.local16(-4, m)                                                # 663D
    param = ss8(mem, r, r.bp + 4)
    while True:
        r.ax = m                                                    # 6645
        _local_far(mem, r, -0xA)                                    # 6648
        r.di = r.di + r.ax                                          # 664B
        if rb(mem, r, 1) != 0:                                      # 664D cmp byte es:[di + 1], 0; 6652 jne 6657
            world = False
            if param != 0:                                          # 6657 cmp byte [bp + 4], 0; 665B je 666e
                _local_far(mem, r, -0xA)                            # 665D
                world = rb(mem, r, 0x40) != 0                       # 6660 cmp; 6665 je 666e
            if world:
                c = 1
                r.local16(-6, c)                                    # 6667
            else:
                r.ax = m                                            # 666E
                r.ax = r.ax + 0x80                                  # 6671
                r.dx = 3                                            # 6674
                mul(r, r.dx)                                        # 6677
                _far(mem, r, MANAGERS)                              # 6679
                r.di = r.di + r.ax                                  # 667D
                r.al = rb(mem, r, 0)                                # 667F
                r.ah = 0                                            # 6682
                r.dx = 0xBF                                         # 6684
                mul(r, r.dx)                                        # 6687
                _far(mem, r, COUNTRIES)                             # 6689
                r.di = r.di + r.ax                                  # 668D
                r.al = rb(mem, r, 0x2C)                             # 668F
                r.ah = 0                                            # 6693
                c = r.ax
                r.local16(-6, c)                                    # 6695
            r.al = param                                            # 6698
            cbw(r)                                                  # 669B
            r.di = r.ax                                             # 669C
            r.al = mem.ds8((0x1104 + (1 if variant == "rounds-of-next-param" else 0) + r.di) & M16)   # 669E
            r.ah = 0                                                # 66A2
            rounds = r.ax
            r.local16(-0xE, rounds)                                 # 66A4
            r.ax = 1                                                # 66A7
            if not 1 > rounds:                                      # 66AA cmp ax, [bp - 0xe]; 66AD ja 671f
                k = 1
                r.local16(-2, k)                                    # 66AF
                while True:
                    r.ax = k                                        # 66B7
                    r.ax = r.ax << 1                                # 66BA
                    r.push(r.ax)                                    # 66BC
                    r.ax = m                                        # 66BD
                    _local_far(mem, r, -0xA)                        # 66C0
                    r.di = r.di + r.ax                              # 66C3
                    r.al = rb(mem, r, 1)                            # 66C5
                    r.ah = 0                                        # 66C9
                    r.dx = 0x38                                     # 66CB
                    mul(r, r.dx)                                    # 66CE
                    r.push(r.ax)                                    # 66D0
                    r.ax = c                                        # 66D1
                    r.dx = 0x1C0                                    # 66D4
                    mul(r, r.dx)                                    # 66D7
                    r.bx = r.ax                                     # 66D9
                    r.al = param                                    # 66DB
                    cbw(r)                                          # 66DE
                    r.dx = 0x700                                    # 66DF
                    mul(r, r.dx)                                    # 66E2
                    r.cx = r.ax                                     # 66E4
                    _local_far(mem, r, -0xA)                        # 66E6
                    r.al = rb(mem, r, 0x40)                         # 66E9
                    cbw(r)                                          # 66ED
                    r.dx = 0xE00                                    # 66EE
                    mul(r, r.dx)                                    # 66F1
                    _far(mem, r, TABLES)                            # 66F3
                    r.di = r.di + r.ax                              # 66F7
                    r.di = r.di + r.cx                              # 66F9
                    r.di = r.di + r.bx                              # 66FB
                    r.ax = pop(mem, r)                              # 66FD
                    r.di = r.di + r.ax                              # 66FE
                    r.ax = pop(mem, r)                              # 6700
                    r.di = r.di + r.ax                              # 6701
                    r.ax = rw(mem, r, -0x1DA)                       # 6703 mov ax, es:[di - 0x1da]
                    _set_cl(r, 3)                                   # 6708
                    r.ax = r.ax << 3                                # 670A
                    _far(mem, r, FIXTURES)                          # 670C
                    r.di = r.di + r.ax                              # 6710
                    w8(mem, r, -8, 0xFF if variant == "mark-ff" else 0xFE, "1771:6712")   # 6712
                    r.ax = k                                        # 6717
                    if k == rounds:                                 # 671A cmp; 671D jne 66b4
                        break
                    k = (k + 1) & M16
                    r.local16(-2, k)                                # 66B4 inc word [bp - 2]
        r.ax = m                                                    # 671F
        if m == count:                                              # 6722 cmp; 6725 je 672a
            break
        m = (m + 1) & M16
        r.local16(-4, m)                                            # 6642 inc word [bp - 4]
    return _end(r)                                                  # 672A-672D ret 2


# -- the two helpers display ports -------------------------------------------------------------------------------------
HELPERS_FROM_DISPLAY = ("1771:5C94", "1771:5CCB")      # fixture_winner, fixture_loser (port/_display_finals.py)


def display_helpers():
    """A Registry holding display's ports of 5C94 and 5CCB alone (the same Entry objects, so the same Python
    functions), with their two falsifiers, for port.install(machine, [..., (display_helpers(), variant)])."""
    from . import display
    reg = Registry("display", "display's fixture_winner 5C94 and fixture_loser 5CCB alone (T73, #419)")
    for address in HELPERS_FROM_DISPLAY:
        reg._add(display.PORTS.entries[address])
        name = "omit-" + address.lower().replace(":", "-")
        reg.variant(name, display.PORTS.variants[name])
    return reg
