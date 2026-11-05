"""T125 synthetic branch tests; original-backed receipts are kept alongside the task proof."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from original_match import port
from original_match.port import assistant
from original_match.port.engine import PortMachine
from original_match.machine import MEM_SIZE


class Assistant(unittest.TestCase):
    def test_five_original_entries_and_falsifiers(self):
        self.assertEqual({a:e.ret for a,e in assistant.PORTS.entries.items()}, {
            '0791:DC7E':'ret', '0791:DBFA':'ret 2', '0791:DB38':'retf 2',
            '0791:DAF8':'retf 2', '1771:55FC':'retf'})
        self.assertTrue(all(e.stub is None for e in assistant.PORTS.entries.values()))
        self.assertEqual(set(assistant.PORTS.variants), {'ties-replace','swap-omitted','next-write-omitted'})

    def machine(self, manager=0):
        m=PortMachine(bytes(MEM_SIZE),0)
        def w(a,v,n=2):m.write(a,int(v).to_bytes(n,'little'))
        ds=m.DS*16
        for ptr,off,seg in [(0xA923,0x100,0x5000),(0xA91F,0,0x5100),
                (0xA917,0,0x5200),(0xA91B,0,0x5400),(0xA927,0,0x5600),
                (0xA92B,0x100,0x5800),(0xA92F,0,0x5900)]:
            w(ds+ptr,off);w(ds+ptr+2,seg)
        w(0x50101,manager,1);w(0x51000+3*(0x80+manager),7,1)
        w(0x50126,1)
        w(ds+0x9B43,0xABCD)
        m.assistant_ports=port.install(m,['assistant','runtime','update','attributes','pilot','menus','display','entrypoints'])
        return m,w

    def invoke(self,m,target,args=()):
        entry=assistant.PORTS.entries[target]
        end=m.far_call(target,args,'0791:E788',0x6000,0x3000)
        if not entry.far:
            words=[0xE788]+list(reversed(args))
            for i,v in enumerate(words):m.write(0x63000+2*i,v.to_bytes(2,'little'))
        m.set_reg('bp',0x3456)
        m.run(end,fresh=True,timeout_s=30)
        self.assertEqual(m.reg('sp'),0x3000+(4 if entry.far else 2)+entry.pop)
        self.assertEqual(m.reg('bp'),0x3456)
        return m.reg('ax')

    def test_sacked_retains_next_fixture_for_both_managers(self):
        for manager in (1,2):
            m,w=self.machine(manager);w(0x50147+manager,1,1)
            self.assertEqual(self.invoke(m,'1771:55FC')&255,0)
            self.assertEqual(m.rd(0x9B43),0xABCD)

    def test_no_next_clears_word_and_returns_false(self):
        m,w=self.machine()
        self.assertEqual(self.invoke(m,'1771:55FC')&255,0)
        self.assertEqual(m.rd(0x9B43),0)

    def test_next_and_tour_predicate_preserve_high_byte(self):
        m,w=self.machine()
        # Synthetic list: one played fixture then 35 pending ones, distinct continents.
        for i in range(36):
            w(0x59000+7*72+2*i,i+1)
            w(0x58100+8*i,0 if i==0 else 0xFE,1)
            w(0x58102+8*i,1,1);w(0x58106+8*i,8)
        w(0x52000+7*191+0x2C,1,1);w(0x52000+8*191+0x2C,2,1)
        self.assertEqual(self.invoke(m,'0791:DAF8',(7,))&255,1)
        self.assertEqual(m.rd(0x9B43),2)
        self.assertEqual(self.invoke(m,'0791:DB38',(7,))&255,1)

    def test_ordered_strict_improvements_and_current_position(self):
        for manager in (1,2):
            m,w=self.machine(manager)
            pool=0x56000+2*(80*(manager-1)+1)
            w(m.DS*16+0x6D18+2*manager,80*(manager-1)+1)
            for i in range(20):w(0x52000+7*191+2*i,1+i)
            for i in range(80):w(pool+2*i,21+i)
            for p in range(1,101):
                for k,v in ((4,80),(6,2),(7,9),(14,50)):w(0x54000+20*p+k,v,1)
            # All ties retain incumbents; then pool word21 improves slot1, 22 improves again.
            w(0x54000+20*21+4,100,1);w(0x54000+20*22+4,120,1)
            w(0x54000+20*23+4,200,1);w(0x54000+20*23+6,3,1)
            self.invoke(m,'0791:DC7E')
            self.assertEqual(m.word_at(0x52000+7*191),22)
            self.assertEqual(m.word_at(0x52000+7*191+2),21)
            self.assertEqual(m.word_at(pool),1)
            self.assertEqual(m.word_at(pool+2),2)
            self.assertEqual(m.assistant_ports.calls['1771:377E'],6320)
            self.assertEqual(m.assistant_ports.calls['214B:007B'],3)

    def state(self,m):
        from original_match.image import Image
        from original_match.port.tables import load
        tables=load(Path(__file__).resolve().parents[1]/'static/goal-exe/tables')
        image=Image.__new__(Image);image.header=bytes(0x78);image.memory=bytearray(m.read(0,MEM_SIZE))
        image.load=m.load;image.DS=m.DS;image.tables=tables
        return image.state(tables),tables

    def test_public_facade_copies_state_and_preserves_rng(self):
        import hashlib,json
        from original_match.assistant import recommend
        m,w=self.machine();w(m.DS*16+0x7B62,0x1234);w(m.DS*16+0x8336,0xBEEF)
        state,tables=self.state(m)
        digest=lambda v:hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
        before=digest(state);result=recommend(state,tables)
        self.assertEqual(digest(state),before)
        self.assertTrue(result['allowed']);self.assertIsNone(result['refusal'])
        from original_match.image import Image
        after=Image.from_state(result['state'],tables)
        self.assertEqual(after.memory[after.DS*16+0x7B62:after.DS*16+0x7B64],bytes.fromhex('3412'))
        self.assertEqual(after.memory[after.DS*16+0x8336:after.DS*16+0x8338],bytes.fromhex('efbe'))
        result['state']['initialised'].append([0,1])
        self.assertEqual(digest(state),before)

    def test_public_facade_refusal_keeps_selection_and_updates_copied_context(self):
        import hashlib,json
        from original_match.assistant import recommend
        m,w=self.machine();w(0x50113,1,1)
        state,tables=self.state(m)
        before=hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest()
        result=recommend(state,tables)
        self.assertFalse(result['allowed']);self.assertEqual(result['refusal'],'finals')
        self.assertEqual(result['squad'],[0]*20);self.assertEqual(result['pool'],[0]*80)
        self.assertEqual(result['next_fixture'],0xABCD)
        self.assertEqual(hashlib.sha256(json.dumps(state,sort_keys=True).encode()).hexdigest(),before)
        self.assertNotEqual(hashlib.sha256(json.dumps(result['state'],sort_keys=True).encode()).hexdigest(),before)

    def test_wrapped_pool_upper_bound_skips_scan(self):
        m,w=self.machine();w(m.DS*16+0x6D18,0xFFF0)
        self.invoke(m,'0791:DC7E')
        self.assertEqual(m.word_at(0x56000),0)

if __name__=='__main__':unittest.main()
