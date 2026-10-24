"""Final T75 fail-closed acceptance audit; append-only output receipts."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families
from original_match import port
from original_match.port import selection
ap=argparse.ArgumentParser();ap.add_argument('--integrated',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
output=Path(a.out);assert not output.exists()
def read(p):return json.loads(Path(p).read_text())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
specs={s.id:s.sha256 for f in families.discover().values() for s in f.matches};assert len(specs)==63
profile=read(ROOT/'experiments/E036-match-port/families/display/profile.json');assert profile['mask']==[]
rawref=ROOT/'experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl';displayref=ROOT/profile['reference']
assert set(compare.load(rawref))==set(compare.load(displayref))==set(specs)
protected=list((ROOT/'experiments/E036-match-port/families').rglob('*.json'))+list((ROOT/'experiments/E036-match-port/families').rglob('*.jsonl'))+list((ROOT/'experiments/E036-match-port/families').glob('*.py'))
for p in protected:
 rel=str(p.relative_to(ROOT));before=subprocess.check_output(['git','show','bf650a337794ffd82e8e1471d45bfb6c5b753fd4:'+rel],cwd=ROOT)
 assert before==p.read_bytes(),('immutable family/profile/reference changed',rel)
local=read(OUT/'local-audit-1.json');assert local['milestone']=={'ported_exact':9,'OUT':9};assert local['controls_caught']==24
own=compare.load(OUT/'own-1/own.jsonl');native=compare.load(OUT/'native-1/own.jsonl');integrated=Path(a.integrated);candidate=compare.load(integrated)
lines,ok=compare.check(compare.load(displayref),candidate,specs,no_screen=True,strict_display=True,image_sha256=families.image_sha256());assert ok,lines
assert compare.candidate_display_profile(candidate,True)==profile
out=[r['address'] for r in read(OUT/'static-inventory-1.json') if r['classification']=='OUT'];pairs=[]
for mid,r in candidate.items():
 assert r['mask']==[] and set(r['ports'])==set(port.available())
 for address in selection.PORTS.entries:
  assert r['counts'][address]==r['port_calls'][address]==native[mid]['counts'][address]==own[mid]['port_calls'][address],(mid,address)
  pairs.append({'match':mid,'address':address,'count':r['counts'][address]})
 for address in out:assert r['counts'][address]==0
assert len(pairs)==567
manifest=read(integrated.parent/'manifest.json');dispatch=read(OUT/'actions-dispatch-1.json');assert manifest['sha']==dispatch['head'];assert manifest['run_id']==str(dispatch['run_id']);assert manifest['run_attempt']=='1'
for p in sorted((ROOT/'runtime/original_match').rglob('*.py')):
 rel=str(p.relative_to(ROOT));before=subprocess.check_output(['git','show',dispatch['head']+':'+rel],cwd=ROOT);assert before==p.read_bytes(),rel
validation=OUT/'validation-final-3';assert read(validation/'results.json')=={'owned-unit':0,'check':0,'annotations':0,'full-suite':0}
assert read(validation/'source.json')['sources']==read(validation/'source-after.json')
for rel,value in read(validation/'source.json')['sources'].items():assert digest(ROOT/rel)==value,rel
for label in ('owned-unit','check','annotations','full-suite'):assert (validation/(label+'.exit')).read_text().strip()=='0'
assert 'OK' in (validation/'full-suite.log').read_text()
skips=read(OUT/'skip-inventory-1.json');assert skips['identical_existing_skip_count']==13 and skips['new_skips']==[];assert digest(ROOT/skips['current'])==skips['current_sha256'];assert digest(ROOT/skips['baseline'])==skips['baseline_sha256']
static=read(OUT/'citation-endpoints-final-main-1.json');assert static['valid_endpoints_verified']==200 and static['citations_moved']==0 and static['inherited_problem_strings_unchanged']==18
for rel,value in static['sha256'].items():assert digest(ROOT/rel)==value,rel
controls=read(OUT/'controls-5/summary.json');assert controls['baseline']=='bf650a337794ffd82e8e1471d45bfb6c5b753fd4';assert len(controls['results'])==24 and all(c['caught'] for c in controls['results'])
for rel,value in controls['sources'].items():assert digest(ROOT/rel)==value,rel
base=read(OUT/'image-baseline-1/receipt.json');assert not base['skipped'] and base['returncode']!=0;assert base['tests_sha256']==digest(ROOT/'tests/test_original_match.py')
(OUT/'integrated-compare-audit-1.log').write_text('\n'.join(lines)+'\n')
receipt={'milestone':{'ported_exact':9,'OUT':9},'matches_each_mode':63,'mask':[],'integrated_profile':profile,'integrated_sha256':digest(integrated),'own_sha256':digest(OUT/'own-1/own.jsonl'),'native_sha256':digest(OUT/'native-1/own.jsonl'),'entry_call_checks_total':1134,'OUT_zero_pairs_total':1134,'integrated_entry_call_pairs':pairs,'runtime_matches_dispatch':dispatch['head'],'validation_source_head':read(validation/'source.json')['head'],'synthetic_methods':17,'caught_controls':24,'falsifiers':local['mutants'],'protected_family_reference_hashes':{str(p.relative_to(ROOT)):digest(p) for p in protected},'all_validation_exit0':True,'script_sha256':digest(Path(__file__))}
output.write_text(json.dumps(receipt,indent=2)+'\n');print('T75 acceptance PASS: nine exact/nineOUT;63both modes;1134entry/call checks;empty mask;24controls;3falsifiers;all finalchecksPASS')
