"""#318: the heavy jobs (the family runner, check.py, the unit suite) take a slot of tools/heavy.sh.

runtime/heavy_slot.py's `take` re-runs the command under heavy.sh, so it waits behind the machine's other heavy
jobs; the real script runs here in a throwaway lock folder. Each rule has a test that fails without it."""
import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
import heavy_slot  # noqa: E402

HEAVY = ROOT / "tools" / "heavy.sh"
FAMILY = ROOT / "experiments" / "E036-match-port" / "family.py"
USABLE = HEAVY.is_file() and os.access(HEAVY, os.X_OK)


# [designed] timing constants (nothing here is evidence about the machine; heavy.sh's defaults are justified in heavy.sh
# and notes/318-heavy/). POLL: 0.1 s instead of the default 1 s, so a queued job notices a freed slot in about 0.05 s and the
# tests stay short. HOLD: a holder keeps the only slot 2 s (about 20 polls, and well over the 0.1-0.3 s a Python child
# takes to start); the probe is asserted to wait more than 0.8 s, not 2 s, so a slow `up` read cannot make it flaky.
# The unit-suite test holds 3 s because ci_gate.py's interpreter start-up comes before its first poll.
POLL = "0.1"
HOLD = 2
SUITE_HOLD = 3
MIN_WAIT = 0.8


def env_for(lock_dir, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("CI", "HARNESS_HEAVY_HELD", "HARNESS_HEAVY_OFF")}
    env.update(HARNESS_HEAVY_DIR=str(lock_dir), HARNESS_HEAVY_SLOTS="1", HARNESS_HEAVY_POLL=POLL,
               PYTHONPATH=str(ROOT / "runtime"))
    env.update(extra)
    return env


# What a heavy job prints when it has its slot: whether it is inside a heavy job.
PROBE = "import heavy_slot, os; heavy_slot.take('probe'); print('held=' + os.environ.get('HARNESS_HEAVY_HELD', '-'))"


@unittest.skipUnless(USABLE, "tools/heavy.sh is not executable")
class TakeTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.locks = Path(self._dir.name) / "locks"

    def probe(self, **extra):
        return subprocess.Popen([sys.executable, "-c", PROBE], env=env_for(self.locks, **extra),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_a_job_waits_for_the_slot_a_heavy_job_holds_and_then_runs(self):
        holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {HOLD}"], env=env_for(self.locks),
                                  stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.stdout.close)
        self.addCleanup(holder.wait)
        self.assertEqual(holder.stdout.readline(), "up\n")       # the holder has the only slot
        t0 = time.time()
        out, err = self.probe().communicate(timeout=30)
        self.assertGreater(time.time() - t0, MIN_WAIT, "the probe ran while the slot was held")
        self.assertIn("heavy: probe: waiting for a slot (0 ahead)", err)
        self.assertEqual(out, "held=probe\n")                    # it ran inside its own heavy job

    def test_inside_a_heavy_job_it_runs_at_once(self):
        out, err = self.probe(HARNESS_HEAVY_HELD="outer").communicate(timeout=30)
        self.assertEqual(out, "held=outer\n")                    # not re-run: the outer job holds the slot
        self.assertEqual(err, "")

    def test_in_ci_and_when_switched_off_it_runs_as_it_is(self):
        for var in ("CI", "HARNESS_HEAVY_OFF"):
            out, err = self.probe(**{var: "1"}).communicate(timeout=30)
            self.assertEqual((out, err), ("held=-\n", ""), var)

    def test_the_weight_is_the_number_of_slots_held(self):
        code = ("import heavy_slot; heavy_slot.take('w', weight=2); import subprocess; "
                f"print(subprocess.run(['{HEAVY}', '--status'], capture_output=True, text=True).stdout)")
        r = subprocess.run([sys.executable, "-c", code], env=env_for(self.locks, HARNESS_HEAVY_SLOTS="2"),
                           capture_output=True, text=True, timeout=30)
        # --status asked from inside the job: both slots are busy
        self.assertIn("2 of 2 slots busy", r.stdout, r.stdout + r.stderr)

    def test_take_replaces_the_process_by_heavy_sh_with_the_original_command(self):
        with mock.patch.dict(os.environ, {"HARNESS_HEAVY_HELD": "", "CI": "", "HARNESS_HEAVY_OFF": ""}), \
                mock.patch("heavy_slot.os.execv") as execv:
            heavy_slot.take("x", weight=2, argv=["python3", "-m", "pkg.mod", "--a"])
        execv.assert_called_once_with(str(HEAVY), [str(HEAVY), "--weight", "2", "x", "--", "python3", "-m", "pkg.mod", "--a"])


class ConstantsTest(unittest.TestCase):
    def test_the_timings_relate_as_their_comment_says(self):
        self.assertLess(MIN_WAIT, HOLD)               # the probe must be able to see the wait
        self.assertGreaterEqual(HOLD, 10 * float(POLL))
        self.assertGreater(SUITE_HOLD, 1)             # more than interpreter start-up plus a few polls


class FamilyWorkersTest(unittest.TestCase):
    """family.py holds one slot per match process: --workers 2 holds two."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(FAMILY.parent))
        import family
        cls.family = family

    OUT = ["--family", "S", "--out", "never-written.jsonl"]    # S has many matches: more than 2 to run

    def run_main(self, argv):
        """The `workers` main() hands to run_family for this command line (run_family stubbed: no match runs)."""
        seen = []
        stub = mock.patch.object(self.family, "run_family", side_effect=lambda sel, out, workers, *a, **k: seen.append(workers) or [])
        with stub, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.family.main(argv), 0)
        return seen[0]

    def test_the_weight_is_the_workers_main_uses_whatever_the_spelling(self):
        # each spelling argparse accepts: the last of a repeated option wins, --opt=value, an abbreviation
        for tail, workers in ((["--workers", "2"], 2), (["--workers=2"], 2), (["--workers", "1", "--workers", "2"], 2),
                              (["--workers", "2", "--workers", "1"], 1), (["--workers=1", "--workers=2"], 2),
                              (["--work", "2"], 2), (["--wor=2"], 2), (["--workers", "2", "--wor", "1"], 1), ([], 1)):
            argv = self.OUT + tail
            self.assertEqual(self.family._slot_weight(argv), self.run_main(argv), argv)   # the two cannot disagree
            self.assertEqual(self.family._slot_weight(argv), workers, argv)

    def actual_processes(self, argv, done):
        """How many match processes main() really runs at once for this command line, seen from what it calls (nothing
        real runs): the pool (a stand-in that records its size and the matches it is given), the sequential loop of a
        --workers 1 run (one process: this one), or the write watch (also one loop in this process). `done`: the matches
        already in --out."""
        seen = {"pool": None}

        class Pool:
            def __init__(self, max_workers, **k):
                seen["pool"] = [max_workers, 0]

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def map(self, fn, items):
                items = list(items)
                seen["pool"][1] = len(items)
                return []

        def match(image, spec, *a, **k):
            return {"id": spec.id, "error": None, "stopped_at_board": True, "strays": [], "score": [0, 0], "ticks": 0, "cpu_s": 0}

        with mock.patch("concurrent.futures.ProcessPoolExecutor", Pool), mock.patch.object(self.family, "find_ranges"), \
                mock.patch.object(self.family, "existing_records", return_value=done), mock.patch.object(self.family, "run_match", match), \
                mock.patch.object(self.family, "append"), mock.patch("original_match.assets.reference_image", return_value=b""), \
                mock.patch("original_match.Image"), contextlib.redirect_stdout(io.StringIO()):
            self.family.main(argv)
        return min(seen["pool"]) if seen["pool"] else 1       # at most that many matches at once, or the one in this process

    def test_the_weight_is_the_load_of_the_mode_not_the_workers_option(self):
        ids = ["S/quick-1", "S/quick-30"]
        cases = (
            # (argv, matches still to run, the weight)
            (self.OUT + ["--workers", "2"], None, 2),
            (self.OUT + ["--workers", "1"], None, 1),
            # the write watch runs its matches one by one in this process, whatever --workers says
            (["--family", "S", "--find-ranges", "ranges-never-written.json", "--workers", "2"], None, 1),
            (["--family", "S", "--find-ranges", "ranges-never-written.json", "--workers", "2", "--only", ids[0]], None, 1),
            # two workers over one match to run run one match
            (self.OUT + ["--workers", "2", "--only", ids[0]], None, 1),
            (self.OUT + ["--workers", "2", "--max", "1"], None, 1),
            (self.OUT + ["--workers", "2", "--only", ",".join(ids)], None, 2),
            # a resumed run: everything but one match is already in --out
            (self.OUT + ["--workers", "2"], [ids[0]], 1),
            (self.OUT + ["--workers", "2"], ids, 2),
        )
        for argv, todo, weight in cases:
            done = self.done_but(todo)
            with mock.patch.object(self.family, "existing_records", return_value=done):
                got = self.family._slot_weight(argv)
            self.assertEqual(got, weight, argv)
            self.assertEqual(got, self.actual_processes(argv, done), argv)    # and it is what main() really runs

    def done_but(self, todo_ids):
        if todo_ids is None:
            return {}
        return {m.id: {"error": None, "stopped_at_board": True, "strays": []} for fam in self.family.families.select("S", self.family.families.discover()) for m in fam.matches
                if m.id not in todo_ids}

    def test_a_command_line_main_refuses_holds_no_slot(self):
        for argv in (self.OUT + ["--workers", "0"], self.OUT + ["--workers", "-1"], self.OUT + ["--workers", "3"],
                     self.OUT + ["--workers", "x"], self.OUT + ["--workers"], self.OUT + ["--workers", "1", "--workers", "9"],
                     self.OUT + ["--bogus"], ["--out", "x"], ["--help"]):
            self.assertIsNone(self.family._slot_weight(argv), argv)   # argparse's own error then speaks, once, from main()

    def test_a_line_main_refuses_after_parsing_holds_no_slot_either(self):
        self.assertIsNone(self.family._slot_weight(["--family", "NO-SUCH-FAMILY", "--out", "x"]))     # families.FamilyError
        self.assertIsNone(self.family._slot_weight(["--family", "S", "--out", "x", "--only", "S/no-such-match"]))
        self.assertIsNone(self.family._slot_weight(["--family", "S", "--out", "x", "--max", "0"]))
        with mock.patch.object(self.family, "existing_records", side_effect=self.family.Refused("not this run's log")):
            self.assertIsNone(self.family._slot_weight(self.OUT))

    def test_check_py_runs_in_one_process_in_every_mode(self):
        """Audit of #318 round 3: check.py's modes (--family, --ports, --variant, --image, --json) run their matches one after
        another in the one process, so its weight is 1; this fails when it gains a pool or a child process, whose weight
        must then be derived like family.py's."""
        text = (ROOT / "runtime" / "original_match" / "check.py").read_text()
        for word in ("ProcessPool", "multiprocessing", "subprocess", "Popen", "os.fork", "Thread"):
            self.assertNotIn(word, text, word)

    def test_parsed_prints_nothing_and_returns_none_on_a_refused_line(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertIsNone(heavy_slot.parsed(self.family.parser(), ["--workers", "3"]))
        self.assertEqual(err.getvalue(), "")


@unittest.skipUnless(USABLE, "tools/heavy.sh is not executable")
class EntryPointsTest(unittest.TestCase):
    """The three commands call heavy_slot.take as their first act when run as scripts (not when imported)."""

    def test_the_entry_points_take_a_slot(self):
        for rel, name in (("experiments/E036-match-port/family.py", "family"), ("runtime/original_match/check.py", "check"),
                          ("tools/ci_gate.py", "unit-suite")):
            text = (ROOT / rel).read_text()
            tail = text[text.index('if __name__ == "__main__":'):]
            self.assertIn("heavy_slot", tail, rel)
            self.assertIn(f'take("{name}"', tail, rel)

    def test_a_valid_command_line_waits_in_the_queue(self):
        """Each entry point queues a line it will run (the refused ones do not: RefusedAfterParsingTest). #328 changed the
        unit suite's old test, which used a refused line (--modules nope) to see the wait."""
        with tempfile.TemporaryDirectory() as d:
            env = env_for(Path(d) / "locks")
            holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {SUITE_HOLD}"], env=env,
                                      stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(holder.stdout.readline(), "up\n")
                for name, argv, cwd in (
                        ("unit-suite", [str(ROOT / "tools" / "ci_gate.py"), "run-tests"], ROOT),
                        ("family", [str(FAMILY), "--family", "S", "--find-ranges", str(Path(d) / "never-written.json")], ROOT),
                        ("check", ["-m", "original_match.check"], ROOT / "runtime")):
                    p = subprocess.Popen([sys.executable, *argv], env=env, cwd=cwd, stdout=subprocess.DEVNULL,
                                         stderr=subprocess.PIPE, text=True)
                    try:
                        line = p.stderr.readline()      # blocks until it says it waits (the holder keeps the slot)
                        self.assertIn(f"heavy: {name}: waiting for a slot", line, argv)
                    finally:
                        p.terminate()
                        p.wait()
                        p.stderr.close()
            finally:
                holder.wait()
                holder.stdout.close()

    def test_a_command_line_the_script_refuses_does_not_queue(self):
        # the slot is held for SUITE_HOLD s; a refused line must answer at once with argparse's message, not wait for it
        with tempfile.TemporaryDirectory() as d:
            env = env_for(Path(d) / "locks")
            holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {SUITE_HOLD}"], env=env,
                                      stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(holder.stdout.readline(), "up\n")
                for argv in ([str(ROOT / "tools" / "ci_gate.py"), "run-tests", "--bogus"],
                             [str(FAMILY), "--family", "S", "--out", "x", "--workers", "1", "--workers", "9"],
                             ["-m", "original_match.check", "--bogus"]):
                    t0 = time.time()
                    r = subprocess.run([sys.executable, *argv], env=env, cwd=ROOT / "runtime" if argv[0] == "-m" else ROOT,
                                       capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(r.returncode, 0, argv)
                    self.assertNotIn("waiting", r.stderr, argv)
                    self.assertLess(time.time() - t0, SUITE_HOLD - 1, argv)
                    self.assertEqual(r.stderr.count("error:"), 1, argv)       # argparse speaks once
            finally:
                holder.wait()
                holder.stdout.close()


@unittest.skipUnless(USABLE, "tools/heavy.sh is not executable")
class RefusedAfterParsingTest(unittest.TestCase):
    """#328: a command line an entry point refuses after argparse answers at once while the slot is held. Each entry point
    has ONE validation (ci_gate.refusal, family.prepare, check.validate) that main() and the slot step share; the cases
    below enumerate every refusal that function can make, so a refusal moved back into main() fails here."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.tmp = Path(self._dir.name)
        self.env = env_for(self.tmp / "locks")
        self.holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {SUITE_HOLD}"], env=self.env,
                                       stdout=subprocess.PIPE, text=True)
        self.addCleanup(self.holder.stdout.close)
        self.addCleanup(self.holder.wait)
        self.assertEqual(self.holder.stdout.readline(), "up\n")        # it has the only slot for SUITE_HOLD s

    def refused_at_once(self, argv, said, cwd=ROOT):
        t0 = time.time()
        r = subprocess.run([sys.executable, *argv], env=self.env, cwd=cwd, capture_output=True, text=True, timeout=60)
        out = r.stdout + r.stderr
        self.assertNotIn("waiting", out, argv)
        self.assertLess(time.time() - t0, SUITE_HOLD - 1, argv)           # answered while the slot was still held
        self.assertEqual(r.returncode, 2, (argv, out))
        self.assertIn(said, out, argv)

    def test_ci_gate_refusals(self):
        gate = str(ROOT / "tools" / "ci_gate.py")
        self.refused_at_once([gate, "run-tests", "--modules", "nope"], "not slow modules: ['nope']")
        self.refused_at_once([gate, "run-tests", "--modules", "nope,also-not"], "not slow modules: ['also-not', 'nope']")

    def test_family_refusals(self):
        log = self.tmp / "log.jsonl"
        log.write_text("not json\n")
        existing = self.tmp / "ranges.json"
        existing.write_text("{}")
        base = [str(FAMILY), "--family", "S"]
        for tail, said in (
                ([], "give --out (a family run) or --find-ranges"),                                   # neither
                (["--out", "x", "--find-ranges", "y"], "give --out (a family run) or --find-ranges"),  # both
                (["--out", "x", "--max", "0"], "--max is a number of matches"),
                (["--out", "x", "--time-limit", "0"], "--time-limit is a number of seconds"),
                (["--out", "x", "--time-limit", "36001"], "--time-limit is a number of seconds"),
                (["--out", "x", "--stretch-limit", "0"], "--stretch-limit is a number of seconds"),
                (["--out", "x", "--only", "S/no-such-match"], "--only 'S/no-such-match'"),
                (["--out", "x", "--only", "S/quick-1,S/quick-1"], "distinct ids"),
                (["--out", "x", "--count", "bad"], "--count 'bad'"),
                (["--out", "x", "--mask", str(self.tmp / "no-such-mask")], "--mask"),
                (["--find-ranges", str(existing)], f"{existing}: exists (an output is never overwritten)"),
                (["--out", str(log)], "is not a valid log")):                                          # existing_records
            self.refused_at_once(base + tail, said)
        self.refused_at_once([str(FAMILY), "--family", "NO-SUCH-FAMILY", "--out", "x"], "refused:")  # families.FamilyError

    def test_check_refusals(self):
        existing = self.tmp / "report.json"
        existing.write_text("{}")
        for tail, said in (
                (["--variant", "bad"], "--variant is MODULE.NAME"),
                (["--variant", "no-such-module.v"], "no port module 'no-such-module'"),
                (["--variant", "pilot.no-such-variant"], "has no variant 'no-such-variant'"),
                (["--ports", "no-such-module"], "no port module 'no-such-module'"),
                (["--ports", "pilot", "--variant", "pilot.no-such-variant"], "has no variant"),
                (["--image", str(self.tmp / "no-such-image")], "does not exist"),
                (["--json", str(existing)], "exists (an output is never overwritten)"),
                (["--json", str(self.tmp / "no-folder" / "report.json")], "its folder does not exist")):
            self.refused_at_once(["-m", "original_match.check", *tail], said, cwd=ROOT / "runtime")

    def test_main_asks_the_same_validation(self):
        """The slot step and main() share one function: main() refuses through it, so the two cannot diverge."""
        sys.path.insert(0, str(ROOT / "runtime"))
        from original_match import check
        with mock.patch.object(check, "validate", side_effect=check.Refused("sentinel")), \
                contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as cm:
            check.main(["--json", str(self.tmp / "unused.json")])
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("sentinel", err.getvalue())
        with mock.patch.object(check, "validate", side_effect=check.Refused("sentinel")):
            self.assertFalse(check._takes_a_slot([]))
        spec = importlib.util.spec_from_file_location("ci_gate_328", ROOT / "tools" / "ci_gate.py")
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        with mock.patch.object(gate, "refusal", return_value="sentinel"), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(gate.main(["run-tests"]), 2)
        self.assertIn("sentinel", err.getvalue())


ROOT_USER = hasattr(os, "geteuid") and os.geteuid() == 0     # root opens and creates what a mode forbids: no such condition

# Every input/output path option of the three entry points (ci_gate.py has none), by what the run does with it. A condition
# is a path in a folder made for the test; the table says whether the run can use it (A) or not (R).
#   INPUT      --image, --mask       read: a regular file this process can open
#   NEW        --json, --find-ranges created exclusively: nothing there, its folder an existing writable folder
#   LOG        --out                 appended to (read first if there): a file read and writable, or a path whose nearest
#                                    existing folder is writable (the run makes the missing folders)
#   CACHE      --cache               a folder: the reference file in it is readable, or it is missing and the folder can be made
#   FOLDER     --checkpoint          a folder files are written in (#359): an existing writable folder, or a missing one whose
#                                    nearest existing folder is writable (the run makes the missing folders)
A, R = True, False
INPUT = dict(missing=R, directory=R, file=A, link=A, broken=R, empty=R, missing_parent=R, file_in_the_way=R)
NEW = dict(missing=A, directory=R, file=R, link=R, broken=R, empty=R, missing_parent=R, file_in_the_way=R)
LOG = dict(missing=A, directory=R, file=A, link=A, broken=R, empty=R, missing_parent=A, file_in_the_way=R)
INPUT_PERM = dict(unreadable=R, readonly=A, unwritable_parent=R)
NEW_PERM = dict(unreadable=R, readonly=R, unwritable_parent=R)
LOG_PERM = dict(unreadable=R, readonly=R, unwritable_parent=R)
CACHE = dict(missing=A, empty_folder=A, asset_file=A, asset_link=A, asset_folder=R, asset_broken=R, cache_is_a_file=R,
             under_a_file=R, missing_parent=A)
CACHE_PERM = dict(asset_unreadable=R, unwritable_folder=R, under_unwritable=R)
FOLDER = dict(missing=A, directory=A, file=R, link=R, broken=R, empty=R, missing_parent=A, file_in_the_way=R)
FOLDER_PERM = dict(unreadable=R, readonly=R, unwritable_parent=R)
# What a refusal says, by condition (a fragment of the message): the reason, so that a wrong reason that still refuses is caught.
SAID_INPUT = dict(missing="does not exist", directory="is not a file", empty="does not exist", broken="does not exist",
                  missing_parent="does not exist", file_in_the_way="cannot be read", unreadable="cannot be read",
                  unwritable_parent="does not exist")
SAID_NEW = dict(directory="exists (an output", file="exists (an output", link="exists (an output", broken="exists (an output",
                empty="is empty", missing_parent="its folder does not exist", file_in_the_way="its folder does not exist",
                unreadable="exists (an output", readonly="exists (an output", unwritable_parent="its folder is not writable")
SAID_LOG = dict(directory="is not a file", broken="is a broken link", empty="is empty",
                file_in_the_way="cannot create its folder (a file is in the way)", unreadable="cannot be read",
                readonly="is not writable", unwritable_parent="its folder is not writable")
SAID_FOLDER = dict(file="is not a folder", link="is not a folder", broken="is a broken link", empty="is empty",
                   file_in_the_way="cannot create its folder (a file is in the way)", unreadable="is not a folder",
                   readonly="is not a folder", unwritable_parent="its folder is not writable")
SAID_CACHE = dict(asset_folder="is not a file", asset_broken="does not exist", asset_unreadable="cannot be read",
                  cache_is_a_file="cannot create its folder (a file is in the way)",
                  under_a_file="cannot create its folder (a file is in the way)", unwritable_folder="its folder is not writable",
                  under_unwritable="its folder is not writable")


def build_paths(d, content="[]"):
    """The conditions of INPUT, NEW and LOG as paths under `d`, and the permission ones as a second dict."""
    d = Path(d)
    (d / "adir").mkdir()
    (d / "afile").write_text(content)
    (d / "link").symlink_to(d / "afile")
    (d / "broken").symlink_to(d / "nowhere")
    (d / "unreadable").write_text(content)
    (d / "unreadable").chmod(0)
    (d / "readonly").write_text(content)
    (d / "readonly").chmod(0o444)
    (d / "ro").mkdir()
    (d / "ro").chmod(0o555)
    plain = dict(missing=d / "new", directory=d / "adir", file=d / "afile", link=d / "link", broken=d / "broken",
                 empty="", missing_parent=d / "nodir" / "new", file_in_the_way=d / "afile" / "new")
    perm = dict(unreadable=d / "unreadable", readonly=d / "readonly", unwritable_parent=d / "ro" / "new")
    return {k: str(v) for k, v in plain.items()}, {k: str(v) for k, v in perm.items()}


def build_caches(d):
    """The conditions of CACHE as cache folders under `d` (the reference file's name is assets.REFERENCE['asset'])."""
    from original_match.assets import REFERENCE
    d, name = Path(d), REFERENCE["asset"]
    plain, perm = {}, {}

    def cache(key, into, make=None):
        folder = d / key
        if make:
            folder.mkdir(parents=True)
            make(folder)
        into[key] = str(folder)

    cache("missing", plain)
    cache("empty_folder", plain, lambda f: None)
    cache("asset_file", plain, lambda f: (f / name).write_bytes(b"x"))
    cache("asset_link", plain, lambda f: ((f / "t").write_bytes(b"x"), (f / name).symlink_to(f / "t")))
    cache("asset_folder", plain, lambda f: (f / name).mkdir())
    cache("asset_broken", plain, lambda f: (f / name).symlink_to(f / "nowhere"))
    (d / "afile").write_text("x")
    plain["cache_is_a_file"] = str(d / "afile")
    plain["under_a_file"] = str(d / "afile" / "c")
    plain["missing_parent"] = str(d / "nodir" / "c")
    cache("asset_unreadable", perm, lambda f: ((f / name).write_bytes(b"x"), (f / name).chmod(0)))
    cache("unwritable_folder", perm, lambda f: f.chmod(0o555))
    (d / "ro").mkdir()
    (d / "ro").chmod(0o555)
    perm["under_unwritable"] = str(d / "ro" / "c")
    return plain, perm


@unittest.skipUnless(USABLE, "tools/heavy.sh is not executable")
class PathOptionsTest(unittest.TestCase):
    """#328 round 2: every path option is checked before the slot by the operation the run applies to it
    (runtime/fileopts.py). Per option and per path condition: the entry point's own validation accepts or refuses it as the
    table says; a refused one is answered at once by the real script while a slot is held; and the run's own operation
    fails with the same message (an accepted one does not fail on the path). The permission conditions are separate tests,
    skipped only as root, who is not stopped by a mode."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(FAMILY.parent))
        import family
        from original_match import check, assets
        import fileopts
        cls.family, cls.check, cls.assets, cls.fileopts = family, check, assets, fileopts

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self._dir.name)

        def clean():
            for p in self.tmp.rglob("*"):
                try:
                    p.chmod(0o755 if p.is_dir() else 0o644)      # a folder at 555 or a file at 0 would stop the cleanup
                except OSError:
                    pass
            self._dir.cleanup()
        self.addCleanup(clean)
        self.env = env_for(self.tmp / "locks")
        # the only slot, held for as long as the test lasts: `exec sleep` so that terminating the holder frees it
        self.holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", "echo up; exec sleep 300"], env=self.env,
                                       stdout=subprocess.PIPE, text=True)
        self.addCleanup(self.holder.stdout.close)
        self.addCleanup(self.holder.wait)
        self.addCleanup(self.holder.terminate)
        self.assertEqual(self.holder.stdout.readline(), "up\n")

    def answered_at_once(self, argv, cwd, message):
        """The script refuses `argv` with exit 2 and `message` while the slot is held, without waiting for it."""
        p = subprocess.Popen([sys.executable, *argv], env=self.env, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
        try:
            out, err = p.communicate(timeout=10)       # a line that queued would wait here for the 300 s holder
        except subprocess.TimeoutExpired:
            p.kill()
            p.communicate()
            self.fail(f"{argv} waited for the slot instead of being refused")
        self.assertNotIn("waiting", out + err, argv)
        self.assertEqual(p.returncode, 2, (argv, out, err))
        self.assertIn(message, out + err, argv)

    def table(self, option, table, paths, validate, entry, run, said):
        """validate(path) -> the refusal message or None; entry(path) -> (argv, cwd); run(path) -> the run's operation."""
        for cond, ok in table.items():
            path = paths[cond]
            label = f"{option} {cond} {path!r}"
            why = validate(path)
            if ok:
                self.assertIsNone(why, label)
                try:
                    run(path)
                except self.fileopts.PathError as e:
                    self.fail(f"{label}: validation accepts it, the run refuses it: {e}")
                except Exception:
                    pass                       # the run's own later failures (no image, no download) are not the path's
            else:
                self.assertIsNotNone(why, label)
                self.assertIn(said[cond], why, label)
                self.assertTrue(why.startswith(f"{option} {path}"), (label, why))   # the cache: the file in the folder
                with self.assertRaises(self.fileopts.PathError, msg=label) as cm:
                    run(path)
                self.assertEqual(str(cm.exception), why, label)           # the same condition fails identically in the run
                argv, cwd = entry(path)
                self.answered_at_once(argv, cwd, why)

    # ---- check.py
    def check_validate(self, option):
        def validate(path):
            ns = self.check.parser().parse_args([option, path])
            try:
                self.check.validate(ns)
            except self.check.Refused as e:
                return str(e)
        return validate

    def check_entry(self, option):
        return lambda path: (["-m", "original_match.check", option, path], ROOT / "runtime")

    def load_image(self, path):
        return self.check.load_image(self.check.parser().parse_args(["--image", path]))

    def test_check_image(self):
        plain, _ = build_paths(self.tmp)
        self.table("--image", INPUT, plain, self.check_validate("--image"), self.check_entry("--image"), self.load_image, SAID_INPUT)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a file mode")
    def test_check_image_permissions(self):
        _, perm = build_paths(self.tmp)
        self.table("--image", INPUT_PERM, perm, self.check_validate("--image"), self.check_entry("--image"), self.load_image, SAID_INPUT)

    def test_check_json(self):
        plain, _ = build_paths(self.tmp)
        self.table("--json", NEW, plain, self.check_validate("--json"), self.check_entry("--json"),
                   lambda path: self.check.write_report(path, {}), SAID_NEW)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a folder or file mode")
    def test_check_json_permissions(self):
        _, perm = build_paths(self.tmp)
        self.table("--json", NEW_PERM, perm, self.check_validate("--json"), self.check_entry("--json"),
                   lambda path: self.check.write_report(path, {}), SAID_NEW)

    def reference(self, cache):
        with mock.patch.object(self.assets.subprocess, "run", side_effect=OSError("no gh in this test")):
            return self.assets.reference_image(cache)

    def test_check_cache(self):
        plain, _ = build_caches(self.tmp)
        self.table("--cache", CACHE, plain, self.check_validate("--cache"), self.check_entry("--cache"), self.reference, SAID_CACHE)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a folder or file mode")
    def test_check_cache_permissions(self):
        _, perm = build_caches(self.tmp)
        self.table("--cache", CACHE_PERM, perm, self.check_validate("--cache"), self.check_entry("--cache"), self.reference, SAID_CACHE)

    # ---- family.py
    def family_validate(self, extra):
        def validate(path):
            ns = self.family.parser().parse_args(["--family", "S", *extra(path)])
            try:
                self.family.prepare(ns)
            except self.fileopts.PathError as e:
                return str(e)
        return validate

    def family_entry(self, extra):
        return lambda path: ([str(FAMILY), "--family", "S", *extra(path)], ROOT)

    def run_family(self, path):
        self.family.run_family([], path, run_one=lambda spec: None, say=lambda *a: None)

    def out_args(self, path):
        return ["--out", path]

    def ranges_args(self, path):
        return ["--find-ranges", path]

    def mask_args(self, path):
        return ["--out", str(self.tmp / "out.jsonl"), "--mask", path]

    def cache_args(self, path):
        return ["--out", str(self.tmp / "out.jsonl"), "--cache", path]

    def test_family_out(self):
        plain, _ = build_paths(self.tmp, content="")      # an empty log: nothing to resume
        self.table("--out", LOG, plain, self.family_validate(self.out_args), self.family_entry(self.out_args), self.run_family, SAID_LOG)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a folder or file mode")
    def test_family_out_permissions(self):
        _, perm = build_paths(self.tmp, content="")
        self.table("--out", LOG_PERM, perm, self.family_validate(self.out_args), self.family_entry(self.out_args),
                   self.run_family, SAID_LOG)

    def test_family_find_ranges(self):
        plain, _ = build_paths(self.tmp)
        self.table("--find-ranges", NEW, plain, self.family_validate(self.ranges_args), self.family_entry(self.ranges_args),
                   lambda path: self.family.write_ranges(path, {}), SAID_NEW)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a folder or file mode")
    def test_family_find_ranges_permissions(self):
        _, perm = build_paths(self.tmp)
        self.table("--find-ranges", NEW_PERM, perm, self.family_validate(self.ranges_args),
                   self.family_entry(self.ranges_args), lambda path: self.family.write_ranges(path, {}), SAID_NEW)

    def checkpoint_args(self, path):
        return ["--out", str(self.tmp / "out.jsonl"), "--checkpoint", path]

    def save_checkpoint(self, path):
        self.family.Checkpoints(path).save("S/quick-1", {}, b"", {}, b"")

    def test_family_checkpoint(self):
        plain, _ = build_paths(self.tmp)
        self.table("--checkpoint", FOLDER, plain, self.family_validate(self.checkpoint_args),
                   self.family_entry(self.checkpoint_args), self.save_checkpoint, SAID_FOLDER)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a folder or file mode")
    def test_family_checkpoint_permissions(self):
        _, perm = build_paths(self.tmp)
        self.table("--checkpoint", FOLDER_PERM, perm, self.family_validate(self.checkpoint_args),
                   self.family_entry(self.checkpoint_args), self.save_checkpoint, SAID_FOLDER)

    def test_family_mask(self):
        plain, _ = build_paths(self.tmp)
        self.table("--mask", INPUT, plain, self.family_validate(self.mask_args), self.family_entry(self.mask_args),
                   self.family.parse_mask, SAID_INPUT)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a file mode")
    def test_family_mask_permissions(self):
        _, perm = build_paths(self.tmp)
        self.table("--mask", INPUT_PERM, perm, self.family_validate(self.mask_args), self.family_entry(self.mask_args),
                   self.family.parse_mask, SAID_INPUT)

    def test_family_cache(self):
        plain, _ = build_caches(self.tmp)
        self.table("--cache", CACHE, plain, self.family_validate(self.cache_args), self.family_entry(self.cache_args),
                   self.reference, SAID_CACHE)

    @unittest.skipIf(ROOT_USER, "root is not stopped by a folder or file mode")
    def test_family_cache_permissions(self):
        _, perm = build_caches(self.tmp)
        self.table("--cache", CACHE_PERM, perm, self.family_validate(self.cache_args), self.family_entry(self.cache_args),
                   self.reference, SAID_CACHE)

    def test_a_fifo_is_not_a_file_and_does_not_block(self):
        """Opening a FIFO for reading waits for a writer: the check must refuse it before it opens anything."""
        import signal
        fifo = self.tmp / "fifo"
        os.mkfifo(fifo)
        signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(AssertionError("check_input opened the FIFO and blocked")))
        signal.alarm(5)
        try:
            with self.assertRaises(self.fileopts.PathError) as cm:
                self.fileopts.check_input(str(fifo), "--image")
        finally:
            signal.alarm(0)
        self.assertIn("is not a file", str(cm.exception))

    def test_every_path_option_is_in_a_table(self):
        """The audit: the options of the three parsers. A new option that names a file fails here until it has a table."""
        listed = {"--image", "--json", "--cache", "--out", "--find-ranges", "--mask", "--checkpoint"}
        others = {"--family", "--max", "--workers", "--time-limit", "--stretch-limit", "--count", "--only", "--ports", "--variant", "--modules",
                  "--help", "-h"}
        seen = set()
        for parser in (self.family.parser(), self.check.parser()):
            seen |= {o for a in parser._actions for o in a.option_strings}
        spec = importlib.util.spec_from_file_location("ci_gate_328b", ROOT / "tools" / "ci_gate.py")
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        for sub in gate.parser()._subparsers._group_actions[0].choices.values():
            seen |= {o for a in sub._actions for o in a.option_strings}
        self.assertEqual(seen - listed - others, set())
        self.assertTrue(listed <= seen)


if __name__ == "__main__":
    unittest.main()
