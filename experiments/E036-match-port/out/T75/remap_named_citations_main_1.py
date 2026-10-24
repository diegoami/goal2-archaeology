"""One-shot T75 migration: preserve each cited endpoint's text and routine.

The old view comes from the fixed pre-regeneration Git object, not the current
checkout or a previous task's temporary files. Run dry first; --write refuses
unresolved endpoints. Historical out/ evidence is never rewritten.
"""
import csv
import difflib
import io
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = (sys.argv[sys.argv.index('--baseline') + 1] if '--baseline' in sys.argv
        else json.loads((OUT / 'annotation-launch-1.json').read_text())['pre_named_commit'])
CACHE = {}
LEGACY = json.loads((ROOT / 'experiments/E036-match-port/out/T74/citation-remap-main-applied-1.json').read_text())['inherited_invalid_unchanged']
LEGACY_KEYS = {(r['document'], r['citation']) for r in LEGACY}


def old_text(path):
    if path not in CACHE:
        CACHE[path] = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True)
    return CACHE[path]


def index(text):
    return {r['address']: r for r in csv.DictReader(io.StringIO(text), delimiter='\t') if r['file']}


old = index(old_text('static/goal-exe/named/index.tsv'))
new = index((ROOT / 'static/goal-exe/named/index.tsv').read_text())
raw = index((ROOT / 'static/goal-exe/decompiled/index.tsv').read_text())


def lines(view, file, before=False):
    path = f'static/goal-exe/{view}/{file}'
    return (old_text(path) if before else (ROOT / path).read_text()).splitlines()


def bounds(idx, address, content):
    row = idx[address]
    first = int(row['line']) - 1
    last = min([int(r['line']) - 1 for r in idx.values()
                if r['file'] == row['file'] and int(r['line']) - 1 > first] or [len(content)])
    return first, last


mapping = {}
for address, row in old.items():
    a = lines('named', row['file'], True)
    b = lines('named', new[address]['file'])
    first, last = bounds(old, address, a)
    after, end = bounds(new, address, b)
    for block in difflib.SequenceMatcher(None, a[first:last], b[after:end], autojunk=False).get_matching_blocks():
        for k in range(block.size):
            mapping[row['file'], first + block.a + k + 1] = (
                'named', new[address]['file'], after + block.b + k + 1, a[first + block.a + k])


def endpoint(file, number, force_raw=False):
    if not force_raw and (file, number) in mapping:
        return mapping[file, number]
    a = lines('named', file, True)
    if not force_raw and not a[number - 1].strip():
        for distance in range(1, 5):
            for neighbour in (number - distance, number + distance):
                anchor = mapping.get((file, neighbour))
                if anchor:
                    n = anchor[2] + number - neighbour
                    b = lines('named', anchor[1])
                    if 0 < n <= len(b) and b[n - 1] == a[number - 1]:
                        return 'named', anchor[1], n, a[number - 1]
    owners = [(address, row) for address, row in old.items()
              if row['file'] == file and int(row['line']) <= number]
    if not owners:
        return None
    address, row = max(owners, key=lambda pair: int(pair[1]['line']))
    if address not in raw:
        return None
    first, last = bounds(old, address, a)
    b = lines('decompiled', raw[address]['file'])
    start, end = bounds(raw, address, b)
    relative = number - first - 1
    for block in difflib.SequenceMatcher(None, a[first:last], b[start:end], autojunk=False).get_matching_blocks():
        if block.a <= relative < block.a + block.size:
            n = start + block.b + relative - block.a + 1
            assert b[n - 1] == a[number - 1]
            return 'decompiled', raw[address]['file'], n, a[number - 1]
    return None


pattern = re.compile(r'((?:static:)?(?:static/goal-exe/)?)(named/)(seg_[0-9A-Za-z_]+\.c):(\d+)((?:[-–,]\d+)*)')
changes, inherited, unresolved, verified, pending = [], [], [], [], []
paths = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=ROOT, text=True).splitlines()
for rel in paths:
    path = Path(rel)
    if 'out' in path.parts or rel.startswith('static/goal-exe/named/'):
        continue
    original = (ROOT / path).read_text()

    def replace(match):
        prefix, _, file, start, tail = match.groups()
        if (rel, match.group(0)) in LEGACY_KEYS:
            inherited.append({'document': rel, 'citation': match.group(0), 'reason': 'known inherited citation problem retained from pre-T74 (#307)'})
            return match.group(0)
        nums = [int(start)] + [int(n) for n in re.findall(r'\d+', tail)]
        separators = re.findall(r'[-–,]', tail)
        try:
            before = lines('named', file, True)
        except subprocess.CalledProcessError:
            before = []
        if any(n < 1 or n > len(before) for n in nums):
            inherited.append({'document': rel, 'citation': match.group(0), 'reason': 'pre-existing out-of-range endpoint'})
            return match.group(0)
        if len(nums) == 1 and not before[nums[0] - 1].strip():
            inherited.append({'document': rel, 'citation': match.group(0), 'reason': 'pre-existing blank single-line endpoint'})
            return match.group(0)
        targets = [endpoint(file, n) for n in nums]
        if len(targets) > 1 and all(targets) and any(t[:2] != targets[0][:2] for t in targets[1:]):
            targets = [endpoint(file, n, True) for n in nums]
        if any(t is None for t in targets) or (len(targets) > 1 and any(t[:2] != targets[0][:2] for t in targets[1:])):
            unresolved.append({'document': rel, 'citation': match.group(0), 'texts': [before[n - 1] for n in nums]})
            return match.group(0)
        target = targets[0]
        after = f'{prefix}{target[0]}/{target[1]}:{target[2]}'
        for separator, dest in zip(separators, targets[1:]):
            after += f'{separator}{dest[2]}'
        for n, dest in zip(nums, targets):
            actual = lines(dest[0], dest[1])[dest[2] - 1]
            assert actual == before[n - 1] == dest[3]
            verified.append({'document': rel, 'before': f'{file}:{n}',
                             'after': f'{dest[0]}/{dest[1]}:{dest[2]}', 'same_text': actual})
        if after != match.group(0):
            changes.append({'document': rel, 'before': match.group(0), 'after': after,
                            'same_endpoint_texts': [t[3] for t in targets]})
        return after

    result = pattern.sub(replace, original)
    if result != original:
        pending.append((ROOT / path, original, result))

if '--write' in sys.argv and not unresolved:
    for path, original, result in pending:
        assert path.read_text() == original, f'concurrent document change: {path}'
        path.write_text(result)
print(json.dumps({'pre_named_commit': BASE, 'changes': changes, 'verified_endpoints': verified,
                  'inherited_invalid_unchanged': inherited, 'unresolved': unresolved,
                  'written': '--write' in sys.argv and not unresolved}, indent=2))
sys.exit(bool(unresolved))
