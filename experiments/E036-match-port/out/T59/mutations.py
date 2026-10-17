#!/usr/bin/env python3
"""T59: each rule of the guest calls, the proof and the locator taken out of a copy, one at a time; tests.test_port_guest
must fail on every mutated copy and pass on the unmutated one (rule 9: a test proves behaviour only if it fails
without it).

    python3 -B experiments/E036-match-port/out/T59/mutations.py > experiments/E036-match-port/out/T59/mutations-<commit>.txt

The copies live in a temporary directory (runtime/original_match, experiments/E036-match-port, the test file); the
worktree is never edited."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
K, E = "runtime/original_match", "experiments/E036-match-port"
MUTATIONS = [
    ("no translation cache dropped", f"{K}/machine.py", "            self.uc.ctl_remove_cache(lin, lin + 1)\n", ""),
    ("a frame resumes at any SP", f"{K}/port/guest.py",
     "return machine.reg(\"ss\") == self.ss and machine.reg(\"sp\") == self.expect_sp", "return True"),
    ("listeners not muted", f"{K}/machine.py", "            if always or not self.muted:\n", "            if True:\n"),
    ("far call without its segment", f"{K}/port/guest.py", "([m.seg(rseg)] if c.far else [])", "[]"),
    ("caller_pops not dropped", f"{K}/port/guest.py",
     "        machine.set_reg(\"sp\", self.after_sp)     # caller_pops", "        pass     # caller_pops"),
    ("a port goes on from a stop", f"{K}/machine.py",
     "elif frame is not None and frame.ret_lin == lin and frame.returned(self):",
     "elif frame is not None and frame.returned(self):"),
    ("the original's writes not undone", f"{K}/port/prove.py",
     "        for address, old, _ in reversed(st.writes):\n            m.write(address, old)\n", ""),
    ("bytes not compared", f"{K}/port/prove.py", "            if o != p:\n", "            if False:\n"),
    ("lengths not compared", f"{K}/port/prove.py", "        if len(original) != len(model):\n", "        if False:\n"),
    ("registers not compared", f"{K}/port/prove.py",
     "        for r in compared:\n            if st.original_regs[r] != model_regs[r]:",
     "        for r in compared:\n            if False:"),
    ("no giving way at a kit site", f"{K}/port/prove.py", "        elif m.hooked(lin):\n", "        elif False:\n"),
    ("the proof always armed", f"{K}/port/prove.py", "or not self.armed():", ":"),
    ("a procedure's AX compared", f"{K}/port/prove.py", "result if frame.value is not None else ()", "result"),
    ("save with a frame live", f"{K}/match.py", "        if self.m.frames:              #", "        if False:              #"),
    ("the row's draws not summed", f"{E}/locate.py", "        before += a[1]\n", ""),
    ("a ported reference accepted", f"{E}/compare.py", "        if \"ports\" in ref[mid]:", "        if False:"),
    ("a log of other ports resumed", f"{E}/family.py", "        if (r.get(\"ports\"), r.get(\"variant\")) != want:",
     "        if False:"),
    ("ports unsorted accepted", f"{E}/records.py", "    if p != sorted(set(p)):", "    if False:"),
    ("a variant of another module accepted", f"{E}/records.py",
     "        if r[\"variant\"].split(\".\")[0] not in p:", "        if False:"),
    ("partial port keys accepted", f"{E}/records.py", "    _keys(r, REQUIRED + (PORT_KEYS if ported else ()), \"record\")",
     "    _keys(r, REQUIRED + tuple(k for k in PORT_KEYS if k in r), \"record\")"),
    ("the machinery listed as ports", f"{K}/port/__init__.py", "NOT_PORT_MODULES = (\"mem\", \"guest\", \"prove\")",
     "NOT_PORT_MODULES = (\"mem\",)"),
]


def copy(dst):
    shutil.copytree(ROOT / K, dst / K, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / E, dst / E, ignore=shutil.ignore_patterns("__pycache__"))
    (dst / "tests").mkdir()
    shutil.copy(ROOT / "tests/test_port_guest.py", dst / "tests/test_port_guest.py")


def run(dst):
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", "tests.test_port_guest"], cwd=dst, capture_output=True,
                       text=True)
    tail = [line for line in p.stderr.splitlines() if line.startswith(("FAIL:", "ERROR:", "Ran ", "OK", "FAILED"))]
    return p.returncode, tail


def main():
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        base = Path(d) / "clean"
        copy(base)
        code, tail = run(base)
        print(f"unmutated: exit {code}; " + " | ".join(tail))
        bad += code != 0
        for i, (name, path, old, new) in enumerate(MUTATIONS):
            dst = Path(d) / f"m{i}"
            copy(dst)
            f = dst / path
            text = f.read_text()
            if text.count(old) != 1:
                print(f"{name}: the mutation does not apply ({text.count(old)} matches): NOT RUN")
                bad += 1
                continue
            f.write_text(text.replace(old, new))
            code, tail = run(dst)
            caught = code != 0
            bad += not caught
            print(f"{name} ({path}): {'caught' if caught else 'NOT CAUGHT'}; " + " | ".join(tail[:4]))
    print(f"{len(MUTATIONS)} mutations, {'all caught' if not bad else f'{bad} problems'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
