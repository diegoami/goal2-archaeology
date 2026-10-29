"""Scratch, T80b step 1: which port routine reads each heap input byte outside the players, countries and text page."""
import sys, json, collections, importlib.util
from pathlib import Path
sys.path[:0] = ['.', 'runtime']
from original_match import Image, Match, Fixture
from original_match import image as I
from original_match.assets import reference_image
from original_match.machine import MEM_SIZE
from original_match.port.engine import PortMachine
spec = importlib.util.spec_from_file_location('b', 'experiments/E033-original-match-kit/save_boundaries.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
img = Image.from_savestate(reference_image(Path('.cache/dl')))
far = img.far
known = [(far(I.PLAYERS_PTR), I.PLAYER_SIZE * I.N_PLAYERS), (far(I.COUNTRIES_PTR), I.COUNTRY_SIZE * I.N_COUNTRIES), (0xB8000, 0x8000)]
code0, ds_end = img.load * 16, img.DS * 16 + 0x10000
def interesting(x): return not (code0 <= x < ds_end) and not any(b <= x < b + n for b, n in known)
written = bytearray(MEM_SIZE); stack = []; who = collections.defaultdict(collections.Counter); st = {'w': 0, 'm': None}
bounds, write_as, dispatch = PortMachine._bounds, PortMachine.write_as, PortMachine._dispatch
def tb(linear, n):
    bounds(linear, n)
    m = st['m']
    if st['w'] or m is None or not m.running or n > 0x1000: return
    for i in range(linear, linear + n):
        if not written[i] and interesting(i): who[i][stack[-1] if stack else None] += 1
def tw(self, linear, size, value, at):
    st['w'] += 1
    try: return write_as(self, linear, size, value, at)
    finally:
        st['w'] -= 1
        for i in range(linear, linear + size): written[i] = 1
def td(self, linear):
    stack.append(linear)
    try: return dispatch(self, linear)
    finally: stack.pop()
PortMachine._bounds = staticmethod(tb); PortMachine.write_as = tw; PortMachine._dispatch = td
m = Match(img, Fixture(7, 19, index=9, kind=200), managed=7, substitutions=None, engine='port', record_draws=True)
st['m'] = m.m
def policy(match, d): match.answer(quick=True) if d['context'] == 'half_time' else match.answer()
h.drive(m, policy, ())
names = {}
for linear in {l for c in who.values() for l in c}:
    if linear is None: continue
    seg = (linear - code0) // 16; names[linear] = m.m.where(linear >> 4, linear & 15) if hasattr(m.m, 'where') else hex(linear)
blocks = collections.defaultdict(collections.Counter)
def ranges(a):
    out=[];s=p=None
    for x in a:
        if s is None: s=p=x
        elif x<=p+16: p=x
        else: out.append((s,p)); s=p=x
    if s is not None: out.append((s,p))
    return out
for s, e in ranges(sorted(who)):
    for x in range(s, e + 1):
        for l, n in who.get(x, {}).items(): blocks[(s, e)][l] += n
for (s, e), c in sorted(blocks.items(), key=lambda kv: -(kv[0][1] - kv[0][0]))[:20]:
    top = [(hex(l - code0) if l else None, n) for l, n in c.most_common(3)]
    print(f"{s:#07x}-{e:#07x} ({e - s + 1:5d} B): read by image offsets {top}")
