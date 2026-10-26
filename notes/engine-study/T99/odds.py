#!/usr/bin/env python3
"""Run exact finite-seed analytical examples; these are not whole-match experiments."""
import argparse
import importlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import write_new


def main():
    ap=argparse.ArgumentParser(description=__doc__);g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--gates',action='store_true');g.add_argument('--contests',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    name='gates' if a.gates else 'contests';data=importlib.import_module(name).build();version='v1' if a.gates else 'v2';path=ROOT/f'notes/engine-study/T99/{name}-{version}.json'
    if a.check:
        assert json.loads(path.read_text())==data,f'{name} analysis/source differs';print('PASS:',name,json.dumps(data['checks'],sort_keys=True))
    else:write_new(path,data);print('wrote',path.relative_to(ROOT),data['checks'])


if __name__=='__main__':main()
