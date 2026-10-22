# E039 notes (T83, #369)

1. **Static.** The date: `214B:206A` (unit start-up, `0000:000A`) ends with `call 0x1c63` (`seg_214B_04.asm:443`);
   `214B:1C63` passes `DS:A9FD` and three locals to `GetDate` `235C:006C` (`seg_214B_03.asm:1084`), which runs
   `mov ah, 2Ah; int 21h` at `235C:0071` (`seg_235C_01.asm:99`). `calls.tsv`: `235C:006C` has one caller. `datarefs.tsv`:
   `DS:A9FD` is touched by `214B:1C63` and `1771:9B85` only. `1771:9B85` (`seg_1771_14.asm:385`): year + 1, + 1 if
   odd, at `[A923]+3A`; `+40` = (`+3A` mod 4 = 2); `+3C` = `DS:118E[+40]` (`02 05`, read from E038's state).
2. **Catching.** At `cycles=30000` the savestate polls are 0.58 s apart and the start-up before the date read is
   shorter than that: of five launches with `--first-save` 0.2–0.4 s, two caught (r0005, and one before amendment 2),
   the rest saw DOSBox-X's BIOS and then the title. The probe of T83 (scratch, no record) caught `214B:1DE4` once.
3. **derive.py** from r0005 (load+2382:0074): 3 ticks modelled, INT 21h AH=25h (vector 1Bh, the CRT unit's Ctrl-Break)
   and INT 10h AH=02h ×2 (`Intr` from `214B:0661`), stop at `235C:0071` with AH = 2Ah. `DS:A9FF` 4279 (DOSBox-X at the
   same cycles: 4275 in r0001 and r0002). Port I/O: none. Text page: not written.
4. **trace.py**, 1990 and 1992: the date call, then nothing but polls and speaker ports to the title's read; then
   F032's path. `summarise.py` 6 of 6 per date; `compare` at the manager menu as F033 says. The extra difference for
   1992 is DOS's own date copy at linear 07C70: `04 10 00 05 49 07 [wd] 2c fe 05 [year lo hi] 0a 04 …` (weekday at
   07C76, year at 07C7A, then month and day), 1990 in the derived state.
