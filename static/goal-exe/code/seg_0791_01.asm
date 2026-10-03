; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 1 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 0791:0000  (found by: call)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  81 EC 00 01     sub sp, 0x100
0007  80 3E 2D 83 FF  cmp byte ptr [0x832d], 0xff
000C  73 5A           jae 0x68
000E  BF 10 5B        mov di, 0x5b10
0011  1E              push ds
0012  57              push di
0013  BF 6E A9        mov di, 0xa96e
0016  1E              push ds
0017  57              push di
0018  9A 29 03 4B 21  call far 214B:0329
001D  B0 07           mov al, 7
001F  50              push ax
0020  8D BE 00 FF     lea di, [bp - 0x100]
0024  16              push ss
0025  57              push di
0026  A0 2D 83        mov al, byte ptr [0x832d]
0029  30 E4           xor ah, ah
002B  31 D2           xor dx, dx
002D  52              push dx
002E  50              push ax
002F  9A DA 09 4B 21  call far 214B:09DA
0034  B0 06           mov al, 6
0036  50              push ax
0037  B0 0E           mov al, 0xe
0039  50              push ax
003A  BF 6E A9        mov di, 0xa96e
003D  1E              push ds
003E  57              push di
003F  9A 05 02 4B 21  call far 214B:0205
0044  8D BE 00 FF     lea di, [bp - 0x100]
0048  16              push ss
0049  57              push di
004A  A0 2C 83        mov al, byte ptr [0x832c]
004D  30 E4           xor ah, ah
004F  31 D2           xor dx, dx
0051  52              push dx
0052  50              push ax
0053  9A DA 09 4B 21  call far 214B:09DA
0058  B0 06           mov al, 6
005A  50              push ax
005B  B0 10           mov al, 0x10
005D  50              push ax
005E  BF 6E A9        mov di, 0xa96e
0061  1E              push ds
0062  57              push di
0063  9A 6D 02 4B 21  call far 214B:026D
loc_0068:
0068  89 EC           mov sp, bp
006A  5D              pop bp
006B  C3              ret

; ---- routine 0791:006C  (found by: call)
sub_006C:
006C  55              push bp
006D  89 E5           mov bp, sp
006F  83 EC 02        sub sp, 2
0072  C4 7E 08        les di, ptr [bp + 8]
0075  26 8B 45 02     mov ax, word ptr es:[di + 2]
0079  C4 7E 08        les di, ptr [bp + 8]
007C  26 03 05        add ax, word ptr es:[di]
007F  09 C0           or ax, ax
0081  75 02           jne 0x85
0083  EB 76           jmp 0xfb
loc_0085:
0085  C4 7E 08        les di, ptr [bp + 8]
0088  26 8B 45 02     mov ax, word ptr es:[di + 2]
008C  C4 7E 08        les di, ptr [bp + 8]
008F  26 03 05        add ax, word ptr es:[di]
0092  8B D8           mov bx, ax
0094  C4 7E 08        les di, ptr [bp + 8]
0097  26 8B 45 02     mov ax, word ptr es:[di + 2]
009B  B9 18 00        mov cx, 0x18
009E  F7 E1           mul cx
00A0  31 D2           xor dx, dx
00A2  F7 F3           div bx
00A4  89 46 FE        mov word ptr [bp - 2], ax
00A7  8B 46 06        mov ax, word ptr [bp + 6]
00AA  BA A0 00        mov dx, 0xa0
00AD  F7 E2           mul dx
00AF  C4 3E 6E A9     les di, ptr [0xa96e]
00B3  03 F8           add di, ax
00B5  81 C7 A4 FF     add di, 0xffa4
00B9  06              push es
00BA  57              push di
00BB  A0 2F 83        mov al, byte ptr [0x832f]
00BE  30 E4           xor ah, ah
00C0  50              push ax
00C1  FF 76 FE        push word ptr [bp - 2]
00C4  9A DB 00 4B 21  call far 214B:00DB
00C9  8B 46 FE        mov ax, word ptr [bp - 2]
00CC  05 23 00        add ax, 0x23
00CF  D1 E0           shl ax, 1
00D1  8B C8           mov cx, ax
00D3  8B 46 06        mov ax, word ptr [bp + 6]
00D6  BA A0 00        mov dx, 0xa0
00D9  F7 E2           mul dx
00DB  C4 3E 6E A9     les di, ptr [0xa96e]
00DF  03 F8           add di, ax
00E1  03 F9           add di, cx
00E3  81 C7 5E FF     add di, 0xff5e
00E7  06              push es
00E8  57              push di
00E9  A0 2E 83        mov al, byte ptr [0x832e]
00EC  30 E4           xor ah, ah
00EE  50              push ax
00EF  B8 18 00        mov ax, 0x18
00F2  2B 46 FE        sub ax, word ptr [bp - 2]
00F5  50              push ax
00F6  9A DB 00 4B 21  call far 214B:00DB
loc_00FB:
00FB  89 EC           mov sp, bp
00FD  5D              pop bp
00FE  C2 08 00        ret 8
; data (not reached as code), 5 bytes
0101                  db 01 50 02 6F 67   ; .P.og

; ---- routine 0791:0106  (found by: call)
sub_0106:
0106  55              push bp
0107  89 E5           mov bp, sp
0109  81 EC 08 01     sub sp, 0x108
010D  80 7E 06 00     cmp byte ptr [bp + 6], 0
0111  74 0A           je 0x11d
0113  BF 6E 27        mov di, 0x276e
0116  1E              push ds
0117  57              push di
0118  E8 7E A5        call 0xffffa699
011B  EB 08           jmp 0x125
loc_011D:
011D  BF A0 27        mov di, 0x27a0
0120  1E              push ds
0121  57              push di
0122  E8 74 A5        call 0xffffa699
loc_0125:
0125  BF 4A 41        mov di, 0x414a
0128  1E              push ds
0129  57              push di
012A  BF 6E A9        mov di, 0xa96e
012D  1E              push ds
012E  57              push di
012F  9A 29 03 4B 21  call far 214B:0329
0134  BF 6E A9        mov di, 0xa96e
0137  1E              push ds
0138  57              push di
0139  0E              push cs
013A  E8 D5 05        call 0x712
013D  80 3E 3F 9A 00  cmp byte ptr [0x9a3f], 0
0142  74 12           je 0x156
0144  BF 58 1B        mov di, 0x1b58
0147  1E              push ds
0148  57              push di
0149  BF 6E A9        mov di, 0xa96e
014C  1E              push ds
014D  57              push di
014E  9A 29 03 4B 21  call far 214B:0329
0153  E9 09 01        jmp 0x25f
loc_0156:
0156  E8 A7 FE        call 0
0159  83 3E 3A 7C 00  cmp word ptr [0x7c3a], 0
015E  74 76           je 0x1d6
0160  BF C8 14        mov di, 0x14c8
0163  1E              push ds
0164  57              push di
0165  BF 6E A9        mov di, 0xa96e
0168  1E              push ds
0169  57              push di
016A  9A 29 03 4B 21  call far 214B:0329
016F  FF 36 3A 7C     push word ptr [0x7c3a]
0173  A1 3A 7C        mov ax, word ptr [0x7c3a]
0176  BA 14 00        mov dx, 0x14
0179  F7 E2           mul dx
017B  C4 3E 1B A9     les di, ptr [0xa91b]
017F  03 F8           add di, ax
0181  26 8A 45 06     mov al, byte ptr es:[di + 6]
0185  30 E4           xor ah, ah
0187  50              push ax
0188  9A 20 2E 71 17  call far 1771:2E20
018D  50              push ax
018E  8D BE FC FE     lea di, [bp - 0x104]
0192  16              push ss
0193  57              push di
0194  A1 3A 7C        mov ax, word ptr [0x7c3a]
0197  C4 3E 70 9B     les di, ptr [0x9b70]
019B  03 F8           add di, ax
019D  26 8A 05        mov al, byte ptr es:[di]
01A0  50              push ax
01A1  9A 5A 07 E4 23  call far 23E4:075A
01A6  B0 16           mov al, 0x16
01A8  50              push ax
01A9  B0 2B           mov al, 0x2b
01AB  50              push ax
01AC  BF 6E A9        mov di, 0xa96e
01AF  1E              push ds
01B0  57              push di
01B1  9A C8 02 4B 21  call far 214B:02C8
01B6  A1 3A 7C        mov ax, word ptr [0x7c3a]
01B9  BA 0B 00        mov dx, 0xb
01BC  F7 E2           mul dx
01BE  C4 3E 6C 9B     les di, ptr [0x9b6c]
01C2  03 F8           add di, ax
01C4  06              push es
01C5  57              push di
01C6  B0 16           mov al, 0x16
01C8  50              push ax
01C9  B0 2D           mov al, 0x2d
01CB  50              push ax
01CC  BF 6E A9        mov di, 0xa96e
01CF  1E              push ds
01D0  57              push di
01D1  9A 6D 02 4B 21  call far 214B:026D
loc_01D6:
01D6  C6 46 FC 00     mov byte ptr [bp - 4], 0
01DA  EB 03           jmp 0x1df
loc_01DC:
01DC  FE 46 FC        inc byte ptr [bp - 4]
loc_01DF:
01DF  C6 46 FD 00     mov byte ptr [bp - 3], 0
01E3  EB 03           jmp 0x1e8
loc_01E5:
01E5  FE 46 FD        inc byte ptr [bp - 3]
loc_01E8:
01E8  8A 46 FD        mov al, byte ptr [bp - 3]
01EB  98              cwde
01EC  8B F8           mov di, ax
01EE  8A 85 74 06     mov al, byte ptr [di + 0x674]
01F2  50              push ax
01F3  8D BE FC FE     lea di, [bp - 0x104]
01F7  16              push ss
01F8  57              push di
01F9  8A 46 FD        mov al, byte ptr [bp - 3]
01FC  98              cwde
01FD  8B C8           mov cx, ax
01FF  8A 46 FC        mov al, byte ptr [bp - 4]
0202  98              cwde
0203  BA 0A 00        mov dx, 0xa
0206  F7 E2           mul dx
0208  8B F8           mov di, ax
020A  03 F9           add di, cx
020C  8A 85 7E 7B     mov al, byte ptr [di + 0x7b7e]
0210  30 E4           xor ah, ah
0212  31 D2           xor dx, dx
0214  52              push dx
0215  50              push ax
0216  9A DA 09 4B 21  call far 214B:09DA
021B  8A 46 FD        mov al, byte ptr [bp - 3]
021E  30 E4           xor ah, ah
0220  05 09 00        add ax, 9
0223  50              push ax
0224  8A 46 FC        mov al, byte ptr [bp - 4]
0227  98              cwde
0228  8B F8           mov di, ax
022A  8A 85 72 06     mov al, byte ptr [di + 0x672]
022E  50              push ax
022F  BF 6E A9        mov di, 0xa96e
0232  1E              push ds
0233  57              push di
0234  9A 05 02 4B 21  call far 214B:0205
0239  80 7E FD 08     cmp byte ptr [bp - 3], 8
023D  75 A6           jne 0x1e5
023F  80 7E FC 01     cmp byte ptr [bp - 4], 1
0243  75 97           jne 0x1dc
0245  BF F2 80        mov di, 0x80f2
0248  1E              push ds
0249  57              push di
024A  B8 13 00        mov ax, 0x13
024D  50              push ax
024E  55              push bp
024F  E8 1A FE        call 0x6c
0252  BF F6 80        mov di, 0x80f6
0255  1E              push ds
0256  57              push di
0257  B8 14 00        mov ax, 0x14
025A  50              push ax
025B  55              push bp
025C  E8 0D FE        call 0x6c
loc_025F:
025F  C6 46 FC 00     mov byte ptr [bp - 4], 0
0263  EB 03           jmp 0x268
loc_0265:
0265  FE 46 FC        inc byte ptr [bp - 4]
loc_0268:
0268  8A 46 FC        mov al, byte ptr [bp - 4]
026B  98              cwde
026C  8B F8           mov di, ax
026E  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
0272  50              push ax
0273  8A 46 FC        mov al, byte ptr [bp - 4]
0276  98              cwde
0277  8B F8           mov di, ax
0279  D1 E7           shl di, 1
027B  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
027F  B1 04           mov cl, 4
0281  D3 E0           shl ax, cl
0283  C4 3E 68 9B     les di, ptr [0x9b68]
0287  03 F8           add di, ax
0289  06              push es
028A  57              push di
028B  B0 07           mov al, 7
028D  50              push ax
028E  8A 46 FC        mov al, byte ptr [bp - 4]
0291  98              cwde
0292  8B F8           mov di, ax
0294  8A 85 6E 06     mov al, byte ptr [di + 0x66e]
0298  50              push ax
0299  BF 6E A9        mov di, 0xa96e
029C  1E              push ds
029D  57              push di
029E  9A C8 02 4B 21  call far 214B:02C8
02A3  C7 46 FE 01 00  mov word ptr [bp - 2], 1
02A8  EB 03           jmp 0x2ad
loc_02AA:
02AA  FF 46 FE        inc word ptr [bp - 2]
loc_02AD:
02AD  8B 46 FE        mov ax, word ptr [bp - 2]
02B0  BA 03 00        mov dx, 3
02B3  F7 E2           mul dx
02B5  8B C8           mov cx, ax
02B7  8A 46 FC        mov al, byte ptr [bp - 4]
02BA  98              cwde
02BB  BA 21 00        mov dx, 0x21
02BE  F7 E2           mul dx
02C0  8B F8           mov di, ax
02C2  03 F9           add di, cx
02C4  81 C7 D1 7B     add di, 0x7bd1
02C8  89 7E F8        mov word ptr [bp - 8], di
02CB  8C 5E FA        mov word ptr [bp - 6], ds
02CE  C4 7E F8        les di, ptr [bp - 8]
02D1  26 83 3D 00     cmp word ptr es:[di], 0
02D5  77 03           ja 0x2da
02D7  E9 0E 01        jmp 0x3e8
loc_02DA:
02DA  C4 7E F8        les di, ptr [bp - 8]
02DD  26 FF 35        push word ptr es:[di]
02E0  8B 46 FE        mov ax, word ptr [bp - 2]
02E3  05 0B 00        add ax, 0xb
02E6  50              push ax
02E7  8A 46 FC        mov al, byte ptr [bp - 4]
02EA  98              cwde
02EB  8B F8           mov di, ax
02ED  8A 85 70 06     mov al, byte ptr [di + 0x670]
02F1  30 E4           xor ah, ah
02F3  50              push ax
02F4  9A E5 2E 71 17  call far 1771:2EE5
02F9  C6 06 B2 AA 04  mov byte ptr [0xaab2], 4
02FE  C4 7E F8        les di, ptr [bp - 8]
0301  26 80 7D 02 80  cmp byte ptr es:[di + 2], 0x80
0306  77 3C           ja 0x344
0308  8D BE F8 FE     lea di, [bp - 0x108]
030C  16              push ss
030D  57              push di
030E  C4 7E F8        les di, ptr [bp - 8]
0311  26 8A 45 02     mov al, byte ptr es:[di + 2]
0315  30 E4           xor ah, ah
0317  31 D2           xor dx, dx
0319  52              push dx
031A  50              push ax
031B  9A DA 09 4B 21  call far 214B:09DA
0320  8B 46 FE        mov ax, word ptr [bp - 2]
0323  05 0B 00        add ax, 0xb
0326  50              push ax
0327  8A 46 FC        mov al, byte ptr [bp - 4]
032A  98              cwde
032B  8B F8           mov di, ax
032D  8A 85 70 06     mov al, byte ptr [di + 0x670]
0331  30 E4           xor ah, ah
0333  05 12 00        add ax, 0x12
0336  50              push ax
0337  BF 6E A9        mov di, 0xa96e
033A  1E              push ds
033B  57              push di
033C  9A A3 01 4B 21  call far 214B:01A3
0341  E9 A4 00        jmp 0x3e8
loc_0344:
0344  C4 7E F8        les di, ptr [bp - 8]
0347  26 FF 35        push word ptr es:[di]
034A  8A 46 FC        mov al, byte ptr [bp - 4]
034D  98              cwde
034E  8B F8           mov di, ax
0350  D1 E7           shl di, 1
0352  FF B5 34 9B     push word ptr [di - 0x64cc]
0356  9A 82 3A 71 17  call far 1771:3A82
035B  09 C0           or ax, ax
035D  74 28           je 0x387
035F  BF 01 01        mov di, 0x101
0362  0E              push cs
0363  57              push di
0364  8B 46 FE        mov ax, word ptr [bp - 2]
0367  05 0B 00        add ax, 0xb
036A  50              push ax
036B  8A 46 FC        mov al, byte ptr [bp - 4]
036E  98              cwde
036F  8B F8           mov di, ax
0371  8A 85 70 06     mov al, byte ptr [di + 0x670]
0375  30 E4           xor ah, ah
0377  05 0E 00        add ax, 0xe
037A  50              push ax
037B  BF 6E A9        mov di, 0xa96e
037E  1E              push ds
037F  57              push di
0380  9A 6D 02 4B 21  call far 214B:026D
0385  EB 26           jmp 0x3ad
loc_0387:
0387  BF 03 01        mov di, 0x103
038A  0E              push cs
038B  57              push di
038C  8B 46 FE        mov ax, word ptr [bp - 2]
038F  05 0B 00        add ax, 0xb
0392  50              push ax
0393  8A 46 FC        mov al, byte ptr [bp - 4]
0396  98              cwde
0397  8B F8           mov di, ax
0399  8A 85 70 06     mov al, byte ptr [di + 0x670]
039D  30 E4           xor ah, ah
039F  05 0D 00        add ax, 0xd
03A2  50              push ax
03A3  BF 6E A9        mov di, 0xa96e
03A6  1E              push ds
03A7  57              push di
03A8  9A 6D 02 4B 21  call far 214B:026D
loc_03AD:
03AD  8D BE F8 FE     lea di, [bp - 0x108]
03B1  16              push ss
03B2  57              push di
03B3  C4 7E F8        les di, ptr [bp - 8]
03B6  26 8A 45 02     mov al, byte ptr es:[di + 2]
03BA  30 E4           xor ah, ah
03BC  2D 80 00        sub ax, 0x80
03BF  99              cdq
03C0  52              push dx
03C1  50              push ax
03C2  9A DA 09 4B 21  call far 214B:09DA
03C7  8B 46 FE        mov ax, word ptr [bp - 2]
03CA  05 0B 00        add ax, 0xb
03CD  50              push ax
03CE  8A 46 FC        mov al, byte ptr [bp - 4]
03D1  98              cwde
03D2  8B F8           mov di, ax
03D4  8A 85 70 06     mov al, byte ptr [di + 0x670]
03D8  30 E4           xor ah, ah
03DA  05 12 00        add ax, 0x12
03DD  50              push ax
03DE  BF 6E A9        mov di, 0xa96e
03E1  1E              push ds
03E2  57              push di
03E3  9A A3 01 4B 21  call far 214B:01A3
loc_03E8:
03E8  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
03EC  74 03           je 0x3f1
03EE  E9 B9 FE        jmp 0x2aa
loc_03F1:
03F1  80 7E FC 01     cmp byte ptr [bp - 4], 1
03F5  74 03           je 0x3fa
03F7  E9 6B FE        jmp 0x265
loc_03FA:
03FA  C4 3E 6E A9     les di, ptr [0xa96e]
03FE  06              push es
03FF  57              push di
0400  C4 3E 6A A9     les di, ptr [0xa96a]
0404  06              push es
0405  57              push di
0406  B8 A0 0F        mov ax, 0xfa0
0409  50              push ax
040A  9A 5D 02 E4 23  call far 23E4:025D
040F  80 7E 06 00     cmp byte ptr [bp + 6], 0
0413  74 05           je 0x41a
0415  9A DD 08 4B 21  call far 214B:08DD
loc_041A:
041A  C6 06 76 A9 00  mov byte ptr [0xa976], 0
041F  89 EC           mov sp, bp
0421  5D              pop bp
0422  CA 02 00        retf 2

; ---- routine 0791:0425  (found by: call)
sub_0425:
0425  55              push bp
0426  89 E5           mov bp, sp
0428  C4 3E 23 A9     les di, ptr [0xa923]
042C  26 80 7D 3F 00  cmp byte ptr es:[di + 0x3f], 0
0431  76 08           jbe 0x43b
0433  FF 76 04        push word ptr [bp + 4]
0436  9A 09 1E 4B 21  call far 214B:1E09
loc_043B:
043B  89 EC           mov sp, bp
043D  5D              pop bp
043E  C2 02 00        ret 2

; ---- routine 0791:0441  (found by: call)
sub_0441:
0441  55              push bp
0442  89 E5           mov bp, sp
0444  C4 3E 23 A9     les di, ptr [0xa923]
0448  26 80 7D 3F 00  cmp byte ptr es:[di + 0x3f], 0
044D  76 08           jbe 0x457
044F  FF 76 04        push word ptr [bp + 4]
0452  9A 87 1F 4B 21  call far 214B:1F87
loc_0457:
0457  89 EC           mov sp, bp
0459  5D              pop bp
045A  C2 02 00        ret 2

; ---- routine 0791:045D  (found by: call)
sub_045D:
045D  55              push bp
045E  89 E5           mov bp, sp
0460  83 EC 02        sub sp, 2
0463  83 7E 04 01     cmp word ptr [bp + 4], 1
0467  74 0A           je 0x473
0469  83 7E 04 0C     cmp word ptr [bp + 4], 0xc
046D  74 04           je 0x473
046F  B0 00           mov al, 0
0471  EB 02           jmp 0x475
loc_0473:
0473  B0 01           mov al, 1
loc_0475:
0475  88 46 FF        mov byte ptr [bp - 1], al
0478  8A 46 FF        mov al, byte ptr [bp - 1]
047B  89 EC           mov sp, bp
047D  5D              pop bp
047E  C2 02 00        ret 2

; ---- routine 0791:0481  (found by: call)
sub_0481:
0481  55              push bp
0482  89 E5           mov bp, sp
0484  8B 7E 04        mov di, word ptr [bp + 4]
0487  36 8B 45 04     mov ax, word ptr ss:[di + 4]
048B  05 DC 00        add ax, 0xdc
048E  8B D0           mov dx, ax
0490  8B 46 06        mov ax, word ptr [bp + 6]
0493  D1 E0           shl ax, 1
0495  8B 7E 04        mov di, word ptr [bp + 4]
0498  36 C4 7D F6     les di, ptr ss:[di - 0xa]
049C  03 F8           add di, ax
049E  26 89 55 FE     mov word ptr es:[di - 2], dx
04A2  8B 7E 04        mov di, word ptr [bp + 4]
04A5  36 8B 45 04     mov ax, word ptr ss:[di + 4]
04A9  05 DB 00        add ax, 0xdb
04AC  8B D0           mov dx, ax
04AE  8B 46 06        mov ax, word ptr [bp + 6]
04B1  05 50 00        add ax, 0x50
04B4  D1 E0           shl ax, 1
04B6  8B 7E 04        mov di, word ptr [bp + 4]
04B9  36 C4 7D F6     les di, ptr ss:[di - 0xa]
04BD  03 F8           add di, ax
04BF  26 89 55 FE     mov word ptr es:[di - 2], dx
04C3  89 EC           mov sp, bp
04C5  5D              pop bp
04C6  C2 04 00        ret 4

; ---- routine 0791:04C9  (found by: call)
sub_04C9:
04C9  55              push bp
04CA  89 E5           mov bp, sp
04CC  83 EC 02        sub sp, 2
04CF  C7 46 FE 01 00  mov word ptr [bp - 2], 1
04D4  EB 03           jmp 0x4d9
loc_04D6:
04D6  FF 46 FE        inc word ptr [bp - 2]
loc_04D9:
04D9  8A 46 08        mov al, byte ptr [bp + 8]
04DC  30 E4           xor ah, ah
04DE  8B C8           mov cx, ax
04E0  8B 46 FE        mov ax, word ptr [bp - 2]
04E3  BA 0A 00        mov dx, 0xa
04E6  F7 E2           mul dx
04E8  8B F8           mov di, ax
04EA  03 F9           add di, cx
04EC  80 BD 44 06 00  cmp byte ptr [di + 0x644], 0
04F1  74 4D           je 0x540
04F3  83 7E FE 04     cmp word ptr [bp - 2], 4
04F7  73 34           jae 0x52d
04F9  8B 46 06        mov ax, word ptr [bp + 6]
04FC  8B 7E FE        mov di, word ptr [bp - 2]
04FF  D1 E7           shl di, 1
0501  03 85 C2 06     add ax, word ptr [di + 0x6c2]
0505  40              inc ax
0506  D1 E0           shl ax, 1
0508  8B 7E 04        mov di, word ptr [bp + 4]
050B  36 C4 7D F6     les di, ptr ss:[di - 0xa]
050F  03 F8           add di, ax
0511  81 C7 FE FF     add di, 0xfffe
0515  06              push es
0516  57              push di
0517  B8 04 00        mov ax, 4
051A  50              push ax
051B  8B 7E 04        mov di, word ptr [bp + 4]
051E  36 8B 45 04     mov ax, word ptr ss:[di + 4]
0522  05 DF 00        add ax, 0xdf
0525  50              push ax
0526  9A 00 00 4B 21  call far 214B:0000
052B  EB 13           jmp 0x540
loc_052D:
052D  8B 46 06        mov ax, word ptr [bp + 6]
0530  8B 7E FE        mov di, word ptr [bp - 2]
0533  D1 E7           shl di, 1
0535  03 85 C2 06     add ax, word ptr [di + 0x6c2]
0539  50              push ax
053A  FF 76 04        push word ptr [bp + 4]
053D  E8 41 FF        call 0x481
loc_0540:
0540  83 7E FE 07     cmp word ptr [bp - 2], 7
0544  75 90           jne 0x4d6
0546  89 EC           mov sp, bp
0548  5D              pop bp
0549  C2 06 00        ret 6

; ---- routine 0791:054C  (found by: call)
sub_054C:
054C  55              push bp
054D  89 E5           mov bp, sp
054F  81 EC 0C 01     sub sp, 0x10c
0553  C4 3E 6A A9     les di, ptr [0xa96a]
0557  89 F8           mov ax, di
0559  8C C2           mov dx, es
055B  89 46 F6        mov word ptr [bp - 0xa], ax
055E  89 56 F8        mov word ptr [bp - 8], dx
0561  8B 46 04        mov ax, word ptr [bp + 4]
0564  B9 08 00        mov cx, 8
0567  D3 E0           shl ax, cl
0569  89 46 04        mov word ptr [bp + 4], ax
056C  BF 3E 61        mov di, 0x613e
056F  1E              push ds
0570  57              push di
0571  BF 6A A9        mov di, 0xa96a
0574  1E              push ds
0575  57              push di
0576  9A 29 03 4B 21  call far 214B:0329
057B  8D BE F5 FE     lea di, [bp - 0x10b]
057F  16              push ss
0580  57              push di
0581  8B 46 06        mov ax, word ptr [bp + 6]
0584  31 D2           xor dx, dx
0586  52              push dx
0587  50              push ax
0588  9A DA 09 4B 21  call far 214B:09DA
058D  8D 7E FA        lea di, [bp - 6]
0590  16              push ss
0591  57              push di
0592  B8 05 00        mov ax, 5
0595  50              push ax
0596  9A 44 06 E4 23  call far 23E4:0644
059B  80 7E FA 02     cmp byte ptr [bp - 6], 2
059F  75 0C           jne 0x5ad
05A1  8A 46 FB        mov al, byte ptr [bp - 5]
05A4  50              push ax
05A5  B8 45 00        mov ax, 0x45
05A8  50              push ax
05A9  55              push bp
05AA  E8 1C FF        call 0x4c9
loc_05AD:
05AD  8A 46 FA        mov al, byte ptr [bp - 6]
05B0  30 E4           xor ah, ah
05B2  8B F8           mov di, ax
05B4  8A 43 FA        mov al, byte ptr [bp + di - 6]
05B7  50              push ax
05B8  B8 4B 00        mov ax, 0x4b
05BB  50              push ax
05BC  55              push bp
05BD  E8 09 FF        call 0x4c9
05C0  89 EC           mov sp, bp
05C2  5D              pop bp
05C3  C2 04 00        ret 4

; ---- routine 0791:05C6  (found by: call)
sub_05C6:
05C6  55              push bp
05C7  89 E5           mov bp, sp
05C9  83 EC 02        sub sp, 2
05CC  A0 6A 06        mov al, byte ptr [0x66a]
05CF  3C 00           cmp al, 0
05D1  75 07           jne 0x5da
05D3  C6 46 FF 01     mov byte ptr [bp - 1], 1
05D7  E9 AE 00        jmp 0x688
loc_05DA:
05DA  3C 01           cmp al, 1
05DC  75 2E           jne 0x60c
05DE  8B 7E 04        mov di, word ptr [bp + 4]
05E1  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
05E5  BA 16 00        mov dx, 0x16
05E8  F7 E2           mul dx
05EA  8B F8           mov di, ax
05EC  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
05F0  BA 14 00        mov dx, 0x14
05F3  F7 E2           mul dx
05F5  C4 3E 1B A9     les di, ptr [0xa91b]
05F9  03 F8           add di, ax
05FB  26 8A 45 06     mov al, byte ptr es:[di + 6]
05FF  30 E4           xor ah, ah
0601  8B F8           mov di, ax
0603  8A 85 A8 69     mov al, byte ptr [di + 0x69a8]
0607  88 46 FF        mov byte ptr [bp - 1], al
060A  EB 7C           jmp 0x688
loc_060C:
060C  3C 02           cmp al, 2
060E  75 3E           jne 0x64e
0610  A0 19 83        mov al, byte ptr [0x8319]
0613  98              cwde
0614  99              cdq
0615  8B C8           mov cx, ax
0617  8B DA           mov bx, dx
0619  A1 1B 83        mov ax, word ptr [0x831b]
061C  31 D2           xor dx, dx
061E  3B D3           cmp dx, bx
0620  7F 0A           jg 0x62c
0622  7C 04           jl 0x628
0624  3B C1           cmp ax, cx
0626  77 04           ja 0x62c
loc_0628:
0628  B0 00           mov al, 0
062A  EB 02           jmp 0x62e
loc_062C:
062C  B0 01           mov al, 1
loc_062E:
062E  8A D0           mov dl, al
0630  8B 7E 04        mov di, word ptr [bp + 4]
0633  36 83 7D FE 0C  cmp word ptr ss:[di - 2], 0xc
0638  72 04           jb 0x63e
063A  B0 00           mov al, 0
063C  EB 02           jmp 0x640
loc_063E:
063E  B0 01           mov al, 1
loc_0640:
0640  32 C2           xor al, dl
0642  98              cwde
0643  8B F8           mov di, ax
0645  8A 85 D4 06     mov al, byte ptr [di + 0x6d4]
0649  88 46 FF        mov byte ptr [bp - 1], al
064C  EB 3A           jmp 0x688
loc_064E:
064E  3C 03           cmp al, 3
0650  75 1C           jne 0x66e
0652  8B 7E 04        mov di, word ptr [bp + 4]
0655  36 83 7D FE 0C  cmp word ptr ss:[di - 2], 0xc
065A  72 04           jb 0x660
065C  B0 00           mov al, 0
065E  EB 02           jmp 0x662
loc_0660:
0660  B0 01           mov al, 1
loc_0662:
0662  98              cwde
0663  8B F8           mov di, ax
0665  8A 85 D2 06     mov al, byte ptr [di + 0x6d2]
0669  88 46 FF        mov byte ptr [bp - 1], al
066C  EB 1A           jmp 0x688
loc_066E:
066E  3C 04           cmp al, 4
0670  75 16           jne 0x688
0672  8B 7E 04        mov di, word ptr [bp + 4]
0675  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
0679  48              dec ax
067A  31 D2           xor dx, dx
067C  B9 0B 00        mov cx, 0xb
067F  F7 F1           div cx
0681  92              xchg dx, ax
0682  05 2F 00        add ax, 0x2f
0685  88 46 FF        mov byte ptr [bp - 1], al
loc_0688:
0688  8A 46 FF        mov al, byte ptr [bp - 1]
068B  89 EC           mov sp, bp
068D  5D              pop bp
068E  C2 02 00        ret 2

; ---- routine 0791:0691  (found by: call)
sub_0691:
0691  55              push bp
0692  89 E5           mov bp, sp
0694  83 EC 06        sub sp, 6
0697  C7 46 FE 01 00  mov word ptr [bp - 2], 1
069C  EB 03           jmp 0x6a1
loc_069E:
069E  FF 46 FE        inc word ptr [bp - 2]
loc_06A1:
06A1  8B 46 FE        mov ax, word ptr [bp - 2]
06A4  BA 16 00        mov dx, 0x16
06A7  F7 E2           mul dx
06A9  8B F8           mov di, ax
06AB  81 C7 E8 80     add di, 0x80e8
06AF  89 7E FA        mov word ptr [bp - 6], di
06B2  8C 5E FC        mov word ptr [bp - 4], ds
06B5  FF 76 FE        push word ptr [bp - 2]
06B8  E8 A2 FD        call 0x45d
06BB  08 C0           or al, al
06BD  74 21           je 0x6e0
06BF  C4 7E FA        les di, ptr [bp - 6]
06C2  06              push es
06C3  57              push di
06C4  0E              push cs
06C5  E8 AC 22        call 0x2974
06C8  98              cwde
06C9  8B F8           mov di, ax
06CB  8A 85 30 83     mov al, byte ptr [di - 0x7cd0]
06CF  30 E4           xor ah, ah
06D1  B9 08 00        mov cx, 8
06D4  D3 E0           shl ax, cl
06D6  40              inc ax
06D7  C4 7E FA        les di, ptr [bp - 6]
06DA  26 89 45 04     mov word ptr es:[di + 4], ax
06DE  EB 28           jmp 0x708
loc_06E0:
06E0  55              push bp
06E1  E8 E2 FE        call 0x5c6
06E4  30 E4           xor ah, ah
06E6  50              push ax
06E7  C4 7E FA        les di, ptr [bp - 6]
06EA  06              push es
06EB  57              push di
06EC  0E              push cs
06ED  E8 84 22        call 0x2974
06F0  98              cwde
06F1  8B F8           mov di, ax
06F3  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
06F7  30 E4           xor ah, ah
06F9  B9 08 00        mov cx, 8
06FC  D3 E0           shl ax, cl
06FE  5A              pop dx
06FF  03 C2           add ax, dx
0701  C4 7E FA        les di, ptr [bp - 6]
0704  26 89 45 04     mov word ptr es:[di + 4], ax
loc_0708:
0708  83 7E FE 16     cmp word ptr [bp - 2], 0x16
070C  75 90           jne 0x69e
070E  89 EC           mov sp, bp
0710  5D              pop bp
0711  C3              ret

; ---- routine 0791:0712  (found by: call, far)
sub_0712:
0712  55              push bp
0713  89 E5           mov bp, sp
0715  81 EC 04 01     sub sp, 0x104
0719  C4 7E 06        les di, ptr [bp + 6]
071C  89 7E FC        mov word ptr [bp - 4], di
071F  8C 46 FE        mov word ptr [bp - 2], es
0722  B0 70           mov al, 0x70
0724  50              push ax
0725  8D BE FC FE     lea di, [bp - 0x104]
0729  16              push ss
072A  57              push di
072B  A0 3D 9B        mov al, byte ptr [0x9b3d]
072E  30 E4           xor ah, ah
0730  31 D2           xor dx, dx
0732  52              push dx
0733  50              push ax
0734  9A DA 09 4B 21  call far 214B:09DA
0739  B0 02           mov al, 2
073B  50              push ax
073C  B0 1F           mov al, 0x1f
073E  50              push ax
073F  C4 7E FC        les di, ptr [bp - 4]
0742  06              push es
0743  57              push di
0744  9A 05 02 4B 21  call far 214B:0205
0749  B0 70           mov al, 0x70
074B  50              push ax
074C  8D BE FC FE     lea di, [bp - 0x104]
0750  16              push ss
0751  57              push di
0752  A0 3C 9B        mov al, byte ptr [0x9b3c]
0755  30 E4           xor ah, ah
0757  31 D2           xor dx, dx
0759  52              push dx
075A  50              push ax
075B  9A DA 09 4B 21  call far 214B:09DA
0760  B0 04           mov al, 4
0762  50              push ax
0763  B0 1F           mov al, 0x1f
0765  50              push ax
0766  C4 7E FC        les di, ptr [bp - 4]
0769  06              push es
076A  57              push di
076B  9A 05 02 4B 21  call far 214B:0205
0770  89 EC           mov sp, bp
0772  5D              pop bp
0773  CA 04 00        retf 4

; ---- routine 0791:0776  (found by: call)
sub_0776:
0776  55              push bp
0777  89 E5           mov bp, sp
0779  8B 7E 04        mov di, word ptr [bp + 4]
077C  36 80 7D 04 00  cmp byte ptr ss:[di + 4], 0
0781  74 0F           je 0x792
0783  C4 7E 08        les di, ptr [bp + 8]
0786  06              push es
0787  57              push di
0788  FF 76 06        push word ptr [bp + 6]
078B  9A 47 1B 4B 21  call far 214B:1B47
0790  EB 1E           jmp 0x7b0
loc_0792:
0792  8B 7E 04        mov di, word ptr [bp + 4]
0795  36 80 7D FE 00  cmp byte ptr ss:[di - 2], 0
079A  74 14           je 0x7b0
079C  C4 7E 08        les di, ptr [bp + 8]
079F  06              push es
07A0  57              push di
07A1  FF 76 06        push word ptr [bp + 6]
07A4  9A D1 1A 4B 21  call far 214B:1AD1
07A9  8B 7E 04        mov di, word ptr [bp + 4]
07AC  36 88 45 FE     mov byte ptr ss:[di - 2], al
loc_07B0:
07B0  89 EC           mov sp, bp
07B2  5D              pop bp
07B3  C2 08 00        ret 8
; data (not reached as code), 4 bytes
07B6                  pstr '...'

; ---- routine 0791:07BA  (found by: call)
sub_07BA:
07BA  55              push bp
07BB  89 E5           mov bp, sp
07BD  81 EC 04 01     sub sp, 0x104
07C1  C6 46 FF 01     mov byte ptr [bp - 1], 1
07C5  C6 46 FE 01     mov byte ptr [bp - 2], 1
07C9  B0 19           mov al, 0x19
07CB  50              push ax
07CC  8D BE FC FE     lea di, [bp - 0x104]
07D0  16              push ss
07D1  57              push di
07D2  8A 46 04        mov al, byte ptr [bp + 4]
07D5  98              cwde
07D6  BA 0B 00        mov dx, 0xb
07D9  F7 E2           mul dx
07DB  8B F8           mov di, ax
07DD  81 C7 22 0C     add di, 0xc22
07E1  1E              push ds
07E2  57              push di
07E3  9A 2A 06 E4 23  call far 23E4:062A
07E8  BF B6 07        mov di, 0x7b6
07EB  0E              push cs
07EC  57              push di
07ED  9A B7 06 E4 23  call far 23E4:06B7
07F2  BF 6A A9        mov di, 0xa96a
07F5  1E              push ds
07F6  57              push di
07F7  9A 50 03 4B 21  call far 214B:0350
07FC  80 7E 04 00     cmp byte ptr [bp + 4], 0
0800  75 05           jne 0x807
0802  C6 06 A0 99 FE  mov byte ptr [0x99a0], 0xfe
loc_0807:
0807  BF A0 99        mov di, 0x99a0
080A  1E              push ds
080B  57              push di
080C  B8 01 00        mov ax, 1
080F  50              push ax
0810  55              push bp
0811  E8 62 FF        call 0x776
0814  80 3E A0 99 FE  cmp byte ptr [0x99a0], 0xfe
0819  74 0D           je 0x828
081B  C6 46 FF 00     mov byte ptr [bp - 1], 0
081F  C7 06 65 A9 FE 00 mov word ptr [0xa965], 0xfe
0825  E9 24 01        jmp 0x94c
loc_0828:
0828  BF 6D 06        mov di, 0x66d
082B  1E              push ds
082C  57              push di
082D  B8 01 00        mov ax, 1
0830  50              push ax
0831  55              push bp
0832  E8 41 FF        call 0x776
0835  BF 3A 7C        mov di, 0x7c3a
0838  1E              push ds
0839  57              push di
083A  B8 02 00        mov ax, 2
083D  50              push ax
083E  55              push bp
083F  E8 34 FF        call 0x776
0842  BF 39 84        mov di, 0x8439
0845  1E              push ds
0846  57              push di
0847  B8 FB 07        mov ax, 0x7fb
084A  50              push ax
084B  55              push bp
084C  E8 27 FF        call 0x776
084F  BF 34 8C        mov di, 0x8c34
0852  1E              push ds
0853  57              push di
0854  B8 7E 01        mov ax, 0x17e
0857  50              push ax
0858  55              push bp
0859  E8 1A FF        call 0x776
085C  BF 30 8F        mov di, 0x8f30
085F  1E              push ds
0860  57              push di
0861  B8 20 03        mov ax, 0x320
0864  50              push ax
0865  55              push bp
0866  E8 0D FF        call 0x776
0869  BF 70 95        mov di, 0x9570
086C  1E              push ds
086D  57              push di
086E  B8 B8 01        mov ax, 0x1b8
0871  50              push ax
0872  55              push bp
0873  E8 00 FF        call 0x776
0876  BF E0 98        mov di, 0x98e0
0879  1E              push ds
087A  57              push di
087B  B8 28 00        mov ax, 0x28
087E  50              push ax
087F  55              push bp
0880  E8 F3 FE        call 0x776
0883  BF 30 99        mov di, 0x9930
0886  1E              push ds
0887  57              push di
0888  B8 06 00        mov ax, 6
088B  50              push ax
088C  55              push bp
088D  E8 E6 FE        call 0x776
0890  BF 6A 7B        mov di, 0x7b6a
0893  1E              push ds
0894  57              push di
0895  B8 14 00        mov ax, 0x14
0898  50              push ax
0899  55              push bp
089A  E8 D9 FE        call 0x776
089D  BF 92 7B        mov di, 0x7b92
08A0  1E              push ds
08A1  57              push di
08A2  B8 42 00        mov ax, 0x42
08A5  50              push ax
08A6  55              push bp
08A7  E8 CC FE        call 0x776
08AA  BF 2E 7C        mov di, 0x7c2e
08AD  1E              push ds
08AE  57              push di
08AF  B8 08 00        mov ax, 8
08B2  50              push ax
08B3  55              push bp
08B4  E8 BF FE        call 0x776
08B7  BF 3C 9A        mov di, 0x9a3c
08BA  1E              push ds
08BB  57              push di
08BC  B8 01 00        mov ax, 1
08BF  50              push ax
08C0  55              push bp
08C1  E8 B2 FE        call 0x776
08C4  BF 90 9A        mov di, 0x9a90
08C7  1E              push ds
08C8  57              push di
08C9  B8 50 00        mov ax, 0x50
08CC  50              push ax
08CD  55              push bp
08CE  E8 A5 FE        call 0x776
08D1  BF E0 9A        mov di, 0x9ae0
08D4  1E              push ds
08D5  57              push di
08D6  B8 28 00        mov ax, 0x28
08D9  50              push ax
08DA  55              push bp
08DB  E8 98 FE        call 0x776
08DE  BF 30 9B        mov di, 0x9b30
08E1  1E              push ds
08E2  57              push di
08E3  B8 04 00        mov ax, 4
08E6  50              push ax
08E7  55              push bp
08E8  E8 8B FE        call 0x776
08EB  BF 38 9B        mov di, 0x9b38
08EE  1E              push ds
08EF  57              push di
08F0  B8 02 00        mov ax, 2
08F3  50              push ax
08F4  55              push bp
08F5  E8 7E FE        call 0x776
08F8  BF 3E 9B        mov di, 0x9b3e
08FB  1E              push ds
08FC  57              push di
08FD  B8 02 00        mov ax, 2
0900  50              push ax
0901  55              push bp
0902  E8 71 FE        call 0x776
0905  BF 42 9B        mov di, 0x9b42
0908  1E              push ds
0909  57              push di
090A  B8 01 00        mov ax, 1
090D  50              push ax
090E  55              push bp
090F  E8 64 FE        call 0x776
0912  BF 74 99        mov di, 0x9974
0915  1E              push ds
0916  57              push di
0917  B8 02 00        mov ax, 2
091A  50              push ax
091B  55              push bp
091C  E8 57 FE        call 0x776
091F  BF 8C 99        mov di, 0x998c
0922  1E              push ds
0923  57              push di
0924  B8 14 00        mov ax, 0x14
0927  50              push ax
0928  55              push bp
0929  E8 4A FE        call 0x776
092C  BF 3C 99        mov di, 0x993c
092F  1E              push ds
0930  57              push di
0931  B8 1A 00        mov ax, 0x1a
0934  50              push ax
0935  55              push bp
0936  E8 3D FE        call 0x776
0939  BF 70 99        mov di, 0x9970
093C  1E              push ds
093D  57              push di
093E  B8 02 00        mov ax, 2
0941  50              push ax
0942  55              push bp
0943  E8 30 FE        call 0x776
0946  8A 46 FE        mov al, byte ptr [bp - 2]
0949  88 46 FF        mov byte ptr [bp - 1], al
loc_094C:
094C  8A 46 FF        mov al, byte ptr [bp - 1]
094F  89 EC           mov sp, bp
0951  5D              pop bp
0952  C2 02 00        ret 2

