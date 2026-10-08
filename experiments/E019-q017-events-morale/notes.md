# Q017 static notebook

## Method

Read the named view first: `seg_0791_05.c` (record_goal 6443, after_goal 65FE), `seg_0791_06.c` (7EEF foul dispatch, 798D booking, 7B77 sending-off, 7D56 injury, 7CC5 the live-form helper, B7A4D's card dispatch), `seg_0791_09.c` (B7FA already covered by F019), `seg_1771_01.c` (1771:13D0 the team aggregate) and `seg_1771_02.c` (157D draw_team_panel, the only reader of `DS:9B5A`). Cross-checked against the raw `decompiled/` and capstone `code/` listings where Ghidra's set-membership and Pascal retf/ret are misleading. No DOSBox match was run.

## Direct `+0xC` writers outside F019's result rule

Every direct `+0xC` store this listing establishes is `0791:7CC5 adjust_player_form(pitch, flag, delta)`. The assembly:

```
7CC5  push bp; mov bp, sp; sub sp, 4
       ; load pitch[+0xD] = player_word (seg_0791_13.asm:487-495)
       ; param_1 = [bp+6..8] (far ptr to pitch record)
       ; signed_byte byte ptr es:[di + 0xc]
       ; cwde  ax = sign_ext(al)
       ; add ax, word ptr [bp + 0xc]   ; param_3 HIGH word — the actual delta
       ; clamp to [1, 255]             ; param_3 LOW byte is the flag
       ; store low byte back to player +0xC
       ; if [bp + 0xa] (param_3 low byte) != 0:
       ;   DS:9B07[side*20+slot] := min(32, signed byte of new +0xC)
       ; retf 8                        ; 4 stack slots = pitch + delta_high + delta_low
```

Caller push convention (right-to-left on stack):

| Delta HIGH | Delta LOW (low byte = flag) | Caller | Effect on `+0xC` | DS:9B07 |
| --- | --- | --- | --- | --- |
| `s8(DS:0x7920[side])` (goal scorer, ±1) | `0x0001` or `0xff01` (flag = 1) | `0791:6443 record_goal` | `+0xC += ±1`, clamp [1, 255] | written (`min(32, new)`) |
| `s8(DS:0x7920[side])` (team reaction, ±1) | `0x0000` (flag = 0) | `0791:65FE after_goal` loop over available pitch slots | `+0xC += ±1`, clamp [1, 255] | NOT written |
| `0x0002` (+2) | `0x0000` (flag = 0) | `0791:7B77 send_off` tail loop over the OTHER side's available pitch slots | `+0xC += +2`, clamp [1, 255] | NOT written |
| `0xfffe` (-2) | `0x0001` (flag = 1) | `0791:7B77 send_off` head call (the sent-off player) | `+0xC += -2`, clamp [1, 255] | written (`min(32, new)`) |
| `0xfffe` (-2) | `0x0001` (flag = 1) | `0791:7D56 injure` (the injured player) | `+0xC += -2`, clamp [1, 255] | written |
| (no direct caller in this listing) | — | `0791:798D booking` (yellow card) | **does NOT write `+0xC`** — the routine sets `+0x10` bit 5, increments side-bookings, calls `1771:33CD force_tactic4_off` when the side is unmanaged. The "yellow card drops confidence" claim does not appear in these lines; a yellow card is a status-bit store only. |

The `flag` is the **low byte** of `param_3`'s low word, not a separate argument. The C decompiler shows four expressions per call site (the two words of the int). Listing citations are all in `code/seg_0791_13.asm`:

* the adjust_player_form body (`7CC5..7D53`) at lines 484..548 — the `add ax, word ptr [bp + 0xc]` is at 7CEB (delta HIGH word), the flag check `cmp byte ptr [bp + 0xa], 0` is at 7D0D, and the DS:9B07 write `mov byte ptr [di - 0x64f9], al` at 7D4C;
* the send_off head call (`7BF5..7C02`) at lines 386..394, push 0xfffe / push 0x0001 / push pitch;
* the send_off tail call for the OTHER team (`7C4C..7C59`) at lines 430..438, push 0x0002 / push 0x0000 / push pitch;
* the injury call (`7DAD..7DBA`) at lines 593..601, push 0xfffe / push 0x0001 / push pitch;
* the booking routine (`798D..7A40`) at lines 115..188 has no 7CC5 call (verified by grep — the only adjust_player_form callers in segment 0791 are at 64DE, 66AC, 66D6, 7C02, 7C59, 7DBA; the 66AC and 66D6 are the 65FE team reactions, 64DE is the scorer);
* the record_goal call (`64CF..64DE`) at lines 177..191, push `s8(0x7920[side])` (cwde) / push low byte 1 (the scorer flag).

The `0xfffe` (-2) for send-off/injury sits in the **high word** of delta (the addend), the low byte of `0x0001` is the **flag**. Adding `0xfffe` to a signed-byte-extended morale gives a 16-bit signed sum that is then clamped to `[1, 255]` (not `[1, 32]` — `7CC5`'s clamp range differs from `B364`'s). After clamping, if the flag byte is non-zero, the saved `DS:9B07[side*20+slot]` is set to `min(32, signed_byte(new_live))`. The clamp bypasses 32 because the routine operates on `live` morale that can exceed 32 (from `65FE`); the `DS:9B07` write then re-anchors to the saved range.

## The team-aggregate byte `DS:9B5A`

`1771:13D0` is the routine that fills the panel's six-word bar (`9B5A..9B64`). Listing:

```
13D0  push bp; mov bp, sp; sub sp, 0xa
       DS:9B5A = 6;  DS:9B5C = 6;  DS:9B5E = 6;  DS:9B60 = 6;  DS:9B62 = 6;  DS:9B64 = 6
       for slot = 1 .. 0x0B:
         if 1771:3216(squad[slot-1]) == 0 (player available):
           morale = s8(players[squad[slot-1]].morale)
           DS:9B5A += min(0x20, max(0, morale))         ; signed byte, clamp [0, 32]
           if s8(players[...].energy) > 0:
             DS:9B5C += s8(players[...].fitness)
           DS:9B5E += (player_hardness(squad[slot-1]) & 0xff)
           DS:9B60 += s8(players[...].energy)
           DS:9B62 += players[...].age (byte)
           DS:9B64 += players[...].caps (word)
       ; unsigned divide each by 11
       DS:9B5A /= 0x0B;  DS:9B5C /= 0x0B; ... DS:9B64 /= 0x0B
       if DS:9B5A < 1: DS:9B5A = 1   ; the displayed string must be in-range
       ret 2
```

(`code/seg_1771_02.asm:1001..1126`.) The byte `DS:9B5A` is `team_panel_morale` — `team morale := 1 + ⌊mean(min(32, max(0, signed +0xC over the 11 available starters))⌋` (offset 6 cancels out after the divide). The 6 seed and the divide-by-11 mean each starter's contribution is `min(32, max(0, signed_byte(+0xC))) / 11` plus `6/11 ≈ 0.5`, so a team of all-32 starters displays 32 (the rounded index of "demoralised" → "excellent" reads `+0xC` itself; the 6 seed lifts the floor only when starters are at 0 or absent).

The panel then reads `DS:9B5A` as the index into `DS:78A3` (`named/seg_1771_02.c:72..88`; `code/seg_1771_03.asm:201,218,235,252`), itself a stride-16 Pascal string rooted at `DS:6EB4` — the same description table the player screen uses for individual morale. There is **no other reader** of `DS:9B5A` in the listing. `DS:9B5A` is never written anywhere except by `1771:13D0` (grep over `code/`, `decompiled/`, `named/`: every reference is in the draw_team_panel path or in `13D0`'s own locals).

`DS:9B5A` is therefore a transient aggregate, recomputed only when the team panel renders, **not a stored team-morale byte**. The team panel is drawn from `157D draw_team_panel`, called by `1771:26B9 country_list_screen` and `1771:50F1 view_squad_screen` (`calls.tsv`). The bot's claim "team morale = mean of player morale" holds byte-for-byte through this routine; the claim "team morale is also stored as a single byte on the country record" does not.

## Foul dispatch `0791:7EEF`

The routine is reached from the in-match engine (`0791:8206 watched_substitution_sequence`) and from the quick engine's foul handler (`0791:D5C1 roll_quick_foul`, `F012`). The decision tree at `seg_0791_06.c:714..758`:

```
uVar1 = (uint)DS:830C  ; own pitch slot (DS:830C is the fouling player's slot)
prev = f_0791_261A()    ; tick-counter helper (increments and returns the previous count)
if prev < 4:           ; strength comparison routed in 2605... arbitrary; not read
  if u214b_set_test_bit(players[pitch[uVar1].player_index].status, 5) == 0:
    f_0791_798D(ppVar1)        ; yellow card
  else:
    send_off(ppVar1)
else:
  if u214b_random_is_one(0x20):
    send_off(ppVar1)

prev = f_0791_261A()
if prev == 1:
  hard_own  = player_hardness(pitch[DS:830C].player_index)
  hard_oth  = player_hardness(pitch[DS:830B].player_index)
  if hard_own < hard_oth:
    f_0791_7D56(pitch[DS:830C])  ; injure own side
  else:
    f_0791_7D56(pitch[DS:830B])  ; injure the other side
```

`f_0791_261A` (`code/seg_0791_04.asm:696..714`) is a tick counter which returns the previous value (the byte at `DS:8437`), then increments. So the `<4` and `==1` branches are time-gated, not strength-driven. The routine does NOT itself write `+0xC`; it dispatches to `798D` / `7B77` / `7D56`, which each have their own effects listed above.

## Routes and orders outside the result rule (Q016 recap)

* `000E:6970 simulate_fixture` plays fixtures the router sends here: `D47E` (quick result), then `B7FA` (result update), `B602` (silent-route scorers, +1 to scorer), `D050` (well-known post-update). After `B602`, `B7FA`'s `B364` has already clipped each `+0xC`, so a scorer's bonus is added on top of the result term. There is no injury/card/friendly branch here.
* `0791:F1F6 run_match` plays fixtures in the watched path. After `F098 play_match` it calls `BC5D reset_team_tactics` (per unmanaged team), `D050`, then `BA4E update_pool_player_state` (managed pool). `B7FA` is NOT in this list — `B7FA` is the silent-result updater.
* `000E:6E15` (router tail) is the watched/managed path: `BB2F prepare_unplayed_match` when `fixture +2 = 0`, else `F1F6 run_match`. `BB2F` calls `1771:3558` (fitness/energy redraw, NOT 3651) per player, then `B364` with `rand(2) - rand(4)` (no B71C), then per team `BC5D` (unmanaged) or `BA4E` (managed). The friendly/competition distinction in this listing is the `fixture +2` byte's membership in `DS:0F3E` (the result-term set) and the small code-byte sets at `CS:695A` and `CS:697A` (the watch-prompt set). The literal "friendly" classification is not a stored byte, and the result-term doubling in `B71C` (`(winner == side) == (side == 0 or 1771:5A03)`) does not name friendlies: F019 already establishes this set is `{kinds 4, 5, 8, 9..196}` (the kinds whose set bits in the 32-byte `DS:0F3E` are 1, with gaps `{0, 1, 2, 3, 6, 7, 197..255}`). Whether any one is "friendly" is **not established** by these lines.

## Complete `+0xC` and `DS:9B5A` reader/writer inventory

The F019 table (`experiments/E018-q016-confidence/notes.md`, "Complete direct player +0C reader/writer inventory") lists every direct reader and writer of `player +0xC` it found. The event writers are the three additions this task establishes:

| Routine | Reads / writes | Listing lines |
| --- | --- | --- |
| `0791:7CC5` `adjust_player_form` | reads `player +0xC`; writes `clamp(s8(+0xC) + delta_high, 1, 255)`; flag non-zero also writes `min(32, s8(new))` to `DS:9B07[side*20+slot]` | `code/seg_0791_13.asm:484..548` |
| `0791:798D` `f_0791_798D` (booking) | sets `player +0x10` bit 5, increments side-booking count, calls `1771:33CD force_tactic4_off` on unmanaged teams. **Does NOT write `+0xC`.** | `code/seg_0791_13.asm:115..188`; `named/seg_0791_06.c:431..463` |
| `0791:7B77` `send_off` | sets `+0x10` bit 6 and clears bit 5, walks the player off; calls `7CC5(pitch, 0xfffe, flag=1)` for the sent-off player (so `+0xC += -2`, clamp [1, 255], DS:9B07 written), then loops `7CC5(pitch, 2, flag=0)` over the OTHER side's available pitch slots | `code/seg_0791_13.asm:330..480` |
| `0791:7D56` `f_0791_7D56` (injure) | sets `player +0xE = 0`, walks the player off, calls `7CC5(pitch, 0xfffe, flag=1)` (so `+0xC += -2`, clamp [1, 255], DS:9B07 written), and on unmanaged sides calls `C88D substitute_player` to bring a bench player on. | `code/seg_0791_13.asm:551..672` |
| `0791:7EEF` `f_0791_7EEF` (foul dispatch) | dispatches to `798D` (yellow card), `7B77` (sending-off) or `7D56` (injury). Does not write `+0xC` directly. | `named/seg_0791_06.c:712..758` |
| `0791:6443` `record_goal` (scorer) | calls `7CC5(pitch, s8(DS:0x7920[side]), flag=1)`: `+0xC += ±1`, clamp [1, 255], DS:9B07 written | `code/seg_0791_11.asm:177..191` |
| `0791:65FE` `after_goal` (team reaction) | per available pitch slot calls `7CC5(pitch, s8(DS:0x7920[side]), flag=0)`: `+0xC += ±1`, clamp [1, 255], DS:9B07 NOT written | `code/seg_0791_11.asm:380..429` |
| `1771:13D0` `f_1771_13D0` (team aggregate) | reads `+0xC` of each available starter; writes `DS:9B5A..9B64` (six aggregate bytes) | `code/seg_1771_02.asm:1001..1126` |
| `1771:157D` `draw_team_panel` | reads `DS:9B5A..9B64`; the only consumer of `DS:9B5A` in the listing | `named/seg_1771_02.c:7..110` |

No other direct `+0xC` writer is in the named view. `1771:13D0` is the only writer of `DS:9B5A`. `DS:9B5A` is not stored as a country byte.

## What can be predicted from before state and event alone

A single event (booking / sending-off / injury / goal reaction) changes a player's `+0xC` to `clamp(s8(+0xC) + delta, 1, 255)`, where `delta` is named: `-2` for sending-off and injury, `+1` for the scoring side's team-wide reaction, `-1` for the conceding side's team-wide reaction, `+1` or `-1` for the scorer depending on the in-match `DS:7C39` flag. The booking routine does NOT touch `+0xC` — the yellow-card confidence claim is NOT established by these lines. The `DS:9B07` saved byte is updated only by the `-2` (and the scorer's `+1`) — team-wide reactions and the OTHER-team's `+2` from a sending-off leave the saved byte alone, so the after-match restore from `9B07` is consistent.

The team aggregate `DS:9B5A` is recomputed at panel-render time as `(6 + Σ_i clamp(s8(+0xC[i]), 0, 32) for i in 1..11 available starters) // 11`, with no carries into the country record. Two saves of the same team minutes apart can disagree in the displayed team morale even when neither member's stored `+0xC` has changed (e.g. when an unavailable starter becomes available after recovery).

## Available human records

`experiments/E015-human-playthrough/README.md:55-65` identifies all three records as extractions of the same four-state scripted sitting; the four savestates hold empty player records (the game had not been played). No E015 record describes a played match's before/after pairs, and none is used here. None of the brief's 6-run budget was spent on DOSBox matches; the listing answer above is established by static analysis and one guest-routine probe per routine.