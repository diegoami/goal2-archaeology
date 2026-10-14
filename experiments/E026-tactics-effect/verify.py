#!/usr/bin/env python3
"""Audit E026's immutable measurements and a complete re-run of arm e3.

python3 -B experiments/E026-tactics-effect/verify.py

Compares all deterministic result fields, including every raw board statistic, against
previous records; CPU/wall times are intentionally excluded. Requires all 30 distinct
seeds for each of the nine arms and for the new e3 reproduction. Existing void records
are retained and counted but cannot enter the summary. No files are written.
"""
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
    runs, bad, repeats = load()
    for arm in ARMS:
        if len(runs[arm]) != 30:
            raise ValueError(f'{arm}: expected 30 distinct successful seeds, found {len(runs[arm])}')
    reference = {}
    for path in sorted(HERE.glob('out/e3-s*.jsonl')):
        for line in path.read_text().splitlines():
            record = json.loads(line)
            reference[record['seed']] = record
    reproduced = [json.loads(line) for line in REPRO.read_text().splitlines()]
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
    print('N per arm: ' + ', '.join(f'{arm} 30' for arm in ARMS))
    print(f'void records retained/excluded: {len(bad)}')
    print('full e3 arm reproduced: 30/30 scores, raw statistics, board, draw digest and declared inputs identical')
    print('counter mutation rejected: stats differs')


if __name__ == '__main__':
    main()
