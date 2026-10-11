"""Done-when 2: change every numeric constant of the condition model by +1 and by -1, in place, and
require tests.test_model_condition to fail each time.

    python3 experiments/E020-q018-condition-performance/mutate_condition.py mutations-001.log

Targets, each integer literal (bools excluded) in:
  runtime/model/condition.py          every module-level constant (tuples and dicts included) and every
                                      literal inside a function body
  runtime/model/quick_engine.py       the bodies of player_strength (1771:377E), unavailable (3216)
                                      and wrong_foot (3179): the quick-engine code condition.strength
                                      calls, which is not copied
Each mutant is a separate subprocess importing the real module (no copy, no monkeypatch); the
source is restored from its saved contents in `finally` (never git checkout); bytecode is cleared
before each run; the log is exclusive-create. Survivors are listed, not hidden: the exit status is
non-zero unless every mutant is killed."""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMMAND = [sys.executable, "-m", "unittest", "tests.test_model_condition"]
TARGETS = [(ROOT / "runtime/model/condition.py", None),
           (ROOT / "runtime/model/quick_engine.py", {"player_strength", "unavailable", "wrong_foot"})]


def literals(path, functions):
    tree = ast.parse(path.read_text())
    found = []
    if functions is None:
        nodes = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
    else:
        nodes = [f for c in ast.walk(tree) if isinstance(c, ast.ClassDef) for f in c.body
                 if isinstance(f, ast.FunctionDef) and f.name in functions]
    for top in nodes:
        for n in ast.walk(top):
            if isinstance(n, ast.Constant) and type(n.value) is int and n.lineno == n.end_lineno:
                found.append((n.lineno, n.col_offset, n.end_col_offset, n.value))
    return sorted(set(found))


def clear_bytecode():
    for path in (ROOT / "runtime/model/__pycache__").glob("*.pyc"):
        path.unlink()


def main():
    destination = ROOT / "experiments/E020-q018-condition-performance" / sys.argv[1]
    killed = total = 0
    survivors = []
    with destination.open("x") as log:
        log.write("In-place +1 and -1 sweep of every integer literal of the condition model\n")
        log.write("Command: python3 -m unittest tests.test_model_condition   (timeout 60 s per mutant)\n")
        baseline = subprocess.run(COMMAND, cwd=ROOT, capture_output=True, text=True, timeout=60)
        log.write(f"BASELINE exit={baseline.returncode}\n")
        if baseline.returncode:
            log.write(baseline.stderr)
            return 1
        for path, functions in TARGETS:
            original = path.read_text()
            lines = original.splitlines(keepends=True)
            try:
                for lineno, col, end, value in literals(path, functions):
                    text = lines[lineno - 1][col:end]
                    for delta in (+1, -1):
                        new = value + delta
                        shown = hex(new) if text.lower().startswith("0x") else str(new)
                        changed = lines.copy()
                        changed[lineno - 1] = lines[lineno - 1][:col] + shown + lines[lineno - 1][end:]
                        label = f"{path.name}:{lineno}:{col} {text} -> {shown}"
                        path.write_text("".join(changed))
                        clear_bytecode()
                        total += 1
                        try:
                            result = subprocess.run(COMMAND, cwd=ROOT, capture_output=True, text=True, timeout=60)
                            status = "KILLED" if result.returncode else "SURVIVED"
                        except subprocess.TimeoutExpired:
                            status = "TIMEOUT"       # not counted as a kill
                        if status == "KILLED":
                            killed += 1
                        else:
                            survivors.append(label)
                        log.write(f"{label}: {status}\n")
                        log.flush()
            finally:
                path.write_text(original)
                clear_bytecode()
        log.write(f"killed: {killed}/{total}\n")
        for label in survivors:
            log.write(f"SURVIVOR {label}\n")
    print(f"killed: {killed}/{total}; log: {sys.argv[1]}")
    return int(killed != total)


if __name__ == "__main__":
    raise SystemExit(main())
