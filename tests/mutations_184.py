#!/usr/bin/env python3
"""Fix #184: mutation check of tests/test_asset_cache.py, in memory (no tracked file is edited).

    python3 -B tests/mutations_184.py

Same pattern as tests/mutations_t47.py: each mutation replaces text(s) in check.py's source, compiles the
mutated module in a CHILD process, puts it in sys.modules and runs the named tests; killed = one fails."""
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = "experiments/E021-m0-whole-match/check.py"
T = "tests.test_asset_cache."
TWO = [T + "TwoProcessTests.test_two_first_runs_end_with_the_right_file_and_no_partial"]
COMMON = [T + "CommonCacheTests"]
FAIL = [T + "FailureTests"]
RUN = "subprocess.run(cmd[:-1] + [str(tmp)], check=True)"
EXISTS = "if not (tmp / name).is_file():"

# (name, [(old, new), ...], tests that must fail)
MUTATIONS = [
    ("no temp name, no rename: download straight into the cache dir",
     [(RUN + "\n                    " + EXISTS, "subprocess.run(cmd, check=True)\n                    if not path.is_file():"),
      ("os.replace(tmp / name, path)", "pass")], TWO),
    ("common cache never consulted", [("if common is not None and (common / name).is_file()", "if False and (common / name).is_file()")], COMMON),
    ("common cache: file-exists guard removed", [("if common is not None and (common / name).is_file()", "if common is not None")], COMMON),
    ("common cache: None guard removed", [("if common is not None and (common / name).is_file()", "if (common / name).is_file()")], COMMON),
    ("common_dl without .parent", [("Path(r.stdout.strip()).parent / \".cache/dl\"", "Path(r.stdout.strip()) / \".cache/dl\"")], COMMON),
    ("common_dl: no path-format absolute", [("\"--path-format=absolute\", ", "")], COMMON),
    ("common cache copy goes to the cache dir directly, not renamed", [("shutil.copyfile(common / name, tmp / name)", "shutil.copyfile(common / name, tmp / name); (tmp / name).rename(path); (tmp / name).write_bytes(b'')")], COMMON),
    ("cache check always misses", [("    if not path.is_file():\n        DL.mkdir", "    if True:\n        DL.mkdir")], COMMON),
    ("failed download not turned into SystemExit", [("except (subprocess.CalledProcessError, OSError) as e:", "except ZeroDivisionError as e:")], FAIL),
    ("empty download not detected", [(EXISTS, "if False:")], FAIL),
    ("temp directory not removed", [("        finally:\n            shutil.rmtree(tmp, ignore_errors=True)\n", "        finally:\n            pass\n")], FAIL),
    ("message names the temp dir, not the cache dir", [("\"--pattern\", name, \"--dir\", str(DL)]", "\"--pattern\", name, \"--dir\", str(tmp)]")], FAIL),
    ("main: assets not fetched first", [("    for p in records:       # every asset first", "    for p in []:       # every asset first")], FAIL),
    ("sha256 check removed", [("    if driver.sha256(data) != entry[\"sha256\"]:\n        raise SystemExit(f\"{path}", "    if False:\n        raise SystemExit(f\"{path}")], COMMON),
]


def child(index):
    name, pairs, tests = MUTATIONS[index]
    sys.path[:0] = [str(ROOT), str(ROOT / "runtime/emul"), str(ROOT / "experiments/E021-m0-whole-match"), str(ROOT / "tests")]
    source = (ROOT / CHECK).read_text()
    for old, new in pairs:
        assert source.count(old) >= 1, f"{name}: text not found: {old!r}"
        source = source.replace(old, new, 1)
    import os
    import tempfile
    copy = Path(tempfile.mkdtemp()) / "check_mutated.py"      # for the test's child processes (CHECK_SOURCE seam)
    copy.write_text(source)
    os.environ["CHECK_SOURCE"] = str(copy)
    module = types.ModuleType("check")
    module.__file__ = str(ROOT / CHECK)
    sys.modules["check"] = module
    exec(compile(source, str(ROOT / CHECK), "exec"), module.__dict__)
    import unittest
    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
    result = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)      # 0: SURVIVED, 1: killed


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        child(int(sys.argv[2]))
    survived = 0
    for i, (name, pairs, tests) in enumerate(MUTATIONS):
        r = subprocess.run([sys.executable, "-B", __file__, "--child", str(i)], capture_output=True, text=True)
        killed = r.returncode == 1
        err = r.returncode not in (0, 1)
        print(("KILLED  " if killed else "ERROR   " if err else "SURVIVED"), name + (": " + r.stderr.strip().splitlines()[-1] if err else ""))
        survived += not killed
    print(f"{len(MUTATIONS)} mutations, {survived} not killed")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
