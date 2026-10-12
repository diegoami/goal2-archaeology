#!/usr/bin/env python3
"""The live view of a sitting: the newest staged snapshot's screen and the keys since the last call.

    python3 runtime/human/live.py <session> [--all-keys]

<session> is the session folder (scratch/human/sessions/<date-time>) or its name. Prints the
newest snapshot the recorder has staged (the last complete line of index.jsonl; the snapshot is
written before its index line, so a listed snapshot is whole) as CP437 text, then every key
press logged since the previous call, with its time into the sitting, and whether DOSBox-X is
paused (pauses.jsonl).

Read-only on the session: every session file is opened for reading only, and nothing is
created there. Where the previous call stopped in keys.jsonl (a byte offset, after the last
complete line) is kept outside the session, in scratch/human/live/<name>.json; `--all-keys`
prints every key from the start instead."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402

SESSIONS = ROOT / "scratch" / "human" / "sessions"
CURSORS = ROOT / "scratch" / "human" / "live"


def session_dir(arg):
    p = Path(arg)
    if not p.is_dir() and (SESSIONS / arg).is_dir():
        p = SESSIONS / arg
    if not (p / "meta.json").is_file():
        raise SystemExit(f"{arg}: not a recorder session folder (no meta.json)")
    return p


def complete_lines(data):
    """The JSON objects of `data`'s complete lines (a line still being written has no newline yet
    and is left for the next call), and the byte offset after the last complete line."""
    end = data.rfind(b"\n") + 1
    out = []
    for raw in data[:end].splitlines():
        try:
            out.append(json.loads(raw))
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
    return out, end


def newest_snapshot(session):
    """(index entry, screen text or a reason it is unreadable), or (None, None) before the first."""
    index = session / "index.jsonl"
    if not index.is_file():
        return None, None
    entries, _ = complete_lines(index.read_bytes())
    if not entries:
        return None, None
    entry = entries[-1]
    try:
        data = (session / entry["file"]).read_bytes()
    except OSError as e:
        return entry, f"(unreadable: {e})"
    if entry.get("sha256") and hashlib.sha256(data).hexdigest() != entry["sha256"]:
        return entry, "(the snapshot's bytes differ from its index line)"
    try:
        return entry, savestate.Savestate(data).screen().text()
    except Exception as e:  # a savestate this reader cannot parse is reported, never fatal
        return entry, f"(not a savestate this reader parses: {e})"


def paused_state(session, t0):
    """'paused since +Ns' when the last line of pauses.jsonl is a pause, else None."""
    p = session / "pauses.jsonl"
    if not p.is_file():
        return None
    lines, _ = complete_lines(p.read_bytes())
    if lines and lines[-1].get("event") == "pause":
        return f"paused since +{lines[-1]['monotonic_s'] - t0:.1f}s"
    return None


def view(session, all_keys=False, cursors=CURSORS):
    """The text the command prints; advances the key cursor (outside the session folder)."""
    session = Path(session)
    meta = json.loads((session / "meta.json").read_text())
    t0 = meta.get("monotonic_start_s") or 0.0
    entry, text = newest_snapshot(session)
    out = [f"session {session.name}"]
    if entry is None:
        out.append("no snapshot staged yet")
    else:
        out.append(f"newest snapshot: seq {entry.get('seq')}, {entry.get('origin')}, "
                   f"+{entry.get('elapsed_s')}s, {entry.get('utc')}")
        state = paused_state(session, t0)
        if state:
            out.append(state)
        out.append(text)
    cursor = Path(cursors) / f"{session.name}.json"
    start = 0
    if not all_keys and cursor.is_file():
        start = json.loads(cursor.read_text()).get("keys_offset", 0)
    keys = session / "keys.jsonl"
    data = keys.read_bytes() if keys.is_file() else b""
    if start > len(data):
        start = 0                    # a different file under the same name: start again
    events, used = complete_lines(data[start:])
    presses = [e for e in events if e.get("event") == "press"]
    out.append(f"keys since the previous call: {len(presses)} press(es)")
    if presses:
        out.append(" ".join(f"+{e['monotonic_s'] - t0:.1f}s {e['keysym']}" for e in presses))
    Path(cursors).mkdir(parents=True, exist_ok=True)
    cursor.write_text(json.dumps({"keys_offset": start + used}))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("session", help="the session folder, or its name under scratch/human/sessions")
    ap.add_argument("--all-keys", action="store_true", help="every key from the sitting's start")
    a = ap.parse_args(argv)
    print(view(session_dir(a.session), all_keys=a.all_keys))
    return 0


if __name__ == "__main__":
    sys.exit(main())
