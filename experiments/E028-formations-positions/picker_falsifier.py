"""Falsifier for picker_truth.py: compare its single-candidate table with WRONG rules: "expected foot = 1 when the role count of the
outgoing row exceeds 3" (the round-1 wording) and "no exemption for two-footed candidates"; both must differ from the original.
usage: python3 -B picker_falsifier.py picker-truth-<ts>.tsv"""
import sys
rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if not l.startswith("#")]
CNT = {3: 3, 4: 3, 7: 7, 8: 7, 10: 6, 11: 6}      # role counts of DS:099A rows (tables.py)
STR = [3, 7, 10, 4, 8, 11]                         # DS:08CE

def right(oc): return None if oc not in STR else (0 if STR.index(oc) < 3 else 1)
def count(oc): return None if oc not in STR else (1 if CNT[oc] > 3 else 0)

def accepts(exp_fn, exempt_two, r):
    exp = exp_fn(int(r[0])); two = int(r[4]); foot = int(r[5])
    return exp is None or (exempt_two and two) or foot == exp

for name, fn, ex in (("string-index (stated rule)", right, True), ("role-count (round 1)", count, True), ("no two-footed exemption", right, False)):
    d = sum(1 for r in rows if r[6] == "1" and (int(r[7]) != 0) != accepts(fn, ex, r))
    print("%-28s single-candidate rows differing from the original: %d" % (name, d))
