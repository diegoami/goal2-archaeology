"""T70: the unit tests fail without the change (after out/T68/test_controls.py). Each control copies runtime/ and the
test module into a scratch tree, applies one change (setup.py removed, as on main before T70; or a one-line mutation of
a tested branch), runs the tests there and expects a failure that is an assertion (or, without the module, the missing
port module: KeyError/ValueError), never a pass."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = "runtime/original_match/port/setup.py"
CONTROLS = [
    ("setup.py absent (main before T70)", None, None),
    ("A547: the kind test inverted", "friendly = rb(mem, r, 2) == 1 ", "friendly = rb(mem, r, 2) != 1 "),
    ("A5FB: the budget of the other kind", "mem.ds8((r.di + 0x66B) & M16)", "mem.ds8((r.di + 0x66C) & M16)"),
    ("A707: 5A03's answer ignored", "if r.al != 0:                                                # A707", "if False:  #"),
    ("A70E: the 0x40 flag ignored", "if rb(mem, r, 0x40) != 0:", "if False:"),
    ("A715: slot 4 for 5", "            c = 5\n", "            c = 4\n"),
    ("D466: the host test inverted", "r.al = 1 if r.ax == rw(mem, r, 6) else 0", "r.al = 0 if r.ax == rw(mem, r, 6) else 1"),
    ("B0A3: slot 1 not tested", "if not replace and s == 1:", "if not replace and s == 2:"),
    ("B0B7: a keeper replaced", "replace = rb(mem, r, 7) != 0", "replace = True"),
    ("B0C1: a bench player assumed", "if ss16(mem, r, r.di - 2) != 0:", "if True:"),
    ("B100: A9B8's 0 swapped in", "if r.ax != 0:                                # B100", "if True:  #"),
    ("1076: the fixed colours never", "if mem.ds8(0xA964) != 0:", "if False:  #"),
    ("1111: team 1's clash never", "if r.al == mem.ds8(0x8331):", "if False:  #"),
    ("A65D: neither managed read as managed", "r.al = 1 if managed else 0 ", "r.al = 1 "),
    ("B07B: the role match inverted", "swap = r.al == (r.cx & 0xFF)", "swap = r.al != (r.cx & 0xFF)"),
    ("5359: a managed country not asked", "if managed != 0:", "if False:  #"),
    ("586C: kind 6's title the default", '6: (0x579D, "587F"), ', ''),
    ("5970: kind 0xFE's title shifted", '0xFE: (0x57EC, "5983")', '0xFE: (0x57F7, "5983")'),
]
ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        shutil.copytree(ROOT / "runtime", d / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_setup.py", d / "tests")
        src = d / P
        if old is None:
            src.unlink()
        else:
            text = src.read_text()
            assert text.count(old) == 1, name
            src.write_text(text.replace(old, new))
        try:
            out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_setup"], cwd=d,
                                 capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            ok = False
            print(f"{name}: timed out, NOT CAUGHT")
            continue
        tail = out.stderr.strip().splitlines()[-1]
        failed = out.returncode != 0 and ("AssertionError" in out.stderr or
                                          (old is None and ("ValueError" in out.stderr or "KeyError" in out.stderr)))
        ok &= failed
        print(f"{name}: exit {out.returncode}, {tail}, {'caught' if failed else 'NOT CAUGHT'}")
print("all controls caught" if ok else "a control was not caught")
sys.exit(0 if ok else 1)
