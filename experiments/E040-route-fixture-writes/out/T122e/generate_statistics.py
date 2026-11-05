"""Development-only fixed statistics transcription; no runtime decoder/listing dependency."""
import argparse,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
listing='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
ROWS={}
for entry,end in ((0x3CC8,0x4045),(0x4440,0x47E6),(0x4A87,0x4DB7)):
 text=listing[listing.index(f'; ---- routine 000E:{entry:04X}'):listing.index(f'; ---- routine 000E:{end:04X}')]
 rows=[]
 for line in text.splitlines():
  m=re.match(r'^([0-9A-F]{4})\s+(?:[0-9A-F]{2}\s+)+([a-z].*)',line)
  if m:rows.append((int(m[1],16),m[2]))
 ROWS[entry]=rows
NEXT={pc:rows[i+1][0] for rows in ROWS.values() for i,(pc,_) in enumerate(rows[:-1])}
ALL={pc:ins for rows in ROWS.values() for pc,ins in rows}
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
 if m:
  off=re.sub(r'\b(di|ax|cx)\b',lambda m:'r.'+m[1],m[2].strip() or '0')
  return f'r.local{8 if m[1]=="byte" else 16}({off}, {value})'
 if lhs=='byte ptr [0x22]':return f"mem.wds8(0x22, {value}, '000E:{pc:04X}')"
 m=re.match(r'(byte|word) ptr (?:(ss|es):)?\[(.+)\]',lhs)
 if m:
  width,seg,off=m.groups();width=8 if width=='byte' else 16
  off=re.sub(r'\b(bp|di|ax|cx)\b',lambda m:'r.'+m[1],off)
  actual='r.ss' if seg=='ss' or ('r.bp' in off and seg is None) else 'r.es' if seg=='es' else 'mem.DS'
  return f"_headline_store(mem, r, variant, {actual}, {off}, {width}, {value}, '000E:{pc:04X}')"
 return f'{expr(lhs)} = {value}'

def instruction(pc,ins):
 op,_,operand=ins.partition(' ');v=[x.strip() for x in operand.split(',')]
 if op=='mov':return assign(v[0],expr(v[1]),pc)
 if op=='lea':return 'r.di = '+re.sub(r'\b(bp|di)\b',lambda m:'r.'+m[1],v[1].strip('[]'))
 if op=='les':
  operand=v[1].replace('ptr ','word ptr ')
  return f'r.es, r.di = {expr(operand.replace("]"," + 2]"))}, {expr(operand)}'
 if op=='push':return f'r.push({expr(operand)})'
 if op=='cmp':
  right=expr(v[1])
  return f'_left, _right = {expr(v[0])}, {right}'
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
  words={'000E:3A5E':3,'000E:4045':5,'000E:47E6':5,'000E:4865':1,'000E:09DB':1,'000E:0A53':1,'000E:0ACB':1,'000E:0B0A':1,'000E:0B4D':1,'000E:0B77':1,
         '1771:5C60':2,'214B:06B1':1,'214B:06FA':0,'23E4:062A':2,'23E4:06B7':2,'23E4:08DF':3}[target]
  code=f"r = yield from _statistics_call(mem, r, variant, '{target}', {words}, 0x{NEXT[pc]:04X}, far={far})"
  if target=='23E4:08DF':code+="\n_left, _right = int(not (mem.reg('eflags') & 0x40)), 0"
  return code
 if op.startswith('j'):return None
 raise ValueError((pc,ins))

def cond(op):
 return {'je':'_left == _right','jne':'_left != _right','jae':'_left >= _right','jb':'_left < _right','jbe':'_left <= _right','ja':'_left > _right',
 'jl':'s16(_left) < s16(_right)','jg':'s16(_left) > s16(_right)','jge':'s16(_left) >= s16(_right)','jle':'s16(_left) <= s16(_right)'}[op]

pieces=[]
def straight(start,stop,depth):
 for pc in sorted(a for a in ALL if start<=a<stop):
  py=instruction(pc,ALL[pc])
  if py:
   for line in py.splitlines():pieces.append('    '*depth+line+f'  # {pc:04X}')

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
    if py:
     for line in py.splitlines():generated.append('    '*depth+line+f'  # {pc:04X}')
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

source='''

# T122e [confirmed: F039; code/seg_000E_05.asm3CC8-4044/4440-47BB,
# code/seg_000E_06.asm4A87-4DB6]. Fixed statistics, original partial-register ABI.
def _statistics_call(mem, r, variant, target, words, ret, far):
    if variant == 'statistics-draw-dropped' and target == '214B:06B1':
        for _ in range(words):
            pop(mem, r)
        r.ax = 1
        return r
    return (yield from _result_call(mem, r, variant, target, words, ret, far))
'''
for entry,start,end,size,name,ret,value in ((0x3CC8,0x3CCF,0x403F,0x20A,'statistics_fan_quote','ret 2',True),(0x4440,0x4447,0x47B6,0x204,'statistics_manager_quote','ret 4',False),(0x4A87,0x4A8E,0x4DB1,0x20A,'statistics_board_quote','ret 2',True)):
 source+=f"\n\n@PORTS.port('000E:{entry:04X}', ret='{ret}')\ndef {name}(mem, variant):\n    r = Regs(mem)\n    r.enter(0x{size:X})\n    r = yield from _statistics_{start:04x}(mem, r, variant)\n    return _end(r"+(', value=True)' if value else ')')+'\n'
 source+=acyclic(start,end,'_statistics')
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--check',action='store_true');args=ap.parse_args()
if args.check:
 production=(ROOT/'runtime/original_match/port/news.py').read_text();assert production[production.index('\n\n# T122e [confirmed:'):]==source
 print('fixed statistics transcription matches generator')
elif args.out:args.out.write_text(source)
else:print(source)
