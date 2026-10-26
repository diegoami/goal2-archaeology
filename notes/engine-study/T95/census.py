#!/usr/bin/env python3
"""Reproduce the source inventory without creating a Match or reading an original image."""
import argparse
import ast
import copy
import csv
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = "08beac2e9d43faf766e445e924da096b8a99d748"
REPORT = ROOT / "notes/engine-study/T95/census-08beac2e-v1.json"
CHAPTER = ROOT / "docs/engine-study/inventory.md"
sys.path.insert(0, str(ROOT / "runtime"))
from original_match.port import load  # noqa: E402

# Editorial routing, not a claim of measured reach or an evidence-level promotion.
ROUTES = {
    "attributes": ("T96,T98", "F007 F008 F010 F015 F018 F021 F028"),
    "ball": ("T102", "F022 F026"),
    "contests": ("T99,T102", "F022 F026"),
    "discipline": ("T104", "F018 F020 F024 F027 F029"),
    "display": ("T97,T100,T104", "F013 F014 F030"),
    "duels": ("T99,T102", "F015 F020 F022"),
    "frame": ("T100", "F005 F013 F014 F029 F030"),
    "geometry": ("T98,T99,T101", "F013 F015 F021 F022 F026"),
    "menus": ("T103,T104", "F026 F029 F030"),
    "motion": ("T101", "F013 F018 F028"),
    "pilot": ("T101", "F013"),
    "positioning": ("T101,T103", "F024 F026 F028"),
    "postmatch": ("T104", "F014 F018 F019 F020 F023 F029 F030"),
    "quick": ("T99,T100", "F005 F012 F021 F024 F027"),
    "rare": ("T100,T104", "F005 F024 F027 F030"),
    "restarts": ("T102,T104", "F013 F022 F027 F030"),
    "runtime": ("T99,T100", "F004 F012 F013"),
    "selection": ("T103,T104", "F024 F027 F029"),
    "setup": ("T97,T103,T104", "F010 F024 F027 F028 F029"),
    "takers": ("T99,T104", "F015 F023 F030"),
    "update": ("T104", "F018 F019 F020 F027"),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rel(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def tsv(path):
    return list(csv.DictReader((s for s in path.read_text().splitlines()
                                if not s.startswith(";")), delimiter="\t"))


def generate():
    sources = set()

    def source(path):
        path = ROOT / path
        sources.add(rel(path))
        return path

    named = {r["address"]: r for r in tsv(source("static/goal-exe/named/index.tsv"))}
    annotations = {r["address"]: r for r in tsv(source("static/goal-exe/annotations/routines.tsv"))}
    findings = {}
    for path in sorted(ROOT.glob("findings/F*.md")):
        text = source(path).read_text()
        status = next((s.split(":", 1)[1].strip() for s in text.splitlines()
                       if s.startswith("- **Status**:")), "not declared")
        findings[path.name.split("-", 1)[0]] = {"path": rel(path), "status": status}

    modules, routines = [], []
    for reg, _ in load(["all"]):
        chapters, evidence = ROUTES[reg.name]
        path = source(f"runtime/original_match/port/{reg.name}.py")
        modules.append({"module": reg.name, "entries": len(reg.entries),
                        "declared_stubs": sum(e.stub is not None for e in reg.entries.values()),
                        "variants": len(reg.variants), "chapters": chapters.split(","),
                        "findings": evidence.split(), "registry_source": rel(path)})
        for address, entry in sorted(reg.entries.items()):
            original = named[address]
            if original["status"] == "failed":
                # Retain the decompiler failure, and cite the available instruction listing.
                matches = []
                for asm in sorted(ROOT.glob(f"static/goal-exe/code/seg_{address[:4]}_*.asm")):
                    for number, text in enumerate(asm.read_text().splitlines(), 1):
                        if text.startswith("; ---- routine " + address + " "):
                            matches.append((asm, number))
                if len(matches) != 1:
                    raise ValueError(f"no unique listing fallback: {address}: {matches}")
                named_path, line = matches[0]
                named_path = source(named_path)
            else:
                named_path = source("static/goal-exe/named/" + original["file"])
                line = int(original["line"])
            if not 1 <= line <= len(named_path.read_text().splitlines()):
                raise ValueError(f"invalid named location: {address}")
            if entry.stub is not None:
                literals = [n.lineno for n in ast.walk(ast.parse(path.read_text()))
                            if isinstance(n, ast.Constant) and n.value == address]
                implementation = {"file": rel(path), "line": min(literals) if literals else None,
                                  "function": None}
            else:
                fn_path = source(inspect.getsourcefile(entry.fn))
                implementation = {"file": rel(fn_path),
                                  "line": inspect.getsourcelines(entry.fn)[1],
                                  "function": entry.name}
            routines.append({"address": address, "module": reg.name,
                             "kind": "declared-stub" if entry.stub is not None else "body",
                             "return": entry.ret, "stub_reason": entry.stub,
                             "implementation": implementation,
                             "original": {"file": rel(named_path), "line": line,
                                          "name": original["name"],
                                          "decompiler_status": original["status"],
                                          "confidence": original["confidence"],
                                          "basis": annotations.get(address, {}).get("basis", "")}})

    families = []
    for path in sorted(ROOT.glob("experiments/E036-match-port/families/*.json")):
        family = json.loads(source(path).read_text())
        reference = source(family["reference"])
        refs = [json.loads(s)["id"] for s in reference.read_text().splitlines() if s.strip()]
        ids = [m["id"] for m in family["matches"]]
        if len(set(ids)) != len(ids) or set(ids) - set(refs):
            raise ValueError(f"duplicate cases or missing declared references: {path}")
        families.append({"name": family["family"], "definition": rel(path),
                         "cases": len(ids), "ids": ids, "reference": rel(reference),
                         "reference_records": len(refs)})
    profile = json.loads(source("experiments/E036-match-port/families/display/profile.json").read_text())
    source(profile["reference"])
    source(profile["proof"])
    for pattern in ("runtime/original_match/**/*.py", "static/goal-exe/annotations/*.tsv",
                    "static/goal-exe/code/*.asm", "experiments/E036-match-port/families/*.py"):
        for path in sorted(ROOT.glob(pattern)):
            source(path)
    for name in ("routines.tsv", "calls.tsv", "datarefs.tsv"):
        source("static/goal-exe/" + name)

    hashes = {}
    for name in sorted(sources):
        data = (ROOT / name).read_bytes()
        pinned = subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)
        if data != pinned:
            raise ValueError(f"input drift from {BASE}: {name}")
        hashes[name] = digest(data)
    out = {"schema": 1, "source_commit": BASE,
           "generator_sha256": digest(Path(__file__).read_bytes()),
           "summary": {"modules": len(modules), "entries": len(routines),
                       "declared_stubs": sum(m["declared_stubs"] for m in modules),
                       "family_cases": sum(f["cases"] for f in families)},
           "modules": modules, "routines": sorted(routines, key=lambda r: r["address"]),
           "findings": findings, "families": families, "display_profile": profile,
           "source_sha256": hashes}
    if out["summary"] != {"modules": 21, "entries": 423, "declared_stubs": 17, "family_cases": 75}:
        raise ValueError(f"contract counts changed: {out['summary']}")
    return out


def validate(actual, expected):
    addresses = [r["address"] for r in actual["routines"]]
    if len(addresses) != 423 or len(set(addresses)) != len(addresses):
        raise ValueError("missing or duplicate registered routine")
    if sum(r["kind"] == "declared-stub" for r in actual["routines"]) != 17:
        raise ValueError("declared-stub classification changed")
    if actual != expected:
        raise ValueError("census differs from the pinned sources/registry")


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--controls", action="store_true")
    ap.add_argument("--receipt", type=Path)
    args = ap.parse_args()
    expected = generate()
    if args.write:
        write_new(REPORT, expected)
        print(f"wrote {rel(REPORT)}: {expected['summary']}")
        return
    actual = json.loads(REPORT.read_text())
    validate(actual, expected)
    if args.check:
        chapter = CHAPTER.read_text()
        for module in expected["modules"]:
            if f"| {module['module']} |" not in chapter:
                raise ValueError(f"chapter missing module: {module['module']}")
        print(f"PASS: {expected['summary']}; {len(expected['source_sha256'])} source hashes; all named locations and chapter routes")
        return
    results = {"positive": "accepted"}
    for name in ("missing-routine", "duplicate-address", "stub-as-body"):
        changed = copy.deepcopy(actual)
        if name == "missing-routine":
            changed["routines"].pop()
        elif name == "duplicate-address":
            changed["routines"][-1] = copy.deepcopy(changed["routines"][0])
        else:
            next(r for r in changed["routines"] if r["kind"] == "declared-stub")["kind"] = "body"
        try:
            validate(changed, expected)
        except ValueError as exc:
            results[name] = {"rejected": str(exc)}
        else:
            raise AssertionError(f"control escaped: {name}")
    receipt = {"source_commit": BASE, "generator_sha256": expected["generator_sha256"],
               "report_sha256": digest(REPORT.read_bytes()), "controls": results}
    if args.receipt:
        write_new(args.receipt, receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
