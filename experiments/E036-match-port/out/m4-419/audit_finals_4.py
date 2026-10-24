"""Validate every final source-pinned original/display/all finals record."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,records
from original_match import port
addresses=['1771:'+a for a in ('883F','89C1','89FE','8A5D','8CCF','8D84','9028','91CE','937C','9509','5C94','5CCB')]
results=[];entry_checks=0
for name,score in [('FS',[2,0]),('G13',[1,0])]:
 spec=families.load_family(OUT/'source-specs-1'/f'{name}.json').matches[0]
 reference=compare.load(OUT/f'{name}-reference-3.jsonl')
 for mode,ports in [('display',['display']),('all',port.available())]:
  path=OUT/f'{name}-{mode}-{4 if mode=="all" else 3}.jsonl';candidate=compare.load(path)
  lines,ok=compare.check(reference,candidate,{spec.id:spec.sha256},no_screen=True,strict_display=True,image_sha256={spec.id:spec.image_sha256});assert ok,lines
  row=candidate[spec.id];assert row['score']==score and row['mask']==[] and row['ports']==ports and row['variant'] is None and len(row['after']['ds'])==64 and len(row['after']['ranges']['records'])==105
  for address in addresses:
   assert row['counts'][address]==row['port_calls'][address]==reference[spec.id]['counts'][address],(name,mode,address)
   entry_checks+=1
  results.append({'id':spec.id,'mode':mode,'strict_identical':True,'source_sha256':row['image_sha256'],'score':score,'record_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
paths=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+[p for p in (ROOT/'experiments/E036-match-port').glob('*.py') if p.name!='locate.py'])
hashes={}
for p in paths:
 rel=str(p.relative_to(ROOT));actual=hashlib.sha256(p.read_bytes()).hexdigest();before=hashlib.sha256(subprocess.check_output(['git','show','158790a0:'+rel],cwd=ROOT)).hexdigest();assert actual==before,rel;hashes[rel]=actual
receipt={'comparisons':results,'entry_call_checks':entry_checks,'mask':[],'all_DS_blocks_compared':True,'all_calendar_blocks_compared':105,'runtime_and_match_producer_sources_match_integration_launch':True,'source_commit':'158790a0620c486a5c8dad0e0670cc6064151e8d','source_sha256':hashes,'separate_diagnostic_change':'locate.py; not imported by family runner; covered by final full suite and dedicated old-loader control'}
with (OUT/'finals-audit-4.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('PASS: both finals sources; original/display/all;4 strict candidate comparisons;48 entry/call checks; every DS and calendar block')
