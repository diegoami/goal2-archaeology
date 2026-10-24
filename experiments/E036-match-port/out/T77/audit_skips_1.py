"""Bind final test count and all skips to the fixed actual pre-task baseline."""
from pathlib import Path
import ast,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
BASE='186f08cfc9f4ff5f30089b7662ff911a59e16032'
log=(OUT/'validation-final-1/full-suite.log').read_text()
match=re.search(r'Ran (\d+) tests in ([\d.]+)s',log);assert match and 'OK (skipped=16)' in log
current_skips={}
for line in log.splitlines():
 m=re.match(r'^\w+ \(([\w.]+)\) \.\.\. skipped (.*)$',line)
 if m:current_skips[m[1]]=m[2]
old=json.loads((ROOT/'experiments/E036-match-port/out/T76/skip-inventory-final-1.json').read_text())['expected_current_skips']
assert current_skips==old,(current_skips,old)
unchanged={}
for module in {key.split('.')[0] for key in old}:
 p='tests/'+module+'.py';before=subprocess.check_output(['git','show',BASE+':'+p],cwd=ROOT);after=(ROOT/p).read_bytes();assert before==after,p;unchanged[p]=hashlib.sha256(after).hexdigest()

def methods(data):
 tree=ast.parse(data);return {c.name+'.'+n.name for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith('test_')}
changes={};net=0
for name in ('test_port_quick.py','test_port_rare.py','test_e036_family.py','test_e036_compare.py'):
 p='tests/'+name;now=methods((ROOT/p).read_text())
 r=subprocess.run(['git','show',BASE+':'+p],cwd=ROOT,capture_output=True,text=True);before=methods(r.stdout) if r.returncode==0 else set()
 changes[p]={'added':sorted(now-before),'removed':sorted(before-now)};net+=len(now)-len(before)
assert net==22,net
assert int(match[1])==2043+net,(match[1],net)
assert not any(key.startswith(('test_port_quick.','test_port_rare.')) for key in current_skips)
receipt={'fixed_baseline':BASE,'baseline_tests':2043,'net_added_test_methods':net,'expected_final_tests':2065,'actual_final_tests':int(match[1]),'duration_s':float(match[2]),'inherited_skips':current_skips,'baseline_skip_sources_unchanged':unchanged,'changed_test_methods':changes,'T77_skips':[]}
(OUT/'skip-inventory-final-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS:2065 tests,16 inherited skips,0 T77 skips; fixed baseline',BASE)
