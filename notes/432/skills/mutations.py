"""T114 in-memory negative controls; never edit the checked-out source."""
import importlib
import io
import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import runtime.decoders.team_bars as bars  # noqa: E402
import runtime.decoders.team_skills as skills  # noqa: E402
import tests.test_team_skills_decoder as t  # noqa: E402
assert len(sys.argv) == 2 and not Path(sys.argv[1]).exists(), 'new output path required'
sources = {bars: Path(bars.__file__).read_text(), skills: Path(skills.__file__).read_text()}
mutants = [
    ('divide_keeper', bars, 'word if k == 0 else idiv(word, 4)', 'idiv(word, 4)'),
    ('divide_by_eight', bars, 'idiv(word, 4)', 'idiv(word, 8)'),
    ('clamp_from_zero', bars, 'value = 1 if value < 1', 'value = 0 if value < 0'),
    ('clamp_255', bars, '0x100 if value > 0x100', '0xFF if value > 0xFF'),
    ('scale_26', bars, 'value*25//256', 'value*26//256'),
    ('round_scale', bars, 'value*25//256', '(value*25+128)//256'),
    ('column_11', bars, 'BAR_COLUMN = 10', 'BAR_COLUMN = 11'),
    ('bonus_always', skills, 'if value:\n', 'if True:\n'),
    ('bonus_quarter', skills, 'bonus//8', 'bonus//4'),
    ('bonus_formula', skills, "manager_record[1]//8+0x10", "manager_record[1]//8"),
    ('ability_from_confidence', skills, 'manager_record[1]', 'manager_record[2]'),
    ('keeper_gets_tactics', skills, 'if player[6]:', 'if True:'),
    ('tactic_sides_swapped', skills, 'sums[3 if bit else 1]', 'sums[1 if bit else 3]'),
    ('no_player_override', skills, 'if e < 5 and _element', 'if False and _element'),
    ('panel_country_tactics', skills, "_read(read_country, player[0], 191", "_read(read_country, 1, 191"),
    ('hybrid_whole', skills, 'value//2', 'value'),
    ('hybrid_wrong_lines', skills, 'sums[line-3]', 'sums[line-4]'),
    ('slot_twelve', skills, 'range(1, 12)', 'range(1, 13)'),
    ('form_threshold', skills, 'form >= 0x20', 'form > 0x20'),
    ('no_halving', skills, "return _idiv(value, 2) if", "return value if"),
    ('availability_ignores_status', skills, 'any(_element(player[0x10], n) for n in (8, 6, 3))', 'False'),
    ('strength_offset', skills, 'player[4]-0x3E', 'player[4]-0x40'),
    ('no_line_bound', skills, 'if line > 5:', 'if False:'),
]
rows = []
try:
    for name, module, old, new in mutants:
        source = sources[module]
        assert source.count(old) >= 1, name
        exec(compile(source.replace(old, new), module.__file__, 'exec'), module.__dict__)
        if module is bars:
            exec(compile(sources[skills], skills.__file__, 'exec'), skills.__dict__)
        importlib.reload(t)
        r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
        assert not r.wasSuccessful(), name
        rows.append(dict(mutation=name, failures=len(r.failures), errors=len(r.errors)))
        for m, s in sources.items():
            exec(compile(s, m.__file__, 'exec'), m.__dict__)
finally:
    for m, s in sources.items():
        exec(compile(s, m.__file__, 'exec'), m.__dict__)
    importlib.reload(t)
r = unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromModule(t))
assert r.wasSuccessful()
Path(sys.argv[1]).write_text(json.dumps(dict(baseline_tests=r.testsRun, mutants=rows), indent=2)+'\n')
print(f'baseline {r.testsRun}/{r.testsRun}; {len(rows)}/{len(rows)} mutants rejected')
