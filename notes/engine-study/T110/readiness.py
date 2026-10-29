#!/usr/bin/env python3
"""Pre-dispatch absent rejection, labelled structural mocks and mock-evidence refusal; no engine calls."""
import argparse,subprocess,sys,tempfile
from pathlib import Path
from check import ROOT,BASE,IDS,OPTIONS,validate,controls,reference,sha,original,write_new
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 rows=[];source='docs/engine-study/inventory.md';ref=reference(source,'# Engine inventory')
 for task,ids in IDS.items():
  cmd=[sys.executable,'-B',str(ROOT/'notes/engine-study/T110/check.py'),'--task',task,'--controls']
  absent=subprocess.run(cmd,capture_output=True,text=True);assert absent.returncode!=0 and 'FileNotFoundError' in absent.stderr
  items=[]
  for i in ids:
   r=dict(id=i,claim='MOCK',sources=[ref],validation='MOCK',limits=['MOCK'],obligations=['arithmetic'],
    before='MOCK',after='MOCK',counterexample='MOCK',omitted_machine_effects='MOCK',benefit='MOCK',risk='MOCK',dependencies=['MOCK'],contract='MOCK')
   if task=='T110c':
    r.update(estimate_kind='designed active-engineering-hour assumptions, not measured productivity',assumptions=['MOCK'],
     compute='not budgeted; no execution authorised',work=[dict(units=1,basis='MOCK',activity='implementation',hours_per_unit=[1,2])],
     total_hours=[1,2],double_validation_and_implementation_hours=[2,4],disposition='defer',
     oracle='MOCK',negative_controls=['MOCK'],readability_questions=['MOCK'],stop=['MOCK'],owner_decisions=['MOCK'],authorised=False)
   items.append(r)
  d=dict(task=task,baseline=BASE,mock=True,method='MOCK:structural only',limits=['MOCK'],sources={source:sha(original(source))},
   sections=['One','Two','Three'],rows=items,research_engine_calls=0,prototype_implemented=False)
  text='\n'.join('## '+s for s in d['sections'])+'\n'+'\n'.join('### '+i for i in ids)
  validate(task,d,text,allow_mock=True);negatives=controls(task,d,text,allow_mock=True)
  with tempfile.TemporaryDirectory(prefix='T110-labelled-mock-') as tmp:
   p=Path(tmp)/'mock.json';write_new(p,d)
   refused=subprocess.run(cmd+['--ledger',str(p)],capture_output=True,text=True)
   assert refused.returncode!=0 and 'structural mock is not design evidence' in refused.stderr
  rows.append(dict(task=task,baseline_argv=cmd,baseline_exit=absent.returncode,baseline_stderr=absent.stderr,
   labelled_mock='accepted only structurally; not evidence',production_mock_exit=refused.returncode,structural_negatives=negatives))
 write_new(a.out,dict(scope=__doc__,execution_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),results=rows))
 print('PASS:3 absent ledgers reject;3 labelled mocks accepted structurally;3 production mock refusals;19 structural negatives reject')
if __name__=='__main__':main()
