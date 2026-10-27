#!/usr/bin/env python3
"""Candidate/source integrity plus explicit literal-listing guards; not automatic attribution."""
import argparse,copy,hashlib,json,re,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE='f1d1767219569ab9b2c67a034012ee645f0d5e83'
CANDIDATES={
    'T109a':'launch-stack wall-flags launch-callers production-stubs'.split(),
    'T109b':'cache-reset side-bindings occupancy score-counters modes save-load manager-continuations legacy-offside coverage-gaps'.split(),
}
CHAPTERS={'T109a':'audit-boundaries','T109b':'audit-integration'}
DISPOSITIONS={'original quirk','intentional path difference','documentation/test defect','unsupported suspicion','unresolved','port defect'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def write_new(path,data):
    with Path(path).open('x') as f:json.dump(data,f,indent=2,sort_keys=True);f.write('\n')


def instruction(text,address):
    values=[m.group(1) for line in text.splitlines() if (m:=re.match(r'^'+re.escape(address)+r'\s+(?:[0-9A-F]{2} )+\s*(\S.*)$',line))]
    assert len(values)==1,(address,values)
    return values[0]


def check_guard(guard,text):assert instruction(text,guard['address'])==guard['instruction'],guard


def pin(data,sources,guards,support=()):
    data.update(source_commit=BASE,source_sha256={p:sha((ROOT/p).read_bytes()) for p in sorted(set(sources))},
                guards=guards,supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in sorted(set(support))})
    return data


def validate(task,data,text,*,allow_mock=False):
    assert data['task']==task and data['source_commit']==BASE
    assert allow_mock or not data.get('mock'),'structural mock is not research evidence'
    assert len(data['candidates'])==len(CANDIDATES[task]) and {r['id'] for r in data['candidates']}==set(CANDIDATES[task])
    assert data['method'] and data['limits'] and data['source_sha256'] and len(data['guards'])>=6
    assert len(text.split())>=250 and len(data['sections'])>=3
    assert all('## '+s in text for s in data['sections'])
    for path,digest in data['source_sha256'].items():
        live=(ROOT/path).read_bytes();historical=subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
        assert sha(live)==digest and live==historical,path
    for path,digest in data['supporting_artifacts'].items():assert sha((ROOT/path).read_bytes())==digest,path
    for guard in data['guards']:
        assert guard['path'] in data['source_sha256'];check_guard(guard,(ROOT/guard['path']).read_text())
    for row in data['candidates']:
        assert all(row.get(k) for k in ['minimal_input','expected','actual','evidence','reachability','limits','follow_up'])
        assert row['disposition'] in DISPOSITIONS
        assert all(p in data['source_sha256'] or p in data['supporting_artifacts'] for p in row['evidence'])
        if row['disposition']=='port defect':assert row['independent_reproduction']
    if not allow_mock:
        producer=data['producer'];raw=subprocess.check_output(['git','show',producer['commit']+':'+producer['path']],cwd=ROOT)
        assert sha(raw)==producer['sha256']


def controls(task,data,text,*,allow_mock=False):
    result={}
    for name in ['missing-candidate','missing-evidence','missing-source','missing-limit','mock-as-evidence']:
        bad=copy.deepcopy(data)
        if name=='missing-candidate':bad['candidates'].pop()
        elif name=='missing-evidence':bad['candidates'][0]['evidence']=[]
        elif name=='missing-source':bad['source_sha256']={}
        elif name=='missing-limit':bad['candidates'][0]['limits']=[]
        else:bad['mock']=True
        try:validate(task,bad,text,allow_mock=False if name=='mock-as-evidence' else allow_mock)
        except (AssertionError,KeyError):result[name]='rejected'
        else:raise AssertionError('negative escaped: '+name)
    negatives=[]
    for guard in data['guards']:
        text_source=(ROOT/guard['path']).read_text();line=next(s for s in text_source.splitlines() if s.startswith(guard['address']+' '))
        altered=text_source.replace(line,line[:line.index(guard['instruction'])]+'nop',1)
        try:check_guard(guard,altered)
        except AssertionError:negatives.append(dict(path=guard['path'],address=guard['address'],result='altered listing rejected'))
        else:raise AssertionError('altered listing escaped')
    result['literal_listing_negatives']=negatives
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--task',choices=CANDIDATES,required=True);ap.add_argument('--controls',action='store_true');ap.add_argument('--ledger',type=Path);ap.add_argument('--receipt',type=Path);a=ap.parse_args()
    path=a.ledger or ROOT/f'notes/engine-study/T109/{a.task}-v1.json';data=json.loads(path.read_text())
    assert not data.get('mock'),'structural mock is not research evidence'
    text=(ROOT/f'docs/engine-study/{CHAPTERS[a.task]}.md').read_text();validate(a.task,data,text)
    result=dict(task=a.task,candidates=len(data['candidates']),ledger_sha256=sha(path.read_bytes()),scope=__doc__)
    if a.controls:result['controls']=controls(a.task,data,text)
    if a.receipt:write_new(a.receipt,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
