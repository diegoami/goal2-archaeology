"""Acquire the heavy slot first, then bind final sources and run checks serially."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent;PY='/home/diego/.local/bin/python3.12'
if '--inside' not in sys.argv:
 for receipt in ('own-1/compare.exit','native-1/compare.exit'):
  while not (OUT/receipt).exists():time.sleep(10)
  if not receipt.endswith('.json') and (OUT/receipt).read_text().strip()!='0':raise SystemExit(receipt+' failed; final validation not started')
 raise SystemExit(subprocess.call(['tools/heavy.sh','--slots','8','T76-final-validation-3','--',PY,'-B',str(Path(__file__).resolve()),'--inside'],cwd=ROOT,env={**os.environ,'HARNESS_HEAVY_SLOTS':'8'}))
folder=OUT/'validation-final-1';folder.mkdir(exist_ok=False)
paths=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+list((ROOT/'tests').glob('*.py'))+[ROOT/'experiments/E036-match-port'/p for p in ('family.py','families.py','compare.py','records.py')])
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
receipt={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sources':hashes(),'slot_acquired':True}
(folder/'source.json').write_text(json.dumps(receipt,indent=2)+'\n')
commands=[('owned-unit',[PY,'-B','-m','unittest','tests.test_port_takers','tests.test_original_match']),('check',[PY,'-B','-m','original_match.check','--cache','.cache/dl','--ports','takers','--json',str(folder/'check.json')]),('annotations',[PY,'tools/static/check_annotations.py']),('full-suite',[PY,'-B','-m','unittest','discover','-s','tests','-v'])]
results={}
for label,command in commands:
 (folder/(label+'-command.json')).write_text(json.dumps(command,indent=2)+'\n')
 with (folder/(label+'.log')).open('x') as log:r=subprocess.run(command,cwd=ROOT,env={**os.environ,'PYTHONPATH':'runtime'},stdout=log,stderr=subprocess.STDOUT)
 (folder/(label+'.exit')).write_text(str(r.returncode)+'\n');results[label]=r.returncode
 if r.returncode:break
receipt_after=hashes();(folder/'source-after.json').write_text(json.dumps(receipt_after,indent=2)+'\n')
assert receipt['sources']==receipt_after,'runtime/tests changed during final validation'
(folder/'results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if len(results)==len(commands) and not any(results.values()) else 1)
