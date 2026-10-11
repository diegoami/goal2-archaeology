#!/usr/bin/env python3
"""T39b rework round 1 (R2): the extraction of the owner's test sitting 20261011-215411 that
supersedes E015-r0009. E015-r0009 (extract_215411.py) declared the main session's Pause keys but
counted them as the owner's presses and mapped them as owner transitions. This pass names each one
with --injected, so they are kept out of the owner's count and the screen/key map; keys.jsonl, the
raw log, is unchanged. The declared interventions are corrected to the key log: it holds three
Pause presses, at +88.312 s, +141.643 s and +148.438 s, all the main session's (the owner's
keyboard has no Pause key).

    python3 experiments/E015-human-playthrough/extract_215411_v2.py"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract  # noqa: E402

SESSION = ROOT / "scratch" / "human" / "sessions" / "20261011-215411"
INJECTED = ["Pause@88.312:main session", "Pause@141.643:main session",
            "Pause@148.438:main session"]
DECLARED = [
    "I3:the main session copied the owner's saved game 1.GL (169553 bytes, sha256 "
    "4a0f9bc0afaf0f32adf830de427a25120d60cacaf427922a630a86b50f86a470, from the main checkout's "
    "scratch/human/sessions/20261011-161003/game/1.GL) into this session's game copy at "
    "2026-10-11T19:54:11.10Z, the second the session folder appeared and before DOSBox-X started "
    "(the recorder had no --load then); the owner loaded it with the game's own keys (y, Return) "
    "and played on from Italy's main menu (Belgium away next)",
    "I2:the main session pressed the Pause key for the owner (whose keyboard has no Pause key). "
    "keys.jsonl logs three of its presses: +88.312 s (after the resume logged at +86.090 s with no "
    "key: it reached a running game), +141.643 s (during pause 2; the resume came at +145.836 s "
    "with no logged key) and +148.438 s (a running game); all three are named --injected and are "
    "not the owner's. A further Pause at about 19:58:40Z (pause 3) is in neither keys.jsonl nor "
    "pauses.jsonl: the recorder no longer read either after +237.9 s",
]


if __name__ == "__main__":
    sys.exit(extract.main([str(SESSION), "--countries", "16"]
                          + [a for d in DECLARED for a in ("--declare", d)]
                          + [a for i in INJECTED for a in ("--injected", i)]))
