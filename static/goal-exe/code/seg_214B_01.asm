; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 214B (image offsets 214B0..235BF), part 1 of 4
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 214B:0000  (found by: far)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  8B 8E 08 00     mov cx, word ptr [bp + 8]
0007  C4 BE 0A 00     les di, ptr [bp + 0xa]
000B  FC              cld
000C  8B 86 06 00     mov ax, word ptr [bp + 6]
0010  F3 AB           rep stosw word ptr es:[di], ax
0012  89 EC           mov sp, bp
0014  5D              pop bp
0015  CA 08 00        retf 8

; ---- routine 214B:0018  (found by: call, far)
sub_0018:
0018  55              push bp
0019  89 E5           mov bp, sp
001B  8B 8E 08 00     mov cx, word ptr [bp + 8]
001F  51              push cx
0020  D1 E9           shr cx, 1
0022  FC              cld
0023  C4 BE 0A 00     les di, ptr [bp + 0xa]
0027  8B 86 06 00     mov ax, word ptr [bp + 6]
002B  88 C4           mov ah, al
002D  F3 AB           rep stosw word ptr es:[di], ax
002F  59              pop cx
0030  81 E1 01 00     and cx, 1
0034  F3 AA           rep stosb byte ptr es:[di], al
0036  89 EC           mov sp, bp
0038  5D              pop bp
0039  CA 08 00        retf 8

; ---- routine 214B:003C  (found by: call, far)
sub_003C:
003C  55              push bp
003D  89 E5           mov bp, sp
003F  1E              push ds
0040  C5 B6 0C 00     lds si, ptr [bp + 0xc]
0044  C4 BE 08 00     les di, ptr [bp + 8]
0048  8B 8E 06 00     mov cx, word ptr [bp + 6]
004C  8B D1           mov dx, cx
004E  81 E2 01 00     and dx, 1
0052  89 C8           mov ax, cx
0054  D1 E9           shr cx, 1
0056  FC              cld
0057  3B F7           cmp si, di
0059  77 11           ja 0x6c
005B  FD              std
005C  03 F0           add si, ax
005E  4E              dec si
005F  03 F8           add di, ax
0061  4F              dec di
0062  80 FA 00        cmp dl, 0
0065  74 01           je 0x68
0067  A4              movsb byte ptr es:[di], byte ptr [si]
loc_0068:
0068  4E              dec si
0069  4F              dec di
006A  EB 06           jmp 0x72
loc_006C:
006C  80 FA 00        cmp dl, 0
006F  74 01           je 0x72
0071  A4              movsb byte ptr es:[di], byte ptr [si]
loc_0072:
0072  F3 A5           rep movsw word ptr es:[di], word ptr [si]
0074  1F              pop ds
0075  89 EC           mov sp, bp
0077  5D              pop bp
0078  CA 0A 00        retf 0xa

; ---- routine 214B:007B  (found by: far)
sub_007B:
007B  55              push bp
007C  89 E5           mov bp, sp
007E  1E              push ds
007F  C5 B6 0C 00     lds si, ptr [bp + 0xc]
0083  C4 BE 08 00     les di, ptr [bp + 8]
0087  8B 8E 06 00     mov cx, word ptr [bp + 6]
008B  FC              cld
008C  26 8A 05        mov al, byte ptr es:[di]
008F  86 04           xchg byte ptr [si], al
0091  46              inc si
0092  AA              stosb byte ptr es:[di], al
0093  E2 F7           loop 0x8c
0095  1F              pop ds
0096  89 EC           mov sp, bp
0098  5D              pop bp
0099  CA 0A 00        retf 0xa

; ---- routine 214B:009C  (found by: call, far)
sub_009C:
009C  55              push bp
009D  89 E5           mov bp, sp
009F  83 EC 52        sub sp, 0x52
00A2  C4 7E 06        les di, ptr [bp + 6]
00A5  06              push es
00A6  57              push di
00A7  8D 7E AF        lea di, [bp - 0x51]
00AA  16              push ss
00AB  57              push di
00AC  B8 50 00        mov ax, 0x50
00AF  50              push ax
00B0  9A 44 06 E4 23  call far 23E4:0644
00B5  1E              push ds
00B6  C5 B6 06 00     lds si, ptr [bp + 6]
00BA  C4 BE 0A 00     les di, ptr [bp + 0xa]
00BE  FC              cld
00BF  A4              movsb byte ptr es:[di], byte ptr [si]
00C0  32 ED           xor ch, ch
00C2  88 C1           mov cl, al
00C4  E3 0E           jcxz 0xd4
00C6  AC              lodsb al, byte ptr [si]
00C7  3C 61           cmp al, 0x61
00C9  72 06           jb 0xd1
00CB  3C 7A           cmp al, 0x7a
00CD  77 02           ja 0xd1
00CF  2C 20           sub al, 0x20
loc_00D1:
00D1  AA              stosb byte ptr es:[di], al
00D2  E2 F2           loop 0xc6
loc_00D4:
00D4  1F              pop ds
00D5  89 EC           mov sp, bp
00D7  5D              pop bp
00D8  CA 04 00        retf 4

; ---- routine 214B:00DB  (found by: call, far)
sub_00DB:
00DB  55              push bp
00DC  89 E5           mov bp, sp
00DE  83 7E 06 00     cmp word ptr [bp + 6], 0
00E2  7E 15           jle 0xf9
00E4  1E              push ds
00E5  C4 BE 0A 00     les di, ptr [bp + 0xa]
00E9  8B 86 08 00     mov ax, word ptr [bp + 8]
00ED  8B 8E 06 00     mov cx, word ptr [bp + 6]
00F1  FC              cld
00F2  E3 04           jcxz 0xf8
00F4  47              inc di
00F5  AA              stosb byte ptr es:[di], al
00F6  E2 FC           loop 0xf4
loc_00F8:
00F8  1F              pop ds
loc_00F9:
00F9  89 EC           mov sp, bp
00FB  5D              pop bp
00FC  CA 08 00        retf 8

; ---- routine 214B:00FF  (found by: call)
sub_00FF:
00FF  55              push bp
0100  89 E5           mov bp, sp
0102  1E              push ds
0103  C5 B6 0A 00     lds si, ptr [bp + 0xa]
0107  FC              cld
0108  8B 8E 06 00     mov cx, word ptr [bp + 6]
010C  E3 0E           jcxz 0x11c
010E  C4 BE 0E 00     les di, ptr [bp + 0xe]
0112  8B 86 08 00     mov ax, word ptr [bp + 8]
0116  86 E0           xchg al, ah
0118  AC              lodsb al, byte ptr [si]
0119  AB              stosw word ptr es:[di], ax
011A  E2 FC           loop 0x118
loc_011C:
011C  1F              pop ds
011D  89 EC           mov sp, bp
011F  5D              pop bp
0120  CA 0C 00        retf 0xc

; ---- routine 214B:0123  (found by: call)
sub_0123:
0123  55              push bp
0124  89 E5           mov bp, sp
0126  1E              push ds
0127  C5 B6 08 00     lds si, ptr [bp + 8]
012B  FD              std
012C  8B 8E 04 00     mov cx, word ptr [bp + 4]
0130  E3 0E           jcxz 0x140
0132  C4 BE 0C 00     les di, ptr [bp + 0xc]
0136  8B 86 06 00     mov ax, word ptr [bp + 6]
013A  86 E0           xchg al, ah
013C  AC              lodsb al, byte ptr [si]
013D  AB              stosw word ptr es:[di], ax
013E  E2 FC           loop 0x13c
loc_0140:
0140  1F              pop ds
0141  89 EC           mov sp, bp
0143  5D              pop bp
0144  C2 0C 00        ret 0xc

; ---- routine 214B:0147  (found by: call)
sub_0147:
0147  55              push bp
0148  89 E5           mov bp, sp
014A  1E              push ds
014B  FC              cld
014C  C5 76 06        lds si, ptr [bp + 6]
014F  C4 7E 0A        les di, ptr [bp + 0xa]
0152  AD              lodsw ax, word ptr [si]
0153  48              dec ax
0154  D1 E0           shl ax, 1
0156  01 C7           add di, ax
0158  33 D2           xor dx, dx
015A  33 C0           xor ax, ax
015C  AC              lodsb al, byte ptr [si]
015D  8B D8           mov bx, ax
015F  AC              lodsb al, byte ptr [si]
0160  89 C1           mov cx, ax
0162  D1 E1           shl cx, 1
0164  55              push bp
loc_0165:
0165  8B EF           mov bp, di
0167  03 E9           add bp, cx
loc_0169:
0169  39 EF           cmp di, bp
016B  74 0E           je 0x17b
loc_016D:
016D  AC              lodsb al, byte ptr [si]
016E  3C FF           cmp al, 0xff
0170  74 17           je 0x189
0172  3C 00           cmp al, 0
0174  74 18           je 0x18e
0176  AB              stosw word ptr es:[di], ax
0177  8B D0           mov dx, ax
0179  EB EE           jmp 0x169
loc_017B:
017B  4B              dec bx
017C  83 FB 00        cmp bx, 0
017F  74 1A           je 0x19b
0181  29 CF           sub di, cx
0183  81 C7 A0 00     add di, 0xa0
0187  EB DC           jmp 0x165
loc_0189:
0189  AC              lodsb al, byte ptr [si]
018A  88 C4           mov ah, al
018C  EB DF           jmp 0x16d
loc_018E:
018E  51              push cx
018F  AC              lodsb al, byte ptr [si]
0190  33 C9           xor cx, cx
0192  88 C1           mov cl, al
0194  8B C2           mov ax, dx
0196  F3 AB           rep stosw word ptr es:[di], ax
0198  59              pop cx
0199  EB CE           jmp 0x169
loc_019B:
019B  5D              pop bp
019C  1F              pop ds
019D  89 EC           mov sp, bp
019F  5D              pop bp
01A0  CA 08 00        retf 8

; ---- routine 214B:01A3  (found by: far)
sub_01A3:
01A3  55              push bp
01A4  89 E5           mov bp, sp
01A6  81 EC 00 01     sub sp, 0x100
01AA  C4 7E 0E        les di, ptr [bp + 0xe]
01AD  06              push es
01AE  57              push di
01AF  8D BE 00 FF     lea di, [bp - 0x100]
01B3  16              push ss
01B4  57              push di
01B5  B8 FF 00        mov ax, 0xff
01B8  50              push ax
01B9  9A 44 06 E4 23  call far 23E4:0644
01BE  8A 46 0A        mov al, byte ptr [bp + 0xa]
01C1  30 E4           xor ah, ah
01C3  D1 E0           shl ax, 1
01C5  8B C8           mov cx, ax
01C7  8A 46 0C        mov al, byte ptr [bp + 0xc]
01CA  30 E4           xor ah, ah
01CC  BA A0 00        mov dx, 0xa0
01CF  F7 E2           mul dx
01D1  C4 7E 06        les di, ptr [bp + 6]
01D4  26 C4 3D        les di, ptr es:[di]
01D7  03 F8           add di, ax
01D9  03 F9           add di, cx
01DB  81 C7 5E FF     add di, 0xff5e
01DF  06              push es
01E0  57              push di
01E1  8A 86 00 FF     mov al, byte ptr [bp - 0x100]
01E5  30 E4           xor ah, ah
01E7  8B F8           mov di, ax
01E9  8D BB 00 FF     lea di, [bp + di - 0x100]
01ED  16              push ss
01EE  57              push di
01EF  A0 B2 AA        mov al, byte ptr [0xaab2]
01F2  30 E4           xor ah, ah
01F4  50              push ax
01F5  8A 86 00 FF     mov al, byte ptr [bp - 0x100]
01F9  30 E4           xor ah, ah
01FB  50              push ax
01FC  E8 24 FF        call 0x123
01FF  89 EC           mov sp, bp
0201  5D              pop bp
0202  CA 0C 00        retf 0xc

; ---- routine 214B:0205  (found by: call, far)
sub_0205:
0205  55              push bp
0206  89 E5           mov bp, sp
0208  81 EC 00 01     sub sp, 0x100
020C  C4 7E 0E        les di, ptr [bp + 0xe]
020F  06              push es
0210  57              push di
0211  8D BE 00 FF     lea di, [bp - 0x100]
0215  16              push ss
0216  57              push di
0217  B8 FF 00        mov ax, 0xff
021A  50              push ax
021B  9A 44 06 E4 23  call far 23E4:0644
0220  8A 46 12        mov al, byte ptr [bp + 0x12]
0223  A2 B2 AA        mov byte ptr [0xaab2], al
0226  8A 46 0A        mov al, byte ptr [bp + 0xa]
0229  30 E4           xor ah, ah
022B  D1 E0           shl ax, 1
022D  8B C8           mov cx, ax
022F  8A 46 0C        mov al, byte ptr [bp + 0xc]
0232  30 E4           xor ah, ah
0234  BA A0 00        mov dx, 0xa0
0237  F7 E2           mul dx
0239  C4 7E 06        les di, ptr [bp + 6]
023C  26 C4 3D        les di, ptr es:[di]
023F  03 F8           add di, ax
0241  03 F9           add di, cx
0243  81 C7 5E FF     add di, 0xff5e
0247  06              push es
0248  57              push di
0249  8A 86 00 FF     mov al, byte ptr [bp - 0x100]
024D  30 E4           xor ah, ah
024F  8B F8           mov di, ax
0251  8D BB 00 FF     lea di, [bp + di - 0x100]
0255  16              push ss
0256  57              push di
0257  A0 B2 AA        mov al, byte ptr [0xaab2]
025A  30 E4           xor ah, ah
025C  50              push ax
025D  8A 86 00 FF     mov al, byte ptr [bp - 0x100]
0261  30 E4           xor ah, ah
0263  50              push ax
0264  E8 BC FE        call 0x123
0267  89 EC           mov sp, bp
0269  5D              pop bp
026A  CA 0E 00        retf 0xe

; ---- routine 214B:026D  (found by: call, far)
sub_026D:
026D  55              push bp
026E  89 E5           mov bp, sp
0270  81 EC 00 01     sub sp, 0x100
0274  C4 7E 0E        les di, ptr [bp + 0xe]
0277  06              push es
0278  57              push di
0279  8D BE 00 FF     lea di, [bp - 0x100]
027D  16              push ss
027E  57              push di
027F  B8 FF 00        mov ax, 0xff
0282  50              push ax
0283  9A 44 06 E4 23  call far 23E4:0644
0288  8A 46 0A        mov al, byte ptr [bp + 0xa]
028B  30 E4           xor ah, ah
028D  D1 E0           shl ax, 1
028F  8B C8           mov cx, ax
0291  8A 46 0C        mov al, byte ptr [bp + 0xc]
0294  30 E4           xor ah, ah
0296  BA A0 00        mov dx, 0xa0
0299  F7 E2           mul dx
029B  C4 7E 06        les di, ptr [bp + 6]
029E  26 C4 3D        les di, ptr es:[di]
02A1  03 F8           add di, ax
02A3  03 F9           add di, cx
02A5  81 C7 5E FF     add di, 0xff5e
02A9  06              push es
02AA  57              push di
02AB  8D BE 01 FF     lea di, [bp - 0xff]
02AF  16              push ss
02B0  57              push di
02B1  A0 B2 AA        mov al, byte ptr [0xaab2]
02B4  30 E4           xor ah, ah
02B6  50              push ax
02B7  8A 86 00 FF     mov al, byte ptr [bp - 0x100]
02BB  30 E4           xor ah, ah
02BD  50              push ax
02BE  0E              push cs
02BF  E8 3D FE        call 0xff
02C2  89 EC           mov sp, bp
02C4  5D              pop bp
02C5  CA 0C 00        retf 0xc

; ---- routine 214B:02C8  (found by: call, far)
sub_02C8:
02C8  55              push bp
02C9  89 E5           mov bp, sp
02CB  81 EC 00 01     sub sp, 0x100
02CF  C4 7E 0E        les di, ptr [bp + 0xe]
02D2  06              push es
02D3  57              push di
02D4  8D BE 00 FF     lea di, [bp - 0x100]
02D8  16              push ss
02D9  57              push di
02DA  B8 FF 00        mov ax, 0xff
02DD  50              push ax
02DE  9A 44 06 E4 23  call far 23E4:0644
02E3  8A 46 12        mov al, byte ptr [bp + 0x12]
02E6  A2 B2 AA        mov byte ptr [0xaab2], al
02E9  8A 46 0A        mov al, byte ptr [bp + 0xa]
02EC  30 E4           xor ah, ah
02EE  D1 E0           shl ax, 1
02F0  8B C8           mov cx, ax
02F2  8A 46 0C        mov al, byte ptr [bp + 0xc]
02F5  30 E4           xor ah, ah
02F7  BA A0 00        mov dx, 0xa0
02FA  F7 E2           mul dx
02FC  C4 7E 06        les di, ptr [bp + 6]
02FF  26 C4 3D        les di, ptr es:[di]
0302  03 F8           add di, ax
0304  03 F9           add di, cx
0306  81 C7 5E FF     add di, 0xff5e
030A  06              push es
030B  57              push di
030C  8D BE 01 FF     lea di, [bp - 0xff]
0310  16              push ss
0311  57              push di
0312  A0 B2 AA        mov al, byte ptr [0xaab2]
0315  30 E4           xor ah, ah
0317  50              push ax
0318  8A 86 00 FF     mov al, byte ptr [bp - 0x100]
031C  30 E4           xor ah, ah
031E  50              push ax
031F  0E              push cs
0320  E8 DC FD        call 0xff
0323  89 EC           mov sp, bp
0325  5D              pop bp
0326  CA 0E 00        retf 0xe

; ---- routine 214B:0329  (found by: call, far)
sub_0329:
0329  55              push bp
032A  89 E5           mov bp, sp
032C  C4 7E 06        les di, ptr [bp + 6]
032F  26 C4 3D        les di, ptr es:[di]
0332  06              push es
0333  57              push di
0334  C4 7E 0A        les di, ptr [bp + 0xa]
0337  06              push es
0338  57              push di
0339  0E              push cs
033A  E8 0A FE        call 0x147
033D  89 EC           mov sp, bp
033F  5D              pop bp
0340  CA 08 00        retf 8
; data (not reached as code), 13 bytes
0343                  db 01 20 02 2E 2E   ; . ...
0348                  pstr '? (Y/N)'

; ---- routine 214B:0350  (found by: call, far)
sub_0350:
0350  55              push bp
0351  89 E5           mov bp, sp
0353  81 EC 5A 01     sub sp, 0x15a
0357  C4 7E 0A        les di, ptr [bp + 0xa]
035A  06              push es
035B  57              push di
035C  8D 7E AF        lea di, [bp - 0x51]
035F  16              push ss
0360  57              push di
0361  B8 50 00        mov ax, 0x50
0364  50              push ax
0365  9A 44 06 E4 23  call far 23E4:0644
036A  80 7E B0 20     cmp byte ptr [bp - 0x50], 0x20
036E  74 28           je 0x398
0370  8D BE A7 FE     lea di, [bp - 0x159]
0374  16              push ss
0375  57              push di
0376  BF 43 03        mov di, 0x343
0379  0E              push cs
037A  57              push di
037B  9A 2A 06 E4 23  call far 23E4:062A
0380  8D 7E AF        lea di, [bp - 0x51]
0383  16              push ss
0384  57              push di
0385  9A B7 06 E4 23  call far 23E4:06B7
038A  8D 7E AF        lea di, [bp - 0x51]
038D  16              push ss
038E  57              push di
038F  B8 50 00        mov ax, 0x50
0392  50              push ax
0393  9A 44 06 E4 23  call far 23E4:0644
loc_0398:
0398  8D BE A7 FE     lea di, [bp - 0x159]
039C  16              push ss
039D  57              push di
039E  8D 7E AF        lea di, [bp - 0x51]
03A1  16              push ss
03A2  57              push di
03A3  9A 2A 06 E4 23  call far 23E4:062A
03A8  BF 43 03        mov di, 0x343
03AB  0E              push cs
03AC  57              push di
03AD  9A B7 06 E4 23  call far 23E4:06B7
03B2  8D 7E AF        lea di, [bp - 0x51]
03B5  16              push ss
03B6  57              push di
03B7  B8 50 00        mov ax, 0x50
03BA  50              push ax
03BB  9A 44 06 E4 23  call far 23E4:0644
03C0  8A 46 AF        mov al, byte ptr [bp - 0x51]
03C3  30 E4           xor ah, ah
03C5  89 46 AD        mov word ptr [bp - 0x53], ax
03C8  8B 46 AD        mov ax, word ptr [bp - 0x53]
03CB  40              inc ax
03CC  8B F8           mov di, ax
03CE  8D 7B AF        lea di, [bp + di - 0x51]
03D1  16              push ss
03D2  57              push di
03D3  B8 50 00        mov ax, 0x50
03D6  2B 46 AD        sub ax, word ptr [bp - 0x53]
03D9  50              push ax
03DA  B8 FE 00        mov ax, 0xfe
03DD  50              push ax
03DE  0E              push cs
03DF  E8 36 FC        call 0x18
03E2  B8 50 00        mov ax, 0x50
03E5  2B 46 AD        sub ax, word ptr [bp - 0x53]
03E8  31 D2           xor dx, dx
03EA  B9 02 00        mov cx, 2
03ED  F7 F1           div cx
03EF  40              inc ax
03F0  89 46 AB        mov word ptr [bp - 0x55], ax
03F3  8D 7E B0        lea di, [bp - 0x50]
03F6  16              push ss
03F7  57              push di
03F8  8B 7E AB        mov di, word ptr [bp - 0x55]
03FB  8D 7B AF        lea di, [bp + di - 0x51]
03FE  16              push ss
03FF  57              push di
0400  FF 76 AD        push word ptr [bp - 0x53]
0403  0E              push cs
0404  E8 35 FC        call 0x3c
0407  8D 7E B0        lea di, [bp - 0x50]
040A  16              push ss
040B  57              push di
040C  8B 46 AB        mov ax, word ptr [bp - 0x55]
040F  48              dec ax
0410  50              push ax
0411  B8 FE 00        mov ax, 0xfe
0414  50              push ax
0415  0E              push cs
0416  E8 FF FB        call 0x18
0419  C6 46 AF 50     mov byte ptr [bp - 0x51], 0x50
041D  BF 45 03        mov di, 0x345
0420  0E              push cs
0421  57              push di
0422  8D 7E AF        lea di, [bp - 0x51]
0425  16              push ss
0426  57              push di
0427  9A E3 06 E4 23  call far 23E4:06E3
042C  09 C0           or ax, ax
042E  75 1B           jne 0x44b
0430  A0 22 79        mov al, byte ptr [0x7922]
0433  50              push ax
0434  8D 7E AF        lea di, [bp - 0x51]
0437  16              push ss
0438  57              push di
0439  8A 46 0E        mov al, byte ptr [bp + 0xe]
043C  50              push ax
043D  B0 01           mov al, 1
043F  50              push ax
0440  C4 7E 06        les di, ptr [bp + 6]
0443  06              push es
0444  57              push di
0445  0E              push cs
0446  E8 7F FE        call 0x2c8
0449  EB 18           jmp 0x463
loc_044B:
044B  B0 82           mov al, 0x82
044D  50              push ax
044E  8D 7E AF        lea di, [bp - 0x51]
0451  16              push ss
0452  57              push di
0453  8A 46 0E        mov al, byte ptr [bp + 0xe]
0456  50              push ax
0457  B0 01           mov al, 1
0459  50              push ax
045A  C4 7E 06        les di, ptr [bp + 6]
045D  06              push es
045E  57              push di
045F  0E              push cs
0460  E8 65 FE        call 0x2c8
loc_0463:
0463  BF 48 03        mov di, 0x348
0466  0E              push cs
0467  57              push di
0468  8D 7E AF        lea di, [bp - 0x51]
046B  16              push ss
046C  57              push di
046D  9A E3 06 E4 23  call far 23E4:06E3
0472  89 46 A9        mov word ptr [bp - 0x57], ax
0475  83 7E A9 00     cmp word ptr [bp - 0x57], 0
0479  75 02           jne 0x47d
047B  EB 64           jmp 0x4e1
loc_047D:
047D  8B 46 A9        mov ax, word ptr [bp - 0x57]
0480  05 03 00        add ax, 3
0483  D1 E0           shl ax, 1
0485  8B C8           mov cx, ax
0487  8A 46 0E        mov al, byte ptr [bp + 0xe]
048A  30 E4           xor ah, ah
048C  BA A0 00        mov dx, 0xa0
048F  F7 E2           mul dx
0491  C4 7E 06        les di, ptr [bp + 6]
0494  26 C4 3D        les di, ptr es:[di]
0497  03 F8           add di, ax
0499  03 F9           add di, cx
049B  81 C7 5E FF     add di, 0xff5e
049F  06              push es
04A0  57              push di
04A1  A0 23 79        mov al, byte ptr [0x7923]
04A4  30 E4           xor ah, ah
04A6  50              push ax
04A7  B8 01 00        mov ax, 1
04AA  50              push ax
04AB  0E              push cs
04AC  E8 2C FC        call 0xdb
04AF  8B 46 A9        mov ax, word ptr [bp - 0x57]
04B2  05 05 00        add ax, 5
04B5  D1 E0           shl ax, 1
04B7  8B C8           mov cx, ax
04B9  8A 46 0E        mov al, byte ptr [bp + 0xe]
04BC  30 E4           xor ah, ah
04BE  BA A0 00        mov dx, 0xa0
04C1  F7 E2           mul dx
04C3  C4 7E 06        les di, ptr [bp + 6]
04C6  26 C4 3D        les di, ptr es:[di]
04C9  03 F8           add di, ax
04CB  03 F9           add di, cx
04CD  81 C7 5E FF     add di, 0xff5e
04D1  06              push es
04D2  57              push di
04D3  A0 23 79        mov al, byte ptr [0x7923]
04D6  30 E4           xor ah, ah
04D8  50              push ax
04D9  B8 01 00        mov ax, 1
04DC  50              push ax
04DD  0E              push cs
04DE  E8 FA FB        call 0xdb
loc_04E1:
04E1  89 EC           mov sp, bp
04E3  5D              pop bp
04E4  CA 0A 00        retf 0xa
; data (not reached as code), 17 bytes
04E7                  pstr '  PRESS ANY KEY '

; ---- routine 214B:04F8  (found by: call, far)
sub_04F8:
04F8  55              push bp
04F9  89 E5           mov bp, sp
04FB  81 EC 54 01     sub sp, 0x154
04FF  C4 7E 06        les di, ptr [bp + 6]
0502  06              push es
0503  57              push di
0504  8D 7E AF        lea di, [bp - 0x51]
0507  16              push ss
0508  57              push di
0509  B8 50 00        mov ax, 0x50
050C  50              push ax
050D  9A 44 06 E4 23  call far 23E4:0644
0512  A0 22 79        mov al, byte ptr [0x7922]
0515  30 E4           xor ah, ah
0517  89 46 AD        mov word ptr [bp - 0x53], ax
051A  A0 24 79        mov al, byte ptr [0x7924]
051D  A2 22 79        mov byte ptr [0x7922], al
0520  0E              push cs
0521  E8 01 01        call 0x625
0524  B0 19           mov al, 0x19
0526  50              push ax
0527  8D BE AD FE     lea di, [bp - 0x153]
052B  16              push ss
052C  57              push di
052D  8D 7E AF        lea di, [bp - 0x51]
0530  16              push ss
0531  57              push di
0532  9A 2A 06 E4 23  call far 23E4:062A
0537  BF E7 04        mov di, 0x4e7
053A  0E              push cs
053B  57              push di
053C  9A B7 06 E4 23  call far 23E4:06B7
0541  BF 6A A9        mov di, 0xa96a
0544  1E              push ds
0545  57              push di
0546  0E              push cs
0547  E8 06 FE        call 0x350
054A  0E              push cs
054B  E8 35 04        call 0x983
054E  0E              push cs
054F  E8 F1 00        call 0x643
0552  8A 46 AD        mov al, byte ptr [bp - 0x53]
0555  A2 22 79        mov byte ptr [0x7922], al
0558  89 EC           mov sp, bp
055A  5D              pop bp
055B  CA 04 00        retf 4
; data (not reached as code), 8 bytes
055E                  pstr '? (Y/N)'

; ---- routine 214B:0566  (found by: call, far)
sub_0566:
0566  55              push bp
0567  89 E5           mov bp, sp
0569  81 EC 52 01     sub sp, 0x152
056D  C4 7E 06        les di, ptr [bp + 6]
0570  06              push es
0571  57              push di
0572  8D 7E AE        lea di, [bp - 0x52]
0575  16              push ss
0576  57              push di
0577  B8 50 00        mov ax, 0x50
057A  50              push ax
057B  9A 44 06 E4 23  call far 23E4:0644
0580  0E              push cs
0581  E8 A1 00        call 0x625
0584  B0 19           mov al, 0x19
0586  50              push ax
0587  8D BE AE FE     lea di, [bp - 0x152]
058B  16              push ss
058C  57              push di
058D  8D 7E AE        lea di, [bp - 0x52]
0590  16              push ss
0591  57              push di
0592  9A 2A 06 E4 23  call far 23E4:062A
0597  BF 5E 05        mov di, 0x55e
059A  0E              push cs
059B  57              push di
059C  9A B7 06 E4 23  call far 23E4:06B7
05A1  BF 6A A9        mov di, 0xa96a
05A4  1E              push ds
05A5  57              push di
05A6  0E              push cs
05A7  E8 A6 FD        call 0x350
05AA  BF 46 79        mov di, 0x7946
05AD  1E              push ds
05AE  57              push di
05AF  0E              push cs
05B0  E8 F4 03        call 0x9a7
05B3  A0 76 A9        mov al, byte ptr [0xa976]
05B6  50              push ax
05B7  9A B2 19 E4 23  call far 23E4:19B2
05BC  3C 59           cmp al, 0x59
05BE  74 04           je 0x5c4
05C0  B0 00           mov al, 0
05C2  EB 02           jmp 0x5c6
loc_05C4:
05C4  B0 01           mov al, 1
loc_05C6:
05C6  88 46 FF        mov byte ptr [bp - 1], al
05C9  0E              push cs
05CA  E8 76 00        call 0x643
05CD  C6 06 76 A9 00  mov byte ptr [0xa976], 0
05D2  8A 46 FF        mov al, byte ptr [bp - 1]
05D5  89 EC           mov sp, bp
05D7  5D              pop bp
05D8  CA 04 00        retf 4

; ---- routine 214B:05DB  (found by: call, far)
sub_05DB:
05DB  55              push bp
05DC  89 E5           mov bp, sp
05DE  BF 6A 79        mov di, 0x796a
05E1  1E              push ds
05E2  57              push di
05E3  BF 6E A9        mov di, 0xa96e
05E6  1E              push ds
05E7  57              push di
05E8  0E              push cs
05E9  E8 3D FD        call 0x329
05EC  89 EC           mov sp, bp
05EE  5D              pop bp
05EF  CB              retf

; ---- routine 214B:05F0  (found by: far)
sub_05F0:
05F0  55              push bp
05F1  89 E5           mov bp, sp
05F3  83 EC 04        sub sp, 4
05F6  B8 A4 79        mov ax, 0x79a4
05F9  8C DA           mov dx, ds
05FB  89 46 FC        mov word ptr [bp - 4], ax
05FE  89 56 FE        mov word ptr [bp - 2], dx
0601  8B 46 06        mov ax, word ptr [bp + 6]
0604  48              dec ax
0605  B9 50 00        mov cx, 0x50
0608  F7 E1           mul cx
060A  40              inc ax
060B  C4 7E FC        les di, ptr [bp - 4]
060E  26 89 05        mov word ptr es:[di], ax
0611  BF A4 79        mov di, 0x79a4
0614  1E              push ds
0615  57              push di
0616  BF 6E A9        mov di, 0xa96e
0619  1E              push ds
061A  57              push di
061B  0E              push cs
061C  E8 0A FD        call 0x329
061F  89 EC           mov sp, bp
0621  5D              pop bp
0622  CA 02 00        retf 2

; ---- routine 214B:0625  (found by: call, far)
sub_0625:
0625  55              push bp
0626  89 E5           mov bp, sp
0628  C4 3E 6A A9     les di, ptr [0xa96a]
062C  81 C7 00 0F     add di, 0xf00
0630  06              push es
0631  57              push di
0632  BF 04 AA        mov di, 0xaa04
0635  1E              push ds
0636  57              push di
0637  B8 A0 00        mov ax, 0xa0
063A  50              push ax
063B  0E              push cs
063C  E8 FD F9        call 0x3c
063F  89 EC           mov sp, bp
0641  5D              pop bp
0642  CB              retf

; ---- routine 214B:0643  (found by: call, far)
sub_0643:
0643  55              push bp
0644  89 E5           mov bp, sp
0646  BF 04 AA        mov di, 0xaa04
0649  1E              push ds
064A  57              push di
064B  C4 3E 6A A9     les di, ptr [0xa96a]
064F  81 C7 00 0F     add di, 0xf00
0653  06              push es
0654  57              push di
0655  B8 A0 00        mov ax, 0xa0
0658  50              push ax
0659  0E              push cs
065A  E8 DF F9        call 0x3c
065D  89 EC           mov sp, bp
065F  5D              pop bp
0660  CB              retf

; ---- routine 214B:0661  (found by: call)
sub_0661:
0661  55              push bp
0662  89 E5           mov bp, sp
0664  83 EC 14        sub sp, 0x14
0667  C6 46 ED 02     mov byte ptr [bp - 0x13], 2
066B  C6 46 EF 00     mov byte ptr [bp - 0x11], 0
066F  C6 46 F3 1A     mov byte ptr [bp - 0xd], 0x1a
0673  C6 46 F2 01     mov byte ptr [bp - 0xe], 1
0677  B0 10           mov al, 0x10
0679  50              push ax
067A  8D 7E EC        lea di, [bp - 0x14]
067D  16              push ss
067E  57              push di
067F  9A 0B 00 5C 23  call far 235C:000B
0684  89 EC           mov sp, bp
0686  5D              pop bp
0687  CB              retf

; ---- routine 214B:0688  (found by: call, far)
sub_0688:
0688  55              push bp
0689  89 E5           mov bp, sp
068B  83 EC 02        sub sp, 2
068E  1E              push ds
068F  C5 76 08        lds si, ptr [bp + 8]
0692  1E              push ds
0693  56              push si
0694  AD              lodsw ax, word ptr [si]
0695  BB BD 7A        mov bx, 0x7abd
0698  F7 E3           mul bx
069A  05 0F 1B        add ax, 0x1b0f
069D  5F              pop di
069E  07              pop es
069F  AB              stosw word ptr es:[di], ax
06A0  F7 66 06        mul word ptr [bp + 6]
06A3  1F              pop ds
06A4  42              inc dx
06A5  89 56 FE        mov word ptr [bp - 2], dx
06A8  8B 46 FE        mov ax, word ptr [bp - 2]
06AB  89 EC           mov sp, bp
06AD  5D              pop bp
06AE  CA 06 00        retf 6

; ---- routine 214B:06B1  (found by: far)
sub_06B1:
06B1  55              push bp
06B2  89 E5           mov bp, sp
06B4  83 EC 02        sub sp, 2
06B7  C4 3E 78 A9     les di, ptr [0xa978]
06BB  06              push es
06BC  57              push di
06BD  FF 76 06        push word ptr [bp + 6]
06C0  0E              push cs
06C1  E8 C4 FF        call 0x688
06C4  89 46 FE        mov word ptr [bp - 2], ax
06C7  8B 46 FE        mov ax, word ptr [bp - 2]
06CA  89 EC           mov sp, bp
06CC  5D              pop bp
06CD  CA 02 00        retf 2

; ---- routine 214B:06D0  (found by: far)
sub_06D0:
06D0  55              push bp
06D1  89 E5           mov bp, sp
06D3  83 EC 02        sub sp, 2
06D6  C4 3E 78 A9     les di, ptr [0xa978]
06DA  06              push es
06DB  57              push di
06DC  FF 76 06        push word ptr [bp + 6]
06DF  0E              push cs
06E0  E8 A5 FF        call 0x688
06E3  3D 01 00        cmp ax, 1
06E6  74 04           je 0x6ec
06E8  B0 00           mov al, 0
06EA  EB 02           jmp 0x6ee
loc_06EC:
06EC  B0 01           mov al, 1
loc_06EE:
06EE  88 46 FF        mov byte ptr [bp - 1], al
06F1  8A 46 FF        mov al, byte ptr [bp - 1]
06F4  89 EC           mov sp, bp
06F6  5D              pop bp
06F7  CA 02 00        retf 2

; ---- routine 214B:06FA  (found by: far)
sub_06FA:
06FA  55              push bp
06FB  89 E5           mov bp, sp
06FD  83 EC 02        sub sp, 2
0700  C4 3E 78 A9     les di, ptr [0xa978]
0704  06              push es
0705  57              push di
0706  B8 02 00        mov ax, 2
0709  50              push ax
070A  0E              push cs
070B  E8 7A FF        call 0x688
070E  3D 01 00        cmp ax, 1
0711  74 04           je 0x717
0713  B0 00           mov al, 0
0715  EB 02           jmp 0x719
loc_0717:
0717  B0 01           mov al, 1
loc_0719:
0719  88 46 FF        mov byte ptr [bp - 1], al
071C  8A 46 FF        mov al, byte ptr [bp - 1]
071F  89 EC           mov sp, bp
0721  5D              pop bp
0722  CB              retf

; ---- routine 214B:0723  (found by: call, far)
sub_0723:
0723  55              push bp
0724  89 E5           mov bp, sp
0726  83 EC 16        sub sp, 0x16
0729  C6 46 EC 01     mov byte ptr [bp - 0x14], 1
072D  B0 16           mov al, 0x16
072F  50              push ax
0730  8D 7E EB        lea di, [bp - 0x15]
0733  16              push ss
0734  57              push di
0735  9A 0B 00 5C 23  call far 235C:000B
073A  8B 46 FD        mov ax, word ptr [bp - 3]
073D  25 40 00        and ax, 0x40
0740  3D 40 00        cmp ax, 0x40
0743  75 04           jne 0x749
0745  B0 00           mov al, 0
0747  EB 02           jmp 0x74b
loc_0749:
0749  B0 01           mov al, 1
loc_074B:
074B  88 46 FF        mov byte ptr [bp - 1], al
074E  8A 46 FF        mov al, byte ptr [bp - 1]
0751  89 EC           mov sp, bp
0753  5D              pop bp
0754  CB              retf

; ---- routine 214B:0755  (found by: call)
sub_0755:
0755  55              push bp
0756  89 E5           mov bp, sp
0758  BE 40 00        mov si, 0x40
075B  8E C6           mov es, si
075D  26 80 3E 49 00 07 cmp byte ptr es:[0x49], 7
0763  74 04           je 0x769
0765  B0 00           mov al, 0
0767  EB 02           jmp 0x76b
loc_0769:
0769  B0 01           mov al, 1
loc_076B:
076B  A2 64 A9        mov byte ptr [0xa964], al
076E  80 3E 64 A9 00  cmp byte ptr [0xa964], 0
0773  74 0E           je 0x783
0775  C7 06 6A A9 00 00 mov word ptr [0xa96a], 0
077B  C7 06 6C A9 00 B0 mov word ptr [0xa96c], 0xb000
0781  EB 22           jmp 0x7a5
loc_0783:
0783  BE 40 00        mov si, 0x40
0786  8E C6           mov es, si
0788  26 80 3E 49 00 03 cmp byte ptr es:[0x49], 3
078E  74 09           je 0x799
0790  B8 03 00        mov ax, 3
0793  50              push ax
0794  9A 6D 01 82 23  call far 2382:016D
loc_0799:
0799  C7 06 6A A9 00 00 mov word ptr [0xa96a], 0
079F  C7 06 6C A9 00 B8 mov word ptr [0xa96c], 0xb800
loc_07A5:
07A5  89 EC           mov sp, bp
07A7  5D              pop bp
07A8  C3              ret
; data (not reached as code), 106 bytes
07A9                  pstr 'Type EXIT to return...'
07C0                  pstr 'COMSPEC'
07C8                  db 00   ; .
07C9                  pstr 'Not enough memory'
07DB                  pstr 'Cannot find "COMMAND.COM"'
07F5                  pstr 'Error trying to run DOS shell'

; ---- routine 214B:0813  (found by: call)
sub_0813:
0813  55              push bp
0814  89 E5           mov bp, sp
0816  81 EC 00 01     sub sp, 0x100
081A  C4 3E 6A A9     les di, ptr [0xa96a]
081E  06              push es
081F  57              push di
0820  C4 3E 72 A9     les di, ptr [0xa972]
0824  06              push es
0825  57              push di
0826  B8 A0 0F        mov ax, 0xfa0
0829  50              push ax
082A  9A 5D 02 E4 23  call far 23E4:025D
082F  B0 01           mov al, 1
0831  50              push ax
0832  B0 01           mov al, 1
0834  50              push ax
0835  9A 15 02 82 23  call far 2382:0215
083A  0E              push cs
083B  E8 9D FD        call 0x5db
083E  C4 3E 6E A9     les di, ptr [0xa96e]
0842  06              push es
0843  57              push di
0844  C4 3E 6A A9     les di, ptr [0xa96a]
0848  06              push es
0849  57              push di
084A  B8 A0 0F        mov ax, 0xfa0
084D  50              push ax
084E  9A 5D 02 E4 23  call far 23E4:025D
0853  C6 06 B2 AA 0F  mov byte ptr [0xaab2], 0xf
0858  BF C0 AB        mov di, 0xabc0
085B  1E              push ds
085C  57              push di
085D  BF A9 07        mov di, 0x7a9
0860  0E              push cs
0861  57              push di
0862  31 C0           xor ax, ax
0864  50              push ax
0865  9A 3B 17 E4 23  call far 23E4:173B
086A  9A BE 16 E4 23  call far 23E4:16BE
086F  8D BE 00 FF     lea di, [bp - 0x100]
0873  16              push ss
0874  57              push di
0875  BF C0 07        mov di, 0x7c0
0878  0E              push cs
0879  57              push di
087A  9A F2 01 5C 23  call far 235C:01F2
087F  BF C8 07        mov di, 0x7c8
0882  0E              push cs
0883  57              push di
0884  9A 59 01 5C 23  call far 235C:0159
0889  83 3E A6 AA 08  cmp word ptr [0xaaa6], 8
088E  75 0B           jne 0x89b
0890  BF C9 07        mov di, 0x7c9
0893  0E              push cs
0894  57              push di
0895  0E              push cs
0896  E8 5F FC        call 0x4f8
0899  EB 22           jmp 0x8bd
loc_089B:
089B  83 3E A6 AA 02  cmp word ptr [0xaaa6], 2
08A0  75 0B           jne 0x8ad
08A2  BF DB 07        mov di, 0x7db
08A5  0E              push cs
08A6  57              push di
08A7  0E              push cs
08A8  E8 4D FC        call 0x4f8
08AB  EB 10           jmp 0x8bd
loc_08AD:
08AD  83 3E A6 AA 00  cmp word ptr [0xaaa6], 0
08B2  74 09           je 0x8bd
08B4  BF F5 07        mov di, 0x7f5
08B7  0E              push cs
08B8  57              push di
08B9  0E              push cs
08BA  E8 3B FC        call 0x4f8
loc_08BD:
08BD  E8 95 FE        call 0x755
08C0  C4 3E 72 A9     les di, ptr [0xa972]
08C4  06              push es
08C5  57              push di
08C6  C4 3E 6A A9     les di, ptr [0xa96a]
08CA  06              push es
08CB  57              push di
08CC  B8 A0 0F        mov ax, 0xfa0
08CF  50              push ax
08D0  9A 5D 02 E4 23  call far 23E4:025D
08D5  0E              push cs
08D6  E8 88 FD        call 0x661
08D9  89 EC           mov sp, bp
08DB  5D              pop bp
08DC  C3              ret

