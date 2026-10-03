; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 13 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:8CA2  (found by: call)
sub_8CA2:
8CA2  55              push bp
8CA3  89 E5           mov bp, sp
8CA5  83 7E 0A 00     cmp word ptr [bp + 0xa], 0
8CA9  76 1C           jbe 0x8cc7
8CAB  8B 46 0A        mov ax, word ptr [bp + 0xa]
8CAE  B1 03           mov cl, 3
8CB0  D3 E0           shl ax, cl
8CB2  C4 3E 2B A9     les di, ptr [0xa92b]
8CB6  03 F8           add di, ax
8CB8  81 C7 F8 FF     add di, 0xfff8
8CBC  06              push es
8CBD  57              push di
8CBE  FF 76 08        push word ptr [bp + 8]
8CC1  FF 76 06        push word ptr [bp + 6]
8CC4  E8 FC EA        call 0x77c3
loc_8CC7:
8CC7  89 EC           mov sp, bp
8CC9  5D              pop bp
8CCA  C2 08 00        ret 8
; data (not reached as code), 2 bytes
8CCD                  db 01 3C   ; .<

; ---- routine 1771:8CCF  (found by: call)
sub_8CCF:
8CCF  55              push bp
8CD0  89 E5           mov bp, sp
8CD2  83 EC 04        sub sp, 4
8CD5  83 7E 0E 00     cmp word ptr [bp + 0xe], 0
8CD9  77 03           ja 0x8cde
8CDB  E9 A0 00        jmp 0x8d7e
loc_8CDE:
8CDE  8B 46 0E        mov ax, word ptr [bp + 0xe]
8CE1  B1 03           mov cl, 3
8CE3  D3 E0           shl ax, cl
8CE5  C4 3E 2B A9     les di, ptr [0xa92b]
8CE9  03 F8           add di, ax
8CEB  81 C7 F8 FF     add di, 0xfff8
8CEF  89 7E FC        mov word ptr [bp - 4], di
8CF2  8C 46 FE        mov word ptr [bp - 2], es
8CF5  C4 7E FC        les di, ptr [bp - 4]
8CF8  26 FF 75 06     push word ptr es:[di + 6]
8CFC  FF 76 0C        push word ptr [bp + 0xc]
8CFF  8B 46 0A        mov ax, word ptr [bp + 0xa]
8D02  05 0E 00        add ax, 0xe
8D05  50              push ax
8D06  E8 A8 82        call 0xfb1
8D09  C4 7E FC        les di, ptr [bp - 4]
8D0C  26 FF 75 04     push word ptr es:[di + 4]
8D10  8B 46 0C        mov ax, word ptr [bp + 0xc]
8D13  40              inc ax
8D14  50              push ax
8D15  8B 46 0A        mov ax, word ptr [bp + 0xa]
8D18  05 0E 00        add ax, 0xe
8D1B  50              push ax
8D1C  E8 92 82        call 0xfb1
8D1F  8B 46 0E        mov ax, word ptr [bp + 0xe]
8D22  B1 03           mov cl, 3
8D24  D3 E0           shl ax, cl
8D26  C4 3E 2B A9     les di, ptr [0xa92b]
8D2A  03 F8           add di, ax
8D2C  81 C7 F8 FF     add di, 0xfff8
8D30  06              push es
8D31  57              push di
8D32  FF 76 08        push word ptr [bp + 8]
8D35  FF 76 06        push word ptr [bp + 6]
8D38  0E              push cs
8D39  E8 BE E9        call 0x76fa
8D3C  C4 7E FC        les di, ptr [bp - 4]
8D3F  26 80 3D FE     cmp byte ptr es:[di], 0xfe
8D43  73 39           jae 0x8d7e
8D45  C4 7E FC        les di, ptr [bp - 4]
8D48  26 80 7D 02 06  cmp byte ptr es:[di + 2], 6
8D4D  74 2F           je 0x8d7e
8D4F  B0 06           mov al, 6
8D51  50              push ax
8D52  BF CD 8C        mov di, 0x8ccd
8D55  0E              push cs
8D56  57              push di
8D57  C4 7E FC        les di, ptr [bp - 4]
8D5A  26 80 7D 03 00  cmp byte ptr es:[di + 3], 0
8D5F  74 04           je 0x8d65
8D61  B0 00           mov al, 0
8D63  EB 02           jmp 0x8d67
loc_8D65:
8D65  B0 01           mov al, 1
loc_8D67:
8D67  30 E4           xor ah, ah
8D69  03 46 0C        add ax, word ptr [bp + 0xc]
8D6C  50              push ax
8D6D  8B 46 0A        mov ax, word ptr [bp + 0xa]
8D70  05 0F 00        add ax, 0xf
8D73  50              push ax
8D74  BF 6E A9        mov di, 0xa96e
8D77  1E              push ds
8D78  57              push di
8D79  9A C8 02 4B 21  call far 214B:02C8
loc_8D7E:
8D7E  89 EC           mov sp, bp
8D80  5D              pop bp
8D81  C2 0C 00        ret 0xc

; ---- routine 1771:8D84  (found by: call)
sub_8D84:
8D84  55              push bp
8D85  89 E5           mov bp, sp
8D87  83 EC 0C        sub sp, 0xc
8D8A  C4 3E 23 A9     les di, ptr [0xa923]
8D8E  89 7E F8        mov word ptr [bp - 8], di
8D91  8C 46 FA        mov word ptr [bp - 6], es
8D94  C4 7E F8        les di, ptr [bp - 8]
8D97  26 80 7D 3C 05  cmp byte ptr es:[di + 0x3c], 5
8D9C  75 03           jne 0x8da1
8D9E  E9 F3 00        jmp 0x8e94
loc_8DA1:
8DA1  C7 46 FE 01 00  mov word ptr [bp - 2], 1
8DA6  EB 03           jmp 0x8dab
loc_8DA8:
8DA8  FF 46 FE        inc word ptr [bp - 2]
loc_8DAB:
8DAB  8B 7E 04        mov di, word ptr [bp + 4]
8DAE  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
8DB2  BA BF 00        mov dx, 0xbf
8DB5  F7 E2           mul dx
8DB7  C4 3E 17 A9     les di, ptr [0xa917]
8DBB  03 F8           add di, ax
8DBD  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8DC1  30 E4           xor ah, ah
8DC3  2D 03 00        sub ax, 3
8DC6  B9 03 00        mov cx, 3
8DC9  D3 E0           shl ax, cl
8DCB  03 46 FE        add ax, word ptr [bp - 2]
8DCE  48              dec ax
8DCF  89 46 FC        mov word ptr [bp - 4], ax
8DD2  C4 7E F8        les di, ptr [bp - 8]
8DD5  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
8DD9  03 46 FC        add ax, word ptr [bp - 4]
8DDC  50              push ax
8DDD  8B 7E FE        mov di, word ptr [bp - 2]
8DE0  8A 85 25 11     mov al, byte ptr [di + 0x1125]
8DE4  30 E4           xor ah, ah
8DE6  50              push ax
8DE7  B8 3D 00        mov ax, 0x3d
8DEA  50              push ax
8DEB  FF 76 04        push word ptr [bp + 4]
8DEE  E8 B1 FE        call 0x8ca2
8DF1  8A 46 FE        mov al, byte ptr [bp - 2]
8DF4  D0 E8           shr al, 1
8DF6  72 03           jb 0x8dfb
8DF8  E9 90 00        jmp 0x8e8b
loc_8DFB:
8DFB  8B 46 FC        mov ax, word ptr [bp - 4]
8DFE  31 D2           xor dx, dx
8E00  B9 02 00        mov cx, 2
8E03  F7 F1           div cx
8E05  05 61 09        add ax, 0x961
8E08  50              push ax
8E09  8B 46 FE        mov ax, word ptr [bp - 2]
8E0C  05 08 00        add ax, 8
8E0F  50              push ax
8E10  B8 04 00        mov ax, 4
8E13  50              push ax
8E14  8B 46 FE        mov ax, word ptr [bp - 2]
8E17  40              inc ax
8E18  31 D2           xor dx, dx
8E1A  B9 02 00        mov cx, 2
8E1D  F7 F1           div cx
8E1F  8B F8           mov di, ax
8E21  8A 85 2D 11     mov al, byte ptr [di + 0x112d]
8E25  30 E4           xor ah, ah
8E27  50              push ax
8E28  B8 17 00        mov ax, 0x17
8E2B  50              push ax
8E2C  FF 76 04        push word ptr [bp + 4]
8E2F  E8 9D FE        call 0x8ccf
8E32  8B 46 FC        mov ax, word ptr [bp - 4]
8E35  31 D2           xor dx, dx
8E37  B9 02 00        mov cx, 2
8E3A  F7 F1           div cx
8E3C  05 61 09        add ax, 0x961
8E3F  B1 03           mov cl, 3
8E41  D3 E0           shl ax, cl
8E43  C4 3E 2B A9     les di, ptr [0xa92b]
8E47  03 F8           add di, ax
8E49  81 C7 F8 FF     add di, 0xfff8
8E4D  89 7E F4        mov word ptr [bp - 0xc], di
8E50  8C 46 F6        mov word ptr [bp - 0xa], es
8E53  C4 7E F4        les di, ptr [bp - 0xc]
8E56  26 80 3D FE     cmp byte ptr es:[di], 0xfe
8E5A  73 2F           jae 0x8e8b
8E5C  C4 7E F4        les di, ptr [bp - 0xc]
8E5F  26 8A 45 03     mov al, byte ptr es:[di + 3]
8E63  98              cwde
8E64  D1 E0           shl ax, 1
8E66  C4 7E F4        les di, ptr [bp - 0xc]
8E69  03 F8           add di, ax
8E6B  26 FF 75 04     push word ptr es:[di + 4]
8E6F  8B 46 FE        mov ax, word ptr [bp - 2]
8E72  40              inc ax
8E73  31 D2           xor dx, dx
8E75  B9 02 00        mov cx, 2
8E78  F7 F1           div cx
8E7A  8B F8           mov di, ax
8E7C  8A 85 31 11     mov al, byte ptr [di + 0x1131]
8E80  30 E4           xor ah, ah
8E82  50              push ax
8E83  B8 18 00        mov ax, 0x18
8E86  50              push ax
8E87  0E              push cs
8E88  E8 CD 80        call 0xf58
loc_8E8B:
8E8B  83 7E FE 08     cmp word ptr [bp - 2], 8
8E8F  74 03           je 0x8e94
8E91  E9 14 FF        jmp 0x8da8
loc_8E94:
8E94  89 EC           mov sp, bp
8E96  5D              pop bp
8E97  C2 02 00        ret 2

; ---- routine 1771:8E9A  (found by: call)
sub_8E9A:
8E9A  55              push bp
8E9B  89 E5           mov bp, sp
8E9D  83 EC 06        sub sp, 6
8EA0  8B 7E 04        mov di, word ptr [bp + 4]
8EA3  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
8EA7  BA BF 00        mov dx, 0xbf
8EAA  F7 E2           mul dx
8EAC  C4 3E 17 A9     les di, ptr [0xa917]
8EB0  03 F8           add di, ax
8EB2  89 7E FA        mov word ptr [bp - 6], di
8EB5  8C 46 FC        mov word ptr [bp - 4], es
8EB8  8B 7E 04        mov di, word ptr [bp + 4]
8EBB  36 83 7D FC 08  cmp word ptr ss:[di - 4], 8
8EC0  76 1D           jbe 0x8edf
8EC2  C4 7E FA        les di, ptr [bp - 6]
8EC5  26 80 7D 2C 03  cmp byte ptr es:[di + 0x2c], 3
8ECA  72 0A           jb 0x8ed6
8ECC  8B 7E 04        mov di, word ptr [bp + 4]
8ECF  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
8ED4  75 09           jne 0x8edf
loc_8ED6:
8ED6  8B 7E 04        mov di, word ptr [bp + 4]
8ED9  36 C7 45 FC 01 00 mov word ptr ss:[di - 4], 1
loc_8EDF:
8EDF  8B 7E 04        mov di, word ptr [bp + 4]
8EE2  36 83 7D FC 09  cmp word ptr ss:[di - 4], 9
8EE7  75 2A           jne 0x8f13
8EE9  BF F2 36        mov di, 0x36f2
8EEC  1E              push ds
8EED  57              push di
8EEE  BF 6E A9        mov di, 0xa96e
8EF1  1E              push ds
8EF2  57              push di
8EF3  9A 29 03 4B 21  call far 214B:0329
8EF8  8B 7E 04        mov di, word ptr [bp + 4]
8EFB  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
8F00  74 0F           je 0x8f11
8F02  BF 3C 2D        mov di, 0x2d3c
8F05  1E              push ds
8F06  57              push di
8F07  BF 6E A9        mov di, 0xa96e
8F0A  1E              push ds
8F0B  57              push di
8F0C  9A 29 03 4B 21  call far 214B:0329
loc_8F11:
8F11  EB 28           jmp 0x8f3b
loc_8F13:
8F13  BF 1E 35        mov di, 0x351e
8F16  1E              push ds
8F17  57              push di
8F18  BF 6E A9        mov di, 0xa96e
8F1B  1E              push ds
8F1C  57              push di
8F1D  9A 29 03 4B 21  call far 214B:0329
8F22  8B 7E 04        mov di, word ptr [bp + 4]
8F25  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
8F2A  74 0F           je 0x8f3b
8F2C  BF 5A 2D        mov di, 0x2d5a
8F2F  1E              push ds
8F30  57              push di
8F31  BF 6E A9        mov di, 0xa96e
8F34  1E              push ds
8F35  57              push di
8F36  9A 29 03 4B 21  call far 214B:0329
loc_8F3B:
8F3B  8B 7E 04        mov di, word ptr [bp + 4]
8F3E  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
8F43  74 09           je 0x8f4e
8F45  B0 01           mov al, 1
8F47  50              push ax
8F48  FF 76 04        push word ptr [bp + 4]
8F4B  E8 0F FB        call 0x8a5d
loc_8F4E:
8F4E  B0 00           mov al, 0
8F50  50              push ax
8F51  8B 7E 04        mov di, word ptr [bp + 4]
8F54  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
8F58  50              push ax
8F59  C4 7E FA        les di, ptr [bp - 6]
8F5C  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8F60  30 E4           xor ah, ah
8F62  50              push ax
8F63  E8 5E CB        call 0x5ac4
8F66  BF 2A 14        mov di, 0x142a
8F69  1E              push ds
8F6A  57              push di
8F6B  BF 6E A9        mov di, 0xa96e
8F6E  1E              push ds
8F6F  57              push di
8F70  9A 29 03 4B 21  call far 214B:0329
8F75  8B 7E 04        mov di, word ptr [bp + 4]
8F78  36 83 7D FC 09  cmp word ptr ss:[di - 4], 9
8F7D  75 08           jne 0x8f87
8F7F  FF 76 04        push word ptr [bp + 4]
8F82  E8 FF FD        call 0x8d84
8F85  EB 6D           jmp 0x8ff4
loc_8F87:
8F87  B0 00           mov al, 0
8F89  50              push ax
8F8A  FF 76 04        push word ptr [bp + 4]
8F8D  E8 F7 FA        call 0x8a87
8F90  C7 46 FE 01 00  mov word ptr [bp - 2], 1
8F95  EB 03           jmp 0x8f9a
loc_8F97:
8F97  FF 46 FE        inc word ptr [bp - 2]
loc_8F9A:
8F9A  8B 46 FE        mov ax, word ptr [bp - 2]
8F9D  D1 E0           shl ax, 1
8F9F  50              push ax
8FA0  8B 7E 04        mov di, word ptr [bp + 4]
8FA3  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
8FA7  BA 38 00        mov dx, 0x38
8FAA  F7 E2           mul dx
8FAC  8B D8           mov bx, ax
8FAE  C4 7E FA        les di, ptr [bp - 6]
8FB1  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8FB5  30 E4           xor ah, ah
8FB7  BA C0 01        mov dx, 0x1c0
8FBA  F7 E2           mul dx
8FBC  8B C8           mov cx, ax
8FBE  8B 7E 04        mov di, word ptr [bp + 4]
8FC1  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
8FC5  98              cwde
8FC6  BA 00 0E        mov dx, 0xe00
8FC9  F7 E2           mul dx
8FCB  C4 3E 33 A9     les di, ptr [0xa933]
8FCF  03 F8           add di, ax
8FD1  03 F9           add di, cx
8FD3  03 FB           add di, bx
8FD5  58              pop ax
8FD6  03 F8           add di, ax
8FD8  26 FF B5 26 FE  push word ptr es:[di - 0x1da]
8FDD  8B 46 FE        mov ax, word ptr [bp - 2]
8FE0  05 07 00        add ax, 7
8FE3  50              push ax
8FE4  B8 3A 00        mov ax, 0x3a
8FE7  50              push ax
8FE8  FF 76 04        push word ptr [bp + 4]
8FEB  E8 B4 FC        call 0x8ca2
8FEE  83 7E FE 0C     cmp word ptr [bp - 2], 0xc
8FF2  75 A3           jne 0x8f97
loc_8FF4:
8FF4  8B 7E 04        mov di, word ptr [bp + 4]
8FF7  81 C7 FC FF     add di, 0xfffc
8FFB  16              push ss
8FFC  57              push di
8FFD  8B 7E 04        mov di, word ptr [bp + 4]
9000  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
9005  74 0A           je 0x9011
9007  C4 7E FA        les di, ptr [bp - 6]
900A  26 80 7D 2C 02  cmp byte ptr es:[di + 0x2c], 2
900F  77 04           ja 0x9015
loc_9011:
9011  B0 00           mov al, 0
9013  EB 02           jmp 0x9017
loc_9015:
9015  B0 01           mov al, 1
loc_9017:
9017  30 E4           xor ah, ah
9019  05 08 00        add ax, 8
901C  50              push ax
901D  9A 60 15 4B 21  call far 214B:1560
9022  89 EC           mov sp, bp
9024  5D              pop bp
9025  C2 02 00        ret 2

; ---- routine 1771:9028  (found by: call)
sub_9028:
9028  55              push bp
9029  89 E5           mov bp, sp
902B  81 EC 0A 01     sub sp, 0x10a
902F  C4 3E 23 A9     les di, ptr [0xa923]
9033  89 7E F6        mov word ptr [bp - 0xa], di
9036  8C 46 F8        mov word ptr [bp - 8], es
9039  8B 7E 04        mov di, word ptr [bp + 4]
903C  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
9040  89 46 FA        mov word ptr [bp - 6], ax
9043  8B 7E 04        mov di, word ptr [bp + 4]
9046  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
904B  74 09           je 0x9056
904D  8B 7E 04        mov di, word ptr [bp + 4]
9050  36 C7 45 F8 01 00 mov word ptr ss:[di - 8], 1
loc_9056:
9056  8B 7E 04        mov di, word ptr [bp + 4]
9059  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
905D  98              cwde
905E  8B F8           mov di, ax
9060  8A 85 36 11     mov al, byte ptr [di + 0x1136]
9064  30 E4           xor ah, ah
9066  89 46 FC        mov word ptr [bp - 4], ax
9069  B0 01           mov al, 1
906B  50              push ax
906C  8B 7E 04        mov di, word ptr [bp + 4]
906F  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
9073  50              push ax
9074  8B 7E 04        mov di, word ptr [bp + 4]
9077  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
907B  BA BF 00        mov dx, 0xbf
907E  F7 E2           mul dx
9080  C4 3E 17 A9     les di, ptr [0xa917]
9084  03 F8           add di, ax
9086  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
908A  30 E4           xor ah, ah
908C  50              push ax
908D  E8 34 CA        call 0x5ac4
9090  FF 76 04        push word ptr [bp + 4]
9093  E8 A9 F7        call 0x883f
9096  8B 7E 04        mov di, word ptr [bp + 4]
9099  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
909D  3B 46 FC        cmp ax, word ptr [bp - 4]
90A0  76 09           jbe 0x90ab
90A2  8B 7E 04        mov di, word ptr [bp + 4]
90A5  36 C7 45 FC 01 00 mov word ptr ss:[di - 4], 1
loc_90AB:
90AB  BF 6E 38        mov di, 0x386e
90AE  1E              push ds
90AF  57              push di
90B0  BF 6E A9        mov di, 0xa96e
90B3  1E              push ds
90B4  57              push di
90B5  9A 29 03 4B 21  call far 214B:0329
90BA  8B 7E 04        mov di, word ptr [bp + 4]
90BD  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
90C2  74 26           je 0x90ea
90C4  BF 5A 2D        mov di, 0x2d5a
90C7  1E              push ds
90C8  57              push di
90C9  BF 6E A9        mov di, 0xa96e
90CC  1E              push ds
90CD  57              push di
90CE  9A 29 03 4B 21  call far 214B:0329
90D3  8B 7E 04        mov di, word ptr [bp + 4]
90D6  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
90DB  74 04           je 0x90e1
90DD  B0 00           mov al, 0
90DF  EB 02           jmp 0x90e3
loc_90E1:
90E1  B0 01           mov al, 1
loc_90E3:
90E3  50              push ax
90E4  FF 76 04        push word ptr [bp + 4]
90E7  E8 73 F9        call 0x8a5d
loc_90EA:
90EA  8B 7E 04        mov di, word ptr [bp + 4]
90ED  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
90F1  C4 7E F6        les di, ptr [bp - 0xa]
90F4  26 3A 45 40     cmp al, byte ptr es:[di + 0x40]
90F8  75 34           jne 0x912e
90FA  0E              push cs
90FB  E8 DA C8        call 0x59d8
90FE  08 C0           or al, al
9100  75 2C           jne 0x912e
9102  B0 07           mov al, 7
9104  50              push ax
9105  8D BE F6 FE     lea di, [bp - 0x10a]
9109  16              push ss
910A  57              push di
910B  8B 7E 04        mov di, word ptr [bp + 4]
910E  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
9112  05 40 00        add ax, 0x40
9115  50              push ax
9116  9A 5A 07 E4 23  call far 23E4:075A
911B  B0 09           mov al, 9
911D  50              push ax
911E  B0 0B           mov al, 0xb
9120  50              push ax
9121  BF 6E A9        mov di, 0xa96e
9124  1E              push ds
9125  57              push di
9126  9A C8 02 4B 21  call far 214B:02C8
912B  E9 7F 00        jmp 0x91ad
loc_912E:
912E  B0 01           mov al, 1
9130  50              push ax
9131  FF 76 04        push word ptr [bp + 4]
9134  E8 50 F9        call 0x8a87
9137  C7 46 FE 01 00  mov word ptr [bp - 2], 1
913C  EB 03           jmp 0x9141
loc_913E:
913E  FF 46 FE        inc word ptr [bp - 2]
loc_9141:
9141  8B 46 FE        mov ax, word ptr [bp - 2]
9144  D1 E0           shl ax, 1
9146  50              push ax
9147  8B 7E 04        mov di, word ptr [bp + 4]
914A  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
914E  BA 38 00        mov dx, 0x38
9151  F7 E2           mul dx
9153  8B D8           mov bx, ax
9155  8B 7E 04        mov di, word ptr [bp + 4]
9158  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
915C  BA BF 00        mov dx, 0xbf
915F  F7 E2           mul dx
9161  C4 3E 17 A9     les di, ptr [0xa917]
9165  03 F8           add di, ax
9167  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
916B  30 E4           xor ah, ah
916D  BA C0 01        mov dx, 0x1c0
9170  F7 E2           mul dx
9172  8B C8           mov cx, ax
9174  8B 7E 04        mov di, word ptr [bp + 4]
9177  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
917B  98              cwde
917C  BA 00 0E        mov dx, 0xe00
917F  F7 E2           mul dx
9181  C4 3E 33 A9     les di, ptr [0xa933]
9185  03 F8           add di, ax
9187  03 F9           add di, cx
9189  03 FB           add di, bx
918B  58              pop ax
918C  03 F8           add di, ax
918E  26 FF B5 26 05  push word ptr es:[di + 0x526]
9193  8B 7E FE        mov di, word ptr [bp - 2]
9196  8A 85 37 11     mov al, byte ptr [di + 0x1137]
919A  30 E4           xor ah, ah
919C  50              push ax
919D  B8 3A 00        mov ax, 0x3a
91A0  50              push ax
91A1  FF 76 04        push word ptr [bp + 4]
91A4  E8 FB FA        call 0x8ca2
91A7  83 7E FE 06     cmp word ptr [bp - 2], 6
91AB  75 91           jne 0x913e
loc_91AD:
91AD  8B 7E 04        mov di, word ptr [bp + 4]
91B0  81 C7 FC FF     add di, 0xfffc
91B4  16              push ss
91B5  57              push di
91B6  FF 76 FC        push word ptr [bp - 4]
91B9  9A 60 15 4B 21  call far 214B:1560
91BE  8B 46 FA        mov ax, word ptr [bp - 6]
91C1  8B 7E 04        mov di, word ptr [bp + 4]
91C4  36 89 45 F8     mov word ptr ss:[di - 8], ax
91C8  89 EC           mov sp, bp
91CA  5D              pop bp
91CB  C2 02 00        ret 2

; ---- routine 1771:91CE  (found by: call)
sub_91CE:
91CE  55              push bp
91CF  89 E5           mov bp, sp
91D1  83 EC 06        sub sp, 6
91D4  8B 7E 04        mov di, word ptr [bp + 4]
91D7  36 8B 7D 04     mov di, word ptr ss:[di + 4]
91DB  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
91DF  BA BF 00        mov dx, 0xbf
91E2  F7 E2           mul dx
91E4  C4 3E 17 A9     les di, ptr [0xa917]
91E8  03 F8           add di, ax
91EA  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
91EE  30 E4           xor ah, ah
91F0  BA C0 01        mov dx, 0x1c0
91F3  F7 E2           mul dx
91F5  8B C8           mov cx, ax
91F7  8B 7E 04        mov di, word ptr [bp + 4]
91FA  36 8B 7D 04     mov di, word ptr ss:[di + 4]
91FE  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
9202  98              cwde
9203  BA 00 0E        mov dx, 0xe00
9206  F7 E2           mul dx
9208  C4 3E 33 A9     les di, ptr [0xa933]
920C  03 F8           add di, ax
920E  03 F9           add di, cx
9210  81 C7 40 05     add di, 0x540
9214  89 7E FA        mov word ptr [bp - 6], di
9217  8C 46 FC        mov word ptr [bp - 4], es
921A  BF 08 33        mov di, 0x3308
921D  1E              push ds
921E  57              push di
921F  BF 6E A9        mov di, 0xa96e
9222  1E              push ds
9223  57              push di
9224  9A 29 03 4B 21  call far 214B:0329
9229  8B 7E 04        mov di, word ptr [bp + 4]
922C  36 8B 7D 04     mov di, word ptr ss:[di + 4]
9230  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
9235  74 0D           je 0x9244
9237  B0 01           mov al, 1
9239  50              push ax
923A  8B 7E 04        mov di, word ptr [bp + 4]
923D  36 FF 75 04     push word ptr ss:[di + 4]
9241  E8 19 F8        call 0x8a5d
loc_9244:
9244  C4 3E 23 A9     les di, ptr [0xa923]
9248  26 80 7D 3C 04  cmp byte ptr es:[di + 0x3c], 4
924D  73 03           jae 0x9252
924F  E9 04 01        jmp 0x9356
loc_9252:
9252  C7 46 FE 07 00  mov word ptr [bp - 2], 7
9257  EB 03           jmp 0x925c
loc_9259:
9259  FF 46 FE        inc word ptr [bp - 2]
loc_925C:
925C  8B 46 FE        mov ax, word ptr [bp - 2]
925F  D1 E0           shl ax, 1
9261  C4 7E FA        les di, ptr [bp - 6]
9264  03 F8           add di, ax
9266  26 FF 75 1E     push word ptr es:[di + 0x1e]
926A  8B 7E FE        mov di, word ptr [bp - 2]
926D  8A 85 37 11     mov al, byte ptr [di + 0x1137]
9271  30 E4           xor ah, ah
9273  50              push ax
9274  83 7E FE 08     cmp word ptr [bp - 2], 8
9278  77 04           ja 0x927e
927A  B0 00           mov al, 0
927C  EB 02           jmp 0x9280
loc_927E:
927E  B0 01           mov al, 1
loc_9280:
9280  98              cwde
9281  8B F8           mov di, ax
9283  8A 85 42 11     mov al, byte ptr [di + 0x1142]
9287  30 E4           xor ah, ah
9289  50              push ax
928A  8B 7E FE        mov di, word ptr [bp - 2]
928D  8A 85 3D 11     mov al, byte ptr [di + 0x113d]
9291  30 E4           xor ah, ah
9293  50              push ax
9294  83 7E FE 08     cmp word ptr [bp - 2], 8
9298  77 04           ja 0x929e
929A  B0 00           mov al, 0
929C  EB 02           jmp 0x92a0
loc_929E:
929E  B0 01           mov al, 1
loc_92A0:
92A0  98              cwde
92A1  8B F8           mov di, ax
92A3  8A 85 48 11     mov al, byte ptr [di + 0x1148]
92A7  30 E4           xor ah, ah
92A9  50              push ax
92AA  8B 7E 04        mov di, word ptr [bp + 4]
92AD  36 FF 75 04     push word ptr ss:[di + 4]
92B1  E8 1B FA        call 0x8ccf
92B4  83 7E FE 0A     cmp word ptr [bp - 2], 0xa
92B8  75 9F           jne 0x9259
92BA  C4 7E FA        les di, ptr [bp - 6]
92BD  26 83 7D 32 00  cmp word ptr es:[di + 0x32], 0
92C2  74 18           je 0x92dc
92C4  C4 7E FA        les di, ptr [bp - 6]
92C7  26 8B 45 32     mov ax, word ptr es:[di + 0x32]
92CB  B1 03           mov cl, 3
92CD  D3 E0           shl ax, cl
92CF  C4 3E 2B A9     les di, ptr [0xa92b]
92D3  03 F8           add di, ax
92D5  26 80 7D F8 FE  cmp byte ptr es:[di - 8], 0xfe
92DA  72 02           jb 0x92de
loc_92DC:
92DC  EB 78           jmp 0x9356
loc_92DE:
92DE  C4 7E FA        les di, ptr [bp - 6]
92E1  26 8B 45 32     mov ax, word ptr es:[di + 0x32]
92E5  B1 03           mov cl, 3
92E7  D3 E0           shl ax, cl
92E9  C4 3E 2B A9     les di, ptr [0xa92b]
92ED  03 F8           add di, ax
92EF  81 C7 F8 FF     add di, 0xfff8
92F3  06              push es
92F4  57              push di
92F5  0E              push cs
92F6  E8 9B C9        call 0x5c94
92F9  50              push ax
92FA  B8 0A 00        mov ax, 0xa
92FD  50              push ax
92FE  B8 3C 00        mov ax, 0x3c
9301  50              push ax
9302  0E              push cs
9303  E8 52 7C        call 0x10f58
9306  C4 7E FA        les di, ptr [bp - 6]
9309  26 8B 45 32     mov ax, word ptr es:[di + 0x32]
930D  B1 03           mov cl, 3
930F  D3 E0           shl ax, cl
9311  C4 3E 2B A9     les di, ptr [0xa92b]
9315  03 F8           add di, ax
9317  81 C7 F8 FF     add di, 0xfff8
931B  06              push es
931C  57              push di
931D  0E              push cs
931E  E8 AA C9        call 0x5ccb
9321  50              push ax
9322  B8 0C 00        mov ax, 0xc
9325  50              push ax
9326  B8 3C 00        mov ax, 0x3c
9329  50              push ax
932A  0E              push cs
932B  E8 2A 7C        call 0x10f58
932E  C4 7E FA        les di, ptr [bp - 6]
9331  26 8B 45 30     mov ax, word ptr es:[di + 0x30]
9335  B1 03           mov cl, 3
9337  D3 E0           shl ax, cl
9339  C4 3E 2B A9     les di, ptr [0xa92b]
933D  03 F8           add di, ax
933F  81 C7 F8 FF     add di, 0xfff8
9343  06              push es
9344  57              push di
9345  0E              push cs
9346  E8 4B C9        call 0x5c94
9349  50              push ax
934A  B8 0E 00        mov ax, 0xe
934D  50              push ax
934E  B8 3C 00        mov ax, 0x3c
9351  50              push ax
9352  0E              push cs
9353  E8 02 7C        call 0x10f58
loc_9356:
9356  89 EC           mov sp, bp
9358  5D              pop bp
9359  C2 02 00        ret 2
; data (not reached as code), 32 bytes
935C                  db E0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
936C                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:937C  (found by: call)
sub_937C:
937C  55              push bp
937D  89 E5           mov bp, sp
937F  83 EC 06        sub sp, 6
9382  C4 3E 23 A9     les di, ptr [0xa923]
9386  89 7E FA        mov word ptr [bp - 6], di
9389  8C 46 FC        mov word ptr [bp - 4], es
938C  BF F4 2E        mov di, 0x2ef4
938F  1E              push ds
9390  57              push di
9391  BF 6E A9        mov di, 0xa96e
9394  1E              push ds
9395  57              push di
9396  9A 29 03 4B 21  call far 214B:0329
939B  8B 7E 04        mov di, word ptr [bp + 4]
939E  36 8B 7D 04     mov di, word ptr ss:[di + 4]
93A2  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
93A7  74 0A           je 0x93b3
93A9  8B 7E 04        mov di, word ptr [bp + 4]
93AC  36 FF 75 04     push word ptr ss:[di + 4]
93B0  E8 0E F6        call 0x89c1
loc_93B3:
93B3  C4 7E FA        les di, ptr [bp - 6]
93B6  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
93BA  50              push ax
93BB  BF 5C 93        mov di, 0x935c
93BE  0E              push cs
93BF  57              push di
93C0  9A DF 08 E4 23  call far 23E4:08DF
93C5  74 03           je 0x93ca
93C7  E9 39 01        jmp 0x9503
loc_93CA:
93CA  C7 46 FE 01 00  mov word ptr [bp - 2], 1
93CF  EB 03           jmp 0x93d4
loc_93D1:
93D1  FF 46 FE        inc word ptr [bp - 2]
loc_93D4:
93D4  C4 7E FA        les di, ptr [bp - 6]
93D7  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
93DC  74 13           je 0x93f1
93DE  C4 7E FA        les di, ptr [bp - 6]
93E1  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
93E5  03 46 FE        add ax, word ptr [bp - 2]
93E8  C4 7E FA        les di, ptr [bp - 6]
93EB  26 3B 45 28     cmp ax, word ptr es:[di + 0x28]
93EF  77 3E           ja 0x942f
loc_93F1:
93F1  C4 7E FA        les di, ptr [bp - 6]
93F4  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
93F8  03 46 FE        add ax, word ptr [bp - 2]
93FB  48              dec ax
93FC  50              push ax
93FD  8B 7E FE        mov di, word ptr [bp - 2]
9400  8A 85 49 11     mov al, byte ptr [di + 0x1149]
9404  30 E4           xor ah, ah
9406  50              push ax
9407  8B 7E FE        mov di, word ptr [bp - 2]
940A  8A 85 59 11     mov al, byte ptr [di + 0x1159]
940E  30 E4           xor ah, ah
9410  50              push ax
9411  8B 7E FE        mov di, word ptr [bp - 2]
9414  8A 85 69 11     mov al, byte ptr [di + 0x1169]
9418  30 E4           xor ah, ah
941A  50              push ax
941B  8B 7E FE        mov di, word ptr [bp - 2]
941E  8A 85 79 11     mov al, byte ptr [di + 0x1179]
9422  30 E4           xor ah, ah
9424  50              push ax
9425  8B 7E 04        mov di, word ptr [bp + 4]
9428  36 FF 75 04     push word ptr ss:[di + 4]
942C  E8 A0 F8        call 0x8ccf
loc_942F:
942F  83 7E FE 10     cmp word ptr [bp - 2], 0x10
9433  75 9C           jne 0x93d1
9435  C4 7E FA        les di, ptr [bp - 6]
9438  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
943D  74 16           je 0x9455
943F  C4 7E FA        les di, ptr [bp - 6]
9442  26 8B 45 28     mov ax, word ptr es:[di + 0x28]
9446  C4 7E FA        les di, ptr [bp - 6]
9449  26 2B 45 2A     sub ax, word ptr es:[di + 0x2a]
944D  3D 10 00        cmp ax, 0x10
9450  74 03           je 0x9455
9452  E9 AE 00        jmp 0x9503
loc_9455:
9455  C4 7E FA        les di, ptr [bp - 6]
9458  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
945C  05 0F 00        add ax, 0xf
945F  B1 03           mov cl, 3
9461  D3 E0           shl ax, cl
9463  C4 3E 2B A9     les di, ptr [0xa92b]
9467  03 F8           add di, ax
9469  26 80 7D F8 FE  cmp byte ptr es:[di - 8], 0xfe
946E  72 03           jb 0x9473
9470  E9 90 00        jmp 0x9503
loc_9473:
9473  BF 02 2C        mov di, 0x2c02
9476  1E              push ds
9477  57              push di
9478  BF 6E A9        mov di, 0xa96e
947B  1E              push ds
947C  57              push di
947D  9A 29 03 4B 21  call far 214B:0329
9482  C4 7E FA        les di, ptr [bp - 6]
9485  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
9489  05 0F 00        add ax, 0xf
948C  B1 03           mov cl, 3
948E  D3 E0           shl ax, cl
9490  C4 3E 2B A9     les di, ptr [0xa92b]
9494  03 F8           add di, ax
9496  81 C7 F8 FF     add di, 0xfff8
949A  06              push es
949B  57              push di
949C  0E              push cs
949D  E8 F4 C7        call 0x5c94
94A0  50              push ax
94A1  B8 02 00        mov ax, 2
94A4  50              push ax
94A5  B8 41 00        mov ax, 0x41
94A8  50              push ax
94A9  0E              push cs
94AA  E8 AB 7A        call 0x10f58
94AD  C4 7E FA        les di, ptr [bp - 6]
94B0  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
94B4  05 0F 00        add ax, 0xf
94B7  B1 03           mov cl, 3
94B9  D3 E0           shl ax, cl
94BB  C4 3E 2B A9     les di, ptr [0xa92b]
94BF  03 F8           add di, ax
94C1  81 C7 F8 FF     add di, 0xfff8
94C5  06              push es
94C6  57              push di
94C7  0E              push cs
94C8  E8 00 C8        call 0x5ccb
94CB  50              push ax
94CC  B8 04 00        mov ax, 4
94CF  50              push ax
94D0  B8 41 00        mov ax, 0x41
94D3  50              push ax
94D4  0E              push cs
94D5  E8 80 7A        call 0x10f58
94D8  C4 7E FA        les di, ptr [bp - 6]
94DB  26 8B 45 2A     mov ax, word ptr es:[di + 0x2a]
94DF  05 0E 00        add ax, 0xe
94E2  B1 03           mov cl, 3
94E4  D3 E0           shl ax, cl
94E6  C4 3E 2B A9     les di, ptr [0xa92b]
94EA  03 F8           add di, ax
94EC  81 C7 F8 FF     add di, 0xfff8
94F0  06              push es
94F1  57              push di
94F2  0E              push cs
94F3  E8 9E C7        call 0x5c94
94F6  50              push ax
94F7  B8 06 00        mov ax, 6
94FA  50              push ax
94FB  B8 41 00        mov ax, 0x41
94FE  50              push ax
94FF  0E              push cs
9500  E8 55 7A        call 0x10f58
loc_9503:
9503  89 EC           mov sp, bp
9505  5D              pop bp
9506  C2 02 00        ret 2

; ---- routine 1771:9509  (found by: call)
sub_9509:
9509  55              push bp
950A  89 E5           mov bp, sp
950C  B0 01           mov al, 1
950E  50              push ax
950F  8B 7E 04        mov di, word ptr [bp + 4]
9512  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
9516  50              push ax
9517  8B 7E 04        mov di, word ptr [bp + 4]
951A  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
951E  BA BF 00        mov dx, 0xbf
9521  F7 E2           mul dx
9523  C4 3E 17 A9     les di, ptr [0xa917]
9527  03 F8           add di, ax
9529  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
952D  30 E4           xor ah, ah
952F  50              push ax
9530  E8 91 C5        call 0x5ac4
9533  FF 76 04        push word ptr [bp + 4]
9536  E8 06 F3        call 0x883f
9539  8B 7E 04        mov di, word ptr [bp + 4]
953C  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
9541  74 06           je 0x9549
9543  55              push bp
9544  E8 35 FE        call 0x937c
9547  EB 04           jmp 0x954d
loc_9549:
9549  55              push bp
954A  E8 81 FC        call 0x91ce
loc_954D:
954D  C4 3E 6E A9     les di, ptr [0xa96e]
9551  06              push es
9552  57              push di
9553  C4 3E 6A A9     les di, ptr [0xa96a]
9557  06              push es
9558  57              push di
9559  B8 A0 0F        mov ax, 0xfa0
955C  50              push ax
955D  9A 5D 02 E4 23  call far 23E4:025D
9562  9A DD 08 4B 21  call far 214B:08DD
9567  89 EC           mov sp, bp
9569  5D              pop bp
956A  C2 02 00        ret 2
; data (not reached as code), 32 bytes
956D                  db 10 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
957D                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:958D  (found by: far)
sub_958D:
958D  55              push bp
958E  89 E5           mov bp, sp
9590  83 EC 0E        sub sp, 0xe
9593  C4 3E 23 A9     les di, ptr [0xa923]
9597  89 7E F3        mov word ptr [bp - 0xd], di
959A  8C 46 F5        mov word ptr [bp - 0xb], es
959D  8B 46 06        mov ax, word ptr [bp + 6]
95A0  89 46 F8        mov word ptr [bp - 8], ax
95A3  C4 7E F3        les di, ptr [bp - 0xd]
95A6  26 80 7D 3C 07  cmp byte ptr es:[di + 0x3c], 7
95AB  72 05           jb 0x95b2
95AD  C7 46 F8 01 00  mov word ptr [bp - 8], 1
loc_95B2:
95B2  C4 7E F3        les di, ptr [bp - 0xd]
95B5  26 80 7D 3C 06  cmp byte ptr es:[di + 0x3c], 6
95BA  75 1C           jne 0x95d8
95BC  8B 46 06        mov ax, word ptr [bp + 6]
95BF  BA BF 00        mov dx, 0xbf
95C2  F7 E2           mul dx
95C4  C4 3E 17 A9     les di, ptr [0xa917]
95C8  03 F8           add di, ax
95CA  26 80 7D 2C 02  cmp byte ptr es:[di + 0x2c], 2
95CF  76 07           jbe 0x95d8
95D1  C7 46 FC 09 00  mov word ptr [bp - 4], 9
95D6  EB 13           jmp 0x95eb
loc_95D8:
95D8  83 7E 08 00     cmp word ptr [bp + 8], 0
95DC  75 07           jne 0x95e5
95DE  C7 46 FC 01 00  mov word ptr [bp - 4], 1
95E3  EB 06           jmp 0x95eb
loc_95E5:
95E5  8B 46 08        mov ax, word ptr [bp + 8]
95E8  89 46 FC        mov word ptr [bp - 4], ax
loc_95EB:
95EB  8B 46 06        mov ax, word ptr [bp + 6]
95EE  89 46 FA        mov word ptr [bp - 6], ax
95F1  C4 7E F3        les di, ptr [bp - 0xd]
95F4  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
95F8  50              push ax
95F9  BF 6D 95        mov di, 0x956d
95FC  0E              push cs
95FD  57              push di
95FE  9A DF 08 E4 23  call far 23E4:08DF
9603  75 04           jne 0x9609
9605  B0 00           mov al, 0
9607  EB 02           jmp 0x960b
loc_9609:
9609  B0 01           mov al, 1
loc_960B:
960B  30 E4           xor ah, ah
960D  50              push ax
960E  0E              push cs
960F  E8 C6 C3        call 0x59d8
9612  30 E4           xor ah, ah
9614  40              inc ax
9615  5A              pop dx
9616  03 C2           add ax, dx
9618  89 46 FE        mov word ptr [bp - 2], ax
961B  C4 7E F3        les di, ptr [bp - 0xd]
961E  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
9622  88 46 F7        mov byte ptr [bp - 9], al
loc_9625:
9625  55              push bp
9626  E8 10 F3        call 0x8939
9629  8B 46 FE        mov ax, word ptr [bp - 2]
962C  3D 01 00        cmp ax, 1
962F  75 06           jne 0x9637
9631  55              push bp
9632  E8 65 F8        call 0x8e9a
9635  EB 14           jmp 0x964b
loc_9637:
9637  3D 02 00        cmp ax, 2
963A  75 06           jne 0x9642
963C  55              push bp
963D  E8 E8 F9        call 0x9028
9640  EB 09           jmp 0x964b
loc_9642:
9642  3D 03 00        cmp ax, 3
9645  75 04           jne 0x964b
9647  55              push bp
9648  E8 BE FE        call 0x9509
loc_964B:
964B  A0 76 A9        mov al, byte ptr [0xa976]
964E  3C 20           cmp al, 0x20
9650  75 18           jne 0x966a
9652  8D 7E F8        lea di, [bp - 8]
9655  16              push ss
9656  57              push di
9657  B8 01 00        mov ax, 1
965A  50              push ax
965B  B8 80 00        mov ax, 0x80
965E  50              push ax
965F  B8 20 00        mov ax, 0x20
9662  50              push ax
9663  9A 86 1C 4B 21  call far 214B:1C86
9668  EB 53           jmp 0x96bd
loc_966A:
966A  3C AE           cmp al, 0xae
966C  74 04           je 0x9672
966E  3C AF           cmp al, 0xaf
9670  75 2A           jne 0x969c
loc_9672:
9672  8D 7E FE        lea di, [bp - 2]
9675  16              push ss
9676  57              push di
9677  B8 01 00        mov ax, 1
967A  50              push ax
967B  B8 03 00        mov ax, 3
967E  50              push ax
967F  80 3E 76 A9 AF  cmp byte ptr [0xa976], 0xaf
9684  74 04           je 0x968a
9686  B0 00           mov al, 0
9688  EB 02           jmp 0x968c
loc_968A:
968A  B0 01           mov al, 1
loc_968C:
968C  98              cwde
968D  8B F8           mov di, ax
968F  8A 85 20 79     mov al, byte ptr [di + 0x7920]
9693  98              cwde
9694  50              push ax
9695  9A 86 1C 4B 21  call far 214B:1C86
969A  EB 21           jmp 0x96bd
loc_969C:
969C  3C B6           cmp al, 0xb6
969E  74 04           je 0x96a4
96A0  3C B7           cmp al, 0xb7
96A2  75 19           jne 0x96bd
loc_96A4:
96A4  C4 7E F3        les di, ptr [bp - 0xd]
96A7  26 83 7D 38 00  cmp word ptr es:[di + 0x38], 0
96AC  76 0F           jbe 0x96bd
96AE  80 7E F7 00     cmp byte ptr [bp - 9], 0
96B2  74 04           je 0x96b8
96B4  B0 00           mov al, 0
96B6  EB 02           jmp 0x96ba
loc_96B8:
96B8  B0 01           mov al, 1
loc_96BA:
96BA  88 46 F7        mov byte ptr [bp - 9], al
loc_96BD:
96BD  80 7E 0A 00     cmp byte ptr [bp + 0xa], 0
96C1  74 0A           je 0x96cd
96C3  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
96C8  74 03           je 0x96cd
96CA  E9 58 FF        jmp 0x9625
loc_96CD:
96CD  89 EC           mov sp, bp
96CF  5D              pop bp
96D0  CA 06 00        retf 6

; ---- routine 1771:96D3  (found by: call, far)
sub_96D3:
96D3  55              push bp
96D4  89 E5           mov bp, sp
96D6  83 EC 04        sub sp, 4
96D9  8B 46 0C        mov ax, word ptr [bp + 0xc]
96DC  BA 14 00        mov dx, 0x14
96DF  F7 E2           mul dx
96E1  C4 3E 1B A9     les di, ptr [0xa91b]
96E5  03 F8           add di, ax
96E7  89 7E FC        mov word ptr [bp - 4], di
96EA  8C 46 FE        mov word ptr [bp - 2], es
96ED  8A 46 0A        mov al, byte ptr [bp + 0xa]
96F0  C4 7E FC        les di, ptr [bp - 4]
96F3  26 88 05        mov byte ptr es:[di], al
96F6  8A 46 08        mov al, byte ptr [bp + 8]
96F9  C4 7E FC        les di, ptr [bp - 4]
96FC  26 88 45 07     mov byte ptr es:[di + 7], al
9700  C4 7E FC        les di, ptr [bp - 4]
9703  26 8A 45 07     mov al, byte ptr es:[di + 7]
9707  C4 7E FC        les di, ptr [bp - 4]
970A  26 88 45 06     mov byte ptr es:[di + 6], al
970E  B8 10 00        mov ax, 0x10
9711  50              push ax
9712  9A B1 06 4B 21  call far 214B:06B1
9717  C4 7E FC        les di, ptr [bp - 4]
971A  26 88 45 05     mov byte ptr es:[di + 5], al
971E  B8 07 00        mov ax, 7
9721  50              push ax
9722  9A B1 06 4B 21  call far 214B:06B1
9727  50              push ax
9728  B8 07 00        mov ax, 7
972B  50              push ax
972C  9A B1 06 4B 21  call far 214B:06B1
9731  8B D0           mov dx, ax
9733  C4 7E FC        les di, ptr [bp - 4]
9736  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
973B  74 04           je 0x9741
973D  B0 00           mov al, 0
973F  EB 02           jmp 0x9743
loc_9741:
9741  B0 01           mov al, 1
loc_9743:
9743  98              cwde
9744  8B F8           mov di, ax
9746  8A 85 8A 11     mov al, byte ptr [di + 0x118a]
974A  30 E4           xor ah, ah
974C  2B C2           sub ax, dx
974E  5A              pop dx
974F  03 C2           add ax, dx
9751  C4 7E FC        les di, ptr [bp - 4]
9754  26 88 45 01     mov byte ptr es:[di + 1], al
9758  FF 76 0C        push word ptr [bp + 0xc]
975B  E8 33 9B        call 0x3291
975E  80 7E 06 00     cmp byte ptr [bp + 6], 0
9762  74 13           je 0x9777
9764  FF 76 0A        push word ptr [bp + 0xa]
9767  0E              push cs
9768  E8 7C 79        call 0x110e7
976B  05 7F 00        add ax, 0x7f
976E  C4 7E FC        les di, ptr [bp - 4]
9771  26 88 45 03     mov byte ptr es:[di + 3], al
9775  EB 21           jmp 0x9798
loc_9777:
9777  B8 0A 00        mov ax, 0xa
977A  50              push ax
977B  9A B1 06 4B 21  call far 214B:06B1
9780  50              push ax
9781  FF 76 0A        push word ptr [bp + 0xa]
9784  0E              push cs
9785  E8 5F 79        call 0x110e7
9788  05 7F 00        add ax, 0x7f
978B  2D 0A 00        sub ax, 0xa
978E  5A              pop dx
978F  2B C2           sub ax, dx
9791  C4 7E FC        les di, ptr [bp - 4]
9794  26 88 45 03     mov byte ptr es:[di + 3], al
loc_9798:
9798  FF 76 0C        push word ptr [bp + 0xc]
979B  0E              push cs
979C  E8 4C 9B        call 0x32eb
979F  B8 20 00        mov ax, 0x20
97A2  50              push ax
97A3  9A B1 06 4B 21  call far 214B:06B1
97A8  C4 7E FC        les di, ptr [bp - 4]
97AB  26 88 45 0C     mov byte ptr es:[di + 0xc], al
97AF  FF 76 0C        push word ptr [bp + 0xc]
97B2  0E              push cs
97B3  E8 7B 9C        call 0x3431
97B6  FF 76 0C        push word ptr [bp + 0xc]
97B9  0E              push cs
97BA  E8 9B 9D        call 0x3558
97BD  C4 7E FC        les di, ptr [bp - 4]
97C0  26 C7 45 12 FF 7F mov word ptr es:[di + 0x12], 0x7fff
97C6  89 EC           mov sp, bp
97C8  5D              pop bp
97C9  CA 08 00        retf 8

