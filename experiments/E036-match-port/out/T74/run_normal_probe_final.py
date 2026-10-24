"""Selected normal probes on the final frozen runtime, before the accepted full family."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PYTHON='/home/diego/.local/bin/python3.12'
paths=sorted((ROOT/'runtime/original_match').rglob('*.py'))
receipt={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(OUT/'normal-final-probe-source-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (OUT/'normal-final-probe-1.log').open('x') as log:
 r=subprocess.run([PYTHON,'-B','experiments/E036-match-port/family.py','--family','S',
    '--only','S/decisions-70,S/no-managed-side','--ports','menus','--workers','2',
    '--time-limit','1800','--out',str(OUT/'normal-final-probe-1.jsonl')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
(OUT/'normal-final-probe-1.exit').write_text(str(r.returncode)+'\n')
raise SystemExit(r.returncode)
