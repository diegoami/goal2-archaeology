"""Exhaustive check that the four surviving compute_ability mutants of mutation_sweep.py equal
the model on every byte triple (age, peak, rating) in 0..255 — equivalent mutants, which no
test can kill (T28, Done-when 2).

    python3 experiments/E014-q013-ageing/mutation_equivalence.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "runtime" / "model"))
import ageing as A


def m_lower_strict(a, p, r):        # peak < age <= peak + 3
    if p < a <= p + 3:
        return r & 0xFF
    k = a - (p + 3) if a > p + 3 else (p - a) // 2
    return (((r & 0xFF) * ((16 - k) & 0xFFFF)) & 0xFFFF) // 16 & 0xFF


def m_above_ge(a, p, r):            # age >= peak + 3 in the second test
    if p <= a <= p + 3:
        return r & 0xFF
    k = a - (p + 3) if a >= p + 3 else (p - a) // 2
    return (((r & 0xFF) * ((16 - k) & 0xFFFF)) & 0xFFFF) // 16 & 0xFF


def m_no_product_mask(a, p, r):
    if p <= a <= p + 3:
        return r & 0xFF
    k = a - (p + 3) if a > p + 3 else (p - a) // 2
    return (((r & 0xFF) * ((16 - k) & 0xFFFF))) // 16 & 0xFF


def m_no_factor_mask(a, p, r):
    if p <= a <= p + 3:
        return r & 0xFF
    k = a - (p + 3) if a > p + 3 else (p - a) // 2
    return (((r & 0xFF) * (16 - k)) & 0xFFFF) // 16 & 0xFF


for f in (m_lower_strict, m_above_ge, m_no_product_mask, m_no_factor_mask):
    bad = 0
    for a in range(256):
        for p in range(256):
            for r in range(256):
                if f(a, p, r) != A.compute_ability(a, p, r):
                    bad += 1
    print(f.__name__, "differs on", bad, "of", 256 ** 3)
