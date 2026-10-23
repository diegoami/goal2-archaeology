"""T72: every port call equals its counted entry and the unhooked count, per match."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
entries = subprocess.check_output([sys.executable, str(HERE/'coverage_addresses.py'), '--entries'], text=True).strip().split(',')
reference = {r['id']: r for r in map(json.loads, (HERE/'coverage-unported-desktop-20261023/coverage-unported.jsonl').read_text().splitlines())}
candidate = [json.loads(line) for line in Path(sys.argv[1]).read_text().splitlines() if line]
assert len(candidate) == 62
assert {r['id'] for r in candidate} == set(reference)
print('match\t'+'\t'.join(entries))
for rec in candidate:
    assert 'update' in rec['ports'], (rec['id'], rec['ports'])
    for entry in entries:
        assert rec['port_calls'][entry] == rec['counts'][entry] == reference[rec['id']]['counts'][entry], (rec['id'], entry, rec['port_calls'][entry], rec['counts'][entry], reference[rec['id']]['counts'][entry])
    print(rec['id']+'\t'+'\t'.join(str(rec['port_calls'][e]) for e in entries))
print('PASS: 62 matches x 12 routines; port calls = counted entries = unhooked entry counts')
for entry in entries:
    calls = [r['port_calls'][entry] for r in candidate]
    print(f'{entry}: {sum(calls)} calls; {sum(bool(c) for c in calls)}/62 matches; range {min(calls)}..{max(calls)}')
