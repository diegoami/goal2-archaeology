#!/usr/bin/env python3
"""Offline, read-only verification of T89 originals, lineage and role coverage."""
import hashlib,json,subprocess
from pathlib import Path
from inventory import SIZES
from frames import ROOT,derive,Image
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    notes=ROOT/'notes/400-next';assets=ROOT/'.cache/400-next/assets'
    known=json.loads((ROOT/'notes/390/inventory.json').read_text())['assets']
    inv=json.loads((notes/'inventory-r1.json').read_text());pools=json.loads((notes/'pool-inventory-r1.json').read_text())
    for rec,script in ((inv,'inventory.py'),(pools,'pool_inventory.py')):
        code=subprocess.check_output(['git','show',rec['head']+':notes/400-next/'+script],cwd=ROOT)
        assert sha(code)==rec['collector_sha256']
    for i,a in enumerate(inv['assets']):
        raw=(assets/a['file']).read_bytes();assert sha(raw)==a['sha256']==next(k['sha256'] for k in known if k['file']==a['file']) and len(raw)==sum(SIZES)
        countries=raw[sum(SIZES[:10]):sum(SIZES[:11])];pool=raw[sum(SIZES[:13]):sum(SIZES[:14])]
        ms=[];ps=[]
        for c in range(1,129):
            cr=countries[c*191:(c+1)*191];manager=cr[0x2E]-0x80
            if manager<=0:continue
            assert manager<=6
            ms.append(dict(country=c,manager_byte=cr[0x2E],empty_slots=[n+1 for n in range(20) if int.from_bytes(cr[2*n:2*n+2],'little')==0]))
            base=1+80*(manager-1)
            ps.append(dict(country=c,manager=manager,pool_empty_rows=[n+1 for n in range(80) if int.from_bytes(pool[2*(base+n):2*(base+n)+2],'little')==0]))
        assert ms==a['managed'] and ps==pools['assets'][i]['managed']
    assert len(inv['assets'])==17 and all(not x['empty_slots'] for a in inv['assets'] for x in a['managed'])
    assert all(not x['pool_empty_rows'] for a in pools['assets'] for x in a['managed'])
    from core_inventory import observe
    cores=json.loads((notes/'core-inventory-r1.json').read_text());assert not cores['errors'] and len(cores['inputs'])==12
    assert sha(subprocess.check_output(['git','show',cores['head']+':notes/400-next/core_inventory.py'],cwd=ROOT))==cores['collector_sha256']
    for item in cores['inputs']:
        raw=(ROOT/item['file']).read_bytes();assert sha(raw)==item['sha256'] and observe(raw)==item['managed']
        assert all(not m['empty_squad_slots'] and not m['empty_pool_rows'] for m in item['managed'])
    count=0;attempts={}
    for folder in sorted(notes.glob('G3B-r*')):
        rec=json.loads((folder/'record.json').read_text());code=(folder/'collector.py').read_bytes()
        assert sha(code)==rec['collector_sha256']
        assert subprocess.check_output(['git','show',rec['head']+':notes/400-next/collect.py'],cwd=ROOT)==code
        assert rec['bound_s']==240 and rec['fixture_bound']==1 and rec['elapsed_s']<240
        assert sha((assets/rec['source']).read_bytes())==rec['source_sha256']
        rows=[json.loads(l) for l in (folder/'steps.jsonl').read_text().splitlines()];assert len(rows)==rec['observations']
        prior=None
        for n,row in enumerate(rows,1):
            raw=(ROOT/row['file']).read_bytes();assert sha(raw)==row['sha256'] and row['n']==n and row['preceding']==prior
            assert not Image.from_savestate(raw).build_problems();prior=row['sha256'];count+=1
        if 'resume' in rec:
            r=rec['resume'];assert sha((ROOT/r['file']).read_bytes())==r['sha256']
            conf=(folder/'preceding-dosbox.conf').read_bytes();assert sha(conf)==r['config_sha256']
            assert [l for l in conf.decode().splitlines() if l.startswith('mount ')]==r['verified_mounts']
        else:
            assert any('Please enter name of saved game' in x['screen'] for x in rows)
            assert any(x['request']=={'keys':['g','3','b']} for x in rows)
        attempts[folder.name]=(rec,rows)
    assert attempts['G3B-r1'][0]['target']==dict(role=5,before=20,pitch=21,back=22)
    assert attempts['G3B-r2'][0]['status']=='full time without target'
    assert 'FULL TIME' in attempts['G3B-r2'][1][-1]['screen']
    d=json.loads((notes/'delivery.json').read_text());assert d['covered_roles']==[5]
    assert set(d['remaining'])=={'role3_penalty','role4_free_kick','E062_no_player','EC60_vacancy'}
    rows=attempts['G3B-r1'][1]
    for item in d['inputs']:
        row=rows[item['step']-1];raw=(ROOT/row['file']).read_bytes()
        assert item['sha256']==row['sha256']==sha((ROOT/item['readback']).read_bytes())
        assert item['preceding_sha256']==row['preceding']==sha((ROOT/item['preceding_readback']).read_bytes())
        assert item['frame']==derive(raw) and item['frame']['role']==5 and not item['frame']['build_problems']
    assert rows[20]['request']=={'keys':['space']} and rows[21]['request']=={'keys':['Return']}
    assert d['inputs'][1]['frame']['site']=='0791:CF3A'
    package=d['package'];assert sha((ROOT/package['readback']).read_bytes())==package['sha256']
    package=d['core_inventory_package'];assert sha((ROOT/package['readback']).read_bytes())==package['sha256']
    print(f'PASS:17 original saves +12 retained G13 inputs /100 managed slots each: no vacancies; {count} observations in2 bounded native attempts; original role5 + CF3A and return; all private hashes verified;4 cases remain')
if __name__=='__main__':main()
