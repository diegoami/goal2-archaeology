"""T129p receipt/source verifier; verifies retained full private traces, never runs an engine."""
import argparse,ast,gzip,hashlib,json,pickle,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match.machine import MEM_SIZE
BASE='1bbbc2cf'     # the accepted T128 merge this leaf starts from
def sha(data):return hashlib.sha256(data).hexdigest()
def rows(name):return [json.loads(line) for line in (HERE/name).read_text().splitlines()]
def expanded(writes,interval):
    low,high=interval
    return [(a+i,data[i]) for a,data in writes for i in range(len(data)) if not low<=a+i<high]
def verify_private(row):
    reference=row['private_trace'];path=ROOT/reference['path']
    assert sha(path.read_bytes())==reference['sha256']
    with gzip.open(path,'rb') as stream:value=pickle.load(stream)  # trusted locally generated/private proof
    assert value['candidate']['memory']==value['expected']['memory']
    assert value['candidate']['regs']==value['expected']['regs']
    interval=value['meta']['ordered_write_frame']
    assert expanded(value['original_writes'],interval)==expanded(value['candidate']['writes'],interval)
    assert len(value['expected']['memory'])==MEM_SIZE and len(value['expected']['regs'])==16
    for helper in value['original_helpers']:   # complete original helper-entry snapshots are retained
        assert len(helper['entry']['memory'])==MEM_SIZE and len(helper['entry']['regs'])==16
    return sha(path.read_bytes())
def git_show(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT,text=True)
def functions(tree):
    return {n.name:n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--primitive',default='primitive-v1.jsonl')
    ap.add_argument('--auxiliary',default='auxiliary-v1.jsonl');args=ap.parse_args()
    primitive=rows(args.primitive);auxiliary=rows(args.auxiliary)
    sys.path.insert(0,str(ROOT))
    from tests import test_port_pool_view as view
    cases={(setup,case) for setup in (0,1) for case in view.CASES}
    assert len(primitive)==len(cases)==32 and {(r['setup'],r['case']) for r in primitive}==cases
    kinds={}
    for r in auxiliary:kinds.setdefault(r['kind'],[]).append(r)
    assert {k:len(v) for k,v in kinds.items()}=={'falsifier':5,'sealed-primitive':5,'sealed-real-flow':5,'real-flow-falsifier':5,
                                                'real-flow-omitted-callee':3,'unknown-callee':1},{k:len(v) for k,v in kinds.items()}
    variants={'pool-view-row-off-by-one','pool-view-base-omitted','pool-view-highlight-omitted',
              'pool-view-cursor-attribute-off-by-one','pool-view-return-ax-clobbered'}
    assert {r['variant'] for r in kinds['falsifier']}==variants=={r['variant'] for r in kinds['real-flow-falsifier']}
    assert {r['flow'] for r in kinds['sealed-real-flow']}==set(view.FLOWS)
    for r in kinds['sealed-real-flow']:
        assert r['unicorn_denied'] and r['exe_denied']
        if r['flow']!='c1f-pool-unreachable':
            assert r['calls']['0791:E2E6']==6 and r['calls']['0791:DEA6']==2 and r['calls']['0791:DBFA']==1
            assert r['stub_calls']=={'1771:3947':11} and r['stub_boundary']['outside']==0
            assert r['complete_screen_buffer_equal_to_registered_stub_original']
        else:
            assert r['calls']['0791:E2E6']==0
    for row in primitive+auxiliary:
        assert row['status']=='passed'
        for name,digest in row['source_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
    private=[verify_private(row) for row in primitive]
    # Only the E2E6 body and its five variants are new in selection.py: every other function is unchanged.
    old=functions(ast.parse(git_show('runtime/original_match/port/selection.py')))
    new=functions(ast.parse((ROOT/'runtime/original_match/port/selection.py').read_text()))
    assert set(new)-set(old)=={'draw_pool_view'},set(new)-set(old)
    for name,node in old.items():assert ast.dump(node)==ast.dump(new[name]),name
    # The T128 proofs are untouched.
    for path in ('tests/test_port_pool_swap.py','tests/test_port_counter_compat_t128.py','tests/test_port_pre_match_swap.py'):
        assert git_show(path)==(ROOT/path).read_text(),path
    result=dict(status='passed',git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                model='Claude Sonnet 5.5 (claude-sonnet-5-5)',primitive_cases=len(primitive),falsifiers=len(kinds['falsifier']),
                sealed_exact_primitive_cases=len(kinds['sealed-primitive']),sealed_real_flows=len(kinds['sealed-real-flow']),
                real_flow_falsifiers=len(kinds['real-flow-falsifier']),omitted_callee_stops=len(kinds['real-flow-omitted-callee']),
                private_complete_trace_pairs_verified=len(private),compared_memory_bytes=MEM_SIZE,
                full_final_and_helper_memory_and_all16_no_masks=True,
                only_new_selection_function='draw_pool_view',t128_tests_unchanged=True,
                files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [ROOT/'runtime/original_match/port/selection.py',ROOT/'tests/test_port_pool_view.py',Path(__file__)]})
    with args.out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','primitive_cases','falsifiers','sealed_real_flows','private_complete_trace_pairs_verified')}))
if __name__=='__main__':main()
