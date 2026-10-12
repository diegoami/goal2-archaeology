#!/usr/bin/env python3
"""T39b: the extraction of the owner's second sittings, 20261011-224811 and 20261011-225621, with
what the session folders do not record declared (the main session's account, 2026-10-11).

    python3 experiments/E015-human-playthrough/extract_224811_225621.py

Both run extract.py with --countries 16 (Italy, the owner's country). The saved-game copy
(meta.json `load`) and the recorder's own Pause keys (`by: recorder`) are declared by extract.py
itself from the session; the notes and live views of the main session are declared here."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402

SESSIONS = ROOT / "scratch" / "human" / "sessions"
DECLARED = {
    "20261011-224811": [
        "I0:no effect on the emulator: the main session ran runtime/human/live.py once during play "
        "(T39b-live-20261011-02.log, read-only), and a second time and wrote the note \"owner "
        "(chat): ok it works\" to notes.jsonl at 2026-10-11T20:52:35Z, after the window closed at "
        "20:52:32Z (the note lies after the last state)",
    ],
    "20261011-225621": [
        "I0:no effect on the emulator: the main session wrote both notes in notes.jsonl during the "
        "two pauses (its coach script) and ran runtime/human/live.py during each pause "
        "(T39b-live-20261011-03.log, read-only)",
    ],
}


def main():
    rc = 0
    for name, declared in DECLARED.items():
        rc |= extract.main([str(SESSIONS / name), "--countries", "16"]
                           + [a for d in declared for a in ("--declare", d)])
    return rc


if __name__ == "__main__":
    sys.exit(main())
