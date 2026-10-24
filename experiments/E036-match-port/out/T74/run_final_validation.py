"""Final source-bound validation, serial after the local own family releases its slots."""
import hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PYTHON='/home/diego/.local/bin/python3.12'
while not (OUT/'own-menus-desktop-2/compare.exit').exists():
    if (OUT/'own-menus-desktop-2/exits.json').exists():
        exits=json.loads((OUT/'own-menus-desktop-2/exits.json').read_text())
        if any(exits.values()):raise SystemExit('own2 failed; final validation not started')
    time.sleep(15)
if (OUT/'own-menus-desktop-2/compare.exit').read_text().strip()!='0':
    raise SystemExit('own2 differs; final validation not started')
folder=OUT/'validation-final-1';folder.mkdir(exist_ok=False)
source_paths=sorted((ROOT/'runtime/original_match').rglob('*.py'))+[ROOT/'tests/test_port_menus.py',ROOT/'tests/test_original_match.py',ROOT/'tests/test_e036_family.py',ROOT/'tests/test_e036_compare.py']
receipt={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}}
(folder/'source.json').write_text(json.dumps(receipt,indent=2)+'\n')
env={**os.environ,'PYTHONPATH':'runtime','HARNESS_HEAVY_SLOTS':'8'}
commands=[
 ('owned-unit',[str(ROOT/'tools/heavy.sh'),'--slots','8','T74-owned-final','--',PYTHON,'-B','-m','unittest','tests.test_port_menus','tests.test_original_match']),
 ('check',[PYTHON,'-B','-m','original_match.check','--cache','.cache/dl','--ports','menus','--json',str(folder/'check.json')]),
 ('annotations',[PYTHON,'tools/static/check_annotations.py']),
 ('full-suite',[str(ROOT/'tools/heavy.sh'),'--slots','8','T74-full-final','--',PYTHON,'-B','-m','unittest','discover','-s','tests','-v']),
]
results={}
for name,command in commands:
    (folder/(name+'-command.json')).write_text(json.dumps(command,indent=2)+'\n')
    with (folder/(name+'.log')).open('x') as log:
        r=subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    (folder/(name+'.exit')).write_text(str(r.returncode)+'\n');results[name]=r.returncode
    if r.returncode:break
(folder/'results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if len(results)==len(commands) and not any(results.values()) else 1)
