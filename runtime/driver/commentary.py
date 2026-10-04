#!/usr/bin/env python3
"""GOAL.EXE's match commentary, score and speed read from a savestate's guest memory (I1; T10).

Layout (static/goal-exe/, segment 0791 and the data segment; every offset is a DS offset):
- the commentary is a ring of 200 records of 6 bytes at DS:7C38 + 6*n, n = 1..200, written by
  `0791:1D4A` (seg_0791_03.asm:862-926): byte +0 the template, word +1 player 1, word +3 player 2,
  byte +5 the team; the record after the newest gets 0xFF (seg_0791_03.asm:944); `0791:A4A1` fills
  the ring with 0xFF and zeroes the counter at the start of every match (seg_0791_17.asm:272-280), and
  clears the quick-result flags DS:9A3E, DS:9A3F and DS:7C38 (seg_0791_17.asm:440-444);
- the word DS:80EE is the newest record's n, advanced 1..200 by `214B:1C86` (seg_0791_03.asm:862-871);
- template t is a Pascal string at DS:00BE + 0x15*t, byte 1 marks player 1 and byte 2 player 2
  (`0791:1829`, seg_0791_03.asm:292-306; the strings are in static/goal-exe/data/ds_2581_01.hex);
- a player's name is a Pascal string at the far pointer DS:9B6C + 11*index (seg_0791_03.asm:318-321);
- the score bytes DS:9B3C (engine team 0) and DS:9B3D (engine team 1) (compared at seg_0791_23.asm:1020-1021);
- the match delay byte at the far pointer DS:A923 + 0x3F (0 fastest), raised by key code 0xAE up to
  5 and lowered by 0xAF down to 0 (`0791:9372`, seg_0791_15.asm:775-791).
Standard library only."""

RING, REC, SIZE = 0x7C38, 6, 200
COUNTER = 0x80EE
TEMPLATES, TEMPLATE_STRIDE, N_TEMPLATES = 0x00BE, 0x15, 67   # 0 .. 66: the last is "** LINESMAN FLAGS **"
NAMES, NAME_LEN = 0x9B6C, 11
SCORE = 0x9B3C
GAME_RECORD, SPEED_FIELD = 0xA923, 0x3F

# Templates that are events in the sense of GOAL.HLP P106 ("goals, bookings, sendings-off and
# injuries are listed in the commentary"), plus substitutions; indices from the template table
# (static/goal-exe/data/ds_2581_01.hex lines 13, 38-39, 46-47: DS:00BE, 03DC, 03F1, 04D8, 04ED, 0502).
EVENTS = {0: "substitution", 38: "goal", 39: "own goal", 50: "booking", 51: "sending off", 52: "injury"}

# Lines between two reads above which the ring may have wrapped past the older read: the ring holds
# SIZE records and a delta is only known modulo SIZE. [designed] Half the ring; the largest delta
# measured between two polls is in the E004 summary (`max lines between reads`).
GAP_LIMIT = SIZE // 2


def far(state, off):
    """The linear address of the far pointer (offset word, segment word) at DS:off."""
    return state.ds_word(off + 2) * 16 + state.ds_word(off)


def pascal(raw):
    return raw[1:1 + min(raw[0], len(raw) - 1)].decode("cp437", errors="replace")


class Snapshot:
    """What one savestate holds of the match: the counter, the ring, the score, the speed byte."""

    def __init__(self, state):
        self.counter = state.ds_word(COUNTER)
        self.ring = state.ds_bytes(RING, REC * (SIZE + 1))  # n = 0 (the DS:7C38 flag byte) .. 200
        self.score = tuple(state.ds_bytes(SCORE, 2))
        self.speed = state.memory(far(state, GAME_RECORD) + SPEED_FIELD, 1)[0]
        self.templates = [pascal(state.ds_bytes(TEMPLATES + TEMPLATE_STRIDE * t, TEMPLATE_STRIDE)) for t in range(N_TEMPLATES)]
        self._names_at = far(state, NAMES)
        self._state = state

    def record(self, n):
        r = self.ring[REC * n:REC * n + REC]
        return {"template": r[0], "p1": int.from_bytes(r[1:3], "little"), "p2": int.from_bytes(r[3:5], "little"), "team": r[5]}

    def name(self, index):
        return pascal(self._state.memory(self._names_at + NAME_LEN * index, NAME_LEN)) if index else ""

    def text(self, rec):
        """The line as `0791:1829` draws it: the template with byte 1 and byte 2 replaced by the names."""
        if rec["template"] >= len(self.templates):
            return f"<template {rec['template']}>"
        t = self.templates[rec["template"]].replace("\x01", f" {self.name(rec['p1'])} ").replace("\x02", f" {self.name(rec['p2'])} ")
        return " ".join(t.split())


class Tracker:
    """Accumulates the commentary of one match over successive reads. Each read adds the records
    after the previous read's counter, up to this read's; a read whose distance from the previous one
    is GAP_LIMIT or more (modulo SIZE) is noted in `gaps`, since lines may have been lost."""

    def __init__(self):
        self.lines, self.gaps, self.deltas = [], [], []
        self.last = 0  # A4A1 zeroes the counter at the start of every match

    def add(self, snap, label=""):
        delta = (snap.counter - self.last) % SIZE
        if delta >= GAP_LIMIT:
            self.gaps.append(f"{label}: counter {self.last} -> {snap.counter} ({delta} lines)")
        self.deltas.append(delta)
        for k in range(1, delta + 1):
            n = (self.last + k - 1) % SIZE + 1
            rec = snap.record(n)
            if rec["template"] == 0xFF:
                self.gaps.append(f"{label}: record {n} is the end marker 0xFF")
                continue
            self.lines.append(dict(rec, n=n, text=snap.text(rec)))
        self.last = snap.counter
        return delta

    def events(self):
        """The event lines (EVENTS) in order: (kind, team, text)."""
        return [(EVENTS[x["template"]], x["team"], x["text"]) for x in self.lines if x["template"] in EVENTS]
