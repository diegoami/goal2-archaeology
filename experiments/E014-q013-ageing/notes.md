# E014 (T28, Q013): how skills change with age, and the peak age — the static map

Static first (rule 22): every claim below is read from `static/goal-exe/` — the named view
`named/` first, then the raw `code/` listing and `decompiled/`, with `calls.tsv`, `datarefs.tsv`
and the initialised data image `data/ds_2581_01.hex` closing the reader/writer sets. Listing
citations are `file:line` with the routine address; addresses are the listing's own left column.
No run was needed to find the loop or its rule; the runs (`runs/E014`) corroborate (section 6).

## 1. The yearly chain: who calls the ageing loop, and when

The ageing loop is **not** in `000E` near `50D4` (the retirement news) as F008's candidate note
suggested; it is `1771:7FDF` per country, reached from the stage machinery:

1. `000E:70B9` (play_round; annotation, F004) plays the stage's fixtures; when the fixture index
   `[A923]+0x26` reaches the count `+0x28` it calls `1771:8208` (seg_000E_09.asm:492), then
   `000E:7072` and `1771:76B1` (run_stage), and, when the new stage is in the set `CS:7099`
   (seg_000E_09.asm:500-508; the set byte is 0xAC, data row seg_000E_09.asm:471 = bits 2, 3, 5,
   7), `000E:60CB` per manager whose `+0x47` flag is clear — the new-season screen
   (seg_000E_09.asm:509-556, the call at :534).
2. `1771:8208` (seg_1771_12.asm:122-186) decrements the state's rounds byte `+0x3D`
   (:126-131) and returns while it is positive. At 0 it:
   - advances the stage byte `+0x3C` by 1, wrapped into [2, 8], through `214B:1D6F`
     (`u214b_wrap_add_in_range_byte`; :143-155: the far pointer to `+0x3C`, then 2, 8, 1 —
     annotation "wraps a byte variable by a delta inside [lo, hi]"). The stage order is
     2→3→4→5→6→7→8→2…;
   - tests the NEW stage against the set `CS:81E8` (:156-163; `23E4:08DF` is the Pascal-set
     membership test, annotation). The set byte at `CS:81E8` is 0xAC (data row
     seg_1771_12.asm:118) = {2, 3, 5, 7}: the ageing runs on entry to those four stages, and
     only there (:163 `call 0x80da` is skipped by the `je` at :162);
   - sets `+0x40` = (stage > 4) and the next rounds count `+0x3D` = 1 + (stage == 4) +
     3·(stage == 8) (:164-181).
3. `1771:80DA` (seg_1771_12.asm:7-119) loops countries 1..0x80 and calls `1771:7FDF` for each
   (:17-30). Then it tests the stage against `CS:80BA` = 0x24 (data row seg_1771_11.asm:1115) =
   {2, 5} (:31-38): only on entry to stage 2 or 5 does it increment the year word `[A923]+0x38`
   (:34) and run the new-season country housekeeping (managed-country ranking copy :41-73;
   `+0x41`→`+0x3B` move of 0x36 bytes via `214B:003C` :74-84; `+0x3B` 6 bytes zeroed via
   `214B:0018` :85-95). The housekeeping writes country records, not player records — outside
   this task.
4. `000E:7439` (main_menu_loop) reaches play_round on Enter with item 6 "after `000E:57E5` and
   `000E:5CF4` return 0" (F004; seg_000E_09.asm — the menu loop's call of 70B9) — so the
   offer/promise path `57E5` (section 4) runs from the menu, separately from the yearly loop.

So one 4-year cycle = one pass of stages 2..8; the players age **four times per cycle**, on entry
to stages 2, 3, 5 and 7 — one ageing per displayed year: the displayed year is
`2·(+0x38) + (+0x3A)` (`000E:5978`, named/seg_000E_04.c:691 decompiled line; fixture dates add
`(+0x40 != side)·(−2)`, decompiled/seg_1771_04.c:40-41), `+0x38` increments twice per cycle
(stages 2 and 5) and `+0x3A` is the new-game base year (init_new_game `1771:9B85`,
seg_1771_14.asm:394-400 area, annotation; the state word write `9BF0` area). New games start at
stage `DS:118E[+0x40]` = 2 or 5 (`data/ds_2581_01.hex:147`, offset 118E = `02 05`).

## 2. The per-country loop `1771:7FDF` and the per-player write `1771:7FB1`/`7E4A`

`1771:7FDF(country)` (seg_1771_11.asm:1021-1112, named/decompiled `f_1771_7FDF`):

- country record = `[A917] + country·0xBF` (:1025-1031); squad slots 1..20 are the words at
  country `+0..+0x27` (F011), read at `800B push word ptr es:[di - 2]` with the loop counter
  1..0x14 (:1032-1045);
- **first pass, every squad word** → `1771:7FB1(player)` (:1043);
- then `1771:0B77(country)` (is_managed, :1046-1049):
  - **managed** (nonzero): the manager's pool is aged too — base = `DS:6D18[+0x2E − 0x80]`
    (:1050-1064), the 80 words `[A927] + 2·i`, i = base..base+0x4F (:1065-1085), each →
    `7FB1`. No retirement test runs for a managed country here;
  - **computer**: a second pass over squad slots 1..20 → `1771:7F40(player)` (the retirement
    test, :1086-1099, the call at :1098) and, when it returns 1, `1771:7E80(player)`
    (re-create, :1100-1107, the call at :1106).

`1771:7FB1(player)` (seg_1771_11.asm:1001-1018): calls `1771:7E4A(player)` (:1013), then writes
**`+0x11` = 0** unconditionally (:1015, `7FD4 mov byte ptr es:[di + 0x11], 0`).

`1771:7E4A(player)` (seg_1771_11.asm:845-868): skips player 0 (`7E64 cmp word ptr [bp + 4], 0`
/ `jne`, :856-858), else **increments `+1` (age)** (:861, `7E6F inc byte ptr es:[di + 1]`,
wraps at 255) and calls `1771:32EB(player)` (compute_ability, :864).

**The complete set of per-player bytes the yearly loop writes on a continuing player is
{+1, +4, +0x11}**: `+1` by `7E6F`, `+4` by compute_ability (section 3), `+0x11` by `7FD4`.
Evidence that nothing else writes the record in this path: `calls.tsv` gives 7FDF's callees
(0B77, 7E80, 7F40, 7FB1), 7FB1's (7E4A), 7E4A's (32EB) and 32EB's (none); 32EB's only record
writes are `+4` (seg_1771_05.asm:312 `333A` and :366 `33C3`, both `mov byte ptr es:[di + 4],
al`). **+2 (peak age) never moves in the yearly loop**: its only writer is `roll_peak_age`
(`1771:3291`), whose only caller is `make_player` (`1771:96D3`; calls.tsv) — the creation path.
The loop writes neither +2, +3, +5, +6 nor +7 (the task's "+5 profile, +7 club position?" is
answered: untouched; only the retirement re-create 7E80 redraws them, section 4). **+0x11's only
writer in the whole program is `7FD4`**: every other `es:[di + 0x11]` access in `code/` is
0791's 22-byte pitch record (a different struct — grep over the listing, e.g.
seg_0791_04.asm:246, seg_0791_18.asm:677), and no reader of the player's +0x11 exists (F008:
"of the 20 bytes only +0x11 is not read by the screen's routines"; the named view has no
`players[n]` field for it and no raw `·0x14 + 0x11` read — the only `0x14 + 0x11` hit in
`decompiled/` is the write itself, seg_1771_05.c:288).

## 3. The peak-age rule: `compute_ability` `1771:32EB` (seg_1771_05.asm:283-370)

With a = age (+1), p = peak (+2), r = rating (+3), each a zero-extended byte:

- **band test** (:296-311, `3305`-`332E`): `a < p` (`3313 jb`) or `a > p + 3` (`332E jg`,
  16-bit compare of zero-extended bytes) leaves the band; inside it (`p <= a <= p + 3`)
  **`+4 = r`** (:312, `333A`);
- **above the band** (:337-347, `3366 jle` skips it): `k = a − (p + 3)`;
- **below the band** (:348-361, `338D`-`33B0`): `k = (p − a) idiv 2` — a SIGNED divide by 2
  (`33A3 cdq`, `33A7 idiv cx`; p > a here, so floor((p−a)/2));
- **the scale** (:362-366, `33B3`-`33C3`): `factor = 0x10 − k` as a 16-bit word (`3386`/`33AE`
  `sub ax, dx` — wraps when k > 16), then `+4 = low byte of ((r · factor) mod 65536) div 16`:
  `33B6 mul word ptr [bp - 2]` (unsigned 16×16→32), `33B9 xor dx, dx` DISCARDS the high
  product, `33BB-33BE div cx` with cx = 0x10 (unsigned), `al` stored (:366).

So ability **rises** by r/16 per two years below the band, equals the ceiling r inside the band
p..p+3 (four ages), and **falls** by r/16 per year above it — the backlog's "rise to a peak,
fall after", with the peak a 4-age band, not one year. The peak differs per player from
creation: `roll_peak_age` `1771:3291` (seg_1771_05.asm:242-281) draws
`+2 = DS:0E80[gk] + b − a` with a then b = `214B:06B1(3)` (rand 1..3; :249-260), gk = (+7 == 0)
(:261-270, `32C3-32CE`), and stores at `32E1` (:277); `DS:0E80 = 1B 1E`
(data/ds_2581_01.hex:123) → peak 25..29 outfield, 28..32 goalkeeper. F008's byte check
(`+2` set to 0/0xFF changes 2 shown values) is consistent: the screen reads +2 only for the
two-footed test; the ageing rule reads it every year.

**No randomness in the yearly path**: calls.tsv shows 8208, 80DA, 7FDF, 7FB1, 7E4A, 32EB and
7F40 call no RNG routine (the RNG entry points are `214B:06B1`, `214B:0674`-family and
`1771:0000`; none appears in those callee rows). The ageing of a continuing player is
deterministic given its record — the year-to-year variance between players is the creation draw
(+2, +3), not a yearly draw. `1771:6730` (stage_qualifying) re-seeds `DS:7B62` from the DOS
time on entry to stages 2/5 (annotation, F004) — AFTER the ageing of that transition (8208
calls 80DA, and play_round calls 76B1 only afterwards, seg_000E_09.asm:492-500).

## 4. The retirement test `1771:7F40` and the re-create `1771:7E80` (context; Q014's territory)

`1771:7F40(player)` (seg_1771_11.asm:950-1000, `7F40`-`7FAE`): retires when
`(DS:110E[gk] < +1 AND the caps word +8 == 0) OR (+1 > +2 + 5)` (`7F5A-7F9D`: gk = (+7 == 0) at
`7F5D-7F6A`, the limit compare at `7F74-7F78`, the caps test at `7F7D-7F82`, the peak+5 compare
at `7F87-7F9D`; `DS:110E = 1E 21` = 30 outfield / 33 goalkeeper, data/ds_2581_01.hex:143). No
RNG. It runs at the year end **only for computer countries** (7FDF's 0B77 branch); for the
managed country the same test drives the menu's offer path `000E:57E5` → `000E:56F3` (the
retirement news `000E:50D4`, the promise line `000E:544D`, the new player `000E:54F0`), which
is RNG-selected (`57E5` draws `u214b_random_1_to_n(0x50)` over the pool; `54F0` draws rand(6)
twice for the age and rand(3) for the young-squad check — named/seg_000E_04.c:646-710) and is
Q014's subject, not modelled here.

`1771:7E80(player)` (seg_1771_11.asm:871-948, `7E80`-`7F3D`) replaces a retired
computer-country player: `make_player(1, old +7, old +0, player)` (`7EA6-7EC0`) re-draws +5, +2
(roll_peak_age), +3 = country rating + 0x7F (make_player's param_1 ≠ 0 branch,
named/seg_1771_06.c:904-906), morale, tactics, fitness/energy, performance = 0x7FFF; then age
`+1 = DS:110C[gk] + rand(6) − rand(6)` (`DS:110C = 19 1C` = base 25/28; `7EC3-7EF9`),
compute_ability (`7F01`), caps +8 = 0 (`7F09`), goals +0xA = 0 (`7F12`), status +0x10 = 0
(`7F19`), a new name-initial byte at `[DS:9B70] + player` from `1771:0000` (`7F1E-7F2D`), and
`+6 = old +6` restored (`7F30-7F36`). All RNG — a year-end prediction cannot give a replaced
player's new bytes without the LCG state and every draw of the year between; the predictor marks
such players "replaced" (the predicate is deterministic) and does not predict their bytes
(Q014).

## 5. The derived-skill consequence (F015/F008)

The engines read skill element e as
`DS:6DCD[12·(+5) + DS:6D25[12·(+7) + e]] · ((+4)+1) div 32` (`1771:3A06`,
seg_1771_05.asm:1032-3A7F area, `div 32` at `3A71-3A74`; F015). The yearly loop changes only +4
of the three inputs (+5, +7 untouched, section 2), so one year of ageing scales all twelve
engine skills by the same ratio of `(new +4 + 1)` to `(old +4 + 1)` under that integer
division — inside the band the skills rise to the profile's ceiling, above it they fall by up to
1/16 of the ceiling per year. The player screen's bars (divisor 256, `1771:3947`, F008) move the
same way. `check_ageing.py` reports both the record bytes and, with the tables of the same
savestate, the derived-skill values before and after.

## 6. What the runs corroborate (E014)

- the year-end timing: after entry to a stage in {2,3,5,7} the players' +1/+4/+0x11 are as
  predicted from the previous year-end's records (sections 2, 3);
- the retirement predicate on computer countries: every player it flags is replaced (name
  initial / age / caps discontinuity) and no unflagged player is (section 4) — including the
  one same-name replacement of r0006 (player 57 'R Douwen', country 3: retired at year-end age
  33 > peak 28 + 5, and the re-create drew the same surname and initial; recognised by the
  creation bytes +2/+3/+5 changing, `check_ageing.py`);
- +2, +3, +5, +7 unchanged across the year for continuing players (section 2). **+6 (position)
  is not year-invariant**: 7 of r0006's 263 continuing players moved (05 → 08 and back, 01 → 04)
  — the per-match bookkeeping of the national team's repositioning, not the yearly loop: the
  program's writers of player +6 are 0791:AD8F's substitution path (`position = <pitch slot>`
  then `position = club_position` on the way out, seg_0791_08.c:910/921-922), the 'C' key of
  the player screen (1771:4952, seg_1771_03.c:1062), and unmanage_country's bench copy
  (000E:0290, squad slots 12..20) — none is in the yearly loop's callee set (section 2's
  calls.tsv claim stands: the LOOP writes only +1/+4/+0x11);
- the tables `DS:6D25`/`DS:6DCD` are not mutated by the yearly path (F008's hazard): the
  year-end records carry both years' copies and `check_ageing.py` compares them.

## 7. The auto-play path: the pre-match team screen's silent refusal, and the assistant

Static, read while fixing the r0002-r0004 stall (the runner sent 15-1193 Enters on one
`location:` screen with no advance):

- `0791:ED8A` (`in_match_menu`, the pre-match team screen; seg_0791_11.c:405-538): the option
  cursor is `local_9` (1..10); ` play ` is the fall-through Enter branch (`local_3 = 1`,
  seg_0791_11.c:529-531), and the menu loop's exit is
  `while ((local_3 == 0) || (EA09() == 0))` (seg_0791_11.c:533) — Enter on ` play ` leaves the
  menu ONLY when `0791:EA09` returns 1; otherwise the screen is redrawn and the key waits again,
  with no message: a silent refusal.
- `0791:EA09` (seg_0791_11.c:258-402): for every managed side (`is_managed` of `DS:9B34[side]`),
  walks the first eleven squad words `squad[0..10]`; a player `player_unavailable` while
  `DS:0C1F == 0` sets the side invalid outright (seg_0791_11.c:299-303); position counts are
  taken only over available players (`local_12[position]`, seg_0791_11.c:296-298), and the
  keeper/count warnings ("X has an ineligible player in the first team", `0791:E9A2`;
  "X has too many/no ... ", `0791:E9CE`/`E9E0`) are shown by `u214b_message_if_flag`
  (214B:1765: copies the message, shows it with the press-any-key box 04F8 when the flag is
  set, returns the flag) — each shown warning also marks the side invalid. EA09 returns 1 only
  when both sides stayed valid. So one injured/suspended player among the eleven makes ` play `
  a silent infinite loop — which is what r0002-r0004 hit after two quick friendlies.
- The recovery, from the same screen: Space opens the players screen directly
  (seg_0791_11.c:498-500: `DS:A976 == ' '` → `0791:E949`, which for a managed side runs
  `select_team_screen` `0791:E44F`); there the Ins key (`cVar3 == -0x4a`,
  seg_0791_09.c/select_team_screen key chain) with the squad list side up and `DS:0C1F == 0`
  calls `0791:DC7E`: the assistant's recommended 20 — two passes over the 20 squad slots, and
  for each slot the whole pool is scanned for a same-position player whose `player_strength`
  (1771:...) exceeds the incumbent's; the stronger pool player is swapped in
  (u214b_swap_bytes, seg_0791_10.c:742-790). GOAL.HLP P58 documents the key ("Hit Ins for
  assistant's recommended 20", sources/goal-hlp.md:324-325 and the screen string 2581:58FD).
  Esc exits the screen (the `local_7 == 1` Esc branch, seg_0791_09.c:83-89), and ` play ` then
  passes EA09. r0005 confirms: after the Space/Ins/Esc recovery at fixture 114 the season ran
  on to the stage-2→3 year end at fixture 769.

## 8. Match speed on the E014 path (owner direction, GOAL.HLP P102/P106)

The E014 runner never watches a match at variable speed: the managed side's matches go through
the captain screen's quick arm (Enter+r, F004's d3b: `r` at the first running-clock poll
`0791:92FC`, the immediate result F005 calls the quick engine — match.py `START_KEYS["quick"]`),
and every other fixture is refused at `0791:E80D` (n → the fixture byte 0xFE, simulated by
`000E:6970`). So the R quick-result path is the only match path the corroborating years run
through, for every match of every year. The ageing loop is not on the match path at all: it
runs in the year-end settling after the stage byte `[A923]+0x3C` enters a stage in {2,3,5,7}
(notes §1), which the quick path still traverses — r0005's capture 1 (stage 2→3, fixture 769,
fix_cnt 769→1345) is on that path, and its records are the corroboration input. The Left/Right
match-speed keys ([DS:A923]+0x3F, seg_0791_15.asm:785-791) are therefore never needed.
