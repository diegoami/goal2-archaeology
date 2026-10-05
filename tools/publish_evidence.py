#!/usr/bin/env python3
"""Publish a run's evidence files to the experiment's release, by hash (ADR-008).

`python3 tools/publish_evidence.py E<nnn> --run <run_id> --file <path> [--file …]` computes each
file's sha256, uploads it to release `E<nnn>` as `<sha256[:16]>-<name>` (creating the release when
missing) and only then writes `evidence/E<nnn>/<run_id>.manifest.json` (`evidence-manifest/1`, the
`artifact` taken from the run record): the manifest never names an asset that was not uploaded and
verified by downloading it back. An asset already on the release under that name is not uploaded
again: it is downloaded and its sha256 checked, and a different content stops the tool — releases
are shared state, an asset is never deleted or replaced. A manifest already present with other
content stops the tool before anything touches the release; the same content is left as it is, so
re-running the command changes nothing.

A published file is class `save` (the tool publishes start states: a DOSBox-X savestate holds the
game's memory, so it is an asset of this private repository only, never of the tree).

Exit 0 when the bundle is published (or was already), 1 otherwise.

Companion to tools/verify_evidence.py, which re-checks the manifests against the release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "diegoami/goal2-archaeology"
SCHEMA = "evidence-manifest/1"
# The tool publishes start states, and a start state is a savestate: class save
# (evidence-manifest/1). A config, log or screenshot is not a start state and is not published here.
CLASS = "save"

RELEASE_NOTES = (
    "Evidence bundles of this experiment (ADR-008): the start states its run records name by"
    " sha256, one asset per file, named `<sha256[:16]>-<name>`, indexed by"
    " evidence/E<nnn>/*.manifest.json and re-verified by `tools/verify_evidence.py`.\n\n"
    "A savestate holds the game's memory: these are assets of this private repository only, never"
    " of the tree. Assets are never deleted or replaced; a conflicting upload stops"
    " tools/publish_evidence.py."
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gh(args: list[str], repo: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args, "--repo", repo], check=False, capture_output=True,
                          text=True)


def release_assets(release: str, repo: str) -> list[str] | None:
    """Every asset name of the release, from one `gh release view` listing; None when missing."""
    out = gh(["release", "view", release, "--json", "assets", "-q", ".assets[].name"], repo)
    return out.stdout.splitlines() if out.returncode == 0 else None


def create_release(release: str, repo: str) -> subprocess.CompletedProcess:
    return gh(["release", "create", release, "--title", f"{release} evidence bundles",
               "--notes", RELEASE_NOTES.replace("E<nnn>", release)], repo)


def download_asset(asset: str, release: str, repo: str, cache: Path) -> bool:
    """Download one asset into the cache; only a file this run's `gh release download` produced
    counts, so a stale copy cannot stand in for a download that failed or produced nothing."""
    destination = cache / asset
    destination.unlink(missing_ok=True)
    result = gh(["release", "download", release, "-p", asset, "-D", str(cache), "--clobber"], repo)
    return result.returncode == 0 and destination.is_file()


def check_or_upload(entry: dict, release: str, repo: str, names: list[str], cache: Path,
                    staging: Path, uploaded: dict) -> str | None:
    """Make `entry`'s asset hold exactly this file's bytes, without ever replacing one.

    An asset already on the release is downloaded and checked by sha256: the same content is kept
    (no second upload), another content is a conflict and stops the tool. A missing asset is
    uploaded from a staged copy named `<sha256[:16]>-<name>` — `gh release upload` takes the asset
    name from the file name — and then verified by downloading it back."""
    asset, path = entry["asset"], entry["path"]
    if asset in names:
        if not download_asset(asset, release, repo, cache):
            return f"{asset}: download from release {release} failed"
        actual = sha256_file(cache / asset)
        if actual != entry["sha256"]:
            return (f"{asset}: already on release {release} with sha256 {actual},"
                    f" this file's is {entry['sha256']}; not replacing it")
        return None
    staged = staging / asset
    staged.unlink(missing_ok=True)
    shutil.copyfile(path, staged)
    result = gh(["release", "upload", release, str(staged)], repo)
    if result.returncode != 0:
        return f"{asset}: upload failed: {result.stderr.strip()}"
    if not download_asset(asset, release, repo, cache):
        return f"{asset}: download-after-upload from release {release} failed"
    actual = sha256_file(cache / asset)
    if actual != entry["sha256"]:
        return (f"{asset}: on release {release} after upload with sha256 {actual},"
                f" expected {entry['sha256']}")
    uploaded[asset] = True
    return None


def manifest_document(experiment: str, run_id: str, artifact: dict, entries: list[dict]) -> dict:
    return {
        "schema": SCHEMA,
        "run_id": run_id,
        "experiment": experiment,
        "store": f"release:{experiment}",
        "artifact": artifact,
        "files": [{key: entry[key] for key in ("name", "bytes", "sha256", "asset", "class")}
                  for entry in entries],
    }


def publish(experiment: str, run_id: str, files: list[Path], evidence_dir: Path, runs_dir: Path,
            repo: str) -> list[str]:
    """Publish the files as run_id's bundle; return the problems (empty when it published)."""
    record_path = runs_dir / experiment / f"{run_id}.json"
    if not record_path.is_file():
        return [f"{record_path}: no run record for {run_id} (--runs-dir {runs_dir})"]
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{record_path}: invalid JSON: {exc}"]
    artifact = record.get("artifact")
    if not isinstance(artifact, dict) or "set" not in artifact or "variant" not in artifact:
        return [f"{record_path}: no artifact set/variant to put in the manifest"]

    entries = []
    for path in files:
        if not path.is_file():
            return [f"{path}: no such file"]
        digest = sha256_file(path)
        entries.append({"name": path.name, "bytes": path.stat().st_size, "sha256": digest,
                        "asset": f"{digest[:16]}-{path.name}", "class": CLASS, "path": path})

    # A manifest already present with other content stops here, before the release is touched;
    # the same content is left as written, so a re-run changes nothing.
    manifest_path = evidence_dir / experiment / f"{run_id}.manifest.json"
    new = manifest_document(experiment, run_id, artifact, entries)
    if manifest_path.is_file():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        except ValueError as exc:
            return [f"{manifest_path}: existing manifest is invalid JSON: {exc}"]
        if existing != new:
            return [f"{manifest_path}: exists with other content; not overwriting it"]
    else:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

    names = release_assets(experiment, repo)
    if names is None:
        result = create_release(experiment, repo)
        if result.returncode != 0:
            return [f"release {experiment}: create failed: {result.stderr.strip()}"]
        names = release_assets(experiment, repo)
        if names is None:
            return [f"release {experiment}: still missing after create"]

    problems = []
    uploaded: dict = {}
    with tempfile.TemporaryDirectory() as tmp:
        cache, staging = Path(tmp) / "cache", Path(tmp) / "staging"
        cache.mkdir()
        staging.mkdir()
        for entry in entries:
            problem = check_or_upload(entry, experiment, repo, names, cache, staging, uploaded)
            if problem:
                problems.append(problem)
    if problems:
        return problems

    # The manifest is written only after every asset is on the release and verified (hazard:
    # a manifest whose asset was not uploaded). An equal manifest is not rewritten.
    if not manifest_path.is_file():
        manifest_path.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")
        print(f"{manifest_path}: written")
    else:
        print(f"{manifest_path}: already as published")
    for entry in entries:
        state = "uploaded" if entry["asset"] in uploaded else "already on the release, same sha256"
        print(f"{entry['asset']}: {state}")
    return []


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", help="experiment id, e.g. E005")
    parser.add_argument("--run", required=True, metavar="RUN_ID",
                        help="run id the bundle belongs to, e.g. E005-r0010; its record under"
                             " --runs-dir gives the manifest's artifact")
    parser.add_argument("--file", required=True, action="append", type=Path, metavar="PATH",
                        dest="files", help="a file to publish (repeatable)")
    parser.add_argument("--evidence-dir", type=Path, default=REPO_ROOT / "evidence")
    parser.add_argument("--runs-dir", type=Path, default=REPO_ROOT / "runs")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args(argv)

    problems = publish(args.experiment, args.run, args.files, args.evidence_dir, args.runs_dir,
                       args.repo)
    if problems:
        print("\n".join(problems))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
