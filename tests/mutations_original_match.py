#!/usr/bin/env python3
"""Issue 250: mutation check of tests/test_original_match.py (no tracked file is edited).

    python3 -B tests/mutations_original_match.py

Each mutation copies runtime/original_match to a temporary directory, replaces a text in one of its files, and runs
the named tests in a CHILD process that imports the mutated package before the test module (which then finds it in
sys.modules). Killed = one of the named tests fails or errors. The unmutated copy runs first: all must pass. The
OriginalTests need the E006-r0001 image in .cache/dl and unicorn."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "runtime" / "original_match"
T = "tests.test_original_match."
ENGINE = T + "OriginalTests.test_engine_is_e011_r0001"
LINES = T + "OriginalTests.test_every_commentary_line_is_an_event"
SUB = T + "OriginalTests.test_half_time_substitution"
REFUSED = T + "OriginalTests.test_refused_eleven_comes_back"

# (name, file, [(old, new)], tests that must fail)
MUTATIONS = [
    ("the team menu's item read from another frame word", "screens.py", [("MENU_ITEM_BP = -7", "MENU_ITEM_BP = -9")], [SUB]),
    ("the commentary cursor starts at the counter, not 0", "match.py",
     [('st["ring"] = 0            # (DS:80EE', 'st["ring"] = m.rd(RING_NEWEST)  # (DS:80EE')], [ENGINE, LINES]),
    ("no replay flag on resume", "machine.py", [("replay = lin == self._resume_lin", "replay = False")],
     [T + "MachineTests.test_stop_and_replay", ENGINE]),
    ("the original's message not kept", "match.py", [("if replay or not m.stack_word(8) & 0xFF:", "if True:")], [REFUSED]),
    ("a swap counted as made without looking", "screens.py",
     [('if job[2] in s["squad"][:11] and job[1] not in s["squad"][:11]:', "if True:")],
     [T + "ScreenDriverTests.test_substitution_mark_swap_and_check"]),
    ("the request pressed again (Enter cancels it)", "screens.py",
     [('if s["request"] == 0 and s["subs_left"] and not self.requested:', 'if s["subs_left"]:')],
     [T + "ScreenDriverTests.test_request_when_not_allowed_now"]),
    ("far-call arguments in push order", "machine.py", [("+ list(reversed(args))", "+ list(args)")],
     [T + "MachineTests.test_far_call_returns_with_its_argument_popped", ENGINE]),
    ("the fixture index (the set-up's seed source) not written", "match.py",
     [('self._declare("fixture index [A923]+0x26', 'None and self._declare("fixture index [A923]+0x26')], [ENGINE]),
    ("the half-time menu decided as play", "match.py",
     [('DECIDED_AT_MENU = ("half_time", "pause", "extra_time")', 'DECIDED_AT_MENU = ("pause", "extra_time")')], [SUB]),
    ("a refused eleven not handed back", "match.py",
     [("st[\"refused\"], st[\"message\"], self._menu = refusal, None, None", "raise MatchError(refusal)")], [REFUSED]),
    ("an image of another build accepted", "match.py",
     [("if image.build() != REGISTERED_BUILD:", "if False:")], [T + "OriginalTests.test_another_build_is_refused"]),
    ("the memory component cut to 1 MiB + HMA", "match.py",
     [("return self.image_header + self.m.read(0, MEM_SIZE) + self.image_tail",
       "return self.image_header + self.m.read(0, MEM_SIZE)")], [SUB]),
]

CHILD = """
import sys, unittest
sys.path.insert(0, {tmp!r})
sys.path.insert(1, {root!r})
import original_match
assert original_match.__file__.startswith({tmp!r}), original_match.__file__
suite = unittest.defaultTestLoader.loadTestsFromNames({tests!r})
r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
sys.exit(0 if r.wasSuccessful() else 1)
"""


def run(pairs, file, tests):
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "original_match"
        shutil.copytree(PKG, dst, ignore=shutil.ignore_patterns("__pycache__"))
        if pairs:
            src = (dst / file).read_text()
            for old, new in pairs:
                if src.count(old) != 1:
                    return f"text not found once: {old!r}"
                src = src.replace(old, new)
            (dst / file).write_text(src)
        code = CHILD.format(tmp=tmp, root=str(ROOT), tests=tests)
        try:
            p = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, timeout=150, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            return "killed (time limit)"
        return "survived" if p.returncode == 0 else "killed"


def main():
    every = sorted({t for _, _, _, ts in MUTATIONS for t in ts})
    base = run([], None, every)
    print(f"unmutated: {'all pass' if base == 'survived' else 'FAILS: ' + base}", flush=True)
    if base != "survived":
        sys.exit(2)
    killed = 0
    for name, file, pairs, tests in MUTATIONS:
        verdict = run(pairs, file, tests)
        killed += verdict.startswith("killed")
        print(f"{verdict:20s} {file:11s} {name}", flush=True)
    print(f"{killed} of {len(MUTATIONS)} killed")
    sys.exit(0 if killed == len(MUTATIONS) else 1)


if __name__ == "__main__":
    main()
