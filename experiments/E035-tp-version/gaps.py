#!/usr/bin/env python3
"""List the stretches of GOAL's System segment that the candidate's System segment does not reproduce
(skeleton blocks >= 4 instructions): offset, length, sha256 and the masked mnemonics of each stretch, no bytes.
usage: gaps.py GOAL.unp.exe CAND.EXE"""
import sys, struct, difflib, hashlib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg
system_code = sysseg.system_code

gcode, _ = system_code(sys.argv[1])
ccode, _ = system_code(sys.argv[2])
gs = sysseg.skel(gcode, 0)
cs = sysseg.skel(ccode, 0)
ga = [s for _, _, s, _ in gs]
ca = [s for _, _, s, _ in cs]
sm = difflib.SequenceMatcher(None, ga, ca, autojunk=False)
cov = [False] * len(ga)
for b in sm.get_matching_blocks():
    if b.size >= 4:
        for k in range(b.size):
            cov[b.a + k] = True
i = 0
while i < len(ga):
    if not cov[i]:
        j = i
        while j < len(ga) and not cov[j]:
            j += 1
        lo, hi = gs[i][0], gs[j - 1][0] + gs[j - 1][1]
        # offset, length and sha256 of the stretch; the mnemonic skeleton, never the bytes (rule 18)
        print('--- GOAL 23E4:%04X..%04X (%d instr, %d bytes, sha256 %s)' % (lo, hi, j - i, hi - lo, hashlib.sha256(gcode[lo:hi]).hexdigest()))
        for k in range(i, min(j, i + 40)):
            print('   %04X %s' % (gs[k][0], gs[k][2]))
        if j - i > 40:
            print('   ... %d more instructions' % (j - i - 40))
        i = j
    else:
        i += 1
