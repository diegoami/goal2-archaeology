"""T124e: actual stage-news calls, cursor lifetime and ordered page history."""
from tests.test_port_stages import _Calls, RET
from original_match import port
from original_match.port import Registry, stages as ST

RET.update({'000E:5DAF':'000E:5FA0','000E:5E6C':'000E:6199','000E:60CB':'000E:7152'})


def specs(variant=None,news_helpers=True):
    wanted={'000E:5DAF','000E:5E6C','000E:60CB','0791:DAF8','1771:55FC','1771:0947','1771:10E7','1771:5A38','1771:59D8','214B:06B1','214B:0018','214B:003C','214B:007B','23E4:025D',
            '23E4:0644','23E4:062A','23E4:06B7','23E4:075A'}
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for a,e in reg.entries.items():
            if a in wanted or (news_helpers and reg.name in ('news','route')):
                assert not e.stub;sub._add(e)
        if sub.entries:
            sub.variants=dict(reg.variants);result.append((sub,variant if reg.name=='stages' else None))
    return result


def manager_country(m):return m.read(m.far(ST.MANAGERS)+3*129,1)[0]


def parent_frame(m,rating=24,sacked=False):
    from original_match.match import SS_PARAGRAPH
    ss=m.seg(SS_PARAGRAPH)*16;parent=0x3F00
    m.write(ss+parent+6,manager_country(m).to_bytes(2,'little'))
    m.write(ss+parent-0x21,rating.to_bytes(2,'little'))
    if sacked:m.write(m.far(ST.GAME)+0x47+1,b'\1')


class StageNews(_Calls):
    def test_tour_helper_true_original_near_abi_and_no_duplicate_assistant_owner(self):
        self.assertEqual(ST.PORTS.entries['000E:5DAF'].ret,'ret 2')
        self.assertNotIn('0791:DAF8',ST.PORTS.entries)
        self.assertNotIn('1771:55FC',ST.PORTS.entries)
        m,p=self.call('000E:5DAF',(0x3F00,),specs=specs(),before=parent_frame)
        self.proved(p,'000E:5DAF')

    def test_failure_headline_keeps_manager_ownership_and_visits_tour_when_sacked(self):
        saved={}
        def before(m):
            parent_frame(m,sacked=True)
            saved['country']=manager_country(m);saved['tag']=m.read(m.far(ST.COUNTRIES)+191*saved['country']+46,1)
            m.wr(0x9B43,0x1234)
        m,p=self.call('000E:5E6C',(0x3F00,),specs=specs(),before=before)
        self.proved(p,'000E:5E6C')
        self.assertEqual(p.summary()['000E:5DAF']['nested'],1)
        self.assertEqual(m.read(m.far(ST.COUNTRIES)+191*saved['country']+46,1),saved['tag'])
        self.assertEqual(m.rd(0x9B43),0x1234)


def world_image():
    # Reuse D's validated original constructor/finalizer recipe. CI missing its
    # private captures uses its real E006/original6970+8757 fallback, never skips.
    from tests.test_port_stage_world import get_inputs
    return get_inputs()[1]['groups']


def group_members(m):
    t=m.far(ST.TABLES)
    return {m.word_at(t+0x14C8+g*0x38+8*s):g for g in range(1,9) for s in range(4)}


def managers(m,countries,groups=None):
    g=m.far(ST.GAME);cp=m.far(ST.COUNTRIES);mp=m.far(ST.MANAGERS)
    for index in range(1,m.read(g,1)[0]+1):
        old=m.read(mp+3*(128+index),1)[0]
        if old:m.write(cp+191*old+46,bytes([old]))
    members=group_members(m) if groups is None else groups
    m.write(g,bytes([len(countries),len(countries)]))
    for index,country in enumerate(countries,1):
        m.write(cp+191*country+46,bytes([128+index]));m.write(mp+3*(128+index),bytes([country]))
        m.write(g+1+index,bytes([members.get(country,0)]))
        m.write(g+0x47+index,b'\0')
        # Give manager2 the same actual original name representation as manager1.
        if index>1:
            a=m.far(0x9B78);b=m.far(0x9B74)
            m.write(a+128+index,m.read(a+129,1));m.write(b+13*(128+index),m.read(b+13*129,13))
    return countries


def announce(image,countries,*,variant=None,capture=True,setup=None,helper_variant=None):
    from original_match import route as R
    from original_match.match import SS_PARAGRAPH
    from original_match.port.prove import Prover
    r=R.Route(image,record_writes=False,capture_news=capture);m=r.m
    managers(m,countries)
    if setup:setup(m)
    contexts=[];r.comparison_sites=[]
    def comparison(replay):
        if replay or m.muted:return
        site=f'000E:{m.stack_word(0):04X}'
        if site in ('000E:64C1','000E:6500','000E:651E'):r.comparison_sites.append(site)
    m.at('000E:062F',comparison)
    def entry(replay):
        if replay or m.muted:return
        s=m.reg('ss')*16+m.reg('sp')
        if m.word_at(s)!=0x6625:return
        country=m.frame_word(m.reg('bp'),6);g=m.far(ST.GAME)
        contexts.append((country,m.read(g+1,1)[0],m.read(m.far(ST.COUNTRIES)+191*country+46,1)[0],m.rd(0x9B43)))
    if capture:m.at('000E:05F6',entry)
    chosen=specs(variant)
    if helper_variant:chosen=[(reg,helper_variant if reg.name=='assistant' else v) for reg,v in chosen]
    inst=port.install(m,chosen);p=Prover(m,inst)
    m.at('000E:7152',lambda replay:m.stop('announcement-return'))
    for country in countries:
        ss=m.seg(SS_PARAGRAPH);sp=0x3EDC
        for i,w in enumerate((0x7152,m.seg(0xE),country)):m.write(ss*16+sp+2*i,w.to_bytes(2,'little'))
        for n,v in (('ss',ss),('sp',sp),('bp',0x3EEA),('ds',m.DS),('es',m.DS),('cs',m.seg(0xE)),('eip',0x60CB)):m.set_reg(n,v)
        assert m.run(m.lin('000E:7152')+1,120,fresh=True)=='announcement-return'
        assert m.reg('sp')==sp+6
    return r,p,contexts


def host_country(image):
    from original_match.machine import Machine
    m=Machine(image.memory,image.load)
    return m.word_at(m.far(ST.GAME)+0x36)


def tour_country(image):
    from original_match.machine import Machine
    m=Machine(image.memory,image.load);members=group_members(m);g=m.far(ST.GAME);fx=m.far(ST.FIXTURES);cp=m.far(ST.COUNTRIES)
    for n in range(m.word_at(g+0x26),m.word_at(g+0x28)):
        a=fx+8*(n-1);home=m.word_at(a+4);away=m.word_at(a+6)
        if m.read(a+2,1)[0]==1 and home in members and m.read(cp+191*home+44,1)!=m.read(cp+191*away+44,1):return home
    raise AssertionError('original world calendar has no cross-continent friendly for a qualified country')


class StageNewsControl(_Calls):
    def test_two_actual_pages_keep_each_selected_manager_then_restore_cursor(self):
        from original_match.machine import Machine
        image=world_image();m=Machine(image.memory,image.load);countries=list(group_members(m))[:2]
        r,p,contexts=announce(image,countries)
        self.assertEqual(p.summary()['000E:60CB']['proved'],2)
        self.assertEqual([x[:3] for x in contexts],[(countries[0],1,129),(countries[1],2,130)])
        self.assertEqual(len(r.news_history),2);self.assertEqual(len(r.news_pages),2)
        self.assertEqual(r.m.read(r.m.far(ST.GAME)+1,1)[0],2)
        self.assertNotEqual(r.news_history[0].cells,r.news_history[1].cells)

    def test_host_announcement_uses_actual_original_draw_host_and_group(self):
        image=world_image();country=host_country(image)
        r,p,contexts=announce(image,[country])
        self.assertEqual(p.summary()['000E:60CB']['proved'],1)
        self.assertEqual(contexts[0][:3],(country,1,129))
        self.assertTrue(any('IS TO HOST' in line for line in r.news_pages[0]))

    def test_failed_group_still_calls_tour_and_preserves_ownership(self):
        image=world_image();country=tour_country(image)
        def failure(m):m.write(m.far(ST.GAME)+2,b'\0')
        r,p,contexts=announce(image,[country],setup=failure)
        self.assertEqual(p.summary()['000E:5E6C']['nested'],1)
        self.assertEqual(p.summary()['000E:5DAF']['nested'],1)
        self.assertGreater(contexts[0][3],0)
        self.assertTrue(any('TO TOUR' in line for line in r.news_pages[0]))
        self.assertEqual(r.m.read(r.m.far(ST.COUNTRIES)+191*country+46,1)[0],129)
        self.assertTrue(any('FAIL TO QUALIFY FOR' in line for line in r.news_pages[0]))

    def test_observer_on_off_preserves_full_state_keys_draws_and_records(self):
        from original_match.machine import MEM_SIZE,REGS
        image=world_image();country=tour_country(image)
        def pushed(m):
            from original_match import route as R
            m.wr(R.PUSHED_BACK,1,1);m.wr(R.KEY,0x50,1)
        a,pa,_=announce(image,[country],setup=pushed)
        b,pb,_=announce(image,[country],capture=False,setup=pushed)
        self.assertEqual(pa.summary()['000E:60CB']['proved'],1)
        self.assertEqual(pb.summary()['000E:60CB']['proved'],1)
        self.assertEqual(a.m.read(0,MEM_SIZE),b.m.read(0,MEM_SIZE))
        self.assertEqual([a.m.reg(n) for n in REGS],[b.m.reg(n) for n in REGS])
        self.assertEqual(a.record,b.record);self.assertEqual(a.keys.waiting,b.keys.waiting)
        self.assertEqual(len(a.news_history),1);self.assertEqual(b.news_history,[])

    def test_news_draw_and_cursor_restoration_falsifiers_are_caught(self):
        from original_match.port.prove import ProofError
        image=world_image();country=tour_country(image)
        def failure(m):m.write(m.far(ST.GAME)+2,b'\0')
        with self.assertRaises(ProofError):announce(image,[country],variant='stage-news-draw-dropped',setup=failure)
        from original_match.machine import Machine
        m=Machine(image.memory,image.load);countries=list(group_members(m))[:2]
        with self.assertRaises(ProofError):announce(image,countries,variant='stage-news-cursor-not-restored')

    def test_all_three_rating_comparisons_use_actual_unmodified_country_ranks(self):
        from original_match.machine import Machine
        image=world_image();m=Machine(image.memory,image.load);cp=m.far(ST.COUNTRIES);groups=group_members(m)
        # Input selection from original10E7's established rank/continent formula;
        # no rank, country, score, fixture or result byte is rewritten.
        ratings={c:((33-m.read(cp+191*c+42,1)[0])*(5-m.read(cp+191*c+44,1)[0])+129-m.read(cp+191*c+43,1)[0])//2 for c in groups}
        selected={};host=host_country(image)
        for c,g in groups.items():
            if c==host:continue
            total=sum(ratings[p] for p,pg in groups.items() if pg==g and p!=c)
            site='000E:64C1' if total<2*ratings[c] else ('000E:6500' if total<3*ratings[c] else '000E:651E')
            selected.setdefault(site,c)
        self.assertEqual(set(selected),{'000E:64C1','000E:6500','000E:651E'})
        for site,country in selected.items():
            with self.subTest(return_pc=site):
                r,p,_=announce(image,[country]);self.assertEqual(p.summary()['000E:60CB']['proved'],1)
                self.assertEqual(r.comparison_sites,[site])

    def test_tour_next_fixture_write_falsifier_is_caught_in_announcements(self):
        from original_match.port.prove import ProofError
        image=world_image();country=tour_country(image)
        def stale(m):m.wr(0x9B43,0)
        with self.assertRaises(ProofError):announce(image,[country],setup=stale,helper_variant='next-write-omitted')


class TourEffects(_Calls):
    def test_no_next_fixture_false_still_clears_previous_word(self):
        def before(m):
            parent_frame(m);country=manager_country(m)
            m.write(m.far(ST.LISTS)+0x48*country,b'\0'*0x48);m.wr(0x9B43,0x1234)
        m,p=self.call('000E:5DAF',(0x3F00,),specs=specs(),before=before)
        self.proved(p,'000E:5DAF');self.assertEqual(m.reg('ax')&255,0);self.assertEqual(m.rd(0x9B43),0)

    def test_competitive_next_fixture_false_still_updates_previous_word(self):
        from tests.test_port_stage_world import get_inputs
        old=self.image;self.image=get_inputs()[1]['last16']
        try:
            def before(m):
                first=m.word_at(m.far(ST.GAME)+0x26);country=m.word_at(m.far(ST.FIXTURES)+8*(first-1)+4)
                managers(m,[country]);parent_frame(m);m.wr(0x9B43,0x1234)
            m,p=self.call('000E:5DAF',(0x3F00,),specs=specs(),before=before)
        finally:self.image=old
        self.proved(p,'000E:5DAF');self.assertEqual(m.reg('ax')&255,0)
        next_fixture=m.rd(0x9B43);self.assertGreater(next_fixture,0)
        self.assertEqual(m.read(m.far(ST.FIXTURES)+8*(next_fixture-1)+2,1)[0],8)

    def test_side_b_friendly_false_preserves_real_next_fixture_write_in_failure_page(self):
        from original_match.machine import Machine
        image=world_image();m=Machine(image.memory,image.load);n=m.word_at(m.far(ST.GAME)+0x26)
        fx=m.far(ST.FIXTURES)+8*(n-1);country=m.word_at(fx+6)
        self.assertEqual(m.read(fx+2,1)[0],1)
        def failure(m):m.write(m.far(ST.GAME)+2,b'\0');m.wr(0x9B43,0x1234)
        r,p,contexts=announce(image,[country],setup=failure)
        self.assertEqual(p.summary()['000E:5DAF']['nested'],1)
        self.assertEqual(contexts[0][3],n)
        self.assertFalse(any('TO TOUR' in line for line in r.news_pages[0]))


def stage_news_falsifier_input(m,variant):
    """Only the two new old-map cases receive these declared complete frames."""
    if variant=='stage-news-draw-dropped':parent_frame(m,sacked=True);return
    assert variant=='stage-news-cursor-not-restored'
    from tests.test_port_stage_world import get_inputs
    from original_match import route as R
    from original_match.machine import MEM_SIZE
    image=get_inputs(m.load)[1]['groups'];m.write(0,bytes(image.memory[:MEM_SIZE]))
    second=next(c for c in group_members(m) if c!=7);managers(m,[7,second])
    # The real Route key service preempts BIOS key routines, exactly as in the
    # primary harness. Keep this Route alive through its bound entry handlers.
    r=R.Route(image,record_writes=False,capture_news=False);r.m=m
    m.at(R.KEYPRESSED,r._on_poll);m.at(R.READKEY,r._on_read)


class CIMissingPrivateInputs(_Calls):
    def test_actual_stage_news_oracles_run_with_receipt_present_and_private_inputs_absent(self):
        import unittest
        from pathlib import Path
        from unittest.mock import patch
        from tests import test_port_stage_world as W
        saved=dict(W._CACHES);original=Path.read_bytes;reads=[]
        def missing(path):
            if '/.cache/t124d/natural/' in path.as_posix():
                reads.append(str(path));raise FileNotFoundError('CI ignored private input absent')
            return original(path)
        W._CACHES.clear()
        try:
            with patch.object(Path,'read_bytes',missing):
                suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c) for c in (StageNews,StageNewsControl,TourEffects))
                result=unittest.TestResult();suite.run(result)
                self.assertEqual(result.testsRun,12);self.assertEqual(result.skipped,[])
                self.assertTrue(result.wasSuccessful(),str(result.errors)+str(result.failures))
                self.assertTrue(reads);self.assertIn('original6970+actual8757',W.get_inputs()[2])
        finally:W._CACHES.clear();W._CACHES.update(saved)
