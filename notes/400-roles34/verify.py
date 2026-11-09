#!/usr/bin/env python3
"""Offline, read-only verification of T131: provenance pins, the kept states, the live CC7B frames and the keys.

Executes no guest instruction and imports no goal2 code. Needs the private states under .cache/400-roles34/ (the
raw attempt files) and .cache/400-roles34/readback/ (the delivered, t131-named copies and the package), see
docs/requests/400-roles34.md. Exit status 0 with a PASS line, or an AssertionError naming the first failing check.
"""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import frames
ROOT=HERE.parents[1];NOTES=HERE;CACHE=ROOT/'.cache/400-roles34'
def sha(b):return hashlib.sha256(b).hexdigest()
def rows(name):return [json.loads(l) for l in (NOTES/name/'steps.jsonl').read_text().splitlines()]
def rec(name):return json.loads((NOTES/name/'record.json').read_text())
FORBIDDEN=('.wr(','set_reg','restore(','return_from(','.m.stop(','uc.reg_write','uc.mem_write','mem_write','.poke')   # a guest write, a register edit, a CPU move

def check_attempt(name):
    r=rec(name);src=json.loads((NOTES/name/'source.json').read_text())
    for k,v in src.items():assert r[k]==v,f'{name}: source.json {k} differs from record.json'
    collector=(NOTES/name/'collector.py').read_bytes();framesrc=(NOTES/name/'frames.py').read_bytes()
    assert sha(collector)==r['collector_sha256'] and sha(framesrc)==r['frames_sha256'],name
    assert subprocess.check_output(['git','show',r['head']+':notes/400-roles34/collect.py'],cwd=ROOT)==collector,name
    assert subprocess.check_output(['git','show',r['head']+':notes/400-roles34/frames.py'],cwd=ROOT)==framesrc,name
    for token in FORBIDDEN:assert token not in collector.decode(),f'{name}: the collector contains {token}'
    assert r['date_call_sha256']=='0d9c683023c7327f17bfc29900f2eff4e703641d21d3f353693f09654688494b'
    assert r['goal_dat_sha256']=='bc5e5c04434d31f350eb7803afc3810333393e049d50dde559797a5b068c60ca'
    assert r['core_source_commit']=='42c25412a81a397cb40ed28ba54bca7c688d8b07'
    core=CACHE/'core-source'
    if core.exists():
        files={str(p.relative_to(core)):sha(p.read_bytes()) for p in sorted(core.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
        assert sha(json.dumps(files,sort_keys=True).encode())==r['core_tree_sha256'],f'{name}: the pinned goal2 Core source differs'
    return r

def states(name):
    n=0
    for i,row in enumerate(rows(name),1):
        assert row['n']==i
        if row.get('state'):
            raw=(ROOT/row['state']['file']).read_bytes();assert sha(raw)==row['state']['sha256'],row['state']['file']
            if row.get('frame') is not None:
                if raw[:4]==b'G2C1':meta,mem=frames.read_g2core(raw);load,regs=meta['load'],meta['regs']
                else:meta,mem=frames.read_ucstate(raw);load,regs=meta['load'],meta['regs']
                assert frames.derive(mem,load,regs)==row['frame'],f"{name}#{i}: the frame derived from the kept bytes differs"
            n+=1
    return n

def main():
    attempts={n:check_attempt(n) for n in ('reach-r1','stop-r1','search-r1','preceding-r1')}
    kept=sum(states(n) for n in attempts)
    reach=rows('reach-r1');repair=[r for r in reach if r['label']=='repair-r07'][0]
    menu=attempts['search-r1']['menu']['sha256'];assert menu==attempts['stop-r1']['menu']['sha256']==attempts['preceding-r1']['menu']['sha256']==repair['state']['sha256']
    # the reach reached round 7 by T170e's keys: round 6 and round 7 each refused an ineligible eleven, repaired by the squad screen's own keys
    assert [r['label'] for r in reach if r['label'].startswith('repair')]==['repair-r06','repair-r07']
    assert all('refuses the eleven' in r['refusal'] for r in reach if r['label'].startswith('repair'))
    assert 'keyword argument' in attempts['reach-r1']['error'] and attempts['stop-r1']['status']=='unknown screen captured'
    d=json.loads((NOTES/'delivery.json').read_text())
    assert d['schema']=='T131-original-inputs/1' and 3 in d['covered_roles']
    for role,entry in d['roles'].items():
        role=int(role);keys=json.loads((NOTES/f'keys-role{role}.json').read_text())
        assert keys['sha256']==sha(bytes(keys['keys'])) and keys['count']==len(keys['keys'])
        decision=None;previous=None
        for item in entry['inputs']:
            raw=(ROOT/item['readback']).read_bytes();assert sha(raw)==item['sha256'] and item['file'].startswith(f"t131-{item['sha256'][:16]}-role{role}-")
            meta,mem=frames.read_g2core(raw)
            if item['frame'] is not None:
                got=frames.derive(mem,meta['load'],meta['regs']);assert got==item['frame'],item['file']
                assert (got['role'],got['pick_in_eleven'])==(role,True)
            assert len(meta['keys'])==item['keys'] and sha(bytes(meta['keys']))==item['keys_sha256']
            if item['label'].endswith('decision-before-space'):
                decision=item;assert meta['keys']==keys['keys'] and meta['at_poll'] and item['site']=='0791:CC54' and item['kind']=='set-piece-select'
                f=item['frame'];assert f['highlight']>=1 and f['pick']==f['stored_pick']==f['eleven'][f['highlight']-1]
            elif item['label'].endswith('space-pitch-read'):
                assert meta['keys']==keys['keys']+[32] and not meta['at_poll'] and item['site']=='0791:CF3A' and item['kind']=='set-piece-pitch'
            elif item['label'].endswith('return-back-at-selector'):
                assert meta['keys']==keys['keys']+[32,13] and meta['at_poll'] and item['site']=='0791:CC54'
                assert (item['frame']['highlight'],item['frame']['pick'])==(decision['frame']['highlight'],decision['frame']['pick'])
            elif item['label'].endswith('return-accept'):
                assert meta['keys']==keys['keys']+[32,13,13] and item['site']=='0791:93C2' and item['kind']=='match-live'
                ds=(meta['load']+frames.GOAL_DS_PARAGRAPH)*16;f=decision['frame']
                stored=int.from_bytes(mem[ds+0x9976+10*f['side']+2*f['role']:][:2],'little');assert stored==f['pick'],'the accepted pick is stored'
            elif item['label']=='preceding-wait':
                assert item['site']=='0791:93C2' and item['kind']=='match-live' and item['poll']
            previous=item
        assert decision is not None
        if role==3:
            f=decision['frame'];assert (f['role'],f['side'],f['country'],f['opponent'],f['highlight'],f['pick'],f['minute'])==(3,1,7,9,11,131,33)
            assert entry['round']==7
            prec=[i for i in entry['inputs'] if i['label']=='preceding-wait'][0];assert prec['keys']==decision['keys']
    # the unchanged Core stops at the same machine the adapter's decision serves: one state, two routes to it
    u=d['unchanged_core_stop'];raw=(ROOT/u['readback']).read_bytes();assert sha(raw)==u['sha256']
    umeta,umem=frames.read_ucstate(raw)
    dec=[i for i in d['roles']['3']['inputs'] if i['label'].endswith('decision-before-space')][0]
    gmeta,gmem=frames.read_g2core((ROOT/dec['readback']).read_bytes())
    assert umeta['regs']==gmeta['regs'] and umeta['load']==gmeta['load'] and umem==gmem[:len(umem)],'the unchanged stop and the decision are one machine'
    reach_state=sorted((CACHE/'reach-r1').glob('017-unknown-screen-r07.ucstate'))[0]
    rmeta,rmem=frames.read_ucstate(reach_state.read_bytes());assert rmeta==umeta and rmem==umem,'reach-r1 and stop-r1 stopped at one machine'
    assert u['frame']['site']=='0791:CC54' and u['frame']['role']==3
    for name in ('package',):
        pkg=d['package'];assert sha((ROOT/pkg['readback']).read_bytes())==pkg['sha256']
    print(f"PASS: 4 attempts pinned to their collector commits; {kept} kept states re-derived; roles {d['covered_roles']} covered by original keys; remaining {d['remaining']}; "
          f"unchanged Core stop = decision machine; all private readbacks verified")

if __name__=='__main__':main()
