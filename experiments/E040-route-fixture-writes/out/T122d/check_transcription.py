"""Independent row lexer/completeness check for fixed headline/sack Python."""
import argparse
from collections import Counter
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);args=ap.parse_args()
 text='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
 rows={}
 for entry,end in ((0x01FA,0x038E),(0x319B,0x3A5E),(0x4DB7,0x4E0E),(0x4E0E,0x50D4)):
  part=text[text.index(f'; ---- routine 000E:{entry:04X}'):text.index(f'; ---- routine 000E:{end:04X}')]
  for line in part.splitlines():
   v=line.split()
   if not v or not re.fullmatch('[0-9A-F]{4}',v[0]):continue
   k=1
   while k<len(v) and re.fullmatch('[0-9A-F]{2}',v[k]):k+=1
   if k>1 and k<len(v):rows[int(v[0],16)]=' '.join(v[k:])
 assert len(rows)==1256
 frame={0x01FA,0x01FB,0x01FD,0x0388,0x038A,0x038B,0x319B,0x319C,0x319E,0x3A2C,0x3A2E,0x3A2F,0x4DB7,0x4DB8,0x4DE8,0x4DEA,0x4DEB,0x4E0E,0x4E0F,0x4E11,0x4F93,0x4F95,0x4F96}
 jumps={a for a,i in rows.items() if i.startswith('jmp ')}
 source=(ROOT/'runtime/original_match/port/news.py').read_text();source=source[source.index('\n\n# T122d [confirmed:'):]
 represented=Counter(int(x,16) for x in re.findall(r'# ([0-9A-F]{4})\b',source))
 missing=set(rows)-set(represented)-frame-jumps;extra=set(represented)-set(rows)
 assert not missing and not extra,(sorted(missing),sorted(extra))
 subprocess.run(['python3','-B',str(Path(__file__).with_name('generate_headlines.py')),'--check'],check=True,cwd=ROOT)
 record={'schema':'e040-t122d-transcription/1','task':'T122d','code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'instruction_rows':len(rows),'rows_by_routine':{'01FA':141,'319B':932,'4DB7':28,'4E0E':155},'represented_unique_pcs':len(represented),
 'missing_semantic_pcs':[],'extra_pcs':[],'folded_frame_pcs':[f'{x:04X}' for x in sorted(frame)],
 'folded_unconditional_edges':[f'{x:04X}' for x in sorted(jumps)],
 'real_loop_back_edges':[{'from':'0298','to':'024B','meaning':'bench12..20 after actual reset'},{'from':'02E2','to':'02BC','meaning':'pool inclusive base..base+79, unsigned wrap skip'},{'from':'032C','to':'0306','meaning':'unbounded zero-prefix scan to actual nonzero sentinel'},{'from':'0386','to':'033B','meaning':'future fixture words through36'},{'from':'4EB0','to':'4E7F','meaning':'actual scorer entries'},{'from':'4EDA','to':'4EBF','meaning':'strict first histogram maximum over1..20'}],
 'duplicate_pc_annotations':{f'{p:04X}':n for p,n in represented.items() if n>1},
 'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('runtime/original_match/port/news.py','experiments/E040-route-fixture-writes/out/T122d/generate_headlines.py',str(Path(__file__).relative_to(ROOT)))}}
 if args.out:assert not args.out.exists();args.out.write_text(json.dumps(record,indent=1)+'\n')
 print(json.dumps({k:record[k] for k in ('instruction_rows','represented_unique_pcs','missing_semantic_pcs','extra_pcs')}))
if __name__=='__main__':main()
