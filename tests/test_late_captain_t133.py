"""T133/#715: late captain choice via the original prompt's keys; no original bytes retained."""
import copy
import hashlib
import json
import sys
import unittest
from dataclasses import asdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'runtime'), str(ROOT/'tools')]
from original_match.match import Match, Fixture, PLAYER_POSITION, SITE_PROMPT
from original_match.machine import MEM_SIZE, REGS
from original_match.image import Image
from original_match.port.tables import from_record, to_record
from tests.test_route_sealed import _fixtures
from port_test_runtime import call_in_pypy


def _snapshot(m):
    return (m.m.read(0, MEM_SIZE), {r:m.m.reg(r) for r in REGS}, copy.deepcopy(m.opts),
            copy.deepcopy(m.st), copy.deepcopy(m._queue), copy.deepcopy(getattr(m, '_replay_actions', None)),
            getattr(m, '_replay_events', None), copy.deepcopy(m._frame_state()))


def _decision(m, events):
    for ev in m.events():
        events.append(asdict(ev))
        if ev.kind == 'decision':
            assert ev.data['context'] == 'pre_match'
            return ev.data
    raise AssertionError('pre_match decision missing')


def _drive(m, mode, original=False):
    events, keys, captains = [], [], []
    previous = m._key_for
    target = [None]
    initial_prompt = [False]
    def key(site):
        # Independent original key policy at CC7B, using the same published
        # F030 cursor grammar as the legacy configured captain path. No new
        # captain answer or new input state is used by this oracle.
        if (original and mode == 'late' and site == SITE_PROMPT
                and m.st['prompt']['role'] == 1 and m.st['prompt'].get('initial')):
            from original_match import screens as S
            slot = m._squad(m.opts['managed']).index(target[0])+1
            here = m.m.frame_word(m.m.reg('bp'), S.PROMPT_SLOT_BP)
            value = S.step_toward(here, slot) if here != slot else S.ENTER
            if here == slot:
                m.st['prompt'] = None
        else:
            value = previous(site)
        if value is not None:
            keys.append([site, value])
        return value
    m._key_for = key
    def prompt(replay):
        if not replay:
            initial_prompt[0] = m.m.stack_word(2) == 1 and m.m.stack_word(4) == m.side
    def accepted(replay):
        if not replay and initial_prompt[0]:
            captains.append(m.m.reg('ax')); initial_prompt[0] = False
    m.m.at('0791:CC7B', prompt); m.m.at('0791:D010', accepted)
    first = _decision(m, events)
    m.answer(edit_only=True, tactics={8:not bool(first['tactics'] & 128)})
    second = _decision(m, events)
    pos = dict(second['positions']); off = second['eleven'][-1]
    on = next(w for w in second['bench'] if w and pos[w] == pos[off])
    m.answer(edit_only=True, substitutions=[[off, on]])
    third = _decision(m, events); pool_off = third['eleven'][-1]
    incoming = next(w for w in third['pool'] if m._player(w, PLAYER_POSITION) == pos[pool_off]
                    and m._available(w))
    m.answer(edit_only=True, substitutions=[[pool_off, incoming]])
    fourth = _decision(m, events)
    assert incoming in fourth['eleven'] and pool_off in fourth['pool']
    assert incoming not in first['eleven']
    target[0] = incoming
    replay_checks = 0
    if not original:
        before = _snapshot(m)
        for bad in (True, False, 0, -1, 3061, fourth['bench'][0], pool_off, '121', 121.0):
            try:
                m.answer(captain=bad)
            except ValueError:
                pass
            else:
                raise AssertionError('bad/stale captain accepted: '+repr(bad))
            assert _snapshot(m) == before
        if mode == 'late':
            m.answer(captain=incoming)
        elif mode == 'default':
            m.answer(captain=None)
        else:
            m.answer()
        # Omission must preserve legacy checkpoint/event shape.
        assert ('captain' in m.st['decisions'][-1]['answer']) == (mode != 'omit')
        before = _snapshot(m)
        try:
            m.answer(captain=incoming)
        except Exception as exc:
            from original_match.match import MatchError
            assert isinstance(exc, MatchError)
        else:
            raise AssertionError('consumed answer accepted')
        assert _snapshot(m) == before
        raw = m.save(); loaded = Match.load(raw)
        assert loaded.m.read(0, MEM_SIZE) == m.m.read(0, MEM_SIZE)
        assert all(loaded.m.reg(r) == m.m.reg(r) for r in REGS)
        assert loaded.st == json.loads(json.dumps(m.st)) or json.dumps(loaded.st, sort_keys=True) == json.dumps(m.st, sort_keys=True)
        replay_checks += 1
    else:
        m.answer()  # The oracle gets its captain solely from the original prompt's keys.
    for ev in m.events():
        events.append(asdict(ev))
        if ev.kind == 'decision':
            raise AssertionError('unexpected decision before first minute: '+str(ev.data))
        if ev.kind == 'minute':
            break
    assert ev.kind == 'minute' and captains
    if mode == 'late':
        assert captains[0] == incoming
    if not original:
        loaded = Match.load(m.save())
        assert loaded.m.read(0, MEM_SIZE) == m.m.read(0, MEM_SIZE)
        assert all(loaded.m.reg(r) == m.m.reg(r) for r in REGS)
        replay_checks += 1
    image=Image(m.image_header+m.m.read(0,MEM_SIZE)+m.image_tail); image.tables=m.tables if not original else m._test_tables
    return dict(state=image.state(image.tables), memory=m.m.read(0, MEM_SIZE), registers={r:m.m.reg(r) for r in REGS},
                keys=keys, events=events, draws=m.st['draws'], captains=captains,
                incoming=incoming, replay_checks=replay_checks)


def _port(state, tables, fixture, context, mode):
    assert sys.implementation.name == 'pypy' and sys.version_info[:2] == (3,11)
    m = Match.from_route_entry(Image.from_state(state, from_record(tables)), Fixture(**fixture), context)
    m.configure_route_entry(pre_match_edits=True, record_draws=True, substitutions=2)
    return _drive(m, mode)


def _guards(state, tables, fixture, context):
    assert sys.implementation.name == 'pypy'
    m = Match.from_route_entry(Image.from_state(state, from_record(tables)), Fixture(**fixture), context)
    m.configure_route_entry(pre_match_edits=True)
    d = _decision(m, [])
    w = next(w for w in d['eleven'] if m._available(w))
    cases = [dict(edit_only=True), dict(tactics={8:True}), dict(substitutions=[[d['eleven'][-1],d['bench'][0]]]),
             dict(positions={w:3}), dict(marking={w:0}), dict(own_tactics={w:{1:True}}),
             dict(quick=True), dict(speed=1), dict(taker=w), dict(shootout_order=[w]),
             dict(request_substitution=False), dict(opportunity='accept')]
    for extra in cases:
        before = _snapshot(m)
        try:m.answer(captain=w, **extra)
        except ValueError:pass
        else:raise AssertionError('mixed captain answer accepted')
        assert _snapshot(m) == before
    for context_name in ('half_time', 'pause', 'substitution', 'extra_time', 'set_piece', 'shootout_order'):
        m.st['waiting']['context'] = context_name
        before = _snapshot(m)
        try:m.answer(captain=w)
        except ValueError:pass
        else:raise AssertionError('wrong context accepted')
        assert _snapshot(m) == before
    m.st['waiting']['context'] = 'pre_match'
    m.opts.pop('pre_match_edits')
    before = _snapshot(m)
    try:m.answer(captain=w)
    except ValueError:pass
    else:raise AssertionError('unconfigured captain accepted')
    assert _snapshot(m) == before
    # Unavailable XI member: declared fixture mutation before the purity snapshot.
    m.opts['pre_match_edits'] = True
    from original_match.image import PLAYERS_PTR, PLAYER_SIZE
    m.m.write(m.m.far(PLAYERS_PTR)+PLAYER_SIZE*w+0x0E, b'\0')
    before = _snapshot(m)
    try:m.answer(captain=w)
    except ValueError:pass
    else:raise AssertionError('unavailable captain accepted')
    assert _snapshot(m) == before
    # Later replacement prompts ignore both kinds of kickoff override.
    m.st['kickoff_captain'] = w; m.st['prompt'] = {'role':1, 'initial':False}
    from original_match import screens as S
    assert m._captain_key() == S.ENTER
    return len(cases)+len(('half_time','pause','substitution','extra_time','set_piece','shootout_order'))+2


class LateCaptain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image, cls.context, cls.fixture = _fixtures().entry()

    def test_rejection_matrix_preserves_full_state_and_replay(self):
        count=call_in_pypy('test_late_captain_t133','_guards', args=(self.image.state(self.image.tables),
                          to_record(self.image.tables),self.fixture,self.context))
        self.assertEqual(count,20)

    def test_chained_edits_late_pool_captain_equal_original_keys(self):
        self.compare('late')

    def test_explicit_default_and_omission_equal_legacy_original(self):
        for mode in ('default','omit'):
            with self.subTest(mode=mode):self.compare(mode)

    def compare(self, mode):
        expected_match=Match(self.image,Fixture(**self.fixture),engine='original',tail=False,
                             record_draws=True,substitutions=2)
        assert expected_match.m.read(0,MEM_SIZE)==bytes(self.image.memory[:MEM_SIZE])
        for k,v in self.context.items():expected_match.m.set_reg(k,v)
        expected_match._test_tables=self.image.tables
        expected_match.opts['pre_match_edits']=True  # proof-only original menu input policy
        expected=_drive(expected_match,mode,original=True)
        actual=call_in_pypy('test_late_captain_t133','_port', args=(self.image.state(self.image.tables),
                           to_record(self.image.tables),self.fixture,self.context,mode))
        for field in ('state','keys','events','draws','captains','incoming'):
            self.assertEqual(actual[field],expected[field],field)
        print('T133_REGISTER_DIFF '+str({r:(expected['registers'][r],actual['registers'][r]) for r in REGS if expected['registers'][r]!=actual['registers'][r]}),flush=True)
        self.assertEqual(actual['replay_checks'],2)
        receipt=dict(mode=mode, memory_sha256=hashlib.sha256(actual['memory']).hexdigest(),
                     all16=actual['registers'],key_count=len(actual['keys']),
                     keys_sha256=hashlib.sha256(json.dumps(actual['keys']).encode()).hexdigest(),
                     event_count=len(actual['events']),draw_count=len(actual['draws']),
                     captains=actual['captains'],incoming=actual['incoming'],replay_checks=2,
                     original_full_memory_equal=True, original_all16_equal=True)
        print('T133_RECEIPT '+json.dumps(receipt,sort_keys=True),flush=True)


if __name__=='__main__':unittest.main()
