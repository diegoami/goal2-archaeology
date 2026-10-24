"""Reconcile T75's historical suite with the fixed actual pre-task T76 baseline."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
BASE='411fdefa0287f984e5c0efc1fb1c585263c67690'
historical=ROOT/'experiments/E036-match-port/out/T75/full-suite-4/full-suite.log'
current=OUT/'validation-final-1/full-suite.log'
def skip_rows(path):
 rows={}
 for line in path.read_text().splitlines():
  m=re.match(r'^\w+ \(([^)]+)\) \.\.\. skipped (.+)$',line)
  if m:rows[m[1]]=m[2]
 return rows
old=skip_rows(historical);now=skip_rows(current);assert len(old)==13 and len(now)==16
p='tests/test_build_guard_mutable.py'
baseline_source=subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT)
assert baseline_source==(ROOT/p).read_bytes()
methods=[n.name for n in ast.walk(ast.parse(baseline_source)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
assert len(methods)==5
extra={k:v for k,v in now.items() if k not in old}
assert len(extra)==3 and all(k.startswith('test_build_guard_mutable.OriginalCheckpoint.') for k in extra)
assert all(k.rsplit('.',1)[1] in methods for k in extra)
assert all(now.get(k)==v for k,v in old.items())
assert all('private unchanged E031 checkpoint absent' in v for v in extra.values())
files=['tests/test_port_takers.py','tests/test_original_match.py','tests/test_e036_family.py','tests/test_e036_compare.py']
changes={}
def names(raw):
 return {n.name for n in ast.walk(ast.parse(raw)) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
for f in files:
 r=subprocess.run(['git','show',BASE+':'+f],cwd=ROOT,capture_output=True)
 before=names(r.stdout) if r.returncode==0 else set()
 after=names((ROOT/f).read_bytes());assert before<=after
 changes[f]=sorted(after-before)
assert sum(map(len,changes.values()))==11
assert 'Ran 2027 tests' in historical.read_text()
assert 'Ran 2043 tests' in current.read_text()
source=json.loads((OUT/'validation-final-1/source.json').read_text())
after=json.loads((OUT/'validation-final-1/source-after.json').read_text())
assert source['slot_acquired'] and source['sources']==after
assert all(hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==d for f,d in after.items())
receipt={'fixed_baseline':BASE,'historical_T75_tests':2027,'preexisting_T85_tests':5,
         'T76_added_tests':11,'expected_current_tests':2043,'historical_T75_skips':old,
         'preexisting_baseline_T85_skips':extra,'expected_current_skips':now,
         'baseline_T85_source_unchanged':True,'baseline_T85_sha256':hashlib.sha256(baseline_source).hexdigest(),
         'T76_new_skips':[],'added_test_methods':changes,'final_sources_unchanged':True}
(OUT/'skip-inventory-final-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('2043 tests = historical2027 + preexisting baselineT85 5 + T76 11')
print('16 inherited skips = historical13 + preexisting baselineT85 3; no new skips')
