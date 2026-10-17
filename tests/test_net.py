"""`tools/net.py` retries a `gh` call once when it fails on the network, never on any other
failure and never twice; `tools/ga.py` and `tools/fetch_artifact.py` call gh through it; and
`tests/netskip.py` skips a test that needs the pinned tools, printing its reason, only when the
fetch failed on the network (#236).

A fake `gh` on PATH fails with the message in FAKE_GH_FAIL for its first FAKE_GH_FAILS calls, then
prints FAKE_GH_OUT; every call is appended to FAKE_GH_LOG. One test runs the real gh with
HTTPS_PROXY at a closed local port, which is how a blocked network looks to it.
"""
from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tests import netskip  # noqa: E402
from tools import fetch_artifact, ga, net  # noqa: E402

FAKE_GH = """#!/usr/bin/env python3
import os
import sys
log = os.environ["FAKE_GH_LOG"]
with open(log, "a", encoding="utf-8") as f:
    f.write(" ".join(sys.argv[1:]) + "\\n")
calls = len(open(log, encoding="utf-8").read().splitlines())
if calls <= int(os.environ.get("FAKE_GH_FAILS", "0")):
    sys.stderr.write(os.environ["FAKE_GH_FAIL"] + "\\n")
    sys.exit(1)
sys.stdout.write(os.environ.get("FAKE_GH_OUT", ""))
"""

TIMEOUT = ('Get "https://api.github.com/repos/x/y": net/http: TLS handshake timeout')
OFFLINE = "error connecting to api.github.com\ncheck your internet connection"
NOT_FOUND = "gh: Not Found (HTTP 404)"


class FakeGh(unittest.TestCase):
    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "gh").write_text(FAKE_GH, encoding="utf-8")
        (tmp / "gh").chmod(0o755)
        self.tmp = tmp
        self.log = tmp / "gh.log"
        self.log.touch()
        patch = mock.patch.dict(os.environ, {
            "PATH": f"{tmp}{os.pathsep}{os.environ['PATH']}", "FAKE_GH_LOG": str(self.log)})
        patch.start()
        self.addCleanup(patch.stop)

    def gh(self, fails: int, message: str, out: str = ""):
        os.environ.update(FAKE_GH_FAILS=str(fails), FAKE_GH_FAIL=message, FAKE_GH_OUT=out)

    def calls(self) -> int:
        return len(self.log.read_text(encoding="utf-8").splitlines())


class RunRetrying(FakeGh):
    def test_a_timeout_is_retried_once_and_the_retry_is_printed(self):
        self.gh(1, TIMEOUT, "ok")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            result = net.run_retrying(["gh", "api", "x"])
        self.assertEqual(0, result.returncode)
        self.assertEqual(b"ok", result.stdout)
        self.assertEqual(2, self.calls())
        self.assertIn("network failure, retrying once: ", err.getvalue())
        self.assertIn("TLS handshake timeout", err.getvalue())

    def test_a_second_network_failure_is_returned_not_retried_again(self):
        self.gh(5, TIMEOUT)
        with contextlib.redirect_stderr(io.StringIO()):
            result = net.run_retrying(["gh", "api", "x"])
        self.assertEqual(1, result.returncode)
        self.assertEqual(2, self.calls())

    def test_a_failure_that_is_not_the_network_is_never_retried(self):
        self.gh(5, NOT_FOUND)
        with contextlib.redirect_stderr(io.StringIO()) as err:
            result = net.run_retrying(["gh", "api", "x"])
        self.assertEqual(1, result.returncode)
        self.assertEqual(1, self.calls())
        self.assertEqual("", err.getvalue())

    def test_the_messages_gh_printed_offline_are_network_errors(self):
        # Seen with the network blocked (unshare -cn) and with HTTPS_PROXY at a closed port and at
        # an unroutable address; the 404 and the auth prompt are answers, not network failures.
        for message in (OFFLINE, TIMEOUT,
                        "proxyconnect tcp: dial tcp 127.0.0.1:9: connect: connection refused",
                        "proxyconnect tcp: dial tcp 10.255.255.1:3128: i/o timeout"):
            self.assertTrue(net.is_network_error(message), message)
        for message in (NOT_FOUND, "To get started with GitHub CLI, please run:  gh auth login",
                        "", None):
            self.assertFalse(net.is_network_error(message), message)

    @unittest.skipUnless(shutil.which("gh"), "gh is not installed")
    def test_the_real_gh_behind_a_closed_proxy_is_retried_once(self):
        # The real gh, not the fake: HTTPS_PROXY at a closed local port fails at once, as a
        # blocked network does, and the failure is retried exactly once.
        path = os.pathsep.join(p for p in os.environ["PATH"].split(os.pathsep)
                               if p != str(self.tmp))
        env = {**os.environ, "PATH": path, "HTTPS_PROXY": "http://127.0.0.1:9", "GH_TOKEN": "x"}
        with contextlib.redirect_stderr(io.StringIO()) as err:
            result = net.run_retrying(["gh", "api", "rate_limit"], env=env)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("proxyconnect", net.text(result.stderr))
        self.assertEqual(1, err.getvalue().count("network failure, retrying once"))


class GaRetries(FakeGh):
    def test_gh_api_retries_a_timeout_and_returns_the_answer(self):
        self.gh(1, TIMEOUT, '{"tree": []}')
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual({"tree": []}, ga._gh_api("repos/x/y/git/trees/z"))
        self.assertEqual(2, self.calls())
        self.assertIn("retrying once", err.getvalue())

    def test_gh_api_offline_after_the_retry_is_a_named_error(self):
        self.gh(5, OFFLINE)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(ga.GaError) as raised:
            ga._gh_api("repos/x/y/git/trees/z")
        self.assertIn("error connecting to api.github.com", str(raised.exception))
        self.assertEqual(2, self.calls())


class RecorderRetries(FakeGh):
    def test_the_release_download_of_a_sitting_retries_a_timeout(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "human_recorder_net", REPO_ROOT / "runtime/human/recorder.py")
        rec = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rec)
        self.gh(1, TIMEOUT)
        checks = [SystemExit("cache does not match"), "goal2-67cf27d6"]

        def verify(cache):
            outcome = checks.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome

        with mock.patch.object(rec.driver, "verify_release", verify), \
                mock.patch.object(rec.driver, "CACHE", self.tmp / "release"), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual("goal2-67cf27d6", rec.verify_release_or_die())
        self.assertEqual(2, self.calls())
        self.assertIn("retrying once", err.getvalue())


class FetchArtifactOffline(FakeGh):
    SET = "goal2-a949da2f"

    def setUp(self):
        super().setUp()
        self.cache = self.tmp / "cache"
        patch = mock.patch.object(fetch_artifact, "CACHE", self.cache)
        patch.start()
        self.addCleanup(patch.stop)

    def test_offline_with_no_cached_copy_fails_after_one_retry(self):
        self.gh(5, OFFLINE)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(subprocess.CalledProcessError):
                fetch_artifact.download(self.SET)
        self.assertEqual(2, self.calls())

    def test_offline_with_a_verified_cache_skips_the_download_and_says_so(self):
        self.gh(5, OFFLINE)
        with mock.patch.object(fetch_artifact, "verify", return_value=[]):
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(self.cache / self.SET, fetch_artifact.download(self.SET))
        self.assertIn(f"{self.SET}: offline, download skipped (error connecting to", err.getvalue())
        self.assertEqual(2, self.calls())

    def test_a_failure_that_is_not_the_network_stands_with_a_verified_cache(self):
        self.gh(5, NOT_FOUND)
        with mock.patch.object(fetch_artifact, "verify", return_value=[]):
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(subprocess.CalledProcessError):
                    fetch_artifact.download(self.SET)
        self.assertEqual(1, self.calls())


class NetSkip(unittest.TestCase):
    """A dummy test marked @needs_pinned_tools (or `needs` with its own probe), run with the
    probe patched and the per-process state cleared."""

    def setUp(self):
        patch = mock.patch.dict(netskip._state, clear=True)
        patch.start()
        self.addCleanup(patch.stop)
        self.ran = []

    def run_marked(self, fetch_effect, mark=None):
        ran = self.ran
        mark = mark or netskip.needs_pinned_tools

        class Marked(unittest.TestCase):
            @mark
            def test_marked(self):
                ran.append(True)

        result = unittest.TestResult()
        with mock.patch.object(ga, "fetch", side_effect=fetch_effect), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            Marked("test_marked").run(result)
        return result, err.getvalue()

    def test_offline_skips_and_prints_its_reason(self):
        result, err = self.run_marked(ga.GaError(
            "gh api repos/x/git/trees/y failed: " + OFFLINE))
        self.assertEqual([], self.ran)
        self.assertEqual(1, len(result.skipped))
        reason = result.skipped[0][1]
        self.assertEqual("offline, needs the network for the pinned game-archaeologist tools: "
                         "gh api repos/x/git/trees/y failed: error connecting to api.github.com",
                         reason)
        self.assertIn("SKIPPED ", err)
        self.assertIn(reason, err)

    def test_the_offline_state_is_kept_and_every_later_test_skips_without_a_new_fetch(self):
        with mock.patch.object(ga, "fetch", side_effect=ga.GaError(OFFLINE)) as fetch:
            for _ in range(2):
                with contextlib.redirect_stderr(io.StringIO()), \
                        self.assertRaises(unittest.SkipTest):
                    netskip.require("the pinned game-archaeologist tools", lambda: ga.fetch())
        self.assertEqual(1, fetch.call_count)

    def test_a_failure_that_is_not_the_network_errors_the_test(self):
        result, err = self.run_marked(ga.GaError("blob sha mismatch for tools/x.py"))
        self.assertEqual([], self.ran)
        self.assertEqual([], result.skipped)
        self.assertEqual(1, len(result.errors))
        self.assertIn("blob sha mismatch", result.errors[0][1])
        self.assertEqual("", err)

    def test_a_failed_download_is_skipped_with_the_network_line_of_its_stderr(self):
        # fetch_artifact raises CalledProcessError, whose own text names only the command: the
        # reason is the network line of the captured stderr.
        failure = subprocess.CalledProcessError(1, ["gh", "release", "download"],
                                                stderr=b"warming up\n" + OFFLINE.encode())

        def probe():
            raise failure

        result, err = self.run_marked(None, mark=netskip.needs("the release copy", probe))
        self.assertEqual([], self.ran)
        self.assertEqual("offline, needs the network for the release copy: "
                         "error connecting to api.github.com", result.skipped[0][1])
        self.assertIn(result.skipped[0][1], err)

    def test_online_the_test_runs(self):
        result, err = self.run_marked(lambda: Path("/x"))
        self.assertEqual([True], self.ran)
        self.assertEqual([], result.skipped)
        self.assertTrue(result.wasSuccessful())

    def test_a_marked_class_marks_every_test_method(self):
        ran = self.ran

        @netskip.needs_pinned_tools
        class Marked(unittest.TestCase):
            def test_one(self):
                ran.append(1)

            def test_two(self):
                ran.append(2)

        result = unittest.TestResult()
        with mock.patch.object(ga, "fetch", side_effect=ga.GaError(OFFLINE)), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            unittest.defaultTestLoader.loadTestsFromTestCase(Marked).run(result)
        self.assertEqual([], ran)
        self.assertEqual(2, len(result.skipped))
        self.assertEqual(2, err.getvalue().count("SKIPPED "))


if __name__ == "__main__":
    unittest.main()
