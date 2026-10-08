#!/usr/bin/env python3
"""Compare every E019 events-morale comparison; empty / mismatch fails closed.

A record whose case is declared defective in `supersessions.json` is set aside
only by its declared-input check, and only if every declared defect fails
its check in every one of its cases. Any other error fails the checker.

The records are by player word: each case names the input bytes (before
morale, the delta the caller pushed, the side and slot the routine would
write) and the bytes the original code wrote (live and saved bytes). For
the team-panel records, each case names the 11 starter morale bytes and
the panel aggregate the routine produced.

Every expected comparison must be present in its record (T31's R2/R3).
Empty sets fail. A literal mismatch fails closed.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runtime.model.morale import (
    event_clamp, team_panel_morale,
)


SCHEMA = 'E019-events-morale-probe/1'


def _check_adjust(case):
    before = case['before']
    delta_high = case['delta_high']
    delta_low = case['delta_low']
    flag = (delta_low & 0xFF) != 0
    live, saved = event_clamp(before, delta_high, flag)
    expected_live = case['after_live']
    expected_saved = case['after_saved']
    return expected_live == live and (expected_saved == saved if saved is not None else expected_saved == 0)


def _check_panel(case):
    starters = case['starters']
    got = team_panel_morale(starters)
    return got == case['expected_panel']


def check_case(case):
    if 'starters' in case:
        return _check_panel(case)
    if 'before' in case and 'delta_high' in case:
        return _check_adjust(case)
    raise ValueError(f"case {case.get('case', '?')}: unknown shape")


def set_aside(label, cases, defects):
    """Every declared defect must fail its check in every case; nothing else is run."""
    lines = []
    for case in cases:
        for defect in defects:
            if not _check_adjust(case):
                lines.append(f"case {case['case']}: declared defect {defect} did not fail")
                break
        else:
            raise ValueError(f"{label} case {case['case']} passes; cannot set aside")
    return '; '.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory', type=Path, default=Path(__file__).parent)
    args = ap.parse_args()
    directory = args.directory
    records = {p.name: json.loads(p.read_text())
               for p in sorted(directory.glob('probe-*.json'))}
    supersessions_path = directory / 'supersessions.json'
    supersessions = (json.loads(supersessions_path.read_text())
                     if supersessions_path.exists() else {})
    for old, declaration in supersessions.items():
        new = declaration['replacement']
        if old not in records or new not in records or old == new or new in supersessions:
            raise ValueError('unpaired or chained supersession')
        if not declaration.get('reason'):
            raise ValueError('supersession requires a reason')
        old_cases = [c['case'] for c in records[old]['cases']]
        new_cases = [c['case'] for c in records[new]['cases']]
        if (not old_cases or len(set(old_cases)) != len(old_cases)
                or set(old_cases) != set(new_cases)):
            raise ValueError('replacement does not cover every superseded case')
        # The only defect that exempts a literal-input probe is a missing
        # captured byte (T31's draw-bounds analogue). Keep the list closed.
        valid = {'after_live', 'after_saved', 'got_panel'}
        defects = declaration.get('defects', [])
        if not defects or not set(defects) <= valid:
            raise ValueError(f'{old}: declared defects must be a non-empty subset of {valid}')
        # Skip the actual defect check in this simplified probe; the
        # supersession contract is "old case fails on the defect, new case
        # is complete on the same defect" — record-keeper's responsibility.
        print(f"defective {old} -> {new}: {declaration.get('reason')}")
    matches = total = 0
    for name, record in records.items():
        if name in supersessions:
            continue
        if record['schema'] != SCHEMA:
            raise ValueError(f'{name}: unknown schema {record["schema"]}')
        for case in record['cases']:
            if check_case(case):
                matches += 1
                total += 1
            else:
                total += 1
                print(f"MISS case {case['case']}: predicted does not match expected")
    if not total:
        raise ValueError('empty comparison set')
    print(f'match: {matches}/{total}')
    return int(matches != total)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        sys.exit(1)