# E038 notes (T82, #367)

## 1. Why the `title.sav` checkpoints are refused (static, then the run)

The title is `1771:080C` (`static/goal-exe/code/seg_1771_01.asm:897`): it draws the screen and the prompt
"Do you want to load a saved game? (Y/N)" (`1771:07C4`, through `214B:0350`), copies the screen (`23E4:025D` at
`0852`), then calls `1771:07B4` (`:934`), which runs the animation `1771:06F3` (`:887`): `DS:7968` from 4 to 0x0C,
each round 24 cells then 13 cells drawn by `214B:1EF1` (`:849`, `:870`), each preceded by a "key pressed?" poll
`214B:0723` (`:820`, `:858`) that leaves the animation when a key waits. `214B:1EF1` waits in CRT `Delay`
`214B:1E09` (`seg_214B_04.asm:75`); the checkpoints' CPU at load+214B:1E3E–1E44 is that delay loop
(`seg_214B_04.asm:98`–`101`). After the animation, `214B:1E8D` and then `call far 214B:08DD` at `1771:085A`
(`:935`): the blocking read (`08DD` calls `Intr` `235C:000B` with AL = 16h, AH = 0, at `08FF`,
`seg_214B_02.asm:23`). So a state taken once the animation is over is in the read.

The scratch probe (not a record) polled a fresh launch: CPU at load+214B:1E33–1E4A for 11.9 s, then at
F000:CFA1–CFB2 (the BIOS's INT 16h wait loop) from 12.4 s on. In E038-r0001, whose savestate polls slow the guest,
the state in the read came 24.9 s after the title appeared.

`cycles=30000` (E006's) crashed DOSBox-X 2024.03.01 at the first savestate in this cloud session (signal 11, twice;
`cycles=max` and the clock option alone did not); the run uses `cycles=max`, the driver's default and the
checkpoints'. Not investigated further.

## 2. The run (E038-r0001)

Every kept state but the name entry has the CPU in F000 (CFA1–CFB1) and exactly one frame of 08DD's `Intr` call
above SS:SP; the record holds the registers, the frame and the callers. The name entry (`214B:0D90`,
`seg_214B_02.asm:608`–`617`) loops on "key pressed?" and reads the BIOS tick count for the cursor's blink; it calls
08DD (`214B:1128`, `:972`) only when a key waits, so its state (CPU in `235C`, inside `Intr` on the way back from the
INT 16h AH=1 call) is not a read state; goal2's core refuses it, as it should.

## 3. The trace (`trace.py`, `out/trace-r0001.*`)

From `e038-title-load-prompt-r0001.sav`, keys `6E 0D 0D 62 6F 62 0D 0D 0D` answered at 08DD; the name entry's poll
`214B:0DB9` answered "a key waits" while keys remain (every other poll "no key"; there were none). DOS time served
10:00:20.95, the value the DOSBox-X run's `DS:7B64` shows it read (`0x145F`). End: the read at `000E:75D1`
(the manager menu). Its end against `e038-manager-menu-r0001.sav` (`compare` in the JSON): the screen's 4000 bytes
equal; `DS:7B62` `EE42` and `DS:7B64` `145F` equal; the player array (F007) and the country array equal byte for
byte; in 640 KiB of conventional memory the only differences are the BIOS keyboard buffer (0040:001A–0040:002F, the
keys DOSBox-X typed), the tick count byte 0040:006C, one word at 0815:000E (DOS's own save of the caller's stack in
GOAL's PSP, `0813:002E`, written by every INT 21h in DOSBox-X), and stack bytes below the read's SP
(SS:3B8F–3EE7, below SP 3EEA: what the BIOS and DOS handlers pushed in DOSBox-X). `summarise.py` checks each
intermediate read's site, callers and screen against the record: 6 of 6 equal.

The served set is therefore enough for this path: nothing else the guest reads differs.
