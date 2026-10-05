# F002 GOAL.EXE unpacks to 185,216 bytes of Pascal-style real-mode code that can be listed and indexed by area, and GOAL.DAT is ten consecutive blocks read in a fixed order

- **Status**: proposed
- **Question**: Can `GOAL.EXE` be unpacked and disassembled reproducibly from public format knowledge alone, can its code be indexed by the areas of `knowledge-map.md` from strings, calls and data references, and can `GOAL.DAT`'s structure be proposed from its bytes, each claim with its offsets? (T04, G3)
- **Tests claims**: R001, R002, R003, R004, R005, R006, R007, R008, R009, R010, R011, R012, R013 (proposed here; `spec/representation.md` has no rows yet)
- **Experiment and runs**: none. Static analysis only; the artifact was never run. No `runs/` or `evidence/` record exists for this finding.
- **Artifact**: set `goal2-a949da2f`, variant: none (the original files, from release `goal2-original`)
- **Max intervention**: I1 (static analysis, `vocabulary/interventions.md`)
- **Tier reached**: V0 (nothing was run; every claim is about bytes and listed code, which a reviewer can re-derive from the released files with the commands under Reproduction)
- **Confidence**: unreviewed (status `proposed`) — `static:static/goal-exe/code` and `static:static/goal-dat/blocks.tsv`, one method (capstone listing plus the byte checks of `tools/static/goaldat.py`), 11 of 11 byte checks agree, the unpacker is tested on a fixture the tests generate and the unpacked file is consistent in the ways listed under Alternatives; the code-to-area map has 27 inferred rows (named under "What this does not establish")

## Answer

- `GOAL.EXE` (packed sha256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`, 92,391 bytes, LZEXE 0.91) unpacks with `tools/static/unlzexe.py`, written from the public format, to a plain MZ file of **193,408 bytes, sha256 `6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188`**; running it twice gives the same hash (Observations O1). `static:tools/static/unlzexe.py`
- The unpacked code is listed reproducibly: `tools/static/regenerate.sh` rewrites `static/goal-exe/` byte for byte with capstone 5.0.9 (O2). 726 routines, 57,508 instructions and 142,044 of 153,616 code-segment bytes were decoded; the rest is strings and tables. `static:static/goal-exe/README.md`
- `GOAL.DAT` (44,040 bytes) is **ten consecutive blocks** whose sizes are the ones the game's loader reads in order (`1771:018A`); they add up to the file size, and the content changes character exactly at each boundary (R001; O3, O4). `static:static/goal-dat/checks.txt`
- The blocks hold: 128 country names (R002), 3,060 player surnames (R003) and initials (R004), 128 manager surnames (R005) and initials (R006), three small values per country (R007), one byte per country (R008), two permutations of 0..128 (R009, R010) and a squad table of 20 bytes per country (R011). The squad `c` takes player names `(c-1)*20+1 .. c*20` (R012). The file holds no per-player skill values (R013). `static:static/goal-dat/checks.txt`
- The map in `static/goal-exe-map.md` places the executable's routines in: data files and saves, the help viewer, countries, the squad, team comparison, positions, tactics, match commentary, discipline, fixtures, tours, the manager names, press text on sacking, and the several-human-players slots. It does not place the match engine's moving simulation, the skill and attribute numbers, ageing, fitness numbers, strength of each country, how rankings are set, how the computer teams choose, the shareware limit's routine, or `ALTER.EXE`'s code. `static:static/goal-exe-map.md`

## Method

- Artifact: `artifacts/known.json`, set `goal2-a949da2f`; files from `gh release download goal2-original --repo diegoami/goal2-archaeology -D .cache/goal2` (private release; never committed).
- Unpacker: `tools/static/unlzexe.py` (Python 3.12.3, standard library only). The format used: the 14-word MZ header; the signature `LZ91` at 0x1C; the bit-stream starting at `(e_cs - packed_paragraphs + e_cparhdr) * 16`; eight info words at the start of the stub (`ip0 cs0 sp0 ss0 packed_paragraphs growth - -`); the packed relocation table at stub + 0x158. The output header is padded to 512 bytes; its minimum and maximum allocation are derived (packed minimum less the growth) and do not affect code or data.
- Listing: `tools/static/listing.py` with `capstone==5.0.9` (pip package; the Python module reports `__version__` 5.0.7, the core library 5.0.1280), `CS_ARCH_X86` `CS_MODE_16`, run in `scratch/venv`. Recursive descent from the entry point (`0000:0000`), from every relocated far-call target, near call and jump, then from routine prologues (`55 89 E5`, `55 8B EC`) in the remaining bytes, repeated until nothing is added. Addresses are `SEGMENT:OFFSET` with the segment as the image paragraph before relocation; relocated segment words are named in the listing. The script refuses another capstone version and any input whose sha256 is not the known one.
- Tables: `routines.tsv`, `calls.tsv`, `datarefs.tsv`, `strings.tsv` in `static/goal-exe/`, from `tools/static/xrefs.py`.
- `GOAL.DAT`: `tools/static/goaldat.py` (standard library) checks R001..R011 against the file and writes `static/goal-dat/blocks.tsv` and `checks.txt`. The block sizes are not guessed: they are the constants of the ten reads in `1771:018A`.
- Basis for each representation claim R001..R013 is `static:static/goal-dat/blocks.tsv` (the offsets cited) with `static:static/goal-exe/code` where code is cited; none decodes a field beyond what is written.
- Tests: `tests/static/` (unpacker on a fixture packer written for the tests, relocation handling, `GOAL.DAT` checks on a synthetic file, listing on a 96-byte synthetic image, the map's addresses and quotes against the listing). Each test was run against a deliberately broken copy of the code or data and fails there (see the PR body).
- Static tools not available here and what they would add: **Ghidra** (Java, the owner's install) or another decompiler, for decompiler views of the Pascal routines, type recovery of the 191-byte country record and the 20-byte player record, and jump-table recovery in the places the descent could not follow; a **second disassembler** (for example radare2 or Ghidra's own) to cross-check capstone's decoding. DOSBox-X's debugger (G1) would show which of the inferred routines run in a match.

## Observations

**O1. Unpacking** (`python3 tools/static/unlzexe.py .cache/goal2/GOAL.EXE scratch/goal.exe`, run twice):

| Item | Value |
| --- | --- |
| packed header | `e_cparhdr` 2, `e_cs` 0x15F1, `e_ip` 0x000E, minimum allocation 0x1F19, `LZ91` at 0x1C |
| stub info words at file offset 0x15F30 | `ip0` 0, `cs0` 0, `sp0` 0x4000, `ss0` 0x3052, packed paragraphs 0x15F1, growth 0x175A |
| bit-stream | from file offset 0x20; end marker reached at file offset 0x15F21 (before the stub); 4 segment-change markers |
| unpacked image | 185,216 bytes (0x2D380) |
| relocations | 1,916 (table at stub + 0x158); 1,910 of them are the segment word of a far call (`9A` three bytes before); the largest relocated value is 0x2581, below the image's 0x2D38 paragraphs |
| unpacked file | **193,408 bytes** (header 8,192 + image 185,216), sha256 **`6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188`**, twice |
| far-call targets | 206 distinct; 165 begin with a `55 89 E5` or `55 8B EC` prologue |
| `ALTER.EXE` (not committed) | `tools/static/unlzexe.py` unpacks it too: 49,888 bytes, sha256 `21f97b9d50ac89aa346dfb3de74935aa33422efce45adc1479737464d851ebc8` |

**O2. Listing** (`static/goal-exe/README.md`): entry `0000:0000`, stack `3052:4000`, data segment `2581`; 11 code segments (`0000 000E 0791 16D6 1771 2138 2139 214B 235C 2382 23E4`); routines per segment `1 58 283 26 154 1 1 85 12 17 88` = 726; 57,508 instructions; `git diff --exit-code static/` is clean after `regenerate.sh`.

**O3. The loader** (`1771:018A`, `static:static/goal-exe/code`): the string `goal.dat` at `1771:0181`, then ten calls to `214B:1B47` (a read: it sets AH to 0x3F and calls `235C:0000`, handle in `DS:AAA4`). Sizes and destinations, in order: 0x0810 `[9B68]`, 0x8387 `[9B6C]`, 0x0BF5 `[9B70]`, 0x06DB `[9B74]`, 0x0087 `[9B78]` (five far pointers allocated by `2139:0000`), then 0x0183 `DS:9D80`, 0x0081 `DS:9B7C`, 0x0081 `DS:9BFD`, 0x0081 `DS:9C7E`, 0x0A14 `DS:9F03`. Sum 44,040.

**O4. The checks** (`static/goal-dat/checks.txt`, `python3 tools/static/goaldat.py .cache/goal2/GOAL.DAT static/goal-dat`; every line `OK`):

| Block | File offsets | Size | Records | First bytes |
| --- | --- | --- | --- | --- |
| 1 | 0x0000..0x080F | 2,064 | 129 × 16 | record 0 zero; `07 "Albania"` at 0x0010 |
| 2 | 0x0810..0x8B96 | 33,671 | 3,061 × 11 | record 0 zero; `05 "Musta"` at 0x081B |
| 3 | 0x8B97..0x978B | 3,061 | 3,061 × 1 | `00` then `A R K H T W S C M K` from 0x8B98 |
| 4 | 0x978C..0x9E66 | 1,755 | 135 × 13 | record 0 zero; `05 "Birce"` at 0x9799 |
| 5 | 0x9E67..0x9EED | 135 | 135 × 1 | `00` then `B D P D A M R J` from 0x9E68 |
| 6 | 0x9EEE..0xA070 | 387 | 129 × 3 | `00 00 00`, then `0C 0E 0A` at 0x9EF1 |
| 7 | 0xA071..0xA0F1 | 129 | 129 × 1 | `00`, then `F7 47 EA 88` from 0xA072 |
| 8 | 0xA0F2..0xA172 | 129 | 129 × 1 | `00 0C 22 10 09 44 06 08` |
| 9 | 0xA173..0xA1F3 | 129 | 129 × 1 | `00 07 0C 14 1B 19 0B 09` |
| 10 | 0xA1F4..0xAC07 | 2,580 | 129 × 20 | record 0 zero; at 0xA208 `00 01 02 02 05 06 07 08 0C 0D 0D | 00 01 02 05 06 07 0C 0D 0D` |

Other raw values: block 1 has 7 of 128 records whose text continues beyond the length byte (record 6 length 5, text `R.C.Soslovakia` at 0x0060; record 20 length 7, `Hollandherlands` at 0x0140); block 2 has 336 of 3,060 such records (record 21 at 0x08F7: length 9, text `Wohlfahrtg`); block 4: 25 of 128 records longer than the length byte, 1 shorter (record 12 at 0x9828: length 6, text `Vogts`). Block 6 values: 9 ×38, 10 ×66, 11 ×44, 12 ×87, 14 ×66, 15 ×83 (no 13). Block 7: 34 distinct values over records 1..128, from 54 to 254. Blocks 8 and 9: each of 0..128 once; neither is the identity. Block 10: in 123 of 128 records bytes 0..10 and bytes 11..19 are each non-decreasing; the exceptions are records 33, 56, 62, 94, 107 (offsets 0xA488, 0xA654, 0xA6CC, 0xA94C, 0xAA50); in all 128, bytes 0 and 11 are 0; all values are in 0..13 and all 14 occur.

**O5. Cross-references in the code** (`static:static/goal-exe/code`; addresses as in `static/goal-exe-map.md`):
- `1771:9A40`, for positions 1..128: reads block 8 at `DS:9BFD` and stores the position at field +0x2B of the 191-byte country record `[A917] + 0xBF * country`; reads block 9 at `DS:9C7E` and stores `(i-1) mod 32 + 1` at +0x2A and `(i-1) div 32 + 1` at +0x2C; copies block 7 (`DS:9B7C`) into +0x2D; fills 20 words of the record with the player numbers `(country-1)*20 + 1 .. country*20` (accumulator `+0x14` per country); calls `1771:97CC(country)`.
- `1771:97CC`: for slots 1..20 calls `1771:96D3` with the player number, the country and the byte of block 10 at `DS:9F03 + 20*country + slot - 1`. `0791:BC5D`: for slots 1..11 copies that byte to field +6 of the 20-byte player record `[A91B] + 0x14 * number`. `0791:05C6` reads field +6 and indexes the 14 bytes at `DS:69A8` (`G S C B B D 80 M M F W W 9B 24`); the 14 position names are at `DS:69B6`, 19 bytes apart (`goalkeeper`, `sweeper`, `centre back`, `left back`, `right back`, `defensive midfield`, `central midfield`, `left midfield`, `right midfield`, `forward midfield`, `left winger`, `right winger`, `centre forward`, `striker`).
- `0791:1073` reads bytes 0 and 2 of the block-6 record of each of two countries (`DS:9B34`, `DS:9B36`), and byte 1 when two of them would be equal, into `DS:832E..8331`.
- `0791:1829` reads the player's name at `[9B6C] + 11 * number` (`mul 0xB`); `0791:0106` reads the initial at `[9B70] + number` and the name, with `number` in `DS:7C3A`.
- `1771:09A0` reads and writes the 13-byte manager record at `[9B74] + 13 * index` and the initial at `[9B78] + index`; when the length byte is 0 it stores the string `Player` (6 characters, `1771:0999`).
- `1771:027B` (save and load a game) transfers the ten `GOAL.DAT` arrays with the same ten sizes, then twelve more blocks (169,553 bytes in all); `2139:0000` allocates the sixteen heap pointers with the same sizes.

## Inferences

### Representation claims proposed

| ID | Claim | `GOAL.DAT` offsets | Code evidence |
| --- | --- | --- | --- |
| R001 | The file is ten blocks in this order and with these sizes: `country_names` 0x0000+0x0810, `player_names` 0x0810+0x8387, `player_initials` 0x8B97+0x0BF5, `manager_names` 0x978C+0x06DB, `manager_initials` 0x9E67+0x0087, `per_country_3` 0x9EEE+0x0183, `per_country_a` 0xA071+0x0081, `per_country_b` 0xA0F2+0x0081, `per_country_c` 0xA173+0x0081, `squad_20` 0xA1F4+0x0A14; there is no header, no index and no padding | 0x0000..0xAC07; the content changes at each boundary (O4) | `1771:018A` (O3) `static:static/goal-dat/checks.txt` |
| R002 | Block 1: 129 records of 16 bytes (a length byte, then text, zero-filled); record 0 is empty; records 1..128 are the 128 country names; the record index is the country number | 0x0000 (record 0), 0x0010 `Albania` (1), 0x0020 `Austria` (2), 0x0200 `Yugoslavia` (32), 0x0210 `Antigua` (33), 0x0410 `Algeria` (65), 0x0610 `Australia` (97), 0x0800 `Yemen AR` (128). Byte 0 is a length 1..15 and the following bytes up to the first zero are printable ASCII in all 128; in 121 the text run equals the length, in 7 it is longer (residue of an edit, e.g. 0x0060, 0x0140) | `1771:018A`: `[9B68]`; `1771:9A40` indexes country records 1..128 `static:static/goal-dat/checks.txt` |
| R003 | Block 2: 3,061 records of 11 bytes (a length byte 1..10, text, zero-filled); record 0 is empty; records 1..3060 are surnames only, no forenames; the record index is the player number | 0x0810 (record 0), 0x081B `Musta` (1), 0x08F7 `Wohlfahrtg` (21), 0x761B `Longley` (2561), 0x8B8C `Godfrey` (3060). All 3,060 well formed; 2,724 have text run = length byte, 336 a longer run | `0791:1829` (`mul 0xB`, `[9B6C]`) `static:static/goal-dat/checks.txt` |
| R004 | Block 3: 3,061 bytes, one per player number; byte 0 is 0; bytes 1..3060 are upper-case ASCII letters (25 distinct), the initial shown with the surname | 0x8B97 (0), 0x8B98..0x978B | `0791:0106`: `[9B70] + DS:7C3A` and `[9B6C] + 11 * DS:7C3A` `static:static/goal-dat/checks.txt` |
| R005 | Block 4: 135 records of 13 bytes (a length byte 1..12, text, zero-filled); record 0 is empty; records 1..128 are surnames; records 129..134 are empty; for records 1..128 the index equals the country number (record 1 `Birce` follows country 1 `Albania`, 2 `Constantini` country 2 `Austria`, 3 `Van Himst` country 3 `Belgium`, 128 `Hussein` country 128 `Yemen AR`) | 0x978C (0), 0x9799, 0x97A6, 0x97B3, 0x9E0C (128), 0x9E19..0x9E66 (129..134 zero) | `1771:09A0` (`mul 0xD`, `[9B74]`) `static:static/goal-dat/checks.txt` |
| R006 | Block 5: 135 bytes, one per manager record; byte 0 and bytes 129..134 are 0; bytes 1..128 are upper-case ASCII letters | 0x9E67..0x9EED | `1771:09A0` (`[9B78]`) `static:static/goal-dat/checks.txt` |
| R007 | Block 6: 129 records of 3 bytes; record 0 is zero; every byte of records 1..128 is in 9..15 (13 does not occur); the record index is the country number | 0x9EEE..0xA070; record 1 at 0x9EF1 is `0C 0E 0A` | `0791:1073`: `DS:9D80 + 3 * country` (bytes 0, 2 and 1). Not decoded further `static:static/goal-dat/checks.txt` |
| R008 | Block 7: 129 bytes, one per country 0..128; byte 0 is 0; records 1..128 take 34 distinct values from 54 to 254 | 0xA071..0xA0F1 | `1771:9A40` copies it into field +0x2D of the country record; `0791:BC5D` passes `DS:9B7C[country]` to `0791:BBFF`. Not decoded `static:static/goal-dat/checks.txt` |
| R009 | Block 8: 129 bytes; byte 0 is 0; the 129 values are each of 0..128 exactly once (a permutation, not the identity) | 0xA0F2..0xA172 | `1771:9A40` loop 1 (O5) `static:static/goal-dat/checks.txt` |
| R010 | Block 9: the same properties as R009 | 0xA173..0xA1F3 | `1771:9A40` loop 2 (O5) `static:static/goal-dat/checks.txt` |
| R011 | Block 10: 129 records of 20 bytes; record 0 is zero; in every record 1..128 byte 0 and byte 11 are 0, every value is in 0..13 (all 14 occur), and bytes 0..10 and 11..19 are each non-decreasing in 123 of 128 records (exceptions: 33, 56, 62, 94, 107). The values are position codes: they are copied to the player's field +6, which indexes a 14-entry table (`DS:69A8`) that sits directly before the 14 position names (`DS:69B6`) | 0xA1F4..0xAC07; 0xA208 (record 1) | `1771:97CC`, `0791:BC5D`, `0791:05C6` (O5). That slots 0..10 are the first eleven is not established `static:static/goal-dat/checks.txt` |
| R012 | The squad of country `c` is player records `(c-1)*20 + 1 .. c*20` of blocks 2, 3 | 0x081B (country 1, first), 0x08F7 (country 2), 0x09D3 `Preud'homm` (country 3), 0x7610 `Mugahid` (country 128, last = record 2560); records 2561..3060 (0x761B..0x8B8C, 500 names) are named by no squad in `1771:9A40` | `1771:9A40` (O5) `static:static/goal-exe/code` |
| R013 | The file holds no per-player skill values: 12 one-byte skills for 3,060 names would need 36,720 bytes; the bytes outside blocks 2 and 3 are 7,308 | all blocks (R001) | the player record is 20 bytes at `[A91B]` (0xEF24 = 3061 × 0x14), built at start-up from these blocks `static:static/goal-dat/blocks.tsv` |

### The executable and the saved game

- The code is Pascal compiled to real-mode 8086 with one code segment per unit (length-prefixed strings, per-unit start-up calls in `0000:0000`, a start-up routine at `23E4:0000` and a halt at `23E4:00D8` that call INT 21h). Which compiler and version is not established. `static:static/goal-exe/code`
- From O3 and O5: the 10 arrays of `GOAL.DAT` are the first ten blocks of a saved game (`1771:027B`), so a save file is this file's data as edited in memory, followed by twelve blocks of the game's own state. `static:static/goal-exe/code`
- From O5 and `1771:09A0`: manager records 129..134 are empty in the file and filled with the text `Player` when empty; together with the prompt `How many players  1 2 3 4 5 6  ?` at `DS:1B1C` and the main program's loops over `(i + 0x80) * 3` in `[A91F]`, they are probably the names of up to six human managers. Inferred. `static:static/goal-exe/code`
- Every other inferred row of the map is named under "What this does not establish". `static:static/goal-exe-map.md`

## Alternatives considered

1. *The ten-block layout is a coincidence of sizes and the real layout has other boundaries.* Excluded by the content: strings of 16-byte records stop at 0x0810, 11-byte records stop at 0x8B97, a run of upper-case letters starts exactly at 0x8B98 and ends at 0x978B, 13-byte records start at 0x978C, and so on; each block's internal rule (R002..R011) holds across its whole extent, and the sum of the loader's sizes equals the file size.
2. *The unpacked image is wrong and the listing decodes garbage that still looks like code.* Excluded by: the bit-stream's end marker is reached at 0x15F21 inside the window the header gives; all 1,916 relocated words point inside the image, 1,910 of them as far-call operands; 165 of 206 far-call targets start with a routine prologue; the data segment's text reads cleanly (`goal.dat` at `1771:0181`, the commentary strings, the 14 position names); the loader's sizes reproduce the file's size. Not excluded: a defect in a rarely used back-reference form that the fixture tests and this image do not exercise; a second unpacker would settle it.
3. *capstone's linear decoding hides data inside code, or code inside the reported data.* Not excluded for 11,572 bytes of the code segments (7.5%): they are strings, tables and routines reached only through computed jumps or procedure variables; the listing reports them as data. A decompiler's view (Ghidra) would be a second method.
4. *A map row's role is wrong: text beside a routine need not be its text.* Not excluded for the 27 inferred rows; the rows marked observed state only a string, constant or call the listing shows.
5. *The block roles are other than R007..R011 suggest (for example block 6 is not colours, block 10 is not positions).* The claims name only what the bytes and the code access show; the roles in the map are marked inferred; a behavioural check (G1) would test them.

## What this does not establish

- No behaviour of the game, no rule, no number a rule uses. Nothing was run (G1).
- Other versions or copies of `GOAL.EXE` and `GOAL.DAT`: only set `goal2-a949da2f` was read. `ALTER.EXE` and `Y.HIL` are named, not read: `ALTER.EXE` unpacks with the same tool and holds the strings `ALTER : customisation utility`, `goal.dat`, `Do you want to save changes`; `Y.HIL` (3,989 bytes) begins `FE 00 00 00 06 CA 04 CA` and its extension is the string `.HIL` at `DS:06D6` of `GOAL.EXE`, next to the prompt `to save this goal` (`0791:0C65`): a saved goal, probably, inferred. `INSTALL.EXE` has no LZEXE 0.91 signature at 0x1C and was not read.
- The fields of the 191-byte country record, of the 20-byte player record and of the other heap blocks (except those `1771:9A40` sets and `0791:BC5D` copies, named above).
- The meaning of blocks 6 and 7: "display colours" for block 6 and any role for block 7 are not decoded; `0791:1073` and `1771:9A40` are the only evidence.
- The two runs of 11 and 9 in block 10 (R011) are an observation, not a decoded formation; five records break the ordering.
- The text-length residue in blocks 1, 2 and 4 (an edited name keeps the old tail) is observed, not explained; which of the length byte and the text the game shows is read from `23E4:062A` (a Pascal string copy) only by inference.
- **Areas the map could not place** (texts or tables exist in the data segment, no routine is tied to them): player attributes and skills, ageing and peak age, fitness, energy, confidence and morale (as numbers and as the word lists at `DS:6ED4..6FF4`, `DS:74D4`, `DS:7624`), how strong each country is, how rankings are set, injuries and suspensions (rules and durations), the shareware limit (`DS:19E8..1AB5` exists; no routine is tied to it), how a dismissal is decided, how the computer-run teams choose squads and tactics, the match engine's moving simulation (positions, marking, passing, tackling, shooting, offside, home advantage: only the commentary builder, the shoot-out and the replay are placed, and the region of match state), the customisation editor's code (`ALTER.EXE` is not mapped).
- **Inferred entries of the map** (role read from strings or data uses, not shown by the code alone): units `000E`, `0791`, `1771`, `214B`, `235C`, `2382`, `23E4` (what each is); `2139:0000` (allocation); `000E:7439` (the top-level screens); `1771:011B`, `1771:03FF`, `1771:0657`, `1771:101A`, `0791:0C65`, `0791:F1F6` (file, save and replay roles); `1771:9B85` (the four-year cycle); `0791:1073` (colours); `1771:97CC` (creates the players); `1771:377E` (a player's value); `0791:BD03` (compares two teams); `1771:26B9`, `1771:6730` (the post and option menus); `1771:3AE2`, `1771:3B3F` (marking zones); `0791:A4A1` (one step of a match); `1771:09A0` (the six human slots).
- No INT 34h..3Dh (8087 emulation) instruction occurs in the listing; computed-jump tables were not searched for.

## Where the evidence is

No run records or evidence manifests: the evidence is the released original files (`goal2-original`, sha256 in `artifacts/known.json`) and these derived extracts, regenerated by `tools/static/regenerate.sh`:
`static/goal-exe/` (listing, `routines.tsv`, `calls.tsv`, `datarefs.tsv`, `strings.tsv`, data hex), `static/goal-dat/` (`blocks.tsv`, `checks.txt`), `static/goal-exe-map.md` (the map). The unpacked executable is never committed (`scratch/goal.exe`).

## Reproduction

From a clean clone with Python 3.12, `gh` logged in, network to PyPI and GitHub:

```text
gh release download goal2-original --repo diegoami/goal2-archaeology -D .cache/goal2
python3 tools/static/unlzexe.py .cache/goal2/GOAL.EXE scratch/goal.exe        # twice: same sha256, 193408 bytes
sh tools/static/regenerate.sh                                                  # venv, capstone==5.0.9, the listing and the GOAL.DAT checks
git diff --exit-code static/                                                   # clean
python3 -m unittest discover -s tests/static -v                                # with scratch/venv/bin/python the listing tests run as well
python3 tools/static/goaldat.py .cache/goal2/GOAL.DAT                          # R001..R011, one OK line each
```
