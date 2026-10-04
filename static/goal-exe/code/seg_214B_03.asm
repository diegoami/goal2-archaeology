; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 214B (image offsets 214B0..235BF), part 3 of 4
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 214B:136B  (found by: prologue)
sub_136B:
136B  55              push bp
136C  89 E5           mov bp, sp
136E  81 EC 00 01     sub sp, 0x100
1372  8D BE 00 FF     lea di, [bp - 0x100]
1376  16              push ss
1377  57              push di
1378  B8 01 00        mov ax, 1
137B  50              push ax
137C  9A 2A 19 E4 23  call far 23E4:192A
1381  BF 66 13        mov di, 0x1366
1384  0E              push cs
1385  57              push di
1386  9A 2F 07 E4 23  call far 23E4:072F
138B  75 02           jne 0x138f
138D  EB 32           jmp 0x13c1
loc_138F:
138F  0E              push cs
1390  E8 48 F2        call 0x5db
1393  BF 26 7A        mov di, 0x7a26
1396  1E              push ds
1397  57              push di
1398  BF 6E A9        mov di, 0xa96e
139B  1E              push ds
139C  57              push di
139D  0E              push cs
139E  E8 88 EF        call 0x329
13A1  B0 01           mov al, 1
13A3  50              push ax
13A4  B0 19           mov al, 0x19
13A6  50              push ax
13A7  9A 15 02 82 23  call far 2382:0215
13AC  C4 3E 6E A9     les di, ptr [0xa96e]
13B0  06              push es
13B1  57              push di
13B2  C4 3E 6A A9     les di, ptr [0xa96a]
13B6  06              push es
13B7  57              push di
13B8  B8 A0 0F        mov ax, 0xfa0
13BB  50              push ax
13BC  9A 5D 02 E4 23  call far 23E4:025D
loc_13C1:
13C1  89 EC           mov sp, bp
13C3  5D              pop bp
13C4  CB              retf

; ---- routine 214B:13C5  (found by: far)
sub_13C5:
13C5  55              push bp
13C6  89 E5           mov bp, sp
13C8  8B 46 08        mov ax, word ptr [bp + 8]
13CB  D1 E0           shl ax, 1
13CD  8B C8           mov cx, ax
13CF  8B 46 0A        mov ax, word ptr [bp + 0xa]
13D2  BA A0 00        mov dx, 0xa0
13D5  F7 E2           mul dx
13D7  C4 3E 6E A9     les di, ptr [0xa96e]
13DB  03 F8           add di, ax
13DD  03 F9           add di, cx
13DF  81 C7 5E FF     add di, 0xff5e
13E3  06              push es
13E4  57              push di
13E5  B8 70 00        mov ax, 0x70
13E8  50              push ax
13E9  FF 76 06        push word ptr [bp + 6]
13EC  0E              push cs
13ED  E8 EB EC        call 0xdb
13F0  89 EC           mov sp, bp
13F2  5D              pop bp
13F3  CA 06 00        retf 6

; ---- routine 214B:13F6  (found by: call)
sub_13F6:
13F6  55              push bp
13F7  89 E5           mov bp, sp
13F9  A0 76 A9        mov al, byte ptr [0xa976]
13FC  3C AD           cmp al, 0xad
13FE  74 04           je 0x1404
1400  3C AB           cmp al, 0xab
1402  75 09           jne 0x140d
loc_1404:
1404  C4 7E 08        les di, ptr [bp + 8]
1407  26 C6 05 01     mov byte ptr es:[di], 1
140B  EB 3F           jmp 0x144c
loc_140D:
140D  3C B2           cmp al, 0xb2
140F  74 04           je 0x1415
1411  3C B0           cmp al, 0xb0
1413  75 0B           jne 0x1420
loc_1415:
1415  8A 46 06        mov al, byte ptr [bp + 6]
1418  C4 7E 08        les di, ptr [bp + 8]
141B  26 88 05        mov byte ptr es:[di], al
141E  EB 2C           jmp 0x144c
loc_1420:
1420  3C AC           cmp al, 0xac
1422  75 11           jne 0x1435
1424  C4 7E 08        les di, ptr [bp + 8]
1427  26 80 3D 01     cmp byte ptr es:[di], 1
142B  76 06           jbe 0x1433
142D  C4 7E 08        les di, ptr [bp + 8]
1430  26 FE 0D        dec byte ptr es:[di]
loc_1433:
1433  EB 17           jmp 0x144c
loc_1435:
1435  3C B1           cmp al, 0xb1
1437  75 13           jne 0x144c
1439  C4 7E 08        les di, ptr [bp + 8]
143C  26 8A 05        mov al, byte ptr es:[di]
143F  30 E4           xor ah, ah
1441  3B 46 06        cmp ax, word ptr [bp + 6]
1444  73 06           jae 0x144c
1446  C4 7E 08        les di, ptr [bp + 8]
1449  26 FE 05        inc byte ptr es:[di]
loc_144C:
144C  89 EC           mov sp, bp
144E  5D              pop bp
144F  CA 06 00        retf 6

; ---- routine 214B:1452  (found by: far)
sub_1452:
1452  55              push bp
1453  89 E5           mov bp, sp
1455  A0 76 A9        mov al, byte ptr [0xa976]
1458  3C AC           cmp al, 0xac
145A  75 1C           jne 0x1478
145C  C4 7E 08        les di, ptr [bp + 8]
145F  26 80 3D 01     cmp byte ptr es:[di], 1
1463  76 08           jbe 0x146d
1465  C4 7E 08        les di, ptr [bp + 8]
1468  26 FE 0D        dec byte ptr es:[di]
146B  EB 09           jmp 0x1476
loc_146D:
146D  8A 46 06        mov al, byte ptr [bp + 6]
1470  C4 7E 08        les di, ptr [bp + 8]
1473  26 88 05        mov byte ptr es:[di], al
loc_1476:
1476  EB 2E           jmp 0x14a6
loc_1478:
1478  3C B1           cmp al, 0xb1
147A  75 1E           jne 0x149a
147C  C4 7E 08        les di, ptr [bp + 8]
147F  26 8A 05        mov al, byte ptr es:[di]
1482  30 E4           xor ah, ah
1484  3B 46 06        cmp ax, word ptr [bp + 6]
1487  73 08           jae 0x1491
1489  C4 7E 08        les di, ptr [bp + 8]
148C  26 FE 05        inc byte ptr es:[di]
148F  EB 07           jmp 0x1498
loc_1491:
1491  C4 7E 08        les di, ptr [bp + 8]
1494  26 C6 05 01     mov byte ptr es:[di], 1
loc_1498:
1498  EB 0C           jmp 0x14a6
loc_149A:
149A  C4 7E 08        les di, ptr [bp + 8]
149D  06              push es
149E  57              push di
149F  FF 76 06        push word ptr [bp + 6]
14A2  0E              push cs
14A3  E8 50 FF        call 0x13f6
loc_14A6:
14A6  89 EC           mov sp, bp
14A8  5D              pop bp
14A9  CA 06 00        retf 6

; ---- routine 214B:14AC  (found by: call)
sub_14AC:
14AC  55              push bp
14AD  89 E5           mov bp, sp
14AF  A0 76 A9        mov al, byte ptr [0xa976]
14B2  3C AD           cmp al, 0xad
14B4  74 04           je 0x14ba
14B6  3C AB           cmp al, 0xab
14B8  75 0A           jne 0x14c4
loc_14BA:
14BA  C4 7E 08        les di, ptr [bp + 8]
14BD  26 C7 05 01 00  mov word ptr es:[di], 1
14C2  EB 3D           jmp 0x1501
loc_14C4:
14C4  3C B2           cmp al, 0xb2
14C6  74 04           je 0x14cc
14C8  3C B0           cmp al, 0xb0
14CA  75 0B           jne 0x14d7
loc_14CC:
14CC  8B 46 06        mov ax, word ptr [bp + 6]
14CF  C4 7E 08        les di, ptr [bp + 8]
14D2  26 89 05        mov word ptr es:[di], ax
14D5  EB 2A           jmp 0x1501
loc_14D7:
14D7  3C AC           cmp al, 0xac
14D9  75 11           jne 0x14ec
14DB  C4 7E 08        les di, ptr [bp + 8]
14DE  26 83 3D 01     cmp word ptr es:[di], 1
14E2  76 06           jbe 0x14ea
14E4  C4 7E 08        les di, ptr [bp + 8]
14E7  26 FF 0D        dec word ptr es:[di]
loc_14EA:
14EA  EB 15           jmp 0x1501
loc_14EC:
14EC  3C B1           cmp al, 0xb1
14EE  75 11           jne 0x1501
14F0  C4 7E 08        les di, ptr [bp + 8]
14F3  26 8B 05        mov ax, word ptr es:[di]
14F6  3B 46 06        cmp ax, word ptr [bp + 6]
14F9  73 06           jae 0x1501
14FB  C4 7E 08        les di, ptr [bp + 8]
14FE  26 FF 05        inc word ptr es:[di]
loc_1501:
1501  89 EC           mov sp, bp
1503  5D              pop bp
1504  CA 06 00        retf 6

; ---- routine 214B:1507  (found by: call, far)
sub_1507:
1507  55              push bp
1508  89 E5           mov bp, sp
150A  A0 76 A9        mov al, byte ptr [0xa976]
150D  3C AC           cmp al, 0xac
150F  75 1C           jne 0x152d
1511  C4 7E 08        les di, ptr [bp + 8]
1514  26 83 3D 01     cmp word ptr es:[di], 1
1518  76 08           jbe 0x1522
151A  C4 7E 08        les di, ptr [bp + 8]
151D  26 FF 0D        dec word ptr es:[di]
1520  EB 09           jmp 0x152b
loc_1522:
1522  8B 46 06        mov ax, word ptr [bp + 6]
1525  C4 7E 08        les di, ptr [bp + 8]
1528  26 89 05        mov word ptr es:[di], ax
loc_152B:
152B  EB 2D           jmp 0x155a
loc_152D:
152D  3C B1           cmp al, 0xb1
152F  75 1D           jne 0x154e
1531  C4 7E 08        les di, ptr [bp + 8]
1534  26 8B 05        mov ax, word ptr es:[di]
1537  3B 46 06        cmp ax, word ptr [bp + 6]
153A  73 08           jae 0x1544
153C  C4 7E 08        les di, ptr [bp + 8]
153F  26 FF 05        inc word ptr es:[di]
1542  EB 08           jmp 0x154c
loc_1544:
1544  C4 7E 08        les di, ptr [bp + 8]
1547  26 C7 05 01 00  mov word ptr es:[di], 1
loc_154C:
154C  EB 0C           jmp 0x155a
loc_154E:
154E  C4 7E 08        les di, ptr [bp + 8]
1551  06              push es
1552  57              push di
1553  FF 76 06        push word ptr [bp + 6]
1556  0E              push cs
1557  E8 52 FF        call 0x14ac
loc_155A:
155A  89 EC           mov sp, bp
155C  5D              pop bp
155D  CA 06 00        retf 6

; ---- routine 214B:1560  (found by: far)
sub_1560:
1560  55              push bp
1561  89 E5           mov bp, sp
1563  C4 3E 6E A9     les di, ptr [0xa96e]
1567  06              push es
1568  57              push di
1569  C4 3E 6A A9     les di, ptr [0xa96a]
156D  06              push es
156E  57              push di
156F  B8 A0 0F        mov ax, 0xfa0
1572  50              push ax
1573  9A 5D 02 E4 23  call far 23E4:025D
1578  0E              push cs
1579  E8 61 F3        call 0x8dd
157C  C4 7E 08        les di, ptr [bp + 8]
157F  06              push es
1580  57              push di
1581  FF 76 06        push word ptr [bp + 6]
1584  0E              push cs
1585  E8 7F FF        call 0x1507
1588  89 EC           mov sp, bp
158A  5D              pop bp
158B  CA 06 00        retf 6

; ---- routine 214B:158E  (found by: call)
sub_158E:
158E  55              push bp
158F  89 E5           mov bp, sp
1591  8B 46 08        mov ax, word ptr [bp + 8]
1594  8B 7E 04        mov di, word ptr [bp + 4]
1597  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
159B  26 89 05        mov word ptr es:[di], ax
159E  8B 46 06        mov ax, word ptr [bp + 6]
15A1  8B 7E 04        mov di, word ptr [bp + 4]
15A4  36 C4 7D 0A     les di, ptr ss:[di + 0xa]
15A8  26 89 05        mov word ptr es:[di], ax
15AB  89 EC           mov sp, bp
15AD  5D              pop bp
15AE  C2 06 00        ret 6

; ---- routine 214B:15B1  (found by: far)
sub_15B1:
15B1  55              push bp
15B2  89 E5           mov bp, sp
15B4  83 EC 02        sub sp, 2
15B7  C4 7E 0A        les di, ptr [bp + 0xa]
15BA  26 8B 05        mov ax, word ptr es:[di]
15BD  C4 7E 0E        les di, ptr [bp + 0xe]
15C0  26 03 05        add ax, word ptr es:[di]
15C3  48              dec ax
15C4  89 46 FE        mov word ptr [bp - 2], ax
15C7  A0 76 A9        mov al, byte ptr [0xa976]
15CA  3C B1           cmp al, 0xb1
15CC  75 3C           jne 0x160a
15CE  8B 46 FE        mov ax, word ptr [bp - 2]
15D1  3B 46 06        cmp ax, word ptr [bp + 6]
15D4  73 31           jae 0x1607
15D6  C4 7E 0E        les di, ptr [bp + 0xe]
15D9  26 8B 05        mov ax, word ptr es:[di]
15DC  3B 46 08        cmp ax, word ptr [bp + 8]
15DF  75 14           jne 0x15f5
15E1  C4 7E 0E        les di, ptr [bp + 0xe]
15E4  26 FF 35        push word ptr es:[di]
15E7  C4 7E 0A        les di, ptr [bp + 0xa]
15EA  26 8B 05        mov ax, word ptr es:[di]
15ED  40              inc ax
15EE  50              push ax
15EF  55              push bp
15F0  E8 9B FF        call 0x158e
15F3  EB 12           jmp 0x1607
loc_15F5:
15F5  C4 7E 0E        les di, ptr [bp + 0xe]
15F8  26 8B 05        mov ax, word ptr es:[di]
15FB  40              inc ax
15FC  50              push ax
15FD  C4 7E 0A        les di, ptr [bp + 0xa]
1600  26 FF 35        push word ptr es:[di]
1603  55              push bp
1604  E8 87 FF        call 0x158e
loc_1607:
1607  E9 55 01        jmp 0x175f
loc_160A:
160A  3C AC           cmp al, 0xac
160C  75 38           jne 0x1646
160E  83 7E FE 01     cmp word ptr [bp - 2], 1
1612  76 2F           jbe 0x1643
1614  C4 7E 0E        les di, ptr [bp + 0xe]
1617  26 83 3D 01     cmp word ptr es:[di], 1
161B  75 14           jne 0x1631
161D  C4 7E 0E        les di, ptr [bp + 0xe]
1620  26 FF 35        push word ptr es:[di]
1623  C4 7E 0A        les di, ptr [bp + 0xa]
1626  26 8B 05        mov ax, word ptr es:[di]
1629  48              dec ax
162A  50              push ax
162B  55              push bp
162C  E8 5F FF        call 0x158e
162F  EB 12           jmp 0x1643
loc_1631:
1631  C4 7E 0E        les di, ptr [bp + 0xe]
1634  26 8B 05        mov ax, word ptr es:[di]
1637  48              dec ax
1638  50              push ax
1639  C4 7E 0A        les di, ptr [bp + 0xa]
163C  26 FF 35        push word ptr es:[di]
163F  55              push bp
1640  E8 4B FF        call 0x158e
loc_1643:
1643  E9 19 01        jmp 0x175f
loc_1646:
1646  3C AD           cmp al, 0xad
1648  75 4C           jne 0x1696
164A  C4 7E 0A        les di, ptr [bp + 0xa]
164D  26 83 3D 01     cmp word ptr es:[di], 1
1651  76 32           jbe 0x1685
1653  8B 46 08        mov ax, word ptr [bp + 8]
1656  40              inc ax
1657  C4 7E 0A        les di, ptr [bp + 0xa]
165A  26 3B 05        cmp ax, word ptr es:[di]
165D  77 16           ja 0x1675
165F  C4 7E 0E        les di, ptr [bp + 0xe]
1662  26 FF 35        push word ptr es:[di]
1665  C4 7E 0A        les di, ptr [bp + 0xa]
1668  26 8B 05        mov ax, word ptr es:[di]
166B  2B 46 08        sub ax, word ptr [bp + 8]
166E  50              push ax
166F  55              push bp
1670  E8 1B FF        call 0x158e
1673  EB 0E           jmp 0x1683
loc_1675:
1675  C4 7E 0E        les di, ptr [bp + 0xe]
1678  26 FF 35        push word ptr es:[di]
167B  B8 01 00        mov ax, 1
167E  50              push ax
167F  55              push bp
1680  E8 0B FF        call 0x158e
loc_1683:
1683  EB 0E           jmp 0x1693
loc_1685:
1685  B8 01 00        mov ax, 1
1688  50              push ax
1689  C4 7E 0A        les di, ptr [bp + 0xa]
168C  26 FF 35        push word ptr es:[di]
168F  55              push bp
1690  E8 FB FE        call 0x158e
loc_1693:
1693  E9 C9 00        jmp 0x175f
loc_1696:
1696  3C B2           cmp al, 0xb2
1698  75 68           jne 0x1702
169A  C4 7E 0A        les di, ptr [bp + 0xa]
169D  26 8B 05        mov ax, word ptr es:[di]
16A0  03 46 08        add ax, word ptr [bp + 8]
16A3  48              dec ax
16A4  3B 46 06        cmp ax, word ptr [bp + 6]
16A7  73 3A           jae 0x16e3
16A9  8B 46 08        mov ax, word ptr [bp + 8]
16AC  D1 E0           shl ax, 1
16AE  C4 7E 0A        les di, ptr [bp + 0xa]
16B1  26 03 05        add ax, word ptr es:[di]
16B4  3B 46 06        cmp ax, word ptr [bp + 6]
16B7  77 16           ja 0x16cf
16B9  C4 7E 0E        les di, ptr [bp + 0xe]
16BC  26 FF 35        push word ptr es:[di]
16BF  C4 7E 0A        les di, ptr [bp + 0xa]
16C2  26 8B 05        mov ax, word ptr es:[di]
16C5  03 46 08        add ax, word ptr [bp + 8]
16C8  50              push ax
16C9  55              push bp
16CA  E8 C1 FE        call 0x158e
16CD  EB 12           jmp 0x16e1
loc_16CF:
16CF  C4 7E 0E        les di, ptr [bp + 0xe]
16D2  26 FF 35        push word ptr es:[di]
16D5  8B 46 06        mov ax, word ptr [bp + 6]
16D8  2B 46 08        sub ax, word ptr [bp + 8]
16DB  40              inc ax
16DC  50              push ax
16DD  55              push bp
16DE  E8 AD FE        call 0x158e
loc_16E1:
16E1  EB 1D           jmp 0x1700
loc_16E3:
16E3  8B 46 06        mov ax, word ptr [bp + 6]
16E6  31 D2           xor dx, dx
16E8  52              push dx
16E9  50              push ax
16EA  8B 46 08        mov ax, word ptr [bp + 8]
16ED  31 D2           xor dx, dx
16EF  52              push dx
16F0  50              push ax
16F1  0E              push cs
16F2  E8 27 F6        call 0xd1c
16F5  50              push ax
16F6  C4 7E 0A        les di, ptr [bp + 0xa]
16F9  26 FF 35        push word ptr es:[di]
16FC  55              push bp
16FD  E8 8E FE        call 0x158e
loc_1700:
1700  EB 5D           jmp 0x175f
loc_1702:
1702  3C AB           cmp al, 0xab
1704  75 0E           jne 0x1714
1706  B8 01 00        mov ax, 1
1709  50              push ax
170A  B8 01 00        mov ax, 1
170D  50              push ax
170E  55              push bp
170F  E8 7C FE        call 0x158e
1712  EB 4B           jmp 0x175f
loc_1714:
1714  3C B0           cmp al, 0xb0
1716  75 47           jne 0x175f
1718  8B 46 08        mov ax, word ptr [bp + 8]
171B  31 D2           xor dx, dx
171D  52              push dx
171E  50              push ax
171F  8B 46 06        mov ax, word ptr [bp + 6]
1722  31 D2           xor dx, dx
1724  52              push dx
1725  50              push ax
1726  0E              push cs
1727  E8 F2 F5        call 0xd1c
172A  50              push ax
172B  B8 01 00        mov ax, 1
172E  31 D2           xor dx, dx
1730  52              push dx
1731  50              push ax
1732  8B 46 06        mov ax, word ptr [bp + 6]
1735  31 D2           xor dx, dx
1737  8B C8           mov cx, ax
1739  8B DA           mov bx, dx
173B  8B 46 08        mov ax, word ptr [bp + 8]
173E  31 D2           xor dx, dx
1740  F7 D0           not ax
1742  F7 D2           not dx
1744  05 01 00        add ax, 1
1747  83 D2 00        adc dx, 0
174A  05 01 00        add ax, 1
174D  83 D2 00        adc dx, 0
1750  03 C1           add ax, cx
1752  13 D3           adc dx, bx
1754  52              push dx
1755  50              push ax
1756  0E              push cs
1757  E8 FC F5        call 0xd56
175A  50              push ax
175B  55              push bp
175C  E8 2F FE        call 0x158e
loc_175F:
175F  89 EC           mov sp, bp
1761  5D              pop bp
1762  CA 0C 00        retf 0xc

; ---- routine 214B:1765  (found by: far)
sub_1765:
1765  55              push bp
1766  89 E5           mov bp, sp
1768  83 EC 52        sub sp, 0x52
176B  C4 7E 06        les di, ptr [bp + 6]
176E  06              push es
176F  57              push di
1770  8D 7E AE        lea di, [bp - 0x52]
1773  16              push ss
1774  57              push di
1775  B8 50 00        mov ax, 0x50
1778  50              push ax
1779  9A 44 06 E4 23  call far 23E4:0644
177E  8A 46 0A        mov al, byte ptr [bp + 0xa]
1781  88 46 FF        mov byte ptr [bp - 1], al
1784  80 7E 0A 00     cmp byte ptr [bp + 0xa], 0
1788  74 09           je 0x1793
178A  8D 7E AE        lea di, [bp - 0x52]
178D  16              push ss
178E  57              push di
178F  0E              push cs
1790  E8 65 ED        call 0x4f8
loc_1793:
1793  8A 46 FF        mov al, byte ptr [bp - 1]
1796  89 EC           mov sp, bp
1798  5D              pop bp
1799  CA 06 00        retf 6

; ---- routine 214B:179C  (found by: far)
sub_179C:
179C  55              push bp
179D  89 E5           mov bp, sp
179F  BF EC 7A        mov di, 0x7aec
17A2  1E              push ds
17A3  57              push di
17A4  BF 6A A9        mov di, 0xa96a
17A7  1E              push ds
17A8  57              push di
17A9  0E              push cs
17AA  E8 7C EB        call 0x329
17AD  89 EC           mov sp, bp
17AF  5D              pop bp
17B0  CB              retf
; data (not reached as code), 184 bytes
17B1                  pstr 'Illegal file name or file not found'
17D5                  pstr 'Path not found'
17E4                  pstr 'Read only/hidden file'
17FA                  pstr 'No such drive'
1808                  pstr 'Disk is full'
1815                  pstr 'No disk in drive'
1826                  pstr 'Bad disk sector'
1836                  pstr 'Incompatible file'
1848                  pstr 'File handling error'
185C                  pstr ' - try again'

; ---- routine 214B:1869  (found by: far)
sub_1869:
1869  55              push bp
186A  89 E5           mov bp, sp
186C  81 EC 52 01     sub sp, 0x152
1870  C6 46 FF 00     mov byte ptr [bp - 1], 0
1874  83 3E 65 A9 00  cmp word ptr [0xa965], 0
1879  75 03           jne 0x187e
187B  E9 2C 01        jmp 0x19aa
loc_187E:
187E  A1 65 A9        mov ax, word ptr [0xa965]
1881  3D 02 00        cmp ax, 2
1884  75 16           jne 0x189c
1886  BF B1 17        mov di, 0x17b1
1889  0E              push cs
188A  57              push di
188B  8D 7E AE        lea di, [bp - 0x52]
188E  16              push ss
188F  57              push di
1890  B8 50 00        mov ax, 0x50
1893  50              push ax
1894  9A 44 06 E4 23  call far 23E4:0644
1899  E9 CB 00        jmp 0x1967
loc_189C:
189C  3D 03 00        cmp ax, 3
189F  75 16           jne 0x18b7
18A1  BF D5 17        mov di, 0x17d5
18A4  0E              push cs
18A5  57              push di
18A6  8D 7E AE        lea di, [bp - 0x52]
18A9  16              push ss
18AA  57              push di
18AB  B8 50 00        mov ax, 0x50
18AE  50              push ax
18AF  9A 44 06 E4 23  call far 23E4:0644
18B4  E9 B0 00        jmp 0x1967
loc_18B7:
18B7  3D 0C 00        cmp ax, 0xc
18BA  75 16           jne 0x18d2
18BC  BF E4 17        mov di, 0x17e4
18BF  0E              push cs
18C0  57              push di
18C1  8D 7E AE        lea di, [bp - 0x52]
18C4  16              push ss
18C5  57              push di
18C6  B8 50 00        mov ax, 0x50
18C9  50              push ax
18CA  9A 44 06 E4 23  call far 23E4:0644
18CF  E9 95 00        jmp 0x1967
loc_18D2:
18D2  3D 0F 00        cmp ax, 0xf
18D5  75 15           jne 0x18ec
18D7  BF FA 17        mov di, 0x17fa
18DA  0E              push cs
18DB  57              push di
18DC  8D 7E AE        lea di, [bp - 0x52]
18DF  16              push ss
18E0  57              push di
18E1  B8 50 00        mov ax, 0x50
18E4  50              push ax
18E5  9A 44 06 E4 23  call far 23E4:0644
18EA  EB 7B           jmp 0x1967
loc_18EC:
18EC  3D 65 00        cmp ax, 0x65
18EF  75 15           jne 0x1906
18F1  BF 08 18        mov di, 0x1808
18F4  0E              push cs
18F5  57              push di
18F6  8D 7E AE        lea di, [bp - 0x52]
18F9  16              push ss
18FA  57              push di
18FB  B8 50 00        mov ax, 0x50
18FE  50              push ax
18FF  9A 44 06 E4 23  call far 23E4:0644
1904  EB 61           jmp 0x1967
loc_1906:
1906  3D 98 00        cmp ax, 0x98
1909  75 15           jne 0x1920
190B  BF 15 18        mov di, 0x1815
190E  0E              push cs
190F  57              push di
1910  8D 7E AE        lea di, [bp - 0x52]
1913  16              push ss
1914  57              push di
1915  B8 50 00        mov ax, 0x50
1918  50              push ax
1919  9A 44 06 E4 23  call far 23E4:0644
191E  EB 47           jmp 0x1967
loc_1920:
1920  3D 9A 00        cmp ax, 0x9a
1923  75 15           jne 0x193a
1925  BF 26 18        mov di, 0x1826
1928  0E              push cs
1929  57              push di
192A  8D 7E AE        lea di, [bp - 0x52]
192D  16              push ss
192E  57              push di
192F  B8 50 00        mov ax, 0x50
1932  50              push ax
1933  9A 44 06 E4 23  call far 23E4:0644
1938  EB 2D           jmp 0x1967
loc_193A:
193A  3D FE 00        cmp ax, 0xfe
193D  75 15           jne 0x1954
193F  BF 36 18        mov di, 0x1836
1942  0E              push cs
1943  57              push di
1944  8D 7E AE        lea di, [bp - 0x52]
1947  16              push ss
1948  57              push di
1949  B8 50 00        mov ax, 0x50
194C  50              push ax
194D  9A 44 06 E4 23  call far 23E4:0644
1952  EB 13           jmp 0x1967
loc_1954:
1954  BF 48 18        mov di, 0x1848
1957  0E              push cs
1958  57              push di
1959  8D 7E AE        lea di, [bp - 0x52]
195C  16              push ss
195D  57              push di
195E  B8 50 00        mov ax, 0x50
1961  50              push ax
1962  9A 44 06 E4 23  call far 23E4:0644
loc_1967:
1967  81 3E 65 A9 FF 00 cmp word ptr [0xa965], 0xff
196D  74 28           je 0x1997
196F  8D BE AE FE     lea di, [bp - 0x152]
1973  16              push ss
1974  57              push di
1975  8D 7E AE        lea di, [bp - 0x52]
1978  16              push ss
1979  57              push di
197A  9A 2A 06 E4 23  call far 23E4:062A
197F  BF 5C 18        mov di, 0x185c
1982  0E              push cs
1983  57              push di
1984  9A B7 06 E4 23  call far 23E4:06B7
1989  0E              push cs
198A  E8 D9 EB        call 0x566
198D  08 C0           or al, al
198F  74 06           je 0x1997
1991  C6 46 FF 01     mov byte ptr [bp - 1], 1
1995  EB 13           jmp 0x19aa
loc_1997:
1997  80 7E 06 00     cmp byte ptr [bp + 6], 0
199B  74 09           je 0x19a6
199D  31 C0           xor ax, ax
199F  9A D8 00 E4 23  call far 23E4:00D8
19A4  EB 04           jmp 0x19aa
loc_19A6:
19A6  C6 46 FF 00     mov byte ptr [bp - 1], 0
loc_19AA:
19AA  8A 46 FF        mov al, byte ptr [bp - 1]
19AD  89 EC           mov sp, bp
19AF  5D              pop bp
19B0  CA 02 00        retf 2

; ---- routine 214B:19B3  (found by: call)
sub_19B3:
19B3  55              push bp
19B4  89 E5           mov bp, sp
19B6  83 EC 52        sub sp, 0x52
19B9  C4 7E 08        les di, ptr [bp + 8]
19BC  06              push es
19BD  57              push di
19BE  8D 7E AF        lea di, [bp - 0x51]
19C1  16              push ss
19C2  57              push di
19C3  B8 50 00        mov ax, 0x50
19C6  50              push ax
19C7  9A 44 06 E4 23  call far 23E4:0644
19CC  8D 7E B0        lea di, [bp - 0x50]
19CF  16              push ss
19D0  57              push di
19D1  C4 7E 04        les di, ptr [bp + 4]
19D4  06              push es
19D5  57              push di
19D6  8A 46 AF        mov al, byte ptr [bp - 0x51]
19D9  30 E4           xor ah, ah
19DB  50              push ax
19DC  0E              push cs
19DD  E8 5C E6        call 0x3c
19E0  8A 46 AF        mov al, byte ptr [bp - 0x51]
19E3  30 E4           xor ah, ah
19E5  C4 7E 04        les di, ptr [bp + 4]
19E8  03 F8           add di, ax
19EA  26 C6 05 00     mov byte ptr es:[di], 0
19EE  89 EC           mov sp, bp
19F0  5D              pop bp
19F1  C2 08 00        ret 8

; ---- routine 214B:19F4  (found by: call)
sub_19F4:
19F4  55              push bp
19F5  89 E5           mov bp, sp
19F7  83 EC 04        sub sp, 4
19FA  C4 7E 04        les di, ptr [bp + 4]
19FD  89 7E FC        mov word ptr [bp - 4], di
1A00  8C 46 FE        mov word ptr [bp - 2], es
1A03  C4 7E FC        les di, ptr [bp - 4]
1A06  26 8B 45 12     mov ax, word ptr es:[di + 0x12]
1A0A  25 01 00        and ax, 1
1A0D  3D 01 00        cmp ax, 1
1A10  75 10           jne 0x1a22
1A12  31 C0           xor ax, ax
1A14  A3 A4 AA        mov word ptr [0xaaa4], ax
1A17  C4 7E FC        les di, ptr [bp - 4]
1A1A  26 8B 05        mov ax, word ptr es:[di]
1A1D  A3 65 A9        mov word ptr [0xa965], ax
1A20  EB 0E           jmp 0x1a30
loc_1A22:
1A22  31 C0           xor ax, ax
1A24  A3 65 A9        mov word ptr [0xa965], ax
1A27  C4 7E FC        les di, ptr [bp - 4]
1A2A  26 8B 05        mov ax, word ptr es:[di]
1A2D  A3 A4 AA        mov word ptr [0xaaa4], ax
loc_1A30:
1A30  89 EC           mov sp, bp
1A32  5D              pop bp
1A33  C2 04 00        ret 4

; ---- routine 214B:1A36  (found by: far)
sub_1A36:
1A36  55              push bp
1A37  89 E5           mov bp, sp
1A39  83 EC 14        sub sp, 0x14
1A3C  83 3E A4 AA 00  cmp word ptr [0xaaa4], 0
1A41  75 02           jne 0x1a45
1A43  EB 14           jmp 0x1a59
loc_1A45:
1A45  A1 A4 AA        mov ax, word ptr [0xaaa4]
1A48  89 46 EE        mov word ptr [bp - 0x12], ax
1A4B  C6 46 ED 3E     mov byte ptr [bp - 0x13], 0x3e
1A4F  8D 7E EC        lea di, [bp - 0x14]
1A52  16              push ss
1A53  57              push di
1A54  9A 00 00 5C 23  call far 235C:0000
loc_1A59:
1A59  89 EC           mov sp, bp
1A5B  5D              pop bp
1A5C  CB              retf
; data (not reached as code), 2 bytes
1A5D                  db 01 20   ; . 

; ---- routine 214B:1A5F  (found by: call)
sub_1A5F:
1A5F  55              push bp
1A60  89 E5           mov bp, sp
1A62  81 EC B6 00     sub sp, 0xb6
1A66  C4 7E 06        les di, ptr [bp + 6]
1A69  06              push es
1A6A  57              push di
1A6B  8D 7E AF        lea di, [bp - 0x51]
1A6E  16              push ss
1A6F  57              push di
1A70  B8 50 00        mov ax, 0x50
1A73  50              push ax
1A74  9A 44 06 E4 23  call far 23E4:0644
1A79  BF 5D 1A        mov di, 0x1a5d
1A7C  0E              push cs
1A7D  57              push di
1A7E  8D 7E AF        lea di, [bp - 0x51]
1A81  16              push ss
1A82  57              push di
1A83  9A E3 06 E4 23  call far 23E4:06E3
1A88  09 C0           or ax, ax
1A8A  74 08           je 0x1a94
1A8C  C7 06 65 A9 02 00 mov word ptr [0xa965], 2
1A92  EB 37           jmp 0x1acb
loc_1A94:
1A94  8D 7E AF        lea di, [bp - 0x51]
1A97  16              push ss
1A98  57              push di
1A99  8D BE 4A FF     lea di, [bp - 0xb6]
1A9D  16              push ss
1A9E  57              push di
1A9F  E8 11 FF        call 0x19b3
1AA2  8C D0           mov ax, ss
1AA4  89 46 A9        mov word ptr [bp - 0x57], ax
1AA7  8D 86 4A FF     lea ax, [bp - 0xb6]
1AAB  89 46 A1        mov word ptr [bp - 0x5f], ax
1AAE  31 C0           xor ax, ax
1AB0  89 46 9F        mov word ptr [bp - 0x61], ax
1AB3  8B 46 04        mov ax, word ptr [bp + 4]
1AB6  89 46 9B        mov word ptr [bp - 0x65], ax
1AB9  8D 7E 9B        lea di, [bp - 0x65]
1ABC  16              push ss
1ABD  57              push di
1ABE  9A 00 00 5C 23  call far 235C:0000
1AC3  8D 7E 9B        lea di, [bp - 0x65]
1AC6  16              push ss
1AC7  57              push di
1AC8  E8 29 FF        call 0x19f4
loc_1ACB:
1ACB  89 EC           mov sp, bp
1ACD  5D              pop bp
1ACE  C2 06 00        ret 6

; ---- routine 214B:1AD1  (found by: far)
sub_1AD1:
1AD1  55              push bp
1AD2  89 E5           mov bp, sp
1AD4  83 EC 16        sub sp, 0x16
1AD7  83 7E 06 00     cmp word ptr [bp + 6], 0
1ADB  74 07           je 0x1ae4
1ADD  83 3E A4 AA 00  cmp word ptr [0xaaa4], 0
1AE2  75 02           jne 0x1ae6
loc_1AE4:
1AE4  EB 58           jmp 0x1b3e
loc_1AE6:
1AE6  C4 7E 08        les di, ptr [bp + 8]
1AE9  8C C0           mov ax, es
1AEB  89 46 F9        mov word ptr [bp - 7], ax
1AEE  C4 7E 08        les di, ptr [bp + 8]
1AF1  89 F8           mov ax, di
1AF3  89 46 F1        mov word ptr [bp - 0xf], ax
1AF6  C6 46 EC 40     mov byte ptr [bp - 0x14], 0x40
1AFA  A1 A4 AA        mov ax, word ptr [0xaaa4]
1AFD  89 46 ED        mov word ptr [bp - 0x13], ax
1B00  8B 46 06        mov ax, word ptr [bp + 6]
1B03  89 46 EF        mov word ptr [bp - 0x11], ax
1B06  8D 7E EB        lea di, [bp - 0x15]
1B09  16              push ss
1B0A  57              push di
1B0B  9A 00 00 5C 23  call far 235C:0000
1B10  8B 46 FD        mov ax, word ptr [bp - 3]
1B13  25 01 00        and ax, 1
1B16  3D 01 00        cmp ax, 1
1B19  74 08           je 0x1b23
1B1B  8B 46 EB        mov ax, word ptr [bp - 0x15]
1B1E  3B 46 EF        cmp ax, word ptr [bp - 0x11]
1B21  74 04           je 0x1b27
loc_1B23:
1B23  B0 00           mov al, 0
1B25  EB 02           jmp 0x1b29
loc_1B27:
1B27  B0 01           mov al, 1
loc_1B29:
1B29  88 46 EA        mov byte ptr [bp - 0x16], al
1B2C  8A 46 EA        mov al, byte ptr [bp - 0x16]
1B2F  88 46 FF        mov byte ptr [bp - 1], al
1B32  80 7E EA 00     cmp byte ptr [bp - 0x16], 0
1B36  75 06           jne 0x1b3e
1B38  C7 06 65 A9 65 00 mov word ptr [0xa965], 0x65
loc_1B3E:
1B3E  8A 46 FF        mov al, byte ptr [bp - 1]
1B41  89 EC           mov sp, bp
1B43  5D              pop bp
1B44  CA 06 00        retf 6

; ---- routine 214B:1B47  (found by: far)
sub_1B47:
1B47  55              push bp
1B48  89 E5           mov bp, sp
1B4A  83 EC 14        sub sp, 0x14
1B4D  83 7E 06 00     cmp word ptr [bp + 6], 0
1B51  74 07           je 0x1b5a
1B53  83 3E A4 AA 00  cmp word ptr [0xaaa4], 0
1B58  75 02           jne 0x1b5c
loc_1B5A:
1B5A  EB 55           jmp 0x1bb1
loc_1B5C:
1B5C  C4 7E 08        les di, ptr [bp + 8]
1B5F  8C C0           mov ax, es
1B61  89 46 FA        mov word ptr [bp - 6], ax
1B64  C4 7E 08        les di, ptr [bp + 8]
1B67  89 F8           mov ax, di
1B69  89 46 F2        mov word ptr [bp - 0xe], ax
1B6C  C6 46 ED 3F     mov byte ptr [bp - 0x13], 0x3f
1B70  A1 A4 AA        mov ax, word ptr [0xaaa4]
1B73  89 46 EE        mov word ptr [bp - 0x12], ax
1B76  8B 46 06        mov ax, word ptr [bp + 6]
1B79  89 46 F0        mov word ptr [bp - 0x10], ax
1B7C  8D 7E EC        lea di, [bp - 0x14]
1B7F  16              push ss
1B80  57              push di
1B81  9A 00 00 5C 23  call far 235C:0000
1B86  8B 46 F0        mov ax, word ptr [bp - 0x10]
1B89  A3 67 A9        mov word ptr [0xa967], ax
1B8C  8B 46 FE        mov ax, word ptr [bp - 2]
1B8F  25 01 00        and ax, 1
1B92  3D 01 00        cmp ax, 1
1B95  75 06           jne 0x1b9d
1B97  8B 46 EC        mov ax, word ptr [bp - 0x14]
1B9A  A3 65 A9        mov word ptr [0xa965], ax
loc_1B9D:
1B9D  83 7E EC 00     cmp word ptr [bp - 0x14], 0
1BA1  74 0E           je 0x1bb1
1BA3  8B 46 EC        mov ax, word ptr [bp - 0x14]
1BA6  3B 46 F0        cmp ax, word ptr [bp - 0x10]
1BA9  73 06           jae 0x1bb1
1BAB  8B 46 EC        mov ax, word ptr [bp - 0x14]
1BAE  A3 67 A9        mov word ptr [0xa967], ax
loc_1BB1:
1BB1  89 EC           mov sp, bp
1BB3  5D              pop bp
1BB4  CA 06 00        retf 6

; ---- routine 214B:1BB7  (found by: far)
sub_1BB7:
1BB7  55              push bp
1BB8  89 E5           mov bp, sp
1BBA  83 EC 52        sub sp, 0x52
1BBD  C4 7E 06        les di, ptr [bp + 6]
1BC0  06              push es
1BC1  57              push di
1BC2  8D 7E AE        lea di, [bp - 0x52]
1BC5  16              push ss
1BC6  57              push di
1BC7  B8 50 00        mov ax, 0x50
1BCA  50              push ax
1BCB  9A 44 06 E4 23  call far 23E4:0644
1BD0  8D 7E AE        lea di, [bp - 0x52]
1BD3  16              push ss
1BD4  57              push di
1BD5  B8 00 3C        mov ax, 0x3c00
1BD8  50              push ax
1BD9  E8 83 FE        call 0x1a5f
1BDC  83 3E 65 A9 00  cmp word ptr [0xa965], 0
1BE1  74 04           je 0x1be7
1BE3  B0 00           mov al, 0
1BE5  EB 02           jmp 0x1be9
loc_1BE7:
1BE7  B0 01           mov al, 1
loc_1BE9:
1BE9  88 46 FF        mov byte ptr [bp - 1], al
1BEC  8A 46 FF        mov al, byte ptr [bp - 1]
1BEF  89 EC           mov sp, bp
1BF1  5D              pop bp
1BF2  CA 04 00        retf 4

; ---- routine 214B:1BF5  (found by: far)
sub_1BF5:
1BF5  55              push bp
1BF6  89 E5           mov bp, sp
1BF8  83 EC 52        sub sp, 0x52
1BFB  C4 7E 06        les di, ptr [bp + 6]
1BFE  06              push es
1BFF  57              push di
1C00  8D 7E AE        lea di, [bp - 0x52]
1C03  16              push ss
1C04  57              push di
1C05  B8 50 00        mov ax, 0x50
1C08  50              push ax
1C09  9A 44 06 E4 23  call far 23E4:0644
1C0E  8D 7E AE        lea di, [bp - 0x52]
1C11  16              push ss
1C12  57              push di
1C13  B8 02 3D        mov ax, 0x3d02
1C16  50              push ax
1C17  E8 45 FE        call 0x1a5f
1C1A  83 3E 65 A9 00  cmp word ptr [0xa965], 0
1C1F  74 04           je 0x1c25
1C21  B0 00           mov al, 0
1C23  EB 02           jmp 0x1c27
loc_1C25:
1C25  B0 01           mov al, 1
loc_1C27:
1C27  88 46 FF        mov byte ptr [bp - 1], al
1C2A  8A 46 FF        mov al, byte ptr [bp - 1]
1C2D  89 EC           mov sp, bp
1C2F  5D              pop bp
1C30  CA 04 00        retf 4

; ---- routine 214B:1C33  (found by: far)
sub_1C33:
1C33  55              push bp
1C34  89 E5           mov bp, sp
1C36  83 EC 16        sub sp, 0x16
1C39  C6 46 EC 19     mov byte ptr [bp - 0x14], 0x19
1C3D  8D 7E EB        lea di, [bp - 0x15]
1C40  16              push ss
1C41  57              push di
1C42  9A 00 00 5C 23  call far 235C:0000
1C47  80 7E EB 02     cmp byte ptr [bp - 0x15], 2
1C4B  72 0A           jb 0x1c57
1C4D  80 7E EB 03     cmp byte ptr [bp - 0x15], 3
1C51  77 04           ja 0x1c57
1C53  B0 00           mov al, 0
1C55  EB 02           jmp 0x1c59
loc_1C57:
1C57  B0 01           mov al, 1
loc_1C59:
1C59  88 46 FF        mov byte ptr [bp - 1], al
1C5C  8A 46 FF        mov al, byte ptr [bp - 1]
1C5F  89 EC           mov sp, bp
1C61  5D              pop bp
1C62  CB              retf

; ---- routine 214B:1C63  (found by: call)
sub_1C63:
1C63  55              push bp
1C64  89 E5           mov bp, sp
1C66  83 EC 06        sub sp, 6
1C69  BF FD A9        mov di, 0xa9fd
1C6C  1E              push ds
1C6D  57              push di
1C6E  8D 7E FE        lea di, [bp - 2]
1C71  16              push ss
1C72  57              push di
1C73  8D 7E FC        lea di, [bp - 4]
1C76  16              push ss
1C77  57              push di
1C78  8D 7E FA        lea di, [bp - 6]
1C7B  16              push ss
1C7C  57              push di
1C7D  9A 6C 00 5C 23  call far 235C:006C
1C82  89 EC           mov sp, bp
1C84  5D              pop bp
1C85  C3              ret

; ---- routine 214B:1C86  (found by: call, far)
sub_1C86:
1C86  55              push bp
1C87  89 E5           mov bp, sp
1C89  83 7E 06 00     cmp word ptr [bp + 6], 0
1C8D  7E 6E           jle 0x1cfd
1C8F  8B 46 06        mov ax, word ptr [bp + 6]
1C92  99              cdq
1C93  8B C8           mov cx, ax
1C95  8B DA           mov bx, dx
1C97  C4 7E 0C        les di, ptr [bp + 0xc]
1C9A  26 8B 05        mov ax, word ptr es:[di]
1C9D  31 D2           xor dx, dx
1C9F  03 C1           add ax, cx
1CA1  13 D3           adc dx, bx
1CA3  8B C8           mov cx, ax
1CA5  8B DA           mov bx, dx
1CA7  8B 46 08        mov ax, word ptr [bp + 8]
1CAA  31 D2           xor dx, dx
1CAC  3B D3           cmp dx, bx
1CAE  7F 06           jg 0x1cb6
1CB0  7C 0F           jl 0x1cc1
1CB2  3B C1           cmp ax, cx
1CB4  72 0B           jb 0x1cc1
loc_1CB6:
1CB6  8B 46 06        mov ax, word ptr [bp + 6]
1CB9  C4 7E 0C        les di, ptr [bp + 0xc]
1CBC  26 01 05        add word ptr es:[di], ax
1CBF  EB 3A           jmp 0x1cfb
loc_1CC1:
1CC1  8B 46 08        mov ax, word ptr [bp + 8]
1CC4  31 D2           xor dx, dx
1CC6  52              push dx
1CC7  50              push ax
1CC8  8B 46 06        mov ax, word ptr [bp + 6]
1CCB  99              cdq
1CCC  8B C8           mov cx, ax
1CCE  8B DA           mov bx, dx
1CD0  C4 7E 0C        les di, ptr [bp + 0xc]
1CD3  26 8B 05        mov ax, word ptr es:[di]
1CD6  31 D2           xor dx, dx
1CD8  03 C1           add ax, cx
1CDA  13 D3           adc dx, bx
1CDC  59              pop cx
1CDD  5B              pop bx
1CDE  2B C1           sub ax, cx
1CE0  1B D3           sbb dx, bx
1CE2  8B C8           mov cx, ax
1CE4  8B DA           mov bx, dx
1CE6  8B 46 0A        mov ax, word ptr [bp + 0xa]
1CE9  31 D2           xor dx, dx
1CEB  03 C1           add ax, cx
1CED  13 D3           adc dx, bx
1CEF  2D 01 00        sub ax, 1
1CF2  83 DA 00        sbb dx, 0
1CF5  C4 7E 0C        les di, ptr [bp + 0xc]
1CF8  26 89 05        mov word ptr es:[di], ax
loc_1CFB:
1CFB  EB 6C           jmp 0x1d69
loc_1CFD:
1CFD  8B 46 06        mov ax, word ptr [bp + 6]
1D00  99              cdq
1D01  8B C8           mov cx, ax
1D03  8B DA           mov bx, dx
1D05  C4 7E 0C        les di, ptr [bp + 0xc]
1D08  26 8B 05        mov ax, word ptr es:[di]
1D0B  31 D2           xor dx, dx
1D0D  03 C1           add ax, cx
1D0F  13 D3           adc dx, bx
1D11  8B C8           mov cx, ax
1D13  8B DA           mov bx, dx
1D15  8B 46 0A        mov ax, word ptr [bp + 0xa]
1D18  31 D2           xor dx, dx
1D1A  3B D3           cmp dx, bx
1D1C  7C 06           jl 0x1d24
1D1E  7F 0F           jg 0x1d2f
1D20  3B C1           cmp ax, cx
1D22  77 0B           ja 0x1d2f
loc_1D24:
1D24  8B 46 06        mov ax, word ptr [bp + 6]
1D27  C4 7E 0C        les di, ptr [bp + 0xc]
1D2A  26 01 05        add word ptr es:[di], ax
1D2D  EB 3A           jmp 0x1d69
loc_1D2F:
1D2F  8B 46 0A        mov ax, word ptr [bp + 0xa]
1D32  31 D2           xor dx, dx
1D34  52              push dx
1D35  50              push ax
1D36  8B 46 06        mov ax, word ptr [bp + 6]
1D39  99              cdq
1D3A  8B C8           mov cx, ax
1D3C  8B DA           mov bx, dx
1D3E  C4 7E 0C        les di, ptr [bp + 0xc]
1D41  26 8B 05        mov ax, word ptr es:[di]
1D44  31 D2           xor dx, dx
1D46  03 C1           add ax, cx
1D48  13 D3           adc dx, bx
1D4A  8B C8           mov cx, ax
1D4C  8B DA           mov bx, dx
1D4E  8B 46 08        mov ax, word ptr [bp + 8]
1D51  31 D2           xor dx, dx
1D53  03 C1           add ax, cx
1D55  13 D3           adc dx, bx
1D57  59              pop cx
1D58  5B              pop bx
1D59  2B C1           sub ax, cx
1D5B  1B D3           sbb dx, bx
1D5D  05 01 00        add ax, 1
1D60  83 D2 00        adc dx, 0
1D63  C4 7E 0C        les di, ptr [bp + 0xc]
1D66  26 89 05        mov word ptr es:[di], ax
loc_1D69:
1D69  89 EC           mov sp, bp
1D6B  5D              pop bp
1D6C  CA 0A 00        retf 0xa

