"""T67: the unit tests fail without the change (after out/T66/test_controls.py). Each control copies runtime/ and the
test module into a scratch tree, applies one change (restarts.py as on main before T67, T59's throw-in only; or a
one-line mutation of a tested branch), runs the tests there and expects a failure that is an assertion (or, for main's
module, the missing ports: KeyError), never a pass.

v2 (#381, milestone review #376): the "as on main" control reads restarts.py from 22614457, main just before T67's
merge (T59's throw-in only), not from the moving origin/main, which holds T67 itself once T67 is merged. The first
version, test_controls.py, and its recorded output stay as they were."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = "runtime/original_match/port/restarts.py"
BEFORE_T67 = "22614457b0ba6871f9b60fc8988507d52d1935f1"   # main before T67's merge (#373)
MAIN = subprocess.run(["git", "show", BEFORE_T67 + ":" + P], cwd=ROOT, capture_output=True, text=True, check=True).stdout
CONTROLS = [
    ("restarts.py as on main (T59's 6E11 only)", None, None),
    ("6DCB: the first slot for the nearest", "        r.al = mem.ds8((r.di + 0x8311) & M16)                    # [di - 0x7cef]",
     "        r.al = mem.ds8((r.di + 0x668) & M16)"),
    ("7754: DS:8315 >= 0 read as negative", "            r.al = 1 if s8(mem.ds8(0x8315)) < 0 else 0           # 774D-775A jl",
     "            r.al = 1"),
    ("7779: DS:8316 >= 0 read as negative", "            r.al = 1 if s8(mem.ds8(0x8316)) < 0 else 0           # 7772-777F jl",
     "            r.al = 1"),
    ("78A7: the off-pitch test dropped", "    if r.ax == mem.ds16(0x640):                                  # 78A1 jne 78AA; jmp 7987",
     "    if False:"),
    ("78FD: a waiting key not read", "                if r.al:                                         # 78F9 je 7902",
     "                if False:"),
    ("7A89: the cap at 4", "        return s16(r.ax) < 3", "        return s16(r.ax) <= 3"),
    ("7B12: 11 available enough", "        if available > 0xB:                                      # 7AE1 cmp word; jbe 7B12",
     "        if available >= 0xB:"),
    ("7A01: the booking written as another instruction",
     '+ 1, "0791:7A01")   # the booking', '+ 1, "0791:7A05")'),
    ("7A05: the tally's cap at 6", "    if mem.ds16(0x8321) < 5:", "    if mem.ds16(0x8321) < 6:"),
]
ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        shutil.copytree(ROOT / "runtime", d / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_restarts.py", d / "tests")
        src = d / P
        if old is None:
            src.write_text(MAIN)
        else:
            text = src.read_text()
            assert text.count(old) == 1, name
            src.write_text(text.replace(old, new))
        try:
            out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_restarts"], cwd=d,
                                 capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            ok = False
            print(f"{name}: timed out, NOT CAUGHT")
            continue
        tail = out.stderr.strip().splitlines()[-1]
        failed = out.returncode != 0 and ("AssertionError" in out.stderr or (old is None and "KeyError" in out.stderr))
        ok &= failed
        print(f"{name}: exit {out.returncode}, {tail}, {'caught' if failed else 'NOT CAUGHT'}")
print("all controls caught" if ok else "a control was not caught")
sys.exit(0 if ok else 1)
