"""Independent T74 launch-source/reference binding; this is not a match pass.

Verify byte identity against the integrated dispatch Git object, both local
producer receipts and the original immutable references. No source, record,
profile, mask or comparison is modified.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
E036 = ROOT / 'experiments/E036-match-port'
DISPATCH = (OUT / 'all-actions-final-1-dispatch-head.txt').read_text().strip()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_bytes(commit, path):
    return subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)


code = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'runtime/original_match').rglob('*.py'))
code += [f'experiments/E036-match-port/{p}' for p in ['family.py', 'families.py', 'compare.py', 'records.py']]
inputs = [f'experiments/E036-match-port/families/{p}' for p in ['F40.json', 'O8.json', 'S.json']]
inputs += [f'experiments/E036-match-port/families/display/{p}' for p in ['profile.json', 'mask.json']]
profile = json.loads((E036 / 'families/display/profile.json').read_text())
assert profile['mask'] == [], 'the approved DS mask must remain empty'
inputs += [profile['reference'], 'experiments/E036-match-port/out/T57/reference.jsonl',
           'experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl',
           'experiments/E036-match-port/families/display/reference-all-20261023-v1.jsonl']
hashes = {}
for path in sorted(set(code + inputs)):
    data = (ROOT / path).read_bytes()
    assert git_bytes(DISPATCH, path) == data, f'current/dispatch byte mismatch: {path}'
    hashes[path] = sha(data)

local_receipts = {}
for name in ['own-menus-desktop-2', 'falsifiers-desktop-3']:
    path = OUT / name / 'source.json'
    receipt = json.loads(path.read_text())
    assert set(receipt['sources']) == set(code), f'{name}: source inventory changed'
    for source, digest in receipt['sources'].items():
        assert hashes[source] == digest, f'{name}: launch/current/dispatch mismatch: {source}'
    local_receipts[name] = {'head': receipt['head'], 'receipt_sha256': sha(path.read_bytes()),
                            'source_files': len(receipt['sources'])}

sys.path[:0] = [str(E036), str(ROOT / 'runtime')]
import compare
import families

specs = {m.id: m.sha256 for f in families.discover().values() for m in f.matches}
assert len(specs) == 63
old_paths = ['experiments/E036-match-port/out/T57/reference.jsonl',
             'experiments/E036-match-port/families/display/reference-all-20261023-v1.jsonl']
new_paths = ['experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl',
             profile['reference']]
references = []
for old, new in zip(old_paths, new_paths):
    before = (ROOT / old).read_bytes()
    assert before == git_bytes('53b011249446c4a562624b573b84640726134c6b', old)
    after = (ROOT / new).read_bytes()
    assert after.startswith(before), f'{new}: immutable historical prefix changed'
    ref = compare.load(ROOT / new)
    assert set(ref) == set(specs)
    for mid, row in ref.items():
        assert row['spec_sha256'] == specs[mid]
        assert row['image_sha256'] == families.image_sha256()
        assert 'ports' not in row and compare.completed(row) is None
        assert row['mask'] == []
    assert ref['S/no-managed-side']['decisions'] == []
    references.append({'historical': old, 'historical_sha256': sha(before),
                       'extended': new, 'extended_sha256': sha(after),
                       'completed_original_only_matches': len(ref)})

print(json.dumps({'scope': 'source/reference binding only; not an own/integrated match acceptance verdict',
                  'dispatch_head': DISPATCH, 'byte_identical_files': hashes,
                  'local_launch_receipts': local_receipts, 'references': references,
                  'approved_mask': [], 'scenario_specs': len(specs)}, indent=2))
