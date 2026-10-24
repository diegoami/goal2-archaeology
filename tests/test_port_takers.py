"""T76 listing-value prompt, clock, order and shoot-out branches."""
import inspect
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
from original_match.port import takers
from tests.test_port_selection import Rig as BaseRig
from tests.test_port_update import SQSEG,SQOFF,GSEG,GOFF


class Rig(BaseRig):
    def run(self,address,words=(),answer=None,variant=None):
        self.respond=answer
        entry=takers.PORTS.entries[address]
        sp=self.mem.reg('sp')
        for i,value in enumerate([0x5678]+([0x0791] if entry.far else [])+list(words)):
            self.lin16(sp+2*i,value)
        return self._invoke(entry,variant)

    def _invoke(self,entry,variant=None):
        mem=self.mem;sp=mem.reg('sp');bp=mem.reg('bp');mem._entries.append((sp,entry.far))
        try:
            value=entry.fn(mem,variant)
            if inspect.isgenerator(value):
                gen=value;sent=None
                while True:
                    try:request=gen.send(sent)
                    except StopIteration as stop:value=stop.value;break
                    self.steps+=1
                    if self.steps>10000:raise AssertionError('taker routine did not terminate')
                    self.calls.append((request.target,request.args,request.ret_to,request.far))
                    oldsp=mem.reg('sp');oldbp=mem.reg('bp');oldcs=mem.reg('cs');stack=oldsp
                    for w in request.args+((int(request.ret_to.split(':')[0],16),) if request.far else ())+ (int(request.ret_to.split(':')[1],16),):
                        stack=(stack-2)&0xFFFF;self.lin16(stack,w)
                    mem.regs.update(sp=stack,cs=int(request.target.split(':')[0],16))
                    handled=self.respond(request,mem) if self.respond else None
                    if handled is None:
                        registries=[takers.PORTS]+[port._module_registry(n) for n in ('runtime','menus')]
                        callee=next((reg.entries[request.target] for reg in registries if request.target in reg.entries),None)
                        if callee is not None:self._invoke(callee)
                        else:mem.regs['ax']=0
                    else:mem.regs['ax']=handled&0xFFFF
                    mem.regs.update(sp=oldsp,bp=oldbp,cs=oldcs);sent=mem.reg('ax')
            if value is not None:mem.regs['ax']=int(value)&0xFFFF
            return value
        finally:
            mem._entries.pop();mem.regs.update(sp=sp,bp=bp)


class Takers(unittest.TestCase):
    def test_ten_listing_entries_and_returns(self):
        expected={f'0791:{a}':ret for a,ret in [('CC7B','ret 4'),('CC2E','ret 2'),('0B7C','ret 4'),
                  ('9B0C','ret'),('9B5B','ret'),('A10A','ret'),('0C0B','ret'),('9B93','ret 2'),
                  ('9ED3','ret 2'),('A006','ret 2')]}
        self.assertEqual({a:e.ret for a,e in takers.PORTS.entries.items()},expected)
        self.assertTrue(all(e.stub is None for e in takers.PORTS.entries.values()))

    def test_wait_zero_timeout_and_key_poll(self):
        for count,at,polls,delays in [(0,99,0,0),(3,99,3,3),(5,2,2,1)]:
            r=Rig();seen=[]
            def answer(q,mem):
                seen.append(q.target)
                if q.target=='214B:0723':return int(seen.count(q.target)==at)
                return 0
            r.run('0791:CC2E',[count],answer)
            self.assertEqual(seen.count('214B:0723'),polls)
            self.assertEqual(seen.count('214B:1E09'),delays)
            self.assertTrue(all(args==(10,) for target,args,_,_ in r.calls if target=='214B:1E09'))

    def test_speed_byte_bounds(self):
        for start,want in [(0,2),(1,2),(2,3),(4,5),(5,5),(255,255)]:
            r=Rig();r.lin8(GSEG*16+GOFF+63,start);r.run('0791:0C0B')
            self.assertEqual(r.mem.u8(GSEG*16+GOFF+63),want)

    def test_yes_no_with_and_without_a_waiting_key(self):
        for key,want in [(None,0),(ord('Y'),1),(ord('y'),1),(ord('N'),0),(13,0)]:
            r=Rig();r.mem.regs['ax']=0xAB00
            r.lin8(0x1000,3)
            for i,c in enumerate(b'foo'):r.lin8(0x1001+i,c)
            def answer(q,mem):
                if q.target=='0791:CC2E':return 0
                if q.target=='214B:0723':return int(key is not None)
                if q.target=='214B:08DD':r.ds8(0xA976,key);return key
                if q.target.startswith('214B:'):return 0
            r.run('0791:0B7C',[0x1000,0],answer)
            self.assertEqual(r.mem.reg('ax')&255,want)
            self.assertEqual(sum(t=='214B:08DD' for t,*_ in r.calls),int(key is not None))

    def prompt_rig(self,stored=105,side=0,role=3):
        r=Rig();r.ds16(0x9B34+2*side,7);r.squad(7,list(range(101,121)))
        r.ds16(0x9976+10*side+2*role,stored)
        return r

    def test_unavailable_and_outside_eleven_stored_taker_falls_back(self):
        for side in (0,1):
            for unavailable in (False,True):
                r=self.prompt_rig(999,side);seen=[]
                def answer(q,mem):
                    if q.target=='1771:3216':return int(unavailable and q.args[0]==999)
                    if q.target=='0791:6B65':return 12
                    if q.target=='0791:1FDD':
                        seen.append(q.args);r.ds16(0x9976+10*side+6,105);return 0
                    if q.target in ('0791:CC2E','0791:A699') or q.target.startswith('214B:') or q.target.startswith('1771:'):return 0
                r.run('0791:CC7B',[3,side],answer)
                self.assertEqual(r.mem.reg('ax'),105)
                self.assertEqual(len(seen),1)
                self.assertEqual(tuple(x&255 for x in seen[0]),(side,0,3))

    def test_enter_chooses_highlight_escape_retains_current_and_c_computes(self):
        for key,want in [(13,107),(27,105),(ord('C'),109)]:
            r=self.prompt_rig();r.ds8(0x767,12)
            def answer(q,mem):
                if q.target=='1771:3216':return 0
                if q.target=='0791:6B65':return 5
                if q.target=='0791:1FDD':r.ds16(0x997C,109);return 0
                if q.target=='0791:CC2E':
                    r.lin16(mem.reg('bp')-5,7);return 0
                if q.target=='214B:0723':return 1
                if q.target=='214B:08DD':r.ds8(0xA976,key);return key
                if q.target=='0791:A699' or q.target.startswith('214B:') or q.target.startswith('1771:'):return 0
            r.run('0791:CC7B',[3,0],answer)
            self.assertEqual(r.mem.reg('ax'),want)

    def test_order_escape_removes_last_pick_and_final_down_is_pushed_back(self):
        r=Rig();parent=0x2000;r.lin8(parent-31,0);r.ds16(0x9B34,7);r.squad(7,list(range(101,121)))
        r.ds8(0x668,0);r.ds8(0x7920,255);r.ds8(0x7921,1)
        moves=iter([(1,13),(2,27),(2,13),(1,13),(3,13)])
        def answer(q,mem):
            if q.target=='1771:3216':return int(q.args[0]>103)
            if q.target=='214B:1560':
                cursor,key=next(moves);r.lin16(mem.reg('bp')-6,cursor);r.ds8(0xA976,key);return key
            if q.target=='23E4:025D' or q.target in ('214B:0329','214B:13C5') or q.target.startswith('1771:'):return 0
        r.run('0791:9B93',[parent],answer)
        self.assertEqual(r.mem.read(parent-26,4),bytes([3,2,1,3]))
        pushes=[args for target,args,*_ in r.calls if target=='214B:0993']
        self.assertEqual(len(pushes),4)
        self.assertTrue(all(args[0]&255==0xB1 for args in pushes))
        self.assertEqual(r.mem.ds8(0x79AE),1)


if __name__=='__main__':unittest.main()
