#!/usr/bin/env python3
"""Which compiler routine is GOAL's System helper at 23E4:025D (a plain `cld; rep movsb`, retf 0Ah)?
Looks for it in the System segment of T5.EXE (`a := b` on two arrays) and T6.EXE (`Move(a, b, 4000)`) of a
compiler, and for the overlap-safe public Move in GOAL.   usage: movecheck.py GOAL.unp.exe T5.EXE T6.EXE"""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

plain = bytes.fromhex('8bdc8cda36c5770a36c47f06368b4f04fcf3a48edaca0a00')
overlap_safe = bytes.fromhex('fc3bf7730703f103f94e4ffd')  # cld; cmp si,di; jae..; add si,cx; add di,cx; dec si; dec di; std
g, _ = sysseg.system_code(sys.argv[1])
print('GOAL: plain helper at 23E4:%04X; overlap-safe Move present: %s' % (g.find(plain), g.find(overlap_safe) >= 0))
for p in sys.argv[2:]:
    c, _ = sysseg.system_code(p)
    print('%s: plain helper %s, overlap-safe Move %s' % (p.rsplit('/', 1)[-1], c.find(plain) >= 0, c.find(overlap_safe) >= 0))
