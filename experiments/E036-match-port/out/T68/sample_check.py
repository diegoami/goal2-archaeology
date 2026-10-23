"""T68 development check (copied from out/T67): compare.check on a subset of ALL (the matches a sample log holds) against the T57 reference.
Diagnostic only; the acceptance is compare.py on the whole family."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HERE))
import compare  # noqa: E402

cand = compare.load(sys.argv[1])
ref = compare.load(str(HERE / "out/T57/reference.jsonl"))
expect = sys.argv[2] if len(sys.argv) > 2 else "identical"
expected = {mid: ref[mid]["spec_sha256"] for mid in cand}
lines, ok = compare.check(ref, cand, expected, expect)
print("\n".join(lines))
sys.exit(0 if ok else 1)
