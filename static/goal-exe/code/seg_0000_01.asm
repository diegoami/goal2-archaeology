; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0000 (image offsets 00000..000DF), part 1 of 1
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 0000:0000  (found by: entry)
sub_0000:
0000  9A 00 00 E4 23  call far 23E4:0000
0005  9A 00 00 82 23  call far 2382:0000
000A  9A 6A 20 4B 21  call far 214B:206A
000F  9A 00 00 39 21  call far 2139:0000
0014  9A 00 00 38 21  call far 2138:0000
0019  9A F2 F3 91 07  call far 0791:F3F2
001E  55              push bp
001F  89 E5           mov bp, sp
0021  83 EC 02        sub sp, 2
0024  9A 0C 08 71 17  call far 1771:080C
0029  08 C0           or al, al
002B  74 03           je 0x30
002D  E9 96 00        jmp 0xc6
loc_0030:
0030  9A 9C 17 4B 21  call far 214B:179C
0035  9A 85 9B 71 17  call far 1771:9B85
003A  9A 15 2D 71 17  call far 1771:2D15
003F  C4 3E 23 A9     les di, ptr [0xa923]
0043  26 8A 05        mov al, byte ptr es:[di]
0046  30 E4           xor ah, ah
0048  89 46 FE        mov word ptr [bp - 2], ax
004B  B8 01 00        mov ax, 1
004E  3B 46 FE        cmp ax, word ptr [bp - 2]
0051  77 2D           ja 0x80
0053  A3 68 7B        mov word ptr [0x7b68], ax
0056  EB 04           jmp 0x5c
loc_0058:
0058  FF 06 68 7B     inc word ptr [0x7b68]
loc_005C:
005C  A1 68 7B        mov ax, word ptr [0x7b68]
005F  05 80 00        add ax, 0x80
0062  BA 03 00        mov dx, 3
0065  F7 E2           mul dx
0067  C4 3E 1F A9     les di, ptr [0xa91f]
006B  03 F8           add di, ax
006D  26 8A 05        mov al, byte ptr es:[di]
0070  30 E4           xor ah, ah
0072  50              push ax
0073  9A A4 68 0E 00  call far 000E:68A4
0078  A1 68 7B        mov ax, word ptr [0x7b68]
007B  3B 46 FE        cmp ax, word ptr [bp - 2]
007E  75 D8           jne 0x58
loc_0080:
0080  9A B1 76 71 17  call far 1771:76B1
0085  C4 3E 23 A9     les di, ptr [0xa923]
0089  26 8A 05        mov al, byte ptr es:[di]
008C  30 E4           xor ah, ah
008E  89 46 FE        mov word ptr [bp - 2], ax
0091  B8 01 00        mov ax, 1
0094  3B 46 FE        cmp ax, word ptr [bp - 2]
0097  77 2D           ja 0xc6
0099  A3 68 7B        mov word ptr [0x7b68], ax
009C  EB 04           jmp 0xa2
loc_009E:
009E  FF 06 68 7B     inc word ptr [0x7b68]
loc_00A2:
00A2  A1 68 7B        mov ax, word ptr [0x7b68]
00A5  05 80 00        add ax, 0x80
00A8  BA 03 00        mov dx, 3
00AB  F7 E2           mul dx
00AD  C4 3E 1F A9     les di, ptr [0xa91f]
00B1  03 F8           add di, ax
00B3  26 8A 05        mov al, byte ptr es:[di]
00B6  30 E4           xor ah, ah
00B8  50              push ax
00B9  9A CB 60 0E 00  call far 000E:60CB
00BE  A1 68 7B        mov ax, word ptr [0x7b68]
00C1  3B 46 FE        cmp ax, word ptr [bp - 2]
00C4  75 D8           jne 0x9e
loc_00C6:
00C6  9A 39 74 0E 00  call far 000E:7439
00CB  89 EC           mov sp, bp
00CD  5D              pop bp
00CE  31 C0           xor ax, ax
00D0  9A D8 00 E4 23  call far 23E4:00D8
00D5  00 00           add byte ptr [bx + si], al
00D7  00 00           add byte ptr [bx + si], al
00D9  00 00           add byte ptr [bx + si], al
00DB  00 00           add byte ptr [bx + si], al
00DD  00 00           add byte ptr [bx + si], al
; data (not reached as code), 1 bytes
00DF                  db 00   ; .
