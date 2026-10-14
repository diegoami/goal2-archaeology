"""Collision-proof log creation for the E027 scripts (CLAUDE.md rule 20: a measured output is never overwritten or mixed).

`open_new(path, mode="w")` creates the file with exclusive creation ('x'); when the name exists it tries `<stem>-1<suffix>`,
`<stem>-2<suffix>`, ... so two launches in the same second keep separate files and an existing log is never truncated or
appended to. `stamped(directory, prefix, suffix=".log")` builds `<prefix>-<UTC second>-<pid>` as the first candidate.
"""
import os
from datetime import datetime, timezone
from pathlib import Path


def open_new(path, mode="w"):
    path = Path(path)
    n = 0
    while True:
        p = path if n == 0 else path.with_name(f"{path.stem}-{n}{path.suffix}")
        try:
            return p, open(p, mode.replace("w", "x").replace("a", "x"))
        except FileExistsError:
            n += 1


def stamped(directory, prefix, suffix=".log"):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return Path(directory) / f"{prefix}-{stamp}-{os.getpid()}{suffix}"
