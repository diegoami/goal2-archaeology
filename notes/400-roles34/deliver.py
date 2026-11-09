#!/usr/bin/env python3
"""Build delivery.json and the t131-named private copies from the raw records (read-only on them).

The raw steps.jsonl rows of search-r1 (the decision, its branch of Space, Return, Return) and preceding-r1 are the
source; this script only names, copies and indexes. Run once the search has finished.
"""
import hashlib,json,shutil,sys
from pathlib import Path
import frames
ROOT=Path(__file__).resolve().parents[2];NOTES=ROOT/'notes/400-roles34'
OUT=ROOT/'.cache/400-roles34/delivery'
DRIVE='goal2drive:goal2-archaeology/400-roles34-20261109'
def sha(b):return hashlib.sha256(b).hexdigest()
def rows(name):return [json.loads(l) for l in (NOTES/name/'steps.jsonl').read_text().splitlines()]
def record(name):return json.loads((NOTES/name/'record.json').read_text())

def item(row,tag,role,step,preceding=None):
    raw=(ROOT/row['state']['file']).read_bytes();digest=sha(raw);assert digest==row['state']['sha256']
    ext=Path(row['state']['file']).suffix
    name=f't131-{digest[:16]}-role{role}-{tag}{ext}'
    OUT.mkdir(parents=True,exist_ok=True);(OUT/name).write_bytes(raw)
    f=row['frame']
    out=dict(step=step,label=row['label'],file=name,sha256=digest,bytes=len(raw),site=row['site'],kind=row['kind'],poll=row['poll'],
             keys=row['keys'],keys_sha256=row['keys_sha256'],raw_row=f"{row['_attempt']}#{row['n']}",
             frame=None if f is None else {k:f[k] for k in ('site','cpu','ss','sp','chain','role','side','country','country_name','opponent','opponent_name','highlight','pick','stored_pick','eleven','pick_in_eleven','pick_status','pick_position','manager_byte','minute','rng_main','rng_aux')},
             private=f'{DRIVE}/{name}',readback=f'.cache/400-roles34/readback/{name}')
    if preceding:out['preceding']=preceding
    return out

def main():
    search=rows('search-r1');rec=record('search-r1')
    for r in search:r['_attempt']='search-r1'
    prec=rows('preceding-r1')
    for r in prec:r['_attempt']='preceding-r1'
    stop=rows('stop-r1')
    for r in stop:r['_attempt']='stop-r1'
    reach=record('reach-r1')
    by={r['label']:r for r in search}
    roles={}
    for role in (3,4):
        if f'role{role}-decision-before-space' not in by:continue
        d=by[f'role{role}-decision-before-space']
        entry=dict(round=d['round'],run_index=d['run_index'],inputs=[])
        if role==3:
            p=prec[0];entry['inputs'].append(item(p,'preceding-wait',3,0))
        steps=[('decision-before-space','decision-before-space'),('space-pitch-read','space-pitch-read'),
               ('return-back-at-selector','return-back-at-selector'),('return-accept','return-accept')]
        for i,(label,tag) in enumerate(steps,1):
            entry['inputs'].append(item(by[f'role{role}-{label}'],tag,role,i))
        roles[str(role)]=entry
    s=stop[0]
    unchanged=item(s,'unchanged-core-stop',3,0)
    keys={}
    for role,e in roles.items():
        decision=next(x for x in e['inputs'] if x['label'].endswith('decision-before-space'))
        meta,_=frames.read_g2core((OUT/decision['file']).read_bytes())
        keys[role]=meta['keys']
        (NOTES/f'keys-role{role}.json').write_text(json.dumps(dict(role=role,keys=meta['keys'],count=len(meta['keys']),sha256=sha(bytes(meta['keys']))))+'\n')
    delivery=dict(schema='T131-original-inputs/1',covered_roles=[int(r) for r in roles],
                  remaining=[f'role{r}_{n}' for r,n in ((3,'penalty'),(4,'free_kick')) if str(r) not in roles],
                  search_status=rec.get('status'),search_bound=dict(bound_s=rec.get('bound_s'),max_round=rec.get('max_round')),
                  core=dict(commit=reach['core_source_commit'],tree_sha256=reach['core_tree_sha256']),
                  source=dict(date_call_sha256=reach['date_call_sha256'],goal_dat_sha256=reach['goal_dat_sha256'],
                              private='goal2drive:e039-r0005-date-call.sav'),
                  menu=search[0]['state'] and rec['menu'],roles=roles,unchanged_core_stop=unchanged)
    (NOTES/'delivery.json').write_text(json.dumps(delivery,indent=2)+'\n')
    print(json.dumps({r:[x['file'] for x in e['inputs']] for r,e in roles.items()},indent=1))

if __name__=='__main__':main()
