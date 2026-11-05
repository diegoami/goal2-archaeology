"""Verify the native-record supplement without changing the original acceptance index."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
PRIOR='df447fc5310358c9ca746a6b9c4a5ed1c70d67bbc5fc8ddbb108ff9529df886e'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(out):
    prior=HERE/'final-audit/index.json';assert sha(prior)==PRIOR
    index=json.loads(prior.read_text())
    for path,value in index['sources'].items():assert sha(ROOT/path)==value,path
    data=HERE/'published-v1/results.jsonl';rows=[json.loads(line) for line in data.read_text().splitlines()]
    assert len(rows)==3 and len({r['asset'] for r in rows})==3
    for r in rows:
        assert r['status']=='passed' and r['input_type']=='native-published-record-population'
        assert r['record_arrays_retained'] and not r['active_manager_edited']
        assert r['source_image_sha256']==r['prepared_image_sha256']
        assert r['source_fields']==r['prepared_fields']
        assert all(not e['changed'] and e['before_sha256']==e['after_sha256'] for e in r['field_edits'])
        assert {e['field'] for e in r['field_edits']}=={'DS:0C1E','DS:0C1F'}
        assert r['full_memory_and_ALLREGS_match'] and r['summary']['0791:DC7E']['proved']==1
        assert not any(v['scratch'] for v in r['summary'].values())
        trace=r['strength_trace'];assert trace and len(trace)%2==0 and r['swap_args']
        assert all(e[0]=='call' for e in trace[::2])
        assert all(e[0]==('0791:DD6B' if i%2==0 else '0791:DD7F') for i,e in enumerate(trace[1::2]))
        counts=r['native_context_counts'];assert len(counts['current_position'])>1
        assert any(country!='0' for country in counts['affiliation'])
        assert r['after_fields']['records']['players']==r['source_fields']['records']['players']
        s=r['sealed'];assert s['fields']==r['after_fields']
        assert s['copy_isolated'] and s['tables_unchanged'] and s['unicorn_denied'] and s['exe_denied']
        assert s['result']['allowed'] and s['result']['refusal'] is None
        assert s['normalized_state_sha256']
        for path,value in r['source_hashes'].items():assert sha(ROOT/path)==value,path
    sources={path:sha(ROOT/path) for path in index['sources']}
    sources.update({str(p.relative_to(ROOT)):sha(p) for p in (HERE/'published.py',Path(__file__))})
    value={'schema':'t125-native-supplement-index/1','prior_index':{'path':str(prior.relative_to(ROOT)),'sha256':PRIOR},
      'prior_families':{'raw_function_domain_cases':48,'sealed_function_domain_cases':22,
         'classification':'Explicitly synthetic isolated-function inputs; player affiliation and homogeneous position fixtures are not valid whole-career populations.'},
      'native_cases':[{'asset':r['asset'],'asset_sha256':r['asset_sha256'],'manager':r['source_fields']['manager'],
         'country':r['source_fields']['country'],'source_image_sha256':r['source_image_sha256'],
         'strength_calls':len(r['strength_trace'])//2,'swaps':len(r['swap_args']),
         'actual_context_byte_changes':0,'record_arrays_retained':True} for r in rows],
      'scope':'Three hash-verified native published populations; original players/countries/pools/manager mapping retained. C1E/C1F preparation was declared but changed zero bytes. Active manager unchanged. Isolated DC7E entry ABI, not natural calendar or full E44F/52CC/menu workflow.',
      'raw_comparison':'Prover ordered LIVE/caller-visible writes and guest frame effects, plus independent complete native/port memory including final dead-frame bytes and ALLREGS. No ISA-level intermediate dead-stack chronology claim.',
      'sealed_comparison':'Full allocated record regions, squad/pool order, RNG/9B43, all canonical state/table deltas excluding strictly SS:2000..2FFF dead helper locals; copy/table purity and positive Unicorn/GOAL.EXE denial.',
      'receipt_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (data,HERE/'published-v1/run.log')},'sources':sources}
    with out.open('x') as f:f.write(json.dumps(value,indent=2,sort_keys=True)+'\n')
    print('PASS: prior acceptance index intact; 3 native published populations; context edits 0; original/port/sealed match')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();verify(a.out)
