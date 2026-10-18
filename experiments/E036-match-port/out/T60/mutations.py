#!/usr/bin/env python3
"""T60 (rule 9): a test proves behaviour only if it fails without it. Each operator and constant of the two ports'
code is changed once, in a copy of the ports and the two test files, and tests.test_port_runtime / test_port_geometry (the
hand-worked tests; the fuzz class is skipped, T60_NO_FUZZ=1) must fail on the copy. A mutant that passes is listed: it is
either equivalent (the same value by another route), or a branch only the families or the fuzz against the original
prove, and the list says which lines.

    python3 -B experiments/E036-match-port/out/T60/mutations.py [--module runtime|geometry] > mutations-<commit>.txt

Operators: < <-> <=, > <-> >=, == <-> !=, and <-> or, + <-> -, << <-> >>, an integer literal +1 (decimal or hex, not
inside a string, not a listing address). The worktree is never edited: the copies live under .cache/tmp."""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PORT = "runtime/original_match/port"
FILES = {"runtime": f"{PORT}/runtime.py", "geometry": f"{PORT}/geometry.py"}
TESTS = {"runtime": "tests/test_port_runtime.py", "geometry": "tests/test_port_geometry.py"}
SWAPS = [(" < ", " <= "), (" <= ", " < "), (" > ", " >= "), (" >= ", " > "), (" == ", " != "), (" != ", " == "),
         (" and ", " or "), (" or ", " and "), (" + ", " - "), (" - ", " + "), (" << ", " >> "), (" >> ", " << ")]
NUMBER = re.compile(r"(?<![\w\"':.])(0x[0-9A-Fa-f]+|\d+)(?![\w\"':.])")


def code_lines(text):
    """(line number, line) of the code lines: not blank, not a comment, not inside a docstring."""
    out, in_doc = [], False
    for i, line in enumerate(text.split("\n")):
        stripped = line.strip()
        quotes = stripped.count('"""')
        if in_doc:
            if quotes % 2 == 1:
                in_doc = False
            continue
        if quotes % 2 == 1:
            in_doc = True
            continue
        if not stripped or stripped.startswith("#") or stripped.startswith(("from ", "import ", "PORTS.variant")):
            continue
        if quotes == 2:
            continue
        out.append((i, line))
    return out


def mutants(text):
    for i, line in code_lines(text):
        code, _, comment = line.partition("  #")
        for old, new in SWAPS:
            pos = code.find(old)
            while pos >= 0:
                if code.count('"', 0, pos) % 2 == 0 and code.count("'", 0, pos) % 2 == 0:
                    yield i, code[:pos] + new + code[pos + len(old):] + (("  #" + comment) if comment else ""), f"{old.strip()} -> {new.strip()}"
                pos = code.find(old, pos + 1)
        for m in NUMBER.finditer(code):
            if code.count('"', 0, m.start()) % 2 == 0 and code.count("'", 0, m.start()) % 2 == 0:
                value = int(m.group(1), 0)
                text_new = hex(value + 1) if m.group(1).startswith("0x") else str(value + 1)
                yield i, code[:m.start()] + text_new + code[m.end():] + (("  #" + comment) if comment else ""), f"{m.group(1)} -> {text_new}"


def run_tests(tmp, test):
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", test.replace("/", ".")[:-3]], cwd=tmp, capture_output=True,
                       text=True, env={"PATH": "/usr/bin:/bin", "T60_NO_FUZZ": "1", "HOME": str(tmp)}, timeout=300)
    return p.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", choices=("runtime", "geometry"))
    a = ap.parse_args()
    modules = [a.module] if a.module else ["runtime", "geometry"]
    base = ROOT / ".cache" / "tmp"
    base.mkdir(parents=True, exist_ok=True)
    survivors = total = 0
    with tempfile.TemporaryDirectory(dir=base) as d:
        tmp = Path(d)
        shutil.copytree(ROOT / "runtime" / "original_match", tmp / "runtime" / "original_match",
                        ignore=shutil.ignore_patterns("__pycache__"))
        (tmp / "tests").mkdir()
        for t in TESTS.values():
            shutil.copy(ROOT / t, tmp / t)
        for module in modules:
            path = tmp / FILES[module]
            original = path.read_text()
            lines = original.split("\n")
            tests = [TESTS["runtime"], TESTS["geometry"]]
            assert all(run_tests(tmp, t) for t in tests), "the unmutated copy must pass"
            print(f"== {FILES[module]}: unmutated copy passes {', '.join(tests)}")
            try:
                for i, new_line, what in mutants(original):
                    total += 1
                    mutated = lines[:i] + [new_line] + lines[i + 1:]
                    path.write_text("\n".join(mutated))
                    caught = not all(run_tests(tmp, t) for t in tests)
                    if not caught:
                        survivors += 1
                        print(f"SURVIVED {FILES[module]}:{i + 1}: {what}: {lines[i].strip()[:110]}")
            finally:
                path.write_text(original)
    print(f"{total} mutants, {total - survivors} caught, {survivors} survived")
    return 0


if __name__ == "__main__":
    sys.exit(main())
