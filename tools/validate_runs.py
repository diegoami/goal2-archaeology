#!/usr/bin/env python3
"""Validate run records (`run/1`) and evidence manifests (`evidence-manifest/1`).

`python3 tools/validate_runs.py <dir|files...>` takes directories (their `*.json` files) or files,
and checks each against the pinned game-archaeologist schema plus the rules no schema can express,
with the checker `tools/ga.py` fetches. Exit 0 when everything holds, 1 otherwise.

Adapted from diegoami/toy-archaeology tools/validate_runs.py at a3056ff.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402

VALID_SCHEMAS = set(ga.SCHEMA_FILES)


def documents(paths) -> list[Path]:
    found = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            found += sorted(path.glob("*.json"))
        elif path.is_file():
            found.append(path)
        else:
            found.append(path)  # reported as missing by the caller
    return found


def check(path: Path) -> list[str]:
    if not path.is_file():
        return [f"{path}: no such file or directory"]
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{path}: invalid JSON: {exc}"]
    schema_id = doc.get("schema")
    if schema_id not in VALID_SCHEMAS:
        return [f"{path}: unknown schema {schema_id!r}"]
    schema = ga.schema(schema_id)
    return [f"{path}: {error}" for error in
            ga.validate(doc, schema) + ga.semantic_errors(schema_id, doc)]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate run records (`run/1`) and evidence manifests (`evidence-manifest/1`)"
                    " against the pinned game-archaeologist schema plus the rules no schema can"
                    " express. Exit 0 when everything holds, 1 otherwise.")
    parser.add_argument("paths", nargs="+", metavar="DIR|FILE",
                        help="a directory (its *.json files) or a JSON document")
    args = parser.parse_args(argv)
    paths = documents(args.paths)
    problems = []
    for path in paths:
        problems += check(path)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"ok: {len(paths)} document(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
