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
                         '2E1F':'ret 0xe', '3A5E':'ret 6', '4045':'ret 0xa', '47E6':'ret 0xa', '11D9':'ret 2', '2071':'ret 2', '26F2':'ret 2', '319B':'ret 2', '01FA':'ret 2', '4DB7':'ret 2', '4E0E':'ret 6'})
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

    def test_original_backed_result_families(self):
        port._module_registry('news').entries['000E:11D9']
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'experiments/E040-route-fixture-writes/out/T122b/prove_column.py'
        spec=importlib.util.spec_from_file_location('t122b_column_proof',path);module=importlib.util.module_from_spec(spec)
        try:spec.loader.exec_module(module)
        except ImportError as exc:
            if exc.name=='unicorn':self.skipTest('unicorn missing')
            raise
        state=next(c for c in module.runner.CASES if c[0]=='E040-r0004');asset=module.ROOT/'.cache/dl'/state[3]
        if not asset.is_file():self.skipTest('published E040 state missing; runner.py --fetch')
        import hashlib
        data=asset.read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),module.runner.expected(state[3]))
        names={'special-0-203-win','special-0-203-loss','ordinary-0-win-1-balanced-0','ordinary-0-draw-0-strong-6',
               'ordinary-1-loss-3-weak-11','sack-1--6-4','red-0-win-1','confidence-1-q-minus-2-1-0',
               'confidence-0-q-minus-3-1-6','confidence-0-q-minus-3-3-7'}
        chosen=[c for c in module.cases() if c[0] in names];self.assertEqual(len(chosen),len(names))
        for case in chosen:
            with self.subTest(case=case[0]):
                result=module.prove(data,case)
                self.assertEqual(result['status'],'completed',result['error'])
                self.assertEqual(result['proof']['000E:11D9']['proved'],1)
                self.assertEqual(result['proof']['000E:11D9']['before'],0)


    def test_actual_finals_gate_preserves_nonzero_confidence_unless_exempt(self):
        port._module_registry('news').entries['000E:11D9']
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'experiments/E040-route-fixture-writes/out/T122b/prove_column.py'
        spec=importlib.util.spec_from_file_location('t122b_real_gate_proof',path);module=importlib.util.module_from_spec(spec)
        try:spec.loader.exec_module(module)
        except ImportError as exc:
            if exc.name=='unicorn':self.skipTest('unicorn missing')
            raise
        state=next(c for c in module.runner.CASES if c[0]=='E040-r0004');asset=module.ROOT/'.cache/dl'/state[3]
        if not asset.is_file():self.skipTest('published E040 state missing; runner.py --fetch')
        import hashlib
        data=asset.read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),module.runner.expected(state[3]))
        chosen=[c for c in module.cases() if c[0].startswith('finals-')];self.assertEqual(len(chosen),24)
        for case in chosen:
            with self.subTest(case=case[0]):
                result=module.prove(data,case)
                self.assertEqual(result['status'],'completed',result['error'])
                self.assertEqual(result['proof'][case[1]]['proved'],1)
                gate=result['gate_check'];self.assertIsNotNone(gate)
                self.assertEqual(gate['observed_59D8'],[gate['expected_59D8']])
                self.assertEqual(gate['observed_0B77'],[gate['expected_0B77']])


class SecondaryText(Case):
    def recommendation_frame(self):
        r=Rig();wrapper=0x2800;parent=0x2900
        r.lin16(wrapper+4,parent);r.lin16(parent+8,3);r.country(3,0x2E,0x81)
        return r,wrapper,parent

    def column_frame(self,winner=0):
        r,parent,_=self.recommendation_frame();r.lin16(parent+4,FXOFF);r.lin16(parent+6,FXSEG)
        r.lin16(parent+8,3);r.lin8(parent-1,0);r.fixture(2,3,4);r.lin8(FXSEG*16+FXOFF+3,winner)
        return r,parent

    def test_both_original_near_returns(self):
        reg=port._module_registry('news')
        for a in ('000E:2071','000E:26F2'):
            self.assertEqual(reg.entries[a].ret,'ret 2');self.assertFalse(reg.entries[a].far)

    def test_role_draw_and_global_write_precede_the_manager_gate(self):
        r,parent,_=self.recommendation_frame();r.lin8(GAME+0x14,1)
        result=r.run('000E:2071',[parent],responder({'214B:06B1':8}))
        self.assertEqual(result & 255,0);self.assertEqual(r.mem.ds8(0x22),7)
        self.assertEqual(r.args('214B:06B1'),[(14,)])
        self.assertEqual(r.args('1771:3216'),[]);self.assertEqual(r.args('1771:377E'),[])

    def test_no_matching_role_still_visits_all_twenty_squad_slots(self):
        r,parent,_=self.recommendation_frame();r.squad(3,list(range(100,120)))
        for word in range(100,120):r.player(word,6,1)
        result=r.run('000E:2071',[parent],responder({'214B:06B1':1}))
        self.assertEqual(result & 255,0);self.assertEqual(r.u16(0x2FFE-5),20)
        self.assertEqual(r.args('1771:3216'),[]);self.assertEqual(r.args('1771:377E'),[])

    def test_unavailable_squad_players_are_not_strength_candidates(self):
        r,parent,_=self.recommendation_frame();r.squad(3,list(range(100,120)))
        result=r.run('000E:2071',[parent],responder({'214B:06B1':1,'1771:3216':1}))
        self.assertEqual(result & 255,0);self.assertEqual(len(r.args('1771:3216')),20)
        self.assertEqual(r.args('1771:377E'),[])

    def pool_frame(self):
        r,parent,_=self.recommendation_frame();r.squad(3,list(range(100,120)))
        r.ds16(0x6D18+2,5);r.ds16(0xA927,0x100);r.ds16(0xA929,0x5200)
        for index,word in enumerate(range(300,380),5):r.lin16(0x52100+2*index,word)
        for word in range(100,120):r.player(word,6,0)
        for word in range(300,380):r.player(word,7,0)
        return r,parent

    def test_strict_ties_keep_first_and_both_loops_keep_original_call_counts(self):
        r,parent=self.pool_frame()
        def strength(req,mem):
            w=req.args[0]
            if w in (100,101):return 10
            if w in (300,301):return 30
            return 20
        result=r.run('000E:2071',[parent],responder({'214B:06B1':[1,1],'1771:3216':0,'1771:377E':strength}))
        self.assertEqual(result & 255,1)
        self.assertEqual(len(r.args('1771:3216')),20)
        self.assertEqual(len(r.args('1771:377E')),103)
        self.assertEqual(r.args('214B:06B1'),[(14,),(10,)])
        self.assertEqual(r.args('1771:2E93'),[(300,)])
        self.assertEqual(len(r.args('000E:075F')),1)
        self.assertEqual(r.u16(0x2FFE-7),100);self.assertEqual(r.u16(0x2FFE-9),300)

    def test_no_improvement_has_no_second_draw_or_text(self):
        r,parent=self.pool_frame()
        result=r.run('000E:2071',[parent],responder({'214B:06B1':1,'1771:3216':0,'1771:377E':10}))
        self.assertEqual(result & 255,0);self.assertEqual(r.args('214B:06B1'),[(14,)])
        self.assertEqual(r.args('000E:075F'),[])
        self.assertEqual(len(r.args('1771:377E')),102)
        self.assertTrue(all((word,) in r.args('1771:377E') for word in range(300,380)))

    def test_winning_streak_draw_and_severe_sack_bypass_have_original_order(self):
        r,parent=self.column_frame();r.country(3,0xAC,1)
        r.run('000E:26F2',[parent],responder({'000E:2071':0,'214B:06B1':1}))
        self.assertEqual(r.args('000E:2071'),[(0x2FFE,)])
        self.assertEqual(r.args('214B:06B1'),[(4,)])
        self.assertEqual(len(r.args('000E:075F')),1)
        r,parent=self.column_frame(winner=1)
        r.run('000E:26F2',[parent],responder({'000E:0B77':0xFFF5}))
        self.assertEqual(r.args('000E:2071'),[])
        self.assertEqual(r.args('214B:06B1'),[])
        self.assertEqual(len(r.args('000E:075F')),1)

    def test_original_backed_loop_and_column_frames(self):
        port._module_registry('news').entries['000E:2071']
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'experiments/E040-route-fixture-writes/out/T122c/prove_secondary.py'
        spec=importlib.util.spec_from_file_location('t122c_secondary_proof',path);module=importlib.util.module_from_spec(spec)
        try:spec.loader.exec_module(module)
        except ImportError as exc:
            if exc.name=='unicorn':self.skipTest('unicorn missing')
            raise
        state=next(c for c in module.runner.CASES if c[0]=='E040-r0004');asset=module.ROOT/'.cache/dl'/state[3]
        if not asset.is_file():self.skipTest('published E040 state missing; runner.py --fetch')
        import hashlib
        data=asset.read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),module.runner.expected(state[3]))
        names={'pool-2071-0-ties','pool-2071-1-pool-unavailable','pool-2071-0-wrap','pool-2071-0-pool-first-unavailable',
               'pool-26F2-0-ties','column-streak-1-1-4','column-sack-0--11','recommend-text-2071-0-10'}
        chosen=[c for c in module.cases() if c[0] in names];self.assertEqual(len(chosen),len(names))
        for case in chosen:
            with self.subTest(case=case[0]):
                result=module.prove(data,case)
                self.assertEqual(result['status'],'completed',result['error'])
                self.assertEqual(result['proof'][case[1]]['proved'],1)
                self.assertEqual(result['proof'][case[1]]['before'],0)


class HeadlineSack(Case):
    def headline_frame(self,score=-11,goals=(0,1),kind=2,side=0):
        r=Rig();news=0x2800;pages=0x2900;country=3 if side==0 else 4
        r.lin16(pages+4,news);r.lin16(news+4,FXOFF);r.lin16(news+6,FXSEG);r.lin16(news+8,country)
        r.lin8(news-1,side);r.lin8(news-2,0);r.lin16(news-6,1);r.lin8(news-0x1b+1,1)
        r.fixture(kind,3,4);r.lin8(FXSEG*16+FXOFF,goals[0]);r.lin8(FXSEG*16+FXOFF+1,goals[1]);r.lin8(FXSEG*16+FXOFF+3,1-side)
        return r,pages,news

    def test_four_exact_original_returns(self):
        reg=port._module_registry('news')
        for a,ret in (('319B','ret 2'),('01FA','ret 2'),('4DB7','ret 2'),('4E0E','ret 6')):
            self.assertEqual(reg.entries['000E:'+a].ret,ret)

    def test_actual_signed_bands_and_injected_lower_bound_are_preserved(self):
        # -255/-256 are explicit returned-value stress, not signed-byte manager states.
        for score in (-256,-255,-128,-11,-10,-8,-7,-6,-5):
            r,pages,news=self.headline_frame()
            r.run('000E:319B',[pages],responder({'000E:0B77':score&65535,'1771:5C60':1,'214B:06B1':1}))
            self.assertEqual(r.mem.memory[news-2],int(-255<=score<=-11),score)
            self.assertEqual(len(r.args('000E:0B77')),1)
            self.assertEqual(len(r.args('000E:2E1F')),1)

    def test_equal_goal_shootout_bypasses_sack_score(self):
        r,pages,news=self.headline_frame(goals=(1,1),kind=0x66)
        r.run('000E:319B',[pages],responder({'000E:0B77':0xfff5,'214B:06B1':1}))
        self.assertEqual(r.args('000E:0B77'),[]);self.assertEqual(r.mem.memory[news-2],0)
        self.assertIn(0x306E,r.args('000E:2E1F')[0]);self.assertIn(0x3080,r.args('000E:2E1F')[0])

    def test_statistics_dispatch_order_and_rows(self):
        for first,second,want,row in ((0,0,['319B','3CC8','4440','4A87'],6),(1,0,['319B','3CC8','4A87','4440'],10),(1,1,['319B','3CC8','4A87'],None)):
            r=Rig();r.run('000E:4DB7',[0x2800],responder({'000E:3CC8':first,'000E:4A87':second}))
            self.assertEqual([a.split(':')[1] for a,_ in r.targets()],want)
            self.assertEqual(r.args('000E:4440'),[(row,0x2FFE)] if row else [])

    def outer(self,goals,slots=(),side=0,sack=False):
        r=Rig();country=3 if side==0 else 4;r.fixture(0x67,3,4)
        fx=FXSEG*16+FXOFF;r.lin8(fx,goals[0]);r.lin8(fx+1,goals[1]);r.lin8(fx+3,side)
        r.country(country,0x2E,0x81);pending=list(slots);members=iter((0xC0DE,0xD0AD))
        def answer(req,mem):
            if req.target=='214B:0018':
                seg,off,count,value=req.args;mem.memory[seg*16+off:seg*16+off+count]=bytes([value&255])*count
            if req.target=='1771:3A82':return pending.pop(0)
            if req.target=='000E:4DB7' and sack:r.lin8(req.args[0]-2,1)
            if req.target=='000E:26F2':return 0xABCD
            if req.target=='23E4:08DF':mem.regs['eflags']=0;return next(members)
            return 0
        r.run('000E:4E0E',[FXOFF,FXSEG,country],answer)
        return r

    def test_goal_histogram_zero_and_first_strict_maximum(self):
        r=self.outer((0,1));self.assertEqual(r.u16(0x2FFE-6),0);self.assertEqual(r.args('1771:3A82'),[])
        r=self.outer((4,0),slots=(2,4,2,4));self.assertEqual(r.u16(0x2FFE-6),2)
        self.assertEqual(r.mem.memory[0x2FFE-0x1b+2],2);self.assertEqual(r.mem.memory[0x2FFE-0x1b+4],2)
        self.assertEqual(len(r.args('1771:3A82')),4)

    def test_full_flag_words_and_wait_before_unmanage(self):
        r=self.outer((1,0),slots=(1,),sack=True)
        self.assertEqual(r.args('000E:05F6'),[(0xAB00,0xC001,0xD001)])
        order=[a for a,_ in r.targets()];self.assertLess(order.index('000E:05F6'),order.index('000E:01FA'))
        self.assertEqual(r.args('000E:01FA'),[(1,)])

    def unmanage_frame(self,prefix=1):
        r=Rig();r.ds16(0xA91F,0x100);r.ds16(0xA921,0x5100);manager=0x51100+3*0x81
        r.lin8(manager,3);r.country(3,0x2E,0x81);r.squad(3,list(range(100,120)))
        for i,w in enumerate(range(100,120)):r.player(w,6,0x20);r.player(w,7,i%14)
        r.ds16(0xA927,0x100);r.ds16(0xA929,0x5200);r.ds16(0x6D18+2,1)
        for i,w in enumerate(range(300,380),1):r.lin16(0x52100+2*i,w);r.player(w,0,3)
        r.ds16(0xA92F,0x100);r.ds16(0xA931,0x5400);listing=0x54100+3*0x48
        for slot in range(21,37):r.lin16(listing+2*(slot-1),0 if slot<21+prefix else 1)
        if prefix>=16:r.lin16(listing+2*36,1)
        r.lin8(0x50008,0xFE)
        return r,manager

    def test_unmanage_flags_precede_real_reset_and_roster_is_read_after_reset(self):
        r,manager=self.unmanage_frame();seen=[]
        def reset(req,mem):
            if req.target=='0791:BC5D':
                self.assertEqual(r.mem.memory[GAME+0x48],1);self.assertEqual(r.mem.memory[manager+1],1)
                from test_port_update import SQSEG,SQOFF
                base=SQSEG*16+SQOFF+3*0xBF
                self.assertEqual(r.mem.memory[base+0x2E],0x81)
                words=list(range(100,120));words[0],words[11]=words[11],words[0];r.squad(3,words);r.player(111,6,3);seen.extend(words[11:])
            return 0
        r.run('000E:01FA',[1],reset)
        self.assertEqual(len(seen),9)
        from test_port_update import PSEG,POFF,SQSEG,SQOFF
        for word in seen:self.assertEqual(r.mem.memory[PSEG*16+POFF+20*word+6],r.mem.memory[PSEG*16+POFF+20*word+7])
        self.assertEqual(r.mem.memory[PSEG*16+POFF+20*111+6],3)
        self.assertTrue(all(r.mem.memory[PSEG*16+POFF+20*w]==0 for w in range(300,380)))
        self.assertEqual(r.mem.memory[SQSEG*16+SQOFF+3*0xBF+0x2E],3);self.assertEqual(r.mem.memory[0x50008],0xFF)

    def test_zero_prefix_scan_reaches_real_nonzero_sentinel_beyond_36(self):
        r,_=self.unmanage_frame(prefix=16);r.run('000E:01FA',[1])
        self.assertEqual(r.u16(0x2FFE-2),37);self.assertEqual(r.mem.memory[0x50008],0xFE)

    def test_original_backed_sack_release_both_sides_and_real_route_continuation(self):
        port._module_registry('news').entries['000E:4E0E']
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'experiments/E040-route-fixture-writes/out/T122d/prove_headlines.py'
        spec=importlib.util.spec_from_file_location('t122d_actual_sack',path);module=importlib.util.module_from_spec(spec)
        try:spec.loader.exec_module(module)
        except ImportError as exc:
            if exc.name=='unicorn':self.skipTest('unicorn missing')
            raise
        state=next(c for c in module.runner.CASES if c[0]=='E040-r0004');asset=module.ROOT/'.cache/dl'/state[3]
        if not asset.is_file():self.skipTest('published E040 state missing; runner.py --fetch')
        import hashlib
        data=asset.read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),module.runner.expected(state[3]))
        names={'band-0--11','band-1--10','outer-band-0--11','outer-band-1--11','outer-exempt-0-continent-group',
               'outer-shootout-1','unmanage-1-16-0','unmanage-2-2-1','route-fragment-0','route-fragment-1'}
        selected=[c for c in module.cases() if c[0] in names];self.assertEqual(len(selected),len(names))
        for case in selected:
            with self.subTest(case=case[0]):
                result=module.prove(data,case)
                self.assertEqual(result['status'],'completed',result['error'])
                for address,n in result['calls'].items():
                    self.assertEqual(result['proof'][address]['proved']+result['proof'][address]['nested'],n)
                    self.assertEqual(result['proof'][address]['before'],0)
                if case[1]=='route-fragment':
                    self.assertEqual(len(result['checks']['news_order']),2)
                    self.assertEqual(result['checks']['wait_order'],result['checks']['news_order'])
                    self.assertEqual(result['checks']['released'],result['checks']['news_order'][:1])
