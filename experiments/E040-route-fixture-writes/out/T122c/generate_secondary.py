"""Development-only fixed transcription: real 2071 loops, acyclic 26F2.
The generated Python has no instruction decoder, dispatch loop or listing dependency.
"""
import argparse
from collections import Counter
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[4]
listing='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
ROWS={}
for entry,end in ((0x2071,0x26F2),(0x26F2,0x2E1F)):
 text=listing[listing.index(f'; ---- routine 000E:{entry:04X}'):listing.index(f'; ---- routine 000E:{end:04X}')]
 rows=[]
 for line in text.splitlines():
  m=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s+)+([a-z].*)',line)
  if m:rows.append((int(m[1],16),m[2]))
 ROWS[entry]=rows
NEXT={a:rows[i+1][0] for rows in ROWS.values() for i,(a,_) in enumerate(rows[:-1])}
ALL={a:ins for rows in ROWS.values() for a,ins in rows}

def expr(x):
 x=x.strip()
 if x in ('ax','bx','cx','dx','si','di','sp','bp','al','ah','es'):return 'r.'+x
 if x=='cl':return '(r.cx & 255)'
 if x=='dl':return '(r.dx & 255)'
 if x=='ss':return 'r.ss'
 if x=='cs':return 'mem.seg(0xE)'
 if x=='ds':return 'mem.DS'
 if re.fullmatch(r'-?(?:0x[0-9a-f]+|[0-9]+)',x):return x if not x.startswith('-') else hex(int(x,0)&65535)
 m=re.match(r'(byte|word) ptr (?:(ss|es):)?\[(.+)\]',x)
 if m:
  width,seg,off=m.groups();width=8 if width=='byte' else 16
  off=re.sub(r'\b(bp|di|ax)\b',lambda m:'r.'+m[1],off)
  if seg=='ss' or ('r.bp' in off and not seg):return f'ss{width}(mem, r, {off})'
  if seg=='es':return f'mem.u{width}(mem.addr(r.es, {off}))'
  return f'mem.ds{width}(({off}) & M16)'
 raise ValueError(x)

def assign(lhs,value,pc):
 if lhs=='cl':return f'r.cx = (r.cx & 0xff00) | (({value}) & 255)'
 if lhs=='dl':return f'r.dx = (r.dx & 0xff00) | (({value}) & 255)'
 m=re.match(r'(byte|word) ptr \[bp(.*)\]',lhs)
 if m:return f'r.local{8 if m[1]=="byte" else 16}({m[2].replace(" ","") or "0"}, {value})'
 if lhs=='byte ptr [0x22]':return f"mem.wds8(0x22, {value}, '000E:{pc:04X}')"
 return f'{expr(lhs)} = {value}'

def instruction(pc,ins):
 op,_,operand=ins.partition(' ');v=[x.strip() for x in operand.split(',')]
 if op=='mov':return assign(v[0],expr(v[1]),pc)
 if op=='lea':return 'r.di = '+re.sub(r'\b(bp|di)\b',lambda m:'r.'+m[1],v[1].strip('[]'))
 if op=='les':
  operand=v[1].replace('ptr ','word ptr ')
  return f'r.es, r.di = {expr(operand.replace("]"," + 2]"))}, {expr(operand)}'
 if op=='push':return f'r.push({expr(operand)})'
 if op=='cmp':return f'_left, _right = {expr(v[0])}, {expr(v[1])}'
 if op=='or':assert v[0]==v[1];return f'_left, _right = {expr(v[0])}, 0'
 if op=='xor':assert v[0]==v[1];return assign(v[0],'0',pc)
 if op=='mul':return 'mul(r, '+expr(operand)+')'
 if op=='cwde':return 'cbw(r)'
 if op in ('add','sub','shl'):
  operator={'add':'+','sub':'-','shl':'<<'}[op]
  return assign(v[0],f'{expr(v[0])} {operator} {expr(v[1])}',pc)
 if op in ('inc','dec'):
  return assign(operand,f'{expr(operand)} {"+" if op=="inc" else "-"} 1',pc)
 if op=='call':
  far=operand.startswith('far ');target=operand.removeprefix('far ') if far else f'000E:{int(operand,16):04X}'
  words={'000E:075F':6,'000E:2071':1,'000E:0ACB':1,'000E:0B4D':1,'000E:0B77':1,
         '1771:3216':1,'1771:377E':1,'1771:2E93':1,'1771:5C60':2,
         '214B:06B1':1,'214B:06FA':0,'214B:09DA':2,'23E4:062A':2,'23E4:06B7':2}[target]
  return f"r = yield from _secondary_call(mem, r, variant, '{target}', {words}, 0x{NEXT[pc]:04X}, far={far})"
 if op.startswith('j'):return None
 raise ValueError((pc,ins))

def cond(op):
 return {'je':'_left == _right','jne':'_left != _right','jae':'_left >= _right','jb':'_left < _right','jbe':'_left <= _right','ja':'_left > _right',
 'jl':'s16(_left) < s16(_right)','jg':'s16(_left) > s16(_right)','jge':'s16(_left) >= s16(_right)','jle':'s16(_left) <= s16(_right)'}[op]

pieces=[]
def straight(start,stop,depth):
 for pc in sorted(a for a in ALL if start<=a<stop):
  py=instruction(pc,ALL[pc])
  if py:pieces.append('    '*depth+py+f'  # {pc:04X}')

def acyclic(start,sink,prefix):
 rows=[(a,ALL[a]) for a in sorted(ALL) if start<=a<sink]
 assert all(int(ins.split()[1],16)>a for a,ins in rows if ins.startswith('j'))
 bounds={start,sink}
 for i,(a,ins) in enumerate(rows):
  if ins.startswith('j'):
   bounds.add(int(ins.split()[1],16));bounds.add(NEXT[a])
 starts=sorted(bounds);blocks={a:[(pc,ins) for pc,ins in rows if a<=pc<next((b for b in starts if b>a),65536)] for a in starts}
 succ={sink:[]}
 for i,a in enumerate(starts[:-1]):
  tail=blocks[a][-1][1]
  succ[a]=[int(tail.split()[1],16)] if tail.startswith('jmp ') else [int(tail.split()[1],16),starts[i+1]] if tail.startswith('j') else [starts[i+1]]
 post={sink:{sink}}
 for a in reversed(starts[:-1]):post[a]={a}|set.intersection(*(post[b] for b in succ[a]))
 incoming=Counter(b for destinations in succ.values() for b in destinations)
 regions={a for a,n in incoming.items() if n>1 and a!=sink}
 generated=[];seen=[]
 def emit(a,stop,depth,owner):
  while a!=stop:
   if a in regions and a!=owner:
    generated.append('    '*depth+f'return (yield from {prefix}_{a:04x}(mem, r, variant))');return
   seen.append(a)
   for pc,ins in blocks[a]:
    py=instruction(pc,ins)
    if py:generated.append('    '*depth+py+f'  # {pc:04X}')
   if len(succ[a])==1:a=succ[a][0];continue
   join=min(post[a]-{a});op=blocks[a][-1][1].split()[0]
   generated.append('    '*depth+f'if {cond(op)}:  # {blocks[a][-1][0]:04X}')
   before=len(generated);emit(succ[a][0],join,depth+1,owner)
   if before==len(generated):generated.append('    '*(depth+1)+'pass')
   generated.append('    '*depth+'else:')
   before=len(generated);emit(succ[a][1],join,depth+1,owner)
   if before==len(generated):generated.append('    '*(depth+1)+'pass')
   a=join
 output=[]
 for owner in sorted(regions|{start}):
  generated=[];emit(owner,sink,1,owner);generated.append('    return r')
  if not any('yield from' in l for l in generated):generated.insert(0,'    yield from ()')
  output.append(f'\n\ndef {prefix}_{owner:04x}(mem, r, variant):\n'+'\n'.join(generated)+'\n')
 assert set(seen)==set(starts)-{sink}
 return ''.join(output)

header='''

# T122c [confirmed: F039; code/seg_000E_03.asm 2071-2389/26F2-2E1E].
# The two real recommendation loops are explicit below. Only their acyclic
# bodies/tails and the secondary column's acyclic branches are factored.
def _secondary_call(mem, r, variant, target, words, ret, far):
    if variant == 'secondary-draw-dropped' and target == '214B:06B1' and 0x26F2 < ret < 0x2E1F:
        for _ in range(words):
            pop(mem, r)
        r.ax = 1
        return r
    r = yield from _result_call(mem, r, variant, target, words, ret, far)
    if variant == 'secondary-text-byte-flipped' and ret == 0x274D:
        off, seg = ss16(mem, r, r.sp), ss16(mem, r, r.sp + 2)
        p = mem.addr(seg, off)
        if mem.u8(p):
            mem.w8(p + 1, mem.u8(p + 1) ^ 1, '000E:274D')
    return r


@PORTS.port('000E:2071', ret='ret 2')
def recommend_pool_player(mem, variant):
    """Original 20-slot minimum and 80-slot pool maximum, with strict ties.

    Both candidate improvements make the original second strength call.
    Pool candidates have no additional availability check in this caller.
    """
    r = Regs(mem)
    r.enter(0x312)
'''
pieces=[header.rstrip('\n')]
straight(0x2078,0x20BC,1)
pieces.append('    if _left == _right:  # 20BC')
straight(0x20C1,0x20CB,2)
pieces.append('        while True:  # 20D0; back edge 2158 -> 20CD')
pieces.append('            r = yield from _secondary_squad_20d0(mem, r, variant)')
straight(0x2152,0x2156,3)
pieces.append('            if _left == _right:  # 2156\n                break')
straight(0x20CD,0x20D0,3)
straight(0x215B,0x215F,2)
pieces.append('        if _left < _right:  # 215F')
straight(0x2164,0x2195,3)
pieces.append('            if _left <= _right:  # 2195 (JA skips the pool loop)')
straight(0x2197,0x219A,4)
pieces.append('                while True:  # 219F; back edge 2210 -> 219C')
pieces.append('                    r = yield from _secondary_pool_219f(mem, r, variant)')
straight(0x220A,0x2210,5)
pieces.append('                    if _left == _right:  # 2210\n                        break')
straight(0x219C,0x219F,5)
straight(0x2212,0x2231,3)
pieces.append('            if _left < _right:  # 2231')
straight(0x2236,0x223F,4)
pieces.append('                r = yield from _secondary_recommend_223f(mem, r, variant)')
straight(0x2381,0x2384,1)
pieces.append('    return _end(r, value=True)')
source='\n'.join(pieces)+'\n'
source+=acyclic(0x20D0,0x2152,'_secondary_squad')
source+=acyclic(0x219F,0x220A,'_secondary_pool')
source+=acyclic(0x223F,0x2381,'_secondary_recommend')
source+='''

@PORTS.port('000E:26F2', ret='ret 2')
def secondary_result_column(mem, variant):
    """Original right-column branch tree; recommendation 2071 remains a real call."""
    r = Regs(mem)
    r.enter(0x308)
    r = yield from _secondary_column_26f9(mem, r, variant)
    return _end(r)
'''
source+=acyclic(0x26F9,0x2E19,'_secondary_column')
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--check',action='store_true');a=ap.parse_args()
if a.check:
 production=(ROOT/'runtime/original_match/port/news.py').read_text()
 assert production[production.index('\n\n# T122c [confirmed:'):]==source
 print('fixed secondary transcription matches generator')
elif a.out:a.out.write_text(source)
else:print(source)
