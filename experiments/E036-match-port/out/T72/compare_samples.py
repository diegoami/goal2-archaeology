"""T72: strict declared-spec sample comparisons and the post-update falsifier hazard.

Arguments are sample JSONL files. Default runs must equal T57; each variant except
an explicitly noted unreached control must differ in after.seed or the records digest.
The unhooked entry/block counts establish the selected branches' original reach.
"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036))
import compare
import families

f = families.discover()['O8']
refs = compare.load(E036.parents[1] / f.reference)
specs = f.expected()
all_ok = True
for raw in sys.argv[1:]:
    p = Path(raw)
    rs = compare.load(p)
    ids = {mid: specs[mid] for mid in rs}
    variant = next(iter(rs.values())).get('variant')
    unreachable = p.name == 'sample-recovered-energy-plus-one.jsonl'
    expectation = 'differ' if variant and not unreachable else 'identical'
    lines, ok = compare.check(refs, rs, ids, expectation, image_sha256=next(iter(refs.values()))['image_sha256'])
    print(p.name)
    print('\n'.join(lines))
    for mid, rec in rs.items():
        if expectation == 'differ':
            before = refs[mid]
            seed = before['after']['seed'] != rec['after']['seed']
            records = before['after']['ranges']['records'] != rec['after']['ranges']['records']
            preserved = all(compare.get(before, k) == compare.get(rec, k) for k in
                            ('score', 'ticks', 'draws', 'events', 'board', 'templates', 'decisions'))
            print(f'{mid}: after.seed differs={seed}; after.ranges.records differs={records}; '
                  f'board/draws/events/decisions unchanged={preserved}')
            ok &= seed or records
        if unreachable:
            print('declared unreached control: 3651 has zero calls, so this sample is not an accepted falsifier')
    all_ok &= ok
sys.exit(0 if all_ok else 1)
