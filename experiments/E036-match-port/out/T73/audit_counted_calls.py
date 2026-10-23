"""Audit all 88 T73 entry counters against port calls in a complete ALL run.

Removed routines may eliminate nested calls: equality is against the candidate's
independent entry counters, not historical unhooked totals.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
E036 = ROOT / 'experiments/E036-match-port'
sys.path.insert(0, str(E036))
import compare
import families


def main():
    candidate = compare.load(sys.argv[1])
    expected = {mid: digest for fam in families.select('ALL', families.discover())
                for mid, digest in fam.expected().items()}
    assert set(candidate) == set(expected), 'Not the complete ALL family'
    entries = [r['address'] for r in json.loads((E036 / 'out/T73/static-inventory.json').read_text())]
    assert len(set(entries)) == 88
    assert compare.candidate_display_profile(candidate, True) is not None, 'Strict display profile required'
    totals = {entry: 0 for entry in entries}
    checks = 0
    for mid, rec in candidate.items():
        assert rec['spec_sha256'] == expected[mid], mid
        assert not compare.completed(rec), (mid, compare.completed(rec))
        for entry in entries:
            calls = rec['port_calls'][entry]
            counted = rec['counts'][entry]
            assert calls == counted, (mid, entry, calls, counted)
            totals[entry] += calls
            checks += 1
    print(json.dumps({'matches': len(candidate), 'routines': len(entries), 'entry_checks': checks,
                      'mismatches': 0, 'total_calls_by_routine': totals}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
