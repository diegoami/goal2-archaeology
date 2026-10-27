#!/usr/bin/env python3
"""T106 record/completeness integrity; field, ABI and full-state results stay separate."""
import argparse,copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
GROUPS={'T106a':['launch-zero','launch-small','launch-diagonal'],
        'T106b':['wall-near','wall-far-positive','wall-far-negative'],
        'T106c':['launch-zero','launch-small','launch-diagonal','wall-near','wall-far-positive','wall-far-negative']}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def write_new(path,data):
    with Path(path).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')

def validate(task,data,*,allow_mock=False):
    assert data['task']==task
    assert allow_mock or data.get('mock') is not True,'mock is not measurement'
    rows=data['cases'];assert len(rows)==len(GROUPS[task]) and {r['id'] for r in rows}==set(GROUPS[task])
    assert data['method'] and data['limits'] and data['source_sha256']
    for r in rows:
        assert r['manifest_sha256'] and r['records'] and r['prediction']
        expected_records=2 if r['id'].startswith('launch-') else 10
        assert len(r['records'])==expected_records
        assert len({rec['path'] for rec in r['records']})==expected_records
        assert isinstance(r['field_match'],bool) and isinstance(r['strict_memory_equal'],bool)
        assert r['completed'] is True
        assert r['disposition'] in ['exact','state disagreement','field disagreement']
        assert r['disposition']!='exact' or (r['field_match'] and r['strict_memory_equal'] and r['abi_equal'])
        assert r['controls'] and r['limits']
    budget=data['budget'];assert 0<budget['invocations']<=60 and 0<=budget['cpu_s']<=600 and 0<=budget['active_wall_s']<=900
    if not allow_mock:
        for name,digest in data['source_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
        for row in rows:
            for rec in row['records']:
                assert sha((ROOT/rec['path']).read_bytes())==rec['sha256'],rec['path']


def controls(task,data,*,allow_mock=False):
    out={}
    for name in ['missing-case','missing-source','missing-input','missing-completion','missing-budget','missing-record','false-exact']:
        bad=copy.deepcopy(data)
        if name=='missing-case':bad['cases'].pop()
        elif name=='missing-source':bad['source_sha256']={}
        elif name=='missing-input':bad['cases'][0]['manifest_sha256']=''
        elif name=='missing-completion':bad['cases'][0]['completed']=False
        elif name=='missing-budget':bad['budget']={}
        elif name=='missing-record':bad['cases'][0]['records'].pop()
        else:bad['cases'][0].update(strict_memory_equal=False,disposition='exact')
        try:validate(task,bad,allow_mock=allow_mock)
        except (AssertionError,KeyError):out[name]='rejected'
        else:raise AssertionError('negative escaped '+name)
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--task',choices=GROUPS,required=True);ap.add_argument('--controls',action='store_true');ap.add_argument('--ledger',type=Path);ap.add_argument('--receipt',type=Path);a=ap.parse_args()
    path=a.ledger or ROOT/f'notes/engine-study/T106/{a.task}-v1.json';data=json.loads(path.read_text());validate(a.task,data)
    result=dict(task=a.task,scope=__doc__,positive='accepted',cases=len(data['cases']),ledger_sha256=sha(path.read_bytes()))
    if a.controls:result['controls']=controls(a.task,data)
    if a.receipt:write_new(a.receipt,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
