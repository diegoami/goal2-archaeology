; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 1 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 1771:0000  (found by: call, far)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  83 EC 02        sub sp, 2
0006  A0 38 0C        mov al, byte ptr [0xc38]
0009  30 E4           xor ah, ah
000B  50              push ax
000C  9A B1 06 4B 21  call far 214B:06B1
0011  8B F8           mov di, ax
0013  8A 85 38 0C     mov al, byte ptr [di + 0xc38]
0017  88 46 FF        mov byte ptr [bp - 1], al
001A  8A 46 FF        mov al, byte ptr [bp - 1]
001D  89 EC           mov sp, bp
001F  5D              pop bp
0020  CB              retf

; ---- routine 1771:0021  (found by: call)
sub_0021:
0021  55              push bp
0022  89 E5           mov bp, sp
0024  83 EC 04        sub sp, 4
0027  C4 3E 23 A9     les di, ptr [0xa923]
002B  89 7E FC        mov word ptr [bp - 4], di
002E  8C 46 FE        mov word ptr [bp - 2], es
0031  BF 9C 18        mov di, 0x189c
0034  1E              push ds
0035  57              push di
0036  BF 6E A9        mov di, 0xa96e
0039  1E              push ds
003A  57              push di
003B  9A 29 03 4B 21  call far 214B:0329
loc_0040:
0040  BF 0E 1B        mov di, 0x1b0e
0043  1E              push ds
0044  57              push di
0045  BF 6E A9        mov di, 0xa96e
0048  1E              push ds
0049  57              push di
004A  9A 29 03 4B 21  call far 214B:0329
004F  B8 0E 00        mov ax, 0xe
0052  50              push ax
0053  8B 3E 4E 0C     mov di, word ptr [0xc4e]
0057  8A 85 4F 0C     mov al, byte ptr [di + 0xc4f]
005B  30 E4           xor ah, ah
005D  50              push ax
005E  B8 01 00        mov ax, 1
0061  50              push ax
0062  9A C5 13 4B 21  call far 214B:13C5
0067  C4 3E 6E A9     les di, ptr [0xa96e]
006B  06              push es
006C  57              push di
006D  C4 3E 6A A9     les di, ptr [0xa96a]
0071  06              push es
0072  57              push di
0073  B8 A0 0F        mov ax, 0xfa0
0076  50              push ax
0077  9A 5D 02 E4 23  call far 23E4:025D
007C  9A DD 08 4B 21  call far 214B:08DD
0081  80 3E 76 A9 AE  cmp byte ptr [0xa976], 0xae
0086  75 07           jne 0x8f
0088  C6 06 76 A9 AC  mov byte ptr [0xa976], 0xac
008D  EB 0C           jmp 0x9b
loc_008F:
008F  80 3E 76 A9 AF  cmp byte ptr [0xa976], 0xaf
0094  75 05           jne 0x9b
0096  C6 06 76 A9 B1  mov byte ptr [0xa976], 0xb1
loc_009B:
009B  BF 4E 0C        mov di, 0xc4e
009E  1E              push ds
009F  57              push di
00A0  B8 06 00        mov ax, 6
00A3  50              push ax
00A4  9A 07 15 4B 21  call far 214B:1507
00A9  A0 76 A9        mov al, byte ptr [0xa976]
00AC  3C 31           cmp al, 0x31
00AE  72 14           jb 0xc4
00B0  3C 36           cmp al, 0x36
00B2  77 10           ja 0xc4
00B4  A0 76 A9        mov al, byte ptr [0xa976]
00B7  30 E4           xor ah, ah
00B9  2D 30 00        sub ax, 0x30
00BC  C4 7E FC        les di, ptr [bp - 4]
00BF  26 88 05        mov byte ptr es:[di], al
00C2  EB 1A           jmp 0xde
loc_00C4:
00C4  3C 0D           cmp al, 0xd
00C6  75 0B           jne 0xd3
00C8  A0 4E 0C        mov al, byte ptr [0xc4e]
00CB  C4 7E FC        les di, ptr [bp - 4]
00CE  26 88 05        mov byte ptr es:[di], al
00D1  EB 0B           jmp 0xde
loc_00D3:
00D3  3C 1B           cmp al, 0x1b
00D5  75 07           jne 0xde
00D7  31 C0           xor ax, ax
00D9  9A D8 00 E4 23  call far 23E4:00D8
loc_00DE:
00DE  C4 7E FC        les di, ptr [bp - 4]
00E1  26 80 3D 00     cmp byte ptr es:[di], 0
00E5  75 03           jne 0xea
00E7  E9 56 FF        jmp 0x40
loc_00EA:
00EA  89 EC           mov sp, bp
00EC  5D              pop bp
00ED  C3              ret
; data (not reached as code), 45 bytes
00EE                  pstr 'Cannot load file "'
0101                  pstr '" - program terminated - '

; ---- routine 1771:011B  (found by: call)
sub_011B:
011B  55              push bp
011C  89 E5           mov bp, sp
011E  81 EC 16 01     sub sp, 0x116
0122  C4 7E 04        les di, ptr [bp + 4]
0125  06              push es
0126  57              push di
0127  8D 7E EB        lea di, [bp - 0x15]
012A  16              push ss
012B  57              push di
012C  B8 14 00        mov ax, 0x14
012F  50              push ax
0130  9A 44 06 E4 23  call far 23E4:0644
0135  BF 56 0C        mov di, 0xc56
0138  1E              push ds
0139  57              push di
013A  BF 6A A9        mov di, 0xa96a
013D  1E              push ds
013E  57              push di
013F  9A 29 03 4B 21  call far 214B:0329
0144  8D 7E EB        lea di, [bp - 0x15]
0147  16              push ss
0148  57              push di
0149  9A F5 1B 4B 21  call far 214B:1BF5
014E  08 C0           or al, al
0150  75 29           jne 0x17b
0152  8D BE EB FE     lea di, [bp - 0x115]
0156  16              push ss
0157  57              push di
0158  BF EE 00        mov di, 0xee
015B  0E              push cs
015C  57              push di
015D  9A 2A 06 E4 23  call far 23E4:062A
0162  8D 7E EB        lea di, [bp - 0x15]
0165  16              push ss
0166  57              push di
0167  9A B7 06 E4 23  call far 23E4:06B7
016C  BF 01 01        mov di, 0x101
016F  0E              push cs
0170  57              push di
0171  9A B7 06 E4 23  call far 23E4:06B7
0176  9A 10 0A 4B 21  call far 214B:0A10
loc_017B:
017B  89 EC           mov sp, bp
017D  5D              pop bp
017E  C2 04 00        ret 4
; data (not reached as code), 9 bytes
0181                  pstr 'goal.dat'

; ---- routine 1771:018A  (found by: call)
sub_018A:
018A  55              push bp
018B  89 E5           mov bp, sp
018D  83 EC 02        sub sp, 2
0190  BF 81 01        mov di, 0x181
0193  0E              push cs
0194  57              push di
0195  E8 83 FF        call 0x11b
0198  C4 3E 68 9B     les di, ptr [0x9b68]
019C  06              push es
019D  57              push di
019E  B8 10 08        mov ax, 0x810
01A1  50              push ax
01A2  9A 47 1B 4B 21  call far 214B:1B47
01A7  C4 3E 6C 9B     les di, ptr [0x9b6c]
01AB  06              push es
01AC  57              push di
01AD  B8 87 83        mov ax, 0x8387
01B0  50              push ax
01B1  9A 47 1B 4B 21  call far 214B:1B47
01B6  C4 3E 70 9B     les di, ptr [0x9b70]
01BA  06              push es
01BB  57              push di
01BC  B8 F5 0B        mov ax, 0xbf5
01BF  50              push ax
01C0  9A 47 1B 4B 21  call far 214B:1B47
01C5  C4 3E 74 9B     les di, ptr [0x9b74]
01C9  06              push es
01CA  57              push di
01CB  B8 DB 06        mov ax, 0x6db
01CE  50              push ax
01CF  9A 47 1B 4B 21  call far 214B:1B47
01D4  C4 3E 78 9B     les di, ptr [0x9b78]
01D8  06              push es
01D9  57              push di
01DA  B8 87 00        mov ax, 0x87
01DD  50              push ax
01DE  9A 47 1B 4B 21  call far 214B:1B47
01E3  BF 80 9D        mov di, 0x9d80
01E6  1E              push ds
01E7  57              push di
01E8  B8 83 01        mov ax, 0x183
01EB  50              push ax
01EC  9A 47 1B 4B 21  call far 214B:1B47
01F1  BF 7C 9B        mov di, 0x9b7c
01F4  1E              push ds
01F5  57              push di
01F6  B8 81 00        mov ax, 0x81
01F9  50              push ax
01FA  9A 47 1B 4B 21  call far 214B:1B47
01FF  BF FD 9B        mov di, 0x9bfd
0202  1E              push ds
0203  57              push di
0204  B8 81 00        mov ax, 0x81
0207  50              push ax
0208  9A 47 1B 4B 21  call far 214B:1B47
020D  BF 7E 9C        mov di, 0x9c7e
0210  1E              push ds
0211  57              push di
0212  B8 81 00        mov ax, 0x81
0215  50              push ax
0216  9A 47 1B 4B 21  call far 214B:1B47
021B  BF 03 9F        mov di, 0x9f03
021E  1E              push ds
021F  57              push di
0220  B8 14 0A        mov ax, 0xa14
0223  50              push ax
0224  9A 47 1B 4B 21  call far 214B:1B47
0229  9A 36 1A 4B 21  call far 214B:1A36
022E  89 EC           mov sp, bp
0230  5D              pop bp
0231  CB              retf

; ---- routine 1771:0232  (found by: call)
sub_0232:
0232  55              push bp
0233  89 E5           mov bp, sp
0235  8B 7E 04        mov di, word ptr [bp + 4]
0238  36 80 7D 04 00  cmp byte ptr ss:[di + 4], 0
023D  74 0F           je 0x24e
023F  C4 7E 08        les di, ptr [bp + 8]
0242  06              push es
0243  57              push di
0244  FF 76 06        push word ptr [bp + 6]
0247  9A 47 1B 4B 21  call far 214B:1B47
024C  EB 1E           jmp 0x26c
loc_024E:
024E  8B 7E 04        mov di, word ptr [bp + 4]
0251  36 80 7D FE 00  cmp byte ptr ss:[di - 2], 0
0256  74 14           je 0x26c
0258  C4 7E 08        les di, ptr [bp + 8]
025B  06              push es
025C  57              push di
025D  FF 76 06        push word ptr [bp + 6]
0260  9A D1 1A 4B 21  call far 214B:1AD1
0265  8B 7E 04        mov di, word ptr [bp + 4]
0268  36 88 45 FE     mov byte ptr ss:[di - 2], al
loc_026C:
026C  89 EC           mov sp, bp
026E  5D              pop bp
026F  C2 08 00        ret 8
; data (not reached as code), 9 bytes
0272                  pstr ' game...'

; ---- routine 1771:027B  (found by: call)
sub_027B:
027B  55              push bp
027C  89 E5           mov bp, sp
027E  81 EC 04 01     sub sp, 0x104
0282  C6 46 FE 01     mov byte ptr [bp - 2], 1
0286  B0 19           mov al, 0x19
0288  50              push ax
0289  8D BE FC FE     lea di, [bp - 0x104]
028D  16              push ss
028E  57              push di
028F  8A 46 04        mov al, byte ptr [bp + 4]
0292  98              cwde
0293  BA 0B 00        mov dx, 0xb
0296  F7 E2           mul dx
0298  8B F8           mov di, ax
029A  81 C7 22 0C     add di, 0xc22
029E  1E              push ds
029F  57              push di
02A0  9A 2A 06 E4 23  call far 23E4:062A
02A5  BF 72 02        mov di, 0x272
02A8  0E              push cs
02A9  57              push di
02AA  9A B7 06 E4 23  call far 23E4:06B7
02AF  BF 6A A9        mov di, 0xa96a
02B2  1E              push ds
02B3  57              push di
02B4  9A 50 03 4B 21  call far 214B:0350
02B9  C4 3E 68 9B     les di, ptr [0x9b68]
02BD  06              push es
02BE  57              push di
02BF  B8 10 08        mov ax, 0x810
02C2  50              push ax
02C3  55              push bp
02C4  E8 6B FF        call 0x232
02C7  C4 3E 6C 9B     les di, ptr [0x9b6c]
02CB  06              push es
02CC  57              push di
02CD  B8 87 83        mov ax, 0x8387
02D0  50              push ax
02D1  55              push bp
02D2  E8 5D FF        call 0x232
02D5  C4 3E 70 9B     les di, ptr [0x9b70]
02D9  06              push es
02DA  57              push di
02DB  B8 F5 0B        mov ax, 0xbf5
02DE  50              push ax
02DF  55              push bp
02E0  E8 4F FF        call 0x232
02E3  C4 3E 74 9B     les di, ptr [0x9b74]
02E7  06              push es
02E8  57              push di
02E9  B8 DB 06        mov ax, 0x6db
02EC  50              push ax
02ED  55              push bp
02EE  E8 41 FF        call 0x232
02F1  C4 3E 78 9B     les di, ptr [0x9b78]
02F5  06              push es
02F6  57              push di
02F7  B8 87 00        mov ax, 0x87
02FA  50              push ax
02FB  55              push bp
02FC  E8 33 FF        call 0x232
02FF  BF 80 9D        mov di, 0x9d80
0302  1E              push ds
0303  57              push di
0304  B8 83 01        mov ax, 0x183
0307  50              push ax
0308  55              push bp
0309  E8 26 FF        call 0x232
030C  BF 7C 9B        mov di, 0x9b7c
030F  1E              push ds
0310  57              push di
0311  B8 81 00        mov ax, 0x81
0314  50              push ax
0315  55              push bp
0316  E8 19 FF        call 0x232
0319  BF FD 9B        mov di, 0x9bfd
031C  1E              push ds
031D  57              push di
031E  B8 81 00        mov ax, 0x81
0321  50              push ax
0322  55              push bp
0323  E8 0C FF        call 0x232
0326  BF 7E 9C        mov di, 0x9c7e
0329  1E              push ds
032A  57              push di
032B  B8 81 00        mov ax, 0x81
032E  50              push ax
032F  55              push bp
0330  E8 FF FE        call 0x232
0333  BF 03 9F        mov di, 0x9f03
0336  1E              push ds
0337  57              push di
0338  B8 14 0A        mov ax, 0xa14
033B  50              push ax
033C  55              push bp
033D  E8 F2 FE        call 0x232
0340  C4 3E 17 A9     les di, ptr [0xa917]
0344  06              push es
0345  57              push di
0346  B8 3F 60        mov ax, 0x603f
0349  50              push ax
034A  55              push bp
034B  E8 E4 FE        call 0x232
034E  C4 3E 1B A9     les di, ptr [0xa91b]
0352  06              push es
0353  57              push di
0354  B8 24 EF        mov ax, 0xef24
0357  50              push ax
0358  55              push bp
0359  E8 D6 FE        call 0x232
035C  C4 3E 23 A9     les di, ptr [0xa923]
0360  06              push es
0361  57              push di
0362  B8 0E 01        mov ax, 0x10e
0365  50              push ax
0366  55              push bp
0367  E8 C8 FE        call 0x232
036A  C4 3E 27 A9     les di, ptr [0xa927]
036E  06              push es
036F  57              push di
0370  B8 C2 03        mov ax, 0x3c2
0373  50              push ax
0374  55              push bp
0375  E8 BA FE        call 0x232
0378  C4 3E 1F A9     les di, ptr [0xa91f]
037C  06              push es
037D  57              push di
037E  B8 95 01        mov ax, 0x195
0381  50              push ax
0382  55              push bp
0383  E8 AC FE        call 0x232
0386  C4 3E 2B A9     les di, ptr [0xa92b]
038A  06              push es
038B  57              push di
038C  B8 48 4B        mov ax, 0x4b48
038F  50              push ax
0390  55              push bp
0391  E8 9E FE        call 0x232
0394  C4 3E 2F A9     les di, ptr [0xa92f]
0398  06              push es
0399  57              push di
039A  B8 48 24        mov ax, 0x2448
039D  50              push ax
039E  55              push bp
039F  E8 90 FE        call 0x232
03A2  BF FF 9C        mov di, 0x9cff
03A5  1E              push ds
03A6  57              push di
03A7  B8 81 00        mov ax, 0x81
03AA  50              push ax
03AB  55              push bp
03AC  E8 83 FE        call 0x232
03AF  C4 3E 33 A9     les di, ptr [0xa933]
03B3  06              push es
03B4  57              push di
03B5  B8 00 1C        mov ax, 0x1c00
03B8  50              push ax
03B9  55              push bp
03BA  E8 75 FE        call 0x232
03BD  C4 3E 37 A9     les di, ptr [0xa937]
03C1  06              push es
03C2  57              push di
03C3  B8 48 03        mov ax, 0x348
03C6  50              push ax
03C7  55              push bp
03C8  E8 67 FE        call 0x232
03CB  C4 3E 3B A9     les di, ptr [0xa93b]
03CF  06              push es
03D0  57              push di
03D1  B8 48 03        mov ax, 0x348
03D4  50              push ax
03D5  55              push bp
03D6  E8 59 FE        call 0x232
03D9  C4 3E 3F A9     les di, ptr [0xa93f]
03DD  06              push es
03DE  57              push di
03DF  B8 E0 01        mov ax, 0x1e0
03E2  50              push ax
03E3  55              push bp
03E4  E8 4B FE        call 0x232
03E7  9A 36 1A 4B 21  call far 214B:1A36
03EC  8A 46 FE        mov al, byte ptr [bp - 2]
03EF  88 46 FF        mov byte ptr [bp - 1], al
03F2  8A 46 FF        mov al, byte ptr [bp - 1]
03F5  89 EC           mov sp, bp
03F7  5D              pop bp
03F8  C2 02 00        ret 2
; data (not reached as code), 4 bytes
03FB                  pstr '.GL'

; ---- routine 1771:03FF  (found by: call)
sub_03FF:
03FF  55              push bp
0400  89 E5           mov bp, sp
0402  BF C4 0C        mov di, 0xcc4
0405  1E              push ds
0406  57              push di
0407  BF 6E A9        mov di, 0xa96e
040A  1E              push ds
040B  57              push di
040C  9A 29 03 4B 21  call far 214B:0329
0411  B0 05           mov al, 5
0413  50              push ax
0414  BF FB 03        mov di, 0x3fb
0417  0E              push cs
0418  57              push di
0419  B0 19           mov al, 0x19
041B  50              push ax
041C  B0 2D           mov al, 0x2d
041E  50              push ax
041F  BF 6E A9        mov di, 0xa96e
0422  1E              push ds
0423  57              push di
0424  9A C8 02 4B 21  call far 214B:02C8
0429  C4 3E 6E A9     les di, ptr [0xa96e]
042D  81 C7 00 0F     add di, 0xf00
0431  06              push es
0432  57              push di
0433  C4 3E 6A A9     les di, ptr [0xa96a]
0437  81 C7 00 0F     add di, 0xf00
043B  06              push es
043C  57              push di
043D  B8 A0 00        mov ax, 0xa0
0440  50              push ax
0441  9A 3C 00 4B 21  call far 214B:003C
0446  BF 72 0C        mov di, 0xc72
0449  1E              push ds
044A  57              push di
044B  B0 50           mov al, 0x50
044D  50              push ax
044E  B0 24           mov al, 0x24
0450  50              push ax
0451  B0 2D           mov al, 0x2d
0453  50              push ax
0454  B0 19           mov al, 0x19
0456  50              push ax
0457  9A 86 10 4B 21  call far 214B:1086
045C  89 EC           mov sp, bp
045E  5D              pop bp
045F  C3              ret
; data (not reached as code), 32 bytes
0460                  pstr 'Finding saved games...'
0477                  pstr '*.GL'
047C                  pstr '.GL'

; ---- routine 1771:0480  (found by: call)
sub_0480:
0480  55              push bp
0481  89 E5           mov bp, sp
0483  81 EC E6 01     sub sp, 0x1e6
0487  B0 19           mov al, 0x19
0489  50              push ax
048A  BF 60 04        mov di, 0x460
048D  0E              push cs
048E  57              push di
048F  BF 6A A9        mov di, 0xa96a
0492  1E              push ds
0493  57              push di
0494  9A 50 03 4B 21  call far 214B:0350
0499  31 C0           xor ax, ax
049B  89 46 FE        mov word ptr [bp - 2], ax
049E  BF 77 04        mov di, 0x477
04A1  0E              push cs
04A2  57              push di
04A3  B8 20 00        mov ax, 0x20
04A6  50              push ax
04A7  8D 7E CF        lea di, [bp - 0x31]
04AA  16              push ss
04AB  57              push di
04AC  9A DE 00 5C 23  call far 235C:00DE
loc_04B1:
04B1  83 3E A6 AA 00  cmp word ptr [0xaaa6], 0
04B6  75 53           jne 0x50b
04B8  83 7E FE 14     cmp word ptr [bp - 2], 0x14
04BC  73 4D           jae 0x50b
04BE  FF 46 FE        inc word ptr [bp - 2]
04C1  8D BE 1B FE     lea di, [bp - 0x1e5]
04C5  16              push ss
04C6  57              push di
04C7  8D 7E ED        lea di, [bp - 0x13]
04CA  16              push ss
04CB  57              push di
04CC  B8 01 00        mov ax, 1
04CF  50              push ax
04D0  BF 7C 04        mov di, 0x47c
04D3  0E              push cs
04D4  57              push di
04D5  8D 7E ED        lea di, [bp - 0x13]
04D8  16              push ss
04D9  57              push di
04DA  9A E3 06 E4 23  call far 23E4:06E3
04DF  48              dec ax
04E0  50              push ax
04E1  9A 76 06 E4 23  call far 23E4:0676
04E6  8B 46 FE        mov ax, word ptr [bp - 2]
04E9  BA 09 00        mov dx, 9
04EC  F7 E2           mul dx
04EE  8B F8           mov di, ax
04F0  8D BB 12 FF     lea di, [bp + di - 0xee]
04F4  16              push ss
04F5  57              push di
04F6  B8 08 00        mov ax, 8
04F9  50              push ax
04FA  9A 44 06 E4 23  call far 23E4:0644
04FF  8D 7E CF        lea di, [bp - 0x31]
0502  16              push ss
0503  57              push di
0504  9A 1C 01 5C 23  call far 235C:011C
0509  EB A6           jmp 0x4b1
loc_050B:
050B  83 7E FE 01     cmp word ptr [bp - 2], 1
050F  75 17           jne 0x528
0511  8D BE 1B FF     lea di, [bp - 0xe5]
0515  16              push ss
0516  57              push di
0517  BF 72 0C        mov di, 0xc72
051A  1E              push ds
051B  57              push di
051C  B8 50 00        mov ax, 0x50
051F  50              push ax
0520  9A 44 06 E4 23  call far 23E4:0644
0525  E9 24 01        jmp 0x64c
loc_0528:
0528  83 7E FE 00     cmp word ptr [bp - 2], 0
052C  75 03           jne 0x531
052E  E9 1B 01        jmp 0x64c
loc_0531:
0531  B8 19 00        mov ax, 0x19
0534  50              push ax
0535  9A F0 05 4B 21  call far 214B:05F0
loc_053A:
053A  BF D4 28        mov di, 0x28d4
053D  1E              push ds
053E  57              push di
053F  BF 6E A9        mov di, 0xa96e
0542  1E              push ds
0543  57              push di
0544  9A 29 03 4B 21  call far 214B:0329
0549  C7 46 FA 01 00  mov word ptr [bp - 6], 1
054E  A1 04 0D        mov ax, word ptr [0xd04]
0551  05 09 00        add ax, 9
0554  89 86 19 FF     mov word ptr [bp - 0xe7], ax
0558  A1 04 0D        mov ax, word ptr [0xd04]
055B  3B 86 19 FF     cmp ax, word ptr [bp - 0xe7]
055F  77 40           ja 0x5a1
0561  89 46 FC        mov word ptr [bp - 4], ax
0564  EB 03           jmp 0x569
loc_0566:
0566  FF 46 FC        inc word ptr [bp - 4]
loc_0569:
0569  8B 46 FC        mov ax, word ptr [bp - 4]
056C  3B 46 FE        cmp ax, word ptr [bp - 2]
056F  77 27           ja 0x598
0571  FF 46 FA        inc word ptr [bp - 6]
0574  B0 02           mov al, 2
0576  50              push ax
0577  8B 46 FC        mov ax, word ptr [bp - 4]
057A  BA 09 00        mov dx, 9
057D  F7 E2           mul dx
057F  8B F8           mov di, ax
0581  8D BB 12 FF     lea di, [bp + di - 0xee]
0585  16              push ss
0586  57              push di
0587  8A 46 FA        mov al, byte ptr [bp - 6]
058A  50              push ax
058B  B0 1C           mov al, 0x1c
058D  50              push ax
058E  BF 6E A9        mov di, 0xa96e
0591  1E              push ds
0592  57              push di
0593  9A C8 02 4B 21  call far 214B:02C8
loc_0598:
0598  8B 46 FC        mov ax, word ptr [bp - 4]
059B  3B 86 19 FF     cmp ax, word ptr [bp - 0xe7]
059F  75 C5           jne 0x566
loc_05A1:
05A1  A1 02 0D        mov ax, word ptr [0xd02]
05A4  40              inc ax
05A5  50              push ax
05A6  B8 1B 00        mov ax, 0x1b
05A9  50              push ax
05AA  B8 0A 00        mov ax, 0xa
05AD  50              push ax
05AE  9A C5 13 4B 21  call far 214B:13C5
05B3  C4 3E 6E A9     les di, ptr [0xa96e]
05B7  06              push es
05B8  57              push di
05B9  C4 3E 6A A9     les di, ptr [0xa96a]
05BD  06              push es
05BE  57              push di
05BF  B8 A0 0F        mov ax, 0xfa0
05C2  50              push ax
05C3  9A 5D 02 E4 23  call far 23E4:025D
05C8  9A DD 08 4B 21  call far 214B:08DD
05CD  BF 02 0D        mov di, 0xd02
05D0  1E              push ds
05D1  57              push di
05D2  BF 04 0D        mov di, 0xd04
05D5  1E              push ds
05D6  57              push di
05D7  B8 0A 00        mov ax, 0xa
05DA  50              push ax
05DB  FF 76 FE        push word ptr [bp - 2]
05DE  9A B1 15 4B 21  call far 214B:15B1
05E3  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
05E8  75 25           jne 0x60f
05EA  A1 02 0D        mov ax, word ptr [0xd02]
05ED  03 06 04 0D     add ax, word ptr [0xd04]
05F1  48              dec ax
05F2  BA 09 00        mov dx, 9
05F5  F7 E2           mul dx
05F7  8B F8           mov di, ax
05F9  8D BB 12 FF     lea di, [bp + di - 0xee]
05FD  16              push ss
05FE  57              push di
05FF  BF 72 0C        mov di, 0xc72
0602  1E              push ds
0603  57              push di
0604  B8 50 00        mov ax, 0x50
0607  50              push ax
0608  9A 44 06 E4 23  call far 23E4:0644
060D  EB 40           jmp 0x64f
loc_060F:
060F  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
0614  74 03           je 0x619
0616  E9 21 FF        jmp 0x53a
loc_0619:
0619  BF D2 29        mov di, 0x29d2
061C  1E              push ds
061D  57              push di
061E  BF 6E A9        mov di, 0xa96e
0621  1E              push ds
0622  57              push di
0623  9A 29 03 4B 21  call far 214B:0329
0628  BF F2 26        mov di, 0x26f2
062B  1E              push ds
062C  57              push di
062D  BF 6E A9        mov di, 0xa96e
0630  1E              push ds
0631  57              push di
0632  9A 29 03 4B 21  call far 214B:0329
0637  C4 3E 6E A9     les di, ptr [0xa96e]
063B  06              push es
063C  57              push di
063D  C4 3E 6A A9     les di, ptr [0xa96a]
0641  06              push es
0642  57              push di
0643  B8 A0 0F        mov ax, 0xfa0
0646  50              push ax
0647  9A 5D 02 E4 23  call far 23E4:025D
loc_064C:
064C  E8 B0 FD        call 0x3ff
loc_064F:
064F  89 EC           mov sp, bp
0651  5D              pop bp
0652  C3              ret
; data (not reached as code), 4 bytes
0653                  pstr '.GL'

; ---- routine 1771:0657  (found by: call)
sub_0657:
0657  55              push bp
0658  89 E5           mov bp, sp
065A  81 EC 02 01     sub sp, 0x102
065E  80 7E 06 00     cmp byte ptr [bp + 6], 0
0662  74 09           je 0x66d
0664  9A 33 1C 4B 21  call far 214B:1C33
0669  08 C0           or al, al
066B  74 05           je 0x672
loc_066D:
066D  E8 8F FD        call 0x3ff
0670  EB 03           jmp 0x675
loc_0672:
0672  E8 0B FE        call 0x480
loc_0675:
0675  C6 46 FE 00     mov byte ptr [bp - 2], 0
0679  80 3E 77 A9 1B  cmp byte ptr [0xa977], 0x1b
067E  75 08           jne 0x688
0680  C7 06 65 A9 FF 00 mov word ptr [0xa965], 0xff
0686  EB 4C           jmp 0x6d4
loc_0688:
0688  80 7E 06 00     cmp byte ptr [bp + 6], 0
068C  74 24           je 0x6b2
068E  8D BE FE FE     lea di, [bp - 0x102]
0692  16              push ss
0693  57              push di
0694  BF 72 0C        mov di, 0xc72
0697  1E              push ds
0698  57              push di
0699  9A 2A 06 E4 23  call far 23E4:062A
069E  BF 53 06        mov di, 0x653
06A1  0E              push cs
06A2  57              push di
06A3  9A B7 06 E4 23  call far 23E4:06B7
06A8  9A F5 1B 4B 21  call far 214B:1BF5
06AD  88 46 FE        mov byte ptr [bp - 2], al
06B0  EB 22           jmp 0x6d4
loc_06B2:
06B2  8D BE FE FE     lea di, [bp - 0x102]
06B6  16              push ss
06B7  57              push di
06B8  BF 72 0C        mov di, 0xc72
06BB  1E              push ds
06BC  57              push di
06BD  9A 2A 06 E4 23  call far 23E4:062A
06C2  BF 53 06        mov di, 0x653
06C5  0E              push cs
06C6  57              push di
06C7  9A B7 06 E4 23  call far 23E4:06B7
06CC  9A B7 1B 4B 21  call far 214B:1BB7
06D1  88 46 FE        mov byte ptr [bp - 2], al
loc_06D4:
06D4  80 7E FE 00     cmp byte ptr [bp - 2], 0
06D8  74 0A           je 0x6e4
06DA  8A 46 06        mov al, byte ptr [bp + 6]
06DD  50              push ax
06DE  E8 9A FB        call 0x27b
06E1  88 46 FE        mov byte ptr [bp - 2], al
loc_06E4:
06E4  8A 46 FE        mov al, byte ptr [bp - 2]
06E7  88 46 FF        mov byte ptr [bp - 1], al
06EA  8A 46 FF        mov al, byte ptr [bp - 1]
06ED  89 EC           mov sp, bp
06EF  5D              pop bp
06F0  CA 02 00        retf 2

; ---- routine 1771:06F3  (found by: call)
sub_06F3:
06F3  55              push bp
06F4  89 E5           mov bp, sp
06F6  83 EC 02        sub sp, 2
06F9  9A 75 1E 4B 21  call far 214B:1E75
06FE  C6 06 68 79 04  mov byte ptr [0x7968], 4
loc_0703:
0703  A0 68 79        mov al, byte ptr [0x7968]
0706  30 E4           xor ah, ah
0708  D1 E0           shl ax, 1
070A  8B D0           mov dx, ax
070C  B8 7D 00        mov ax, 0x7d
070F  2B C2           sub ax, dx
0711  A3 66 79        mov word ptr [0x7966], ax
0714  C7 46 FE 01 00  mov word ptr [bp - 2], 1
0719  EB 03           jmp 0x71e
loc_071B:
071B  FF 46 FE        inc word ptr [bp - 2]
loc_071E:
071E  9A 23 07 4B 21  call far 214B:0723
0723  08 C0           or al, al
0725  74 05           je 0x72c
0727  E9 84 00        jmp 0x7ae
; data (not reached as code), 2 bytes
072A                  db EB 3B   ; .;
loc_072C:
072C  8B 46 FE        mov ax, word ptr [bp - 2]
072F  BA 03 00        mov dx, 3
0732  F7 E2           mul dx
0734  8B F8           mov di, ax
0736  8A 85 03 0D     mov al, byte ptr [di + 0xd03]
073A  30 E4           xor ah, ah
073C  05 02 00        add ax, 2
073F  50              push ax
0740  8B 46 FE        mov ax, word ptr [bp - 2]
0743  BA 03 00        mov dx, 3
0746  F7 E2           mul dx
0748  8B F8           mov di, ax
074A  8A 85 04 0D     mov al, byte ptr [di + 0xd04]
074E  30 E4           xor ah, ah
0750  50              push ax
0751  8B 46 FE        mov ax, word ptr [bp - 2]
0754  BA 03 00        mov dx, 3
0757  F7 E2           mul dx
0759  8B F8           mov di, ax
075B  8A 85 05 0D     mov al, byte ptr [di + 0xd05]
075F  30 E4           xor ah, ah
0761  50              push ax
0762  9A F1 1E 4B 21  call far 214B:1EF1
0767  83 7E FE 18     cmp word ptr [bp - 2], 0x18
076B  75 AE           jne 0x71b
076D  C7 06 66 79 19 00 mov word ptr [0x7966], 0x19
0773  C7 46 FE 02 00  mov word ptr [bp - 2], 2
0778  EB 03           jmp 0x77d
loc_077A:
077A  FF 46 FE        inc word ptr [bp - 2]
loc_077D:
077D  9A 23 07 4B 21  call far 214B:0723
0782  08 C0           or al, al
0784  74 04           je 0x78a
0786  EB 26           jmp 0x7ae
; data (not reached as code), 2 bytes
0788                  db EB 10   ; ..
loc_078A:
078A  B8 02 00        mov ax, 2
078D  50              push ax
078E  FF 76 FE        push word ptr [bp - 2]
0791  B8 01 00        mov ax, 1
0794  50              push ax
0795  9A F1 1E 4B 21  call far 214B:1EF1
079A  83 7E FE 0E     cmp word ptr [bp - 2], 0xe
079E  75 DA           jne 0x77a
07A0  FE 06 68 79     inc byte ptr [0x7968]
07A4  80 3E 68 79 0D  cmp byte ptr [0x7968], 0xd
07A9  74 03           je 0x7ae
07AB  E9 55 FF        jmp 0x703
loc_07AE:
07AE  89 EC           mov sp, bp
07B0  5D              pop bp
07B1  C2 02 00        ret 2

; ---- routine 1771:07B4  (found by: call)
sub_07B4:
07B4  55              push bp
07B5  89 E5           mov bp, sp
07B7  55              push bp
07B8  E8 38 FF        call 0x6f3
07BB  9A 8D 1E 4B 21  call far 214B:1E8D
07C0  89 EC           mov sp, bp
07C2  5D              pop bp
07C3  C3              ret
; data (not reached as code), 72 bytes
07C4                  pstr 'Do you want to load a saved game? (Y/N)'
07EC                  db 00 20 00 00 01 00 00 00 00 00 00 02 00 00 00 00   ; . ..............
07FC                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:080C  (found by: far)
sub_080C:
080C  55              push bp
080D  89 E5           mov bp, sp
080F  83 EC 02        sub sp, 2
0812  BF D2 29        mov di, 0x29d2
0815  1E              push ds
0816  57              push di
0817  BF 6E A9        mov di, 0xa96e
081A  1E              push ds
081B  57              push di
081C  9A 29 03 4B 21  call far 214B:0329
0821  BF F2 26        mov di, 0x26f2
0824  1E              push ds
0825  57              push di
0826  BF 6E A9        mov di, 0xa96e
0829  1E              push ds
082A  57              push di
082B  9A 29 03 4B 21  call far 214B:0329
0830  B0 19           mov al, 0x19
0832  50              push ax
0833  BF C4 07        mov di, 0x7c4
0836  0E              push cs
0837  57              push di
0838  BF 6E A9        mov di, 0xa96e
083B  1E              push ds
083C  57              push di
083D  9A 50 03 4B 21  call far 214B:0350
0842  C4 3E 6E A9     les di, ptr [0xa96e]
0846  06              push es
0847  57              push di
0848  C4 3E 6A A9     les di, ptr [0xa96a]
084C  06              push es
084D  57              push di
084E  B8 A0 0F        mov ax, 0xfa0
0851  50              push ax
0852  9A 5D 02 E4 23  call far 23E4:025D
0857  E8 5A FF        call 0x7b4
085A  9A DD 08 4B 21  call far 214B:08DD
085F  A0 76 A9        mov al, byte ptr [0xa976]
0862  50              push ax
0863  9A B2 19 E4 23  call far 23E4:19B2
0868  50              push ax
0869  BF EC 07        mov di, 0x7ec
086C  0E              push cs
086D  57              push di
086E  9A DF 08 E4 23  call far 23E4:08DF
0873  75 04           jne 0x879
0875  B0 00           mov al, 0
0877  EB 02           jmp 0x87b
loc_0879:
0879  B0 01           mov al, 1
loc_087B:
087B  88 46 FE        mov byte ptr [bp - 2], al
087E  80 7E FE 00     cmp byte ptr [bp - 2], 0
0882  74 17           je 0x89b
loc_0884:
0884  B0 01           mov al, 1
0886  50              push ax
0887  0E              push cs
0888  E8 CC FD        call 0x657
088B  08 C0           or al, al
088D  75 0C           jne 0x89b
088F  B0 01           mov al, 1
0891  50              push ax
0892  9A 69 18 4B 21  call far 214B:1869
0897  08 C0           or al, al
0899  75 E9           jne 0x884
loc_089B:
089B  80 7E FE 00     cmp byte ptr [bp - 2], 0
089F  75 07           jne 0x8a8
08A1  0E              push cs
08A2  E8 E5 F8        call 0x18a
08A5  E8 79 F7        call 0x21
loc_08A8:
08A8  8A 46 FE        mov al, byte ptr [bp - 2]
08AB  88 46 FF        mov byte ptr [bp - 1], al
08AE  8A 46 FF        mov al, byte ptr [bp - 1]
08B1  89 EC           mov sp, bp
08B3  5D              pop bp
08B4  CB              retf

; ---- routine 1771:08B5  (found by: call, far)
sub_08B5:
08B5  55              push bp
08B6  89 E5           mov bp, sp
loc_08B8:
08B8  B0 00           mov al, 0
08BA  50              push ax
08BB  0E              push cs
08BC  E8 98 FD        call 0x657
08BF  08 C0           or al, al
08C1  75 0C           jne 0x8cf
08C3  B0 00           mov al, 0
08C5  50              push ax
08C6  9A 69 18 4B 21  call far 214B:1869
08CB  08 C0           or al, al
08CD  75 E9           jne 0x8b8
loc_08CF:
08CF  89 EC           mov sp, bp
08D1  5D              pop bp
08D2  CB              retf
; data (not reached as code), 60 bytes
08D3                  pstr 'Are you sure you want to quit'
08F1                  pstr 'Do you want to save this game'

; ---- routine 1771:090F  (found by: far)
sub_090F:
090F  55              push bp
0910  89 E5           mov bp, sp
0912  BF D3 08        mov di, 0x8d3
0915  0E              push cs
0916  57              push di
0917  9A 66 05 4B 21  call far 214B:0566
091C  08 C0           or al, al
091E  75 02           jne 0x922
0920  EB 1F           jmp 0x941
loc_0922:
0922  B0 01           mov al, 1
0924  08 C0           or al, al
0926  74 12           je 0x93a
0928  BF F1 08        mov di, 0x8f1
092B  0E              push cs
092C  57              push di
092D  9A 66 05 4B 21  call far 214B:0566
0932  08 C0           or al, al
0934  74 04           je 0x93a
0936  0E              push cs
0937  E8 7B FF        call 0x8b5
loc_093A:
093A  31 C0           xor ax, ax
093C  9A D8 00 E4 23  call far 23E4:00D8
loc_0941:
0941  89 EC           mov sp, bp
0943  5D              pop bp
0944  CB              retf
; data (not reached as code), 2 bytes
0945                  db 01 20   ; . 

; ---- routine 1771:0947  (found by: call, far)
sub_0947:
0947  55              push bp
0948  89 E5           mov bp, sp
094A  81 EC 00 01     sub sp, 0x100
094E  8D BE 00 FF     lea di, [bp - 0x100]
0952  16              push ss
0953  57              push di
0954  8B 46 06        mov ax, word ptr [bp + 6]
0957  C4 3E 78 9B     les di, ptr [0x9b78]
095B  03 F8           add di, ax
095D  26 8A 05        mov al, byte ptr es:[di]
0960  50              push ax
0961  9A 5A 07 E4 23  call far 23E4:075A
0966  BF 45 09        mov di, 0x945
0969  0E              push cs
096A  57              push di
096B  9A B7 06 E4 23  call far 23E4:06B7
0970  8B 46 06        mov ax, word ptr [bp + 6]
0973  BA 0D 00        mov dx, 0xd
0976  F7 E2           mul dx
0978  C4 3E 74 9B     les di, ptr [0x9b74]
097C  03 F8           add di, ax
097E  06              push es
097F  57              push di
0980  9A B7 06 E4 23  call far 23E4:06B7
0985  C4 7E 08        les di, ptr [bp + 8]
0988  06              push es
0989  57              push di
098A  B8 0E 00        mov ax, 0xe
098D  50              push ax
098E  9A 44 06 E4 23  call far 23E4:0644
0993  89 EC           mov sp, bp
0995  5D              pop bp
0996  CA 02 00        retf 2
; data (not reached as code), 7 bytes
0999                  pstr 'Player'

; ---- routine 1771:09A0  (found by: call, far)
sub_09A0:
09A0  55              push bp
09A1  89 E5           mov bp, sp
09A3  81 EC 10 01     sub sp, 0x110
09A7  8B 46 0A        mov ax, word ptr [bp + 0xa]
09AA  BA 0D 00        mov dx, 0xd
09AD  F7 E2           mul dx
09AF  C4 3E 74 9B     les di, ptr [0x9b74]
09B3  03 F8           add di, ax
09B5  26 80 3D 00     cmp byte ptr es:[di], 0
09B9  75 30           jne 0x9eb
09BB  0E              push cs
09BC  E8 41 F6        call 0
09BF  8A D0           mov dl, al
09C1  8B 46 0A        mov ax, word ptr [bp + 0xa]
09C4  C4 3E 78 9B     les di, ptr [0x9b78]
09C8  03 F8           add di, ax
09CA  26 88 15        mov byte ptr es:[di], dl
09CD  BF 99 09        mov di, 0x999
09D0  0E              push cs
09D1  57              push di
09D2  8B 46 0A        mov ax, word ptr [bp + 0xa]
09D5  BA 0D 00        mov dx, 0xd
09D8  F7 E2           mul dx
09DA  C4 3E 74 9B     les di, ptr [0x9b74]
09DE  03 F8           add di, ax
09E0  06              push es
09E1  57              push di
09E2  B8 0C 00        mov ax, 0xc
09E5  50              push ax
09E6  9A 44 06 E4 23  call far 23E4:0644
loc_09EB:
09EB  8D BE F0 FE     lea di, [bp - 0x110]
09EF  16              push ss
09F0  57              push di
09F1  FF 76 0A        push word ptr [bp + 0xa]
09F4  0E              push cs
09F5  E8 4F FF        call 0x947
09F8  8D 7E F0        lea di, [bp - 0x10]
09FB  16              push ss
09FC  57              push di
09FD  B8 0F 00        mov ax, 0xf
0A00  50              push ax
0A01  9A 44 06 E4 23  call far 23E4:0644
0A06  8D 7E F0        lea di, [bp - 0x10]
0A09  16              push ss
0A0A  57              push di
0A0B  B0 0E           mov al, 0xe
0A0D  50              push ax
0A0E  8A 46 06        mov al, byte ptr [bp + 6]
0A11  50              push ax
0A12  8B 46 06        mov ax, word ptr [bp + 6]
0A15  05 0E 00        add ax, 0xe
0A18  50              push ax
0A19  8A 46 08        mov al, byte ptr [bp + 8]
0A1C  50              push ax
0A1D  9A 86 10 4B 21  call far 214B:1086
0A22  8D 7E F0        lea di, [bp - 0x10]
0A25  16              push ss
0A26  57              push di
0A27  8D BE F0 FE     lea di, [bp - 0x110]
0A2B  16              push ss
0A2C  57              push di
0A2D  FF 76 0A        push word ptr [bp + 0xa]
0A30  0E              push cs
0A31  E8 13 FF        call 0x947
0A34  9A 2F 07 E4 23  call far 23E4:072F
0A39  75 02           jne 0xa3d
0A3B  EB 64           jmp 0xaa1
loc_0A3D:
0A3D  8A 56 F1        mov dl, byte ptr [bp - 0xf]
0A40  8B 46 0A        mov ax, word ptr [bp + 0xa]
0A43  C4 3E 78 9B     les di, ptr [0x9b78]
0A47  03 F8           add di, ax
0A49  26 88 15        mov byte ptr es:[di], dl
0A4C  8D 7E F0        lea di, [bp - 0x10]
0A4F  16              push ss
0A50  57              push di
0A51  B8 01 00        mov ax, 1
0A54  50              push ax
0A55  80 7E F2 20     cmp byte ptr [bp - 0xe], 0x20
0A59  74 04           je 0xa5f
0A5B  B0 00           mov al, 0
0A5D  EB 02           jmp 0xa61
loc_0A5F:
0A5F  B0 01           mov al, 1
loc_0A61:
0A61  30 E4           xor ah, ah
0A63  40              inc ax
0A64  50              push ax
0A65  9A DB 07 E4 23  call far 23E4:07DB
0A6A  80 7E F0 00     cmp byte ptr [bp - 0x10], 0
0A6E  75 02           jne 0xa72
0A70  EB 2F           jmp 0xaa1
loc_0A72:
0A72  8A 46 F1        mov al, byte ptr [bp - 0xf]
0A75  50              push ax
0A76  9A B2 19 E4 23  call far 23E4:19B2
0A7B  88 46 F1        mov byte ptr [bp - 0xf], al
0A7E  8D 7E F0        lea di, [bp - 0x10]
0A81  16              push ss
0A82  57              push di
0A83  8B 46 0A        mov ax, word ptr [bp + 0xa]
0A86  BA 0D 00        mov dx, 0xd
0A89  F7 E2           mul dx
0A8B  C4 3E 74 9B     les di, ptr [0x9b74]
0A8F  03 F8           add di, ax
0A91  06              push es
0A92  57              push di
0A93  B8 0C 00        mov ax, 0xc
0A96  50              push ax
0A97  9A 44 06 E4 23  call far 23E4:0644
0A9C  C6 06 1A 0C 01  mov byte ptr [0xc1a], 1
loc_0AA1:
0AA1  89 EC           mov sp, bp
0AA3  5D              pop bp
0AA4  CA 06 00        retf 6

