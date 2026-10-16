#!/usr/bin/env python3
"""The start-up routine of the System segment (first 0xA0 bytes) and its table of saved interrupt vectors, GOAL against
candidates: skeleton similarity, the first differing instructions (masked mnemonics), and the vector table
(entry count; entries a candidate saves that GOAL does not, and the reverse).
usage: startup.py GOAL.unp.exe CAND.EXE ..."""
import sys, difflib, struct
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

N = 0xA0


def table(code):
    """(offset, entries) of the lodsb-driven vector table read by the start-up loop:
    mov si, TABLE; mov cx, COUNT; nop; cld; lodsb al, byte ptr cs:[si]."""
    sk = sysseg.skel(code[:N], 0)
    for k in range(len(sk) - 4):
        if sk[k][2].startswith('mov si, N') and sk[k + 1][2].startswith('mov cx, N') and sk[k + 4][2].startswith('lodsb'):
            off = struct.unpack_from('<H', sk[k][3], 1)[0]
            cnt = struct.unpack_from('<H', sk[k + 1][3], 1)[0]
            return off, list(code[off:off + cnt])
    return None, None


g, _ = sysseg.system_code(sys.argv[1])
gsk = sysseg.skel(g[:N], 0)
goff, gtab = table(g)
print('GOAL: start-up %d instructions in the first 0x%X bytes; vector table of %d entries' % (len(gsk), N, len(gtab)))
for p in sys.argv[2:]:
    c, _ = sysseg.system_code(p)
    csk = sysseg.skel(c[:N], 0)
    a, b = [s for _, _, s, _ in gsk], [s for _, _, s, _ in csk]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    off, tab = table(c)
    label = p.rsplit('/', 2)[1]
    print('%s: skeleton similarity %.3f; vector table %s entries; identical to GOAL: %s; saved by it and not by GOAL: %s; by GOAL and not by it: %s' % (
        label, sm.ratio(), len(tab) if tab else '?', tab == gtab,
        ['%02X' % x for x in sorted(set(tab or []) - set(gtab))], ['%02X' % x for x in sorted(set(gtab) - set(tab or []))]))
    if sm.ratio() < 1:
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                print('    %s GOAL[%s] -> cand[%s]' % (tag, '; '.join(a[i1:i2][:4]), '; '.join(b[j1:j2][:4])))
