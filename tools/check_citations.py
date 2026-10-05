#!/usr/bin/env python3
"""Run game-archaeologist's pinned citation checker on this repository's behalf (ADR-009).

`tools/ga.py` fetches the tool at the commit `archaeology.json` pins into
`.cache/game-archaeologist/<commit>/`, beside the pinned `tools/validate_records.py` and `formats/`;
this wrapper is a subprocess pass-through, never a copy: arguments, standard streams and the exit
code go through unchanged, so the rules applied are the pinned ones and only theirs. The tool runs
from this wrapper's working directory, never from the cache folder that holds it, so it serves the
repository it is run in: `runs/` and the repository root come from there.

    python3 tools/check_citations.py <finding.md> [--runs DIR] [--root DIR]
        Exit 1 when a run id in the finding has no record under `runs/E<nnn>/`, or when a claim in
        `## Answer` or `## Inferences` cites no run id, or when a `static:<path>[:<line>]` citation
        is malformed, names no tracked path or names a line the file lacks. Exit 0 otherwise.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402


def main(argv=None) -> int:
    """Exit with the pinned tool's own exit code for the same arguments."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        tool = ga.fetch() / ga.CHECK_CITATIONS
    except ga.GaError as e:
        print(f"check_citations.py: {e}")
        return 1
    completed = subprocess.run([sys.executable, str(tool), *argv])
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
