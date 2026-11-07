"""Create a fresh immutable T124f acceptance directory; never rewrite evidence."""
import argparse,hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def sha(v):return hashlib.sha256(v).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dir',required=True);opts=ap.parse_args();out=Path(opts.dir);out.mkdir()
    rel=lambda p:str(p.relative_to(ROOT));natural={c:rel(HERE/f'natural-{c}-v1.jsonl') for c in ('continental','world')}
    plain=[rel(HERE/f'plain-{c}-{m}-v1.jsonl') for c in ('continental','world') for m in ('raw','state')]
    direct=rel(HERE/'direct-branches-v1.jsonl');sources={};private={}
    def visit(v):
        if isinstance(v,dict):
            if str(v.get('path','')).startswith('.cache/') and 'sha256' in v:
                if v['path'] in private:assert private[v['path']]==v
                private[v['path']]=v
            for z in v.values():visit(z)
        elif isinstance(v,list):
            for z in v:visit(z)
    for path in list(natural.values())+plain+[direct]:
        rr=list(map(json.loads,(ROOT/path).read_text().splitlines()));visit(rr)
        for p,h in rr[0]['source_hashes'].items():
            assert p not in sources or sources[p]==h;sources[p]=h
    from tests.test_port_stages import IMAGE,IMAGE_SHA
    private[str(IMAGE.relative_to(ROOT))]={'path':str(IMAGE.relative_to(ROOT)),'sha256':IMAGE_SHA,'kind':'published-savestate'}
    files={rel(p):sha(p.read_bytes()) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and not any(n.startswith('acceptance') for n in p.relative_to(HERE).parts)}
    for p in ['static/goal-exe/annotations/routines.tsv','static/goal-exe/named/seg_1771_01.c','static/goal-exe/named/seg_1771_03.c',
      'static/goal-exe/named/seg_1771_06.c','static/goal-exe/named/seg_1771_07.c','static/goal-exe/tables/manifest.json','static/goal-exe/tables/ds.hex','static/goal-exe/tables/code_data.hex',
      'experiments/E040-route-fixture-writes/out/T124c/natural-groups-input-v1.jsonl','experiments/E040-route-fixture-writes/out/T124d/natural-inputs-v1.jsonl']:
        files[p]=sha((ROOT/p).read_bytes())
    x={'schema':'t124f-acceptance/1','base_commit':'0cf79c2a81e9f606d869a0ef26f53a9da8654765',
      'source_freeze_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
      'source_hashes':sources,'file_hashes':files,'private_inputs':private,'natural':natural,'plain':plain,'direct':direct,
      'limits':'PRIMARY actual70E6 natural contexts; synthetic direct caller frames separately labelled. All real ports in plain child; Unicorn/GOAL.EXE denied. Raw Image or explicit state/2+Tables as labelled. Exact observed below-entry-SP dead stack only beyond state/2 opcode exclusion; all DS/code-data deviations/LIVEwrites retained. Annual2/5 refused before body; T123 must guard before70E6. No whole sealed Route/year-rollover claim.'}
    with (out/'index.json').open('x') as f:f.write(json.dumps(x,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
