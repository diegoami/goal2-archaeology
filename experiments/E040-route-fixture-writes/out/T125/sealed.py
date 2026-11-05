"""Independent original vs sealed facade, positive denial and complete state-copy checks.
Guest state crosses a private subprocess pipe only; outputs contain hashes/scalar decisions.
"""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT),str(Path(__file__).resolve().parent)]

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def fields(image):
    from original_match.machine import MEM_SIZE
    m=image.memory;ds=image.DS*16
    def word(a):return int.from_bytes(m[a:a+2],'little')
    def far(o):return word(ds+o)+16*word(ds+o+2)
    game=far(0xA923);manager=m[game+1];country=m[far(0xA91F)+3*(128+manager)]
    squad=far(0xA917)+191*country;base=word(ds+0x6D18+2*manager)
    poolseg=word(ds+0xA929);pooloff=word(ds+0xA927)
    return {'manager':manager,'country':country,'squad':[word(squad+2*i) for i in range(20)],
      'pool':[word(poolseg*16+((pooloff+2*((base+i)&65535))&65535)) for i in range(80)],
      'next_fixture':word(ds+0x9B43),'rng':{hex(o):word(ds+o) for o in (0x7B62,0x8336)},
      'records':{name:hashlib.sha256(m[far(ptr):far(ptr)+size]).hexdigest() for name,ptr,size in
        [('players',0xA91B,3061*20),('countries',0xA917,129*191),('pool',0xA927,160),('fixtures',0xA92B,36*8),('game',0xA923,0x68)]}}

def child():
    import builtins,io,os,importlib.abc
    class Deny(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname=='unicorn' or fullname.startswith('unicorn.'):raise ModuleNotFoundError('T125 positive Unicorn denial')
    sys.meta_path.insert(0,Deny())
    try:__import__('unicorn')
    except ModuleNotFoundError:denied=True
    else:raise AssertionError('Unicorn denial inactive')
    def guarded(fn):
        def check(path,*args,**kwargs):
            if isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).name.upper()=='GOAL.EXE':
                raise PermissionError('T125 positive GOAL.EXE denial')
            return fn(path,*args,**kwargs)
        return check
    builtins.open=guarded(builtins.open);io.open=guarded(io.open);os.open=guarded(os.open)
    try:Path('GOAL.EXE').read_bytes()
    except PermissionError:exe_denied=True
    else:raise AssertionError('EXE denial inactive')
    from original_match import assistant
    from original_match.image import Image
    from original_match.port.tables import load
    tables=load(ROOT/'static/goal-exe/tables');state=json.load(sys.stdin);before=digest(state)
    result=assistant.recommend(state,tables)
    assert digest(state)==before
    result_state=result.pop('state');after=Image.from_state(result_state,tables)
    print(json.dumps({'fields':fields(after),'result':result,'input_state_sha256':before,
      'output_state_sha256':digest(result_state),'copy_isolated':True,'unicorn_denied':denied,'exe_denied':exe_denied},sort_keys=True))

def parent(out):
    import subprocess
    import prove
    from original_match.image import Image
    from original_match.port.tables import load
    tables=load(ROOT/'static/goal-exe/tables');source,sha=prove.image()
    for manager in (0,1):
      for case in ('improve','ties','nomatch','weaker','unavailable','wrap','finals','tour','sacked','none','next'):
        m=prove.prepare(source,manager,case)
        view=Image.__new__(Image);view.memory=bytearray(m.read(0,len(source.memory))) if len(source.memory)<=0x110000 else bytearray(source.memory)
        view.memory[:0x110000]=m.read(0,0x110000);view.header=source.header;view.load=source.load;view.DS=source.DS;view.tables=tables
        state=view.state(tables)
        def read_key(replay):m.wr(0xA976,0x0D0D);m.return_from(True)
        def keypressed(replay):m.set_reg('ax',(m.reg('ax')&0xFF00)|1);m.return_from(True)
        m.at('214B:08DD',read_key);m.at('214B:0723',keypressed)
        decisions=[]
        m.at('214B:1765',lambda replay:decisions.append([m.where(m.stack_word(2),m.stack_word(0)),m.stack_word(8)&255]))
        before=fields(view);prove.call(m,'0791:DC7E')
        view.memory[:0x110000]=m.read(0,0x110000);expected=fields(view)
        p=subprocess.run([sys.executable,'-B',str(Path(__file__)),'--child'],input=json.dumps(state),text=True,capture_output=True)
        if p.returncode:raise RuntimeError(p.stderr)
        sealed=json.loads(p.stdout)
        difference={k:[expected[k],sealed['fields'][k]] for k in expected if expected[k]!=sealed['fields'][k]}
        refusal=next(({'0791:DC3D':'finals','0791:DC68':'tour'}[s] for s,f in decisions if f),None)
        assert sealed['result']['refusal']==refusal
        assert sealed['result']['allowed']==(refusal is None)
        assert not difference,difference
        if refusal:
            for k in ('squad','pool'):assert sealed['fields'][k]==before[k]
        rec={'manager':manager,'case':case,'asset_sha256':sha,'status':'passed','original_messages':decisions,
          'original_fields':expected,'sealed':sealed,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),ROOT/'runtime/original_match/assistant.py',ROOT/'runtime/original_match/port/assistant.py']}}
        with out.open('a') as f:f.write(json.dumps(rec,sort_keys=True)+'\n')
        print(manager,case,'passed',flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--child',action='store_true');ap.add_argument('--out',type=Path);a=ap.parse_args()
    if a.child:child()
    else:
        if a.out.exists():raise SystemExit('immutable output exists')
        parent(a.out)
