; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 4 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:1FDD  (found by: call)
sub_1FDD:
1FDD  55              push bp
1FDE  89 E5           mov bp, sp
1FE0  83 EC 08        sub sp, 8
1FE3  8B 46 04        mov ax, word ptr [bp + 4]
1FE6  D1 E0           shl ax, 1
1FE8  8B C8           mov cx, ax
1FEA  8A 46 08        mov al, byte ptr [bp + 8]
1FED  98              cwde
1FEE  BA 0A 00        mov dx, 0xa
1FF1  F7 E2           mul dx
1FF3  8B F8           mov di, ax
1FF5  03 F9           add di, cx
1FF7  31 C0           xor ax, ax
1FF9  89 85 76 99     mov word ptr [di - 0x668a], ax
1FFD  83 7E 04 05     cmp word ptr [bp + 4], 5
2001  74 04           je 0x2007
2003  B0 00           mov al, 0
2005  EB 02           jmp 0x2009
loc_2007:
2007  B0 01           mov al, 1
loc_2009:
2009  98              cwde
200A  8B F8           mov di, ax
200C  8A 85 64 07     mov al, byte ptr [di + 0x764]
2010  30 E4           xor ah, ah
2012  40              inc ax
2013  3D 0B 00        cmp ax, 0xb
2016  76 03           jbe 0x201b
2018  E9 C2 00        jmp 0x20dd
loc_201B:
201B  89 46 FE        mov word ptr [bp - 2], ax
201E  EB 03           jmp 0x2023
loc_2020:
2020  FF 46 FE        inc word ptr [bp - 2]
loc_2023:
2023  8A 46 08        mov al, byte ptr [bp + 8]
2026  98              cwde
2027  8B F8           mov di, ax
2029  8A 85 68 06     mov al, byte ptr [di + 0x668]
202D  30 E4           xor ah, ah
202F  03 46 FE        add ax, word ptr [bp - 2]
2032  89 46 FC        mov word ptr [bp - 4], ax
2035  8B 46 FC        mov ax, word ptr [bp - 4]
2038  BA 16 00        mov dx, 0x16
203B  F7 E2           mul dx
203D  8B F8           mov di, ax
203F  81 C7 E8 80     add di, 0x80e8
2043  89 7E F8        mov word ptr [bp - 8], di
2046  8C 5E FA        mov word ptr [bp - 6], ds
2049  C4 7E F8        les di, ptr [bp - 8]
204C  26 FF 75 0D     push word ptr es:[di + 0xd]
2050  9A 16 32 71 17  call far 1771:3216
2055  08 C0           or al, al
2057  75 7B           jne 0x20d4
2059  8B 46 04        mov ax, word ptr [bp + 4]
205C  D1 E0           shl ax, 1
205E  8B C8           mov cx, ax
2060  8A 46 08        mov al, byte ptr [bp + 8]
2063  98              cwde
2064  BA 0A 00        mov dx, 0xa
2067  F7 E2           mul dx
2069  8B F8           mov di, ax
206B  03 F9           add di, cx
206D  83 BD 76 99 00  cmp word ptr [di - 0x668a], 0
2072  74 41           je 0x20b5
2074  FF 76 06        push word ptr [bp + 6]
2077  8B 46 04        mov ax, word ptr [bp + 4]
207A  D1 E0           shl ax, 1
207C  8B C8           mov cx, ax
207E  8A 46 08        mov al, byte ptr [bp + 8]
2081  98              cwde
2082  BA 0A 00        mov dx, 0xa
2085  F7 E2           mul dx
2087  8B F8           mov di, ax
2089  03 F9           add di, cx
208B  FF B5 76 99     push word ptr [di - 0x668a]
208F  E8 8E 88        call 0xffffa920
2092  BA 16 00        mov dx, 0x16
2095  F7 E2           mul dx
2097  8B F8           mov di, ax
2099  81 C7 E8 80     add di, 0x80e8
209D  1E              push ds
209E  57              push di
209F  0E              push cs
20A0  E8 E7 06        call 0x278a
20A3  50              push ax
20A4  FF 76 06        push word ptr [bp + 6]
20A7  C4 7E F8        les di, ptr [bp - 8]
20AA  06              push es
20AB  57              push di
20AC  0E              push cs
20AD  E8 DA 06        call 0x278a
20B0  5A              pop dx
20B1  3B C2           cmp ax, dx
20B3  76 1F           jbe 0x20d4
loc_20B5:
20B5  C4 7E F8        les di, ptr [bp - 8]
20B8  26 8B 5D 0D     mov bx, word ptr es:[di + 0xd]
20BC  8B 46 04        mov ax, word ptr [bp + 4]
20BF  D1 E0           shl ax, 1
20C1  8B C8           mov cx, ax
20C3  8A 46 08        mov al, byte ptr [bp + 8]
20C6  98              cwde
20C7  BA 0A 00        mov dx, 0xa
20CA  F7 E2           mul dx
20CC  8B F8           mov di, ax
20CE  03 F9           add di, cx
20D0  89 9D 76 99     mov word ptr [di - 0x668a], bx
loc_20D4:
20D4  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
20D8  74 03           je 0x20dd
20DA  E9 43 FF        jmp 0x2020
loc_20DD:
20DD  89 EC           mov sp, bp
20DF  5D              pop bp
20E0  C2 06 00        ret 6

; ---- routine 0791:20E3  (found by: call)
sub_20E3:
20E3  55              push bp
20E4  89 E5           mov bp, sp
20E6  83 EC 0C        sub sp, 0xc
20E9  C6 46 FF 00     mov byte ptr [bp - 1], 0
20ED  EB 03           jmp 0x20f2
loc_20EF:
20EF  FE 46 FF        inc byte ptr [bp - 1]
loc_20F2:
20F2  8A 46 FF        mov al, byte ptr [bp - 1]
20F5  98              cwde
20F6  8B F8           mov di, ax
20F8  D1 E7           shl di, 1
20FA  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
20FE  BA BF 00        mov dx, 0xbf
2101  F7 E2           mul dx
2103  C4 3E 17 A9     les di, ptr [0xa917]
2107  03 F8           add di, ax
2109  89 7E F8        mov word ptr [bp - 8], di
210C  8C 46 FA        mov word ptr [bp - 6], es
210F  8A 46 FF        mov al, byte ptr [bp - 1]
2112  98              cwde
2113  8B F8           mov di, ax
2115  D1 E7           shl di, 1
2117  FF B5 34 9B     push word ptr [di - 0x64cc]
211B  9A 77 0B 71 17  call far 1771:0B77
2120  88 46 FE        mov byte ptr [bp - 2], al
2123  80 7E FE 00     cmp byte ptr [bp - 2], 0
2127  74 07           je 0x2130
2129  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
212E  75 44           jne 0x2174
loc_2130:
2130  80 7E FE 00     cmp byte ptr [bp - 2], 0
2134  75 18           jne 0x214e
2136  8A 46 FF        mov al, byte ptr [bp - 1]
2139  50              push ax
213A  E8 FF FD        call 0x1f3c
213D  8B C8           mov cx, ax
213F  8A 46 FF        mov al, byte ptr [bp - 1]
2142  98              cwde
2143  BA 0A 00        mov dx, 0xa
2146  F7 E2           mul dx
2148  8B F8           mov di, ax
214A  89 8D 78 99     mov word ptr [di - 0x6688], cx
loc_214E:
214E  C7 46 FC 02 00  mov word ptr [bp - 4], 2
2153  EB 03           jmp 0x2158
loc_2155:
2155  FF 46 FC        inc word ptr [bp - 4]
loc_2158:
2158  8A 46 FF        mov al, byte ptr [bp - 1]
215B  50              push ax
215C  8B 7E FC        mov di, word ptr [bp - 4]
215F  8A 85 64 07     mov al, byte ptr [di + 0x764]
2163  30 E4           xor ah, ah
2165  50              push ax
2166  FF 76 FC        push word ptr [bp - 4]
2169  E8 71 FE        call 0x1fdd
216C  83 7E FC 05     cmp word ptr [bp - 4], 5
2170  75 E3           jne 0x2155
2172  EB 4A           jmp 0x21be
loc_2174:
2174  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
2179  74 43           je 0x21be
217B  8A 46 FF        mov al, byte ptr [bp - 1]
217E  98              cwde
217F  BA 0A 00        mov dx, 0xa
2182  F7 E2           mul dx
2184  8B F8           mov di, ax
2186  FF B5 78 99     push word ptr [di - 0x6688]
218A  9A 16 32 71 17  call far 1771:3216
218F  08 C0           or al, al
2191  75 10           jne 0x21a3
2193  8A 46 FF        mov al, byte ptr [bp - 1]
2196  50              push ax
2197  B8 01 00        mov ax, 1
219A  50              push ax
219B  E8 C7 49        call 0x6b65
219E  3D 0B 00        cmp ax, 0xb
21A1  76 1B           jbe 0x21be
loc_21A3:
21A3  8A 46 FF        mov al, byte ptr [bp - 1]
21A6  50              push ax
21A7  B0 01           mov al, 1
21A9  50              push ax
21AA  E8 CE AA        call 0xffffcc7b
21AD  8B C8           mov cx, ax
21AF  8A 46 FF        mov al, byte ptr [bp - 1]
21B2  98              cwde
21B3  BA 0A 00        mov dx, 0xa
21B6  F7 E2           mul dx
21B8  8B F8           mov di, ax
21BA  89 8D 78 99     mov word ptr [di - 0x6688], cx
loc_21BE:
21BE  C7 46 FC 01 00  mov word ptr [bp - 4], 1
21C3  EB 03           jmp 0x21c8
loc_21C5:
21C5  FF 46 FC        inc word ptr [bp - 4]
loc_21C8:
21C8  8A 46 FF        mov al, byte ptr [bp - 1]
21CB  98              cwde
21CC  8B F8           mov di, ax
21CE  8A 85 68 06     mov al, byte ptr [di + 0x668]
21D2  30 E4           xor ah, ah
21D4  03 46 FC        add ax, word ptr [bp - 4]
21D7  BA 16 00        mov dx, 0x16
21DA  F7 E2           mul dx
21DC  8B F8           mov di, ax
21DE  81 C7 E8 80     add di, 0x80e8
21E2  89 7E F4        mov word ptr [bp - 0xc], di
21E5  8C 5E F6        mov word ptr [bp - 0xa], ds
21E8  8A 46 FF        mov al, byte ptr [bp - 1]
21EB  98              cwde
21EC  BA 0A 00        mov dx, 0xa
21EF  F7 E2           mul dx
21F1  8B F8           mov di, ax
21F3  FF B5 78 99     push word ptr [di - 0x6688]
21F7  9A D9 30 71 17  call far 1771:30D9
21FC  D1 E0           shl ax, 1
21FE  C4 7E F4        les di, ptr [bp - 0xc]
2201  26 00 45 11     add byte ptr es:[di + 0x11], al
2205  83 7E FC 0B     cmp word ptr [bp - 4], 0xb
2209  75 BA           jne 0x21c5
220B  80 7E FF 01     cmp byte ptr [bp - 1], 1
220F  74 03           je 0x2214
2211  E9 DB FE        jmp 0x20ef
loc_2214:
2214  89 EC           mov sp, bp
2216  5D              pop bp
2217  C3              ret

; ---- routine 0791:2218  (found by: call)
sub_2218:
2218  55              push bp
2219  89 E5           mov bp, sp
221B  83 EC 04        sub sp, 4
221E  8B 7E 04        mov di, word ptr [bp + 4]
2221  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
2225  98              cwde
2226  8B F8           mov di, ax
2228  D1 E7           shl di, 1
222A  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
222E  BA BF 00        mov dx, 0xbf
2231  F7 E2           mul dx
2233  C4 3E 17 A9     les di, ptr [0xa917]
2237  03 F8           add di, ax
2239  89 7E FC        mov word ptr [bp - 4], di
223C  8C 46 FE        mov word ptr [bp - 2], es
223F  8B 7E 04        mov di, word ptr [bp + 4]
2242  36 8B 45 FD     mov ax, word ptr ss:[di - 3]
2246  D1 E0           shl ax, 1
2248  C4 7E FC        les di, ptr [bp - 4]
224B  03 F8           add di, ax
224D  81 C7 FE FF     add di, 0xfffe
2251  06              push es
2252  57              push di
2253  8B 7E 04        mov di, word ptr [bp + 4]
2256  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
225A  D1 E0           shl ax, 1
225C  C4 7E FC        les di, ptr [bp - 4]
225F  03 F8           add di, ax
2261  81 C7 FE FF     add di, 0xfffe
2265  06              push es
2266  57              push di
2267  B8 02 00        mov ax, 2
226A  50              push ax
226B  9A 7B 00 4B 21  call far 214B:007B
2270  8B 7E 04        mov di, word ptr [bp + 4]
2273  36 8B 45 FD     mov ax, word ptr ss:[di - 3]
2277  8B C8           mov cx, ax
2279  8B 7E 04        mov di, word ptr [bp + 4]
227C  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
2280  98              cwde
2281  BA 14 00        mov dx, 0x14
2284  F7 E2           mul dx
2286  8B F8           mov di, ax
2288  03 F9           add di, cx
228A  81 C7 07 9B     add di, 0x9b07
228E  1E              push ds
228F  57              push di
2290  8B 7E 04        mov di, word ptr [bp + 4]
2293  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
2297  8B C8           mov cx, ax
2299  8B 7E 04        mov di, word ptr [bp + 4]
229C  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
22A0  98              cwde
22A1  BA 14 00        mov dx, 0x14
22A4  F7 E2           mul dx
22A6  8B F8           mov di, ax
22A8  03 F9           add di, cx
22AA  81 C7 07 9B     add di, 0x9b07
22AE  1E              push ds
22AF  57              push di
22B0  B8 01 00        mov ax, 1
22B3  50              push ax
22B4  9A 7B 00 4B 21  call far 214B:007B
22B9  8B 7E 04        mov di, word ptr [bp + 4]
22BC  36 8B 45 FD     mov ax, word ptr ss:[di - 3]
22C0  D1 E0           shl ax, 1
22C2  8B C8           mov cx, ax
22C4  8B 7E 04        mov di, word ptr [bp + 4]
22C7  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
22CB  98              cwde
22CC  BA 28 00        mov dx, 0x28
22CF  F7 E2           mul dx
22D1  8B F8           mov di, ax
22D3  03 F9           add di, cx
22D5  81 C7 3E 9A     add di, 0x9a3e
22D9  1E              push ds
22DA  57              push di
22DB  8B 7E 04        mov di, word ptr [bp + 4]
22DE  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
22E2  D1 E0           shl ax, 1
22E4  8B C8           mov cx, ax
22E6  8B 7E 04        mov di, word ptr [bp + 4]
22E9  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
22ED  98              cwde
22EE  BA 28 00        mov dx, 0x28
22F1  F7 E2           mul dx
22F3  8B F8           mov di, ax
22F5  03 F9           add di, cx
22F7  81 C7 3E 9A     add di, 0x9a3e
22FB  1E              push ds
22FC  57              push di
22FD  B8 02 00        mov ax, 2
2300  50              push ax
2301  9A 7B 00 4B 21  call far 214B:007B
2306  89 EC           mov sp, bp
2308  5D              pop bp
2309  C2 02 00        ret 2

; ---- routine 0791:230C  (found by: call)
sub_230C:
230C  55              push bp
230D  89 E5           mov bp, sp
230F  83 EC 1A        sub sp, 0x1a
2312  C6 46 FF 00     mov byte ptr [bp - 1], 0
2316  EB 03           jmp 0x231b
loc_2318:
2318  FE 46 FF        inc byte ptr [bp - 1]
loc_231B:
231B  8A 46 FF        mov al, byte ptr [bp - 1]
231E  98              cwde
231F  8B F8           mov di, ax
2321  D1 E7           shl di, 1
2323  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
2327  BA BF 00        mov dx, 0xbf
232A  F7 E2           mul dx
232C  C4 3E 17 A9     les di, ptr [0xa917]
2330  03 F8           add di, ax
2332  89 7E EA        mov word ptr [bp - 0x16], di
2335  8C 46 EC        mov word ptr [bp - 0x14], es
2338  C7 46 FD 01 00  mov word ptr [bp - 3], 1
233D  EB 03           jmp 0x2342
loc_233F:
233F  FF 46 FD        inc word ptr [bp - 3]
loc_2342:
2342  8B 46 FD        mov ax, word ptr [bp - 3]
2345  D1 E0           shl ax, 1
2347  C4 7E EA        les di, ptr [bp - 0x16]
234A  03 F8           add di, ax
234C  26 8B 45 FE     mov ax, word ptr es:[di - 2]
2350  BA 14 00        mov dx, 0x14
2353  F7 E2           mul dx
2355  C4 3E 1B A9     les di, ptr [0xa91b]
2359  03 F8           add di, ax
235B  89 7E E6        mov word ptr [bp - 0x1a], di
235E  8C 46 E8        mov word ptr [bp - 0x18], es
2361  8B 46 FD        mov ax, word ptr [bp - 3]
2364  D1 E0           shl ax, 1
2366  C4 7E EA        les di, ptr [bp - 0x16]
2369  03 F8           add di, ax
236B  26 FF 75 FE     push word ptr es:[di - 2]
236F  9A 16 32 71 17  call far 1771:3216
2374  08 C0           or al, al
2376  74 09           je 0x2381
2378  8B 7E FD        mov di, word ptr [bp - 3]
237B  C6 43 ED 0E     mov byte ptr [bp + di - 0x13], 0xe
237F  EB 0D           jmp 0x238e
loc_2381:
2381  C4 7E E6        les di, ptr [bp - 0x1a]
2384  26 8A 45 06     mov al, byte ptr es:[di + 6]
2388  8B 7E FD        mov di, word ptr [bp - 3]
238B  88 43 ED        mov byte ptr [bp + di - 0x13], al
loc_238E:
238E  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
2392  75 AB           jne 0x233f
2394  C7 46 FB 01 00  mov word ptr [bp - 5], 1
2399  EB 03           jmp 0x239e
loc_239B:
239B  FF 46 FB        inc word ptr [bp - 5]
loc_239E:
239E  8B 46 FB        mov ax, word ptr [bp - 5]
23A1  40              inc ax
23A2  3D 0B 00        cmp ax, 0xb
23A5  76 03           jbe 0x23aa
23A7  E9 8E 01        jmp 0x2538
loc_23AA:
23AA  89 46 FD        mov word ptr [bp - 3], ax
23AD  EB 03           jmp 0x23b2
loc_23AF:
23AF  FF 46 FD        inc word ptr [bp - 3]
loc_23B2:
23B2  8B 7E FD        mov di, word ptr [bp - 3]
23B5  8A 43 ED        mov al, byte ptr [bp + di - 0x13]
23B8  8B 7E FB        mov di, word ptr [bp - 5]
23BB  3A 43 ED        cmp al, byte ptr [bp + di - 0x13]
23BE  72 03           jb 0x23c3
23C0  E9 6C 01        jmp 0x252f
loc_23C3:
23C3  55              push bp
23C4  E8 51 FE        call 0x2218
23C7  8B 7E FD        mov di, word ptr [bp - 3]
23CA  8D 7B ED        lea di, [bp + di - 0x13]
23CD  16              push ss
23CE  57              push di
23CF  8B 7E FB        mov di, word ptr [bp - 5]
23D2  8D 7B ED        lea di, [bp + di - 0x13]
23D5  16              push ss
23D6  57              push di
23D7  B8 01 00        mov ax, 1
23DA  50              push ax
23DB  9A 7B 00 4B 21  call far 214B:007B
23E0  8A 46 FF        mov al, byte ptr [bp - 1]
23E3  98              cwde
23E4  8B F8           mov di, ax
23E6  8A 85 68 06     mov al, byte ptr [di + 0x668]
23EA  30 E4           xor ah, ah
23EC  03 46 FD        add ax, word ptr [bp - 3]
23EF  BA 16 00        mov dx, 0x16
23F2  F7 E2           mul dx
23F4  8B F8           mov di, ax
23F6  81 C7 E8 80     add di, 0x80e8
23FA  1E              push ds
23FB  57              push di
23FC  8A 46 FF        mov al, byte ptr [bp - 1]
23FF  98              cwde
2400  8B F8           mov di, ax
2402  8A 85 68 06     mov al, byte ptr [di + 0x668]
2406  30 E4           xor ah, ah
2408  03 46 FB        add ax, word ptr [bp - 5]
240B  BA 16 00        mov dx, 0x16
240E  F7 E2           mul dx
2410  8B F8           mov di, ax
2412  81 C7 E8 80     add di, 0x80e8
2416  1E              push ds
2417  57              push di
2418  B8 16 00        mov ax, 0x16
241B  50              push ax
241C  9A 7B 00 4B 21  call far 214B:007B
2421  8A 46 FF        mov al, byte ptr [bp - 1]
2424  98              cwde
2425  8B F8           mov di, ax
2427  8A 85 68 06     mov al, byte ptr [di + 0x668]
242B  30 E4           xor ah, ah
242D  03 46 FD        add ax, word ptr [bp - 3]
2430  8B D0           mov dx, ax
2432  A0 0B 83        mov al, byte ptr [0x830b]
2435  30 E4           xor ah, ah
2437  3B C2           cmp ax, dx
2439  75 14           jne 0x244f
243B  8A 46 FF        mov al, byte ptr [bp - 1]
243E  98              cwde
243F  8B F8           mov di, ax
2441  8A 85 68 06     mov al, byte ptr [di + 0x668]
2445  30 E4           xor ah, ah
2447  03 46 FB        add ax, word ptr [bp - 5]
244A  A2 0B 83        mov byte ptr [0x830b], al
244D  EB 2C           jmp 0x247b
loc_244F:
244F  8A 46 FF        mov al, byte ptr [bp - 1]
2452  98              cwde
2453  8B F8           mov di, ax
2455  8A 85 68 06     mov al, byte ptr [di + 0x668]
2459  30 E4           xor ah, ah
245B  03 46 FB        add ax, word ptr [bp - 5]
245E  8B D0           mov dx, ax
2460  A0 0B 83        mov al, byte ptr [0x830b]
2463  30 E4           xor ah, ah
2465  3B C2           cmp ax, dx
2467  75 12           jne 0x247b
2469  8A 46 FF        mov al, byte ptr [bp - 1]
246C  98              cwde
246D  8B F8           mov di, ax
246F  8A 85 68 06     mov al, byte ptr [di + 0x668]
2473  30 E4           xor ah, ah
2475  03 46 FD        add ax, word ptr [bp - 3]
2478  A2 0B 83        mov byte ptr [0x830b], al
loc_247B:
247B  8A 46 FF        mov al, byte ptr [bp - 1]
247E  98              cwde
247F  8B F8           mov di, ax
2481  8A 85 68 06     mov al, byte ptr [di + 0x668]
2485  30 E4           xor ah, ah
2487  03 46 FD        add ax, word ptr [bp - 3]
248A  8B D0           mov dx, ax
248C  A0 0C 83        mov al, byte ptr [0x830c]
248F  30 E4           xor ah, ah
2491  3B C2           cmp ax, dx
2493  75 14           jne 0x24a9
2495  8A 46 FF        mov al, byte ptr [bp - 1]
2498  98              cwde
2499  8B F8           mov di, ax
249B  8A 85 68 06     mov al, byte ptr [di + 0x668]
249F  30 E4           xor ah, ah
24A1  03 46 FB        add ax, word ptr [bp - 5]
24A4  A2 0C 83        mov byte ptr [0x830c], al
24A7  EB 2C           jmp 0x24d5
loc_24A9:
24A9  8A 46 FF        mov al, byte ptr [bp - 1]
24AC  98              cwde
24AD  8B F8           mov di, ax
24AF  8A 85 68 06     mov al, byte ptr [di + 0x668]
24B3  30 E4           xor ah, ah
24B5  03 46 FB        add ax, word ptr [bp - 5]
24B8  8B D0           mov dx, ax
24BA  A0 0C 83        mov al, byte ptr [0x830c]
24BD  30 E4           xor ah, ah
24BF  3B C2           cmp ax, dx
24C1  75 12           jne 0x24d5
24C3  8A 46 FF        mov al, byte ptr [bp - 1]
24C6  98              cwde
24C7  8B F8           mov di, ax
24C9  8A 85 68 06     mov al, byte ptr [di + 0x668]
24CD  30 E4           xor ah, ah
24CF  03 46 FD        add ax, word ptr [bp - 3]
24D2  A2 0C 83        mov byte ptr [0x830c], al
loc_24D5:
24D5  8A 46 FF        mov al, byte ptr [bp - 1]
24D8  98              cwde
24D9  8B F8           mov di, ax
24DB  8A 85 68 06     mov al, byte ptr [di + 0x668]
24DF  30 E4           xor ah, ah
24E1  03 46 FD        add ax, word ptr [bp - 3]
24E4  8B D0           mov dx, ax
24E6  A0 0D 83        mov al, byte ptr [0x830d]
24E9  30 E4           xor ah, ah
24EB  3B C2           cmp ax, dx
24ED  75 14           jne 0x2503
24EF  8A 46 FF        mov al, byte ptr [bp - 1]
24F2  98              cwde
24F3  8B F8           mov di, ax
24F5  8A 85 68 06     mov al, byte ptr [di + 0x668]
24F9  30 E4           xor ah, ah
24FB  03 46 FB        add ax, word ptr [bp - 5]
24FE  A2 0D 83        mov byte ptr [0x830d], al
2501  EB 2C           jmp 0x252f
loc_2503:
2503  8A 46 FF        mov al, byte ptr [bp - 1]
2506  98              cwde
2507  8B F8           mov di, ax
2509  8A 85 68 06     mov al, byte ptr [di + 0x668]
250D  30 E4           xor ah, ah
250F  03 46 FB        add ax, word ptr [bp - 5]
2512  8B D0           mov dx, ax
2514  A0 0D 83        mov al, byte ptr [0x830d]
2517  30 E4           xor ah, ah
2519  3B C2           cmp ax, dx
251B  75 12           jne 0x252f
251D  8A 46 FF        mov al, byte ptr [bp - 1]
2520  98              cwde
2521  8B F8           mov di, ax
2523  8A 85 68 06     mov al, byte ptr [di + 0x668]
2527  30 E4           xor ah, ah
2529  03 46 FD        add ax, word ptr [bp - 3]
252C  A2 0D 83        mov byte ptr [0x830d], al
loc_252F:
252F  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
2533  74 03           je 0x2538
2535  E9 77 FE        jmp 0x23af
loc_2538:
2538  83 7E FB 0A     cmp word ptr [bp - 5], 0xa
253C  74 03           je 0x2541
253E  E9 5A FE        jmp 0x239b
loc_2541:
2541  8A 46 FF        mov al, byte ptr [bp - 1]
2544  98              cwde
2545  8B F8           mov di, ax
2547  8A 85 68 06     mov al, byte ptr [di + 0x668]
254B  30 E4           xor ah, ah
254D  05 0B 00        add ax, 0xb
2550  89 46 E8        mov word ptr [bp - 0x18], ax
2553  8A 46 FF        mov al, byte ptr [bp - 1]
2556  98              cwde
2557  8B F8           mov di, ax
2559  8A 85 68 06     mov al, byte ptr [di + 0x668]
255D  30 E4           xor ah, ah
255F  40              inc ax
2560  3B 46 E8        cmp ax, word ptr [bp - 0x18]
2563  77 27           ja 0x258c
2565  89 46 FD        mov word ptr [bp - 3], ax
2568  EB 03           jmp 0x256d
loc_256A:
256A  FF 46 FD        inc word ptr [bp - 3]
loc_256D:
256D  FF 76 FD        push word ptr [bp - 3]
2570  8B 46 FD        mov ax, word ptr [bp - 3]
2573  BA 16 00        mov dx, 0x16
2576  F7 E2           mul dx
2578  8B F8           mov di, ax
257A  81 C7 E8 80     add di, 0x80e8
257E  1E              push ds
257F  57              push di
2580  0E              push cs
2581  E8 DC 7C        call 0xa260
2584  8B 46 FD        mov ax, word ptr [bp - 3]
2587  3B 46 E8        cmp ax, word ptr [bp - 0x18]
258A  75 DE           jne 0x256a
loc_258C:
258C  C7 46 FB 0C 00  mov word ptr [bp - 5], 0xc
2591  EB 03           jmp 0x2596
loc_2593:
2593  FF 46 FB        inc word ptr [bp - 5]
loc_2596:
2596  8B 46 FB        mov ax, word ptr [bp - 5]
2599  40              inc ax
259A  3D 14 00        cmp ax, 0x14
259D  77 50           ja 0x25ef
259F  89 46 FD        mov word ptr [bp - 3], ax
25A2  EB 03           jmp 0x25a7
loc_25A4:
25A4  FF 46 FD        inc word ptr [bp - 3]
loc_25A7:
25A7  8B 46 FB        mov ax, word ptr [bp - 5]
25AA  D1 E0           shl ax, 1
25AC  C4 7E EA        les di, ptr [bp - 0x16]
25AF  03 F8           add di, ax
25B1  26 8B 45 FE     mov ax, word ptr es:[di - 2]
25B5  BA 14 00        mov dx, 0x14
25B8  F7 E2           mul dx
25BA  C4 3E 1B A9     les di, ptr [0xa91b]
25BE  03 F8           add di, ax
25C0  26 8A 4D 06     mov cl, byte ptr es:[di + 6]
25C4  8B 46 FD        mov ax, word ptr [bp - 3]
25C7  D1 E0           shl ax, 1
25C9  C4 7E EA        les di, ptr [bp - 0x16]
25CC  03 F8           add di, ax
25CE  26 8B 45 FE     mov ax, word ptr es:[di - 2]
25D2  BA 14 00        mov dx, 0x14
25D5  F7 E2           mul dx
25D7  C4 3E 1B A9     les di, ptr [0xa91b]
25DB  03 F8           add di, ax
25DD  26 8A 45 06     mov al, byte ptr es:[di + 6]
25E1  3A C1           cmp al, cl
25E3  73 04           jae 0x25e9
25E5  55              push bp
25E6  E8 2F FC        call 0x2218
loc_25E9:
25E9  83 7E FD 14     cmp word ptr [bp - 3], 0x14
25ED  75 B5           jne 0x25a4
loc_25EF:
25EF  83 7E FB 13     cmp word ptr [bp - 5], 0x13
25F3  75 9E           jne 0x2593
25F5  80 7E FF 01     cmp byte ptr [bp - 1], 1
25F9  74 03           je 0x25fe
25FB  E9 1A FD        jmp 0x2318
loc_25FE:
25FE  9A F8 3E 71 17  call far 1771:3EF8
2603  E8 8B E0        call 0x691
2606  E8 DA FA        call 0x20e3
2609  E8 90 1B        call 0x419c
260C  31 C0           xor ax, ax
260E  A3 09 81        mov word ptr [0x8109], ax
2611  31 C0           xor ax, ax
2613  A3 FB 81        mov word ptr [0x81fb], ax
2616  89 EC           mov sp, bp
2618  5D              pop bp
2619  C3              ret

; ---- routine 0791:261A  (found by: call)
sub_261A:
261A  55              push bp
261B  89 E5           mov bp, sp
261D  83 EC 02        sub sp, 2
2620  8B 3E 37 84     mov di, word ptr [0x8437]
2624  8A 85 37 83     mov al, byte ptr [di - 0x7cc9]
2628  30 E4           xor ah, ah
262A  89 46 FE        mov word ptr [bp - 2], ax
262D  81 3E 37 84 FF 00 cmp word ptr [0x8437], 0xff
2633  75 08           jne 0x263d
2635  C7 06 37 84 01 00 mov word ptr [0x8437], 1
263B  EB 04           jmp 0x2641
loc_263D:
263D  FF 06 37 84     inc word ptr [0x8437]
loc_2641:
2641  8B 46 FE        mov ax, word ptr [bp - 2]
2644  89 EC           mov sp, bp
2646  5D              pop bp
2647  C3              ret

; ---- routine 0791:2648  (found by: call)
sub_2648:
2648  55              push bp
2649  89 E5           mov bp, sp
264B  83 EC 08        sub sp, 8
264E  C4 3E 23 A9     les di, ptr [0xa923]
2652  89 7E F8        mov word ptr [bp - 8], di
2655  8C 46 FA        mov word ptr [bp - 6], es
2658  C4 7E F8        les di, ptr [bp - 8]
265B  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
265F  89 46 FC        mov word ptr [bp - 4], ax
2662  C4 7E F8        les di, ptr [bp - 8]
2665  26 8B 45 38     mov ax, word ptr es:[di + 0x38]
2669  40              inc ax
266A  F7 66 FC        mul word ptr [bp - 4]
266D  C4 3E 78 A9     les di, ptr [0xa978]
2671  26 89 05        mov word ptr es:[di], ax
2674  C7 46 FE 01 00  mov word ptr [bp - 2], 1
2679  EB 03           jmp 0x267e
loc_267B:
267B  FF 46 FE        inc word ptr [bp - 2]
loc_267E:
267E  B8 10 00        mov ax, 0x10
2681  50              push ax
2682  9A B1 06 4B 21  call far 214B:06B1
2687  48              dec ax
2688  8B 7E FE        mov di, word ptr [bp - 2]
268B  88 85 37 83     mov byte ptr [di - 0x7cc9], al
268F  81 7E FE FF 00  cmp word ptr [bp - 2], 0xff
2694  75 E5           jne 0x267b
2696  A1 36 9B        mov ax, word ptr [0x9b36]
2699  A3 37 84        mov word ptr [0x8437], ax
269C  89 EC           mov sp, bp
269E  5D              pop bp
269F  C3              ret

; ---- routine 0791:26A0  (found by: call)
sub_26A0:
26A0  55              push bp
26A1  89 E5           mov bp, sp
26A3  80 7E 04 00     cmp byte ptr [bp + 4], 0
26A7  74 08           je 0x26b1
26A9  C7 06 08 83 AF 0E mov word ptr [0x8308], 0xeaf
26AF  EB 06           jmp 0x26b7
loc_26B1:
26B1  C7 06 08 83 AE 0E mov word ptr [0x8308], 0xeae
loc_26B7:
26B7  C6 06 28 83 01  mov byte ptr [0x8328], 1
26BC  89 EC           mov sp, bp
26BE  5D              pop bp
26BF  C2 02 00        ret 2

; ---- routine 0791:26C2  (found by: call)
sub_26C2:
26C2  55              push bp
26C3  89 E5           mov bp, sp
26C5  BF 04 83        mov di, 0x8304
26C8  1E              push ds
26C9  57              push di
26CA  0E              push cs
26CB  E8 AB 69        call 0x9079
26CE  C6 06 28 83 00  mov byte ptr [0x8328], 0
26D3  89 EC           mov sp, bp
26D5  5D              pop bp
26D6  C3              ret

; ---- routine 0791:26D7  (found by: call)
sub_26D7:
26D7  55              push bp
26D8  89 E5           mov bp, sp
26DA  83 EC 02        sub sp, 2
26DD  83 7E 0A 05     cmp word ptr [bp + 0xa], 5
26E1  73 4F           jae 0x2732
26E3  8B 46 0A        mov ax, word ptr [bp + 0xa]
26E6  05 04 00        add ax, 4
26E9  50              push ax
26EA  C4 7E 06        les di, ptr [bp + 6]
26ED  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
26F1  BA 14 00        mov dx, 0x14
26F4  F7 E2           mul dx
26F6  C4 3E 1B A9     les di, ptr [0xa91b]
26FA  03 F8           add di, ax
26FC  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
2700  30 E4           xor ah, ah
2702  50              push ax
2703  9A 57 0C 4B 21  call far 214B:0C57
2708  08 C0           or al, al
270A  74 26           je 0x2732
270C  FF 76 0A        push word ptr [bp + 0xa]
270F  C4 7E 06        les di, ptr [bp + 6]
2712  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
2716  BA 14 00        mov dx, 0x14
2719  F7 E2           mul dx
271B  C4 3E 1B A9     les di, ptr [0xa91b]
271F  03 F8           add di, ax
2721  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
2725  30 E4           xor ah, ah
2727  50              push ax
2728  9A 57 0C 4B 21  call far 214B:0C57
272D  88 46 FF        mov byte ptr [bp - 1], al
2730  EB 2F           jmp 0x2761
loc_2732:
2732  FF 76 0A        push word ptr [bp + 0xa]
2735  C4 7E 06        les di, ptr [bp + 6]
2738  06              push es
2739  57              push di
273A  0E              push cs
273B  E8 36 02        call 0x2974
273E  98              cwde
273F  8B F8           mov di, ax
2741  D1 E7           shl di, 1
2743  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
2747  BA BF 00        mov dx, 0xbf
274A  F7 E2           mul dx
274C  C4 3E 17 A9     les di, ptr [0xa917]
2750  03 F8           add di, ax
2752  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
2756  30 E4           xor ah, ah
2758  50              push ax
2759  9A 57 0C 4B 21  call far 214B:0C57
275E  88 46 FF        mov byte ptr [bp - 1], al
loc_2761:
2761  8A 46 FF        mov al, byte ptr [bp - 1]
2764  89 EC           mov sp, bp
2766  5D              pop bp
2767  CA 06 00        retf 6
; data (not reached as code), 32 bytes
276A                  db 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
277A                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:278A  (found by: call)
sub_278A:
278A  55              push bp
278B  89 E5           mov bp, sp
278D  83 EC 0A        sub sp, 0xa
2790  C4 7E 06        les di, ptr [bp + 6]
2793  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
2797  BA 14 00        mov dx, 0x14
279A  F7 E2           mul dx
279C  C4 3E 1B A9     les di, ptr [0xa91b]
27A0  03 F8           add di, ax
27A2  89 7E F6        mov word ptr [bp - 0xa], di
27A5  8C 46 F8        mov word ptr [bp - 8], es
27A8  C4 7E F6        les di, ptr [bp - 0xa]
27AB  26 80 7D 0C 20  cmp byte ptr es:[di + 0xc], 0x20
27B0  7D 0E           jge 0x27c0
27B2  C4 7E F6        les di, ptr [bp - 0xa]
27B5  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
27B9  98              cwde
27BA  40              inc ax
27BB  89 46 FC        mov word ptr [bp - 4], ax
27BE  EB 05           jmp 0x27c5
loc_27C0:
27C0  31 C0           xor ax, ax
27C2  89 46 FC        mov word ptr [bp - 4], ax
loc_27C5:
27C5  83 7E 0A 0C     cmp word ptr [bp + 0xa], 0xc
27C9  72 06           jb 0x27d1
27CB  83 46 FC 20     add word ptr [bp - 4], 0x20
27CF  EB 0B           jmp 0x27dc
loc_27D1:
27D1  C4 7E F6        les di, ptr [bp - 0xa]
27D4  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
27D8  98              cwde
27D9  01 46 FC        add word ptr [bp - 4], ax
loc_27DC:
27DC  C4 7E 06        les di, ptr [bp + 6]
27DF  26 FF 75 0D     push word ptr es:[di + 0xd]
27E3  FF 76 0A        push word ptr [bp + 0xa]
27E6  9A 06 3A 71 17  call far 1771:3A06
27EB  89 46 FA        mov word ptr [bp - 6], ax
27EE  C4 7E 06        les di, ptr [bp + 6]
27F1  26 80 7D 13 00  cmp byte ptr es:[di + 0x13], 0
27F6  74 0D           je 0x2805
27F8  8B 46 FA        mov ax, word ptr [bp - 6]
27FB  31 D2           xor dx, dx
27FD  B9 02 00        mov cx, 2
2800  F7 F1           div cx
2802  89 46 FA        mov word ptr [bp - 6], ax
loc_2805:
2805  8B 46 FA        mov ax, word ptr [bp - 6]
2808  31 D2           xor dx, dx
280A  B9 04 00        mov cx, 4
280D  F7 F1           div cx
280F  8B D8           mov bx, ax
2811  8B 46 FC        mov ax, word ptr [bp - 4]
2814  F7 66 FA        mul word ptr [bp - 6]
2817  31 D2           xor dx, dx
2819  B9 00 01        mov cx, 0x100
281C  F7 F1           div cx
281E  03 C3           add ax, bx
2820  89 46 FC        mov word ptr [bp - 4], ax
2823  8B 7E 0A        mov di, word ptr [bp + 0xa]
2826  80 BD 69 07 00  cmp byte ptr [di + 0x769], 0
282B  75 16           jne 0x2843
282D  83 7E 0A 01     cmp word ptr [bp + 0xa], 1
2831  75 1C           jne 0x284f
2833  A0 27 83        mov al, byte ptr [0x8327]
2836  50              push ax
2837  BF 6A 27        mov di, 0x276a
283A  0E              push cs
283B  57              push di
283C  9A DF 08 E4 23  call far 23E4:08DF
2841  74 0C           je 0x284f
loc_2843:
2843  C4 7E 06        les di, ptr [bp + 6]
2846  26 8A 45 11     mov al, byte ptr es:[di + 0x11]
284A  30 E4           xor ah, ah
284C  01 46 FC        add word ptr [bp - 4], ax
loc_284F:
284F  C4 7E 06        les di, ptr [bp + 6]
2852  26 80 7D 06 0C  cmp byte ptr es:[di + 6], 0xc
2857  73 14           jae 0x286d
2859  80 3E FC 80 00  cmp byte ptr [0x80fc], 0
285E  74 0D           je 0x286d
2860  8B 46 FC        mov ax, word ptr [bp - 4]
2863  31 D2           xor dx, dx
2865  B9 10 00        mov cx, 0x10
2868  F7 F1           div cx
286A  01 46 FC        add word ptr [bp - 4], ax
loc_286D:
286D  8B 46 FC        mov ax, word ptr [bp - 4]
2870  89 46 FE        mov word ptr [bp - 2], ax
2873  8B 46 FE        mov ax, word ptr [bp - 2]
2876  89 EC           mov sp, bp
2878  5D              pop bp
2879  CA 06 00        retf 6

; ---- routine 0791:287C  (found by: call)
sub_287C:
287C  55              push bp
287D  89 E5           mov bp, sp
287F  83 EC 02        sub sp, 2
2882  FF 76 0A        push word ptr [bp + 0xa]
2885  C4 7E 06        les di, ptr [bp + 6]
2888  06              push es
2889  57              push di
288A  0E              push cs
288B  E8 FC FE        call 0x278a
288E  31 D2           xor dx, dx
2890  B9 20 00        mov cx, 0x20
2893  F7 F1           div cx
2895  40              inc ax
2896  50              push ax
2897  9A D0 06 4B 21  call far 214B:06D0
289C  08 C0           or al, al
289E  74 04           je 0x28a4
28A0  B0 00           mov al, 0
28A2  EB 02           jmp 0x28a6
loc_28A4:
28A4  B0 01           mov al, 1
loc_28A6:
28A6  88 46 FF        mov byte ptr [bp - 1], al
28A9  8A 46 FF        mov al, byte ptr [bp - 1]
28AC  89 EC           mov sp, bp
28AE  5D              pop bp
28AF  CA 06 00        retf 6

; ---- routine 0791:28B2  (found by: call)
sub_28B2:
28B2  55              push bp
28B3  89 E5           mov bp, sp
28B5  83 EC 0A        sub sp, 0xa
28B8  31 C0           xor ax, ax
28BA  89 46 FB        mov word ptr [bp - 5], ax
28BD  C7 46 FD 01 00  mov word ptr [bp - 3], 1
28C2  EB 03           jmp 0x28c7
loc_28C4:
28C4  FF 46 FD        inc word ptr [bp - 3]
loc_28C7:
28C7  8B 46 FD        mov ax, word ptr [bp - 3]
28CA  BA 16 00        mov dx, 0x16
28CD  F7 E2           mul dx
28CF  8B F8           mov di, ax
28D1  81 C7 E8 80     add di, 0x80e8
28D5  89 7E F7        mov word ptr [bp - 9], di
28D8  8C 5E F9        mov word ptr [bp - 7], ds
28DB  C4 7E F7        les di, ptr [bp - 9]
28DE  26 8A 45 12     mov al, byte ptr es:[di + 0x12]
28E2  3A 46 04        cmp al, byte ptr [bp + 4]
28E5  74 21           je 0x2908
28E7  A0 0B 83        mov al, byte ptr [0x830b]
28EA  30 E4           xor ah, ah
28EC  3B 46 FD        cmp ax, word ptr [bp - 3]
28EF  74 17           je 0x2908
28F1  A0 0C 83        mov al, byte ptr [0x830c]
28F4  30 E4           xor ah, ah
28F6  3B 46 FD        cmp ax, word ptr [bp - 3]
28F9  74 0D           je 0x2908
28FB  C4 7E F7        les di, ptr [bp - 9]
28FE  06              push es
28FF  57              push di
2900  0E              push cs
2901  E8 52 00        call 0x2956
2904  08 C0           or al, al
2906  74 03           je 0x290b
loc_2908:
2908  FF 46 FB        inc word ptr [bp - 5]
loc_290B:
290B  83 7E FD 16     cmp word ptr [bp - 3], 0x16
290F  75 B3           jne 0x28c4
2911  83 7E FB 16     cmp word ptr [bp - 5], 0x16
2915  74 04           je 0x291b
2917  B0 00           mov al, 0
2919  EB 02           jmp 0x291d
loc_291B:
291B  B0 01           mov al, 1
loc_291D:
291D  88 46 FF        mov byte ptr [bp - 1], al
2920  8A 46 FF        mov al, byte ptr [bp - 1]
2923  89 EC           mov sp, bp
2925  5D              pop bp
2926  C2 02 00        ret 2

; ---- routine 0791:2929  (found by: call)
sub_2929:
2929  55              push bp
292A  89 E5           mov bp, sp
292C  83 EC 02        sub sp, 2
292F  C7 46 FE 01 00  mov word ptr [bp - 2], 1
2934  EB 03           jmp 0x2939
loc_2936:
2936  FF 46 FE        inc word ptr [bp - 2]
loc_2939:
2939  8A 4E 04        mov cl, byte ptr [bp + 4]
293C  8B 46 FE        mov ax, word ptr [bp - 2]
293F  BA 16 00        mov dx, 0x16
2942  F7 E2           mul dx
2944  8B F8           mov di, ax
2946  88 8D FA 80     mov byte ptr [di - 0x7f06], cl
294A  83 7E FE 16     cmp word ptr [bp - 2], 0x16
294E  75 E6           jne 0x2936
2950  89 EC           mov sp, bp
2952  5D              pop bp
2953  C2 02 00        ret 2

; ---- routine 0791:2956  (found by: call)
sub_2956:
2956  55              push bp
2957  89 E5           mov bp, sp
2959  83 EC 02        sub sp, 2
295C  C4 7E 06        les di, ptr [bp + 6]
295F  26 FF 75 0D     push word ptr es:[di + 0xd]
2963  9A 16 32 71 17  call far 1771:3216
2968  88 46 FF        mov byte ptr [bp - 1], al
296B  8A 46 FF        mov al, byte ptr [bp - 1]
296E  89 EC           mov sp, bp
2970  5D              pop bp
2971  CA 04 00        retf 4

; ---- routine 0791:2974  (found by: call)
sub_2974:
2974  55              push bp
2975  89 E5           mov bp, sp
2977  83 EC 02        sub sp, 2
297A  C4 7E 06        les di, ptr [bp + 6]
297D  26 80 7D 06 0C  cmp byte ptr es:[di + 6], 0xc
2982  72 04           jb 0x2988
2984  B0 00           mov al, 0
2986  EB 02           jmp 0x298a
loc_2988:
2988  B0 01           mov al, 1
loc_298A:
298A  88 46 FF        mov byte ptr [bp - 1], al
298D  8A 46 FF        mov al, byte ptr [bp - 1]
2990  89 EC           mov sp, bp
2992  5D              pop bp
2993  CA 04 00        retf 4

; ---- routine 0791:2996  (found by: call)
sub_2996:
2996  55              push bp
2997  89 E5           mov bp, sp
2999  83 EC 02        sub sp, 2
299C  80 3E 0B 83 0C  cmp byte ptr [0x830b], 0xc
29A1  72 04           jb 0x29a7
29A3  B0 00           mov al, 0
29A5  EB 02           jmp 0x29a9
loc_29A7:
29A7  B0 01           mov al, 1
loc_29A9:
29A9  88 46 FF        mov byte ptr [bp - 1], al
29AC  8A 46 FF        mov al, byte ptr [bp - 1]
29AF  89 EC           mov sp, bp
29B1  5D              pop bp
29B2  C3              ret

; ---- routine 0791:29B3  (found by: call)
sub_29B3:
29B3  55              push bp
29B4  89 E5           mov bp, sp
29B6  83 EC 02        sub sp, 2
29B9  E8 DA FF        call 0x2996
29BC  08 C0           or al, al
29BE  74 04           je 0x29c4
29C0  B0 00           mov al, 0
29C2  EB 02           jmp 0x29c6
loc_29C4:
29C4  B0 01           mov al, 1
loc_29C6:
29C6  98              cwde
29C7  8B F8           mov di, ax
29C9  8A 85 68 06     mov al, byte ptr [di + 0x668]
29CD  30 E4           xor ah, ah
29CF  40              inc ax
29D0  BA 16 00        mov dx, 0x16
29D3  F7 E2           mul dx
29D5  8B F8           mov di, ax
29D7  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
29DB  98              cwde
29DC  09 C0           or ax, ax
29DE  79 02           jns 0x29e2
29E0  F7 D8           neg ax
loc_29E2:
29E2  8B C8           mov cx, ax
29E4  A0 0B 83        mov al, byte ptr [0x830b]
29E7  30 E4           xor ah, ah
29E9  BA 16 00        mov dx, 0x16
29EC  F7 E2           mul dx
29EE  8B F8           mov di, ax
29F0  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
29F4  98              cwde
29F5  09 C0           or ax, ax
29F7  79 02           jns 0x29fb
29F9  F7 D8           neg ax
loc_29FB:
29FB  3B C1           cmp ax, cx
29FD  7D 04           jge 0x2a03
29FF  B0 00           mov al, 0
2A01  EB 02           jmp 0x2a05
loc_2A03:
2A03  B0 01           mov al, 1
loc_2A05:
2A05  A2 FB 80        mov byte ptr [0x80fb], al
2A08  A0 FB 80        mov al, byte ptr [0x80fb]
2A0B  88 46 FF        mov byte ptr [bp - 1], al
2A0E  8A 46 FF        mov al, byte ptr [bp - 1]
2A11  89 EC           mov sp, bp
2A13  5D              pop bp
2A14  C3              ret

