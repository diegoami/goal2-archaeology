"""E024 (rework 2): does every `read <file>[:lines]` citation of a routines.tsv row lie in that row's routine?

    python3 -B experiments/E024-computer-managers/check_annotation_citations.py [--base REF] [--all]

For each row of static/goal-exe/annotations/routines.tsv that is new or changed against REF (default 434bc08,
this branch's base; --all: every row) and each citation in its basis column of the form `read PATH[:LINES]`
(PATH under code/, named/ or decompiled/, relative to static/goal-exe/; LINES `N`, `N-M` or a comma list):
  - with LINES: the lines are found in the CURRENT file and the enclosing routine of the first and last line is
    taken (the nearest preceding `// ---- ADDR` heading of named/ and decompiled/, or `; ---- routine ADDR` of
    code/); it must be the row's own address;
  - without LINES: the file must contain the row's heading.
The citations in the other columns (purpose text) are listed too when they carry `seg_...:LINE`. Prints
`OK` / `MISMATCH` per citation and exits 1 on any mismatch. Log: out/check-annotation-citations-<UTC>.log.
"""
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = static = ROOT / "static/goal-exe"
REF = "434bc08"
if "--base" in sys.argv:
    REF = sys.argv[sys.argv.index("--base") + 1]
ALL = "--all" in sys.argv
lines_out = []


def out(s):
    lines_out.append(s)
    print(s)


def rows(text):
    return [ln.split("\t") for ln in text.split("\n")[1:] if ln.strip()]


cur = rows((static / "annotations/routines.tsv").read_text())
old = {r[0]: r for r in rows(subprocess.run(["git", "show", f"{REF}:static/goal-exe/annotations/routines.tsv"],
                                            capture_output=True, text=True, cwd=ROOT).stdout)}
HEAD = re.compile(r"^(?://\s*----\s+([0-9A-F]{4}:[0-9A-F]{4})\b|;\s*----\s+routine\s+([0-9A-F]{4}:[0-9A-F]{4})\b)")


def enclosing(path, n):
    last = None
    for i, ln in enumerate(path.read_text().split("\n"), 1):
        if i > n:
            break
        m = HEAD.match(ln)
        if m:
            last = m.group(1) or m.group(2)
    return last


CITE = re.compile(r"((?:named|decompiled|code)/seg_[0-9A-F]{4}_[0-9]{2}\.(?:c|asm))(?::([0-9][0-9,\-]*))?")
bad = n = 0
for r in cur:
    if not ALL and old.get(r[0]) == r:
        continue
    for col in (2, 4):
        if len(r) <= col:
            continue
        for m in CITE.finditer(r[col]):
            f, lines = m.group(1), m.group(2)
            p = static / f
            if not p.exists():
                out(f"MISMATCH {r[0]} {f}: no such file")
                bad += 1
                continue
            n += 1
            if lines:
                ends = [int(x) for x in re.split(r"[-,]", lines.strip(",-")) if x]
                encl = {enclosing(p, ends[0]), enclosing(p, ends[-1])}
                ok = encl == {r[0]}
                out(f"{'OK      ' if ok else 'MISMATCH'} {r[0]} {r[1]} col{col + 1}: {f}:{lines} lies in {sorted(map(str, encl))}")
            else:
                ok = (r[0] in p.read_text()) if f.startswith("code/") else bool(re.search(
                    r"----\s+" + re.escape(r[0]) + r"\b", p.read_text()))
                out(f"{'OK      ' if ok else 'MISMATCH'} {r[0]} {r[1]} col{col + 1}: {f} (no lines) {'contains' if ok else 'does not contain'} the routine")
            bad += not ok
out(f"citations checked: {n}, mismatches: {bad} (rows {'all' if ALL else 'new or changed against ' + REF})")
fn = HERE / "out" / f"check-annotation-citations-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines_out) + "\n")
print("log:", fn)
sys.exit(1 if bad else 0)
