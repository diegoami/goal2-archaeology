# Q017 static notebook (Q017, T33)

## Method

Read the named view first: `seg_0791_05.c` (record_goal 6443, after_goal
65FE), `seg_0791_06.c` (7EEF foul dispatch, 798D booking, 7B77
sending-off, 7D56 injury, 7CC5 the live-form helper, B7A4D's card
dispatch), `seg_0791_09.c` (B7FA already covered by F019), `seg_1771_01.c`
(1771:13D0 the team aggregate) and `seg_1771_02.c` (157D draw_team_panel,
the only reader of `DS:9B5A`). Cross-checked against the raw `decompiled/`
and capstone `code/` listings where Ghidra's set-membership and Pascal
retf/ret are misleading. No DOSBox match was run.

The complete direct player `+0xC` reader/writer inventory is in
"Reader/writer inventory" below; it reconciles F019's result-rule
inventory (the `B364` writer and its callers) with this task's event
writers (the `7CC5` family and its callers) and the team aggregate.

`runtime/model/morale.py` extends F019 with the event types and the
team aggregate:

- `event_clamp(before, delta, persist)` — the `7CC5` operation on a
  single player byte: writes `clamp(s8(before) + delta, 1, 255)` to the
  player and, when `persist` is True, also writes
  `min(32, s8(new)) & 0xFF` to `DS:9B07[side*20+slot]`. Each named
  helper (`injure`, `send_off`, `scorer`, `team_reaction`) is a fixed
  pair of `delta, persist`.
- `injure(before)`, `send_off(before)` — `delta=-2, persist=True`.
- `scorer(before, morale_delta)`, `team_reaction(before, morale_delta)`
  — `delta=morale_delta`, `persist=True/False` respectively.
- `team_panel_morale(morales)` — `max(1, (6 + Σ_i min(32, s8(+0xC[i])))
  // 11)`, with the accumulator wrapping to 16-bit unsigned on every
  add (matching the `add word ptr [0x9B5A], ax` at
  `code/seg_1771_02.asm:1067`); the `div cx` at line 1093 is the
  16-bit unsigned divide. **There is no lower clamp on the per-starter
  contribution** — a -128 starter contributes -128, and `[128, 0, ...,
  0]` (one -128 signed byte, ten 0s) hand-traces to 5946
  (= (6 + (-128)) & 0xFFFF = 65414, 65414 // 11). The aggregate is
  recomputed at every panel render by `1771:13D0` and never persisted
  into the country record.

`experiments/E019-q017-events-morale/check_morale.py` replays every
probe by player word and by routine; `python3 -m unittest -v
tests.test_model_morale` runs 33 literal tests; `tests/test_check_morale`
runs 19 negative tests for the checker. The mutation sweep
(`mutations_morale.py`) shifts each of the 9 numeric constants by
`+1` and `-1`, deletes each of the 5 named helpers, and reruns the
unit suite in a fresh subprocess; **23/23 mutants killed**.

The probe file's `expected_*` and `got_*` fields are both
listing-derived (hand-traced from the listing bytes). The probe
generator (`probe_literal.py`) does NOT import `runtime.model.morale`;
the model's output is verified independently by the checker against
both listing-derived fields. Every case is identified by `player_word`
(the 16-bit squad slot the routine reads from `pitch[+0xD]`, the
player's record identity) — `side` and `slot` are the DS:9B07
persistence index, kept for completeness but not used as the
comparison key.

## Direct `+0xC` writers outside F019's result rule

Every direct `+0xC` store this listing establishes outside F019's
result rule is `0791:7CC5 adjust_player_form(pitch, flag, delta)`. The
assembly:

```
7CC5  push bp; mov bp, sp; sub sp, 4
       ; load pitch[+0xD] = player_word (seg_0791_13.asm:487-495)
       ; param_1 = [bp+6..8] (far ptr to pitch record)
       ; signed_byte byte ptr es:[di + 0xc]
       ; cwde  ax = sign_ext(al)
       ; add ax, word ptr [bp + 0xc]   ; param_3 HIGH word — the actual delta
       ; clamp to [1, 255] (calls 214B:2000 clamp_int(0xFF, 1, &ax))
       ; store low byte back to player +0xC
       ; if [bp + 0xa] (param_3 low byte) != 0:
       ;   ax = s8(new live); cdq:ax
       ;   push s8(new live); push 32
       ;   call 214B:0D1C min_longint(32, s8(new live))
       ;   DS:9B07[side*20 + min(32, ...)] := al
       ; retf 8                        ; 4 stack slots = pitch + delta_high + delta_low
```

Caller push convention (right-to-left on stack):

| Delta HIGH | Delta LOW (low byte = flag) | Caller | Effect on `+0xC` | DS:9B07 |
| --- | --- | --- | --- | --- |
| `s8(DS:0x7920[side])` (goal scorer, ±1) | `0x0001` or `0xff01` (flag = 1) | `0791:6443 record_goal` | `+0xC += ±1`, clamp [1, 255] | written (`min(32, s8(new))`) |
| `s8(DS:0x7920[side])` (team reaction, ±1) | `0x0000` (flag = 0) | `0791:65FE after_goal` loop over available pitch slots | `+0xC += ±1`, clamp [1, 255] | NOT written |
| `0x0002` (+2) | `0x0000` (flag = 0) | `0791:7B77 send_off` tail loop over the OTHER side's available pitch slots | `+0xC += +2`, clamp [1, 255] | NOT written |
| `0xfffe` (-2) | `0x0001` (flag = 1) | `0791:7B77 send_off` head call (the sent-off player) | `+0xC += -2`, clamp [1, 255] | written (`min(32, s8(new))`) |
| `0xfffe` (-2) | `0x0001` (flag = 1) | `0791:7D56 injure` (the injured player) | `+0xC += -2`, clamp [1, 255] | written |
| (no direct caller in this listing) | — | `0791:798D booking` (yellow card) | **does NOT write `+0xC`** — the routine sets `+0x10` bit 5, increments side-bookings, calls `1771:33CD force_tactic4_off` when the side is unmanaged. The "yellow card drops confidence" claim does not appear in these lines; a yellow card is a status-bit store only. |

The `flag` is the **low byte** of `param_3`'s low word, not a separate
argument. The C decompiler shows four expressions per call site (the
two words of the int). Listing citations are all in `code/seg_0791_13.asm`:

* the adjust_player_form body (`7CC5..7D53`) at lines 484..548 — the
  `add ax, word ptr [bp + 0xc]` is at 7CEB (delta HIGH word), the flag
  check `cmp byte ptr [bp + 0xa], 0` is at 7D0D, the `min_longint`
  call at 7D25, and the DS:9B07 write `mov byte ptr [di - 0x64f9], al`
  at 7D4C;
* the send_off head call (`7BF5..7C02`) at lines 386..394, push
  0xfffe / push 0x0001 / pitch;
* the send_off tail call for the OTHER team (`7C4C..7C59`) at lines
  430..438, push 0x0002 / push 0x0000 / pitch;
* the injury call (`7DAD..7DBA`) at lines 593..601, push 0xfffe /
  push 0x0001 / pitch;
* the booking routine (`798D..7A40`) at lines 115..188 has no 7CC5
  call (verified by grep — the only adjust_player_form callers in
  segment 0791 are at 64DE, 66AC, 66D6, 7C02, 7C59, 7DBA; the 66AC
  and 66D6 are the 65FE team reactions, 64DE is the scorer);
* the record_goal call (`64CF..64DE`) at lines 177..191, push
  `s8(0x7920[side])` (cwde) / push low byte 1 (the scorer flag).

The `0xfffe` (-2) for send-off/injury sits in the **high word** of
delta (the addend), the low byte of `0x0001` is the **flag**. Adding
`0xfffe` to a signed-byte-extended morale gives a 16-bit signed sum
that is then clamped to `[1, 255]` (not `[1, 32]` — `7CC5`'s clamp
range differs from `B364`'s). After clamping, if the flag byte is
non-zero, the saved `DS:9B07[side*20+slot]` is set to
`min(32, s8(new live))`. The clamp bypasses 32 because the routine
operates on `live` morale that can exceed 32 (from `65FE`); the
`DS:9B07` write then re-anchors to the saved range.

## The team-aggregate byte `DS:9B5A`

`1771:13D0` is the routine that fills the panel's six-word bar
(`9B5A..9B64`). Listing (R1 — the lower-clamp removal):

```
13D0  push bp; mov bp, sp; sub sp, 0xa
       DS:9B5A = 6;  DS:9B5C = 6;  DS:9B5E = 6;  DS:9B60 = 6;  DS:9B62 = 6;  DS:9B64 = 6
       for slot = 1 .. 0x0B:
         if 1771:3216(squad[slot-1]) == 0 (player available):
           morale = s8(players[squad[slot-1]].morale)
           ax = s8(morale);  push ax (sign-extended 32-bit)
           push 0x20 (sign-extended 32-bit)
           call 214B:0D1C  ; min_longint — returns min(0x20, s8(morale))
           add word ptr [0x9b5a], ax   ; 16-bit add, wraps mod 0x10000
           ; (other 5 aggregates analogous)
       ; unsigned divide each by 11
       DS:9B5A /= 0x0B;  DS:9B5C /= 0x0B; ... DS:9B64 /= 0x0B
       if DS:9B5A < 1: DS:9B5A = 1   ; the displayed string must be in-range
       ret 2
```

(`code/seg_1771_02.asm:1001..1126`.) The byte `DS:9B5A` is
`team_panel_morale` — `team morale := max(1, ((6 + sum_of_min(32,
s8(+0xC)) for the 11 available starters) & 0xFFFF) // 11)`. **No lower
clamp on `s8(+0xC)`**: a -128 signed byte contributes -128; the
`add word ptr [0x9b5a], ax` wraps mod 0x10000 on each add; the divide
is the 16-bit unsigned divide. The panel then reads `DS:9B5A` as the
index into `DS:78A3` (`named/seg_1771_02.c:72..88`;
`code/seg_1771_03.asm:201,218,235,252`), itself a stride-16 Pascal
string rooted at `DS:6EB4` — the same description table the player
screen uses for individual morale. There is **no other reader** of
`DS:9B5A` in the listing. `DS:9B5A` is never written anywhere except
by `1771:13D0` (grep over `code/`, `decompiled/`, `named/`: every
reference is in the draw_team_panel path or in `13D0`'s own locals).

`DS:9B5A` is therefore a transient aggregate, recomputed only when
the team panel renders, **not a stored team-morale byte**. The team
panel is drawn from `157D draw_team_panel`, called by `1771:26B9
country_list_screen` and `1771:50F1 view_squad_screen` (`calls.tsv`).
The bot's claim "team morale = mean of player morale" holds
byte-for-byte through this routine; the claim "team morale is also
stored as a single byte on the country record" does not.

The R1 reproduction (`[128, 0, ..., 0]`):

* one contribution: `min(32, -128) = -128` (0xFF80 in 16-bit)
* total: 6 + 0xFF80 = 0xFF86 (= 65414, the wrap)
* divide: 65414 // 11 = 5946 (with remainder 8)
* 5946 >= 1, so result = 5946

The model returns 1 under the old `[0, 32]` clamp; the original
returns 5946. The reviewer ran the original listing bytes in Unicorn
and got 5946; the listing-arithmetic reproduction here matches.

## Foul dispatch `0791:7EEF`

The routine is reached from the in-match engine (`0791:8206
watched_substitution_sequence`) and from the quick engine's foul
handler (`0791:D5C1 roll_quick_foul`, `F012`). The decision tree at
`seg_0791_06.c:714..758`:

```
uVar1 = (uint)DS:830C  ; own pitch slot (DS:830C is the fouling player's slot)
prev = f_0791_261A()    ; draws the next byte from a 255-byte table
if prev < 4:            ; 4/16 chance (table byte in [0,3])
  if u214b_set_test_bit(players[pitch[uVar1].player_index].status, 5) == 0:
    f_0791_798D(ppVar1)        ; yellow card
  else:
    send_off(ppVar1)
else:
  if u214b_random_is_one(0x20):
    send_off(ppVar1)         ; 1/32 chance unconditional send-off

prev = f_0791_261A()    ; draws the next byte again
if prev == 1:            ; 1/16 chance (table byte == 1)
  hard_own  = player_hardness(pitch[DS:830C].player_index)
  hard_oth  = player_hardness(pitch[DS:830B].player_index)
  if hard_own < hard_oth:
    f_0791_7D56(pitch[DS:830C])  ; injure own side
  else:
    f_0791_7D56(pitch[DS:830B])  ; injure the other side
```

`f_0791_261A` is **a table draw, not a tick counter** (R5). Its
listing (`code/seg_0791_04.asm:696..714`) reads `DS:8437` as a
16-bit index, returns the byte at `DS:(DS:8437 - 0x7CC9)` (effective
address `DS:0x8337 + index` after the segment-offset wrap), and
advances `DS:8437` (wrapping from `0xff` to `1`):

```
sub_261A:
261A  55              push bp
261B  89 E5           mov bp, sp
261D  83 EC 02        sub sp, 2
2620  8B 3E 37 84     mov di, word ptr [0x8437]        ; di = index
2624  8A 85 37 83     mov al, byte ptr [di - 0x7cc9]    ; al = DS:0x8337[di]
2628  30 E4           xor ah, ah
262A  89 46 FE        mov word ptr [bp - 2], ax         ; save byte
262D  81 3E 37 84 FF 00 cmp word ptr [0x8437], 0xff
2633  75 08           jne 0x263d
2635  C7 06 37 84 01 00 mov word ptr [0x8437], 1        ; wrap to 1
263B  EB 04           jmp 0x2641
loc_263D:
263D  FF 06 37 84     inc word ptr [0x8437]             ; advance
loc_2641:
2641  8B 46 FE        mov ax, word ptr [bp - 2]
2644  89 EC           mov sp, bp
2646  5D              pop bp
2647  C3              ret
```

The 255-byte table at `DS:0x8337` is initialised by `0791:2648` (a
routine called once per match) with `random(0x10) - 1` (values 0..15)
for `i = 1..0xff`, and `DS:8437` is then set from `DS:9B36`
(`code/seg_0791_04.asm:716..750`). So 261A returns the next byte from
a 255-element pre-shuffled table, advancing the index, and the values
in the table are bounded to [0, 15]. The `<4` branch in the foul
dispatch fires for table bytes 0..3 (4/16 = 1/4 of the entries); the
`==1` branch fires for table bytes == 1 (1/16 of the entries). The
dispatcher's "time-gated" reading is incorrect: it is "table-gated",
and the table is a pre-shuffled draw, not a tick counter.

The routine does NOT itself write `+0xC`; it dispatches to `798D` /
`7B77` / `7D56`, which each have their own effects listed above. The
injury branch is gated on a `player_hardness` comparison between
`DS:830C` (fouling slot) and `DS:830B` (other slot) and is also
table-gated by the same pre-shuffled table.

## Routes and orders outside the result rule (Q016 recap)

* `000E:6970 simulate_fixture` plays fixtures the router sends here:
  `D47E` (quick result), then `B7FA` (result update), `B602`
  (silent-route scorers, +1 to scorer), `D050` (well-known
  post-update). After `B602`, `B7FA`'s `B364` has already clipped
  each `+0xC`, so a scorer's bonus is added on top of the result
  term. There is no injury/card/friendly branch here.
* `0791:F1F6 run_match` plays fixtures in the watched path. After
  `F098 play_match` it calls `BC5D reset_team_tactics` (per
  unmanaged team), `D050`, then `BA4E update_pool_player_state`
  (managed pool). `B7FA` is NOT in this list — `B7FA` is the
  silent-result updater.
* `000E:6E15` (router tail) is the watched/managed path: `BB2F
  prepare_unplayed_match` when `fixture +2 = 0`, else `F1F6
  run_match`. `BB2F` calls `1771:3558` (fitness/energy redraw, NOT
  3651) per player, then `B364` with `rand(2) - rand(4)` (no
  B71C), then per team `BC5D` (unmanaged) or `BA4E` (managed). The
  friendly/competition distinction in this listing is the
  `fixture +2` byte's membership in `DS:0F3E` (the result-term set)
  and the small code-byte sets at `CS:695A` and `CS:697A` (the
  watch-prompt set). The literal "friendly" classification is not
  a stored byte, and the result-term doubling in `B71C` (`(winner
  == side) == (side == 0 or 1771:5A03)`) does not name friendlies:
  F019 already establishes this set is `{kinds 4, 5, 8, 9..196}`
  (the kinds whose set bits in the 32-byte `DS:0F3E` are 1, with
  gaps `{0, 1, 2, 3, 6, 7, 197..255}`). Whether any one is
  "friendly" is **not established** by these lines.

## Reader/writer inventory of `+0xC` and `DS:9B5A` (R6)

This is the complete inventory. F019's result-rule inventory
(`B364` and its callers) is included; the event writers (the
`7CC5` family) are this task's contribution. The team-morale
inventory is `DS:9B5A` and its single writer `1771:13D0`. Every
entry names the routine, what it reads/writes, and the listing
line citation. The "direct" writers are routines that
read-modify-write a player byte at +0xC or the team-morale byte;
"callers" are routines that invoke a direct writer with a specific
delta. No other direct writer exists in the named view.

| Routine | Reads / writes | Listing lines |
| --- | --- | --- |
| `0791:7CC5` `adjust_player_form` | reads `player +0xC`; writes `clamp(s8(+0xC)+delta_high,1,255)`; flag non-zero also writes `min(32, s8(new)) & 0xFF` to `DS:9B07[side*20+slot]` | `code/seg_0791_13.asm:484..548` |
| `0791:B364` `B364` (F019 result rule) | reads/writes signed `+0xC`, clamp [1, 32] | `code/seg_0791_18.asm:621..653`; `named/seg_0791_09.c:540..548` |
| `0791:798D` `booking` | sets `player +0x10` bit 5, increments side booking count, calls `1771:33CD force_tactic4_off` on unmanaged teams. **Does NOT write `+0xC`.** | `code/seg_0791_13.asm:115..188`; `named/seg_0791_06.c:1087..1118` |
| `0791:7B77` `send_off` | sets `+0x10` bit 6 and clears bit 5, walks the player off; calls `7CC5(pitch, 0xfffe, flag=1)` for the sent-off player (so `+0xC += -2`, clamp [1, 255], DS:9B07 written), then loops `7CC5(pitch, 2, flag=0)` over the OTHER side's available pitch slots | `code/seg_0791_13.asm:330..480` |
| `0791:7D56` `injure` | sets `+0xE = 0`, walks the player off, calls `7CC5(pitch, 0xfffe, flag=1)` (so `+0xC += -2`, clamp [1, 255], DS:9B07 written), and on unmanaged sides calls `C88D substitute_player` to bring a bench player on. | `code/seg_0791_13.asm:551..672` |
| `0791:7EEF` `foul_dispatch` | dispatches to `798D` (yellow card), `7B77` (sending-off) or `7D56` (injury). Does not write `+0xC` directly. Gated by a pre-shuffled 255-element draw table at `DS:0x8337` via `0791:261A` (R5). | `named/seg_0791_07.c:120..167`; `code/seg_0791_04.asm:696..714` |
| `0791:6443` `record_goal` (scorer) | calls `7CC5(pitch, s8(DS:0x7920[side_of_credit]), flag=1)`: `+0xC += ±1`, clamp [1, 255], DS:9B07 written | `code/seg_0791_11.asm:177..191` |
| `0791:65FE` `after_goal` (team reaction) | per available pitch slot calls `7CC5(pitch, s8(DS:0x7920[side_of_ball]), flag=0)`: `+0xC += ±1`, clamp [1, 255], DS:9B07 NOT written | `code/seg_0791_11.asm:380..429` |
| `1771:13D0` `team_panel_aggregate` | reads `+0xC` of each available starter; sums `min(32, s8(+0xC))` (no lower clamp) into `DS:9B5A`; also writes `DS:9B5C..9B64` | `code/seg_1771_02.asm:1001..1126` |
| `1771:157D` `draw_team_panel` | reads `DS:9B5A..9B64`; the only consumer of `DS:9B5A` in the listing | `named/seg_1771_02.c:7..110` |
| `0791:278A` (F015) | reads signed `+0xC` for the skill blend | `named/seg_0791_02.c:614..624`; `code/seg_0791_04.asm, 27A2..27BC` |
| `0791:CB7D` (F018 restore) | writes `+0xC` from saved `DS:9B07` | `code/seg_0791_20.asm:973..`; `named/seg_0791_10.c:658..679` |
| `0791:F1F6` (run_match) | reads `+0xC` into saved `DS:9B07` | `code/seg_0791_23.asm:1035..`; `named/seg_0791_12.c:378..395` |
| `1771:377E` (strength) | reads signed `+0xC` for player strength (special branch >=32) | `named/seg_1771_03.c:309..326` |
| `1771:42BC` (description) | reads `+0xC` for description string and bar | `code/seg_1771_06.asm:1114..1142`; `named/seg_1771_03.c:882..893` |
| `1771:96D3` (creation) | writes `draw(32)` at player creation | `named/seg_1771_07.c:181..186` |

Callers of the direct writers (event-result rule chain):

* `B364` callers: `B602` goal scorer (+1; `named/seg_0791_09.c:654..662`),
  `B7FA` result/bench (`code/seg_0791_19.asm:137..187`), `BA4E`
  managed pool (`named/seg_0791_09.c:847..862`), `BB2F` unplayed
  fixture (`named/seg_0791_09.c:890..922`).
* `7CC5` callers: `6443` scorer with flag one (`named/seg_0791_05.c:906..908`);
  `65FE` team-wide goal reaction with flag zero (`:992..1007`);
  `7B77` head (flag 1) and tail (flag 0) for sending-off;
  `7D56` for injury (flag 1).
* `CB7D` is called by `F1F6` after the summary
  (`named/seg_0791_12.c:420`).
* `96D3` is reached by creation and retirement/replacement (F007/F016);
  it is not a post-match result-relative update.

No other direct `+0xC` writer is in the named view. `1771:13D0` is
the only writer of `DS:9B5A`. `DS:9B5A` is not stored as a country
byte.

## What can be predicted from before state and event alone

A single event (booking / sending-off / injury / goal reaction)
changes a player's `+0xC` to `clamp(s8(+0xC) + delta, 1, 255)`,
where `delta` is named: `-2` for sending-off and injury, `+1` for
the scoring side's team-wide reaction, `-1` for the conceding side's
team-wide reaction, `+1` or `-1` for the scorer depending on the
in-match `DS:7C39` flag. The booking routine does NOT touch `+0xC`
— the yellow-card confidence claim is NOT established by these
lines. The `DS:9B07` saved byte is updated only by the `-2` (and
the scorer's `+1`) — team-wide reactions and the OTHER-team's `+2`
from a sending-off leave the saved byte alone, so the after-match
restore from `9B07` is consistent.

The team aggregate `DS:9B5A` is recomputed at panel-render time as
`max(1, ((6 + Σ_i min(32, s8(+0xC[i])) for i in 1..11 available
starters) & 0xFFFF) // 11)`, with no carries into the country
record. Two saves of the same team minutes apart can disagree in the
displayed team morale even when neither member's stored `+0xC` has
changed (e.g. when an unavailable starter becomes available after
recovery).

## Available human records

`experiments/E015-human-playthrough/README.md:55-65` identifies all
three records as extractions of the same four-state scripted
sitting; the four savestates hold empty player records (the game
had not been played). No E015 record describes a played match's
before/after pairs, and none is used here. None of the brief's
6-run budget was spent on DOSBox matches; the listing answer
above is established by static analysis and the hand-traced
listing arithmetic in `experiments/E019-q017-events-morale/probe-literal-001.json`.
