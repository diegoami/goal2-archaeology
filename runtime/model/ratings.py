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
- a sending-off (template 51) or injury (template 52) line removes its player from the pitch
  and re-sorts his side's slots 1..11 with `0791:230C`'s pairwise compare-and-swap (reached
  from `7B77`/`7D56` through `C48D → C503`): each player's key is 0x0E when unavailable
  (1771:3216), else his position byte `+6` — the model keys a player by his starting slot,
  which the records corroborate; equal keys never swap, but the scan swaps on every strictly
  smaller key, so the sort is an exchange sort, not a stable partition — two removed players
  can REVERSE their original relative order (XI 101-111, removing 103 then 108, ends with the
  tail 108,103; observed in E012-r0002/r0003, whose tails 126,130 and side-0 173-at-slot-11
  this rule and the keying reproduce); a booking (template 50) re-orders nothing — r0002's
  booked-and-remaining players (131, 127) stay among the available in the half-time read,
  and the reorder is the removal, not the card;
- the man of the match is `0791:CAB0`'s max-scan over both sides' squad slots 1..20 (slots
  12..20 only when the player was substituted off, status bit 3 — from the log, the player a
  substitution line names as player 2), decoded value compared strictly, first in scan order
  winning ties; the scan runs after the match (F1F6 at F2F8) and its word is drawn on the
  summary only when the match was watched (0106's DS:9A3F gate).

Known edge (E012 notes.md §4.3): `0791:56CB` adds +10 directly, without a ring line, to the
challenger of a "challenge by" line (template 65) that `0791:5565` emitted while DS:8303 was
set and whose invocation ran past its checks — the completed challenge nets 0, not the
table's −10. 5565's 8303-set invocation first emits the `2B28(0x41)` "challenge by" line
(`5653`), then runs the chain `5474` (5676) → `5513` (567E) → `4151` (5685) → `045D(DS:830B)`
(5692) → `4D3F` (56A3) → the `DS:8303` test (56A6, `jne 56B5`) → `56CB`. Every bail that
EMITS does so as the line immediately after the 0x41 line: `5474`/`5513` → `539F`, whose
8303-set path emits the pair 2AA3(0x0E) then 2AA3(0x21) (`5465`/`5468`) or `408E`'s
0x16/0x17/0x18 (`5405`-`5416`); `5513`'s coin → `8206`'s substitution lines 0x35-0x37;
`4151` → `3FAD(9)`'s 2AA3(0x15) (`3F82`) — a 0x41 line whose follower is one of those
bailed before 56CB and keeps the plain −10. The ONE silent bail is `045D(DS:830B)` at
5692-5697: `045D` (seg_0791_01.asm:511) returns 1 when its argument — the HOLDER's pitch
slot, DS:830B — is 1 or 12, i.e. when the ball holder stands on a side's slot 1 (pitch
slots 1 and 12 are the two keepers' slots; 0668 = [0x0B, 0x00]: team 0 plays pitch 12..22,
team 1 plays 1..11), and the `jne 56D0` skips 56CB without emitting anything. (`4D3F` at
56A3 is NOT a bail: its return is never tested — 56A6's `cmp byte [0x8303],0` is the next
branch, so the challenger being a goalkeeper does not stop the +10; T26 rework R1 removed
the earlier claim that it does.) A 2B28 ring line stores p2 = 0 (2B41-2B43), so the duel's
holder is not named by the line; the model tracks it as the p1 of the most recent
2AA3-family line (HOLDER_P1) or the p2 of the most recent 2AD4 line (HOLDER_P2), and a 0x41
line that carries p2 != 0 names its holder explicitly (a convention for inputs that provide
it — the unit tests use it). When the follower is not a visible bail line and the holder is
unknown — or the 0x41 line is last in its batch, so a bail follower could still arrive in
the next one — the outcome cannot be inferred from the log: the model records the case in
`undecided` (no +10 applied, the number NOT asserted) instead of silently returning an
exact rating. `0791:5B36` can also emit a 0x41 line with 8303 set and never adds the +10;
its follow-ups (5A8E's 5A33 lines, 5C44's 8206) are the rule's remaining ambiguity, recorded
in the notes. The E012 record pins the mechanism: its two adjacent 0x41 lines (positions
294/295) are a completed challenge (followed by the other player's 0x41, holder 364 on side
1's slot 3 — not a keeper — +10 observed on the read) and a 539F-bailed one (followed by
the 0x0E/0x21 pair naming the same player — the plain −10).

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
SENT_OFF = 51            # 0791:7B77 (2AD4 0x33): the sending-off line; the player leaves the pitch
INJURY = 52              # 0791:7D56 (2B28 0x34): the injury line; the player leaves the pitch (E004's EVENTS)
XI = 0xB                 # the XI: squad slots 1..11 = slice length 11 (F2A8's bound; CAB0 always scans them)
# 0791:230C's sort key for an unavailable player (seg_0791_04.asm:2378-237B): 1771:3216
# returns 1 (unavailable) when the record's +0xE >= 1 or status byte +0x10 has bit 8, 6 or 3,
# and 230C then writes the key 0x0E instead of the record's position byte +6 (2381-238B)
UNAVAILABLE_KEY = 0x0E
# the templates 5565's 8303-set invocation emits when it BAILS between its 0x41 line and 56CB
# (seg_0791_09.asm 5474/5513 → 539F: 0x0E then 0x21 (5465/5468) or 408E's 0x16-0x18; 5513 →
# 8206's 0x35-0x37; 4151 → 3FAD(9)'s 0x15): a 0x41 line whose following line is one of these
# bailed (the one silent bail, the holder on a keeper pitch slot, is handled separately)
CHALLENGE_BAIL = frozenset({0x0E, 0x21, 0x15, 0x16, 0x17, 0x18, 0x35, 0x36, 0x37})
# the templates emitted ONLY through 0791:2AA3 (seg_0791_05.asm:80-136): p1 = the ball
# holder (2AA3 reads DS:830B's pitch slot for p1, 830C's for p2). Every id below is pushed
# immediately before a `call 0x2aa3` — 384C (seg_0791_06.asm:855-916: the 0x786/0x788/0x78A
# coin tables 1,2,7,6,5,4 and the constants 3, 0xA, 9, 8), 3B9E (3), 3DF6 (0x794: 15,16),
# 3EF8 (0x17,0x18), 3FAD (0x16,0x15), 539F (0x0E,0x21), 5565 (0x0C, 56B0), 5B36 (0x0C 5C79,
# 0x1C 5E38), 5EAB (0x20), 5F06 (0x20 and the 0x80A coin table's 31,33,10,4,12), 6443
# (0x26,0x27 — the goal), 6755 (0x28,0x29), 69BD (0x31), 6E11 (0x2B), 6F01 (0x38), 6FEE
# (0x2A), 70F6 (0x2C), 71E8 (0x2E), 72F2 (0x3C,0x2F), 74C2 (0x30), 8206 (0x37, 8250).
# NOT here: 11 (0x0B, 2B28 in 5565/5B36 and 2AA3 in 5F06's 0x80A table), 25 (0x19, 2AD4 in
# 8AE9 and 2B28 in 5F8A) and 0 (C5DC's 1EB5 line and 5F06's 0x80A table) — their p1 is not
# reliably the holder. The param-driven 2AA3 call sites (3C3F, 593B, 5A33, 67B6, 6DEA) can
# in principle emit any id; none of the ids they pass is established, so a line of an id
# above is taken at face value (E012 notes §2).
HOLDER_P1 = frozenset({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 21, 22, 23, 24, 28,
                       31, 32, 33, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 49, 55, 56, 60})
# the templates emitted ONLY through 0791:2AD4: p1 = 830C's player, p2 = the ball holder —
# 798D (0x32, 79AB-79AE), 7B77 (0x33, 7BA9-7BAC), 8206 (0x35, 8253-8256), 82EB (0x36,
# 82F9-82FC). (8AE9's 0x19 = 25 is excluded: 5F8A also emits it through 2B28.)
HOLDER_P2 = frozenset({50, 51, 53, 54})


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
        self.off_pitch = set()       # sent off or injured: 230C keys them 14, to the XI's tail
        self.key = {}                # each XI player's sort key: his STARTING slot (see _sort_xi)
        for squad in self.squads:
            for slot, word in enumerate(squad, start=1):
                if word and slot < 0xC:
                    self.key[word] = slot
        self.holder = None           # the ball holder's word (2AA3/2AD4 lines name him)
        self.undecided = []          # (player word, why) — a challenge the log cannot decide

    def _holder_on_keeper_slot(self, holder):
        """045D(DS:830B) at 0791:5692: the bail fires when the holder's PITCH slot is 1 or 12
        — the two keepers' slots (0668 = [0x0B, 0x00]: team 1 plays pitch 1..11, team 0
        plays 12..22), i.e. when the holder's side-slot is 1. True/False when the holder is
        on a squad, None when he is not on either (unknown)."""
        if not holder:
            return None
        for squad in self.squads:
            if holder in squad:
                return squad.index(holder) == 0
        return None

    def _sort_xi(self, side):
        """`0791:230C` (reached from `C48D`'s tail `C503`, called by `7B77`'s sending-off at
        `7CAB`, `7D56`'s injury through `C88D` at `7E33`, and the quick engine's substitution
        path `8062 → C88D` at `81DB`; seg_0791_04.asm:357-465): build a key per side-slot
        1..11 — 0x0E when `1771:3216` says the player is unavailable (`2378-237B`), else the
        record's position byte +6 (`2381-238B`) — then the pairwise compare-and-swap: for
        j = 1..10 (`239E`/`2538`), for i = j+1..11 (`23B2`/`252F`), `key[i] < key[j]`
        (`23B5-23BE`, `jb`) swaps slots i and j fully — squad words (`2218`, `2239-22B4`),
        the 9B07 form bytes and the 0x80E8 pitch records (`23C7-23DB`/`23FA-241C`), and the
        keys themselves (`23C7-23DB`). This is an exchange sort, NOT a stable partition:
        equal keys never swap, but the scan swaps on EVERY strictly smaller key, so two
        removed players can reverse their original relative order (review R2's case: XI
        101-111, removing 103 then 108, ends with the tail 108,103). The predictor's key is
        the player's STARTING slot index — the position byte +6 is not in the line log;
        every E012 record's available XI stays in its starting order through the sorts, and
        the reads match this keying (r0002/r0003's tails and r0002's side 0). The sort also
        runs on the quick engine's substitution path; a substituted-in player's own +6 is
        likewise not in the log, so he inherits the outgoing's key — with the XI sorted by
        ascending key after every removal, that makes the sub-path sort a no-op on this
        model, which is what the records show (r0001's two subs left the swap order)."""
        squad = self.squads[side]
        xi = squad[:XI]
        keys = [UNAVAILABLE_KEY if (w in self.off_pitch or w not in self.key)
                else self.key[w] for w in xi]
        for j in range(XI - 1):              # [bp-5] = 1..10
            for i in range(j + 1, XI):       # [bp-3] = j+1..11
                if keys[i] < keys[j]:        # 23B5-23BE: jb -> 23C3 swaps i and j
                    xi[i], xi[j] = xi[j], xi[i]
                    keys[i], keys[j] = keys[j], keys[i]
        squad[:XI] = xi

    def apply_line(self, template, p1, p2=0):
        """One ring line, as 1D4A wrote it: (template, player-1 word, player-2 word). A
        template-65 line is applied with its table delta; `apply_lines` decides 56CB's +10
        (the follower, and the holder's pitch slot). The ball holder is tracked from the
        2AA3-family lines (HOLDER_P1: p1) and the 2AD4 lines (HOLDER_P2: p2); other lines
        leave it unchanged."""
        if not 0 <= template < N_TEMPLATES:
            raise RatingsError(f"template {template} outside the table (0..{N_TEMPLATES - 1})")
        if template == SUB_TEMPLATE:
            # C5DC: the incoming (p1) takes 0x2747; the squad words swap; the outgoing (p2)
            # is marked (status bit 3) and keeps accumulating nothing (off the pitch)
            if p1:
                self.words[p1] = SUB_IN
                for side, squad in enumerate(self.squads):
                    if p1 in squad and p2 in squad:
                        i, j = squad.index(p1), squad.index(p2)
                        squad[i], squad[j] = p2, p1
                        self.key[p1] = self.key.get(p2)   # the incoming inherits the slot's key
                        break
            if p2:
                self.subbed_off.add(p2)
            return
        if p1:
            # 1E53: add s8(DS:0x720[template]) to p1's word, 16-bit with wraparound
            self.words[p1] = (self.words.get(p1, 0) + DELTA_TABLE[template]) & 0xFFFF
        if template in (SENT_OFF, INJURY) and p1:
            # the player leaves the pitch (7B77's 2AD4(0x33) / 7D56's 2B28(0x34), both -> C48D
            # -> C503 -> 230C) and his side's XI is re-sorted by 230C's exchange sort: the
            # unavailable (key 14) fall to the tail, the rest keep ascending key order
            self.off_pitch.add(p1)
            for side, squad in enumerate(self.squads):
                if p1 in squad:
                    self._sort_xi(side)
                    break
        if p1 and template in HOLDER_P1:
            self.holder = p1          # 2AA3: the line's p1 is the ball holder
        elif p2 and template in HOLDER_P2:
            self.holder = p2           # 2AD4: the line's p2 is the ball holder

    def apply_lines(self, lines):
        """`lines`: an iterable of (template, p1, p2) in ring order.

        A template-65 "challenge by" line nets 0 (the table's −10 plus 56CB's +10) when the
        invocation ran to 56CB. Decided, in order: (1) the FOLLOWING line is one of 5565's
        visible bail lines (CHALLENGE_BAIL) — bailed, plain −10; (2) the duel's holder —
        the line's p2 when it carries one (a real 2B28 line stores 0), else the tracked
        holder — stands on a side's slot 1 (045D at 5692: pitch slot 1 or 12) — the silent
        bail, plain −10; (3) the follower exists and is not a bail line and the holder is
        known and off slot 1 — completed, +10. Everything else — holder unknown, or the
        0x41 line last in its batch (a bail follower could still arrive in the next one) —
        is UNDECIDABLE from the log: recorded in `self.undecided`, no +10 applied, the
        number not asserted. The state (words, holder) carries across calls, so a log split
        at half time decides a 0x41 at the split only when its follower opens the second
        batch — which none of the E012 records has."""
        lines = list(lines)
        for i, (template, p1, p2) in enumerate(lines):
            self.apply_line(template, p1, p2)
            if template == CHALLENGE and p1:
                follower = lines[i + 1][0] if i + 1 < len(lines) else None
                if follower in CHALLENGE_BAIL:
                    continue                      # 5474/5513/4151 bailed, visibly
                holder = p2 or self.holder
                on_keeper = self._holder_on_keeper_slot(holder)
                if on_keeper is None:
                    self.undecided.append(
                        (p1, "the duel's holder is not named by the log"))
                    continue
                if on_keeper:
                    continue                      # 045D(830B): the silent bail at 5692
                if follower is None:
                    self.undecided.append(
                        (p1, "the 0x41 line is last in its batch; the follower could still bail"))
                    continue
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
