#!/usr/bin/env python3
"""Recompute current probe/integration evidence without new engine calls; full CI is separate."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREVIOUS='m6-engine-study-field-behaviour'
STUDY_BASE='f057b4b1d62794a544208ee25e12a2479473657b'


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def matrix():
    commands=[]
    for slice in ['launch','wall']:
        commands.append([sys.executable,'-B',f'notes/engine-study/T106/{slice}/analyse.py','--check'])
    commands.append([sys.executable,'-B','notes/engine-study/T106/analysis.py','--check'])
    for task in ['T106a','T106b','T106c']:
        commands.append(['tools/heavy.sh','ES-R3-'+task,'--',sys.executable,'-B','notes/engine-study/T106/check.py','--task',task,'--controls'])
    commands.append([sys.executable,'-B','notes/engine-study/T106/runner.py','--audit'])
    commands.append([sys.executable,'-B','-m','unittest','discover','-s','notes/engine-study/T106','-p','test_software.py','-v'])
    for task,script in [('T109a','boundaries'),('T109b','integration')]:
        commands.append([sys.executable,'-B',f'notes/engine-study/T109/{script}.py','--check'])
        commands.append(['tools/heavy.sh','ES-R3-'+task,'--',sys.executable,'-B','notes/engine-study/T109/check.py','--task',task,'--controls'])
    commands += [[sys.executable,'-B','notes/engine-study/ES-R2/listing_guards.py'],
                 [sys.executable,'-B','notes/engine-study/ES-R2/whitespace.py','--controls'],
                 [sys.executable,'tools/check_links.py']]
    return commands


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path);a=ap.parse_args()
    if a.receipt and a.receipt.exists():raise SystemExit('refuse to overwrite existing receipt')
    head=git('rev-parse','HEAD').decode().strip();checks=[]
    for cmd in matrix():
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        checks.append(dict(argv=cmd,exit=p.returncode,stdout=p.stdout,stderr=p.stderr))
        print(('PASS' if p.returncode==0 else 'FAIL')+': '+' '.join(cmd),flush=True)
        if p.returncode:raise SystemExit(p.stderr or p.stdout)
    raw_changes=git('diff','--name-only',PREVIOUS,'HEAD','--','static/goal-exe/code','static/goal-exe/decompiled').decode().splitlines();assert not raw_changes
    runtime_paths=git('diff','--name-only',PREVIOUS,'HEAD','--','runtime/original_match').decode().splitlines()
    declared=git('diff','--name-only',PREVIOUS,STUDY_BASE,'--','runtime/original_match').decode().splitlines()
    assert runtime_paths==declared,'unaccounted runtime path changes after study start'
    runtime={p:sha(git('show',STUDY_BASE+':'+p)) for p in declared}
    for p,digest in runtime.items():assert sha((ROOT/p).read_bytes())==digest,p
    # Include every previously tracked JSON/TXT study artifact,including failed/obsolete versions.
    preserved=[]
    for p in git('ls-tree','-r','--name-only',head,'--','notes/engine-study').decode().splitlines():
        if not p.endswith(('.json','.txt')):continue
        first=git('log','--reverse','--format=%H','--diff-filter=A',head,'--',p).decode().splitlines()[0]
        raw=(ROOT/p).read_bytes();assert git('show',first+':'+p)==raw,('immutable artifact changed',p)
        preserved.append(dict(path=p,first_commit=first,sha256=sha(raw)))
    probes=json.loads((ROOT/'notes/engine-study/T106/report-v1.json').read_text())
    audits=[json.loads((ROOT/f'notes/engine-study/T109/T109{t}-v{v}.json').read_text()) for t,v in [('a',1),('b',2)]]
    inputs=['notes/engine-study/ES-R3/verify.py','docs/engine-study/README.md','docs/engine-study/micro-probes.md','docs/engine-study/audit-boundaries.md','docs/engine-study/audit-integration.md','docs/engine-study/t107-revision-proposal.md','notes/engine-study/T106/check.py','notes/engine-study/T106/analysis.py','notes/engine-study/T109/check.py','notes/engine-study/T109/boundaries.py','notes/engine-study/T109/integration.py']
    data=dict(scope=__doc__,execution_head=head,previous_milestone=PREVIOUS,declared_intervening_runtime_base=STUDY_BASE,
              python=sys.version,checks=checks,probe_summary=probes['summary'],actual_research_budget=probes['budget'],
              audit_candidates=sum(len(d['candidates']) for d in audits),new_literal_guards=sum(len(d['guards']) for d in audits),
              original_raw_source_changes=raw_changes,intervening_runtime_sha256=runtime,immutable_previous_outputs=preserved,
              current_input_sha256={p:sha((ROOT/p).read_bytes()) for p in inputs},
              limits=['15source/data/software commands,not15engine experiments. Existing ES-R2 listing guards are reused separately from45new audit guards.','Research cap counts48top-level calls;full-CIexisting regressions are a separate verification workload.','T107deferred;no scoring-effect interval or null result. No reviewer launched.','Full static/unit CI with all6slowmodules must pass separately on exact merged candidate.'])
    if a.receipt:write=a.receipt.open('x');json.dump(data,write,indent=2,sort_keys=True);write.write('\n');write.close()
    print(json.dumps(dict(checks=len(checks),preserved_outputs=len(preserved),probe_cases=6,audit_candidates=data['audit_candidates'],new_literal_guards=data['new_literal_guards'],research_invocations=probes['budget']['invocations']),indent=2))


if __name__=='__main__':main()
