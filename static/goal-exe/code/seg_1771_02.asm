; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 2 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:0AA7  (found by: call, far)
sub_0AA7:
0AA7  55              push bp
0AA8  89 E5           mov bp, sp
0AAA  83 EC 06        sub sp, 6
0AAD  8B 46 06        mov ax, word ptr [bp + 6]
0AB0  BA BF 00        mov dx, 0xbf
0AB3  F7 E2           mul dx
0AB5  C4 3E 17 A9     les di, ptr [0xa917]
0AB9  03 F8           add di, ax
0ABB  89 7E FA        mov word ptr [bp - 6], di
0ABE  8C 46 FC        mov word ptr [bp - 4], es
0AC1  C4 7E FA        les di, ptr [bp - 6]
0AC4  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0AC8  30 E4           xor ah, ah
0ACA  BA 03 00        mov dx, 3
0ACD  F7 E2           mul dx
0ACF  C4 3E 1F A9     les di, ptr [0xa91f]
0AD3  03 F8           add di, ax
0AD5  26 8A 45 01     mov al, byte ptr es:[di + 1]
0AD9  30 E4           xor ah, ah
0ADB  99              cdq
0ADC  B9 08 00        mov cx, 8
0ADF  F7 F9           idiv cx
0AE1  05 10 00        add ax, 0x10
0AE4  89 46 FE        mov word ptr [bp - 2], ax
0AE7  8B 46 FE        mov ax, word ptr [bp - 2]
0AEA  89 EC           mov sp, bp
0AEC  5D              pop bp
0AED  CA 02 00        retf 2
; data (not reached as code), 8 bytes
0AF0                  pstr 'unknown'

; ---- routine 1771:0AF8  (found by: call, far)
sub_0AF8:
0AF8  55              push bp
0AF9  89 E5           mov bp, sp
0AFB  83 EC 04        sub sp, 4
0AFE  8B 46 0A        mov ax, word ptr [bp + 0xa]
0B01  BA 03 00        mov dx, 3
0B04  F7 E2           mul dx
0B06  C4 3E 1F A9     les di, ptr [0xa91f]
0B0A  03 F8           add di, ax
0B0C  89 7E FC        mov word ptr [bp - 4], di
0B0F  8C 46 FE        mov word ptr [bp - 2], es
0B12  83 7E 0A 00     cmp word ptr [bp + 0xa], 0
0B16  74 59           je 0xb71
0B18  C4 7E FC        les di, ptr [bp - 4]
0B1B  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
0B20  75 19           jne 0xb3b
0B22  BF F0 0A        mov di, 0xaf0
0B25  0E              push cs
0B26  57              push di
0B27  8A 46 08        mov al, byte ptr [bp + 8]
0B2A  50              push ax
0B2B  8A 46 06        mov al, byte ptr [bp + 6]
0B2E  50              push ax
0B2F  BF 6E A9        mov di, 0xa96e
0B32  1E              push ds
0B33  57              push di
0B34  9A 6D 02 4B 21  call far 214B:026D
0B39  EB 36           jmp 0xb71
loc_0B3B:
0B3B  C4 7E FC        les di, ptr [bp - 4]
0B3E  26 8A 45 01     mov al, byte ptr es:[di + 1]
0B42  30 E4           xor ah, ah
0B44  48              dec ax
0B45  99              cdq
0B46  B9 08 00        mov cx, 8
0B49  F7 F9           idiv cx
0B4B  8B F8           mov di, ax
0B4D  8A 85 94 78     mov al, byte ptr [di + 0x7894]
0B51  30 E4           xor ah, ah
0B53  8B F8           mov di, ax
0B55  B1 04           mov cl, 4
0B57  D3 E7           shl di, cl
0B59  81 C7 B4 6E     add di, 0x6eb4
0B5D  1E              push ds
0B5E  57              push di
0B5F  8A 46 08        mov al, byte ptr [bp + 8]
0B62  50              push ax
0B63  8A 46 06        mov al, byte ptr [bp + 6]
0B66  50              push ax
0B67  BF 6E A9        mov di, 0xa96e
0B6A  1E              push ds
0B6B  57              push di
0B6C  9A 6D 02 4B 21  call far 214B:026D
loc_0B71:
0B71  89 EC           mov sp, bp
0B73  5D              pop bp
0B74  CA 06 00        retf 6

; ---- routine 1771:0B77  (found by: call, far)
sub_0B77:
0B77  55              push bp
0B78  89 E5           mov bp, sp
0B7A  83 EC 02        sub sp, 2
0B7D  8B 46 06        mov ax, word ptr [bp + 6]
0B80  BA BF 00        mov dx, 0xbf
0B83  F7 E2           mul dx
0B85  C4 3E 17 A9     les di, ptr [0xa917]
0B89  03 F8           add di, ax
0B8B  26 80 7D 2E 80  cmp byte ptr es:[di + 0x2e], 0x80
0B90  77 04           ja 0xb96
0B92  B0 00           mov al, 0
0B94  EB 02           jmp 0xb98
loc_0B96:
0B96  B0 01           mov al, 1
loc_0B98:
0B98  88 46 FF        mov byte ptr [bp - 1], al
0B9B  8A 46 FF        mov al, byte ptr [bp - 1]
0B9E  89 EC           mov sp, bp
0BA0  5D              pop bp
0BA1  CA 02 00        retf 2
; data (not reached as code), 32 bytes
0BA4                  db 62 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; b...............
0BB4                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:0BC4  (found by: call, far)
sub_0BC4:
0BC4  55              push bp
0BC5  89 E5           mov bp, sp
0BC7  83 EC 12        sub sp, 0x12
0BCA  8B 46 0A        mov ax, word ptr [bp + 0xa]
0BCD  BA BF 00        mov dx, 0xbf
0BD0  F7 E2           mul dx
0BD2  C4 3E 17 A9     les di, ptr [0xa917]
0BD6  03 F8           add di, ax
0BD8  89 7E F3        mov word ptr [bp - 0xd], di
0BDB  8C 46 F5        mov word ptr [bp - 0xb], es
0BDE  FF 76 0A        push word ptr [bp + 0xa]
0BE1  0E              push cs
0BE2  E8 C2 FE        call 0xaa7
0BE5  89 46 FC        mov word ptr [bp - 4], ax
0BE8  31 C0           xor ax, ax
0BEA  89 46 FE        mov word ptr [bp - 2], ax
0BED  EB 03           jmp 0xbf2
loc_0BEF:
0BEF  FF 46 FE        inc word ptr [bp - 2]
loc_0BF2:
0BF2  8A 46 08        mov al, byte ptr [bp + 8]
0BF5  98              cwde
0BF6  D1 E0           shl ax, 1
0BF8  8B 7E FE        mov di, word ptr [bp - 2]
0BFB  D1 E7           shl di, 1
0BFD  D1 E7           shl di, 1
0BFF  03 F8           add di, ax
0C01  31 C0           xor ax, ax
0C03  89 85 45 9B     mov word ptr [di - 0x64bb], ax
0C07  83 7E FE 03     cmp word ptr [bp - 2], 3
0C0B  75 E2           jne 0xbef
0C0D  C7 46 FE 01 00  mov word ptr [bp - 2], 1
0C12  EB 03           jmp 0xc17
loc_0C14:
0C14  FF 46 FE        inc word ptr [bp - 2]
loc_0C17:
0C17  8B 46 FE        mov ax, word ptr [bp - 2]
0C1A  D1 E0           shl ax, 1
0C1C  C4 7E F3        les di, ptr [bp - 0xd]
0C1F  03 F8           add di, ax
0C21  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
0C26  75 03           jne 0xc2b
0C28  E9 A6 01        jmp 0xdd1
loc_0C2B:
0C2B  8B 46 FE        mov ax, word ptr [bp - 2]
0C2E  D1 E0           shl ax, 1
0C30  C4 7E F3        les di, ptr [bp - 0xd]
0C33  03 F8           add di, ax
0C35  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0C39  BA 14 00        mov dx, 0x14
0C3C  F7 E2           mul dx
0C3E  C4 3E 1B A9     les di, ptr [0xa91b]
0C42  03 F8           add di, ax
0C44  89 7E EF        mov word ptr [bp - 0x11], di
0C47  8C 46 F1        mov word ptr [bp - 0xf], es
0C4A  8B 46 FE        mov ax, word ptr [bp - 2]
0C4D  D1 E0           shl ax, 1
0C4F  C4 7E F3        les di, ptr [bp - 0xd]
0C52  03 F8           add di, ax
0C54  26 FF 75 FE     push word ptr es:[di - 2]
0C58  0E              push cs
0C59  E8 22 2B        call 0x377e
0C5C  89 46 FA        mov word ptr [bp - 6], ax
0C5F  83 7E FA 00     cmp word ptr [bp - 6], 0
0C63  74 06           je 0xc6b
0C65  8B 46 FC        mov ax, word ptr [bp - 4]
0C68  01 46 FA        add word ptr [bp - 6], ax
loc_0C6B:
0C6B  C4 7E EF        les di, ptr [bp - 0x11]
0C6E  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
0C73  75 03           jne 0xc78
0C75  E9 BA 00        jmp 0xd32
loc_0C78:
0C78  C7 46 F8 01 00  mov word ptr [bp - 8], 1
0C7D  EB 03           jmp 0xc82
loc_0C7F:
0C7F  FF 46 F8        inc word ptr [bp - 8]
loc_0C82:
0C82  8A 46 F8        mov al, byte ptr [bp - 8]
0C85  50              push ax
0C86  BF A4 0B        mov di, 0xba4
0C89  0E              push cs
0C8A  57              push di
0C8B  9A DF 08 E4 23  call far 23E4:08DF
0C90  75 03           jne 0xc95
0C92  E9 94 00        jmp 0xd29
loc_0C95:
0C95  83 7E F8 05     cmp word ptr [bp - 8], 5
0C99  73 31           jae 0xccc
0C9B  8B 46 F8        mov ax, word ptr [bp - 8]
0C9E  05 04 00        add ax, 4
0CA1  50              push ax
0CA2  C4 7E EF        les di, ptr [bp - 0x11]
0CA5  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
0CA9  30 E4           xor ah, ah
0CAB  50              push ax
0CAC  9A 57 0C 4B 21  call far 214B:0C57
0CB1  08 C0           or al, al
0CB3  74 17           je 0xccc
0CB5  FF 76 F8        push word ptr [bp - 8]
0CB8  C4 7E EF        les di, ptr [bp - 0x11]
0CBB  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
0CBF  30 E4           xor ah, ah
0CC1  50              push ax
0CC2  9A 57 0C 4B 21  call far 214B:0C57
0CC7  88 46 F7        mov byte ptr [bp - 9], al
0CCA  EB 25           jmp 0xcf1
loc_0CCC:
0CCC  FF 76 F8        push word ptr [bp - 8]
0CCF  C4 7E EF        les di, ptr [bp - 0x11]
0CD2  26 8A 05        mov al, byte ptr es:[di]
0CD5  30 E4           xor ah, ah
0CD7  BA BF 00        mov dx, 0xbf
0CDA  F7 E2           mul dx
0CDC  C4 3E 17 A9     les di, ptr [0xa917]
0CE0  03 F8           add di, ax
0CE2  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
0CE6  30 E4           xor ah, ah
0CE8  50              push ax
0CE9  9A 57 0C 4B 21  call far 214B:0C57
0CEE  88 46 F7        mov byte ptr [bp - 9], al
loc_0CF1:
0CF1  80 7E F7 00     cmp byte ptr [bp - 9], 0
0CF5  74 1A           je 0xd11
0CF7  8B 46 FC        mov ax, word ptr [bp - 4]
0CFA  31 D2           xor dx, dx
0CFC  B9 08 00        mov cx, 8
0CFF  F7 F1           div cx
0D01  8B D0           mov dx, ax
0D03  8A 46 08        mov al, byte ptr [bp + 8]
0D06  98              cwde
0D07  8B F8           mov di, ax
0D09  D1 E7           shl di, 1
0D0B  01 95 51 9B     add word ptr [di - 0x64af], dx
0D0F  EB 18           jmp 0xd29
loc_0D11:
0D11  8B 46 FC        mov ax, word ptr [bp - 4]
0D14  31 D2           xor dx, dx
0D16  B9 08 00        mov cx, 8
0D19  F7 F1           div cx
0D1B  8B D0           mov dx, ax
0D1D  8A 46 08        mov al, byte ptr [bp + 8]
0D20  98              cwde
0D21  8B F8           mov di, ax
0D23  D1 E7           shl di, 1
0D25  01 95 49 9B     add word ptr [di - 0x64b7], dx
loc_0D29:
0D29  83 7E F8 06     cmp word ptr [bp - 8], 6
0D2D  74 03           je 0xd32
0D2F  E9 4D FF        jmp 0xc7f
loc_0D32:
0D32  C4 7E EF        les di, ptr [bp - 0x11]
0D35  26 8A 45 06     mov al, byte ptr es:[di + 6]
0D39  30 E4           xor ah, ah
0D3B  8B F8           mov di, ax
0D3D  80 BD 4E 0D 04  cmp byte ptr [di + 0xd4e], 4
0D42  73 2A           jae 0xd6e
0D44  8B 4E FA        mov cx, word ptr [bp - 6]
0D47  8A 46 08        mov al, byte ptr [bp + 8]
0D4A  98              cwde
0D4B  D1 E0           shl ax, 1
0D4D  8B D0           mov dx, ax
0D4F  C4 7E EF        les di, ptr [bp - 0x11]
0D52  26 8A 45 06     mov al, byte ptr es:[di + 6]
0D56  30 E4           xor ah, ah
0D58  8B F8           mov di, ax
0D5A  8A 85 4E 0D     mov al, byte ptr [di + 0xd4e]
0D5E  30 E4           xor ah, ah
0D60  8B F8           mov di, ax
0D62  D1 E7           shl di, 1
0D64  D1 E7           shl di, 1
0D66  03 FA           add di, dx
0D68  01 8D 45 9B     add word ptr [di - 0x64bb], cx
0D6C  EB 63           jmp 0xdd1
loc_0D6E:
0D6E  8B 46 FA        mov ax, word ptr [bp - 6]
0D71  31 D2           xor dx, dx
0D73  B9 02 00        mov cx, 2
0D76  F7 F1           div cx
0D78  89 46 FA        mov word ptr [bp - 6], ax
0D7B  8B 4E FA        mov cx, word ptr [bp - 6]
0D7E  8A 46 08        mov al, byte ptr [bp + 8]
0D81  98              cwde
0D82  D1 E0           shl ax, 1
0D84  8B D0           mov dx, ax
0D86  C4 7E EF        les di, ptr [bp - 0x11]
0D89  26 8A 45 06     mov al, byte ptr es:[di + 6]
0D8D  30 E4           xor ah, ah
0D8F  8B F8           mov di, ax
0D91  8A 85 4E 0D     mov al, byte ptr [di + 0xd4e]
0D95  30 E4           xor ah, ah
0D97  2D 03 00        sub ax, 3
0D9A  8B F8           mov di, ax
0D9C  D1 E7           shl di, 1
0D9E  D1 E7           shl di, 1
0DA0  03 FA           add di, dx
0DA2  01 8D 45 9B     add word ptr [di - 0x64bb], cx
0DA6  8B 4E FA        mov cx, word ptr [bp - 6]
0DA9  8A 46 08        mov al, byte ptr [bp + 8]
0DAC  98              cwde
0DAD  D1 E0           shl ax, 1
0DAF  8B D0           mov dx, ax
0DB1  C4 7E EF        les di, ptr [bp - 0x11]
0DB4  26 8A 45 06     mov al, byte ptr es:[di + 6]
0DB8  30 E4           xor ah, ah
0DBA  8B F8           mov di, ax
0DBC  8A 85 4E 0D     mov al, byte ptr [di + 0xd4e]
0DC0  30 E4           xor ah, ah
0DC2  2D 02 00        sub ax, 2
0DC5  8B F8           mov di, ax
0DC7  D1 E7           shl di, 1
0DC9  D1 E7           shl di, 1
0DCB  03 FA           add di, dx
0DCD  01 8D 45 9B     add word ptr [di - 0x64bb], cx
loc_0DD1:
0DD1  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
0DD5  74 03           je 0xdda
0DD7  E9 3A FE        jmp 0xc14
loc_0DDA:
0DDA  80 7E 06 00     cmp byte ptr [bp + 6], 0
0DDE  74 3E           je 0xe1e
0DE0  31 C0           xor ax, ax
0DE2  89 46 FE        mov word ptr [bp - 2], ax
0DE5  EB 03           jmp 0xdea
loc_0DE7:
0DE7  FF 46 FE        inc word ptr [bp - 2]
loc_0DEA:
0DEA  8A 46 08        mov al, byte ptr [bp + 8]
0DED  98              cwde
0DEE  D1 E0           shl ax, 1
0DF0  8B 7E FE        mov di, word ptr [bp - 2]
0DF3  D1 E7           shl di, 1
0DF5  D1 E7           shl di, 1
0DF7  03 F8           add di, ax
0DF9  8B 85 45 9B     mov ax, word ptr [di - 0x64bb]
0DFD  99              cdq
0DFE  B9 08 00        mov cx, 8
0E01  F7 F9           idiv cx
0E03  8B D0           mov dx, ax
0E05  8A 46 08        mov al, byte ptr [bp + 8]
0E08  98              cwde
0E09  D1 E0           shl ax, 1
0E0B  8B 7E FE        mov di, word ptr [bp - 2]
0E0E  D1 E7           shl di, 1
0E10  D1 E7           shl di, 1
0E12  03 F8           add di, ax
0E14  01 95 45 9B     add word ptr [di - 0x64bb], dx
0E18  83 7E FE 03     cmp word ptr [bp - 2], 3
0E1C  75 C9           jne 0xde7
loc_0E1E:
0E1E  89 EC           mov sp, bp
0E20  5D              pop bp
0E21  CA 06 00        retf 6

; ---- routine 1771:0E24  (found by: call)
sub_0E24:
0E24  55              push bp
0E25  89 E5           mov bp, sp
0E27  83 EC 06        sub sp, 6
0E2A  8B 46 04        mov ax, word ptr [bp + 4]
0E2D  BA BF 00        mov dx, 0xbf
0E30  F7 E2           mul dx
0E32  C4 3E 17 A9     les di, ptr [0xa917]
0E36  03 F8           add di, ax
0E38  89 7E FB        mov word ptr [bp - 5], di
0E3B  8C 46 FD        mov word ptr [bp - 3], es
0E3E  FF 76 04        push word ptr [bp + 4]
0E41  0E              push cs
0E42  E8 32 FD        call 0xb77
0E45  08 C0           or al, al
0E47  74 06           je 0xe4f
0E49  C6 46 FF 0F     mov byte ptr [bp - 1], 0xf
0E4D  EB 12           jmp 0xe61
loc_0E4F:
0E4F  C4 7E FB        les di, ptr [bp - 5]
0E52  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
0E56  30 E4           xor ah, ah
0E58  8B F8           mov di, ax
0E5A  8A 85 05 69     mov al, byte ptr [di + 0x6905]
0E5E  88 46 FF        mov byte ptr [bp - 1], al
loc_0E61:
0E61  8A 46 FF        mov al, byte ptr [bp - 1]
0E64  89 EC           mov sp, bp
0E66  5D              pop bp
0E67  C2 02 00        ret 2
; data (not reached as code), 2 bytes
0E6A                  db 01 2D   ; .-

; ---- routine 1771:0E6C  (found by: call, far)
sub_0E6C:
0E6C  55              push bp
0E6D  89 E5           mov bp, sp
0E6F  81 EC 0A 03     sub sp, 0x30a
0E73  8B 46 06        mov ax, word ptr [bp + 6]
0E76  BA BF 00        mov dx, 0xbf
0E79  F7 E2           mul dx
0E7B  C4 3E 17 A9     les di, ptr [0xa917]
0E7F  03 F8           add di, ax
0E81  89 7E F6        mov word ptr [bp - 0xa], di
0E84  8C 46 F8        mov word ptr [bp - 8], es
0E87  31 C0           xor ax, ax
0E89  89 46 FC        mov word ptr [bp - 4], ax
0E8C  89 46 FE        mov word ptr [bp - 2], ax
0E8F  C7 46 FA 01 00  mov word ptr [bp - 6], 1
0E94  EB 03           jmp 0xe99
loc_0E96:
0E96  FF 46 FA        inc word ptr [bp - 6]
loc_0E99:
0E99  8B 46 FA        mov ax, word ptr [bp - 6]
0E9C  D1 E0           shl ax, 1
0E9E  C4 7E F6        les di, ptr [bp - 0xa]
0EA1  03 F8           add di, ax
0EA3  26 FF 75 FE     push word ptr es:[di - 2]
0EA7  0E              push cs
0EA8  E8 6B 23        call 0x3216
0EAB  08 C0           or al, al
0EAD  75 35           jne 0xee4
0EAF  8B 46 FA        mov ax, word ptr [bp - 6]
0EB2  D1 E0           shl ax, 1
0EB4  C4 7E F6        les di, ptr [bp - 0xa]
0EB7  03 F8           add di, ax
0EB9  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0EBD  BA 14 00        mov dx, 0x14
0EC0  F7 E2           mul dx
0EC2  C4 3E 1B A9     les di, ptr [0xa91b]
0EC6  03 F8           add di, ax
0EC8  89 7E F2        mov word ptr [bp - 0xe], di
0ECB  8C 46 F4        mov word ptr [bp - 0xc], es
0ECE  C4 7E F2        les di, ptr [bp - 0xe]
0ED1  26 8A 45 06     mov al, byte ptr es:[di + 6]
0ED5  30 E4           xor ah, ah
0ED7  8B F8           mov di, ax
0ED9  8A 85 5C 0D     mov al, byte ptr [di + 0xd5c]
0EDD  30 E4           xor ah, ah
0EDF  8B F8           mov di, ax
0EE1  FE 43 FC        inc byte ptr [bp + di - 4]
loc_0EE4:
0EE4  83 7E FA 0B     cmp word ptr [bp - 6], 0xb
0EE8  75 AC           jne 0xe96
0EEA  8D BE F6 FE     lea di, [bp - 0x10a]
0EEE  16              push ss
0EEF  57              push di
0EF0  8A 46 FD        mov al, byte ptr [bp - 3]
0EF3  30 E4           xor ah, ah
0EF5  31 D2           xor dx, dx
0EF7  52              push dx
0EF8  50              push ax
0EF9  9A DA 09 4B 21  call far 214B:09DA
0EFE  BF 6A 0E        mov di, 0xe6a
0F01  0E              push cs
0F02  57              push di
0F03  9A B7 06 E4 23  call far 23E4:06B7
0F08  8D BE F6 FD     lea di, [bp - 0x20a]
0F0C  16              push ss
0F0D  57              push di
0F0E  8A 46 FE        mov al, byte ptr [bp - 2]
0F11  30 E4           xor ah, ah
0F13  31 D2           xor dx, dx
0F15  52              push dx
0F16  50              push ax
0F17  9A DA 09 4B 21  call far 214B:09DA
0F1C  9A B7 06 E4 23  call far 23E4:06B7
0F21  BF 6A 0E        mov di, 0xe6a
0F24  0E              push cs
0F25  57              push di
0F26  9A B7 06 E4 23  call far 23E4:06B7
0F2B  8D BE F6 FC     lea di, [bp - 0x30a]
0F2F  16              push ss
0F30  57              push di
0F31  8A 46 FF        mov al, byte ptr [bp - 1]
0F34  30 E4           xor ah, ah
0F36  31 D2           xor dx, dx
0F38  52              push dx
0F39  50              push ax
0F3A  9A DA 09 4B 21  call far 214B:09DA
0F3F  9A B7 06 E4 23  call far 23E4:06B7
0F44  C4 7E 08        les di, ptr [bp + 8]
0F47  06              push es
0F48  57              push di
0F49  B8 0A 00        mov ax, 0xa
0F4C  50              push ax
0F4D  9A 44 06 E4 23  call far 23E4:0644
0F52  89 EC           mov sp, bp
0F54  5D              pop bp
0F55  CA 02 00        retf 2

; ---- routine 1771:0F58  (found by: call, far)
sub_0F58:
0F58  55              push bp
0F59  89 E5           mov bp, sp
0F5B  A0 64 A9        mov al, byte ptr [0xa964]
0F5E  98              cwde
0F5F  8B F8           mov di, ax
0F61  8A 85 7A 0D     mov al, byte ptr [di + 0xd7a]
0F65  50              push ax
0F66  BF 6A 0D        mov di, 0xd6a
0F69  1E              push ds
0F6A  57              push di
0F6B  8A 46 08        mov al, byte ptr [bp + 8]
0F6E  50              push ax
0F6F  8A 46 06        mov al, byte ptr [bp + 6]
0F72  50              push ax
0F73  BF 6E A9        mov di, 0xa96e
0F76  1E              push ds
0F77  57              push di
0F78  9A C8 02 4B 21  call far 214B:02C8
0F7D  83 7E 0A 00     cmp word ptr [bp + 0xa], 0
0F81  74 28           je 0xfab
0F83  FF 76 0A        push word ptr [bp + 0xa]
0F86  E8 9B FE        call 0xe24
0F89  50              push ax
0F8A  8B 46 0A        mov ax, word ptr [bp + 0xa]
0F8D  B1 04           mov cl, 4
0F8F  D3 E0           shl ax, cl
0F91  C4 3E 68 9B     les di, ptr [0x9b68]
0F95  03 F8           add di, ax
0F97  06              push es
0F98  57              push di
0F99  8A 46 08        mov al, byte ptr [bp + 8]
0F9C  50              push ax
0F9D  8A 46 06        mov al, byte ptr [bp + 6]
0FA0  50              push ax
0FA1  BF 6E A9        mov di, 0xa96e
0FA4  1E              push ds
0FA5  57              push di
0FA6  9A C8 02 4B 21  call far 214B:02C8
loc_0FAB:
0FAB  89 EC           mov sp, bp
0FAD  5D              pop bp
0FAE  CA 06 00        retf 6

; ---- routine 1771:0FB1  (found by: call)
sub_0FB1:
0FB1  55              push bp
0FB2  89 E5           mov bp, sp
0FB4  A0 64 A9        mov al, byte ptr [0xa964]
0FB7  98              cwde
0FB8  8B F8           mov di, ax
0FBA  8A 85 7A 0D     mov al, byte ptr [di + 0xd7a]
0FBE  50              push ax
0FBF  BF 6A 0D        mov di, 0xd6a
0FC2  1E              push ds
0FC3  57              push di
0FC4  8A 46 06        mov al, byte ptr [bp + 6]
0FC7  50              push ax
0FC8  8A 46 04        mov al, byte ptr [bp + 4]
0FCB  50              push ax
0FCC  BF 6E A9        mov di, 0xa96e
0FCF  1E              push ds
0FD0  57              push di
0FD1  9A 05 02 4B 21  call far 214B:0205
0FD6  83 7E 08 00     cmp word ptr [bp + 8], 0
0FDA  74 28           je 0x1004
0FDC  FF 76 08        push word ptr [bp + 8]
0FDF  E8 42 FE        call 0xe24
0FE2  50              push ax
0FE3  8B 46 08        mov ax, word ptr [bp + 8]
0FE6  B1 04           mov cl, 4
0FE8  D3 E0           shl ax, cl
0FEA  C4 3E 68 9B     les di, ptr [0x9b68]
0FEE  03 F8           add di, ax
0FF0  06              push es
0FF1  57              push di
0FF2  8A 46 06        mov al, byte ptr [bp + 6]
0FF5  50              push ax
0FF6  8A 46 04        mov al, byte ptr [bp + 4]
0FF9  50              push ax
0FFA  BF 6E A9        mov di, 0xa96e
0FFD  1E              push ds
0FFE  57              push di
0FFF  9A 05 02 4B 21  call far 214B:0205
loc_1004:
1004  89 EC           mov sp, bp
1006  5D              pop bp
1007  C2 06 00        ret 6
; data (not reached as code), 16 bytes
100A                  pstr ' already exists'

; ---- routine 1771:101A  (found by: call)
sub_101A:
101A  55              push bp
101B  89 E5           mov bp, sp
101D  81 EC 12 01     sub sp, 0x112
1021  8B 46 04        mov ax, word ptr [bp + 4]
1024  B1 04           mov cl, 4
1026  D3 E0           shl ax, cl
1028  C4 3E 68 9B     les di, ptr [0x9b68]
102C  03 F8           add di, ax
102E  06              push es
102F  57              push di
1030  8D 7E F0        lea di, [bp - 0x10]
1033  16              push ss
1034  57              push di
1035  B8 0F 00        mov ax, 0xf
1038  50              push ax
1039  9A 44 06 E4 23  call far 23E4:0644
103E  8D 7E F0        lea di, [bp - 0x10]
1041  16              push ss
1042  57              push di
1043  B0 0F           mov al, 0xf
1045  50              push ax
1046  B0 02           mov al, 2
1048  50              push ax
1049  B0 11           mov al, 0x11
104B  50              push ax
104C  B0 08           mov al, 8
104E  50              push ax
104F  9A 86 10 4B 21  call far 214B:1086
1054  80 7E F0 00     cmp byte ptr [bp - 0x10], 0
1058  75 03           jne 0x105d
105A  E9 84 00        jmp 0x10e1
loc_105D:
105D  C7 46 EE 01 00  mov word ptr [bp - 0x12], 1
1062  EB 03           jmp 0x1067
loc_1064:
1064  FF 46 EE        inc word ptr [bp - 0x12]
loc_1067:
1067  8B 46 EE        mov ax, word ptr [bp - 0x12]
106A  3B 46 04        cmp ax, word ptr [bp + 4]
106D  74 49           je 0x10b8
106F  8D 7E F0        lea di, [bp - 0x10]
1072  16              push ss
1073  57              push di
1074  8B 46 EE        mov ax, word ptr [bp - 0x12]
1077  B1 04           mov cl, 4
1079  D3 E0           shl ax, cl
107B  C4 3E 68 9B     les di, ptr [0x9b68]
107F  03 F8           add di, ax
1081  06              push es
1082  57              push di
1083  9A 2F 07 E4 23  call far 23E4:072F
1088  75 2E           jne 0x10b8
108A  8D BE EE FE     lea di, [bp - 0x112]
108E  16              push ss
108F  57              push di
1090  8B 46 EE        mov ax, word ptr [bp - 0x12]
1093  B1 04           mov cl, 4
1095  D3 E0           shl ax, cl
1097  C4 3E 68 9B     les di, ptr [0x9b68]
109B  03 F8           add di, ax
109D  06              push es
109E  57              push di
109F  9A 2A 06 E4 23  call far 23E4:062A
10A4  BF 0A 10        mov di, 0x100a
10A7  0E              push cs
10A8  57              push di
10A9  9A B7 06 E4 23  call far 23E4:06B7
10AE  9A F8 04 4B 21  call far 214B:04F8
10B3  C7 46 EE 80 00  mov word ptr [bp - 0x12], 0x80
loc_10B8:
10B8  81 7E EE 80 00  cmp word ptr [bp - 0x12], 0x80
10BD  75 A5           jne 0x1064
10BF  8D 7E F0        lea di, [bp - 0x10]
10C2  16              push ss
10C3  57              push di
10C4  8B 46 04        mov ax, word ptr [bp + 4]
10C7  B1 04           mov cl, 4
10C9  D3 E0           shl ax, cl
10CB  C4 3E 68 9B     les di, ptr [0x9b68]
10CF  03 F8           add di, ax
10D1  06              push es
10D2  57              push di
10D3  B8 0F 00        mov ax, 0xf
10D6  50              push ax
10D7  9A 44 06 E4 23  call far 23E4:0644
10DC  C6 06 1A 0C 01  mov byte ptr [0xc1a], 1
loc_10E1:
10E1  89 EC           mov sp, bp
10E3  5D              pop bp
10E4  C2 02 00        ret 2

; ---- routine 1771:10E7  (found by: call, far)
sub_10E7:
10E7  55              push bp
10E8  89 E5           mov bp, sp
10EA  83 EC 06        sub sp, 6
10ED  8B 46 06        mov ax, word ptr [bp + 6]
10F0  BA BF 00        mov dx, 0xbf
10F3  F7 E2           mul dx
10F5  C4 3E 17 A9     les di, ptr [0xa917]
10F9  03 F8           add di, ax
10FB  89 7E FA        mov word ptr [bp - 6], di
10FE  8C 46 FC        mov word ptr [bp - 4], es
1101  C4 7E FA        les di, ptr [bp - 6]
1104  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
1108  30 E4           xor ah, ah
110A  8B D0           mov dx, ax
110C  B8 05 00        mov ax, 5
110F  2B C2           sub ax, dx
1111  8B C8           mov cx, ax
1113  C4 7E FA        les di, ptr [bp - 6]
1116  26 8A 45 2A     mov al, byte ptr es:[di + 0x2a]
111A  30 E4           xor ah, ah
111C  8B D0           mov dx, ax
111E  B8 21 00        mov ax, 0x21
1121  2B C2           sub ax, dx
1123  F7 E9           imul cx
1125  8B C8           mov cx, ax
1127  C4 7E FA        les di, ptr [bp - 6]
112A  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
112E  30 E4           xor ah, ah
1130  8B D0           mov dx, ax
1132  B8 81 00        mov ax, 0x81
1135  2B C2           sub ax, dx
1137  03 C1           add ax, cx
1139  99              cdq
113A  B9 02 00        mov cx, 2
113D  F7 F9           idiv cx
113F  89 46 FE        mov word ptr [bp - 2], ax
1142  8B 46 FE        mov ax, word ptr [bp - 2]
1145  89 EC           mov sp, bp
1147  5D              pop bp
1148  CA 02 00        retf 2

; ---- routine 1771:114B  (found by: call)
sub_114B:
114B  55              push bp
114C  89 E5           mov bp, sp
114E  83 EC 12        sub sp, 0x12
1151  8B 46 06        mov ax, word ptr [bp + 6]
1154  BA BF 00        mov dx, 0xbf
1157  F7 E2           mul dx
1159  C4 3E 17 A9     les di, ptr [0xa917]
115D  03 F8           add di, ax
115F  89 7E F6        mov word ptr [bp - 0xa], di
1162  8C 46 F8        mov word ptr [bp - 8], es
1165  C4 3E 23 A9     les di, ptr [0xa923]
1169  89 7E F2        mov word ptr [bp - 0xe], di
116C  8C 46 F4        mov word ptr [bp - 0xc], es
116F  31 C0           xor ax, ax
1171  89 46 FA        mov word ptr [bp - 6], ax
1174  C7 46 FC 01 00  mov word ptr [bp - 4], 1
1179  EB 03           jmp 0x117e
loc_117B:
117B  FF 46 FC        inc word ptr [bp - 4]
loc_117E:
117E  8B 46 FC        mov ax, word ptr [bp - 4]
1181  BA BF 00        mov dx, 0xbf
1184  F7 E2           mul dx
1186  C4 3E 17 A9     les di, ptr [0xa917]
118A  03 F8           add di, ax
118C  89 7E EE        mov word ptr [bp - 0x12], di
118F  8C 46 F0        mov word ptr [bp - 0x10], es
1192  8B 46 06        mov ax, word ptr [bp + 6]
1195  BA BF 00        mov dx, 0xbf
1198  F7 E2           mul dx
119A  C4 3E 17 A9     les di, ptr [0xa917]
119E  03 F8           add di, ax
11A0  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
11A4  C4 7E EE        les di, ptr [bp - 0x12]
11A7  26 3A 45 2C     cmp al, byte ptr es:[di + 0x2c]
11AB  75 1E           jne 0x11cb
11AD  8B 46 06        mov ax, word ptr [bp + 6]
11B0  BA BF 00        mov dx, 0xbf
11B3  F7 E2           mul dx
11B5  C4 3E 17 A9     les di, ptr [0xa917]
11B9  03 F8           add di, ax
11BB  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
11BF  C4 7E EE        les di, ptr [bp - 0x12]
11C2  26 3A 45 2B     cmp al, byte ptr es:[di + 0x2b]
11C6  72 03           jb 0x11cb
11C8  FF 46 FA        inc word ptr [bp - 6]
loc_11CB:
11CB  81 7E FC 80 00  cmp word ptr [bp - 4], 0x80
11D0  75 A9           jne 0x117b
11D2  8B 46 FA        mov ax, word ptr [bp - 6]
11D5  89 46 FE        mov word ptr [bp - 2], ax
11D8  8B 46 FE        mov ax, word ptr [bp - 2]
11DB  89 EC           mov sp, bp
11DD  5D              pop bp
11DE  CA 02 00        retf 2

; ---- routine 1771:11E1  (found by: call)
sub_11E1:
11E1  55              push bp
11E2  89 E5           mov bp, sp
11E4  83 EC 02        sub sp, 2
11E7  C7 46 FE 01 00  mov word ptr [bp - 2], 1
11EC  EB 03           jmp 0x11f1
loc_11EE:
11EE  FF 46 FE        inc word ptr [bp - 2]
loc_11F1:
11F1  8B 7E FE        mov di, word ptr [bp - 2]
11F4  D1 E7           shl di, 1
11F6  D1 E7           shl di, 1
11F8  8B 85 47 9B     mov ax, word ptr [di - 0x64b9]
11FC  99              cdq
11FD  B9 04 00        mov cx, 4
1200  F7 F9           idiv cx
1202  8B 7E FE        mov di, word ptr [bp - 2]
1205  D1 E7           shl di, 1
1207  D1 E7           shl di, 1
1209  89 85 47 9B     mov word ptr [di - 0x64b9], ax
120D  83 7E FE 03     cmp word ptr [bp - 2], 3
1211  75 DB           jne 0x11ee
1213  31 C0           xor ax, ax
1215  89 46 FE        mov word ptr [bp - 2], ax
1218  EB 03           jmp 0x121d
loc_121A:
121A  FF 46 FE        inc word ptr [bp - 2]
loc_121D:
121D  8B 7E FE        mov di, word ptr [bp - 2]
1220  D1 E7           shl di, 1
1222  D1 E7           shl di, 1
1224  83 BD 47 9B 01  cmp word ptr [di - 0x64b9], 1
1229  7D 0F           jge 0x123a
122B  8B 7E FE        mov di, word ptr [bp - 2]
122E  D1 E7           shl di, 1
1230  D1 E7           shl di, 1
1232  C7 85 47 9B 01 00 mov word ptr [di - 0x64b9], 1
1238  EB 1C           jmp 0x1256
loc_123A:
123A  8B 7E FE        mov di, word ptr [bp - 2]
123D  D1 E7           shl di, 1
123F  D1 E7           shl di, 1
1241  81 BD 47 9B 00 01 cmp word ptr [di - 0x64b9], 0x100
1247  7E 0D           jle 0x1256
1249  8B 7E FE        mov di, word ptr [bp - 2]
124C  D1 E7           shl di, 1
124E  D1 E7           shl di, 1
1250  C7 85 47 9B 00 01 mov word ptr [di - 0x64b9], 0x100
loc_1256:
1256  8B 46 04        mov ax, word ptr [bp + 4]
1259  03 46 FE        add ax, word ptr [bp - 2]
125C  50              push ax
125D  B8 0A 00        mov ax, 0xa
1260  50              push ax
1261  8B 7E FE        mov di, word ptr [bp - 2]
1264  D1 E7           shl di, 1
1266  D1 E7           shl di, 1
1268  8B 85 47 9B     mov ax, word ptr [di - 0x64b9]
126C  B9 19 00        mov cx, 0x19
126F  F7 E9           imul cx
1271  99              cdq
1272  B9 00 01        mov cx, 0x100
1275  F7 F9           idiv cx
1277  50              push ax
1278  9A C5 13 4B 21  call far 214B:13C5
127D  83 7E FE 03     cmp word ptr [bp - 2], 3
1281  75 97           jne 0x121a
1283  89 EC           mov sp, bp
1285  5D              pop bp
1286  C2 02 00        ret 2

; ---- routine 1771:1289  (found by: call)
sub_1289:
1289  55              push bp
128A  89 E5           mov bp, sp
128C  83 EC 0E        sub sp, 0xe
128F  BF 45 9B        mov di, 0x9b45
1292  1E              push ds
1293  57              push di
1294  B8 10 00        mov ax, 0x10
1297  50              push ax
1298  31 C0           xor ax, ax
129A  50              push ax
129B  9A 18 00 4B 21  call far 214B:0018
12A0  C7 46 FE 01 00  mov word ptr [bp - 2], 1
12A5  EB 03           jmp 0x12aa
loc_12A7:
12A7  FF 46 FE        inc word ptr [bp - 2]
loc_12AA:
12AA  8A 46 04        mov al, byte ptr [bp + 4]
12AD  98              cwde
12AE  8B F8           mov di, ax
12B0  D1 E7           shl di, 1
12B2  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
12B6  BA BF 00        mov dx, 0xbf
12B9  F7 E2           mul dx
12BB  C4 3E 17 A9     les di, ptr [0xa917]
12BF  03 F8           add di, ax
12C1  89 7E F6        mov word ptr [bp - 0xa], di
12C4  8C 46 F8        mov word ptr [bp - 8], es
12C7  8B 46 FE        mov ax, word ptr [bp - 2]
12CA  D1 E0           shl ax, 1
12CC  C4 7E F6        les di, ptr [bp - 0xa]
12CF  03 F8           add di, ax
12D1  26 FF 75 FE     push word ptr es:[di - 2]
12D5  8A 46 04        mov al, byte ptr [bp + 4]
12D8  98              cwde
12D9  8B F8           mov di, ax
12DB  D1 E7           shl di, 1
12DD  FF B5 34 9B     push word ptr [di - 0x64cc]
12E1  0E              push cs
12E2  E8 9D 27        call 0x3a82
12E5  89 46 FC        mov word ptr [bp - 4], ax
12E8  8B 46 FE        mov ax, word ptr [bp - 2]
12EB  D1 E0           shl ax, 1
12ED  C4 7E F6        les di, ptr [bp - 0xa]
12F0  03 F8           add di, ax
12F2  26 8B 45 FE     mov ax, word ptr es:[di - 2]
12F6  BA 14 00        mov dx, 0x14
12F9  F7 E2           mul dx
12FB  C4 3E 1B A9     les di, ptr [0xa91b]
12FF  03 F8           add di, ax
1301  26 8B 45 12     mov ax, word ptr es:[di + 0x12]
1305  2D 37 00        sub ax, 0x37
1308  89 46 FA        mov word ptr [bp - 6], ax
130B  81 7E FA 88 13  cmp word ptr [bp - 6], 0x1388
1310  7E 05           jle 0x1317
1312  81 6E FA 10 27  sub word ptr [bp - 6], 0x2710
loc_1317:
1317  83 46 FA 64     add word ptr [bp - 6], 0x64
131B  8B 46 FE        mov ax, word ptr [bp - 2]
131E  D1 E0           shl ax, 1
1320  C4 7E F6        les di, ptr [bp - 0xa]
1323  03 F8           add di, ax
1325  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1329  BA 14 00        mov dx, 0x14
132C  F7 E2           mul dx
132E  C4 3E 1B A9     les di, ptr [0xa91b]
1332  03 F8           add di, ax
1334  89 7E F2        mov word ptr [bp - 0xe], di
1337  8C 46 F4        mov word ptr [bp - 0xc], es
133A  C4 7E F2        les di, ptr [bp - 0xe]
133D  26 8A 45 06     mov al, byte ptr es:[di + 6]
1341  30 E4           xor ah, ah
1343  8B F8           mov di, ax
1345  80 BD 7C 0D 04  cmp byte ptr [di + 0xd7c], 4
134A  73 20           jae 0x136c
134C  8B 56 FA        mov dx, word ptr [bp - 6]
134F  C4 7E F2        les di, ptr [bp - 0xe]
1352  26 8A 45 06     mov al, byte ptr es:[di + 6]
1356  30 E4           xor ah, ah
1358  8B F8           mov di, ax
135A  8A 85 7C 0D     mov al, byte ptr [di + 0xd7c]
135E  30 E4           xor ah, ah
1360  8B F8           mov di, ax
1362  D1 E7           shl di, 1
1364  D1 E7           shl di, 1
1366  01 95 47 9B     add word ptr [di - 0x64b9], dx
136A  EB 4E           jmp 0x13ba
loc_136C:
136C  8B 46 FA        mov ax, word ptr [bp - 6]
136F  99              cdq
1370  B9 02 00        mov cx, 2
1373  F7 F9           idiv cx
1375  89 46 FA        mov word ptr [bp - 6], ax
1378  8B 56 FA        mov dx, word ptr [bp - 6]
137B  C4 7E F2        les di, ptr [bp - 0xe]
137E  26 8A 45 06     mov al, byte ptr es:[di + 6]
1382  30 E4           xor ah, ah
1384  8B F8           mov di, ax
1386  8A 85 7C 0D     mov al, byte ptr [di + 0xd7c]
138A  30 E4           xor ah, ah
138C  2D 03 00        sub ax, 3
138F  8B F8           mov di, ax
1391  D1 E7           shl di, 1
1393  D1 E7           shl di, 1
1395  01 95 47 9B     add word ptr [di - 0x64b9], dx
1399  8B 56 FA        mov dx, word ptr [bp - 6]
139C  C4 7E F2        les di, ptr [bp - 0xe]
139F  26 8A 45 06     mov al, byte ptr es:[di + 6]
13A3  30 E4           xor ah, ah
13A5  8B F8           mov di, ax
13A7  8A 85 7C 0D     mov al, byte ptr [di + 0xd7c]
13AB  30 E4           xor ah, ah
13AD  2D 02 00        sub ax, 2
13B0  8B F8           mov di, ax
13B2  D1 E7           shl di, 1
13B4  D1 E7           shl di, 1
13B6  01 95 47 9B     add word ptr [di - 0x64b9], dx
loc_13BA:
13BA  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
13BE  74 03           je 0x13c3
13C0  E9 E4 FE        jmp 0x12a7
loc_13C3:
13C3  B8 14 00        mov ax, 0x14
13C6  50              push ax
13C7  E8 17 FE        call 0x11e1
13CA  89 EC           mov sp, bp
13CC  5D              pop bp
13CD  C2 02 00        ret 2

; ---- routine 1771:13D0  (found by: call)
sub_13D0:
13D0  55              push bp
13D1  89 E5           mov bp, sp
13D3  83 EC 0A        sub sp, 0xa
13D6  8B 46 04        mov ax, word ptr [bp + 4]
13D9  BA BF 00        mov dx, 0xbf
13DC  F7 E2           mul dx
13DE  C4 3E 17 A9     les di, ptr [0xa917]
13E2  03 F8           add di, ax
13E4  89 7E FA        mov word ptr [bp - 6], di
13E7  8C 46 FC        mov word ptr [bp - 4], es
13EA  C7 06 5A 9B 06 00 mov word ptr [0x9b5a], 6
13F0  C7 06 5C 9B 06 00 mov word ptr [0x9b5c], 6
13F6  C7 06 5E 9B 06 00 mov word ptr [0x9b5e], 6
13FC  C7 06 60 9B 06 00 mov word ptr [0x9b60], 6
1402  C7 06 62 9B 06 00 mov word ptr [0x9b62], 6
1408  C7 06 64 9B 06 00 mov word ptr [0x9b64], 6
140E  C7 46 FE 01 00  mov word ptr [bp - 2], 1
1413  EB 03           jmp 0x1418
loc_1415:
1415  FF 46 FE        inc word ptr [bp - 2]
loc_1418:
1418  8B 46 FE        mov ax, word ptr [bp - 2]
141B  D1 E0           shl ax, 1
141D  C4 7E FA        les di, ptr [bp - 6]
1420  03 F8           add di, ax
1422  26 FF 75 FE     push word ptr es:[di - 2]
1426  0E              push cs
1427  E8 EC 1D        call 0x3216
142A  08 C0           or al, al
142C  74 03           je 0x1431
142E  E9 8C 00        jmp 0x14bd
loc_1431:
1431  8B 46 FE        mov ax, word ptr [bp - 2]
1434  D1 E0           shl ax, 1
1436  C4 7E FA        les di, ptr [bp - 6]
1439  03 F8           add di, ax
143B  26 8B 45 FE     mov ax, word ptr es:[di - 2]
143F  BA 14 00        mov dx, 0x14
1442  F7 E2           mul dx
1444  C4 3E 1B A9     les di, ptr [0xa91b]
1448  03 F8           add di, ax
144A  89 7E F6        mov word ptr [bp - 0xa], di
144D  8C 46 F8        mov word ptr [bp - 8], es
1450  C4 7E F6        les di, ptr [bp - 0xa]
1453  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
1457  98              cwde
1458  99              cdq
1459  52              push dx
145A  50              push ax
145B  B8 20 00        mov ax, 0x20
145E  31 D2           xor dx, dx
1460  52              push dx
1461  50              push ax
1462  9A 1C 0D 4B 21  call far 214B:0D1C
1467  01 06 5A 9B     add word ptr [0x9b5a], ax
146B  C4 7E F6        les di, ptr [bp - 0xa]
146E  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
1473  7E 0C           jle 0x1481
1475  C4 7E F6        les di, ptr [bp - 0xa]
1478  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
147C  98              cwde
147D  01 06 5C 9B     add word ptr [0x9b5c], ax
loc_1481:
1481  8B 46 FE        mov ax, word ptr [bp - 2]
1484  D1 E0           shl ax, 1
1486  C4 7E FA        les di, ptr [bp - 6]
1489  03 F8           add di, ax
148B  26 FF 75 FE     push word ptr es:[di - 2]
148F  0E              push cs
1490  E8 68 1B        call 0x2ffb
1493  30 E4           xor ah, ah
1495  01 06 5E 9B     add word ptr [0x9b5e], ax
1499  C4 7E F6        les di, ptr [bp - 0xa]
149C  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
14A0  98              cwde
14A1  01 06 60 9B     add word ptr [0x9b60], ax
14A5  C4 7E F6        les di, ptr [bp - 0xa]
14A8  26 8A 45 01     mov al, byte ptr es:[di + 1]
14AC  30 E4           xor ah, ah
14AE  01 06 62 9B     add word ptr [0x9b62], ax
14B2  C4 7E F6        les di, ptr [bp - 0xa]
14B5  26 8B 45 08     mov ax, word ptr es:[di + 8]
14B9  01 06 64 9B     add word ptr [0x9b64], ax
loc_14BD:
14BD  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
14C1  74 03           je 0x14c6
14C3  E9 4F FF        jmp 0x1415
loc_14C6:
14C6  A1 5A 9B        mov ax, word ptr [0x9b5a]
14C9  31 D2           xor dx, dx
14CB  B9 0B 00        mov cx, 0xb
14CE  F7 F1           div cx
14D0  A3 5A 9B        mov word ptr [0x9b5a], ax
14D3  A1 5C 9B        mov ax, word ptr [0x9b5c]
14D6  31 D2           xor dx, dx
14D8  B9 0B 00        mov cx, 0xb
14DB  F7 F1           div cx
14DD  A3 5C 9B        mov word ptr [0x9b5c], ax
14E0  A1 5E 9B        mov ax, word ptr [0x9b5e]
14E3  31 D2           xor dx, dx
14E5  B9 0B 00        mov cx, 0xb
14E8  F7 F1           div cx
14EA  A3 5E 9B        mov word ptr [0x9b5e], ax
14ED  A1 60 9B        mov ax, word ptr [0x9b60]
14F0  31 D2           xor dx, dx
14F2  B9 0B 00        mov cx, 0xb
14F5  F7 F1           div cx
14F7  A3 60 9B        mov word ptr [0x9b60], ax
14FA  A1 62 9B        mov ax, word ptr [0x9b62]
14FD  31 D2           xor dx, dx
14FF  B9 0B 00        mov cx, 0xb
1502  F7 F1           div cx
1504  A3 62 9B        mov word ptr [0x9b62], ax
1507  A1 64 9B        mov ax, word ptr [0x9b64]
150A  31 D2           xor dx, dx
150C  B9 0B 00        mov cx, 0xb
150F  F7 F1           div cx
1511  A3 64 9B        mov word ptr [0x9b64], ax
1514  83 3E 5A 9B 01  cmp word ptr [0x9b5a], 1
1519  73 06           jae 0x1521
151B  C7 06 5A 9B 01 00 mov word ptr [0x9b5a], 1
loc_1521:
1521  89 EC           mov sp, bp
1523  5D              pop bp
1524  C2 02 00        ret 2

