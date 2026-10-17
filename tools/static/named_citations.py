#!/usr/bin/env python3
"""Citations of lines of the named view `static/goal-exe/named/seg_SSSS_NN.c:LINE` in the prose and code.

Regenerating the named view (`docs/process.md`, "The named view") inserts and removes lines, so a line
number cited in a finding, a spec row or an experiment's notes stops pointing at the code it cited
(issue #307: PR 302 moved 20 of them, and many more had moved in earlier regenerations). A line number
carries no text, so the text each citation pointed at is recorded in `static/goal-exe/named-citations.tsv`
(document, cited file and line, the line's text with the line before and after it, as of when the
citation was last verified), and:

    python3 tools/static/named_citations.py check
        exit 1 when a cited line no longer holds the recorded text, a citation has no row, or a row has no
        citation (the unit test `tests/test_named_citations.py` runs it).
    python3 tools/static/named_citations.py remap (--base REF | --authored) [--apply]
        after a regeneration: map each cited line from the view it was written against to the new view (the
        lines of a segment's parts, concatenated in part order, aligned whole-line with difflib), print
        `doc:line old -> new (equal|approx; same text: yes|NO)` and, with --apply, rewrite the citations and
        write the manifest: the text each citation had in the old view, at its new line. REF is the commit
        before the regeneration (every citation was right then); --authored takes, per citation, the named
        view at the commit that introduced the citation's text into the document (for citations that were
        left behind by earlier regenerations). `equal` is a line that survived; `approx` a changed line (an
        identifier renamed), mapped to the nearest line before it that survived: read it. A cited line the old
        view does not have is UNRESOLVED. After a remap `check` fails on the lines whose neighbours were
        renamed, with both texts: read them, then `update --accept`.
    python3 tools/static/named_citations.py update [--accept]
        add the rows of new citations (with the text now there) and drop the rows of removed ones; a row
        whose line now holds other text is refused unless --accept: read the line first.

What counts as a citation: `seg_SSSS_NN.c:N`, `N-M`, `N–M` or a comma list (`N,M-K`, no spaces) written with
a `named/` prefix (`static/goal-exe/named/...`, `static:static/goal-exe/named/...`), or bare after a `named/`
citation on the same line. A bare one after `decompiled/` or `code/` is the raw view's, and one with no prefix
at all is unreadable and not checked. A range is checked at both ends. Not scanned: `static/`, `runs/`,
`docs/tasks/` (briefs), `tests/`, every `out/` folder and `*.log` (raw, immutable outputs, game-archaeologist
L207), this tool and the manifest.
"""
from __future__ import annotations

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMED_DIR = "static/goal-exe/named"
MANIFEST = ROOT / "static/goal-exe/named-citations.tsv"
SCAN_SUFFIX = (".md", ".py")
SKIP_PREFIX = ("static/", "runs/", "docs/tasks/", "tests/")
SKIP_FILES = {"tools/static/named_citations.py"}
SEP = " ¦ "

TOKEN = re.compile(
    r"(?P<pfx>(?:static:)?(?:static/goal-exe/)?(?P<view>named|decompiled|code)/)?"
    r"(?P<file>seg_(?P<seg>[0-9A-F]{4})_(?P<part>[0-9]{2})\.(?P<ext>c|asm))"
    r"(?::(?P<lines>[0-9]+(?:[-–][0-9]+)?(?:,[0-9]+(?:[-–][0-9]+)?)*))?")
ITEM = re.compile(r"([0-9]+)(?:([-–])([0-9]+))?")


class Cite:
    """One named-view citation in a document: the file, and each cited line with its span in the text."""

    def __init__(self, doc, line_no, file, span, items):
        self.doc, self.line_no, self.file = doc, line_no, file
        self.span = span                      # (start, end) of the lines text within its line
        self.items = items                    # [(a, sep, b)] with sep and b None for a single line

    def endpoints(self):
        for a, _sep, b in self.items:
            yield a
            if b is not None:
                yield b


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def scanned_docs():
    for p in git("ls-files").split("\n"):
        if not p or not p.endswith(SCAN_SUFFIX) or p in SKIP_FILES or p.startswith(SKIP_PREFIX) or "/out/" in p:
            continue
        if (ROOT / p).is_file():
            yield p


def citations_in(doc, text):
    """The named-view citations with lines in `text`, in order."""
    out = []
    for line_no, line in enumerate(text.split("\n"), 1):
        view = None
        for m in TOKEN.finditer(line):
            if m.group("pfx"):
                view = m.group("view")
            if m.group("ext") != "c" or m.group("lines") is None:
                continue
            if (m.group("view") or view) != "named":
                continue
            items = []
            for it in m.group("lines").split(","):
                im = ITEM.fullmatch(it)
                items.append((int(im.group(1)), im.group(2), int(im.group(3)) if im.group(3) else None))
            out.append(Cite(doc, line_no, m.group("file"), (m.start("lines"), m.end("lines")), items))
    return out


def norm(s):
    return s.replace("\t", "    ").strip()


def view_lines(ref=None):
    """{file name: [lines]} of the named view at `ref` (None: the working tree)."""
    out = {}
    if ref is None:
        for p in sorted((ROOT / NAMED_DIR).glob("seg_*.c")):
            out[p.name] = p.read_text().split("\n")
    else:
        for n in git("ls-tree", "--name-only", ref, NAMED_DIR + "/").split():
            if Path(n).name.startswith("seg_") and n.endswith(".c"):
                out[Path(n).name] = git("show", f"{ref}:{n}").split("\n")
    return out


def text_at(view, file, line):
    """The cited line and the lines before and after it, joined (a lone `}` or a blank line says too little)."""
    lines = view.get(file)
    if lines is None or not 1 <= line <= len(lines):
        return None
    return SEP.join(norm(lines[i - 1]) if 1 <= i <= len(lines) else "" for i in (line - 1, line, line + 1))


def all_cites():
    cites = []
    for doc in scanned_docs():
        cites += citations_in(doc, (ROOT / doc).read_text())
    return cites


def keys_of(cites):
    return {(c.doc, c.file, n) for c in cites for n in c.endpoints()}


def read_manifest():
    rows = {}
    if MANIFEST.exists():
        for ln in MANIFEST.read_text().split("\n")[1:]:
            if ln:
                doc, cite, text = ln.split("\t", 2)
                file, n = cite.rsplit(":", 1)
                rows[(doc, file, int(n))] = text
    return rows


def write_manifest(rows):
    body = "".join(f"{d}\t{f}:{n}\t{t}\n" for (d, f, n), t in sorted(rows.items()))
    MANIFEST.write_text("doc\tcited line\ttext when verified\n" + body)


def check():
    """(problems, number of cited lines): drift, unrecorded citations and orphan rows."""
    view = view_lines()
    rows = read_manifest()
    keys = keys_of(all_cites())
    problems = []
    for k in sorted(keys):
        doc, file, n = k
        now = text_at(view, file, n)
        if k not in rows:
            problems.append(f"{doc}: {file}:{n} is cited but has no row in {MANIFEST.name} (run `update`)")
        elif now is None:
            problems.append(f"{doc}: {file}:{n} is past the end of the file (recorded: {rows[k]!r})")
        elif now != rows[k]:
            problems.append(f"{doc}: {file}:{n} now holds {now!r}, recorded {rows[k]!r} (run `remap --base <ref before the regeneration>`)")
    for k in sorted(set(rows) - keys):
        problems.append(f"{MANIFEST.name}: row {k[1]}:{k[2]} for {k[0]} has no citation (run `update`)")
    return problems, len(keys)


def update(accept):
    view = view_lines()
    rows = read_manifest()
    keys = keys_of(all_cites())
    new, refused = {}, []
    for k in sorted(keys):
        now = text_at(view, k[1], k[2])
        if now is None:
            refused.append(f"{k[0]}: {k[1]}:{k[2]} is past the end of the file")
        elif k in rows and rows[k] != now and not accept:
            refused.append(f"{k[0]}: {k[1]}:{k[2]} now holds {now!r}, recorded {rows[k]!r}")
        else:
            new[k] = now
    for r in refused:
        print("refused:", r)
    if refused:
        return 1
    write_manifest(new)
    print(f"{MANIFEST.name}: {len(new)} rows ({len(set(new) - set(rows))} added, {len(set(rows) - set(new))} dropped)")
    return 0


def heading_of(text):
    """The `SSSS:OOOO` of a routine heading line (`// ---- 0791:DB38  name ...`), or None."""
    m = re.match(r"// ---- ([0-9A-F]{4}:[0-9A-F]{4})\b", text.strip())
    return m.group(1) if m else None


def line_map(old, new, seg):
    """{(file, old line): (file, new line, equal?)} for the segment `seg`: the lines of its parts, concatenated in
    part order, matched whole-line with difflib; an old line the regeneration changed maps to the nearest line
    before it that survived."""
    def flat(view):
        lines, where = [], []
        for f in sorted(f for f in view if f[4:8] == seg):
            for i, ln in enumerate(view[f], 1):
                lines.append(ln)
                where.append((f, i))
        return lines, where
    ol, ow = flat(old)
    nl, nw = flat(new)
    mp, last = {}, 0
    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(None, ol, nl, autojunk=False).get_opcodes():
        for k in range(a1, a2):
            if tag == "equal":
                last = b1 + (k - a1)
                mp[ow[k]] = (*nw[last], True)
            elif tag == "replace":          # the changed line sits at the same offset in what replaced it
                mp[ow[k]] = (*nw[b1 + min(k - a1, b2 - b1 - 1)], False)
            else:                           # deleted: the nearest line before that survived
                mp[ow[k]] = (*nw[last], False)
    heads = {}
    for k, ln in enumerate(nl):
        h = heading_of(ln)
        if h:
            heads[h] = nw[k]
    for k, ln in enumerate(ol):             # a renamed routine heading is found by its address
        h = heading_of(ln)
        if h in heads and not mp[ow[k]][2]:
            mp[ow[k]] = (*heads[h], False)
    return mp


def remap(base, authored, apply):
    """Move every citation from the line it cited in the view it was written against to the same line of the new view."""
    new = view_lines()
    views, maps = {}, {}

    def old_view(ref):
        if ref not in views:
            views[ref] = view_lines(ref)
        return views[ref]

    def mapping(ref, seg):
        if (ref, seg) not in maps:
            maps[(ref, seg)] = line_map(old_view(ref), new, seg)
        return maps[(ref, seg)]
    rows, moved, unresolved, split = {}, 0, 0, 0
    for doc in sorted({c.doc for c in all_cites()}):
        path = ROOT / doc
        text = path.read_text()
        lines = text.split("\n")
        edits = []
        for c in citations_in(doc, text):
            ref = base
            if authored:
                raw = lines[c.line_no - 1][c.span[0]:c.span[1]]
                intro = authoring_commit(doc, c.file, raw)
                ref = git("log", "-1", "--format=%H", intro, "--", NAMED_DIR).strip() if intro else None
            where, bad = {}, False
            for e in sorted(set(c.endpoints())):
                old_text = text_at(old_view(ref), c.file, e) if ref else None
                if old_text is None:
                    print(f"{doc}:{c.line_no}  {c.file}:{e}  UNRESOLVED, the line is not in the view it was written against"
                          f" ({ref[:8] if ref else 'no commit introduced it'})")
                    unresolved += 1
                    bad = True
                    continue
                f, i, equal = mapping(ref, c.file[4:8])[(c.file, e)]
                where[e] = (f, i, equal, old_text)
            if bad:
                continue
            for e, (f, i, equal, old_text) in where.items():
                rows[(doc, f, i)] = old_text
            shifted = {e: w for e, w in where.items() if (w[0], w[1]) != (c.file, e)}
            for e, (f, i, equal, old_text) in shifted.items():
                same = text_at(new, f, i) == old_text
                print(f"{doc}:{c.line_no}  {c.file}:{e} -> {f}:{i}  ({'equal' if equal else 'approx'}; "
                      f"same text: {'yes' if same else 'NO'}) | {old_text.split(SEP)[1][:70]}")
            if not shifted:
                continue
            moved += 1
            files = {w[0] for w in where.values()}
            if len(files) != 1:
                print(f"{doc}:{c.line_no}  the citation would span {sorted(files)}: edit by hand")
                split += 1
                continue
            new_items = [str(where[a][1]) if b is None else f"{where[a][1]}{sep}{where[b][1]}" for a, sep, b in c.items]
            edits.append((c, next(iter(files)), ",".join(new_items)))
        if apply and edits:
            for c, new_file, new_lines in sorted(edits, key=lambda x: (x[0].line_no, x[0].span[0]), reverse=True):
                s, e_ = c.span
                line = lines[c.line_no - 1]
                head = line[:s]
                if new_file != c.file:
                    head = head[:len(head) - 1 - len(c.file)] + new_file + ":"
                lines[c.line_no - 1] = head + new_lines + line[e_:]
            path.write_text("\n".join(lines))
    print(f"{moved} citations moved, {unresolved} cited lines not in their old view, {split} to edit by hand")
    if apply:
        write_manifest(rows)
    return 1 if unresolved or split else 0


def authoring_commit(doc, file, lines_text, ref="HEAD"):
    """The newest commit that introduced this exact citation string into `doc`, or None.

    A merge that brought the string from one parent is followed into that parent, where it was written."""
    key = f"{file}:{lines_text}"
    for c in git("log", "-m", "--format=%H", "-S" + key, ref, "--", doc).split():
        parents = git("show", "-s", "--format=%P", c).split()
        count = git("show", f"{c}:{doc}", check=False).count(key)
        having = [p for p in parents if git("show", f"{p}:{doc}", check=False).count(key) >= count]
        if not parents or not having:
            return c
        if len(parents) == 1:
            continue
        found = authoring_commit(doc, file, lines_text, having[-1])
        if found:
            return found
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    u = sub.add_parser("update")
    u.add_argument("--accept", action="store_true")
    r = sub.add_parser("remap")
    grp = r.add_mutually_exclusive_group(required=True)
    grp.add_argument("--base")
    grp.add_argument("--authored", action="store_true")
    r.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        problems, n = check()
        for p in problems:
            print(p)
        print(f"{n} cited lines, {len(problems)} problems")
        return 1 if problems else 0
    if a.cmd == "update":
        return update(a.accept)
    return remap(a.base, a.authored, a.apply)


if __name__ == "__main__":
    sys.exit(main())
