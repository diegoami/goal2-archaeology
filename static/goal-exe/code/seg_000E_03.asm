; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 3 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:1F4D  (found by: call)
sub_1F4D:
1F4D  55              push bp
1F4E  89 E5           mov bp, sp
1F50  83 EC 02        sub sp, 2
1F53  8B 7E 04        mov di, word ptr [bp + 4]
1F56  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
1F5A  98              cwde
1F5B  BA 0A 00        mov dx, 0xa
1F5E  F7 E2           mul dx
1F60  8B F8           mov di, ax
1F62  8A 85 83 7B     mov al, byte ptr [di + 0x7b83]
1F66  30 E4           xor ah, ah
1F68  8B D8           mov bx, ax
1F6A  8B 7E 04        mov di, word ptr [bp + 4]
1F6D  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
1F72  74 04           je 0x1f78
1F74  B0 00           mov al, 0
1F76  EB 02           jmp 0x1f7a
loc_1F78:
1F78  B0 01           mov al, 1
loc_1F7A:
1F7A  98              cwde
1F7B  BA 0A 00        mov dx, 0xa
1F7E  F7 E2           mul dx
1F80  8B F8           mov di, ax
1F82  8A 85 82 7B     mov al, byte ptr [di + 0x7b82]
1F86  30 E4           xor ah, ah
1F88  8B C8           mov cx, ax
1F8A  8B 7E 04        mov di, word ptr [bp + 4]
1F8D  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
1F92  74 04           je 0x1f98
1F94  B0 00           mov al, 0
1F96  EB 02           jmp 0x1f9a
loc_1F98:
1F98  B0 01           mov al, 1
loc_1F9A:
1F9A  98              cwde
1F9B  BA 0A 00        mov dx, 0xa
1F9E  F7 E2           mul dx
1FA0  8B F8           mov di, ax
1FA2  8A 85 7E 7B     mov al, byte ptr [di + 0x7b7e]
1FA6  30 E4           xor ah, ah
1FA8  03 C1           add ax, cx
1FAA  03 C3           add ax, bx
1FAC  50              push ax
1FAD  8B 7E 04        mov di, word ptr [bp + 4]
1FB0  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
1FB5  74 04           je 0x1fbb
1FB7  B0 00           mov al, 0
1FB9  EB 02           jmp 0x1fbd
loc_1FBB:
1FBB  B0 01           mov al, 1
loc_1FBD:
1FBD  98              cwde
1FBE  BA 0A 00        mov dx, 0xa
1FC1  F7 E2           mul dx
1FC3  8B F8           mov di, ax
1FC5  8A 85 83 7B     mov al, byte ptr [di + 0x7b83]
1FC9  30 E4           xor ah, ah
1FCB  8B D8           mov bx, ax
1FCD  8B 7E 04        mov di, word ptr [bp + 4]
1FD0  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
1FD4  98              cwde
1FD5  BA 0A 00        mov dx, 0xa
1FD8  F7 E2           mul dx
1FDA  8B F8           mov di, ax
1FDC  8A 85 82 7B     mov al, byte ptr [di + 0x7b82]
1FE0  30 E4           xor ah, ah
1FE2  8B C8           mov cx, ax
1FE4  8B 7E 04        mov di, word ptr [bp + 4]
1FE7  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
1FEB  98              cwde
1FEC  BA 0A 00        mov dx, 0xa
1FEF  F7 E2           mul dx
1FF1  8B F8           mov di, ax
1FF3  8A 85 7E 7B     mov al, byte ptr [di + 0x7b7e]
1FF7  30 E4           xor ah, ah
1FF9  03 C1           add ax, cx
1FFB  03 C3           add ax, bx
1FFD  5A              pop dx
1FFE  3B C2           cmp ax, dx
2000  7F 04           jg 0x2006
2002  B0 00           mov al, 0
2004  EB 02           jmp 0x2008
loc_2006:
2006  B0 01           mov al, 1
loc_2008:
2008  88 46 FF        mov byte ptr [bp - 1], al
200B  8A 46 FF        mov al, byte ptr [bp - 1]
200E  89 EC           mov sp, bp
2010  5D              pop bp
2011  C2 02 00        ret 2
; data (not reached as code), 93 bytes
2014                  pstr ' AS'
2018                  pstr 'GET RID OF'
2023                  pstr ' AND'
2028                  pstr 'TRY '
202D                  pstr ' IS'
2031                  pstr 'MUCH BETTER THAN'
2042                  pstr 'MUST GO !'
204C                  pstr 'DESERVES'
2055                  pstr 'A GAME'
205C                  pstr 'MUST GET'
2065                  pstr 'IN THE TEAM'

; ---- routine 000E:2071  (found by: call)
sub_2071:
2071  55              push bp
2072  89 E5           mov bp, sp
2074  81 EC 12 03     sub sp, 0x312
2078  8B 7E 04        mov di, word ptr [bp + 4]
207B  36 8B 7D 04     mov di, word ptr ss:[di + 4]
207F  36 8B 45 08     mov ax, word ptr ss:[di + 8]
2083  BA BF 00        mov dx, 0xbf
2086  F7 E2           mul dx
2088  C4 3E 17 A9     les di, ptr [0xa917]
208C  03 F8           add di, ax
208E  89 7E F3        mov word ptr [bp - 0xd], di
2091  8C 46 F5        mov word ptr [bp - 0xb], es
2094  B8 0E 00        mov ax, 0xe
2097  50              push ax
2098  9A B1 06 4B 21  call far 214B:06B1
209D  48              dec ax
209E  A2 22 00        mov byte ptr [0x22], al
20A1  C6 46 FF 00     mov byte ptr [bp - 1], 0
20A5  C4 7E F3        les di, ptr [bp - 0xd]
20A8  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
20AC  30 E4           xor ah, ah
20AE  2D 80 00        sub ax, 0x80
20B1  C4 3E 23 A9     les di, ptr [0xa923]
20B5  03 F8           add di, ax
20B7  26 80 7D 13 00  cmp byte ptr es:[di + 0x13], 0
20BC  74 03           je 0x20c1
20BE  E9 C0 02        jmp 0x2381
loc_20C1:
20C1  C7 46 FD FF FF  mov word ptr [bp - 3], 0xffff
20C6  C7 46 FB 01 00  mov word ptr [bp - 5], 1
20CB  EB 03           jmp 0x20d0
loc_20CD:
20CD  FF 46 FB        inc word ptr [bp - 5]
loc_20D0:
20D0  8B 46 FB        mov ax, word ptr [bp - 5]
20D3  D1 E0           shl ax, 1
20D5  C4 7E F3        les di, ptr [bp - 0xd]
20D8  03 F8           add di, ax
20DA  26 8B 45 FE     mov ax, word ptr es:[di - 2]
20DE  BA 14 00        mov dx, 0x14
20E1  F7 E2           mul dx
20E3  C4 3E 1B A9     les di, ptr [0xa91b]
20E7  03 F8           add di, ax
20E9  89 7E EF        mov word ptr [bp - 0x11], di
20EC  8C 46 F1        mov word ptr [bp - 0xf], es
20EF  C4 7E EF        les di, ptr [bp - 0x11]
20F2  26 8A 45 06     mov al, byte ptr es:[di + 6]
20F6  3A 06 22 00     cmp al, byte ptr [0x22]
20FA  75 56           jne 0x2152
20FC  8B 46 FB        mov ax, word ptr [bp - 5]
20FF  D1 E0           shl ax, 1
2101  C4 7E F3        les di, ptr [bp - 0xd]
2104  03 F8           add di, ax
2106  26 FF 75 FE     push word ptr es:[di - 2]
210A  9A 16 32 71 17  call far 1771:3216
210F  08 C0           or al, al
2111  75 3F           jne 0x2152
2113  8B 46 FB        mov ax, word ptr [bp - 5]
2116  D1 E0           shl ax, 1
2118  C4 7E F3        les di, ptr [bp - 0xd]
211B  03 F8           add di, ax
211D  26 FF 75 FE     push word ptr es:[di - 2]
2121  9A 7E 37 71 17  call far 1771:377E
2126  3B 46 FD        cmp ax, word ptr [bp - 3]
2129  73 27           jae 0x2152
212B  8B 46 FB        mov ax, word ptr [bp - 5]
212E  D1 E0           shl ax, 1
2130  C4 7E F3        les di, ptr [bp - 0xd]
2133  03 F8           add di, ax
2135  26 FF 75 FE     push word ptr es:[di - 2]
2139  9A 7E 37 71 17  call far 1771:377E
213E  89 46 FD        mov word ptr [bp - 3], ax
2141  8B 46 FB        mov ax, word ptr [bp - 5]
2144  D1 E0           shl ax, 1
2146  C4 7E F3        les di, ptr [bp - 0xd]
2149  03 F8           add di, ax
214B  26 8B 45 FE     mov ax, word ptr es:[di - 2]
214F  89 46 F9        mov word ptr [bp - 7], ax
loc_2152:
2152  83 7E FB 14     cmp word ptr [bp - 5], 0x14
2156  74 03           je 0x215b
2158  E9 72 FF        jmp 0x20cd
loc_215B:
215B  83 7E FD FF     cmp word ptr [bp - 3], -1
215F  72 03           jb 0x2164
2161  E9 1D 02        jmp 0x2381
loc_2164:
2164  C4 7E F3        les di, ptr [bp - 0xd]
2167  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
216B  30 E4           xor ah, ah
216D  2D 80 00        sub ax, 0x80
2170  8B F8           mov di, ax
2172  D1 E7           shl di, 1
2174  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
2178  05 4F 00        add ax, 0x4f
217B  89 46 F1        mov word ptr [bp - 0xf], ax
217E  C4 7E F3        les di, ptr [bp - 0xd]
2181  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
2185  30 E4           xor ah, ah
2187  2D 80 00        sub ax, 0x80
218A  8B F8           mov di, ax
218C  D1 E7           shl di, 1
218E  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
2192  3B 46 F1        cmp ax, word ptr [bp - 0xf]
2195  77 7B           ja 0x2212
2197  89 46 FB        mov word ptr [bp - 5], ax
219A  EB 03           jmp 0x219f
loc_219C:
219C  FF 46 FB        inc word ptr [bp - 5]
loc_219F:
219F  8B 46 FB        mov ax, word ptr [bp - 5]
21A2  D1 E0           shl ax, 1
21A4  C4 3E 27 A9     les di, ptr [0xa927]
21A8  03 F8           add di, ax
21AA  26 8B 05        mov ax, word ptr es:[di]
21AD  BA 14 00        mov dx, 0x14
21B0  F7 E2           mul dx
21B2  C4 3E 1B A9     les di, ptr [0xa91b]
21B6  03 F8           add di, ax
21B8  89 7E ED        mov word ptr [bp - 0x13], di
21BB  8C 46 EF        mov word ptr [bp - 0x11], es
21BE  C4 7E ED        les di, ptr [bp - 0x13]
21C1  26 8A 45 07     mov al, byte ptr es:[di + 7]
21C5  3A 06 22 00     cmp al, byte ptr [0x22]
21C9  75 3F           jne 0x220a
21CB  8B 46 FB        mov ax, word ptr [bp - 5]
21CE  D1 E0           shl ax, 1
21D0  C4 3E 27 A9     les di, ptr [0xa927]
21D4  03 F8           add di, ax
21D6  26 FF 35        push word ptr es:[di]
21D9  9A 7E 37 71 17  call far 1771:377E
21DE  3B 46 FD        cmp ax, word ptr [bp - 3]
21E1  76 27           jbe 0x220a
21E3  8B 46 FB        mov ax, word ptr [bp - 5]
21E6  D1 E0           shl ax, 1
21E8  C4 3E 27 A9     les di, ptr [0xa927]
21EC  03 F8           add di, ax
21EE  26 FF 35        push word ptr es:[di]
21F1  9A 7E 37 71 17  call far 1771:377E
21F6  89 46 FD        mov word ptr [bp - 3], ax
21F9  8B 46 FB        mov ax, word ptr [bp - 5]
21FC  D1 E0           shl ax, 1
21FE  C4 3E 27 A9     les di, ptr [0xa927]
2202  03 F8           add di, ax
2204  26 8B 05        mov ax, word ptr es:[di]
2207  89 46 F7        mov word ptr [bp - 9], ax
loc_220A:
220A  8B 46 FB        mov ax, word ptr [bp - 5]
220D  3B 46 F1        cmp ax, word ptr [bp - 0xf]
2210  75 8A           jne 0x219c
loc_2212:
2212  8B 46 F9        mov ax, word ptr [bp - 7]
2215  BA 14 00        mov dx, 0x14
2218  F7 E2           mul dx
221A  C4 3E 1B A9     les di, ptr [0xa91b]
221E  03 F8           add di, ax
2220  89 7E EF        mov word ptr [bp - 0x11], di
2223  8C 46 F1        mov word ptr [bp - 0xf], es
2226  FF 76 F9        push word ptr [bp - 7]
2229  9A 7E 37 71 17  call far 1771:377E
222E  3B 46 FD        cmp ax, word ptr [bp - 3]
2231  72 03           jb 0x2236
2233  E9 4B 01        jmp 0x2381
loc_2236:
2236  B8 0A 00        mov ax, 0xa
2239  50              push ax
223A  9A B1 06 4B 21  call far 214B:06B1
223F  89 46 FD        mov word ptr [bp - 3], ax
2242  8B 46 FD        mov ax, word ptr [bp - 3]
2245  3D 01 00        cmp ax, 1
2248  72 42           jb 0x228c
224A  3D 05 00        cmp ax, 5
224D  77 3D           ja 0x228c
224F  8B 7E FD        mov di, word ptr [bp - 3]
2252  B1 04           mov cl, 4
2254  D3 E7           shl di, cl
2256  81 C7 14 00     add di, 0x14
225A  1E              push ds
225B  57              push di
225C  8D BE EF FE     lea di, [bp - 0x111]
2260  16              push ss
2261  57              push di
2262  FF 76 F7        push word ptr [bp - 9]
2265  9A 93 2E 71 17  call far 1771:2E93
226A  BF 14 20        mov di, 0x2014
226D  0E              push cs
226E  57              push di
226F  9A B7 06 E4 23  call far 23E4:06B7
2274  A0 22 00        mov al, byte ptr [0x22]
2277  30 E4           xor ah, ah
2279  BA 13 00        mov dx, 0x13
227C  F7 E2           mul dx
227E  8B F8           mov di, ax
2280  81 C7 B6 69     add di, 0x69b6
2284  1E              push ds
2285  57              push di
2286  E8 D6 E4        call 0x75f
2289  E9 F1 00        jmp 0x237d
loc_228C:
228C  3D 06 00        cmp ax, 6
228F  75 46           jne 0x22d7
2291  BF 18 20        mov di, 0x2018
2294  0E              push cs
2295  57              push di
2296  8D BE EF FE     lea di, [bp - 0x111]
229A  16              push ss
229B  57              push di
229C  FF 76 F9        push word ptr [bp - 7]
229F  9A 93 2E 71 17  call far 1771:2E93
22A4  BF 23 20        mov di, 0x2023
22A7  0E              push cs
22A8  57              push di
22A9  9A B7 06 E4 23  call far 23E4:06B7
22AE  8D BE EF FC     lea di, [bp - 0x311]
22B2  16              push ss
22B3  57              push di
22B4  BF 28 20        mov di, 0x2028
22B7  0E              push cs
22B8  57              push di
22B9  9A 2A 06 E4 23  call far 23E4:062A
22BE  8D BE EF FD     lea di, [bp - 0x211]
22C2  16              push ss
22C3  57              push di
22C4  FF 76 F7        push word ptr [bp - 9]
22C7  9A 93 2E 71 17  call far 1771:2E93
22CC  9A B7 06 E4 23  call far 23E4:06B7
22D1  E8 8B E4        call 0x75f
22D4  E9 A6 00        jmp 0x237d
loc_22D7:
22D7  3D 07 00        cmp ax, 7
22DA  75 30           jne 0x230c
22DC  8D BE EF FE     lea di, [bp - 0x111]
22E0  16              push ss
22E1  57              push di
22E2  FF 76 F7        push word ptr [bp - 9]
22E5  9A 93 2E 71 17  call far 1771:2E93
22EA  BF 2D 20        mov di, 0x202d
22ED  0E              push cs
22EE  57              push di
22EF  9A B7 06 E4 23  call far 23E4:06B7
22F4  BF 31 20        mov di, 0x2031
22F7  0E              push cs
22F8  57              push di
22F9  8D BE EF FD     lea di, [bp - 0x211]
22FD  16              push ss
22FE  57              push di
22FF  FF 76 F9        push word ptr [bp - 7]
2302  9A 93 2E 71 17  call far 1771:2E93
2307  E8 55 E4        call 0x75f
230A  EB 71           jmp 0x237d
loc_230C:
230C  3D 08 00        cmp ax, 8
230F  75 2A           jne 0x233b
2311  A0 22 00        mov al, byte ptr [0x22]
2314  30 E4           xor ah, ah
2316  BA 13 00        mov dx, 0x13
2319  F7 E2           mul dx
231B  8B F8           mov di, ax
231D  81 C7 B6 69     add di, 0x69b6
2321  1E              push ds
2322  57              push di
2323  8D BE EF FE     lea di, [bp - 0x111]
2327  16              push ss
2328  57              push di
2329  FF 76 F9        push word ptr [bp - 7]
232C  9A 93 2E 71 17  call far 1771:2E93
2331  BF 42 20        mov di, 0x2042
2334  0E              push cs
2335  57              push di
2336  E8 26 E4        call 0x75f
2339  EB 42           jmp 0x237d
loc_233B:
233B  3D 09 00        cmp ax, 9
233E  75 1D           jne 0x235d
2340  8D BE EF FE     lea di, [bp - 0x111]
2344  16              push ss
2345  57              push di
2346  FF 76 F7        push word ptr [bp - 9]
2349  9A 93 2E 71 17  call far 1771:2E93
234E  BF 4C 20        mov di, 0x204c
2351  0E              push cs
2352  57              push di
2353  BF 55 20        mov di, 0x2055
2356  0E              push cs
2357  57              push di
2358  E8 04 E4        call 0x75f
235B  EB 20           jmp 0x237d
loc_235D:
235D  3D 0A 00        cmp ax, 0xa
2360  75 1B           jne 0x237d
2362  8D BE EF FE     lea di, [bp - 0x111]
2366  16              push ss
2367  57              push di
2368  FF 76 F7        push word ptr [bp - 9]
236B  9A 93 2E 71 17  call far 1771:2E93
2370  BF 5C 20        mov di, 0x205c
2373  0E              push cs
2374  57              push di
2375  BF 65 20        mov di, 0x2065
2378  0E              push cs
2379  57              push di
237A  E8 E2 E3        call 0x75f
loc_237D:
237D  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_2381:
2381  8A 46 FF        mov al, byte ptr [bp - 1]
2384  89 EC           mov sp, bp
2386  5D              pop bp
2387  C2 02 00        ret 2
; data (not reached as code), 872 bytes
238A                  pstr 'WORLD CUP VICTORS'
239C                  pstr 'AND '
23A1                  pstr 'ARE READY TO TAKE'
23B3                  pstr 'ON THE WORLD'
23C0                  pstr ' TAKES'
23C7                  pstr 'TO THE FINAL'
23D4                  pstr 'WE REMAIN TO BE'
23E4                  pstr 'CONVINCED'
23EE                  pstr 'A VICTORY FOR'
23FC                  db 01 21 00   ; .!.
23FF                  pstr 'DO IT AGAIN'
240B                  pstr 'IS ON THE'
2415                  pstr 'WINNING TRACK'
2423                  pstr 'NOT BAD'
242B                  pstr 'TWO IN A ROW!'
2439                  pstr 'KEEP IT UP'
2444                  pstr 'THINGS ARE LOOKING'
2457                  pstr 'UP FOR'
245E                  pstr 'IS PERFORMING'
246C                  pstr 'WELL, WE SAY'
2479                  pstr 'ARE LOOKING GOOD'
248A                  pstr 'IS ON THE RIGHT'
249A                  pstr 'TRACK'
24A0                  pstr 'MAKES IT LOOK'
24AE                  pstr 'SO EASY'
24B6                  pstr 'GENIUS OF'
24C0                  pstr 'CONTINUES TO SHOW'
24D2                  pstr 'IS OUR MAN'
24DD                  pstr 'IS THE BEST'
24E9                  pstr "WE'VE SEEN"
24F4                  pstr 'WE LOVE YOU'
2500                  pstr ' WINS'
2506                  pstr 'IT JUST GOES ON!'
2517                  pstr ' CONSECUTIVE'
2524                  pstr 'WINS CANNOT'
2530                  pstr 'BE BAD'
2537                  pstr ' GLORIOUS WINS!'
2547                  pstr 'THANK YOU '
2552                  pstr 'WHO WILL REPLACE'
2563                  db 01 3F   ; .?
2565                  pstr 'WHAT ARE YOU'
2572                  pstr 'DOING?'
2579                  pstr 'BETTER GET YOUR'
2589                  pstr 'TACTICS WORKED OUT'
259C                  pstr 'WE COULD DO MUCH'
25AD                  pstr 'BETTER'
25B4                  pstr 'NEED A DEFENCE'
25C3                  pstr 'WHERE WAS THE'
25D1                  pstr 'DEFENCE, WE ASK?'
25E2                  pstr 'COULD DO WITH A'
25F2                  pstr 'FOOTBALL TEAM'
2600                  pstr 'NEED TO'
2608                  pstr 'CREATE CHANCES'
2617                  pstr 'LOOK WEAK'
2621                  pstr 'IN ATTACK'
262B                  pstr 'NEED A STRIKE'
2639                  pstr 'FORCE'
263F                  pstr 'NEED A GOALKEEPER'
2651                  pstr 'GET A NEW KEEPER'
2662                  pstr 'SHILTON WOULD BE'
2673                  pstr 'BETTER IN GOALS'
2683                  pstr 'TRY A BIT HARDER'
2694                  pstr 'WE ARE WATCHING YOU'
26A8                  pstr 'WE ARE NOT'
26B3                  pstr 'DESERVE BETTER'
26C2                  pstr 'NOTHING BUT A WIN'
26D4                  pstr 'WILL DO'
26DC                  pstr 'DO BETTER '
26E7                  pstr 'OR GIVE UP'

; ---- routine 000E:26F2  (found by: call)
sub_26F2:
26F2  55              push bp
26F3  89 E5           mov bp, sp
26F5  81 EC 08 03     sub sp, 0x308
26F9  8B 7E 04        mov di, word ptr [bp + 4]
26FC  36 C4 7D 04     les di, ptr ss:[di + 4]
2700  89 7E FC        mov word ptr [bp - 4], di
2703  8C 46 FE        mov word ptr [bp - 2], es
2706  8B 7E 04        mov di, word ptr [bp + 4]
2709  36 8B 45 08     mov ax, word ptr ss:[di + 8]
270D  BA BF 00        mov dx, 0xbf
2710  F7 E2           mul dx
2712  C4 3E 17 A9     les di, ptr [0xa917]
2716  03 F8           add di, ax
2718  89 7E F8        mov word ptr [bp - 8], di
271B  8C 46 FA        mov word ptr [bp - 6], es
271E  C4 7E FC        les di, ptr [bp - 4]
2721  26 8A 45 03     mov al, byte ptr es:[di + 3]
2725  8B 7E 04        mov di, word ptr [bp + 4]
2728  36 3A 45 FF     cmp al, byte ptr ss:[di - 1]
272C  74 03           je 0x2731
272E  E9 C4 03        jmp 0x2af5
loc_2731:
2731  C4 7E FC        les di, ptr [bp - 4]
2734  26 8A 45 02     mov al, byte ptr es:[di + 2]
2738  3C CB           cmp al, 0xcb
273A  75 38           jne 0x2774
273C  BF 8A 23        mov di, 0x238a
273F  0E              push cs
2740  57              push di
2741  8D BE F8 FE     lea di, [bp - 0x108]
2745  16              push ss
2746  57              push di
2747  FF 76 04        push word ptr [bp + 4]
274A  E8 00 E4        call 0xb4d
274D  8D BE F8 FC     lea di, [bp - 0x308]
2751  16              push ss
2752  57              push di
2753  BF 9C 23        mov di, 0x239c
2756  0E              push cs
2757  57              push di
2758  9A 2A 06 E4 23  call far 23E4:062A
275D  8D BE F8 FD     lea di, [bp - 0x208]
2761  16              push ss
2762  57              push di
2763  FF 76 04        push word ptr [bp + 4]
2766  E8 62 E3        call 0xacb
2769  9A B7 06 E4 23  call far 23E4:06B7
276E  E8 EE DF        call 0x75f
2771  E9 7E 03        jmp 0x2af2
loc_2774:
2774  3C 67           cmp al, 0x67
2776  75 1C           jne 0x2794
2778  8D BE F8 FE     lea di, [bp - 0x108]
277C  16              push ss
277D  57              push di
277E  FF 76 04        push word ptr [bp + 4]
2781  E8 C9 E3        call 0xb4d
2784  BF A1 23        mov di, 0x23a1
2787  0E              push cs
2788  57              push di
2789  BF B3 23        mov di, 0x23b3
278C  0E              push cs
278D  57              push di
278E  E8 CE DF        call 0x75f
2791  E9 5E 03        jmp 0x2af2
loc_2794:
2794  3C C9           cmp al, 0xc9
2796  74 04           je 0x279c
2798  3C 65           cmp al, 0x65
279A  75 2D           jne 0x27c9
loc_279C:
279C  8D BE F8 FE     lea di, [bp - 0x108]
27A0  16              push ss
27A1  57              push di
27A2  FF 76 04        push word ptr [bp + 4]
27A5  E8 23 E3        call 0xacb
27A8  BF C0 23        mov di, 0x23c0
27AB  0E              push cs
27AC  57              push di
27AD  9A B7 06 E4 23  call far 23E4:06B7
27B2  8D BE F8 FD     lea di, [bp - 0x208]
27B6  16              push ss
27B7  57              push di
27B8  FF 76 04        push word ptr [bp + 4]
27BB  E8 8F E3        call 0xb4d
27BE  BF C7 23        mov di, 0x23c7
27C1  0E              push cs
27C2  57              push di
27C3  E8 99 DF        call 0x75f
27C6  E9 29 03        jmp 0x2af2
loc_27C9:
27C9  55              push bp
27CA  E8 A4 F8        call 0x2071
27CD  08 C0           or al, al
27CF  74 03           je 0x27d4
27D1  E9 1E 03        jmp 0x2af2
loc_27D4:
27D4  C4 7E F8        les di, ptr [bp - 8]
27D7  26 8A 85 AC 00  mov al, byte ptr es:[di + 0xac]
27DC  3C 01           cmp al, 1
27DE  74 03           je 0x27e3
27E0  E9 9E 00        jmp 0x2881
loc_27E3:
27E3  B8 04 00        mov ax, 4
27E6  50              push ax
27E7  9A B1 06 4B 21  call far 214B:06B1
27EC  3D 01 00        cmp ax, 1
27EF  75 1B           jne 0x280c
27F1  BF D4 23        mov di, 0x23d4
27F4  0E              push cs
27F5  57              push di
27F6  BF E4 23        mov di, 0x23e4
27F9  0E              push cs
27FA  57              push di
27FB  8D BE F8 FE     lea di, [bp - 0x108]
27FF  16              push ss
2800  57              push di
2801  FF 76 04        push word ptr [bp + 4]
2804  E8 C4 E2        call 0xacb
2807  E8 55 DF        call 0x75f
280A  EB 72           jmp 0x287e
loc_280C:
280C  3D 02 00        cmp ax, 2
280F  75 25           jne 0x2836
2811  BF EE 23        mov di, 0x23ee
2814  0E              push cs
2815  57              push di
2816  8D BE F8 FE     lea di, [bp - 0x108]
281A  16              push ss
281B  57              push di
281C  FF 76 04        push word ptr [bp + 4]
281F  E8 A9 E2        call 0xacb
2822  BF FC 23        mov di, 0x23fc
2825  0E              push cs
2826  57              push di
2827  9A B7 06 E4 23  call far 23E4:06B7
282C  BF FE 23        mov di, 0x23fe
282F  0E              push cs
2830  57              push di
2831  E8 2B DF        call 0x75f
2834  EB 48           jmp 0x287e
loc_2836:
2836  3D 03 00        cmp ax, 3
2839  75 25           jne 0x2860
283B  BF FF 23        mov di, 0x23ff
283E  0E              push cs
283F  57              push di
2840  8D BE F8 FE     lea di, [bp - 0x108]
2844  16              push ss
2845  57              push di
2846  FF 76 04        push word ptr [bp + 4]
2849  E8 7F E2        call 0xacb
284C  BF FC 23        mov di, 0x23fc
284F  0E              push cs
2850  57              push di
2851  9A B7 06 E4 23  call far 23E4:06B7
2856  BF FE 23        mov di, 0x23fe
2859  0E              push cs
285A  57              push di
285B  E8 01 DF        call 0x75f
285E  EB 1E           jmp 0x287e
loc_2860:
2860  3D 04 00        cmp ax, 4
2863  75 19           jne 0x287e
2865  8D BE F8 FE     lea di, [bp - 0x108]
2869  16              push ss
286A  57              push di
286B  FF 76 04        push word ptr [bp + 4]
286E  E8 5A E2        call 0xacb
2871  BF 0B 24        mov di, 0x240b
2874  0E              push cs
2875  57              push di
2876  BF 15 24        mov di, 0x2415
2879  0E              push cs
287A  57              push di
287B  E8 E1 DE        call 0x75f
loc_287E:
287E  E9 71 02        jmp 0x2af2
loc_2881:
2881  3C 02           cmp al, 2
2883  75 39           jne 0x28be
2885  9A FA 06 4B 21  call far 214B:06FA
288A  08 C0           or al, al
288C  74 1B           je 0x28a9
288E  BF 23 24        mov di, 0x2423
2891  0E              push cs
2892  57              push di
2893  8D BE F8 FE     lea di, [bp - 0x108]
2897  16              push ss
2898  57              push di
2899  FF 76 04        push word ptr [bp + 4]
289C  E8 2C E2        call 0xacb
289F  BF FE 23        mov di, 0x23fe
28A2  0E              push cs
28A3  57              push di
28A4  E8 B8 DE        call 0x75f
28A7  EB 12           jmp 0x28bb
loc_28A9:
28A9  BF 2B 24        mov di, 0x242b
28AC  0E              push cs
28AD  57              push di
28AE  BF FE 23        mov di, 0x23fe
28B1  0E              push cs
28B2  57              push di
28B3  BF FE 23        mov di, 0x23fe
28B6  0E              push cs
28B7  57              push di
28B8  E8 A4 DE        call 0x75f
loc_28BB:
28BB  E9 34 02        jmp 0x2af2
loc_28BE:
28BE  3C 03           cmp al, 3
28C0  75 1C           jne 0x28de
28C2  BF 39 24        mov di, 0x2439
28C5  0E              push cs
28C6  57              push di
28C7  8D BE F8 FE     lea di, [bp - 0x108]
28CB  16              push ss
28CC  57              push di
28CD  FF 76 04        push word ptr [bp + 4]
28D0  E8 F8 E1        call 0xacb
28D3  BF FE 23        mov di, 0x23fe
28D6  0E              push cs
28D7  57              push di
28D8  E8 84 DE        call 0x75f
28DB  E9 14 02        jmp 0x2af2
loc_28DE:
28DE  3C 04           cmp al, 4
28E0  75 1C           jne 0x28fe
28E2  BF 44 24        mov di, 0x2444
28E5  0E              push cs
28E6  57              push di
28E7  BF 57 24        mov di, 0x2457
28EA  0E              push cs
28EB  57              push di
28EC  8D BE F8 FE     lea di, [bp - 0x108]
28F0  16              push ss
28F1  57              push di
28F2  FF 76 04        push word ptr [bp + 4]
28F5  E8 55 E2        call 0xb4d
28F8  E8 64 DE        call 0x75f
28FB  E9 F4 01        jmp 0x2af2
loc_28FE:
28FE  3C 05           cmp al, 5
2900  75 1C           jne 0x291e
2902  8D BE F8 FE     lea di, [bp - 0x108]
2906  16              push ss
2907  57              push di
2908  FF 76 04        push word ptr [bp + 4]
290B  E8 BD E1        call 0xacb
290E  BF 5E 24        mov di, 0x245e
2911  0E              push cs
2912  57              push di
2913  BF 6C 24        mov di, 0x246c
2916  0E              push cs
2917  57              push di
2918  E8 44 DE        call 0x75f
291B  E9 D4 01        jmp 0x2af2
loc_291E:
291E  3C 06           cmp al, 6
2920  75 1C           jne 0x293e
2922  8D BE F8 FE     lea di, [bp - 0x108]
2926  16              push ss
2927  57              push di
2928  FF 76 04        push word ptr [bp + 4]
292B  E8 1F E2        call 0xb4d
292E  BF 79 24        mov di, 0x2479
2931  0E              push cs
2932  57              push di
2933  BF FE 23        mov di, 0x23fe
2936  0E              push cs
2937  57              push di
2938  E8 24 DE        call 0x75f
293B  E9 B4 01        jmp 0x2af2
loc_293E:
293E  3C 07           cmp al, 7
2940  75 1C           jne 0x295e
2942  8D BE F8 FE     lea di, [bp - 0x108]
2946  16              push ss
2947  57              push di
2948  FF 76 04        push word ptr [bp + 4]
294B  E8 7D E1        call 0xacb
294E  BF 8A 24        mov di, 0x248a
2951  0E              push cs
2952  57              push di
2953  BF 9A 24        mov di, 0x249a
2956  0E              push cs
2957  57              push di
2958  E8 04 DE        call 0x75f
295B  E9 94 01        jmp 0x2af2
loc_295E:
295E  B8 10 00        mov ax, 0x10
2961  50              push ax
2962  9A B1 06 4B 21  call far 214B:06B1
2967  3D 01 00        cmp ax, 1
296A  75 1C           jne 0x2988
296C  8D BE F8 FE     lea di, [bp - 0x108]
2970  16              push ss
2971  57              push di
2972  FF 76 04        push word ptr [bp + 4]
2975  E8 53 E1        call 0xacb
2978  BF A0 24        mov di, 0x24a0
297B  0E              push cs
297C  57              push di
297D  BF AE 24        mov di, 0x24ae
2980  0E              push cs
2981  57              push di
2982  E8 DA DD        call 0x75f
2985  E9 6A 01        jmp 0x2af2
loc_2988:
2988  3D 02 00        cmp ax, 2
298B  75 1C           jne 0x29a9
298D  BF B6 24        mov di, 0x24b6
2990  0E              push cs
2991  57              push di
2992  8D BE F8 FE     lea di, [bp - 0x108]
2996  16              push ss
2997  57              push di
2998  FF 76 04        push word ptr [bp + 4]
299B  E8 2D E1        call 0xacb
299E  BF C0 24        mov di, 0x24c0
29A1  0E              push cs
29A2  57              push di
29A3  E8 B9 DD        call 0x75f
29A6  E9 49 01        jmp 0x2af2
loc_29A9:
29A9  3D 03 00        cmp ax, 3
29AC  75 1C           jne 0x29ca
29AE  8D BE F8 FE     lea di, [bp - 0x108]
29B2  16              push ss
29B3  57              push di
29B4  FF 76 04        push word ptr [bp + 4]
29B7  E8 11 E1        call 0xacb
29BA  BF D2 24        mov di, 0x24d2
29BD  0E              push cs
29BE  57              push di
29BF  BF FE 23        mov di, 0x23fe
29C2  0E              push cs
29C3  57              push di
29C4  E8 98 DD        call 0x75f
29C7  E9 28 01        jmp 0x2af2
loc_29CA:
29CA  3D 04 00        cmp ax, 4
29CD  75 1C           jne 0x29eb
29CF  BF 39 24        mov di, 0x2439
29D2  0E              push cs
29D3  57              push di
29D4  8D BE F8 FE     lea di, [bp - 0x108]
29D8  16              push ss
29D9  57              push di
29DA  FF 76 04        push word ptr [bp + 4]
29DD  E8 EB E0        call 0xacb
29E0  BF FE 23        mov di, 0x23fe
29E3  0E              push cs
29E4  57              push di
29E5  E8 77 DD        call 0x75f
29E8  E9 07 01        jmp 0x2af2
loc_29EB:
29EB  3D 05 00        cmp ax, 5
29EE  75 1C           jne 0x2a0c
29F0  8D BE F8 FE     lea di, [bp - 0x108]
29F4  16              push ss
29F5  57              push di
29F6  FF 76 04        push word ptr [bp + 4]
29F9  E8 CF E0        call 0xacb
29FC  BF DD 24        mov di, 0x24dd
29FF  0E              push cs
2A00  57              push di
2A01  BF E9 24        mov di, 0x24e9
2A04  0E              push cs
2A05  57              push di
2A06  E8 56 DD        call 0x75f
2A09  E9 E6 00        jmp 0x2af2
loc_2A0C:
2A0C  3D 06 00        cmp ax, 6
2A0F  75 1C           jne 0x2a2d
2A11  BF F4 24        mov di, 0x24f4
2A14  0E              push cs
2A15  57              push di
2A16  8D BE F8 FE     lea di, [bp - 0x108]
2A1A  16              push ss
2A1B  57              push di
2A1C  FF 76 04        push word ptr [bp + 4]
2A1F  E8 A9 E0        call 0xacb
2A22  BF FE 23        mov di, 0x23fe
2A25  0E              push cs
2A26  57              push di
2A27  E8 35 DD        call 0x75f
2A2A  E9 C5 00        jmp 0x2af2
loc_2A2D:
2A2D  3D 07 00        cmp ax, 7
2A30  7C 38           jl 0x2a6a
2A32  3D 09 00        cmp ax, 9
2A35  7F 33           jg 0x2a6a
2A37  8D BE F8 FE     lea di, [bp - 0x108]
2A3B  16              push ss
2A3C  57              push di
2A3D  C4 7E F8        les di, ptr [bp - 8]
2A40  26 8A 85 AC 00  mov al, byte ptr es:[di + 0xac]
2A45  30 E4           xor ah, ah
2A47  31 D2           xor dx, dx
2A49  52              push dx
2A4A  50              push ax
2A4B  9A DA 09 4B 21  call far 214B:09DA
2A50  BF 00 25        mov di, 0x2500
2A53  0E              push cs
2A54  57              push di
2A55  9A B7 06 E4 23  call far 23E4:06B7
2A5A  BF 06 25        mov di, 0x2506
2A5D  0E              push cs
2A5E  57              push di
2A5F  BF FE 23        mov di, 0x23fe
2A62  0E              push cs
2A63  57              push di
2A64  E8 F8 DC        call 0x75f
2A67  E9 88 00        jmp 0x2af2
loc_2A6A:
2A6A  3D 0A 00        cmp ax, 0xa
2A6D  7C 37           jl 0x2aa6
2A6F  3D 0D 00        cmp ax, 0xd
2A72  7F 32           jg 0x2aa6
2A74  8D BE F8 FE     lea di, [bp - 0x108]
2A78  16              push ss
2A79  57              push di
2A7A  C4 7E F8        les di, ptr [bp - 8]
2A7D  26 8A 85 AC 00  mov al, byte ptr es:[di + 0xac]
2A82  30 E4           xor ah, ah
2A84  31 D2           xor dx, dx
2A86  52              push dx
2A87  50              push ax
2A88  9A DA 09 4B 21  call far 214B:09DA
2A8D  BF 17 25        mov di, 0x2517
2A90  0E              push cs
2A91  57              push di
2A92  9A B7 06 E4 23  call far 23E4:06B7
2A97  BF 24 25        mov di, 0x2524
2A9A  0E              push cs
2A9B  57              push di
2A9C  BF 30 25        mov di, 0x2530
2A9F  0E              push cs
2AA0  57              push di
2AA1  E8 BB DC        call 0x75f
2AA4  EB 4C           jmp 0x2af2
loc_2AA6:
2AA6  8D BE F8 FE     lea di, [bp - 0x108]
2AAA  16              push ss
2AAB  57              push di
2AAC  C4 7E F8        les di, ptr [bp - 8]
2AAF  26 8A 85 AC 00  mov al, byte ptr es:[di + 0xac]
2AB4  30 E4           xor ah, ah
2AB6  31 D2           xor dx, dx
2AB8  52              push dx
2AB9  50              push ax
2ABA  9A DA 09 4B 21  call far 214B:09DA
2ABF  BF 37 25        mov di, 0x2537
2AC2  0E              push cs
2AC3  57              push di
2AC4  9A B7 06 E4 23  call far 23E4:06B7
2AC9  8D BE F8 FC     lea di, [bp - 0x308]
2ACD  16              push ss
2ACE  57              push di
2ACF  BF 47 25        mov di, 0x2547
2AD2  0E              push cs
2AD3  57              push di
2AD4  9A 2A 06 E4 23  call far 23E4:062A
2AD9  8D BE F8 FD     lea di, [bp - 0x208]
2ADD  16              push ss
2ADE  57              push di
2ADF  FF 76 04        push word ptr [bp + 4]
2AE2  E8 E6 DF        call 0xacb
2AE5  9A B7 06 E4 23  call far 23E4:06B7
2AEA  BF FE 23        mov di, 0x23fe
2AED  0E              push cs
2AEE  57              push di
2AEF  E8 6D DC        call 0x75f
loc_2AF2:
2AF2  E9 24 03        jmp 0x2e19
loc_2AF5:
2AF5  FF 76 04        push word ptr [bp + 4]
2AF8  E8 7C E0        call 0xb77
2AFB  3D F6 FF        cmp ax, 0xfff6
2AFE  7D 26           jge 0x2b26
2B00  BF 52 25        mov di, 0x2552
2B03  0E              push cs
2B04  57              push di
2B05  8D BE F8 FE     lea di, [bp - 0x108]
2B09  16              push ss
2B0A  57              push di
2B0B  FF 76 04        push word ptr [bp + 4]
2B0E  E8 BA DF        call 0xacb
2B11  BF 63 25        mov di, 0x2563
2B14  0E              push cs
2B15  57              push di
2B16  9A B7 06 E4 23  call far 23E4:06B7
2B1B  BF FE 23        mov di, 0x23fe
2B1E  0E              push cs
2B1F  57              push di
2B20  E8 3C DC        call 0x75f
2B23  E9 F3 02        jmp 0x2e19
loc_2B26:
2B26  55              push bp
2B27  E8 47 F5        call 0x2071
2B2A  08 C0           or al, al
2B2C  74 03           je 0x2b31
2B2E  E9 E8 02        jmp 0x2e19
loc_2B31:
2B31  8B 7E 04        mov di, word ptr [bp + 4]
2B34  36 C4 7D 04     les di, ptr ss:[di + 4]
2B38  06              push es
2B39  57              push di
2B3A  9A 60 5C 71 17  call far 1771:5C60
2B3F  3D 01 00        cmp ax, 1
2B42  77 03           ja 0x2b47
2B44  E9 CB 00        jmp 0x2c12
loc_2B47:
2B47  B8 06 00        mov ax, 6
2B4A  50              push ax
2B4B  9A B1 06 4B 21  call far 214B:06B1
2B50  3D 01 00        cmp ax, 1
2B53  75 1C           jne 0x2b71
2B55  8D BE F8 FE     lea di, [bp - 0x108]
2B59  16              push ss
2B5A  57              push di
2B5B  FF 76 04        push word ptr [bp + 4]
2B5E  E8 6A DF        call 0xacb
2B61  BF 65 25        mov di, 0x2565
2B64  0E              push cs
2B65  57              push di
2B66  BF 72 25        mov di, 0x2572
2B69  0E              push cs
2B6A  57              push di
2B6B  E8 F1 DB        call 0x75f
2B6E  E9 9E 00        jmp 0x2c0f
loc_2B71:
2B71  3D 02 00        cmp ax, 2
2B74  75 1B           jne 0x2b91
2B76  8D BE F8 FE     lea di, [bp - 0x108]
2B7A  16              push ss
2B7B  57              push di
2B7C  FF 76 04        push word ptr [bp + 4]
2B7F  E8 49 DF        call 0xacb
2B82  BF 79 25        mov di, 0x2579
2B85  0E              push cs
2B86  57              push di
2B87  BF 89 25        mov di, 0x2589
2B8A  0E              push cs
2B8B  57              push di
2B8C  E8 D0 DB        call 0x75f
2B8F  EB 7E           jmp 0x2c0f
loc_2B91:
2B91  3D 03 00        cmp ax, 3
2B94  75 1B           jne 0x2bb1
2B96  BF 9C 25        mov di, 0x259c
2B99  0E              push cs
2B9A  57              push di
2B9B  BF AD 25        mov di, 0x25ad
2B9E  0E              push cs
2B9F  57              push di
2BA0  8D BE F8 FE     lea di, [bp - 0x108]
2BA4  16              push ss
2BA5  57              push di
2BA6  FF 76 04        push word ptr [bp + 4]
2BA9  E8 1F DF        call 0xacb
2BAC  E8 B0 DB        call 0x75f
2BAF  EB 5E           jmp 0x2c0f
loc_2BB1:
2BB1  3D 04 00        cmp ax, 4
2BB4  75 22           jne 0x2bd8
2BB6  8D BE F8 FE     lea di, [bp - 0x108]
2BBA  16              push ss
2BBB  57              push di
2BBC  FF 76 04        push word ptr [bp + 4]
2BBF  E8 8B DF        call 0xb4d
2BC2  BF B4 25        mov di, 0x25b4
2BC5  0E              push cs
2BC6  57              push di
2BC7  8D BE F8 FD     lea di, [bp - 0x208]
2BCB  16              push ss
2BCC  57              push di
2BCD  FF 76 04        push word ptr [bp + 4]
2BD0  E8 F8 DE        call 0xacb
2BD3  E8 89 DB        call 0x75f
2BD6  EB 37           jmp 0x2c0f
loc_2BD8:
2BD8  3D 05 00        cmp ax, 5
2BDB  75 14           jne 0x2bf1
2BDD  BF C3 25        mov di, 0x25c3
2BE0  0E              push cs
2BE1  57              push di
2BE2  BF D1 25        mov di, 0x25d1
2BE5  0E              push cs
2BE6  57              push di
2BE7  BF FE 23        mov di, 0x23fe
2BEA  0E              push cs
2BEB  57              push di
2BEC  E8 70 DB        call 0x75f
2BEF  EB 1E           jmp 0x2c0f
loc_2BF1:
2BF1  3D 06 00        cmp ax, 6
2BF4  75 19           jne 0x2c0f
2BF6  8D BE F8 FE     lea di, [bp - 0x108]
2BFA  16              push ss
2BFB  57              push di
2BFC  FF 76 04        push word ptr [bp + 4]
2BFF  E8 4B DF        call 0xb4d
2C02  BF E2 25        mov di, 0x25e2
2C05  0E              push cs
2C06  57              push di
2C07  BF F2 25        mov di, 0x25f2
2C0A  0E              push cs
2C0B  57              push di
2C0C  E8 50 DB        call 0x75f
loc_2C0F:
2C0F  E9 07 02        jmp 0x2e19
loc_2C12:
2C12  8B 7E 04        mov di, word ptr [bp + 4]
2C15  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
2C19  98              cwde
2C1A  BA 0A 00        mov dx, 0xa
2C1D  F7 E2           mul dx
2C1F  8B F8           mov di, ax
2C21  8A 85 7E 7B     mov al, byte ptr [di + 0x7b7e]
2C25  30 E4           xor ah, ah
2C27  8B C8           mov cx, ax
2C29  8B 7E 04        mov di, word ptr [bp + 4]
2C2C  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
2C30  98              cwde
2C31  BA 0A 00        mov dx, 0xa
2C34  F7 E2           mul dx
2C36  8B F8           mov di, ax
2C38  8A 85 81 7B     mov al, byte ptr [di + 0x7b81]
2C3C  30 E4           xor ah, ah
2C3E  03 C1           add ax, cx
2C40  3D 08 00        cmp ax, 8
2C43  7D 6A           jge 0x2caf
2C45  B8 03 00        mov ax, 3
2C48  50              push ax
2C49  9A B1 06 4B 21  call far 214B:06B1
2C4E  3D 01 00        cmp ax, 1
2C51  75 1B           jne 0x2c6e
2C53  8D BE F8 FE     lea di, [bp - 0x108]
2C57  16              push ss
2C58  57              push di
2C59  FF 76 04        push word ptr [bp + 4]
2C5C  E8 EE DE        call 0xb4d
2C5F  BF 00 26        mov di, 0x2600
2C62  0E              push cs
2C63  57              push di
2C64  BF 08 26        mov di, 0x2608
2C67  0E              push cs
2C68  57              push di
2C69  E8 F3 DA        call 0x75f
2C6C  EB 3E           jmp 0x2cac
loc_2C6E:
2C6E  3D 02 00        cmp ax, 2
2C71  75 1B           jne 0x2c8e
2C73  8D BE F8 FE     lea di, [bp - 0x108]
2C77  16              push ss
2C78  57              push di
2C79  FF 76 04        push word ptr [bp + 4]
2C7C  E8 CE DE        call 0xb4d
2C7F  BF 17 26        mov di, 0x2617
2C82  0E              push cs
2C83  57              push di
2C84  BF 21 26        mov di, 0x2621
2C87  0E              push cs
2C88  57              push di
2C89  E8 D3 DA        call 0x75f
2C8C  EB 1E           jmp 0x2cac
loc_2C8E:
2C8E  3D 03 00        cmp ax, 3
2C91  75 19           jne 0x2cac
2C93  8D BE F8 FE     lea di, [bp - 0x108]
2C97  16              push ss
2C98  57              push di
2C99  FF 76 04        push word ptr [bp + 4]
2C9C  E8 AE DE        call 0xb4d
2C9F  BF 2B 26        mov di, 0x262b
2CA2  0E              push cs
2CA3  57              push di
2CA4  BF 39 26        mov di, 0x2639
2CA7  0E              push cs
2CA8  57              push di
2CA9  E8 B3 DA        call 0x75f
loc_2CAC:
2CAC  E9 6A 01        jmp 0x2e19
loc_2CAF:
2CAF  8B 7E 04        mov di, word ptr [bp + 4]
2CB2  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
2CB6  98              cwde
2CB7  BA 0A 00        mov dx, 0xa
2CBA  F7 E2           mul dx
2CBC  8B F8           mov di, ax
2CBE  8A 95 83 7B     mov dl, byte ptr [di + 0x7b83]
2CC2  8B 7E 04        mov di, word ptr [bp + 4]
2CC5  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
2CCA  74 04           je 0x2cd0
2CCC  B0 00           mov al, 0
2CCE  EB 02           jmp 0x2cd2
loc_2CD0:
2CD0  B0 01           mov al, 1
loc_2CD2:
2CD2  98              cwde
2CD3  C4 7E FC        les di, ptr [bp - 4]
2CD6  03 F8           add di, ax
2CD8  26 8A 05        mov al, byte ptr es:[di]
2CDB  3A C2           cmp al, dl
2CDD  76 6A           jbe 0x2d49
2CDF  B8 03 00        mov ax, 3
2CE2  50              push ax
2CE3  9A B1 06 4B 21  call far 214B:06B1
2CE8  3D 01 00        cmp ax, 1
2CEB  75 1B           jne 0x2d08
2CED  8D BE F8 FE     lea di, [bp - 0x108]
2CF1  16              push ss
2CF2  57              push di
2CF3  FF 76 04        push word ptr [bp + 4]
2CF6  E8 54 DE        call 0xb4d
2CF9  BF 3F 26        mov di, 0x263f
2CFC  0E              push cs
2CFD  57              push di
2CFE  BF FE 23        mov di, 0x23fe
2D01  0E              push cs
2D02  57              push di
2D03  E8 59 DA        call 0x75f
2D06  EB 3E           jmp 0x2d46
loc_2D08:
2D08  3D 02 00        cmp ax, 2
2D0B  75 1B           jne 0x2d28
2D0D  BF 51 26        mov di, 0x2651
2D10  0E              push cs
2D11  57              push di
2D12  8D BE F8 FE     lea di, [bp - 0x108]
2D16  16              push ss
2D17  57              push di
2D18  FF 76 04        push word ptr [bp + 4]
2D1B  E8 AD DD        call 0xacb
2D1E  BF FE 23        mov di, 0x23fe
2D21  0E              push cs
2D22  57              push di
2D23  E8 39 DA        call 0x75f
2D26  EB 1E           jmp 0x2d46
loc_2D28:
2D28  3D 03 00        cmp ax, 3
2D2B  75 19           jne 0x2d46
2D2D  BF 62 26        mov di, 0x2662
2D30  0E              push cs
2D31  57              push di
2D32  BF 73 26        mov di, 0x2673
2D35  0E              push cs
2D36  57              push di
2D37  8D BE F8 FE     lea di, [bp - 0x108]
2D3B  16              push ss
2D3C  57              push di
2D3D  FF 76 04        push word ptr [bp + 4]
2D40  E8 88 DD        call 0xacb
2D43  E8 19 DA        call 0x75f
loc_2D46:
2D46  E9 D0 00        jmp 0x2e19
loc_2D49:
2D49  B8 06 00        mov ax, 6
2D4C  50              push ax
2D4D  9A B1 06 4B 21  call far 214B:06B1
2D52  3D 01 00        cmp ax, 1
2D55  75 1C           jne 0x2d73
2D57  BF 83 26        mov di, 0x2683
2D5A  0E              push cs
2D5B  57              push di
2D5C  8D BE F8 FE     lea di, [bp - 0x108]
2D60  16              push ss
2D61  57              push di
2D62  FF 76 04        push word ptr [bp + 4]
2D65  E8 63 DD        call 0xacb
2D68  BF FE 23        mov di, 0x23fe
2D6B  0E              push cs
2D6C  57              push di
2D6D  E8 EF D9        call 0x75f
2D70  E9 A6 00        jmp 0x2e19
loc_2D73:
2D73  3D 02 00        cmp ax, 2
2D76  75 1C           jne 0x2d94
2D78  BF 94 26        mov di, 0x2694
2D7B  0E              push cs
2D7C  57              push di
2D7D  8D BE F8 FE     lea di, [bp - 0x108]
2D81  16              push ss
2D82  57              push di
2D83  FF 76 04        push word ptr [bp + 4]
2D86  E8 42 DD        call 0xacb
2D89  BF FE 23        mov di, 0x23fe
2D8C  0E              push cs
2D8D  57              push di
2D8E  E8 CE D9        call 0x75f
2D91  E9 85 00        jmp 0x2e19
loc_2D94:
2D94  3D 03 00        cmp ax, 3
2D97  75 1B           jne 0x2db4
2D99  BF A8 26        mov di, 0x26a8
2D9C  0E              push cs
2D9D  57              push di
2D9E  BF E4 23        mov di, 0x23e4
2DA1  0E              push cs
2DA2  57              push di
2DA3  8D BE F8 FE     lea di, [bp - 0x108]
2DA7  16              push ss
2DA8  57              push di
2DA9  FF 76 04        push word ptr [bp + 4]
2DAC  E8 1C DD        call 0xacb
2DAF  E8 AD D9        call 0x75f
2DB2  EB 65           jmp 0x2e19
loc_2DB4:
2DB4  3D 04 00        cmp ax, 4
2DB7  75 22           jne 0x2ddb
2DB9  8D BE F8 FE     lea di, [bp - 0x108]
2DBD  16              push ss
2DBE  57              push di
2DBF  FF 76 04        push word ptr [bp + 4]
2DC2  E8 88 DD        call 0xb4d
2DC5  BF B3 26        mov di, 0x26b3
2DC8  0E              push cs
2DC9  57              push di
2DCA  8D BE F8 FD     lea di, [bp - 0x208]
2DCE  16              push ss
2DCF  57              push di
2DD0  FF 76 04        push word ptr [bp + 4]
2DD3  E8 F5 DC        call 0xacb
2DD6  E8 86 D9        call 0x75f
2DD9  EB 3E           jmp 0x2e19
loc_2DDB:
2DDB  3D 05 00        cmp ax, 5
2DDE  75 1B           jne 0x2dfb
2DE0  BF C2 26        mov di, 0x26c2
2DE3  0E              push cs
2DE4  57              push di
2DE5  BF D4 26        mov di, 0x26d4
2DE8  0E              push cs
2DE9  57              push di
2DEA  8D BE F8 FE     lea di, [bp - 0x108]
2DEE  16              push ss
2DEF  57              push di
2DF0  FF 76 04        push word ptr [bp + 4]
2DF3  E8 D5 DC        call 0xacb
2DF6  E8 66 D9        call 0x75f
2DF9  EB 1E           jmp 0x2e19
loc_2DFB:
2DFB  3D 06 00        cmp ax, 6
2DFE  75 19           jne 0x2e19
2E00  BF DC 26        mov di, 0x26dc
2E03  0E              push cs
2E04  57              push di
2E05  BF E7 26        mov di, 0x26e7
2E08  0E              push cs
2E09  57              push di
2E0A  8D BE F8 FE     lea di, [bp - 0x108]
2E0E  16              push ss
2E0F  57              push di
2E10  FF 76 04        push word ptr [bp + 4]
2E13  E8 B5 DC        call 0xacb
2E16  E8 46 D9        call 0x75f
loc_2E19:
2E19  89 EC           mov sp, bp
2E1B  5D              pop bp
2E1C  C2 02 00        ret 2

