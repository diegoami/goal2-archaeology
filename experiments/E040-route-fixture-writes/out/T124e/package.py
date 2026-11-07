"""Create a new immutable acceptance index; historical versions remain untouched."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dir',required=True);a=ap.parse_args();out=Path(a.dir);out.mkdir()
    rel=lambda p:str(p.relative_to(ROOT))
    phases=['continental','world-qualifying','world-finals','next-continental']
    natural={p:rel(HERE/f'natural-{p}-proof-v3.jsonl') for p in phases}
    plain=[rel(HERE/f'plain-{p}-v5.jsonl') for p in phases]+[rel(HERE/'plain-pushed-back-v5.jsonl'),rel(HERE/'plain-continental-host-v4.jsonl')]
    controlled=[rel(HERE/'controlled-continental-host-proof-v4.jsonl')]
    inputs=[rel(HERE/f'natural-{p}-input-v{2 if p=="world-qualifying" else 1}.jsonl') for p in phases]+[rel(HERE/'controlled-continental-host-input-v4.jsonl')]
    control=rel(HERE/'controlled-pages-falsifiers-v1.jsonl');sources={};private={}
    def visit(v):
        if isinstance(v,dict):
            if str(v.get('path','')).startswith('.cache/') and 'sha256' in v:
                if v['path'] in private:assert private[v['path']]==v
                private[v['path']]=v
            for z in v.values():visit(z)
        elif isinstance(v,list):
            for z in v:visit(z)
    for path in list(natural.values())+plain+controlled+inputs+[control]:
        rows=list(map(json.loads,(ROOT/path).read_text().splitlines()));visit(rows)
        # Input producer headers retain their historical source versions. Final
        # measurement headers bind the current frozen source below.
        if path not in inputs:
            for p,h in rows[0]['source_hashes'].items():
                assert p not in sources or sources[p]==h
                sources[p]=h
    for row in map(json.loads,(HERE.parent/'T124d/natural-inputs-v1.jsonl').read_text().splitlines()):
        if row.get('status')=='constructed' and row['phase'] in ('groups','last16'):visit(row['checkpoint'])
    for p in ['tests/test_port_stages.py','tests/test_port_stage_world.py',
       'experiments/E040-route-fixture-writes/out/T124d/reference.py','experiments/E040-route-fixture-writes/out/T124d/prepare.py',
       'experiments/E040-route-fixture-writes/out/T124e/continental_host.py','experiments/E040-route-fixture-writes/out/T124e/controls.py']:
        sources[p]=sha((ROOT/p).read_bytes())
    files={rel(p):sha(p.read_bytes()) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and not any(x.startswith('acceptance') for x in p.relative_to(HERE).parts)}
    for p in ['experiments/E040-route-fixture-writes/out/T124d/natural-inputs-v1.jsonl','static/goal-exe/annotations/routines.tsv','static/goal-exe/named/index.tsv','static/goal-exe/named/seg_000E_04.c','static/goal-exe/named/seg_000E_05.c']:
        files[p]=sha((ROOT/p).read_bytes())
    x={'schema':'t124e-acceptance/1','base_commit':'4e8c34201473c46e058daf96c0b559c21fb41116',
      'source_freeze_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
      'source_hashes':sources,'file_hashes':files,'private_files':private,'natural_tails':natural,
      'controlled_tails':controlled,'plain_compositions':plain,'input_receipts':inputs,'controlled_pages':control,
      'measurement_modes':{'natural_and_controlled_tail':'strictProver new-body/selected-real-helper hybrid;009C remains ORIGINAL; fullmemory/all16regs equality as measured',
       'plain':'raw supplied Image, all reached real ports incl009C/0644/0723/08DD; SAME Route.Keys via adapter; no original opcode/savestate fallback; exact observed dedicated below-entry-SP deadstack only; every register difference reported'},
      'limits':'four PRIMARY natural inputs; continental-host/two-manager edits DECLARED SYNTHETIC. No sealed Route/year-rollover claim. Historical calibration receipts immutable; final lists above are acceptance.'}
    with (out/'index.json').open('x') as f:f.write(json.dumps(x,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
