#!/usr/bin/env python3
"""Download one artifact set from this repository's release and verify it by hash.

`python3 tools/fetch_artifact.py <set-id>` reads `artifacts/known.json`, downloads that set's files
from release `goal2-original` into `.cache/artifacts/<set-id>/`, and verifies each file's sha256
and byte count. Any mismatch exits 1, so a corrupted download never becomes a running artifact.

`--check` only verifies what is already cached, without downloading.

A download that fails on the network is retried once (`tools/net.py`, #236). When it still fails on
the network and the cached copy already verifies, the download is skipped with a printed line and
the set is verified from the cache; with no verified copy the failure stands.

[designed: owner, 2026-10-21] When `gh release download` fails other than on the network (a cloud
session's proxy allows only GitHub's REST API, and gh's release commands use GraphQL), each file is
downloaded over plain HTTPS
from the public release instead (`https://github.com/<repo>/releases/download/<tag>/<name>`); the
sha256 check is the same either way.

Adapted from diegoami/toy-archaeology tools/fetch_artifact.py at a3056ff: the release is
`goal2-original` and the repository `diegoami/goal2-archaeology`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

try:  # imported as tools.fetch_artifact, or run as tools/fetch_artifact.py with tools/ on the path
    from tools import net
except ImportError:
    import net

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE = REPO_ROOT / ".cache" / "artifacts"
KNOWN = REPO_ROOT / "artifacts" / "known.json"
RELEASE = "goal2-original"
DEFAULT_REPO = "diegoami/goal2-archaeology"


def sets() -> dict:
    """The artifact-set manifests in known.json, keyed by id."""
    data = json.loads(KNOWN.read_text(encoding="utf-8"))
    return {entry["manifest"]["id"]: entry["manifest"] for entry in data["sets"]}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(set_id: str) -> list[str]:
    """Every problem with the cached copy of a set; empty when it is exactly as released."""
    known = sets()
    if set_id not in known:
        return [f"{set_id}: unknown artifact set (not in artifacts/known.json)"]
    manifest = known[set_id]
    dest = CACHE / set_id
    problems = []
    for entry in manifest["files"]:
        path = dest / entry["path"]
        if not path.is_file():
            problems.append(f"{entry['path']}: missing from {dest}")
            continue
        if path.stat().st_size != entry["bytes"]:
            problems.append(
                f"{entry['path']}: {path.stat().st_size} bytes, known.json says {entry['bytes']}")
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            problems.append(f"{entry['path']}: sha256 {actual}, known.json says {entry['sha256']}")
    return problems


def https_download(repo: str, tag: str, name: str, dest: Path) -> bool:
    """Download one release asset of a public repository over plain HTTPS; False when it fails."""
    url = f"https://github.com/{repo}/releases/download/{tag}/{name}"
    try:
        with urllib.request.urlopen(url, timeout=120) as r, open(dest / name, "wb") as out:
            shutil.copyfileobj(r, out)
        return True
    except OSError as e:
        print(f"{name}: HTTPS download failed too ({e})", file=sys.stderr)
        return False


def download(set_id: str, repo: str = DEFAULT_REPO) -> Path:
    """Download a set's files from the release into the cache; return the destination."""
    known = sets()
    if set_id not in known:
        raise SystemExit(f"{set_id}: unknown artifact set (not in artifacts/known.json)")
    dest = CACHE / set_id
    dest.mkdir(parents=True, exist_ok=True)
    for entry in known[set_id]["files"]:
        result = net.run_retrying(
            ["gh", "release", "download", RELEASE, "--repo", repo,
             "-p", entry["path"], "-D", str(dest), "--clobber"])
        if result.returncode == 0:
            continue
        # Only a failure that is not the network (a cloud proxy's 403 on gh's GraphQL) falls back to
        # HTTPS; when the network itself is down, the offline handling below applies as before.
        if not net.is_network_error(result.stderr) and https_download(repo, RELEASE, entry["path"], dest):
            continue
        if net.is_network_error(result.stderr) and not verify(set_id):
            reason = net.text(result.stderr).strip().splitlines()[0]
            print(f"{set_id}: offline, download skipped ({reason}); "
                  f"the cached copy is verified by hash instead", file=sys.stderr)
            return dest
        sys.stderr.write(net.text(result.stderr))
        raise subprocess.CalledProcessError(result.returncode, result.args,
                                            result.stdout, result.stderr)
    return dest


def fetch(set_id: str, repo: str = DEFAULT_REPO) -> Path:
    """The verified cache directory for a set, downloading it first when needed."""
    if verify(set_id):
        download(set_id, repo=repo)
    problems = verify(set_id)
    if problems:
        raise SystemExit("\n".join(problems))
    return CACHE / set_id


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("set_id")
    parser.add_argument("--check", action="store_true",
                        help="verify the cached copy only; never download")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args(argv)
    if not args.check:
        try:
            download(args.set_id, repo=args.repo)
        except subprocess.CalledProcessError as e:
            lines = net.text(e.stderr).strip().splitlines()
            reason = lines[0] if lines else f"gh exited {e.returncode}"
            print(f"{args.set_id}: could not be downloaded and is not cached ({reason}); "
                  f"run it again with the network", file=sys.stderr)
            return 1
    problems = verify(args.set_id)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"{args.set_id}: verified in {CACHE / args.set_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
