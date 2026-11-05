"""Independent row lexer/completeness check for fixed 2071/26F2 Python."""
import argparse
from collections import Counter
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args()
 text='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
 rows={}
 for entry,end in ((0x2071,0x26F2),(0x26F2,0x2E1F)):
  part=text[text.index(f'; ---- routine 000E:{entry:04X}'):text.index(f'; ---- routine 000E:{end:04X}')]
  for line in part.splitlines():
   v=line.split()
   if not v or not re.fullmatch('[0-9A-F]{4}',v[0]):continue
   k=1
   while k<len(v) and re.fullmatch('[0-9A-F]{2}',v[k]):k+=1
   if k>1 and k<len(v):rows[int(v[0],16)]=' '.join(v[k:])
 assert len(rows)==1098
 frame={0x2071,0x2072,0x2074,0x2384,0x2386,0x2387,0x26F2,0x26F3,0x26F5,0x2E19,0x2E1B,0x2E1C}
 jumps={a for a,i in rows.items() if i.startswith('jmp ')}
 source=(ROOT/'runtime/original_match/port/news.py').read_text();source=source[source.index('\n\n# T122c [confirmed:'):]
 represented=Counter(int(x,16) for x in re.findall(r'# ([0-9A-F]{4})\b',source))
 missing=set(rows)-set(represented)-frame-jumps;extra=set(represented)-set(rows)
 assert not missing and not extra,(sorted(missing),sorted(extra))
 subprocess.run(['python3','-B',str(Path(__file__).with_name('generate_secondary.py')),'--check'],check=True,cwd=ROOT)
 record={'schema':'e040-t122c-transcription/1','task':'T122c','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'instruction_rows':len(rows),'rows_by_routine':{'2071':291,'26F2':807},'represented_unique_pcs':len(represented),
 'missing_semantic_pcs':[],'extra_pcs':[],'folded_frame_pcs':[f'{x:04X}' for x in sorted(frame)],
 'folded_unconditional_edges':[f'{x:04X}' for x in sorted(jumps)],
 'real_loop_back_edges':[{'from':'2158','to':'20CD','meaning':'squad scan until slot20'},{'from':'2210','to':'219C','meaning':'pool scan through inclusive base+79 unless unsigned addition wrapped'}],
 'duplicate_pc_annotations':{f'{p:04X}':n for p,n in represented.items() if n>1},
 'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('runtime/original_match/port/news.py','experiments/E040-route-fixture-writes/out/T122c/generate_secondary.py',str(Path(__file__).relative_to(ROOT)))}}
 if args.out:assert not args.out.exists();args.out.write_text(json.dumps(record,indent=1)+'\n')
 print(json.dumps({k:record[k] for k in ('instruction_rows','represented_unique_pcs','missing_semantic_pcs','extra_pcs')}))
if __name__=='__main__':main()
