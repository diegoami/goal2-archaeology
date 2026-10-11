#!/usr/bin/env python3
"""Fetch game-archaeologist's pinned record tools at the commit `archaeology.json` pins.

The files land in `.cache/game-archaeologist/<commit>/` (git-ignored) with `gh api`; nothing is
copied into the repository. ADR-009 and formats/README.md ("The validator", "Verifying a bundle and
checking citations"): a game repository uses the pinned tools by fetching them, never by copying or
editing them.

The cache is only a cache of those fetched files. Before any file is used, every needed file must be
present and its git blob sha must equal the sha the pinned tree names: a partial cache is fetched
again, and a file whose bytes were changed is a named `GaError`, never silently re-downloaded. The
blob sha (sha1 of `blob <len>\\0<bytes>`) is the git object id the tree lists, not the sha256 of the
file's content.

`tools/validate_records.py` (stdlib only) is imported and its `validate`, `semantic_errors`,
`canonical_set_hash` and `unknown_keywords` are exposed here with their signatures unchanged; the
module finds the schemas in the `formats/` tree fetched beside it, so `validate_document` and
`load_file` run on the pinned schemas too. `tools/register_artifact.py` and the two new tools,
`tools/verify_evidence.py` and `tools/check_citations.py`, are fetched beside the validator for this
repository's thin wrappers to run; they are never imported here, so a wrapper and its tool stay two
processes.

Adapted from diegoami/toy-archaeology tools/ga.py at a3056ff (this repository is the second
consumer; game-archaeologist#10 extracted the shared tools).
"""
from __future__ import annotations

import base64
import binascii
import errno
import hashlib
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE = REPO_ROOT / ".cache" / "game-archaeologist"
ARCHAEOLOGY = REPO_ROOT / "archaeology.json"

# The pinned validator and the three tool wrappers this repository runs, plus the whole formats/
# tree (schemas, examples, expected-errors.json). The validator finds the schemas relative to its
# own path and the artifact tool imports the validator beside it, so the fetched layout must keep
# tools/ beside formats/.
NEEDED_FILES = (
    "tools/validate_records.py",
    "tools/register_artifact.py",
    "tools/verify_evidence.py",
    "tools/check_citations.py",
)
NEEDED_PREFIXES = ("formats/",)

VALIDATOR = NEEDED_FILES[0]
ARTIFACT_TOOL = NEEDED_FILES[1]
VERIFY_EVIDENCE = NEEDED_FILES[2]
CHECK_CITATIONS = NEEDED_FILES[3]

SCHEMA_FILES = {
    "run/1": "run-1.schema.json",
    "artifact-set/1": "artifact-set-1.schema.json",
    "variant/1": "variant-1.schema.json",
    "evidence-manifest/1": "evidence-manifest-1.schema.json",
}


class GaError(RuntimeError):
    """A named failure while fetching the pinned tools or checking the cache: never a traceback."""


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


def git_blob_sha(data: bytes) -> str:
    """The git blob sha1 of `data`, as the pinned tree names each file."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _gh_api(path: str):
    """The parsed JSON from one `gh api` call; a failure is a named `GaError`."""
    try:
        out = subprocess.run(["gh", "api", path], check=False, capture_output=True)
    except OSError as e:  # gh is not installed, or is not executable
        raise GaError(f"cannot run gh: {e.strerror or e}") from None
    if out.returncode != 0:
        message = out.stderr.decode("utf-8", "replace").strip()
        raise GaError(f"gh api {path} failed: {message or f'exit {out.returncode}'}") from None
    try:
        return json.loads(out.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise GaError(f"gh api {path}: invalid JSON: {e}") from None


def _wanted(repo: str, commit: str) -> dict[str, str]:
    """The pinned tree's needed blobs as {path: git blob sha}."""
    tree = _gh_api(f"repos/{repo}/git/trees/{commit}?recursive=1")
    wanted = {}
    for item in tree.get("tree", []):
        if item["type"] != "blob":
            continue
        path = item["path"]
        if path in NEEDED_FILES or path.startswith(NEEDED_PREFIXES):
            wanted[path] = item["sha"]
    return wanted


def _probe(path: Path, what: str) -> bool:
    """A filesystem probe (`is_file`, `is_symlink`) as a named `GaError`, never a traceback."""
    # `os.stat`, not `Path.is_file`: from Python 3.14 `is_file` and `is_symlink` return False on
    # any OSError, so an unreadable directory would pass for "missing" and trigger a refetch.
    try:
        if what == "file":
            return stat.S_ISREG(os.stat(path).st_mode)
        return stat.S_ISLNK(os.lstat(path).st_mode)
    except OSError as e:
        if e.errno in (errno.ENOENT, errno.ENOTDIR, errno.ELOOP):
            return False
        raise GaError(f"cannot stat {path}: {e.strerror or e}") from None


def _probe_tree(path: Path) -> None:
    """Every entry of a cached folder that exists, probed before any gh call: an unreadable folder
    or file under it is a named `GaError` (Luna's R1 on PR 122, round 1: an unreadable formats/
    was first probed after the tree request). A missing folder is not an error here."""
    try:
        mode = os.stat(path).st_mode
    except OSError as e:
        if e.errno in (errno.ENOENT, errno.ENOTDIR, errno.ELOOP):
            return
        raise GaError(f"cannot stat {path}: {e.strerror or e}") from None
    if not stat.S_ISDIR(mode):
        return
    try:
        entries = sorted(os.scandir(path), key=lambda entry: entry.name)
    except OSError as e:
        raise GaError(f"cannot stat {path}: {e.strerror or e}") from None
    for entry in entries:
        child = Path(entry.path)
        if _probe(child, "symlink") or _probe(child, "file"):
            continue
        _probe_tree(child)


def _missing(dest: Path, wanted: dict[str, str]) -> list[str]:
    """The needed files the cache does not hold; a non-empty list makes the cache untrusted."""
    return [path for path in sorted(wanted) if not _probe(dest / path, "file")]


def _download(repo: str, dest: Path, wanted: dict[str, str]) -> None:
    """Write every wanted blob into the cache; a filesystem failure is a named `GaError`."""
    for path, sha in sorted(wanted.items()):
        blob = _gh_api(f"repos/{repo}/git/blobs/{sha}")
        try:
            content = base64.b64decode(blob["content"])
        except (KeyError, ValueError, binascii.Error) as e:
            raise GaError(f"cannot decode blob {sha} for {path}: {e}") from None
        target = dest / path
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        except OSError as e:
            raise GaError(f"cannot write {target}: {e.strerror or e}") from None


def _check(dest: Path, wanted: dict[str, str]) -> None:
    """A named `GaError` unless every wanted file is present and holds its pinned bytes."""
    for path, sha in sorted(wanted.items()):
        target = dest / path
        if not _probe(target, "file"):
            raise GaError(f"{path}: missing from the pinned cache {dest}")
        try:
            content = target.read_bytes()
        except OSError as e:
            raise GaError(f"cannot read {target}: {e.strerror or e}") from None
        actual = git_blob_sha(content)
        if actual != sha:
            raise GaError(
                f"blob sha mismatch for {path}: cache has {actual}, pinned tree says {sha}")


def _drop_bytecode(dest: Path) -> None:
    """Delete every `__pycache__` under the cache, so only verified source can ever run.

    Python accepts a cached `.pyc` when the source's size and mtime match its header, and a
    same-length edit restored within the same second slips past that check: the verified source
    would be ignored for stale bytecode. Removing the bytecode closes that hole for the default
    location; bytecode redirected by `PYTHONPYCACHEPREFIX` lives outside the cache, so the wrappers
    launch the fetched tools with that variable cleared and with `-B`, and `validator()` compiles
    the verified source text itself instead of importing it. Nothing reads or writes bytecode for
    the cache."""
    try:
        pycaches = sorted(dest.rglob("__pycache__"))
        for pycache in pycaches:
            shutil.rmtree(pycache)
    except OSError as e:
        raise GaError(f"cannot remove bytecode under {dest}: {e.strerror or e}") from None


def fetch(commit: str | None = None) -> Path:
    """The pinned tools and formats/ tree in the cache for `commit`, fetched when incomplete.

    The pinned tree is read first: a cache missing any needed file is downloaded again, and then
    every file's git blob sha is checked against that tree before the cache is returned. An edited
    file is a named error, never silently replaced, so the caller never runs something that is not
    the pinned bytes (ADR-009)."""
    repo, pinned = pin()
    if commit is None:
        commit = pinned
    dest = root(commit)
    # The cache is a plain directory under the working tree. A symlinked cache root (or commit
    # folder) could point elsewhere, so it is refused by name rather than written through.
    if _probe(CACHE, "symlink"):
        raise GaError(f"cache root {CACHE} is a symlink, not a directory")
    if _probe(dest, "symlink"):
        raise GaError(f"cache for {commit} is a symlink: {dest}")
    # An unreadable cache is a named error before anything is asked of gh: probe the fixed tool
    # paths and everything already cached under formats/ first.
    for path in NEEDED_FILES:
        _probe(dest / path, "file")
    for prefix in NEEDED_PREFIXES:
        _probe_tree(dest / prefix)
    wanted = _wanted(repo, commit)
    if _missing(dest, wanted):
        _download(repo, dest, wanted)
    _drop_bytecode(dest)
    _check(dest, wanted)
    return dest


def run_tool(rel: str, argv: list[str]) -> int:
    """Run one fetched tool as a subprocess: `-B` (no bytecode), named launch errors, and the
    tool's own exit code, with death by signal re-raised in this process rather than mangled.

    The tool always runs from the caller's working directory, never from the cache folder that
    holds it, so it serves the repository it is run in. `PYTHONPYCACHEPREFIX` is cleared for the
    child: with it set, the tool's own `import validate_records` would read bytecode from that
    prefix, which `fetch()` cannot see or delete, instead of the verified source beside it."""
    tool = fetch() / rel
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPYCACHEPREFIX"}
    try:
        completed = subprocess.run([sys.executable, "-B", str(tool), *argv], env=env)
    except OSError as e:  # the interpreter or the tool cannot be launched
        raise GaError(f"cannot run {tool}: {e.strerror or e}") from None
    code = completed.returncode
    if code < 0:
        # The tool was killed by signal -code; sys.exit(code) would report 241 for SIGTERM, so
        # the same signal is re-raised here to preserve the termination as it happened.
        # SIGKILL (and SIGSTOP) refuse a new disposition with ValueError but are always fatal
        # by default, so the reset is attempted alone and the signal is delivered regardless.
        sig = -code
        try:
            signal.signal(sig, signal.SIG_DFL)
        except (OSError, ValueError):
            pass
        try:
            os.kill(os.getpid(), sig)
        except OSError:
            pass
        return 128 + sig
    return code


_validator = None


def validator():
    """The pinned validator module (`tools/validate_records.py`), loaded from verified source.

    The module is built from the source text `fetch()` has just verified: the bytes are compiled
    and executed here, never imported, so no `.pyc` is read (from `__pycache__` or from a
    `PYTHONPYCACHEPREFIX` / `sys.pycache_prefix` tree) and none is written."""
    global _validator
    if _validator is None:
        path = fetch() / VALIDATOR
        try:
            source = path.read_bytes()
        except OSError as e:
            raise GaError(f"cannot read {path}: {e.strerror or e}") from None
        module = types.ModuleType("ga_validate_records")
        module.__file__ = str(path)
        exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
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
