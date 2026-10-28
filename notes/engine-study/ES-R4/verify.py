#!/usr/bin/env python3
"""ES-R4 source/design/control verification only. Full CI is separate; no research engine or prototype call."""
import argparse,hashlib,importlib.util,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='f55ef8314c1da390eb96091efe2bdab7b73fa534'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def matrix():
 p=ROOT/'notes/engine-study/ES-R3/verify.py'
 spec=importlib.util.spec_from_file_location('esr3_source_matrix',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 out=m.matrix()
 for task,producer in [('T110a','contract'),('T110b','options'),('T110c','recommendation')]:
  out.append([sys.executable,'-B',f'notes/engine-study/T110/{producer}.py','--check'])
  out.append(['tools/heavy.sh','ES-R4-'+task,'--',sys.executable,'-B','notes/engine-study/T110/check.py','--task',task,'--controls'])
 assert len(out)==21
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path);a=ap.parse_args()
 if a.receipt and a.receipt.exists():raise SystemExit('refuse to overwrite receipt')
 checks=[];head=git('rev-parse','HEAD').decode().strip()
 for cmd in matrix():
  r=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
  checks.append(dict(argv=cmd,exit=r.returncode,stdout=r.stdout,stderr=r.stderr))
  print(('PASS' if r.returncode==0 else 'FAIL')+': '+' '.join(cmd),flush=True)
  if r.returncode:raise SystemExit(r.stderr or r.stdout)
 changed=git('diff','--name-only',BASE,'HEAD').decode().splitlines()
 exact={'AGENTS.md','CLAUDE.md','docs/tasks/README.md','docs/tasks/T110.md','docs/tasks/T110a.md','docs/tasks/T110b.md','docs/tasks/T110c.md','docs/engine-study/README.md','docs/engine-study/rewrite-contract.md','docs/engine-study/rewrite-options.md','docs/engine-study/rewrite-assessment.md'}
 unexpected=[p for p in changed if p not in exact and not p.startswith(('notes/engine-study/T110/','notes/engine-study/ES-R4/'))]
 assert not unexpected,('unaccounted milestone changes',unexpected)
 protected=git('diff','--name-only',BASE,'HEAD','--','runtime','static','spec','findings','runs','experiments','tests','tools','.github').decode().splitlines()
 assert not protected,('production/original/evidence infrastructure changed',protected)
 old=json.loads((ROOT/'notes/engine-study/ES-R3/source-checks-v2.json').read_text())
 old_input_diffs=[p for p,h in old['current_input_sha256'].items() if sha((ROOT/p).read_bytes())!=h]
 assert old_input_diffs==['docs/engine-study/README.md'],'unexpected old receipt input drift'
 for x in old['immutable_previous_outputs']:assert sha((ROOT/x['path']).read_bytes())==x['sha256'],x['path']
 preserved=[]
 for p in git('ls-tree','-r','--name-only',head,'--','notes/engine-study').decode().splitlines():
  if not p.endswith(('.json','.txt','.log')):continue
  first=git('log','--reverse','--format=%H','--diff-filter=A',head,'--',p).decode().splitlines()[0]
  raw=(ROOT/p).read_bytes();assert git('show',first+':'+p)==raw,('immutable output changed',p)
  preserved.append(dict(path=p,first_commit=first,sha256=sha(raw)))
 ledgers={t:json.loads((ROOT/f'notes/engine-study/T110/{t}-v{v}.json').read_text()) for t,v in [('T110a',1),('T110b',2),('T110c',1)]}
 assert all(d['research_engine_calls']==0 and d['prototype_implemented'] is False for d in ledgers.values())
 assert ledgers['T110a']['adopted_weaker_contract'] is False
 assert next(r for r in ledgers['T110c']['rows'] if r['id']=='prototype')['authorised'] is False
 report=json.loads((ROOT/'notes/engine-study/T106/report-v1.json').read_text());assert report['budget']['invocations']==48
 inputs=sorted(set(['notes/engine-study/ES-R4/verify.py','docs/engine-study/README.md']+
  [f'notes/engine-study/T110/{n}.py' for n in ['check','contract','options','recommendation']]+
  [f'docs/engine-study/rewrite-{n}.md' for n in ['contract','options','assessment']]))
 result=dict(scope=__doc__,execution_head=head,previous_milestone=BASE,checks=checks,
  changed_paths=changed,protected_changes=protected,historical_ESR3_receipt_input_diffs=old_input_diffs,
  historical_ESR3_receipt_scope='Its README pin remains historical at m7; current guide links/explanation are declared changes, not overwritten evidence.',
  current_input_sha256={p:sha((ROOT/p).read_bytes()) for p in inputs},immutable_previous_outputs=preserved,
  operative_ledgers={t:d['producer'] for t,d in ledgers.items()},
  historical_ledgers={'T110b-v1':'Retained incorrect proposed movement-effect order; structural pass never proved semantics. Operative v2 corrects writes before readers.'},
  design_rows=sum(len(d['rows']) for d in ledgers.values()),registry_modules=23,registry_entries=439,
  prior_research_invocations=48,new_research_engine_calls=0,prototype_implemented=False,
  limits=['21source/data/design/software commands,not21engine experiments.','19new source/structure/cost negatives;not19executed gameplay mutants.','Existing55ES-R3literal guards and25ES-R2guards retain their original scopes;do not sum copied/mocked controls as independent proof.',
   'Cost rates/scopes are uncalibrated planning assumptions; arithmetic consistency does not validate forecasts.','No adopted weaker contract,T111,full rewrite,T107 budget or new match evidence.','Exact-candidate full static/unit CI selecting all6slowmodules remains separately required.'])
 if a.receipt:
  with a.receipt.open('x') as f:json.dump(result,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps(dict(commands=len(checks),preserved_outputs=len(preserved),design_rows=result['design_rows'],
  source_registry=[23,439],prior_research_invocations=48,new_research_engine_calls=0,prototype_implemented=False),indent=2))
if __name__=='__main__':main()
