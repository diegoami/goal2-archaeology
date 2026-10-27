#!/usr/bin/env python3
"""Absent-ledger and labelled structural mocks only; no candidate finding or engine execution."""
import argparse,subprocess,sys,tempfile
from pathlib import Path
from check import ROOT,CANDIDATES,pin,validate,controls,instruction,write_new


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    path='static/goal-exe/code/seg_0791_14.asm';text=(ROOT/path).read_text()
    guards=[dict(path=path,address=off,instruction=instruction(text,off)) for off in ['8889','888A','888C','888F','8894','8896']]
    rows=[];chapter='\n'.join('## '+s+'\n'+'mock '*100 for s in ['One','Two','Three'])
    for task,ids in CANDIDATES.items():
        cmd=[sys.executable,'-B',str(ROOT/'notes/engine-study/T109/check.py'),'--task',task,'--controls']
        baseline=subprocess.run(cmd,capture_output=True,text=True);assert baseline.returncode!=0 and 'FileNotFoundError' in baseline.stderr
        mock=pin(dict(task=task,mock=True,method='MOCK:structural only',limits=['MOCK'],sections=['One','Two','Three'],
                      candidates=[dict(id=i,minimal_input='MOCK',expected='MOCK',actual='MOCK',evidence=[path],reachability='MOCK',limits=['MOCK'],follow_up='MOCK',disposition='unresolved') for i in ids]),[path],guards)
        validate(task,mock,chapter,allow_mock=True);negative=controls(task,mock,chapter,allow_mock=True)
        with tempfile.TemporaryDirectory(prefix='T109-labelled-mock-') as tmp:
            mock_path=Path(tmp)/'mock.json';write_new(mock_path,mock)
            rejected=subprocess.run(cmd+['--ledger',str(mock_path)],capture_output=True,text=True)
            assert rejected.returncode!=0 and 'structural mock is not research evidence' in rejected.stderr
        rows.append(dict(task=task,baseline_argv=cmd,baseline_exit=baseline.returncode,baseline_stderr=baseline.stderr,
                         mock='accepted only with allow_mock=True;not evidence',production_cli_mock_exit=rejected.returncode,
                         controls=negative))
    write_new(a.out,dict(scope=__doc__,results=rows));print('PASS:2 absent ledgers reject;2 labelled mocks accepted structurally;production mock CLI refuses;10structural+12listing negatives reject')


if __name__=='__main__':main()
