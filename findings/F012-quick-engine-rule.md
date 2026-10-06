# F012 The quick-result engine: one D733 per minute, three contests per attempt against the line sums, and a ±1 form swing on every player after a goal

- **Status**: proposed
- **Question**: What is the exact rule of GOAL's quick-result engine (`0791:D733` and everything it
  reaches) — the per-minute structure, the goal contests, the line sums they are drawn against, the
  goal minute and scorer, the post-goal state changes, the substitutions and the computer's tactics —
  such that a rebuild reproduces a recorded quick match seed-exactly? (Q010, `docs/backlog.md`;
  T23/T24, milestone 2)
- **Tests claims**: the backlog's Q010 (the quick engine's rule); feeds the rebuild's quick-result
  path and the bot's World-Cup optimisation; bears on F005 (the quick result runs another engine
  than the watched match — this is the quick one), F010 (R008 tactics, read by BD83), F004 (the RNG
  and its two streams).
- **Experiment and runs**: E010 (T23's ten records r0001..r0010 over E006/E008 start states, and
  T24's Unicorn full-loop emulation of r0010's second half,
  `experiments/E010-q010-quick-engine/emu_full_loop.py`).
- **Artifact**: set `goal2-67cf27d6`, variant none (the E010 records' half-time savestates).
- **Max intervention**: I2 (savestates read and written by the driver; the model checked against
  the records' recorded final score, goals and seed words; the Unicorn harness runs the original
  binary's own code from the published half-time savestate).
- **Tier reached**: V2 (the model is seed-exact on 10/10 E010 records, `check_model.py`; the
  original binary emulated from r0010's half-time state reproduces the record's own trajectory
  0x543a/3617 draws exactly).
- **Confidence**: unreviewed (status `proposed`). Static: every claim is read from the listing
  (`static/goal-exe/code/`), cross-checked against the decompiled view where useful. Behavioural:
  the ten E010 records and the full-loop Unicorn emulation of r0010's second half (which passes
  through the goal, the substitutions and the form swing and ends at the record's own full-time
  seed). Claims marked "both" have both routes; a claim on one route says so.

## Answer

- **The quick match runs one `D733` per game minute, paced by the tick loop, not by the timer**
  (both). `0791:97D0` (seg_0791_16.asm:97D3-983C) loops: `DS:9A3E != 0` → `call 0791:D733` →
  `jmp 9824` → `call 0791:970C`; with `9A3E = 1` (quick mode) the watched branch (9564/8CF5/9119)
  never runs. `D733` zeroes `DS:831D` at its start (:D759), so every `970C` call takes the
  minute-advance branch (:972E-9762: `831B` dec, `831F` inc, `831D := 0x24`) — the 0x24 sub-tick
  countdown never elapses and the half is CPU-paced: 46 D733 calls per half, `831F` = 0..45 then
  46..91, `831B` = 91 − `831F` throughout. The original's second half passes inside ~1 s of host
  time (r0010's record, reads 41→42). High confidence (listing; the record's read timings; the
  Unicorn loop reproduces the whole half).
- **Per minute, `D733` draws in this order** (both). Save the score word `DS:9B3C` to a local and
  clear it (:D75C-D77B); `0BC4(flag, side, country)` for both sides (:D77E-D798, side 1 first with
  `DS:80FC` as its flag); `B19D(attempts)` with attempts = `DS:0A8A[8319==0x0F]` = 12 (:D79D-D7B4);
  four statistics chances — per side, element 5 of `+0x2D` → 1/`DS:0A90[bit]` → `DS:7B7E+10t`, then
  element 1 → 1/`DS:0A8E[bit]` → `DS:7B82+10t` and `DS:7B83+10·(1−t)` (:D7C0-D86A, counters only,
  never in the score); then the fill and goal phase (below); then the energy loop (below); then
  `9A3D != 0` and no goal → `D5C1`, goal → `0106(0)+65FE`, else `8062`; last `9372` (:DACB-DAF1,
  the key poll, no RNG). High confidence.
- **`B19D` plays up to three contests per attempt, the opponent's draw first** (both). For team
  `t` (the score byte's side; team t's goals are drawn against side 1−t's sums — `al = 1 − t` at
  B1C5-B1D4, the second draw side `t` at B1E0-B1E8): c1 `rand(mid[1−t])` vs `rand(mid[t])` (B1DF,
  B1F1); c2 `rand(2·def[1−t])` (B207) vs `rand(atk[t])` (B220); c3 `rand(gk[1−t])` (B23B) vs
  `rand(atk[t])` (B24D); each `jle` (signed) stops the attempt at 2/4/6 draws; all three won →
  `inc DS:9B3C+t` (B261). So a team scores from the *opponent's* defence and keeper. High
  confidence (listing; the model's 696/341/40 contest draws in the emulated half match the
  structure exactly).
- **The line sums `0BC4` are the eleven squad strengths plus a manager bonus, shared to
  attack/defence by the players' tactic bits** (both). `1771:0AA7`: M = manager byte
  `[0xA91F]+3·(+0x2E)+1`, zero-extended, `idiv 8`, `+0x10` (:0AD9 xor ah,ah). Per squad word 1..11:
  `v = 377E(w)`, `+M` when v ≠ 0; positions ≠ 0 add `M/8` to attack (9B51+2·side) or defence
  (9B49+2·side) per element e ∈ {1,5,6} — e < 5 uses the player's `+0xF` element (e+4) when set,
  else `+0x2D`'s element e (:0C95-0D01); the position→line table `DS:0D4E` = [0,1,1,4,4,2,2,2,2,5,
  5,5,3,3,0,1] sends k<4 to sums[k] and k≥4 halved to sums[k−3] and sums[k−2] (:0D32-0DCD); with
  flag set every sum gains `idiv sum/8` (:0DDA-0E1C). `377E` = `(+4) + s8(+0xE) − 0x3E`, form
  `+0xC` ≥ 0x20 shrinks `v − v idiv 16` else adds, clamp 0..0x100, wrong foot halves. High
  confidence.
- **The fill and goal phase: minutes are drawn for both teams only when a team's fresh count
  exceeds its saved score, and at most one goal is scored per call** (both). Per team t (0 then 1),
  only when fresh `9B3C[t] > saved[t]` (`ja`, D88F): subtract the saved score (D8A5), then draw
  minutes for BOTH teams j = 0, 1 from the current `9B3C[j]` counts (D8B2-D8FC,
  `rand(DS:0A8C[8319==0x0F])` = 90); the goal phase (D911-DA43) is the fill's own j loop fallen
  through: a drawn minute equal to `831F`, with `saved[j] < 0xF` and no goal yet this call, draws
  the scorer slot as the byte at `DS:0xA6B + rand(30)` (D973-D984, a 31-byte table: a dummy base
  at 0xA6B plus 30 entries), redrawn while `3216` says unavailable (D9A7-D9B2); `inc` the local
  count, `DS:830B := DS:0668[t] + squad slot`, `6443(minute, 830B, t)`; a scored goal sets the
  outer team byte (DA34) so the other team's fill never runs that minute. High confidence (listing;
  R1/R2 of T23's rework round; the model is seed-exact).
- **`6443` writes the scorer's record as well as the commentary** (both). The scorer's `+0x0A`
  (goals) increments (:6484); `+0xC := clamp(s8(+0xC) + s8(DS:0x7920[7C39≠0?0:1]))` — +1 in a quick
  match — via `7CC5`'s `214B:2000` clamp (:64BF-64DE, 7CC5:7CCE-7D09); `+0x12 += s8(DS:0x720[0x26])`
  = +40 (the goal commentary's ring write, 1E53's tail 1E9C-1EAB). `+0xC` is read by `377E`, so the
  scorer's strength shifts from the next minute on. High confidence (T24 round 2 diffed the staged
  goal-pause savestate against the model byte-for-byte).
- **After a goal, `65FE` swings EVERY available player's form by ±1 by side** (both — T24 round 3's
  find, the cause of E010-r0010's divergence). `65FE` (seg_0791_11.asm:65FE-6754) runs after the
  goal screen `0106(0)`: the whistle `0441(4)` (:660D — the ~4.5 s "goal pause" the record's reads
  sit in; it draws nothing), the pitch+7 word copies (:6617-663A, display), `65A4` (pitch+0x12 :=
  6 for same-side non-keeper slots else 0, then `6337`: when `830B` is a keeper slot {1,12},
  `830B := rand(10)+1+0668[2996()]`, :6384-638D), `C173` (the computer's tactics, :665C), then a
  per-slot loop (:6666-66DD): for pitch slot 1..22, skip the unavailable (2956 at :6683), else
  `7CC5(pitch, 0, s8(DS:0x7920[2b51]))` where `2b51` (:2B51) = "the slot's side (2974, pitch+6 <
  12) equals `830B`'s side (2996, 830B < 12)". `DS:0x7920 = [0xFF, 0x01]`: every available player
  on the scorer's side gains +1 form, every available opponent loses 1 — read by `377E`, so both
  line sums shift from the next minute on. High confidence (the listing; the full-loop Unicorn
  emulation with and without the model's swing lands on 0x543a/3617 vs 0x8ddf/3640 — the record's
  own value is 0x543a; `check_model.py` 10/10 only with the swing).
- **The LCG chain position is independent of n, so a seed match does not prove the draws match**
  (both, method). `214B:0688` steps `seed := seed·0x7ABD + 0x1B0F` (16-bit) regardless of n; the
  value is `((seed·n)>>16)+1`. Two runs can make the same NUMBER of draws with different n's and
  sit on the same seed: E010-r0010's pre-fix model matched the original's seed at the goal pause
  (0x5164) and through minute 85 (0x40b5) while every contest drew from sums 589/914 instead of
  595/919 — the first divergent draw is minute 63's first B19D contest (`r0010-divergence.txt`);
  the first outcome flip (and seed split) came at minute 86. High confidence.
- **The energy loop decrements every fifth minute** (both). For pitch slot 1..22, when
  `831B unsigned mod 5 = 0` and the player's `+0xE > 1`, dec `+0xE` (:DA6F-DAC9, `div cx` at
  :DA92). Minutes 66, 71, 76, 81, 86 and 91 of the second half. High confidence.
- **Substitutions are silent in a quick match: `8062` scans down from squad slot 11** (both). Only
  unmanaged teams (country `+0x2E ≤ 0x80`, `1771:0B77`) with budget `DS:9B3A[t] > 0` (5 per team in
  a friendly, `DS:066B[9A3D]` at A4A1): squad slot s = 11 down to 2, pitch slot `0668[t]+s`, sub
  iff the player's `+0x10` element 6 clear, `+0xE > 0`, `1 < 831B < 0x23`, and the PLAYER's signed
  `+0x12 < 0x5A − 831B` (:815D-81AF). `C88D(0, t, slot, country)` picks the bench slot from the
  formation table `DS:0x99A + 8·(outgoing pos)` (aae8, seg_0791_17.asm:AAE8-AC64) against c7eb's
  map of available bench `+7` roles, with the foot expectation `1` when the position's Pos() count
  exceeds 3; the keeper falls back to `a9b8` (best bench by `DS:0x8D5[14·pos + role]`, the position
  ARGUMENT's product, :AA4E-AA62); the outgoing's position is copied to the incoming (C9AD-C9CA),
  the squad words swap, and `c5dc` marks the outgoing `+0x10` element 3, gives the incoming
  `+0x12 := 0x2747`, `+0xF := 0` and `3431`, then `230C` re-sorts pitch and squad (C7A7). The
  substitution animation tree (`0791:8206`, from 5513/5B36 — the WATCHED engine) clears `8325` and
  draws via `9119`; it is NOT reachable from a quick result. High confidence (the r0009/r0010 twins
  made all five N.Ireland subs identically).
- **The computer's tactics `C173` react to the score difference** (both, and F010). `d = s8(9B3C −
  9B3D)`; per unmanaged team: `|d| < 2` → `BD83(t)` (reset `+0x2D` to R008, `3431` per player, and
  when BD03 says t is stronger, 2 × `include(rand(6))`); `|d| = 2` → `BF6B(flag, t)` — flag 0 for
  the team ahead (3 × exclude(rand(6))), 1 behind (3 × include); `|d| > 2` → `C0DF(t)` ahead (once:
  5 × exclude(rand(5)) + element 6) or `C01A(t)` behind (once: 5 × include(rand(5)) + element 6,
  then BEC7/230C re-place the back four when the player at squad word +0x10 is not at position 12
  or 13). The rand RESULT is the element number. High confidence.
- **The foul path `D5C1` never runs in a friendly** (static; the E010 runs all have `9A3D = 0`).
  `9A3D` = "fixture+2 ≠ 1" (A4A1); when set and no goal, `D5C1` draws `r = rand(10)+1`, maps side
  1's slot to r and side 0's to `DS:0xA90[r]` (= 13−r, both +0668[side]), returns at either
  unavailable check BEFORE the `06FA` coin, then `278A(own,3) < 278A(other,10)` and
  `26D7(own,4)`/chance-20, hardness draws, and `7EEF` — bookings, injuries and the walk-off that
  steps the second seed `DS:8336` — are beyond this finding's scope (Q012). Medium-high confidence
  for the prefix (R9, listing), the rest only traced.
- **The second seed `DS:8336` never moves during a quick result** (both). Only `0791:94C9` steps
  it, called only by `94E8` (speaker noise), reached only from `7881` (walk-off) and `9564`
  (watched) — neither runs in a quick result. All ten records' `8336` at full time equal their
  half-time value. High confidence (calls.tsv; F004).
- **The half-time wait and its two Enters consume no RNG** (both, corroborated in F004's terms).
  `9955` quick mode only stops the clock; the wait is `ED8A` inside `9A32`; the only rand caller
  reachable from the menu is `1771:3EF8` (the tactics submenu), not taken. The model starts from
  the half-time savestate and reproduces ten records' full halves exactly, so nothing between the
  stall and `D733(46)` drew. One exception the closure missed before T24 round 2: `000E:045D`, the
  crowd animation (1000–1500 draws per call), runs from the key waits `04F5`/`0572`; it cannot run
  inside a quick half (one call exceeds a tenth of the half's draws and the pause seeds are
  stable), but any model of the menu/attract screens must treat it as an RNG consumer. High
  confidence.

## Method

Static first (U32): every rule above was read from the disassembled listing
(`static/goal-exe/code/`, addresses SEGMENT:OFFSET) and cross-checked against the decompiled view;
`calls.tsv` closed the RNG-consumer set (every caller of `214B:0688/06B1/06D0/06FA` and `94C9`).
The model `runtime/model/quick_engine.py` encodes the rules and cites the listing line per
constant. What static analysis could not answer: whether the decode was complete and right — the
listing gives necessary, not sufficient, evidence for the exact draw sequence. That was settled
behaviourally, without further DOSBox runs, by emulating the ORIGINAL BINARY with Unicorn
(`experiments/E010-q010-quick-engine/emu_full_loop.py`): the whole `97D0` loop from r0010's
published half-time savestate (only the BIOS key check stubbed "no key", interrupts swallowed, and
the never-reached 000E wait family skipped) reproduces the record's own trajectory exactly — 3617
draws, final seed 0x543a, score [0,1] — which is both the corroboration of the decoded rules and
the ground truth that found the model's one missing rule (65FE's form swing, above): the staged
goal-pause savestate of round 2 was taken mid-65FE, during the goal whistle, so it — like the
pre-fix model — lacked the swing's writes, and the emulations from it followed the model's path
while the full loop from half time followed the original's. The ten E010 records (T23) then check
the model end-to-end: `check_model.py` reports `match: 10/10`, each record's final score,
second-half goals (player word and minute) and both seed words.

## Scope and limits

The watched engine `9564`, ratings (Q011), keeping and penalties and the foul path beyond the
`278A` compare (Q012) are out of scope. Extra time and the second half's kick-off writes were
taken from the listing only where the model needs them; the model refuses extra time
(`ExtraTimeNotModelled`) and the `7EEF` branch (`FoulPathNotModelled`) rather than guess. The
Unicorn harness's interventions (key stub, swallowed interrupts) are justified in its header; the
wait-family skip log stayed empty through the emulated half.
