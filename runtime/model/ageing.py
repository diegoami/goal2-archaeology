#!/usr/bin/env python3
"""How a player's record changes at the year end, and what his peak age does (T28, Q013; E014).

The yearly loop (experiments/E014-q013-ageing/notes.md, every constant with its listing line):
`000E:70B9` (play_round) -> `1771:8208` (stage end: the stage byte `[A923]+0x3C` wraps +1 in
[2,8] via `214B:1D6F`, seg_1771_12.asm:143-155; the ageing gate is the set CS:81E8 = {2,3,5,7},
data row seg_1771_12.asm:118, tested at :156-163) -> `1771:80DA` (all 128 countries,
seg_1771_12.asm:17-30; the year word `[A923]+0x38` increments only for the set CS:80BA = {2,5},
data row seg_1771_11.asm:1115) -> `1771:7FDF` per country (seg_1771_11.asm:1021-1112), in TWO
passes: the first (:1032-1045, the call at :1043) runs `1771:7FB1` on every squad word —
`7E4A` (:845-868): age +1 (`7E6F inc byte ptr es:[di + 1]`, :861; player 0 is skipped, `7E64`,
:856) then `compute_ability` `1771:32EB`; then `7FD4` (:1015) zeroes +0x11 unconditionally.
+0x11 is the player's count for the top-scorer table: `0791:B3B7` increments it per goal (`B3EC`,
seg_0791_18.asm:677) and reads it (`B446`/`B53B`/`B5E4`, :712/:814/:881); `7FD4` is its only
other access on a player record (notes.md section 2). The second pass (computer countries only,
:1086-1107) tests retirement `1771:7F40` (the call at :1098) on the record the first pass
already aged, and re-creates a retiree with `1771:7E80` (:1106).

The peak-age rule is `compute_ability` `1771:32EB` (seg_1771_05.asm:283-370): with a = +1,
p = +2, r = +3, the copy branch p <= a <= p + 3 gives +4 = r (:296-312); below it
k = (p - a) idiv 2 (SIGNED, `33A7 idiv cx`, :348-361), so a = p - 1 gives k = 0 and the ceiling
too: the MAXIMUM holds for the five ages p-1..p+3, the copy branch covers four of them; above
it k = a - (p + 3) (:337-347); then factor = 0x10 - k as a 16-bit word (wraps when k > 16,
`3386`/`33AE`) and the stored byte is AL (`33C3`), the low byte of the quotient
((r * factor) mod 65536) div 16 — `33B6 mul` unsigned, `33B9 xor dx, dx` discards the high
product, `33BE div cx` with cx = 0x10 (:362-366). For k <= 16 (a <= p + 19) the quotient is at
most r and is stored whole, falling to 0 at a = p + 19; from k = 17 the factor wraps and the
stored byte is the truncated quotient (a = 47, p = 27, r = 240 gives 0xF1), so the decline is
monotone only up to p + 19.

Retirement `1771:7F40` (:950-1000), on the AGED record: (DS:110E[gk] < a AND caps == 0) OR
a > p + 5, gk = (+7 == 0), DS:110E = 1E 21 (data/ds_2581_01.hex:143). The re-create `7E80`
(:871-948) is RNG: two `214B:06B1` draws at `7EC7`/`7ED1` for the age, make_player's draws
(`7EC0`) and the initial from `1771:0000` (`7F1F`). Its deterministic part is what
`recreate_constraints` (runtime/model/recreate.py, T30) returns; recreate.py models the draws
too (Q014, F017). For a MANAGED country
the loop ages the manager's 80 pool players instead (base DS:6D18[+0x2E-0x80], indices [A927],
:1050-1085) and runs no retirement test.

The CONTINUING-player update consumes no RNG: its callee closure is 7FB1 -> 7E4A -> 32EB, none
of which calls a random routine (calls.tsv; the RNG entry points `214B:06B1` and `1771:0000`
are called in this path only by 7E80), so the `seed` argument of `ageing_value` is accepted for
the task's signature and never consumed: a continuing player's predicted bytes are a pure
function of its record. The yearly path as a whole is NOT RNG-free — retirement re-creation
draws. The year-to-year variance between continuing players is the creation draw (+2 by
roll_peak_age 1771:3291: DS:0E80[gk] + rand(3) - rand(3), DS:0E80 = 1B 1E; +3 by make_player).

The engines read the twelve skills as DS:6DCD[12*(+5) + DS:6D25[12*(+7) + e]] * ((+4)+1) div 32
(1771:3A06, F015); the update changes only +4 of the three inputs, so `derived_skills` here
gives the before/after of all twelve from the same two tables (initialised data, read from the
savestate — F008's hazard; they arrive as arguments, as in runtime/model/keeping.py).
Standard library only.
"""

# --- the record's bytes (F008; annotations/fields.tsv) -----------------------------------
COUNTRY = 0x00        # 7EAC: mov al, es:[di] — make_player's country argument
AGE = 0x01            # 7E6F: inc byte ptr es:[di + 1]
PEAK = 0x02           # 330F/3318/3350/336B/339B: es:[di + 2] — read, never written, in the loop
RATING = 0x03         # 3333/3344: es:[di + 3] — the ceiling r
ABILITY = 0x04        # 333A/33C3: es:[di + 4] — compute_ability's only write
PROFILE = 0x05        # 3A51-3A60: the profile row of 1771:3A06; make_player's rand(0x10)
CLUB_POSITION = 0x07  # 7F5D/32C3: es:[di + 7] == 0 is the goalkeeper test
CAPS = 0x08           # 7F7D: cmp word ptr es:[di + 8], 0 — the retirement test's caps word
GOALS = 0x0A          # 7F12: mov word ptr es:[di + 0xa], ax — zeroed by the re-create
STATUS = 0x10         # 7F19: mov byte ptr es:[di + 0x10], 0 — zeroed by the re-create
SCORER_COUNT = 0x11   # 7FD4: mov byte ptr es:[di + 0x11], 0; 0791:B3B7 increments it (B3EC)
PERFORMANCE = 0x12    # make_player: performance = 0x7FFF (named/seg_1771_06.c, make_player)

# --- the ageing gate 1771:8208 (seg_1771_12.asm:156-163, the set byte CS:81E8 = 0xAC :118) -
AGEING_STAGES = frozenset({2, 3, 5, 7})   # bits 2, 3, 5, 7 of 0xAC
STAGE_RANGE = (2, 8)                       # 8247-824D: 214B:1D6F(+0x3C, 2, 8, 1)

# --- compute_ability 1771:32EB (seg_1771_05.asm:283-370) ----------------------------------
PEAK_BAND = 3         # 331E/3356/3371: add ax, 3 — the copy branch is p..p+3 (four ages)
BELOW_DIVISOR = 2     # 33A4-33A7: mov cx, 2; idiv cx — SIGNED (cdq at 33A3), floor for p > a
FACTOR_BASE = 0x10    # 3383/33AB: mov ax, 0x10 — factor = 0x10 - k, a 16-bit word (wraps)
ABILITY_DIVISOR = 16  # 33BB-33BE: mov cx, 0x10; div cx — UNSIGNED, after `xor dx, dx` (33B9)

# --- retirement 1771:7F40 (seg_1771_11.asm:950-1000; DS:110E = 1E 21, ds_2581_01.hex:143) --
RETIRE_LIMIT = (0x1E, 0x21)   # 7F6D: [di + 0x110e] indexed by (+7 == 0): 30 outfield, 33 keeper
RETIRE_PEAK_MARGIN = 5        # 7F8D: add ax, 5 — retires when a > p + 5

# --- re-create 1771:7E80 (seg_1771_11.asm:871-948) and roll_peak_age 1771:3291 -------------
RECREATE_AGE_BASE = (0x19, 0x1C)  # 7EEB: [di + 0x110c] by (+7 == 0); DS:110C = 19 1C (:143)
RECREATE_AGE_SPREAD = 5           # 7EC3-7EF4: base + rand(6) - rand(6), rand 1..6
PEAK_BASE = (0x1B, 0x1E)          # 32D3: [di + 0xe80] by (+7 == 0); DS:0E80 = 1B 1E (:123)
PEAK_SPREAD = 2                   # 32AB-32DC: base + rand(3) - rand(3), rand 1..3
PROFILE_RANGE = (1, 16)           # make_player: u214b_random_1_to_n(0x10)

# --- derived skills 1771:3A06 (F015; seg_1771_05.asm, div 32 at 3A71-3A74) ----------------
SKILL_DIVISOR = 32    # 3A71-3A74: mov cx, 0x20; div cx (the screen's 3947 divides by 256, F008)
SKILL_STRIDE = 12     # 3A3D/3A57: both tables have 12-column rows
SKILL_ELEMENTS = 12   # the twelve elements 0..11 (F015)


def compute_ability(age, peak, rating):
    """`1771:32EB`: the ability byte +4 from +1/+2/+3, exactly as the listing computes it.

    Inside peak..peak+PEAK_BAND the ceiling is copied (3330-333A); outside, k is the
    half-distance below (idiv 2, 338D-33B0; k = 0 at peak - 1, so the ceiling again) or the
    distance above (3368-3388), factor = 0x10 - k wraps as a 16-bit word when k > 16
    (3386/33AE), and the product is taken mod 65536 before the unsigned divide by 16 (33B6 mul,
    33B9 xor dx,dx, 33BE div cx) with only al stored (33C3)."""
    if peak <= age <= peak + PEAK_BAND:          # 3308-332E: jb at 3313, jg at 332E
        return rating & 0xFF                     # 3330-333A: +4 = +3
    if age > peak + PEAK_BAND:                   # 3364-3366: cmp a, p+3; jle skips
        k = age - (peak + PEAK_BAND)             # 3368-3381 (16-bit, both small and positive)
    else:                                        # 338D-33A7: ax = p - a (33A1), cdq/idiv 2 —
        k = (peak - age) // BELOW_DIVISOR        # signed, and p > a in this branch (3313 jb)
    factor = (FACTOR_BASE - k) & 0xFFFF          # 3383-3388 / 33AB-33B0: a 16-bit word, wraps
    return (((rating & 0xFF) * factor) & 0xFFFF) // ABILITY_DIVISOR & 0xFF  # 33B3-33C3


def retirement_flag(record):
    """`1771:7F40` on `record` as it stands: 1 when it retires (no RNG in its callee set).

    (DS:110E[gk] < age AND the caps word == 0) OR age > peak + 5, gk = (record[+7] == 0)
    (7F5A-7F9D). At the year end 7FDF calls it in the SECOND pass, on the record the first pass
    has aged (seg_1771_11.asm:1043 then :1098) — `ageing_value` applies it to the aged record.
    Runs at the year end only for computer countries (7FDF's 0B77 branch)."""
    gk = 1 if record[CLUB_POSITION] == 0 else 0  # 7F5D-7F6A
    caps = record[CAPS] | (record[CAPS + 1] << 8)  # 7F7D: cmp word ptr es:[di + 8], 0
    if RETIRE_LIMIT[gk] < record[AGE] and caps == 0:  # 7F6D-7F82: cmp al, [di+1]; jae skips
        return 1
    return 1 if record[AGE] > record[PEAK] + RETIRE_PEAK_MARGIN else 0  # 7F87-7F9D: jg


def aged_record(record):
    """The 20 bytes after 7FDF's first pass on a player >= 1: +1, +4 and +0x11 rewritten."""
    out = bytearray(record)
    out[AGE] = (record[AGE] + 1) & 0xFF                                  # 7E6F
    out[ABILITY] = compute_ability(out[AGE], record[PEAK], record[RATING])  # 7E77 call 32EB
    out[SCORER_COUNT] = 0                                                # 7FD4
    return bytes(out)


def ageing_value(record, year, class_table, profile_table, seed):
    """The per-byte new value of one year's ageing for a CONTINUING player (task signature).

    record: the 20 bytes at [A91B] + 20*n. year: the year-end's index (accepted for the record
    it annotates; the loop's writes do not read it). class_table: DS:6D25 (14 positions x 12
    rows), profile_table: DS:6DCD (16 profiles x 12 classes) — used only for the derived-skill
    report, from the SAME savestate (F008's hazard). seed: accepted, never consumed — the
    continuing-player update calls no RNG (notes.md section 3), which test_model_ageing pins.

    Returns {0x01: new age, 0x04: new ability, 0x11: 0, 'retires': flag, 'skills': (before,
    after)}; 'retires' is 7F40's predicate on the AGED record with the caps word the record
    carries (the year end's caps) — when it fires for a computer country the record is
    re-created by 7E80 (see recreate_constraints)."""
    aged = aged_record(record)
    if class_table is None or profile_table is None:
        skills = None                    # the tables are a report, not an input to the writes
    else:
        skills = (derived_skills(record[ABILITY], record, class_table, profile_table),
                  derived_skills(aged[ABILITY], record, class_table, profile_table))
    return {AGE: aged[AGE], ABILITY: aged[ABILITY], SCORER_COUNT: aged[SCORER_COUNT],
            "retires": retirement_flag(aged), "skills": skills}


def year_end_bytes(player, record, year=0, class_table=None, profile_table=None, seed=0):
    """`1771:7FB1(player)` (seg_1771_11.asm:1001-1018): the first pass's per-player writes.

    7E4A skips player 0 (`7E64 cmp word ptr [bp + 4], 0` / `jne`, :856-858) — an empty squad
    slot still runs 7FB1's unconditional `+0x11 = 0` (`7FD4`, :1015) on record 0, and nothing
    else. For player >= 1 this is ageing_value's byte set."""
    if player == 0:
        return {SCORER_COUNT: 0}
    out = ageing_value(record, year, class_table, profile_table, seed)
    writes = {k: v for k, v in out.items() if isinstance(k, int)}
    writes["retires"] = out["retires"]
    return writes


def recreate_constraints(old, country_record=None):
    """Re-export of `recreate.recreate_constraints` (T30 moved it to runtime/model/recreate.py,
    with 7E80's complete contract next to it). Both import styles work: `import ageing` with
    runtime/model on sys.path (experiments/E014-q013-ageing/check_ageing.py) and
    `runtime.model.ageing` from the repository root (tests.test_model_recreate pins both)."""
    try:
        from . import recreate as _r
    except ImportError:
        import recreate as _r
    return _r.recreate_constraints(old, country_record=country_record)


def derived_skills(ability, record, class_table, profile_table):
    """`1771:3A06`: the twelve engine skill values for ability byte `ability` (F015).

    skill e = profile_table[12*(+5) + class_table[12*(+7) + e]] * (ability + 1) div 32."""
    out = []
    for e in range(SKILL_ELEMENTS):
        c = class_table[SKILL_STRIDE * record[CLUB_POSITION] + e]     # 3A37-3A46
        t = profile_table[SKILL_STRIDE * record[PROFILE] + c]         # 3A51-3A60
        out.append((t * ((ability + 1) & 0xFFFF)) // SKILL_DIVISOR)   # 3A66-3A74
    return tuple(out)
