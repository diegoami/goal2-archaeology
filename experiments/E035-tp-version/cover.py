#!/usr/bin/env python3
"""How much of GOAL's System-unit code segment (23E4) is reproduced, instruction by instruction with
immediates/offsets masked, by the System segment of a Turbo Pascal EXE.
usage: cover.py GOAL.unp.exe CAND.EXE [CAND.EXE ...]   (needs capstone)
The unpacked GOAL.EXE and the candidate EXEs are read and never written; nothing is committed."""
import sys, struct, difflib, hashlib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg


def system_code(path):
    img, seg, off, d = sysseg.load(path)
    base = seg * 16
    code = img[base:base + 0x2400]
    dsg = struct.unpack_from('<H', code, 1)[0]
    return img[base:dsg * 16], d


gcode, gd = system_code(sys.argv[1])
gs = sysseg.skel(gcode, 0)
print('GOAL system segment: %d bytes, %d decoded items, sha256 %s' % (len(gcode), len(gs), hashlib.sha256(gcode).hexdigest()[:16]))
ga = [s for _, _, s, _ in gs]
for p in sys.argv[2:]:
    ccode, cd = system_code(p)
    cs = sysseg.skel(ccode, 0)
    ca = [s for _, _, s, _ in cs]
    sm = difflib.SequenceMatcher(None, ga, ca, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size >= 4]
    gm = sum(b.size for b in blocks)
    # bytes of GOAL covered by blocks of >= 4 instructions
    gb = sum(sum(gs[b.a + k][1] for k in range(b.size)) for b in blocks)
    print('%s: system %d bytes; GOAL instr matched in blocks>=4: %d of %d (%.1f%%), %d of %d bytes (%.1f%%)' % (
        p.rsplit('/', 2)[-2] + '/' + p.rsplit('/', 1)[-1], len(ccode), gm, len(ga), 100.0 * gm / len(ga), gb, len(gcode), 100.0 * gb / len(gcode)))
