#!/usr/bin/env python3
"""Turn the raw output of tools/static/ghidra/GoalDecompile.java into static/goal-exe/decompiled/ (T18).

Called by tools/static/decompile.sh; not normally run by hand. It reads the raw per-function C,
rewrites Ghidra's addresses into the listing's SEGMENT:OFFSET numbering, splits the functions into
one or more files per code segment, and writes index.tsv and README.md. The output depends only on
its inputs, so the same raw output always gives the same files.

Ghidra holds listing segment number k (ascending) at Ghidra segment k*0x1000 (GoalSetup.java says
why); segmap.tsv gives the pairs. The rewriting:
  DAT_b000_9a3e, _DAT_b000_9a3e (data segment)   -> DS:9A3E
  DAT_/LAB_/PTR_<ghidra seg>_<offset>             -> DAT_/LAB_/PTR_<SSSS>_<OOOO> (listing numbering)
  DAT_0000_0449 (past the program's bytes in that Ghidra segment: memory outside GOAL.EXE, such as
  the BIOS data area at 0040:0049)                 -> ABS_00449 (the physical address)
  func_0x0002abcd, code_r0x0002abcd (linear)      -> func_0791_ABCD, code_r_0791_ABCD
  (ram,0x0002abcd) in Ghidra's warnings           -> (0791:ABCD)
Numbers in the code (a pushed segment such as 0xb000) are left as Ghidra wrote them; README.md
gives the table to read them.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_BYTES = 40_000  # about 12k tokens of C, under the 20k-token rule (CLAUDE.md rule 16)
DATA_SEGMENT = 0x2581    # static/goal-exe/README.md

HEADER = re.compile(r"^@@FUNC (\S+) (\S+) (\S+) (ok|failed)(?: (.*))?$")


@dataclass
class Function:
    ghidra: str          # Ghidra address, e.g. 2000:97d0
    name: str            # f_SSSS_OOOO
    convention: str
    ok: bool
    error: str
    code: str

    @property
    def listing(self) -> str:
        _, seg, off = self.name.split("_")
        return f"{seg}:{off}"


class SegMap:
    """Listing segment <-> Ghidra segment, from segmap.tsv."""

    def __init__(self, rows: list[tuple[int, int, int]]):
        """rows: listing segment, Ghidra segment, bytes the segment holds from offset 0."""
        self.to_ghidra = {s: g for s, g, _ in rows}
        self.to_listing = {g: s for s, g, _ in rows}
        self.size = {g: n for _, g, n in rows}

    @classmethod
    def read(cls, path: Path) -> "SegMap":
        rows = []
        for line in path.read_text(encoding="utf-8").splitlines()[1:]:
            s, g, n = line.split("\t")
            rows.append((int(s, 16), int(g, 16), int(n)))
        return cls(rows)

    def listing_of(self, gseg: int, off: int) -> tuple[int, int] | None:
        """The listing SEGMENT, OFFSET of Ghidra gseg:off; None where GOAL.EXE holds no byte there."""
        seg = self.to_listing.get(gseg)
        if seg is None or off >= self.size[gseg]:
            return None
        return (seg, off)

    def listing_of_linear(self, linear: int) -> tuple[int, int] | None:
        """Ghidra prints some addresses as a linear offset: segment k*0x1000 holds k*0x10000.."""
        return self.listing_of((linear >> 4) & 0xF000, linear & 0xFFFF)


def rewrite(code: str, segmap: SegMap) -> str:
    """Ghidra's addresses in one function's C, in the listing's numbering."""
    ds = segmap.to_ghidra[DATA_SEGMENT]

    def named(m: re.Match) -> str:
        prefix, gseg, off = m.group(1), int(m.group(2), 16), int(m.group(3), 16)
        where = segmap.listing_of(gseg, off)
        if where is None:
            return f"ABS_{gseg * 16 + off:05X}" if prefix in ("DAT", "_DAT") else m.group(0)
        if gseg == ds and prefix in ("DAT", "_DAT"):
            return f"DS:{off:04X}"
        return f"{prefix}_{where[0]:04X}_{where[1]:04X}"

    def linear(m: re.Match) -> str:
        where = segmap.listing_of_linear(int(m.group(2), 16))
        if where is None:
            return m.group(0)
        if m.group(1) == "(ram,":
            return f"({where[0]:04X}:{where[1]:04X})"
        return f"{m.group(1).removesuffix('0x')}_{where[0]:04X}_{where[1]:04X}"

    code = re.sub(r"(?<![\w])(_?DAT|LAB|PTR)_([0-9a-f]{4})_([0-9a-f]{4})(?![\w])", named, code)
    code = re.sub(r"(func_0x|code_r0x|\(ram,0x)([0-9a-f]{8})(?=\W)", linear, code)
    return code


def parse_raw(text: str) -> list[Function]:
    functions: list[Function] = []
    for line in text.splitlines():
        m = HEADER.match(line)
        if m:
            functions.append(Function(m.group(1), m.group(2), m.group(3), m.group(4) == "ok",
                                      m.group(5) or "", ""))
        elif functions:
            functions[-1].code += line + "\n"
        elif line.strip():
            raise ValueError(f"text before the first function: {line!r}")
    return functions


def read_routines(path: Path) -> list[str]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(";") or line.startswith("segment:") or not line.strip():
            continue
        out.append(line.split("\t", 1)[0])
    return out


def render(functions: list[Function], routines: list[str], segmap: SegMap
           ) -> tuple[dict[str, str], list[list[str]]]:
    """The .c files (name -> text) and the rows of index.tsv."""
    known = set(routines)
    by_listing = {f.listing: f for f in functions}
    files: dict[str, list[str]] = {}
    where: dict[str, tuple[str, int]] = {}
    current: dict[int, tuple[str, int]] = {}  # segment -> (file name, its part number)
    for f in sorted(functions, key=lambda f: f.listing):
        if not f.ok:
            continue
        seg = int(f.listing.split(":")[0], 16)
        found = "routines.tsv" if f.listing in known else "Ghidra's analysis (not in routines.tsv)"
        block = (f"// ---- {f.listing}  {f.name}  (Ghidra {f.ghidra.upper()}, {f.convention}; "
                 f"found by {found})\n\n" + rewrite(f.code, segmap).strip("\n") + "\n\n\n")
        name, part = current.get(seg, (None, 0))
        if name is None or (len("".join(files[name]).encode()) + len(block.encode()) > MAX_FILE_BYTES
                            and len(files[name]) > 1):
            part += 1
            name = f"seg_{seg:04X}_{part:02d}.c"
            current[seg] = (name, part)
            files[name] = [file_header(seg, part, segmap)]
        line = "".join(files[name]).count("\n") + 1
        files[name].append(block)
        where[f.listing] = (name, line)
    rows = []
    for addr in sorted(set(routines) | set(by_listing)):
        f = by_listing.get(addr)
        source = "routines.tsv" if addr in known else "ghidra"
        if f is None:
            rows.append([addr, "missing", "", "", "", source, "Ghidra made no function here"])
        elif f.ok:
            name, line = where[addr]
            rows.append([addr, "decompiled", name, str(line), f.ghidra.upper(), source, ""])
        else:
            rows.append([addr, "failed", "", "", f.ghidra.upper(), source, f.error])
    return {n: "".join(parts).rstrip("\n") + "\n" for n, parts in files.items()}, rows


def file_header(seg: int, part: int, segmap: SegMap) -> str:
    table = ", ".join(f"{s:04X}={g:04X}" for s, g in sorted(segmap.to_ghidra.items()))
    return (f"// GOAL.EXE code segment {seg:04X}, part {part}: Ghidra's decompiler output, generated by "
            f"tools/static/decompile.sh (see README.md here; never edited by hand).\n"
            f"// Headings and names give listing addresses (SEGMENT:OFFSET, as in ../code/). DS:XXXX is the "
            f"data segment 2581. A segment number written in the code (a far pointer's segment, a far "
            f"call's) is Ghidra's: listing=Ghidra {table}.\n\n")


def readme(files: dict[str, str], rows: list[list[str]], summary: str, ghidra: str, jdk: str,
           segmap: SegMap) -> str:
    count = {}
    for r in rows:
        count[(r[1], r[5])] = count.get((r[1], r[5]), 0) + 1
    failed = [r for r in rows if r[1] != "decompiled"]
    lines = [
        "# static/goal-exe/decompiled/",
        "",
        "Generated, never edited by hand: `bash tools/static/decompile.sh <released GOAL.EXE> "
        "static/goal-exe/decompiled` rewrites every file here byte for byte.",
        "",
        "- Artifact: the released `GOAL.EXE` (packed sha256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`), "
        "unpacked by `tools/static/unlzexe.py` to sha256 `6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188` "
        "(checked by the tool; the unpacked file is never committed).",
        f"- Ghidra {ghidra}, JDK {jdk}, run headless with `-max-cpu 2`: the MZ loader, language "
        "`x86:LE:16:Real Mode` (compiler spec `default`), Ghidra's default auto-analysis options, "
        "the default decompiler options. Scripts: `tools/static/ghidra/GoalSetup.java` (before the "
        "analysis), `GoalDecompile.java` (after it); `tools/static/decompiled.py` writes these files.",
        "- One function per routine of `../routines.tsv`, named `f_SSSS_OOOO` after its listing address, "
        "near or far by whether it returns with RETF. Ghidra's analysis may add functions; they are "
        "named the same way and marked in `index.tsv`.",
        "",
        "## Addresses",
        "",
        "Every heading, function name and label gives the listing address `SEGMENT:OFFSET` of `../code/`. "
        "Ghidra holds listing segment k (ascending) at its segment k×0x1000, so that each segment starts "
        "on a 64K boundary; at the listing's own segment numbers Ghidra's x86 language computes "
        "near call and jump targets wrongly (`GoalSetup.java` says why). Each heading also gives the "
        "Ghidra address. The map:",
        "",
        "| listing | Ghidra |",
        "| --- | --- |",
    ]
    lines += [f"| {s:04X} | {g:04X} |" for s, g in sorted(segmap.to_ghidra.items())]
    lines += [
        "",
        "- `DS:9A3E` is offset 9A3E of the data segment 2581 (Ghidra's `DAT_b000_9a3e`, or "
        "`_DAT_b000_9a3e` for a wider access over smaller symbols).",
        "- A segment number written in the code (a pushed segment, a far pointer's segment) is "
        "Ghidra's, from the table above: `0xb000` is the data segment 2581.",
        "- A data address that Ghidra did not resolve stays a number, often signed: "
        "`*(char *)(i + -0x7f10)` is `DS:80F0 + i`.",
        "",
        "What the decompiled view can be trusted for, and what not, was checked against the hand-traced "
        "claims of F002–F007: `findings/F009-*.md`.",
        "",
        "## Counts",
        "",
        f"- Routines of `routines.tsv`: {len([r for r in rows if r[5] == 'routines.tsv'])}; "
        f"decompiled {count.get(('decompiled', 'routines.tsv'), 0)}, "
        f"failed {count.get(('failed', 'routines.tsv'), 0)}, "
        f"no function {count.get(('missing', 'routines.tsv'), 0)}.",
        f"- Functions Ghidra's analysis added (not in `routines.tsv`): "
        f"{len([r for r in rows if r[5] == 'ghidra'])}: "
        + ", ".join(f"`{r[0]}`" for r in rows if r[5] == "ghidra") + ".",
        "- Not decompiled:" + ("" if failed else " none."),
    ]
    lines += [f"  - `{r[0]}` ({r[1]}): {r[6]}" for r in failed]
    lines += ["- The scripts' own report: " + "; ".join(summary.strip().splitlines()) + ".", ""]
    lines += ["| File | What |", "| --- | --- |",
              "| `index.tsv` | per function: listing address, decompiled or not, file and line of its "
              "heading, Ghidra address, found in `routines.tsv` or by Ghidra, why it failed |"]
    for name in sorted(files):
        lines.append(f"| `{name}` | code segment {name[4:8]}, part {int(name[9:11])} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--segmap", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--routines", type=Path, required=True)
    ap.add_argument("--ghidra", required=True)
    ap.add_argument("--jdk", required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    segmap = SegMap.read(a.segmap)
    functions = parse_raw(a.raw.read_text(encoding="utf-8"))
    files, rows = render(functions, read_routines(a.routines), segmap)
    a.out.mkdir(parents=True, exist_ok=True)
    for old in list(a.out.glob("seg_*.c")) + [a.out / "index.tsv", a.out / "README.md"]:
        old.unlink(missing_ok=True)
    for name, text in files.items():
        (a.out / name).write_text(text, encoding="utf-8")
    index = ["address\tstatus\tfile\tline\tghidra_address\tfound_in\tnote"]
    index += ["\t".join(r) for r in rows]
    (a.out / "index.tsv").write_text("\n".join(index) + "\n", encoding="utf-8")
    (a.out / "README.md").write_text(
        readme(files, rows, a.summary.read_text(encoding="utf-8"), a.ghidra, a.jdk, segmap),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
