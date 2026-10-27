#!/usr/bin/env python3
"""Recompute launch results from immutable native/production-port observations; no execution."""
import argparse,json,sys,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check import ROOT,sha,write_new
from runner import Budget
EXPECTED={
 'launch-zero':{'velocity':[0,-1],'timer':2,'event':6,'projected':[0,-2]},
 'launch-small':{'velocity':[1,-1],'timer':2,'event':6,'projected':[2,-2]},
 'launch-diagonal':{'velocity':[1,2],'timer':7,'event':7,'projected':[7,14]},
}


def build(analysis_commit=None):
    folder=Path(__file__).resolve().parent
    manifests=sorted(folder.glob('manifest-v*.json'));assert manifests,'input manifest absent'
    manifest_path=manifests[-1];manifest=json.loads(manifest_path.read_text());digest=sha(manifest_path.read_bytes())
    comparisons=list((folder/'out').glob('*-comparisons.json'));matching=[json.loads(p.read_text()) for p in comparisons if json.loads(p.read_text())['manifest_sha256']==digest]
    assert len(matching)==1,'one complete comparison batch required';comp=matching[0]['comparisons']
    raw={}
    for p in (folder/'out').glob('*.json'):
        d=json.loads(p.read_text())
        if d.get('manifest_sha256')==digest and 'spec' in d:
            assert d['completed'] and d['process_exit']==0
            assert not d['native_instruction_attempts']
            raw[d['logical']]=(p,d)
    assert len(raw)==12
    for item in manifest['invocations']:assert item['spec']['logical'] in raw
    for case in EXPECTED:
        for backend in ['original','port']:
            p,d=raw[case+'/baseline/'+backend];assert d['observed']==EXPECTED[case]
            if backend=='port':assert d['port_entries'] and d['spec']['routine'] in d['port_entries']
    for backend in ['original','port']:
        assert raw['launch-zero/energy16/'+backend][1]['observed']==raw['launch-zero/baseline/'+backend][1]['observed']
    for case in ['launch-small','launch-diagonal']:
        baseline=raw[case+'/baseline/original'][1]['observed'];changed=raw[case+'/reverse-x/port'][1]['observed']
        assert changed!=baseline and changed['velocity'][0]==-baseline['velocity'][0]
    for case,backend in [('launch-zero','original'),('launch-diagonal','port')]:
        before=raw[case+'/baseline/'+backend][1];repeat=raw[case+'/repeat/'+backend][1]
        assert before['observed']==repeat['observed'] and before['full_memory_sha256']==repeat['full_memory_sha256'] and before['registers']==repeat['registers']
    # These are observation-backed rejected hypotheses,not executed source/engine mutations.
    assert raw['launch-zero/baseline/original'][1]['observed']['velocity']!=[0,0]
    assert raw['launch-diagonal/baseline/original'][1]['observed']['timer']!=10
    batches=[json.loads(p.read_text()) for p in (folder/'out').glob('*-batch.json') if json.loads(p.read_text())['manifest_sha256']==digest]
    assert len(batches)==1 and not batches[0]['error']
    historical_budget=batches[0]['budget']
    analysis_commit=analysis_commit or subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
    sources=dict(manifest['source_sha256']);sources[str(Path(__file__).resolve().relative_to(ROOT))]=sha(Path(__file__).read_bytes())
    rows=[]
    for case,prediction in EXPECTED.items():
        pair=next(c for c in comp if c['case']==case)
        rows.append(dict(id=case,manifest_sha256=digest,records=[pair['original_record'],pair['port_record']],prediction=prediction,field_match=True,strict_memory_equal=pair['memory_equal'],abi_equal=pair['abi_equal'],completed=True,disposition='exact' if pair['memory_equal'] and pair['abi_equal'] else 'state disagreement',strict_comparison=pair,controls=['observation-backed no-effect/mutant/repeat checks as declared;zero-idle/universal-half hypotheses rejected by native data'],limits=['Synthetic direct-call geometry;not natural incidence or whole-match fidelity.','Any byte/ABI disagreement is retained,not masked. Production sound stub is observed metadata,not automatic causal attribution.']))
    return dict(task='T106a',method='Native original versus actual registered production ports on committed identical synthetic inputs;no helper response stubbing;all memory compared',limits=['DeclaredT73sound stub214B:1EA1 may be reached;not claimed as native-body execution.','Scratch register/flag differences are listed separately from declared ABI.'],source_sha256=sources,source_commits={name:(analysis_commit if name==str(Path(__file__).resolve().relative_to(ROOT)) else manifest['construction_commit']) for name in sources},analysis_commit=analysis_commit,budget=historical_budget,cases=rows,control_outcomes={'energy_no_effect':'passed in both backends','reverse_x_real_variants':'both rejected against original baseline','fixed_repeats':'exact register/full-memory repetition','wrong_geometry_hypotheses':'rejected by original observations'})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args();path=a.out or ROOT/'notes/engine-study/T106/T106a-v2.json'
    previous=json.loads(path.read_text()) if a.check else None
    data=build(previous['analysis_commit'] if previous else None)
    if a.check:assert previous==data;print('PASS: three launch predictions;native-backed controls/repeats;unmasked state comparisons;budget')
    else:write_new(path,data);print('wrote immutable launch result ledger;no engine calls')


if __name__=='__main__':main()
