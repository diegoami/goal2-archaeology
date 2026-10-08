# E016 (T30, Q014): retirement, the making of players, and results -> talent — the static map

Static first (rule 22). Every claim is read from `static/goal-exe/code/` (cited `file:line` and the
instruction address), with `calls.tsv` for callee sets and the initialised data image
`data/ds_2581_01.hex` for every table value; the named view was read first and corrected where it
was wrong (section 9). The committed records then corroborate: E014's six year-end records (the
38 re-creates, F016) and E006's twelve new games (F007). No run was taken (section 8 says why
none was needed). Files are under `static/goal-exe/code/`; `ds:N` is `data/ds_2581_01.hex:N`.

## 1. When old players leave: computer countries at the ageing gate

- `000E:70B9` (play next game; seg_000E_09.asm:476) routes a fixture (`6CA7`, :484); when the
  stage's fixtures are done it calls `1771:8208` (:492), then `000E:7072`, then the stage routine
  `1771:76B1` (:498). So a transition's ageing always runs before that transition's stage routine.
- `1771:8208` (seg_1771_12.asm:123) steps the stage byte `[A923]+0x3C` in [2,8] (`8251`, :154) and
  calls `1771:80DA` when the new stage is in the set at CS:81E8 = 0xAC = **{2, 3, 5, 7}** (`8263`,
  :161; `826A`, :163); only afterwards it sets `+0x40 = (stage >= 5)` (`8280`, :174).
- `1771:80DA` (seg_1771_12.asm:8) calls `1771:7FDF` for countries 1..128 in that order (`80F7`,
  :20); then, for the set CS:80BA = 0x24 = {2, 5}, increments the year word `[A923]+0x38`
  (`811B`, :34) and moves the countries' +0x3B..+0x40 history.
- `1771:7FDF(country)` (seg_1771_11.asm:1022): first pass, every squad slot 1..20 through
  `7FB1` (`8012`, :1043: age +1 at `7E6F` :861, `32EB`, +0x11 = 0 at `7FD4` :1015); then
  `1771:0B77` (`801F`, :1048). A **managed** country (0B77 true) ages its manager's 80 pool
  players too (`8024`-`8079`, :1050-1080) and runs **no retirement test**. A **computer** country
  runs `1771:7F40` on each squad slot (`8096`, :1098) and, on 1, `1771:7E80` (`80AB`, :1106).
- `1771:7F40(player)` (seg_1771_11.asm:951-998), deterministic, no callee: retires when
  `(DS:110E[gk] < +1 AND word +8 == 0) OR +1 > +2 + 5`, gk = (+7 == 0) (`7F5D`); `DS:110E = 1E 21`
  (ds:143: 30 outfield, 33 keeper); both comparisons strict (`7F78 jae`, :974; `7F9D jg`, :988).
  On the record the first pass aged (F016).

## 2. What happens to a managed country's old players

There is a retirement path for them, outside the year end:

- `000E:7439` (the main-menu loop): on Enter with item 6, for the current manager m
  (`[A923]+1`) whose `[A923]+0x47+m` is 0, it calls `000E:57E5(country of m)` (`7785`,
  seg_000E_09.asm:1210); a 1 returns to the menu (`7788`), a 0 goes on to `000E:5CF4` and, for the
  last manager, to `000E:70B9` (play next game, `77BF`, :1233).
- `000E:57E5(country)` (seg_000E_07.asm:383): returns 0 when the year word `+0x38` is 0
  (`580C`, :397) or the manager's flag `[A923]+0x4D+m` is set (`5824`, :405). Otherwise, when
  `[A923]+0x13+m` is 0 and `0791:DB38(country)` returns 0 (`5851`/`585B`, :421-424), it tests the
  squad slots 1..20 with `1771:7F40` (`587C`, :437) and replaces the **first** retiree at once:
  `000E:56F3(retiree, 1)` (`5897`, :448), return 1. Else it draws `rand(0x50)` (`58AB`, :457) and
  walks the 80 pool words cyclically from `DS:6D18[m] - 1 + rand` (`58BA`, :463) with `7F40`
  (`58DC`, :477); the first retiree is replaced by `56F3(retiree, caps > 0)` (`590C`-`591B`,
  :494-503), return 1; none: return 0 (`5948`, :521). The predicate's 1 leads straight to the
  replacement: the path has no question or acceptance step.
- `000E:56F3(retiree, announced)` (seg_000E_07.asm:289): sets the manager's flag `+0x4D+m = 1`
  (`570D`, :298); announced: the retirement news `000E:50D4` (`571E`, :303); `1771:1B2E` twice
  (:310, :316); a fresh record from `1771:4CF7` (`5745`, :317; seg_1771_07.asm:511-559): start =
  0xA00 + rand(0x1F3) (`4CFD`-`4D09`), then from start + 1 the first record with country byte
  0, wrapping 0xBF4 -> 0xA01 (`4D13`-`4D40`), and stopping if it comes back round to start; only
  then (the extra range 0xA01..0xBF4 full, `4D42`-`4D48`) a second search from rand(0xBF3)
  (`4D4A`-`4D53`) scans cyclically through **1..0xBF4**, wrapping 0xBF4 -> 1, to the first free
  record (`4D56`-`4D7B`, with no stop: it relies on one existing). Review round 2 R2; its number into the retiree's
  pool slot or squad slot (`5771`, :330 / `579C`, :346); `000E:54F0` (`57A6`, :350); the retiree's
  20 bytes zeroed (`214B:0018`, `57C0`, :362); announced: `000E:544D` and `000E:05F6` (:368).
- The flags `[A923]+0x4E..+0x53` (the six managers' +0x4D) are cleared by `000E:6CA7` at every
  fixture (`6CC8`-`6CD5`, seg_000E_09.asm:67-74). So a managed country loses **at most one old
  player per manager between two fixtures**, the squad before the pool, from the first game
  after year 0 on; computer countries lose every retiree at each ageing gate.

## 3. `1771:96D3` make_player(flag, club_position, country, player): every byte

Arguments by the callers' push order (first pushed = highest `[bp + n]`): `[bp+0xC]` player,
`[bp+0xA]` country, `[bp+8]` club position, `[bp+6]` flag (7E80 pushes player, +0, +7, 1 at
`7EA6`-`7EBE`, seg_1771_11.asm:886-897). seg_1771_13.asm:1107-1201:

| byte | write | draw (214B:06B1 arguments, in order) |
| --- | --- | --- |
| +0 | country (`96F3`, :1119) | - |
| +7 | club position (`96FC`, :1122) | - |
| +6 | = +7 (`970A`, :1126) | - |
| +5 | rand(0x10), 1..16 (`9711`-`971A`, :1128-1131) | 1: rand(16) |
| +1 | DS:118A[gk] - b + a, a then b = rand(7) (`9722`-`9754`, :1134-1156); DS:118A = 1C 1F (ds:147): 22..34 / 25..37 | 2, 3: rand(7), rand(7) |
| +2 | `1771:3291` (`975B`, :1158): DS:0E80[gk] + b - a, a then b = rand(3) (seg_1771_05.asm:255-277); DS:0E80 = 1B 1E (ds:123) | 4, 5: rand(3), rand(3) |
| +3 | flag != 0: country_rating(country) + 0x7F (`9768`-`9771`, :1163-1166); flag 0: country_rating + 0x7F - 10 - rand(10) (`977B`-`9794`, :1171-1181) | flag 0 only: rand(10) |
| +4 | `1771:32EB` of +1/+2/+3 (`979C`, :1185) | - |
| +0xC | rand(0x20), 1..32 (`97A3`-`97AB`, :1188-1190) | rand(32) |
| +0xF | `1771:3431` (`97B3`, :1193), bits only (below) | - |
| +0xD, +0xE | `1771:3558` (`97BA`, :1196) (below) | computer: rand(2T); managed: rand(T+1), rand(3T) |
| +0x12/+0x13 | 0x7FFF (`97C0`, :1198) | - |

Not written: +8..+0xB, +0x10, +0x11, and +0xF's other bits. No name byte (the initial and the
surname live in `[DS:9B70]` and `[DS:9B6C]`).

- `1771:3431` (seg_1771_05.asm:407-481): hardness `1771:2FFB` = +5 - (+3 and 1) (seg_1771_04.asm:
  1113-1126); below 4 (`3452`, :420) `1771:33CD` includes element 8 (bit 7) and excludes element
  4 (bit 3) (:390, :397). Then +6 in the set CS:3411 = 1B = {0, 1, 3, 4} (`346A`, :432; the set
  bytes at :402) includes elements 5 and 1 (`347E`, `3490`); +6 = 2 (`349A`, :451) includes element
  5 when +5 < 14 (`34A4`-`34B8`, :454-462), then elements 6 and 2 (`34CA`, `34DC`). `214B:0C79`
  ORs a bit (seg_214B_02.asm:441-460): 3431 never clears the byte first. In make_player +6 = +7.
- `1771:3558` (seg_1771_05.asm:532-633): T = DS:0E82[+1 > +2 + 4] (`3583`-`3589`, `35AD`, :548-569;
  DS:0E82 = 10 0D, ds:123), read with make_player's +1 and +2. `1771:0B77(+0)` (`35A0`, :563):
  managed: a = rand(T + 1), b = rand(3T), value T + b - a (`35B5`-`35E8`, :573-594); computer:
  value T + rand(2T) (`35FD`-`3615`, :604-613). Capped at 0x20 (`361C`/`3626`, signed `jle`),
  copied to +0xE (`3635`, :624), then +0xD floored at 1 (`363C`/`3646`, signed `jge`). In the
  computer branch the value is at least T + 1 = 14, so +0xE = +0xD, 14..32; in the managed branch
  0 is possible (energy 0, fitness 1; tests.test_model_recreate visits it).
- `1771:10E7` (seg_1771_02.asm:699-738): ((5 - +0x2C) * (0x21 - +0x2A) + (0x81 - +0x2B)) idiv 2,
  reads at `1104`, `1116`, `112A`, signed (`cwd` :731, `idiv cx` :733). Each difference grows as
  its rank gets better (smaller), so a better rank gives a larger rating. Domain: continent 1..4
  (63A4 sorts four continent groups, `6408`-`6431`), continent rank 1..32 (`6514`-`6524`), world
  rank 1..128 (`6530`): rating 1..128, +3 = 0x80..0xFF.

`recreate.make_player` is this table; it reproduces every byte of the 2560 squad players and the
80 pool players of the E006 new game (tests.test_model_recreate.NewGameTests).

## 4. The callers of make_player, caller by caller (calls.tsv: 7E80, 54F0, 97CC, 9873)

| caller | when | flag | club position | branch of 3558 | after make_player |
| --- | --- | --- | --- | --- | --- |
| `1771:97CC` | new game: `1771:9B85` -> `9A40` -> `97CC` per country (seg_1771_14.asm:393, :374); also `1771:26B9`'s rank-swap branch (below) | 1 | DS:9F02[20 country + slot] (`9859`, :59) | computer (no country is managed yet) | nothing |
| `1771:9873` <- `1771:98C4` | new game: `1771:2D15` -> `98C4` (seg_1771_04.asm:878), the managed country chosen | 0 | 0..13 four times; each squad slot's +7; slots 6..9 again | managed | squad-slot copies: +1 = DS:118C[gk] + rand(3) (`99C0`-`99E5`, :203-219; DS:118C = 11 14, ds:147), `32EB` (`99F8`) |
| `1771:7E80` | ageing gate, computer country (section 1) | 1 | the retiree's +7 (`7EB5`) | computer | +1 = DS:110C[gk] + b - a, a then b = rand(6) (`7EC7`/`7ED1`, `7EEB`-`7EF9`, :901-923; DS:110C = 19 1C, ds:143); `32EB` (`7F01`, :926); +8/+9 = 0 (`7F09`), +0xA/+0xB = 0 (`7F12`), +0x10 = 0 (`7F19`); the initial `[DS:9B70]+player` = `1771:0000` (`7F1F`-`7F2D`, :936-941); +6 = the retiree's +6 saved at `7E9D` (:883), restored at `7F36` (:944) |
| `000E:54F0` | between fixtures, managed country (section 2) | 1 | the retiree's +7 (`552A`, :105), into the fresh record | managed | +1 = **DS:0x78**[gk] + b - a, a then b = rand(6) (`553D`/`5547`, `5561`-`556F`, :113-135; DS:0078 = 19 1C, ds:10); `32EB`; caps/goals/status zeroed (`5584`, `558D`, `5594`); the initial (`5599`-`55AD`); then the young count: squad slots 1..20 and the 80 pool words with +1 < **DS:0x76**[gk] + 4 (`55B5`-`56AA`, :156-254; DS:0076 = 11 14, ds:10; the fresh record is already in its slot); fewer than 0x14 (`56AC`, :256): +1 = DS:0x76[gk] + rand(3) (`56B8`-`56DD`, :262-278), `32EB` (`56E8`) |

- `1771:0000` (seg_1771_01.asm:9-22): `r = rand(byte DS:0C38)` (`0006`-`000C`), returns
  `DS:0C38[r]` (`0013`): DS:0C38 = 0x15 then "ABCDEFGHIJKLMNOPRSTVW" (ds:104-105) — one of 21
  letters, never Q, U, X, Y, Z. One draw.
- `97CC(country)` (seg_1771_14.asm:8-70): the RNG word := country (`97ED`, :20); +0x29 := +0x2B and
  +0x28 := +0x2A (`97FA`, `9808`); `[A91F]+3(+0x2E)+1 := country_rating` (`9810`-`9829`); then the
  20 make_player calls (`9864`, :65).
- `98C4` (seg_1771_14.asm:107-256) starts one draw after 97CC(128) ends in E006 (`1771:2D15` calls
  `1771:09A0`, which draws an initial for an empty manager name, seg_1771_01.asm:1087), and its
  80 records then match E006 exactly.
- `1771:26B9` (seg_1771_04.asm:591-683): a branch swaps two countries' +0x2B (world view,
  `2B99`) or +0x2A (`2BE2`) and their places in the order (`2C01`), then re-makes both squads with
  `97CC` (`2C16`, `2C29`): seeded by the country number again, with the swapped ranks.

`recreate.recreate`, `managed_replacement`, `new_game_squad`, `managed_pool` are these rows.

## 5. The RNG at a year end, and whether a savestate recovers it

- The state is the 16-bit word the far pointer DS:A978 points to. `214B:06B1(n)`
  (seg_214B_01.asm:897-911) loads that pointer (`06B7`, :901) and calls `214B:0688` (:906), which
  stores `w * 0x7ABD + 0x1B0F` mod 2^16 (`0694`-`069F`, :880-886) and returns `hi16(w * n) + 1`
  (`06A0`-`06A4`, :887-889). The pointer's only writer is `214B:206A`: DS:A978 := DS:7B62
  (seg_214B_04.asm:435-436, F004). Writers of the word: `1771:97CC` (:20, := country), `23E4:11D7`
  (seg_23E4_02.asm:807, DS:7B62 := CX = hour·256 + minute; :808 also writes DS:7B64 := DX),
  `0791:2648` (seg_0791_04.asm:732, := (year + 1) * state +0x26) and the save/restore at
  `0791:17F7`/`0791:0F1D` (seg_0791_03.asm:250-251, seg_0791_02.asm:626-627), both match-time.
- `1771:6730` (seg_1771_09.asm:1094) calls `23E4:11D7` only when the year word `+0x38` is 0
  (`675B`, :1111, then `67A3`, :1138); otherwise it calls `1771:63A4` (`6762`, :1113). 80DA
  increments +0x38 at every {2, 5} gate (`811B`) before that transition's 6730, and 9B85 sets it
  to 0 at a new game: the DOS time seeds the word once, at the new game's first 6730, and never
  again in that game. (A loaded game was not traced.)
- Draws at an ageing gate: the first pass and 7F40 draw nothing (calls.tsv; 7E4A, 7FB1, 32EB,
  7F40 have no RNG callee). Each computer-country re-create draws **ten** times, in this order:
  rand(16) +5; rand(7), rand(7) make_player's +1; rand(3), rand(3) +2; rand(32) +0xC; rand(2T) +0xD;
  rand(6), rand(6) +1; rand(21) the initial (no rand(10): flag 1). Countries 1..128, slots 1..20.
  A managed replacement draws rand(0x1F3) in 4CF7, and rand(0xBF3) only when the extra range
  holds no free record (`4D4A`); rand(0x50) when the squad has no retiree; then 54F0 draws
  **11** — make_player's **8** (six with flag 1, which skips rand(10), then two for the managed
  fitness), rand(6) x 2, rand(21) — or **12** with rand(3) when the young count is short (review
  round 2 R3; a traced call from word 0: [16, 7, 7, 3, 3, 32, 17, 48, 6, 6, 21], final word
  0x72b1).
- Recoverable? The word is in every savestate (guest memory). A savestate taken at 80DA's entry
  gives it directly, and from there the gate's draws are the sequence above. A savestate taken
  earlier needs the draws in between (the last fixture's match, 6CA7); one taken after (the
  E014 capture's) has the stage routine's draws after it too (6730 shuffles fixtures with 128
  draws at `6808`-`6846`, :1179-1207); neither count was traced. The E014 records carry no RNG
  word, but the 16-bit word at 80DA's entry is **recovered from the records themselves**: the
  captured countries are 1, 2, 3, the first of 80DA's order, so their re-creates make the gate's
  first draws, and exactly one of the 65536 words reproduces every drawn byte of every re-create
  of the pair, for each of the five pairs (0xbb1a, 0xfdf6, 0x8827, 0x36ca, 0x1a42;
  `check_recreate.py`).

## 6. Readers and writers

Player bytes the creation writes, with their writers in the creation paths: +0, +7 (`96F3`,
`96FC`); +6 (`970A`; `7F36` in 7E80); +5 (`971A`); +1 (`9754`; `7EF9` 7E80; `556F`, `56DD` 54F0;
`99E5` 98C4); +2 (`32E1`); +3 (`9771`, `9794`); +4 (`32EB`, after each age write: `979C`, `7F01`,
`557A`, `56E8`, `99F8`); +0xC (`97AB`); +0xD/+0xE (`3615`/`35E8`, `3626`, `3635`, `3646`); +0xF
(`214B:0C79`/`0CA1` from `3431`/`33CD`); +8..+0xB, +0x10 (`7F09`, `7F12`, `7F19`; `5584`,
`558D`, `5594`); +0x12 (`97C0`); the initial `[DS:9B70]+n` (`7F2D`, `55AD`). +0x11: no writer in
these paths; `7FD4` cleared it in the gate's first pass.

Country bytes the creation reads: +0x2A/+0x2B/+0x2C (`10E7`), +0x2E (`0B77`). Writers of
+0x2A/+0x2B: `9A40` at a new game (`9A75`, `9AB4`, seg_1771_14.asm:281/306, from GOAL.DAT),
`63A4` (`6524`, `6530`), and `26B9`'s swap through `214B:007B` (`2B99`, `2BE2`); of +0x2C: `9AC7`
only. Nothing in 80DA writes them, so every re-create of one country at one gate reads one
rating.

Between a gate's re-creates and E014's capture: the capture is the first settled screen after
the stage byte changed (experiments/E014-q013-ageing/run.py `maybe_capture`), so no fixture is
played in between. The call closure of `1771:76B1`, `000E:7072` and `000E:60CB` (calls.tsv, 131
routines) holds no direct writer of a player's +6, +0xC, +0xD, +0xE or +0xF (the writers:
3431, 33CD, 3558, 3651, 34E7, 96D3, 0791:474D/4B64/69BD/7CC5/7D56/83A2/8AE9/9A32/A260/A375/B364/
B3B7/BC5D/C5DC/CB7D/D733, 1771:1B2E, 2D15); it does reach the generic `214B:0018`/`003C`/`007B`
(fill, move, swap), whose call sites there were not traced byte by byte. The checker reads
morale, fitness, energy and the tactics bits at the capture on that basis.

## 7. Results -> talent

The only input of a re-created player's bytes that results move is the country's rating, through
its ranks; the chain, as far as it is traced:

1. **Points.** The country's +0x2F word accumulates: `1771:61F8` (seg_1771_09.asm:538-639) adds
   (5 - k) x (the group entry's points byte +7) for groups k = 1..4 of the tables at `[A933]`
   (`627A`-`6295`, :595-605; a second loop `62E9`-`637E`); `602D` (world, :333) and `6103` (each of
   the four continents, :429) add placement bonuses through `1771:5FD1` (:296; +0x2F += bonus at
   `600B`, :316): 800, 600, 400, 200 (`605C`, `608C`, `60BC`, `60EC`; `6151`, `617E`, `61AB`, `61D8`)
   to the sides `5C94` and `5CCB` pick from two fixtures (the side the fixture's +3 byte names and
   the other, seg_1771_08.asm:1082/1109); `1771:5E3A` adds 200 to both countries of a fixture it
   schedules with an argument other than 1 (`5E79`, `5E8D`, :150/156; called by the stage routines
   6B55, 6E59, 71B2, 74BE). +0x2F is reset to 5 - continent at each recompute (`6605`, :964) and
   by 6730's year-0 path (`6798`, :1135).
2. **Order.** `1771:5EE1` (:197-292) quicksorts a range of the order array `[DS:9B56]` by +0x2F,
   largest first (`5F3D jbe`, `5F64 jae`); 63A4 points DS:9B56 at DS:9BFD (world) or DS:9C7E
   (continents) (`63D6`-`63EC`) and sorts 1..128 (`6403`) or each continent's 32 from
   DS:10F9[c] (`642A`, c = 1..4).
3. **Ranks.** `1771:63A4` (:726-967), from 6730 at stages 2 and 5 when +0x38 > 0: with +0x40 = 0
   (stage 2) `602D`, `61F8`, the world sort, then +0x2B := place 1..128 (`6530`, :888); with +0x40
   = 1 (stage 5) `6103`, `61F8`, the continent sorts, then +0x2A := (place - 1) mod 32 + 1
   (`6524`, :883). Per country it also keeps the best ranks +0x29/+0x28 (`6537`-`656E`) and, for a
   managed one, the manager's records (`6476`-`6506`).
4. **Rating and +3.** `10E7` turns the ranks into the rating (section 3); make_player writes +3 =
   rating + 0x7F for every caller with flag 1 (7E80, 54F0, 97CC). A rank one better raises the
   rating by about (5 - continent)/2 (continent rank) or 1/2 (world rank) and +3 with it; +4
   follows +3 through `32EB`.

The other byte 63A4 writes from the rating, `[A91F]+3(+0x2E)+1 := clamp(country_rating +
signed [A91F]+3(+0x2E)+2, 1, 128)`, then `+2 := 0` (`6582`-`65ED`, :918-956), is the manager
byte `1771:0AA7` adds to match strength (F012); its accumulator +2 is moved by `0791:B6CC`
(seg_0791_18.asm:982-1012, a signed sum clamped to -127..127; callers 000E:6CA7 and 0791:B7FA).
make_player and its callees never read [A91F] (section 3), so this byte does not reach a new
player.

**Which recompute each replacement reads** (the gate's re-creates run before the gate's 6730):

| gate | +0x2B (world rank) | +0x2A (continent rank) |
| --- | --- | --- |
| entry to 2 | the previous cycle's stage-2 recompute | the previous cycle's stage-5 recompute |
| entry to 3 | this cycle's stage-2 recompute (6730 ran after the stage-2 gate) | the previous cycle's stage-5 recompute |
| entry to 5 | this cycle's stage-2 recompute | the previous cycle's stage-5 recompute (this one runs after the gate) |
| entry to 7 | this cycle's stage-2 recompute | this cycle's stage-5 recompute |

Before the first recompute of each kind the ranks are GOAL.DAT's (9A40). Stage 8 is no gate. A
managed replacement (54F0, between fixtures) reads the latest of each. Each recompute reads the
+0x2F points gathered since the previous recompute (both kinds reset +0x2F, step 1).

**Answer: yes, results feed new talent**: points, placements and knockout fixtures
(+0x2F) -> the sort -> the ranks -> country_rating -> +3 (and +4) of every re-created and every
managed replacement. What the trace does not show is the help file's "better than expected
(from your country's skill ratings)": no step of the chain reads a skill rating or an expected
value; a country's ranks come from its points against every other country's (the world) or its
continent's (the continent rank), so whether a weak country's points count for more (Q04.7) is
not established by this chain.

## 8. What the records corroborate, and why no run was taken

- E014 (F016's six records, five pairs, three computer countries): `check_recreate.py` compares
  every squad word (300); 262 continue, 38 are re-created, and every re-create meets the
  contract a capture can show; for every pair exactly one RNG word at 80DA's entry reproduces all
  its re-creates' drawn bytes and initials (38 of 38): the draw order, the arguments, the T index
  and the initial table of section 5.
- E006 (F007's twelve new games): make_player reproduces all 2560 squad players and the 80 pool
  players (tests.test_model_recreate).
- Not corroborated by a record: the managed path (54F0/56F3/57E5; no committed record shows a
  managed retirement) and the exact +3 of a re-create (the E014 captures hold no country record;
  checked only as one byte per country and in 0x80..0xFF). Both are static only. A run could
  show them (a managed country's sitting past year 0; a capture with the country records), but
  the task's question is answered without it, so the run budget (4) was not used.

## 9. Corrections to earlier text

- The 6730 annotation said the DOS time seeds DS:7B62 on every entry to stages 2/5, and round 1
  that its year-0 call reads the time without seeding: 23E4:11D7 writes DS:7B62 and DS:7B64, and
  6730 calls it only in year 0 (section 5). E014's notes (section 3, "re-seeds DS:7B62 from the
  DOS time on entry to stages 2/5") carry the first form; that file is not this task's (reported).
- `1771:0000` is a bounded draw indexing DS:0C38 (section 4), not "one byte of the LCG".
- Round 1's chain named 602D/6103 as sorts, 61F8 as a stabiliser, the manager byte as
  min(prior, rating), the managed age base as DS:0x76, and the managed path as out of scope with
  a user acceptance; sections 2, 4 and 7 replace those.
