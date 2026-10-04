#!/usr/bin/env python3
"""Validate run records (`run/1`) and evidence manifests (`evidence-manifest/1`).

`python3 tools/validate_runs.py <dir|files...>` takes directories (their `*.json` files) or files,
and checks each with the validator `tools/ga.py` fetches at the pinned commit: the document is
loaded by the pinned loader (NaN/Infinity and a duplicate key are errors) and checked against the
schema its `schema` field names plus the rules no schema can express. Exit 0 when everything holds,
1 otherwise.

Adapted from diegoami/toy-archaeology tools/validate_runs.py at a3056ff.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402


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
        doc = ga.load_file(path)
    except (OSError, ValueError) as exc:
        return [f"{path}: invalid JSON: {exc}"]
    return [f"{path}: {error}" for error in ga.validate_document(doc)]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate run records (`run/1`) and evidence manifests (`evidence-manifest/1`)"
                    " with the pinned game-archaeologist validator: the schema plus the rules no"
                    " schema can express. Exit 0 when everything holds, 1 otherwise.")
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
