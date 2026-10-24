"""Complete retry after the one isolated DOSBox-X crash; no changed assertions/skips."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'full-suite-4';OUT.mkdir(exist_ok=False);PY='/home/diego/.local/bin/python3.12'
paths=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+list((ROOT/'tests').glob('*.py')))
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();original=json.loads((OUT.parent/'validation-final-3/source.json').read_text())['sources'];assert before==original,'source changed since final3'
(OUT/'source.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sources':before,'slot_acquired':True,'reason':'complete rerun after isolated DOSBox-X SIGABRT in existing GuardTests; original failure retained'},indent=2)+'\n')
command=[PY,'-B','-m','unittest','discover','-s','tests','-v'];(OUT/'command.json').write_text(json.dumps(command,indent=2)+'\n')
with (OUT/'full-suite.log').open('x') as log:r=subprocess.run(command,cwd=ROOT,env={**os.environ,'PYTHONPATH':'runtime'},stdout=log,stderr=subprocess.STDOUT)
(OUT/'full-suite.exit').write_text(str(r.returncode)+'\n');after=hashes();(OUT/'source-after.json').write_text(json.dumps(after,indent=2)+'\n');assert before==after,'runtime/tests changed during full suite'
raise SystemExit(r.returncode)
