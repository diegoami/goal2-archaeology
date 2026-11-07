"""Four faithful original-stage cases, sequential within one shared heavy slot."""
from pathlib import Path
import sys,types
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import terminal_v2 as T
for case in ('continental','world','ageing-continental','ageing-world'):
    print('natural strict case',case,flush=True)
    T.parent(types.SimpleNamespace(case=case,out=str(HERE/('natural-'+case+'-v3.jsonl'))))
    print('PASS',case,flush=True)
print('ALL FOUR NATURAL CASES COMPLETED',flush=True)
