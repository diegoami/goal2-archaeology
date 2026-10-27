#!/usr/bin/env python3
"""Current source-study checks; no new engine/probe/match execution. Full CI is separate."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE='0fd699cdb3f675c38a26910cf0f79aa6eba707f8'
PREVIOUS='m5-engine-study-foundations'
SLICES=[
 ('T101a','T101','posts',1,'positioning'),('T101b','T101','marking',1,'marking'),('T101c','T101','movement',1,'movement'),
 ('T102a','T102','receivers',2,'possession'),('T102b','T102','flight',1,'ball-play'),('T102c','T102','resolution',1,'scoring'),
 ('T103a','T103','controls',1,'tactics'),('T103b','T103','lineups',1,'lineup-policy'),('T103c','T103','computer',1,'computer-policy'),
 ('T104a','T104','set_pieces',1,'restarts'),('T104b','T104','discipline',1,'discipline'),('T104c','T104','substitutions',2,'substitutions'),('T104d','T104','shootouts',1,'shootouts'),('T104e','T104','postmatch',1,'lifecycle'),
 ('T105a','T105','design',1,'experiment-design'),('T105b','T105','budget',1,'experiment-budget'),
 ('T108a','T108','arithmetic',1,'audit-arithmetic'),('T108b','T108','records',1,'audit-records')]


def sha(raw):return hashlib.sha256(raw).hexdigest()

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def matrix():
    commands=[]
    for task,folder,script,version,chapter in SLICES:
        commands.append([sys.executable,'-B',f'notes/engine-study/{folder}/{script}.py','--check'])
        commands.append(['tools/heavy.sh','ES-R2-'+task,'--',sys.executable,'-B',f'notes/engine-study/{folder}/check.py','--task',task,'--controls'])
    commands += [[sys.executable,'-B','notes/engine-study/T97/make_transient.py','--check'],
                 ['tools/heavy.sh','ES-R2-T97b','--',sys.executable,'-B','notes/engine-study/foundations/check.py','--task','T97b','--controls'],
                 [sys.executable,'-B','notes/engine-study/T97/check_snapshot_restores.py','--ledger','notes/engine-study/T97/transient-v4.json','--controls'],
                 [sys.executable,'tools/check_links.py'],['git','diff','--check']]
    return commands


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--receipt',type=Path);a=ap.parse_args()
    if a.receipt and a.receipt.exists():raise SystemExit('refuse to overwrite existing receipt')
    records=[]
    for argv in matrix():
        p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True)
        records.append(dict(argv=argv,exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
        print(('PASS' if p.returncode==0 else 'FAIL')+': '+' '.join(argv),flush=True)
        if p.returncode:raise SystemExit(json.dumps(records[-1],indent=2))
    changed=git('diff','--name-only',PREVIOUS,'HEAD','--','runtime/original_match','static/goal-exe/code','static/goal-exe/decompiled').decode().splitlines()
    assert not changed,('original/runtime source changed since accepted foundation',changed)
    prior_paths=[p for p in git('ls-tree','-r','--name-only',BASE,'--','notes/engine-study').decode().splitlines() if p.endswith(('.json','.txt'))]
    preserved=[]
    for path in prior_paths:
        commits=git('log','--reverse','--format=%H','--diff-filter=A',BASE,'--',path).decode().splitlines()
        assert commits,path
        first=git('show',f'{commits[0]}:{path}');current=(ROOT/path).read_bytes()
        assert first==current,('prior output altered',path)
        preserved.append(dict(path=path,first_commit=commits[0],sha256=sha(current)))
    coverage=[];paths={'notes/engine-study/ES-R2/verify.py','docs/engine-study/README.md'};addresses=[]
    for task,folder,script,version,chapter in SLICES:
        path=f'notes/engine-study/{folder}/{task}-v{version}.json';data=json.loads((ROOT/path).read_text())
        rows=data.get('routines',[]);addresses.extend(r['address'] for r in rows)
        coverage.append(dict(task=task,ledger=path,routines=len(rows),examples=len(data.get('examples',[])),audit_candidates=len(data.get('candidates',[])),calculation_controls=len(data['calculations'].get('controls',{}))))
        paths.update([path,f'notes/engine-study/{folder}/{script}.py',f'notes/engine-study/{folder}/check.py',f'docs/engine-study/{chapter}.md'])
        paths.update(data['source_sha256']);paths.update(data.get('supporting_artifacts',{}))
        own=data.get('analysis_sha256',{})
        if isinstance(own,dict):paths.update(own)
    assert len(addresses)==len(set(addresses))==201
    totals={key:sum(r[key] for r in coverage) for key in ['routines','examples','audit_candidates','calculation_controls']}
    data=dict(scope=__doc__,validation_baseline=BASE,execution_head=git('rev-parse','HEAD').decode().strip(),previous_milestone=PREVIOUS,python=sys.version,python_executable=sys.executable,checks=records,
              coverage=coverage,totals=totals,original_runtime_raw_source_changes=changed,immutable_previous_outputs=preserved,
              current_input_sha256={p:sha((ROOT/p).read_bytes()) for p in sorted(paths)},
              limits=['Integrity/calculation checks are not semantic,natural-reach or match-effect proof.','Historical m5 strict-source receipts remain at their accepted checkout; named annotations changed in T114-T116.','New field study pins a42c2cbe; current engine/raw original unchanged.','Full static/unit CI including six slow modules is required separately on the exact merged candidate.','No T106/T107 research execution or independent reviewer is launched by this command.'])
    if a.receipt:
        a.receipt.parent.mkdir(parents=True,exist_ok=True)
        with a.receipt.open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps(dict(checks=len(records),passed=len(records),totals=totals,previous_outputs_preserved=len(preserved),receipt=str(a.receipt) if a.receipt else None),indent=2))


if __name__=='__main__':main()
