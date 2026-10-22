"""T65: the unit tests fail without the change. Each control copies runtime/ and the test module into a scratch tree,
applies one change (the module removed, as on main; or a one-line mutation of a tested branch), runs the tests there and
expects a failure that is an assertion or the missing module, never a pass."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = "runtime/original_match/port/contests.py"
CONTROLS = [
    ("module absent (main before T65)", None, None),
    ("4F16: pass returns to 4F14", 'yield from pass_("4F23")', 'yield from pass_("4F14")'),
    ("5180: header kept DS:8303", 'mem.wds8(0x8303, 0, "0791:51A6")', 'pass'),
    ("5224: 2EF0 result ignored", '            if r.al:\n                seg, off = nested(mem, r)\n                r = yield from guest(mem, r, "3EDF", seg, off, ret="5231")',
     '            if False:\n                seg, off = nested(mem, r)\n                r = yield from guest(mem, r, "3EDF", seg, off, ret="5231")'),
    ("53AF: keeper test dropped", '    if r.al:\n        r.leave()                                                # 546E',
     '    if False:\n        r.leave()                                                # 546E'),
    ("4DFC: held roll not pushed", "        r.push(r.ax)                                             # 4DFC: the holder's roll, live across two calls",
     "        r.push(0)"),
]
ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        shutil.copytree(ROOT / "runtime", d / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_contests.py", d / "tests")
        src = d / P
        if old is None:
            src.unlink()
        else:
            text = src.read_text()
            assert text.count(old) == 1, name
            src.write_text(text.replace(old, new))
        out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_contests"], cwd=d,
                             capture_output=True, text=True)
        tail = out.stderr.strip().splitlines()[-1]
        failed = out.returncode != 0 and ("AssertionError" in out.stderr or "no port module" in out.stderr)
        ok &= failed
        print(f"{name}: exit {out.returncode}, {tail}, {'caught' if failed else 'NOT CAUGHT'}")
print("all controls caught" if ok else "a control was not caught")
sys.exit(0 if ok else 1)
