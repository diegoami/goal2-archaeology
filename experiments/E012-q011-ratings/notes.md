# E012 q011-ratings — reading notes (performance ratings and the man of the match)

Static map of every writer of the player-record performance field (+0x12), the commentary delta
table `DS:0x720`, the readers, and the man-of-the-match selection. Addresses are `segment:offset`;
listings are `static/goal-exe/code/seg_0791_NN.asm` etc. (the named view `static/goal-exe/named/`
was read first, then the raw listings). Data tables are DS offsets read from
`static/goal-exe/data/ds_2581_01.hex` and cross-checked against a savestate (`scratch/`, E011's
published release assets — identical). Status: append-only, commit per batch.

## 1. The field and its encodings (recap, F007/F008)

The performance is the word at `+0x12` of the 20-byte player record at `[DS:A91B] + 0x14*word`
(F007/F008). Three encodings, all taken from the listing, never the displayed string:

- `0x7FFF` = blank (never rated): written at new game (`1771:97C0`, make_player, §4) and by the
  silent quick result (`0791:D5A9`, §4).
- raw word: the rating as a plain 16-bit value (a starter begins at `0x37` = 55, §4).
- `+10000` (`0x2710`) flag: a substitute's rating is stored as `10000 + raw` (written whole as
  `0x2747` = 10055, `0791:C6FA`, §4). Readers decode: `> 5000` (signed, `0x1388`) → subtract
  `0x2710` (`1771:385C`, `0791:CB43`). There is no instruction anywhere that adds `0x2710` to the
  field (grep `27 10` over the whole listing: only the two `sub` sites); the flag only ever enters
  through the `0x2747` store.

`1771:3827` `performance_text` (seg_1771_05.asm:833-900, F008): blank when `0x7FFF` (`384B`);
else `v := word`, `if v > 0x1388 (jle, signed) then v -= 0x2710` (`3855`-`385C`), `v -= 0x37`
(`3861`); the displayed 1..9 bucket is then the first threshold `v` is below: `< -0x32` → 1,
`< 0` → 2, `< 0x32` → 3, `< 0x64` → 4, `< 0x96` → 5, `< 0xC8` → 6, `< 0x12C` → 7, `< 0x190` → 8,
else 9 (`3865`-`38CF`, every compare signed `jge`). So the initial `0x37` shows bucket 3 (middle).

## 2. The delta mechanism: every commentary line rates its named player

`0791:1EB5` (seg_0791_03.asm:991-1063) is the common tail of every commentary emitter. It is
called with the event frame laid out on the caller's stack — word at `+4` the template id
(the ring id), `+6` player-2's side-relative slot (0 = none), `+8` player-1's slot, `+0xA` the
team byte — and does two things, **in this order**:

1. `call 1E53` (`1EBC`): **apply the rating delta** — `0791:1E53` (seg_0791_03.asm:952-989) reads
   the frame (bp at its entry still points at 1EB5's frame), computes the pitch record
   `0x80E8 + 0x16*(0668[team] + slot)` (`1E5C`-`1E7B`), takes its `+0xD` word as the player
   (`1E84`), forms the record pointer `[A91B] + 0x14*player` (`1E88`-`1E91`), reads the delta
   `al := s8(DS:0x720[frame+4])` (`1E9C`-`1EA3`, `8A 85 20 07`) and executes
   `add word es:[di+0x12], ax` (`1EAB`, `26 01 45 12`): **the s8 byte at `DS:0x720[template]`
   is added, 16-bit with wraparound, to the named player's performance**.
2. `call 1D4A` (`1ECD`): write the line into the commentary ring at `DS:7C38 + 6*n`
   (seg_0791_03.asm:843-950, E004's reader): byte `+0` the template, `+1` player 1's record word
   (the squad word at the frame's `+8` slot, `1DCA`-`1DDB`), `+3` player 2 (`1DEA`-`1E01`),
   `+5` the team (`1E10`-`1E16`). `1D4A` can refuse: `1C78` (seg_0791_03.asm:760-847) returns 0
   when the new line is identical to the newest ring line (same template, p1, p2, team,
   `1D01`-`1D3A`) — then the record is not written and the counter does not advance
   (`1D54`-`1D63`), **but the delta from step 1 has already been applied**.

So the rule is: **every ring line applies `s8(DS:0x720[template])` to the record word the line
names as player 1** (a line with no player names — slot ≤ 0 — writes p1 = 0 into the ring
(`1DC4`-`1DE6`) while the delta still lands on the pitch record `0668[team] + 0`, i.e. the dummy
pitch record 0 for team 1 (0668 = `[0x0B, 0x00]`, team 0 plays pitch 12..22, team 1 plays 1..11;
`2BB1`/`2974` map a pitch record to its side slot, seg_0791_05.asm:233-258, seg_0791_04.asm:1066-
1102) — a garbage player word beyond the array, harmless to any real rating).

The emitters (all reach 1EB5 through 2AA3/2AD4/2B0F/2B28, seg_0791_05.asm:80-235):

- `2AA3(id)`: line about the ball holder `DS:830B` (p1 = its slot, delta player), p2 = `830C`'s
  slot, team = `2996()` (the holder's side).
- `2AD4(id)`: the mirror — p1/delta player = `830C`'s player, p2 = the holder, team = `830C`'s side.
- `2B0F(id)`: no players (p1 = p2 = 0, team 1) — the flavour lines (clock, full time…).
- `2B28(id, pitch record)`: p1 = the record's player (delta player), team = its side.
- direct `1EB5` callers: `0791:998C` (pre-match, id 0x3B "wins the toss", seg_0791_16.asm:99CF-99E2)
  and `0791:C5DC` (the substitution, id 0, seg_0791_20.asm C6AE-C6BA — see §4).

Emitters by id (the constant pushed at each call site; `tab` = a byte table at DS:0x786/0x788/
0x78A/0x78C/0x794/0x80A chosen by a coin or a param): `384C` (384C: two coin-indexed ids from
0x786 `[2,1]` and 0x788 `[7,6]`, and constants 3, 0xA, 9, 8; seg_0791_06.asm:855-916),
`3B15` (0x78A `[5,4]`), `3B9E` (3), `3C3F` (param `[bp+0xC]`), `3DF6` (0x794 `[15,16]`),
`3EF8` (0x17, 0x18), `3FAD` (0x16, 0x15), `539F` (0xE, 0xE, 0x21), `5565` (2B28 0x41 and 0x0B,
2AA3 0x0C), `56D9` (2B0F 0x42), `593B` (param `[bp+6]`), `5A33` (param `[bp+6]`), `5B36`
(2B28 `[bp-7]` ∈ {0x0B, 0x41, 0x0D}, 2AA3 0x0C, 2AA3 0x1C), `5EAB` (0x20), `5F06` (0x20 or
0x80A `[31,33,10,11,4,12,12,0]`), `5F8A` (2B28 0x19, 0x23, 0x22), `6443` (0x27/0x26 — the goal),
`6755` (0x28, 0x29), `67B6` (2B28 0x24, 0x25; 2AA3 param-dependent), `69BD` (0x31), `6DEA`
(param `[bp+4]`), `6E11` (0x2B), `6F01` (0x38), `6FEE` (0x2A), `70F6` (0x2C), `71E8` (0x2E),
`72F2` (0x3C, 0x2F), `74C2` (0x30), `798D` (2AD4 0x32), `7B77` (2AD4 0x33), `7D56` (2B28 0x34),
`8206` (0x37, 2AD4 0x35), `82EB` (2AD4 0x36), `8AE9` (2AD4 0x19), `970C` (2B0F 0x3F, 0x40),
`998C` (1EB5 0x3B), `9B0C` (2B0F 0x3E), `A10A` (2B0F 0x3D), `C5DC` (1EB5 0).

Both engines reach this mechanism: the watched engine's goal is `690C → 67B6 → 6443` (6443 also
called by the quick engine's `D733`), and the watched event tree (`9564 → 6188 → 5B36/5F8A`,
`8AE9 → 57AC → 5565`, `83A2 → 690C`) emits through the same 2AA3 family — so the delta rule is
engine-independent; which ids appear differs by engine (the quick engine's second half in E010
showed goals 0x26/0x27 and substitutions only; a watched half shows the full flavour set, §6).

## 3. The delta table `DS:0x720`

67 entries (0x720..0x762), indexed by the template id 0..66 — the id is the same number that
indexes the template strings at `DS:00BE + 0x15*t` (E004's reader; the largest id any emitter
pushes is 0x42 = 66, `56D9`/`970C`). Read from `static/goal-exe/data/ds_2581_01.hex` rows
0x720-0x762 and cross-checked byte-for-byte against the runtime DS of the E011 half-time
savestates (identical; the table is never written at runtime):

```
id  0     1    2    3   4   5    6   7    8   9   10   11   12  13  14  15  16..20  21  22  23
    +0   -10  -10   0   0  -1   0  -10  +10 +10 +10  -10 +20  0  +20 +20  0       +2 +16 +2
id 24  25   26  27  28  29   30   31..34  35  36  37  38   39   40   41   42..46  47  48  49
   +16 +1   +8  +8  +1 +20  +10   0      +1  0   0  +40  -50  -10  -10  0       -20  0   0
id 50   51    52  53  54   55..64  65    66
   -20 -100   0   0  -2    0     -10    0
```

With the template strings (ds_2581_01.hex, E004's table): 38 `**** GOAL **** by` +40, 39
`** OWN GOAL ** by` −50, 50 `BOOKED` −20, 51 `SENT OFF` −100, 54 `is OFFSIDE` −2, 0 `on for`
(substitution) +0, 65 `challenge by` −10, 11 `tackle by` −10, 12 `dodged by` +20, 14 `wins the
ball` +20, 8/9/10 `good/long/high ball` +10, 25 `on the ball` +1, 34 `intercepts` +4, 47
`to take penalty` −20, 66 `** LINESMAN FLAGS **` 0, 63/64 full/half time 0 (66 and the two
time lines are 2B0F flavour lines, p1 = 0; an earlier draft of this note wrote 66 as −10 —
the byte at `DS:0x720+66` is 0, and 65 `challenge by` is the −10).

## 4. Every writer of player +0x12 (word writes; all others in the listing are the pitch
record's own byte field at pitch+0x12, F013)

1. `0791:F2C7` (in `F1F6 run_match`, seg_0791_23.asm:1105-1122): **pre-match**, for both teams'
   squad slots 1..11 with a player: `mov word es:[di+0x12], 0x37` — the starting XI begins at 55.
   (The same loop first copies each player's `+0xC` form to `DS:9B07 + 0x14*side + slot`, restored
   by `CB7D` after the match, F2A4.) `F1F6` then runs the match (`F098`) and, after it, calls
   `CAB0` (`F2F8`) — the MoM selection, §5.
2. `0791:1EAB` (in `1E53`, §2): `add word es:[di+0x12], ax` — the commentary delta, per line.
 3. `0791:56CB` (in `5565`, seg_0791_09.asm:780-793): `add word es:[di+0x12], 0xA` — a +10 that
    `5565` writes **directly, with no ring line**, to the event's pitch-record player when
    `DS:8303` is set (`56A6` `cmp byte [0x8303],0; jne 56B5`); when clear the branch emits the
    2AA3(0x0C) "dodged by" line instead (`56AD`). `5565`'s 8303-set invocation first emits the
    `2B28(0x41)` "challenge by" line (`5653`), then runs a chain of checks (`5474` at `5676`,
    `5513` at `567E`, `4151` at `5685`, `45d(8303B)` at `5692`, `4d3f` at `56A3`); every bail
    that emits does so as the line **immediately after** the 0x41 line: `5474`/`5513` →
    `539F`, whose 8303-set path emits the pair 2AA3(0x0E) then 2AA3(0x21) (`5465`/`5468`) or
    `408E`'s 0x16/0x17/0x18 (`5405`-`5416`); `5513`'s coin → `8206`'s substitution lines
    0x35-0x37; `4151` → `3FAD(9)`'s 2AA3(0x15) (`3F82`). The ONE silent bail is `45d(8303B)`
    at `5692`-`5697`: `045D` (seg_0791_01.asm:511) returns 1 when its argument — the HOLDER's
    pitch slot, `DS:830B` — is 1 or 12 (the two keepers' slots: 0668 = [0x0B, 0x00], team 1
    plays pitch 1..11, team 0 plays 12..22, so pitch 1/12 is either side's slot 1), and the
    `jne 56D0` at `5697` skips `56CB` without emitting anything. `4d3f` at `56A3` is NOT a
    second bail: it checks the CHALLENGER's record byte `+6` (`4D4F`), but its return value is
    never tested — the next branch is `56A6`'s `cmp byte [0x8303],0` — so a goalkeeper
    challenger still gets the +10 (an earlier draft of this note claimed a challenger bail;
    review R1). So a 0x41 line whose follower is none of
    {0x0E, 0x21, 0x15, 0x16, 0x17, 0x18, 0x35, 0x36, 0x37} reached the `5692` test: it nets 0
    (the table's −10 plus the +10) **iff the duel's holder is not on a side's slot 1**, and
    keeps the plain −10 when he is. The holder is not named by the 0x41 line itself (`2B28`
    stores p2 = 0, `2B41`-`2B43`), but the log tracks him: the p1 of every 2AA3-only line
    and the p2 of every 2AD4-only line (the id sets, with call sites, in
    `runtime/model/ratings.py`'s HOLDER_P1/HOLDER_P2; 11, 25 and 0 are excluded — each is
    emitted by both a holder-carrying and a non-holder emitter). **This fired in E012-r0001's
    first half** (its slot 3 read 0x8C where the plain table gives 0x82):
    positions 294/295 are two adjacent 0x41 lines — 123's (preceded by the 2AA3(0x0A) line
    `(10, 364, 378, 1)` naming the holder 364 — side 1's slot 3, not a keeper — and followed by
    124's 0x41, a new invocation: completed, +10) and 124's (followed by 539F's 0x0E/0x21 pair
    naming 124: bailed, the plain −10). When the follower does not visibly bail and the holder
    cannot be established from the log — or the 0x41 is the last line of a batch, so a bail
    follower could still arrive — the outcome is not inferable: the predictor records the case
    as UNDECIDABLE instead of silently returning an exact rating (T26 rework R1); no E012
    record has such a case. `0791:5B36` can also emit a 0x41 line with 8303 set
    (`5B88`-`5B93`) and never adds the +10; its follow-ups (`5A8E`'s `5A33` lines, `5C44`'s
    `8206`) are the rule's one remaining ambiguity — no 5B36-emitted 0x41 appeared in any
    analysed half.
4. `0791:C6FA` (in `C5DC refresh_pitch_slot`, seg_0791_20.asm:498-502): **the incoming
   substitute** gets `mov word es:[di+0x12], 0x2747` (10000 + 55) — reached from both engines'
   substitution paths (`8062 → C88D → C5DC` quick, the watched event tree's `5513/8206`;
   F012), and C5DC also emits the substitution line through `1EB5` with id 0 (delta +0,
   C6AE-C6BA), which is why the sub line itself moves no rating.
5. `0791:D5A9` (in `D47E quick_result_silent`, seg_0791_21.asm:600-616): both sides' slots 1..11
   := `0x7FFF` — a CPU-vs-CPU result played without display has no ratings at all.
6. `1771:97C0` (in make_player, seg_1771_13.asm:1198): `0x7FFF` at new game (F007).

## 5. The readers and the man of the match

- `1771:3827` `performance_text` — the display, §1.
- `1771:1289` → `1301`-`1320` (seg_1771_02.asm:871-940): a player-value calculation reads the
  word, `−0x37`, then `if > 0x1388: −0x2710`, `+0x64` (note the different decode order — the
  flag test happens on the already-shifted value; for the raw and flagged encodings both yield
  `raw − 0x37 + 100`), feeding `3A82` — the value screens, out of scope here.
- `214B:19F4` (seg_214B_03.asm:769-790): tests bit 0 of the word at a record's `+0x12` and,
  when set, stores the record's word `+0` to `DS:A965` (else 0). Every encoding the writers
  produce (`0x37`, `0x2747`, `0x7FFF`) is odd, and all but three deltas (ids 5, 25, 35: −1/+1/+1)
  are even, so bit 0 acts as a persistent "rated" marker for this test. Caller `214B:1A5F`.
- `0791:81A2` (in `8062`, seg_0791_13.asm:1028-1035): the quick engine's substitution scan reads
  the word and compares signed `+0x12 < 0x5A − 831B` (F012's sub-readiness rule).
- `0791:CAB0` — **the man of the match** (seg_0791_20.asm:918-975, decompiled
  seg_0791_09.c:596-651): for side 0 then side 1 (`local_3`, team = `DS:9B34[side]`), squad slot
  `local_5` = 1..0x14: slots 1..11 always considered; slots 12..20 only when the player's status
  byte bit 3 (`+0x10`, `214B:0C57` — the substituted-off marker c5dc sets, F012) is set
  (`CB1B`-`CB27`); skip `0x7FFF` (`CB2A`); `v := word`, `if v > 5000 (signed): v -= 0x2710`
  (`CB2E`-`CB43`); `if best < v (strict, best starts at 1)`: `DS:7C3A := the squad word`,
  `best := v` (`CB4C`-`CB60`). Ties keep the first player in scan order (side 0, lower slot).
  `7C3A` is cleared per match by `A4A1 match_setup` (seg_0791_16.asm:441, `DS:7C3A = 0`) and the
  only caller of `CAB0` is `F1F6` at `F2F8` — after the match, before the summary.
- The consumer: `0791:0106 draw_match_summary` (seg_0791_01.c:80-105) draws the name from
  `DS:7C3A` on the summary board (screen 0x14C8, the " MAN OF THE MATCH " row, string
  2581:14D6) **only when `DS:9A3F` is clear** — 9A3F is set together with 9A3E (quick mode) by
  the key poll `9372` (seg_0791_15.asm:9356), so a quick result shows no MoM; a watched match
  does. The MoM is therefore `CAB0`'s max-scan over both sides' rated players.

## 6. The rule, and the instrumented checks that proved it

**Rule (the predictor):** start every squad slot 1..11 of both teams at `0x37`, every other
player at `0x7FFF`; for every ring line `(template t, p1, p2, team)` in order: `t == 0` →
the substitution's incoming player (`p1`) := `0x2747`, the squad words swapping slots;
`t ∈ {51, 52}` (sent off / injured) → `p1` leaves the pitch and his side's slots 1..11 are
re-sorted by `230C`'s pairwise compare-and-swap — key 14 for the unavailable, else the
player's key (the predictor keys him by his starting slot), equal keys never swap but every
strictly smaller key does, so the removed can reverse their original relative order
(`0791:7B77`/`0791:7D56` → `C48D` → `C503` → `230C`; a booking, 50, re-orders nothing); `t == 65` → the challenge nets 0
(the table's −10 plus 56CB's +10, §4.3) when the FOLLOWING line's template is none of
{0x0E, 0x21, 0x15, 0x16, 0x17, 0x18, 0x35, 0x36, 0x37} AND the duel's holder (tracked from
the 2AA3/2AD4 lines, or the line's p2 when it carries one) is not on a side's slot 1 — the
`045D(830B)` silent bail keeps the plain −10; when the follower does not visibly bail but
the holder cannot be established (or the 0x41 is last in its batch), the case is UNDECIDABLE
and reported, never silently matched; else `p1 != 0` →
`rating[p1] := (rating[p1] + s8(DS:0x720[t])) mod 0x10000`. The MoM is `CAB0`'s scan over the
final words (§5). Ratings are read at half time and full time by applying the lines up to that
point.

Check 1 (the second halves, emulated): the Unicorn harness (`runtime/emul/watched.py`) runs
the ORIGINAL binary's own second half from each E011 half-time savestate (the published
release assets, fetched into `scratch/` and manifest-verified), instrumented (a scratch
script, not committed) to log every `1E53` call — (id, team, slot, player, delta) — every
`1D4A` ENTRY, the line only at `0791:1D66` (the accepted-write path; a refused call jumps
`1D61 → 1D63 → 1E4A` and never reaches it — T26 rework R3: the first instrumentation logged
a "ring line" at `1D4A`'s entry, which a refused duplicate also reaches, so it could not
detect a refusal), the `56CB`/`C6FA` writers, and the final words. Over both E011 halves
(identical second halves, r0001/r0002): 550 `1E53` calls, 550 `1D4A` entries, **507
accepted ring lines — 43 dedup refusals measured** (7.8%; every refused invocation a repeat
of the immediately preceding line, all of them template-6 "makes a run" pairs — `1C78`
refuses only a line identical in template/p1/p2/team to the ring's comparison line — and
`DS:0x720[6]` is 0, so no rating moved: the refused delta is still applied by `1E53`, but
it is 0), **no `56CB` +10**, 2 substitutions (`0x2747` + deltas), goals 0x26/0x27 absent
(both goals fell in the first half). Per player, the sum of `s8(0x720[template])` over the
accepted lines naming him equals the sum of the `1E53` deltas the binary applied, and the
end-to-end predictor (half-time words + second-half accepted lines → full-time words)
matches the emulated final words for **40/40 squad players of both teams, both halves**
(`mismatched: 0`). The check is not vacuous: the template histogram of a watched half
(50 "makes a run", 66 "on the ball", 57 "tackle by", 45 "wins the ball", 36 "intercepts",
3 "to take penalty"…) exercises 34 different deltas, and a first version with one mistyped
table entry mismatched 5 players per half (found and fixed before any predictor was
written; the table in §3 is the byte-exact one).

Check 2 (a first half, emulated): `emu_firsthalf.py` (this folder) runs the ORIGINAL
binary's own FIRST half from E011's published `watchstart` savestate (the captain-screen
state of the same deterministic match), entering at `998C` after applying F1F6's pre-match
loop by hand. 580 `1E53` calls, 580 `1D4A` entries, **523 accepted ring lines — 57 dedup
refusals measured (9.8%, every one a template-6 repeat, delta 0)**, **no 56CB, no C6FA**,
and the plain-table predictor replays the 523 accepted lines to its final words 40/40
(`emu-firsthalf-r0002.txt/.json`, committed; `emu-firsthalf-r0001.txt/.json` is the earlier
run with the entry-logging defect — its "580 ring lines / no dedup refusal" counts entries,
not writes, and is superseded). The emulated half is NOT the record's own first half: the
DOSBox run consumed main-seed draws in the team-screen key wait that the emulator's "no
key" thunk does not reproduce (with the refused entries no longer polluting the log, the
emulated accepted lines are identical to the record's ring lines for the first 123 lines —
r0001's "divergence at line 7" was the same instrumentation artifact — the true divergence
is at line 124), so it corroborates the mechanism, not the record's trajectory. For the
DOSBox records themselves the refusal count is not directly observable (a refused line
never enters the ring); the reads matching the written-line replay (Check 3) implies no
refused NONZERO delta occurred in them — a refused nonzero delta would leave the
predictor's word one delta short of the read.

Check 3 (the records): `check_ratings.py` over `runs/E012` — r0001 (the 56CB case, §4.3),
r0002/r0003 (two sendings-off and an injury: the XI re-sort; the half-time and full-time
squad reads are the re-sorted order, one slot out from the first removal without the
rule) — ends `match: 3/3`, every slot's word at both reads and the MoM equal to the read,
and no UNDECIDED challenge (§4.3) in any of them.

## 7. The runs (E012)

Watched matches from E010's published start states under E004's conditions
(`experiments/E012-q011-ratings/run.py`); each record carries the full line log, the half-time
and full-time read of every squad slot's `+0x12` both sides, and the MoM word `DS:7C3A` at full
time. `check_ratings.py` (same folder) reports the predictor's match over the records.
3 watched launches of the 6-run cap: r0001 from `e006-2100-r0005`; r0002/r0003 from
`e006-1001-r0002` (r0003 the replay, its ground truth identical to r0002's — deterministic).
