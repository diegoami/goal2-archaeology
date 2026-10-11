"""`tools/ga.py` fetches the four pinned tools and the `formats/` tree for the commit
`archaeology.json` pins; a cached copy is used only when every needed file is present and its git
blob sha matches the pinned tree, so a partial cache is fetched again and an edited file is a named
`GaError`, never silently replaced (ADR-009).

`tools/verify_evidence.py` and `tools/check_citations.py` are pass-through wrappers: they run the
pinned tool from the working directory with the same arguments, streams and exit code.

The fake `gh` serves one git tree and its blobs from a JSON file; the cache is patched into a
temporary directory, so no test here touches the network or the repository's real cache. The
wrappers are driven in-process with a stub tool in that fake cache, again without network.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import py_compile
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import check_citations, ga, register_artifact, verify_evidence  # noqa: E402

# The pinned files the fake tree serves, and the bytes each holds. The blob sha the tree lists is
# `ga.git_blob_sha` of these bytes, so a real download passes the same check a real tree would.
CONTENTS = {
    "tools/validate_records.py": "validator body\n",
    "tools/register_artifact.py": "artifact body\n",
    "tools/verify_evidence.py": "verifier body\n",
    "tools/check_citations.py": "citations body\n",
    "formats/run-1.schema.json": '{"schema": "run/1"}\n',
}

# A fake `gh api`: print the git tree, or one blob, from FAKE_GH_TREE ({"tree": [...],
# "blobs": {sha: text}}); every call is appended to FAKE_GH_LOG. A tree entry, a blob outside the
# tree and a non-needed path exercise ga.py's filtering.
FAKE_GH = """#!/usr/bin/env python3
import base64
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\\n")
data = json.loads(open(os.environ["FAKE_GH_TREE"], encoding="utf-8").read())
path = args[1]
if "/git/trees/" in path:
    print(json.dumps({"tree": data["tree"]}))
elif "/git/blobs/" in path:
    text = data["blobs"][path.rsplit("/", 1)[1]]
    print(json.dumps({"content": base64.b64encode(text.encode()).decode()}))
else:
    sys.exit(2)
"""

# A stub pinned tool: it records its own arguments beside itself and exits 7, so a wrapper that
# changes its arguments or its exit code is caught.
STUB_TOOL = '''#!/usr/bin/env python3
import sys
from pathlib import Path

Path(__file__).with_name(Path(__file__).name + ".args").write_text(
    "\\n".join(sys.argv[1:]), encoding="utf-8")
sys.exit(7)
'''


def tree_fixture(contents: dict[str, str] | None = None) -> dict:
    contents = CONTENTS if contents is None else contents
    tree = [{"path": path, "type": "blob", "sha": ga.git_blob_sha(text.encode())}
            for path, text in contents.items()]
    # Files the fetch must not take: a tree, a file outside the needed set.
    tree.append({"path": "formats/examples", "type": "tree", "sha": "t"})
    tree.append({"path": "tests/formats/other.py", "type": "blob", "sha": "0" * 40})
    blobs = {ga.git_blob_sha(text.encode()): text for text in contents.values()}
    return {"tree": tree, "blobs": blobs}


class GaFetchTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        fakebin = self.tmp / "bin"
        fakebin.mkdir()
        gh = fakebin / "gh"
        gh.write_text(FAKE_GH, encoding="utf-8")
        gh.chmod(0o755)
        (self.tmp / "tree.json").write_text(json.dumps(tree_fixture()), encoding="utf-8")
        self.log = self.tmp / "gh.log"
        self.env = {"PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
                    "FAKE_GH_LOG": str(self.log), "FAKE_GH_TREE": str(self.tmp / "tree.json")}
        self.cache = self.tmp / "cache"
        self.pinner = mock.patch.object(ga, "CACHE", self.cache)

    def calls(self) -> list[str]:
        if not self.log.exists():
            return []
        return self.log.read_text(encoding="utf-8").splitlines()

    def seed(self, dest: Path, contents: dict[str, str] | None = None) -> None:
        for path, text in (CONTENTS if contents is None else contents).items():
            target = dest / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")

    def blob_calls(self) -> list[str]:
        return [call for call in self.calls() if "git/blobs" in call]

    def test_root_is_the_cache_path_for_that_commit(self):
        # A cache for another commit can never satisfy this pin: root() keys the folder by commit.
        self.assertEqual(ga.CACHE / "deadbeef", ga.root("deadbeef"))
        self.assertEqual(ga.CACHE / ga.pin()[1], ga.root())

    def test_symlinked_cache_root_or_commit_is_a_named_error(self):
        # A cache root that is a symlink is refused before anything is fetched or written.
        real = self.tmp / "real"
        real.mkdir()
        link = self.tmp / "link"
        link.symlink_to(real)
        with mock.patch.object(ga, "CACHE", link):
            with self.assertRaises(ga.GaError) as raised:
                ga.fetch()
        self.assertIn("symlink", str(raised.exception))
        # So is a commit folder that is a symlink, which could point at another commit's cache.
        dest = self.cache / ga.pin()[1]
        dest.parent.mkdir(parents=True)
        other = self.tmp / "other"
        other.mkdir()
        dest.symlink_to(other, target_is_directory=True)
        with self.pinner:
            with self.assertRaises(ga.GaError) as raised:
                ga.fetch()
        self.assertIn("symlink", str(raised.exception))

    def test_git_blob_sha_is_the_sha_git_gives_the_blob(self):
        # The mix-up this guards against is using the sha256 of the content; git names a blob by
        # sha1 of `blob <len>\0<bytes>`, checked here against git itself.
        data = b"the pinned bytes\n"
        with tempfile.NamedTemporaryFile() as handle:
            handle.write(data)
            handle.flush()
            hashed = subprocess.run(["git", "hash-object", handle.name],
                                    capture_output=True, text=True)
        self.assertEqual(0, hashed.returncode, hashed.stderr)
        self.assertEqual(hashed.stdout.strip(), ga.git_blob_sha(data))

    def test_complete_cache_is_used_and_nothing_is_downloaded(self):
        repo, commit = ga.pin()
        dest = self.cache / commit
        self.seed(dest)
        with self.pinner, mock.patch.dict(os.environ, self.env):
            self.assertEqual(dest, ga.fetch())
        self.assertEqual([], self.blob_calls())
        self.assertTrue(any(f"git/trees/{commit}" in call for call in self.calls()))

    def test_partial_cache_is_fetched_again(self):
        # The cache holds one needed file only: it is never used, and the whole set is fetched.
        repo, commit = ga.pin()
        dest = self.cache / commit
        self.seed(dest, {"tools/validate_records.py": CONTENTS["tools/validate_records.py"]})
        with self.pinner, mock.patch.dict(os.environ, self.env):
            self.assertEqual(dest, ga.fetch())
        for path, text in CONTENTS.items():
            self.assertEqual(text, (dest / path).read_text(encoding="utf-8"), path)
        self.assertEqual(len(CONTENTS), len(self.blob_calls()))

    def test_edited_cached_tool_is_a_named_blob_sha_error(self):
        # A file that was changed after the fetch is left alone: fetch fails by name, it is not
        # silently re-downloaded over.
        repo, commit = ga.pin()
        dest = self.cache / commit
        self.seed(dest)
        edited = dest / "tools" / "check_citations.py"
        edited.write_text(CONTENTS["tools/check_citations.py"] + "# edited\n", encoding="utf-8")
        with self.pinner, mock.patch.dict(os.environ, self.env):
            with self.assertRaises(ga.GaError) as raised:
                ga.fetch()
        self.assertIn("blob sha mismatch", str(raised.exception))
        self.assertIn("tools/check_citations.py", str(raised.exception))
        self.assertEqual([], self.blob_calls())

    def test_gh_failure_is_a_named_error(self):
        # gh failing is a named error, never a traceback from _gh_api.
        with self.pinner, mock.patch.dict(os.environ, self.env):
            (self.tmp / "tree.json").unlink()
            with self.assertRaises(ga.GaError) as raised:
                ga.fetch()
        self.assertIn("gh api", str(raised.exception))

    def test_unreadable_tools_directory_is_a_named_error(self):
        # A tools/ directory without search permission makes the filesystem probes fail; that is
        # a named GaError with exit 1, never a raw PermissionError traceback (R2).
        repo, commit = ga.pin()
        dest = self.cache / commit
        self.seed(dest)
        tools_dir = dest / "tools"
        tools_dir.chmod(0o000)
        self.addCleanup(tools_dir.chmod, 0o755)
        wanted = {path: ga.git_blob_sha(text.encode()) for path, text in CONTENTS.items()}
        # gh is the fake of setUp: the test never reaches the network, and no blob is fetched
        with self.pinner, mock.patch.dict(os.environ, self.env), \
                mock.patch.object(ga, "_wanted", return_value=wanted):
            with self.assertRaises(ga.GaError) as raised:
                ga.fetch()
        self.assertIn("cannot stat", str(raised.exception))
        self.assertEqual([], self.blob_calls())

    def test_stale_cached_pyc_is_never_run(self):
        # R1: a same-length edit of the cached validator, byte-compiled and then restored to the
        # pinned bytes with the original mtime, must not run through its stale .pyc.
        good = "def validate(value, schema, path='$'):\n    return [path + ': real error']\n"
        bad = "def validate(value, schema, path='$'):\n    return [][0:0] + [][0:0]      \n"
        self.assertEqual(len(good), len(bad))
        contents = dict(CONTENTS)
        contents["tools/validate_records.py"] = good
        (self.tmp / "tree.json").write_text(json.dumps(tree_fixture(contents)), encoding="utf-8")
        repo, commit = ga.pin()
        dest = self.cache / commit
        self.seed(dest, contents)
        target = dest / "tools" / "validate_records.py"
        stat = target.stat()
        target.write_text(bad, encoding="utf-8")
        py_compile.compile(str(target))  # writes tools/__pycache__ for the edited source
        target.write_text(good, encoding="utf-8")
        os.utime(target, (stat.st_atime, stat.st_mtime))  # the .pyc now looks fresh
        ga._validator = None
        self.addCleanup(setattr, ga, "_validator", None)
        with self.pinner, mock.patch.dict(os.environ, self.env):
            errors = ga.validate(-1, {"type": "integer", "minimum": 0})
        self.assertEqual(["$: real error"], errors)
        # Nothing left or written: the cache holds source only.
        self.assertEqual([], list(dest.rglob("__pycache__")))
        self.assertEqual([], list(dest.rglob("*.pyc")))

    def test_stale_pyc_under_a_pycache_prefix_is_never_run(self):
        # Round 3 R1: bytecode redirected by PYTHONPYCACHEPREFIX (sys.pycache_prefix) lies
        # outside the cache, where fetch() cannot delete it. A same-length edit of the cached
        # validator, compiled under such a prefix and then restored to the pinned bytes with the
        # original mtime, must still not run: the validator is executed from its verified source.
        good = "def validate(value, schema, path='$'):\n    return [path + ': real error']\n"
        bad = "def validate(value, schema, path='$'):\n    return [][0:0] + [][0:0]      \n"
        self.assertEqual(len(good), len(bad))
        contents = dict(CONTENTS)
        contents["tools/validate_records.py"] = good
        (self.tmp / "tree.json").write_text(json.dumps(tree_fixture(contents)), encoding="utf-8")
        repo, commit = ga.pin()
        dest = self.cache / commit
        self.seed(dest, contents)
        target = dest / "tools" / "validate_records.py"
        prefix = self.tmp / "pycache-prefix"
        with mock.patch.object(sys, "pycache_prefix", str(prefix)):
            stat = target.stat()
            target.write_text(bad, encoding="utf-8")
            py_compile.compile(str(target))  # the stale .pyc lands under the prefix
            target.write_text(good, encoding="utf-8")
            os.utime(target, (stat.st_atime, stat.st_mtime))  # the .pyc now looks fresh
            self.assertEqual(1, len(list(prefix.rglob("validate_records*.pyc"))))
            ga._validator = None
            self.addCleanup(setattr, ga, "_validator", None)
            with self.pinner, mock.patch.dict(os.environ, self.env):
                errors = ga.validate(-1, {"type": "integer", "minimum": 0})
        self.assertEqual(["$: real error"], errors)


class WrapperPassThroughTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def stub_cache(self, tool: str) -> Path:
        cache = self.tmp / "cache"
        target = cache / tool
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(STUB_TOOL, encoding="utf-8")
        return cache

    def recorded(self, cache: Path, tool: str) -> str:
        return (cache / tool).with_name(Path(tool).name + ".args").read_text(encoding="utf-8")

    def test_verify_evidence_passes_arguments_and_exit_code(self):
        cache = self.stub_cache(ga.VERIFY_EVIDENCE)
        with mock.patch.object(ga, "fetch", return_value=cache):
            code = verify_evidence.main(["E900", "--local", "somewhere"])
        self.assertEqual(7, code)
        self.assertEqual("E900\n--local\nsomewhere",
                         self.recorded(cache, ga.VERIFY_EVIDENCE))

    def test_check_citations_passes_arguments_and_exit_code(self):
        cache = self.stub_cache(ga.CHECK_CITATIONS)
        with mock.patch.object(ga, "fetch", return_value=cache):
            code = check_citations.main(["findings/F001.md", "--runs", "runs"])
        self.assertEqual(7, code)
        self.assertEqual("findings/F001.md\n--runs\nruns",
                         self.recorded(cache, ga.CHECK_CITATIONS))

    def test_wrapper_reports_the_ga_error_by_name_and_exits_1(self):
        for module in (verify_evidence, check_citations):
            buffer = io.StringIO()
            with mock.patch.object(ga, "fetch",
                                   side_effect=ga.GaError("blob sha mismatch for x: cache has a")):
                with contextlib.redirect_stdout(buffer):
                    code = module.main(["E900"])
            self.assertEqual(1, code, module.__name__)
            self.assertIn("blob sha mismatch", buffer.getvalue())

    def test_launch_failure_is_a_named_error_and_exits_1(self):
        # R3: the subprocess failing to start (PermissionError, FileNotFoundError) is a named
        # error with exit 1, never a traceback from either wrapper's main().
        for module, tool in ((verify_evidence, ga.VERIFY_EVIDENCE),
                             (check_citations, ga.CHECK_CITATIONS)):
            cache = self.stub_cache(tool)
            for failure in (PermissionError(13, "Permission denied"),
                            FileNotFoundError(2, "No such file or directory")):
                buffer = io.StringIO()
                with mock.patch.object(ga, "fetch", return_value=cache), \
                        mock.patch.object(ga.subprocess, "run", side_effect=failure), \
                        contextlib.redirect_stdout(buffer):
                    code = module.main(["E900"])
                self.assertEqual(1, code, (module.__name__, failure))
                self.assertIn("cannot run", buffer.getvalue())

    def test_fetched_tool_never_runs_stale_pyc_under_a_pycache_prefix(self):
        # Round 3 R1: a fetched tool imports the validator beside it. With PYTHONPYCACHEPREFIX
        # set, that import would read bytecode from the prefix, outside the cache fetch() cleans;
        # a same-length edit compiled there and then restored must not run through any wrapper.
        cache = (self.tmp / "cache").resolve()
        tools_dir = cache / "tools"
        tools_dir.mkdir(parents=True)
        importer = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
            "import validate_records\n"
            "sys.exit(validate_records.CODE)\n"
        )
        for tool in (ga.VERIFY_EVIDENCE, ga.CHECK_CITATIONS, ga.ARTIFACT_TOOL):
            (cache / tool).write_text(importer, encoding="utf-8")
        validator = cache / ga.VALIDATOR
        validator.write_text("CODE = 3\n", encoding="utf-8")
        stat = validator.stat()
        validator.write_text("CODE = 4\n", encoding="utf-8")
        prefix = self.tmp / "pycache-prefix"
        compiled = subprocess.run(
            [sys.executable, "-c", "import py_compile, sys; py_compile.compile(sys.argv[1])",
             str(validator)],
            env={**os.environ, "PYTHONPYCACHEPREFIX": str(prefix)},
            capture_output=True, text=True, timeout=60)
        self.assertEqual(0, compiled.returncode, compiled.stderr)
        validator.write_text("CODE = 3\n", encoding="utf-8")
        os.utime(validator, (stat.st_atime, stat.st_mtime))  # the .pyc now looks fresh
        self.assertEqual(1, len(list(prefix.rglob("validate_records*.pyc"))))
        self.assertEqual([], list(cache.rglob("__pycache__")))
        for module in (verify_evidence, check_citations, register_artifact):
            with mock.patch.object(ga, "fetch", return_value=cache), \
                    mock.patch.dict(os.environ, {"PYTHONPYCACHEPREFIX": str(prefix)}):
                code = module.main([])
            self.assertEqual(3, code, module.__name__)

    def test_a_tool_killed_by_a_signal_terminates_the_wrapper_with_it(self):
        # R4: a negative return code must not become 241 (SIGTERM) or 137 (SIGKILL) through
        # sys.exit(); the wrapper process itself dies of the same signal, SIGKILL included, whose
        # disposition cannot be reset (round 3 R2). Driven through a real subprocess per wrapper.
        signal_tool = (
            "import os, signal, sys\n"
            "sig = signal.{sig}\n"
            "if sig != signal.SIGKILL:\n"
            "    signal.signal(sig, signal.SIG_DFL)\n"
            "os.kill(os.getpid(), sig)\n"
        )
        driver = (
            "import importlib, sys\n"
            "from pathlib import Path\n"
            "from unittest import mock\n"
            "sys.path.insert(0, {root!r})\n"
            "from tools import ga\n"
            "module = importlib.import_module({name!r})\n"
            "with mock.patch.object(ga, 'fetch', return_value=Path({cache!r})):\n"
            "    sys.exit(module.main([]))\n"
        )
        for sig, expected in (("SIGTERM", -15), ("SIGKILL", -9)):
            for module, tool in ((verify_evidence, ga.VERIFY_EVIDENCE),
                                 (check_citations, ga.CHECK_CITATIONS),
                                 (register_artifact, ga.ARTIFACT_TOOL)):
                cache = self.stub_cache(tool)
                (cache / tool).write_text(signal_tool.format(sig=sig), encoding="utf-8")
                child = subprocess.run(
                    [sys.executable, "-c",
                     driver.format(root=str(REPO_ROOT), name=module.__name__, cache=str(cache))],
                    capture_output=True, text=True, timeout=60)
                self.assertEqual(expected, child.returncode,
                                 (sig, module.__name__, child.stderr))
                self.assertTrue(child.stderr.strip() == "" or
                                "Traceback" not in child.stderr, (sig, module.__name__))


if __name__ == "__main__":
    unittest.main()
