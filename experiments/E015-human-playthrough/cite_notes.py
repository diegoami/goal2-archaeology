#!/usr/bin/env python3
"""Write and check note citations from the run records, so numbers cannot drift by hand.

A record's own note numbering is the `notes.jsonl line N` of its `note (...)` observations (1-based);
the time is that note's UTC time.

  cite_notes.py --table RUN...            print every note of the runs (number, UTC time, text start)
  cite_notes.py --resolve FILE...         replace each {{rNNNN:kw}} in place by "rNNNN note N, HH:MM:SS UTC"
                                          kw = a substring found in exactly one note of that run;
                                          {{rNNNN:a .. b}} -> "rNNNN notes N–M"; {{rNNNN:a ; b}} -> "rNNNN notes N, M"
  cite_notes.py --check FILE...           verify every "rNNNN note(s) N[, HH:MM:SS UTC]" written in the files
                                          against the records; exit 1 on a mismatch

Reads only runs/E015/*.json (never writes there).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTE = re.compile(r"note \(notes\.jsonl line (\d+), UTC [^T]+T(\d\d:\d\d:\d\d)")
_cache: dict = {}


def notes(run: str) -> list[tuple[int, str, str]]:
    if run not in _cache:
        record = json.loads((ROOT / "runs" / "E015" / f"E015-{run}.json").read_text(encoding="utf-8"))
        found = []
        for obs in record["observations"]:
            match = NOTE.match(obs["field"])
            if match:
                found.append((int(match.group(1)), match.group(2), obs["value"]))
        _cache[run] = sorted(found)
    return _cache[run]


def find(run: str, keyword: str) -> tuple[int, str, str]:
    hits = [n for n in notes(run) if keyword.strip() in n[2]]
    if len(hits) != 1:
        raise SystemExit(f"{run}: {keyword!r} matches {len(hits)} notes, need exactly 1")
    return hits[0]


PLACEHOLDER = re.compile(r"\{\{(r\d{4}):([^}]*)\}\}")


def resolve_one(match: re.Match, log: list[str]) -> str:
    run, spec = match.group(1), match.group(2)
    if " .. " in spec:
        a, b = (find(run, k) for k in spec.split(" .. "))
        out = f"{run} notes {a[0]}–{b[0]}"
    elif " ; " in spec:
        picked = [find(run, k) for k in spec.split(" ; ")]
        out = f"{run} notes " + ", ".join(str(n[0]) for n in picked)
    else:
        n = find(run, spec)
        out = f"{run} note {n[0]}, {n[1]} UTC"
    log.append(f"{out}\t<- {spec}")
    return out


CITATION = re.compile(r"\b(r\d{4}) notes? (\d+(?:(?:–|, )\d+(?![\d:]))*)(?:, (\d\d:\d\d:\d\d) UTC)?")


def check(path: Path) -> list[str]:
    problems = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for m in CITATION.finditer(line):
            run = m.group(1)
            numbers = [int(x) for x in re.findall(r"\d+", m.group(2))]
            known = {n[0]: n[1] for n in notes(run)}
            for number in numbers:
                if number not in known:
                    problems.append(f"{path}:{lineno}: {run} has no note {number}")
            if m.group(3) and known.get(numbers[0]) != m.group(3):
                problems.append(f"{path}:{lineno}: {run} note {numbers[0]} is at {known.get(numbers[0])}, not {m.group(3)}")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    mode, rest = argv[1], argv[2:]
    if mode == "--table":
        for run in rest:
            for number, time, text in notes(run):
                print(f"{run} note {number}\t{time} UTC\t{text[:90]}")
        return 0
    if mode == "--resolve":
        for name in rest:
            path = Path(name)
            log: list[str] = []
            text = PLACEHOLDER.sub(lambda m: resolve_one(m, log), path.read_text(encoding="utf-8"))
            path.write_text(text, encoding="utf-8")
            print(f"== {name}: {len(log)} citations written")
            print("\n".join(log))
        return 0
    if mode == "--check":
        problems = [p for name in rest for p in check(Path(name))]
        print("\n".join(problems) if problems else "citations ok")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
