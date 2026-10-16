#!/usr/bin/env python3
"""Which compiler routine is GOAL's System helper at 23E4:025D (a plain `cld; rep movsb`, retf 0Ah)?
Looks for its instruction sequence (masked mnemonics, no bytes) in the System segment of T5.EXE (`a := b` on two
arrays) and T6.EXE (`Move(a, b, 4000)`) of a compiler, and for the overlap-safe public Move (a `std`) in GOAL.
usage: movecheck.py GOAL.unp.exe T5.EXE T6.EXE"""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

PLAIN = ['mov bx, sp', 'mov dx, ds', 'lds si, ptr ss:[bx + N]', 'les di, ptr ss:[bx + N]', 'mov cx, word ptr ss:[bx + N]',
         'cld ', 'rep movsb byte ptr es:[di], byte ptr [si]', 'mov ds, dx', 'retf N']
OVERLAP_SAFE = ['cld ', 'cmp si, di', 'jae N', 'add si, cx', 'add di, cx', 'dec si', 'dec di', 'std ']


def find(code, seq):
    """Offset of the first place where the decoded instruction sequence equals seq. Decoding starts at every
    offset, because a linear sweep from the segment start loses sync on the string data before the routines."""
    for i in range(len(code)):
        names = [s for _, _, s, _ in sysseg.skel(code[i:i + 12 * len(seq)], 0)[:len(seq)]]
        if names == seq:
            return i
    return None


def report(label, code):
    p, o = find(code, PLAIN), find(code, OVERLAP_SAFE)
    print('%s: plain helper %s; overlap-safe Move (with std) %s' % (
        label, 'at 23E4:%04X' % p if p is not None else 'absent', 'at %04X' % o if o is not None else 'absent'))


g, _ = sysseg.system_code(sys.argv[1])
report('GOAL', g)
for p in sys.argv[2:]:
    c, _ = sysseg.system_code(p)
    report(p.rsplit('/', 1)[-1], c)
