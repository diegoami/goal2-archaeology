#!/usr/bin/env python3
"""Check the annotations of static/goal-exe/annotations/ and print their coverage (T20).

    python3 tools/static/check_annotations.py [--annotations DIR] [--routines FILE] [--findings DIR]

The annotations name what the decompiled GOAL.EXE means; tools/static/decompile.sh --annotations
applies them to write static/goal-exe/named/. Four TSV files, each with a header line:

  routines.tsv  address (SSSS:OOOO), name, purpose, confidence, basis
  records.tsv   record, size (0xNN), purpose, basis
  fields.tsv    record, offset (0xNN), name, type, purpose, confidence, basis
  globals.tsv   address (DS:XXXX), name, type (or -), purpose, confidence, basis

Checked, each failing the run with a message naming the file and line:
  - a routine's address is a routine of static/goal-exe/routines.tsv; a global's lies in the data
    segment 2581; a field's offset and size lie inside its record, and fields do not overlap;
  - names are valid C identifiers, not C keywords, not Ghidra's or the raw view's generated names
    (f_SSSS_OOOO, FUN_, DAT_, LAB_, ...), unique among routines and globals, unique within a record;
  - confidence is one of CONFIDENCE; `established` needs a finding id in the basis;
  - a basis is present: `; `-separated parts, each a finding id F<nnn> with a file findings/F<nnn>-*.md,
    or `read <path>` with <path> (an optional :line suffix aside) an existing file under static/goal-exe/;
  - a type is byte, char, word, int16, dword, a record, X[N] or "X far*";
  - every routine of a run-time library segment (RTL_SEGMENTS) has a row.
Then it prints the coverage per code segment: named / routines of routines.tsv.
"""
from __future__ import annotations

import argparse
import keyword
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIDENCE = ("established", "likely", "guess")
# Turbo Pascal's System unit (23E4), CRT (2382), Dos (235C) and the library units 214B, 2138, 2139
# (decompiled/README.md, T18; F002): T20 labels every routine of these.
RTL_SEGMENTS = ("214B", "2138", "2139", "235C", "2382", "23E4")
# The data segment 2581 runs up to the stack segment 3052 (static/goal-exe/README.md): 0xAD10 bytes.
DATA_SEGMENT_BYTES = (0x3052 - 0x2581) * 16
C_KEYWORDS = {
    "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum",
    "extern", "float", "for", "goto", "if", "inline", "int", "long", "register", "restrict", "return",
    "short", "signed", "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void",
    "volatile", "while", "far", "near", "byte", "word", "dword", "bool",
}
GENERATED = re.compile(r"^(f_[0-9A-F]{4}_[0-9A-F]{4}|(FUN|DAT|LAB|PTR|SUB|UNK|ABS|func|code_r)_.*|"
                       r"(param|local)_[0-9a-f]+|[a-z]{1,3}Var\d+|in_[A-Z][A-Za-z]*|in_stack_.*|"
                       r"(unaff|extraout)_.*)$")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
BASE_TYPES = {"byte": 1, "char": 1, "word": 2, "int16": 2, "dword": 4}

HEADERS = {
    "routines.tsv": ["address", "name", "purpose", "confidence", "basis"],
    "records.tsv": ["record", "size", "purpose", "basis"],
    "fields.tsv": ["record", "offset", "name", "type", "purpose", "confidence", "basis"],
    "globals.tsv": ["address", "name", "type", "purpose", "confidence", "basis"],
}


class Checker:
    def __init__(self, annotations: Path, routines: Path, findings: Path, static: Path):
        self.dir = annotations
        self.findings = findings
        self.static = static
        self.routines = read_routine_addresses(routines)
        self.errors: list[str] = []
        self.rows: dict[str, list[tuple[int, dict[str, str]]]] = {}

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def load(self) -> None:
        for name, header in HEADERS.items():
            path = self.dir / name
            if not path.is_file():
                self.error(name, "missing")
                self.rows[name] = []
                continue
            lines = path.read_text(encoding="utf-8").split("\n")
            if lines and lines[-1] == "":
                lines.pop()
            if not lines or lines[0].split("\t") != header:
                self.error(f"{name}:1", f"header must be {chr(9).join(header)!r}")
            rows = []
            for i, line in enumerate(lines[1:], start=2):
                if not line.strip() or line.startswith(";"):
                    continue
                cells = line.split("\t")
                if len(cells) != len(header) or any(not c.strip() for c in cells):
                    self.error(f"{name}:{i}", f"{len(header)} non-empty tab-separated cells needed")
                    continue
                rows.append((i, dict(zip(header, cells))))
            self.rows[name] = rows

    def check(self) -> None:
        self.load()
        records = {}
        for i, r in self.rows["records.tsv"]:
            where = f"records.tsv:{i}"
            self.check_name(where, r["record"])
            size = parse_hex(r["size"])
            if size is None or size <= 0:
                self.error(where, f"size {r['size']!r} is not 0x<hex> > 0")
                continue
            if r["record"] in records:
                self.error(where, f"record {r['record']} defined twice")
            records[r["record"]] = size
            self.check_basis(where, r["basis"], None)
        self.records = records

        names = Counter()
        for i, r in self.rows["routines.tsv"]:
            where = f"routines.tsv:{i}"
            if r["address"] not in self.routines:
                self.error(where, f"address {r['address']} is not a routine of routines.tsv")
            self.check_name(where, r["name"])
            names[r["name"]] += 1
            self.check_confidence(where, r)
        for i, r in self.rows["globals.tsv"]:
            where = f"globals.tsv:{i}"
            m = re.fullmatch(r"DS:([0-9A-F]{4})", r["address"])
            size = 1 if r["type"] == "-" else self.type_size(where, r["type"])
            if not m:
                self.error(where, f"address {r['address']!r} is not DS:XXXX (upper-case hex)")
            elif size is not None and int(m.group(1), 16) + size > DATA_SEGMENT_BYTES:
                self.error(where, f"{r['address']} is outside the data segment (0x{DATA_SEGMENT_BYTES:X} bytes)")
            self.check_name(where, r["name"])
            names[r["name"]] += 1
            self.check_confidence(where, r)
        for name, n in names.items():
            if n > 1:
                self.error("routines.tsv/globals.tsv", f"name {name} used {n} times")
        for dup in sorted({a for a, n in Counter(r["address"] for _, r in self.rows["routines.tsv"]).items() if n > 1}):
            self.error("routines.tsv", f"address {dup} has more than one row")
        for dup in sorted({a for a, n in Counter(r["address"] for _, r in self.rows["globals.tsv"]).items() if n > 1}):
            self.error("globals.tsv", f"address {dup} has more than one row")

        spans: dict[str, list[tuple[int, int, str]]] = {}
        fnames: dict[str, Counter] = {}
        for i, r in self.rows["fields.tsv"]:
            where = f"fields.tsv:{i}"
            self.check_name(where, r["name"])
            self.check_confidence(where, r)
            if r["record"] not in records:
                self.error(where, f"record {r['record']} not in records.tsv")
                continue
            fnames.setdefault(r["record"], Counter())[r["name"]] += 1
            off = parse_hex(r["offset"])
            size = self.type_size(where, r["type"])
            if off is None:
                self.error(where, f"offset {r['offset']!r} is not 0x<hex>")
                continue
            if size is None:
                continue
            if off + size > records[r["record"]]:
                self.error(where, f"{r['name']} (+0x{off:X}, {size} bytes) runs past the record's "
                                  f"0x{records[r['record']]:X} bytes")
            for a, b, other in spans.get(r["record"], []):
                if off < b and a < off + size:
                    self.error(where, f"{r['name']} overlaps {other}")
            spans.setdefault(r["record"], []).append((off, off + size, r["name"]))
        for record, c in fnames.items():
            for name, n in c.items():
                if n > 1:
                    self.error("fields.tsv", f"field name {record}.{name} used {n} times")

        named = {r["address"] for _, r in self.rows["routines.tsv"]}
        for seg in RTL_SEGMENTS:
            missing = sorted(a for a in self.routines if a.startswith(seg + ":") and a not in named)
            if missing:
                self.error("routines.tsv", f"run-time library segment {seg}: {len(missing)} routine(s) "
                                           f"without a row, first {missing[0]}")

    def check_name(self, where: str, name: str) -> None:
        if not IDENT.match(name):
            self.error(where, f"name {name!r} is not a C identifier")
        elif keyword.iskeyword(name) or name in C_KEYWORDS:
            self.error(where, f"name {name!r} is a keyword or type name")
        elif GENERATED.match(name):
            self.error(where, f"name {name!r} looks like a generated name")

    def check_confidence(self, where: str, r: dict[str, str]) -> None:
        if r["confidence"] not in CONFIDENCE:
            self.error(where, f"confidence {r['confidence']!r} is not one of {', '.join(CONFIDENCE)}")
        self.check_basis(where, r["basis"], r["confidence"])

    def check_basis(self, where: str, basis: str, confidence: str | None) -> None:
        parts = [p.strip() for p in basis.split(";")]
        has_finding = False
        for p in parts:
            if re.fullmatch(r"F\d{3}", p):
                has_finding = True
                if not list(self.findings.glob(f"{p}-*.md")):
                    self.error(where, f"basis {p}: no file findings/{p}-*.md")
            elif p.startswith("read "):
                path = p[5:].strip().split(":")[0]
                if not path or ".." in Path(path).parts or not (self.static / path).is_file():
                    self.error(where, f"basis {p!r}: no file static/goal-exe/{path}")
            else:
                self.error(where, f"basis part {p!r} is neither a finding id F<nnn> nor 'read <path>'")
        if confidence == "established" and not has_finding:
            self.error(where, "confidence established needs a finding id in the basis")

    def type_size(self, where: str, spec: str) -> int | None:
        spec = spec.strip()
        if spec.endswith(" far*"):
            return 4 if self.type_size(where, spec[:-5]) is not None else None
        m = re.fullmatch(r"(.+)\[(\d+)\]", spec)
        if m:
            inner = self.type_size(where, m.group(1))
            return None if inner is None or int(m.group(2)) < 1 else inner * int(m.group(2))
        if spec in BASE_TYPES:
            return BASE_TYPES[spec]
        if spec in getattr(self, "records", {}):
            return self.records[spec]
        self.error(where, f"type {spec!r} unknown")
        return None

    def coverage(self) -> list[tuple[str, int, int]]:
        named = {r["address"] for _, r in self.rows["routines.tsv"]}
        out = []
        for seg in sorted({a.split(":")[0] for a in self.routines}):
            total = [a for a in self.routines if a.startswith(seg + ":")]
            out.append((seg, len([a for a in total if a in named]), len(total)))
        return out


def parse_hex(s: str) -> int | None:
    return int(s[2:], 16) if re.fullmatch(r"0x[0-9A-F]+", s) else None


def read_routine_addresses(path: Path) -> set[str]:
    out = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(";") or line.startswith("segment:") or not line.strip():
            continue
        out.add(line.split("\t", 1)[0])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--annotations", type=Path, default=ROOT / "static/goal-exe/annotations")
    ap.add_argument("--routines", type=Path, default=ROOT / "static/goal-exe/routines.tsv")
    ap.add_argument("--findings", type=Path, default=ROOT / "findings")
    ap.add_argument("--static", type=Path, default=ROOT / "static/goal-exe")
    a = ap.parse_args(argv)
    c = Checker(a.annotations, a.routines, a.findings, a.static)
    c.check()
    for e in c.errors:
        print(f"check_annotations: {e}", file=sys.stderr)
    print("segment\tnamed\troutines")
    for seg, n, total in c.coverage():
        tag = "  (run-time library)" if seg in RTL_SEGMENTS else ""
        print(f"{seg}\t{n}\t{total}{tag}")
    print(f"records {len(c.rows['records.tsv'])}, fields {len(c.rows['fields.tsv'])}, "
          f"globals {len(c.rows['globals.tsv'])}")
    if c.errors:
        print(f"check_annotations: {len(c.errors)} error(s)", file=sys.stderr)
        return 1
    print("check_annotations: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
