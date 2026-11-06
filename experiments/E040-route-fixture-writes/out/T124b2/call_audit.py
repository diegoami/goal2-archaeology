"""T124b2: adapt main's B1 read-only verifier to four new routines; all17 static call sites."""
import ast, hashlib, importlib.util, json, pathlib, re, sys
sys.path.insert(0,'runtime')
from original_match import port
spec=importlib.util.spec_from_file_location('writeset_check',pathlib.Path('notes/427/writeset/check.py'))
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
ROUTINES={'1771:56E4':'continent_order_offset','1771:56FF':'build_draw_order',
          '1771:6730':'stage_qualifying','23E4:11D7':'reference_seed_from_registers'}
raw={}
for routine in ROUTINES:
 p,f,l=w.listing_of(routine); previous=''
 for line in p.read_text().splitlines()[f-1:l]:
  match=re.match(r'^([0-9A-F]{4})\s+((?:[0-9A-F]{2} )*[0-9A-F]{2})\s+(.*)$',line)
  if not match: continue
  off,data,insn=match.groups()
  if insn.startswith('call '):
   ret=f'{routine.split(":")[0]}:{(int(off,16)+len(data.split()))&65535:04X}'
   raw[ret]={'target':w.callee(routine,insn),'far':('far ' in insn or previous=='push cs'),'site':f'{routine.split(":")[0]}:{off}'}
  previous=insn
source=pathlib.Path('runtime/original_match/port/stages.py');tree=ast.parse(source.read_text())
names=set(ROUTINES.values()); actual={}
# The 63A4 name is determined by its port decorator, not its chosen Python spelling.
for fn in tree.body:
 if not isinstance(fn,ast.FunctionDef):continue
 selected=False
 for d in fn.decorator_list:
  if isinstance(d,ast.Call) and d.args and isinstance(d.args[0],ast.Constant) and d.args[0].value in ROUTINES:selected=True
 if not selected:continue
 rows=None
 for n in ast.walk(fn):
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows' for t in n.targets):rows=ast.literal_eval(n.value)
 for n in ast.walk(fn):
  if not(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='guest'):continue
  kws={k.arg:k.value for k in n.keywords};ret=kws['ret'];target=n.args[2]
  far=ast.literal_eval(kws['far']) if 'far' in kws else True
  pairs=[]
  if isinstance(target,ast.Constant) and isinstance(ret,ast.Constant):pairs=[(target.value,ret.value)]
  elif rows is not None:
   for row in rows:
    pairs.append((target.value if isinstance(target,ast.Constant) else row[1],row[5] if isinstance(ret,ast.Name) and ret.id=='bonus_ret' else row[2]))
  else:raise AssertionError(ast.unparse(n))
  # All starred arguments here are two-word far pointers.
  words=sum(2 if isinstance(a,ast.Starred) else 1 for a in n.args[3:])
  for t,r in pairs:
   assert r not in actual,r
   actual[r]={'target':t,'far':far,'argument_words':words}
assert set(actual)==set(raw),(set(raw)-set(actual),set(actual)-set(raw))
entries={a:e for reg,_ in port.load(['all']) for a,e in reg.entries.items()}
for ret,r in raw.items():
 a=actual[ret]
 assert (r['target'],r['far'])==(a['target'],a['far']),(ret,r,a)
 e=entries[r['target']]
 assert e.far==r['far'],(ret,'callee ABI',e.ret)
 assert e.pop==2*a['argument_words'],(ret,'argument cleanup',e.ret,a)
print(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
 'static_call_sites':len(raw),'targets_far_frames_returnPCs_argument_cleanup':'all match original listing and real registry',
 'sites':{ret:{**raw[ret],'argument_words':actual[ret]['argument_words']} for ret in sorted(raw)}},indent=2))
