"""Read-only call convention check; no original execution or runtime imports."""
import ast, hashlib, json, pathlib, re
root=pathlib.Path('/home/diego/projects/goal2-archaeology')
returns={}
for listing in (root/'static/goal-exe/code').glob('*.asm'):
 target=None
 for n,line in enumerate(listing.read_text().splitlines(),1):
  header=re.match(r'; ---- routine ([0-9A-F]{4}:[0-9A-F]{4})\b',line)
  if header:target=header[1];returns.setdefault(target,[])
  ret=re.search(r'\s(retf?)\s*(0x[0-9a-f]+|[0-9]+)?\s*$',line)
  if target and ret:returns[target].append({'return':[ret[1],int(ret[2],0) if ret[2] else 0],'listing':str(listing.relative_to(root)),'line':n})
work=root/'.claude/worktrees/task-T64-port-ball'
source=work/'runtime/original_match/port/ball.py'
tree=ast.parse(source.read_text());rows=[]
for fn in tree.body:
 if not isinstance(fn,ast.FunctionDef):continue
 targets={}
 for node in ast.walk(fn):
  if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Tuple) and isinstance(node.value,ast.IfExp):
   for index,t in enumerate(node.targets[0].elts):
    if isinstance(t,ast.Name):
     choices=[b.elts[index] for b in (node.value.body,node.value.orelse) if isinstance(b,ast.Tuple)]
     if choices and all(isinstance(c,ast.Constant) for c in choices):targets[t.id]=[c.value for c in choices]
 for node in ast.walk(fn):
  if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='call':continue
  target=node.args[0]
  resolved=[target.value] if isinstance(target,ast.Constant) else targets.get(target.id,[]) if isinstance(target,ast.Name) else []
  assert resolved,(fn.name,node.lineno,'unresolved target')
  assert not any(isinstance(a,ast.Starred) for a in node.args)
  kw={k.arg:ast.literal_eval(k.value) for k in node.keywords if k.arg in ('far','caller_pops')}
  expected=['retf' if kw['far'] else 'ret',0 if kw.get('caller_pops') else 2*(len(node.args)-1)]
  for address in resolved:
   actual=returns.get(address,[])
   rows.append({'function':fn.name,'line':node.lineno,'target':address,'expected_return':expected,'listing_returns':actual,'matches':bool(actual) and all(a['return']==expected for a in actual)})
result={'scope':'Static call argument-byte and near/far convention only; no dynamic resumption, register, held-word, call-site or match-equivalence proof. Source unchanged.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'calls':rows,'mismatches':[r for r in rows if not r['matches']]}
out=root/'.cache/t64-static-call-audit-resumed.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
print('T64',len(rows),'resolved alternatives;',len(result['mismatches']),'mismatches')
for r in result['mismatches']:print(json.dumps(r))
work=root/'.claude/worktrees/agent-aca0f4fd155445184';source=work/'runtime/original_match/port/frame.py';tree=ast.parse(source.read_text())
sites=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SITES' for t in n.targets));rows=[]
for site,(target,far,ret_to,nargs) in sites.items():
 expected=['retf' if far else 'ret',2*nargs];actual=returns.get(target,[])
 rows.append({'site':f'0791:{site:04X}','target':target,'ret_to':ret_to,'expected_return':expected,'listing_returns':actual,'matches':bool(actual) and all(a['return']==expected for a in actual)})
result={'scope':'Static SITES call argument-byte and near/far convention only; no dynamic resumption, register, held-word or match-equivalence proof. Source unchanged.','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'calls':rows,'mismatches':[r for r in rows if not r['matches']]}
out=root/'.cache/t69-static-call-audit-resumed.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n')
print('T69',len(rows),'SITES alternatives;',len(result['mismatches']),'mismatches')
for r in result['mismatches']:print(json.dumps(r))
