; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 214B (image offsets 214B0..235BF), part 2 of 4
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 214B:08DD  (found by: call, far)
sub_08DD:
08DD  55              push bp
08DE  89 E5           mov bp, sp
08E0  83 EC 14        sub sp, 0x14
08E3  80 3E AE 79 00  cmp byte ptr [0x79ae], 0
08E8  74 08           je 0x8f2
08EA  C6 06 AE 79 00  mov byte ptr [0x79ae], 0
08EF  E9 87 00        jmp 0x979
loc_08F2:
08F2  31 C0           xor ax, ax
08F4  89 46 EC        mov word ptr [bp - 0x14], ax
08F7  B0 16           mov al, 0x16
08F9  50              push ax
08FA  8D 7E EC        lea di, [bp - 0x14]
08FD  16              push ss
08FE  57              push di
08FF  9A 0B 00 5C 23  call far 235C:000B
0904  83 7E EC 00     cmp word ptr [bp - 0x14], 0
0908  75 07           jne 0x911
090A  31 C0           xor ax, ax
090C  9A D8 00 E4 23  call far 23E4:00D8
loc_0911:
0911  80 7E EC 00     cmp byte ptr [bp - 0x14], 0
0915  75 2D           jne 0x944
0917  8A 46 ED        mov al, byte ptr [bp - 0x13]
091A  3C 4B           cmp al, 0x4b
091C  75 05           jne 0x923
091E  FE 4E ED        dec byte ptr [bp - 0x13]
0921  EB 16           jmp 0x939
loc_0923:
0923  3C 4D           cmp al, 0x4d
0925  75 06           jne 0x92d
0927  80 6E ED 02     sub byte ptr [bp - 0x13], 2
092B  EB 0C           jmp 0x939
loc_092D:
092D  3C 4F           cmp al, 0x4f
092F  72 08           jb 0x939
0931  3C 51           cmp al, 0x51
0933  77 04           ja 0x939
0935  80 6E ED 03     sub byte ptr [bp - 0x13], 3
loc_0939:
0939  8A 46 ED        mov al, byte ptr [bp - 0x13]
093C  30 E4           xor ah, ah
093E  05 64 00        add ax, 0x64
0941  00 46 EC        add byte ptr [bp - 0x14], al
loc_0944:
0944  8A 46 EC        mov al, byte ptr [bp - 0x14]
0947  A2 76 A9        mov byte ptr [0xa976], al
094A  80 3E 76 A9 A6  cmp byte ptr [0xa976], 0xa6
094F  75 0B           jne 0x95c
0951  B0 00           mov al, 0
0953  08 C0           or al, al
0955  74 05           je 0x95c
0957  E8 B9 FE        call 0x813
095A  EB 0B           jmp 0x967
loc_095C:
095C  80 3E 76 A9 A3  cmp byte ptr [0xa976], 0xa3
0961  75 04           jne 0x967
0963  0E              push cs
0964  E8 E6 01        call 0xb4d
loc_0967:
0967  0E              push cs
0968  E8 B8 FD        call 0x723
096B  08 C0           or al, al
096D  75 83           jne 0x8f2
096F  80 3E 76 A9 A3  cmp byte ptr [0xa976], 0xa3
0974  75 03           jne 0x979
0976  E9 79 FF        jmp 0x8f2
loc_0979:
0979  A0 76 A9        mov al, byte ptr [0xa976]
097C  A2 77 A9        mov byte ptr [0xa977], al
097F  89 EC           mov sp, bp
0981  5D              pop bp
0982  CB              retf

; ---- routine 214B:0983  (found by: call)
sub_0983:
0983  55              push bp
0984  89 E5           mov bp, sp
0986  0E              push cs
0987  E8 53 FF        call 0x8dd
098A  C6 06 76 A9 00  mov byte ptr [0xa976], 0
098F  89 EC           mov sp, bp
0991  5D              pop bp
0992  CB              retf

; ---- routine 214B:0993  (found by: far)
sub_0993:
0993  55              push bp
0994  89 E5           mov bp, sp
0996  C6 06 AE 79 01  mov byte ptr [0x79ae], 1
099B  8A 46 06        mov al, byte ptr [bp + 6]
099E  A2 76 A9        mov byte ptr [0xa976], al
09A1  89 EC           mov sp, bp
09A3  5D              pop bp
09A4  CA 02 00        retf 2

; ---- routine 214B:09A7  (found by: call)
sub_09A7:
09A7  55              push bp
09A8  89 E5           mov bp, sp
09AA  83 EC 20        sub sp, 0x20
09AD  C4 7E 06        les di, ptr [bp + 6]
09B0  06              push es
09B1  57              push di
09B2  8D 7E E0        lea di, [bp - 0x20]
09B5  16              push ss
09B6  57              push di
09B7  B8 20 00        mov ax, 0x20
09BA  50              push ax
09BB  9A BF 08 E4 23  call far 23E4:08BF
loc_09C0:
09C0  0E              push cs
09C1  E8 19 FF        call 0x8dd
09C4  A0 76 A9        mov al, byte ptr [0xa976]
09C7  50              push ax
09C8  8D 7E E0        lea di, [bp - 0x20]
09CB  16              push ss
09CC  57              push di
09CD  9A DF 08 E4 23  call far 23E4:08DF
09D2  74 EC           je 0x9c0
09D4  89 EC           mov sp, bp
09D6  5D              pop bp
09D7  CA 04 00        retf 4

; ---- routine 214B:09DA  (found by: call, far)
sub_09DA:
09DA  55              push bp
09DB  89 E5           mov bp, sp
09DD  83 EC 16        sub sp, 0x16
09E0  FF 76 08        push word ptr [bp + 8]
09E3  FF 76 06        push word ptr [bp + 6]
09E6  31 C0           xor ax, ax
09E8  50              push ax
09E9  8D 7E EB        lea di, [bp - 0x15]
09EC  16              push ss
09ED  57              push di
09EE  B8 14 00        mov ax, 0x14
09F1  50              push ax
09F2  9A F6 12 E4 23  call far 23E4:12F6
09F7  8D 7E EB        lea di, [bp - 0x15]
09FA  16              push ss
09FB  57              push di
09FC  C4 7E 0A        les di, ptr [bp + 0xa]
09FF  06              push es
0A00  57              push di
0A01  B8 14 00        mov ax, 0x14
0A04  50              push ax
0A05  9A 44 06 E4 23  call far 23E4:0644
0A0A  89 EC           mov sp, bp
0A0C  5D              pop bp
0A0D  CA 04 00        retf 4

; ---- routine 214B:0A10  (found by: call, far)
sub_0A10:
0A10  55              push bp
0A11  89 E5           mov bp, sp
0A13  83 EC 52        sub sp, 0x52
0A16  C4 7E 06        les di, ptr [bp + 6]
0A19  06              push es
0A1A  57              push di
0A1B  8D 7E AF        lea di, [bp - 0x51]
0A1E  16              push ss
0A1F  57              push di
0A20  B8 50 00        mov ax, 0x50
0A23  50              push ax
0A24  9A 44 06 E4 23  call far 23E4:0644
0A29  8D 7E AF        lea di, [bp - 0x51]
0A2C  16              push ss
0A2D  57              push di
0A2E  0E              push cs
0A2F  E8 C6 FA        call 0x4f8
0A32  31 C0           xor ax, ax
0A34  9A D8 00 E4 23  call far 23E4:00D8
0A39  89 EC           mov sp, bp
0A3B  5D              pop bp
0A3C  CA 04 00        retf 4
; data (not reached as code), 35 bytes
0A3F                  pstr 'Insufficient memory to run program'

; ---- routine 214B:0A62  (found by: call, far)
sub_0A62:
0A62  55              push bp
0A63  89 E5           mov bp, sp
0A65  9A D0 03 E4 23  call far 23E4:03D0
0A6A  8B C8           mov cx, ax
0A6C  8B DA           mov bx, dx
0A6E  8B 46 06        mov ax, word ptr [bp + 6]
0A71  31 D2           xor dx, dx
0A73  3B D3           cmp dx, bx
0A75  7F 06           jg 0xa7d
0A77  7C 0D           jl 0xa86
0A79  3B C1           cmp ax, cx
0A7B  76 09           jbe 0xa86
loc_0A7D:
0A7D  BF 3F 0A        mov di, 0xa3f
0A80  0E              push cs
0A81  57              push di
0A82  0E              push cs
0A83  E8 8A FF        call 0xa10
loc_0A86:
0A86  FF 76 06        push word ptr [bp + 6]
0A89  9A 29 03 E4 23  call far 23E4:0329
0A8E  C4 7E 08        les di, ptr [bp + 8]
0A91  26 89 05        mov word ptr es:[di], ax
0A94  26 89 55 02     mov word ptr es:[di + 2], dx
0A98  C4 7E 08        les di, ptr [bp + 8]
0A9B  26 C4 3D        les di, ptr es:[di]
0A9E  06              push es
0A9F  57              push di
0AA0  FF 76 06        push word ptr [bp + 6]
0AA3  31 C0           xor ax, ax
0AA5  50              push ax
0AA6  0E              push cs
0AA7  E8 6E F5        call 0x18
0AAA  89 EC           mov sp, bp
0AAC  5D              pop bp
0AAD  CA 06 00        retf 6
; data (not reached as code), 9 bytes
0AB0                  pstr 'Printer '

; ---- routine 214B:0AB9  (found by: call, far)
sub_0AB9:
0AB9  55              push bp
0ABA  89 E5           mov bp, sp
0ABC  81 EC 16 01     sub sp, 0x116
0AC0  C6 46 EC 02     mov byte ptr [bp - 0x14], 2
0AC4  31 C0           xor ax, ax
0AC6  89 46 F1        mov word ptr [bp - 0xf], ax
0AC9  B0 17           mov al, 0x17
0ACB  50              push ax
0ACC  8D 7E EB        lea di, [bp - 0x15]
0ACF  16              push ss
0AD0  57              push di
0AD1  9A 0B 00 5C 23  call far 235C:000B
0AD6  8A 46 EC        mov al, byte ptr [bp - 0x14]
0AD9  24 40           and al, 0x40
0ADB  3C 40           cmp al, 0x40
0ADD  75 06           jne 0xae5
0ADF  C6 46 EA 01     mov byte ptr [bp - 0x16], 1
0AE3  EB 13           jmp 0xaf8
loc_0AE5:
0AE5  8A 46 EC        mov al, byte ptr [bp - 0x14]
0AE8  24 08           and al, 8
0AEA  3C 08           cmp al, 8
0AEC  75 06           jne 0xaf4
0AEE  C6 46 EA 02     mov byte ptr [bp - 0x16], 2
0AF2  EB 04           jmp 0xaf8
loc_0AF4:
0AF4  C6 46 EA 00     mov byte ptr [bp - 0x16], 0
loc_0AF8:
0AF8  80 7E EA 00     cmp byte ptr [bp - 0x16], 0
0AFC  74 29           je 0xb27
0AFE  8D BE EA FE     lea di, [bp - 0x116]
0B02  16              push ss
0B03  57              push di
0B04  BF B0 0A        mov di, 0xab0
0B07  0E              push cs
0B08  57              push di
0B09  9A 2A 06 E4 23  call far 23E4:062A
0B0E  8A 46 EA        mov al, byte ptr [bp - 0x16]
0B11  98              cwde
0B12  8B F8           mov di, ax
0B14  B1 04           mov cl, 4
0B16  D3 E7           shl di, cl
0B18  81 C7 A0 79     add di, 0x79a0
0B1C  1E              push ds
0B1D  57              push di
0B1E  9A B7 06 E4 23  call far 23E4:06B7
0B23  0E              push cs
0B24  E8 D1 F9        call 0x4f8
loc_0B27:
0B27  80 7E EA 00     cmp byte ptr [bp - 0x16], 0
0B2B  74 04           je 0xb31
0B2D  B0 00           mov al, 0
0B2F  EB 02           jmp 0xb33
loc_0B31:
0B31  B0 01           mov al, 1
loc_0B33:
0B33  88 46 FF        mov byte ptr [bp - 1], al
0B36  8A 46 FF        mov al, byte ptr [bp - 1]
0B39  89 EC           mov sp, bp
0B3B  5D              pop bp
0B3C  CB              retf
; data (not reached as code), 16 bytes
0B3D                  pstr 'Printing...'
0B49                  pstr 'prn'

; ---- routine 214B:0B4D  (found by: call)
sub_0B4D:
0B4D  55              push bp
0B4E  89 E5           mov bp, sp
0B50  81 EC 84 00     sub sp, 0x84
0B54  0E              push cs
0B55  E8 61 FF        call 0xab9
0B58  08 C0           or al, al
0B5A  75 03           jne 0xb5f
0B5C  E9 F4 00        jmp 0xc53
loc_0B5F:
0B5F  0E              push cs
0B60  E8 C2 FA        call 0x625
0B63  B0 19           mov al, 0x19
0B65  50              push ax
0B66  BF 3D 0B        mov di, 0xb3d
0B69  0E              push cs
0B6A  57              push di
0B6B  BF 6A A9        mov di, 0xa96a
0B6E  1E              push ds
0B6F  57              push di
0B70  0E              push cs
0B71  E8 DC F7        call 0x350
0B74  8D BE 7D FF     lea di, [bp - 0x83]
0B78  16              push ss
0B79  57              push di
0B7A  BF 49 0B        mov di, 0xb49
0B7D  0E              push cs
0B7E  57              push di
0B7F  9A 79 17 E4 23  call far 23E4:1779
0B84  8D BE 7D FF     lea di, [bp - 0x83]
0B88  16              push ss
0B89  57              push di
0B8A  B8 01 00        mov ax, 1
0B8D  50              push ax
0B8E  9A B0 17 E4 23  call far 23E4:17B0
0B93  C6 46 FE 01     mov byte ptr [bp - 2], 1
0B97  EB 03           jmp 0xb9c
loc_0B99:
0B99  FE 46 FE        inc byte ptr [bp - 2]
loc_0B9C:
0B9C  C6 46 FF 01     mov byte ptr [bp - 1], 1
0BA0  EB 03           jmp 0xba5
loc_0BA2:
0BA2  FE 46 FF        inc byte ptr [bp - 1]
loc_0BA5:
0BA5  8A 46 FF        mov al, byte ptr [bp - 1]
0BA8  30 E4           xor ah, ah
0BAA  D1 E0           shl ax, 1
0BAC  8B C8           mov cx, ax
0BAE  8A 46 FE        mov al, byte ptr [bp - 2]
0BB1  30 E4           xor ah, ah
0BB3  BA A0 00        mov dx, 0xa0
0BB6  F7 E2           mul dx
0BB8  C4 3E 6A A9     les di, ptr [0xa96a]
0BBC  03 F8           add di, ax
0BBE  03 F9           add di, cx
0BC0  26 8A 85 5E FF  mov al, byte ptr es:[di - 0xa2]
0BC5  88 46 FD        mov byte ptr [bp - 3], al
0BC8  80 7E FD 20     cmp byte ptr [bp - 3], 0x20
0BCC  72 06           jb 0xbd4
0BCE  80 7E FD 80     cmp byte ptr [bp - 3], 0x80
0BD2  76 04           jbe 0xbd8
loc_0BD4:
0BD4  C6 46 FD 20     mov byte ptr [bp - 3], 0x20
loc_0BD8:
0BD8  8D BE 7D FF     lea di, [bp - 0x83]
0BDC  16              push ss
0BDD  57              push di
0BDE  8D 7E FD        lea di, [bp - 3]
0BE1  16              push ss
0BE2  57              push di
0BE3  B8 01 00        mov ax, 1
0BE6  50              push ax
0BE7  31 C0           xor ax, ax
0BE9  50              push ax
0BEA  50              push ax
0BEB  9A 99 18 E4 23  call far 23E4:1899
0BF0  80 7E FF 50     cmp byte ptr [bp - 1], 0x50
0BF4  75 AC           jne 0xba2
0BF6  8D BE 7D FF     lea di, [bp - 0x83]
0BFA  16              push ss
0BFB  57              push di
0BFC  BF D0 79        mov di, 0x79d0
0BFF  1E              push ds
0C00  57              push di
0C01  B8 02 00        mov ax, 2
0C04  50              push ax
0C05  31 C0           xor ax, ax
0C07  50              push ax
0C08  50              push ax
0C09  9A 99 18 E4 23  call far 23E4:1899
0C0E  80 7E FE 19     cmp byte ptr [bp - 2], 0x19
0C12  75 85           jne 0xb99
0C14  C6 46 FF 01     mov byte ptr [bp - 1], 1
0C18  EB 03           jmp 0xc1d
loc_0C1A:
0C1A  FE 46 FF        inc byte ptr [bp - 1]
loc_0C1D:
0C1D  8D BE 7D FF     lea di, [bp - 0x83]
0C21  16              push ss
0C22  57              push di
0C23  BF D0 79        mov di, 0x79d0
0C26  1E              push ds
0C27  57              push di
0C28  B8 02 00        mov ax, 2
0C2B  50              push ax
0C2C  31 C0           xor ax, ax
0C2E  50              push ax
0C2F  50              push ax
0C30  9A 99 18 E4 23  call far 23E4:1899
0C35  80 7E FF 02     cmp byte ptr [bp - 1], 2
0C39  75 DF           jne 0xc1a
0C3B  8D BE 7D FF     lea di, [bp - 0x83]
0C3F  16              push ss
0C40  57              push di
0C41  9A 28 18 E4 23  call far 23E4:1828
0C46  9A 07 02 E4 23  call far 23E4:0207
0C4B  09 C0           or ax, ax
0C4D  75 00           jne 0xc4f
loc_0C4F:
0C4F  0E              push cs
0C50  E8 F0 F9        call 0x643
loc_0C53:
0C53  89 EC           mov sp, bp
0C55  5D              pop bp
0C56  CB              retf

; ---- routine 214B:0C57  (found by: far)
sub_0C57:
0C57  55              push bp
0C58  89 E5           mov bp, sp
0C5A  83 EC 02        sub sp, 2
0C5D  8B 46 08        mov ax, word ptr [bp + 8]
0C60  48              dec ax
0C61  8B D0           mov dx, ax
0C63  8B 46 06        mov ax, word ptr [bp + 6]
0C66  8B CA           mov cx, dx
0C68  D3 E8           shr ax, cl
0C6A  25 01 00        and ax, 1
0C6D  88 46 FF        mov byte ptr [bp - 1], al
0C70  8A 46 FF        mov al, byte ptr [bp - 1]
0C73  89 EC           mov sp, bp
0C75  5D              pop bp
0C76  CA 04 00        retf 4

; ---- routine 214B:0C79  (found by: call, far)
sub_0C79:
0C79  55              push bp
0C7A  89 E5           mov bp, sp
0C7C  8B 46 0A        mov ax, word ptr [bp + 0xa]
0C7F  48              dec ax
0C80  8B D0           mov dx, ax
0C82  B8 01 00        mov ax, 1
0C85  8B CA           mov cx, dx
0C87  D3 E0           shl ax, cl
0C89  8B D0           mov dx, ax
0C8B  C4 7E 06        les di, ptr [bp + 6]
0C8E  26 8A 05        mov al, byte ptr es:[di]
0C91  30 E4           xor ah, ah
0C93  0B C2           or ax, dx
0C95  C4 7E 06        les di, ptr [bp + 6]
0C98  26 88 05        mov byte ptr es:[di], al
0C9B  89 EC           mov sp, bp
0C9D  5D              pop bp
0C9E  CA 06 00        retf 6

; ---- routine 214B:0CA1  (found by: call, far)
sub_0CA1:
0CA1  55              push bp
0CA2  89 E5           mov bp, sp
0CA4  8B 46 0A        mov ax, word ptr [bp + 0xa]
0CA7  48              dec ax
0CA8  8B D0           mov dx, ax
0CAA  B8 01 00        mov ax, 1
0CAD  8B CA           mov cx, dx
0CAF  D3 E0           shl ax, cl
0CB1  F7 D0           not ax
0CB3  8B D0           mov dx, ax
0CB5  C4 7E 06        les di, ptr [bp + 6]
0CB8  26 8A 05        mov al, byte ptr es:[di]
0CBB  30 E4           xor ah, ah
0CBD  23 C2           and ax, dx
0CBF  C4 7E 06        les di, ptr [bp + 6]
0CC2  26 88 05        mov byte ptr es:[di], al
0CC5  89 EC           mov sp, bp
0CC7  5D              pop bp
0CC8  CA 06 00        retf 6

; ---- routine 214B:0CCB  (found by: far)
sub_0CCB:
0CCB  55              push bp
0CCC  89 E5           mov bp, sp
0CCE  80 7E 06 00     cmp byte ptr [bp + 6], 0
0CD2  74 0E           je 0xce2
0CD4  FF 76 0C        push word ptr [bp + 0xc]
0CD7  C4 7E 08        les di, ptr [bp + 8]
0CDA  06              push es
0CDB  57              push di
0CDC  0E              push cs
0CDD  E8 99 FF        call 0xc79
0CE0  EB 0C           jmp 0xcee
loc_0CE2:
0CE2  FF 76 0C        push word ptr [bp + 0xc]
0CE5  C4 7E 08        les di, ptr [bp + 8]
0CE8  06              push es
0CE9  57              push di
0CEA  0E              push cs
0CEB  E8 B3 FF        call 0xca1
loc_0CEE:
0CEE  89 EC           mov sp, bp
0CF0  5D              pop bp
0CF1  CA 08 00        retf 8

; ---- routine 214B:0CF4  (found by: far)
sub_0CF4:
0CF4  55              push bp
0CF5  89 E5           mov bp, sp
0CF7  8B 46 0A        mov ax, word ptr [bp + 0xa]
0CFA  48              dec ax
0CFB  8B D0           mov dx, ax
0CFD  B8 01 00        mov ax, 1
0D00  8B CA           mov cx, dx
0D02  D3 E0           shl ax, cl
0D04  8B D0           mov dx, ax
0D06  C4 7E 06        les di, ptr [bp + 6]
0D09  26 8A 05        mov al, byte ptr es:[di]
0D0C  30 E4           xor ah, ah
0D0E  33 C2           xor ax, dx
0D10  C4 7E 06        les di, ptr [bp + 6]
0D13  26 88 05        mov byte ptr es:[di], al
0D16  89 EC           mov sp, bp
0D18  5D              pop bp
0D19  CA 06 00        retf 6

; ---- routine 214B:0D1C  (found by: call, far)
sub_0D1C:
0D1C  55              push bp
0D1D  89 E5           mov bp, sp
0D1F  83 EC 04        sub sp, 4
0D22  C4 46 0A        les ax, ptr [bp + 0xa]
0D25  8C C2           mov dx, es
0D27  3B 56 08        cmp dx, word ptr [bp + 8]
0D2A  7F 07           jg 0xd33
0D2C  7C 12           jl 0xd40
0D2E  3B 46 06        cmp ax, word ptr [bp + 6]
0D31  76 0D           jbe 0xd40
loc_0D33:
0D33  C4 46 06        les ax, ptr [bp + 6]
0D36  8C C2           mov dx, es
0D38  89 46 FC        mov word ptr [bp - 4], ax
0D3B  89 56 FE        mov word ptr [bp - 2], dx
0D3E  EB 0B           jmp 0xd4b
loc_0D40:
0D40  C4 46 0A        les ax, ptr [bp + 0xa]
0D43  8C C2           mov dx, es
0D45  89 46 FC        mov word ptr [bp - 4], ax
0D48  89 56 FE        mov word ptr [bp - 2], dx
loc_0D4B:
0D4B  C4 46 FC        les ax, ptr [bp - 4]
0D4E  8C C2           mov dx, es
0D50  89 EC           mov sp, bp
0D52  5D              pop bp
0D53  CA 08 00        retf 8

; ---- routine 214B:0D56  (found by: call, far)
sub_0D56:
0D56  55              push bp
0D57  89 E5           mov bp, sp
0D59  83 EC 04        sub sp, 4
0D5C  C4 46 0A        les ax, ptr [bp + 0xa]
0D5F  8C C2           mov dx, es
0D61  3B 56 08        cmp dx, word ptr [bp + 8]
0D64  7F 07           jg 0xd6d
0D66  7C 12           jl 0xd7a
0D68  3B 46 06        cmp ax, word ptr [bp + 6]
0D6B  76 0D           jbe 0xd7a
loc_0D6D:
0D6D  C4 46 0A        les ax, ptr [bp + 0xa]
0D70  8C C2           mov dx, es
0D72  89 46 FC        mov word ptr [bp - 4], ax
0D75  89 56 FE        mov word ptr [bp - 2], dx
0D78  EB 0B           jmp 0xd85
loc_0D7A:
0D7A  C4 46 06        les ax, ptr [bp + 6]
0D7D  8C C2           mov dx, es
0D7F  89 46 FC        mov word ptr [bp - 4], ax
0D82  89 56 FE        mov word ptr [bp - 2], dx
loc_0D85:
0D85  C4 46 FC        les ax, ptr [bp - 4]
0D88  8C C2           mov dx, es
0D8A  89 EC           mov sp, bp
0D8C  5D              pop bp
0D8D  CA 08 00        retf 8

; ---- routine 214B:0D90  (found by: call)
sub_0D90:
0D90  55              push bp
0D91  89 E5           mov bp, sp
0D93  83 EC 02        sub sp, 2
0D96  8B 46 06        mov ax, word ptr [bp + 6]
0D99  D1 E0           shl ax, 1
0D9B  8B C8           mov cx, ax
0D9D  8B 46 08        mov ax, word ptr [bp + 8]
0DA0  BA A0 00        mov dx, 0xa0
0DA3  F7 E2           mul dx
0DA5  C4 3E 6A A9     les di, ptr [0xa96a]
0DA9  03 F8           add di, ax
0DAB  03 F9           add di, cx
0DAD  26 8B 85 5E FF  mov ax, word ptr es:[di - 0xa2]
0DB2  89 46 FE        mov word ptr [bp - 2], ax
loc_0DB5:
0DB5  0E              push cs
0DB6  E8 6A F9        call 0x723
0DB9  08 C0           or al, al
0DBB  75 5D           jne 0xe1a
0DBD  31 F6           xor si, si
0DBF  8E C6           mov es, si
0DC1  26 A1 6C 04     mov ax, word ptr es:[0x46c]
0DC5  31 D2           xor dx, dx
0DC7  B9 03 00        mov cx, 3
0DCA  F7 F1           div cx
0DCC  D0 E8           shr al, 1
0DCE  73 21           jae 0xdf1
0DD0  8B 5E FE        mov bx, word ptr [bp - 2]
0DD3  8B 46 06        mov ax, word ptr [bp + 6]
0DD6  D1 E0           shl ax, 1
0DD8  8B C8           mov cx, ax
0DDA  8B 46 08        mov ax, word ptr [bp + 8]
0DDD  BA A0 00        mov dx, 0xa0
0DE0  F7 E2           mul dx
0DE2  C4 3E 6A A9     les di, ptr [0xa96a]
0DE6  03 F8           add di, ax
0DE8  03 F9           add di, cx
0DEA  26 89 9D 5E FF  mov word ptr es:[di - 0xa2], bx
0DEF  EB 27           jmp 0xe18
loc_0DF1:
0DF1  8B 46 FE        mov ax, word ptr [bp - 2]
0DF4  25 00 F0        and ax, 0xf000
0DF7  0D 02 0F        or ax, 0xf02
0DFA  8B D8           mov bx, ax
0DFC  8B 46 06        mov ax, word ptr [bp + 6]
0DFF  D1 E0           shl ax, 1
0E01  8B C8           mov cx, ax
0E03  8B 46 08        mov ax, word ptr [bp + 8]
0E06  BA A0 00        mov dx, 0xa0
0E09  F7 E2           mul dx
0E0B  C4 3E 6A A9     les di, ptr [0xa96a]
0E0F  03 F8           add di, ax
0E11  03 F9           add di, cx
0E13  26 89 9D 5E FF  mov word ptr es:[di - 0xa2], bx
loc_0E18:
0E18  EB 9B           jmp 0xdb5
loc_0E1A:
0E1A  8B 5E FE        mov bx, word ptr [bp - 2]
0E1D  8B 46 06        mov ax, word ptr [bp + 6]
0E20  D1 E0           shl ax, 1
0E22  8B C8           mov cx, ax
0E24  8B 46 08        mov ax, word ptr [bp + 8]
0E27  BA A0 00        mov dx, 0xa0
0E2A  F7 E2           mul dx
0E2C  C4 3E 6A A9     les di, ptr [0xa96a]
0E30  03 F8           add di, ax
0E32  03 F9           add di, cx
0E34  26 89 9D 5E FF  mov word ptr es:[di - 0xa2], bx
0E39  89 EC           mov sp, bp
0E3B  5D              pop bp
0E3C  C2 06 00        ret 6
; data (not reached as code), 2 bytes
0E3F                  db 01 20   ; . 

; ---- routine 214B:0E41  (found by: call)
sub_0E41:
0E41  55              push bp
0E42  89 E5           mov bp, sp
0E44  81 EC 00 01     sub sp, 0x100
0E48  C6 06 B2 AA 05  mov byte ptr [0xaab2], 5
0E4D  8B 7E 04        mov di, word ptr [bp + 4]
0E50  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0E54  26 8A 45 01     mov al, byte ptr es:[di + 1]
0E58  50              push ax
0E59  9A B2 19 E4 23  call far 23E4:19B2
0E5E  8B 7E 04        mov di, word ptr [bp + 4]
0E61  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0E65  26 88 45 01     mov byte ptr es:[di + 1], al
0E69  8B 7E 04        mov di, word ptr [bp + 4]
0E6C  36 8A 45 08     mov al, byte ptr ss:[di + 8]
0E70  30 E4           xor ah, ah
0E72  8B D0           mov dx, ax
0E74  8B 7E 04        mov di, word ptr [bp + 4]
0E77  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
0E7B  2B C2           sub ax, dx
0E7D  40              inc ax
0E7E  99              cdq
0E7F  52              push dx
0E80  50              push ax
0E81  B8 01 00        mov ax, 1
0E84  31 D2           xor dx, dx
0E86  52              push dx
0E87  50              push ax
0E88  0E              push cs
0E89  E8 CA FE        call 0xd56
0E8C  8B 7E 04        mov di, word ptr [bp + 4]
0E8F  36 88 45 FE     mov byte ptr ss:[di - 2], al
0E93  8B 7E 04        mov di, word ptr [bp + 4]
0E96  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0E9A  26 80 3D 00     cmp byte ptr es:[di], 0
0E9E  76 41           jbe 0xee1
0EA0  8D BE 00 FF     lea di, [bp - 0x100]
0EA4  16              push ss
0EA5  57              push di
0EA6  8B 7E 04        mov di, word ptr [bp + 4]
0EA9  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0EAD  06              push es
0EAE  57              push di
0EAF  8B 7E 04        mov di, word ptr [bp + 4]
0EB2  36 8A 45 FE     mov al, byte ptr ss:[di - 2]
0EB6  30 E4           xor ah, ah
0EB8  50              push ax
0EB9  8B 7E 04        mov di, word ptr [bp + 4]
0EBC  36 8A 45 08     mov al, byte ptr ss:[di + 8]
0EC0  30 E4           xor ah, ah
0EC2  50              push ax
0EC3  9A 76 06 E4 23  call far 23E4:0676
0EC8  8B 7E 04        mov di, word ptr [bp + 4]
0ECB  36 8A 45 06     mov al, byte ptr ss:[di + 6]
0ECF  50              push ax
0ED0  8B 7E 04        mov di, word ptr [bp + 4]
0ED3  36 8A 45 0A     mov al, byte ptr ss:[di + 0xa]
0ED7  50              push ax
0ED8  BF 6A A9        mov di, 0xa96a
0EDB  1E              push ds
0EDC  57              push di
0EDD  0E              push cs
0EDE  E8 8C F3        call 0x26d
loc_0EE1:
0EE1  8B 7E 04        mov di, word ptr [bp + 4]
0EE4  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0EE8  26 8A 05        mov al, byte ptr es:[di]
0EEB  8B 7E 04        mov di, word ptr [bp + 4]
0EEE  36 3A 45 08     cmp al, byte ptr ss:[di + 8]
0EF2  73 55           jae 0xf49
0EF4  8B 7E 04        mov di, word ptr [bp + 4]
0EF7  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0EFB  26 8A 05        mov al, byte ptr es:[di]
0EFE  30 E4           xor ah, ah
0F00  8B D0           mov dx, ax
0F02  8B 7E 04        mov di, word ptr [bp + 4]
0F05  36 8A 45 08     mov al, byte ptr ss:[di + 8]
0F09  30 E4           xor ah, ah
0F0B  2B C2           sub ax, dx
0F0D  8B 7E 04        mov di, word ptr [bp + 4]
0F10  36 88 85 FC FD  mov byte ptr ss:[di - 0x204], al
0F15  8B 7E 04        mov di, word ptr [bp + 4]
0F18  81 C7 FC FD     add di, 0xfdfc
0F1C  16              push ss
0F1D  57              push di
0F1E  8B 7E 04        mov di, word ptr [bp + 4]
0F21  36 8A 45 06     mov al, byte ptr ss:[di + 6]
0F25  50              push ax
0F26  8B 7E 04        mov di, word ptr [bp + 4]
0F29  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0F2D  26 8A 05        mov al, byte ptr es:[di]
0F30  30 E4           xor ah, ah
0F32  8B D0           mov dx, ax
0F34  8B 7E 04        mov di, word ptr [bp + 4]
0F37  36 8A 45 0A     mov al, byte ptr ss:[di + 0xa]
0F3B  30 E4           xor ah, ah
0F3D  03 C2           add ax, dx
0F3F  50              push ax
0F40  BF 6A A9        mov di, 0xa96a
0F43  1E              push ds
0F44  57              push di
0F45  0E              push cs
0F46  E8 24 F3        call 0x26d
loc_0F49:
0F49  8B 7E 04        mov di, word ptr [bp + 4]
0F4C  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0F50  26 8A 05        mov al, byte ptr es:[di]
0F53  30 E4           xor ah, ah
0F55  8B 7E 04        mov di, word ptr [bp + 4]
0F58  36 3B 45 FC     cmp ax, word ptr ss:[di - 4]
0F5C  7D 51           jge 0xfaf
0F5E  BF 3F 0E        mov di, 0xe3f
0F61  0E              push cs
0F62  57              push di
0F63  8B 7E 04        mov di, word ptr [bp + 4]
0F66  36 8A 45 06     mov al, byte ptr ss:[di + 6]
0F6A  50              push ax
0F6B  8B 7E 04        mov di, word ptr [bp + 4]
0F6E  36 8A 45 08     mov al, byte ptr ss:[di + 8]
0F72  30 E4           xor ah, ah
0F74  8B D0           mov dx, ax
0F76  8B 7E 04        mov di, word ptr [bp + 4]
0F79  36 8A 45 0A     mov al, byte ptr ss:[di + 0xa]
0F7D  30 E4           xor ah, ah
0F7F  03 C2           add ax, dx
0F81  48              dec ax
0F82  99              cdq
0F83  52              push dx
0F84  50              push ax
0F85  8B 7E 04        mov di, word ptr [bp + 4]
0F88  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0F8C  26 8A 05        mov al, byte ptr es:[di]
0F8F  30 E4           xor ah, ah
0F91  8B D0           mov dx, ax
0F93  8B 7E 04        mov di, word ptr [bp + 4]
0F96  36 8A 45 0A     mov al, byte ptr ss:[di + 0xa]
0F9A  30 E4           xor ah, ah
0F9C  03 C2           add ax, dx
0F9E  99              cdq
0F9F  52              push dx
0FA0  50              push ax
0FA1  0E              push cs
0FA2  E8 77 FD        call 0xd1c
0FA5  50              push ax
0FA6  BF 6A A9        mov di, 0xa96a
0FA9  1E              push ds
0FAA  57              push di
0FAB  0E              push cs
0FAC  E8 BE F2        call 0x26d
loc_0FAF:
0FAF  89 EC           mov sp, bp
0FB1  5D              pop bp
0FB2  C2 02 00        ret 2

; ---- routine 214B:0FB5  (found by: call)
sub_0FB5:
0FB5  55              push bp
0FB6  89 E5           mov bp, sp
0FB8  81 EC 00 01     sub sp, 0x100
0FBC  8B 7E 04        mov di, word ptr [bp + 4]
0FBF  36 8A 45 0C     mov al, byte ptr ss:[di + 0xc]
0FC3  30 E4           xor ah, ah
0FC5  8B 7E 04        mov di, word ptr [bp + 4]
0FC8  36 3B 45 FC     cmp ax, word ptr ss:[di - 4]
0FCC  7E 59           jle 0x1027
0FCE  80 3E 24 7A 00  cmp byte ptr [0x7a24], 0
0FD3  75 15           jne 0xfea
0FD5  8B 7E 04        mov di, word ptr [bp + 4]
0FD8  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0FDC  26 8A 05        mov al, byte ptr es:[di]
0FDF  30 E4           xor ah, ah
0FE1  8B 7E 04        mov di, word ptr [bp + 4]
0FE4  36 3B 45 FC     cmp ax, word ptr ss:[di - 4]
0FE8  7D 3D           jge 0x1027
loc_0FEA:
0FEA  8B 7E 04        mov di, word ptr [bp + 4]
0FED  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
0FF1  26 8A 05        mov al, byte ptr es:[di]
0FF4  8B 7E 04        mov di, word ptr [bp + 4]
0FF7  36 3A 45 0C     cmp al, byte ptr ss:[di + 0xc]
0FFB  73 2A           jae 0x1027
0FFD  8D BE 00 FF     lea di, [bp - 0x100]
1001  16              push ss
1002  57              push di
1003  8A 46 06        mov al, byte ptr [bp + 6]
1006  50              push ax
1007  9A 5A 07 E4 23  call far 23E4:075A
100C  8B 7E 04        mov di, word ptr [bp + 4]
100F  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
1013  06              push es
1014  57              push di
1015  B8 FF 00        mov ax, 0xff
1018  50              push ax
1019  8B 7E 04        mov di, word ptr [bp + 4]
101C  36 FF 75 FC     push word ptr ss:[di - 4]
1020  9A 87 07 E4 23  call far 23E4:0787
1025  EB 16           jmp 0x103d
loc_1027:
1027  8A 56 06        mov dl, byte ptr [bp + 6]
102A  8B 7E 04        mov di, word ptr [bp + 4]
102D  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
1031  8B 7E 04        mov di, word ptr [bp + 4]
1034  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
1038  03 F8           add di, ax
103A  26 88 15        mov byte ptr es:[di], dl
loc_103D:
103D  8B 7E 04        mov di, word ptr [bp + 4]
1040  36 8A 45 0C     mov al, byte ptr ss:[di + 0xc]
1044  30 E4           xor ah, ah
1046  8B 7E 04        mov di, word ptr [bp + 4]
1049  36 3B 45 FC     cmp ax, word ptr ss:[di - 4]
104D  75 11           jne 0x1060
104F  8B 7E 04        mov di, word ptr [bp + 4]
1052  36 8A 45 0C     mov al, byte ptr ss:[di + 0xc]
1056  8B 7E 04        mov di, word ptr [bp + 4]
1059  36 C4 7D 0E     les di, ptr ss:[di + 0xe]
105D  26 88 05        mov byte ptr es:[di], al
loc_1060:
1060  89 EC           mov sp, bp
1062  5D              pop bp
1063  C2 04 00        ret 4
; data (not reached as code), 32 bytes
1066                  db 00 20 00 08 00 00 00 00 00 00 00 00 00 00 00 00   ; . ..............
1076                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 214B:1086  (found by: far)
sub_1086:
1086  55              push bp
1087  89 E5           mov bp, sp
1089  81 EC 06 03     sub sp, 0x306
108D  8A 46 0A        mov al, byte ptr [bp + 0xa]
1090  30 E4           xor ah, ah
1092  8B D0           mov dx, ax
1094  8A 46 08        mov al, byte ptr [bp + 8]
1097  30 E4           xor ah, ah
1099  2B C2           sub ax, dx
109B  88 46 08        mov byte ptr [bp + 8], al
109E  8D BE FD FD     lea di, [bp - 0x203]
10A2  16              push ss
10A3  57              push di
10A4  B8 FF 00        mov ax, 0xff
10A7  50              push ax
10A8  B8 B1 00        mov ax, 0xb1
10AB  50              push ax
10AC  0E              push cs
10AD  E8 68 EF        call 0x18
10B0  C4 7E 0E        les di, ptr [bp + 0xe]
10B3  06              push es
10B4  57              push di
10B5  8D BE FC FE     lea di, [bp - 0x104]
10B9  16              push ss
10BA  57              push di
10BB  B8 FF 00        mov ax, 0xff
10BE  50              push ax
10BF  9A 44 06 E4 23  call far 23E4:0644
10C4  C7 46 FC 01 00  mov word ptr [bp - 4], 1
10C9  C6 86 FB FD 01  mov byte ptr [bp - 0x205], 1
10CE  80 7E 06 19     cmp byte ptr [bp + 6], 0x19
10D2  74 33           je 0x1107
10D4  BF D2 79        mov di, 0x79d2
10D7  1E              push ds
10D8  57              push di
10D9  BF 6A A9        mov di, 0xa96a
10DC  1E              push ds
10DD  57              push di
10DE  0E              push cs
10DF  E8 47 F2        call 0x329
10E2  B0 0E           mov al, 0xe
10E4  50              push ax
10E5  8D BE FB FC     lea di, [bp - 0x305]
10E9  16              push ss
10EA  57              push di
10EB  8A 46 0C        mov al, byte ptr [bp + 0xc]
10EE  30 E4           xor ah, ah
10F0  31 D2           xor dx, dx
10F2  52              push dx
10F3  50              push ax
10F4  0E              push cs
10F5  E8 E2 F8        call 0x9da
10F8  B0 19           mov al, 0x19
10FA  50              push ax
10FB  B0 2C           mov al, 0x2c
10FD  50              push ax
10FE  BF 6A A9        mov di, 0xa96a
1101  1E              push ds
1102  57              push di
1103  0E              push cs
1104  E8 FE F0        call 0x205
loc_1107:
1107  55              push bp
1108  E8 36 FD        call 0xe41
110B  8A 46 06        mov al, byte ptr [bp + 6]
110E  30 E4           xor ah, ah
1110  50              push ax
1111  8A 46 FE        mov al, byte ptr [bp - 2]
1114  30 E4           xor ah, ah
1116  8B D0           mov dx, ax
1118  8A 46 0A        mov al, byte ptr [bp + 0xa]
111B  30 E4           xor ah, ah
111D  03 46 FC        add ax, word ptr [bp - 4]
1120  2B C2           sub ax, dx
1122  50              push ax
1123  55              push bp
1124  E8 69 FC        call 0xd90
1127  0E              push cs
1128  E8 B2 F7        call 0x8dd
112B  A0 76 A9        mov al, byte ptr [0xa976]
112E  3C 20           cmp al, 0x20
1130  72 67           jb 0x1199
1132  3C 7E           cmp al, 0x7e
1134  77 63           ja 0x1199
1136  80 BE FB FD 00  cmp byte ptr [bp - 0x205], 0
113B  74 25           je 0x1162
113D  8D BE FB FC     lea di, [bp - 0x305]
1141  16              push ss
1142  57              push di
1143  A0 76 A9        mov al, byte ptr [0xa976]
1146  50              push ax
1147  9A B2 19 E4 23  call far 23E4:19B2
114C  50              push ax
114D  9A 5A 07 E4 23  call far 23E4:075A
1152  C4 7E 0E        les di, ptr [bp + 0xe]
1155  06              push es
1156  57              push di
1157  B8 FF 00        mov ax, 0xff
115A  50              push ax
115B  9A 44 06 E4 23  call far 23E4:0644
1160  EB 27           jmp 0x1189
loc_1162:
1162  8B 46 FC        mov ax, word ptr [bp - 4]
1165  48              dec ax
1166  C4 7E 0E        les di, ptr [bp + 0xe]
1169  03 F8           add di, ax
116B  26 80 3D 20     cmp byte ptr es:[di], 0x20
116F  75 10           jne 0x1181
1171  A0 76 A9        mov al, byte ptr [0xa976]
1174  50              push ax
1175  9A B2 19 E4 23  call far 23E4:19B2
117A  50              push ax
117B  55              push bp
117C  E8 36 FE        call 0xfb5
117F  EB 08           jmp 0x1189
loc_1181:
1181  A0 76 A9        mov al, byte ptr [0xa976]
1184  50              push ax
1185  55              push bp
1186  E8 2C FE        call 0xfb5
loc_1189:
1189  8A 46 0C        mov al, byte ptr [bp + 0xc]
118C  30 E4           xor ah, ah
118E  3B 46 FC        cmp ax, word ptr [bp - 4]
1191  7E 03           jle 0x1196
1193  FF 46 FC        inc word ptr [bp - 4]
loc_1196:
1196  E9 65 01        jmp 0x12fe
loc_1199:
1199  3C B7           cmp al, 0xb7
119B  74 04           je 0x11a1
119D  3C 07           cmp al, 7
119F  75 14           jne 0x11b5
loc_11A1:
11A1  C4 7E 0E        les di, ptr [bp + 0xe]
11A4  06              push es
11A5  57              push di
11A6  FF 76 FC        push word ptr [bp - 4]
11A9  B8 01 00        mov ax, 1
11AC  50              push ax
11AD  9A DB 07 E4 23  call far 23E4:07DB
11B2  E9 49 01        jmp 0x12fe
loc_11B5:
11B5  3C 08           cmp al, 8
11B7  75 1D           jne 0x11d6
11B9  83 7E FC 01     cmp word ptr [bp - 4], 1
11BD  7E 03           jle 0x11c2
11BF  FF 4E FC        dec word ptr [bp - 4]
loc_11C2:
11C2  C4 7E 0E        les di, ptr [bp + 0xe]
11C5  06              push es
11C6  57              push di
11C7  FF 76 FC        push word ptr [bp - 4]
11CA  B8 01 00        mov ax, 1
11CD  50              push ax
11CE  9A DB 07 E4 23  call far 23E4:07DB
11D3  E9 28 01        jmp 0x12fe
loc_11D6:
11D6  3C 1B           cmp al, 0x1b
11D8  75 17           jne 0x11f1
11DA  8D BE FC FE     lea di, [bp - 0x104]
11DE  16              push ss
11DF  57              push di
11E0  C4 7E 0E        les di, ptr [bp + 0xe]
11E3  06              push es
11E4  57              push di
11E5  B8 FF 00        mov ax, 0xff
11E8  50              push ax
11E9  9A 44 06 E4 23  call far 23E4:0644
11EE  E9 0D 01        jmp 0x12fe
loc_11F1:
11F1  3C B6           cmp al, 0xb6
11F3  75 13           jne 0x1208
11F5  80 3E 24 7A 00  cmp byte ptr [0x7a24], 0
11FA  74 04           je 0x1200
11FC  B0 00           mov al, 0
11FE  EB 02           jmp 0x1202
loc_1200:
1200  B0 01           mov al, 1
loc_1202:
1202  A2 24 7A        mov byte ptr [0x7a24], al
1205  E9 F6 00        jmp 0x12fe
loc_1208:
1208  3C AE           cmp al, 0xae
120A  75 2D           jne 0x1239
120C  83 7E FC 01     cmp word ptr [bp - 4], 1
1210  7E 24           jle 0x1236
1212  FF 4E FC        dec word ptr [bp - 4]
1215  C4 7E 0E        les di, ptr [bp + 0xe]
1218  26 8A 05        mov al, byte ptr es:[di]
121B  30 E4           xor ah, ah
121D  3B 46 FC        cmp ax, word ptr [bp - 4]
1220  75 14           jne 0x1236
1222  8B 46 FC        mov ax, word ptr [bp - 4]
1225  C4 7E 0E        les di, ptr [bp + 0xe]
1228  03 F8           add di, ax
122A  26 80 3D 20     cmp byte ptr es:[di], 0x20
122E  75 06           jne 0x1236
1230  C4 7E 0E        les di, ptr [bp + 0xe]
1233  26 FE 0D        dec byte ptr es:[di]
loc_1236:
1236  E9 C5 00        jmp 0x12fe
loc_1239:
1239  3C AF           cmp al, 0xaf
123B  75 25           jne 0x1262
123D  8A 46 0C        mov al, byte ptr [bp + 0xc]
1240  30 E4           xor ah, ah
1242  3B 46 FC        cmp ax, word ptr [bp - 4]
1245  7E 18           jle 0x125f
1247  C4 7E 0E        les di, ptr [bp + 0xe]
124A  26 8A 05        mov al, byte ptr es:[di]
124D  30 E4           xor ah, ah
124F  40              inc ax
1250  3B 46 FC        cmp ax, word ptr [bp - 4]
1253  75 07           jne 0x125c
1255  B0 20           mov al, 0x20
1257  50              push ax
1258  55              push bp
1259  E8 59 FD        call 0xfb5
loc_125C:
125C  FF 46 FC        inc word ptr [bp - 4]
loc_125F:
125F  E9 9C 00        jmp 0x12fe
loc_1262:
1262  3C D7           cmp al, 0xd7
1264  75 34           jne 0x129a
1266  83 7E FC 01     cmp word ptr [bp - 4], 1
126A  7E 12           jle 0x127e
126C  8B 46 FC        mov ax, word ptr [bp - 4]
126F  48              dec ax
1270  C4 7E 0E        les di, ptr [bp + 0xe]
1273  03 F8           add di, ax
1275  26 80 3D 20     cmp byte ptr es:[di], 0x20
1279  75 03           jne 0x127e
127B  FF 4E FC        dec word ptr [bp - 4]
loc_127E:
127E  83 7E FC 01     cmp word ptr [bp - 4], 1
1282  7E 14           jle 0x1298
1284  8B 46 FC        mov ax, word ptr [bp - 4]
1287  48              dec ax
1288  C4 7E 0E        les di, ptr [bp + 0xe]
128B  03 F8           add di, ax
128D  26 80 3D 20     cmp byte ptr es:[di], 0x20
1291  74 05           je 0x1298
1293  FF 4E FC        dec word ptr [bp - 4]
1296  EB E6           jmp 0x127e
loc_1298:
1298  EB 64           jmp 0x12fe
loc_129A:
129A  3C D8           cmp al, 0xd8
129C  75 35           jne 0x12d3
loc_129E:
129E  C4 7E 0E        les di, ptr [bp + 0xe]
12A1  26 8A 05        mov al, byte ptr es:[di]
12A4  30 E4           xor ah, ah
12A6  3B 46 FC        cmp ax, word ptr [bp - 4]
12A9  7E 13           jle 0x12be
12AB  8B 46 FC        mov ax, word ptr [bp - 4]
12AE  C4 7E 0E        les di, ptr [bp + 0xe]
12B1  03 F8           add di, ax
12B3  26 80 3D 20     cmp byte ptr es:[di], 0x20
12B7  74 05           je 0x12be
12B9  FF 46 FC        inc word ptr [bp - 4]
12BC  EB E0           jmp 0x129e
loc_12BE:
12BE  83 7E FC 01     cmp word ptr [bp - 4], 1
12C2  7E 0D           jle 0x12d1
12C4  8A 46 0C        mov al, byte ptr [bp + 0xc]
12C7  30 E4           xor ah, ah
12C9  3B 46 FC        cmp ax, word ptr [bp - 4]
12CC  7E 03           jle 0x12d1
12CE  FF 46 FC        inc word ptr [bp - 4]
loc_12D1:
12D1  EB 2B           jmp 0x12fe
loc_12D3:
12D3  3C AB           cmp al, 0xab
12D5  75 07           jne 0x12de
12D7  C7 46 FC 01 00  mov word ptr [bp - 4], 1
12DC  EB 20           jmp 0x12fe
loc_12DE:
12DE  3C B0           cmp al, 0xb0
12E0  75 1C           jne 0x12fe
12E2  C4 7E 0E        les di, ptr [bp + 0xe]
12E5  26 8A 05        mov al, byte ptr es:[di]
12E8  30 E4           xor ah, ah
12EA  40              inc ax
12EB  99              cdq
12EC  52              push dx
12ED  50              push ax
12EE  8A 46 0C        mov al, byte ptr [bp + 0xc]
12F1  30 E4           xor ah, ah
12F3  31 D2           xor dx, dx
12F5  52              push dx
12F6  50              push ax
12F7  0E              push cs
12F8  E8 21 FA        call 0xd1c
12FB  89 46 FC        mov word ptr [bp - 4], ax
loc_12FE:
12FE  C6 86 FB FD 00  mov byte ptr [bp - 0x205], 0
1303  A0 76 A9        mov al, byte ptr [0xa976]
1306  50              push ax
1307  BF 66 10        mov di, 0x1066
130A  0E              push cs
130B  57              push di
130C  9A DF 08 E4 23  call far 23E4:08DF
1311  75 03           jne 0x1316
1313  E9 F1 FD        jmp 0x1107
loc_1316:
1316  C4 7E 0E        les di, ptr [bp + 0xe]
1319  26 8A 05        mov al, byte ptr es:[di]
131C  30 E4           xor ah, ah
131E  C4 7E 0E        les di, ptr [bp + 0xe]
1321  03 F8           add di, ax
1323  26 80 3D 20     cmp byte ptr es:[di], 0x20
1327  75 11           jne 0x133a
1329  C4 7E 0E        les di, ptr [bp + 0xe]
132C  26 80 3D 00     cmp byte ptr es:[di], 0
1330  76 08           jbe 0x133a
1332  C4 7E 0E        les di, ptr [bp + 0xe]
1335  26 FE 0D        dec byte ptr es:[di]
1338  EB DC           jmp 0x1316
loc_133A:
133A  C7 46 FC 01 00  mov word ptr [bp - 4], 1
133F  55              push bp
1340  E8 FE FA        call 0xe41
1343  C4 7E 0E        les di, ptr [bp + 0xe]
1346  26 80 3D 00     cmp byte ptr es:[di], 0
134A  75 14           jne 0x1360
134C  8D BE FC FE     lea di, [bp - 0x104]
1350  16              push ss
1351  57              push di
1352  C4 7E 0E        les di, ptr [bp + 0xe]
1355  06              push es
1356  57              push di
1357  B8 FF 00        mov ax, 0xff
135A  50              push ax
135B  9A 44 06 E4 23  call far 23E4:0644
loc_1360:
1360  89 EC           mov sp, bp
1362  5D              pop bp
1363  CA 0C 00        retf 0xc
; data (not reached as code), 5 bytes
1366                  pstr 'BAMI'

