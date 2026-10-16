#!/usr/bin/env python3
"""Compare the part of GOAL's image that holds the small library units (image 21380..23E3F: segments
2138, 2139, 214B, 235C, 2382) with everything of a candidate EXE before its System segment (the
main program and the units it uses, here Crt and Dos), by instruction skeleton.
usage: unitcmp.py GOAL.unp.exe CAND.EXE ..."""
import sys, difflib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

gimg, gseg, _, _ = sysseg.load(sys.argv[1])
region = gimg[0x21380:gseg * 16]
gs = sysseg.skel(region, 0)
ga = [s for _, _, s, _ in gs]
print('GOAL region 21380..%X: %d bytes, %d items' % (gseg * 16, len(region), len(ga)))
for p in sys.argv[2:]:
    img, seg, _, _ = sysseg.load(p)
    pre = img[:seg * 16]
    cs = sysseg.skel(pre, 0)
    ca = [s for _, _, s, _ in cs]
    sm = difflib.SequenceMatcher(None, ga, ca, autojunk=False)
    bl = [b for b in sm.get_matching_blocks() if b.size >= 6]
    m = sum(b.size for b in bl)
    print('%s: GOAL region items matched (blocks>=6): %d of %d (%.1f%%)  [cand pre-System %d bytes]' % (
        p.rsplit('/', 2)[-2], m, len(ga), 100.0 * m / len(ga), len(pre)))
