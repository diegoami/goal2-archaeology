#!/usr/bin/env python3
"""Run game-archaeologist's pinned artifact tool on this repository's behalf (ADR-009).

`tools/ga.py` fetches the tool at the commit `archaeology.json` pins into
`.cache/game-archaeologist/<commit>/`, beside the pinned `tools/validate_records.py` and
`formats/`; this wrapper is a subprocess pass-through, never a copy: arguments, standard streams
and the exit code go through unchanged, so the identity rule is the pinned one and only theirs.

    python3 tools/register_artifact.py manifest <dir> --label … --title … --version … --how …
        [--when <date>] [--note …] [--writes GLOB]… [--exclude GLOB]…
        Print the artifact-set/1 manifest for <dir>; `--when` defaults to today; a file matching a
        `runtime_writes` glob or an `--exclude` glob leaves `files` (U21).
    python3 tools/register_artifact.py check (<dir> | --list <file>) <set-id> [--strict]
        [--known artifacts/known.json]
        Re-hash a copy (or a `<sha256>  <bytes>  <path>` listing) against the known.json entry.
    python3 tools/register_artifact.py validate [--known artifacts/known.json]
        Check every known.json entry against the schema and recompute its id.

`--known` defaults to `artifacts/known.json` relative to the working directory. Errors are named
lines and exit 1; usage errors exit 2.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402


def main(argv=None) -> int:
    """Exit with the pinned tool's own exit code for the same arguments.

    Fetching or launching failures are named lines and exit 1; a tool killed by a signal
    terminates this process with that same signal."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        return ga.run_tool(ga.ARTIFACT_TOOL, list(argv))
    except ga.GaError as e:
        print(f"register_artifact.py: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
