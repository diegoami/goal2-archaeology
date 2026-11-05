"""Audit immutable T125 acceptance families and normalized-state falsifiers.
No original bytes are written: all emitted artifacts contain hashes/counts only.
"""
import argparse, copy, hashlib, json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'runtime'),str(HERE)]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(path):return [json.loads(line) for line in path.read_text().splitlines()]

def verify(out,sealed_folder):
    raw=rows(HERE/'real-v1/raw.jsonl');sealed=rows(HERE/sealed_folder/'sealed.jsonl')
    assert len(raw)==48 and {r['manager'] for r in raw}=={1,2}
    assert {r['target'] for r in raw}=={'0791:DC7E','0791:DBFA','0791:DB38','0791:DAF8','1771:55FC'}
    assert all(r['status']=='passed' and r['summary'][r['target']]['proved']==1 and
      r['full_memory_and_registers_match'] and not any(v['scratch'] for v in r['summary'].values()) for r in raw)
    expected_dependencies=['runtime/original_match/port/assistant.py',str((HERE/'prove.py').relative_to(ROOT))]
    for r in raw:
      for path in expected_dependencies:assert r['source_hashes'][path]==sha(ROOT/path)
      if r['target']=='0791:DC7E':
        strength=r['strength_trace'];calls=[e[1] for e in strength[::2]]
        assert len(strength)%2==0 and all(e[0]=='call' for e in strength[::2])
        assert all(e[0]==('0791:DD6B' if i%2==0 else '0791:DD7F') for i,e in enumerate(strength[1::2]))
        case=r['case']
        if case=='improve':
          assert len(calls)==6320 and len(r['swap_args'])==3
          assert r['squad'][:2]==[22,21] and r['pool'][:2]==[1,2]
          assert calls[:4]==[21,1,22,21]
        if case in ('ties','weaker'):assert len(calls)==6400 and not r['swap_args']
        if case in ('nomatch','wrap','finals','tour'):assert not strength and not r['swap_args']
        if case=='unavailable':
          assert len(calls)==6320 and 22 not in r['squad']
          assert any(a==['call',22] and b[1]==0 for a,b in zip(strength[::2],strength[1::2]))
        if case in ('finals','tour'):
          assert r['squad']==list(range(1,21)) and r['pool']==list(range(21,101))
          assert r['next']==(0xABCD if case=='finals' else 2)
    assert len(sealed)==22 and {r['manager'] for r in sealed}=={1,2}
    for r in sealed:
      s=r['sealed'];assert r['status']=='passed' and s['fields']==r['original_fields']
      assert s['copy_isolated'] and s['tables_unchanged'] and s['unicorn_denied'] and s['exe_denied']
      assert set(s['fields']['records'])=={'countries','players','managers','pool','fixtures','country_lists','game'}
      for path,value in r['source_hashes'].items():assert value==sha(ROOT/path)
    failures={}
    for variant in ('ties-replace','swap-omitted','next-write-omitted'):
      rr=rows(HERE/'real-v1'/f'{variant}.jsonl')
      assert len(rr)==2 and {r['manager'] for r in rr}=={1,2}
      assert all(r['status'].startswith('ProofError:') for r in rr)
      failures[variant]=[r['status'] for r in rr]
    # Construct only in private process memory. Check both exclusion boundaries,
    # an owned manager byte, and RNG. None may hide outside the dead frame.
    import prove,sealed as S
    from original_match.image import Image
    from original_match.port.tables import load
    tables=load(ROOT/'static/goal-exe/tables');source,_=prove.image();m=prove.prepare(source,1,'none')
    image=Image.__new__(Image);image.memory=bytearray(source.memory);image.memory[:0x110000]=m.read(0,0x110000)
    image.header=source.header;image.load=source.load;image.DS=source.DS;image.tables=tables
    base=S.normalized(image.state(tables));ss=(image.load+0x3052)*16;negative={}
    for name,address,changes in [('below',ss+0x1FFF,True),('inside-first',ss+0x2000,False),
        ('inside-last',ss+0x2FFF,False),('above',ss+0x3000,True),('manager',m.far(0xA91F)+3*129,True),
        ('rng',image.DS*16+0x7B62,True)]:
      old=image.memory[address];image.memory[address]^=1;value=S.normalized(image.state(tables));image.memory[address]=old
      assert (value!=base)==changes,(name,changes)
      negative[name]={'address':address,'base_sha256':base,'changed_sha256':value,'detected':value!=base}
    files={str(p.relative_to(ROOT)):sha(p) for directory in (HERE/'real-v1',HERE/sealed_folder) for p in directory.iterdir() if p.is_file()}
    sources={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'runtime/original_match/port/assistant.py',ROOT/'runtime/original_match/assistant.py',ROOT/'tests/test_port_assistant.py',HERE/'prove.py',HERE/'sealed.py',Path(__file__)]}
    result={'schema':'t125-index/1','checked_at_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'raw_source_commit':'49115eec86c6','raw_cases':len(raw),'sealed_cases':len(sealed),'real_managers':[1,2],
      'raw_scope':'Five port bodies versus original callees: ordered live writes through Prover; independent raw-original complete memory including dead frames and ALL REGS equality. Raw driver and port-module source hashes must match. Recorded facade hash is informational: raw nonclosure mode does not import/run the facade.',
      'sealed_scope':'Independent original versus facade: all allocated countries/players/managers/pool/fixtures/lists/game records; ordered squad/pool, both RNG words and 9B43. Entire state including table deltas/metadata also matches after excluding ONLY SS:2000..2FFF dead stack locals below the entry SP3000. Positive import/file denials, full input/output state hashes, state-copy and table purity. No full manager-menu/E44F/52CC preparation claim.',
      'excluded_stack':{'segment':'load+3052','start_inclusive':'2000','end_exclusive':'3000','why':'Existing reused helper ports inline frames differently; these returned-call scratch bytes below entry SP are dead. The five new routines independently match even dead frames in raw mode.'},
      'sources':sources,'receipt_sha256':files,'falsifiers':failures,'normalization_controls':negative}
    with out.open('x') as f:f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS: 48 real-manager raw cases; 22 sealed cases; 6 falsifiers; 6 normalization controls')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--sealed-folder',default='real-v2');a=p.parse_args()
    verify(a.out,a.sealed_folder)
