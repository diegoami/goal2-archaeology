#!/usr/bin/env python3
"""T61: one-line mutations of port/attributes.py taken one at a time in a copy; the unit tests must fail on each
(rule 9: a test proves behaviour only if it fails without the behaviour), and pass on the unmutated copy.

    python3 -B experiments/E036-match-port/out/T61/mutations.py [--all-tests] > experiments/E036-match-port/out/T61/mutations-<commit>.txt

By default only the simulator and variant tests run on a copy (fast, no emulator); `--all-tests` runs the whole module,
the differential tests against the original included, and is the second pass for the mutations the simulator misses.
The copy lives in a temporary directory under .cache/tmp; the worktree is never edited."""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
A = "runtime/original_match/port/attributes.py"
MUTATIONS = [
    ("0AA7 bonus +0x10 -> +0x11 (return)", "return ret(mem, m // 8 + 0x10, m % 8)", "return ret(mem, m // 8 + 0x11, m % 8)"),
    ("0B77 above 0x80 -> from 0x80", "managed = Rec(mem, COUNTRIES, ax).u8(0x2E) > 0x80", "managed = Rec(mem, COUNTRIES, ax).u8(0x2E) >= 0x80"),
    ("0E24 colour 0x0F -> 0x0E", "return ret(mem, (ax & 0xFF00) | 0x0F, dx)", "return ret(mem, (ax & 0xFF00) | 0x0E, dx)"),
    ("2E20 element 8 -> 7", '8, "1771:2E5D")', '7, "1771:2E5D")'),
    ("2E20 colour 5 -> 4", "return ret(mem, (ax & 0xFF00) | 5, dx)", "return ret(mem, (ax & 0xFF00) | 4, dx)"),
    ("2FAD mod 12 -> mod 11", "mem.ds8(0xE54 + n % 12)", "mem.ds8(0xE54 + n % 11)"),
    ("2FFB bit 0 -> bits 0-1", "dx = p.u8(3) & 1 ", "dx = p.u8(3) & 3 "),
    ("3041 sum 30 -> 31", "flag = total == 0x1E", "flag = total == 0x1F"),
    ("3088 mod 3 -> mod 2", "row = mem.ds8(0xE7C + n % 3)", "row = mem.ds8(0xE7C + n % 2)"),
    ("30D9 jae 0x15 -> ja", "if p.u8(1) >= 0x15:", "if p.u8(1) > 0x15:"),
    ("3216 energy below 1 -> below 0", "if energy < 1:", "if energy < 0:"),
    ("3216 element 3 -> bit 3", "(3, 2, 0x327B)", "(3, 3, 0x327B)"),
    ("3216 element 8 -> bit 6", "(8, 7, 0x324D)", "(8, 6, 0x324D)"),
    ("3A06 scale +1 -> +0", "scale = p.u8(4) + 1", "scale = p.u8(4) + 0"),
    ("3A06 divisor 0x20 -> 0x10", "divisor = 0x1F if variant == \"skill-divisor-31\" else 0x20", "divisor = 0x1F if variant == \"skill-divisor-31\" else 0x10"),
    ("3A82 20 slots -> 19", "for slot in range(1, 0x15):                             # 3AA1-3AC6", "for slot in range(1, 0x14):                             # 3AA1-3AC6"),
    ("5A03 kind +2 -> +1", "mem.u8((seg << 4) + ((off + 2) & 0xFFFF))", "mem.u8((seg << 4) + ((off + 1) & 0xFFFF))"),
    ("5A03 set DS:0F3E -> 0F3F", "mem.reg(\"ds\"), 0xF3E,", "mem.reg(\"ds\"), 0xF3F,"),
    ("33CD element 8 -> 7", 'dx, p, 0xF, 8, "1771:33F9")', 'dx, p, 0xF, 7, "1771:33F9")'),
    ("33CD clear element 4 -> 3", 'dx, p, 0xF, 4, "1771:340B")', 'dx, p, 0xF, 3, "1771:340B")'),
    ("3431 hardness below 4 -> below 3", "if (ax & 0xFF) < 4:", "if (ax & 0xFF) < 3:"),
    ("3431 element 1 -> 2", 'p, 0xF, 1, "1771:3495")', 'p, 0xF, 2, "1771:3495")'),
    ("3431 position 2 +5 below 0xE -> at most", "if p.u8(5) < 0xE:", "if p.u8(5) <= 0xE:"),
    ("3431 element 6 -> 7", 'p, 0xF, 6, "1771:34CF")', 'p, 0xF, 7, "1771:34CF")'),
    ("34E7 +0xF not cleared", 'Rec(mem, PLAYERS, ax).w8(0xF, 0, "1771:3535")', 'Rec(mem, PLAYERS, ax).w8(0xF, 0xFF, "1771:3535")'),
    ("34E7 empty slots not skipped", "        if word == 0:                                       # 351A: je 354C\n            continue\n", "        if False:\n            continue\n"),
    ("3179 the left-foot set CS:3159 -> CS:3139", "left = 0x3139 if variant == \"foot-sets-swapped\" else 0x3159", "left = 0x3139 if variant == \"foot-sets-swapped\" else 0x3139"),
    ("3179 two-footed ignored", "if not (ax & 0xFF) and foot != 0:", "if foot != 0:"),
    ("3179 xor of +6 and +7 -> and", "flag = 1 if (p6 == 0) != (p7 == 0) else 0", "flag = 1 if (p6 == 0) and (p7 == 0) else 0"),
    ("377E form threshold 0x20 -> 0x21", "if c >= 0x20:", "if c >= 0x21:"),
    ("377E clamp 0x100 -> 0xFF", "        v = 0x100\n    f.w16(-4, v,", "        v = 0xFF\n    f.w16(-4, v,"),
    ("377E no halving", "    if ax & 0xFF:                                           # 3808-380A", "    if False:                                               # 3808-380A"),
    ("2E93 separator CS:2E91 -> CS:0E6A", '"23E4:06B7", cs, 0x2E91,', '"23E4:06B7", cs, 0x0E6A,'),
    ("2E93 maximum 12 -> 5", 'dest_seg, dest_off, 0xC, ret_to="1771:2EDF")', 'dest_seg, dest_off, 5, ret_to="1771:2EDF")'),
    ("0E6C defence and midfield swapped", "counts = [f.u8(-4), f.u8(-3), f.u8(-2), f.u8(-1)]", "counts = [f.u8(-4), f.u8(-2), f.u8(-3), f.u8(-1)]"),
    ("0E6C unavailable players counted", "        if ax & 0xFF:                                       # 0EAB-0EAD: unavailable\n            continue\n", "        if False:\n            continue\n"),
    ("3E2F lower bound inclusive -> exclusive", "if oc < lo:", "if oc <= lo:"),
    ("3E2F rows 1..4 -> 1..3", "for r in range(1, 5):                                   # 3E36-3EEF", "for r in range(1, 4):                                   # 3E36-3EEF"),
    ("3E2F the marker's slot not noted", 'parent.w8(pos - 0x27, j, "1771:3EDC")', 'parent.w8(pos - 0x27, 0, "1771:3EDC")'),
    ("3EF8 slot 1's word not cleared", 'MARK_BASE + 0x28 * t + 2) & 0xFFFF), 0, "1771:3F31")', 'MARK_BASE + 0x28 * t + 2) & 0xFFFF), 1, "1771:3F31")'),
    ("3EF8 the unavailable not cleared from the opponents", "            if ax & 0xFF:                                   # 4034-4036", "            if False:                                       # 4034-4036"),
    ("3EF8 team tactic element 8 -> 7", 'mine.u8(0x2D), 8, "1771:41D4")', 'mine.u8(0x2D), 7, "1771:41D4")'),
    # The dead stack frames and registers: only the differential tests (against the original) see them.
    ("0AA7 the result local [bp - 2] wrong", "f.w16(-2, m // 8 + 0x10", "f.w16(-2, m // 8 + 0x11", "frame"),
    ("3216 the stack block: the set pushed wrong", "block[8:10] = s.to_bytes(2, \"little\")", "block[8:10] = (s ^ 1).to_bytes(2, \"little\")", "frame"),
    ("3216 DX after the elements", "    return ret(mem, result, dx) ", "    return ret(mem, result, dx ^ 1) ", "frame"),
    ("0E6C the loop variable local", "f.w16(-6, i, \"1771:0E96\" if i > 1 else \"1771:0E8F\")", "f.w16(-6, 0, \"1771:0E96\" if i > 1 else \"1771:0E8F\")", "frame"),
    ("377E DX after the wrong-foot halving", "        q, dx = idiv(s16(v), 2)                             # 380C-3813: cdq; idiv 2", "        q, dx = idiv(s16(v), 2)\n        dx = 0                                              # 380C-3813: cdq; idiv 2", "frame"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all-tests", action="store_true")
    ap.add_argument("--frames-only", action="store_true", help="only the mutations of frames and registers, with all tests")
    a = ap.parse_args()
    if a.frames_only:
        a.all_tests = True
    tests = ["tests.test_port_attributes"] if a.all_tests else ["tests.test_port_attributes.SimTests", "tests.test_port_attributes.VariantTests"]
    tmp_root = ROOT / ".cache/tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="t61-mut-", dir=tmp_root))
    try:
        for d in ("runtime", "tests", "experiments/E036-match-port/out/T61"):
            (work / d).parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ROOT / "runtime", work / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "tests", work / "tests", ignore=shutil.ignore_patterns("__pycache__"))
        (work / "experiments/E036-match-port/out/T61").mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / "experiments/E036-match-port/out/T61/diffcheck.py", work / "experiments/E036-match-port/out/T61/diffcheck.py")
        (work / ".cache").mkdir(exist_ok=True)
        (work / ".cache/dl").symlink_to(ROOT / ".cache/dl")
        target = work / A
        original = target.read_text()

        def run():
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=work, capture_output=True, text=True)
            return r.returncode, (r.stderr.strip().splitlines() or [""])[-1]
        code, last = run()
        print(f"unmutated: exit {code} ({last})")
        if code != 0:
            return 2
        missed = 0
        for name, old, new, *kind in MUTATIONS:
            if a.frames_only and not kind:
                continue
            if kind and not a.all_tests:
                continue
            if original.count(old) != 1:
                print(f"{name}: THE TEXT TO MUTATE IS FOUND {original.count(old)} TIMES")
                missed += 1
                continue
            target.write_text(original.replace(old, new))
            code, last = run()
            print(f"{name}: {'caught' if code != 0 else 'MISSED'} (exit {code}; {last})")
            missed += code == 0
        target.write_text(original)
        print(f"{sum(1 for _, _, _, *k in MUTATIONS if (k and a.all_tests) or (not k and not a.frames_only))} mutations run, {missed} not caught")
        return 1 if missed else 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
