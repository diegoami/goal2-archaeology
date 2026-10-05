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
