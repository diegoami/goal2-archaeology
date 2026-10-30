"""Scratch, T80b step 1: which known structure each 'elsewhere' input byte of the family read map lies in."""
import json, sys, collections
from pathlib import Path
sys.path[:0] = ['runtime', '.']
from original_match import Image
from original_match.assets import reference_image
from original_match import image as I
img = Image.from_savestate(reference_image(Path('.cache/dl')))
far = img.far
spans = {"players": (far(I.PLAYERS_PTR), I.PLAYER_SIZE * I.N_PLAYERS), "countries": (far(I.COUNTRIES_PTR), I.COUNTRY_SIZE * I.N_COUNTRIES),
         "managers": (far(I.MANAGERS_PTR), None), "fixtures": (far(I.FIXTURES_PTR), None), "game": (far(I.GAME_PTR), None)}
for k, ptr in (("text page", 0xA96A), ("text buffer 1", 0xA96E), ("text buffer 2", 0xA972)):
    spans[k] = (far(ptr), 4000)
spans["video B800"] = (0xB8000, 0x8000)
chunks = sorted(Path('experiments/E036-match-port/out/T80/a').glob('read-map-family-v1.chunk-*.json'))
addrs = set()
for c in chunks:
    for s, n in json.loads(c.read_text())['ranges']:
        addrs.update(range(s, s + n))
code0, ds0 = img.load * 16, img.DS * 16
else_ = sorted(x for x in addrs if not (code0 <= x < ds0 + 0x10000))
starts = sorted((b, name, n) for name, (b, n) in spans.items())
print({name: (hex(b), n) for name, (b, n) in spans.items()})
count = collections.Counter(); unknown = []
for x in else_:
    hit = None
    for b, name, n in starts:
        if n is not None and b <= x < b + n: hit = name; break
    if hit is None:
        # nearest structure below, for the open-ended ones
        below = [(b, name) for b, name, n in starts if b <= x]
        hit = f"after {below[-1][1]} (+{x - below[-1][0]:#x})" if below else "below all"
        unknown.append(x)
    count[hit.split(' (+')[0]] += 1
for k, v in count.most_common(): print(f"{v:6d}  {k}")
def ranges(a):
    out=[];s=p=None
    for x in a:
        if s is None: s=p=x
        elif x==p+1: p=x
        else: out.append((s,p-s+1)); s=p=x
    if s is not None: out.append((s,p-s+1))
    return out
r = ranges(unknown); print(len(r), "unattributed ranges, largest:", sorted(r, key=lambda t: -t[1])[:8])
# Which DS far pointers point into (or just below) the unattributed blocks.
mem = img.memory
ptrs = []
for off in range(0, 0x10000 - 3, 2):
    o = mem[ds0 + off] | mem[ds0 + off + 1] << 8; sg = mem[ds0 + off + 2] | mem[ds0 + off + 3] << 8
    lin = sg * 16 + o
    if 0x30000 <= lin < 0x60000: ptrs.append((lin, off))
ptrs.sort()
import bisect
owners = collections.Counter()
for s, n in r:
    i = bisect.bisect_right([p for p, _ in ptrs], s) - 1
    if i >= 0: owners[(hex(ptrs[i][0]), f"DS:{ptrs[i][1]:04X}")] += n
for (lin, ds), n in owners.most_common(14): print(f"{n:6d}  block at {lin} (pointer {ds})")
