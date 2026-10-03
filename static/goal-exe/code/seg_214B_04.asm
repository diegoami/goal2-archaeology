; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 214B (image offsets 214B0..235BF), part 4 of 4
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 214B:1D6F  (found by: far)
sub_1D6F:
1D6F  55              push bp
1D70  89 E5           mov bp, sp
1D72  83 EC 02        sub sp, 2
1D75  C4 7E 0C        les di, ptr [bp + 0xc]
1D78  26 8A 05        mov al, byte ptr es:[di]
1D7B  30 E4           xor ah, ah
1D7D  89 46 FE        mov word ptr [bp - 2], ax
1D80  8D 7E FE        lea di, [bp - 2]
1D83  16              push ss
1D84  57              push di
1D85  8A 46 0A        mov al, byte ptr [bp + 0xa]
1D88  30 E4           xor ah, ah
1D8A  50              push ax
1D8B  8A 46 08        mov al, byte ptr [bp + 8]
1D8E  30 E4           xor ah, ah
1D90  50              push ax
1D91  FF 76 06        push word ptr [bp + 6]
1D94  0E              push cs
1D95  E8 EE FE        call 0x1c86
1D98  8A 46 FE        mov al, byte ptr [bp - 2]
1D9B  C4 7E 0C        les di, ptr [bp + 0xc]
1D9E  26 88 05        mov byte ptr es:[di], al
1DA1  89 EC           mov sp, bp
1DA3  5D              pop bp
1DA4  CA 0A 00        retf 0xa

; ---- routine 214B:1DA7  (found by: call)
sub_1DA7:
1DA7  55              push bp
1DA8  89 E5           mov bp, sp
1DAA  83 EC 06        sub sp, 6
1DAD  31 C0           xor ax, ax
1DAF  89 46 FA        mov word ptr [bp - 6], ax
1DB2  89 46 FC        mov word ptr [bp - 4], ax
1DB5  31 F6           xor si, si
1DB7  8E C6           mov es, si
1DB9  26 A1 6C 04     mov ax, word ptr es:[0x46c]
1DBD  89 46 FE        mov word ptr [bp - 2], ax
loc_1DC0:
1DC0  8B 46 FE        mov ax, word ptr [bp - 2]
1DC3  31 F6           xor si, si
1DC5  8E C6           mov es, si
1DC7  26 3B 06 6C 04  cmp ax, word ptr es:[0x46c]
1DCC  74 F2           je 0x1dc0
1DCE  31 F6           xor si, si
1DD0  8E C6           mov es, si
1DD2  26 A1 6C 04     mov ax, word ptr es:[0x46c]
1DD6  89 46 FE        mov word ptr [bp - 2], ax
loc_1DD9:
1DD9  83 46 FA 01     add word ptr [bp - 6], 1
1DDD  83 56 FC 00     adc word ptr [bp - 4], 0
1DE1  8B 46 FE        mov ax, word ptr [bp - 2]
1DE4  31 F6           xor si, si
1DE6  8E C6           mov es, si
1DE8  26 3B 06 6C 04  cmp ax, word ptr es:[0x46c]
1DED  74 EA           je 0x1dd9
1DEF  C4 46 FA        les ax, ptr [bp - 6]
1DF2  8C C2           mov dx, es
1DF4  B9 37 00        mov cx, 0x37
1DF7  31 DB           xor bx, bx
1DF9  9A 94 02 E4 23  call far 23E4:0294
1DFE  A3 FF A9        mov word ptr [0xa9ff], ax
1E01  89 16 01 AA     mov word ptr [0xaa01], dx
1E05  89 EC           mov sp, bp
1E07  5D              pop bp
1E08  C3              ret

; ---- routine 214B:1E09  (found by: call, far)
sub_1E09:
1E09  55              push bp
1E0A  89 E5           mov bp, sp
1E0C  83 EC 08        sub sp, 8
1E0F  83 7E 06 00     cmp word ptr [bp + 6], 0
1E13  76 3F           jbe 0x1e54
1E15  8B 46 06        mov ax, word ptr [bp + 6]
1E18  89 46 F8        mov word ptr [bp - 8], ax
1E1B  B8 01 00        mov ax, 1
1E1E  3B 46 F8        cmp ax, word ptr [bp - 8]
1E21  77 31           ja 0x1e54
1E23  89 46 FE        mov word ptr [bp - 2], ax
1E26  EB 03           jmp 0x1e2b
loc_1E28:
1E28  FF 46 FE        inc word ptr [bp - 2]
loc_1E2B:
1E2B  31 C0           xor ax, ax
1E2D  89 46 FA        mov word ptr [bp - 6], ax
1E30  89 46 FC        mov word ptr [bp - 4], ax
loc_1E33:
1E33  83 46 FA 01     add word ptr [bp - 6], 1
1E37  83 56 FC 00     adc word ptr [bp - 4], 0
1E3B  C4 46 FA        les ax, ptr [bp - 6]
1E3E  8C C2           mov dx, es
1E40  3B 16 01 AA     cmp dx, word ptr [0xaa01]
1E44  75 ED           jne 0x1e33
1E46  3B 06 FF A9     cmp ax, word ptr [0xa9ff]
1E4A  75 E7           jne 0x1e33
1E4C  8B 46 FE        mov ax, word ptr [bp - 2]
1E4F  3B 46 F8        cmp ax, word ptr [bp - 8]
1E52  75 D4           jne 0x1e28
loc_1E54:
1E54  89 EC           mov sp, bp
1E56  5D              pop bp
1E57  CA 02 00        retf 2

; ---- routine 214B:1E5A  (found by: far)
sub_1E5A:
1E5A  55              push bp
1E5B  89 E5           mov bp, sp
1E5D  0E              push cs
1E5E  E8 2C 00        call 0x1e8d
1E61  80 3E FC A9 00  cmp byte ptr [0xa9fc], 0
1E66  74 04           je 0x1e6c
1E68  B0 00           mov al, 0
1E6A  EB 02           jmp 0x1e6e
loc_1E6C:
1E6C  B0 01           mov al, 1
loc_1E6E:
1E6E  A2 FC A9        mov byte ptr [0xa9fc], al
1E71  89 EC           mov sp, bp
1E73  5D              pop bp
1E74  CB              retf

; ---- routine 214B:1E75  (found by: call, far)
sub_1E75:
1E75  55              push bp
1E76  89 E5           mov bp, sp
1E78  80 3E FC A9 00  cmp byte ptr [0xa9fc], 0
1E7D  75 0A           jne 0x1e89
1E7F  B0 B6           mov al, 0xb6
1E81  E6 43           out 0x43, al
1E83  E4 61           in al, 0x61
1E85  0C 03           or al, 3
1E87  E6 61           out 0x61, al
loc_1E89:
1E89  89 EC           mov sp, bp
1E8B  5D              pop bp
1E8C  CB              retf

; ---- routine 214B:1E8D  (found by: call, far)
sub_1E8D:
1E8D  55              push bp
1E8E  89 E5           mov bp, sp
1E90  80 3E FC A9 00  cmp byte ptr [0xa9fc], 0
1E95  75 06           jne 0x1e9d
1E97  E4 61           in al, 0x61
1E99  24 FC           and al, 0xfc
1E9B  E6 61           out 0x61, al
loc_1E9D:
1E9D  89 EC           mov sp, bp
1E9F  5D              pop bp
1EA0  CB              retf

; ---- routine 214B:1EA1  (found by: far)
sub_1EA1:
1EA1  55              push bp
1EA2  89 E5           mov bp, sp
1EA4  FF 76 08        push word ptr [bp + 8]
1EA7  0E              push cs
1EA8  E8 11 00        call 0x1ebc
1EAB  FF 76 06        push word ptr [bp + 6]
1EAE  0E              push cs
1EAF  E8 57 FF        call 0x1e09
1EB2  0E              push cs
1EB3  E8 D7 FF        call 0x1e8d
1EB6  89 EC           mov sp, bp
1EB8  5D              pop bp
1EB9  CA 04 00        retf 4

; ---- routine 214B:1EBC  (found by: call, far)
sub_1EBC:
1EBC  55              push bp
1EBD  89 E5           mov bp, sp
1EBF  80 3E FC A9 00  cmp byte ptr [0xa9fc], 0
1EC4  75 25           jne 0x1eeb
1EC6  0E              push cs
1EC7  E8 AB FF        call 0x1e75
1ECA  8B 46 06        mov ax, word ptr [bp + 6]
1ECD  31 D2           xor dx, dx
1ECF  8B C8           mov cx, ax
1ED1  8B DA           mov bx, dx
1ED3  B8 DD 34        mov ax, 0x34dd
1ED6  BA 12 00        mov dx, 0x12
1ED9  9A 94 02 E4 23  call far 23E4:0294
1EDE  89 46 06        mov word ptr [bp + 6], ax
1EE1  8A 46 06        mov al, byte ptr [bp + 6]
1EE4  E6 42           out 0x42, al
1EE6  8A 46 07        mov al, byte ptr [bp + 7]
1EE9  E6 42           out 0x42, al
loc_1EEB:
1EEB  89 EC           mov sp, bp
1EED  5D              pop bp
1EEE  CA 02 00        retf 2

; ---- routine 214B:1EF1  (found by: call, far)
sub_1EF1:
1EF1  55              push bp
1EF2  89 E5           mov bp, sp
1EF4  83 EC 02        sub sp, 2
1EF7  80 3E FC A9 00  cmp byte ptr [0xa9fc], 0
1EFC  75 77           jne 0x1f75
1EFE  A0 68 79        mov al, byte ptr [0x7968]
1F01  30 E4           xor ah, ah
1F03  01 46 08        add word ptr [bp + 8], ax
loc_1F06:
1F06  83 7E 08 0B     cmp word ptr [bp + 8], 0xb
1F0A  76 09           jbe 0x1f15
1F0C  FF 46 0A        inc word ptr [bp + 0xa]
1F0F  83 6E 08 0C     sub word ptr [bp + 8], 0xc
1F13  EB F1           jmp 0x1f06
loc_1F15:
1F15  B8 0B 00        mov ax, 0xb
1F18  2B 46 08        sub ax, word ptr [bp + 8]
1F1B  31 D2           xor dx, dx
1F1D  9A B9 0C E4 23  call far 23E4:0CB9
1F22  B9 84 00        mov cx, 0x84
1F25  31 F6           xor si, si
1F27  BF 00 40        mov di, 0x4000
1F2A  9A AB 0C E4 23  call far 23E4:0CAB
1F2F  52              push dx
1F30  53              push bx
1F31  50              push ax
1F32  B8 0F 00        mov ax, 0xf
1F35  2B 46 0A        sub ax, word ptr [bp + 0xa]
1F38  31 D2           xor dx, dx
1F3A  9A B9 0C E4 23  call far 23E4:0CB9
1F3F  59              pop cx
1F40  5E              pop si
1F41  5F              pop di
1F42  9A 93 0C E4 23  call far 23E4:0C93
1F47  52              push dx
1F48  53              push bx
1F49  50              push ax
1F4A  B8 82 00        mov ax, 0x82
1F4D  31 DB           xor bx, bx
1F4F  31 D2           xor dx, dx
1F51  9A 67 0E E4 23  call far 23E4:0E67
1F56  59              pop cx
1F57  5E              pop si
1F58  5F              pop di
1F59  9A A5 0C E4 23  call far 23E4:0CA5
1F5E  9A 10 0F E4 23  call far 23E4:0F10
1F63  9A C5 0C E4 23  call far 23E4:0CC5
1F68  89 46 FE        mov word ptr [bp - 2], ax
1F6B  8A 46 FE        mov al, byte ptr [bp - 2]
1F6E  E6 42           out 0x42, al
1F70  8A 46 FF        mov al, byte ptr [bp - 1]
1F73  E6 42           out 0x42, al
loc_1F75:
1F75  8B 46 06        mov ax, word ptr [bp + 6]
1F78  F7 26 66 79     mul word ptr [0x7966]
1F7C  50              push ax
1F7D  0E              push cs
1F7E  E8 88 FE        call 0x1e09
1F81  89 EC           mov sp, bp
1F83  5D              pop bp
1F84  CA 06 00        retf 6

; ---- routine 214B:1F87  (found by: far)
sub_1F87:
1F87  55              push bp
1F88  89 E5           mov bp, sp
1F8A  83 EC 0A        sub sp, 0xa
1F8D  0E              push cs
1F8E  E8 E4 FE        call 0x1e75
1F91  C4 06 FF A9     les ax, ptr [0xa9ff]
1F95  8C C2           mov dx, es
1F97  B9 0A 00        mov cx, 0xa
1F9A  31 DB           xor bx, bx
1F9C  9A 94 02 E4 23  call far 23E4:0294
1FA1  8B C8           mov cx, ax
1FA3  8B DA           mov bx, dx
1FA5  8B 46 06        mov ax, word ptr [bp + 6]
1FA8  31 D2           xor dx, dx
1FAA  9A 79 02 E4 23  call far 23E4:0279
1FAF  89 46 06        mov word ptr [bp + 6], ax
1FB2  C7 06 66 79 01 00 mov word ptr [0x7966], 1
1FB8  8B 46 06        mov ax, word ptr [bp + 6]
1FBB  89 46 F6        mov word ptr [bp - 0xa], ax
1FBE  B8 01 00        mov ax, 1
1FC1  3B 46 F6        cmp ax, word ptr [bp - 0xa]
1FC4  77 30           ja 0x1ff6
1FC6  89 46 FE        mov word ptr [bp - 2], ax
1FC9  EB 03           jmp 0x1fce
loc_1FCB:
1FCB  FF 46 FE        inc word ptr [bp - 2]
loc_1FCE:
1FCE  B8 06 00        mov ax, 6
1FD1  50              push ax
1FD2  B8 09 00        mov ax, 9
1FD5  50              push ax
1FD6  B8 01 00        mov ax, 1
1FD9  50              push ax
1FDA  0E              push cs
1FDB  E8 13 FF        call 0x1ef1
1FDE  B8 06 00        mov ax, 6
1FE1  50              push ax
1FE2  B8 07 00        mov ax, 7
1FE5  50              push ax
1FE6  B8 01 00        mov ax, 1
1FE9  50              push ax
1FEA  0E              push cs
1FEB  E8 03 FF        call 0x1ef1
1FEE  8B 46 FE        mov ax, word ptr [bp - 2]
1FF1  3B 46 F6        cmp ax, word ptr [bp - 0xa]
1FF4  75 D5           jne 0x1fcb
loc_1FF6:
1FF6  0E              push cs
1FF7  E8 93 FE        call 0x1e8d
1FFA  89 EC           mov sp, bp
1FFC  5D              pop bp
1FFD  CA 02 00        retf 2

; ---- routine 214B:2000  (found by: far)
sub_2000:
2000  55              push bp
2001  89 E5           mov bp, sp
2003  C4 7E 0A        les di, ptr [bp + 0xa]
2006  26 8B 05        mov ax, word ptr es:[di]
2009  3B 46 08        cmp ax, word ptr [bp + 8]
200C  7D 09           jge 0x2017
200E  8B 46 08        mov ax, word ptr [bp + 8]
2011  C4 7E 0A        les di, ptr [bp + 0xa]
2014  26 89 05        mov word ptr es:[di], ax
loc_2017:
2017  C4 7E 0A        les di, ptr [bp + 0xa]
201A  26 8B 05        mov ax, word ptr es:[di]
201D  3B 46 06        cmp ax, word ptr [bp + 6]
2020  7E 09           jle 0x202b
2022  8B 46 06        mov ax, word ptr [bp + 6]
2025  C4 7E 0A        les di, ptr [bp + 0xa]
2028  26 89 05        mov word ptr es:[di], ax
loc_202B:
202B  89 EC           mov sp, bp
202D  5D              pop bp
202E  CA 08 00        retf 8

; ---- routine 214B:2031  (found by: far)
sub_2031:
2031  55              push bp
2032  89 E5           mov bp, sp
2034  C4 7E 0A        les di, ptr [bp + 0xa]
2037  26 8A 05        mov al, byte ptr es:[di]
203A  3A 46 08        cmp al, byte ptr [bp + 8]
203D  7D 09           jge 0x2048
203F  8A 46 08        mov al, byte ptr [bp + 8]
2042  C4 7E 0A        les di, ptr [bp + 0xa]
2045  26 88 05        mov byte ptr es:[di], al
loc_2048:
2048  C4 7E 0A        les di, ptr [bp + 0xa]
204B  26 8A 05        mov al, byte ptr es:[di]
204E  3A 46 06        cmp al, byte ptr [bp + 6]
2051  7E 09           jle 0x205c
2053  8A 46 06        mov al, byte ptr [bp + 6]
2056  C4 7E 0A        les di, ptr [bp + 0xa]
2059  26 88 05        mov byte ptr es:[di], al
loc_205C:
205C  89 EC           mov sp, bp
205E  5D              pop bp
205F  CA 08 00        retf 8
; data (not reached as code), 8 bytes
2062                  pstr 'BAMI'
2067                  db 01 51 00   ; .Q.

; ---- routine 214B:206A  (found by: far)
sub_206A:
206A  55              push bp
206B  89 E5           mov bp, sp
206D  81 EC 00 02     sub sp, 0x200
2071  B0 00           mov al, 0
2073  08 C0           or al, al
2075  74 22           je 0x2099
2077  8D BE 00 FF     lea di, [bp - 0x100]
207B  16              push ss
207C  57              push di
207D  B8 01 00        mov ax, 1
2080  50              push ax
2081  9A 2A 19 E4 23  call far 23E4:192A
2086  BF 62 20        mov di, 0x2062
2089  0E              push cs
208A  57              push di
208B  9A 2F 07 E4 23  call far 23E4:072F
2090  74 07           je 0x2099
2092  31 C0           xor ax, ax
2094  9A D8 00 E4 23  call far 23E4:00D8
loc_2099:
2099  8D BE 00 FE     lea di, [bp - 0x200]
209D  16              push ss
209E  57              push di
209F  8D BE 00 FF     lea di, [bp - 0x100]
20A3  16              push ss
20A4  57              push di
20A5  B8 01 00        mov ax, 1
20A8  50              push ax
20A9  9A 2A 19 E4 23  call far 23E4:192A
20AE  0E              push cs
20AF  E8 EA DF        call 0x9c
20B2  BF 67 20        mov di, 0x2067
20B5  0E              push cs
20B6  57              push di
20B7  9A 2F 07 E4 23  call far 23E4:072F
20BC  74 04           je 0x20c2
20BE  B0 00           mov al, 0
20C0  EB 02           jmp 0x20c4
loc_20C2:
20C2  B0 01           mov al, 1
loc_20C4:
20C4  A2 FC A9        mov byte ptr [0xa9fc], al
20C7  E8 8B E6        call 0x755
20CA  E8 DA FC        call 0x1da7
20CD  BF 6E A9        mov di, 0xa96e
20D0  1E              push ds
20D1  57              push di
20D2  B8 A0 0F        mov ax, 0xfa0
20D5  50              push ax
20D6  0E              push cs
20D7  E8 88 E9        call 0xa62
20DA  BF 72 A9        mov di, 0xa972
20DD  1E              push ds
20DE  57              push di
20DF  B8 A0 0F        mov ax, 0xfa0
20E2  50              push ax
20E3  0E              push cs
20E4  E8 7B E9        call 0xa62
20E7  0E              push cs
20E8  E8 76 E5        call 0x661
20EB  B8 62 7B        mov ax, 0x7b62
20EE  8C DA           mov dx, ds
20F0  A3 78 A9        mov word ptr [0xa978], ax
20F3  89 16 7A A9     mov word ptr [0xa97a], dx
20F7  B8 6B 13        mov ax, 0x136b
20FA  BA 4B 21        mov dx, 0x214b   ; relocated segment word 214B
20FD  A3 52 7B        mov word ptr [0x7b52], ax
2100  89 16 54 7B     mov word ptr [0x7b54], dx
2104  0E              push cs
2105  E8 59 E5        call 0x661
2108  E8 58 FB        call 0x1c63
210B  89 EC           mov sp, bp
210D  5D              pop bp
210E  CB              retf
; data (not reached as code), 1 bytes
210F                  db 00   ; .
