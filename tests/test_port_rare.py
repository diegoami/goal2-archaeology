"""T77 rare paths: concrete state changes, return sites and branch boundaries."""
import unittest
from tests.test_port_quick import Rig,rare
from tests.test_port_update import PSEG,POFF,SQSEG,SQOFF
PARENT=0x2000


class Rare(unittest.TestCase):
    def test_thirteen_real_entries(self):
        self.assertEqual(set(rare.PORTS.entries),{'0791:'+a for a in ('6ECF','73BA','72F2','7B77','7B24','B3B7','C01A','C0DF','C48D','BEC7','C24D','C2A8','C406')})
        self.assertTrue(all(e.stub is None for e in rare.PORTS.entries.values()))

    def test_penalty_stops_then_selects_role_three_and_sets_state(self):
        r=Rig();r.ds8(0x830E,9)
        r.run('0791:6ECF',answer=lambda q,m:1 if q.target=='0791:2996' else 0)
        self.assertEqual([t for t,*_ in r.calls],['0791:0441','0791:8062','0791:2996','0791:6D4E','0791:6DEA'])
        self.assertEqual(r.args('0791:0441'),[(2,)])
        self.assertEqual(r.args('0791:6D4E'),[(1,3,10)])
        self.assertEqual(tuple(v&255 for v in r.args('0791:6DEA')[0]),(2,0x39))
        self.assertEqual((r.mem.ds8(0x830E),r.mem.ds8(0x8324)),(0,1))

    def test_sent_off_sets_red_clears_booking_and_counts_correct_side(self):
        for side in (0,1):
            r=Rig();r.player(101,16,0xD8);r.ds8(0x7B86+side*10,255)
            r.run('0791:7B24',[101,side])
            self.assertEqual(r.mem.u8(PSEG*16+POFF+101*20+16),0xE8)
            self.assertEqual(r.mem.ds8(0x7B86+side*10),0)
            self.assertEqual(r.mem.ds8(0x7B86+(1-side)*10),0)

    def test_send_off_loss_cap_refusal_keeps_state(self):
        r=Rig();r.ds16(0x80E8+22+13,101)
        def answer(q,m):
            if q.target=='0791:2974':return 0
            if q.target=='0791:7A43':return 0
            self.fail(q.target)
        r.run('0791:7B77',[0x80FE,r.mem.DS],answer)
        self.assertEqual([t for t,*_ in r.calls],['0791:2974','0791:7A43'])

    def setup_squad(self,r,positions):
        r.squad(7,list(range(101,112)))
        for w,pos in zip(range(101,112),positions):r.player(w,6,pos)
        r.lin16(PARENT+6,SQOFF+7*0xBF);r.lin16(PARENT+8,SQSEG)

    def test_keeper_replacement_first_available_outfielder_or_none(self):
        cases=[({103},103,[102,103]),
               (set(),None,list(range(102,112))),
               ({111},111,list(range(102,112))),
               ({103,105},103,[102,103]),
               ({102,111},102,[102]),
               ({101,111},111,list(range(102,112)))]
        for available,want,scanned in cases:
            with self.subTest(available=sorted(available)):
                r=Rig();self.setup_squad(r,[0]+[5]*10)
                r.run('0791:C24D',[PARENT],lambda q,m:int(q.args[0] not in available))
                got=[r.mem.u8(PSEG*16+POFF+20*w+6) for w in range(101,112)]
                self.assertEqual(got,[0]+[0 if w==want else 5 for w in range(102,112)])
                self.assertEqual(r.args('1771:3216'),[(w,) for w in scanned])

    def test_rebalance_back_uses_surplus_threshold_and_skips_unavailable(self):
        r=Rig();self.setup_squad(r,[0,1,1,5,5,5,5,5,12,13,13])
        r.ds8(0xA2A,5);r.ds8(0xA2F,2)
        def answer(q,m):return int(q.args[0]==104)
        r.run('0791:C2A8',[PARENT,1],answer)
        self.assertEqual(r.mem.u8(PSEG*16+POFF+20*105+6),1)
        self.assertEqual(r.mem.u8(PSEG*16+POFF+20*104+6),5)

    def test_rebalance_without_surplus_keeps_positions(self):
        r=Rig();self.setup_squad(r,[0]+[5]*10)
        for k in range(1,6):r.ds8(0xA29+k,5);r.ds8(0xA2E+k,10)
        r.run('0791:C2A8',[PARENT,2],lambda q,m:0)
        self.assertEqual(r.mem.u8(PSEG*16+POFF+20*102+6),5)

    def test_wingback_conversion_changes_all_available_members_only(self):
        r=Rig();self.setup_squad(r,[0,3,4,3,5,6,7,8,9,12,13])
        r.lin8(r.mem.lin('0791:C3E6'),0x18)
        r.run('0791:C406',[PARENT],lambda q,m:int(q.args[0]==103) if q.target=='1771:3216' else None)
        got=[r.mem.u8(PSEG*16+POFF+20*w+6) for w in range(101,106)]
        self.assertEqual(got,[0,2,4,2,5])

    def test_forward_conversion_first_available_and_height_boundary(self):
        for height,want in [(71,13),(72,12)]:
            r=Rig();self.setup_squad(r,[0,9,10,11]+[5]*7)
            r.lin8(r.mem.lin('0791:BEA7')+1,0x0E);r.ds8(0xA28,13);r.ds8(0xA29,12)
            def answer(q,m):
                if q.target=='1771:3216':return int(q.args[0]==102)
                if q.target=='1771:2FAD':return height
            r.run('0791:BEC7',[SQOFF+7*0xBF,SQSEG],answer)
            self.assertEqual(r.mem.u8(PSEG*16+POFF+20*103+6),want)
            self.assertEqual(r.mem.u8(PSEG*16+POFF+20*104+6),11)

    def test_remove_dispatch_and_always_sort(self):
        for role,target in [(0,'C24D'),(1,'C2A8'),(2,'C2A8'),(3,'C406'),(4,'C406'),(12,'BEC7'),(13,'BEC7'),(5,None)]:
            r=Rig();r.ds16(0x80E8+22+13,101);r.player(101,6,role)
            def answer(q,m):return 0
            r.run('0791:C48D',[1,SQOFF+7*0xBF,SQSEG],answer)
            self.assertEqual([t for t,*_ in r.calls],(['0791:'+target] if target else [])+['0791:230C'])

    def test_tactic_changes_five_draws_once_then_gate_blocks_all_work(self):
        for address,initial,want,flag in [('C01A',0,0x3F,0x8332),('C0DF',0xFF,0xC0,0x8334)]:
            r=Rig();r.ds16(0x9B34,7);r.country(7,45,initial);r.squad(7,[101]*20);r.player(101,6,12)
            r.lin8(r.mem.lin('0791:BFFA')+1,0x30)
            draws=iter(range(1,6))
            def answer(q,m):
                if q.target=='214B:06B1':return next(draws)
                if q.target=='0791:BBFF':return 0
            r.run('0791:'+address,[0],answer)
            self.assertEqual(r.mem.u8(SQSEG*16+SQOFF+7*0xBF+45),want)
            self.assertEqual(r.mem.ds8(flag),1)
            self.assertEqual(len(r.args('214B:06B1')),5)
            self.assertEqual(r.args('0791:BBFF')[0][1]&255,want)
            r.calls=[];r.run('0791:'+address,[0],answer)
            self.assertEqual(r.calls,[])

    def test_restart_holder_sets_ready_then_shoots_and_nonholder_arrives(self):
        for ready in (0,1):
            r=Rig();off=0x80FE;r.ds8(off+6,1);r.ds8(0x830B,1);r.ds16(off,0x1234);r.ds16(0x8315,0x1234);r.ds8(0x8323,ready)
            def answer(q,m):
                if q.target=='0791:2CC5':return 1
                if q.target=='0791:28B2':return 1
                if q.target=='0791:2BE5':return 255
                return 0
            r.run('0791:73BA',[off,r.mem.DS],answer)
            self.assertEqual(len(r.args('0791:72F2')),1)
            # Exercise the nested body itself with the original parent pointer.
            r.lin16(PARENT+6,off);r.lin16(PARENT+8,r.mem.DS);r.calls=[]
            r.run('0791:72F2',[PARENT],answer)
            if ready:self.assertEqual(tuple(v&255 for v in r.args('0791:3C3F')[0][:2]),(17,3))
            else:self.assertEqual((r.mem.ds8(off+8),r.mem.ds8(0x8323)),(232,1))
        r=Rig();off=0x80FE;r.ds8(off+6,1);r.ds8(0x830B,2);r.ds8(off+18,10);r.ds16(0x850,0x3344)
        def answer(q,m):
            if q.target=='0791:045D':return 1
            if q.target=='0791:2C86':return 0x3344
            if q.target=='0791:2CC5':return 1
            return 0
        r.run('0791:73BA',[off,r.mem.DS],answer)
        self.assertEqual((r.mem.ds16(off+7),r.mem.ds8(off+18)),(0x3344,0))

    def test_top_scorer_inserts_name_count_and_existing_entry_moves_up(self):
        r=Rig();r.ds16(0xA93F,0x4000);r.ds16(0xA941,0)
        r.ds16(0x9B70,0x5000);r.ds16(0x9B72,0);r.lin8(0x5000+101,ord('A'))
        r.ds16(0x9B6C,0x6000);r.ds16(0x9B6E,0);r.lin8(0x6000+101*11,3)
        for i,c in enumerate(b'foo'):r.lin8(0x6000+101*11+1+i,c)
        r.player(101,17,4)
        r.run('0791:B3B7',[1,101])
        self.assertEqual(r.mem.u8(PSEG*16+POFF+101*20+17),5)
        self.assertEqual(r.u16(0x400E),101);self.assertEqual(r.u16(0x400C),5)
        self.assertEqual(r.mem.u8(0x4000),ord('A'))
        self.assertEqual(r.mem.read(0x4001,4),b'\x03foo')
        r.lin16(0x400C,6);r.lin16(0x401E,101);r.lin16(0x400E,102);r.player(101,17,7)
        r.run('0791:B3B7',[1,101])
        self.assertEqual((r.u16(0x400E),r.u16(0x400C)),(101,8))

if __name__=='__main__':unittest.main()
