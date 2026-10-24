import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
old=ROOT/'experiments/E036-match-port/out/T74/validation-final-1/full-suite.log';new=OUT/'full-suite-4/full-suite.log'
extract=lambda p:[line for line in p.read_text().splitlines() if ' ... skipped ' in line]
a,b=extract(old),extract(new)
assert len(a)==13 and a==b,(a,b)
receipt={'baseline':str(old.relative_to(ROOT)),'baseline_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'current':str(new.relative_to(ROOT)),'current_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'identical_existing_skip_count':len(a),'new_skips':[],'rows':b}
(OUT/'skip-inventory-1.json').write_text(json.dumps(receipt,indent=2)+'\n');print('13 identical existing skips; zero added')
