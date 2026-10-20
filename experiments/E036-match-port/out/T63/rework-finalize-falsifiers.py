"""Officially compare all three fresh T63 reached-branch F40 falsifiers."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "experiments/E036-match-port/out/T63"
VARIANTS = ("depth-plus-one", "marking-no-copy", "keeper-no-state")
MANIFEST = OUT / "falsifiers-rework-cbbfb28.sha256"


def main():
    assert not MANIFEST.exists()
    files = []
    for variant in VARIANTS:
        candidate = OUT / f"falsifier-rework-cbbfb28-{variant}-F40.jsonl"
        comparison = OUT / f"falsifier-rework-cbbfb28-{variant}-F40-compare.txt"
        records = [json.loads(line) for line in candidate.read_text().splitlines()]
        assert len(records) == 40 and len({record["id"] for record in records}) == 40, variant
        assert all(record["family"] == "F40" and record["ports"] == ["positioning"]
                   and record["variant"] == f"positioning.{variant}" and record["error"] is None
                   for record in records), variant
        result = subprocess.run([sys.executable, "-B", "experiments/E036-match-port/compare.py",
                                 "--family", "F40", "--candidate", str(candidate.relative_to(ROOT)),
                                 "--expect", "differ"], cwd=ROOT, capture_output=True, text=True)
        output = result.stdout + result.stderr
        assert result.returncode == 0, output
        if comparison.exists():
            assert comparison.read_text() == output, comparison
        else:
            comparison.write_text(output)
        files.extend((candidate, comparison))
        print(variant, comparison.read_text().splitlines()[-1])
    MANIFEST.write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT)}\n"
                                for path in files))


if __name__ == "__main__":
    main()
