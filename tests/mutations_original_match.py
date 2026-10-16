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
GOALS = T + "OriginalTests.test_goal_records_agree_with_the_board_in_every_path"
ORDER = T + "OriginalTests.test_event_stream_is_in_the_originals_write_order"
C = T + "CompetitiveTests."
PENALTIES, ORDER_SO, BUDGET = (C + "test_penalties_after_extra_time", C + "test_goal2s_shootout_order",
                               C + "test_substitution_budget_is_settable_per_side")

# (name, file, [(old, new)], tests that must fail)
MUTATIONS = [
    ("the team menu's item read from another frame word", "screens.py", [("MENU_ITEM_BP = -7", "MENU_ITEM_BP = -9")], [SUB]),
    ("a commentary line stamped with the previous event's minute, not the guest clock at the ring write", "match.py",
     [('self.st["pending"].append(["line"] + self._stamp() + [n])',
       'self.st["pending"].append(["line", self.st["minute"]] + self._stamp()[1:] + [n])')],
     [T + "OriginalTests.test_events_are_stamped_at_the_originals_writes"]),
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
     [("        if problems:\n            raise ValueError(\"the image does not hold", "        if False:\n            raise ValueError(\"the image does not hold")],
     [T + "OriginalTests.test_another_build_is_refused"]),
    ("the code guard: its first block only (a prefix guard)", "image.py",
     [("for i, want in enumerate(build.CODE_SHA256):", "for i, want in enumerate(build.CODE_SHA256[:1]):")],
     [T + "OriginalTests.test_guard_covers_code_beyond_prefixes"]),
    ("the data guard left out", "image.py",
     [("for blk, want in build.DATA_SHA256.items():", "for blk, want in []:")],
     [T + "OriginalTests.test_guard_covers_data_tables"]),
    ("a screen plan kept after a stop (save refused at full time)", "match.py",
     [("        self._menu = None\n        if stopped is not None:", "        if stopped is not None:")],
     [T + "OriginalTests.test_save_at_full_time_and_at_a_decision"]),
    ("commentary stamped at the flush, not at its write", "match.py",
     [('self._emit("commentary", minute, score, text=text', 'self._emit("commentary", text=text')],
     [T + "OriginalTests.test_events_are_stamped_at_the_originals_writes"]),
    ("the substitutions-left counter read at the action replay's copy", "screens.py",
     [("SUBS_LEFT = 0x9B3A", "SUBS_LEFT = 0x9B38")],
     [T + "OriginalTests.test_events_are_stamped_at_the_originals_writes"]),
    ("the memory component cut to 1 MiB + HMA", "match.py",
     [("return self.image_header + self.m.read(0, MEM_SIZE) + self.image_tail",
       "return self.image_header + self.m.read(0, MEM_SIZE)")], [SUB]),
    # PR 251 review round 2: R1 (quick-engine trial counts are not goals) and R2 (a take-back at its own write)
    ("the quick engine's commit counted against its trial count, not the score it saved", "match.py",
     [("for _ in range(new[t] - saved[t]):", "for _ in range(max(0, new[t] - old[t])):")], [GOALS]),
    ("stamps inside the quick engine read its trial counts", "match.py",
     [("        if quick is not None:\n            return [m.rd(MINUTE)] + list(quick)\n", "")], [GOALS]),
    ("a take-back rewrites the goal it cancels in place (not queued at its own write)", "match.py",
     [('taken[-1][5] = True\n                st["pending"].append(["goal_disallowed", minute, new[0], new[1], t])',
       'taken[-1][0] = "goal_disallowed"\n                taken[-1][2:4] = [new[0], new[1]]')], [ORDER]),
    # issue 252: competitive fixtures (extra time, the shoot-out, the budget)
    ("extra time's clock write (9B15) not declared", "match.py",
     [("if self.m.pc() == self.m.lin(EXTRA_TIME_CLOCK):", "if False:")], [PENALTIES]),
    ("a shoot-out goal taken as a match goal", "match.py",
     [('if st.get("stage") == "shootout":\n                kick = st["kick"]',
       'if False:\n                kick = st["kick"]')], [PENALTIES]),
    ("a kick that went in not marked (emitted again at its return)", "match.py",
     [('                kick["scored"] = True\n', "")], [PENALTIES]),
    ("the kicking side taken as team 0", "match.py",
     [("side = self._so_byte(bp, SO_SIDE)", "side = 0")], [PENALTIES]),
    ("the shoot-out's score counts the 120 minutes' goals too", "match.py",
     [('out["shootout"] = {"score": [final[t] - st["score_120"][t] for t in (0, 1)]',
       'out["shootout"] = {"score": list(final)')], [ORDER_SO]),
    ("goal2's order: the highlight aimed one slot too high", "match.py",
     [('target = self._squad(self.opts["managed"]).index(want[0]) + 1',
       'target = self._squad(self.opts["managed"]).index(want[0]) + 2')], [ORDER_SO]),
    ("goal2's order never asked (the original's Enter for every pick)", "match.py",
     [('            if st["answer"] is None:\n                squad = self._squad(self.opts["managed"])',
       '            if False:\n                squad = self._squad(self.opts["managed"])')], [ORDER_SO]),
    ("the full-time board's event only at a key read (lost under 9B93's pushed-back key)", "match.py",
     [("        if site == SITE_BOARD:\n            self._on_board()",
       "        if site == SITE_BOARD and not m.rd(PUSHED_BACK, 1):\n            self._on_board()")], [PENALTIES]),
    ("a pause taken in the shoot-out", "match.py",
     [('if self.st.get("stage") == "shootout":\n            raise MatchError', 'if False:\n            raise MatchError')],
     [PENALTIES]),
    ("goal2's budget not written", "match.py",
     [('self._declare("substitution budget DS:9B3A', 'None and self._declare("substitution budget DS:9B3A')], [BUDGET]),
    ("an extra-time goal not marked", "match.py",
     [('return {"extra_time": True} if self.st.get("stage") == "extra_time" else {}', "return {}")],
     [C + "test_extra_time_goal_marked"]),
    ("the competition table's read after a qualifier undeclared", "match.py",
     [('if caller in TABLE_READS and st["full_time"]:', "if False:")], [C + "test_qualifier"]),
    ("a missed kick emitted before the lines its kick wrote", "match.py",
     [("""        self._flush()                  # a goal's kick is emitted here, at its write's place in the order
        if not kick["scored"]:
            minute, s0, s1 = self._stamp()
            self._emit_kick(minute, [s0, s1])""",
       """        if not kick["scored"]:
            minute, s0, s1 = self._stamp()
            self._emit_kick(minute, [s0, s1])
        self._flush()""")], [C + "test_competitive_stream_is_in_the_originals_write_order"]),
    ("a ban read at the wrong status bit", "match.py",
     [("SUSPENDED, SENT_OFF, CARRIED_BOOKING, SUBSTITUTED_OFF = 0x80,", "SUSPENDED, SENT_OFF, CARRIED_BOOKING, SUBSTITUTED_OFF = 0x20,")],
     [C + "test_consequences_of_a_sending_off"]),
    ("the players' bytes 'before' read after the match", "match.py",
     [('before = st.get("players_before") or {}', 'before = self._players_now([self.opts["first"], self.opts["second"]])')],
     [C + "test_consequences_of_a_sending_off"]),
    ("kind 4 accepted (a decider no builder writes)", "match.py",
     [("KINDS = (1, 2, 3, 5, 6, 7, 8,", "KINDS = (1, 2, 3, 4, 5, 6, 7, 8,")], [C + "test_kinds_and_budget_arguments"]),
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
            p = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, timeout=600, capture_output=True, text=True)
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
