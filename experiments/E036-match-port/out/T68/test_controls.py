"""T68: the unit tests fail without the change (after out/T67/test_controls.py). Each control copies runtime/ and the
test module into a scratch tree, applies one change (discipline.py removed, as on main before T68; or a one-line
mutation of a tested branch or writer), runs the tests there and expects a failure that is an assertion (or, without
the module, the missing port module: ValueError), never a pass."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = "runtime/original_match/port/discipline.py"
CONTROLS = [
    ("discipline.py absent (main before T68)", None, None),
    ("7F35: a second booking books", "if r.al:                                                 # 7F35 or al, al; je 7F44",
     "if False:"),
    ("7F99: a tie injures the fouler", "if r.al > (r.dx & 0xFF):", "if r.al >= (r.dx & 0xFF):"),
    ("7D76: 7A43's refusal ignored", "go = r.al != 0                                           # 7D76", "go = True"),
    ("C899: a budget of 0 read as one left", "if mem.ds8((r.di + 0x9B3A) & M16) == 0:                      # C899",
     "if False:"),
    ("C8C9: +0xE < 1 read as < 2", "if s8(rb(mem, r, 0xE)) < 1:", "if s8(rb(mem, r, 0xE)) < 2:"),
    ("8111: a computer side with no budget scanned", "if mem.ds8((r.di + 0x9B3A) & M16) > 0:               # 8111",
     "if mem.ds8((r.di + 0x9B3A) & M16) >= 0:"),
    ("C1D0: ahead and behind swapped", "r.al = 0 if ahead() else 1", "r.al = 1 if ahead() else 0"),
    ("BF9F: the direction ignored", "if direction:                                            # BF9F", "if True:"),
    ("7DD9: the injury written as another instruction", '+ 1, "0791:7DD9")   # the injury',
     '+ 1, "0791:7DDA")'),
    ("C7DC: the substitution written as another instruction", '- 1, "0791:C7DC")   # the substitution',
     '- 1, "0791:C7DD")'),
]
ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        shutil.copytree(ROOT / "runtime", d / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_discipline.py", d / "tests")
        src = d / P
        if old is None:
            src.unlink()
        else:
            text = src.read_text()
            assert text.count(old) == 1, name
            src.write_text(text.replace(old, new + "  # T68 control:"))     # the rest of the line stays a comment
        try:
            out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_discipline"], cwd=d,
                                 capture_output=True, text=True, timeout=300)
        except subprocess.TimeoutExpired:
            ok = False
            print(f"{name}: timed out, NOT CAUGHT")
            continue
        tail = out.stderr.strip().splitlines()[-1]
        failed = out.returncode != 0 and ("AssertionError" in out.stderr or (old is None and "ValueError" in out.stderr))
        ok &= failed
        print(f"{name}: exit {out.returncode}, {tail}, {'caught' if failed else 'NOT CAUGHT'}")
print("all controls caught" if ok else "a control was not caught")
sys.exit(0 if ok else 1)
