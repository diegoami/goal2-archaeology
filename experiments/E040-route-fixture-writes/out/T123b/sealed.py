"""T123b positive-denial PortMachine leaf with real helpers, no stubs.
Supported native-record/synthetic-frame cases compare with unported original;
unsupported modes require complete pre-body memory equality. Guest states cross
only private subprocess pipes. The only normalized exclusion is dead SS9000:2000..2FFF.
"""
import argparse,base64,hashlib,json,sys,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT/'runtime'),str(HERE)]

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def sha(data):return hashlib.sha256(data).hexdigest()
def normalize(state):
    data=bytearray(zlib.decompress(base64.b64decode(state['memory'])))
    data[0x92000:0x93000]=bytes(0x1000)
    return digest({**state,'memory':sha(data)})
def table_hash(t):return digest({'ds':sha(t.ds),'code_data':[[off,sha(raw)] for off,raw in t.code_data],'sha256':t.sha256})

def image_of(source,m,tables):
    from original_match.image import Image
    from original_match.machine import MEM_SIZE
    image=Image.__new__(Image);image.memory=bytearray(source.memory);image.memory[:MEM_SIZE]=m.read(0,MEM_SIZE)
    image.header=source.header;image.load=source.load;image.DS=source.DS;image.tables=tables
    return image

def fields(m):
    return {'records':{name:sha(m.read(m.far(ptr),size)) for name,ptr,size in
      [('countries',0xA917,0x603F),('players',0xA91B,0xEF24),('managers',0xA91F,0x195),('pool',0xA927,0x3C2),
       ('fixtures',0xA92B,0x4B48),('lists',0xA92F,0x2448),('game',0xA923,0x10E)]},
      'rng':{hex(off):m.rd(off) for off in (0x7B62,0x8336,0x9B43)}}

def child():
    import builtins,io,os,importlib.abc
    class Deny(importlib.abc.MetaPathFinder):
      def find_spec(self,fullname,path=None,target=None):
        if fullname=='unicorn' or fullname.startswith('unicorn.'):raise ModuleNotFoundError('T123b positive Unicorn denial')
    sys.meta_path.insert(0,Deny())
    try:__import__('unicorn')
    except ModuleNotFoundError:pass
    else:raise AssertionError('Unicorn denial inactive')
    def guarded(fn):
      def check(path,*args,**kwargs):
        if isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).name.upper()=='GOAL.EXE':raise PermissionError('T123b positive EXE denial')
        return fn(path,*args,**kwargs)
      return check
    builtins.open=guarded(builtins.open);io.open=guarded(io.open);os.open=guarded(os.open)
    try:Path('GOAL.EXE').read_bytes()
    except PermissionError:pass
    else:raise AssertionError('EXE denial inactive')
    import prove
    from original_match import port
    from original_match.image import Image
    from original_match.machine import MEM_SIZE,REGS
    from original_match.port.engine import PortMachine
    from original_match.port.mem import PortError
    from original_match.port.tables import load
    tables=load(ROOT/'static/goal-exe/tables');payload=json.load(sys.stdin);state=payload['state'];input_hash=digest(state);table_before=table_hash(tables)
    image=Image.from_state(state,tables);m=PortMachine(image.memory,image.load)
    real=[]
    for reg,v in port.load(['all']):
      clean=port.Registry(reg.name,reg.doc)
      for entry in reg.entries.values():
        if entry.stub is None:clean._add(entry)
      real.append((clean,v))
    inst=port.install(m,real)
    m.far_call('0791:DEA6',(prove.PARENT,),'0791:E672',prove.SS,prove.SP)
    m.write(prove.SS*16+prove.SP,(0xE672).to_bytes(2,'little')+prove.PARENT.to_bytes(2,'little'));m.set_reg('bp',prove.PARENT)
    for name,value in [('ax',0xA55A),('bx',0x1234),('cx',0x5678),('dx',0xABCD),('si',0x1357),('di',0x2468),('eflags',0x202)]:m.set_reg(name,value)
    before=sha(m.read(0,MEM_SIZE));rejected=False
    m.at('0791:E672',lambda replay:m.stop('returned'))
    try:m.run(m.lin('0791:E673'),fresh=True)
    except PortError:
      if not payload['unsupported']:raise
      rejected=True
    assert rejected==payload['unsupported']
    if rejected:assert sha(m.read(0,MEM_SIZE))==before
    else:assert m.reg('sp')==prove.SP+4 and m.reg('bp')==prove.PARENT
    after=image_of(image,m,tables);output_state=after.state(tables)
    assert digest(state)==input_hash and table_hash(tables)==table_before
    print(json.dumps({'unsupported':rejected,'full_memory_unchanged':sha(m.read(0,MEM_SIZE))==before,
      'before_memory_sha256':before,'after_memory_sha256':sha(m.read(0,MEM_SIZE)),
      'input_state_sha256':input_hash,'output_state_sha256':digest(output_state),'normalized_state_sha256':normalize(output_state),
      'fields':fields(m),'parent':prove.parent(m),'registers':{r:m.reg(r) for r in REGS},
      'calls':{k:v for k,v in inst.calls.items() if v},'unicorn_denied':True,'exe_denied':True,'state_unchanged':True,'tables_unchanged':True},sort_keys=True))

def run(out):
    import subprocess,prove
    from original_match.port.tables import load
    from original_match.machine import REGS
    tables=load(ROOT/'static/goal-exe/tables');original,asset_sha=prove.source();prepared,_=prove.setup_source(original)
    source_hashes={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [Path(__file__),HERE/'prove.py',ROOT/'runtime/original_match/port/selection.py']}
    for setup,image in [(0,original),(1,prepared)]:
      for case in ('mark','empty','same','swap','empty-outgoing','pool-current','pool-marked','in-match'):
        actual_case='same' if case in ('pool-current','pool-marked','in-match') else case
        m,country,edits=prove.prepare(image,setup,actual_case);unsupported=case.startswith('pool-') or case=='in-match'
        def edit(a,v,n,why):
          old=m.read(a,n);m.write(a,int(v).to_bytes(n,'little'));edits.append({'linear':a,'size':n,'before_sha256':sha(old),'after_sha256':sha(m.read(a,n)),'why':why})
        if case=='pool-current':edit(prove.SS*16+prove.PARENT-5,2,2,'unsupported current pool')
        if case=='pool-marked':edit(prove.SS*16+prove.PARENT-7,2,2,'unsupported marked pool')
        if case=='in-match':edit(m.DS*16+0xC1F,1,1,'unsupported in-match substitution mode')
        state=image_of(image,m,tables).state(tables)
        child_run=subprocess.run([sys.executable,'-B',str(Path(__file__)),'--child'],input=json.dumps({'state':state,'unsupported':unsupported}),text=True,capture_output=True)
        if child_run.returncode:raise RuntimeError(child_run.stderr)
        result=json.loads(child_run.stdout)
        if not unsupported:
          prove.call(m);expected=image_of(image,m,tables).state(tables)
          assert fields(m)==result['fields'] and prove.parent(m)==result['parent']
          assert normalize(expected)==result['normalized_state_sha256'],'complete normalized state differs'
          for reg in ('ESP','EBP','SS','DS','CS','EIP'):assert m.reg(reg)==result['registers'][reg],reg
        else:assert result['full_memory_unchanged']
        record={'setup':setup,'case':case,'unsupported':unsupported,'status':'passed','asset':prove.ASSET,
          'asset_sha256':asset_sha,'input_type':'native records plus explicit synthetic parent/context edits',
          'edits':edits,'source_hashes':source_hashes,'sealed':result}
        with out.open('a') as f:f.write(json.dumps(record,sort_keys=True)+'\n')
        print(setup,case,'passed',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--child',action='store_true');p.add_argument('--out',type=Path);a=p.parse_args()
    if a.child:child()
    else:
      if a.out.exists():raise SystemExit('immutable output exists')
      run(a.out)
