#!/usr/bin/env python3
"""Compare every retained confidence probe by player word, fail closed.

A record declared defective in supersessions.json is set aside only by its
declared-input check (the squad and status injection the probe declares),
and only if each declared defect fails in every one of its cases. Any other
error, in a kept or a superseded record, trace or run, fails the checker.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runtime.model.confidence import country_rating, result_delta, participant_values

# probe_fixture.py's declared injection: record[16] = 4 if slot == 12 else 0
# (player +0x10, Pascal set element 3 = bit 2; B7FA reads it, notes.md).
STATUS_OFFSET = 16
PARTICIPATED = 4
DECLARED_PARTICIPANT_SLOT = 12
DEFECT_CHECKS = ('squad', 'status')


def squad_word(case, side, slot):
    fixture = bytes.fromhex(case['fixture'])
    word = int.from_bytes(fixture[4 + side * 2:6 + side * 2], 'little')
    country = {c['country_word']: bytes.fromhex(c['record']) for c in case['countries']}[word]
    return int.from_bytes(country[(slot - 1) * 2:slot * 2], 'little')


def declared_input_failures(case):
    """The probe's declared inputs against what the record shows it injected."""
    failures = {}
    for p in case['before']:
        if 'squad' not in failures and squad_word(case, p['side'], p['slot']) != p['player_word']:
            failures['squad'] = 'declared slot disagrees with injected squad'
        declared = PARTICIPATED if p['slot'] == DECLARED_PARTICIPANT_SLOT else 0
        if 'status' not in failures and bytes.fromhex(p['record'])[STATUS_OFFSET] != declared:
            failures['status'] = 'declared status disagrees with injected +0x10'
    return failures


def check_case(case):
    failures = declared_input_failures(case)
    if failures:
        raise ValueError('; '.join(failures.values()))
    if case['strays']:
        raise ValueError('probe skipped a reachable call')
    fixture = bytes.fromhex(case['fixture'])
    countries = {c['country_word']: bytes.fromhex(c['record']) for c in case['countries']}
    before = {p['player_word']: p for p in case['before']}
    after = {p['player_word']: p['confidence'] for p in case['after']}
    if len(before) != len(case['before']) or len(after) != len(case['after']) or not before or before.keys() != after.keys():
        raise ValueError('missing or duplicate player-word comparison')
    table = bytes.fromhex(case['classification_set'])
    kind = fixture[2]
    special = bool(table[kind // 8] & (1 << (kind % 8)))
    ratings = []
    for side in (0, 1):
        word = int.from_bytes(fixture[4 + side * 2:6 + side * 2], 'little')
        country = countries[word]
        ratings.append(country_rating(country[44], country[42], country[43]))
    expected_ops = []
    matched = 0
    for word, p in before.items():
        record = bytes.fromhex(p['record'])
        side, slot = p['side'], p['slot']
        role = 'starter' if slot <= 11 else 'substitute' if record[STATUS_OFFSET] & PARTICIPATED else 'unused'
        delta = result_delta(ratings[side], ratings[1 - side], fixture[:2], fixture[3], side, special)
        ops = [o for o in case['operations'] if o['player_word'] == word]
        sites = [o['return_ip'] for o in ops]
        expected_sites = [0xB951] if role == 'starter' else [0xB951, 0xB991] if role == 'substitute' else [0xB9BB]
        if sites != expected_sites:
            raise ValueError(f'player word {word}: unexpected confidence call sites {sites}')
        if role != 'unused' and ops[0]['delta_word'] != delta & 65535:
            raise ValueError(f'player word {word}: result delta disagrees with original B71C')
        draws = None
        if role != 'starter':
            count = ops[-1]['draw_count']
            pair = case['draws'][count - 2:count]
            if [d['bound'] for d in pair] != ([2, 2] if role == 'substitute' else [4, 2]):
                raise ValueError('confidence draw bounds disagree')
            draws = tuple(d['value'] for d in pair)
            if ops[-1]['delta_word'] != (draws[1] - draws[0]) & 65535:
                raise ValueError('confidence draw arithmetic disagrees')
        predicted = participant_values(record[12], delta, role, draws)
        expected_ops.extend(ops)
        if predicted != (after[word],):
            print(f"MISS case {case['case']} player-word {word}: expected {predicted}, observed {after[word]}")
        else:
            matched += 1
    if len(expected_ops) != len(case['operations']):
        raise ValueError('unaccounted confidence calls')
    return matched, len(before)


def set_aside(label, cases, defects):
    """Every declared defect must fail its check in every case; nothing else is run."""
    # Callers guarantee cases is non-empty (the coverage check, and run == trace).
    lines = []
    for case in cases:
        failures = declared_input_failures(case)
        for defect in defects:
            if defect not in failures:
                raise ValueError(f"{label} case {case['case']} passes its declared {defect} check; cannot set aside")
        lines.append(f"case {case['case']}: " + '; '.join(failures[d] for d in defects))
    return '; '.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory', type=Path, default=Path(__file__).parent)
    args = ap.parse_args()
    directory = args.directory
    records = {p.name: json.loads(p.read_text()) for p in sorted(directory.glob('fixture-probe-*.json'))}
    supersessions = json.loads((directory / 'supersessions.json').read_text())
    for old, declaration in supersessions.items():
        new = declaration['replacement']
        if old not in records or new not in records or old == new or new in supersessions or not declaration['reason']:
            raise ValueError('unpaired or chained supersession')
        defects = declaration['defects']
        if not defects or len(set(defects)) != len(defects) or not set(defects) <= set(DEFECT_CHECKS):
            raise ValueError(f'{old}: declared defects must be a non-empty subset of {DEFECT_CHECKS}')
        old_cases = [c['case'] for c in records[old]['cases']]
        new_cases = [c['case'] for c in records[new]['cases']]
        if not old_cases or len(set(old_cases)) != len(old_cases) or set(old_cases) != set(new_cases):
            raise ValueError('replacement does not cover every superseded case')
        print(f"defective {old} -> {new}: {set_aside(old, records[old]['cases'], defects)}; {declaration['reason']}")
    matches = total = 0
    for name, record in records.items():
        if name in supersessions:
            continue
        if record['schema'] != 'E018-confidence-probe/1':
            raise ValueError('unknown record schema')
        for case in record['cases']:
            n, count = check_case(case)
            matches += n
            total += count
    distinct_matches, distinct = matches, total
    # Run observations are retained comparisons too, not merely metadata.
    if directory.resolve() == Path(__file__).parent.resolve():
        for path in sorted((ROOT / 'runs/E018').glob('*.json')):
            run = json.loads(path.read_text())
            trace_name = run['observations'][0]['field'].split()[-1]
            cases = [json.loads(o['value']) for o in run['observations'][1:]]
            if cases != records[trace_name]['cases']:
                raise ValueError(f'{path.name}: run observations disagree with retained trace')
            if trace_name in supersessions:
                declaration = supersessions[trace_name]
                print(f"defective {path.name}: {set_aside(path.name, cases, declaration['defects'])}; replacement {declaration['replacement']}")
            else:
                for case in cases:
                    n, count = check_case(case)
                    matches += n
                    total += count
    if not total:
        raise ValueError('empty comparison set')
    print(f'match: {distinct_matches}/{distinct} ({total} incl. run observations)')
    return int(matches != total)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)
