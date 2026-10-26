"""T116: TEAM characteristics against genuine DOSBox screens, original renders and synthetic controls."""
import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'notes/432/skills'))
import harness as h  # noqa: E402
from decoders.team_characteristics import DESCRIPTORS, FIELDS, aggregates, bar_cells, team_characteristics  # noqa: E402

WIDTH = 16   # the template's characteristics cells, columns 46..61


def year_one():
    """E014-r0006's start state, a year into a game (nonzero caps), checked against its manifest and run record."""
    run = 'E014-r0006'
    f = json.loads((h.ROOT/f'evidence/E014/{run}.manifest.json').read_text())['files'][0]
    raw = (h.CACHE/f['asset']).read_bytes()
    assert h.sha(raw) == f['sha256'] == json.loads((h.ROOT/f'runs/E014/{run}.json').read_text())['start_state']['sha256']
    return (f'{run}:{f["name"]}', raw)


def decode(m, country):
    return team_characteristics(m.read_country(country), m.read_player, m.read_ds)


def observed(chars, attrs, d):
    """Label text, highlight over the 16 template cells, and the two numbers, as the screen holds them."""
    out = {}
    for x in d['descriptors']:
        start = 80*(x['row']-1)+x['column']-1
        out[x['field']] = (h.glyphs(chars[start:start+len(x['text'])]), h.highlight(attrs, x['row'], x['column'], WIDTH))
    for x in d['numbers']:
        start = 80*(x['row']-1)+x['column']-1
        out[x['field']] = h.glyphs(chars[start:start+len(x['text'])])
    return out


def lit(d):
    """Every cell the four bars highlight, in row-major order from each label's cell (a bar longer
    than the row runs on into the next rows); the screen ends at cell 2000."""
    cells = set()
    for x in d['descriptors']:
        start = 80*(x['row']-1)+x['column']-1
        cells.update(range(start, min(2000, start+x['cells'])))
    return cells


def expected(d):
    on = lit(d)
    out = {}
    for x in d['descriptors']:
        start = 80*(x['row']-1)+x['column']-1
        out[x['field']] = (x['text'], ''.join('1' if c in on else '0' for c in range(start, start+WIDTH)))
    out.update({x['field']: x['text'] for x in d['numbers']})
    return out


def direct(m, country):
    """13D0(country) called directly: the six words DS:9B5A..9B64 it leaves."""
    m.original.call('1771:13D0', [country], far=False, pop=2)
    return {f: m.ds_word(0x9B5A+2*i) for i, f in enumerate(FIELDS)}


WIDE = 6144   # cells: the furthest bar (row 23, column 46, 4095 cells) ends at 5900


def wide_panel(m, country):
    """157D into a scratch buffer cleared well past the screen: a run-on bar's whole length is visible."""
    m.g.put(h.SCREEN, b'\x20\x07'*2000+bytes(2*(WIDE-2000)))
    m.put_ds(0xA96E, b'\0\0'+(h.SCREEN >> 4).to_bytes(2, 'little'))
    m.original.call('1771:157D', [country], far=False, pop=2)
    raw = m.g.mem(h.SCREEN, 2*WIDE)
    return raw[::2], raw[1::2]


def exact_extent(m, country, descriptors):
    """With no performance bars on rows 20..23, the cells from row 20 column 46 onwards carrying 0x70
    are exactly the union of the four bars, beyond the screen's end included."""
    if m.read_ds(0xC1E, 1)[0] and m.read_ds(0xC1F, 1)[0]:
        return False
    _, attrs = wide_panel(m, country)
    on = set()
    for x in descriptors:
        start = 80*(x['row']-1)+x['column']-1
        on.update(range(start, start+x['cells']))
    first = 80*19+45
    assert {c for c in range(first, WIDE) if attrs[c] == 0x70} == {c for c in on if c >= first}, (country, 'extent')
    return True


def compare(m, country, where, screen=None):
    """13D0 directly against the aggregates; 157D's cells against the decoded panel. A label the
    host refuses (a Pascal length above 15 read from outside the tables) returns None."""
    values = aggregates(m.read_country(country), m.read_player)
    assert direct(m, country) == values, where
    try:
        d = team_characteristics(m.read_country(country), m.read_player, m.read_ds)
    except ValueError:
        # the label is refused; the bars and the highlight still come from the aggregates alone
        bars = dict(descriptors=[dict(field=f, row=row, column=46, cells=bar_cells(values[f], divisor))
                                 for f, _, row, divisor, _ in DESCRIPTORS])
        _, attrs = m.panel(country)
        on = lit(bars)
        for x in bars['descriptors']:
            start = 80*(x['row']-1)+x['column']-1
            assert all((attrs[c] == 0x70) == (c in on) for c in range(start, start+WIDTH)), (where, x)
        assert all(attrs[c] == 0x70 for c in on), (where, 'run-on')
        exact_extent(m, country, bars['descriptors'])
        return None
    chars, attrs = m.panel(country)
    assert observed(chars, attrs, d) == expected(d), (where, observed(chars, attrs, d), expected(d))
    on = lit(d)
    assert all((attrs[c] == 0x70) for c in on), (where, 'run-on')
    exact_extent(m, country, d['descriptors'])
    if screen is not None:
        assert observed(screen.chars, screen.attrs, d) == expected(d), (where, 'genuine')
    return d


def genuine_screens():
    rows = []
    for label, raw, screen in h.sitting_screens():
        m = h.Machine(raw)
        country = h.screen_country(m, screen.chars)
        chars, attrs = m.panel(country)
        stale = h.stale_rows(screen, chars, attrs)
        d = compare(m, country, label, None if stale else screen)
        assert d is not None, label
        rows.append(dict(state=label, genuine_screen=not stale, stale_rows=stale, country=country,
                         name=m.name(country), aggregates=d['aggregates'],
                         descriptors={x['field']: [x['text'], x['cells']] for x in d['descriptors']}))
    return rows


def genuine_renders(states):
    rows, seen = [], {}
    for label, raw in states:
        m = h.Machine(raw)
        for country in range(1, 129):
            d = compare(m, country, (label, country))
            assert d is not None, (label, country)
            for f, v in d['aggregates'].items():
                lo, hi = seen.get(f, (v, v))
                seen[f] = (min(lo, v), max(hi, v))
        players = [m.read_player(w) for c in range(1, 129) for i in range(11)
                   for w in [int.from_bytes(m.read_country(c)[2*i:2*i+2], 'little')]]
        rows.append(dict(state=label, countries=128,
                         starter_bytes={k: [min(p[o] for p in players), max(p[o] for p in players)]
                                        for k, o in (('morale', 0xC), ('fitness', 0xD), ('energy', 0xE),
                                                     ('hardness+5', 5), ('age', 1))}))
    return rows, {f: list(v) for f, v in seen.items()}


def fuzz(m, rnd, cases):
    """Synthetic: random edits of genuine starters' condition, hardness, age, caps and availability bytes."""
    rows = []
    for case in range(cases):
        country = rnd.randrange(1, 129)
        record = m.read_country(country)
        mode = case % 4    # 0 natural-like, 1 any byte, 2 negative corners, 3 table edges
        for i in range(11):
            w = int.from_bytes(record[2*i:2*i+2], 'little')
            if w == 0:
                continue
            p = bytearray(m.read_player(w))
            if mode == 0:
                p[0xC], p[0xD], p[0xE] = rnd.randrange(1, 33), rnd.randrange(1, 33), rnd.randrange(1, 33)
                p[5] = rnd.randrange(0, 18)
            elif mode == 1:
                for off in (1, 3, 5, 8, 9, 0xC, 0xD, 0xE, 0x10):
                    p[off] = rnd.randrange(256)
            elif mode == 2:
                p[0xC], p[0xD] = rnd.randrange(0x80, 0x100), rnd.randrange(0x80, 0x100)
                p[0xE] = rnd.choice([1, 0x7F, rnd.randrange(256)])
                p[8], p[9] = 0xFF, rnd.randrange(256)
            else:
                v = rnd.choice([16, 17, 32, 33, 0, 1])
                p[0xC] = p[0xD] = p[0xE] = max(1, v)
                p[5], p[3] = v, rnd.randrange(2)
            if mode != 1:
                p[0x10] = rnd.choice([0, 0, 0, 0x80, 0x20, 0x04, 0x5B])
            m.put_player(w, 0, bytes(p))
        if rnd.random() < 0.1:
            m.put_country(country, 2*rnd.randrange(11), b'\0\0')
        d = compare(m, country, case)
        rows.append(None if d is None else d['aggregates'])
    return rows


def wrap_controls(m, country):
    """Synthetic: eleven available players with fitness, then morale, of -k (k = 1..128): the
    wrapped sums divide unsigned to 5830..5957, past the shift's 4096 limit."""
    record = m.read_country(country)
    words = [int.from_bytes(record[2*i:2*i+2], 'little') for i in range(11)]
    compared = refused = 0
    for offset in (0xD, 0xC):
        for k in range(1, 129):
            for w in words:
                p = bytearray(m.read_player(w))
                p[0xC], p[0xD], p[0xE], p[0x10] = 16, 20, 20, 0
                p[offset] = (-k) & 0xFF
                m.put_player(w, 0, bytes(p))
            d = compare(m, country, ('wrap', offset, k))
            compared += d is not None
            refused += d is None
    return dict(labels_compared=compared, label_refusals_bars_compared=refused)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--cases', type=int, default=4000)
    a = ap.parse_args()
    if a.output.exists():
        raise SystemExit('immutable output already exists')
    t = time.time()
    screens = genuine_screens()
    states = h.cached_states()
    renders, ranges = genuine_renders(states + [year_one()] + [(label, raw) for label, raw, _ in h.sitting_screens()[::6]])
    fuzzed = fuzz(h.Machine(states[0][1]), random.Random(432116), a.cases)
    refused = fuzzed.count(None)
    wraps = wrap_controls(h.Machine(states[0][1]), 12)
    fuzzed = [x for x in fuzzed if x is not None]
    out_of_table = sum(1 for x in fuzzed if not (x['hardness'] <= 16 and x['fitness'] <= 32 and x['energy'] <= 32))
    receipt = dict(h.receipt_base(__file__),
                   method='genuine E015-r0007 DOSBox screens paired by digest with their snapshots, and '
                          'unmodified original 13D0 and 157D on genuine states; synthetic controls are '
                          'labelled and edit a private copied machine only',
                   genuine_screens=screens, genuine_renders=renders, genuine_aggregate_ranges=ranges,
                   synthetic_wrap=wraps,
                   synthetic_fuzz=dict(cases=len(fuzzed)+refused, compared=len(fuzzed), host_refusals=refused, seed=432116,
                                       out_of_table_cases=out_of_table,
                                       ranges={f: [min(x[f] for x in fuzzed), max(x[f] for x in fuzzed)]
                                               for f in FIELDS}),
                   source_hashes={p: h.sha((h.ROOT/p).read_bytes()) for p in [
                       'runtime/decoders/team_characteristics.py', 'runtime/decoders/team_skills.py',
                       'runtime/decoders/manager.py', 'static/goal-exe/code/seg_1771_02.asm',
                       'static/goal-exe/code/seg_1771_03.asm']},
                   seconds=round(time.time()-t))
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(receipt, indent=1, ensure_ascii=False)+'\n')
    print(f'{len(screens)} genuine TEAM screens; {len(renders)} genuine states x 128 original renders; '
          f'{len(fuzzed)} synthetic squads compared ({out_of_table} out of table, {refused} host refusals); wrap controls {wraps}: all exact')


if __name__ == '__main__':
    main()
