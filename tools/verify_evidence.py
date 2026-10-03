#!/usr/bin/env python3
"""Verify an experiment's evidence bundle.

`python3 tools/verify_evidence.py E<nnn>` reads `evidence/E<nnn>/*.manifest.json` and checks every
listed file against release `E<nnn>`: its asset name (`<sha256[:16]>-<name>`) and its sha256. With
`--local <dir>` it checks a directory instead of the release (the bundle already downloaded).

The release is listed once and each distinct asset is downloaded once, however many manifests share
it (toy-archaeology#11). A missing asset is reported by name, and a download that fails or leaves no
file is retried once before it is reported. A file already in the cache is never accepted in place
of this run's download: it is removed before each attempt, so a stale copy cannot stand in for a
download that fails or silently produces nothing.

Exit 0 when every file matches, 1 otherwise. `--evidence-dir` overrides where the manifests live.

Adapted from diegoami/toy-archaeology tools/verify_evidence.py at a3056ff: the repository is
`diegoami/goal2-archaeology`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "diegoami/goal2-archaeology"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_asset(entry: dict) -> str:
    return f"{entry.get('sha256', '')[:16]}-{entry.get('name', '')}"


def check_local(manifest: dict, local: Path) -> list[str]:
    problems = []
    for entry in manifest.get("files", []):
        asset = expected_asset(entry)
        path = local / asset
        if not path.is_file():
            problems.append(f"{asset}: missing from {local}")
            continue
        actual = sha256_file(path)
        if actual != entry.get("sha256"):
            problems.append(f"{asset}: sha256 {actual}, manifest says {entry.get('sha256')}")
    return problems


def release_assets(release: str, repo: str) -> list[str]:
    """Every asset name of the release, from one `gh release view` listing."""
    out = subprocess.run(
        ["gh", "release", "view", release, "--repo", repo, "--json", "assets", "-q", ".assets[].name"],
        check=True, capture_output=True, text=True)
    return [name for name in out.stdout.splitlines() if name]


def download_asset(asset: str, release: str, repo: str, cache: Path) -> bool:
    """Download one asset into the cache, retrying once when it fails or leaves no file.

    A file already in the cache is not a result: it is removed before each attempt, so only a file
    this run's `gh release download` produced and returned 0 for counts (toy-archaeology#11)."""
    destination = cache / asset
    for _ in range(2):
        destination.unlink(missing_ok=True)
        result = subprocess.run(
            ["gh", "release", "download", release, "--repo", repo, "-p", asset, "-D", str(cache),
             "--clobber"],
            check=False, capture_output=True)
        if result.returncode == 0 and destination.is_file():
            return True
    return False


def check_release(manifests: list[tuple[str, dict]], release: str, repo: str,
                  cache: Path) -> list[str]:
    """Problems for every manifest against the release, one listing and one download per asset.

    `manifests` is a list of (manifest file name, parsed manifest) pairs."""
    problems = []
    assets = release_assets(release, repo)
    cache.mkdir(parents=True, exist_ok=True)
    wanted = []
    distinct = {}
    for name, manifest in manifests:
        for entry in manifest.get("files", []):
            asset = expected_asset(entry)
            wanted.append((name, asset, entry.get("sha256")))
            distinct.setdefault(asset, entry.get("sha256"))
    downloaded = {}
    for asset in sorted(distinct):
        if asset in assets:
            downloaded[asset] = download_asset(asset, release, repo, cache)
    for name, asset, sha in wanted:
        if asset not in assets:
            problems.append(f"{name}: {asset}: not an asset of release {release}")
            continue
        if not downloaded.get(asset):
            problems.append(f"{name}: {asset}: download failed from release {release}")
            continue
        path = cache / asset
        if not path.is_file():
            problems.append(f"{name}: {asset}: missing after download from release {release}")
            continue
        actual = sha256_file(path)
        if actual != sha:
            problems.append(f"{name}: {asset}: sha256 {actual}, manifest says {sha}")
    return problems


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", help="experiment id, e.g. E001")
    parser.add_argument("--local", type=Path, help="check this directory instead of the release")
    parser.add_argument("--evidence-dir", type=Path, default=REPO_ROOT / "evidence")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args(argv)

    manifests = sorted((args.evidence_dir / args.experiment).glob("*.manifest.json"))
    if not manifests:
        print(f"no manifest under {args.evidence_dir / args.experiment}")
        return 1

    loaded = [(path.name, json.loads(path.read_text(encoding="utf-8"))) for path in manifests]
    problems = []
    if args.local is not None:
        for name, manifest in loaded:
            problems += [f"{name}: {p}" for p in check_local(manifest, args.local)]
    else:
        problems = check_release(
            loaded, args.experiment, args.repo,
            REPO_ROOT / ".cache" / "evidence" / args.experiment)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"ok: {len(manifests)} manifest(s) verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
