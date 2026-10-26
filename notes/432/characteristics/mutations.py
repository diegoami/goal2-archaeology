"""T116 in-memory negative controls; never edit the checked-out source."""
import importlib
import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import runtime.decoders.team_characteristics as ch  # noqa: E402
import tests.test_team_characteristics_decoder as t  # noqa: E402
assert len(sys.argv) == 2 and not Path(sys.argv[1]).exists(), 'new output path required'
source = Path(ch.__file__).read_text()
mutants = [
    ('seed_zero', 'acc = dict.fromkeys(FIELDS, 6)', 'acc = dict.fromkeys(FIELDS, 0)'),
    ('seed_five', 'acc = dict.fromkeys(FIELDS, 6)', 'acc = dict.fromkeys(FIELDS, 5)'),
    ('divide_by_ten', '(v & 0xFFFF)//11', '(v & 0xFFFF)//10'),
    ('signed_sums', '(v & 0xFFFF)//11', '(v if v >= 0 else 0)//11'),
    ('count_unavailable', '        if unavailable(player):\n            continue\n', ''),
    ('morale_unclamped', 'min(32, _s8(player[0xC]))', '_s8(player[0xC])'),
    ('morale_unsigned', 'min(32, _s8(player[0xC]))', 'min(32, player[0xC])'),
    ('no_morale_floor', "out['morale'] = max(1, out['morale'])", 'pass'),
    ('floor_everything', "out['morale'] = max(1, out['morale'])", 'out = {k: max(1, v) for k, v in out.items()}'),
    ('fitness_unsigned', 'acc[\'fitness\'] += _s8(player[0xD])', 'acc[\'fitness\'] += player[0xD]'),
    ('hardness_ignores_bit', "(player[5]-(player[3] & 1)) & 0xFF", 'player[5]'),
    ('hardness_signed', "(player[5]-(player[3] & 1)) & 0xFF", '(player[5]-(player[3] & 1))'),
    ('age_from_fitness', "acc['age'] += player[1]", "acc['age'] += player[0xD]"),
    ('caps_byte', "acc['caps'] += int.from_bytes(player[8:10], 'little')", "acc['caps'] += player[8]"),
    ('slot_twelve', 'range(1, 12)', 'range(1, 13)'),
    ('hardness_bar_32', "('hardness', 0x78C4, 20, 16,", "('hardness', 0x78C4, 20, 32,"),
    ('morale_bar_16', "('morale', 0x78A3, 23, 32,", "('morale', 0x78A3, 23, 16,"),
    ('no_shift_mask', 'return ((value << 4) & 0xFFFF)//divisor', 'return (value << 4)//divisor'),
    ('swap_fitness_energy_tables', "('fitness', 0x78D5,", "('fitness', 0x78F6,"),
    ('morale_table_offset', "('morale', 0x78A3,", "('morale', 0x78A4,"),
    ('column_47', 'COLUMN = 46', 'COLUMN = 47'),
    ('caps_column', "('caps', 19, 49)", "('caps', 19, 50)"),
    ('clamp_to_table', 'text=_label(read_ds, table, values[f])', 'text=_label(read_ds, table, min(values[f], hi))'),
    ('unbounded_label', 'record[0] > 15', 'record[0] > 255'),
]
rows = []
try:
    for name, old, new in mutants:
        assert source.count(old) >= 1, name
        exec(compile(source.replace(old, new), ch.__file__, 'exec'), ch.__dict__)
        importlib.reload(t)
        r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
        assert not r.wasSuccessful(), name
        rows.append(dict(mutation=name, failures=len(r.failures), errors=len(r.errors)))
finally:
    exec(compile(source, ch.__file__, 'exec'), ch.__dict__)
    importlib.reload(t)
r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
assert r.wasSuccessful()
Path(sys.argv[1]).write_text(json.dumps(dict(baseline_tests=r.testsRun, mutants=rows), indent=2)+'\n')
print(f'baseline {r.testsRun}/{r.testsRun}; {len(rows)}/{len(rows)} mutants rejected')
