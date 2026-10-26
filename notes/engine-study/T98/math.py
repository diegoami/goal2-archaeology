#!/usr/bin/env python3
"""Run a source-derived analytical slice; no original emulator or Match is created."""
import argparse
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import write_new


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--skill',action='store_true');g.add_argument('--strength',action='store_true')
    ap.add_argument('--check',action='store_true');a=ap.parse_args()
    name='skill' if a.skill else 'strength'
    data=importlib.import_module(name).build()
    path=ROOT/f'notes/engine-study/T98/{name}-v1.json'
    if a.check:
        assert json.loads(path.read_text())==data,f'{name} calculations/source provenance differ'
        print('PASS:',name,json.dumps(data['checks'],sort_keys=True))
    else:write_new(path,data);print('wrote',path.relative_to(ROOT),data['checks'])


if __name__=='__main__':main()
