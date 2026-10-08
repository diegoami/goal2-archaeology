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


def _cases(path):
    record = json.loads(path.read_text())
    return record['cases'] if 'cases' in record else [record]


# The only fields a declared defect may exempt (delta review R1): a missing listing input shows in
# the captured draws of an operation and the case's draw bounds, nowhere else. The players'
# initial records (`before`), the expected comparisons (`after`), the operations' kinds, words
# and every other field are compared unconditionally, whatever a declaration says.
EXEMPTIBLE = {'case': {'draw_bounds'}, 'operation': {'draws'}}


def _is_prefix(old, new):
    """A completion only adds what was missing: the old capture is a strict prefix of the new."""
    return (isinstance(old, list) and isinstance(new, list) and len(old) < len(new)
            and new[:len(old)] == old)


def _without(case, fields):
    """The case with the declared defect fields removed (top-level and per operation)."""
    out = {k: v for k, v in case.items() if k not in fields['case']}
    out['operations'] = [{k: v for k, v in op.items() if k not in fields['operation']}
                         for op in case['operations']]
    return out


def select_records(files, supersessions):
    """Omit a superseded capture only when Done-when 1's conditions hold (review round 1 R1):
    the successor is a later record of the SAME cases — identical but for the fields the declared
    defect concerns — and the superseded record really is incomplete: on its own it fails with the
    declared error. Anything else is a failure, never a silent omission."""
    order = [path.name for path in files]
    by_name = {path.name: path for path in files}
    for name, entry in supersessions.items():
        successor = entry['superseded_by']
        if name not in by_name or successor not in by_name:
            raise ValueError('supersession requires both committed records')
        if successor == name or successor in supersessions:
            raise ValueError('superseding record must itself be complete')
        if not isinstance(entry['reason'], str) or not entry['reason'].strip():
            raise ValueError('supersession requires a reason')
        if order.index(successor) <= order.index(name):
            raise ValueError(f'{successor} does not come after {name}')
        fields = entry['differs_only_in']
        for level in ('case', 'operation'):
            extra = set(fields.get(level, [])) - EXEMPTIBLE[level]
            if extra:
                raise ValueError(f'{name}: a defect may not exempt {level} fields {sorted(extra)}')
        old, new = _cases(by_name[name]), _cases(by_name[successor])
        if len(old) != len(new) or any(len(a['operations']) != len(b['operations'])
                                       for a, b in zip(old, new)):
            raise ValueError(f'{successor} does not hold the cases of {name}')
        if any(_without(a, fields) != _without(b, fields) for a, b in zip(old, new)):
            raise ValueError(f'{successor} differs from {name} outside the declared defect '
                             f'fields {fields}')
        for a, b in zip(old, new):           # the exempt fields may only gain what was missing
            for key in fields.get('case', []):
                if a.get(key) != b.get(key) and not _is_prefix(a.get(key), b.get(key)):
                    raise ValueError(f'{successor} replaces {key} instead of completing it')
            for p, q in zip(a['operations'], b['operations']):
                for key in fields.get('operation', []):
                    if p.get(key) != q.get(key) and not _is_prefix(p.get(key), q.get(key)):
                        raise ValueError(f'{successor} replaces an operation\'s {key} '
                                         f'instead of completing it')
        error = entry['fails_alone_with']
        failed = 0
        for case in old:
            try:
                good, total = compare(case)
            except ValueError as e:
                if error not in str(e):
                    raise ValueError(f'{name} fails otherwise than declared: {e}')
                failed += 1
                continue
            if good != total:                 # delta review R2: an ordinary mismatch is never
                raise ValueError(f'{name} has a mismatch beside its declared defect: '
                                 f'{good}/{total}')     # carried off by a superseded record
        if not failed:
            raise ValueError(f'{name} is complete on its own: nothing to supersede')
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
