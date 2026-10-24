"""#419: finals effects, parent frames, bracket bounds and meaningful returns."""
import unittest
from tests.test_port_display import Rig, Case, PARENT, FXSEG, FXOFF, GSEG, GOFF

class Finals(Case):
    def rig(self,snapshot=0,interactive=0):
        r=Rig();r.mem.regs.update(ax=0xBEEF,dx=0xCAFE)
        r.lin8(PARENT-9,snapshot);r.lin16(PARENT-8,20);r.lin16(PARENT-4,3);r.lin16(PARENT-2,3)
        r.lin8(PARENT+10,interactive)
        r.ds16(0xA92B,FXOFF);r.ds16(0xA92D,FXSEG)
        return r

    def test_winner_and_loser_return_real_countries_for_all_decider_bytes(self):
        for decider in (0,1,2,255):
            for target,want in (('1771:5C94',3 if decider==1 else 20),('1771:5CCB',3 if decider==0 else 20)):
                with self.subTest(target=target,decider=decider):
                    r=self.rig();r.fixture(8,20,3);r.lin8(FXSEG*16+FXOFF+3,decider)
                    r.run(target,(FXOFF,FXSEG))
                    self.assertEqual(r.mem.regs['ax'],want)
                    self.assertEqual(r.calls,[])

    def test_leaderboard_keeps_attribute_and_three_selected_entries(self):
        for snapshot,continent in ((0,2),(1,5)):
            r=self.rig(snapshot);r.country(20,0x2C,2)
            r.ds16(0xA93F,0x100);r.ds16(0xA941,FXSEG)
            for k in (1,2,3):r.lin16(FXSEG*16+0x100+continent*0x60+k*0x10-0x62,1)
            r.run('1771:883F',(PARENT,))
            self.assertEqual(r.mem.ds8(0xAAB2),7)
            self.assertEqual(len(r.args('214B:01A3')),3)
            self.assertEqual(len(r.args('214B:026D')),6)
            self.assertEqual(r.written('1771:8881'),[(0xAAB2,1,7)])

    def test_group_bounds_temporary_country_key_effect_and_restore(self):
        for snapshot,limit in ((0,8),(1,2)):
            r=self.rig(snapshot,1);r.country(1,0x2C,1);r.country(20,0x2C,2)
            r.ds8(0x1136+snapshot,limit);r.lin16(PARENT-4,limit+1)
            key_calls=[]
            def answer(q,mem):
                if q.target=='1771:59D8':return 1
                if q.target=='214B:1560':
                    key_calls.append(q.args)
                    self.assertEqual(r.u16(PARENT-8),1 if snapshot else 20)
                    self.assertEqual(r.u16(PARENT-4),1)
                    r.lin16(PARENT-4,2);r.ds8(0xA976,0x4D)
                return 0
            r.run('1771:9028',(PARENT,),answer=answer)
            self.assertEqual(key_calls,[(r.mem.regs['ss'],PARENT-4,limit)])
            self.assertEqual((r.u16(PARENT-8),r.u16(PARENT-4),r.mem.ds8(0xA976)),(20,2,0x4D))
            self.assertEqual(len(r.args('1771:8CA2')),6)

    def test_bracket_dispatch_full_copy_and_key_order(self):
        for snapshot,target in ((0,'1771:91CE'),(1,'1771:937C')):
            r=self.rig(snapshot);r.country(20,0x2C,2)
            r.ds16(0xA96A,0x100);r.ds16(0xA96C,0x4000)
            r.ds16(0xA96E,0x200);r.ds16(0xA970,0x4100)
            def answer(q,mem):
                if q.target=='214B:08DD':r.ds8(0xA976,27)
                return 0
            r.run('1771:9509',(PARENT,),answer=answer)
            self.assertEqual([q[0] for q in r.calls],['1771:5AC4','1771:883F',target,'23E4:025D','214B:08DD'])
            self.assertEqual(r.args('23E4:025D'),[(0x4100,0x200,0x4000,0x100,4000)])
            self.assertEqual(r.mem.ds8(0xA976),27)
            self.assertEqual(r.args(target),[(0x2FFE,)])

    def test_playoff_odd_carry_visits_four_aggregate_fixtures(self):
        r=self.rig();r.country(20,0x2C,3)
        r.lin8(GSEG*16+GOFF+0x3C,6);r.lin16(GSEG*16+GOFF+0x2C,100)
        r.run('1771:8D84',(PARENT,))
        self.assertEqual(len(r.args('1771:8CA2')),8)
        self.assertEqual([x[0] for x in r.args('1771:8CA2')],[100+k for k in range(8)])
        self.assertEqual([x[0] for x in r.args('1771:8CCF')],[0x961+k for k in range(4)])
        self.assertEqual([x[1] for x in r.args('1771:8CCF')],[9,11,13,15])
        r=self.rig();r.lin8(GSEG*16+GOFF+0x3C,5);r.run('1771:8D84',(PARENT,))
        self.assertEqual(r.calls,[])

    def test_bracket_fixture_zero_and_marker_conditions(self):
        for index,score,kind,decider in ((0,0,8,0),(1,254,8,0),(1,1,6,0),(1,1,8,0),(1,1,8,1)):
            r=self.rig();r.fixture(kind,20,3);r.lin8(FXSEG*16+FXOFF,score);r.lin8(FXSEG*16+FXOFF+3,decider)
            r.run('1771:8CCF',(PARENT,23,8,4,9,index))
            self.assertEqual(len(r.args('1771:0FB1')),2 if index else 0)
            self.assertEqual(len(r.args('1771:76FA')),1 if index else 0)
            markers=r.args('214B:02C8')
            self.assertEqual(len(markers),int(bool(index and score<254 and kind!=6)))
            if markers:self.assertEqual(markers[0][3:5],(9+int(decider==0),19))

    def test_selector_helpers_preserve_lookup_arguments_and_nested_calls(self):
        r=self.rig();r.ds8(0x1116+3,4);r.ds8(0x1113+3,9)
        r.run('1771:89C1',(PARENT,));self.assertEqual(r.args('214B:13C5'),[(23,9,4)])
        r=self.rig();r.country(20,0x2C,2)
        for off,val in ((0x1121,5),(0x1119,10),(0x111D,11)):r.ds8(off+2,val)
        r.run('1771:89FE',(PARENT,));self.assertEqual(r.args('214B:13C5'),[(11,10,5)])
        r=self.rig();r.run('1771:8A5D',(PARENT,1))
        self.assertEqual([q[0] for q in r.calls],['214B:0329','1771:89C1','1771:89FE'])

    def test_continental_bracket_stage_bound_and_four_reference_positions(self):
        for stage in (3,4):
            r=self.rig();r.lin16(PARENT+4,0x2600)
            r.lin16(0x2600-8,20);r.country(20,0x2C,2)
            r.lin8(GSEG*16+GOFF+0x3C,stage)
            r.run('1771:91CE',(PARENT,))
            self.assertEqual(len(r.args('1771:8CCF')),4 if stage>3 else 0)

    def test_world_bracket_gates_unpublished_fixtures(self):
        for snapshot,available,want in ((0,0,16),(1,4,3),(1,17,16)):
            r=self.rig();r.lin16(PARENT+4,0x2600)
            r.lin16(0x2600-8,20);r.lin8(0x2600-9,snapshot)
            r.lin8(GSEG*16+GOFF+0x40,snapshot)
            r.lin16(GSEG*16+GOFF+0x2A,1);r.lin16(GSEG*16+GOFF+0x28,available)
            # Sixteenth fixture is unplayed so no placement getters are called.
            r.lin8(FXSEG*16+FXOFF+15*8,254)
            def answer(q,mem):
                if q.target=='23E4:08DF':mem.regs['eflags'] |= 64
                return 0
            r.run('1771:937C',(PARENT,),answer=answer)
            self.assertEqual(len(r.args('1771:8CCF')),want)
            self.assertEqual(r.args('1771:5C94'),[])

    def test_every_advertised_new_omission_variant_omits_its_body(self):
        from original_match import port
        from original_match.port import _display_finals
        reg=port._module_registry('display')
        for address in _display_finals.PORTS.entries:
            with self.subTest(address=address):
                variant='omit-'+address.lower().replace(':','-')
                self.assertIn(variant,reg.variants)
                r=self.rig();before=bytes(r.mem.memory);registers=dict(r.mem.regs)
                r.run(address,(PARENT,),variant=variant)
                self.assertEqual(r.calls,[])
                self.assertEqual(r.writes,[])
                self.assertEqual(r.mem.regs,registers)
                # Rig writes the declared entry stack before invoking the body.
                after=bytes(r.mem.memory)
                self.assertEqual(after[:0x3000],before[:0x3000])
                self.assertEqual(after[0x300A:],before[0x300A:])

if __name__=='__main__':unittest.main()
