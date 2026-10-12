#!/usr/bin/env python3
"""In-place mutation sweep for T28 (Done-when 2): edit the file, clear __pycache__, run the
unit tests in a fresh interpreter, restore the original in `finally` (and on SIGINT/SIGTERM).

    python3 experiments/E014-q013-ageing/mutation_sweep.py

Each line: KILLED/SURVIVED, the file, the mutation, the test run's tail and the failing tests.
The survivors are the four compute_ability mutants that mutation_equivalence.py shows equal to
the model on every byte triple. The committed outputs are under mutations/."""
import hashlib
import shutil
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M = "runtime/model/ageing.py"
R = "runtime/model/recreate.py"
K = "experiments/E014-q013-ageing/check_ageing.py"

MUTATIONS = [
    # (file, id, old, new) — old must occur exactly once
    (M, "COUNTRY 0x00->0x01", "COUNTRY = 0x00 ", "COUNTRY = 0x01 "),
    (M, "AGE 0x01->0x02", "AGE = 0x01 ", "AGE = 0x02 "),
    (M, "PEAK 0x02->0x03", "PEAK = 0x02 ", "PEAK = 0x03 "),
    (M, "PEAK 0x02->0x0A", "PEAK = 0x02 ", "PEAK = 0x0A "),
    (M, "RATING 0x03->0x04", "RATING = 0x03 ", "RATING = 0x04 "),
    (M, "RATING 0x03->0x0B", "RATING = 0x03 ", "RATING = 0x0B "),
    (M, "ABILITY 0x04->0x05", "ABILITY = 0x04 ", "ABILITY = 0x05 "),
    (M, "PROFILE 0x05->0x06", "PROFILE = 0x05 ", "PROFILE = 0x06 "),
    (M, "CLUB_POSITION 0x07->0x06", "CLUB_POSITION = 0x07 ", "CLUB_POSITION = 0x06 "),
    (M, "CAPS 0x08->0x0A", "CAPS = 0x08 ", "CAPS = 0x0A "),
    (M, "GOALS 0x0A->0x0B", "GOALS = 0x0A ", "GOALS = 0x0B "),
    (M, "STATUS 0x10->0x0F", "STATUS = 0x10 ", "STATUS = 0x0F "),
    (M, "SCORER_COUNT 0x11->0x10", "SCORER_COUNT = 0x11 ", "SCORER_COUNT = 0x10 "),
    (M, "PERFORMANCE 0x12->0x13", "PERFORMANCE = 0x12 ", "PERFORMANCE = 0x13 "),
    (M, "AGEING_STAGES drop 7", "frozenset({2, 3, 5, 7})", "frozenset({2, 3, 5})"),
    (M, "AGEING_STAGES add 4", "frozenset({2, 3, 5, 7})", "frozenset({2, 3, 4, 5, 7})"),
    (M, "STAGE_RANGE hi 8->9", "STAGE_RANGE = (2, 8)", "STAGE_RANGE = (2, 9)"),
    (M, "STAGE_RANGE lo 2->1", "STAGE_RANGE = (2, 8)", "STAGE_RANGE = (1, 8)"),
    (M, "PEAK_BAND 3->2", "PEAK_BAND = 3 ", "PEAK_BAND = 2 "),
    (M, "PEAK_BAND 3->4", "PEAK_BAND = 3 ", "PEAK_BAND = 4 "),
    (M, "BELOW_DIVISOR 2->1", "BELOW_DIVISOR = 2 ", "BELOW_DIVISOR = 1 "),
    (M, "BELOW_DIVISOR 2->3", "BELOW_DIVISOR = 2 ", "BELOW_DIVISOR = 3 "),
    (M, "FACTOR_BASE 0x10->0x11", "FACTOR_BASE = 0x10 ", "FACTOR_BASE = 0x11 "),
    (M, "FACTOR_BASE 0x10->0x0F", "FACTOR_BASE = 0x10 ", "FACTOR_BASE = 0x0F "),
    (M, "ABILITY_DIVISOR 16->15", "ABILITY_DIVISOR = 16 ", "ABILITY_DIVISOR = 15 "),
    (M, "ABILITY_DIVISOR 16->32", "ABILITY_DIVISOR = 16 ", "ABILITY_DIVISOR = 32 "),
    (M, "RETIRE_LIMIT outfield 30->31", "RETIRE_LIMIT = (0x1E, 0x21)", "RETIRE_LIMIT = (0x1F, 0x21)"),
    (M, "RETIRE_LIMIT keeper 33->34", "RETIRE_LIMIT = (0x1E, 0x21)", "RETIRE_LIMIT = (0x1E, 0x22)"),
    (M, "RETIRE_LIMIT swapped", "RETIRE_LIMIT = (0x1E, 0x21)", "RETIRE_LIMIT = (0x21, 0x1E)"),
    (M, "RETIRE_PEAK_MARGIN 5->4", "RETIRE_PEAK_MARGIN = 5 ", "RETIRE_PEAK_MARGIN = 4 "),
    (M, "RETIRE_PEAK_MARGIN 5->6", "RETIRE_PEAK_MARGIN = 5 ", "RETIRE_PEAK_MARGIN = 6 "),
    (M, "RECREATE_AGE_BASE outfield 25->26", "RECREATE_AGE_BASE = (0x19, 0x1C)", "RECREATE_AGE_BASE = (0x1A, 0x1C)"),
    (M, "RECREATE_AGE_BASE keeper 28->29", "RECREATE_AGE_BASE = (0x19, 0x1C)", "RECREATE_AGE_BASE = (0x19, 0x1D)"),
    (M, "RECREATE_AGE_SPREAD 5->4", "RECREATE_AGE_SPREAD = 5 ", "RECREATE_AGE_SPREAD = 4 "),
    (M, "RECREATE_AGE_SPREAD 5->6", "RECREATE_AGE_SPREAD = 5 ", "RECREATE_AGE_SPREAD = 6 "),
    (M, "PEAK_BASE outfield 27->28", "PEAK_BASE = (0x1B, 0x1E)", "PEAK_BASE = (0x1C, 0x1E)"),
    (M, "PEAK_BASE keeper 30->31", "PEAK_BASE = (0x1B, 0x1E)", "PEAK_BASE = (0x1B, 0x1F)"),
    (M, "PEAK_SPREAD 2->3", "PEAK_SPREAD = 2 ", "PEAK_SPREAD = 3 "),
    (M, "PEAK_SPREAD 2->1", "PEAK_SPREAD = 2 ", "PEAK_SPREAD = 1 "),
    (M, "PROFILE_RANGE lo 1->0", "PROFILE_RANGE = (1, 16)", "PROFILE_RANGE = (0, 16)"),
    (M, "PROFILE_RANGE hi 16->15", "PROFILE_RANGE = (1, 16)", "PROFILE_RANGE = (1, 15)"),
    (M, "SKILL_DIVISOR 32->31", "SKILL_DIVISOR = 32 ", "SKILL_DIVISOR = 31 "),
    (M, "SKILL_STRIDE 12->11", "SKILL_STRIDE = 12 ", "SKILL_STRIDE = 11 "),
    (M, "SKILL_ELEMENTS 12->11", "SKILL_ELEMENTS = 12 ", "SKILL_ELEMENTS = 11 "),
    # branch directions and operators of compute_ability (3313 jb, 332E jg, 3366 jle)
    (M, "band upper <= -> <", "if peak <= age <= peak + PEAK_BAND:", "if peak <= age < peak + PEAK_BAND:"),
    (M, "band lower <= -> < (expected equivalent: k = 0 at a = p)", "if peak <= age <= peak + PEAK_BAND:", "if peak < age <= peak + PEAK_BAND:"),
    (M, "band lower <= -> >=", "if peak <= age <= peak + PEAK_BAND:", "if peak >= age and age <= peak + PEAK_BAND:"),
    (M, "above > -> < (direction)", "    if age > peak + PEAK_BAND:   ", "    if age < peak + PEAK_BAND:   "),
    (M, "above > -> >= (expected equivalent: equality is in the band)", "    if age > peak + PEAK_BAND:   ", "    if age >= peak + PEAK_BAND:   "),
    (M, "below k sign (a - p)", "k = (peak - age) // BELOW_DIVISOR", "k = (age - peak) // BELOW_DIVISOR"),
    (M, "above k = a - p", "k = age - (peak + PEAK_BAND)", "k = age - peak"),
    (M, "copy branch returns the ability, not the rating", "        return rating & 0xFF ", "        return (rating * 15 // 16) & 0xFF "),
    (M, "drop the stored-byte mask (33C3 al)", "// ABILITY_DIVISOR & 0xFF  #", "// ABILITY_DIVISOR  #"),
    (M, "drop the product mask (expected equivalent: 65536/16 = 4096 is a multiple of 256)", "* factor) & 0xFFFF) // ABILITY_DIVISOR", "* factor)) // ABILITY_DIVISOR"),
    (M, "drop the factor word mask (expected equivalent: & 0xFFFF of the product folds it)", "factor = (FACTOR_BASE - k) & 0xFFFF", "factor = FACTOR_BASE - k"),
    (M, "rating operand mask dropped (above)", "return (((rating & 0xFF) * factor)", "return (((rating) * factor)"),
    (M, "rating operand mask dropped (copy)", "        return rating & 0xFF ", "        return rating "),
    # retirement 7F40
    (M, "limit < -> <= (7F78 jae)", "if RETIRE_LIMIT[gk] < record[AGE] and caps == 0:", "if RETIRE_LIMIT[gk] <= record[AGE] and caps == 0:"),
    (M, "limit < -> > (direction)", "if RETIRE_LIMIT[gk] < record[AGE] and caps == 0:", "if RETIRE_LIMIT[gk] > record[AGE] and caps == 0:"),
    (M, "caps == 0 -> != 0", "if RETIRE_LIMIT[gk] < record[AGE] and caps == 0:", "if RETIRE_LIMIT[gk] < record[AGE] and caps != 0:"),
    (M, "and -> or", "if RETIRE_LIMIT[gk] < record[AGE] and caps == 0:", "if RETIRE_LIMIT[gk] < record[AGE] or caps == 0:"),
    (M, "peak clause > -> >= (7F9D jg)", "return 1 if record[AGE] > record[PEAK] + RETIRE_PEAK_MARGIN else 0", "return 1 if record[AGE] >= record[PEAK] + RETIRE_PEAK_MARGIN else 0"),
    (M, "peak clause > -> < (direction)", "return 1 if record[AGE] > record[PEAK] + RETIRE_PEAK_MARGIN else 0", "return 1 if record[AGE] < record[PEAK] + RETIRE_PEAK_MARGIN else 0"),
    (M, "gk test inverted (7F5D)", "    gk = 1 if record[CLUB_POSITION] == 0 else 0  # 7F5D-7F6A", "    gk = 0 if record[CLUB_POSITION] == 0 else 1  # 7F5D-7F6A"),
    (M, "caps low byte only", "caps = record[CAPS] | (record[CAPS + 1] << 8)", "caps = record[CAPS]"),
    (M, "R5: flag on the record before the increment", '"retires": retirement_flag(aged)', '"retires": retirement_flag(record)'),
    # the first pass
    (M, "age increment +2", "out[AGE] = (record[AGE] + 1) & 0xFF", "out[AGE] = (record[AGE] + 2) & 0xFF"),
    (M, "age wrap mask dropped", "out[AGE] = (record[AGE] + 1) & 0xFF", "out[AGE] = record[AGE] + 1"),
    (M, "ability from the old age", "out[ABILITY] = compute_ability(out[AGE], record[PEAK], record[RATING])", "out[ABILITY] = compute_ability(record[AGE], record[PEAK], record[RATING])"),
    (M, "+0x11 not cleared", "    out[SCORER_COUNT] = 0                ", "    out[SCORER_COUNT] = record[SCORER_COUNT]"),
    (M, "player 0 ages", "    if player == 0:\n        return {SCORER_COUNT: 0}", "    if player == -1:\n        return {SCORER_COUNT: 0}"),
    (M, "seed consumed (a variance term)", "return {AGE: aged[AGE], ABILITY: aged[ABILITY]", "return {AGE: aged[AGE], ABILITY: (aged[ABILITY] + (seed % 2)) & 0xFF"),
    # re-create 7E80
    # recreate_constraints lives in recreate.py since T30 (fix #102); the contract function above
    # it repeats some lines, so each old text spans into recreate_constraints' own next line.
    (R, "re-create gk inverted", "    gk = 1 if old[A.CLUB_POSITION] == 0 else 0\n    exact = {A.COUNTRY: old[A.COUNTRY], A.CLUB_POSITION: old[A.CLUB_POSITION],\n             A.CAPS: 0", "    gk = 0 if old[A.CLUB_POSITION] == 0 else 1\n    exact = {A.COUNTRY: old[A.COUNTRY], A.CLUB_POSITION: old[A.CLUB_POSITION],\n             A.CAPS: 0"),
    (R, "re-create performance bytes swapped", "A.PERFORMANCE: 0xFF, A.PERFORMANCE + 1: 0x7F", "A.PERFORMANCE: 0x7F, A.PERFORMANCE + 1: 0xFF"),
    (R, "re-create keeps country dropped", "exact = {A.COUNTRY: old[A.COUNTRY], A.CLUB_POSITION: old[A.CLUB_POSITION],\n             A.CAPS: 0", "exact = {A.CLUB_POSITION: old[A.CLUB_POSITION],\n             A.CAPS: 0"),
    (R, "re-create keeps +7 dropped", "A.CLUB_POSITION: old[A.CLUB_POSITION],\n             A.CAPS: 0", "\n             A.CAPS: 0"),
    # derived skills 3A06
    (M, "skills (ability + 1) -> ability", "(t * ((ability + 1) & 0xFFFF))", "(t * (ability & 0xFFFF))"),
    # the checker (R1-R4)
    (K, "MANAGED_ABOVE 0x80->0x7F", "MANAGED_ABOVE = 0x80 ", "MANAGED_ABOVE = 0x7F "),
    (K, "SQUAD_SIZE 20->19", "SQUAD_SIZE = 20 ", "SQUAD_SIZE = 19 "),
    (K, "continuing invariants drop +7", "CONTINUING_SAME = (A.COUNTRY, A.PEAK, A.RATING, A.PROFILE, A.CLUB_POSITION)", "CONTINUING_SAME = (A.COUNTRY, A.PEAK, A.RATING, A.PROFILE)"),
    (K, "decided always (undecided caps clause ignored)", "decided = caps_lo > 0 or fire_lo == fire_zero", "decided = True"),
    (K, "undecided continuing with caps 0 accepted", "if caps_word(new) == 0:", "if caps_word(new) == 0 and False:"),
    (K, "per-country rating check off", "if len(ratings) > 1:", "if len(ratings) > 99:"),
    (K, "zero comparisons accepted (R4)", "    if total == 0:\n", "    if total < 0:\n"),
    (K, "completed record without a pair accepted (R4)", 'if status == "completed":', 'if status == "never":'),
    (K, "no record accepted (R4)", "    if not paths:\n", "    if paths is None:\n"),
    (K, "squad size check off (R2)", "    if len(squad) != SQUAD_SIZE or 0 in squad or len(set(squad)) != len(squad):", "    if False:"),
    (K, "missing second record accepted (R2)", "            if w not in a:\n                mismatches.append", "            if w not in a:\n                0 or mismatches.count"),
    (K, "coverage check off (R2)", "    if sorted(words) != sorted(set(squad)) or len(words) != len(set(words)):", "    if False:"),
    (K, "re-create ranges off (R3)", "    for off, (lo, hi) in sorted(c[\"range\"].items()):", "    for off, (lo, hi) in []:"),
    (K, "re-create exact bytes off (R3)", "    for off, want in sorted(c[\"exact\"].items()):", "    for off, want in []:"),
    (K, "tables check off", 'if before["tables"] != after["tables"]:', "if False:"),
    (K, "one-ageing span check off", "if ageings_between(sb, sa) != 1:", "if False:"),
    (K, "caps fall accepted", "if caps_word(new) < caps_word(rec):", "if False:"),
    (K, "exit 0 on zero comparisons", "return 0 if total > 0 and not mismatches else 1", "return 0 if not mismatches else 1"),
]


def clear_cache():
    for d in ("runtime", "experiments", "tests"):
        for p in (ROOT / d).rglob("__pycache__"):
            shutil.rmtree(p, ignore_errors=True)


def run_tests():
    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_model_ageing"],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    tail = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "FAILED", "OK"))]
    failing = sorted({l.split()[1] for l in r.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))})
    return r.returncode, " ".join(tail), failing


def main():
    originals = {f: (ROOT / f).read_text() for f in (M, R, K)}
    digests = {f: hashlib.sha256(t.encode()).hexdigest() for f, t in originals.items()}

    def restore(*_):
        for f, t in originals.items():
            (ROOT / f).write_text(t)
        clear_cache()

    signal.signal(signal.SIGINT, lambda *a: (restore(), sys.exit(130)))
    signal.signal(signal.SIGTERM, lambda *a: (restore(), sys.exit(143)))
    rc, tail, _ = run_tests()
    print(f"baseline: rc {rc} {tail}")
    if rc != 0:
        return 1
    killed = survived = 0
    try:
        for f, mid, old, new in MUTATIONS:
            text = originals[f]
            if text.count(old) != 1:
                print(f"BAD MUTATION ({text.count(old)} matches): {f} {mid}")
                continue
            (ROOT / f).write_text(text.replace(old, new))
            clear_cache()
            try:
                rc, tail, failing = run_tests()
            finally:
                (ROOT / f).write_text(text)
                clear_cache()
            status = "KILLED" if rc != 0 else "SURVIVED"
            killed += rc != 0
            survived += rc == 0
            print(f"{status}\t{Path(f).name}\t{mid}\t{tail}\t{', '.join(failing[:4])}")
    finally:
        restore()
    for f, t in originals.items():
        assert hashlib.sha256((ROOT / f).read_text().encode()).hexdigest() == digests[f], f
    print(f"restored: {', '.join(f'{f} sha256 {d[:12]}' for f, d in digests.items())}")
    print(f"mutations: {killed} killed, {survived} survived")
    return 0


if __name__ == "__main__":
    sys.exit(main())
