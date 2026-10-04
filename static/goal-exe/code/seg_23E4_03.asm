; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 23E4 (image offsets 23E40..2580F), part 3 of 3
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 23E4:143B  (found by: call)
sub_143B:
143B  B0 01           mov al, 1
143D  8B DC           mov bx, sp
143F  36 C4 7F 04     les di, ptr ss:[bx + 4]
1443  26 81 7D 02 B1 D7 cmp word ptr es:[di + 2], 0xd7b1
1449  74 18           je 0x1463
144B  26 81 7D 02 B2 D7 cmp word ptr es:[di + 2], 0xd7b2
1451  74 08           je 0x145b
1453  C7 06 60 7B 67 00 mov word ptr [0x7b60], 0x67
1459  EB 18           jmp 0x1473
loc_145B:
145B  50              push ax
145C  BB 14 00        mov bx, 0x14
145F  E8 14 00        call 0x1476
1462  58              pop ax
loc_1463:
1463  0A C0           or al, al
1465  74 0C           je 0x1473
1467  BB 1C 00        mov bx, 0x1c
146A  E8 09 00        call 0x1476
146D  26 C7 45 02 B0 D7 mov word ptr es:[di + 2], 0xd7b0
loc_1473:
1473  CA 04 00        retf 4

; ---- routine 23E4:1476  (found by: call)
sub_1476:
1476  06              push es
1477  57              push di
1478  06              push es
1479  57              push di
147A  26 FF 19        lcall es:[bx + di]
147D  0B C0           or ax, ax
147F  74 03           je 0x1484
1481  A3 60 7B        mov word ptr [0x7b60], ax
loc_1484:
1484  5F              pop di
1485  07              pop es
1486  C3              ret
; data (not reached as code), 362 bytes
1487                  db 8B DC 1E 36 C5 7F 04 33 C9 89 0D B8 00 3D 81 7D   ; ...6...3.....=.}
1497                  db 02 B1 D7 74 0D B0 02 FF 05 81 7D 02 B3 D7 74 02   ; ...t......}...t.
14A7                  db B4 3C 80 7D 30 00 74 09 8D 55 30 CD 21 72 4F 89   ; .<.}0.t..U0.!rO.
14B7                  db 05 B8 63 15 33 C9 8B D9 81 7D 02 B1 D7 74 29 8B   ; ..c.3....}...t).
14C7                  db 1D B8 00 44 CD 21 B8 B8 15 8B C8 8C CB F6 C2 80   ; ...D.!..........
14D7                  db 75 11 81 7D 02 B3 D7 75 03 E8 26 00 B8 93 15 33   ; u..}...u..&....3
14E7                  db C9 8B D9 C7 45 02 B2 D7 89 45 14 8C 4D 16 89 4D   ; ....E....E..M..M
14F7                  db 18 89 5D 1A C7 45 1C D8 15 8C 4D 1E 33 C0 1F CA   ; ..]..E....M.3...
1507                  db 04 00 33 D2 33 C9 8B 1D B8 02 42 CD 21 2D 80 00   ; ..3.3.....B.!-..
1517                  db 83 DA 00 73 04 33 C0 33 D2 8B CA 8B D0 8B 1D B8   ; ...s.3.3........
1527                  db 00 42 CD 21 8D 95 80 00 B9 80 00 8B 1D B4 3F CD   ; .B.!..........?.
1537                  db 21 73 02 33 C0 33 DB 3B D8 74 20 80 B9 80 00 1A   ; !s.3.3.;.t .....
1547                  db 74 03 43 EB F2 8B D3 2B D0 B9 FF FF 8B 1D B8 02   ; t.C....+........
1557                  db 42 CD 21 33 C9 8B 1D B4 40 CD 21 C3 8B DC 1E 36   ; B.!3....@.!....6
1567                  db C4 7F 04 26 C5 55 0C 26 8B 4D 04 26 8B 1D B4 3F   ; ...&.U.&.M.&...?
1577                  db CD 21 72 10 26 89 45 0A 33 C0 26 C7 45 08 00 00   ; .!r.&.E.3.&.E...
1587                  db 1F CA 04 00 26 C7 45 0A 00 00 EB EE 8B DC 1E 36   ; ....&.E........6
1597                  db C4 7F 04 26 C5 55 0C 33 C9 26 87 4D 08 26 8B 1D   ; ...&.U.3.&.M.&..
15A7                  db B4 40 CD 21 72 07 2B C1 74 03 B8 65 00 1F CA 04   ; .@.!r.+.t..e....
15B7                  db 00 8B DC 1E 36 C4 7F 04 26 C5 55 0C 33 C9 26 87   ; ....6...&.U.3.&.
15C7                  db 4D 08 26 8B 1D B4 40 CD 21 72 02 33 C0 1F CA 04   ; M.&...@.!r.3....
15D7                  db 00 8B DC 36 C4 7F 04 26 8B 1D 83 FB 04 76 06 B4   ; ...6...&.....v..
15E7                  db 3E CD 21 72 02 33 C0 CA 04 00   ; >.!r.3....

; ---- routine 23E4:15F1  (found by: call)
sub_15F1:
15F1  83 3E 60 7B 00  cmp word ptr [0x7b60], 0
15F6  75 08           jne 0x1600
15F8  26 81 7D 02 B1 D7 cmp word ptr es:[di + 2], 0xd7b1
15FE  75 0D           jne 0x160d
loc_1600:
1600  26 8B 5D 08     mov bx, word ptr es:[di + 8]
1604  26 8B 55 0A     mov dx, word ptr es:[di + 0xa]
1608  26 C4 7D 0C     les di, ptr es:[di + 0xc]
160C  C3              ret
loc_160D:
160D  C7 06 60 7B 68 00 mov word ptr [0x7b60], 0x68
1613  EB EB           jmp 0x1600

; ---- routine 23E4:1615  (found by: call)
sub_1615:
1615  3B DA           cmp bx, dx
1617  74 05           je 0x161e
loc_1619:
1619  26 8A 01        mov al, byte ptr es:[bx + di]
161C  F8              clc
161D  C3              ret
loc_161E:
161E  8B FC           mov di, sp
1620  36 C4 7D 02     les di, ptr ss:[di + 2]
1624  E8 3D 00        call 0x1664
1627  8B D0           mov dx, ax
1629  3B DA           cmp bx, dx
162B  75 EC           jne 0x1619
162D  B0 1A           mov al, 0x1a
162F  F9              stc
1630  C3              ret

; ---- routine 23E4:1631  (found by: call)
sub_1631:
1631  83 3E 60 7B 00  cmp word ptr [0x7b60], 0
1636  75 08           jne 0x1640
1638  26 81 7D 02 B2 D7 cmp word ptr es:[di + 2], 0xd7b2
163E  75 0D           jne 0x164d
loc_1640:
1640  26 8B 5D 08     mov bx, word ptr es:[di + 8]
1644  26 8B 55 04     mov dx, word ptr es:[di + 4]
1648  26 C4 7D 0C     les di, ptr es:[di + 0xc]
164C  C3              ret
loc_164D:
164D  C7 06 60 7B 69 00 mov word ptr [0x7b60], 0x69
1653  EB EB           jmp 0x1640

; ---- routine 23E4:1655  (found by: call)
sub_1655:
1655  26 88 01        mov byte ptr es:[bx + di], al
1658  43              inc bx
1659  3B DA           cmp bx, dx
165B  74 01           je 0x165e
165D  C3              ret
loc_165E:
165E  8B FC           mov di, sp
1660  36 C4 7D 02     les di, ptr ss:[di + 2]

; ---- routine 23E4:1664  (found by: call)
sub_1664:
1664  51              push cx
1665  56              push si
1666  1E              push ds
1667  BA 81 25        mov dx, 0x2581   ; relocated segment word 2581
166A  8E DA           mov ds, dx
166C  26 89 5D 08     mov word ptr es:[di + 8], bx
1670  06              push es
1671  57              push di
1672  06              push es
1673  57              push di
1674  26 FF 5D 14     lcall es:[di + 0x14]
1678  0B C0           or ax, ax
167A  74 03           je 0x167f
167C  A3 60 7B        mov word ptr [0x7b60], ax
loc_167F:
167F  5F              pop di
1680  07              pop es
1681  26 8B 45 0A     mov ax, word ptr es:[di + 0xa]
1685  26 8B 5D 08     mov bx, word ptr es:[di + 8]
1689  26 8B 55 04     mov dx, word ptr es:[di + 4]
168D  26 C4 7D 0C     les di, ptr es:[di + 0xc]
1691  1F              pop ds
1692  5E              pop si
1693  59              pop cx
1694  C3              ret
; data (not reached as code), 41 bytes
1695                  db 8B DC 36 C4 7F 04 06 57 E8 51 FF 75 14 E8 70 FF   ; ..6....W.Q.u..p.
16A5                  db 3C 1A 74 0D 43 3C 0D 75 F4 E8 64 FF 3C 0A 75 01   ; <.t.C<.u..d.<.u.
16B5                  db 43 5F 07 26 89 5D 08 EB 25   ; C_.&.]..%

; ---- routine 23E4:16BE  (found by: far)
sub_16BE:
16BE  8B DC           mov bx, sp
16C0  36 C4 7F 04     les di, ptr ss:[bx + 4]
16C4  06              push es
16C5  57              push di
16C6  E8 68 FF        call 0x1631
16C9  75 0A           jne 0x16d5
16CB  B0 0D           mov al, 0xd
16CD  E8 85 FF        call 0x1655
16D0  B0 0A           mov al, 0xa
16D2  E8 80 FF        call 0x1655
loc_16D5:
16D5  5F              pop di
16D6  07              pop es
16D7  26 89 5D 08     mov word ptr es:[di + 8], bx
16DB  EB 06           jmp 0x16e3
; data (not reached as code), 6 bytes
16DD                  db 8B DC 36 C4 7F 04   ; ..6...
loc_16E3:
16E3  26 83 7D 1A 00  cmp word ptr es:[di + 0x1a], 0
16E8  75 03           jne 0x16ed
loc_16EA:
16EA  CA 04 00        retf 4
loc_16ED:
16ED  83 3E 60 7B 00  cmp word ptr [0x7b60], 0
16F2  75 F6           jne 0x16ea
16F4  06              push es
16F5  57              push di
16F6  26 FF 5D 18     lcall es:[di + 0x18]
16FA  0B C0           or ax, ax
16FC  74 EC           je 0x16ea
16FE  A3 60 7B        mov word ptr [0x7b60], ax
1701  EB E7           jmp 0x16ea

; ---- routine 23E4:1703  (found by: prologue)
sub_1703:
1703  55              push bp
1704  8B EC           mov bp, sp
1706  1E              push ds
1707  C4 7E 0C        les di, ptr [bp + 0xc]
170A  06              push es
170B  57              push di
170C  E8 E2 FE        call 0x15f1
170F  C5 76 08        lds si, ptr [bp + 8]
1712  B9 00 00        mov cx, 0
1715  75 15           jne 0x172c
loc_1717:
1717  E8 FB FE        call 0x1615
171A  3C 0D           cmp al, 0xd
171C  74 0E           je 0x172c
171E  3C 1A           cmp al, 0x1a
1720  74 0A           je 0x172c
1722  43              inc bx
1723  41              inc cx
1724  46              inc si
1725  88 04           mov byte ptr [si], al
1727  3B 4E 06        cmp cx, word ptr [bp + 6]
172A  75 EB           jne 0x1717
loc_172C:
172C  2B F1           sub si, cx
172E  88 0C           mov byte ptr [si], cl
1730  5F              pop di
1731  07              pop es
1732  26 89 5D 08     mov word ptr es:[di + 8], bx
1736  1F              pop ds
1737  5D              pop bp
1738  CA 06 00        retf 6

; ---- routine 23E4:173B  (found by: far)
sub_173B:
173B  55              push bp
173C  8B EC           mov bp, sp
173E  1E              push ds
173F  C4 7E 0C        les di, ptr [bp + 0xc]
1742  06              push es
1743  57              push di
1744  E8 EA FE        call 0x1631
1747  75 25           jne 0x176e
1749  C5 76 08        lds si, ptr [bp + 8]
174C  8B 4E 06        mov cx, word ptr [bp + 6]
174F  FC              cld
1750  AC              lodsb al, byte ptr [si]
1751  32 E4           xor ah, ah
1753  2B C8           sub cx, ax
1755  7E 0C           jle 0x1763
1757  B0 20           mov al, 0x20
1759  E8 F9 FE        call 0x1655
175C  E2 F9           loop 0x1757
175E  8A 44 FF        mov al, byte ptr [si - 1]
1761  32 E4           xor ah, ah
loc_1763:
1763  8B C8           mov cx, ax
1765  E3 07           jcxz 0x176e
1767  FC              cld
1768  AC              lodsb al, byte ptr [si]
1769  E8 E9 FE        call 0x1655
176C  E2 F9           loop 0x1767
loc_176E:
176E  5F              pop di
176F  07              pop es
1770  26 89 5D 08     mov word ptr es:[di + 8], bx
1774  1F              pop ds
1775  5D              pop bp
1776  CA 06 00        retf 6

; ---- routine 23E4:1779  (found by: far)
sub_1779:
1779  8B DC           mov bx, sp
177B  1E              push ds
177C  36 C4 7F 08     les di, ptr ss:[bx + 8]
1780  36 C5 77 04     lds si, ptr ss:[bx + 4]
1784  FC              cld
1785  33 C0           xor ax, ax
1787  AB              stosw word ptr es:[di], ax
1788  B8 B0 D7        mov ax, 0xd7b0
178B  AB              stosw word ptr es:[di], ax
178C  33 C0           xor ax, ax
178E  B9 16 00        mov cx, 0x16
1791  F3 AB           rep stosw word ptr es:[di], ax
1793  AC              lodsb al, byte ptr [si]
1794  3C 4F           cmp al, 0x4f
1796  76 02           jbe 0x179a
1798  B0 4F           mov al, 0x4f
loc_179A:
179A  8A C8           mov cl, al
179C  32 ED           xor ch, ch
179E  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
17A0  32 C0           xor al, al
17A2  AA              stosb byte ptr es:[di], al
17A3  1F              pop ds
17A4  CA 08 00        retf 8
; data (not reached as code), 9 bytes
17A7                  db A0 66 7B B4 3D 33 D2 EB 06   ; .f{.=3...

; ---- routine 23E4:17B0  (found by: far)
sub_17B0:
17B0  B8 00 3C        mov ax, 0x3c00
17B3  BA 01 00        mov dx, 1
17B6  55              push bp
17B7  8B EC           mov bp, sp
17B9  C4 7E 08        les di, ptr [bp + 8]
17BC  26 81 7D 02 B0 D7 cmp word ptr es:[di + 2], 0xd7b0
17C2  74 1A           je 0x17de
17C4  26 81 7D 02 B3 D7 cmp word ptr es:[di + 2], 0xd7b3
17CA  74 08           je 0x17d4
17CC  C7 06 60 7B 66 00 mov word ptr [0x7b60], 0x66
17D2  EB 34           jmp 0x1808
loc_17D4:
17D4  50              push ax
17D5  52              push dx
17D6  06              push es
17D7  57              push di
17D8  0E              push cs
17D9  E8 4C 00        call 0x1828
17DC  5A              pop dx
17DD  58              pop ax
loc_17DE:
17DE  26 80 7D 30 00  cmp byte ptr es:[di + 0x30], 0
17E3  74 12           je 0x17f7
17E5  1E              push ds
17E6  8D 55 30        lea dx, [di + 0x30]
17E9  06              push es
17EA  1F              pop ds
17EB  33 C9           xor cx, cx
17ED  CD 21           int 0x21   ; INT 21h, AH not set by a nearby mov
17EF  1F              pop ds
17F0  73 06           jae 0x17f8
17F2  A3 60 7B        mov word ptr [0x7b60], ax
17F5  EB 11           jmp 0x1808
loc_17F7:
17F7  92              xchg dx, ax
loc_17F8:
17F8  26 C7 45 02 B3 D7 mov word ptr es:[di + 2], 0xd7b3
17FE  26 89 05        mov word ptr es:[di], ax
1801  8B 46 06        mov ax, word ptr [bp + 6]
1804  26 89 45 04     mov word ptr es:[di + 4], ax
loc_1808:
1808  5D              pop bp
1809  CA 06 00        retf 6
; data (not reached as code), 28 bytes
180C                  db 8B DC 36 C4 7F 04 E8 38 00 75 0E 33 C9 26 8B 1D   ; ..6....8.u.3.&..
181C                  db B4 40 CD 21 73 03 A3 60 7B CA 04 00   ; .@.!s..`{...

; ---- routine 23E4:1828  (found by: call, far)
sub_1828:
1828  8B DC           mov bx, sp
182A  36 C4 7F 04     les di, ptr ss:[bx + 4]
182E  E8 1C 00        call 0x184d
1831  75 17           jne 0x184a
1833  26 8B 1D        mov bx, word ptr es:[di]
1836  83 FB 04        cmp bx, 4
1839  76 09           jbe 0x1844
183B  B4 3E           mov ah, 0x3e
183D  CD 21           int 0x21   ; INT 21h AH=3E close file
183F  73 03           jae 0x1844
1841  A3 60 7B        mov word ptr [0x7b60], ax
loc_1844:
1844  26 C7 45 02 B0 D7 mov word ptr es:[di + 2], 0xd7b0
loc_184A:
184A  CA 04 00        retf 4

; ---- routine 23E4:184D  (found by: call)
sub_184D:
184D  26 81 7D 02 B3 D7 cmp word ptr es:[di + 2], 0xd7b3
1853  74 06           je 0x185b
1855  C7 06 60 7B 67 00 mov word ptr [0x7b60], 0x67
loc_185B:
185B  C3              ret
; data (not reached as code), 12 bytes
185C                  db B4 3F BA 64 00 EB 05 B4 40 BA 65 00   ; .?.d....@.e.

; ---- routine 23E4:1868  (found by: prologue)
sub_1868:
1868  55              push bp
1869  8B EC           mov bp, sp
186B  C4 7E 0A        les di, ptr [bp + 0xa]
186E  E8 DC FF        call 0x184d
1871  75 1B           jne 0x188e
1873  1E              push ds
1874  52              push dx
1875  C5 56 06        lds dx, ptr [bp + 6]
1878  26 8B 4D 04     mov cx, word ptr es:[di + 4]
187C  26 8B 1D        mov bx, word ptr es:[di]
187F  CD 21           int 0x21   ; INT 21h, AH not set by a nearby mov
1881  5A              pop dx
1882  1F              pop ds
1883  72 06           jb 0x188b
1885  3B C1           cmp ax, cx
1887  74 05           je 0x188e
1889  8B C2           mov ax, dx
loc_188B:
188B  A3 60 7B        mov word ptr [0x7b60], ax
loc_188E:
188E  5D              pop bp
188F  CA 04 00        retf 4
; data (not reached as code), 7 bytes
1892                  db B3 3F B9 64 00 EB 05   ; .?.d...

; ---- routine 23E4:1899  (found by: far)
sub_1899:
1899  B3 40           mov bl, 0x40
189B  B9 65 00        mov cx, 0x65
189E  55              push bp
189F  8B EC           mov bp, sp
18A1  C4 7E 10        les di, ptr [bp + 0x10]
18A4  E8 A6 FF        call 0x184d
18A7  75 3F           jne 0x18e8
18A9  8B 46 0A        mov ax, word ptr [bp + 0xa]
18AC  0B C0           or ax, ax
18AE  74 1C           je 0x18cc
18B0  1E              push ds
18B1  51              push cx
18B2  26 F7 65 04     mul word ptr es:[di + 4]
18B6  8B C8           mov cx, ax
18B8  C5 56 0C        lds dx, ptr [bp + 0xc]
18BB  8A E3           mov ah, bl
18BD  26 8B 1D        mov bx, word ptr es:[di]
18C0  CD 21           int 0x21   ; INT 21h, AH not set by a nearby mov
18C2  59              pop cx
18C3  1F              pop ds
18C4  72 1F           jb 0x18e5
18C6  33 D2           xor dx, dx
18C8  26 F7 75 04     div word ptr es:[di + 4]
loc_18CC:
18CC  C4 7E 06        les di, ptr [bp + 6]
18CF  8C C2           mov dx, es
18D1  0B D7           or dx, di
18D3  74 05           je 0x18da
18D5  26 89 05        mov word ptr es:[di], ax
18D8  EB 1C           jmp 0x18f6
loc_18DA:
18DA  3B 46 0A        cmp ax, word ptr [bp + 0xa]
18DD  74 17           je 0x18f6
18DF  89 0E 60 7B     mov word ptr [0x7b60], cx
18E3  EB 11           jmp 0x18f6
loc_18E5:
18E5  A3 60 7B        mov word ptr [0x7b60], ax
loc_18E8:
18E8  C4 7E 06        les di, ptr [bp + 6]
18EB  8C C2           mov dx, es
18ED  0B D7           or dx, di
18EF  74 05           je 0x18f6
18F1  33 C0           xor ax, ax
18F3  26 89 05        mov word ptr es:[di], ax
loc_18F6:
18F6  5D              pop bp
18F7  CA 0E 00        retf 0xe

; ---- routine 23E4:18FA  (found by: prologue)
sub_18FA:
18FA  55              push bp
18FB  8B EC           mov bp, sp
18FD  C4 7E 0A        les di, ptr [bp + 0xa]
1900  E8 4A FF        call 0x184d
1903  75 21           jne 0x1926
1905  8B 46 08        mov ax, word ptr [bp + 8]
1908  26 F7 65 04     mul word ptr es:[di + 4]
190C  8B C8           mov cx, ax
190E  8B 46 06        mov ax, word ptr [bp + 6]
1911  26 F7 65 04     mul word ptr es:[di + 4]
1915  03 CA           add cx, dx
1917  8B D0           mov dx, ax
1919  26 8B 1D        mov bx, word ptr es:[di]
191C  B8 00 42        mov ax, 0x4200
191F  CD 21           int 0x21   ; INT 21h AH=42 seek
1921  73 03           jae 0x1926
1923  A3 60 7B        mov word ptr [0x7b60], ax
loc_1926:
1926  5D              pop bp
1927  CA 08 00        retf 8

; ---- routine 23E4:192A  (found by: far)
sub_192A:
192A  55              push bp
192B  8B EC           mov bp, sp
192D  8B 56 06        mov dx, word ptr [bp + 6]
1930  0B D2           or dx, dx
1932  74 05           je 0x1939
1934  E8 49 00        call 0x1980
1937  EB 30           jmp 0x1969
loc_1939:
1939  B4 30           mov ah, 0x30
193B  CD 21           int 0x21   ; INT 21h AH=30 get DOS version
193D  3C 03           cmp al, 3
193F  B8 00 00        mov ax, 0
1942  72 25           jb 0x1969
1944  8E 06 5C 7B     mov es, word ptr [0x7b5c]
1948  26 8E 06 2C 00  mov es, word ptr es:[0x2c]
194D  33 FF           xor di, di
194F  FC              cld
loc_1950:
1950  26 3A 05        cmp al, byte ptr es:[di]
1953  74 07           je 0x195c
1955  B9 FF FF        mov cx, 0xffff
1958  F2 AE           repne scasb al, byte ptr es:[di]
195A  EB F4           jmp 0x1950
loc_195C:
195C  83 C7 03        add di, 3
195F  8B F7           mov si, di
1961  B9 00 01        mov cx, 0x100
1964  F2 AE           repne scasb al, byte ptr es:[di]
1966  91              xchg cx, ax
1967  F6 D0           not al
loc_1969:
1969  1E              push ds
196A  06              push es
196B  1F              pop ds
196C  C4 7E 08        les di, ptr [bp + 8]
196F  FC              cld
1970  AA              stosb byte ptr es:[di], al
1971  91              xchg cx, ax
1972  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
1974  1F              pop ds
1975  5D              pop bp
1976  CA 02 00        retf 2
; data (not reached as code), 7 bytes
1979                  db 33 D2 E8 02 00 93 CB   ; 3......

; ---- routine 23E4:1980  (found by: call)
sub_1980:
1980  8E 06 5C 7B     mov es, word ptr [0x7b5c]
1984  BF 80 00        mov di, 0x80
1987  26 8A 0D        mov cl, byte ptr es:[di]
198A  32 ED           xor ch, ch
198C  47              inc di
198D  33 DB           xor bx, bx
loc_198F:
198F  E3 09           jcxz 0x199a
1991  26 80 3D 20     cmp byte ptr es:[di], 0x20
1995  77 03           ja 0x199a
1997  47              inc di
1998  E2 F7           loop 0x1991
loc_199A:
199A  8B F7           mov si, di
199C  E3 09           jcxz 0x19a7
199E  26 80 3D 20     cmp byte ptr es:[di], 0x20
19A2  76 03           jbe 0x19a7
19A4  47              inc di
19A5  E2 F7           loop 0x199e
loc_19A7:
19A7  8B C7           mov ax, di
19A9  2B C6           sub ax, si
19AB  74 04           je 0x19b1
19AD  43              inc bx
19AE  4A              dec dx
19AF  75 DE           jne 0x198f
loc_19B1:
19B1  C3              ret

; ---- routine 23E4:19B2  (found by: far)
sub_19B2:
19B2  8B DC           mov bx, sp
19B4  36 8A 47 04     mov al, byte ptr ss:[bx + 4]
19B8  3C 61           cmp al, 0x61
19BA  72 06           jb 0x19c2
19BC  3C 7A           cmp al, 0x7a
19BE  77 02           ja 0x19c2
19C0  2C 20           sub al, 0x20
loc_19C2:
19C2  CA 02 00        retf 2
; data (not reached as code), 11 bytes
19C5                  db 00 00 00 00 00 00 00 00 00 00 00   ; ...........
