#!/usr/bin/env python3
"""Fetch game-archaeologist's pinned record tools at the commit `archaeology.json` pins.

The files land in `.cache/game-archaeologist/<commit>/` (git-ignored) with `gh api`; nothing is
copied into the repository. ADR-009 and formats/README.md ("The validator"): a game repository uses
the pinned validator and artifact tool by fetching them, never by copying or editing them.

`tools/validate_records.py` (stdlib only) is imported and its `validate`, `semantic_errors`,
`canonical_set_hash` and `unknown_keywords` are exposed here with their signatures unchanged; the
module finds the schemas in the `formats/` tree fetched beside it, so `validate_document` and
`load_file` run on the pinned schemas too. `tools/register_artifact.py` is fetched beside the
validator for the repository's thin wrapper `tools/register_artifact.py` to run; it is never
imported here, so the wrapper and the tool stay two processes.

Adapted from diegoami/toy-archaeology tools/ga.py at a3056ff (this repository is the second
consumer; game-archaeologist#10 extracted the shared tools).
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

# The pinned validator and artifact tool, plus the whole formats/ tree (schemas, examples,
# expected-errors.json). The validator finds the schemas relative to its own path and the artifact
# tool imports the validator beside it, so the fetched layout must keep tools/ beside formats/.
NEEDED_FILES = ("tools/validate_records.py", "tools/register_artifact.py")
NEEDED_PREFIXES = ("formats/",)

VALIDATOR = NEEDED_FILES[0]
ARTIFACT_TOOL = NEEDED_FILES[1]

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
    """Download the pinned tools and the formats/ tree into the cache, once; return its root."""
    repo, pinned = pin()
    if commit is None:
        commit = pinned
    dest = root(commit)
    if (dest / VALIDATOR).exists():
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


_validator = None


def validator():
    """The imported pinned validator module (`tools/validate_records.py`)."""
    global _validator
    if _validator is None:
        path = fetch() / VALIDATOR
        spec = importlib.util.spec_from_file_location("ga_validate_records", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _validator = module
    return _validator


def validate(value, schema, path: str = "$"):
    """Errors for `value` against `schema`, as `path: message` strings (the validator's own)."""
    return validator().validate(value, schema, path)


def semantic_errors(schema_id, doc):
    """The rules no schema can express, as checked on the examples (the validator's own)."""
    return validator().semantic_errors(schema_id, doc)


def canonical_set_hash(manifest):
    """sha256 of the canonical manifest: without id and acquired, files sorted by path."""
    return validator().canonical_set_hash(manifest)


def unknown_keywords(schema):
    """Keywords the pinned validator does not implement, anywhere in the schema."""
    return validator().unknown_keywords(schema)


def validate_document(doc):
    """Errors for one parsed record document, as `path: message` strings (the validator's own)."""
    return validator().validate_document(doc)


def load_file(path):
    """The parsed document at `path`, by the pinned loader (NaN/Infinity, a duplicate key, and a
    lone surrogate's missing canonical form are value or key errors, never silently read)."""
    return validator().load_file(path)


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
