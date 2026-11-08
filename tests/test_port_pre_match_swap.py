"""T123b: bounded pre-match DEA6 with real registered pointer/swap/re-sort helpers.
Synthetic frame and records are deliberate; published natural-entry proofs live in T123b receipts.
"""
import hashlib
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
from original_match.port import selection
from original_match.port.engine import PortMachine
from original_match.port.mem import PortError
from original_match.port.tables import load
from original_match.machine import MEM_SIZE

PARENT=0x4000
SS=0x9000

class PreMatchSwap(unittest.TestCase):
    def machine(self,setup=0,marked=False,cursor=3,marked_slot=3,pane=1,marked_pane=1,mode=0,empty=False):
        memory=bytearray(MEM_SIZE);load(ROOT/'static/goal-exe/tables').place(memory,0)
        m=PortMachine(memory,0)
        def w(address,value,n=2):m.write(address,int(value).to_bytes(n,'little'))
        ds=m.DS*16
        for ptr,seg in [(0xA917,0x5000),(0xA91B,0x6000),(0xA923,0x7000),(0xA91F,0x7100),(0xA927,0x7200)]:
            w(ds+ptr,0);w(ds+ptr+2,seg)
        w(ds+0xC1B,cursor);w(ds+0xC1E,setup,1);w(ds+0xC1F,mode,1)
        w(ds+0x9B34,7);w(ds+0x9B36,8)
        for country,first in ((7,1),(8,21)):
            w(0x50000+country*191+0x2E,0x81 if country==7 else 0,1)
            for i in range(20):
                player=first+i;w(0x50000+country*191+2*i,0 if empty and country==7 and i==cursor-1 else player)
                for k,value in ((0,country),(4,100),(6,i%14),(7,i%14),(14,50)):
                    w(0x60000+20*player+k,value,1)
        w(SS*16+PARENT+6,7);w(SS*16+PARENT-5,pane);w(SS*16+PARENT-7,marked_pane)
        w(SS*16+PARENT-9,marked_slot);w(SS*16+PARENT-11,0xBEEF);w(SS*16+PARENT-1,int(marked),1)
        real=[]
        for reg,v in port.load(['all']):
            clean=port.Registry(reg.name,reg.doc)
            for entry in reg.entries.values():
                if entry.stub is None:clean._add(entry)
            real.append((clean,v))
        m.ports_inst=port.install(m,real)
        return m,w

    def invoke(self,m):
        # Expected near frame from E66F, with the parent BP as its one argument.
        entry=selection.PORTS.entries['0791:DEA6']
        self.assertEqual(entry.ret,'ret 2');self.assertIsNone(entry.stub)
        m.far_call('0791:DEA6',(PARENT,),'0791:E672',SS,0x3000)
        m.write(SS*16+0x3000,bytes.fromhex('72e60040'))
        m.set_reg('bp',PARENT);m.run(m.lin('0791:E672'),fresh=True,timeout_s=30)
        self.assertEqual(m.reg('sp'),0x3004);self.assertEqual(m.reg('bp'),PARENT)

    def parent(self,m,k,n=2):return int.from_bytes(m.read(SS*16+PARENT+k,n),'little')
    def squad(self,m):return [m.word_at(0x50000+7*191+2*i) for i in range(20)]

    def test_first_enter_marks_nonempty_slot(self):
        m,w=self.machine(marked_slot=19);before=self.squad(m);self.invoke(m)
        self.assertEqual((self.parent(m,-1,1),self.parent(m,-9),self.parent(m,-7),self.parent(m,-11)),(1,3,1,0))
        self.assertEqual(self.squad(m),before)
        self.assertEqual(m.ports_inst.calls['214B:007B'],0)

    def test_first_enter_ignores_unmarked_stale_pool_location(self):
        m,w=self.machine(marked=False,marked_pane=2);self.invoke(m)
        self.assertEqual((self.parent(m,-1,1),self.parent(m,-7)),(1,1))

    def test_empty_first_enter_leaves_parent_fields_unchanged(self):
        m,w=self.machine(empty=True,marked_slot=19);before=self.squad(m);self.invoke(m)
        self.assertEqual((self.parent(m,-1,1),self.parent(m,-9),self.parent(m,-7),self.parent(m,-11)),(0,19,1,0xBEEF))
        self.assertEqual(self.squad(m),before)

    def test_two_enters_swap_starter_bench_then_use_live_sort(self):
        for setup,sort in [(0,'1771:52CC'),(1,'0791:230C')]:
            m,w=self.machine(setup=setup);self.invoke(m)
            w(m.DS*16+0xC1B,13);self.invoke(m)
            after=self.squad(m)
            self.assertEqual((self.parent(m,-1,1),self.parent(m,-11)),(0,0))
            self.assertIn(13,after[:11]);self.assertIn(3,after[11:]);self.assertNotIn(3,after[:11])
            self.assertEqual(m.ports_inst.calls[sort],1)
            positions=[m.read(0x60000+20*p+6,1)[0] for p in after]
            self.assertEqual(positions[:11],sorted(positions[:11]));self.assertEqual(positions[11:],sorted(positions[11:]))

    def test_original_partial_argument_frames_and_post_sort_read(self):
        for setup in (0,1):
            m,w=self.machine(setup=setup);events=[];post_sort=[]
            for address,far,count in [('0791:DE27',False,1),('0791:DE51',False,3),
                    ('214B:007B',True,5),('1771:52CC',True,1),('0791:230C',False,0)]:
                def entered(replay,address=address,far=far,count=count):
                    caller=m.where(m.stack_word(2) if far else m.reg('cs'),m.stack_word(0))
                    if caller in ('0791:DF5E','0791:DF65','0791:DF75','0791:DEF9','0791:DF00','0791:DF1A','0791:DF29','0791:DF33','0791:DF41'):
                        off=4 if far else 2
                        events.append((address,caller,[m.stack_word(off+2*i) for i in range(count)],m.stack_word(4)))
                m.at(address,entered)
            sort_return='0791:DF33' if setup else '0791:DF41'
            m.at(sort_return,lambda replay:post_sort.append(self.squad(m)))
            self.invoke(m);w(m.DS*16+0xC1B,13);self.invoke(m)
            self.assertEqual([(a,b) for a,b,_,_ in events],[
                ('0791:DE27','0791:DF5E'),('0791:DE51','0791:DF65'),('0791:DE27','0791:DF75'),
                ('0791:DE27','0791:DEF9'),('0791:DE51','0791:DF00'),('0791:DE51','0791:DF1A'),
                ('214B:007B','0791:DF29'),(('0791:230C' if setup else '1771:52CC'),sort_return)])
            self.assertEqual(events[0][2],[PARENT]);self.assertEqual(events[0][3],1)
            self.assertEqual(events[1][2],[PARENT,3,1]);self.assertEqual(events[3][3],1)
            self.assertEqual(events[4][2],[PARENT,13,1]);self.assertEqual(events[5][2],[PARENT,3,1])
            self.assertEqual(events[6][2],[2,7*191+4,0x5000,7*191+24,0x5000])
            self.assertEqual(post_sort,[self.squad(m)])

    def test_same_slot_second_enter_still_re_sorts_and_clears(self):
        for setup,sort in [(0,'1771:52CC'),(1,'0791:230C')]:
            m,w=self.machine(setup=setup,marked=True)
            self.invoke(m)
            self.assertEqual((self.parent(m,-1,1),self.parent(m,-11)),(0,0))
            self.assertEqual(m.ports_inst.calls[sort],1)
            self.assertGreaterEqual(m.ports_inst.calls['214B:007B'],1)

    def test_nonempty_first_mark_allows_empty_outgoing_second_slot(self):
        m,w=self.machine(cursor=13);self.invoke(m)
        w(0x50000+7*191+2*2,0);w(m.DS*16+0xC1B,3);self.invoke(m)
        self.assertIn(13,self.squad(m)[:11]);self.assertIn(0,self.squad(m)[11:])
        self.assertEqual(self.parent(m,-1,1),0)

    def test_in_match_modes_refuse_before_any_memory_write(self):
        for options in ({'mode':1},{'mode':255}):
            m,w=self.machine(**options)
            # Require the entry to exist on old code too: missing behavior fails this test.
            entry=selection.PORTS.entries['0791:DEA6'];self.assertEqual(entry.ret,'ret 2')
            m.far_call('0791:DEA6',(PARENT,),'0791:E672',SS,0x3000)
            m.write(SS*16+0x3000,bytes.fromhex('72e60040'));m.set_reg('bp',PARENT)
            before=hashlib.sha256(m.read(0,MEM_SIZE)).hexdigest()
            with self.assertRaises(PortError):m.run(m.lin('0791:E672'),fresh=True)
            self.assertEqual(hashlib.sha256(m.read(0,MEM_SIZE)).hexdigest(),before)

if __name__=='__main__':unittest.main()
