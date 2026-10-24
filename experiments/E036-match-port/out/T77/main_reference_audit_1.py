"""Independent immutable-reference and original-only provenance audit."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families
BASE='186f08cfc9f4ff5f30089b7662ff911a59e16032'
old_display='experiments/E036-match-port/families/display/reference-all-set-piece-20261024-v2.jsonl'
new_display='experiments/E036-match-port/families/display/reference-all-rare-20261024-v1.jsonl'
raw_path='experiments/E036-match-port/families/R.reference-20261024-v2.jsonl'
def old(path):return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT)
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
expected={mid:d for f in families.discover().values() for mid,d in f.expected().items()}
historical={}
for f in families.discover().values():
 if f.name=='R':continue
 path=str(f.reference)
 assert (ROOT/path).read_bytes()==old(path),path
 historical.update(compare.load(ROOT/path))
 assert all(expected[mid]==r['spec_sha256'] for mid,r in historical.items())
assert len(historical)==64
raw=compare.load(ROOT/raw_path)
assert len(raw)==10
old_r=ROOT/'experiments/E036-match-port/families/R.reference-20261024-v1.jsonl'
assert (ROOT/raw_path).read_bytes().startswith(old_r.read_bytes())
display=compare.load(ROOT/new_display)
assert len(display)==74
assert (ROOT/old_display).read_bytes()==old(old_display)
assert (ROOT/new_display).read_bytes().startswith(old(old_display))
projection=compare.load(OUT/'R-display-original-1.jsonl')
assert set(projection)==set(raw)
lines,ok=compare.check(projection,{k:display[k] for k in raw},{k:expected[k] for k in raw},image_sha256=families.image_sha256())
assert ok,lines
diffs={}
for mid,r in raw.items():
 assert 'ports' not in r and compare.completed(r) is None and r['mask']==[]
 assert 'ports' not in projection[mid] and projection[mid]['mask']==[]
 assert r['spec_sha256']==expected[mid]
 diffs[mid]=compare.differences(r,projection[mid],False)
 assert all(field=='events' for field,where in diffs[mid]),(mid,diffs[mid])
native=compare.load(OUT/'native-1/own.jsonl'); assert len(native)==64
reference={**historical,**raw};candidate={**native,**raw}
lines,ok=compare.check(reference,candidate,expected,image_sha256=families.image_sha256());assert ok,lines
receipt={'baseline':BASE,'old_specs_preserved':len(historical),'original_only_completed_records':len(candidate),'old_raw_reference_bytes_preserved':True,'old_display_prefix_preserved':True,'R_v1_prefix_preserved':True,'R_display_independently_recorded':True,'mask':[],'raw_vs_display_differences':diffs,'sha256':{p:sha(p) for p in [old_display,new_display,raw_path]}}
(OUT/'main-reference-extension-audit-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('raw_vs_display_differences','sha256')},indent=2))
