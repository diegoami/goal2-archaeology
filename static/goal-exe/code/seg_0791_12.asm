; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 12 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:6D4E  (found by: call)
sub_6D4E:
6D4E  55              push bp
6D4F  89 E5           mov bp, sp
6D51  83 EC 02        sub sp, 2
6D54  8A 46 08        mov al, byte ptr [bp + 8]
6D57  98              cwde
6D58  8B F8           mov di, ax
6D5A  D1 E7           shl di, 1
6D5C  FF B5 34 9B     push word ptr [di - 0x64cc]
6D60  9A 77 0B 71 17  call far 1771:0B77
6D65  08 C0           or al, al
6D67  74 27           je 0x6d90
6D69  8A 46 08        mov al, byte ptr [bp + 8]
6D6C  50              push ax
6D6D  8A 46 06        mov al, byte ptr [bp + 6]
6D70  50              push ax
6D71  E8 07 5F        call 0xcc7b
6D74  8B D8           mov bx, ax
6D76  8B 46 06        mov ax, word ptr [bp + 6]
6D79  D1 E0           shl ax, 1
6D7B  8B C8           mov cx, ax
6D7D  8A 46 08        mov al, byte ptr [bp + 8]
6D80  98              cwde
6D81  BA 0A 00        mov dx, 0xa
6D84  F7 E2           mul dx
6D86  8B F8           mov di, ax
6D88  03 F9           add di, cx
6D8A  89 9D 76 99     mov word ptr [di - 0x668a], bx
6D8E  EB 14           jmp 0x6da4
loc_6D90:
6D90  8A 46 08        mov al, byte ptr [bp + 8]
6D93  50              push ax
6D94  8B 7E 06        mov di, word ptr [bp + 6]
6D97  8A 85 64 07     mov al, byte ptr [di + 0x764]
6D9B  30 E4           xor ah, ah
6D9D  50              push ax
6D9E  FF 76 06        push word ptr [bp + 6]
6DA1  E8 39 B2        call 0x1fdd
loc_6DA4:
6DA4  8A 46 08        mov al, byte ptr [bp + 8]
6DA7  50              push ax
6DA8  FF 76 06        push word ptr [bp + 6]
6DAB  E8 B7 FD        call 0x6b65
6DAE  89 46 FE        mov word ptr [bp - 2], ax
6DB1  83 7E FE 0C     cmp word ptr [bp - 2], 0xc
6DB5  73 14           jae 0x6dcb
6DB7  8A 46 08        mov al, byte ptr [bp + 8]
6DBA  98              cwde
6DBB  8B F8           mov di, ax
6DBD  8A 85 68 06     mov al, byte ptr [di + 0x668]
6DC1  30 E4           xor ah, ah
6DC3  03 46 FE        add ax, word ptr [bp - 2]
6DC6  89 46 FE        mov word ptr [bp - 2], ax
6DC9  EB 0F           jmp 0x6dda
loc_6DCB:
6DCB  8A 46 08        mov al, byte ptr [bp + 8]
6DCE  98              cwde
6DCF  8B F8           mov di, ax
6DD1  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
6DD5  30 E4           xor ah, ah
6DD7  89 46 FE        mov word ptr [bp - 2], ax
loc_6DDA:
6DDA  FF 76 FE        push word ptr [bp - 2]
6DDD  8A 46 04        mov al, byte ptr [bp + 4]
6DE0  50              push ax
6DE1  E8 0D FE        call 0x6bf1
6DE4  89 EC           mov sp, bp
6DE6  5D              pop bp
6DE7  C2 06 00        ret 6

; ---- routine 0791:6DEA  (found by: call)
sub_6DEA:
6DEA  55              push bp
6DEB  89 E5           mov bp, sp
6DED  8A 46 04        mov al, byte ptr [bp + 4]
6DF0  50              push ax
6DF1  E8 AF BC        call 0x2aa3
6DF4  8A 46 06        mov al, byte ptr [bp + 6]
6DF7  98              cwde
6DF8  50              push ax
6DF9  E8 9A BB        call 0x2996
6DFC  98              cwde
6DFD  BA 0A 00        mov dx, 0xa
6E00  F7 E2           mul dx
6E02  8B F8           mov di, ax
6E04  58              pop ax
6E05  03 F8           add di, ax
6E07  FE 85 7E 7B     inc byte ptr [di + 0x7b7e]
6E0B  89 EC           mov sp, bp
6E0D  5D              pop bp
6E0E  C2 04 00        ret 4

; ---- routine 0791:6E11  (found by: call)
sub_6E11:
6E11  55              push bp
6E12  89 E5           mov bp, sp
6E14  80 3E 26 83 00  cmp byte ptr [0x8326], 0
6E19  75 4F           jne 0x6e6a
6E1B  C6 06 0E 83 00  mov byte ptr [0x830e], 0
6E20  E8 3F 12        call 0x8062
6E23  E8 70 BB        call 0x2996
6E26  08 C0           or al, al
6E28  74 04           je 0x6e2e
6E2A  B0 00           mov al, 0
6E2C  EB 02           jmp 0x6e30
loc_6E2E:
6E2E  B0 01           mov al, 1
loc_6E30:
6E30  98              cwde
6E31  8B F8           mov di, ax
6E33  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
6E37  30 E4           xor ah, ah
6E39  50              push ax
6E3A  B0 07           mov al, 7
6E3C  50              push ax
6E3D  E8 B1 FD        call 0x6bf1
6E40  B0 2B           mov al, 0x2b
6E42  50              push ax
6E43  E8 5D BC        call 0x2aa3
6E46  A0 0B 83        mov al, byte ptr [0x830b]
6E49  30 E4           xor ah, ah
6E4B  BA 16 00        mov dx, 0x16
6E4E  F7 E2           mul dx
6E50  8B F8           mov di, ax
6E52  81 C7 E8 80     add di, 0x80e8
6E56  1E              push ds
6E57  57              push di
6E58  0E              push cs
6E59  E8 89 BD        call 0x2be5
6E5C  08 C0           or al, al
6E5E  7F 04           jg 0x6e64
6E60  B0 00           mov al, 0
6E62  EB 02           jmp 0x6e66
loc_6E64:
6E64  B0 01           mov al, 1
loc_6E66:
6E66  50              push ax
6E67  E8 36 B8        call 0x26a0
loc_6E6A:
6E6A  89 EC           mov sp, bp
6E6C  5D              pop bp
6E6D  C3              ret

; ---- routine 0791:6E6E  (found by: call)
sub_6E6E:
6E6E  55              push bp
6E6F  89 E5           mov bp, sp
6E71  80 3E 26 83 00  cmp byte ptr [0x8326], 0
6E76  75 53           jne 0x6ecb
6E78  C6 06 0E 83 00  mov byte ptr [0x830e], 0
6E7D  E8 E2 11        call 0x8062
6E80  E8 13 BB        call 0x2996
6E83  08 C0           or al, al
6E85  74 04           je 0x6e8b
6E87  B0 00           mov al, 0
6E89  EB 02           jmp 0x6e8d
loc_6E8B:
6E8B  B0 01           mov al, 1
loc_6E8D:
6E8D  50              push ax
6E8E  B8 02 00        mov ax, 2
6E91  50              push ax
6E92  B0 09           mov al, 9
6E94  50              push ax
6E95  E8 B6 FE        call 0x6d4e
6E98  A0 0B 83        mov al, byte ptr [0x830b]
6E9B  A2 0A 83        mov byte ptr [0x830a], al
6E9E  B0 00           mov al, 0
6EA0  50              push ax
6EA1  B0 2D           mov al, 0x2d
6EA3  50              push ax
6EA4  E8 43 FF        call 0x6dea
6EA7  A0 0B 83        mov al, byte ptr [0x830b]
6EAA  30 E4           xor ah, ah
6EAC  BA 16 00        mov dx, 0x16
6EAF  F7 E2           mul dx
6EB1  8B F8           mov di, ax
6EB3  81 C7 E8 80     add di, 0x80e8
6EB7  1E              push ds
6EB8  57              push di
6EB9  0E              push cs
6EBA  E8 28 BD        call 0x2be5
6EBD  08 C0           or al, al
6EBF  7F 04           jg 0x6ec5
6EC1  B0 00           mov al, 0
6EC3  EB 02           jmp 0x6ec7
loc_6EC5:
6EC5  B0 01           mov al, 1
loc_6EC7:
6EC7  50              push ax
6EC8  E8 D5 B7        call 0x26a0
loc_6ECB:
6ECB  89 EC           mov sp, bp
6ECD  5D              pop bp
6ECE  C3              ret

; ---- routine 0791:6ECF  (found by: call)
sub_6ECF:
6ECF  55              push bp
6ED0  89 E5           mov bp, sp
6ED2  C6 06 0E 83 00  mov byte ptr [0x830e], 0
6ED7  B8 02 00        mov ax, 2
6EDA  50              push ax
6EDB  E8 63 95        call 0x441
6EDE  E8 81 11        call 0x8062
6EE1  E8 B2 BA        call 0x2996
6EE4  50              push ax
6EE5  B8 03 00        mov ax, 3
6EE8  50              push ax
6EE9  B0 0A           mov al, 0xa
6EEB  50              push ax
6EEC  E8 5F FE        call 0x6d4e
6EEF  B0 02           mov al, 2
6EF1  50              push ax
6EF2  B0 39           mov al, 0x39
6EF4  50              push ax
6EF5  E8 F2 FE        call 0x6dea
6EF8  C6 06 24 83 01  mov byte ptr [0x8324], 1
6EFD  89 EC           mov sp, bp
6EFF  5D              pop bp
6F00  C3              ret

; ---- routine 0791:6F01  (found by: call)
sub_6F01:
6F01  55              push bp
6F02  89 E5           mov bp, sp
6F04  80 3E 26 83 00  cmp byte ptr [0x8326], 0
6F09  75 2D           jne 0x6f38
6F0B  C6 06 0E 83 00  mov byte ptr [0x830e], 0
6F10  E8 4F 11        call 0x8062
6F13  8A 46 06        mov al, byte ptr [bp + 6]
6F16  50              push ax
6F17  B8 05 00        mov ax, 5
6F1A  50              push ax
6F1B  B0 08           mov al, 8
6F1D  50              push ax
6F1E  E8 2D FE        call 0x6d4e
6F21  80 7E 04 00     cmp byte ptr [bp + 4], 0
6F25  74 0B           je 0x6f32
6F27  B0 01           mov al, 1
6F29  50              push ax
6F2A  B0 3A           mov al, 0x3a
6F2C  50              push ax
6F2D  E8 BA FE        call 0x6dea
6F30  EB 06           jmp 0x6f38
loc_6F32:
6F32  B0 38           mov al, 0x38
6F34  50              push ax
6F35  E8 6B BB        call 0x2aa3
loc_6F38:
6F38  89 EC           mov sp, bp
6F3A  5D              pop bp
6F3B  C2 04 00        ret 4

; ---- routine 0791:6F3E  (found by: call)
sub_6F3E:
6F3E  55              push bp
6F3F  89 E5           mov bp, sp
6F41  C6 06 0E 83 00  mov byte ptr [0x830e], 0
6F46  E8 19 11        call 0x8062
6F49  8A 46 04        mov al, byte ptr [bp + 4]
6F4C  98              cwde
6F4D  8B F8           mov di, ax
6F4F  8A 85 68 06     mov al, byte ptr [di + 0x668]
6F53  30 E4           xor ah, ah
6F55  40              inc ax
6F56  BA 16 00        mov dx, 0x16
6F59  F7 E2           mul dx
6F5B  8B F8           mov di, ax
6F5D  81 C7 E8 80     add di, 0x80e8
6F61  1E              push ds
6F62  57              push di
6F63  0E              push cs
6F64  E8 7E BC        call 0x2be5
6F67  98              cwde
6F68  8B D0           mov dx, ax
6F6A  A0 F7 82        mov al, byte ptr [0x82f7]
6F6D  98              cwde
6F6E  F7 EA           imul dx
6F70  3D 12 00        cmp ax, 0x12
6F73  7C 1F           jl 0x6f94
6F75  A0 F6 82        mov al, byte ptr [0x82f6]
6F78  98              cwde
6F79  09 C0           or ax, ax
6F7B  79 02           jns 0x6f7f
6F7D  F7 D8           neg ax
loc_6F7F:
6F7F  3D 04 00        cmp ax, 4
6F82  7F 10           jg 0x6f94
6F84  8A 46 04        mov al, byte ptr [bp + 4]
6F87  50              push ax
6F88  B8 04 00        mov ax, 4
6F8B  50              push ax
6F8C  B0 0B           mov al, 0xb
6F8E  50              push ax
6F8F  E8 BC FD        call 0x6d4e
6F92  EB 13           jmp 0x6fa7
loc_6F94:
6F94  8A 46 04        mov al, byte ptr [bp + 4]
6F97  98              cwde
6F98  8B F8           mov di, ax
6F9A  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
6F9E  30 E4           xor ah, ah
6FA0  50              push ax
6FA1  B0 0B           mov al, 0xb
6FA3  50              push ax
6FA4  E8 4A FC        call 0x6bf1
loc_6FA7:
6FA7  B0 01           mov al, 1
6FA9  50              push ax
6FAA  B0 3A           mov al, 0x3a
6FAC  50              push ax
6FAD  E8 3A FE        call 0x6dea
6FB0  89 EC           mov sp, bp
6FB2  5D              pop bp
6FB3  C2 02 00        ret 2

; ---- routine 0791:6FB6  (found by: call)
sub_6FB6:
6FB6  55              push bp
6FB7  89 E5           mov bp, sp
6FB9  FF 36 F6 82     push word ptr [0x82f6]
6FBD  A0 0B 83        mov al, byte ptr [0x830b]
6FC0  30 E4           xor ah, ah
6FC2  BA 16 00        mov dx, 0x16
6FC5  F7 E2           mul dx
6FC7  8B F8           mov di, ax
6FC9  81 C7 E8 80     add di, 0x80e8
6FCD  1E              push ds
6FCE  57              push di
6FCF  0E              push cs
6FD0  E8 63 BE        call 0x2e36
6FD3  08 C0           or al, al
6FD5  74 0C           je 0x6fe3
6FD7  E8 BC B9        call 0x2996
6FDA  50              push ax
6FDB  B0 01           mov al, 1
6FDD  50              push ax
6FDE  E8 20 FF        call 0x6f01
6FE1  EB 07           jmp 0x6fea
loc_6FE3:
6FE3  E8 B0 B9        call 0x2996
6FE6  50              push ax
6FE7  E8 54 FF        call 0x6f3e
loc_6FEA:
6FEA  89 EC           mov sp, bp
6FEC  5D              pop bp
6FED  C3              ret

; ---- routine 0791:6FEE  (found by: call)
sub_6FEE:
6FEE  55              push bp
6FEF  89 E5           mov bp, sp
6FF1  8B 7E 04        mov di, word ptr [bp + 4]
6FF4  36 C4 7D 06     les di, ptr ss:[di + 6]
6FF8  06              push es
6FF9  57              push di
6FFA  0E              push cs
6FFB  E8 C7 BC        call 0x2cc5
6FFE  08 C0           or al, al
7000  74 61           je 0x7063
7002  80 3E 23 83 00  cmp byte ptr [0x8323], 0
7007  74 2C           je 0x7035
7009  8B 7E 04        mov di, word ptr [bp + 4]
700C  36 C4 7D 06     les di, ptr ss:[di + 6]
7010  06              push es
7011  57              push di
7012  0E              push cs
7013  E8 5E B9        call 0x2974
7016  98              cwde
7017  8B F8           mov di, ax
7019  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
701D  30 E4           xor ah, ah
701F  50              push ax
7020  8B 7E 04        mov di, word ptr [bp + 4]
7023  36 C4 7D 06     les di, ptr ss:[di + 6]
7027  06              push es
7028  57              push di
7029  0E              push cs
702A  E8 71 CB        call 0x3b9e
702D  B0 05           mov al, 5
702F  50              push ax
7030  E8 F6 B8        call 0x2929
7033  EB 2E           jmp 0x7063
loc_7035:
7035  8B 7E 04        mov di, word ptr [bp + 4]
7038  36 C4 7D 06     les di, ptr ss:[di + 6]
703C  26 80 7D 10 00  cmp byte ptr es:[di + 0x10], 0
7041  76 0D           jbe 0x7050
7043  8B 7E 04        mov di, word ptr [bp + 4]
7046  36 C4 7D 06     les di, ptr ss:[di + 6]
704A  26 FE 4D 10     dec byte ptr es:[di + 0x10]
704E  EB 13           jmp 0x7063
loc_7050:
7050  C6 06 02 83 00  mov byte ptr [0x8302], 0
7055  B0 2A           mov al, 0x2a
7057  50              push ax
7058  E8 48 BA        call 0x2aa3
705B  C6 06 23 83 01  mov byte ptr [0x8323], 1
7060  E8 5F B6        call 0x26c2
loc_7063:
7063  89 EC           mov sp, bp
7065  5D              pop bp
7066  C2 02 00        ret 2

; ---- routine 0791:7069  (found by: call)
sub_7069:
7069  55              push bp
706A  89 E5           mov bp, sp
706C  C4 7E 06        les di, ptr [bp + 6]
706F  26 8A 45 06     mov al, byte ptr es:[di + 6]
7073  3A 06 0B 83     cmp al, byte ptr [0x830b]
7077  75 06           jne 0x707f
7079  55              push bp
707A  E8 71 FF        call 0x6fee
707D  EB 71           jmp 0x70f0
loc_707F:
707F  C4 7E 06        les di, ptr [bp + 6]
7082  06              push es
7083  57              push di
7084  0E              push cs
7085  E8 EC B8        call 0x2974
7088  98              cwde
7089  8B F8           mov di, ax
708B  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
708F  C4 7E 06        les di, ptr [bp + 6]
7092  26 3A 45 06     cmp al, byte ptr es:[di + 6]
7096  75 4F           jne 0x70e7
7098  9A FA 06 4B 21  call far 214B:06FA
709D  30 E4           xor ah, ah
709F  50              push ax
70A0  9A FA 06 4B 21  call far 214B:06FA
70A5  30 E4           xor ah, ah
70A7  8B D8           mov bx, ax
70A9  A0 F6 82        mov al, byte ptr [0x82f6]
70AC  98              cwde
70AD  99              cdq
70AE  B9 02 00        mov cx, 2
70B1  F7 F9           idiv cx
70B3  03 C3           add ax, bx
70B5  5A              pop dx
70B6  2B C2           sub ax, dx
70B8  C4 7E 06        les di, ptr [bp + 6]
70BB  26 88 45 07     mov byte ptr es:[di + 7], al
70BF  C4 7E 06        les di, ptr [bp + 6]
70C2  06              push es
70C3  57              push di
70C4  0E              push cs
70C5  E8 1D BB        call 0x2be5
70C8  98              cwde
70C9  50              push ax
70CA  B8 04 00        mov ax, 4
70CD  50              push ax
70CE  9A B1 06 4B 21  call far 214B:06B1
70D3  5A              pop dx
70D4  F7 EA           imul dx
70D6  8B D0           mov dx, ax
70D8  A0 F7 82        mov al, byte ptr [0x82f7]
70DB  98              cwde
70DC  03 C2           add ax, dx
70DE  C4 7E 06        les di, ptr [bp + 6]
70E1  26 88 45 08     mov byte ptr es:[di + 8], al
70E5  EB 09           jmp 0x70f0
loc_70E7:
70E7  C4 7E 06        les di, ptr [bp + 6]
70EA  06              push es
70EB  57              push di
70EC  0E              push cs
70ED  E8 74 DA        call 0x4b64
loc_70F0:
70F0  89 EC           mov sp, bp
70F2  5D              pop bp
70F3  CA 04 00        retf 4

; ---- routine 0791:70F6  (found by: call)
sub_70F6:
70F6  55              push bp
70F7  89 E5           mov bp, sp
70F9  8B 7E 04        mov di, word ptr [bp + 4]
70FC  36 C4 7D 06     les di, ptr ss:[di + 6]
7100  06              push es
7101  57              push di
7102  0E              push cs
7103  E8 BF BB        call 0x2cc5
7106  08 C0           or al, al
7108  74 4A           je 0x7154
710A  80 3E 23 83 00  cmp byte ptr [0x8323], 0
710F  74 15           je 0x7126
7111  8B 7E 04        mov di, word ptr [bp + 4]
7114  36 C4 7D 06     les di, ptr ss:[di + 6]
7118  06              push es
7119  57              push di
711A  0E              push cs
711B  E8 D8 CC        call 0x3df6
711E  B0 05           mov al, 5
7120  50              push ax
7121  E8 05 B8        call 0x2929
7124  EB 2E           jmp 0x7154
loc_7126:
7126  8B 7E 04        mov di, word ptr [bp + 4]
7129  36 C4 7D 06     les di, ptr ss:[di + 6]
712D  26 80 7D 10 00  cmp byte ptr es:[di + 0x10], 0
7132  76 0D           jbe 0x7141
7134  8B 7E 04        mov di, word ptr [bp + 4]
7137  36 C4 7D 06     les di, ptr ss:[di + 6]
713B  26 FE 4D 10     dec byte ptr es:[di + 0x10]
713F  EB 13           jmp 0x7154
loc_7141:
7141  C6 06 02 83 00  mov byte ptr [0x8302], 0
7146  B0 2C           mov al, 0x2c
7148  50              push ax
7149  E8 57 B9        call 0x2aa3
714C  C6 06 23 83 01  mov byte ptr [0x8323], 1
7151  E8 6E B5        call 0x26c2
loc_7154:
7154  89 EC           mov sp, bp
7156  5D              pop bp
7157  C2 02 00        ret 2

; ---- routine 0791:715A  (found by: call)
sub_715A:
715A  55              push bp
715B  89 E5           mov bp, sp
715D  C4 7E 06        les di, ptr [bp + 6]
7160  26 8A 45 06     mov al, byte ptr es:[di + 6]
7164  3A 06 0B 83     cmp al, byte ptr [0x830b]
7168  75 06           jne 0x7170
716A  55              push bp
716B  E8 88 FF        call 0x70f6
716E  EB 09           jmp 0x7179
loc_7170:
7170  C4 7E 06        les di, ptr [bp + 6]
7173  06              push es
7174  57              push di
7175  0E              push cs
7176  E8 EB D9        call 0x4b64
loc_7179:
7179  89 EC           mov sp, bp
717B  5D              pop bp
717C  CA 04 00        retf 4

; ---- routine 0791:717F  (found by: call)
sub_717F:
717F  55              push bp
7180  89 E5           mov bp, sp
7182  83 EC 04        sub sp, 4
7185  C6 46 FC 01     mov byte ptr [bp - 4], 1
7189  C7 46 FD 01 00  mov word ptr [bp - 3], 1
718E  EB 03           jmp 0x7193
loc_7190:
7190  FF 46 FD        inc word ptr [bp - 3]
loc_7193:
7193  FF 76 FD        push word ptr [bp - 3]
7196  E8 C4 92        call 0x45d
7199  08 C0           or al, al
719B  75 36           jne 0x71d3
719D  A0 0B 83        mov al, byte ptr [0x830b]
71A0  30 E4           xor ah, ah
71A2  3B 46 FD        cmp ax, word ptr [bp - 3]
71A5  74 2C           je 0x71d3
71A7  8B 46 FD        mov ax, word ptr [bp - 3]
71AA  BA 16 00        mov dx, 0x16
71AD  F7 E2           mul dx
71AF  8B F8           mov di, ax
71B1  FF B5 E8 80     push word ptr [di - 0x7f18]
71B5  A0 0B 83        mov al, byte ptr [0x830b]
71B8  30 E4           xor ah, ah
71BA  BA 16 00        mov dx, 0x16
71BD  F7 E2           mul dx
71BF  8B F8           mov di, ax
71C1  81 C7 E8 80     add di, 0x80e8
71C5  1E              push ds
71C6  57              push di
71C7  0E              push cs
71C8  E8 ED BC        call 0x2eb8
71CB  08 C0           or al, al
71CD  74 04           je 0x71d3
71CF  C6 46 FC 00     mov byte ptr [bp - 4], 0
loc_71D3:
71D3  83 7E FD 16     cmp word ptr [bp - 3], 0x16
71D7  75 B7           jne 0x7190
71D9  8A 46 FC        mov al, byte ptr [bp - 4]
71DC  88 46 FF        mov byte ptr [bp - 1], al
71DF  8A 46 FF        mov al, byte ptr [bp - 1]
71E2  89 EC           mov sp, bp
71E4  5D              pop bp
71E5  C2 02 00        ret 2

; ---- routine 0791:71E8  (found by: call)
sub_71E8:
71E8  55              push bp
71E9  89 E5           mov bp, sp
71EB  8B 7E 04        mov di, word ptr [bp + 4]
71EE  36 C4 7D 06     les di, ptr ss:[di + 6]
71F2  06              push es
71F3  57              push di
71F4  0E              push cs
71F5  E8 CD BA        call 0x2cc5
71F8  08 C0           or al, al
71FA  75 03           jne 0x71ff
71FC  E9 82 00        jmp 0x7281
loc_71FF:
71FF  8B 7E 04        mov di, word ptr [bp + 4]
7202  36 C4 7D 06     les di, ptr ss:[di + 6]
7206  26 8B 05        mov ax, word ptr es:[di]
7209  3B 06 15 83     cmp ax, word ptr [0x8315]
720D  75 51           jne 0x7260
720F  80 3E 23 83 00  cmp byte ptr [0x8323], 0
7214  74 15           je 0x722b
7216  8B 7E 04        mov di, word ptr [bp + 4]
7219  36 C4 7D 06     les di, ptr ss:[di + 6]
721D  06              push es
721E  57              push di
721F  0E              push cs
7220  E8 F2 C8        call 0x3b15
7223  B0 05           mov al, 5
7225  50              push ax
7226  E8 00 B7        call 0x2929
7229  EB 33           jmp 0x725e
loc_722B:
722B  FF 76 04        push word ptr [bp + 4]
722E  E8 4E FF        call 0x717f
7231  08 C0           or al, al
7233  74 29           je 0x725e
7235  8B 7E 04        mov di, word ptr [bp + 4]
7238  36 C4 7D 06     les di, ptr ss:[di + 6]
723C  06              push es
723D  57              push di
723E  0E              push cs
723F  E8 A3 B9        call 0x2be5
7242  98              cwde
7243  B9 DB FF        mov cx, 0xffdb
7246  F7 E9           imul cx
7248  8B 7E 04        mov di, word ptr [bp + 4]
724B  36 C4 7D 06     les di, ptr ss:[di + 6]
724F  26 88 45 08     mov byte ptr es:[di + 8], al
7253  B0 2E           mov al, 0x2e
7255  50              push ax
7256  E8 4A B8        call 0x2aa3
7259  C6 06 23 83 01  mov byte ptr [0x8323], 1
loc_725E:
725E  EB 21           jmp 0x7281
loc_7260:
7260  8B 7E 04        mov di, word ptr [bp + 4]
7263  36 C4 7D 06     les di, ptr ss:[di + 6]
7267  26 8A 45 06     mov al, byte ptr es:[di + 6]
726B  A2 0C 83        mov byte ptr [0x830c], al
726E  C6 06 0D 83 00  mov byte ptr [0x830d], 0
7273  A1 15 83        mov ax, word ptr [0x8315]
7276  8B 7E 04        mov di, word ptr [bp + 4]
7279  36 C4 7D 06     les di, ptr ss:[di + 6]
727D  26 89 45 07     mov word ptr es:[di + 7], ax
loc_7281:
7281  89 EC           mov sp, bp
7283  5D              pop bp
7284  C2 02 00        ret 2

; ---- routine 0791:7287  (found by: call)
sub_7287:
7287  55              push bp
7288  89 E5           mov bp, sp
728A  C4 7E 06        les di, ptr [bp + 6]
728D  26 8A 45 06     mov al, byte ptr es:[di + 6]
7291  3A 06 0B 83     cmp al, byte ptr [0x830b]
7295  75 06           jne 0x729d
7297  55              push bp
7298  E8 4D FF        call 0x71e8
729B  EB 4F           jmp 0x72ec
loc_729D:
729D  C4 7E 06        les di, ptr [bp + 6]
72A0  26 8A 45 06     mov al, byte ptr es:[di + 6]
72A4  30 E4           xor ah, ah
72A6  50              push ax
72A7  E8 B3 91        call 0x45d
72AA  08 C0           or al, al
72AC  74 0B           je 0x72b9
72AE  C4 7E 06        les di, ptr [bp + 6]
72B1  06              push es
72B2  57              push di
72B3  0E              push cs
72B4  E8 9D D0        call 0x4354
72B7  EB 33           jmp 0x72ec
loc_72B9:
72B9  C4 7E 06        les di, ptr [bp + 6]
72BC  26 FF 35        push word ptr es:[di]
72BF  A0 0B 83        mov al, byte ptr [0x830b]
72C2  30 E4           xor ah, ah
72C4  BA 16 00        mov dx, 0x16
72C7  F7 E2           mul dx
72C9  8B F8           mov di, ax
72CB  81 C7 E8 80     add di, 0x80e8
72CF  1E              push ds
72D0  57              push di
72D1  0E              push cs
72D2  E8 E3 BB        call 0x2eb8
72D5  08 C0           or al, al
72D7  74 0A           je 0x72e3
72D9  C4 7E 06        les di, ptr [bp + 6]
72DC  26 C6 45 08 00  mov byte ptr es:[di + 8], 0
72E1  EB 09           jmp 0x72ec
loc_72E3:
72E3  C4 7E 06        les di, ptr [bp + 6]
72E6  06              push es
72E7  57              push di
72E8  0E              push cs
72E9  E8 78 D8        call 0x4b64
loc_72EC:
72EC  89 EC           mov sp, bp
72EE  5D              pop bp
72EF  CA 04 00        retf 4

; ---- routine 0791:72F2  (found by: call)
sub_72F2:
72F2  55              push bp
72F3  89 E5           mov bp, sp
72F5  8B 7E 04        mov di, word ptr [bp + 4]
72F8  36 C4 7D 06     les di, ptr ss:[di + 6]
72FC  06              push es
72FD  57              push di
72FE  0E              push cs
72FF  E8 C3 B9        call 0x2cc5
7302  08 C0           or al, al
7304  75 03           jne 0x7309
7306  E9 AB 00        jmp 0x73b4
loc_7309:
7309  8B 7E 04        mov di, word ptr [bp + 4]
730C  36 C4 7D 06     les di, ptr ss:[di + 6]
7310  26 8B 05        mov ax, word ptr es:[di]
7313  3B 06 15 83     cmp ax, word ptr [0x8315]
7317  75 67           jne 0x7380
7319  80 3E 23 83 00  cmp byte ptr [0x8323], 0
731E  74 1C           je 0x733c
7320  B0 11           mov al, 0x11
7322  50              push ax
7323  B8 03 00        mov ax, 3
7326  50              push ax
7327  8B 7E 04        mov di, word ptr [bp + 4]
732A  36 C4 7D 06     les di, ptr ss:[di + 6]
732E  06              push es
732F  57              push di
7330  0E              push cs
7331  E8 0B C9        call 0x3c3f
7334  B0 05           mov al, 5
7336  50              push ax
7337  E8 EF B5        call 0x2929
733A  EB 42           jmp 0x737e
loc_733C:
733C  B0 00           mov al, 0
733E  50              push ax
733F  E8 70 B5        call 0x28b2
7342  08 C0           or al, al
7344  74 38           je 0x737e
7346  8B 7E 04        mov di, word ptr [bp + 4]
7349  36 C4 7D 06     les di, ptr ss:[di + 6]
734D  06              push es
734E  57              push di
734F  0E              push cs
7350  E8 92 B8        call 0x2be5
7353  98              cwde
7354  B9 18 00        mov cx, 0x18
7357  F7 E9           imul cx
7359  8B 7E 04        mov di, word ptr [bp + 4]
735C  36 C4 7D 06     les di, ptr ss:[di + 6]
7360  26 88 45 08     mov byte ptr es:[di + 8], al
7364  80 3E 26 83 00  cmp byte ptr [0x8326], 0
7369  74 08           je 0x7373
736B  B0 3C           mov al, 0x3c
736D  50              push ax
736E  E8 32 B7        call 0x2aa3
7371  EB 06           jmp 0x7379
loc_7373:
7373  B0 2F           mov al, 0x2f
7375  50              push ax
7376  E8 2A B7        call 0x2aa3
loc_7379:
7379  C6 06 23 83 01  mov byte ptr [0x8323], 1
loc_737E:
737E  EB 34           jmp 0x73b4
loc_7380:
7380  C4 3E 23 A9     les di, ptr [0xa923]
7384  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
7388  30 E4           xor ah, ah
738A  B9 28 00        mov cx, 0x28
738D  F7 E9           imul cx
738F  50              push ax
7390  E8 92 90        call 0x425
7393  8B 7E 04        mov di, word ptr [bp + 4]
7396  36 C4 7D 06     les di, ptr ss:[di + 6]
739A  26 8A 45 06     mov al, byte ptr es:[di + 6]
739E  A2 0C 83        mov byte ptr [0x830c], al
73A1  C6 06 0D 83 00  mov byte ptr [0x830d], 0
73A6  A1 15 83        mov ax, word ptr [0x8315]
73A9  8B 7E 04        mov di, word ptr [bp + 4]
73AC  36 C4 7D 06     les di, ptr ss:[di + 6]
73B0  26 89 45 07     mov word ptr es:[di + 7], ax
loc_73B4:
73B4  89 EC           mov sp, bp
73B6  5D              pop bp
73B7  C2 02 00        ret 2

; ---- routine 0791:73BA  (found by: call)
sub_73BA:
73BA  55              push bp
73BB  89 E5           mov bp, sp
73BD  C4 7E 06        les di, ptr [bp + 6]
73C0  26 8A 45 06     mov al, byte ptr es:[di + 6]
73C4  3A 06 0B 83     cmp al, byte ptr [0x830b]
73C8  75 07           jne 0x73d1
73CA  55              push bp
73CB  E8 24 FF        call 0x72f2
73CE  E9 EB 00        jmp 0x74bc
loc_73D1:
73D1  80 3E 26 83 00  cmp byte ptr [0x8326], 0
73D6  74 03           je 0x73db
73D8  E9 80 00        jmp 0x745b
loc_73DB:
73DB  C4 7E 06        les di, ptr [bp + 6]
73DE  26 8A 45 06     mov al, byte ptr es:[di + 6]
73E2  30 E4           xor ah, ah
73E4  50              push ax
73E5  E8 75 90        call 0x45d
73E8  08 C0           or al, al
73EA  74 16           je 0x7402
73EC  FF 36 4E 08     push word ptr [0x84e]
73F0  C4 7E 06        les di, ptr [bp + 6]
73F3  06              push es
73F4  57              push di
73F5  0E              push cs
73F6  E8 8D B8        call 0x2c86
73F9  C4 7E 06        les di, ptr [bp + 6]
73FC  26 89 45 07     mov word ptr es:[di + 7], ax
7400  EB 57           jmp 0x7459
loc_7402:
7402  C4 7E 06        les di, ptr [bp + 6]
7405  06              push es
7406  57              push di
7407  0E              push cs
7408  E8 A6 B7        call 0x2bb1
740B  30 E4           xor ah, ah
740D  D1 E0           shl ax, 1
740F  50              push ax
7410  C4 7E 06        les di, ptr [bp + 6]
7413  06              push es
7414  57              push di
7415  0E              push cs
7416  E8 38 B7        call 0x2b51
7419  98              cwde
741A  BA 14 00        mov dx, 0x14
741D  F7 E2           mul dx
741F  8B F8           mov di, ax
7421  58              pop ax
7422  03 F8           add di, ax
7424  8B 85 22 08     mov ax, word ptr [di + 0x822]
7428  C4 7E 06        les di, ptr [bp + 6]
742B  26 89 45 07     mov word ptr es:[di + 7], ax
742F  A0 0B 83        mov al, byte ptr [0x830b]
7432  30 E4           xor ah, ah
7434  BA 16 00        mov dx, 0x16
7437  F7 E2           mul dx
7439  8B F8           mov di, ax
743B  81 C7 E8 80     add di, 0x80e8
743F  1E              push ds
7440  57              push di
7441  0E              push cs
7442  E8 A0 B7        call 0x2be5
7445  98              cwde
7446  8B D0           mov dx, ax
7448  C4 7E 06        les di, ptr [bp + 6]
744B  26 8A 45 08     mov al, byte ptr es:[di + 8]
744F  98              cwde
7450  F7 EA           imul dx
7452  C4 7E 06        les di, ptr [bp + 6]
7455  26 88 45 08     mov byte ptr es:[di + 8], al
loc_7459:
7459  EB 4C           jmp 0x74a7
loc_745B:
745B  C4 7E 06        les di, ptr [bp + 6]
745E  06              push es
745F  57              push di
7460  0E              push cs
7461  E8 ED B6        call 0x2b51
7464  08 C0           or al, al
7466  75 27           jne 0x748f
7468  C4 7E 06        les di, ptr [bp + 6]
746B  26 8A 45 06     mov al, byte ptr es:[di + 6]
746F  30 E4           xor ah, ah
7471  50              push ax
7472  E8 E8 8F        call 0x45d
7475  08 C0           or al, al
7477  74 16           je 0x748f
7479  FF 36 4E 08     push word ptr [0x84e]
747D  C4 7E 06        les di, ptr [bp + 6]
7480  06              push es
7481  57              push di
7482  0E              push cs
7483  E8 00 B8        call 0x2c86
7486  C4 7E 06        les di, ptr [bp + 6]
7489  26 89 45 07     mov word ptr es:[di + 7], ax
748D  EB 18           jmp 0x74a7
loc_748F:
748F  C4 7E 06        les di, ptr [bp + 6]
7492  26 8A 45 06     mov al, byte ptr es:[di + 6]
7496  30 E4           xor ah, ah
7498  8B F8           mov di, ax
749A  D1 E7           shl di, 1
749C  8B 85 4E 08     mov ax, word ptr [di + 0x84e]
74A0  C4 7E 06        les di, ptr [bp + 6]
74A3  26 89 45 07     mov word ptr es:[di + 7], ax
loc_74A7:
74A7  C4 7E 06        les di, ptr [bp + 6]
74AA  06              push es
74AB  57              push di
74AC  0E              push cs
74AD  E8 15 B8        call 0x2cc5
74B0  08 C0           or al, al
74B2  74 08           je 0x74bc
74B4  C4 7E 06        les di, ptr [bp + 6]
74B7  26 C6 45 12 00  mov byte ptr es:[di + 0x12], 0
loc_74BC:
74BC  89 EC           mov sp, bp
74BE  5D              pop bp
74BF  CA 04 00        retf 4

; ---- routine 0791:74C2  (found by: call)
sub_74C2:
74C2  55              push bp
74C3  89 E5           mov bp, sp
74C5  83 EC 02        sub sp, 2
74C8  8B 7E 04        mov di, word ptr [bp + 4]
74CB  36 C4 7D 06     les di, ptr ss:[di + 6]
74CF  06              push es
74D0  57              push di
74D1  0E              push cs
74D2  E8 F0 B7        call 0x2cc5
74D5  08 C0           or al, al
74D7  75 03           jne 0x74dc
74D9  E9 1F 01        jmp 0x75fb
loc_74DC:
74DC  80 3E 23 83 00  cmp byte ptr [0x8323], 0
74E1  75 03           jne 0x74e6
74E3  E9 EA 00        jmp 0x75d0
loc_74E6:
74E6  E8 AD B4        call 0x2996
74E9  08 C0           or al, al
74EB  74 04           je 0x74f1
74ED  B0 00           mov al, 0
74EF  EB 02           jmp 0x74f3
loc_74F1:
74F1  B0 01           mov al, 1
loc_74F3:
74F3  98              cwde
74F4  8B F8           mov di, ax
74F6  8A 85 68 06     mov al, byte ptr [di + 0x668]
74FA  30 E4           xor ah, ah
74FC  40              inc ax
74FD  BA 16 00        mov dx, 0x16
7500  F7 E2           mul dx
7502  8B F8           mov di, ax
7504  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
7508  98              cwde
7509  09 C0           or ax, ax
750B  79 02           jns 0x750f
750D  F7 D8           neg ax
loc_750F:
750F  3D 25 00        cmp ax, 0x25
7512  74 03           je 0x7517
7514  E9 E4 00        jmp 0x75fb
loc_7517:
7517  8B 7E 04        mov di, word ptr [bp + 4]
751A  36 C4 7D 06     les di, ptr ss:[di + 6]
751E  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7522  BA 14 00        mov dx, 0x14
7525  F7 E2           mul dx
7527  C4 3E 1B A9     les di, ptr [0xa91b]
752B  03 F8           add di, ax
752D  26 8A 45 06     mov al, byte ptr es:[di + 6]
7531  30 E4           xor ah, ah
7533  89 46 FE        mov word ptr [bp - 2], ax
7536  8B 7E 04        mov di, word ptr [bp + 4]
7539  36 C4 7D 06     les di, ptr ss:[di + 6]
753D  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7541  BA 14 00        mov dx, 0x14
7544  F7 E2           mul dx
7546  C4 3E 1B A9     les di, ptr [0xa91b]
754A  03 F8           add di, ax
754C  26 C6 45 06 01  mov byte ptr es:[di + 6], 1
7551  9A FA 06 4B 21  call far 214B:06FA
7556  08 C0           or al, al
7558  74 44           je 0x759e
755A  8B 7E 04        mov di, word ptr [bp + 4]
755D  36 C4 7D 06     les di, ptr ss:[di + 6]
7561  06              push es
7562  57              push di
7563  0E              push cs
7564  E8 C1 B9        call 0x2f28
7567  08 C0           or al, al
7569  74 33           je 0x759e
756B  8A 4E FE        mov cl, byte ptr [bp - 2]
756E  8B 7E 04        mov di, word ptr [bp + 4]
7571  36 C4 7D 06     les di, ptr ss:[di + 6]
7575  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7579  BA 14 00        mov dx, 0x14
757C  F7 E2           mul dx
757E  C4 3E 1B A9     les di, ptr [0xa91b]
7582  03 F8           add di, ax
7584  26 88 4D 06     mov byte ptr es:[di + 6], cl
7588  B0 11           mov al, 0x11
758A  50              push ax
758B  B8 04 00        mov ax, 4
758E  50              push ax
758F  8B 7E 04        mov di, word ptr [bp + 4]
7592  36 C4 7D 06     les di, ptr ss:[di + 6]
7596  06              push es
7597  57              push di
7598  0E              push cs
7599  E8 A3 C6        call 0x3c3f
759C  EB 2A           jmp 0x75c8
loc_759E:
759E  8A 4E FE        mov cl, byte ptr [bp - 2]
75A1  8B 7E 04        mov di, word ptr [bp + 4]
75A4  36 C4 7D 06     les di, ptr ss:[di + 6]
75A8  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
75AC  BA 14 00        mov dx, 0x14
75AF  F7 E2           mul dx
75B1  C4 3E 1B A9     les di, ptr [0xa91b]
75B5  03 F8           add di, ax
75B7  26 88 4D 06     mov byte ptr es:[di + 6], cl
75BB  8B 7E 04        mov di, word ptr [bp + 4]
75BE  36 C4 7D 06     les di, ptr ss:[di + 6]
75C2  06              push es
75C3  57              push di
75C4  0E              push cs
75C5  E8 5B BD        call 0x3323
loc_75C8:
75C8  B0 05           mov al, 5
75CA  50              push ax
75CB  E8 5B B3        call 0x2929
75CE  EB 2B           jmp 0x75fb
loc_75D0:
75D0  8B 7E 04        mov di, word ptr [bp + 4]
75D3  36 C4 7D 06     les di, ptr ss:[di + 6]
75D7  26 80 7D 10 00  cmp byte ptr es:[di + 0x10], 0
75DC  76 0D           jbe 0x75eb
75DE  8B 7E 04        mov di, word ptr [bp + 4]
75E1  36 C4 7D 06     les di, ptr ss:[di + 6]
75E5  26 FE 4D 10     dec byte ptr es:[di + 0x10]
75E9  EB 10           jmp 0x75fb
loc_75EB:
75EB  C6 06 02 83 00  mov byte ptr [0x8302], 0
75F0  B0 30           mov al, 0x30
75F2  50              push ax
75F3  E8 AD B4        call 0x2aa3
75F6  C6 06 23 83 01  mov byte ptr [0x8323], 1
loc_75FB:
75FB  89 EC           mov sp, bp
75FD  5D              pop bp
75FE  C2 02 00        ret 2
; data (not reached as code), 32 bytes
7601                  db 80 0F 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
7611                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:7621  (found by: call)
sub_7621:
7621  55              push bp
7622  89 E5           mov bp, sp
7624  83 EC 04        sub sp, 4
7627  C4 7E 06        les di, ptr [bp + 6]
762A  26 8A 45 06     mov al, byte ptr es:[di + 6]
762E  3A 06 0B 83     cmp al, byte ptr [0x830b]
7632  75 07           jne 0x763b
7634  55              push bp
7635  E8 8A FE        call 0x74c2
7638  E9 40 02        jmp 0x787b
loc_763B:
763B  C4 7E 06        les di, ptr [bp + 6]
763E  06              push es
763F  57              push di
7640  0E              push cs
7641  E8 0D B5        call 0x2b51
7644  08 C0           or al, al
7646  74 03           je 0x764b
7648  E9 BA 01        jmp 0x7805
loc_764B:
764B  A0 0B 83        mov al, byte ptr [0x830b]
764E  30 E4           xor ah, ah
7650  BA 16 00        mov dx, 0x16
7653  F7 E2           mul dx
7655  8B F8           mov di, ax
7657  81 C7 E8 80     add di, 0x80e8
765B  1E              push ds
765C  57              push di
765D  0E              push cs
765E  E8 84 B5        call 0x2be5
7661  98              cwde
7662  8B D0           mov dx, ax
7664  A0 16 83        mov al, byte ptr [0x8316]
7667  98              cwde
7668  F7 EA           imul dx
766A  09 C0           or ax, ax
766C  7F 03           jg 0x7671
766E  E9 94 01        jmp 0x7805
loc_7671:
7671  A0 15 83        mov al, byte ptr [0x8315]
7674  98              cwde
7675  09 C0           or ax, ax
7677  79 02           jns 0x767b
7679  F7 D8           neg ax
loc_767B:
767B  8B D0           mov dx, ax
767D  A0 16 83        mov al, byte ptr [0x8316]
7680  98              cwde
7681  09 C0           or ax, ax
7683  79 02           jns 0x7687
7685  F7 D8           neg ax
loc_7687:
7687  2B C2           sub ax, dx
7689  3D 0A 00        cmp ax, 0xa
768C  7F 03           jg 0x7691
768E  E9 74 01        jmp 0x7805
loc_7691:
7691  C4 7E 06        les di, ptr [bp + 6]
7694  06              push es
7695  57              push di
7696  0E              push cs
7697  E8 17 B5        call 0x2bb1
769A  50              push ax
769B  BF 01 76        mov di, 0x7601
769E  0E              push cs
769F  57              push di
76A0  9A DF 08 E4 23  call far 23E4:08DF
76A5  75 03           jne 0x76aa
76A7  E9 5B 01        jmp 0x7805
loc_76AA:
76AA  A0 16 83        mov al, byte ptr [0x8316]
76AD  98              cwde
76AE  09 C0           or ax, ax
76B0  79 02           jns 0x76b4
76B2  F7 D8           neg ax
loc_76B4:
76B4  3D 1A 00        cmp ax, 0x1a
76B7  7C 03           jl 0x76bc
76B9  E9 89 00        jmp 0x7745
loc_76BC:
76BC  80 3E 15 83 00  cmp byte ptr [0x8315], 0
76C1  7E 06           jle 0x76c9
76C3  C6 46 FC 01     mov byte ptr [bp - 4], 1
76C7  EB 04           jmp 0x76cd
loc_76C9:
76C9  C6 46 FC FF     mov byte ptr [bp - 4], 0xff
loc_76CD:
76CD  A0 15 83        mov al, byte ptr [0x8315]
76D0  98              cwde
76D1  09 C0           or ax, ax
76D3  79 02           jns 0x76d7
76D5  F7 D8           neg ax
loc_76D7:
76D7  3D 04 00        cmp ax, 4
76DA  7E 1B           jle 0x76f7
76DC  A0 0B 83        mov al, byte ptr [0x830b]
76DF  30 E4           xor ah, ah
76E1  BA 16 00        mov dx, 0x16
76E4  F7 E2           mul dx
76E6  8B F8           mov di, ax
76E8  81 C7 E8 80     add di, 0x80e8
76EC  1E              push ds
76ED  57              push di
76EE  0E              push cs
76EF  E8 F3 B4        call 0x2be5
76F2  88 46 FD        mov byte ptr [bp - 3], al
76F5  EB 04           jmp 0x76fb
loc_76F7:
76F7  C6 46 FD 00     mov byte ptr [bp - 3], 0
loc_76FB:
76FB  8A 46 FC        mov al, byte ptr [bp - 4]
76FE  98              cwde
76FF  D1 E0           shl ax, 1
7701  8B D8           mov bx, ax
7703  A0 15 83        mov al, byte ptr [0x8315]
7706  98              cwde
7707  99              cdq
7708  B9 02 00        mov cx, 2
770B  F7 F9           idiv cx
770D  2B C3           sub ax, bx
770F  88 46 FE        mov byte ptr [bp - 2], al
7712  8A 46 FD        mov al, byte ptr [bp - 3]
7715  98              cwde
7716  D1 E0           shl ax, 1
7718  50              push ax
7719  A0 0B 83        mov al, byte ptr [0x830b]
771C  30 E4           xor ah, ah
771E  BA 16 00        mov dx, 0x16
7721  F7 E2           mul dx
7723  8B F8           mov di, ax
7725  81 C7 E8 80     add di, 0x80e8
7729  1E              push ds
772A  57              push di
772B  0E              push cs
772C  E8 B6 B4        call 0x2be5
772F  98              cwde
7730  B9 05 00        mov cx, 5
7733  F7 E9           imul cx
7735  8B D0           mov dx, ax
7737  A0 16 83        mov al, byte ptr [0x8316]
773A  98              cwde
773B  03 C2           add ax, dx
773D  5A              pop dx
773E  2B C2           sub ax, dx
7740  88 46 FF        mov byte ptr [bp - 1], al
7743  EB 5F           jmp 0x77a4
loc_7745:
7745  C6 46 FC 00     mov byte ptr [bp - 4], 0
7749  C6 46 FD 01     mov byte ptr [bp - 3], 1
774D  80 3E 15 83 00  cmp byte ptr [0x8315], 0
7752  7C 04           jl 0x7758
7754  B0 00           mov al, 0
7756  EB 02           jmp 0x775a
loc_7758:
7758  B0 01           mov al, 1
loc_775A:
775A  98              cwde
775B  8B F8           mov di, ax
775D  8A 85 20 79     mov al, byte ptr [di + 0x7920]
7761  98              cwde
7762  B9 03 00        mov cx, 3
7765  F7 E9           imul cx
7767  8B D0           mov dx, ax
7769  A0 15 83        mov al, byte ptr [0x8315]
776C  98              cwde
776D  03 C2           add ax, dx
776F  88 46 FE        mov byte ptr [bp - 2], al
7772  80 3E 16 83 00  cmp byte ptr [0x8316], 0
7777  7C 04           jl 0x777d
7779  B0 00           mov al, 0
777B  EB 02           jmp 0x777f
loc_777D:
777D  B0 01           mov al, 1
loc_777F:
777F  98              cwde
7780  8B F8           mov di, ax
7782  8A 85 20 79     mov al, byte ptr [di + 0x7920]
7786  98              cwde
7787  8B D8           mov bx, ax
7789  A0 16 83        mov al, byte ptr [0x8316]
778C  98              cwde
778D  09 C0           or ax, ax
778F  79 02           jns 0x7793
7791  F7 D8           neg ax
loc_7793:
7793  05 E6 FF        add ax, 0xffe6
7796  99              cdq
7797  B9 02 00        mov cx, 2
779A  F7 F9           idiv cx
779C  05 1C 00        add ax, 0x1c
779F  F7 EB           imul bx
77A1  88 46 FF        mov byte ptr [bp - 1], al
loc_77A4:
77A4  C4 7E 06        les di, ptr [bp + 6]
77A7  06              push es
77A8  57              push di
77A9  0E              push cs
77AA  E8 04 B4        call 0x2bb1
77AD  30 E4           xor ah, ah
77AF  2D 07 00        sub ax, 7
77B2  8B D0           mov dx, ax
77B4  8A 46 FD        mov al, byte ptr [bp - 3]
77B7  98              cwde
77B8  F7 EA           imul dx
77BA  8B D0           mov dx, ax
77BC  8A 46 FF        mov al, byte ptr [bp - 1]
77BF  98              cwde
77C0  03 C2           add ax, dx
77C2  C4 7E 06        les di, ptr [bp + 6]
77C5  26 88 45 08     mov byte ptr es:[di + 8], al
77C9  C4 7E 06        les di, ptr [bp + 6]
77CC  06              push es
77CD  57              push di
77CE  0E              push cs
77CF  E8 DF B3        call 0x2bb1
77D2  30 E4           xor ah, ah
77D4  2D 07 00        sub ax, 7
77D7  8B D0           mov dx, ax
77D9  8A 46 FC        mov al, byte ptr [bp - 4]
77DC  98              cwde
77DD  F7 EA           imul dx
77DF  8B D0           mov dx, ax
77E1  8A 46 FE        mov al, byte ptr [bp - 2]
77E4  98              cwde
77E5  03 C2           add ax, dx
77E7  C4 7E 06        les di, ptr [bp + 6]
77EA  26 88 45 07     mov byte ptr es:[di + 7], al
77EE  C4 7E 06        les di, ptr [bp + 6]
77F1  06              push es
77F2  57              push di
77F3  0E              push cs
77F4  E8 CE B4        call 0x2cc5
77F7  08 C0           or al, al
77F9  74 08           je 0x7803
77FB  C4 7E 06        les di, ptr [bp + 6]
77FE  26 C6 45 12 00  mov byte ptr es:[di + 0x12], 0
loc_7803:
7803  EB 76           jmp 0x787b
loc_7805:
7805  C4 7E 06        les di, ptr [bp + 6]
7808  06              push es
7809  57              push di
780A  0E              push cs
780B  E8 56 D3        call 0x4b64
780E  C4 7E 06        les di, ptr [bp + 6]
7811  06              push es
7812  57              push di
7813  0E              push cs
7814  E8 3A B3        call 0x2b51
7817  08 C0           or al, al
7819  75 60           jne 0x787b
loc_781B:
781B  A0 16 83        mov al, byte ptr [0x8316]
781E  98              cwde
781F  09 C0           or ax, ax
7821  79 02           jns 0x7825
7823  F7 D8           neg ax
loc_7825:
7825  8B D0           mov dx, ax
7827  C4 7E 06        les di, ptr [bp + 6]
782A  26 8A 45 08     mov al, byte ptr es:[di + 8]
782E  98              cwde
782F  09 C0           or ax, ax
7831  79 02           jns 0x7835
7833  F7 D8           neg ax
loc_7835:
7835  2B C2           sub ax, dx
7837  3D 04 00        cmp ax, 4
783A  7D 1F           jge 0x785b
783C  A0 0B 83        mov al, byte ptr [0x830b]
783F  30 E4           xor ah, ah
7841  BA 16 00        mov dx, 0x16
7844  F7 E2           mul dx
7846  8B F8           mov di, ax
7848  81 C7 E8 80     add di, 0x80e8
784C  1E              push ds
784D  57              push di
784E  0E              push cs
784F  E8 93 B3        call 0x2be5
7852  C4 7E 06        les di, ptr [bp + 6]
7855  26 00 45 08     add byte ptr es:[di + 8], al
7859  EB C0           jmp 0x781b
loc_785B:
785B  C4 7E 06        les di, ptr [bp + 6]
785E  26 8A 45 07     mov al, byte ptr es:[di + 7]
7862  3A 06 15 83     cmp al, byte ptr [0x8315]
7866  75 13           jne 0x787b
7868  9A FA 06 4B 21  call far 214B:06FA
786D  98              cwde
786E  8B F8           mov di, ax
7870  8A 85 20 79     mov al, byte ptr [di + 0x7920]
7874  C4 7E 06        les di, ptr [bp + 6]
7877  26 00 45 07     add byte ptr es:[di + 7], al
loc_787B:
787B  89 EC           mov sp, bp
787D  5D              pop bp
787E  CA 04 00        retf 4

