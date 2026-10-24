"""Bind successful local checks, current Git blobs and immutable historical families."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
BASE='186f08cfc9f4ff5f30089b7662ff911a59e16032'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def blob(sha,p):return subprocess.check_output(['git','show',f'{sha}:{p}'],cwd=ROOT)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
v=OUT/'validation-final-1'
assert json.loads((v/'results.json').read_text())=={'owned-unit':0,'check':0,'annotations':0,'full-suite':0}
before=json.loads((v/'source.json').read_text());after=json.loads((v/'source-after.json').read_text())
assert before['sources']==after
for p,h in after.items():
 assert digest(p)==h and hashlib.sha256(blob(head,p)).hexdigest()==h,p
dispatch=json.loads((OUT/'all-actions-dispatch-source-1.json').read_text())
for p,h in dispatch['sources'].items():
 assert digest(p)==h and hashlib.sha256(blob(dispatch['head'],p)).hexdigest()==h and hashlib.sha256(blob(head,p)).hexdigest()==h,p
static=json.loads((OUT/'citation-endpoints-final-main-1.json').read_text())
assert all(digest(p)==h for p,h in static['sha256'].items())
assert (OUT/'static-after-regeneration-1.exit').read_text().strip()=='0'
assert 'Ran 47 tests' in (OUT/'static-after-regeneration-1.log').read_text()
suite=(v/'full-suite.log').read_text();m=re.search(r'Ran (\d+) tests in ([\d.]+)s',suite)
assert m and int(m[1])==2065 and 'OK (skipped=16)' in suite
gui=[line for line in suite.splitlines() if line.startswith('test_scripted_sitting_produces_one_burst_snapshot_per_key_group ')]
assert len(gui)==1 and gui[0].endswith(' ... ok'),gui
skips=json.loads((OUT/'skip-inventory-final-1.json').read_text());assert len(skips['inherited_skips'])==16 and skips['T77_skips']==[]
assert 'Ran 134 tests' in (v/'owned-unit.log').read_text()
cli=(v/'check.log').read_text();assert re.findall(r'(?m)^(engine|interactive|goals|knockout)\s+PASS\b',cli)==['engine','interactive','goals','knockout']
assert '0078fad9859d4b4083a88707785e2cf0a49e1b6cddfa48bfec5aa765590e592f' in cli
assert '7de611c6dec2508bf8504a83a2c680fd253c1ff798ad2c9e1e6db79592034049' in cli
historical={}
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'experiments/E036-match-port/families'],cwd=ROOT,text=True).splitlines()
for p in paths:
 if p.endswith('/display/profile.json'):continue
 assert (ROOT/p).read_bytes()==blob(BASE,p),p
 historical[p]=digest(p)
receipt={'git_head':head,'local_source_count':len(after),'local_before_after_current_and_git_identical':True,'dispatch_head':dispatch['head'],'dispatch_input_count':len(dispatch['sources']),'dispatch_current_and_git_identical':True,'historical_family_files_preserved':historical,'historical_profile_only_changes_reference_path':True,'static_fingerprints_current':True,'suite':{'tests':int(m[1]),'seconds':float(m[2]),'sha256':hashlib.sha256((v/'full-suite.log').read_bytes()).hexdigest(),'inherited_skips':16,'T77_skips':[],'real_gui':gui[0]},'focused_tests':134,'static_tests':47,'CLI_PASS':['engine','interactive','goals','knockout']}
oldprofile=json.loads(blob(BASE,'experiments/E036-match-port/families/display/profile.json'))
profile=json.loads((ROOT/'experiments/E036-match-port/families/display/profile.json').read_text())
assert oldprofile.pop('reference')!=profile.pop('reference') and oldprofile==profile
(OUT/'main-validation-final-audit-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='historical_family_files_preserved'},indent=2))
