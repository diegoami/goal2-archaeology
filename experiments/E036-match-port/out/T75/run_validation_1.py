import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'validation-1';OUT.mkdir(exist_ok=False)
PY='/home/diego/.local/bin/python3.12'
sources=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+[ROOT/'tests/test_port_selection.py',ROOT/'tests/test_original_match.py'])
(OUT/'source.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}},indent=2)+'\n')
commands=[('units',['tools/heavy.sh','T75-unit-1','--',PY,'-B','-m','unittest','tests.test_port_selection','tests.test_original_match']),('check',[PY,'-B','-m','original_match.check','--cache','.cache/dl','--ports','menus,selection'])]
for label,command in commands:
 (OUT/(label+'-command.json')).write_text(json.dumps(command,indent=2)+'\n')
 with (OUT/(label+'.log')).open('x') as log:r=subprocess.run(command,cwd=ROOT,env={**os.environ,'PYTHONPATH':'runtime','HARNESS_HEAVY_SLOTS':'8'},stdout=log,stderr=subprocess.STDOUT)
 (OUT/(label+'.exit')).write_text(str(r.returncode)+'\n')
 if r.returncode:raise SystemExit(r.returncode)
