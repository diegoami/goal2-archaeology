#!/usr/bin/env python3
"""Build delivery.json, the key logs and the t131-named private copies from the raw records (read-only on them).

The raw steps.jsonl rows of the search attempts (the decision, its branch of Space, Return, Return) and of the
preceding attempts are the source; this script only names, copies and indexes. Run once the searches have finished.
"""
import hashlib,json,shutil,sys
from pathlib import Path
import frames
ROOT=Path(__file__).resolve().parents[2];NOTES=ROOT/'notes/400-roles34'
OUT=ROOT/'.cache/400-roles34/delivery'
DRIVE='goal2drive:goal2-archaeology/400-roles34-20261109'
# case id -> (role, the search attempt that kept it, the attempt that kept the wait before it)
CASES={'role3':(3,'search-r1','preceding-r1'),'role4-england':(4,'search-c9','preceding-c9'),'role4-albania':(4,'search-c1','preceding-c1')}
def sha(b):return hashlib.sha256(b).hexdigest()
def rows(name):
    out=[json.loads(l) for l in (NOTES/name/'steps.jsonl').read_text().splitlines()]
    for r in out:r['_attempt']=name
    return out
def record(name):return json.loads((NOTES/name/'record.json').read_text())

def item(row,tag,case,step):
    raw=(ROOT/row['state']['file']).read_bytes();digest=sha(raw);assert digest==row['state']['sha256']
    name=f"t131-{digest[:16]}-{case}-{tag}{Path(row['state']['file']).suffix}"
    OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_bytes(raw)
    f=row['frame']
    origin=None
    if f is not None:
        meta,mem=frames.read_g2core(raw) if raw[:4]==b'G2C1' else frames.read_ucstate(raw)
        origin=frames.origin(mem,meta['load'],meta['regs'])
    return dict(step=step,label=tag,file=name,sha256=digest,bytes=len(raw),site=row['site'],kind=row['kind'],poll=row['poll'],
                keys=row['keys'],keys_sha256=row['keys_sha256'],raw_row=f"{row['_attempt']}#{row['n']}",
                origin=origin,
                frame=None if f is None else {k:f[k] for k in ('site','cpu','ss','sp','chain','role','side','country','country_name','opponent','opponent_name','highlight','pick','stored_pick','eleven','pick_in_eleven','pick_status','pick_position','manager_byte','minute','rng_main','rng_aux')},
                private=f'{DRIVE}/{name}',readback=f'.cache/400-roles34/readback/{name}')

def stats(name):
    """Prompts by role (first of each round/role/side/minute) and the rounds in which the managed side played a match."""
    prompts={};matches=0;seen=set();menu={}
    for r in rows(name):
        if r['label'].startswith('taker-r'):prompts[str(r['role'])]=prompts.get(str(r['role']),0)+1
        if r['label'].startswith('menu-r') and '-repair' not in r['label']:menu[r['round']]=r['t']
        if r['label'].startswith('round-r') and r['round'] in menu and r['round'] not in seen:
            seen.add(r['round']);matches+=r['t']-menu[r['round']]>100
    return dict(taker_prompts_by_role=prompts,managed_matches=int(matches))

def main():
    names=sorted(p.name for p in NOTES.glob('search-*') if (p/'record.json').exists())
    recs={n:record(n) for n in names}
    reach=record('reach-r1')
    roles={};keys={}
    for case,(role,search,prec) in CASES.items():
        by={r['label']:r for r in rows(search)}
        d=by[f'role{role}-decision-before-space']
        entry=dict(role=role,attempt=search,round=d['round'],run_index=d['run_index'],inputs=[])
        entry['inputs'].append(item(rows(prec)[0],'preceding-wait',case,0))
        for i,tag in enumerate(('decision-before-space','space-pitch-read','return-back-at-selector','return-accept'),1):
            entry['inputs'].append(item(by[f'role{role}-{tag}'],tag,case,i))
        roles[case]=entry
        meta,_=frames.read_g2core((OUT/entry['inputs'][1]['file']).read_bytes())
        (NOTES/f'keys-{case}.json').write_text(json.dumps(dict(case=case,role=role,keys=meta['keys'],count=len(meta['keys']),sha256=sha(bytes(meta['keys']))))+'\n')
    # the unchanged Core's own stop (no adapter): for role 3 and for England's role 4 it is the decision's machine. Albania's
    # career stops earlier, at a role 3 (minute 13), so the unchanged Core never reaches its role 4: kept as what it is.
    unchanged={case:item(rows(stop)[0],'unchanged-core-stop',case,0) for case,stop in (('role3','stop-r1'),('role4-england','stop-c9'))}
    albania_first=item(rows('stop-c1')[0],'unchanged-core-first-stop','albania-career',0)
    st={n:stats(n) for n in names};st['reach-r1']=stats('reach-r1')
    total={}
    for v in st.values():
        for k,c in v['taker_prompts_by_role'].items():total[k]=total.get(k,0)+c
    covered=sorted({e['role'] for e in roles.values()})
    delivery=dict(schema='T131-original-inputs/2',covered_roles=covered,
                  remaining=[f'role{r}_{n}' for r,n in ((3,'penalty'),(4,'free_kick')) if r not in covered],
                  core=dict(commit=reach['core_source_commit'],tree_sha256=reach['core_tree_sha256']),
                  source=dict(date_call_sha256=reach['date_call_sha256'],goal_dat_sha256=reach['goal_dat_sha256'],private='goal2drive:e039-r0005-date-call.sav'),
                  searches={n:dict(status=recs[n].get('status'),error=recs[n].get('error'),bound_s=recs[n]['bound_s'],first_round=recs[n]['first_round'],
                                   max_round=recs[n]['max_round'],want=recs[n].get('want_roles',[3,4]),elapsed_s=round(recs[n]['elapsed_s'],1),menu=recs[n]['menu'],**st[n]) for n in names},
                  roles=roles,unchanged_core_stop=unchanged,albania_first_stop=albania_first,
                  prompts=dict(managed_matches=sum(v['managed_matches'] for v in st.values()),taker_prompts_by_role=total,
                               note='first prompt of each round, role, side and minute; reach-r1 plays rounds 1-6 with the unchanged Core, which stops at any role 3/4 prompt and met none'))
    pkg=OUT/'t131-all-attempts-private.zip'
    if pkg.exists():
        raw=pkg.read_bytes();delivery['package']=dict(file=pkg.name,sha256=sha(raw),bytes=len(raw),private=f'{DRIVE}/{pkg.name}',readback=f'.cache/400-roles34/readback/{pkg.name}')
    (NOTES/'delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
    print(json.dumps({c:[x['file'] for x in e['inputs']] for c,e in roles.items()},indent=1))

if __name__=='__main__':main()
