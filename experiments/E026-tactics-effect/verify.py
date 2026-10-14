#!/usr/bin/env python3
"""Audit E026's immutable measurements and a complete re-run of arm e3.

python3 -B experiments/E026-tactics-effect/verify.py

Compares all deterministic result fields, including every raw board statistic, against
previous records; CPU/wall times are intentionally excluded. Requires 30 distinct successful
seeds per arm (29 for e7, whose retained void record is excluded) and for the new e3 reproduction. Existing void records
are retained and counted but cannot enter the summary. No files are written.
"""
import argparse
import json
from pathlib import Path
from analyze import ARMS, load

HERE = Path(__file__).resolve().parent
REPRO = HERE / 'out/repro-e3-s0-29-20261014.jsonl'
FIELDS = ('arm', 'mask', 'seed', 'error', 'stopped_at_board', 'strays', 'score', 'clock',
          'stats', 'sides', 'scorers', 'man_of_the_match', 'commentary_calls',
          'board_sha256', 'draws_count', 'draws_sha256', 'inputs', 'i')


def compare(reference, reproduced):
    for field in FIELDS:
        if reference[field] != reproduced[field]:
            raise ValueError(f"{reproduced['arm']} seed {reproduced['seed']}: {field} differs")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--repro', type=Path, default=REPRO, help='full e3 re-run JSONL to compare')
    args = parser.parse_args()
    runs, bad, repeats = load()
    for arm in ARMS:
        expected = 29 if arm == 'e7' else 30
        if len(runs[arm]) != expected:
            raise ValueError(f'{arm}: expected {expected} distinct successful seeds, found {len(runs[arm])}')
    seen = {}
    checked = 0
    for path in sorted(HERE.glob('out/*-s*.jsonl')):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            if record.get('error') or not record.get('stopped_at_board') or record.get('strays'):
                continue
            key = (record['arm'], record['seed'])
            if key in seen:
                compare(seen[key], record)
                checked += 1
            else:
                seen[key] = record
    reference = {}
    for path in sorted(HERE.glob('out/e3-s*.jsonl')):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            reference[record['seed']] = record
    reproduced = [json.loads(line) for line in args.repro.read_text().splitlines()]
    if len(reproduced) != 30 or {r['seed'] for r in reproduced} != set(reference):
        raise ValueError('reproduction must cover exactly the same 30 distinct e3 seeds')
    for record in reproduced:
        compare(reference[record['seed']], record)
    # Prove the comparison checks a board counter, not just the score/draw digest.
    changed = json.loads(json.dumps(reproduced[0]))
    changed['stats']['Shots'][0] += 1
    try:
        compare(reference[changed['seed']], changed)
    except ValueError as error:
        if 'stats differs' not in str(error):
            raise
    else:
        raise ValueError('counter mutation was not detected')
    print('N per arm: ' + ', '.join(f'{arm} {len(runs[arm])}' for arm in ARMS))
    print(f'void records retained/excluded: {len(bad)}')
    print(f'all repeated (arm, seed) results identical in every deterministic field: {checked}')
    print('full e3 arm reproduced: 30/30 scores, raw statistics, board, draw digest and declared inputs identical')
    print('counter mutation rejected: stats differs')


if __name__ == '__main__':
    main()
