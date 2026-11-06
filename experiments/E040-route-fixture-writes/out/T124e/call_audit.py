"""All three new bodies' calls, including helper-generated PCs, against raw listing."""
import ast,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
source=ROOT/'runtime/original_match/port/stages.py';tree=ast.parse(source.read_text())
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
new=['stage_tour_line','failed_qualification_news','_stage_copy','_stage_heading','_stage_qualified','stage_news']

def values(n):
 if isinstance(n,ast.Constant) and type(n.value) is int:return {n.value}
 if isinstance(n,ast.IfExp):return values(n.body)|values(n.orelse)
 return set()

# Resolve the named local return-PC values from actual literal source tuples,
# and wrapper return parameters from their callsites. No textual guest count.
locals={}
for fn in new:
 node=functions[fn];env={}
 for n in ast.walk(node):
  if isinstance(n,ast.Tuple) and len(n.elts)==2 and values(n.elts[1]):env.setdefault('ret',set()).update(values(n.elts[1]))
  if isinstance(n,ast.For) and isinstance(n.target,ast.Tuple) and isinstance(n.iter,ast.Tuple):
   for row in n.iter.elts:
    if isinstance(row,ast.Tuple):
     for name,v in zip(n.target.elts,row.elts):
      if isinstance(name,ast.Name):env.setdefault(name.id,set()).update(values(v))
 locals[fn]=env
for wrapper,index in [('_stage_copy',3),('_stage_heading',4)]:
 vals=set()
 for fn in new:
  for n in ast.walk(functions[fn]):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id==wrapper:vals|=values(n.args[index])
 locals[wrapper]['ret']=vals
calls=set()
for fn in new:
 for n in ast.walk(functions[fn]):
  if not(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_news_call'):continue
  target=ast.literal_eval(n.args[2]);words=ast.literal_eval(n.args[3]);ret=n.args[4]
  returns=values(ret) if not isinstance(ret,ast.Name) else locals[fn].get(ret.id,set())
  assert returns,(fn,ast.unparse(n))
  far=ast.literal_eval(n.args[5]) if len(n.args)>5 else False
  for pc in returns:calls.add((pc,target,words,far))
entries={a:e for reg,_ in port.load(['all']) for a,e in reg.entries.items()}
listing=[];counts={}
for file,start,end in [('seg_000E_07.asm',0x5DAF,0x5E1C),('seg_000E_07.asm',0x5E6C,0x5FDB),('seg_000E_08.asm',0x60CB,0x6632)]:
 ins=[]
 for line in (ROOT/'static/goal-exe/code'/file).read_text().splitlines():
  match=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2} )+\s+(.*)$',line)
  if match and start<=int(match[1],16)<=end:ins.append((int(match[1],16),match[2]))
 counts[f'000E:{start:04X}']=len(ins)
 for index,(pc,op) in enumerate(ins):
  if not op.startswith('call '):continue
  if op.startswith('call far '):target=op.split()[-1].upper();far=True
  else:target=f'000E:{int(op.split()[-1],16):04X}';far=False
  e=entries[target];assert e.far==far and e.pop%2==0,(pc,target,e.ret)
  ret=ins[index+1][0];listing.append({'call_pc':f'000E:{pc:04X}','target':target,'return_pc':f'000E:{ret:04X}','argument_words':e.pop//2,'far':far})
expected={(int(v['return_pc'].split(':')[1],16),v['target'],v['argument_words'],v['far']) for v in listing}
assert calls==expected,{'source_only':sorted(calls-expected),'listing_only':sorted(expected-calls)}
import hashlib
print(json.dumps({'status':'passed','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'instruction_counts':counts,'total_instructions':sum(counts.values()),'call_count':len(listing),'calls':listing},indent=2,sort_keys=True))
