; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 10 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:6B55  (found by: call)
sub_6B55:
6B55  55              push bp
6B56  89 E5           mov bp, sp
6B58  83 EC 1A        sub sp, 0x1a
6B5B  C4 3E 23 A9     les di, ptr [0xa923]
6B5F  89 7E EE        mov word ptr [bp - 0x12], di
6B62  8C 46 F0        mov word ptr [bp - 0x10], es
6B65  31 C0           xor ax, ax
6B67  50              push ax
6B68  E8 2E F3        call 0x5e99
6B6B  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6B70  EB 03           jmp 0x6b75
loc_6B72:
6B72  FF 46 FE        inc word ptr [bp - 2]
loc_6B75:
6B75  B8 08 00        mov ax, 8
6B78  50              push ax
6B79  9A B1 06 4B 21  call far 214B:06B1
6B7E  BA 38 00        mov dx, 0x38
6B81  F7 E2           mul dx
6B83  8B C8           mov cx, ax
6B85  8B 46 FE        mov ax, word ptr [bp - 2]
6B88  BA C0 01        mov dx, 0x1c0
6B8B  F7 E2           mul dx
6B8D  C4 3E 33 A9     les di, ptr [0xa933]
6B91  03 F8           add di, ax
6B93  03 F9           add di, cx
6B95  26 8B 95 08 FE  mov dx, word ptr es:[di - 0x1f8]
6B9A  8B 46 FE        mov ax, word ptr [bp - 2]
6B9D  D1 E0           shl ax, 1
6B9F  C4 7E EE        les di, ptr [bp - 0x12]
6BA2  03 F8           add di, ax
6BA4  26 89 55 2C     mov word ptr es:[di + 0x2c], dx
6BA8  C7 46 FA 01 00  mov word ptr [bp - 6], 1
6BAD  EB 03           jmp 0x6bb2
loc_6BAF:
6BAF  FF 46 FA        inc word ptr [bp - 6]
loc_6BB2:
6BB2  B8 04 00        mov ax, 4
6BB5  50              push ax
6BB6  9A B1 06 4B 21  call far 214B:06B1
6BBB  89 46 F6        mov word ptr [bp - 0xa], ax
6BBE  C7 46 F8 01 00  mov word ptr [bp - 8], 1
6BC3  EB 03           jmp 0x6bc8
loc_6BC5:
6BC5  FF 46 F8        inc word ptr [bp - 8]
loc_6BC8:
6BC8  8B 46 F8        mov ax, word ptr [bp - 8]
6BCB  8B 7E F6        mov di, word ptr [bp - 0xa]
6BCE  D1 E7           shl di, 1
6BD0  D1 E7           shl di, 1
6BD2  03 F8           add di, ax
6BD4  8A 85 71 0F     mov al, byte ptr [di + 0xf71]
6BD8  30 E4           xor ah, ah
6BDA  B1 03           mov cl, 3
6BDC  D3 E0           shl ax, cl
6BDE  8B D8           mov bx, ax
6BE0  8B 46 FA        mov ax, word ptr [bp - 6]
6BE3  BA 38 00        mov dx, 0x38
6BE6  F7 E2           mul dx
6BE8  8B C8           mov cx, ax
6BEA  8B 46 FE        mov ax, word ptr [bp - 2]
6BED  BA C0 01        mov dx, 0x1c0
6BF0  F7 E2           mul dx
6BF2  C4 3E 33 A9     les di, ptr [0xa933]
6BF6  03 F8           add di, ax
6BF8  03 F9           add di, cx
6BFA  03 FB           add di, bx
6BFC  81 C7 00 05     add di, 0x500
6C00  89 7E EA        mov word ptr [bp - 0x16], di
6C03  8C 46 EC        mov word ptr [bp - 0x14], es
6C06  8B 46 FA        mov ax, word ptr [bp - 6]
6C09  40              inc ax
6C0A  31 D2           xor dx, dx
6C0C  B9 02 00        mov cx, 2
6C0F  F7 F1           div cx
6C11  B1 03           mov cl, 3
6C13  D3 E0           shl ax, cl
6C15  8B D8           mov bx, ax
6C17  8A 46 FA        mov al, byte ptr [bp - 6]
6C1A  D0 E8           shr al, 1
6C1C  72 04           jb 0x6c22
6C1E  B0 00           mov al, 0
6C20  EB 02           jmp 0x6c24
loc_6C22:
6C22  B0 01           mov al, 1
loc_6C24:
6C24  98              cwde
6C25  8B D0           mov dx, ax
6C27  8B 46 F8        mov ax, word ptr [bp - 8]
6C2A  D1 E0           shl ax, 1
6C2C  2B C2           sub ax, dx
6C2E  BA 38 00        mov dx, 0x38
6C31  F7 E2           mul dx
6C33  8B C8           mov cx, ax
6C35  8B 46 FE        mov ax, word ptr [bp - 2]
6C38  BA C0 01        mov dx, 0x1c0
6C3B  F7 E2           mul dx
6C3D  C4 3E 33 A9     les di, ptr [0xa933]
6C41  03 F8           add di, ax
6C43  03 F9           add di, cx
6C45  03 FB           add di, bx
6C47  26 8B 85 00 FE  mov ax, word ptr es:[di - 0x200]
6C4C  C4 7E EA        les di, ptr [bp - 0x16]
6C4F  26 89 05        mov word ptr es:[di], ax
6C52  C4 7E EA        les di, ptr [bp - 0x16]
6C55  26 8B 05        mov ax, word ptr es:[di]
6C58  BA BF 00        mov dx, 0xbf
6C5B  F7 E2           mul dx
6C5D  C4 3E 17 A9     les di, ptr [0xa917]
6C61  03 F8           add di, ax
6C63  89 7E E6        mov word ptr [bp - 0x1a], di
6C66  8C 46 E8        mov word ptr [bp - 0x18], es
6C69  C4 7E E6        les di, ptr [bp - 0x1a]
6C6C  26 80 7D 2E 80  cmp byte ptr es:[di + 0x2e], 0x80
6C71  76 1E           jbe 0x6c91
6C73  83 7E FA 03     cmp word ptr [bp - 6], 3
6C77  73 18           jae 0x6c91
6C79  8A 56 FA        mov dl, byte ptr [bp - 6]
6C7C  C4 7E E6        les di, ptr [bp - 0x1a]
6C7F  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
6C83  30 E4           xor ah, ah
6C85  2D 80 00        sub ax, 0x80
6C88  C4 7E EE        les di, ptr [bp - 0x12]
6C8B  03 F8           add di, ax
6C8D  26 88 55 01     mov byte ptr es:[di + 1], dl
loc_6C91:
6C91  83 7E F8 04     cmp word ptr [bp - 8], 4
6C95  74 03           je 0x6c9a
6C97  E9 2B FF        jmp 0x6bc5
loc_6C9A:
6C9A  83 7E FA 08     cmp word ptr [bp - 6], 8
6C9E  74 03           je 0x6ca3
6CA0  E9 0C FF        jmp 0x6baf
loc_6CA3:
6CA3  83 7E FE 04     cmp word ptr [bp - 2], 4
6CA7  74 03           je 0x6cac
6CA9  E9 C6 FE        jmp 0x6b72
loc_6CAC:
6CAC  C7 46 F4 01 00  mov word ptr [bp - 0xc], 1
6CB1  EB 03           jmp 0x6cb6
loc_6CB3:
6CB3  FF 46 F4        inc word ptr [bp - 0xc]
loc_6CB6:
6CB6  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6CBB  EB 03           jmp 0x6cc0
loc_6CBD:
6CBD  FF 46 FE        inc word ptr [bp - 2]
loc_6CC0:
6CC0  C7 46 FC 01 00  mov word ptr [bp - 4], 1
6CC5  EB 03           jmp 0x6cca
loc_6CC7:
6CC7  FF 46 FC        inc word ptr [bp - 4]
loc_6CCA:
6CCA  8B 46 FC        mov ax, word ptr [bp - 4]
6CCD  BA 38 00        mov dx, 0x38
6CD0  F7 E2           mul dx
6CD2  8B C8           mov cx, ax
6CD4  8B 46 FE        mov ax, word ptr [bp - 2]
6CD7  BA C0 01        mov dx, 0x1c0
6CDA  F7 E2           mul dx
6CDC  C4 3E 33 A9     les di, ptr [0xa933]
6CE0  03 F8           add di, ax
6CE2  03 F9           add di, cx
6CE4  81 C7 08 05     add di, 0x508
6CE8  89 7E EA        mov word ptr [bp - 0x16], di
6CEB  8C 46 EC        mov word ptr [bp - 0x14], es
6CEE  83 7E F4 07     cmp word ptr [bp - 0xc], 7
6CF2  72 03           jb 0x6cf7
6CF4  E9 7E 00        jmp 0x6d75
loc_6CF7:
6CF7  8B 46 F4        mov ax, word ptr [bp - 0xc]
6CFA  8B 7E FC        mov di, word ptr [bp - 4]
6CFD  D1 E7           shl di, 1
6CFF  8B F7           mov si, di
6D01  D1 E7           shl di, 1
6D03  03 FE           add di, si
6D05  03 F8           add di, ax
6D07  80 BD 87 10 00  cmp byte ptr [di + 0x1087], 0
6D0C  76 67           jbe 0x6d75
6D0E  C7 46 F8 01 00  mov word ptr [bp - 8], 1
6D13  EB 03           jmp 0x6d18
loc_6D15:
6D15  FF 46 F8        inc word ptr [bp - 8]
loc_6D18:
6D18  8B 46 F8        mov ax, word ptr [bp - 8]
6D1B  B1 03           mov cl, 3
6D1D  D3 E0           shl ax, cl
6D1F  C4 7E EA        les di, ptr [bp - 0x16]
6D22  03 F8           add di, ax
6D24  26 FF 75 F8     push word ptr es:[di - 8]
6D28  8B 46 F8        mov ax, word ptr [bp - 8]
6D2B  B1 03           mov cl, 3
6D2D  D3 E0           shl ax, cl
6D2F  8B D8           mov bx, ax
6D31  8B 46 F4        mov ax, word ptr [bp - 0xc]
6D34  8B 7E FC        mov di, word ptr [bp - 4]
6D37  D1 E7           shl di, 1
6D39  8B F7           mov si, di
6D3B  D1 E7           shl di, 1
6D3D  03 FE           add di, si
6D3F  03 F8           add di, ax
6D41  8A 85 87 10     mov al, byte ptr [di + 0x1087]
6D45  30 E4           xor ah, ah
6D47  BA 38 00        mov dx, 0x38
6D4A  F7 E2           mul dx
6D4C  8B C8           mov cx, ax
6D4E  8B 46 FE        mov ax, word ptr [bp - 2]
6D51  BA C0 01        mov dx, 0x1c0
6D54  F7 E2           mul dx
6D56  C4 3E 33 A9     les di, ptr [0xa933]
6D5A  03 F8           add di, ax
6D5C  03 F9           add di, cx
6D5E  03 FB           add di, bx
6D60  26 FF B5 00 05  push word ptr es:[di + 0x500]
6D65  B8 01 00        mov ax, 1
6D68  50              push ax
6D69  31 C0           xor ax, ax
6D6B  50              push ax
6D6C  E8 25 F0        call 0x5d94
6D6F  83 7E F8 04     cmp word ptr [bp - 8], 4
6D73  75 A0           jne 0x6d15
loc_6D75:
6D75  83 7E F4 06     cmp word ptr [bp - 0xc], 6
6D79  77 03           ja 0x6d7e
6D7B  E9 B6 00        jmp 0x6e34
loc_6D7E:
6D7E  83 7E FC 03     cmp word ptr [bp - 4], 3
6D82  73 6C           jae 0x6df0
6D84  C4 7E EE        les di, ptr [bp - 0x12]
6D87  26 8B 55 28     mov dx, word ptr es:[di + 0x28]
6D8B  8B 46 F4        mov ax, word ptr [bp - 0xc]
6D8E  2D 06 00        sub ax, 6
6D91  D1 E0           shl ax, 1
6D93  C4 7E EA        les di, ptr [bp - 0x16]
6D96  03 F8           add di, ax
6D98  26 89 55 1E     mov word ptr es:[di + 0x1e], dx
6D9C  8B 46 F4        mov ax, word ptr [bp - 0xc]
6D9F  2D 06 00        sub ax, 6
6DA2  8B F8           mov di, ax
6DA4  D1 E7           shl di, 1
6DA6  8A 85 BD 10     mov al, byte ptr [di + 0x10bd]
6DAA  30 E4           xor ah, ah
6DAC  B1 03           mov cl, 3
6DAE  D3 E0           shl ax, cl
6DB0  C4 7E EA        les di, ptr [bp - 0x16]
6DB3  03 F8           add di, ax
6DB5  26 FF 75 F8     push word ptr es:[di - 8]
6DB9  8B 46 F4        mov ax, word ptr [bp - 0xc]
6DBC  2D 06 00        sub ax, 6
6DBF  8B F8           mov di, ax
6DC1  D1 E7           shl di, 1
6DC3  8A 85 BC 10     mov al, byte ptr [di + 0x10bc]
6DC7  30 E4           xor ah, ah
6DC9  B1 03           mov cl, 3
6DCB  D3 E0           shl ax, cl
6DCD  C4 7E EA        les di, ptr [bp - 0x16]
6DD0  03 F8           add di, ax
6DD2  26 FF 75 F8     push word ptr es:[di - 8]
6DD6  B8 03 00        mov ax, 3
6DD9  50              push ax
6DDA  FF 76 FC        push word ptr [bp - 4]
6DDD  8B 46 FE        mov ax, word ptr [bp - 2]
6DE0  D1 E0           shl ax, 1
6DE2  C4 7E EE        les di, ptr [bp - 0x12]
6DE5  03 F8           add di, ax
6DE7  26 FF 75 2C     push word ptr es:[di + 0x2c]
6DEB  E8 4C F0        call 0x5e3a
6DEE  EB 44           jmp 0x6e34
loc_6DF0:
6DF0  8B 46 F4        mov ax, word ptr [bp - 0xc]
6DF3  2D 06 00        sub ax, 6
6DF6  8B F8           mov di, ax
6DF8  D1 E7           shl di, 1
6DFA  8A 85 BD 10     mov al, byte ptr [di + 0x10bd]
6DFE  30 E4           xor ah, ah
6E00  B1 03           mov cl, 3
6E02  D3 E0           shl ax, cl
6E04  C4 7E EA        les di, ptr [bp - 0x16]
6E07  03 F8           add di, ax
6E09  26 FF 75 F8     push word ptr es:[di - 8]
6E0D  8B 46 F4        mov ax, word ptr [bp - 0xc]
6E10  2D 06 00        sub ax, 6
6E13  8B F8           mov di, ax
6E15  D1 E7           shl di, 1
6E17  8A 85 BC 10     mov al, byte ptr [di + 0x10bc]
6E1B  30 E4           xor ah, ah
6E1D  B1 03           mov cl, 3
6E1F  D3 E0           shl ax, cl
6E21  C4 7E EA        les di, ptr [bp - 0x16]
6E24  03 F8           add di, ax
6E26  26 FF 75 F8     push word ptr es:[di - 8]
6E2A  B8 01 00        mov ax, 1
6E2D  50              push ax
6E2E  31 C0           xor ax, ax
6E30  50              push ax
6E31  E8 60 EF        call 0x5d94
loc_6E34:
6E34  83 7E FC 08     cmp word ptr [bp - 4], 8
6E38  74 03           je 0x6e3d
6E3A  E9 8A FE        jmp 0x6cc7
loc_6E3D:
6E3D  83 7E FE 04     cmp word ptr [bp - 2], 4
6E41  74 03           je 0x6e46
6E43  E9 77 FE        jmp 0x6cbd
loc_6E46:
6E46  83 7E F4 0C     cmp word ptr [bp - 0xc], 0xc
6E4A  74 03           je 0x6e4f
6E4C  E9 64 FE        jmp 0x6cb3
loc_6E4F:
6E4F  B0 01           mov al, 1
6E51  50              push ax
6E52  E8 C2 F7        call 0x6617
6E55  89 EC           mov sp, bp
6E57  5D              pop bp
6E58  C3              ret

; ---- routine 1771:6E59  (found by: call)
sub_6E59:
6E59  55              push bp
6E5A  89 E5           mov bp, sp
6E5C  83 EC 0A        sub sp, 0xa
6E5F  C4 3E 23 A9     les di, ptr [0xa923]
6E63  89 7E FA        mov word ptr [bp - 6], di
6E66  8C 46 FC        mov word ptr [bp - 4], es
6E69  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6E6E  EB 03           jmp 0x6e73
loc_6E70:
6E70  FF 46 FE        inc word ptr [bp - 2]
loc_6E73:
6E73  8B 46 FE        mov ax, word ptr [bp - 2]
6E76  BA C0 01        mov dx, 0x1c0
6E79  F7 E2           mul dx
6E7B  C4 3E 33 A9     les di, ptr [0xa933]
6E7F  03 F8           add di, ax
6E81  81 C7 40 05     add di, 0x540
6E85  89 7E F6        mov word ptr [bp - 0xa], di
6E88  8C 46 F8        mov word ptr [bp - 8], es
6E8B  C4 7E FA        les di, ptr [bp - 6]
6E8E  26 8A 45 3D     mov al, byte ptr es:[di + 0x3d]
6E92  3C 02           cmp al, 2
6E94  74 03           je 0x6e99
6E96  E9 82 00        jmp 0x6f1b
loc_6E99:
6E99  C4 7E FA        les di, ptr [bp - 6]
6E9C  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
6EA0  C4 7E F6        les di, ptr [bp - 0xa]
6EA3  26 89 45 2C     mov word ptr es:[di + 0x2c], ax
6EA7  C4 7E F6        les di, ptr [bp - 0xa]
6EAA  26 FF 35        push word ptr es:[di]
6EAD  8B 46 FE        mov ax, word ptr [bp - 2]
6EB0  BA C0 01        mov dx, 0x1c0
6EB3  F7 E2           mul dx
6EB5  C4 3E 33 A9     les di, ptr [0xa933]
6EB9  03 F8           add di, ax
6EBB  26 FF B5 80 05  push word ptr es:[di + 0x580]
6EC0  B8 65 00        mov ax, 0x65
6EC3  50              push ax
6EC4  31 C0           xor ax, ax
6EC6  50              push ax
6EC7  8B 46 FE        mov ax, word ptr [bp - 2]
6ECA  D1 E0           shl ax, 1
6ECC  C4 7E FA        les di, ptr [bp - 6]
6ECF  03 F8           add di, ax
6ED1  26 FF 75 2C     push word ptr es:[di + 0x2c]
6ED5  E8 62 EF        call 0x5e3a
6ED8  C4 7E FA        les di, ptr [bp - 6]
6EDB  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
6EDF  C4 7E F6        les di, ptr [bp - 0xa]
6EE2  26 89 45 2E     mov word ptr es:[di + 0x2e], ax
6EE6  8B 46 FE        mov ax, word ptr [bp - 2]
6EE9  BA C0 01        mov dx, 0x1c0
6EEC  F7 E2           mul dx
6EEE  C4 3E 33 A9     les di, ptr [0xa933]
6EF2  03 F8           add di, ax
6EF4  26 FF B5 78 05  push word ptr es:[di + 0x578]
6EF9  C4 7E F6        les di, ptr [bp - 0xa]
6EFC  26 FF 75 08     push word ptr es:[di + 8]
6F00  B8 65 00        mov ax, 0x65
6F03  50              push ax
6F04  31 C0           xor ax, ax
6F06  50              push ax
6F07  8B 46 FE        mov ax, word ptr [bp - 2]
6F0A  D1 E0           shl ax, 1
6F0C  C4 7E FA        les di, ptr [bp - 6]
6F0F  03 F8           add di, ax
6F11  26 FF 75 2C     push word ptr es:[di + 0x2c]
6F15  E8 22 EF        call 0x5e3a
6F18  E9 C3 00        jmp 0x6fde
loc_6F1B:
6F1B  3C 01           cmp al, 1
6F1D  74 03           je 0x6f22
6F1F  E9 BC 00        jmp 0x6fde
loc_6F22:
6F22  C4 7E FA        les di, ptr [bp - 6]
6F25  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
6F29  C4 7E F6        les di, ptr [bp - 0xa]
6F2C  26 89 45 30     mov word ptr es:[di + 0x30], ax
6F30  C4 7E F6        les di, ptr [bp - 0xa]
6F33  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
6F37  B1 03           mov cl, 3
6F39  D3 E0           shl ax, cl
6F3B  C4 3E 2B A9     les di, ptr [0xa92b]
6F3F  03 F8           add di, ax
6F41  81 C7 F8 FF     add di, 0xfff8
6F45  06              push es
6F46  57              push di
6F47  0E              push cs
6F48  E8 80 ED        call 0x5ccb
6F4B  50              push ax
6F4C  C4 7E F6        les di, ptr [bp - 0xa]
6F4F  26 8B 45 2E     mov ax, word ptr es:[di + 0x2e]
6F53  B1 03           mov cl, 3
6F55  D3 E0           shl ax, cl
6F57  C4 3E 2B A9     les di, ptr [0xa92b]
6F5B  03 F8           add di, ax
6F5D  81 C7 F8 FF     add di, 0xfff8
6F61  06              push es
6F62  57              push di
6F63  0E              push cs
6F64  E8 64 ED        call 0x5ccb
6F67  50              push ax
6F68  B8 66 00        mov ax, 0x66
6F6B  50              push ax
6F6C  31 C0           xor ax, ax
6F6E  50              push ax
6F6F  8B 46 FE        mov ax, word ptr [bp - 2]
6F72  D1 E0           shl ax, 1
6F74  C4 7E FA        les di, ptr [bp - 6]
6F77  03 F8           add di, ax
6F79  26 FF 75 2C     push word ptr es:[di + 0x2c]
6F7D  E8 BA EE        call 0x5e3a
6F80  C4 7E FA        les di, ptr [bp - 6]
6F83  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
6F87  C4 7E F6        les di, ptr [bp - 0xa]
6F8A  26 89 45 32     mov word ptr es:[di + 0x32], ax
6F8E  C4 7E F6        les di, ptr [bp - 0xa]
6F91  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
6F95  B1 03           mov cl, 3
6F97  D3 E0           shl ax, cl
6F99  C4 3E 2B A9     les di, ptr [0xa92b]
6F9D  03 F8           add di, ax
6F9F  81 C7 F8 FF     add di, 0xfff8
6FA3  06              push es
6FA4  57              push di
6FA5  0E              push cs
6FA6  E8 EB EC        call 0x5c94
6FA9  50              push ax
6FAA  C4 7E F6        les di, ptr [bp - 0xa]
6FAD  26 8B 45 2E     mov ax, word ptr es:[di + 0x2e]
6FB1  B1 03           mov cl, 3
6FB3  D3 E0           shl ax, cl
6FB5  C4 3E 2B A9     les di, ptr [0xa92b]
6FB9  03 F8           add di, ax
6FBB  81 C7 F8 FF     add di, 0xfff8
6FBF  06              push es
6FC0  57              push di
6FC1  0E              push cs
6FC2  E8 CF EC        call 0x5c94
6FC5  50              push ax
6FC6  B8 67 00        mov ax, 0x67
6FC9  50              push ax
6FCA  31 C0           xor ax, ax
6FCC  50              push ax
6FCD  8B 46 FE        mov ax, word ptr [bp - 2]
6FD0  D1 E0           shl ax, 1
6FD2  C4 7E FA        les di, ptr [bp - 6]
6FD5  03 F8           add di, ax
6FD7  26 FF 75 2C     push word ptr es:[di + 0x2c]
6FDB  E8 5C EE        call 0x5e3a
loc_6FDE:
6FDE  83 7E FE 04     cmp word ptr [bp - 2], 4
6FE2  74 03           je 0x6fe7
6FE4  E9 89 FE        jmp 0x6e70
loc_6FE7:
6FE7  89 EC           mov sp, bp
6FE9  5D              pop bp
6FEA  C3              ret

; ---- routine 1771:6FEB  (found by: call)
sub_6FEB:
6FEB  55              push bp
6FEC  89 E5           mov bp, sp
6FEE  83 EC 0C        sub sp, 0xc
6FF1  C4 3E 23 A9     les di, ptr [0xa923]
6FF5  89 7E FA        mov word ptr [bp - 6], di
6FF8  8C 46 FC        mov word ptr [bp - 4], es
6FFB  C4 7E FA        les di, ptr [bp - 6]
6FFE  26 8A 05        mov al, byte ptr es:[di]
7001  30 E4           xor ah, ah
7003  89 46 F8        mov word ptr [bp - 8], ax
7006  B8 01 00        mov ax, 1
7009  3B 46 F8        cmp ax, word ptr [bp - 8]
700C  77 7C           ja 0x708a
700E  89 46 FE        mov word ptr [bp - 2], ax
7011  EB 03           jmp 0x7016
loc_7013:
7013  FF 46 FE        inc word ptr [bp - 2]
loc_7016:
7016  8B 46 FE        mov ax, word ptr [bp - 2]
7019  05 80 00        add ax, 0x80
701C  BA 03 00        mov dx, 3
701F  F7 E2           mul dx
7021  C4 3E 1F A9     les di, ptr [0xa91f]
7025  03 F8           add di, ax
7027  26 8A 05        mov al, byte ptr es:[di]
702A  30 E4           xor ah, ah
702C  BA BF 00        mov dx, 0xbf
702F  F7 E2           mul dx
7031  C4 3E 17 A9     les di, ptr [0xa917]
7035  03 F8           add di, ax
7037  89 7E F4        mov word ptr [bp - 0xc], di
703A  8C 46 F6        mov word ptr [bp - 0xa], es
703D  C4 7E FA        les di, ptr [bp - 6]
7040  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
7044  48              dec ax
7045  B1 03           mov cl, 3
7047  D3 E0           shl ax, cl
7049  C4 3E 2B A9     les di, ptr [0xa92b]
704D  03 F8           add di, ax
704F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
7053  BA BF 00        mov dx, 0xbf
7056  F7 E2           mul dx
7058  C4 3E 17 A9     les di, ptr [0xa917]
705C  03 F8           add di, ax
705E  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
7062  C4 7E F4        les di, ptr [bp - 0xc]
7065  26 3A 45 2C     cmp al, byte ptr es:[di + 0x2c]
7069  75 17           jne 0x7082
706B  C4 7E FA        les di, ptr [bp - 6]
706E  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
7072  48              dec ax
7073  B1 03           mov cl, 3
7075  D3 E0           shl ax, cl
7077  C4 3E 2B A9     les di, ptr [0xa92b]
707B  03 F8           add di, ax
707D  26 C6 45 F8 FE  mov byte ptr es:[di - 8], 0xfe
loc_7082:
7082  8B 46 FE        mov ax, word ptr [bp - 2]
7085  3B 46 F8        cmp ax, word ptr [bp - 8]
7088  75 89           jne 0x7013
loc_708A:
708A  89 EC           mov sp, bp
708C  5D              pop bp
708D  C2 02 00        ret 2

; ---- routine 1771:7090  (found by: call)
sub_7090:
7090  55              push bp
7091  89 E5           mov bp, sp
7093  83 EC 0C        sub sp, 0xc
7096  C4 3E 23 A9     les di, ptr [0xa923]
709A  89 7E F8        mov word ptr [bp - 8], di
709D  8C 46 FA        mov word ptr [bp - 6], es
70A0  C4 7E F8        les di, ptr [bp - 8]
70A3  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
70A7  C4 7E F8        les di, ptr [bp - 8]
70AA  26 89 45 2C     mov word ptr es:[di + 0x2c], ax
70AE  C7 46 FE 03 00  mov word ptr [bp - 2], 3
70B3  EB 03           jmp 0x70b8
loc_70B5:
70B5  FF 46 FE        inc word ptr [bp - 2]
loc_70B8:
70B8  C7 46 FC 01 00  mov word ptr [bp - 4], 1
70BD  EB 03           jmp 0x70c2
loc_70BF:
70BF  FF 46 FC        inc word ptr [bp - 4]
loc_70C2:
70C2  8B 46 FC        mov ax, word ptr [bp - 4]
70C5  BA 38 00        mov dx, 0x38
70C8  F7 E2           mul dx
70CA  8B C8           mov cx, ax
70CC  8B 46 FE        mov ax, word ptr [bp - 2]
70CF  BA C0 01        mov dx, 0x1c0
70D2  F7 E2           mul dx
70D4  C4 3E 33 A9     les di, ptr [0xa933]
70D8  03 F8           add di, ax
70DA  03 F9           add di, cx
70DC  81 C7 08 0C     add di, 0xc08
70E0  89 7E F4        mov word ptr [bp - 0xc], di
70E3  8C 46 F6        mov word ptr [bp - 0xa], es
70E6  C4 7E F4        les di, ptr [bp - 0xc]
70E9  26 FF 35        push word ptr es:[di]
70EC  B8 09 00        mov ax, 9
70EF  2B 46 FC        sub ax, word ptr [bp - 4]
70F2  BA 38 00        mov dx, 0x38
70F5  F7 E2           mul dx
70F7  8B C8           mov cx, ax
70F9  8B 46 FE        mov ax, word ptr [bp - 2]
70FC  BA C0 01        mov dx, 0x1c0
70FF  F7 E2           mul dx
7101  C4 3E 33 A9     les di, ptr [0xa933]
7105  03 F8           add di, ax
7107  03 F9           add di, cx
7109  26 FF B5 08 0C  push word ptr es:[di + 0xc08]
710E  B8 06 00        mov ax, 6
7111  50              push ax
7112  31 C0           xor ax, ax
7114  50              push ax
7115  E8 7C EC        call 0x5d94
7118  55              push bp
7119  E8 CF FE        call 0x6feb
711C  C4 7E F8        les di, ptr [bp - 8]
711F  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
7123  48              dec ax
7124  B1 03           mov cl, 3
7126  D3 E0           shl ax, cl
7128  C4 3E 2B A9     les di, ptr [0xa92b]
712C  03 F8           add di, ax
712E  81 C7 F8 FF     add di, 0xfff8
7132  06              push es
7133  57              push di
7134  C4 7E F8        les di, ptr [bp - 8]
7137  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
713B  C4 7E F8        les di, ptr [bp - 8]
713E  26 2B 45 2C     sub ax, word ptr es:[di + 0x2c]
7142  48              dec ax
7143  31 D2           xor dx, dx
7145  B9 02 00        mov cx, 2
7148  F7 F1           div cx
714A  05 61 09        add ax, 0x961
714D  B1 03           mov cl, 3
714F  D3 E0           shl ax, cl
7151  C4 3E 2B A9     les di, ptr [0xa92b]
7155  03 F8           add di, ax
7157  81 C7 F8 FF     add di, 0xfff8
715B  06              push es
715C  57              push di
715D  B8 08 00        mov ax, 8
7160  50              push ax
7161  9A 5D 02 E4 23  call far 23E4:025D
7166  B8 09 00        mov ax, 9
7169  2B 46 FC        sub ax, word ptr [bp - 4]
716C  BA 38 00        mov dx, 0x38
716F  F7 E2           mul dx
7171  8B C8           mov cx, ax
7173  8B 46 FE        mov ax, word ptr [bp - 2]
7176  BA C0 01        mov dx, 0x1c0
7179  F7 E2           mul dx
717B  C4 3E 33 A9     les di, ptr [0xa933]
717F  03 F8           add di, ax
7181  03 F9           add di, cx
7183  26 FF B5 08 0C  push word ptr es:[di + 0xc08]
7188  C4 7E F4        les di, ptr [bp - 0xc]
718B  26 FF 35        push word ptr es:[di]
718E  B8 06 00        mov ax, 6
7191  50              push ax
7192  31 C0           xor ax, ax
7194  50              push ax
7195  E8 FC EB        call 0x5d94
7198  55              push bp
7199  E8 4F FE        call 0x6feb
719C  83 7E FC 04     cmp word ptr [bp - 4], 4
71A0  74 03           je 0x71a5
71A2  E9 1A FF        jmp 0x70bf
loc_71A5:
71A5  83 7E FE 04     cmp word ptr [bp - 2], 4
71A9  74 03           je 0x71ae
71AB  E9 07 FF        jmp 0x70b5
loc_71AE:
71AE  89 EC           mov sp, bp
71B0  5D              pop bp
71B1  C3              ret

; ---- routine 1771:71B2  (found by: call)
sub_71B2:
71B2  55              push bp
71B3  89 E5           mov bp, sp
71B5  83 EC 1A        sub sp, 0x1a
71B8  C4 3E 23 A9     les di, ptr [0xa923]
71BC  89 7E EE        mov word ptr [bp - 0x12], di
71BF  8C 46 F0        mov word ptr [bp - 0x10], es
71C2  31 C0           xor ax, ax
71C4  50              push ax
71C5  E8 D1 EC        call 0x5e99
71C8  B8 08 00        mov ax, 8
71CB  50              push ax
71CC  9A B1 06 4B 21  call far 214B:06B1
71D1  BA 38 00        mov dx, 0x38
71D4  F7 E2           mul dx
71D6  50              push ax
71D7  B8 02 00        mov ax, 2
71DA  50              push ax
71DB  9A B1 06 4B 21  call far 214B:06B1
71E0  BA C0 01        mov dx, 0x1c0
71E3  F7 E2           mul dx
71E5  C4 3E 33 A9     les di, ptr [0xa933]
71E9  03 F8           add di, ax
71EB  58              pop ax
71EC  03 F8           add di, ax
71EE  26 8B 85 08 0C  mov ax, word ptr es:[di + 0xc08]
71F3  C4 7E EE        les di, ptr [bp - 0x12]
71F6  26 89 45 36     mov word ptr es:[di + 0x36], ax
71FA  C7 46 F6 01 00  mov word ptr [bp - 0xa], 1
71FF  EB 03           jmp 0x7204
loc_7201:
7201  FF 46 F6        inc word ptr [bp - 0xa]
loc_7204:
7204  B8 04 00        mov ax, 4
7207  50              push ax
7208  9A B1 06 4B 21  call far 214B:06B1
720D  89 46 F2        mov word ptr [bp - 0xe], ax
7210  8B 46 F6        mov ax, word ptr [bp - 0xa]
7213  BA 38 00        mov dx, 0x38
7216  F7 E2           mul dx
7218  C4 3E 33 A9     les di, ptr [0xa933]
721C  03 F8           add di, ax
721E  81 C7 C8 14     add di, 0x14c8
7222  89 7E EA        mov word ptr [bp - 0x16], di
7225  8C 46 EC        mov word ptr [bp - 0x14], es
7228  8B 46 F6        mov ax, word ptr [bp - 0xa]
722B  BA 38 00        mov dx, 0x38
722E  F7 E2           mul dx
7230  C4 3E 33 A9     les di, ptr [0xa933]
7234  03 F8           add di, ax
7236  26 8B 95 C8 0D  mov dx, word ptr es:[di + 0xdc8]
723B  8B 7E F2        mov di, word ptr [bp - 0xe]
723E  D1 E7           shl di, 1
7240  D1 E7           shl di, 1
7242  8A 85 72 0F     mov al, byte ptr [di + 0xf72]
7246  30 E4           xor ah, ah
7248  B1 03           mov cl, 3
724A  D3 E0           shl ax, cl
724C  C4 7E EA        les di, ptr [bp - 0x16]
724F  03 F8           add di, ax
7251  26 89 55 F8     mov word ptr es:[di - 8], dx
7255  B8 09 00        mov ax, 9
7258  2B 46 F6        sub ax, word ptr [bp - 0xa]
725B  BA 38 00        mov dx, 0x38
725E  F7 E2           mul dx
7260  C4 3E 33 A9     les di, ptr [0xa933]
7264  03 F8           add di, ax
7266  26 8B 95 D0 0D  mov dx, word ptr es:[di + 0xdd0]
726B  8B 7E F2        mov di, word ptr [bp - 0xe]
726E  D1 E7           shl di, 1
7270  D1 E7           shl di, 1
7272  8A 85 73 0F     mov al, byte ptr [di + 0xf73]
7276  30 E4           xor ah, ah
7278  B1 03           mov cl, 3
727A  D3 E0           shl ax, cl
727C  C4 7E EA        les di, ptr [bp - 0x16]
727F  03 F8           add di, ax
7281  26 89 55 F8     mov word ptr es:[di - 8], dx
7285  8B 46 F6        mov ax, word ptr [bp - 0xa]
7288  BA 38 00        mov dx, 0x38
728B  F7 E2           mul dx
728D  C4 3E 33 A9     les di, ptr [0xa933]
7291  03 F8           add di, ax
7293  26 8B 95 88 0F  mov dx, word ptr es:[di + 0xf88]
7298  8B 7E F2        mov di, word ptr [bp - 0xe]
729B  D1 E7           shl di, 1
729D  D1 E7           shl di, 1
729F  8A 85 74 0F     mov al, byte ptr [di + 0xf74]
72A3  30 E4           xor ah, ah
72A5  B1 03           mov cl, 3
72A7  D3 E0           shl ax, cl
72A9  C4 7E EA        les di, ptr [bp - 0x16]
72AC  03 F8           add di, ax
72AE  26 89 55 F8     mov word ptr es:[di - 8], dx
72B2  8B 46 F6        mov ax, word ptr [bp - 0xa]
72B5  05 61 09        add ax, 0x961
72B8  48              dec ax
72B9  B1 03           mov cl, 3
72BB  D3 E0           shl ax, cl
72BD  C4 3E 2B A9     les di, ptr [0xa92b]
72C1  03 F8           add di, ax
72C3  81 C7 F8 FF     add di, 0xfff8
72C7  06              push es
72C8  57              push di
72C9  0E              push cs
72CA  E8 C7 E9        call 0x5c94
72CD  8B D0           mov dx, ax
72CF  8B 7E F2        mov di, word ptr [bp - 0xe]
72D2  D1 E7           shl di, 1
72D4  D1 E7           shl di, 1
72D6  8A 85 75 0F     mov al, byte ptr [di + 0xf75]
72DA  30 E4           xor ah, ah
72DC  B1 03           mov cl, 3
72DE  D3 E0           shl ax, cl
72E0  C4 7E EA        les di, ptr [bp - 0x16]
72E3  03 F8           add di, ax
72E5  26 89 55 F8     mov word ptr es:[di - 8], dx
72E9  C7 46 F4 01 00  mov word ptr [bp - 0xc], 1
72EE  EB 03           jmp 0x72f3
loc_72F0:
72F0  FF 46 F4        inc word ptr [bp - 0xc]
loc_72F3:
72F3  8B 46 F4        mov ax, word ptr [bp - 0xc]
72F6  B1 03           mov cl, 3
72F8  D3 E0           shl ax, cl
72FA  C4 7E EA        les di, ptr [bp - 0x16]
72FD  03 F8           add di, ax
72FF  26 8B 45 F8     mov ax, word ptr es:[di - 8]
7303  BA BF 00        mov dx, 0xbf
7306  F7 E2           mul dx
7308  C4 3E 17 A9     les di, ptr [0xa917]
730C  03 F8           add di, ax
730E  89 7E E6        mov word ptr [bp - 0x1a], di
7311  8C 46 E8        mov word ptr [bp - 0x18], es
7314  C4 7E E6        les di, ptr [bp - 0x1a]
7317  26 80 7D 2E 80  cmp byte ptr es:[di + 0x2e], 0x80
731C  76 18           jbe 0x7336
731E  8A 56 F6        mov dl, byte ptr [bp - 0xa]
7321  C4 7E E6        les di, ptr [bp - 0x1a]
7324  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
7328  30 E4           xor ah, ah
732A  2D 80 00        sub ax, 0x80
732D  C4 7E EE        les di, ptr [bp - 0x12]
7330  03 F8           add di, ax
7332  26 88 55 01     mov byte ptr es:[di + 1], dl
loc_7336:
7336  83 7E F4 04     cmp word ptr [bp - 0xc], 4
733A  75 B4           jne 0x72f0
733C  83 7E F6 08     cmp word ptr [bp - 0xa], 8
7340  74 03           je 0x7345
7342  E9 BC FE        jmp 0x7201
loc_7345:
7345  C7 46 FE 01 00  mov word ptr [bp - 2], 1
734A  EB 03           jmp 0x734f
loc_734C:
734C  FF 46 FE        inc word ptr [bp - 2]
loc_734F:
734F  C7 46 FA 01 00  mov word ptr [bp - 6], 1
7354  EB 03           jmp 0x7359
loc_7356:
7356  FF 46 FA        inc word ptr [bp - 6]
loc_7359:
7359  C7 46 F6 01 00  mov word ptr [bp - 0xa], 1
735E  EB 03           jmp 0x7363
loc_7360:
7360  FF 46 F6        inc word ptr [bp - 0xa]
loc_7363:
7363  8B 46 FE        mov ax, word ptr [bp - 2]
7366  8B D8           mov bx, ax
7368  8B 46 F6        mov ax, word ptr [bp - 0xa]
736B  40              inc ax
736C  31 D2           xor dx, dx
736E  B9 02 00        mov cx, 2
7371  F7 F1           div cx
7373  8B F8           mov di, ax
7375  D1 E7           shl di, 1
7377  D1 E7           shl di, 1
7379  03 FB           add di, bx
737B  8A 85 D5 10     mov al, byte ptr [di + 0x10d5]
737F  30 E4           xor ah, ah
7381  8B D8           mov bx, ax
7383  8B 46 F6        mov ax, word ptr [bp - 0xa]
7386  31 D2           xor dx, dx
7388  B9 04 00        mov cx, 4
738B  F7 F1           div cx
738D  92              xchg dx, ax
738E  8B 7E FA        mov di, word ptr [bp - 6]
7391  D1 E7           shl di, 1
7393  D1 E7           shl di, 1
7395  03 F8           add di, ax
7397  8A 85 C6 10     mov al, byte ptr [di + 0x10c6]
739B  30 E4           xor ah, ah
739D  48              dec ax
739E  B9 05 00        mov cx, 5
73A1  D3 E0           shl ax, cl
73A3  03 C3           add ax, bx
73A5  8B F8           mov di, ax
73A7  8A 85 FF 9C     mov al, byte ptr [di - 0x6301]
73AB  30 E4           xor ah, ah
73AD  50              push ax
73AE  8B 46 F6        mov ax, word ptr [bp - 0xa]
73B1  D1 E0           shl ax, 1
73B3  8B D0           mov dx, ax
73B5  8B 46 FA        mov ax, word ptr [bp - 6]
73B8  48              dec ax
73B9  B9 05 00        mov cx, 5
73BC  D3 E0           shl ax, cl
73BE  03 C2           add ax, dx
73C0  48              dec ax
73C1  8B F8           mov di, ax
73C3  8A 85 FF 9C     mov al, byte ptr [di - 0x6301]
73C7  30 E4           xor ah, ah
73C9  50              push ax
73CA  B8 01 00        mov ax, 1
73CD  50              push ax
73CE  31 C0           xor ax, ax
73D0  50              push ax
73D1  E8 C0 E9        call 0x5d94
73D4  83 7E F6 10     cmp word ptr [bp - 0xa], 0x10
73D8  75 86           jne 0x7360
73DA  83 7E FA 04     cmp word ptr [bp - 6], 4
73DE  74 03           je 0x73e3
73E0  E9 73 FF        jmp 0x7356
loc_73E3:
73E3  83 7E FE 04     cmp word ptr [bp - 2], 4
73E7  74 03           je 0x73ec
73E9  E9 60 FF        jmp 0x734c
loc_73EC:
73EC  C7 46 F6 01 00  mov word ptr [bp - 0xa], 1
73F1  EB 03           jmp 0x73f6
loc_73F3:
73F3  FF 46 F6        inc word ptr [bp - 0xa]
loc_73F6:
73F6  8B 46 F6        mov ax, word ptr [bp - 0xa]
73F9  D1 E0           shl ax, 1
73FB  48              dec ax
73FC  8B F8           mov di, ax
73FE  8A 85 FF 9C     mov al, byte ptr [di - 0x6301]
7402  30 E4           xor ah, ah
7404  50              push ax
7405  8B 46 F6        mov ax, word ptr [bp - 0xa]
7408  D1 E0           shl ax, 1
740A  8B F8           mov di, ax
740C  8A 85 FF 9C     mov al, byte ptr [di - 0x6301]
7410  30 E4           xor ah, ah
7412  50              push ax
7413  B8 01 00        mov ax, 1
7416  50              push ax
7417  31 C0           xor ax, ax
7419  50              push ax
741A  E8 77 E9        call 0x5d94
741D  83 7E F6 40     cmp word ptr [bp - 0xa], 0x40
7421  75 D0           jne 0x73f3
7423  C7 46 FE 01 00  mov word ptr [bp - 2], 1
7428  EB 03           jmp 0x742d
loc_742A:
742A  FF 46 FE        inc word ptr [bp - 2]
loc_742D:
742D  C7 46 F8 01 00  mov word ptr [bp - 8], 1
7432  EB 03           jmp 0x7437
loc_7434:
7434  FF 46 F8        inc word ptr [bp - 8]
loc_7437:
7437  8B 46 F8        mov ax, word ptr [bp - 8]
743A  BA 38 00        mov dx, 0x38
743D  F7 E2           mul dx
743F  C4 3E 33 A9     les di, ptr [0xa933]
7443  03 F8           add di, ax
7445  81 C7 C8 14     add di, 0x14c8
7449  89 7E EA        mov word ptr [bp - 0x16], di
744C  8C 46 EC        mov word ptr [bp - 0x14], es
744F  C4 7E EE        les di, ptr [bp - 0x12]
7452  26 8B 55 28     mov dx, word ptr es:[di + 0x28]
7456  8B 46 FE        mov ax, word ptr [bp - 2]
7459  D1 E0           shl ax, 1
745B  C4 7E EA        les di, ptr [bp - 0x16]
745E  03 F8           add di, ax
7460  26 89 55 1E     mov word ptr es:[di + 0x1e], dx
7464  8B 7E FE        mov di, word ptr [bp - 2]
7467  D1 E7           shl di, 1
7469  8A 85 BD 10     mov al, byte ptr [di + 0x10bd]
746D  30 E4           xor ah, ah
746F  B1 03           mov cl, 3
7471  D3 E0           shl ax, cl
7473  C4 7E EA        les di, ptr [bp - 0x16]
7476  03 F8           add di, ax
7478  26 FF 75 F8     push word ptr es:[di - 8]
747C  8B 7E FE        mov di, word ptr [bp - 2]
747F  D1 E7           shl di, 1
7481  8A 85 BC 10     mov al, byte ptr [di + 0x10bc]
7485  30 E4           xor ah, ah
7487  B1 03           mov cl, 3
7489  D3 E0           shl ax, cl
748B  C4 7E EA        les di, ptr [bp - 0x16]
748E  03 F8           add di, ax
7490  26 FF 75 F8     push word ptr es:[di - 8]
7494  B8 07 00        mov ax, 7
7497  50              push ax
7498  FF 76 F8        push word ptr [bp - 8]
749B  C4 7E EE        les di, ptr [bp - 0x12]
749E  26 FF 75 36     push word ptr es:[di + 0x36]
74A2  E8 95 E9        call 0x5e3a
74A5  83 7E F8 08     cmp word ptr [bp - 8], 8
74A9  75 89           jne 0x7434
74AB  83 7E FE 06     cmp word ptr [bp - 2], 6
74AF  74 03           je 0x74b4
74B1  E9 76 FF        jmp 0x742a
loc_74B4:
74B4  B0 01           mov al, 1
74B6  50              push ax
74B7  E8 5D F1        call 0x6617
74BA  89 EC           mov sp, bp
74BC  5D              pop bp
74BD  C3              ret

; ---- routine 1771:74BE  (found by: call)
sub_74BE:
74BE  55              push bp
74BF  89 E5           mov bp, sp
74C1  83 EC 08        sub sp, 8
74C4  C4 3E 23 A9     les di, ptr [0xa923]
74C8  89 7E F8        mov word ptr [bp - 8], di
74CB  8C 46 FA        mov word ptr [bp - 6], es
74CE  C4 7E F8        les di, ptr [bp - 8]
74D1  26 8B 45 36     mov ax, word ptr es:[di + 0x36]
74D5  89 46 FC        mov word ptr [bp - 4], ax
74D8  C4 7E F8        les di, ptr [bp - 8]
74DB  26 8A 45 3D     mov al, byte ptr es:[di + 0x3d]
74DF  3C 04           cmp al, 4
74E1  75 57           jne 0x753a
74E3  C4 7E F8        les di, ptr [bp - 8]
74E6  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
74EA  C4 7E F8        les di, ptr [bp - 8]
74ED  26 89 45 2A     mov word ptr es:[di + 0x2a], ax
74F1  C7 46 FE 01 00  mov word ptr [bp - 2], 1
74F6  EB 03           jmp 0x74fb
loc_74F8:
74F8  FF 46 FE        inc word ptr [bp - 2]
loc_74FB:
74FB  8B 46 FE        mov ax, word ptr [bp - 2]
74FE  BA 38 00        mov dx, 0x38
7501  F7 E2           mul dx
7503  C4 3E 33 A9     les di, ptr [0xa933]
7507  03 F8           add di, ax
7509  26 FF B5 C8 14  push word ptr es:[di + 0x14c8]
750E  B8 09 00        mov ax, 9
7511  2B 46 FE        sub ax, word ptr [bp - 2]
7514  BA 38 00        mov dx, 0x38
7517  F7 E2           mul dx
7519  C4 3E 33 A9     les di, ptr [0xa933]
751D  03 F8           add di, ax
751F  26 FF B5 D0 14  push word ptr es:[di + 0x14d0]
7524  B8 08 00        mov ax, 8
7527  50              push ax
7528  31 C0           xor ax, ax
752A  50              push ax
752B  FF 76 FC        push word ptr [bp - 4]
752E  E8 09 E9        call 0x5e3a
7531  83 7E FE 08     cmp word ptr [bp - 2], 8
7535  75 C1           jne 0x74f8
7537  E9 73 01        jmp 0x76ad
loc_753A:
753A  3C 03           cmp al, 3
753C  75 66           jne 0x75a4
753E  C7 46 FE 01 00  mov word ptr [bp - 2], 1
7543  EB 03           jmp 0x7548
loc_7545:
7545  FF 46 FE        inc word ptr [bp - 2]
loc_7548:
7548  8B 46 FE        mov ax, word ptr [bp - 2]
754B  D1 E0           shl ax, 1
754D  C4 7E F8        les di, ptr [bp - 8]
7550  26 03 45 2A     add ax, word ptr es:[di + 0x2a]
7554  2D 02 00        sub ax, 2
7557  B1 03           mov cl, 3
7559  D3 E0           shl ax, cl
755B  C4 3E 2B A9     les di, ptr [0xa92b]
755F  03 F8           add di, ax
7561  81 C7 F8 FF     add di, 0xfff8
7565  06              push es
7566  57              push di
7567  0E              push cs
7568  E8 29 E7        call 0x5c94
756B  50              push ax
756C  8B 46 FE        mov ax, word ptr [bp - 2]
756F  D1 E0           shl ax, 1
7571  C4 7E F8        les di, ptr [bp - 8]
7574  26 03 45 2A     add ax, word ptr es:[di + 0x2a]
7578  48              dec ax
7579  B1 03           mov cl, 3
757B  D3 E0           shl ax, cl
757D  C4 3E 2B A9     les di, ptr [0xa92b]
7581  03 F8           add di, ax
7583  81 C7 F8 FF     add di, 0xfff8
7587  06              push es
7588  57              push di
7589  0E              push cs
758A  E8 07 E7        call 0x5c94
758D  50              push ax
758E  B8 C8 00        mov ax, 0xc8
7591  50              push ax
7592  31 C0           xor ax, ax
7594  50              push ax
7595  FF 76 FC        push word ptr [bp - 4]
7598  E8 9F E8        call 0x5e3a
759B  83 7E FE 04     cmp word ptr [bp - 2], 4
759F  75 A4           jne 0x7545
75A1  E9 09 01        jmp 0x76ad
loc_75A4:
75A4  3C 02           cmp al, 2
75A6  75 68           jne 0x7610
75A8  C7 46 FE 01 00  mov word ptr [bp - 2], 1
75AD  EB 03           jmp 0x75b2
loc_75AF:
75AF  FF 46 FE        inc word ptr [bp - 2]
loc_75B2:
75B2  8B 46 FE        mov ax, word ptr [bp - 2]
75B5  D1 E0           shl ax, 1
75B7  C4 7E F8        les di, ptr [bp - 8]
75BA  26 03 45 2A     add ax, word ptr es:[di + 0x2a]
75BE  05 06 00        add ax, 6
75C1  B1 03           mov cl, 3
75C3  D3 E0           shl ax, cl
75C5  C4 3E 2B A9     les di, ptr [0xa92b]
75C9  03 F8           add di, ax
75CB  81 C7 F8 FF     add di, 0xfff8
75CF  06              push es
75D0  57              push di
75D1  0E              push cs
75D2  E8 BF E6        call 0x5c94
75D5  50              push ax
75D6  8B 46 FE        mov ax, word ptr [bp - 2]
75D9  D1 E0           shl ax, 1
75DB  C4 7E F8        les di, ptr [bp - 8]
75DE  26 03 45 2A     add ax, word ptr es:[di + 0x2a]
75E2  05 07 00        add ax, 7
75E5  B1 03           mov cl, 3
75E7  D3 E0           shl ax, cl
75E9  C4 3E 2B A9     les di, ptr [0xa92b]
75ED  03 F8           add di, ax
75EF  81 C7 F8 FF     add di, 0xfff8
75F3  06              push es
75F4  57              push di
75F5  0E              push cs
75F6  E8 9B E6        call 0x5c94
75F9  50              push ax
75FA  B8 C9 00        mov ax, 0xc9
75FD  50              push ax
75FE  31 C0           xor ax, ax
7600  50              push ax
7601  FF 76 FC        push word ptr [bp - 4]
7604  E8 33 E8        call 0x5e3a
7607  83 7E FE 02     cmp word ptr [bp - 2], 2
760B  75 A2           jne 0x75af
760D  E9 9D 00        jmp 0x76ad
loc_7610:
7610  3C 01           cmp al, 1
7612  74 03           je 0x7617
7614  E9 96 00        jmp 0x76ad
loc_7617:
7617  C4 7E F8        les di, ptr [bp - 8]
761A  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
761E  05 0C 00        add ax, 0xc
7621  B1 03           mov cl, 3
7623  D3 E0           shl ax, cl
7625  C4 3E 2B A9     les di, ptr [0xa92b]
7629  03 F8           add di, ax
762B  81 C7 F8 FF     add di, 0xfff8
762F  06              push es
7630  57              push di
7631  0E              push cs
7632  E8 96 E6        call 0x5ccb
7635  50              push ax
7636  C4 7E F8        les di, ptr [bp - 8]
7639  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
763D  05 0D 00        add ax, 0xd
7640  B1 03           mov cl, 3
7642  D3 E0           shl ax, cl
7644  C4 3E 2B A9     les di, ptr [0xa92b]
7648  03 F8           add di, ax
764A  81 C7 F8 FF     add di, 0xfff8
764E  06              push es
764F  57              push di
7650  0E              push cs
7651  E8 77 E6        call 0x5ccb
7654  50              push ax
7655  B8 CA 00        mov ax, 0xca
7658  50              push ax
7659  31 C0           xor ax, ax
765B  50              push ax
765C  FF 76 FC        push word ptr [bp - 4]
765F  E8 D8 E7        call 0x5e3a
7662  C4 7E F8        les di, ptr [bp - 8]
7665  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
7669  05 0C 00        add ax, 0xc
766C  B1 03           mov cl, 3
766E  D3 E0           shl ax, cl
7670  C4 3E 2B A9     les di, ptr [0xa92b]
7674  03 F8           add di, ax
7676  81 C7 F8 FF     add di, 0xfff8
767A  06              push es
767B  57              push di
767C  0E              push cs
767D  E8 14 E6        call 0x5c94
7680  50              push ax
7681  C4 7E F8        les di, ptr [bp - 8]
7684  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
7688  05 0D 00        add ax, 0xd
768B  B1 03           mov cl, 3
768D  D3 E0           shl ax, cl
768F  C4 3E 2B A9     les di, ptr [0xa92b]
7693  03 F8           add di, ax
7695  81 C7 F8 FF     add di, 0xfff8
7699  06              push es
769A  57              push di
769B  0E              push cs
769C  E8 F5 E5        call 0x5c94
769F  50              push ax
76A0  B8 CB 00        mov ax, 0xcb
76A3  50              push ax
76A4  31 C0           xor ax, ax
76A6  50              push ax
76A7  FF 76 FC        push word ptr [bp - 4]
76AA  E8 8D E7        call 0x5e3a
loc_76AD:
76AD  89 EC           mov sp, bp
76AF  5D              pop bp
76B0  C3              ret

