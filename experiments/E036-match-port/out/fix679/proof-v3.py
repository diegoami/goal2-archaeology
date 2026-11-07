"""Owner goal2#610: actual paused/half-time team-tactics edits, no injected game values."""
import argparse
import builtins
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
p = argparse.ArgumentParser()
p.add_argument('--engine', choices=('original', 'port'), required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--knockout', action='store_true')
a = p.parse_args()
assert not a.out.exists()
if a.engine == 'port':
    assert sys.implementation.name == 'pypy' and sys.version_info[:2] == (3, 11)
    real_import = builtins.__import__
    def deny(name, *args, **kwargs):
        if name == 'unicorn' or name.startswith('unicorn.'):
            raise ImportError('positive Unicorn denial')
        return real_import(name, *args, **kwargs)
    builtins.__import__ = deny
    try: __import__('unicorn')
    except ImportError: pass
    else: raise AssertionError('Unicorn denial is not active')
else:
    assert sys.implementation.name == 'cpython'
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'experiments/E036-match-port')]
from original_match import Image, Fixture, Match
from original_match import screens as S
import family
import records

raw = (ROOT / '.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
image_hash = hashlib.sha256(raw).hexdigest()
assert image_hash == 'e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
m = Match(Image.from_savestate(raw), Fixture(7, 19, index=39 if a.knockout else 21, kind=200 if a.knockout else 1), managed=7,
          seed=None if a.knockout else 0x1234, substitutions=5, delay_byte=0, record_draws=True, engine=a.engine,
          ports=['all'] if a.engine == 'port' else [], timeout_s=600)
started = time.monotonic()
paused = False
events = []
snapshots = []
stops = {}
ticks = 0
for e in m.events():
    events.append((e.kind, e.minute, e.score, copy.deepcopy(e.data)))
    if e.kind == 'tick': ticks += 1
    if not a.knockout and e.kind == 'minute' and e.minute >= 2 and not paused:
        paused = True
        m.pause()
    if e.kind != 'decision': continue
    d = e.data
    context = d['context']
    if context not in (('extra_time',) if a.knockout else ('pause', 'half_time')):
        m.answer(); continue
    key = context + str(d.get('half', ''))
    if key not in stops:
        original = d['tactics']
        steps = [(bit, not bool(original & (1 << (bit - 1)))) for bit in range(1, 9)]
        steps += [(bit, bool(original & (1 << (bit - 1)))) for bit in range(1, 9)]
        stops[key] = dict(steps=steps, index=0, expected=original,
            minute=e.minute, score=e.score, eleven=d['eleven'], bench=d['bench'],
            left=d['substitutions_left'], ticks=m.st['ticks'],
            seeds=[m.m.rd(0x7B62), m.m.rd(0x8336)])
    state = stops[key]
    assert e.minute == state['minute'] and e.score == state['score']
    assert d['eleven'] == state['eleven'] and d['bench'] == state['bench']
    assert d['substitutions_left'] == state['left'] and m.st['ticks'] == state['ticks']
    assert [m.m.rd(0x7B62), m.m.rd(0x8336)] == state['seeds']
    assert d['tactics'] == m._tactics() == state['expected']
    if context == 'pause':
        assert not d['substitutions_now'] and not m.m.rd(S.SUBS_ALLOWED, 1)
    if state['index']:
        assert d['edited']
    snapshots.append(dict(context=context, operation=state['index'], minute=e.minute,
        tactics=d['tactics'], left=d['substitutions_left'], ticks=m.st['ticks'],
        substitutions_now=d['substitutions_now'], seeds=state['seeds']))
    print(json.dumps(snapshots[-1]), flush=True)
    if state['index'] < len(state['steps']):
        bit, value = state['steps'][state['index']]
        state['expected'] = (state['expected'] | (1 << (bit - 1))) if value else (state['expected'] & ~(1 << (bit - 1)))
        state['index'] += 1
        m.answer(tactics={bit: value}, edit_only=True)
    else:
        m.answer()

assert (any(k.startswith('extra_time') for k in stops) if a.knockout else set(stops) == {'pause', 'half_time'})
assert all(s['index'] == 16 for s in stops.values())
assert not [e for e in events if e[0] == 'substitution_requested' or (e[0] == 'substitution' and e[3]['team'] == m.side)]
assert len([e for e in events if e[0] == 'tactics']) == 16 * len(stops)
result = m.result()
assert a.engine != 'port' or ('unicorn' not in sys.modules and not hasattr(m.m, '_uc'))
receipt = dict(knockout=a.knockout, engine=a.engine, implementation=sys.implementation.name, python=sys.version,
    engine_reference='unhooked original' if a.engine == 'original' else 'plain port; positive Unicorn denial',
    input_sha256=image_hash, completed=True, elapsed_s=time.monotonic()-started,
    snapshots=snapshots, result_sha256=records.result_digest(result),
    all_events_sha256=hashlib.sha256(repr(events).encode()).hexdigest(),
    canonical_events=records.events_digest(events),
    display_profile_events=family.display_events_digest(events),
    full_memory_sha256=hashlib.sha256(m.m.read(0, 0x110000)).hexdigest(),
    accepted_state_ranges=family.digest_memory(m, [], image_hash), memory_mask=[],
    score=result['score'], draws=result['draws'], draws_digest=result['draws_digest'],
    runtime_source_sha256=hashlib.sha256((ROOT/'runtime/original_match/match.py').read_bytes()).hexdigest(),
    proof_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
with a.out.open('x') as f: json.dump(receipt, f, indent=2); f.write('\n')
print(json.dumps({k: receipt[k] for k in ('engine', 'completed', 'elapsed_s', 'score', 'draws')}), flush=True)
