; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 15 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:8CCA  (found by: call)
sub_8CCA:
8CCA  55              push bp
8CCB  89 E5           mov bp, sp
8CCD  B0 01           mov al, 1
8CCF  50              push ax
8CD0  55              push bp
8CD1  E8 93 FF        call 0x8c67
8CD4  B0 00           mov al, 0
8CD6  50              push ax
8CD7  55              push bp
8CD8  E8 8C FF        call 0x8c67
8CDB  C6 06 EF 82 00  mov byte ptr [0x82ef], 0
8CE0  C6 06 EE 82 01  mov byte ptr [0x82ee], 1
8CE5  A1 EE 82        mov ax, word ptr [0x82ee]
8CE8  A3 F0 82        mov word ptr [0x82f0], ax
8CEB  A1 EE 82        mov ax, word ptr [0x82ee]
8CEE  A3 F4 82        mov word ptr [0x82f4], ax
8CF1  89 EC           mov sp, bp
8CF3  5D              pop bp
8CF4  C3              ret

; ---- routine 0791:8CF5  (found by: call)
sub_8CF5:
8CF5  55              push bp
8CF6  89 E5           mov bp, sp
8CF8  83 EC 0C        sub sp, 0xc
8CFB  C6 46 FF 00     mov byte ptr [bp - 1], 0
8CFF  EB 03           jmp 0x8d04
loc_8D01:
8D01  FE 46 FF        inc byte ptr [bp - 1]
loc_8D04:
8D04  8A 46 FF        mov al, byte ptr [bp - 1]
8D07  98              cwde
8D08  8B F8           mov di, ax
8D0A  D1 E7           shl di, 1
8D0C  8B F7           mov si, di
8D0E  D1 E7           shl di, 1
8D10  03 FE           add di, si
8D12  81 C7 E2 82     add di, 0x82e2
8D16  89 7E F7        mov word ptr [bp - 9], di
8D19  8C 5E F9        mov word ptr [bp - 7], ds
8D1C  C4 7E F7        les di, ptr [bp - 9]
8D1F  26 C6 45 01 00  mov byte ptr es:[di + 1], 0
8D24  8A 46 FF        mov al, byte ptr [bp - 1]
8D27  98              cwde
8D28  8B F8           mov di, ax
8D2A  8A 85 68 06     mov al, byte ptr [di + 0x668]
8D2E  30 E4           xor ah, ah
8D30  40              inc ax
8D31  BA 16 00        mov dx, 0x16
8D34  F7 E2           mul dx
8D36  8B F8           mov di, ax
8D38  81 C7 E8 80     add di, 0x80e8
8D3C  1E              push ds
8D3D  57              push di
8D3E  0E              push cs
8D3F  E8 A3 9E        call 0x2be5
8D42  98              cwde
8D43  89 46 FB        mov word ptr [bp - 5], ax
8D46  8A 46 FF        mov al, byte ptr [bp - 1]
8D49  98              cwde
8D4A  8B F8           mov di, ax
8D4C  8A 85 68 06     mov al, byte ptr [di + 0x668]
8D50  30 E4           xor ah, ah
8D52  05 0B 00        add ax, 0xb
8D55  89 46 F5        mov word ptr [bp - 0xb], ax
8D58  8A 46 FF        mov al, byte ptr [bp - 1]
8D5B  98              cwde
8D5C  8B F8           mov di, ax
8D5E  8A 85 68 06     mov al, byte ptr [di + 0x668]
8D62  30 E4           xor ah, ah
8D64  05 02 00        add ax, 2
8D67  3B 46 F5        cmp ax, word ptr [bp - 0xb]
8D6A  7F 49           jg 0x8db5
8D6C  89 46 FD        mov word ptr [bp - 3], ax
8D6F  EB 03           jmp 0x8d74
loc_8D71:
8D71  FF 46 FD        inc word ptr [bp - 3]
loc_8D74:
8D74  C4 7E F7        les di, ptr [bp - 9]
8D77  26 8A 45 01     mov al, byte ptr es:[di + 1]
8D7B  98              cwde
8D7C  8B C8           mov cx, ax
8D7E  8B 46 FD        mov ax, word ptr [bp - 3]
8D81  BA 16 00        mov dx, 0x16
8D84  F7 E2           mul dx
8D86  8B F8           mov di, ax
8D88  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
8D8C  98              cwde
8D8D  F7 6E FB        imul word ptr [bp - 5]
8D90  3B C1           cmp ax, cx
8D92  7D 19           jge 0x8dad
8D94  8B 46 FD        mov ax, word ptr [bp - 3]
8D97  BA 16 00        mov dx, 0x16
8D9A  F7 E2           mul dx
8D9C  8B F8           mov di, ax
8D9E  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
8DA2  98              cwde
8DA3  F7 6E FB        imul word ptr [bp - 5]
8DA6  C4 7E F7        les di, ptr [bp - 9]
8DA9  26 88 45 01     mov byte ptr es:[di + 1], al
loc_8DAD:
8DAD  8B 46 FD        mov ax, word ptr [bp - 3]
8DB0  3B 46 F5        cmp ax, word ptr [bp - 0xb]
8DB3  75 BC           jne 0x8d71
loc_8DB5:
8DB5  C4 7E F7        les di, ptr [bp - 9]
8DB8  26 8A 45 01     mov al, byte ptr es:[di + 1]
8DBC  98              cwde
8DBD  F7 6E FB        imul word ptr [bp - 5]
8DC0  C4 7E F7        les di, ptr [bp - 9]
8DC3  26 88 45 01     mov byte ptr es:[di + 1], al
8DC7  C4 7E F7        les di, ptr [bp - 9]
8DCA  06              push es
8DCB  57              push di
8DCC  0E              push cs
8DCD  E8 54 00        call 0x8e24
8DD0  C4 7E F7        les di, ptr [bp - 9]
8DD3  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
8DD8  7F 04           jg 0x8dde
8DDA  B0 00           mov al, 0
8DDC  EB 02           jmp 0x8de0
loc_8DDE:
8DDE  B0 01           mov al, 1
loc_8DE0:
8DE0  8A D0           mov dl, al
8DE2  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
8DE7  7F 04           jg 0x8ded
8DE9  B0 00           mov al, 0
8DEB  EB 02           jmp 0x8def
loc_8DED:
8DED  B0 01           mov al, 1
loc_8DEF:
8DEF  3A C2           cmp al, dl
8DF1  75 24           jne 0x8e17
8DF3  80 3E 28 83 00  cmp byte ptr [0x8328], 0
8DF8  74 1D           je 0x8e17
8DFA  C4 7E F7        les di, ptr [bp - 9]
8DFD  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
8E02  74 13           je 0x8e17
8E04  FF 36 08 83     push word ptr [0x8308]
8E08  C4 7E F7        les di, ptr [bp - 9]
8E0B  26 FF 35        push word ptr es:[di]
8E0E  BF 04 83        mov di, 0x8304
8E11  1E              push ds
8E12  57              push di
8E13  0E              push cs
8E14  E8 AE 02        call 0x90c5
loc_8E17:
8E17  80 7E FF 01     cmp byte ptr [bp - 1], 1
8E1B  74 03           je 0x8e20
8E1D  E9 E1 FE        jmp 0x8d01
loc_8E20:
8E20  89 EC           mov sp, bp
8E22  5D              pop bp
8E23  C3              ret

; ---- routine 0791:8E24  (found by: call)
sub_8E24:
8E24  55              push bp
8E25  89 E5           mov bp, sp
8E27  C4 7E 06        les di, ptr [bp + 6]
8E2A  26 8B 45 02     mov ax, word ptr es:[di + 2]
8E2E  C4 7E 06        les di, ptr [bp + 6]
8E31  26 3B 05        cmp ax, word ptr es:[di]
8E34  74 7B           je 0x8eb1
8E36  C4 7E 06        les di, ptr [bp + 6]
8E39  26 8A 45 03     mov al, byte ptr es:[di + 3]
8E3D  98              cwde
8E3E  D1 E0           shl ax, 1
8E40  8B C8           mov cx, ax
8E42  C4 7E 06        les di, ptr [bp + 6]
8E45  26 8A 45 02     mov al, byte ptr es:[di + 2]
8E49  98              cwde
8E4A  BA A0 00        mov dx, 0xa0
8E4D  F7 E2           mul dx
8E4F  C4 3E 16 7C     les di, ptr [0x7c16]
8E53  03 F8           add di, ax
8E55  03 F9           add di, cx
8E57  26 8B 85 0E 09  mov ax, word ptr es:[di + 0x90e]
8E5C  C4 7E 06        les di, ptr [bp + 6]
8E5F  26 3B 45 04     cmp ax, word ptr es:[di + 4]
8E63  75 4C           jne 0x8eb1
8E65  C4 7E 06        les di, ptr [bp + 6]
8E68  26 8A 45 03     mov al, byte ptr es:[di + 3]
8E6C  98              cwde
8E6D  D1 E0           shl ax, 1
8E6F  8B C8           mov cx, ax
8E71  C4 7E 06        les di, ptr [bp + 6]
8E74  26 8A 45 02     mov al, byte ptr es:[di + 2]
8E78  98              cwde
8E79  BA A0 00        mov dx, 0xa0
8E7C  F7 E2           mul dx
8E7E  C4 3E 1E 7C     les di, ptr [0x7c1e]
8E82  03 F8           add di, ax
8E84  03 F9           add di, cx
8E86  26 8B 9D 0E 09  mov bx, word ptr es:[di + 0x90e]
8E8B  C4 7E 06        les di, ptr [bp + 6]
8E8E  26 8A 45 03     mov al, byte ptr es:[di + 3]
8E92  98              cwde
8E93  D1 E0           shl ax, 1
8E95  8B C8           mov cx, ax
8E97  C4 7E 06        les di, ptr [bp + 6]
8E9A  26 8A 45 02     mov al, byte ptr es:[di + 2]
8E9E  98              cwde
8E9F  BA A0 00        mov dx, 0xa0
8EA2  F7 E2           mul dx
8EA4  C4 3E 16 7C     les di, ptr [0x7c16]
8EA8  03 F8           add di, ax
8EAA  03 F9           add di, cx
8EAC  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_8EB1:
8EB1  C4 7E 06        les di, ptr [bp + 6]
8EB4  26 8B 05        mov ax, word ptr es:[di]
8EB7  C4 7E 06        les di, ptr [bp + 6]
8EBA  26 89 45 02     mov word ptr es:[di + 2], ax
8EBE  C4 7E 06        les di, ptr [bp + 6]
8EC1  26 8B 5D 04     mov bx, word ptr es:[di + 4]
8EC5  C4 7E 06        les di, ptr [bp + 6]
8EC8  26 8A 45 01     mov al, byte ptr es:[di + 1]
8ECC  98              cwde
8ECD  D1 E0           shl ax, 1
8ECF  8B C8           mov cx, ax
8ED1  C4 7E 06        les di, ptr [bp + 6]
8ED4  26 8A 05        mov al, byte ptr es:[di]
8ED7  98              cwde
8ED8  BA A0 00        mov dx, 0xa0
8EDB  F7 E2           mul dx
8EDD  C4 3E 16 7C     les di, ptr [0x7c16]
8EE1  03 F8           add di, ax
8EE3  03 F9           add di, cx
8EE5  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
8EEA  89 EC           mov sp, bp
8EEC  5D              pop bp
8EED  CA 04 00        retf 4
; data (not reached as code), 32 bytes
8EF0                  db 80 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
8F00                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:8F10  (found by: call)
sub_8F10:
8F10  55              push bp
8F11  89 E5           mov bp, sp
8F13  C4 7E 06        les di, ptr [bp + 6]
8F16  26 8B 45 02     mov ax, word ptr es:[di + 2]
8F1A  3B 06 40 06     cmp ax, word ptr [0x640]
8F1E  75 03           jne 0x8f23
8F20  E9 91 00        jmp 0x8fb4
loc_8F23:
8F23  C4 7E 06        les di, ptr [bp + 6]
8F26  26 8B 45 02     mov ax, word ptr es:[di + 2]
8F2A  C4 7E 06        les di, ptr [bp + 6]
8F2D  26 3B 05        cmp ax, word ptr es:[di]
8F30  75 03           jne 0x8f35
8F32  E9 7F 00        jmp 0x8fb4
loc_8F35:
8F35  C4 7E 06        les di, ptr [bp + 6]
8F38  26 8A 45 03     mov al, byte ptr es:[di + 3]
8F3C  98              cwde
8F3D  D1 E0           shl ax, 1
8F3F  8B C8           mov cx, ax
8F41  C4 7E 06        les di, ptr [bp + 6]
8F44  26 8A 45 02     mov al, byte ptr es:[di + 2]
8F48  98              cwde
8F49  BA A0 00        mov dx, 0xa0
8F4C  F7 E2           mul dx
8F4E  C4 3E 16 7C     les di, ptr [0x7c16]
8F52  03 F8           add di, ax
8F54  03 F9           add di, cx
8F56  26 8A 85 0E 09  mov al, byte ptr es:[di + 0x90e]
8F5B  50              push ax
8F5C  BF F0 8E        mov di, 0x8ef0
8F5F  0E              push cs
8F60  57              push di
8F61  9A DF 08 E4 23  call far 23E4:08DF
8F66  74 4C           je 0x8fb4
8F68  C4 7E 06        les di, ptr [bp + 6]
8F6B  26 8A 45 03     mov al, byte ptr es:[di + 3]
8F6F  98              cwde
8F70  D1 E0           shl ax, 1
8F72  8B C8           mov cx, ax
8F74  C4 7E 06        les di, ptr [bp + 6]
8F77  26 8A 45 02     mov al, byte ptr es:[di + 2]
8F7B  98              cwde
8F7C  BA A0 00        mov dx, 0xa0
8F7F  F7 E2           mul dx
8F81  C4 3E 1E 7C     les di, ptr [0x7c1e]
8F85  03 F8           add di, ax
8F87  03 F9           add di, cx
8F89  26 8B 9D 0E 09  mov bx, word ptr es:[di + 0x90e]
8F8E  C4 7E 06        les di, ptr [bp + 6]
8F91  26 8A 45 03     mov al, byte ptr es:[di + 3]
8F95  98              cwde
8F96  D1 E0           shl ax, 1
8F98  8B C8           mov cx, ax
8F9A  C4 7E 06        les di, ptr [bp + 6]
8F9D  26 8A 45 02     mov al, byte ptr es:[di + 2]
8FA1  98              cwde
8FA2  BA A0 00        mov dx, 0xa0
8FA5  F7 E2           mul dx
8FA7  C4 3E 16 7C     les di, ptr [0x7c16]
8FAB  03 F8           add di, ax
8FAD  03 F9           add di, cx
8FAF  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_8FB4:
8FB4  C4 7E 06        les di, ptr [bp + 6]
8FB7  26 8B 05        mov ax, word ptr es:[di]
8FBA  C4 7E 06        les di, ptr [bp + 6]
8FBD  26 89 45 02     mov word ptr es:[di + 2], ax
8FC1  C4 7E 06        les di, ptr [bp + 6]
8FC4  26 80 7D 0D 00  cmp byte ptr es:[di + 0xd], 0
8FC9  74 0E           je 0x8fd9
8FCB  C4 7E 06        les di, ptr [bp + 6]
8FCE  06              push es
8FCF  57              push di
8FD0  0E              push cs
8FD1  E8 8B F3        call 0x835f
8FD4  3D 02 00        cmp ax, 2
8FD7  77 04           ja 0x8fdd
loc_8FD9:
8FD9  B0 00           mov al, 0
8FDB  EB 02           jmp 0x8fdf
loc_8FDD:
8FDD  B0 01           mov al, 1
loc_8FDF:
8FDF  98              cwde
8FE0  8B F8           mov di, ax
8FE2  8A 85 80 08     mov al, byte ptr [di + 0x880]
8FE6  C4 7E 06        les di, ptr [bp + 6]
8FE9  26 88 45 04     mov byte ptr es:[di + 4], al
8FED  C4 7E 06        les di, ptr [bp + 6]
8FF0  26 8B 05        mov ax, word ptr es:[di]
8FF3  3B 06 40 06     cmp ax, word ptr [0x640]
8FF7  74 7A           je 0x9073
8FF9  C4 7E 06        les di, ptr [bp + 6]
8FFC  26 8A 45 01     mov al, byte ptr es:[di + 1]
9000  98              cwde
9001  D1 E0           shl ax, 1
9003  8B C8           mov cx, ax
9005  C4 7E 06        les di, ptr [bp + 6]
9008  26 8A 05        mov al, byte ptr es:[di]
900B  98              cwde
900C  BA A0 00        mov dx, 0xa0
900F  F7 E2           mul dx
9011  C4 3E 1E 7C     les di, ptr [0x7c1e]
9015  03 F8           add di, ax
9017  03 F9           add di, cx
9019  26 8B 9D 0E 09  mov bx, word ptr es:[di + 0x90e]
901E  C4 7E 06        les di, ptr [bp + 6]
9021  26 8A 45 01     mov al, byte ptr es:[di + 1]
9025  98              cwde
9026  D1 E0           shl ax, 1
9028  8B C8           mov cx, ax
902A  C4 7E 06        les di, ptr [bp + 6]
902D  26 8A 05        mov al, byte ptr es:[di]
9030  98              cwde
9031  BA A0 00        mov dx, 0xa0
9034  F7 E2           mul dx
9036  C4 3E 16 7C     les di, ptr [0x7c16]
903A  03 F8           add di, ax
903C  03 F9           add di, cx
903E  26 8B 85 0E 09  mov ax, word ptr es:[di + 0x90e]
9043  3B C3           cmp ax, bx
9045  75 2C           jne 0x9073
9047  C4 7E 06        les di, ptr [bp + 6]
904A  26 8B 5D 04     mov bx, word ptr es:[di + 4]
904E  C4 7E 06        les di, ptr [bp + 6]
9051  26 8A 45 01     mov al, byte ptr es:[di + 1]
9055  98              cwde
9056  D1 E0           shl ax, 1
9058  8B C8           mov cx, ax
905A  C4 7E 06        les di, ptr [bp + 6]
905D  26 8A 05        mov al, byte ptr es:[di]
9060  98              cwde
9061  BA A0 00        mov dx, 0xa0
9064  F7 E2           mul dx
9066  C4 3E 16 7C     les di, ptr [0x7c16]
906A  03 F8           add di, ax
906C  03 F9           add di, cx
906E  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_9073:
9073  89 EC           mov sp, bp
9075  5D              pop bp
9076  CA 04 00        retf 4

; ---- routine 0791:9079  (found by: call)
sub_9079:
9079  55              push bp
907A  89 E5           mov bp, sp
907C  A1 44 06        mov ax, word ptr [0x644]
907F  C4 7E 06        les di, ptr [bp + 6]
9082  26 89 05        mov word ptr es:[di], ax
9085  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
908A  74 02           je 0x908e
908C  EB 31           jmp 0x90bf
loc_908E:
908E  C4 7E 06        les di, ptr [bp + 6]
9091  06              push es
9092  57              push di
9093  0E              push cs
9094  E8 8D FD        call 0x8e24
9097  A0 44 06        mov al, byte ptr [0x644]
909A  98              cwde
909B  BA A0 00        mov dx, 0xa0
909E  F7 E2           mul dx
90A0  C4 3E 1E 7C     les di, ptr [0x7c1e]
90A4  03 F8           add di, ax
90A6  26 8B 8D 0E 09  mov cx, word ptr es:[di + 0x90e]
90AB  A0 44 06        mov al, byte ptr [0x644]
90AE  98              cwde
90AF  BA A0 00        mov dx, 0xa0
90B2  F7 E2           mul dx
90B4  C4 3E 16 7C     les di, ptr [0x7c16]
90B8  03 F8           add di, ax
90BA  26 89 8D 0E 09  mov word ptr es:[di + 0x90e], cx
loc_90BF:
90BF  89 EC           mov sp, bp
90C1  5D              pop bp
90C2  CA 04 00        retf 4

; ---- routine 0791:90C5  (found by: call)
sub_90C5:
90C5  55              push bp
90C6  89 E5           mov bp, sp
90C8  8B 46 0C        mov ax, word ptr [bp + 0xc]
90CB  C4 7E 06        les di, ptr [bp + 6]
90CE  26 89 45 04     mov word ptr es:[di + 4], ax
90D2  C4 7E 06        les di, ptr [bp + 6]
90D5  26 81 7D 04 AE 0E cmp word ptr es:[di + 4], 0xeae
90DB  75 04           jne 0x90e1
90DD  B0 00           mov al, 0
90DF  EB 02           jmp 0x90e3
loc_90E1:
90E1  B0 01           mov al, 1
loc_90E3:
90E3  98              cwde
90E4  8B F8           mov di, ax
90E6  8A 85 20 79     mov al, byte ptr [di + 0x7920]
90EA  98              cwde
90EB  8B D0           mov dx, ax
90ED  8A 46 0B        mov al, byte ptr [bp + 0xb]
90F0  98              cwde
90F1  03 C2           add ax, dx
90F3  C4 7E 06        les di, ptr [bp + 6]
90F6  26 88 45 01     mov byte ptr es:[di + 1], al
90FA  8A 46 0A        mov al, byte ptr [bp + 0xa]
90FD  C4 7E 06        les di, ptr [bp + 6]
9100  26 88 05        mov byte ptr es:[di], al
9103  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9108  75 09           jne 0x9113
910A  C4 7E 06        les di, ptr [bp + 6]
910D  06              push es
910E  57              push di
910F  0E              push cs
9110  E8 11 FD        call 0x8e24
loc_9113:
9113  89 EC           mov sp, bp
9115  5D              pop bp
9116  CA 08 00        retf 8

; ---- routine 0791:9119  (found by: call)
sub_9119:
9119  55              push bp
911A  89 E5           mov bp, sp
911C  80 7E 0A 00     cmp byte ptr [bp + 0xa], 0
9120  75 03           jne 0x9125
9122  E9 94 00        jmp 0x91b9
loc_9125:
9125  A0 F7 82        mov al, byte ptr [0x82f7]
9128  C4 7E 06        les di, ptr [bp + 6]
912B  26 88 45 07     mov byte ptr es:[di + 7], al
912F  A0 F6 82        mov al, byte ptr [0x82f6]
9132  98              cwde
9133  40              inc ax
9134  C4 7E 06        les di, ptr [bp + 6]
9137  26 88 45 06     mov byte ptr es:[di + 6], al
913B  C4 7E 06        les di, ptr [bp + 6]
913E  26 8A 45 07     mov al, byte ptr es:[di + 7]
9142  C4 7E 06        les di, ptr [bp + 6]
9145  26 3A 45 01     cmp al, byte ptr es:[di + 1]
9149  7F 04           jg 0x914f
914B  B0 00           mov al, 0
914D  EB 02           jmp 0x9151
loc_914F:
914F  B0 01           mov al, 1
loc_9151:
9151  98              cwde
9152  8B F8           mov di, ax
9154  8A 85 20 79     mov al, byte ptr [di + 0x7920]
9158  C4 7E 06        les di, ptr [bp + 6]
915B  26 00 45 01     add byte ptr es:[di + 1], al
915F  C4 7E 06        les di, ptr [bp + 6]
9162  26 8A 45 06     mov al, byte ptr es:[di + 6]
9166  C4 7E 06        les di, ptr [bp + 6]
9169  26 3A 05        cmp al, byte ptr es:[di]
916C  7F 04           jg 0x9172
916E  B0 00           mov al, 0
9170  EB 02           jmp 0x9174
loc_9172:
9172  B0 01           mov al, 1
loc_9174:
9174  98              cwde
9175  8B F8           mov di, ax
9177  8A 85 20 79     mov al, byte ptr [di + 0x7920]
917B  C4 7E 06        les di, ptr [bp + 6]
917E  26 00 05        add byte ptr es:[di], al
9181  C4 7E 06        les di, ptr [bp + 6]
9184  06              push es
9185  57              push di
9186  0E              push cs
9187  E8 9A FC        call 0x8e24
918A  C4 7E 06        les di, ptr [bp + 6]
918D  26 8B 5D 04     mov bx, word ptr es:[di + 4]
9191  C4 7E 06        les di, ptr [bp + 6]
9194  26 8A 45 01     mov al, byte ptr es:[di + 1]
9198  98              cwde
9199  D1 E0           shl ax, 1
919B  8B C8           mov cx, ax
919D  C4 7E 06        les di, ptr [bp + 6]
91A0  26 8A 05        mov al, byte ptr es:[di]
91A3  98              cwde
91A4  BA A0 00        mov dx, 0xa0
91A7  F7 E2           mul dx
91A9  C4 3E 16 7C     les di, ptr [0x7c16]
91AD  03 F8           add di, ax
91AF  03 F9           add di, cx
91B1  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
91B6  E9 3D 01        jmp 0x92f6
loc_91B9:
91B9  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
91BE  7E 25           jle 0x91e5
91C0  A0 F7 82        mov al, byte ptr [0x82f7]
91C3  98              cwde
91C4  40              inc ax
91C5  99              cdq
91C6  52              push dx
91C7  50              push ax
91C8  B8 02 00        mov ax, 2
91CB  50              push ax
91CC  9A B1 06 4B 21  call far 214B:06B1
91D1  05 1E 00        add ax, 0x1e
91D4  99              cdq
91D5  52              push dx
91D6  50              push ax
91D7  9A 1C 0D 4B 21  call far 214B:0D1C
91DC  C4 7E 06        les di, ptr [bp + 6]
91DF  26 88 45 07     mov byte ptr es:[di + 7], al
91E3  EB 27           jmp 0x920c
loc_91E5:
91E5  A0 F7 82        mov al, byte ptr [0x82f7]
91E8  98              cwde
91E9  48              dec ax
91EA  99              cdq
91EB  52              push dx
91EC  50              push ax
91ED  B8 02 00        mov ax, 2
91F0  50              push ax
91F1  9A B1 06 4B 21  call far 214B:06B1
91F6  8B D0           mov dx, ax
91F8  B8 E2 FF        mov ax, 0xffe2
91FB  2B C2           sub ax, dx
91FD  99              cdq
91FE  52              push dx
91FF  50              push ax
9200  9A 56 0D 4B 21  call far 214B:0D56
9205  C4 7E 06        les di, ptr [bp + 6]
9208  26 88 45 07     mov byte ptr es:[di + 7], al
loc_920C:
920C  C4 7E 06        les di, ptr [bp + 6]
920F  26 8A 45 07     mov al, byte ptr es:[di + 7]
9213  98              cwde
9214  99              cdq
9215  B9 04 00        mov cx, 4
9218  F7 F9           idiv cx
921A  40              inc ax
921B  C4 7E 06        les di, ptr [bp + 6]
921E  26 88 45 06     mov byte ptr es:[di + 6], al
9222  C4 7E 06        les di, ptr [bp + 6]
9225  81 C7 06 00     add di, 6
9229  06              push es
922A  57              push di
922B  B0 FB           mov al, 0xfb
922D  50              push ax
922E  B0 05           mov al, 5
9230  50              push ax
9231  9A 31 20 4B 21  call far 214B:2031
9236  C4 7E 06        les di, ptr [bp + 6]
9239  26 8B 45 06     mov ax, word ptr es:[di + 6]
923D  C4 7E 06        les di, ptr [bp + 6]
9240  26 3B 45 02     cmp ax, word ptr es:[di + 2]
9244  75 03           jne 0x9249
9246  E9 A4 00        jmp 0x92ed
loc_9249:
9249  C4 7E 06        les di, ptr [bp + 6]
924C  26 8A 45 07     mov al, byte ptr es:[di + 7]
9250  C4 7E 06        les di, ptr [bp + 6]
9253  26 3A 45 01     cmp al, byte ptr es:[di + 1]
9257  74 24           je 0x927d
9259  C4 7E 06        les di, ptr [bp + 6]
925C  26 8A 45 07     mov al, byte ptr es:[di + 7]
9260  C4 7E 06        les di, ptr [bp + 6]
9263  26 3A 45 01     cmp al, byte ptr es:[di + 1]
9267  7F 04           jg 0x926d
9269  B0 00           mov al, 0
926B  EB 02           jmp 0x926f
loc_926D:
926D  B0 01           mov al, 1
loc_926F:
926F  98              cwde
9270  8B F8           mov di, ax
9272  8A 85 20 79     mov al, byte ptr [di + 0x7920]
9276  C4 7E 06        les di, ptr [bp + 6]
9279  26 00 45 01     add byte ptr es:[di + 1], al
loc_927D:
927D  C4 7E 06        les di, ptr [bp + 6]
9280  26 8A 45 06     mov al, byte ptr es:[di + 6]
9284  C4 7E 06        les di, ptr [bp + 6]
9287  26 3A 05        cmp al, byte ptr es:[di]
928A  74 22           je 0x92ae
928C  C4 7E 06        les di, ptr [bp + 6]
928F  26 8A 45 06     mov al, byte ptr es:[di + 6]
9293  C4 7E 06        les di, ptr [bp + 6]
9296  26 3A 05        cmp al, byte ptr es:[di]
9299  7F 04           jg 0x929f
929B  B0 00           mov al, 0
929D  EB 02           jmp 0x92a1
loc_929F:
929F  B0 01           mov al, 1
loc_92A1:
92A1  98              cwde
92A2  8B F8           mov di, ax
92A4  8A 85 20 79     mov al, byte ptr [di + 0x7920]
92A8  C4 7E 06        les di, ptr [bp + 6]
92AB  26 00 05        add byte ptr es:[di], al
loc_92AE:
92AE  C4 7E 06        les di, ptr [bp + 6]
92B1  26 8A 45 01     mov al, byte ptr es:[di + 1]
92B5  98              cwde
92B6  D1 E0           shl ax, 1
92B8  8B C8           mov cx, ax
92BA  C4 7E 06        les di, ptr [bp + 6]
92BD  26 8A 05        mov al, byte ptr es:[di]
92C0  98              cwde
92C1  BA A0 00        mov dx, 0xa0
92C4  F7 E2           mul dx
92C6  C4 3E 1E 7C     les di, ptr [0x7c1e]
92CA  03 F8           add di, ax
92CC  03 F9           add di, cx
92CE  26 8A 85 0E 09  mov al, byte ptr es:[di + 0x90e]
92D3  50              push ax
92D4  BF 48 06        mov di, 0x648
92D7  1E              push ds
92D8  57              push di
92D9  9A DF 08 E4 23  call far 23E4:08DF
92DE  74 0D           je 0x92ed
92E0  C4 7E 06        les di, ptr [bp + 6]
92E3  26 8B 45 02     mov ax, word ptr es:[di + 2]
92E7  C4 7E 06        les di, ptr [bp + 6]
92EA  26 89 05        mov word ptr es:[di], ax
loc_92ED:
92ED  C4 7E 06        les di, ptr [bp + 6]
92F0  06              push es
92F1  57              push di
92F2  0E              push cs
92F3  E8 2E FB        call 0x8e24
loc_92F6:
92F6  89 EC           mov sp, bp
92F8  5D              pop bp
92F9  CA 06 00        retf 6

; ---- routine 0791:92FC  (found by: call)
sub_92FC:
92FC  55              push bp
92FD  89 E5           mov bp, sp
92FF  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9304  75 15           jne 0x931b
9306  83 3E 1B 83 00  cmp word ptr [0x831b], 0
930B  74 0E           je 0x931b
930D  80 3E 26 83 00  cmp byte ptr [0x8326], 0
9312  75 07           jne 0x931b
9314  80 3E 21 0C 00  cmp byte ptr [0xc21], 0
9319  74 02           je 0x931d
loc_931B:
931B  EB 4F           jmp 0x936c
loc_931D:
931D  80 3E 25 83 00  cmp byte ptr [0x8325], 0
9322  74 15           je 0x9339
9324  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
9329  75 0E           jne 0x9339
932B  80 3E 37 7C 00  cmp byte ptr [0x7c37], 0
9330  75 07           jne 0x9339
9332  80 3E 55 9B 00  cmp byte ptr [0x9b55], 0
9337  74 1D           je 0x9356
loc_9339:
9339  80 3E 38 7C 00  cmp byte ptr [0x7c38], 0
933E  75 0F           jne 0x934f
9340  BF E4 26        mov di, 0x26e4
9343  1E              push ds
9344  57              push di
9345  BF 6A A9        mov di, 0xa96a
9348  1E              push ds
9349  57              push di
934A  9A 29 03 4B 21  call far 214B:0329
loc_934F:
934F  C6 06 38 7C 01  mov byte ptr [0x7c38], 1
9354  EB 16           jmp 0x936c
loc_9356:
9356  C6 06 3E 9A 01  mov byte ptr [0x9a3e], 1
935B  C6 06 3F 9A 01  mov byte ptr [0x9a3f], 1
9360  C6 06 38 7C 00  mov byte ptr [0x7c38], 0
9365  B0 00           mov al, 0
9367  50              push ax
9368  0E              push cs
9369  E8 9A 6D        call 0x10106
loc_936C:
936C  89 EC           mov sp, bp
936E  5D              pop bp
936F  C2 02 00        ret 2

; ---- routine 0791:9372  (found by: call)
sub_9372:
9372  55              push bp
9373  89 E5           mov bp, sp
9375  83 EC 02        sub sp, 2
9378  C7 46 FE 01 00  mov word ptr [bp - 2], 1
937D  EB 03           jmp 0x9382
loc_937F:
937F  FF 46 FE        inc word ptr [bp - 2]
loc_9382:
9382  C4 3E 23 A9     les di, ptr [0xa923]
9386  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
938A  30 E4           xor ah, ah
938C  8B D0           mov dx, ax
938E  B8 06 00        mov ax, 6
9391  2B C2           sub ax, dx
9393  3B 46 FE        cmp ax, word ptr [bp - 2]
9396  73 04           jae 0x939c
9398  B0 00           mov al, 0
939A  EB 02           jmp 0x939e
loc_939C:
939C  B0 01           mov al, 1
loc_939E:
939E  98              cwde
939F  8B F8           mov di, ax
93A1  8A 95 82 08     mov dl, byte ptr [di + 0x882]
93A5  8B 46 FE        mov ax, word ptr [bp - 2]
93A8  05 95 07        add ax, 0x795
93AB  D1 E0           shl ax, 1
93AD  C4 3E 26 7C     les di, ptr [0x7c26]
93B1  03 F8           add di, ax
93B3  26 88 55 FE     mov byte ptr es:[di - 2], dl
93B7  83 7E FE 06     cmp word ptr [bp - 2], 6
93BB  75 C2           jne 0x937f
93BD  9A 23 07 4B 21  call far 214B:0723
93C2  08 C0           or al, al
93C4  75 03           jne 0x93c9
93C6  E9 E5 00        jmp 0x94ae
loc_93C9:
93C9  9A 8D 1E 4B 21  call far 214B:1E8D
93CE  9A DD 08 4B 21  call far 214B:08DD
93D3  A0 76 A9        mov al, byte ptr [0xa976]
93D6  50              push ax
93D7  9A B2 19 E4 23  call far 23E4:19B2
93DC  3C 20           cmp al, 0x20
93DE  75 06           jne 0x93e6
93E0  E8 21 86        call 0x1a04
93E3  E9 C6 00        jmp 0x94ac
loc_93E6:
93E6  3C AE           cmp al, 0xae
93E8  75 16           jne 0x9400
93EA  C4 3E 23 A9     les di, ptr [0xa923]
93EE  26 80 7D 3F 05  cmp byte ptr es:[di + 0x3f], 5
93F3  73 08           jae 0x93fd
93F5  C4 3E 23 A9     les di, ptr [0xa923]
93F9  26 FE 45 3F     inc byte ptr es:[di + 0x3f]
loc_93FD:
93FD  E9 AC 00        jmp 0x94ac
loc_9400:
9400  3C AF           cmp al, 0xaf
9402  75 16           jne 0x941a
9404  C4 3E 23 A9     les di, ptr [0xa923]
9408  26 80 7D 3F 00  cmp byte ptr es:[di + 0x3f], 0
940D  76 08           jbe 0x9417
940F  C4 3E 23 A9     les di, ptr [0xa923]
9413  26 FE 4D 3F     dec byte ptr es:[di + 0x3f]
loc_9417:
9417  E9 92 00        jmp 0x94ac
loc_941A:
941A  3C AC           cmp al, 0xac
941C  74 04           je 0x9422
941E  3C B1           cmp al, 0xb1
9420  75 2B           jne 0x944d
loc_9422:
9422  BF 6A 06        mov di, 0x66a
9425  1E              push ds
9426  57              push di
9427  B0 00           mov al, 0
9429  50              push ax
942A  B0 04           mov al, 4
942C  50              push ax
942D  80 3E 76 A9 B1  cmp byte ptr [0xa976], 0xb1
9432  74 04           je 0x9438
9434  B0 00           mov al, 0
9436  EB 02           jmp 0x943a
loc_9438:
9438  B0 01           mov al, 1
loc_943A:
943A  98              cwde
943B  8B F8           mov di, ax
943D  8A 85 20 79     mov al, byte ptr [di + 0x7920]
9441  98              cwde
9442  50              push ax
9443  9A 6F 1D 4B 21  call far 214B:1D6F
9448  E8 46 72        call 0x10691
944B  EB 5F           jmp 0x94ac
loc_944D:
944D  3C 0D           cmp al, 0xd
944F  74 04           je 0x9455
9451  3C 1B           cmp al, 0x1b
9453  75 08           jne 0x945d
loc_9455:
9455  B0 01           mov al, 1
9457  50              push ax
9458  E8 2F 59        call 0xed8a
945B  EB 4F           jmp 0x94ac
loc_945D:
945D  3C 9F           cmp al, 0x9f
945F  75 38           jne 0x9499
9461  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9466  75 2F           jne 0x9497
9468  C4 3E 6A A9     les di, ptr [0xa96a]
946C  06              push es
946D  57              push di
946E  C4 3E 72 A9     les di, ptr [0xa972]
9472  06              push es
9473  57              push di
9474  B8 A0 0F        mov ax, 0xfa0
9477  50              push ax
9478  9A 5D 02 E4 23  call far 23E4:025D
947D  9A 45 09 D6 16  call far 16D6:0945
9482  C4 3E 72 A9     les di, ptr [0xa972]
9486  06              push es
9487  57              push di
9488  C4 3E 6A A9     les di, ptr [0xa96a]
948C  06              push es
948D  57              push di
948E  B8 A0 0F        mov ax, 0xfa0
9491  50              push ax
9492  9A 5D 02 E4 23  call far 23E4:025D
loc_9497:
9497  EB 13           jmp 0x94ac
loc_9499:
9499  3C A7           cmp al, 0xa7
949B  75 07           jne 0x94a4
949D  9A 5A 1E 4B 21  call far 214B:1E5A
94A2  EB 08           jmp 0x94ac
loc_94A4:
94A4  3C 52           cmp al, 0x52
94A6  75 04           jne 0x94ac
94A8  55              push bp
94A9  E8 50 FE        call 0x92fc
loc_94AC:
94AC  EB 0B           jmp 0x94b9
loc_94AE:
94AE  80 3E 38 7C 00  cmp byte ptr [0x7c38], 0
94B3  74 04           je 0x94b9
94B5  55              push bp
94B6  E8 43 FE        call 0x92fc
loc_94B9:
94B9  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
94BE  74 05           je 0x94c5
94C0  9A 8D 1E 4B 21  call far 214B:1E8D
loc_94C5:
94C5  89 EC           mov sp, bp
94C7  5D              pop bp
94C8  C3              ret

; ---- routine 0791:94C9  (found by: call)
sub_94C9:
94C9  55              push bp
94CA  89 E5           mov bp, sp
94CC  83 EC 02        sub sp, 2
94CF  BF 36 83        mov di, 0x8336
94D2  1E              push ds
94D3  57              push di
94D4  FF 76 04        push word ptr [bp + 4]
94D7  9A 88 06 4B 21  call far 214B:0688
94DC  89 46 FE        mov word ptr [bp - 2], ax
94DF  8B 46 FE        mov ax, word ptr [bp - 2]
94E2  89 EC           mov sp, bp
94E4  5D              pop bp
94E5  C2 02 00        ret 2

; ---- routine 0791:94E8  (found by: call)
sub_94E8:
94E8  55              push bp
94E9  89 E5           mov bp, sp
94EB  83 3E 2A 83 00  cmp word ptr [0x832a], 0
94F0  76 3B           jbe 0x952d
94F2  B8 32 00        mov ax, 0x32
94F5  50              push ax
94F6  E8 D0 FF        call 0x94c9
94F9  99              cdq
94FA  8B C8           mov cx, ax
94FC  8B DA           mov bx, dx
94FE  A1 2A 83        mov ax, word ptr [0x832a]
9501  31 D2           xor dx, dx
9503  3B D3           cmp dx, bx
9505  7F 06           jg 0x950d
9507  7C 24           jl 0x952d
9509  3B C1           cmp ax, cx
950B  76 20           jbe 0x952d
loc_950D:
950D  C4 3E 23 A9     les di, ptr [0xa923]
9511  26 80 7D 3F 00  cmp byte ptr es:[di + 0x3f], 0
9516  76 15           jbe 0x952d
9518  A1 2A 83        mov ax, word ptr [0x832a]
951B  05 2C 01        add ax, 0x12c
951E  50              push ax
951F  E8 A7 FF        call 0x94c9
9522  05 64 00        add ax, 0x64
9525  50              push ax
9526  9A BC 1E 4B 21  call far 214B:1EBC
952B  EB 05           jmp 0x9532
loc_952D:
952D  9A 8D 1E 4B 21  call far 214B:1E8D
loc_9532:
9532  C4 3E 23 A9     les di, ptr [0xa923]
9536  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
953A  30 E4           xor ah, ah
953C  50              push ax
953D  E8 E5 6E        call 0x10425
9540  89 EC           mov sp, bp
9542  5D              pop bp
9543  C3              ret
; data (not reached as code), 32 bytes
9544                  db 1E 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
9554                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:9564  (found by: call)
sub_9564:
9564  55              push bp
9565  89 E5           mov bp, sp
9567  83 EC 08        sub sp, 8
956A  C7 46 FE 01 00  mov word ptr [bp - 2], 1
956F  EB 03           jmp 0x9574
loc_9571:
9571  FF 46 FE        inc word ptr [bp - 2]
loc_9574:
9574  80 3E 02 83 00  cmp byte ptr [0x8302], 0
9579  75 03           jne 0x957e
957B  E9 1D 01        jmp 0x969b
loc_957E:
957E  8B 46 FE        mov ax, word ptr [bp - 2]
9581  50              push ax
9582  80 3E 03 83 00  cmp byte ptr [0x8303], 0
9587  74 10           je 0x9599
9589  A0 27 83        mov al, byte ptr [0x8327]
958C  50              push ax
958D  BF 44 95        mov di, 0x9544
9590  0E              push cs
9591  57              push di
9592  9A DF 08 E4 23  call far 23E4:08DF
9597  74 04           je 0x959d
loc_9599:
9599  B0 00           mov al, 0
959B  EB 02           jmp 0x959f
loc_959D:
959D  B0 01           mov al, 1
loc_959F:
959F  98              cwde
95A0  BA 16 00        mov dx, 0x16
95A3  F7 E2           mul dx
95A5  8B F8           mov di, ax
95A7  58              pop ax
95A8  03 F8           add di, ax
95AA  8A 85 99 08     mov al, byte ptr [di + 0x899]
95AE  30 E4           xor ah, ah
95B0  3B 06 00 83     cmp ax, word ptr [0x8300]
95B4  76 03           jbe 0x95b9
95B6  E9 E2 00        jmp 0x969b
loc_95B9:
95B9  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
95BE  74 32           je 0x95f2
95C0  BF FE 80        mov di, 0x80fe
95C3  1E              push ds
95C4  57              push di
95C5  0E              push cs
95C6  E8 1C 96        call 0x2be5
95C9  8A D0           mov dl, al
95CB  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
95D0  7F 04           jg 0x95d6
95D2  B0 00           mov al, 0
95D4  EB 02           jmp 0x95d8
loc_95D6:
95D6  B0 01           mov al, 1
loc_95D8:
95D8  98              cwde
95D9  8B F8           mov di, ax
95DB  8A 85 20 79     mov al, byte ptr [di + 0x7920]
95DF  3A C2           cmp al, dl
95E1  74 04           je 0x95e7
95E3  B0 00           mov al, 0
95E5  EB 02           jmp 0x95e9
loc_95E7:
95E7  B0 01           mov al, 1
loc_95E9:
95E9  98              cwde
95EA  8B F8           mov di, ax
95EC  D1 E7           shl di, 1
95EE  FF 85 F6 80     inc word ptr [di - 0x7f0a]
loc_95F2:
95F2  BF F6 82        mov di, 0x82f6
95F5  1E              push ds
95F6  57              push di
95F7  0E              push cs
95F8  E8 A7 ED        call 0x83a2
95FB  E8 B3 99        call 0x2fb1
95FE  E8 95 93        call 0x2996
9601  08 C0           or al, al
9603  74 04           je 0x9609
9605  B0 00           mov al, 0
9607  EB 02           jmp 0x960b
loc_9609:
9609  B0 01           mov al, 1
loc_960B:
960B  98              cwde
960C  8B F8           mov di, ax
960E  8A 85 68 06     mov al, byte ptr [di + 0x668]
9612  30 E4           xor ah, ah
9614  40              inc ax
9615  BA 16 00        mov dx, 0x16
9618  F7 E2           mul dx
961A  8B F8           mov di, ax
961C  81 C7 E8 80     add di, 0x80e8
9620  89 7E F8        mov word ptr [bp - 8], di
9623  8C 5E FA        mov word ptr [bp - 6], ds
9626  A0 27 83        mov al, byte ptr [0x8327]
9629  50              push ax
962A  BF 44 95        mov di, 0x9544
962D  0E              push cs
962E  57              push di
962F  9A DF 08 E4 23  call far 23E4:08DF
9634  74 33           je 0x9669
9636  C4 7E F8        les di, ptr [bp - 8]
9639  06              push es
963A  57              push di
963B  0E              push cs
963C  E8 AD 96        call 0x2cec
963F  08 C0           or al, al
9641  75 26           jne 0x9669
9643  C4 7E F8        les di, ptr [bp - 8]
9646  26 8A 05        mov al, byte ptr es:[di]
9649  3A 06 F6 82     cmp al, byte ptr [0x82f6]
964D  75 11           jne 0x9660
964F  FF 36 F6 82     push word ptr [0x82f6]
9653  C4 7E F8        les di, ptr [bp - 8]
9656  06              push es
9657  57              push di
9658  0E              push cs
9659  E8 DA 97        call 0x2e36
965C  08 C0           or al, al
965E  74 09           je 0x9669
loc_9660:
9660  C4 7E F8        les di, ptr [bp - 8]
9663  06              push es
9664  57              push di
9665  0E              push cs
9666  E8 80 F4        call 0x8ae9
loc_9669:
9669  E8 47 C3        call 0x59b3
966C  08 C0           or al, al
966E  75 2B           jne 0x969b
9670  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9675  EB 03           jmp 0x967a
loc_9677:
9677  FF 46 FC        inc word ptr [bp - 4]
loc_967A:
967A  80 3E 02 83 00  cmp byte ptr [0x8302], 0
967F  74 14           je 0x9695
9681  8B 46 FC        mov ax, word ptr [bp - 4]
9684  BA 16 00        mov dx, 0x16
9687  F7 E2           mul dx
9689  8B F8           mov di, ax
968B  81 C7 E8 80     add di, 0x80e8
968F  1E              push ds
9690  57              push di
9691  0E              push cs
9692  E8 F3 CA        call 0x6188
loc_9695:
9695  83 7E FC 16     cmp word ptr [bp - 4], 0x16
9699  75 DC           jne 0x9677
loc_969B:
969B  8B 7E FE        mov di, word ptr [bp - 2]
969E  8A 85 83 08     mov al, byte ptr [di + 0x883]
96A2  30 E4           xor ah, ah
96A4  BA 16 00        mov dx, 0x16
96A7  F7 E2           mul dx
96A9  8B F8           mov di, ax
96AB  81 C7 E8 80     add di, 0x80e8
96AF  89 7E F8        mov word ptr [bp - 8], di
96B2  8C 5E FA        mov word ptr [bp - 6], ds
96B5  C4 7E F8        les di, ptr [bp - 8]
96B8  06              push es
96B9  57              push di
96BA  0E              push cs
96BB  E8 98 92        call 0x2956
96BE  08 C0           or al, al
96C0  75 09           jne 0x96cb
96C2  C4 7E F8        les di, ptr [bp - 8]
96C5  06              push es
96C6  57              push di
96C7  0E              push cs
96C8  E8 1E F4        call 0x8ae9
loc_96CB:
96CB  8B 7E FE        mov di, word ptr [bp - 2]
96CE  8A 85 83 08     mov al, byte ptr [di + 0x883]
96D2  3A 06 0B 83     cmp al, byte ptr [0x830b]
96D6  75 03           jne 0x96db
96D8  E8 D6 98        call 0x2fb1
loc_96DB:
96DB  E8 0A FE        call 0x94e8
96DE  BF F6 82        mov di, 0x82f6
96E1  1E              push ds
96E2  57              push di
96E3  0E              push cs
96E4  E8 29 F8        call 0x8f10
96E7  E8 88 FC        call 0x9372
96EA  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
96EF  74 02           je 0x96f3
96F1  EB 15           jmp 0x9708
loc_96F3:
96F3  83 7E FE 16     cmp word ptr [bp - 2], 0x16
96F7  74 03           je 0x96fc
96F9  E9 75 FE        jmp 0x9571
loc_96FC:
96FC  83 3E 2A 83 00  cmp word ptr [0x832a], 0
9701  76 05           jbe 0x9708
9703  83 2E 2A 83 02  sub word ptr [0x832a], 2
loc_9708:
9708  89 EC           mov sp, bp
970A  5D              pop bp
970B  C3              ret

