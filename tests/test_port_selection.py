"""T75 original selection branches, with original frames and guest-call sites."""
import inspect
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
from original_match.port import selection, menus
from tests.test_port_menus import KeysMem
from tests.test_port_update import Rig as BaseRig, PSEG, POFF, SQSEG, SQOFF

class Rig(BaseRig):
    def __init__(self):
        super().__init__()
        old=self.mem
        self.mem=KeysMem(old.memory,regs=old.regs)
        self.mem.listeners=old.listeners
        self.mem.keys=[];self.mem.key_sites=[];self.mem.poll_sites=[];self.mem.waiting=False
        self.mem.regs.update(cs=0x1771)
        self.respond=None
        self.calls=[]
        self.steps=0

    def run(self,address,words=(),answer=None,variant=None):
        self.respond=answer
        entry=selection.PORTS.entries[address]
        sp=self.mem.reg('sp')
        layout=[0x5678]+([0x0791] if entry.far else [])+list(words)
        for i,value in enumerate(layout):self.lin16(sp+2*i,value)
        return self._invoke(entry,variant)

    def _invoke(self,entry,variant=None):
        mem=self.mem;sp=mem.reg('sp');bp=mem.reg('bp')
        mem._entries.append((sp,entry.far))
        try:
            value=entry.fn(mem,variant)
            if inspect.isgenerator(value):
                gen=value;sent=None
                while True:
                    try:request=gen.send(sent)
                    except StopIteration as stop:value=stop.value;break
                    self.steps+=1
                    if self.steps>1000:raise AssertionError('menu did not terminate within1000 calls')
                    self.calls.append((request.target,request.args,request.ret_to,request.far))
                    oldsp=mem.reg('sp');oldbp=mem.reg('bp');oldcs=mem.reg('cs')
                    stack=oldsp
                    for word in request.args+((int(request.ret_to.split(':')[0],16),) if request.far else ())+ (int(request.ret_to.split(':')[1],16),):
                        stack=(stack-2)&0xFFFF;self.lin16(stack,word)
                    mem.regs.update(sp=stack,cs=int(request.target.split(':')[0],16))
                    handled=self.respond(request,mem) if self.respond else None
                    if handled is None and request.target=='23E4:08DF':
                        from original_match.port.pilot import in_set
                        element,seg,off=request.args
                        present=in_set(mem,mem.addr(seg,off),element&255)
                        mem.regs['eflags']=(mem.reg('eflags')&~0x40) if present else (mem.reg('eflags')|0x40)
                        handled=1<<(element&7)
                    if handled is None:
                        registry=selection.PORTS if request.target in selection.PORTS.entries else menus.PORTS if request.target in menus.PORTS.entries else port._module_registry('runtime')
                        callee=registry.entries.get(request.target)
                        if callee is None:callee=port._module_registry('pilot').entries.get(request.target)
                        if callee is not None:self._invoke(callee)
                        else:mem.regs['ax']=0
                    else:mem.regs['ax']=handled&0xFFFF
                    mem.regs.update(sp=oldsp,bp=oldbp,cs=oldcs)
                    sent=mem.reg('ax')
            if value is not None:mem.regs['ax']=int(value)&0xFFFF
            return value
        finally:
            mem._entries.pop();mem.regs.update(sp=sp,bp=bp)



PARENT=0x2000

class Selection(unittest.TestCase):
    def setup_parent(self,r,selected=0,cursor=3,marked=False,side=0):
        r.lin16(PARENT+6,7);r.lin16(PARENT-5,1);r.lin16(PARENT-9,selected)
        r.lin8(PARENT-1,marked);r.lin8(PARENT-3,side);r.ds16(0xC1B,cursor)
        r.squad(7,list(range(101,121)))

    def test_nine_listing_entries_and_returns(self):
        expected={'0791:E44F':'retf 2','0791:E022':'ret 2','0791:DE27':'ret 2','0791:DE51':'ret 6',
                  '0791:E2A0':'ret 2','0791:E949':'ret 2','0791:EA09':'ret 2',
                  '1771:5532':'retf','1771:53E8':'ret 6'}
        self.assertEqual({a:e.ret for a,e in selection.PORTS.entries.items()},expected)
        self.assertTrue(all(e.stub is None for e in selection.PORTS.entries.values()))

    def test_squad_pointer_and_pool_pointer(self):
        for side,index,wantseg,wantoff in [(1,3,SQSEG,SQOFF+7*0xBF+4),(2,8,0x4C00,0x110)]:
            r=Rig();self.setup_parent(r);r.ds16(0xA927,0x100);r.ds16(0xA929,0x4C00)
            r.run('0791:DE51',[PARENT,index,side])
            self.assertEqual((r.mem.reg('dx'),r.mem.reg('ax')),(wantseg,wantoff))
        r=Rig();self.setup_parent(r,cursor=20);r.run('0791:DE27',[PARENT]);self.assertEqual(r.mem.reg('ax'),20)

    def swap_rig(self,selected=3,cursor=13,marked=True,missing=False,unavailable=False,sentoff=False):
        r=Rig();self.setup_parent(r,selected,cursor,marked)
        if missing:r.squad(7,[0]+list(range(102,121)));r.ds16(0xC1B,1)
        r.player(103,16,0x20 if sentoff else 0)
        r.messages=[]
        def respond(q,mem):
            if q.target=='214B:1765':
                r.messages.append((q.args[0]&255,q.args[2]));return q.args[0]&255
            if q.target=='1771:3216':return int(unavailable)
            if q.target in ('23E4:062A','23E4:06B7','0791:C5DC'):return 0
            return None
        return r,respond

    def test_empty_slot_and_first_mark(self):
        for missing in (False,True):
            r,respond=self.swap_rig(marked=False,missing=missing)
            r.run('0791:E022',[PARENT],answer=respond)
            self.assertEqual(r.mem.u8(PARENT-1),int(not missing))
            self.assertEqual(r.messages,[(int(missing),0xDFDF)])
            if not missing:self.assertEqual((r.u16(PARENT-9),r.u16(PARENT-7)),(13,1))

    def test_same_block_unavailable_and_sentoff_refusals(self):
        for selected,cursor,unavailable,sentoff,want in [(3,5,False,False,0xDFF7),(13,20,False,False,0xDFF7),
                                                       (3,13,True,False,None),(3,13,False,True,0xE019)]:
            r,respond=self.swap_rig(selected,cursor,unavailable=unavailable,sentoff=sentoff)
            before=bytes(r.mem.memory[SQSEG*16+SQOFF+7*0xBF:SQSEG*16+SQOFF+7*0xBF+40])
            r.run('0791:E022',[PARENT],answer=respond)
            self.assertEqual(r.mem.u8(PARENT-1),0)
            self.assertFalse(r.args('0791:C5DC'))
            self.assertEqual(bytes(r.mem.memory[SQSEG*16+SQOFF+7*0xBF:SQSEG*16+SQOFF+7*0xBF+40]),before)
            self.assertEqual(r.messages[-1][0],1)
            if want is not None:self.assertEqual(r.messages[-1][1],want)

    def test_swap_changes_only_squad_form_and_marking_before_refresh(self):
        for side in (0,1):
            r,respond=self.swap_rig();r.lin8(PARENT-3,side)
            r.ds8(0x9B07+20*side+3,41);r.ds8(0x9B07+20*side+13,99)
            r.ds16(0x9A3E+40*side+6,711);r.ds16(0x9A3E+40*side+26,722)
            r.ds8(0x668+side,side*11);r.ds8(0x9B40,1)
            r.run('0791:E022',[PARENT],answer=respond)
            base=SQSEG*16+SQOFF+7*0xBF
            self.assertEqual((r.u16(base+4),r.u16(base+24)),(113,103))
            self.assertEqual((r.mem.ds8(0x9B07+20*side+3),r.mem.ds8(0x9B07+20*side+13)),(99,41))
            self.assertEqual((r.mem.ds16(0x9A3E+40*side+6),r.mem.ds16(0x9A3E+40*side+26)),(722,0))
            self.assertEqual(r.args('0791:C5DC'),[(side,3+side*11,13)])
            self.assertEqual(r.mem.ds8(0x9B40),0)

    def select_rig(self,keys,allowed=0,budget=2,request=0):
        r=Rig();r.ds8(0xC1E,1);r.ds8(0xC1F,1);r.ds8(0x9B41,allowed);r.ds8(0x9B3A,budget);r.ds8(0x9B40,request)
        r.ds16(0x9B36,19);r.country(7,0x2E,0x80);r.ds8(0xABC,1);r.ds16(0xC1B,3)
        r.mem.keys=list(keys)
        def respond(q,mem):
            if q.target in ('1771:4E22','214B:0329','1771:5532','214B:00DB'):return 0
            if q.target=='0791:E022':r.lin8(mem.reg('bp')-1,1);return 0
            return None
        return r,respond

    def test_request_toggle_and_zero_budget(self):
        for budget,request,keys,want in [(2,0,[13,27],1),(2,1,[13,27],0),(0,0,[13,27],0),(0,1,[13,27],0)]:
            r,respond=self.select_rig(keys,budget=budget,request=request)
            r.run('0791:E44F',[7],answer=respond)
            self.assertEqual(r.mem.ds8(0x9B40),want)
            self.assertFalse(r.args('0791:E022'))
            self.assertEqual(r.mem.key_sites,['0791:E61F']*2)

    def test_allowed_zero_budget_never_calls_swap(self):
        r,respond=self.select_rig([13,27],allowed=1,budget=0)
        r.run('0791:E44F',[7],answer=respond)
        self.assertFalse(r.args('0791:E022'))
        self.assertIn(0x2538,[a[1] for a in r.args('214B:0329')])

    def test_bench_and_pitch_instruction_templates(self):
        for cursor,want in [(11,0x4720),(12,0x4740),(20,0x4740)]:
            r=Rig();r.ds16(0xC1B,cursor);r.run('0791:E2A0',[PARENT],answer=lambda q,m:0)
            self.assertEqual([a[1] for a in r.args('214B:0329')],[0x4840,want])

    def validation_rig(self,positions=None,empty=(),unavailable=(),used=1):
        r=Rig();r.lin16(PARENT-5,91);r.ds16(0x9B34,7);r.ds16(0x9B36,19);r.ds8(0xC1F,used)
        positions=positions or [0,1,1,2,2,3,3,4,4,5,5]
        words=list(range(101,112))
        for index in empty:words[index]=0
        r.squad(7,words)
        for word,position in zip(range(101,112),positions):r.player(word,6,position)
        r.warned=[];r.flagged=[]
        def respond(q,mem):
            if q.target=='1771:0B77':return int(q.args[0]==7)
            if q.target=='1771:3216':return int(q.args[0] in unavailable)
            if q.target in ('23E4:062A','23E4:06B7'):return 0
            if q.target=='214B:1765':
                r.warned.append(q.ret_to)
                if q.args[0]&255:r.flagged.append(q.ret_to)
                return q.args[0]&255
            return None
        return r,respond

    def test_each_first_team_refusal_and_parent_restoration(self):
        cases=[({},True,None),({'positions':[0,0,1,2,2,3,3,4,4,5,5]},False,'0791:EBD7'),
               ({'positions':[1,1,1,2,2,3,3,4,4,5,5]},False,'0791:EC22'),
               ({'empty':(10,)},False,'0791:EC60'),
               ({'positions':[0,1,1,1,1,3,3,4,4,5,5]},False,'0791:ECEB'),
               ({'unavailable':(103,),'used':0},False,'0791:EB82'),
               ({'unavailable':(103,),'used':1},True,None)]
        for kwargs,want,where in cases:
            with self.subTest(kwargs=kwargs):
                r,respond=self.validation_rig(**kwargs)
                r.run('0791:EA09',[PARENT],answer=respond)
                self.assertEqual(r.mem.reg('ax')&255,int(want))
                self.assertEqual(r.u16(PARENT-5),91)
                self.assertEqual(r.flagged,[] if where is None else [where])
                if where=='0791:EB82':self.assertNotIn('0791:EBD7',r.warned)

    def test_both_managed_sides_are_checked_and_unmanaged_side_is_accepted(self):
        r,respond=self.validation_rig()
        r.squad(19,list(range(201,212)))
        for word in range(201,212):r.player(word,6,0)
        def both(q,mem):
            if q.target=='1771:0B77':return 1
            return respond(q,mem)
        r.run('0791:EA09',[PARENT],answer=both)
        self.assertEqual(r.mem.reg('ax')&255,0)
        self.assertEqual(r.flagged,['0791:EBD7'])
        r=Rig();r.lin16(PARENT-5,91);r.ds16(0x9B34,7);r.ds16(0x9B36,19)
        r.run('0791:EA09',[PARENT],answer=lambda q,m:0)
        self.assertEqual(r.mem.reg('ax')&255,1)
        self.assertEqual(r.u16(PARENT-5),91)
        self.assertFalse(r.args('214B:1765'))

    def test_full_pool_with_equal_keys_keeps_original_partition_tie_order(self):
        r=Rig();r.ds16(0xA927,0x100);r.ds16(0xA929,0x4C00);r.ds16(0x6D18,1)
        words=list(range(101,181))
        for index,word in enumerate(words):
            r.lin16(0x4C000+0x100+2*(index+1),word);r.player(word,6,index%14)
        original={word:index%14 for index,word in enumerate(words)}
        # Independent index-only rendition of the listing's strict comparisons.
        expected=list(words)
        def partition(lo,hi):
            i,j=lo,hi;pivot=original[expected[(lo+hi)//2]]
            while i<=j:
                while original[expected[i]]<pivot:i+=1
                while original[expected[j]]>pivot:j-=1
                if i<=j:expected[i],expected[j]=expected[j],expected[i];i+=1;j-=1
            if lo<j:partition(lo,j)
            if i<hi:partition(i,hi)
        partition(0,79)
        r.steps=-10000
        r.run('1771:5532')
        got=[r.u16(0x4C000+0x100+2*(index+1)) for index in range(80)]
        self.assertEqual(got,expected)
        self.assertEqual([r.mem.u8(PSEG*16+POFF+20*w+6) for w in words],[original[w] for w in words])
        self.assertTrue(r.args('1771:53E8'))

    def test_empty_pool_slots_share_the_original_sentinel_position(self):
        r=Rig();r.ds16(0xA927,0x100);r.ds16(0xA929,0x4C00);r.ds16(0x6D18,1)
        r.player(0,6,7)
        r.steps=-10000;r.run('1771:5532')
        # All80 zeros alias player0: only the first save sees7; later saves see14.
        self.assertEqual(r.mem.u8(PSEG*16+POFF+6),14)
