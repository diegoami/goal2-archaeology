#!/usr/bin/env python3
"""Byte-level view of the skeleton match: of the GOAL System instructions matched (blocks >= 4) by a
candidate, how many have identical bytes, and what the differing ones look like (only operands that
are DS offsets of System variables, which move with the data layout, should differ).
usage: bytecmp.py GOAL.unp.exe CAND.EXE"""
import sys, difflib, collections
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

g, _ = sysseg.system_code(sys.argv[1])
c, _ = sysseg.system_code(sys.argv[2])
gs, cs = sysseg.skel(g, 0), sysseg.skel(c, 0)
sm = difflib.SequenceMatcher(None, [s for _, _, s, _ in gs], [s for _, _, s, _ in cs], autojunk=False)
same = diff = 0
kinds = collections.Counter()
ex = {}
for b in sm.get_matching_blocks():
    if b.size < 4:
        continue
    for k in range(b.size):
        gb, cb = gs[b.a + k][3], cs[b.b + k][3]
        if gb == cb:
            same += 1
        else:
            diff += 1
            # which bytes differ: opcode/modrm byte(s) vs the 16-bit operand tail
            dpos = [i for i in range(len(gb)) if gb[i] != cb[i]]
            key = (gs[b.a + k][2].split(' ')[0], 'opcode-differs' if dpos and dpos[0] < len(gb) - 2 else 'operand-only')
            kinds[key] += 1
            ex.setdefault(key, (gb.hex(), cb.hex()))
print('matched instructions: %d identical bytes, %d differing' % (same, diff))
n_opdiff = sum(v for (m, t), v in kinds.items() if t == 'opcode-differs')
print('differing instructions where a byte other than the trailing 16-bit operand differs: %d' % n_opdiff)
for key, v in kinds.most_common(8):
    print('  ', key, v, 'e.g. GOAL %s vs cand %s' % ex[key])
