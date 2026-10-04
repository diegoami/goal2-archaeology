; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 9 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:5D02  (found by: call)
sub_5D02:
5D02  55              push bp
5D03  89 E5           mov bp, sp
5D05  83 EC 08        sub sp, 8
5D08  8B 46 06        mov ax, word ptr [bp + 6]
5D0B  BA BF 00        mov dx, 0xbf
5D0E  F7 E2           mul dx
5D10  C4 3E 17 A9     les di, ptr [0xa917]
5D14  03 F8           add di, ax
5D16  89 7E FC        mov word ptr [bp - 4], di
5D19  8C 46 FE        mov word ptr [bp - 2], es
5D1C  8B 46 06        mov ax, word ptr [bp + 6]
5D1F  BA 48 00        mov dx, 0x48
5D22  F7 E2           mul dx
5D24  C4 3E 2F A9     les di, ptr [0xa92f]
5D28  03 F8           add di, ax
5D2A  81 C7 02 00     add di, 2
5D2E  06              push es
5D2F  57              push di
5D30  8B 46 06        mov ax, word ptr [bp + 6]
5D33  BA 48 00        mov dx, 0x48
5D36  F7 E2           mul dx
5D38  C4 3E 2F A9     les di, ptr [0xa92f]
5D3C  03 F8           add di, ax
5D3E  06              push es
5D3F  57              push di
5D40  B8 46 00        mov ax, 0x46
5D43  50              push ax
5D44  9A 3C 00 4B 21  call far 214B:003C
5D49  C4 3E 23 A9     les di, ptr [0xa923]
5D4D  26 8B 4D 28     mov cx, word ptr es:[di + 0x28]
5D51  8B 46 06        mov ax, word ptr [bp + 6]
5D54  BA 48 00        mov dx, 0x48
5D57  F7 E2           mul dx
5D59  C4 3E 2F A9     les di, ptr [0xa92f]
5D5D  03 F8           add di, ax
5D5F  26 89 4D 46     mov word ptr es:[di + 0x46], cx
5D63  C4 7E FC        les di, ptr [bp - 4]
5D66  81 C7 3B 00     add di, 0x3b
5D6A  89 7E F8        mov word ptr [bp - 8], di
5D6D  8C 46 FA        mov word ptr [bp - 6], es
5D70  C4 7E F8        les di, ptr [bp - 8]
5D73  26 8A 05        mov al, byte ptr es:[di]
5D76  30 E4           xor ah, ah
5D78  8B 7E 04        mov di, word ptr [bp + 4]
5D7B  36 3B 45 06     cmp ax, word ptr ss:[di + 6]
5D7F  73 0D           jae 0x5d8e
5D81  8B 7E 04        mov di, word ptr [bp + 4]
5D84  36 8A 45 06     mov al, byte ptr ss:[di + 6]
5D88  C4 7E F8        les di, ptr [bp - 8]
5D8B  26 88 05        mov byte ptr es:[di], al
loc_5D8E:
5D8E  89 EC           mov sp, bp
5D90  5D              pop bp
5D91  C2 04 00        ret 4

; ---- routine 1771:5D94  (found by: call)
sub_5D94:
5D94  55              push bp
5D95  89 E5           mov bp, sp
5D97  83 EC 06        sub sp, 6
5D9A  C4 3E 23 A9     les di, ptr [0xa923]
5D9E  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
5DA2  B1 03           mov cl, 3
5DA4  D3 E0           shl ax, cl
5DA6  C4 3E 2B A9     les di, ptr [0xa92b]
5DAA  03 F8           add di, ax
5DAC  81 C7 F8 FF     add di, 0xfff8
5DB0  89 7E FA        mov word ptr [bp - 6], di
5DB3  8C 46 FC        mov word ptr [bp - 4], es
5DB6  8B 46 0A        mov ax, word ptr [bp + 0xa]
5DB9  C4 7E FA        les di, ptr [bp - 6]
5DBC  26 89 45 06     mov word ptr es:[di + 6], ax
5DC0  FF 76 0A        push word ptr [bp + 0xa]
5DC3  55              push bp
5DC4  E8 3B FF        call 0x5d02
5DC7  8B 46 08        mov ax, word ptr [bp + 8]
5DCA  C4 7E FA        les di, ptr [bp - 6]
5DCD  26 89 45 04     mov word ptr es:[di + 4], ax
5DD1  FF 76 08        push word ptr [bp + 8]
5DD4  55              push bp
5DD5  E8 2A FF        call 0x5d02
5DD8  C4 7E FA        les di, ptr [bp - 6]
5DDB  26 C6 05 FF     mov byte ptr es:[di], 0xff
5DDF  8A 46 04        mov al, byte ptr [bp + 4]
5DE2  C4 7E FA        les di, ptr [bp - 6]
5DE5  26 88 45 01     mov byte ptr es:[di + 1], al
5DE9  C4 7E FA        les di, ptr [bp - 6]
5DEC  26 8B 45 04     mov ax, word ptr es:[di + 4]
5DF0  BA BF 00        mov dx, 0xbf
5DF3  F7 E2           mul dx
5DF5  C4 3E 17 A9     les di, ptr [0xa917]
5DF9  03 F8           add di, ax
5DFB  26 80 7D 2E 80  cmp byte ptr es:[di + 0x2e], 0x80
5E00  77 19           ja 0x5e1b
5E02  C4 7E FA        les di, ptr [bp - 6]
5E05  26 8B 45 06     mov ax, word ptr es:[di + 6]
5E09  BA BF 00        mov dx, 0xbf
5E0C  F7 E2           mul dx
5E0E  C4 3E 17 A9     les di, ptr [0xa917]
5E12  03 F8           add di, ax
5E14  26 80 7D 2E 80  cmp byte ptr es:[di + 0x2e], 0x80
5E19  76 07           jbe 0x5e22
loc_5E1B:
5E1B  C4 7E FA        les di, ptr [bp - 6]
5E1E  26 C6 05 FE     mov byte ptr es:[di], 0xfe
loc_5E22:
5E22  8A 46 06        mov al, byte ptr [bp + 6]
5E25  C4 7E FA        les di, ptr [bp - 6]
5E28  26 88 45 02     mov byte ptr es:[di + 2], al
5E2C  C4 3E 23 A9     les di, ptr [0xa923]
5E30  26 FF 45 28     inc word ptr es:[di + 0x28]
5E34  89 EC           mov sp, bp
5E36  5D              pop bp
5E37  C2 08 00        ret 8

; ---- routine 1771:5E3A  (found by: call)
sub_5E3A:
5E3A  55              push bp
5E3B  89 E5           mov bp, sp
5E3D  8B 46 0A        mov ax, word ptr [bp + 0xa]
5E40  3B 46 04        cmp ax, word ptr [bp + 4]
5E43  75 11           jne 0x5e56
5E45  FF 76 0A        push word ptr [bp + 0xa]
5E48  FF 76 0C        push word ptr [bp + 0xc]
5E4B  FF 76 08        push word ptr [bp + 8]
5E4E  FF 76 06        push word ptr [bp + 6]
5E51  E8 40 FF        call 0x5d94
5E54  EB 0F           jmp 0x5e65
loc_5E56:
5E56  FF 76 0C        push word ptr [bp + 0xc]
5E59  FF 76 0A        push word ptr [bp + 0xa]
5E5C  FF 76 08        push word ptr [bp + 8]
5E5F  FF 76 06        push word ptr [bp + 6]
5E62  E8 2F FF        call 0x5d94
loc_5E65:
5E65  83 7E 08 01     cmp word ptr [bp + 8], 1
5E69  74 28           je 0x5e93
5E6B  8B 46 0A        mov ax, word ptr [bp + 0xa]
5E6E  BA BF 00        mov dx, 0xbf
5E71  F7 E2           mul dx
5E73  C4 3E 17 A9     les di, ptr [0xa917]
5E77  03 F8           add di, ax
5E79  26 81 45 2F C8 00 add word ptr es:[di + 0x2f], 0xc8
5E7F  8B 46 0C        mov ax, word ptr [bp + 0xc]
5E82  BA BF 00        mov dx, 0xbf
5E85  F7 E2           mul dx
5E87  C4 3E 17 A9     les di, ptr [0xa917]
5E8B  03 F8           add di, ax
5E8D  26 81 45 2F C8 00 add word ptr es:[di + 0x2f], 0xc8
loc_5E93:
5E93  89 EC           mov sp, bp
5E95  5D              pop bp
5E96  C2 0A 00        ret 0xa

; ---- routine 1771:5E99  (found by: call)
sub_5E99:
5E99  55              push bp
5E9A  89 E5           mov bp, sp
5E9C  83 EC 08        sub sp, 8
5E9F  C4 3E 23 A9     les di, ptr [0xa923]
5EA3  89 7E FA        mov word ptr [bp - 6], di
5EA6  8C 46 FC        mov word ptr [bp - 4], es
5EA9  C4 7E FA        les di, ptr [bp - 6]
5EAC  26 8A 05        mov al, byte ptr es:[di]
5EAF  30 E4           xor ah, ah
5EB1  89 46 F8        mov word ptr [bp - 8], ax
5EB4  B8 01 00        mov ax, 1
5EB7  3B 46 F8        cmp ax, word ptr [bp - 8]
5EBA  77 1F           ja 0x5edb
5EBC  89 46 FE        mov word ptr [bp - 2], ax
5EBF  EB 03           jmp 0x5ec4
loc_5EC1:
5EC1  FF 46 FE        inc word ptr [bp - 2]
loc_5EC4:
5EC4  8A 56 04        mov dl, byte ptr [bp + 4]
5EC7  8B 46 FE        mov ax, word ptr [bp - 2]
5ECA  C4 7E FA        les di, ptr [bp - 6]
5ECD  03 F8           add di, ax
5ECF  26 88 55 01     mov byte ptr es:[di + 1], dl
5ED3  8B 46 FE        mov ax, word ptr [bp - 2]
5ED6  3B 46 F8        cmp ax, word ptr [bp - 8]
5ED9  75 E6           jne 0x5ec1
loc_5EDB:
5EDB  89 EC           mov sp, bp
5EDD  5D              pop bp
5EDE  C2 02 00        ret 2

; ---- routine 1771:5EE1  (found by: call)
sub_5EE1:
5EE1  55              push bp
5EE2  89 E5           mov bp, sp
5EE4  83 EC 06        sub sp, 6
5EE7  8B 46 08        mov ax, word ptr [bp + 8]
5EEA  89 46 FE        mov word ptr [bp - 2], ax
5EED  8B 46 06        mov ax, word ptr [bp + 6]
5EF0  89 46 FC        mov word ptr [bp - 4], ax
5EF3  8B 46 08        mov ax, word ptr [bp + 8]
5EF6  03 46 06        add ax, word ptr [bp + 6]
5EF9  31 D2           xor dx, dx
5EFB  B9 02 00        mov cx, 2
5EFE  F7 F1           div cx
5F00  C4 3E 56 9B     les di, ptr [0x9b56]
5F04  03 F8           add di, ax
5F06  26 8A 05        mov al, byte ptr es:[di]
5F09  30 E4           xor ah, ah
5F0B  BA BF 00        mov dx, 0xbf
5F0E  F7 E2           mul dx
5F10  C4 3E 17 A9     les di, ptr [0xa917]
5F14  03 F8           add di, ax
5F16  26 8B 45 2F     mov ax, word ptr es:[di + 0x2f]
5F1A  89 46 FA        mov word ptr [bp - 6], ax
loc_5F1D:
5F1D  8B 46 FE        mov ax, word ptr [bp - 2]
5F20  C4 3E 56 9B     les di, ptr [0x9b56]
5F24  03 F8           add di, ax
5F26  26 8A 05        mov al, byte ptr es:[di]
5F29  30 E4           xor ah, ah
5F2B  BA BF 00        mov dx, 0xbf
5F2E  F7 E2           mul dx
5F30  C4 3E 17 A9     les di, ptr [0xa917]
5F34  03 F8           add di, ax
5F36  26 8B 45 2F     mov ax, word ptr es:[di + 0x2f]
5F3A  3B 46 FA        cmp ax, word ptr [bp - 6]
5F3D  76 05           jbe 0x5f44
5F3F  FF 46 FE        inc word ptr [bp - 2]
5F42  EB D9           jmp 0x5f1d
loc_5F44:
5F44  8B 46 FC        mov ax, word ptr [bp - 4]
5F47  C4 3E 56 9B     les di, ptr [0x9b56]
5F4B  03 F8           add di, ax
5F4D  26 8A 05        mov al, byte ptr es:[di]
5F50  30 E4           xor ah, ah
5F52  BA BF 00        mov dx, 0xbf
5F55  F7 E2           mul dx
5F57  C4 3E 17 A9     les di, ptr [0xa917]
5F5B  03 F8           add di, ax
5F5D  26 8B 45 2F     mov ax, word ptr es:[di + 0x2f]
5F61  3B 46 FA        cmp ax, word ptr [bp - 6]
5F64  73 05           jae 0x5f6b
5F66  FF 4E FC        dec word ptr [bp - 4]
5F69  EB D9           jmp 0x5f44
loc_5F6B:
5F6B  8B 46 FE        mov ax, word ptr [bp - 2]
5F6E  3B 46 FC        cmp ax, word ptr [bp - 4]
5F71  77 25           ja 0x5f98
5F73  8B 46 FE        mov ax, word ptr [bp - 2]
5F76  C4 3E 56 9B     les di, ptr [0x9b56]
5F7A  03 F8           add di, ax
5F7C  06              push es
5F7D  57              push di
5F7E  8B 46 FC        mov ax, word ptr [bp - 4]
5F81  C4 3E 56 9B     les di, ptr [0x9b56]
5F85  03 F8           add di, ax
5F87  06              push es
5F88  57              push di
5F89  B8 01 00        mov ax, 1
5F8C  50              push ax
5F8D  9A 7B 00 4B 21  call far 214B:007B
5F92  FF 46 FE        inc word ptr [bp - 2]
5F95  FF 4E FC        dec word ptr [bp - 4]
loc_5F98:
5F98  8B 46 FE        mov ax, word ptr [bp - 2]
5F9B  3B 46 FC        cmp ax, word ptr [bp - 4]
5F9E  77 03           ja 0x5fa3
5FA0  E9 7A FF        jmp 0x5f1d
loc_5FA3:
5FA3  8B 46 08        mov ax, word ptr [bp + 8]
5FA6  3B 46 FC        cmp ax, word ptr [bp - 4]
5FA9  73 0C           jae 0x5fb7
5FAB  FF 76 08        push word ptr [bp + 8]
5FAE  FF 76 FC        push word ptr [bp - 4]
5FB1  FF 76 04        push word ptr [bp + 4]
5FB4  E8 2A FF        call 0x5ee1
loc_5FB7:
5FB7  8B 46 FE        mov ax, word ptr [bp - 2]
5FBA  3B 46 06        cmp ax, word ptr [bp + 6]
5FBD  73 0C           jae 0x5fcb
5FBF  FF 76 FE        push word ptr [bp - 2]
5FC2  FF 76 06        push word ptr [bp + 6]
5FC5  FF 76 04        push word ptr [bp + 4]
5FC8  E8 16 FF        call 0x5ee1
loc_5FCB:
5FCB  89 EC           mov sp, bp
5FCD  5D              pop bp
5FCE  C2 06 00        ret 6

; ---- routine 1771:5FD1  (found by: call)
sub_5FD1:
5FD1  55              push bp
5FD2  89 E5           mov bp, sp
5FD4  83 EC 08        sub sp, 8
5FD7  8B 46 0C        mov ax, word ptr [bp + 0xc]
5FDA  BA BF 00        mov dx, 0xbf
5FDD  F7 E2           mul dx
5FDF  C4 3E 17 A9     les di, ptr [0xa917]
5FE3  03 F8           add di, ax
5FE5  89 7E FC        mov word ptr [bp - 4], di
5FE8  8C 46 FE        mov word ptr [bp - 2], es
5FEB  C4 7E FC        les di, ptr [bp - 4]
5FEE  81 C7 41 00     add di, 0x41
5FF2  89 7E F8        mov word ptr [bp - 8], di
5FF5  8C 46 FA        mov word ptr [bp - 6], es
5FF8  8B 7E 08        mov di, word ptr [bp + 8]
5FFB  8A 85 FD 10     mov al, byte ptr [di + 0x10fd]
5FFF  C4 7E F8        les di, ptr [bp - 8]
6002  26 88 05        mov byte ptr es:[di], al
6005  8B 46 0A        mov ax, word ptr [bp + 0xa]
6008  C4 7E FC        les di, ptr [bp - 4]
600B  26 01 45 2F     add word ptr es:[di + 0x2f], ax
600F  8B 46 08        mov ax, word ptr [bp + 8]
6012  8B D0           mov dx, ax
6014  8A 46 06        mov al, byte ptr [bp + 6]
6017  98              cwde
6018  D1 E0           shl ax, 1
601A  D1 E0           shl ax, 1
601C  C4 7E FC        les di, ptr [bp - 4]
601F  03 F8           add di, ax
6021  03 FA           add di, dx
6023  26 FE 45 32     inc byte ptr es:[di + 0x32]
6027  89 EC           mov sp, bp
6029  5D              pop bp
602A  C2 0A 00        ret 0xa

; ---- routine 1771:602D  (found by: call)
sub_602D:
602D  55              push bp
602E  89 E5           mov bp, sp
6030  83 EC 04        sub sp, 4
6033  C4 3E 23 A9     les di, ptr [0xa923]
6037  89 7E FC        mov word ptr [bp - 4], di
603A  8C 46 FE        mov word ptr [bp - 2], es
603D  C4 7E FC        les di, ptr [bp - 4]
6040  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
6044  05 0F 00        add ax, 0xf
6047  B1 03           mov cl, 3
6049  D3 E0           shl ax, cl
604B  C4 3E 2B A9     les di, ptr [0xa92b]
604F  03 F8           add di, ax
6051  81 C7 F8 FF     add di, 0xfff8
6055  06              push es
6056  57              push di
6057  0E              push cs
6058  E8 39 FC        call 0x5c94
605B  50              push ax
605C  B8 20 03        mov ax, 0x320
605F  50              push ax
6060  B8 01 00        mov ax, 1
6063  50              push ax
6064  B0 01           mov al, 1
6066  50              push ax
6067  FF 76 04        push word ptr [bp + 4]
606A  E8 64 FF        call 0x5fd1
606D  C4 7E FC        les di, ptr [bp - 4]
6070  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
6074  05 0F 00        add ax, 0xf
6077  B1 03           mov cl, 3
6079  D3 E0           shl ax, cl
607B  C4 3E 2B A9     les di, ptr [0xa92b]
607F  03 F8           add di, ax
6081  81 C7 F8 FF     add di, 0xfff8
6085  06              push es
6086  57              push di
6087  0E              push cs
6088  E8 40 FC        call 0x5ccb
608B  50              push ax
608C  B8 58 02        mov ax, 0x258
608F  50              push ax
6090  B8 02 00        mov ax, 2
6093  50              push ax
6094  B0 01           mov al, 1
6096  50              push ax
6097  FF 76 04        push word ptr [bp + 4]
609A  E8 34 FF        call 0x5fd1
609D  C4 7E FC        les di, ptr [bp - 4]
60A0  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
60A4  05 0E 00        add ax, 0xe
60A7  B1 03           mov cl, 3
60A9  D3 E0           shl ax, cl
60AB  C4 3E 2B A9     les di, ptr [0xa92b]
60AF  03 F8           add di, ax
60B1  81 C7 F8 FF     add di, 0xfff8
60B5  06              push es
60B6  57              push di
60B7  0E              push cs
60B8  E8 D9 FB        call 0x5c94
60BB  50              push ax
60BC  B8 90 01        mov ax, 0x190
60BF  50              push ax
60C0  B8 03 00        mov ax, 3
60C3  50              push ax
60C4  B0 01           mov al, 1
60C6  50              push ax
60C7  FF 76 04        push word ptr [bp + 4]
60CA  E8 04 FF        call 0x5fd1
60CD  C4 7E FC        les di, ptr [bp - 4]
60D0  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
60D4  05 0E 00        add ax, 0xe
60D7  B1 03           mov cl, 3
60D9  D3 E0           shl ax, cl
60DB  C4 3E 2B A9     les di, ptr [0xa92b]
60DF  03 F8           add di, ax
60E1  81 C7 F8 FF     add di, 0xfff8
60E5  06              push es
60E6  57              push di
60E7  0E              push cs
60E8  E8 E0 FB        call 0x5ccb
60EB  50              push ax
60EC  B8 C8 00        mov ax, 0xc8
60EF  50              push ax
60F0  B8 04 00        mov ax, 4
60F3  50              push ax
60F4  B0 01           mov al, 1
60F6  50              push ax
60F7  FF 76 04        push word ptr [bp + 4]
60FA  E8 D4 FE        call 0x5fd1
60FD  89 EC           mov sp, bp
60FF  5D              pop bp
6100  C2 02 00        ret 2

; ---- routine 1771:6103  (found by: call)
sub_6103:
6103  55              push bp
6104  89 E5           mov bp, sp
6106  83 EC 0A        sub sp, 0xa
6109  C4 3E 23 A9     les di, ptr [0xa923]
610D  89 7E FA        mov word ptr [bp - 6], di
6110  8C 46 FC        mov word ptr [bp - 4], es
6113  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6118  EB 03           jmp 0x611d
loc_611A:
611A  FF 46 FE        inc word ptr [bp - 2]
loc_611D:
611D  8B 46 FE        mov ax, word ptr [bp - 2]
6120  BA C0 01        mov dx, 0x1c0
6123  F7 E2           mul dx
6125  C4 3E 33 A9     les di, ptr [0xa933]
6129  03 F8           add di, ax
612B  81 C7 40 05     add di, 0x540
612F  89 7E F6        mov word ptr [bp - 0xa], di
6132  8C 46 F8        mov word ptr [bp - 8], es
6135  C4 7E F6        les di, ptr [bp - 0xa]
6138  26 8B 45 32     mov ax, word ptr es:[di + 0x32]
613C  B1 03           mov cl, 3
613E  D3 E0           shl ax, cl
6140  C4 3E 2B A9     les di, ptr [0xa92b]
6144  03 F8           add di, ax
6146  81 C7 F8 FF     add di, 0xfff8
614A  06              push es
614B  57              push di
614C  0E              push cs
614D  E8 44 FB        call 0x5c94
6150  50              push ax
6151  B8 20 03        mov ax, 0x320
6154  50              push ax
6155  B8 01 00        mov ax, 1
6158  50              push ax
6159  B0 00           mov al, 0
615B  50              push ax
615C  FF 76 04        push word ptr [bp + 4]
615F  E8 6F FE        call 0x5fd1
6162  C4 7E F6        les di, ptr [bp - 0xa]
6165  26 8B 45 32     mov ax, word ptr es:[di + 0x32]
6169  B1 03           mov cl, 3
616B  D3 E0           shl ax, cl
616D  C4 3E 2B A9     les di, ptr [0xa92b]
6171  03 F8           add di, ax
6173  81 C7 F8 FF     add di, 0xfff8
6177  06              push es
6178  57              push di
6179  0E              push cs
617A  E8 4E FB        call 0x5ccb
617D  50              push ax
617E  B8 58 02        mov ax, 0x258
6181  50              push ax
6182  B8 02 00        mov ax, 2
6185  50              push ax
6186  B0 00           mov al, 0
6188  50              push ax
6189  FF 76 04        push word ptr [bp + 4]
618C  E8 42 FE        call 0x5fd1
618F  C4 7E F6        les di, ptr [bp - 0xa]
6192  26 8B 45 30     mov ax, word ptr es:[di + 0x30]
6196  B1 03           mov cl, 3
6198  D3 E0           shl ax, cl
619A  C4 3E 2B A9     les di, ptr [0xa92b]
619E  03 F8           add di, ax
61A0  81 C7 F8 FF     add di, 0xfff8
61A4  06              push es
61A5  57              push di
61A6  0E              push cs
61A7  E8 EA FA        call 0x5c94
61AA  50              push ax
61AB  B8 90 01        mov ax, 0x190
61AE  50              push ax
61AF  B8 03 00        mov ax, 3
61B2  50              push ax
61B3  B0 00           mov al, 0
61B5  50              push ax
61B6  FF 76 04        push word ptr [bp + 4]
61B9  E8 15 FE        call 0x5fd1
61BC  C4 7E F6        les di, ptr [bp - 0xa]
61BF  26 8B 45 30     mov ax, word ptr es:[di + 0x30]
61C3  B1 03           mov cl, 3
61C5  D3 E0           shl ax, cl
61C7  C4 3E 2B A9     les di, ptr [0xa92b]
61CB  03 F8           add di, ax
61CD  81 C7 F8 FF     add di, 0xfff8
61D1  06              push es
61D2  57              push di
61D3  0E              push cs
61D4  E8 F4 FA        call 0x5ccb
61D7  50              push ax
61D8  B8 C8 00        mov ax, 0xc8
61DB  50              push ax
61DC  B8 04 00        mov ax, 4
61DF  50              push ax
61E0  B0 00           mov al, 0
61E2  50              push ax
61E3  FF 76 04        push word ptr [bp + 4]
61E6  E8 E8 FD        call 0x5fd1
61E9  83 7E FE 04     cmp word ptr [bp - 2], 4
61ED  74 03           je 0x61f2
61EF  E9 28 FF        jmp 0x611a
loc_61F2:
61F2  89 EC           mov sp, bp
61F4  5D              pop bp
61F5  C2 02 00        ret 2

; ---- routine 1771:61F8  (found by: call)
sub_61F8:
61F8  55              push bp
61F9  89 E5           mov bp, sp
61FB  83 EC 12        sub sp, 0x12
61FE  C4 3E 23 A9     les di, ptr [0xa923]
6202  89 7E F6        mov word ptr [bp - 0xa], di
6205  8C 46 F8        mov word ptr [bp - 8], es
6208  C7 46 FE 01 00  mov word ptr [bp - 2], 1
620D  EB 03           jmp 0x6212
loc_620F:
620F  FF 46 FE        inc word ptr [bp - 2]
loc_6212:
6212  C7 46 FC 01 00  mov word ptr [bp - 4], 1
6217  EB 03           jmp 0x621c
loc_6219:
6219  FF 46 FC        inc word ptr [bp - 4]
loc_621C:
621C  C7 46 FA 01 00  mov word ptr [bp - 6], 1
6221  EB 03           jmp 0x6226
loc_6223:
6223  FF 46 FA        inc word ptr [bp - 6]
loc_6226:
6226  8B 46 FA        mov ax, word ptr [bp - 6]
6229  B1 03           mov cl, 3
622B  D3 E0           shl ax, cl
622D  50              push ax
622E  8B 46 FC        mov ax, word ptr [bp - 4]
6231  BA 38 00        mov dx, 0x38
6234  F7 E2           mul dx
6236  8B D8           mov bx, ax
6238  8B 46 FE        mov ax, word ptr [bp - 2]
623B  BA C0 01        mov dx, 0x1c0
623E  F7 E2           mul dx
6240  8B C8           mov cx, ax
6242  C4 7E F6        les di, ptr [bp - 0xa]
6245  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
624A  74 04           je 0x6250
624C  B0 00           mov al, 0
624E  EB 02           jmp 0x6252
loc_6250:
6250  B0 01           mov al, 1
loc_6252:
6252  98              cwde
6253  BA 00 0E        mov dx, 0xe00
6256  F7 E2           mul dx
6258  C4 3E 33 A9     les di, ptr [0xa933]
625C  03 F8           add di, ax
625E  03 F9           add di, cx
6260  03 FB           add di, bx
6262  58              pop ax
6263  03 F8           add di, ax
6265  81 C7 00 FE     add di, 0xfe00
6269  89 7E F2        mov word ptr [bp - 0xe], di
626C  8C 46 F4        mov word ptr [bp - 0xc], es
626F  B8 05 00        mov ax, 5
6272  2B 46 FE        sub ax, word ptr [bp - 2]
6275  8B D0           mov dx, ax
6277  C4 7E F2        les di, ptr [bp - 0xe]
627A  26 8A 45 07     mov al, byte ptr es:[di + 7]
627E  30 E4           xor ah, ah
6280  F7 E2           mul dx
6282  8B C8           mov cx, ax
6284  C4 7E F2        les di, ptr [bp - 0xe]
6287  26 8B 05        mov ax, word ptr es:[di]
628A  BA BF 00        mov dx, 0xbf
628D  F7 E2           mul dx
628F  C4 3E 17 A9     les di, ptr [0xa917]
6293  03 F8           add di, ax
6295  26 01 4D 2F     add word ptr es:[di + 0x2f], cx
6299  83 7E FA 04     cmp word ptr [bp - 6], 4
629D  75 84           jne 0x6223
629F  83 7E FC 08     cmp word ptr [bp - 4], 8
62A3  74 03           je 0x62a8
62A5  E9 71 FF        jmp 0x6219
loc_62A8:
62A8  83 7E FE 04     cmp word ptr [bp - 2], 4
62AC  74 03           je 0x62b1
62AE  E9 5E FF        jmp 0x620f
loc_62B1:
62B1  C4 7E F6        les di, ptr [bp - 0xa]
62B4  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
62B8  30 E4           xor ah, ah
62BA  B9 03 00        mov cx, 3
62BD  F7 E9           imul cx
62BF  40              inc ax
62C0  89 46 F4        mov word ptr [bp - 0xc], ax
62C3  B8 01 00        mov ax, 1
62C6  3B 46 F4        cmp ax, word ptr [bp - 0xc]
62C9  76 03           jbe 0x62ce
62CB  E9 D0 00        jmp 0x639e
loc_62CE:
62CE  89 46 FE        mov word ptr [bp - 2], ax
62D1  EB 03           jmp 0x62d6
loc_62D3:
62D3  FF 46 FE        inc word ptr [bp - 2]
loc_62D6:
62D6  C4 7E F6        les di, ptr [bp - 0xa]
62D9  26 80 7D 3C 02  cmp byte ptr es:[di + 0x3c], 2
62DE  74 04           je 0x62e4
62E0  B0 00           mov al, 0
62E2  EB 02           jmp 0x62e6
loc_62E4:
62E4  B0 01           mov al, 1
loc_62E6:
62E6  98              cwde
62E7  8B F8           mov di, ax
62E9  8A 85 02 11     mov al, byte ptr [di + 0x1102]
62ED  30 E4           xor ah, ah
62EF  89 46 F2        mov word ptr [bp - 0xe], ax
62F2  B8 01 00        mov ax, 1
62F5  3B 46 F2        cmp ax, word ptr [bp - 0xe]
62F8  76 03           jbe 0x62fd
62FA  E9 96 00        jmp 0x6393
loc_62FD:
62FD  89 46 FC        mov word ptr [bp - 4], ax
6300  EB 03           jmp 0x6305
loc_6302:
6302  FF 46 FC        inc word ptr [bp - 4]
loc_6305:
6305  C7 46 FA 01 00  mov word ptr [bp - 6], 1
630A  EB 03           jmp 0x630f
loc_630C:
630C  FF 46 FA        inc word ptr [bp - 6]
loc_630F:
630F  8B 46 FA        mov ax, word ptr [bp - 6]
6312  B1 03           mov cl, 3
6314  D3 E0           shl ax, cl
6316  50              push ax
6317  8B 46 FC        mov ax, word ptr [bp - 4]
631A  BA 38 00        mov dx, 0x38
631D  F7 E2           mul dx
631F  8B D8           mov bx, ax
6321  8B 46 FE        mov ax, word ptr [bp - 2]
6324  BA C0 01        mov dx, 0x1c0
6327  F7 E2           mul dx
6329  8B C8           mov cx, ax
632B  C4 7E F6        les di, ptr [bp - 0xa]
632E  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
6333  74 04           je 0x6339
6335  B0 00           mov al, 0
6337  EB 02           jmp 0x633b
loc_6339:
6339  B0 01           mov al, 1
loc_633B:
633B  98              cwde
633C  BA 00 0E        mov dx, 0xe00
633F  F7 E2           mul dx
6341  C4 3E 33 A9     les di, ptr [0xa933]
6345  03 F8           add di, ax
6347  03 F9           add di, cx
6349  03 FB           add di, bx
634B  58              pop ax
634C  03 F8           add di, ax
634E  81 C7 00 05     add di, 0x500
6352  89 7E EE        mov word ptr [bp - 0x12], di
6355  8C 46 F0        mov word ptr [bp - 0x10], es
6358  B8 05 00        mov ax, 5
635B  2B 46 FE        sub ax, word ptr [bp - 2]
635E  8B D0           mov dx, ax
6360  C4 7E EE        les di, ptr [bp - 0x12]
6363  26 8A 45 07     mov al, byte ptr es:[di + 7]
6367  30 E4           xor ah, ah
6369  F7 E2           mul dx
636B  8B C8           mov cx, ax
636D  C4 7E EE        les di, ptr [bp - 0x12]
6370  26 8B 05        mov ax, word ptr es:[di]
6373  BA BF 00        mov dx, 0xbf
6376  F7 E2           mul dx
6378  C4 3E 17 A9     les di, ptr [0xa917]
637C  03 F8           add di, ax
637E  26 01 4D 2F     add word ptr es:[di + 0x2f], cx
6382  83 7E FA 04     cmp word ptr [bp - 6], 4
6386  75 84           jne 0x630c
6388  8B 46 FC        mov ax, word ptr [bp - 4]
638B  3B 46 F2        cmp ax, word ptr [bp - 0xe]
638E  74 03           je 0x6393
6390  E9 6F FF        jmp 0x6302
loc_6393:
6393  8B 46 FE        mov ax, word ptr [bp - 2]
6396  3B 46 F4        cmp ax, word ptr [bp - 0xc]
6399  74 03           je 0x639e
639B  E9 35 FF        jmp 0x62d3
loc_639E:
639E  89 EC           mov sp, bp
63A0  5D              pop bp
63A1  C2 02 00        ret 2

; ---- routine 1771:63A4  (found by: call)
sub_63A4:
63A4  55              push bp
63A5  89 E5           mov bp, sp
63A7  83 EC 0C        sub sp, 0xc
63AA  C4 3E 23 A9     les di, ptr [0xa923]
63AE  89 7E F8        mov word ptr [bp - 8], di
63B1  8C 46 FA        mov word ptr [bp - 6], es
63B4  C4 7E F8        les di, ptr [bp - 8]
63B7  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
63BC  74 06           je 0x63c4
63BE  55              push bp
63BF  E8 41 FD        call 0x6103
63C2  EB 04           jmp 0x63c8
loc_63C4:
63C4  55              push bp
63C5  E8 65 FC        call 0x602d
loc_63C8:
63C8  55              push bp
63C9  E8 2C FE        call 0x61f8
63CC  C4 7E F8        les di, ptr [bp - 8]
63CF  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
63D4  74 0E           je 0x63e4
63D6  B8 7E 9C        mov ax, 0x9c7e
63D9  8C DA           mov dx, ds
63DB  A3 56 9B        mov word ptr [0x9b56], ax
63DE  89 16 58 9B     mov word ptr [0x9b58], dx
63E2  EB 0C           jmp 0x63f0
loc_63E4:
63E4  B8 FD 9B        mov ax, 0x9bfd
63E7  8C DA           mov dx, ds
63E9  A3 56 9B        mov word ptr [0x9b56], ax
63EC  89 16 58 9B     mov word ptr [0x9b58], dx
loc_63F0:
63F0  C4 7E F8        les di, ptr [bp - 8]
63F3  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
63F8  75 0E           jne 0x6408
63FA  B8 01 00        mov ax, 1
63FD  50              push ax
63FE  B8 80 00        mov ax, 0x80
6401  50              push ax
6402  55              push bp
6403  E8 DB FA        call 0x5ee1
6406  EB 2B           jmp 0x6433
loc_6408:
6408  C7 46 FE 01 00  mov word ptr [bp - 2], 1
640D  EB 03           jmp 0x6412
loc_640F:
640F  FF 46 FE        inc word ptr [bp - 2]
loc_6412:
6412  8B 7E FE        mov di, word ptr [bp - 2]
6415  8A 85 F9 10     mov al, byte ptr [di + 0x10f9]
6419  30 E4           xor ah, ah
641B  50              push ax
641C  8B 7E FE        mov di, word ptr [bp - 2]
641F  8A 85 F9 10     mov al, byte ptr [di + 0x10f9]
6423  30 E4           xor ah, ah
6425  05 1F 00        add ax, 0x1f
6428  50              push ax
6429  55              push bp
642A  E8 B4 FA        call 0x5ee1
642D  83 7E FE 04     cmp word ptr [bp - 2], 4
6431  75 DC           jne 0x640f
loc_6433:
6433  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6438  EB 03           jmp 0x643d
loc_643A:
643A  FF 46 FE        inc word ptr [bp - 2]
loc_643D:
643D  8B 46 FE        mov ax, word ptr [bp - 2]
6440  C4 3E 56 9B     les di, ptr [0x9b56]
6444  03 F8           add di, ax
6446  26 8A 05        mov al, byte ptr es:[di]
6449  30 E4           xor ah, ah
644B  BA BF 00        mov dx, 0xbf
644E  F7 E2           mul dx
6450  C4 3E 17 A9     les di, ptr [0xa917]
6454  03 F8           add di, ax
6456  89 7E F4        mov word ptr [bp - 0xc], di
6459  8C 46 F6        mov word ptr [bp - 0xa], es
645C  8B 46 FE        mov ax, word ptr [bp - 2]
645F  C4 3E 56 9B     les di, ptr [0x9b56]
6463  03 F8           add di, ax
6465  26 8A 05        mov al, byte ptr es:[di]
6468  30 E4           xor ah, ah
646A  50              push ax
646B  0E              push cs
646C  E8 08 A7        call 0xb77
646F  08 C0           or al, al
6471  75 03           jne 0x6476
6473  E9 94 00        jmp 0x650a
loc_6476:
6476  C4 7E F4        les di, ptr [bp - 0xc]
6479  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
647D  30 E4           xor ah, ah
647F  2D 80 00        sub ax, 0x80
6482  C4 7E F8        les di, ptr [bp - 8]
6485  03 F8           add di, ax
6487  26 8A 45 07     mov al, byte ptr es:[di + 7]
648B  C4 7E F4        les di, ptr [bp - 0xc]
648E  26 3A 45 2A     cmp al, byte ptr es:[di + 0x2a]
6492  76 1C           jbe 0x64b0
6494  C4 7E F4        les di, ptr [bp - 0xc]
6497  26 8A 55 2A     mov dl, byte ptr es:[di + 0x2a]
649B  C4 7E F4        les di, ptr [bp - 0xc]
649E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
64A2  30 E4           xor ah, ah
64A4  2D 80 00        sub ax, 0x80
64A7  C4 7E F8        les di, ptr [bp - 8]
64AA  03 F8           add di, ax
64AC  26 88 55 07     mov byte ptr es:[di + 7], dl
loc_64B0:
64B0  8B 46 FE        mov ax, word ptr [bp - 2]
64B3  C4 3E 56 9B     les di, ptr [0x9b56]
64B7  03 F8           add di, ax
64B9  26 8A 05        mov al, byte ptr es:[di]
64BC  30 E4           xor ah, ah
64BE  50              push ax
64BF  0E              push cs
64C0  E8 88 AC        call 0x114b
64C3  8B D0           mov dx, ax
64C5  C4 7E F4        les di, ptr [bp - 0xc]
64C8  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
64CC  30 E4           xor ah, ah
64CE  2D 80 00        sub ax, 0x80
64D1  C4 7E F8        les di, ptr [bp - 8]
64D4  03 F8           add di, ax
64D6  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
64DA  30 E4           xor ah, ah
64DC  3B C2           cmp ax, dx
64DE  7E 2A           jle 0x650a
64E0  8B 46 FE        mov ax, word ptr [bp - 2]
64E3  C4 3E 56 9B     les di, ptr [0x9b56]
64E7  03 F8           add di, ax
64E9  26 8A 05        mov al, byte ptr es:[di]
64EC  30 E4           xor ah, ah
64EE  50              push ax
64EF  0E              push cs
64F0  E8 58 AC        call 0x114b
64F3  8A D0           mov dl, al
64F5  C4 7E F4        les di, ptr [bp - 0xc]
64F8  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
64FC  30 E4           xor ah, ah
64FE  2D 80 00        sub ax, 0x80
6501  C4 7E F8        les di, ptr [bp - 8]
6504  03 F8           add di, ax
6506  26 88 55 0D     mov byte ptr es:[di + 0xd], dl
loc_650A:
650A  C4 7E F8        les di, ptr [bp - 8]
650D  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
6512  74 16           je 0x652a
6514  8B 46 FE        mov ax, word ptr [bp - 2]
6517  48              dec ax
6518  31 D2           xor dx, dx
651A  B9 20 00        mov cx, 0x20
651D  F7 F1           div cx
651F  92              xchg dx, ax
6520  40              inc ax
6521  C4 7E F4        les di, ptr [bp - 0xc]
6524  26 88 45 2A     mov byte ptr es:[di + 0x2a], al
6528  EB 0A           jmp 0x6534
loc_652A:
652A  8A 46 FE        mov al, byte ptr [bp - 2]
652D  C4 7E F4        les di, ptr [bp - 0xc]
6530  26 88 45 2B     mov byte ptr es:[di + 0x2b], al
loc_6534:
6534  C4 7E F4        les di, ptr [bp - 0xc]
6537  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
653B  C4 7E F4        les di, ptr [bp - 0xc]
653E  26 3A 45 29     cmp al, byte ptr es:[di + 0x29]
6542  73 10           jae 0x6554
6544  C4 7E F4        les di, ptr [bp - 0xc]
6547  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
654B  C4 7E F4        les di, ptr [bp - 0xc]
654E  26 88 45 29     mov byte ptr es:[di + 0x29], al
6552  EB 1E           jmp 0x6572
loc_6554:
6554  C4 7E F4        les di, ptr [bp - 0xc]
6557  26 8A 45 2A     mov al, byte ptr es:[di + 0x2a]
655B  C4 7E F4        les di, ptr [bp - 0xc]
655E  26 3A 45 28     cmp al, byte ptr es:[di + 0x28]
6562  73 0E           jae 0x6572
6564  C4 7E F4        les di, ptr [bp - 0xc]
6567  26 8A 45 2A     mov al, byte ptr es:[di + 0x2a]
656B  C4 7E F4        les di, ptr [bp - 0xc]
656E  26 88 45 28     mov byte ptr es:[di + 0x28], al
loc_6572:
6572  8B 46 FE        mov ax, word ptr [bp - 2]
6575  C4 3E 56 9B     les di, ptr [0x9b56]
6579  03 F8           add di, ax
657B  26 8A 05        mov al, byte ptr es:[di]
657E  30 E4           xor ah, ah
6580  50              push ax
6581  0E              push cs
6582  E8 62 AB        call 0x10e7
6585  8B C8           mov cx, ax
6587  C4 7E F4        les di, ptr [bp - 0xc]
658A  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
658E  30 E4           xor ah, ah
6590  BA 03 00        mov dx, 3
6593  F7 E2           mul dx
6595  C4 3E 1F A9     les di, ptr [0xa91f]
6599  03 F8           add di, ax
659B  26 8A 45 02     mov al, byte ptr es:[di + 2]
659F  98              cwde
65A0  03 C1           add ax, cx
65A2  89 46 FC        mov word ptr [bp - 4], ax
65A5  83 7E FC 01     cmp word ptr [bp - 4], 1
65A9  7D 07           jge 0x65b2
65AB  C7 46 FC 01 00  mov word ptr [bp - 4], 1
65B0  EB 0C           jmp 0x65be
loc_65B2:
65B2  81 7E FC 80 00  cmp word ptr [bp - 4], 0x80
65B7  7E 05           jle 0x65be
65B9  C7 46 FC 80 00  mov word ptr [bp - 4], 0x80
loc_65BE:
65BE  8A 4E FC        mov cl, byte ptr [bp - 4]
65C1  C4 7E F4        les di, ptr [bp - 0xc]
65C4  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
65C8  30 E4           xor ah, ah
65CA  BA 03 00        mov dx, 3
65CD  F7 E2           mul dx
65CF  C4 3E 1F A9     les di, ptr [0xa91f]
65D3  03 F8           add di, ax
65D5  26 88 4D 01     mov byte ptr es:[di + 1], cl
65D9  C4 7E F4        les di, ptr [bp - 0xc]
65DC  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
65E0  30 E4           xor ah, ah
65E2  BA 03 00        mov dx, 3
65E5  F7 E2           mul dx
65E7  C4 3E 1F A9     les di, ptr [0xa91f]
65EB  03 F8           add di, ax
65ED  26 C6 45 02 00  mov byte ptr es:[di + 2], 0
65F2  C4 7E F4        les di, ptr [bp - 0xc]
65F5  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
65F9  30 E4           xor ah, ah
65FB  8B D0           mov dx, ax
65FD  B8 05 00        mov ax, 5
6600  2B C2           sub ax, dx
6602  C4 7E F4        les di, ptr [bp - 0xc]
6605  26 89 45 2F     mov word ptr es:[di + 0x2f], ax
6609  81 7E FE 80 00  cmp word ptr [bp - 2], 0x80
660E  74 03           je 0x6613
6610  E9 27 FE        jmp 0x643a
loc_6613:
6613  89 EC           mov sp, bp
6615  5D              pop bp
6616  C3              ret

; ---- routine 1771:6617  (found by: call)
sub_6617:
6617  55              push bp
6618  89 E5           mov bp, sp
661A  83 EC 0E        sub sp, 0xe
661D  C4 3E 23 A9     les di, ptr [0xa923]
6621  89 7E F6        mov word ptr [bp - 0xa], di
6624  8C 46 F8        mov word ptr [bp - 8], es
6627  C4 7E F6        les di, ptr [bp - 0xa]
662A  26 8A 05        mov al, byte ptr es:[di]
662D  30 E4           xor ah, ah
662F  89 46 F4        mov word ptr [bp - 0xc], ax
6632  B8 01 00        mov ax, 1
6635  3B 46 F4        cmp ax, word ptr [bp - 0xc]
6638  76 03           jbe 0x663d
663A  E9 ED 00        jmp 0x672a
loc_663D:
663D  89 46 FC        mov word ptr [bp - 4], ax
6640  EB 03           jmp 0x6645
loc_6642:
6642  FF 46 FC        inc word ptr [bp - 4]
loc_6645:
6645  8B 46 FC        mov ax, word ptr [bp - 4]
6648  C4 7E F6        les di, ptr [bp - 0xa]
664B  03 F8           add di, ax
664D  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
6652  75 03           jne 0x6657
6654  E9 C8 00        jmp 0x671f
loc_6657:
6657  80 7E 04 00     cmp byte ptr [bp + 4], 0
665B  74 11           je 0x666e
665D  C4 7E F6        les di, ptr [bp - 0xa]
6660  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
6665  74 07           je 0x666e
6667  C7 46 FA 01 00  mov word ptr [bp - 6], 1
666C  EB 2A           jmp 0x6698
loc_666E:
666E  8B 46 FC        mov ax, word ptr [bp - 4]
6671  05 80 00        add ax, 0x80
6674  BA 03 00        mov dx, 3
6677  F7 E2           mul dx
6679  C4 3E 1F A9     les di, ptr [0xa91f]
667D  03 F8           add di, ax
667F  26 8A 05        mov al, byte ptr es:[di]
6682  30 E4           xor ah, ah
6684  BA BF 00        mov dx, 0xbf
6687  F7 E2           mul dx
6689  C4 3E 17 A9     les di, ptr [0xa917]
668D  03 F8           add di, ax
668F  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
6693  30 E4           xor ah, ah
6695  89 46 FA        mov word ptr [bp - 6], ax
loc_6698:
6698  8A 46 04        mov al, byte ptr [bp + 4]
669B  98              cwde
669C  8B F8           mov di, ax
669E  8A 85 04 11     mov al, byte ptr [di + 0x1104]
66A2  30 E4           xor ah, ah
66A4  89 46 F2        mov word ptr [bp - 0xe], ax
66A7  B8 01 00        mov ax, 1
66AA  3B 46 F2        cmp ax, word ptr [bp - 0xe]
66AD  77 70           ja 0x671f
66AF  89 46 FE        mov word ptr [bp - 2], ax
66B2  EB 03           jmp 0x66b7
loc_66B4:
66B4  FF 46 FE        inc word ptr [bp - 2]
loc_66B7:
66B7  8B 46 FE        mov ax, word ptr [bp - 2]
66BA  D1 E0           shl ax, 1
66BC  50              push ax
66BD  8B 46 FC        mov ax, word ptr [bp - 4]
66C0  C4 7E F6        les di, ptr [bp - 0xa]
66C3  03 F8           add di, ax
66C5  26 8A 45 01     mov al, byte ptr es:[di + 1]
66C9  30 E4           xor ah, ah
66CB  BA 38 00        mov dx, 0x38
66CE  F7 E2           mul dx
66D0  50              push ax
66D1  8B 46 FA        mov ax, word ptr [bp - 6]
66D4  BA C0 01        mov dx, 0x1c0
66D7  F7 E2           mul dx
66D9  8B D8           mov bx, ax
66DB  8A 46 04        mov al, byte ptr [bp + 4]
66DE  98              cwde
66DF  BA 00 07        mov dx, 0x700
66E2  F7 E2           mul dx
66E4  8B C8           mov cx, ax
66E6  C4 7E F6        les di, ptr [bp - 0xa]
66E9  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
66ED  98              cwde
66EE  BA 00 0E        mov dx, 0xe00
66F1  F7 E2           mul dx
66F3  C4 3E 33 A9     les di, ptr [0xa933]
66F7  03 F8           add di, ax
66F9  03 F9           add di, cx
66FB  03 FB           add di, bx
66FD  58              pop ax
66FE  03 F8           add di, ax
6700  58              pop ax
6701  03 F8           add di, ax
6703  26 8B 85 26 FE  mov ax, word ptr es:[di - 0x1da]
6708  B1 03           mov cl, 3
670A  D3 E0           shl ax, cl
670C  C4 3E 2B A9     les di, ptr [0xa92b]
6710  03 F8           add di, ax
6712  26 C6 45 F8 FE  mov byte ptr es:[di - 8], 0xfe
6717  8B 46 FE        mov ax, word ptr [bp - 2]
671A  3B 46 F2        cmp ax, word ptr [bp - 0xe]
671D  75 95           jne 0x66b4
loc_671F:
671F  8B 46 FC        mov ax, word ptr [bp - 4]
6722  3B 46 F4        cmp ax, word ptr [bp - 0xc]
6725  74 03           je 0x672a
6727  E9 18 FF        jmp 0x6642
loc_672A:
672A  89 EC           mov sp, bp
672C  5D              pop bp
672D  C2 02 00        ret 2

; ---- routine 1771:6730  (found by: call)
sub_6730:
6730  55              push bp
6731  89 E5           mov bp, sp
6733  83 EC 18        sub sp, 0x18
6736  C4 3E 23 A9     les di, ptr [0xa923]
673A  89 7E F0        mov word ptr [bp - 0x10], di
673D  8C 46 F2        mov word ptr [bp - 0xe], es
6740  C4 7E F0        les di, ptr [bp - 0x10]
6743  81 C7 14 00     add di, 0x14
6747  06              push es
6748  57              push di
6749  B8 06 00        mov ax, 6
674C  50              push ax
674D  31 C0           xor ax, ax
674F  50              push ax
6750  9A 18 00 4B 21  call far 214B:0018
6755  E8 A7 EF        call 0x56ff
6758  C4 7E F0        les di, ptr [bp - 0x10]
675B  26 83 7D 38 00  cmp word ptr es:[di + 0x38], 0
6760  76 05           jbe 0x6767
6762  E8 3F FC        call 0x63a4
6765  EB 41           jmp 0x67a8
loc_6767:
6767  C7 46 FA 01 00  mov word ptr [bp - 6], 1
676C  EB 03           jmp 0x6771
loc_676E:
676E  FF 46 FA        inc word ptr [bp - 6]
loc_6771:
6771  8B 46 FA        mov ax, word ptr [bp - 6]
6774  BA BF 00        mov dx, 0xbf
6777  F7 E2           mul dx
6779  C4 3E 17 A9     les di, ptr [0xa917]
677D  03 F8           add di, ax
677F  89 7E EC        mov word ptr [bp - 0x14], di
6782  8C 46 EE        mov word ptr [bp - 0x12], es
6785  C4 7E EC        les di, ptr [bp - 0x14]
6788  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
678C  30 E4           xor ah, ah
678E  8B D0           mov dx, ax
6790  B8 05 00        mov ax, 5
6793  2B C2           sub ax, dx
6795  C4 7E EC        les di, ptr [bp - 0x14]
6798  26 89 45 2F     mov word ptr es:[di + 0x2f], ax
679C  81 7E FA 80 00  cmp word ptr [bp - 6], 0x80
67A1  75 CB           jne 0x676e
67A3  9A D7 11 E4 23  call far 23E4:11D7
loc_67A8:
67A8  C4 7E F0        les di, ptr [bp - 0x10]
67AB  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
67AF  98              cwde
67B0  8B F8           mov di, ax
67B2  D1 E7           shl di, 1
67B4  8B 85 36 69     mov ax, word ptr [di + 0x6936]
67B8  C4 7E F0        les di, ptr [bp - 0x10]
67BB  26 89 45 28     mov word ptr es:[di + 0x28], ax
67BF  C4 7E F0        les di, ptr [bp - 0x10]
67C2  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
67C6  C4 7E F0        les di, ptr [bp - 0x10]
67C9  26 89 45 26     mov word ptr es:[di + 0x26], ax
67CD  C4 7E F0        les di, ptr [bp - 0x10]
67D0  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
67D4  98              cwde
67D5  BA 00 0E        mov dx, 0xe00
67D8  F7 E2           mul dx
67DA  C4 3E 33 A9     les di, ptr [0xa933]
67DE  03 F8           add di, ax
67E0  06              push es
67E1  57              push di
67E2  B8 00 0E        mov ax, 0xe00
67E5  50              push ax
67E6  31 C0           xor ax, ax
67E8  50              push ax
67E9  9A 18 00 4B 21  call far 214B:0018
67EE  B8 01 00        mov ax, 1
67F1  50              push ax
67F2  E8 A4 F6        call 0x5e99
67F5  31 C0           xor ax, ax
67F7  89 46 F4        mov word ptr [bp - 0xc], ax
loc_67FA:
67FA  C7 46 FE 01 00  mov word ptr [bp - 2], 1
67FF  EB 03           jmp 0x6804
loc_6801:
6801  FF 46 FE        inc word ptr [bp - 2]
loc_6804:
6804  B8 08 00        mov ax, 8
6807  50              push ax
6808  9A B1 06 4B 21  call far 214B:06B1
680D  99              cdq
680E  8B C8           mov cx, ax
6810  8B DA           mov bx, dx
6812  8B 46 F4        mov ax, word ptr [bp - 0xc]
6815  31 D2           xor dx, dx
6817  03 C1           add ax, cx
6819  13 D3           adc dx, bx
681B  8B F8           mov di, ax
681D  81 C7 FF 9C     add di, 0x9cff
6821  1E              push ds
6822  57              push di
6823  B8 08 00        mov ax, 8
6826  50              push ax
6827  9A B1 06 4B 21  call far 214B:06B1
682C  99              cdq
682D  8B C8           mov cx, ax
682F  8B DA           mov bx, dx
6831  8B 46 F4        mov ax, word ptr [bp - 0xc]
6834  31 D2           xor dx, dx
6836  03 C1           add ax, cx
6838  13 D3           adc dx, bx
683A  8B F8           mov di, ax
683C  81 C7 FF 9C     add di, 0x9cff
6840  1E              push ds
6841  57              push di
6842  B8 01 00        mov ax, 1
6845  50              push ax
6846  9A 7B 00 4B 21  call far 214B:007B
684B  83 7E FE 04     cmp word ptr [bp - 2], 4
684F  75 B0           jne 0x6801
6851  83 46 F4 08     add word ptr [bp - 0xc], 8
6855  81 7E F4 80 00  cmp word ptr [bp - 0xc], 0x80
685A  75 9E           jne 0x67fa
685C  C4 7E F0        les di, ptr [bp - 0x10]
685F  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
6864  74 0B           je 0x6871
6866  C4 7E F0        les di, ptr [bp - 0x10]
6869  31 C0           xor ax, ax
686B  26 89 45 36     mov word ptr es:[di + 0x36], ax
686F  EB 20           jmp 0x6891
loc_6871:
6871  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6876  EB 03           jmp 0x687b
loc_6878:
6878  FF 46 FE        inc word ptr [bp - 2]
loc_687B:
687B  8B 46 FE        mov ax, word ptr [bp - 2]
687E  D1 E0           shl ax, 1
6880  C4 7E F0        les di, ptr [bp - 0x10]
6883  03 F8           add di, ax
6885  31 C0           xor ax, ax
6887  26 89 45 2C     mov word ptr es:[di + 0x2c], ax
688B  83 7E FE 04     cmp word ptr [bp - 2], 4
688F  75 E7           jne 0x6878
loc_6891:
6891  C4 7E F0        les di, ptr [bp - 0x10]
6894  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
6899  74 18           je 0x68b3
689B  C4 3E 3F A9     les di, ptr [0xa93f]
689F  81 C7 80 01     add di, 0x180
68A3  06              push es
68A4  57              push di
68A5  B8 60 00        mov ax, 0x60
68A8  50              push ax
68A9  31 C0           xor ax, ax
68AB  50              push ax
68AC  9A 18 00 4B 21  call far 214B:0018
68B1  EB 12           jmp 0x68c5
loc_68B3:
68B3  C4 3E 3F A9     les di, ptr [0xa93f]
68B7  06              push es
68B8  57              push di
68B9  B8 80 01        mov ax, 0x180
68BC  50              push ax
68BD  31 C0           xor ax, ax
68BF  50              push ax
68C0  9A 18 00 4B 21  call far 214B:0018
loc_68C5:
68C5  C7 46 FE 01 00  mov word ptr [bp - 2], 1
68CA  EB 03           jmp 0x68cf
loc_68CC:
68CC  FF 46 FE        inc word ptr [bp - 2]
loc_68CF:
68CF  C7 46 FA 01 00  mov word ptr [bp - 6], 1
68D4  EB 03           jmp 0x68d9
loc_68D6:
68D6  FF 46 FA        inc word ptr [bp - 6]
loc_68D9:
68D9  B8 04 00        mov ax, 4
68DC  50              push ax
68DD  9A B1 06 4B 21  call far 214B:06B1
68E2  89 46 F6        mov word ptr [bp - 0xa], ax
68E5  C7 46 F8 01 00  mov word ptr [bp - 8], 1
68EA  EB 03           jmp 0x68ef
loc_68EC:
68EC  FF 46 F8        inc word ptr [bp - 8]
loc_68EF:
68EF  8B 46 F8        mov ax, word ptr [bp - 8]
68F2  8B 7E F6        mov di, word ptr [bp - 0xa]
68F5  D1 E7           shl di, 1
68F7  D1 E7           shl di, 1
68F9  03 F8           add di, ax
68FB  8A 85 71 0F     mov al, byte ptr [di + 0xf71]
68FF  30 E4           xor ah, ah
6901  B1 03           mov cl, 3
6903  D3 E0           shl ax, cl
6905  50              push ax
6906  8B 46 FA        mov ax, word ptr [bp - 6]
6909  BA 38 00        mov dx, 0x38
690C  F7 E2           mul dx
690E  8B D8           mov bx, ax
6910  8B 46 FE        mov ax, word ptr [bp - 2]
6913  BA C0 01        mov dx, 0x1c0
6916  F7 E2           mul dx
6918  8B C8           mov cx, ax
691A  C4 7E F0        les di, ptr [bp - 0x10]
691D  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
6921  98              cwde
6922  BA 00 0E        mov dx, 0xe00
6925  F7 E2           mul dx
6927  C4 3E 33 A9     les di, ptr [0xa933]
692B  03 F8           add di, ax
692D  03 F9           add di, cx
692F  03 FB           add di, bx
6931  58              pop ax
6932  03 F8           add di, ax
6934  81 C7 00 FE     add di, 0xfe00
6938  89 7E EC        mov word ptr [bp - 0x14], di
693B  8C 46 EE        mov word ptr [bp - 0x12], es
693E  FF 76 FE        push word ptr [bp - 2]
6941  E8 A0 ED        call 0x56e4
6944  8B D0           mov dx, ax
6946  8B 46 F8        mov ax, word ptr [bp - 8]
6949  48              dec ax
694A  B9 03 00        mov cx, 3
694D  D3 E0           shl ax, cl
694F  03 C2           add ax, dx
6951  03 46 FA        add ax, word ptr [bp - 6]
6954  8B F8           mov di, ax
6956  8A 85 FF 9C     mov al, byte ptr [di - 0x6301]
695A  30 E4           xor ah, ah
695C  C4 7E EC        les di, ptr [bp - 0x14]
695F  26 89 05        mov word ptr es:[di], ax
6962  C4 7E EC        les di, ptr [bp - 0x14]
6965  26 8B 05        mov ax, word ptr es:[di]
6968  BA BF 00        mov dx, 0xbf
696B  F7 E2           mul dx
696D  C4 3E 17 A9     les di, ptr [0xa917]
6971  03 F8           add di, ax
6973  89 7E E8        mov word ptr [bp - 0x18], di
6976  8C 46 EA        mov word ptr [bp - 0x16], es
6979  C4 7E E8        les di, ptr [bp - 0x18]
697C  26 80 7D 2E 80  cmp byte ptr es:[di + 0x2e], 0x80
6981  76 18           jbe 0x699b
6983  8A 56 FA        mov dl, byte ptr [bp - 6]
6986  C4 7E E8        les di, ptr [bp - 0x18]
6989  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
698D  30 E4           xor ah, ah
698F  2D 80 00        sub ax, 0x80
6992  C4 7E F0        les di, ptr [bp - 0x10]
6995  03 F8           add di, ax
6997  26 88 55 01     mov byte ptr es:[di + 1], dl
loc_699B:
699B  83 7E F8 04     cmp word ptr [bp - 8], 4
699F  74 03           je 0x69a4
69A1  E9 48 FF        jmp 0x68ec
loc_69A4:
69A4  83 7E FA 08     cmp word ptr [bp - 6], 8
69A8  74 03           je 0x69ad
69AA  E9 29 FF        jmp 0x68d6
loc_69AD:
69AD  83 7E FE 04     cmp word ptr [bp - 2], 4
69B1  74 03           je 0x69b6
69B3  E9 16 FF        jmp 0x68cc
loc_69B6:
69B6  C7 46 FA 01 00  mov word ptr [bp - 6], 1
69BB  EB 03           jmp 0x69c0
loc_69BD:
69BD  FF 46 FA        inc word ptr [bp - 6]
loc_69C0:
69C0  C7 46 FE 01 00  mov word ptr [bp - 2], 1
69C5  EB 03           jmp 0x69ca
loc_69C7:
69C7  FF 46 FE        inc word ptr [bp - 2]
loc_69CA:
69CA  C7 46 FC 01 00  mov word ptr [bp - 4], 1
69CF  EB 03           jmp 0x69d4
loc_69D1:
69D1  FF 46 FC        inc word ptr [bp - 4]
loc_69D4:
69D4  8B 46 FC        mov ax, word ptr [bp - 4]
69D7  BA 38 00        mov dx, 0x38
69DA  F7 E2           mul dx
69DC  8B D8           mov bx, ax
69DE  8B 46 FE        mov ax, word ptr [bp - 2]
69E1  BA C0 01        mov dx, 0x1c0
69E4  F7 E2           mul dx
69E6  8B C8           mov cx, ax
69E8  C4 7E F0        les di, ptr [bp - 0x10]
69EB  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
69EF  98              cwde
69F0  BA 00 0E        mov dx, 0xe00
69F3  F7 E2           mul dx
69F5  C4 3E 33 A9     les di, ptr [0xa933]
69F9  03 F8           add di, ax
69FB  03 F9           add di, cx
69FD  03 FB           add di, bx
69FF  81 C7 08 FE     add di, 0xfe08
6A03  89 7E EC        mov word ptr [bp - 0x14], di
6A06  8C 46 EE        mov word ptr [bp - 0x12], es
6A09  C4 7E F0        les di, ptr [bp - 0x10]
6A0C  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
6A11  74 04           je 0x6a17
6A13  B0 00           mov al, 0
6A15  EB 02           jmp 0x6a19
loc_6A17:
6A17  B0 01           mov al, 1
loc_6A19:
6A19  98              cwde
6A1A  8B F8           mov di, ax
6A1C  8A 85 06 11     mov al, byte ptr [di + 0x1106]
6A20  30 E4           xor ah, ah
6A22  3B 46 FA        cmp ax, word ptr [bp - 6]
6A25  77 03           ja 0x6a2a
6A27  E9 8F 00        jmp 0x6ab9
loc_6A2A:
6A2A  8B 46 FA        mov ax, word ptr [bp - 6]
6A2D  8B 7E FC        mov di, word ptr [bp - 4]
6A30  D1 E7           shl di, 1
6A32  8B F7           mov si, di
6A34  D1 E7           shl di, 1
6A36  03 FE           add di, si
6A38  03 F8           add di, ax
6A3A  80 BD 87 10 00  cmp byte ptr [di + 0x1087], 0
6A3F  76 78           jbe 0x6ab9
6A41  C7 46 F8 01 00  mov word ptr [bp - 8], 1
6A46  EB 03           jmp 0x6a4b
loc_6A48:
6A48  FF 46 F8        inc word ptr [bp - 8]
loc_6A4B:
6A4B  8B 46 F8        mov ax, word ptr [bp - 8]
6A4E  B1 03           mov cl, 3
6A50  D3 E0           shl ax, cl
6A52  C4 7E EC        les di, ptr [bp - 0x14]
6A55  03 F8           add di, ax
6A57  26 FF 75 F8     push word ptr es:[di - 8]
6A5B  8B 46 F8        mov ax, word ptr [bp - 8]
6A5E  B1 03           mov cl, 3
6A60  D3 E0           shl ax, cl
6A62  50              push ax
6A63  8B 46 FA        mov ax, word ptr [bp - 6]
6A66  8B 7E FC        mov di, word ptr [bp - 4]
6A69  D1 E7           shl di, 1
6A6B  8B F7           mov si, di
6A6D  D1 E7           shl di, 1
6A6F  03 FE           add di, si
6A71  03 F8           add di, ax
6A73  8A 85 87 10     mov al, byte ptr [di + 0x1087]
6A77  30 E4           xor ah, ah
6A79  BA 38 00        mov dx, 0x38
6A7C  F7 E2           mul dx
6A7E  8B D8           mov bx, ax
6A80  8B 46 FE        mov ax, word ptr [bp - 2]
6A83  BA C0 01        mov dx, 0x1c0
6A86  F7 E2           mul dx
6A88  8B C8           mov cx, ax
6A8A  C4 7E F0        les di, ptr [bp - 0x10]
6A8D  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
6A91  98              cwde
6A92  BA 00 0E        mov dx, 0xe00
6A95  F7 E2           mul dx
6A97  C4 3E 33 A9     les di, ptr [0xa933]
6A9B  03 F8           add di, ax
6A9D  03 F9           add di, cx
6A9F  03 FB           add di, bx
6AA1  58              pop ax
6AA2  03 F8           add di, ax
6AA4  26 FF B5 00 FE  push word ptr es:[di - 0x200]
6AA9  B8 01 00        mov ax, 1
6AAC  50              push ax
6AAD  31 C0           xor ax, ax
6AAF  50              push ax
6AB0  E8 E1 F2        call 0x5d94
6AB3  83 7E F8 04     cmp word ptr [bp - 8], 4
6AB7  75 8F           jne 0x6a48
loc_6AB9:
6AB9  C4 7E F0        les di, ptr [bp - 0x10]
6ABC  26 8B 55 28     mov dx, word ptr es:[di + 0x28]
6AC0  8B 46 FA        mov ax, word ptr [bp - 6]
6AC3  D1 E0           shl ax, 1
6AC5  C4 7E EC        les di, ptr [bp - 0x14]
6AC8  03 F8           add di, ax
6ACA  26 89 55 1E     mov word ptr es:[di + 0x1e], dx
6ACE  8B 46 FA        mov ax, word ptr [bp - 6]
6AD1  D1 E0           shl ax, 1
6AD3  8B C8           mov cx, ax
6AD5  8B 46 FC        mov ax, word ptr [bp - 4]
6AD8  03 46 FE        add ax, word ptr [bp - 2]
6ADB  BA 18 00        mov dx, 0x18
6ADE  F7 E2           mul dx
6AE0  8B F8           mov di, ax
6AE2  03 F9           add di, cx
6AE4  8A 85 55 0F     mov al, byte ptr [di + 0xf55]
6AE8  30 E4           xor ah, ah
6AEA  B1 03           mov cl, 3
6AEC  D3 E0           shl ax, cl
6AEE  C4 7E EC        les di, ptr [bp - 0x14]
6AF1  03 F8           add di, ax
6AF3  26 FF 75 F8     push word ptr es:[di - 8]
6AF7  8B 46 FA        mov ax, word ptr [bp - 6]
6AFA  D1 E0           shl ax, 1
6AFC  8B C8           mov cx, ax
6AFE  8B 46 FC        mov ax, word ptr [bp - 4]
6B01  03 46 FE        add ax, word ptr [bp - 2]
6B04  BA 18 00        mov dx, 0x18
6B07  F7 E2           mul dx
6B09  8B F8           mov di, ax
6B0B  03 F9           add di, cx
6B0D  8A 85 54 0F     mov al, byte ptr [di + 0xf54]
6B11  30 E4           xor ah, ah
6B13  B1 03           mov cl, 3
6B15  D3 E0           shl ax, cl
6B17  C4 7E EC        les di, ptr [bp - 0x14]
6B1A  03 F8           add di, ax
6B1C  26 FF 75 F8     push word ptr es:[di - 8]
6B20  C4 7E F0        les di, ptr [bp - 0x10]
6B23  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
6B27  30 E4           xor ah, ah
6B29  50              push ax
6B2A  FF 76 FC        push word ptr [bp - 4]
6B2D  E8 64 F2        call 0x5d94
6B30  83 7E FC 08     cmp word ptr [bp - 4], 8
6B34  74 03           je 0x6b39
6B36  E9 98 FE        jmp 0x69d1
loc_6B39:
6B39  83 7E FE 04     cmp word ptr [bp - 2], 4
6B3D  74 03           je 0x6b42
6B3F  E9 85 FE        jmp 0x69c7
loc_6B42:
6B42  83 7E FA 0C     cmp word ptr [bp - 6], 0xc
6B46  74 03           je 0x6b4b
6B48  E9 72 FE        jmp 0x69bd
loc_6B4B:
6B4B  B0 00           mov al, 0
6B4D  50              push ax
6B4E  E8 C6 FA        call 0x6617
6B51  89 EC           mov sp, bp
6B53  5D              pop bp
6B54  C3              ret

