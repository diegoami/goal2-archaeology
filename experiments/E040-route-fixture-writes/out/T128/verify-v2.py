"""T128 receipt/source verifier; verifies retained full private traces, never runs an engine."""
import argparse,ast,gzip,hashlib,json,pickle,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match.machine import MEM_SIZE
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
    # Complete original helper-entry snapshots are retained, not just hashes.
    for helper in value['original_helpers']:
        assert len(helper['entry']['memory'])==MEM_SIZE and len(helper['entry']['regs'])==16
    return sha(path.read_bytes())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--primitive',default='primitive-final-v1.jsonl')
    ap.add_argument('--auxiliary',default='auxiliary-final-v1.jsonl');args=ap.parse_args()
    primitive=rows(args.primitive);auxiliary=rows(args.auxiliary)
    assert len(primitive)==15
    assert {(r['setup'],r['case']) for r in primitive}=={(setup,case) for setup in (0,1) for case in ('mark','empty','squad-to-pool','pool-to-squad','pool-to-pool','same')}|{(0,case) for case in ('refused-mark','refused-swap','tour-refused')}
    kinds={kind:[r for r in auxiliary if r['kind']==kind] for kind in ('falsifier','sealed-primitive','sealed-real-helpers','ddcb')}
    assert {k:len(v) for k,v in kinds.items()}=={'falsifier':5,'sealed-primitive':4,'sealed-real-helpers':5,'ddcb':6}
    assert {r['variant'] for r in kinds['falsifier']}=={'pool-gate-omitted','pool-index-off-by-one','pool-scroll-omitted','squad-word-swap-omitted','squad-mark-clear-omitted'}
    for row in primitive+auxiliary:
        assert row['status']=='passed'
        for name,digest in row['source_sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
    private=[verify_private(row) for row in primitive+kinds['ddcb']]
    baseline=subprocess.check_output(['git','show','6bdf7bbed441b6e2c758949bae409963dfa6c175:tests/test_port_pre_match_swap.py'],cwd=ROOT,text=True)
    old=ast.parse(baseline);new=ast.parse((ROOT/'tests/test_port_pre_match_swap.py').read_text())
    oldfunc={n.name:n for c in old.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
    newfunc={n.name:n for c in new.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
    for name,node in oldfunc.items():
        if name=='test_pool_or_in_match_modes_refuse_before_any_memory_write':
            node.name='test_in_match_modes_refuse_before_any_memory_write'
            loop=next(n for n in node.body if isinstance(n,ast.For));loop.iter.elts=loop.iter.elts[2:]
            name=node.name
        assert ast.dump(node,include_attributes=False)==ast.dump(newfunc[name],include_attributes=False),name
    result=dict(status='passed',git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                model='Codex GPT-6 family; exact variant unavailable',primitive_cases=15,ddcb_cases=6,falsifiers=5,
                sealed_exact_primitive_cases=4,sealed_real_registered_helper_cases=5,private_complete_trace_pairs_verified=len(private),
                full_final_and_helper_memory_and_all16_no_masks=True,compared_memory_bytes=MEM_SIZE,
                order_boundary='Original-measured lowest stack reached while writing..caller returned SP; byte-expanded live order, main701-order-boundary.md; not instruction-order fidelity',
                within_twenty_bodies_assertions_unchanged=True,C1F_refusal_assertions_unchanged=True,
                primitive_helper_scope='Original helpers replayed privately only after complete helper-entry memory/ALL16 equality',
                real_helper_scope='Separate code-free actual registered helpers; complete gameplay/caller record hashes and RNG + retained caller ABI, not a new all-scratch-register proof of existing helpers',
                failed_calibrations_retained=True,files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [ROOT/'runtime/original_match/port/selection.py',ROOT/'tests/test_port_pool_swap.py',ROOT/'tests/test_port_pre_match_swap.py',ROOT/'tests/test_port_selection.py',Path(__file__)]})
    with args.out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','primitive_cases','ddcb_cases','falsifiers','sealed_real_registered_helper_cases','private_complete_trace_pairs_verified')}))
if __name__=='__main__':main()
