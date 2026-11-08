"""Verify #695 immutable public/source bindings; --private additionally hashes retained raw artifacts."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];FOLDER=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--private',action='store_true');a=p.parse_args()
value=json.loads((FOLDER/'acceptance-v1.json').read_text())
for group in ('sources_sha256','evidence_sha256'):
 for name,expected in value[group].items():
  assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,(group,name)
assert hashlib.sha256((ROOT/'runtime/original_match/README.md').read_bytes()).hexdigest()==value['api_readme_sha256']
if a.private:
 for name,expected in value['private_sha256'].items():
  assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==expected,('private',name)
comparison=json.loads((FOLDER/'comparison-v2.json').read_text())
assert len(comparison['natural_pairs'])==6 and len(comparison['within_backend_checkpoint_replays'])==2
assert len(comparison['legacy_prechange_pairs'])==2 and len(comparison['prepared_controls'])==2
assert comparison['events_exclusions']==[] and comparison['memory_mask']==[]
assert comparison['mutation_omission_rejected']
print(f"#695 bindings PASS: {len(value['sources_sha256'])} sources, {len(value['evidence_sha256'])} public files"
      +(f", {len(value['private_sha256'])} private artifacts" if a.private else ''))
