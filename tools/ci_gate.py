#!/usr/bin/env python3
"""Which checks a CI run needs (issue #297; the owner, 2026-10-17: fewer CI minutes).

    python3 tools/ci_gate.py decide    # in the workflow: print `key=value` lines for $GITHUB_OUTPUT
    python3 tools/ci_gate.py run-tests [--modules test_a,test_b]    # the unit suite

A change is classified by the files it touches into what it obliges CI to run:

  nothing  only measured outputs (`*.log`, `experiments/**/out/**`).
  quick    prose no test reads (docs): links, citations and the no-original-file check.
  code     anything else: also the harness tests, tests/static and every unit test except SLOW.
  modules  a file one of the SLOW test modules reads obliges that module (SLOW_DEPS); the CI
           definition, a manual run and a nightly run on main oblige all of them.

On a pull request the obligation is that of the whole PR (merge-base..head), except on a push to a
PR (`synchronize`), where it is that of the push (before..after) when the previous head's `checks`
job already succeeded: that success covered everything else the PR changes, so the push needs only
what it changed oblige.  Anything unknown (a first run, a reopen, a force-push whose old head is
gone, a previous head whose run failed, was cancelled or never ran) falls back to the whole PR.  So
a green `checks` job on a head always means: every obligation of the whole PR's diff has been met.
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

# Measured outputs (the rule of 2026-10-12): a push of these alone runs nothing.
OUTPUT_RE = re.compile(r"(\.log$|^experiments/.*/out/)")

# The unit-test modules that take 282 of the 360 seconds of a CI run's unit suite (per-test timestamps of
# run 39031916644, notes/T297/ci-module-times-20261017.txt), and test_emul_match, which took nothing in CI
# until unicorn was installed there (issue #304: it is 187 s on the author's machine, 180 s of them one
# test).  Each module's list is the repository paths it reads, from an audit-hook trace of the module
# (notes/T297/slow-module-deps-20261017.json, notes/T304/deps-test_emul_match-20261017.json; tracer
# notes/T297/trace_deps.py), widened to the whole directory where its traced files sit.  A prefix ending in
# "/" is a directory.  A path missing here lets a PR skip a module it could break: the nightly full run on
# main (workflow `schedule`) is the net for that.  tests/test_ci_gate.py requires every traced path to be
# covered and every prefix to exist.  test_emul_watched (14 s) and test_emul_skip_ret (0.1 s) are cheap and
# run in the code tier.
_HUMAN = ("runtime/human/", "runtime/driver/", "experiments/E015-human-playthrough/", "tools/ga.py", "tools/net.py",
          "tools/fetch_saves.py", "tools/validate_runs.py", "tests/netskip.py", "runs/E015/",
          "tests/test_human_keys.py", "tests/test_human_record.py")  # each imports the other
SLOW_DEPS = {
    "test_human_keys": _HUMAN + ("artifacts/known.json",),
    "test_human_record": _HUMAN + ("archaeology.json",),
    "test_screens_video": ("runtime/driver/", "tools/screens/", "static/screens/", "experiments/E022-video-screens/",
                           "tests/test_screens_video.py"),
    "test_e032_recheck": ("experiments/E032-match-engine-inventory/", "tests/test_e032_recheck.py"),
    "test_e036_compare": ("experiments/E036-match-port/", "runtime/original_match/", "tests/test_e036_compare.py"),
    # the E011 watchstart savestate it resumes is a release asset (runs/E011/ names it), not a repository file
    "test_emul_match": ("runtime/emul/", "runtime/driver/", "runtime/model/", "experiments/E021-m0-whole-match/",
                        "runs/E011/", "static/goal-exe/code/", "tests/longs_original.py", "tests/test_emul_match.py"),
}
SLOW = tuple(SLOW_DEPS)

# What the CI definition itself obliges: everything.
EVERYTHING_PATHS = (".github/", "tools/ci_gate.py")

# Prose that some test or harness script reads (make-brief.mjs reads docs/process.md section 5
# and docs/review-brief.md; test_e031_checks the play guide; test_e032_compare the plan).
DOCS_READ_BY_TESTS = (
    "docs/process.md",
    "docs/review-brief.md",
    "docs/play-guide.md",
    "docs/match-engine-plan.md",
)
DOCS_RE = re.compile(r"^([^/]+\.md|docs/.*|notes/.*|spec/.*)$")

QUICK, CODE = "quick", "code"


def _under(path, prefix):
    return path.startswith(prefix) if prefix.endswith("/") else path == prefix


def classify(path):
    """What one changed file obliges: a frozenset of "quick", "code" and slow module names."""
    if OUTPUT_RE.search(path):
        return frozenset()
    if any(_under(path, p) for p in EVERYTHING_PATHS):
        return frozenset({QUICK, CODE, *SLOW})
    hits = {m for m, deps in SLOW_DEPS.items() if any(_under(path, d) for d in deps)}
    if hits:
        return frozenset({QUICK, CODE, *hits})
    if DOCS_RE.match(path) and path not in DOCS_READ_BY_TESTS:
        return frozenset({QUICK})
    return frozenset({QUICK, CODE})


def obligations(paths):
    out = frozenset()
    for p in paths:
        out |= classify(p)
    return out


def name_of(ob):
    """A word for the log: none, docs, fast, full, or fast+N modules."""
    if not ob:
        return "none"
    if CODE not in ob:
        return "docs"
    mods = ob & set(SLOW)
    return "fast" if not mods else "full" if len(mods) == len(SLOW) else f"fast+{len(mods)}"


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


ALL = frozenset({QUICK, CODE, *SLOW})


def decide(env, diff=changed, succeeded=previous_head_succeeded):
    """(obligations, reason) for the event described by `env` (the workflow's environment)."""
    event = env.get("EVENT", "")
    if event != "pull_request":
        if event == "schedule":
            # nightly net on main: only when something that is more than prose has landed since
            r = git("log", "--since=26 hours ago", "--name-only", "--pretty=format:", "HEAD")
            ob = obligations([p for p in r.stdout.split("\n") if p])
            return (ALL, "nightly: code landed on main") if CODE in ob else (frozenset(), "nightly: nothing but prose landed")
        return ALL, f"{event or 'manual'} run"
    base, head, before = env["BASE"], env["HEAD"], env.get("BEFORE", "")
    whole = diff(base, head, three_dots=True)
    if whole is None:
        return ALL, "the PR's diff cannot be read"
    pr = obligations(whole)
    if env.get("ACTION") == "synchronize" and before:
        push_files = diff(before, head)
        if push_files is not None:
            push = obligations(push_files)
            if push >= pr:
                return pr, "the push obliges all the PR does"
            if succeeded(env["REPO"], before):
                return push, f"push of tier {name_of(push)}; the previous head's checks passed (PR tier {name_of(pr)})"
            return pr, "the previous head's checks did not pass: the whole PR"
    return pr, f"the whole PR (event {env.get('ACTION', '')})"


def select_suite(modules=()):
    """The unit tests of `tests/`, as `python3 -m unittest discover -s tests` finds them, minus the
    SLOW modules not named in `modules`."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))

    def flatten(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                yield from flatten(t)
            else:
                yield t

    left_out = set(SLOW) - set(modules)
    keep = unittest.TestSuite()
    for t in flatten(suite):
        if type(t).__module__.rsplit(".", 1)[-1] in left_out:
            continue
        keep.addTest(t)
    return keep


def run_tests(modules):
    return 0 if unittest.TextTestRunner(verbosity=2).run(select_suite(modules)).wasSuccessful() else 1


def parser():
    """The command line's one definition: main() parses with it, and so does the heavy-job slot (heavy_slot.parsed)."""
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("decide")
    rt = sub.add_parser("run-tests")
    rt.add_argument("--modules", default="", help="comma-separated SLOW modules to run besides the others")
    return ap


def modules_of(a):
    return [m for m in a.modules.split(",") if m]


def refusal(a):
    """Why main() refuses a command line that parsed, or None. The one definition of every refusal after parsing: main()
    asks it, and so does the heavy-job slot, so a refused line is answered at once and never queues (#328)."""
    if a.cmd == "run-tests":
        unknown = set(modules_of(a)) - set(SLOW)
        if unknown:
            return f"not slow modules: {sorted(unknown)}"
    return None


def main(argv):
    a = parser().parse_args(argv)
    why = refusal(a)
    if why:
        print(why, file=sys.stderr)
        return 2
    if a.cmd == "run-tests":
        return run_tests(modules_of(a))
    env = {k: os.environ.get(k, "") for k in ("EVENT", "ACTION", "BASE", "HEAD", "BEFORE", "REPO")}
    ob, why = decide(env)
    print(f"tier={name_of(ob)} ({why})", file=sys.stderr)
    print(f"tier={name_of(ob)}")
    print(f"quick={'true' if QUICK in ob else 'false'}")
    print(f"code={'true' if CODE in ob else 'false'}")
    print("modules=" + ",".join(m for m in SLOW if m in ob))
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "runtime"))
    import heavy_slot
    _ns = heavy_slot.parsed(parser())
    # the unit suite is a heavy job (#318); `decide` is not, and a line main() refuses (parser or refusal()) holds no slot
    if _ns is not None and _ns.cmd == "run-tests" and refusal(_ns) is None:
        heavy_slot.take("unit-suite")
    sys.exit(main(sys.argv[1:]))
