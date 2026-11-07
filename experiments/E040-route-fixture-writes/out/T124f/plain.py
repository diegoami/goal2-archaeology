"""Isolated80DA with ALL real ports; raw Image and no-opcode state/tables arms.

Private memory/state crosses a subprocess pipe only. Public receipts contain
hashes/scalars. The state/2 codec retains all DS/code-data deviations, including
RNG and80BA, while excluding opcode bytes. Only exact observed dead stack is
additionally normalized; all ordered LIVE writes remain compared.
"""
import argparse,base64,builtins,hashlib,importlib.abc,io,json,os,subprocess,sys,time,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
def sha(v):return hashlib.sha256(v).hexdigest()
def digest(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':')).encode())

def real_specs():
    from original_match import port
    for reg,var in port.load(['all']):
        sub=port.Registry(reg.name,reg.doc)
        for e in reg.entries.values():
            if not e.stub:sub._add(e)
        if sub.entries:yield sub,var


def collect(r):
    m=r.m;events=[];entry=m.reg('sp');ss=m.reg('ss')*16;minimum=[entry]
    def written(address,size,value):
        sp=m.reg('sp');minimum[0]=min(minimum[0],sp)
        if ss+sp-4<=address<ss+sp:minimum[0]=min(minimum[0],address-ss)
        events.extend((address+i,(value>>(8*i))&255) for i in range(size))
    m.on_write(0,0x110000-1,written)
    assert m.run(m.lin('1771:826D'),300,fresh=True) is None
    return events,minimum[0]


def child():
    class Deny(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname=='unicorn' or fullname.startswith('unicorn.'):raise ModuleNotFoundError('T124f positive Unicorn denial')
    sys.meta_path.insert(0,Deny())
    try:__import__('unicorn')
    except ModuleNotFoundError:unicorn_denied=True
    else:raise AssertionError('Unicorn denial inactive')
    def guarded(fn):
        def invoke(path,*args,**kwargs):
            if isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).name.upper()=='GOAL.EXE':
                raise PermissionError('T124f positive GOAL.EXE denial')
            return fn(path,*args,**kwargs)
        return invoke
    builtins.open=guarded(builtins.open);io.open=guarded(io.open);os.open=guarded(os.open)
    try:Path('GOAL.EXE').read_bytes()
    except PermissionError:exe_denied=True
    else:raise AssertionError('original file denial inactive')
    from unittest.mock import patch
    import proof as P
    from original_match import port,route as R
    from original_match.image import Image
    from original_match.machine import REGS
    from original_match.port.engine import PortMachine
    from original_match.port.mem import PortError
    from original_match.port import tables as T
    data=json.load(sys.stdin);tbl=T.from_record(data['tables']);table_before=digest(T.to_record(tbl))
    state_before=digest(data.get('state'))
    image=Image.from_state(data['state'],tbl) if data['mode']=='state' else Image(zlib.decompress(base64.b64decode(data['component'])))
    with patch.object(R,'Machine',PortMachine):r=R.Route(image,entry='play_round',record_writes=False)
    assert type(r.m) is PortMachine and not hasattr(r.m,'_uc')
    P.D.restore(r,data['context']);inst=port.install(r.m,list(real_specs()))
    events,minimum=collect(r);m=r.m;memory=m.read(0,0x110000)
    regs={n:m.reg(n) for n in REGS};record=P.D.public(r.record)
    assert not any(e[0]=='key' for e in r.record)
    assert table_before==digest(T.to_record(tbl)) and state_before==digest(data.get('state'))
    guard=PortMachine(image.memory,image.load);guard.set_reg('cs',guard.seg(0x1771));guard.set_reg('eip',0x826D)
    try:guard.run(guard.lin('1771:826E'),1,fresh=True)
    except PortError as exc:assert 'no registered port/return' in str(exc);refusal=str(exc)
    else:raise AssertionError('unregistered original instruction executed')
    print(json.dumps({'memory':base64.b64encode(zlib.compress(memory,9)).decode(),'minimum_sp':minimum,
      'writes':events,'registers':regs,'record':record,'waiting_key':r.keys.waiting,
      'calls':{k:v for k,v in inst.calls.items() if v},'backend_no_uc':True,'unicorn_denied':unicorn_denied,
      'exe_denied':exe_denied,'unregistered_original_guard':refusal,'table_unchanged':True,'input_state_unchanged':True}))


def parent(opts):
    import proof as P
    from original_match.image import Image
    from original_match.machine import REGS,MEM_SIZE
    from original_match.port import tables as T
    rows=list(map(json.loads,Path(opts.input).read_text().splitlines()));entry=next(r for r in rows if r.get('status')=='original-80DA-entry')
    cp=entry['checkpoint'];case=entry['case'];start=time.monotonic();r=P.load(cp);image=Image((ROOT/cp['path']).read_bytes())
    tbl=T.load(ROOT/'static/goal-exe/tables');payload={'mode':opts.mode,'context':cp['context'],'tables':T.to_record(tbl)}
    if opts.mode=='state':payload['state']=image.state(tbl)
    else:payload['component']=base64.b64encode(zlib.compress((ROOT/cp['path']).read_bytes(),9)).decode()
    events,minimum=collect(r);reference=r.m.read(0,MEM_SIZE)
    proc=subprocess.run([sys.executable,'-B',str(Path(__file__)),'--child'],input=json.dumps(payload),text=True,capture_output=True)
    if proc.returncode:raise RuntimeError(proc.stderr)
    actual=json.loads(proc.stdout);candidate=zlib.decompress(base64.b64decode(actual['memory']))
    ss=cp['context']['regs']['SS']*16;dead=(ss+min(minimum,actual['minimum_sp']),ss+(cp['context']['regs']['ESP']&65535))
    def normalized(memory):
        if opts.mode=='raw':
            buf=bytearray(memory);buf[dead[0]:dead[1]]=bytes(dead[1]-dead[0]);return sha(buf)
        view=Image.__new__(Image);view.header=image.header;view.memory=bytearray(image.memory)
        view.memory[:MEM_SIZE]=memory;view.load=image.load;view.DS=image.DS;view.tables=tbl
        state=view.state(tbl);buf=bytearray(zlib.decompress(base64.b64decode(state['memory'])))
        buf[dead[0]:dead[1]]=bytes(dead[1]-dead[0]);state['memory']=sha(buf)
        return digest(state)
    live=lambda writes:[tuple(v) for v in writes if not dead[0]<=v[0]<dead[1]]
    expected=normalized(reference);got=normalized(candidate);controls={}
    for name,address,caught_expected in [('below_dead',dead[0]-1,True),('inside_low',dead[0],False),
      ('inside_high',dead[1]-1,False),('return_word',dead[1],True),('caller_game_pointer',dead[1]+2,True),
      ('rng_7B62',r.m.DS*16+0x7B62,True),('rng_8336',r.m.DS*16+0x8336,True),
      ('constant_80BA',r.m.seg(0x1771)*16+0x80BA,True)]:
        bad=bytearray(candidate);bad[address]^=1;caught=normalized(bad)!=expected
        assert caught==caught_expected,name
        controls[name]={'linear':address,'caught':caught,'expected':caught_expected}
    controls['live_write_drop_caught']=live(events)!=live(actual['writes'])[1:];assert controls['live_write_drop_caught']
    regs={n:[r.m.reg(n),actual['registers'][n]] for n in REGS if r.m.reg(n)!=actual['registers'][n]}
    assert not(set(regs)-{'EBX','ECX','ESI','EDI','ES','EFLAGS'})
    assert expected==got and live(events)==live(actual['writes']) and P.D.public(r.record)==actual['record']
    assert r.keys.waiting==actual['waiting_key']
    assert all(actual[k] for k in ('backend_no_uc','unicorn_denied','exe_denied','table_unchanged','input_state_unchanged'))
    with Path(opts.out).open('x') as f:
        P.emit(f,{'schema':'t124f-fully-ported/1','case':case,'mode':opts.mode,'input':cp,
          'input_receipt_sha256':P.sha(Path(opts.input).read_bytes()),
          'source_hashes':{**P.sources(),str(Path(__file__).relative_to(ROOT)):P.sha(Path(__file__).read_bytes())},
          'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'scope':'isolated actual80DAentry; ALL real ports/noopcode/no originalfile; raw Image or state/2+Tables as labelled; no wholeRoute/annual claim'})
        P.emit(f,{'status':'completed','case':case,'mode':opts.mode,'normalized_complete_memory_or_state_equal':True,
          'normalization':'exact observed below-entry-SP dead stack only; state/2 explicitly omits opcodes and retains ALL DS/code-data deviations',
          'dead_stack_linear':list(dead),'normalization_controls':controls,'ordered_live_byte_writes_equal':True,
          'live_byte_writes':len(live(events)),'ordered_live_byte_writes_sha256':digest(live(events)),
          'records_equal':True,'ordered_record_sha256':digest(actual['record']),'waiting_key_equal':True,
          'register_differences':regs,'calls':actual['calls'],
          **{k:actual[k] for k in ('backend_no_uc','unicorn_denied','exe_denied','unregistered_original_guard','table_unchanged','input_state_unchanged')},
          'table_digests':tbl.sha256,'elapsed_s':round(time.monotonic()-start,4)})


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--child',action='store_true');ap.add_argument('--input');ap.add_argument('--mode',choices=['raw','state'],default='raw');ap.add_argument('--out');opts=ap.parse_args()
    if opts.child:child()
    else:parent(opts)
