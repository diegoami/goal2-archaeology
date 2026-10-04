#!/usr/bin/env python3
"""Fetch game-archaeologist's record-format checker at the commit `archaeology.json` pins.

The files land in `.cache/game-archaeologist/<commit>/` (git-ignored) with `gh api`; nothing is
copied into the repository. game-archaeologist#10: a game repository uses the pinned checker by
fetching it, never by copying and editing it.

The checker (`tests/formats/check_examples.py`, stdlib only) is imported and its `validate`,
`semantic_errors` and `canonical_set_hash` are exposed here for the record tools.

Adapted from diegoami/toy-archaeology tools/ga.py at a3056ff (this repository is the second
consumer; game-archaeologist#10 will extract the shared tool).
"""
from __future__ import annotations

import base64
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE = REPO_ROOT / ".cache" / "game-archaeologist"
ARCHAEOLOGY = REPO_ROOT / "archaeology.json"

# The checker itself, plus the whole formats/ tree (schemas, examples, expected-errors.json).
NEEDED_FILES = ("tests/formats/check_examples.py",)
NEEDED_PREFIXES = ("formats/",)

SCHEMA_FILES = {
    "run/1": "run-1.schema.json",
    "artifact-set/1": "artifact-set-1.schema.json",
    "variant/1": "variant-1.schema.json",
    "evidence-manifest/1": "evidence-manifest-1.schema.json",
}


def pin() -> tuple[str, str]:
    """The (repo, commit) `archaeology.json` pins."""
    cfg = json.loads(ARCHAEOLOGY.read_text(encoding="utf-8"))
    ga = cfg["game-archaeologist"]
    return ga["repo"], ga["commit"]


def root(commit: str | None = None) -> Path:
    """The cache directory for this commit's copy."""
    if commit is None:
        commit = pin()[1]
    return CACHE / commit


def _gh_api(path: str):
    out = subprocess.run(["gh", "api", path], check=True, capture_output=True)
    return json.loads(out.stdout.decode("utf-8"))


def fetch(commit: str | None = None) -> Path:
    """Download the checker and the formats/ tree into the cache, once; return its root."""
    repo, pinned = pin()
    if commit is None:
        commit = pinned
    dest = root(commit)
    if (dest / NEEDED_FILES[0]).exists():
        return dest
    tree = _gh_api(f"repos/{repo}/git/trees/{commit}?recursive=1")
    wanted = {}
    for item in tree.get("tree", []):
        if item["type"] != "blob":
            continue
        path = item["path"]
        if path in NEEDED_FILES or path.startswith(NEEDED_PREFIXES):
            wanted[path] = item["sha"]
    for path, sha in sorted(wanted.items()):
        blob = _gh_api(f"repos/{repo}/git/blobs/{sha}")
        target = dest / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(blob["content"]))
    return dest


_checker = None


def checker():
    """The imported checker module, at the pinned commit."""
    global _checker
    if _checker is None:
        path = fetch() / NEEDED_FILES[0]
        spec = importlib.util.spec_from_file_location("ga_check_examples", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _checker = module
    return _checker


def validate(value, schema, path: str = "$"):
    """Errors for `value` against `schema`, as `path: message` strings (the checker's own)."""
    return checker().validate(value, schema, path)


def semantic_errors(schema_id, doc):
    """The rules no schema can express, as checked on the examples (the checker's own)."""
    return checker().semantic_errors(schema_id, doc)


def canonical_set_hash(manifest):
    """sha256 of the canonical manifest: without id and acquired, files sorted by path."""
    return checker().canonical_set_hash(manifest)


def schema(schema_id: str):
    """The parsed schema for a format id such as `run/1`."""
    name = SCHEMA_FILES[schema_id]
    return json.loads((fetch() / "formats" / name).read_text(encoding="utf-8"))


def example(relative: str) -> Path:
    """A fetched formats/examples file, e.g. `valid/run-1--seeded-crafted-state.json`."""
    return fetch() / "formats" / "examples" / relative


if __name__ == "__main__":
    print(fetch())
    sys.exit(0)
