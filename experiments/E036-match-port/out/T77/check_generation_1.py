"""Reproduce generated ports in an isolated temporary tree; never touch live source."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(prefix='T77-reproduce-') as name:
 tree=Path(name);dest=tree/'experiments/E036-match-port/out/T77';dest.mkdir(parents=True)
 generator=dest/'generate_ports_1.py';shutil.copy(OUT/generator.name,generator)
 code=tree/'static/goal-exe/code';code.parent.mkdir(parents=True);code.symlink_to(ROOT/'static/goal-exe/code',target_is_directory=True)
 sizes=tree/'experiments/E036-match-port/out/backlog/sizes-20261017d.json';sizes.parent.mkdir(parents=True);shutil.copy(ROOT/sizes.relative_to(tree),sizes)
 (tree/'runtime/original_match/port').mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(generator)],check=True)
 checks={}
 for rel in ('runtime/original_match/port/quick.py','runtime/original_match/port/rare.py','experiments/E036-match-port/out/T77/generated-source-map-1.json'):
  assert (tree/rel).read_bytes()==(ROOT/rel).read_bytes(),rel;checks[rel]=sha(ROOT/rel)
 raw={row['listing']:sha(ROOT/row['listing']) for row in json.loads((OUT/'listing-inventory-1.json').read_text())}
 receipt={'generator_sha256':sha(OUT/generator.name),'reproduced_byte_identical':checks,'raw_listing_sha256':raw,'live_source_untouched':True}
 (OUT/'generation-reproduction-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('PASS: isolated generation exactly reproduces both ports and source map')
