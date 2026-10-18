"""Final frame-code sample: preserve generation and apply compare.check to exactly three declared cases."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments/E036-match-port"))
import compare
import families


def main():
    out = ROOT / "experiments/E036-match-port/out/T69"
    ids = ("S/quick-1", "S/quick-30", "F40/e032-0101")
    candidate = out / "final-sample-f69ce1c.jsonl"
    args = [sys.executable, "-B", "experiments/E036-match-port/family.py", "--family", "ALL", "--ports", "frame",
            "--only", ",".join(ids), "--out", str(candidate)]
    with (out / "run-final-sample-f69ce1c.txt").open("x") as log:
        print("COMMAND:", " ".join(args), file=log, flush=True)
        code = subprocess.run(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT).returncode
        print("GENERATOR EXIT:", code, file=log)
    if code:
        return code
    expected = {mid: digest for fam in families.discover().values() for mid, digest in fam.expected().items()
                if mid in ids}
    if set(expected) != set(ids):
        raise ValueError("sample does not name exactly three declared matches")
    ref = compare.load(ROOT / "experiments/E036-match-port/out/T57/reference.jsonl")
    cand = compare.load(candidate)
    lines, ok = compare.check(ref, cand, expected, image_sha256=families.image_sha256())
    with (out / "compare-final-sample-f69ce1c.txt").open("x") as log:
        log.write("\n".join(lines) + "\nexit " + str(0 if ok else 1) + "\n")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
