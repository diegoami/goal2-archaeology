import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
receipt={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'runtime/original_match').rglob('*.py'))}}
(OUT/'probe-source-2.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (OUT/'probe-2.log').open('x') as log:
 r=subprocess.run(['/home/diego/.local/bin/python3.12','-B','experiments/E036-match-port/family.py','--family','S','--only','S/decisions-70','--ports','menus,selection','--time-limit','1800','--count','0791:E44F,0791:E022,0791:DE27,0791:DE51,0791:E2A0,0791:E949,0791:EA09,1771:5532,1771:53E8','--out',str(OUT/'probe-2.jsonl')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
(OUT/'probe-2.exit').write_text(str(r.returncode)+'\n')
