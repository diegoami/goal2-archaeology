"""Falsifier for posts.py / posts_synthetic.py: the same comparison with the port deliberately wrong in one place each
(nothing tracked is edited; the wrong ports are defined here). Each variant must differ from the original 0791:419C on some
eleven, otherwise the comparison proves nothing.
usage: python3 -B posts_falsifier.py <GOAL.EXE>"""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foot_truth import load, Guest
from posts import emulate, port
from ds import load_full

def variant(name):
    def f(poss, ds):
        tab = [(((ds[0x79E + 2 * p] ^ 0x80) - 0x80), ((ds[0x79F + 2 * p] ^ 0x80) - 0x80)) for p in range(14)]
        posts = [list(tab[p]) for p in poss]
        for i in range(1, len(posts)):
            if tuple(posts[i - 1]) == tuple(tab[poss[i]]):
                x = posts[i][0]
                if abs(x) <= (3 if name == "threshold-3" else 4):
                    posts[i][0] += 3 if name != "plus-2" else 2
                    posts[i - 1][0] -= 3
                else:
                    posts[i][0] -= 3 * (1 if x > 0 else -1) * (-1 if name == "outer-sign" else 1)
                    posts[i - 1][1] -= 3 if name != "prev-y-0" else 0
        return [tuple(p) for p in posts]
    return f

psha, usha, image = load(sys.argv[1])
g = Guest(image); ds = load_full()
rnd = random.Random(54)
cases = []
for code in range(14):
    for k in (2, 3):
        cases.append(sorted([code] * k + [rnd.randrange(14) for _ in range(11 - k)]))
for _ in range(300):
    cases.append(sorted(rnd.randrange(14) for _ in range(11)))
for name in ("honest", "plus-2", "outer-sign", "prev-y-0", "threshold-3"):
    fn = port if name == "honest" else variant(name)
    bad = 0
    for poss in cases:
        a, b = emulate(g, poss, poss)
        if a != fn(poss, ds):
            bad += 1
    print("%-12s elevens %d differ from the original: %d" % (name, len(cases), bad))
