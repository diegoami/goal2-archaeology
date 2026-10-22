"""T66: the unit tests fail without the change. Each control copies runtime/ and the test module into a scratch tree,
applies one change (the module removed, as on main; or a one-line mutation of a tested branch), runs the tests there and
expects a failure that is an assertion or the missing module, never a pass."""
import shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
P = "runtime/original_match/port/duels.py"
CONTROLS = [
    ("module absent (main before T66)", None, None),
    ("5B43/5B4A: the 8325/8324 gate dropped", "    if mem.ds8(0x8325) == 0 and mem.ds8(0x8324) == 0:            # 5B3C-5B4A",
     "    if False:"),
    ("5B8F: line 0x41 said as 0x0D", "        template = 0x41                                          # 5B8F",
     "        template = 0x0D"),
    ("5BAD: the keeper's roll not doubled", "        r.ax = r.ax << 1                                         # 5BDB shl ax, 1",
     "        pass"),
    ("5BCD: the holder's roll not held on the stack", "        r.push(r.ax)                                             # 5BCD: the holder's roll, live across two calls",
     "        r.push(0)"),
    ("5C5A: the coin ignored", "        if r.al:\n            own(mem, r)                                          # 5C5A",
     "        if False:\n            own(mem, r)                                          # 5C5A"),
    ("5CE3: event 4 not tested", "        r.al = 1 if mem.ds8(0x8327) == 4 else 0                  # 5CD8-5CE3",
     "        r.al = 0"),
    ("5D78: the high words not compared", "            caught = s16(r.dx) > s16(r.bx)", "            caught = True"),
    ("5F66: line 0x20 said as 0x22", "        r.al = 0x20                                              # 5F66",
     "        r.al = 0x22"),
    ("6141: line 0x19 said as 0x23", '            r.al, ret = 0x19, "6151"                             # 6141',
     '            r.al, ret = 0x23, "6151"'),
    ("634A: the keeper test dropped", "    if r.al:\n        holder_record(r, mem)                                    # 634A-6356",
     "    if False:\n        holder_record(r, mem)                                    # 634A-6356"),
    ("68D6: DS:0C20 not cleared", '        mem.wds8(0x0C20, 0, "0791:68D6")', "        pass"),
    ("6508: the cap at 12", "    if mem.ds8((r.di + 0x80F0) & M16) < 0xB:", "    if mem.ds8((r.di + 0x80F0) & M16) < 0xC:"),
    ("64FA: the own goal's side not reversed", "        r.local8(8, r.al)                                        # 64FA: the side argument reversed",
     "        pass"),
    ("68B3: the take-back written as 685C", '- 1, "0791:68B3")', '- 1, "0791:685C")'),
]
ok = True
for name, old, new in CONTROLS:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        shutil.copytree(ROOT / "runtime", d / "runtime", ignore=shutil.ignore_patterns("__pycache__"))
        (d / "tests").mkdir()
        shutil.copy(ROOT / "tests/test_port_duels.py", d / "tests")
        src = d / P
        if old is None:
            src.unlink()
        else:
            text = src.read_text()
            assert text.count(old) == 1, name
            src.write_text(text.replace(old, new))
        out = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_duels"], cwd=d,
                             capture_output=True, text=True)
        tail = out.stderr.strip().splitlines()[-1]
        failed = out.returncode != 0 and ("AssertionError" in out.stderr or "no port module" in out.stderr)
        ok &= failed
        print(f"{name}: exit {out.returncode}, {tail}, {'caught' if failed else 'NOT CAUGHT'}")
print("all controls caught" if ok else "a control was not caught")
sys.exit(0 if ok else 1)
