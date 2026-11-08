"""T128: original DEA6 frames, PyPy candidate, exact helper-oracle replay and sealed closure.
Native records plus declared synthetic caller/cursor/window fields; not a natural game journey.
Original memory/helper snapshots cross only the trusted private test-child pipe, never logs/Git.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match import port
from original_match.machine import MEM_SIZE,REGS
from original_match.port import selection
from original_match.port.engine import PortMachine
from port_test_runtime import call_in_pypy

SS=0x9000;SP=0x3000;PARENT=0x4000
ASSET=ROOT/'.cache/dl/c6b4796bbd02b1ab-e006-0000-r0007.sav'
HELPERS={'0791:DBFA':('0791:DECA',), '0791:DE27':('0791:DF5E','0791:DF75','0791:DEF9'),
 '0791:DE51':('0791:DF65','0791:DF00','0791:DF1A'), '214B:007B':('0791:DF29',),
 '0791:230C':('0791:DF33',), '1771:52CC':('0791:DF41',)}

def sha(data):return hashlib.sha256(data).hexdigest()
def regs(m):return {r:m.reg(r) for r in REGS}
def frame(m):return {'memory':m.read(0,MEM_SIZE),'regs':regs(m),'load':m.load}
def keys(m):
    def read(replay):m.wr(0xA976,0x0D0D);m.return_from(True)
    def poll(replay):m.set_reg('ax',(m.reg('ax')&0xFF00)|1);m.return_from(True)
    m.at('214B:08DD',read);m.at('214B:0723',poll)

def source():
    name='t128_existing_source'
    spec=importlib.util.spec_from_file_location(name,ROOT/'experiments/E040-route-fixture-writes/out/T123b/prove.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.source()

def prepare(case,setup):
    from original_match.machine import Machine
    image,asset_sha=source();m=Machine(image.memory,image.load);ds=m.DS*16;game=m.far(0xA923)
    manager=m.read(game+1,1)[0];country=m.read(m.far(0xA91F)+3*(128+manager),1)[0]
    def w(a,v,n=2):m.write(a,int(v).to_bytes(n,'little'))
    base=m.rd(0x6D18+2*manager);index=base+4+3-2
    w(game+2*manager+0x52,4);w(game+2*manager+0x5E,3)
    w(ds+0xC1B,3);w(ds+0xC1E,setup,1);w(ds+0xC1F,0,1)
    w(game+0x13+manager,int(case.startswith('refused') or case=='pool-to-squad'),1)
    # No pending friendly: isolate the allowed DBFA arm, not F031's ambiguous new-game tour edge.
    for i in range(36):w(m.far(0xA92F)+72*country+2*i,0)
    marked=case not in ('mark','empty','refused-mark','tour-refused')
    pane=1 if case in ('pool-to-squad','squad-only') else 2
    previous=1 if case in ('squad-to-pool','refused-swap','squad-only') else 2
    previous_index=3 if previous==1 else index if case=='same' else index+1
    for off,v,n in [(6,country,2),(0,0x4200,2),(2,0xE99C,2),(4,m.seg(0x791),2),
                    (-1,int(marked),1),(-3,int(country==m.rd(0x9B36)),1),(-5,pane,2),
                    (-7,previous,2),(-9,previous_index,2),(-11,0xBEEF,2)]:w(SS*16+PARENT+off,v,n)
    if case=='empty':w(m.far(0xA927)+2*index,0)
    if case=='tour-refused':
        other=next(c for c in range(1,129) if m.read(m.far(0xA917)+191*c+44,1)!=m.read(m.far(0xA917)+191*country+44,1))
        for i in range(36):
            w(m.far(0xA92F)+72*country+2*i,i+1)
            for off,v,n in [(0,0 if i==0 else 254,1),(2,1,1),(4,country,2),(6,other,2)]:w(m.far(0xA92B)+8*i+off,v,n)
    m.far_call('0791:DEA6',(PARENT,),'0791:E672',SS,SP)
    m.write(SS*16+SP,(0xE672).to_bytes(2,'little')+PARENT.to_bytes(2,'little'));m.set_reg('bp',PARENT)
    for r,v in [('ax',0xA55A),('bx',0x1234),('cx',0x5678),('dx',0xABCD),('si',0x1357),('di',0x2468),('eflags',0x202)]:m.set_reg(r,v)
    keys(m)
    return m,image,{'case':case,'setup':setup,'asset_sha256':asset_sha,'country':country,'manager':manager,'pool_index':index}

def original(case,setup):
    m,image,meta=prepare(case,setup);initial=frame(m);writes=[];helpers=[];active=[None];low=[SS*16+SP]
    def write(a,n,v):
        from original_match.port.prove import pushes
        writes.append((a,int(v).to_bytes(n,'little')))
        if m.reg('ss')==SS:
            position=SS*16+m.reg('sp')
            if pushes(m.read(m.pc(),6)) and position-16<=a<position:position=a
            low[0]=min(low[0],position)
    m.set_recorder(write);m.write_tap=lambda a,data:writes.append((a,data))
    for address,returns in HELPERS.items():
        def enter(replay,address=address,returns=returns):
            far=address in ('214B:007B','1771:52CC')
            ret=m.where(m.stack_word(2) if far else m.reg('cs'),m.stack_word(0))
            if active[0] is None and ret in returns:
                record={'target':address,'return':ret,'entry':frame(m),'write_start':len(writes)}
                helpers.append(record);active[0]=record
        m.at(address,enter)
        for ret in returns:
            def returned(replay,ret=ret):
                item=active[0]
                if item is not None and item['return']==ret:
                    item['writes']=writes[item.pop('write_start'):];item['after_regs']=regs(m);active[0]=None
            m.at(ret,returned)
    m.at('0791:E672',lambda replay:m.stop('t128-return'))
    m.run(m.lin('0791:E673'),fresh=True,timeout_s=60)
    assert active[0] is None
    meta['ordered_write_frame']=[low[0],SS*16+m.reg('sp')]
    return initial,frame(m),writes,helpers,meta,image

def deny_original():
    import builtins,importlib.abc,io
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    class Deny(importlib.abc.MetaPathFinder):
        def find_spec(self,fullname,path=None,target=None):
            if fullname=='unicorn' or fullname.startswith('unicorn.'):raise ModuleNotFoundError('T128 positive Unicorn denial')
    sys.meta_path.insert(0,Deny())
    try:__import__('unicorn')
    except ModuleNotFoundError:pass
    else:raise AssertionError('Unicorn denial absent')
    def guard(fn):
        def opened(path,*a,**kw):
            if isinstance(path,(str,bytes,os.PathLike)) and Path(os.fsdecode(path)).name.upper()=='GOAL.EXE':raise PermissionError('T128 positive GOAL.EXE denial')
            return fn(path,*a,**kw)
        return opened
    builtins.open=guard(builtins.open);io.open=guard(io.open);os.open=guard(os.open)
    try:Path('GOAL.EXE').read_bytes()
    except PermissionError:pass
    else:raise AssertionError('EXE denial absent')

def candidate(initial,helpers,variant=None):
    """Exact isolated primitive proof; real original helper effects replay privately after entry equality.
    Helper implementations are not proved here; sealed real-helper closure is a separate control.
    """
    deny_original();m=PortMachine(initial['memory'],initial['load'])
    for r,v in initial['regs'].items():m.set_reg(r,v)
    reg=port.Registry('selection','T128 DEA6 candidate');reg._add(selection.PORTS.entries['0791:DEA6']);reg.variants=dict(selection.PORTS.variants)
    port.install(m,[(reg,variant)]);writes=[];at=[0]
    m.set_recorder(lambda a,n,v:writes.append((a,int(v).to_bytes(n,'little'))))
    def replay_hook(address):
        def replay(again):
            assert at[0]<len(helpers),'extra helper call'
            record=helpers[at[0]];at[0]+=1
            assert record['target']==address,'helper order differs'
            assert m.read(0,MEM_SIZE)==record['entry']['memory'],'complete helper-entry memory differs'
            assert regs(m)==record['entry']['regs'],'ALL16 helper-entry ABI differs'
            for a,data in record['writes']:m.write_as(a,len(data),int.from_bytes(data,'little'),m.pc())
            for r,v in record['after_regs'].items():m.set_reg(r,v)
        return replay
    for target in HELPERS:m.at(target,replay_hook(target))
    m.at('0791:E672',lambda replay:m.stop('t128-return'))
    m.run(m.lin('0791:E673'),fresh=True,timeout_s=60)
    assert at[0]==len(helpers),'missing helper call'
    return {'memory':m.read(0,MEM_SIZE),'regs':regs(m),'writes':writes,'unicorn_denied':True,'exe_denied':True}



def live_writes(writes,interval):
    low,high=interval
    return [(a+i,data[i]) for a,data in writes for i in range(len(data)) if not low<=a+i<high]


def retain_traces(meta,initial,expected,writes,actual,helpers):
    # Original bytes and both complete traces remain private and retained; no payload is logged/published.
    import gzip,pickle,uuid
    directory=ROOT/'.cache/t128-private-traces';directory.mkdir(parents=True,exist_ok=True)
    path=directory/(meta['case']+'-'+str(meta['setup'])+'-'+uuid.uuid4().hex+'.pickle.gz')
    with gzip.open(path,'xb') as stream:
        pickle.dump(dict(meta=meta,initial=initial,expected=expected,original_writes=writes,
                         candidate=actual,original_helpers=helpers),stream,protocol=4)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}



def auxiliary(kind,**values):
    path=os.environ.get('T128_AUX_RECEIPTS')
    if path:
        row=dict(kind=kind,status='passed',**values)
        row['source_sha256']={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [Path(__file__),ROOT/'runtime/original_match/port/selection.py']}
        with Path(path).open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')


def receipt(meta,expected,writes,helpers,initial,actual):
    out=os.environ.get('T128_RECEIPTS')
    if out:
        trace=retain_traces(meta,initial,expected,writes,actual,helpers)
        row=dict(meta,status='passed',private_trace=trace,input_class='native records; declared synthetic parent/cursor/window fields',
                 memory_sha256=sha(expected['memory']),registers=expected['regs'],ordered_writes_sha256=sha(repr(writes).encode()),port_full_trace_sha256=sha(repr(actual['writes']).encode()),
                 ordered_live_byte_writes_sha256=sha(repr(live_writes(writes,meta['ordered_write_frame'])).encode()),
                 full_memory_and_helper_checkpoints_have_no_exclusions=True,
                 helpers=[h['target'] for h in helpers],complete_memory_all16_equal=True,ordered_live_byte_writes_equal=True,
                 primitive_candidate='verified PyPy3.11; positive Unicorn/GOAL.EXE denial; original helper transcript replay',
                 source_sha256={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [Path(__file__),ROOT/'runtime/original_match/port/selection.py']})
        with Path(out).open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')


@unittest.skipUnless(ASSET.is_file() and importlib.util.find_spec('unicorn'), 'original fixture/Unicorn required')
class PoolSwap(unittest.TestCase):
    def compare(self,case,setup=0):
        initial,expected,writes,helpers,meta,_=original(case,setup)
        actual=call_in_pypy(__name__,'candidate',(initial,helpers))
        self.assertTrue(actual['memory']==expected['memory'],'complete primitive memory differs')
        self.assertEqual(actual['regs'],expected['regs'])
        low,high=meta['ordered_write_frame']
        self.assertEqual(high,SS*16+SP+4)
        self.assertLessEqual(low,SS*16+SP)
        # Main-authored701-order-boundary.md: only transient dead-frame ORDER is outside comparison.
        protected=[(SS*16+PARENT-11,19)]
        machine=PortMachine(initial['memory'],initial['load'])
        protected += [(machine.far(0xA917),0x603F),(machine.far(0xA927),0x3C2)]
        self.assertTrue(all(a+n<=low or a>=high for a,n in protected),'frame overlaps caller/squad/pool')
        self.assertTrue(live_writes(actual['writes'],(low,high))==live_writes(writes,(low,high)),
                        'ordered live/caller byte writes differ')
        self.assertTrue(actual['unicorn_denied'] and actual['exe_denied'])
        self.assertEqual(actual['regs']['ESP'],SP+4);self.assertEqual(actual['regs']['EBP'],PARENT)
        self.assertEqual([h['target'] for h in helpers].count('0791:DBFA'),0 if case=='pool-to-squad' else 1)
        receipt(meta,expected,writes,helpers,initial,actual)
        return initial,expected,helpers

    def test_pool_first_marks_scroll_and_empty(self):
        for setup in (0,1):
            for case in ('mark','empty'):
                with self.subTest(setup=setup,case=case):self.compare(case,setup)

    def test_both_swap_directions_pool_pairs_and_same_entry(self):
        for setup in (0,1):
            for case in ('squad-to-pool','pool-to-squad','pool-to-pool','same'):
                with self.subTest(setup=setup,case=case):self.compare(case,setup)

    def test_final_and_tour_refusals_preserve_existing_mark(self):
        for case in ('refused-mark','refused-swap','tour-refused'):
            with self.subTest(case=case):self.compare(case)



    def test_falsifiers_gate_index_scroll_swap_and_mark(self):
        from port_test_runtime import PortRuntimeError
        for variant,case in [('pool-gate-omitted','refused-mark'),('pool-index-off-by-one','mark'),
                             ('pool-scroll-omitted','mark'),('squad-word-swap-omitted','squad-to-pool'),
                             ('squad-mark-clear-omitted','squad-to-pool')]:
            with self.subTest(variant=variant):
                initial,expected,writes,helpers,meta,_=original(case,0)
                try:actual=call_in_pypy(__name__,'candidate',(initial,helpers,variant))
                except PortRuntimeError as exc:
                    self.assertTrue(any(message in str(exc) for message in
                        ('helper order differs','complete helper-entry memory differs','ALL16 helper-entry ABI differs','missing helper call','extra helper call')))
                else:
                    self.assertTrue(actual['memory']!=expected['memory'] or actual['regs']!=expected['regs'],
                                    'falsifier escaped complete memory/ALL16 comparison')
                auxiliary('falsifier',variant=variant,case=case,detected=True)

    def test_code_free_sealed_primitive_exact_helper_replay(self):
        for case in ('mark','squad-to-pool','pool-to-squad','refused-mark'):
            with self.subTest(case=case):
                initial,expected,writes,helpers,meta,image=original(case,0)
                sealed_initial=dict(initial,memory=seal_memory(image,initial['memory']))
                sealed_helpers=[dict(h,entry=dict(h['entry'],memory=seal_memory(image,h['entry']['memory']))) for h in helpers]
                actual=call_in_pypy(__name__,'candidate',(sealed_initial,sealed_helpers))
                self.assertTrue(actual['memory']==seal_memory(image,expected['memory']),'complete sealed primitive memory differs')
                self.assertEqual(actual['regs'],expected['regs'])
                self.assertTrue(actual['unicorn_denied'] and actual['exe_denied'])
                auxiliary('sealed-primitive',case=case,complete_memory_all16_equal=True,unicorn_denied=True,exe_denied=True)



    def test_sealed_real_registered_helpers_preserve_caller_records_and_rng(self):
        for case in ('mark','squad-to-pool','pool-to-squad','refused-mark','tour-refused'):
            with self.subTest(case=case):
                initial,expected,writes,helpers,meta,image=original(case,0)
                sealed_initial=dict(initial,memory=seal_memory(image,initial['memory']))
                actual=call_in_pypy(__name__,'real_helpers',(sealed_initial,))
                reference=PortMachine(expected['memory'],initial['load'])
                self.assertEqual(actual['fields'],observable_fields(reference))
                for name in ('ESP','EBP','SS','DS','CS','EIP'):
                    self.assertEqual(actual['regs'][name],expected['regs'][name],name)
                self.assertEqual(actual['calls'].get('0791:DBFA',0),0 if case=='pool-to-squad' else 1)
                self.assertTrue(actual['unicorn_denied'] and actual['exe_denied'])
                auxiliary('sealed-real-helpers',case=case,fields=actual['fields'],calls={k:v for k,v in actual['calls'].items() if v},caller_abi_equal=True,unicorn_denied=True,exe_denied=True)



    def test_ddcb_original_leaf_full_abi_and_wrap(self):
        from original_match.port.prove import pushes
        for manager,base,scroll,cursor in [(1,1,0,1),(2,81,4,3),(6,401,65535,65535),
                                         (0,65535,1,2),(1,0,0,0),(2,0xFF00,0xFFF0,0x111)]:
            with self.subTest(manager=manager,base=base,scroll=scroll,cursor=cursor):
                m,image,meta=prepare('mark',0);game=m.far(0xA923)
                m.write(game+1,bytes([manager]));m.wr(0x6D18+2*manager,base)
                m.write(game+2*manager+0x52,scroll.to_bytes(2,'little'))
                m.write(game+2*manager+0x5E,cursor.to_bytes(2,'little'));m.set_reg('ip',0xDDCB)
                initial=frame(m);writes=[];low=[SS*16+SP]
                def written(a,n,v):
                    writes.append((a,int(v).to_bytes(n,'little')))
                    position=SS*16+m.reg('sp')
                    if pushes(m.read(m.pc(),6)) and position-16<=a<position:position=a
                    low[0]=min(low[0],position)
                m.set_recorder(written);m.at('0791:E672',lambda replay:m.stop('t128-ddcb-return'))
                m.run(m.lin('0791:E673'),fresh=True,timeout_s=30);expected=frame(m)
                actual=call_in_pypy(__name__,'ddcb_candidate',(initial,))
                self.assertTrue(actual['memory']==expected['memory'],'complete DDCB memory differs')
                self.assertEqual(actual['regs'],expected['regs'])
                interval=(low[0],SS*16+m.reg('sp'))
                self.assertTrue(live_writes(writes,interval)==live_writes(actual['writes'],interval))
                self.assertEqual(m.reg('ax'),(base+scroll+cursor-2)&65535)
                self.assertEqual((m.reg('sp'),m.reg('bp')),(SP+4,PARENT))
                self.assertTrue(all(a+n<=interval[0] or a>=interval[1] for a,n in
                    [(game+1,1),(game+2*manager+0x52,2),(game+2*manager+0x5E,2),(m.DS*16+0x6D18+2*manager,2)]))
                meta.update(case='ddcb-'+str(manager)+'-'+str(base)+'-'+str(scroll)+'-'+str(cursor),
                            ordered_write_frame=list(interval))
                private=retain_traces(meta,initial,expected,writes,actual,[])
                auxiliary('ddcb',manager=manager,base=base,scroll=scroll,cursor=cursor,ax=m.reg('ax'),
                          ordered_write_frame=list(interval),complete_memory_all16_equal=True,
                          ordered_live_byte_writes_equal=True,private_trace=private)


def ddcb_candidate(initial):
    deny_original();m=PortMachine(initial['memory'],initial['load'])
    for r,v in initial['regs'].items():m.set_reg(r,v)
    reg=port.Registry('selection','T128 DDCB leaf');reg._add(selection.PORTS.entries['0791:DDCB'])
    port.install(m,[(reg,None)]);writes=[]
    m.set_recorder(lambda a,n,v:writes.append((a,int(v).to_bytes(n,'little'))))
    m.at('0791:E672',lambda replay:m.stop('t128-ddcb-return'))
    m.run(m.lin('0791:E673'),fresh=True,timeout_s=30)
    return {'memory':m.read(0,MEM_SIZE),'regs':regs(m),'writes':writes}


def observable_fields(m):
    return {'records':{name:sha(m.read(m.far(ptr),size)) for name,ptr,size in
        [('countries',0xA917,0x603F),('players',0xA91B,0xEF24),('managers',0xA91F,0x195),
         ('pool',0xA927,0x3C2),('fixtures',0xA92B,0x4B48),('lists',0xA92F,0x2448),('game',0xA923,0x10E)]},
        'parent':sha(m.read(SS*16+PARENT-11,19)),
        'rng':{str(k):m.rd(k) for k in (0x7B62,0x8336,0x9B43)}}


def real_helpers(initial):
    """Sealed integration control uses REAL existing helper ports, not the primitive oracle.
    Fingerprints cover all gameplay/caller records; full primitive/dead-frame ABI is proved separately.
    """
    deny_original();m=PortMachine(initial['memory'],initial['load'])
    for r,v in initial['regs'].items():m.set_reg(r,v)
    real=[]
    for reg,variant in port.load(['all']):
        clean=port.Registry(reg.name,reg.doc)
        for entry in reg.entries.values():
            if entry.stub is None and entry.address not in ('214B:08DD','214B:0723'):clean._add(entry)
        if clean.entries:real.append((clean,variant))
    installed=port.install(m,real);keys(m)
    m.at('0791:E672',lambda replay:m.stop('t128-return'))
    m.run(m.lin('0791:E673'),fresh=True,timeout_s=60)
    return {'fields':observable_fields(m),'regs':regs(m),'calls':dict(installed.calls),
            'unicorn_denied':True,'exe_denied':True}


def seal_memory(image,memory):
    from original_match.image import Image
    from original_match.port.tables import load
    tables=load(ROOT/'static/goal-exe/tables')
    view=Image.__new__(Image);view.memory=bytearray(image.memory);view.memory[:MEM_SIZE]=memory
    view.header=image.header;view.load=image.load;view.DS=image.DS;view.tables=tables
    state=view.state(tables)
    return bytes(Image.from_state(state,tables).memory[:MEM_SIZE])

def baseline_candidate(source_text,initial,helpers):
    """T128 diagnostic only: run the accepted pre-task implementation in the same private PyPy proof."""
    namespace={'__package__':selection.__package__,'__name__':selection.__name__, '__file__':selection.__file__}
    exec(compile(source_text,selection.__file__,'exec'),namespace)
    entry=selection.PORTS.entries['0791:DEA6'];saved=entry.fn
    try:
        entry.fn=namespace['swap_pre_match_squad']
        return candidate(initial,helpers)
    finally:entry.fn=saved
