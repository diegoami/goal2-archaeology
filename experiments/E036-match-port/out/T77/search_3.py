"""Bounded original-only search declarations, separate from accepted families."""
import json,sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import families,family,heavy_slot
HERE=Path(__file__).parent
DIRECTORY=HERE/'search-family-3'
if __name__=='__main__':
 heavy_slot.take('T77-bounded-search',weight=2)
 DIRECTORY.mkdir(exist_ok=False)
 doc=json.loads((ROOT/'experiments/E036-match-port/families/R.json').read_text())
 doc['matches']=[{'id':f'R/search-away-{seed}','seed':seed,'fixture':[7,19,21,1], 'managed':19,
                  'policy':{'name':'PlayOn','contexts':['half_time','substitution']}}
                 for seed in range(1,49)]
 (DIRECTORY/'R.json').write_text(json.dumps(doc,indent=2)+'\n')
original=families.discover
families.discover=lambda:original(DIRECTORY)
if __name__=='__main__':
 sys.argv=[sys.argv[0],'--family','R','--workers','2','--count','0791:C24D,0791:C2A8,0791:C406,0791:C48D,0791:7B77,0791:6ECF','--out',str(HERE/'search-native-3.jsonl')]
 raise SystemExit(family.main())
