"""T93: bounded unmodified formatter and screen-writer execution; no original bytes exported."""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'runtime'))
from original_match.image import Image, build_problems
from emul.watched_match import Guest
from decoders.manager import manager_payload, manager_text
import unicorn

BASE = ROOT / '.cache/dl/e1dee7e2f5ad443e-E010-r0001-halftime.sav'
BASE_SHA = 'e1dee7e2f5ad443e'  # full hash verified against the immutable run record below
LOW = '☺☻♥♦♣♠•◘○◙♂♀♪♫☼►◄↕‼¶§▬↨↑↓→←∟↔▲▼'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def glyphs(payload):
    return ''.join(' ' if b == 0 else LOW[b-1] if b < 32 else '⌂' if b == 127
                   else bytes([b]).decode('cp437') for b in payload)


class Original:
    """Isolated source-derived call frames. No behavior hooks or instruction edits."""
    def __init__(self, image):
        self.g = Guest(memory=bytes(image.memory[:0x110000]), load=image.load)
        self.g.set_reg('ds', image.DS)
        self.g.set_reg('es', image.DS)
        self.g.set_reg('ss', 0x7000)
        self.g.set_reg('eflags', 0x202)

    def call(self, address, args, far=True, pop=None):
        g = self.g
        seg, off = (int(v, 16) for v in address.split(':'))
        sentinel = 0xFFF0
        frame = [sentinel] + ([g.seg(seg)] if far else []) + list(args)
        g.put(0x77000, b''.join(w.to_bytes(2, 'little') for w in frame))
        g.set_reg('sp', 0x7000)
        g.set_reg('bp', 0)
        g.set_reg('cs', g.seg(seg))
        g.set_reg('ip', off)
        g.mu.emu_start(g.lin(address), g.seg(seg)*16+sentinel, timeout=2_000_000, count=500_000)
        assert (g.reg('cs'), g.reg('ip')) == (g.seg(seg), sentinel), address
        if pop is not None:
            assert g.reg('sp') == 0x7000 + 2 + 2*far + pop, (address, g.reg('sp'))

    def name(self, manager):
        g = self.g
        # 0947 retf 2 leaves the hidden far result pointer to its caller.
        g.put(0x78000, b'\xA5'*16)
        self.call('1771:0947', [manager, 0, 0x7800], pop=2)
        length = g.mem(0x78000, 1)[0]
        assert length <= 14
        return g.mem(0x78001, length)

    def render(self, payload):
        g = self.g
        g.put(0x78000, bytes([len(payload)]) + payload)
        g.put(0x7A000, b'\xA5'*160)
        # Target 7A000; row1, column1 => no offset. Indirect screen pointer at79000.
        g.put(0x79000, (0xA000).to_bytes(2, 'little') + (0x7000).to_bytes(2, 'little'))
        self.call('214B:026D', [0, 0x7900, 1, 1, 0, 0x7800], pop=12)
        cells = g.mem(0x7A000, 2*len(payload))
        assert cells[::2] == payload
        assert g.mem(0x7A000+2*len(payload), 1) == b'\xA5'
        return glyphs(cells[::2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists():
        raise SystemExit('immutable output already exists')
    data = BASE.read_bytes()
    record = json.loads((ROOT/'runs/E010/E010-r0001.json').read_text())
    expected = next(o['sha256'] for o in record['outputs'] if o['name'].endswith('-halftime.sav'))
    assert sha(data) == expected and expected.startswith(BASE_SHA)
    image = Image.from_savestate(data)
    assert not build_problems(image.memory, image.load)
    original = Original(image)
    g = original.g
    names = []
    for manager in range(135):
        payload = original.name(manager)
        initial = g.mem(g.far(0x9B78)+manager, 1)
        rec = g.mem(g.far(0x9B74)+13*manager, 13)
        assert rec[0] <= 12
        independent = (initial + b' ' + rec[1:1+rec[0]])[:14]
        assert payload == independent
        rendered = original.render(payload)
        assert manager_payload(initial[0], rec) == payload
        assert manager_text(initial[0], rec) == rendered
        names.append(dict(manager=manager, surname_length=rec[0],
                          embedded_nul=0 in payload, original_text=rendered,
                          downstream_text=payload.decode('cp437'),
                          formatted_sha256=sha(payload), screen_matches_payload=True))
    synthetic = []
    for initial, surname in [(ord('X'), b''), (ord('X'), b'ABCDEFGHIJKL'),
                             (ord('X'), b'A\0B'), (ord('X'), b'A\x01\x82\x7f'), (0, b'Name')]:
        g.put(g.far(0x9B78)+134, bytes([initial]))
        g.put(g.far(0x9B74)+13*134, bytes([len(surname)])+surname+b'Z'*(12-len(surname)))
        payload = original.name(134)
        expected_payload = bytes([initial])+b' '+surname
        assert payload == expected_payload
        synthetic.append(dict(initial=initial, synthetic_surname=list(surname),
                              original_text=original.render(payload), length=len(payload)))
    receipt = dict(base_sha256=sha(data),
                   source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                   producer_sha256=sha(Path(__file__).read_bytes()), unicorn=unicorn.__version__,
                   method='isolated unmodified original routines, synthetic call frames; no behavior hooks',
                   bound_per_call='2 seconds / 500000 instructions',
                   source_hashes={p:sha((ROOT/p).read_bytes()) for p in [
                       'static/goal-exe/code/seg_1771_01.asm', 'static/goal-exe/code/seg_214B_01.asm',
                       'static/goal-exe/code/seg_23E4_01.asm']},
                   names=names, synthetic=synthetic)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, ensure_ascii=True)+'\n')
    print(f'{len(names)} genuine records; {len(synthetic)} synthetic controls; formatter/writer exact')
    print(json.dumps(names[12]))


if __name__ == '__main__':
    main()
