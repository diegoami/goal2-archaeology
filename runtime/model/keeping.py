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
  pitch-record halving flag, the UNSIGNED low-word product-and-divide (2814 `mul` / 2817 `xor
  dx, dx` / 281C `div` — no IDIV, no sign extension of the product), the **table-controlled
  keeper extra** at
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
import sys
from pathlib import Path

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
DUEL_AIR_MULTIPLIER = 2       # 5BDB: `shl ax, 1` — the air branch (DS:8303 set) doubles the
                              # challenger's keeping before the rand (5BD8 reads element 1, 5BDB x2)
DUEL_GROUND_BONUS = 1         # 5C23-5C31: the ground branch adds 0 or 1 (the [bp-7] != 0x0B flag)
DUEL_SAVE_JLE_OPCODE = 0x7E   # 5C3C: `jle 0x5C44` (cmp ax, dx at 5C3A). `jle` jumps to no-save when
                              # challenger <= holder, so the keeper saves exactly when challenger >
                              # holder. A mutated `jl` (0x7C) widens the save to >= and flips the
                              # equal boundary; `jbe` (0x76) coincides with `jle` for the non-negative
                              # draws. The duel model below (`duel_contests` / `keeper_saves`) USES
                              # these three constants so a mutation of any one fails a test.

# --- 0791:1D4A (seg_0791_03.asm:1D4A-1E50) — the commentary ring write ---------------------
# A commentary line is written at 1DC1 `mov byte ptr es:[di], al` (template), reached only after
# the 1C78 dedup predicate passes (1D54-1D63); 1E46 `mov byte ptr [bp-1], 1` marks the write and
# is the point the emulation hooks to count an ACCEPTED line (the template is still [bp+4] there).
COMMENTARY_WRITE_OFF = 0x1E46

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


def _contest_product(base, skill):
    """`0791:278A`'s value product-and-divide (2805-281E), exactly as the listing computes it.

    `mov ax, [bp-6]; xor dx, dx; mov cx, 4; div cx` (2805-280D, UNSIGNED) puts bx = skill / 4
    (skill is non-negative, so this is an ordinary floor). `mov ax, [bp-4]; mul word ptr [bp-6]`
    (2811-2814) is the UNSIGNED 16x16 multiply base x skill — base is the SIGNED form/energy
    blend (27AB-27D9), so a negative base is its two's-complement word. `xor dx, dx` (2817)
    DISCARDS the product's high word; `mov cx, 0x100; div cx` (2819-281C, UNSIGNED) divides the
    low word by 256; `add ax, bx` (281E) adds the skill/4 quarter.

    There is no IDIV and no sign extension of the product. The value is therefore
    `((base * skill) & 0xFFFF) // 256 + skill // 4` — NOT `int(base * skill / 256) + skill // 4`,
    which truncates toward zero and drops the borrow for a negative base (the review's
    +4=180, +5=1, +7=0, form=0, energy=0xFE, element=1 example: base -1, skill 147,
    listing ((−147) & 0xFFFF) // 256 + 36 = 255 + 36 = 291; the old truncation gave 36)."""
    return ((base * skill) & 0xFFFF) // CONTEST_DIVISOR + (skill // CONTEST_QUARTER)


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
    # 2805-281E: the product-and-divide is UNSIGNED (`mul` at 2814, `xor dx, dx` at 2817 discards
    # the high word, `div cx` at 281C divides the low word) — see _contest_product.
    value = _contest_product(base, skill)
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


def duel_contests(challenger_record, holder_record, class_table, profile_table, ground=True):
    """The two contest values `0791:5B36`'s save duel draws against (seg_0791_10.asm:5BAD-5C3C).

    The challenger's contest is `278A(challenger, DUEL_KEEPER_ELEMENT)` (element 1 = keeping, read
    at 5BD8/5C1A); the holder's is `278A(holder, DUEL_HOLDER_ELEMENTS[0 if ground else 1])`
    (element 10 dribbling on the ground at 5BC4, element 4 heading in the air at 5C06). A record
    is the player's 20 bytes: record[4]=+4, [5]=+5, [7]=+7, [0xC]=form, [0xE]=energy. The
    constants DUEL_KEEPER_ELEMENT and DUEL_HOLDER_ELEMENTS are USED here, so mutating either one
    changes the returned contests and fails the tests that pin them."""
    ch = contest_value(plus4=challenger_record[4], plus5=challenger_record[5],
                       plus7=challenger_record[7], plus_c=challenger_record[0xC],
                       plus_e=challenger_record[0xE], element=DUEL_KEEPER_ELEMENT,
                       class_table=class_table, profile_table=profile_table)
    hh = contest_value(plus4=holder_record[4], plus5=holder_record[5],
                       plus7=holder_record[7], plus_c=holder_record[0xC],
                       plus_e=holder_record[0xE],
                       element=DUEL_HOLDER_ELEMENTS[0 if ground else 1],
                       class_table=class_table, profile_table=profile_table)
    return ch, hh


def duel_operand(contest, ground):
    """The challenger's draw operand after the element is applied: the air branch doubles the
    contest (`shl ax, 1`, 5BDB, DUEL_AIR_MULTIPLIER), the ground branch adds DUEL_GROUND_BONUS when
    the tackle flag is clear (5C23-5C31)."""
    return contest + (DUEL_GROUND_BONUS if ground else 0) if ground else contest * DUEL_AIR_MULTIPLIER


def keeper_saves(challenger_draw, holder_draw, jle_opcode=DUEL_SAVE_JLE_OPCODE):
    """The save duel's comparison (5C3A-5C3E: `cmp ax, dx; jle 0x5C44`). With the actual opcode
    `jle` (0x7E, DUEL_SAVE_JLE_OPCODE) the jump to no-save fires when challenger <= holder, so the
    keeper saves exactly when challenger > holder (strict). A mutated `jl` (0x7C) jumps only when
    challenger < holder and so saves on >= (the equal boundary flips); `jbe` (0x76) coincides with
    `jle` for the non-negative draws. The constant is USED here, so a mutation fails the test that
    pins the equal draw as a no-save."""
    if jle_opcode in (0x7E, 0x76):      # jle / jbe: save iff challenger > holder
        return challenger_draw > holder_draw
    if jle_opcode == 0x7C:              # jl: save iff challenger >= holder (a mutation)
        return challenger_draw >= holder_draw
    raise ValueError(f"unexpected duel jle opcode 0x{jle_opcode:02x}")


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


def _emulation_cls(emulation_cls):
    """Resolve the emulation class: the caller may pass a swap (a fake for the test suite);
    otherwise load the real `watched.WatchedHalf`. The import is local to keep the model
    importable on its own."""
    if emulation_cls is not None:
        return emulation_cls
    try:
        from watched import WatchedHalf   # local import: the emul harness is heavy
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "emul"))
        from watched import WatchedHalf
    return WatchedHalf


def keeper_save_predictions(savestate_bytes, new4, edited_keeping, emulation_cls=None):
    """What the E013 keeper-edit runs are checked against (the watched engine only; the quick
    engine reads no derived skill, F012). R2 fix: a SAVESTATE-DERIVED prediction, not an
    observed-outcome flag. R2 follow-up: the emulation class is an injectable parameter so the
    test suite can substitute a fake and assert the predictor's return depends on the emulation.

    For `new4 = 0x00` (keeping value = 0), the derivation is purely analytical: every save duel
    in `0791:5B36` (seg_0791_10.asm:5BC4-5C3E) draws the challenger's rand as
    `u214b_random_1_to_n(0)`, which is `((seed * 0) >> 16) + 1 = 1` for every seed. The holder's
    rand is at least 1 (positive n), so the duel always loses: 0 saves. A "0 saves" prediction
    is derived from the listing, not from the baseline's count.

    For `new4 > 0`, the count depends on the actual seed draws; without running the engine we
    cannot enumerate them, so the prediction asks for the actual emulation: the check
    `check_keeping.py` runs `runtime/emul/watched.py` over the half-time-edit savestate and
    counts saves via a hook on `0791:5A8E` (the template-29 writer, `write_save_line`).

    `savestate_bytes` may be None for the LOW edit (the analytical derivation covers it).
    `emulation_cls` may be a fake class for the test suite; the model returns its result."""
    if edited_keeping == 0:
        # Every save duel the keeper enters, his rand = 1 and the holder's rand >= 1: the keeper
        # cannot win a single duel. The derivation is independent of the seed.
        return {"saves_at_most": 0, "saves_at_least": 0, "saves_count": 0,
                "analytical_derivation": True}
    if savestate_bytes is None:
        return {"requires_state": "edit not 0x00 — the count is seed-dependent; emulate the half-time-edit savestate via runtime/emul/watched.py and hook 0791:5A8E"}
    Emul = _emulation_cls(emulation_cls)
    with_saves = Emul(savestate_bytes).run()
    n = with_saves.save_calls
    return {"saves_count": n, "saves_at_least": n, "saves_at_most": n,
            "goal_count": with_saves.goal_calls,
            "ticks": with_saves.ticks, "draws": len(with_saves.draws),
            "score": with_saves.final.get("score", [0, 0]),
            "analytical_derivation": True, "emulated": True,
            "emulation_cls_used": getattr(Emul, "__name__", str(Emul))}


def outfield_edit_predictions(savestate_bytes, new4, edited_keeping_before, edited_keeping_after,
                              emulation_cls=None):
    """R2 fix: an outfield player's +4 edit shifts his derived values by ((new4)+1)/((old4)+1)
    for every element (`3A06` reads +4 for all twelve); the only outcomes that change are the
    duels whose RAND operands flip — a comparison whose operands (the rand draws) and threshold
    (the holder's rand range) change. With the edited keeping differing from the original by
    only a small fraction (`(new4+1)/(old4+1)` is close to 1), most comparison outcomes do not
    flip; whether they do depends on where the actual draws land.

    R3 fix: the prediction returns the EDITED state's full event fingerprint (lines counted via
    the `tick` hook at 0791:970C, draws counted via the LCG hook at 214B:0688, saves via 0791:5A8E,
    goals via 0791:6443, and the final score). The check `check_keeping.py` consumes this and
    asserts equality with the unedited baseline's fingerprint; the line-log record equality
    alone is not the prediction.

    `emulation_cls` may be a fake class for the test suite; the model returns its result."""
    Emul = _emulation_cls(emulation_cls)
    run = Emul(savestate_bytes).run()
    return {
        "saves_count": run.save_calls,
        "goal_count": run.goal_calls,
        "ticks": run.ticks,
        "draws": len(run.draws),
        "score": run.final.get("score", [0, 0]),
        "event_counts": (run.ticks, run.goal_calls, run.save_calls),
        "edited_keeping_before": edited_keeping_before,
        "edited_keeping_after": edited_keeping_after,
        "emulated": True,
        "emulation_cls_used": getattr(Emul, "__name__", str(Emul)),
    }
