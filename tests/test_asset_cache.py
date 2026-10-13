"""Fix #184: check.py's asset() (the E011 record outputs the experiments read).

- A stub `gh` on PATH stands in for GitHub (the real command is `gh release download`); it is the only fake.
- TwoProcessTests: two real processes start with an empty cache dir; the stub writes garbage into the file it is
  asked for, holds it for 1.5 s, then writes the true bytes. Both end with the right file (sha256) and the
  cache dir holds that file only (no partial, no temp directory). Fails when the download goes straight into the
  cache dir (no temp name, no rename): the second process then finds the first one's garbage and its sha check stops it.
- CommonCacheTests: a file in the main checkout's cache is copied in with no `gh` call; absent there, `gh` runs.
- FailureTests: a failed `gh` exits with the command to run, leaves nothing in the cache dir, and main() writes
  nothing under out/ even though an earlier record was cached and could have been emulated first.
"""
import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/emul"))
sys.path.insert(0, str(ROOT / "experiments/E021-m0-whole-match"))

try:
    import check  # noqa: E402
except ModuleNotFoundError:     # unicorn missing
    check = None

GOOD = bytes(range(256)) * 40
SHA = hashlib.sha256(GOOD).hexdigest()
ENTRY = {"sha256": SHA, "name": "r-watchstart.sav"}
NAME = f"{SHA[:16]}-r-watchstart.sav"

STUB = '''#!/usr/bin/env python3
import os, sys, time
a = sys.argv
d = a[a.index("--dir") + 1]
pat = a[a.index("--pattern") + 1]
state = os.environ["STUB_DIR"]
open(os.path.join(state, "calls"), "a").write(pat + "\\n")
if os.environ.get("STUB_FAIL"):
    sys.exit(1)
try:
    os.close(os.open(os.path.join(state, "first"), os.O_CREAT | os.O_EXCL))
    first = True
except FileExistsError:
    first = False
good = open(os.path.join(state, "good"), "rb").read()
f = open(os.path.join(d, pat), "wb")
if first:
    f.write(b"GARBAGE"); f.flush(); time.sleep(1.5); f.seek(0); f.truncate()
f.write(good); f.close()
'''

CHILD = '''
import os, sys, time
from pathlib import Path
sys.path[:0] = [%r, %r]
if os.environ.get("CHECK_SOURCE"):      # the mutation harness's seam: run a mutated copy of check.py
    import types
    check = types.ModuleType("check"); check.__file__ = os.environ["CHECK_SOURCE"]
    sys.modules["check"] = check
    exec(compile(open(check.__file__).read(), check.__file__, "exec"), check.__dict__)
import check
check.DL = Path(sys.argv[1]); check.common_dl = lambda: None
while not os.path.exists(sys.argv[2]):
    time.sleep(0.01)
print(len(check.asset(%r)))
''' % (str(ROOT / "runtime/emul"), str(ROOT / "experiments/E021-m0-whole-match"), ENTRY)


@unittest.skipIf(check is None, "unicorn is not installed")
class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        t = Path(self.tmp.name)
        self.bin, self.state, self.dl = t / "bin", t / "state", t / "dl"
        self.bin.mkdir(), self.state.mkdir()
        (self.state / "good").write_bytes(GOOD)
        gh = self.bin / "gh"
        gh.write_text(STUB)
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
        self.saved = (check.DL, check.common_dl, check.OUT, os.environ.copy())
        self.addCleanup(self.restore)
        os.environ.update(PATH=f"{self.bin}:{os.environ['PATH']}", STUB_DIR=str(self.state))
        os.environ.pop("STUB_FAIL", None)
        self.env = dict(os.environ)
        check.DL = self.dl
        check.common_dl = lambda: None

    def restore(self):
        check.DL, check.common_dl, check.OUT, env = self.saved
        os.environ.clear()
        os.environ.update(env)

    def calls(self):
        f = self.state / "calls"
        return f.read_text().split() if f.exists() else []


class TwoProcessTests(Base):
    def test_two_first_runs_end_with_the_right_file_and_no_partial(self):
        gos = [Path(self.tmp.name) / f"go{i}" for i in range(2)]
        procs = [subprocess.Popen([sys.executable, "-B", "-c", CHILD, str(self.dl), str(g)], env=self.env,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for g in gos]
        time.sleep(4)                   # both have imported check and wait for their go file
        gos[0].write_text("go")
        time.sleep(0.5)                 # the first process is inside the stub, its garbage on disk
        gos[1].write_text("go")
        results = [p.communicate(timeout=60) + (p.returncode,) for p in procs]
        self.assertEqual([(r[2], r[0].strip()) for r in results], [(0, str(len(GOOD)))] * 2, results)
        self.assertEqual(sorted(p.name for p in self.dl.iterdir()), [NAME])
        self.assertEqual(hashlib.sha256((self.dl / NAME).read_bytes()).hexdigest(), SHA)
        self.assertEqual(self.calls(), [NAME, NAME])


class CommonCacheTests(Base):
    def common(self, content=None):
        common = Path(self.tmp.name) / "common"
        common.mkdir()
        if content is not None:
            (common / NAME).write_bytes(content)
        check.common_dl = lambda: common

    def test_a_file_in_the_common_cache_is_copied_in_with_no_download(self):
        self.common(GOOD)
        self.assertEqual(check.asset(ENTRY), GOOD)
        self.assertEqual(self.calls(), [])
        self.assertEqual(sorted(p.name for p in self.dl.iterdir()), [NAME])
        self.assertEqual((self.dl / NAME).read_bytes(), GOOD)

    def test_a_file_missing_from_the_common_cache_is_downloaded(self):
        self.common()
        self.assertEqual(check.asset(ENTRY), GOOD)
        self.assertEqual(self.calls(), [NAME])

    def test_no_common_cache_is_downloaded(self):
        self.assertEqual(check.asset(ENTRY), GOOD)
        self.assertEqual(self.calls(), [NAME])

    def test_a_cached_file_is_used_with_neither(self):
        self.dl.mkdir()
        (self.dl / NAME).write_bytes(GOOD)
        self.assertEqual(check.asset(ENTRY), GOOD)
        self.assertEqual(self.calls(), [])

    def test_a_wrong_file_in_the_common_cache_is_refused(self):
        self.common(GOOD + b"x")
        with self.assertRaises(SystemExit) as e:
            check.asset(ENTRY)
        self.assertIn("sha256 does not match", str(e.exception))

    def test_common_dl_in_a_main_checkout_is_its_own_cache(self):
        # there `git rev-parse --git-common-dir` prints a relative ".git" unless asked for an absolute path
        repo = Path(self.tmp.name) / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        check.common_dl = self.saved[1]
        check.ROOT = repo
        self.addCleanup(setattr, check, "ROOT", ROOT)
        self.assertEqual(check.common_dl(), repo / ".cache/dl")

    def test_common_dl_is_the_main_checkouts_cache(self):
        common = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
        check.common_dl = self.saved[1]
        self.assertEqual(check.common_dl(), Path(common).parent / ".cache/dl")
        self.assertTrue(Path(common).is_dir())


class FailureTests(Base):
    def test_a_failed_download_exits_with_the_command_and_leaves_the_cache_empty(self):
        os.environ["STUB_FAIL"] = "1"
        with self.assertRaises(SystemExit) as e:
            check.asset(ENTRY)
        msg = str(e.exception)
        self.assertIn(f"cannot download {NAME}", msg)
        self.assertTrue(msg.endswith(
            f"run: gh release download E011 --repo diegoami/goal2-archaeology --pattern {NAME} --dir {self.dl}"), msg)
        self.assertEqual(list(self.dl.iterdir()), [])
        self.assertEqual(self.calls(), [NAME])

    def test_a_download_that_writes_nothing_is_a_failure(self):
        (self.bin / "gh").write_text("#!/bin/sh\nexit 0\n")
        with self.assertRaises(SystemExit) as e:
            check.asset(ENTRY)
        self.assertIn("gh wrote no such file", str(e.exception))
        self.assertEqual(list(self.dl.iterdir()), [])

    def test_main_writes_nothing_under_out_when_a_later_record_cannot_be_fetched(self):
        os.environ["STUB_FAIL"] = "1"
        t = Path(self.tmp.name)
        runs, out = t / "runs", t / "out"
        runs.mkdir()
        other = b"cached but not a savestate"
        e1 = {"sha256": hashlib.sha256(other).hexdigest(), "name": "a-watchstart.sav"}
        self.dl.mkdir()
        (self.dl / f"{e1['sha256'][:16]}-a-watchstart.sav").write_bytes(other)
        for i, e in enumerate((e1, ENTRY), 1):
            (runs / f"E011-r000{i}.json").write_text(json.dumps({"run_id": f"r{i}", "outputs": [e]}))
        check.OUT = out
        with self.assertRaises(SystemExit) as e:
            check.main(["--runs", str(runs)])
        self.assertIn(f"cannot download {NAME}", str(e.exception))
        self.assertFalse(out.exists() and list(out.iterdir()))
        self.assertEqual(self.calls(), [NAME])


if __name__ == "__main__":
    unittest.main()
