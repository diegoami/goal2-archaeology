#!/usr/bin/env python3
"""Absent-design rejection and labelled structural mock acceptance, not scientific proof."""
import subprocess,sys
from check import ROOT,BASE,TOPICS,pin,sha,write_new,validate,controls
rows=[]
for task,topics in TOPICS.items():
    argv=[sys.executable,'-B',str(ROOT/'notes/engine-study/T105/check.py'),'--task',task,'--controls']
    p=subprocess.run(argv,capture_output=True,text=True);assert p.returncode and 'FileNotFoundError' in p.stderr
    mock=pin(dict(task=task,sections=['Mock1','Mock2','Mock3'],decisions=[dict(topic=t,decision='MOCK',why='MOCK',limits='MOCK') for t in topics],examples=[dict(inputs='MOCK',expected='MOCK',limits='MOCK')]*2,calculations={'controls':{'MOCK':'labelled'}}),['0791:F1F6'],source_commit=BASE)
    text='\n'.join('## '+s+'\n'+'mock '*150 for s in mock['sections']);validate(task,mock,text)
    rows.append(dict(task=task,argv=argv,absent_exit=p.returncode,absent_stderr=p.stderr,mock='accepted; structural only',controls=controls(task,mock,text)))
write_new(ROOT/'notes/engine-study/T105/readiness-v1.json',dict(scope=__doc__,results=rows,checker_sha256=sha((ROOT/'notes/engine-study/T105/check.py').read_bytes())))
print('PASS: two absent designs rejected; two structural mocks accepted; ten negative controls rejected')
