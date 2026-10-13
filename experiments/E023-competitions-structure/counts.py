"""Count the fixtures each stage builder writes, by re-running the builders' loops over the data-image tables.

python3 -B experiments/E023-competitions-structure/counts.py > experiments/E023-competitions-structure/counts.txt

This is arithmetic over the listing (loops and tables transcribed from 1771:6730, 6B55, 6E59, 7090, 71B2, 74BE as
cited in findings/F023), not a run of GOAL.EXE. A team is identified by its slot (table, continent, group, slot) or by
its position in the 128-byte order table; the draw (which country takes which slot) does not change a count.
"""
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsbytes

mem = dsbytes.load()


def b(a):
    return mem[a]


T1087 = lambda g, e: b(0x1087 + 6 * g + e)           # 6730/6B55: friendlies partner group
SCHED = lambda k, r: (b(0xF54 + 0x18 * k + 2 * r), b(0xF54 + 0x18 * k + 2 * r + 1))   # 6730 pair of round r
RR = lambda m: (b(0x10BC + 2 * m), b(0x10BD + 2 * m))   # 6B55/71B2 single round robin pairs (m = 1..6)

fixtures = []  # (stage, kind, group, teamA, teamB)


def add(stage, kind, group, a, b_):
    fixtures.append((stage, kind, group, a, b_))


# ---- stage 2 and 5 (1771:6730), class 0 / 1: loops e=1..12, c=1..4, g=1..8
for stage, cls, limit in ((2, 0, b(0x1107)), (5, 1, b(0x1106))):
    for e in range(1, 13):
        for c in range(1, 5):
            for g in range(1, 9):
                t = T1087(g, e)
                if e < limit and t:
                    for a in range(1, 5):
                        add(stage, 1, 0, ('A%d' % cls, c, t, a), ('A%d' % cls, c, g, a))
                pa, pb = SCHED(g + c, e)
                add(stage, stage, g, ('A%d' % cls, c, g, pa), ('A%d' % cls, c, g, pb))

# ---- stage 3 (1771:6B55): B table (class 0), e=1..12, c=1..4, g=1..8
for e in range(1, 13):
    for c in range(1, 5):
        for g in range(1, 9):
            t = T1087(g, e)
            if e < 7 and t:
                for a in range(1, 5):
                    add(3, 1, 0, ('B0', c, t, a), ('B0', c, g, a))
            if e > 6:
                pa, pb = RR(e - 6)
                kind, grp = (3, g) if g < 3 else (1, 0)
                add(3, kind, grp, ('B0', c, g, pa), ('B0', c, g, pb))

# ---- stage 4 (1771:6E59): +0x3D = 2 semi-finals, then +0x3D = 1 third place and final, per continent
for c in range(1, 5):
    add(4, 0x65, 0, ('B0', c, 2, 2), ('B0', c, 1, 1))
    add(4, 0x65, 0, ('B0', c, 1, 2), ('B0', c, 2, 1))
    add(4, 0x66, 0, 'loser SF2', 'loser SF1')
    add(4, 0x67, 0, 'winner SF2', 'winner SF1')

# ---- stage 6 (1771:7090): play-off, continents 3 and 4, g=1..4, two legs of winner(9-g) v winner(g)
for c in (3, 4):
    for g in range(1, 5):
        add(6, 6, 0, ('A1', c, 9 - g, 1), ('A1', c, g, 1))
        add(6, 6, 0, ('A1', c, g, 1), ('A1', c, 9 - g, 1))

# ---- stage 7 (1771:71B2): friendlies on the 128-byte order table, then 6 rounds x 8 groups
for c in range(1, 5):                     # local_4
    for g in range(1, 5):                 # local_8
        for i in range(1, 17):            # local_c
            posA = (g - 1) * 32 + 2 * i - 1
            tcont = b(0x10C6 + 4 * g + (i % 4))
            posB = (tcont - 1) * 32 + b(0x10D5 + 4 * ((i + 1) // 2) + c)
            add(7, 1, 0, ('O', posA), ('O', posB))
for i in range(1, 65):
    add(7, 1, 0, ('O', 2 * i), ('O', 2 * i - 1))
for m in range(1, 7):
    for g in range(1, 9):
        pa, pb = RR(m)
        add(7, 7, g, ('F7', g, pa), ('F7', g, pb))

# ---- stage 8 (1771:74BE): last 16, quarter-finals, semi-finals, third place and final
for i in range(1, 9):
    add(8, 8, 0, ('W', 'runner-up', 9 - i), ('W', 'winner', i))
for i in range(1, 5):
    add(8, 200, 0, 'winner L16', 'winner L16')
for i in range(1, 3):
    add(8, 0xC9, 0, 'winner QF', 'winner QF')
add(8, 0xCA, 0, 'loser SF', 'loser SF')
add(8, 0xCB, 0, 'winner SF', 'winner SF')

print('== fixtures written per stage and kind (one build of each stage; the sum per class is checked against DS:6936)')
per = Counter((f[0], f[1]) for f in fixtures)
for (stage, kind), n in sorted(per.items()):
    print('stage %d kind %3d : %4d' % (stage, kind, n))
cls0 = sum(1 for f in fixtures if f[0] in (2, 3, 4))
cls1 = sum(1 for f in fixtures if f[0] in (5, 6, 7, 8))
first1 = b(0x6936 + 2) + 256 * b(0x6937 + 2)
print('class 0 (stages 2,3,4): %d fixtures; numbering 1..%d (DS:6936 class 1 starts at %d)' % (cls0, first1 - 1, first1))
print('class 1 (stages 5..8) : %d fixtures; numbers %d..%d; aggregate records follow at 0x961..0x968 (=2401..2408)' % (cls1, first1, first1 + cls1 - 1))
print('class 0 fills its block exactly:', cls0 == first1 - 1, '; class 1 ends at 2400:', first1 + cls1 - 1 == 2400)

print('\n== fixtures per team per stage (slots), and the 12-entry window of 1771:82BD (list entries 25..36)')
for stage in (2, 3, 5, 7):
    cnt = defaultdict(int)
    for f in fixtures:
        if f[0] != stage:
            continue
        for t in (f[3], f[4]):
            cnt[t] += 1
    if stage == 7:      # order-table positions (all 128 countries, friendlies) and the 32 finalists' group slots
        for tag in ('O', 'F7'):
            vals = [v for k, v in cnt.items() if k[0] == tag]
            print('stage 7 %s: %d teams, fixtures per team min %d max %d' % (tag, len(vals), min(vals), max(vals)))
        print('stage 7: a finalist plays its 3 group matches plus the friendlies of its order position (max total %d)' % (3 + max(v for k, v in cnt.items() if k[0] == 'O')))
        continue
    vals = list(cnt.values())
    print('stage %d: teams counted %d, fixtures per team min %d max %d' % (stage, len(vals), min(vals), max(vals)))
