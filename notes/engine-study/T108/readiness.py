#!/usr/bin/env python3
"""Absent-baseline and labelled-mock audit contract checks; not research evidence."""
import subprocess
import sys
from check import ROOT,BASE,CANDIDATES,pin,validate,controls,write_new

results=[]
for task,ids in CANDIDATES.items():
    cmd=[sys.executable,'-B',str(ROOT/'notes/engine-study/T108/check.py'),'--task',task,'--controls']
    old=subprocess.run(cmd,text=True,capture_output=True)
    assert old.returncode!=0 and 'FileNotFoundError' in old.stderr
    mock=pin({'task':task,'sections':['Mock one','Mock two','Mock three'],
              'candidates':[dict(id=i,minimal_input='MOCK',expected='MOCK',actual='MOCK',
                                 evidence=['0791:278A'],reachability='MOCK',follow_up='MOCK',
                                 disposition='unresolved') for i in ids]},['0791:278A'],source_commit=BASE)
    text='\n'.join('## '+s+'\n'+'mock '*100 for s in mock['sections'])
    validate(task,mock,text)
    results.append(dict(task=task,baseline_argv=cmd,baseline_exit=old.returncode,baseline_stderr=old.stderr,
                        mock='accepted; structural only',controls=controls(task,mock,text)))
write_new(ROOT/'notes/engine-study/T108/readiness-v1.json',dict(scope=__doc__,source_commit=BASE,results=results))
print('PASS: two absent ledgers rejected, two structural mocks accepted, ten negative controls rejected')
