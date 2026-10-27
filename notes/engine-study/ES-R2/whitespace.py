#!/usr/bin/env python3
"""Check committed milestone whitespace; exempt generated TSV and immutable raw .log output."""
import argparse,json,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]


def command(previous='m5-engine-study-foundations',head='HEAD'):
    return ['git','diff','--check',previous,head,'--','.',':(exclude)static/goal-exe/named/index.tsv',':(exclude)**/*.log']


def negative():
    with tempfile.TemporaryDirectory(prefix='es-r2-whitespace-') as name:
        root=Path(name)
        def run(args):return subprocess.run(args,cwd=root,capture_output=True,text=True)
        assert run(['git','init','-q']).returncode==0
        def commit(text,message):
            (root/'sample.py').write_text(text);assert run(['git','add','sample.py']).returncode==0
            assert run(['git','-c','user.name=validation','-c','user.email=fixture@example.invalid','commit','-qm',message]).returncode==0
            return run(['git','rev-parse','HEAD']).stdout.strip()
        first=commit('x = 1\n','clean fixture');bad=commit('x = 1  \n','committed whitespace defect')
        old=run(['git','diff','--check']);new=run(['git','diff','--check',first,bad])
        assert old.returncode==0 and new.returncode!=0 and 'trailing whitespace' in new.stdout
        return dict(scope='independent temporary fixture repository; no project worktree',old_clean_worktree_exit=old.returncode,committed_range_exit=new.returncode,range_stdout=new.stdout)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--receipt',type=Path);a=ap.parse_args();cmd=command();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
    data=dict(scope=__doc__,argv=cmd,exit=p.returncode,stdout=p.stdout,stderr=p.stderr)
    if a.controls:data['negative_control']=negative()
    if a.receipt:
        with a.receipt.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    if p.returncode:raise SystemExit(p.stdout+p.stderr)
    print('PASS: committed milestone range whitespace; generated TSV and immutable raw logs excluded'+('; committed-defect control rejected' if a.controls else ''))


if __name__=='__main__':main()
