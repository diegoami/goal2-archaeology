#!/usr/bin/env python3
"""T39b: the extraction of the owner's test sitting 20261011-215411, with the interventions the
session folder does not record, declared (the main session's account, 2026-10-11).

    python3 experiments/E015-human-playthrough/extract_215411.py

Runs extract.py on scratch/human/sessions/20261011-215411 with --countries 16 (Italy, the owner's
country) and one --declare per intervention."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402

SESSION = ROOT / "scratch" / "human" / "sessions" / "20261011-215411"
DECLARED = [
    "I3:the main session copied the owner's saved game 1.GL (169553 bytes, sha256 "
    "4a0f9bc0afaf0f32adf830de427a25120d60cacaf427922a630a86b50f86a470, from the main checkout's "
    "scratch/human/sessions/20261011-161003/game/1.GL) into this session's game copy at "
    "2026-10-11T19:54:11.10Z, the second the session folder appeared and before DOSBox-X started "
    "(the recorder had no --load then); the owner loaded it with the game's own keys (y, Return) "
    "and played on from Italy's main menu (Belgium away next)",
    "I2:the main session pressed the Pause key to end the owner's pauses (the owner's keyboard "
    "has no Pause key): about 19:55:39Z (keys.jsonl holds a Pause press at +88.312 s, after the "
    "recorder had logged the resume at +86.090 s with no key: that Pause reached a running game), "
    "at 19:56:37Z (the resume logged at +145.836 s; keys.jsonl holds no key then), and about "
    "19:58:40Z (the title left PAUSED; pauses.jsonl holds no third resume and keys.jsonl no key "
    "after +237.9 s: the recorder no longer read either)",
]


if __name__ == "__main__":
    sys.exit(extract.main([str(SESSION), "--countries", "16"]
                          + [a for d in DECLARED for a in ("--declare", d)]))
