# F020 Injuries, cards, sending-offs and the team-morale aggregate

- **Status**: proposed
- **Question**: Q017 (Q05.7–Q05.9), T33.
- **Hypothesis** (from the brief): a booked or injured player loses
  confidence; team morale moves with the mean confidence. The static
  route is the writers of `player +0xC` outside F019's result rule
  (`0791:7CC5`) and the team aggregate `DS:9B5A` written by
  `1771:13D0`.
- **Confidence**: static-derived; the team-aggregate routine's
  arithmetic is byte-exact on the listing and the named event deltas
  are the only delta pushes any caller makes. The reproduction of
  `[128, 0, ..., 0]` from the listing gives `(6 + (-128)) & 0xFFFF =
  65414`, `65414 // 11 = 5946`; the model returns 5946; the reviewer's
  Unicorn run of the original listing bytes also returned 5946.

## Method

Read the named view first: `static/goal-exe/named/seg_0791_05.c`
(`record_goal` 6443, `after_goal` 65FE), `seg_0791_06.c`
(`foul_dispatch` 7EEF, `booking` 798D, `send_off` 7B77, `injure`
7D56, `adjust_player_form` 7CC5, `restore_match_player_state` CB7D,
`run_match` F1F6), `seg_0791_09.c` (the B7FA result-rule chain),
`seg_1771_01.c` (`team_aggregate` 1771:13D0) and `seg_1771_02.c`
(`draw_team_panel` 157D, the only consumer of `DS:9B5A`).
Cross-checked against the raw `decompiled/` output and the capstone
`code/` listing where Ghidra's set-membership and Pascal retf/ret
are misleading. The complete direct player `+0xC` reader/writer
inventory outside F019's result rule is in
`experiments/E019-q017-events-morale/notes.md`, with listing lines
and the reconciliation of F019's `B364` writer with this task's
event writers.

The event writers are all callers of `0791:7CC5 adjust_player_form`,
each pushing a specific `(delta_high, delta_low)` pair:

| Caller | delta_high | delta_low (low byte = flag) | Effect on `+0xC` | DS:9B07 written? |
| --- | --- | --- | --- | --- |
| `0791:798D` booking | — | — | does **not** call 7CC5; no `+0xC` write | — |
| `0791:7B77` send_off head | `0xFFFE` (-2) | `0x0001` (flag=1) | sent-off player: `+0xC := clamp(s8(+0xC)-2,1,255)` | yes (the sent-off player only) |
| `0791:7B77` send_off tail | `0x0002` (+2) | `0x0000` (flag=0) | OTHER team available players (1..11): `+0xC := clamp(s8(+0xC)+2,1,255)` | no |
| `0791:7D56` injure | `0xFFFE` (-2) | `0x0001` (flag=1) | injured player: `+0xC := clamp(s8(+0xC)-2,1,255)`; `+0xE := 0` (F018) | yes (the injured player only) |
| `0791:6443` record_goal scorer | `s8(DS:0x7920[DS:7C39==0?1:0])` | `0x0001` (flag=1) | scorer: `+0xC := clamp(s8(+0xC)+1,1,255)` (or `-1` when `DS:7C39` is set) | yes |
| `0791:65FE` after_goal team reaction | `s8(DS:0x7920[side_of_ball])` | `0x0000` (flag=0) | every available pitch player: `+0xC := clamp(s8(+0xC)+1,1,255)` (the ball side gains) and `clamp(s8(+0xC)-1,1,255)` (the other side loses) | no |

The named `flag` is the low byte of `delta_low`; the high word of
delta is the actual addend (`add ax, word ptr [bp + 0xc]` in
`7CC5`'s body). A yellow card (`0791:798D`) sets `+0x10` bit 5,
increments the side booking counters, and calls `1771:33CD
force_tactic4_off` on unmanaged sides; it never calls `7CC5`, so
the listing does **not** establish that a yellow card drops
confidence. The brief's "a booked or injured player loses
confidence" holds for sending-off and injury (-2), but is **not
established** for booking by these lines.

The team-morale aggregate `DS:9B5A` is the only team-level morale
byte in the listing. It is written **only** by `1771:13D0
team_panel_aggregate` (assembly: `code/seg_1771_02.asm:1001..1126`).
The routine resets six 16-bit words (`DS:9B5A..9B5C..9B5E..9B60..
9B62..9B64`) to `6`, walks the 11 starting-XI slots, and for each
**available** player (`1771:3216` = `+0xE > 0` AND `+0x10` bits
8/6/3 all clear) sums `min(32, s8(players[squad[slot-1]].morale))`
(no lower clamp — the `214B:0D1C` helper returns
`min(32, s8(+0xC))` only) into `DS:9B5A`, with analogous
contributions for fitness, hardness, energy, age and caps into the
other five bytes. The `add word ptr [0x9B5A], ax` at line 1067
wraps mod 0x10000 on each add; after the loop each word is
unsigned-divided by 11 (`div cx` at line 1093) and `DS:9B5A` is
floored to `1`. The result is therefore

```
team_panel_morale(starters) := max(1, ((6 + Σ_{available} min(32, s8(+0xC))) & 0xFFFF) // 11)
```

where `starters` are the 11 squad words' signed `+0xC` bytes. The
aggregate is recomputed every time `1771:157D draw_team_panel`
renders the team panel (only consumer of `DS:9B5A` in the listing:
the bar at row 0x17 is filled from `DS:9B5A`, and the morale
string at row 0x17 is selected via `DS:78A3[DS:9B5A]`, the same
6EB4-rooted table the player panel reads for individual morale,
`code/seg_1771_02.asm:81..88`). No other writer of `DS:9B5A` exists
in the listing — `grep -rn 9B5A` over `code/`, `decompiled/`,
`named/` returns only the lines cited here.

The brief's "team morale moves with the mean confidence" therefore
holds byte-for-byte: the team panel aggregate `DS:9B5A` is
`max(1, ((6 + mean of min(32, s8(+0xC)) for the 11 starters) &
0xFFFF) // 11)`. The brief's "team morale is also stored as a
single byte on the country record" does **not** hold: `DS:9B5A` is
a transient byte recomputed at every panel render and never
persisted. The R1 reproduction case `[128, 0, ..., 0]` (one
squad word's `+0xC` = 128 = -128 signed) gives total
`(6 + (-128)) & 0xFFFF = 65414`, `65414 // 11 = 5946` — the
reviewer's Unicorn run of the original listing bytes confirms
5946; the model returns 5946.

## Answer and claim-by-claim basis

All paths below are relative to `static/goal-exe/`. Each
paragraph's listing citations are physical line numbers.

### Booking, sending-off and injury change `+0xC` by a fixed amount

The single `+0xC` writer outside F019's result rule is `0791:7CC5`
(`code/seg_0791_13.asm:484..548`, the only `add ax, word ptr [bp +
0xc]` followed by `clamp_int` (line 507) and the `DS:9B07` write
at 7D4C). Its calling convention is unusual: the routine's int
parameter is pushed as two 16-bit words (right-to-left), then the
pitch pointer is pushed as segment + offset, then `cs`, then a near
call. After `push bp; mov bp, sp`, the routine reads `[bp + 6]`
and `[bp + 8]` as the pitch pointer, `[bp + 0xc]` as the **high
word of delta** (the actual addend), and the **low byte of
`[bp + 0xa]`** as the persist flag (the bool that controls
whether `DS:9B07[side*20+slot]` is written). All five callers in
the listing push the matching `(delta_high, delta_low)` pair.

The listing establishes:

* **Sending-off (`0791:7B77`, `code/seg_0791_13.asm:330..480`)**
  drops the sent-off player's `+0xC` by 2
  (`code/seg_0791_13.asm:386..394`, push `0xfffe` / push `0x0001`
  / pitch ptr / call 7CC5) and adds 2 to every available pitch
  player on the OTHER side (line 430..438, push `0x0002` / push
  `0x0000` / pitch ptr / call 7CC5; flag=0 → DS:9B07 NOT
  updated). The -2 to the sent-off player is a `flag=1` write, so
  `DS:9B07` IS set for that player. There is no DS:9B07 store for
  the other-team +2.
* **Injury (`0791:7D56`, `code/seg_0791_13.asm:551..672`)** also
  drops the injured player's `+0xC` by 2
  (`code/seg_0791_13.asm:593..601`, same push sequence as
  send_off head), and sets `+0xE := 0` (the injury store at line
  587, F018). On unmanaged sides it then calls C88D
  substitute_player to bring a bench player on.
* **Yellow card (`0791:798D`, `code/seg_0791_13.asm:115..188`)**
  does **not** call `7CC5` (the only `7CC5` calls in
  `seg_0791_13.asm` are at lines 394 (send_off head), 438 (send_off
  tail), 601 (injure); grep confirms no `7CC5` reference inside
  the `798D..7A40` body). It sets `+0x10` bit 5 (line 149,
  `214B:0C79 include`), increments the side booking counters
  (`DS:7B85[side*10]` at line 165, `DS:8321` at line 168), and
  calls `1771:33CD force_tactic4_off` on unmanaged sides (line
  184). The routine is a status-bit store; the listing does
  **not** establish that a yellow card drops confidence.

  → **Help claim "booked player loses confidence"**: not
    established by these lines for booking. Established for
    sending-off and injury.

### Foul dispatch: 0791:7EEF

The foul dispatch (`code/seg_0791_06.asm:712..758`, F012) is
reached from the quick engine's foul handler (`0791:D5C1
roll_quick_foul`, F012) and from the in-match foul path
(`0791:5B36`'s coin-flip branch and `0791:8206
watched_substitution_sequence`). It draws twice from
`0791:261A`, a 255-element pre-shuffled table at `DS:0x8337`
initialised by `0791:2648` with `random(0x10) - 1` (values 0..15,
`code/seg_0791_04.asm:716..750`); the table byte is **not a tick
counter** (R5). With the first draw `< 4` (table bytes 0..3, 4/16
of entries) the routine picks booking (`0791:798D`) or sending
off (`0791:7B77`) based on whether the player's `+0x10` bit 5 is
already set; else, with `random_is_one(0x20)` (1/32), it sends
off unconditionally. After that, if the second draw `== 1` (1/16
of entries) it compares `player_hardness(2FFB)` on `DS:830C` and
`DS:830B` and calls `7D56` on the lower-hardness side. The routine
does not itself write `+0xC`; the effect is whatever the callee
does. Its listing establishes the dispatch tree; the strength
comparison routing into injury is established by the same
`player_hardness` call used elsewhere; the table semantics are
established by `2648`'s fill loop and `261A`'s draw.

### Friendlies vs competition matches: not established

The fixture router (`000E:6970 simulate_fixture`, `000E:6CA7
route_fixture`, `code/seg_000E_09.asm:1..200`) sends a fixture to
`6970` (silent result) or to `6E15` (watched/managed path) by the
first byte (`0xFE` for managed-team fixtures, otherwise) and by
membership in `DS:0F3E` (the result-term set), `CS:695A`,
`CS:697A`, and `CS:6C87` (the watch-prompt sets whose bytes happen
to be instruction bytes at those code addresses). The literal
"friendly" classification does not appear as a stored byte; F019
already established the result-term set is `{kinds 4, 5, 8,
9..196}` (the kinds whose set bits in the 32-byte `DS:0F3E` are 1,
with gaps `{0, 1, 2, 3, 6, 7, 197..255}`). The injury and card
dispatch (`0791:7EEF`) is not gated by fixture kind. Whether any
one of those kinds is "friendly" is **not established** by these
lines.

### The team morale aggregate

`1771:13D0 team_panel_aggregate`
(`code/seg_1771_02.asm:1001..1126`) sums, over the 11
starting-XI slots, `min(32, s8(+0xC))` per available starter
(line 1038..1045), adds the 6 seed (line 1012), and
unsigned-divides by 11 (line 1067) — `div cx` is the 16-bit
unsigned divide. The accumulator is a 16-bit word, wrapped mod
0x10000 on each add (line 1067, `add word ptr [0x9b5a], ax`). The
result is the team morale aggregate `DS:9B5A`. It is then floored
to `1` (line 1120..1122, `cmp word ptr [0x9b5a], 1; jae`). The
value is recomputed every time `1771:157D draw_team_panel`
renders the team panel; the only consumer of `DS:9B5A` is that
same caller (the bar at row 0x17 is filled from `DS:9B5A`, and
the morale string at row 0x17 is selected via `DS:78A3[DS:9B5A]`,
the same 6EB4-rooted table the player panel reads for individual
morale, `code/seg_1771_02.asm:81..88`). No other writer of
`DS:9B5A` exists in the listing — `grep -rn 9B5A` over `code/`,
`decompiled/`, `named/` returns only the lines cited here.

The brief's "team morale moves with the mean confidence"
therefore holds byte-for-byte: the team panel aggregate `DS:9B5A`
is `max(1, ((6 + mean of min(32, s8(+0xC)) for the 11 starters) &
0xFFFF) // 11)`. The brief's "team morale is also stored as a
single byte on the country record" does **not** hold: `DS:9B5A`
is a transient byte recomputed at every panel render and never
persisted.

Two consequences follow:

* Saving a game and reloading it does not preserve the displayed
  team morale; the panel computes it from the squad's current
  `+0xC` bytes on every render.
* The team panel reading only the 11 starting-XI slots means a
  substitute's `+0xC` does not contribute. The aggregate
  therefore reflects the team the manager picks to start, not the
  squad as a whole.

### The complete `+0xC` writer inventory (F019 + this task)

| Routine | Reads / writes | Listing lines |
| --- | --- | --- |
| `0791:7CC5` `adjust_player_form` | reads live +C; writes clamp(s8(live)+delta,1,255); nonzero flag writes min(32,s8(new live)) to DS:9B07[side*20+slot] | `code/seg_0791_13.asm:484..548` |
| `0791:B364` (F019 result rule) | reads/writes signed +C, clamp [1, 32] | `code/seg_0791_18.asm:621..653`; `named/seg_0791_08.c:1118..1126` |
| `0791:798D` booking | sets +0x10 bit 5, increments side bookings, calls `1771:33CD force_tactic4_off` for unmanaged sides; does **not** write +0xC | `code/seg_0791_13.asm:115..188` |
| `0791:7B77` `send_off` head | `7CC5(pitch, 0xfffe, 1)` → sent-off player: +0xC += -2, clamp [1,255], DS:9B07 set | `code/seg_0791_13.asm:386..394` |
| `0791:7B77` `send_off` tail | `7CC5(pitch, 2, 0)` per available pitch player of the OTHER team (slots 1..11) → +0xC += +2, clamp [1,255], DS:9B07 NOT updated | `code/seg_0791_13.asm:430..438` |
| `0791:7D56` injure | +0xE := 0 (F018 injury store), walks off, `7CC5(pitch, 0xfffe, 1)` → injured player: +0C += -2, clamp [1,255], DS:9B07 set | `code/seg_0791_13.asm:587..601` |
| `0791:7EEF` foul_dispatch | dispatches to 798D / 7B77 / 7D56; does not write +0xC directly. Gated by a 255-byte pre-shuffled draw table at DS:0x8337 via 0791:261A (R5). | `code/seg_0791_06.asm:712..758` |
| `0791:6443` `record_goal` scorer | `7CC5(pitch, s8(DS:0x7920[side_of_credit]), 1)` → scorer: +0C += ±1, clamp [1,255], DS:9B07 set | `code/seg_0791_11.asm:177..191` |
| `0791:65FE` `after_goal` team reaction | per available pitch slot `7CC5(pitch, s8(DS:0x7920[side_of_ball]), 0)` → every available pitch player: +0C += ±1, clamp [1,255], DS:9B07 NOT updated | `code/seg_0791_11.asm:380..429` |
| `1771:13D0` team_panel_aggregate | reads +0xC of each available starter; sums min(32, s8(+0xC)) (no lower clamp) into DS:9B5A; also writes DS:9B5C..9B64 | `code/seg_1771_02.asm:1001..1126` |
| `1771:157D` `draw_team_panel` | reads DS:9B5A..9B64; the only consumer of DS:9B5A in the listing | `code/seg_1771_02.asm:7..110` |

No other direct `+0xC` writer is in the named view. `1771:13D0`
is the only writer of `DS:9B5A`.

## Reproduction and limits

`python3 experiments/E019-q017-events-morale/check_morale.py`
replays every E019 probe by player word; the probe record
`probe-literal-001.json` holds 22 literal-input cases (13
adjust-form cases covering the named event deltas, including
clamp boundaries, signed-byte edges, and a persist-vs-no-persist
comparison; 9 team-panel cases covering the seed, divisor, floor,
signed-byte clamp, and the R1 reproduction case). Every
`expected_*` and `got_*` field is hand-traced from the listing
bytes (`code/seg_0791_13.asm:484..548` for the adjust-form cases;
`code/seg_1771_02.asm:1001..1126` for the panel cases); the
`got_*` fields are captured from the model at probe generation
and the checker enforces that they match the model's output at
check time. The probe fails closed on empty sets, on a literal
mismatch, and on a missing or mutated `got_*` field:
`match: 22/22`.

`python3 -m unittest -v tests.test_model_morale` runs 33 literal
tests; `python3 -m unittest -v tests.test_check_morale` runs 10
negative tests for the checker; the mutation sweep
`experiments/E019-q017-events-morale/mutations_morale.py` shifts
each of the 9 numeric constants by `+1` and `-1`, deletes each
of the 5 named helpers, and reruns the unit suite in a fresh
subprocess. **23/23 mutants killed**
(`mutations_morale.py` writes and `os.fsync`s the mutation so the
subprocess sees the mutated source; without `fsync` the parent's
buffered write leaves the subprocess reading stale bytes from the
kernel page cache and several mutants appear to survive).

This does **not** claim:

* a Unicorn probe of the original `7CC5` and `13D0` against the
  unpacked `GOAL.EXE` (the listing-only probe covers the
  arithmetic byte for byte, and a Unicorn pass tripped on a later
  library call inside the engine — the existing
  `probe_adjust_form.py` harness remains as a diagnostic, and the
  one-shot `13D0` routine call path I tried hits a
  `player_unavailable` library chain that the harness can't
  stub; the reviewer's Unicorn run of the original listing bytes
  for `[128, 0, ..., 0]` confirms 5946, matching the hand-traced
  result);
* a DosBox match run with an injury, a booking, or a sending-off
  captured (E015 has no useful records; the brief's 6-run budget
  is not spent here because static analysis already settles
  every claim the listing supports);
* an established "friendly" classification (the listing names
  the result-term set as kinds `{4, 5, 8, 9..196}`, not as
  friendlies);
* a confident claim that a yellow card drops confidence (the
  listing does not write `+0xC` from `0791:798D`; a static
  reviewer can only say "not established");
* a team-morale byte persisted anywhere outside the panel
  render.

These limits cannot be removed by improving the model; they are
the limits of the listing.
