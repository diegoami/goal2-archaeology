"""T122a: shared news routines, their original call frames and ordered effects."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from original_match import port
from test_port_silent import Rig as BaseRig, responder, GAME
from test_port_update import Case, FXSEG, FXOFF


class Rig(BaseRig):
    def run(self, address, words=(), answer=None, variant=None):
        entry = port._module_registry('news').entries[address]
        for i, value in enumerate([0x5678] + list(words)):
            self.lin16(0x3000 + i * 2, value)
        self.mem._entries.append((0x3000, False))
        try:
            result = entry.fn(self.mem, variant)
            if not hasattr(result, 'send'):
                return result
            sent = None
            while True:
                try:
                    req = result.send(sent)
                except StopIteration as stop:
                    return stop.value
                self.calls.append((req.target, req.args, req.ret_to, req.far))
                if len(self.calls) > 5000:
                    raise AssertionError('port did not return')
                sent = answer(req, self.mem) if answer else 0
                self.mem.regs['ax'] = sent & 0xffff
        finally:
            self.mem._entries.pop()


class Shared(Case):
    def test_twenty_original_routines_and_returns(self):
        reg = port._module_registry('news')
        expected = {a: 'ret 2' for a in '08F9 094A 09DB 0A53 0ACB 0B0A 0B4D 0B77 0C3A 1F4D 4865 0572'.split()}
        expected.update({'03C4':'ret 6', '045D':'ret 4', '04F5':'ret 4', '0868':'ret 0xa',
                         '2E1F':'ret 0xe', '3A5E':'ret 6', '4045':'ret 0xa', '47E6':'ret 0xa', '11D9':'ret 2'})
        self.assertEqual({a: e.ret for a,e in reg.entries.items()}, {'000E:'+a:r for a,r in expected.items()})

    def test_crowd_uses_two_draws_per_seat_and_a_conditional_third(self):
        for char, count in ((6,1500),(7,1000)):
            r=Rig(); r.ds16(0xA96A,0x100); r.ds16(0xA96C,0x5000)
            r.lin8(0x50100,char)
            r.run('000E:045D',[0x2800,2],responder({'214B:06B1':1}))
            self.assertEqual(len(r.args('214B:06B1')),count)
            self.assertEqual(r.args('214B:1E09'),[(4,)]*50)
            self.assertEqual(len(r.written('000E:04D0')),500 if char<7 else 0)

    def test_first_key_poll_stops_the_tune_before_any_note(self):
        r=Rig(); r.run('000E:04F5',[0x2800,8],responder({'214B:0723':1}))
        self.assertEqual(r.targets(), [('214B:1E75','000E:0506'),('214B:0723','000E:0515')])
        self.assertEqual(r.mem.ds8(0x7968),8)

    def test_celebration_still_animates_once_before_the_first_poll(self):
        r=Rig(); r.lin8(0x2800+6,1)
        r.run('000E:0572',[0x2800],responder({'214B:0723':1}))
        self.assertEqual(r.args('000E:045D'),[(2,0x2ffe)])
        self.assertEqual(r.targets()[-2:],[('000E:045D','000E:05E7'),('214B:0723','000E:05EC')])
        self.assertEqual(r.args('000E:04F5'),[])

    def test_sack_score_unsigned_year_and_all_exemptions(self):
        for year,kind,finals,group,exempt,want in ((1,2,0,0,0,0),(2,1,0,0,0,0),(2,2,1,1,0,0),
                (2,2,0,0,1,0),(2,2,0,0,0,-12),(0xffff,2,1,0,0,-12)):
            r=Rig(); r.lin16(0x2808,3); r.lin16(0x2804,FXOFF); r.lin16(0x2806,FXSEG)
            r.country(3,0x2e,0x81); r.country(3,0xbe,exempt)
            r.lin16(GAME+0x38,year); r.lin8(GAME+2,group)
            r.lin8(FXSEG*16+FXOFF+2,kind)
            r.ds16(0xA91F,0x100); r.ds16(0xA921,0x5100); r.lin8(0x51100+3*0x81+2,244)
            got=r.run('000E:0B77',[0x2800],responder({'1771:59D8':finals}))
            self.assertEqual(got & 0xffff,want & 0xffff)

    def test_discipline_thresholds_read_the_grandparent_side(self):
        for stats,want in (((10,2,1),0),((11,2,1),1),((10,3,1),1),((10,2,2),1)):
            r=Rig(); r.lin16(0x2804,0x2900); r.lin16(0x2904,0x2a00); r.lin8(0x29ff,1)
            for off,value in zip((0x7b84,0x7b85,0x7b86),stats): r.ds8(off+10,value)
            self.assertEqual(r.run('000E:4865',[0x2800]) & 255,want)

    def test_rating_comparisons_keep_home_advantage_and_signed_words(self):
        for side in (0,1):
            for first,second in ((10,10),(10,13),(13,10),(0x7fff,0x8000)):
                for address in ('000E:09DB','000E:0A53'):
                    r=Rig(); r.lin8(0x27ff,side); r.lin16(0x2804,FXOFF); r.lin16(0x2806,FXSEG)
                    r.fixture(2,3,4)
                    got=r.run(address,[0x2800],responder({'1771:10E7':[first,second]}))
                    signed=lambda v: (v+32768)%65536-32768
                    if address.endswith('09DB'): want=signed(second)>signed(first+2-int(side==1))
                    else: want=signed(second+2+int(side==1))>signed(first)
                    self.assertEqual(got & 255,int(want))

    def test_all_twenty_routines_match_the_original_on_declared_frames(self):
        # Every routine also proves independently, beyond route's nested calls.
        # The synthetic driver declares all memory edits and verifies its asset.
        port._module_registry('news')
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'experiments/E040-route-fixture-writes/out/T122a/prove_shared.py'
        spec=importlib.util.spec_from_file_location('t122a_shared_proof',path)
        module=importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except ImportError as exc:
            if exc.name=='unicorn': self.skipTest('unicorn missing')
            raise
        case=next(c for c in module.runner.CASES if c[0]=='E040-r0004')
        asset=module.ROOT/'.cache/dl'/case[3]
        if not asset.is_file(): self.skipTest('published E040 state missing; runner.py --fetch')
        import hashlib
        data=asset.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),module.runner.expected(case[3]))
        visited=set()
        for case in module.cases():
            if case[1] in visited: continue
            visited.add(case[1])
            with self.subTest(routine=case[1]):
                result=module.prove(data,case)
                self.assertEqual(result['status'],'completed',result['error'])
                self.assertEqual(result['proof'][case[1]]['proved'],1)
                self.assertEqual(result['proof'][case[1]]['before'],0)
        self.assertEqual(len(visited),20)


class ResultColumn(Case):
    def frame(self,kind=2,winner=0,side=0):
        r=Rig();parent=0x2800
        r.lin16(parent+4,FXOFF);r.lin16(parent+6,FXSEG);r.lin16(parent+8,3)
        r.lin8(parent-1,side);r.fixture(kind,3,4);r.lin8(FXSEG*16+FXOFF+3,winner)
        return r,parent

    def test_port_has_original_near_return_and_no_other_new_owner(self):
        entry=port._module_registry('news').entries['000E:11D9']
        self.assertEqual(entry.ret,'ret 2')
        self.assertFalse(entry.far)

    def test_winning_and_losing_world_final_render_different_three_line_columns(self):
        for winner,want in ((0,[0x0CCF,0x0CE4]),(1,[0x0FDB,0x0FE3,0x0FEB])):
            r,parent=self.frame(kind=0xCB,winner=winner)
            r.run('000E:11D9',[parent])
            self.assertEqual(len(r.args('000E:062F')),1)
            constants=[value for value in r.args('000E:062F')[0] if value in want]
            self.assertEqual(constants,want)
            self.assertEqual(len(r.args('000E:0ACB')),int(winner==0))
            self.assertEqual(r.args('214B:06B1'),[])

    def test_confidence_choice_draw_has_original_bound_and_return_site(self):
        for choice in (1,2):
            r,parent=self.frame()
            r.run('000E:11D9',[parent],responder({'1771:5C60':1,'0791:B71C':0xfffb,'214B:06B1':choice}))
            self.assertEqual(r.args('214B:06B1'),[(2,)])
            self.assertEqual(r.calls_of('214B:06B1')[0][2],'000E:139B')
            self.assertEqual(len(r.args('000E:0ACB')),int(choice==1))
            self.assertEqual(len(r.args('000E:0B4D')),int(choice==2))
            self.assertEqual(len(r.args('000E:062F')),1)

    def test_red_card_branch_uses_the_current_column_frame(self):
        r,parent=self.frame();r.ds8(0x7B86,1)
        r.run('000E:11D9',[parent],responder({'1771:5C60':2}))
        self.assertEqual(r.args('000E:0C3A'),[(0x2ffe,)])
        self.assertEqual(r.args('0791:B71C'),[])

    def test_all_sack_bands_use_the_original_signed_boundaries(self):
        for score in (-256,-255,-11,-10,-8,-7,-6,-5):
            r,parent=self.frame(winner=1)
            r.run('000E:11D9',[parent],responder({'1771:5C60':2,'000E:0B77':score&65535,'214B:06B1':1}))
            self.assertEqual(len(r.args('000E:0B77')),1)
            self.assertEqual(len(r.args('000E:062F')),1)
            self.assertEqual(bool(r.args('214B:06B1')),score in (-256,-5))
