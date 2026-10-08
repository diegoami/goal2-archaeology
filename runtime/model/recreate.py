#!/usr/bin/env python3
"""How a retired player is replaced and how a new player is made (T30, Q014; F017, E016).

Every constant carries its listing line; the claim-by-claim map is
experiments/E016-q014-retirement/notes.md.

- The RNG is one 16-bit word, the one the far pointer DS:A978 points to (214B:206A sets it to
  DS:7B62, F004). `214B:06B1(n)` (seg_214B_01.asm:897-911) passes that pointer to `214B:0688`
  (:871-894), which stores `w = w * 0x7ABD + 0x1B0F` (mod 2^16, :880-886) and returns
  `hi16(w * n) + 1`, 1..n (:887-889). `lcg_step` / `draw` below.
- `1771:96D3` make_player(flag, club_position, country, player) (seg_1771_13.asm:1107-1201)
  writes +0, +7, +6 (= +7), +5, +1, +2 (via 1771:3291), +3 (via 1771:10E7), +4 (1771:32EB),
  +0xC, +0xF (1771:3431, bits only), +0xD/+0xE (1771:3558) and +0x12 = 0x7FFF, drawing in a
  fixed order (`make_player`).
- `1771:7E80` (seg_1771_11.asm:872-947) re-creates a computer country's retiree IN PLACE:
  make_player(1, old +7, old +0, player), then +1 = DS:110C[gk] + b - a (a, b = rand(6)),
  32EB again, caps/goals/status zeroed, a new initial DS:0C38[rand(DS:0C38)] at
  [DS:9B70] + player, and the old +6 restored (`recreate`). Ten draws per re-create.
- `000E:54F0` (seg_000E_07.asm:84-283) makes a MANAGED country's replacement in a fresh
  record: the same make_player (managed fitness branch), +1 = DS:0x78[gk] + b - a, 32EB,
  zeroed caps/goals/status, a new initial, then the young-squad override
  (`managed_replacement`).

`recreate_contract` is 7E80's complete instantaneous contract in range form (no RNG state);
`recreate` is the same routine exactly, given the RNG state; `recreate_constraints` is F016's
reduced form (moved here from ageing.py, which re-exports it). `NOT_IN_CAPTURES` says which
part of the contract year-apart captures cannot show, and why.

Standard library only.
"""

try:                                   # imported as runtime.model.recreate (the tests)
    from . import ageing as A
except ImportError:                    # imported as a top-level module (runtime/model on sys.path)
    import ageing as A

# --- the record's bytes beyond F016's (F007/F008; annotations/fields.tsv) ------------------
POSITION = 0x06       # 970A: +6 = +7 in make_player; 7E9D saves the old +6, 7F36 restores it
MORALE = 0x0C         # 97AB: mov byte ptr es:[di + 0xc], al
FITNESS = 0x0D        # 35E8/3615/3626/3646 (1771:3558)
ENERGY = 0x0E         # 3635: +0xE = +0xD after the cap, before the floor
TACTICS = 0x0F        # 214B:0C79/0CA1 on +0xF from 1771:3431 / 33CD

# --- the generator 214B:0688 (seg_214B_01.asm:880-889; F004) -------------------------------
LCG_MUL = 0x7ABD      # 0695: mov bx, 0x7abd
LCG_INC = 0x1B0F      # 069A: add ax, 0x1b0f (the low word only: stosw at 069F)

# --- make_player 1771:96D3 (seg_1771_13.asm:1107-1201) -------------------------------------
PROFILE_DRAW = 0x10                # 970E-9712: rand(0x10) -> +5 (971A)
MP_AGE_DRAW = 7                    # 971E/9728: a, b = rand(7)
MP_AGE_BASE = (0x1C, 0x1F)         # 9746: [di + 0x118a] by (+7 == 0); DS:118A = 1C 1F (ds_2581_01.hex:147)
PEAK_DRAW = 3                      # 1771:3291, 32AB/32B5: a, b = rand(3); +2 = DS:0E80[gk] + b - a (32D3-32E1)
POOL_RATING_DRAW = 10              # 9777-977B: rand(0xa), only when flag == 0
POOL_RATING_CUT = 10               # 978B: sub ax, 0xa
RATING_OFFSET = 0x7F               # 976B / 9788: add ax, 0x7f
MORALE_DRAW = 0x20                 # 979F-97A3: rand(0x20) -> +0xC (97AB)
PERFORMANCE_INIT = 0x7FFF          # 97C0: mov word ptr es:[di + 0x12], 0x7fff

# --- set_player_tactics 1771:3431, 33CD, 2FFB (seg_1771_05.asm:372-481, seg_1771_04.asm:1102-1131)
HARDNESS_LIMIT = 4                 # 3452: cmp al, 4; jae skips 33CD
OVERRIDE_BIT = 0x80                # 33E7-33F4: include element 8 (bit 7)
TACKLE_BIT = 0x08                  # 33F9-3406: exclude element 4 (bit 3)
BACK_POSITIONS = frozenset({0, 1, 3, 4})   # CS:3411 = 1B (set test 346A): positions 0, 1, 3, 4
BACK_BITS = 0x10 | 0x01            # 3471-3490: elements 5 and 1
CENTRE_BACK = 2                    # 349A: cmp byte ptr es:[di + 6], 2
CENTRE_BACK_PROFILE = 0x0E         # 34A4: cmp byte ptr es:[di + 5], 0xe; jae skips element 5
CENTRE_BACK_BITS = 0x20 | 0x02     # 34BD-34DC: elements 6 and 2

# --- roll_fitness_energy 1771:3558 (seg_1771_05.asm:532-633) -------------------------------
FITNESS_BASE = (0x10, 0x0D)        # 35AD/35F4: [di + 0xe82] by (+1 > +2 + 4); DS:0E82 = 10 0D (ds_2581_01.hex:123)
FITNESS_OLD_MARGIN = 4             # 357B: add ax, 4 (the index is +1 > +2 + 4, 3589 jg)
FITNESS_CAP = 0x20                 # 361C/3626: +0xD > 0x20 (signed, jle) -> 0x20
FITNESS_FLOOR = 1                  # 363C/3646: +0xD < 1 (signed, jge) -> 1, after +0xE is copied

# --- the re-create 1771:7E80 (seg_1771_11.asm:872-947) and the initial 1771:0000 ------------
RECREATE_AGE_DRAW = 6              # 7EC3/7ECD: a, b = rand(6); +1 = DS:110C[gk] + b - a (7EEB-7EF9)
INITIAL_LETTERS = b"ABCDEFGHIJKLMNOPRSTVW"  # DS:0C38 = 0x15, then these 21 bytes (ds_2581_01.hex:104-105)
#   1771:0000 (seg_1771_01.asm:9-22): r = rand(byte DS:0C38) (0006-000C), returns DS:0C38[r] (0013)

# --- the managed replacement 000E:54F0 (seg_000E_07.asm:84-283) ----------------------------
MANAGED_AGE_BASE = (0x19, 0x1C)    # 5561: [di + 0x78] by (+7 == 0); DS:0078 = 19 1C (ds_2581_01.hex:10)
YOUNG_BASE = (0x11, 0x14)          # 5609/5689/56D2: [di + 0x76]; DS:0076 = 11 14 (ds_2581_01.hex:10)
YOUNG_MARGIN = 4                   # 560F/568F: add ax, 4 — "young" is +1 < DS:76[gk] + 4
YOUNG_QUOTA = 0x14                 # 56AC: cmp word ptr [bp - 2], 0x14; jb -> the override
YOUNG_DRAW = 3                     # 56B4: rand(3); +1 = DS:76[gk] + rand(3) (56D2-56DD)

# --- the new game: make_squad 1771:97CC and make_managed_pool 1771:98C4 (seg_1771_14.asm) ---
SQUAD_SLOTS = 20                   # 9867: cmp word ptr [bp - 2], 0x14
POOL_POSITIONS = 14                # 9955: cmp word ptr [bp - 4], 0xd (positions 0..13)
POOL_PER_POSITION = 4              # 994F: cmp word ptr [bp - 6], 4
POOL_AGE_BASE = (0x11, 0x14)       # 99DA: [di + 0x118c] by (+7 == 0); DS:118C = 11 14 (ds_2581_01.hex:147)
POOL_AGE_DRAW = 3                  # 99BC: rand(3)
POOL_EXTRA_SLOTS = (6, 9)          # 9A04: from slot 6; 9A32: cmp word ptr [bp - 4], 9

# --- country_rating 1771:10E7 (seg_1771_02.asm:697-738) ------------------------------------
CONTINENT_WEIGHT = 5               # 110C: mov ax, 5; sub ax, continent (+0x2C)
CONTINENT_RANKS = 0x21             # 111E: mov ax, 0x21; sub ax, continent rank (+0x2A)
WORLD_RANKS = 0x81                 # 1132: mov ax, 0x81; sub ax, world rank (+0x2B)
RATING_DIVISOR = 2                 # 1139-113D: cwd; mov cx, 2; idiv cx (signed, toward zero)

# What year-apart captures cannot show of 7E80's contract (check_recreate.py skips exactly these
# and prints them): the re-create copies or keeps bytes of the retiree AS THEY STAND AT THE
# INSTANT, and a year of matches between two captures rewrites those bytes of the retiree.
NOT_IN_CAPTURES = {
    POSITION: "+6 = the retiree's +6 at the instant (7E9D/7F36); +6 is moved per match "
              "(0791:AD8F, 1771:4952, 000E:0290, 0791:BC5D; E014 notes section 6), so a capture "
              "a year earlier does not give it",
    TACTICS: "+0xF keeps the retiree's +0xF bits that 1771:3431 neither sets nor clears; "
             "0791:BC5D, 0791:C5DC and 1771:34E7 clear and re-derive +0xF between captures; the "
             "bits 3431 sets or clears are checked",
    A.RATING: "+3 = country_rating + 0x7F reads the country record (+0x2A/+0x2B/+0x2C), which "
              "the E014 captures do not hold; checked as one byte per country per 7FDF call and "
              "in the domain 0x80..0xFF",
}


def lcg_step(w):
    """`214B:0688`'s store: the next value of the word (mod 2^16)."""
    return (w * LCG_MUL + LCG_INC) & 0xFFFF


def draw(w, n):
    """`214B:06B1(n)`: (value 1..n, the new word)."""
    w = lcg_step(w)
    return ((w * n) >> 16) + 1, w


def country_rating(continent, continent_rank, world_rank):
    """`1771:10E7`: ((5 - continent) * (0x21 - continent rank) + (0x81 - world rank)) idiv 2.

    The three are the country record's +0x2C, +0x2A, +0x2B (1104, 1116, 112A). The subtractions
    are 16-bit (110F, 1121, 1135), the product `imul cx` (1123), the divide SIGNED toward zero
    (`cwd` 1139, `idiv cx` 113D). A smaller (better) rank makes its difference larger, so a
    better rank gives a larger rating. In the game's domain (continent 1..4, the four groups
    1771:63A4 sorts at 6408-6431; continent rank 1..32, 6514-6524; world rank 1..128, 652A-6530)
    the rating runs 1 (4, 32, 128) .. 128 (1, 1, 1), so +3 = rating + 0x7F is 0x80..0xFF."""
    a = ((CONTINENT_WEIGHT - continent) * (CONTINENT_RANKS - continent_rank)
         + (WORLD_RANKS - world_rank))
    a = ((a + 0x8000) & 0xFFFF) - 0x8000          # the 16-bit word idiv sees
    q = abs(a) // RATING_DIVISOR
    return q if a >= 0 else -q


def rating_of(country_record):
    """country_rating of a 0xBF-byte country record, or of (continent, continent rank, world rank)."""
    if len(country_record) == 3:
        return country_rating(*country_record)
    return country_rating(country_record[0x2C], country_record[0x2A], country_record[0x2B])


def hardness(record):
    """`1771:2FFB`: +5 - (+3 and 1), a byte (3018-3033)."""
    return (record[A.PROFILE] - (record[A.RATING] & 1)) & 0xFF


def tactics_bits(record):
    """`1771:3431` on `record` (+5, +3, +6 as they stand): (bits it sets, bits it clears).

    Hardness below 4 calls 33CD first (344F-345A): include element 8, exclude element 4. Then
    position +6 in CS:3411 = {0, 1, 3, 4} sets elements 5 and 1 (346A-3490); position 2 sets
    element 5 when +5 < 14 (34A4-34B8), then elements 6 and 2 (34BD-34DC). It never clears
    +0xF first: the result is (old +0xF | set) & ~clear."""
    set_, clear = 0, 0
    if hardness(record) < HARDNESS_LIMIT:
        set_, clear = OVERRIDE_BIT, TACKLE_BIT
    if record[POSITION] in BACK_POSITIONS:
        set_ |= BACK_BITS
    elif record[POSITION] == CENTRE_BACK:
        if record[A.PROFILE] < CENTRE_BACK_PROFILE:
            set_ |= 0x10
        set_ |= CENTRE_BACK_BITS
    return set_, clear


def fitness(record, managed, w):
    """`1771:3558` on `record` (+1, +2 as they stand): (+0xD, +0xE, the new word).

    T = DS:0E82[+1 > +2 + 4] (3572-3593, 35AD). A managed country (1771:0B77 at 35A0) draws
    a = rand(T + 1), then b = rand(3T), value T + b - a (35AD-35E8); a computer country draws
    once, value T + rand(2T) (35EE-3615). The value is capped at 0x20 (361C-3626), +0xE takes
    it (3635), then +0xD is floored at 1 (363C-3646)."""
    t = FITNESS_BASE[1 if record[A.AGE] > record[A.PEAK] + FITNESS_OLD_MARGIN else 0]
    if managed:
        a, w = draw(w, t + 1)
        b, w = draw(w, 3 * t)
        v = t + b - a
    else:
        r, w = draw(w, 2 * t)
        v = t + r
    v = min(v, FITNESS_CAP)
    return max(v, FITNESS_FLOOR) & 0xFF, v & 0xFF, w


def make_player(record, flag, club_position, country, rating, managed, w):
    """`1771:96D3` on the 20 bytes `record` (what the slot held): (new record, new word).

    rating: country_rating(country) (1771:10E7 at 9768/9785). managed: 1771:0B77(country), the
    fitness branch. Bytes it does not write (+8..+0xB, +0x10, +0x11) are carried, and +0xF keeps
    the bits 3431 does not touch."""
    r = bytearray(record)
    r[A.COUNTRY] = country                                    # 96ED-96F3
    r[A.CLUB_POSITION] = club_position                        # 96F6-96FC
    r[POSITION] = club_position                               # 9700-970A
    gk = 1 if club_position == 0 else 0                       # 9736-9746, 32C3-32D3
    r[A.PROFILE], w = draw(w, PROFILE_DRAW)                   # 970E-971A
    a, w = draw(w, MP_AGE_DRAW)                               # 971E-9722 (pushed)
    b, w = draw(w, MP_AGE_DRAW)                               # 9728-9731
    r[A.AGE] = (MP_AGE_BASE[gk] - b + a) & 0xFF               # 9746-9754
    a, w = draw(w, PEAK_DRAW)                                 # 3291: 32AB-32B4 (pushed)
    b, w = draw(w, PEAK_DRAW)                                 # 32B5-32BE
    r[A.PEAK] = (A.PEAK_BASE[gk] + b - a) & 0xFF              # 32D3-32E1
    if flag:                                                  # 975E-9771
        r[A.RATING] = (rating + RATING_OFFSET) & 0xFF
    else:                                                     # 9777-9794
        d, w = draw(w, POOL_RATING_DRAW)
        r[A.RATING] = (rating + RATING_OFFSET - POOL_RATING_CUT - d) & 0xFF
    r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 979C
    r[MORALE], w = draw(w, MORALE_DRAW)                       # 979F-97AB
    s, c = tactics_bits(r)                                    # 97B3: 1771:3431
    r[TACTICS] = (r[TACTICS] | s) & ~c & 0xFF
    r[FITNESS], r[ENERGY], w = fitness(r, managed, w)         # 97BA: 1771:3558
    r[0x12], r[0x13] = PERFORMANCE_INIT & 0xFF, PERFORMANCE_INIT >> 8   # 97C0
    return bytes(r), w


def initial(w):
    """`1771:0000`: (the initial byte DS:0C38[rand(21)], the new word)."""
    r, w = draw(w, len(INITIAL_LETTERS))
    return INITIAL_LETTERS[r - 1], w


def recreate(old, rating, w):
    """`1771:7E80(player)` exactly: (new record, new initial, new word), from the record `old`
    as 7FDF's second pass sees it (the aged record), the country's rating at that instant and
    the RNG word. A computer country only (7FDF reaches 7E80 only there), so the fitness
    branch is the unmanaged one. The surname is not written."""
    gk = 1 if old[A.CLUB_POSITION] == 0 else 0                # 7EDB-7EE9: the OLD +7 (= new +7)
    r, w = make_player(old, 1, old[A.CLUB_POSITION], old[A.COUNTRY], rating, False, w)  # 7EA6-7EC0
    r = bytearray(r)
    a, w = draw(w, RECREATE_AGE_DRAW)                         # 7EC3-7ECC (pushed)
    b, w = draw(w, RECREATE_AGE_DRAW)                         # 7ECD-7ED6
    r[A.AGE] = (A.RECREATE_AGE_BASE[gk] + b - a) & 0xFF       # 7EEB-7EF9
    r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 7F01
    r[A.CAPS] = r[A.CAPS + 1] = 0                             # 7F09
    r[A.GOALS] = r[A.GOALS + 1] = 0                           # 7F12
    r[A.STATUS] = 0                                           # 7F19
    ini, w = initial(w)                                       # 7F1F-7F2D
    r[POSITION] = old[POSITION]                               # 7E9D-7EA3 saved, 7F30-7F36
    return bytes(r), ini, w


def young(rec):
    """54F0's count test for one record: +1 < DS:0x76[gk] + 4 (55F6-561F, 5676-569F)."""
    return rec[A.AGE] < YOUNG_BASE[1 if rec[A.CLUB_POSITION] == 0 else 0] + YOUNG_MARGIN


def managed_replacement(fresh, retiree, country, rating, others, w):
    """`000E:54F0` exactly: (new record, new initial, new word).

    fresh: the 20 bytes of the record 1771:4CF7 chose (a record with country byte 0; 56F3
    stores its number in the retiree's squad or pool slot before calling 54F0, 574A-579C).
    retiree: the retiring record (its +7 is make_player's club position, 551C-552A). others: the
    records of the other 99 words the count reads (squad slots 1..20, 55B5-5628, and the
    manager's 80 pool words DS:6D18[m] .. +0x4F, 562A-56AA), the new word's own record being
    the new one. A managed country: make_player's managed fitness branch."""
    r, w = make_player(fresh, 1, retiree[A.CLUB_POSITION], country, rating, True, w)  # 550E-5534
    r = bytearray(r)
    gk = 1 if r[A.CLUB_POSITION] == 0 else 0                  # 554E-555F: the new record's +7
    a, w = draw(w, RECREATE_AGE_DRAW)                         # 5539-5542 (pushed)
    b, w = draw(w, RECREATE_AGE_DRAW)                         # 5543-554C
    r[A.AGE] = (MANAGED_AGE_BASE[gk] + b - a) & 0xFF          # 5561-556F
    r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 557A
    r[A.CAPS] = r[A.CAPS + 1] = 0                             # 5584
    r[A.GOALS] = r[A.GOALS + 1] = 0                           # 558D
    r[A.STATUS] = 0                                           # 5594
    ini, w = initial(w)                                       # 5599-55AD
    count = sum(1 for o in others if young(o)) + (1 if young(r) else 0)
    if count < YOUNG_QUOTA:                                   # 56AC-56B2
        d, w = draw(w, YOUNG_DRAW)                            # 56B4-56BD
        r[A.AGE] = (YOUNG_BASE[gk] + d) & 0xFF                # 56BF-56DD
        r[A.ABILITY] = A.compute_ability(r[A.AGE], r[A.PEAK], r[A.RATING])   # 56E8
    return bytes(r), ini, w


def new_game_squad(country, rating, club_positions, before=None):
    """`1771:97CC(country)` at a new game (seg_1771_14.asm:6-70): the word := country (97E6-97ED),
    then make_player(1, DS:9F02[20 * country + slot], country, squad[slot]) for slots 1..20
    (982D-986B; club_positions are those 20 bytes). No country is managed yet (1771:2D15 runs
    after 1771:9B85, seg_0000_01.asm:24-25), so the fitness branch is the unmanaged one.
    before: the 20 records as they were (zeros by default). Returns (20 records, the word)."""
    w, out = country & 0xFFFF, []
    for slot in range(SQUAD_SLOTS):
        rec = bytes(20) if before is None else before[slot]
        rec, w = make_player(rec, 1, club_positions[slot], country, rating, False, w)
        out.append(rec)
    return out, w


def managed_pool(w, country, rating, squad_club_positions):
    """`1771:98C4` (seg_1771_14.asm:106-256): the manager's 80 extra players through
    `1771:9873` = make_player(0, position, country, 0xA00 + counter) (987D-98BB), the country
    already managed (2D15 set its +0x2E): four per position 0..13 (993E-9959); one per squad
    slot 1..20 with that slot's +7, its age then redrawn DS:118C[gk] + rand(3) and +4
    recomputed (9976-99F8); then slots 6..9 again (9A04-9A36). Returns (80 records in the
    order made, the word). 1771:5532 then sorts the pool's word list, not the records."""
    out = []
    for pos in range(POOL_POSITIONS):
        for _ in range(POOL_PER_POSITION):
            rec, w = make_player(bytes(20), 0, pos, country, rating, True, w)
            out.append(rec)
    for slot in range(SQUAD_SLOTS):
        rec, w = make_player(bytes(20), 0, squad_club_positions[slot], country, rating, True, w)
        rec = bytearray(rec)
        d, w = draw(w, POOL_AGE_DRAW)                                   # 99BC-99C0
        rec[A.AGE] = (POOL_AGE_BASE[1 if rec[A.CLUB_POSITION] == 0 else 0] + d) & 0xFF  # 99C7-99E5
        rec[A.ABILITY] = A.compute_ability(rec[A.AGE], rec[A.PEAK], rec[A.RATING])  # 99F8
        out.append(bytes(rec))
    for slot in range(POOL_EXTRA_SLOTS[0], POOL_EXTRA_SLOTS[1] + 1):
        rec, w = make_player(bytes(20), 0, squad_club_positions[slot - 1], country, rating, True, w)
        out.append(rec)
    return out, w


def _spread(base, n):
    """base + b - a with a, b = rand(n): base - (n - 1) .. base + (n - 1)."""
    return (base - (n - 1), base + (n - 1))


def recreate_contract(old, rating=None):
    """7E80's complete instantaneous contract in range form (no RNG state), given the record
    `old` as the second pass sees it and, when known, the country's rating.

    Returns {'exact': {off: byte}, 'range': {off: (lo, hi)}, 'same_as': {off: off},
    'tactics': (old +0xF, function new -> (set, clear)), 'initial': letters,
    'surname': 'kept', 'ability_of_own_bytes': True, 'same_rating_per_country': True}:
    - exact: +0 = old +0 and +7 = old +7 (make_player's arguments, 7EAC/7EB5 -> 96F3/96FC);
      +6 = old +6 (7E9D/7F36); +8..+0xB = 0 (7F09, 7F12); +0x10 = 0 (7F19); +0x11 = old
      +0x11 (nothing in 7E80's callee set writes it; 7FB1 zeroed it in the first pass, 7FD4);
      +0x12/+0x13 = FF 7F (97C0); +3 = rating + 0x7F when the rating is given (976B-9771);
    - range: +1 in DS:110C[gk] +- 5 (7EC3-7EF9); +2 in DS:0E80[gk] +- 2 (3291); +5 in 1..16
      (9711); +0xC in 1..32 (97A3); +0xD in min(T)+1 .. min(3 max(T), 0x20) = 14..32 (3558's
      computer branch; which T is the index of make_player's intermediate age, overwritten at
      7EF9); +3 in 0x80..0xFF when the rating is not given (country_rating's domain);
    - same_as: +0xE = +0xD (3635: the floor at 363C cannot fire, the value is at least T + 1);
    - +4 = compute_ability of the new +1/+2/+3 (7F01); the initial one of DS:0C38's 21 letters
      (7F1F); the surname kept (7E80 writes only [DS:9B70] + player, 7F2D)."""
    gk = 1 if old[A.CLUB_POSITION] == 0 else 0
    exact = {A.COUNTRY: old[A.COUNTRY], A.CLUB_POSITION: old[A.CLUB_POSITION],
             POSITION: old[POSITION],
             A.CAPS: 0, A.CAPS + 1: 0, A.GOALS: 0, A.GOALS + 1: 0, A.STATUS: 0,
             A.SCORER_COUNT: old[A.SCORER_COUNT],
             0x12: PERFORMANCE_INIT & 0xFF, 0x13: PERFORMANCE_INIT >> 8}
    t_lo, t_hi = min(FITNESS_BASE), max(FITNESS_BASE)
    rng = {A.AGE: _spread(A.RECREATE_AGE_BASE[gk], RECREATE_AGE_DRAW),
           A.PEAK: _spread(A.PEAK_BASE[gk], PEAK_DRAW),
           A.PROFILE: (1, PROFILE_DRAW),
           MORALE: (1, MORALE_DRAW),
           FITNESS: (t_lo + 1, min(3 * t_hi, FITNESS_CAP))}
    if rating is None:
        rng[A.RATING] = ((1 + RATING_OFFSET) & 0xFF, (128 + RATING_OFFSET) & 0xFF)
    else:
        exact[A.RATING] = (rating + RATING_OFFSET) & 0xFF
    return {"exact": exact, "range": rng, "same_as": {ENERGY: FITNESS},
            "tactics": (old[TACTICS], tactics_bits), "initial": INITIAL_LETTERS,
            "surname": "kept", "ability_of_own_bytes": True, "same_rating_per_country": True}


def recreate_constraints(old, country_record=None):
    """F016's reduced form of 7E80's contract (T28; moved from ageing.py, which re-exports it):
    the bytes a capture a year earlier fixes, given the retiree's record `old` as the second
    pass saw it. {'exact', 'range', 'ability_of_own_bytes', 'same_rating_per_country'}:
    +0/+7 carried, +8..+0xB/+0x10/+0x11 = 0, +0x12/+0x13 = FF 7F; +1 in DS:110C[gk] +- 5, +2 in
    DS:0E80[gk] +- 2, +5 in 1..16 (ageing.py's constants, F016). With `country_record` (0xBF
    bytes, or the three rank bytes) +3 = country_rating + 0x7F is exact too. The complete
    contract is `recreate_contract`."""
    gk = 1 if old[A.CLUB_POSITION] == 0 else 0
    exact = {A.COUNTRY: old[A.COUNTRY], A.CLUB_POSITION: old[A.CLUB_POSITION],
             A.CAPS: 0, A.CAPS + 1: 0, A.GOALS: 0, A.GOALS + 1: 0, A.STATUS: 0,
             A.SCORER_COUNT: 0, A.PERFORMANCE: 0xFF, A.PERFORMANCE + 1: 0x7F}
    rng = {A.AGE: (A.RECREATE_AGE_BASE[gk] - A.RECREATE_AGE_SPREAD,
                   A.RECREATE_AGE_BASE[gk] + A.RECREATE_AGE_SPREAD),
           A.PEAK: (A.PEAK_BASE[gk] - A.PEAK_SPREAD, A.PEAK_BASE[gk] + A.PEAK_SPREAD),
           A.PROFILE: A.PROFILE_RANGE}
    if country_record is not None:
        exact[A.RATING] = (rating_of(country_record) + RATING_OFFSET) & 0xFF
    return {"exact": exact, "range": rng, "ability_of_own_bytes": True,
            "same_rating_per_country": True}
