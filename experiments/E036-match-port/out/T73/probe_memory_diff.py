"""T73 diagnostic byte-difference LOCATIONS, never a proposed mask or original bytes.

Both actual matches run unmasked. Raw memory stays in this process only; outputs
contain DS/program-relative spans, counts and digests. Original-only access proof,
not these candidate differences, determines any future mask eligibility.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'experiments/E036-match-port'))
import family,families,records
from original_match import Image
from original_match.assets import reference_image

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
source=(ROOT/'runtime/original_match/port/display.py').read_bytes()
(out/'candidate-source.py').open('xb').write(source)
image=Image.from_bytes(reference_image(family.DEFAULT_CACHE))
spec=next(m for m in families.discover()['O8'].matches if m.id=='O8/c1-c2-friendly')
held=[];memory=[]
for name,ports in [('original',()),('display',('display',))]:
 holder=[]
 record=family.run_match(image,spec,ports=ports,time_limit=120,stretch_limit=30,
                         watch=lambda match:holder.append(match))
 (out/(name+'-record.jsonl')).open('x').write(records.dumps(record)+'\n')
 if record['error']:raise SystemExit(record['error'])
 m=holder[0].m
 regions={'DS':m.read(m.DS*16,65536)}
 for key,(start,n) in records.RANGES.items():regions[key]=m.read(m.load*16+start,n)
 memory.append(regions)

def sha(data):return hashlib.sha256(data).hexdigest()
report={'candidate_source_sha256':sha(source),'warning':'Diagnostic differences are NOT mask evidence','regions':{}}
for key in memory[0]:
 a,b=memory[0][key],memory[1][key]
 changed=[]
 for i,(x,y) in enumerate(zip(a,b)):
  if x!=y:
   if changed and changed[-1][1]==i:changed[-1][1]=i+1
   else:changed.append([i,i+1])
 report['regions'][key]=[{'start':start,'length':end-start,'original_sha256':sha(a[start:end]),
                         'candidate_sha256':sha(b[start:end])} for start,end in changed]
(out/'differences.json').open('x').write(json.dumps(report,indent=2)+'\n')
for key,spans in report['regions'].items():
 print(key,sum(s['length'] for s in spans),'different bytes;',len(spans),'spans',flush=True)
print('DS spans',[(hex(s['start']),s['length']) for s in report['regions']['DS']],flush=True)
