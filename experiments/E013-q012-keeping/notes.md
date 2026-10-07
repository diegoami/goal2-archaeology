# E013 (T27, Q012): where keeping is read, and where penalties are read — the static map

Static first (rule 22): every claim below is read from `static/goal-exe/code/` (the named view
first), with `calls.tsv` closing the caller sets. No run was needed to answer any of them; the
E013 runs corroborate (see the finding F015 and `runs/E013`).

## 1. No engine reads a stored skill; the derivation is `1771:3A06`, divisor 32

- The player screen's bar painter `1771:3947` (F008) computes each skill as
  `DS:6DCD[12·(+5) + c] · ((+4)+1) div 256` with `c = DS:6D25[12·(+7) + i]`
  (seg_1771_05.asm:3969-39C4; `div 256` at 39C1, `mov cx, 0x100`).
- `1771:3A06(player_word, element)` (seg_1771_05.asm:1032-3A7F) is the same derivation with the
  same three record bytes (+4 at 3A23, +7 at 3A37, +5 at 3A51) and the same two tables
  (`DS:6D25` at 3A46, `DS:6DCD` at 3A60), but divides by **32** (`3A71-3A74`:
  `mov cx, 0x20` / `div cx`). It returns the skill `element` (1..12) of a player as the match
  engine weighs it: a goalkeeper's keeping (+7 = 0, class column 1, profile rows give 23..26)
  is `26·((+4)+1) div 32` = 147 at the new game's +4 = 180.
- callers (calls.tsv): `1771:3A06` is called by exactly one routine, `0791:278A`. `1771:3947`
  is called by exactly one routine, `1771:42BC` (the player screen). So the twelve-skill
  derivation exists twice — screen (÷256) and engine (÷32) — and nowhere else; there is no
  stored keeping or penalties byte anywhere (F008's alternative "the engine may use +7 = 0 as a
  guard and skip the derivation" is refuted: the guard does not exist, the derivation runs).

## 2. `0791:278A` is the engines' only skill reader

`0791:278A(pitch_record_far_ptr, element)` (seg_0791_04.asm:846-2879) computes, for the player
whose word the pitch record holds at +0xD (2793-27A0):

1. base = form `+0xC` + 1 while `+0xC < 0x20`, else 0 (27AB-27C2) — the form byte is read
   with `cwde` at 27B9, so a value 0x80..0xFF is SIGNED (negative); a non-negative Python read
   of the byte is wrong (F015, R5);
2. element ≥ 0xC adds 0x20 to the base — the penalties bonus (27C5-27CF); any other element
   adds the signed energy `+0xE` instead (27D1-27D9, also sign-extended at 27D8);
3. skill = `1771:3A06(player, element)` (27E6);
4. the pitch record's byte +0x13, when set, halves the skill (27F1-2802);
5. value = base·skill div 256 + skill div 4 (2805-281E) — the multiply is UNSIGNED
   (`mul word ptr [bp - 6]` at 2814), the product's high word is DISCARDED (`xor dx, dx` at
   2817), and the divide is UNSIGNED (`mov cx, 0x100` / `div cx` at 2819-281C): the value is
   `((base·skill) & 0xFFFF) div 256 + skill div 4`, the low word in two's complement for a
   negative base; the `skill div 4` quarter at 2808-280D is also unsigned. There is no IDIV
   and no sign extension of the product;
6. **the keeper extra** is TABLE-CONTROLLED, not element-1-only. The first gate at 2826 is
   `cmp byte ptr [di + 0x769], 0 / jne 2843`: a non-zero byte for the element jumps directly
   to the extra-term branch, adding pitch +0x11 WITHOUT testing element 1 or event
   membership. The data image at DS:0x769 has 0x769[2] = 0x01, 0x769[4] = 0x01, 0x769[12] =
   0x01, so elements 2, 4 and 12 carry the extra unconditionally. The 282D-284C fallback
   (`cmp word ptr [bp + 0xa], 1` AND `23E4:08DF` membership of 0x18 in `CS:276A`) only fires
   when the table byte is zero — that path is element 1 and the goal-mouth event code;
7. an outfield slot (pitch +6 < 0xC) with `DS:80FC` set adds value/16 (284F-286A).

`0791:287C(pitch, element)` = `rand(278A div 32 + 1)` (2882-2897) — the contest draw helper.

Its callers (calls.tsv, with the element each site passes — immediates from the listing, table
indices from the data image `DS:0769..0x817`):

| caller | element | what it is |
| --- | --- | --- |
| `0791:1FDD` (20A0/20AD) | its own param [bp+6] | the best-player-by-skill scan (slots 1..11) |
| `0791:34C1` (368A/36DA) | `DS:0x779[8327]` | the ball-event dispatcher's own contest (events 8/0xE give 1) |
| `0791:3B15` (3B32) | 2 (kicking) | kick evaluation |
| `0791:3EF8` (3F48) | `DS:0x796[di]` | set-piece taker evaluation |
| `0791:47C5` (494A-499A) | 8 and immediates | the pass/cross path |
| `0791:5474` (549E/54EF) | `DS:0x7F6[8303]`, `DS:0x7F4[8303]` (3/4) | the foul duel (tackling/heading) |
| `0791:5B36` (5BC4/5BD8/5C06/5C1A) | 10, **1**, 4, **1** | the save duel (below) |
| `0791:690C` (6968) | `DS:0x80C[8327]` (≤ 4) | the shot/goal-mouth contest (codes 3/4 give 12) |
| `0791:9ED3` (9F6A/9F9F) | **0xC (penalties)** | the shoot-out taker ranking (A10A only) |
| `0791:D5C1` (DC7E area) | 3 and 10 | the quick-engine foul prefix |

So the engines read the skill rows: keeping (1), kicking (2), tackling (3), heading (4),
passing's neighbours (8/9/10/11 by the `0x7FE..0x80C` event tables), and penalties (12) — each
through the same `3A06` derivation; there is no special-cased keeping arithmetic anywhere else.

## 3. Keeping: read in the watched engine's save duel; the quick engine never reads it

- The save event ("saved by X", commentary template 29) is written by `0791:5A8E`
  (seg_0791_04.c named view 1003-1022: `f_0791_5A33(param_1, 0x1d)`), and `5A8E` is exactly the
  branch target of the duel inside `0791:5B36` (seg_0791_10.asm:5BC4-5C3E, named
  seg_0791_05.c:104-137): with the goal-mouth flag `DS:8303` clear,
  `rand(278A(holder 830B, 4))` (5BC4) against `rand(278A(challenger, 1) + (tackle? 0 : 1))`
  (5BD8) — the challenger's **keeping** against the holder's heading; with `8303` set it is
  `rand(278A(830B, 10))` (5C06) against `rand(2·278A(challenger, 1))` (5C1A). The keeper is not
  chosen by a record byte here: he is whatever pitch record reaches the duel — the goalkeeper
  route is the keeper special of `9564` (below), which hands the side's slot-1 record to
  `8AE9`, whose state machine brings him to the duel.
- The keeper special `0791:9636-9666` (F013's gate) reads **no player-record byte at all**: it
  runs when the event code `DS:8327` is a member of `CS:9544` = {0x1E} (9626-9634), takes the
  side's slot-1 pitch record (`0668[side] + 1`, 960E-9620), compares that record's pitch byte
  +0 (x) with the ball's `DS:82F6` (9646-964D) and calls `2CEC`/`2E36`/`8AE9` (update_player).
  F013's candidate — "the class-1 reading of `DS:6D25[12·(+7)+1]` or a +7 = 0 guard" — is
  therefore wrong in both forms: the keeping read happens later, in `5B36` via `278A(·, 1)`,
  and "goalkeeper" is a slot property (slot 1 of the side), not a record-byte test.
- Keeping is read of ANY player who reaches the duel — not gated by position: an outfield
  challenger's element-1 value is his own derived keeping (class column 7, 11 or 12 for the
  outfield positions, class table rows 1..13; a position-2 defender with profile 1 keeps at
  19·181 div 32 = 107 against a goalkeeper's 147 — up to ~73% at the same +4). "Only the
  keeper keeps" is therefore FALSE at the value level: the keeper is the strongest keeper by
  class, but the read itself is open to any challenger, and the keeper's edge is one of
  degree (class 1 vs 7/11/12), not a gate.
- The quick engine (`D733` → `1771:0BC4` → `B19D`) reads NO derived skill: its `gk` line sum is
  the eleven `377E(w)` strengths (ability +4, form, energy) routed by the position table
  `DS:0D4E[+6]` (F012), and no caller under `D733` reaches `278A`/`3A06` (calls.tsv). So in a
  quick result the keeper line holds plain ability, and "keeping" as a skill is never read.

## 4. Penalties: element 12 with a +0x20 base bonus; ranked only in `A10A`

- `278A`'s base adds 0x20 for element ≥ 0xC (27C5-27CF): a penalty contest is the penalties
  skill **plus 32** before the product. The 2826 table-controlled gate (above) ALSO fires
  for element 12 (DS:0x769[12] = 1), so penalties contests add pitch +0x11 on top of the
  +0x20 base bonus.
- `0791:9ED3` (seg_0791_16.asm:9ED3-A003) fills the shoot-out taker array
  `[bp-0x1A + 12·team + i]` with the side's pitch slots 1..11 in order (9EE3-9F11, the loop
  at 9EE3 increments to 0xB) and then sorts entries 1..11 (THE KEEPER IS INCLUDED — the
  outer index initialises to 1 at 9F1B, the inner to outer+1 at 9F25-9F31, and the
  compare/exchange at 9F39-9FE9 has the keeper at slot 1 in its scope) **downward by
  `278A(pitch, 0xC)`** (9F39-9FA5: both calls, `cmp/jbe` exchange sort via `214B:007B`).
  The unmanaged side's five takers are its best penalty takers by derived penalties skill.
  The keeper is on the taker list; the keeper's penalties skill is read the same way as any
  other player's. `9ED3` is called only from `A10A` (calls.tsv).
- The managed side picks its takers by hand: `0791:9B93` (seg_0791_16.asm:9B93-9ED0) shows the
  squad's player cards — it calls the player screen `1771:42BC` itself (9C5C) — and the
  manager's choices fill the same array (the loop at 9C4E-9CA2).
- The kick: `0791:A006` (seg_0791_16.asm:976-A0F5) sets `DS:830B` to the taker's slot and calls
  `6BF1(0xA, taker)` (A05B-A065), which starts a ball phase (`8302 = 1`, 6C0A) and branches on
  the restart type 0xA for the run-up sprite (6C46-6C64); the kick then plays out through the
  watched engine (`9564` loops at A0D8/A0E8) — the same `5B36`/`690C` contests decide it.
  `690C`'s element is `DS:0x80C[DS:8327]`, which is 12 at event codes 3 and 4: the shoot-out
  kick and the match's own penalty events read the taker's penalties skill with the +0x20
  bonus there. In the duel itself, `5B36`'s `DS:8324`-set branch — `A006` sets `DS:8324` = 1
  before its `9564` loops (seg_0791_16.asm:A0CE-A0D3), so it is the shoot-out kick's frame —
  rates the ball holder (the taker) by `278A(830B, DS:0x800[(8327 == 4)])` = element 12,
  halved (named seg_0791_05.c:57-63). Penalties is read in normal play only through `690C`'s
  table column; every immediate element-12 caller is inside `A10A`.
- `A10A` itself (seg_0791_16.asm:A10A-A25F) is the round bookkeeping: five kicks per side
  (counters `[bp-0x1C]`, A156-A166), the managed/unmanaged taker pick per side (A172-A187:
  `1771:0B77` managed?), `A006` per kick (A1EB), the win test on the score bytes `DS:9B3C/9B3D`
  against kicks taken (A1B9-A1E9), sudden death after five (A204-A228), and the only print of
  `penalty shoot out` (`DS:1078`, pstr at A0F8) via `214B:04F8` (A12D-A132).
- Reachability: `A10A` is called only by `0791:F098` (calls.tsv, F179), and only when the
  fixture record's byte +3 = 2 (a draw) **and** `DS:7C36` ≠ 0 (F0F6-F10C); `DS:7C36` is set at
  match start (`0791:A417`, also `0791:1394`) to "fixture byte +2 is a member of the set
  `DS:693A` = {0x10}". So only a decider fixture (byte +2 = 0x10, a cup tie) drawn at full
  time reaches the shoot-out; a drawn friendly ends at FULL TIME (E012-r0002/r0003: 2-0 and
  1-1-class outcomes, no template 61; E011-r0001 drew 1-1 and printed no shoot-out).

## 5. What the I3 edits test (the corroboration arms)

- The edit is the keeper's +4 (F008's scale of all twelve skills): keeping scales linearly
  with (+4)+1 (`3A2C`), +4 = 0x00 floors a goalkeeper's keeping at `26·1 div 32` = 0 — every
  save duel he enters draws rand(1..2) against the holder's rand(element 10) — and +4 = 0xFF
  lifts it by (0x100)/(old+1).
- An outfield player's +4 feeds the SAME derivation for every element (`3A06` is element-
  parametric), so his duels shift too — the backlog's "editing an outfield player's keeping
  changes no event count" cannot be asked of a byte that does not exist; the question the runs
  answer is whether his +4 changes any watched event count (static answer: yes, every contest
  he enters draws differently).
- The shoot-out arm needs a fixture with byte +2 = 0x10; the E006/E012 release start states
  are friendlies, whose drawn matches end at full time (F0F6's gate) — see the run records for
  what was done about it.
