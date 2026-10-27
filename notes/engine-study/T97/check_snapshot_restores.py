#!/usr/bin/env python3
"""Check country-snapshot restore ownership against the original instruction listing."""
import argparse
import copy
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]


def validate(data):
    listing = (ROOT / 'static/goal-exe/code/seg_0791_02.asm').read_text()
    owners, routine = {}, None
    for line in listing.splitlines():
        header = re.match(r'; ---- routine (\S+)', line)
        if header:
            routine = header[1]
        instruction = re.match(r'([0-9A-F]{4})  .*mov word ptr \[0x9b3[46]\],', line)
        if instruction:
            owners[instruction[1]] = routine
    sites = data.get('country_restore_sites', [])
    declared = {site: row['routine'] for row in sites for site in row['sites']}
    assert len(declared) == 4, 'four explicit restore sites required'
    assert set(declared) == {'0CDE', '0CE1', '11BD', '11C0'}, 'restore frontier differs'
    for site, owner in declared.items():
        assert owners[site] == owner, f'{site}: declared {owner}, listing {owners[site]}'
    return declared


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--ledger', type=Path, default=ROOT / 'notes/engine-study/T97/transient-v3.json')
    ap.add_argument('--controls', action='store_true')
    args = ap.parse_args()
    data = json.loads(args.ledger.read_text())
    print(json.dumps(validate(data), sort_keys=True))
    if args.controls:
        wrong = copy.deepcopy(data)
        wrong['country_restore_sites'][1]['routine'] = '0791:0C65'
        try:
            validate(wrong)
        except AssertionError as exc:
            print(f'PASS: inherited wrong-owner control rejected: {exc}')
        else:
            raise AssertionError('wrong-owner control escaped')


if __name__ == '__main__':
    main()
