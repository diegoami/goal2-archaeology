"""Combine and compare the immutable fresh T63 positioning-only ALL halves."""
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "experiments/E036-match-port/out/T63"
ADDRESSES = ("1F3C", "1FDD", "20E3", "2218", "419C", "42CB", "4354", "4438", "44C1", "4532",
             "4649", "474D", "47C5", "4A28", "4B64", "4D3F")
LABELS = tuple(f"0791:{offset}" for offset in ADDRESSES)
HALVES = tuple(OUT / f"own-rework-cbbfb28-r2-{half}.jsonl" for half in "ab")
COMBINED = OUT / "own-rework-cbbfb28.jsonl"
COMPARE = OUT / "own-rework-cbbfb28-compare.txt"
MATRIX = OUT / "own-rework-cbbfb28-calls-per-match.tsv"
MANIFEST = OUT / "own-rework-cbbfb28.sha256"


def main():
    assert not any(path.exists() for path in (COMBINED, COMPARE, MATRIX, MANIFEST))
    chunks = [path.read_bytes() for path in HALVES]
    records = [[json.loads(line) for line in chunk.splitlines()] for chunk in chunks]
    assert all(len(half) == 31 for half in records), [len(half) for half in records]
    records = records[0] + records[1]
    assert len({record["id"] for record in records}) == 62
    assert all(record["family"] in ("F40", "O8", "S") and record["ports"] == ["positioning"]
               and record["error"] is None for record in records)
    assert all(record["counts"][label] == record["port_calls"][label]
               for record in records for label in LABELS)
    COMBINED.write_bytes(b"".join(chunks))
    result = subprocess.run([sys.executable, "-B", "experiments/E036-match-port/compare.py",
                             "--family", "ALL", "--candidate", str(COMBINED.relative_to(ROOT))],
                            cwd=ROOT, capture_output=True, text=True)
    COMPARE.write_text(result.stdout + result.stderr)
    assert result.returncode == 0, COMPARE.read_text()
    with MATRIX.open("w", newline="") as stream:
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(("match", *LABELS))
        for record in records:
            writer.writerow((record["id"], *(record["port_calls"][label] for label in LABELS)))
    files = (*HALVES, COMBINED, COMPARE, MATRIX)
    MANIFEST.write_text("".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(ROOT)}\n"
                                for path in files))
    reach = {label: sum(record["port_calls"][label] > 0 for record in records) for label in LABELS}
    print(json.dumps({"records": len(records), "source_ports": "positioning", "compare": COMPARE.read_text().strip(),
                      "reached_matches": reach}, indent=2))


if __name__ == "__main__":
    main()
