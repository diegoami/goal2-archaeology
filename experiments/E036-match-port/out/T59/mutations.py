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
    ("the port's writes not undone before the original", f"{K}/port/prove.py",
     "        for address, old, _ in reversed(st.port_writes):\n            m.uc.mem_write(address, old)\n", ""),
    ("bytes not compared", f"{K}/port/prove.py", "            if o != p:\n", "            if False:\n"),
    ("lengths not compared", f"{K}/port/prove.py", "        if len(original) != len(port):\n", "        if False:\n"),
    ("returned registers not compared", f"{K}/port/prove.py",
     "        for r in REGS_RETURNED:\n            if original_regs[r] != port_regs[r]:",
     "        for r in REGS_RETURNED:\n            if False:"),
    ("a dead result exempted at any return address", f"{K}/port/prove.py",
     "dead = RESULT_DEAD.get((st.address, st.caller), ((), \"\"))[0]",
     "dead = next((v[0] for k, v in RESULT_DEAD.items() if k[0] == st.address), ())"),
    ("the port's registers not put back", f"{K}/port/prove.py",
     "        for r, v in st.port_regs.items():\n            m.set_reg(r, v)\n", ""),
    ("the kit's sites not replayed", f"{K}/port/prove.py", "        elif m.hooked(lin):\n            self._replay(lin)",
     "        elif False:\n            self._replay(lin)"),
    ("a site's writes not replayed", f"{K}/port/prove.py",
     "                st.writes.append((a, self._raw(a, len(b)), b))\n                m.uc.mem_write(a, b)\n",
     "                pass\n"),
    ("a site's registers not replayed", f"{K}/port/prove.py", "                self._sreg(a, b)\n",
     "                pass\n"),
    # Round 2 (sol-6.1 R1 of round 1: a replayed answer's inputs)
    ("the kit's memory reads not compared", f"{K}/port/prove.py",
     "                now = self._raw(a, len(b))\n                if now != b:",
     "                now = self._raw(a, len(b))\n                if False:"),
    ("the kit's register reads not compared", f"{K}/port/prove.py",
     "                now = self._rreg(a)\n                if now != b:",
     "                now = self._rreg(a)\n                if False:"),
    ("the kit's reads between runs not kept", f"{K}/port/prove.py",
     "        if v is None and not self.m.running and st.visits and st.visits[-1].open:", "        if False:"),
    ("the kit's memory reads not tapped", f"{K}/machine.py",
     "            self.io_tap(\"r\", linear, data)", "            pass"),
    ("the kit's register reads not tapped", f"{K}/machine.py",
     "            self.io_tap(\"g\", name.lower(), value)", "            pass"),
    ("the kit's register sets not tapped", f"{K}/machine.py",
     "            self.io_tap(\"s\", name.lower(), value)", "            pass"),
    ("emu_start not marked running", f"{K}/machine.py", "        self.running = True\n        try:",
     "        self.running = False\n        try:"),
    ("a site's place among the writes not compared", f"{K}/port/prove.py", "            if before_o != before_p:",
     "            if False:"),
    ("a site's address not compared", f"{K}/port/prove.py", "        if v.lin != lin:\n", "        if False:\n"),
    ("a site's stack not compared", f"{K}/port/prove.py", "            if here != v.at:\n", "            if False:\n"),
    ("sites left over accepted", f"{K}/port/prove.py", "        if st.next_visit < len(st.visits):\n",
     "        if False:\n"),
    ("more sites accepted", f"{K}/port/prove.py", "        if i >= len(st.visits):\n",
     "        if i >= len(st.visits):\n            return\n"),
    ("a stopped site's replay a second visit", f"{K}/port/prove.py",
     "        if replay and last is not None and last.open and last.lin == lin:", "        if False:"),
    ("the entry's own hooks taken for a site", f"{K}/port/prove.py",
     "        if not st.started and lin == st.entry_lin:", "        if False:"),
    ("the kit's writes not recorded", f"{K}/machine.py",
     "        if self.write_tap is not None:\n            self.write_tap(linear, bytes(data))\n", ""),
    ("the kit's word writes past the tap", f"{K}/machine.py",
     "        self.write(self.DS * 16 + off, int(value).to_bytes(n, \"little\"))",
     "        self.uc.mem_write(self.DS * 16 + off, int(value).to_bytes(n, \"little\"))"),
    ("a kit write outside a site accepted", f"{K}/port/prove.py",
     "        else:                                   # a write of the kit's outside its handlers",
     "        elif False:                             # a write of the kit's outside its handlers"),
    ("a port's own key read proved blind", f"{K}/match.py",
     "        if prover is not None and prover.in_port_run():", "        if False:"),
    ("nested calls not counted", f"{K}/port/prove.py", "                self.nested[address] += 1", "                pass"),
    ("the proof always armed", f"{K}/port/prove.py", "            if not self.armed():", "            if False:"),
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
    shutil.copytree(ROOT / E, dst / E, ignore=shutil.ignore_patterns("__pycache__", "out"))
    (dst / E / "out/T57").mkdir(parents=True)
    shutil.copy(ROOT / E / "out/T57/reference.jsonl", dst / E / "out/T57/reference.jsonl")   # the tests read it
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
