; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 8 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:60CB  (found by: call, far)
sub_60CB:
60CB  55              push bp
60CC  89 E5           mov bp, sp
60CE  81 EC 30 03     sub sp, 0x330
60D2  C4 3E 23 A9     les di, ptr [0xa923]
60D6  89 7E D5        mov word ptr [bp - 0x2b], di
60D9  8C 46 D7        mov word ptr [bp - 0x29], es
60DC  8B 46 06        mov ax, word ptr [bp + 6]
60DF  BA BF 00        mov dx, 0xbf
60E2  F7 E2           mul dx
60E4  C4 3E 17 A9     les di, ptr [0xa917]
60E8  03 F8           add di, ax
60EA  89 7E D1        mov word ptr [bp - 0x2f], di
60ED  8C 46 D3        mov word ptr [bp - 0x2d], es
60F0  C4 7E D5        les di, ptr [bp - 0x2b]
60F3  26 8A 45 01     mov al, byte ptr es:[di + 1]
60F7  30 E4           xor ah, ah
60F9  89 46 E9        mov word ptr [bp - 0x17], ax
60FC  C4 7E D1        les di, ptr [bp - 0x2f]
60FF  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
6103  30 E4           xor ah, ah
6105  2D 80 00        sub ax, 0x80
6108  C4 7E D5        les di, ptr [bp - 0x2b]
610B  26 88 45 01     mov byte ptr es:[di + 1], al
610F  E8 7C A2        call 0x38e
6112  C4 7E D5        les di, ptr [bp - 0x2b]
6115  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
611A  74 0C           je 0x6128
611C  C4 7E D5        les di, ptr [bp - 0x2b]
611F  26 8B 45 36     mov ax, word ptr es:[di + 0x36]
6123  89 46 E1        mov word ptr [bp - 0x1f], ax
6126  EB 17           jmp 0x613f
loc_6128:
6128  C4 7E D1        les di, ptr [bp - 0x2f]
612B  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
612F  30 E4           xor ah, ah
6131  D1 E0           shl ax, 1
6133  C4 7E D5        les di, ptr [bp - 0x2b]
6136  03 F8           add di, ax
6138  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
613C  89 46 E1        mov word ptr [bp - 0x1f], ax
loc_613F:
613F  C4 7E D5        les di, ptr [bp - 0x2b]
6142  26 8A 45 01     mov al, byte ptr es:[di + 1]
6146  30 E4           xor ah, ah
6148  8B D0           mov dx, ax
614A  C4 7E D5        les di, ptr [bp - 0x2b]
614D  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
6151  98              cwde
6152  D1 E0           shl ax, 1
6154  8B F0           mov si, ax
6156  D1 E0           shl ax, 1
6158  03 C6           add ax, si
615A  C4 7E D5        les di, ptr [bp - 0x2b]
615D  03 F8           add di, ax
615F  03 FA           add di, dx
6161  26 8A 45 07     mov al, byte ptr es:[di + 7]
6165  30 E4           xor ah, ah
6167  89 46 DF        mov word ptr [bp - 0x21], ax
616A  B8 01 00        mov ax, 1
616D  50              push ax
616E  8B 46 06        mov ax, word ptr [bp + 6]
6171  B1 04           mov cl, 4
6173  D3 E0           shl ax, cl
6175  C4 3E 68 9B     les di, ptr [0x9b68]
6179  03 F8           add di, ax
617B  06              push es
617C  57              push di
617D  E8 8B A5        call 0x70b
6180  C4 7E D5        les di, ptr [bp - 0x2b]
6183  26 8A 45 01     mov al, byte ptr es:[di + 1]
6187  30 E4           xor ah, ah
6189  C4 7E D5        les di, ptr [bp - 0x2b]
618C  03 F8           add di, ax
618E  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
6193  75 07           jne 0x619c
6195  55              push bp
6196  E8 D3 FC        call 0x5e6c
6199  E9 5B 04        jmp 0x65f7
loc_619C:
619C  C4 7E D5        les di, ptr [bp - 0x2b]
619F  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
61A4  74 10           je 0x61b6
61A6  9A D8 59 71 17  call far 1771:59D8
61AB  08 C0           or al, al
61AD  74 07           je 0x61b6
61AF  C7 46 E5 01 00  mov word ptr [bp - 0x1b], 1
61B4  EB 0C           jmp 0x61c2
loc_61B6:
61B6  C4 7E D1        les di, ptr [bp - 0x2f]
61B9  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
61BD  30 E4           xor ah, ah
61BF  89 46 E5        mov word ptr [bp - 0x1b], ax
loc_61C2:
61C2  C7 46 E7 01 00  mov word ptr [bp - 0x19], 1
61C7  C4 7E D5        les di, ptr [bp - 0x2b]
61CA  26 8A 45 01     mov al, byte ptr es:[di + 1]
61CE  30 E4           xor ah, ah
61D0  C4 7E D5        les di, ptr [bp - 0x2b]
61D3  03 F8           add di, ax
61D5  26 8A 45 01     mov al, byte ptr es:[di + 1]
61D9  30 E4           xor ah, ah
61DB  BA 38 00        mov dx, 0x38
61DE  F7 E2           mul dx
61E0  50              push ax
61E1  8B 46 E5        mov ax, word ptr [bp - 0x1b]
61E4  BA C0 01        mov dx, 0x1c0
61E7  F7 E2           mul dx
61E9  50              push ax
61EA  9A D8 59 71 17  call far 1771:59D8
61EF  98              cwde
61F0  BA 00 07        mov dx, 0x700
61F3  F7 E2           mul dx
61F5  8B C8           mov cx, ax
61F7  C4 7E D5        les di, ptr [bp - 0x2b]
61FA  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
61FE  98              cwde
61FF  BA 00 0E        mov dx, 0xe00
6202  F7 E2           mul dx
6204  C4 3E 33 A9     les di, ptr [0xa933]
6208  03 F8           add di, ax
620A  03 F9           add di, cx
620C  58              pop ax
620D  03 F8           add di, ax
620F  58              pop ax
6210  03 F8           add di, ax
6212  81 C7 08 FE     add di, 0xfe08
6216  89 7E CD        mov word ptr [bp - 0x33], di
6219  8C 46 CF        mov word ptr [bp - 0x31], es
621C  C7 46 E3 01 00  mov word ptr [bp - 0x1d], 1
6221  EB 03           jmp 0x6226
loc_6223:
6223  FF 46 E3        inc word ptr [bp - 0x1d]
loc_6226:
6226  8B 46 E7        mov ax, word ptr [bp - 0x19]
6229  B1 03           mov cl, 3
622B  D3 E0           shl ax, cl
622D  C4 7E CD        les di, ptr [bp - 0x33]
6230  03 F8           add di, ax
6232  26 8B 45 F8     mov ax, word ptr es:[di - 8]
6236  3B 46 06        cmp ax, word ptr [bp + 6]
6239  75 03           jne 0x623e
623B  FF 46 E7        inc word ptr [bp - 0x19]
loc_623E:
623E  8B 46 E7        mov ax, word ptr [bp - 0x19]
6241  B1 03           mov cl, 3
6243  D3 E0           shl ax, cl
6245  C4 7E CD        les di, ptr [bp - 0x33]
6248  03 F8           add di, ax
624A  26 8B 45 F8     mov ax, word ptr es:[di - 8]
624E  8B 7E E3        mov di, word ptr [bp - 0x1d]
6251  D1 E7           shl di, 1
6253  89 43 D7        mov word ptr [bp + di - 0x29], ax
6256  FF 46 E7        inc word ptr [bp - 0x19]
6259  83 7E E3 03     cmp word ptr [bp - 0x1d], 3
625D  75 C4           jne 0x6223
625F  9A D8 59 71 17  call far 1771:59D8
6264  08 C0           or al, al
6266  74 2D           je 0x6295
6268  8B 46 E1        mov ax, word ptr [bp - 0x1f]
626B  3B 46 06        cmp ax, word ptr [bp + 6]
626E  75 25           jne 0x6295
6270  B8 02 00        mov ax, 2
6273  50              push ax
6274  BF DE 5F        mov di, 0x5fde
6277  0E              push cs
6278  57              push di
6279  E8 8F A4        call 0x70b
627C  B8 03 00        mov ax, 3
627F  50              push ax
6280  FF 76 06        push word ptr [bp + 6]
6283  E8 F2 F6        call 0x5978
6286  B8 08 00        mov ax, 8
6289  50              push ax
628A  BF E9 5F        mov di, 0x5fe9
628D  0E              push cs
628E  57              push di
628F  E8 79 A4        call 0x70b
6292  E9 92 00        jmp 0x6327
loc_6295:
6295  9A D8 59 71 17  call far 1771:59D8
629A  08 C0           or al, al
629C  74 1F           je 0x62bd
629E  B8 02 00        mov ax, 2
62A1  50              push ax
62A2  BF FE 5F        mov di, 0x5ffe
62A5  0E              push cs
62A6  57              push di
62A7  E8 61 A4        call 0x70b
62AA  B8 03 00        mov ax, 3
62AD  50              push ax
62AE  BF 0C 60        mov di, 0x600c
62B1  0E              push cs
62B2  57              push di
62B3  E8 55 A4        call 0x70b
62B6  C7 46 E7 04 00  mov word ptr [bp - 0x19], 4
62BB  EB 1D           jmp 0x62da
loc_62BD:
62BD  B8 01 00        mov ax, 1
62C0  50              push ax
62C1  BF E9 5F        mov di, 0x5fe9
62C4  0E              push cs
62C5  57              push di
62C6  E8 42 A4        call 0x70b
62C9  B8 02 00        mov ax, 2
62CC  50              push ax
62CD  BF 1A 60        mov di, 0x601a
62D0  0E              push cs
62D1  57              push di
62D2  E8 36 A4        call 0x70b
62D5  C7 46 E7 03 00  mov word ptr [bp - 0x19], 3
loc_62DA:
62DA  FF 76 E7        push word ptr [bp - 0x19]
62DD  FF 76 06        push word ptr [bp + 6]
62E0  E8 95 F6        call 0x5978
62E3  9A D8 59 71 17  call far 1771:59D8
62E8  08 C0           or al, al
62EA  74 3B           je 0x6327
62EC  C4 7E D5        les di, ptr [bp - 0x2b]
62EF  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
62F3  30 E4           xor ah, ah
62F5  8B D0           mov dx, ax
62F7  8B 46 E7        mov ax, word ptr [bp - 0x19]
62FA  05 02 00        add ax, 2
62FD  2B C2           sub ax, dx
62FF  50              push ax
6300  8D BE D1 FE     lea di, [bp - 0x12f]
6304  16              push ss
6305  57              push di
6306  BF 2D 60        mov di, 0x602d
6309  0E              push cs
630A  57              push di
630B  9A 2A 06 E4 23  call far 23E4:062A
6310  8B 46 E1        mov ax, word ptr [bp - 0x1f]
6313  B1 04           mov cl, 4
6315  D3 E0           shl ax, cl
6317  C4 3E 68 9B     les di, ptr [0x9b68]
631B  03 F8           add di, ax
631D  06              push es
631E  57              push di
631F  9A B7 06 E4 23  call far 23E4:06B7
6324  E8 E4 A3        call 0x70b
loc_6327:
6327  9A FA 06 4B 21  call far 214B:06FA
632C  08 C0           or al, al
632E  74 15           je 0x6345
6330  BF 31 60        mov di, 0x6031
6333  0E              push cs
6334  57              push di
6335  8D 7E EB        lea di, [bp - 0x15]
6338  16              push ss
6339  57              push di
633A  B8 14 00        mov ax, 0x14
633D  50              push ax
633E  9A 44 06 E4 23  call far 23E4:0644
6343  EB 13           jmp 0x6358
loc_6345:
6345  BF 36 60        mov di, 0x6036
6348  0E              push cs
6349  57              push di
634A  8D 7E EB        lea di, [bp - 0x15]
634D  16              push ss
634E  57              push di
634F  B8 14 00        mov ax, 0x14
6352  50              push ax
6353  9A 44 06 E4 23  call far 23E4:0644
loc_6358:
6358  B8 09 00        mov ax, 9
635B  50              push ax
635C  8D BE D1 FE     lea di, [bp - 0x12f]
6360  16              push ss
6361  57              push di
6362  8B 46 06        mov ax, word ptr [bp + 6]
6365  B1 04           mov cl, 4
6367  D3 E0           shl ax, cl
6369  C4 3E 68 9B     les di, ptr [0x9b68]
636D  03 F8           add di, ax
636F  06              push es
6370  57              push di
6371  9A 2A 06 E4 23  call far 23E4:062A
6376  BF 3B 60        mov di, 0x603b
6379  0E              push cs
637A  57              push di
637B  9A B7 06 E4 23  call far 23E4:06B7
6380  8D 7E EB        lea di, [bp - 0x15]
6383  16              push ss
6384  57              push di
6385  9A B7 06 E4 23  call far 23E4:06B7
638A  E8 7E A3        call 0x70b
638D  B8 0A 00        mov ax, 0xa
6390  50              push ax
6391  8D BE D1 FE     lea di, [bp - 0x12f]
6395  16              push ss
6396  57              push di
6397  8B 46 D9        mov ax, word ptr [bp - 0x27]
639A  B1 04           mov cl, 4
639C  D3 E0           shl ax, cl
639E  C4 3E 68 9B     les di, ptr [0x9b68]
63A2  03 F8           add di, ax
63A4  06              push es
63A5  57              push di
63A6  9A 2A 06 E4 23  call far 23E4:062A
63AB  BF 3D 60        mov di, 0x603d
63AE  0E              push cs
63AF  57              push di
63B0  9A B7 06 E4 23  call far 23E4:06B7
63B5  E8 53 A3        call 0x70b
63B8  B8 0B 00        mov ax, 0xb
63BB  50              push ax
63BC  8D BE D1 FE     lea di, [bp - 0x12f]
63C0  16              push ss
63C1  57              push di
63C2  8B 46 DB        mov ax, word ptr [bp - 0x25]
63C5  B1 04           mov cl, 4
63C7  D3 E0           shl ax, cl
63C9  C4 3E 68 9B     les di, ptr [0x9b68]
63CD  03 F8           add di, ax
63CF  06              push es
63D0  57              push di
63D1  9A 2A 06 E4 23  call far 23E4:062A
63D6  BF 3D 60        mov di, 0x603d
63D9  0E              push cs
63DA  57              push di
63DB  9A B7 06 E4 23  call far 23E4:06B7
63E0  E8 28 A3        call 0x70b
63E3  B8 0C 00        mov ax, 0xc
63E6  50              push ax
63E7  8D BE D1 FE     lea di, [bp - 0x12f]
63EB  16              push ss
63EC  57              push di
63ED  BF 3F 60        mov di, 0x603f
63F0  0E              push cs
63F1  57              push di
63F2  9A 2A 06 E4 23  call far 23E4:062A
63F7  8B 46 DD        mov ax, word ptr [bp - 0x23]
63FA  B1 04           mov cl, 4
63FC  D3 E0           shl ax, cl
63FE  C4 3E 68 9B     les di, ptr [0x9b68]
6402  03 F8           add di, ax
6404  06              push es
6405  57              push di
6406  9A B7 06 E4 23  call far 23E4:06B7
640B  E8 FD A2        call 0x70b
640E  9A D8 59 71 17  call far 1771:59D8
6413  08 C0           or al, al
6415  74 4B           je 0x6462
6417  8B 46 E1        mov ax, word ptr [bp - 0x1f]
641A  3B 46 06        cmp ax, word ptr [bp + 6]
641D  75 43           jne 0x6462
641F  BF 44 60        mov di, 0x6044
6422  0E              push cs
6423  57              push di
6424  8B 46 06        mov ax, word ptr [bp + 6]
6427  B1 04           mov cl, 4
6429  D3 E0           shl ax, cl
642B  C4 3E 68 9B     les di, ptr [0x9b68]
642F  03 F8           add di, ax
6431  06              push es
6432  57              push di
6433  BF 53 60        mov di, 0x6053
6436  0E              push cs
6437  57              push di
6438  E8 F4 A1        call 0x62f
643B  55              push bp
643C  E8 70 F9        call 0x5daf
643F  08 C0           or al, al
6441  75 1C           jne 0x645f
6443  8B 46 06        mov ax, word ptr [bp + 6]
6446  B1 04           mov cl, 4
6448  D3 E0           shl ax, cl
644A  C4 3E 68 9B     les di, ptr [0x9b68]
644E  03 F8           add di, ax
6450  06              push es
6451  57              push di
6452  BF 54 60        mov di, 0x6054
6455  0E              push cs
6456  57              push di
6457  BF 62 60        mov di, 0x6062
645A  0E              push cs
645B  57              push di
645C  E8 00 A3        call 0x75f
loc_645F:
645F  E9 95 01        jmp 0x65f7
loc_6462:
6462  31 C0           xor ax, ax
6464  89 46 E7        mov word ptr [bp - 0x19], ax
6467  C7 46 E3 01 00  mov word ptr [bp - 0x1d], 1
646C  EB 03           jmp 0x6471
loc_646E:
646E  FF 46 E3        inc word ptr [bp - 0x1d]
loc_6471:
6471  8B 7E E3        mov di, word ptr [bp - 0x1d]
6474  D1 E7           shl di, 1
6476  FF 73 D7        push word ptr [bp + di - 0x29]
6479  9A E7 10 71 17  call far 1771:10E7
647E  01 46 E7        add word ptr [bp - 0x19], ax
6481  83 7E E3 03     cmp word ptr [bp - 0x1d], 3
6485  75 E7           jne 0x646e
6487  FF 76 06        push word ptr [bp + 6]
648A  9A E7 10 71 17  call far 1771:10E7
648F  D1 E0           shl ax, 1
6491  99              cdq
6492  8B C8           mov cx, ax
6494  8B DA           mov bx, dx
6496  8B 46 E7        mov ax, word ptr [bp - 0x19]
6499  31 D2           xor dx, dx
649B  3B D3           cmp dx, bx
649D  7C 06           jl 0x64a5
649F  7F 22           jg 0x64c3
64A1  3B C1           cmp ax, cx
64A3  73 1E           jae 0x64c3
loc_64A5:
64A5  8B 46 06        mov ax, word ptr [bp + 6]
64A8  B1 04           mov cl, 4
64AA  D3 E0           shl ax, cl
64AC  C4 3E 68 9B     les di, ptr [0x9b68]
64B0  03 F8           add di, ax
64B2  06              push es
64B3  57              push di
64B4  BF 6C 60        mov di, 0x606c
64B7  0E              push cs
64B8  57              push di
64B9  BF 53 60        mov di, 0x6053
64BC  0E              push cs
64BD  57              push di
64BE  E8 6E A1        call 0x62f
64C1  EB 5B           jmp 0x651e
loc_64C3:
64C3  FF 76 06        push word ptr [bp + 6]
64C6  9A E7 10 71 17  call far 1771:10E7
64CB  B9 03 00        mov cx, 3
64CE  F7 E9           imul cx
64D0  99              cdq
64D1  8B C8           mov cx, ax
64D3  8B DA           mov bx, dx
64D5  8B 46 E7        mov ax, word ptr [bp - 0x19]
64D8  31 D2           xor dx, dx
64DA  3B D3           cmp dx, bx
64DC  7C 06           jl 0x64e4
64DE  7F 22           jg 0x6502
64E0  3B C1           cmp ax, cx
64E2  73 1E           jae 0x6502
loc_64E4:
64E4  8B 46 06        mov ax, word ptr [bp + 6]
64E7  B1 04           mov cl, 4
64E9  D3 E0           shl ax, cl
64EB  C4 3E 68 9B     les di, ptr [0x9b68]
64EF  03 F8           add di, ax
64F1  06              push es
64F2  57              push di
64F3  BF 7D 60        mov di, 0x607d
64F6  0E              push cs
64F7  57              push di
64F8  BF 53 60        mov di, 0x6053
64FB  0E              push cs
64FC  57              push di
64FD  E8 2F A1        call 0x62f
6500  EB 1C           jmp 0x651e
loc_6502:
6502  BF 8F 60        mov di, 0x608f
6505  0E              push cs
6506  57              push di
6507  8B 46 06        mov ax, word ptr [bp + 6]
650A  B1 04           mov cl, 4
650C  D3 E0           shl ax, cl
650E  C4 3E 68 9B     les di, ptr [0x9b68]
6512  03 F8           add di, ax
6514  06              push es
6515  57              push di
6516  BF 53 60        mov di, 0x6053
6519  0E              push cs
651A  57              push di
651B  E8 11 A1        call 0x62f
loc_651E:
651E  8B 46 06        mov ax, word ptr [bp + 6]
6521  89 46 E7        mov word ptr [bp - 0x19], ax
6524  C7 46 E3 01 00  mov word ptr [bp - 0x1d], 1
6529  EB 03           jmp 0x652e
loc_652B:
652B  FF 46 E3        inc word ptr [bp - 0x1d]
loc_652E:
652E  FF 76 E7        push word ptr [bp - 0x19]
6531  9A E7 10 71 17  call far 1771:10E7
6536  50              push ax
6537  8B 7E E3        mov di, word ptr [bp - 0x1d]
653A  D1 E7           shl di, 1
653C  FF 73 D7        push word ptr [bp + di - 0x29]
653F  9A E7 10 71 17  call far 1771:10E7
6544  5A              pop dx
6545  3B C2           cmp ax, dx
6547  7E 0B           jle 0x6554
6549  8B 7E E3        mov di, word ptr [bp - 0x1d]
654C  D1 E7           shl di, 1
654E  8B 43 D7        mov ax, word ptr [bp + di - 0x29]
6551  89 46 E7        mov word ptr [bp - 0x19], ax
loc_6554:
6554  83 7E E3 03     cmp word ptr [bp - 0x1d], 3
6558  75 D1           jne 0x652b
655A  9A FA 06 4B 21  call far 214B:06FA
655F  08 C0           or al, al
6561  74 15           je 0x6578
6563  BF 9E 60        mov di, 0x609e
6566  0E              push cs
6567  57              push di
6568  8D 7E EB        lea di, [bp - 0x15]
656B  16              push ss
656C  57              push di
656D  B8 14 00        mov ax, 0x14
6570  50              push ax
6571  9A 44 06 E4 23  call far 23E4:0644
6576  EB 13           jmp 0x658b
loc_6578:
6578  BF AF 60        mov di, 0x60af
657B  0E              push cs
657C  57              push di
657D  8D 7E EB        lea di, [bp - 0x15]
6580  16              push ss
6581  57              push di
6582  B8 14 00        mov ax, 0x14
6585  50              push ax
6586  9A 44 06 E4 23  call far 23E4:0644
loc_658B:
658B  55              push bp
658C  E8 20 F8        call 0x5daf
658F  08 C0           or al, al
6591  75 64           jne 0x65f7
6593  8D BE D1 FE     lea di, [bp - 0x12f]
6597  16              push ss
6598  57              push di
6599  8B 46 E7        mov ax, word ptr [bp - 0x19]
659C  B1 04           mov cl, 4
659E  D3 E0           shl ax, cl
65A0  C4 3E 68 9B     les di, ptr [0x9b68]
65A4  03 F8           add di, ax
65A6  06              push es
65A7  57              push di
65A8  9A 2A 06 E4 23  call far 23E4:062A
65AD  BF C0 60        mov di, 0x60c0
65B0  0E              push cs
65B1  57              push di
65B2  9A B7 06 E4 23  call far 23E4:06B7
65B7  8D 7E EB        lea di, [bp - 0x15]
65BA  16              push ss
65BB  57              push di
65BC  8D BE D1 FC     lea di, [bp - 0x32f]
65C0  16              push ss
65C1  57              push di
65C2  BF C4 60        mov di, 0x60c4
65C5  0E              push cs
65C6  57              push di
65C7  9A 2A 06 E4 23  call far 23E4:062A
65CC  8D BE D1 FD     lea di, [bp - 0x22f]
65D0  16              push ss
65D1  57              push di
65D2  C4 7E D5        les di, ptr [bp - 0x2b]
65D5  26 8A 45 01     mov al, byte ptr es:[di + 1]
65D9  30 E4           xor ah, ah
65DB  C4 7E D5        les di, ptr [bp - 0x2b]
65DE  03 F8           add di, ax
65E0  26 8A 45 01     mov al, byte ptr es:[di + 1]
65E4  30 E4           xor ah, ah
65E6  05 40 00        add ax, 0x40
65E9  50              push ax
65EA  9A 5A 07 E4 23  call far 23E4:075A
65EF  9A B7 06 E4 23  call far 23E4:06B7
65F4  E8 68 A1        call 0x75f
loc_65F7:
65F7  9A D8 59 71 17  call far 1771:59D8
65FC  08 C0           or al, al
65FE  74 15           je 0x6615
6600  C4 7E D5        les di, ptr [bp - 0x2b]
6603  26 8A 45 01     mov al, byte ptr es:[di + 1]
6607  30 E4           xor ah, ah
6609  C4 7E D5        les di, ptr [bp - 0x2b]
660C  03 F8           add di, ax
660E  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
6613  77 04           ja 0x6619
loc_6615:
6615  B0 00           mov al, 0
6617  EB 02           jmp 0x661b
loc_6619:
6619  B0 01           mov al, 1
loc_661B:
661B  50              push ax
661C  B0 00           mov al, 0
661E  50              push ax
661F  B0 00           mov al, 0
6621  50              push ax
6622  E8 D1 9F        call 0x5f6
6625  8A 46 E9        mov al, byte ptr [bp - 0x17]
6628  C4 7E D5        les di, ptr [bp - 0x2b]
662B  26 88 45 01     mov byte ptr es:[di + 1], al
662F  89 EC           mov sp, bp
6631  5D              pop bp
6632  CA 02 00        retf 2
; data (not reached as code), 80 bytes
6635                  db 01 20   ; . 
6637                  pstr ' IS'
663B                  pstr 'TOP SCORER WITH'
664B                  pstr ' GOALS'
6652                  pstr ' WINS'
6658                  db 00   ; .
6659                  pstr 'PIPPED AT'
6663                  pstr 'THE POST'
666C                  pstr 'LOSE OUT TO'
6678                  pstr 'TRIUMPH OVER'

; ---- routine 000E:6685  (found by: call)
sub_6685:
6685  55              push bp
6686  89 E5           mov bp, sp
6688  81 EC 2E 01     sub sp, 0x12e
668C  C4 3E 23 A9     les di, ptr [0xa923]
6690  89 7E DA        mov word ptr [bp - 0x26], di
6693  8C 46 DC        mov word ptr [bp - 0x24], es
6696  C4 7E 04        les di, ptr [bp + 4]
6699  89 7E D6        mov word ptr [bp - 0x2a], di
669C  8C 46 D8        mov word ptr [bp - 0x28], es
669F  E8 EC 9C        call 0x38e
66A2  C4 7E DA        les di, ptr [bp - 0x26]
66A5  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
66AA  74 07           je 0x66b3
66AC  C7 46 DE 05 00  mov word ptr [bp - 0x22], 5
66B1  EB 1B           jmp 0x66ce
loc_66B3:
66B3  C4 7E D6        les di, ptr [bp - 0x2a]
66B6  26 8B 45 06     mov ax, word ptr es:[di + 6]
66BA  BA BF 00        mov dx, 0xbf
66BD  F7 E2           mul dx
66BF  C4 3E 17 A9     les di, ptr [0xa917]
66C3  03 F8           add di, ax
66C5  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
66C9  30 E4           xor ah, ah
66CB  89 46 DE        mov word ptr [bp - 0x22], ax
loc_66CE:
66CE  8B 46 DE        mov ax, word ptr [bp - 0x22]
66D1  BA 60 00        mov dx, 0x60
66D4  F7 E2           mul dx
66D6  C4 3E 3F A9     les di, ptr [0xa93f]
66DA  03 F8           add di, ax
66DC  81 C7 A0 FF     add di, 0xffa0
66E0  89 7E D2        mov word ptr [bp - 0x2e], di
66E3  8C 46 D4        mov word ptr [bp - 0x2c], es
66E6  C4 7E D2        les di, ptr [bp - 0x2e]
66E9  26 83 7D 0E 00  cmp word ptr es:[di + 0xe], 0
66EE  74 78           je 0x6768
66F0  C4 7E D2        les di, ptr [bp - 0x2e]
66F3  26 83 7D 0C 01  cmp word ptr es:[di + 0xc], 1
66F8  76 6E           jbe 0x6768
66FA  B8 04 00        mov ax, 4
66FD  50              push ax
66FE  8D BE D2 FE     lea di, [bp - 0x12e]
6702  16              push ss
6703  57              push di
6704  C4 7E D2        les di, ptr [bp - 0x2e]
6707  26 8A 05        mov al, byte ptr es:[di]
670A  50              push ax
670B  9A 5A 07 E4 23  call far 23E4:075A
6710  BF 35 66        mov di, 0x6635
6713  0E              push cs
6714  57              push di
6715  9A B7 06 E4 23  call far 23E4:06B7
671A  C4 7E D2        les di, ptr [bp - 0x2e]
671D  81 C7 01 00     add di, 1
6721  06              push es
6722  57              push di
6723  9A B7 06 E4 23  call far 23E4:06B7
6728  BF 37 66        mov di, 0x6637
672B  0E              push cs
672C  57              push di
672D  9A B7 06 E4 23  call far 23E4:06B7
6732  E8 D6 9F        call 0x70b
6735  B8 05 00        mov ax, 5
6738  50              push ax
6739  BF 3B 66        mov di, 0x663b
673C  0E              push cs
673D  57              push di
673E  E8 CA 9F        call 0x70b
6741  B8 06 00        mov ax, 6
6744  50              push ax
6745  8D BE D2 FE     lea di, [bp - 0x12e]
6749  16              push ss
674A  57              push di
674B  C4 7E D2        les di, ptr [bp - 0x2e]
674E  26 8B 45 0C     mov ax, word ptr es:[di + 0xc]
6752  31 D2           xor dx, dx
6754  52              push dx
6755  50              push ax
6756  9A DA 09 4B 21  call far 214B:09DA
675B  BF 4B 66        mov di, 0x664b
675E  0E              push cs
675F  57              push di
6760  9A B7 06 E4 23  call far 23E4:06B7
6765  E8 A3 9F        call 0x70b
loc_6768:
6768  C4 7E 04        les di, ptr [bp + 4]
676B  06              push es
676C  57              push di
676D  9A 94 5C 71 17  call far 1771:5C94
6772  B1 04           mov cl, 4
6774  D3 E0           shl ax, cl
6776  C4 3E 68 9B     les di, ptr [0x9b68]
677A  03 F8           add di, ax
677C  06              push es
677D  57              push di
677E  8D 7E F0        lea di, [bp - 0x10]
6781  16              push ss
6782  57              push di
6783  B8 0F 00        mov ax, 0xf
6786  50              push ax
6787  9A 44 06 E4 23  call far 23E4:0644
678C  C4 7E 04        les di, ptr [bp + 4]
678F  06              push es
6790  57              push di
6791  9A CB 5C 71 17  call far 1771:5CCB
6796  B1 04           mov cl, 4
6798  D3 E0           shl ax, cl
679A  C4 3E 68 9B     les di, ptr [0x9b68]
679E  03 F8           add di, ax
67A0  06              push es
67A1  57              push di
67A2  8D 7E E0        lea di, [bp - 0x20]
67A5  16              push ss
67A6  57              push di
67A7  B8 0F 00        mov ax, 0xf
67AA  50              push ax
67AB  9A 44 06 E4 23  call far 23E4:0644
67B0  B8 01 00        mov ax, 1
67B3  50              push ax
67B4  8D BE D6 FE     lea di, [bp - 0x12a]
67B8  16              push ss
67B9  57              push di
67BA  8D 7E F0        lea di, [bp - 0x10]
67BD  16              push ss
67BE  57              push di
67BF  9A 2A 06 E4 23  call far 23E4:062A
67C4  BF 52 66        mov di, 0x6652
67C7  0E              push cs
67C8  57              push di
67C9  9A B7 06 E4 23  call far 23E4:06B7
67CE  E8 3A 9F        call 0x70b
67D1  B8 02 00        mov ax, 2
67D4  50              push ax
67D5  C4 7E 04        les di, ptr [bp + 4]
67D8  06              push es
67D9  57              push di
67DA  9A 94 5C 71 17  call far 1771:5C94
67DF  50              push ax
67E0  E8 95 F1        call 0x5978
67E3  B8 03 00        mov ax, 3
67E6  50              push ax
67E7  9A B1 06 4B 21  call far 214B:06B1
67EC  8B F8           mov di, ax
67EE  B1 04           mov cl, 4
67F0  D3 E7           shl di, cl
67F2  81 C7 6A 00     add di, 0x6a
67F6  1E              push ds
67F7  57              push di
67F8  8D 7E F0        lea di, [bp - 0x10]
67FB  16              push ss
67FC  57              push di
67FD  BF 58 66        mov di, 0x6658
6800  0E              push cs
6801  57              push di
6802  E8 2A 9E        call 0x62f
6805  B8 03 00        mov ax, 3
6808  50              push ax
6809  9A B1 06 4B 21  call far 214B:06B1
680E  3D 01 00        cmp ax, 1
6811  75 14           jne 0x6827
6813  8D 7E E0        lea di, [bp - 0x20]
6816  16              push ss
6817  57              push di
6818  BF 59 66        mov di, 0x6659
681B  0E              push cs
681C  57              push di
681D  BF 63 66        mov di, 0x6663
6820  0E              push cs
6821  57              push di
6822  E8 3A 9F        call 0x75f
6825  EB 30           jmp 0x6857
loc_6827:
6827  3D 02 00        cmp ax, 2
682A  75 14           jne 0x6840
682C  8D 7E E0        lea di, [bp - 0x20]
682F  16              push ss
6830  57              push di
6831  BF 6C 66        mov di, 0x666c
6834  0E              push cs
6835  57              push di
6836  8D 7E F0        lea di, [bp - 0x10]
6839  16              push ss
683A  57              push di
683B  E8 21 9F        call 0x75f
683E  EB 17           jmp 0x6857
loc_6840:
6840  3D 03 00        cmp ax, 3
6843  75 12           jne 0x6857
6845  8D 7E F0        lea di, [bp - 0x10]
6848  16              push ss
6849  57              push di
684A  BF 78 66        mov di, 0x6678
684D  0E              push cs
684E  57              push di
684F  8D 7E E0        lea di, [bp - 0x20]
6852  16              push ss
6853  57              push di
6854  E8 08 9F        call 0x75f
loc_6857:
6857  B0 00           mov al, 0
6859  50              push ax
685A  B0 00           mov al, 0
685C  50              push ax
685D  B0 00           mov al, 0
685F  50              push ax
6860  E8 93 9D        call 0x5f6
6863  89 EC           mov sp, bp
6865  5D              pop bp
6866  C2 04 00        ret 4
; data (not reached as code), 59 bytes
6869                  pstr 'APPOINT A NEW'
6877                  pstr 'MANAGER'
687F                  pstr 'WELCOME'
6887                  pstr 'ABOARD'
688E                  db 02 20 21   ; . !
6891                  pstr 'CAN '
6896                  pstr 'DO THE JOB ?'
68A3                  db 00   ; .

; ---- routine 000E:68A4  (found by: far)
sub_68A4:
68A4  55              push bp
68A5  89 E5           mov bp, sp
68A7  81 EC 16 01     sub sp, 0x116
68AB  E8 E0 9A        call 0x38e
68AE  B8 01 00        mov ax, 1
68B1  50              push ax
68B2  8B 46 06        mov ax, word ptr [bp + 6]
68B5  B1 04           mov cl, 4
68B7  D3 E0           shl ax, cl
68B9  C4 3E 68 9B     les di, ptr [0x9b68]
68BD  03 F8           add di, ax
68BF  06              push es
68C0  57              push di
68C1  E8 47 9E        call 0x70b
68C4  B8 02 00        mov ax, 2
68C7  50              push ax
68C8  BF 69 68        mov di, 0x6869
68CB  0E              push cs
68CC  57              push di
68CD  E8 3B 9E        call 0x70b
68D0  B8 03 00        mov ax, 3
68D3  50              push ax
68D4  BF 77 68        mov di, 0x6877
68D7  0E              push cs
68D8  57              push di
68D9  E8 2F 9E        call 0x70b
68DC  8D BE EB FE     lea di, [bp - 0x115]
68E0  16              push ss
68E1  57              push di
68E2  8B 46 06        mov ax, word ptr [bp + 6]
68E5  BA BF 00        mov dx, 0xbf
68E8  F7 E2           mul dx
68EA  C4 3E 17 A9     les di, ptr [0xa917]
68EE  03 F8           add di, ax
68F0  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
68F4  30 E4           xor ah, ah
68F6  50              push ax
68F7  9A 47 09 71 17  call far 1771:0947
68FC  8D 7E EB        lea di, [bp - 0x15]
68FF  16              push ss
6900  57              push di
6901  B8 14 00        mov ax, 0x14
6904  50              push ax
6905  9A 44 06 E4 23  call far 23E4:0644
690A  BF 7F 68        mov di, 0x687f
690D  0E              push cs
690E  57              push di
690F  BF 87 68        mov di, 0x6887
6912  0E              push cs
6913  57              push di
6914  8D BE EB FE     lea di, [bp - 0x115]
6918  16              push ss
6919  57              push di
691A  8D 7E EB        lea di, [bp - 0x15]
691D  16              push ss
691E  57              push di
691F  9A 2A 06 E4 23  call far 23E4:062A
6924  BF 8E 68        mov di, 0x688e
6927  0E              push cs
6928  57              push di
6929  9A B7 06 E4 23  call far 23E4:06B7
692E  E8 FE 9C        call 0x62f
6931  8D BE EB FE     lea di, [bp - 0x115]
6935  16              push ss
6936  57              push di
6937  BF 91 68        mov di, 0x6891
693A  0E              push cs
693B  57              push di
693C  9A 2A 06 E4 23  call far 23E4:062A
6941  8D 7E EB        lea di, [bp - 0x15]
6944  16              push ss
6945  57              push di
6946  9A B7 06 E4 23  call far 23E4:06B7
694B  BF 96 68        mov di, 0x6896
694E  0E              push cs
694F  57              push di
6950  BF A3 68        mov di, 0x68a3
6953  0E              push cs
6954  57              push di
6955  E8 07 9E        call 0x75f
6958  B0 00           mov al, 0
695A  50              push ax
695B  B0 00           mov al, 0
695D  50              push ax
695E  B0 00           mov al, 0
6960  50              push ax
6961  E8 92 9C        call 0x5f6
6964  89 EC           mov sp, bp
6966  5D              pop bp
6967  CA 02 00        retf 2
; data (not reached as code), 6 bytes
696A                  pstr 'PAUSE'

; ---- routine 000E:6970  (found by: call)
sub_6970:
6970  55              push bp
6971  89 E5           mov bp, sp
6973  83 EC 10        sub sp, 0x10
6976  C4 3E 23 A9     les di, ptr [0xa923]
697A  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
697E  B1 03           mov cl, 3
6980  D3 E0           shl ax, cl
6982  C4 3E 2B A9     les di, ptr [0xa92b]
6986  03 F8           add di, ax
6988  81 C7 F8 FF     add di, 0xfff8
698C  89 7E F6        mov word ptr [bp - 0xa], di
698F  8C 46 F8        mov word ptr [bp - 8], es
6992  C4 3E 23 A9     les di, ptr [0xa923]
6996  89 7E F2        mov word ptr [bp - 0xe], di
6999  8C 46 F4        mov word ptr [bp - 0xc], es
699C  C4 7E F6        les di, ptr [bp - 0xa]
699F  26 80 3D FE     cmp byte ptr es:[di], 0xfe
69A3  74 04           je 0x69a9
69A5  B0 00           mov al, 0
69A7  EB 02           jmp 0x69ab
loc_69A9:
69A9  B0 01           mov al, 1
loc_69AB:
69AB  88 46 FE        mov byte ptr [bp - 2], al
69AE  C4 7E F2        les di, ptr [bp - 0xe]
69B1  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
69B5  B1 03           mov cl, 3
69B7  D3 E0           shl ax, cl
69B9  C4 3E 2B A9     les di, ptr [0xa92b]
69BD  03 F8           add di, ax
69BF  81 C7 F8 FF     add di, 0xfff8
69C3  06              push es
69C4  57              push di
69C5  9A 7E D4 91 07  call far 0791:D47E
69CA  C4 7E F2        les di, ptr [bp - 0xe]
69CD  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
69D1  B1 03           mov cl, 3
69D3  D3 E0           shl ax, cl
69D5  C4 3E 2B A9     les di, ptr [0xa92b]
69D9  03 F8           add di, ax
69DB  81 C7 F8 FF     add di, 0xfff8
69DF  06              push es
69E0  57              push di
69E1  9A FA B7 91 07  call far 0791:B7FA
69E6  C4 7E F2        les di, ptr [bp - 0xe]
69E9  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
69ED  B1 03           mov cl, 3
69EF  D3 E0           shl ax, cl
69F1  C4 3E 2B A9     les di, ptr [0xa92b]
69F5  03 F8           add di, ax
69F7  81 C7 F8 FF     add di, 0xfff8
69FB  06              push es
69FC  57              push di
69FD  9A 02 B6 91 07  call far 0791:B602
6A02  C4 7E F2        les di, ptr [bp - 0xe]
6A05  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6A09  B1 03           mov cl, 3
6A0B  D3 E0           shl ax, cl
6A0D  C4 3E 2B A9     les di, ptr [0xa92b]
6A11  03 F8           add di, ax
6A13  81 C7 F8 FF     add di, 0xfff8
6A17  06              push es
6A18  57              push di
6A19  9A 50 D0 91 07  call far 0791:D050
6A1E  C6 46 FF 00     mov byte ptr [bp - 1], 0
6A22  EB 03           jmp 0x6a27
loc_6A24:
6A24  FE 46 FF        inc byte ptr [bp - 1]
loc_6A27:
6A27  8A 46 FF        mov al, byte ptr [bp - 1]
6A2A  98              cwde
6A2B  D1 E0           shl ax, 1
6A2D  C4 7E F6        les di, ptr [bp - 0xa]
6A30  03 F8           add di, ax
6A32  26 FF 75 04     push word ptr es:[di + 4]
6A36  9A 5D BC 91 07  call far 0791:BC5D
6A3B  80 7E FF 01     cmp byte ptr [bp - 1], 1
6A3F  75 E3           jne 0x6a24
6A41  80 7E FE 00     cmp byte ptr [bp - 2], 0
6A45  74 63           je 0x6aaa
6A47  BF 6E A9        mov di, 0xa96e
6A4A  1E              push ds
6A4B  57              push di
6A4C  9A 12 07 91 07  call far 0791:0712
6A51  BF CC 25        mov di, 0x25cc
6A54  1E              push ds
6A55  57              push di
6A56  BF 6E A9        mov di, 0xa96e
6A59  1E              push ds
6A5A  57              push di
6A5B  9A 29 03 4B 21  call far 214B:0329
6A60  BF A6 14        mov di, 0x14a6
6A63  1E              push ds
6A64  57              push di
6A65  BF 6E A9        mov di, 0xa96e
6A68  1E              push ds
6A69  57              push di
6A6A  9A 29 03 4B 21  call far 214B:0329
6A6F  C4 3E 6E A9     les di, ptr [0xa96e]
6A73  06              push es
6A74  57              push di
6A75  C4 3E 6A A9     les di, ptr [0xa96a]
6A79  06              push es
6A7A  57              push di
6A7B  B8 A0 0F        mov ax, 0xfa0
6A7E  50              push ax
6A7F  9A 5D 02 E4 23  call far 23E4:025D
6A84  9A DD 08 4B 21  call far 214B:08DD
6A89  C4 7E F6        les di, ptr [bp - 0xa]
6A8C  26 FF 75 06     push word ptr es:[di + 6]
6A90  B0 00           mov al, 0
6A92  50              push ax
6A93  9A 29 E9 91 07  call far 0791:E929
6A98  C4 7E F2        les di, ptr [bp - 0xe]
6A9B  26 FF 45 26     inc word ptr es:[di + 0x26]
6A9F  8B 7E 04        mov di, word ptr [bp + 4]
6AA2  36 C6 45 FE 00  mov byte ptr ss:[di - 2], 0
6AA7  E9 71 01        jmp 0x6c1b
loc_6AAA:
6AAA  BF 0C 5C        mov di, 0x5c0c
6AAD  1E              push ds
6AAE  57              push di
6AAF  BF 6E A9        mov di, 0xa96e
6AB2  1E              push ds
6AB3  57              push di
6AB4  9A 29 03 4B 21  call far 214B:0329
6AB9  BF F2 26        mov di, 0x26f2
6ABC  1E              push ds
6ABD  57              push di
6ABE  BF 6E A9        mov di, 0xa96e
6AC1  1E              push ds
6AC2  57              push di
6AC3  9A 29 03 4B 21  call far 214B:0329
6AC8  9A F6 5B 71 17  call far 1771:5BF6
6ACD  BF 2A 14        mov di, 0x142a
6AD0  1E              push ds
6AD1  57              push di
6AD2  BF 6E A9        mov di, 0xa96e
6AD5  1E              push ds
6AD6  57              push di
6AD7  9A 29 03 4B 21  call far 214B:0329
6ADC  C7 46 FA 07 00  mov word ptr [bp - 6], 7
6AE1  C4 7E F2        les di, ptr [bp - 0xe]
6AE4  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6AE8  89 46 F0        mov word ptr [bp - 0x10], ax
6AEB  8B 7E 04        mov di, word ptr [bp + 4]
6AEE  36 8B 45 FA     mov ax, word ptr ss:[di - 6]
6AF2  31 D2           xor dx, dx
6AF4  52              push dx
6AF5  50              push ax
6AF6  C4 7E F2        les di, ptr [bp - 0xe]
6AF9  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6AFD  31 D2           xor dx, dx
6AFF  05 F1 FF        add ax, 0xfff1
6B02  83 D2 FF        adc dx, -1
6B05  52              push dx
6B06  50              push ax
6B07  9A 56 0D 4B 21  call far 214B:0D56
6B0C  3B 46 F0        cmp ax, word ptr [bp - 0x10]
6B0F  77 32           ja 0x6b43
6B11  89 46 FC        mov word ptr [bp - 4], ax
6B14  EB 03           jmp 0x6b19
loc_6B16:
6B16  FF 46 FC        inc word ptr [bp - 4]
loc_6B19:
6B19  FF 46 FA        inc word ptr [bp - 6]
6B1C  8B 46 FC        mov ax, word ptr [bp - 4]
6B1F  B1 03           mov cl, 3
6B21  D3 E0           shl ax, cl
6B23  C4 3E 2B A9     les di, ptr [0xa92b]
6B27  03 F8           add di, ax
6B29  81 C7 F8 FF     add di, 0xfff8
6B2D  06              push es
6B2E  57              push di
6B2F  FF 76 FA        push word ptr [bp - 6]
6B32  B8 21 00        mov ax, 0x21
6B35  50              push ax
6B36  9A 12 78 71 17  call far 1771:7812
6B3B  8B 46 FC        mov ax, word ptr [bp - 4]
6B3E  3B 46 F0        cmp ax, word ptr [bp - 0x10]
6B41  75 D3           jne 0x6b16
loc_6B43:
6B43  C4 3E 23 A9     les di, ptr [0xa923]
6B47  26 8A 45 3E     mov al, byte ptr es:[di + 0x3e]
6B4B  30 E4           xor ah, ah
6B4D  8B D0           mov dx, ax
6B4F  B8 05 00        mov ax, 5
6B52  2B C2           sub ax, dx
6B54  A2 AA 00        mov byte ptr [0xaa], al
6B57  B0 0E           mov al, 0xe
6B59  50              push ax
6B5A  BF AA 00        mov di, 0xaa
6B5D  1E              push ds
6B5E  57              push di
6B5F  B0 19           mov al, 0x19
6B61  50              push ax
6B62  B0 34           mov al, 0x34
6B64  50              push ax
6B65  BF 6E A9        mov di, 0xa96e
6B68  1E              push ds
6B69  57              push di
6B6A  9A C8 02 4B 21  call far 214B:02C8
6B6F  C4 3E 6E A9     les di, ptr [0xa96e]
6B73  06              push es
6B74  57              push di
6B75  C4 3E 6A A9     les di, ptr [0xa96a]
6B79  06              push es
6B7A  57              push di
6B7B  B8 A0 0F        mov ax, 0xfa0
6B7E  50              push ax
6B7F  9A 5D 02 E4 23  call far 23E4:025D
6B84  9A 23 07 4B 21  call far 214B:0723
6B89  08 C0           or al, al
6B8B  74 48           je 0x6bd5
6B8D  9A DD 08 4B 21  call far 214B:08DD
6B92  A0 76 A9        mov al, byte ptr [0xa976]
6B95  3C AE           cmp al, 0xae
6B97  75 15           jne 0x6bae
6B99  C4 3E 23 A9     les di, ptr [0xa923]
6B9D  26 80 7D 3E 05  cmp byte ptr es:[di + 0x3e], 5
6BA2  73 08           jae 0x6bac
6BA4  C4 3E 23 A9     les di, ptr [0xa923]
6BA8  26 FE 45 3E     inc byte ptr es:[di + 0x3e]
loc_6BAC:
6BAC  EB 27           jmp 0x6bd5
loc_6BAE:
6BAE  3C AF           cmp al, 0xaf
6BB0  75 15           jne 0x6bc7
6BB2  C4 3E 23 A9     les di, ptr [0xa923]
6BB6  26 80 7D 3E 00  cmp byte ptr es:[di + 0x3e], 0
6BBB  76 08           jbe 0x6bc5
6BBD  C4 3E 23 A9     les di, ptr [0xa923]
6BC1  26 FE 4D 3E     dec byte ptr es:[di + 0x3e]
loc_6BC5:
6BC5  EB 0E           jmp 0x6bd5
loc_6BC7:
6BC7  3C 20           cmp al, 0x20
6BC9  75 0A           jne 0x6bd5
6BCB  BF 6A 69        mov di, 0x696a
6BCE  0E              push cs
6BCF  57              push di
6BD0  9A F8 04 4B 21  call far 214B:04F8
loc_6BD5:
6BD5  C4 3E 23 A9     les di, ptr [0xa923]
6BD9  26 8A 45 3E     mov al, byte ptr es:[di + 0x3e]
6BDD  30 E4           xor ah, ah
6BDF  89 46 F0        mov word ptr [bp - 0x10], ax
6BE2  B8 01 00        mov ax, 1
6BE5  3B 46 F0        cmp ax, word ptr [bp - 0x10]
6BE8  77 22           ja 0x6c0c
6BEA  89 46 FC        mov word ptr [bp - 4], ax
6BED  EB 03           jmp 0x6bf2
loc_6BEF:
6BEF  FF 46 FC        inc word ptr [bp - 4]
loc_6BF2:
6BF2  9A 23 07 4B 21  call far 214B:0723
6BF7  08 C0           or al, al
6BF9  75 09           jne 0x6c04
6BFB  B8 32 00        mov ax, 0x32
6BFE  50              push ax
6BFF  9A 09 1E 4B 21  call far 214B:1E09
loc_6C04:
6C04  8B 46 FC        mov ax, word ptr [bp - 4]
6C07  3B 46 F0        cmp ax, word ptr [bp - 0x10]
6C0A  75 E3           jne 0x6bef
loc_6C0C:
6C0C  8B 7E 04        mov di, word ptr [bp + 4]
6C0F  36 C6 45 FE 01  mov byte ptr ss:[di - 2], 1
6C14  C4 7E F2        les di, ptr [bp - 0xe]
6C17  26 FF 45 26     inc word ptr es:[di + 0x26]
loc_6C1B:
6C1B  89 EC           mov sp, bp
6C1D  5D              pop bp
6C1E  C2 02 00        ret 2

