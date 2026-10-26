"""#432: shared original-code harness for the TEAM panel probes (T114, T115, T116).

Genuine inputs only come by hash: cached E006/E010/E011 savestates whose run
records list them, and the E015-r0007 owner-sitting snapshots whose manifest
lists them and whose run record holds the digest of the DOSBox screen captured
with each. Original routines run unmodified under Unicorn (notes/429/probe.py's
Original: synthetic call frames, no behaviour hooks, 2 s / 500000 instructions
per call). Nothing here writes original bytes anywhere but the private guest.
"""
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT/'runtime'), str(ROOT/'runtime/driver')]
_spec = importlib.util.spec_from_file_location('manager_probe', ROOT/'notes/429/probe.py')
helper = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(helper)
Image, Original, glyphs, unicorn = helper.Image, helper.Original, helper.glyphs, helper.unicorn
from savestate import Savestate  # noqa: E402

CACHE = ROOT/'.cache/dl'
SCREEN = 0x7A000   # scratch back buffer for original renders (as T94)
CACHED = [('E006-r0001', 'e0afff6751747233-e006-1000-r0001.sav')] + \
    [(f'E010-r{n:04d}', None) for n in range(1, 11)] + \
    [('E011-r0001', 'd68e48c734a742a6-E011-r0001-watchstart.sav'),
     ('E011-r0001', '092f5f74bc5dc0c0-E011-r0001-halftime.sav')]
SITTING = 'E015-r0007'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _record(run):
    return json.loads((ROOT/'runs'/run.split('-')[0]/(run+'.json')).read_text())


def cached_states():
    """(label, raw) of each cached genuine state, its sha256 checked against its run record."""
    out = []
    for run, name in CACHED:
        if name is None:
            name = next(p.name for p in CACHE.glob(f'*-{run}-halftime.sav'))
        raw = (CACHE/name).read_bytes()
        assert sha(raw) in [o.get('sha256') for o in _record(run)['outputs']], name
        out.append((f'{run}:{name.split("-", 1)[1]}', raw))
    return out


def sitting_screens():
    """E015-r0007's TEAM screens: (label, raw, screen) with manifest hash and capture digest checked."""
    manifest = {f['name']: f for f in json.loads(
        (ROOT/f'evidence/E015/{SITTING}.manifest.json').read_text())['files']}
    out = []
    for o in _record(SITTING)['observations']:
        v = o.get('value')
        if not (isinstance(v, str) and '├skills──' in v and ' status ' in v):
            continue
        name = re.search(r'snapshots/(snap-[^)\s]*\.sav)', o['field']).group(1)
        digest = re.search(r'digest ([0-9a-f]{64})', o['field']).group(1)
        f = manifest[name]
        raw = (CACHE/f['asset']).read_bytes()
        assert sha(raw) == f['sha256'], name
        screen = Savestate(raw).screen()
        assert screen.digest() == digest, name
        out.append((f'{SITTING}:{name}', raw, screen))
    return out


class Machine:
    """One genuine state in Unicorn, with the read callbacks the decoders take."""
    def __init__(self, raw):
        image = Image.from_savestate(raw)
        assert not helper.build_problems(image.memory, image.load)
        self.original = Original(image)
        g = self.g = self.original.g
        self.read_ds = lambda off, n: g.mem(g.DS*16+off, n)
        self.read_code = lambda seg, off, n: g.mem(g.seg(seg)*16+off, n)
        self.read_player = lambda w: g.mem(g.far(0xA91B)+20*w, 20)
        self.read_country = lambda c: g.mem(g.far(0xA917)+191*c, 191)
        self.read_manager = lambda m: g.mem(g.far(0xA91F)+3*m, 3)

    def ds_word(self, off):
        return int.from_bytes(self.read_ds(off, 2), 'little')

    def put_ds(self, off, raw):
        self.g.put(self.g.DS*16+off, raw)

    def put_player(self, word, offset, raw):
        self.g.put(self.g.far(0xA91B)+20*word+offset, raw)

    def put_country(self, c, offset, raw):
        self.g.put(self.g.far(0xA917)+191*c+offset, raw)

    def put_manager(self, m, offset, raw):
        self.g.put(self.g.far(0xA91F)+3*m+offset, raw)

    def name(self, c):
        record = self.g.mem(self.g.far(0x9B68)+16*c, 16)
        return glyphs(record[1:1+record[0]])

    def panel(self, country):
        """Run the unmodified 157D(country) into a blank scratch buffer; (chars, attrs) of 80x25."""
        g = self.g
        g.put(g.DS*16+0xA96E, b'\0\0'+(SCREEN >> 4).to_bytes(2, 'little'))
        g.put(SCREEN, b'\x20\x07'*2000)
        self.original.call('1771:157D', [country], far=False, pop=2)
        raw = g.mem(SCREEN, 4000)
        return raw[::2], raw[1::2]


def screen_country(machine, chars):
    """The country whose name 0F58 drew at row 8, column 2 (15 dashes, then the name)."""
    row = glyphs(chars[80*7+1:80*7+16])
    found = [c for c in range(1, 129) if (machine.name(c)+'-'*15)[:15] == row]
    assert len(found) == 1, row
    return found[0]


def stale_rows(screen, chars, attrs):
    """Rows 8..24 where the genuine screen's left panel (columns 1..34) differs from an original
    re-render of the same memory. Nonempty means the screen predates the memory (it was drawn
    before a later state change); the right column's tactic cursor (1981) is not compared."""
    return [r for r in range(8, 25) if screen.chars[80*(r-1):80*(r-1)+34] != chars[80*(r-1):80*(r-1)+34]
            or screen.attrs[80*(r-1):80*(r-1)+34] != attrs[80*(r-1):80*(r-1)+34]]


def highlight(attrs, row, column, n):
    """The cells of a row from column (1-based) that carry attribute 0x70, as a 0/1 string."""
    start = 80*(row-1)+column-1
    return ''.join('1' if a == 0x70 else '0' for a in attrs[start:start+n])


def expected(cells, n):
    return '1'*cells+'0'*(n-cells)


def receipt_base(producer):
    import subprocess
    return dict(source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                producer_sha256=sha(Path(producer).read_bytes()),
                harness_sha256=sha(Path(__file__).read_bytes()),
                helper_sha256=sha((ROOT/'notes/429/probe.py').read_bytes()),
                unicorn=unicorn.__version__,
                bound_per_call='2seconds/500000instructions')
