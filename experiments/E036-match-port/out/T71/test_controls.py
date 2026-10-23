"""T71 tests on the fixed pre-task commit and under one-line mutations.

The baseline is a1f8a97, never origin/main (which advances after merge). Each control
runs the actual test module in an isolated temporary tree; no checkout or worktree changes.
"""
import io
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = "a1f8a97dfd6593b8c88053083d1f33c113dff25b"
P = "runtime/original_match/port/postmatch.py"
CONTROLS = [
    ("fixed pre-task baseline", None, None),
    ("59D8 zero AX returns no value", "return _end(r, value=True)", "return _end(r, r.ax)"),
    ("CB4E equal man replaces", 's16(perf) > s16(best)', 's16(perf) >= s16(best)'),
    ("CB41 performance not decoded", 'if s16(perf) > 5000:', 'if False:'),
    ("CB25 bench bit ignored", 'if not r.al:\n                    continue', 'if False:\n                    continue'),
    ("CC08 negative energy restored", 'rb(mem, r, 0xE) < 0x80 and rb(mem, r, 0xE) > 0', 'rb(mem, r, 0xE) > 0'),
    ("CC14 energy not restored", 'if variant != "restore-energy-omitted":', 'if False:'),
    ("BC9A overrides retained", 'w8(mem, r, 0xF, 0, "BC9A")', 'w8(mem, r, 0xF, 255, "BC9A")'),
    ("D021 place ignored", 'r.di = off + r.ax\n    w8(mem, r, 3, rb', 'r.di = off\n    w8(mem, r, 3, rb'),
    ("D045 total not cleared", 'w8(mem, r, 5, 0, "D045")', 'w8(mem, r, 5, 1, "D045")'),
    ("D0AE wins counted as losses", '(1, "D0AE") if r.al == side', '(3, "D0AE") if r.al == side'),
    ("D387 equal/larger maxima overwritten", 'if r.al > (r.dx & 0xFF):\n                    r.ax = k', 'if True:\n                    r.ax = k'),
    ("83FF win worth one", 'r.ax << (0 if variant == "group-points-one" else 1)', 'r.ax << 0'),
    ("8390 kind filter omitted", 'if r.al != rb(mem, r, 0x3C):', 'if False:'),
    ("839C unplayed filter omitted", 'if rb(mem, r, 0) >= 0xFE:', 'if False:'),
    ("85B0 sort goals tie omitted", 'swap = r.al > (r.dx & 0xFF)\n            if swap:', 'swap = False\n            if swap:'),
    ("870A aggregate equality loses", 'win = r.ax >= first_home', 'win = r.ax > first_home'),
    ("863D unplayed aggregate included", 'if rb(mem, r, -8) >= 0xFE:', 'if False:'),
    ("59F7 finals membership inverted", 'r.al = int(member(mem))', 'r.al = int(not member(mem))'),
    ("878C stage7 dimension ignored", 'int(rb(mem, r, 0x3C) == 7)', '0'),
    ("87BB stage3 dimension ignored", 'int(rb(mem, r, 0x3C) == 3)', '0'),
    ("8838 aggregate dispatch omitted", 'if rb(mem, r, 0x3C) == 6:', 'if False:'),
    ("F344 save branch omitted", 'if r.al:\n            r = yield from guest(mem, r, "0A6B"', 'if False:\n            r = yield from guest(mem, r, "0A6B"'),
    ("F331 quick tail takes snapshot", 'if mem.ds8(0x9A3E) == 0:', 'if True:'),
    ("F2E3 hook omitted", 'mem.site("0791:F2E3")', 'pass'),
]
all_ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as raw:
        d = Path(raw)
        baseline = subprocess.check_output(["git", "archive", BASE, "runtime"], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(baseline)) as tf:
            tf.extractall(d, filter="data")
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_postmatch.py", d / "tests")
        if old is not None:
            source = (ROOT / P).read_text()
            if name == "F331 quick tail takes snapshot":
                assert source.count(old) == 2
                source = source.replace(old, new, 1)
            else:
                assert source.count(old) == 1, (name, source.count(old))
                source = source.replace(old, new)
            (d / P).write_text(source)
        out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_postmatch"], cwd=d,
                             capture_output=True, text=True, timeout=120)
        caught = out.returncode != 0 and ("AssertionError" in out.stderr or
                                         (old is None and "no port module 'postmatch'" in out.stderr))
        all_ok &= caught
        print(f"{name}: exit {out.returncode}, {'caught' if caught else 'NOT CAUGHT'}", flush=True)
        if not caught:
            print(out.stderr)
print("all controls caught" if all_ok else "a control was not caught")
sys.exit(0 if all_ok else 1)
