"""Fix #315: Ghidra's work folder has no dot element, whatever the repository's path and TMPDIR are.

Ghidra 12.1.4 refuses a project path with an element that starts with '.', and the harness's
isolated worktrees live under <repository>/.claude/worktrees/. tools/static/ghidra_work.py makes the
folder; tools/static/decompile.sh uses it. A stub stands in for Ghidra's analyzeHeadless in the
wrapper test: it applies Ghidra's rule to the project path and records the path (the real Ghidra
is exercised by GhidraMappingTests in test_decompile.py, which also uses this folder).
"""
import os
import shutil
import stat
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "static"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_work  # noqa: E402
from test_decompile import EXE  # noqa: E402  (the released GOAL.EXE, or None)

STUB = """#!/bin/sh
# stands in for Ghidra's analyzeHeadless: $1 is the project folder; records what it was given
case "/$1/" in
  */.*) echo "ERROR Abort due to Headless analyzer error: Path element starting with '.' is not permitted" >&2; exit 1 ;;
esac
{
  echo "PROJECT=$1"
  echo "TMPDIR=$TMPDIR"
  echo "TMP=$TMP"
  echo "TEMP=$TEMP"
  shift
  for a in "$@"; do echo "ARG=$a"; done
} > "$STUB_RECORD"
exit 1
"""
NOOP_CHECK = "import sys\nsys.exit(0)\n"  # stands in for check_annotations.py, which is not under test here
FAKE_JAVA = """#!/bin/sh
echo 'openjdk version "21.0.12.1" 2026-08-18 LTS' >&2
"""


def dotted(path) -> list[str]:
    return [p for p in Path(path).parts if p.startswith(".")]


class WorkFolderTests(unittest.TestCase):
    def setUp(self):
        self.base = ghidra_work.new_work_dir("test-fixture")  # dot-free by construction
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)

    def env(self, **extra):
        return dict(HOME=str(self.base / "home"), **extra)

    def test_default_base_is_under_home_whatever_tmpdir_and_cwd_are(self):
        (self.base / "home").mkdir()
        hidden = self.base / ".claude" / "worktrees" / "agent-x"
        hidden.mkdir(parents=True)
        old = Path.cwd()
        os.chdir(hidden)
        try:
            work = ghidra_work.new_work_dir("decompile", self.env(TMPDIR=str(hidden)))
        finally:
            os.chdir(old)
        self.assertEqual(work.parent, self.base / "home" / "goal2-ghidra-work")
        self.assertEqual(dotted(work), [])
        self.assertTrue(work.is_dir())
        self.assertEqual(list(work.iterdir()), [])
        self.assertTrue(work.name.startswith("decompile-"))

    def test_each_call_makes_a_new_folder(self):
        (self.base / "home").mkdir()
        a, b = (ghidra_work.new_work_dir("u", self.env()) for _ in range(2))
        self.assertNotEqual(a, b)

    def test_unit_names_cannot_escape_or_add_a_dot(self):
        (self.base / "home").mkdir()
        work = ghidra_work.new_work_dir("../.evil/x", self.env())
        self.assertEqual(work.parent, self.base / "home" / "goal2-ghidra-work")
        self.assertEqual(dotted(work), [])

    def test_a_home_with_a_dot_element_is_refused_with_a_message(self):
        home = self.base / ".hidden" / "home"
        home.mkdir(parents=True)
        with self.assertRaisesRegex(ghidra_work.DottedPathError, r"element starting with '\.'"):
            ghidra_work.new_work_dir("u", dict(HOME=str(home)))

    def test_a_named_base_that_is_relative_or_dotted_or_a_link_into_a_dotted_folder_is_refused(self):
        hidden = self.base / ".hidden"
        hidden.mkdir()
        link = self.base / "link"
        link.symlink_to(hidden)
        for named in ("relative/path", str(hidden / "w"), str(link)):
            with self.subTest(named=named):
                with self.assertRaises(ghidra_work.DottedPathError):
                    ghidra_work.new_work_dir("u", dict(HOME=str(self.base), GOAL2_GHIDRA_WORK=named))

    def test_command_line_prints_a_path_or_exits_1_with_the_reason(self):
        hidden_home = self.base / ".h"
        hidden_home.mkdir()
        run = subprocess.run([sys.executable, str(ROOT / "tools" / "static" / "ghidra_work.py"), "new", "u"],
                             env=dict(os.environ, HOME=str(hidden_home)), capture_output=True, text=True)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("element starting with '.'", run.stderr)
        self.assertEqual(run.stdout, "")


@unittest.skipIf(EXE is None, "needs the released GOAL.EXE in .cache/ (python3 tools/fetch_artifact.py goal2-67cf27d6)")
class WrapperFromADottedWorktreeTests(unittest.TestCase):
    """decompile.sh run from <repo>/.claude/worktrees/agent-x with a TMPDIR inside the worktree."""

    def setUp(self):
        self.fixture = ghidra_work.new_work_dir("test-wrapper")
        self.addCleanup(shutil.rmtree, self.fixture, ignore_errors=True)
        self.home = self.fixture / "home"
        self.repo = self.fixture / "repo" / ".claude" / "worktrees" / "agent-x"
        tools = self.repo / "tools" / "static"
        tools.mkdir(parents=True)
        for name in ("decompile.sh", "unlzexe.py", "ghidra_work.py"):
            shutil.copy2(ROOT / "tools" / "static" / name, tools / name)
        (tools / "check_annotations.py").write_text(NOOP_CHECK)
        self.annotations = self.fixture / "annotations"
        self.annotations.mkdir()
        self.tmp = self.repo / ".cache" / "tmp"
        self.tmp.mkdir(parents=True)
        self.home.mkdir()
        ghidra = self.fixture / "ghidra"
        (ghidra / "support").mkdir(parents=True)
        (ghidra / "Ghidra").mkdir()
        (ghidra / "Ghidra" / "application.properties").write_text(
            "application.version=12.1.4\napplication.revision.ghidra=stub\n")
        self.write_exec(ghidra / "support" / "analyzeHeadless", STUB)
        jdk = self.fixture / "jdk-21"
        (jdk / "bin").mkdir(parents=True)
        self.write_exec(jdk / "bin" / "java", FAKE_JAVA)
        self.record = self.fixture / "record.txt"
        self.env = dict(os.environ, HOME=str(self.home), TMPDIR=str(self.tmp), GHIDRA_HOME=str(ghidra),
                        JAVA_HOME=str(jdk), STUB_RECORD=str(self.record))
        self.env.pop("KEEP_WORK", None)
        self.env.pop("GOAL2_GHIDRA_WORK", None)

    @staticmethod
    def write_exec(path: Path, text: str):
        path.write_text(text)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_wrapper(self, *flags, exe=None, **extra) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["bash", str(self.repo / "tools" / "static" / "decompile.sh"), *flags,
                               str(exe or EXE), str(self.fixture / "out")], cwd=self.repo,
                              env=dict(self.env, **extra), capture_output=True, text=True, timeout=120)

    def recorded(self) -> tuple[Path, dict[str, str], list[str]]:
        """What the stub received: the project folder, TMPDIR/TMP/TEMP, and the other arguments."""
        lines = self.record.read_text().splitlines()
        env = dict(line.split("=", 1) for line in lines if not line.startswith("ARG="))
        args = [line[4:] for line in lines if line.startswith("ARG=")]
        return Path(env.pop("PROJECT")), env, args

    def test_the_project_path_has_no_dot_element_and_the_work_folder_is_cleaned(self):
        self.assertNotEqual(dotted(self.repo), [], "the fixture must sit under a dot element")
        run = self.run_wrapper()
        self.assertNotIn("Path element", run.stderr)
        self.assertTrue(self.record.exists(), run.stderr)  # the stub accepted the project path
        project, _, _ = self.recorded()
        self.assertEqual(dotted(project), [], project)
        self.assertEqual(project.parent.parent, self.home / "goal2-ghidra-work")
        self.assertEqual(list((self.home / "goal2-ghidra-work").iterdir()), [], "work folder left behind")
        self.assertEqual(list(self.tmp.iterdir()), [], "nothing was made in the dotted TMPDIR")

    def test_ghidras_temporary_folders_are_the_dot_free_work_folder(self):
        # the environment says TMPDIR is inside the dotted worktree; TMP and TEMP are set to it too
        run = self.run_wrapper(TMP=str(self.tmp), TEMP=str(self.tmp))
        project, env, _ = self.recorded()
        work = project.parent
        for name in ("TMPDIR", "TMP", "TEMP"):
            with self.subTest(name=name):
                self.assertEqual(Path(env[name]), work, run.stderr)
                self.assertEqual(dotted(env[name]), [])
                self.assertEqual(work.parent, self.home / "goal2-ghidra-work")

    def test_ghidra_gets_the_options_the_decompile_needs(self):
        self.run_wrapper()
        project, _, args = self.recorded()
        work = str(project.parent)
        scripts = self.repo / "static" / "goal-exe" / "routines.tsv"
        self.assertEqual(project.name, "project")
        self.assertEqual(args, [
            "goal", "-import", f"{work}/goal.exe", "-loader", "MzLoader", "-processor", "x86:LE:16:Real Mode",
            "-scriptPath", str(self.repo / "tools" / "static" / "ghidra"),
            "-preScript", "GoalSetup.java", str(scripts), f"{work}/segmap.tsv",
            "-postScript", "GoalDecompile.java", f"{work}/segmap.tsv", f"{work}/raw.txt", "600",
            "-deleteProject", "-max-cpu", "2"])

    def test_the_annotations_form_adds_the_annotation_script_before_the_decompile(self):
        self.run_wrapper("--annotations", str(self.annotations))
        project, _, args = self.recorded()
        work = str(project.parent)
        note = ["-postScript", "GoalAnnotate.java", f"{work}/segmap.tsv", str(self.annotations)]
        at = args.index("GoalAnnotate.java") - 1
        self.assertEqual(args[at:at + 4], note)
        self.assertLess(at, args.index("GoalDecompile.java"))

    def test_an_early_failure_after_the_folder_is_made_leaves_nothing(self):
        garbage = self.fixture / "GOAL.EXE"
        garbage.write_bytes(b"not an executable")
        run = self.run_wrapper(exe=garbage)
        self.assertNotEqual(run.returncode, 0)
        self.assertFalse(self.record.exists(), "the failure must come before Ghidra")
        self.assertEqual(list((self.home / "goal2-ghidra-work").iterdir()), [], run.stderr)

    def test_mapping_tests_remove_their_folder_when_the_probe_fails(self):
        env = dict(self.env, HOME=str(self.home))
        run = subprocess.run([sys.executable, "-m", "unittest", "test_decompile.GhidraMappingTests"],
                             cwd=ROOT / "tests" / "static", env=env, capture_output=True, text=True,
                             timeout=120)
        self.assertNotEqual(run.returncode, 0, "the stub makes the probe fail")
        self.assertIn("Ghidra probe failed", run.stderr)
        self.assertTrue(self.record.exists(), "the stub must have been reached")
        self.assertEqual(list((self.home / "goal2-ghidra-work").iterdir()), [], run.stderr)

    def test_keep_work_keeps_the_folder(self):
        run = self.run_wrapper(KEEP_WORK="1")
        kept = list((self.home / "goal2-ghidra-work").iterdir())
        self.assertEqual(len(kept), 1, run.stderr)
        self.assertIn(str(kept[0]), run.stderr)

    def test_a_dotted_work_base_stops_the_wrapper_with_the_reason(self):
        run = self.run_wrapper(GOAL2_GHIDRA_WORK=str(self.fixture / ".dotted"))
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("ghidra_work.py: Ghidra's work folder", run.stderr)
        self.assertFalse(self.record.exists())


if __name__ == "__main__":
    unittest.main()
