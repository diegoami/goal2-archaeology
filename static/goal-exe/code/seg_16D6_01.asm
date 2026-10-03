; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 16D6 (image offsets 16D60..1770F), part 1 of 2
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 16D6:0000  (found by: call)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  83 EC 02        sub sp, 2
0006  FC              cld
0007  C4 7E 06        les di, ptr [bp + 6]
000A  8B 4E 04        mov cx, word ptr [bp + 4]
000D  33 D2           xor dx, dx
000F  B0 0A           mov al, 0xa
loc_0011:
0011  F2 AE           repne scasb al, byte ptr es:[di]
0013  42              inc dx
0014  83 F9 00        cmp cx, 0
0017  77 F8           ja 0x11
0019  89 56 FE        mov word ptr [bp - 2], dx
001C  8B 46 FE        mov ax, word ptr [bp - 2]
001F  89 EC           mov sp, bp
0021  5D              pop bp
0022  C2 06 00        ret 6

; ---- routine 16D6:0025  (found by: call)
sub_0025:
0025  55              push bp
0026  89 E5           mov bp, sp
0028  83 EC 02        sub sp, 2
002B  1E              push ds
002C  C5 76 08        lds si, ptr [bp + 8]
002F  FC              cld
0030  8B 5E 04        mov bx, word ptr [bp + 4]
0033  80 7E 0C 01     cmp byte ptr [bp + 0xc], 1
0037  74 04           je 0x3d
0039  FD              std
003A  E9 07 00        jmp 0x44
loc_003D:
003D  8B 56 06        mov dx, word ptr [bp + 6]
0040  2B D3           sub dx, bx
0042  89 D3           mov bx, dx
loc_0044:
0044  33 C9           xor cx, cx
0046  8B 56 0E        mov dx, word ptr [bp + 0xe]
loc_0049:
0049  41              inc cx
004A  AC              lodsb al, byte ptr [si]
004B  83 FB 00        cmp bx, 0
004E  74 0B           je 0x5b
0050  4B              dec bx
0051  3C 0A           cmp al, 0xa
0053  75 F4           jne 0x49
0055  4A              dec dx
0056  83 FA 00        cmp dx, 0
0059  75 EE           jne 0x49
loc_005B:
005B  89 4E FE        mov word ptr [bp - 2], cx
005E  1F              pop ds
005F  8B 46 FE        mov ax, word ptr [bp - 2]
0062  89 EC           mov sp, bp
0064  5D              pop bp
0065  C2 0C 00        ret 0xc

; ---- routine 16D6:0068  (found by: call)
sub_0068:
0068  55              push bp
0069  89 E5           mov bp, sp
006B  81 EC 06 01     sub sp, 0x106
006F  C4 46 06        les ax, ptr [bp + 6]
0072  8C C2           mov dx, es
0074  89 46 FA        mov word ptr [bp - 6], ax
0077  89 56 FC        mov word ptr [bp - 4], dx
007A  C4 7E FA        les di, ptr [bp - 6]
007D  26 8A 05        mov al, byte ptr es:[di]
0080  88 46 FE        mov byte ptr [bp - 2], al
0083  8A 46 04        mov al, byte ptr [bp + 4]
0086  C4 7E FA        les di, ptr [bp - 6]
0089  26 88 05        mov byte ptr es:[di], al
008C  C4 7E FA        les di, ptr [bp - 6]
008F  06              push es
0090  57              push di
0091  8D BE FA FE     lea di, [bp - 0x106]
0095  16              push ss
0096  57              push di
0097  C4 7E FA        les di, ptr [bp - 6]
009A  06              push es
009B  57              push di
009C  9A 9C 00 4B 21  call far 214B:009C
00A1  9A 2F 07 E4 23  call far 23E4:072F
00A6  74 04           je 0xac
00A8  B0 00           mov al, 0
00AA  EB 02           jmp 0xae
loc_00AC:
00AC  B0 01           mov al, 1
loc_00AE:
00AE  88 46 FF        mov byte ptr [bp - 1], al
00B1  8A 46 FE        mov al, byte ptr [bp - 2]
00B4  C4 7E FA        les di, ptr [bp - 6]
00B7  26 88 05        mov byte ptr es:[di], al
00BA  8A 46 FF        mov al, byte ptr [bp - 1]
00BD  89 EC           mov sp, bp
00BF  5D              pop bp
00C0  C2 06 00        ret 6

; ---- routine 16D6:00C3  (found by: call)
sub_00C3:
00C3  55              push bp
00C4  89 E5           mov bp, sp
00C6  83 EC 02        sub sp, 2
00C9  1E              push ds
00CA  8B 4E 06        mov cx, word ptr [bp + 6]
00CD  C5 76 08        lds si, ptr [bp + 8]
00D0  32 F6           xor dh, dh
00D2  8A 56 0C        mov dl, byte ptr [bp + 0xc]
00D5  33 DB           xor bx, bx
00D7  E3 18           jcxz 0xf1
00D9  80 7E 0E 01     cmp byte ptr [bp + 0xe], 1
00DD  74 04           je 0xe3
00DF  FD              std
00E0  E9 01 00        jmp 0xe4
loc_00E3:
00E3  FC              cld
loc_00E4:
00E4  AC              lodsb al, byte ptr [si]
00E5  43              inc bx
00E6  83 FB 00        cmp bx, 0
00E9  74 06           je 0xf1
00EB  38 D0           cmp al, dl
00ED  75 F5           jne 0xe4
00EF  E2 F3           loop 0xe4
loc_00F1:
00F1  89 5E FE        mov word ptr [bp - 2], bx
00F4  1F              pop ds
00F5  8B 46 FE        mov ax, word ptr [bp - 2]
00F8  89 EC           mov sp, bp
00FA  5D              pop bp
00FB  CA 0A 00        retf 0xa

; ---- routine 16D6:00FE  (found by: call)
sub_00FE:
00FE  55              push bp
00FF  89 E5           mov bp, sp
0101  83 EC 08        sub sp, 8
0104  C6 06 B2 AA 06  mov byte ptr [0xaab2], 6
0109  8B 46 04        mov ax, word ptr [bp + 4]
010C  3B 06 B6 99     cmp ax, word ptr [0x99b6]
0110  72 03           jb 0x115
0112  E9 9D 00        jmp 0x1b2
loc_0115:
0115  B0 01           mov al, 1
0117  50              push ax
0118  B0 0A           mov al, 0xa
011A  50              push ax
011B  8B 46 06        mov ax, word ptr [bp + 6]
011E  C4 3E B0 99     les di, ptr [0x99b0]
0122  03 F8           add di, ax
0124  06              push es
0125  57              push di
0126  B8 01 00        mov ax, 1
0129  50              push ax
012A  0E              push cs
012B  E8 95 FF        call 0xc3
012E  2D 02 00        sub ax, 2
0131  89 46 FE        mov word ptr [bp - 2], ax
0134  83 7E FE 00     cmp word ptr [bp - 2], 0
0138  7E 78           jle 0x1b2
013A  8B 46 06        mov ax, word ptr [bp + 6]
013D  48              dec ax
013E  C4 3E B0 99     les di, ptr [0x99b0]
0142  03 F8           add di, ax
0144  89 F8           mov ax, di
0146  8C C2           mov dx, es
0148  52              push dx
0149  50              push ax
014A  8A 46 FE        mov al, byte ptr [bp - 2]
014D  50              push ax
014E  E8 17 FF        call 0x68
0151  08 C0           or al, al
0153  74 05           je 0x15a
0155  C6 06 B2 AA 02  mov byte ptr [0xaab2], 2
loc_015A:
015A  8B 46 06        mov ax, word ptr [bp + 6]
015D  48              dec ax
015E  C4 3E B0 99     les di, ptr [0x99b0]
0162  03 F8           add di, ax
0164  89 F8           mov ax, di
0166  8C C2           mov dx, es
0168  89 46 FA        mov word ptr [bp - 6], ax
016B  89 56 FC        mov word ptr [bp - 4], dx
016E  C4 7E FA        les di, ptr [bp - 6]
0171  26 8A 05        mov al, byte ptr es:[di]
0174  88 46 F9        mov byte ptr [bp - 7], al
0177  B8 50 00        mov ax, 0x50
017A  31 D2           xor dx, dx
017C  52              push dx
017D  50              push ax
017E  8B 46 FE        mov ax, word ptr [bp - 2]
0181  99              cdq
0182  52              push dx
0183  50              push ax
0184  9A 1C 0D 4B 21  call far 214B:0D1C
0189  C4 7E FA        les di, ptr [bp - 6]
018C  26 88 05        mov byte ptr es:[di], al
018F  A0 B2 AA        mov al, byte ptr [0xaab2]
0192  50              push ax
0193  C4 7E FA        les di, ptr [bp - 6]
0196  06              push es
0197  57              push di
0198  A0 BA 99        mov al, byte ptr [0x99ba]
019B  50              push ax
019C  B0 01           mov al, 1
019E  50              push ax
019F  BF 6E A9        mov di, 0xa96e
01A2  1E              push ds
01A3  57              push di
01A4  9A C8 02 4B 21  call far 214B:02C8
01A9  8A 46 F9        mov al, byte ptr [bp - 7]
01AC  C4 7E FA        les di, ptr [bp - 6]
01AF  26 88 05        mov byte ptr es:[di], al
loc_01B2:
01B2  FE 06 BA 99     inc byte ptr [0x99ba]
01B6  89 EC           mov sp, bp
01B8  5D              pop bp
01B9  C2 04 00        ret 4

; ---- routine 16D6:01BC  (found by: call)
sub_01BC:
01BC  55              push bp
01BD  89 E5           mov bp, sp
01BF  83 EC 02        sub sp, 2
01C2  A0 F2 0A        mov al, byte ptr [0xaf2]
01C5  30 E4           xor ah, ah
01C7  03 06 EE 0A     add ax, word ptr [0xaee]
01CB  3B 06 B6 99     cmp ax, word ptr [0x99b6]
01CF  75 06           jne 0x1d7
01D1  80 7E 04 01     cmp byte ptr [bp + 4], 1
01D5  74 11           je 0x1e8
loc_01D7:
01D7  83 3E EE 0A 01  cmp word ptr [0xaee], 1
01DC  75 06           jne 0x1e4
01DE  80 7E 04 FF     cmp byte ptr [bp + 4], 0xff
01E2  74 04           je 0x1e8
loc_01E4:
01E4  B0 00           mov al, 0
01E6  EB 02           jmp 0x1ea
loc_01E8:
01E8  B0 01           mov al, 1
loc_01EA:
01EA  88 46 FF        mov byte ptr [bp - 1], al
01ED  8A 46 FF        mov al, byte ptr [bp - 1]
01F0  89 EC           mov sp, bp
01F2  5D              pop bp
01F3  C2 02 00        ret 2

; ---- routine 16D6:01F6  (found by: call)
sub_01F6:
01F6  55              push bp
01F7  89 E5           mov bp, sp
01F9  8A 46 06        mov al, byte ptr [bp + 6]
01FC  50              push ax
01FD  E8 BC FF        call 0x1bc
0200  08 C0           or al, al
0202  74 02           je 0x206
0204  EB 5A           jmp 0x260
loc_0206:
0206  80 7E 06 01     cmp byte ptr [bp + 6], 1
020A  75 1E           jne 0x22a
020C  B0 01           mov al, 1
020E  50              push ax
020F  B0 0A           mov al, 0xa
0211  50              push ax
0212  A1 F0 0A        mov ax, word ptr [0xaf0]
0215  C4 3E B0 99     les di, ptr [0x99b0]
0219  03 F8           add di, ax
021B  06              push es
021C  57              push di
021D  FF 76 04        push word ptr [bp + 4]
0220  0E              push cs
0221  E8 9F FE        call 0xc3
0224  01 06 F0 0A     add word ptr [0xaf0], ax
0228  EB 1F           jmp 0x249
loc_022A:
022A  B0 00           mov al, 0
022C  50              push ax
022D  B0 0A           mov al, 0xa
022F  50              push ax
0230  A1 F0 0A        mov ax, word ptr [0xaf0]
0233  2D 02 00        sub ax, 2
0236  C4 3E B0 99     les di, ptr [0x99b0]
023A  03 F8           add di, ax
023C  06              push es
023D  57              push di
023E  FF 76 04        push word ptr [bp + 4]
0241  0E              push cs
0242  E8 7E FE        call 0xc3
0245  29 06 F0 0A     sub word ptr [0xaf0], ax
loc_0249:
0249  8A 46 06        mov al, byte ptr [bp + 6]
024C  98              cwde
024D  99              cdq
024E  8B C8           mov cx, ax
0250  8B DA           mov bx, dx
0252  8B 46 04        mov ax, word ptr [bp + 4]
0255  31 D2           xor dx, dx
0257  9A 79 02 E4 23  call far 23E4:0279
025C  01 06 EE 0A     add word ptr [0xaee], ax
loc_0260:
0260  89 EC           mov sp, bp
0262  5D              pop bp
0263  C2 04 00        ret 4

; ---- routine 16D6:0266  (found by: call)
sub_0266:
0266  55              push bp
0267  89 E5           mov bp, sp
0269  83 EC 04        sub sp, 4
026C  80 7E 06 00     cmp byte ptr [bp + 6], 0
0270  74 0A           je 0x27c
0272  8A 46 06        mov al, byte ptr [bp + 6]
0275  50              push ax
0276  FF 76 04        push word ptr [bp + 4]
0279  E8 7A FF        call 0x1f6
loc_027C:
027C  A1 F0 0A        mov ax, word ptr [0xaf0]
027F  89 46 FD        mov word ptr [bp - 3], ax
0282  C6 06 BA 99 01  mov byte ptr [0x99ba], 1
0287  9A DB 05 4B 21  call far 214B:05DB
028C  C6 46 FF 01     mov byte ptr [bp - 1], 1
0290  EB 03           jmp 0x295
loc_0292:
0292  FE 46 FF        inc byte ptr [bp - 1]
loc_0295:
0295  FF 76 FD        push word ptr [bp - 3]
0298  8A 46 FF        mov al, byte ptr [bp - 1]
029B  30 E4           xor ah, ah
029D  03 06 EE 0A     add ax, word ptr [0xaee]
02A1  48              dec ax
02A2  50              push ax
02A3  E8 58 FE        call 0xfe
02A6  8B 46 FD        mov ax, word ptr [bp - 3]
02A9  3B 06 B4 99     cmp ax, word ptr [0x99b4]
02AD  73 1C           jae 0x2cb
02AF  B0 01           mov al, 1
02B1  50              push ax
02B2  B0 0A           mov al, 0xa
02B4  50              push ax
02B5  8B 46 FD        mov ax, word ptr [bp - 3]
02B8  C4 3E B0 99     les di, ptr [0x99b0]
02BC  03 F8           add di, ax
02BE  06              push es
02BF  57              push di
02C0  B8 01 00        mov ax, 1
02C3  50              push ax
02C4  0E              push cs
02C5  E8 FB FD        call 0xc3
02C8  01 46 FD        add word ptr [bp - 3], ax
loc_02CB:
02CB  80 7E FF 18     cmp byte ptr [bp - 1], 0x18
02CF  75 C1           jne 0x292
02D1  BF F4 0A        mov di, 0xaf4
02D4  1E              push ds
02D5  57              push di
02D6  BF 6E A9        mov di, 0xa96e
02D9  1E              push ds
02DA  57              push di
02DB  9A 29 03 4B 21  call far 214B:0329
02E0  C4 3E 6E A9     les di, ptr [0xa96e]
02E4  06              push es
02E5  57              push di
02E6  C4 3E 6A A9     les di, ptr [0xa96a]
02EA  06              push es
02EB  57              push di
02EC  B8 A0 0F        mov ax, 0xfa0
02EF  50              push ax
02F0  9A 5D 02 E4 23  call far 23E4:025D
02F5  89 EC           mov sp, bp
02F7  5D              pop bp
02F8  C2 04 00        ret 4

; ---- routine 16D6:02FB  (found by: call)
sub_02FB:
02FB  55              push bp
02FC  89 E5           mov bp, sp
02FE  8B 46 06        mov ax, word ptr [bp + 6]
0301  A3 EE 0A        mov word ptr [0xaee], ax
0304  8B 46 04        mov ax, word ptr [bp + 4]
0307  A3 F0 0A        mov word ptr [0xaf0], ax
030A  80 3E F2 0A 01  cmp byte ptr [0xaf2], 1
030F  75 06           jne 0x317
0311  83 7E 06 01     cmp word ptr [bp + 6], 1
0315  74 0C           je 0x323
loc_0317:
0317  B0 FF           mov al, 0xff
0319  50              push ax
031A  A0 F2 0A        mov al, byte ptr [0xaf2]
031D  30 E4           xor ah, ah
031F  50              push ax
0320  E8 D3 FE        call 0x1f6
loc_0323:
0323  B0 00           mov al, 0
0325  50              push ax
0326  E8 44 00        call 0x36d
0329  89 EC           mov sp, bp
032B  5D              pop bp
032C  C2 04 00        ret 4

; ---- routine 16D6:032F  (found by: call)
sub_032F:
032F  55              push bp
0330  89 E5           mov bp, sp
0332  8A 46 04        mov al, byte ptr [bp + 4]
0335  A2 F2 0A        mov byte ptr [0xaf2], al
0338  B8 01 00        mov ax, 1
033B  50              push ax
033C  B8 01 00        mov ax, 1
033F  50              push ax
0340  E8 B8 FF        call 0x2fb
0343  89 EC           mov sp, bp
0345  5D              pop bp
0346  C2 02 00        ret 2

; ---- routine 16D6:0349  (found by: call)
sub_0349:
0349  55              push bp
034A  89 E5           mov bp, sp
034C  B0 01           mov al, 1
034E  50              push ax
034F  E8 6A FE        call 0x1bc
0352  08 C0           or al, al
0354  74 02           je 0x358
0356  EB 11           jmp 0x369
loc_0358:
0358  C6 06 F2 0A 17  mov byte ptr [0xaf2], 0x17
035D  FF 36 B6 99     push word ptr [0x99b6]
0361  A1 B4 99        mov ax, word ptr [0x99b4]
0364  48              dec ax
0365  50              push ax
0366  E8 92 FF        call 0x2fb
loc_0369:
0369  89 EC           mov sp, bp
036B  5D              pop bp
036C  C3              ret

; ---- routine 16D6:036D  (found by: call)
sub_036D:
036D  55              push bp
036E  89 E5           mov bp, sp
0370  8A 46 04        mov al, byte ptr [bp + 4]
0373  50              push ax
0374  E8 45 FE        call 0x1bc
0377  08 C0           or al, al
0379  74 02           je 0x37d
037B  EB 44           jmp 0x3c1
loc_037D:
037D  80 7E 04 00     cmp byte ptr [bp + 4], 0
0381  74 1F           je 0x3a2
0383  80 7E 04 FF     cmp byte ptr [bp + 4], 0xff
0387  75 07           jne 0x390
0389  83 3E EE 0A 17  cmp word ptr [0xaee], 0x17
038E  77 12           ja 0x3a2
loc_0390:
0390  80 7E 04 01     cmp byte ptr [bp + 4], 1
0394  75 19           jne 0x3af
0396  A1 EE 0A        mov ax, word ptr [0xaee]
0399  05 2E 00        add ax, 0x2e
039C  3B 06 B6 99     cmp ax, word ptr [0x99b6]
03A0  77 0D           ja 0x3af
loc_03A2:
03A2  8A 46 04        mov al, byte ptr [bp + 4]
03A5  50              push ax
03A6  B8 17 00        mov ax, 0x17
03A9  50              push ax
03AA  E8 B9 FE        call 0x266
03AD  EB 12           jmp 0x3c1
loc_03AF:
03AF  80 7E 04 FF     cmp byte ptr [bp + 4], 0xff
03B3  75 09           jne 0x3be
03B5  B8 01 00        mov ax, 1
03B8  50              push ax
03B9  E8 73 FF        call 0x32f
03BC  EB 03           jmp 0x3c1
loc_03BE:
03BE  E8 88 FF        call 0x349
loc_03C1:
03C1  89 EC           mov sp, bp
03C3  5D              pop bp
03C4  C2 02 00        ret 2

; ---- routine 16D6:03C7  (found by: call)
sub_03C7:
03C7  55              push bp
03C8  89 E5           mov bp, sp
03CA  80 7E 04 01     cmp byte ptr [bp + 4], 1
03CE  75 0C           jne 0x3dc
03D0  A1 EE 0A        mov ax, word ptr [0xaee]
03D3  05 17 00        add ax, 0x17
03D6  3B 06 B6 99     cmp ax, word ptr [0x99b6]
03DA  72 06           jb 0x3e2
loc_03DC:
03DC  80 7E 04 FF     cmp byte ptr [bp + 4], 0xff
03E0  75 0B           jne 0x3ed
loc_03E2:
03E2  8A 46 04        mov al, byte ptr [bp + 4]
03E5  50              push ax
03E6  B8 01 00        mov ax, 1
03E9  50              push ax
03EA  E8 09 FE        call 0x1f6
loc_03ED:
03ED  B0 00           mov al, 0
03EF  50              push ax
03F0  E8 7A FF        call 0x36d
03F3  89 EC           mov sp, bp
03F5  5D              pop bp
03F6  C2 02 00        ret 2

; ---- routine 16D6:03F9  (found by: call)
sub_03F9:
03F9  55              push bp
03FA  89 E5           mov bp, sp
03FC  83 3E B6 99 02  cmp word ptr [0x99b6], 2
0401  73 06           jae 0x409
0403  C7 06 B6 99 02 00 mov word ptr [0x99b6], 2
loc_0409:
0409  B8 01 00        mov ax, 1
040C  50              push ax
040D  B0 00           mov al, 0
040F  50              push ax
0410  8B 46 04        mov ax, word ptr [bp + 4]
0413  C4 3E B0 99     les di, ptr [0x99b0]
0417  03 F8           add di, ax
0419  06              push es
041A  57              push di
041B  FF 36 B4 99     push word ptr [0x99b4]
041F  FF 76 04        push word ptr [bp + 4]
0422  E8 00 FC        call 0x25
0425  8B D0           mov dx, ax
0427  8B 46 04        mov ax, word ptr [bp + 4]
042A  2B C2           sub ax, dx
042C  05 02 00        add ax, 2
042F  A3 F0 0A        mov word ptr [0xaf0], ax
0432  C4 3E B0 99     les di, ptr [0x99b0]
0436  81 C7 01 00     add di, 1
043A  06              push es
043B  57              push di
043C  FF 36 F0 0A     push word ptr [0xaf0]
0440  E8 BD FB        call 0
0443  A3 EE 0A        mov word ptr [0xaee], ax
0446  8B 46 04        mov ax, word ptr [bp + 4]
0449  40              inc ax
044A  2B 06 F0 0A     sub ax, word ptr [0xaf0]
044E  A2 F3 0A        mov byte ptr [0xaf3], al
0451  A1 F0 0A        mov ax, word ptr [0xaf0]
0454  3B 06 B4 99     cmp ax, word ptr [0x99b4]
0458  76 05           jbe 0x45f
045A  E8 EC FE        call 0x349
045D  EB 24           jmp 0x483
loc_045F:
045F  83 3E EE 0A 17  cmp word ptr [0xaee], 0x17
0464  73 09           jae 0x46f
0466  FF 36 EE 0A     push word ptr [0xaee]
046A  E8 C2 FE        call 0x32f
046D  EB 14           jmp 0x483
loc_046F:
046F  80 3E F2 0A 01  cmp byte ptr [0xaf2], 1
0474  74 0D           je 0x483
0476  B0 FF           mov al, 0xff
0478  50              push ax
0479  A0 F2 0A        mov al, byte ptr [0xaf2]
047C  30 E4           xor ah, ah
047E  48              dec ax
047F  50              push ax
0480  E8 73 FD        call 0x1f6
loc_0483:
0483  89 EC           mov sp, bp
0485  5D              pop bp
0486  C2 02 00        ret 2
; data (not reached as code), 58 bytes
0489                  pstr 'Do you want a print out of the help file'
04B2                  pstr 'Printing....'
04BF                  pstr 'prn'

; ---- routine 16D6:04C3  (found by: call)
sub_04C3:
04C3  55              push bp
04C4  89 E5           mov bp, sp
04C6  83 EC 02        sub sp, 2
04C9  BF 89 04        mov di, 0x489
04CC  0E              push cs
04CD  57              push di
04CE  9A 66 05 4B 21  call far 214B:0566
04D3  08 C0           or al, al
04D5  74 09           je 0x4e0
04D7  9A B9 0A 4B 21  call far 214B:0AB9
04DC  08 C0           or al, al
04DE  75 02           jne 0x4e2
loc_04E0:
04E0  EB 78           jmp 0x55a
loc_04E2:
04E2  9A 25 06 4B 21  call far 214B:0625
04E7  B0 19           mov al, 0x19
04E9  50              push ax
04EA  BF B2 04        mov di, 0x4b2
04ED  0E              push cs
04EE  57              push di
04EF  BF 6A A9        mov di, 0xa96a
04F2  1E              push ds
04F3  57              push di
04F4  9A 50 03 4B 21  call far 214B:0350
04F9  BF BB 99        mov di, 0x99bb
04FC  1E              push ds
04FD  57              push di
04FE  BF BF 04        mov di, 0x4bf
0501  0E              push cs
0502  57              push di
0503  9A 79 17 E4 23  call far 23E4:1779
0508  BF BB 99        mov di, 0x99bb
050B  1E              push ds
050C  57              push di
050D  B8 01 00        mov ax, 1
0510  50              push ax
0511  9A B0 17 E4 23  call far 23E4:17B0
0516  BF BB 99        mov di, 0x99bb
0519  1E              push ds
051A  57              push di
051B  C4 3E B0 99     les di, ptr [0x99b0]
051F  81 C7 01 00     add di, 1
0523  06              push es
0524  57              push di
0525  FF 36 B4 99     push word ptr [0x99b4]
0529  8D 7E FE        lea di, [bp - 2]
052C  16              push ss
052D  57              push di
052E  9A 99 18 E4 23  call far 23E4:1899
0533  BF BB 99        mov di, 0x99bb
0536  1E              push ds
0537  57              push di
0538  BF EC 0A        mov di, 0xaec
053B  1E              push ds
053C  57              push di
053D  B8 02 00        mov ax, 2
0540  50              push ax
0541  8D 7E FE        lea di, [bp - 2]
0544  16              push ss
0545  57              push di
0546  9A 99 18 E4 23  call far 23E4:1899
054B  BF BB 99        mov di, 0x99bb
054E  1E              push ds
054F  57              push di
0550  9A 28 18 E4 23  call far 23E4:1828
0555  9A 43 06 4B 21  call far 214B:0643
loc_055A:
055A  89 EC           mov sp, bp
055C  5D              pop bp
055D  C3              ret

; ---- routine 16D6:055E  (found by: call)
sub_055E:
055E  55              push bp
055F  89 E5           mov bp, sp
0561  1E              push ds
0562  8A 56 06        mov dl, byte ptr [bp + 6]
0565  C5 4E 08        lds cx, ptr [bp + 8]
0568  C5 76 0C        lds si, ptr [bp + 0xc]
056B  C4 7E 10        les di, ptr [bp + 0x10]
056E  32 FF           xor bh, bh
0570  26 8A 1D        mov bl, byte ptr es:[di]
0573  47              inc di
0574  55              push bp
0575  B8 00 00        mov ax, 0
0578  50              push ax
loc_0579:
0579  39 F1           cmp cx, si
057B  74 56           je 0x5d3
057D  77 04           ja 0x583
057F  4E              dec si
0580  E9 01 00        jmp 0x584
loc_0583:
0583  46              inc si
loc_0584:
0584  8A 04           mov al, byte ptr [si]
0586  26 8A 25        mov ah, byte ptr es:[di]
0589  BD 00 00        mov bp, 0
058C  3C 0A           cmp al, 0xa
058E  74 20           je 0x5b0
loc_0590:
0590  80 FA 01        cmp dl, 1
0593  74 0A           je 0x59f
0595  3C 61           cmp al, 0x61
0597  72 06           jb 0x59f
0599  3C 7A           cmp al, 0x7a
059B  77 02           ja 0x59f
059D  2C 20           sub al, 0x20
loc_059F:
059F  3A C4           cmp al, ah
05A1  75 D6           jne 0x579
05A3  45              inc bp
05A4  39 DD           cmp bp, bx
05A6  73 0D           jae 0x5b5
05A8  26 8A 23        mov ah, byte ptr es:[bp + di]
05AB  3E 8A 02        mov al, byte ptr ds:[bp + si]
05AE  EB E0           jmp 0x590
loc_05B0:
05B0  58              pop ax
05B1  40              inc ax
05B2  50              push ax
05B3  EB C4           jmp 0x579
loc_05B5:
05B5  58              pop ax
05B6  5D              pop bp
05B7  C4 7E 18        les di, ptr [bp + 0x18]
05BA  AB              stosw word ptr es:[di], ax
05BB  8B C6           mov ax, si
05BD  C5 76 0C        lds si, ptr [bp + 0xc]
05C0  39 F0           cmp ax, si
05C2  72 05           jb 0x5c9
05C4  29 F0           sub ax, si
05C6  E9 03 00        jmp 0x5cc
loc_05C9:
05C9  29 C6           sub si, ax
05CB  96              xchg si, ax
loc_05CC:
05CC  C4 7E 14        les di, ptr [bp + 0x14]
05CF  AB              stosw word ptr es:[di], ax
05D0  E9 0D 00        jmp 0x5e0
loc_05D3:
05D3  58              pop ax
05D4  5D              pop bp
05D5  C4 7E 18        les di, ptr [bp + 0x18]
05D8  AB              stosw word ptr es:[di], ax
05D9  B8 00 00        mov ax, 0
05DC  C4 7E 14        les di, ptr [bp + 0x14]
05DF  AB              stosw word ptr es:[di], ax
loc_05E0:
05E0  1F              pop ds
05E1  89 EC           mov sp, bp
05E3  5D              pop bp
05E4  CA 16 00        retf 0x16

; ---- routine 16D6:05E7  (found by: call)
sub_05E7:
05E7  55              push bp
05E8  89 E5           mov bp, sp
05EA  81 EC 02 01     sub sp, 0x102
05EE  BF 50 0B        mov di, 0xb50
05F1  1E              push ds
05F2  57              push di
05F3  BF 6A A9        mov di, 0xa96a
05F6  1E              push ds
05F7  57              push di
05F8  9A 29 03 4B 21  call far 214B:0329
05FD  BF 04 0C        mov di, 0xc04
0600  1E              push ds
0601  57              push di
0602  B0 14           mov al, 0x14
0604  50              push ax
0605  B0 1E           mov al, 0x1e
0607  50              push ax
0608  B0 32           mov al, 0x32
060A  50              push ax
060B  B0 19           mov al, 0x19
060D  50              push ax
060E  9A 86 10 4B 21  call far 214B:1086
0613  8D BE FF FE     lea di, [bp - 0x101]
0617  16              push ss
0618  57              push di
0619  BF 04 0C        mov di, 0xc04
061C  1E              push ds
061D  57              push di
061E  9A 9C 00 4B 21  call far 214B:009C
0623  BF 04 0C        mov di, 0xc04
0626  1E              push ds
0627  57              push di
0628  B8 14 00        mov ax, 0x14
062B  50              push ax
062C  9A 44 06 E4 23  call far 23E4:0644
0631  8B 7E 04        mov di, word ptr [bp + 4]
0634  36 C7 45 F8 01 00 mov word ptr ss:[di - 8], 1
063A  A0 04 0C        mov al, byte ptr [0xc04]
063D  30 E4           xor ah, ah
063F  8B 7E 04        mov di, word ptr [bp + 4]
0642  36 89 45 FA     mov word ptr ss:[di - 6], ax
0646  80 3E 04 0C 00  cmp byte ptr [0xc04], 0
064B  75 04           jne 0x651
064D  B0 00           mov al, 0
064F  EB 02           jmp 0x653
loc_0651:
0651  B0 01           mov al, 1
loc_0653:
0653  88 46 FF        mov byte ptr [bp - 1], al
0656  8A 46 FF        mov al, byte ptr [bp - 1]
0659  89 EC           mov sp, bp
065B  5D              pop bp
065C  C2 02 00        ret 2

; ---- routine 16D6:065F  (found by: call)
sub_065F:
065F  55              push bp
0660  89 E5           mov bp, sp
0662  83 EC 02        sub sp, 2
0665  8B 7E 04        mov di, word ptr [bp + 4]
0668  81 C7 FC FF     add di, 0xfffc
066C  16              push ss
066D  57              push di
066E  8B 7E 04        mov di, word ptr [bp + 4]
0671  81 C7 FE FF     add di, 0xfffe
0675  16              push ss
0676  57              push di
0677  BF 04 0C        mov di, 0xc04
067A  1E              push ds
067B  57              push di
067C  8B 7E 04        mov di, word ptr [bp + 4]
067F  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
0683  C4 3E B0 99     les di, ptr [0x99b0]
0687  03 F8           add di, ax
0689  06              push es
068A  57              push di
068B  A1 B4 99        mov ax, word ptr [0x99b4]
068E  C4 3E B0 99     les di, ptr [0x99b0]
0692  03 F8           add di, ax
0694  06              push es
0695  57              push di
0696  B0 00           mov al, 0
0698  50              push ax
0699  0E              push cs
069A  E8 C1 FE        call 0x55e
069D  8B 7E 04        mov di, word ptr [bp + 4]
06A0  36 83 7D FE 00  cmp word ptr ss:[di - 2], 0
06A5  75 04           jne 0x6ab
06A7  B0 00           mov al, 0
06A9  EB 02           jmp 0x6ad
loc_06AB:
06AB  B0 01           mov al, 1
loc_06AD:
06AD  88 46 FF        mov byte ptr [bp - 1], al
06B0  8B 7E 04        mov di, word ptr [bp + 4]
06B3  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
06B7  8B 7E 04        mov di, word ptr [bp + 4]
06BA  36 01 45 F8     add word ptr ss:[di - 8], ax
06BE  8B 7E 04        mov di, word ptr [bp + 4]
06C1  36 83 7D FE 00  cmp word ptr ss:[di - 2], 0
06C6  74 02           je 0x6ca
06C8  EB 14           jmp 0x6de
loc_06CA:
06CA  BF D4 0B        mov di, 0xbd4
06CD  1E              push ds
06CE  57              push di
06CF  BF 6A A9        mov di, 0xa96a
06D2  1E              push ds
06D3  57              push di
06D4  9A 29 03 4B 21  call far 214B:0329
06D9  9A DD 08 4B 21  call far 214B:08DD
loc_06DE:
06DE  8A 46 FF        mov al, byte ptr [bp - 1]
06E1  89 EC           mov sp, bp
06E3  5D              pop bp
06E4  C2 02 00        ret 2

; ---- routine 16D6:06E7  (found by: call)
sub_06E7:
06E7  55              push bp
06E8  89 E5           mov bp, sp
loc_06EA:
06EA  FF 76 04        push word ptr [bp + 4]
06ED  E8 6F FF        call 0x65f
06F0  08 C0           or al, al
06F2  75 02           jne 0x6f6
06F4  EB 78           jmp 0x76e
loc_06F6:
06F6  8B 7E 04        mov di, word ptr [bp + 4]
06F9  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
06FD  8B 7E 04        mov di, word ptr [bp + 4]
0700  36 03 45 FA     add ax, word ptr ss:[di - 6]
0704  50              push ax
0705  E8 F1 FC        call 0x3f9
0708  B0 00           mov al, 0
070A  50              push ax
070B  31 C0           xor ax, ax
070D  50              push ax
070E  E8 55 FB        call 0x266
0711  BF 9A 0B        mov di, 0xb9a
0714  1E              push ds
0715  57              push di
0716  BF 6A A9        mov di, 0xa96a
0719  1E              push ds
071A  57              push di
071B  9A 29 03 4B 21  call far 214B:0329
0720  A0 F3 0A        mov al, byte ptr [0xaf3]
0723  30 E4           xor ah, ah
0725  8B 7E 04        mov di, word ptr [bp + 4]
0728  36 2B 45 FA     sub ax, word ptr ss:[di - 6]
072C  D1 E0           shl ax, 1
072E  8B C8           mov cx, ax
0730  A0 F2 0A        mov al, byte ptr [0xaf2]
0733  30 E4           xor ah, ah
0735  BA A0 00        mov dx, 0xa0
0738  F7 E2           mul dx
073A  C4 3E 6A A9     les di, ptr [0xa96a]
073E  03 F8           add di, ax
0740  03 F9           add di, cx
0742  81 C7 5E FF     add di, 0xff5e
0746  06              push es
0747  57              push di
0748  B8 4F 00        mov ax, 0x4f
074B  50              push ax
074C  8B 7E 04        mov di, word ptr [bp + 4]
074F  36 FF 75 FA     push word ptr ss:[di - 6]
0753  9A DB 00 4B 21  call far 214B:00DB
0758  9A DD 08 4B 21  call far 214B:08DD
075D  80 3E 76 A9 20  cmp byte ptr [0xa976], 0x20
0762  74 86           je 0x6ea
0764  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
0769  75 03           jne 0x76e
076B  E9 7C FF        jmp 0x6ea
loc_076E:
076E  89 EC           mov sp, bp
0770  5D              pop bp
0771  C2 02 00        ret 2

; ---- routine 16D6:0774  (found by: call)
sub_0774:
0774  55              push bp
0775  89 E5           mov bp, sp
0777  83 EC 08        sub sp, 8
077A  55              push bp
077B  E8 69 FE        call 0x5e7
077E  08 C0           or al, al
0780  74 04           je 0x786
0782  55              push bp
0783  E8 61 FF        call 0x6e7
loc_0786:
0786  B0 00           mov al, 0
0788  50              push ax
0789  31 C0           xor ax, ax
078B  50              push ax
078C  E8 D7 FA        call 0x266
078F  89 EC           mov sp, bp
0791  5D              pop bp
0792  C3              ret

; ---- routine 16D6:0793  (found by: call)
sub_0793:
0793  55              push bp
0794  89 E5           mov bp, sp
0796  83 EC 02        sub sp, 2
0799  B0 00           mov al, 0
079B  50              push ax
079C  E8 CE FB        call 0x36d
loc_079F:
079F  9A DD 08 4B 21  call far 214B:08DD
07A4  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
07A9  74 04           je 0x7af
07AB  B0 00           mov al, 0
07AD  EB 02           jmp 0x7b1
loc_07AF:
07AF  B0 01           mov al, 1
loc_07B1:
07B1  88 46 FF        mov byte ptr [bp - 1], al
07B4  A0 76 A9        mov al, byte ptr [0xa976]
07B7  50              push ax
07B8  9A B2 19 E4 23  call far 23E4:19B2
07BD  3C AD           cmp al, 0xad
07BF  75 08           jne 0x7c9
07C1  B0 FF           mov al, 0xff
07C3  50              push ax
07C4  E8 A6 FB        call 0x36d
07C7  EB 52           jmp 0x81b
loc_07C9:
07C9  3C B2           cmp al, 0xb2
07CB  75 08           jne 0x7d5
07CD  B0 01           mov al, 1
07CF  50              push ax
07D0  E8 9A FB        call 0x36d
07D3  EB 46           jmp 0x81b
loc_07D5:
07D5  3C AB           cmp al, 0xab
07D7  75 09           jne 0x7e2
07D9  B8 01 00        mov ax, 1
07DC  50              push ax
07DD  E8 4F FB        call 0x32f
07E0  EB 39           jmp 0x81b
loc_07E2:
07E2  3C B0           cmp al, 0xb0
07E4  75 05           jne 0x7eb
07E6  E8 60 FB        call 0x349
07E9  EB 30           jmp 0x81b
loc_07EB:
07EB  3C B1           cmp al, 0xb1
07ED  74 04           je 0x7f3
07EF  3C AF           cmp al, 0xaf
07F1  75 08           jne 0x7fb
loc_07F3:
07F3  B0 01           mov al, 1
07F5  50              push ax
07F6  E8 CE FB        call 0x3c7
07F9  EB 20           jmp 0x81b
loc_07FB:
07FB  3C AC           cmp al, 0xac
07FD  74 04           je 0x803
07FF  3C AE           cmp al, 0xae
0801  75 08           jne 0x80b
loc_0803:
0803  B0 FF           mov al, 0xff
0805  50              push ax
0806  E8 BE FB        call 0x3c7
0809  EB 10           jmp 0x81b
loc_080B:
080B  3C 50           cmp al, 0x50
080D  75 05           jne 0x814
080F  E8 B1 FC        call 0x4c3
0812  EB 07           jmp 0x81b
loc_0814:
0814  3C 46           cmp al, 0x46
0816  75 03           jne 0x81b
0818  E8 59 FF        call 0x774
loc_081B:
081B  80 7E FF 00     cmp byte ptr [bp - 1], 0
081F  75 03           jne 0x824
0821  E9 7B FF        jmp 0x79f
loc_0824:
0824  89 EC           mov sp, bp
0826  5D              pop bp
0827  C3              ret

; ---- routine 16D6:0828  (found by: call)
sub_0828:
0828  55              push bp
0829  89 E5           mov bp, sp
082B  BF BB 99        mov di, 0x99bb
082E  1E              push ds
082F  57              push di
0830  9A 28 18 E4 23  call far 23E4:1828
0835  9A 07 02 E4 23  call far 23E4:0207
083A  09 C0           or ax, ax
083C  75 00           jne 0x83e
loc_083E:
083E  89 EC           mov sp, bp
0840  5D              pop bp
0841  C3              ret

; ---- routine 16D6:0842  (found by: call)
sub_0842:
0842  55              push bp
0843  89 E5           mov bp, sp
0845  83 EC 04        sub sp, 4
0848  31 C0           xor ax, ax
084A  89 46 FE        mov word ptr [bp - 2], ax
084D  31 C0           xor ax, ax
084F  89 46 FC        mov word ptr [bp - 4], ax
0852  BF EC 0A        mov di, 0xaec
0855  1E              push ds
0856  57              push di
0857  A1 B4 99        mov ax, word ptr [0x99b4]
085A  C4 3E B0 99     les di, ptr [0x99b0]
085E  03 F8           add di, ax
0860  06              push es
0861  57              push di
0862  B8 02 00        mov ax, 2
0865  50              push ax
0866  9A 3C 00 4B 21  call far 214B:003C
loc_086B:
086B  FF 46 FC        inc word ptr [bp - 4]
086E  B0 01           mov al, 1
0870  50              push ax
0871  B0 0A           mov al, 0xa
0873  50              push ax
0874  8B 46 FE        mov ax, word ptr [bp - 2]
0877  C4 3E B0 99     les di, ptr [0x99b0]
087B  03 F8           add di, ax
087D  06              push es
087E  57              push di
087F  B8 01 00        mov ax, 1
0882  50              push ax
0883  0E              push cs
0884  E8 3C F8        call 0xc3
0887  01 46 FE        add word ptr [bp - 2], ax
088A  8B 46 FE        mov ax, word ptr [bp - 2]
088D  3B 06 B4 99     cmp ax, word ptr [0x99b4]
0891  72 D8           jb 0x86b
0893  FF 06 B4 99     inc word ptr [0x99b4]
0897  8B 46 FC        mov ax, word ptr [bp - 4]
089A  A3 B6 99        mov word ptr [0x99b6], ax
089D  E8 88 FF        call 0x828
08A0  89 EC           mov sp, bp
08A2  5D              pop bp
08A3  C3              ret
; data (not reached as code), 33 bytes
08A4                  pstr 'GOAL.HLP'
08AD                  pstr ' "GOAL.HLP" not found..'

; ---- routine 16D6:08C5  (found by: call)
sub_08C5:
08C5  55              push bp
08C6  89 E5           mov bp, sp
08C8  83 EC 02        sub sp, 2
08CB  BF A4 08        mov di, 0x8a4
08CE  0E              push cs
08CF  57              push di
08D0  9A F5 1B 4B 21  call far 214B:1BF5
08D5  08 C0           or al, al
08D7  74 04           je 0x8dd
08D9  B0 00           mov al, 0
08DB  EB 02           jmp 0x8df
loc_08DD:
08DD  B0 01           mov al, 1
loc_08DF:
08DF  50              push ax
08E0  BF AD 08        mov di, 0x8ad
08E3  0E              push cs
08E4  57              push di
08E5  9A 65 17 4B 21  call far 214B:1765
08EA  08 C0           or al, al
08EC  74 04           je 0x8f2
08EE  B0 00           mov al, 0
08F0  EB 02           jmp 0x8f4
loc_08F2:
08F2  B0 01           mov al, 1
loc_08F4:
08F4  88 46 FF        mov byte ptr [bp - 1], al
08F7  8A 46 FF        mov al, byte ptr [bp - 1]
08FA  89 EC           mov sp, bp
08FC  5D              pop bp
08FD  C3              ret
; data (not reached as code), 18 bytes
08FE                  pstr 'not enough memory'

