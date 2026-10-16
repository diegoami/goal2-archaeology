#!/usr/bin/env python3
"""E034: every check this experiment reports, run one after another from one commit, outputs stamped.

    python3 -B experiments/E034-kit-competitive/final_runs.py --stamp 20261016x [--skip mutations]

Writes out/<name>-<stamp>.{txt,json,jsonl} (refuses any that exists) and out/final-<stamp>.json (the commit, each
command, its exit code and wall time). The runs: the unit tests; the new tests against origin/main's kit (they must
fail there: base-tests); the kit's check (engine, interactive, goals, knockout) with --json; the E031 shoot-out;
the competitive stamps; the competitive save boundaries; the mutations."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments" / "E034-kit-competitive" / "out"
E = "experiments/E034-kit-competitive/"
BASE_RUNNER = """
import sys, unittest
sys.path.insert(0, {kit!r})
import original_match
assert original_match.__file__.startswith({kit!r}), original_match.__file__
print("kit from", original_match.__file__)
sys.path.insert(1, {root!r})
suite = unittest.defaultTestLoader.loadTestsFromNames(["tests.test_original_match.CompetitiveTests"])
r = unittest.TextTestRunner(verbosity=2).run(suite)
print("failures", len(r.failures), "errors", len(r.errors), "run", r.testsRun)
sys.exit(0 if not r.wasSuccessful() and len(r.failures) + len(r.errors) == r.testsRun else 1)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", required=True)
    ap.add_argument("--skip", nargs="*", default=[])
    a = ap.parse_args()
    s = a.stamp
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "runtime", "tests", E], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    tmp = tempfile.mkdtemp()
    subprocess.run(["git", "archive", "origin/main", "runtime/original_match", "-o", f"{tmp}/kit.tar"], cwd=ROOT, check=True)
    subprocess.run(["tar", "-xf", f"{tmp}/kit.tar", "-C", tmp], check=True)
    py = [sys.executable, "-B"]
    runs = [
        ("tests", f"tests-{s}.txt", py + ["-m", "unittest", "tests.test_original_match"]),
        ("base-tests", f"base-tests-{s}.txt", py + ["-c", BASE_RUNNER.format(kit=f"{tmp}/runtime", root=str(ROOT))]),
        ("check", f"check-{s}.txt", py + ["-m", "original_match.check", "--cache", ".cache", "--json",
                                         str(OUT / f"check-{s}.json")]),
        ("e031-shootout", f"e031-shootout-{s}.txt", py + [E + "e031_shootout.py", "--out", str(OUT / f"e031-shootout-{s}.json")]),
        ("stamps", f"stamps-competitive-{s}.txt", py + [E + "stamps_competitive.py", "--log",
                                                        str(OUT / f"stamps-competitive-{s}.jsonl")]),
        ("save-boundaries", f"save-boundaries-competitive-{s}.txt", py + [E + "save_boundaries_competitive.py", "--log",
                                                                          str(OUT / f"save-boundaries-competitive-{s}.jsonl")]),
        ("mutations", f"mutations-{s}.txt", py + ["tests/mutations_original_match.py"]),
    ]
    report = {"commit": commit, "dirty": dirty, "stamp": s, "runs": []}
    final = OUT / f"final-{s}.json"
    for name, out, cmd in runs:
        if name in a.skip:
            continue
        path = OUT / out
        if path.exists() or final.exists():
            sys.exit(f"refused: {path} or {final} exists")
        t = time.time()
        with path.open("x") as f:
            p = subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONPATH="runtime"))
        report["runs"].append({"name": name, "output": out, "command": " ".join(cmd), "exit": p.returncode,
                               "wall_s": round(time.time() - t, 1)})
        print(name, p.returncode, round(time.time() - t, 1), flush=True)
    with final.open("x") as f:
        json.dump(report, f, indent=1)


if __name__ == "__main__":
    main()
