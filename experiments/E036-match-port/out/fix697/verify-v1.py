"""Verify source binding and the unchanged682 cross-backend fidelity profile."""
import hashlib
import json
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    originals = FOLDER / 'original-friendly-v2.json'
    port = FOLDER / 'port-friendly-v2.json'
    x, y = (json.loads(path.read_text()) for path in (originals, port))
    for receipt in (x, y):
        assert receipt['source_sha256'] == sha(ROOT / 'runtime/original_match/match.py')
        assert receipt['proof_sha256'] == sha(FOLDER / 'proof-v2.py')
        assert receipt['same_full_result'] and receipt['same_full_physical_memory']
        assert receipt['same_live_records_at_all_stops']
        assert receipt['same_live_team_context_at_all_stops']
        assert receipt['events_equal_with_only_exact_independent_record_and_context_additions']
        assert receipt['memory_mask'] == []
    assert x['engine'] == 'original' and x['implementation'] == 'cpython'
    assert y['engine'] == 'port' and y['implementation'] == 'pypy'
    assert x['input_sha256'] == y['input_sha256']
    comparison = {}
    for arm in ('legacy', 'live'):
        a, b = x[arm], y[arm]
        assert a['completed'] and b['completed']
        for field in ('result_sha256', 'display_profile_events', 'accepted_state_ranges',
                      'snapshots', 'draws', 'draws_digest', 'score'):
            assert a[field] == b[field], (arm, field)
        comparison[arm] = {
            'accepted_fidelity_fields_equal': True,
            'raw_full_memory_equal': a['full_physical_memory_sha256'] == b['full_physical_memory_sha256'],
            'raw_all_events_equal': a['events_sha256'] == b['events_sha256'],
        }
    return {
        'source_sha256': sha(ROOT / 'runtime/original_match/match.py'),
        'proof_sha256': sha(FOLDER / 'proof-v2.py'),
        'receipts_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (originals, port)},
        'matches_completed': 4,
        'decision_snapshots_checked': sum(len(r[arm]['snapshots']) for r in (x, y) for arm in ('legacy', 'live')),
        'within_backend_full_result_memory_exact_event_extension': True,
        'cross_backend': comparison,
        'scope': 'Fresh friendly pause, half-time, immediate swap and checkpoint-load equality; synthetic controls cover other visibility bytes and sides. No extra-time or goal2UI acceptance claim.',
        'event_profile': 'Unchanged682 profile; only full_time.data.screen_sha256 excluded cross-backend. Raw hashes retained.',
        'memory_mask': [],
    }


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
