"""Development-only fixed headline/sack transcription; real loops stay explicit."""
import argparse,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
listing='\n'.join(p.read_text() for p in sorted((ROOT/'static/goal-exe/code').glob('seg_000E_*.asm')))
ROWS={}
for entry in (0x01FA,0x319B,0x4DB7,0x4E0E):
 part=listing[listing.index(f'; ---- routine 000E:{entry:04X}'):]
 end=part.find('; ---- routine ',1)
 if end!=-1:part=part[:end]
 rows=[]
 for line in part.splitlines():
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
  right="(0xfff4 if variant == 'sack-threshold-minus-one' else 0xfff5)" if pc==0x3782 else expr(v[1])
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
  words={'000E:319B':1,'000E:3CC8':1,'000E:4440':2,'000E:4A87':1,'000E:038E':0,'000E:11D9':1,'000E:4DB7':1,'000E:26F2':1,'000E:05F6':3,'000E:01FA':1,
         '000E:2E1F':7,'000E:1F4D':1,'000E:08F9':1,'000E:09DB':1,'000E:0A53':1,'000E:0ACB':1,'000E:0B0A':1,'000E:0B4D':1,'000E:0B77':1,
         '1771:5C60':2,'214B:06B1':1,'214B:09DA':2,'23E4:062A':2,'23E4:06B7':2,'0791:BC5D':1,'1771:3A82':2,'214B:0018':4,'23E4:08DF':3}[target]
  code=f"r = yield from _headline_call(mem, r, variant, '{target}', {words}, 0x{NEXT[pc]:04X}, far={far})"
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

header='''

# T122d [confirmed: F025/F039; code/seg_000E_01.asm01FA-038D,
# _04.asm319B-3A31 and _06.asm4DB7-4F98]. Fixed Python, no runtime decoder.
def _headline_call(mem, r, variant, target, words, ret, far):
    if variant == 'headline-draw-dropped' and target == '214B:06B1' and 0x319B < ret < 0x3A32:
        for _ in range(words):
            pop(mem, r)
        r.ax = 1
        return r
    return (yield from _result_call(mem, r, variant, target, words, ret, far))


def _headline_store(mem, r, variant, seg, off, width, value, at):
    r.flush()
    if variant == 'unmanage-manager-write-dropped' and at == '000E:02FD':
        return
    if width == 8:
        mem.w8(mem.addr(seg, off), value & 255, at)
    else:
        mem.w16(mem.addr(seg, off), value & M16, at)


@PORTS.port('000E:01FA', ret='ret 2')
def unmanage_country(mem, variant):
    """Original ordered flags/reset, post-reset roster reads, pool clear and future fixtures.

    The zero-prefix scan is intentionally unbounded, as the original is.
    """
    r = Regs(mem)
    r.enter(0x14)
'''
pieces=[header.rstrip('\n')]
straight(0x0200,0x0244,1);straight(0x0244,0x0249,1)
pieces.append('    while True:  # 024E; original back edge 0298 -> 024B')
straight(0x024E,0x0298,2)
pieces.append('        if _left == _right:  # 0298\n            break')
straight(0x024B,0x024E,2)
straight(0x029A,0x02B5,1)
pieces.append('    if _left <= _right:  # 02B5')
straight(0x02B7,0x02BA,2)
pieces.append('        while True:  # 02BF; original back edge 02E2 -> 02BC')
straight(0x02BF,0x02E2,3)
pieces.append('            if _left == _right:  # 02E2\n                break')
straight(0x02BC,0x02BF,3)
straight(0x02E4,0x0306,1)
pieces.append('    while True:  # 0306; zero-prefix scan has no invented bound')
straight(0x0306,0x0327,2)
pieces.append('        if _left != _right:  # 0327\n            break')
straight(0x0329,0x032C,2)
straight(0x032E,0x0334,1)
pieces.append('    if _left <= _right:  # 0334')
straight(0x0336,0x0339,2)
pieces.append('        while True:  # 033E; original back edge 0386 -> 033B')
pieces.append('            r = yield from _unmanage_fixtures_033e(mem, r, variant)')
straight(0x0382,0x0386,3)
pieces.append('            if _left == _right:  # 0386\n                break')
straight(0x033B,0x033E,3)
pieces.append('    return _end(r)')
source='\n'.join(pieces)+'\n'+acyclic(0x033E,0x0382,'_unmanage_fixtures')
source+='''

@PORTS.port('000E:319B', ret='ret 2')
def result_headline_and_sack(mem, variant):
    """Original nested-parent headline, signed[-255,-11] sack band and real outer flag."""
    r = Regs(mem)
    r.enter(0x308)
    r = yield from _headline_31a2(mem, r, variant)
    return _end(r)
'''
source+=acyclic(0x31A2,0x3A2C,'_headline')
source+='''

@PORTS.port('000E:4DB7', ret='ret 2')
def headline_statistics_pages(mem, variant):
    """Statistics routines stay actual original calls until T122e."""
    r = Regs(mem)
    r.enter()
    r = yield from _headline_pages_4dba(mem, r, variant)
    return _end(r)
'''
source+=acyclic(0x4DBA,0x4DE8,'_headline_pages')
source+='''

@PORTS.port('000E:4E0E', ret='ret 6')
def post_match_news_and_sack(mem, variant):
    """Original scorer histogram, strict first maximum, whole flag words and actual wait before unmanage."""
    r = Regs(mem)
    r.enter(0x22)
    r = yield from _news_outer_prelude_4e14(mem, r, variant)
'''
pieces=[]
straight(0x4E72,0x4E78,1)
pieces.append('    if _left <= _right:  # 4E78')
straight(0x4E7A,0x4E7D,2)
pieces.append('        while True:  # 4E82; original scorer-loop back edge 4EB0 -> 4E7F')
straight(0x4E82,0x4EB0,3)
pieces.append('            if _left == _right:  # 4EB0\n                break')
straight(0x4E7F,0x4E82,3)
straight(0x4EB2,0x4EB6,1)
pieces.append('    if _left > _right:  # 4EB6')
straight(0x4EB8,0x4EBD,2)
pieces.append('        while True:  # 4EC2; original max-loop back edge 4EDA -> 4EBF')
pieces.append('            r = yield from _news_histogram_max_4ec2(mem, r, variant)')
straight(0x4ED6,0x4EDA,3)
pieces.append('            if _left == _right:  # 4EDA\n                break')
straight(0x4EBF,0x4EC2,3)
pieces.append('    r = yield from _news_outer_tail_4edc(mem, r, variant)')
pieces.append('    return _end(r)')
source+='\n'.join(pieces)+'\n'
source+=acyclic(0x4E14,0x4E72,'_news_outer_prelude')
source+=acyclic(0x4EC2,0x4ED6,'_news_histogram_max')
source+=acyclic(0x4EDC,0x4F93,'_news_outer_tail')
ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path);ap.add_argument('--check',action='store_true');args=ap.parse_args()
if args.check:
 production=(ROOT/'runtime/original_match/port/news.py').read_text()
 assert production[production.index('\n\n# T122d [confirmed:'):]==source
 print('fixed headline/sack transcription matches generator')
elif args.out:args.out.write_text(source)
else:print(source)
