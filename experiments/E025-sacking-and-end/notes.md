# E025 Sacking and the end of the game (T51, F025)

Static only. No game run, no hook, no savestate. Reproduce the searches:

```sh
python3 -B experiments/E025-sacking-and-end/searches.py > /tmp/searches.log
diff /tmp/searches.log experiments/E025-sacking-and-end/searches.log   # no output
```

`searches.log` is the committed output; it is never overwritten (a new run of the script goes to another file).

## Reading order (what was read, in order)

1. `named/seg_000E_04.c:388` (`000E:4E0E`): the sack flag looks constant 0 in C. The listing `seg_000E_06.asm:549-725` shows `mov byte ptr [bp - 2], 0` at `:557` and a test of it at `:708` before the call of `000E:01FA` at `:719`.
2. The nested routines `11D9`, `4DB7`, `26F2` receive `4E0E`'s `bp` (`push bp` before each call). Search "stores through `ss:[di - 2]`" over all code: in segment `000E` only `seg_000E_04.asm:825` (inside `000E:319B`, reached from `4DB7`, whose static link is `4E0E`'s frame) writes 1; `seg_000E_08.asm:1049/1200` belong to the fixture gate `6C21`.
3. `seg_000E_04.asm:133-825` (`319B`): branch tree on the fixture winner byte `+3` against the side, then `+3 == 2`, then score bytes equal, then `call 0xb77` and the compares at `:756-806`. The pascal strings at `CS:2E94..3118` give the headline texts.
4. `seg_000E_02.asm:146-196` (`000E:0B77`): the score and its four gates. `1771:59D8` set bytes at `seg_1771_08.asm:735` (`98 01` = {3, 4, 7, 8}; bit i of byte i/8, the same decoding as `CS:80BA` = 0x24 = {2, 5}).
5. Who writes the score: `seg_000E_09.asm:296-352` (`6CA7`) calls `0791:B71C` then `0791:B6CC` for both sides; `seg_0791_18.asm:979-1007` (`B6CC`, clamp -127..127); the fold `seg_1771_09.asm:946-960` (`63A4`), reached from `6730` only when the year word is above 0 (`seg_1771_09.asm:1111-1113`).
6. The shareware limit: `seg_000E_09.asm:448-470` (`7072`), its users at `:493` (`70B9`), `:718` (manager screen, `721E` with `DS:19D6`), `:1175` (menu item 6); `seg_1771_12.asm:136-154` (`8208`); `seg_1771_01.asm:1015-1017` (`090F`).
7. Year display: `seg_000E_07.asm:555-566`, `seg_1771_08.asm:942-957` (`2 * word + [+0x3A]`).
8. Terminal conditions: `searches.log` blocks 3-5 (state accesses, constant tests, Halt callers).

## Searches that came out empty or negative (for "never" claims)

- Stores that set the sack flag of `4E0E`: one (`seg_000E_04.asm:825`).
- Calls of `000E:01FA`: one, near (`seg_000E_06.asm:719`); no far call.
- Compares of the year word against anything above 2, or of `+0x3A` against anything: none.
- Mode-2 callers of `1771:26B9` (the country picker that assigns a country): `1771:2D15` only (`searches.log`, last block). The calls from `000E:7439` push 1 and 3, `1771:7AAB` pushes 4.
- Writers of `[A923]+m+1`: none found by direct stores (see F025, Limits). The searched forms: `mov byte ptr es:[di], 1` and `[di + 1], 1` within 14 lines of `les di, ptr [0xa923]`: hits `seg_000E_09.asm:483` and `:1188` (`[A923]+1 := 1`); `mov byte ptr es:[di], al|cl` within 16 lines of such a load: none.
- Readers of country byte `+0xBE`: one (`seg_000E_02.asm:179`); writers: none by an explicit displacement.

## Strings used

`CS:2E94..3118` headlines (pascal strings in `seg_000E_04.asm:66-118`): `THINGS LOOK GRIM` `3086`, `YOUR JOB IS` `3097`, `ON THE LINE!` `30A3`, `IS SACKED!!!!` `30B0`, `UNLUCKY TO LOSE` `30BE`. `strings.tsv:1076-1089` the `DS:591E` template (" GOAL ", " NE'93 ", "  Tough luck.  ", "You have ", "been ", " SACKED ", "for ", " incompetence "); `strings.tsv:746-754` the `DS:19D6` template (the shareware notice).

## Round 2 (review R1-R5)

- `searches2.py` / `searches2.log` (new; `searches.log` is kept unchanged) list every instruction with displacement 0x38, 0x3A or 0x3C (any base register) and every `add reg, 0x3X`. Classification of the `es:[di + 0x3c]` hits on `[A923]`: set-membership tests (`seg_000E_09.asm:500` 70B9, `seg_1771_08.asm:744` 59D8, `seg_1771_12.asm:24` 80DA, `:156` 8208, `:694` 876A, `seg_1771_13.asm:762` 93B6, `:991` 95F4); dispatch `seg_1771_11.asm:11` (76B1); class selectors (`seg_1771_08.asm:1017`, `seg_1771_09.asm:634`, `seg_1771_12.asm:140,166,176,188,704,727,787`, `seg_1771_13.asm:118,611,963,968`); stage pushed as fixture kind `seg_1771_09.asm:1506` (6B23); kind compare `seg_1771_12.asm:286`; writers: `seg_1771_14.asm:429` (new game) and `seg_1771_12.asm:145` (`add di, 0x3c` for `214B:1D6F`). The `mov dx, 0x38` / `mov ax, 0x3X` hits are multiplications by the group-row size 0x38 and other constants, not field accesses.
- Year word `+0x38`: compares with 0 or 2 only; reads for display and `(word+1)*[+0x26]` (`seg_0791_04.asm:728`); one increment (`seg_1771_12.asm:34`), one init (`seg_1771_14.asm:407`). Displayed year `+0x3A`: store `:397`, parity round `:399-403`, modulo-four start decision `:409-414`, display reads.
- Worked B71C examples (R1) follow `seg_0791_18.asm:1030-1102` by hand: q = idiv32(opp - own); non-draw winner adds the margin, loser subtracts; doubled when (winner == side) equals (side == 0 or kind in DS:0F3E).
- `[A923]+m+1` is the manager's group number: `seg_000E_08.asm:79-84` (0 -> `5E6C`), `:109` (`mov dx, 0x38`, the group-table row size).
- `5E6C` draws one random number: `seg_000E_07.asm:1010-1012` (`214B:06B1(3)`).
