#!/usr/bin/env python3
"""Which checks a CI run needs (issue #297; the owner, 2026-10-17: fewer CI minutes).

    python3 tools/ci_gate.py decide    # in the workflow: print `tier=<name>` for $GITHUB_OUTPUT
    python3 tools/ci_gate.py run-tests --tier fast|full    # the unit suite, minus SLOW when fast

A change is classified by the files it touches, into four tiers (a higher tier includes the lower):

  none  only measured outputs (`*.log`, `experiments/**/out/**`): nothing runs.
  docs  prose no test reads: links, citations and the no-original-file check.
  fast  anything else: also the harness tests, tests/static and every unit test except SLOW.
  full  the paths SLOW reads (traced, notes/T297/slow-module-deps-20261017.json), the CI
        definition itself, a nightly run on main, a manual run: the whole suite.

On a pull request the tier is that of the whole PR (merge-base..head), except on a push to a PR
(`synchronize`), where it is that of the push (before..after) when the previous head's `checks`
job already succeeded: that success covered the PR's other files, so the push needs only the tier
of what it changed.  Anything unknown (a first run, a reopen, a force-push whose old head is gone,
a previous head whose run failed, was cancelled or never ran) falls back to the whole PR.  So a
green `checks` job on a head always means: every obligation of the whole PR's diff has been met.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NONE, DOCS, FAST, FULL = 0, 1, 2, 3
NAMES = {NONE: "none", DOCS: "docs", FAST: "fast", FULL: "full"}

# Measured outputs (the rule of 2026-10-12): a push of these alone runs nothing.
OUTPUT_RE = re.compile(r"(\.log$|^experiments/.*/out/)")

# The unit-test modules that take about 5 of the 6.5 minutes of a run (tests/ module times, T297).
# They run only in the full tier.  Each reads the paths of FULL_PATHS below.
SLOW = (
    "test_emul_match",
    "test_emul_watched",
    "test_human_keys",
    "test_human_record",
    "test_screens_video",
    "test_e032_recheck",
)

# What SLOW (and the harness running them) read or execute, from an audit-hook trace of each
# module (notes/T297/slow-module-deps-20261017.json, tracer notes/T297/trace_deps.py), widened
# to the whole directory where a module's traced files sit.  A path missing here lets a PR
# skip a slow module it could break: the nightly full run on main (workflow `schedule`) is the
# net for that, and tests/test_ci_gate.py checks each prefix names something that exists.
FULL_PATHS = (
    "runtime/",
    "experiments/E011-q010-watched-engine/",
    "experiments/E015-human-playthrough/",
    "experiments/E021-m0-whole-match/",
    "experiments/E022-video-screens/",
    "experiments/E032-match-engine-inventory/",
    "runs/E011/",
    "runs/E015/",
    "static/goal-exe/code/",
    "static/screens/",
    "tools/screens/",
    "artifacts/known.json",
    "archaeology.json",
    "tests/netskip.py",
    "tests/fixtures/",
    "tools/ci_gate.py",
    ".github/",
) + tuple(f"tests/{m}.py" for m in SLOW)

# tools/*.py at the top level are imported by tests/test_human_keys.py (the `tools` package).
FULL_RE = re.compile(r"^tools/[^/]+\.py$")

# Prose that some test or harness script reads (make-brief.mjs reads docs/process.md section 5
# and docs/review-brief.md; test_e031_checks the play guide; test_e032_compare the plan).
DOCS_READ_BY_TESTS = (
    "docs/process.md",
    "docs/review-brief.md",
    "docs/play-guide.md",
    "docs/match-engine-plan.md",
)
DOCS_RE = re.compile(r"^([^/]+\.md|docs/.*|notes/.*|spec/.*)$")


def classify(path):
    """The tier one changed file needs."""
    if OUTPUT_RE.search(path):
        return NONE
    if any(path.startswith(p) if p.endswith("/") else path == p for p in FULL_PATHS) or FULL_RE.match(path):
        return FULL
    if DOCS_RE.match(path) and path not in DOCS_READ_BY_TESTS:
        return DOCS
    return FAST


def tier_of(paths):
    return max((classify(p) for p in paths), default=NONE)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def changed(a, b, three_dots=False):
    """Files changed between two commits, or None when git cannot tell (a commit is missing)."""
    r = git("diff", "--name-only", f"{a}...{b}" if three_dots else f"{a}..{b}")
    return r.stdout.split("\n")[:-1] if r.returncode == 0 else None


def previous_head_succeeded(repo, sha, runner=subprocess.run):
    """Did the `checks` job of the workflow succeed on commit `sha`?  False when it did not run."""
    r = runner(["gh", "api", f"repos/{repo}/commits/{sha}/check-runs?per_page=100"], capture_output=True, text=True)
    if r.returncode != 0:
        return False
    try:
        runs = json.loads(r.stdout)["check_runs"]
    except (ValueError, KeyError):
        return False
    return any(c.get("name") == "checks" and c.get("conclusion") == "success" for c in runs)


def decide(env, diff=changed, succeeded=previous_head_succeeded):
    """(tier, reason) for the event described by `env` (the workflow's environment)."""
    event = env.get("EVENT", "")
    if event != "pull_request":
        if event == "schedule":
            # nightly net on main: only when something that is more than prose has landed since
            r = git("log", "--since=26 hours ago", "--name-only", "--pretty=format:", "HEAD")
            t = tier_of([p for p in r.stdout.split("\n") if p])
            return (FULL, "nightly: code landed on main") if t >= FAST else (NONE, "nightly: nothing but prose landed")
        return FULL, f"{event or 'manual'} run"
    base, head, before = env["BASE"], env["HEAD"], env.get("BEFORE", "")
    whole = diff(base, head, three_dots=True)
    if whole is None:
        return FULL, "the PR's diff cannot be read"
    pr_tier = tier_of(whole)
    if env.get("ACTION") == "synchronize" and before:
        push = diff(before, head)
        if push is not None:
            t = tier_of(push)
            if t >= pr_tier:
                return pr_tier, "the push touches the PR's highest tier"
            if succeeded(env["REPO"], before):
                return t, f"push of tier {NAMES[t]}; the previous head's checks passed (PR tier {NAMES[pr_tier]})"
            return pr_tier, "the previous head's checks did not pass: the whole PR"
    return pr_tier, f"the whole PR (event {env.get('ACTION', '')})"


def select_suite(tier):
    """The unit tests of `tests/`, as `python3 -m unittest discover -s tests` finds them, minus
    the SLOW modules when the tier is fast."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))

    def flatten(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                yield from flatten(t)
            else:
                yield t

    keep = unittest.TestSuite()
    for t in flatten(suite):
        if tier == "fast" and type(t).__module__.rsplit(".", 1)[-1] in SLOW:
            continue
        keep.addTest(t)
    return keep


def run_tests(tier):
    return 0 if unittest.TextTestRunner(verbosity=2).run(select_suite(tier)).wasSuccessful() else 1


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("decide")
    rt = sub.add_parser("run-tests")
    rt.add_argument("--tier", choices=["fast", "full"], required=True)
    a = ap.parse_args(argv)
    if a.cmd == "run-tests":
        return run_tests(a.tier)
    env = {k: os.environ.get(k, "") for k in ("EVENT", "ACTION", "BASE", "HEAD", "BEFORE", "REPO")}
    tier, why = decide(env)
    print(f"tier={NAMES[tier]} ({why})", file=sys.stderr)
    print(f"tier={NAMES[tier]}")
    print(f"quick={'true' if tier >= DOCS else 'false'}")
    print(f"code={'true' if tier >= FAST else 'false'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
