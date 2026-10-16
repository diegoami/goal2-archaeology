#!/usr/bin/env python3
"""Crt (2382) and Dos (235C) units of GOAL against everything before the System segment of each candidate
(the main program, Crt, Dos), by instruction skeleton.  usage: units.py GOAL.unp.exe CAND.EXE ..."""
import sys, difflib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

gimg, gseg, _, _ = sysseg.load(sys.argv[1])
cs_ = []
for p in sys.argv[2:]:
    img, seg, _, _ = sysseg.load(p)
    cs_.append((p.rsplit('/', 2)[1], [s for _, _, s, _ in sysseg.skel(img[:seg * 16], 0)]))
for name, a, b in (('Dos 235C', 0x235C0, 0x23820), ('Crt 2382', 0x23820, 0x23E40)):
    ga = [s for _, _, s, _ in sysseg.skel(gimg[a:b], 0)]
    out = []
    for v, ca in cs_:
        sm = difflib.SequenceMatcher(None, ga, ca, autojunk=False)
        m = sum(x.size for x in sm.get_matching_blocks() if x.size >= 4)
        out.append('%s:%.0f%%' % (v, 100.0 * m / len(ga)))
    print(name, len(ga), 'items matched;', ' '.join(out))
