"""The draw wrappers `214B:06B1(n)` and `214B:06D0(n)` (F004; T47, milestone M2c).

Both are `retf 2` routines (seg_214B_01.asm:911, :935) that read the far seed pointer from DS:A978
(`les di, [0xa978]`, 06B7 and 06D6), push it with n (`push word ptr [bp + 6]`, 06BD and 06DC) and call
`214B:0688` (06C1, 06E0): the seed word steps and is stored (`stosw`, 069F) and AX = DX = the draw,
1..n (06A4-06A8; recreate.draw). What each does after the call:
- `06B1` stores AX in a local and reloads it (06C4, 06C7): AX = DX = the draw, nothing else changes;
- `06D0` compares `cmp ax, 1` (06E3): AL = 1 when the draw is 1 (06EC), else 0 (06E8); AH keeps the
  draw's high byte and DX the draw (neither is written after 0688: 06EE-06F1 touch AL only).
"""
from collections import namedtuple

import recreate

SUCCESS_DRAW = 1        # 06E3 `cmp ax, 1`

Wrapper = namedtuple("Wrapper", "draw seed ax dx")


def draw_06b1(seed, n):
    """`214B:06B1(n)` on the seed word: the draw, the new seed, and the AX and DX it returns."""
    draw, new_seed = recreate.draw(seed, n & 0xFFFF)                # 06BD-06C1 -> 0688
    return Wrapper(draw, new_seed, draw & 0xFFFF, draw & 0xFFFF)    # 06C4-06C7


def draw_06d0(seed, n):
    """`214B:06D0(n)`: AL = 1 when the draw is 1, else 0 (06E3-06EC); AH the draw's high byte; DX the draw."""
    draw, new_seed = recreate.draw(seed, n & 0xFFFF)                # 06DC-06E0 -> 0688
    result = 1 if draw == SUCCESS_DRAW else 0
    return Wrapper(draw, new_seed, (draw & 0xFF00) | result, draw & 0xFFFF)
