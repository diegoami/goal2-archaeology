# E016 (T30, Q014): how retirements happen, how new players are made, and whether results feed new talent — the static map

Static first (rule 22): every claim below is read from `static/goal-exe/` — the named view
`named/` first, then the raw `code/` listing, with `calls.tsv`, `datarefs.tsv` and the initialised
data image `data/ds_2581_01.hex` closing the reader/writer sets. The prior finding F016 / T28
(`findings/F016-ageing-peak-band-and-yearly-writes.md`, the notes of `experiments/E014-q013-ageing/`)
is the stage-2, retirement-test, re-create and +3-as-country_rating context. Listing citations
are `file:line` with the routine address; addresses are the listing's own left column. No run
was needed to find any byte the re-create writes, the RNG entries it reaches, or the chain that
might bring results to a retiree.

## 1. The retirement test for computer countries (`1771:7F40`)

`1771:7F40(player)` (seg_1771_11.asm:949-998). On the AGED record (`7FDF`'s second pass,
:1086-1099 the call at :1098):

- `gk = record[+7] == 0` (:7F5D, byte compare; al = 1 if gk, else 0, then cwde into di);
- cap the test uses: `DS:0x110E[gk]` is the strict age limit, compared against `+1` (the AGE byte
  already incremented by `7E4A`): `cmp al, byte ptr es:[di + 1]; jae 0x7f84` (:7F74-:7F78).
  `DS:0x110E = 1E 21` (data/ds_2581_01.hex:143): 30 outfield, 33 goalkeeper;
- the caps clause: only when the age clause is OPEN (DS:0x110E[gk] strictly less than +1) does
  the caps test run: `cmp word ptr es:[di + 8], 0; je 0x7fa3` (:7F7D-:7F82) — both compared as
  16-bit (`83 7D 08 00` is a word compare per the `83` opcode). Equal zero closes the clause;
- when the age clause is closed (or caps nonzero), the peak clause runs:
  `peak + 5` (signed 16-bit +5, :7F87-:7F8D), then `cmp +1, peak+5; jg 0x7fa3` (:7F9B-:7F9D).
  The `jg` is a signed GREATER (so a player aged to peak+6 retires);
- result: 1 returned when the (age AND caps-zero) clause fired OR peak+5 < +1 (signed, strict);
  otherwise 0.

The test is deterministic; its callees are empty (`calls.tsv` 7F40 has none). It runs only for
computer countries and only at the year end (`7FDF`'s 0B77 branch, :1046; `7F40` is in the
else-branch at :1086-1099). Reading `DS:0x110E` is the only non-record data access.

```text
R = (DS:0x110E[gk] < +1 AND caps == 0) OR (+1 > peak + 5)
gk = (+7 == 0)
caps = word
DS:0x110E = 1E 21 (30 / 33)
```

## 2. The re-create of a retired computer-country player (`1771:7E80`) — every byte

`1771:7E80(player)` (seg_1771_11.asm:870-947, the routine `recreate_retired_player` in
`named/seg_1771_05.c`). Called from `7FDF`'s second pass at the year end, on the AGED record.
The routine address is read once at the top:

- `:7E83-7E97`: `local_6` ← record pointer `es:di + 20·player` from `[0xA91B]` (`7E58`: 0x14·player,
  `7E92` adds it; matches the F008 20-byte player record layout).
- `:7E9D-7EA3`: saves `bVar1 = record[+6]` (the player screen's old position, untouched by 7FB1/7E4A).

Then the deterministic calls:

- `:7EA6-7EC0`: `call 0x96d3` with stack `[+0][player]`, `[+7][player]`, `1[player]` — the
  __stdcall16far convention pushes right-to-left, so the call is
  `make_player(1, record[+7], record[+0], player)` — param_1=1 forces the re-create's
  `+3 = country_rating(country) + 0x7F` rule (no `−10 − rand(10)` for pool). make_player is
  `1771:96D3` (seg_1771_13.asm:1105-1201, the named view's `make_player`):
  - `:96ED-96FC`: writes `[player].country = arg_2 (= param_3 = record[+0])` — the carry-back of
    the OLD +0;
  - `:96F6-96FC`: writes `[player].club_position = arg_1 (= param_2 = record[+7])` — the
    carry-back of the OLD +7;
  - `:9700-970A`: copies `+7` to `+6` (position);
  - `:970E-971A`: `+5 = rand(0x10)` (`u214b_random_1_to_n`, returns 1..16 — `97` `97`
    `97` `97` `FB` `CF` are sequential `214B:06B1` far calls in seg_214B_02.asm);
  - `:971E-9756`: `+1 = DS:0x118A[+7==0] − rand(7) + rand(7)` (`DS:0x118A = 1C 1F` per
    data/ds_2581_01.hex:147 — 28 outfield / 31 goalkeeper; with two `rand(7)` draws in [1..7]
    the final +1 lies in base−6..base+6, i.e. 22..34 outfield / 25..37 goalkeeper). This draw
    is consumed by the LCG on the re-create path even though 7E80 OVERWRITES +1 at :7EF9 with
    its own `DS:0x110C[gk] ± rand(6) − rand(6)` draw — the make_player's draws still shift the
    LCG for downstream draws of the same year end.
  - `:975B`: `roll_peak_age` (1771:3291, seg_1771_05.asm:243-281): two `214B:06B1(3)` draws
    (32AB-32BF) give +2 = `DS:0x0E80[+7==0] + rand(3) − rand(3)`. `DS:0x0E80 = 1B 1E` so peak
    25..29 outfield, 28..32 goalkeeper (`:32D3-32DB`, :32DC-32E1 store it). NOT REACHED by the
    re-create path either (the carry is already from make_player's own call).
  - `:9764-9775 (param_1 != 0)`: `+3 = country_rating(country) + 0x7F` — `country_rating` at
    `1771:10E7` (seg_1771_02.asm:697-738, named `country_rating`): the call at `:9768`
    `call 0x10e7` with the country arg, then `add ax, 0x7F` at `:976B`. `country_rating(country)`
    itself reads the country record +0x2C/0x2A/0x2B at `:1104-1137`:
    ```
    ax = (5 − continent) · (33 − continent_rank) + (129 − world_rank)   ; signed 16-bit
    ax = idiv 2                                                       ; signed
    ```
    so a higher world_rank (better country) ⇒ LOWER (129-world_rank) ⇒ LOWER rating ⇒ WORSE
    prospective `+3`. The strongest countries (world_rank 1) yield a rating of
    `(5-cont)·(33-cr) + 128` divided by 2; the weakest (world_rank 128) yields
    `(5-cont)·(33-cr) + 1` divided by 2. Note: better results lower world_rank, so better results
    LOWER the `+3` of the next cycle's re-creates — the chain exists; the reading is the
    opposite of "results → talent" being a simple "+talent"; see section 4 for the full chain.
  - `:979C`: `compute_ability(player)` recomputes +4 from the new +1/+2/+3 (32EB, seg_1771_05.asm
    :282-370; the F016 plateau of p−1..p+3, the F016 wrap past p+19).
  - `:97A2-97AB`: `+0xC = rand(0x20)` (morale).
  - `:97B3`: `set_player_tactics` (1771:3431, the player's own-tactics default writes of
    seg_1771_05.asm).
  - `:97BA`: `roll_fitness_energy` (1771:3558, seg_1771_05.asm:223+/the fitness /energy draws).
  - `:97C0`: `performance = 0x7FFF` (the "blank" sentinel).

After make_player, `7E80` continues:

- `:7EC3-7EF9`: two `214B:06B1(6)` draws (the order matters — `cVar3` then `cVar2`):
  `:7EC7` first rand(6) saved on stack, `:7ED1` second rand(6) assigned to `dx`. Then
  `ax = DS:0x110C[+7==0] + second_rand`, `sub ax, first_rand`, stored as the new `+1`. So
  `+1 = DS:0x110C[gk] + rand(6) − rand(6)`, range DS:0x110C[gk] − 5 .. DS:0x110C[gk] + 5.
  `DS:0x110C = 19 1C` (data/ds_2581_01.hex:143) so 20..30 outfield, 23..33 goalkeeper.
  - Calls.tsv: 7E80's RNG draws are exactly these two `214B:06B1(6)` calls plus make_player's
    (which uses 0x10, 7, 7 — `21 4B 06 B1` calls) plus `roll_peak_age`'s two 0x10-3 draws (NOT
    reached on the re-create path), plus the LCG byte from `1771:0000` (:7F1F).
- `:7EFD-7F01`: `call 0x32eb` — `compute_ability(player)` again, with the OVERWRITTEN +1 (the
  one written at :7EF9). This computes +4 from +1 (new), +2 (set by make_player at 975B), +3
  (= country_rating+0x7F). The first compute_ability at make_player used the values as make_player
  drew them — for the re-create path that means `+1 = DS:0x118A[gk] − rand(7) + rand(7)`,
  `+2 = DS:0x0E80[gk] + b − a` and `+3 = country_rating+0x7F`. The second compute_ability
  after the +1 override recomputes with the final new +1.
- `:7F04-7F09`: `[player].caps = 0` (`F09` is `mov word ptr es:[di + 8], ax` with ax = 0 from
  :7F07 xor ax,ax).
- `:7F0D-7F12`: `[player].goals = 0` (word). +0xA is bytes 0xA,0xB.
- `:7F16-7F19`: `[player].status = 0` (`mov byte ptr es:[di + 0x10], 0`).
- `:7F1E-7F2D`: `[DS:9B70] + player = f_1771_0000()` — a new initial byte from the LCG. The
  surname is unchanged.
- `:7F30-7F36`: `[player].position = old_+6` (the byte saved at :7E9D-7EA3 / :7F30 `mov al, [bp-2];
  :7F33-7F36 stores it). This `+6 = old +6` is the F008 "which shown cell each feeds is static
  only" — the position the new player inherits from the retiree.
- `:7F3A-7F3D`: ret 2.

### 2.1 The re-create's byte set

What `7E80` writes, listing line by line:

| offset | writes | source line | deterministic? |
|---|---|---|---|
| +0 (country) | record[+0] (make_player arg) | 7EAC, 96F3 | yes — carry from old |
| +1 (age) | DS:0x110C[gk] + rand(6) − rand(6) | 7EF9 | NO (LCG state) |
| +2 (peak) | country_rating(country) + 0x7F... wait that's +3. +2 from make_player: roll_peak_age sets it. But the re-create entry DID call make_player which set +2 via roll_peak_age. Hmm — see "roll_peak_age from make_player" below — +2 is reached via the make_player call at 7EC0 (just before 7EC7), so it is set. | 975B+32E1 | NO (LCG state for the peak draw) |
| +3 (rating) | country_rating(country) + 0x7F | 976B+9771 | depends on country record state |
| +4 (ability) | compute_ability of (final +1, +2, +3) | 33C3 | deterministic given +1/+2/+3 |
| +5 (skill_profile) | rand(0x10) | 971A | NO (LCG state) |
| +6 (position) | old +6 | 7F36 | yes — carry from old |
| +7 (club_position) | record[+7] (make_player arg) | 96FC | yes — carry from old |
| +8/+9 (caps) | 0 | 7F09 | yes |
| +0xA/+0xB (goals) | 0 | 7F12 | yes |
| +0xC (morale) | rand(0x20) | 97AB | NO |
| +0xD (fitness) | DS:0x78D5[+0xD], drawn by roll_fitness_energy | 3558 | NO (the draws) |
| +0xE (energy) | DS:0x78F6[+0xE], drawn by roll_fitness_energy | 3558 | NO (the draws) |
| +0xF (own_tactics) | set_player_tactics 3431 | 97B3 | deterministic (the routine) |
| +0x10 (status) | 0 | 7F19 | yes |
| +0x11 (scorer_count) | unchanged (= 0, since 7FB1 cleared it in the first pass) | — | yes (zero) |
| +0x12/+0x13 (performance) | 0x7F 0xFF | 97C0 | yes |
| [9B70] + player (initial) | f_1771_0000() | 7F1F-7F2D | NO (LCG state) |
| surname | unchanged | — | yes |

The deterministic bytes (exact), given the old record and the country record at re-create time:

```python
exact = {
    COUNTRY:           old[COUNTRY],
    CLUB_POSITION:     old[CLUB_POSITION],
    CAPS:              0, CAPS+1: 0,
    GOALS:             0, GOALS+1: 0,
    STATUS:            0,
    SCORER_COUNT:      0,                      # 7FB1's first pass cleared it; 7E80 writes nothing here
    PERFORMANCE:       0xFF, PERFORMANCE+1: 0x7F,
    POSITION:          old[POSITION],          # carry
}
```

The drawn bytes (range), given `gk = (+7 == 0)`:

```python
range = {
    AGE:       (DS_110C[gk] - 5, DS_110C[gk] + 5),   # rand(6) is 1..6
    PEAK:      (DS_0E80[gk] - 2, DS_0E80[gk] + 2),   # rand(3) is 1..3
    PROFILE:   (1, 16),                                # rand(0x10)
    # MORALE, FITNESS, ENERGY, INITIAL drawn but the model does not predict exact bytes unless the
    # LCG state is known — see section 5.
}
```

`+3 = country_rating(country) + 0x7F` is FIXED PER country in one 7FDF call: the country record
is read but `+0x2A/+0x2B/+0x2C` are not written between two re-creates of the same 7FDF call
(`0177:7FB1` and `0177:7F40` and `0177:7E80` walk squad slots but never touch the country
record; `make_player` doesn't either — verified by all writers of `[di + 0x2A..0x2C]`: only the
seasonal recompute `0177:63A4` writes them, and it runs OUTSIDE the 7FDF loop, between stage
transitions; see section 4).

### 2.2 The RNG draws in the re-create path — the exact sequence

In order of consumption by `7E80` (called from `7FDF`'s second pass at the year end):

```text
[7F40 — retirement test, deterministic, NO RNG entry — see section 1]
call 1771:7E80            ; the re-create path
  call 1771:96D3          ; make_player(1, old+7, old+0, player)
    214B:06B1(0x10)        ; +5 = rand(0x10)              (1 draw, 1..16)
    214B:06B1(7)           ; +1 = base − rand(7)         (the THIRD rand of +1; 1 draw, 1..7)
    214B:06B1(7)           ;                                then base+ (NEW rand, 1..7)
    call 1771:3291         ; roll_peak_age
      214B:06B1(3)         ; b = rand(3)               (the THIRD rand of +2; 1 draw, 1..3)
      214B:06B1(3)         ; a = rand(3)               (NEW; 1 draw, 1..3)
    call 1771:10E7         ; country_rating → +3
    call 1771:32EB          ; compute_ability
    214B:06B1(0x20)         ; +0xC morale (1 draw, 1..32)
    call 1771:3431          ; set_player_tactics (deterministic given +7/+6/+5)
    call 1771:3558          ; roll_fitness_energy (3 draws?)
    performance = 0x7FFF
  214B:06B1(6)              ; first rand of +1 (stored)
  214B:06B1(6)              ; +1 = DS:0x110C[gk] + SECOND_RAND(6) - FIRST_RAND(6)
  call 1771:32EB            ; compute_ability again — note the order matters
  214B:0018(0, 0x14, +0/+7/...) nope
  caps = goals = status = 0
  call 1771:0000            ; initial byte
  position = old_position
```

(The +1 / roll_peak_age draws inside make_player are NOT used by the re-create's final bytes:
the re-create overwrites +1 at 7EF9 with its OWN draws from `DS:0x110C[gk] ± 5`, and roll_peak_age
has set +2 once — make_player's draws for +1/+2 are wasted on the re-create path because they
are overridden. The runs do consume the LCG though, so they shift the RNG state for any subsequent
draw in the same year end; tests must not assume the LCG skips.)

### 2.3 Note on the ACTIVE age compute

Order matters: `7E80` calls `make_player`, which calls `compute_ability` at `:979C-979F`. Then
`7E80` overrides `+1` at `:7EF9`, then calls `compute_ability` again at `:7F01`. The final
`+4` is from the SECOND call, which used the OVERRIDDEN `+1`. This matters because:
- `make_player`'s `compute_ability` runs at `+1 = DS:0x118A[gk] − rand(7) + rand(7)` (28±6/31±6);
- `7E80`'s `compute_ability` runs at `+1 = DS:0x110C[gk] + rand(6) − rand(6)` (25±5/28±5).

The two ages DIFFER. So the +4 byte of a re-created player is the result of
`compute_ability(DS:0x110C[gk] ± 5, peak, country_rating+0x7F)`,
NOT `compute_ability(DS:0x118A[gk] ± rand-symmetric, peak, country_rating+0x7F)`.

The full byte sequence make_player draws for a re-create:

1. `+5 = rand(0x10)` — :9711-971A
2. `+1a = rand(7)` (the THREE-draw slot) — :9722-972C
3. `+1b = rand(7)` — :972C-9732
4. (roll_peak_age, which draws two `rand(3)` :32AF-32B9) — :975B call
5. (country_rating, no RNG)
6. (compute_ability with the OLD new +1 / +2 / +3) — :979C call
7. `+0xC = rand(0x20)` — :97A3-97AB (morale)
8. (set_player_tactics 3431, no RNG)
9. (roll_fitness_energy 3558 — its draws)
10. (LCG byte for no record write here)

Then `7E80`'s overrides/draws:

11. `+1 = cVar3(cVar4) = ...` Actually the order is reversed — :7EC7 stores first rand,
    :7ED1 stores second rand; :7EF9 final `+1 = DS:0x110C[gk] + cVar4 - cVar2`. The earlier
    variable-c is `(cVar3, then cVar2) := (rand(6), rand(6))` with `cVar3` first on stack — but
    the SUBTRACTION order is `+rand(cVar3) - rand(cVar2)` where cVar3 is the FIRST rand and
    cVar2 is the SECOND. So +1 = DS:0x110C[gk] + first_rand - second_rand, range DS:0x110C[gk]
    − 5 .. DS:0x110C[gk] + 5.
12. compute_ability — :7F01
13. `+0x11 = 0` (well, +0xC was already set, but I mean write to it — see actual writes below)
14. (LCG byte from `1771:0000` for the initial at :7B70 + player)

## 3. The managed-country retirement replacement path

For a MANAGED country, the main menu's offer to retire a player is reached from `000E:57E5`
(seg_000E_07.asm:381-526, `f_000E_57E5`). It walks the 20 squad slots 1..20, calls
`1771:7F40(retirement_test)` for each, and on retirement calls `000E:56F3`
(seg_000E_07.asm:287-379, `f_000E_56F3`). `56F3` runs the retirement news (`000E:50D4` if any),
two `1771:1B2E` calls to update the squad book, then `1771:4CF7` to obtain a NEW player number
(a free pool slot), then writes the new index into either the squad slot or the pool (the
manager-record `+0x4D` byte, "the new index is in the pool" indicator), then calls
`000E:54F0` to make the new player. If no squad retiree is available, `57E5` falls through to
a pool walk (drawn from `rand(0x50)` + base, `:58A3-:58CE`).

`000E:54F0(new_player_index, retiree_index)` (seg_000E_07.asm:83-285, `f_000E_54F0`):

- pushes (new_index, retiree[+7], 1) and `call far 1771:96D3` (`:5534-5539`) — the same
  `make_player(1, retiree[+7], country, new_index)` as 7E80's call, but with `country` from
  the menu's frame, not from `retiree[+0]`;
- two `214B:06B1(6)` draws (`:553D-5542`, `:5547-554C`) and `+1 = DS:0x78[gk] + rand − rand`.
  `DS:0x78 = 19 1C` (data/ds_2581_01.hex:10) — same as `DS:0x110C`. So the BASE ages are
  `25 / 28` (outfield / goalkeeper), with `±rand(6) − rand(6)` spread `5`: same range as
  7E80 (20..30 / 23..33);
- compute_ability for the new +1 — `:557A-5582`;
- caps = goals = status = 0 — `:5584-:5596`;
- `1771:0000()` for the new initial at `[DS:9B70] + new_player_index` — `:5599-:55AD`;
- after the make_player returns, the rest of `54F0` (`:55B0-:56CB`) is "young squad" detection
  — counts how many of the squad / pool players are younger than `DS:0x76[gk] + 4`; if younger
  than 0x14 (= 20) of them, override with `+1 = DS:0x76[gk] + rand(3)` and re-`compute_ability`
  (`:56B4-:56E8`). So when few young players are present in the squad/pool, the managed
  retirement replacement gets a YOUNGER age (`+1 = DS:0x76[gk] + rand(3)`, with a draw of 1..3).

This path is OUT OF SCOPE for the Q014 model (the brief lists it as the BOT's
"transfers between countries" — the managed retirement replacement is a user-initiated offer).
The bytes the path writes follow the same make_player contract as 7E80, with `+3 =
country_rating(country) + 0x7F` (param_1 = 1, so the same form). So the BOT's claim "do results
feed talent for managed countries" would also be YES, with a possible age override at the end.

A `runtime/model/recreate.py` PREDICTOR for this path would mirror `recreate_constraints` but
consume the LCG state (4 RNG calls per re-create plus the make_player's draws), and apply the
young-squad override when `count_young < 20`. The current task does not model it: the brief
says "the bot" is out of scope, and the model here is for the COMPUTER retirement re-create
that the 38 E014 re-creates exercise.

## 4. Results and talent — does anything a country's results change reach a re-created player's bytes?

The chain from results to a re-created player's `+3`:

```
country results (points/wins/goal diff, scored over a stage)
   ↓
written into the points/wins/diff byte of [DS:A923] + ... + [A91F+...]  ; per side per manager
   ↓
on entry to stages 2 / 5, 0177:6730 (stage_qualifying, seg_1771_09.asm:1092-1164) calls
0177:63A4 (recompute ranks) which sorts countries by points (0177:602D for stages 2,3,4
world qualifying, 0177:6103 for stages 5,6,7,8 finals — chosen by [A923]+0x40 = (stage > 4))
and writes either [country]+0x2B = world_rank or [country]+0x2A = continent_rank.
   ↓
at the year end, 0177:8208 (stage_end) calls 0177:80DA (yearly_ageing) → 0177:7FDF →
0177:7F40 → 0171:7E80 → 0177:96D3 (make_player) which calls 0177:10E7 (country_rating)
which READS +0x2A/0x2B/0x2C off the country record (seg_1771_02.asm:1116/112A/1104).
country_rating = ((5 - continent) * (33 - continent_rank) + (129 - world_rank)) / 2   ; signed
   ↓
+3 = country_rating + 0x7F    (1771:96D3 :976B add ax, 0x7F; :9771 store al to es:[di+3])
```

So YES: results DO feed new talent. The direction is:
- A country with a BETTER world_rank (smaller +0x2B) gives +3 a LARGER value of
  (129 - world_rank) → country_rating is LARGER → +3 is LARGER. So a country that does better
  produces re-created players with HIGHER `+3` (and therefore higher `+4` ceilings).

BUT, the timing matters:

- Stage transition ordering: per `000E:70B9` (play_round, seg_000E_09.asm:475-542), the calls
  are `:70E6 call 1771:8208` THEN `:70F4 call 1771:76B1`. So ageing happens BEFORE run_stage.
- `8208` calls `80DA` for new stage ∈ {2,3,5,7} (`:162-163`). `80DA` ages every country in
  `7FDF`, which re-creates via `7E80` (`:1106`). The country's +0x2A/+0x2B are what they were
  BEFORE this stage transition's rank recompute.
- `76B1` dispatches the new stage; for stages 2 and 5 it routes to `6730`, which calls `63A4`
  ONLY when `[A923]+0x38 > 0` (the year counter, seg_1771_09.asm:1111-1112). So the rank
  recompute at stage 2/5 entries uses points from the PRECEDING stage's results.

Therefore: when a country loses or wins its matches, the change in points during THIS stage's
matches is not reflected in the +0x2A/+0x2B until the NEXT stage 2/5 entry — and even then, the
ageing of THAT stage 2/5 entry has already run with the OLD ranks.

Concrete: at the entry to stage 5 (finals qualifying), the COMPUTER-side re-creates for the
finals use the world_rank from the world-qualifying stage 2 entry (i.e. WORLDCUP qualifier
results). At the entry to stage 2 of the next cycle, re-creates use the continent_rank from the
last stage 5 entry (FINALS results). The world_rank and continent_rank read by `country_rating`
in the re-create were both LAST refreshed at the most recent stage 2 / stage 5 entry BEFORE
the current ageing — i.e. on average (over a season's 4 re-creates) reflecting results from at
least one cycle earlier.

So the precise finding is: a re-created player's `+3` is `country_rating(country) + 0x7F` where
country_rating reads `+0x2A/+0x2B/+0x2C` last written at the most recent stage 2 (world_rank)
or stage 5 (continent_rank) entry BEFORE this year's ageing — which reflects the PRECEDING
season's results in those competitions. The CHAIN EXISTS. It is INDIRECT (1-cycle lag for
world_rank) and PER-SIDE (+0x2B updates in world stage, +0x2A in finals stage).

Are there any other reads of `+0x2A/+0x2B/+0x2C` by an actual player-byte writer? No — `grep`
for writers finds only `1771:63A4` (`+0x2B`, `+0x2A`), and the helper `1771:114B` is a
country-info panel score, not a writer. So `+3` is the ONLY player byte that depends on
results.

Are there other results-driven bytes? The country rating also drives `manager_countries[3*m + 1]`
(the manager's score byte at `1791:114B`, line 84 in the decompiled view, written at
seg_1771_05.c:84) — but this is a manager record, not a player record. So:

- Q014's claim "do results feed new talent?" → YES, via `+3 = country_rating + 0x7F`.
- The direction: better results → smaller world_rank → larger (129 - world_rank) → larger
  country_rating → larger `+3`.

## 5. The RNG state at a year-end savestate — can it be recovered?

The LCG state is the single 16-bit word `DS:0x7B62` (per F004's annotation:
`0177:6730 re-seeds DS:7B62 from the DOS time`); `0177:0000` returns a byte from it, `214B:06B1`
is the only consumer. Both are called multiple times per re-create (section 2.2). The state
is therefore not recoverable from a single savestate without reading `DS:0x7B62` itself (the
savestate must include the byte image, which it does for DOSBox-X's `Vga`+`Memory` components).
E014 reads include the whole process memory, so `DS:0x7B62` is reachable — but the model
reproduces the deterministic bytes and the drawn-byte ranges, which suffices for check_ageing
without recovering the LCG. The model **does not** pretend to know the drawn bytes exactly;
that is a `[Likely]` carve-out in section 2.1.

## 6. Where the records (E014) corroborate — six records, 38 re-creates

`runs/E014/E014-r000{01..06}.json` capture 5 stage transitions across 6 sessions (r0001-r0004
aborted, r0005 + r0006 carry 5 corroborating pairs). `experiments/E014-q013-ageing/check_ageing.py`
checks every squad player with the F016 model; its `replacement_errors` uses
`ageing.recreate_constraints(old)` (the function this task moves to `runtime/model/recreate.py`
unchanged in semantics) and additionally requires:
- `+4 = compute_ability(+1, +2, +3)` of the new bytes (the model's `ability_of_own_bytes`
  invariant, section 2.1, line 2);
- all `+3` (country_rating + 0x7F) of one country in one 7FDF call are equal (the
  `same_rating_per_country` invariant, section 2.1, line 1).

E014's `300/300` check_ageing match (T28) is the only behavioural evidence this task needs:
the static map above was read from the listing, the records corroborate the deterministic bytes
and the per-country +3 invariant, the per-byte draws are bracketed by their ranges and can be
predicted exactly only when the LCG state is in hand.

## 7. Files this task creates / changes

- `experiments/E016-q014-retirement/notes.md` — this file
- `experiments/E016-q014-retirement/check_recreate.py` — checker, mirrors check_ageing
- `runtime/model/recreate.py` — NEW, holds `recreate_constraints` + helpers (moved from
  `runtime/model/ageing.py` and re-exported there as the brief's note says)
- `runtime/model/ageing.py` — keep a re-export so `import ageing` keeps working
- `runtime/README.md` — the moved constants are listed
- `tests/test_model_recreate.py` — literal-record, literal-expected tests; mutation tests
- `tests/static/test_annotations.py` — re-add the F017 routines to the routine-naming-check
- `findings/F017-retirement-and-talent.md` — the proposed finding (T28-style claim-by-claim)
- `static/goal-exe/annotations/routines.tsv` (+ globals, fields) — F017's reader/writer rows
- `static/goal-exe/named/…` — regenerated

The new annotation rows the brief implies (and that `check_annotations.py` then verifies):

| routine | name | basis |
|---|---|---|
| `000E:54F0` | `create_managed_replacement` (likely) | this task: draws +1 from `DS:0x78[gk] ± rand(6)` (a 54F0-specific base — distinct from `0x118A`) |
| `000E:56F3` | `replace_retiree` (likely) | this task: zero-pad the retiree record before continuing to the offer path |
| `000E:57E5` | `offer_retire_player` (likely) | F011 + this task: walks squad slots for retirement, then pool |
| `000E:6730` | `stage_qualifying` | exists (F004 / F007) — base, no change |
| `0177:63A4` | `recompute_country_ranks` (established) | this task: writes +0x2A/+0x2B from points, gated by stage |
| `0177:6730` | `stage_qualifying` | exists — no change |
| `0177:7E80` | `recreate_retired_player` | exists — annotation already covers section 2 |
| `0177:7F40` | `retirement_test` | exists — annotation already covers section 1 |
| `0177:96D3` | `make_player` | exists — annotation row carries section 2 paragraph |
| `0177:10E7` | `country_rating` | new annotation row (the three-byte formula, signed divide) |
| `1771:114B` | `update_manager_score` (likely) | this task: writes the manager's score byte per cycle |
| `0177:0000` | `lcg_byte` (likely) | this task's RNG-byte reader |
| `214B:06B1` | `u214b_random_1_to_n` | exists |
