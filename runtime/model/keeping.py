#!/usr/bin/env python3
"""Where keeping is read and where penalties are read in GOAL.EXE's match engines (T27, Q012; E013).

The player record holds no twelve skills (F008): each is computed. The player screen's bar painter
`1771:3947` divides by 256 (seg_1771_05.asm:39C1 `mov cx, 0x100`); the engines reach the SAME
derivation through another routine, `1771:3A06(player, element)` (seg_1771_05.asm:1032-3A7F), which
divides by 32 instead (`3A71 mov cx, 0x20`, seg_0791_05.asm:3A71 — same lines, listing file
seg_1771_05.asm:1070-1071). `3A06` has exactly one caller in calls.tsv: `0791:278A` — the engine's
skill reader. So no engine reads a stored keeping or penalties byte, and every skill read of a
match goes through `278A(pitch_record, element)` (seg_0791_04.asm:846-2879), which blends the
derived skill with the player's form and energy.

This module is that reading as code, with the listing line per constant, plus the predictor the
E013 records check (`check_keeping.py`):

- `skill_value` — `1771:3A06`: `DS:6DCD[12*+5 + DS:6D25[12*+7 + element]] * ((+4) + 1) div 32`;
- `contest_value` — `0791:278A`: form base, the element >= 0xC penalty bonus, energy, the
  pitch-record halving flag, the goal-mouth product, the event-0x18 keeper extra and the
  manager's `80FC` share;
- `keeper_save_predictions` / `outfield_edit_predictions` — the watched-engine predictions the
  runs corroborate: every `saved by` line names a goalkeeper (`5A8E`, the template-29 writer, is
  reached from `5B36`'s duel, where the challenger's element 1 is read against the holder's
  element 10 or 4, seg_0791_10.asm:5BC4-5C1E), and an I3 edit of +4 shifts the derived values
  linearly, so a keeper edited to +4 = 0x00 keeps with value 0 and saves less, and any player's
  +4 edit feeds every later skill read (`3A06` reads +4 for all twelve elements).

The tables `DS:6D25` (14 positions x 12 classes) and `DS:6DCD` (16 profiles x 12 classes) are
initialised data, NOT part of the record: a prediction from a savestate must read them from that
savestate (F008's hazard; here they arrive as arguments). Standard library only.
"""

# --- 1771:3A06 (seg_1771_05.asm:1032-3A7F) -------------------------------------------
SKILL_DIVISOR = 32            # 3A71-3A74: mov cx, 0x20; div cx  (3947, the screen's painter, uses 0x100 at 39C1)
SKILL_STRIDE = 12             # 3A3D/3A57: mul dx with dx = 0xC — both tables have 12-column rows

# --- 0791:278A (seg_0791_04.asm:846-2879) --------------------------------------------
FORM_CAP = 0x20               # 27AB: cmp byte ptr es:[di + 0xc], 0x20 / jge 27c0 — form >= 0x20 counts 0
PENALTY_ELEMENT = 0xC         # 27C5: cmp word ptr [bp + 0xa], 0xC — element 12 (penalties) and above
PENALTY_BONUS = 0x20          # 27CB-27CF: add word ptr [bp - 4], 0x20 — the base bonus of a penalty contest
CONTEST_DIVISOR = 0x100       # 2819-281C: div cx with cx = 0x100 — base * skill / 256
CONTEST_QUARTER = 4           # 280A-280D: div cx with cx = 4 — plus skill / 4
KEEPING_EVENT = 0x18          # 2837: the set CS:276A = {0x18} (seg_0791_04.asm:843) — the goal-mouth event
KEEPING_ELEMENT = 1           # 282D: cmp word ptr [bp + 0xa], 1 — the extra term is keeping-only
KEEPING_TABLE = 0x769         # 2826: cmp byte ptr [di + 0x769], 0 — the gate's table column (element 1 holds 0)
PITCH_HALVED = 0x13           # 27F1: cmp byte ptr es:[di + 0x13], 0 — set halves the derived skill
MANAGER_SHARE = 0x10          # 2865-286A: div 0x10; add — the 80FC bonus adds skill/16 for outfield slots
OUTFIELD_SLOT = 0xC           # 2852: cmp byte ptr es:[di + 6], 0xC — the pitch record's slot/address byte

# --- 0791:5B36 (seg_0791_10.asm:5BC4-5C1E) — the duel whose win writes template 29 ----
# The challenger's keeping (element 1, 5BD8/5C1A) against the holder's dribbling (element 10,
# 5BC4) or heading (element 4, 5C06); the winner's branch goes to 5A8E (template 0x1D = 29,
# `saved by`, seg_0791_04.c named view 1003-1022). 0791:9ED3 ranks shoot-out takers by
# 278A(pitch, 0xC) (seg_0791_16.asm:9F6A/9F9F) — the only element-12 caller, inside A10A.
SAVE_TEMPLATE = 29
DUEL_KEEPER_ELEMENT = 1
DUEL_HOLDER_ELEMENTS = (10, 4)

# The quick engine (0791:D733 -> 1771:0BC4 -> B19D) reads NO derived skill: its four line sums
# are 377E(w) = ability-based strengths routed by DS:0D4E[+6] (F012); 278A/3A06 appear nowhere
# under D733 (calls.tsv: 278A's callers are 1FDD, 287C, 34C1, 3B15, 3EF8, 47C5, 5474, 5B36,
# 690C, 9ED3, D5C1 — D5C1's two use elements 3 and 10).


def skill_value(plus4, plus5, plus7, element, class_table, profile_table):
    """`1771:3A06`: the derived skill `element` (1 = keeping ... 12 = penalties) of a player whose
    record holds +4 (scale), +5 (profile 1..16) and +7 (club position 0..13).

    class_table is the 168 bytes at DS:6D25 (14 positions x 12 elements), profile_table the 192
    bytes at DS:6DCD (16 profiles x 12 classes); both are read from the same savestate as the
    record (they are initialised data, not record bytes; F008)."""
    c = class_table[SKILL_STRIDE * plus7 + element]                      # 3A37-3A46
    row = profile_table[SKILL_STRIDE * plus5 + c]                        # 3A51-3A60
    return (row * (plus4 + 1)) // SKILL_DIVISOR                          # 3A2C inc; 3A6C mul; 3A71 div 32


def contest_value(plus4, plus5, plus7, plus_c, plus_e, element, class_table, profile_table,
                  pitch_13=0, pitch_11=0, event_code=0, flag_80fc=0, pitch_6=0):
    """`0791:278A(pitch_record, element)`: the value a match contest draws against
    (`rand(contest)` at the call sites, or `/32 + 1` inside `0791:287C`).

    plus_c is the player's form byte +0xC, plus_e the energy byte +0xE; pitch_13 the pitch
    record's halving flag, pitch_11 its keeper extra byte, event_code `DS:8327`, flag_80fc
    `DS:80FC` and pitch_6 the pitch record's slot/address byte."""
    base = (plus_c + 1) if plus_c < FORM_CAP else 0                      # 27AB-27C2
    if element >= PENALTY_ELEMENT:
        base += PENALTY_BONUS                                            # 27C5-27CF
    else:
        base += plus_e                                                   # 27D1-27D9 (signed in the listing)
    skill = skill_value(plus4, plus5, plus7, element, class_table, profile_table)
    if pitch_13:
        skill //= 2                                                      # 27F1-2802
    value = (base * skill) // CONTEST_DIVISOR + skill // CONTEST_QUARTER  # 2805-281E
    if element == KEEPING_ELEMENT and event_code == KEEPING_EVENT:
        value += pitch_11                                                # 2823-284C (0x769[1] == 0 in the data image)
    if pitch_6 < OUTFIELD_SLOT and flag_80fc:
        value += value // MANAGER_SHARE                                  # 284F-286A
    return value


def keepers_of(squad):
    """The squad words the engines treat as keepers: squad word 1 (the side's pitch slot
    `0668[side] + 1`, seg_0791_15.asm:960E-9620 picks record slot 1 for the keeper special)."""
    return squad[0]


def predict_edited_values(plus4, plus5, plus7, element, class_table, profile_table, new4):
    """The derived values before and after an I3 edit of +4. The derivation is linear in
    (+4)+1 (`3A2C`'s inc), so the value scales by ((new4)+1)/((plus4)+1); new4 = 0x00 leaves the
    floor (+4)+1 = 1. Element 1 of a goalkeeper (+7 = 0, whose class column is 1) is the value
    the save duels draw against."""
    return (skill_value(plus4, plus5, plus7, element, class_table, profile_table),
            skill_value(new4, plus5, plus7, element, class_table, profile_table))


def keeper_save_predictions(baseline_saves_second_half, new4):
    """What the E013 keeper-edit runs are checked against (the watched engine only; the quick
    engine reads no derived skill, F012).

    - the keeper's keeping value after the edit (exact, `skill_value` with the record's own
      +5/+7 and the savestate's tables);
    - with +4 edited to 0x00 the keeper's keeping value is 0 (profile row [+5] class 1 is
      23..26, times 1 div 32 = 0), so every save duel he enters is drawn as
      rand(1..2) against rand(holder element 10) (seg_0791_10.asm:5BC4-5BE8): he saves strictly
      less than the baseline's second half;
    - with +4 edited to 0xFF his value rises by (0x100)/(plus4+1), at least a third over the
      180..253 the new game gives (F008), so the second half is not the baseline replay: its
      line log differs (the draws change, F004/F005's determinism makes an unchanged log the
      only alternative);
    - every `saved by` line names a player of the conceding side whose derived keeping is
      among that side's stronger values: template 29's writer `5A8E` is reached from `5B36`'s
      duel on the challenger, and the read is NOT gated by position — an outfield challenger's
      keeping class column is 7, 11 or 12 (values up to ~73% of a goalkeeper's at the same
      +4), so a defender on the goal line can win a save duel too (F015's answer to Q012).
    """
    if new4 == 0x00:
        return {"saves_below_baseline": True, "threshold": baseline_saves_second_half,
                "saves_at_most": baseline_saves_second_half - 1}
    return {"saves_below_baseline": False, "line_log_differs_from_baseline": True}


def outfield_edit_predictions():
    """A non-keeper's +4 edit (the I3 edit of E013's outfield arm). `3A06` reads +4 for EVERY
    element, so the edited player's derived values all shift (exactly, by ((new4)+1)/((plus4)+1))
    — but the RNG chain position is value-independent (`214B:0688` steps once per `rand(n)` call
    whatever n is, F012), so the edit changes an outcome ONLY where a shifted value flips a
    comparison. The prediction the E013 record checks: the second half's line log is the
    baseline's (no comparison flipped) — corroborated by E013-r0003 (507 lines, 0 goals, 3
    saves, the baseline's own counts), while the keeper's edits DID flip his goal-mouth duels
    (E013-r0001/r0002). A flip is possible in principle (the drawn comparison operands change),
    so "no change" is this match's answer, not a law; the finding says so."""
    return {"line_log_unchanged": True, "values_change": True}
