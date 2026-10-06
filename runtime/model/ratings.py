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
  2AA3-family emitter; the ring record itself is written by `0791:1D4A` AFTER the delta) — except
  a completed "challenge by" line, whose net is 0 (the −10 of the table plus `0791:56CB`'s +10,
  the one ring-invisible writer; the rule below);
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

Known edge (E012 notes.md §4.3): `0791:56CB` adds +10 directly, without a ring line, to the
challenger of a "challenge by" line (template 65) that `0791:5565` emitted while DS:8303 was
set and whose invocation ran to its end — the completed challenge nets 0, not the table's −10.
5565's 8303-set invocation can, after its 0x41 line, only emit further lines when it bails
before 56CB (5474/5513 → 539F's 0x0E/0x21 pair or 408E's 0x16/0x17/0x18; 5513 → 8206's
substitution lines 0x35-0x37; 4151 → 3FAD(9)'s 0x15) or bail silently (a goalkeeper holder,
`45d(8303B)`; a goalkeeper challenger, 4D3F) — so a 0x41 line whose FOLLOWING line's template
is none of those came from an invocation that reached 56CB and nets 0. `0791:5B36` can also
emit a 0x41 line with 8303 set and never adds the +10; its follow-ups (5A8E's 5A33 lines) are
the rule's remaining ambiguity, recorded in the notes. The E012 record pins the mechanism: its
two adjacent 0x41 lines (positions 294/295) are a completed challenge (followed by the other
player's 0x41 — +10 observed on the read) and a 539F-bailed one (followed by the 0x0E/0x21
pair naming the same player — the plain −10).

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
CHALLENGE = 65           # 0791:5653 (in 5565) / 0791:5B8F (in 5B36): "challenge by", 8303 set
CHALLENGE_BONUS = 10     # 0791:56CB: 5565's ring-invisible +10 to the challenger
# the templates 5565's 8303-set invocation emits when it BAILS between its 0x41 line and 56CB
# (seg_0791_09.asm 5474/5513 → 539F: 0x0E then 0x21 (5465/5468) or 408E's 0x16-0x18; 5513 →
# 8206's 0x35-0x37; 4151 → 3FAD(9)'s 0x15): a 0x41 line whose following line is none of these
# completed (56CB) and nets 0; the two silent bails need a goalkeeper (holder or challenger)
CHALLENGE_BAIL = frozenset({0x0E, 0x21, 0x15, 0x16, 0x17, 0x18, 0x35, 0x36, 0x37})


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
        """One ring line, as 1D4A wrote it: (template, player-1 word, player-2 word). A
        template-65 line is applied with its table delta; `apply_lines` adds 56CB's +10 to the
        completed ones (a single line carries no follower to decide completion)."""
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
        """`lines`: an iterable of (template, p1, p2) in ring order.

        A template-65 "challenge by" line nets 0 (the table's −10 plus 56CB's +10) when the
        line AFTER it is not one of 5565's bail lines (CHALLENGE_BAIL) — that invocation ran
        to 56CB. The decision needs the follower, so the last line of a batch is judged
        without one: split a log at half time only where no 0x41 line is last (none is, in
        the E012 records)."""
        lines = list(lines)
        for i, (template, p1, p2) in enumerate(lines):
            self.apply_line(template, p1, p2)
            if template == CHALLENGE and p1 and \
                    (i + 1 == len(lines) or lines[i + 1][0] not in CHALLENGE_BAIL):
                self.words[p1] = (self.words.get(p1, 0) + CHALLENGE_BONUS) & 0xFFFF
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
