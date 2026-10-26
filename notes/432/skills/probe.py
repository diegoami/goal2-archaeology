"""T114: TEAM skills bars against genuine DOSBox screens, original renders and synthetic controls."""
import argparse
import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as h  # noqa: E402
from decoders.team_bars import line_bars  # noqa: E402
from decoders.team_skills import line_sums, team_skills  # noqa: E402

ROWS = range(15, 19)


def decode(m, country):
    return team_skills(m.read_country(country), m.read_player, m.read_country, m.read_manager,
                       m.read_ds, m.read_code)


def bar_cells(attrs, decoded):
    """Observed and expected highlight over the 25 bar cells of each skills row."""
    seen = [h.highlight(attrs, b['row'], b['column'], 25) for b in decoded['bars']]
    want = [h.expected(b['cells'], 25) for b in decoded['bars']]
    return seen, want


def direct_sums(m, country):
    """0BC4(flag 0, side 1, country) called directly; the four words it leaves at DS:9B47+4k."""
    m.original.call('1771:0BC4', [0, 1, country], far=True, pop=6)
    return [int.from_bytes(m.read_ds(0x9B47+4*k, 2), 'little', signed=True) for k in range(4)]


def genuine_screens():
    """Each E015-r0007 TEAM screen: exact when current; a stale screen (drawn before a later state
    change) is recorded with its differing rows and checked against the re-render instead."""
    rows = []
    for label, raw, screen in h.sitting_screens():
        m = h.Machine(raw)
        country = h.screen_country(m, screen.chars)
        d = decode(m, country)
        chars, attrs = m.panel(country)
        stale = h.stale_rows(screen, chars, attrs)
        seen, want = bar_cells(attrs if stale else screen.attrs, d)
        assert seen == want, (label, seen, want)
        rows.append(dict(state=label, genuine_screen=not stale, stale_rows=stale, country=country,
                         name=m.name(country), line_sums=d['line_sums'], cells=[b['cells'] for b in d['bars']],
                         screen_cells=bar_cells(screen.attrs, d)[0]))
    return rows


def genuine_renders(states):
    rows = []
    for label, raw in states:
        m = h.Machine(raw)
        cells = []
        for country in range(1, 129):
            d = decode(m, country)
            assert direct_sums(m, country) == d['line_sums'], (label, country)
            _, attrs = m.panel(country)
            seen, want = bar_cells(attrs, d)
            assert seen == want, (label, country, seen, want)
            cells.append([b['cells'] for b in d['bars']])
        rows.append(dict(state=label, countries=128, cells_by_country=cells))
    return rows


def bars_sweep(m):
    """Synthetic: 11E1 alone over every signed word value, the same value on all four lines."""
    count = 0
    for v in range(-0x8000, 0x8000):
        m.put_ds(0x9B47, b''.join((v & 0xFFFF).to_bytes(2, 'little')+b'\0\0' for _ in range(4)))
        m.g.put(h.SCREEN, b'\x20\x07'*2000)
        m.put_ds(0xA96E, b'\0\0'+(h.SCREEN >> 4).to_bytes(2, 'little'))
        m.original.call('1771:11E1', [15], far=False, pop=2)
        attrs = m.g.mem(h.SCREEN, 4000)[1::2]
        bars = line_bars([v]*4, 15)
        stored = [int.from_bytes(m.read_ds(0x9B47+4*k, 2), 'little', signed=True) for k in range(4)]
        assert stored == [b['value'] for b in bars], (v, stored)
        assert [h.highlight(attrs, b['row'], 10, 30) for b in bars] == [h.expected(b['cells'], 30) for b in bars], v
        count += 1
    return count


def fuzz(m, seed, cases):
    """Synthetic: random edits of genuine squads, tactics and manager bytes; 0BC4 and 157D vs the decoder."""
    rnd = random.Random(seed)
    rows = []
    for case in range(cases):
        country = rnd.randrange(1, 129)
        record = m.read_country(country)
        words = [int.from_bytes(record[2*i:2*i+2], 'little') for i in range(11)]
        for i, w in enumerate(words):
            if rnd.random() < 0.08:
                m.put_country(country, 2*i, b'\0\0')
                continue
            if w == 0:
                continue
            p = bytearray(m.read_player(w))
            for off in (2, 4, 5, 0xC, 0xE, 0xF, 0x10):
                if rnd.random() < 0.7:
                    p[off] = rnd.randrange(256)
            if rnd.random() < 0.2:
                p[5] = rnd.randrange(31)
                p[2] = 30-p[5]
            p[6] = rnd.randrange(16)
            p[7] = rnd.randrange(14)
            if rnd.random() < 0.5:
                p[0] = rnd.randrange(1, 129)
            m.put_player(w, 0, bytes(p))
        m.put_country(country, 0x2D, bytes([rnd.randrange(256)]))
        manager = rnd.choice([0, record[0x2E], rnd.randrange(1, 135)])
        m.put_country(country, 0x2E, bytes([manager]))
        m.put_manager(manager, 1, bytes([rnd.randrange(256)]))
        d = decode(m, country)
        assert direct_sums(m, country) == d['line_sums'], (seed, case)
        _, attrs = m.panel(country)
        seen, want = bar_cells(attrs, d)
        assert seen == want, (seed, case, seen, want)
        rows.append(d['line_sums'])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--fuzz', type=int, default=1500)
    a = ap.parse_args()
    if a.output.exists():
        raise SystemExit('immutable output already exists')
    t = time.time()
    screens = genuine_screens()
    states = h.cached_states()
    renders = genuine_renders(states)
    renders += genuine_renders([(label, raw) for label, raw, _ in h.sitting_screens()[::6]])
    m = h.Machine(states[0][1])
    swept = bars_sweep(m)
    fuzzed = fuzz(h.Machine(states[0][1]), 432114, a.fuzz) + fuzz(h.Machine(states[1][1]), 432115, a.fuzz)
    receipt = dict(h.receipt_base(__file__),
                   method='genuine E015-r0007 DOSBox screens (chars and attributes from the snapshot paired by '
                          'digest) and unmodified original 0BC4/11E1/157D calls on genuine states; synthetic '
                          'controls are labelled and edit a private copied machine only',
                   genuine_screens=screens,
                   genuine_renders=[dict(state=r['state'], countries=r['countries']) for r in renders],
                   genuine_render_cells={r['state']: r['cells_by_country'] for r in renders},
                   synthetic_11E1_sweep=dict(values=swept, range='-32768..32767 on all four lines'),
                   synthetic_fuzz=dict(cases=len(fuzzed), seeds=[432114, 432115],
                                       distinct_line_sums=len({tuple(x) for x in fuzzed}),
                                       min_sum=min(min(x) for x in fuzzed), max_sum=max(max(x) for x in fuzzed)),
                   source_hashes={p: h.sha((h.ROOT/p).read_bytes()) for p in [
                       'runtime/decoders/team_bars.py', 'runtime/decoders/team_skills.py',
                       'static/goal-exe/code/seg_1771_02.asm', 'static/goal-exe/code/seg_1771_03.asm',
                       'static/goal-exe/code/seg_1771_05.asm', 'static/goal-exe/code/seg_214B_01.asm',
                       'static/goal-exe/code/seg_214B_03.asm']},
                   seconds=round(time.time()-t))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=1, ensure_ascii=False)+'\n')
    print(f'{len(screens)} genuine TEAM screens; {len(renders)} genuine states x 128 original renders; '
          f'{swept} 11E1 values; {len(fuzzed)} synthetic squads: all exact')


if __name__ == '__main__':
    main()
