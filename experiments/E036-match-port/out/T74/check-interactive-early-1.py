"""Real menu-port save/resume check while translations are completed; not final-suite evidence."""
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import check, Image
from original_match.assets import reference_image
out=Path(__file__).resolve().parent
source=ROOT/'runtime/original_match/port/menus.py'
receipt={'menus_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
image=Image.from_savestate(reference_image(ROOT/'.cache/dl'))
check.MATCH=check.ported(['menus'])
check.example.Match=check.MATCH
started=time.time()
ok,details=check.interactive(image)
receipt.update(ok=ok,details=details,wall_s=time.time()-started)
(out/'check-interactive-early-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2),flush=True)
raise SystemExit(0 if ok else 1)
