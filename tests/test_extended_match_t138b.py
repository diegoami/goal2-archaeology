"""[designed: T138b/#727] Opt-in full match-day bench; original20 unchanged."""
import copy,sys,unittest
from pathlib import Path
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'runtime'),str(Path(__file__).resolve().parents[1]/'tools')]
from original_match.match import Match,Fixture,PLAYER_POSITION
from original_match.machine import MEM_SIZE,REGS
from tests.test_route_sealed import _fixtures
from tests.test_route_entry_config import snapshot


class Config(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.context,cls.fixture=_fixtures().entry()

    def match(self):return Match.from_route_entry(self.image,Fixture(**self.fixture),self.context)

    def test_defaults_and_invalid_extras_preserve_the_entry(self):
        normal=self.match();before=snapshot(normal);normal.configure_route_entry();self.assertEqual(snapshot(normal),before)
        pool=self.match()._pool();core=self.match()._squad(self.fixture['first'])
        bad=(False,'yes',[True],[0],[3061],[pool[0],pool[0]],pool[:5],[core[0]],[next(w for w in range(1,3061) if w not in core+pool)])
        for extra in bad:
            with self.subTest(extra=extra):
                m=self.match();before=snapshot(m)
                self.assertRaises(ValueError,m.configure_route_entry,extra_players=extra)
                self.assertEqual(snapshot(m),before)
                m.configure_route_entry()

    def test_valid_22_and_24_options_are_detached_without_entry_execution(self):
        for count in (2,4):
            m=self.match();before=snapshot(m);extra=m._pool()[:count]
            m.configure_route_entry(extra_players=extra)
            self.assertEqual(snapshot(m)[:2],before[:2])
            self.assertEqual(len(m._selected_squad()),20+count)
            extra[0]=0;self.assertNotIn(0,m.opts['extra_players'])


def _decision(stream):
    for event in stream:
        if event.kind=='decision':return event.data
    raise AssertionError('decision missing')


def actual_entry(value,tables_record,fixture,context,count):
    assert sys.implementation.name=='pypy'
    from original_match.image import Image
    from original_match.port.tables import from_record
    from tests.test_route_sealed import _denials
    _denials()
    image=Image.from_state(value,from_record(tables_record))
    m=Match.from_route_entry(image,Fixture(**fixture),context)
    core=m._squad(m.opts['managed']);pool=m._pool()
    off,on=next((a,b) for a in core[1:11] for b in pool if m._available(a) and m._available(b) and m._player(a,6)==m._player(b,6))
    extras=[on]+[w for w in pool if w!=on and m._available(w)][:count-1]
    original=set(core+extras);before=m.m.read(0,MEM_SIZE);registers=tuple(m.m.reg(r) for r in REGS)
    m.configure_route_entry(extra_players=extras,pre_match_edits=True,live_players=True,substitutions=5)
    assert m.m.read(0,MEM_SIZE)==before and tuple(m.m.reg(r) for r in REGS)==registers
    stream=iter(m.events());first=_decision(stream)
    assert len(first['bench'])==9+count and set(first['eleven']+first['bench'])==original
    assert len(first['player_records'])==20+count
    m.answer(edit_only=True,substitutions=[(off,on)])
    edited=_decision(stream)
    assert on in edited['eleven'] and off not in edited['eleven']
    assert len(edited['bench'])==9+count and set(edited['national_squad'])==original
    assert len([x for x in m.inputs if x['what'].startswith('extended selected bench input')])==2
    raw=m.save();loaded=Match.load(raw)
    assert loaded.waiting==m.waiting
    assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
    assert tuple(loaded.m.reg(r) for r in REGS)==tuple(m.m.reg(r) for r in REGS)
    assert loaded.st['national_roster']==m.st['national_roster']
    m.answer();next_event=next(stream)
    return dict(capacity=20+count,bench=len(edited['bench']),same_machine=True,save_equal=True,next_kind=next_event.kind)


class Native(unittest.TestCase):
    def test_actual_22_and_24_prematch_extra_entry_and_save(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image,context,fixture=_fixtures().entry()
        for count in (2,4):
            with self.subTest(count=count):
                result=call_in_pypy('test_extended_match_t138b','actual_entry',args=(image.state(image.tables),to_record(image.tables),fixture,context,count),timeout=180)
                self.assertEqual(result['capacity'],20+count)
                self.assertEqual(result['bench'],9+count)
                self.assertTrue(result['save_equal'])


def actual_halftime(value,tables_record,fixture,context,count):
    assert sys.implementation.name=='pypy'
    from original_match.image import Image
    from original_match.port.tables import from_record
    from original_match import screens as S
    from tests.test_route_sealed import _denials
    _denials();image=Image.from_state(value,from_record(tables_record))
    m=Match.from_route_entry(image,Fixture(**fixture),context)
    extra=[w for w in m._pool() if m._available(w) and m._player(w,6)>0][:count]
    members=set(m._squad(m.opts['managed'])+extra)
    m.configure_route_entry(extra_players=extra,pre_match_edits=True,live_players=True,substitutions=5)
    stream=iter(m.events());d=_decision(stream);m.answer(quick=True)
    for event in stream:
        if event.kind=='decision':
            d=event.data
            if d['context']=='half_time':break
            m.answer(quick=True)
    else:raise AssertionError('half-time decision missing')
    assert len(d['bench'])==9+count and set(d['national_squad'])==members
    native=m._squad(m.opts['managed']);on=next(w for w in d['bench'] if w not in native and m._available(w))
    off=next(w for w in reversed(d['eleven']) if m._player(w,6)>0)
    budget=d['substitutions_left'];m.answer(substitutions=[(off,on)],quick=True)
    for event in stream:
        if event.kind=='substitution':break
        if event.kind=='decision':m.answer(quick=True)
    else:raise AssertionError('extra substitution event missing')
    assert on in m._squad(m.opts['managed'])[:11] and off not in m._squad(m.opts['managed'])[:11]
    assert set(m._selected_squad())==members
    assert m.m.rd(S.SUBS_LEFT+m.side,1)==budget-1
    assert not m._available(off)
    loaded=Match.load(m.save())
    assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
    assert tuple(loaded.m.reg(r) for r in REGS)==tuple(m.m.reg(r) for r in REGS)
    assert loaded.st['national_roster']==m.st['national_roster']
    return dict(capacity=20+count,substituted=True,budget=budget-1,withdrawn=True,save_equal=True)


class Substitutions(unittest.TestCase):
    def test_actual_extra_is_eligible_at_half_time_and_original_effects_apply(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image,context,fixture=_fixtures().entry()
        for count in (2,4):
            with self.subTest(count=count):
                result=call_in_pypy('test_extended_match_t138b','actual_halftime',args=(image.state(image.tables),to_record(image.tables),fixture,context,count),timeout=600)
                self.assertTrue(result['substituted']);self.assertTrue(result['withdrawn']);self.assertTrue(result['save_equal'])


def actual_personal(value,tables_record,fixture,context):
    assert sys.implementation.name=='pypy'
    from original_match.image import Image
    from original_match.port.tables import from_record
    from tests.test_route_sealed import _denials
    _denials();m=Match.from_route_entry(Image.from_state(value,from_record(tables_record)),Fixture(**fixture),context)
    extras=[w for w in m._pool() if m._available(w) and m._player(w,6)>=2][:4]
    members=set(m._squad(m.opts['managed'])+extras)
    m.configure_route_entry(extra_players=extras,pre_match_edits=True,live_players=True)
    stream=iter(m.events());d=_decision(stream);word=extras[0];new=(m._player(word,6)+1)%14
    if new<2:new=2
    m.answer(edit_only=True,positions={word:new});d=_decision(stream)
    assert m._player(word,6)==new and set(d['national_squad'])==members
    m.answer(edit_only=True,own_tactics={word:{1:False,2:True,3:None}});d=_decision(stream)
    m.answer(edit_only=True,marking={word:0});d=_decision(stream)
    assert word in d['bench'] and set(d['national_squad'])==members
    assert len(d['player_records'])==24
    return dict(positions=True,own=True,mark=True,card_count=len(d['player_records']))


class Personal(unittest.TestCase):
    def test_actual_additional_bench_player_personal_controls_and_cards(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image,context,fixture=_fixtures().entry()
        result=call_in_pypy('test_extended_match_t138b','actual_personal',args=(image.state(image.tables),to_record(image.tables),fixture,context),timeout=180)
        self.assertEqual(result['card_count'],24)
        self.assertTrue(result['positions'] and result['own'] and result['mark'])


class SavedGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.context,cls.fixture=_fixtures().entry()

    def match(self):return Match.from_route_entry(self.image,Fixture(**self.fixture),self.context)

    def test_malformed_extended_checkpoint_members_reject(self):
        m=self.match();m.configure_route_entry(extra_players=m._pool()[:4])
        state,memory=m._save_state()
        bad=[[],state['st']['national_roster'][:-1],[True]+state['st']['national_roster'][1:],
             state['st']['national_roster'][:-1]+[3061],state['st']['national_roster'][:-1]+[state['st']['national_roster'][0]]]
        for members in bad:
            altered=copy.deepcopy(state);altered['st']['national_roster']=members
            with self.subTest(members=members):self.assertRaises(ValueError,Match.load,Match._encode_save(altered,memory))

    def test_stale_or_invalid_batch_does_not_promote_or_consume(self):
        # Guarding the actual decided context is exercised in the PyPy function below.
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image,context,fixture=self.image,self.context,self.fixture
        self.assertTrue(call_in_pypy('test_extended_match_t138b','actual_batch_guard',args=(image.state(image.tables),to_record(image.tables),fixture,context)))


def actual_batch_guard(value,tables_record,fixture,context):
    assert sys.implementation.name=='pypy'
    from original_match.image import Image
    from original_match.port.tables import from_record
    from tests.test_route_sealed import _denials
    _denials();m=Match.from_route_entry(Image.from_state(value,from_record(tables_record)),Fixture(**fixture),context)
    extras=[w for w in m._pool() if m._available(w)][:4]
    m.configure_route_entry(extra_players=extras,pre_match_edits=True,live_players=True)
    stream=iter(m.events());d=_decision(stream);before=snapshot(m)
    try:m.answer(edit_only=True,substitutions=[(d['eleven'][-1],extras[0]),(0,extras[1])])
    except ValueError:pass
    else:raise AssertionError('invalid later pair accepted')
    assert snapshot(m)==before
    m.answer(edit_only=True,substitutions=[(d['eleven'][-1],extras[0])]);d=_decision(stream)
    assert extras[0] in d['eleven']
    return True


def record_digest(m):
    import hashlib
    blocks={}
    for name,pointer,length in (('players',0xA91B,3061*20),('countries',0xA917,129*191),('managers',0xA91F,135*3),('game',0xA923,0x10E)):
        blocks[name]=hashlib.sha256(m.m.read(m.m.far(pointer),length)).hexdigest()
    blocks.update(core=m._squad(m.opts['managed']),pool=m._pool(),national=m._selected_squad(),seeds=(m.m.rd(0x7B62),m.m.rd(0x8336)))
    return blocks


def normal_reference_drive(m):
    m.opts['pre_match_edits']=True  # Declared test keyboard policy, as T134's original arm.
    stream=iter(m.events());d=_decision(stream);on=m.opts['extra_players'][0]
    off=next(w for w in d['eleven'][1:] if m._player(w,6)==m._player(on,6))
    m.answer(edit_only=True,substitutions=[(off,on)]);edited=_decision(stream)
    assert on in edited['eleven'] and off not in edited['eleven']
    return dict(records=record_digest(m),selection=edited['national_squad'],inputs=m.inputs,
                changed=True,bench=len(edited['bench']))


def port_normal_reference(value,tables_record,fixture,extras):
    assert sys.implementation.name=='pypy'
    from original_match.image import Image
    from original_match.port.tables import from_record
    from tests.test_route_sealed import _denials
    _denials();m=Match(Image.from_state(value,from_record(tables_record)),Fixture(**fixture),engine='port',tail=False,extra_players=extras,live_players=True)
    return normal_reference_drive(m)


class OriginalReference(unittest.TestCase):
    def test_original_instructions_and_port_equal_after_identical_declared_extra_inputs(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image,context,fixture=_fixtures().entry()
        probe=Match.from_route_entry(image,Fixture(**fixture),context)
        core=probe._squad(probe.opts['managed']);pool=probe._pool()
        on=next(b for a in core[1:11] for b in pool if probe._available(a) and probe._available(b) and probe._player(a,6)==probe._player(b,6))
        extras=[on]+[w for w in pool if w!=on and probe._available(w)][:3]
        original=Match(image,Fixture(**fixture),engine='original',tail=False,extra_players=extras,live_players=True)
        expected=normal_reference_drive(original)
        actual=call_in_pypy('test_extended_match_t138b','port_normal_reference',args=(image.state(image.tables),to_record(image.tables),fixture,extras),timeout=180)
        self.assertEqual(actual['records'],expected['records'])
        self.assertEqual(actual['selection'],expected['selection'])
        self.assertEqual(actual['inputs'],expected['inputs'])
        self.assertEqual(actual['bench'],13)
