#!/usr/bin/env python3
"""Run every check the PR quotes and write their output to out/checks.txt, failing closed: each
check's own exit status decides, the output is cut only after the check has finished, and the file
ends with ALL PASSED or FAILED and the names of the checks that failed (exit 1). No game is run.
Usage: python3 experiments/E031-play-the-game/checks.py [--out FILE]"""
import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E = "experiments/E031-play-the-game"
CHECKS = [  # (name, argv, how many trailing lines of its output to quote; 0 = all)
    ("verify_saves", ["python3", f"{E}/verify_saves.py"], 1),
    ("progress", ["python3", f"{E}/progress.py", "g1", "--md", f"{E}/out/g1/progress.md"], 6),
    ("claims", ["python3", f"{E}/claims.py"], 0),
    ("check_links", ["python3", "tools/check_links.py"], 1),
    ("unit tests", ["python3", "-m", "unittest", "tests.test_agent_permissions", "tests.test_screens",
                    "tests.test_e031_checks"], 3),
]


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def run(checks, out_path, cwd=ROOT):
    lines, failed = [], []
    dirty = git("status", "--porcelain", "--", E, "docs", f":!{E}/out/checks.txt")
    lines.append(f"commit {git('rev-parse', '--short', 'HEAD')} (worktree clean apart from this file: "
                 f"{'no' if dirty else 'yes'}), {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    for name, argv, tail in checks:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
        out = (p.stdout + p.stderr).rstrip("\n").split("\n")
        lines += ["", "$ " + " ".join(argv) + (f"   (last {tail} lines)" if tail else "")]
        lines += out[-tail:] if tail else out
        lines.append(f"exit {p.returncode}")
        if p.returncode != 0:
            failed.append(name)
    lines += ["", f"FAILED: {', '.join(failed)}" if failed else "ALL PASSED"]
    Path(out_path).write_text("\n".join(lines) + "\n")
    return 1 if failed else 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "out" / "checks.txt"))
    a = ap.parse_args(argv)
    rc = run(CHECKS, a.out)
    print(Path(a.out).read_text(), end="")
    return rc


if __name__ == "__main__":
    sys.exit(main())
