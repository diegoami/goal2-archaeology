# static/goal-exe/

Generated, never edited by hand: `python3 tools/static/listing.py <released GOAL.EXE> static/goal-exe` (or
`tools/static/regenerate.sh`) rewrites every file here byte for byte.

- Artifact: `GOAL.EXE` of artifact set `goal2-a949da2f`, packed sha256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664` (LZEXE 0.91).
- Unpacked by `tools/static/unlzexe.py`: sha256 `6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188`, 193408 bytes (the unpacked file is never committed).
- Tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py.
- Image: 185216 bytes of load module (1916 relocations). Entry point 0000:0000, stack 3052:4000.  Data segment 2581.
- Addresses are `SEGMENT:OFFSET` where SEGMENT is the paragraph in the image before relocation (what the file holds);
  the image offset is `SEGMENT*16 + OFFSET`; the unpacked file's offset is that plus its header size (8192 bytes).
  A relocated segment word in an instruction is shown by its unrelocated value.
- 57508 instructions decoded; 142044 of 153616 code-segment bytes are code. The rest is reported as `data`.

| File | What |
| --- | --- |
| `code/seg_0000_01.asm` | code segment 0000 (image 00000..000DF) |
| `code/seg_000E_01.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_02.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_03.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_04.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_05.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_06.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_07.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_08.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_000E_09.asm` | code segment 000E (image 000E0..0790F) |
| `code/seg_0791_01.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_02.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_03.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_04.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_05.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_06.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_07.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_08.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_09.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_10.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_11.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_12.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_13.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_14.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_15.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_16.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_17.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_18.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_19.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_20.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_21.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_22.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_23.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_0791_24.asm` | code segment 0791 (image 07910..16D5F) |
| `code/seg_16D6_01.asm` | code segment 16D6 (image 16D60..1770F) |
| `code/seg_16D6_02.asm` | code segment 16D6 (image 16D60..1770F) |
| `code/seg_1771_01.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_02.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_03.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_04.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_05.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_06.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_07.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_08.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_09.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_10.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_11.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_12.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_13.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_1771_14.asm` | code segment 1771 (image 17710..2137F) |
| `code/seg_2138_01.asm` | code segment 2138 (image 21380..2138F) |
| `code/seg_2139_01.asm` | code segment 2139 (image 21390..214AF) |
| `code/seg_214B_01.asm` | code segment 214B (image 214B0..235BF) |
| `code/seg_214B_02.asm` | code segment 214B (image 214B0..235BF) |
| `code/seg_214B_03.asm` | code segment 214B (image 214B0..235BF) |
| `code/seg_214B_04.asm` | code segment 214B (image 214B0..235BF) |
| `code/seg_235C_01.asm` | code segment 235C (image 235C0..2381F) |
| `code/seg_2382_01.asm` | code segment 2382 (image 23820..23E3F) |
| `code/seg_23E4_01.asm` | code segment 23E4 (image 23E40..2580F) |
| `code/seg_23E4_02.asm` | code segment 23E4 (image 23E40..2580F) |
| `code/seg_23E4_03.asm` | code segment 23E4 (image 23E40..2580F) |
| `data/ds_2581_NN.hex` | the initialised data segment as hex with ASCII |
| `strings.tsv` | ASCII runs and Pascal strings, with addresses |
| `routines.tsv` | every routine found: address, size, callers, INT 21h functions, string and data references |
| `calls.tsv` | call edges: caller routine, callee |
| `datarefs.tsv` | data-segment offsets and the routines that reference them |

Method limits: recursive descent misses code reached only through computed jumps or procedure
variables unless a routine prologue shows it; bytes after the last decoded instruction of a gap are
reported as data. A listing line is capstone's decoding of the bytes, not a claim about the program.
