#!/usr/bin/env python3
"""Citations of lines of the named view `static/goal-exe/named/seg_SSSS_NN.c:LINES` in the prose and code.

Regenerating the named view (`docs/process.md`, "The named view") inserts and removes lines, so a line
number cited in a finding, a spec row or an experiment's notes stops pointing at the code it cited
(issue #307: PR 302 moved 20 of them, and many more had moved in earlier regenerations). A line number
carries no text, so `static/goal-exe/named-citations.tsv` records, for every cited line or range of lines,
a hash of its text (the lines from one before the first to one after the last, whitespace-trimmed) and a
preview of its first and last line, as of when the citation was last verified. Then:

    python3 tools/static/named_citations.py check
        exit 1 when a cited line or range no longer holds the recorded text (any line inside a range, or the
        line before or after it), a citation has no row, a row has no citation, or text that looks like a
        citation of the named view cannot be parsed. Run by `tests/test_named_citations.py` and by the quick
        tier of CI.
    python3 tools/static/named_citations.py remap (--base REF | --authored) [--apply]
        after a regeneration: map each cited line from the view it was written against to the new view (the
        lines of a segment's parts, concatenated in part order, aligned whole-line with difflib), print
        `doc:line old -> new (equal|approx; same text: yes|NO)` per cited range (`same text` compares the
        whole range, with its neighbours) and, with --apply, rewrite the citations and write the manifest:
        the text each range had in the old view, at its new lines. REF is the commit before the regeneration
        (every citation was right then); --authored takes, per citation, the named view at the commit that
        introduced the citation's text into the document (for citations left behind by earlier
        regenerations). `equal` is an end that survived; `approx` a changed line (an identifier renamed),
        mapped to the most alike line of what replaced it: read it. A cited line the old view does
        not have is UNRESOLVED; a range whose ends land in two files is left for a hand edit. After a remap
        `check` fails on the ranges whose text was renamed or whose neighbours were: read them, then
        `update --accept`.
    python3 tools/static/named_citations.py update [--accept]
        add the rows of new citations (with the text now there) and drop the rows of removed ones; a row
        whose text changed is refused unless --accept: read the lines first.

What counts as a citation (the forms in the repository, and no others): `seg_SSSS_NN.c:` followed by `N`,
`N-M`, `N–M` (en dash), `N..M`, `N..` (from N on) or a comma list of these (no spaces), written with a
`named/` prefix (`static/goal-exe/named/...`, `static:static/goal-exe/named/...`), or bare after a `named/`
citation on the same line; and an abbreviated `` `:N–M` `` in backticks, which takes the file of the named
citation just before it on the same or the previous line. A bare one after `decompiled/`, `code/` or an `.asm`
file is the raw view's, one with no prefix at all is unreadable, and neither is checked. Text that starts like
a citation of the named view and is anything else (`:12abc`, `:3-4-5`, `.c, lines 5 and 7`) is an error, not
skipped. Not scanned: `static/`, `runs/`, `docs/tasks/` (briefs), `tests/`, every `out/` folder and `*.log`
(raw, immutable outputs, game-archaeologist L207), this tool and the manifest.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
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

_ITEM = r"[0-9]+(?:(?:[-–]|\.\.)[0-9]+|\.\.)?"
LINES = rf"{_ITEM}(?:,{_ITEM})*"
# what may not follow a parsed line list: it would mean the list was read short
_CUT = r"(?:[0-9A-Za-z_]|\.[0-9]|[-–][0-9])"
TOKEN = re.compile(
    r"(?P<pfx>(?:static:)?(?:static/goal-exe/)?(?P<view>named|decompiled|code)/)?"
    r"(?P<file>seg_(?P<seg>[0-9A-F]{4})_(?P<part>[0-9]{2})\.(?P<ext>c|asm))"
    rf"(?::(?P<lines>{LINES})(?P<cut>{_CUT})?)?")
ABBREVIATED = re.compile(rf"(?<=`):(?P<lines>{LINES})(?P<cut>{_CUT})?(?=`)")
LINE_PROSE = re.compile(r"[`)]*,? ?(?:lines?|ll?\.)\s*[0-9]")
ITEM = re.compile(r"([0-9]+)(?:(-|–|\.\.)([0-9]+)?)?")


class Cite:
    """One citation of the named view in a document: the file and each cited item with its span in the text."""

    def __init__(self, doc, line_no, file, span, items, abbreviated=False):
        self.doc, self.line_no, self.file = doc, line_no, file
        self.span = span                      # (start, end) of the lines text within its line
        self.items = items                    # [(a, sep, b)]: `N`, `N-M` (sep "-", "–" or ".."), `N..` (b None)
        self.abbreviated = abbreviated        # no file written: it is the previous citation's

    def ranges(self):
        """The cited (first, last) lines, one pair per item; a single line or `N..` is (N, N)."""
        return [(a, a if b is None else b) for a, _sep, b in self.items]

    def endpoints(self):
        for a, b in self.ranges():
            yield a
            if b != a:
                yield b


class CitationError(Exception):
    pass


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


def parse_items(lines_text):
    items = []
    for it in lines_text.split(","):
        im = ITEM.fullmatch(it)
        items.append((int(im.group(1)), im.group(2), int(im.group(3)) if im.group(3) else None))
    return items


def scan(doc, text):
    """([Cite], [error text]): the citations of the named view in `text`, and what looked like one and is not parsable."""
    cites, errors = [], []
    last = None                                  # the last file token: (line number, ext, is named, file)
    view = None
    for line_no, line in enumerate(text.split("\n"), 1):
        events = [(m.start(), "token", m) for m in TOKEN.finditer(line)]
        events += [(m.start(), "abbreviated", m) for m in ABBREVIATED.finditer(line)]
        view = None
        for _pos, kind, m in sorted(events, key=lambda e: e[0]):
            if kind == "abbreviated":
                if last and last[1] == "c" and last[2] and line_no - last[0] <= 1:
                    if m.group("cut"):
                        errors.append(f"{doc}:{line_no}: cannot parse the lines in `:{m.group('lines')}{m.group('cut')}...`")
                    else:
                        cites.append(Cite(doc, line_no, last[3], (m.start("lines"), m.end("lines")),
                                          parse_items(m.group("lines")), abbreviated=True))
                continue
            if m.group("pfx"):
                view = m.group("view")
            named = (m.group("view") or view) == "named" and m.group("ext") == "c"
            last = (line_no, m.group("ext"), named, m.group("file"))
            if not named:
                continue
            if m.group("lines") is None:
                if LINE_PROSE.match(line[m.end():]):
                    errors.append(f"{doc}:{line_no}: lines of {m.group('file')} cited in words: {line[m.start():m.end() + 30]!r}")
                continue
            if m.group("cut"):
                errors.append(f"{doc}:{line_no}: cannot parse the lines of {line[m.start():m.end() + 12]!r}")
                continue
            cites.append(Cite(doc, line_no, m.group("file"), (m.start("lines"), m.end("lines")),
                              parse_items(m.group("lines"))))
    return cites, errors


def citations_in(doc, text):
    cites, errors = scan(doc, text)
    if errors:
        raise CitationError("; ".join(errors))
    return cites


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


def content(view, file, a, b):
    """The text a citation of lines a..b stands on: those lines and the one before and after, trimmed."""
    lines = view.get(file)
    if lines is None or a < 1 or b > len(lines) or b < a:
        return None
    return "\n".join(norm(lines[i - 1]) if 1 <= i <= len(lines) else "" for i in range(a - 1, b + 2))


def digest(text):
    return None if text is None else hashlib.sha256(text.encode()).hexdigest()[:16]


def preview(view, file, a, b):
    lines = view.get(file) or [""]
    pick = lambda i: norm(lines[i - 1])[:60] if 1 <= i <= len(lines) else ""   # noqa: E731
    return pick(a) if a == b else f"{pick(a)}{SEP}{pick(b)}"


def all_cites(strict=True):
    """Every citation; with strict, text that looks like one and cannot be parsed raises CitationError."""
    cites = []
    for doc in scanned_docs():
        found, errors = scan(doc, (ROOT / doc).read_text())
        if errors and strict:
            raise CitationError("; ".join(errors))
        cites += found
    return cites


def keys_of(cites):
    return {(c.doc, c.file, a, b) for c in cites for a, b in c.ranges()}


def label(file, a, b):
    return f"{file}:{a}" if a == b else f"{file}:{a}-{b}"


def read_manifest():
    rows = {}
    if MANIFEST.exists():
        for ln in MANIFEST.read_text().split("\n")[1:]:
            if ln:
                doc, cite, h, pv = ln.split("\t", 3)
                file, span = cite.split(":")
                a, _, b = span.partition("-")
                rows[(doc, file, int(a), int(b or a))] = (h, pv)
    return rows


def write_manifest(rows):
    body = "".join(f"{d}\t{label(f, a, b)}\t{h}\t{pv}\n" for (d, f, a, b), (h, pv) in sorted(rows.items()))
    MANIFEST.write_text("doc\tcited lines\thash of the text with a neighbour each side\tfirst and last line\n" + body)


def all_errors():
    errors = []
    for doc in scanned_docs():
        errors += scan(doc, (ROOT / doc).read_text())[1]
    return errors


def check():
    """(problems, number of cited ranges): drift, unrecorded citations, orphan rows and unparsable citations."""
    view = view_lines()
    rows = read_manifest()
    problems = all_errors()
    keys = keys_of(all_cites(strict=False))
    for k in sorted(keys):
        doc, file, a, b = k
        h = digest(content(view, file, a, b))
        if k not in rows:
            problems.append(f"{doc}: {label(file, a, b)} is cited but has no row in {MANIFEST.name} (run `update`)")
        elif h is None:
            problems.append(f"{doc}: {label(file, a, b)} is past the end of the file (recorded: {rows[k][1]!r})")
        elif h != rows[k][0]:
            now = preview(view, file, a, b)
            what = (f"now {now!r}, recorded {rows[k][1]!r}" if now != rows[k][1] else
                    "its first and last line are as recorded: a line inside it, or the one before or after, changed")
            problems.append(f"{doc}: {label(file, a, b)} no longer holds the text recorded for it: {what} "
                            f"(run `remap --base <ref before the regeneration>`, or read the lines and `update --accept`)")
    for k in sorted(set(rows) - keys):
        problems.append(f"{MANIFEST.name}: row {label(k[1], k[2], k[3])} for {k[0]} has no citation (run `update`)")
    return problems, len(keys)


def update(accept):
    view = view_lines()
    rows = read_manifest()
    errors = all_errors()
    for e in errors:
        print("refused:", e)
    if errors:
        return 1
    keys = keys_of(all_cites())
    new, refused = {}, []
    for k in sorted(keys):
        h = digest(content(view, k[1], k[2], k[3]))
        pv = preview(view, k[1], k[2], k[3])
        if h is None:
            refused.append(f"{k[0]}: {label(*k[1:])} is past the end of the file")
        elif k in rows and rows[k][0] != h and not accept:
            refused.append(f"{k[0]}: {label(*k[1:])} now holds {pv!r}, recorded {rows[k][1]!r}")
        else:
            new[k] = (h, pv)
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
    part order, matched whole-line with difflib; an old line the regeneration changed maps to the line at the same
    alike line of what replaced it, a deleted one to the nearest line before that survived."""
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
            elif tag == "replace":          # the most alike line of what replaced it (a renamed identifier)
                cand = range(b1, b2) if b2 - b1 <= 200 else [b1 + min(k - a1, b2 - b1 - 1)]
                j = max(cand, key=lambda j: (difflib.SequenceMatcher(None, ol[k], nl[j], autojunk=False).ratio(),
                                             -abs((j - b1) - (k - a1))))
                mp[ow[k]] = (*nw[j], False)
            else:
                mp[ow[k]] = (*nw[last], False)
    heads = {}
    for k, ln in enumerate(nl):
        h = heading_of(ln)
        if h:
            heads[h] = nw[k]
    for k, ln in enumerate(ol):                 # a renamed routine heading is found by its address
        h = heading_of(ln)
        if h in heads and not mp[ow[k]][2]:
            mp[ow[k]] = (*heads[h], False)
    return mp


def authoring_commit(doc, key, ref="HEAD"):
    """The newest commit that introduced the exact text `key` into `doc`, or None.

    A merge that brought the text from one parent is followed into that parent, where it was written."""
    for c in git("log", "-m", "--format=%H", "-S" + key, ref, "--", doc).split():
        parents = git("show", "-s", "--format=%P", c).split()
        count = git("show", f"{c}:{doc}", check=False).count(key)
        having = [p for p in parents if git("show", f"{p}:{doc}", check=False).count(key) >= count]
        if not parents or not having:
            return c
        if len(parents) == 1:
            continue
        found = authoring_commit(doc, key, having[-1])
        if found:
            return found
    return None


def remap(base, authored, apply):
    """Move every citation from the lines it cited in the view it was written against to the same lines of the new view."""
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
                intro = authoring_commit(doc, f":{raw}" if c.abbreviated else f"{c.file}:{raw}")
                ref = git("log", "-1", "--format=%H", intro, "--", NAMED_DIR).strip() if intro else None
            where, bad = [], False
            for a, b in c.ranges():
                old = content(old_view(ref), c.file, a, b) if ref else None
                if old is None:
                    print(f"{doc}:{c.line_no}  {label(c.file, a, b)}  UNRESOLVED, not in the view it was written against"
                          f" ({ref[:8] if ref else 'no commit introduced it'})")
                    unresolved += 1
                    bad = True
                    continue
                mp = mapping(ref, c.file[4:8])
                (fa, na, eq_a), (fb, nb, eq_b) = mp[(c.file, a)], mp[(c.file, b)]
                where.append((a, b, fa, na, fb, nb, eq_a and eq_b, old, preview(old_view(ref), c.file, a, b)))
            if bad:
                continue
            shifted = [w for w in where if (w[2], w[3], w[5]) != (c.file, w[0], w[1])]
            for a, b, fa, na, fb, nb, equal, old, pv in where:
                if fa == fb:
                    rows[(doc, fa, na, nb)] = (digest(old), pv)
            for a, b, fa, na, fb, nb, equal, old, pv in shifted:
                now = content(new, fa, na, nb) if fa == fb else None
                same = now is not None and digest(now) == digest(old)
                alike = "" if now is None else f", {difflib.SequenceMatcher(None, old.split(chr(10)), now.split(chr(10)), autojunk=False).ratio():.2f} of its lines alike"
                print(f"{doc}:{c.line_no}  {label(c.file, a, b)} -> {label(fa, na, nb) if fa == fb else f'{fa}:{na}..{fb}:{nb}'}"
                      f"  ({'equal' if equal else 'approx'}; same text: {'yes' if same else f'NO{alike}'}) | {pv[:80]}")
            if not shifted:
                continue
            moved += 1
            files = {w[2] for w in where} | {w[4] for w in where}
            if len(files) != 1 or (c.abbreviated and files != {c.file}):
                print(f"{doc}:{c.line_no}  the citation would span {sorted(files)}: edit by hand")
                split += 1
                for a, b, fa, na, fb, nb, equal, old, pv in where:      # keep the rows of what a hand edit will cite
                    rows.pop((doc, fa, na, nb), None)
                continue
            parts = []
            for (a, sep, b), (_a, _b, fa, na, fb, nb, *_rest) in zip(c.items, where):
                parts.append(str(na) if sep is None else f"{na}{sep}{nb}" if b is not None else f"{na}..")
            edits.append((c, next(iter(files)), ",".join(parts)))
        if apply and edits:
            for c, new_file, new_lines in sorted(edits, key=lambda x: (x[0].line_no, x[0].span[0]), reverse=True):
                s, e_ = c.span
                line = lines[c.line_no - 1]
                head = line[:s]
                if new_file != c.file and not c.abbreviated:
                    head = head[:len(head) - 1 - len(c.file)] + new_file + ":"
                lines[c.line_no - 1] = head + new_lines + line[e_:]
            path.write_text("\n".join(lines))
    print(f"{moved} citations moved, {unresolved} cited ranges not in their old view, {split} to edit by hand")
    if apply:
        write_manifest(rows)
    return 1 if unresolved or split else 0


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
        print(f"{n} cited ranges, {len(problems)} problems")
        return 1 if problems else 0
    if a.cmd == "update":
        return update(a.accept)
    return remap(a.base, a.authored, a.apply)


if __name__ == "__main__":
    sys.exit(main())
