"""Provenance and exclusive output for design-only ledgers; no engine execution."""
import argparse,json,re
from pathlib import Path
from check import ROOT,BASE,pin,sha,write_new


def ledger(task,script,sections,decisions,examples,calculations,addresses,sources,artifacts=()):
    listings=[]
    for path in (ROOT/'static/goal-exe/code').glob('*.asm'):
        if set(re.findall(r'^; ---- routine (\S+)',path.read_text(),re.M))&set(addresses):listings.append(str(path.relative_to(ROOT)))
    data=dict(task=task,status='proposed preregistration; no measurements authorised before accepted ES-R2',method='Source/API reading and retained-record arithmetic only; no engine or match execution',sections=sections,decisions=decisions,examples=examples,calculations=calculations,
              analysis_sha256={str(Path(script).relative_to(ROOT)):sha(Path(script).read_bytes()),'notes/engine-study/T105/common.py':sha(Path(__file__).read_bytes())},supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in artifacts})
    return pin(data,addresses,sorted(set(sources+listings)),source_commit=BASE)


def run(task,builder):
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();data=builder();path=ROOT/f'notes/engine-study/T105/{task}-v1.json'
    if a.check:
        assert json.loads(path.read_text())==data
        print(f'PASS: {task}, eight design topics,{len(data["examples"])} literal examples,{len(data["calculations"]["controls"])} altered-design controls; source pins match; no engine execution')
    else:write_new(path,data);print('wrote immutable design ledger; no engine execution')
