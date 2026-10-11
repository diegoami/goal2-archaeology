#!/usr/bin/env python3
"""The per-player numbers F021 quotes, from the model (each value is checked against the original
for the same inputs by check_condition.py where the record exists).

    python3 experiments/E020-q018-condition-performance/tables.py > experiments/E020-q018-condition-performance/tables-002.txt

1. 1771:377E at skill +4 = 0xE1 (225) and 0x4A (74), keeper-position record, over energy 1..32 and
   the form values 1, 16, 31, 32, 33.
2. 0791:278A at the same skill byte for element 3 (energy-blended, outfield) and its share relative
   to the (energy 32, form 31) value, the E010 half-time image's class/profile tables.
3. the chance gates that read energy only: 2B7B (1/(33 - E)), 4A28 (E > rand(6)), 5049 (1/(E idiv 2))."""
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from runtime.model import condition  # noqa: E402

rec = json.loads((HERE / "records/strength-001.json").read_text())
foot_table, foot_index = bytes.fromhex(rec["foot_table_DS_0E60"]), bytes.fromhex(rec["foot_index_DS_0E7C"])
con = json.loads((HERE / "records/contest-001.json").read_text())
class_table, profile_table = bytes.fromhex(con["class_table_DS_6D25"]), bytes.fromhex(con["profile_table_DS_6DCD"])

FORMS = (1, 16, 31, 32, 33)
print("377E (quick engine), keeper-position record, +5 = 8")
for skill in (0xE1, 0x4A):
    print(f"skill +4 = {skill}: rows energy, columns form {FORMS}")
    for e in (1, 8, 16, 24, 32):
        row = [condition.strength(1, condition.with_condition(bytes([0] * 4 + [skill, 8] + [0] * 14), e, f),
                                  foot_table, foot_index) for f in FORMS]
        print(f"  energy {e:2d}: {row}")
print()
print("278A element 3 (watched engine), record +4=0xB4 +5=8 +7=2, rows energy, columns form", FORMS)
base = bytes([0, 0, 0, 0, 0xB4, 8, 0, 2] + [0] * 12)
ref = condition.contest(condition.with_condition(base, 32, 31), 3, class_table, profile_table, event=0)
print("  value at (energy 32, form 31) =", ref)
for e in (1, 8, 16, 24, 32):
    row = [condition.contest(condition.with_condition(base, e, f), 3, class_table, profile_table, event=0) for f in FORMS]
    print(f"  energy {e:2d}: {row}  share of the (32,31) value: {[round(v / ref, 3) for v in row]}")
print()
print("energy-only gates (probability / condition) for energy 1..32")
for e in (1, 2, 8, 16, 24, 32):
    p2b7b = Fraction(1, 33 - e)
    print(f"  energy {e:2d}: 2B7B P(true) = {p2b7b} = {float(p2b7b):.3f}; 4A28 P(E > rand(6)) = "
          f"{Fraction(max(0, min(6, e - 1)), 6)}; 5049 chance n = {e // 2} -> P = "
          f"{Fraction(1, max(e // 2, 1)) if e // 2 else 1}")
