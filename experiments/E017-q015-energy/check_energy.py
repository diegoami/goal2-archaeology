#!/usr/bin/env python3
"""Replay every E017 comparison by player word; absent/empty/malformed records fail."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runtime.model import energy


def compare(record):
    players = {}
    for item in record['before']:
        word = item['player_word']
        if word in players:
            raise ValueError('duplicate initial player word')
        players[word] = bytes.fromhex(item['record'])
    for op in record['operations']:
        word = op['player_word']
        old = players[word]
        kind = op['kind']
        if kind == 'watched':
            players[word], counter = energy.watched_step(old, op['counter'], op['enabled'])
            if counter != op['counter_after']:
                raise ValueError('activity reset disagrees')
        elif kind == 'quick':
            players[word] = energy.quick_tick(old, op['minute'])
        elif kind == 'form':
            players[word] = energy.form_delta(old, op['delta'])
        elif kind == 'injury':
            players[word] = energy.injure(old)
        elif kind == 'restore':
            players[word] = energy.restore(old, op['match_form'])
        elif kind == 'recover':
            players[word] = energy.recover(old, op['flag'], op['draws'], op['caps'])
        else:
            raise ValueError(f'unknown operation {kind}')
    seen = set()
    good = total = 0
    for item in record['after']:
        word = item['player_word']
        if word in seen:
            raise ValueError('duplicate final player word')
        seen.add(word)
        expected = bytes.fromhex(item['bytes_c_d_e'])
        if len(expected) != 3:
            raise ValueError('expected comparison must contain all three bytes')
        predicted = players[word][12:15]
        total += 1
        good += predicted == expected
        if predicted != expected:
            print(f'MISS player word {word}: {predicted.hex()} != {expected.hex()}')
    if seen != set(players) or not total:
        raise ValueError('every initial player word must have exactly one final comparison')
    if record.get('unknown_stores') or record.get('strays'):
        raise ValueError('unmodelled guest store or stray skipped RNG consumer')
    return good, total


def select_records(files, supersessions):
    """Validate explicit supersessions before omitting any incomplete capture."""
    names = {path.name for path in files}
    for name, entry in supersessions.items():
        successor = entry['superseded_by']
        if name not in names or successor not in names:
            raise ValueError('supersession requires both committed records')
        if successor == name or successor in supersessions:
            raise ValueError('superseding record must itself be complete')
        if not isinstance(entry['reason'], str) or not entry['reason'].strip():
            raise ValueError('supersession requires a reason')
    for name, entry in sorted(supersessions.items()):
        print(f"superseded {name} by {entry['superseded_by']}: {entry['reason']}")
    return [path for path in files if path.name not in supersessions]


def main():
    files = sorted(Path(__file__).with_name('records').glob('*.json'))
    supersessions = json.loads(Path(__file__).with_name('supersessions.json').read_text())
    files = select_records(files, supersessions)
    good = total = 0
    for path in files:
        record = json.loads(path.read_text())
        cases = record['cases'] if 'cases' in record else [record]
        if not cases:
            raise ValueError('empty case batch')
        for case in cases:
            matched, count = compare(case)
            good += matched
            total += count
    print(f'match: {good}/{total}')
    return 0 if total and good == total else 1


if __name__ == '__main__':
    sys.exit(main())
