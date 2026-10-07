#!/usr/bin/env python3
"""How a player's record changes at the year end, and what his peak age does (T28, Q013; E014).

The yearly loop (experiments/E014-q013-ageing/notes.md, every constant with its listing line):
`000E:70B9` (play_round) -> `1771:8208` (stage end: the stage byte `[A923]+0x3C` wraps +1 in
[2,8] via `214B:1D6F`, seg_1771_12.asm:143-155; the ageing gate is the set CS:81E8 = {2,3,5,7},
data row seg_1771_12.asm:118, tested at :156-163) -> `1771:80DA` (all 128 countries,
seg_1771_12.asm:17-30; the year word `[A923]+0x38` increments only for the set CS:80BA = {2,5},
data row seg_1771_11.asm:1115) -> `1771:7FDF` per country (seg_1771_11.asm:1021-1112) ->
`1771:7FB1` per player (:1001-1018) -> `1771:7E4A` (:845-868): age +1 (`7E6F inc byte ptr
es:[di + 1]`, :861; player 0 is skipped, `7E64`, :856) then `compute_ability` `1771:32EB`;
`7FB1` also zeroes +0x11 unconditionally (`7FD4`, :1015 — the byte's only writer in the whole
program, and no reader: notes.md section 2).

The peak-age rule is `compute_ability` `1771:32EB` (seg_1771_05.asm:283-370): with a = +1,
p = +2, r = +3, the band p <= a <= p + 3 gives +4 = r (:296-312); below it k = (p - a) idiv 2
(SIGNED, `33A7 idiv cx`, :348-361); above it k = a - (p + 3) (:337-347); then factor = 0x10 - k
as a 16-bit word (wraps when k > 16, `3386`/`33AE`) and +4 = low byte of
((r * factor) mod 65536) div 16 — `33B6 mul` unsigned, `33B9 xor dx, dx` discards the high
product, `33BE div cx` with cx = 0x10 (:362-366).

For a COMPUTER country the loop then tests retirement `1771:7F40` (:950-1000) and re-creates
the retiree `1771:7E80` (:871-948); the predicate is deterministic —
(DS:110E[gk] < a AND caps == 0) OR a > p + 5, gk = (+7 == 0), DS:110E = 1E 21
(data/ds_2581_01.hex:143) — but the re-create is all RNG (make_player + two rand(6) + the
name byte; Q014), so a replaced player's new bytes are NOT predicted here. For a MANAGED
country the loop ages the manager's 80 pool players instead (base DS:6D18[+0x2E-0x80], indices
[A927], :1050-1085) and runs no retirement test; the menu's offer path (000E:57E5/56F3/54F0)
is RNG-selected and also out of scope.

The yearly path consumes NO RNG (calls.tsv: 8208/80DA/7FDF/7FB1/7E4A/32EB/7F40 call no random
routine), so the `seed` argument of `ageing_value` is accepted for the task's signature and
never consumed: the predicted bytes of a continuing player are a pure function of its record.
The year-to-year variance between players is the creation draw (+2 by roll_peak_age 1771:3291:
DS:0E80[gk] + rand(3) - rand(3), DS:0E80 = 1B 1E; +3 by make_player), not a yearly draw.

The engines read the twelve skills as DS:6DCD[12*(+5) + DS:6D25[12*(+7) + e]] * ((+4)+1) div 32
(1771:3A06, F015); the loop changes only +4 of the three inputs, so `derived_skills` here gives
the before/after of all twelve from the same two tables (initialised data, read from the
savestate — F008's hazard; they arrive as arguments, as in runtime/model/keeping.py).
Standard library only.
"""

# --- the record's bytes (F008; annotations/fields.tsv) -----------------------------------
AGE = 0x01            # 7E6F: inc byte ptr es:[di + 1]
PEAK = 0x02           # 330F/3318/3350/336B/339B: es:[di + 2] — read, never written, in the loop
RATING = 0x03         # 3333/3344: es:[di + 3] — the ceiling r
ABILITY = 0x04        # 333A/33C3: es:[di + 4] — compute_ability's only write
CLUB_POSITION = 0x07  # 7F5D/32C3: es:[di + 7] == 0 is the goalkeeper test
CAPS = 0x08           # 7F7D: cmp word ptr es:[di + 8], 0 — the retirement test's caps word
DEAD_BYTE = 0x11      # 7FD4: mov byte ptr es:[di + 0x11], 0 — the loop's third write

# --- compute_ability 1771:32EB (seg_1771_05.asm:283-370) ----------------------------------
PEAK_BAND = 3         # 331E/3356/3371: add ax, 3 — the band is p..p+3 (four ages)
BELOW_DIVISOR = 2     # 33A4-33A7: mov cx, 2; idiv cx — SIGNED (cdq at 33A3), floor for p > a
FACTOR_BASE = 0x10    # 3383/33AB: mov ax, 0x10 — factor = 0x10 - k, a 16-bit word (wraps)
ABILITY_DIVISOR = 16  # 33BB-33BE: mov cx, 0x10; div cx — UNSIGNED, after `xor dx, dx` (33B9)

# --- retirement 1771:7F40 (seg_1771_11.asm:950-1000; DS:110E = 1E 21, ds_2581_01.hex:143) --
RETIRE_LIMIT = (0x1E, 0x21)   # 7F6D: [di + 0x110e] indexed by (+7 == 0): 30 outfield, 33 keeper
RETIRE_PEAK_MARGIN = 5        # 7F8D: add ax, 5 — retires when a > p + 5

# --- derived skills 1771:3A06 (F015; seg_1771_05.asm, div 32 at 3A71-3A74) ----------------
SKILL_DIVISOR = 32    # 3A71-3A74: mov cx, 0x20; div cx (the screen's 3947 divides by 256, F008)
SKILL_STRIDE = 12     # 3A3D/3A57: both tables have 12-column rows
SKILL_ELEMENTS = 12   # the twelve elements 0..11 (F015)


def compute_ability(age, peak, rating):
    """`1771:32EB`: the ability byte +4 from +1/+2/+3, exactly as the listing computes it.

    Inside the band peak..peak+PEAK_BAND the ceiling is copied (3330-333A); outside, k is the
    half-distance below (idiv 2, 338D-33B0) or the distance above (3368-3388), factor = 0x10 - k
    wraps as a 16-bit word when k > 16 (3386/33AE), and the product is taken mod 65536 before
    the unsigned divide by 16 (33B6 mul, 33B9 xor dx,dx, 33BE div cx) with only al stored
    (33C3)."""
    if peak <= age <= peak + PEAK_BAND:          # 3308-332E: jb at 3313, jg at 332E
        return rating & 0xFF                     # 3330-333A: +4 = +3
    if age > peak + PEAK_BAND:                   # 3364-3366: cmp a, p+3; jle skips
        k = age - (peak + PEAK_BAND)             # 3368-3381 (16-bit, both small and positive)
    else:                                        # 338D-33A7: ax = p - a (33A1), cdq/idiv 2 —
        k = (peak - age) // BELOW_DIVISOR        # signed, and p > a in this branch (3313 jb)
    factor = (FACTOR_BASE - k) & 0xFFFF          # 3383-3388 / 33AB-33B0: a 16-bit word, wraps
    return (((rating & 0xFF) * factor) & 0xFFFF) // ABILITY_DIVISOR & 0xFF  # 33B3-33C3


def retirement_flag(record):
    """`1771:7F40`: 1 when the record retires, deterministic (no RNG in its callee set).

    (DS:110E[gk] < age AND the caps word == 0) OR age > peak + 5, gk = (record[+7] == 0)
    (7F5A-7F9D). Runs at the year end only for computer countries (7FDF's 0B77 branch); for the
    managed country the same predicate drives the RNG-selected menu offer path (Q014)."""
    gk = 1 if record[CLUB_POSITION] == 0 else 0  # 7F5D-7F6A
    caps = record[CAPS] | (record[CAPS + 1] << 8)  # 7F7D: cmp word ptr es:[di + 8], 0
    if RETIRE_LIMIT[gk] < record[AGE] and caps == 0:  # 7F74-7F82
        return 1
    return 1 if record[AGE] > record[PEAK] + RETIRE_PEAK_MARGIN else 0  # 7F87-7F9D


def ageing_value(record, year, class_table, profile_table, seed):
    """The per-byte new value of one year's ageing for a CONTINUING player (task signature).

    record: the 20 bytes at [A91B] + 20*n. year: the year-end's index (accepted for the record
    it annotates; the loop's writes do not read it). class_table: DS:6D25 (14 positions x 12
    rows), profile_table: DS:6DCD (16 profiles x 12 classes) — used only for the derived-skill
    report, from the SAME savestate (F008's hazard). seed: accepted, never consumed — the
    yearly path calls no RNG (notes.md section 3), which test_model_ageing pins.

    Returns {0x01: new age, 0x04: new ability, 0x11: 0, 'retires': flag, 'skills': (before,
    after)}; 'retires' is 7F40's predicate — when it fires for a computer country the record is
    re-created by 7E80 with RNG bytes this predictor does not model (Q014)."""
    new_age = (record[AGE] + 1) & 0xFF                    # 7E6F: inc byte, wraps at 255
    new_ability = compute_ability(new_age, record[PEAK], record[RATING])  # 7E77 call 32EB
    if class_table is None or profile_table is None:
        skills = None                    # the tables are a report, not an input to the writes
    else:
        skills = (derived_skills(record[ABILITY], record, class_table, profile_table),
                  derived_skills(new_ability, record, class_table, profile_table))
    return {AGE: new_age, ABILITY: new_ability, DEAD_BYTE: 0,   # 7FD4
            "retires": retirement_flag(record), "skills": skills}


def year_end_bytes(player, record, year=0, class_table=None, profile_table=None, seed=0):
    """`1771:7FB1(player)` (seg_1771_11.asm:1001-1018): the loop's per-player writes.

    7E4A skips player 0 (`7E64 cmp word ptr [bp + 4], 0` / `jne`, :856-858) — an empty squad
    slot still runs 7FB1's unconditional `+0x11 = 0` (`7FD4`, :1015) on record 0, and nothing
    else. For player >= 1 this is ageing_value's byte set."""
    if player == 0:
        return {DEAD_BYTE: 0}
    out = ageing_value(record, year, class_table, profile_table, seed)
    writes = {k: v for k, v in out.items() if isinstance(k, int)}
    writes["retires"] = out["retires"]
    return writes


def derived_skills(ability, record, class_table, profile_table):
    """`1771:3A06`: the twelve engine skill values for ability byte `ability` (F015).

    skill e = profile_table[12*(+5) + class_table[12*(+7) + e]] * (ability + 1) div 32."""
    out = []
    for e in range(SKILL_ELEMENTS):
        c = class_table[SKILL_STRIDE * record[CLUB_POSITION] + e]     # 3A37-3A46
        t = profile_table[SKILL_STRIDE * record[0x05] + c]            # 3A51-3A60
        out.append((t * ((ability + 1) & 0xFFFF)) // SKILL_DIVISOR)   # 3A66-3A74
    return tuple(out)
