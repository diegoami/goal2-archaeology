"""T73: compare event-field digests without recording any event text or original bytes.

The same actual play loop runs original and display candidate. Only field names and
SHA-256 digests are emitted, plus whether dropping exactly full_time.screen_sha256
makes the complete event streams equal. No comparison policy is changed here.
"""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'experiments/E036-match-port'))
import family,families,records
from original_match import Image
from original_match.assets import reference_image

out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
image=Image.from_bytes(reference_image(family.DEFAULT_CACHE))
spec=next(m for m in families.discover()['O8'].matches if m.id=='O8/c1-c2-friendly')
original_play=family.play
reports=[]
def digest(v):return records.sha256_text(records.canonical(v))
for name,ports in [('original',()),('display',('display',))]:
 def play(m,*args,**kwargs):
  result=original_play(m,*args,**kwargs)
  rows=[];without=[]
  for kind,minute,score,data in result[0]:
   rows.append({'kind':kind,'meta_sha256':digest([kind,minute,list(score)]),
                'fields':{k:digest(v) for k,v in data.items()}})
   cleaned=dict(data)
   if kind=='full_time':cleaned.pop('screen_sha256',None)
   without.append((kind,minute,score,cleaned))
  reports.append({'run':name,'events':rows,'event_count':len(rows),
                  'digest_without_full_time_screen':records.events_digest(without)[1]})
  return result
 family.play=play
 rec=family.run_match(image,spec,ports=ports,time_limit=120,stretch_limit=30)
 (out/(name+'-record.jsonl')).open('x').write(records.dumps(rec)+'\n')
 if rec['error']:raise SystemExit(rec['error'])
family.play=original_play
(out/'field-digests.json').open('x').write(json.dumps(reports,indent=2)+'\n')
a,b=reports
problems=[]
for i,(x,y) in enumerate(zip(a['events'],b['events'])):
 for k in set(x['fields'])|set(y['fields']):
  if x['fields'].get(k)!=y['fields'].get(k):problems.append({'event':i,'kind':x['kind'],'field':k})
 if x['meta_sha256']!=y['meta_sha256']:problems.append({'event':i,'kind':x['kind'],'field':'event-metadata'})
summary={'event_counts':[a['event_count'],b['event_count']], 'differences':problems,
         'equal_without_only_full_time_screen_sha256':a['digest_without_full_time_screen']==b['digest_without_full_time_screen'],
         'candidate_source_sha256':hashlib.sha256((ROOT/'runtime/original_match/port/display.py').read_bytes()).hexdigest()}
(out/'summary.json').open('x').write(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2),flush=True)
