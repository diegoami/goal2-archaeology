"""The kit vendors as one folder (runtime/original_match/__init__.py, README): copied alone, with nothing else of runtime/ on
the path, it imports, its check imports, and its cache check runs (goal2#483: check.py and assets.py imported runtime's
fileopts by name, which a vendored copy does not have). runtime's own `fileopts` is the kit's module."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OneFolder(unittest.TestCase):
    def test_a_copy_of_the_kit_alone_imports_and_checks_its_cache(self):
        tmp = Path(tempfile.mkdtemp());self.addCleanup(shutil.rmtree, tmp)
        shutil.copytree(ROOT / "runtime/original_match", tmp / "original_match", ignore=shutil.ignore_patterns("__pycache__"))
        code = ("import sys; sys.path.insert(0, sys.argv[1])\n"
                "import original_match.check, original_match.assets as a\n"
                "a.check_cache(sys.argv[1] + '/cache')\n"
                "assert 'fileopts' not in sys.modules, 'a top-level fileopts was imported'\n")
        r = subprocess.run([sys.executable, "-I", "-B", "-c", code, str(tmp)], cwd=tmp, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])

    def test_runtime_fileopts_is_the_kits_module(self):
        sys.path.insert(0, str(ROOT / "runtime"))
        try:
            import fileopts
            from original_match import fileopts as kit
        finally:
            sys.path.remove(str(ROOT / "runtime"))
        self.assertIs(fileopts, kit)


if __name__ == "__main__":
    unittest.main()
