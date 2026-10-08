#!/usr/bin/env python3
"""In-place mutation sweep for T30 (Done-when 2): edit the file, clear __pycache__, run
tests.test_model_recreate in a fresh interpreter (timeout per mutant), restore the original in
`finally` and on SIGINT/SIGTERM, and verify every file's sha256 at the end.

    python3 experiments/E016-q014-retirement/mutation_sweep.py > experiments/E016-q014-retirement/mutations/<new file>

Each line: KILLED/SURVIVED/TIMEOUT, the file, the mutation, the test run's tail and the first
failing tests. A mutation marked "(expected equivalent: ...)" says why it may survive."""
import hashlib
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = "runtime/model/recreate.py"
G = "runtime/model/ageing.py"
K = "experiments/E016-q014-retirement/check_recreate.py"
TIMEOUT = 600

MUTATIONS = [
    # (file, id, old, new) — old must occur exactly once
    # offsets
    (M, "POSITION 0x06->0x07", "POSITION = 0x06 ", "POSITION = 0x07 "),
    (M, "MORALE 0x0C->0x0B", "MORALE = 0x0C ", "MORALE = 0x0B "),
    (M, "FITNESS 0x0D->0x0E", "FITNESS = 0x0D ", "FITNESS = 0x0E "),
    (M, "ENERGY 0x0E->0x0D", "ENERGY = 0x0E ", "ENERGY = 0x0D "),
    (M, "TACTICS 0x0F->0x10", "TACTICS = 0x0F ", "TACTICS = 0x10 "),
    # the generator
    (M, "LCG_MUL 0x7ABD->0x7ABF", "LCG_MUL = 0x7ABD ", "LCG_MUL = 0x7ABF "),
    (M, "LCG_INC 0x1B0F->0x1B0E", "LCG_INC = 0x1B0F ", "LCG_INC = 0x1B0E "),
    (M, "draw returns 0..n-1", "return ((w * n) >> 16) + 1, w", "return ((w * n) >> 16), w"),
    (M, "draw multiplies the old word", "    w = lcg_step(w)\n    return ((w * n) >> 16) + 1, w",
     "    v = ((w * n) >> 16) + 1\n    return v, lcg_step(w)"),
    # make_player
    (M, "PROFILE_DRAW 16->15", "PROFILE_DRAW = 0x10 ", "PROFILE_DRAW = 0x0F "),
    (M, "MP_AGE_DRAW 7->6", "MP_AGE_DRAW = 7 ", "MP_AGE_DRAW = 6 "),
    (M, "MP_AGE_BASE outfield 28->29", "MP_AGE_BASE = (0x1C, 0x1F)", "MP_AGE_BASE = (0x1D, 0x1F)"),
    (M, "MP_AGE_BASE keeper 31->30", "MP_AGE_BASE = (0x1C, 0x1F)", "MP_AGE_BASE = (0x1C, 0x1E)"),
    (M, "make_player age a/b swapped", "r[A.AGE] = (MP_AGE_BASE[gk] - b + a) & 0xFF", "r[A.AGE] = (MP_AGE_BASE[gk] - a + b) & 0xFF"),
    (M, "PEAK_DRAW 3->4", "PEAK_DRAW = 3 ", "PEAK_DRAW = 4 "),
    (M, "peak a/b swapped", "r[A.PEAK] = (A.PEAK_BASE[gk] + b - a) & 0xFF", "r[A.PEAK] = (A.PEAK_BASE[gk] + a - b) & 0xFF"),
    (M, "POOL_RATING_DRAW 10->9", "POOL_RATING_DRAW = 10 ", "POOL_RATING_DRAW = 9 "),
    (M, "POOL_RATING_CUT 10->9", "POOL_RATING_CUT = 10 ", "POOL_RATING_CUT = 9 "),
    (M, "RATING_OFFSET 0x7F->0x80", "RATING_OFFSET = 0x7F ", "RATING_OFFSET = 0x80 "),
    (M, "flag branches swapped", "    if flag:                                                  # 975E-9771",
     "    if not flag:                                              # 975E-9771"),
    (M, "MORALE_DRAW 32->31", "MORALE_DRAW = 0x20 ", "MORALE_DRAW = 0x1F "),
    (M, "PERFORMANCE_INIT 0x7FFF->0x7FFE", "PERFORMANCE_INIT = 0x7FFF ", "PERFORMANCE_INIT = 0x7FFE "),
    (M, "make_player club position not copied to +6", "    r[POSITION] = club_position                               # 9700-970A",
     "    r[POSITION] = record[POSITION]                            # 9700-970A"),
    (M, "make_player gk from the record, not the argument", "    gk = 1 if club_position == 0 else 0                       # 9736-9746, 32C3-32D3",
     "    gk = 1 if record[A.CLUB_POSITION] == 0 else 0              # 9736-9746, 32C3-32D3"),
    (M, "morale drawn before the ability (order; expected equivalent: 32EB draws nothing)", "    r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 979C\n    r[MORALE], w = draw(w, MORALE_DRAW)",
     "    r[MORALE], w = draw(w, MORALE_DRAW)\n    r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 979C"),
    (M, "tactics clears +0xF first", "    r[TACTICS] = (r[TACTICS] | s) & ~c & 0xFF", "    r[TACTICS] = s & ~c & 0xFF"),
    # review round 2 R1: make_player's carried bytes
    (M, "make_player writes +0x8 (carried byte zeroed)", "    r = bytearray(record)\n    r[A.COUNTRY] = country", "    r = bytearray(record)\n    r[8] = 0\n    r[A.COUNTRY] = country"),
    (M, "make_player writes +0x9 (carried byte zeroed)", "    r = bytearray(record)\n    r[A.COUNTRY] = country", "    r = bytearray(record)\n    r[9] = 0\n    r[A.COUNTRY] = country"),
    (M, "make_player writes +0xA (carried byte zeroed)", "    r = bytearray(record)\n    r[A.COUNTRY] = country", "    r = bytearray(record)\n    r[10] = 0\n    r[A.COUNTRY] = country"),
    (M, "make_player writes +0xB (carried byte zeroed)", "    r = bytearray(record)\n    r[A.COUNTRY] = country", "    r = bytearray(record)\n    r[11] = 0\n    r[A.COUNTRY] = country"),
    (M, "make_player writes +0x10 (carried byte zeroed)", "    r = bytearray(record)\n    r[A.COUNTRY] = country", "    r = bytearray(record)\n    r[16] = 0\n    r[A.COUNTRY] = country"),
    # tactics 3431
    (M, "HARDNESS_LIMIT 4->5", "HARDNESS_LIMIT = 4 ", "HARDNESS_LIMIT = 5 "),
    (M, "HARDNESS_LIMIT 4->3", "HARDNESS_LIMIT = 4 ", "HARDNESS_LIMIT = 3 "),
    (M, "OVERRIDE_BIT 0x80->0x40", "OVERRIDE_BIT = 0x80 ", "OVERRIDE_BIT = 0x40 "),
    (M, "TACKLE_BIT 0x08->0x04", "TACKLE_BIT = 0x08 ", "TACKLE_BIT = 0x04 "),
    (M, "BACK_POSITIONS drop 4", "frozenset({0, 1, 3, 4})", "frozenset({0, 1, 3})"),
    (M, "BACK_POSITIONS add 5", "frozenset({0, 1, 3, 4})", "frozenset({0, 1, 3, 4, 5})"),
    (M, "BACK_BITS drop element 1", "BACK_BITS = 0x10 | 0x01 ", "BACK_BITS = 0x10 "),
    (M, "CENTRE_BACK 2->3", "CENTRE_BACK = 2 ", "CENTRE_BACK = 3 "),
    (M, "CENTRE_BACK_PROFILE 14->13", "CENTRE_BACK_PROFILE = 0x0E ", "CENTRE_BACK_PROFILE = 0x0D "),
    (M, "CENTRE_BACK_BITS drop element 2", "CENTRE_BACK_BITS = 0x20 | 0x02 ", "CENTRE_BACK_BITS = 0x20 "),
    (M, "hardness without the rating bit", "return (record[A.PROFILE] - (record[A.RATING] & 1)) & 0xFF", "return record[A.PROFILE] & 0xFF"),
    # fitness 3558
    (M, "FITNESS_BASE young 16->15", "FITNESS_BASE = (0x10, 0x0D)", "FITNESS_BASE = (0x0F, 0x0D)"),
    (M, "FITNESS_BASE old 13->14", "FITNESS_BASE = (0x10, 0x0D)", "FITNESS_BASE = (0x10, 0x0E)"),
    (M, "FITNESS_OLD_MARGIN 4->3", "FITNESS_OLD_MARGIN = 4 ", "FITNESS_OLD_MARGIN = 3 "),
    (M, "FITNESS_OLD_MARGIN 4->5", "FITNESS_OLD_MARGIN = 4 ", "FITNESS_OLD_MARGIN = 5 "),
    (M, "FITNESS_CAP 32->31", "FITNESS_CAP = 0x20 ", "FITNESS_CAP = 0x1F "),
    (M, "FITNESS_FLOOR 1->0", "FITNESS_FLOOR = 1 ", "FITNESS_FLOOR = 0 "),
    (M, "FITNESS_FLOOR 1->2", "FITNESS_FLOOR = 1 ", "FITNESS_FLOOR = 2 "),
    (M, "computer branch draws 3T", "        r, w = draw(w, 2 * t)", "        r, w = draw(w, 3 * t)"),
    (M, "managed branch a/b swapped", "        v = t + b - a", "        v = t + a - b"),
    (M, "managed branch draws T, not T + 1", "        a, w = draw(w, t + 1)", "        a, w = draw(w, t)"),
    (M, "energy after the floor", "    return max(v, FITNESS_FLOOR) & 0xFF, v & 0xFF, w", "    return max(v, FITNESS_FLOOR) & 0xFF, max(v, FITNESS_FLOOR) & 0xFF, w"),
    # 7E80 and the initial
    (M, "RECREATE_AGE_DRAW 6->5", "RECREATE_AGE_DRAW = 6 ", "RECREATE_AGE_DRAW = 5 "),
    (M, "re-create age a/b swapped", "r[A.AGE] = (A.RECREATE_AGE_BASE[gk] + b - a) & 0xFF", "r[A.AGE] = (A.RECREATE_AGE_BASE[gk] + a - b) & 0xFF"),
    (M, "re-create keeps make_player's ability", "    r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 7F01", "    pass                                                      # 7F01"),
    (M, "re-create keeps the caps", "    r[A.CAPS] = r[A.CAPS + 1] = 0                             # 7F09", "    pass                                                      # 7F09"),
    (M, "re-create keeps the goals", "    r[A.GOALS] = r[A.GOALS + 1] = 0                           # 7F12", "    pass                                                      # 7F12"),
    (M, "re-create keeps the status", "    r[A.STATUS] = 0                                           # 7F19", "    pass                                                      # 7F19"),
    (M, "re-create does not restore +6", "    r[POSITION] = old[POSITION]                               # 7E9D-7EA3 saved, 7F30-7F36",
     "    pass                                                      # 7E9D-7EA3 saved, 7F30-7F36"),
    (M, "re-create takes the managed fitness branch", "rating, False, w)  # 7EA6-7EC0", "rating, True, w)  # 7EA6-7EC0"),
    (M, "INITIAL_LETTERS W->X", 'INITIAL_LETTERS = b"ABCDEFGHIJKLMNOPRSTVW"', 'INITIAL_LETTERS = b"ABCDEFGHIJKLMNOPRSTVX"'),
    (M, "INITIAL_LETTERS with Q (22 letters)", 'INITIAL_LETTERS = b"ABCDEFGHIJKLMNOPRSTVW"', 'INITIAL_LETTERS = b"ABCDEFGHIJKLMNOPQRSTVW"'),
    (M, "initial indexed from 1", "return INITIAL_LETTERS[r - 1], w", "return INITIAL_LETTERS[r % len(INITIAL_LETTERS)], w"),
    # 54F0
    (M, "MANAGED_AGE_BASE outfield 25->26 (the R7 table: 0x76 would give 17)", "MANAGED_AGE_BASE = (0x19, 0x1C)", "MANAGED_AGE_BASE = (0x1A, 0x1C)"),
    (M, "MANAGED_AGE_BASE keeper 28->29", "MANAGED_AGE_BASE = (0x19, 0x1C)", "MANAGED_AGE_BASE = (0x19, 0x1D)"),
    (M, "MANAGED_AGE_BASE = DS:0x76 (R7)", "MANAGED_AGE_BASE = (0x19, 0x1C)", "MANAGED_AGE_BASE = (0x11, 0x14)"),
    (M, "YOUNG_BASE outfield 17->18", "YOUNG_BASE = (0x11, 0x14)", "YOUNG_BASE = (0x12, 0x14)"),
    (M, "YOUNG_BASE keeper 20->21", "YOUNG_BASE = (0x11, 0x14)", "YOUNG_BASE = (0x11, 0x15)"),
    (M, "YOUNG_MARGIN 4->3", "YOUNG_MARGIN = 4 ", "YOUNG_MARGIN = 3 "),
    (M, "YOUNG_MARGIN 4->5", "YOUNG_MARGIN = 4 ", "YOUNG_MARGIN = 5 "),
    (M, "YOUNG_QUOTA 20->19", "YOUNG_QUOTA = 0x14 ", "YOUNG_QUOTA = 0x13 "),
    (M, "YOUNG_QUOTA 20->21", "YOUNG_QUOTA = 0x14 ", "YOUNG_QUOTA = 0x15 "),
    (M, "YOUNG_DRAW 3->4", "YOUNG_DRAW = 3 ", "YOUNG_DRAW = 4 "),
    (M, "young test <= (560F/561F jge)", "    return rec[A.AGE] < YOUNG_BASE", "    return rec[A.AGE] <= YOUNG_BASE"),
    (M, "54F0 does not count the new record", "+ (1 if young(r) else 0)", "+ 0"),
    (M, "54F0 takes the unmanaged fitness branch", "rating, True, w)  # 550E-5534", "rating, False, w)  # 550E-5534"),
    # 97CC / 98C4
    (M, "SQUAD_SLOTS 20->19", "SQUAD_SLOTS = 20 ", "SQUAD_SLOTS = 19 "),
    (M, "POOL_POSITIONS 14->13", "POOL_POSITIONS = 14 ", "POOL_POSITIONS = 13 "),
    (M, "POOL_PER_POSITION 4->3", "POOL_PER_POSITION = 4 ", "POOL_PER_POSITION = 3 "),
    (M, "POOL_AGE_BASE outfield 17->18", "POOL_AGE_BASE = (0x11, 0x14)", "POOL_AGE_BASE = (0x12, 0x14)"),
    (M, "POOL_AGE_BASE keeper 20->21", "POOL_AGE_BASE = (0x11, 0x14)", "POOL_AGE_BASE = (0x11, 0x15)"),
    (M, "POOL_AGE_DRAW 3->2", "POOL_AGE_DRAW = 3 ", "POOL_AGE_DRAW = 2 "),
    (M, "POOL_EXTRA_SLOTS 6..9 -> 6..8", "POOL_EXTRA_SLOTS = (6, 9)", "POOL_EXTRA_SLOTS = (6, 8)"),
    (M, "POOL_EXTRA_SLOTS 6..9 -> 5..8", "POOL_EXTRA_SLOTS = (6, 9)", "POOL_EXTRA_SLOTS = (5, 8)"),
    (M, "new game seed = country + 1", "w, out = country & 0xFFFF, []", "w, out = (country + 1) & 0xFFFF, []"),
    # country_rating
    (M, "CONTINENT_WEIGHT 5->4", "CONTINENT_WEIGHT = 5 ", "CONTINENT_WEIGHT = 4 "),
    (M, "CONTINENT_RANKS 0x21->0x20", "CONTINENT_RANKS = 0x21 ", "CONTINENT_RANKS = 0x20 "),
    (M, "WORLD_RANKS 0x81->0x80", "WORLD_RANKS = 0x81 ", "WORLD_RANKS = 0x80 "),
    (M, "RATING_DIVISOR 2->3", "RATING_DIVISOR = 2 ", "RATING_DIVISOR = 3 "),
    (M, "floor divide (not toward zero)", "    q = abs(a) // RATING_DIVISOR\n    return q if a >= 0 else -q", "    return a // RATING_DIVISOR"),
    (M, "world rank subtraction reversed (R6)", "+ (WORLD_RANKS - world_rank))", "+ (world_rank - WORLD_RANKS))"),
    # the contract
    (M, "contract: fitness lower bound T + 1 -> T", "FITNESS: (t_lo + 1, min(3 * t_hi, FITNESS_CAP))", "FITNESS: (t_lo, min(3 * t_hi, FITNESS_CAP))"),
    (M, "contract: energy not tied to fitness", '"same_as": {ENERGY: FITNESS}', '"same_as": {}'),
    (M, "contract: +6 not carried", "             POSITION: old[POSITION],\n", ""),
    (M, "contract: +0x11 zeroed (it is carried)", "A.SCORER_COUNT: old[A.SCORER_COUNT],", "A.SCORER_COUNT: 0,"),
    (M, "contract: rating domain from 0", "rng[A.RATING] = ((1 + RATING_OFFSET) & 0xFF,", "rng[A.RATING] = ((0 + RATING_OFFSET) & 0xFF,"),
    (M, "NOT_IN_CAPTURES drops +6", '    POSITION: "+6 = the retiree', '    0x66: "+6 = the retiree'),
    # ageing.py's constants that the re-create uses (F016)
    (G, "RECREATE_AGE_BASE outfield 25->26", "RECREATE_AGE_BASE = (0x19, 0x1C)", "RECREATE_AGE_BASE = (0x1A, 0x1C)"),
    (G, "RECREATE_AGE_BASE keeper 28->29", "RECREATE_AGE_BASE = (0x19, 0x1C)", "RECREATE_AGE_BASE = (0x19, 0x1D)"),
    (G, "RECREATE_AGE_SPREAD 5->4", "RECREATE_AGE_SPREAD = 5 ", "RECREATE_AGE_SPREAD = 4 "),
    (G, "PEAK_BASE outfield 27->28", "PEAK_BASE = (0x1B, 0x1E)", "PEAK_BASE = (0x1C, 0x1E)"),
    (G, "PEAK_BASE keeper 30->31", "PEAK_BASE = (0x1B, 0x1E)", "PEAK_BASE = (0x1B, 0x1F)"),
    (G, "PEAK_SPREAD 2->1", "PEAK_SPREAD = 2 ", "PEAK_SPREAD = 1 "),
    (G, "PROFILE_RANGE 1..16 -> 1..15", "PROFILE_RANGE = (1, 16)", "PROFILE_RANGE = (1, 15)"),
    (G, "RETIRE_LIMIT outfield 30->31", "RETIRE_LIMIT = (0x1E, 0x21)", "RETIRE_LIMIT = (0x1F, 0x21)"),
    (G, "RETIRE_LIMIT keeper 33->32", "RETIRE_LIMIT = (0x1E, 0x21)", "RETIRE_LIMIT = (0x1E, 0x20)"),
    (G, "RETIRE_PEAK_MARGIN 5->6", "RETIRE_PEAK_MARGIN = 5 ", "RETIRE_PEAK_MARGIN = 6 "),
    (G, "shim breaks the top-level import (R9)", "    except ImportError:\n        import recreate as _r", "    except ImportError:\n        from runtime.model import recreate as _r"),
    # the checker (R1-R3)
    (K, "undecided: a record matching neither accepted as a re-create (R1)", "    if not repl:\n        return \"recreate\", []", "    if True:\n        return \"recreate\", []"),
    (K, "undecided continuing with caps 0 accepted", "        if C.caps_word(new) == 0:", "        if C.caps_word(new) == 0 and False:"),
    (K, "decided always (undecided caps clause ignored)", "decided = caps_lo > 0 or fire_lo == fire_zero", "decided = True"),
    (K, "per-country rating check off (R1)", "        if len(ratings) > 1:", "        if len(ratings) > 99:"),
    (K, "surname check off (R2)", "    if name_new[0] != name_old[0]:", "    if False:"),
    (K, "initial table check off (R2)", "    if len(ini) != 1 or ini[0] not in c[\"initial\"]:", "    if False:"),
    (K, "exact bytes off (R3)", "        if off not in R.NOT_IN_CAPTURES and new[off] != want:", "        if False:"),
    (K, "range checks off (R3)", "    for off, (lo, hi) in sorted(c[\"range\"].items()):", "    for off, (lo, hi) in []:"),
    (K, "energy = fitness check off (R3)", "    for off, other in sorted(c[\"same_as\"].items()):", "    for off, other in []:"),
    (K, "tactics bits check off (R3)", "    if new[R.TACTICS] & must != must or new[R.TACTICS] & clear:", "    if False:"),
    (K, "ability of its own bytes off", "    if new[A.ABILITY] != A.compute_ability(new[A.AGE], new[A.PEAK], new[A.RATING]):", "    if False:"),
    (K, "exact check: a pair with no RNG word accepted", "        if not hits:", "        if False:"),
    (K, "exact check never applied", "    elif sorted(nb) != list(range(1, len(nb) + 1)):", "    elif True:"),
    (K, "exact check: morale not compared", "DRAWN = (A.AGE, A.PEAK, A.ABILITY, A.PROFILE, R.MORALE, R.FITNESS, R.ENERGY)", "DRAWN = (A.AGE, A.PEAK, A.ABILITY, A.PROFILE, R.FITNESS, R.ENERGY)"),
    (K, "exact check: age not compared", "DRAWN = (A.AGE, A.PEAK, A.ABILITY, A.PROFILE, R.MORALE, R.FITNESS, R.ENERGY)", "DRAWN = (A.PEAK, A.ABILITY, A.PROFILE, R.MORALE, R.FITNESS, R.ENERGY)"),
    (K, "exact check: ability not compared (expected equivalent: the contract checks +4 of +1/+2/+3)", "DRAWN = (A.AGE, A.PEAK, A.ABILITY, A.PROFILE, R.MORALE, R.FITNESS, R.ENERGY)", "DRAWN = (A.AGE, A.PEAK, A.PROFILE, R.MORALE, R.FITNESS, R.ENERGY)"),
    (K, "exact check: initial not compared", "            if gi != ini or any(", "            if any("),
    (K, "exact check: half the RNG words", "SEEDS = 0x10000 ", "SEEDS = 0x8000 "),
    (K, "exact check in the first capture's slot order", "        slot = {w: i for i, w in enumerate(ca.get(\"squad\", []), 1)}", "        slot = {w: i for i, w in enumerate(cb.get(\"squad\", []), 1)}"),
    (K, "+6 checked too (expected equivalent on E014: every re-create kept the capture's +6)", "        if off not in R.NOT_IN_CAPTURES and new[off] != want:", "        if off != 3 and new[off] != want:"),
    (K, "3431's +6 taken as the record's +6 (expected equivalent on E014: +6 = +7 in every re-create)", "    seen[R.POSITION] = new[A.CLUB_POSITION]", "    seen[R.POSITION] = new[R.POSITION]"),
    (K, "zero comparisons accepted", "    if total == 0:\n        mismatches.append", "    if total < 0:\n        mismatches.append"),
    (K, "no re-create accepted", "    elif made == 0:", "    elif made < 0:"),
    (K, "exit 0 with mismatches", "    ok = not mismatches and made > 0", "    ok = made > 0"),
]


def clear_cache():
    for d in ("runtime", "experiments", "tests"):
        for p in (ROOT / d).rglob("__pycache__"):
            shutil.rmtree(p, ignore_errors=True)


def run_tests():
    try:
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_model_recreate"],
                           cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, f"timeout after {TIMEOUT} s", []
    tail = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "FAILED", "OK"))]
    failing = sorted({l.split()[1] for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))})
    return r.returncode, " ".join(tail), failing


def main():
    files = sorted({f for f, *_ in MUTATIONS})
    originals = {f: (ROOT / f).read_text() for f in files}
    digests = {f: hashlib.sha256(t.encode()).hexdigest() for f, t in originals.items()}

    def restore(*_):
        for f, t in originals.items():
            (ROOT / f).write_text(t)
        clear_cache()

    signal.signal(signal.SIGINT, lambda *a: (restore(), sys.exit(130)))
    signal.signal(signal.SIGTERM, lambda *a: (restore(), sys.exit(143)))
    rc, tail, _ = run_tests()
    print(f"baseline: rc {rc} {tail}", flush=True)
    if rc != 0:
        return 1
    counts = {"KILLED": 0, "SURVIVED": 0, "TIMEOUT": 0, "BAD": 0}
    try:
        for f, mid, old, new in MUTATIONS:
            text = originals[f]
            if text.count(old) != 1:
                print(f"BAD MUTATION ({text.count(old)} matches)\t{f}\t{mid}", flush=True)
                counts["BAD"] += 1
                continue
            (ROOT / f).write_text(text.replace(old, new))
            clear_cache()
            try:
                rc, tail, failing = run_tests()
            finally:
                (ROOT / f).write_text(text)
                clear_cache()
            status = "TIMEOUT" if rc is None else "KILLED" if rc != 0 else "SURVIVED"
            counts[status] += 1
            print(f"{status}\t{Path(f).name}\t{mid}\t{tail}\t{', '.join(failing[:4])}", flush=True)
    finally:
        restore()
    for f, t in originals.items():
        assert hashlib.sha256((ROOT / f).read_text().encode()).hexdigest() == digests[f], f
    print(f"restored: {', '.join(f'{f} sha256 {d[:12]}' for f, d in digests.items())}")
    print("mutations: " + ", ".join(f"{v} {k.lower()}" for k, v in counts.items()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
