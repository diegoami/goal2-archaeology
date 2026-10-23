"""T72 tests on the fixed pre-task commit and under one-line mutations.

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
BASE = "31121d14131161207a27789311a98c5c3e1e94d2"
P = "runtime/original_match/port/update.py"
CONTROLS = [
    ("fixed pre-task baseline", None, None),
    ("B395 confidence floor zero", "value = 1\n        r.local16(-2, value)\n    elif s16(value) > 32:", "value = 0\n        r.local16(-2, value)\n    elif s16(value) > 32:"),
    ("B3A2 confidence ceiling31", "elif s16(value) > 32:\n        value = 32", "elif s16(value) > 32:\n        value = 31"),
    ("B6FA manager floor minus128", "value = (-127) & M16", "value = (-128) & M16"),
    ("B707 manager upper126", "elif s16(value) > 127:\n        value = 127", "elif s16(value) > 127:\n        value = 126"),
    ("B2A6 old suspension kept", '"214B:0CA1", *status_ptr(8), ret="B2AB"', '"214B:0C79", *status_ptr(8), ret="B2AB"'),
    ("B347 carried booking not cleared", '"214B:0CA1", *status_ptr(4), ret="B34C"', '"214B:0C79", *status_ptr(4), ret="B34C"'),
    ("113D rating divisor3", "idiv_by(r, 2)", "idiv_by(r, 3)"),
    ("110C continent base4", "r.ax = 5 - r.dx", "r.ax = 4 - r.dx"),
    ("B764 expectation divisor16", "idiv_by(r, 32)", "idiv_by(r, 16)"),
    ("B7E6 result not doubled", "r.ax = value\n            r.ax = r.ax << 1", "r.ax = value\n            r.ax = r.ax"),
    ("5C84 margin not absolute", "if s16(r.ax) < 0:\n        r.ax = -r.ax", "if False:\n        r.ax = -r.ax"),
    ("5A4F friendly kind2", "if rb(mem, r, 2) == 1:", "if rb(mem, r, 2) == 2:"),
    ("5AA3 set route not consulted", "if not gradual:\n        seg, off", "if False:\n        seg, off"),
    ("357B roll age margin3", "r.ax = r.ax + 4", "r.ax = r.ax + 3"),
    ("35C7 managed draw2B", "r.cx = 3\n        imul(r, r.cx)", "r.cx = 2\n        imul(r, r.cx)"),
    ("3626 roll upper31", 'w8(mem, r, 0xD, 32, "1771:3626")', 'w8(mem, r, 0xD, 31, "1771:3626")'),
    ("3646 roll lower floor zero", 'w8(mem, r, 0xD, 1, "1771:3646")', 'w8(mem, r, 0xD, 0, "1771:3646")'),
    ("367E injured test reversed", "if rb(mem, r, 0xE) == 0:", "if rb(mem, r, 0xE) != 0:"),
    ("36DD rest bonus omitted", "if s16(value) < 16:", "if False:"),
    ("36F6 cap age margin4", "r.ax = r.ax + 3", "r.ax = r.ax + 4"),
    ("3768 healing reversed", "heal = bool(r.al)", "heal = not bool(r.al)"),
    ("B8E9 bench all participants", "participant = k < 12", "participant = True"),
    ("B920 recovery flag AH from playerword", "return rw(mem, r, -2)\n\n    for side", "r.ax = rw(mem, r, -2)\n        return r.ax\n\n    for side"),
    ("B871 manager credit even for friendlies", "if rb(mem, r, 2) != 1:", "if True:"),
    ("BA09 unused positions not restored", "if k > 11 and not managed:", "if False:"),
    ("BB09 kind0 serves a ban", "if rb(mem, r, 2) != 0:", "if True:"),
    ("BA93 pool end not wrapped", "last = r.ax", "last = first + 0x4F"),
]
all_ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as raw:
        d = Path(raw)
        baseline = subprocess.check_output(["git", "archive", BASE, "runtime"], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(baseline)) as tf:
            tf.extractall(d, filter="data")
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_update.py", d / "tests")
        if old is not None:
            source = (ROOT / P).read_text()
            assert source.count(old) == 1, (name, source.count(old))
            source = source.replace(old, new)
            (d / P).write_text(source)
        out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_update"], cwd=d,
                             capture_output=True, text=True, timeout=120)
        caught = out.returncode != 0 and ("AssertionError" in out.stderr or
                                         (old is None and "no port module 'update'" in out.stderr))
        all_ok &= caught
        print(f"{name}: exit {out.returncode}, {'caught' if caught else 'NOT CAUGHT'}", flush=True)
        if not caught:
            print(out.stderr)
print("all controls caught" if all_ok else "a control was not caught")
sys.exit(0 if all_ok else 1)
