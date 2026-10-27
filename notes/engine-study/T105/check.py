#!/usr/bin/env python3
"""Experiment preregistration completeness/provenance; not causal validity or executed readiness."""
import argparse,copy,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study'))
from foundations.check import pin,sha,write_new
BASE='a42c2cbe91300c8ee261b82fa993e665ed3f3325'
TOPICS={'T105a':'provenance interventions seed-boundary instrumentation probes batch controls deferrals'.split(),
        'T105b':'seed-blocks estimands uncertainty multiplicity stopping compute reproducibility completion'.split()}
VERSIONS={'T105a':2,'T105b':2}
CHAPTERS={'T105a':'experiment-design','T105b':'experiment-budget'}


def validate(task,data,text):
    assert data['task']==task and data['source_commit']==BASE
    assert {r['topic'] for r in data['decisions']}==set(TOPICS[task]) and len(data['decisions'])==8
    assert all(all(r.get(k) for k in ['decision','why','limits']) for r in data['decisions'])
    assert len(text.split())>=350 and len(data['sections'])>=3
    assert all('## '+s in text for s in data['sections'])
    assert len(data['examples'])>=2 and all(e.get('inputs') and e.get('expected') is not None and e.get('limits') for e in data['examples'])
    assert data['calculations']['controls'] and data['source_sha256'] and data['locations']
    for path,digest in data['source_sha256'].items():
        raw=(ROOT/path).read_bytes();assert sha(raw)==digest
        assert raw==subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT)
    for loc in data['locations']:
        line=(ROOT/loc['file']).read_text().splitlines()[loc['line']-1]
        assert loc['address'] in line and sha(line.encode())==loc['heading_sha256']


def controls(task,data,text):
    results={}
    for case in ['missing-topic','missing-source','shifted-source','missing-expectation','missing-controls']:
        broken=copy.deepcopy(data)
        if case=='missing-topic':broken['decisions'].pop()
        elif case=='missing-source':broken['source_sha256']={}
        elif case=='shifted-source':broken['locations'][0]['line']+=1
        elif case=='missing-expectation':broken['examples'][0].pop('expected')
        else:broken['calculations']['controls']={}
        try:validate(task,broken,text)
        except (AssertionError,KeyError):results[case]='rejected'
        else:raise AssertionError('escaped '+case)
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--task',choices=TOPICS,required=True);ap.add_argument('--controls',action='store_true');ap.add_argument('--receipt',type=Path);a=ap.parse_args()
    path=ROOT/f'notes/engine-study/T105/{a.task}-v{VERSIONS[a.task]}.json';data=json.loads(path.read_text());text=(ROOT/f'docs/engine-study/{CHAPTERS[a.task]}.md').read_text();validate(a.task,data,text)
    result=dict(task=a.task,scope=__doc__,positive='accepted',topics=len(data['decisions']),manifest_sha256=sha(path.read_bytes()))
    if a.controls:result['controls']=controls(a.task,data,text)
    if a.receipt:write_new(a.receipt,result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
