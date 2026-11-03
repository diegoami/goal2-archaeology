"""T118 (#427): check a write-set table against the raw listings.

    python3 notes/427/writeset/check.py [table.json ...]     # default: writeset.json beside this file
    python3 notes/427/writeset/check.py --list 000E:6CA7     # every store and call of a routine, to author rows

A table names routines (its scope) and rows. In each scoped routine, every instruction that writes memory
(a memory destination, a string store, a pop to memory) and every call must be the site of exactly one row,
at the listing line the row names. A row says what the site writes or calls, its class, the phase of
route_fixture it belongs to and the path condition. A port-owned call names an address the port registers
(`@PORTS.port("<address>"` under runtime/original_match/port/). The listing decides (named/README.md).
"""
import functools
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODE = ROOT / "static" / "goal-exe" / "code"
PORT = ROOT / "runtime" / "original_match" / "port"
HERE = Path(__file__).resolve().parent

INSN = re.compile(r"^([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s*([a-z]+)(?: (.*))?$")
ROUTINE = re.compile(r"^; ---- routine ([0-9A-F]{4}:[0-9A-F]{4}) ")
# Instructions whose first operand is their destination; a memory operand there is a write.
DEST_FIRST = {"mov", "add", "adc", "sub", "sbb", "and", "or", "xor", "inc", "dec", "neg", "not",
              "shl", "shr", "sar", "sal", "rol", "ror", "rcl", "rcr", "pop", "xchg",
              "seta", "setb", "sete", "setne"}
STRING_STORES = re.compile(r"^(rep[a-z]* )?(stos|movs)[bwd]?$")
CLASSES = {"frame", "game", "countries", "managers", "fixtures", "players", "ds-global", "screen",
           "rng", "pure", "port-owned", "subtree", "prompt"}
PHASES = {"pre-match", "route", "watch-prompt", "run_match", "confidence", "news", "player_update",
          "cursor", "group_tables", "silent", "unplayed", "6685"}
FIELDS = ("site", "line", "op", "class", "phase", "target", "condition", "evidence")


@functools.lru_cache(maxsize=None)
def listing_of(routine):
    """(file, first line, last line) of a routine in the raw listings: from its header to the next one."""
    for path in sorted(CODE.glob(f"seg_{routine[:4]}_*.asm")):
        lines = path.read_text().splitlines()
        for i, text in enumerate(lines):
            m = ROUTINE.match(text)
            if m and m.group(1) == routine:
                end = next((j for j in range(i + 1, len(lines)) if ROUTINE.match(lines[j])), len(lines))
                return path, i + 1, end
    raise ValueError(f"routine {routine} is not in the listings")


@functools.lru_cache(maxsize=None)
def sites(routine):
    """Every write and call of a routine: {site: (line number, op, text)}."""
    path, first, last = listing_of(routine)
    seg = routine[:4]
    out = {}
    for n, text in enumerate(path.read_text().splitlines()[first - 1:last], start=first):
        m = INSN.match(text)
        if not m:
            continue
        addr, mnem, ops = m.group(1), m.group(2), (m.group(3) or "")
        if mnem in ("rep", "repe", "repne") and ops:
            mnem = f"{mnem} {ops.split()[0]}"
            ops = ""
        op = None
        if mnem == "call":
            op = "call"
        elif STRING_STORES.match(mnem):
            op = "store"
        elif mnem in DEST_FIRST and "[" in ops.split(",")[0]:
            op = "store"
        elif mnem == "xchg" and "[" in ops:
            op = "store"
        if op:
            out[f"{seg}:{addr}"] = (n, op, text.strip())
    return out


def callee(routine, text):
    """The target of a call line: 'SEG:OFF' for a far call, the routine's own segment for a near one."""
    m = re.search(r"call far ([0-9A-F]{4}:[0-9A-F]{4})", text)
    if m:
        return m.group(1)
    m = re.search(r"call 0x([0-9a-f]+)$", text)
    return f"{routine[:4]}:{int(m.group(1), 16):04X}" if m else None


@functools.lru_cache(maxsize=None)
def ported():
    found = set()
    for path in PORT.glob("*.py"):
        found.update(re.findall(r'@PORTS\.port\("([0-9A-F]{4}:[0-9A-F]{4})"', path.read_text()))
    return found


def check(table):
    """The problems of one table, as a list of strings (empty: the table is complete and consistent)."""
    problems = []
    scope = table["scope"]
    rows = table["rows"]
    port = ported()
    by_site = {}
    for row in rows:
        missing = [f for f in FIELDS if f not in row or row[f] in ("", None)]
        if missing:
            problems.append(f"row {row.get('site')}: missing {missing}")
            continue
        if row["class"] not in CLASSES:
            problems.append(f"row {row['site']}: class {row['class']!r}")
        if row["phase"] not in PHASES:
            problems.append(f"row {row['site']}: phase {row['phase']!r}")
        by_site.setdefault(row["site"], []).append(row)
    for site, same in by_site.items():
        if len(same) > 1:
            problems.append(f"site {site}: {len(same)} rows")
    covered = set()
    for routine in scope:
        found = sites(routine)
        for site, (line, op, text) in found.items():
            covered.add(site)
            same = by_site.get(site)
            if not same:
                problems.append(f"{routine}: {op} at {site} (line {line}) has no row: {text}")
                continue
            row = same[0]
            if row["line"] != line:
                problems.append(f"row {site}: line {row['line']}, the listing has it at {line}")
            if row["op"] != op:
                problems.append(f"row {site}: op {row['op']}, the listing has a {op}")
            if op == "call":
                target = callee(routine, text)
                if row.get("callee") != target:
                    problems.append(f"row {site}: callee {row.get('callee')}, the listing calls {target}")
                if row["class"] == "port-owned" and target not in port:
                    problems.append(f"row {site}: {target} is not a registered port")
    for site in by_site:
        if site not in covered:
            problems.append(f"row {site}: not a write or call of a scoped routine")
    for rule in table.get("rules", ()):
        name = rule.get("name")
        if not name or not rule.get("rule"):
            problems.append(f"rule {name!r}: missing its name or text")
            continue
        cited = re.findall(r"(seg_[0-9A-F]{4}_\d+\.asm):(\d+)", rule.get("evidence", ""))
        if not cited:
            problems.append(f"rule {name!r}: cites no listing line")
        for file, line in cited:
            path = CODE / file
            if not path.exists() or int(line) > len(path.read_text().splitlines()):
                problems.append(f"rule {name!r}: {file}:{line} is not a listing line")
    return problems


def main(argv):
    if argv[:1] == ["--list"]:
        for routine in argv[1:]:
            for site, (line, op, text) in sorted(sites(routine).items(), key=lambda kv: kv[1][0]):
                print(f"{site}\t{line}\t{op}\t{text}")
        return 0
    paths = [Path(a) for a in argv] or [HERE / "writeset.json"]
    bad = 0
    for path in paths:
        problems = check(json.loads(path.read_text()))
        for p in problems:
            print(f"{path.name}: {p}")
        bad += len(problems)
        print(f"{path.name}: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
