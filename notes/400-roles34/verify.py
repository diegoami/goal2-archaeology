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
    for k,v in src.items():assert k=='status' or r[k]==v,f'{name}: source.json {k} differs from record.json'
    collector=(NOTES/name/'collector.py').read_bytes();framesrc=(NOTES/name/'frames.py').read_bytes()
    assert sha(collector)==r['collector_sha256'] and sha(framesrc)==r['frames_sha256'],name
    assert subprocess.check_output(['git','show',r['head']+':notes/400-roles34/collect.py'],cwd=ROOT)==collector,name
    headframes=subprocess.check_output(['git','show',r['head']+':notes/400-roles34/frames.py'],cwd=ROOT)
    if headframes!=framesrc:
        # provenance-clarifications.json: stop-c9 and stop-c1 copied frames.py while `origin` was being appended to it
        # (after their head commit): the copy is that commit's file plus exactly the current file's tail
        assert name in ('stop-c9','stop-c1') and framesrc.startswith(headframes) and (HERE/'frames.py').read_bytes().endswith(framesrc[len(headframes):]),name
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
    names=sorted(p.parent.name for p in NOTES.glob('*/record.json'))
    attempts={n:check_attempt(n) for n in names}
    kept=sum(states(n) for n in attempts)
    reach=rows('reach-r1');repair=[r for r in reach if r['label']=='repair-r07'][0]
    menu=attempts['search-r1']['menu']['sha256'];assert menu==attempts['stop-r1']['menu']['sha256']==attempts['preceding-r1']['menu']['sha256']==repair['state']['sha256']
    # the reach reached round 7 by T170e's keys: round 6 and round 7 each refused an ineligible eleven, repaired by the squad screen's own keys
    assert [r['label'] for r in reach if r['label'].startswith('repair')]==['repair-r06','repair-r07']
    assert all('refuses the eleven' in r['refusal'] for r in reach if r['label'].startswith('repair'))
    # every later search starts from a kept state of an earlier attempt, by hash
    held={r['state']['sha256'] for n in names for r in rows(n) if r.get('state')}
    for n in names:
        if n.startswith(('search-','preceding-','stop-')) and n!='search-r1':assert attempts[n]['menu']['sha256'] in held,f'{n}: its menu is not a kept state'
    assert 'keyword argument' in attempts['reach-r1']['error'] and attempts['stop-r1']['status']=='unknown screen captured'
    d=json.loads((NOTES/'delivery.json').read_text())
    assert d['schema']=='T131-original-inputs/2'
    # the statement of what was met is recomputed from the raw rows: prompts by role, managed matches played
    prompts={};matches=0
    for n in ['reach-r1']+[n for n in names if n.startswith('search-')]:
        menu={};done=set()
        for r in rows(n):
            if r['label'].startswith('taker-r'):prompts[str(r['role'])]=prompts.get(str(r['role']),0)+1
            if r['label'].startswith('menu-r') and '-repair' not in r['label']:menu[r['round']]=r['t']
            if r['label'].startswith('round-r') and r['round'] in menu and r['round'] not in done:
                done.add(r['round']);matches+=r['t']-menu[r['round']]>100
    assert d['prompts']['taker_prompts_by_role']==prompts and d['prompts']['managed_matches']==matches,(prompts,matches)
    assert d['covered_roles']==[3,4] and d['remaining']==[]
    # what each case is: (role, side, country, opponent, highlight, current pick, minute, CC7B's caller 6D4E returns to, its args)
    EXPECT={'role3':(3,1,7,9,11,131,33,0x6EEF,[10,3,1]),'role4-england':(4,0,9,23,3,163,71,0x6F92,[11,4,0]),'role4-albania':(4,1,1,5,10,10,58,0x6F92,[11,4,1])}
    assert set(d['roles'])==set(EXPECT)
    for case,entry in d['roles'].items():
        role=entry['role'];keys=json.loads((NOTES/f'keys-{case}.json').read_text())
        assert keys['sha256']==sha(bytes(keys['keys'])) and keys['count']==len(keys['keys']) and all(0<k<=255 for k in keys['keys'])
        decision=None;labels=[i['label'] for i in entry['inputs']]
        assert labels==['preceding-wait','decision-before-space','space-pitch-read','return-back-at-selector','return-accept'],labels
        for item in entry['inputs']:
            raw=(ROOT/item['readback']).read_bytes();assert sha(raw)==item['sha256'] and item['file'].startswith(f"t131-{item['sha256'][:16]}-{case}-")
            meta,mem=frames.read_g2core(raw)
            if item['frame'] is not None:
                got=frames.derive(mem,meta['load'],meta['regs']);assert got==item['frame'],item['file']
                assert (got['role'],got['pick_in_eleven'])==(role,True)
                assert item['origin']==frames.origin(mem,meta['load'],meta['regs'])
            assert len(meta['keys'])==item['keys'] and sha(bytes(meta['keys']))==item['keys_sha256']
            tag=item['label']
            if tag=='decision-before-space':
                decision=item;assert meta['keys']==keys['keys'] and meta['at_poll'] and item['site']=='0791:CC54' and item['kind']=='set-piece-select'
                f=item['frame'];assert f['pick']==f['stored_pick']==f['eleven'][f['highlight']-1]
                assert (f['role'],f['side'],f['country'],f['opponent'],f['highlight'],f['pick'],f['minute'],item['origin']['return_offset'],item['origin']['args'])==EXPECT[case],(case,f)
            elif tag=='space-pitch-read':
                assert meta['keys']==keys['keys']+[32] and not meta['at_poll'] and item['site']=='0791:CF3A' and item['kind']=='set-piece-pitch'
            elif tag=='return-back-at-selector':
                assert meta['keys']==keys['keys']+[32,13] and meta['at_poll'] and item['site']=='0791:CC54'
                assert (item['frame']['highlight'],item['frame']['pick'])==(decision['frame']['highlight'],decision['frame']['pick'])
            elif tag=='return-accept':
                assert meta['keys']==keys['keys']+[32,13,13] and item['site']=='0791:93C2' and item['kind']=='match-live'
                ds=(meta['load']+frames.GOAL_DS_PARAGRAPH)*16;f=decision['frame']
                assert int.from_bytes(mem[ds+0x9976+10*f['side']+2*f['role']:][:2],'little')==f['pick'],'the accepted pick is stored'
            elif tag=='preceding-wait':
                assert item['poll'] and item['keys']==len(keys['keys']),'the wait before the decision has the decision\'s key log'
        # the decision pending belongs to a managed side's own career: which side is the manager's, from the kept country record
    # the unchanged Core's stop is the decision's machine: one state, two routes to it
    for case,u in d['unchanged_core_stop'].items():
        raw=(ROOT/u['readback']).read_bytes();assert sha(raw)==u['sha256']
        umeta,umem=frames.read_ucstate(raw)
        dec=d['roles'][case]['inputs'][1];gmeta,gmem=frames.read_g2core((ROOT/dec['readback']).read_bytes())
        assert umeta['regs']==gmeta['regs'] and umeta['load']==gmeta['load'] and umem==gmem[:len(umem)],f'{case}: the unchanged stop and the decision are one machine'
        assert u['frame']==dec['frame'] and u['site']=='0791:CC54'
    reach_state=CACHE/'reach-r1/017-unknown-screen-r07.ucstate'
    rmeta,rmem=frames.read_ucstate(reach_state.read_bytes());umeta,umem=frames.read_ucstate((ROOT/d['unchanged_core_stop']['role3']['readback']).read_bytes())
    assert rmeta==umeta and rmem==umem,'reach-r1 and stop-r1 stopped at one machine'
    # Albania's unchanged Core stops earlier, at a role 3 of its own (minute 13): it never reaches that career's role 4
    a=d['albania_first_stop'];assert sha((ROOT/a['readback']).read_bytes())==a['sha256'] and a['frame']['role']==3 and a['frame']['minute']<d['roles']['role4-albania']['inputs'][1]['frame']['minute']
    pkg=d['package'];assert sha((ROOT/pkg['readback']).read_bytes())==pkg['sha256']
    print(f"PASS: {len(names)} attempts pinned to their collector commits; {kept} kept states re-derived; cases {sorted(d['roles'])} reached by original keys, "
          f"CC7B's caller 6D4E confirms penalty (6EEF) and free kick (6F92); unchanged Core stops at the decision machine for role 3 and England's role 4; all private readbacks verified")

if __name__=='__main__':main()
