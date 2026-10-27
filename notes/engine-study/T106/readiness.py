#!/usr/bin/env python3
"""Absent-result rejection and explicitly labelled structural mocks; no game execution."""
import subprocess,sys
from check import ROOT,GROUPS,validate,controls,write_new,sha
rows=[]
for task,cases in GROUPS.items():
    argv=[sys.executable,'-B','notes/engine-study/T106/check.py','--task',task,'--controls']
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True);assert p.returncode and 'FileNotFoundError' in p.stderr
    mock=dict(task=task,mock=True,method='LABELLED MOCK ONLY',limits=['not a native/port observation'],source_sha256={'MOCK':'MOCK'},budget={'invocations':1,'cpu_s':0,'active_wall_s':0},cases=[dict(id=c,manifest_sha256='MOCK',records=[{'path':'MOCK','sha256':'MOCK'}],prediction={'MOCK':1},field_match=True,strict_memory_equal=True,abi_equal=True,completed=True,disposition='exact',controls=['MOCK'],limits=['MOCK']) for c in cases])
    validate(task,mock,allow_mock=True)
    try:validate(task,mock)
    except AssertionError:rejected=True
    else:raise AssertionError('mock accepted as measurement')
    rows.append(dict(task=task,argv=argv,absent_exit=p.returncode,absent_stderr=p.stderr,structural_mock='accepted with explicit readiness-only switch',mock_as_measurement='rejected',controls=controls(task,mock,allow_mock=True)))
write_new(ROOT/'notes/engine-study/T106/readiness-v1.json',dict(scope=__doc__,results=rows,checker_sha256=sha((ROOT/'notes/engine-study/T106/check.py').read_bytes())))
print('PASS: three absent results rejected;three labelled structural mocks accepted;three mocks rejected as measurements;18 negatives rejected')
