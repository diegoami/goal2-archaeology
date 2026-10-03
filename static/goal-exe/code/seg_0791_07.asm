; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 7 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:3D38  (found by: call)
sub_3D38:
3D38  55              push bp
3D39  89 E5           mov bp, sp
3D3B  83 EC 08        sub sp, 8
3D3E  E8 55 EC        call 0x2996
3D41  98              cwde
3D42  8B F8           mov di, ax
3D44  8A 85 68 06     mov al, byte ptr [di + 0x668]
3D48  30 E4           xor ah, ah
3D4A  05 0B 00        add ax, 0xb
3D4D  89 46 FC        mov word ptr [bp - 4], ax
3D50  E8 43 EC        call 0x2996
3D53  98              cwde
3D54  8B F8           mov di, ax
3D56  8A 85 68 06     mov al, byte ptr [di + 0x668]
3D5A  30 E4           xor ah, ah
3D5C  05 02 00        add ax, 2
3D5F  3B 46 FC        cmp ax, word ptr [bp - 4]
3D62  76 03           jbe 0x3d67
3D64  E9 89 00        jmp 0x3df0
loc_3D67:
3D67  89 46 FE        mov word ptr [bp - 2], ax
3D6A  EB 03           jmp 0x3d6f
loc_3D6C:
3D6C  FF 46 FE        inc word ptr [bp - 2]
loc_3D6F:
3D6F  8B 46 FE        mov ax, word ptr [bp - 2]
3D72  BA 16 00        mov dx, 0x16
3D75  F7 E2           mul dx
3D77  8B F8           mov di, ax
3D79  81 C7 E8 80     add di, 0x80e8
3D7D  89 7E F8        mov word ptr [bp - 8], di
3D80  8C 5E FA        mov word ptr [bp - 6], ds
3D83  C4 7E F8        les di, ptr [bp - 8]
3D86  26 8A 45 06     mov al, byte ptr es:[di + 6]
3D8A  30 E4           xor ah, ah
3D8C  3B 46 04        cmp ax, word ptr [bp + 4]
3D8F  74 54           je 0x3de5
3D91  C4 7E F8        les di, ptr [bp - 8]
3D94  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
3D98  BA 14 00        mov dx, 0x14
3D9B  F7 E2           mul dx
3D9D  C4 3E 1B A9     les di, ptr [0xa91b]
3DA1  03 F8           add di, ax
3DA3  26 8A 45 06     mov al, byte ptr es:[di + 6]
3DA7  50              push ax
3DA8  BF 18 3D        mov di, 0x3d18
3DAB  0E              push cs
3DAC  57              push di
3DAD  9A DF 08 E4 23  call far 23E4:08DF
3DB2  74 31           je 0x3de5
3DB4  C4 7E F8        les di, ptr [bp - 8]
3DB7  26 FF 75 0D     push word ptr es:[di + 0xd]
3DBB  9A 16 32 71 17  call far 1771:3216
3DC0  08 C0           or al, al
3DC2  75 21           jne 0x3de5
3DC4  C4 7E F8        les di, ptr [bp - 8]
3DC7  26 FF 35        push word ptr es:[di]
3DCA  C4 7E F8        les di, ptr [bp - 8]
3DCD  06              push es
3DCE  57              push di
3DCF  0E              push cs
3DD0  E8 1D F1        call 0x2ef0
3DD3  08 C0           or al, al
3DD5  74 0E           je 0x3de5
3DD7  C4 7E F8        les di, ptr [bp - 8]
3DDA  26 8B 05        mov ax, word ptr es:[di]
3DDD  C4 7E 06        les di, ptr [bp + 6]
3DE0  26 89 05        mov word ptr es:[di], ax
3DE3  EB 0B           jmp 0x3df0
loc_3DE5:
3DE5  8B 46 FE        mov ax, word ptr [bp - 2]
3DE8  3B 46 FC        cmp ax, word ptr [bp - 4]
3DEB  74 03           je 0x3df0
3DED  E9 7C FF        jmp 0x3d6c
loc_3DF0:
3DF0  89 EC           mov sp, bp
3DF2  5D              pop bp
3DF3  C2 06 00        ret 6

; ---- routine 0791:3DF6  (found by: call)
sub_3DF6:
3DF6  55              push bp
3DF7  89 E5           mov bp, sp
3DF9  83 EC 02        sub sp, 2
3DFC  31 C0           xor ax, ax
3DFE  89 46 FE        mov word ptr [bp - 2], ax
3E01  8D 7E FE        lea di, [bp - 2]
3E04  16              push ss
3E05  57              push di
3E06  C4 7E 06        les di, ptr [bp + 6]
3E09  26 8A 45 06     mov al, byte ptr es:[di + 6]
3E0D  30 E4           xor ah, ah
3E0F  50              push ax
3E10  E8 25 FF        call 0x3d38
3E13  83 7E FE 00     cmp word ptr [bp - 2], 0
3E17  75 55           jne 0x3e6e
3E19  E8 FE E7        call 0x261a
3E1C  99              cdq
3E1D  B9 04 00        mov cx, 4
3E20  F7 F9           idiv cx
3E22  05 04 00        add ax, 4
3E25  8B D0           mov dx, ax
3E27  C4 7E 06        les di, ptr [bp + 6]
3E2A  26 80 3D 00     cmp byte ptr es:[di], 0
3E2E  7C 04           jl 0x3e34
3E30  B0 00           mov al, 0
3E32  EB 02           jmp 0x3e36
loc_3E34:
3E34  B0 01           mov al, 1
loc_3E36:
3E36  98              cwde
3E37  8B F8           mov di, ax
3E39  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3E3D  98              cwde
3E3E  F7 EA           imul dx
3E40  88 46 FE        mov byte ptr [bp - 2], al
3E43  B8 0A 00        mov ax, 0xa
3E46  50              push ax
3E47  9A B1 06 4B 21  call far 214B:06B1
3E4C  05 18 00        add ax, 0x18
3E4F  8B D0           mov dx, ax
3E51  C4 7E 06        les di, ptr [bp + 6]
3E54  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
3E59  7F 04           jg 0x3e5f
3E5B  B0 00           mov al, 0
3E5D  EB 02           jmp 0x3e61
loc_3E5F:
3E5F  B0 01           mov al, 1
loc_3E61:
3E61  98              cwde
3E62  8B F8           mov di, ax
3E64  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3E68  98              cwde
3E69  F7 EA           imul dx
3E6B  88 46 FF        mov byte ptr [bp - 1], al
loc_3E6E:
3E6E  C6 06 0C 83 FF  mov byte ptr [0x830c], 0xff
3E73  FF 76 FE        push word ptr [bp - 2]
3E76  B8 05 00        mov ax, 5
3E79  50              push ax
3E7A  C4 7E 06        les di, ptr [bp + 6]
3E7D  06              push es
3E7E  57              push di
3E7F  0E              push cs
3E80  E8 3E F6        call 0x34c1
3E83  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
3E88  74 04           je 0x3e8e
3E8A  B0 00           mov al, 0
3E8C  EB 02           jmp 0x3e90
loc_3E8E:
3E8E  B0 01           mov al, 1
loc_3E90:
3E90  98              cwde
3E91  8B F8           mov di, ax
3E93  8A 85 94 07     mov al, byte ptr [di + 0x794]
3E97  50              push ax
3E98  E8 08 EC        call 0x2aa3
3E9B  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3EA0  B8 08 00        mov ax, 8
3EA3  50              push ax
3EA4  9A D0 06 4B 21  call far 214B:06D0
3EA9  08 C0           or al, al
3EAB  74 04           je 0x3eb1
3EAD  B0 00           mov al, 0
3EAF  EB 02           jmp 0x3eb3
loc_3EB1:
3EB1  B0 01           mov al, 1
loc_3EB3:
3EB3  A2 03 83        mov byte ptr [0x8303], al
3EB6  C4 7E 06        les di, ptr [bp + 6]
3EB9  06              push es
3EBA  57              push di
3EBB  0E              push cs
3EBC  E8 80 0E        call 0x4d3f
3EBF  89 EC           mov sp, bp
3EC1  5D              pop bp
3EC2  CA 04 00        retf 4

; ---- routine 0791:3EC5  (found by: call)
sub_3EC5:
3EC5  55              push bp
3EC6  89 E5           mov bp, sp
3EC8  8A 46 0A        mov al, byte ptr [bp + 0xa]
3ECB  50              push ax
3ECC  B8 01 00        mov ax, 1
3ECF  50              push ax
3ED0  C4 7E 06        les di, ptr [bp + 6]
3ED3  06              push es
3ED4  57              push di
3ED5  0E              push cs
3ED6  E8 66 FD        call 0x3c3f
3ED9  89 EC           mov sp, bp
3EDB  5D              pop bp
3EDC  CA 06 00        retf 6

; ---- routine 0791:3EDF  (found by: call)
sub_3EDF:
3EDF  55              push bp
3EE0  89 E5           mov bp, sp
3EE2  B0 14           mov al, 0x14
3EE4  50              push ax
3EE5  B8 02 00        mov ax, 2
3EE8  50              push ax
3EE9  C4 7E 06        les di, ptr [bp + 6]
3EEC  06              push es
3EED  57              push di
3EEE  0E              push cs
3EEF  E8 4D FD        call 0x3c3f
3EF2  89 EC           mov sp, bp
3EF4  5D              pop bp
3EF5  CA 04 00        retf 4

; ---- routine 0791:3EF8  (found by: call)
sub_3EF8:
3EF8  55              push bp
3EF9  89 E5           mov bp, sp
3EFB  83 EC 04        sub sp, 4
3EFE  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3F03  A1 F6 82        mov ax, word ptr [0x82f6]
3F06  89 46 FE        mov word ptr [bp - 2], ax
3F09  83 7E 0A 09     cmp word ptr [bp + 0xa], 9
3F0D  74 04           je 0x3f13
3F0F  B0 00           mov al, 0
3F11  EB 02           jmp 0x3f15
loc_3F13:
3F13  B0 01           mov al, 1
loc_3F15:
3F15  88 46 FD        mov byte ptr [bp - 3], al
3F18  8A 46 FD        mov al, byte ptr [bp - 3]
3F1B  98              cwde
3F1C  8B F8           mov di, ax
3F1E  8A 85 9C 07     mov al, byte ptr [di + 0x79c]
3F22  30 E4           xor ah, ah
3F24  31 D2           xor dx, dx
3F26  52              push dx
3F27  50              push ax
3F28  8A 46 FD        mov al, byte ptr [bp - 3]
3F2B  98              cwde
3F2C  8B F8           mov di, ax
3F2E  8A 85 98 07     mov al, byte ptr [di + 0x798]
3F32  30 E4           xor ah, ah
3F34  50              push ax
3F35  8A 46 FD        mov al, byte ptr [bp - 3]
3F38  98              cwde
3F39  8B F8           mov di, ax
3F3B  8A 85 96 07     mov al, byte ptr [di + 0x796]
3F3F  30 E4           xor ah, ah
3F41  50              push ax
3F42  C4 7E 06        les di, ptr [bp + 6]
3F45  06              push es
3F46  57              push di
3F47  0E              push cs
3F48  E8 3F E8        call 0x278a
3F4B  59              pop cx
3F4C  31 D2           xor dx, dx
3F4E  F7 F1           div cx
3F50  50              push ax
3F51  9A B1 06 4B 21  call far 214B:06B1
3F56  99              cdq
3F57  52              push dx
3F58  50              push ax
3F59  9A 56 0D 4B 21  call far 214B:0D56
3F5E  52              push dx
3F5F  50              push ax
3F60  C4 7E 06        les di, ptr [bp + 6]
3F63  06              push es
3F64  57              push di
3F65  0E              push cs
3F66  E8 7C EC        call 0x2be5
3F69  98              cwde
3F6A  99              cdq
3F6B  59              pop cx
3F6C  5B              pop bx
3F6D  9A 79 02 E4 23  call far 23E4:0279
3F72  00 46 FF        add byte ptr [bp - 1], al
3F75  FF 76 FE        push word ptr [bp - 2]
3F78  8A 46 FD        mov al, byte ptr [bp - 3]
3F7B  98              cwde
3F7C  8B F8           mov di, ax
3F7E  8A 85 9A 07     mov al, byte ptr [di + 0x79a]
3F82  30 E4           xor ah, ah
3F84  50              push ax
3F85  C4 7E 06        les di, ptr [bp + 6]
3F88  06              push es
3F89  57              push di
3F8A  0E              push cs
3F8B  E8 33 F5        call 0x34c1
3F8E  C6 06 03 83 01  mov byte ptr [0x8303], 1
3F93  80 7E FD 00     cmp byte ptr [bp - 3], 0
3F97  74 08           je 0x3fa1
3F99  B0 17           mov al, 0x17
3F9B  50              push ax
3F9C  E8 04 EB        call 0x2aa3
3F9F  EB 06           jmp 0x3fa7
loc_3FA1:
3FA1  B0 18           mov al, 0x18
3FA3  50              push ax
3FA4  E8 FC EA        call 0x2aa3
loc_3FA7:
3FA7  89 EC           mov sp, bp
3FA9  5D              pop bp
3FAA  CA 06 00        retf 6

; ---- routine 0791:3FAD  (found by: call)
sub_3FAD:
3FAD  55              push bp
3FAE  89 E5           mov bp, sp
3FB0  83 EC 02        sub sp, 2
3FB3  9A FA 06 4B 21  call far 214B:06FA
3FB8  08 C0           or al, al
3FBA  75 11           jne 0x3fcd
3FBC  C4 7E 06        les di, ptr [bp + 6]
3FBF  26 8A 45 06     mov al, byte ptr es:[di + 6]
3FC3  30 E4           xor ah, ah
3FC5  50              push ax
3FC6  E8 94 C4        call 0x45d
3FC9  08 C0           or al, al
3FCB  74 49           je 0x4016
loc_3FCD:
3FCD  C4 7E 06        les di, ptr [bp + 6]
3FD0  26 80 3D 00     cmp byte ptr es:[di], 0
3FD4  7F 04           jg 0x3fda
3FD6  B0 00           mov al, 0
3FD8  EB 02           jmp 0x3fdc
loc_3FDA:
3FDA  B0 01           mov al, 1
loc_3FDC:
3FDC  98              cwde
3FDD  8B F8           mov di, ax
3FDF  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3FE3  98              cwde
3FE4  B9 0C 00        mov cx, 0xc
3FE7  F7 E9           imul cx
3FE9  88 46 FE        mov byte ptr [bp - 2], al
3FEC  B8 28 00        mov ax, 0x28
3FEF  50              push ax
3FF0  9A B1 06 4B 21  call far 214B:06B1
3FF5  8B D0           mov dx, ax
3FF7  C4 7E 06        les di, ptr [bp + 6]
3FFA  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
3FFF  7F 04           jg 0x4005
4001  B0 00           mov al, 0
4003  EB 02           jmp 0x4007
loc_4005:
4005  B0 01           mov al, 1
loc_4007:
4007  98              cwde
4008  8B F8           mov di, ax
400A  8A 85 20 79     mov al, byte ptr [di + 0x7920]
400E  98              cwde
400F  F7 EA           imul dx
4011  88 46 FF        mov byte ptr [bp - 1], al
4014  EB 4A           jmp 0x4060
loc_4016:
4016  B8 08 00        mov ax, 8
4019  50              push ax
401A  9A B1 06 4B 21  call far 214B:06B1
401F  05 02 00        add ax, 2
4022  8B D0           mov dx, ax
4024  C4 7E 06        les di, ptr [bp + 6]
4027  26 80 3D 00     cmp byte ptr es:[di], 0
402B  7F 04           jg 0x4031
402D  B0 00           mov al, 0
402F  EB 02           jmp 0x4033
loc_4031:
4031  B0 01           mov al, 1
loc_4033:
4033  98              cwde
4034  8B F8           mov di, ax
4036  8A 85 20 79     mov al, byte ptr [di + 0x7920]
403A  98              cwde
403B  F7 EA           imul dx
403D  88 46 FE        mov byte ptr [bp - 2], al
4040  C4 7E 06        les di, ptr [bp + 6]
4043  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
4048  7F 04           jg 0x404e
404A  B0 00           mov al, 0
404C  EB 02           jmp 0x4050
loc_404E:
404E  B0 01           mov al, 1
loc_4050:
4050  98              cwde
4051  8B F8           mov di, ax
4053  8A 85 20 79     mov al, byte ptr [di + 0x7920]
4057  98              cwde
4058  B9 32 00        mov cx, 0x32
405B  F7 E9           imul cx
405D  88 46 FF        mov byte ptr [bp - 1], al
loc_4060:
4060  FF 76 FE        push word ptr [bp - 2]
4063  FF 76 0A        push word ptr [bp + 0xa]
4066  C4 7E 06        les di, ptr [bp + 6]
4069  06              push es
406A  57              push di
406B  0E              push cs
406C  E8 52 F4        call 0x34c1
406F  C6 06 03 83 01  mov byte ptr [0x8303], 1
4074  83 7E 0A 0B     cmp word ptr [bp + 0xa], 0xb
4078  75 08           jne 0x4082
407A  B0 16           mov al, 0x16
407C  50              push ax
407D  E8 23 EA        call 0x2aa3
4080  EB 06           jmp 0x4088
loc_4082:
4082  B0 15           mov al, 0x15
4084  50              push ax
4085  E8 1B EA        call 0x2aa3
loc_4088:
4088  89 EC           mov sp, bp
408A  5D              pop bp
408B  CA 06 00        retf 6

; ---- routine 0791:408E  (found by: call)
sub_408E:
408E  55              push bp
408F  89 E5           mov bp, sp
4091  9A FA 06 4B 21  call far 214B:06FA
4096  08 C0           or al, al
4098  74 0F           je 0x40a9
409A  B8 0B 00        mov ax, 0xb
409D  50              push ax
409E  C4 7E 06        les di, ptr [bp + 6]
40A1  06              push es
40A2  57              push di
40A3  0E              push cs
40A4  E8 06 FF        call 0x3fad
40A7  EB 0D           jmp 0x40b6
loc_40A9:
40A9  B8 0B 00        mov ax, 0xb
40AC  50              push ax
40AD  C4 7E 06        les di, ptr [bp + 6]
40B0  06              push es
40B1  57              push di
40B2  0E              push cs
40B3  E8 42 FE        call 0x3ef8
loc_40B6:
40B6  89 EC           mov sp, bp
40B8  5D              pop bp
40B9  CA 04 00        retf 4

; ---- routine 0791:40BC  (found by: call)
sub_40BC:
40BC  55              push bp
40BD  89 E5           mov bp, sp
40BF  83 EC 06        sub sp, 6
40C2  A0 0B 83        mov al, byte ptr [0x830b]
40C5  30 E4           xor ah, ah
40C7  BA 16 00        mov dx, 0x16
40CA  F7 E2           mul dx
40CC  8B F8           mov di, ax
40CE  81 C7 E8 80     add di, 0x80e8
40D2  89 7E FB        mov word ptr [bp - 5], di
40D5  8C 5E FD        mov word ptr [bp - 3], ds
40D8  C4 7E FB        les di, ptr [bp - 5]
40DB  06              push es
40DC  57              push di
40DD  0E              push cs
40DE  E8 73 EB        call 0x2c54
40E1  08 C0           or al, al
40E3  75 5C           jne 0x4141
40E5  E8 AE E8        call 0x2996
40E8  08 C0           or al, al
40EA  74 04           je 0x40f0
40EC  B0 00           mov al, 0
40EE  EB 02           jmp 0x40f2
loc_40F0:
40F0  B0 01           mov al, 1
loc_40F2:
40F2  98              cwde
40F3  8B F8           mov di, ax
40F5  D1 E7           shl di, 1
40F7  8B F7           mov si, di
40F9  D1 E7           shl di, 1
40FB  03 FE           add di, si
40FD  8A 85 E3 82     mov al, byte ptr [di - 0x7d1d]
4101  98              cwde
4102  09 C0           or ax, ax
4104  79 02           jns 0x4108
4106  F7 D8           neg ax
loc_4108:
4108  8B D0           mov dx, ax
410A  C4 7E FB        les di, ptr [bp - 5]
410D  26 8A 45 01     mov al, byte ptr es:[di + 1]
4111  98              cwde
4112  09 C0           or ax, ax
4114  79 02           jns 0x4118
4116  F7 D8           neg ax
loc_4118:
4118  3B C2           cmp ax, dx
411A  7E 25           jle 0x4141
411C  C4 7E FB        les di, ptr [bp - 5]
411F  26 8A 45 01     mov al, byte ptr es:[di + 1]
4123  98              cwde
4124  09 C0           or ax, ax
4126  79 02           jns 0x412a
4128  F7 D8           neg ax
loc_412A:
412A  3D 23 00        cmp ax, 0x23
412D  7D 12           jge 0x4141
412F  C4 7E FB        les di, ptr [bp - 5]
4132  26 8A 05        mov al, byte ptr es:[di]
4135  98              cwde
4136  09 C0           or ax, ax
4138  79 02           jns 0x413c
413A  F7 D8           neg ax
loc_413C:
413C  3D 04 00        cmp ax, 4
413F  7C 04           jl 0x4145
loc_4141:
4141  B0 00           mov al, 0
4143  EB 02           jmp 0x4147
loc_4145:
4145  B0 01           mov al, 1
loc_4147:
4147  88 46 FF        mov byte ptr [bp - 1], al
414A  8A 46 FF        mov al, byte ptr [bp - 1]
414D  89 EC           mov sp, bp
414F  5D              pop bp
4150  C3              ret

; ---- routine 0791:4151  (found by: call)
sub_4151:
4151  55              push bp
4152  89 E5           mov bp, sp
4154  83 EC 06        sub sp, 6
4157  A0 0B 83        mov al, byte ptr [0x830b]
415A  30 E4           xor ah, ah
415C  BA 16 00        mov dx, 0x16
415F  F7 E2           mul dx
4161  8B F8           mov di, ax
4163  81 C7 E8 80     add di, 0x80e8
4167  89 7E FB        mov word ptr [bp - 5], di
416A  8C 5E FD        mov word ptr [bp - 3], ds
416D  C6 46 FF 00     mov byte ptr [bp - 1], 0
4171  C4 7E FB        les di, ptr [bp - 5]
4174  26 FF 35        push word ptr es:[di]
4177  C4 7E FB        les di, ptr [bp - 5]
417A  06              push es
417B  57              push di
417C  0E              push cs
417D  E8 38 ED        call 0x2eb8
4180  08 C0           or al, al
4182  74 11           je 0x4195
4184  B8 09 00        mov ax, 9
4187  50              push ax
4188  C4 7E FB        les di, ptr [bp - 5]
418B  06              push es
418C  57              push di
418D  0E              push cs
418E  E8 1C FE        call 0x3fad
4191  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_4195:
4195  8A 46 FF        mov al, byte ptr [bp - 1]
4198  89 EC           mov sp, bp
419A  5D              pop bp
419B  C3              ret

; ---- routine 0791:419C  (found by: call)
sub_419C:
419C  55              push bp
419D  89 E5           mov bp, sp
419F  83 EC 0C        sub sp, 0xc
41A2  8A 46 FF        mov al, byte ptr [bp - 1]
41A5  98              cwde
41A6  8B F8           mov di, ax
41A8  8A 85 68 06     mov al, byte ptr [di + 0x668]
41AC  30 E4           xor ah, ah
41AE  40              inc ax
41AF  89 46 FB        mov word ptr [bp - 5], ax
41B2  C6 46 FF 00     mov byte ptr [bp - 1], 0
41B6  EB 03           jmp 0x41bb
loc_41B8:
41B8  FE 46 FF        inc byte ptr [bp - 1]
loc_41BB:
41BB  8A 46 FF        mov al, byte ptr [bp - 1]
41BE  98              cwde
41BF  8B F8           mov di, ax
41C1  8A 85 68 06     mov al, byte ptr [di + 0x668]
41C5  30 E4           xor ah, ah
41C7  05 0B 00        add ax, 0xb
41CA  89 46 F9        mov word ptr [bp - 7], ax
41CD  8A 46 FF        mov al, byte ptr [bp - 1]
41D0  98              cwde
41D1  8B F8           mov di, ax
41D3  8A 85 68 06     mov al, byte ptr [di + 0x668]
41D7  30 E4           xor ah, ah
41D9  40              inc ax
41DA  3B 46 F9        cmp ax, word ptr [bp - 7]
41DD  76 03           jbe 0x41e2
41DF  E9 DC 00        jmp 0x42be
loc_41E2:
41E2  89 46 FD        mov word ptr [bp - 3], ax
41E5  EB 03           jmp 0x41ea
loc_41E7:
41E7  FF 46 FD        inc word ptr [bp - 3]
loc_41EA:
41EA  8B 46 FD        mov ax, word ptr [bp - 3]
41ED  BA 16 00        mov dx, 0x16
41F0  F7 E2           mul dx
41F2  8B F8           mov di, ax
41F4  81 C7 E8 80     add di, 0x80e8
41F8  89 7E F5        mov word ptr [bp - 0xb], di
41FB  8C 5E F7        mov word ptr [bp - 9], ds
41FE  C4 7E F5        les di, ptr [bp - 0xb]
4201  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4205  BA 14 00        mov dx, 0x14
4208  F7 E2           mul dx
420A  C4 3E 1B A9     les di, ptr [0xa91b]
420E  03 F8           add di, ax
4210  26 8A 45 06     mov al, byte ptr es:[di + 6]
4214  30 E4           xor ah, ah
4216  8B F8           mov di, ax
4218  D1 E7           shl di, 1
421A  8B 85 9E 07     mov ax, word ptr [di + 0x79e]
421E  C4 7E F5        les di, ptr [bp - 0xb]
4221  26 89 45 09     mov word ptr es:[di + 9], ax
4225  8A 46 FF        mov al, byte ptr [bp - 1]
4228  98              cwde
4229  8B F8           mov di, ax
422B  8A 85 68 06     mov al, byte ptr [di + 0x668]
422F  30 E4           xor ah, ah
4231  40              inc ax
4232  3B 46 FD        cmp ax, word ptr [bp - 3]
4235  73 76           jae 0x42ad
4237  8B 46 FB        mov ax, word ptr [bp - 5]
423A  BA 16 00        mov dx, 0x16
423D  F7 E2           mul dx
423F  8B F8           mov di, ax
4241  8B 85 F1 80     mov ax, word ptr [di - 0x7f0f]
4245  C4 7E F5        les di, ptr [bp - 0xb]
4248  26 3B 45 09     cmp ax, word ptr es:[di + 9]
424C  75 5F           jne 0x42ad
424E  C4 7E F5        les di, ptr [bp - 0xb]
4251  26 8A 45 09     mov al, byte ptr es:[di + 9]
4255  98              cwde
4256  09 C0           or ax, ax
4258  79 02           jns 0x425c
425A  F7 D8           neg ax
loc_425C:
425C  3D 04 00        cmp ax, 4
425F  7E 35           jle 0x4296
4261  C4 7E F5        les di, ptr [bp - 0xb]
4264  26 80 7D 09 00  cmp byte ptr es:[di + 9], 0
4269  7F 04           jg 0x426f
426B  B0 00           mov al, 0
426D  EB 02           jmp 0x4271
loc_426F:
426F  B0 01           mov al, 1
loc_4271:
4271  98              cwde
4272  8B F8           mov di, ax
4274  8A 85 20 79     mov al, byte ptr [di + 0x7920]
4278  98              cwde
4279  B9 03 00        mov cx, 3
427C  F7 E9           imul cx
427E  C4 7E F5        les di, ptr [bp - 0xb]
4281  26 28 45 09     sub byte ptr es:[di + 9], al
4285  8B 46 FB        mov ax, word ptr [bp - 5]
4288  BA 16 00        mov dx, 0x16
428B  F7 E2           mul dx
428D  8B F8           mov di, ax
428F  80 AD F2 80 03  sub byte ptr [di - 0x7f0e], 3
4294  EB 17           jmp 0x42ad
loc_4296:
4296  C4 7E F5        les di, ptr [bp - 0xb]
4299  26 80 45 09 03  add byte ptr es:[di + 9], 3
429E  8B 46 FB        mov ax, word ptr [bp - 5]
42A1  BA 16 00        mov dx, 0x16
42A4  F7 E2           mul dx
42A6  8B F8           mov di, ax
42A8  80 AD F1 80 03  sub byte ptr [di - 0x7f0f], 3
loc_42AD:
42AD  8B 46 FD        mov ax, word ptr [bp - 3]
42B0  89 46 FB        mov word ptr [bp - 5], ax
42B3  8B 46 FD        mov ax, word ptr [bp - 3]
42B6  3B 46 F9        cmp ax, word ptr [bp - 7]
42B9  74 03           je 0x42be
42BB  E9 29 FF        jmp 0x41e7
loc_42BE:
42BE  80 7E FF 01     cmp byte ptr [bp - 1], 1
42C2  74 03           je 0x42c7
42C4  E9 F1 FE        jmp 0x41b8
loc_42C7:
42C7  89 EC           mov sp, bp
42C9  5D              pop bp
42CA  C3              ret

; ---- routine 0791:42CB  (found by: call)
sub_42CB:
42CB  55              push bp
42CC  89 E5           mov bp, sp
42CE  83 EC 06        sub sp, 6
42D1  C4 7E 06        les di, ptr [bp + 6]
42D4  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
42D8  BA 14 00        mov dx, 0x14
42DB  F7 E2           mul dx
42DD  C4 3E 1B A9     les di, ptr [0xa91b]
42E1  03 F8           add di, ax
42E3  89 7E FA        mov word ptr [bp - 6], di
42E6  8C 46 FC        mov word ptr [bp - 4], es
42E9  C4 7E FA        les di, ptr [bp - 6]
42EC  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
42F1  75 07           jne 0x42fa
42F3  C7 46 FE 04 00  mov word ptr [bp - 2], 4
42F8  EB 51           jmp 0x434b
loc_42FA:
42FA  C4 7E FA        les di, ptr [bp - 6]
42FD  26 80 7D 06 0B  cmp byte ptr es:[di + 6], 0xb
4302  77 22           ja 0x4326
4304  B8 01 00        mov ax, 1
4307  50              push ax
4308  C4 7E 06        les di, ptr [bp + 6]
430B  06              push es
430C  57              push di
430D  0E              push cs
430E  E8 C6 E3        call 0x26d7
4311  08 C0           or al, al
4313  74 0D           je 0x4322
4315  C4 7E 06        les di, ptr [bp + 6]
4318  06              push es
4319  57              push di
431A  0E              push cs
431B  E8 33 E8        call 0x2b51
431E  08 C0           or al, al
4320  75 04           jne 0x4326
loc_4322:
4322  B0 00           mov al, 0
4324  EB 02           jmp 0x4328
loc_4326:
4326  B0 01           mov al, 1
loc_4328:
4328  98              cwde
4329  8B D0           mov dx, ax
432B  C4 7E FA        les di, ptr [bp - 6]
432E  26 80 7D 06 04  cmp byte ptr es:[di + 6], 4
4333  77 04           ja 0x4339
4335  B0 00           mov al, 0
4337  EB 02           jmp 0x433b
loc_4339:
4339  B0 01           mov al, 1
loc_433B:
433B  98              cwde
433C  8B F8           mov di, ax
433E  D1 E7           shl di, 1
4340  03 FA           add di, dx
4342  8A 85 BA 07     mov al, byte ptr [di + 0x7ba]
4346  30 E4           xor ah, ah
4348  89 46 FE        mov word ptr [bp - 2], ax
loc_434B:
434B  8B 46 FE        mov ax, word ptr [bp - 2]
434E  89 EC           mov sp, bp
4350  5D              pop bp
4351  CA 04 00        retf 4

; ---- routine 0791:4354  (found by: call)
sub_4354:
4354  55              push bp
4355  89 E5           mov bp, sp
4357  C4 7E 06        les di, ptr [bp + 6]
435A  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
435E  BA 14 00        mov dx, 0x14
4361  F7 E2           mul dx
4363  C4 3E 1B A9     les di, ptr [0xa91b]
4367  03 F8           add di, ax
4369  26 8A 45 06     mov al, byte ptr es:[di + 6]
436D  3C 00           cmp al, 0
436F  75 0A           jne 0x437b
4371  C4 7E 06        les di, ptr [bp + 6]
4374  26 C6 45 0B 00  mov byte ptr es:[di + 0xb], 0
4379  EB 4B           jmp 0x43c6
loc_437B:
437B  3C 0D           cmp al, 0xd
437D  75 34           jne 0x43b3
437F  C4 7E 06        les di, ptr [bp + 6]
4382  26 80 7D 12 09  cmp byte ptr es:[di + 0x12], 9
4387  75 15           jne 0x439e
4389  B8 05 00        mov ax, 5
438C  50              push ax
438D  9A B1 06 4B 21  call far 214B:06B1
4392  2D 03 00        sub ax, 3
4395  C4 7E 06        les di, ptr [bp + 6]
4398  26 88 45 0B     mov byte ptr es:[di + 0xb], al
439C  EB 13           jmp 0x43b1
loc_439E:
439E  B8 0F 00        mov ax, 0xf
43A1  50              push ax
43A2  9A B1 06 4B 21  call far 214B:06B1
43A7  2D 08 00        sub ax, 8
43AA  C4 7E 06        les di, ptr [bp + 6]
43AD  26 88 45 0B     mov byte ptr es:[di + 0xb], al
loc_43B1:
43B1  EB 13           jmp 0x43c6
loc_43B3:
43B3  B8 05 00        mov ax, 5
43B6  50              push ax
43B7  9A B1 06 4B 21  call far 214B:06B1
43BC  2D 03 00        sub ax, 3
43BF  C4 7E 06        les di, ptr [bp + 6]
43C2  26 88 45 0B     mov byte ptr es:[di + 0xb], al
loc_43C6:
43C6  C4 7E 06        les di, ptr [bp + 6]
43C9  26 80 7D 0C 02  cmp byte ptr es:[di + 0xc], 2
43CE  7D 15           jge 0x43e5
43D0  C4 7E 06        les di, ptr [bp + 6]
43D3  26 8A 45 09     mov al, byte ptr es:[di + 9]
43D7  98              cwde
43D8  99              cdq
43D9  B9 02 00        mov cx, 2
43DC  F7 F9           idiv cx
43DE  C4 7E 06        les di, ptr [bp + 6]
43E1  26 28 45 0B     sub byte ptr es:[di + 0xb], al
loc_43E5:
43E5  C4 7E 06        les di, ptr [bp + 6]
43E8  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
43EC  98              cwde
43ED  8B D0           mov dx, ax
43EF  C4 7E 06        les di, ptr [bp + 6]
43F2  26 8A 45 0A     mov al, byte ptr es:[di + 0xa]
43F6  98              cwde
43F7  03 C2           add ax, dx
43F9  C4 7E 06        les di, ptr [bp + 6]
43FC  26 88 45 08     mov byte ptr es:[di + 8], al
4400  C4 7E 06        les di, ptr [bp + 6]
4403  26 8A 45 0B     mov al, byte ptr es:[di + 0xb]
4407  98              cwde
4408  8B D0           mov dx, ax
440A  C4 7E 06        les di, ptr [bp + 6]
440D  26 8A 45 09     mov al, byte ptr es:[di + 9]
4411  98              cwde
4412  03 C2           add ax, dx
4414  C4 7E 06        les di, ptr [bp + 6]
4417  26 88 45 07     mov byte ptr es:[di + 7], al
441B  C4 7E 06        les di, ptr [bp + 6]
441E  26 FF 75 07     push word ptr es:[di + 7]
4422  C4 7E 06        les di, ptr [bp + 6]
4425  06              push es
4426  57              push di
4427  0E              push cs
4428  E8 5B E8        call 0x2c86
442B  C4 7E 06        les di, ptr [bp + 6]
442E  26 89 45 07     mov word ptr es:[di + 7], ax
4432  89 EC           mov sp, bp
4434  5D              pop bp
4435  CA 04 00        retf 4

; ---- routine 0791:4438  (found by: call)
sub_4438:
4438  55              push bp
4439  89 E5           mov bp, sp
443B  83 EC 04        sub sp, 4
443E  C4 7E 06        les di, ptr [bp + 6]
4441  26 8B 45 09     mov ax, word ptr es:[di + 9]
4445  89 46 FD        mov word ptr [bp - 3], ax
4448  C4 7E 06        les di, ptr [bp + 6]
444B  26 80 7D 12 09  cmp byte ptr es:[di + 0x12], 9
4450  74 21           je 0x4473
4452  C4 7E 06        les di, ptr [bp + 6]
4455  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4459  BA 14 00        mov dx, 0x14
445C  F7 E2           mul dx
445E  C4 3E 1B A9     les di, ptr [0xa91b]
4462  03 F8           add di, ax
4464  26 8A 45 06     mov al, byte ptr es:[di + 6]
4468  30 E4           xor ah, ah
446A  8B F8           mov di, ax
446C  8A 85 BE 07     mov al, byte ptr [di + 0x7be]
4470  00 46 FE        add byte ptr [bp - 2], al
loc_4473:
4473  8A 46 FD        mov al, byte ptr [bp - 3]
4476  98              cwde
4477  8B D0           mov dx, ax
4479  8A 46 0A        mov al, byte ptr [bp + 0xa]
447C  98              cwde
447D  2B C2           sub ax, dx
447F  09 C0           or ax, ax
4481  79 02           jns 0x4485
4483  F7 D8           neg ax
loc_4485:
4485  3D 04 00        cmp ax, 4
4488  7D 25           jge 0x44af
448A  C4 7E 06        les di, ptr [bp + 6]
448D  06              push es
448E  57              push di
448F  0E              push cs
4490  E8 52 E7        call 0x2be5
4493  98              cwde
4494  8B D0           mov dx, ax
4496  8A 46 FE        mov al, byte ptr [bp - 2]
4499  98              cwde
449A  F7 EA           imul dx
449C  8B D0           mov dx, ax
449E  8A 46 0B        mov al, byte ptr [bp + 0xb]
44A1  98              cwde
44A2  2B C2           sub ax, dx
44A4  09 C0           or ax, ax
44A6  79 02           jns 0x44aa
44A8  F7 D8           neg ax
loc_44AA:
44AA  3D 09 00        cmp ax, 9
44AD  7C 04           jl 0x44b3
loc_44AF:
44AF  B0 00           mov al, 0
44B1  EB 02           jmp 0x44b5
loc_44B3:
44B3  B0 01           mov al, 1
loc_44B5:
44B5  88 46 FF        mov byte ptr [bp - 1], al
44B8  8A 46 FF        mov al, byte ptr [bp - 1]
44BB  89 EC           mov sp, bp
44BD  5D              pop bp
44BE  CA 06 00        retf 6

; ---- routine 0791:44C1  (found by: call)
sub_44C1:
44C1  55              push bp
44C2  89 E5           mov bp, sp
44C4  83 EC 02        sub sp, 2
44C7  C4 7E 06        les di, ptr [bp + 6]
44CA  26 80 7D 12 0D  cmp byte ptr es:[di + 0x12], 0xd
44CF  74 4F           je 0x4520
44D1  A0 0B 83        mov al, byte ptr [0x830b]
44D4  C4 7E 06        les di, ptr [bp + 6]
44D7  26 3A 45 06     cmp al, byte ptr es:[di + 6]
44DB  74 43           je 0x4520
44DD  C4 7E 06        les di, ptr [bp + 6]
44E0  26 8A 05        mov al, byte ptr es:[di]
44E3  98              cwde
44E4  8B D0           mov dx, ax
44E6  8A 46 0A        mov al, byte ptr [bp + 0xa]
44E9  98              cwde
44EA  2B C2           sub ax, dx
44EC  09 C0           or ax, ax
44EE  79 02           jns 0x44f2
44F0  F7 D8           neg ax
loc_44F2:
44F2  3D 04 00        cmp ax, 4
44F5  7D 29           jge 0x4520
44F7  C4 7E 06        les di, ptr [bp + 6]
44FA  06              push es
44FB  57              push di
44FC  0E              push cs
44FD  E8 E5 E6        call 0x2be5
4500  98              cwde
4501  8B D0           mov dx, ax
4503  C4 7E 06        les di, ptr [bp + 6]
4506  26 8A 45 01     mov al, byte ptr es:[di + 1]
450A  98              cwde
450B  F7 EA           imul dx
450D  8B D0           mov dx, ax
450F  8A 46 0B        mov al, byte ptr [bp + 0xb]
4512  98              cwde
4513  2B C2           sub ax, dx
4515  09 C0           or ax, ax
4517  79 02           jns 0x451b
4519  F7 D8           neg ax
loc_451B:
451B  3D 06 00        cmp ax, 6
451E  7C 04           jl 0x4524
loc_4520:
4520  B0 00           mov al, 0
4522  EB 02           jmp 0x4526
loc_4524:
4524  B0 01           mov al, 1
loc_4526:
4526  88 46 FF        mov byte ptr [bp - 1], al
4529  8A 46 FF        mov al, byte ptr [bp - 1]
452C  89 EC           mov sp, bp
452E  5D              pop bp
452F  CA 06 00        retf 6

; ---- routine 0791:4532  (found by: call)
sub_4532:
4532  55              push bp
4533  89 E5           mov bp, sp
4535  83 EC 02        sub sp, 2
4538  C6 46 FF 00     mov byte ptr [bp - 1], 0
453C  8B 7E 04        mov di, word ptr [bp + 4]
453F  36 C4 7D 06     les di, ptr ss:[di + 6]
4543  06              push es
4544  57              push di
4545  0E              push cs
4546  E8 82 FD        call 0x42cb
4549  50              push ax
454A  B8 07 00        mov ax, 7
454D  50              push ax
454E  8B 7E 04        mov di, word ptr [bp + 4]
4551  36 C4 7D 06     les di, ptr ss:[di + 6]
4555  06              push es
4556  57              push di
4557  0E              push cs
4558  E8 7C E1        call 0x26d7
455B  98              cwde
455C  8B F8           mov di, ax
455E  D1 E7           shl di, 1
4560  D1 E7           shl di, 1
4562  58              pop ax
4563  03 F8           add di, ax
4565  8A 85 DB 07     mov al, byte ptr [di + 0x7db]
4569  30 E4           xor ah, ah
456B  8B D0           mov dx, ax
456D  8B 7E 04        mov di, word ptr [bp + 4]
4570  36 C4 7D 06     les di, ptr ss:[di + 6]
4574  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
4578  98              cwde
4579  3B C2           cmp ax, dx
457B  7C 03           jl 0x4580
457D  E9 C0 00        jmp 0x4640
loc_4580:
4580  8B 7E 04        mov di, word ptr [bp + 4]
4583  36 C4 7D 06     les di, ptr ss:[di + 6]
4587  06              push es
4588  57              push di
4589  0E              push cs
458A  E8 3E FD        call 0x42cb
458D  3D 01 00        cmp ax, 1
4590  75 3D           jne 0x45cf
4592  31 C0           xor ax, ax
4594  50              push ax
4595  8B 7E 04        mov di, word ptr [bp + 4]
4598  36 C4 7D 06     les di, ptr ss:[di + 6]
459C  06              push es
459D  57              push di
459E  0E              push cs
459F  E8 6E E7        call 0x2d10
45A2  08 C0           or al, al
45A4  75 22           jne 0x45c8
45A6  B8 01 00        mov ax, 1
45A9  50              push ax
45AA  8B 7E 04        mov di, word ptr [bp + 4]
45AD  36 C4 7D 06     les di, ptr ss:[di + 6]
45B1  06              push es
45B2  57              push di
45B3  0E              push cs
45B4  E8 20 E1        call 0x26d7
45B7  08 C0           or al, al
45B9  75 0D           jne 0x45c8
45BB  9A FA 06 4B 21  call far 214B:06FA
45C0  08 C0           or al, al
45C2  75 04           jne 0x45c8
45C4  B0 00           mov al, 0
45C6  EB 02           jmp 0x45ca
loc_45C8:
45C8  B0 01           mov al, 1
loc_45CA:
45CA  88 46 FF        mov byte ptr [bp - 1], al
45CD  EB 71           jmp 0x4640
loc_45CF:
45CF  3D 02 00        cmp ax, 2
45D2  75 34           jne 0x4608
45D4  31 C0           xor ax, ax
45D6  50              push ax
45D7  8B 7E 04        mov di, word ptr [bp + 4]
45DA  36 C4 7D 06     les di, ptr ss:[di + 6]
45DE  06              push es
45DF  57              push di
45E0  0E              push cs
45E1  E8 2C E7        call 0x2d10
45E4  08 C0           or al, al
45E6  75 19           jne 0x4601
45E8  B8 01 00        mov ax, 1
45EB  50              push ax
45EC  8B 7E 04        mov di, word ptr [bp + 4]
45EF  36 C4 7D 06     les di, ptr ss:[di + 6]
45F3  06              push es
45F4  57              push di
45F5  0E              push cs
45F6  E8 DE E0        call 0x26d7
45F9  08 C0           or al, al
45FB  75 04           jne 0x4601
45FD  B0 00           mov al, 0
45FF  EB 02           jmp 0x4603
loc_4601:
4601  B0 01           mov al, 1
loc_4603:
4603  88 46 FF        mov byte ptr [bp - 1], al
4606  EB 38           jmp 0x4640
loc_4608:
4608  3D 03 00        cmp ax, 3
460B  75 33           jne 0x4640
460D  B8 1E 00        mov ax, 0x1e
4610  50              push ax
4611  8B 7E 04        mov di, word ptr [bp + 4]
4614  36 C4 7D 06     les di, ptr ss:[di + 6]
4618  06              push es
4619  57              push di
461A  0E              push cs
461B  E8 F2 E6        call 0x2d10
461E  08 C0           or al, al
4620  75 19           jne 0x463b
4622  B8 07 00        mov ax, 7
4625  50              push ax
4626  8B 7E 04        mov di, word ptr [bp + 4]
4629  36 C4 7D 06     les di, ptr ss:[di + 6]
462D  06              push es
462E  57              push di
462F  0E              push cs
4630  E8 A4 E0        call 0x26d7
4633  08 C0           or al, al
4635  75 04           jne 0x463b
4637  B0 00           mov al, 0
4639  EB 02           jmp 0x463d
loc_463B:
463B  B0 01           mov al, 1
loc_463D:
463D  88 46 FF        mov byte ptr [bp - 1], al
loc_4640:
4640  8A 46 FF        mov al, byte ptr [bp - 1]
4643  89 EC           mov sp, bp
4645  5D              pop bp
4646  C2 02 00        ret 2

