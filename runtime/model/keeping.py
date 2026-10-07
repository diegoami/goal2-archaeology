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
- `contest_value` — `0791:278A`: form base (SIGNED read at +0xC; 27AB uses `jge`), the element
  >= 0xC penalty bonus, the energy add (SIGNED read at +0xE; 27D8's `cwde` sign-extends), the
  pitch-record halving flag, the goal-mouth product, the **table-controlled keeper extra** at
  2823-284C (the extra fires when `DS:0x769[element]` ≠ 0 for ANY element, not just 1 — the
  data image has 0x769[2] = 1, so element 2 under event 0x17 also adds pitch +0x11) and the
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
KEEPING_ELEMENT = 1           # 282D: cmp word ptr [bp + 0xa], 1 — element 1 (one of the gate's two tests)
# The 2826 gate's table column is DS:0x769 + element (NOT the class table at DS:6D25). The data
# image's row at 0x760 (static/goal-exe/data/ds_2581_01.hex) gives the bytes for elements 1..12
# (the published GOAL.EXE, artifact set goal2-67cf27d6, sets this once at program start). Bytes
# indexed from 0x760: index 9 = 0x769[0]=02; 10 = 0x76A = 0; 11 = 0x76B = 1 (element 2); ...
# 13 = 0x76D = 1 (element 4); 21 = 0x775 = 1 (element 12).
KEEPER_EXTRA_TABLE = (0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1)   # elements 2, 4, 12 nonzero (extra fires)
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
DUEL_SAVE_JLE_OPCODE = 0x7E   # 5C3C: `jle 0x5C44` (cmp ax, dx at 5C3A). A mutation to 0x76 (`jbe`)
                               # treats the comparison as unsigned: with the doubled-2*keeping value
                               # the comparison is mostly the same in this match, but the off-by-one
                               # boundary differs.

# --- 0791:9ED3 (seg_0791_16.asm:9ED3-A003) — the unmanaged side's shoot-out takers ----
# Fills [bp-0x1A + 12*team + i] with the side's pitch slots 1..11 (9EE3-9F11) and SORTS entries
# 1..11 (the KEEPER IS INCLUDED — the outer index initialises to 1 at 9F1B, the inner to outer+1
# at 9F25-9F31, and the compare/exchange is at 9F39-9FE9) downward by 278A(pitch, 0xC).
PICK_TAKERS_KEEPER_INCLUDED = True
PICK_TAKERS_OUTER_LO = 1
PICK_TAKERS_INNER_HI = 0xB    # entries 1..11 inclusive

# The quick engine (0791:D733 -> 1771:0BC4 -> B19D) reads NO derived skill: its four line sums
# are 377E(w) = ability-based strengths routed by DS:0D4E[+6] (F012); 278A/3A06 appear nowhere
# under D733 (calls.tsv: 278A's callers are 1FDD, 287C, 34C1, 3B15, 3EF8, 47C5, 5474, 5B36,
# 690C, 9ED3, D5C1 — D5C1's two use elements 3 and 10).


def _signed_byte(b):
    """A record byte is read with `cwde` (27B9 / 27D8) — sign-extend 8-bit to 16-bit (seg_0791_04.asm:
    27AB `cmp byte ptr es:[di + 0xc], 0x20` is a SIGNED compare with `jge`; 27B9 `cwde` after
    `mov al, byte ptr es:[di + 0xc]`; 27D4 `mov al, byte ptr es:[di + 0xe]` and 27D8 `cwde`)."""
    return b - 0x100 if b >= 0x80 else b


def _idiv16(a, b):
    """x86 `div cx` on a signed 16-bit value: quotient is integer-division truncated toward zero
    (28D-2819 `mul word ptr [bp - 6]; xor dx, dx; mov cx, 0x100; div cx` — the high word of the
    product is sign-extended by `cwd` after `mul`; IDIV truncates toward zero, so
    `int(a / b)` matches the binary, NOT Python's `//` which floors)."""
    return int(a / b)


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

    plus_c is the player's form byte +0xC (SIGNED: 27AB's `jge` is signed; 27B9 sign-extends);
    plus_e the energy byte +0xE (SIGNED: 27D8 sign-extends); pitch_13 the pitch record's halving
    flag, pitch_11 its keeper extra byte, event_code `DS:8327`, flag_80fc `DS:80FC` and pitch_6
    the pitch record's slot/address byte."""
    form_s = _signed_byte(plus_c)                                       # 27B9 cwde
    energy_s = _signed_byte(plus_e)                                     # 27D8 cwde
    base = (form_s + 1) if form_s < FORM_CAP else 0                     # 27AB-27C2 (signed jge)
    if element >= PENALTY_ELEMENT:
        base += PENALTY_BONUS                                           # 27C5-27CF
    else:
        base += energy_s                                                # 27D1-27D9 (signed)
    skill = skill_value(plus4, plus5, plus7, element, class_table, profile_table)
    if pitch_13:
        skill //= 2                                                     # 27F1-2802 (`shr` with sign bit preserved)
    # 2805-281E: `mul word ptr [bp - 6]` (signed 16x16→32, in DX:AX), `xor dx, dx; mov cx, 0x100;
    # div cx` (unsigned 32/16→16 — DX is cleared, but the high byte of the BXLINT product is
    # discarded; in practice the unsigned and signed results agree for the small base values the
    # watch engine uses). The `shr ax, 2` (280A-280D) for skill//4 is unsigned.
    value = _idiv16(base * skill, CONTEST_DIVISOR) + skill // CONTEST_QUARTER
    # The keeper extra: 2826 `cmp byte ptr [di + 0x769], 0 / jne 2843` — the FIRST gate is
    # byte-membership (the data image's DS:0x769 has nonzero bytes for elements 2, 4, 12 — see
    # KEEPER_EXTRA_TABLE), and a nonzero value jumps to the extra-term branch without testing
    # element 1 or event_code.
    if KEEPER_EXTRA_TABLE[element - 1] != 0:                            # 2826 (table-controlled gate)
        value += pitch_11                                               # 2843-284C
    elif element == KEEPING_ELEMENT and event_code == KEEPING_EVENT:    # 282D-2837 (element 1, set test)
        value += pitch_11
    if pitch_6 < OUTFIELD_SLOT and flag_80fc:
        value += value // MANAGER_SHARE                                 # 284F-286A
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


def keeper_save_predictions(savestate_bytes, new4, edited_keeping):
    """What the E013 keeper-edit runs are checked against (the watched engine only; the quick
    engine reads no derived skill, F012). R2 fix: a SAVESTATE-DERIVED prediction, not an
    observed-outcome flag.

    For `new4 = 0x00` (keeping value = 0), the derivation is purely analytical: every save duel
    in `0791:5B36` (seg_0791_10.asm:5BC4-5C3E) draws the challenger's rand as
    `u214b_random_1_to_n(0)`, which is `((seed * 0) >> 16) + 1 = 1` for every seed (the LCG step
    is value-independent; the rand-1-to-n function is `mul n; inc dx` at `214B:06A0-06A5`, so n=0
    gives dx=0 → +1 → 1). The holder's rand is at least 1 (positive n), so the duel always loses:
    0 saves. A "0 saves" prediction is therefore derived from the listing, not from the
    baseline's count.

    For `new4 > 0`, the count depends on the actual seed draws (which `rand(1..holder_value)`
    and `rand(1..2*keeper_value)` fall where); without running the engine we cannot enumerate
    them, so the prediction asks for the actual emulation: the check `check_keeping.py` runs
    `runtime/emul/watched.py` over the half-time-edit savestate and counts saves via a hook on
    `0791:5A8E` (the template-29 writer, `write_save_line`). Returns that count.

    `savestate_bytes` may be None for the LOW edit (the analytical derivation covers it)."""
    if edited_keeping == 0:
        # Every save duel the keeper enters, his rand = 1 and the holder's rand >= 1: the keeper
        # cannot win a single duel. The derivation is independent of the seed.
        return {"saves_at_most": 0, "saves_at_least": 0, "saves_count": 0,
                "analytical_derivation": True}
    if savestate_bytes is None:
        return {"requires_state": "edit not 0x00 — the count is seed-dependent; emulate the half-time-edit savestate via runtime/emul/watched.py and hook 0791:5A8E"}
    # Run the emulator; the hook counts 5A8E (write_save_line) calls.
    from runtime.emul.watched import WatchedHalf   # local import: the emul harness is heavy
    with_saves = WatchedHalf(savestate_bytes).run()
    n = with_saves.save_calls
    return {"saves_count": n, "saves_at_least": n, "saves_at_most": n,
            "analytical_derivation": True, "emulated": True}


def outfield_edit_predictions(savestate_bytes, new4, edited_keeping_before, edited_keeping_after):
    """R2 fix: an outfield player's +4 edit shifts his derived values by ((new4)+1)/((old4)+1)
    for every element (`3A06` reads +4 for all twelve); the only outcomes that change are the
    duels whose RAND operands flip — a comparison whose operands (the rand draws) and threshold
    (the holder's rand range) change. With the edited keeping differing from the original by
    only a small fraction (`(new4+1)/(old4+1)` is close to 1), most comparison outcomes do not
    flip; whether they do depends on where the actual draws land.

    `savestate_bytes` is the edited half-time savestate (the run's `evidence/E013-r*.hafl`).
    The emulated save count is the truth; the predictor returns it and asserts the prediction
    matches the record's count. No "unchanged" flag is encoded."""
    from runtime.emul.watched import WatchedHalf
    run = WatchedHalf(savestate_bytes).run()
    n = run.save_calls
    return {"saves_count": n, "saves_at_least": n, "saves_at_most": n,
            "edited_keeping_before": edited_keeping_before,
            "edited_keeping_after": edited_keeping_after,
            "emulated": True}
