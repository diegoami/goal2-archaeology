#!/usr/bin/env python3
"""Check the guide's claims against the session logs, and the guide against its claims; write
out/claims.md. Fails closed: an empty table, an empty or missing log, a needle not where the row says,
a file whose content does not match, a guide sentence with no backing, a row no sentence cites, or a
tag with no row: exit 1. No game is run.

claims.tsv: id, claim, kind, session, step, needle.
- `screen`: the needle is in the logged screen after the step (the first such step when the step is
  empty); `notscreen`: the needle is NOT in the logged screen after that step (the step is required);
- `log`: the needle is in the step's own log line (the request, its result, an error);
- `anyscreen`: the needle is in a logged screen that has no step of its own (a card `scan` read);
- `file`: `path :: regex :: =N` or `path :: regex :: >=N`: the tracked file (relative to the experiment) has
  exactly N (at least N) lines matching the regex: the content a claim asserts, not the file's mere
  existence.

The guide check (docs/play-guide.md, sections 2 to 9): every sentence of a paragraph or list item,
and every table row, carries a tag `[Cnn]` or a label (*F030* and the other findings *F0nn*,
*listing*, *manual*, *owner*, *not seen*, *tool*, *assumed*); every tag names a row; every row is cited.

Usage: python3 experiments/E031-play-the-game/claims.py [--base DIR] [--guide FILE] [--md FILE]"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TAG = re.compile(r"\[(C\d+[a-z]?(?:, C\d+[a-z]?)*)\]")
LABEL = re.compile(r"\*(F0\d\d|listing|manual|owner|not seen|tool|assumed)\*")


class Evidence:
    def __init__(self, base):
        self.base = Path(base)
        self.cache = {}

    def session(self, name):
        if name not in self.cache:
            d = self.base / "out" / name
            screens = {}
            for line in (d / "screens.jsonl").read_text().splitlines():
                s = json.loads(line)
                screens[s["digest"]] = s["text"]
            steps = [(json.loads(line), line) for line in (d / "steps.jsonl").read_text().splitlines()]
            if not steps or not screens:
                raise ValueError(f"session {name}: empty log")
            self.cache[name] = (steps, screens)
        return self.cache[name]

    def resolve(self, row):
        """(where, the matching line) or (None, why)."""
        kind, needle = row["kind"], row["needle"]
        if kind == "file":
            path, regex, want = needle.split(" :: ")
            p = self.base / path
            if not p.is_file():
                return None, f"{path} missing"
            n = sum(1 for line in p.read_text().splitlines() if re.search(regex, line))
            ok = n == int(want[1:]) if want.startswith("=") else n >= int(want[2:])
            return (f"{path}: {n} lines match", "") if ok else (None, f"{path}: {n} lines match {regex!r}, want {want}")
        steps, screens = self.session(row["session"])
        if kind == "anyscreen":
            for digest, text in screens.items():
                if needle in text:
                    line = next(r for r in text.split("\n") if needle in r)
                    return f"{row['session']} screens.jsonl, digest {digest[:12]}", line.strip()
            return None, "no screen holds it"
        want = int(row["step"]) if row["step"] else None
        if kind == "notscreen" and want is None:
            return None, "notscreen needs a step"
        for st, raw in steps:
            if want is not None and st["n"] != want:
                continue
            hay = raw if kind == "log" else screens.get(st.get("digest"), "")
            where = f"{row['session']} step {st['n']} ({st['utc'][11:19]} UTC)"
            if kind == "notscreen":
                return (where + ": absent", "") if hay and needle not in hay else (None, "present (or no screen)")
            if needle in hay:
                line = next((r for r in hay.split("\n") if needle in r), "") if kind == "screen" else ""
                return where, line.strip()
        return None, "not at that step" if want is not None else "in no step"


def units(guide_text):
    """(line number, text) for every sentence of a paragraph or list item, and every table row, in
    sections 2 to 9 of the guide."""
    out, block, start, in_code, on = [], [], 0, False, False

    def flush():
        if block:
            text = " ".join(block)
            for s in re.split(r"(?<=[.!])\s+(?=[A-Z`*\"(])", text):  # not at "?": quoted questions
                if s.strip():
                    out.append((start, s.strip()))
        block.clear()

    for i, line in enumerate(guide_text.splitlines(), 1):
        if line.startswith("## "):
            flush()
            on = not line.startswith("## 1.")
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not on or in_code:
            continue
        s = line.strip()
        if not s or s.startswith("#"):
            flush()
            continue
        if s.startswith("|"):
            flush()
            if not re.fullmatch(r"\|[\s\-|]+\|", s) and not s.startswith("| looks stuck") \
                    and not s.startswith("| what |") and not s.startswith("| screen |") \
                    and not s.startswith("| option |") and not s.startswith("| year |"):
                out.append((i, s))
            continue
        if s.startswith("- "):
            flush()
            start = i
            block.append(s[2:])
            continue
        if not block:
            start = i
        block.append(s)
    flush()
    return out


def check_guide(guide_text, ids):
    problems, cited = [], set()
    for i, text in units(guide_text):
        tags = set()
        for group in TAG.findall(text):
            tags.update(t.strip() for t in group.split(","))
        cited |= tags
        if not tags and not LABEL.search(text):
            problems.append(f"guide line {i}: no tag or label: {text[:100]!r}")
    for t in sorted(cited - ids):
        problems.append(f"the guide cites {t}, which claims.tsv does not have")
    for t in sorted(ids - cited):
        problems.append(f"claims.tsv row {t} is cited by no guide sentence")
    return problems, cited


def run(base, guide, md):
    base = Path(base)
    rows = list(csv.DictReader((base / "claims.tsv").open(), delimiter="\t", quoting=csv.QUOTE_NONE))
    problems = []
    if not rows:
        problems.append("claims.tsv has no rows")
    ev = Evidence(base)
    table = ["# The guide's observed claims and the logged steps that show them", "",
             "Generated by `claims.py` from `claims.tsv` and the session logs; `screen.py <session> <step>` "
             "prints the whole screen. A statement the guide labels *F030*, *listing*, *manual*, *owner*, "
             "*not seen*, *tool* or *assumed* is not in this table.", "",
             "| id | claim | evidence | the row that holds it |", "| --- | --- | --- | --- |"]
    found = 0
    for r in rows:
        try:
            where, line = ev.resolve(r)
        except (OSError, ValueError, KeyError) as e:
            where, line = None, f"{type(e).__name__}: {e}"
        if where is None:
            problems.append(f"NOT FOUND {r['id']}: {r['needle']!r} in {r['session']} {r['step']}: {line}")
            where, line = "**not found**", ""
        else:
            found += 1
        cell = line.replace("|", "│")[:90]
        table.append(f"| {r['id']} | {r['claim']} | {where} | `{cell}` |" if cell else f"| {r['id']} | {r['claim']} | {where} | |")
    gp, cited = check_guide(Path(guide).read_text(), {r["id"] for r in rows})
    problems += gp
    if md:
        Path(md).write_text("\n".join(table) + "\n")
    return rows, found, cited, problems


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=str(HERE))
    ap.add_argument("--guide", default=str(HERE.parents[1] / "docs" / "play-guide.md"))
    ap.add_argument("--md", default=None, help="default: <base>/out/claims.md")
    a = ap.parse_args(argv)
    rows, found, cited, problems = run(a.base, a.guide, a.md or str(Path(a.base) / "out" / "claims.md"))
    for p in problems:
        print(p)
    print(f"{found} of {len(rows)} claims found where claims.tsv says; the guide cites {len(cited)} of them; "
          f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
