"""Exact distribution of the group a pot's team lands in after the stage-2/5 draw's weak shuffle (F023).

python3 -B experiments/E023-competitions-structure/shuffle.py > experiments/E023-competitions-structure/shuffle.txt

1771:6730 (seg_1771_09.asm:1168-1210, 6804-6855): for each of the 16 blocks of 8 bytes of the order table
(DS:9D00..9D7F: continent c, pot a = 8 ranked teams), 4 times: swap the bytes at two positions r1, r2, each
drawn by 214B:06B1 (1..8). Position p of the block then becomes group g = p. Assumes 214B:06B1 is uniform on 1..n.
Also the slot a pot takes inside its group: a random row of the permutations at DS:0F76 (tables.txt).
"""
from fractions import Fraction
from itertools import product

N = 8
SWAPS = 4
# state: tuple, position -> the original position of the team now there; follow exact probabilities
dist = {tuple(range(N)): Fraction(1)}
for _ in range(SWAPS):
    new = {}
    for state, p in dist.items():
        for r1, r2 in product(range(N), repeat=2):
            s = list(state)
            s[r1], s[r2] = s[r2], s[r1]
            t = tuple(s)
            new[t] = new.get(t, 0) + p / (N * N)
    dist = new

print('P(team of pot position i ends in group j) after %d swaps of two uniform positions (rows i = 1..8 by rank in the pot)' % SWAPS)
mat = [[Fraction(0)] * N for _ in range(N)]
for state, p in dist.items():
    for pos, orig in enumerate(state):
        mat[orig][pos] += p
for i in range(N):
    print('rank %d in pot:' % (i + 1), ' '.join('%.3f' % float(x) for x in mat[i]))
print('P(stays) =', float(mat[0][0]), '= (1/8) + (7/8)(3/4)^4 =', 1 / 8 + 7 / 8 * 0.75 ** 4, '; a uniform draw would give 0.125')
perm = [(1, 2, 3, 4), (2, 3, 4, 1), (3, 4, 2, 1), (4, 1, 2, 3)]
print('\nslot taken inside the group by the pot-a team (random row of DS:0F76 rows):')
for a in range(4):
    cnt = {}
    for row in perm:
        cnt[row[a]] = cnt.get(row[a], 0) + 1
    print('pot %d: ' % (a + 1), {s: '%d/4' % n for s, n in sorted(cnt.items())})
