import ast,collections,re,sys,importlib.util,pathlib,json,hashlib,subprocess
sys.path.insert(0,'runtime');from original_match import port
s=importlib.util.spec_from_file_location('w',pathlib.Path('notes/427/writeset/check.py'));w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
raw={}
for routine in ('000E:3CC8','000E:4440','000E:4A87'):
 p,f,l=w.listing_of(routine)
 for line in p.read_text().splitlines()[f-1:l]:
  v=line.split()
  if not v or not re.fullmatch('[0-9A-F]{4}',v[0]):continue
  k=1
  while k<len(v) and re.fullmatch('[0-9A-F]{2}',v[k]):k+=1
  if k>=len(v) or v[k]!='call':continue
  instruction=' '.join(v[k:]);ret=(int(v[0],16)+k-1)&65535
  raw[ret]=(w.callee(routine,instruction),'far' in instruction)
source=pathlib.Path('runtime/original_match/port/news.py');tree=ast.parse(source.read_text());found={};counts=collections.Counter()
entries={a:e for reg,_ in port.load(['all']) for a,e in reg.entries.items()}
for n in ast.walk(tree):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_statistics_call':
  target,words,ret=[ast.literal_eval(x) for x in n.args[3:6]];far=ast.literal_eval(n.args[6] if len(n.args)>6 else next(k.value for k in n.keywords if k.arg=='far'))
  assert ret not in found,hex(ret)
  found[ret]=(target,far);counts[target]+=1;e=entries.get(target)
  if e:assert e.pop==2*words,(hex(ret),target,words,e.ret)
  else:
   rp,rf,rl=w.listing_of(target)
   returns=[]
   for line in rp.read_text().splitlines()[rf-1:rl]:
    m=re.search(r'\b(retf?)(?: (0x[0-9a-f]+|[0-9]+))?$',line.strip())
    if m:returns.append((m[1],int(m[2],0) if m[2] else 0))
   assert returns and all(v==2*words for _,v in returns),(target,words,returns)
assert found==raw,(set(raw)-set(found),set(found)-set(raw),[(hex(k),raw[k],found.get(k)) for k in raw if raw[k]!=found.get(k)])
print(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'static_call_sites':len(raw),'targets_near_far_and_return_addresses':'match original listing','argument_words':'match registered cleanup or unported original return instruction','counts':dict(counts)},indent=2))
