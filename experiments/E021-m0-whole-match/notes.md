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
