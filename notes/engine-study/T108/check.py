#!/usr/bin/env python3
"""Audit candidate completeness and source integrity, not automatic defect attribution."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study'))
from foundations.check import pin,sha,write_new

BASE='a42c2cbe91300c8ee261b82fa993e665ed3f3325'
CANDIDATES={
    'T108a':'form-sentinel negative-leadership half-pitch-follow strict-edges'.split(),
    'T108b':'table-windows cache-and-identities uncaught-initial-direction existing-edge-coverage annotation-claims'.split(),
}
CHAPTERS={'T108a':'audit-arithmetic','T108b':'audit-records'}
DISPOSITIONS={'original quirk','port defect','documentation/test defect','unsupported suspicion','unresolved'}


def validate(task,data,text):
    assert data['task']==task and data['source_commit']==BASE
    rows=data['candidates']
    assert len(rows)==len(CANDIDATES[task]) and {r['id'] for r in rows}==set(CANDIDATES[task])
    locations={r['address'] for r in data['locations']}
    assert locations and data['source_sha256']
    for row in rows:
        assert all(row.get(k) for k in ['minimal_input','expected','actual','evidence','reachability','follow_up'])
        assert row['disposition'] in DISPOSITIONS
        assert all(e in locations or e in data['source_sha256'] for e in row['evidence'])
    assert len(data['sections'])>=3 and len(text.split())>=250
    assert all('## '+s in text for s in data['sections'])
    for path,digest in data['source_sha256'].items():
        raw=(ROOT/path).read_bytes()
        assert sha(raw)==digest and raw==subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path
    for loc in data['locations']:
        line=(ROOT/loc['file']).read_text().splitlines()[loc['line']-1]
        assert loc['address'] in line and sha(line.encode())==loc['heading_sha256']
    for path,digest in data.get('supporting_artifacts',{}).items():
        assert sha((ROOT/path).read_bytes())==digest,path


def controls(task,data,text):
    results={}
    for case in ['missing-candidate','missing-evidence','missing-disposition','missing-source','shifted-source']:
        broken=copy.deepcopy(data)
        if case=='missing-candidate':broken['candidates'].pop()
        elif case=='missing-evidence':broken['candidates'][0]['evidence']=[]
        elif case=='missing-disposition':broken['candidates'][0].pop('disposition')
        elif case=='missing-source':broken['source_sha256']={}
        else:broken['locations'][0]['line']+=1
        try:validate(task,broken,text)
        except (AssertionError,KeyError):results[case]='rejected'
        else:raise AssertionError('control escaped:'+case)
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--task',choices=CANDIDATES,required=True)
    ap.add_argument('--controls',action='store_true');ap.add_argument('--receipt',type=Path)
    args=ap.parse_args();path=ROOT/f'notes/engine-study/T108/{args.task}-v1.json'
    data=json.loads(path.read_text());text=(ROOT/f'docs/engine-study/{CHAPTERS[args.task]}.md').read_text()
    validate(args.task,data,text)
    result=dict(task=args.task,candidates=len(data['candidates']),manifest_sha256=sha(path.read_bytes()),
                checker_sha256=sha(Path(__file__).read_bytes()),positive='accepted',scope=__doc__)
    if args.controls:result['controls']=controls(args.task,data,text)
    if args.receipt:write_new(args.receipt,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
