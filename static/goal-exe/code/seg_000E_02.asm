; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 2 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:0A53  (found by: call)
sub_0A53:
0A53  55              push bp
0A54  89 E5           mov bp, sp
0A56  83 EC 02        sub sp, 2
0A59  8B 7E 04        mov di, word ptr [bp + 4]
0A5C  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
0A61  74 04           je 0xa67
0A63  B0 00           mov al, 0
0A65  EB 02           jmp 0xa69
loc_0A67:
0A67  B0 01           mov al, 1
loc_0A69:
0A69  98              cwde
0A6A  D1 E0           shl ax, 1
0A6C  8B 7E 04        mov di, word ptr [bp + 4]
0A6F  36 C4 7D 04     les di, ptr ss:[di + 4]
0A73  03 F8           add di, ax
0A75  26 FF 75 04     push word ptr es:[di + 4]
0A79  9A E7 10 71 17  call far 1771:10E7
0A7E  50              push ax
0A7F  8B 7E 04        mov di, word ptr [bp + 4]
0A82  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
0A86  98              cwde
0A87  D1 E0           shl ax, 1
0A89  8B 7E 04        mov di, word ptr [bp + 4]
0A8C  36 C4 7D 04     les di, ptr ss:[di + 4]
0A90  03 F8           add di, ax
0A92  26 FF 75 04     push word ptr es:[di + 4]
0A96  9A E7 10 71 17  call far 1771:10E7
0A9B  05 02 00        add ax, 2
0A9E  8B D0           mov dx, ax
0AA0  8B 7E 04        mov di, word ptr [bp + 4]
0AA3  36 80 7D FF 01  cmp byte ptr ss:[di - 1], 1
0AA8  74 04           je 0xaae
0AAA  B0 00           mov al, 0
0AAC  EB 02           jmp 0xab0
loc_0AAE:
0AAE  B0 01           mov al, 1
loc_0AB0:
0AB0  30 E4           xor ah, ah
0AB2  03 C2           add ax, dx
0AB4  5A              pop dx
0AB5  3B C2           cmp ax, dx
0AB7  7F 04           jg 0xabd
0AB9  B0 00           mov al, 0
0ABB  EB 02           jmp 0xabf
loc_0ABD:
0ABD  B0 01           mov al, 1
loc_0ABF:
0ABF  88 46 FF        mov byte ptr [bp - 1], al
0AC2  8A 46 FF        mov al, byte ptr [bp - 1]
0AC5  89 EC           mov sp, bp
0AC7  5D              pop bp
0AC8  C2 02 00        ret 2

; ---- routine 000E:0ACB  (found by: call)
sub_0ACB:
0ACB  55              push bp
0ACC  89 E5           mov bp, sp
0ACE  81 EC 00 01     sub sp, 0x100
0AD2  8D BE 00 FF     lea di, [bp - 0x100]
0AD6  16              push ss
0AD7  57              push di
0AD8  8B 7E 04        mov di, word ptr [bp + 4]
0ADB  36 8B 45 08     mov ax, word ptr ss:[di + 8]
0ADF  BA BF 00        mov dx, 0xbf
0AE2  F7 E2           mul dx
0AE4  C4 3E 17 A9     les di, ptr [0xa917]
0AE8  03 F8           add di, ax
0AEA  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0AEE  30 E4           xor ah, ah
0AF0  50              push ax
0AF1  9A 47 09 71 17  call far 1771:0947
0AF6  C4 7E 06        les di, ptr [bp + 6]
0AF9  06              push es
0AFA  57              push di
0AFB  B8 0F 00        mov ax, 0xf
0AFE  50              push ax
0AFF  9A 44 06 E4 23  call far 23E4:0644
0B04  89 EC           mov sp, bp
0B06  5D              pop bp
0B07  C2 02 00        ret 2

; ---- routine 000E:0B0A  (found by: call)
sub_0B0A:
0B0A  55              push bp
0B0B  89 E5           mov bp, sp
0B0D  8B 7E 04        mov di, word ptr [bp + 4]
0B10  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
0B15  74 04           je 0xb1b
0B17  B0 00           mov al, 0
0B19  EB 02           jmp 0xb1d
loc_0B1B:
0B1B  B0 01           mov al, 1
loc_0B1D:
0B1D  98              cwde
0B1E  D1 E0           shl ax, 1
0B20  8B 7E 04        mov di, word ptr [bp + 4]
0B23  36 C4 7D 04     les di, ptr ss:[di + 4]
0B27  03 F8           add di, ax
0B29  26 8B 45 04     mov ax, word ptr es:[di + 4]
0B2D  B1 04           mov cl, 4
0B2F  D3 E0           shl ax, cl
0B31  C4 3E 68 9B     les di, ptr [0x9b68]
0B35  03 F8           add di, ax
0B37  06              push es
0B38  57              push di
0B39  C4 7E 06        les di, ptr [bp + 6]
0B3C  06              push es
0B3D  57              push di
0B3E  B8 0F 00        mov ax, 0xf
0B41  50              push ax
0B42  9A 44 06 E4 23  call far 23E4:0644
0B47  89 EC           mov sp, bp
0B49  5D              pop bp
0B4A  C2 02 00        ret 2

; ---- routine 000E:0B4D  (found by: call)
sub_0B4D:
0B4D  55              push bp
0B4E  89 E5           mov bp, sp
0B50  8B 7E 04        mov di, word ptr [bp + 4]
0B53  36 8B 45 08     mov ax, word ptr ss:[di + 8]
0B57  B1 04           mov cl, 4
0B59  D3 E0           shl ax, cl
0B5B  C4 3E 68 9B     les di, ptr [0x9b68]
0B5F  03 F8           add di, ax
0B61  06              push es
0B62  57              push di
0B63  C4 7E 06        les di, ptr [bp + 6]
0B66  06              push es
0B67  57              push di
0B68  B8 0F 00        mov ax, 0xf
0B6B  50              push ax
0B6C  9A 44 06 E4 23  call far 23E4:0644
0B71  89 EC           mov sp, bp
0B73  5D              pop bp
0B74  C2 02 00        ret 2

; ---- routine 000E:0B77  (found by: call)
sub_0B77:
0B77  55              push bp
0B78  89 E5           mov bp, sp
0B7A  83 EC 06        sub sp, 6
0B7D  8B 7E 04        mov di, word ptr [bp + 4]
0B80  36 8B 45 08     mov ax, word ptr ss:[di + 8]
0B84  BA BF 00        mov dx, 0xbf
0B87  F7 E2           mul dx
0B89  C4 3E 17 A9     les di, ptr [0xa917]
0B8D  03 F8           add di, ax
0B8F  89 7E FA        mov word ptr [bp - 6], di
0B92  8C 46 FC        mov word ptr [bp - 4], es
0B95  C4 3E 23 A9     les di, ptr [0xa923]
0B99  26 83 7D 38 02  cmp word ptr es:[di + 0x38], 2
0B9E  72 3B           jb 0xbdb
0BA0  8B 7E 04        mov di, word ptr [bp + 4]
0BA3  36 C4 7D 04     les di, ptr ss:[di + 4]
0BA7  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
0BAC  74 2D           je 0xbdb
0BAE  9A D8 59 71 17  call far 1771:59D8
0BB3  08 C0           or al, al
0BB5  74 19           je 0xbd0
0BB7  C4 7E FA        les di, ptr [bp - 6]
0BBA  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0BBE  30 E4           xor ah, ah
0BC0  2D 80 00        sub ax, 0x80
0BC3  C4 3E 23 A9     les di, ptr [0xa923]
0BC7  03 F8           add di, ax
0BC9  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
0BCE  75 0B           jne 0xbdb
loc_0BD0:
0BD0  C4 7E FA        les di, ptr [bp - 6]
0BD3  26 80 BD BE 00 00 cmp byte ptr es:[di + 0xbe], 0
0BD9  76 07           jbe 0xbe2
loc_0BDB:
0BDB  31 C0           xor ax, ax
0BDD  89 46 FE        mov word ptr [bp - 2], ax
0BE0  EB 1C           jmp 0xbfe
loc_0BE2:
0BE2  C4 7E FA        les di, ptr [bp - 6]
0BE5  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0BE9  30 E4           xor ah, ah
0BEB  BA 03 00        mov dx, 3
0BEE  F7 E2           mul dx
0BF0  C4 3E 1F A9     les di, ptr [0xa91f]
0BF4  03 F8           add di, ax
0BF6  26 8A 45 02     mov al, byte ptr es:[di + 2]
0BFA  98              cwde
0BFB  89 46 FE        mov word ptr [bp - 2], ax
loc_0BFE:
0BFE  8B 46 FE        mov ax, word ptr [bp - 2]
0C01  89 EC           mov sp, bp
0C03  5D              pop bp
0C04  C2 02 00        ret 2
; data (not reached as code), 51 bytes
0C07                  pstr 'HACKER'
0C0E                  pstr 'SENT OFF'
0C17                  pstr 'MARCHING ORDERS'
0C27                  pstr 'FOR '
0C2C                  db 00   ; .
0C2D                  pstr 'RED CARD FOR'

; ---- routine 000E:0C3A  (found by: call)
sub_0C3A:
0C3A  55              push bp
0C3B  89 E5           mov bp, sp
0C3D  81 EC 00 02     sub sp, 0x200
0C41  B8 03 00        mov ax, 3
0C44  50              push ax
0C45  9A B1 06 4B 21  call far 214B:06B1
0C4A  3D 01 00        cmp ax, 1
0C4D  75 1F           jne 0xc6e
0C4F  BF 07 0C        mov di, 0xc07
0C52  0E              push cs
0C53  57              push di
0C54  8D BE 00 FF     lea di, [bp - 0x100]
0C58  16              push ss
0C59  57              push di
0C5A  8B 7E 04        mov di, word ptr [bp + 4]
0C5D  36 FF 75 04     push word ptr ss:[di + 4]
0C61  E8 E6 FC        call 0x94a
0C64  BF 0E 0C        mov di, 0xc0e
0C67  0E              push cs
0C68  57              push di
0C69  E8 C3 F9        call 0x62f
0C6C  EB 5B           jmp 0xcc9
loc_0C6E:
0C6E  3D 02 00        cmp ax, 2
0C71  75 34           jne 0xca7
0C73  BF 17 0C        mov di, 0xc17
0C76  0E              push cs
0C77  57              push di
0C78  8D BE 00 FE     lea di, [bp - 0x200]
0C7C  16              push ss
0C7D  57              push di
0C7E  BF 27 0C        mov di, 0xc27
0C81  0E              push cs
0C82  57              push di
0C83  9A 2A 06 E4 23  call far 23E4:062A
0C88  8D BE 00 FF     lea di, [bp - 0x100]
0C8C  16              push ss
0C8D  57              push di
0C8E  8B 7E 04        mov di, word ptr [bp + 4]
0C91  36 FF 75 04     push word ptr ss:[di + 4]
0C95  E8 B2 FC        call 0x94a
0C98  9A B7 06 E4 23  call far 23E4:06B7
0C9D  BF 2C 0C        mov di, 0xc2c
0CA0  0E              push cs
0CA1  57              push di
0CA2  E8 8A F9        call 0x62f
0CA5  EB 22           jmp 0xcc9
loc_0CA7:
0CA7  3D 03 00        cmp ax, 3
0CAA  75 1D           jne 0xcc9
0CAC  BF 2D 0C        mov di, 0xc2d
0CAF  0E              push cs
0CB0  57              push di
0CB1  8D BE 00 FF     lea di, [bp - 0x100]
0CB5  16              push ss
0CB6  57              push di
0CB7  8B 7E 04        mov di, word ptr [bp + 4]
0CBA  36 FF 75 04     push word ptr ss:[di + 4]
0CBE  E8 89 FC        call 0x94a
0CC1  BF 2C 0C        mov di, 0xc2c
0CC4  0E              push cs
0CC5  57              push di
0CC6  E8 66 F9        call 0x62f
loc_0CC9:
0CC9  89 EC           mov sp, bp
0CCB  5D              pop bp
0CCC  C2 02 00        ret 2
; data (not reached as code), 1290 bytes
0CCF                  pstr 'WORLD CHAMPIONS!'
0CE0                  pstr ' is'
0CE4                  pstr 'a national hero'
0CF4                  pstr 'WE ARE THE'
0CFF                  pstr 'CHAMPIONS!'
0D0A                  db 00   ; .
0D0B                  pstr 'HERE WE GO '
0D17                  pstr 'HERE WE GO!'
0D23                  db 02 21 20 01 21   ; .! .!
0D28                  pstr 'UTTER MAGIC!'
0D35                  pstr 'CAN DO IT!'
0D40                  pstr ' TOO CLOSE'
0D4B                  pstr 'FOR COMFORT'
0D57                  pstr 'TRIUMPH IN'
0D62                  pstr 'PENALTY SHOOTOUT'
0D73                  pstr 'IS USELESS'
0D7E                  pstr 'SCRAPE A WIN'
0D8B                  pstr 'LOOK RAGGED'
0D97                  pstr 'FAIL TO'
0D9F                  pstr 'CONVINCE'
0DA8                  pstr 'LOOK ORDINARY'
0DB6                  pstr 'BELOW PAR'
0DC0                  pstr 'PERFORMANCE'
0DCC                  pstr 'BY '
0DD0                  pstr 'STRUGGLE'
0DD9                  pstr 'MUST IMPROVE'
0DE6                  pstr 'DO THE JOB'
0DF1                  pstr 'JUST'
0DF6                  pstr ' IN'
0DFA                  pstr 'NERVE TINGLER'
0E08                  pstr 'A REAL NAIL-BITER'
0E1A                  pstr 'FROM '
0E20                  pstr 'A CRACKER'
0E2A                  pstr 'OF A MATCH'
0E35                  pstr 'SHOULD HAVE'
0E41                  pstr 'BEEN MORE'
0E4B                  pstr 'IN TRAINING'
0E57                  pstr 'EXCERCISE'
0E61                  pstr 'WIN AS'
0E68                  pstr 'EXPECTED'
0E71                  pstr 'NEED TO PLAY'
0E7E                  pstr 'BETTER'
0E85                  pstr 'LOOKING GOOD'
0E92                  pstr 'DOING FINE'
0E9D                  pstr 'A GRITTY'
0EA6                  pstr 'WIN COMFORTABLY'
0EB6                  pstr 'CONFIDENCE'
0EC1                  pstr 'BOOST FOR'
0ECB                  pstr 'IN IMPRESSIVE'
0ED9                  pstr 'FORM'
0EDE                  pstr 'DO THEIR STUFF'
0EED                  pstr 'SHOW THEM'
0EF7                  pstr 'DO IT IN STYLE'
0F06                  pstr 'WIN IN STYLE'
0F13                  pstr 'A GOOD RESULT'
0F21                  pstr 'FOR '
0F26                  pstr 'THIS IS WHAT'
0F33                  pstr 'WE WANT ,'
0F3D                  pstr 'TRIUMPH!'
0F46                  pstr 'HIT THE BIG TIME'
0F57                  pstr 'DESTROY'
0F5F                  pstr 'STORM TO VICTORY'
0F70                  pstr 'IMPRESS'
0F78                  pstr 'SIMPLY STUNNING!'
0F89                  pstr 'STANDING OVATION'
0F9A                  pstr 'FOR OUR LADS'
0FA7                  pstr ' GOAL BONANZA'
0FB5                  pstr 'GOALS GALORE'
0FC2                  pstr 'ROMP HOME'
0FCC                  pstr 'WALKS ON WATER'
0FDB                  pstr 'SO NEAR'
0FE3                  pstr 'AND YET'
0FEB                  pstr 'SO FAR!'
0FF3                  pstr 'BETTER LUCK'
0FFF                  pstr 'NEXT TIME'
1009                  pstr 'WORLD CUP'
1013                  pstr 'HOPES DASHED!'
1021                  pstr 'TRIP UP!'
102A                  pstr 'DISAPPOINTING'
1038                  pstr 'LACKING'
1040                  pstr 'HOLD ON'
1048                  pstr 'FORCE A DRAW'
1055                  pstr 'GAMES'
105B                  pstr 'WITHOUT A WIN'
1069                  pstr 'IS LUCKY TO'
1075                  pstr 'KEEP HIS JOB'
1082                  pstr 'IS OUT OF'
108C                  pstr 'HIS DEPTH'
1096                  pstr 'THIS MUST BE'
10A3                  pstr 'THE END FOR'
10AF                  pstr 'GOODBYE'
10B7                  pstr ',AND'
10BC                  pstr 'GOOD RIDDANCE!'
10CB                  pstr 'DISGRACEFUL'
10D7                  pstr 'SHOWING BY'
10E2                  pstr 'FANS WALK OUT'
10F0                  pstr 'MUST DO BETTER'
10FF                  pstr 'BLACK DAY FOR'
110D                  pstr 'SCRAPPY'
1115                  pstr 'PERFORMANCE BY'
1124                  pstr 'FALL APART'
112F                  pstr 'DISMAL EFFORT BY'
1140                  pstr 'FAIL MISERABLY'
114F                  pstr 'GUTSY'
1155                  pstr 'UNLUCKY TO LOSE'
1165                  pstr 'FIGHT HARD'
1170                  pstr 'LOSE TOUGH'
117B                  pstr 'BATTLE'
1182                  pstr 'UNHAPPY WITH'
118F                  pstr 'WHAT A LOAD'
119B                  pstr 'OF RUBBISH'
11A6                  pstr 'SLAUGHTERED'
11B2                  pstr 'by '
11B6                  pstr 'NOT GOOD ENOUGH'
11C6                  pstr 'THRASHED'
11CF                  pstr 'DESTROYED'

; ---- routine 000E:11D9  (found by: call)
sub_11D9:
11D9  55              push bp
11DA  89 E5           mov bp, sp
11DC  81 EC 08 03     sub sp, 0x308
11E0  8B 7E 04        mov di, word ptr [bp + 4]
11E3  36 C4 7D 04     les di, ptr ss:[di + 4]
11E7  89 7E FC        mov word ptr [bp - 4], di
11EA  8C 46 FE        mov word ptr [bp - 2], es
11ED  8B 7E 04        mov di, word ptr [bp + 4]
11F0  36 8B 45 08     mov ax, word ptr ss:[di + 8]
11F4  BA BF 00        mov dx, 0xbf
11F7  F7 E2           mul dx
11F9  C4 3E 17 A9     les di, ptr [0xa917]
11FD  03 F8           add di, ax
11FF  89 7E F8        mov word ptr [bp - 8], di
1202  8C 46 FA        mov word ptr [bp - 6], es
1205  C4 7E FC        les di, ptr [bp - 4]
1208  26 8A 45 03     mov al, byte ptr es:[di + 3]
120C  8B 7E 04        mov di, word ptr [bp + 4]
120F  36 3A 45 FF     cmp al, byte ptr ss:[di - 1]
1213  74 03           je 0x1218
1215  E9 B4 07        jmp 0x19cc
loc_1218:
1218  C4 7E FC        les di, ptr [bp - 4]
121B  26 8A 45 02     mov al, byte ptr es:[di + 2]
121F  3C CB           cmp al, 0xcb
1221  75 26           jne 0x1249
1223  BF CF 0C        mov di, 0xccf
1226  0E              push cs
1227  57              push di
1228  8D BE F8 FE     lea di, [bp - 0x108]
122C  16              push ss
122D  57              push di
122E  FF 76 04        push word ptr [bp + 4]
1231  E8 97 F8        call 0xacb
1234  BF E0 0C        mov di, 0xce0
1237  0E              push cs
1238  57              push di
1239  9A B7 06 E4 23  call far 23E4:06B7
123E  BF E4 0C        mov di, 0xce4
1241  0E              push cs
1242  57              push di
1243  E8 E9 F3        call 0x62f
1246  E9 80 07        jmp 0x19c9
loc_1249:
1249  3C 67           cmp al, 0x67
124B  75 15           jne 0x1262
124D  BF F4 0C        mov di, 0xcf4
1250  0E              push cs
1251  57              push di
1252  BF FF 0C        mov di, 0xcff
1255  0E              push cs
1256  57              push di
1257  BF 0A 0D        mov di, 0xd0a
125A  0E              push cs
125B  57              push di
125C  E8 D0 F3        call 0x62f
125F  E9 67 07        jmp 0x19c9
loc_1262:
1262  3C C9           cmp al, 0xc9
1264  75 15           jne 0x127b
1266  BF 0B 0D        mov di, 0xd0b
1269  0E              push cs
126A  57              push di
126B  BF 0B 0D        mov di, 0xd0b
126E  0E              push cs
126F  57              push di
1270  BF 17 0D        mov di, 0xd17
1273  0E              push cs
1274  57              push di
1275  E8 B7 F3        call 0x62f
1278  E9 4E 07        jmp 0x19c9
loc_127B:
127B  3C 65           cmp al, 0x65
127D  75 37           jne 0x12b6
127F  8D BE F8 FE     lea di, [bp - 0x108]
1283  16              push ss
1284  57              push di
1285  FF 76 04        push word ptr [bp + 4]
1288  E8 C2 F8        call 0xb4d
128B  BF 23 0D        mov di, 0xd23
128E  0E              push cs
128F  57              push di
1290  9A B7 06 E4 23  call far 23E4:06B7
1295  8D BE F8 FD     lea di, [bp - 0x208]
1299  16              push ss
129A  57              push di
129B  FF 76 04        push word ptr [bp + 4]
129E  E8 AC F8        call 0xb4d
12A1  BF 26 0D        mov di, 0xd26
12A4  0E              push cs
12A5  57              push di
12A6  9A B7 06 E4 23  call far 23E4:06B7
12AB  BF 0A 0D        mov di, 0xd0a
12AE  0E              push cs
12AF  57              push di
12B0  E8 7C F3        call 0x62f
12B3  E9 13 07        jmp 0x19c9
loc_12B6:
12B6  3C C8           cmp al, 0xc8
12B8  75 15           jne 0x12cf
12BA  BF 28 0D        mov di, 0xd28
12BD  0E              push cs
12BE  57              push di
12BF  BF 0A 0D        mov di, 0xd0a
12C2  0E              push cs
12C3  57              push di
12C4  BF 0A 0D        mov di, 0xd0a
12C7  0E              push cs
12C8  57              push di
12C9  E8 63 F3        call 0x62f
12CC  E9 FA 06        jmp 0x19c9
loc_12CF:
12CF  3C 08           cmp al, 8
12D1  75 1C           jne 0x12ef
12D3  8D BE F8 FE     lea di, [bp - 0x108]
12D7  16              push ss
12D8  57              push di
12D9  FF 76 04        push word ptr [bp + 4]
12DC  E8 6E F8        call 0xb4d
12DF  BF 35 0D        mov di, 0xd35
12E2  0E              push cs
12E3  57              push di
12E4  BF 0A 0D        mov di, 0xd0a
12E7  0E              push cs
12E8  57              push di
12E9  E8 43 F3        call 0x62f
12EC  E9 DA 06        jmp 0x19c9
loc_12EF:
12EF  8B 7E 04        mov di, word ptr [bp + 4]
12F2  36 C4 7D 04     les di, ptr ss:[di + 4]
12F6  06              push es
12F7  57              push di
12F8  9A 60 5C 71 17  call far 1771:5C60
12FD  3D 03 00        cmp ax, 3
1300  73 1D           jae 0x131f
1302  8B 7E 04        mov di, word ptr [bp + 4]
1305  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
1309  98              cwde
130A  BA 0A 00        mov dx, 0xa
130D  F7 E2           mul dx
130F  8B F8           mov di, ax
1311  80 BD 86 7B 00  cmp byte ptr [di + 0x7b86], 0
1316  76 07           jbe 0x131f
1318  55              push bp
1319  E8 1E F9        call 0xc3a
131C  E9 AA 06        jmp 0x19c9
loc_131F:
131F  8B 7E 04        mov di, word ptr [bp + 4]
1322  36 C4 7D 04     les di, ptr ss:[di + 4]
1326  06              push es
1327  57              push di
1328  9A 60 5C 71 17  call far 1771:5C60
132D  09 C0           or ax, ax
132F  75 41           jne 0x1372
1331  FF 76 04        push word ptr [bp + 4]
1334  E8 A4 F6        call 0x9db
1337  08 C0           or al, al
1339  74 1B           je 0x1356
133B  8D BE F8 FE     lea di, [bp - 0x108]
133F  16              push ss
1340  57              push di
1341  FF 76 04        push word ptr [bp + 4]
1344  E8 C3 F7        call 0xb0a
1347  BF 40 0D        mov di, 0xd40
134A  0E              push cs
134B  57              push di
134C  BF 4B 0D        mov di, 0xd4b
134F  0E              push cs
1350  57              push di
1351  E8 DB F2        call 0x62f
1354  EB 19           jmp 0x136f
loc_1356:
1356  8D BE F8 FE     lea di, [bp - 0x108]
135A  16              push ss
135B  57              push di
135C  FF 76 04        push word ptr [bp + 4]
135F  E8 EB F7        call 0xb4d
1362  BF 57 0D        mov di, 0xd57
1365  0E              push cs
1366  57              push di
1367  BF 62 0D        mov di, 0xd62
136A  0E              push cs
136B  57              push di
136C  E8 C0 F2        call 0x62f
loc_136F:
136F  E9 57 06        jmp 0x19c9
loc_1372:
1372  8B 7E 04        mov di, word ptr [bp + 4]
1375  36 C4 7D 04     les di, ptr ss:[di + 4]
1379  06              push es
137A  57              push di
137B  8B 7E 04        mov di, word ptr [bp + 4]
137E  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
1382  50              push ax
1383  9A 1C B7 91 07  call far 0791:B71C
1388  3D 01 FF        cmp ax, 0xff01
138B  7C 4F           jl 0x13dc
138D  3D FB FF        cmp ax, 0xfffb
1390  7F 4A           jg 0x13dc
1392  B8 02 00        mov ax, 2
1395  50              push ax
1396  9A B1 06 4B 21  call far 214B:06B1
139B  3D 01 00        cmp ax, 1
139E  75 1B           jne 0x13bb
13A0  8D BE F8 FE     lea di, [bp - 0x108]
13A4  16              push ss
13A5  57              push di
13A6  FF 76 04        push word ptr [bp + 4]
13A9  E8 1F F7        call 0xacb
13AC  BF 73 0D        mov di, 0xd73
13AF  0E              push cs
13B0  57              push di
13B1  BF 0A 0D        mov di, 0xd0a
13B4  0E              push cs
13B5  57              push di
13B6  E8 76 F2        call 0x62f
13B9  EB 1E           jmp 0x13d9
loc_13BB:
13BB  3D 02 00        cmp ax, 2
13BE  75 19           jne 0x13d9
13C0  8D BE F8 FE     lea di, [bp - 0x108]
13C4  16              push ss
13C5  57              push di
13C6  FF 76 04        push word ptr [bp + 4]
13C9  E8 81 F7        call 0xb4d
13CC  BF 7E 0D        mov di, 0xd7e
13CF  0E              push cs
13D0  57              push di
13D1  BF 0A 0D        mov di, 0xd0a
13D4  0E              push cs
13D5  57              push di
13D6  E8 56 F2        call 0x62f
loc_13D9:
13D9  E9 ED 05        jmp 0x19c9
loc_13DC:
13DC  3D FC FF        cmp ax, 0xfffc
13DF  7C 6F           jl 0x1450
13E1  3D FE FF        cmp ax, 0xfffe
13E4  7F 6A           jg 0x1450
13E6  B8 03 00        mov ax, 3
13E9  50              push ax
13EA  9A B1 06 4B 21  call far 214B:06B1
13EF  3D 01 00        cmp ax, 1
13F2  75 1B           jne 0x140f
13F4  8D BE F8 FE     lea di, [bp - 0x108]
13F8  16              push ss
13F9  57              push di
13FA  FF 76 04        push word ptr [bp + 4]
13FD  E8 4D F7        call 0xb4d
1400  BF 8B 0D        mov di, 0xd8b
1403  0E              push cs
1404  57              push di
1405  BF 0A 0D        mov di, 0xd0a
1408  0E              push cs
1409  57              push di
140A  E8 22 F2        call 0x62f
140D  EB 3E           jmp 0x144d
loc_140F:
140F  3D 02 00        cmp ax, 2
1412  75 1B           jne 0x142f
1414  8D BE F8 FE     lea di, [bp - 0x108]
1418  16              push ss
1419  57              push di
141A  FF 76 04        push word ptr [bp + 4]
141D  E8 2D F7        call 0xb4d
1420  BF 97 0D        mov di, 0xd97
1423  0E              push cs
1424  57              push di
1425  BF 9F 0D        mov di, 0xd9f
1428  0E              push cs
1429  57              push di
142A  E8 02 F2        call 0x62f
142D  EB 1E           jmp 0x144d
loc_142F:
142F  3D 03 00        cmp ax, 3
1432  75 19           jne 0x144d
1434  8D BE F8 FE     lea di, [bp - 0x108]
1438  16              push ss
1439  57              push di
143A  FF 76 04        push word ptr [bp + 4]
143D  E8 0D F7        call 0xb4d
1440  BF A8 0D        mov di, 0xda8
1443  0E              push cs
1444  57              push di
1445  BF 0A 0D        mov di, 0xd0a
1448  0E              push cs
1449  57              push di
144A  E8 E2 F1        call 0x62f
loc_144D:
144D  E9 79 05        jmp 0x19c9
loc_1450:
1450  3D FF FF        cmp ax, 0xffff
1453  74 03           je 0x1458
1455  E9 7F 00        jmp 0x14d7
loc_1458:
1458  B8 03 00        mov ax, 3
145B  50              push ax
145C  9A B1 06 4B 21  call far 214B:06B1
1461  3D 01 00        cmp ax, 1
1464  75 30           jne 0x1496
1466  BF B6 0D        mov di, 0xdb6
1469  0E              push cs
146A  57              push di
146B  BF C0 0D        mov di, 0xdc0
146E  0E              push cs
146F  57              push di
1470  8D BE F8 FD     lea di, [bp - 0x208]
1474  16              push ss
1475  57              push di
1476  BF CC 0D        mov di, 0xdcc
1479  0E              push cs
147A  57              push di
147B  9A 2A 06 E4 23  call far 23E4:062A
1480  8D BE F8 FE     lea di, [bp - 0x108]
1484  16              push ss
1485  57              push di
1486  FF 76 04        push word ptr [bp + 4]
1489  E8 C1 F6        call 0xb4d
148C  9A B7 06 E4 23  call far 23E4:06B7
1491  E8 9B F1        call 0x62f
1494  EB 3E           jmp 0x14d4
loc_1496:
1496  3D 02 00        cmp ax, 2
1499  75 1B           jne 0x14b6
149B  8D BE F8 FE     lea di, [bp - 0x108]
149F  16              push ss
14A0  57              push di
14A1  FF 76 04        push word ptr [bp + 4]
14A4  E8 A6 F6        call 0xb4d
14A7  BF D0 0D        mov di, 0xdd0
14AA  0E              push cs
14AB  57              push di
14AC  BF 0A 0D        mov di, 0xd0a
14AF  0E              push cs
14B0  57              push di
14B1  E8 7B F1        call 0x62f
14B4  EB 1E           jmp 0x14d4
loc_14B6:
14B6  3D 03 00        cmp ax, 3
14B9  75 19           jne 0x14d4
14BB  8D BE F8 FE     lea di, [bp - 0x108]
14BF  16              push ss
14C0  57              push di
14C1  FF 76 04        push word ptr [bp + 4]
14C4  E8 86 F6        call 0xb4d
14C7  BF D9 0D        mov di, 0xdd9
14CA  0E              push cs
14CB  57              push di
14CC  BF 0A 0D        mov di, 0xd0a
14CF  0E              push cs
14D0  57              push di
14D1  E8 5B F1        call 0x62f
loc_14D4:
14D4  E9 F2 04        jmp 0x19c9
loc_14D7:
14D7  3D 00 00        cmp ax, 0
14DA  74 03           je 0x14df
14DC  E9 42 01        jmp 0x1621
loc_14DF:
14DF  8B 7E 04        mov di, word ptr [bp + 4]
14E2  36 C4 7D 04     les di, ptr ss:[di + 4]
14E6  06              push es
14E7  57              push di
14E8  9A 60 5C 71 17  call far 1771:5C60
14ED  3D 01 00        cmp ax, 1
14F0  74 03           je 0x14f5
14F2  E9 A2 00        jmp 0x1597
loc_14F5:
14F5  B8 04 00        mov ax, 4
14F8  50              push ax
14F9  9A B1 06 4B 21  call far 214B:06B1
14FE  3D 01 00        cmp ax, 1
1501  75 1B           jne 0x151e
1503  8D BE F8 FE     lea di, [bp - 0x108]
1507  16              push ss
1508  57              push di
1509  FF 76 04        push word ptr [bp + 4]
150C  E8 3E F6        call 0xb4d
150F  BF E6 0D        mov di, 0xde6
1512  0E              push cs
1513  57              push di
1514  BF F1 0D        mov di, 0xdf1
1517  0E              push cs
1518  57              push di
1519  E8 13 F1        call 0x62f
151C  EB 76           jmp 0x1594
loc_151E:
151E  3D 02 00        cmp ax, 2
1521  75 25           jne 0x1548
1523  8D BE F8 FE     lea di, [bp - 0x108]
1527  16              push ss
1528  57              push di
1529  FF 76 04        push word ptr [bp + 4]
152C  E8 1E F6        call 0xb4d
152F  BF F6 0D        mov di, 0xdf6
1532  0E              push cs
1533  57              push di
1534  9A B7 06 E4 23  call far 23E4:06B7
1539  BF FA 0D        mov di, 0xdfa
153C  0E              push cs
153D  57              push di
153E  BF 0A 0D        mov di, 0xd0a
1541  0E              push cs
1542  57              push di
1543  E8 E9 F0        call 0x62f
1546  EB 4C           jmp 0x1594
loc_1548:
1548  3D 03 00        cmp ax, 3
154B  75 30           jne 0x157d
154D  BF 08 0E        mov di, 0xe08
1550  0E              push cs
1551  57              push di
1552  8D BE F8 FD     lea di, [bp - 0x208]
1556  16              push ss
1557  57              push di
1558  BF 1A 0E        mov di, 0xe1a
155B  0E              push cs
155C  57              push di
155D  9A 2A 06 E4 23  call far 23E4:062A
1562  8D BE F8 FE     lea di, [bp - 0x108]
1566  16              push ss
1567  57              push di
1568  FF 76 04        push word ptr [bp + 4]
156B  E8 DF F5        call 0xb4d
156E  9A B7 06 E4 23  call far 23E4:06B7
1573  BF 0A 0D        mov di, 0xd0a
1576  0E              push cs
1577  57              push di
1578  E8 B4 F0        call 0x62f
157B  EB 17           jmp 0x1594
loc_157D:
157D  3D 04 00        cmp ax, 4
1580  75 12           jne 0x1594
1582  BF 20 0E        mov di, 0xe20
1585  0E              push cs
1586  57              push di
1587  BF 2A 0E        mov di, 0xe2a
158A  0E              push cs
158B  57              push di
158C  BF 0A 0D        mov di, 0xd0a
158F  0E              push cs
1590  57              push di
1591  E8 9B F0        call 0x62f
loc_1594:
1594  E9 87 00        jmp 0x161e
loc_1597:
1597  B8 04 00        mov ax, 4
159A  50              push ax
159B  9A B1 06 4B 21  call far 214B:06B1
15A0  3D 01 00        cmp ax, 1
15A3  75 1B           jne 0x15c0
15A5  BF 35 0E        mov di, 0xe35
15A8  0E              push cs
15A9  57              push di
15AA  BF 41 0E        mov di, 0xe41
15AD  0E              push cs
15AE  57              push di
15AF  8D BE F8 FE     lea di, [bp - 0x108]
15B3  16              push ss
15B4  57              push di
15B5  FF 76 04        push word ptr [bp + 4]
15B8  E8 10 F5        call 0xacb
15BB  E8 71 F0        call 0x62f
15BE  EB 5E           jmp 0x161e
loc_15C0:
15C0  3D 02 00        cmp ax, 2
15C3  75 1B           jne 0x15e0
15C5  8D BE F8 FE     lea di, [bp - 0x108]
15C9  16              push ss
15CA  57              push di
15CB  FF 76 04        push word ptr [bp + 4]
15CE  E8 7C F5        call 0xb4d
15D1  BF 4B 0E        mov di, 0xe4b
15D4  0E              push cs
15D5  57              push di
15D6  BF 57 0E        mov di, 0xe57
15D9  0E              push cs
15DA  57              push di
15DB  E8 51 F0        call 0x62f
15DE  EB 3E           jmp 0x161e
loc_15E0:
15E0  3D 03 00        cmp ax, 3
15E3  75 1B           jne 0x1600
15E5  8D BE F8 FE     lea di, [bp - 0x108]
15E9  16              push ss
15EA  57              push di
15EB  FF 76 04        push word ptr [bp + 4]
15EE  E8 5C F5        call 0xb4d
15F1  BF 61 0E        mov di, 0xe61
15F4  0E              push cs
15F5  57              push di
15F6  BF 68 0E        mov di, 0xe68
15F9  0E              push cs
15FA  57              push di
15FB  E8 31 F0        call 0x62f
15FE  EB 1E           jmp 0x161e
loc_1600:
1600  3D 04 00        cmp ax, 4
1603  75 19           jne 0x161e
1605  8D BE F8 FE     lea di, [bp - 0x108]
1609  16              push ss
160A  57              push di
160B  FF 76 04        push word ptr [bp + 4]
160E  E8 3C F5        call 0xb4d
1611  BF 71 0E        mov di, 0xe71
1614  0E              push cs
1615  57              push di
1616  BF 7E 0E        mov di, 0xe7e
1619  0E              push cs
161A  57              push di
161B  E8 11 F0        call 0x62f
loc_161E:
161E  E9 A8 03        jmp 0x19c9
loc_1621:
1621  3D 01 00        cmp ax, 1
1624  74 03           je 0x1629
1626  E9 C0 00        jmp 0x16e9
loc_1629:
1629  B8 05 00        mov ax, 5
162C  50              push ax
162D  9A B1 06 4B 21  call far 214B:06B1
1632  3D 01 00        cmp ax, 1
1635  75 1C           jne 0x1653
1637  8D BE F8 FE     lea di, [bp - 0x108]
163B  16              push ss
163C  57              push di
163D  FF 76 04        push word ptr [bp + 4]
1640  E8 0A F5        call 0xb4d
1643  BF 85 0E        mov di, 0xe85
1646  0E              push cs
1647  57              push di
1648  BF 0A 0D        mov di, 0xd0a
164B  0E              push cs
164C  57              push di
164D  E8 DF EF        call 0x62f
1650  E9 93 00        jmp 0x16e6
loc_1653:
1653  3D 02 00        cmp ax, 2
1656  75 1B           jne 0x1673
1658  8D BE F8 FE     lea di, [bp - 0x108]
165C  16              push ss
165D  57              push di
165E  FF 76 04        push word ptr [bp + 4]
1661  E8 67 F4        call 0xacb
1664  BF 92 0E        mov di, 0xe92
1667  0E              push cs
1668  57              push di
1669  BF 0A 0D        mov di, 0xd0a
166C  0E              push cs
166D  57              push di
166E  E8 BE EF        call 0x62f
1671  EB 73           jmp 0x16e6
loc_1673:
1673  3D 03 00        cmp ax, 3
1676  75 30           jne 0x16a8
1678  BF 9D 0E        mov di, 0xe9d
167B  0E              push cs
167C  57              push di
167D  BF C0 0D        mov di, 0xdc0
1680  0E              push cs
1681  57              push di
1682  8D BE F8 FD     lea di, [bp - 0x208]
1686  16              push ss
1687  57              push di
1688  BF CC 0D        mov di, 0xdcc
168B  0E              push cs
168C  57              push di
168D  9A 2A 06 E4 23  call far 23E4:062A
1692  8D BE F8 FE     lea di, [bp - 0x108]
1696  16              push ss
1697  57              push di
1698  FF 76 04        push word ptr [bp + 4]
169B  E8 AF F4        call 0xb4d
169E  9A B7 06 E4 23  call far 23E4:06B7
16A3  E8 89 EF        call 0x62f
16A6  EB 3E           jmp 0x16e6
loc_16A8:
16A8  3D 04 00        cmp ax, 4
16AB  75 1B           jne 0x16c8
16AD  8D BE F8 FE     lea di, [bp - 0x108]
16B1  16              push ss
16B2  57              push di
16B3  FF 76 04        push word ptr [bp + 4]
16B6  E8 94 F4        call 0xb4d
16B9  BF A6 0E        mov di, 0xea6
16BC  0E              push cs
16BD  57              push di
16BE  BF 0A 0D        mov di, 0xd0a
16C1  0E              push cs
16C2  57              push di
16C3  E8 69 EF        call 0x62f
16C6  EB 1E           jmp 0x16e6
loc_16C8:
16C8  3D 05 00        cmp ax, 5
16CB  75 19           jne 0x16e6
16CD  BF B6 0E        mov di, 0xeb6
16D0  0E              push cs
16D1  57              push di
16D2  BF C1 0E        mov di, 0xec1
16D5  0E              push cs
16D6  57              push di
16D7  8D BE F8 FE     lea di, [bp - 0x108]
16DB  16              push ss
16DC  57              push di
16DD  FF 76 04        push word ptr [bp + 4]
16E0  E8 6A F4        call 0xb4d
16E3  E8 49 EF        call 0x62f
loc_16E6:
16E6  E9 E0 02        jmp 0x19c9
loc_16E9:
16E9  3D 02 00        cmp ax, 2
16EC  74 03           je 0x16f1
16EE  E9 8A 00        jmp 0x177b
loc_16F1:
16F1  B8 04 00        mov ax, 4
16F4  50              push ax
16F5  9A B1 06 4B 21  call far 214B:06B1
16FA  3D 01 00        cmp ax, 1
16FD  75 1B           jne 0x171a
16FF  8D BE F8 FE     lea di, [bp - 0x108]
1703  16              push ss
1704  57              push di
1705  FF 76 04        push word ptr [bp + 4]
1708  E8 42 F4        call 0xb4d
170B  BF CB 0E        mov di, 0xecb
170E  0E              push cs
170F  57              push di
1710  BF D9 0E        mov di, 0xed9
1713  0E              push cs
1714  57              push di
1715  E8 17 EF        call 0x62f
1718  EB 5E           jmp 0x1778
loc_171A:
171A  3D 02 00        cmp ax, 2
171D  75 1B           jne 0x173a
171F  8D BE F8 FE     lea di, [bp - 0x108]
1723  16              push ss
1724  57              push di
1725  FF 76 04        push word ptr [bp + 4]
1728  E8 22 F4        call 0xb4d
172B  BF DE 0E        mov di, 0xede
172E  0E              push cs
172F  57              push di
1730  BF 0A 0D        mov di, 0xd0a
1733  0E              push cs
1734  57              push di
1735  E8 F7 EE        call 0x62f
1738  EB 3E           jmp 0x1778
loc_173A:
173A  3D 03 00        cmp ax, 3
173D  75 1B           jne 0x175a
173F  8D BE F8 FE     lea di, [bp - 0x108]
1743  16              push ss
1744  57              push di
1745  FF 76 04        push word ptr [bp + 4]
1748  E8 02 F4        call 0xb4d
174B  BF ED 0E        mov di, 0xeed
174E  0E              push cs
174F  57              push di
1750  BF 0A 0D        mov di, 0xd0a
1753  0E              push cs
1754  57              push di
1755  E8 D7 EE        call 0x62f
1758  EB 1E           jmp 0x1778
loc_175A:
175A  3D 04 00        cmp ax, 4
175D  75 19           jne 0x1778
175F  8D BE F8 FE     lea di, [bp - 0x108]
1763  16              push ss
1764  57              push di
1765  FF 76 04        push word ptr [bp + 4]
1768  E8 E2 F3        call 0xb4d
176B  BF F7 0E        mov di, 0xef7
176E  0E              push cs
176F  57              push di
1770  BF 0A 0D        mov di, 0xd0a
1773  0E              push cs
1774  57              push di
1775  E8 B7 EE        call 0x62f
loc_1778:
1778  E9 4E 02        jmp 0x19c9
loc_177B:
177B  3D 03 00        cmp ax, 3
177E  74 03           je 0x1783
1780  E9 C0 00        jmp 0x1843
loc_1783:
1783  B8 05 00        mov ax, 5
1786  50              push ax
1787  9A B1 06 4B 21  call far 214B:06B1
178C  3D 01 00        cmp ax, 1
178F  75 1C           jne 0x17ad
1791  8D BE F8 FE     lea di, [bp - 0x108]
1795  16              push ss
1796  57              push di
1797  FF 76 04        push word ptr [bp + 4]
179A  E8 B0 F3        call 0xb4d
179D  BF 06 0F        mov di, 0xf06
17A0  0E              push cs
17A1  57              push di
17A2  BF 0A 0D        mov di, 0xd0a
17A5  0E              push cs
17A6  57              push di
17A7  E8 85 EE        call 0x62f
17AA  E9 93 00        jmp 0x1840
loc_17AD:
17AD  3D 02 00        cmp ax, 2
17B0  75 30           jne 0x17e2
17B2  BF 13 0F        mov di, 0xf13
17B5  0E              push cs
17B6  57              push di
17B7  8D BE F8 FD     lea di, [bp - 0x208]
17BB  16              push ss
17BC  57              push di
17BD  BF 21 0F        mov di, 0xf21
17C0  0E              push cs
17C1  57              push di
17C2  9A 2A 06 E4 23  call far 23E4:062A
17C7  8D BE F8 FE     lea di, [bp - 0x108]
17CB  16              push ss
17CC  57              push di
17CD  FF 76 04        push word ptr [bp + 4]
17D0  E8 7A F3        call 0xb4d
17D3  9A B7 06 E4 23  call far 23E4:06B7
17D8  BF 0A 0D        mov di, 0xd0a
17DB  0E              push cs
17DC  57              push di
17DD  E8 4F EE        call 0x62f
17E0  EB 5E           jmp 0x1840
loc_17E2:
17E2  3D 03 00        cmp ax, 3
17E5  75 1B           jne 0x1802
17E7  BF 26 0F        mov di, 0xf26
17EA  0E              push cs
17EB  57              push di
17EC  BF 33 0F        mov di, 0xf33
17EF  0E              push cs
17F0  57              push di
17F1  8D BE F8 FE     lea di, [bp - 0x108]
17F5  16              push ss
17F6  57              push di
17F7  FF 76 04        push word ptr [bp + 4]
17FA  E8 CE F2        call 0xacb
17FD  E8 2F EE        call 0x62f
1800  EB 3E           jmp 0x1840
loc_1802:
1802  3D 04 00        cmp ax, 4
1805  75 1B           jne 0x1822
1807  8D BE F8 FE     lea di, [bp - 0x108]
180B  16              push ss
180C  57              push di
180D  FF 76 04        push word ptr [bp + 4]
1810  E8 3A F3        call 0xb4d
1813  BF 3D 0F        mov di, 0xf3d
1816  0E              push cs
1817  57              push di
1818  BF 0A 0D        mov di, 0xd0a
181B  0E              push cs
181C  57              push di
181D  E8 0F EE        call 0x62f
1820  EB 1E           jmp 0x1840
loc_1822:
1822  3D 05 00        cmp ax, 5
1825  75 19           jne 0x1840
1827  8D BE F8 FE     lea di, [bp - 0x108]
182B  16              push ss
182C  57              push di
182D  FF 76 04        push word ptr [bp + 4]
1830  E8 1A F3        call 0xb4d
1833  BF 46 0F        mov di, 0xf46
1836  0E              push cs
1837  57              push di
1838  BF 0A 0D        mov di, 0xd0a
183B  0E              push cs
183C  57              push di
183D  E8 EF ED        call 0x62f
loc_1840:
1840  E9 86 01        jmp 0x19c9
loc_1843:
1843  3D 04 00        cmp ax, 4
1846  7D 03           jge 0x184b
1848  E9 AB 00        jmp 0x18f6
loc_184B:
184B  3D 06 00        cmp ax, 6
184E  7E 03           jle 0x1853
1850  E9 A3 00        jmp 0x18f6
loc_1853:
1853  B8 05 00        mov ax, 5
1856  50              push ax
1857  9A B1 06 4B 21  call far 214B:06B1
185C  3D 01 00        cmp ax, 1
185F  75 22           jne 0x1883
1861  8D BE F8 FE     lea di, [bp - 0x108]
1865  16              push ss
1866  57              push di
1867  FF 76 04        push word ptr [bp + 4]
186A  E8 E0 F2        call 0xb4d
186D  BF 57 0F        mov di, 0xf57
1870  0E              push cs
1871  57              push di
1872  8D BE F8 FD     lea di, [bp - 0x208]
1876  16              push ss
1877  57              push di
1878  FF 76 04        push word ptr [bp + 4]
187B  E8 8C F2        call 0xb0a
187E  E8 AE ED        call 0x62f
1881  EB 70           jmp 0x18f3
loc_1883:
1883  3D 02 00        cmp ax, 2
1886  75 1B           jne 0x18a3
1888  8D BE F8 FE     lea di, [bp - 0x108]
188C  16              push ss
188D  57              push di
188E  FF 76 04        push word ptr [bp + 4]
1891  E8 B9 F2        call 0xb4d
1894  BF 5F 0F        mov di, 0xf5f
1897  0E              push cs
1898  57              push di
1899  BF 0A 0D        mov di, 0xd0a
189C  0E              push cs
189D  57              push di
189E  E8 8E ED        call 0x62f
18A1  EB 50           jmp 0x18f3
loc_18A3:
18A3  3D 03 00        cmp ax, 3
18A6  75 1B           jne 0x18c3
18A8  8D BE F8 FE     lea di, [bp - 0x108]
18AC  16              push ss
18AD  57              push di
18AE  FF 76 04        push word ptr [bp + 4]
18B1  E8 99 F2        call 0xb4d
18B4  BF 70 0F        mov di, 0xf70
18B7  0E              push cs
18B8  57              push di
18B9  BF 0A 0D        mov di, 0xd0a
18BC  0E              push cs
18BD  57              push di
18BE  E8 6E ED        call 0x62f
18C1  EB 30           jmp 0x18f3
loc_18C3:
18C3  3D 04 00        cmp ax, 4
18C6  75 14           jne 0x18dc
18C8  BF 78 0F        mov di, 0xf78
18CB  0E              push cs
18CC  57              push di
18CD  BF 0A 0D        mov di, 0xd0a
18D0  0E              push cs
18D1  57              push di
18D2  BF 0A 0D        mov di, 0xd0a
18D5  0E              push cs
18D6  57              push di
18D7  E8 55 ED        call 0x62f
18DA  EB 17           jmp 0x18f3
loc_18DC:
18DC  3D 05 00        cmp ax, 5
18DF  75 12           jne 0x18f3
18E1  BF 89 0F        mov di, 0xf89
18E4  0E              push cs
18E5  57              push di
18E6  BF 9A 0F        mov di, 0xf9a
18E9  0E              push cs
18EA  57              push di
18EB  BF 0A 0D        mov di, 0xd0a
18EE  0E              push cs
18EF  57              push di
18F0  E8 3C ED        call 0x62f
loc_18F3:
18F3  E9 D3 00        jmp 0x19c9
loc_18F6:
18F6  3D 07 00        cmp ax, 7
18F9  7D 03           jge 0x18fe
18FB  E9 CB 00        jmp 0x19c9
loc_18FE:
18FE  3D FF 00        cmp ax, 0xff
1901  7E 03           jle 0x1906
1903  E9 C3 00        jmp 0x19c9
loc_1906:
1906  8B 7E 04        mov di, word ptr [bp + 4]
1909  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
190D  98              cwde
190E  C4 7E FC        les di, ptr [bp - 4]
1911  03 F8           add di, ax
1913  26 80 3D 05     cmp byte ptr es:[di], 5
1917  76 73           jbe 0x198c
1919  9A FA 06 4B 21  call far 214B:06FA
191E  08 C0           or al, al
1920  74 56           je 0x1978
1922  8D BE F8 FE     lea di, [bp - 0x108]
1926  16              push ss
1927  57              push di
1928  8B 7E 04        mov di, word ptr [bp + 4]
192B  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
192F  98              cwde
1930  C4 7E FC        les di, ptr [bp - 4]
1933  03 F8           add di, ax
1935  26 8A 05        mov al, byte ptr es:[di]
1938  30 E4           xor ah, ah
193A  31 D2           xor dx, dx
193C  52              push dx
193D  50              push ax
193E  9A DA 09 4B 21  call far 214B:09DA
1943  BF A7 0F        mov di, 0xfa7
1946  0E              push cs
1947  57              push di
1948  9A B7 06 E4 23  call far 23E4:06B7
194D  8D BE F8 FC     lea di, [bp - 0x308]
1951  16              push ss
1952  57              push di
1953  BF 1A 0E        mov di, 0xe1a
1956  0E              push cs
1957  57              push di
1958  9A 2A 06 E4 23  call far 23E4:062A
195D  8D BE F8 FD     lea di, [bp - 0x208]
1961  16              push ss
1962  57              push di
1963  FF 76 04        push word ptr [bp + 4]
1966  E8 E4 F1        call 0xb4d
1969  9A B7 06 E4 23  call far 23E4:06B7
196E  BF 0A 0D        mov di, 0xd0a
1971  0E              push cs
1972  57              push di
1973  E8 B9 EC        call 0x62f
1976  EB 12           jmp 0x198a
loc_1978:
1978  BF B5 0F        mov di, 0xfb5
197B  0E              push cs
197C  57              push di
197D  BF 0A 0D        mov di, 0xd0a
1980  0E              push cs
1981  57              push di
1982  BF 0A 0D        mov di, 0xd0a
1985  0E              push cs
1986  57              push di
1987  E8 A5 EC        call 0x62f
loc_198A:
198A  EB 3D           jmp 0x19c9
loc_198C:
198C  9A FA 06 4B 21  call far 214B:06FA
1991  08 C0           or al, al
1993  74 1B           je 0x19b0
1995  8D BE F8 FE     lea di, [bp - 0x108]
1999  16              push ss
199A  57              push di
199B  FF 76 04        push word ptr [bp + 4]
199E  E8 AC F1        call 0xb4d
19A1  BF C2 0F        mov di, 0xfc2
19A4  0E              push cs
19A5  57              push di
19A6  BF 0A 0D        mov di, 0xd0a
19A9  0E              push cs
19AA  57              push di
19AB  E8 81 EC        call 0x62f
19AE  EB 19           jmp 0x19c9
loc_19B0:
19B0  8D BE F8 FE     lea di, [bp - 0x108]
19B4  16              push ss
19B5  57              push di
19B6  FF 76 04        push word ptr [bp + 4]
19B9  E8 0F F1        call 0xacb
19BC  BF CC 0F        mov di, 0xfcc
19BF  0E              push cs
19C0  57              push di
19C1  BF 0A 0D        mov di, 0xd0a
19C4  0E              push cs
19C5  57              push di
19C6  E8 66 EC        call 0x62f
loc_19C9:
19C9  E9 7B 05        jmp 0x1f47
loc_19CC:
19CC  C4 7E FC        les di, ptr [bp - 4]
19CF  26 8A 45 02     mov al, byte ptr es:[di + 2]
19D3  3C CB           cmp al, 0xcb
19D5  75 15           jne 0x19ec
19D7  BF DB 0F        mov di, 0xfdb
19DA  0E              push cs
19DB  57              push di
19DC  BF E3 0F        mov di, 0xfe3
19DF  0E              push cs
19E0  57              push di
19E1  BF EB 0F        mov di, 0xfeb
19E4  0E              push cs
19E5  57              push di
19E6  E8 46 EC        call 0x62f
19E9  E9 5B 05        jmp 0x1f47
loc_19EC:
19EC  3C 67           cmp al, 0x67
19EE  75 26           jne 0x1a16
19F0  BF F3 0F        mov di, 0xff3
19F3  0E              push cs
19F4  57              push di
19F5  BF FF 0F        mov di, 0xfff
19F8  0E              push cs
19F9  57              push di
19FA  8D BE F8 FE     lea di, [bp - 0x108]
19FE  16              push ss
19FF  57              push di
1A00  FF 76 04        push word ptr [bp + 4]
1A03  E8 C5 F0        call 0xacb
1A06  BF 26 0D        mov di, 0xd26
1A09  0E              push cs
1A0A  57              push di
1A0B  9A B7 06 E4 23  call far 23E4:06B7
1A10  E8 1C EC        call 0x62f
1A13  E9 31 05        jmp 0x1f47
loc_1A16:
1A16  3C C9           cmp al, 0xc9
1A18  74 08           je 0x1a22
1A1A  3C C8           cmp al, 0xc8
1A1C  74 04           je 0x1a22
1A1E  3C 08           cmp al, 8
1A20  75 15           jne 0x1a37
loc_1A22:
1A22  BF 09 10        mov di, 0x1009
1A25  0E              push cs
1A26  57              push di
1A27  BF 13 10        mov di, 0x1013
1A2A  0E              push cs
1A2B  57              push di
1A2C  BF 0A 0D        mov di, 0xd0a
1A2F  0E              push cs
1A30  57              push di
1A31  E8 FB EB        call 0x62f
1A34  E9 10 05        jmp 0x1f47
loc_1A37:
1A37  3C 65           cmp al, 0x65
1A39  75 1C           jne 0x1a57
1A3B  8D BE F8 FE     lea di, [bp - 0x108]
1A3F  16              push ss
1A40  57              push di
1A41  FF 76 04        push word ptr [bp + 4]
1A44  E8 06 F1        call 0xb4d
1A47  BF 21 10        mov di, 0x1021
1A4A  0E              push cs
1A4B  57              push di
1A4C  BF 0A 0D        mov di, 0xd0a
1A4F  0E              push cs
1A50  57              push di
1A51  E8 DB EB        call 0x62f
1A54  E9 F0 04        jmp 0x1f47
loc_1A57:
1A57  8B 7E 04        mov di, word ptr [bp + 4]
1A5A  36 C4 7D 04     les di, ptr ss:[di + 4]
1A5E  06              push es
1A5F  57              push di
1A60  9A 60 5C 71 17  call far 1771:5C60
1A65  09 C0           or ax, ax
1A67  74 03           je 0x1a6c
1A69  E9 F1 00        jmp 0x1b5d
loc_1A6C:
1A6C  FF 76 04        push word ptr [bp + 4]
1A6F  E8 69 EF        call 0x9db
1A72  08 C0           or al, al
1A74  74 4A           je 0x1ac0
1A76  B8 02 00        mov ax, 2
1A79  50              push ax
1A7A  9A B1 06 4B 21  call far 214B:06B1
1A7F  3D 01 00        cmp ax, 1
1A82  75 1B           jne 0x1a9f
1A84  8D BE F8 FE     lea di, [bp - 0x108]
1A88  16              push ss
1A89  57              push di
1A8A  FF 76 04        push word ptr [bp + 4]
1A8D  E8 BD F0        call 0xb4d
1A90  BF 97 0D        mov di, 0xd97
1A93  0E              push cs
1A94  57              push di
1A95  BF 9F 0D        mov di, 0xd9f
1A98  0E              push cs
1A99  57              push di
1A9A  E8 92 EB        call 0x62f
1A9D  EB 1E           jmp 0x1abd
loc_1A9F:
1A9F  3D 02 00        cmp ax, 2
1AA2  75 19           jne 0x1abd
1AA4  BF 2A 10        mov di, 0x102a
1AA7  0E              push cs
1AA8  57              push di
1AA9  8D BE F8 FE     lea di, [bp - 0x108]
1AAD  16              push ss
1AAE  57              push di
1AAF  FF 76 04        push word ptr [bp + 4]
1AB2  E8 98 F0        call 0xb4d
1AB5  BF 0A 0D        mov di, 0xd0a
1AB8  0E              push cs
1AB9  57              push di
1ABA  E8 72 EB        call 0x62f
loc_1ABD:
1ABD  E9 9A 00        jmp 0x1b5a
loc_1AC0:
1AC0  FF 76 04        push word ptr [bp + 4]
1AC3  E8 8D EF        call 0xa53
1AC6  08 C0           or al, al
1AC8  74 49           je 0x1b13
1ACA  B8 02 00        mov ax, 2
1ACD  50              push ax
1ACE  9A B1 06 4B 21  call far 214B:06B1
1AD3  3D 01 00        cmp ax, 1
1AD6  75 1B           jne 0x1af3
1AD8  8D BE F8 FE     lea di, [bp - 0x108]
1ADC  16              push ss
1ADD  57              push di
1ADE  FF 76 04        push word ptr [bp + 4]
1AE1  E8 69 F0        call 0xb4d
1AE4  BF D0 0D        mov di, 0xdd0
1AE7  0E              push cs
1AE8  57              push di
1AE9  BF 0A 0D        mov di, 0xd0a
1AEC  0E              push cs
1AED  57              push di
1AEE  E8 3E EB        call 0x62f
1AF1  EB 1E           jmp 0x1b11
loc_1AF3:
1AF3  3D 02 00        cmp ax, 2
1AF6  75 19           jne 0x1b11
1AF8  8D BE F8 FE     lea di, [bp - 0x108]
1AFC  16              push ss
1AFD  57              push di
1AFE  FF 76 04        push word ptr [bp + 4]
1B01  E8 49 F0        call 0xb4d
1B04  BF 38 10        mov di, 0x1038
1B07  0E              push cs
1B08  57              push di
1B09  BF 0A 0D        mov di, 0xd0a
1B0C  0E              push cs
1B0D  57              push di
1B0E  E8 1E EB        call 0x62f
loc_1B11:
1B11  EB 47           jmp 0x1b5a
loc_1B13:
1B13  B8 02 00        mov ax, 2
1B16  50              push ax
1B17  9A B1 06 4B 21  call far 214B:06B1
1B1C  3D 01 00        cmp ax, 1
1B1F  75 1B           jne 0x1b3c
1B21  8D BE F8 FE     lea di, [bp - 0x108]
1B25  16              push ss
1B26  57              push di
1B27  FF 76 04        push word ptr [bp + 4]
1B2A  E8 20 F0        call 0xb4d
1B2D  BF 40 10        mov di, 0x1040
1B30  0E              push cs
1B31  57              push di
1B32  BF 0A 0D        mov di, 0xd0a
1B35  0E              push cs
1B36  57              push di
1B37  E8 F5 EA        call 0x62f
1B3A  EB 1E           jmp 0x1b5a
loc_1B3C:
1B3C  3D 02 00        cmp ax, 2
1B3F  75 19           jne 0x1b5a
1B41  8D BE F8 FE     lea di, [bp - 0x108]
1B45  16              push ss
1B46  57              push di
1B47  FF 76 04        push word ptr [bp + 4]
1B4A  E8 00 F0        call 0xb4d
1B4D  BF 48 10        mov di, 0x1048
1B50  0E              push cs
1B51  57              push di
1B52  BF 0A 0D        mov di, 0xd0a
1B55  0E              push cs
1B56  57              push di
1B57  E8 D5 EA        call 0x62f
loc_1B5A:
1B5A  E9 EA 03        jmp 0x1f47
loc_1B5D:
1B5D  8B 7E 04        mov di, word ptr [bp + 4]
1B60  36 C4 7D 04     les di, ptr ss:[di + 4]
1B64  06              push es
1B65  57              push di
1B66  9A 60 5C 71 17  call far 1771:5C60
1B6B  3D 03 00        cmp ax, 3
1B6E  73 1D           jae 0x1b8d
1B70  8B 7E 04        mov di, word ptr [bp + 4]
1B73  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
1B77  98              cwde
1B78  BA 0A 00        mov dx, 0xa
1B7B  F7 E2           mul dx
1B7D  8B F8           mov di, ax
1B7F  80 BD 86 7B 00  cmp byte ptr [di + 0x7b86], 0
1B84  76 07           jbe 0x1b8d
1B86  55              push bp
1B87  E8 B0 F0        call 0xc3a
1B8A  E9 BA 03        jmp 0x1f47
loc_1B8D:
1B8D  FF 76 04        push word ptr [bp + 4]
1B90  E8 E4 EF        call 0xb77
1B93  3D FA FF        cmp ax, 0xfffa
1B96  75 4F           jne 0x1be7
1B98  C4 7E F8        les di, ptr [bp - 8]
1B9B  26 80 BD B8 00 03 cmp byte ptr es:[di + 0xb8], 3
1BA1  76 28           jbe 0x1bcb
1BA3  8D BE F8 FE     lea di, [bp - 0x108]
1BA7  16              push ss
1BA8  57              push di
1BA9  C4 7E F8        les di, ptr [bp - 8]
1BAC  26 8A 85 B8 00  mov al, byte ptr es:[di + 0xb8]
1BB1  30 E4           xor ah, ah
1BB3  31 D2           xor dx, dx
1BB5  52              push dx
1BB6  50              push ax
1BB7  9A DA 09 4B 21  call far 214B:09DA
1BBC  BF 55 10        mov di, 0x1055
1BBF  0E              push cs
1BC0  57              push di
1BC1  BF 5B 10        mov di, 0x105b
1BC4  0E              push cs
1BC5  57              push di
1BC6  E8 66 EA        call 0x62f
1BC9  EB 19           jmp 0x1be4
loc_1BCB:
1BCB  8D BE F8 FE     lea di, [bp - 0x108]
1BCF  16              push ss
1BD0  57              push di
1BD1  FF 76 04        push word ptr [bp + 4]
1BD4  E8 F4 EE        call 0xacb
1BD7  BF 69 10        mov di, 0x1069
1BDA  0E              push cs
1BDB  57              push di
1BDC  BF 75 10        mov di, 0x1075
1BDF  0E              push cs
1BE0  57              push di
1BE1  E8 4B EA        call 0x62f
loc_1BE4:
1BE4  E9 60 03        jmp 0x1f47
loc_1BE7:
1BE7  3D F9 FF        cmp ax, 0xfff9
1BEA  75 1C           jne 0x1c08
1BEC  8D BE F8 FE     lea di, [bp - 0x108]
1BF0  16              push ss
1BF1  57              push di
1BF2  FF 76 04        push word ptr [bp + 4]
1BF5  E8 D3 EE        call 0xacb
1BF8  BF 82 10        mov di, 0x1082
1BFB  0E              push cs
1BFC  57              push di
1BFD  BF 8C 10        mov di, 0x108c
1C00  0E              push cs
1C01  57              push di
1C02  E8 2A EA        call 0x62f
1C05  E9 3F 03        jmp 0x1f47
loc_1C08:
1C08  3D F6 FF        cmp ax, 0xfff6
1C0B  7C 21           jl 0x1c2e
1C0D  3D F8 FF        cmp ax, 0xfff8
1C10  7F 1C           jg 0x1c2e
1C12  BF 96 10        mov di, 0x1096
1C15  0E              push cs
1C16  57              push di
1C17  BF A3 10        mov di, 0x10a3
1C1A  0E              push cs
1C1B  57              push di
1C1C  8D BE F8 FE     lea di, [bp - 0x108]
1C20  16              push ss
1C21  57              push di
1C22  FF 76 04        push word ptr [bp + 4]
1C25  E8 A3 EE        call 0xacb
1C28  E8 04 EA        call 0x62f
1C2B  E9 19 03        jmp 0x1f47
loc_1C2E:
1C2E  3D 01 FF        cmp ax, 0xff01
1C31  7C 2B           jl 0x1c5e
1C33  3D F5 FF        cmp ax, 0xfff5
1C36  7F 26           jg 0x1c5e
1C38  BF AF 10        mov di, 0x10af
1C3B  0E              push cs
1C3C  57              push di
1C3D  8D BE F8 FE     lea di, [bp - 0x108]
1C41  16              push ss
1C42  57              push di
1C43  FF 76 04        push word ptr [bp + 4]
1C46  E8 82 EE        call 0xacb
1C49  BF B7 10        mov di, 0x10b7
1C4C  0E              push cs
1C4D  57              push di
1C4E  9A B7 06 E4 23  call far 23E4:06B7
1C53  BF BC 10        mov di, 0x10bc
1C56  0E              push cs
1C57  57              push di
1C58  E8 D4 E9        call 0x62f
1C5B  E9 E9 02        jmp 0x1f47
loc_1C5E:
1C5E  8B 7E 04        mov di, word ptr [bp + 4]
1C61  36 C4 7D 04     les di, ptr ss:[di + 4]
1C65  06              push es
1C66  57              push di
1C67  9A 60 5C 71 17  call far 1771:5C60
1C6C  3D 03 00        cmp ax, 3
1C6F  72 03           jb 0x1c74
1C71  E9 90 01        jmp 0x1e04
loc_1C74:
1C74  FF 76 04        push word ptr [bp + 4]
1C77  E8 61 ED        call 0x9db
1C7A  08 C0           or al, al
1C7C  75 03           jne 0x1c81
1C7E  E9 83 00        jmp 0x1d04
loc_1C81:
1C81  B8 04 00        mov ax, 4
1C84  50              push ax
1C85  9A B1 06 4B 21  call far 214B:06B1
1C8A  3D 01 00        cmp ax, 1
1C8D  75 1B           jne 0x1caa
1C8F  BF CB 10        mov di, 0x10cb
1C92  0E              push cs
1C93  57              push di
1C94  BF D7 10        mov di, 0x10d7
1C97  0E              push cs
1C98  57              push di
1C99  8D BE F8 FE     lea di, [bp - 0x108]
1C9D  16              push ss
1C9E  57              push di
1C9F  FF 76 04        push word ptr [bp + 4]
1CA2  E8 A8 EE        call 0xb4d
1CA5  E8 87 E9        call 0x62f
1CA8  EB 57           jmp 0x1d01
loc_1CAA:
1CAA  3D 02 00        cmp ax, 2
1CAD  75 14           jne 0x1cc3
1CAF  BF E2 10        mov di, 0x10e2
1CB2  0E              push cs
1CB3  57              push di
1CB4  BF 0A 0D        mov di, 0xd0a
1CB7  0E              push cs
1CB8  57              push di
1CB9  BF 0A 0D        mov di, 0xd0a
1CBC  0E              push cs
1CBD  57              push di
1CBE  E8 6E E9        call 0x62f
1CC1  EB 3E           jmp 0x1d01
loc_1CC3:
1CC3  3D 03 00        cmp ax, 3
1CC6  75 1B           jne 0x1ce3
1CC8  8D BE F8 FE     lea di, [bp - 0x108]
1CCC  16              push ss
1CCD  57              push di
1CCE  FF 76 04        push word ptr [bp + 4]
1CD1  E8 F7 ED        call 0xacb
1CD4  BF F0 10        mov di, 0x10f0
1CD7  0E              push cs
1CD8  57              push di
1CD9  BF 0A 0D        mov di, 0xd0a
1CDC  0E              push cs
1CDD  57              push di
1CDE  E8 4E E9        call 0x62f
1CE1  EB 1E           jmp 0x1d01
loc_1CE3:
1CE3  3D 04 00        cmp ax, 4
1CE6  75 19           jne 0x1d01
1CE8  BF FF 10        mov di, 0x10ff
1CEB  0E              push cs
1CEC  57              push di
1CED  8D BE F8 FE     lea di, [bp - 0x108]
1CF1  16              push ss
1CF2  57              push di
1CF3  FF 76 04        push word ptr [bp + 4]
1CF6  E8 54 EE        call 0xb4d
1CF9  BF 0A 0D        mov di, 0xd0a
1CFC  0E              push cs
1CFD  57              push di
1CFE  E8 2E E9        call 0x62f
loc_1D01:
1D01  E9 FD 00        jmp 0x1e01
loc_1D04:
1D04  FF 76 04        push word ptr [bp + 4]
1D07  E8 49 ED        call 0xa53
1D0A  08 C0           or al, al
1D0C  75 03           jne 0x1d11
1D0E  E9 89 00        jmp 0x1d9a
loc_1D11:
1D11  B8 04 00        mov ax, 4
1D14  50              push ax
1D15  9A B1 06 4B 21  call far 214B:06B1
1D1A  3D 01 00        cmp ax, 1
1D1D  75 1B           jne 0x1d3a
1D1F  BF 0D 11        mov di, 0x110d
1D22  0E              push cs
1D23  57              push di
1D24  BF 15 11        mov di, 0x1115
1D27  0E              push cs
1D28  57              push di
1D29  8D BE F8 FE     lea di, [bp - 0x108]
1D2D  16              push ss
1D2E  57              push di
1D2F  FF 76 04        push word ptr [bp + 4]
1D32  E8 18 EE        call 0xb4d
1D35  E8 F7 E8        call 0x62f
1D38  EB 5E           jmp 0x1d98
loc_1D3A:
1D3A  3D 02 00        cmp ax, 2
1D3D  75 1B           jne 0x1d5a
1D3F  8D BE F8 FE     lea di, [bp - 0x108]
1D43  16              push ss
1D44  57              push di
1D45  FF 76 04        push word ptr [bp + 4]
1D48  E8 02 EE        call 0xb4d
1D4B  BF 24 11        mov di, 0x1124
1D4E  0E              push cs
1D4F  57              push di
1D50  BF 0A 0D        mov di, 0xd0a
1D53  0E              push cs
1D54  57              push di
1D55  E8 D7 E8        call 0x62f
1D58  EB 3E           jmp 0x1d98
loc_1D5A:
1D5A  3D 03 00        cmp ax, 3
1D5D  75 1B           jne 0x1d7a
1D5F  BF 2F 11        mov di, 0x112f
1D62  0E              push cs
1D63  57              push di
1D64  8D BE F8 FE     lea di, [bp - 0x108]
1D68  16              push ss
1D69  57              push di
1D6A  FF 76 04        push word ptr [bp + 4]
1D6D  E8 DD ED        call 0xb4d
1D70  BF 0A 0D        mov di, 0xd0a
1D73  0E              push cs
1D74  57              push di
1D75  E8 B7 E8        call 0x62f
1D78  EB 1E           jmp 0x1d98
loc_1D7A:
1D7A  3D 04 00        cmp ax, 4
1D7D  75 19           jne 0x1d98
1D7F  8D BE F8 FE     lea di, [bp - 0x108]
1D83  16              push ss
1D84  57              push di
1D85  FF 76 04        push word ptr [bp + 4]
1D88  E8 C2 ED        call 0xb4d
1D8B  BF 40 11        mov di, 0x1140
1D8E  0E              push cs
1D8F  57              push di
1D90  BF 0A 0D        mov di, 0xd0a
1D93  0E              push cs
1D94  57              push di
1D95  E8 97 E8        call 0x62f
loc_1D98:
1D98  EB 67           jmp 0x1e01
loc_1D9A:
1D9A  B8 03 00        mov ax, 3
1D9D  50              push ax
1D9E  9A B1 06 4B 21  call far 214B:06B1
1DA3  3D 01 00        cmp ax, 1
1DA6  75 1B           jne 0x1dc3
1DA8  BF 4F 11        mov di, 0x114f
1DAB  0E              push cs
1DAC  57              push di
1DAD  8D BE F8 FE     lea di, [bp - 0x108]
1DB1  16              push ss
1DB2  57              push di
1DB3  FF 76 04        push word ptr [bp + 4]
1DB6  E8 94 ED        call 0xb4d
1DB9  BF 55 11        mov di, 0x1155
1DBC  0E              push cs
1DBD  57              push di
1DBE  E8 6E E8        call 0x62f
1DC1  EB 3E           jmp 0x1e01
loc_1DC3:
1DC3  3D 02 00        cmp ax, 2
1DC6  75 1B           jne 0x1de3
1DC8  8D BE F8 FE     lea di, [bp - 0x108]
1DCC  16              push ss
1DCD  57              push di
1DCE  FF 76 04        push word ptr [bp + 4]
1DD1  E8 79 ED        call 0xb4d
1DD4  BF 65 11        mov di, 0x1165
1DD7  0E              push cs
1DD8  57              push di
1DD9  BF 0A 0D        mov di, 0xd0a
1DDC  0E              push cs
1DDD  57              push di
1DDE  E8 4E E8        call 0x62f
1DE1  EB 1E           jmp 0x1e01
loc_1DE3:
1DE3  3D 03 00        cmp ax, 3
1DE6  75 19           jne 0x1e01
1DE8  8D BE F8 FE     lea di, [bp - 0x108]
1DEC  16              push ss
1DED  57              push di
1DEE  FF 76 04        push word ptr [bp + 4]
1DF1  E8 59 ED        call 0xb4d
1DF4  BF 70 11        mov di, 0x1170
1DF7  0E              push cs
1DF8  57              push di
1DF9  BF 7B 11        mov di, 0x117b
1DFC  0E              push cs
1DFD  57              push di
1DFE  E8 2E E8        call 0x62f
loc_1E01:
1E01  E9 43 01        jmp 0x1f47
loc_1E04:
1E04  FF 76 04        push word ptr [bp + 4]
1E07  E8 D1 EB        call 0x9db
1E0A  08 C0           or al, al
1E0C  74 4A           je 0x1e58
1E0E  B8 02 00        mov ax, 2
1E11  50              push ax
1E12  9A B1 06 4B 21  call far 214B:06B1
1E17  3D 01 00        cmp ax, 1
1E1A  75 22           jne 0x1e3e
1E1C  8D BE F8 FE     lea di, [bp - 0x108]
1E20  16              push ss
1E21  57              push di
1E22  FF 76 04        push word ptr [bp + 4]
1E25  E8 25 ED        call 0xb4d
1E28  BF 82 11        mov di, 0x1182
1E2B  0E              push cs
1E2C  57              push di
1E2D  8D BE F8 FD     lea di, [bp - 0x208]
1E31  16              push ss
1E32  57              push di
1E33  FF 76 04        push word ptr [bp + 4]
1E36  E8 92 EC        call 0xacb
1E39  E8 F3 E7        call 0x62f
1E3C  EB 17           jmp 0x1e55
loc_1E3E:
1E3E  3D 02 00        cmp ax, 2
1E41  75 12           jne 0x1e55
1E43  BF 8F 11        mov di, 0x118f
1E46  0E              push cs
1E47  57              push di
1E48  BF 9B 11        mov di, 0x119b
1E4B  0E              push cs
1E4C  57              push di
1E4D  BF 0A 0D        mov di, 0xd0a
1E50  0E              push cs
1E51  57              push di
1E52  E8 DA E7        call 0x62f
loc_1E55:
1E55  E9 EF 00        jmp 0x1f47
loc_1E58:
1E58  FF 76 04        push word ptr [bp + 4]
1E5B  E8 F5 EB        call 0xa53
1E5E  08 C0           or al, al
1E60  74 66           je 0x1ec8
1E62  B8 02 00        mov ax, 2
1E65  50              push ax
1E66  9A B1 06 4B 21  call far 214B:06B1
1E6B  3D 01 00        cmp ax, 1
1E6E  75 37           jne 0x1ea7
1E70  8D BE F8 FE     lea di, [bp - 0x108]
1E74  16              push ss
1E75  57              push di
1E76  FF 76 04        push word ptr [bp + 4]
1E79  E8 D1 EC        call 0xb4d
1E7C  BF A6 11        mov di, 0x11a6
1E7F  0E              push cs
1E80  57              push di
1E81  8D BE F8 FC     lea di, [bp - 0x308]
1E85  16              push ss
1E86  57              push di
1E87  BF B2 11        mov di, 0x11b2
1E8A  0E              push cs
1E8B  57              push di
1E8C  9A 2A 06 E4 23  call far 23E4:062A
1E91  8D BE F8 FD     lea di, [bp - 0x208]
1E95  16              push ss
1E96  57              push di
1E97  FF 76 04        push word ptr [bp + 4]
1E9A  E8 6D EC        call 0xb0a
1E9D  9A B7 06 E4 23  call far 23E4:06B7
1EA2  E8 8A E7        call 0x62f
1EA5  EB 1E           jmp 0x1ec5
loc_1EA7:
1EA7  3D 02 00        cmp ax, 2
1EAA  75 19           jne 0x1ec5
1EAC  BF B6 11        mov di, 0x11b6
1EAF  0E              push cs
1EB0  57              push di
1EB1  8D BE F8 FE     lea di, [bp - 0x108]
1EB5  16              push ss
1EB6  57              push di
1EB7  FF 76 04        push word ptr [bp + 4]
1EBA  E8 0E EC        call 0xacb
1EBD  BF 0A 0D        mov di, 0xd0a
1EC0  0E              push cs
1EC1  57              push di
1EC2  E8 6A E7        call 0x62f
loc_1EC5:
1EC5  E9 7F 00        jmp 0x1f47
loc_1EC8:
1EC8  B8 02 00        mov ax, 2
1ECB  50              push ax
1ECC  9A B1 06 4B 21  call far 214B:06B1
1ED1  3D 01 00        cmp ax, 1
1ED4  75 37           jne 0x1f0d
1ED6  8D BE F8 FE     lea di, [bp - 0x108]
1EDA  16              push ss
1EDB  57              push di
1EDC  FF 76 04        push word ptr [bp + 4]
1EDF  E8 6B EC        call 0xb4d
1EE2  BF C6 11        mov di, 0x11c6
1EE5  0E              push cs
1EE6  57              push di
1EE7  8D BE F8 FC     lea di, [bp - 0x308]
1EEB  16              push ss
1EEC  57              push di
1EED  BF CC 0D        mov di, 0xdcc
1EF0  0E              push cs
1EF1  57              push di
1EF2  9A 2A 06 E4 23  call far 23E4:062A
1EF7  8D BE F8 FD     lea di, [bp - 0x208]
1EFB  16              push ss
1EFC  57              push di
1EFD  FF 76 04        push word ptr [bp + 4]
1F00  E8 07 EC        call 0xb0a
1F03  9A B7 06 E4 23  call far 23E4:06B7
1F08  E8 24 E7        call 0x62f
1F0B  EB 3A           jmp 0x1f47
loc_1F0D:
1F0D  3D 02 00        cmp ax, 2
1F10  75 35           jne 0x1f47
1F12  8D BE F8 FE     lea di, [bp - 0x108]
1F16  16              push ss
1F17  57              push di
1F18  FF 76 04        push word ptr [bp + 4]
1F1B  E8 2F EC        call 0xb4d
1F1E  BF CF 11        mov di, 0x11cf
1F21  0E              push cs
1F22  57              push di
1F23  8D BE F8 FC     lea di, [bp - 0x308]
1F27  16              push ss
1F28  57              push di
1F29  BF CC 0D        mov di, 0xdcc
1F2C  0E              push cs
1F2D  57              push di
1F2E  9A 2A 06 E4 23  call far 23E4:062A
1F33  8D BE F8 FD     lea di, [bp - 0x208]
1F37  16              push ss
1F38  57              push di
1F39  FF 76 04        push word ptr [bp + 4]
1F3C  E8 CB EB        call 0xb0a
1F3F  9A B7 06 E4 23  call far 23E4:06B7
1F44  E8 E8 E6        call 0x62f
loc_1F47:
1F47  89 EC           mov sp, bp
1F49  5D              pop bp
1F4A  C2 02 00        ret 2

