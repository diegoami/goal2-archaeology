"""The contest gate `0791:287C(pitch, element)` (F022; T46, milestone M2b): a pass/fail draw on a
skill.

The routine (seg_0791_04.asm:946-962) calls `278A(pitch, element)` (28 8B), divides the value by 0x20
(`xor dx, dx; mov cx, 0x20; div cx`, 288E-2893, UNSIGNED: the value is the 16-bit AX), adds 1 (2895),
and calls `214B:06D0(n)` (2897): `06D0` draws `214B:0688(n)` through the far pointer DS:A978 (06D6,
06E0) and returns 1 when the draw is 1 (`cmp ax, 1`, 06E3), else 0 (seg_214B_01.asm:915-931). `287C`
returns 1 when `06D0` returned 0 (289C `or al, al; je 28A4` -> `mov al, 1`) and 0 otherwise (28A0):
**1 with probability (n - 1) / n**.

What the proof compares (REGS_RETURNED) besides the seed word's two bytes:
- AL = the result (28A6-28A9);
- AH = the high byte of the draw: 0688 ends `inc dx; mov [bp - 2], dx; mov ax, [bp - 2]` (06A4-06A8), so AX is
  the draw; 06D0 and 287C change AL only (06E8/06EC, 28A0/28A4);
- DX = the draw: 0688's `mul word ptr [bp + 6]` leaves the high word in DX, `inc dx` (06A4), and nothing
  after it writes DX (06D0 and 287C do not).
"""
from collections import namedtuple

import recreate

DIVISOR = 0x20          # 2890 `mov cx, 0x20`; 2893 `div cx`
SUCCESS_DRAW = 1        # 06E3 `cmp ax, 1`: 06D0 is true on this draw only

Gate = namedtuple("Gate", "result n draw seed ax dx")


def gate(value, seed):
    """`287C` given 278A's value (AX, 16 bits) and the seed word the draw steps: the result (AL), n, the
    draw (`214B:0688`'s AX and DX), the new seed, and the AX and DX the routine returns."""
    n = ((value & 0xFFFF) // DIVISOR + 1) & 0xFFFF                  # 288E-2895
    draw, new_seed = recreate.draw(seed, n)                          # 06D6-06E0 -> 0688 (F004)
    result = 0 if draw == SUCCESS_DRAW else 1                        # 06E3-06EC, 289C-28A4
    return Gate(result, n, draw, new_seed, (draw & 0xFF00) | result, draw & 0xFFFF)
