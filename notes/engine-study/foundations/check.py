#!/usr/bin/env python3
"""Source/document and byte-coverage integrity; not a semantic or match-fidelity proof."""
import argparse
import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = "08beac2e9d43faf766e445e924da096b8a99d748"
FILES = {
    "T96a": ("T96/fields.json", "player-fields.md"),
    "T96b": ("T96/derived.json", "player-derived.md"),
    "T97a": ("T97/persistent.json", "match-fields.md"),
    "T97b": ("T97/transient.json", "transient-state.md"),
    "T98a": ("T98/skill-v1.json", "attribute-formulas.md"),
    "T98b": ("T98/strength-v1.json", "strength-formulas.md"),
    "T99a": ("T99/gates-v1.json", "skill-gates.md"),
    "T99b": ("T99/contests-v1.json", "contest-formulas.md"),
    "T100": ("T100/flow.json", "match-flow.md"),
}
RECORDS = {"T96a": {"player": 20}, "T97a": {"country": 191, "fixture": 8, "manager-entry": 3},
           "T97b": {"pitch": 22, "ball": 12, "sprite": 8}}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def index():
    path = ROOT / "static/goal-exe/named/index.tsv"
    return {r["address"]: r for r in csv.DictReader(path.read_text().splitlines(), delimiter="\t")}


def pin(data, addresses, sources=()):
    """Bind a hand-written interpretation to unchanged original/evidence source locations."""
    ix, names, locations = index(), set(sources), []
    names.add("static/goal-exe/named/index.tsv")
    for address in sorted(set(addresses)):
        r = ix[address]
        if r["status"] != "decompiled":
            raise ValueError(f"explicit listing fallback needed: {address}")
        name, line = "static/goal-exe/named/" + r["file"], int(r["line"])
        text = (ROOT / name).read_text().splitlines()[line - 1]
        if address not in text:
            raise ValueError(f"index does not point at its heading: {address}")
        locations.append({"address": address, "file": name, "line": line, "heading_sha256": sha(text.encode())})
        names.add(name)
    hashes = {}
    for name in sorted(names):
        path = ROOT / name
        raw = path.read_bytes()
        original = subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)
        if raw != original:
            raise ValueError(f"source drift: {name}")
        hashes[name] = sha(raw)
    return {"schema": 1, "source_commit": BASE, **data, "locations": locations, "source_sha256": hashes}


def write_new(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        f.write(json.dumps(data, indent=2, sort_keys=True) + "\n")


def validate(task, data):
    if data.get("schema") != 1 or data.get("source_commit") != BASE or data.get("task") != task:
        raise ValueError("wrong task/schema/source baseline")
    doc = ROOT / "docs/engine-study" / FILES[task][1]
    text = doc.read_text()
    if len(text.split()) < 250:
        raise ValueError("chapter is absent or only a placeholder")
    if len(data.get("sections", [])) < 3:
        raise ValueError("missing chapter coverage checklist")
    for section in data["sections"]:
        if "## " + section not in text:
            raise ValueError(f"chapter section missing: {section}")
    if not data.get("locations") or not data.get("source_sha256"):
        raise ValueError("missing original source provenance")
    ix = index()
    for loc in data["locations"]:
        r = ix[loc["address"]]
        if loc["file"] != "static/goal-exe/named/" + r["file"] or loc["line"] != int(r["line"]):
            raise ValueError("original source index drift")
        line = (ROOT / loc["file"]).read_text().splitlines()[loc["line"] - 1]
        if sha(line.encode()) != loc["heading_sha256"]:
            raise ValueError("cited heading changed")
    for name, digest in data["source_sha256"].items():
        raw = (ROOT / name).read_bytes()
        if sha(raw) != digest:
            raise ValueError(f"source hash differs: {name}")
        if raw != subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT):
            raise ValueError(f"source differs from baseline: {name}")
    for name, size in RECORDS.get(task, {}).items():
        fields = data["records"][name]["fields"]
        cover = [k for f in fields for k in range(f["offset"], f["offset"] + f["width"])]
        if sorted(cover) != list(range(size)):
            raise ValueError(f"missing/overlapping byte coverage: {name}")
        if any(not f.get("name") or not f.get("meaning") for f in fields):
            raise ValueError(f"unexplained field: {name}")
    if task == "T96a" and len(data["records"]["player"]["fields"]) != 17:
        raise ValueError("player word/byte field census changed")
    if task == "T96b" and len(data.get("skills", [])) != 12:
        raise ValueError("missing displayed skill")
    if task == "T97b" and not {"clock", "score-statistics", "rng", "marking", "restart", "occupancy", "save-decisions"} <= set(data.get("state_groups", [])):
        raise ValueError("missing transient state family")
    if task in {"T98a", "T98b", "T99a", "T99b"} and not data.get("checks"):
        raise ValueError("missing numerical-check results; run the package checker too")
    if task == "T100" and not {"0791:F1F6", "0791:A4A1", "0791:F098", "0791:9564", "0791:D733", "0791:D47E", "0791:97D0", "0791:970C", "0791:B7FA"} <= {r["address"] for r in data["locations"]}:
        raise ValueError("missing main execution route")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task", choices=FILES, required=True)
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--receipt", type=Path)
    args = ap.parse_args()
    path = ROOT / "notes/engine-study" / FILES[args.task][0]
    data = json.loads(path.read_text())
    validate(args.task, data)
    results = {"positive": "accepted"}
    if args.controls:
        cases = ["missing-provenance", "shifted-source"]
        if args.task in RECORDS:
            cases += ["missing-field", "overlapping-field"]
        for case in cases:
            changed = copy.deepcopy(data)
            if case == "missing-provenance":
                changed["source_sha256"] = {}
            elif case == "shifted-source":
                changed["locations"][0]["line"] += 1
            else:
                fields = next(iter(changed["records"].values()))["fields"]
                if case == "missing-field":
                    fields.pop()
                else:
                    fields.append(copy.deepcopy(fields[0]))
            try:
                validate(args.task, changed)
            except (ValueError, KeyError):
                results[case] = "rejected"
            else:
                raise AssertionError(f"control escaped: {case}")
    receipt = {"task": args.task, "manifest_sha256": sha(path.read_bytes()),
               "checker_sha256": sha(Path(__file__).read_bytes()), "results": results}
    if args.receipt:
        write_new(args.receipt, receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
