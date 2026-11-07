"""All eight owned entry frames and sixteen listing callsites, including helpers."""
import ast,hashlib,json,re,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
ranges=[('route','shareware_limit_reached','000E','09',0x7072,0x7098),('route','play_round_body','000E','09',0x70B9,0x715D),
 ('silent','result_needs_winner','0791','18',0xB15F,0xB19A),('display','silent_results_header','1771','08',0x5BF6,0x5C5F),
 ('display','silent_fixture_row','1771','11',0x7812,0x78B9),('display','summary_statistic_bar','0791','01',0x006C,0x00FE),
 ('entrypoints','expand_small_set','23E4','01',0x0831,0x0858),('entrypoints','union_sets','23E4','01',0x0900,0x0919)]
entries={a:e for reg,_ in port.load(['all']) for a,e in reg.entries.items()};rows=[];hashes={}
for owner,function,segment,part,start,end in ranges:
 path=ROOT/f'runtime/original_match/port/{owner}.py';hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
 tree=ast.parse(path.read_text());body=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==function);actual=[]
 for n in ast.walk(body):
  if not isinstance(n,ast.Call):continue
  name=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else None
  if name not in ('near','far','guest','_call'):continue
  kw={k.arg:k.value for k in n.keywords};target=ast.literal_eval(n.args[2]);target=f'{segment}:{target:04X}' if isinstance(target,int) else target
  if name=='_call':words=ast.literal_eval(n.args[3]);ret=ast.literal_eval(n.args[4]);far=ast.literal_eval(n.args[5])
  else:
   words=sum(2 if isinstance(a,ast.Starred) else 1 for a in n.args[3:]);ret=ast.literal_eval(kw['ret']);far=name!='near'
   if 'far' in kw:far=ast.literal_eval(kw['far'])
  ret=f'{segment}:{ret:04X}' if isinstance(ret,int) else ret if ':' in ret else segment+':'+ret
  actual.append((target,ret,words,far))
 listing=ROOT/f'static/goal-exe/code/seg_{segment}_{part}.asm';ins=[]
 hashes[str(listing.relative_to(ROOT))]=hashlib.sha256(listing.read_bytes()).hexdigest()
 for line in listing.read_text().splitlines():
  m=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s+)+([a-z].*)$',line)
  if m and start<=int(m[1],16)<=end:ins.append((int(m[1],16),m[2]))
 expected=[]
 for i,(pc,op) in enumerate(ins):
  if not op.startswith('call '):continue
  literal=op.split()[-1];target=literal.upper() if op.startswith('call far ') else f'{segment}:{int(literal,16)&65535:04X}'
  far=op.startswith('call far ') or (i>0 and ins[i-1][1]=='push cs');entry=entries[target]
  assert entry.far==far,(target,entry.ret,far)
  ret=f'{segment}:{ins[i+1][0]:04X}';item=(target,ret,entry.pop//2,far);expected.append(item)
  rows.append({'routine':f'{segment}:{start:04X}','call_pc':f'{segment}:{pc:04X}','target':target,'return_pc':ret,'argument_words':entry.pop//2,'far':far,'pushed_cs_near_encoding':not op.startswith('call far ') and far})
 assert sorted(actual)==sorted(expected),(function,actual,expected)
 last=ins[-1][1].split();entry=entries[f'{segment}:{start:04X}'];assert entry.far==(last[0]=='retf') and entry.pop==(int(last[1],0) if len(last)>1 else 0),(function,last,entry.ret)
assert len(rows)==16,len(rows)
print(json.dumps({'status':'passed','routines':8,'listing_calls':16,'method':'all listing calls matched to guest/near/far/manual _call placements, real callee cleanup and pushCS far frames','sources':hashes,'calls':rows},sort_keys=True,indent=2))
