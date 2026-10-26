"""T115: TEAM performance bars against genuine DOSBox screens, original renders and synthetic controls."""
import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'notes/432/skills'))
import harness as h  # noqa: E402
from decoders.team_performance import team_performance  # noqa: E402

ROWS = range(20, 24)


def state(m):
    return (m.read_ds(0xC1E, 1)[0], m.read_ds(0xC1F, 1)[0], (m.ds_word(0x9B34), m.ds_word(0x9B36)))


def decode(m, country):
    c1e, c1f, sides = state(m)
    return team_performance(country, c1e, c1f, sides, m.read_country, m.read_player, m.read_ds)


def check(attrs, d, where):
    """Open gate: the decoder's highlight; closed gate: no 0x70 anywhere in the four bar rows."""
    seen = [h.highlight(attrs, r, 10, 25) for r in ROWS]
    want = ['0'*25]*4 if d is None else [h.expected(b['cells'], 25) for b in d['bars']]
    assert seen == want, (where, seen, want)
    return seen


def genuine_screens():
    rows = []
    for label, raw, screen in h.sitting_screens():
        m = h.Machine(raw)
        country = h.screen_country(m, screen.chars)
        d = decode(m, country)
        chars, attrs = m.panel(country)
        stale = h.stale_rows(screen, chars, attrs)
        check(attrs if stale else screen.attrs, d, label)
        c1e, c1f, sides = state(m)
        rows.append(dict(state=label, genuine_screen=not stale, stale_rows=stale, country=country,
                         name=m.name(country), c1e=c1e, c1f=c1f, sides=list(sides),
                         shown=d is not None, side=d and d['side'], role_sums=d and d['role_sums'],
                         cells=d and [b['cells'] for b in d['bars']]))
    return rows


def genuine_renders(states):
    rows = []
    for label, raw in states:
        m = h.Machine(raw)
        c1e, c1f, sides = state(m)
        shown = 0
        for country in range(1, 129):
            d = decode(m, country)
            _, attrs = m.panel(country)
            check(attrs, d, (label, country))
            shown += d is not None
        rows.append(dict(state=label, c1e=c1e, c1f=c1f, sides=list(sides), countries=128, shown=shown))
    return rows


def gate_controls(m, country):
    """Synthetic: every C1E/C1F pair in {0,1,255}^2, and DS:9B36 set to and away from the country."""
    rows = []
    sides = (m.ds_word(0x9B34), m.ds_word(0x9B36))
    for c1e in (0, 1, 255):
        for c1f in (0, 1, 255):
            for second in (sides[1], country, 0):
                m.put_ds(0xC1E, bytes([c1e, c1f]))
                m.put_ds(0x9B36, second.to_bytes(2, 'little'))
                d = decode(m, country)
                _, attrs = m.panel(country)
                check(attrs, d, (c1e, c1f, second))
                rows.append(dict(c1e=c1e, c1f=c1f, second=second, shown=d is not None, side=d and d['side']))
    m.put_ds(0x9B36, sides[1].to_bytes(2, 'little'))
    return rows


BOUNDARY = [0, 1, 0x36, 0x37, 0x38, 0x37+156, 0x37+157, 0x37-99, 0x37-100, 5000+0x37, 5001+0x37,
            5000, 5001, 10000+0x37, 10000+0x37-99, 0x7FFF, 0x8000, 0x8036, 0x8037, 0x8038, 0xFFFF]


def value_controls(m, rnd, cases):
    """Synthetic: one team's eleven +0x12 words and positions 0..13, boundary values and random words."""
    team = m.ds_word(0x9B34)
    m.put_ds(0xC1E, b'\1\1')
    record = m.read_country(team)
    words = [int.from_bytes(record[2*i:2*i+2], 'little') for i in range(11)]
    rows = []
    for case in range(cases):
        for i, w in enumerate(words):
            value = rnd.choice(BOUNDARY) if rnd.random() < 0.5 else rnd.randrange(0x10000)
            if case < len(BOUNDARY):
                value = BOUNDARY[case] if i == 0 else 0x37
            m.put_player(w, 0x12, (value & 0xFFFF).to_bytes(2, 'little'))
            m.put_player(w, 6, bytes([0 if case < len(BOUNDARY) and i == 0 else rnd.randrange(14)]))
        d = decode(m, team)
        _, attrs = m.panel(team)
        check(attrs, d, case)
        rows.append(d['role_sums'])
    return rows


def word_for(value):
    """A +0x12 word whose 1289 value is `value` (|value| < 4000: no -10000 branch)."""
    return (value-100+0x37) & 0xFFFF


def half_controls(m):
    """Synthetic: a hybrid player (positions 3 and 9) with odd and even signed values beside a line
    player whose value puts the line's quarter on a 25/256 cell boundary; the truncating half shows."""
    team = m.ds_word(0x9B34)
    m.put_ds(0xC1E, b'\1\1')
    record = m.read_country(team)
    words = [int.from_bytes(record[2*i:2*i+2], 'little') for i in range(11)]
    count = 0
    for hybrid, line in ((3, 1), (9, 12)):
        for half in range(-9, 10):
            for base in range(36, 52):
                for i, w in enumerate(words):
                    position, value = ((hybrid, half) if i == 0 else (line, base) if i == 1 else (0, 100))
                    m.put_player(w, 0x12, word_for(value).to_bytes(2, 'little'))
                    m.put_player(w, 6, bytes([position]))
                d = decode(m, team)
                _, attrs = m.panel(team)
                check(attrs, d, (hybrid, half, base))
                count += 1
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cases', type=int, default=3000)
    a = ap.parse_args()
    if a.output.exists():
        raise SystemExit('immutable output already exists')
    t = time.time()
    screens = genuine_screens()
    states = h.cached_states()
    renders = genuine_renders(states) + genuine_renders([(label, raw) for label, raw, _ in h.sitting_screens()[::6]])
    halftime = next(raw for label, raw in states if 'E010-r0001' in label)
    gates = gate_controls(h.Machine(halftime), 12)
    values = value_controls(h.Machine(halftime), random.Random(432115), a.cases)
    halves = half_controls(h.Machine(halftime))
    receipt = dict(h.receipt_base(__file__),
                   method='genuine E015-r0007 DOSBox screens paired by digest with their snapshots, and '
                          'unmodified original 157D (1289/11E1) on genuine states; synthetic controls are '
                          'labelled and edit a private copied machine only',
                   genuine_screens=screens, genuine_renders=renders,
                   synthetic_gates=gates, synthetic_hybrid_halves=halves,
                   synthetic_values=dict(cases=len(values), seed=432115, boundary_words=BOUNDARY,
                                         distinct_role_sums=len({tuple(x) for x in values}),
                                         min_sum=min(min(x) for x in values), max_sum=max(max(x) for x in values)),
                   source_hashes={p: h.sha((h.ROOT/p).read_bytes()) for p in [
                       'runtime/decoders/team_bars.py', 'runtime/decoders/team_performance.py',
                       'static/goal-exe/code/seg_1771_02.asm', 'static/goal-exe/code/seg_1771_03.asm']},
                   seconds=round(time.time()-t))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=1, ensure_ascii=False)+'\n')
    print(f'{len(screens)} genuine TEAM screens; {len(renders)} genuine states x 128 original renders; '
          f'{len(gates)} gate, {len(values)} value and {halves} hybrid-half controls: all exact')


if __name__ == '__main__':
    main()
