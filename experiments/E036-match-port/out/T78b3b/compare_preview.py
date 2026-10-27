"""Strict existing-record comparison for this bounded facade diagnostic."""
import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(root/'runtime'),str(root/'experiments/E036-match-port')]
import compare,records
folder=Path(__file__).resolve().parent
version=sys.argv[1]
a=records.loads((folder/f'quick-original-{version}.jsonl').read_text());records.validate(a)
b=records.loads((folder/f'quick-port-{version}.jsonl').read_text());records.validate(b)
d=compare.differences(a,b,no_screen=True,strict_display=True)
report={'id':a['id'],'reference':'unhooked original','candidate':'preserved T78b port facade, positive Unicorn import denial','strict_display':True,'no_screen':True,'mask':a['mask'],'differences':d,'pass':not d}
(folder/f'quick-comparison-{version}.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(bool(d))
