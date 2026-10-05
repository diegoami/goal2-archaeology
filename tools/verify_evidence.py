#!/usr/bin/env python3
"""Run game-archaeologist's pinned evidence verifier on this repository's behalf (ADR-009).

`tools/ga.py` fetches the tool at the commit `archaeology.json` pins into
`.cache/game-archaeologist/<commit>/`, beside the pinned `tools/validate_records.py` and `formats/`;
this wrapper is a subprocess pass-through, never a copy: arguments, standard streams and the exit
code go through unchanged, so the rules applied are the pinned ones and only theirs. The tool runs
from this wrapper's working directory, never from the cache folder that holds it, so it serves the
repository it is run in.

    python3 tools/verify_evidence.py E<nnn> [--local DIR] [--evidence-dir DIR] [--repo OWNER/NAME]
        Read `evidence/E<nnn>/*.manifest.json`, validate each as `evidence-manifest/1` with the
        pinned validator, download release `E<nnn>` into a fresh `.cache/evidence/<E<nnn>>/` in one
        `gh release download` call, and check every listed asset there by sha256. `--local DIR`
        checks an already-downloaded bundle instead of the release. Exit 0 prints
        `ok: <n> manifest(s) verified`; any problem is a named line and exit 1.
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
        tool = ga.fetch() / ga.VERIFY_EVIDENCE
    except ga.GaError as e:
        print(f"verify_evidence.py: {e}")
        return 1
    completed = subprocess.run([sys.executable, str(tool), *argv])
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
