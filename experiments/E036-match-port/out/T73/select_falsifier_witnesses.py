"""Select genuinely caught historical witnesses as inputs for a fresh frozen run.

This does not promote old-source mutants to final-source acceptance. Prefer a
completed differing match, then the shortest original ALL entry witness, then
the earliest cohort. All failed/uncaught source records remain untouched.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
from original_match import port
import compare,family

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',required=True);ap.add_argument('--receipt',required=True);a=ap.parse_args()
 registry=port._module_registry('display');needed=set(registry.variants)
 reference=compare.load(ROOT/family.read_display_profile()['reference'])
 original=compare.load(ROOT/'experiments/E036-match-port/out/T73/coverage-unported-desktop-20261023/coverage-unported.jsonl')
 choices={v:[] for v in needed}
 for cohort in (1,2,3):
  folder=ROOT/f'experiments/E036-match-port/out/T73/falsifiers-desktop-20261023-v{cohort}'
  launch=json.loads((folder/'launch.json').read_text())
  routine={row['variant']:row['routine'] for row in launch['manifest']}
  for path in sorted(folder.glob('*.jsonl')):
   for record in compare.load(path).values():
    variant=record['variant'].removeprefix('display.')
    if variant not in needed:continue
    mid=record['id'];completed=not bool(compare.completed(record))
    difference=compare.differences(reference[mid],record,True,True) if completed else []
    if not difference and completed:continue
    assert original[mid]['counts'][routine[variant]]>0
    key=(0 if completed else 1,original[mid]['cpu_s'],cohort,mid)
    choices[variant].append((key,{'variant':variant,'routine':routine[variant],'only':mid},
        {'source':str(path.relative_to(ROOT)),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'match':mid,'completed':completed,'differences':difference,'error':record['error'],'cohort':cohort}))
 assert all(choices.values()),[v for v,c in choices.items() if not c]
 selected=[min(choices[v],key=lambda c:c[0]) for v in sorted(choices)]
 manifest=[x[1] for x in selected]
 (ROOT/a.manifest).open('x').write(json.dumps(manifest,indent=2)+'\n')
 receipt={'purpose':'Historical caughtness chooses inputs only; same-source B normal/mutant validation is still required',
          'runtime_source_sha256':hashlib.sha256((ROOT/'runtime/original_match/port/display.py').read_bytes()).hexdigest(),
          'variants':len(manifest),'completed_witnesses':sum(x[2]['completed'] for x in selected),'witnesses':[x[2] for x in selected]}
 (ROOT/a.receipt).open('x').write(json.dumps(receipt,indent=2)+'\n')
 print('selected',len(manifest),'variants;',receipt['completed_witnesses'],'completed witnesses',flush=True)
if __name__=='__main__':main()
