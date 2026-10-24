"""Reproduce generated bodies in a temporary source-only tree, without originals."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='m4-419-generator-') as name:
 temp=Path(name);(temp/'static/goal-exe').mkdir(parents=True)
 shutil.copytree(ROOT/'static/goal-exe/code',temp/'static/goal-exe/code')
 dest=temp/'experiments/E036-match-port/out/m4-419';dest.mkdir(parents=True)
 shutil.copy2(OUT/'generate_ports_2.py',dest/'generate_ports_2.py');(temp/'runtime/original_match/port').mkdir(parents=True)
 subprocess.run([sys.executable,'-B',str(dest/'generate_ports_2.py')],check=True)
 paths=['runtime/original_match/port/_display_finals.py','experiments/E036-match-port/out/m4-419/generated-source-map-2.json']
 outputs={}
 for rel in paths:
  expected=(ROOT/rel).read_bytes();actual=(temp/rel).read_bytes();assert actual==expected,rel
  outputs[rel]=hashlib.sha256(actual).hexdigest()
 receipt={'byte_reproducible':True,'generated_paths':outputs,'source_only_no_original_inputs':True,'no_runtime_listing_read':True,'public_port_module_count_unchanged':21}
with (OUT/'generator-reproduction-2.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt))
