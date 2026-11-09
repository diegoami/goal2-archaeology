"""T129p: original E2E6 (the SELECT TEAM pool pane), the verified-PyPy candidate and sealed closure.
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
from original_match.machine import MEM_SIZE
from original_match.port import selection
from original_match.port.engine import PortMachine
from port_test_runtime import call_in_pypy
from tests import test_port_pool_swap as swap

SS,SP,PARENT=swap.SS,swap.SP,swap.PARENT
ENTRY='0791:E2E6';RETURN='0791:E4D8';M16=0xFFFF
ASSET=swap.ASSET
# E2E6's direct callees and the return address of each call site in the listing (code/seg_0791_22.asm).
HELPERS={'214B:0329':('0791:E31D','0791:E32C','0791:E33B','0791:E3F5','0791:E404'),
         '1771:2F37':('0791:E3AA',),'214B:00DB':('0791:E3D7',),'0791:DDCB':('0791:E411',),
         '0791:DE51':('0791:E418',),'1771:42BC':('0791:E424',),'214B:13C5':('0791:E449',)}
DEFAULT=dict(manager=None,base=None,top=4,cursor=3,mark=0xBEEF,c20=0,country=None,empty_selected=False,
             empty_row=None,pane=2)
# Declared synthetic pool-pane states: base DS:6D18[manager], top game+0x52, cursor game+0x5E, retained mark
# (caller -11), the manager and country words, DS:0C20 and empty pool words.
CASES={'first-page':dict(top=1,cursor=1,mark=1,base=1,manager=1),
       'mid-highlight':dict(top=5,cursor=9,mark=12),
       'last-row-highlight':dict(top=10,cursor=2,mark=30),
       'above-range-mark':dict(top=10,cursor=2,mark=31),
       'below-range-mark':dict(top=10,cursor=2,mark=9),
       'no-highlight':dict(),
       'manager-2-base-81':dict(manager=2,base=81,top=6,cursor=4,mark=10),
       'manager-6-base-401':dict(manager=6,base=401,top=2,cursor=17,mark=4),
       'manager-0-base-wrap':dict(manager=0,base=0xFFF0,top=9,cursor=5,mark=12),
       'empty-selected-word':dict(top=3,cursor=4,mark=3,empty_selected=True),
       'empty-row-word':dict(top=3,cursor=4,mark=7,empty_row=7),
       'top-wrap-skips-rows':dict(top=0xFFF0,cursor=3,mark=0xFFF2),
       'top-no-wrap-last':dict(top=0xFFEB,cursor=3,mark=0xFFFF),
       'zero-top':dict(top=0,cursor=1,mark=0),
       'footer-suppressed':dict(top=4,cursor=3,mark=5,c20=1),
       'wide-country':dict(top=4,cursor=3,mark=5,country=0x1234)}


def sha(data):return hashlib.sha256(data).hexdigest()


def pool_lin(m,offset_word):
    """Linear address of the pool word at A927 + offset_word (16-bit offset wrap)."""
    return m.far(0xA927)+((m.rd(0xA927)+offset_word)&M16)-m.rd(0xA927)


def prepare(case,setup):
    from original_match.machine import Machine
    p=dict(DEFAULT,**CASES[case])
    image,asset_sha=swap.source();m=Machine(image.memory,image.load);ds=m.DS*16;game=m.far(0xA923)
    if p['manager'] is not None:m.write(game+1,bytes([p['manager']]))
    manager=m.read(game+1,1)[0]
    country=p['country'] if p['country'] is not None else m.read(m.far(0xA91F)+3*(128+manager),1)[0]
    def w(a,v,n=2):m.write(a,int(v).to_bytes(n,'little'))
    if p['base'] is not None:m.wr(0x6D18+2*manager,p['base'])
    base=m.rd(0x6D18+2*manager)
    w(game+2*manager+0x52,p['top']);w(game+2*manager+0x5E,p['cursor'])
    w(ds+0xC1B,3);w(ds+0xC1E,setup,1);w(ds+0xC1F,0,1);w(ds+0xC20,p['c20'],1)
    selected=(base+p['top']+p['cursor']-2)&M16
    if p['empty_selected']:w(pool_lin(m,(selected<<1)&M16),0)
    if p['empty_row'] is not None:w(pool_lin(m,(((base+p['empty_row']-1)&M16)<<1)&M16),0)
    for off,v,n in [(6,country,2),(0,0x4200,2),(2,0xE99C,2),(4,m.seg(0x791),2),
                    (-1,int(p['mark']!=0xBEEF),1),(-3,int(country==m.rd(0x9B36)),1),(-5,p['pane'],2),
                    (-7,1,2),(-9,3,2),(-11,p['mark'],2)]:w(SS*16+PARENT+off,v,n)
    m.far_call(ENTRY,(PARENT,),RETURN,SS,SP)
    m.write(SS*16+SP,(0xE4D8).to_bytes(2,'little')+PARENT.to_bytes(2,'little'));m.set_reg('bp',PARENT)
    for r,v in [('ax',0xA55A),('bx',0x1234),('cx',0x5678),('dx',0xABCD),('si',0x1357),('di',0x2468),('eflags',0x202)]:m.set_reg(r,v)
    return m,image,{'case':case,'setup':setup,'asset_sha256':asset_sha,'country':country,'manager':manager,
                    'base':base,'selected_index':selected}


def original(case,setup):
    m,image,meta=prepare(case,setup);initial=swap.frame(m);writes=[];helpers=[];active=[None];low=[SS*16+SP]
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
            far=not address.startswith('0791:')
            ret=m.where(m.stack_word(2) if far else m.reg('cs'),m.stack_word(0))
            if active[0] is None and ret in returns:
                record={'target':address,'return':ret,'entry':swap.frame(m),'write_start':len(writes)}
                helpers.append(record);active[0]=record
        m.at(address,enter)
        for ret in returns:
            def returned(replay,ret=ret):
                item=active[0]
                if item is not None and item['return']==ret:
                    item['writes']=writes[item.pop('write_start'):];item['after_regs']=swap.regs(m);active[0]=None
            m.at(ret,returned)
    m.at(RETURN,lambda replay:m.stop('t129p-return'))
    m.run(m.lin('0791:E4D9'),fresh=True,timeout_s=60)
    assert active[0] is None
    meta['ordered_write_frame']=[low[0],SS*16+m.reg('sp')]
    return initial,swap.frame(m),writes,helpers,meta,image


def candidate(initial,helpers,variant=None):
    """Exact isolated primitive proof; original helper effects replay privately after complete entry equality.
    Helper implementations are not proved here; sealed real-helper closure is a separate control.
    """
    swap.deny_original();m=PortMachine(initial['memory'],initial['load'])
    for r,v in initial['regs'].items():m.set_reg(r,v)
    reg=port.Registry('selection','T129p E2E6 candidate');reg._add(selection.PORTS.entries[ENTRY]);reg.variants=dict(selection.PORTS.variants)
    port.install(m,[(reg,variant)]);writes=[];at=[0]
    m.set_recorder(lambda a,n,v:writes.append((a,int(v).to_bytes(n,'little'))))
    def replay_hook(address):
        def replay(again):
            assert at[0]<len(helpers),'extra helper call'
            record=helpers[at[0]];at[0]+=1
            assert record['target']==address,'helper order differs'
            assert m.read(0,MEM_SIZE)==record['entry']['memory'],'complete helper-entry memory differs'
            assert swap.regs(m)==record['entry']['regs'],'ALL16 helper-entry ABI differs'
            for a,data in record['writes']:m.write_as(a,len(data),int.from_bytes(data,'little'),m.pc())
            for r,v in record['after_regs'].items():m.set_reg(r,v)
        return replay
    for target in HELPERS:m.at(target,replay_hook(target))
    m.at(RETURN,lambda replay:m.stop('t129p-return'))
    m.run(m.lin('0791:E4D9'),fresh=True,timeout_s=60)
    assert at[0]==len(helpers),'missing helper call'
    return {'memory':m.read(0,MEM_SIZE),'regs':swap.regs(m),'writes':writes,'unicorn_denied':True,'exe_denied':True}


def retain_traces(meta,initial,expected,writes,actual,helpers):
    # Original bytes and both complete traces remain private and retained; no payload is logged/published.
    import gzip,pickle,uuid
    directory=ROOT/'.cache/t129p-private-traces';directory.mkdir(parents=True,exist_ok=True)
    path=directory/(meta['case']+'-'+str(meta['setup'])+'-'+uuid.uuid4().hex+'.pickle.gz')
    with gzip.open(path,'xb') as stream:
        pickle.dump(dict(meta=meta,initial=initial,expected=expected,original_writes=writes,
                         candidate=actual,original_helpers=helpers),stream,protocol=4)
    return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}


def sources():
    return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in [Path(__file__),ROOT/'runtime/original_match/port/selection.py']}


def auxiliary(kind,**values):
    path=os.environ.get('T129P_AUX_RECEIPTS')
    if path:
        row=dict(kind=kind,status='passed',**values);row['source_sha256']=sources()
        with Path(path).open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')


def receipt(meta,expected,writes,helpers,initial,actual):
    out=os.environ.get('T129P_RECEIPTS')
    if out:
        trace=retain_traces(meta,initial,expected,writes,actual,helpers)
        row=dict(meta,status='passed',private_trace=trace,input_class='native records; declared synthetic parent/pool-pane fields',
                 memory_sha256=sha(expected['memory']),registers=expected['regs'],ordered_writes_sha256=sha(repr(writes).encode()),
                 port_full_trace_sha256=sha(repr(actual['writes']).encode()),
                 ordered_live_byte_writes_sha256=sha(repr(swap.live_writes(writes,meta['ordered_write_frame'])).encode()),
                 full_memory_and_helper_checkpoints_have_no_exclusions=True,
                 helpers=[h['target'] for h in helpers],complete_memory_all16_equal=True,ordered_live_byte_writes_equal=True,
                 primitive_candidate='verified PyPy3.11; positive Unicorn/GOAL.EXE denial; original helper transcript replay',
                 source_sha256=sources())
        with Path(out).open('a') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')


@unittest.skipUnless(ASSET.is_file() and importlib.util.find_spec('unicorn'), 'original fixture/Unicorn required')
class PoolView(unittest.TestCase):
    def compare(self,case,setup=0):
        initial,expected,writes,helpers,meta,_=original(case,setup)
        actual=call_in_pypy(__name__,'candidate',(initial,helpers))
        self.assertTrue(actual['memory']==expected['memory'],'complete primitive memory differs')
        self.assertEqual(actual['regs'],expected['regs'])
        low,high=meta['ordered_write_frame']
        self.assertEqual(high,SS*16+SP+4)
        self.assertLessEqual(low,SS*16+SP)
        # Main701-order-boundary.md: only transient dead-frame ORDER is outside comparison.
        machine=PortMachine(initial['memory'],initial['load'])
        protected=[(SS*16+PARENT-11,19),(machine.far(0xA917),0x603F),(machine.far(0xA927),0x3C2)]
        self.assertTrue(all(a+n<=low or a>=high for a,n in protected),'frame overlaps caller/squad/pool')
        self.assertTrue(swap.live_writes(actual['writes'],(low,high))==swap.live_writes(writes,(low,high)),
                        'ordered live/caller byte writes differ')
        self.assertTrue(actual['unicorn_denied'] and actual['exe_denied'])
        self.assertEqual(actual['regs']['ESP'],SP+4);self.assertEqual(actual['regs']['EBP'],PARENT)
        names=[h['target'] for h in helpers]
        self.assertEqual(names.count('214B:0329'),3 if CASES[case].get('c20',0) else 5)
        self.assertEqual([n for n in names if n!='214B:0329' and n!='1771:2F37' and n!='214B:00DB'],
                         ['0791:DDCB','0791:DE51','1771:42BC','214B:13C5'])
        receipt(meta,expected,writes,helpers,initial,actual)
        return initial,expected,helpers

    def test_primitive_cases_both_sort_setups(self):
        for setup in (0,1):
            for case in CASES:
                with self.subTest(setup=setup,case=case):self.compare(case,setup)

    def test_falsifiers_row_base_highlight_attribute_and_return(self):
        from port_test_runtime import PortRuntimeError
        for variant,case in [('pool-view-row-off-by-one','first-page'),('pool-view-base-omitted','manager-2-base-81'),
                             ('pool-view-highlight-omitted','mid-highlight'),
                             ('pool-view-cursor-attribute-off-by-one','mid-highlight'),
                             ('pool-view-return-ax-clobbered','no-highlight')]:
            with self.subTest(variant=variant):
                initial,expected,writes,helpers,meta,_=original(case,0)
                try:actual=call_in_pypy(__name__,'candidate',(initial,helpers,variant))
                except PortRuntimeError as exc:
                    self.assertTrue(any(message in str(exc) for message in
                        ('helper order differs','complete helper-entry memory differs','ALL16 helper-entry ABI differs','missing helper call','extra helper call')),str(exc)[-300:])
                else:
                    self.assertTrue(actual['memory']!=expected['memory'] or actual['regs']!=expected['regs'],
                                    'falsifier escaped complete memory/ALL16 comparison')
                auxiliary('falsifier',variant=variant,case=case,detected=True)

    def test_code_free_sealed_primitive_exact_helper_replay(self):
        for case in ('first-page','last-row-highlight','empty-selected-word','top-wrap-skips-rows','footer-suppressed'):
            with self.subTest(case=case):
                initial,expected,writes,helpers,meta,image=original(case,0)
                sealed_initial=dict(initial,memory=swap.seal_memory(image,initial['memory']))
                sealed_helpers=[dict(h,entry=dict(h['entry'],memory=swap.seal_memory(image,h['entry']['memory']))) for h in helpers]
                actual=call_in_pypy(__name__,'candidate',(sealed_initial,sealed_helpers))
                self.assertTrue(actual['memory']==swap.seal_memory(image,expected['memory']),'complete sealed primitive memory differs')
                self.assertEqual(actual['regs'],expected['regs'])
                self.assertTrue(actual['unicorn_denied'] and actual['exe_denied'])
                auxiliary('sealed-primitive',case=case,complete_memory_all16_equal=True,unicorn_denied=True,exe_denied=True)


# --- sealed real-registered E44F pool toggle -> browse -> swap -> back/Esc ------------------------------------
RIGHT,LEFT,UP,DOWN,ENTER,ESC=0xAF,0xAE,0xAC,0xB1,0x0D,0x1B
EXIT='0791:E99C'
WATCH=('0791:E2E6','0791:DDCB','0791:DE27','0791:DE51','0791:DEA6','0791:DBFA','1771:4E22','1771:42BC',
       '1771:2F37','214B:00DB','214B:13C5','1771:3947')
# Mark a pool player, browse past it, return to the squad, swap, return to the pool, Esc twice.
KEYS=[RIGHT,DOWN,DOWN,ENTER,DOWN,LEFT,DOWN,ENTER,RIGHT,ESC,ESC]
FLOWS={'exchange-setup0':dict(setup=0,keys=KEYS),
       'exchange-setup1':dict(setup=1,keys=KEYS),
       'refused-gate-setup0':dict(setup=0,keys=KEYS,refused=1),
       'refused-gate-setup1':dict(setup=1,keys=KEYS,refused=1),
       'c1f-pool-unreachable':dict(setup=1,keys=[RIGHT,ESC],c1f=1)}
E44F_BP=SP-2


def flow_prepare(flow):
    from original_match.machine import Machine
    p=FLOWS[flow];image,asset_sha=swap.source();m=Machine(image.memory,image.load);ds=m.DS*16;game=m.far(0xA923)
    manager=m.read(game+1,1)[0];country=m.read(m.far(0xA91F)+3*(128+manager),1)[0]
    def w(a,v,n=2):m.write(a,int(v).to_bytes(n,'little'))
    w(game+2*manager+0x52,4);w(game+2*manager+0x5E,3)
    w(ds+0xC1B,3);w(ds+0xC1E,p['setup'],1);w(ds+0xC1F,p.get('c1f',0),1)
    w(game+0x13+manager,p.get('refused',0),1)
    # No pending friendly: isolate the allowed DBFA arm, not F031's ambiguous new-game tour edge.
    for i in range(36):w(m.far(0xA92F)+72*country+2*i,0)
    m.far_call('0791:E44F',(country,),EXIT,SS,SP);m.set_reg('bp',0x4200)
    for r,v in [('ax',0xA55A),('bx',0x1234),('cx',0x5678),('dx',0xABCD),('si',0x1357),('di',0x2468),('eflags',0x202)]:m.set_reg(r,v)
    return m,image,{'flow':flow,'asset_sha256':asset_sha,'country':country,'manager':manager}


def attach(m,keys,skip_3947=False):
    """The same key script, hooks and recorders on the original and the port: only observations, no effect."""
    ledger={'e2e6':[],'keys':[],'used':[],'calls':{a:0 for a in WATCH},'ddcb':[]};inside=[False]
    script=iter(list(keys)+[ESC]*3)             # trailing Esc only ever leaves; both machines read the same list
    ds=m.DS
    def squad(country):return [m.word_at(m.far(0xA917)+191*country+2*i) for i in range(20)]
    def state():
        game=m.far(0xA923);country=m.word_at(SS*16+E44F_BP+6)
        return {'c1b':m.rd(0xC1B),'game':m.read(game+0x52,0x30),'frame':m.read(SS*16+E44F_BP-0x12,0x1C),
                'squad':squad(country),'pool':sha(m.read(m.far(0xA927),0x3C2)),'c20':m.rd(0xC20,1)}
    def read(replay):
        ledger['keys'].append(state());k=next(script);ledger['used'].append(k);m.wr(0xA976,k|(k<<8));m.return_from(True)
    def poll(replay):m.set_reg('ax',(m.reg('ax')&0xFF00)|1);m.return_from(True)
    m.at('214B:08DD',read);m.at('214B:0723',poll)
    for address in WATCH:
        def count(replay,address=address):
            ledger['calls'][address]+=1
            if address=='1771:3947' and skip_3947:m.return_from(False,6)
        m.at(address,count)
    def enter(replay):inside[0]=True
    def leave(replay):
        if inside[0]:
            inside[0]=False
            ledger['e2e6'].append({'regs':swap.regs(m),'buffer':m.read(m.far(0xA96E),4000),**state()})
    m.at('0791:E2E6',enter);m.at(RETURN,leave)
    for site in ('0791:E411','0791:DE45'):
        m.at(site,lambda replay,site=site:ledger['ddcb'].append((site,m.reg('ax'))))
    m.at(EXIT,lambda replay:m.stop('t129p-flow-exit'))
    return ledger


def finish(m,ledger,full_memory=False):
    ledger['keys'].append(None)
    country=m.word_at(SS*16+E44F_BP+6)
    ledger['final']={'regs':swap.regs(m),'fields':swap.observable_fields(m) if False else None}
    ledger['final']['fields']={name:sha(m.read(m.far(ptr),size)) for name,ptr,size in
        [('countries',0xA917,0x603F),('players',0xA91B,0xEF24),('managers',0xA91F,0x195),
         ('pool',0xA927,0x3C2),('fixtures',0xA92B,0x4B48),('lists',0xA92F,0x2448),('game',0xA923,0x10E)]}
    ledger['final']['rng']={str(k):m.rd(k) for k in (0x7B62,0x8336,0x9B43)}
    ledger['final']['frame']=m.read(SS*16+E44F_BP-0x12,0x1C)
    ledger['final']['buffer']=m.read(m.far(0xA96E),4000);ledger['final']['video']=m.read(0xB8000,4000)
    ledger['final']['squad']=[m.word_at(m.far(0xA917)+191*country+2*i) for i in range(20)]
    if full_memory:ledger['final']['memory']=m.read(0,MEM_SIZE)
    return ledger


def flow_original(flow,skip_3947=False):
    m,image,meta=flow_prepare(flow);initial=swap.frame(m);ledger=attach(m,FLOWS[flow]['keys'],skip_3947)
    m.run(m.lin('0791:E99D'),fresh=True,timeout_s=120)
    return initial,finish(m,ledger,True),meta,image


def real_flow(initial,flow,variant=None):
    """Sealed (code-free) memory; positively denied Unicorn/GOAL.EXE; the REGISTERED production ports, stubs included,
    except the two key services the script answers. No helper replay: every callee is a registered port or the run fails.
    """
    swap.deny_original();m=PortMachine(initial['memory'],initial['load'])
    for r,v in initial['regs'].items():m.set_reg(r,v)
    loaded=[]
    for reg,_ in port.load(['all']):
        clean=port.Registry(reg.name,reg.doc);clean.variants=dict(reg.variants)
        for entry in reg.entries.values():
            if entry.address not in ('214B:08DD','214B:0723'):clean._add(entry)
        if clean.entries:loaded.append((clean,variant if reg.name=='selection' else None))
    installed=port.install(m,loaded);ledger=attach(m,FLOWS[flow]['keys'])
    m.run(m.lin('0791:E99D'),fresh=True,timeout_s=120)
    finish(m,ledger)
    stubs={e.address for reg,_ in port.load(['all']) for e in reg.entries.values() if e.stub is not None}
    ledger['installed_calls']={a:n for a,n in installed.calls.items() if n}
    ledger['registered']=sorted(installed.calls)
    ledger['stub_calls']={a:n for a,n in installed.calls.items() if n and a in stubs}
    ledger['unicorn_denied']=True;ledger['exe_denied']=True
    return ledger


def stub_boundary(true,stubbed,meta):
    """The accepted 1771:3947 stub omits DS:AAB2 and twelve attribute writes: the pure original and the original with
    that one routine returning at its entry (the registered stub) may differ only in screen-buffer/video attribute
    bytes and the routine's dead stack frame, nowhere else. Measured, never masked."""
    for a,b in zip(true['e2e6'],stubbed['e2e6']):
        assert {k:v for k,v in a.items() if k!='buffer'}=={k:v for k,v in b.items() if k!='buffer'},'stub changed more than the buffer'
        diff=[i for i in range(4000) if a['buffer'][i]!=b['buffer'][i]]
        assert diff and all(i%2 for i in diff),'stub effect is not attribute bytes'
        rows={i//160 for i in diff};assert rows==set(range(11,23)),sorted(rows)
    assert true['keys']==stubbed['keys']
    A,B=true['final'],stubbed['final']
    assert {k:v for k,v in A.items() if k not in ('buffer','video','memory')}=={k:v for k,v in B.items() if k not in ('buffer','video','memory')}
    for name in ('buffer','video'):
        diff=[i for i in range(4000) if A[name][i]!=B[name][i]];assert diff and all(i%2 for i in diff),name
    stack=range(SS*16,SS*16+0x10000);buffer=range(meta['buffer_linear'],meta['buffer_linear']+4000);video=range(0xB8000,0xB8000+4000)
    diff=[i for i in range(MEM_SIZE) if A['memory'][i]!=B['memory'][i]]
    counts={'stack':len([i for i in diff if i in stack]),'buffer':len([i for i in diff if i in buffer]),
            'video':len([i for i in diff if i in video])}
    assert all(i%2 for i in diff if i in buffer or i in video)
    return dict(counts,total=len(diff),outside=len(diff)-sum(counts.values()))


def reference_buffer(initial):
    from original_match.machine import Machine
    return Machine(initial['memory'],initial['load']).far(0xA96E)


@unittest.skipUnless(ASSET.is_file() and importlib.util.find_spec('unicorn'), 'original fixture/Unicorn required')
class SealedRealPoolFlow(unittest.TestCase):
    def compare(self,flow,boundary=True):
        initial,stubbed,meta,image=flow_original(flow,True)
        sealed=dict(initial,memory=swap.seal_memory(image,initial['memory']))
        actual=call_in_pypy(__name__,'real_flow',(sealed,flow))
        want=FLOWS[flow]['keys']
        self.assertEqual(stubbed['used'][:len(want)],want);self.assertEqual(actual['used'],stubbed['used'])
        self.assertEqual(len(stubbed['keys']),len(stubbed['used'])+1)
        # The actual E2E6 / DDCB / DEA6 / DBFA calls and every watched callee: counts equal the original's.
        self.assertEqual(actual['calls'],stubbed['calls'])
        self.assertEqual(actual['ddcb'],stubbed['ddcb'])
        for name in ('0791:E2E6','0791:DDCB'):self.assertEqual(actual['installed_calls'][name] if stubbed['calls'][name] else 0,stubbed['calls'][name])
        self.assertEqual(set(actual['stub_calls']),{'1771:3947'} if stubbed['calls']['1771:3947'] else set())
        self.assertEqual(actual['keys'],stubbed['keys'],'per-key records/cursor/frame/squad/pool differ')
        self.assertEqual(len(actual['e2e6']),len(stubbed['e2e6']))
        for i,(a,b) in enumerate(zip(actual['e2e6'],stubbed['e2e6'])):
            self.assertEqual(a['regs'],b['regs'],'E2E6 return ALL16 differs at call '+str(i))
            self.assertTrue(a['buffer']==b['buffer'],'complete screen buffer (rows, highlight, card, attributes) differs at call '+str(i))
            self.assertEqual({k:v for k,v in a.items() if k not in('regs','buffer')},{k:v for k,v in b.items() if k not in('regs','buffer')})
        A,B=actual['final'],stubbed['final']
        for name in ('fields','rng','frame','squad','buffer','video'):self.assertTrue(A[name]==B[name],name+' differs')
        for name in ('EAX','EBX','ECX','EDX','ESI','EDI','EBP','ESP','EIP','CS','DS','ES','SS','FS','GS'):
            self.assertEqual(A['regs'][name],B['regs'][name],name)
        self.assertEqual(B['regs']['ESP'],SP+6);self.assertEqual(B['regs']['EIP'],0xE99C)
        self.assertTrue(actual['unicorn_denied'] and actual['exe_denied'])
        self.assertIn('0791:E2E6',actual['registered']);self.assertIn('0791:DDCB',actual['registered'])
        if boundary:
            # The registered 3947 stub is the only departure from the pure original: measure it, never mask it.
            _,true,_,_=flow_original(flow,False);meta['buffer_linear']=reference_buffer(initial)
            report=stub_boundary(true,stubbed,meta)
            self.assertEqual(report['outside'],0,report)
            actual['stub_boundary']=report
        return initial,stubbed,actual,meta

    def test_exchange_flow_calls_records_cursor_attributes_stack_and_rng(self):
        for flow in ('exchange-setup0','exchange-setup1'):
            with self.subTest(flow=flow):
                initial,stubbed,actual,meta=self.compare(flow)
                self.assertEqual(stubbed['calls']['0791:E2E6'],6)
                self.assertEqual(stubbed['calls']['0791:DEA6'],2);self.assertEqual(stubbed['calls']['0791:DBFA'],1)
                self.assertGreaterEqual(stubbed['calls']['0791:DDCB'],8)
                # The pool Enter marked a player, the squad Enter swapped it in: the squad record really changed.
                first=stubbed['keys'][0]['squad'];self.assertNotEqual(first,stubbed['final']['squad'])
                self.assertEqual([s['frame'][17] for s in stubbed['keys'][3:7]],[0,1,1,1],'pool mark byte after the pool Enter')
                auxiliary('sealed-real-flow',flow=flow,calls=stubbed['calls'],ddcb=stubbed['ddcb'],
                          stub_calls=actual['stub_calls'],e2e6_calls=len(actual['e2e6']),stub_boundary=actual['stub_boundary'],
                          complete_screen_buffer_equal_to_registered_stub_original=True,all16_equal_at_each_e2e6_return=True,
                          fields=actual['final']['fields'],rng=actual['final']['rng'],unicorn_denied=True,exe_denied=True)

    def test_refused_gate_leaves_pool_unmarked_and_records_unswapped(self):
        for flow in ('refused-gate-setup0','refused-gate-setup1'):
            with self.subTest(flow=flow):
                initial,stubbed,actual,meta=self.compare(flow)
                self.assertEqual(stubbed['calls']['0791:DBFA'],1)
                marks={s['frame'][0x12-1] for s in stubbed['keys'] if s}   # E44F bp-1: the retained pool mark byte
                self.assertTrue(all(v in (0,1) for v in marks))
                pool_marks=[s['frame'][0x12-1] for s in stubbed['keys'][:8] if s]
                self.assertFalse(any(pool_marks[3:6]),'DBFA refusal still marked a pool player')
                auxiliary('sealed-real-flow',flow=flow,calls=stubbed['calls'],stub_calls=actual['stub_calls'],stub_boundary=actual['stub_boundary'],
                          complete_screen_buffer_equal_to_registered_stub_original=True,unicorn_denied=True,exe_denied=True)

    def test_c1f_mode_keeps_the_pool_unreachable(self):
        initial,stubbed,actual,meta=self.compare('c1f-pool-unreachable',boundary=False)
        self.assertEqual(stubbed['calls']['0791:E2E6'],0);self.assertEqual(actual['calls']['0791:E2E6'],0)
        self.assertEqual(actual['installed_calls'].get('0791:E2E6',0),0)
        auxiliary('sealed-real-flow',flow='c1f-pool-unreachable',calls=stubbed['calls'],unicorn_denied=True,exe_denied=True)

    def test_real_flow_falsifiers_row_base_highlight_attribute_and_return(self):
        for variant,flow in [('pool-view-row-off-by-one','exchange-setup0'),('pool-view-base-omitted','exchange-setup0'),
                             ('pool-view-highlight-omitted','exchange-setup0'),
                             ('pool-view-cursor-attribute-off-by-one','exchange-setup0'),
                             ('pool-view-return-ax-clobbered','exchange-setup0')]:
            with self.subTest(variant=variant):
                initial,stubbed,meta,image=flow_original(flow,True)
                sealed=dict(initial,memory=swap.seal_memory(image,initial['memory']))
                actual=call_in_pypy(__name__,'real_flow',(sealed,flow,variant))
                differs=(actual['e2e6']!=stubbed['e2e6'] or actual['keys']!=stubbed['keys'] or actual['final']['fields']!=stubbed['final']['fields']
                         or actual['final']['buffer']!=stubbed['final']['buffer'])
                self.assertTrue(differs,'falsifier escaped the real E44F flow comparison')
                auxiliary('real-flow-falsifier',variant=variant,flow=flow,detected=True)


class HistoricalE2E6Counter(unittest.TestCase):
    """Main701-counter-compatibility (T129p): the new unused E2E6 entry appears in `result.ports.calls` as a zero.
    Historical digests omit exactly that zero from a detached copy; any call, and every other field, stays hashed."""
    ADDRESS='0791:E2E6'

    def record(self):
        return dict(result={'score':[1,2],'ports':{'names':['selection'],'calls':{'0791:DEA6':0,'other':3}}},
                    events=[{'tick':7}],keys=[13],draws=[2],returned={'EFLAGS':2},memory=b'full memory')

    def target(self):
        from tests import test_route_entry_config as target
        return target

    def test_registry_inventory_adds_exactly_the_one_entry(self):
        self.assertEqual(selection.PORTS.entries[self.ADDRESS].ret,'ret 2')
        self.assertIsNone(selection.PORTS.entries[self.ADDRESS].stub)
        self.assertEqual(sorted(selection.PORTS.entries),sorted(['0791:E44F','0791:E022','0791:DE27','0791:DE51','0791:E2A0',
            '0791:E949','0791:EA09','1771:5532','1771:53E8','0791:DEA6','0791:DDCB','0791:E2E6']))

    def test_zero_counter_is_omitted_only_from_a_detached_copy(self):
        import copy
        target=self.target();row=self.record();expected=target.accepted_default_fields(row)
        for counters in ({self.ADDRESS:0},{self.ADDRESS:0,'0791:DDCB':0}):
            row=self.record();row['result']['ports']['calls'].update(counters);before=copy.deepcopy(row)
            self.assertEqual(target.accepted_default_fields(row),expected)
            self.assertEqual(row,before)

    def test_any_call_is_refused_without_mutation(self):
        import copy
        target=self.target()
        for address in (self.ADDRESS,'0791:DDCB'):
            for count in (1,-1,2):
                row=self.record();row['result']['ports']['calls'][address]=count;before=copy.deepcopy(row)
                with self.subTest(address=address,count=count):
                    with self.assertRaises(AssertionError):target.accepted_default_fields(row)
                    self.assertEqual(row,before)

    def test_missing_counter_and_every_other_field_remain_part_of_the_digest(self):
        import copy
        target=self.target();row=self.record();baseline=target.accepted_default_fields(row)
        for field in row:
            changed=copy.deepcopy(row);changed['result']['ports']['calls'][self.ADDRESS]=0
            if field=='result':changed[field]['ports']['calls']['other']+=1
            elif field=='memory':changed[field]+=b'!'
            elif field=='returned':changed[field]['EFLAGS']+=1
            else:changed[field].append(9)
            with self.subTest(field=field):
                self.assertNotEqual(target.accepted_default_fields(changed)[field],baseline[field])
