"""The player attributes (segment 1771), ported (T61, step P1 part b): the routines that read a player's or a country's
record and answer a small number, plus the player's own tactics and the marking words.

From the listing static/goal-exe/code/seg_1771_02.asm (0AA7-0E6C), seg_1771_04.asm (2E20-2FFB), seg_1771_05.asm
(3041-3A82), seg_1771_06.asm (3E2F, 3EF8) and seg_1771_08.asm (5A03); the line comments are the listing's offsets. The
records are the ones image.py names: the player array, 3061 records of 0x14 bytes at the far pointer DS:A91B, the
country array, 129 of 0xBF at DS:A917, the manager array at DS:A91F. Every routine is `retf n` (1771 is a far segment,
Turbo Pascal's convention: the callee pops its arguments) but 0E24, called near (`ret 2`) and 3E2F, a nested procedure
(`ret 6`, its parent's BP is its first argument).

Registers. The proof (port/prove.py) compares AX and DX at every return, so each port returns the AX and DX the
original leaves, not only its value: the high byte of AX and DX are what the last instruction of the listing left
(`mul` leaves the high word in DX; `xor ah, ah` makes AH 0; a `mov al, ..` keeps AH). Each routine below tracks AX and DX
through the listing as the plain variables `ax`, `dx`; the tiny runtime helpers it calls inline are the helpers
below, each with the registers it leaves (`bit_test` is 214B:0C57, `bit_set` 214B:0C79, `bit_clear` 214B:0CA1; the
set test 23E4:08DF is inlined where its set is a constant of the code segment, `cs_set_has`).

A routine it calls that is still the original's (the Pascal string helpers of 23E4, `Str` 214B:09DA, `FillChar`
214B:0018) is a guest call (port/guest.py) with the registers the listing hands it; a routine of this module it
calls is a guest call too (the guest then runs its port), so every call is counted and proved on its own. The Turbo
Pascal string helpers leave the destination pointer on the stack for the next call (`retf 2` / `retf 4`), which a
guest call cannot express, so the pointer words are pushed by the port (`push`) and dropped with `drop` and pushed again
as the next call's arguments (the same bytes at the same stack addresses)."""
from .guest import call
from .mem import s8, s16
from . import Registry

PORTS = Registry("attributes", "the player attributes of segment 1771: the records' readers, tactics and marking (T61)")
PORTS.variant("foot-right-3", "3179's right-footed wrong-position set {3, 7, 10} (CS:3139) without 7 (31C0)")
PORTS.variant("unavailable-bit-6", "3216 tests element 5 where it tests element 6 (3251-3264)")
PORTS.variant("skill-divisor-31", "3A06's divisor 0x20 read as 0x1F (3A71)")
PORTS.variant("mark-hi-excl", "3E2F's upper bound 'oc > hi' read as 'oc >= hi' (3E6E-3E71)")

PLAYERS, COUNTRIES, MANAGERS = 0xA91B, 0xA917, 0xA91F      # far pointers at DS:xxxx (0AB5, 0ACF, 3F18...)
TEAM_COUNTRY = 0x9B34       # the two teams' countries, words (3F0F: [di - 0x64cc])
MARK_BASE = 0x9A3E          # the marking word of slot s of team t: DS:9A3E + 0x28 t + 2 s (3F31: [di - 0x65c0])

# The sets of the code segment (23E4:08DF reads bit e of byte e >> 3 of a 32-byte set), each cited by its data row in
# the listing: 3139 = 88 04 (bits 3, 7, 10), 3159 = 10 09 (bits 4, 8, 11), 3411 = 1B 00 (bits 0, 1, 3, 4); the rest of
# each row is zero.
RIGHT_FOOT_BAD = frozenset({3, 7, 10})          # CS:3139 (read at 31B6)
LEFT_FOOT_BAD = frozenset({4, 8, 11})           # CS:3159 (read at 31D0)
TACTIC_POSITIONS = frozenset({0, 1, 3, 4})      # CS:3411 (read at 3465)
S_SET_WRITE, S_CLEAR_WRITE = "214B:0C98", "214B:0CC2"   # the writes of the set-element helpers 0C79 and 0CA1


# -- the view of a record ------------------------------------------------------------------------------------------
class Rec:
    """`les di, ptr [DS:ptr]; add di, ax`: record bytes at seg:(off + ax + k), the offset wrapping in 16 bits."""
    __slots__ = ("mem", "seg", "off")

    def __init__(self, mem, ptr, ax):
        off, seg = mem.farptr(mem.DS * 16 + ptr)
        self.mem, self.seg, self.off = mem, seg, (off + ax) & 0xFFFF

    def lin(self, k):
        return (self.seg << 4) + ((self.off + k) & 0xFFFF)

    def u8(self, k):
        return self.mem.u8(self.lin(k))

    def u16(self, k):
        return self.mem.u16(self.lin(k))

    def w8(self, k, value, at):
        self.mem.w8(self.lin(k), value, at)


def mul(a, b):
    """`mov dx, b; mul dx` (or `mov ax, a; mov dx, b; mul dx`): (AX, DX) the low and high word of a * b."""
    p = (a & 0xFFFF) * b
    return p & 0xFFFF, p >> 16


def idiv(a, b):
    """x86 `idiv` of the signed word a by b (cwd first): (quotient, remainder) truncated toward zero."""
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q & 0xFFFF, (a - q * b) & 0xFFFF


# -- the runtime helpers the routines call inline, with the registers they leave -------------------------------------
def bit_test(setword, elem):
    """214B:0C57 (0C5D-0C6D): ((word set) >> (elem - 1)) & 1, `shr ax, cl`: (AX, DX): AX the bit, DX = elem - 1."""
    cl = (elem - 1) & 0xFFFF
    return ((setword & 0xFFFF) >> (cl & 0x1F)) & 1, cl


def bit_set(old, elem):
    """214B:0C79 (0C7C-0C98): the byte with element elem set, (byte, AX, DX): AX the byte (AH 0), DX the mask."""
    mask = (1 << ((elem - 1) & 0x1F)) & 0xFFFF
    new = (old | mask) & 0xFF
    return new, (old | mask) & 0xFFFF, mask


def bit_clear(old, elem):
    """214B:0CA1 (0CA4-0CC2): the byte with element elem cleared, (byte, AX, DX): AX the byte (AH 0), DX the mask."""
    mask = ~(1 << ((elem - 1) & 0x1F)) & 0xFFFF
    return old & mask & 0xFF, old & mask & 0xFFFF, mask


def cs_set_has(members, e, ax):
    """23E4:08DF on a set of the code segment (08E5-08FA): whether the low byte of the pushed word is a member, and the
    AX it leaves: AL = 1 << (e & 7) (08F6-08F8), AH as it was."""
    e &= 0xFF
    return e in members, (ax & 0xFF00) | (1 << (e & 7))


def regs(mem, ax, dx):
    mem.set_reg("ax", ax & 0xFFFF)
    mem.set_reg("dx", dx & 0xFFFF)


def ret(mem, ax, dx):
    """The end of a function: AX is the value the port returns, DX set here."""
    mem.set_reg("dx", dx & 0xFFFF)
    return ax & 0xFFFF


def end(mem, ax, dx):
    """The end of a procedure: AX and DX as the listing leaves them (the port returns no value)."""
    regs(mem, ax, dx)
    return None


def gcall(mem, ax, dx, target, *args, ret_to, far=True):
    """A guest call (yield from): the registers the listing hands the callee, and (AX, DX) it returns."""
    regs(mem, ax, dx)
    result = yield call(target, *args, ret_to=ret_to, far=far)
    return result & 0xFFFF, mem.reg("dx")


def push(mem, word, at):
    """`push word`: the word written at the new SP, as the original's instruction `at` writes it."""
    sp = (mem.reg("sp") - 2) & 0xFFFF
    mem.w16(mem.ss_lin(sp), word, at)
    mem.set_reg("sp", sp)


def drop(mem, words):
    """The stack pointer back over words the callee of a string helper would have popped: they are pushed again as the
    arguments of the next call (same words, same addresses)."""
    mem.set_reg("sp", (mem.reg("sp") + 2 * words) & 0xFFFF)


# -- the small readers -------------------------------------------------------------------------------------------
@PORTS.port("1771:0AA7", ret="retf 2")
def manager_bonus(mem, variant):
    """0AA7: the manager's match bonus: idiv 8 of the manager byte at [DS:A91F] + 3 * (country +0x2E), plus 0x10."""
    ax, dx = mul(mem.arg(0), 0xBF)                          # 0AAD-0AB3
    b = Rec(mem, COUNTRIES, ax).u8(0x2E)                    # 0AB5-0AC8: xor ah, ah
    ax, dx = mul(b, 3)                                      # 0ACA-0ACD
    m = Rec(mem, MANAGERS, ax).u8(1)                        # 0ACF-0AD9: xor ah, ah
    return ret(mem, m // 8 + 0x10, m % 8)                   # 0ADB-0AE1: cdq, idiv 8 (DX is the remainder), add ax, 0x10


@PORTS.port("1771:0B77", ret="retf 2")
def is_managed(mem, variant):
    """0B77: the country's +0x2E above 0x80 (ja)."""
    ax, dx = mul(mem.arg(0), 0xBF)                          # 0B7D-0B83
    managed = Rec(mem, COUNTRIES, ax).u8(0x2E) > 0x80       # 0B85-0B90
    return ret(mem, (ax & 0xFF00) | managed, dx)            # 0B92/0B96: mov al, 0/1, AH from the mul


@PORTS.port("1771:0E24", ret="ret 2")
def country_colour(mem, variant):
    """0E24 (near): 0x0F when the country is managed (0B77), else the byte DS:6905[country +0x2C]."""
    country = mem.arg(0)
    mem.enter(6, "1771:0E24")                               # 0E24-0E27
    ax, dx = mul(country, 0xBF)                             # 0E2A-0E30
    ax, dx = yield from gcall(mem, ax, dx, "1771:0B77", country, ret_to="1771:0E45")   # 0E3E-0E42 push; push cs; call
    if ax & 0xFF:                                           # 0E45-0E47
        return ret(mem, (ax & 0xFF00) | 0x0F, dx)           # 0E49: [bp - 1] = 0xF; 0E61 mov al, [bp - 1]
    colour = mem.ds8(0x6905 + Rec(mem, COUNTRIES, mul(country, 0xBF)[0]).u8(0x2C))   # 0E4F-0E5A (xor ah, ah)
    return ret(mem, colour, dx)


@PORTS.port("1771:2E20", ret="retf 4")
def player_name_colour(mem, variant):
    """2E20: 6 when +0x0E is 0, 5 when element 8 or 6 of +0x10 is set, else DS:699A[position]."""
    pos, n = mem.arg(0), mem.arg(1)                         # [bp + 6], [bp + 8]
    ax, dx = mul(n, 0x14)                                   # 2E26-2E2C
    p = Rec(mem, PLAYERS, ax)
    if p.u8(0xE) == 0:                                      # 2E3A-2E42
        return ret(mem, (ax & 0xFF00) | 6, dx)              # 2E44
    flags = p.u8(0x10)
    ax, dx = bit_test(flags, 8)                             # 2E4A-2E58 (214B:0C57 leaves AH 0)
    if not ax:
        ax, dx = bit_test(flags, 6)                         # 2E61-2E6F
    if ax:
        return ret(mem, 5, dx)                              # 2E78
    return ret(mem, mem.ds8(0x699A + pos), dx)              # 2E7E-2E85: AL from the table, AH 0 (0C57)


@PORTS.port("1771:2FAD", ret="retf 2")
def player_height(mem, variant):
    """2FAD: DS:0E46[+7] + DS:0E54[n mod 12]."""
    n = mem.arg(0)
    ax, dx = mul(n, 0x14)                                   # 2FB3-2FB9
    p = Rec(mem, PLAYERS, ax)
    dx = mem.ds8(0xE54 + n % 12)                            # 2FC7-2FDA: div 12, xchg dx, ax; mov dx, ax
    ax = mem.ds8(0xE46 + p.u8(7)) + dx                      # 2FDF-2FED
    return ret(mem, ax, dx)


@PORTS.port("1771:2FFB", ret="retf 2")
def player_hardness(mem, variant):
    """2FFB: +5 minus bit 0 of +3."""
    ax, dx = mul(mem.arg(0), 0x14)                          # 3001-3007
    p = Rec(mem, PLAYERS, ax)
    dx = p.u8(3) & 1                                        # 3015-3028 (shr al, 1; jb; mov dx, ax)
    return ret(mem, p.u8(5) - dx, dx)                       # 302A-3035: sub ax, dx (16 bits); AL stored and reloaded


@PORTS.port("1771:3041", ret="retf 2")
def is_two_footed(mem, variant):
    """3041: +5 + +2 == 30."""
    ax, dx = mul(mem.arg(0), 0x14)                          # 3047-304D
    p = Rec(mem, PLAYERS, ax)
    dx = p.u8(5)                                            # 305B-3064: mov dx, ax
    total = p.u8(2) + dx                                    # 3066-306F
    return ret(mem, (total & 0xFF00) | (total == 0x1E), dx)     # 3071-307C: mov al, 0/1, AH of the sum


@PORTS.port("1771:3088", ret="retf 2")
def foot_index(mem, variant):
    """3088: DS:0E60[14 * DS:0E7C[n mod 3] + +7]."""
    n = mem.arg(0)
    ax, dx = mul(n, 0x14)                                   # 308E-3094
    bx = Rec(mem, PLAYERS, ax).u8(7)                        # 30A2-30AB
    row = mem.ds8(0xE7C + n % 3)                            # 30AD-30BE: div 3, xchg, xor ah, ah
    ax, dx = mul(row, 0xE)                                  # 30C0-30C3
    return ret(mem, (ax & 0xFF00) | mem.ds8(0xE60 + ((ax + bx) & 0xFFFF)), dx)   # 30C5-30CD: AH of the mul


@PORTS.port("1771:30D9", ret="retf 2")
def player_leadership(mem, variant):
    """30D9: ((+3) - (+5)) mod 8 (idiv: the remainder keeps the dividend's sign), halved (div 2) when +1 < 0x15."""
    ax, dx = mul(mem.arg(0), 0x14)                          # 30DF-30E5
    p = Rec(mem, PLAYERS, ax)
    dx = p.u8(5)                                            # 30F6-30FC: mov dx, ax
    quotient, remainder = idiv(p.u8(3) - dx, 8)             # 30FE-310D: sub ax, dx; cdq; idiv 8
    if p.u8(1) >= 0x15:                                     # 3116-311B: jae
        return ret(mem, remainder, quotient)                # 310F: xchg dx, ax
    return ret(mem, remainder // 2, remainder % 2)          # 311D-3127: xor dx, dx; div 2


@PORTS.port("1771:3216", ret="retf 2")
def player_unavailable(mem, variant):
    """3216: 1 when +0xE is below 1 (signed) or element 8, 6 or 3 of +0x10 is set, else 0."""
    ax, dx = mul(mem.arg(0), 0x14)                          # 321C-3222
    p = Rec(mem, PLAYERS, ax)
    if s8(p.u8(0xE)) < 1:                                   # 3230-3238: jl
        return ret(mem, (ax & 0xFF00) | 1, dx)              # 3283: mov al, 1 (AH of the mul)
    s = p.u8(0x10)
    if (s >> 7) & 1:                                        # 323A-324F: element 8
        return ret(mem, 1, 7)
    elem6 = 5 if variant == "unavailable-bit-6" else 6
    if (s >> (elem6 - 1)) & 1:                              # 3251-3266: element 6
        return ret(mem, 1, elem6 - 1)
    if (s >> 2) & 1:                                        # 3268-327D: element 3
        return ret(mem, 1, 2)
    return ret(mem, 0, 2)                                   # 327F: mov al, 0 (AH 0 from 0C57)


@PORTS.port("1771:3A06", ret="retf 4")
def derived_skill(mem, variant):
    """3A06: DS:6DCD[12 * (+5) + DS:6D25[12 * (+7) + element]] * ((+4) + 1) div 32."""
    element, n = mem.arg(0), mem.arg(1)                     # [bp + 6], [bp + 8]
    ax, dx = mul(n, 0x14)                                   # 3A0C-3A12
    p = Rec(mem, PLAYERS, ax)
    scale = p.u8(4) + 1                                     # 3A20-3A2C
    cx = mem.ds8(0x6D25 + ((p.u8(7) * 12 + element) & 0xFFFF))      # 3A2F-3A4C (mul 12: DX 0, no overflow)
    t = mem.ds8(0x6DCD + ((p.u8(5) * 12 + cx) & 0xFFFF))    # 3A4E-3A64
    product = (t * scale) & 0xFFFF                          # 3A69-3A6C: mul; xor dx, dx drops the high word
    divisor = 0x1F if variant == "skill-divisor-31" else 0x20
    return ret(mem, product // divisor, product % divisor)  # 3A6F-3A76: div 0x20


@PORTS.port("1771:3A82", ret="retf 4")
def squad_slot_of_player(mem, variant):
    """3A82: the slot 1..20 of a player word in the country's word list, or 0."""
    country, player = mem.arg(0), mem.arg(1)                # [bp + 6], [bp + 8]
    ax, dx = mul(country, 0xBF)                             # 3A88-3A8E
    c = Rec(mem, COUNTRIES, ax)
    found = 0
    for slot in range(1, 0x15):                             # 3AA1-3AC6
        if c.u16(2 * slot - 2) == player:
            found = slot
            break
    return ret(mem, found, dx)


@PORTS.port("1771:5A03", ret="retf 4")
def fixture_kind_in_result_set(mem, variant):
    """5A03: whether the fixture's +2 is in the set DS:0F3E (through 23E4:08DF)."""
    ax0, dx0 = mem.reg("ax"), mem.reg("dx")                 # the caller's (the listing never writes AX's high byte or DX)
    kind = mem.u8(((mem.arg(1) << 4) + ((mem.arg(0) + 2) & 0xFFFF)))     # 5A09-5A15: les di, [bp + 6]; [di + 2]
    e = kind & 0xFF
    member = mem.u8(mem.DS * 16 + ((0xF3E + (e >> 3)) & 0xFFFF)) & (1 << (e & 7))       # 5A1A-5A1F -> 08DF
    return ret(mem, (ax0 & 0xFF00) | (1 if member else 0), dx0)    # 5A24-5A2C


# -- the two routines that build Pascal strings (the helpers of 23E4 and 214B stay the original's: T60) ------------------
@PORTS.port("1771:2E93", ret="retf 2")
def player_name(mem, variant):
    """2E93: the player's name into the string at the far pointer [bp + 8]: the initial DS:[9B70] + n, a space (CS:2E91)
    and the surname, 11 bytes at [DS:9B6C] + 11 n, assigned with a maximum of 12 (23E4:075A, 06B7 twice, 0644)."""
    n = mem.arg(0)
    dest_off, dest_seg = mem.arg(1), mem.arg(2)             # les di, [bp + 8]
    dx = mem.reg("dx")
    mem.enter(0x100, "1771:2E93")                           # 2E93-2E96
    ss, cs, local = mem.reg("ss"), mem.seg(0x1771), (mem.reg("bp") - 0x100) & 0xFFFF
    push(mem, ss, "1771:2E9E")                              # 2E9A-2E9F: lea di, [bp - 0x100]; push ss; push di
    push(mem, local, "1771:2E9F")
    off, seg = mem.farptr(mem.DS * 16 + 0x9B70)             # 2EA3
    ax = (n & 0xFF00) | mem.u8((seg << 4) + ((off + n) & 0xFFFF))      # 2EA0-2EA9: mov ax, [bp + 6]; mov al, es:[di]
    ax, dx = yield from gcall(mem, ax, dx, "23E4:075A", ax, ret_to="1771:2EB2")                  # 2EAC-2EAD
    ax, dx = yield from gcall(mem, ax, dx, "23E4:06B7", cs, 0x2E91, ret_to="1771:2EBC")          # 2EB2-2EB7
    ax, dx = mul(n, 11)                                     # 2EBC-2EC2
    off, seg = mem.farptr(mem.DS * 16 + 0x9B6C)             # 2EC4
    ax, dx = yield from gcall(mem, ax, dx, "23E4:06B7", seg, (off + ax) & 0xFFFF, ret_to="1771:2ED1")   # 2ECA-2ECC
    drop(mem, 2)                                            # 0644 pops the pointer 06B7 left (retf 0xA)
    yield from gcall(mem, 0xC, dx, "23E4:0644", ss, local, dest_seg, dest_off, 0xC, ret_to="1771:2EDF")   # 2ED1-2EDA


@PORTS.port("1771:0E6C", ret="retf 2")
def formation_label(mem, variant):
    """0E6C: 'defence-midfield-attack' of the country's available players of squad slots 1..11 by DS:0D5C[position]
    (3216 per slot), built with 214B:09DA (Str) and 23E4:06B7 (concatenate) and assigned with a maximum of 10 (0644)
    into the string at the far pointer [bp + 8]."""
    country = mem.arg(0)
    dest_off, dest_seg = mem.arg(1), mem.arg(2)
    f = mem.enter(0x30A, "1771:0E6C")                       # 0E6C-0E6F
    bp, ss, cs = mem.reg("bp"), mem.reg("ss"), mem.seg(0x1771)
    ax, dx = mul(country, 0xBF)                             # 0E73-0E79
    c = Rec(mem, COUNTRIES, ax)
    ax = 0                                                  # 0E87-0E8C: the four counts [bp - 4 .. bp - 1] := 0
    f.w16(-4, 0, "1771:0E89")
    f.w16(-2, 0, "1771:0E8C")
    for i in range(1, 12):                                  # 0E8F-0EE8
        ax = 2 * i
        w = c.u16(2 * i - 2)                                # 0E99-0EA3
        ax, dx = yield from gcall(mem, ax, dx, "1771:3216", w, ret_to="1771:0EAB")          # 0EA3-0EA8
        if ax & 0xFF:                                       # 0EAB-0EAD: unavailable
            continue
        ax, dx = mul(w, 0x14)                               # 0EAF-0EC0
        code = mem.ds8(0xD5C + Rec(mem, PLAYERS, ax).u8(6))     # 0EC2-0EDD (xor ah, ah)
        ax = code
        f.w8(code - 4, f.u8(code - 4) + 1, "1771:0EE1")     # 0EDF-0EE1: inc byte [bp + di - 4]
    counts = [f.u8(-4), f.u8(-3), f.u8(-2), f.u8(-1)]
    buffers = [(bp - 0x10A) & 0xFFFF, (bp - 0x20A) & 0xFFFF, (bp - 0x30A) & 0xFFFF]
    # defence: Str(count) onto the stack, then the separator CS:0E6A (a string of one byte, '-')
    push(mem, ss, "1771:0EEE")                              # 0EEA-0EEF: lea di, [bp - 0x10a]; push ss; push di
    push(mem, buffers[0], "1771:0EEF")
    ax, dx = yield from gcall(mem, counts[1], 0, "214B:09DA", 0, counts[1], ret_to="1771:0EFE")   # 0EF0-0EF9
    ax, dx = yield from gcall(mem, ax, dx, "23E4:06B7", cs, 0x0E6A, ret_to="1771:0F08")          # 0EFE-0F03
    push(mem, ss, "1771:0F0C")                              # 0F08-0F0D
    push(mem, buffers[1], "1771:0F0D")
    ax, dx = yield from gcall(mem, counts[2], 0, "214B:09DA", 0, counts[2], ret_to="1771:0F1C")   # 0F0E-0F17
    drop(mem, 2)
    ax, dx = yield from gcall(mem, ax, dx, "23E4:06B7", ss, buffers[1], ret_to="1771:0F21")      # 0F1C
    ax, dx = yield from gcall(mem, ax, dx, "23E4:06B7", cs, 0x0E6A, ret_to="1771:0F2B")          # 0F21-0F26
    push(mem, ss, "1771:0F2F")                              # 0F2B-0F30
    push(mem, buffers[2], "1771:0F30")
    ax, dx = yield from gcall(mem, counts[3], 0, "214B:09DA", 0, counts[3], ret_to="1771:0F3F")   # 0F31-0F3A
    drop(mem, 2)
    ax, dx = yield from gcall(mem, ax, dx, "23E4:06B7", ss, buffers[2], ret_to="1771:0F44")      # 0F3F
    drop(mem, 2)                                            # 0644 pops the first pointer too (retf 0xA)
    yield from gcall(mem, 0xA, dx, "23E4:0644", ss, buffers[0], dest_seg, dest_off, 0xA, ret_to="1771:0F52")   # 0F44-0F4D


# -- the player's own tactics ------------------------------------------------------------------------------------
@PORTS.port("1771:33CD", ret="retf 2")
def force_tactic4_off(mem, variant):
    """33CD: set element 8 and clear element 4 of the player's +0xF (214B:0C79, 0CA1)."""
    n = mem.arg(0)
    ax, dx = mul(n, 0x14)                                   # 33D3-33D9
    p = Rec(mem, PLAYERS, ax)
    byte, ax, dx = bit_set(p.u8(0xF), 8)                    # 33E7-33F4
    p.w8(0xF, byte, S_SET_WRITE)
    byte, ax, dx = bit_clear(p.u8(0xF), 4)                  # 33F9-3406
    p.w8(0xF, byte, S_CLEAR_WRITE)
    return end(mem, ax, dx)


@PORTS.port("1771:3431", ret="retf 2")
def set_player_tactics(mem, variant):
    """3431: from the player's own fields: element 8 on and 4 off when the hardness is below 4 (33CD), then by the
    position code (the set CS:3411): elements 5 and 1, or for position 2 elements 5 (when +5 < 0xE), 6 and 2."""
    n = mem.arg(0)
    mem.enter(4, "1771:3431")                               # 3431-3434
    ax, dx = mul(n, 0x14)                                   # 3437-343D
    p = Rec(mem, PLAYERS, ax)
    ax, dx = yield from gcall(mem, ax, dx, "1771:2FFB", n, ret_to="1771:3452")      # 344B-344F
    if (ax & 0xFF) < 4:                                     # 3452: cmp al, 4; jae
        ax, dx = yield from gcall(mem, ax, dx, "1771:33CD", n, ret_to="1771:345D")  # 3456-345A
    pos = p.u8(6)                                           # 345D-3464: mov al, [di + 6]
    ax = (ax & 0xFF00) | pos
    in_set, ax = cs_set_has(TACTIC_POSITIONS, pos, ax)      # 3465-346A (23E4:08DF; AL = 1 << (e & 7))
    if in_set:                                              # 346F: je 3497 (not in the set)
        for elem in (5, 1):                                 # 3471-348E
            byte, ax, dx = bit_set(p.u8(0xF), elem)
            p.w8(0xF, byte, S_SET_WRITE)
        return end(mem, ax, dx)
    if pos == 2:                                            # 3497-349F
        elems = (6, 2) if p.u8(5) >= 0xE else (5, 6, 2)     # 34A1-34A9: element 5 only when +5 < 0xE
        for elem in elems:                                  # 34AB-34DC
            byte, ax, dx = bit_set(p.u8(0xF), elem)
            p.w8(0xF, byte, S_SET_WRITE)
    return end(mem, ax, dx)


@PORTS.port("1771:34E7", ret="retf 2")
def reset_own_tactics(mem, variant):
    """34E7: the +0xF of each of a country's players (squad slots 1..20, a word 0 is empty) cleared, then 3431."""
    country = mem.arg(0)
    mem.enter(6, "1771:34E7")
    ax, dx = mul(country, 0xBF)                             # 34ED-34F3
    c = Rec(mem, COUNTRIES, ax)
    for slot in range(1, 0x15):                             # 3501-3550
        ax = (2 * slot) & 0xFFFF                            # 350B-350E: shl ax, 1
        word = c.u16(2 * slot - 2)                          # 3510-3515
        if word == 0:                                       # 351A: je 354C
            continue
        ax, dx = mul(word, 0x14)                            # 3526-352D
        Rec(mem, PLAYERS, ax).w8(0xF, 0, "1771:3535")       # 352F-3535
        ax = (2 * slot) & 0xFFFF                            # 353A-353D
        ax, dx = yield from gcall(mem, ax, dx, "1771:3431", word, ret_to="1771:354C")   # 3544-3549
    return end(mem, ax, dx)


# -- a player's strength -------------------------------------------------------------------------------------------
@PORTS.port("1771:3179", ret="retf 2")
def out_of_place_flag(mem, variant):
    """3179: 1 when the player plays on the wrong foot for the position (3088, 3041, the sets CS:3139 and CS:3159) or
    when exactly one of +6 and +7 is 0."""
    n = mem.arg(0)
    mem.enter(6, "1771:3179")
    ax, dx = mul(n, 0x14)                                   # 317F-3185
    p = Rec(mem, PLAYERS, ax)
    ax, dx = yield from gcall(mem, ax, dx, "1771:3088", n, ret_to="1771:319A")      # 3193-3197
    foot = ax & 0xFF                                        # 319A: [bp - 2] = al
    ax, dx = yield from gcall(mem, ax, dx, "1771:3041", n, ret_to="1771:31A4")      # 319D-31A1
    # Nothing after 3041 changes AH or DX (08DF leaves them), so they are 3041's whatever the path.
    keep = ax & 0xFF00
    flag = None
    if not (ax & 0xFF) and foot != 0:                       # 31A4-31AC
        right = RIGHT_FOOT_BAD - {7} if variant == "foot-right-3" else RIGHT_FOOT_BAD
        if p.u8(6) in right:                                # 31AE-31C0: 08DF on CS:3139
            flag = 1
    if flag is None and foot == 0:                          # 31C2-31DA
        if p.u8(6) in LEFT_FOOT_BAD:                        # 08DF on CS:3159
            flag = 1
    if flag is None:
        p6, p7 = p.u8(6), p.u8(7)                           # 31DC-3202
        flag = 1 if (p6 == 0) != (p7 == 0) else 0
    return ret(mem, keep | flag, dx)                        # 3204/3208, 320A-3210


@PORTS.port("1771:377E", ret="retf 2")
def player_strength(mem, variant):
    """377E: (+4 - 0x3E) + s8(+0xE), then plus s8(+0xC) when that is below 0x20 else minus a sixteenth, clamped 0..0x100,
    halved when 3179 says so; 0 when 3216 says unavailable. (T43's model: runtime/model/quick_engine.py.)"""
    n = mem.arg(0)
    mem.enter(8, "1771:377E")
    ax, dx = mul(n, 0x14)                                   # 3784-378A
    p = Rec(mem, PLAYERS, ax)
    ax, dx = yield from gcall(mem, ax, dx, "1771:3216", n, ret_to="1771:379F")      # 3798-379C
    if ax & 0xFF:                                           # 379F-37A1
        return ret(mem, 0, dx)                              # 37A3-37A8
    dx = s8(p.u8(0xE)) & 0xFFFF                             # 37AA-37B2: cwde; mov dx, ax
    v = (p.u8(4) - 0x3E + dx) & 0xFFFF                      # 37B4-37C2
    ax = v
    c = s8(p.u8(0xC))
    if c >= 0x20:                                           # 37C8-37CD: jl 37DD
        q, dx = idiv(s16(v), 0x10)                          # 37CF-37D6: cdq; idiv 0x10
        v = (v - q) & 0xFFFF                                # 37D8
        ax = q
    else:
        ax = c & 0xFFFF                                     # 37DD-37E5: cwde; add [bp - 4], ax
        v = (v + c) & 0xFFFF
    if s16(v) < 0:                                          # 37E8-37F3
        v, ax = 0, 0
    elif s16(v) > 0x100:                                    # 37F5-37FC
        v = 0x100
    ax, dx = yield from gcall(mem, ax, dx, "1771:3179", n, ret_to="1771:3808")      # 3801-3805
    if ax & 0xFF:                                           # 3808-380A
        q, dx = idiv(s16(v), 2)                             # 380C-3813: cdq; idiv 2
        v = q
        ax = q
    else:
        ax = v
    return ret(mem, v, dx)                                  # 3818-3821 (AX = v in both cases)


# -- the marking words ---------------------------------------------------------------------------------------------
@PORTS.port("1771:3E2F", ret="ret 6")
def pick_mark_target(mem, variant):
    """3E2F (a nested procedure of 3EF8; its parent's BP, hi, lo): for the opposing slots 11 down to 2 whose position
    byte (the opponents' string at BP - 0x1C + slot) is in [lo, hi], and the rows r = 1..4 of the table DS:0EE6 + 14 r
    (the own position that marks it), the first own slot (the own string at BP - 0x10) holding that position is taken: its
    entry is cleared, the opponent's is cleared and the opponent's slot is noted at BP - 0x27 + own slot."""
    parent = mem.frame(mem.arg(0))
    hi, lo = mem.arg(1), mem.arg(2)                         # [bp + 6], [bp + 8]
    ax, dx = mem.reg("ax"), mem.reg("dx")                   # the caller's, which the loop carries when it does not write them
    f = mem.enter(0x106, "1771:3E2F")                       # 3E2F-3E32
    bp = mem.reg("bp")
    pattern = (bp - 0x106) & 0xFFFF                         # 3E73: lea di, [bp - 0x106]
    target = (mem.arg(0) - 0x10) & 0xFFFF                   # 3E9F-3EA2: [bp + 4] + 0xFFF0
    ss = mem.reg("ss")
    for r in range(1, 5):                                   # 3E36-3EEF
        for j in range(11, 1, -1):                          # 3E40-3EE6
            oc = parent.u8(j - 0x1C)                        # 3E4D-3E56 (xor ah, ah)
            ax = oc
            if oc < lo:                                     # 3E58-3E5D
                continue
            if oc > hi or (variant == "mark-hi-excl" and oc == hi):    # 3E6E-3E71
                continue
            push(mem, ss, "1771:3E77")                      # 3E73-3E78
            push(mem, pattern, "1771:3E78")
            ax, dx = mul(r, 14)                             # 3E89-3E8C
            ax = (ax & 0xFF00) | mem.ds8(0xEE6 + ((ax + oc) & 0xFFFF))      # 3E8F-3E95
            ax, dx = yield from gcall(mem, ax, dx, "23E4:075A", ax, ret_to="1771:3E9F")     # 3E99-3E9A (leaves the pointer)
            drop(mem, 2)
            ax, dx = yield from gcall(mem, ax, dx, "23E4:06E3", ss, pattern, ss, target, ret_to="1771:3EAD")  # 3EA5-3EA8
            pos = (ax + 1) & 0xFFFF                         # 3EAD: inc ax
            ax = pos
            if pos <= 1:                                    # 3EB1-3EB5: jbe
                continue
            parent.w8(pos - 0x11, 0, "1771:3EBF")           # 3EB7-3EBF
            parent.w8(j - 0x1C, 0, "1771:3ECC")             # 3EC4-3ECC
            dx = (dx & 0xFF00) | j                          # 3ED1: mov dl, [bp - 2]
            parent.w8(pos - 0x27, j, "1771:3EDC")           # 3ED4-3EDC
    return end(mem, ax, dx)


@PORTS.port("1771:3EF8", ret="retf")
def set_marking_words(mem, variant):
    """3EF8: per team t the marking words (DS:9A3E + 0x28 t + 2 slot): the own positions string (slots 2..11; 0 for a
    sweeper, a protect-zone player or an unavailable one) and the opponents', the protect-zone men cleared from the
    opponents', the five calls of 3E2F, then each marking word set from the match (3E2F's marks) or cleared."""
    f = mem.enter(0x32, "1771:3EF8")
    ss = mem.reg("ss")
    bp = mem.reg("bp")
    DS = mem.DS * 16
    ax = dx = 0
    for t in (0, 1):                                        # 3EFE-3F04, 4250-4256
        other = 1 - t
        ax, dx = mul(mem.ds16(TEAM_COUNTRY + 2 * t), 0xBF)                  # 3F0F-3F16
        mine = Rec(mem, COUNTRIES, ax)
        ax = dx = 0
        mem.w16(DS + ((MARK_BASE + 0x28 * t + 2) & 0xFFFF), 0, "1771:3F31")  # 3F24-3F31: slot 1's word := 0
        ax, dx = mul(mine.u16(2), 0x14)                     # 3F35-3F3F: slot 2's player
        if Rec(mem, PLAYERS, ax).u8(6) == 1:                # 3F41-3F47
            ax = dx = 0
            mem.w16(DS + ((MARK_BASE + 0x28 * t + 4) & 0xFFFF), 0, "1771:3F5B")   # 3F4E-3F5B: slot 2's word := 0
        f.w8(-0x10, 10, "1771:3F5F")                        # 3F5F, 3F63: the two strings' lengths
        f.w8(-0x1B, 10, "1771:3F63")
        for j in range(2, 12):                              # 3F67-4054
            w = mine.u16(2 * j - 2)
            ax, dx = mul(w, 0x14)                           # 3F71-3F82
            q = Rec(mem, PLAYERS, ax)
            unusable = q.u8(6) == 1                         # 3F93: je 3FC7
            if not unusable:
                ax, dx = bit_test(q.u8(0x10), 7)            # 3F9A-3FA8
                unusable = bool(ax & 0xFF)
            if not unusable:
                ax, dx = yield from gcall(mem, ax, dx, "1771:3216", w, ret_to="1771:3FC3")      # 3FB1-3FC0
                unusable = bool(ax & 0xFF)
            if unusable:
                f.w8(j - 0x11, 0, "1771:3FCA")              # 3FC7-3FCA
            else:
                ax = (ax & 0xFF00) | q.u8(6)                # 3FD0-3FD3
                f.w8(j - 0x11, ax & 0xFF, "1771:3FDA")
            ax, dx = mul(mem.ds16(TEAM_COUNTRY + 2 * other), 0xBF)          # 3FDD-3FF5 (cmp [bp - 5], 0; mov al, 0/1; cwde)
            opponents = Rec(mem, COUNTRIES, ax)
            ow = opponents.u16(2 * j - 2)                   # 4003-400D
            ax, dx = mul(ow, 0x14)                          # 400D-4014
            oq = Rec(mem, PLAYERS, ax)
            ax, dx = yield from gcall(mem, ax, dx, "1771:3216", ow, ret_to="1771:4034")     # 4022-4031
            if ax & 0xFF:                                   # 4034-4036
                f.w8(j - 0x1C, 0, "1771:403B")              # 4038-403B
            else:
                ax = (ax & 0xFF00) | oq.u8(6)               # 4041-4044
                f.w8(j - 0x1C, ax & 0xFF, "1771:404B")
        for j in range(2, 12):                              # 4057-40FD: the protect-zone men take their own marker's man
            ax, dx = mul(mine.u16(2 * j - 2), 0x14)         # 4061-4072
            q = Rec(mem, PLAYERS, ax)
            ax, dx = bit_test(q.u8(0x10), 7)                # 4080-408E
            if not (ax & 0xFF):                             # 4093: je 40F7
                continue
            for k in range(2, 12):                          # 4097-40F5
                ax, dx = mul(t, 0x28)                       # 40A8-40B3
                bx = mem.ds16(MARK_BASE + 0x28 * t + 2 * j)           # 40B5
                ax, dx = mul(mem.ds16(TEAM_COUNTRY + 2 * other), 0xBF)  # 40C0-40D8
                ax = Rec(mem, COUNTRIES, ax).u16(2 * k - 2)  # 40DA-40E2
                if ax == bx:                                # 40E6-40E8
                    f.w8(k - 0x1C, 0, "1771:40ED")          # 40EA-40ED
        ax, dx = yield from gcall(mem, 0, dx, "214B:0018", ss, (bp - 0x26) & 0xFFFF, 0xB, 0, ret_to="1771:4111")   # 4100-410C
        for hi, lo, ret_to in ((0xD, 0xC, "411D"), (0xB, 9, "4129"), (8, 5, "4135"), (1, 1, "4141"), (4, 2, "414D")):
            ax, dx = yield from gcall(mem, hi, dx, "1771:3E2F", lo, hi, bp, ret_to="1771:" + ret_to, far=False)  # 4111-414A
        for j in range(2, 12):                              # 414D-424D
            ax, dx = mul(mine.u16(2 * j - 2), 0x14)         # 4157-416A
            q = Rec(mem, PLAYERS, ax)
            ax, dx = bit_test(q.u8(0x10), 7)                # 4176-4184
            if not (ax & 0xFF):                             # 418B: jne 41A7
                ax, dx = (0, 0)                             # 418D-41A3: AX := 0 (cwde; mul 0x28; xor ax, ax)
                mem.w16(DS + ((MARK_BASE + 0x28 * t + 2 * j) & 0xFFFF), 0, "1771:41A3")
            ax, dx = bit_test(q.u8(0x10), 7)                # 41A7-41B5
            if ax & 0xFF:                                   # 41BA: je 41C1; jmp 4247
                continue
            ax, dx = bit_test(mine.u8(0x2D), 8)             # 41C1-41CF: team tactics, element 8
            if not (ax & 0xFF):                             # 41D4
                continue
            mark = f.u8(j - 0x27)                           # 41D8-41DF: jbe 422D
            if mark > 0:                                    # 41E1-4227
                ax, dx = mul(mem.ds16(TEAM_COUNTRY + 2 * other), 0xBF)      # 41FE-4205
                bx = Rec(mem, COUNTRIES, ax).u16(2 * mark - 2)             # 4207-420F
                ax, dx = mul(t, 0x28)                       # 421A-4223
                mem.w16(DS + ((MARK_BASE + 0x28 * t + 2 * j) & 0xFFFF), bx, "1771:4227")
            else:
                ax, dx = mul(t, 0x28)                       # 422D-423D
                ax = 0                                      # 4241
                mem.w16(DS + ((MARK_BASE + 0x28 * t + 2 * j) & 0xFFFF), 0, "1771:4243")
    return end(mem, ax, dx)
