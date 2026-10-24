#!/usr/bin/env python3
"""Read-only T90 provenance, original-key selection and target-state verification."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
from frames import ROOT,derive,Image
sys.path.insert(0,str(ROOT/'notes/400-next'))
from inventory import SIZES
def sha(b):return hashlib.sha256(b).hexdigest()
def recorded_code(rec,name):
    b=subprocess.check_output(['git','show',rec['head']+':notes/400-last/'+name],cwd=ROOT)
    assert sha(b)==rec['collector_sha256'];return b
def strings(obj):
    if isinstance(obj,dict):
        for v in obj.values():yield from strings(v)
    elif isinstance(obj,list):
        for v in obj:yield from strings(v)
    elif isinstance(obj,str):yield obj
def squad(raw):
    im=Image.from_savestate(raw);m=im.memory;ds=im.DS*16
    w=lambda a:int.from_bytes(m[a:a+2],'little');far=lambda a:w(ds+a)+16*w(ds+a+2)
    c=far(0xA917)+20*191;assert m[c+0x2E]==129
    return [w(c+2*i) for i in range(20)]
def main():
    base=ROOT/'notes/400-last';d=json.loads((base/'delivery.json').read_text());count=0;attempts={}
    for name in d['attempts']:
        folder=base/name;rec=json.loads((folder/'record.json').read_text());code=recorded_code(rec,'collect.py');assert code==(folder/'collector.py').read_bytes()
        assert rec['bound_s']==240 and rec['fixture_bound']==1
        assert rec['elapsed_s']<=241
        assert sha((ROOT/'.cache/400-last/assets'/rec['source']).read_bytes())==rec['source_sha256']
        rows=[json.loads(line) for line in (folder/'steps.jsonl').read_text().splitlines()];assert len(rows)==rec['observations'];previous=None
        for n,row in enumerate(rows,1):
            raw=(ROOT/row['file']).read_bytes();assert sha(raw)==row['sha256'] and row['n']==n and row['preceding']==previous
            assert not Image.from_savestate(raw).build_problems();previous=row['sha256'];count+=1
        if 'resume' in rec:
            r=rec['resume'];assert sha((ROOT/r['file']).read_bytes())==r['sha256'];conf=(folder/'preceding-dosbox.conf').read_bytes()
            assert sha(conf)==r['config_sha256'] and [l for l in conf.decode().splitlines() if l.startswith('mount ')]==r['verified_mounts']
        else:
            assert any('Please enter name of saved game' in r['screen'] for r in rows)
            assert any(r['request']=={'keys':list(rec['source'][:-3].lower())} for r in rows)
        bysha={r['sha256']:r for r in rows}
        for change in rec.get('selection_changes',[]):
            before=squad((ROOT/bysha[change['before_sha256']]['file']).read_bytes());after=squad((ROOT/bysha[change['after_sha256']]['file']).read_bytes())
            assert sorted(before)==sorted(after)
            assert change['outgoing'] in before[:11] and change['incoming'] in before[11:]
            assert change['incoming'] in after[:11] and change['outgoing'] in after[11:]
        if rec['status']=='full time without target':
            assert 'FULL TIME' in rows[-1]['screen']
            end=Image.from_savestate((ROOT/rows[-1]['file']).read_bytes());ds=end.DS*16
            assert end.memory[ds+0x9A3E]==0 and end.memory[ds+0x9A3F]==0
        for change in rec.get('position_changes',[]):
            b=Image.from_savestate((ROOT/bysha[change['before_sha256']]['file']).read_bytes());a=Image.from_savestate((ROOT/bysha[change['after_sha256']]['file']).read_bytes())
            def pos(image):
                m=image.memory;ds=image.DS*16;off=int.from_bytes(m[ds+0xA91B:ds+0xA91D],'little');seg=int.from_bytes(m[ds+0xA91D:ds+0xA91F],'little')
                return m[seg*16+off+20*change['player']+6]
            assert pos(b)==change['before'] and pos(a)==change['after'] and change['keys']==['r','r']
        attempts[name]=(rec,rows)
    search=json.loads((base/'record-search-r1.json').read_text());recorded_code(search,'scan_records.py')
    pattern=re.compile(r'select\s+(FREE\s*KICK|PENALTY)\s+taker',re.I)
    assert len(search['records'])==477 and not search['matches']
    for item in search['records']:
        raw=(ROOT/item['file']).read_bytes();assert sha(raw)==item['sha256']
        assert not any(pattern.search(t) for t in strings(json.loads(raw))) and item['hits']==0
    assess=json.loads((base/'source-assessment-r1.json').read_text());recorded_code(assess,'assess_sources.py');assert len(assess['sources'])==17
    for item in assess['sources']:
        raw=(ROOT/'.cache/400-last/assets'/item['file']).read_bytes();assert sha(raw)==item['sha256'] and len(raw)==sum(SIZES)
        cs=raw[sum(SIZES[:10]):sum(SIZES[:11])];ps=raw[sum(SIZES[:11]):sum(SIZES[:12])];c=item['country']
        ids=[int.from_bytes(cs[c*191+2*i:c*191+2*i+2],'little') for i in range(11)]
        assert item['positions']==[ps[20*p+6] for p in ids]
        assert item['zero_energy_slots']==[i+1 for i,p in enumerate(ids) if ps[20*p+14]==0]
    foul=json.loads((base/'foul-gate-assessment-r1.json').read_text());recorded_code(foul,'assess_foul_gate.py');assert len(foul['sources'])==14
    for source in foul['sources']:
        raw=(ROOT/'.cache/400-last/assets'/source['file']).read_bytes();assert sha(raw)==source['sha256']
        cs=raw[sum(SIZES[:10]):sum(SIZES[:11])];ps=raw[sum(SIZES[:11]):sum(SIZES[:12])];names=raw[:SIZES[0]]
        name=lambda c:names[c*16+1:c*16+1+names[c*16]].decode('cp437')
        other=next(c for c in range(1,129) if name(c)==source['opponent'])
        for country,key in ((20,'own'),(other,'other')):
            for i,item in enumerate(source[key]):
                p=int.from_bytes(cs[country*191+2*i:country*191+2*i+2],'little');r=ps[20*p:20*p+20]
                assert item==dict(slot=i+1,player=p,position=r[6],hardness=r[5]-(r[3]&1),energy=r[14],status=r[16],saved_own_tactic4=bool(r[15]&8),saved_own_override4=bool(r[15]&128))
    multi=json.loads((base/'multiplayer-save-search-r1.json').read_text());recorded_code(multi,'scan_multiplayer_saves.py');assert not multi['errors']
    for item in multi['inputs']:
        raw=(ROOT/'.cache/400-last/multiplayer-search-assets'/(item['sha256']+'.GL')).read_bytes();assert sha(raw)==item['sha256']
        game=raw[sum(SIZES[:12]):sum(SIZES[:13])];assert game[0]==item['managers']==1
    retained=json.loads((base/'retained-target-scan-r1.json').read_text());recorded_code(retained,'scan_retained_targets.py')
    assert len(retained['snapshots'])==count==848 and all(not x['caption_match'] and not x['stack_candidates'] for x in retained['snapshots'])
    for item in retained['snapshots']:assert sha((ROOT/item['file']).read_bytes())==item['sha256']
    roles=set()
    for case in d['cases']:
        rec,rows=attempts[case['attempt']];role=case['role'];assert role in (3,4) and rec['target']['role']==role
        for item in case['inputs']:
            row=rows[item['step']-1];raw=(ROOT/row['file']).read_bytes()
            assert row['sha256']==item['sha256']==sha((ROOT/item['readback']).read_bytes())
            assert row['preceding']==item['preceding_sha256']==sha((ROOT/item['preceding_readback']).read_bytes())
            assert derive(raw)==item['frame'] and item['frame']['role']==role
        before,board,back=[rows[i['step']-1] for i in case['inputs']]
        assert board['request']=={'keys':['space']} and back['request']=={'keys':['Return']}
        assert case['inputs'][1]['frame']['site']=='0791:CF3A';roles.add(role)
    assert sorted(roles)==d['captured_roles']
    assert set(d['remaining'])==({'role3_penalty','role4_free_kick','E062_no_player','EC60_vacancy'}-{f'role{r}_'+('penalty' if r==3 else 'free_kick') for r in roles})
    for package in d['packages']:assert sha((ROOT/package['readback']).read_bytes())==package['sha256']
    from verify_unicorn import records
    uc=records();assert set(uc)=={'uc-r1','uc-r2'}
    assert uc['uc-r1'][0]['status']=='aborted' and 'UnknownScreen' in uc['uc-r1'][0]['error']
    assert uc['uc-r2'][0]['status']=='full time without target' and uc['uc-r2'][0]['elapsed_s']<120
    assert uc['uc-r2'][0]['existing_effective_tactics']==dict(push_forward=True,quick_pass=False)
    core_count=sum(len(rows) for rec,rows in uc.values())
    assert core_count==94
    print(f'PASS:{len(attempts)} native attempts /{count} observations +2 exact-CPU replays /{core_count} observations;477 decoded records and17 source assessments; captured roles{sorted(roles)}; remaining {d["remaining"]}; all private readbacks verified')
if __name__=='__main__':main()
