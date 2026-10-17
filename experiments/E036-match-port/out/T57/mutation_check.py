#!/usr/bin/env python3
"""T57: show that each fail-closed rule's test fails without the rule (CLAUDE.md rule 9).

    python3 -B experiments/E036-match-port/out/T57/mutation_check.py > experiments/E036-match-port/out/T57/mutation-tests-<stamp>.txt

Copies experiments/E036-match-port (without out/) to a temporary tree beside a link to runtime/, takes ONE rule out of
the copy at a time (a one-line replacement that must match exactly once), and runs tests.test_e036_compare and
tests.test_e036_family against the copy (E036_DIR). The unmutated copy must pass; each mutated copy must fail at least
one test, and the failing tests are listed. The working tree is never changed. No match is run (E036_NO_REAL_MATCH=1
makes the one real-kit test skip itself)."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / "experiments/E036-match-port"
MUTATIONS = [
    # compare.py
    ("compare.py", 'if missing_ref or missing or unexpected:', 'if missing_ref or unexpected:', "a match missing from the candidate"),
    ("compare.py", 'if missing_ref or missing or unexpected:', 'if missing_ref or missing:', "an unexpected match"),
    ("compare.py", 'if missing_ref or missing or unexpected:', 'if missing or unexpected:', "a match missing from the reference"),
    ("compare.py", 'if r["id"] in out:', 'if False:', "a duplicate match in a log"),
    ("compare.py", 'bad = completed(b)', 'bad = None', "an incomplete candidate match counts"),
    ("compare.py", '        if why:\n            raise Malformed(f"reference {mid} is not a completed match', '        if False:\n            raise Malformed(f"reference {mid} is not a completed match', "an incomplete reference match is accepted"),
    ("compare.py", 'ok = bool(bad or diff)', 'ok = True', "--expect differ passes an identical candidate"),
    ("compare.py", 'ok = bool(bad or diff)', 'ok = bool(diff)', "--expect differ does not count a match that did not complete"),
    ("compare.py", 'ok = not bad and not diff', 'ok = not bad', "--expect identical ignores differences"),
    ("compare.py", 'if r["spec_sha256"] != expected[mid]:', 'if False:', "a record of another declaration"),
    ("compare.py", 'if image_sha256 is not None and r["image_sha256"] != image_sha256:', 'if False:', "a record of another image"),
    ("compare.py", 'if ref[mid]["mask"] != cand[mid]["mask"]:', 'if False:', "two masks"),
    ("compare.py", 'if no_screen and field in SCREEN_FIELDS:', 'if no_screen:', "--no-screen leaves out more than the screen"),
    ("compare.py", 'if no_screen and field in SCREEN_FIELDS:', 'if False and field in SCREEN_FIELDS:', "--no-screen leaves out nothing"),
    ("compare.py", '"decisions", "after.seed", "after.ds",', '"decisions", "after.seed",', "the DS blocks are not compared"),
    ("compare.py", '            for name in records.RANGES:\n                if no_screen', '            for name in ():\n                if no_screen', "the ranges are not compared"),
    ("compare.py", 'if draws and diff[0][0] != "draws.per_minute":', 'if False:', "the first differing minute is not named"),
    ("compare.py", 'equal = got == want', 'equal = True', "the E032 seeds are not compared"),
    # records.py
    ("records.py", 'raise SchemaError(f"the JSON token {token} is not a finite number")', 'return 0.0', "NaN and Infinity tokens"),
    ("records.py", '        if k in seen:', '        if False:', "a duplicate key"),
    ("records.py", 'if text.startswith("\\ufeff"):', 'if False:', "a byte-order mark"),
    ("records.py", 'if text and not text.endswith("\\n"):', 'if False:', "an incomplete last line"),
    ("records.py", 'not pattern.fullmatch(v):', 'not pattern.match(v):', "a pattern matched against a prefix"),
    ("records.py", 'return isinstance(v, int) and not isinstance(v, bool)', 'return isinstance(v, int)', "a boolean for an integer"),
    ("records.py", 'if set(d) != set(want):', 'if not set(want) <= set(d):', "an unknown key"),
    ("records.py", '        _str(h, DIGEST, f"after.ds[{i}]")', '        pass', "the DS digests are not read"),
    ("records.py", '_list(a["ds"], "after.ds", DS_BLOCKS)', '_list(a["ds"], "after.ds")', "the number of DS digests"),
    ("records.py", '            _str(h, DIGEST, f"after.ranges.{name}[{i}]")', '            pass', "the range digests are not read"),
    ("records.py", 'if total != d["count"]:', 'if False:', "per-minute counts that do not add up"),
    ("records.py", 'raise SchemaError("evidence beside an error")', 'pass', "evidence beside an error"),
    ("records.py", 'raise SchemaError("a completed record without its evidence")', 'return', "a completed record without evidence"),
    ("records.py", 'ok = math.isfinite(v) and not (v == 0 and math.copysign(1, v) < 0)', 'ok = True', "a non-finite float or -0.0"),
    ("records.py", '    for i, x in enumerate(v):\n        _int(x, lo, hi, f"{path}[{i}]")', '    for i, x in enumerate(v[:1]):\n        _int(x, lo, hi, f"{path}[{i}]")', "the second element of a pair"),
    ("records.py", '_str(r["error"], ERROR_TEXT, "error")', 'pass', "an error text with a newline"),
    ("records.py", 'if s[0] in prev and s[1] < prev[s[0]]:', 'if False:', "an unsorted or overlapping mask"),
    ("records.py", 'if int(k) >= N_TEMPLATES:', 'if False:', "a template id past the game's 67"),
    ("records.py", '        raise SchemaError(f"id {r[\'id\']!r} is not in family {r[\'family\']!r}")', '        pass', "an id outside its family"),
    # families.py
    ("families.py", '"policy_code_sha256": self.policy_cls.code_sha256()', '"policy_code_sha256": ""', "the policy's code is not in the digest"),
    ("families.py", '            check_edit(e, f"{where} edits[{i}]")', '            pass', "an edit is not checked"),
    ("families.py", 'and 1 <= fixture[2] <= 0xFFFF and fixture[3] in KINDS):', 'and 1 <= fixture[2] <= 0xFFFF):', "a fixture kind the builders do not write"),
    ("families.py", 'if m.id in seen:', 'if False:', "an id twice in a family"),
    ("families.py", 'if clash:', 'if False:', "an id in two families"),
    # family.py
    ("family.py", 'strays.append(context)', 'pass', "a stray decision"),
    ("family.py", 'seen[address] += 1', 'seen[address] += 2', "each execution of a --count address is counted once"),
    ("family.py", '    except Exception as e:      # the record says what failed', '    except KeyboardInterrupt as e:      # the record says what failed', "an error is a record"),
    ("family.py", 'first = (str(e).splitlines() or [""])[0]', 'first = str(e)', "the error text keeps the screen"),
    ("family.py", 'ds = records.apply_mask(machine.read(machine.DS * 16, records.DS_SIZE), "DS", 0, mask)', 'ds = machine.read(machine.DS * 16, records.DS_SIZE)', "the mask"),
    ("family.py", 'todo = [s for s in selected if s.id not in done]', 'todo = list(selected)', "a match already in the log is not run again"),
    ("family.py", 'if r["spec_sha256"] != expected[r["id"]].sha256 or', 'if False or', "a log of another declaration is refused"),
    ("family.py", 'if r["mask"] != [list(s) for s in mask]:', 'if False:', "a log of another mask is refused"),
    ("family.py", 'if ev.kind == "minute" and ev.minute in policy.pause_at and ev.minute not in paused:', 'if ev.kind == "minute" and ev.minute in policy.pause_at:', "a pause is made once"),
    ("family.py", 'if time.time() > deadline:', 'if False:', "the time limit"),
    ("family.py", 'os.O_WRONLY | os.O_APPEND | os.O_CREAT', 'os.O_WRONLY | os.O_TRUNC | os.O_CREAT', "a log is appended to, never rewritten"),
    ("family.py", 'todo = todo[:max_new]', 'pass', "--max"),
    ("family.py", 'return 1 if bad else 0', 'return 0', "the exit status of a match that did not complete"),
    ("family.py", 'if a.find_ranges and Path(a.find_ranges).exists():', 'if False:', "an output is never overwritten"),
]
TESTS = ["tests.test_e036_compare", "tests.test_e036_family"]


def run(tree):
    env = dict(os.environ, E036_DIR=str(tree / "experiments/E036-match-port"), E036_NO_REAL_MATCH="1")
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", *TESTS], cwd=ROOT, env=env, capture_output=True, text=True, timeout=900)
    out = p.stderr
    failing = sorted(set(re.findall(r"^(?:FAIL|ERROR): (\S+) \(([^)]*)\)", out, re.M)))
    ran = re.search(r"Ran (\d+) tests", out)
    return p.returncode, [f"{c.split('.')[-1]}.{t}" for t, c in failing], ran.group(1) if ran else "?"


def main():
    only = sys.argv[1:]
    with tempfile.TemporaryDirectory() as tmp:
        tree = Path(tmp)
        (tree / "experiments").mkdir()
        shutil.copytree(SRC, tree / "experiments/E036-match-port", ignore=shutil.ignore_patterns("out", "__pycache__"))
        (tree / "experiments/E036-match-port/out/T57").mkdir(parents=True)
        os.symlink(ROOT / "runtime", tree / "runtime")
        code, failing, ran = run(tree)
        print(f"unmutated copy: exit {code}, {ran} tests, failing: {failing}")
        bad = code != 0
        for n, (name, old, new, what) in enumerate(m for m in MUTATIONS if m[3] is not None):
            if only and str(n) not in only:
                continue
            path = tree / "experiments/E036-match-port" / name
            text = path.read_text()
            if text.count(old) != 1:
                print(f"[{n:2d}] {name}: {what}: the replaced text appears {text.count(old)} times, not once: FIX THE MUTATION")
                bad = True
                continue
            path.write_text(text.replace(old, new))
            try:
                code, failing, ran = run(tree)
            finally:
                path.write_text(text)
            caught = code != 0 and failing
            bad = bad or not caught
            print(f"[{n:2d}] {name}: without '{what}': exit {code}, {len(failing)} failing" + (" -> " + "; ".join(failing[:4]) + (f" (+{len(failing) - 4})" if len(failing) > 4 else "") if failing else " -> NOT CAUGHT"))
            sys.stdout.flush()
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
