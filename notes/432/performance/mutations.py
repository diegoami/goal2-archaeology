"""T115 in-memory negative controls; never edit the checked-out source."""
import importlib
import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import runtime.decoders.team_performance as perf  # noqa: E402
import tests.test_team_performance_decoder as t  # noqa: E402
assert len(sys.argv) == 2 and not Path(sys.argv[1]).exists(), 'new output path required'
source = Path(perf.__file__).read_text()
mutants = [
    ('gate_c1e_only', 'return bool(match_set_up) and bool(in_match_menu_used)', 'return bool(match_set_up)'),
    ('gate_c1f_only', 'return bool(match_set_up) and bool(in_match_menu_used)', 'return bool(in_match_menu_used)'),
    ('gate_either', 'bool(match_set_up) and bool', 'bool(match_set_up) or bool'),
    ('own_country_always', 'sums = role_sums(read_country(sides[side])', 'sums = role_sums(read_country(country)'),
    ('side_by_first', 'return 1 if sides[1] == country else 0', 'return 0 if sides[0] == country else 1'),
    ('no_offset', 'value = s16(word-0x37)', 'value = s16(word)'),
    ('threshold_before_offset', 'value = s16(word-0x37)\n    if value > 5000:', 'value = s16(word-0x37)\n    if value+0x37 > 5000:'),
    ('threshold_inclusive', 'if value > 5000:', 'if value >= 5000:'),
    ('no_substitute_decode', 'value = s16(value-10000)', 'value = value'),
    ('no_plus_100', 'return s16(value+100)', 'return s16(value)'),
    ('skip_blank', "value = player_value(int.from_bytes(player[0x12:0x14], 'little'))",
     "value = 0 if player[0x12:0x14] == b'\\xff\\x7f' else player_value(int.from_bytes(player[0x12:0x14], 'little'))"),
    ('skip_zero_words', "player = read_player(word)\n", "player = read_player(word)\n        if word == 0:\n            continue\n"),
    ('half_floor', 'sums[role-3] += idiv(value, 2)', 'sums[role-3] += value//2'),
    ('hybrid_whole', 'sums[role-2] += idiv(value, 2)', 'sums[role-2] += value'),
    ('skills_table', 'read_ds(0xD7C+player[6], 1)', 'read_ds(0xD4E+player[6], 1)'),
    ('no_role_bound', 'if role > 5:', 'if False:'),
    ('row_15', 'PERFORMANCE_ROW = 20', 'PERFORMANCE_ROW = 15'),
    ('no_wrap', 'return [s16(v) for v in sums]', 'return sums'),
]
rows = []
try:
    for name, old, new in mutants:
        assert source.count(old) >= 1, name
        exec(compile(source.replace(old, new), perf.__file__, 'exec'), perf.__dict__)
        importlib.reload(t)
        r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
        assert not r.wasSuccessful(), name
        rows.append(dict(mutation=name, failures=len(r.failures), errors=len(r.errors)))
finally:
    exec(compile(source, perf.__file__, 'exec'), perf.__dict__)
    importlib.reload(t)
r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
assert r.wasSuccessful()
Path(sys.argv[1]).write_text(json.dumps(dict(baseline_tests=r.testsRun, mutants=rows), indent=2)+'\n')
print(f'baseline {r.testsRun}/{r.testsRun}; {len(rows)}/{len(rows)} mutants rejected')
