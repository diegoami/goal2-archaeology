#!/usr/bin/env python3
"""Check sources/goal-hlp.md against the released GOAL.HLP, and knowledge-map.md against the passages.

Usage: python3 sources/check_quotes.py <path to GOAL.HLP>

1. Every quotation (a `#### Pnn` heading, a `Lines a–b` line, a ```text block) must equal the file's
   lines a..b exactly, CR dropped: same number of lines, same text, no paraphrase and no stretch.
   The sha256 the page declares must equal the file's.
2. Every knowledge-map row whose status is `documented` must link to at least one passage that exists
   (`sources/goal-hlp.md#pnn`); every row left `unknown` must give a reason after the status; no row
   may have any other status (nothing above `documented` belongs to this map's G4 state).
Exit 0 when both print 0 problems, 1 otherwise. The original file is read, never copied.
"""
import hashlib
import re
import sys
from pathlib import Path

HEAD = re.compile(r"^#### (P\d+)\s*$")
LINES = re.compile(r"^Lines (\d+)(?:–(\d+))?(?: · .*)?$")
SHA = re.compile(r"sha256 `([0-9a-f]{64})`")
LINK = re.compile(r"\]\(sources/goal-hlp\.md#(p\d+)\)")


def hlp_lines(data):
    """The file's lines, CR dropped. The file ends with CR LF and a DOS end-of-file byte (0x1A), which
    is not a line."""
    text = data.decode("latin-1").replace("\r", "")
    parts = text.split("\n")
    if parts and parts[-1] in ("", "\x1a"):
        parts.pop()
    return parts


def parse_passages(md):
    """Return (passages, problems). A passage is (id, start, end, quoted lines, md line number)."""
    src = md.split("\n")
    passages, problems = [], []
    i = 0
    while i < len(src):
        m = HEAD.match(src[i])
        if not m:
            i += 1
            continue
        pid, at = m.group(1), i + 1
        i += 1
        lm = LINES.match(src[i]) if i < len(src) else None
        if not lm:
            problems.append(f"{pid} (line {at}): no 'Lines a–b' line after the heading")
            continue
        start = int(lm.group(1))
        end = int(lm.group(2) or lm.group(1))
        i += 1
        while i < len(src) and not src[i].strip():
            i += 1
        if i >= len(src) or src[i] != "```text":
            problems.append(f"{pid} (line {at}): no ```text block after the Lines line")
            continue
        i += 1
        body = []
        while i < len(src) and src[i] != "```":
            body.append(src[i])
            i += 1
        if i >= len(src):
            problems.append(f"{pid} (line {at}): the ```text block is never closed")
            continue
        i += 1
        passages.append((pid, start, end, body, at))
    return passages, problems


def check_quotes(md, data):
    """Return (number of quotations, list of mismatches)."""
    lines = hlp_lines(data)
    passages, problems = parse_passages(md)
    declared = SHA.search(md)
    if not declared:
        problems.append("no sha256 declared")
    elif declared.group(1) != hashlib.sha256(data).hexdigest():
        problems.append(f"declared sha256 {declared.group(1)} differs from the file's")
    seen = set()
    for pid, start, end, body, at in passages:
        if pid in seen:
            problems.append(f"{pid} (line {at}): duplicate passage id")
        seen.add(pid)
        if start < 1 or end < start or end > len(lines):
            problems.append(f"{pid}: lines {start}-{end} are outside the file's 1-{len(lines)}")
            continue
        want = lines[start - 1:end]
        if len(body) != len(want):
            problems.append(f"{pid}: quotes {len(body)} lines for lines {start}-{end} ({len(want)})")
            continue
        for k, (got, exp) in enumerate(zip(body, want)):
            if got != exp:
                problems.append(f"{pid}: line {start + k} differs: quoted {got!r}, file {exp!r}")
                break
    return len(passages), problems


def check_map(km, md):
    """Return the problems in the knowledge map's rows, given the sources page."""
    known = {p[0].lower() for p in parse_passages(md)[0]}
    problems = []
    for n, row in enumerate(km.split("\n"), 1):
        if not row.startswith("| "):
            continue
        cells = [c.strip() for c in row.strip().strip("|").split(" | ")]
        if len(cells) != 4 or cells[0] in ("Area", "---") or cells[1] == "---":
            continue
        area, status = cells[0], cells[1]
        if status.startswith("`documented`"):
            links = LINK.findall(row)
            if not links:
                problems.append(f"knowledge-map line {n} ({area}): documented but links to no passage")
            for link in links:
                if link not in known:
                    problems.append(f"knowledge-map line {n} ({area}): link to missing passage {link}")
        elif status.startswith("`unknown`"):
            if len(status[len("`unknown`"):].strip(" ,;:-—")) < 15:
                problems.append(f"knowledge-map line {n} ({area}): unknown without a reason")
        else:
            problems.append(f"knowledge-map line {n} ({area}): status {status!r} is not documented or unknown")
    return problems


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    here = Path(__file__).resolve().parent
    data = Path(argv[1]).read_bytes()
    md = (here / "goal-hlp.md").read_text(encoding="utf-8")
    km = (here.parent / "knowledge-map.md").read_text(encoding="utf-8")
    n, bad = check_quotes(md, data)
    map_bad = check_map(km, md)
    for p in bad + map_bad:
        print("MISMATCH " + p)
    print(f"{n} quotations checked, {len(bad)} mismatches")
    print(f"knowledge-map: {len(map_bad)} problems")
    return 1 if bad or map_bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
