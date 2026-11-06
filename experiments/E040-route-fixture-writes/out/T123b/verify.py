"""T123b acceptance index: immutable families, source hashes and normalized-state controls."""
import argparse,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'runtime'),str(HERE)]
def sha(data):return hashlib.sha256(data).hexdigest()
def rows(p):return [json.loads(line) for line in p.read_text().splitlines()]

def verify(out):
    raw=rows(HERE/'raw-v2/results.jsonl');sealed=rows(HERE/'sealed-v1/results.jsonl');natural=rows(HERE/'natural-v2/results.jsonl')
    assert len(raw)==10 and {(r['setup'],r['case']) for r in raw}=={(s,c) for s in (0,1) for c in ('mark','empty','same','swap','empty-outgoing')}
    for r in raw:
        assert r['status']=='passed' and r['proof']['0791:DEA6']['proved']==1
        assert not r['proof']['0791:DEA6']['scratch']
        calls=[e['call'] for e in r['actual_original_events'] if 'call' in e]
        after=r['after']['parent'];before=r['before']['parent']
        if r['case']=='mark':
            assert after['-1']==1 and after['-9']==before['-9'] and after['-7']==1 and after['-11']==0
            assert calls==['0791:DE27','0791:DE51','0791:DE27']
            assert r['after']['squad']==r['before']['squad']
        elif r['case']=='empty':
            assert after==before and r['after']['squad']==r['before']['squad']
            assert calls==['0791:DE27','0791:DE51']
        else:
            assert after['-1']==0 and after['-11']==0
            assert calls[:4]==['0791:DE27','0791:DE51','0791:DE51','214B:007B']
            expected='0791:230C' if r['setup'] else '1771:52CC'
            assert calls.count(expected)==1
            sort_reads=[e for e in r['actual_original_events'] if e.get('post_sort')==expected]
            assert len(sort_reads)==1 and sort_reads[0]['live_squad']==r['after']['squad']
        for p,h in r['source_hashes'].items():assert sha((ROOT/p).read_bytes())==h,p
    assert len(sealed)==16 and sum(r['unsupported'] for r in sealed)==6
    assert {(r['setup'],r['case']) for r in sealed}=={(s,c) for s in (0,1) for c in ('mark','empty','same','swap','empty-outgoing','pool-current','pool-marked','in-match')}
    for r in sealed:
        s=r['sealed'];assert r['status']=='passed' and s['unicorn_denied'] and s['exe_denied']
        assert s['state_unchanged'] and s['tables_unchanged']
        if r['unsupported']:assert s['unsupported'] and s['full_memory_unchanged'] and s['before_memory_sha256']==s['after_memory_sha256']
        for p,h in r['source_hashes'].items():assert sha((ROOT/p).read_bytes())==h,p
    falsifiers={}
    for name in ('squad-word-swap-omitted','squad-mark-clear-omitted'):
        rr=rows(HERE/'falsifiers-v1'/f'{name}.jsonl')
        assert len(rr)==2 and {r['setup'] for r in rr}=={0,1}
        assert all(r['status'].startswith('ProofError:') for r in rr)
        falsifiers[name]=[r['status'] for r in rr]
    header=natural[0]
    assert header['input_type']=='accepted original T124t continuation checkpoint; no record edits'
    source_receipt=ROOT/header['source_receipt'];assert sha(source_receipt.read_bytes())==header['source_receipt_sha256']
    accepted=rows(source_receipt);reference={r['round']:r for r in accepted if r.get('status')=='round'}
    cp=header['source_checkpoint'];assert cp==reference[1]['checkpoint']
    assert sha((ROOT/cp['path']).read_bytes())==cp['sha256']
    assert set(cp['context']['regs'])=={'EAX','EBX','ECX','EDX','ESI','EDI','EBP','ESP','EFLAGS','CS','DS','ES','SS','FS','GS','EIP'}
    nr=[r for r in natural if r.get('status')=='round'];assert [r['round'] for r in nr]==[2,3,4]
    assert natural[-1]['status']=='completed'
    leaf_frames=[]
    for r in nr:
        number=r['round'];assert r['end']==reference[number]['end']
        assert r['matches']==reference[number]['matches']
        assert r['teams']==reference[number]['teams']
        assert r['after_context']==reference[number]['checkpoint']['context']
        assert set(r['after_context']['regs'])==set(cp['context']['regs'])
        checkpoint=r['checkpoint'];assert sha((ROOT/checkpoint['path']).read_bytes())==checkpoint['sha256']
        assert checkpoint['sha256']==reference[number]['checkpoint']['sha256']
        for match in r['leaf_matches']:
            count=match['calls']['0791:DEA6'];p=match['proof']['0791:DEA6']
            assert p['proved']==count and p['before']==0 and not p['scratch']
            assert count==len(match['frames'])
            leaf_frames.extend(match['frames'])
    assert len(nr[0]['matches'])==9 and len(leaf_frames)==2
    assert [f['entry']['mark'] for f in leaf_frames]==[0,1]
    assert [f['after']['mark'] for f in leaf_frames]==[1,0]
    assert all(f['entry']['C1F']==0 and f['entry']['pane']==1 for f in leaf_frames)
    assert all(f['entry']['parent_bp']==f['entry']['regs']['EBP'] and f['entry']['parent_return_offset']==0xE99C for f in leaf_frames)
    assert all(f['after']['regs']['ESP']==f['entry']['regs']['ESP']+4 for f in leaf_frames)
    assert leaf_frames[1]['after']['marked_scroll']==0
    for p,h in header['source_hashes'].items():assert sha((ROOT/p).read_bytes())==h,p
    # Prove the normalized dead-stack exception cannot hide parent/RNG changes.
    import prove,sealed as S
    from original_match.image import Image
    from original_match.port.tables import load
    tables=load(ROOT/'static/goal-exe/tables');source,_=prove.source();m,_,_=prove.prepare(source,0,'mark')
    image=S.image_of(source,m,tables);baseline=S.normalize(image.state(tables));controls={}
    for name,address,changes in [('below',0x91FFF,True),('inside-first',0x92000,False),('inside-last',0x92FFF,False),
        ('above',0x93000,True),('caller-mark',0x93FFF,True),('rng',image.DS*16+0x7B62,True)]:
        old=image.memory[address];image.memory[address]^=1;value=S.normalize(image.state(tables));image.memory[address]=old
        assert (value!=baseline)==changes,name
        controls[name]={'linear':address,'baseline_sha256':baseline,'mutated_sha256':value,'detected':value!=baseline}
    paths=[ROOT/'runtime/original_match/port/selection.py',ROOT/'tests/test_port_pre_match_swap.py',ROOT/'tests/test_port_selection.py',HERE/'prove.py',HERE/'sealed.py',HERE/'continuation.py',Path(__file__)]
    index={'schema':'t123b-index/1','raw_cases':10,'sealed_cases':16,'unsupported_cases':6,'falsifiers':falsifiers,
      'natural_rounds':[r['end'] for r in nr],'natural_matches':len(nr[0]['matches']),'natural_leaf_calls':len(leaf_frames),
      'natural_context_scope':'New T123b original-menu proof from verified accepted T124t round1 checkpoint, complete CPU/waiting_key restored; original policy/9 matches/keys/choices and later stages compared exactly. Leaf attached to actual Match machine.',
      'raw_scope':'Native published records plus declared synthetic parent/empty-slot edits; actual original re-sorts and post-sort live reads, ordered live/caller-visible writes and guest-frame effects; complete final memory including dead frames and ALLREGS match.',
      'sealed_scope':'Actual PortMachine with real helpers only, positive Unicorn/EXE denial, full canonical state/record/RNG/parent comparison; only SS9000:2000..2FFF dead helper locals normalized. Unsupported modes preserve complete body-entry memory.',
      'input_classification':'Focused synthetic parent/edge fixtures are isolated-function evidence. Natural continuation has genuine original E44F frames and unchanged T124t policy; no product automatic-eleven policy or full sealed outer-route claim.',
      'sources':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths},
      'receipt_sha256':{str(p.relative_to(ROOT)):sha(p.read_bytes()) for directory in (HERE/'raw-v2',HERE/'sealed-v1',HERE/'falsifiers-v1',HERE/'natural-v2',HERE/'unit-v3',HERE/'baseline-final-v2',HERE/'annotations-v1') for p in directory.iterdir() if p.is_file()},
      'normalization_controls':controls}
    with out.open('x') as f:f.write(json.dumps(index,indent=2,sort_keys=True)+'\n')
    print('PASS: 10 raw, 16 sealed (6 unsupported), 4 falsifiers, 2 natural leaf calls, 9 matches, stages 3/4, 6 normalization controls')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();verify(a.out)
