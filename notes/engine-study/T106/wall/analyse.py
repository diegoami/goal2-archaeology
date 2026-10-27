#!/usr/bin/env python3
"""Recompute wall geometry, guards and strict comparisons from immutable observations."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check import ROOT,sha,write_new

# Literal accepted T105a-v2 predictions, independent of the engine's implementation.
EXPECTED={
    'wall-near':dict(slots=list(range(18,23)),targets=[[2,30],[1,30],[0,30],[-1,30],[-2,30]]),
    'wall-far-positive':dict(slots=list(range(18,23)),targets=[[-3,-28],[-3,-27],[-3,-26],[-3,-25],[-3,-24]]),
    'wall-far-negative':dict(slots=list(range(7,12)),targets=[[-3,28],[-3,29],[-3,30],[-3,31],[-3,32]]),
}


def build(analysis_commit=None):
    folder=Path(__file__).resolve().parent;manifest_path=folder/'manifest-v1.json'
    manifest=json.loads(manifest_path.read_text());digest=sha(manifest_path.read_bytes())
    def matching(pattern):
        values=[json.loads(p.read_text()) for p in (folder/'out').glob(pattern)]
        result=[d for d in values if d['manifest_sha256']==digest];assert len(result)==1
        return result[0]
    comparisons=matching('*-comparisons.json')['comparisons'];batch=matching('*-batch.json')
    assert not batch['error'] and len(batch['records'])==36 and len(comparisons)==15
    raw={}
    for rec in batch['records']:
        p=ROOT/rec['path'];assert sha(p.read_bytes())==rec['sha256']
        d=json.loads(p.read_text());assert d['completed'] and d['process_exit']==0
        assert d['manifest_sha256']==digest and not d['native_instruction_attempts']
        assert not d['production_stub_entries'],'wall slice reaches no declared production stub'
        raw[d['logical']]=d
    assert len(raw)==36 and set(raw)=={i['spec']['logical'] for i in manifest['invocations']}
    for case,prediction in EXPECTED.items():
        for slot,target in zip(prediction['slots'],prediction['targets']):
            for backend in ['original','port']:
                d=raw[f'{case}/slot{slot}/{backend}'];assert d['observed']==dict(target=target,state=11)
                assert '0791:4B64' not in d['known_entry_events']
                if backend=='port':assert '0791:7621' in d['port_entries']
    guard_results={}
    for label in ['outside-slot6','forward-false']:
        original=raw[f'wall-near/{label}/original'];port=raw[f'wall-near/{label}/port']
        assert '0791:4B64' in original['known_entry_events'] and '0791:4B64' in port['port_entries']
        assert original['observed']==port['observed']
        assert original['observed']['target'] not in EXPECTED['wall-near']['targets']
        guard_results[label]=dict(observed=original['observed'],original_native_fallback_entry=True,
                                 production_port_fallback_entry=True,field_equal=True,
                                 full_memory_equal=original['full_memory_sha256']==port['full_memory_sha256'],
                                 abi_equal=original['abi_registers']==port['abi_registers'] and not ((original['registers']['eflags']^port['registers']['eflags'])&0x400))
    for case,slot,backend in [('wall-near',18,'original'),('wall-far-negative',11,'port')]:
        before=raw[f'{case}/slot{slot}/{backend}'];repeat=raw[f'{case}/repeat-slot{slot}/{backend}']
        assert before['observed']==repeat['observed'] and before['registers']==repeat['registers'] and before['full_memory_sha256']==repeat['full_memory_sha256']
    # Wrong alternatives are observation-backed hypotheses, not actual port mutants.
    assert raw['wall-near/slot18/original']['observed']['target']!=[-3,-28]
    assert all(raw[f'wall-far-positive/slot{s}/original']['observed']['target'][1]<0 for s in range(18,23))
    assert all(raw[f'wall-far-negative/slot{s}/original']['observed']['target'][0]==-3 for s in range(7,12))
    analysis_commit=analysis_commit or subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
    sources=manifest['source_sha256'];own=str(Path(__file__).resolve().relative_to(ROOT));sources[own]=sha(Path(__file__).read_bytes())
    rows=[]
    for case,prediction in EXPECTED.items():
        pairs=sorted([c for c in comparisons if c['case']==case],key=lambda c:c['slot'])
        assert [p['slot'] for p in pairs]==prediction['slots']
        memory_equal=all(p['memory_equal'] for p in pairs);abi_equal=all(p['abi_equal'] for p in pairs)
        rows.append(dict(id=case,manifest_sha256=digest,records=[r for p in pairs for r in [p['original_record'],p['port_record']]],
                         prediction=prediction,field_match=True,strict_memory_equal=memory_equal,abi_equal=abi_equal,completed=True,
                         disposition='exact' if memory_equal and abi_equal else 'state disagreement',strict_comparisons=pairs,
                         controls=['real original/port guard fallback witnesses;two fixed repeats;wrong boundary/sign/axis hypotheses rejected by native data'],
                         limits=['Five synthetic defending slots;not natural occurrence or whole-match fidelity.','Every memory byte compared;no normalisation/masks;full-register differences separate from declared ABI.']))
    return dict(task='T106b',method='Native original and actual registered production ports on identical hash-frozen synthetic inputs',
                limits=['Direct single-call geometry;not natural incidence.','Production callees only;native fallback refused in port arm;no sound/display stub reached.'],
                source_sha256=sources,source_commits={p:analysis_commit if p==own else manifest['construction_commit'] for p in sources},
                analysis_commit=analysis_commit,budget=batch['budget'],cases=rows,
                control_outcomes=dict(guards=guard_results,fixed_repeats='exact full-memory/register repetition',
                                      wrong_geometry_hypotheses='rejected by original observations;not executed engine mutants'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args()
    path=a.out or ROOT/'notes/engine-study/T106/T106b-v1.json';previous=json.loads(path.read_text()) if a.check else None
    data=build(previous['analysis_commit'] if previous else None)
    if a.check:assert data==previous;print('PASS:15wall targets per backend;native-backed guards/repeats;unmasked comparisons;frozen budget')
    else:write_new(path,data);print('wrote immutable wall result ledger;no engine calls')


if __name__=='__main__':main()
