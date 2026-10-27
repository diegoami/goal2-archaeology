"""Reproduce the bounded public-CLI comparison, including input/backend binding."""
import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(root/'runtime'),str(root/'experiments/E036-match-port')]
import compare,records,family,families
folder=Path(__file__).resolve().parent
candidate=records.read_log(folder/'public-reference-v1.jsonl')[0]
profile=compare.candidate_display_profile({candidate['id']:candidate},True)
assert profile is not None
reference=next(r for r in records.read_log(root/profile['reference']) if r['id']==candidate['id'])
spec=next(s for f in families.discover().values() for s in f.matches if s.id==candidate['id'])
assert candidate['engine']=='port' and 'display' in candidate['ports']
assert 'ports' not in reference and reference.get('engine','original')=='original'
for key in ('id','family','spec_sha256','image_sha256','kit','mask'):
    assert reference[key]==candidate[key],key
assert candidate['spec_sha256']==spec.sha256 and candidate['image_sha256']==spec.image_sha256
assert candidate['mask']==profile['mask'] and records.is_completed(reference) and records.is_completed(candidate)
differences=compare.differences(reference,candidate,no_screen=True,strict_display=True)
print(json.dumps({'id':candidate['id'],'inputs_bound':True,'reference_unhooked':True,
    'engine':candidate['engine'],'strict_display':True,'no_screen':True,'mask':candidate['mask'],
    'differences':differences,'pass':not differences}))
raise SystemExit(bool(differences))
