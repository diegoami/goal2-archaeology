"""Produce a new unhooked reference for the strict, empty-mask display profile.

Every game field and memory digest must match T57. Only the opaque event digest
changes, because the already-tested projector removes the duplicate screen hash.
No port or variant is installed and no historical reference is modified.
"""
import concurrent.futures
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
E036=ROOT/'experiments/E036-match-port'
sys.path.insert(0,str(E036))
import compare,families,family,records

OUT=E036/'out/T73/projected-reference-desktop-20261023-v1'
OUT.mkdir(exist_ok=False)
PROFILE=E036/'families/display/profile.json'
MASK=E036/'families/display/mask.json'
manifest_bytes=PROFILE.read_bytes();mask_bytes=MASK.read_bytes()
manifest=json.loads(manifest_bytes)
assert json.loads(mask_bytes)==manifest['mask']==[]
REFERENCE=ROOT/manifest['reference']
assert not REFERENCE.exists(),'Refuse to replace a measured reference'
projector=inspect.getsource(family.display_events_digest).encode()
(OUT/'launch.json').open('x').write(json.dumps({
    'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'ports':[],'variant':None,'mask':[],'profile_selected':True,
    'projector_sha256':hashlib.sha256(projector).hexdigest(),
    'reference':str(REFERENCE.relative_to(ROOT)),
},indent=2)+'\n')
plan=json.loads(subprocess.check_output([sys.executable,str(E036/'shards.py'),'plan',
                                       '--family','ALL','--shards','16'],cwd=ROOT))
(OUT/'plan.json').open('x').write(json.dumps(plan,indent=2)+'\n')
env=dict(os.environ,HARNESS_HEAVY_SLOTS='32')

def run(shard):
    i=shard['shard']
    cmd=[sys.executable,'-B',str(E036/'family.py'),'--family','ALL','--only',shard['only'],
         '--mask',str(MASK),'--workers','2','--time-limit','6000','--stretch-limit','1200',
         '--out',str(OUT/f'shard-{i}.jsonl')]
    started=time.monotonic()
    with (OUT/f'shard-{i}.log').open('x') as log:
        log.write('COMMAND: '+repr(cmd)+'\n');log.flush()
        result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    return {'shard':i,'exit_code':result.returncode,'seconds':time.monotonic()-started}

with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    results=list(pool.map(run,plan['include']))
(OUT/'timing.json').open('x').write(json.dumps(results,indent=2)+'\n')
if any(r['exit_code'] for r in results):
    sys.exit('Reference producer shard failed; preserve and inspect its log')
assert PROFILE.read_bytes()==manifest_bytes and MASK.read_bytes()==mask_bytes
assert inspect.getsource(family.display_events_digest).encode()==projector
with (OUT/'collect.log').open('x') as log:
    subprocess.run([sys.executable,str(E036/'shards.py'),'collect','--family','ALL','--out',str(REFERENCE),
                    *[str(OUT/f'shard-{s["shard"]}.jsonl') for s in plan['include']]],
                   cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
base=compare.load(E036/'out/T57/reference.jsonl')
fresh=compare.load(REFERENCE)
expected={k:v for f in families.select('ALL',families.discover()) for k,v in f.expected().items()}
assert set(fresh)==set(expected) and len(fresh)==62
for mid,r in fresh.items():
    old=base[mid]
    assert 'ports' not in r and r['mask']==[] and compare.completed(r) is None
    assert r['spec_sha256']==expected[mid] and r['image_sha256']==families.image_sha256()
    assert compare.differences(old,r)==[('events','')],(mid,compare.differences(old,r))
    assert r['events']['count']==old['events']['count']
    assert r['events']['sha256']!=old['events']['sha256']
(OUT/'audit.json').open('x').write(json.dumps({
    'matches':62,'unhooked':True,'mask':[],
    'all_non_event_fields_equal_T57':True,'event_counts_equal':True,
    'event_digest_projection':'only full_time.data.screen_sha256 (unit-verified)',
    'reference_sha256':hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
    'projector_sha256':hashlib.sha256(projector).hexdigest(),
},indent=2)+'\n')
print('COMPLETE: 62 projected unhooked references; all non-screen/game/memory fields unchanged',flush=True)
