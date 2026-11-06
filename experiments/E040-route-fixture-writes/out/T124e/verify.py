"""Verify the final source-bound T124e index without running a game or gate."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match.image import Image
from original_match.machine import REGS
from original_match.port import stages

def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return [json.loads(l) for l in (ROOT/path).read_text().splitlines()]
def check(index):
    x=json.loads(Path(index).read_text());assert x['schema']=='t124e-acceptance/1'
    for field in ('file_hashes','source_hashes'):
        for path,digest in x[field].items():assert sha((ROOT/path).read_bytes())==digest,'changed '+path
    for path,digest in x['source_hashes'].items():
        blob=subprocess.check_output(['git','show',x['source_freeze_commit']+':'+path],cwd=ROOT)
        assert sha(blob)==digest,'freeze commit differs '+path
    for path,cp in x['private_files'].items():
        data=(ROOT/path).read_bytes();assert sha(data)==cp['sha256'],'private digest '+path
        if 'context' in cp:
            ctx=cp['context'];assert set(ctx['regs'])==set(REGS) and 'waiting_key' in ctx
            assert not Image(data).build_problems(),'unregistered original image '+path
    for phase,path in x['natural_tails'].items():
        header,r=read(path);assert r['status']=='completed' and r['phase']==phase
        assert r['all_memory_equal'] and not r['register_differences'] and r['records_equal'] and r['waiting_key_equal']
        assert r['summary']['000E:60CB']['proved']==1 and r['pages']
        for p in r['pages']:assert p['manager_tag']==128+p['manager_cursor']
        for p,h in header['source_hashes'].items():assert x['source_hashes'][p]==h
    for path in x['controlled_tails']:
        header,r=read(path);assert r['status']=='completed' and r['phase']=='continental-host'
        assert r['all_memory_equal'] and not r['register_differences'] and r['records_equal'] and r['waiting_key_equal']
    for path in x['plain_compositions']:
        header,r=read(path);assert r['status']=='completed' and r['pages_equal'] and r['ordered_live_byte_writes_equal']
        assert not r['memory_difference_spans_outside_dead_stack'] and r['records_equal'] and r['waiting_key_equal'] and r['backend_no_uc']
        assert not(set(r['register_differences'])-{'EBX','ECX','ESI','EDI','ES','EFLAGS'})
        assert r['reached_real_ports']['214B:009C'] and r['reached_real_ports']['23E4:0644']
        assert r['reached_real_ports']['214B:08DD']
        for v in r['normalization_controls'].values():
            if isinstance(v,dict):assert v['caught']==v['expected']
            else:assert v
        assert 'no registered port/return' in r['unregistered_original_guard']
        for p,h in header['source_hashes'].items():assert x['source_hashes'][p]==h
    controls=read(x['controlled_pages']);two=next(r for r in controls if r.get('status')=='two-managers-proved')
    assert two['cursor_before']==two['cursor_after']==2 and two['summary']['000E:60CB']['proved']==2
    assert [(p['manager_cursor'],p['manager_tag']) for p in two['pages']]==[(1,129),(2,130)]
    assert {r['case'] for r in controls if r.get('status')=='falsifier-caught'}=={'news-draw','cursor-restoration','tour-next-write'}
    for path in x['input_receipts']:
        rows=read(path);r=rows[-1];cp=r['checkpoint'];assert r['status']=='announcement-entry'
        data=(ROOT/cp['path']).read_bytes();image=Image(data);regs=cp['context']['regs']
        assert (regs['CS']-image.load,regs['EIP']&65535)==(0xE,0x60CB)
        s=regs['SS']*16+(regs['ESP']&65535)
        assert int.from_bytes(image.memory[s:s+2],'little')==0x7152
        assert int.from_bytes(image.memory[s+2:s+4],'little')==image.load+0xE
        assert (regs['ESP']&65535)==0x3EDC and (regs['EBP']&65535)==0x3EEA
    before=subprocess.check_output(['git','show',x['base_commit']+':runtime/original_match/port/stages.py'],text=True,cwd=ROOT)
    old={n.name:ast.dump(n) for n in ast.parse(before).body if isinstance(n,ast.FunctionDef)}
    new={n.name:ast.dump(n) for n in ast.parse((ROOT/'runtime/original_match/port/stages.py').read_text()).body if isinstance(n,ast.FunctionDef)}
    assert len(old)==35 and all(new.get(n)==v for n,v in old.items())
    assert len(stages.PORTS.entries)==27 and len(stages.PORTS.variants)==25
    audit=json.loads((HERE/'static-call-audit-v1.json').read_text())
    assert audit['status']=='passed' and audit['call_count']==75 and audit['total_instructions']==758
    assert audit['source_sha256']==sha((ROOT/'runtime/original_match/port/stages.py').read_bytes())
    assert 'Ran 59 tests' in (HERE/'focused-final-v2.log').read_text() and (HERE/'focused-final-v2.log').read_text().rstrip().endswith('OK')
    assert 'ALL13 exact final new tests failed/errors' in (HERE/'exact-tests-before-v2.log').read_text()
    print(json.dumps({'status':'passed','file_hashes':len(x['file_hashes']),'source_hashes':len(x['source_hashes']),
      'private_files':len(x['private_files']),'private_contexts':sum('context' in v for v in x['private_files'].values()),
      'natural_tails':len(x['natural_tails']),'controlled_tails':len(x['controlled_tails']),'plain_compositions':len(x['plain_compositions']),
      'two_manager_pages':2,'falsifiers':3,'old_functions_unchanged':len(old),'static_calls':75,'static_instructions':758},sort_keys=True))
if __name__=='__main__':check(sys.argv[1])
