; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 2 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:0955  (found by: call)
sub_0955:
0955  55              push bp
0956  89 E5           mov bp, sp
0958  BF E0 06        mov di, 0x6e0
095B  1E              push ds
095C  57              push di
095D  BF 6E A9        mov di, 0xa96e
0960  1E              push ds
0961  57              push di
0962  9A 29 03 4B 21  call far 214B:0329
0967  B0 05           mov al, 5
0969  50              push ax
096A  A0 6D 06        mov al, byte ptr [0x66d]
096D  98              cwde
096E  BA 05 00        mov dx, 5
0971  F7 E2           mul dx
0973  8B F8           mov di, ax
0975  81 C7 D6 06     add di, 0x6d6
0979  1E              push ds
097A  57              push di
097B  B0 19           mov al, 0x19
097D  50              push ax
097E  B0 2D           mov al, 0x2d
0980  50              push ax
0981  BF 6E A9        mov di, 0xa96e
0984  1E              push ds
0985  57              push di
0986  9A C8 02 4B 21  call far 214B:02C8
098B  C4 3E 6E A9     les di, ptr [0xa96e]
098F  81 C7 00 0F     add di, 0xf00
0993  06              push es
0994  57              push di
0995  C4 3E 6A A9     les di, ptr [0xa96a]
0999  81 C7 00 0F     add di, 0xf00
099D  06              push es
099E  57              push di
099F  B8 A0 00        mov ax, 0xa0
09A2  50              push ax
09A3  9A 3C 00 4B 21  call far 214B:003C
09A8  C4 7E 04        les di, ptr [bp + 4]
09AB  06              push es
09AC  57              push di
09AD  B0 50           mov al, 0x50
09AF  50              push ax
09B0  B0 24           mov al, 0x24
09B2  50              push ax
09B3  B0 2D           mov al, 0x2d
09B5  50              push ax
09B6  B0 19           mov al, 0x19
09B8  50              push ax
09B9  9A 86 10 4B 21  call far 214B:1086
09BE  89 EC           mov sp, bp
09C0  5D              pop bp
09C1  C2 04 00        ret 4

; ---- routine 0791:09C4  (found by: call)
sub_09C4:
09C4  55              push bp
09C5  89 E5           mov bp, sp
09C7  81 EC 02 01     sub sp, 0x102
09CB  C4 7E 04        les di, ptr [bp + 4]
09CE  06              push es
09CF  57              push di
09D0  E8 82 FF        call 0x955
09D3  C6 46 FE 00     mov byte ptr [bp - 2], 0
09D7  80 3E 77 A9 1B  cmp byte ptr [0xa977], 0x1b
09DC  75 08           jne 0x9e6
09DE  C7 06 65 A9 FF 00 mov word ptr [0xa965], 0xff
09E4  EB 64           jmp 0xa4a
loc_09E6:
09E6  80 7E 08 00     cmp byte ptr [bp + 8], 0
09EA  74 30           je 0xa1c
09EC  8D BE FE FE     lea di, [bp - 0x102]
09F0  16              push ss
09F1  57              push di
09F2  C4 7E 04        les di, ptr [bp + 4]
09F5  06              push es
09F6  57              push di
09F7  9A 2A 06 E4 23  call far 23E4:062A
09FC  A0 6D 06        mov al, byte ptr [0x66d]
09FF  98              cwde
0A00  BA 05 00        mov dx, 5
0A03  F7 E2           mul dx
0A05  8B F8           mov di, ax
0A07  81 C7 D6 06     add di, 0x6d6
0A0B  1E              push ds
0A0C  57              push di
0A0D  9A B7 06 E4 23  call far 23E4:06B7
0A12  9A F5 1B 4B 21  call far 214B:1BF5
0A17  88 46 FE        mov byte ptr [bp - 2], al
0A1A  EB 2E           jmp 0xa4a
loc_0A1C:
0A1C  8D BE FE FE     lea di, [bp - 0x102]
0A20  16              push ss
0A21  57              push di
0A22  C4 7E 04        les di, ptr [bp + 4]
0A25  06              push es
0A26  57              push di
0A27  9A 2A 06 E4 23  call far 23E4:062A
0A2C  A0 6D 06        mov al, byte ptr [0x66d]
0A2F  98              cwde
0A30  BA 05 00        mov dx, 5
0A33  F7 E2           mul dx
0A35  8B F8           mov di, ax
0A37  81 C7 D6 06     add di, 0x6d6
0A3B  1E              push ds
0A3C  57              push di
0A3D  9A B7 06 E4 23  call far 23E4:06B7
0A42  9A B7 1B 4B 21  call far 214B:1BB7
0A47  88 46 FE        mov byte ptr [bp - 2], al
loc_0A4A:
0A4A  80 7E FE 00     cmp byte ptr [bp - 2], 0
0A4E  74 0A           je 0xa5a
0A50  8A 46 08        mov al, byte ptr [bp + 8]
0A53  50              push ax
0A54  E8 63 FD        call 0x7ba
0A57  88 46 FE        mov byte ptr [bp - 2], al
loc_0A5A:
0A5A  8A 46 FE        mov al, byte ptr [bp - 2]
0A5D  88 46 FF        mov byte ptr [bp - 1], al
0A60  8A 46 FF        mov al, byte ptr [bp - 1]
0A63  89 EC           mov sp, bp
0A65  5D              pop bp
0A66  C2 06 00        ret 6
; data (not reached as code), 2 bytes
0A69                  db 01 2D   ; .-

; ---- routine 0791:0A6B  (found by: call)
sub_0A6B:
0A6B  55              push bp
0A6C  89 E5           mov bp, sp
0A6E  81 EC 0E 02     sub sp, 0x20e
0A72  C4 3E 23 A9     les di, ptr [0xa923]
0A76  89 7E F2        mov word ptr [bp - 0xe], di
0A79  8C 46 F4        mov word ptr [bp - 0xc], es
0A7C  A0 26 83        mov al, byte ptr [0x8326]
0A7F  A2 6D 06        mov byte ptr [0x66d], al
0A82  80 3E 6D 06 00  cmp byte ptr [0x66d], 0
0A87  74 12           je 0xa9b
0A89  C4 7E F2        les di, ptr [bp - 0xe]
0A8C  26 8D 85 BD 00  lea ax, es:[di + 0xbd]
0A91  8C C2           mov dx, es
0A93  89 46 F6        mov word ptr [bp - 0xa], ax
0A96  89 56 F8        mov word ptr [bp - 8], dx
0A99  EB 0F           jmp 0xaaa
loc_0A9B:
0A9B  C4 7E F2        les di, ptr [bp - 0xe]
0A9E  26 8D 45 6C     lea ax, es:[di + 0x6c]
0AA2  8C C2           mov dx, es
0AA4  89 46 F6        mov word ptr [bp - 0xa], ax
0AA7  89 56 F8        mov word ptr [bp - 8], dx
loc_0AAA:
0AAA  BF 69 0A        mov di, 0xa69
0AAD  0E              push cs
0AAE  57              push di
0AAF  C4 7E F6        les di, ptr [bp - 0xa]
0AB2  06              push es
0AB3  57              push di
0AB4  9A E3 06 E4 23  call far 23E4:06E3
0AB9  89 46 FE        mov word ptr [bp - 2], ax
0ABC  83 7E FE 00     cmp word ptr [bp - 2], 0
0AC0  75 03           jne 0xac5
0AC2  E9 7E 00        jmp 0xb43
loc_0AC5:
0AC5  C4 7E F6        les di, ptr [bp - 0xa]
0AC8  26 8A 05        mov al, byte ptr es:[di]
0ACB  30 E4           xor ah, ah
0ACD  3B 46 FE        cmp ax, word ptr [bp - 2]
0AD0  76 71           jbe 0xb43
0AD2  8D BE F2 FE     lea di, [bp - 0x10e]
0AD6  16              push ss
0AD7  57              push di
0AD8  C4 7E F6        les di, ptr [bp - 0xa]
0ADB  06              push es
0ADC  57              push di
0ADD  8B 46 FE        mov ax, word ptr [bp - 2]
0AE0  40              inc ax
0AE1  50              push ax
0AE2  C4 7E F6        les di, ptr [bp - 0xa]
0AE5  26 8A 05        mov al, byte ptr es:[di]
0AE8  30 E4           xor ah, ah
0AEA  2B 46 FE        sub ax, word ptr [bp - 2]
0AED  50              push ax
0AEE  9A 76 06 E4 23  call far 23E4:0676
0AF3  8D 7E FA        lea di, [bp - 6]
0AF6  16              push ss
0AF7  57              push di
0AF8  9A 41 13 E4 23  call far 23E4:1341
0AFD  89 46 FC        mov word ptr [bp - 4], ax
0B00  83 7E FA 00     cmp word ptr [bp - 6], 0
0B04  75 3D           jne 0xb43
0B06  8D BE F2 FE     lea di, [bp - 0x10e]
0B0A  16              push ss
0B0B  57              push di
0B0C  C4 7E F6        les di, ptr [bp - 0xa]
0B0F  06              push es
0B10  57              push di
0B11  B8 01 00        mov ax, 1
0B14  50              push ax
0B15  FF 76 FE        push word ptr [bp - 2]
0B18  9A 76 06 E4 23  call far 23E4:0676
0B1D  8D BE F2 FD     lea di, [bp - 0x20e]
0B21  16              push ss
0B22  57              push di
0B23  8B 46 FC        mov ax, word ptr [bp - 4]
0B26  40              inc ax
0B27  31 D2           xor dx, dx
0B29  52              push dx
0B2A  50              push ax
0B2B  9A DA 09 4B 21  call far 214B:09DA
0B30  9A B7 06 E4 23  call far 23E4:06B7
0B35  C4 7E F6        les di, ptr [bp - 0xa]
0B38  06              push es
0B39  57              push di
0B3A  B8 50 00        mov ax, 0x50
0B3D  50              push ax
0B3E  9A 44 06 E4 23  call far 23E4:0644
loc_0B43:
0B43  B0 00           mov al, 0
0B45  50              push ax
0B46  C4 7E F6        les di, ptr [bp - 0xa]
0B49  06              push es
0B4A  57              push di
0B4B  E8 76 FE        call 0x9c4
0B4E  08 C0           or al, al
0B50  75 0C           jne 0xb5e
0B52  B0 00           mov al, 0
0B54  50              push ax
0B55  9A 69 18 4B 21  call far 214B:1869
0B5A  08 C0           or al, al
0B5C  75 E5           jne 0xb43
loc_0B5E:
0B5E  9A 36 1A 4B 21  call far 214B:1A36
0B63  89 EC           mov sp, bp
0B65  5D              pop bp
0B66  C3              ret
; data (not reached as code), 21 bytes
0B67                  pstr 'Do you want '
0B74                  pstr '? (Y/N)'

; ---- routine 0791:0B7C  (found by: call)
sub_0B7C:
0B7C  55              push bp
0B7D  89 E5           mov bp, sp
0B7F  81 EC 2A 01     sub sp, 0x12a
0B83  C4 7E 04        les di, ptr [bp + 4]
0B86  06              push es
0B87  57              push di
0B88  8D 7E D6        lea di, [bp - 0x2a]
0B8B  16              push ss
0B8C  57              push di
0B8D  B8 28 00        mov ax, 0x28
0B90  50              push ax
0B91  9A 44 06 E4 23  call far 23E4:0644
0B96  C6 46 FF 00     mov byte ptr [bp - 1], 0
0B9A  9A 25 06 4B 21  call far 214B:0625
0B9F  B0 19           mov al, 0x19
0BA1  50              push ax
0BA2  8D BE D6 FE     lea di, [bp - 0x12a]
0BA6  16              push ss
0BA7  57              push di
0BA8  BF 67 0B        mov di, 0xb67
0BAB  0E              push cs
0BAC  57              push di
0BAD  9A 2A 06 E4 23  call far 23E4:062A
0BB2  8D 7E D6        lea di, [bp - 0x2a]
0BB5  16              push ss
0BB6  57              push di
0BB7  9A B7 06 E4 23  call far 23E4:06B7
0BBC  BF 74 0B        mov di, 0xb74
0BBF  0E              push cs
0BC0  57              push di
0BC1  9A B7 06 E4 23  call far 23E4:06B7
0BC6  BF 6A A9        mov di, 0xa96a
0BC9  1E              push ds
0BCA  57              push di
0BCB  9A 50 03 4B 21  call far 214B:0350
0BD0  B8 58 02        mov ax, 0x258
0BD3  50              push ax
0BD4  E8 57 C0        call 0xffffcc2e
0BD7  9A 43 06 4B 21  call far 214B:0643
0BDC  9A 23 07 4B 21  call far 214B:0723
0BE1  08 C0           or al, al
0BE3  75 02           jne 0xbe7
0BE5  EB 1B           jmp 0xc02
loc_0BE7:
0BE7  9A DD 08 4B 21  call far 214B:08DD
0BEC  A0 76 A9        mov al, byte ptr [0xa976]
0BEF  50              push ax
0BF0  9A B2 19 E4 23  call far 23E4:19B2
0BF5  3C 59           cmp al, 0x59
0BF7  74 04           je 0xbfd
0BF9  B0 00           mov al, 0
0BFB  EB 02           jmp 0xbff
loc_0BFD:
0BFD  B0 01           mov al, 1
loc_0BFF:
0BFF  88 46 FF        mov byte ptr [bp - 1], al
loc_0C02:
0C02  8A 46 FF        mov al, byte ptr [bp - 1]
0C05  89 EC           mov sp, bp
0C07  5D              pop bp
0C08  C2 04 00        ret 4

; ---- routine 0791:0C0B  (found by: call)
sub_0C0B:
0C0B  55              push bp
0C0C  89 E5           mov bp, sp
0C0E  83 EC 04        sub sp, 4
0C11  C4 3E 23 A9     les di, ptr [0xa923]
0C15  89 7E FC        mov word ptr [bp - 4], di
0C18  8C 46 FE        mov word ptr [bp - 2], es
0C1B  C4 7E FC        les di, ptr [bp - 4]
0C1E  26 80 7D 3F 05  cmp byte ptr es:[di + 0x3f], 5
0C23  73 07           jae 0xc2c
0C25  C4 7E FC        les di, ptr [bp - 4]
0C28  26 FE 45 3F     inc byte ptr es:[di + 0x3f]
loc_0C2C:
0C2C  C4 7E FC        les di, ptr [bp - 4]
0C2F  26 80 7D 3F 02  cmp byte ptr es:[di + 0x3f], 2
0C34  73 08           jae 0xc3e
0C36  C4 7E FC        les di, ptr [bp - 4]
0C39  26 C6 45 3F 02  mov byte ptr es:[di + 0x3f], 2
loc_0C3E:
0C3E  89 EC           mov sp, bp
0C40  5D              pop bp
0C41  C3              ret
; data (not reached as code), 35 bytes
0C42                  pstr 'an action replay'
0C53                  pstr 'to save this goal'

; ---- routine 0791:0C65  (found by: call)
sub_0C65:
0C65  55              push bp
0C66  89 E5           mov bp, sp
0C68  83 EC 08        sub sp, 8
0C6B  C6 06 55 9B 00  mov byte ptr [0x9b55], 0
0C70  C4 3E 23 A9     les di, ptr [0xa923]
0C74  26 80 7D 41 00  cmp byte ptr es:[di + 0x41], 0
0C79  74 13           je 0xc8e
0C7B  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
0C80  74 0F           je 0xc91
0C82  BF 42 0C        mov di, 0xc42
0C85  0E              push cs
0C86  57              push di
0C87  E8 F2 FE        call 0xb7c
0C8A  08 C0           or al, al
0C8C  75 03           jne 0xc91
loc_0C8E:
0C8E  E9 DE 03        jmp 0x106f
loc_0C91:
0C91  C4 3E 23 A9     les di, ptr [0xa923]
0C95  26 80 7D 41 00  cmp byte ptr es:[di + 0x41], 0
0C9A  74 16           je 0xcb2
0C9C  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
0CA1  74 0F           je 0xcb2
0CA3  BF 53 0C        mov di, 0xc53
0CA6  0E              push cs
0CA7  57              push di
0CA8  E8 D1 FE        call 0xb7c
0CAB  08 C0           or al, al
0CAD  74 03           je 0xcb2
0CAF  E8 B9 FD        call 0xa6b
loc_0CB2:
0CB2  C6 06 20 0C 01  mov byte ptr [0xc20], 1
0CB7  C4 3E 23 A9     les di, ptr [0xa923]
0CBB  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
0CBF  A2 3C 7C        mov byte ptr [0x7c3c], al
0CC2  E8 46 FF        call 0xc0b
0CC5  BF 39 84        mov di, 0x8439
0CC8  1E              push ds
0CC9  57              push di
0CCA  BF 3E 7C        mov di, 0x7c3e
0CCD  1E              push ds
0CCE  57              push di
0CCF  B8 FB 07        mov ax, 0x7fb
0CD2  50              push ax
0CD3  9A 5D 02 E4 23  call far 23E4:025D
0CD8  C4 06 30 9B     les ax, ptr [0x9b30]
0CDC  8C C2           mov dx, es
0CDE  A3 34 9B        mov word ptr [0x9b34], ax
0CE1  89 16 36 9B     mov word ptr [0x9b36], dx
0CE5  C6 46 FF 00     mov byte ptr [bp - 1], 0
0CE9  EB 03           jmp 0xcee
loc_0CEB:
0CEB  FE 46 FF        inc byte ptr [bp - 1]
loc_0CEE:
0CEE  8A 46 FF        mov al, byte ptr [bp - 1]
0CF1  98              cwde
0CF2  BA BF 00        mov dx, 0xbf
0CF5  F7 E2           mul dx
0CF7  8B F8           mov di, ax
0CF9  81 C7 34 8C     add di, 0x8c34
0CFD  1E              push ds
0CFE  57              push di
0CFF  8A 46 FF        mov al, byte ptr [bp - 1]
0D02  98              cwde
0D03  8B F8           mov di, ax
0D05  D1 E7           shl di, 1
0D07  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
0D0B  BA BF 00        mov dx, 0xbf
0D0E  F7 E2           mul dx
0D10  C4 3E 17 A9     les di, ptr [0xa917]
0D14  03 F8           add di, ax
0D16  06              push es
0D17  57              push di
0D18  B8 BF 00        mov ax, 0xbf
0D1B  50              push ax
0D1C  9A 5D 02 E4 23  call far 23E4:025D
0D21  8A 46 FF        mov al, byte ptr [bp - 1]
0D24  98              cwde
0D25  8B F8           mov di, ax
0D27  D1 E7           shl di, 1
0D29  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
0D2D  BA BF 00        mov dx, 0xbf
0D30  F7 E2           mul dx
0D32  C4 3E 17 A9     les di, ptr [0xa917]
0D36  03 F8           add di, ax
0D38  89 7E F9        mov word ptr [bp - 7], di
0D3B  8C 46 FB        mov word ptr [bp - 5], es
0D3E  8A 46 FF        mov al, byte ptr [bp - 1]
0D41  98              cwde
0D42  BA 03 00        mov dx, 3
0D45  F7 E2           mul dx
0D47  8B F8           mov di, ax
0D49  81 C7 30 99     add di, 0x9930
0D4D  1E              push ds
0D4E  57              push di
0D4F  C4 7E F9        les di, ptr [bp - 7]
0D52  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0D56  30 E4           xor ah, ah
0D58  BA 03 00        mov dx, 3
0D5B  F7 E2           mul dx
0D5D  C4 3E 1F A9     les di, ptr [0xa91f]
0D61  03 F8           add di, ax
0D63  06              push es
0D64  57              push di
0D65  B8 03 00        mov ax, 3
0D68  50              push ax
0D69  9A 5D 02 E4 23  call far 23E4:025D
0D6E  8A 46 FF        mov al, byte ptr [bp - 1]
0D71  98              cwde
0D72  BA 0D 00        mov dx, 0xd
0D75  F7 E2           mul dx
0D77  8B F8           mov di, ax
0D79  81 C7 3C 99     add di, 0x993c
0D7D  1E              push ds
0D7E  57              push di
0D7F  C4 7E F9        les di, ptr [bp - 7]
0D82  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0D86  30 E4           xor ah, ah
0D88  BA 0D 00        mov dx, 0xd
0D8B  F7 E2           mul dx
0D8D  C4 3E 74 9B     les di, ptr [0x9b74]
0D91  03 F8           add di, ax
0D93  06              push es
0D94  57              push di
0D95  B8 0C 00        mov ax, 0xc
0D98  50              push ax
0D99  9A 44 06 E4 23  call far 23E4:0644
0D9E  8A 46 FF        mov al, byte ptr [bp - 1]
0DA1  98              cwde
0DA2  8B F8           mov di, ax
0DA4  8A 95 70 99     mov dl, byte ptr [di - 0x6690]
0DA8  C4 7E F9        les di, ptr [bp - 7]
0DAB  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
0DAF  30 E4           xor ah, ah
0DB1  C4 3E 78 9B     les di, ptr [0x9b78]
0DB5  03 F8           add di, ax
0DB7  26 88 15        mov byte ptr es:[di], dl
0DBA  8A 46 FF        mov al, byte ptr [bp - 1]
0DBD  98              cwde
0DBE  8B F8           mov di, ax
0DC0  D1 E7           shl di, 1
0DC2  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
0DC6  BA BF 00        mov dx, 0xbf
0DC9  F7 E2           mul dx
0DCB  C4 3E 17 A9     les di, ptr [0xa917]
0DCF  03 F8           add di, ax
0DD1  89 7E F9        mov word ptr [bp - 7], di
0DD4  8C 46 FB        mov word ptr [bp - 5], es
0DD7  C7 46 FD 01 00  mov word ptr [bp - 3], 1
0DDC  EB 03           jmp 0xde1
loc_0DDE:
0DDE  FF 46 FD        inc word ptr [bp - 3]
loc_0DE1:
0DE1  8B 46 FD        mov ax, word ptr [bp - 3]
0DE4  BA 14 00        mov dx, 0x14
0DE7  F7 E2           mul dx
0DE9  8B C8           mov cx, ax
0DEB  8A 46 FF        mov al, byte ptr [bp - 1]
0DEE  98              cwde
0DEF  BA 90 01        mov dx, 0x190
0DF2  F7 E2           mul dx
0DF4  8B F8           mov di, ax
0DF6  03 F9           add di, cx
0DF8  81 C7 1C 8F     add di, 0x8f1c
0DFC  1E              push ds
0DFD  57              push di
0DFE  8B 46 FD        mov ax, word ptr [bp - 3]
0E01  D1 E0           shl ax, 1
0E03  C4 7E F9        les di, ptr [bp - 7]
0E06  03 F8           add di, ax
0E08  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0E0C  BA 14 00        mov dx, 0x14
0E0F  F7 E2           mul dx
0E11  C4 3E 1B A9     les di, ptr [0xa91b]
0E15  03 F8           add di, ax
0E17  06              push es
0E18  57              push di
0E19  B8 14 00        mov ax, 0x14
0E1C  50              push ax
0E1D  9A 5D 02 E4 23  call far 23E4:025D
0E22  8B 46 FD        mov ax, word ptr [bp - 3]
0E25  BA 0B 00        mov dx, 0xb
0E28  F7 E2           mul dx
0E2A  8B C8           mov cx, ax
0E2C  8A 46 FF        mov al, byte ptr [bp - 1]
0E2F  98              cwde
0E30  BA DC 00        mov dx, 0xdc
0E33  F7 E2           mul dx
0E35  8B F8           mov di, ax
0E37  03 F9           add di, cx
0E39  81 C7 65 95     add di, 0x9565
0E3D  1E              push ds
0E3E  57              push di
0E3F  8B 46 FD        mov ax, word ptr [bp - 3]
0E42  D1 E0           shl ax, 1
0E44  C4 7E F9        les di, ptr [bp - 7]
0E47  03 F8           add di, ax
0E49  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0E4D  BA 0B 00        mov dx, 0xb
0E50  F7 E2           mul dx
0E52  C4 3E 6C 9B     les di, ptr [0x9b6c]
0E56  03 F8           add di, ax
0E58  06              push es
0E59  57              push di
0E5A  B8 0A 00        mov ax, 0xa
0E5D  50              push ax
0E5E  9A 44 06 E4 23  call far 23E4:0644
0E63  8B 46 FD        mov ax, word ptr [bp - 3]
0E66  8B C8           mov cx, ax
0E68  8A 46 FF        mov al, byte ptr [bp - 1]
0E6B  98              cwde
0E6C  BA 14 00        mov dx, 0x14
0E6F  F7 E2           mul dx
0E71  8B F8           mov di, ax
0E73  03 F9           add di, cx
0E75  8A 95 DF 98     mov dl, byte ptr [di - 0x6721]
0E79  8B 46 FD        mov ax, word ptr [bp - 3]
0E7C  D1 E0           shl ax, 1
0E7E  C4 7E F9        les di, ptr [bp - 7]
0E81  03 F8           add di, ax
0E83  26 8B 45 FE     mov ax, word ptr es:[di - 2]
0E87  C4 3E 70 9B     les di, ptr [0x9b70]
0E8B  03 F8           add di, ax
0E8D  26 88 15        mov byte ptr es:[di], dl
0E90  83 7E FD 14     cmp word ptr [bp - 3], 0x14
0E94  74 03           je 0xe99
0E96  E9 45 FF        jmp 0xdde
loc_0E99:
0E99  80 7E FF 01     cmp byte ptr [bp - 1], 1
0E9D  74 03           je 0xea2
0E9F  E9 49 FE        jmp 0xceb
loc_0EA2:
0EA2  BF 6A 7B        mov di, 0x7b6a
0EA5  1E              push ds
0EA6  57              push di
0EA7  BF 7E 7B        mov di, 0x7b7e
0EAA  1E              push ds
0EAB  57              push di
0EAC  B8 14 00        mov ax, 0x14
0EAF  50              push ax
0EB0  9A 5D 02 E4 23  call far 23E4:025D
0EB5  BF 92 7B        mov di, 0x7b92
0EB8  1E              push ds
0EB9  57              push di
0EBA  BF D4 7B        mov di, 0x7bd4
0EBD  1E              push ds
0EBE  57              push di
0EBF  B8 42 00        mov ax, 0x42
0EC2  50              push ax
0EC3  9A 5D 02 E4 23  call far 23E4:025D
0EC8  BF 2E 7C        mov di, 0x7c2e
0ECB  1E              push ds
0ECC  57              push di
0ECD  C4 3E 2A 7C     les di, ptr [0x7c2a]
0ED1  06              push es
0ED2  57              push di
0ED3  B8 08 00        mov ax, 8
0ED6  50              push ax
0ED7  9A 5D 02 E4 23  call far 23E4:025D
0EDC  A0 3C 9A        mov al, byte ptr [0x9a3c]
0EDF  A2 3D 9A        mov byte ptr [0x9a3d], al
0EE2  BF 90 9A        mov di, 0x9a90
0EE5  1E              push ds
0EE6  57              push di
0EE7  BF 40 9A        mov di, 0x9a40
0EEA  1E              push ds
0EEB  57              push di
0EEC  B8 50 00        mov ax, 0x50
0EEF  50              push ax
0EF0  9A 5D 02 E4 23  call far 23E4:025D
0EF5  BF E0 9A        mov di, 0x9ae0
0EF8  1E              push ds
0EF9  57              push di
0EFA  BF 08 9B        mov di, 0x9b08
0EFD  1E              push ds
0EFE  57              push di
0EFF  B8 28 00        mov ax, 0x28
0F02  50              push ax
0F03  9A 5D 02 E4 23  call far 23E4:025D
0F08  A1 38 9B        mov ax, word ptr [0x9b38]
0F0B  A3 3A 9B        mov word ptr [0x9b3a], ax
0F0E  A1 3E 9B        mov ax, word ptr [0x9b3e]
0F11  A3 3C 9B        mov word ptr [0x9b3c], ax
0F14  A0 42 9B        mov al, byte ptr [0x9b42]
0F17  A2 41 9B        mov byte ptr [0x9b41], al
0F1A  A1 74 99        mov ax, word ptr [0x9974]
0F1D  C4 3E 78 A9     les di, ptr [0xa978]
0F21  26 89 05        mov word ptr es:[di], ax
0F24  BF 8C 99        mov di, 0x998c
0F27  1E              push ds
0F28  57              push di
0F29  BF 78 99        mov di, 0x9978
0F2C  1E              push ds
0F2D  57              push di
0F2E  B8 14 00        mov ax, 0x14
0F31  50              push ax
0F32  9A 5D 02 E4 23  call far 23E4:025D
0F37  E8 07 99        call 0xffffa841
0F3A  C4 3E 1E 7C     les di, ptr [0x7c1e]
0F3E  06              push es
0F3F  57              push di
0F40  C4 3E 16 7C     les di, ptr [0x7c16]
0F44  06              push es
0F45  57              push di
0F46  B8 A0 0F        mov ax, 0xfa0
0F49  50              push ax
0F4A  9A 5D 02 E4 23  call far 23E4:025D
0F4F  C7 46 FD 01 00  mov word ptr [bp - 3], 1
0F54  EB 03           jmp 0xf59
loc_0F56:
0F56  FF 46 FD        inc word ptr [bp - 3]
loc_0F59:
0F59  8B 46 FD        mov ax, word ptr [bp - 3]
0F5C  BA 16 00        mov dx, 0x16
0F5F  F7 E2           mul dx
0F61  8B F8           mov di, ax
0F63  81 C7 E8 80     add di, 0x80e8
0F67  89 7E F9        mov word ptr [bp - 7], di
0F6A  8C 5E FB        mov word ptr [bp - 5], ds
0F6D  C4 7E F9        les di, ptr [bp - 7]
0F70  26 8B 05        mov ax, word ptr es:[di]
0F73  3B 06 40 06     cmp ax, word ptr [0x640]
0F77  74 4C           je 0xfc5
0F79  C4 7E F9        les di, ptr [bp - 7]
0F7C  26 80 7D 04 01  cmp byte ptr es:[di + 4], 1
0F81  75 0C           jne 0xf8f
0F83  A0 0B 83        mov al, byte ptr [0x830b]
0F86  C4 7E F9        les di, ptr [bp - 7]
0F89  26 3A 45 06     cmp al, byte ptr es:[di + 6]
0F8D  74 04           je 0xf93
loc_0F8F:
0F8F  B0 00           mov al, 0
0F91  EB 02           jmp 0xf95
loc_0F93:
0F93  B0 01           mov al, 1
loc_0F95:
0F95  30 E4           xor ah, ah
0F97  C4 7E F9        les di, ptr [bp - 7]
0F9A  26 03 45 04     add ax, word ptr es:[di + 4]
0F9E  8B D8           mov bx, ax
0FA0  C4 7E F9        les di, ptr [bp - 7]
0FA3  26 8A 45 01     mov al, byte ptr es:[di + 1]
0FA7  98              cwde
0FA8  D1 E0           shl ax, 1
0FAA  8B C8           mov cx, ax
0FAC  C4 7E F9        les di, ptr [bp - 7]
0FAF  26 8A 05        mov al, byte ptr es:[di]
0FB2  98              cwde
0FB3  BA A0 00        mov dx, 0xa0
0FB6  F7 E2           mul dx
0FB8  C4 3E 16 7C     les di, ptr [0x7c16]
0FBC  03 F8           add di, ax
0FBE  03 F9           add di, cx
0FC0  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_0FC5:
0FC5  83 7E FD 16     cmp word ptr [bp - 3], 0x16
0FC9  75 8B           jne 0xf56
0FCB  A1 EE 82        mov ax, word ptr [0x82ee]
0FCE  3B 06 40 06     cmp ax, word ptr [0x640]
0FD2  74 22           je 0xff6
0FD4  8B 1E F2 82     mov bx, word ptr [0x82f2]
0FD8  A0 EF 82        mov al, byte ptr [0x82ef]
0FDB  98              cwde
0FDC  D1 E0           shl ax, 1
0FDE  8B C8           mov cx, ax
0FE0  A0 EE 82        mov al, byte ptr [0x82ee]
0FE3  98              cwde
0FE4  BA A0 00        mov dx, 0xa0
0FE7  F7 E2           mul dx
0FE9  C4 3E 16 7C     les di, ptr [0x7c16]
0FED  03 F8           add di, ax
0FEF  03 F9           add di, cx
0FF1  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_0FF6:
0FF6  C6 46 FF 00     mov byte ptr [bp - 1], 0
0FFA  EB 03           jmp 0xfff
loc_0FFC:
0FFC  FE 46 FF        inc byte ptr [bp - 1]
loc_0FFF:
0FFF  8A 46 FF        mov al, byte ptr [bp - 1]
1002  98              cwde
1003  8B F8           mov di, ax
1005  D1 E7           shl di, 1
1007  8B F7           mov si, di
1009  D1 E7           shl di, 1
100B  03 FE           add di, si
100D  81 C7 E2 82     add di, 0x82e2
1011  89 7E F9        mov word ptr [bp - 7], di
1014  8C 5E FB        mov word ptr [bp - 5], ds
1017  C4 7E F9        les di, ptr [bp - 7]
101A  26 8B 05        mov ax, word ptr es:[di]
101D  3B 06 40 06     cmp ax, word ptr [0x640]
1021  74 2C           je 0x104f
1023  C4 7E F9        les di, ptr [bp - 7]
1026  26 8B 5D 04     mov bx, word ptr es:[di + 4]
102A  C4 7E F9        les di, ptr [bp - 7]
102D  26 8A 45 01     mov al, byte ptr es:[di + 1]
1031  98              cwde
1032  D1 E0           shl ax, 1
1034  8B C8           mov cx, ax
1036  C4 7E F9        les di, ptr [bp - 7]
1039  26 8A 05        mov al, byte ptr es:[di]
103C  98              cwde
103D  BA A0 00        mov dx, 0xa0
1040  F7 E2           mul dx
1042  C4 3E 16 7C     les di, ptr [0x7c16]
1046  03 F8           add di, ax
1048  03 F9           add di, cx
104A  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_104F:
104F  80 7E FF 01     cmp byte ptr [bp - 1], 1
1053  75 A7           jne 0xffc
1055  BF 30 61        mov di, 0x6130
1058  1E              push ds
1059  57              push di
105A  BF 6A A9        mov di, 0xa96a
105D  1E              push ds
105E  57              push di
105F  9A 29 03 4B 21  call far 214B:0329
1064  FF 36 1B 83     push word ptr [0x831b]
1068  B8 03 00        mov ax, 3
106B  50              push ax
106C  E8 DD F4        call 0x54c
loc_106F:
106F  89 EC           mov sp, bp
1071  5D              pop bp
1072  C3              ret

; ---- routine 0791:1073  (found by: call)
sub_1073:
1073  55              push bp
1074  89 E5           mov bp, sp
1076  80 3E 64 A9 00  cmp byte ptr [0xa964], 0
107B  74 17           je 0x1094
107D  C6 06 2F 83 01  mov byte ptr [0x832f], 1
1082  C6 06 2E 83 04  mov byte ptr [0x832e], 4
1087  C6 06 31 83 09  mov byte ptr [0x8331], 9
108C  C6 06 30 83 0C  mov byte ptr [0x8330], 0xc
1091  E9 94 00        jmp 0x1128
loc_1094:
1094  A1 36 9B        mov ax, word ptr [0x9b36]
1097  BA 03 00        mov dx, 3
109A  F7 E2           mul dx
109C  8B F8           mov di, ax
109E  8A 85 80 9D     mov al, byte ptr [di - 0x6280]
10A2  A2 2F 83        mov byte ptr [0x832f], al
10A5  A1 36 9B        mov ax, word ptr [0x9b36]
10A8  BA 03 00        mov dx, 3
10AB  F7 E2           mul dx
10AD  8B F8           mov di, ax
10AF  8A 85 82 9D     mov al, byte ptr [di - 0x627e]
10B3  A2 31 83        mov byte ptr [0x8331], al
10B6  A1 34 9B        mov ax, word ptr [0x9b34]
10B9  BA 03 00        mov dx, 3
10BC  F7 E2           mul dx
10BE  8B F8           mov di, ax
10C0  8A 85 80 9D     mov al, byte ptr [di - 0x6280]
10C4  A2 2E 83        mov byte ptr [0x832e], al
10C7  A1 34 9B        mov ax, word ptr [0x9b34]
10CA  BA 03 00        mov dx, 3
10CD  F7 E2           mul dx
10CF  8B F8           mov di, ax
10D1  8A 85 82 9D     mov al, byte ptr [di - 0x627e]
10D5  A2 30 83        mov byte ptr [0x8330], al
10D8  A0 2F 83        mov al, byte ptr [0x832f]
10DB  3A 06 2E 83     cmp al, byte ptr [0x832e]
10DF  75 13           jne 0x10f4
10E1  A1 34 9B        mov ax, word ptr [0x9b34]
10E4  BA 03 00        mov dx, 3
10E7  F7 E2           mul dx
10E9  8B F8           mov di, ax
10EB  8A 85 81 9D     mov al, byte ptr [di - 0x627f]
10EF  A2 2E 83        mov byte ptr [0x832e], al
10F2  EB 1A           jmp 0x110e
loc_10F4:
10F4  A0 2F 83        mov al, byte ptr [0x832f]
10F7  3A 06 30 83     cmp al, byte ptr [0x8330]
10FB  75 11           jne 0x110e
10FD  A1 34 9B        mov ax, word ptr [0x9b34]
1100  BA 03 00        mov dx, 3
1103  F7 E2           mul dx
1105  8B F8           mov di, ax
1107  8A 85 81 9D     mov al, byte ptr [di - 0x627f]
110B  A2 30 83        mov byte ptr [0x8330], al
loc_110E:
110E  A0 2E 83        mov al, byte ptr [0x832e]
1111  3A 06 31 83     cmp al, byte ptr [0x8331]
1115  75 11           jne 0x1128
1117  A1 36 9B        mov ax, word ptr [0x9b36]
111A  BA 03 00        mov dx, 3
111D  F7 E2           mul dx
111F  8B F8           mov di, ax
1121  8A 85 81 9D     mov al, byte ptr [di - 0x627f]
1125  A2 31 83        mov byte ptr [0x8331], al
loc_1128:
1128  89 EC           mov sp, bp
112A  5D              pop bp
112B  C3              ret

; ---- routine 0791:112C  (found by: far)
sub_112C:
112C  55              push bp
112D  89 E5           mov bp, sp
112F  83 EC 0E        sub sp, 0xe
1132  80 3E 76 A9 A2  cmp byte ptr [0xa976], 0xa2
1137  74 04           je 0x113d
1139  B0 00           mov al, 0
113B  EB 02           jmp 0x113f
loc_113D:
113D  B0 01           mov al, 1
loc_113F:
113F  A2 6D 06        mov byte ptr [0x66d], al
1142  80 3E 6D 06 00  cmp byte ptr [0x66d], 0
1147  74 13           je 0x115c
1149  C4 3E 23 A9     les di, ptr [0xa923]
114D  26 8D 85 BD 00  lea ax, es:[di + 0xbd]
1152  8C C2           mov dx, es
1154  89 46 F6        mov word ptr [bp - 0xa], ax
1157  89 56 F8        mov word ptr [bp - 8], dx
115A  EB 10           jmp 0x116c
loc_115C:
115C  C4 3E 23 A9     les di, ptr [0xa923]
1160  26 8D 45 6C     lea ax, es:[di + 0x6c]
1164  8C C2           mov dx, es
1166  89 46 F6        mov word ptr [bp - 0xa], ax
1169  89 56 F8        mov word ptr [bp - 8], dx
loc_116C:
116C  B0 01           mov al, 1
116E  50              push ax
116F  C4 7E F6        les di, ptr [bp - 0xa]
1172  06              push es
1173  57              push di
1174  E8 4D F8        call 0x9c4
1177  08 C0           or al, al
1179  75 11           jne 0x118c
117B  B0 00           mov al, 0
117D  50              push ax
117E  9A 69 18 4B 21  call far 214B:1869
1183  08 C0           or al, al
1185  75 03           jne 0x118a
1187  E9 2B 04        jmp 0x15b5
loc_118A:
118A  EB E0           jmp 0x116c
loc_118C:
118C  9A 36 1A 4B 21  call far 214B:1A36
1191  C6 06 21 0C 01  mov byte ptr [0xc21], 1
1196  C4 3E 23 A9     les di, ptr [0xa923]
119A  26 8A 45 01     mov al, byte ptr es:[di + 1]
119E  30 E4           xor ah, ah
11A0  89 46 FA        mov word ptr [bp - 6], ax
11A3  C4 3E 23 A9     les di, ptr [0xa923]
11A7  26 8A 45 41     mov al, byte ptr es:[di + 0x41]
11AB  88 46 FE        mov byte ptr [bp - 2], al
11AE  C4 3E 23 A9     les di, ptr [0xa923]
11B2  26 C6 45 41 01  mov byte ptr es:[di + 0x41], 1
11B7  C4 06 30 9B     les ax, ptr [0x9b30]
11BB  8C C2           mov dx, es
11BD  A3 34 9B        mov word ptr [0x9b34], ax
11C0  89 16 36 9B     mov word ptr [0x9b36], dx
11C4  C6 46 FF 00     mov byte ptr [bp - 1], 0
11C8  EB 03           jmp 0x11cd
loc_11CA:
11CA  FE 46 FF        inc byte ptr [bp - 1]
loc_11CD:
11CD  8A 46 FF        mov al, byte ptr [bp - 1]
11D0  98              cwde
11D1  8B F8           mov di, ax
11D3  D1 E7           shl di, 1
11D5  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
11D9  BA BF 00        mov dx, 0xbf
11DC  F7 E2           mul dx
11DE  C4 3E 17 A9     les di, ptr [0xa917]
11E2  03 F8           add di, ax
11E4  06              push es
11E5  57              push di
11E6  8A 46 FF        mov al, byte ptr [bp - 1]
11E9  98              cwde
11EA  BA BF 00        mov dx, 0xbf
11ED  F7 E2           mul dx
11EF  8B F8           mov di, ax
11F1  81 C7 B2 8D     add di, 0x8db2
11F5  1E              push ds
11F6  57              push di
11F7  B8 BF 00        mov ax, 0xbf
11FA  50              push ax
11FB  9A 5D 02 E4 23  call far 23E4:025D
1200  8A 46 FF        mov al, byte ptr [bp - 1]
1203  98              cwde
1204  BA BF 00        mov dx, 0xbf
1207  F7 E2           mul dx
1209  8B F8           mov di, ax
120B  81 C7 34 8C     add di, 0x8c34
120F  89 7E F2        mov word ptr [bp - 0xe], di
1212  8C 5E F4        mov word ptr [bp - 0xc], ds
1215  C4 7E F2        les di, ptr [bp - 0xe]
1218  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
121C  30 E4           xor ah, ah
121E  BA 03 00        mov dx, 3
1221  F7 E2           mul dx
1223  C4 3E 1F A9     les di, ptr [0xa91f]
1227  03 F8           add di, ax
1229  06              push es
122A  57              push di
122B  8A 46 FF        mov al, byte ptr [bp - 1]
122E  98              cwde
122F  BA 03 00        mov dx, 3
1232  F7 E2           mul dx
1234  8B F8           mov di, ax
1236  81 C7 36 99     add di, 0x9936
123A  1E              push ds
123B  57              push di
123C  B8 03 00        mov ax, 3
123F  50              push ax
1240  9A 5D 02 E4 23  call far 23E4:025D
1245  C4 7E F2        les di, ptr [bp - 0xe]
1248  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
124C  30 E4           xor ah, ah
124E  BA 0D 00        mov dx, 0xd
1251  F7 E2           mul dx
1253  C4 3E 74 9B     les di, ptr [0x9b74]
1257  03 F8           add di, ax
1259  06              push es
125A  57              push di
125B  8A 46 FF        mov al, byte ptr [bp - 1]
125E  98              cwde
125F  BA 0D 00        mov dx, 0xd
1262  F7 E2           mul dx
1264  8B F8           mov di, ax
1266  81 C7 56 99     add di, 0x9956
126A  1E              push ds
126B  57              push di
126C  B8 0C 00        mov ax, 0xc
126F  50              push ax
1270  9A 44 06 E4 23  call far 23E4:0644
1275  C4 7E F2        les di, ptr [bp - 0xe]
1278  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
127C  30 E4           xor ah, ah
127E  C4 3E 78 9B     les di, ptr [0x9b78]
1282  03 F8           add di, ax
1284  26 8A 15        mov dl, byte ptr es:[di]
1287  8A 46 FF        mov al, byte ptr [bp - 1]
128A  98              cwde
128B  8B F8           mov di, ax
128D  88 95 72 99     mov byte ptr [di - 0x668e], dl
1291  C7 46 FC 01 00  mov word ptr [bp - 4], 1
1296  EB 03           jmp 0x129b
loc_1298:
1298  FF 46 FC        inc word ptr [bp - 4]
loc_129B:
129B  8B 46 FC        mov ax, word ptr [bp - 4]
129E  D1 E0           shl ax, 1
12A0  C4 7E F2        les di, ptr [bp - 0xe]
12A3  03 F8           add di, ax
12A5  26 8B 45 FE     mov ax, word ptr es:[di - 2]
12A9  BA 14 00        mov dx, 0x14
12AC  F7 E2           mul dx
12AE  C4 3E 1B A9     les di, ptr [0xa91b]
12B2  03 F8           add di, ax
12B4  06              push es
12B5  57              push di
12B6  8B 46 FC        mov ax, word ptr [bp - 4]
12B9  BA 14 00        mov dx, 0x14
12BC  F7 E2           mul dx
12BE  8B C8           mov cx, ax
12C0  8A 46 FF        mov al, byte ptr [bp - 1]
12C3  98              cwde
12C4  BA 90 01        mov dx, 0x190
12C7  F7 E2           mul dx
12C9  8B F8           mov di, ax
12CB  03 F9           add di, cx
12CD  81 C7 3C 92     add di, 0x923c
12D1  1E              push ds
12D2  57              push di
12D3  B8 14 00        mov ax, 0x14
12D6  50              push ax
12D7  9A 5D 02 E4 23  call far 23E4:025D
12DC  8B 46 FC        mov ax, word ptr [bp - 4]
12DF  D1 E0           shl ax, 1
12E1  C4 7E F2        les di, ptr [bp - 0xe]
12E4  03 F8           add di, ax
12E6  26 8B 45 FE     mov ax, word ptr es:[di - 2]
12EA  BA 0B 00        mov dx, 0xb
12ED  F7 E2           mul dx
12EF  C4 3E 6C 9B     les di, ptr [0x9b6c]
12F3  03 F8           add di, ax
12F5  06              push es
12F6  57              push di
12F7  8B 46 FC        mov ax, word ptr [bp - 4]
12FA  BA 0B 00        mov dx, 0xb
12FD  F7 E2           mul dx
12FF  8B C8           mov cx, ax
1301  8A 46 FF        mov al, byte ptr [bp - 1]
1304  98              cwde
1305  BA DC 00        mov dx, 0xdc
1308  F7 E2           mul dx
130A  8B F8           mov di, ax
130C  03 F9           add di, cx
130E  81 C7 1D 97     add di, 0x971d
1312  1E              push ds
1313  57              push di
1314  B8 0A 00        mov ax, 0xa
1317  50              push ax
1318  9A 44 06 E4 23  call far 23E4:0644
131D  8B 46 FC        mov ax, word ptr [bp - 4]
1320  D1 E0           shl ax, 1
1322  C4 7E F2        les di, ptr [bp - 0xe]
1325  03 F8           add di, ax
1327  26 8B 45 FE     mov ax, word ptr es:[di - 2]
132B  C4 3E 70 9B     les di, ptr [0x9b70]
132F  03 F8           add di, ax
1331  26 8A 1D        mov bl, byte ptr es:[di]
1334  8B 46 FC        mov ax, word ptr [bp - 4]
1337  8B C8           mov cx, ax
1339  8A 46 FF        mov al, byte ptr [bp - 1]
133C  98              cwde
133D  BA 14 00        mov dx, 0x14
1340  F7 E2           mul dx
1342  8B F8           mov di, ax
1344  03 F9           add di, cx
1346  88 9D 07 99     mov byte ptr [di - 0x66f9], bl
134A  83 7E FC 14     cmp word ptr [bp - 4], 0x14
134E  74 03           je 0x1353
1350  E9 45 FF        jmp 0x1298
loc_1353:
1353  80 7E FF 01     cmp byte ptr [bp - 1], 1
1357  74 03           je 0x135c
1359  E9 6E FE        jmp 0x11ca
loc_135C:
135C  C6 06 1E 0C 00  mov byte ptr [0xc1e], 0
1361  B8 2E 7C        mov ax, 0x7c2e
1364  8C DA           mov dx, ds
1366  A3 2A 7C        mov word ptr [0x7c2a], ax
1369  89 16 2C 7C     mov word ptr [0x7c2c], dx
136D  E8 F5 F8        call 0xc65
1370  C4 3E 2A 7C     les di, ptr [0x7c2a]
1374  89 7E F2        mov word ptr [bp - 0xe], di
1377  8C 46 F4        mov word ptr [bp - 0xc], es
137A  C4 7E F2        les di, ptr [bp - 0xe]
137D  26 8A 45 02     mov al, byte ptr es:[di + 2]
1381  50              push ax
1382  BF 3A 69        mov di, 0x693a
1385  1E              push ds
1386  57              push di
1387  9A DF 08 E4 23  call far 23E4:08DF
138C  75 04           jne 0x1392
138E  B0 00           mov al, 0
1390  EB 02           jmp 0x1394
loc_1392:
1392  B0 01           mov al, 1
loc_1394:
1394  A2 36 7C        mov byte ptr [0x7c36], al
1397  C6 06 39 7C 00  mov byte ptr [0x7c39], 0
139C  E8 D4 FC        call 0x1073
139F  C6 06 40 9B 00  mov byte ptr [0x9b40], 0
13A4  C6 06 1E 0C 01  mov byte ptr [0xc1e], 1
13A9  C6 06 1F 0C 01  mov byte ptr [0xc1f], 1
13AE  C6 06 37 7C 00  mov byte ptr [0x7c37], 0
13B3  C6 06 3E 9A 00  mov byte ptr [0x9a3e], 0
13B8  C6 06 38 7C 00  mov byte ptr [0x7c38], 0
13BD  C6 06 3F 9A 00  mov byte ptr [0x9a3f], 0
13C2  B0 01           mov al, 1
13C4  50              push ax
13C5  E8 C2 D9        call 0xffffed8a
13C8  80 3E 6D 06 00  cmp byte ptr [0x66d], 0
13CD  75 1F           jne 0x13ee
13CF  B0 01           mov al, 1
13D1  50              push ax
13D2  E8 FB 83        call 0xffff97d0
13D5  9A 8D 1E 4B 21  call far 214B:1E8D
13DA  BF A6 14        mov di, 0x14a6
13DD  1E              push ds
13DE  57              push di
13DF  BF 6A A9        mov di, 0xa96a
13E2  1E              push ds
13E3  57              push di
13E4  9A 29 03 4B 21  call far 214B:0329
13E9  9A DD 08 4B 21  call far 214B:08DD
loc_13EE:
13EE  C6 46 FF 00     mov byte ptr [bp - 1], 0
13F2  EB 03           jmp 0x13f7
loc_13F4:
13F4  FE 46 FF        inc byte ptr [bp - 1]
loc_13F7:
13F7  8A 46 FF        mov al, byte ptr [bp - 1]
13FA  98              cwde
13FB  BA BF 00        mov dx, 0xbf
13FE  F7 E2           mul dx
1400  8B F8           mov di, ax
1402  81 C7 B2 8D     add di, 0x8db2
1406  1E              push ds
1407  57              push di
1408  8A 46 FF        mov al, byte ptr [bp - 1]
140B  98              cwde
140C  8B F8           mov di, ax
140E  D1 E7           shl di, 1
1410  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
1414  BA BF 00        mov dx, 0xbf
1417  F7 E2           mul dx
1419  C4 3E 17 A9     les di, ptr [0xa917]
141D  03 F8           add di, ax
141F  06              push es
1420  57              push di
1421  B8 BF 00        mov ax, 0xbf
1424  50              push ax
1425  9A 5D 02 E4 23  call far 23E4:025D
142A  8A 46 FF        mov al, byte ptr [bp - 1]
142D  98              cwde
142E  BA BF 00        mov dx, 0xbf
1431  F7 E2           mul dx
1433  8B F8           mov di, ax
1435  81 C7 34 8C     add di, 0x8c34
1439  89 7E F2        mov word ptr [bp - 0xe], di
143C  8C 5E F4        mov word ptr [bp - 0xc], ds
143F  8A 46 FF        mov al, byte ptr [bp - 1]
1442  98              cwde
1443  BA 03 00        mov dx, 3
1446  F7 E2           mul dx
1448  8B F8           mov di, ax
144A  81 C7 36 99     add di, 0x9936
144E  1E              push ds
144F  57              push di
1450  C4 7E F2        les di, ptr [bp - 0xe]
1453  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
1457  30 E4           xor ah, ah
1459  BA 03 00        mov dx, 3
145C  F7 E2           mul dx
145E  C4 3E 1F A9     les di, ptr [0xa91f]
1462  03 F8           add di, ax
1464  06              push es
1465  57              push di
1466  B8 03 00        mov ax, 3
1469  50              push ax
146A  9A 5D 02 E4 23  call far 23E4:025D
146F  8A 46 FF        mov al, byte ptr [bp - 1]
1472  98              cwde
1473  BA 0D 00        mov dx, 0xd
1476  F7 E2           mul dx
1478  8B F8           mov di, ax
147A  81 C7 56 99     add di, 0x9956
147E  1E              push ds
147F  57              push di
1480  C4 7E F2        les di, ptr [bp - 0xe]
1483  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
1487  30 E4           xor ah, ah
1489  BA 0D 00        mov dx, 0xd
148C  F7 E2           mul dx
148E  C4 3E 74 9B     les di, ptr [0x9b74]
1492  03 F8           add di, ax
1494  06              push es
1495  57              push di
1496  B8 0C 00        mov ax, 0xc
1499  50              push ax
149A  9A 44 06 E4 23  call far 23E4:0644
149F  8A 46 FF        mov al, byte ptr [bp - 1]
14A2  98              cwde
14A3  8B F8           mov di, ax
14A5  8A 95 72 99     mov dl, byte ptr [di - 0x668e]
14A9  C4 7E F2        les di, ptr [bp - 0xe]
14AC  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
14B0  30 E4           xor ah, ah
14B2  C4 3E 78 9B     les di, ptr [0x9b78]
14B6  03 F8           add di, ax
14B8  26 88 15        mov byte ptr es:[di], dl
14BB  C7 46 FC 01 00  mov word ptr [bp - 4], 1
14C0  EB 03           jmp 0x14c5
loc_14C2:
14C2  FF 46 FC        inc word ptr [bp - 4]
loc_14C5:
14C5  8B 46 FC        mov ax, word ptr [bp - 4]
14C8  BA 14 00        mov dx, 0x14
14CB  F7 E2           mul dx
14CD  8B C8           mov cx, ax
14CF  8A 46 FF        mov al, byte ptr [bp - 1]
14D2  98              cwde
14D3  BA 90 01        mov dx, 0x190
14D6  F7 E2           mul dx
14D8  8B F8           mov di, ax
14DA  03 F9           add di, cx
14DC  81 C7 3C 92     add di, 0x923c
14E0  1E              push ds
14E1  57              push di
14E2  8B 46 FC        mov ax, word ptr [bp - 4]
14E5  D1 E0           shl ax, 1
14E7  C4 7E F2        les di, ptr [bp - 0xe]
14EA  03 F8           add di, ax
14EC  26 8B 45 FE     mov ax, word ptr es:[di - 2]
14F0  BA 14 00        mov dx, 0x14
14F3  F7 E2           mul dx
14F5  C4 3E 1B A9     les di, ptr [0xa91b]
14F9  03 F8           add di, ax
14FB  06              push es
14FC  57              push di
14FD  B8 14 00        mov ax, 0x14
1500  50              push ax
1501  9A 5D 02 E4 23  call far 23E4:025D
1506  8B 46 FC        mov ax, word ptr [bp - 4]
1509  BA 0B 00        mov dx, 0xb
150C  F7 E2           mul dx
150E  8B C8           mov cx, ax
1510  8A 46 FF        mov al, byte ptr [bp - 1]
1513  98              cwde
1514  BA DC 00        mov dx, 0xdc
1517  F7 E2           mul dx
1519  8B F8           mov di, ax
151B  03 F9           add di, cx
151D  81 C7 1D 97     add di, 0x971d
1521  1E              push ds
1522  57              push di
1523  8B 46 FC        mov ax, word ptr [bp - 4]
1526  D1 E0           shl ax, 1
1528  C4 7E F2        les di, ptr [bp - 0xe]
152B  03 F8           add di, ax
152D  26 8B 45 FE     mov ax, word ptr es:[di - 2]
1531  BA 0B 00        mov dx, 0xb
1534  F7 E2           mul dx
1536  C4 3E 6C 9B     les di, ptr [0x9b6c]
153A  03 F8           add di, ax
153C  06              push es
153D  57              push di
153E  B8 0A 00        mov ax, 0xa
1541  50              push ax
1542  9A 44 06 E4 23  call far 23E4:0644
1547  8B 46 FC        mov ax, word ptr [bp - 4]
154A  8B C8           mov cx, ax
154C  8A 46 FF        mov al, byte ptr [bp - 1]
154F  98              cwde
1550  BA 14 00        mov dx, 0x14
1553  F7 E2           mul dx
1555  8B F8           mov di, ax
1557  03 F9           add di, cx
1559  8A 95 07 99     mov dl, byte ptr [di - 0x66f9]
155D  8B 46 FC        mov ax, word ptr [bp - 4]
1560  D1 E0           shl ax, 1
1562  C4 7E F2        les di, ptr [bp - 0xe]
1565  03 F8           add di, ax
1567  26 8B 45 FE     mov ax, word ptr es:[di - 2]
156B  C4 3E 70 9B     les di, ptr [0x9b70]
156F  03 F8           add di, ax
1571  26 88 15        mov byte ptr es:[di], dl
1574  83 7E FC 14     cmp word ptr [bp - 4], 0x14
1578  74 03           je 0x157d
157A  E9 45 FF        jmp 0x14c2
loc_157D:
157D  80 7E FF 01     cmp byte ptr [bp - 1], 1
1581  74 03           je 0x1586
1583  E9 6E FE        jmp 0x13f4
loc_1586:
1586  C6 06 1F 0C 00  mov byte ptr [0xc1f], 0
158B  C6 06 1E 0C 00  mov byte ptr [0xc1e], 0
1590  C6 06 20 0C 00  mov byte ptr [0xc20], 0
1595  8A 46 FA        mov al, byte ptr [bp - 6]
1598  C4 3E 23 A9     les di, ptr [0xa923]
159C  26 88 45 01     mov byte ptr es:[di + 1], al
15A0  8A 46 FE        mov al, byte ptr [bp - 2]
15A3  C4 3E 23 A9     les di, ptr [0xa923]
15A7  26 88 45 41     mov byte ptr es:[di + 0x41], al
15AB  C6 06 21 0C 00  mov byte ptr [0xc21], 0
15B0  C6 06 6D 06 00  mov byte ptr [0x66d], 0
loc_15B5:
15B5  89 EC           mov sp, bp
15B7  5D              pop bp
15B8  CB              retf

