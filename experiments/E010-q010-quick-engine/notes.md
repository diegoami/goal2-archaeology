# E010 q010-quick-engine — reading notes (routine by routine)

Live notes while reading the quick-result engine `0791:D733` and everything it reaches. Each entry:
what the routine reads / draws / writes, with listing addresses. All addresses are
`segment:offset`; `seg_0791_NN.asm` is `static/goal-exe/code/`. Data tables are DS offsets
(read from `static/goal-exe/data/ds_2581_*.hex`). Status: this file is append-only; commit per batch.

## RNG (the one thing the model must reproduce exactly)

`214B:0688` (LCG) — decompiled `seg_214B_01.c:552-562`:

```
uVar1 = *seed * 0x7abd + 0x1b0f   (16-bit)
*seed = uVar1
return ((uVar1 * n) >> 16) + 1      # 1..n
```

- `214B:06B1` rand 1..n = `0688(n, DS:A978)`; `DS:A978` is a far pointer to the seed word (DS:7B62).
- `214B:06D0` = `0688(n) == 1` (chance 1/n).
- `214B:06FA` = `0688(2) == 1` (coin flip).
- The **second stream** `DS:8336` is stepped only by `0791:94C9` (via `214B:0688` on DS:8336), whose only
  caller is `0791:94E8` (speaker noise). `94E8` is reached only from `0791:7881` (walk off) and
  `0791:9564` (watched engine) — neither runs in a quick result. **Conclusion: DS:8336 is unchanged
  during a quick result.** (calls.tsv: `0791:94E8` callers.)

## The line sums `1771:0BC4(flag, side, country)` — seg_1771_02.asm:124-378

Far call; arguments (top of stack first) flag, side, country. Layout of the four word sums
(established, matches B19D's reads): `DS:9B45 + 2*side + 4*k`, k = 0 keeper, 1 defence, 2 midfield,
3 attack. So side 0 keeper=9B45, defence=9B49, midfield=9B4D, attack=9B51; side 1 is +2 each.

Steps:
1. `0AA7(country)` (seg_1771_02.asm:7-35) → M = manager bonus. `0AA7`: country+0x2E (managed byte) * 3,
   byte 1 of `[DS:A91F]` manager table, signed `idiv 8`, `+ 0x10`. So
   `M = (manager[3*(country+0x2E)+1] idiv 8) + 16`.
2. Clear the four sums (0BED-0C0B).
3. For slot 1..11 (`country + 2*(slot-1)`):
   - squad word == 0 → skip (0C21/0C26).
   - player = `[DS:A91B] + squad*0x14`. v = `377E(squad)`; if v != 0, v += M (0C59-0C68).
   - if position +6 != 0 (0C6E; keeper skips): for e = 1..6, if e in {1,5,6} (set 0x62 at CS:0BA4,
     `23E4:08DF` member when `jne` taken; element k at bit k, so 0x62 = bits 1,5,6):
     - effective e = player +0xF bit e when e < 5 and +0xF bit (e+4) set, else country(player byte 0)
       +0x2D bit e (0C95-0CEE; `214B:0C57` tests bit e-1 of the byte, so "bit e" of the Pascal set).
     - set → add M/8 (unsigned `div 8`) to attack 9B51+2*side (0D0B); clear → add M/8 to defence
       9B49+2*side (0D25).
   - k = table `DS:0D4E[+6]` (position→line). If k < 4: sums[k] += v (0D32-0D68). Else: sums[k-3] += v/2
     and sums[k-2] += v/2 (unsigned div 2) (0D6E-0DCD).
4. If flag != 0: for each sum, sums[k] += sums[k] idiv 8 (signed) (0DDA-0E1C).

`DS:0D4E` (16 bytes, pos 0..15) = [0,1,1,4,4,2,2,2,2,5,5,5,3,3,0,1].
`0AA7` table `[DS:A91F]` = manager table (3 bytes/manager, byte 1 is the quality).

## `1771:377E` player_strength — seg_1771_05.asm:763-836

```
377E(player):
  if 3216(player): return 0
  v = (+4) + signed(+0xE) - 0x3E
  if +0xC >= 0x20 (signed): v -= v idiv 16
  else: v += signed(+0xC)
  clamp v to [0, 0x100]
  if 3179(player): v = v idiv 2
  return v
```

## `1771:3216` player_unavailable — seg_1771_05.asm:188-239

returns 1 (unavailable) when: +0xE < 1 (signed), OR +0x10 bit 7 (element 8), OR +0x10 bit 5
(element 6), OR +0x10 bit 2 (element 3). Else 0.

## `1771:3179` (halve strength on wrong foot) — seg_1771_05.asm:120-186

```
foot = 3088(player)            # foot_index
two = 3041(player)             # +5 + +2 == 30
if foot != 0 and not two and position in {3,7,10} (set CS:3139 = 88 04): return 1
if foot == 0 and position in {4,8,11} (set CS:3159 = 10 09): return 1
if position == 0: return 1 if +7 != 0 else 0
else: return 1 if +7 == 0 else 0
```

- `3041` is_two_footed = `(+5) + (+2) == 0x1E` (seg_1771_05.asm:7-37).
- `3088` foot_index = `DS:0xE60[14 * DS:0xE7C[player%3] + (+7)]` (seg_1771_05.asm:40-72).

## `1771:2FFB` hardness — seg_1771_04.asm:1100-1131 = `(+5) - ((+3) & 1)`.

## `1771:3A82` squad_slot_of_player(country, player) — seg_1771_05.asm:1082-1118

loop slot 1..20, return slot whose squad word == player, else 0.

## `1771:3A06(player, k)` skill — seg_1771_05.asm:1033-1080

`s = DS:6DCD[12*(+5) + DS:6D25[12*(+7) + k]]`; return `s * ((+4)+1) / 32` (unsigned).
(Need to dump tables DS:6D25 and DS:6DCD.)

## `1771:3431` set_player_tactics — seg_1771_05.asm:406-481 (F010, re-verified)

hardness = 2FFB; if hardness < 4 → 33CD (clear element 4, set element 8 of +0xF). Then position in
set CS:3411 = 0x1B (bits 0,1,3,4 → positions {0,1,3,4}): set element 5 and element 1, return. Else if
position == 2: set element 5 when +5 < 14, then always element 6 and element 2. Only sets bits.

## `0791:26D7(pitch_slot, ?, k)` effective tactic — seg_0791_04.asm:783-841

k < 5 and +0xF bit (k+4) set → +0xF bit k; else country(2974(pitch)+...)+0x2D bit k. `2974`
(seg_0791_04.asm:1066-1083) = pitch record +6 < 12 ? 1 : 0 (the side index).

## `0791:278A(pitch_slot, k)` — seg_0791_04.asm:846-942 (D5C1's compare)

player = `[DS:A91B] + pitch[+0xD]*0x14`.
v = (+0xC < 0x20 ? signed(+0xC) + 1 : 0); then v += (k >= 12 ? 0x20 : signed(+0xE)).
s = `1771:3A06(player, k)`; if pitch[+0x13] != 0: s /= 2.
v = (v * s) / 0x100 + s / 4 (unsigned). Return v.

## `0791:2956(pitch_slot)` — seg_0791_04.asm:1052-1064 = `3216(pitch[+0xD])`.

## `0791:B19D(attempts)` roll_quick_goals — seg_0791_18.asm:417-523

For side t = 0 then 1, `attempts` attempts (none if 0). Per attempt, up to 3 contests, each 2 draws,
opponent's draw first, a contest drawn only if the previous was won, signed comparisons (jle skips):
1. rand(9B4D[own]) vs rand(9B4D[opp]) — midfield; win when own > opp.
2. rand(9B51[own]) vs rand(2*9B49[opp]) — attack vs 2×defence.
3. rand(9B51[own]) vs rand(9B45[opp]) — attack vs keeper.
All three → `inc DS:9B3C[t]` (a goal). (Layout confirmed: keeper 9B45+2side, defence 9B49+2side,
midfield 9B4D+2side, attack 9B51+2side.)

## `0791:D733` quick_match_engine — seg_0791_21.asm:794-1209

One call per game minute (zeroes DS:831D). Order:
1. DS:8325=1; copy screen 0xFA0 bytes; DS:831D=0.
2. save DS:9B3C to local, clear DS:9B3C, clear a 0x20-byte local buffer.
3. `0BC4(DS:80FC, 1, DS:9B36)` then `0BC4(0, 0, DS:9B34)` (D77E-D798).
4. `B19D(DS:0A8A[DS:8319==0x0F])` = 12 or 16 attempts (D79D-D7B4).
5. Per side t: test element 5 (bit 4) of +0x2D, chance 1/`DS:0A90[bit]` (60 clear/30 set) via 06D0 →
   inc stat byte DS:7B7E+10t (D7C0-D809). Test element 1 (bit 0), chance 1/`DS:0A8E[bit]` (33/10) →
   inc DS:7B82+10t and DS:7B83+10*(other) (D809-D86A). (4 draws total; stats counters, not in score.)
6. For each side t where new goals `DS:9B3C[t]` grew (D873-DA4C): for each new goal, draw
   `rand(DS:0A8C[DS:8319==0x0F])` = rand(90) or rand(120) → a minute (stored in local, 16 per side)
   (D8B2-D90B). Then for each drawn minute (D911-DA43): if it == DS:831F and the side has < 0xF goals
   this call and no goal scored yet this call (DS:9A3E? no — local `[bp-0x2e]`): draw `rand(0x1e)`=30 →
   scorer slot = `DS:0xA6C[rand]` (values 2..11, weighted); loop while `3216(squad word)` (unavailable)
   (D973-D9B2); then `inc DS:9B3C[t]` (the local count, actually `[bp-2]` + side), set DS:830B =
   `DS:0668[side] + 3A82(country, squad word)`, call `6443(minute, slot, side)`, mark a goal scored
   (D9B4-DA30). **At most one goal scored per D733 call** (the "one goal per minute" rule).
7. Restore DS:9B3C = local (DAG…-DA58); `054C(3, DS:831B)` (draw clock); `0712` (draw score).
8. Energy: for each of 22 pitch slots, if `DS:831B % 5 == 0` and player +0xE > 1, dec +0xE
   (DA6F-DAC9). **This changes player strength for later minutes.**
9. If DS:9A3D != 0 and no goal: `D5C1()` (DACB-DAD9).
10. If goal: `0106(0)` + `65FE()`; else `8062()`. Then `9372()` (DADC-DAF1).

`DS:0A8A` = [12, 16]; `DS:0A8C` = [90, 120]; `DS:0A8E` = [33, 10]; `DS:0A90` = [60, 30] (all indexed by
`DS:8319==0x0F`). `DS:0A6C` (30 bytes, scorer slot, index 1..30) =
[2,3,4,5,5,6,6,7,7,8,8,8,9,9,9,9,9,9,10,10,10,10,10,10,11,11,11,11,11,11]. `DS:0668` = [11, 0]
(side base; side 0 base 0 → pitch slots 1..11, side 1 base 11 → slots 12..22).

## `0791:D5C1` roll_quick_foul — seg_0791_21.asm:621-792

1. r = rand(10)+1 (2..11); slot_1 = r (team "1"), slot_0 = `DS:0xA90[r]` (= 13-r; DS:0xA90[2..11] =
   [11,10,9,8,7,6,5,4,3,2]); then slot[side] += `DS:0668[side]` (0 for side 0, 11 for side 1).
   So slots: side 0 → 13-r+11 = 24-r (13..22), side 1 → r (2..11). (1 draw)
2. `2956` of each slot → if either unavailable, return (no more draws).
3. own = coin flip 06FA → own team t. (1 draw)
4. `278A(own, 3) < 278A(other, 10)` unsigned (jb), else return.
5. `26D7(own, 4)` effective element 4; if set, continue; else chance 1/20 (06D0(0x14)) else return. (1 draw)
6. a = rand(`2FFB(other)`), b = rand(`2FFB(own)`); if b <= a (jle) return. (2 draws)
7. store DS:830C=own slot, DS:830B=other slot; call `7EEF()`.

## `0791:7EEF` foul result — seg_0791_13.asm:738-839

- `261a()` twice: 261a (seg_0791_04.asm:695-714) reads a pre-shuffled slot order `DS:8337[DS:8437]`
  and increments DS:8437 (no RNG at call; the shuffle is made by `2648` once at match setup).
- If `261a() < 4`: if own player +0x10 bit 5 set → `7B77` (sending off) else `798D` (booking).
  Else: chance 1/32 (06D0(0x20)) → `7B77`. (1 draw only in the >=4 branch)
- Then `261a()` again: if == 1: compare 2FFB of the two players; harder one gets `7D56` (injury).

## Computer tactics (reached from `65FE` after a goal) — seg_0791_19.asm

`C173(flag)` (:997-1110): d = signed byte `DS:9B3C - DS:9B3D`. Per team (0,1) where `0B77(country)==0`
(unmanaged; a managed team is skipped): |d|<2 → `BD83(t)`; |d|==2 → `BF6B(flag, t)` (flag 0 = team
ahead = exclude, 1 = behind = include); |d|>2 → `C0DF(t)` (ahead) or `C01A(t)` (behind).
- `BD83(t)` (:585-708): `BBFF(R008[c], c)` (reset +0x2D to R008, re-derive +0xF); if t==1 and DS:80FC
  and `BD03(team1,team0)`: include element 1 + BBFF; if `BD03(t, opp)`: include rand(6) twice + BBFF
  (2 draws); clear DS:8332+t and DS:8334+t.
- `BF6B(flag,t)` (:784-843): BD83(t); then 3× (include if flag else exclude) rand(6) (3 draws); BBFF.
- `C01A(t)` (:849-930): only while DS:8332+t==0: 5× include rand(5) (5 draws) + element 6, BBFF, set
  DS:8332+t. Then BEC7/230C conditionally.
- `C0DF(t)` (:932-994): only while DS:8334+t==0: 5× exclude rand(5) (5 draws) + element 6, BBFF, set
  DS:8334+t.
- `BD03(a,b)` (:531-582): sum of 377E over first 11 squad words of a vs b, unsigned `ja`. No RNG.
- `BBFF(value, c)` (:427-463): +0x2D = value; `3431` per nonzero squad word. No RNG.

## Match clock & loop — seg_0791_16.asm

- Tick loop `97D0` (:93-141): if DS:9A3E set → `D733`; then `970C`. Loop until 970C returns 1 (or
  [bp+4] guard). Quick results never call 9564/8CF5/9119 (the else branch).
- Clock `970C` (:6-91): if DS:8325==0 return 0. If DS:831D>0 dec it, return 0. Else: DS:8326 =
  (DS:831B + DS:8321 == 0); if not end: if 831B>0 dec 831B else dec 8321, and if 831F<0x80 inc 831F;
  `054C(3, 831B)`; DS:831D=0x24; if 831B==DS:8319 (signed) → end-of-half (2B0F, whistle, return 1),
  else if 8326 → return 1, else return 0.
- Match setup `A4A1` (:246-447) + `A3DE` (:163-244):
  - A3DE: DS:9B34/9B36 = fixture countries; DS:7C36 = extra-time flag (fixture +2 in set CS:693A);
    `D44C` → DS:80FC; **`2648` (256 × rand(16) shuffle)**; DS:9B3C=0; per unmanaged team: B11F, 34E7,
    BD83.
  - A4A1: DS:832C=0xffff, `11073`, zero 9B08.., DS:8332/8334=0, DS:80EE=0, commentary ring fill 0xFF,
    stats DS:7B7E 0x14 bytes = 0, DS:7BD4 0x42 = 0, DS:80F2/80F6 = 0, DS:9A40 0x50 = 0; DS:9A3D =
    (fixture +2 != 1); **DS:831A = coin flip 06FA**; DS:830C/830E/830D/80FA/7C39 = 0; A3B6 (ball), A3B6
    (referee), A3B6 (DS:8304); per slot 1..22 `A2E6`; DS:0C1F=0, DS:8326=0, DS:9B41=1; per side
    DS:80F0[side]=0 and A3B6(DS:82E2+6*side); DS:9B3A[side] = `DS:066B[DS:9A3D]`; `230C`; `2FB1`;
    DS:9B40=0; DS:831D=831F=8321=0, DS:8325=0, DS:8324=8327=8328=0, DS:832A=0x64; DS:80FD =
    (either team managed); DS:0C1E=1; DS:9978 0x14 bytes = 0; DS:9A3E=9A3F=0; A841; DS:7C37=7C38=0.
- `998C` (first half, :294-337): DS:831B=0x5B (91), DS:8319=0x2D (45); kick-off (DS:830B = DS:0668[831A]
  + 10, 2996, 6b65, 1eb5); `983F`; DS:832C = DS:9B3C.
- `983F` (half, :143-197): DS:9B41=0, DS:830E=0, `8062`, `2a15`, (not quick: 2929, 8cca), DS:8302=0,
  DS:9B55=1, DS:0C20=0, DS:7C37=0, `97D0(0)`, (not quick: 9079 per side + referee), DS:8325=0, `1E8D`.
- `9A32` (second half, :344-436): per slot energy +2 if in set CS:99F2; DS:9B41=1; screen copy ×2;
  `0106(1)`; (ED8A unless key in set CS:9A12); kick-off; DS:832A=0x50; `983F`.
- `F098` (play_match, seg_0791_23.asm:919-1029): 998C, 9955, 9A32; store score/result; if DS:7C36 and
  drawn: 9B0C (extra time: 831B=0x1F=31, 831F=0x59=89, 8319=0x0F=15, 831D=0), 9B5B, then A10A
  (penalties) if still drawn; if not quick and scores differ: 98C4.

**First-half minute count**: 831B 91→45, 831F 0→46 (46 D733 calls, 831F=0..45). Second half: 831B
45→0, 831F 46→91 (46 D733 calls, 831F=46..91). Total 92 D733 calls; `831B = 91 - 831F` throughout.
Goal minutes 1..90: minutes 0 and 91 can never match a drawn 1..90.

## After-goal `65FE` — seg_0791_11.asm:317-484

DS:8325=1; `0441(4)` (whistle, no-op at speed 0); copy pitch records; `65A4` (reset states, no RNG);
`C173(flag)` (computer tactics, RNG as above); per slot: 2956, 2b51, 7cc5 (display, no RNG); compute
DS:832A; if DS:9A3E set DS:9B55=1. **The RNG here is C173 only** (65A4/2b51/7cc5/2956 read only).

## No-goal `8062` check_substitutions — seg_0791_13.asm:905-1078

Per team: managed (`0B77` nonzero): keeper 3216, then only acts if DS:9B40 != 0 (it is 0 during a quick
match: set 0 at A4A1 and never re-set) → no RNG, nothing. Unmanaged: if `[di-0x64c6]` (DS:9B3A[side])
> 0: scan slots 11..2; per slot with +0x10 bit 6 clear, +0xE > 0, 831B > 1, slot > 1, 831B < 0x23, and
+0x12 < 0x5A-831B: call `C88D` (substitution) — **C88D RNG to check**.

## `0791:6443` record_goal(minute, slot, side) — seg_0791_11.asm:123-272

commentary 0x26/0x27 (2aa3), scorer +0x0A++, 5A03 check, `b3b7`, `7cc5`, DS:80F0[side]++, store player
word + minute (+0x80 when 8324/7C39) into DS:7BD1 + side*0x21 + n*3. **RNG in 2aa3/5A03/b3b7/7cc5/2bb1
to check** (they look like display/commentary writers; 2bb1 = ball-side test, no RNG).

## TODO (next reading batch)

- Confirm RNG (or not) in: `D44C`, `B11F`, `11073`, `A2E6`, `230C`, `2FB1`, `C88D`, `6b65`, `1eb5`,
  `2aa3`, `2ad4`, `5A03`, `b3b7`, `7cc5`, `3c20`, `9372`, `7B77`, `7D56`, `798D`, `2a15`, `A841`.
- Dump tables: DS:6D25, DS:6DCD (skill), DS:0xE60, DS:0xE7C (foot), DS:8337 (shuffle, runtime).
- Confirm which of those the quick path actually reaches (fouls may never fire → 7B77/798D/7D56 unused).
- The pitch record at DS:80E8 + slot*0x16: which bytes matter (0xD player index, 6 side, 0x12 state,
  0xE energy is in the PLAYER record, 0x11, 0x13).

## Batch 2 (2026-10-05, third run): the half-time boundary, verified

- `9955` half time, quick mode (seg_0791_16.asm:267-292): only DS:8325=0, DS:8302=0, 214B:1E8D; no
  key wait, no RNG. The half-time wait is `ED8A(0)` inside `9A32` (seg_0791_16.asm:417, gated by
  DS:80FD!=0 = a team managed, else by key [A977] in set CS:9A12).
- `ED8A` menu loop (seg_0791_23.asm:562-...): callees A75D/EA09/E949/E929/1230C/1771:0F58/1981; the
  only rand caller reachable is 1771:3EF8 (via 1981, the tactics submenu, Enter on options 1/6);
  the wait loop itself (A75D key read + redraw) draws nothing. 214B:1E8D is a display flip.
- `9A32` before the wait: energy +2 per pitch slot whose player +0xE is in set CS:99F2 (elements
  1..30, i.e. every +0xE except 0), `0106(1)` draws the half-time screen. **So a savestate taken at
  the stall already contains the +2 energy.** After the key: DS:830B = DS:0668[831A==0] + 10 (note
  the inverted index vs 998C), DS:832A=0x50, then 983F → 97D0 tick loop.
- Clock `970C` (seg_0791_16.asm:6-91): D733 zeroes DS:831D, so one D733 per 97D0 iteration and the
  minute advances in the same iteration. First half 46 calls (831F=0..45, ends 831B==8319=45),
  second half 46 calls (831F=46..91, ends 831B+8321==0 → 8326=1, whistle 2B0F(0x3F)). Goal minutes
  can match 831F in 1..45 / 46..90.
- Probe (scratch, e010-probe, 2026-10-05): from e006-1000-r0001, quick result; at the half-time
  stall the game sat blocked ~40 s (68 polls) with DS:7B62=0xa797 and DS:8336=0x51a8 unchanged, and
  E008-r0001's per-read seeds show the same 0xa797 from its read 9 to 35: **the half-time wait and
  the two Enters that leave it consume no RNG** (corroborates the static claim; the "two waits of
  different length" test is trivially covered by 68 polls over ~38 s).
- Same probe: half-time words 831A=00, 9A3D=00 (D5C1 fouls unreachable in this fixture),
  7C36=00 (no extra time), 9B34=27, 9B36=7. DS:8336=0x51a8 at half time equals E008-r0001's at
  full time: 8336 does not move in these quick matches (94E8 reached only via walk-offs from D5C1).
- Post-match tail: F1F6 after F098 draws the result screen `0106(1)`, then 8757/ED8A?/CB7D/E929/
  D050/BA4E (per managed team; BA4E draws: 1771:3558 or 3651 + 2×rand(4) per squad-pool player),
  then returns to 000E:6CA7, which plays the round's remaining fixtures (6970 → D47E/B7FA/B602).
  Whether any of that runs before the game blocks at the settled result screen (where the driver's
  full-time read lands, seeds frozen) is to be settled by comparing the model's last-D733 seeds
  with the recorded full-time seeds (E008-r0001: half-time a797 → full time 63d7).
- RNG-consumer closure (calls.tsv, all direct callers of 214B:0688/06B1/06D0/06FA and 0791:94C9):
  in the quick second half only D733, B19D, D5C1 (9A3D!=0), 7EEF (1/32 chance), 6337 (one rand(10)
  at most, after a goal), the C173 tree (BD83/BF6B/C01A/C0DF), and 94C9 via 7881 (walk-off, only
  from 7B77/7D56 inside 7EEF). Display, commentary, substitution (C88D) and menu routines draw
  nothing.

## Batch 3 (2026-10-05, fourth run): the substitution tree and the exact D733/B19D/tactics decode

- **`214B:007B(count, a, b)` is a byte SWAP** (decompiled seg_214B_01.c:104-130: exchanges count bytes),
  not a move. `214B:0018` = fill; `214B:0C57(n,set)` = element n (bit n-1) member; `0C79` set; `0CA1` clear.
- **`B19D` both draws of each contest use the SAME side's sums**: the side index is computed once as
  `1 - t` and reused for both `rand` calls (seg_0791_18.asm: B1C5-B1EC, B1F6-B220, B236-B251). So for
  team t's attempt: c1 = rand(mid[s]) vs rand(mid[s]); c2 = rand(2*def[s]) then rand(atk[s]), win iff
  2nd > 1st; c3 = rand(gk[s]) then rand(atk[s]), win iff 2nd > 1st; s = 1-t, all signed `jle` on fail.
  Team t = score byte 9B3C+t = country 9B34+2t (side s of 0BC4 = country 9B34+2s: D77E-D798 pairs
  side 1 with 9B36, side 0 with 9B34). So a team's goals are drawn from the OTHER side's sums
  (E008-r0001's screen: 9B3C=1 = Sweden, 9B34=27 = Sweden).
- **`D733` exact** (seg_0791_21.asm:794-DAF7): saved = word copy of 9B3C; 9B3C=0; the two 0BC4 calls;
  B19D(0A8A[8319==0x0F]); 4 stat draws (element 5 → 1/0A90[bit] → 7B7E+10t; element 1 → 1/0A8E[bit] →
  7B82+10t and 7B83+10*(1-t)); then per side t: if fresh[9B3C+t] > saved[t]: fresh -= saved; draw that
  many minutes rand(0A8C[..]) into local[t*16+j]; then per side t, per j: goal iff minute == 831F and
  saved[t] < 0xF and no goal yet this call; scorer slot = DS:0xA6B[rand(0x1E)] (so bytes 0xA6C..0xA89,
  values 2..11), redrawn while 3216(country[2*(slot-1)]) (unavailable); saved[t]++; 830B =
  DS:0668[t] + 3A82(country, squad word); 6443(minute, 830B, t); side loop forced to end. Restore
  9B3C = saved. Energy: for pitch slot 1..22, if 831B unsigned % 5 == 0 and player(pitch+0xD).+0xE > 1
  → dec +0xE. Then: if 9A3D != 0 and no goal → D5C1; goal → 0106(0)+65FE; else 8062; then 9372.
  DS:0668 bytes = [11, 0] (side t's pitch slots = 0668[t]+1 .. 0668[t]+11: t=0 → 12..22, t=1 → 1..11).
- **`8062`** (seg_0791_13.asm:905-8205): managed team (0B77: country+0x2E > 0x80 unsigned) → nothing
  in a quick match (9B40=0). Unmanaged team with 9B3A[t] > 0: squad slot s = 11 down to 2, pitch slot
  0668[t]+s, player = pitch+0xD; sub iff: player+0x10 element 6 clear AND +0xE > 0 AND 831B > 1 AND
  s > 1 AND 831B < 0x23 AND signed word +0x12 < 0x5A - 831B. After a sub at s: if 9B3A[t]==0 → s = 1
  (stop scanning). DS:066B bytes = [5, 2]; 9B3A[t] = 066B[9A3D] at A4A1 → 5 per team in a friendly
  (9A3D=0): substitutions are live in quick friendlies (E008-r0001 saw 5).
- **`C88D(0, t, slot, country)`** (seg_0791_20.asm:661-CAAA): 9B3A[t]==0 → only a forced C48D when the
  outgoing player's +0xE < 1. Else: fill 14 bytes at DS:99A2 with 0; `c7eb` walks squad slots 12..20
  filling 99A2[+7 of first available candidate] = squad slot (skips the outgoing player's word and
  3216-unavailable ones); `aae8(outgoing)` picks the bench squad slot from the formation table
  DS:0x99A + 8*(outgoing+6) (byte 0 = count; entries are +7 roles; candidate taken iff 99A2[role] != 0
  and (3041 two-footed or 3088 == (count>3 ? 1 : 0))); if 0 and the outgoing player is the keeper
  (+6 == 0) → `a9b8(20, +6, country)` = best bench slot 12..20 by DS:0x8D5[14*(+7) + (+6)] value
  (halved when 3041==0 and 3088 != (setcount>3 ? 1 : 0)). If still 0 → no sub. Else: bench player's +6
  := outgoing's +6; `007B` SWAPs the squad words of slots s and chosen; swaps the words at
  DS:9A3E + 0x28*t + 2*s and + 2*chosen (shadow squad); swaps bytes at DS:9B07 + 0x14*t + s and
  + chosen; then `c5dc(chosen, slot, t)`.
- **`c5dc(chosen, slot, t)`**: 0C79(3, player(outgoing)+0x10) (set element 3 = "substituted" mark);
  quick mode skips the display paths (C50C, 1E8D gated); `11eb5(0, chosen, s, t)` = substitution
  commentary (1D4A ring write, no RNG); pitch+2 word swap with [DS:640]/[DS:644]; player(outgoing)
  +0x12 := 0x2747, +0xF := 0, then 3431(outgoing); a2e6 re-derives the pitch record from the squad
  word (a260: pitch+6, pitch+0xD := country squad word of 2bb1(pitch)); the DS:9978 + 10*side marking
  games (managed teams only); dec 9B3A[t]; 9B55 := 1.
- **`65FE`/`65A4`/`6337`**: 65FE: 8325=1, 0441(4) (whistle, no RNG), pitch[k]+7(word) := pitch[k]+0;
  if 8326==0: 65A4 (per slot 1..22: pitch+0x12 := (2b51(pitch) != 0 and not keeper slot) ? 6 : 0;
  then 6337); C173((7C39==0) ? 1 : 0); display; 832A; if 9A3E → 9B55=1. `6337`: if 045D(830B)
  (keeper slots {1,12}): one rand(0xA); 830B := rand + 1 + 0668[2996()] (2996 = (830B < 12) ? 1 : 0);
  2a15 (display). In quick mode 6337 draws nothing else (63C3 branch is watched-only).
- **`C173(flag)`** exact (seg_0791_19.asm:997-C24A): d = signed(9B3C - 9B3D). Per team t with
  0B77(country[t])==0 (unmanaged): ad = |d|; ad < 2 → BD83(t); ad == 2 → BF6B(flag2, t) with flag2 =
  (score[t] > score[1-t]) ? 0 : 1; ad > 2 → score[t] > score[1-t] ? C0DF(t) : C01A(t).
  - `BD83(t)`: BBFF(9B7C[country[t]], country[t]) (reset +0x2D to R008, 3431 per player); if t==1 and
    80FC != 0 and BD03(t stronger): 0C79(1, +0x2D) + BBFF; then (any t) if BD03(t stronger): 2×
    { 0C79(rand(6), +0x2D) } + BBFF; clear 8332+t, 8334+t.
  - `BF6B(flag2, t)`: BD83(t); 3× { flag2 ? 0C79(rand(6)) : 0CA1(rand(6)) }; BBFF.
  - `C01A(t)`: only if 8332+t == 0: 5× 0C79(rand(5)); 0C79(6); BBFF; 8332+t := 1; then if the +6 of
    the player at country word +0x10 is in the set at CS:0xBFFA (bytes 00 30) → BEC7(country) + 230C.
  - `C0DF(t)`: only if 8334+t == 0: 5× 0CA1(rand(5)); 0CA1(6); BBFF; 8334+t := 1.
  - The rand RESULT is the element number: 0C79(r)/0CA1(r), r ∈ 1..6 or 1..5 (bits r-1).
  - `BBFF(value, c)`: +0x2D := value; per nonzero squad word 3431. `BD03(a,b)`: sum of 377E over the
    first 11 squad words, unsigned >. `BEC7`: per slot 1..11, player+6 in set CS:0xBEA7 (0E 00 ...) and
    available and 2FAD < 0x48 → +6 := DS:0xA28[(2FAD >= 0x48) ? 1 : 0]. `230C` (the `call 0x1230c`
    target, seg_0791_04.asm:357): rebuilds pitch placement from positions — read if the C01A branch
    ever fires in a run.
- `1EB5` (c5dc's commentary) = 1E53 + 1D4A + 1829 (ring write; no RNG). `a2e6`/`a260` re-derive pitch
  fields from the squad words. `2996` = (830B < 12) ? 1 : 0. `045D` = slot ∈ {1,12} (keeper).
  `1771:0B77` = country+0x2E > 0x80 (unsigned). `1771:2FAD` = table lookup DS:0xE54[player % 12] /
  DS:0xE46[+7] product-ish (only reached from BEC7).
- `D5C1` foul path (9A3D != 0 only) and its 7EEF branch stay as batch 1 traced them; our friendly runs
  have 9A3D = 0, so the model implements D5C1's draws up to `7EEF` and raises if the walk-off branch
  (which steps DS:8336) would fire — no E010 run may reach it without the model being extended first.
- Tables dumped from the e006-1000-r0001 savestate (DS bytes): 0668 = 0b 00; 066B = 05 02;
  0A6C..0A89 (scorer slots, indexed 0xA6B+rand(30)) = 02 03 04 05 05 06 06 07 07 08 08 08 09 09 09
  09 09 09 0a 0a 0a 0a 0a 0a 0b 0b 0b 0b 0b 0b; 0A8A = 0c 10; 0A8C = 5a 78; 0A8E = 21 0a;
  0A90 = 3c 1e; 0D4E (pos→line) = 00 01 01 04 04 02 02 02 02 05 05 05 03 03 00 01;
  0A90[2..11] = 0b 0a 09 08 07 06 05 04 03 02 (D5C1's slot map).

## Batch 4 (2026-10-05, fifth run): the model made seed-exact, and the three decodes that got it there

The model (`runtime/model/quick_engine.py`) reproduces the probe replay of E008-r0001's second half
from `scratch/driver/e010-probe/halftime.sav` EXACTLY: score [1,0], `DS:7B62` 0xa797 -> 0x63d7,
`DS:8336` 0x51a8 unchanged, goal by 538 (Nilsson) at minute 85. Verified against the per-poll seed
checkpoints of trace-e008r0001-slow2/slow3 and a fresh sums probe (scratch/probe_sums.py, replay
from the stall: per-poll DS:9B45.. sums; the stall and mid-85 snapshots pin the sums too). Three
decodes fixed on the way (all listing-verified, the notes above were wrong or the model misread):

- **B19D contest sides**: the first draw of each contest uses side 1-t's word (B1C5-B1D4: al = 1-t),
  the second side t's (B1E0-B1E8): c1 rand(9B4D+2(1-t)) vs rand(9B4D+2t); c2 rand(2*(9B49+2(1-t)))
  vs rand(9B51+2t); c3 rand(9B45+2(1-t)) vs rand(9B51+2t). Batch 3's "both draws the same side"
  claim is RETRACTED.
- **D733's fill/goal structure**: per team t (0 then 1): only when fresh 9B3C[t] > saved[t]
  (D88F `ja`), subtract (D8A5), then draw minutes for BOTH teams j=0,1 from the CURRENT 9B3C[j]
  counts (D8B2-D8FC: j loop 0..1, k 1..count, buf[j][k] = rand(0xA8C[idx])), and the goal phase
  (D911-DA43) runs after EVERY team's fill attempt, not once at the end: the t=0 fill's minutes
  score before t=1's fill redraws them (this is why the model first missed the 85th-minute goal:
  the second fill overwrote the drawn 85). The goal phase counts read 9B3C[j] (excess for a team
  that subtracted, raw fresh otherwise); at most one goal per call ([bp-0x2e], DA30/DA34).
  Scorer slot byte = DS:0xA6B + rand(30) (r in 1..30, so bytes 0xA6C..0xA89), redrawn while
  1771:3216(squad word) (D973-D9B2).
- **Substitution c5dc**: a2e6 (C6E5) re-derives pitch+0xD from the ALREADY-SWAPPED squad before
  the C6FA-C724 block, so +0x12 := 0x2747, +0xF := 0 and 3431 apply to the INCOMING player (only
  when 0B77(team) says unmanaged, C700); the 0C79(3) mark at C612 (before a2e6) hits the OUTGOING
  player. The incoming player's fresh +0xF (3431) changes its 0BC4 attack/defence share.
- **Set-constant conventions** (this is where T19 was bitten before): one-byte sets via 214B:0C57/
  0C79/0CA1 hold element n at bit n-1; multi-byte sets via 23E4:08DF hold element e at bit e of
  byte e>>3. So CS:1771:3411 (1B 00) = positions {0,1,3,4} (3431's element-5/1 branch; the model
  first read it bit n-1 -> {1,2,4,5}, wrong), CS:1771:0BA4 (62) = elements {1,5,6} (0BC4's share
  loop), CS:0791:BEA7 (00 0E) = {9,10,11} (BEC7), CS:0791:BFFA (00 30) = {12,13} (C01A's tail),
  CS:1771:3139 (88 04) = {3,7,10}, CS:1771:3159 (10 09) = {4,8,11} (3179 wrong foot).
- Debug method that pinned it: the LCG is a bijection, so every observed seed lies at one exact
  draw count on the model's chain; polls taken MID-D733 (e.g. 0xc6ba = 3 draws into minute 85's
  fill) pin draw counts, not outcomes — the per-poll SUMS probe (DS:9B45.. read at the stall and
  at the mid-85 goal pause) was what exposed the one-m8-share difference (727/389 vs 730/386).

## Batch 5 (2026-10-06, rework round 1): nine model rules corrected from the listing (review R1-R9)

Each item corrects `runtime/model/quick_engine.py`; the listing line is the authority.

- **R1, scorer table extent (D973-D984)**: the draw reads the byte at `DS:0xA6B + rand(30)`,
  r in 1..30, so the array runs 0xA6B..0xA89 = 31 bytes: a dummy base at 0xA6B plus the 30
  entries. The model had loaded only 30 bytes from 0xA6B, so r = 30 (byte 0xA89, value 0x0B)
  raised IndexError. Batch 4's wording "bytes 0xA6C..0xA89" was right; the load length was not.
- **R2, D733's fill loop control (DA30-DA55)**: batch 4's "the goal phase runs after EVERY
  team's fill attempt" is RETRACTED. The goal phase (D911-DA43) is entered only by falling
  through D90B at the end of a fill (fresh > saved, D88F `ja`; otherwise D893 jumps straight to
  the DA4C loop test). And when a goal is scored, DA34 sets the outer team byte [bp-0x2d] to 1,
  so DA4C ends the fill: team 1's fill (and its `rand(0xA8C)` draws) never runs after a goal.
- **R3, C01A's tail branch (C0C5-C0D6)**: batch 3's "if +6 is in the set at CS:0xBFFA →
  BEC7 + 230C" is RETRACTED: `23E4:08DF` membership ZERO takes C0CA's `je` to C0CE (the
  BEC7/230C calls); membership in {12,13} skips them (C0CC → return). So the tail fires when
  the +0x10 player's +6 is NOT 12 or 13.
- **R4, BEC7 stops after the first write (BF56-BF5A)**: after BF56 stores the replacement
  position, BF5A jumps to the return at BF65; only the FIRST qualifying back-four player is
  re-placed (batch 3's "per slot 1..11" wording implied all).
- **R5, 230C's swaps are squad swaps too (23C4 → 2218, 2242-226B)**: every pitch-record swap
  calls 2218, which swaps the same two squad words (loop indices 1..11) of the team's country
  record (and the shadow words at 9A3E+0x28t and the 9B07 bytes, which the engine does not
  read). Scorer selection and later substitutions read those squad words.
- **R6, c5dc calls 230C unconditionally (C7A7)**: after the DS:9978 marking games and BEFORE
  the `dec 9B3A` at C7DC. The substitution path therefore re-sorts pitch and squad every time.
  With R5/R6 faithful, two more decodes fell out (both listing-verified):
  - a2e6 inside c5dc (C6E5) runs BEFORE the sort and re-points the pitch record (+6 := the
    address slot, +0xD := the squad word = the incoming); reading `squad[s-1]` after the sort
    is wrong, and C88D's s is address-based (C8AE: `slot - 0668[t]`), not 2bb1-based;
  - 230C is three parts: the pitch sort, then `a260` for slots base+1..base+10 re-deriving
    pitch+6/+0xD (2541-258A; base+11 is left with its traveled +6), then a BENCH sort of squad
    slots 12..20 by +6 (258C-25F3, `jb` at 25E3, swaps via 2218 at 25E6).
  In the ten E010 fixtures the pitch sort after a substitution is a no-op (the incoming inherits
  the outgoing's position, and 8062 scans s = 11 downwards), which is why the pre-rework model
  could match without any of this.
- **R7, a9b8's table index (AA4E-AA62)**: `BENCH_VALUE[14*[bp+6] + (+7)]` — the POSITION
  ARGUMENT passed by C88D (the outgoing keeper's +6), not the candidate's own +6. Batch 3's
  "DS:0x8D5[14*(+7) + (+6)]" has the operands of the product swapped.
- **R8, the manager quality byte is zero-extended (0AD9)**: `xor ah,ah` before `cdq; idiv 8` —
  the byte is unsigned (0..255), so the bonus is byte/8 + 16 (0x80 → 32). The "signed idiv 8"
  claim in the 0BC4 section above is RETRACTED (the idiv itself is signed, but its dividend
  cannot be negative).
- **R9, D5C1's prefix (D5CB-D63E)**: D5D0 `inc ax` — r = rand(10)+1 in 2..11 (the model had
  used the raw draw, giving pitch slot 24-r in 14..23 and slot 23 out of range); and the 2956
  availability checks (D618 for the r slot, D634 for the other) come BEFORE the 06FA coin at
  D63E — a return at either check saves the coin draw. Batch 1's D5C1 trace (lines 157-162)
  already said this; the model had drifted from it.

The ten records still compare 9/10 (E010-r0010's documented DS:7B62 divergence unchanged:
score, goals and DS:8336 match). R10 (run.py's "match read" ordinal) is a locator wording fix
in the run script, not an engine rule.
