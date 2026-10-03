; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 3 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:1527  (found by: call)
sub_1527:
1527  55              push bp
1528  89 E5           mov bp, sp
152A  83 EC 04        sub sp, 4
152D  8B 46 08        mov ax, word ptr [bp + 8]
1530  BA BF 00        mov dx, 0xbf
1533  F7 E2           mul dx
1535  C4 3E 17 A9     les di, ptr [0xa917]
1539  03 F8           add di, ax
153B  89 7E FC        mov word ptr [bp - 4], di
153E  8C 46 FE        mov word ptr [bp - 2], es
1541  FF 76 08        push word ptr [bp + 8]
1544  0E              push cs
1545  E8 9F FB        call 0x10e7
1548  48              dec ax
1549  99              cdq
154A  B9 08 00        mov cx, 8
154D  F7 F9           idiv cx
154F  8B F8           mov di, ax
1551  8A 85 84 78     mov al, byte ptr [di + 0x7884]
1555  30 E4           xor ah, ah
1557  8B F8           mov di, ax
1559  B1 04           mov cl, 4
155B  D3 E7           shl di, cl
155D  81 C7 B4 6E     add di, 0x6eb4
1561  1E              push ds
1562  57              push di
1563  8A 46 06        mov al, byte ptr [bp + 6]
1566  50              push ax
1567  8A 46 04        mov al, byte ptr [bp + 4]
156A  50              push ax
156B  BF 6E A9        mov di, 0xa96e
156E  1E              push ds
156F  57              push di
1570  9A 6D 02 4B 21  call far 214B:026D
1575  89 EC           mov sp, bp
1577  5D              pop bp
1578  C2 06 00        ret 6
; data (not reached as code), 2 bytes
157B                  db 01 02   ; ..

; ---- routine 1771:157D  (found by: call)
sub_157D:
157D  55              push bp
157E  89 E5           mov bp, sp
1580  81 EC 06 01     sub sp, 0x106
1584  8B 46 04        mov ax, word ptr [bp + 4]
1587  BA BF 00        mov dx, 0xbf
158A  F7 E2           mul dx
158C  C4 3E 17 A9     les di, ptr [0xa917]
1590  03 F8           add di, ax
1592  89 7E FA        mov word ptr [bp - 6], di
1595  8C 46 FC        mov word ptr [bp - 4], es
1598  BF BE 4B        mov di, 0x4bbe
159B  1E              push ds
159C  57              push di
159D  BF 6E A9        mov di, 0xa96e
15A0  1E              push ds
15A1  57              push di
15A2  9A 29 03 4B 21  call far 214B:0329
15A7  FF 76 04        push word ptr [bp + 4]
15AA  B8 08 00        mov ax, 8
15AD  50              push ax
15AE  B8 02 00        mov ax, 2
15B1  50              push ax
15B2  0E              push cs
15B3  E8 A2 F9        call 0xf58
15B6  FF 76 04        push word ptr [bp + 4]
15B9  B8 08 00        mov ax, 8
15BC  50              push ax
15BD  B8 19 00        mov ax, 0x19
15C0  50              push ax
15C1  E8 63 FF        call 0x1527
15C4  8D BE FA FE     lea di, [bp - 0x106]
15C8  16              push ss
15C9  57              push di
15CA  C4 7E FA        les di, ptr [bp - 6]
15CD  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
15D1  30 E4           xor ah, ah
15D3  50              push ax
15D4  0E              push cs
15D5  E8 6F F3        call 0x947
15D8  B0 0A           mov al, 0xa
15DA  50              push ax
15DB  B0 02           mov al, 2
15DD  50              push ax
15DE  BF 6E A9        mov di, 0xa96e
15E1  1E              push ds
15E2  57              push di
15E3  9A 6D 02 4B 21  call far 214B:026D
15E8  C4 7E FA        les di, ptr [bp - 6]
15EB  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
15EF  30 E4           xor ah, ah
15F1  50              push ax
15F2  B8 0A 00        mov ax, 0xa
15F5  50              push ax
15F6  B8 18 00        mov ax, 0x18
15F9  50              push ax
15FA  0E              push cs
15FB  E8 FA F4        call 0xaf8
15FE  8D BE FA FE     lea di, [bp - 0x106]
1602  16              push ss
1603  57              push di
1604  C4 7E FA        les di, ptr [bp - 6]
1607  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
160B  30 E4           xor ah, ah
160D  31 D2           xor dx, dx
160F  52              push dx
1610  50              push ax
1611  9A DA 09 4B 21  call far 214B:09DA
1616  B0 0C           mov al, 0xc
1618  50              push ax
1619  B0 0C           mov al, 0xc
161B  50              push ax
161C  BF 6E A9        mov di, 0xa96e
161F  1E              push ds
1620  57              push di
1621  9A A3 01 4B 21  call far 214B:01A3
1626  8D BE FA FE     lea di, [bp - 0x106]
162A  16              push ss
162B  57              push di
162C  C4 7E FA        les di, ptr [bp - 6]
162F  26 8A 45 29     mov al, byte ptr es:[di + 0x29]
1633  30 E4           xor ah, ah
1635  31 D2           xor dx, dx
1637  52              push dx
1638  50              push ax
1639  9A DA 09 4B 21  call far 214B:09DA
163E  B0 0C           mov al, 0xc
1640  50              push ax
1641  B0 10           mov al, 0x10
1643  50              push ax
1644  BF 6E A9        mov di, 0xa96e
1647  1E              push ds
1648  57              push di
1649  9A A3 01 4B 21  call far 214B:01A3
164E  8D BE FA FE     lea di, [bp - 0x106]
1652  16              push ss
1653  57              push di
1654  C4 7E FA        les di, ptr [bp - 6]
1657  26 8A 45 2A     mov al, byte ptr es:[di + 0x2a]
165B  30 E4           xor ah, ah
165D  31 D2           xor dx, dx
165F  52              push dx
1660  50              push ax
1661  9A DA 09 4B 21  call far 214B:09DA
1666  B0 0D           mov al, 0xd
1668  50              push ax
1669  B0 0C           mov al, 0xc
166B  50              push ax
166C  BF 6E A9        mov di, 0xa96e
166F  1E              push ds
1670  57              push di
1671  9A A3 01 4B 21  call far 214B:01A3
1676  8D BE FA FE     lea di, [bp - 0x106]
167A  16              push ss
167B  57              push di
167C  C4 7E FA        les di, ptr [bp - 6]
167F  26 8A 45 28     mov al, byte ptr es:[di + 0x28]
1683  30 E4           xor ah, ah
1685  31 D2           xor dx, dx
1687  52              push dx
1688  50              push ax
1689  9A DA 09 4B 21  call far 214B:09DA
168E  B0 0D           mov al, 0xd
1690  50              push ax
1691  B0 10           mov al, 0x10
1693  50              push ax
1694  BF 6E A9        mov di, 0xa96e
1697  1E              push ds
1698  57              push di
1699  9A A3 01 4B 21  call far 214B:01A3
169E  8D BE FA FE     lea di, [bp - 0x106]
16A2  16              push ss
16A3  57              push di
16A4  FF 76 04        push word ptr [bp + 4]
16A7  0E              push cs
16A8  E8 C1 F7        call 0xe6c
16AB  B0 0C           mov al, 0xc
16AD  50              push ax
16AE  B0 21           mov al, 0x21
16B0  50              push ax
16B1  BF 6E A9        mov di, 0xa96e
16B4  1E              push ds
16B5  57              push di
16B6  9A A3 01 4B 21  call far 214B:01A3
16BB  FF 76 04        push word ptr [bp + 4]
16BE  E8 0F FD        call 0x13d0
16C1  8B 3E 5E 9B     mov di, word ptr [0x9b5e]
16C5  8A 85 C4 78     mov al, byte ptr [di + 0x78c4]
16C9  30 E4           xor ah, ah
16CB  8B F8           mov di, ax
16CD  B1 04           mov cl, 4
16CF  D3 E7           shl di, cl
16D1  81 C7 B4 6E     add di, 0x6eb4
16D5  1E              push ds
16D6  57              push di
16D7  B0 14           mov al, 0x14
16D9  50              push ax
16DA  B0 2E           mov al, 0x2e
16DC  50              push ax
16DD  BF 6E A9        mov di, 0xa96e
16E0  1E              push ds
16E1  57              push di
16E2  9A 6D 02 4B 21  call far 214B:026D
16E7  8B 3E 5C 9B     mov di, word ptr [0x9b5c]
16EB  8A 85 D5 78     mov al, byte ptr [di + 0x78d5]
16EF  30 E4           xor ah, ah
16F1  8B F8           mov di, ax
16F3  B1 04           mov cl, 4
16F5  D3 E7           shl di, cl
16F7  81 C7 B4 6E     add di, 0x6eb4
16FB  1E              push ds
16FC  57              push di
16FD  B0 15           mov al, 0x15
16FF  50              push ax
1700  B0 2E           mov al, 0x2e
1702  50              push ax
1703  BF 6E A9        mov di, 0xa96e
1706  1E              push ds
1707  57              push di
1708  9A 6D 02 4B 21  call far 214B:026D
170D  8B 3E 60 9B     mov di, word ptr [0x9b60]
1711  8A 85 F6 78     mov al, byte ptr [di + 0x78f6]
1715  30 E4           xor ah, ah
1717  8B F8           mov di, ax
1719  B1 04           mov cl, 4
171B  D3 E7           shl di, cl
171D  81 C7 B4 6E     add di, 0x6eb4
1721  1E              push ds
1722  57              push di
1723  B0 16           mov al, 0x16
1725  50              push ax
1726  B0 2E           mov al, 0x2e
1728  50              push ax
1729  BF 6E A9        mov di, 0xa96e
172C  1E              push ds
172D  57              push di
172E  9A 6D 02 4B 21  call far 214B:026D
1733  8B 3E 5A 9B     mov di, word ptr [0x9b5a]
1737  8A 85 A3 78     mov al, byte ptr [di + 0x78a3]
173B  30 E4           xor ah, ah
173D  8B F8           mov di, ax
173F  B1 04           mov cl, 4
1741  D3 E7           shl di, cl
1743  81 C7 B4 6E     add di, 0x6eb4
1747  1E              push ds
1748  57              push di
1749  B0 17           mov al, 0x17
174B  50              push ax
174C  B0 2E           mov al, 0x2e
174E  50              push ax
174F  BF 6E A9        mov di, 0xa96e
1752  1E              push ds
1753  57              push di
1754  9A 6D 02 4B 21  call far 214B:026D
1759  B8 14 00        mov ax, 0x14
175C  50              push ax
175D  B8 2E 00        mov ax, 0x2e
1760  50              push ax
1761  A1 5E 9B        mov ax, word ptr [0x9b5e]
1764  B9 04 00        mov cx, 4
1767  D3 E0           shl ax, cl
1769  31 D2           xor dx, dx
176B  B9 10 00        mov cx, 0x10
176E  F7 F1           div cx
1770  50              push ax
1771  9A C5 13 4B 21  call far 214B:13C5
1776  B8 15 00        mov ax, 0x15
1779  50              push ax
177A  B8 2E 00        mov ax, 0x2e
177D  50              push ax
177E  A1 5C 9B        mov ax, word ptr [0x9b5c]
1781  B9 04 00        mov cx, 4
1784  D3 E0           shl ax, cl
1786  31 D2           xor dx, dx
1788  B9 20 00        mov cx, 0x20
178B  F7 F1           div cx
178D  50              push ax
178E  9A C5 13 4B 21  call far 214B:13C5
1793  B8 16 00        mov ax, 0x16
1796  50              push ax
1797  B8 2E 00        mov ax, 0x2e
179A  50              push ax
179B  A1 60 9B        mov ax, word ptr [0x9b60]
179E  B9 04 00        mov cx, 4
17A1  D3 E0           shl ax, cl
17A3  31 D2           xor dx, dx
17A5  B9 20 00        mov cx, 0x20
17A8  F7 F1           div cx
17AA  50              push ax
17AB  9A C5 13 4B 21  call far 214B:13C5
17B0  B8 17 00        mov ax, 0x17
17B3  50              push ax
17B4  B8 2E 00        mov ax, 0x2e
17B7  50              push ax
17B8  A1 5A 9B        mov ax, word ptr [0x9b5a]
17BB  B9 04 00        mov cx, 4
17BE  D3 E0           shl ax, cl
17C0  31 D2           xor dx, dx
17C2  B9 20 00        mov cx, 0x20
17C5  F7 F1           div cx
17C7  50              push ax
17C8  9A C5 13 4B 21  call far 214B:13C5
17CD  8D BE FA FE     lea di, [bp - 0x106]
17D1  16              push ss
17D2  57              push di
17D3  A1 64 9B        mov ax, word ptr [0x9b64]
17D6  31 D2           xor dx, dx
17D8  52              push dx
17D9  50              push ax
17DA  9A DA 09 4B 21  call far 214B:09DA
17DF  B0 13           mov al, 0x13
17E1  50              push ax
17E2  B0 31           mov al, 0x31
17E4  50              push ax
17E5  BF 6E A9        mov di, 0xa96e
17E8  1E              push ds
17E9  57              push di
17EA  9A 6D 02 4B 21  call far 214B:026D
17EF  8D BE FA FE     lea di, [bp - 0x106]
17F3  16              push ss
17F4  57              push di
17F5  A1 62 9B        mov ax, word ptr [0x9b62]
17F8  31 D2           xor dx, dx
17FA  52              push dx
17FB  50              push ax
17FC  9A DA 09 4B 21  call far 214B:09DA
1801  B0 13           mov al, 0x13
1803  50              push ax
1804  B0 3B           mov al, 0x3b
1806  50              push ax
1807  BF 6E A9        mov di, 0xa96e
180A  1E              push ds
180B  57              push di
180C  9A 6D 02 4B 21  call far 214B:026D
1811  C7 46 FE 01 00  mov word ptr [bp - 2], 1
1816  EB 03           jmp 0x181b
loc_1818:
1818  FF 46 FE        inc word ptr [bp - 2]
loc_181B:
181B  8B 7E FE        mov di, word ptr [bp - 2]
181E  8A 85 BF 6B     mov al, byte ptr [di + 0x6bbf]
1822  30 E4           xor ah, ah
1824  50              push ax
1825  C4 7E FA        les di, ptr [bp - 6]
1828  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
182C  30 E4           xor ah, ah
182E  50              push ax
182F  9A 57 0C 4B 21  call far 214B:0C57
1834  98              cwde
1835  B1 04           mov cl, 4
1837  D3 E0           shl ax, cl
1839  8B D0           mov dx, ax
183B  8B 7E FE        mov di, word ptr [bp - 2]
183E  8A 85 BF 6B     mov al, byte ptr [di + 0x6bbf]
1842  30 E4           xor ah, ah
1844  8B F8           mov di, ax
1846  B1 05           mov cl, 5
1848  D3 E7           shl di, cl
184A  03 FA           add di, dx
184C  81 C7 A0 6A     add di, 0x6aa0
1850  1E              push ds
1851  57              push di
1852  83 7E FE 03     cmp word ptr [bp - 2], 3
1856  77 04           ja 0x185c
1858  B0 00           mov al, 0
185A  EB 02           jmp 0x185e
loc_185C:
185C  B0 01           mov al, 1
loc_185E:
185E  30 E4           xor ah, ah
1860  8B D0           mov dx, ax
1862  8B 46 FE        mov ax, word ptr [bp - 2]
1865  05 08 00        add ax, 8
1868  03 C2           add ax, dx
186A  50              push ax
186B  B0 3D           mov al, 0x3d
186D  50              push ax
186E  BF 6E A9        mov di, 0xa96e
1871  1E              push ds
1872  57              push di
1873  9A A3 01 4B 21  call far 214B:01A3
1878  83 7E FE 08     cmp word ptr [bp - 2], 8
187C  75 9A           jne 0x1818
187E  FF 76 04        push word ptr [bp + 4]
1881  B0 01           mov al, 1
1883  50              push ax
1884  B0 00           mov al, 0
1886  50              push ax
1887  0E              push cs
1888  E8 39 F3        call 0xbc4
188B  B8 0F 00        mov ax, 0xf
188E  50              push ax
188F  E8 4F F9        call 0x11e1
1892  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
1897  74 19           je 0x18b2
1899  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
189E  74 12           je 0x18b2
18A0  A1 36 9B        mov ax, word ptr [0x9b36]
18A3  3B 46 04        cmp ax, word ptr [bp + 4]
18A6  74 04           je 0x18ac
18A8  B0 00           mov al, 0
18AA  EB 02           jmp 0x18ae
loc_18AC:
18AC  B0 01           mov al, 1
loc_18AE:
18AE  50              push ax
18AF  E8 D7 F9        call 0x1289
loc_18B2:
18B2  C4 7E FA        les di, ptr [bp - 6]
18B5  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
18B9  30 E4           xor ah, ah
18BB  8B F8           mov di, ax
18BD  8A 85 05 69     mov al, byte ptr [di + 0x6905]
18C1  50              push ax
18C2  C4 7E FA        les di, ptr [bp - 6]
18C5  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
18C9  30 E4           xor ah, ah
18CB  8B F8           mov di, ax
18CD  B1 03           mov cl, 3
18CF  D3 E7           shl di, cl
18D1  81 C7 92 6E     add di, 0x6e92
18D5  1E              push ds
18D6  57              push di
18D7  B0 0D           mov al, 0xd
18D9  50              push ax
18DA  B0 02           mov al, 2
18DC  50              push ax
18DD  BF 6E A9        mov di, 0xa96e
18E0  1E              push ds
18E1  57              push di
18E2  9A C8 02 4B 21  call far 214B:02C8
18E7  80 3E 64 A9 00  cmp byte ptr [0xa964], 0
18EC  75 40           jne 0x192e
18EE  C7 46 FE 01 00  mov word ptr [bp - 2], 1
18F3  EB 03           jmp 0x18f8
loc_18F5:
18F5  FF 46 FE        inc word ptr [bp - 2]
loc_18F8:
18F8  8B 46 FE        mov ax, word ptr [bp - 2]
18FB  8B C8           mov cx, ax
18FD  8B 46 04        mov ax, word ptr [bp + 4]
1900  BA 03 00        mov dx, 3
1903  F7 E2           mul dx
1905  8B F8           mov di, ax
1907  03 F9           add di, cx
1909  8A 85 7F 9D     mov al, byte ptr [di - 0x6281]
190D  50              push ax
190E  BF 7B 15        mov di, 0x157b
1911  0E              push cs
1912  57              push di
1913  B0 0D           mov al, 0xd
1915  50              push ax
1916  8B 7E FE        mov di, word ptr [bp - 2]
1919  8A 85 89 0D     mov al, byte ptr [di + 0xd89]
191D  50              push ax
191E  BF 6E A9        mov di, 0xa96e
1921  1E              push ds
1922  57              push di
1923  9A C8 02 4B 21  call far 214B:02C8
1928  83 7E FE 03     cmp word ptr [bp - 2], 3
192C  75 C7           jne 0x18f5
loc_192E:
192E  89 EC           mov sp, bp
1930  5D              pop bp
1931  C2 02 00        ret 2

; ---- routine 1771:1934  (found by: call)
sub_1934:
1934  55              push bp
1935  89 E5           mov bp, sp
1937  83 EC 02        sub sp, 2
193A  BF A8 17        mov di, 0x17a8
193D  1E              push ds
193E  57              push di
193F  BF 6E A9        mov di, 0xa96e
1942  1E              push ds
1943  57              push di
1944  9A 29 03 4B 21  call far 214B:0329
1949  C7 46 FE 01 00  mov word ptr [bp - 2], 1
194E  EB 03           jmp 0x1953
loc_1950:
1950  FF 46 FE        inc word ptr [bp - 2]
loc_1953:
1953  8B 46 FE        mov ax, word ptr [bp - 2]
1956  03 46 04        add ax, word ptr [bp + 4]
1959  48              dec ax
195A  C4 3E 56 9B     les di, ptr [0x9b56]
195E  03 F8           add di, ax
1960  26 8A 05        mov al, byte ptr es:[di]
1963  30 E4           xor ah, ah
1965  50              push ax
1966  8B 46 FE        mov ax, word ptr [bp - 2]
1969  05 07 00        add ax, 7
196C  50              push ax
196D  B8 41 00        mov ax, 0x41
1970  50              push ax
1971  0E              push cs
1972  E8 E3 F5        call 0xf58
1975  83 7E FE 10     cmp word ptr [bp - 2], 0x10
1979  75 D5           jne 0x1950
197B  89 EC           mov sp, bp
197D  5D              pop bp
197E  C2 02 00        ret 2

; ---- routine 1771:1981  (found by: call, far)
sub_1981:
1981  55              push bp
1982  89 E5           mov bp, sp
1984  83 EC 06        sub sp, 6
1987  8B 46 06        mov ax, word ptr [bp + 6]
198A  BA BF 00        mov dx, 0xbf
198D  F7 E2           mul dx
198F  C4 3E 17 A9     les di, ptr [0xa917]
1993  03 F8           add di, ax
1995  89 7E FB        mov word ptr [bp - 5], di
1998  8C 46 FD        mov word ptr [bp - 3], es
199B  B0 00           mov al, 0
199D  08 C0           or al, al
199F  75 16           jne 0x19b7
19A1  FF 76 06        push word ptr [bp + 6]
19A4  0E              push cs
19A5  E8 CF F1        call 0xb77
19A8  08 C0           or al, al
19AA  74 07           je 0x19b3
19AC  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
19B1  74 04           je 0x19b7
loc_19B3:
19B3  B0 00           mov al, 0
19B5  EB 02           jmp 0x19b9
loc_19B7:
19B7  B0 01           mov al, 1
loc_19B9:
19B9  88 46 FF        mov byte ptr [bp - 1], al
19BC  80 7E FF 00     cmp byte ptr [bp - 1], 0
19C0  74 11           je 0x19d3
19C2  BF 0C 1E        mov di, 0x1e0c
19C5  1E              push ds
19C6  57              push di
19C7  BF 6E A9        mov di, 0xa96e
19CA  1E              push ds
19CB  57              push di
19CC  9A 29 03 4B 21  call far 214B:0329
19D1  EB 0F           jmp 0x19e2
loc_19D3:
19D3  BF A6 14        mov di, 0x14a6
19D6  1E              push ds
19D7  57              push di
19D8  BF 6E A9        mov di, 0xa96e
19DB  1E              push ds
19DC  57              push di
19DD  9A 29 03 4B 21  call far 214B:0329
loc_19E2:
19E2  FF 76 06        push word ptr [bp + 6]
19E5  E8 95 FB        call 0x157d
19E8  80 7E FF 00     cmp byte ptr [bp - 1], 0
19EC  74 28           je 0x1a16
19EE  83 3E 8E 0D 03  cmp word ptr [0xd8e], 3
19F3  77 04           ja 0x19f9
19F5  B0 00           mov al, 0
19F7  EB 02           jmp 0x19fb
loc_19F9:
19F9  B0 01           mov al, 1
loc_19FB:
19FB  98              cwde
19FC  8B F8           mov di, ax
19FE  8A 85 90 0D     mov al, byte ptr [di + 0xd90]
1A02  30 E4           xor ah, ah
1A04  03 06 8E 0D     add ax, word ptr [0xd8e]
1A08  50              push ax
1A09  B8 24 00        mov ax, 0x24
1A0C  50              push ax
1A0D  B8 1A 00        mov ax, 0x1a
1A10  50              push ax
1A11  9A C5 13 4B 21  call far 214B:13C5
loc_1A16:
1A16  BF 8E 0D        mov di, 0xd8e
1A19  1E              push ds
1A1A  57              push di
1A1B  B8 08 00        mov ax, 8
1A1E  50              push ax
1A1F  9A 60 15 4B 21  call far 214B:1560
1A24  80 7E FF 00     cmp byte ptr [bp - 1], 0
1A28  75 02           jne 0x1a2c
1A2A  EB 4B           jmp 0x1a77
loc_1A2C:
1A2C  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
1A31  75 19           jne 0x1a4c
1A33  8B 3E 8E 0D     mov di, word ptr [0xd8e]
1A37  8A 85 BF 6B     mov al, byte ptr [di + 0x6bbf]
1A3B  30 E4           xor ah, ah
1A3D  50              push ax
1A3E  C4 7E FB        les di, ptr [bp - 5]
1A41  81 C7 2D 00     add di, 0x2d
1A45  06              push es
1A46  57              push di
1A47  9A F4 0C 4B 21  call far 214B:0CF4
loc_1A4C:
1A4C  B0 01           mov al, 1
1A4E  08 C0           or al, al
1A50  74 16           je 0x1a68
1A52  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
1A57  74 0F           je 0x1a68
1A59  8B 3E 8E 0D     mov di, word ptr [0xd8e]
1A5D  80 BD BF 6B 08  cmp byte ptr [di + 0x6bbf], 8
1A62  75 04           jne 0x1a68
1A64  0E              push cs
1A65  E8 90 24        call 0x3ef8
loc_1A68:
1A68  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
1A6D  74 03           je 0x1a72
1A6F  E9 70 FF        jmp 0x19e2
loc_1A72:
1A72  C6 06 1A 0C 01  mov byte ptr [0xc1a], 1
loc_1A77:
1A77  89 EC           mov sp, bp
1A79  5D              pop bp
1A7A  CA 02 00        retf 2

; ---- routine 1771:1A7D  (found by: call)
sub_1A7D:
1A7D  55              push bp
1A7E  89 E5           mov bp, sp
1A80  C6 06 76 A9 B1  mov byte ptr [0xa976], 0xb1
loc_1A85:
1A85  8B 46 04        mov ax, word ptr [bp + 4]
1A88  8B C8           mov cx, ax
1A8A  8B 46 06        mov ax, word ptr [bp + 6]
1A8D  BA 03 00        mov dx, 3
1A90  F7 E2           mul dx
1A92  8B F8           mov di, ax
1A94  03 F9           add di, cx
1A96  81 C7 7F 9D     add di, 0x9d7f
1A9A  1E              push ds
1A9B  57              push di
1A9C  B8 0F 00        mov ax, 0xf
1A9F  50              push ax
1AA0  9A 52 14 4B 21  call far 214B:1452
1AA5  8B 46 04        mov ax, word ptr [bp + 4]
1AA8  8B C8           mov cx, ax
1AAA  8B 46 06        mov ax, word ptr [bp + 6]
1AAD  BA 03 00        mov dx, 3
1AB0  F7 E2           mul dx
1AB2  8B F8           mov di, ax
1AB4  03 F9           add di, cx
1AB6  8A 85 7F 9D     mov al, byte ptr [di - 0x6281]
1ABA  30 E4           xor ah, ah
1ABC  8B F8           mov di, ax
1ABE  80 BD 92 0D 00  cmp byte ptr [di + 0xd92], 0
1AC3  74 C0           je 0x1a85
1AC5  8B 46 06        mov ax, word ptr [bp + 6]
1AC8  BA 03 00        mov dx, 3
1ACB  F7 E2           mul dx
1ACD  8B F8           mov di, ax
1ACF  8A 8D 81 9D     mov cl, byte ptr [di - 0x627f]
1AD3  8B 46 06        mov ax, word ptr [bp + 6]
1AD6  BA 03 00        mov dx, 3
1AD9  F7 E2           mul dx
1ADB  8B F8           mov di, ax
1ADD  8A 85 80 9D     mov al, byte ptr [di - 0x6280]
1AE1  3A C1           cmp al, cl
1AE3  74 A0           je 0x1a85
1AE5  8B 46 06        mov ax, word ptr [bp + 6]
1AE8  BA 03 00        mov dx, 3
1AEB  F7 E2           mul dx
1AED  8B F8           mov di, ax
1AEF  8A 8D 82 9D     mov cl, byte ptr [di - 0x627e]
1AF3  8B 46 06        mov ax, word ptr [bp + 6]
1AF6  BA 03 00        mov dx, 3
1AF9  F7 E2           mul dx
1AFB  8B F8           mov di, ax
1AFD  8A 85 80 9D     mov al, byte ptr [di - 0x6280]
1B01  3A C1           cmp al, cl
1B03  74 80           je 0x1a85
1B05  8B 46 06        mov ax, word ptr [bp + 6]
1B08  BA 03 00        mov dx, 3
1B0B  F7 E2           mul dx
1B0D  8B F8           mov di, ax
1B0F  8A 8D 82 9D     mov cl, byte ptr [di - 0x627e]
1B13  8B 46 06        mov ax, word ptr [bp + 6]
1B16  BA 03 00        mov dx, 3
1B19  F7 E2           mul dx
1B1B  8B F8           mov di, ax
1B1D  8A 85 81 9D     mov al, byte ptr [di - 0x627f]
1B21  3A C1           cmp al, cl
1B23  75 03           jne 0x1b28
1B25  E9 5D FF        jmp 0x1a85
loc_1B28:
1B28  89 EC           mov sp, bp
1B2A  5D              pop bp
1B2B  C2 04 00        ret 4

; ---- routine 1771:1B2E  (found by: call, far)
sub_1B2E:
1B2E  55              push bp
1B2F  89 E5           mov bp, sp
1B31  83 EC 10        sub sp, 0x10
1B34  8B 46 0A        mov ax, word ptr [bp + 0xa]
1B37  BA 14 00        mov dx, 0x14
1B3A  F7 E2           mul dx
1B3C  C4 3E 1B A9     les di, ptr [0xa91b]
1B40  03 F8           add di, ax
1B42  89 7E F4        mov word ptr [bp - 0xc], di
1B45  8C 46 F6        mov word ptr [bp - 0xa], es
1B48  80 7E 06 00     cmp byte ptr [bp + 6], 0
1B4C  74 0C           je 0x1b5a
1B4E  C4 7E F4        les di, ptr [bp - 0xc]
1B51  26 8B 45 0A     mov ax, word ptr es:[di + 0xa]
1B55  89 46 FC        mov word ptr [bp - 4], ax
1B58  EB 0A           jmp 0x1b64
loc_1B5A:
1B5A  C4 7E F4        les di, ptr [bp - 0xc]
1B5D  26 8B 45 08     mov ax, word ptr es:[di + 8]
1B61  89 46 FC        mov word ptr [bp - 4], ax
loc_1B64:
1B64  80 7E 06 00     cmp byte ptr [bp + 6], 0
1B68  74 10           je 0x1b7a
1B6A  C4 3E 3B A9     les di, ptr [0xa93b]
1B6E  89 F8           mov ax, di
1B70  8C C2           mov dx, es
1B72  89 46 F8        mov word ptr [bp - 8], ax
1B75  89 56 FA        mov word ptr [bp - 6], dx
1B78  EB 0E           jmp 0x1b88
loc_1B7A:
1B7A  C4 3E 37 A9     les di, ptr [0xa937]
1B7E  89 F8           mov ax, di
1B80  8C C2           mov dx, es
1B82  89 46 F8        mov word ptr [bp - 8], ax
1B85  89 56 FA        mov word ptr [bp - 6], dx
loc_1B88:
1B88  C7 46 FE 01 00  mov word ptr [bp - 2], 1
1B8D  EB 03           jmp 0x1b92
loc_1B8F:
1B8F  FF 46 FE        inc word ptr [bp - 2]
loc_1B92:
1B92  8B 46 FE        mov ax, word ptr [bp - 2]
1B95  BA 0E 00        mov dx, 0xe
1B98  F7 E2           mul dx
1B9A  8B C8           mov cx, ax
1B9C  8B 46 08        mov ax, word ptr [bp + 8]
1B9F  BA 8C 00        mov dx, 0x8c
1BA2  F7 E2           mul dx
1BA4  C4 7E F8        les di, ptr [bp - 8]
1BA7  03 F8           add di, ax
1BA9  03 F9           add di, cx
1BAB  26 8B 85 72 FF  mov ax, word ptr es:[di - 0x8e]
1BB0  3B 46 FC        cmp ax, word ptr [bp - 4]
1BB3  76 03           jbe 0x1bb8
1BB5  E9 BC 00        jmp 0x1c74
loc_1BB8:
1BB8  83 7E FE 0A     cmp word ptr [bp - 2], 0xa
1BBC  73 50           jae 0x1c0e
1BBE  8B 46 FE        mov ax, word ptr [bp - 2]
1BC1  BA 0E 00        mov dx, 0xe
1BC4  F7 E2           mul dx
1BC6  8B C8           mov cx, ax
1BC8  8B 46 08        mov ax, word ptr [bp + 8]
1BCB  BA 8C 00        mov dx, 0x8c
1BCE  F7 E2           mul dx
1BD0  C4 7E F8        les di, ptr [bp - 8]
1BD3  03 F8           add di, ax
1BD5  03 F9           add di, cx
1BD7  81 C7 66 FF     add di, 0xff66
1BDB  06              push es
1BDC  57              push di
1BDD  8B 46 FE        mov ax, word ptr [bp - 2]
1BE0  40              inc ax
1BE1  BA 0E 00        mov dx, 0xe
1BE4  F7 E2           mul dx
1BE6  8B C8           mov cx, ax
1BE8  8B 46 08        mov ax, word ptr [bp + 8]
1BEB  BA 8C 00        mov dx, 0x8c
1BEE  F7 E2           mul dx
1BF0  C4 7E F8        les di, ptr [bp - 8]
1BF3  03 F8           add di, ax
1BF5  03 F9           add di, cx
1BF7  81 C7 66 FF     add di, 0xff66
1BFB  06              push es
1BFC  57              push di
1BFD  B8 0A 00        mov ax, 0xa
1C00  2B 46 FE        sub ax, word ptr [bp - 2]
1C03  B9 0E 00        mov cx, 0xe
1C06  F7 E1           mul cx
1C08  50              push ax
1C09  9A 3C 00 4B 21  call far 214B:003C
loc_1C0E:
1C0E  8B 46 FE        mov ax, word ptr [bp - 2]
1C11  BA 0E 00        mov dx, 0xe
1C14  F7 E2           mul dx
1C16  8B C8           mov cx, ax
1C18  8B 46 08        mov ax, word ptr [bp + 8]
1C1B  BA 8C 00        mov dx, 0x8c
1C1E  F7 E2           mul dx
1C20  C4 7E F8        les di, ptr [bp - 8]
1C23  03 F8           add di, ax
1C25  03 F9           add di, cx
1C27  81 C7 66 FF     add di, 0xff66
1C2B  89 7E F0        mov word ptr [bp - 0x10], di
1C2E  8C 46 F2        mov word ptr [bp - 0xe], es
1C31  8B 46 0A        mov ax, word ptr [bp + 0xa]
1C34  BA 0B 00        mov dx, 0xb
1C37  F7 E2           mul dx
1C39  C4 3E 6C 9B     les di, ptr [0x9b6c]
1C3D  03 F8           add di, ax
1C3F  06              push es
1C40  57              push di
1C41  C4 7E F0        les di, ptr [bp - 0x10]
1C44  81 C7 01 00     add di, 1
1C48  06              push es
1C49  57              push di
1C4A  B8 0A 00        mov ax, 0xa
1C4D  50              push ax
1C4E  9A 44 06 E4 23  call far 23E4:0644
1C53  8B 46 0A        mov ax, word ptr [bp + 0xa]
1C56  C4 3E 70 9B     les di, ptr [0x9b70]
1C5A  03 F8           add di, ax
1C5C  26 8A 05        mov al, byte ptr es:[di]
1C5F  C4 7E F0        les di, ptr [bp - 0x10]
1C62  26 88 05        mov byte ptr es:[di], al
1C65  8B 46 FC        mov ax, word ptr [bp - 4]
1C68  C4 7E F0        les di, ptr [bp - 0x10]
1C6B  26 89 45 0C     mov word ptr es:[di + 0xc], ax
1C6F  C7 46 FE 0A 00  mov word ptr [bp - 2], 0xa
loc_1C74:
1C74  83 7E FE 0A     cmp word ptr [bp - 2], 0xa
1C78  74 03           je 0x1c7d
1C7A  E9 12 FF        jmp 0x1b8f
loc_1C7D:
1C7D  89 EC           mov sp, bp
1C7F  5D              pop bp
1C80  CA 06 00        retf 6
; data (not reached as code), 2 bytes
1C83                  db 01 2F   ; ./

; ---- routine 1771:1C85  (found by: call)
sub_1C85:
1C85  55              push bp
1C86  89 E5           mov bp, sp
1C88  81 EC 10 01     sub sp, 0x110
1C8C  C4 3E 23 A9     les di, ptr [0xa923]
1C90  89 7E F1        mov word ptr [bp - 0xf], di
1C93  8C 46 F3        mov word ptr [bp - 0xd], es
1C96  C6 06 B2 AA 03  mov byte ptr [0xaab2], 3
1C9B  C4 7E F1        les di, ptr [bp - 0xf]
1C9E  26 8B 45 38     mov ax, word ptr es:[di + 0x38]
1CA2  31 D2           xor dx, dx
1CA4  8B C8           mov cx, ax
1CA6  8B DA           mov bx, dx
1CA8  8B 7E 04        mov di, word ptr [bp + 4]
1CAB  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
1CAF  31 D2           xor dx, dx
1CB1  F7 D0           not ax
1CB3  F7 D2           not dx
1CB5  05 01 00        add ax, 1
1CB8  83 D2 00        adc dx, 0
1CBB  03 C1           add ax, cx
1CBD  13 D3           adc dx, bx
1CBF  05 01 00        add ax, 1
1CC2  83 D2 00        adc dx, 0
1CC5  B9 02 00        mov cx, 2
1CC8  31 DB           xor bx, bx
1CCA  9A 79 02 E4 23  call far 23E4:0279
1CCF  8B C8           mov cx, ax
1CD1  8B DA           mov bx, dx
1CD3  C4 7E F1        les di, ptr [bp - 0xf]
1CD6  26 8B 45 3A     mov ax, word ptr es:[di + 0x3a]
1CDA  31 D2           xor dx, dx
1CDC  03 C1           add ax, cx
1CDE  13 D3           adc dx, bx
1CE0  8B 7E 04        mov di, word ptr [bp + 4]
1CE3  36 89 45 F6     mov word ptr ss:[di - 0xa], ax
1CE7  8B 7E 04        mov di, word ptr [bp + 4]
1CEA  36 8B 45 F6     mov ax, word ptr ss:[di - 0xa]
1CEE  31 D2           xor dx, dx
1CF0  B9 64 00        mov cx, 0x64
1CF3  F7 F1           div cx
1CF5  92              xchg dx, ax
1CF6  31 D2           xor dx, dx
1CF8  52              push dx
1CF9  50              push ax
1CFA  B8 02 00        mov ax, 2
1CFD  50              push ax
1CFE  8D 7E F5        lea di, [bp - 0xb]
1D01  16              push ss
1D02  57              push di
1D03  B8 0A 00        mov ax, 0xa
1D06  50              push ax
1D07  9A F6 12 E4 23  call far 23E4:12F6
1D0C  80 7E F6 20     cmp byte ptr [bp - 0xa], 0x20
1D10  75 04           jne 0x1d16
1D12  C6 46 F6 30     mov byte ptr [bp - 0xa], 0x30
loc_1D16:
1D16  8D BE F1 FE     lea di, [bp - 0x10f]
1D1A  16              push ss
1D1B  57              push di
1D1C  8B 7E 04        mov di, word ptr [bp + 4]
1D1F  36 8B 45 F6     mov ax, word ptr ss:[di - 0xa]
1D23  48              dec ax
1D24  31 D2           xor dx, dx
1D26  52              push dx
1D27  50              push ax
1D28  9A DA 09 4B 21  call far 214B:09DA
1D2D  BF 83 1C        mov di, 0x1c83
1D30  0E              push cs
1D31  57              push di
1D32  9A B7 06 E4 23  call far 23E4:06B7
1D37  8D 7E F5        lea di, [bp - 0xb]
1D3A  16              push ss
1D3B  57              push di
1D3C  9A B7 06 E4 23  call far 23E4:06B7
1D41  C4 7E 06        les di, ptr [bp + 6]
1D44  06              push es
1D45  57              push di
1D46  B8 0A 00        mov ax, 0xa
1D49  50              push ax
1D4A  9A 44 06 E4 23  call far 23E4:0644
1D4F  89 EC           mov sp, bp
1D51  5D              pop bp
1D52  C2 02 00        ret 2
; data (not reached as code), 7 bytes
1D55                  db 02 57 43 01 43 01 20   ; .WC.C. 

; ---- routine 1771:1D5C  (found by: call)
sub_1D5C:
1D5C  55              push bp
1D5D  89 E5           mov bp, sp
1D5F  81 EC A2 01     sub sp, 0x1a2
1D63  8B 46 04        mov ax, word ptr [bp + 4]
1D66  BA BF 00        mov dx, 0xbf
1D69  F7 E2           mul dx
1D6B  C4 3E 17 A9     les di, ptr [0xa917]
1D6F  03 F8           add di, ax
1D71  89 BE 62 FF     mov word ptr [bp - 0x9e], di
1D75  8C 86 64 FF     mov word ptr [bp - 0x9c], es
1D79  BF D8 3B        mov di, 0x3bd8
1D7C  1E              push ds
1D7D  57              push di
1D7E  BF 6E A9        mov di, 0xa96e
1D81  1E              push ds
1D82  57              push di
1D83  9A 29 03 4B 21  call far 214B:0329
1D88  BF F2 26        mov di, 0x26f2
1D8B  1E              push ds
1D8C  57              push di
1D8D  BF 6E A9        mov di, 0xa96e
1D90  1E              push ds
1D91  57              push di
1D92  9A 29 03 4B 21  call far 214B:0329
1D97  BF F6 1A        mov di, 0x1af6
1D9A  1E              push ds
1D9B  57              push di
1D9C  BF 6E A9        mov di, 0xa96e
1D9F  1E              push ds
1DA0  57              push di
1DA1  9A 29 03 4B 21  call far 214B:0329
1DA6  FF 76 04        push word ptr [bp + 4]
1DA9  B8 14 00        mov ax, 0x14
1DAC  50              push ax
1DAD  B8 41 00        mov ax, 0x41
1DB0  50              push ax
1DB1  0E              push cs
1DB2  E8 A3 F1        call 0xf58
1DB5  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1DB9  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
1DBD  30 E4           xor ah, ah
1DBF  8B F8           mov di, ax
1DC1  8A 85 05 69     mov al, byte ptr [di + 0x6905]
1DC5  A2 B2 AA        mov byte ptr [0xaab2], al
1DC8  C6 46 F3 00     mov byte ptr [bp - 0xd], 0
1DCC  EB 03           jmp 0x1dd1
loc_1DCE:
1DCE  FE 46 F3        inc byte ptr [bp - 0xd]
loc_1DD1:
1DD1  C7 46 FC 01 00  mov word ptr [bp - 4], 1
1DD6  EB 03           jmp 0x1ddb
loc_1DD8:
1DD8  FF 46 FC        inc word ptr [bp - 4]
loc_1DDB:
1DDB  8D BE 62 FE     lea di, [bp - 0x19e]
1DDF  16              push ss
1DE0  57              push di
1DE1  8B 46 FC        mov ax, word ptr [bp - 4]
1DE4  8B D0           mov dx, ax
1DE6  8A 46 F3        mov al, byte ptr [bp - 0xd]
1DE9  98              cwde
1DEA  D1 E0           shl ax, 1
1DEC  D1 E0           shl ax, 1
1DEE  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1DF2  03 F8           add di, ax
1DF4  03 FA           add di, dx
1DF6  26 8A 45 32     mov al, byte ptr es:[di + 0x32]
1DFA  30 E4           xor ah, ah
1DFC  31 D2           xor dx, dx
1DFE  52              push dx
1DFF  50              push ax
1E00  9A DA 09 4B 21  call far 214B:09DA
1E05  8A 46 F3        mov al, byte ptr [bp - 0xd]
1E08  98              cwde
1E09  8B F8           mov di, ax
1E0B  8A 85 A2 0D     mov al, byte ptr [di + 0xda2]
1E0F  50              push ax
1E10  8B 7E FC        mov di, word ptr [bp - 4]
1E13  8A 85 A3 0D     mov al, byte ptr [di + 0xda3]
1E17  50              push ax
1E18  BF 6E A9        mov di, 0xa96e
1E1B  1E              push ds
1E1C  57              push di
1E1D  9A A3 01 4B 21  call far 214B:01A3
1E22  83 7E FC 04     cmp word ptr [bp - 4], 4
1E26  75 B0           jne 0x1dd8
1E28  80 7E F3 01     cmp byte ptr [bp - 0xd], 1
1E2C  75 A0           jne 0x1dce
1E2E  31 C0           xor ax, ax
1E30  89 46 FE        mov word ptr [bp - 2], ax
1E33  C7 46 FC 01 00  mov word ptr [bp - 4], 1
1E38  EB 03           jmp 0x1e3d
loc_1E3A:
1E3A  FF 46 FC        inc word ptr [bp - 4]
loc_1E3D:
1E3D  8B 46 FC        mov ax, word ptr [bp - 4]
1E40  D1 E0           shl ax, 1
1E42  8B F0           mov si, ax
1E44  D1 E0           shl ax, 1
1E46  03 C6           add ax, si
1E48  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1E4C  03 F8           add di, ax
1E4E  26 80 7D 35 00  cmp byte ptr es:[di + 0x35], 0
1E53  74 06           je 0x1e5b
1E55  8B 46 FC        mov ax, word ptr [bp - 4]
1E58  89 46 FE        mov word ptr [bp - 2], ax
loc_1E5B:
1E5B  83 7E FC 0A     cmp word ptr [bp - 4], 0xa
1E5F  75 D9           jne 0x1e3a
1E61  C7 46 F8 08 00  mov word ptr [bp - 8], 8
1E66  83 7E FE 00     cmp word ptr [bp - 2], 0
1E6A  77 03           ja 0x1e6f
1E6C  E9 DC 01        jmp 0x204b
loc_1E6F:
1E6F  8B 46 FE        mov ax, word ptr [bp - 2]
1E72  3D 01 00        cmp ax, 1
1E75  73 03           jae 0x1e7a
1E77  E9 D1 01        jmp 0x204b
loc_1E7A:
1E7A  89 46 FC        mov word ptr [bp - 4], ax
1E7D  EB 03           jmp 0x1e82
loc_1E7F:
1E7F  FF 4E FC        dec word ptr [bp - 4]
loc_1E82:
1E82  8B 46 FC        mov ax, word ptr [bp - 4]
1E85  D1 E0           shl ax, 1
1E87  8B F0           mov si, ax
1E89  D1 E0           shl ax, 1
1E8B  03 C6           add ax, si
1E8D  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1E91  03 F8           add di, ax
1E93  81 C7 35 00     add di, 0x35
1E97  89 BE 5E FF     mov word ptr [bp - 0xa2], di
1E9B  8C 86 60 FF     mov word ptr [bp - 0xa0], es
1E9F  FF 46 F8        inc word ptr [bp - 8]
1EA2  8D BE 5E FE     lea di, [bp - 0x1a2]
1EA6  16              push ss
1EA7  57              push di
1EA8  55              push bp
1EA9  E8 D9 FD        call 0x1c85
1EAC  8A 46 F8        mov al, byte ptr [bp - 8]
1EAF  50              push ax
1EB0  B0 02           mov al, 2
1EB2  50              push ax
1EB3  BF 6E A9        mov di, 0xa96e
1EB6  1E              push ds
1EB7  57              push di
1EB8  9A 6D 02 4B 21  call far 214B:026D
1EBD  8B 46 F6        mov ax, word ptr [bp - 0xa]
1EC0  31 D2           xor dx, dx
1EC2  B9 04 00        mov cx, 4
1EC5  F7 F1           div cx
1EC7  92              xchg dx, ax
1EC8  3D 02 00        cmp ax, 2
1ECB  75 1B           jne 0x1ee8
1ECD  B0 07           mov al, 7
1ECF  50              push ax
1ED0  BF 55 1D        mov di, 0x1d55
1ED3  0E              push cs
1ED4  57              push di
1ED5  8A 46 F8        mov al, byte ptr [bp - 8]
1ED8  50              push ax
1ED9  B0 0A           mov al, 0xa
1EDB  50              push ax
1EDC  BF 6E A9        mov di, 0xa96e
1EDF  1E              push ds
1EE0  57              push di
1EE1  9A C8 02 4B 21  call far 214B:02C8
1EE6  EB 50           jmp 0x1f38
loc_1EE8:
1EE8  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1EEC  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
1EF0  30 E4           xor ah, ah
1EF2  8B F8           mov di, ax
1EF4  8A 85 05 69     mov al, byte ptr [di + 0x6905]
1EF8  50              push ax
1EF9  8D BE 5E FE     lea di, [bp - 0x1a2]
1EFD  16              push ss
1EFE  57              push di
1EFF  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1F03  26 80 7D 2C 01  cmp byte ptr es:[di + 0x2c], 1
1F08  74 04           je 0x1f0e
1F0A  B0 00           mov al, 0
1F0C  EB 02           jmp 0x1f10
loc_1F0E:
1F0E  B0 01           mov al, 1
loc_1F10:
1F10  98              cwde
1F11  8B F8           mov di, ax
1F13  8A 85 B2 0D     mov al, byte ptr [di + 0xdb2]
1F17  50              push ax
1F18  9A 5A 07 E4 23  call far 23E4:075A
1F1D  BF 58 1D        mov di, 0x1d58
1F20  0E              push cs
1F21  57              push di
1F22  9A B7 06 E4 23  call far 23E4:06B7
1F27  8A 46 F8        mov al, byte ptr [bp - 8]
1F2A  50              push ax
1F2B  B0 0A           mov al, 0xa
1F2D  50              push ax
1F2E  BF 6E A9        mov di, 0xa96e
1F31  1E              push ds
1F32  57              push di
1F33  9A C8 02 4B 21  call far 214B:02C8
loc_1F38:
1F38  C4 BE 62 FF     les di, ptr [bp - 0x9e]
1F3C  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
1F40  30 E4           xor ah, ah
1F42  8B F8           mov di, ax
1F44  8A 85 05 69     mov al, byte ptr [di + 0x6905]
1F48  A2 B2 AA        mov byte ptr [0xaab2], al
1F4B  8D BE 5E FE     lea di, [bp - 0x1a2]
1F4F  16              push ss
1F50  57              push di
1F51  C4 BE 5E FF     les di, ptr [bp - 0xa2]
1F55  26 8A 45 01     mov al, byte ptr es:[di + 1]
1F59  30 E4           xor ah, ah
1F5B  31 D2           xor dx, dx
1F5D  52              push dx
1F5E  50              push ax
1F5F  9A DA 09 4B 21  call far 214B:09DA
1F64  8A 46 F8        mov al, byte ptr [bp - 8]
1F67  50              push ax
1F68  B0 0E           mov al, 0xe
1F6A  50              push ax
1F6B  BF 6E A9        mov di, 0xa96e
1F6E  1E              push ds
1F6F  57              push di
1F70  9A A3 01 4B 21  call far 214B:01A3
1F75  8D BE 5E FE     lea di, [bp - 0x1a2]
1F79  16              push ss
1F7A  57              push di
1F7B  C4 BE 5E FF     les di, ptr [bp - 0xa2]
1F7F  26 8A 45 02     mov al, byte ptr es:[di + 2]
1F83  30 E4           xor ah, ah
1F85  31 D2           xor dx, dx
1F87  52              push dx
1F88  50              push ax
1F89  9A DA 09 4B 21  call far 214B:09DA
1F8E  8A 46 F8        mov al, byte ptr [bp - 8]
1F91  50              push ax
1F92  B0 11           mov al, 0x11
1F94  50              push ax
1F95  BF 6E A9        mov di, 0xa96e
1F98  1E              push ds
1F99  57              push di
1F9A  9A A3 01 4B 21  call far 214B:01A3
1F9F  8D BE 5E FE     lea di, [bp - 0x1a2]
1FA3  16              push ss
1FA4  57              push di
1FA5  C4 BE 5E FF     les di, ptr [bp - 0xa2]
1FA9  26 8A 45 03     mov al, byte ptr es:[di + 3]
1FAD  30 E4           xor ah, ah
1FAF  31 D2           xor dx, dx
1FB1  52              push dx
1FB2  50              push ax
1FB3  9A DA 09 4B 21  call far 214B:09DA
1FB8  8A 46 F8        mov al, byte ptr [bp - 8]
1FBB  50              push ax
1FBC  B0 14           mov al, 0x14
1FBE  50              push ax
1FBF  BF 6E A9        mov di, 0xa96e
1FC2  1E              push ds
1FC3  57              push di
1FC4  9A A3 01 4B 21  call far 214B:01A3
1FC9  8D BE 5E FE     lea di, [bp - 0x1a2]
1FCD  16              push ss
1FCE  57              push di
1FCF  C4 BE 5E FF     les di, ptr [bp - 0xa2]
1FD3  26 8A 45 04     mov al, byte ptr es:[di + 4]
1FD7  30 E4           xor ah, ah
1FD9  31 D2           xor dx, dx
1FDB  52              push dx
1FDC  50              push ax
1FDD  9A DA 09 4B 21  call far 214B:09DA
1FE2  8A 46 F8        mov al, byte ptr [bp - 8]
1FE5  50              push ax
1FE6  B0 17           mov al, 0x17
1FE8  50              push ax
1FE9  BF 6E A9        mov di, 0xa96e
1FEC  1E              push ds
1FED  57              push di
1FEE  9A A3 01 4B 21  call far 214B:01A3
1FF3  8D BE 5E FE     lea di, [bp - 0x1a2]
1FF7  16              push ss
1FF8  57              push di
1FF9  C4 BE 5E FF     les di, ptr [bp - 0xa2]
1FFD  26 8A 45 05     mov al, byte ptr es:[di + 5]
2001  30 E4           xor ah, ah
2003  31 D2           xor dx, dx
2005  52              push dx
2006  50              push ax
2007  9A DA 09 4B 21  call far 214B:09DA
200C  8A 46 F8        mov al, byte ptr [bp - 8]
200F  50              push ax
2010  B0 1A           mov al, 0x1a
2012  50              push ax
2013  BF 6E A9        mov di, 0xa96e
2016  1E              push ds
2017  57              push di
2018  9A A3 01 4B 21  call far 214B:01A3
201D  8D BE 5E FE     lea di, [bp - 0x1a2]
2021  16              push ss
2022  57              push di
2023  C4 BE 5E FF     les di, ptr [bp - 0xa2]
2027  26 8A 05        mov al, byte ptr es:[di]
202A  30 E4           xor ah, ah
202C  50              push ax
202D  0E              push cs
202E  E8 DA 37        call 0x580b
2031  8A 46 F8        mov al, byte ptr [bp - 8]
2034  50              push ax
2035  B0 26           mov al, 0x26
2037  50              push ax
2038  BF 6E A9        mov di, 0xa96e
203B  1E              push ds
203C  57              push di
203D  9A A3 01 4B 21  call far 214B:01A3
2042  83 7E FC 01     cmp word ptr [bp - 4], 1
2046  74 03           je 0x204b
2048  E9 34 FE        jmp 0x1e7f
loc_204B:
204B  C6 46 F3 00     mov byte ptr [bp - 0xd], 0
204F  EB 03           jmp 0x2054
loc_2051:
2051  FE 46 F3        inc byte ptr [bp - 0xd]
loc_2054:
2054  31 C0           xor ax, ax
2056  89 46 FC        mov word ptr [bp - 4], ax
2059  EB 03           jmp 0x205e
loc_205B:
205B  FF 46 FC        inc word ptr [bp - 4]
loc_205E:
205E  8B 46 FC        mov ax, word ptr [bp - 4]
2061  B1 03           mov cl, 3
2063  D3 E0           shl ax, cl
2065  8B D8           mov bx, ax
2067  8A 46 F3        mov al, byte ptr [bp - 0xd]
206A  98              cwde
206B  BA 18 00        mov dx, 0x18
206E  F7 E2           mul dx
2070  C4 BE 62 FF     les di, ptr [bp - 0x9e]
2074  03 F8           add di, ax
2076  03 FB           add di, bx
2078  81 C7 77 00     add di, 0x77
207C  89 BE 5E FF     mov word ptr [bp - 0xa2], di
2080  8C 86 60 FF     mov word ptr [bp - 0xa0], es
2084  C4 BE 5E FF     les di, ptr [bp - 0xa2]
2088  26 83 7D 06 00  cmp word ptr es:[di + 6], 0
208D  75 03           jne 0x2092
208F  E9 8D 00        jmp 0x211f
loc_2092:
2092  8B 46 FC        mov ax, word ptr [bp - 4]
2095  B1 03           mov cl, 3
2097  D3 E0           shl ax, cl
2099  8B D8           mov bx, ax
209B  8A 46 F3        mov al, byte ptr [bp - 0xd]
209E  98              cwde
209F  BA 18 00        mov dx, 0x18
20A2  F7 E2           mul dx
20A4  C4 BE 62 FF     les di, ptr [bp - 0x9e]
20A8  03 F8           add di, ax
20AA  03 FB           add di, bx
20AC  81 C7 77 00     add di, 0x77
20B0  06              push es
20B1  57              push di
20B2  8B 7E FC        mov di, word ptr [bp - 4]
20B5  8A 85 AA 0D     mov al, byte ptr [di + 0xdaa]
20B9  30 E4           xor ah, ah
20BB  50              push ax
20BC  8A 46 F3        mov al, byte ptr [bp - 0xd]
20BF  98              cwde
20C0  8B F8           mov di, ax
20C2  8A 85 A8 0D     mov al, byte ptr [di + 0xda8]
20C6  30 E4           xor ah, ah
20C8  50              push ax
20C9  0E              push cs
20CA  E8 2D 56        call 0x76fa
20CD  C6 46 F2 00     mov byte ptr [bp - 0xe], 0
20D1  EB 03           jmp 0x20d6
loc_20D3:
20D3  FE 46 F2        inc byte ptr [bp - 0xe]
loc_20D6:
20D6  8A 46 F2        mov al, byte ptr [bp - 0xe]
20D9  98              cwde
20DA  D1 E0           shl ax, 1
20DC  C4 BE 5E FF     les di, ptr [bp - 0xa2]
20E0  03 F8           add di, ax
20E2  26 8B 45 04     mov ax, word ptr es:[di + 4]
20E6  3B 46 04        cmp ax, word ptr [bp + 4]
20E9  74 2E           je 0x2119
20EB  8A 46 F2        mov al, byte ptr [bp - 0xe]
20EE  98              cwde
20EF  D1 E0           shl ax, 1
20F1  C4 BE 5E FF     les di, ptr [bp - 0xa2]
20F5  03 F8           add di, ax
20F7  26 FF 75 04     push word ptr es:[di + 4]
20FB  8B 7E FC        mov di, word ptr [bp - 4]
20FE  8A 85 AA 0D     mov al, byte ptr [di + 0xdaa]
2102  30 E4           xor ah, ah
2104  50              push ax
2105  8A 46 F3        mov al, byte ptr [bp - 0xd]
2108  98              cwde
2109  8B F8           mov di, ax
210B  8A 85 A8 0D     mov al, byte ptr [di + 0xda8]
210F  30 E4           xor ah, ah
2111  05 04 00        add ax, 4
2114  50              push ax
2115  0E              push cs
2116  E8 3F EE        call 0xf58
loc_2119:
2119  80 7E F2 01     cmp byte ptr [bp - 0xe], 1
211D  75 B4           jne 0x20d3
loc_211F:
211F  83 7E FC 02     cmp word ptr [bp - 4], 2
2123  74 03           je 0x2128
2125  E9 33 FF        jmp 0x205b
loc_2128:
2128  80 7E F3 01     cmp byte ptr [bp - 0xd], 1
212C  74 03           je 0x2131
212E  E9 20 FF        jmp 0x2051
loc_2131:
2131  C6 46 F3 00     mov byte ptr [bp - 0xd], 0
2135  EB 03           jmp 0x213a
loc_2137:
2137  FE 46 F3        inc byte ptr [bp - 0xd]
loc_213A:
213A  31 C0           xor ax, ax
213C  89 46 FC        mov word ptr [bp - 4], ax
213F  EB 03           jmp 0x2144
loc_2141:
2141  FF 46 FC        inc word ptr [bp - 4]
loc_2144:
2144  8A 46 F3        mov al, byte ptr [bp - 0xd]
2147  98              cwde
2148  8B F8           mov di, ax
214A  8A 85 AD 0D     mov al, byte ptr [di + 0xdad]
214E  30 E4           xor ah, ah
2150  8B D0           mov dx, ax
2152  8B 7E FC        mov di, word ptr [bp - 4]
2155  8A 85 AF 0D     mov al, byte ptr [di + 0xdaf]
2159  30 E4           xor ah, ah
215B  2B C2           sub ax, dx
215D  89 46 FA        mov word ptr [bp - 6], ax
2160  8D BE 62 FE     lea di, [bp - 0x19e]
2164  16              push ss
2165  57              push di
2166  8B 46 FC        mov ax, word ptr [bp - 4]
2169  8B C8           mov cx, ax
216B  8A 46 F3        mov al, byte ptr [bp - 0xd]
216E  98              cwde
216F  BA 03 00        mov dx, 3
2172  F7 E2           mul dx
2174  C4 BE 62 FF     les di, ptr [bp - 0x9e]
2178  03 F8           add di, ax
217A  03 F9           add di, cx
217C  26 8A 85 A7 00  mov al, byte ptr es:[di + 0xa7]
2181  30 E4           xor ah, ah
2183  31 D2           xor dx, dx
2185  52              push dx
2186  50              push ax
2187  9A DA 09 4B 21  call far 214B:09DA
218C  B0 03           mov al, 3
218E  50              push ax
218F  8A 46 FA        mov al, byte ptr [bp - 6]
2192  50              push ax
2193  BF 6E A9        mov di, 0xa96e
2196  1E              push ds
2197  57              push di
2198  9A A3 01 4B 21  call far 214B:01A3
219D  8D BE 62 FE     lea di, [bp - 0x19e]
21A1  16              push ss
21A2  57              push di
21A3  8B 46 FC        mov ax, word ptr [bp - 4]
21A6  8B C8           mov cx, ax
21A8  8A 46 F3        mov al, byte ptr [bp - 0xd]
21AB  98              cwde
21AC  BA 03 00        mov dx, 3
21AF  F7 E2           mul dx
21B1  C4 BE 62 FF     les di, ptr [bp - 0x9e]
21B5  03 F8           add di, ax
21B7  03 F9           add di, cx
21B9  26 8A 85 AD 00  mov al, byte ptr es:[di + 0xad]
21BE  30 E4           xor ah, ah
21C0  31 D2           xor dx, dx
21C2  52              push dx
21C3  50              push ax
21C4  9A DA 09 4B 21  call far 214B:09DA
21C9  B0 04           mov al, 4
21CB  50              push ax
21CC  8A 46 FA        mov al, byte ptr [bp - 6]
21CF  50              push ax
21D0  BF 6E A9        mov di, 0xa96e
21D3  1E              push ds
21D4  57              push di
21D5  9A A3 01 4B 21  call far 214B:01A3
21DA  8D BE 62 FE     lea di, [bp - 0x19e]
21DE  16              push ss
21DF  57              push di
21E0  8B 46 FC        mov ax, word ptr [bp - 4]
21E3  8B C8           mov cx, ax
21E5  8A 46 F3        mov al, byte ptr [bp - 0xd]
21E8  98              cwde
21E9  BA 03 00        mov dx, 3
21EC  F7 E2           mul dx
21EE  C4 BE 62 FF     les di, ptr [bp - 0x9e]
21F2  03 F8           add di, ax
21F4  03 F9           add di, cx
21F6  26 8A 85 B3 00  mov al, byte ptr es:[di + 0xb3]
21FB  30 E4           xor ah, ah
21FD  31 D2           xor dx, dx
21FF  52              push dx
2200  50              push ax
2201  9A DA 09 4B 21  call far 214B:09DA
2206  B0 05           mov al, 5
2208  50              push ax
2209  8A 46 FA        mov al, byte ptr [bp - 6]
220C  50              push ax
220D  BF 6E A9        mov di, 0xa96e
2210  1E              push ds
2211  57              push di
2212  9A A3 01 4B 21  call far 214B:01A3
2217  8D BE 62 FE     lea di, [bp - 0x19e]
221B  16              push ss
221C  57              push di
221D  8B 46 FC        mov ax, word ptr [bp - 4]
2220  8B C8           mov cx, ax
2222  8A 46 F3        mov al, byte ptr [bp - 0xd]
2225  98              cwde
2226  BA 03 00        mov dx, 3
2229  F7 E2           mul dx
222B  C4 BE 62 FF     les di, ptr [bp - 0x9e]
222F  03 F8           add di, ax
2231  03 F9           add di, cx
2233  26 8A 85 B9 00  mov al, byte ptr es:[di + 0xb9]
2238  30 E4           xor ah, ah
223A  31 D2           xor dx, dx
223C  52              push dx
223D  50              push ax
223E  9A DA 09 4B 21  call far 214B:09DA
2243  B0 06           mov al, 6
2245  50              push ax
2246  8A 46 FA        mov al, byte ptr [bp - 6]
2249  50              push ax
224A  BF 6E A9        mov di, 0xa96e
224D  1E              push ds
224E  57              push di
224F  9A A3 01 4B 21  call far 214B:01A3
2254  83 7E FC 02     cmp word ptr [bp - 4], 2
2258  74 03           je 0x225d
225A  E9 E4 FE        jmp 0x2141
loc_225D:
225D  80 7E F3 01     cmp byte ptr [bp - 0xd], 1
2261  74 03           je 0x2266
2263  E9 D1 FE        jmp 0x2137
loc_2266:
2266  C6 06 B2 AA 07  mov byte ptr [0xaab2], 7
226B  FF 76 04        push word ptr [bp + 4]
226E  0E              push cs
226F  E8 05 E9        call 0xb77
2272  08 C0           or al, al
2274  74 12           je 0x2288
2276  C4 BE 62 FF     les di, ptr [bp - 0x9e]
227A  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
227E  30 E4           xor ah, ah
2280  2D 80 00        sub ax, 0x80
2283  89 46 F4        mov word ptr [bp - 0xc], ax
2286  EB 05           jmp 0x228d
loc_2288:
2288  C7 46 F4 01 00  mov word ptr [bp - 0xc], 1
loc_228D:
228D  8B 46 F4        mov ax, word ptr [bp - 0xc]
2290  BA 8C 00        mov dx, 0x8c
2293  F7 E2           mul dx
2295  C4 3E 3B A9     les di, ptr [0xa93b]
2299  03 F8           add di, ax
229B  81 C7 74 FF     add di, 0xff74
229F  06              push es
22A0  57              push di
22A1  8D BE 66 FF     lea di, [bp - 0x9a]
22A5  16              push ss
22A6  57              push di
22A7  B8 8C 00        mov ax, 0x8c
22AA  50              push ax
22AB  9A 3C 00 4B 21  call far 214B:003C
22B0  FF 76 04        push word ptr [bp + 4]
22B3  0E              push cs
22B4  E8 C0 E8        call 0xb77
22B7  08 C0           or al, al
22B9  75 20           jne 0x22db
22BB  8B 46 F4        mov ax, word ptr [bp - 0xc]
22BE  BA 8C 00        mov dx, 0x8c
22C1  F7 E2           mul dx
22C3  C4 3E 3B A9     les di, ptr [0xa93b]
22C7  03 F8           add di, ax
22C9  81 C7 74 FF     add di, 0xff74
22CD  06              push es
22CE  57              push di
22CF  B8 8C 00        mov ax, 0x8c
22D2  50              push ax
22D3  31 C0           xor ax, ax
22D5  50              push ax
22D6  9A 18 00 4B 21  call far 214B:0018
loc_22DB:
22DB  C7 46 FC 01 00  mov word ptr [bp - 4], 1
22E0  EB 03           jmp 0x22e5
loc_22E2:
22E2  FF 46 FC        inc word ptr [bp - 4]
loc_22E5:
22E5  8B 46 FC        mov ax, word ptr [bp - 4]
22E8  D1 E0           shl ax, 1
22EA  C4 BE 62 FF     les di, ptr [bp - 0x9e]
22EE  03 F8           add di, ax
22F0  26 FF 75 FE     push word ptr es:[di - 2]
22F4  FF 76 F4        push word ptr [bp - 0xc]
22F7  B0 01           mov al, 1
22F9  50              push ax
22FA  0E              push cs
22FB  E8 30 F8        call 0x1b2e
22FE  83 7E FC 14     cmp word ptr [bp - 4], 0x14
2302  75 DE           jne 0x22e2
2304  FF 76 04        push word ptr [bp + 4]
2307  0E              push cs
2308  E8 6C E8        call 0xb77
230B  08 C0           or al, al
230D  74 48           je 0x2357
230F  8B 7E F4        mov di, word ptr [bp - 0xc]
2312  D1 E7           shl di, 1
2314  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
2318  05 4F 00        add ax, 0x4f
231B  89 86 60 FF     mov word ptr [bp - 0xa0], ax
231F  8B 7E F4        mov di, word ptr [bp - 0xc]
2322  D1 E7           shl di, 1
2324  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
2328  3B 86 60 FF     cmp ax, word ptr [bp - 0xa0]
232C  77 29           ja 0x2357
232E  89 46 FC        mov word ptr [bp - 4], ax
2331  EB 03           jmp 0x2336
loc_2333:
2333  FF 46 FC        inc word ptr [bp - 4]
loc_2336:
2336  8B 46 FC        mov ax, word ptr [bp - 4]
2339  D1 E0           shl ax, 1
233B  C4 3E 27 A9     les di, ptr [0xa927]
233F  03 F8           add di, ax
2341  26 FF 35        push word ptr es:[di]
2344  FF 76 F4        push word ptr [bp - 0xc]
2347  B0 01           mov al, 1
2349  50              push ax
234A  0E              push cs
234B  E8 E0 F7        call 0x1b2e
234E  8B 46 FC        mov ax, word ptr [bp - 4]
2351  3B 86 60 FF     cmp ax, word ptr [bp - 0xa0]
2355  75 DC           jne 0x2333
loc_2357:
2357  C7 46 FC 01 00  mov word ptr [bp - 4], 1
235C  EB 03           jmp 0x2361
loc_235E:
235E  FF 46 FC        inc word ptr [bp - 4]
loc_2361:
2361  8B 46 FC        mov ax, word ptr [bp - 4]
2364  BA 0E 00        mov dx, 0xe
2367  F7 E2           mul dx
2369  8B C8           mov cx, ax
236B  8B 46 F4        mov ax, word ptr [bp - 0xc]
236E  BA 8C 00        mov dx, 0x8c
2371  F7 E2           mul dx
2373  C4 3E 3B A9     les di, ptr [0xa93b]
2377  03 F8           add di, ax
2379  03 F9           add di, cx
237B  81 C7 66 FF     add di, 0xff66
237F  89 BE 5E FF     mov word ptr [bp - 0xa2], di
2383  8C 86 60 FF     mov word ptr [bp - 0xa0], es
2387  C4 BE 5E FF     les di, ptr [bp - 0xa2]
238B  26 83 7D 0C 00  cmp word ptr es:[di + 0xc], 0
2390  76 6B           jbe 0x23fd
2392  8D BE 5E FE     lea di, [bp - 0x1a2]
2396  16              push ss
2397  57              push di
2398  C4 BE 5E FF     les di, ptr [bp - 0xa2]
239C  26 8A 05        mov al, byte ptr es:[di]
239F  50              push ax
23A0  9A 5A 07 E4 23  call far 23E4:075A
23A5  BF 5A 1D        mov di, 0x1d5a
23A8  0E              push cs
23A9  57              push di
23AA  9A B7 06 E4 23  call far 23E4:06B7
23AF  C4 BE 5E FF     les di, ptr [bp - 0xa2]
23B3  81 C7 01 00     add di, 1
23B7  06              push es
23B8  57              push di
23B9  9A B7 06 E4 23  call far 23E4:06B7
23BE  8B 46 FC        mov ax, word ptr [bp - 4]
23C1  05 08 00        add ax, 8
23C4  50              push ax
23C5  B0 29           mov al, 0x29
23C7  50              push ax
23C8  BF 6E A9        mov di, 0xa96e
23CB  1E              push ds
23CC  57              push di
23CD  9A 6D 02 4B 21  call far 214B:026D
23D2  8D BE 5E FE     lea di, [bp - 0x1a2]
23D6  16              push ss
23D7  57              push di
23D8  C4 BE 5E FF     les di, ptr [bp - 0xa2]
23DC  26 8B 45 0C     mov ax, word ptr es:[di + 0xc]
23E0  31 D2           xor dx, dx
23E2  52              push dx
23E3  50              push ax
23E4  9A DA 09 4B 21  call far 214B:09DA
23E9  8B 46 FC        mov ax, word ptr [bp - 4]
23EC  05 08 00        add ax, 8
23EF  50              push ax
23F0  B0 3B           mov al, 0x3b
23F2  50              push ax
23F3  BF 6E A9        mov di, 0xa96e
23F6  1E              push ds
23F7  57              push di
23F8  9A A3 01 4B 21  call far 214B:01A3
loc_23FD:
23FD  83 7E FC 0A     cmp word ptr [bp - 4], 0xa
2401  74 03           je 0x2406
2403  E9 58 FF        jmp 0x235e
loc_2406:
2406  C6 06 B2 AA 05  mov byte ptr [0xaab2], 5
240B  8D BE 66 FF     lea di, [bp - 0x9a]
240F  16              push ss
2410  57              push di
2411  8B 46 F4        mov ax, word ptr [bp - 0xc]
2414  BA 8C 00        mov dx, 0x8c
2417  F7 E2           mul dx
2419  C4 3E 3B A9     les di, ptr [0xa93b]
241D  03 F8           add di, ax
241F  81 C7 74 FF     add di, 0xff74
2423  06              push es
2424  57              push di
2425  B8 8C 00        mov ax, 0x8c
2428  50              push ax
2429  9A 3C 00 4B 21  call far 214B:003C
242E  8B 46 F4        mov ax, word ptr [bp - 0xc]
2431  BA 8C 00        mov dx, 0x8c
2434  F7 E2           mul dx
2436  C4 3E 37 A9     les di, ptr [0xa937]
243A  03 F8           add di, ax
243C  81 C7 74 FF     add di, 0xff74
2440  06              push es
2441  57              push di
2442  8D BE 66 FF     lea di, [bp - 0x9a]
2446  16              push ss
2447  57              push di
2448  B8 8C 00        mov ax, 0x8c
244B  50              push ax
244C  9A 3C 00 4B 21  call far 214B:003C
2451  FF 76 04        push word ptr [bp + 4]
2454  0E              push cs
2455  E8 1F E7        call 0xb77
2458  08 C0           or al, al
245A  75 20           jne 0x247c
245C  8B 46 F4        mov ax, word ptr [bp - 0xc]
245F  BA 8C 00        mov dx, 0x8c
2462  F7 E2           mul dx
2464  C4 3E 37 A9     les di, ptr [0xa937]
2468  03 F8           add di, ax
246A  81 C7 74 FF     add di, 0xff74
246E  06              push es
246F  57              push di
2470  B8 8C 00        mov ax, 0x8c
2473  50              push ax
2474  31 C0           xor ax, ax
2476  50              push ax
2477  9A 18 00 4B 21  call far 214B:0018
loc_247C:
247C  C7 46 FC 01 00  mov word ptr [bp - 4], 1
2481  EB 03           jmp 0x2486
loc_2483:
2483  FF 46 FC        inc word ptr [bp - 4]
loc_2486:
2486  8B 46 FC        mov ax, word ptr [bp - 4]
2489  D1 E0           shl ax, 1
248B  C4 BE 62 FF     les di, ptr [bp - 0x9e]
248F  03 F8           add di, ax
2491  26 FF 75 FE     push word ptr es:[di - 2]
2495  FF 76 F4        push word ptr [bp - 0xc]
2498  B0 00           mov al, 0
249A  50              push ax
249B  0E              push cs
249C  E8 8F F6        call 0x1b2e
249F  83 7E FC 14     cmp word ptr [bp - 4], 0x14
24A3  75 DE           jne 0x2483
24A5  FF 76 04        push word ptr [bp + 4]
24A8  0E              push cs
24A9  E8 CB E6        call 0xb77
24AC  08 C0           or al, al
24AE  74 48           je 0x24f8
24B0  8B 7E F4        mov di, word ptr [bp - 0xc]
24B3  D1 E7           shl di, 1
24B5  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
24B9  05 4F 00        add ax, 0x4f
24BC  89 86 60 FF     mov word ptr [bp - 0xa0], ax
24C0  8B 7E F4        mov di, word ptr [bp - 0xc]
24C3  D1 E7           shl di, 1
24C5  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
24C9  3B 86 60 FF     cmp ax, word ptr [bp - 0xa0]
24CD  77 29           ja 0x24f8
24CF  89 46 FC        mov word ptr [bp - 4], ax
24D2  EB 03           jmp 0x24d7
loc_24D4:
24D4  FF 46 FC        inc word ptr [bp - 4]
loc_24D7:
24D7  8B 46 FC        mov ax, word ptr [bp - 4]
24DA  D1 E0           shl ax, 1
24DC  C4 3E 27 A9     les di, ptr [0xa927]
24E0  03 F8           add di, ax
24E2  26 FF 35        push word ptr es:[di]
24E5  FF 76 F4        push word ptr [bp - 0xc]
24E8  B0 00           mov al, 0
24EA  50              push ax
24EB  0E              push cs
24EC  E8 3F F6        call 0x1b2e
24EF  8B 46 FC        mov ax, word ptr [bp - 4]
24F2  3B 86 60 FF     cmp ax, word ptr [bp - 0xa0]
24F6  75 DC           jne 0x24d4
loc_24F8:
24F8  C7 46 FC 01 00  mov word ptr [bp - 4], 1
24FD  EB 03           jmp 0x2502
loc_24FF:
24FF  FF 46 FC        inc word ptr [bp - 4]
loc_2502:
2502  8B 46 FC        mov ax, word ptr [bp - 4]
2505  BA 0E 00        mov dx, 0xe
2508  F7 E2           mul dx
250A  8B C8           mov cx, ax
250C  8B 46 F4        mov ax, word ptr [bp - 0xc]
250F  BA 8C 00        mov dx, 0x8c
2512  F7 E2           mul dx
2514  C4 3E 37 A9     les di, ptr [0xa937]
2518  03 F8           add di, ax
251A  03 F9           add di, cx
251C  81 C7 66 FF     add di, 0xff66
2520  89 BE 5E FF     mov word ptr [bp - 0xa2], di
2524  8C 86 60 FF     mov word ptr [bp - 0xa0], es
2528  C4 BE 5E FF     les di, ptr [bp - 0xa2]
252C  26 83 7D 0C 00  cmp word ptr es:[di + 0xc], 0
2531  76 6B           jbe 0x259e
2533  8D BE 5E FE     lea di, [bp - 0x1a2]
2537  16              push ss
2538  57              push di
2539  C4 BE 5E FF     les di, ptr [bp - 0xa2]
253D  26 8A 05        mov al, byte ptr es:[di]
2540  50              push ax
2541  9A 5A 07 E4 23  call far 23E4:075A
2546  BF 5A 1D        mov di, 0x1d5a
2549  0E              push cs
254A  57              push di
254B  9A B7 06 E4 23  call far 23E4:06B7
2550  C4 BE 5E FF     les di, ptr [bp - 0xa2]
2554  81 C7 01 00     add di, 1
2558  06              push es
2559  57              push di
255A  9A B7 06 E4 23  call far 23E4:06B7
255F  8B 46 FC        mov ax, word ptr [bp - 4]
2562  05 08 00        add ax, 8
2565  50              push ax
2566  B0 3D           mov al, 0x3d
2568  50              push ax
2569  BF 6E A9        mov di, 0xa96e
256C  1E              push ds
256D  57              push di
256E  9A 6D 02 4B 21  call far 214B:026D
2573  8D BE 5E FE     lea di, [bp - 0x1a2]
2577  16              push ss
2578  57              push di
2579  C4 BE 5E FF     les di, ptr [bp - 0xa2]
257D  26 8B 45 0C     mov ax, word ptr es:[di + 0xc]
2581  31 D2           xor dx, dx
2583  52              push dx
2584  50              push ax
2585  9A DA 09 4B 21  call far 214B:09DA
258A  8B 46 FC        mov ax, word ptr [bp - 4]
258D  05 08 00        add ax, 8
2590  50              push ax
2591  B0 4F           mov al, 0x4f
2593  50              push ax
2594  BF 6E A9        mov di, 0xa96e
2597  1E              push ds
2598  57              push di
2599  9A A3 01 4B 21  call far 214B:01A3
loc_259E:
259E  83 7E FC 0A     cmp word ptr [bp - 4], 0xa
25A2  74 03           je 0x25a7
25A4  E9 58 FF        jmp 0x24ff
loc_25A7:
25A7  8D BE 66 FF     lea di, [bp - 0x9a]
25AB  16              push ss
25AC  57              push di
25AD  8B 46 F4        mov ax, word ptr [bp - 0xc]
25B0  BA 8C 00        mov dx, 0x8c
25B3  F7 E2           mul dx
25B5  C4 3E 37 A9     les di, ptr [0xa937]
25B9  03 F8           add di, ax
25BB  81 C7 74 FF     add di, 0xff74
25BF  06              push es
25C0  57              push di
25C1  B8 8C 00        mov ax, 0x8c
25C4  50              push ax
25C5  9A 3C 00 4B 21  call far 214B:003C
25CA  C4 3E 6E A9     les di, ptr [0xa96e]
25CE  06              push es
25CF  57              push di
25D0  C4 3E 6A A9     les di, ptr [0xa96a]
25D4  06              push es
25D5  57              push di
25D6  B8 A0 0F        mov ax, 0xfa0
25D9  50              push ax
25DA  9A 5D 02 E4 23  call far 23E4:025D
25DF  9A DD 08 4B 21  call far 214B:08DD
25E4  89 EC           mov sp, bp
25E6  5D              pop bp
25E7  C2 02 00        ret 2

