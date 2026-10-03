; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 3 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:15B9  (found by: call)
sub_15B9:
15B9  55              push bp
15BA  89 E5           mov bp, sp
15BC  83 EC 08        sub sp, 8
15BF  BF 3E 7C        mov di, 0x7c3e
15C2  1E              push ds
15C3  57              push di
15C4  BF 39 84        mov di, 0x8439
15C7  1E              push ds
15C8  57              push di
15C9  B8 FB 07        mov ax, 0x7fb
15CC  50              push ax
15CD  9A 5D 02 E4 23  call far 23E4:025D
15D2  C6 46 FF 00     mov byte ptr [bp - 1], 0
15D6  EB 03           jmp 0x15db
loc_15D8:
15D8  FE 46 FF        inc byte ptr [bp - 1]
loc_15DB:
15DB  8A 46 FF        mov al, byte ptr [bp - 1]
15DE  98              cwde
15DF  8B F8           mov di, ax
15E1  D1 E7           shl di, 1
15E3  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
15E7  BA BF 00        mov dx, 0xbf
15EA  F7 E2           mul dx
15EC  C4 3E 17 A9     les di, ptr [0xa917]
15F0  03 F8           add di, ax
15F2  89 7E F9        mov word ptr [bp - 7], di
15F5  8C 46 FB        mov word ptr [bp - 5], es
15F8  8A 46 FF        mov al, byte ptr [bp - 1]
15FB  98              cwde
15FC  8B F8           mov di, ax
15FE  D1 E7           shl di, 1
1600  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
1604  BA BF 00        mov dx, 0xbf
1607  F7 E2           mul dx
1609  C4 3E 17 A9     les di, ptr [0xa917]
160D  03 F8           add di, ax
160F  06              push es
1610  57              push di
1611  8A 46 FF        mov al, byte ptr [bp - 1]
1614  98              cwde
1615  BA BF 00        mov dx, 0xbf
1618  F7 E2           mul dx
161A  8B F8           mov di, ax
161C  81 C7 34 8C     add di, 0x8c34
1620  1E              push ds
1621  57              push di
1622  B8 BF 00        mov ax, 0xbf
1625  50              push ax
1626  9A 5D 02 E4 23  call far 23E4:025D
162B  C4 7E F9        les di, ptr [bp - 7]
162E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
1632  30 E4           xor ah, ah
1634  BA 03 00        mov dx, 3
1637  F7 E2           mul dx
1639  C4 3E 1F A9     les di, ptr [0xa91f]
163D  03 F8           add di, ax
163F  06              push es
1640  57              push di
1641  8A 46 FF        mov al, byte ptr [bp - 1]
1644  98              cwde
1645  BA 03 00        mov dx, 3
1648  F7 E2           mul dx
164A  8B F8           mov di, ax
164C  81 C7 30 99     add di, 0x9930
1650  1E              push ds
1651  57              push di
1652  B8 03 00        mov ax, 3
1655  50              push ax
1656  9A 5D 02 E4 23  call far 23E4:025D
165B  C4 7E F9        les di, ptr [bp - 7]
165E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
1662  30 E4           xor ah, ah
1664  BA 0D 00        mov dx, 0xd
1667  F7 E2           mul dx
1669  C4 3E 74 9B     les di, ptr [0x9b74]
166D  03 F8           add di, ax
166F  06              push es
1670  57              push di
1671  8A 46 FF        mov al, byte ptr [bp - 1]
1674  98              cwde
1675  BA 0D 00        mov dx, 0xd
1678  F7 E2           mul dx
167A  8B F8           mov di, ax
167C  81 C7 3C 99     add di, 0x993c
1680  1E              push ds
1681  57              push di
1682  B8 0C 00        mov ax, 0xc
1685  50              push ax
1686  9A 44 06 E4 23  call far 23E4:0644
168B  C4 7E F9        les di, ptr [bp - 7]
168E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
1692  30 E4           xor ah, ah
1694  C4 3E 78 9B     les di, ptr [0x9b78]
1698  03 F8           add di, ax
169A  26 8A 15        mov dl, byte ptr es:[di]
169D  8A 46 FF        mov al, byte ptr [bp - 1]
16A0  98              cwde
16A1  8B F8           mov di, ax
16A3  88 95 70 99     mov byte ptr [di - 0x6690], dl
16A7  C7 46 FD 01 00  mov word ptr [bp - 3], 1
16AC  EB 03           jmp 0x16b1
loc_16AE:
16AE  FF 46 FD        inc word ptr [bp - 3]
loc_16B1:
16B1  8B 46 FD        mov ax, word ptr [bp - 3]
16B4  D1 E0           shl ax, 1
16B6  C4 7E F9        les di, ptr [bp - 7]
16B9  03 F8           add di, ax
16BB  26 8B 45 FE     mov ax, word ptr es:[di - 2]
16BF  BA 14 00        mov dx, 0x14
16C2  F7 E2           mul dx
16C4  C4 3E 1B A9     les di, ptr [0xa91b]
16C8  03 F8           add di, ax
16CA  06              push es
16CB  57              push di
16CC  8B 46 FD        mov ax, word ptr [bp - 3]
16CF  BA 14 00        mov dx, 0x14
16D2  F7 E2           mul dx
16D4  8B C8           mov cx, ax
16D6  8A 46 FF        mov al, byte ptr [bp - 1]
16D9  98              cwde
16DA  BA 90 01        mov dx, 0x190
16DD  F7 E2           mul dx
16DF  8B F8           mov di, ax
16E1  03 F9           add di, cx
16E3  81 C7 1C 8F     add di, 0x8f1c
16E7  1E              push ds
16E8  57              push di
16E9  B8 14 00        mov ax, 0x14
16EC  50              push ax
16ED  9A 5D 02 E4 23  call far 23E4:025D
16F2  8B 46 FD        mov ax, word ptr [bp - 3]
16F5  D1 E0           shl ax, 1
16F7  C4 7E F9        les di, ptr [bp - 7]
16FA  03 F8           add di, ax
16FC  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1700  BA 0B 00        mov dx, 0xb
1703  F7 E2           mul dx
1705  C4 3E 6C 9B     les di, ptr [0x9b6c]
1709  03 F8           add di, ax
170B  06              push es
170C  57              push di
170D  8B 46 FD        mov ax, word ptr [bp - 3]
1710  BA 0B 00        mov dx, 0xb
1713  F7 E2           mul dx
1715  8B C8           mov cx, ax
1717  8A 46 FF        mov al, byte ptr [bp - 1]
171A  98              cwde
171B  BA DC 00        mov dx, 0xdc
171E  F7 E2           mul dx
1720  8B F8           mov di, ax
1722  03 F9           add di, cx
1724  81 C7 65 95     add di, 0x9565
1728  1E              push ds
1729  57              push di
172A  B8 0A 00        mov ax, 0xa
172D  50              push ax
172E  9A 44 06 E4 23  call far 23E4:0644
1733  8B 46 FD        mov ax, word ptr [bp - 3]
1736  D1 E0           shl ax, 1
1738  C4 7E F9        les di, ptr [bp - 7]
173B  03 F8           add di, ax
173D  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1741  C4 3E 70 9B     les di, ptr [0x9b70]
1745  03 F8           add di, ax
1747  26 8A 1D        mov bl, byte ptr es:[di]
174A  8B 46 FD        mov ax, word ptr [bp - 3]
174D  8B C8           mov cx, ax
174F  8A 46 FF        mov al, byte ptr [bp - 1]
1752  98              cwde
1753  BA 14 00        mov dx, 0x14
1756  F7 E2           mul dx
1758  8B F8           mov di, ax
175A  03 F9           add di, cx
175C  88 9D DF 98     mov byte ptr [di - 0x6721], bl
1760  83 7E FD 14     cmp word ptr [bp - 3], 0x14
1764  74 03           je 0x1769
1766  E9 45 FF        jmp 0x16ae
loc_1769:
1769  80 7E FF 01     cmp byte ptr [bp - 1], 1
176D  74 03           je 0x1772
176F  E9 66 FE        jmp 0x15d8
loc_1772:
1772  BF 7E 7B        mov di, 0x7b7e
1775  1E              push ds
1776  57              push di
1777  BF 6A 7B        mov di, 0x7b6a
177A  1E              push ds
177B  57              push di
177C  B8 14 00        mov ax, 0x14
177F  50              push ax
1780  9A 5D 02 E4 23  call far 23E4:025D
1785  BF D4 7B        mov di, 0x7bd4
1788  1E              push ds
1789  57              push di
178A  BF 92 7B        mov di, 0x7b92
178D  1E              push ds
178E  57              push di
178F  B8 42 00        mov ax, 0x42
1792  50              push ax
1793  9A 5D 02 E4 23  call far 23E4:025D
1798  C4 3E 2A 7C     les di, ptr [0x7c2a]
179C  06              push es
179D  57              push di
179E  BF 2E 7C        mov di, 0x7c2e
17A1  1E              push ds
17A2  57              push di
17A3  B8 08 00        mov ax, 8
17A6  50              push ax
17A7  9A 5D 02 E4 23  call far 23E4:025D
17AC  A0 3D 9A        mov al, byte ptr [0x9a3d]
17AF  A2 3C 9A        mov byte ptr [0x9a3c], al
17B2  BF 40 9A        mov di, 0x9a40
17B5  1E              push ds
17B6  57              push di
17B7  BF 90 9A        mov di, 0x9a90
17BA  1E              push ds
17BB  57              push di
17BC  B8 50 00        mov ax, 0x50
17BF  50              push ax
17C0  9A 5D 02 E4 23  call far 23E4:025D
17C5  BF 08 9B        mov di, 0x9b08
17C8  1E              push ds
17C9  57              push di
17CA  BF E0 9A        mov di, 0x9ae0
17CD  1E              push ds
17CE  57              push di
17CF  B8 28 00        mov ax, 0x28
17D2  50              push ax
17D3  9A 5D 02 E4 23  call far 23E4:025D
17D8  C4 06 34 9B     les ax, ptr [0x9b34]
17DC  8C C2           mov dx, es
17DE  A3 30 9B        mov word ptr [0x9b30], ax
17E1  89 16 32 9B     mov word ptr [0x9b32], dx
17E5  A1 3A 9B        mov ax, word ptr [0x9b3a]
17E8  A3 38 9B        mov word ptr [0x9b38], ax
17EB  A1 3C 9B        mov ax, word ptr [0x9b3c]
17EE  A3 3E 9B        mov word ptr [0x9b3e], ax
17F1  A0 41 9B        mov al, byte ptr [0x9b41]
17F4  A2 42 9B        mov byte ptr [0x9b42], al
17F7  C4 3E 78 A9     les di, ptr [0xa978]
17FB  26 8B 05        mov ax, word ptr es:[di]
17FE  A3 74 99        mov word ptr [0x9974], ax
1801  BF 78 99        mov di, 0x9978
1804  1E              push ds
1805  57              push di
1806  BF 8C 99        mov di, 0x998c
1809  1E              push ds
180A  57              push di
180B  B8 14 00        mov ax, 0x14
180E  50              push ax
180F  9A 5D 02 E4 23  call far 23E4:025D
1814  BF 20 61        mov di, 0x6120
1817  1E              push ds
1818  57              push di
1819  BF 6A A9        mov di, 0xa96a
181C  1E              push ds
181D  57              push di
181E  9A 29 03 4B 21  call far 214B:0329
1823  89 EC           mov sp, bp
1825  5D              pop bp
1826  C3              ret
; data (not reached as code), 2 bytes
1827                  db 01 20   ; . 

; ---- routine 0791:1829  (found by: call)
sub_1829:
1829  55              push bp
182A  89 E5           mov bp, sp
182C  81 EC 28 01     sub sp, 0x128
1830  8B 7E 08        mov di, word ptr [bp + 8]
1833  D1 E7           shl di, 1
1835  8B F7           mov si, di
1837  D1 E7           shl di, 1
1839  03 FE           add di, si
183B  81 C7 38 7C     add di, 0x7c38
183F  89 7E D8        mov word ptr [bp - 0x28], di
1842  8C 5E DA        mov word ptr [bp - 0x26], ds
1845  C4 7E D8        les di, ptr [bp - 0x28]
1848  26 80 3D FF     cmp byte ptr es:[di], 0xff
184C  75 03           jne 0x1851
184E  E9 8D 01        jmp 0x19de
loc_1851:
1851  C4 7E D8        les di, ptr [bp - 0x28]
1854  26 8A 05        mov al, byte ptr es:[di]
1857  98              cwde
1858  BA 15 00        mov dx, 0x15
185B  F7 E2           mul dx
185D  8B F8           mov di, ax
185F  81 C7 BE 00     add di, 0xbe
1863  1E              push ds
1864  57              push di
1865  8D 7E DC        lea di, [bp - 0x24]
1868  16              push ss
1869  57              push di
186A  B8 23 00        mov ax, 0x23
186D  50              push ax
186E  9A 44 06 E4 23  call far 23E4:0644
1873  80 7E DC 00     cmp byte ptr [bp - 0x24], 0
1877  75 03           jne 0x187c
1879  E9 E3 00        jmp 0x195f
loc_187C:
187C  80 7E DD 01     cmp byte ptr [bp - 0x23], 1
1880  75 3B           jne 0x18bd
1882  C6 46 DD 20     mov byte ptr [bp - 0x23], 0x20
1886  8D BE D8 FE     lea di, [bp - 0x128]
188A  16              push ss
188B  57              push di
188C  C4 7E D8        les di, ptr [bp - 0x28]
188F  26 8B 45 01     mov ax, word ptr es:[di + 1]
1893  BA 0B 00        mov dx, 0xb
1896  F7 E2           mul dx
1898  C4 3E 6C 9B     les di, ptr [0x9b6c]
189C  03 F8           add di, ax
189E  06              push es
189F  57              push di
18A0  9A 2A 06 E4 23  call far 23E4:062A
18A5  8D 7E DC        lea di, [bp - 0x24]
18A8  16              push ss
18A9  57              push di
18AA  9A B7 06 E4 23  call far 23E4:06B7
18AF  8D 7E DC        lea di, [bp - 0x24]
18B2  16              push ss
18B3  57              push di
18B4  B8 23 00        mov ax, 0x23
18B7  50              push ax
18B8  9A 44 06 E4 23  call far 23E4:0644
loc_18BD:
18BD  8A 46 DC        mov al, byte ptr [bp - 0x24]
18C0  30 E4           xor ah, ah
18C2  8B F8           mov di, ax
18C4  80 7B DC 01     cmp byte ptr [bp + di - 0x24], 1
18C8  75 44           jne 0x190e
18CA  FE 4E DC        dec byte ptr [bp - 0x24]
18CD  8D BE D8 FE     lea di, [bp - 0x128]
18D1  16              push ss
18D2  57              push di
18D3  8D 7E DC        lea di, [bp - 0x24]
18D6  16              push ss
18D7  57              push di
18D8  9A 2A 06 E4 23  call far 23E4:062A
18DD  BF 27 18        mov di, 0x1827
18E0  0E              push cs
18E1  57              push di
18E2  9A B7 06 E4 23  call far 23E4:06B7
18E7  C4 7E D8        les di, ptr [bp - 0x28]
18EA  26 8B 45 01     mov ax, word ptr es:[di + 1]
18EE  BA 0B 00        mov dx, 0xb
18F1  F7 E2           mul dx
18F3  C4 3E 6C 9B     les di, ptr [0x9b6c]
18F7  03 F8           add di, ax
18F9  06              push es
18FA  57              push di
18FB  9A B7 06 E4 23  call far 23E4:06B7
1900  8D 7E DC        lea di, [bp - 0x24]
1903  16              push ss
1904  57              push di
1905  B8 23 00        mov ax, 0x23
1908  50              push ax
1909  9A 44 06 E4 23  call far 23E4:0644
loc_190E:
190E  8A 46 DC        mov al, byte ptr [bp - 0x24]
1911  30 E4           xor ah, ah
1913  8B F8           mov di, ax
1915  80 7B DC 02     cmp byte ptr [bp + di - 0x24], 2
1919  75 44           jne 0x195f
191B  FE 4E DC        dec byte ptr [bp - 0x24]
191E  8D BE D8 FE     lea di, [bp - 0x128]
1922  16              push ss
1923  57              push di
1924  8D 7E DC        lea di, [bp - 0x24]
1927  16              push ss
1928  57              push di
1929  9A 2A 06 E4 23  call far 23E4:062A
192E  BF 27 18        mov di, 0x1827
1931  0E              push cs
1932  57              push di
1933  9A B7 06 E4 23  call far 23E4:06B7
1938  C4 7E D8        les di, ptr [bp - 0x28]
193B  26 8B 45 03     mov ax, word ptr es:[di + 3]
193F  BA 0B 00        mov dx, 0xb
1942  F7 E2           mul dx
1944  C4 3E 6C 9B     les di, ptr [0x9b6c]
1948  03 F8           add di, ax
194A  06              push es
194B  57              push di
194C  9A B7 06 E4 23  call far 23E4:06B7
1951  8D 7E DC        lea di, [bp - 0x24]
1954  16              push ss
1955  57              push di
1956  B8 23 00        mov ax, 0x23
1959  50              push ax
195A  9A 44 06 E4 23  call far 23E4:0644
loc_195F:
195F  80 7E DC 1E     cmp byte ptr [bp - 0x24], 0x1e
1963  73 23           jae 0x1988
1965  8A 46 DC        mov al, byte ptr [bp - 0x24]
1968  30 E4           xor ah, ah
196A  40              inc ax
196B  8B F8           mov di, ax
196D  8D 7B DC        lea di, [bp + di - 0x24]
1970  16              push ss
1971  57              push di
1972  8A 46 DC        mov al, byte ptr [bp - 0x24]
1975  30 E4           xor ah, ah
1977  8B D0           mov dx, ax
1979  B8 1E 00        mov ax, 0x1e
197C  2B C2           sub ax, dx
197E  50              push ax
197F  B8 20 00        mov ax, 0x20
1982  50              push ax
1983  9A 18 00 4B 21  call far 214B:0018
loc_1988:
1988  C6 46 DC 1E     mov byte ptr [bp - 0x24], 0x1e
198C  C4 7E D8        les di, ptr [bp - 0x28]
198F  26 8A 45 05     mov al, byte ptr es:[di + 5]
1993  98              cwde
1994  8B F8           mov di, ax
1996  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
199A  50              push ax
199B  8D 7E DC        lea di, [bp - 0x24]
199E  16              push ss
199F  57              push di
19A0  8A 46 06        mov al, byte ptr [bp + 6]
19A3  50              push ax
19A4  8A 46 04        mov al, byte ptr [bp + 4]
19A7  50              push ax
19A8  BF 6A A9        mov di, 0xa96a
19AB  1E              push ds
19AC  57              push di
19AD  9A C8 02 4B 21  call far 214B:02C8
19B2  83 7E 06 04     cmp word ptr [bp + 6], 4
19B6  77 26           ja 0x19de
19B8  C4 7E D8        les di, ptr [bp - 0x28]
19BB  26 8A 45 05     mov al, byte ptr es:[di + 5]
19BF  98              cwde
19C0  8B F8           mov di, ax
19C2  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
19C6  50              push ax
19C7  8D 7E DC        lea di, [bp - 0x24]
19CA  16              push ss
19CB  57              push di
19CC  8A 46 06        mov al, byte ptr [bp + 6]
19CF  50              push ax
19D0  8A 46 04        mov al, byte ptr [bp + 4]
19D3  50              push ax
19D4  BF 72 A9        mov di, 0xa972
19D7  1E              push ds
19D8  57              push di
19D9  9A C8 02 4B 21  call far 214B:02C8
loc_19DE:
19DE  89 EC           mov sp, bp
19E0  5D              pop bp
19E1  C2 06 00        ret 6
; data (not reached as code), 32 bytes
19E4                  db 00 20 00 08 00 00 00 00 00 00 00 00 00 00 00 00   ; . ..............
19F4                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:1A04  (found by: call)
sub_1A04:
1A04  55              push bp
1A05  89 E5           mov bp, sp
1A07  83 EC 0E        sub sp, 0xe
1A0A  83 3E EE 80 00  cmp word ptr [0x80ee], 0
1A0F  75 03           jne 0x1a14
1A11  E9 60 02        jmp 0x1c74
loc_1A14:
1A14  C4 3E 16 7C     les di, ptr [0x7c16]
1A18  06              push es
1A19  57              push di
1A1A  C4 3E 22 7C     les di, ptr [0x7c22]
1A1E  06              push es
1A1F  57              push di
1A20  B8 A0 0F        mov ax, 0xfa0
1A23  50              push ax
1A24  9A 5D 02 E4 23  call far 23E4:025D
1A29  B8 8E 2E        mov ax, 0x2e8e
1A2C  8C DA           mov dx, ds
1A2E  89 46 F6        mov word ptr [bp - 0xa], ax
1A31  89 56 F8        mov word ptr [bp - 8], dx
1A34  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
1A39  7C 04           jl 0x1a3f
1A3B  B0 00           mov al, 0
1A3D  EB 02           jmp 0x1a41
loc_1A3F:
1A3F  B0 01           mov al, 1
loc_1A41:
1A41  98              cwde
1A42  8B F8           mov di, ax
1A44  D1 E7           shl di, 1
1A46  8B 85 1C 07     mov ax, word ptr [di + 0x71c]
1A4A  C4 7E F6        les di, ptr [bp - 0xa]
1A4D  26 89 05        mov word ptr es:[di], ax
1A50  A1 EE 80        mov ax, word ptr [0x80ee]
1A53  89 46 FE        mov word ptr [bp - 2], ax
1A56  BF 8E 2E        mov di, 0x2e8e
1A59  1E              push ds
1A5A  57              push di
1A5B  BF 6A A9        mov di, 0xa96a
1A5E  1E              push ds
1A5F  57              push di
1A60  9A 29 03 4B 21  call far 214B:0329
1A65  BF 9A 3B        mov di, 0x3b9a
1A68  1E              push ds
1A69  57              push di
1A6A  BF 6A A9        mov di, 0xa96a
1A6D  1E              push ds
1A6E  57              push di
1A6F  9A 29 03 4B 21  call far 214B:0329
loc_1A74:
1A74  8B 46 FE        mov ax, word ptr [bp - 2]
1A77  89 46 FC        mov word ptr [bp - 4], ax
1A7A  C7 46 FA 11 00  mov word ptr [bp - 6], 0x11
1A7F  EB 03           jmp 0x1a84
loc_1A81:
1A81  FF 4E FA        dec word ptr [bp - 6]
loc_1A84:
1A84  8B 7E FC        mov di, word ptr [bp - 4]
1A87  D1 E7           shl di, 1
1A89  8B F7           mov si, di
1A8B  D1 E7           shl di, 1
1A8D  03 FE           add di, si
1A8F  80 BD 38 7C FF  cmp byte ptr [di + 0x7c38], 0xff
1A94  74 04           je 0x1a9a
1A96  B0 00           mov al, 0
1A98  EB 02           jmp 0x1a9c
loc_1A9A:
1A9A  B0 01           mov al, 1
loc_1A9C:
1A9C  88 46 F5        mov byte ptr [bp - 0xb], al
1A9F  80 7E F5 00     cmp byte ptr [bp - 0xb], 0
1AA3  74 49           je 0x1aee
1AA5  C4 7E F6        les di, ptr [bp - 0xa]
1AA8  26 8B 05        mov ax, word ptr es:[di]
1AAB  2D 8F 01        sub ax, 0x18f
1AAE  D1 E0           shl ax, 1
1AB0  8B C8           mov cx, ax
1AB2  8B 46 FA        mov ax, word ptr [bp - 6]
1AB5  05 06 00        add ax, 6
1AB8  BA A0 00        mov dx, 0xa0
1ABB  F7 E2           mul dx
1ABD  C4 3E 6A A9     les di, ptr [0xa96a]
1AC1  03 F8           add di, ax
1AC3  03 F9           add di, cx
1AC5  81 C7 5E FF     add di, 0xff5e
1AC9  06              push es
1ACA  57              push di
1ACB  C4 7E F6        les di, ptr [bp - 0xa]
1ACE  26 8B 05        mov ax, word ptr es:[di]
1AD1  2D 8F 01        sub ax, 0x18f
1AD4  8B D0           mov dx, ax
1AD6  C4 7E F6        les di, ptr [bp - 0xa]
1AD9  26 8B 05        mov ax, word ptr es:[di]
1ADC  2D 6F 01        sub ax, 0x16f
1ADF  2B C2           sub ax, dx
1AE1  40              inc ax
1AE2  50              push ax
1AE3  B8 20 00        mov ax, 0x20
1AE6  50              push ax
1AE7  9A 00 00 4B 21  call far 214B:0000
1AEC  EB 2D           jmp 0x1b1b
loc_1AEE:
1AEE  FF 76 FC        push word ptr [bp - 4]
1AF1  8B 46 FA        mov ax, word ptr [bp - 6]
1AF4  05 06 00        add ax, 6
1AF7  50              push ax
1AF8  C4 7E F6        les di, ptr [bp - 0xa]
1AFB  26 8B 05        mov ax, word ptr es:[di]
1AFE  2D 8F 01        sub ax, 0x18f
1B01  50              push ax
1B02  E8 24 FD        call 0x1829
1B05  8D 7E FC        lea di, [bp - 4]
1B08  16              push ss
1B09  57              push di
1B0A  B8 01 00        mov ax, 1
1B0D  50              push ax
1B0E  B8 C8 00        mov ax, 0xc8
1B11  50              push ax
1B12  B8 FF FF        mov ax, 0xffff
1B15  50              push ax
1B16  9A 86 1C 4B 21  call far 214B:1C86
loc_1B1B:
1B1B  83 7E FA 01     cmp word ptr [bp - 6], 1
1B1F  74 03           je 0x1b24
1B21  E9 5D FF        jmp 0x1a81
loc_1B24:
1B24  9A DD 08 4B 21  call far 214B:08DD
1B29  A0 76 A9        mov al, byte ptr [0xa976]
1B2C  3C AC           cmp al, 0xac
1B2E  74 04           je 0x1b34
1B30  3C AD           cmp al, 0xad
1B32  75 50           jne 0x1b84
loc_1B34:
1B34  80 7E F5 00     cmp byte ptr [bp - 0xb], 0
1B38  75 47           jne 0x1b81
1B3A  80 3E 76 A9 AD  cmp byte ptr [0xa976], 0xad
1B3F  74 04           je 0x1b45
1B41  B0 00           mov al, 0
1B43  EB 02           jmp 0x1b47
loc_1B45:
1B45  B0 01           mov al, 1
loc_1B47:
1B47  98              cwde
1B48  8B F8           mov di, ax
1B4A  8A 85 1A 07     mov al, byte ptr [di + 0x71a]
1B4E  30 E4           xor ah, ah
1B50  89 46 F3        mov word ptr [bp - 0xd], ax
1B53  B8 01 00        mov ax, 1
1B56  3B 46 F3        cmp ax, word ptr [bp - 0xd]
1B59  77 26           ja 0x1b81
1B5B  89 46 FA        mov word ptr [bp - 6], ax
1B5E  EB 03           jmp 0x1b63
loc_1B60:
1B60  FF 46 FA        inc word ptr [bp - 6]
loc_1B63:
1B63  8D 7E FE        lea di, [bp - 2]
1B66  16              push ss
1B67  57              push di
1B68  B8 01 00        mov ax, 1
1B6B  50              push ax
1B6C  B8 C8 00        mov ax, 0xc8
1B6F  50              push ax
1B70  B8 FF FF        mov ax, 0xffff
1B73  50              push ax
1B74  9A 86 1C 4B 21  call far 214B:1C86
1B79  8B 46 FA        mov ax, word ptr [bp - 6]
1B7C  3B 46 F3        cmp ax, word ptr [bp - 0xd]
1B7F  75 DF           jne 0x1b60
loc_1B81:
1B81  E9 C3 00        jmp 0x1c47
loc_1B84:
1B84  3C B1           cmp al, 0xb1
1B86  74 04           je 0x1b8c
1B88  3C B2           cmp al, 0xb2
1B8A  75 52           jne 0x1bde
loc_1B8C:
1B8C  80 3E 76 A9 B2  cmp byte ptr [0xa976], 0xb2
1B91  74 04           je 0x1b97
1B93  B0 00           mov al, 0
1B95  EB 02           jmp 0x1b99
loc_1B97:
1B97  B0 01           mov al, 1
loc_1B99:
1B99  98              cwde
1B9A  8B F8           mov di, ax
1B9C  8A 85 1A 07     mov al, byte ptr [di + 0x71a]
1BA0  30 E4           xor ah, ah
1BA2  89 46 F3        mov word ptr [bp - 0xd], ax
1BA5  B8 01 00        mov ax, 1
1BA8  3B 46 F3        cmp ax, word ptr [bp - 0xd]
1BAB  77 2F           ja 0x1bdc
1BAD  89 46 FA        mov word ptr [bp - 6], ax
1BB0  EB 03           jmp 0x1bb5
loc_1BB2:
1BB2  FF 46 FA        inc word ptr [bp - 6]
loc_1BB5:
1BB5  8B 46 FE        mov ax, word ptr [bp - 2]
1BB8  3B 06 EE 80     cmp ax, word ptr [0x80ee]
1BBC  74 16           je 0x1bd4
1BBE  8D 7E FE        lea di, [bp - 2]
1BC1  16              push ss
1BC2  57              push di
1BC3  B8 01 00        mov ax, 1
1BC6  50              push ax
1BC7  B8 C8 00        mov ax, 0xc8
1BCA  50              push ax
1BCB  B8 01 00        mov ax, 1
1BCE  50              push ax
1BCF  9A 86 1C 4B 21  call far 214B:1C86
loc_1BD4:
1BD4  8B 46 FA        mov ax, word ptr [bp - 6]
1BD7  3B 46 F3        cmp ax, word ptr [bp - 0xd]
1BDA  75 D6           jne 0x1bb2
loc_1BDC:
1BDC  EB 69           jmp 0x1c47
loc_1BDE:
1BDE  3C AB           cmp al, 0xab
1BE0  75 5B           jne 0x1c3d
loc_1BE2:
1BE2  8B 7E FE        mov di, word ptr [bp - 2]
1BE5  D1 E7           shl di, 1
1BE7  8B F7           mov si, di
1BE9  D1 E7           shl di, 1
1BEB  03 FE           add di, si
1BED  80 BD 38 7C FF  cmp byte ptr [di + 0x7c38], 0xff
1BF2  74 18           je 0x1c0c
1BF4  8D 7E FE        lea di, [bp - 2]
1BF7  16              push ss
1BF8  57              push di
1BF9  B8 01 00        mov ax, 1
1BFC  50              push ax
1BFD  B8 C8 00        mov ax, 0xc8
1C00  50              push ax
1C01  B8 FF FF        mov ax, 0xffff
1C04  50              push ax
1C05  9A 86 1C 4B 21  call far 214B:1C86
1C0A  EB D6           jmp 0x1be2
loc_1C0C:
1C0C  C7 46 FA 01 00  mov word ptr [bp - 6], 1
1C11  EB 03           jmp 0x1c16
loc_1C13:
1C13  FF 46 FA        inc word ptr [bp - 6]
loc_1C16:
1C16  8B 46 FE        mov ax, word ptr [bp - 2]
1C19  3B 06 EE 80     cmp ax, word ptr [0x80ee]
1C1D  74 16           je 0x1c35
1C1F  8D 7E FE        lea di, [bp - 2]
1C22  16              push ss
1C23  57              push di
1C24  B8 01 00        mov ax, 1
1C27  50              push ax
1C28  B8 C8 00        mov ax, 0xc8
1C2B  50              push ax
1C2C  B8 01 00        mov ax, 1
1C2F  50              push ax
1C30  9A 86 1C 4B 21  call far 214B:1C86
loc_1C35:
1C35  83 7E FA 11     cmp word ptr [bp - 6], 0x11
1C39  75 D8           jne 0x1c13
1C3B  EB 0A           jmp 0x1c47
loc_1C3D:
1C3D  3C B0           cmp al, 0xb0
1C3F  75 06           jne 0x1c47
1C41  A1 EE 80        mov ax, word ptr [0x80ee]
1C44  89 46 FE        mov word ptr [bp - 2], ax
loc_1C47:
1C47  A0 76 A9        mov al, byte ptr [0xa976]
1C4A  50              push ax
1C4B  BF E4 19        mov di, 0x19e4
1C4E  0E              push cs
1C4F  57              push di
1C50  9A DF 08 E4 23  call far 23E4:08DF
1C55  75 03           jne 0x1c5a
1C57  E9 1A FE        jmp 0x1a74
loc_1C5A:
1C5A  C4 3E 22 7C     les di, ptr [0x7c22]
1C5E  06              push es
1C5F  57              push di
1C60  C4 3E 16 7C     les di, ptr [0x7c16]
1C64  06              push es
1C65  57              push di
1C66  B8 A0 0F        mov ax, 0xfa0
1C69  50              push ax
1C6A  9A 5D 02 E4 23  call far 23E4:025D
1C6F  C6 06 76 A9 00  mov byte ptr [0xa976], 0
loc_1C74:
1C74  89 EC           mov sp, bp
1C76  5D              pop bp
1C77  C3              ret

; ---- routine 0791:1C78  (found by: call)
sub_1C78:
1C78  55              push bp
1C79  89 E5           mov bp, sp
1C7B  83 EC 0E        sub sp, 0xe
1C7E  8B 3E EE 80     mov di, word ptr [0x80ee]
1C82  D1 E7           shl di, 1
1C84  8B F7           mov si, di
1C86  D1 E7           shl di, 1
1C88  03 FE           add di, si
1C8A  81 C7 38 7C     add di, 0x7c38
1C8E  89 7E F7        mov word ptr [bp - 9], di
1C91  8C 5E F9        mov word ptr [bp - 7], ds
1C94  8B 7E 04        mov di, word ptr [bp + 4]
1C97  36 8A 45 0A     mov al, byte ptr ss:[di + 0xa]
1C9B  98              cwde
1C9C  8B F8           mov di, ax
1C9E  D1 E7           shl di, 1
1CA0  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
1CA4  BA BF 00        mov dx, 0xbf
1CA7  F7 E2           mul dx
1CA9  C4 3E 17 A9     les di, ptr [0xa917]
1CAD  03 F8           add di, ax
1CAF  89 7E F3        mov word ptr [bp - 0xd], di
1CB2  8C 46 F5        mov word ptr [bp - 0xb], es
1CB5  8B 7E 04        mov di, word ptr [bp + 4]
1CB8  36 83 7D 08 00  cmp word ptr ss:[di + 8], 0
1CBD  75 07           jne 0x1cc6
1CBF  31 C0           xor ax, ax
1CC1  89 46 FD        mov word ptr [bp - 3], ax
1CC4  EB 15           jmp 0x1cdb
loc_1CC6:
1CC6  8B 7E 04        mov di, word ptr [bp + 4]
1CC9  36 8B 45 08     mov ax, word ptr ss:[di + 8]
1CCD  D1 E0           shl ax, 1
1CCF  C4 7E F3        les di, ptr [bp - 0xd]
1CD2  03 F8           add di, ax
1CD4  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1CD8  89 46 FD        mov word ptr [bp - 3], ax
loc_1CDB:
1CDB  8B 7E 04        mov di, word ptr [bp + 4]
1CDE  36 83 7D 06 00  cmp word ptr ss:[di + 6], 0
1CE3  75 07           jne 0x1cec
1CE5  31 C0           xor ax, ax
1CE7  89 46 FB        mov word ptr [bp - 5], ax
1CEA  EB 15           jmp 0x1d01
loc_1CEC:
1CEC  8B 7E 04        mov di, word ptr [bp + 4]
1CEF  36 8B 45 06     mov ax, word ptr ss:[di + 6]
1CF3  D1 E0           shl ax, 1
1CF5  C4 7E F3        les di, ptr [bp - 0xd]
1CF8  03 F8           add di, ax
1CFA  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1CFE  89 46 FB        mov word ptr [bp - 5], ax
loc_1D01:
1D01  8B 7E 04        mov di, word ptr [bp + 4]
1D04  36 8A 45 04     mov al, byte ptr ss:[di + 4]
1D08  C4 7E F7        les di, ptr [bp - 9]
1D0B  26 3A 05        cmp al, byte ptr es:[di]
1D0E  75 2C           jne 0x1d3c
1D10  8B 46 FD        mov ax, word ptr [bp - 3]
1D13  C4 7E F7        les di, ptr [bp - 9]
1D16  26 3B 45 01     cmp ax, word ptr es:[di + 1]
1D1A  75 20           jne 0x1d3c
1D1C  8B 46 FB        mov ax, word ptr [bp - 5]
1D1F  C4 7E F7        les di, ptr [bp - 9]
1D22  26 3B 45 03     cmp ax, word ptr es:[di + 3]
1D26  75 14           jne 0x1d3c
1D28  C4 7E F7        les di, ptr [bp - 9]
1D2B  26 8A 45 05     mov al, byte ptr es:[di + 5]
1D2F  8B 7E 04        mov di, word ptr [bp + 4]
1D32  36 3A 45 0A     cmp al, byte ptr ss:[di + 0xa]
1D36  75 04           jne 0x1d3c
1D38  B0 00           mov al, 0
1D3A  EB 02           jmp 0x1d3e
loc_1D3C:
1D3C  B0 01           mov al, 1
loc_1D3E:
1D3E  88 46 FF        mov byte ptr [bp - 1], al
1D41  8A 46 FF        mov al, byte ptr [bp - 1]
1D44  89 EC           mov sp, bp
1D46  5D              pop bp
1D47  C2 02 00        ret 2

; ---- routine 0791:1D4A  (found by: call)
sub_1D4A:
1D4A  55              push bp
1D4B  89 E5           mov bp, sp
1D4D  83 EC 0C        sub sp, 0xc
1D50  C6 46 FF 00     mov byte ptr [bp - 1], 0
1D54  83 3E EE 80 00  cmp word ptr [0x80ee], 0
1D59  74 0B           je 0x1d66
1D5B  55              push bp
1D5C  E8 19 FF        call 0x1c78
1D5F  08 C0           or al, al
1D61  75 03           jne 0x1d66
1D63  E9 E4 00        jmp 0x1e4a
loc_1D66:
1D66  8A 46 0A        mov al, byte ptr [bp + 0xa]
1D69  98              cwde
1D6A  8B F8           mov di, ax
1D6C  D1 E7           shl di, 1
1D6E  FF 85 F2 80     inc word ptr [di - 0x7f0e]
1D72  BF EE 80        mov di, 0x80ee
1D75  1E              push ds
1D76  57              push di
1D77  B8 01 00        mov ax, 1
1D7A  50              push ax
1D7B  B8 C8 00        mov ax, 0xc8
1D7E  50              push ax
1D7F  B8 01 00        mov ax, 1
1D82  50              push ax
1D83  9A 86 1C 4B 21  call far 214B:1C86
1D88  8B 3E EE 80     mov di, word ptr [0x80ee]
1D8C  D1 E7           shl di, 1
1D8E  8B F7           mov si, di
1D90  D1 E7           shl di, 1
1D92  03 FE           add di, si
1D94  81 C7 38 7C     add di, 0x7c38
1D98  89 7E F9        mov word ptr [bp - 7], di
1D9B  8C 5E FB        mov word ptr [bp - 5], ds
1D9E  8A 46 0A        mov al, byte ptr [bp + 0xa]
1DA1  98              cwde
1DA2  8B F8           mov di, ax
1DA4  D1 E7           shl di, 1
1DA6  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
1DAA  BA BF 00        mov dx, 0xbf
1DAD  F7 E2           mul dx
1DAF  C4 3E 17 A9     les di, ptr [0xa917]
1DB3  03 F8           add di, ax
1DB5  89 7E F5        mov word ptr [bp - 0xb], di
1DB8  8C 46 F7        mov word ptr [bp - 9], es
1DBB  8A 46 04        mov al, byte ptr [bp + 4]
1DBE  C4 7E F9        les di, ptr [bp - 7]
1DC1  26 88 05        mov byte ptr es:[di], al
1DC4  83 7E 08 00     cmp word ptr [bp + 8], 0
1DC8  76 17           jbe 0x1de1
1DCA  8B 46 08        mov ax, word ptr [bp + 8]
1DCD  D1 E0           shl ax, 1
1DCF  C4 7E F5        les di, ptr [bp - 0xb]
1DD2  03 F8           add di, ax
1DD4  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1DD8  C4 7E F9        les di, ptr [bp - 7]
1DDB  26 89 45 01     mov word ptr es:[di + 1], ax
1DDF  EB 09           jmp 0x1dea
loc_1DE1:
1DE1  C4 7E F9        les di, ptr [bp - 7]
1DE4  31 C0           xor ax, ax
1DE6  26 89 45 01     mov word ptr es:[di + 1], ax
loc_1DEA:
1DEA  83 7E 06 00     cmp word ptr [bp + 6], 0
1DEE  76 17           jbe 0x1e07
1DF0  8B 46 06        mov ax, word ptr [bp + 6]
1DF3  D1 E0           shl ax, 1
1DF5  C4 7E F5        les di, ptr [bp - 0xb]
1DF8  03 F8           add di, ax
1DFA  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1DFE  C4 7E F9        les di, ptr [bp - 7]
1E01  26 89 45 03     mov word ptr es:[di + 3], ax
1E05  EB 09           jmp 0x1e10
loc_1E07:
1E07  C4 7E F9        les di, ptr [bp - 7]
1E0A  31 C0           xor ax, ax
1E0C  26 89 45 03     mov word ptr es:[di + 3], ax
loc_1E10:
1E10  8A 46 0A        mov al, byte ptr [bp + 0xa]
1E13  C4 7E F9        les di, ptr [bp - 7]
1E16  26 88 45 05     mov byte ptr es:[di + 5], al
1E1A  A1 EE 80        mov ax, word ptr [0x80ee]
1E1D  89 46 FD        mov word ptr [bp - 3], ax
1E20  8D 7E FD        lea di, [bp - 3]
1E23  16              push ss
1E24  57              push di
1E25  B8 01 00        mov ax, 1
1E28  50              push ax
1E29  B8 C8 00        mov ax, 0xc8
1E2C  50              push ax
1E2D  B8 01 00        mov ax, 1
1E30  50              push ax
1E31  9A 86 1C 4B 21  call far 214B:1C86
1E36  8B 7E FD        mov di, word ptr [bp - 3]
1E39  D1 E7           shl di, 1
1E3B  8B F7           mov si, di
1E3D  D1 E7           shl di, 1
1E3F  03 FE           add di, si
1E41  C6 85 38 7C FF  mov byte ptr [di + 0x7c38], 0xff
1E46  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_1E4A:
1E4A  8A 46 FF        mov al, byte ptr [bp - 1]
1E4D  89 EC           mov sp, bp
1E4F  5D              pop bp
1E50  C2 08 00        ret 8

; ---- routine 0791:1E53  (found by: call)
sub_1E53:
1E53  55              push bp
1E54  89 E5           mov bp, sp
1E56  83 EC 08        sub sp, 8
1E59  8B 7E 04        mov di, word ptr [bp + 4]
1E5C  36 8A 45 0A     mov al, byte ptr ss:[di + 0xa]
1E60  98              cwde
1E61  8B F8           mov di, ax
1E63  8A 85 68 06     mov al, byte ptr [di + 0x668]
1E67  30 E4           xor ah, ah
1E69  8B 7E 04        mov di, word ptr [bp + 4]
1E6C  36 03 45 08     add ax, word ptr ss:[di + 8]
1E70  BA 16 00        mov dx, 0x16
1E73  F7 E2           mul dx
1E75  8B F8           mov di, ax
1E77  81 C7 E8 80     add di, 0x80e8
1E7B  89 7E FC        mov word ptr [bp - 4], di
1E7E  8C 5E FE        mov word ptr [bp - 2], ds
1E81  C4 7E FC        les di, ptr [bp - 4]
1E84  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
1E88  BA 14 00        mov dx, 0x14
1E8B  F7 E2           mul dx
1E8D  C4 3E 1B A9     les di, ptr [0xa91b]
1E91  03 F8           add di, ax
1E93  89 7E F8        mov word ptr [bp - 8], di
1E96  8C 46 FA        mov word ptr [bp - 6], es
1E99  8B 7E 04        mov di, word ptr [bp + 4]
1E9C  36 8A 45 04     mov al, byte ptr ss:[di + 4]
1EA0  98              cwde
1EA1  8B F8           mov di, ax
1EA3  8A 85 20 07     mov al, byte ptr [di + 0x720]
1EA7  98              cwde
1EA8  C4 7E F8        les di, ptr [bp - 8]
1EAB  26 01 45 12     add word ptr es:[di + 0x12], ax
1EAF  89 EC           mov sp, bp
1EB1  5D              pop bp
1EB2  C2 02 00        ret 2

; ---- routine 0791:1EB5  (found by: call)
sub_1EB5:
1EB5  55              push bp
1EB6  89 E5           mov bp, sp
1EB8  83 EC 04        sub sp, 4
1EBB  55              push bp
1EBC  E8 94 FF        call 0x1e53
1EBF  8A 46 0A        mov al, byte ptr [bp + 0xa]
1EC2  50              push ax
1EC3  FF 76 08        push word ptr [bp + 8]
1EC6  FF 76 06        push word ptr [bp + 6]
1EC9  8A 46 04        mov al, byte ptr [bp + 4]
1ECC  50              push ax
1ECD  E8 7A FE        call 0x1d4a
1ED0  08 C0           or al, al
1ED2  74 62           je 0x1f36
1ED4  A1 EE 80        mov ax, word ptr [0x80ee]
1ED7  31 D2           xor dx, dx
1ED9  05 FE FF        add ax, 0xfffe
1EDC  83 D2 FF        adc dx, -1
1EDF  89 46 FC        mov word ptr [bp - 4], ax
1EE2  A1 EE 80        mov ax, word ptr [0x80ee]
1EE5  3B 46 FC        cmp ax, word ptr [bp - 4]
1EE8  7C 3F           jl 0x1f29
1EEA  89 46 FE        mov word ptr [bp - 2], ax
1EED  EB 03           jmp 0x1ef2
loc_1EEF:
1EEF  FF 4E FE        dec word ptr [bp - 2]
loc_1EF2:
1EF2  83 7E FE 00     cmp word ptr [bp - 2], 0
1EF6  7E 29           jle 0x1f21
1EF8  FF 76 FE        push word ptr [bp - 2]
1EFB  8B 46 FE        mov ax, word ptr [bp - 2]
1EFE  99              cdq
1EFF  8B C8           mov cx, ax
1F01  8B DA           mov bx, dx
1F03  A1 EE 80        mov ax, word ptr [0x80ee]
1F06  31 D2           xor dx, dx
1F08  2B C1           sub ax, cx
1F0A  1B D3           sbb dx, bx
1F0C  8B C8           mov cx, ax
1F0E  8B DA           mov bx, dx
1F10  B8 04 00        mov ax, 4
1F13  31 D2           xor dx, dx
1F15  2B C1           sub ax, cx
1F17  1B D3           sbb dx, bx
1F19  50              push ax
1F1A  B8 21 00        mov ax, 0x21
1F1D  50              push ax
1F1E  E8 08 F9        call 0x1829
loc_1F21:
1F21  8B 46 FE        mov ax, word ptr [bp - 2]
1F24  3B 46 FC        cmp ax, word ptr [bp - 4]
1F27  75 C6           jne 0x1eef
loc_1F29:
1F29  C4 06 16 7C     les ax, ptr [0x7c16]
1F2D  8C C2           mov dx, es
1F2F  A3 26 7C        mov word ptr [0x7c26], ax
1F32  89 16 28 7C     mov word ptr [0x7c28], dx
loc_1F36:
1F36  89 EC           mov sp, bp
1F38  5D              pop bp
1F39  C2 08 00        ret 8

; ---- routine 0791:1F3C  (found by: call)
sub_1F3C:
1F3C  55              push bp
1F3D  89 E5           mov bp, sp
1F3F  83 EC 0C        sub sp, 0xc
1F42  8A 46 04        mov al, byte ptr [bp + 4]
1F45  98              cwde
1F46  8B F8           mov di, ax
1F48  D1 E7           shl di, 1
1F4A  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
1F4E  BA BF 00        mov dx, 0xbf
1F51  F7 E2           mul dx
1F53  C4 3E 17 A9     les di, ptr [0xa917]
1F57  03 F8           add di, ax
1F59  89 7E F4        mov word ptr [bp - 0xc], di
1F5C  8C 46 F6        mov word ptr [bp - 0xa], es
1F5F  C7 46 F8 FF FF  mov word ptr [bp - 8], 0xffff
1F64  C7 46 FC 01 00  mov word ptr [bp - 4], 1
1F69  EB 03           jmp 0x1f6e
loc_1F6B:
1F6B  FF 46 FC        inc word ptr [bp - 4]
loc_1F6E:
1F6E  8B 46 FC        mov ax, word ptr [bp - 4]
1F71  D1 E0           shl ax, 1
1F73  C4 7E F4        les di, ptr [bp - 0xc]
1F76  03 F8           add di, ax
1F78  26 FF 75 FE     push word ptr es:[di - 2]
1F7C  9A 16 32 71 17  call far 1771:3216
1F81  08 C0           or al, al
1F83  75 43           jne 0x1fc8
1F85  8B 46 FC        mov ax, word ptr [bp - 4]
1F88  D1 E0           shl ax, 1
1F8A  C4 7E F4        les di, ptr [bp - 0xc]
1F8D  03 F8           add di, ax
1F8F  26 FF 75 FE     push word ptr es:[di - 2]
1F93  9A D9 30 71 17  call far 1771:30D9
1F98  31 D2           xor dx, dx
1F9A  8B C8           mov cx, ax
1F9C  8B DA           mov bx, dx
1F9E  8B 46 F8        mov ax, word ptr [bp - 8]
1FA1  99              cdq
1FA2  3B D3           cmp dx, bx
1FA4  7C 06           jl 0x1fac
1FA6  7F 20           jg 0x1fc8
1FA8  3B C1           cmp ax, cx
1FAA  73 1C           jae 0x1fc8
loc_1FAC:
1FAC  8B 46 FC        mov ax, word ptr [bp - 4]
1FAF  D1 E0           shl ax, 1
1FB1  C4 7E F4        les di, ptr [bp - 0xc]
1FB4  03 F8           add di, ax
1FB6  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1FBA  89 46 FA        mov word ptr [bp - 6], ax
1FBD  FF 76 FA        push word ptr [bp - 6]
1FC0  9A D9 30 71 17  call far 1771:30D9
1FC5  89 46 F8        mov word ptr [bp - 8], ax
loc_1FC8:
1FC8  83 7E FC 0B     cmp word ptr [bp - 4], 0xb
1FCC  75 9D           jne 0x1f6b
1FCE  8B 46 FA        mov ax, word ptr [bp - 6]
1FD1  89 46 FE        mov word ptr [bp - 2], ax
1FD4  8B 46 FE        mov ax, word ptr [bp - 2]
1FD7  89 EC           mov sp, bp
1FD9  5D              pop bp
1FDA  C2 02 00        ret 2

