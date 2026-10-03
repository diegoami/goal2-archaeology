; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 23E4 (image offsets 23E40..2580F), part 1 of 3
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 23E4:0000  (found by: far)
sub_0000:
0000  BA 81 25        mov dx, 0x2581   ; relocated segment word 2581
0003  8E DA           mov ds, dx
0005  8C 06 5C 7B     mov word ptr [0x7b5c], es
0009  33 ED           xor bp, bp
000B  8B C4           mov ax, sp
000D  05 13 00        add ax, 0x13
0010  B1 04           mov cl, 4
0012  D3 E8           shr ax, cl
0014  8C D2           mov dx, ss
0016  03 C2           add ax, dx
0018  A3 34 7B        mov word ptr [0x7b34], ax
001B  A3 36 7B        mov word ptr [0x7b36], ax
001E  03 06 2E 7B     add ax, word ptr [0x7b2e]
0022  A3 38 7B        mov word ptr [0x7b38], ax
0025  A3 42 7B        mov word ptr [0x7b42], ax
0028  A3 46 7B        mov word ptr [0x7b46], ax
002B  26 A1 02 00     mov ax, word ptr es:[2]
002F  2D 00 10        sub ax, 0x1000
0032  A3 4A 7B        mov word ptr [0x7b4a], ax
0035  BF C0 AC        mov di, 0xacc0
0038  BE DD 01        mov si, 0x1dd
003B  B9 12 00        mov cx, 0x12
003E  90              nop
003F  FC              cld
0040  2E AC           lodsb al, byte ptr cs:[si]
0042  B4 35           mov ah, 0x35
0044  CD 21           int 0x21   ; INT 21h AH=35 get interrupt vector
0046  89 1D           mov word ptr [di], bx
0048  8C 45 02        mov word ptr [di + 2], es
004B  83 C7 04        add di, 4
004E  E2 F0           loop 0x40
0050  1E              push ds
0051  0E              push cs
0052  1F              pop ds
0053  BA CE 00        mov dx, 0xce
0056  B8 00 25        mov ax, 0x2500
0059  CD 21           int 0x21   ; INT 21h AH=25 set interrupt vector
005B  BA D5 00        mov dx, 0xd5
005E  B8 23 25        mov ax, 0x2523
0061  CD 21           int 0x21   ; INT 21h AH=25 set interrupt vector
0063  BA 9D 00        mov dx, 0x9d
0066  B8 24 25        mov ax, 0x2524
0069  CD 21           int 0x21   ; INT 21h AH=25 set interrupt vector
006B  BA C6 00        mov dx, 0xc6
006E  B8 3F 25        mov ax, 0x253f
0071  CD 21           int 0x21   ; INT 21h AH=25 set interrupt vector
0073  1F              pop ds
0074  B8 C0 AA        mov ax, 0xaac0
0077  1E              push ds
0078  50              push ax
0079  1E              push ds
007A  50              push ax
007B  B8 06 02        mov ax, 0x206
007E  0E              push cs
007F  50              push ax
0080  0E              push cs
0081  E8 EE 12        call 0x1372
0084  0E              push cs
0085  E8 5A 13        call 0x13e2
0088  B8 C0 AB        mov ax, 0xabc0
008B  1E              push ds
008C  50              push ax
008D  1E              push ds
008E  50              push ax
008F  B8 06 02        mov ax, 0x206
0092  0E              push cs
0093  50              push ax
0094  0E              push cs
0095  E8 DA 12        call 0x1372
0098  0E              push cs
0099  E8 4B 13        call 0x13e7
009C  CB              retf
; data (not reached as code), 52 bytes
009D                  db FB 83 C4 06 58 83 E7 1F 81 C7 96 00 80 FC 39 73   ; ....X.........9s
00AD                  db 03 BF FF FF 57 B4 54 CD 21 8B EC 80 4E 16 01 58   ; ....W.T.!...N..X
00BD                  db 5B 59 5A 5E 5F 5D 1F 07 CF B8 D0 00 83 C4 06 EB   ; [YZ^_]..........
00CD                  db 03 B8 C8 00   ; ....
loc_00D1:
00D1  59              pop cx
00D2  5B              pop bx
00D3  EB 07           jmp 0xdc
; data (not reached as code), 3 bytes
00D5                  db B8 FF 00   ; ...

; ---- routine 23E4:00D8  (found by: far)
sub_00D8:
00D8  33 C9           xor cx, cx
00DA  33 DB           xor bx, bx
loc_00DC:
00DC  BA 81 25        mov dx, 0x2581   ; relocated segment word 2581
00DF  8E DA           mov ds, dx
00E1  FB              sti
00E2  A3 56 7B        mov word ptr [0x7b56], ax
00E5  8B C1           mov ax, cx
00E7  0B C3           or ax, bx
00E9  74 1F           je 0x10a
00EB  A1 3A 7B        mov ax, word ptr [0x7b3a]
loc_00EE:
00EE  0B C0           or ax, ax
00F0  74 11           je 0x103
00F2  8E C0           mov es, ax
00F4  26 3B 1E 10 00  cmp bx, word ptr es:[0x10]
00F9  74 06           je 0x101
00FB  26 A1 14 00     mov ax, word ptr es:[0x14]
00FF  EB ED           jmp 0xee
loc_0101:
0101  8C C3           mov bx, es
loc_0103:
0103  2B 1E 5C 7B     sub bx, word ptr [0x7b5c]
0107  83 EB 10        sub bx, 0x10
loc_010A:
010A  89 0E 58 7B     mov word ptr [0x7b58], cx
010E  89 1E 5A 7B     mov word ptr [0x7b5a], bx
0112  C4 1E 52 7B     les bx, ptr [0x7b52]
0116  8C C0           mov ax, es
0118  0B C3           or ax, bx
011A  74 13           je 0x12f
011C  33 C0           xor ax, ax
011E  A3 52 7B        mov word ptr [0x7b52], ax
0121  A3 54 7B        mov word ptr [0x7b54], ax
0124  A3 60 7B        mov word ptr [0x7b60], ax
0127  B8 12 01        mov ax, 0x112
012A  0E              push cs
012B  50              push ax
012C  06              push es
012D  53              push bx
012E  CB              retf
loc_012F:
012F  B8 C0 AA        mov ax, 0xaac0
0132  1E              push ds
0133  50              push ax
0134  0E              push cs
0135  E8 03 13        call 0x143b
0138  B8 C0 AB        mov ax, 0xabc0
013B  1E              push ds
013C  50              push ax
013D  0E              push cs
013E  E8 FA 12        call 0x143b
0141  BF C0 AC        mov di, 0xacc0
0144  BE DD 01        mov si, 0x1dd
0147  B9 12 00        mov cx, 0x12
014A  90              nop
014B  FC              cld
014C  2E AC           lodsb al, byte ptr cs:[si]
014E  B4 25           mov ah, 0x25
0150  1E              push ds
0151  C5 15           lds dx, ptr [di]
0153  CD 21           int 0x21   ; INT 21h AH=25 set interrupt vector
0155  1F              pop ds
0156  83 C7 04        add di, 4
0159  E2 F1           loop 0x14c
015B  A1 58 7B        mov ax, word ptr [0x7b58]
015E  0B 06 5A 7B     or ax, word ptr [0x7b5a]
0162  74 29           je 0x18d
0164  BB EF 01        mov bx, 0x1ef
0167  E8 2A 00        call 0x194
016A  A1 56 7B        mov ax, word ptr [0x7b56]
016D  E8 32 00        call 0x1a2
0170  BB FE 01        mov bx, 0x1fe
0173  E8 1E 00        call 0x194
0176  A1 5A 7B        mov ax, word ptr [0x7b5a]
0179  E8 40 00        call 0x1bc
017C  B0 3A           mov al, 0x3a
017E  E8 55 00        call 0x1d6
0181  A1 58 7B        mov ax, word ptr [0x7b58]
0184  E8 35 00        call 0x1bc
0187  BB 03 02        mov bx, 0x203
018A  E8 07 00        call 0x194
loc_018D:
018D  A1 56 7B        mov ax, word ptr [0x7b56]
0190  B4 4C           mov ah, 0x4c
0192  CD 21           int 0x21   ; INT 21h AH=4C terminate

; ---- routine 23E4:0194  (found by: call, jump)
sub_0194:
0194  2E 8A 07        mov al, byte ptr cs:[bx]
0197  0A C0           or al, al
0199  74 06           je 0x1a1
019B  E8 38 00        call 0x1d6
019E  43              inc bx
019F  EB F3           jmp 0x194
loc_01A1:
01A1  C3              ret

; ---- routine 23E4:01A2  (found by: call)
sub_01A2:
01A2  B1 64           mov cl, 0x64
01A4  E8 07 00        call 0x1ae
01A7  B1 0A           mov cl, 0xa
01A9  E8 02 00        call 0x1ae
01AC  EB 04           jmp 0x1b2

; ---- routine 23E4:01AE  (found by: call)
sub_01AE:
01AE  32 E4           xor ah, ah
01B0  F6 F1           div cl
loc_01B2:
01B2  04 30           add al, 0x30
01B4  50              push ax
01B5  E8 1E 00        call 0x1d6
01B8  58              pop ax
01B9  8A C4           mov al, ah
01BB  C3              ret

; ---- routine 23E4:01BC  (found by: call)
sub_01BC:
01BC  50              push ax
01BD  8A C4           mov al, ah
01BF  E8 01 00        call 0x1c3
01C2  58              pop ax

; ---- routine 23E4:01C3  (found by: call)
sub_01C3:
01C3  50              push ax
01C4  B1 04           mov cl, 4
01C6  D2 E8           shr al, cl
01C8  E8 03 00        call 0x1ce
01CB  58              pop ax
01CC  24 0F           and al, 0xf

; ---- routine 23E4:01CE  (found by: call)
sub_01CE:
01CE  04 30           add al, 0x30
01D0  3C 3A           cmp al, 0x3a
01D2  72 02           jb 0x1d6
01D4  04 07           add al, 7

; ---- routine 23E4:01D6  (found by: call, jump)
sub_01D6:
01D6  8A D0           mov dl, al
01D8  B4 06           mov ah, 6
01DA  CD 21           int 0x21   ; INT 21h AH=06 ?
01DC  C3              ret
; data (not reached as code), 42 bytes
01DD                  db 00 02   ; ..
01DF                  pstr '#$456789:;<=>?uRuntime erro'
01FB                  db 72 20 00 20 61 74 20 00 2E 0D 0A 00   ; r . at .....

; ---- routine 23E4:0207  (found by: far)
sub_0207:
0207  33 C0           xor ax, ax
0209  87 06 60 7B     xchg word ptr [0x7b60], ax
020D  CB              retf
; data (not reached as code), 79 bytes
020E                  db 83 3E 60 7B 00 75 01 CB A1 60 7B E9 B5 FE 8B F4   ; .>`{.u...`{.....
021E                  db 36 8E 44 02 26 3B 55 02 7F 07 7C 14 26 3B 05 72   ; 6.D.&;U...|.&;.r
022E                  db 0F 26 3B 55 06 7C 08 7F 07 26 3B 45 04 77 01 CB   ; .&;U.|...&;E.w..
023E                  db B8 C9 00 E9 8D FE 8B F4 2B F0 72 0D 81 EE 00 02   ; ........+.r.....
024E                  db 72 07 3B 36 5E 7B 72 01 CB B8 CA 00 E9 74 FE   ; r.;6^{r......t.

; ---- routine 23E4:025D  (found by: far)
sub_025D:
025D  8B DC           mov bx, sp
025F  8C DA           mov dx, ds
0261  36 C5 77 0A     lds si, ptr ss:[bx + 0xa]
0265  36 C4 7F 06     les di, ptr ss:[bx + 6]
0269  36 8B 4F 04     mov cx, word ptr ss:[bx + 4]
026D  FC              cld
026E  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
0270  8E DA           mov ds, dx
0272  CA 0A 00        retf 0xa
; data (not reached as code), 4 bytes
0275                  db 8B C8 8B DA   ; ....

; ---- routine 23E4:0279  (found by: far)
sub_0279:
0279  8B F0           mov si, ax
027B  8B FA           mov di, dx
027D  F7 E1           mul cx
027F  50              push ax
0280  52              push dx
0281  8B C6           mov ax, si
0283  F7 E3           mul bx
0285  8B D8           mov bx, ax
0287  8B C7           mov ax, di
0289  F7 E1           mul cx
028B  8B C8           mov cx, ax
028D  5A              pop dx
028E  58              pop ax
028F  03 D3           add dx, bx
0291  03 D1           add dx, cx
0293  CB              retf

; ---- routine 23E4:0294  (found by: far)
sub_0294:
0294  55              push bp
0295  8B E9           mov bp, cx
0297  0B EB           or bp, bx
0299  74 60           je 0x2fb
029B  0B DB           or bx, bx
029D  9C              pushf
029E  79 0A           jns 0x2aa
02A0  F7 D1           not cx
02A2  F7 D3           not bx
02A4  83 C1 01        add cx, 1
02A7  83 D3 00        adc bx, 0
loc_02AA:
02AA  0B D2           or dx, dx
02AC  9C              pushf
02AD  79 0A           jns 0x2b9
02AF  F7 D0           not ax
02B1  F7 D2           not dx
02B3  05 01 00        add ax, 1
02B6  83 D2 00        adc dx, 0
loc_02B9:
02B9  8B F1           mov si, cx
02BB  8B FB           mov di, bx
02BD  33 C9           xor cx, cx
02BF  33 DB           xor bx, bx
02C1  BD 21 00        mov bp, 0x21
loc_02C4:
02C4  D1 D1           rcl cx, 1
02C6  D1 D3           rcl bx, 1
02C8  2B CE           sub cx, si
02CA  1B DF           sbb bx, di
02CC  73 04           jae 0x2d2
02CE  03 CE           add cx, si
02D0  13 DF           adc bx, di
loc_02D2:
02D2  F5              cmc
02D3  D1 D0           rcl ax, 1
02D5  D1 D2           rcl dx, 1
02D7  4D              dec bp
02D8  75 EA           jne 0x2c4
02DA  9D              popf
02DB  79 0F           jns 0x2ec
02DD  F7 D1           not cx
02DF  F7 D3           not bx
02E1  83 C1 01        add cx, 1
02E4  83 D3 00        adc bx, 0
02E7  9D              popf
02E8  79 05           jns 0x2ef
02EA  EB 0D           jmp 0x2f9
loc_02EC:
02EC  9D              popf
02ED  79 0A           jns 0x2f9
loc_02EF:
02EF  F7 D0           not ax
02F1  F7 D2           not dx
02F3  05 01 00        add ax, 1
02F6  83 D2 00        adc dx, 0
loc_02F9:
02F9  5D              pop bp
02FA  CB              retf
loc_02FB:
02FB  5D              pop bp
02FC  B8 C8 00        mov ax, 0xc8
02FF  E9 CF FD        jmp 0xd1
; data (not reached as code), 39 bytes
0302                  db 83 E1 1F 74 06 D1 EA D1 D8 E2 FA CB 83 E1 1F 74   ; ...t...........t
0312                  db 06 D1 E0 D1 D2 E2 FA CB 0B D2 7D 0A F7 D0 F7 D2   ; ..........}.....
0322                  db 05 01 00 83 D2 00 CB   ; .......

; ---- routine 23E4:0329  (found by: far)
sub_0329:
0329  8B DC           mov bx, sp
032B  36 8B 47 04     mov ax, word ptr ss:[bx + 4]
032F  E8 EB 00        call 0x41d
0332  72 07           jb 0x33b
0334  8B C1           mov ax, cx
0336  8B D3           mov dx, bx
0338  CA 02 00        retf 2
loc_033B:
033B  B8 CB 00        mov ax, 0xcb
033E  E9 90 FD        jmp 0xd1

; ---- routine 23E4:0341  (found by: far)
sub_0341:
0341  8B DC           mov bx, sp
0343  36 8B 47 04     mov ax, word ptr ss:[bx + 4]
0347  36 C4 4F 06     les cx, ptr ss:[bx + 6]
034B  8C C3           mov bx, es
034D  E8 88 01        call 0x4d8
0350  72 03           jb 0x355
0352  CA 06 00        retf 6
loc_0355:
0355  B8 CC 00        mov ax, 0xcc
0358  E9 76 FD        jmp 0xd1
; data (not reached as code), 49 bytes
035B                  db 8B DC 36 C4 7F 04 A1 44 7B 26 89 05 A1 46 7B 26   ; ..6....D{&...F{&
036B                  db 89 45 02 CA 04 00 8B DC 36 C4 7F 04 26 8B 05 A3   ; .E......6...&...
037B                  db 44 7B 26 8B 45 02 A3 46 7B 33 C0 A3 48 7B CA 04   ; D{&.E..F{3..H{..
038B                  db 00   ; .

; ---- routine 23E4:038C  (found by: far)
sub_038C:
038C  E8 35 02        call 0x5c4
038F  8B C6           mov ax, si
0391  8B D7           mov dx, di
0393  C4 3E 48 7B     les di, ptr [0x7b48]
0397  2B 16 46 7B     sub dx, word ptr [0x7b46]
039B  2B 06 44 7B     sub ax, word ptr [0x7b44]
039F  73 27           jae 0x3c8
03A1  05 10 00        add ax, 0x10
03A4  4A              dec dx
03A5  EB 21           jmp 0x3c8
loc_03A7:
03A7  26 03 55 06     add dx, word ptr es:[di + 6]
03AB  26 2B 55 02     sub dx, word ptr es:[di + 2]
03AF  26 03 45 04     add ax, word ptr es:[di + 4]
03B3  3D 10 00        cmp ax, 0x10
03B6  72 04           jb 0x3bc
03B8  2D 10 00        sub ax, 0x10
03BB  42              inc dx
loc_03BC:
03BC  26 2B 05        sub ax, word ptr es:[di]
03BF  73 04           jae 0x3c5
03C1  05 10 00        add ax, 0x10
03C4  4A              dec dx
loc_03C5:
03C5  83 C7 08        add di, 8
loc_03C8:
03C8  0B FF           or di, di
03CA  75 DB           jne 0x3a7
03CC  E8 4C 02        call 0x61b
03CF  CB              retf

; ---- routine 23E4:03D0  (found by: far)
sub_03D0:
03D0  E8 F1 01        call 0x5c4
03D3  8B C6           mov ax, si
03D5  8B D7           mov dx, di
03D7  C4 3E 48 7B     les di, ptr [0x7b48]
03DB  2B 16 46 7B     sub dx, word ptr [0x7b46]
03DF  2B 06 44 7B     sub ax, word ptr [0x7b44]
03E3  73 30           jae 0x415
03E5  05 10 00        add ax, 0x10
03E8  4A              dec dx
03E9  EB 2A           jmp 0x415
loc_03EB:
03EB  26 8B 5D 06     mov bx, word ptr es:[di + 6]
03EF  26 2B 5D 02     sub bx, word ptr es:[di + 2]
03F3  3B DA           cmp bx, dx
03F5  72 1B           jb 0x412
03F7  26 8B 4D 04     mov cx, word ptr es:[di + 4]
03FB  26 2B 0D        sub cx, word ptr es:[di]
03FE  73 04           jae 0x404
0400  83 C1 10        add cx, 0x10
0403  4B              dec bx
loc_0404:
0404  3B DA           cmp bx, dx
0406  77 06           ja 0x40e
0408  72 08           jb 0x412
040A  3B C8           cmp cx, ax
040C  72 04           jb 0x412
loc_040E:
040E  8B C1           mov ax, cx
0410  8B D3           mov dx, bx
loc_0412:
0412  83 C7 08        add di, 8
loc_0415:
0415  0B FF           or di, di
0417  75 D2           jne 0x3eb
0419  E8 FF 01        call 0x61b
041C  CB              retf

; ---- routine 23E4:041D  (found by: call, jump)
sub_041D:
041D  50              push ax
041E  E8 EC 01        call 0x60d
0421  C4 3E 48 7B     les di, ptr [0x7b48]
0425  EB 0F           jmp 0x436
loc_0427:
0427  26 8B 5D 06     mov bx, word ptr es:[di + 6]
042B  26 2B 5D 02     sub bx, word ptr es:[di + 2]
042F  3B DA           cmp bx, dx
0431  73 5F           jae 0x492
loc_0433:
0433  83 C7 08        add di, 8
loc_0436:
0436  0B FF           or di, di
0438  75 ED           jne 0x427
043A  E8 87 01        call 0x5c4
043D  8B CE           mov cx, si
043F  8B DF           mov bx, di
0441  2B 1E 46 7B     sub bx, word ptr [0x7b46]
0445  2B 0E 44 7B     sub cx, word ptr [0x7b44]
0449  73 04           jae 0x44f
044B  83 C1 10        add cx, 0x10
044E  4B              dec bx
loc_044F:
044F  3B DA           cmp bx, dx
0451  77 06           ja 0x459
0453  72 22           jb 0x477
0455  3B C8           cmp cx, ax
0457  72 1E           jb 0x477
loc_0459:
0459  8B 0E 44 7B     mov cx, word ptr [0x7b44]
045D  8B 1E 46 7B     mov bx, word ptr [0x7b46]
0461  03 D3           add dx, bx
0463  03 C1           add ax, cx
0465  3D 10 00        cmp ax, 0x10
0468  72 04           jb 0x46e
046A  2D 10 00        sub ax, 0x10
046D  42              inc dx
loc_046E:
046E  A3 44 7B        mov word ptr [0x7b44], ax
0471  89 16 46 7B     mov word ptr [0x7b46], dx
0475  EB 5C           jmp 0x4d3
loc_0477:
0477  58              pop ax
0478  8B 0E 4E 7B     mov cx, word ptr [0x7b4e]
047C  0B 0E 50 7B     or cx, word ptr [0x7b50]
0480  74 54           je 0x4d6
0482  50              push ax
0483  50              push ax
0484  FF 1E 4E 7B     lcall [0x7b4e]
0488  91              xchg cx, ax
0489  58              pop ax
048A  E3 4A           jcxz 0x4d6
048C  49              dec cx
048D  75 8E           jne 0x41d
048F  8B D9           mov bx, cx
0491  C3              ret
loc_0492:
0492  26 8B 4D 04     mov cx, word ptr es:[di + 4]
0496  26 2B 0D        sub cx, word ptr es:[di]
0499  73 04           jae 0x49f
049B  83 C1 10        add cx, 0x10
049E  4B              dec bx
loc_049F:
049F  3B DA           cmp bx, dx
04A1  77 06           ja 0x4a9
04A3  72 8E           jb 0x433
04A5  3B C8           cmp cx, ax
04A7  72 8A           jb 0x433
loc_04A9:
04A9  26 8B 0D        mov cx, word ptr es:[di]
04AC  26 8B 5D 02     mov bx, word ptr es:[di + 2]
04B0  03 D3           add dx, bx
04B2  03 C1           add ax, cx
04B4  3D 10 00        cmp ax, 0x10
04B7  72 04           jb 0x4bd
04B9  2D 10 00        sub ax, 0x10
04BC  42              inc dx
loc_04BD:
04BD  26 89 05        mov word ptr es:[di], ax
04C0  26 89 55 02     mov word ptr es:[di + 2], dx
04C4  26 3B 55 06     cmp dx, word ptr es:[di + 6]
04C8  75 09           jne 0x4d3
04CA  26 3B 45 04     cmp ax, word ptr es:[di + 4]
04CE  75 03           jne 0x4d3
04D0  E8 DC 00        call 0x5af
loc_04D3:
04D3  58              pop ax
04D4  F8              clc
04D5  C3              ret
loc_04D6:
04D6  F9              stc
04D7  C3              ret

; ---- routine 23E4:04D8  (found by: call)
sub_04D8:
04D8  0B C0           or ax, ax
04DA  74 33           je 0x50f
04DC  E8 2E 01        call 0x60d
04DF  03 D3           add dx, bx
04E1  03 C1           add ax, cx
04E3  3D 10 00        cmp ax, 0x10
04E6  72 04           jb 0x4ec
04E8  2D 10 00        sub ax, 0x10
04EB  42              inc dx
loc_04EC:
04EC  3B 1E 42 7B     cmp bx, word ptr [0x7b42]
04F0  72 1C           jb 0x50e
04F2  77 06           ja 0x4fa
04F4  3B 0E 40 7B     cmp cx, word ptr [0x7b40]
04F8  72 14           jb 0x50e
loc_04FA:
04FA  3B 16 46 7B     cmp dx, word ptr [0x7b46]
04FE  77 0E           ja 0x50e
0500  72 06           jb 0x508
0502  3B 06 44 7B     cmp ax, word ptr [0x7b44]
0506  77 06           ja 0x50e
loc_0508:
0508  C4 3E 48 7B     les di, ptr [0x7b48]
050C  EB 4F           jmp 0x55d
loc_050E:
050E  F9              stc
loc_050F:
050F  C3              ret
loc_0510:
0510  26 3B 5D 02     cmp bx, word ptr es:[di + 2]
0514  72 1E           jb 0x534
0516  77 05           ja 0x51d
0518  26 3B 0D        cmp cx, word ptr es:[di]
051B  72 17           jb 0x534
loc_051D:
051D  26 3B 5D 06     cmp bx, word ptr es:[di + 6]
0521  77 37           ja 0x55a
0523  72 06           jb 0x52b
0525  26 3B 4D 04     cmp cx, word ptr es:[di + 4]
0529  77 2F           ja 0x55a
loc_052B:
052B  26 8B 0D        mov cx, word ptr es:[di]
052E  26 8B 5D 02     mov bx, word ptr es:[di + 2]
0532  EB 0D           jmp 0x541
loc_0534:
0534  26 3B 55 02     cmp dx, word ptr es:[di + 2]
0538  72 20           jb 0x55a
053A  77 05           ja 0x541
053C  26 3B 05        cmp ax, word ptr es:[di]
053F  72 19           jb 0x55a
loc_0541:
0541  26 3B 55 06     cmp dx, word ptr es:[di + 6]
0545  77 10           ja 0x557
0547  72 06           jb 0x54f
0549  26 3B 45 04     cmp ax, word ptr es:[di + 4]
054D  77 08           ja 0x557
loc_054F:
054F  26 8B 45 04     mov ax, word ptr es:[di + 4]
0553  26 8B 55 06     mov dx, word ptr es:[di + 6]
loc_0557:
0557  E8 55 00        call 0x5af
loc_055A:
055A  83 C7 08        add di, 8
loc_055D:
055D  0B FF           or di, di
055F  75 AF           jne 0x510
0561  3B 16 46 7B     cmp dx, word ptr [0x7b46]
0565  75 0F           jne 0x576
0567  3B 06 44 7B     cmp ax, word ptr [0x7b44]
056B  75 09           jne 0x576
056D  89 0E 44 7B     mov word ptr [0x7b44], cx
0571  89 1E 46 7B     mov word ptr [0x7b46], bx
0575  C3              ret
loc_0576:
0576  E8 12 00        call 0x58b
0579  72 0F           jb 0x58a
057B  26 89 0D        mov word ptr es:[di], cx
057E  26 89 5D 02     mov word ptr es:[di + 2], bx
0582  26 89 45 04     mov word ptr es:[di + 4], ax
0586  26 89 55 06     mov word ptr es:[di + 6], dx
loc_058A:
058A  C3              ret

; ---- routine 23E4:058B  (found by: call)
sub_058B:
058B  8B 3E 48 7B     mov di, word ptr [0x7b48]
058F  83 EF 08        sub di, 8
0592  74 19           je 0x5ad
0594  8B F7           mov si, di
0596  D1 EE           shr si, 1
0598  D1 EE           shr si, 1
059A  D1 EE           shr si, 1
059C  D1 EE           shr si, 1
059E  03 36 4A 7B     add si, word ptr [0x7b4a]
05A2  3B 36 46 7B     cmp si, word ptr [0x7b46]
05A6  76 05           jbe 0x5ad
05A8  89 3E 48 7B     mov word ptr [0x7b48], di
05AC  C3              ret
loc_05AD:
05AD  F9              stc
05AE  C3              ret

; ---- routine 23E4:05AF  (found by: call)
sub_05AF:
05AF  8B 36 48 7B     mov si, word ptr [0x7b48]
05B3  FC              cld
05B4  26 A5           movsw word ptr es:[di], word ptr es:[si]
05B6  26 A5           movsw word ptr es:[di], word ptr es:[si]
05B8  26 A5           movsw word ptr es:[di], word ptr es:[si]
05BA  26 A5           movsw word ptr es:[di], word ptr es:[si]
05BC  83 EF 08        sub di, 8
05BF  89 36 48 7B     mov word ptr [0x7b48], si
05C3  C3              ret

; ---- routine 23E4:05C4  (found by: call)
sub_05C4:
05C4  8B 3E 48 7B     mov di, word ptr [0x7b48]
05C8  0B FF           or di, di
05CA  75 11           jne 0x5dd
05CC  2B 3E 4C 7B     sub di, word ptr [0x7b4c]
05D0  75 13           jne 0x5e5
05D2  33 F6           xor si, si
05D4  8B 3E 4A 7B     mov di, word ptr [0x7b4a]
05D8  81 C7 00 10     add di, 0x1000
05DC  C3              ret
loc_05DD:
05DD  2B 3E 4C 7B     sub di, word ptr [0x7b4c]
05E1  73 02           jae 0x5e5
05E3  33 FF           xor di, di
loc_05E5:
05E5  8B F7           mov si, di
05E7  83 E6 0F        and si, 0xf
05EA  D1 EF           shr di, 1
05EC  D1 EF           shr di, 1
05EE  D1 EF           shr di, 1
05F0  D1 EF           shr di, 1
05F2  03 3E 4A 7B     add di, word ptr [0x7b4a]
05F6  3B 3E 46 7B     cmp di, word ptr [0x7b46]
05FA  77 10           ja 0x60c
05FC  72 06           jb 0x604
05FE  3B 36 44 7B     cmp si, word ptr [0x7b44]
0602  73 08           jae 0x60c
loc_0604:
0604  8B 36 44 7B     mov si, word ptr [0x7b44]
0608  8B 3E 46 7B     mov di, word ptr [0x7b46]
loc_060C:
060C  C3              ret

; ---- routine 23E4:060D  (found by: call)
sub_060D:
060D  8B D0           mov dx, ax
060F  25 0F 00        and ax, 0xf
0612  D1 EA           shr dx, 1
0614  D1 EA           shr dx, 1
0616  D1 EA           shr dx, 1
0618  D1 EA           shr dx, 1
061A  C3              ret

; ---- routine 23E4:061B  (found by: call)
sub_061B:
061B  B1 04           mov cl, 4
061D  D3 C2           rol dx, cl
061F  8B CA           mov cx, dx
0621  83 E1 F0        and cx, 0xfff0
0624  83 E2 0F        and dx, 0xf
0627  0B C1           or ax, cx
0629  C3              ret

; ---- routine 23E4:062A  (found by: far)
sub_062A:
062A  FC              cld
062B  8B DC           mov bx, sp
062D  8C DA           mov dx, ds
062F  36 C4 7F 08     les di, ptr ss:[bx + 8]
0633  36 C5 77 04     lds si, ptr ss:[bx + 4]
0637  AC              lodsb al, byte ptr [si]
0638  AA              stosb byte ptr es:[di], al
0639  8A C8           mov cl, al
063B  32 ED           xor ch, ch
063D  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
063F  8E DA           mov ds, dx
0641  CA 04 00        retf 4

; ---- routine 23E4:0644  (found by: call, far)
sub_0644:
0644  FC              cld
0645  8B DC           mov bx, sp
0647  8C DA           mov dx, ds
0649  36 C5 77 0A     lds si, ptr ss:[bx + 0xa]
064D  36 C4 7F 06     les di, ptr ss:[bx + 6]
0651  36 8B 4F 04     mov cx, word ptr ss:[bx + 4]
0655  AC              lodsb al, byte ptr [si]
0656  3A C1           cmp al, cl
0658  76 02           jbe 0x65c
065A  8A C1           mov al, cl
loc_065C:
065C  AA              stosb byte ptr es:[di], al
065D  8A C8           mov cl, al
065F  32 ED           xor ch, ch
0661  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
0663  8E DA           mov ds, dx
0665  CA 0A 00        retf 0xa
; data (not reached as code), 14 bytes
0668                  db 8B DC 36 C4 7F 04 26 8A 05 32 E4 CA 04 00   ; ..6...&..2....

; ---- routine 23E4:0676  (found by: call, far)
sub_0676:
0676  FC              cld
0677  8B DC           mov bx, sp
0679  8C DA           mov dx, ds
067B  36 C4 7F 0C     les di, ptr ss:[bx + 0xc]
067F  36 C5 77 08     lds si, ptr ss:[bx + 8]
0683  8A 04           mov al, byte ptr [si]
0685  32 E4           xor ah, ah
0687  36 8B 4F 06     mov cx, word ptr ss:[bx + 6]
068B  0B C9           or cx, cx
068D  7F 03           jg 0x692
068F  B9 01 00        mov cx, 1
loc_0692:
0692  03 F1           add si, cx
0694  2B C1           sub ax, cx
0696  72 13           jb 0x6ab
0698  40              inc ax
0699  36 8B 4F 04     mov cx, word ptr ss:[bx + 4]
069D  0B C9           or cx, cx
069F  7D 02           jge 0x6a3
06A1  33 C9           xor cx, cx
loc_06A3:
06A3  3B C1           cmp ax, cx
06A5  76 06           jbe 0x6ad
06A7  8B C1           mov ax, cx
06A9  EB 02           jmp 0x6ad
loc_06AB:
06AB  33 C0           xor ax, ax
loc_06AD:
06AD  AA              stosb byte ptr es:[di], al
06AE  8B C8           mov cx, ax
06B0  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
06B2  8E DA           mov ds, dx
06B4  CA 08 00        retf 8

; ---- routine 23E4:06B7  (found by: call, far)
sub_06B7:
06B7  FC              cld
06B8  8B DC           mov bx, sp
06BA  8C DA           mov dx, ds
06BC  36 C4 7F 08     les di, ptr ss:[bx + 8]
06C0  36 C5 77 04     lds si, ptr ss:[bx + 4]
06C4  26 8A 0D        mov cl, byte ptr es:[di]
06C7  32 ED           xor ch, ch
06C9  AC              lodsb al, byte ptr [si]
06CA  26 00 05        add byte ptr es:[di], al
06CD  73 08           jae 0x6d7
06CF  26 C6 05 FF     mov byte ptr es:[di], 0xff
06D3  8A C1           mov al, cl
06D5  F6 D0           not al
loc_06D7:
06D7  03 F9           add di, cx
06D9  47              inc di
06DA  8A C8           mov cl, al
06DC  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
06DE  8E DA           mov ds, dx
06E0  CA 04 00        retf 4

; ---- routine 23E4:06E3  (found by: far)
sub_06E3:
06E3  FC              cld
06E4  8B DC           mov bx, sp
06E6  1E              push ds
06E7  36 C5 77 08     lds si, ptr ss:[bx + 8]
06EB  36 C4 7F 04     les di, ptr ss:[bx + 4]
06EF  26 8A 0D        mov cl, byte ptr es:[di]
06F2  32 ED           xor ch, ch
06F4  E3 29           jcxz 0x71f
06F6  47              inc di
06F7  AC              lodsb al, byte ptr [si]
06F8  3C 01           cmp al, 1
06FA  72 29           jb 0x725
06FC  77 08           ja 0x706
06FE  AC              lodsb al, byte ptr [si]
06FF  F2 AE           repne scasb al, byte ptr es:[di]
0701  75 1C           jne 0x71f
0703  4F              dec di
0704  EB 1F           jmp 0x725
loc_0706:
0706  32 E4           xor ah, ah
0708  8B D1           mov dx, cx
070A  2B D0           sub dx, ax
070C  72 11           jb 0x71f
070E  42              inc dx
loc_070F:
070F  8B C8           mov cx, ax
0711  F3 A6           repe cmpsb byte ptr [si], byte ptr es:[di]
0713  74 0E           je 0x723
0715  2B C8           sub cx, ax
0717  03 F1           add si, cx
0719  03 F9           add di, cx
071B  47              inc di
071C  4A              dec dx
071D  75 F0           jne 0x70f
loc_071F:
071F  33 C0           xor ax, ax
0721  EB 08           jmp 0x72b
loc_0723:
0723  2B F8           sub di, ax
loc_0725:
0725  8B C7           mov ax, di
0727  36 2B 47 04     sub ax, word ptr ss:[bx + 4]
loc_072B:
072B  1F              pop ds
072C  CA 08 00        retf 8

; ---- routine 23E4:072F  (found by: far)
sub_072F:
072F  FC              cld
0730  8B DC           mov bx, sp
0732  8C DA           mov dx, ds
0734  36 C5 77 08     lds si, ptr ss:[bx + 8]
0738  36 C4 7F 04     les di, ptr ss:[bx + 4]
073C  AC              lodsb al, byte ptr [si]
073D  26 8A 25        mov ah, byte ptr es:[di]
0740  47              inc di
0741  8A C8           mov cl, al
0743  3A CC           cmp cl, ah
0745  76 02           jbe 0x749
0747  8A CC           mov cl, ah
loc_0749:
0749  0A C9           or cl, cl
074B  74 06           je 0x753
074D  32 ED           xor ch, ch
074F  F3 A6           repe cmpsb byte ptr [si], byte ptr es:[di]
0751  75 02           jne 0x755
loc_0753:
0753  3A C4           cmp al, ah
loc_0755:
0755  8E DA           mov ds, dx
0757  CA 08 00        retf 8

; ---- routine 23E4:075A  (found by: far)
sub_075A:
075A  FC              cld
075B  8B DC           mov bx, sp
075D  36 C4 7F 06     les di, ptr ss:[bx + 6]
0761  B0 01           mov al, 1
0763  AA              stosb byte ptr es:[di], al
0764  36 8A 47 04     mov al, byte ptr ss:[bx + 4]
0768  AA              stosb byte ptr es:[di], al
0769  CA 02 00        retf 2
; data (not reached as code), 27 bytes
076C                  db FC 8B DC 8C DA 36 C4 7F 0A 36 C5 77 06 36 8B 47   ; .....6...6.w.6.G
077C                  db 04 AA 8B C8 F3 A4 8E DA CA 06 00   ; ...........

; ---- routine 23E4:0787  (found by: far)
sub_0787:
0787  55              push bp
0788  8B EC           mov bp, sp
078A  81 EC 00 02     sub sp, 0x200
078E  8D BE 00 FF     lea di, [bp - 0x100]
0792  16              push ss
0793  57              push di
0794  C4 7E 0A        les di, ptr [bp + 0xa]
0797  06              push es
0798  57              push di
0799  B8 01 00        mov ax, 1
079C  50              push ax
079D  8B 46 06        mov ax, word ptr [bp + 6]
07A0  48              dec ax
07A1  50              push ax
07A2  0E              push cs
07A3  E8 D0 FE        call 0x676
07A6  C4 7E 0E        les di, ptr [bp + 0xe]
07A9  06              push es
07AA  57              push di
07AB  0E              push cs
07AC  E8 08 FF        call 0x6b7
07AF  8D BE 00 FE     lea di, [bp - 0x200]
07B3  16              push ss
07B4  57              push di
07B5  C4 7E 0A        les di, ptr [bp + 0xa]
07B8  06              push es
07B9  57              push di
07BA  FF 76 06        push word ptr [bp + 6]
07BD  B8 FF 00        mov ax, 0xff
07C0  50              push ax
07C1  0E              push cs
07C2  E8 B1 FE        call 0x676
07C5  0E              push cs
07C6  E8 EE FE        call 0x6b7
07C9  C4 7E 0A        les di, ptr [bp + 0xa]
07CC  06              push es
07CD  57              push di
07CE  FF 76 08        push word ptr [bp + 8]
07D1  0E              push cs
07D2  E8 6F FE        call 0x644
07D5  8B E5           mov sp, bp
07D7  5D              pop bp
07D8  CA 0C 00        retf 0xc

; ---- routine 23E4:07DB  (found by: far)
sub_07DB:
07DB  55              push bp
07DC  8B EC           mov bp, sp
07DE  81 EC 00 02     sub sp, 0x200
07E2  83 7E 06 00     cmp word ptr [bp + 6], 0
07E6  7E 43           jle 0x82b
07E8  8D BE 00 FF     lea di, [bp - 0x100]
07EC  16              push ss
07ED  57              push di
07EE  C4 7E 0A        les di, ptr [bp + 0xa]
07F1  06              push es
07F2  57              push di
07F3  B8 01 00        mov ax, 1
07F6  50              push ax
07F7  8B 46 08        mov ax, word ptr [bp + 8]
07FA  48              dec ax
07FB  50              push ax
07FC  0E              push cs
07FD  E8 76 FE        call 0x676
0800  8D BE 00 FE     lea di, [bp - 0x200]
0804  16              push ss
0805  57              push di
0806  C4 7E 0A        les di, ptr [bp + 0xa]
0809  06              push es
080A  57              push di
080B  8B 46 08        mov ax, word ptr [bp + 8]
080E  03 46 06        add ax, word ptr [bp + 6]
0811  50              push ax
0812  B8 FF 00        mov ax, 0xff
0815  50              push ax
0816  0E              push cs
0817  E8 5C FE        call 0x676
081A  0E              push cs
081B  E8 99 FE        call 0x6b7
081E  C4 7E 0A        les di, ptr [bp + 0xa]
0821  06              push es
0822  57              push di
0823  B8 FF 00        mov ax, 0xff
0826  50              push ax
0827  0E              push cs
0828  E8 19 FE        call 0x644
loc_082B:
082B  8B E5           mov sp, bp
082D  5D              pop bp
082E  CA 08 00        retf 8

; ---- routine 23E4:0831  (found by: far)
sub_0831:
0831  FC              cld
0832  8B DC           mov bx, sp
0834  8C DA           mov dx, ds
0836  36 C4 7F 0A     les di, ptr ss:[bx + 0xa]
083A  36 C5 77 06     lds si, ptr ss:[bx + 6]
083E  36 8B 5F 04     mov bx, word ptr ss:[bx + 4]
0842  8A CF           mov cl, bh
0844  32 ED           xor ch, ch
0846  32 C0           xor al, al
0848  F3 AA           rep stosb byte ptr es:[di], al
084A  8A CB           mov cl, bl
084C  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
084E  B1 20           mov cl, 0x20
0850  2A CB           sub cl, bl
0852  2A CF           sub cl, bh
0854  F3 AA           rep stosb byte ptr es:[di], al
0856  8E DA           mov ds, dx
0858  CA 06 00        retf 6
; data (not reached as code), 100 bytes
085B                  db FC 8B DC 36 C4 7F 04 B9 10 00 33 C0 F3 AB CB 8B   ; ...6......3.....
086B                  db DC 36 C4 7F 06 36 8A 47 04 8A D8 32 FF B1 03 D3   ; .6...6.G...2....
087B                  db EB 8A C8 80 E1 07 B0 01 D2 E0 26 08 01 CA 02 00   ; ..........&.....
088B                  db 8B DC 36 C4 7F 08 36 8A 47 06 36 8A 57 04 2A D0   ; ..6...6.G.6.W.*.
089B                  db 72 1F FE C2 8A D8 32 FF B1 03 D3 EB 8A C8 80 E1   ; r.....2.........
08AB                  db 07 B0 01 D2 E0 26 08 01 D0 C0 83 D3 00 FE CA 75   ; .....&.........u
08BB                  db F4 CA 04 00   ; ....

; ---- routine 23E4:08BF  (found by: far)
sub_08BF:
08BF  FC              cld
08C0  8B DC           mov bx, sp
08C2  8C DA           mov dx, ds
08C4  36 C5 77 0A     lds si, ptr ss:[bx + 0xa]
08C8  36 C4 7F 06     les di, ptr ss:[bx + 6]
08CC  36 8B 5F 04     mov bx, word ptr ss:[bx + 4]
08D0  8A CF           mov cl, bh
08D2  32 ED           xor ch, ch
08D4  03 F1           add si, cx
08D6  8A CB           mov cl, bl
08D8  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
08DA  8E DA           mov ds, dx
08DC  CA 0A 00        retf 0xa

; ---- routine 23E4:08DF  (found by: far)
sub_08DF:
08DF  8B DC           mov bx, sp
08E1  36 C4 7F 04     les di, ptr ss:[bx + 4]
08E5  36 8A 47 08     mov al, byte ptr ss:[bx + 8]
08E9  8A D8           mov bl, al
08EB  32 FF           xor bh, bh
08ED  B1 03           mov cl, 3
08EF  D3 EB           shr bx, cl
08F1  8A C8           mov cl, al
08F3  80 E1 07        and cl, 7
08F6  B0 01           mov al, 1
08F8  D2 E0           shl al, cl
08FA  26 84 01        test byte ptr es:[bx + di], al
08FD  CA 06 00        retf 6

; ---- routine 23E4:0900  (found by: far)
sub_0900:
0900  FC              cld
0901  8B DC           mov bx, sp
0903  8C DA           mov dx, ds
0905  36 C4 7F 08     les di, ptr ss:[bx + 8]
0909  36 C5 77 04     lds si, ptr ss:[bx + 4]
090D  B9 10 00        mov cx, 0x10
0910  AD              lodsw ax, word ptr [si]
0911  26 0B 05        or ax, word ptr es:[di]
0914  AB              stosw word ptr es:[di], ax
0915  E2 F9           loop 0x910
0917  8E DA           mov ds, dx
0919  CA 04 00        retf 4
; data (not reached as code), 111 bytes
091C                  db FC 8B DC 8C DA 36 C4 7F 08 36 C5 77 04 B9 10 00   ; .....6...6.w....
092C                  db AD F7 D0 26 23 05 AB E2 F7 8E DA CA 04 00 FC 8B   ; ...&#...........
093C                  db DC 8C DA 36 C4 7F 08 36 C5 77 04 B9 10 00 AD 26   ; ...6...6.w.....&
094C                  db 23 05 AB E2 F9 8E DA CA 04 00 FC 8B DC 8C DA 36   ; #..............6
095C                  db C4 7F 08 36 C5 77 04 B9 10 00 F3 A7 8E DA CA 08   ; ...6.w..........
096C                  db 00 FC 8B DC 8C DA 36 C4 7F 08 36 C5 77 04 B9 10   ; ......6...6.w...
097C                  db 00 AD 26 0B 05 AF 75 02 E2 F7 8E DA CA 08 00   ; ..&...u........

; ---- routine 23E4:098B  (found by: call)
sub_098B:
098B  81 F7 00 80     xor di, 0x8000

; ---- routine 23E4:098F  (found by: call)
sub_098F:
098F  0A C9           or cl, cl
0991  74 7B           je 0xa0e
0993  0A C0           or al, al
0995  74 78           je 0xa0f
0997  3A C1           cmp al, cl
0999  76 05           jbe 0x9a0
099B  91              xchg cx, ax
099C  87 DE           xchg si, bx
099E  87 D7           xchg di, dx
loc_09A0:
09A0  2A C1           sub al, cl
09A2  F6 D8           neg al
09A4  3C 28           cmp al, 0x28
09A6  73 67           jae 0xa0f
09A8  86 C1           xchg cl, al
09AA  55              push bp
09AB  50              push ax
09AC  8A E6           mov ah, dh
09AE  80 E4 80        and ah, 0x80
09B1  8B E8           mov bp, ax
09B3  33 C7           xor ax, di
09B5  58              pop ax
09B6  9C              pushf
09B7  B0 00           mov al, 0
09B9  80 CE 80        or dh, 0x80
09BC  81 CF 00 80     or di, 0x8000
loc_09C0:
09C0  80 F9 08        cmp cl, 8
09C3  72 11           jb 0x9d6
09C5  8A C4           mov al, ah
09C7  8A E3           mov ah, bl
09C9  8A DF           mov bl, bh
09CB  8A FA           mov bh, dl
09CD  8A D6           mov dl, dh
09CF  32 F6           xor dh, dh
09D1  80 E9 08        sub cl, 8
09D4  EB EA           jmp 0x9c0
loc_09D6:
09D6  0A C9           or cl, cl
09D8  74 0A           je 0x9e4
loc_09DA:
09DA  D1 EA           shr dx, 1
09DC  D1 DB           rcr bx, 1
09DE  D1 D8           rcr ax, 1
09E0  FE C9           dec cl
09E2  75 F6           jne 0x9da
loc_09E4:
09E4  9D              popf
09E5  78 37           js 0xa1e
09E7  03 C1           add ax, cx
09E9  13 DE           adc bx, si
09EB  13 D7           adc dx, di
09ED  8B CD           mov cx, bp
09EF  5D              pop bp
09F0  73 0A           jae 0x9fc
09F2  D1 DA           rcr dx, 1
09F4  D1 DB           rcr bx, 1
09F6  D1 D8           rcr ax, 1
09F8  FE C1           inc cl
09FA  74 20           je 0xa1c
loc_09FC:
09FC  05 80 00        add ax, 0x80
09FF  83 D3 00        adc bx, 0
0A02  83 D2 00        adc dx, 0
0A05  72 0F           jb 0xa16
loc_0A07:
0A07  8A C1           mov al, cl
0A09  80 E6 7F        and dh, 0x7f
0A0C  0A F5           or dh, ch
loc_0A0E:
0A0E  C3              ret
loc_0A0F:
0A0F  8B C1           mov ax, cx
0A11  8B DE           mov bx, si
0A13  8B D7           mov dx, di
0A15  C3              ret
loc_0A16:
0A16  D1 DA           rcr dx, 1
0A18  FE C1           inc cl
0A1A  75 EB           jne 0xa07
loc_0A1C:
0A1C  F9              stc
0A1D  C3              ret
loc_0A1E:
0A1E  2B C1           sub ax, cx
0A20  1B DE           sbb bx, si
0A22  1B D7           sbb dx, di
0A24  8B CD           mov cx, bp
0A26  5D              pop bp
0A27  73 10           jae 0xa39
0A29  F7 D2           not dx
0A2B  F7 D3           not bx
0A2D  F7 D8           neg ax
0A2F  F5              cmc
0A30  83 D3 00        adc bx, 0
0A33  83 D2 00        adc dx, 0
0A36  80 F5 80        xor ch, 0x80
loc_0A39:
0A39  8B FA           mov di, dx
0A3B  0B FB           or di, bx
0A3D  0B F8           or di, ax
0A3F  74 CD           je 0xa0e
loc_0A41:
0A41  0A F6           or dh, dh
0A43  78 B7           js 0x9fc
0A45  D1 E0           shl ax, 1
0A47  D1 D3           rcl bx, 1
0A49  D1 D2           rcl dx, 1
0A4B  FE C9           dec cl
0A4D  75 F2           jne 0xa41
loc_0A4F:
0A4F  E9 FE 00        jmp 0xb50

