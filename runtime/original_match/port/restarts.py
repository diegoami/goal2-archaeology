"""The dead-ball restarts (T59 ports the throw-in; T67 adds the others): routines that stop play and call the
original's code around them (the substitution check, the commentary, the restart's set-up), the first ports with
guest calls (port/guest.py).

From the listing static/goal-exe/code/seg_0791_12.asm 6E11-6E6D (dead_ball_throw_in, routines.tsv row 0791:6E11; 93
bytes, 43 instructions); the line comments are its offsets. Its callees stay the original's and are called as the
listing calls them, each with its return address: 8062 (ret, seg_0791_13.asm 8205), 2996 (ret, seg_0791_04.asm 29B2),
6BF1 (ret 4, seg_0791_11.asm 6D4B), 2AA3 (ret 2, seg_0791_05.asm 2AD1), 2BE5 (retf 4, seg_0791_05.asm 2C26, called
by `push cs; call near`), 26A0 (ret 2, seg_0791_04.asm 26BF)."""
from .guest import call
from .mem import s8
from . import Registry

PORTS = Registry("restarts", "the dead-ball restarts: the throw-in 0791:6E11 (T59)")
PORTS.variant("side-swapped", "6E26-6E2E's test inverted: the other side's byte of DS:8311 is passed to 6BF1")


@PORTS.port("0791:6E11", ret="ret")                       # 6E6D ret
def dead_ball_throw_in(mem, variant):
    mem.enter(0, "0791:6E11")                             # 6E11-6E12 push bp; mov bp, sp
    if mem.ds8(0x8326) != 0:                              # 6E14 cmp byte ptr [0x8326], 0; jne 6E6A
        return None                                       # AX, DX as they came
    mem.wds8(0x830E, 0, "0791:6E1B")                      # 6E1B mov byte ptr [0x830e], 0
    yield call("0791:8062", ret_to="0791:6E23", far=False)            # 6E20 the substitution check
    ax = yield call("0791:2996", ret_to="0791:6E26", far=False)       # 6E23
    side = 0 if ax & 0xFF else 1                          # 6E26-6E2E: al != 0 -> 0, else 1
    if variant == "side-swapped":
        side ^= 1
    value = mem.ds8(0x8311 + side)                        # 6E30-6E37 cbw; mov di, ax; mov al, [di + 0x8311]; xor ah, ah
    ax = yield call("0791:6BF1", value, 7, ret_to="0791:6E40", far=False)     # 6E39-6E3D push ax; mov al, 7; push ax
    ax = yield call("0791:2AA3", (ax & 0xFF00) | 0x2B, ret_to="0791:6E46", far=False)   # 6E40-6E43: AH is 6BF1's
    record = (mem.ds8(0x830B) * 0x16 + 0x80E8) & 0xFFFF   # 6E46-6E52: the pitch record of slot [0x830b]
    ax = yield call("0791:2BE5", mem.reg("ds"), record, ret_to="0791:6E5C", far=True)   # 6E56-6E59 push ds; push di; push cs
    toward = 1 if s8(ax & 0xFF) > 0 else 0                # 6E5C-6E64 or al, al; jg
    yield call("0791:26A0", (ax & 0xFF00) | toward, ret_to="0791:6E6A", far=False)      # 6E66-6E67: AH is 2BE5's
    return None                                           # 6E6A-6E6D: AX, DX as 26A0 left them
