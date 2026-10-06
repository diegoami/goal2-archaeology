#!/usr/bin/env python3
"""A model of GOAL.EXE's performance ratings (the player-record word at +0x12, F007/F008) and
the man of the match (T26, Q011; E012).

Given a watched match's commentary line log — every ring line the game wrote, in order, as
(n, template, p1, p2, team) — the model reproduces every squad player's +0x12 word at half time
and full time, and the word `DS:7C3A` (the man of the match) that `0791:CAB0` selects after the
match. Every constant below cites the listing it comes from (`static/goal-exe/code/`,
addresses SEGMENT:OFFSET; data offsets are DS offsets, the table read from
`static/goal-exe/data/ds_2581_01.hex` rows 0x720-0x762). The rule, in full (E012 notes.md):

- every ring line applies `s8(DS:0x720[template])` to the word the line names as player 1
  (`0791:1E53`, the `add word es:[di+0x12], ax` at 1EAB, reached through `0791:1EB5` from every
  2AA3-family emitter; the ring record itself is written by `0791:1D4A` AFTER the delta);
- the starting XI (squad slots 1..11 of both teams) begins at 0x37 (`0791:F2C7` in run_match),
  every other player at 0x7FFF (blank, `1771:97C0` at new game);
- a substitution line (template 0, `on for`) sets the incoming player's word to 0x2747
  (`0791:C6FA` in refresh_pitch_slot) — the +10000 flag readers strip when the word is above
  5000 (`1771:385C`, `0791:CB43`);
- the man of the match is `0791:CAB0`'s max-scan over both sides' squad slots 1..20 (slots
  12..20 only when the player was substituted off, status bit 3 — from the log, the player a
  substitution line names as player 2), decoded value compared strictly, first in scan order
  winning ties; the scan runs after the match (F1F6 at F2F8) and its word is drawn on the
  summary only when the match was watched (0106's DS:9A3F gate).

Known edge, never observed in any analysed half (E012 notes.md §4): `0791:56CB` adds +10
directly, without a ring line, when DS:8303 is set inside `0791:5565`; every encoding the
writers produce makes template 65 ("challenge by") the only line whose net effect could differ
from the table (−10 + 10 = 0 when 5565 emits it, plain −10 when 5B36 does). No template-65 line
appeared in the E011 halves or the E012 records, so the model applies the table value.

Standard library only."""
from pathlib import Path

# --- the delta table: DS:0x720[template], 67 entries (ids 0..66) ---------------------
# static/goal-exe/data/ds_2581_01.hex rows 0720-0762, cross-checked against the runtime DS of
# the E011 half-time savestates (identical; nothing writes the table). Index = the template
# id, the same number that indexes the template strings at DS:00BE + 0x15*t (E004's reader).
DELTA_TABLE = (
    0, -10, -10, 0, 0, -1, 0, -10, 10, 10, 10, -10, 20, 0, 20, 20,       #  0..15
    0, 0, 0, 0, 0, 2, 16, 2, 16, 1, 8, 8, 1, 20, 10, 0,                  # 16..31
    0, 0, 4, 1, 0, 0, 40, -50, -10, -10, 0, 0, 0, 0, 0, -20,             # 32..47
    0, 0, -20, -100, 0, 0, -2, 0, 0, 0, 0, 0, 0, 0, 0, 0,                # 48..63
    0, -10, 0,                                                           # 64..66
)

BLANK = 0x7FFF           # 1771:384B: the word that draws blank
START = 0x37             # 0791:F2C7: the starting XI's initial word (55)
SUB_IN = 0x2747          # 0791:C6FA: an incoming substitute's word (10000 + 55)
FLAG_THRESHOLD = 5000    # 1771:3855 / 0791:CB2E: above this (signed) the word carries +10000
FLAG = 0x2710            # 1771:385C / 0791:CB43: the flag stripped by readers
SQUAD_SLOTS = 20         # the squad's 20 words (F007); CAB0 scans them 1..20
SUB_TEMPLATE = 0         # the "on for" template (E004's EVENTS)
N_TEMPLATES = len(DELTA_TABLE)


def s16(v):
    v &= 0xFFFF
    return v - 0x10000 if v >= 0x8000 else v


def decode(word):
    """The value readers compare: the word, minus 10000 when above 5000 (1771:3855-385C,
    0791:CB2E-CB43; the compare is signed, so a raw negative word is never flagged)."""
    v = s16(word)
    return v - FLAG if v > FLAG_THRESHOLD else v


class RatingsError(RuntimeError):
    pass


class Ratings:
    """The +0x12 words of both teams' squads, replayed from the commentary line log.

    `teams` is the two 20-word squads in slot order (the words the country records hold at
    the match start, DS:A917 + 0xBF*country). Slots 1..11 start at 0x37, the rest blank
    (F1F6's pre-match loop); `apply_line` then replays the ring lines. The substitution
    handling keeps the squad arrays in the shape C5DC leaves them (the incoming and outgoing
    words swap slots), so `man_of_the_match` scans in CAB0's exact order."""

    def __init__(self, teams):
        if len(teams) != 2 or any(len(t) != SQUAD_SLOTS for t in teams):
            raise RatingsError("teams must be two 20-word squads")
        self.squads = [list(t) for t in teams]
        self.words = {}
        for squad in self.squads:
            for slot, word in enumerate(squad, start=1):
                if word:
                    # F2A8: only slots below 0xC get the 0x37 store; the rest keep their blank
                    self.words[word] = START if slot < 0xC else BLANK
        self.subbed_off = set()      # the outgoing of every substitution line (status bit 3)

    def apply_line(self, template, p1, p2=0):
        """One ring line, as 1D4A wrote it: (template, player-1 word, player-2 word)."""
        if not 0 <= template < N_TEMPLATES:
            raise RatingsError(f"template {template} outside the table (0..{N_TEMPLATES - 1})")
        if template == SUB_TEMPLATE:
            # C5DC: the incoming (p1) takes 0x2747; the squad words swap; the outgoing (p2)
            # is marked (status bit 3) and keeps accumulating nothing (off the pitch)
            if p1:
                self.words[p1] = SUB_IN
                for squad in self.squads:
                    if p1 in squad and p2 in squad:
                        i, j = squad.index(p1), squad.index(p2)
                        squad[i], squad[j] = p2, p1
                        break
            if p2:
                self.subbed_off.add(p2)
            return
        if p1:
            # 1E53: add s8(DS:0x720[template]) to p1's word, 16-bit with wraparound
            self.words[p1] = (self.words.get(p1, 0) + DELTA_TABLE[template]) & 0xFFFF

    def apply_lines(self, lines):
        """`lines`: an iterable of (template, p1, p2) in ring order."""
        for template, p1, p2 in lines:
            self.apply_line(template, p1, p2)
        return self

    def word(self, player_word):
        return self.words.get(player_word, BLANK)

    def snapshot(self):
        """Both squads' words in slot order, as a savestate read of every slot would give
        them (blank for an empty slot)."""
        return [[self.word(w) if w else BLANK for w in squad] for squad in self.squads]

    def man_of_the_match(self):
        """`0791:CAB0`: the strict maximum of the decoded words over side 0 then side 1,
        squad slots 1..20 — slots 1..11 always scanned, 12..20 only for players substituted
        off (status bit 3, c5dc's mark), 0x7FFF skipped, ties keeping the first in scan
        order; `DS:7C3A` is the winner's squad word, 0 when nobody is rated above 1."""
        best, mom = 1, 0
        for squad in self.squads:
            for slot, word in enumerate(squad, start=1):
                if not word:
                    continue
                if slot >= 0xC and word not in self.subbed_off:
                    continue
                rating = self.word(word)
                if rating == BLANK:
                    continue
                v = decode(rating)
                if best < v:
                    best, mom = v, word
        return mom
