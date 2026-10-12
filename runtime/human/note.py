#!/usr/bin/env python3
"""Append one coaching note to a running (or finished) sitting: a line in the session's notes.jsonl.

    python3 runtime/human/note.py <session> "text"

<session> is the session folder (scratch/human/sessions/<date-time>) or its name. The line holds
the UTC time, the host's monotonic clock (CLOCK_MONOTONIC, the clock the recorder stamps keys and
save requests with, so extract.py can place the note between the two snapshots it falls between)
and the text. The note is the owner's own words, typed in the chat and passed here; nothing is
read from any display. The file is opened for appending and synced, so a note is never lost to a
sitting that ends at once, and several notes never overwrite each other."""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SESSIONS = ROOT / "scratch" / "human" / "sessions"


def session_dir(arg):
    """The session folder named by `arg` (a path, or a name under SESSIONS); it must hold the
    recorder's meta.json, so a note never lands in a folder that is not a sitting."""
    p = Path(arg)
    if not p.is_dir() and (SESSIONS / arg).is_dir():
        p = SESSIONS / arg
    if not (p / "meta.json").is_file():
        raise SystemExit(f"{arg}: not a recorder session folder (no meta.json)")
    return p


def append_note(session, text, clock=time.monotonic):
    """Append the note line; returns it."""
    if not text.strip():
        raise SystemExit("an empty note")
    line = {"utc": datetime.now(timezone.utc).isoformat(), "monotonic_s": clock(), "text": text}
    fd = os.open(Path(session) / "notes.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, (json.dumps(line, ensure_ascii=False) + "\n").encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    return line


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("session", help="the session folder, or its name under scratch/human/sessions")
    ap.add_argument("text", help="the note")
    a = ap.parse_args(argv)
    line = append_note(session_dir(a.session), a.text)
    print(f"noted at {line['utc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
