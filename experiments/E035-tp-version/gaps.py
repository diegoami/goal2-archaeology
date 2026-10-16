#!/usr/bin/env python3
"""List the stretches of GOAL's System segment that the candidate's System segment does not reproduce
(skeleton blocks >= 4 instructions), with the GOAL bytes and the candidate's nearest instructions.
usage: gaps.py GOAL.unp.exe CAND.EXE"""
import sys, struct, difflib
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
        print('--- GOAL 23E4:%04X..%04X (%d instr)' % (gs[i][0], gs[j - 1][0] + gs[j - 1][1], j - i))
        for k in range(i, min(j, i + 40)):
            print('   %04X %-24s %s' % (gs[k][0], gs[k][3].hex(), gs[k][2]))
        i = j
    else:
        i += 1
