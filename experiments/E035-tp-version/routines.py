#!/usr/bin/env python3
"""Per routine of GOAL's System segment (the project's 88 routines at 23E4, named in
static/goal-exe/annotations/routines.tsv): the share of its instructions (skeleton, immediates masked)
that each candidate's System segment reproduces in blocks >= 4 instructions. TSV on stdout.
usage: routines.py GOAL.unp.exe REPO_ROOT CAND.EXE ...   (candidate label = its parent directory)"""
import sys, difflib
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import sysseg

goal, repo, cands = sys.argv[1], sys.argv[2], sys.argv[3:]
g, _ = sysseg.system_code(goal)
gs = sysseg.skel(g, 0)
ga = [s for _, _, s, _ in gs]
rt = []
for l in open(repo + '/static/goal-exe/routines.tsv'):
    f = l.split('\t')
    if f[0].startswith('23E4:'):
        rt.append((int(f[0][5:], 16), int(f[1])))
names = {}
for l in open(repo + '/static/goal-exe/annotations/routines.tsv'):
    f = l.split('\t')
    names[f[0]] = f[1]
cov = {}
for c in cands:
    cd, _ = sysseg.system_code(c)
    cs = sysseg.skel(cd, 0)
    sm = difflib.SequenceMatcher(None, ga, [s for _, _, s, _ in cs], autojunk=False)
    m = [False] * len(ga)
    for b in sm.get_matching_blocks():
        if b.size >= 4:
            for k in range(b.size):
                m[b.a + k] = True
    cov[c] = m
labels = [c.rsplit('/', 2)[1] for c in cands]
print('routine\tname\tbytes\tinstr\t' + '\t'.join('match_%s_pct' % x for x in labels))
for off, size in rt:
    idx = [i for i, (p, _, _, _) in enumerate(gs) if off <= p < off + size]
    if not idx:
        continue
    row = [('%.0f' % (100.0 * sum(cov[c][i] for i in idx) / len(idx))) for c in cands]
    print('23E4:%04X\t%s\t%d\t%d\t%s' % (off, names.get('23E4:%04X' % off, ''), size, len(idx), '\t'.join(row)))
