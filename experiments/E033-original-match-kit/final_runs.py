#!/usr/bin/env python3
"""E033: the final round of runs for a commit, one after another (the machine has one shared CPU), each output a
new file under out/ stamped <stamp>; a summary of every step's exit code at the end.

    python3 -B experiments/E033-original-match-kit/final_runs.py <stamp> <old commit> <goal2 copy>

<old commit>: the reviewed commit the new tests and checks are shown failing on. <goal2 copy>: a throwaway goal2
checkout with E006-r0001 in .cache, into which the kit is vendored as goal2/engine/original_match."""
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
E = ROOT / "experiments" / "E033-original-match-kit"
OUT = E / "out"
PY = [sys.executable, "-B"]


def step(name, args, out, cwd=ROOT, env=None):
    path = OUT / out
    if path.exists():
        sys.exit(f"refused: {path} exists")
    t = time.time()
    with open(path, "x") as f:
        r = subprocess.run(args, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=env)
    line = f"{name:44s} exit {r.returncode}  {time.time() - t:6.1f} s  -> out/{out}"
    print(line, flush=True)
    return line


def main():
    stamp, old, goal2 = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    s = f"20261016{stamp}"
    lines = []
    env = {"PATH": "/usr/local/bin:/usr/bin:/bin", "PYTHONPATH": str(ROOT / "runtime")}
    lines.append(step("tests", PY + ["-m", "unittest", "tests.test_original_match", "-v"], f"tests-{s}.txt"))
    lines.append(step("check --family", PY + ["-m", "original_match.check", "--cache", ".cache/dl", "--family",
                                             "--json", str(OUT / f"check-{s}.json")], f"check-{s}.txt", env=env))
    lines.append(step("paths", PY + [str(E / "paths.py"), "--log", str(OUT / f"paths-{s}.jsonl")], f"paths-{s}.txt"))
    lines.append(step("stamps (14 matches)", PY + [str(E / "stamps.py"), "--log", str(OUT / f"stamps-{s}.jsonl")],
                      f"stamps-{s}.txt"))
    lines.append(step("save boundaries (7 scenarios)", PY + [str(E / "save_boundaries.py"), "--log",
                                                            str(OUT / f"save-boundaries-{s}.jsonl")],
                      f"save-boundaries-{s}.txt"))
    lines.append(step("example", PY + ["-m", "original_match.example", "--cache", ".cache/dl"], f"example-{s}.txt",
                      env=env))
    old_dir = Path(f"/tmp/e033-kit-{old}-{s}")
    lines.append(step(f"new tests on {old}", PY + [str(E / "old_kit.py"), old, str(old_dir),
                      "OriginalTests.test_guard_covers_code_beyond_prefixes", "OriginalTests.test_guard_covers_data_tables",
                      "OriginalTests.test_guard_covers_relocated_words", "OriginalTests.test_guard_leaves_goal2_state_alone",
                      "OriginalTests.test_save_at_full_time_and_at_a_decision",
                      "OriginalTests.test_events_are_stamped_at_the_originals_writes", "ImageTests.test_build_guard_data"],
                      f"old-kit-tests-{s}.txt"))
    lines.append(step(f"stamps on {old} (quick)", PY + [str(E / "stamps.py"), "--quick", "--kit", str(old_dir), "--log",
                                                      str(OUT / f"stamps-at-{old}-{s}.jsonl")], f"stamps-at-{old}-{s}.txt"))
    lines.append(step(f"save boundaries on {old} (1 scenario)", PY + [str(E / "save_boundaries.py"), "--scenarios", "1",
                      "--kit", str(old_dir), "--log", str(OUT / f"save-boundaries-at-{old}-{s}.jsonl")],
                      f"save-boundaries-at-{old}-{s}.txt"))
    lines.append(step("mutations", PY + [str(ROOT / "tests" / "mutations_original_match.py")], f"mutations-{s}.txt"))
    target = goal2 / "goal2" / "engine" / "original_match"
    for f in (ROOT / "runtime" / "original_match").iterdir():
        if f.is_file() and f.suffix in (".py", ".md"):
            shutil.copyfile(f, target / f.name)
    lines.append(step("goal2 trial (vendored copy)", PY + ["trial_watch.py"], f"goal2-trial-{s}.txt", cwd=goal2))
    lines.append(step("check from goal2's tree", PY + ["-m", "goal2.engine.original_match.check", "--cache", ".cache"],
                      f"goal2-check-{s}.txt", cwd=goal2))
    lines.append(step("hashes", PY + [str(E / "hashes.py"), str(OUT / f"sha256-{s}.tsv")], f"hashes-{s}.txt"))
    (OUT / f"final-runs-{s}.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
