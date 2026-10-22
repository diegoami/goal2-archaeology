"""Compare every T63 guest Call argument count with its callee's listing return."""
import ast
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PORT = ROOT / "runtime/original_match/port/positioning.py"
CODE = ROOT / "static/goal-exe/code"


def returns(target):
    segment, offset = target.split(":")
    anchor = f"sub_{offset}:"
    for path in sorted(CODE.glob(f"seg_{segment}_*.asm")):
        source = path.read_text()
        start = source.find("\n" + anchor + "\n")
        if start < 0:
            continue
        end = source.find("\n; ---- routine ", start + len(anchor))
        body = source[start:end if end >= 0 else None]
        found = set()
        for line in body.splitlines():
            match = re.search(r"\s{2,}(retf?|ret)(?:\s+(0x[0-9A-Fa-f]+|\d+))?\s*$", line)
            if match:
                found.add((match.group(1), int(match.group(2) or "0", 0)))
        if found:
            return sorted(found)
        raise AssertionError(f"{target}: no return in {path}")
    raise AssertionError(f"{target}: no listing entry")


def main():
    tree = ast.parse(PORT.read_text())
    calls = []
    for fn in tree.body:
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) or not fn.decorator_list:
            continue
        if not any(isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "port"
                   for d in fn.decorator_list):
            continue
        for call in ast.walk(fn):
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                continue
            kind = call.func.id
            if kind not in ("near", "same", "far"):
                continue
            target = ast.literal_eval(call.args[1])
            target = f"0791:{target}" if kind != "far" else target
            expected = ("ret" if kind == "near" else "retf", 2 * (len(call.args) - 2))
            actual = returns(target)
            calls.append({"function": fn.name, "line": call.lineno, "target": target,
                          "expected": expected, "listing_returns": actual,
                          "matches": expected in actual and len(actual) == 1})
    mismatches = [call for call in calls if not call["matches"]]
    print(json.dumps({"source": str(PORT.relative_to(ROOT)), "calls": len(calls),
                      "mismatches": mismatches}, indent=2))
    assert len(calls) == 95 and not mismatches, mismatches


if __name__ == "__main__":
    main()
