"""T48: run the ORIGINAL machine code of 214B:0D56 and 23E4:0279 (the bytes of the listing's routine block) on a bare
machine, to compare the models in runtime/model/longs.py with what the code does. Test support, not a test."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/emul"))
from watched_match import Guest  # noqa: E402

LISTINGS = ROOT / "static/goal-exe/code"
CODE_SEG, ROUTINE_SEG, SS, SP0 = 0x1000, 0x2000, 0x0800, 0xFF00
SENTINEL = {"BX": 0x1111, "CX": 0x2222, "SI": 0x3333, "DI": 0x4444, "ES": 0x5555}
ARITH_FLAGS = 0x08D5


def routine_bytes(seg, off):
    """The bytes of the routine block 'seg:off' from its listing, as {offset: byte} (up to the next routine)."""
    out = {}
    head = f"; ---- routine {seg:04X}:{off:04X} "
    for path in sorted(LISTINGS.glob(f"seg_{seg:04X}_*.asm")):
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            if line.startswith(head):
                for body in lines[i + 1:]:
                    if body.startswith("; ---- routine"):
                        return out
                    m = re.match(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} ?)+?)\s{2,}\S", body)
                    if m:
                        for k, h in enumerate(m.group(2).split()):
                            out[int(m.group(1), 16) + k] = int(h, 16)
                return out
    raise ValueError(head)


def run(seg, off, caller, regs, flags=0x0202):
    """The routine at seg:off (listing bytes, placed at ROUTINE_SEG:off) called far from `caller` (bytes) with `regs`;
    returns the registers after the guest halts."""
    mem = bytearray(0x40000)
    for o, b in routine_bytes(seg, off).items():
        mem[ROUTINE_SEG * 16 + o] = b
    call = bytes([0x9A, off & 0xFF, off >> 8, ROUTINE_SEG & 0xFF, ROUTINE_SEG >> 8])
    code = caller + call + bytes([0xF4])
    mem[CODE_SEG * 16:CODE_SEG * 16 + len(code)] = code
    start = {"CS": CODE_SEG, "EIP": 0, "SS": SS, "ESP": SP0, "DS": 0, "EFLAGS": flags, **SENTINEL, **regs}
    g = Guest(memory=mem, regs=start)
    g.emulate(CODE_SEG * 16 + len(code) - 1, 5)
    return {r: g.reg(r) for r in ("AX", "DX", "BX", "CX", "SI", "DI", "ES", "SP", "EFLAGS")}


def original_max(a, b, flags=0x0202):
    """214B:0D56 on the longs a and b (32-bit patterns): the registers after it returns."""
    push = lambda w: bytes([0xB8, w & 0xFF, (w >> 8) & 0xFF, 0x50])           # mov ax, w; push ax
    caller = push(a >> 16) + push(a & 0xFFFF) + push(b >> 16) + push(b & 0xFFFF)
    return run(0x214B, 0x0D56, caller, {}, flags)


def original_mul(ax, dx, bx, cx, flags=0x0202):
    """23E4:0279 with the given registers: the registers after it returns."""
    return run(0x23E4, 0x0279, b"", {"AX": ax, "DX": dx, "BX": bx, "CX": cx}, flags)
