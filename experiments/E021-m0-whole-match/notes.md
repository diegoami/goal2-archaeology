# E021 m0-whole-match — reading notes (T38, milestone M0: whole watched matches in the emulator)

Addresses are `segment:offset` (image paragraphs, as the listings write them); listings are
`static/goal-exe/code/seg_*.asm`, read after the named view `static/goal-exe/named/`. Append-only.

## 1. The entry: the start point and the start state

**Where a watched match starts** (`named/seg_0791_11.c`, `run_match`; `code/seg_0791_23.asm`):
`0791:F1F6` calls `0791:A4A1` (match set-up: the commentary ring reset, the kick-off side drawn
through `214B:06FA`, F005) at `F201`, then the team screen `0791:ED8A` with argument 1 at `F207`,
copies the morale snapshot and sets performance 0x37 for slots 1..11, then calls the match proper
`0791:F098` at `F2E0` (`seg_0791_23.asm:1043`, `:1046`, `:1133`). `F098` (`play_match`) runs the
first half `998C` (which sets the clock `DS:831B = 0x5B`, `DS:8319 = 0x2D`, the kick-off slot, the
opening commentary, then `983F`), the end-of-half walk-off `9955`, the pre-half sequence `9A32`
(which ends in the second half's `983F`), and after the score store the full-time walk-off `9955`
(`named/seg_0791_11.c`, `play_match`; `named/seg_0791_07.c`). After `F098` returns (`F2E3`),
`F1F6` picks the man of the match (`CAB0`), calls `15B9`, and draws the full-time board
`0791:0106` with argument 1, which waits for a key (`seg_0791_01.asm:040F`-`0415`,
`call far 214B:08DD`): the "hit any key" board E011's records read as "full time".

**The published state before the kick-off**: each E011 ground-truth record has two outputs on
release E011: `E011-r000N-watchstart.sav` ("captain screen (the watched match's start state)" in
the record) and the half-time stall. The watchstart state is before the kick-off: its clock reads
`(831F, 831D, 8325) = (0, 0, 0)` and the score 0-0 (the records' observation "captain screen ...
clock"), and the record's keys from it are the starting burst `Enter Right×5`, then one Enter on
`hit any key` (half time) and one on the team screen. So no state had to be staged: **no DOSBox-X
run was taken**.

**Where the guest stands in that state.** The savestate's `CPU` component (zlib, like `Memory`)
holds the registers. Its layout is calibrated here, not from a finding, on the four E011 states:
the eight 32-bit general registers in the order EAX ECX EDX EBX ESP EBP ESI EDI at stream offset
0, EIP (32-bit) at 0x20, the flags (64-bit) at 0x28, and the six segment values ES CS SS DS FS GS
as words 8 bytes apart from 0xEB. The calibration's checks: DS = 0x2DA4 equals the data segment
`savestate.Program` finds by the MCB (load segment 0x0823 + 0x2581); CS:IP = 0x296E:1E46
(r0001) and 0x296E:1E44 (r0002) are `214B:1E46` and `214B:1E44`, two instruction boundaries of
the busy-wait loop in `214B:1E09` `u214b_delay_ms` (`seg_214B_04.asm:100`-`103`), and the flags
0x7246 have ZF set as `1E40 cmp dx, [0xAA01]` / `1E44 jne` leave them for r0001's `1E46`; and the
BP chain from SS:BP = 0x3875:3E48 returns, frame by frame, to call sites of the listing:
`0791:CC65` (after `CC60 call far 214B:1E09`, in `CC2E` `wait_or_key`), `0791:CED9` (after
`CED6 call 0xCC2E`, in `CC7B`, with the argument 1000 on the stack), `0791:21AD` (after
`21AA call CC7B`, in `20E3` `assign_marking_slots`), `0791:2609` (after `2606 call 0x20E3`, in
`230C` `resort_pitch_and_bench`), `0791:F092` (after `F08F call 0x230C`, the last call of
`ED8A`), `0791:F20A` (after `F207 call 0xED8A`, in `F1F6`), and far to `000E:6F1D` (the fixture
router, which calls `F1F6`). The half-time states decode to CS:IP = F000:CFA9 (the BIOS's
INT 16h wait), consistent with E011's "stall in the team screen's key wait".

So the captain screen is `0791:CC7B` with argument 1 (`named/seg_0791_10.c`), which `20E3`
calls for a managed side once `DS:0C1F` is set (`ED8A` sets it at `F08A`, just before its final
`230C`) when the player word at `DS:9978 + 10·side` is unavailable (`1771:3216`) or `6B65(1, side)`
is above 0x0B (`named/seg_0791_02.c`, `assign_marking_slots`). It shows the screen, then
`wait_or_key(1000)` (`CC2E`: up to 1000 × `214B:1E09(10)`, stopping when `214B:0723` reports a
key), then reads a key if one waits (`CED9`/`CEE8`); Enter accepts the player under the cursor.
The state was saved inside that wait.

**The harness's start point is therefore the guest's own CPU state in the watchstart savestate**
(registers, flags and segments from the `CPU` component, memory from `Memory`): emulation resumes
at `214B:1E46` (r0001) / `1E44` (r0002) inside the captain screen's wait, with the starting
burst's Enter queued, and runs as guest code through the rest of `CC7B`, `20E3`, `230C`, `ED8A`'s
tail, `F1F6`, `F098` (both halves, the half-time sequence, both walk-offs), `CAB0`, `15B9` and
`0106`, and stops at `0106`'s key wait for the full-time board. No routine is entered by the
harness with a made-up stack: every return address is the guest's own. What already ran before
the start state: `A4A1` (the kick-off side's draw is in the state's `DS:7B62`) and the team
screen's loop; so an input written into the start state (§3) does not redraw the kick-off side.

## 2. Whole matches: the run, the half-time waits, the interventions

`runtime/emul/watched_match.py`'s `WatchedMatch(state).run()` resumes the start state (§1) and
runs to the full-time board as guest code. The interventions, and nothing else:

- **interrupts swallowed** (`UC_HOOK_INTR`), as `watched.py`;
- **the key thunk `214B:0723`** answers "no key" whenever no key is queued; the only queued key
  is the starting burst's Enter for the captain screen (the state stands in `CC7B`'s
  `wait_or_key(1000)`, which polls `0723` between `214B:1E09(10)` delays: `CC4F`, `CC60`;
  then `CED9 call far 214B:0723` and `CEE8 call far 214B:08DD`, `seg_0791_20.asm:1063`, `:1072`,
  `:1342`, `:1348`);
- **the key read `214B:08DD`** (it waits through `INT 16h AH=0`, `08FF call far 235C:000B`,
  `seg_214B_02.asm:6`-`82`) is answered only at the stopped screens E004's discipline answers,
  with the key it sends there, by storing it in `DS:A976` and `DS:A977` (what `0947` and `097C`
  store for Enter) and returning as its `retf`: the queued Enter (captain screen), for the read whose return address is `0791:CEED` only (`CEE8 call far 214B:08DD`, `seg_0791_20.asm:1348`; review R2: a read from any other return raises with the key still queued); the half-time
  board; the half-time team screen. A read anywhere else raises `KeyWaitError` (the run is void);
  a read with the pushed-back flag `DS:79AE` set runs as guest code (`08E3`-`08EF`: no wait);
- **the `000E` wait family** skipped and logged (its returns read from the listing: all four are
  near, `ret 6`, `ret 2`, `ret 4`, `ret 4`), the log empty in every run;
- **one declared write**: the delay byte `[DS:A923]+0x3F` := 0 (§3).

**The half-time stall, handled as E004's discipline makes the original handle it.** After the
first half (`998C` → `983F`) and the walk-off `9955`, `9A32` (`named/seg_0791_07.c`,
`pre_half_sequence`) adds the energy step, draws the half-time board `0106(1)`, which waits for a
key at `0415 call far 214B:08DD` (`seg_0791_01.asm:476`): E004's "hit any key" Enter, delivered
there (the read returns to `0791:041A`). `9A32` then tests `DS:80FD` and the key `DS:A977` against
`CS:9A12` = {13, 27} (`9AC6`-`9ADB`); with the Enter in `A977` the team screen `ED8A` runs
(`9AE0`). Its menu loop reads its key through `214B:1560` (`EE9A call far 214B:1560`,
`seg_0791_23.asm:686`; `1579 call 0x8DD`, `seg_214B_03.asm:279`): E004's team-screen Enter,
delivered there (the read returns to `214B:157C` inside a `1560` called from `0791:EE9F`), on the
menu's default item ' play ', which leaves the loop (`local_3 = 1`, then `EA09`); `ED8A`'s tail
(`F08A` `DS:0C1F = 1`, `F08F call 0x230C`) and `9A32`'s own tail (`9AE3`-`9B05`: the one-byte
kick-off slot store, `DS:832A = 0x50`, `call 983F`) run as guest code. Nothing of the second
half's start state is written by the harness: the first half's end flows into the second.

Every run's key log is exactly these three: the captain screen at clock (0, 0) with the seed
0x9115, the half-time board and the team screen at clock (46, 36) with the seed 0xF457
(`out/*-none-E011-r000N.json`, `key_log`). The full-time board is the stop: the next read at
`0791:041A` after `F098` has returned to `F1F6` (`F2E3`) ends the run (`stopped_at_board`).

Corroboration (`halftime_compare.py`, `out/*-halftime-compare-*.json`, `out/halftime-compare-20261011.log`):
at the team screen's read the emulated clock and seed are (46, 36, 0xF457), the E011 half-time
states' own values, and of the 65536 bytes of the data segment 68 differ from the E011 half-time
state's: `DS:8336-8337` (the speaker stream's word, which the delay byte gates, `0791:94E8`),
`DS:8B31-8B32` (not identified: no listing operand names it), and 64 bytes at `DS:EA48`-`EB9B`,
which is the stack (SS = DS + 0xAD10, so these are `SS:3D38`-`3E8B`: the emulation stops inside
`08DD`'s entry, the savestate inside the BIOS's INT 16h).

## 3. Inputs: declared writes into the start state

`WatchedMatch.write_input(what, linear, bytes)` writes guest memory before `run()` and records
the write (what, linear address, old and new bytes) in `inputs`, which every output carries (an
I3 intervention). The named ones:
- `set_seed(v)`: the main seed word `DS:7B62` (F004);
- `set_country_tactics(country, v)`: the country's `+0x2D`, at `[DS:A917] + 0xBF·country + 0x2D`
  (F007's array, F010's field);
- `set_player_bytes(player, offset, bytes)`: any bytes of a player record, at
  `[DS:A91B] + 0x14·player + offset` (F007, F008/F015, F021: `+4`, `+5`, `+7`, `+0xC`, `+0xE` ...);
- `set_squad(country, words)`: the country's 20 squad words at `+0` (F007), the squad order;
- `set_delay(v)`: the delay byte `[DS:A923]+0x3F`. `run()` declares `set_delay(0)` unless the
  caller declared another value: the starting burst's five Rights, which the original reads at
  the first key polls of the match (`0791:9372`: key code 0xAF lowers the byte down to 0,
  `named/seg_0791_07.c`; the records read 1 at the captain screen and 0 at full time). The byte
  is read by `9372` (the speed display), `94E8` (whether the speaker stream draws twice, the
  second stream `DS:8336`, not the main seed) and `0425` (the busy-wait `214B:1E09`); none of the
  three writes `DS:7B62`, so the write changes no main-seed draw; it saves the emulation the
  delays.

The start state is after `A4A1` (§1): the kick-off side is drawn already, and the teams' pitch
records were bound before the team screen. A squad or player write reaches the match through
what reads it after the start: `ED8A`'s final `230C` (re-sort, `bind_pitch_player`), `20E3`, the
engine's reads of the records. Which reads those are is milestone M1+ material.

**The input run** (Done-when 3; `input_run.py`, `out/*-input-tactics-side0-xor01-E011-r0001.json`):
from E011-r0001's start state, country 7 (engine team 0, `DS:9B34`) `+0x2D` 0x8B → 0x8A (element
1, position, cleared), declared. The run completes to the full-time board (score 1-1, strays none,
the three declared keys). Its seed writes are the unchanged run's for the first 971 (#0..#970);
write #971 has the same values but falls under the clock reading (1, 30) where the unchanged run
makes it under (1, 31): a tick of minute 1 ended earlier, so the first tick whose seed value leaves
the unchanged run's trajectory (F013's rule) is minute 1, sub-tick 30 (value 0x481A is not among
the 43 values the unchanged word takes there).

## 4. Outputs at full time

`WatchedMatch.outputs()`, written by `check.py` and `input_run.py` under `out/`:
- the score `DS:9B3C`/`9B3D` per engine team, the clock and the seed at the board;
- the scorers, per engine team t, from the list `0106` draws: player word, name and the minute
  byte raw (`0106`: `0x7BD1 + 0x21·t + 3·k`, k = 1..11; a byte >= 0x81 is drawn with another
  mark, not named here);
- the man of the match `DS:7C3A` (F014) with the name;
- the board's numbers RAW, per engine team: the bytes `DS:7B7E + 10·t + k`, k = 0..8, and the
  words `DS:80F2`, `DS:80F6` (and +2), each with the label the emulated board shows in the row
  `0106` draws it in (row k + 9, rows 0x13/0x14): Corners, Free kicks, Penalties, Shots,
  On target, Saves, Fouls, Bookings, Red cards, Possession, Territory. Only the row is read from
  the code; what each counter counts is not established (raw);
- the commentary ring oldest first (`commentary.py`'s layout), raw and as text, with the count of
  `1D4A` entries;
- the board's text screen (80×25, from the text page at the far pointer `DS:A96A`) and its sha256;
- the main seed's writes with the clock (`draws`; the output files carry their count and sha256);
  the key log, the stray log, the declared inputs, the hooked-call counts.

## 5. The substitution hook

`Guest.hook(address, fn, ret=None)`: a code hook at the routine's entry (the address relocated
by the load segment) runs `fn(guest)` — which reads and writes registers and memory through the
guest (`arg(i)`, `word`, `set_word`, `reg`, `set_reg` ...) — then returns as the routine's own
return would: `ret` = (far, bytes popped), read by default from the routine's block in the listing
(`routine_return`: every `ret`/`retf` of the block must agree; `214B:0688` gives `retf 6`,
`seg_214B_01.asm:894`). The guest's routine is not executed; `hook_counts[address]` counts the
calls. Every write the fn makes to the seed word through the guest (`put`, `set_word`) is
recorded at write time like a guest write (`watch_word`), a write later undone and a same-value
write included, and a change made around `put` is recorded when the fn returns (review R1), so a
hooked step's writes are what the trajectory check sees, not the true LCG's. `check.py` also runs
each hooked match unhooked and requires the two seed-write traces to be identical, write for write
(value before and after, clock reading): the reads alone cannot see an extra value, since a
checkpoint only asks for membership; `--hook f004+hidden-write` (0xDEAD written and restored
before each F004 step) is that check's falsifier.

The proof (Done-when 2): `check.py --hook f004` hooks `214B:0688` with F004's step in Python
(`seed = seed · 0x7ABD + 0x1B0F`, stored; AX = DX = 1 + (seed · n) >> 16,
`seg_214B_01.asm:873`-`894`); `--hook f004-mult+1` and `--hook f004-inc+1` change the multiplier
or the increment by one. `tests/test_emul_match.py` pins the mechanism: on a synthetic guest the
hooked routine's own instructions never execute and the count is exactly 3; on the real start
state 40 clock ticks call `214B:0688` 1558 times, its second instruction never runs when hooked,
and the seed writes and tick marks equal the unhooked run's.

### 5a. The side-by-side proof (review round 2; T38 Done-when 2 as amended on main, ae8bf4e)

The round-1 checks proved the main seed's sequence, not the model: a model could write anything
else, or write the seed with raw Unicorn calls, or step another seed word wrongly, and the match
could still reproduce (Sol's three falsifiers). `Guest.hook(address, fn, prove=True)` now proves
the model at every call, side by side with the original:
1. at the routine's entry the harness snapshots every register (`REGS_ALL`) and lets the ORIGINAL
   run as guest code, recording every write (address, old bytes, new bytes) through a memory-write
   hook on the whole address space (one for the run, recording only during a proved call); the main-seed trace ignores these
   guest writes (`suppress_guest_watch`), since they are undone;
2. at the routine's own return instruction (from the listing: `214B:06AE retf 6`), with SP back
   at the entry's value, it takes the return state (`return_from` as that `retf`), undoes the
   writes in reverse order and puts the snapshot's registers back;
3. it runs the model on that state with `mu` replaced by a recorder (`_RecordingUc`), so every
   write the fn makes — through `put`/`set_word` or `guest.mu.mem_write` itself — is recorded
   byte by byte in order (and reported to the watched seed word at write time);
4. it compares: the written bytes, in order, address and value, and the registers `REGS_RETURNED`
   after the return. The first difference raises `ProofError`: "call #k of 214B:0688: written byte
   #i differs: the original wrote 0xNN at linear 0x... (DS:xxxx), the model wrote ...", or the
   register. Otherwise the call counts in `proved_calls` and the match continues from the
   model's state.

Two declared limits of the comparison, both from the calling convention, not from the routine:
- **bytes written inside the routine's own stack frame are not compared**: SS below the caller's
  SP after the return (the return address and arguments the `retf 6` pops, the saved BP and DS,
  the pushed SI/DI pointer, the local word `[bp-2]`, `seg_214B_01.asm:873`-`893`). They are dead
  once the routine returns (the next push of the caller overwrites them), and a model of what a
  routine computes does not rebuild its frame. The same rule applies to both sides, so a model
  that writes into that region is not credited either. A later routine reading an uninitialised
  local would see the model's (pre-call) bytes there, not the original's; the whole-match checks
  (every read, the full-time state, the seed-write trace against the unhooked run) are what would
  catch that, and they stay in force;
- **registers compared at the return**: AX and DX (the Turbo Pascal result registers; 0688 leaves
  the result in both, `06A4`-`06A8`) and SP, BP, SS, DS, CS, IP (what the caller relies on). BX,
  CX, SI, DI, ES and the flags are scratch across a call in that convention and are not compared
  (0688 leaves BX = 0x7ABD and SI/DI past the seed word; no model is asked to reproduce that).
  A difference in any of them at a proved call's return is a WARNING, not an error (the owner,
  2026-10-11, accepting both limits): counted per register in `scratch_differences`, the first
  one per register printed to stderr, and the counts printed in `check.py`'s summary line
  "uncompared-register differences (warnings, proved calls): BX n, CX n, ...".

`check.py --hook NAME` hooks with `prove=True` and prints the hooked calls, the calls proved with
no difference, and the differences. The falsifiers: `f004+raw-write` (raw `mu.mem_write` of
0xDEAD to the seed, restored), `f004+831D-write` (0xDEAD written to DS:831D, restored),
`f004+inc+1-off-seed` (the increment + 1 only when the seed pointer is not DS:7B62: DS:8336), and
the earlier `f004+hidden-write`, `f004-mult+1`, `f004-inc+1`; each stops at its first wrong call.
