"""Disjoint sequential groups of the frozen fourteen-case paired corpus.
Each group runs inside its own registered heavy.sh slot; receipts are exclusive.
"""
import argparse,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import pairs
p=argparse.ArgumentParser();p.add_argument('--cases',nargs='+',required=True);p.add_argument('--out-dir',type=Path,required=True);args=p.parse_args()
assert len(args.cases)==len(set(args.cases)) and set(args.cases)<=set(c[0] for c in pairs.F.runner.CASES)
args.out_dir.mkdir(parents=True,exist_ok=True);frozen=pairs.sources()
for case in args.cases:
    assert pairs.sources()==frozen,'source changed during frozen batch'
    print('fresh paired case',case,flush=True)
    pairs.parent(types.SimpleNamespace(case=case,out=str(args.out_dir/(case+'.jsonl')),diagnostics=False))
    assert pairs.sources()==frozen,'source changed during frozen case'
    print('strict state/draw/key/page/choice equality PASS',case,flush=True)
print('GROUP COMPLETED',flush=True)
