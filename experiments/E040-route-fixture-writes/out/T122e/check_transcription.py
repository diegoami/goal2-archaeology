"""Independent row lexer/completeness check for fixed statistics Python."""
import argparse
from collections import Counter
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args()
 text='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
 rows={}
 for entry,end in ((0x3CC8,0x4045),(0x4440,0x47E6),(0x4A87,0x4DB7)):
  part=text[text.index(f'; ---- routine 000E:{entry:04X}'):text.index(f'; ---- routine 000E:{end:04X}')]
  for line in part.splitlines():
   v=line.split()
   if not v or not re.fullmatch('[0-9A-F]{4}',v[0]):continue
   k=1
   while k<len(v) and re.fullmatch('[0-9A-F]{2}',v[k]):k+=1
   if k>1 and k<len(v):rows[int(v[0],16)]=' '.join(v[k:])
 assert len(rows)==1162
 frame={0x3CC8,0x3CC9,0x3CCB,0x403F,0x4041,0x4042,0x4440,0x4441,0x4443,0x47B6,0x47B8,0x47B9,0x4A87,0x4A88,0x4A8A,0x4DB1,0x4DB3,0x4DB4}
 jumps={a for a,i in rows.items() if i.startswith('jmp ')}
 source=(ROOT/'runtime/original_match/port/news.py').read_text();source=source[source.index('\n\n# T122e [confirmed:'):]
 represented=Counter(int(x,16) for x in re.findall(r'# ([0-9A-F]{4})\b',source))
 missing=set(rows)-set(represented)-frame-jumps;extra=set(represented)-set(rows)
 assert not missing and not extra,(sorted(missing),sorted(extra))
 subprocess.run(['python3','-B',str(Path(__file__).with_name('generate_statistics.py')),'--check'],check=True,cwd=ROOT)
 record={'schema':'e040-t122e-transcription/1','task':'T122e','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'instruction_rows':len(rows),'rows_by_routine':{'3CC8':387,'4440':434,'4A87':341},'represented_unique_pcs':len(represented),
 'missing_semantic_pcs':[],'extra_pcs':[],'folded_frame_pcs':[f'{x:04X}' for x in sorted(frame)],
 'folded_unconditional_edges':[f'{x:04X}' for x in sorted(jumps)],
 'real_loop_back_edges':[],
 'duplicate_pc_annotations':{f'{p:04X}':n for p,n in represented.items() if n>1},
 'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('runtime/original_match/port/news.py','experiments/E040-route-fixture-writes/out/T122e/generate_statistics.py',str(Path(__file__).relative_to(ROOT)))}}
 if args.out:assert not args.out.exists();args.out.write_text(json.dumps(record,indent=1)+'\n')
 print(json.dumps({k:record[k] for k in ('instruction_rows','represented_unique_pcs','missing_semantic_pcs','extra_pcs')}))
if __name__=='__main__':main()
