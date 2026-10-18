#!/usr/bin/env python3
"""A work directory for Ghidra whose path has no dot element (fix #315).

Ghidra's headless analyzer refuses a project path with an element that starts with '.'
("Path element starting with '.' is not permitted", ProjectLocator, Ghidra 12.1.4). The harness's
isolated worktrees live under <repository>/.claude/worktrees/, and a TMPDIR under them (or any
other dotted folder) puts the project there. So Ghidra's project, input and temporary files go to
a folder made here: $HOME/goal2-ghidra-work/<unit>-<random> (GOAL2_GHIDRA_WORK names another base),
on the real disk, whatever the repository's own path and TMPDIR are.

  python3 tools/static/ghidra_work.py new <unit>     prints the path of a new, empty directory

The caller removes the directory when it is done (tools/static/decompile.sh does, unless KEEP_WORK=1;
GhidraMappingTests does). The base itself stays; it is empty between runs.
"""
import os
import re
import sys
import tempfile
from pathlib import Path

BASE_NAME = "goal2-ghidra-work"
BASE_ENV = "GOAL2_GHIDRA_WORK"


class DottedPathError(RuntimeError):
    pass


def base_dir(env=None) -> Path:
    env = os.environ if env is None else env
    named = env.get(BASE_ENV)
    if named:
        base = Path(named)
        if not base.is_absolute():
            raise DottedPathError(f"{BASE_ENV} must be an absolute path, got {named!r}")
    else:
        home = env.get("HOME") or str(Path.home())
        base = Path(home) / BASE_NAME
    base.mkdir(parents=True, exist_ok=True)
    resolved = Path(os.path.realpath(base))
    dotted = [part for part in resolved.parts if part.startswith(".")]
    if dotted:
        raise DottedPathError(
            f"Ghidra's work folder {resolved} has an element starting with '.' ({dotted[0]}); "
            f"Ghidra rejects such a project path. Set {BASE_ENV} to an absolute path without one.")
    return resolved


def new_work_dir(unit: str, env=None) -> Path:
    prefix = re.sub(r"[^A-Za-z0-9_-]", "-", unit).lstrip("-_") or "work"
    return Path(tempfile.mkdtemp(prefix=prefix + "-", dir=base_dir(env)))


def main(argv) -> int:
    if len(argv) != 3 or argv[1] != "new":
        print("usage: ghidra_work.py new <unit>", file=sys.stderr)
        return 2
    try:
        print(new_work_dir(argv[2]))
    except DottedPathError as e:
        print(f"ghidra_work.py: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
