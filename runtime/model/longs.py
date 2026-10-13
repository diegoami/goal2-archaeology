"""The long-integer helpers `214B:0D56` (signed 32-bit max) and `23E4:0279` (32-bit multiply) (T48, milestone M2d).

Words are 16-bit, longs are (low word, high word) pairs. Every constant cites its listing line
(static/goal-exe/code/seg_214B_02.asm for 0D56, seg_23E4_01.asm:273 for 0279). The `flags` a model returns are the
six arithmetic flags (CF PF AF ZF SF OF) the routine's last flag-setting instruction leaves; the adapter merges them
into the guest's FLAGS word (every other bit is unchanged by these routines, which have no `popf`/`cli`/`std`).
"""
from collections import namedtuple

CF, PF, AF, ZF, SF, OF = 0x0001, 0x0004, 0x0010, 0x0040, 0x0080, 0x0800
ARITH = CF | PF | AF | ZF | SF | OF

Max = namedtuple("Max", "ax dx es flags")
Mul = namedtuple("Mul", "ax dx bx cx si di flags")


def s16(x):
    return x - 0x10000 if x & 0x8000 else x


def _flags(result, carry, overflow, aux):
    """CF PF AF ZF SF OF of a 16-bit result; PF is the parity of the result's low byte (even -> set)."""
    return ((CF if carry else 0) | (PF if bin(result & 0xFF).count("1") % 2 == 0 else 0) | (AF if aux else 0)
            | (ZF if result == 0 else 0) | (SF if result & 0x8000 else 0) | (OF if overflow else 0))


def sub16_flags(x, y):
    """The flags of `cmp x, y` (16-bit): borrow, signed overflow, borrow out of bit 3."""
    r = (x - y) & 0xFFFF
    return _flags(r, x < y, (x ^ y) & (x ^ r) & 0x8000, (x ^ y ^ r) & 0x10)


def add16_flags(x, y):
    """The flags of `add x, y` (16-bit)."""
    r = (x + y) & 0xFFFF
    return _flags(r, x + y > 0xFFFF, ~(x ^ y) & (x ^ r) & 0x8000, (x ^ y ^ r) & 0x10)


def max_0d56(a_lo, a_hi, b_lo, b_hi):
    """`214B:0D56(a, b)`: the signed 32-bit maximum, ties and a below b giving b (`retf 8`; seg_214B_02.asm:560-588).
    a is at [bp + 0xA] (low) / [bp + 0xC] (high) (0D5C `les ax, [bp + 0xa]`: AX = low word, ES = high word), b at
    [bp + 6] / [bp + 8] (0D7A). The high words compare signed (0D61 `cmp dx, [bp + 8]`; 0D64 `jg` -> a, 0D66 `jl` -> b);
    equal high words compare the low words UNSIGNED (0D68 `cmp ax, [bp + 6]`; 0D6B `jbe` -> b, else a at 0D6D).
    Returns AX = the low word and DX = ES = the high word of the winner (0D85-0D88 `les ax, [bp - 4]; mov dx, es`) and
    the flags of the last `cmp` (nothing after it touches them: 0D6D-0D8D are mov/les/jmp/pop)."""
    if a_hi != b_hi:
        flags = sub16_flags(a_hi, b_hi)                                         # 0D61
        a_wins = s16(a_hi) > s16(b_hi)                                          # 0D64 jg / 0D66 jl
    else:
        flags = sub16_flags(a_lo, b_lo)                                         # 0D68
        a_wins = a_lo > b_lo                                                    # 0D6B jbe -> b
    lo, hi = (a_lo, a_hi) if a_wins else (b_lo, b_hi)
    return Max(lo, hi, hi, flags)


def mul_0279(ax, dx, bx, cx):
    """`23E4:0279`, register convention, `retf` (seg_23E4_01.asm:273-290): DX:AX times the long whose LOW word is CX and
    HIGH word is BX, the low 32 bits. si = ax; di = dx (0279, 027B);
    0x027D `mul cx`: DX:AX = ax * cx, pushed (027F, 0280) and popped back as the product's low and high words (028D, 028E);
    0x0283 `mul bx`: bx = low word of si * bx (0285); 0x0289 `mul cx`: cx = low word of di * cx (028B);
    0x028F, 0x0291: dx += bx; dx += cx (the cross terms). The result is DX:AX; SI, DI, BX and CX are left as above
    (the high words of the two later `mul`s are lost), and the flags are those of the last `add dx, cx`."""
    si, di = ax, dx                                                             # 0279, 027B
    low = ax * cx                                                               # 027D
    bx_out = (si * bx) & 0xFFFF                                                 # 0281-0285
    cx_out = (di * cx) & 0xFFFF                                                 # 0287-028B
    partial = ((low >> 16) + bx_out) & 0xFFFF                                   # 028F
    dx_out = (partial + cx_out) & 0xFFFF                                        # 0291
    return Mul(low & 0xFFFF, dx_out, bx_out, cx_out, si, di, add16_flags(partial, cx_out))
