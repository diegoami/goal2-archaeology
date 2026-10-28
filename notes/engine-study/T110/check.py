#!/usr/bin/env python3
"""Structural/source checks for design proposals; never proof of implementation equivalence."""
import argparse,copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='f55ef8314c1da390eb96091efe2bdab7b73fa534'
IDS={
 'T110a':'arithmetic random-order occupancy event-order decisions modes phase-tail public-api checkpoints identities machine-state evidence-scope'.split(),
 'T110b':'record-view strength-core occupancy-step event-continuation memory-views pure-rules explicit-transitions semantic-rewrite'.split(),
 'T110c':'memory-views pure-rules explicit-transitions semantic-rewrite prototype'.split(),
}
CHAPTERS={'T110a':'rewrite-contract','T110b':'rewrite-options','T110c':'rewrite-assessment'}
OBLIGATIONS=IDS['T110a']
OPTIONS=IDS['T110b'][4:]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def original(path):return git('show',BASE+':'+path)
def write_new(path,data):
 with Path(path).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
def reference(path,needle):
 lines=original(path).decode().splitlines()
 line=next(i for i,s in enumerate(lines,1) if needle in s)
 return dict(path=path,line=line,text=lines[line-1].strip())
def pin(task,producer,rows,sections,*,support=(),**extra):
 paths=sorted({s['path'] for r in rows for s in r['sources']})
 here=Path(producer).resolve().relative_to(ROOT).as_posix()
 return dict(task=task,baseline=BASE,mock=False,method='Design/source synthesis; no engine or prototype execution.',
  limits=['Structural checks do not certify the recommendation, pseudocode or equivalence.','No new engine calls, T107 batch, prototype or adopted semantic change.'],
  producer=dict(path=here,commit=git('rev-parse','HEAD').decode().strip(),sha256=sha((ROOT/here).read_bytes())),
  sources={p:sha(original(p)) for p in paths},
  support={p:sha((ROOT/p).read_bytes()) for p in support},
  sections=sections,rows=rows,**extra)
def validate(task,d,text,*,allow_mock=False):
 assert d['task']==task and d['baseline']==BASE
 assert allow_mock or not d.get('mock'),'structural mock is not design evidence'
 assert d['method'] and d['limits'] and d['sources'] and len(d['sections'])>=3
 assert all('## '+s in text for s in d['sections'])
 assert len(d['rows'])==len(IDS[task]) and {r['id'] for r in d['rows']}==set(IDS[task])
 for p,h in d['sources'].items():assert sha(original(p))==h,('historical source drift',p)
 for p,h in d.get('support',{}).items():assert sha((ROOT/p).read_bytes())==h,('support drift',p)
 for r in d['rows']:
  assert all(r.get(k) for k in ['claim','sources','validation','limits','obligations'])
  assert set(r['obligations'])<=set(OBLIGATIONS)
  assert '### '+r['id'] in text
  for s in r['sources']:
   assert s['path'] in d['sources']
   assert original(s['path']).decode().splitlines()[s['line']-1].strip()==s['text'],s
  if task=='T110b':
   if r['id'] not in OPTIONS:assert r.get('before') and r.get('after') and r.get('counterexample') and r.get('omitted_machine_effects')
   else:assert r.get('benefit') and r.get('risk') and r.get('dependencies') and r.get('contract')
  if task=='T110c' and r['id'] in OPTIONS:
   assert r['estimate_kind']=='designed active-engineering-hour assumptions, not measured productivity'
   assert r['assumptions'] and r['dependencies'] and r['compute']=='not budgeted; no execution authorised'
   assert r['work'] and r['disposition'] in ['recommend','conditional','defer','no-go-now']
   totals=[0,0]
   for w in r['work']:
    assert w['units']>0 and w['basis'] and w['activity'] in ['implementation','validation']
    assert len(w['hours_per_unit'])==2 and 0<=w['hours_per_unit'][0]<=w['hours_per_unit'][1]
    for i in range(2):totals[i]+=w['units']*w['hours_per_unit'][i]
   assert totals==r['total_hours'],'wrong cost sum'
   assert [2*t for t in totals]==r['double_validation_and_implementation_hours'],'wrong sensitivity sum'
  if task=='T110c' and r['id']=='prototype':
   assert all(r.get(k) for k in ['oracle','negative_controls','readability_questions','stop','owner_decisions'])
   assert r['authorised'] is False
 assert d.get('research_engine_calls')==0 and d.get('prototype_implemented') is False
 if not allow_mock:
  p=d['producer'];assert sha(git('show',p['commit']+':'+p['path']))==p['sha256']
  if task=='T110a':
   inv=d['inventory'];assert inv['modules'] and inv['addresses'] and len(inv['addresses'])==len(set(inv['addresses']))
   assert inv['entries']==len(inv['addresses'])
   assert d['compatibility_levels'].keys()=={'machine-boundary','public-api-records','redesigned-semantics'}
   assert d['adopted_weaker_contract'] is False
def controls(task,d,text,*,allow_mock=False):
 out=[]
 for name in ['missing-row','missing-source','missing-limit','missing-obligation','wrong-quote','mock-as-evidence']:
  bad=copy.deepcopy(d)
  if name=='missing-row':bad['rows'].pop()
  elif name=='missing-source':bad['sources']={}
  elif name=='missing-limit':bad['rows'][0]['limits']=[]
  elif name=='missing-obligation':bad['rows'][0]['obligations']=[]
  elif name=='wrong-quote':bad['rows'][0]['sources'][0]['text']='ALTERED-SOURCE'
  else:bad['mock']=True
  try:validate(task,bad,text,allow_mock=allow_mock and name!='mock-as-evidence')
  except (AssertionError,KeyError):out.append(name)
  else:raise AssertionError('negative escaped:'+name)
 if task=='T110c':
  bad=copy.deepcopy(d);bad['rows'][0]['total_hours'][0]+=1
  try:validate(task,bad,text,allow_mock=allow_mock)
  except AssertionError:out.append('wrong-cost-sum')
  else:raise AssertionError('wrong cost sum escaped')
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--task',choices=IDS,required=True);ap.add_argument('--controls',action='store_true');ap.add_argument('--ledger',type=Path);ap.add_argument('--receipt',type=Path);a=ap.parse_args()
 version=2 if a.task=='T110b' else 1
 p=a.ledger or ROOT/f'notes/engine-study/T110/{a.task}-v{version}.json';d=json.loads(p.read_text())
 assert not d.get('mock'),'structural mock is not design evidence'
 text=(ROOT/f'docs/engine-study/{CHAPTERS[a.task]}.md').read_text();validate(a.task,d,text)
 result=dict(task=a.task,ledger_sha256=sha(p.read_bytes()),rows=len(d['rows']),scope=__doc__)
 if a.controls:result['structural_negatives']=controls(a.task,d,text)
 if a.receipt:write_new(a.receipt,result)
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
