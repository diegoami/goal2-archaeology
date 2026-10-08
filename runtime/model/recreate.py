#!/usr/bin/env python3
"""How a retired computer-country player is re-created at the year end, and how results feed
new talent (T30, Q014; E016).

The yearly loop (experiments/E016-q014-retirement/notes.md, every constant with its listing
line): for a computer country the second pass of `0177:7FDF` (seg_1771_11.asm:1086-1107) calls
`0177:7F40(retirement_test)` (seg_1771_11.asm:949-998) per squad slot, and on a 1 from it
`0177:7E80(recreate_retired_player)` (seg_1771_11.asm:870-947) replaces the slot in place.
`7E80` calls `0177:96D3(make_player)` (seg_1771_13.asm:1105-1201) with the retiree's country
and club position; `make_player` writes everything but the age, and `7E80` then overwrites the
age with a draw from `DS:0x110C` (= 19 1C, base 25/28 outfield/goalkeeper) ± rand(6) − rand(6),
runs `0177:32EB(compute_ability)` again, zeros caps/goals/status, draws a new surname-initial
byte from `0177:0000`, and restores the old `+6` (position).

The deterministic byte set of a re-create, then, depends on:
- the OLD record (carries `+0`, `+6`, `+7` over; sets the +3 `country_rating` index via
  country; size of the age/peak spread via `+7`);
- the COUNTRY RECORD at the moment of re-create (its `+0x2A`/`+0x2B`/`+0x2C` go straight into
  `country_rating` 0177:10E7, seg_1771_02.asm:697-738).

The LCG (single 16-bit word at `DS:0x7B62`, F004) drives all drawn bytes; the routine does
multiple LCG byte draws per re-create (see section 5 of notes.md and the listing). The model
returns what the listing fixes deterministically (`recreate_constraints`) and brackets the
drawn bytes; `check_recreate.py` then handles the exact match where the LCG state is in hand.

The results -> talent chain (notes section 4): `country_rating(country)` reads `+0x2C` (continent,
static), `+0x2A` (continent_rank) and `+0x2B` (world_rank); these ranks are recomputed by
`0177:63A4` (seg_1771_09.asm:1019+, named/seg_1771_05.c:23+, here annotated) when
`0177:6730` (`stage_qualifying`, F004) runs at the next stage 2 (writes +0x2B) or stage 5
(writes +0x2A) entry. The re-create happens BEFORE 6730 within a stage transition (8208
calls 80DA, then play_round calls 76B1, seg_000E_09.asm:486-498), so a re-create reads the
rank values that were LAST written — typically from the PRECEDING season's relevant stage
(world_rank from the world-qualifying stage 2, continent_rank from the finals-qualifying
stage 5).

So a re-created player's `+3 = country_rating(country) + 0x7F` is determined by the PRIOR
season's results at the time of this re-create, with a one-cycle lag for the world rank when
the current cycle hasn't yet entered its stage 2 settling. The HELP FILE's claim that
"replacements are better in a country whose points beat its expected points"
(`GOAL.HLP` 196-205) is therefore TRUE: a better results table ⇒ smaller world_rank ⇒ LARGER
(129 - world_rank) ⇒ LARGER country_rating ⇒ LARGER `+3`.

Standard library only.
"""

# --- the record's bytes (F008; annotations/fields.tsv) -----------------------------------
COUNTRY = 0x00        # 7EAC: mov al, es:[di] — make_player's country argument
AGE = 0x01            # 7E6F: inc byte ptr es:[di + 1]
PEAK = 0x02           # 330F/3318/3350/336B/339B: es:[di + 2] — read, never written, in the loop
RATING = 0x03         # 3333/3344: es:[di + 3] — the ceiling r
ABILITY = 0x04        # 333A/33C3: es:[di + 4] — compute_ability's only write
PROFILE = 0x05        # 3A51-3A60: the profile row of 1771:3A06; make_player's rand(0x10)
POSITION = 0x06       # 7F30-7F36: 7E80 restores the OLD +6 after make_player overwrites it
CLUB_POSITION = 0x07  # 7F5D/32C3: es:[di + 7] == 0 is the goalkeeper test, also 96FC's arg
CAPS = 0x08           # 7F09: mov word ptr es:[di + 8], ax — zeroed by the re-create
GOALS = 0x0A          # 7F12: mov word ptr es:[di + 0xa], ax — zeroed by the re-create
STATUS = 0x10         # 7F19: mov byte ptr es:[di + 0x10], 0 — zeroed by the re-create
SCORER_COUNT = 0x11   # 7FD4: mov byte ptr es:[di + 0x11], 0; 0791:B3B7 increments it (B3EC)
PERFORMANCE = 0x12    # make_player: performance = 0x7FFF (97C0), named/seg_1771_06.c
MORALE = 0x0C         # make_player: +0xC = rand(0x20), :97A2-97AB
FITNESS = 0x0D        # roll_fitness_energy 1771:3558 (TBD by the LCG)
ENERGY = 0x0E         # roll_fitness_energy 1771:3558 (TBD by the LCG)
INITIAL_OFFSET = 0x00  # the surname byte at [DS:9B70] + player; f_1771_0000() draws a fresh byte

# --- the re-create draws, list of LCG byte readers in 7E80 (notes section 2.2) -------------
# a 7E80 call path consumes 6 RNG entries: a rand(0x10) for +5 (make_player), a rand(7) + rand(7)
# for +1 (make_player), 2 rand(3) for +2 via roll_peak_age (make_player), a rand(0x20) for +0xC,
# then 2 rand(6) for the +1 override, then a final byte from 1771:0000 for the initial.
# The exact order matters for reproducibility from the LCG, but the model brackets +1, +2, +5
# and reports whether the LCG state is recoverable from a savestate.

# --- re-create's age base 1771:7EEB (notes section 2) ------------------------------------
# +1 = DS:0x110C[gk] + rand(6) - rand(6), where gk = (+7 == 0)
RECREATE_AGE_BASE = (0x19, 0x1C)   # 7EEB: [di + 0x110c] by (+7 == 0); DS:110C = 19 1C (ds_2581_01.hex:143)
RECREATE_AGE_SPREAD = 5             # 7EC7/7ED1: rand 1..6 — first and second rand, the difference

# --- roll_peak_age 1771:3291 (called by make_player 96D3 via 975B) -------------------------
PEAK_BASE = (0x1B, 0x1E)            # 32D3: [di + 0xe80] by (+7 == 0); DS:0E80 = 1B 1E (ds_2581_01.hex:123)
PEAK_SPREAD = 2                     # 32AB-32DC: base + rand(3) − rand(3), rand 1..3

# --- make_player's profile +5 + morale +0xC ------------------------------------------------
PROFILE_RANGE = (1, 16)             # 96D3: 9711 rand(0x10), DS:6DCD is 16 rows × 12 columns
MORALE_RANGE = (1, 32)              # 96D3: 97A2 rand(0x20), DS:78A3 lookup below 0x20

# --- country_rating 1771:10E7 (notes section 4) -------------------------------------------
RATING_BASE = 0x7F                  # 96D3 :976B add ax, 0x7F: +3 = country_rating + 0x7F
CONTINENT_FIELDS = ('continent', 'continent_rank', 'world_rank')  # country rating's three inputs


def country_rating(continent, continent_rank, world_rank):
    """`1771:10E7` (seg_1771_02.asm:697-738): the formula (signed 16-bit, then signed idiv 2).

    lines 1113-1133:
    ```
    cx = 5 − continent                         ; 1113 sub ax, dx
    ax = 33 − continent_rank                   ; 111E-1121
    cx = cx * ax  (imul cx)                    ; 1123
    ax = 129 − world_rank                      ; 1132-1135
    ax = ax + cx                               ; 1137
    (cdq, mov cx, 2, idiv cx: signed divide by 2)
    return ax
    ```
    Note the cdq + idiv at 1139-113D makes the divide SIGNED even though the operands are
    positive in the game's domain (continent 0..4, continent_rank 1..32, world_rank 1..128):
    a 16-bit positive dividend divided by 2 in two's complement is correct.
    """
    cx = 5 - continent
    ax = 33 - continent_rank
    cx = cx * ax
    ax = (129 - world_rank) + cx
    # signed idiv 2; both operands positive here, so the sign extension is benign
    return ax // 2 if (ax >= 0) else -((-ax + 1) // 2)


def recreate_constraints(old, country_record=None):
    """What `1771:7E80(player)` fixes deterministically in the re-created record, given the
    retiree's record `old` as the second pass saw it, and the country record at re-create time.

    Returns `{'exact': {offset: byte}, 'range': {offset: (lo, hi)}}`:

    - **exact**:
        +0 (country) = old[+0]; +7 (club_position) = old[+7] — make_player's two args at
          :96F3/:96FC carry the old values over;
        +6 (position) = old[+6] — restored at :7F30-7F36 after make_player sets +6 = +7;
        +8/+9 (caps) = 0 at :7F09, +0xA/+0xB (goals) = 0 at :7F12, +0x10 (status) = 0 at :7F19;
        +0x11 (scorer_count) = 0 — 7FB1 cleared it in the first pass (:7FD4) and 7E80 writes
          nothing here, leaving it as it was (zero);
        +0x12/+0x13 (performance) = 0xFF/0x7F at :97C0 (make_player writes performance = 0x7FFF).
    - **range**:
        +1 (age) in (DS:0x110C[gk] − 5) .. (DS:0x110C[gk] + 5)  (rand(6) − rand(6) at :7EC7/:7ED1);
        +2 (peak) in (DS:0x0E80[gk] − 2) .. (DS:0x0E80[gk] + 2) (rand(3) − rand(3) via make_player
          calling roll_peak_age :3291);
        +5 (profile) in 1..16 (rand(0x10) at :9711);
        +0xC (morale) in 1..32 (rand(0x20) at :97A2) — predicted for completeness, but not
          checked in `check_recreate` (the layout doesn't carry it into the runner's
          record capture as a high-confidence byte, see check_recreate's selection).

    - **NOT computed here**:
        +3 (rating) depends on `country_record`: a re-create reads the country record's
        +0x2C / +0x2A / +0x2B at make_player call 0x10E7 (:9764-:9771). The model assumes
        the caller passes the country record (or its three rank bytes) for that prediction;
        if absent, +3 is not in the constraints.
        +4 (ability) = compute_ability(+1, +2, +3) of the new bytes — the final compute_ability
        at :7F01 runs AFTER +1 has been overridden. So given +1/+2/+3, +4 is deterministic
        and check_recreate's `compute_ability` self-test verifies it.
        +0xD / +0xE (fitness / energy) — drawn by roll_fitness_energy :3558; bracketed by the
        initialization tables DS:0x78D5/DS:0x78F6, but the model brackets them as range too.
        the surname byte (at +0..+10 of [DS:9B6C] + 11·player, F008) is left unchanged by 7E80
        (only the initial at [DS:9B70] + player is redrawn).
        the new initial byte at [DS:9B70] + player — drawn from 1771:0000 (a uniform byte from
        an LCG word). `check_recreate` does not bracket this; the runner captures the initial.

    The arguments:
        old: the retiree's 20-byte record as the second pass of 7FDF saw it (i.e. aged).
        country_record: optional — when supplied, used for the +3 prediction. Either a 0xBF-byte
            country record (offsets +0x2A/+0x2B/+0x2C used) or a 3-tuple
            (continent, continent_rank, world_rank).
    """
    gk = 1 if old[CLUB_POSITION] == 0 else 0
    age_base, peak_base = RECREATE_AGE_BASE[gk], PEAK_BASE[gk]
    # +6 is fixed by 7E80 (7F30-7F36: position = old +6) but the comparator does not check it
    # because captures are one year apart and the per-match repositioning (0791:AD8F, the player
    # screen's 'C' key 1771:4952, unmanage_country 000E:0290, reset_team_tactics 0791:BC5D;
    # notes of E014, section 6) changes +6 between captures. The literal record at the
    # instant of re-create has +6 = the retiree's +6 as the second pass of 7FDF saw it.
    exact = {COUNTRY: old[COUNTRY], CLUB_POSITION: old[CLUB_POSITION],
             CAPS: 0, CAPS + 1: 0, GOALS: 0, GOALS + 1: 0, STATUS: 0,
             SCORER_COUNT: 0,
             PERFORMANCE: 0xFF, PERFORMANCE + 1: 0x7F}
    rng = {AGE: (age_base - RECREATE_AGE_SPREAD, age_base + RECREATE_AGE_SPREAD),
           PEAK: (peak_base - PEAK_SPREAD, peak_base + PEAK_SPREAD),
           PROFILE: PROFILE_RANGE}
    if country_record is not None:
        if isinstance(country_record, dict):
            cr = country_rating(country_record['continent'],
                                country_record['continent_rank'],
                                country_record['world_rank'])
        elif isinstance(country_record, (tuple, list)) and len(country_record) == 3:
            cr = country_rating(*country_record)
        else:
            cr = country_rating(country_record[0x2C], country_record[0x2A], country_record[0x2B])
        exact[RATING] = (cr + RATING_BASE) & 0xFF
    return {"exact": exact, "range": rng,
            # the re-create's +4 = compute_ability(+1, +2, +3) at :7F01
            "ability_of_own_bytes": True,
            # one +3 per country in one 7FDF call (country record is read but not written
            # between re-creates within the same 7FDF call)
            "same_rating_per_country": True,
            "gk": gk}
