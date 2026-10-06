# E011 q010-watched-engine — reading notes (the watched engine `0791:9564`, milestone 1)

Live notes for the tick map of the watched engine and its ground truth. Addresses are
`segment:offset`; listings are `static/goal-exe/code/seg_0791_NN.asm` (the named view
`static/goal-exe/named/` was read first, then the raw listings to confirm order and guards).
Status: append-only, commit per batch.

## 1. The tick loop's watched branch (one iteration, in order)

`0791:97D0` `match_tick_loop` (seg_0791_16.asm:93-141), per iteration while `DS:9A3E` is clear:

1. if `DS:7C37` set → `0791:10C65` action replay (`97DF`-`97E9`, seg_0791_16.asm:103-105);
2. else if `DS:9B55` set → `0791:15B9` (`97EB`-`97F2`, :107-109);
3. if `DS:9B55` → clear `DS:0C20`; then clear `DS:9B55` and `DS:7C37` (`97F5`-`9806`, :111-115);
4. `call 9564` — the watched engine, one "player sweep" (`980B`, :117);
5. if `DS:9A3E` is STILL clear (R was not pressed inside 9564): `call 8CF5`, then
   `call 9119` with `DS:82EE` and last argument 0 (`9815`-`9821`, :121-126);
6. `call 970C` the clock (`9824`-`9825`, :128-129); loop while it returns 0 and the guard
   holds (`982A`-`9837`, :133-139).

So **the display calls `8CF5` and `9119` run every watched tick from the loop itself**, after
the engine and before the clock — this is the divergence F005 flagged: `9119` draws one
`rand(2)` per tick (§3). With `DS:9A3E` set (quick mode) steps 4-5 never run (`D733` instead),
which is why T24's D733-skip list cannot carry over.

## 2. `0791:9564` `watched_match_engine` — internal order (seg_0791_15.asm:946-1140)

One call = one sweep of an outer slot loop `[bp-2] = 1..0x16` (22 pitch records;
`9567`-`95A0`, `96F3`-`96F9`). Prologue `push bp; mov bp,sp; sub sp,8` (`9564`-`9569`).
Per slot:

- **Ball phase, guarded twice** (`9574`-`95B6`):
  - `DS:8302` must be nonzero (`9574` `cmp byte [0x8302],0`; else jump to the per-slot tail
    `969B`) — the "play running" gate;
  - the byte at `0x899 + 0x16*flag + slot` must be `<= DS:8300` (word compare, `95AA`-`95B4`),
    where `flag` = 0, or (only when `DS:8303` is nonzero, `9582`) the membership of `DS:8327`
    in the set at `CS:9544` (`23E4:08DF`, `958D`-`9597`; flag 0/1 at `9599`/`959D`).
    `0x899` is the second half of a 22-byte-per-flag table at `DS:883` (the per-slot tail
    reads `DS:883[slot]` as a record index, `969E`). The gate skips slots whose threshold
    exceeds the counter `DS:8300`.
- **Shot statistic for the keeper's end** (`95B9`-`95EE`): when the ball's y `DS:82F7` is
  nonzero, `2BE5 attack_direction(DS:80FE)` (the side's slot-1 keeper record) → `dl`, compare
  `DS:7920[(0x82F7 > 0)]` (form_delta) with it and increment the word `DS:80F6 + 2*eq`
  (keeper record +0xE, a two-word counter pair) (`95C0`-`95EE`).
- **Ball move and chase** (`95F2`-`9601`): `83A2 move_ball(DS:82F6)`; `2FB1
  find_nearest_to_ball()`; `2996 ball_holder_is_side0()`.
- **Keeper special** (`9605`-`9666`): keeper record = `(0668[side]+1)*0x16 + 0x80E8`
  (`9605`-`9623`); if the `23E4:08DF` membership (as above) holds (`962F`, `jne 9669` — note
  the reversed sense: the *non*-member path checks the keeper): `2CEC player_at_ball(keeper)`
  is false AND (keeper x == ball x `DS:82F6` or `2E36 in_own_goal_area(keeper, ball)` true)
  → `8AE9 update_player(keeper)` (`9643`-`9666`).
- **Woodwork** (`9669`): `59B3 check_woodwork()`; if it returns 0 → the **player loop**
  `[bp-4] = 1..0x16`: `6188 handle_player_at_ball(record)` per record while `DS:8302`
  (`9670`-`9699`).
- **Per-slot tail (always, even when the ball phase was skipped)** (`969B`-`96D8`):
  - record = `0x80E8 + 0x16*DS:883[slot]` (`969E`-`96AB`);
  - `2956 player_unavailable_on_pitch(record)`; if available → `8AE9 update_player(record)`
    (`96B5`-`96C8`);
  - if `DS:883[slot] == DS:830B` (the slot on the ball) → `2FB1 find_nearest_to_ball()`
    (`96CB`-`96D6`).
- **Per-slot epilogue** (`96DB`-`96F1`): `94E8 speaker_noise()` (second stream `DS:8336`,
  not the main seed — E010 notes, "RNG"); `8F10 draw_ball(DS:82F6)`; `9372 match_key_poll()`.
- **Loop control** (`96EA`-`9703`): if `DS:9A3E` was set (R taken) → return at once
  (`96F1`); slot 0x16 done → if `DS:832A > 0` subtract 2 (`96FC`-`9703`, the kick-off /
  restart countdown) and return; else next slot.

So one tick = 22 slot iterations, each: (guarded ball logic for its slot) + one
`update_player` on the mapped record + `speaker_noise` + `draw_ball` + the key poll; and
once per tick (first slot only, in the ball phase) the keeper checks, the woodwork check and
the 22-player `handle_player_at_ball` loop. `6188` dispatches: a keeper on the ball → `5B36`,
another player → `5F8A` (annotation, seg_0791_10.asm:937+).

### Callee roles (F005's list, each with its listing)

| Callee | Role | Listing |
| --- | --- | --- |
| `0791:2956` | player_unavailable_on_pitch: `1771:3216` of the record's player at +0xD | seg_0791_04.asm:1052-1064 |
| `0791:2996` | ball_holder_is_side0: `DS:830B < 0x0C` (a 0/1 side index) | seg_0791_04.asm:1085+ |
| `0791:2BE5` | attack_direction: `DS:7920[team ^ half]`, a sign | seg_0791_05.asm:257+ |
| `0791:2CEC` | player_at_ball: record position word equals `DS:82F6` | seg_0791_05.asm:404+ |
| `0791:2E36` | in_own_goal_area of the keeper record against the ball | seg_0791_05.asm:600+ |
| `0791:2FB1` | find_nearest_to_ball: per side, slots base+2..base+11, nearest by Manhattan distance → `DS:8311[side]`, goal-side nearest → `DS:830F[side]` | seg_0791_05.asm:815+ |
| `0791:59B3` | check_woodwork: ball moving, holder not a keeper, `abs(y)=0x25`, `abs(x)<2` → 593B may bounce it and returns 1 | seg_0791_10.asm:6+ |
| `0791:6188` | handle_player_at_ball: keeper → `5B36`, player → `5F8A` (only in watched matches) | seg_0791_10.asm:937+ |
| `0791:83A2` | move_ball: velocity +6/+8 of the ball record, timer +0xA, redraw 8F10; out of bounds → restarts 698E/690C/6E11/6E6E/6F01 | seg_0791_14.asm:96+ |
| `0791:8AE9` | update_player: state byte +0x12 handler, then `8889`, `8537` (draw); counts +0x14 | seg_0791_14.asm:892+ |
| `0791:8F10` | draw_ball: restore the old cell in the screen buffer `DS:7C16`, write the new cell | seg_0791_15.asm:246+ |
| `0791:9372` | match_key_poll: on R (or `DS:7C38`) → `92FC`; returns when no key waits | seg_0791_15.asm:726+ |
| `0791:94E8` | speaker_noise: pitch from `94C9`, the second stream `DS:8336` | seg_0791_15.asm:900+ |
| `23E4:08DF` | set membership test used twice per slot for the flag and the keeper gate | seg_0791_15.asm:9592, 962F |

`0791:8CF5` (called by the loop, not 9564): per side, over the side's slots, tracks the most
advanced record (y × attack_direction, `2BE5`) into the byte `0x82E2 + 6*side + 1`
(seg_0791_15.asm:28-110). No RNG.

## 3. Which draws happen per tick, which per event

All draws are the LCG `214B:0688` through `06B1` (rand 1..n), `06D0` (chance 1/n), `06FA`
(coin); `0688` itself is called directly only by `214B:06B1/06D0/06FA` and `0791:94C9`
(the second stream, DS:8336). Over the tree reachable from `9564` (470 routines in
`calls.tsv`), the direct callers of a wrapper are:

- **Per tick, unconditional**: `9119` (called by the loop every tick, argument 0): exactly
  ONE `06B1(2)` — branch `[0x82F7] > 0` at `91C8` calls `06B1` at `91CC` (then min-clamp
  `214B:0D1C`, which draws nothing — seg_214B_02.asm:0D1C-0D53, a two-word min), branch
  `<= 0` calls `06B1` at `91F1` (then `0D56`, a max). Then it draws the referee sprite
  (`8E24`) and writes the glyph cell — the display path that draws from the seed every tick.
- **Per tick, conditional**: `8889` (reached from `8AE9 update_player` per updated record)
  draws ONE `06FA` coin at `8A2E` (seg_0791_14.asm:8A2E) on the path where the record is not
  the ball holder (`88DE`/`88F2` bail out) and `2CC5` returned 0 — the sprint-direction
  choice; 0..22 coins per tick. `9119`'s and `8889`'s draws are the floor consumption of a
  tick; everything below is event-driven.
- **Event draws** (fire only on restarts, contests, fouls, goals, substitutions, tactic
  updates): direct callers `0791:593B`/`59B3` (woodwork bounce), `5B36`/`5F8A` (ball
  handlers), `690C`/`698E` (ball restarts), `6337` (kick-off choice after a goal),
  `7EEF` (foul result), `8206`/`5513` (substitutions), `67B6`/`690C` (→ `C173` tactic
  updates, F010), `34C1`, `384C`, `3B15`, `3B9E`, `3BEE`, `3C3F`, `3DF6`, `3EF8`, `3FAD`,
  `408E`, `4354`, `4532`, `47C5`, `4A28`, `4B64`, `4DA9`, `4E28`, `5049`, `539F`, `5E41`,
  `5F06`, `7069`, `74C2`, `7621`, `287C`, `2B7B`, `BD83`, `BF6B`, `C01A`, `C0DF` (tactics).
  Their per-event shapes are as E010's notes batch 3 traced for the shared subtree
  (C173, 6337, 7EEF, 65FE) — the watched-only ones (5B36, 5F8A, 8206, 690C …) are milestone
  2+ material; the tick map only needs that they draw on events, not per tick.

The key asymmetry with the quick engine: there `D733` is called once per *minute* and draws a
fixed pattern; here the loop runs ~0x25 iterations per *minute* (see §4), each consuming at
least the referee's `rand(2)`, plus coins, so the seed advances hundreds of times per minute
of match time.

## 4. The clock in watched mode

`970C` (seg_0791_16.asm:6-91): while `DS:8325` is set, counts `DS:831D` down; at 0 reloads
`0x24` and takes a minute (`831B`, then `8321`), increments `DS:831F`, draws the big digits,
and at the half's end (`831B == DS:8319` or `DS:8326`) returns 1. **`9564` never writes
`DS:831D`** (no `0x831d` operand anywhere in seg_0791_15.asm:946-1140), unlike `D733`
(seg_0791_21.asm:811). So a watched minute = the 0x24 countdown of `831D` ticks: the tick
counter is `DS:831D` itself, and `(DS:831F, DS:831D)` identifies a tick within the match:
`831F` = the minute, `831D` = the sub-tick (a fresh 0x24 after each minute boundary). The
savestate reads of the ground truth record both words, which pins each read to its tick.

## 5. The half-time stall and the resume (why the harness can start there)

`0791:9A32` (seg_0791_16.asm:268-346) is the pre-half routine both engines share: per slot
1..22 the player's `+0xE` +2 (set-gated, `9A71`-`9A85`), `DS:9B41=1`, screen copies, `0106`,
then the wait `ED8A` (`9AE0`): skipped only when `DS:80FD==0` AND the key `DS:A977` is in the
set at `CS:9A12` (`9AC6`-`9ADB`); with no key sent the wait always runs. E010's batch-2 lesson carries over — the
half-time screen is drawn BEFORE the wait and the wait consumes no RNG, so the savestate at
the stall is the exact input of the second half. After the wait, the tail sets
`DS:830B = 0668[(831A==0 ? 1 : 0)] + 10` (`9AEE`-`9AFC`) and `DS:832A = 0x50` (`9AFF`), then
calls `983F` (the half, `9B05`).

`0791:983F` (seg_0791_16.asm:349-407; decompiled seg_0791_07.c:516-553) per half:
`DS:9B41=0`, `DS:830E=0`, `8062` (substitution logic), `2A15`; **watched-only**: `2929`,
`8CCA` (`9855`-`985D`, gated on `DS:9A3E==0`); then `8302=0`, `9B55=1`, `0C20=0`, `7C37=0`,
and the tick loop `97D0` (`9840`); after it, watched-only cleanups `9079` per side and on the
referee `DS:82EE` (`9865`-`9873`), `DS:8325=0`, speaker off. The watched engine therefore
consumes RNG in `983F`'s head too (8062's tree) — the harness enters at `983F`'s entry, not
at the loop, so that head runs as real guest code (T24's quick harness could shortcut it
because its records proved the head's writes were exactly the constants it applied; here
`2929`/`8CCA` are extra).

The delay family is inert at top speed: `0425 match_delay` calls `214B:1E09` only when the
speed byte `[DS:A923]+0x3F` is above 0 (seg_0791_01.asm:0428-0431, `jbe` skip) — the watched
ground truth runs at the delay byte 0 (five Rights, E004), so no delay runs. The `000E`
wait family (05F6/0572/04F5/045D, the crowd animation — 1000+ draws per call, E010 notes
"RNG-consumer closure missed") has callers only in `000E` menu code (`calls.tsv`), none
reachable from `0791:9564`/`97D0`; the harness keeps T24's skip of it as a safety net with a
stray log that must stay empty.

## 6. The ground truth's checkpoints (definition, and why)

A savestate read during play catches the guest at an arbitrary instruction: its `DS:7B62` is
the value after the last RNG event before the read, and which event was last depends on the
host's timing, not on anything reproducible. But `(DS:831F, DS:831D)` (§4) pins the read to
its tick, and the read's seed value must then be one of the values the seed word takes during
that tick (its value at tick start and after each draw in it). The E011 record therefore
stores `(831F, 831D, 7B62)` for every mid-play read, and `emu_check.py` matches a checkpoint
when the record's seed value lies on the emulated trajectory at that minute and sub-tick —
the exact-tick, exact-value form of "the record's read at that minute". Reads with the clock
stopped (`DS:8325 == 0`, the stalls) are not checkpoints; the half-time stall itself is the
harness's start state.
