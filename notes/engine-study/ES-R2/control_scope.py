#!/usr/bin/env python3
"""Count legacy calculation annotations as model examples, not independent source falsifiers."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
LEDGERS={'T101a':1,'T101b':1,'T101c':1,'T102a':3,'T102b':1,'T102c':1,'T103a':2,'T103b':1,'T103c':2,'T104a':1,'T104b':1,'T104c':2,'T104d':2,'T104e':1,'T105a':2,'T105b':2,'T108a':1,'T108b':2}


def build():
    rows=[];hashes={}
    for task,version in LEDGERS.items():
        path=ROOT/f'notes/engine-study/{task[:4]}/{task}-v{version}.json';raw=path.read_bytes();hashes[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest();data=json.loads(raw)
        for name,claim in data['calculations'].get('controls',{}).items():rows.append(dict(task=task,name=name,legacy_label=claim,classification='model consistency annotation; not counted as a source-bound falsifier'))
    return dict(scope=__doc__,legacy_model_annotations=len(rows),source_bound_falsifiers_from_this_count=0,annotations=rows,ledger_sha256=hashes,source_check='listing_guards.py independently checks named instructions and altered-listing negatives; no engine execution')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');ap.add_argument('--receipt',type=Path);a=ap.parse_args();data=build()
    if a.check:assert json.loads((ROOT/'notes/engine-study/ES-R2/model-annotation-scope-v1.json').read_text())==data
    if a.receipt:
        with a.receipt.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    print(f'PASS: {data["legacy_model_annotations"]} legacy model annotations; zero independent source falsifiers inferred from their labels')


if __name__=='__main__':main()
