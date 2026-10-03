; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 10 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:59B3  (found by: call)
sub_59B3:
59B3  55              push bp
59B4  89 E5           mov bp, sp
59B6  83 EC 02        sub sp, 2
59B9  80 3E 25 83 00  cmp byte ptr [0x8325], 0
59BE  75 07           jne 0x59c7
59C0  80 3E 24 83 00  cmp byte ptr [0x8324], 0
59C5  74 65           je 0x5a2c
loc_59C7:
59C7  C6 46 FF 00     mov byte ptr [bp - 1], 0
59CB  A0 0B 83        mov al, byte ptr [0x830b]
59CE  30 E4           xor ah, ah
59D0  50              push ax
59D1  E8 89 AA        call 0x45d
59D4  08 C0           or al, al
59D6  75 07           jne 0x59df
59D8  83 3E 00 83 00  cmp word ptr [0x8300], 0
59DD  75 02           jne 0x59e1
loc_59DF:
59DF  EB 4B           jmp 0x5a2c
loc_59E1:
59E1  A0 F7 82        mov al, byte ptr [0x82f7]
59E4  98              cwde
59E5  09 C0           or ax, ax
59E7  79 02           jns 0x59eb
59E9  F7 D8           neg ax
loc_59EB:
59EB  3D 25 00        cmp ax, 0x25
59EE  75 3C           jne 0x5a2c
59F0  A0 F6 82        mov al, byte ptr [0x82f6]
59F3  98              cwde
59F4  09 C0           or ax, ax
59F6  79 02           jns 0x59fa
59F8  F7 D8           neg ax
loc_59FA:
59FA  3D 01 00        cmp ax, 1
59FD  7F 2D           jg 0x5a2c
59FF  A0 F6 82        mov al, byte ptr [0x82f6]
5A02  98              cwde
5A03  09 C0           or ax, ax
5A05  79 02           jns 0x5a09
5A07  F7 D8           neg ax
loc_5A09:
5A09  09 C0           or ax, ax
5A0B  74 11           je 0x5a1e
5A0D  B8 04 00        mov ax, 4
5A10  50              push ax
5A11  9A D0 06 4B 21  call far 214B:06D0
5A16  08 C0           or al, al
5A18  75 04           jne 0x5a1e
5A1A  B0 00           mov al, 0
5A1C  EB 02           jmp 0x5a20
loc_5A1E:
5A1E  B0 01           mov al, 1
loc_5A20:
5A20  98              cwde
5A21  8B F8           mov di, ax
5A23  8A 85 FA 07     mov al, byte ptr [di + 0x7fa]
5A27  50              push ax
5A28  55              push bp
5A29  E8 0F FF        call 0x593b
loc_5A2C:
5A2C  8A 46 FF        mov al, byte ptr [bp - 1]
5A2F  89 EC           mov sp, bp
5A31  5D              pop bp
5A32  C3              ret

; ---- routine 0791:5A33  (found by: call)
sub_5A33:
5A33  55              push bp
5A34  89 E5           mov bp, sp
5A36  8B 7E 04        mov di, word ptr [bp + 4]
5A39  36 C4 7D 06     les di, ptr ss:[di + 6]
5A3D  26 8A 45 06     mov al, byte ptr es:[di + 6]
5A41  A2 0B 83        mov byte ptr [0x830b], al
5A44  8A 46 06        mov al, byte ptr [bp + 6]
5A47  50              push ax
5A48  E8 58 D0        call 0x2aa3
5A4B  80 3E 26 83 00  cmp byte ptr [0x8326], 0
5A50  75 1B           jne 0x5a6d
5A52  8B 7E 04        mov di, word ptr [bp + 4]
5A55  36 C4 7D 06     les di, ptr ss:[di + 6]
5A59  06              push es
5A5A  57              push di
5A5B  0E              push cs
5A5C  E8 15 CF        call 0x2974
5A5F  98              cwde
5A60  BA 0A 00        mov dx, 0xa
5A63  F7 E2           mul dx
5A65  8B F8           mov di, ax
5A67  FE 85 83 7B     inc byte ptr [di + 0x7b83]
5A6B  EB 0A           jmp 0x5a77
loc_5A6D:
5A6D  8B 7E 04        mov di, word ptr [bp + 4]
5A70  36 8A 45 FE     mov al, byte ptr ss:[di - 2]
5A74  A2 0B 83        mov byte ptr [0x830b], al
loc_5A77:
5A77  C6 06 24 83 00  mov byte ptr [0x8324], 0
5A7C  80 3E 26 83 00  cmp byte ptr [0x8326], 0
5A81  75 05           jne 0x5a88
5A83  C6 06 27 83 00  mov byte ptr [0x8327], 0
loc_5A88:
5A88  89 EC           mov sp, bp
5A8A  5D              pop bp
5A8B  C2 04 00        ret 4

; ---- routine 0791:5A8E  (found by: call)
sub_5A8E:
5A8E  55              push bp
5A8F  89 E5           mov bp, sp
5A91  80 3E 26 83 00  cmp byte ptr [0x8326], 0
5A96  74 07           je 0x5a9f
5A98  31 C0           xor ax, ax
5A9A  A3 00 83        mov word ptr [0x8300], ax
5A9D  EB 0D           jmp 0x5aac
loc_5A9F:
5A9F  8B 7E 04        mov di, word ptr [bp + 4]
5AA2  36 C4 7D 06     les di, ptr ss:[di + 6]
5AA6  06              push es
5AA7  57              push di
5AA8  0E              push cs
5AA9  E8 F3 2B        call 0x869f
loc_5AAC:
5AAC  B0 1D           mov al, 0x1d
5AAE  50              push ax
5AAF  FF 76 04        push word ptr [bp + 4]
5AB2  E8 7E FF        call 0x5a33
5AB5  8B 7E 04        mov di, word ptr [bp + 4]
5AB8  36 C4 7D 06     les di, ptr ss:[di + 6]
5ABC  26 FF 35        push word ptr es:[di]
5ABF  8B 7E 04        mov di, word ptr [bp + 4]
5AC2  36 C4 7D 06     les di, ptr ss:[di + 6]
5AC6  06              push es
5AC7  57              push di
5AC8  0E              push cs
5AC9  E8 EC D3        call 0x2eb8
5ACC  08 C0           or al, al
5ACE  74 0F           je 0x5adf
5AD0  8B 7E 04        mov di, word ptr [bp + 4]
5AD3  36 C4 7D 06     les di, ptr ss:[di + 6]
5AD7  06              push es
5AD8  57              push di
5AD9  0E              push cs
5ADA  E8 62 F2        call 0x4d3f
5ADD  EB 11           jmp 0x5af0
loc_5ADF:
5ADF  B8 09 00        mov ax, 9
5AE2  50              push ax
5AE3  8B 7E 04        mov di, word ptr [bp + 4]
5AE6  36 C4 7D 06     les di, ptr ss:[di + 6]
5AEA  06              push es
5AEB  57              push di
5AEC  0E              push cs
5AED  E8 BD E4        call 0x3fad
loc_5AF0:
5AF0  89 EC           mov sp, bp
5AF2  5D              pop bp
5AF3  C2 02 00        ret 2
; data (not reached as code), 64 bytes
5AF6                  db E0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
5B06                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
5B16                  db 1E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
5B26                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:5B36  (found by: call)
sub_5B36:
5B36  55              push bp
5B37  89 E5           mov bp, sp
5B39  83 EC 08        sub sp, 8
5B3C  80 3E 25 83 00  cmp byte ptr [0x8325], 0
5B41  75 0A           jne 0x5b4d
5B43  80 3E 24 83 00  cmp byte ptr [0x8324], 0
5B48  75 03           jne 0x5b4d
5B4A  E9 EE 02        jmp 0x5e3b
loc_5B4D:
5B4D  C4 7E 06        les di, ptr [bp + 6]
5B50  06              push es
5B51  57              push di
5B52  0E              push cs
5B53  E8 FB CF        call 0x2b51
5B56  08 C0           or al, al
5B58  74 03           je 0x5b5d
5B5A  E9 C8 02        jmp 0x5e25
loc_5B5D:
5B5D  A0 0B 83        mov al, byte ptr [0x830b]
5B60  30 E4           xor ah, ah
5B62  89 46 FE        mov word ptr [bp - 2], ax
5B65  80 3E 02 83 00  cmp byte ptr [0x8302], 0
5B6A  74 03           je 0x5b6f
5B6C  E9 19 01        jmp 0x5c88
loc_5B6F:
5B6F  C4 7E 06        les di, ptr [bp + 6]
5B72  26 FF 35        push word ptr es:[di]
5B75  C4 7E 06        les di, ptr [bp + 6]
5B78  06              push es
5B79  57              push di
5B7A  0E              push cs
5B7B  E8 3A D3        call 0x2eb8
5B7E  08 C0           or al, al
5B80  75 06           jne 0x5b88
5B82  C6 46 F9 0B     mov byte ptr [bp - 7], 0xb
5B86  EB 11           jmp 0x5b99
loc_5B88:
5B88  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5B8D  74 06           je 0x5b95
5B8F  C6 46 F9 41     mov byte ptr [bp - 7], 0x41
5B93  EB 04           jmp 0x5b99
loc_5B95:
5B95  C6 46 F9 0D     mov byte ptr [bp - 7], 0xd
loc_5B99:
5B99  8A 46 F9        mov al, byte ptr [bp - 7]
5B9C  50              push ax
5B9D  C4 7E 06        les di, ptr [bp + 6]
5BA0  06              push es
5BA1  57              push di
5BA2  0E              push cs
5BA3  E8 82 CF        call 0x2b28
5BA6  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5BAB  74 3B           je 0x5be8
5BAD  B8 04 00        mov ax, 4
5BB0  50              push ax
5BB1  A0 0B 83        mov al, byte ptr [0x830b]
5BB4  30 E4           xor ah, ah
5BB6  BA 16 00        mov dx, 0x16
5BB9  F7 E2           mul dx
5BBB  8B F8           mov di, ax
5BBD  81 C7 E8 80     add di, 0x80e8
5BC1  1E              push ds
5BC2  57              push di
5BC3  0E              push cs
5BC4  E8 C3 CB        call 0x278a
5BC7  50              push ax
5BC8  9A B1 06 4B 21  call far 214B:06B1
5BCD  50              push ax
5BCE  B8 01 00        mov ax, 1
5BD1  50              push ax
5BD2  C4 7E 06        les di, ptr [bp + 6]
5BD5  06              push es
5BD6  57              push di
5BD7  0E              push cs
5BD8  E8 AF CB        call 0x278a
5BDB  D1 E0           shl ax, 1
5BDD  50              push ax
5BDE  9A B1 06 4B 21  call far 214B:06B1
5BE3  5A              pop dx
5BE4  3B C2           cmp ax, dx
5BE6  7F 56           jg 0x5c3e
loc_5BE8:
5BE8  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5BED  75 55           jne 0x5c44
5BEF  B8 0A 00        mov ax, 0xa
5BF2  50              push ax
5BF3  A0 0B 83        mov al, byte ptr [0x830b]
5BF6  30 E4           xor ah, ah
5BF8  BA 16 00        mov dx, 0x16
5BFB  F7 E2           mul dx
5BFD  8B F8           mov di, ax
5BFF  81 C7 E8 80     add di, 0x80e8
5C03  1E              push ds
5C04  57              push di
5C05  0E              push cs
5C06  E8 81 CB        call 0x278a
5C09  50              push ax
5C0A  9A B1 06 4B 21  call far 214B:06B1
5C0F  50              push ax
5C10  B8 01 00        mov ax, 1
5C13  50              push ax
5C14  C4 7E 06        les di, ptr [bp + 6]
5C17  06              push es
5C18  57              push di
5C19  0E              push cs
5C1A  E8 6D CB        call 0x278a
5C1D  31 C9           xor cx, cx
5C1F  D3 E0           shl ax, cl
5C21  8B D0           mov dx, ax
5C23  80 7E F9 0B     cmp byte ptr [bp - 7], 0xb
5C27  75 04           jne 0x5c2d
5C29  B0 00           mov al, 0
5C2B  EB 02           jmp 0x5c2f
loc_5C2D:
5C2D  B0 01           mov al, 1
loc_5C2F:
5C2F  30 E4           xor ah, ah
5C31  03 C2           add ax, dx
5C33  50              push ax
5C34  9A B1 06 4B 21  call far 214B:06B1
5C39  5A              pop dx
5C3A  3B C2           cmp ax, dx
5C3C  7E 06           jle 0x5c44
loc_5C3E:
5C3E  55              push bp
5C3F  E8 4C FE        call 0x5a8e
5C42  EB 41           jmp 0x5c85
loc_5C44:
5C44  C4 7E 06        les di, ptr [bp + 6]
5C47  06              push es
5C48  57              push di
5C49  0E              push cs
5C4A  E8 5C F1        call 0x4da9
5C4D  08 C0           or al, al
5C4F  74 1E           je 0x5c6f
5C51  9A FA 06 4B 21  call far 214B:06FA
5C56  08 C0           or al, al
5C58  74 0F           je 0x5c69
5C5A  C4 7E 06        les di, ptr [bp + 6]
5C5D  26 8A 45 06     mov al, byte ptr es:[di + 6]
5C61  30 E4           xor ah, ah
5C63  50              push ax
5C64  E8 9F 25        call 0x8206
5C67  EB 04           jmp 0x5c6d
loc_5C69:
5C69  55              push bp
5C6A  E8 21 FE        call 0x5a8e
loc_5C6D:
5C6D  EB 16           jmp 0x5c85
loc_5C6F:
5C6F  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5C74  75 06           jne 0x5c7c
5C76  B0 0C           mov al, 0xc
5C78  50              push ax
5C79  E8 27 CE        call 0x2aa3
loc_5C7C:
5C7C  C4 7E 06        les di, ptr [bp + 6]
5C7F  06              push es
5C80  57              push di
5C81  0E              push cs
5C82  E8 BA F0        call 0x4d3f
loc_5C85:
5C85  E9 9B 01        jmp 0x5e23
loc_5C88:
5C88  80 3E 24 83 00  cmp byte ptr [0x8324], 0
5C8D  74 07           je 0x5c96
5C8F  C7 46 FC 01 00  mov word ptr [bp - 4], 1
5C94  EB 22           jmp 0x5cb8
loc_5C96:
5C96  A0 27 83        mov al, byte ptr [0x8327]
5C99  50              push ax
5C9A  BF F6 5A        mov di, 0x5af6
5C9D  0E              push cs
5C9E  57              push di
5C9F  9A DF 08 E4 23  call far 23E4:08DF
5CA4  75 04           jne 0x5caa
5CA6  B0 00           mov al, 0
5CA8  EB 02           jmp 0x5cac
loc_5CAA:
5CAA  B0 01           mov al, 1
loc_5CAC:
5CAC  98              cwde
5CAD  8B F8           mov di, ax
5CAF  8A 85 FE 07     mov al, byte ptr [di + 0x7fe]
5CB3  30 E4           xor ah, ah
5CB5  89 46 FC        mov word ptr [bp - 4], ax
loc_5CB8:
5CB8  80 3E 24 83 00  cmp byte ptr [0x8324], 0
5CBD  75 07           jne 0x5cc6
5CBF  31 C0           xor ax, ax
5CC1  89 46 FA        mov word ptr [bp - 6], ax
5CC4  EB 49           jmp 0x5d0f
loc_5CC6:
5CC6  B8 03 00        mov ax, 3
5CC9  50              push ax
5CCA  9A D0 06 4B 21  call far 214B:06D0
5CCF  08 C0           or al, al
5CD1  75 05           jne 0x5cd8
5CD3  E9 65 01        jmp 0x5e3b
; data (not reached as code), 2 bytes
5CD6                  db EB 37   ; .7
loc_5CD8:
5CD8  80 3E 27 83 04  cmp byte ptr [0x8327], 4
5CDD  74 04           je 0x5ce3
5CDF  B0 00           mov al, 0
5CE1  EB 02           jmp 0x5ce5
loc_5CE3:
5CE3  B0 01           mov al, 1
loc_5CE5:
5CE5  98              cwde
5CE6  8B F8           mov di, ax
5CE8  8A 85 00 08     mov al, byte ptr [di + 0x800]
5CEC  30 E4           xor ah, ah
5CEE  50              push ax
5CEF  A0 0B 83        mov al, byte ptr [0x830b]
5CF2  30 E4           xor ah, ah
5CF4  BA 16 00        mov dx, 0x16
5CF7  F7 E2           mul dx
5CF9  8B F8           mov di, ax
5CFB  81 C7 E8 80     add di, 0x80e8
5CFF  1E              push ds
5D00  57              push di
5D01  0E              push cs
5D02  E8 85 CA        call 0x278a
5D05  31 D2           xor dx, dx
5D07  B9 02 00        mov cx, 2
5D0A  F7 F1           div cx
5D0C  89 46 FA        mov word ptr [bp - 6], ax
loc_5D0F:
5D0F  C4 7E 06        les di, ptr [bp + 6]
5D12  26 FF 35        push word ptr es:[di]
5D15  C4 7E 06        les di, ptr [bp + 6]
5D18  06              push es
5D19  57              push di
5D1A  0E              push cs
5D1B  E8 9A D1        call 0x2eb8
5D1E  08 C0           or al, al
5D20  75 10           jne 0x5d32
5D22  B8 09 00        mov ax, 9
5D25  50              push ax
5D26  C4 7E 06        les di, ptr [bp + 6]
5D29  06              push es
5D2A  57              push di
5D2B  0E              push cs
5D2C  E8 7E E2        call 0x3fad
5D2F  E9 F1 00        jmp 0x5e23
loc_5D32:
5D32  83 3E 00 83 00  cmp word ptr [0x8300], 0
5D37  74 49           je 0x5d82
5D39  BF F6 82        mov di, 0x82f6
5D3C  1E              push ds
5D3D  57              push di
5D3E  0E              push cs
5D3F  E8 1D 26        call 0x835f
5D42  B9 02 00        mov cx, 2
5D45  D3 E0           shl ax, cl
5D47  50              push ax
5D48  9A B1 06 4B 21  call far 214B:06B1
5D4D  99              cdq
5D4E  8B C8           mov cx, ax
5D50  8B DA           mov bx, dx
5D52  8B 46 FA        mov ax, word ptr [bp - 6]
5D55  31 D2           xor dx, dx
5D57  03 C1           add ax, cx
5D59  13 D3           adc dx, bx
5D5B  52              push dx
5D5C  50              push ax
5D5D  FF 76 FC        push word ptr [bp - 4]
5D60  C4 7E 06        les di, ptr [bp + 6]
5D63  06              push es
5D64  57              push di
5D65  0E              push cs
5D66  E8 21 CA        call 0x278a
5D69  50              push ax
5D6A  9A B1 06 4B 21  call far 214B:06B1
5D6F  99              cdq
5D70  59              pop cx
5D71  5B              pop bx
5D72  3B D3           cmp dx, bx
5D74  7F 0C           jg 0x5d82
5D76  7D 03           jge 0x5d7b
5D78  E9 A8 00        jmp 0x5e23
loc_5D7B:
5D7B  3B C1           cmp ax, cx
5D7D  77 03           ja 0x5d82
5D7F  E9 A1 00        jmp 0x5e23
loc_5D82:
5D82  80 3E 26 83 00  cmp byte ptr [0x8326], 0
5D87  75 17           jne 0x5da0
5D89  A0 27 83        mov al, byte ptr [0x8327]
5D8C  50              push ax
5D8D  BF 16 5B        mov di, 0x5b16
5D90  0E              push cs
5D91  57              push di
5D92  9A DF 08 E4 23  call far 23E4:08DF
5D97  74 07           je 0x5da0
5D99  E8 FA CB        call 0x2996
5D9C  50              push ax
5D9D  E8 80 DE        call 0x3c20
loc_5DA0:
5DA0  B8 04 00        mov ax, 4
5DA3  50              push ax
5DA4  9A B1 06 4B 21  call far 214B:06B1
5DA9  3D 01 00        cmp ax, 1
5DAC  75 36           jne 0x5de4
5DAE  A1 FE 82        mov ax, word ptr [0x82fe]
5DB1  F7 D8           neg ax
5DB3  A3 FE 82        mov word ptr [0x82fe], ax
5DB6  A1 FC 82        mov ax, word ptr [0x82fc]
5DB9  F7 D8           neg ax
5DBB  A3 FC 82        mov word ptr [0x82fc], ax
5DBE  B8 01 00        mov ax, 1
5DC1  31 D2           xor dx, dx
5DC3  52              push dx
5DC4  50              push ax
5DC5  A1 00 83        mov ax, word ptr [0x8300]
5DC8  31 D2           xor dx, dx
5DCA  B9 04 00        mov cx, 4
5DCD  F7 F1           div cx
5DCF  31 D2           xor dx, dx
5DD1  52              push dx
5DD2  50              push ax
5DD3  9A 56 0D 4B 21  call far 214B:0D56
5DD8  A3 00 83        mov word ptr [0x8300], ax
5DDB  B0 1E           mov al, 0x1e
5DDD  50              push ax
5DDE  55              push bp
5DDF  E8 51 FC        call 0x5a33
5DE2  EB 3F           jmp 0x5e23
loc_5DE4:
5DE4  3D 02 00        cmp ax, 2
5DE7  75 36           jne 0x5e1f
5DE9  9A FA 06 4B 21  call far 214B:06FA
5DEE  98              cwde
5DEF  8B F8           mov di, ax
5DF1  8A 85 20 79     mov al, byte ptr [di + 0x7920]
5DF5  98              cwde
5DF6  A3 FC 82        mov word ptr [0x82fc], ax
5DF9  B8 01 00        mov ax, 1
5DFC  31 D2           xor dx, dx
5DFE  52              push dx
5DFF  50              push ax
5E00  A1 00 83        mov ax, word ptr [0x8300]
5E03  31 D2           xor dx, dx
5E05  B9 04 00        mov cx, 4
5E08  F7 F1           div cx
5E0A  31 D2           xor dx, dx
5E0C  52              push dx
5E0D  50              push ax
5E0E  9A 56 0D 4B 21  call far 214B:0D56
5E13  A3 00 83        mov word ptr [0x8300], ax
5E16  B0 1F           mov al, 0x1f
5E18  50              push ax
5E19  55              push bp
5E1A  E8 16 FC        call 0x5a33
5E1D  EB 04           jmp 0x5e23
loc_5E1F:
5E1F  55              push bp
5E20  E8 6B FC        call 0x5a8e
loc_5E23:
5E23  EB 16           jmp 0x5e3b
loc_5E25:
5E25  80 3E 26 83 00  cmp byte ptr [0x8326], 0
5E2A  75 0F           jne 0x5e3b
5E2C  C4 7E 06        les di, ptr [bp + 6]
5E2F  06              push es
5E30  57              push di
5E31  0E              push cs
5E32  E8 6A 28        call 0x869f
5E35  B0 1C           mov al, 0x1c
5E37  50              push ax
5E38  E8 68 CC        call 0x2aa3
loc_5E3B:
5E3B  89 EC           mov sp, bp
5E3D  5D              pop bp
5E3E  CA 04 00        retf 4

; ---- routine 0791:5E41  (found by: call)
sub_5E41:
5E41  55              push bp
5E42  89 E5           mov bp, sp
5E44  83 EC 04        sub sp, 4
5E47  C4 7E 06        les di, ptr [bp + 6]
5E4A  26 8B 05        mov ax, word ptr es:[di]
5E4D  89 46 FE        mov word ptr [bp - 2], ax
5E50  C7 46 FC 01 00  mov word ptr [bp - 4], 1
5E55  EB 03           jmp 0x5e5a
loc_5E57:
5E57  FF 46 FC        inc word ptr [bp - 4]
loc_5E5A:
5E5A  A0 03 83        mov al, byte ptr [0x8303]
5E5D  98              cwde
5E5E  8B F8           mov di, ax
5E60  8A 85 02 08     mov al, byte ptr [di + 0x802]
5E64  30 E4           xor ah, ah
5E66  50              push ax
5E67  9A B1 06 4B 21  call far 214B:06B1
5E6C  05 02 00        add ax, 2
5E6F  50              push ax
5E70  9A FA 06 4B 21  call far 214B:06FA
5E75  98              cwde
5E76  8B F8           mov di, ax
5E78  8A 85 20 79     mov al, byte ptr [di + 0x7920]
5E7C  98              cwde
5E7D  5A              pop dx
5E7E  F7 EA           imul dx
5E80  8B 7E FC        mov di, word ptr [bp - 4]
5E83  00 43 FD        add byte ptr [bp + di - 3], al
5E86  83 7E FC 02     cmp word ptr [bp - 4], 2
5E8A  75 CB           jne 0x5e57
5E8C  C4 7E 06        les di, ptr [bp + 6]
5E8F  06              push es
5E90  57              push di
5E91  0E              push cs
5E92  E8 0A 28        call 0x869f
5E95  FF 76 FE        push word ptr [bp - 2]
5E98  B8 06 00        mov ax, 6
5E9B  50              push ax
5E9C  C4 7E 06        les di, ptr [bp + 6]
5E9F  06              push es
5EA0  57              push di
5EA1  0E              push cs
5EA2  E8 1C D6        call 0x34c1
5EA5  89 EC           mov sp, bp
5EA7  5D              pop bp
5EA8  CA 04 00        retf 4

; ---- routine 0791:5EAB  (found by: call)
sub_5EAB:
5EAB  55              push bp
5EAC  89 E5           mov bp, sp
5EAE  C4 7E 06        les di, ptr [bp + 6]
5EB1  06              push es
5EB2  57              push di
5EB3  0E              push cs
5EB4  E8 E8 27        call 0x869f
5EB7  B0 20           mov al, 0x20
5EB9  50              push ax
5EBA  E8 E6 CB        call 0x2aa3
5EBD  E8 F1 D0        call 0x2fb1
5EC0  C6 06 FA 80 01  mov byte ptr [0x80fa], 1
5EC5  E8 CE CA        call 0x2996
5EC8  98              cwde
5EC9  8B F8           mov di, ax
5ECB  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
5ECF  30 E4           xor ah, ah
5ED1  50              push ax
5ED2  C4 7E 06        les di, ptr [bp + 6]
5ED5  06              push es
5ED6  57              push di
5ED7  0E              push cs
5ED8  E8 71 D9        call 0x384c
5EDB  C6 06 FA 80 00  mov byte ptr [0x80fa], 0
5EE0  89 EC           mov sp, bp
5EE2  5D              pop bp
5EE3  CA 04 00        retf 4
; data (not reached as code), 32 bytes
5EE6                  db 1E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
5EF6                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:5F06  (found by: call)
sub_5F06:
5F06  55              push bp
5F07  89 E5           mov bp, sp
5F09  83 EC 02        sub sp, 2
5F0C  A0 03 83        mov al, byte ptr [0x8303]
5F0F  88 46 FF        mov byte ptr [bp - 1], al
5F12  8B 7E 04        mov di, word ptr [bp + 4]
5F15  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5F19  36 C4 7D 06     les di, ptr ss:[di + 6]
5F1D  06              push es
5F1E  57              push di
5F1F  0E              push cs
5F20  E8 2E CC        call 0x2b51
5F23  88 46 FE        mov byte ptr [bp - 2], al
5F26  80 7E FF 00     cmp byte ptr [bp - 1], 0
5F2A  74 23           je 0x5f4f
5F2C  A0 27 83        mov al, byte ptr [0x8327]
5F2F  50              push ax
5F30  BF E6 5E        mov di, 0x5ee6
5F33  0E              push cs
5F34  57              push di
5F35  9A DF 08 E4 23  call far 23E4:08DF
5F3A  75 13           jne 0x5f4f
5F3C  8B 7E 04        mov di, word ptr [bp + 4]
5F3F  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5F43  36 C4 7D 06     les di, ptr ss:[di + 6]
5F47  06              push es
5F48  57              push di
5F49  0E              push cs
5F4A  E8 5E FF        call 0x5eab
5F4D  EB 35           jmp 0x5f84
loc_5F4F:
5F4F  8B 7E 04        mov di, word ptr [bp + 4]
5F52  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5F56  36 C4 7D 06     les di, ptr ss:[di + 6]
5F5A  06              push es
5F5B  57              push di
5F5C  0E              push cs
5F5D  E8 E1 FE        call 0x5e41
5F60  80 7E FF 00     cmp byte ptr [bp - 1], 0
5F64  74 08           je 0x5f6e
5F66  B0 20           mov al, 0x20
5F68  50              push ax
5F69  E8 37 CB        call 0x2aa3
5F6C  EB 0E           jmp 0x5f7c
loc_5F6E:
5F6E  8A 46 FE        mov al, byte ptr [bp - 2]
5F71  98              cwde
5F72  8B F8           mov di, ax
5F74  8A 85 0A 08     mov al, byte ptr [di + 0x80a]
5F78  50              push ax
5F79  E8 27 CB        call 0x2aa3
loc_5F7C:
5F7C  9A FA 06 4B 21  call far 214B:06FA
5F81  A2 03 83        mov byte ptr [0x8303], al
loc_5F84:
5F84  89 EC           mov sp, bp
5F86  5D              pop bp
5F87  C2 02 00        ret 2

; ---- routine 0791:5F8A  (found by: call)
sub_5F8A:
5F8A  55              push bp
5F8B  89 E5           mov bp, sp
5F8D  8B 7E 04        mov di, word ptr [bp + 4]
5F90  36 C4 7D 06     les di, ptr ss:[di + 6]
5F94  06              push es
5F95  57              push di
5F96  0E              push cs
5F97  E8 B7 CB        call 0x2b51
5F9A  08 C0           or al, al
5F9C  75 17           jne 0x5fb5
5F9E  A0 0B 83        mov al, byte ptr [0x830b]
5FA1  30 E4           xor ah, ah
5FA3  50              push ax
5FA4  E8 B6 A4        call 0x45d
5FA7  08 C0           or al, al
5FA9  74 0A           je 0x5fb5
5FAB  83 3E 00 83 00  cmp word ptr [0x8300], 0
5FB0  76 03           jbe 0x5fb5
5FB2  E9 CD 01        jmp 0x6182
loc_5FB5:
5FB5  80 3E 25 83 00  cmp byte ptr [0x8325], 0
5FBA  75 0A           jne 0x5fc6
5FBC  80 3E 24 83 00  cmp byte ptr [0x8324], 0
5FC1  75 03           jne 0x5fc6
5FC3  E9 BC 01        jmp 0x6182
loc_5FC6:
5FC6  BF F6 82        mov di, 0x82f6
5FC9  1E              push ds
5FCA  57              push di
5FCB  0E              push cs
5FCC  E8 90 23        call 0x835f
5FCF  3D 0A 00        cmp ax, 0xa
5FD2  77 04           ja 0x5fd8
5FD4  B0 00           mov al, 0
5FD6  EB 02           jmp 0x5fda
loc_5FD8:
5FD8  B0 01           mov al, 1
loc_5FDA:
5FDA  8B 7E 04        mov di, word ptr [bp + 4]
5FDD  36 88 45 FF     mov byte ptr ss:[di - 1], al
5FE1  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5FE6  74 6E           je 0x6056
5FE8  8B 7E 04        mov di, word ptr [bp + 4]
5FEB  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
5FF0  75 61           jne 0x6053
5FF2  B8 04 00        mov ax, 4
5FF5  50              push ax
5FF6  8B 7E 04        mov di, word ptr [bp + 4]
5FF9  36 C4 7D 06     les di, ptr ss:[di + 6]
5FFD  06              push es
5FFE  57              push di
5FFF  0E              push cs
6000  E8 79 C8        call 0x287c
6003  08 C0           or al, al
6005  74 4C           je 0x6053
6007  FF 36 F6 82     push word ptr [0x82f6]
600B  8B 7E 04        mov di, word ptr [bp + 4]
600E  36 C4 7D 06     les di, ptr ss:[di + 6]
6012  06              push es
6013  57              push di
6014  0E              push cs
6015  E8 A0 CE        call 0x2eb8
6018  08 C0           or al, al
601A  74 0F           je 0x602b
601C  8B 7E 04        mov di, word ptr [bp + 4]
601F  36 C4 7D 06     les di, ptr ss:[di + 6]
6023  06              push es
6024  57              push di
6025  0E              push cs
6026  E8 65 E0        call 0x408e
6029  EB 28           jmp 0x6053
loc_602B:
602B  FF 36 F6 82     push word ptr [0x82f6]
602F  8B 7E 04        mov di, word ptr [bp + 4]
6032  36 C4 7D 06     les di, ptr ss:[di + 6]
6036  06              push es
6037  57              push di
6038  0E              push cs
6039  E8 B4 CE        call 0x2ef0
603C  08 C0           or al, al
603E  74 0F           je 0x604f
6040  8B 7E 04        mov di, word ptr [bp + 4]
6043  36 C4 7D 06     les di, ptr ss:[di + 6]
6047  06              push es
6048  57              push di
6049  0E              push cs
604A  E8 92 DE        call 0x3edf
604D  EB 04           jmp 0x6053
loc_604F:
604F  55              push bp
6050  E8 B3 FE        call 0x5f06
loc_6053:
6053  E9 2C 01        jmp 0x6182
loc_6056:
6056  8B 7E 04        mov di, word ptr [bp + 4]
6059  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
605E  74 1C           je 0x607c
6060  B8 03 00        mov ax, 3
6063  50              push ax
6064  8B 7E 04        mov di, word ptr [bp + 4]
6067  36 C4 7D 06     les di, ptr ss:[di + 6]
606B  06              push es
606C  57              push di
606D  0E              push cs
606E  E8 0B C8        call 0x287c
6071  08 C0           or al, al
6073  74 04           je 0x6079
6075  55              push bp
6076  E8 8D FE        call 0x5f06
loc_6079:
6079  E9 06 01        jmp 0x6182
loc_607C:
607C  8B 7E 04        mov di, word ptr [bp + 4]
607F  36 80 7D FF 00  cmp byte ptr ss:[di - 1], 0
6084  75 6B           jne 0x60f1
6086  8B 7E 04        mov di, word ptr [bp + 4]
6089  36 C4 7D 06     les di, ptr ss:[di + 6]
608D  06              push es
608E  57              push di
608F  0E              push cs
6090  E8 95 CE        call 0x2f28
6093  08 C0           or al, al
6095  74 5A           je 0x60f1
6097  B8 09 00        mov ax, 9
609A  50              push ax
609B  8B 7E 04        mov di, word ptr [bp + 4]
609E  36 C4 7D 06     les di, ptr ss:[di + 6]
60A2  06              push es
60A3  57              push di
60A4  0E              push cs
60A5  E8 D4 C7        call 0x287c
60A8  08 C0           or al, al
60AA  74 45           je 0x60f1
60AC  8B 7E 04        mov di, word ptr [bp + 4]
60AF  36 C4 7D 06     les di, ptr ss:[di + 6]
60B3  06              push es
60B4  57              push di
60B5  0E              push cs
60B6  E8 98 CA        call 0x2b51
60B9  98              cwde
60BA  8B F8           mov di, ax
60BC  8A 85 08 08     mov al, byte ptr [di + 0x808]
60C0  30 E4           xor ah, ah
60C2  50              push ax
60C3  9A D0 06 4B 21  call far 214B:06D0
60C8  08 C0           or al, al
60CA  74 25           je 0x60f1
60CC  8B 7E 04        mov di, word ptr [bp + 4]
60CF  36 C4 7D 06     les di, ptr ss:[di + 6]
60D3  06              push es
60D4  57              push di
60D5  0E              push cs
60D6  E8 78 CA        call 0x2b51
60D9  98              cwde
60DA  8B F8           mov di, ax
60DC  8A 85 06 08     mov al, byte ptr [di + 0x806]
60E0  50              push ax
60E1  8B 7E 04        mov di, word ptr [bp + 4]
60E4  36 C4 7D 06     les di, ptr ss:[di + 6]
60E8  06              push es
60E9  57              push di
60EA  0E              push cs
60EB  E8 D7 DD        call 0x3ec5
60EE  E9 91 00        jmp 0x6182
loc_60F1:
60F1  83 3E 00 83 00  cmp word ptr [0x8300], 0
60F6  74 28           je 0x6120
60F8  8B 7E 04        mov di, word ptr [bp + 4]
60FB  36 C4 7D 06     les di, ptr ss:[di + 6]
60FF  06              push es
6100  57              push di
6101  0E              push cs
6102  E8 4C CA        call 0x2b51
6105  98              cwde
6106  8B F8           mov di, ax
6108  8A 85 04 08     mov al, byte ptr [di + 0x804]
610C  30 E4           xor ah, ah
610E  50              push ax
610F  8B 7E 04        mov di, word ptr [bp + 4]
6112  36 C4 7D 06     les di, ptr ss:[di + 6]
6116  06              push es
6117  57              push di
6118  0E              push cs
6119  E8 60 C7        call 0x287c
611C  08 C0           or al, al
611E  74 62           je 0x6182
loc_6120:
6120  8B 7E 04        mov di, word ptr [bp + 4]
6123  36 C4 7D 06     les di, ptr ss:[di + 6]
6127  06              push es
6128  57              push di
6129  0E              push cs
612A  E8 24 CA        call 0x2b51
612D  08 C0           or al, al
612F  74 34           je 0x6165
6131  A0 0B 83        mov al, byte ptr [0x830b]
6134  8B 7E 04        mov di, word ptr [bp + 4]
6137  36 C4 7D 06     les di, ptr ss:[di + 6]
613B  26 3A 45 06     cmp al, byte ptr es:[di + 6]
613F  75 12           jne 0x6153
6141  B0 19           mov al, 0x19
6143  50              push ax
6144  8B 7E 04        mov di, word ptr [bp + 4]
6147  36 C4 7D 06     les di, ptr ss:[di + 6]
614B  06              push es
614C  57              push di
614D  0E              push cs
614E  E8 D7 C9        call 0x2b28
6151  EB 10           jmp 0x6163
loc_6153:
6153  B0 23           mov al, 0x23
6155  50              push ax
6156  8B 7E 04        mov di, word ptr [bp + 4]
6159  36 C4 7D 06     les di, ptr ss:[di + 6]
615D  06              push es
615E  57              push di
615F  0E              push cs
6160  E8 C5 C9        call 0x2b28
loc_6163:
6163  EB 10           jmp 0x6175
loc_6165:
6165  B0 22           mov al, 0x22
6167  50              push ax
6168  8B 7E 04        mov di, word ptr [bp + 4]
616B  36 C4 7D 06     les di, ptr ss:[di + 6]
616F  06              push es
6170  57              push di
6171  0E              push cs
6172  E8 B3 C9        call 0x2b28
loc_6175:
6175  8B 7E 04        mov di, word ptr [bp + 4]
6178  36 C4 7D 06     les di, ptr ss:[di + 6]
617C  06              push es
617D  57              push di
617E  0E              push cs
617F  E8 1D 25        call 0x869f
loc_6182:
6182  89 EC           mov sp, bp
6184  5D              pop bp
6185  C2 02 00        ret 2

; ---- routine 0791:6188  (found by: call)
sub_6188:
6188  55              push bp
6189  89 E5           mov bp, sp
618B  83 EC 02        sub sp, 2
618E  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
6193  75 51           jne 0x61e6
6195  C4 7E 06        les di, ptr [bp + 6]
6198  26 80 7D 12 0D  cmp byte ptr es:[di + 0x12], 0xd
619D  74 47           je 0x61e6
619F  C4 7E 06        les di, ptr [bp + 6]
61A2  06              push es
61A3  57              push di
61A4  0E              push cs
61A5  E8 44 CB        call 0x2cec
61A8  08 C0           or al, al
61AA  74 3A           je 0x61e6
61AC  C4 7E 06        les di, ptr [bp + 6]
61AF  26 8A 45 06     mov al, byte ptr es:[di + 6]
61B3  30 E4           xor ah, ah
61B5  50              push ax
61B6  E8 A4 A2        call 0x45d
61B9  08 C0           or al, al
61BB  74 0B           je 0x61c8
61BD  C4 7E 06        les di, ptr [bp + 6]
61C0  06              push es
61C1  57              push di
61C2  0E              push cs
61C3  E8 70 F9        call 0x5b36
61C6  EB 1E           jmp 0x61e6
loc_61C8:
61C8  80 3E 26 83 00  cmp byte ptr [0x8326], 0
61CD  75 17           jne 0x61e6
61CF  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
61D4  75 10           jne 0x61e6
61D6  A0 0B 83        mov al, byte ptr [0x830b]
61D9  C4 7E 06        les di, ptr [bp + 6]
61DC  26 3A 45 06     cmp al, byte ptr es:[di + 6]
61E0  74 04           je 0x61e6
61E2  55              push bp
61E3  E8 A4 FD        call 0x5f8a
loc_61E6:
61E6  89 EC           mov sp, bp
61E8  5D              pop bp
61E9  CA 04 00        retf 4

; ---- routine 0791:61EC  (found by: call)
sub_61EC:
61EC  55              push bp
61ED  89 E5           mov bp, sp
61EF  C6 06 25 83 00  mov byte ptr [0x8325], 0
61F4  E8 6B 1E        call 0x8062
61F7  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
61FC  74 14           je 0x6212
61FE  E8 95 C7        call 0x2996
6201  98              cwde
6202  8B F8           mov di, ax
6204  8A 85 68 06     mov al, byte ptr [di + 0x668]
6208  30 E4           xor ah, ah
620A  05 0A 00        add ax, 0xa
620D  A2 0B 83        mov byte ptr [0x830b], al
6210  EB 1C           jmp 0x622e
loc_6212:
6212  E8 81 C7        call 0x2996
6215  08 C0           or al, al
6217  74 04           je 0x621d
6219  B0 00           mov al, 0
621B  EB 02           jmp 0x621f
loc_621D:
621D  B0 01           mov al, 1
loc_621F:
621F  98              cwde
6220  8B F8           mov di, ax
6222  8A 85 68 06     mov al, byte ptr [di + 0x668]
6226  30 E4           xor ah, ah
6228  05 0A 00        add ax, 0xa
622B  A2 0B 83        mov byte ptr [0x830b], al
loc_622E:
622E  C6 06 39 7C 00  mov byte ptr [0x7c39], 0
6233  E8 DF C7        call 0x2a15
6236  B0 01           mov al, 1
6238  50              push ax
6239  E8 ED C6        call 0x2929
623C  89 EC           mov sp, bp
623E  5D              pop bp
623F  C3              ret

; ---- routine 0791:6240  (found by: call)
sub_6240:
6240  55              push bp
6241  89 E5           mov bp, sp
6243  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
6248  74 06           je 0x6250
624A  E8 9F FF        call 0x61ec
624D  E9 E1 00        jmp 0x6331
loc_6250:
6250  C4 7E 06        les di, ptr [bp + 6]
6253  26 8A 45 06     mov al, byte ptr es:[di + 6]
6257  3A 06 0B 83     cmp al, byte ptr [0x830b]
625B  74 49           je 0x62a6
625D  E8 36 C7        call 0x2996
6260  08 C0           or al, al
6262  74 04           je 0x6268
6264  B0 00           mov al, 0
6266  EB 02           jmp 0x626a
loc_6268:
6268  B0 01           mov al, 1
loc_626A:
626A  98              cwde
626B  8B F8           mov di, ax
626D  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
6271  50              push ax
6272  E8 21 C7        call 0x2996
6275  98              cwde
6276  8B F8           mov di, ax
6278  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
627C  5A              pop dx
627D  3A C2           cmp al, dl
627F  72 19           jb 0x629a
6281  A0 0B 83        mov al, byte ptr [0x830b]
6284  30 E4           xor ah, ah
6286  BA 16 00        mov dx, 0x16
6289  F7 E2           mul dx
628B  8B F8           mov di, ax
628D  8B 85 E8 80     mov ax, word ptr [di - 0x7f18]
6291  C4 7E 06        les di, ptr [bp + 6]
6294  26 89 45 07     mov word ptr es:[di + 7], ax
6298  EB 09           jmp 0x62a3
loc_629A:
629A  C4 7E 06        les di, ptr [bp + 6]
629D  06              push es
629E  57              push di
629F  0E              push cs
62A0  E8 B1 E0        call 0x4354
loc_62A3:
62A3  E9 8B 00        jmp 0x6331
loc_62A6:
62A6  C4 7E 06        les di, ptr [bp + 6]
62A9  06              push es
62AA  57              push di
62AB  0E              push cs
62AC  E8 16 CA        call 0x2cc5
62AF  08 C0           or al, al
62B1  75 0D           jne 0x62c0
62B3  B8 10 00        mov ax, 0x10
62B6  50              push ax
62B7  9A D0 06 4B 21  call far 214B:06D0
62BC  08 C0           or al, al
62BE  74 71           je 0x6331
loc_62C0:
62C0  C4 7E 06        les di, ptr [bp + 6]
62C3  06              push es
62C4  57              push di
62C5  0E              push cs
62C6  E8 1C C9        call 0x2be5
62C9  98              cwde
62CA  B9 05 00        mov cx, 5
62CD  F7 E9           imul cx
62CF  8B D0           mov dx, ax
62D1  C4 7E 06        les di, ptr [bp + 6]
62D4  26 8A 45 08     mov al, byte ptr es:[di + 8]
62D8  98              cwde
62D9  3B C2           cmp ax, dx
62DB  74 18           je 0x62f5
62DD  C4 7E 06        les di, ptr [bp + 6]
62E0  06              push es
62E1  57              push di
62E2  0E              push cs
62E3  E8 FF C8        call 0x2be5
62E6  98              cwde
62E7  B9 05 00        mov cx, 5
62EA  F7 E9           imul cx
62EC  C4 7E 06        les di, ptr [bp + 6]
62EF  26 88 45 08     mov byte ptr es:[di + 8], al
62F3  EB 3C           jmp 0x6331
loc_62F5:
62F5  C4 7E 06        les di, ptr [bp + 6]
62F8  26 8A 45 07     mov al, byte ptr es:[di + 7]
62FC  98              cwde
62FD  09 C0           or ax, ax
62FF  79 02           jns 0x6303
6301  F7 D8           neg ax
loc_6303:
6303  3D 06 00        cmp ax, 6
6306  74 26           je 0x632e
6308  C4 7E 06        les di, ptr [bp + 6]
630B  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
6310  7C 04           jl 0x6316
6312  B0 00           mov al, 0
6314  EB 02           jmp 0x6318
loc_6316:
6316  B0 01           mov al, 1
loc_6318:
6318  98              cwde
6319  8B F8           mov di, ax
631B  8A 85 20 79     mov al, byte ptr [di + 0x7920]
631F  98              cwde
6320  B9 06 00        mov cx, 6
6323  F7 E9           imul cx
6325  C4 7E 06        les di, ptr [bp + 6]
6328  26 88 45 07     mov byte ptr es:[di + 7], al
632C  EB 03           jmp 0x6331
loc_632E:
632E  E8 BB FE        call 0x61ec
loc_6331:
6331  89 EC           mov sp, bp
6333  5D              pop bp
6334  CA 04 00        retf 4

