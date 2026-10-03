; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 9 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:6C21  (found by: call)
sub_6C21:
6C21  55              push bp
6C22  89 E5           mov bp, sp
6C24  83 EC 06        sub sp, 6
6C27  C4 3E 23 A9     les di, ptr [0xa923]
6C2B  89 7E FB        mov word ptr [bp - 5], di
6C2E  8C 46 FD        mov word ptr [bp - 3], es
6C31  8B 7E 04        mov di, word ptr [bp + 4]
6C34  36 80 7D FE 00  cmp byte ptr ss:[di - 2], 0
6C39  74 14           je 0x6c4f
6C3B  BF A6 14        mov di, 0x14a6
6C3E  1E              push ds
6C3F  57              push di
6C40  BF 6A A9        mov di, 0xa96a
6C43  1E              push ds
6C44  57              push di
6C45  9A 29 03 4B 21  call far 214B:0329
6C4A  9A DD 08 4B 21  call far 214B:08DD
loc_6C4F:
6C4F  80 7E 06 00     cmp byte ptr [bp + 6], 0
6C53  74 24           je 0x6c79
6C55  C4 7E FB        les di, ptr [bp - 5]
6C58  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6C5C  B1 03           mov cl, 3
6C5E  D3 E0           shl ax, cl
6C60  C4 3E 2B A9     les di, ptr [0xa92b]
6C64  03 F8           add di, ax
6C66  81 C7 F8 FF     add di, 0xfff8
6C6A  06              push es
6C6B  57              push di
6C6C  9A 0D E8 91 07  call far 0791:E80D
6C71  08 C0           or al, al
6C73  75 04           jne 0x6c79
6C75  B0 00           mov al, 0
6C77  EB 02           jmp 0x6c7b
loc_6C79:
6C79  B0 01           mov al, 1
loc_6C7B:
6C7B  88 46 FF        mov byte ptr [bp - 1], al
6C7E  8A 46 FF        mov al, byte ptr [bp - 1]
6C81  89 EC           mov sp, bp
6C83  5D              pop bp
6C84  C2 04 00        ret 4
; data (not reached as code), 32 bytes
6C87                  db 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
6C97                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 000E:6CA7  (found by: call)
sub_6CA7:
6CA7  55              push bp
6CA8  89 E5           mov bp, sp
6CAA  83 EC 16        sub sp, 0x16
6CAD  C4 3E 23 A9     les di, ptr [0xa923]
6CB1  89 7E F0        mov word ptr [bp - 0x10], di
6CB4  8C 46 F2        mov word ptr [bp - 0xe], es
6CB7  C4 7E F0        les di, ptr [bp - 0x10]
6CBA  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6CBE  89 46 FA        mov word ptr [bp - 6], ax
6CC1  C6 46 FE 00     mov byte ptr [bp - 2], 0
6CC5  C4 7E F0        les di, ptr [bp - 0x10]
6CC8  81 C7 4E 00     add di, 0x4e
6CCC  06              push es
6CCD  57              push di
6CCE  B8 06 00        mov ax, 6
6CD1  50              push ax
6CD2  31 C0           xor ax, ax
6CD4  50              push ax
6CD5  9A 18 00 4B 21  call far 214B:0018
6CDA  8D 7E F4        lea di, [bp - 0xc]
6CDD  16              push ss
6CDE  57              push di
6CDF  B8 04 00        mov ax, 4
6CE2  50              push ax
6CE3  31 C0           xor ax, ax
6CE5  50              push ax
6CE6  9A 18 00 4B 21  call far 214B:0018
6CEB  C4 7E F0        les di, ptr [bp - 0x10]
6CEE  26 8A 05        mov al, byte ptr es:[di]
6CF1  30 E4           xor ah, ah
6CF3  89 46 EE        mov word ptr [bp - 0x12], ax
6CF6  B8 01 00        mov ax, 1
6CF9  3B 46 EE        cmp ax, word ptr [bp - 0x12]
6CFC  77 46           ja 0x6d44
6CFE  89 46 F8        mov word ptr [bp - 8], ax
6D01  EB 03           jmp 0x6d06
loc_6D03:
6D03  FF 46 F8        inc word ptr [bp - 8]
loc_6D06:
6D06  8B 46 F8        mov ax, word ptr [bp - 8]
6D09  05 80 00        add ax, 0x80
6D0C  BA 03 00        mov dx, 3
6D0F  F7 E2           mul dx
6D11  C4 3E 1F A9     les di, ptr [0xa91f]
6D15  03 F8           add di, ax
6D17  26 8A 05        mov al, byte ptr es:[di]
6D1A  30 E4           xor ah, ah
6D1C  BA BF 00        mov dx, 0xbf
6D1F  F7 E2           mul dx
6D21  C4 3E 17 A9     les di, ptr [0xa917]
6D25  03 F8           add di, ax
6D27  89 7E EA        mov word ptr [bp - 0x16], di
6D2A  8C 46 EC        mov word ptr [bp - 0x14], es
6D2D  C4 7E EA        les di, ptr [bp - 0x16]
6D30  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
6D34  30 E4           xor ah, ah
6D36  8B F8           mov di, ax
6D38  C6 43 F3 01     mov byte ptr [bp + di - 0xd], 1
6D3C  8B 46 F8        mov ax, word ptr [bp - 8]
6D3F  3B 46 EE        cmp ax, word ptr [bp - 0x12]
6D42  75 BF           jne 0x6d03
loc_6D44:
6D44  C4 7E F0        les di, ptr [bp - 0x10]
6D47  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6D4B  C4 7E F0        les di, ptr [bp - 0x10]
6D4E  26 3B 45 28     cmp ax, word ptr es:[di + 0x28]
6D52  72 03           jb 0x6d57
6D54  E9 12 03        jmp 0x7069
loc_6D57:
6D57  C4 7E F0        les di, ptr [bp - 0x10]
6D5A  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6D5E  B1 03           mov cl, 3
6D60  D3 E0           shl ax, cl
6D62  C4 3E 2B A9     les di, ptr [0xa92b]
6D66  03 F8           add di, ax
6D68  81 C7 F8 FF     add di, 0xfff8
6D6C  89 7E EC        mov word ptr [bp - 0x14], di
6D6F  8C 46 EE        mov word ptr [bp - 0x12], es
6D72  C6 46 FC 00     mov byte ptr [bp - 4], 0
6D76  C4 7E EC        les di, ptr [bp - 0x14]
6D79  26 80 3D FE     cmp byte ptr es:[di], 0xfe
6D7D  75 2F           jne 0x6dae
6D7F  C4 7E EC        les di, ptr [bp - 0x14]
6D82  26 FF 75 06     push word ptr es:[di + 6]
6D86  9A 77 0B 71 17  call far 1771:0B77
6D8B  08 C0           or al, al
6D8D  75 10           jne 0x6d9f
6D8F  C4 7E EC        les di, ptr [bp - 0x14]
6D92  26 FF 75 04     push word ptr es:[di + 4]
6D96  9A 77 0B 71 17  call far 1771:0B77
6D9B  08 C0           or al, al
6D9D  74 04           je 0x6da3
loc_6D9F:
6D9F  B0 00           mov al, 0
6DA1  EB 02           jmp 0x6da5
loc_6DA3:
6DA3  B0 01           mov al, 1
loc_6DA5:
6DA5  50              push ax
6DA6  55              push bp
6DA7  E8 77 FE        call 0x6c21
6DAA  08 C0           or al, al
6DAC  75 67           jne 0x6e15
loc_6DAE:
6DAE  C4 7E EC        les di, ptr [bp - 0x14]
6DB1  26 8A 45 02     mov al, byte ptr es:[di + 2]
6DB5  50              push ax
6DB6  BF 5A 69        mov di, 0x695a
6DB9  1E              push ds
6DBA  57              push di
6DBB  9A DF 08 E4 23  call far 23E4:08DF
6DC0  74 0B           je 0x6dcd
6DC2  B0 01           mov al, 1
6DC4  50              push ax
6DC5  55              push bp
6DC6  E8 58 FE        call 0x6c21
6DC9  08 C0           or al, al
6DCB  75 48           jne 0x6e15
loc_6DCD:
6DCD  C4 7E EC        les di, ptr [bp - 0x14]
6DD0  26 8B 45 06     mov ax, word ptr es:[di + 6]
6DD4  BA BF 00        mov dx, 0xbf
6DD7  F7 E2           mul dx
6DD9  C4 3E 17 A9     les di, ptr [0xa917]
6DDD  03 F8           add di, ax
6DDF  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
6DE3  30 E4           xor ah, ah
6DE5  8B F8           mov di, ax
6DE7  80 7B F3 00     cmp byte ptr [bp + di - 0xd], 0
6DEB  75 03           jne 0x6df0
6DED  E9 23 02        jmp 0x7013
loc_6DF0:
6DF0  C4 7E EC        les di, ptr [bp - 0x14]
6DF3  26 8A 45 02     mov al, byte ptr es:[di + 2]
6DF7  50              push ax
6DF8  BF 7A 69        mov di, 0x697a
6DFB  1E              push ds
6DFC  57              push di
6DFD  9A DF 08 E4 23  call far 23E4:08DF
6E02  75 03           jne 0x6e07
6E04  E9 0C 02        jmp 0x7013
loc_6E07:
6E07  B0 01           mov al, 1
6E09  50              push ax
6E0A  55              push bp
6E0B  E8 13 FE        call 0x6c21
6E0E  08 C0           or al, al
6E10  75 03           jne 0x6e15
6E12  E9 FE 01        jmp 0x7013
loc_6E15:
6E15  C4 7E EC        les di, ptr [bp - 0x14]
6E18  26 8A 45 02     mov al, byte ptr es:[di + 2]
6E1C  50              push ax
6E1D  BF 87 6C        mov di, 0x6c87
6E20  0E              push cs
6E21  57              push di
6E22  9A DF 08 E4 23  call far 23E4:08DF
6E27  75 03           jne 0x6e2c
6E29  E9 81 00        jmp 0x6ead
loc_6E2C:
6E2C  C6 46 FD 00     mov byte ptr [bp - 3], 0
6E30  EB 03           jmp 0x6e35
loc_6E32:
6E32  FE 46 FD        inc byte ptr [bp - 3]
loc_6E35:
6E35  8A 46 FD        mov al, byte ptr [bp - 3]
6E38  98              cwde
6E39  D1 E0           shl ax, 1
6E3B  C4 7E EC        les di, ptr [bp - 0x14]
6E3E  03 F8           add di, ax
6E40  26 FF 75 04     push word ptr es:[di + 4]
6E44  9A 77 0B 71 17  call far 1771:0B77
6E49  08 C0           or al, al
6E4B  74 5A           je 0x6ea7
6E4D  8A 46 FD        mov al, byte ptr [bp - 3]
6E50  98              cwde
6E51  D1 E0           shl ax, 1
6E53  C4 7E EC        les di, ptr [bp - 0x14]
6E56  03 F8           add di, ax
6E58  26 8B 45 04     mov ax, word ptr es:[di + 4]
6E5C  BA BF 00        mov dx, 0xbf
6E5F  F7 E2           mul dx
6E61  C4 3E 17 A9     les di, ptr [0xa917]
6E65  03 F8           add di, ax
6E67  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
6E6B  30 E4           xor ah, ah
6E6D  2D 80 00        sub ax, 0x80
6E70  C4 7E F0        les di, ptr [bp - 0x10]
6E73  03 F8           add di, ax
6E75  26 C6 45 13 01  mov byte ptr es:[di + 0x13], 1
6E7A  8A 46 FD        mov al, byte ptr [bp - 3]
6E7D  98              cwde
6E7E  D1 E0           shl ax, 1
6E80  C4 7E EC        les di, ptr [bp - 0x14]
6E83  03 F8           add di, ax
6E85  26 8B 45 04     mov ax, word ptr es:[di + 4]
6E89  BA BF 00        mov dx, 0xbf
6E8C  F7 E2           mul dx
6E8E  C4 3E 17 A9     les di, ptr [0xa917]
6E92  03 F8           add di, ax
6E94  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
6E98  30 E4           xor ah, ah
6E9A  2D 80 00        sub ax, 0x80
6E9D  C4 7E F0        les di, ptr [bp - 0x10]
6EA0  03 F8           add di, ax
6EA2  26 C6 45 41 00  mov byte ptr es:[di + 0x41], 0
loc_6EA7:
6EA7  80 7E FD 01     cmp byte ptr [bp - 3], 1
6EAB  75 85           jne 0x6e32
loc_6EAD:
6EAD  C6 46 FD 00     mov byte ptr [bp - 3], 0
6EB1  EB 03           jmp 0x6eb6
loc_6EB3:
6EB3  FE 46 FD        inc byte ptr [bp - 3]
loc_6EB6:
6EB6  8A 46 FD        mov al, byte ptr [bp - 3]
6EB9  98              cwde
6EBA  D1 E0           shl ax, 1
6EBC  C4 7E EC        les di, ptr [bp - 0x14]
6EBF  03 F8           add di, ax
6EC1  26 FF 75 04     push word ptr es:[di + 4]
6EC5  9A 77 0B 71 17  call far 1771:0B77
6ECA  08 C0           or al, al
6ECC  74 04           je 0x6ed2
6ECE  C6 46 FC 01     mov byte ptr [bp - 4], 1
loc_6ED2:
6ED2  80 7E FD 01     cmp byte ptr [bp - 3], 1
6ED6  75 DB           jne 0x6eb3
6ED8  C4 7E EC        les di, ptr [bp - 0x14]
6EDB  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
6EE0  75 1F           jne 0x6f01
6EE2  C4 7E F0        les di, ptr [bp - 0x10]
6EE5  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6EE9  B1 03           mov cl, 3
6EEB  D3 E0           shl ax, cl
6EED  C4 3E 2B A9     les di, ptr [0xa92b]
6EF1  03 F8           add di, ax
6EF3  81 C7 F8 FF     add di, 0xfff8
6EF7  06              push es
6EF8  57              push di
6EF9  9A 2F BB 91 07  call far 0791:BB2F
6EFE  E9 FC 00        jmp 0x6ffd
loc_6F01:
6F01  C4 7E F0        les di, ptr [bp - 0x10]
6F04  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6F08  B1 03           mov cl, 3
6F0A  D3 E0           shl ax, cl
6F0C  C4 3E 2B A9     les di, ptr [0xa92b]
6F10  03 F8           add di, ax
6F12  81 C7 F8 FF     add di, 0xfff8
6F16  06              push es
6F17  57              push di
6F18  9A F6 F1 91 07  call far 0791:F1F6
6F1D  80 7E FC 00     cmp byte ptr [bp - 4], 0
6F21  74 6E           je 0x6f91
6F23  C4 7E F0        les di, ptr [bp - 0x10]
6F26  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6F2A  B1 03           mov cl, 3
6F2C  D3 E0           shl ax, cl
6F2E  C4 3E 2B A9     les di, ptr [0xa92b]
6F32  03 F8           add di, ax
6F34  26 80 7D FA 01  cmp byte ptr es:[di - 6], 1
6F39  74 56           je 0x6f91
6F3B  C6 46 FD 00     mov byte ptr [bp - 3], 0
6F3F  EB 03           jmp 0x6f44
loc_6F41:
6F41  FE 46 FD        inc byte ptr [bp - 3]
loc_6F44:
6F44  8A 46 FD        mov al, byte ptr [bp - 3]
6F47  98              cwde
6F48  D1 E0           shl ax, 1
6F4A  C4 7E EC        les di, ptr [bp - 0x14]
6F4D  03 F8           add di, ax
6F4F  26 8B 45 04     mov ax, word ptr es:[di + 4]
6F53  BA BF 00        mov dx, 0xbf
6F56  F7 E2           mul dx
6F58  C4 3E 17 A9     les di, ptr [0xa917]
6F5C  03 F8           add di, ax
6F5E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
6F62  30 E4           xor ah, ah
6F64  50              push ax
6F65  C4 7E F0        les di, ptr [bp - 0x10]
6F68  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6F6C  B1 03           mov cl, 3
6F6E  D3 E0           shl ax, cl
6F70  C4 3E 2B A9     les di, ptr [0xa92b]
6F74  03 F8           add di, ax
6F76  81 C7 F8 FF     add di, 0xfff8
6F7A  06              push es
6F7B  57              push di
6F7C  8A 46 FD        mov al, byte ptr [bp - 3]
6F7F  50              push ax
6F80  9A 1C B7 91 07  call far 0791:B71C
6F85  50              push ax
6F86  9A CC B6 91 07  call far 0791:B6CC
6F8B  80 7E FD 01     cmp byte ptr [bp - 3], 1
6F8F  75 B0           jne 0x6f41
loc_6F91:
6F91  C6 46 FD 00     mov byte ptr [bp - 3], 0
6F95  EB 03           jmp 0x6f9a
loc_6F97:
6F97  FE 46 FD        inc byte ptr [bp - 3]
loc_6F9A:
6F9A  8A 46 FD        mov al, byte ptr [bp - 3]
6F9D  98              cwde
6F9E  D1 E0           shl ax, 1
6FA0  C4 7E EC        les di, ptr [bp - 0x14]
6FA3  03 F8           add di, ax
6FA5  26 FF 75 04     push word ptr es:[di + 4]
6FA9  9A 77 0B 71 17  call far 1771:0B77
6FAE  08 C0           or al, al
6FB0  74 29           je 0x6fdb
6FB2  8A 46 FD        mov al, byte ptr [bp - 3]
6FB5  98              cwde
6FB6  D1 E0           shl ax, 1
6FB8  C4 7E EC        les di, ptr [bp - 0x14]
6FBB  03 F8           add di, ax
6FBD  26 FF 75 04     push word ptr es:[di + 4]
6FC1  C4 7E F0        les di, ptr [bp - 0x10]
6FC4  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6FC8  B1 03           mov cl, 3
6FCA  D3 E0           shl ax, cl
6FCC  C4 3E 2B A9     les di, ptr [0xa92b]
6FD0  03 F8           add di, ax
6FD2  81 C7 F8 FF     add di, 0xfff8
6FD6  06              push es
6FD7  57              push di
6FD8  E8 33 DE        call 0x4e0e
loc_6FDB:
6FDB  80 7E FD 01     cmp byte ptr [bp - 3], 1
6FDF  75 B6           jne 0x6f97
6FE1  C4 7E F0        les di, ptr [bp - 0x10]
6FE4  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
6FE8  B1 03           mov cl, 3
6FEA  D3 E0           shl ax, cl
6FEC  C4 3E 2B A9     les di, ptr [0xa92b]
6FF0  03 F8           add di, ax
6FF2  81 C7 F8 FF     add di, 0xfff8
6FF6  06              push es
6FF7  57              push di
6FF8  9A FA B7 91 07  call far 0791:B7FA
loc_6FFD:
6FFD  C4 7E F0        les di, ptr [bp - 0x10]
7000  26 FF 45 26     inc word ptr es:[di + 0x26]
7004  9A 57 87 71 17  call far 1771:8757
7009  80 7E FC 00     cmp byte ptr [bp - 4], 0
700D  74 02           je 0x7011
700F  EB 5D           jmp 0x706e
loc_7011:
7011  EB 04           jmp 0x7017
loc_7013:
7013  55              push bp
7014  E8 59 F9        call 0x6970
loc_7017:
7017  C4 7E EC        les di, ptr [bp - 0x14]
701A  26 80 7D 02 CB  cmp byte ptr es:[di + 2], 0xcb
701F  74 2A           je 0x704b
7021  C4 7E EC        les di, ptr [bp - 0x14]
7024  26 80 7D 02 67  cmp byte ptr es:[di + 2], 0x67
7029  75 3B           jne 0x7066
702B  C4 7E EC        les di, ptr [bp - 0x14]
702E  26 8B 45 06     mov ax, word ptr es:[di + 6]
7032  BA BF 00        mov dx, 0xbf
7035  F7 E2           mul dx
7037  C4 3E 17 A9     les di, ptr [0xa917]
703B  03 F8           add di, ax
703D  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
7041  30 E4           xor ah, ah
7043  8B F8           mov di, ax
7045  80 7B F3 00     cmp byte ptr [bp + di - 0xd], 0
7049  74 1B           je 0x7066
loc_704B:
704B  C4 7E F0        les di, ptr [bp - 0x10]
704E  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
7052  48              dec ax
7053  B1 03           mov cl, 3
7055  D3 E0           shl ax, cl
7057  C4 3E 2B A9     les di, ptr [0xa92b]
705B  03 F8           add di, ax
705D  81 C7 F8 FF     add di, 0xfff8
7061  06              push es
7062  57              push di
7063  E8 1F F6        call 0x6685
loc_7066:
7066  E9 DB FC        jmp 0x6d44
loc_7069:
7069  9A 57 87 71 17  call far 1771:8757
loc_706E:
706E  89 EC           mov sp, bp
7070  5D              pop bp
7071  C3              ret

; ---- routine 000E:7072  (found by: call)
sub_7072:
7072  55              push bp
7073  89 E5           mov bp, sp
7075  83 EC 02        sub sp, 2
7078  B0 00           mov al, 0
707A  08 C0           or al, al
707C  74 0B           je 0x7089
707E  C4 3E 23 A9     les di, ptr [0xa923]
7082  26 83 7D 38 02  cmp word ptr es:[di + 0x38], 2
7087  73 04           jae 0x708d
loc_7089:
7089  B0 00           mov al, 0
708B  EB 02           jmp 0x708f
loc_708D:
708D  B0 01           mov al, 1
loc_708F:
708F  88 46 FF        mov byte ptr [bp - 1], al
7092  8A 46 FF        mov al, byte ptr [bp - 1]
7095  89 EC           mov sp, bp
7097  5D              pop bp
7098  C3              ret
; data (not reached as code), 32 bytes
7099                  db AC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
70A9                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 000E:70B9  (found by: call)
sub_70B9:
70B9  55              push bp
70BA  89 E5           mov bp, sp
70BC  83 EC 08        sub sp, 8
70BF  C4 3E 23 A9     les di, ptr [0xa923]
70C3  89 7E FA        mov word ptr [bp - 6], di
70C6  8C 46 FC        mov word ptr [bp - 4], es
70C9  C4 7E FA        les di, ptr [bp - 6]
70CC  26 C6 45 01 01  mov byte ptr es:[di + 1], 1
70D1  E8 D3 FB        call 0x6ca7
70D4  C4 7E FA        les di, ptr [bp - 6]
70D7  26 8B 45 26     mov ax, word ptr es:[di + 0x26]
70DB  C4 7E FA        les di, ptr [bp - 6]
70DE  26 3B 45 28     cmp ax, word ptr es:[di + 0x28]
70E2  74 02           je 0x70e6
70E4  EB 74           jmp 0x715a
loc_70E6:
70E6  9A 08 82 71 17  call far 1771:8208
70EB  E8 84 FF        call 0x7072
70EE  08 C0           or al, al
70F0  74 02           je 0x70f4
70F2  EB 66           jmp 0x715a
loc_70F4:
70F4  9A B1 76 71 17  call far 1771:76B1
70F9  C4 7E FA        les di, ptr [bp - 6]
70FC  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
7100  50              push ax
7101  BF 99 70        mov di, 0x7099
7104  0E              push cs
7105  57              push di
7106  9A DF 08 E4 23  call far 23E4:08DF
710B  74 4D           je 0x715a
710D  C4 7E FA        les di, ptr [bp - 6]
7110  26 8A 05        mov al, byte ptr es:[di]
7113  30 E4           xor ah, ah
7115  89 46 F8        mov word ptr [bp - 8], ax
7118  B8 01 00        mov ax, 1
711B  3B 46 F8        cmp ax, word ptr [bp - 8]
711E  77 3A           ja 0x715a
7120  89 46 FE        mov word ptr [bp - 2], ax
7123  EB 03           jmp 0x7128
loc_7125:
7125  FF 46 FE        inc word ptr [bp - 2]
loc_7128:
7128  8B 46 FE        mov ax, word ptr [bp - 2]
712B  C4 7E FA        les di, ptr [bp - 6]
712E  03 F8           add di, ax
7130  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
7135  75 1B           jne 0x7152
7137  8B 46 FE        mov ax, word ptr [bp - 2]
713A  05 80 00        add ax, 0x80
713D  BA 03 00        mov dx, 3
7140  F7 E2           mul dx
7142  C4 3E 1F A9     les di, ptr [0xa91f]
7146  03 F8           add di, ax
7148  26 8A 05        mov al, byte ptr es:[di]
714B  30 E4           xor ah, ah
714D  50              push ax
714E  0E              push cs
714F  E8 79 EF        call 0x60cb
loc_7152:
7152  8B 46 FE        mov ax, word ptr [bp - 2]
7155  3B 46 F8        cmp ax, word ptr [bp - 8]
7158  75 CB           jne 0x7125
loc_715A:
715A  89 EC           mov sp, bp
715C  5D              pop bp
715D  C3              ret

; ---- routine 000E:715E  (found by: call)
sub_715E:
715E  55              push bp
715F  89 E5           mov bp, sp
7161  81 EC 06 01     sub sp, 0x106
7165  8B 46 08        mov ax, word ptr [bp + 8]
7168  BA BF 00        mov dx, 0xbf
716B  F7 E2           mul dx
716D  C4 3E 17 A9     les di, ptr [0xa917]
7171  03 F8           add di, ax
7173  89 7E FA        mov word ptr [bp - 6], di
7176  8C 46 FC        mov word ptr [bp - 4], es
7179  83 7E 08 00     cmp word ptr [bp + 8], 0
717D  75 03           jne 0x7182
717F  E9 96 00        jmp 0x7218
loc_7182:
7182  A0 B2 AA        mov al, byte ptr [0xaab2]
7185  30 E4           xor ah, ah
7187  89 46 FE        mov word ptr [bp - 2], ax
718A  C4 7E FA        les di, ptr [bp - 6]
718D  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
7191  30 E4           xor ah, ah
7193  8B F8           mov di, ax
7195  8A 85 05 69     mov al, byte ptr [di + 0x6905]
7199  50              push ax
719A  C4 7E FA        les di, ptr [bp - 6]
719D  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
71A1  30 E4           xor ah, ah
71A3  8B F8           mov di, ax
71A5  B1 03           mov cl, 3
71A7  D3 E7           shl di, cl
71A9  81 C7 92 6E     add di, 0x6e92
71AD  1E              push ds
71AE  57              push di
71AF  8B 46 06        mov ax, word ptr [bp + 6]
71B2  40              inc ax
71B3  50              push ax
71B4  B0 03           mov al, 3
71B6  50              push ax
71B7  BF 6E A9        mov di, 0xa96e
71BA  1E              push ds
71BB  57              push di
71BC  9A C8 02 4B 21  call far 214B:02C8
71C1  8A 46 FE        mov al, byte ptr [bp - 2]
71C4  50              push ax
71C5  8D BE FA FE     lea di, [bp - 0x106]
71C9  16              push ss
71CA  57              push di
71CB  C4 7E FA        les di, ptr [bp - 6]
71CE  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
71D2  30 E4           xor ah, ah
71D4  31 D2           xor dx, dx
71D6  52              push dx
71D7  50              push ax
71D8  9A DA 09 4B 21  call far 214B:09DA
71DD  8A 46 06        mov al, byte ptr [bp + 6]
71E0  50              push ax
71E1  B0 0D           mov al, 0xd
71E3  50              push ax
71E4  BF 6E A9        mov di, 0xa96e
71E7  1E              push ds
71E8  57              push di
71E9  9A 05 02 4B 21  call far 214B:0205
71EE  8D BE FA FE     lea di, [bp - 0x106]
71F2  16              push ss
71F3  57              push di
71F4  C4 7E FA        les di, ptr [bp - 6]
71F7  26 8A 45 2A     mov al, byte ptr es:[di + 0x2a]
71FB  30 E4           xor ah, ah
71FD  31 D2           xor dx, dx
71FF  52              push dx
7200  50              push ax
7201  9A DA 09 4B 21  call far 214B:09DA
7206  8B 46 06        mov ax, word ptr [bp + 6]
7209  40              inc ax
720A  50              push ax
720B  B0 0D           mov al, 0xd
720D  50              push ax
720E  BF 6E A9        mov di, 0xa96e
7211  1E              push ds
7212  57              push di
7213  9A A3 01 4B 21  call far 214B:01A3
loc_7218:
7218  89 EC           mov sp, bp
721A  5D              pop bp
721B  C2 06 00        ret 6

; ---- routine 000E:721E  (found by: call)
sub_721E:
721E  55              push bp
721F  89 E5           mov bp, sp
7221  83 EC 02        sub sp, 2
7224  8A 46 0A        mov al, byte ptr [bp + 0xa]
7227  88 46 FF        mov byte ptr [bp - 1], al
722A  80 7E 0A 00     cmp byte ptr [bp + 0xa], 0
722E  74 0F           je 0x723f
7230  C4 7E 06        les di, ptr [bp + 6]
7233  06              push es
7234  57              push di
7235  BF 6E A9        mov di, 0xa96e
7238  1E              push ds
7239  57              push di
723A  9A 29 03 4B 21  call far 214B:0329
loc_723F:
723F  8A 46 FF        mov al, byte ptr [bp - 1]
7242  89 EC           mov sp, bp
7244  5D              pop bp
7245  C2 08 00        ret 8
; data (not reached as code), 2 bytes
7248                  db 01 20   ; . 

; ---- routine 000E:724A  (found by: call)
sub_724A:
724A  55              push bp
724B  89 E5           mov bp, sp
724D  81 EC 22 01     sub sp, 0x122
7251  C4 3E 23 A9     les di, ptr [0xa923]
7255  89 7E E3        mov word ptr [bp - 0x1d], di
7258  8C 46 E5        mov word ptr [bp - 0x1b], es
725B  C4 7E E3        les di, ptr [bp - 0x1d]
725E  26 8A 45 01     mov al, byte ptr es:[di + 1]
7262  30 E4           xor ah, ah
7264  05 80 00        add ax, 0x80
7267  BA 03 00        mov dx, 3
726A  F7 E2           mul dx
726C  C4 3E 1F A9     les di, ptr [0xa91f]
7270  03 F8           add di, ax
7272  26 8A 05        mov al, byte ptr es:[di]
7275  30 E4           xor ah, ah
7277  89 46 FE        mov word ptr [bp - 2], ax
727A  C4 7E E3        les di, ptr [bp - 0x1d]
727D  26 8A 45 01     mov al, byte ptr es:[di + 1]
7281  30 E4           xor ah, ah
7283  C4 7E E3        les di, ptr [bp - 0x1d]
7286  03 F8           add di, ax
7288  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
728D  74 07           je 0x7296
728F  C6 06 B2 AA 0F  mov byte ptr [0xaab2], 0xf
7294  EB 10           jmp 0x72a6
loc_7296:
7296  FF 76 FE        push word ptr [bp - 2]
7299  B8 0B 00        mov ax, 0xb
729C  50              push ax
729D  B8 03 00        mov ax, 3
72A0  50              push ax
72A1  9A 58 0F 71 17  call far 1771:0F58
loc_72A6:
72A6  8D BE E3 FE     lea di, [bp - 0x11d]
72AA  16              push ss
72AB  57              push di
72AC  C4 7E E3        les di, ptr [bp - 0x1d]
72AF  26 8A 45 01     mov al, byte ptr es:[di + 1]
72B3  30 E4           xor ah, ah
72B5  05 80 00        add ax, 0x80
72B8  50              push ax
72B9  9A 47 09 71 17  call far 1771:0947
72BE  B0 08           mov al, 8
72C0  50              push ax
72C1  B0 04           mov al, 4
72C3  50              push ax
72C4  BF 6E A9        mov di, 0xa96e
72C7  1E              push ds
72C8  57              push di
72C9  9A 6D 02 4B 21  call far 214B:026D
72CE  C4 7E E3        les di, ptr [bp - 0x1d]
72D1  26 8A 45 01     mov al, byte ptr es:[di + 1]
72D5  30 E4           xor ah, ah
72D7  05 80 00        add ax, 0x80
72DA  50              push ax
72DB  B8 08 00        mov ax, 8
72DE  50              push ax
72DF  B8 13 00        mov ax, 0x13
72E2  50              push ax
72E3  9A F8 0A 71 17  call far 1771:0AF8
72E8  E8 87 FD        call 0x7072
72EB  50              push ax
72EC  BF D6 19        mov di, 0x19d6
72EF  1E              push ds
72F0  57              push di
72F1  55              push bp
72F2  E8 29 FF        call 0x721e
72F5  08 C0           or al, al
72F7  75 20           jne 0x7319
72F9  C4 7E E3        les di, ptr [bp - 0x1d]
72FC  26 8A 45 01     mov al, byte ptr es:[di + 1]
7300  30 E4           xor ah, ah
7302  C4 7E E3        les di, ptr [bp - 0x1d]
7305  03 F8           add di, ax
7307  26 8A 45 47     mov al, byte ptr es:[di + 0x47]
730B  50              push ax
730C  BF 1E 59        mov di, 0x591e
730F  1E              push ds
7310  57              push di
7311  55              push bp
7312  E8 09 FF        call 0x721e
7315  08 C0           or al, al
7317  74 03           je 0x731c
loc_7319:
7319  E9 19 01        jmp 0x7435
loc_731C:
731C  FF 76 FE        push word ptr [bp - 2]
731F  B8 0D 00        mov ax, 0xd
7322  50              push ax
7323  55              push bp
7324  E8 37 FE        call 0x715e
7327  9A FC 55 71 17  call far 1771:55FC
732C  08 C0           or al, al
732E  75 03           jne 0x7333
7330  E9 02 01        jmp 0x7435
loc_7333:
7333  A1 43 9B        mov ax, word ptr [0x9b43]
7336  B1 03           mov cl, 3
7338  D3 E0           shl ax, cl
733A  C4 3E 2B A9     les di, ptr [0xa92b]
733E  03 F8           add di, ax
7340  81 C7 F8 FF     add di, 0xfff8
7344  89 7E DF        mov word ptr [bp - 0x21], di
7347  8C 46 E1        mov word ptr [bp - 0x1f], es
734A  C4 7E DF        les di, ptr [bp - 0x21]
734D  26 8B 45 06     mov ax, word ptr es:[di + 6]
7351  3B 46 FE        cmp ax, word ptr [bp - 2]
7354  75 04           jne 0x735a
7356  B0 00           mov al, 0
7358  EB 02           jmp 0x735c
loc_735A:
735A  B0 01           mov al, 1
loc_735C:
735C  98              cwde
735D  D1 E0           shl ax, 1
735F  C4 7E DF        les di, ptr [bp - 0x21]
7362  03 F8           add di, ax
7364  26 8B 45 04     mov ax, word ptr es:[di + 4]
7368  89 46 FC        mov word ptr [bp - 4], ax
736B  FF 76 FC        push word ptr [bp - 4]
736E  B8 11 00        mov ax, 0x11
7371  50              push ax
7372  B8 03 00        mov ax, 3
7375  50              push ax
7376  9A 58 0F 71 17  call far 1771:0F58
737B  FF 76 FC        push word ptr [bp - 4]
737E  B8 13 00        mov ax, 0x13
7381  50              push ax
7382  55              push bp
7383  E8 D8 FD        call 0x715e
7386  8D BE DF FE     lea di, [bp - 0x121]
738A  16              push ss
738B  57              push di
738C  A1 43 9B        mov ax, word ptr [0x9b43]
738F  B1 03           mov cl, 3
7391  D3 E0           shl ax, cl
7393  C4 3E 2B A9     les di, ptr [0xa92b]
7397  03 F8           add di, ax
7399  26 8A 45 FA     mov al, byte ptr es:[di - 6]
739D  30 E4           xor ah, ah
739F  50              push ax
73A0  9A 0B 58 71 17  call far 1771:580B
73A5  8D 7E E7        lea di, [bp - 0x19]
73A8  16              push ss
73A9  57              push di
73AA  B8 14 00        mov ax, 0x14
73AD  50              push ax
73AE  9A 44 06 E4 23  call far 23E4:0644
73B3  C4 7E DF        les di, ptr [bp - 0x21]
73B6  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
73BB  74 60           je 0x741d
73BD  C4 7E DF        les di, ptr [bp - 0x21]
73C0  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
73C5  74 09           je 0x73d0
73C7  9A D8 59 71 17  call far 1771:59D8
73CC  08 C0           or al, al
73CE  75 4D           jne 0x741d
loc_73D0:
73D0  8D BE DF FE     lea di, [bp - 0x121]
73D4  16              push ss
73D5  57              push di
73D6  8D 7E E7        lea di, [bp - 0x19]
73D9  16              push ss
73DA  57              push di
73DB  9A 2A 06 E4 23  call far 23E4:062A
73E0  BF 48 72        mov di, 0x7248
73E3  0E              push cs
73E4  57              push di
73E5  9A B7 06 E4 23  call far 23E4:06B7
73EA  C4 7E DF        les di, ptr [bp - 0x21]
73ED  26 8B 45 06     mov ax, word ptr es:[di + 6]
73F1  3B 46 FE        cmp ax, word ptr [bp - 2]
73F4  74 04           je 0x73fa
73F6  B0 00           mov al, 0
73F8  EB 02           jmp 0x73fc
loc_73FA:
73FA  B0 01           mov al, 1
loc_73FC:
73FC  98              cwde
73FD  BA 05 00        mov dx, 5
7400  F7 E2           mul dx
7402  8B F8           mov di, ax
7404  81 C7 BA 6E     add di, 0x6eba
7408  1E              push ds
7409  57              push di
740A  9A B7 06 E4 23  call far 23E4:06B7
740F  8D 7E E7        lea di, [bp - 0x19]
7412  16              push ss
7413  57              push di
7414  B8 14 00        mov ax, 0x14
7417  50              push ax
7418  9A 44 06 E4 23  call far 23E4:0644
loc_741D:
741D  B0 07           mov al, 7
741F  50              push ax
7420  8D 7E E7        lea di, [bp - 0x19]
7423  16              push ss
7424  57              push di
7425  B0 16           mov al, 0x16
7427  50              push ax
7428  B0 03           mov al, 3
742A  50              push ax
742B  BF 6E A9        mov di, 0xa96e
742E  1E              push ds
742F  57              push di
7430  9A C8 02 4B 21  call far 214B:02C8
loc_7435:
7435  89 EC           mov sp, bp
7437  5D              pop bp
7438  C3              ret

; ---- routine 000E:7439  (found by: far)
sub_7439:
7439  55              push bp
743A  89 E5           mov bp, sp
743C  81 EC 08 01     sub sp, 0x108
7440  C4 3E 23 A9     les di, ptr [0xa923]
7444  89 7E FA        mov word ptr [bp - 6], di
7447  8C 46 FC        mov word ptr [bp - 4], es
loc_744A:
744A  9A DB 05 4B 21  call far 214B:05DB
744F  9A F6 5B 71 17  call far 1771:5BF6
7454  BF 9A 64        mov di, 0x649a
7457  1E              push ds
7458  57              push di
7459  BF 6E A9        mov di, 0xa96e
745C  1E              push ds
745D  57              push di
745E  9A 29 03 4B 21  call far 214B:0329
7463  BF BA 5A        mov di, 0x5aba
7466  1E              push ds
7467  57              push di
7468  BF 6E A9        mov di, 0xa96e
746B  1E              push ds
746C  57              push di
746D  9A 29 03 4B 21  call far 214B:0329
7472  BF 88 57        mov di, 0x5788
7475  1E              push ds
7476  57              push di
7477  BF 6E A9        mov di, 0xa96e
747A  1E              push ds
747B  57              push di
747C  9A 29 03 4B 21  call far 214B:0329
7481  C4 7E FA        les di, ptr [bp - 6]
7484  26 8A 45 01     mov al, byte ptr es:[di + 1]
7488  C4 7E FA        les di, ptr [bp - 6]
748B  26 3A 05        cmp al, byte ptr es:[di]
748E  73 0F           jae 0x749f
7490  BF 32 5F        mov di, 0x5f32
7493  1E              push ds
7494  57              push di
7495  BF 6E A9        mov di, 0xa96e
7498  1E              push ds
7499  57              push di
749A  9A 29 03 4B 21  call far 214B:0329
loc_749F:
749F  C4 7E FA        les di, ptr [bp - 6]
74A2  26 8A 45 01     mov al, byte ptr es:[di + 1]
74A6  30 E4           xor ah, ah
74A8  05 80 00        add ax, 0x80
74AB  BA 03 00        mov dx, 3
74AE  F7 E2           mul dx
74B0  C4 3E 1F A9     les di, ptr [0xa91f]
74B4  03 F8           add di, ax
74B6  26 8A 05        mov al, byte ptr es:[di]
74B9  30 E4           xor ah, ah
74BB  50              push ax
74BC  9A 8A 4D 71 17  call far 1771:4D8A
74C1  E8 86 FD        call 0x724a
74C4  C4 7E FA        les di, ptr [bp - 6]
74C7  26 8A 05        mov al, byte ptr es:[di]
74CA  30 E4           xor ah, ah
74CC  89 46 F8        mov word ptr [bp - 8], ax
74CF  B8 01 00        mov ax, 1
74D2  3B 46 F8        cmp ax, word ptr [bp - 8]
74D5  76 03           jbe 0x74da
74D7  E9 95 00        jmp 0x756f
loc_74DA:
74DA  89 46 FE        mov word ptr [bp - 2], ax
74DD  EB 03           jmp 0x74e2
loc_74DF:
74DF  FF 46 FE        inc word ptr [bp - 2]
loc_74E2:
74E2  8B 46 FE        mov ax, word ptr [bp - 2]
74E5  05 80 00        add ax, 0x80
74E8  BA 03 00        mov dx, 3
74EB  F7 E2           mul dx
74ED  C4 3E 1F A9     les di, ptr [0xa91f]
74F1  03 F8           add di, ax
74F3  26 80 3D 00     cmp byte ptr es:[di], 0
74F7  74 6B           je 0x7564
74F9  C4 7E FA        les di, ptr [bp - 6]
74FC  26 8A 45 01     mov al, byte ptr es:[di + 1]
7500  30 E4           xor ah, ah
7502  3B 46 FE        cmp ax, word ptr [bp - 2]
7505  75 07           jne 0x750e
7507  C6 06 B2 AA 0F  mov byte ptr [0xaab2], 0xf
750C  EB 30           jmp 0x753e
loc_750E:
750E  8B 46 FE        mov ax, word ptr [bp - 2]
7511  05 80 00        add ax, 0x80
7514  BA 03 00        mov dx, 3
7517  F7 E2           mul dx
7519  C4 3E 1F A9     les di, ptr [0xa91f]
751D  03 F8           add di, ax
751F  26 8A 05        mov al, byte ptr es:[di]
7522  30 E4           xor ah, ah
7524  BA BF 00        mov dx, 0xbf
7527  F7 E2           mul dx
7529  C4 3E 17 A9     les di, ptr [0xa917]
752D  03 F8           add di, ax
752F  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
7533  30 E4           xor ah, ah
7535  8B F8           mov di, ax
7537  8A 85 05 69     mov al, byte ptr [di + 0x6905]
753B  A2 B2 AA        mov byte ptr [0xaab2], al
loc_753E:
753E  8D BE F8 FE     lea di, [bp - 0x108]
7542  16              push ss
7543  57              push di
7544  8B 46 FE        mov ax, word ptr [bp - 2]
7547  05 80 00        add ax, 0x80
754A  50              push ax
754B  9A 47 09 71 17  call far 1771:0947
7550  8B 46 FE        mov ax, word ptr [bp - 2]
7553  05 0A 00        add ax, 0xa
7556  50              push ax
7557  B0 1A           mov al, 0x1a
7559  50              push ax
755A  BF 6E A9        mov di, 0xa96e
755D  1E              push ds
755E  57              push di
755F  9A 6D 02 4B 21  call far 214B:026D
loc_7564:
7564  8B 46 FE        mov ax, word ptr [bp - 2]
7567  3B 46 F8        cmp ax, word ptr [bp - 8]
756A  74 03           je 0x756f
756C  E9 70 FF        jmp 0x74df
loc_756F:
756F  8B 3E B0 00     mov di, word ptr [0xb0]
7573  8A 85 B1 00     mov al, byte ptr [di + 0xb1]
7577  30 E4           xor ah, ah
7579  50              push ax
757A  B8 2F 00        mov ax, 0x2f
757D  50              push ax
757E  8B 3E B0 00     mov di, word ptr [0xb0]
7582  8A 85 B7 00     mov al, byte ptr [di + 0xb7]
7586  30 E4           xor ah, ah
7588  50              push ax
7589  9A C5 13 4B 21  call far 214B:13C5
758E  83 3E B0 00 06  cmp word ptr [0xb0], 6
7593  75 22           jne 0x75b7
7595  C4 7E FA        les di, ptr [bp - 6]
7598  26 8A 45 01     mov al, byte ptr es:[di + 1]
759C  C4 7E FA        les di, ptr [bp - 6]
759F  26 3A 05        cmp al, byte ptr es:[di]
75A2  75 13           jne 0x75b7
75A4  A0 B7 00        mov al, byte ptr [0xb7]
75A7  30 E4           xor ah, ah
75A9  50              push ax
75AA  B8 2F 00        mov ax, 0x2f
75AD  50              push ax
75AE  B8 0E 00        mov ax, 0xe
75B1  50              push ax
75B2  9A C5 13 4B 21  call far 214B:13C5
loc_75B7:
75B7  C4 3E 6E A9     les di, ptr [0xa96e]
75BB  06              push es
75BC  57              push di
75BD  C4 3E 6A A9     les di, ptr [0xa96a]
75C1  06              push es
75C2  57              push di
75C3  B8 A0 0F        mov ax, 0xfa0
75C6  50              push ax
75C7  9A 5D 02 E4 23  call far 23E4:025D
75CC  9A DD 08 4B 21  call far 214B:08DD
75D1  BF B0 00        mov di, 0xb0
75D4  1E              push ds
75D5  57              push di
75D6  B8 06 00        mov ax, 6
75D9  50              push ax
75DA  9A 07 15 4B 21  call far 214B:1507
75DF  A0 76 A9        mov al, byte ptr [0xa976]
75E2  3C 20           cmp al, 0x20
75E4  74 08           je 0x75ee
75E6  3C AE           cmp al, 0xae
75E8  74 04           je 0x75ee
75EA  3C AF           cmp al, 0xaf
75EC  75 3A           jne 0x7628
loc_75EE:
75EE  C4 7E FA        les di, ptr [bp - 6]
75F1  26 8A 45 01     mov al, byte ptr es:[di + 1]
75F5  30 E4           xor ah, ah
75F7  C4 7E FA        les di, ptr [bp - 6]
75FA  03 F8           add di, ax
75FC  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
7601  75 22           jne 0x7625
7603  C4 7E FA        les di, ptr [bp - 6]
7606  26 8A 45 01     mov al, byte ptr es:[di + 1]
760A  30 E4           xor ah, ah
760C  05 80 00        add ax, 0x80
760F  BA 03 00        mov dx, 3
7612  F7 E2           mul dx
7614  C4 3E 1F A9     les di, ptr [0xa91f]
7618  03 F8           add di, ax
761A  26 8A 05        mov al, byte ptr es:[di]
761D  30 E4           xor ah, ah
761F  50              push ax
7620  9A 4F E4 91 07  call far 0791:E44F
loc_7625:
7625  E9 F3 01        jmp 0x781b
loc_7628:
7628  3C 74           cmp al, 0x74
762A  74 04           je 0x7630
762C  3C 54           cmp al, 0x54
762E  75 3A           jne 0x766a
loc_7630:
7630  C4 7E FA        les di, ptr [bp - 6]
7633  26 8A 45 01     mov al, byte ptr es:[di + 1]
7637  30 E4           xor ah, ah
7639  C4 7E FA        les di, ptr [bp - 6]
763C  03 F8           add di, ax
763E  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
7643  75 22           jne 0x7667
7645  C4 7E FA        les di, ptr [bp - 6]
7648  26 8A 45 01     mov al, byte ptr es:[di + 1]
764C  30 E4           xor ah, ah
764E  05 80 00        add ax, 0x80
7651  BA 03 00        mov dx, 3
7654  F7 E2           mul dx
7656  C4 3E 1F A9     les di, ptr [0xa91f]
765A  03 F8           add di, ax
765C  26 8A 05        mov al, byte ptr es:[di]
765F  30 E4           xor ah, ah
7661  50              push ax
7662  9A 81 19 71 17  call far 1771:1981
loc_7667:
7667  E9 B1 01        jmp 0x781b
loc_766A:
766A  3C 0D           cmp al, 0xd
766C  74 03           je 0x7671
766E  E9 5C 01        jmp 0x77cd
loc_7671:
7671  A1 B0 00        mov ax, word ptr [0xb0]
7674  3D 01 00        cmp ax, 1
7677  75 0C           jne 0x7685
7679  B8 01 00        mov ax, 1
767C  50              push ax
767D  9A B9 26 71 17  call far 1771:26B9
7682  E9 46 01        jmp 0x77cb
loc_7685:
7685  3D 02 00        cmp ax, 2
7688  75 06           jne 0x7690
768A  E8 73 89        call 0
768D  E9 3B 01        jmp 0x77cb
loc_7690:
7690  3D 03 00        cmp ax, 3
7693  75 3D           jne 0x76d2
7695  B0 01           mov al, 1
7697  50              push ax
7698  C4 7E FA        les di, ptr [bp - 6]
769B  26 8A 45 01     mov al, byte ptr es:[di + 1]
769F  30 E4           xor ah, ah
76A1  C4 7E FA        les di, ptr [bp - 6]
76A4  03 F8           add di, ax
76A6  26 8A 45 01     mov al, byte ptr es:[di + 1]
76AA  30 E4           xor ah, ah
76AC  50              push ax
76AD  C4 7E FA        les di, ptr [bp - 6]
76B0  26 8A 45 01     mov al, byte ptr es:[di + 1]
76B4  30 E4           xor ah, ah
76B6  05 80 00        add ax, 0x80
76B9  BA 03 00        mov dx, 3
76BC  F7 E2           mul dx
76BE  C4 3E 1F A9     les di, ptr [0xa91f]
76C2  03 F8           add di, ax
76C4  26 8A 05        mov al, byte ptr es:[di]
76C7  30 E4           xor ah, ah
76C9  50              push ax
76CA  9A 8D 95 71 17  call far 1771:958D
76CF  E9 F9 00        jmp 0x77cb
loc_76D2:
76D2  3D 04 00        cmp ax, 4
76D5  75 0C           jne 0x76e3
76D7  B8 03 00        mov ax, 3
76DA  50              push ax
76DB  9A B9 26 71 17  call far 1771:26B9
76E0  E9 E8 00        jmp 0x77cb
loc_76E3:
76E3  3D 05 00        cmp ax, 5
76E6  75 3A           jne 0x7722
76E8  C4 7E FA        les di, ptr [bp - 6]
76EB  26 8A 45 01     mov al, byte ptr es:[di + 1]
76EF  30 E4           xor ah, ah
76F1  C4 7E FA        les di, ptr [bp - 6]
76F4  03 F8           add di, ax
76F6  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
76FB  75 22           jne 0x771f
76FD  C4 7E FA        les di, ptr [bp - 6]
7700  26 8A 45 01     mov al, byte ptr es:[di + 1]
7704  30 E4           xor ah, ah
7706  05 80 00        add ax, 0x80
7709  BA 03 00        mov dx, 3
770C  F7 E2           mul dx
770E  C4 3E 1F A9     les di, ptr [0xa91f]
7712  03 F8           add di, ax
7714  26 8A 05        mov al, byte ptr es:[di]
7717  30 E4           xor ah, ah
7719  50              push ax
771A  9A 4F E4 91 07  call far 0791:E44F
loc_771F:
771F  E9 A9 00        jmp 0x77cb
loc_7722:
7722  3D 06 00        cmp ax, 6
7725  74 03           je 0x772a
7727  E9 A1 00        jmp 0x77cb
loc_772A:
772A  E8 45 F9        call 0x7072
772D  08 C0           or al, al
772F  74 22           je 0x7753
7731  C4 7E FA        les di, ptr [bp - 6]
7734  26 8A 45 01     mov al, byte ptr es:[di + 1]
7738  C4 7E FA        les di, ptr [bp - 6]
773B  26 3A 05        cmp al, byte ptr es:[di]
773E  73 09           jae 0x7749
7740  C4 7E FA        les di, ptr [bp - 6]
7743  26 FE 45 01     inc byte ptr es:[di + 1]
7747  EB 08           jmp 0x7751
loc_7749:
7749  C4 7E FA        les di, ptr [bp - 6]
774C  26 C6 45 01 01  mov byte ptr es:[di + 1], 1
loc_7751:
7751  EB 78           jmp 0x77cb
loc_7753:
7753  C4 7E FA        les di, ptr [bp - 6]
7756  26 8A 45 01     mov al, byte ptr es:[di + 1]
775A  30 E4           xor ah, ah
775C  C4 7E FA        les di, ptr [bp - 6]
775F  03 F8           add di, ax
7761  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
7766  75 48           jne 0x77b0
7768  C4 7E FA        les di, ptr [bp - 6]
776B  26 8A 45 01     mov al, byte ptr es:[di + 1]
776F  30 E4           xor ah, ah
7771  05 80 00        add ax, 0x80
7774  BA 03 00        mov dx, 3
7777  F7 E2           mul dx
7779  C4 3E 1F A9     les di, ptr [0xa91f]
777D  03 F8           add di, ax
777F  26 8A 05        mov al, byte ptr es:[di]
7782  30 E4           xor ah, ah
7784  50              push ax
7785  E8 5D E0        call 0x57e5
7788  08 C0           or al, al
778A  75 3F           jne 0x77cb
778C  C4 7E FA        les di, ptr [bp - 6]
778F  26 8A 45 01     mov al, byte ptr es:[di + 1]
7793  30 E4           xor ah, ah
7795  05 80 00        add ax, 0x80
7798  BA 03 00        mov dx, 3
779B  F7 E2           mul dx
779D  C4 3E 1F A9     les di, ptr [0xa91f]
77A1  03 F8           add di, ax
77A3  26 8A 05        mov al, byte ptr es:[di]
77A6  30 E4           xor ah, ah
77A8  50              push ax
77A9  E8 48 E5        call 0x5cf4
77AC  08 C0           or al, al
77AE  75 1B           jne 0x77cb
loc_77B0:
77B0  C4 7E FA        les di, ptr [bp - 6]
77B3  26 8A 45 01     mov al, byte ptr es:[di + 1]
77B7  C4 7E FA        les di, ptr [bp - 6]
77BA  26 3A 05        cmp al, byte ptr es:[di]
77BD  75 05           jne 0x77c4
77BF  E8 F7 F8        call 0x70b9
77C2  EB 07           jmp 0x77cb
loc_77C4:
77C4  C4 7E FA        les di, ptr [bp - 6]
77C7  26 FE 45 01     inc byte ptr es:[di + 1]
loc_77CB:
77CB  EB 4E           jmp 0x781b
loc_77CD:
77CD  3C 9F           cmp al, 0x9f
77CF  75 07           jne 0x77d8
77D1  9A 45 09 D6 16  call far 16D6:0945
77D6  EB 43           jmp 0x781b
loc_77D8:
77D8  3C A0           cmp al, 0xa0
77DA  75 1C           jne 0x77f8
77DC  C4 7E FA        les di, ptr [bp - 6]
77DF  26 8A 45 01     mov al, byte ptr es:[di + 1]
77E3  30 E4           xor ah, ah
77E5  05 80 00        add ax, 0x80
77E8  50              push ax
77E9  B8 08 00        mov ax, 8
77EC  50              push ax
77ED  B8 04 00        mov ax, 4
77F0  50              push ax
77F1  9A A0 09 71 17  call far 1771:09A0
77F6  EB 23           jmp 0x781b
loc_77F8:
77F8  3C A1           cmp al, 0xa1
77FA  74 04           je 0x7800
77FC  3C A2           cmp al, 0xa2
77FE  75 07           jne 0x7807
loc_7800:
7800  9A 2C 11 91 07  call far 0791:112C
7805  EB 14           jmp 0x781b
loc_7807:
7807  3C A5           cmp al, 0xa5
7809  75 07           jne 0x7812
780B  9A B5 08 71 17  call far 1771:08B5
7810  EB 09           jmp 0x781b
loc_7812:
7812  3C A8           cmp al, 0xa8
7814  75 05           jne 0x781b
7816  9A 0F 09 71 17  call far 1771:090F
loc_781B:
781B  E9 2C FC        jmp 0x744a
; data (not reached as code), 18 bytes
781E                  db 89 EC 5D CB 00 00 00 00 00 00 00 00 00 00 00 00   ; ..].............
782E                  db 00 00   ; ..
