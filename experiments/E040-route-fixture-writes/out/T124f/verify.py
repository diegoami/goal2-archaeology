"""Verify immutable final T124f source/input/proof bindings; no game or gate."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match.image import Image
from original_match.machine import REGS
from original_match.port import ageing

def sha(v):return hashlib.sha256(v).hexdigest()
def rows(path):return list(map(json.loads,(ROOT/path).read_text().splitlines()))
def main(index):
    x=json.loads(Path(index).read_text());assert x['schema']=='t124f-acceptance/1'
    for p,h in {**x['file_hashes'],**x['source_hashes']}.items():assert sha((ROOT/p).read_bytes())==h,'changed '+p
    for p,h in x['source_hashes'].items():
        blob=subprocess.check_output(['git','show',x['source_freeze_commit']+':'+p],cwd=ROOT)
        assert sha(blob)==h,'freeze source '+p
    for p,cp in x['private_inputs'].items():
        data=(ROOT/p).read_bytes();assert sha(data)==cp['sha256'],'private digest '+p
        if 'context' in cp:
            assert set(cp['context']['regs'])==set(REGS) and 'waiting_key' in cp['context']
            assert not Image(data).build_problems()
    for case,path in x['natural'].items():
        h,entry,r=rows(path);assert r['status']=='completed' and r['case']==case
        assert r['all_memory_equal'] and not r['register_differences'] and r['records_equal'] and r['waiting_key_equal'] and r['actual_page_history_equal']
        assert r['start']['stage']==(2 if case=='continental' else 6)
        assert r['end']['stage']==(3 if case=='continental' else 7) and r['start']['year_word']==r['end']['year_word']
        for a,n in [('1771:80DA',1),('1771:7FDF',128),('1771:7FB1',2640),('1771:7F40',2540)]:assert r['summary'][a]['nested']==n
        for a in ('1771:7E80','1771:96D3','1771:0000'):assert r['summary'][a]['nested']>0
        source=h['source']['context']['regs'];assert (source['EIP'],source['ESP'],source['EBP'])==(0x70E6,0x3EE2,0x3EEA)
        regs=entry['checkpoint']['context']['regs'];image=Image((ROOT/entry['checkpoint']['path']).read_bytes())
        assert (regs['CS']-image.load,regs['EIP']&65535)==(0x1771,0x80DA)
        assert (regs['ESP']&65535,regs['EBP']&65535)==(0x3ED6,0x3EDC)
        s=regs['SS']*16+(regs['ESP']&65535);assert int.from_bytes(image.memory[s:s+2],'little')==0x826D
        for p,d in h['source_hashes'].items():assert x['source_hashes'][p]==d
    seen=set()
    for path in x['plain']:
        h,r=rows(path);assert r['status']=='completed';seen.add((r['case'],r['mode']))
        for key in ('normalized_complete_memory_or_state_equal','ordered_live_byte_writes_equal','records_equal','waiting_key_equal',
                    'backend_no_uc','unicorn_denied','exe_denied','table_unchanged','input_state_unchanged'):assert r[key]
        assert not(set(r['register_differences'])-{'EBX','ECX','ESI','EDI','ES','EFLAGS'})
        for v in r['normalization_controls'].values():
            if isinstance(v,dict):assert v['caught']==v['expected']
            else:assert v
        assert 'no registered port/return' in r['unregistered_original_guard']
        assert r['calls']['1771:80DA']==1 and r['calls']['1771:7FDF']==128
        for p,d in h['source_hashes'].items():assert x['source_hashes'][p]==d
    assert seen=={(c,m) for c in ('continental','world') for m in ('raw','state')}
    direct=rows(x['direct']);assert len([r for r in direct if r.get('status')=='proved'])==6
    assert {r['case'] for r in direct if r.get('status')=='falsifier-caught'}==set(ageing.PORTS.variants)
    audit=json.loads((HERE/'static-call-audit-v2.json').read_text())
    assert (audit['original_instructions'],audit['original_calls'],audit['supported_calls'],audit['annual_only_guarded_calls'])==(563,31,28,3)
    assert audit['source_sha256']==sha((ROOT/'runtime/original_match/port/ageing.py').read_bytes())
    assert len(ageing.PORTS.entries)==10
    assert 'ALL18 exact final new tests fail/error' in (HERE/'exact-tests-before-v1.log').read_text()
    text=(HERE/'focused-final-v1.log').read_text();assert 'Ran 77 tests' in text and text.rstrip().endswith('OK')
    print(json.dumps({'status':'passed','public_hashes':len(x['file_hashes']),'source_hashes':len(x['source_hashes']),
      'private_inputs':len(x['private_inputs']),'fullCPUcontexts':sum('context' in v for v in x['private_inputs'].values()),
      'natural_tails':2,'plain_compositions':4,'synthetic_cases':6,'falsifiers':4,'original_calls':31,'supported_calls':28,'annual_only_guarded':3},sort_keys=True))
if __name__=='__main__':main(sys.argv[1])
