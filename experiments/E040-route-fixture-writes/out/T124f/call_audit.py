"""All ten original routines;28 supported calls and3 guarded annual-only calls."""
import ast,hashlib,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
source=ROOT/'runtime/original_match/port/ageing.py';tree=ast.parse(source.read_text());actual=set()
for n in ast.walk(tree):
 if not(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='guest'):continue
 target=ast.literal_eval(n.args[2]);kw={k.arg:k.value for k in n.keywords};ret=ast.literal_eval(kw['ret'])
 actual.add((target,ret,len(n.args)-3,ast.literal_eval(kw['far']) if 'far' in kw else True))
entries={a:e for reg,_ in port.load(['all']) for a,e in reg.entries.items()}
ranges=[('01',0,0x20),('05',0x3291,0x32E8),('05',0x32EB,0x33CA),('11',0x7E4A,0x7E7D),
 ('11',0x7E80,0x7F3D),('11',0x7F40,0x7FAE),('11',0x7FB1,0x7FDC),('11',0x7FDF,0x80B7),
 ('12',0x80DA,0x81E7),('13',0x96D3,0x97C9)]
calls=[];counts={};expected=set()
for part,start,end in ranges:
 ins=[]
 for line in (ROOT/f'static/goal-exe/code/seg_1771_{part}.asm').read_text().splitlines():
  m=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s+)+([a-z].*)$',line)
  if m and start<=int(m[1],16)<=end:ins.append((int(m[1],16),m[2]))
 counts[f'1771:{start:04X}']=len(ins)
 for i,(pc,op) in enumerate(ins):
  if not op.startswith('call '):continue
  literal=op.split()[-1]
  target=literal.upper() if op.startswith('call far ') else f'1771:{int(literal,16)&65535:04X}'
  far=op.startswith('call far ') or (i>0 and ins[i-1][1]=='push cs')
  e=entries[target];assert far==e.far,(pc,target,e.ret)
  ret=f'1771:{ins[i+1][0]:04X}';annual=start==0x80DA and pc>=0x8118
  row={'routine':f'1771:{start:04X}','call_pc':f'1771:{pc:04X}','printed_target':literal,
   'resolved_target':target,'return_pc':ret,'argument_words':e.pop//2,'far':far,'annual_only_guarded':annual}
  calls.append(row)
  if not annual:expected.add((target,ret,e.pop//2,far))
assert actual==expected,{'source_only':sorted(actual-expected),'listing_only':sorted(expected-actual)}
assert sum(counts.values())==563 and len(calls)==31 and len(expected)==28
print(json.dumps({'status':'passed','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'instruction_counts':counts,'original_instructions':sum(counts.values()),'original_calls':len(calls),
 'supported_calls':len(expected),'annual_only_guarded_calls':3,'calls':calls},indent=2,sort_keys=True))
