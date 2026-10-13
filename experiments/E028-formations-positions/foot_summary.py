"""Summarise a foot-truth TSV (foot_truth.py output): what 3179 returned, by foot index and position.
usage: python3 -B foot_summary.py TSV [--swap-sets]   (--swap-sets: falsifier, compare with the left and right sets exchanged)"""
import sys
from collections import Counter, defaultdict
path = sys.argv[1]
rows = [l.rstrip("\n").split("\t") for l in open(path) if not l.startswith("#")][1:]
rows = [tuple(map(int, r)) for r in rows]
swap = "--swap-sets" in sys.argv
left, right = ({4, 8, 11}, {3, 7, 10}) if swap else ({3, 7, 10}, {4, 8, 11})
def rule(pos, club, foot, two):
    if not two and foot != 0 and pos in left: return 1
    if foot == 0 and pos in right: return 1
    if pos == 0 and club != 0: return 1
    if club == 0 and pos != 0: return 1
    return 0
mm = sum(1 for n, m3, pos, club, flag, two, foot, orig, _ in rows if orig != rule(pos, club, foot, two))
print("rows", len(rows), "mismatches vs rule%s: %d" % (" (sets swapped)" if swap else "", mm))
print("is_two_footed true rows:", sum(r[5] for r in rows), "of", len(rows), "; foot_index values:", dict(Counter(r[6] for r in rows)))
print("3179 = 1 rows:", sum(r[7] for r in rows))
# foot index by (n mod 3, club position)
tab = defaultdict(dict)
for n, m3, pos, club, flag, two, foot, orig, _ in rows:
    tab[m3][club] = foot
for m3 in range(3):
    print("foot_index n mod 3 = %d, club 0..13:" % m3, [tab[m3][c] for c in range(14)])
# 3179 by played position and foot for a same-position player (club = played), not two-footed
for foot in (0, 1):
    res = {}
    for n, m3, pos, club, flag, two, f, orig, _ in rows:
        if club == pos and flag == 0 and f == foot:
            res.setdefault(pos, set()).add(orig)
    print("same club = played, one-footed, foot_index %d: positions with 3179 = 1:" % foot, sorted(p for p, v in res.items() if 1 in v), "; foot index never reached for positions", sorted(set(range(14)) - set(res)))
# two-footed players
res = {}
for n, m3, pos, club, flag, two, f, orig, _ in rows:
    if club == pos and two == 1:
        res.setdefault((f, pos), set()).add(orig)
print("two-footed (is_two_footed true), club = played: (foot_index, pos) with 3179 = 1:", sorted(k for k, v in res.items() if 1 in v))
res = {}
for n, m3, pos, club, flag, two, f, orig, _ in rows:
    if pos == club:
        res.setdefault(club, set()).add(orig)
# goalkeeper mismatch
gk = Counter((pos == 0, club == 0, orig) for n, m3, pos, club, flag, two, f, orig, _ in rows if (pos == 0) != (club == 0))
print("exactly one of played/club is goalkeeper: (played_gk, club_gk, 3179):", dict(gk))
