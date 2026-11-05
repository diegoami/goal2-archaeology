"""Development transcription of11D9's acyclic listing into structured Python.
Generated code has no decoder, dispatch loop or runtime listing dependency.
"""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
listing='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
listing=listing[listing.index('; ---- routine 000E:11D9'):listing.index('; ---- routine 000E:1F4D')]
rows=[]
for line in listing.splitlines():
 m=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s+)+([a-z].*)',line)
 if m:rows.append((int(m[1],16),m[2]))
rows=rows[3:-3]
assert rows[0][0]==0x11E0
# Ret epilogue is the sole sink; all branches are forward.
sink=0x1F47
assert all(int(x.split()[1],16)>a for a,x in rows if x.startswith('j'))
addresses=[a for a,x in rows];byaddr=dict(rows)
boundaries={addresses[0],sink}
for i,(addr,ins) in enumerate(rows):
 if ins.startswith('j'):
  boundaries.add(int(ins.split()[1],16))
  if i+1<len(rows):boundaries.add(rows[i+1][0])
starts=sorted(boundaries);blocks={}
for a in starts:
 blocks[a]=[(n,x) for n,x in rows if a<=n<next((b for b in starts if b>a),0x10000)]
succ={sink:[]}
for i,a in enumerate(starts[:-1]):
 code=blocks[a];last=code[-1][1]
 if last.startswith('jmp '):succ[a]=[int(last.split()[1],16)]
 elif last.startswith('j'):succ[a]=[int(last.split()[1],16),starts[i+1]]
 else:succ[a]=[starts[i+1]]
post={sink:{sink}}
for a in reversed(starts[:-1]):post[a]={a}|set.intersection(*(post[s] for s in succ[a]))

def expr(x):
 x=x.strip()
 if x in ('ax','bx','cx','dx','si','di','sp','bp','al','ah','es'):return 'r.'+x
 if x=='ss':return 'r.ss'
 if x=='cs':return 'mem.seg(0xE)'
 if x=='ds':return 'mem.DS'
 if re.fullmatch(r'(?:0x[0-9a-f]+|[0-9]+)',x):return x
 m=re.match(r'(byte|word) ptr (?:(ss|es):)?\[(.+)\]',x)
 if m:
  width,seg,offset=m.groups();width=8 if width=='byte' else 16
  offset=re.sub(r'\b(bp|di|ax)\b',lambda m:'r.'+m[1],offset)
  if seg=='ss' or ('r.bp' in offset and not seg):return f'ss{width}(mem, r, {offset})'
  if seg=='es':return f'mem.u{width}(mem.addr(r.es, {offset}))'
  return f'mem.ds{width}(({offset}) & M16)'
 raise ValueError(x)

def instruction(a,ins):
 op,_,operand=ins.partition(' ');v=[x.strip() for x in operand.split(',')]
 if op=='mov':
  if v[0].startswith('word ptr [bp'):
   off=v[0][len('word ptr [bp'):].rstrip(']').strip();off=off.replace(' ','') or '0'
   return f'r.local16({off}, {expr(v[1])})'
  return f'{expr(v[0])} = {expr(v[1])}'
 if op=='lea':return 'r.di = '+re.sub(r'\b(bp|di)\b',lambda m:'r.'+m[1],v[1].strip('[]'))
 if op=='les':
  memexp=v[1].replace('ptr ','word ptr ');offexpr=expr(memexp);segexpr=expr(memexp.replace(']', ' + 2]'))
  return f'r.es, r.di = {segexpr}, {offexpr}'
 if op=='push':return f'r.push({expr(operand)})'
 if op=='cmp':return f'_left, _right = {expr(v[0])}, {expr(v[1])}'
 if op=='or':assert v[0]==v[1];return f'_left, _right = {expr(v[0])}, 0'
 if op=='xor':assert v[0]==v[1];return f'{expr(v[0])} = 0'
 if op=='mul':return 'mul(r, '+expr(operand)+')'
 if op=='cwde':return 'cbw(r)'
 if op=='add':return f'{expr(v[0])} += {expr(v[1])}'
 if op=='call':
  far=operand.startswith('far ');target=operand.removeprefix('far ') if far else '000E:'+f'{int(operand,16):04X}'
  counts={'000E:062F':6,'000E:09DB':1,'000E:0A53':1,'000E:0ACB':1,'000E:0B0A':1,'000E:0B4D':1,'000E:0B77':1,'000E:0C3A':1,
          '0791:B71C':3,'1771:5C60':2,'214B:06B1':1,'214B:06FA':0,'214B:09DA':2,'23E4:062A':2,'23E4:06B7':2}
  following=addresses[addresses.index(a)+1] if a!=addresses[-1] else sink
  return f"r = yield from _result_call(mem, r, '{target}', {counts[target]}, 0x{following:04X}, far={far})"
 if op=='jmp' or op.startswith('j'):return None
 raise ValueError((a,ins))

def cond(op):
 return {'je':'_left == _right','jne':'_left != _right','jae':'_left >= _right','jb':'_left < _right','jbe':'_left <= _right',
 'jl':'s16(_left) < s16(_right)','jg':'s16(_left) > s16(_right)','jge':'s16(_left) >= s16(_right)','jle':'s16(_left) <= s16(_right)'}[op]
code=[];seen=[]
# Factor shared suffixes into named generator regions, not a runtime dispatch.
# Each region runs to the routine's sink and returns the final Regs to its caller.
from collections import Counter
incoming=Counter(x for values in succ.values() for x in values)
regions={a for a,n in incoming.items() if n>1 and a!=sink}
region_code=[]
def emit(start,stop,depth,owner):
 a=start
 while a!=stop:
  assert a!=sink,(a,stop)
  if a in regions and a!=owner:
   code.append('    '*depth+f'return (yield from _result_at_{a:04x}(mem, r))')
   return
  seen.append(a)
  for address,ins in blocks[a]:
   py=instruction(address,ins)
   if py:code.append('    '*depth+py+f'  # {address:04X}')
  destinations=succ[a]
  if len(destinations)==1:a=destinations[0];continue
  join=min(post[a]-{a})
  op=blocks[a][-1][1].split()[0]
  code.append('    '*depth+'if '+cond(op)+':  # '+f'{blocks[a][-1][0]:04X}')
  before=len(code);emit(destinations[0],join,depth+1,owner)
  if len(code)==before:code.append('    '*(depth+1)+'pass')
  code.append('    '*depth+'else:')
  before=len(code);emit(destinations[1],join,depth+1,owner)
  if len(code)==before:code.append('    '*(depth+1)+'pass')
  a=join
for owner in sorted(regions|{addresses[0]}):
 code=[]
 emit(owner,sink,1,owner)
 code.append('    return r')
 if not any('yield from' in line for line in code):code.insert(0,'    yield from ()')
 region_code.append(f"\n\ndef _result_at_{owner:04x}(mem, r):\n"+'\n'.join(code)+'\n')
assert set(seen)==set(starts)-{sink},set(starts)-set(seen)
source="""\n\ndef _result_call(mem, r, target, words, ret, far):
    \"\"\"11D9's arguments have already been pushed in listing order.

    Consume only the callee's declared words. Hidden string-result pointers stay
    below SP, exactly as their Pascal producers' ret/retf leaves them.
    \"\"\"
    values = [pop(mem, r) for _ in range(words)]
    r.store(stack=True)
    from .guest import call
    yield call(target, *reversed(values), ret_to=f'000E:{ret:04X}', far=far)
    return Regs(mem, resumed=True)


@PORTS.port('000E:11D9', ret='ret 2')
def result_column(mem, variant):
    \"\"\"T122b [confirmed: F039; code/seg_000E_02.asm11D9-1F4C].

    Structured transcription of the listing's acyclic branches, with shared
    suffixes factored into private generator regions named by listing offset.
    There is no instruction decoder or runtime dispatch/listing dependency.
    Each statement's comment is its original offset. Signed branches, temporary
    Pascal strings, caller frames and the real call return addresses stay exact.
    \"\"\"
    r = Regs(mem)
    r.enter(0x308)
    r = yield from _result_at_11e0(mem, r)
    return _end(r)
"""+''.join(region_code)
source=source.replace('(mem, r):','(mem, r, variant):').replace('(mem, r))','(mem, r, variant))').replace('(mem, r)\n','(mem, r, variant)\n')
source=source.replace('def _result_call(mem, r, target, words, ret, far):','def _result_call(mem, r, variant, target, words, ret, far):').replace('_result_call(mem, r, ', '_result_call(mem, r, variant, ')
source=source.replace('def _result_call(mem, r, variant, variant,','def _result_call(mem, r, variant,')
source=source.replace('    r.store(stack=True)\n    from .guest import call','    if variant == "result-draw-dropped" and target == "214B:06B1":\n        r.ax = 1\n        return r\n    r.store(stack=True)\n    from .guest import call')
source=source.replace('if _left == _right:  # 1213','if (_left == _right) != (variant == "result-text-inverted"):  # 1213')
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--check',action='store_true');a=ap.parse_args()
if a.check:
 production=(ROOT/'runtime/original_match/port/news.py').read_text()
 assert production[production.index('\n\ndef _result_call'):]==source
 print('fixed result-column transcription matches generator')
elif a.out:a.out.write_text(source)
else:print(source)
