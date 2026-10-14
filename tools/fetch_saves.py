#!/usr/bin/env python3
"""Download the owner's saved games from release `goal2-saves` and verify them by hash.

`python3 tools/fetch_saves.py` reads `artifacts/saves.json`, downloads every save that is not
already cached (or all of them with `--refresh`) into `.cache/saves/`, and verifies each file's
sha256 and byte count. Any mismatch exits 1. `--check` only verifies the cache and never downloads.
The recorder (`runtime/human/recorder.py`) calls `fetch()` before every sitting.

A new save is added with `python3 tools/fetch_saves.py --add FILE.GL [--as NAME.GL]`: it uploads
the file to the release and records its hash in `artifacts/saves.json` (commit that change).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE = REPO_ROOT / ".cache" / "saves"
MANIFEST = REPO_ROOT / "artifacts" / "saves.json"
DEFAULT_REPO = "diegoami/goal2-archaeology"


def manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(cache: Path = CACHE) -> list[str]:
    """Every problem with the cached saves; empty when each is exactly as released."""
    problems = []
    for entry in manifest()["saves"]:
        path = cache / entry["path"]
        if not path.is_file():
            problems.append(f"{entry['path']}: missing from {cache}")
            continue
        if path.stat().st_size != entry["bytes"]:
            problems.append(f"{entry['path']}: {path.stat().st_size} bytes, "
                            f"saves.json says {entry['bytes']}")
        actual = sha256_file(path)
        if actual != entry["sha256"]:
            problems.append(f"{entry['path']}: sha256 {actual}, saves.json says {entry['sha256']}")
    return problems


def download(names=None, repo: str = DEFAULT_REPO, cache: Path = CACHE) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    data = manifest()
    for entry in data["saves"]:
        if names is not None and entry["path"] not in names:
            continue
        subprocess.run(["gh", "release", "download", data["release"], "--repo", repo,
                        "-p", entry["path"], "-D", str(cache), "--clobber"],
                       check=True, capture_output=True, text=True)


def fetch(repo: str = DEFAULT_REPO, refresh: bool = False, cache: Path = CACHE) -> Path:
    """The verified cache directory; downloads what is missing or wrong (everything on refresh)."""
    bad = {p.split(":", 1)[0] for p in verify(cache)}
    names = None if refresh else bad
    if refresh or bad:
        download(names, repo=repo, cache=cache)
    problems = verify(cache)
    if problems:
        raise SystemExit("\n".join(problems))
    return cache


def add(src: Path, name: str | None, repo: str = DEFAULT_REPO) -> None:
    """Upload a save to the release and record its hash in saves.json."""
    src = Path(src)
    name = (name or src.name).upper()
    if not name.endswith(".GL"):
        raise SystemExit(f"{name}: not a GOAL saved game (.GL)")
    data = manifest()
    entry = {"path": name, "bytes": src.stat().st_size, "sha256": sha256_file(src)}
    known = next((e for e in data["saves"] if e["path"] == name), None)
    if known and known["sha256"] != entry["sha256"]:
        raise SystemExit(f"{name}: already released with another hash; a released save is never "
                         f"overwritten. Give the new one another name (--as).")
    CACHE.mkdir(parents=True, exist_ok=True)
    staged = CACHE / name
    if src.resolve() != staged.resolve():
        shutil.copyfile(src, staged)
    if known is None:
        data["saves"].append(entry)
        MANIFEST.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
    subprocess.run(["gh", "release", "upload", data["release"], str(staged), "--repo", repo],
                   check=True)
    print(f"{name}: uploaded to {data['release']}; commit artifacts/saves.json")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="verify the cache only; never download")
    parser.add_argument("--refresh", action="store_true", help="download every save again")
    parser.add_argument("--add", metavar="FILE.GL", help="upload a new save and record its hash")
    parser.add_argument("--as", dest="name", help="release name for --add")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    args = parser.parse_args(argv)
    if args.add:
        add(Path(args.add), args.name, repo=args.repo)
        return 0
    if args.check:
        problems = verify()
        if problems:
            print("\n".join(problems))
            return 1
    else:
        fetch(repo=args.repo, refresh=args.refresh)
    print(f"saves: verified in {CACHE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
