; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 2382 (image offsets 23820..23E3F), part 1 of 1
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 2382:0000  (found by: far)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  E8 2A 00        call 0x30
0006  BF C0 AA        mov di, 0xaac0
0009  1E              push ds
000A  57              push di
000B  0E              push cs
000C  E8 1F 03        call 0x32e
000F  BF C0 AA        mov di, 0xaac0
0012  1E              push ds
0013  57              push di
0014  9A E2 13 E4 23  call far 23E4:13E2
0019  BF C0 AB        mov di, 0xabc0
001C  1E              push ds
001D  57              push di
001E  0E              push cs
001F  E8 0C 03        call 0x32e
0022  BF C0 AB        mov di, 0xabc0
0025  1E              push ds
0026  57              push di
0027  9A E7 13 E4 23  call far 23E4:13E7
002C  89 EC           mov sp, bp
002E  5D              pop bp
002F  CB              retf

; ---- routine 2382:0030  (found by: call)
sub_0030:
0030  B4 0F           mov ah, 0xf
0032  E8 D3 05        call 0x608
0035  3C 07           cmp al, 7
0037  74 0A           je 0x43
0039  3C 03           cmp al, 3
003B  76 06           jbe 0x43
003D  B8 03 00        mov ax, 3
0040  E8 56 00        call 0x99
loc_0043:
0043  E8 A1 00        call 0xe7
0046  B4 08           mov ah, 8
0048  32 FF           xor bh, bh
004A  E8 BB 05        call 0x608
004D  8A C4           mov al, ah
004F  24 7F           and al, 0x7f
0051  A2 BC AA        mov byte ptr [0xaabc], al
0054  A2 B2 AA        mov byte ptr [0xaab2], al
0057  33 C0           xor ax, ax
0059  A2 AD AA        mov byte ptr [0xaaad], al
005C  A2 BD AA        mov byte ptr [0xaabd], al
005F  A2 BE AA        mov byte ptr [0xaabe], al
0062  40              inc ax
0063  A2 AC AA        mov byte ptr [0xaaac], al
0066  B8 40 00        mov ax, 0x40
0069  8E C0           mov es, ax
006B  BF 6C 00        mov di, 0x6c
006E  26 8A 05        mov al, byte ptr es:[di]
loc_0071:
0071  26 3A 05        cmp al, byte ptr es:[di]
0074  74 FB           je 0x71
0076  26 8A 05        mov al, byte ptr es:[di]
0079  B9 FF FF        mov cx, 0xffff
007C  E8 3F 02        call 0x2be
007F  B8 37 00        mov ax, 0x37
0082  91              xchg cx, ax
0083  F7 D0           not ax
0085  33 D2           xor dx, dx
0087  F7 F1           div cx
0089  A3 B8 AA        mov word ptr [0xaab8], ax
008C  1E              push ds
008D  0E              push cs
008E  1F              pop ds
008F  BA 2F 01        mov dx, 0x12f
0092  B8 1B 25        mov ax, 0x251b
0095  CD 21           int 0x21   ; INT 21h AH=25 set interrupt vector
0097  1F              pop ds
0098  C3              ret

; ---- routine 2382:0099  (found by: call)
sub_0099:
0099  BA 40 00        mov dx, 0x40
009C  8E C2           mov es, dx
009E  26 80 26 87 00 FE and byte ptr es:[0x87], 0xfe
00A4  3C 07           cmp al, 7
00A6  74 06           je 0xae
00A8  3C 04           cmp al, 4
00AA  72 02           jb 0xae
00AC  B0 03           mov al, 3
loc_00AE:
00AE  50              push ax
00AF  B4 00           mov ah, 0
00B1  E8 54 05        call 0x608
00B4  58              pop ax
00B5  0A E4           or ah, ah
00B7  74 2D           je 0xe6
00B9  B8 12 11        mov ax, 0x1112
00BC  B3 00           mov bl, 0
00BE  E8 47 05        call 0x608
00C1  B8 30 11        mov ax, 0x1130
00C4  B7 00           mov bh, 0
00C6  B2 00           mov dl, 0
00C8  E8 3D 05        call 0x608
00CB  80 FA 2A        cmp dl, 0x2a
00CE  75 16           jne 0xe6
00D0  26 80 0E 87 00 01 or byte ptr es:[0x87], 1
00D6  B8 00 01        mov ax, 0x100
00D9  B9 00 06        mov cx, 0x600
00DC  E8 29 05        call 0x608
00DF  B4 12           mov ah, 0x12
00E1  B3 20           mov bl, 0x20
00E3  E8 22 05        call 0x608
loc_00E6:
00E6  C3              ret

; ---- routine 2382:00E7  (found by: call)
sub_00E7:
00E7  B4 0F           mov ah, 0xf
00E9  E8 1C 05        call 0x608
00EC  50              push ax
00ED  B8 30 11        mov ax, 0x1130
00F0  B7 00           mov bh, 0
00F2  B2 00           mov dl, 0
00F4  E8 11 05        call 0x608
00F7  58              pop ax
00F8  B1 00           mov cl, 0
00FA  0A D2           or dl, dl
00FC  75 08           jne 0x106
00FE  B2 18           mov dl, 0x18
0100  3C 03           cmp al, 3
0102  77 02           ja 0x106
0104  B1 01           mov cl, 1
loc_0106:
0106  8A F2           mov dh, dl
0108  8A D4           mov dl, ah
010A  FE CA           dec dl
010C  B4 00           mov ah, 0
010E  80 FE 18        cmp dh, 0x18
0111  76 02           jbe 0x115
0113  B4 01           mov ah, 1
loc_0115:
0115  A3 B0 AA        mov word ptr [0xaab0], ax
0118  89 16 BA AA     mov word ptr [0xaaba], dx
011C  88 0E AF AA     mov byte ptr [0xaaaf], cl
0120  C6 06 AE AA 01  mov byte ptr [0xaaae], 1
0125  33 C0           xor ax, ax
0127  A3 B4 AA        mov word ptr [0xaab4], ax
012A  89 16 B6 AA     mov word ptr [0xaab6], dx
012E  C3              ret
; data (not reached as code), 22 bytes
012F                  db 50 1E B8 81 25 8E D8 80 3E AC AA 00 74 05 C6 06   ; P...%...>...t...
013F                  db BE AA 01 1F 58 CF   ; ....X.

; ---- routine 2382:0145  (found by: call)
sub_0145:
0145  80 3E BE AA 00  cmp byte ptr [0xaabe], 0
014A  75 01           jne 0x14d
014C  C3              ret
loc_014D:
014D  C6 06 BE AA 00  mov byte ptr [0xaabe], 0
loc_0152:
0152  B4 01           mov ah, 1
0154  CD 16           int 0x16
0156  74 06           je 0x15e
0158  B4 00           mov ah, 0
015A  CD 16           int 0x16
015C  EB F4           jmp 0x152
loc_015E:
015E  B0 5E           mov al, 0x5e
0160  E8 18 03        call 0x47b
0163  B0 43           mov al, 0x43
0165  E8 13 03        call 0x47b
0168  E8 09 03        call 0x474
016B  CD 23           int 0x23

; ---- routine 2382:016D  (found by: far)
sub_016D:
016D  8B DC           mov bx, sp
016F  36 8B 47 04     mov ax, word ptr ss:[bx + 4]
0173  E8 23 FF        call 0x99
0176  E8 6E FF        call 0xe7
0179  A0 BC AA        mov al, byte ptr [0xaabc]
017C  A2 B2 AA        mov byte ptr [0xaab2], al
017F  CA 02 00        retf 2
; data (not reached as code), 147 bytes
0182                  db 8B DC 36 8A 57 0A 36 8A 77 08 36 8A 4F 06 36 8A   ; ..6.W.6.w.6.O.6.
0192                  db 6F 04 3A D1 77 27 3A F5 77 23 FE CA 78 1F FE CE   ; o.:.w':.w#..x...
01A2                  db 78 1B FE C9 3A 0E BA AA 77 13 FE CD 3A 2E BB AA   ; x...:...w...:...
01B2                  db 77 0B 89 16 B4 AA 89 0E B6 AA E8 3D 03 CA 08 00   ; w..........=....
01C2                  db B8 00 06 8A 3E B2 AA 8B 0E B4 AA 8B 16 B6 AA E8   ; ....>...........
01D2                  db 34 04 8B 16 B4 AA E8 21 03 CB E8 16 03 B8 00 06   ; 4......!........
01E2                  db 8A 3E B2 AA 8B CA 8A 16 B6 AA E8 19 04 CB B8 01   ; .>..............
01F2                  db 07 EB 03 B8 01 06 50 E8 F9 02 58 8A 3E B2 AA 8A   ; ......P...X.>...
0202                  db 0E B4 AA 8A EE 8B 16 B6 AA 3A EE 75 02 32 C0 E8   ; .........:.u.2..
0212                  db F4 03 CB   ; ...

; ---- routine 2382:0215  (found by: far)
sub_0215:
0215  8B DC           mov bx, sp
0217  36 8A 57 06     mov dl, byte ptr ss:[bx + 6]
021B  36 8A 77 04     mov dh, byte ptr ss:[bx + 4]
021F  FE CA           dec dl
0221  02 16 B4 AA     add dl, byte ptr [0xaab4]
0225  72 17           jb 0x23e
0227  3A 16 B6 AA     cmp dl, byte ptr [0xaab6]
022B  77 11           ja 0x23e
022D  FE CE           dec dh
022F  02 36 B5 AA     add dh, byte ptr [0xaab5]
0233  72 09           jb 0x23e
0235  3A 36 B7 AA     cmp dh, byte ptr [0xaab7]
0239  77 03           ja 0x23e
023B  E8 BE 02        call 0x4fc
loc_023E:
023E  CA 04 00        retf 4
; data (not reached as code), 125 bytes
0241                  db E8 B1 02 8A C2 2A 06 B4 AA FE C0 CB E8 A5 02 8A   ; .....*..........
0251                  db C6 2A 06 B5 AA FE C0 CB 8B DC 36 8A 47 04 A8 F0   ; .*........6.G...
0261                  db 74 04 24 0F 0C 80 80 26 B2 AA 70 08 06 B2 AA CA   ; t.$....&..p.....
0271                  db 02 00 8B DC 36 8A 47 04 24 07 B1 04 D2 E0 80 26   ; ....6.G.$......&
0281                  db B2 AA 8F 08 06 B2 AA CA 02 00 80 26 B2 AA F7 CB   ; ...........&....
0291                  db 80 0E B2 AA 08 CB A0 BC AA A2 B2 AA CB 8B DC 36   ; ...............6
02A1                  db 8B 57 04 0B D2 74 13 33 FF 8E C7 26 8A 05 8B 1E   ; .W...t.3...&....
02B1                  db B8 AA 8B CB E8 06 00 4A 75 F8 CA 02 00   ; .......Ju....

; ---- routine 2382:02BE  (found by: call)
sub_02BE:
02BE  26 3A 05        cmp al, byte ptr es:[di]
02C1  75 02           jne 0x2c5
02C3  E2 F9           loop 0x2be
loc_02C5:
02C5  C3              ret
; data (not reached as code), 70 bytes
02C6                  db 8B DC 36 8B 5F 04 B8 DD 34 BA 12 00 3B D3 73 1A   ; ..6._...4...;.s.
02D6                  db F7 F3 8B D8 E4 61 A8 03 75 08 0C 03 E6 61 B0 B6   ; .....a..u....a..
02E6                  db E6 43 8A C3 E6 42 8A C7 E6 42 CA 02 00 E4 61 24   ; .C...B...B....a$
02F6                  db FC E6 61 CB 80 3E BD AA 00 75 08 B4 01 CD 16 B0   ; ..a..>...u......
0306                  db 00 74 02 B0 01 CB   ; .t....

; ---- routine 2382:030C  (found by: call)
sub_030C:
030C  A0 BD AA        mov al, byte ptr [0xaabd]
030F  C6 06 BD AA 00  mov byte ptr [0xaabd], 0
0314  0A C0           or al, al
0316  75 12           jne 0x32a
0318  32 E4           xor ah, ah
031A  CD 16           int 0x16
031C  0A C0           or al, al
031E  75 0A           jne 0x32a
0320  88 26 BD AA     mov byte ptr [0xaabd], ah
0324  0A E4           or ah, ah
0326  75 02           jne 0x32a
0328  B0 03           mov al, 3
loc_032A:
032A  E8 18 FE        call 0x145
032D  CB              retf

; ---- routine 2382:032E  (found by: call)
sub_032E:
032E  8B DC           mov bx, sp
0330  1E              push ds
0331  36 C5 7F 04     lds di, ptr ss:[bx + 4]
0335  C7 45 02 B0 D7  mov word ptr [di + 2], 0xd7b0
033A  C7 45 04 80 00  mov word ptr [di + 4], 0x80
033F  8D 85 80 00     lea ax, [di + 0x80]
0343  89 45 0C        mov word ptr [di + 0xc], ax
0346  8C 5D 0E        mov word ptr [di + 0xe], ds
0349  C7 45 10 59 03  mov word ptr [di + 0x10], 0x359
034E  8C 4D 12        mov word ptr [di + 0x12], cs
0351  C6 45 30 00     mov byte ptr [di + 0x30], 0
0355  1F              pop ds
0356  CA 04 00        retf 4
; data (not reached as code), 56 bytes
0359                  db 8B DC 1E 36 C5 7F 04 B8 91 03 BB 6F 04 8B CB 81   ; ...6.......o....
0369                  db 7D 02 B1 D7 74 0A C7 45 02 B2 D7 B8 3E 04 8B D8   ; }...t..E....>...
0379                  db 89 45 14 8C 4D 16 89 5D 18 8C 4D 1A 89 4D 1C 8C   ; .E..M..]..M..M..
0389                  db 4D 1E 33 C0 1F CA 04 00   ; M.3.....

; ---- routine 2382:0391  (found by: prologue)
sub_0391:
0391  55              push bp
0392  8B EC           mov bp, sp
0394  C4 7E 06        les di, ptr [bp + 6]
0397  26 8B 55 04     mov dx, word ptr es:[di + 4]
039B  4A              dec dx
039C  4A              dec dx
039D  26 8B 75 08     mov si, word ptr es:[di + 8]
03A1  26 C4 7D 0C     les di, ptr es:[di + 0xc]
03A5  33 DB           xor bx, bx
loc_03A7:
03A7  C6 06 BD AA 00  mov byte ptr [0xaabd], 0
03AC  0E              push cs
03AD  E8 5C FF        call 0x30c
03B0  B9 01 00        mov cx, 1
03B3  3C 08           cmp al, 8
03B5  74 34           je 0x3eb
03B7  3C 13           cmp al, 0x13
03B9  74 30           je 0x3eb
03BB  3C 04           cmp al, 4
03BD  74 44           je 0x403
03BF  49              dec cx
03C0  3C 1B           cmp al, 0x1b
03C2  74 27           je 0x3eb
03C4  3C 01           cmp al, 1
03C6  74 23           je 0x3eb
03C8  3C 06           cmp al, 6
03CA  74 37           je 0x403
03CC  3C 1A           cmp al, 0x1a
03CE  74 46           je 0x416
03D0  3C 0D           cmp al, 0xd
03D2  74 4F           je 0x423
03D4  3C 20           cmp al, 0x20
03D6  72 CF           jb 0x3a7
03D8  3B DA           cmp bx, dx
03DA  74 CB           je 0x3a7
03DC  26 88 01        mov byte ptr es:[bx + di], al
03DF  43              inc bx
03E0  E8 98 00        call 0x47b
03E3  3B DE           cmp bx, si
03E5  76 C0           jbe 0x3a7
03E7  8B F3           mov si, bx
03E9  EB BC           jmp 0x3a7
loc_03EB:
03EB  0B DB           or bx, bx
03ED  74 B8           je 0x3a7
03EF  B0 08           mov al, 8
03F1  E8 87 00        call 0x47b
03F4  B0 20           mov al, 0x20
03F6  E8 82 00        call 0x47b
03F9  B0 08           mov al, 8
03FB  E8 7D 00        call 0x47b
03FE  4B              dec bx
03FF  E2 EA           loop 0x3eb
0401  EB A4           jmp 0x3a7
loc_0403:
0403  3B DE           cmp bx, si
0405  74 A0           je 0x3a7
0407  26 8A 01        mov al, byte ptr es:[bx + di]
040A  3C 20           cmp al, 0x20
040C  72 99           jb 0x3a7
040E  E8 6A 00        call 0x47b
0411  43              inc bx
0412  E2 EF           loop 0x403
0414  EB 91           jmp 0x3a7
loc_0416:
0416  80 3E AD AA 00  cmp byte ptr [0xaaad], 0
041B  74 8A           je 0x3a7
041D  26 88 01        mov byte ptr es:[bx + di], al
0420  43              inc bx
0421  EB 0A           jmp 0x42d
loc_0423:
0423  E8 4E 00        call 0x474
0426  26 C7 01 0D 0A  mov word ptr es:[bx + di], 0xa0d
042B  43              inc bx
042C  43              inc bx
loc_042D:
042D  C4 7E 06        les di, ptr [bp + 6]
0430  33 C0           xor ax, ax
0432  26 89 45 08     mov word ptr es:[di + 8], ax
0436  26 89 5D 0A     mov word ptr es:[di + 0xa], bx
043A  5D              pop bp
043B  CA 04 00        retf 4
; data (not reached as code), 54 bytes
043E                  db 8B DC 36 C4 7F 04 26 8B 4D 08 26 29 4D 08 E3 19   ; ..6...&.M.&)M...
044E                  db 26 C4 7D 0C 80 3E AE AA 00 75 0B 26 8A 05 E8 1C   ; &.}..>...u.&....
045E                  db 00 47 E2 F7 EB 03 E8 9C 00 E8 DB FC 33 C0 CA 04   ; .G..........3...
046E                  db 00 33 C0 CA 04 00   ; .3....

; ---- routine 2382:0474  (found by: call)
sub_0474:
0474  B0 0D           mov al, 0xd
0476  E8 02 00        call 0x47b
0479  B0 0A           mov al, 0xa

; ---- routine 2382:047B  (found by: call)
sub_047B:
047B  53              push bx
047C  51              push cx
047D  52              push dx
047E  06              push es
047F  50              push ax
0480  E8 72 00        call 0x4f5
0483  58              pop ax
0484  3C 07           cmp al, 7
0486  74 2A           je 0x4b2
0488  3C 08           cmp al, 8
048A  74 2D           je 0x4b9
048C  3C 0D           cmp al, 0xd
048E  74 33           je 0x4c3
0490  3C 0A           cmp al, 0xa
0492  74 35           je 0x4c9
0494  B4 09           mov ah, 9
0496  8A 1E B2 AA     mov bl, byte ptr [0xaab2]
049A  32 FF           xor bh, bh
049C  B9 01 00        mov cx, 1
049F  52              push dx
04A0  E8 65 01        call 0x608
04A3  5A              pop dx
04A4  FE C2           inc dl
04A6  3A 16 B6 AA     cmp dl, byte ptr [0xaab6]
04AA  76 20           jbe 0x4cc
04AC  8A 16 B4 AA     mov dl, byte ptr [0xaab4]
04B0  EB 17           jmp 0x4c9
loc_04B2:
04B2  B4 0E           mov ah, 0xe
04B4  E8 51 01        call 0x608
04B7  EB 13           jmp 0x4cc
loc_04B9:
04B9  3A 16 B4 AA     cmp dl, byte ptr [0xaab4]
04BD  74 0D           je 0x4cc
04BF  FE CA           dec dl
04C1  EB 09           jmp 0x4cc
loc_04C3:
04C3  8A 16 B4 AA     mov dl, byte ptr [0xaab4]
04C7  EB 03           jmp 0x4cc
loc_04C9:
04C9  E8 08 00        call 0x4d4
loc_04CC:
04CC  E8 2D 00        call 0x4fc
04CF  07              pop es
04D0  5A              pop dx
04D1  59              pop cx
04D2  5B              pop bx
04D3  C3              ret

; ---- routine 2382:04D4  (found by: call)
sub_04D4:
04D4  FE C6           inc dh
04D6  3A 36 B7 AA     cmp dh, byte ptr [0xaab7]
04DA  76 18           jbe 0x4f4
04DC  FE CE           dec dh
04DE  51              push cx
04DF  52              push dx
04E0  B8 01 06        mov ax, 0x601
04E3  8A 3E B2 AA     mov bh, byte ptr [0xaab2]
04E7  8B 0E B4 AA     mov cx, word ptr [0xaab4]
04EB  8B 16 B6 AA     mov dx, word ptr [0xaab6]
04EF  E8 16 01        call 0x608
04F2  5A              pop dx
04F3  59              pop cx
loc_04F4:
04F4  C3              ret

; ---- routine 2382:04F5  (found by: call)
sub_04F5:
04F5  B4 03           mov ah, 3
04F7  32 FF           xor bh, bh
04F9  E9 0C 01        jmp 0x608

; ---- routine 2382:04FC  (found by: call)
sub_04FC:
04FC  B4 02           mov ah, 2
04FE  32 FF           xor bh, bh
0500  E9 05 01        jmp 0x608
; data (not reached as code), 261 bytes
0503                  db 1E B8 40 00 8E D8 8B 16 50 00 1F 8B DA 8B F7 26   ; ..@.....P......&
0513                  db 8A 05 3C 07 74 21 3C 08 74 2C 3C 0A 74 35 3C 0D   ; ..<.t!<.t,<.t5<.
0523                  db 74 39 47 FE C2 3A 16 B6 AA 76 3C E8 6F 00 E8 A0   ; t9G..:...v<.o...
0533                  db FF 8A 16 B4 AA EB 2C E8 63 00 51 52 B8 07 0E E8   ; ......,.c.QR....
0543                  db C3 00 5A 59 EB 1C E8 54 00 3A 16 B4 AA 74 13 FE   ; ..ZY...T.:...t..
0553                  db CA EB 0F E8 47 00 E8 78 FF EB 07 E8 3F 00 8A 16   ; ....G..x....?...
0563                  db B4 AA 47 8B F7 8B DA E2 A6 E8 31 00 1E B8 40 00   ; ..G.......1...@.
0573                  db 8E D8 89 16 50 00 8A C6 F6 26 4A 00 32 F6 03 C2   ; ....P....&J.2...
0583                  db 8B C8 8B 16 63 00 B0 0E EE EB 00 8A C5 42 EE EB   ; ....c........B..
0593                  db 00 4A B0 0F EE EB 00 8A C1 42 EE 1F C3 3B F7 74   ; .J.......B...;.t
05A3                  db 63 51 52 57 1E 06 8B CF 2B CE 8A 16 AF AA 8A 36   ; cQRW....+......6
05B3                  db B2 AA B8 40 00 8E D8 8A C7 F6 26 4A 00 32 FF 03   ; ...@......&J.2..
05C3                  db C3 D1 E0 8B F8 8B DA 8B 16 63 00 83 C2 06 B8 00   ; .........c......
05D3                  db B8 80 3E 49 00 07 75 02 B4 B0 06 1F 8E C0 FC 0A   ; ..>I..u.........
05E3                  db DB 74 16 AC 8A D8 EC A8 01 75 FB FA EC A8 01 74   ; .t.......u.....t
05F3                  db FB 8B C3 AB FB E2 EC EB 06 8A E7 AC AB E2 FC 07   ; ................
0603                  db 1F 5F 5A 59 C3   ; ._ZY.

; ---- routine 2382:0608  (found by: call, jump)
sub_0608:
0608  56              push si
0609  57              push di
060A  55              push bp
060B  06              push es
060C  CD 10           int 0x10
060E  07              pop es
060F  5D              pop bp
0610  5F              pop di
0611  5E              pop si
0612  C3              ret
; data (not reached as code), 13 bytes
0613                  db 00 00 00 00 00 00 00 00 00 00 00 00 00   ; .............
