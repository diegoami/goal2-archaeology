#!/usr/bin/env python3
"""Print an `artifact-set/1` manifest of a directory, with the canonical id.

`python3 tools/register_artifact.py <dir> --label <label> --title <title> --version <version>
--how <how>` hashes every file under `<dir>` and prints the manifest `artifacts/known.json` holds,
its `id` being `<label>-<first 8 hex of the canonical manifest's sha256>` (formats/README.md).

`--how` is the acquisition kind (`generated`, `purchased download`, `user-supplied install`,
`archive item <name>`); `--when` defaults to today.

Adapted from diegoami/toy-archaeology tools/register_artifact.py at a3056ff.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402


def file_entries(directory: Path) -> list[dict]:
    entries = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        data = path.read_bytes()
        entries.append({
            "path": path.relative_to(directory).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return entries


def manifest_of(directory: Path, label: str, title: str, version: str, how: str,
                when: str, note: str | None, writes: list[str]) -> dict:
    acquired = {"how": how, "when": when}
    if note:
        acquired["note"] = note
    body = {
        "schema": "artifact-set/1",
        "title": title,
        "version": version,
        "acquired": acquired,
        "files": file_entries(directory),
        "runtime_writes": writes,
    }
    body["id"] = f"{label}-{ga.canonical_set_hash(body)[:8]}"
    return body


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dir", type=Path)
    parser.add_argument("--label", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--how", required=True)
    parser.add_argument("--when", default=datetime.date.today().isoformat())
    parser.add_argument("--note")
    parser.add_argument("--writes", action="append", default=[],
                        help="a glob of files the runtime creates or changes; repeatable")
    args = parser.parse_args(argv)
    if not args.dir.is_dir():
        print(f"{args.dir}: not a directory", file=sys.stderr)
        return 1
    manifest = manifest_of(args.dir, args.label, args.title, args.version, args.how,
                           args.when, args.note, args.writes)
    # Schema only: the one semantic rule for artifact-set/1 (the id's hash suffix) holds by
    # construction, since manifest_of computes the id with the checker's own canonical_set_hash.
    problems = ga.validate(manifest, ga.schema("artifact-set/1"))
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
