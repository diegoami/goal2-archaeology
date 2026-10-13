"""Rework R2/R3 counterexamples through the ORIGINAL bytes (Unicorn, as foot_truth.py).
1. 0791:278A with keeping extra 64 (pitch +0x11), element 4, player +4=255 +5=15 +7=2 +0xC=16 +0xE=16: value with pitch +0x13 = 0 and = 1
   (the halving applies to the derived skill, the extra is added after it).
2. 1771:2FAD (height) for every club code and player number mod 12: min and max height per club code (height reads +7, not +6).
usage: python3 -B contest_counter.py <GOAL.EXE> OUTDIR   -> OUTDIR/contest-counter-<UTC>.log"""
import os, struct, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foot_truth import load, Guest, X
psha, usha, image = load(sys.argv[1]); g = Guest(image)
ds = g.DS * 16
out = ["packed GOAL.EXE %s" % psha]
def call278A(flag, extra, element=4):
    rec = bytearray(20); rec[4] = 255; rec[5] = 15; rec[7] = 2; rec[6] = 2; rec[0xC] = 16; rec[0xE] = 16
    g.put(g.players * 16 + 3 * 20, rec)
    pr = bytearray(0x16); struct.pack_into("<H", pr, 0xD, 3); pr[6] = 3; pr[0x11] = extra; pr[0x13] = flag
    g.put(ds + 0x9000, pr)
    mu = g.mu; sp = 0xFF00
    # frame: [bp+6]=off [bp+8]=seg of pitch, [bp+0xA]=element, retf 6
    mu.mem_write(0x90000 + sp - 6, struct.pack("<HHH", 0x9000, g.DS, element))
    mu.mem_write(0x90000 + sp - 8, struct.pack("<H", 0x0100)); mu.mem_write(0x90000 + sp - 10, struct.pack("<H", 0))
    mu.reg_write(X.UC_X86_REG_SP, sp - 10); mu.reg_write(X.UC_X86_REG_CS, 0x0791)
    mu.mem_write(0x1000, b"\xF4")
    mu.emu_start(0x0791 * 16 + 0x278A, 0x1000, count=5000)
    return mu.reg_read(X.UC_X86_REG_AX)
for extra in (0, 64):
    a, b = call278A(0, extra), call278A(1, extra)
    out.append("278A element 4, keeping extra %d: value flag0 = %d, flag1 = %d, ratio %.3f" % (extra, a, b, b / a if a else 0))
H = {}
for club in range(14):
    hs = []
    for n in range(12):
        rec = bytearray(20); rec[7] = club
        g.put(g.players * 16 + n * 20, rec)
        mu = g.mu; sp = 0xFF00
        mu.mem_write(0x90000 + sp - 2, struct.pack("<H", n)); mu.mem_write(0x90000 + sp - 4, struct.pack("<H", 0x0100)); mu.mem_write(0x90000 + sp - 6, struct.pack("<H", 0))
        mu.reg_write(X.UC_X86_REG_SP, sp - 6); mu.reg_write(X.UC_X86_REG_CS, 0x1771)
        mu.emu_start(0x1771 * 16 + 0x2FAD, 0x0100 * 16, count=2000)
        hs.append(mu.reg_read(X.UC_X86_REG_AX) & 0xFFFF)
    H[club] = (min(hs), max(hs))
out.append("2FAD height (min, max) by CLUB code over n mod 12: " + " ".join("%d:%d-%d" % (c, *H[c]) for c in H))
out.append("tall (>= 72) possible for club codes: " + str([c for c in H if H[c][1] >= 72]))
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
open(os.path.join(sys.argv[2], "contest-counter-%s.log" % ts), "x").write("\n".join(out) + "\n")
print("\n".join(out))
