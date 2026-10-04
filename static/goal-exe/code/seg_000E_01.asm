; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 1 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 000E:0000  (found by: call)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  83 EC 10        sub sp, 0x10
0006  C4 3E 23 A9     les di, ptr [0xa923]
000A  89 7E F4        mov word ptr [bp - 0xc], di
000D  8C 46 F6        mov word ptr [bp - 0xa], es
0010  C7 46 F8 01 00  mov word ptr [bp - 8], 1
0015  C4 7E F4        les di, ptr [bp - 0xc]
0018  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
001C  89 46 FA        mov word ptr [bp - 6], ax
loc_001F:
001F  C4 7E F4        les di, ptr [bp - 0xc]
0022  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
0027  74 1E           je 0x47
0029  C4 7E F4        les di, ptr [bp - 0xc]
002C  26 83 7D 38 00  cmp word ptr es:[di + 0x38], 0
0031  75 14           jne 0x47
0033  8B 46 FA        mov ax, word ptr [bp - 6]
0036  3B 06 38 69     cmp ax, word ptr [0x6938]
003A  73 0B           jae 0x47
003C  C7 46 F8 01 00  mov word ptr [bp - 8], 1
0041  A1 38 69        mov ax, word ptr [0x6938]
0044  89 46 FA        mov word ptr [bp - 6], ax
loc_0047:
0047  C7 46 FE 08 00  mov word ptr [bp - 2], 8
004C  BF AC 20        mov di, 0x20ac
004F  1E              push ds
0050  57              push di
0051  BF 6E A9        mov di, 0xa96e
0054  1E              push ds
0055  57              push di
0056  9A 29 03 4B 21  call far 214B:0329
005B  BF F2 26        mov di, 0x26f2
005E  1E              push ds
005F  57              push di
0060  BF 6E A9        mov di, 0xa96e
0063  1E              push ds
0064  57              push di
0065  9A 29 03 4B 21  call far 214B:0329
006A  BF F6 1A        mov di, 0x1af6
006D  1E              push ds
006E  57              push di
006F  BF 6E A9        mov di, 0xa96e
0072  1E              push ds
0073  57              push di
0074  9A 29 03 4B 21  call far 214B:0329
0079  8B 46 FA        mov ax, word ptr [bp - 6]
007C  03 46 F8        add ax, word ptr [bp - 8]
007F  48              dec ax
0080  B1 03           mov cl, 3
0082  D3 E0           shl ax, cl
0084  C4 3E 2B A9     les di, ptr [0xa92b]
0088  03 F8           add di, ax
008A  81 C7 F8 FF     add di, 0xfff8
008E  89 7E F0        mov word ptr [bp - 0x10], di
0091  8C 46 F2        mov word ptr [bp - 0xe], es
0094  C4 7E F0        les di, ptr [bp - 0x10]
0097  26 FF 75 06     push word ptr es:[di + 6]
009B  9A 77 0B 71 17  call far 1771:0B77
00A0  08 C0           or al, al
00A2  75 42           jne 0xe6
00A4  C4 7E F0        les di, ptr [bp - 0x10]
00A7  26 FF 75 04     push word ptr es:[di + 4]
00AB  9A 77 0B 71 17  call far 1771:0B77
00B0  08 C0           or al, al
00B2  75 32           jne 0xe6
00B4  C4 7E F0        les di, ptr [bp - 0x10]
00B7  26 80 3D FE     cmp byte ptr es:[di], 0xfe
00BB  75 11           jne 0xce
00BD  BF 7E 20        mov di, 0x207e
00C0  1E              push ds
00C1  57              push di
00C2  BF 6E A9        mov di, 0xa96e
00C5  1E              push ds
00C6  57              push di
00C7  9A 29 03 4B 21  call far 214B:0329
00CC  EB 18           jmp 0xe6
loc_00CE:
00CE  C4 7E F0        les di, ptr [bp - 0x10]
00D1  26 80 3D FF     cmp byte ptr es:[di], 0xff
00D5  75 0F           jne 0xe6
00D7  BF 50 20        mov di, 0x2050
00DA  1E              push ds
00DB  57              push di
00DC  BF 6E A9        mov di, 0xa96e
00DF  1E              push ds
00E0  57              push di
00E1  9A 29 03 4B 21  call far 214B:0329
loc_00E6:
00E6  C4 7E F4        les di, ptr [bp - 0xc]
00E9  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
00ED  48              dec ax
00EE  31 D2           xor dx, dx
00F0  52              push dx
00F1  50              push ax
00F2  8B 46 FA        mov ax, word ptr [bp - 6]
00F5  05 0F 00        add ax, 0xf
00F8  31 D2           xor dx, dx
00FA  52              push dx
00FB  50              push ax
00FC  9A 1C 0D 4B 21  call far 214B:0D1C
0101  89 46 F2        mov word ptr [bp - 0xe], ax
0104  8B 46 FA        mov ax, word ptr [bp - 6]
0107  3B 46 F2        cmp ax, word ptr [bp - 0xe]
010A  77 32           ja 0x13e
010C  89 46 FC        mov word ptr [bp - 4], ax
010F  EB 03           jmp 0x114
loc_0111:
0111  FF 46 FC        inc word ptr [bp - 4]
loc_0114:
0114  8B 46 FC        mov ax, word ptr [bp - 4]
0117  B1 03           mov cl, 3
0119  D3 E0           shl ax, cl
011B  C4 3E 2B A9     les di, ptr [0xa92b]
011F  03 F8           add di, ax
0121  81 C7 F8 FF     add di, 0xfff8
0125  06              push es
0126  57              push di
0127  FF 76 FE        push word ptr [bp - 2]
012A  B8 21 00        mov ax, 0x21
012D  50              push ax
012E  9A 12 78 71 17  call far 1771:7812
0133  FF 46 FE        inc word ptr [bp - 2]
0136  8B 46 FC        mov ax, word ptr [bp - 4]
0139  3B 46 F2        cmp ax, word ptr [bp - 0xe]
013C  75 D3           jne 0x111
loc_013E:
013E  8B 46 F8        mov ax, word ptr [bp - 8]
0141  05 07 00        add ax, 7
0144  50              push ax
0145  B8 0E 00        mov ax, 0xe
0148  50              push ax
0149  B8 35 00        mov ax, 0x35
014C  50              push ax
014D  9A C5 13 4B 21  call far 214B:13C5
0152  C4 3E 6E A9     les di, ptr [0xa96e]
0156  06              push es
0157  57              push di
0158  C4 3E 6A A9     les di, ptr [0xa96a]
015C  06              push es
015D  57              push di
015E  B8 A0 0F        mov ax, 0xfa0
0161  50              push ax
0162  9A 5D 02 E4 23  call far 23E4:025D
0167  9A DD 08 4B 21  call far 214B:08DD
016C  8D 7E F8        lea di, [bp - 8]
016F  16              push ss
0170  57              push di
0171  8D 7E FA        lea di, [bp - 6]
0174  16              push ss
0175  57              push di
0176  B8 10 00        mov ax, 0x10
0179  50              push ax
017A  C4 7E F4        les di, ptr [bp - 0xc]
017D  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
0181  48              dec ax
0182  50              push ax
0183  9A B1 15 4B 21  call far 214B:15B1
0188  8B 46 FA        mov ax, word ptr [bp - 6]
018B  03 46 F8        add ax, word ptr [bp - 8]
018E  48              dec ax
018F  B1 03           mov cl, 3
0191  D3 E0           shl ax, cl
0193  C4 3E 2B A9     les di, ptr [0xa92b]
0197  03 F8           add di, ax
0199  81 C7 F8 FF     add di, 0xfff8
019D  89 7E F0        mov word ptr [bp - 0x10], di
01A0  8C 46 F2        mov word ptr [bp - 0xe], es
01A3  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
01A8  75 42           jne 0x1ec
01AA  C4 7E F0        les di, ptr [bp - 0x10]
01AD  26 80 3D FE     cmp byte ptr es:[di], 0xfe
01B1  72 39           jb 0x1ec
01B3  C4 7E F0        les di, ptr [bp - 0x10]
01B6  26 FF 75 06     push word ptr es:[di + 6]
01BA  9A 77 0B 71 17  call far 1771:0B77
01BF  08 C0           or al, al
01C1  75 29           jne 0x1ec
01C3  C4 7E F0        les di, ptr [bp - 0x10]
01C6  26 FF 75 04     push word ptr es:[di + 4]
01CA  9A 77 0B 71 17  call far 1771:0B77
01CF  08 C0           or al, al
01D1  75 19           jne 0x1ec
01D3  C4 7E F0        les di, ptr [bp - 0x10]
01D6  26 80 3D FE     cmp byte ptr es:[di], 0xfe
01DA  75 09           jne 0x1e5
01DC  C4 7E F0        les di, ptr [bp - 0x10]
01DF  26 C6 05 FF     mov byte ptr es:[di], 0xff
01E3  EB 07           jmp 0x1ec
loc_01E5:
01E5  C4 7E F0        les di, ptr [bp - 0x10]
01E8  26 C6 05 FE     mov byte ptr es:[di], 0xfe
loc_01EC:
01EC  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
01F1  74 03           je 0x1f6
01F3  E9 29 FE        jmp 0x1f
loc_01F6:
01F6  89 EC           mov sp, bp
01F8  5D              pop bp
01F9  C3              ret

; ---- routine 000E:01FA  (found by: call)
sub_01FA:
01FA  55              push bp
01FB  89 E5           mov bp, sp
01FD  83 EC 14        sub sp, 0x14
0200  C4 3E 23 A9     les di, ptr [0xa923]
0204  89 7E F8        mov word ptr [bp - 8], di
0207  8C 46 FA        mov word ptr [bp - 6], es
020A  8B 46 04        mov ax, word ptr [bp + 4]
020D  05 80 00        add ax, 0x80
0210  BA 03 00        mov dx, 3
0213  F7 E2           mul dx
0215  C4 3E 1F A9     les di, ptr [0xa91f]
0219  03 F8           add di, ax
021B  89 7E F4        mov word ptr [bp - 0xc], di
021E  8C 46 F6        mov word ptr [bp - 0xa], es
0221  8B 46 04        mov ax, word ptr [bp + 4]
0224  C4 7E F8        les di, ptr [bp - 8]
0227  03 F8           add di, ax
0229  26 C6 45 47 01  mov byte ptr es:[di + 0x47], 1
022E  C4 7E F4        les di, ptr [bp - 0xc]
0231  26 C6 45 01 01  mov byte ptr es:[di + 1], 1
0236  C4 7E F4        les di, ptr [bp - 0xc]
0239  26 8A 05        mov al, byte ptr es:[di]
023C  30 E4           xor ah, ah
023E  50              push ax
023F  9A 5D BC 91 07  call far 0791:BC5D
0244  C7 46 FC 0C 00  mov word ptr [bp - 4], 0xc
0249  EB 03           jmp 0x24e
loc_024B:
024B  FF 46 FC        inc word ptr [bp - 4]
loc_024E:
024E  C4 7E F4        les di, ptr [bp - 0xc]
0251  26 8A 05        mov al, byte ptr es:[di]
0254  30 E4           xor ah, ah
0256  BA BF 00        mov dx, 0xbf
0259  F7 E2           mul dx
025B  C4 3E 17 A9     les di, ptr [0xa917]
025F  03 F8           add di, ax
0261  89 7E F0        mov word ptr [bp - 0x10], di
0264  8C 46 F2        mov word ptr [bp - 0xe], es
0267  8B 46 FC        mov ax, word ptr [bp - 4]
026A  D1 E0           shl ax, 1
026C  C4 7E F0        les di, ptr [bp - 0x10]
026F  03 F8           add di, ax
0271  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0275  BA 14 00        mov dx, 0x14
0278  F7 E2           mul dx
027A  C4 3E 1B A9     les di, ptr [0xa91b]
027E  03 F8           add di, ax
0280  89 7E EC        mov word ptr [bp - 0x14], di
0283  8C 46 EE        mov word ptr [bp - 0x12], es
0286  C4 7E EC        les di, ptr [bp - 0x14]
0289  26 8A 45 07     mov al, byte ptr es:[di + 7]
028D  C4 7E EC        les di, ptr [bp - 0x14]
0290  26 88 45 06     mov byte ptr es:[di + 6], al
0294  83 7E FC 14     cmp word ptr [bp - 4], 0x14
0298  75 B1           jne 0x24b
029A  8B 7E 04        mov di, word ptr [bp + 4]
029D  D1 E7           shl di, 1
029F  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
02A3  05 4F 00        add ax, 0x4f
02A6  89 46 F2        mov word ptr [bp - 0xe], ax
02A9  8B 7E 04        mov di, word ptr [bp + 4]
02AC  D1 E7           shl di, 1
02AE  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
02B2  3B 46 F2        cmp ax, word ptr [bp - 0xe]
02B5  77 2D           ja 0x2e4
02B7  89 46 FC        mov word ptr [bp - 4], ax
02BA  EB 03           jmp 0x2bf
loc_02BC:
02BC  FF 46 FC        inc word ptr [bp - 4]
loc_02BF:
02BF  8B 46 FC        mov ax, word ptr [bp - 4]
02C2  D1 E0           shl ax, 1
02C4  C4 3E 27 A9     les di, ptr [0xa927]
02C8  03 F8           add di, ax
02CA  26 8B 05        mov ax, word ptr es:[di]
02CD  BA 14 00        mov dx, 0x14
02D0  F7 E2           mul dx
02D2  C4 3E 1B A9     les di, ptr [0xa91b]
02D6  03 F8           add di, ax
02D8  26 C6 05 00     mov byte ptr es:[di], 0
02DC  8B 46 FC        mov ax, word ptr [bp - 4]
02DF  3B 46 F2        cmp ax, word ptr [bp - 0xe]
02E2  75 D8           jne 0x2bc
loc_02E4:
02E4  C4 7E F4        les di, ptr [bp - 0xc]
02E7  26 8A 0D        mov cl, byte ptr es:[di]
02EA  C4 7E F4        les di, ptr [bp - 0xc]
02ED  26 8A 05        mov al, byte ptr es:[di]
02F0  30 E4           xor ah, ah
02F2  BA BF 00        mov dx, 0xbf
02F5  F7 E2           mul dx
02F7  C4 3E 17 A9     les di, ptr [0xa917]
02FB  03 F8           add di, ax
02FD  26 88 4D 2E     mov byte ptr es:[di + 0x2e], cl
0301  C7 46 FE 15 00  mov word ptr [bp - 2], 0x15
loc_0306:
0306  8B 46 FE        mov ax, word ptr [bp - 2]
0309  D1 E0           shl ax, 1
030B  8B C8           mov cx, ax
030D  C4 7E F4        les di, ptr [bp - 0xc]
0310  26 8A 05        mov al, byte ptr es:[di]
0313  30 E4           xor ah, ah
0315  BA 48 00        mov dx, 0x48
0318  F7 E2           mul dx
031A  C4 3E 2F A9     les di, ptr [0xa92f]
031E  03 F8           add di, ax
0320  03 F9           add di, cx
0322  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
0327  75 05           jne 0x32e
0329  FF 46 FE        inc word ptr [bp - 2]
032C  EB D8           jmp 0x306
loc_032E:
032E  8B 46 FE        mov ax, word ptr [bp - 2]
0331  3D 24 00        cmp ax, 0x24
0334  77 52           ja 0x388
0336  89 46 FC        mov word ptr [bp - 4], ax
0339  EB 03           jmp 0x33e
loc_033B:
033B  FF 46 FC        inc word ptr [bp - 4]
loc_033E:
033E  8B 46 FC        mov ax, word ptr [bp - 4]
0341  D1 E0           shl ax, 1
0343  8B C8           mov cx, ax
0345  C4 7E F4        les di, ptr [bp - 0xc]
0348  26 8A 05        mov al, byte ptr es:[di]
034B  30 E4           xor ah, ah
034D  BA 48 00        mov dx, 0x48
0350  F7 E2           mul dx
0352  C4 3E 2F A9     les di, ptr [0xa92f]
0356  03 F8           add di, ax
0358  03 F9           add di, cx
035A  26 8B 45 FE     mov ax, word ptr es:[di - 2]
035E  B1 03           mov cl, 3
0360  D3 E0           shl ax, cl
0362  C4 3E 2B A9     les di, ptr [0xa92b]
0366  03 F8           add di, ax
0368  81 C7 F8 FF     add di, 0xfff8
036C  89 7E F0        mov word ptr [bp - 0x10], di
036F  8C 46 F2        mov word ptr [bp - 0xe], es
0372  C4 7E F0        les di, ptr [bp - 0x10]
0375  26 80 3D FE     cmp byte ptr es:[di], 0xfe
0379  75 07           jne 0x382
037B  C4 7E F0        les di, ptr [bp - 0x10]
037E  26 C6 05 FF     mov byte ptr es:[di], 0xff
loc_0382:
0382  83 7E FC 24     cmp word ptr [bp - 4], 0x24
0386  75 B3           jne 0x33b
loc_0388:
0388  89 EC           mov sp, bp
038A  5D              pop bp
038B  C2 02 00        ret 2

; ---- routine 000E:038E  (found by: call)
sub_038E:
038E  55              push bp
038F  89 E5           mov bp, sp
0391  BF D8 4E        mov di, 0x4ed8
0394  1E              push ds
0395  57              push di
0396  BF 6E A9        mov di, 0xa96e
0399  1E              push ds
039A  57              push di
039B  9A 29 03 4B 21  call far 214B:0329
03A0  BF 96 57        mov di, 0x5796
03A3  1E              push ds
03A4  57              push di
03A5  BF 6E A9        mov di, 0xa96e
03A8  1E              push ds
03A9  57              push di
03AA  9A 29 03 4B 21  call far 214B:0329
03AF  BF A6 14        mov di, 0x14a6
03B2  1E              push ds
03B3  57              push di
03B4  BF 6E A9        mov di, 0xa96e
03B7  1E              push ds
03B8  57              push di
03B9  9A 29 03 4B 21  call far 214B:0329
03BE  89 EC           mov sp, bp
03C0  5D              pop bp
03C1  C3              ret
; data (not reached as code), 2 bytes
03C2                  db 01 20   ; . 

; ---- routine 000E:03C4  (found by: call)
sub_03C4:
03C4  55              push bp
03C5  89 E5           mov bp, sp
03C7  81 EC 52 01     sub sp, 0x152
03CB  C4 7E 06        les di, ptr [bp + 6]
03CE  06              push es
03CF  57              push di
03D0  8D 7E AF        lea di, [bp - 0x51]
03D3  16              push ss
03D4  57              push di
03D5  B8 50 00        mov ax, 0x50
03D8  50              push ax
03D9  9A 44 06 E4 23  call far 23E4:0644
loc_03DE:
03DE  8A 46 AF        mov al, byte ptr [bp - 0x51]
03E1  30 E4           xor ah, ah
03E3  3B 46 04        cmp ax, word ptr [bp + 4]
03E6  73 5C           jae 0x444
03E8  8D BE AF FE     lea di, [bp - 0x151]
03EC  16              push ss
03ED  57              push di
03EE  BF C2 03        mov di, 0x3c2
03F1  0E              push cs
03F2  57              push di
03F3  9A 2A 06 E4 23  call far 23E4:062A
03F8  8D 7E AF        lea di, [bp - 0x51]
03FB  16              push ss
03FC  57              push di
03FD  9A B7 06 E4 23  call far 23E4:06B7
0402  8D 7E AF        lea di, [bp - 0x51]
0405  16              push ss
0406  57              push di
0407  B8 50 00        mov ax, 0x50
040A  50              push ax
040B  9A 44 06 E4 23  call far 23E4:0644
0410  8A 46 AF        mov al, byte ptr [bp - 0x51]
0413  30 E4           xor ah, ah
0415  3B 46 04        cmp ax, word ptr [bp + 4]
0418  73 28           jae 0x442
041A  8D BE AF FE     lea di, [bp - 0x151]
041E  16              push ss
041F  57              push di
0420  8D 7E AF        lea di, [bp - 0x51]
0423  16              push ss
0424  57              push di
0425  9A 2A 06 E4 23  call far 23E4:062A
042A  BF C2 03        mov di, 0x3c2
042D  0E              push cs
042E  57              push di
042F  9A B7 06 E4 23  call far 23E4:06B7
0434  8D 7E AF        lea di, [bp - 0x51]
0437  16              push ss
0438  57              push di
0439  B8 50 00        mov ax, 0x50
043C  50              push ax
043D  9A 44 06 E4 23  call far 23E4:0644
loc_0442:
0442  EB 9A           jmp 0x3de
loc_0444:
0444  8D 7E AF        lea di, [bp - 0x51]
0447  16              push ss
0448  57              push di
0449  C4 7E 0A        les di, ptr [bp + 0xa]
044C  06              push es
044D  57              push di
044E  B8 50 00        mov ax, 0x50
0451  50              push ax
0452  9A 44 06 E4 23  call far 23E4:0644
0457  89 EC           mov sp, bp
0459  5D              pop bp
045A  C2 06 00        ret 6

; ---- routine 000E:045D  (found by: call)
sub_045D:
045D  55              push bp
045E  89 E5           mov bp, sp
0460  83 EC 08        sub sp, 8
0463  C7 46 FE 01 00  mov word ptr [bp - 2], 1
0468  EB 03           jmp 0x46d
loc_046A:
046A  FF 46 FE        inc word ptr [bp - 2]
loc_046D:
046D  C7 46 FC 01 00  mov word ptr [bp - 4], 1
0472  EB 03           jmp 0x477
loc_0474:
0474  FF 46 FC        inc word ptr [bp - 4]
loc_0477:
0477  B8 05 00        mov ax, 5
047A  50              push ax
047B  9A B1 06 4B 21  call far 214B:06B1
0480  89 46 FA        mov word ptr [bp - 6], ax
0483  B8 50 00        mov ax, 0x50
0486  50              push ax
0487  9A B1 06 4B 21  call far 214B:06B1
048C  89 46 F8        mov word ptr [bp - 8], ax
048F  8B 46 F8        mov ax, word ptr [bp - 8]
0492  D1 E0           shl ax, 1
0494  8B C8           mov cx, ax
0496  8B 46 FA        mov ax, word ptr [bp - 6]
0499  BA A0 00        mov dx, 0xa0
049C  F7 E2           mul dx
049E  C4 3E 6A A9     les di, ptr [0xa96a]
04A2  03 F8           add di, ax
04A4  03 F9           add di, cx
04A6  26 80 BD 5E FF 07 cmp byte ptr es:[di - 0xa2], 7
04AC  73 27           jae 0x4d5
04AE  B8 0F 00        mov ax, 0xf
04B1  50              push ax
04B2  9A B1 06 4B 21  call far 214B:06B1
04B7  8A D8           mov bl, al
04B9  8B 46 F8        mov ax, word ptr [bp - 8]
04BC  D1 E0           shl ax, 1
04BE  8B C8           mov cx, ax
04C0  8B 46 FA        mov ax, word ptr [bp - 6]
04C3  BA A0 00        mov dx, 0xa0
04C6  F7 E2           mul dx
04C8  C4 3E 6A A9     les di, ptr [0xa96a]
04CC  03 F8           add di, ax
04CE  03 F9           add di, cx
04D0  26 88 9D 5F FF  mov byte ptr es:[di - 0xa1], bl
loc_04D5:
04D5  83 7E FC 0A     cmp word ptr [bp - 4], 0xa
04D9  75 99           jne 0x474
04DB  8B 46 06        mov ax, word ptr [bp + 6]
04DE  D1 E0           shl ax, 1
04E0  50              push ax
04E1  9A 09 1E 4B 21  call far 214B:1E09
04E6  83 7E FE 32     cmp word ptr [bp - 2], 0x32
04EA  74 03           je 0x4ef
04EC  E9 7B FF        jmp 0x46a
loc_04EF:
04EF  89 EC           mov sp, bp
04F1  5D              pop bp
04F2  C2 04 00        ret 4

; ---- routine 000E:04F5  (found by: call)
sub_04F5:
04F5  55              push bp
04F6  89 E5           mov bp, sp
04F8  83 EC 02        sub sp, 2
04FB  8A 46 06        mov al, byte ptr [bp + 6]
04FE  A2 68 79        mov byte ptr [0x7968], al
0501  9A 75 1E 4B 21  call far 214B:1E75
0506  C7 46 FE 01 00  mov word ptr [bp - 2], 1
050B  EB 03           jmp 0x510
loc_050D:
050D  FF 46 FE        inc word ptr [bp - 2]
loc_0510:
0510  9A 23 07 4B 21  call far 214B:0723
0515  08 C0           or al, al
0517  74 02           je 0x51b
0519  EB 3E           jmp 0x559
loc_051B:
051B  B8 03 00        mov ax, 3
051E  50              push ax
051F  8B 7E FE        mov di, word ptr [bp - 2]
0522  D1 E7           shl di, 1
0524  8A 85 00 00     mov al, byte ptr [di]
0528  30 E4           xor ah, ah
052A  50              push ax
052B  8B 7E FE        mov di, word ptr [bp - 2]
052E  D1 E7           shl di, 1
0530  8A 85 01 00     mov al, byte ptr [di + 1]
0534  30 E4           xor ah, ah
0536  50              push ax
0537  9A F1 1E 4B 21  call far 214B:1EF1
053C  8B 7E FE        mov di, word ptr [bp - 2]
053F  D1 E7           shl di, 1
0541  8A 85 01 00     mov al, byte ptr [di + 1]
0545  30 E4           xor ah, ah
0547  50              push ax
0548  FF 76 04        push word ptr [bp + 4]
054B  E8 0F FF        call 0x45d
054E  83 7E FE 10     cmp word ptr [bp - 2], 0x10
0552  75 B9           jne 0x50d
0554  9A 8D 1E 4B 21  call far 214B:1E8D
loc_0559:
0559  89 EC           mov sp, bp
055B  5D              pop bp
055C  C2 04 00        ret 4
; data (not reached as code), 19 bytes
055F                  pstr 'BEST PLACE YET  !!'

; ---- routine 000E:0572  (found by: call)
sub_0572:
0572  55              push bp
0573  89 E5           mov bp, sp
0575  BF 94 5B        mov di, 0x5b94
0578  1E              push ds
0579  57              push di
057A  BF 6A A9        mov di, 0xa96a
057D  1E              push ds
057E  57              push di
057F  9A 29 03 4B 21  call far 214B:0329
0584  8B 7E 04        mov di, word ptr [bp + 4]
0587  36 80 7D 06 00  cmp byte ptr ss:[di + 6], 0
058C  74 1A           je 0x5a8
058E  B0 0F           mov al, 0xf
0590  50              push ax
0591  BF 5F 05        mov di, 0x55f
0594  0E              push cs
0595  57              push di
0596  B0 03           mov al, 3
0598  50              push ax
0599  B0 20           mov al, 0x20
059B  50              push ax
059C  BF 6A A9        mov di, 0xa96a
059F  1E              push ds
05A0  57              push di
05A1  9A C8 02 4B 21  call far 214B:02C8
05A6  EB 37           jmp 0x5df
loc_05A8:
05A8  C7 06 66 79 01 00 mov word ptr [0x7966], 1
05AE  31 C0           xor ax, ax
05B0  50              push ax
05B1  55              push bp
05B2  E8 40 FF        call 0x4f5
05B5  8B 7E 04        mov di, word ptr [bp + 4]
05B8  36 80 7D 04 00  cmp byte ptr ss:[di + 4], 0
05BD  74 1B           je 0x5da
05BF  B8 04 00        mov ax, 4
05C2  50              push ax
05C3  55              push bp
05C4  E8 2E FF        call 0x4f5
05C7  C4 3E 23 A9     les di, ptr [0xa923]
05CB  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
05D0  74 08           je 0x5da
05D2  B8 08 00        mov ax, 8
05D5  50              push ax
05D6  55              push bp
05D7  E8 1B FF        call 0x4f5
loc_05DA:
05DA  9A 8D 1E 4B 21  call far 214B:1E8D
loc_05DF:
05DF  B8 02 00        mov ax, 2
05E2  50              push ax
05E3  55              push bp
05E4  E8 76 FE        call 0x45d
05E7  9A 23 07 4B 21  call far 214B:0723
05EC  08 C0           or al, al
05EE  74 EF           je 0x5df
05F0  89 EC           mov sp, bp
05F2  5D              pop bp
05F3  C2 02 00        ret 2

; ---- routine 000E:05F6  (found by: call)
sub_05F6:
05F6  55              push bp
05F7  89 E5           mov bp, sp
05F9  C4 3E 6E A9     les di, ptr [0xa96e]
05FD  06              push es
05FE  57              push di
05FF  C4 3E 6A A9     les di, ptr [0xa96a]
0603  06              push es
0604  57              push di
0605  B8 A0 0F        mov ax, 0xfa0
0608  50              push ax
0609  9A 5D 02 E4 23  call far 23E4:025D
060E  80 7E 08 00     cmp byte ptr [bp + 8], 0
0612  75 0C           jne 0x620
0614  80 7E 06 00     cmp byte ptr [bp + 6], 0
0618  75 06           jne 0x620
061A  80 7E 04 00     cmp byte ptr [bp + 4], 0
061E  74 04           je 0x624
loc_0620:
0620  55              push bp
0621  E8 4E FF        call 0x572
loc_0624:
0624  9A DD 08 4B 21  call far 214B:08DD
0629  89 EC           mov sp, bp
062B  5D              pop bp
062C  C2 06 00        ret 6

; ---- routine 000E:062F  (found by: call)
sub_062F:
062F  55              push bp
0630  89 E5           mov bp, sp
0632  81 EC 40 02     sub sp, 0x240
0636  C4 7E 0C        les di, ptr [bp + 0xc]
0639  06              push es
063A  57              push di
063B  8D 7E EB        lea di, [bp - 0x15]
063E  16              push ss
063F  57              push di
0640  B8 14 00        mov ax, 0x14
0643  50              push ax
0644  9A 44 06 E4 23  call far 23E4:0644
0649  C4 7E 08        les di, ptr [bp + 8]
064C  06              push es
064D  57              push di
064E  8D 7E D6        lea di, [bp - 0x2a]
0651  16              push ss
0652  57              push di
0653  B8 14 00        mov ax, 0x14
0656  50              push ax
0657  9A 44 06 E4 23  call far 23E4:0644
065C  C4 7E 04        les di, ptr [bp + 4]
065F  06              push es
0660  57              push di
0661  8D 7E C1        lea di, [bp - 0x3f]
0664  16              push ss
0665  57              push di
0666  B8 14 00        mov ax, 0x14
0669  50              push ax
066A  9A 44 06 E4 23  call far 23E4:0644
066F  B0 70           mov al, 0x70
0671  50              push ax
0672  8D BE C1 FD     lea di, [bp - 0x23f]
0676  16              push ss
0677  57              push di
0678  8D BE C1 FE     lea di, [bp - 0x13f]
067C  16              push ss
067D  57              push di
067E  8D 7E EB        lea di, [bp - 0x15]
0681  16              push ss
0682  57              push di
0683  B8 12 00        mov ax, 0x12
0686  50              push ax
0687  E8 3A FD        call 0x3c4
068A  9A 9C 00 4B 21  call far 214B:009C
068F  B0 0B           mov al, 0xb
0691  50              push ax
0692  B0 05           mov al, 5
0694  50              push ax
0695  BF 6E A9        mov di, 0xa96e
0698  1E              push ds
0699  57              push di
069A  9A C8 02 4B 21  call far 214B:02C8
069F  80 7E D6 00     cmp byte ptr [bp - 0x2a], 0
06A3  74 2D           je 0x6d2
06A5  8D BE C1 FD     lea di, [bp - 0x23f]
06A9  16              push ss
06AA  57              push di
06AB  8D BE C1 FE     lea di, [bp - 0x13f]
06AF  16              push ss
06B0  57              push di
06B1  8D 7E D6        lea di, [bp - 0x2a]
06B4  16              push ss
06B5  57              push di
06B6  B8 12 00        mov ax, 0x12
06B9  50              push ax
06BA  E8 07 FD        call 0x3c4
06BD  9A 9C 00 4B 21  call far 214B:009C
06C2  B0 0C           mov al, 0xc
06C4  50              push ax
06C5  B0 05           mov al, 5
06C7  50              push ax
06C8  BF 6E A9        mov di, 0xa96e
06CB  1E              push ds
06CC  57              push di
06CD  9A 6D 02 4B 21  call far 214B:026D
loc_06D2:
06D2  80 7E C1 00     cmp byte ptr [bp - 0x3f], 0
06D6  74 2D           je 0x705
06D8  8D BE C1 FD     lea di, [bp - 0x23f]
06DC  16              push ss
06DD  57              push di
06DE  8D BE C1 FE     lea di, [bp - 0x13f]
06E2  16              push ss
06E3  57              push di
06E4  8D 7E C1        lea di, [bp - 0x3f]
06E7  16              push ss
06E8  57              push di
06E9  B8 12 00        mov ax, 0x12
06EC  50              push ax
06ED  E8 D4 FC        call 0x3c4
06F0  9A 9C 00 4B 21  call far 214B:009C
06F5  B0 0D           mov al, 0xd
06F7  50              push ax
06F8  B0 05           mov al, 5
06FA  50              push ax
06FB  BF 6E A9        mov di, 0xa96e
06FE  1E              push ds
06FF  57              push di
0700  9A 6D 02 4B 21  call far 214B:026D
loc_0705:
0705  89 EC           mov sp, bp
0707  5D              pop bp
0708  C2 0C 00        ret 0xc

; ---- routine 000E:070B  (found by: call)
sub_070B:
070B  55              push bp
070C  89 E5           mov bp, sp
070E  81 EC 16 02     sub sp, 0x216
0712  C4 7E 04        les di, ptr [bp + 4]
0715  06              push es
0716  57              push di
0717  8D 7E EB        lea di, [bp - 0x15]
071A  16              push ss
071B  57              push di
071C  B8 14 00        mov ax, 0x14
071F  50              push ax
0720  9A 44 06 E4 23  call far 23E4:0644
0725  B0 17           mov al, 0x17
0727  50              push ax
0728  8D BE EB FD     lea di, [bp - 0x215]
072C  16              push ss
072D  57              push di
072E  8D BE EB FE     lea di, [bp - 0x115]
0732  16              push ss
0733  57              push di
0734  8D 7E EB        lea di, [bp - 0x15]
0737  16              push ss
0738  57              push di
0739  B8 14 00        mov ax, 0x14
073C  50              push ax
073D  E8 84 FC        call 0x3c4
0740  9A 9C 00 4B 21  call far 214B:009C
0745  8B 46 08        mov ax, word ptr [bp + 8]
0748  05 08 00        add ax, 8
074B  50              push ax
074C  B0 1F           mov al, 0x1f
074E  50              push ax
074F  BF 6E A9        mov di, 0xa96e
0752  1E              push ds
0753  57              push di
0754  9A C8 02 4B 21  call far 214B:02C8
0759  89 EC           mov sp, bp
075B  5D              pop bp
075C  C2 06 00        ret 6

; ---- routine 000E:075F  (found by: call)
sub_075F:
075F  55              push bp
0760  89 E5           mov bp, sp
0762  81 EC 40 02     sub sp, 0x240
0766  C4 7E 0C        les di, ptr [bp + 0xc]
0769  06              push es
076A  57              push di
076B  8D 7E EB        lea di, [bp - 0x15]
076E  16              push ss
076F  57              push di
0770  B8 14 00        mov ax, 0x14
0773  50              push ax
0774  9A 44 06 E4 23  call far 23E4:0644
0779  C4 7E 08        les di, ptr [bp + 8]
077C  06              push es
077D  57              push di
077E  8D 7E D6        lea di, [bp - 0x2a]
0781  16              push ss
0782  57              push di
0783  B8 14 00        mov ax, 0x14
0786  50              push ax
0787  9A 44 06 E4 23  call far 23E4:0644
078C  C4 7E 04        les di, ptr [bp + 4]
078F  06              push es
0790  57              push di
0791  8D 7E C1        lea di, [bp - 0x3f]
0794  16              push ss
0795  57              push di
0796  B8 14 00        mov ax, 0x14
0799  50              push ax
079A  9A 44 06 E4 23  call far 23E4:0644
079F  B0 20           mov al, 0x20
07A1  50              push ax
07A2  8D BE C1 FD     lea di, [bp - 0x23f]
07A6  16              push ss
07A7  57              push di
07A8  8D BE C1 FE     lea di, [bp - 0x13f]
07AC  16              push ss
07AD  57              push di
07AE  8D 7E EB        lea di, [bp - 0x15]
07B1  16              push ss
07B2  57              push di
07B3  B8 12 00        mov ax, 0x12
07B6  50              push ax
07B7  E8 0A FC        call 0x3c4
07BA  9A 9C 00 4B 21  call far 214B:009C
07BF  B0 0B           mov al, 0xb
07C1  50              push ax
07C2  B0 3B           mov al, 0x3b
07C4  50              push ax
07C5  BF 6E A9        mov di, 0xa96e
07C8  1E              push ds
07C9  57              push di
07CA  9A C8 02 4B 21  call far 214B:02C8
07CF  80 7E D6 00     cmp byte ptr [bp - 0x2a], 0
07D3  74 2D           je 0x802
07D5  8D BE C1 FD     lea di, [bp - 0x23f]
07D9  16              push ss
07DA  57              push di
07DB  8D BE C1 FE     lea di, [bp - 0x13f]
07DF  16              push ss
07E0  57              push di
07E1  8D 7E D6        lea di, [bp - 0x2a]
07E4  16              push ss
07E5  57              push di
07E6  B8 12 00        mov ax, 0x12
07E9  50              push ax
07EA  E8 D7 FB        call 0x3c4
07ED  9A 9C 00 4B 21  call far 214B:009C
07F2  B0 0C           mov al, 0xc
07F4  50              push ax
07F5  B0 3B           mov al, 0x3b
07F7  50              push ax
07F8  BF 6E A9        mov di, 0xa96e
07FB  1E              push ds
07FC  57              push di
07FD  9A 6D 02 4B 21  call far 214B:026D
loc_0802:
0802  80 7E C1 00     cmp byte ptr [bp - 0x3f], 0
0806  74 2D           je 0x835
0808  8D BE C1 FD     lea di, [bp - 0x23f]
080C  16              push ss
080D  57              push di
080E  8D BE C1 FE     lea di, [bp - 0x13f]
0812  16              push ss
0813  57              push di
0814  8D 7E C1        lea di, [bp - 0x3f]
0817  16              push ss
0818  57              push di
0819  B8 12 00        mov ax, 0x12
081C  50              push ax
081D  E8 A4 FB        call 0x3c4
0820  9A 9C 00 4B 21  call far 214B:009C
0825  B0 0D           mov al, 0xd
0827  50              push ax
0828  B0 3B           mov al, 0x3b
082A  50              push ax
082B  BF 6E A9        mov di, 0xa96e
082E  1E              push ds
082F  57              push di
0830  9A 6D 02 4B 21  call far 214B:026D
loc_0835:
0835  89 EC           mov sp, bp
0837  5D              pop bp
0838  C2 0C 00        ret 0xc
; data (not reached as code), 45 bytes
083B                  pstr 'Assistant says:'
084B                  pstr 'Physio says:'
0858                  pstr 'Coach comments:'

; ---- routine 000E:0868  (found by: call)
sub_0868:
0868  55              push bp
0869  89 E5           mov bp, sp
086B  83 EC 2A        sub sp, 0x2a
086E  C4 7E 08        les di, ptr [bp + 8]
0871  06              push es
0872  57              push di
0873  8D 7E EB        lea di, [bp - 0x15]
0876  16              push ss
0877  57              push di
0878  B8 14 00        mov ax, 0x14
087B  50              push ax
087C  9A 44 06 E4 23  call far 23E4:0644
0881  C4 7E 04        les di, ptr [bp + 4]
0884  06              push es
0885  57              push di
0886  8D 7E D6        lea di, [bp - 0x2a]
0889  16              push ss
088A  57              push di
088B  B8 14 00        mov ax, 0x14
088E  50              push ax
088F  9A 44 06 E4 23  call far 23E4:0644
0894  B8 03 00        mov ax, 3
0897  50              push ax
0898  9A B1 06 4B 21  call far 214B:06B1
089D  3D 01 00        cmp ax, 1
08A0  75 0D           jne 0x8af
08A2  FF 76 0C        push word ptr [bp + 0xc]
08A5  BF 3B 08        mov di, 0x83b
08A8  0E              push cs
08A9  57              push di
08AA  E8 5E FE        call 0x70b
08AD  EB 22           jmp 0x8d1
loc_08AF:
08AF  3D 02 00        cmp ax, 2
08B2  75 0D           jne 0x8c1
08B4  FF 76 0C        push word ptr [bp + 0xc]
08B7  BF 4B 08        mov di, 0x84b
08BA  0E              push cs
08BB  57              push di
08BC  E8 4C FE        call 0x70b
08BF  EB 10           jmp 0x8d1
loc_08C1:
08C1  3D 03 00        cmp ax, 3
08C4  75 0B           jne 0x8d1
08C6  FF 76 0C        push word ptr [bp + 0xc]
08C9  BF 58 08        mov di, 0x858
08CC  0E              push cs
08CD  57              push di
08CE  E8 3A FE        call 0x70b
loc_08D1:
08D1  8B 46 0C        mov ax, word ptr [bp + 0xc]
08D4  40              inc ax
08D5  50              push ax
08D6  8D 7E EB        lea di, [bp - 0x15]
08D9  16              push ss
08DA  57              push di
08DB  E8 2D FE        call 0x70b
08DE  80 7E D6 00     cmp byte ptr [bp - 0x2a], 0
08E2  74 0F           je 0x8f3
08E4  8B 46 0C        mov ax, word ptr [bp + 0xc]
08E7  05 02 00        add ax, 2
08EA  50              push ax
08EB  8D 7E D6        lea di, [bp - 0x2a]
08EE  16              push ss
08EF  57              push di
08F0  E8 18 FE        call 0x70b
loc_08F3:
08F3  89 EC           mov sp, bp
08F5  5D              pop bp
08F6  C2 0A 00        ret 0xa

; ---- routine 000E:08F9  (found by: call)
sub_08F9:
08F9  55              push bp
08FA  89 E5           mov bp, sp
08FC  83 EC 04        sub sp, 4
08FF  8B 7E 04        mov di, word ptr [bp + 4]
0902  36 8B 45 08     mov ax, word ptr ss:[di + 8]
0906  BA BF 00        mov dx, 0xbf
0909  F7 E2           mul dx
090B  C4 3E 17 A9     les di, ptr [0xa917]
090F  03 F8           add di, ax
0911  89 7E FC        mov word ptr [bp - 4], di
0914  8C 46 FE        mov word ptr [bp - 2], es
0917  8B 7E 04        mov di, word ptr [bp + 4]
091A  36 8B 45 FA     mov ax, word ptr ss:[di - 6]
091E  D1 E0           shl ax, 1
0920  C4 7E FC        les di, ptr [bp - 4]
0923  03 F8           add di, ax
0925  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0929  BA 0B 00        mov dx, 0xb
092C  F7 E2           mul dx
092E  C4 3E 6C 9B     les di, ptr [0x9b6c]
0932  03 F8           add di, ax
0934  06              push es
0935  57              push di
0936  C4 7E 06        les di, ptr [bp + 6]
0939  06              push es
093A  57              push di
093B  B8 0F 00        mov ax, 0xf
093E  50              push ax
093F  9A 44 06 E4 23  call far 23E4:0644
0944  89 EC           mov sp, bp
0946  5D              pop bp
0947  C2 02 00        ret 2

; ---- routine 000E:094A  (found by: call)
sub_094A:
094A  55              push bp
094B  89 E5           mov bp, sp
094D  83 EC 06        sub sp, 6
0950  8B 7E 04        mov di, word ptr [bp + 4]
0953  36 8B 45 08     mov ax, word ptr ss:[di + 8]
0957  BA BF 00        mov dx, 0xbf
095A  F7 E2           mul dx
095C  C4 3E 17 A9     les di, ptr [0xa917]
0960  03 F8           add di, ax
0962  89 7E FA        mov word ptr [bp - 6], di
0965  8C 46 FC        mov word ptr [bp - 4], es
0968  C4 7E 06        les di, ptr [bp + 6]
096B  26 C6 05 00     mov byte ptr es:[di], 0
096F  C7 46 FE 01 00  mov word ptr [bp - 2], 1
0974  EB 03           jmp 0x979
loc_0976:
0976  FF 46 FE        inc word ptr [bp - 2]
loc_0979:
0979  B8 06 00        mov ax, 6
097C  50              push ax
097D  8B 46 FE        mov ax, word ptr [bp - 2]
0980  D1 E0           shl ax, 1
0982  C4 7E FA        les di, ptr [bp - 6]
0985  03 F8           add di, ax
0987  26 8B 45 FE     mov ax, word ptr es:[di - 2]
098B  BA 14 00        mov dx, 0x14
098E  F7 E2           mul dx
0990  C4 3E 1B A9     les di, ptr [0xa91b]
0994  03 F8           add di, ax
0996  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
099A  30 E4           xor ah, ah
099C  50              push ax
099D  9A 57 0C 4B 21  call far 214B:0C57
09A2  08 C0           or al, al
09A4  74 29           je 0x9cf
09A6  8B 46 FE        mov ax, word ptr [bp - 2]
09A9  D1 E0           shl ax, 1
09AB  C4 7E FA        les di, ptr [bp - 6]
09AE  03 F8           add di, ax
09B0  26 8B 45 FE     mov ax, word ptr es:[di - 2]
09B4  BA 0B 00        mov dx, 0xb
09B7  F7 E2           mul dx
09B9  C4 3E 6C 9B     les di, ptr [0x9b6c]
09BD  03 F8           add di, ax
09BF  06              push es
09C0  57              push di
09C1  C4 7E 06        les di, ptr [bp + 6]
09C4  06              push es
09C5  57              push di
09C6  B8 0F 00        mov ax, 0xf
09C9  50              push ax
09CA  9A 44 06 E4 23  call far 23E4:0644
loc_09CF:
09CF  83 7E FE 14     cmp word ptr [bp - 2], 0x14
09D3  75 A1           jne 0x976
09D5  89 EC           mov sp, bp
09D7  5D              pop bp
09D8  C2 02 00        ret 2

; ---- routine 000E:09DB  (found by: call)
sub_09DB:
09DB  55              push bp
09DC  89 E5           mov bp, sp
09DE  83 EC 02        sub sp, 2
09E1  8B 7E 04        mov di, word ptr [bp + 4]
09E4  36 80 7D FF 01  cmp byte ptr ss:[di - 1], 1
09E9  74 04           je 0x9ef
09EB  B0 00           mov al, 0
09ED  EB 02           jmp 0x9f1
loc_09EF:
09EF  B0 01           mov al, 1
loc_09F1:
09F1  30 E4           xor ah, ah
09F3  50              push ax
09F4  8B 7E 04        mov di, word ptr [bp + 4]
09F7  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
09FC  74 04           je 0xa02
09FE  B0 00           mov al, 0
0A00  EB 02           jmp 0xa04
loc_0A02:
0A02  B0 01           mov al, 1
loc_0A04:
0A04  98              cwde
0A05  D1 E0           shl ax, 1
0A07  8B 7E 04        mov di, word ptr [bp + 4]
0A0A  36 C4 7D 04     les di, ptr ss:[di + 4]
0A0E  03 F8           add di, ax
0A10  26 FF 75 04     push word ptr es:[di + 4]
0A14  9A E7 10 71 17  call far 1771:10E7
0A19  05 02 00        add ax, 2
0A1C  5A              pop dx
0A1D  2B C2           sub ax, dx
0A1F  50              push ax
0A20  8B 7E 04        mov di, word ptr [bp + 4]
0A23  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
0A27  98              cwde
0A28  D1 E0           shl ax, 1
0A2A  8B 7E 04        mov di, word ptr [bp + 4]
0A2D  36 C4 7D 04     les di, ptr ss:[di + 4]
0A31  03 F8           add di, ax
0A33  26 FF 75 04     push word ptr es:[di + 4]
0A37  9A E7 10 71 17  call far 1771:10E7
0A3C  5A              pop dx
0A3D  3B C2           cmp ax, dx
0A3F  7F 04           jg 0xa45
0A41  B0 00           mov al, 0
0A43  EB 02           jmp 0xa47
loc_0A45:
0A45  B0 01           mov al, 1
loc_0A47:
0A47  88 46 FF        mov byte ptr [bp - 1], al
0A4A  8A 46 FF        mov al, byte ptr [bp - 1]
0A4D  89 EC           mov sp, bp
0A4F  5D              pop bp
0A50  C2 02 00        ret 2

