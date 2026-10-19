"""Static target/return-site audit, without executing ports or the original."""
from pathlib import Path
import ast,hashlib,json,re
root=Path('/home/diego/projects/goal2-archaeology')
work=root/'.claude/worktrees/task-T64-port-ball'
source=work/'runtime/original_match/port/ball.py'
sites={};hashes={}
for listing in (work/'static/goal-exe/code').glob('seg_0791_*.asm'):
 hashes[str(listing.relative_to(work))]=hashlib.sha256(listing.read_bytes()).hexdigest()
 previous=None
 for number,line in enumerate(listing.read_text().splitlines(),1):
  m=re.match(r'^([0-9A-F]{4})  ((?:[0-9A-F]{2} ?)+)\s{2,}([a-z].*)$',line)
  if not m:continue
  offset=int(m[1],16);binary=bytes.fromhex(m[2]);insn=m[3]
  if insn.startswith('call '):
   far=insn.startswith('call far ')
   if far:target=insn.removeprefix('call far ').upper()
   else:
    target='0791:'+f'{int(insn.removeprefix("call "),16)&0xffff:04X}'
    far=previous is not None and previous[0]+len(previous[1])==offset and previous[2]=='push cs'
   ret='0791:'+f'{(offset+len(binary))&0xffff:04X}'
   assert ret not in sites
   sites[ret]={'site':'0791:'+f'{offset:04X}','target':target,'far':far,'path':str(listing.relative_to(work)),'line':number}
  previous=(offset,binary,insn)
def values(node,env):
 if isinstance(node,ast.Constant) and isinstance(node.value,str):return {node.value}
 if isinstance(node,ast.Name):return env.get(node.id,set())
 if isinstance(node,ast.IfExp):return values(node.body,env)|values(node.orelse,env)
 return set()
def assign(target,value,env):
 if isinstance(target,ast.Name):env.setdefault(target.id,set()).update(values(value,env))
 elif isinstance(target,ast.Tuple):
  if isinstance(value,ast.Tuple):
   for t,v in zip(target.elts,value.elts):assign(t,v,env)
  elif isinstance(value,ast.IfExp):assign(target,value.body,env);assign(target,value.orelse,env)
rows=[]
for fn in ast.parse(source.read_text()).body:
 if not isinstance(fn,ast.FunctionDef):continue
 env={}
 for n in ast.walk(fn):
  if isinstance(n,ast.Assign):
   for t in n.targets:assign(t,n.value,env)
 for n in ast.walk(fn):
  if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Name) or n.func.id!='call':continue
  kw={k.arg:k.value for k in n.keywords};targets=values(n.args[0],env);ret_to=values(kw['ret_to'],env)
  assert targets and ret_to,(fn.name,n.lineno)
  far=ast.literal_eval(kw['far'])
  for ret in sorted(ret_to):
   actual=sites.get(ret)
   rows.append({'function':fn.name,'line':n.lineno,'possible_targets':sorted(targets),'ret_to':ret,'far':far,'listing_call':actual,'matches':actual is not None and actual['target'] in targets and actual['far']==far})
result={'scope':'Read-only literal call target, following return address and push-cs/far convention; conservative union for branch alternatives. Does not prove branch-to-return correlation, arguments/registers/held words or runtime resumption.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'listing_sha256':hashes,'calls':rows,'mismatches':[x for x in rows if not x['matches']]}
out=work/'experiments/E036-match-port/out/T64/static-callsite-audit-20261019.json'
assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
print(len(rows),'resolved return-site alternatives;',len(result['mismatches']),'mismatches')
for x in result['mismatches']:print(x)
