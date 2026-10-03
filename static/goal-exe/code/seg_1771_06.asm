; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 6 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:3AE2  (found by: call)
sub_3AE2:
3AE2  55              push bp
3AE3  89 E5           mov bp, sp
3AE5  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
3AEA  74 1D           je 0x3b09
3AEC  80 7E 06 00     cmp byte ptr [bp + 6], 0
3AF0  74 17           je 0x3b09
3AF2  BF D5 3A        mov di, 0x3ad5
3AF5  0E              push cs
3AF6  57              push di
3AF7  B0 10           mov al, 0x10
3AF9  50              push ax
3AFA  B0 3D           mov al, 0x3d
3AFC  50              push ax
3AFD  BF 6E A9        mov di, 0xa96e
3B00  1E              push ds
3B01  57              push di
3B02  9A A3 01 4B 21  call far 214B:01A3
3B07  EB 21           jmp 0x3b2a
loc_3B09:
3B09  8A 46 06        mov al, byte ptr [bp + 6]
3B0C  98              cwde
3B0D  BA 0B 00        mov dx, 0xb
3B10  F7 E2           mul dx
3B12  8B F8           mov di, ax
3B14  81 C7 90 0E     add di, 0xe90
3B18  1E              push ds
3B19  57              push di
3B1A  B0 10           mov al, 0x10
3B1C  50              push ax
3B1D  B0 3D           mov al, 0x3d
3B1F  50              push ax
3B20  BF 6E A9        mov di, 0xa96e
3B23  1E              push ds
3B24  57              push di
3B25  9A A3 01 4B 21  call far 214B:01A3
loc_3B2A:
3B2A  89 EC           mov sp, bp
3B2C  5D              pop bp
3B2D  C2 04 00        ret 4
; data (not reached as code), 15 bytes
3B30                  pstr 'Protect zone P'

; ---- routine 1771:3B3F  (found by: call)
sub_3B3F:
3B3F  55              push bp
3B40  89 E5           mov bp, sp
3B42  83 EC 08        sub sp, 8
3B45  8B 7E 04        mov di, word ptr [bp + 4]
3B48  36 8B 45 04     mov ax, word ptr ss:[di + 4]
3B4C  BA 14 00        mov dx, 0x14
3B4F  F7 E2           mul dx
3B51  C4 3E 1B A9     les di, ptr [0xa91b]
3B55  03 F8           add di, ax
3B57  89 7E FC        mov word ptr [bp - 4], di
3B5A  8C 46 FE        mov word ptr [bp - 2], es
3B5D  C4 7E FC        les di, ptr [bp - 4]
3B60  26 80 7D 06 02  cmp byte ptr es:[di + 6], 2
3B65  73 02           jae 0x3b69
3B67  EB 5F           jmp 0x3bc8
loc_3B69:
3B69  B8 07 00        mov ax, 7
3B6C  50              push ax
3B6D  C4 7E FC        les di, ptr [bp - 4]
3B70  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
3B74  30 E4           xor ah, ah
3B76  50              push ax
3B77  9A 57 0C 4B 21  call far 214B:0C57
3B7C  08 C0           or al, al
3B7E  74 17           je 0x3b97
3B80  BF 30 3B        mov di, 0x3b30
3B83  0E              push cs
3B84  57              push di
3B85  B0 10           mov al, 0x10
3B87  50              push ax
3B88  B0 3D           mov al, 0x3d
3B8A  50              push ax
3B8B  BF 6E A9        mov di, 0xa96e
3B8E  1E              push ds
3B8F  57              push di
3B90  9A A3 01 4B 21  call far 214B:01A3
3B95  EB 31           jmp 0x3bc8
loc_3B97:
3B97  C4 7E FC        les di, ptr [bp - 4]
3B9A  26 8A 05        mov al, byte ptr es:[di]
3B9D  30 E4           xor ah, ah
3B9F  BA BF 00        mov dx, 0xbf
3BA2  F7 E2           mul dx
3BA4  C4 3E 17 A9     les di, ptr [0xa917]
3BA8  03 F8           add di, ax
3BAA  89 7E F8        mov word ptr [bp - 8], di
3BAD  8C 46 FA        mov word ptr [bp - 6], es
3BB0  B8 08 00        mov ax, 8
3BB3  50              push ax
3BB4  C4 7E F8        les di, ptr [bp - 8]
3BB7  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
3BBB  30 E4           xor ah, ah
3BBD  50              push ax
3BBE  9A 57 0C 4B 21  call far 214B:0C57
3BC3  50              push ax
3BC4  55              push bp
3BC5  E8 1A FF        call 0x3ae2
loc_3BC8:
3BC8  89 EC           mov sp, bp
3BCA  5D              pop bp
3BCB  C2 02 00        ret 2
; data (not reached as code), 5 bytes
3BCE                  db 02 20 50 01 50   ; . P.P

; ---- routine 1771:3BD3  (found by: call)
sub_3BD3:
3BD3  55              push bp
3BD4  89 E5           mov bp, sp
3BD6  81 EC 0E 02     sub sp, 0x20e
3BDA  8B 46 04        mov ax, word ptr [bp + 4]
3BDD  BA 14 00        mov dx, 0x14
3BE0  F7 E2           mul dx
3BE2  C4 3E 1B A9     les di, ptr [0xa91b]
3BE6  03 F8           add di, ax
3BE8  89 BE F3 FE     mov word ptr [bp - 0x10d], di
3BEC  8C 86 F5 FE     mov word ptr [bp - 0x10b], es
3BF0  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3BF4  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
3BF9  75 3A           jne 0x3c35
3BFB  BF C0 6A        mov di, 0x6ac0
3BFE  1E              push ds
3BFF  57              push di
3C00  8D BE F8 FE     lea di, [bp - 0x108]
3C04  16              push ss
3C05  57              push di
3C06  B8 00 01        mov ax, 0x100
3C09  50              push ax
3C0A  9A 3C 00 4B 21  call far 214B:003C
3C0F  BF A6 0E        mov di, 0xea6
3C12  1E              push ds
3C13  57              push di
3C14  BF C0 6A        mov di, 0x6ac0
3C17  1E              push ds
3C18  57              push di
3C19  B8 20 00        mov ax, 0x20
3C1C  50              push ax
3C1D  9A 3C 00 4B 21  call far 214B:003C
3C22  BF C6 0E        mov di, 0xec6
3C25  1E              push ds
3C26  57              push di
3C27  BF 00 6B        mov di, 0x6b00
3C2A  1E              push ds
3C2B  57              push di
3C2C  B8 20 00        mov ax, 0x20
3C2F  50              push ax
3C30  9A 3C 00 4B 21  call far 214B:003C
loc_3C35:
3C35  C7 46 FE 01 00  mov word ptr [bp - 2], 1
3C3A  EB 03           jmp 0x3c3f
loc_3C3C:
3C3C  FF 46 FE        inc word ptr [bp - 2]
loc_3C3F:
3C3F  8B 46 FE        mov ax, word ptr [bp - 2]
3C42  05 04 00        add ax, 4
3C45  50              push ax
3C46  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3C4A  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
3C4E  30 E4           xor ah, ah
3C50  50              push ax
3C51  9A 57 0C 4B 21  call far 214B:0C57
3C56  08 C0           or al, al
3C58  74 52           je 0x3cac
3C5A  8D BE F3 FD     lea di, [bp - 0x20d]
3C5E  16              push ss
3C5F  57              push di
3C60  FF 76 FE        push word ptr [bp - 2]
3C63  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3C67  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
3C6B  30 E4           xor ah, ah
3C6D  50              push ax
3C6E  9A 57 0C 4B 21  call far 214B:0C57
3C73  98              cwde
3C74  B1 04           mov cl, 4
3C76  D3 E0           shl ax, cl
3C78  8B 7E FE        mov di, word ptr [bp - 2]
3C7B  B1 05           mov cl, 5
3C7D  D3 E7           shl di, cl
3C7F  03 F8           add di, ax
3C81  81 C7 A0 6A     add di, 0x6aa0
3C85  1E              push ds
3C86  57              push di
3C87  9A 2A 06 E4 23  call far 23E4:062A
3C8C  BF CE 3B        mov di, 0x3bce
3C8F  0E              push cs
3C90  57              push di
3C91  9A B7 06 E4 23  call far 23E4:06B7
3C96  8B 46 FE        mov ax, word ptr [bp - 2]
3C99  05 0B 00        add ax, 0xb
3C9C  50              push ax
3C9D  B0 3D           mov al, 0x3d
3C9F  50              push ax
3CA0  BF 6E A9        mov di, 0xa96e
3CA3  1E              push ds
3CA4  57              push di
3CA5  9A A3 01 4B 21  call far 214B:01A3
3CAA  EB 57           jmp 0x3d03
loc_3CAC:
3CAC  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3CB0  26 8A 05        mov al, byte ptr es:[di]
3CB3  30 E4           xor ah, ah
3CB5  BA BF 00        mov dx, 0xbf
3CB8  F7 E2           mul dx
3CBA  C4 3E 17 A9     les di, ptr [0xa917]
3CBE  03 F8           add di, ax
3CC0  89 BE EF FE     mov word ptr [bp - 0x111], di
3CC4  8C 86 F1 FE     mov word ptr [bp - 0x10f], es
3CC8  FF 76 FE        push word ptr [bp - 2]
3CCB  C4 BE EF FE     les di, ptr [bp - 0x111]
3CCF  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
3CD3  30 E4           xor ah, ah
3CD5  50              push ax
3CD6  9A 57 0C 4B 21  call far 214B:0C57
3CDB  98              cwde
3CDC  B1 04           mov cl, 4
3CDE  D3 E0           shl ax, cl
3CE0  8B 7E FE        mov di, word ptr [bp - 2]
3CE3  B1 05           mov cl, 5
3CE5  D3 E7           shl di, cl
3CE7  03 F8           add di, ax
3CE9  81 C7 A0 6A     add di, 0x6aa0
3CED  1E              push ds
3CEE  57              push di
3CEF  8B 46 FE        mov ax, word ptr [bp - 2]
3CF2  05 0B 00        add ax, 0xb
3CF5  50              push ax
3CF6  B0 3D           mov al, 0x3d
3CF8  50              push ax
3CF9  BF 6E A9        mov di, 0xa96e
3CFC  1E              push ds
3CFD  57              push di
3CFE  9A A3 01 4B 21  call far 214B:01A3
loc_3D03:
3D03  83 7E FE 04     cmp word ptr [bp - 2], 4
3D07  74 03           je 0x3d0c
3D09  E9 30 FF        jmp 0x3c3c
loc_3D0C:
3D0C  31 C0           xor ax, ax
3D0E  89 46 FA        mov word ptr [bp - 6], ax
3D11  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
3D16  75 07           jne 0x3d1f
3D18  55              push bp
3D19  E8 23 FE        call 0x3b3f
3D1C  E9 EB 00        jmp 0x3e0a
loc_3D1F:
3D1F  FF 76 04        push word ptr [bp + 4]
3D22  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3D26  26 8A 05        mov al, byte ptr es:[di]
3D29  30 E4           xor ah, ah
3D2B  50              push ax
3D2C  0E              push cs
3D2D  E8 52 FD        call 0x3a82
3D30  89 46 FA        mov word ptr [bp - 6], ax
3D33  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3D37  26 8A 05        mov al, byte ptr es:[di]
3D3A  30 E4           xor ah, ah
3D3C  3B 06 36 9B     cmp ax, word ptr [0x9b36]
3D40  74 04           je 0x3d46
3D42  B0 00           mov al, 0
3D44  EB 02           jmp 0x3d48
loc_3D46:
3D46  B0 01           mov al, 1
loc_3D48:
3D48  88 86 F7 FE     mov byte ptr [bp - 0x109], al
3D4C  83 7E FA 00     cmp word ptr [bp - 6], 0
3D50  74 1C           je 0x3d6e
3D52  8B 46 FA        mov ax, word ptr [bp - 6]
3D55  D1 E0           shl ax, 1
3D57  8B C8           mov cx, ax
3D59  8A 86 F7 FE     mov al, byte ptr [bp - 0x109]
3D5D  98              cwde
3D5E  BA 28 00        mov dx, 0x28
3D61  F7 E2           mul dx
3D63  8B F8           mov di, ax
3D65  03 F9           add di, cx
3D67  83 BD 3E 9A 00  cmp word ptr [di - 0x65c2], 0
3D6C  75 07           jne 0x3d75
loc_3D6E:
3D6E  55              push bp
3D6F  E8 CD FD        call 0x3b3f
3D72  E9 95 00        jmp 0x3e0a
loc_3D75:
3D75  A0 B2 AA        mov al, byte ptr [0xaab2]
3D78  30 E4           xor ah, ah
3D7A  89 46 FC        mov word ptr [bp - 4], ax
3D7D  8B 46 FA        mov ax, word ptr [bp - 6]
3D80  D1 E0           shl ax, 1
3D82  8B C8           mov cx, ax
3D84  8A 86 F7 FE     mov al, byte ptr [bp - 0x109]
3D88  98              cwde
3D89  BA 28 00        mov dx, 0x28
3D8C  F7 E2           mul dx
3D8E  8B F8           mov di, ax
3D90  03 F9           add di, cx
3D92  8B 85 3E 9A     mov ax, word ptr [di - 0x65c2]
3D96  89 46 F8        mov word ptr [bp - 8], ax
3D99  FF 76 F8        push word ptr [bp - 8]
3D9C  B8 10 00        mov ax, 0x10
3D9F  50              push ax
3DA0  B8 2B 00        mov ax, 0x2b
3DA3  50              push ax
3DA4  0E              push cs
3DA5  E8 3D F1        call 0x2ee5
3DA8  8B 46 F8        mov ax, word ptr [bp - 8]
3DAB  BA 14 00        mov dx, 0x14
3DAE  F7 E2           mul dx
3DB0  C4 3E 1B A9     les di, ptr [0xa91b]
3DB4  03 F8           add di, ax
3DB6  26 8A 45 06     mov al, byte ptr es:[di + 6]
3DBA  30 E4           xor ah, ah
3DBC  BA 13 00        mov dx, 0x13
3DBF  F7 E2           mul dx
3DC1  8B F8           mov di, ax
3DC3  81 C7 B6 69     add di, 0x69b6
3DC7  1E              push ds
3DC8  57              push di
3DC9  B0 11           mov al, 0x11
3DCB  50              push ax
3DCC  B0 2B           mov al, 0x2b
3DCE  50              push ax
3DCF  BF 6E A9        mov di, 0xa96e
3DD2  1E              push ds
3DD3  57              push di
3DD4  9A 6D 02 4B 21  call far 214B:026D
3DD9  B8 07 00        mov ax, 7
3DDC  50              push ax
3DDD  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3DE1  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
3DE5  30 E4           xor ah, ah
3DE7  50              push ax
3DE8  9A 57 0C 4B 21  call far 214B:0C57
3DED  08 C0           or al, al
3DEF  74 19           je 0x3e0a
3DF1  8A 46 FC        mov al, byte ptr [bp - 4]
3DF4  50              push ax
3DF5  BF D1 3B        mov di, 0x3bd1
3DF8  0E              push cs
3DF9  57              push di
3DFA  B0 10           mov al, 0x10
3DFC  50              push ax
3DFD  B0 3D           mov al, 0x3d
3DFF  50              push ax
3E00  BF 6E A9        mov di, 0xa96e
3E03  1E              push ds
3E04  57              push di
3E05  9A C8 02 4B 21  call far 214B:02C8
loc_3E0A:
3E0A  C4 BE F3 FE     les di, ptr [bp - 0x10d]
3E0E  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
3E13  75 14           jne 0x3e29
3E15  8D BE F8 FE     lea di, [bp - 0x108]
3E19  16              push ss
3E1A  57              push di
3E1B  BF C0 6A        mov di, 0x6ac0
3E1E  1E              push ds
3E1F  57              push di
3E20  B8 00 01        mov ax, 0x100
3E23  50              push ax
3E24  9A 3C 00 4B 21  call far 214B:003C
loc_3E29:
3E29  89 EC           mov sp, bp
3E2B  5D              pop bp
3E2C  C2 02 00        ret 2

; ---- routine 1771:3E2F  (found by: call)
sub_3E2F:
3E2F  55              push bp
3E30  89 E5           mov bp, sp
3E32  81 EC 06 01     sub sp, 0x106
3E36  C7 46 FC 01 00  mov word ptr [bp - 4], 1
3E3B  EB 03           jmp 0x3e40
loc_3E3D:
3E3D  FF 46 FC        inc word ptr [bp - 4]
loc_3E40:
3E40  C7 46 FE 0B 00  mov word ptr [bp - 2], 0xb
3E45  EB 03           jmp 0x3e4a
loc_3E47:
3E47  FF 4E FE        dec word ptr [bp - 2]
loc_3E4A:
3E4A  8B 46 FE        mov ax, word ptr [bp - 2]
3E4D  8B 7E 04        mov di, word ptr [bp + 4]
3E50  03 F8           add di, ax
3E52  36 8A 45 E4     mov al, byte ptr ss:[di - 0x1c]
3E56  30 E4           xor ah, ah
3E58  3B 46 08        cmp ax, word ptr [bp + 8]
3E5B  73 03           jae 0x3e60
3E5D  E9 80 00        jmp 0x3ee0
loc_3E60:
3E60  8B 46 FE        mov ax, word ptr [bp - 2]
3E63  8B 7E 04        mov di, word ptr [bp + 4]
3E66  03 F8           add di, ax
3E68  36 8A 45 E4     mov al, byte ptr ss:[di - 0x1c]
3E6C  30 E4           xor ah, ah
3E6E  3B 46 06        cmp ax, word ptr [bp + 6]
3E71  77 6D           ja 0x3ee0
3E73  8D BE FA FE     lea di, [bp - 0x106]
3E77  16              push ss
3E78  57              push di
3E79  8B 46 FE        mov ax, word ptr [bp - 2]
3E7C  8B 7E 04        mov di, word ptr [bp + 4]
3E7F  03 F8           add di, ax
3E81  36 8A 45 E4     mov al, byte ptr ss:[di - 0x1c]
3E85  30 E4           xor ah, ah
3E87  8B C8           mov cx, ax
3E89  8B 46 FC        mov ax, word ptr [bp - 4]
3E8C  BA 0E 00        mov dx, 0xe
3E8F  F7 E2           mul dx
3E91  8B F8           mov di, ax
3E93  03 F9           add di, cx
3E95  8A 85 E6 0E     mov al, byte ptr [di + 0xee6]
3E99  50              push ax
3E9A  9A 5A 07 E4 23  call far 23E4:075A
3E9F  8B 7E 04        mov di, word ptr [bp + 4]
3EA2  81 C7 F0 FF     add di, 0xfff0
3EA6  16              push ss
3EA7  57              push di
3EA8  9A E3 06 E4 23  call far 23E4:06E3
3EAD  40              inc ax
3EAE  89 46 FA        mov word ptr [bp - 6], ax
3EB1  83 7E FA 01     cmp word ptr [bp - 6], 1
3EB5  76 29           jbe 0x3ee0
3EB7  8B 46 FA        mov ax, word ptr [bp - 6]
3EBA  8B 7E 04        mov di, word ptr [bp + 4]
3EBD  03 F8           add di, ax
3EBF  36 C6 45 EF 00  mov byte ptr ss:[di - 0x11], 0
3EC4  8B 46 FE        mov ax, word ptr [bp - 2]
3EC7  8B 7E 04        mov di, word ptr [bp + 4]
3ECA  03 F8           add di, ax
3ECC  36 C6 45 E4 00  mov byte ptr ss:[di - 0x1c], 0
3ED1  8A 56 FE        mov dl, byte ptr [bp - 2]
3ED4  8B 46 FA        mov ax, word ptr [bp - 6]
3ED7  8B 7E 04        mov di, word ptr [bp + 4]
3EDA  03 F8           add di, ax
3EDC  36 88 55 D9     mov byte ptr ss:[di - 0x27], dl
loc_3EE0:
3EE0  83 7E FE 02     cmp word ptr [bp - 2], 2
3EE4  74 03           je 0x3ee9
3EE6  E9 5E FF        jmp 0x3e47
loc_3EE9:
3EE9  83 7E FC 04     cmp word ptr [bp - 4], 4
3EED  74 03           je 0x3ef2
3EEF  E9 4B FF        jmp 0x3e3d
loc_3EF2:
3EF2  89 EC           mov sp, bp
3EF4  5D              pop bp
3EF5  C2 06 00        ret 6

; ---- routine 1771:3EF8  (found by: call, far)
sub_3EF8:
3EF8  55              push bp
3EF9  89 E5           mov bp, sp
3EFB  83 EC 32        sub sp, 0x32
3EFE  C6 46 FB 00     mov byte ptr [bp - 5], 0
3F02  EB 03           jmp 0x3f07
loc_3F04:
3F04  FE 46 FB        inc byte ptr [bp - 5]
loc_3F07:
3F07  8A 46 FB        mov al, byte ptr [bp - 5]
3F0A  98              cwde
3F0B  8B F8           mov di, ax
3F0D  D1 E7           shl di, 1
3F0F  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
3F13  BA BF 00        mov dx, 0xbf
3F16  F7 E2           mul dx
3F18  C4 3E 17 A9     les di, ptr [0xa917]
3F1C  03 F8           add di, ax
3F1E  89 7E D6        mov word ptr [bp - 0x2a], di
3F21  8C 46 D8        mov word ptr [bp - 0x28], es
3F24  8A 46 FB        mov al, byte ptr [bp - 5]
3F27  98              cwde
3F28  BA 28 00        mov dx, 0x28
3F2B  F7 E2           mul dx
3F2D  8B F8           mov di, ax
3F2F  31 C0           xor ax, ax
3F31  89 85 40 9A     mov word ptr [di - 0x65c0], ax
3F35  C4 7E D6        les di, ptr [bp - 0x2a]
3F38  26 8B 45 02     mov ax, word ptr es:[di + 2]
3F3C  BA 14 00        mov dx, 0x14
3F3F  F7 E2           mul dx
3F41  C4 3E 1B A9     les di, ptr [0xa91b]
3F45  03 F8           add di, ax
3F47  26 80 7D 06 01  cmp byte ptr es:[di + 6], 1
3F4C  75 11           jne 0x3f5f
3F4E  8A 46 FB        mov al, byte ptr [bp - 5]
3F51  98              cwde
3F52  BA 28 00        mov dx, 0x28
3F55  F7 E2           mul dx
3F57  8B F8           mov di, ax
3F59  31 C0           xor ax, ax
3F5B  89 85 42 9A     mov word ptr [di - 0x65be], ax
loc_3F5F:
3F5F  C6 46 F0 0A     mov byte ptr [bp - 0x10], 0xa
3F63  C6 46 E5 0A     mov byte ptr [bp - 0x1b], 0xa
3F67  C7 46 FE 02 00  mov word ptr [bp - 2], 2
3F6C  EB 03           jmp 0x3f71
loc_3F6E:
3F6E  FF 46 FE        inc word ptr [bp - 2]
loc_3F71:
3F71  8B 46 FE        mov ax, word ptr [bp - 2]
3F74  D1 E0           shl ax, 1
3F76  C4 7E D6        les di, ptr [bp - 0x2a]
3F79  03 F8           add di, ax
3F7B  26 8B 45 FE     mov ax, word ptr es:[di - 2]
3F7F  BA 14 00        mov dx, 0x14
3F82  F7 E2           mul dx
3F84  C4 3E 1B A9     les di, ptr [0xa91b]
3F88  03 F8           add di, ax
3F8A  89 7E D2        mov word ptr [bp - 0x2e], di
3F8D  8C 46 D4        mov word ptr [bp - 0x2c], es
3F90  C4 7E D2        les di, ptr [bp - 0x2e]
3F93  26 80 7D 06 01  cmp byte ptr es:[di + 6], 1
3F98  74 2D           je 0x3fc7
3F9A  B8 07 00        mov ax, 7
3F9D  50              push ax
3F9E  C4 7E D2        les di, ptr [bp - 0x2e]
3FA1  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
3FA5  30 E4           xor ah, ah
3FA7  50              push ax
3FA8  9A 57 0C 4B 21  call far 214B:0C57
3FAD  08 C0           or al, al
3FAF  75 16           jne 0x3fc7
3FB1  8B 46 FE        mov ax, word ptr [bp - 2]
3FB4  D1 E0           shl ax, 1
3FB6  C4 7E D6        les di, ptr [bp - 0x2a]
3FB9  03 F8           add di, ax
3FBB  26 FF 75 FE     push word ptr es:[di - 2]
3FBF  0E              push cs
3FC0  E8 53 F2        call 0x3216
3FC3  08 C0           or al, al
3FC5  74 09           je 0x3fd0
loc_3FC7:
3FC7  8B 7E FE        mov di, word ptr [bp - 2]
3FCA  C6 43 EF 00     mov byte ptr [bp + di - 0x11], 0
3FCE  EB 0D           jmp 0x3fdd
loc_3FD0:
3FD0  C4 7E D2        les di, ptr [bp - 0x2e]
3FD3  26 8A 45 06     mov al, byte ptr es:[di + 6]
3FD7  8B 7E FE        mov di, word ptr [bp - 2]
3FDA  88 43 EF        mov byte ptr [bp + di - 0x11], al
loc_3FDD:
3FDD  80 7E FB 00     cmp byte ptr [bp - 5], 0
3FE1  74 04           je 0x3fe7
3FE3  B0 00           mov al, 0
3FE5  EB 02           jmp 0x3fe9
loc_3FE7:
3FE7  B0 01           mov al, 1
loc_3FE9:
3FE9  98              cwde
3FEA  8B F8           mov di, ax
3FEC  D1 E7           shl di, 1
3FEE  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
3FF2  BA BF 00        mov dx, 0xbf
3FF5  F7 E2           mul dx
3FF7  C4 3E 17 A9     les di, ptr [0xa917]
3FFB  03 F8           add di, ax
3FFD  89 7E D2        mov word ptr [bp - 0x2e], di
4000  8C 46 D4        mov word ptr [bp - 0x2c], es
4003  8B 46 FE        mov ax, word ptr [bp - 2]
4006  D1 E0           shl ax, 1
4008  C4 7E D2        les di, ptr [bp - 0x2e]
400B  03 F8           add di, ax
400D  26 8B 45 FE     mov ax, word ptr es:[di - 2]
4011  BA 14 00        mov dx, 0x14
4014  F7 E2           mul dx
4016  C4 3E 1B A9     les di, ptr [0xa91b]
401A  03 F8           add di, ax
401C  89 7E CE        mov word ptr [bp - 0x32], di
401F  8C 46 D0        mov word ptr [bp - 0x30], es
4022  8B 46 FE        mov ax, word ptr [bp - 2]
4025  D1 E0           shl ax, 1
4027  C4 7E D2        les di, ptr [bp - 0x2e]
402A  03 F8           add di, ax
402C  26 FF 75 FE     push word ptr es:[di - 2]
4030  0E              push cs
4031  E8 E2 F1        call 0x3216
4034  08 C0           or al, al
4036  74 09           je 0x4041
4038  8B 7E FE        mov di, word ptr [bp - 2]
403B  C6 43 E4 00     mov byte ptr [bp + di - 0x1c], 0
403F  EB 0D           jmp 0x404e
loc_4041:
4041  C4 7E CE        les di, ptr [bp - 0x32]
4044  26 8A 45 06     mov al, byte ptr es:[di + 6]
4048  8B 7E FE        mov di, word ptr [bp - 2]
404B  88 43 E4        mov byte ptr [bp + di - 0x1c], al
loc_404E:
404E  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
4052  74 03           je 0x4057
4054  E9 17 FF        jmp 0x3f6e
loc_4057:
4057  C7 46 FE 02 00  mov word ptr [bp - 2], 2
405C  EB 03           jmp 0x4061
loc_405E:
405E  FF 46 FE        inc word ptr [bp - 2]
loc_4061:
4061  8B 46 FE        mov ax, word ptr [bp - 2]
4064  D1 E0           shl ax, 1
4066  C4 7E D6        les di, ptr [bp - 0x2a]
4069  03 F8           add di, ax
406B  26 8B 45 FE     mov ax, word ptr es:[di - 2]
406F  BA 14 00        mov dx, 0x14
4072  F7 E2           mul dx
4074  C4 3E 1B A9     les di, ptr [0xa91b]
4078  03 F8           add di, ax
407A  89 7E D2        mov word ptr [bp - 0x2e], di
407D  8C 46 D4        mov word ptr [bp - 0x2c], es
4080  B8 07 00        mov ax, 7
4083  50              push ax
4084  C4 7E D2        les di, ptr [bp - 0x2e]
4087  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
408B  30 E4           xor ah, ah
408D  50              push ax
408E  9A 57 0C 4B 21  call far 214B:0C57
4093  08 C0           or al, al
4095  74 60           je 0x40f7
4097  C7 46 FC 02 00  mov word ptr [bp - 4], 2
409C  EB 03           jmp 0x40a1
loc_409E:
409E  FF 46 FC        inc word ptr [bp - 4]
loc_40A1:
40A1  8B 46 FE        mov ax, word ptr [bp - 2]
40A4  D1 E0           shl ax, 1
40A6  8B C8           mov cx, ax
40A8  8A 46 FB        mov al, byte ptr [bp - 5]
40AB  98              cwde
40AC  BA 28 00        mov dx, 0x28
40AF  F7 E2           mul dx
40B1  8B F8           mov di, ax
40B3  03 F9           add di, cx
40B5  8B 9D 3E 9A     mov bx, word ptr [di - 0x65c2]
40B9  8B 46 FC        mov ax, word ptr [bp - 4]
40BC  D1 E0           shl ax, 1
40BE  8B C8           mov cx, ax
40C0  80 7E FB 00     cmp byte ptr [bp - 5], 0
40C4  74 04           je 0x40ca
40C6  B0 00           mov al, 0
40C8  EB 02           jmp 0x40cc
loc_40CA:
40CA  B0 01           mov al, 1
loc_40CC:
40CC  98              cwde
40CD  8B F8           mov di, ax
40CF  D1 E7           shl di, 1
40D1  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
40D5  BA BF 00        mov dx, 0xbf
40D8  F7 E2           mul dx
40DA  C4 3E 17 A9     les di, ptr [0xa917]
40DE  03 F8           add di, ax
40E0  03 F9           add di, cx
40E2  26 8B 45 FE     mov ax, word ptr es:[di - 2]
40E6  3B C3           cmp ax, bx
40E8  75 07           jne 0x40f1
40EA  8B 7E FC        mov di, word ptr [bp - 4]
40ED  C6 43 E4 00     mov byte ptr [bp + di - 0x1c], 0
loc_40F1:
40F1  83 7E FC 0B     cmp word ptr [bp - 4], 0xb
40F5  75 A7           jne 0x409e
loc_40F7:
40F7  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
40FB  74 03           je 0x4100
40FD  E9 5E FF        jmp 0x405e
loc_4100:
4100  8D 7E DA        lea di, [bp - 0x26]
4103  16              push ss
4104  57              push di
4105  B8 0B 00        mov ax, 0xb
4108  50              push ax
4109  31 C0           xor ax, ax
410B  50              push ax
410C  9A 18 00 4B 21  call far 214B:0018
4111  B8 0C 00        mov ax, 0xc
4114  50              push ax
4115  B8 0D 00        mov ax, 0xd
4118  50              push ax
4119  55              push bp
411A  E8 12 FD        call 0x3e2f
411D  B8 09 00        mov ax, 9
4120  50              push ax
4121  B8 0B 00        mov ax, 0xb
4124  50              push ax
4125  55              push bp
4126  E8 06 FD        call 0x3e2f
4129  B8 05 00        mov ax, 5
412C  50              push ax
412D  B8 08 00        mov ax, 8
4130  50              push ax
4131  55              push bp
4132  E8 FA FC        call 0x3e2f
4135  B8 01 00        mov ax, 1
4138  50              push ax
4139  B8 01 00        mov ax, 1
413C  50              push ax
413D  55              push bp
413E  E8 EE FC        call 0x3e2f
4141  B8 02 00        mov ax, 2
4144  50              push ax
4145  B8 04 00        mov ax, 4
4148  50              push ax
4149  55              push bp
414A  E8 E2 FC        call 0x3e2f
414D  C7 46 FE 02 00  mov word ptr [bp - 2], 2
4152  EB 03           jmp 0x4157
loc_4154:
4154  FF 46 FE        inc word ptr [bp - 2]
loc_4157:
4157  8B 46 FE        mov ax, word ptr [bp - 2]
415A  D1 E0           shl ax, 1
415C  C4 7E D6        les di, ptr [bp - 0x2a]
415F  03 F8           add di, ax
4161  26 8B 45 FE     mov ax, word ptr es:[di - 2]
4165  BA 14 00        mov dx, 0x14
4168  F7 E2           mul dx
416A  C4 3E 1B A9     les di, ptr [0xa91b]
416E  03 F8           add di, ax
4170  89 7E D2        mov word ptr [bp - 0x2e], di
4173  8C 46 D4        mov word ptr [bp - 0x2c], es
4176  B8 07 00        mov ax, 7
4179  50              push ax
417A  C4 7E D2        les di, ptr [bp - 0x2e]
417D  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
4181  30 E4           xor ah, ah
4183  50              push ax
4184  9A 57 0C 4B 21  call far 214B:0C57
4189  08 C0           or al, al
418B  75 1A           jne 0x41a7
418D  8B 46 FE        mov ax, word ptr [bp - 2]
4190  D1 E0           shl ax, 1
4192  8B C8           mov cx, ax
4194  8A 46 FB        mov al, byte ptr [bp - 5]
4197  98              cwde
4198  BA 28 00        mov dx, 0x28
419B  F7 E2           mul dx
419D  8B F8           mov di, ax
419F  03 F9           add di, cx
41A1  31 C0           xor ax, ax
41A3  89 85 3E 9A     mov word ptr [di - 0x65c2], ax
loc_41A7:
41A7  B8 07 00        mov ax, 7
41AA  50              push ax
41AB  C4 7E D2        les di, ptr [bp - 0x2e]
41AE  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
41B2  30 E4           xor ah, ah
41B4  50              push ax
41B5  9A 57 0C 4B 21  call far 214B:0C57
41BA  08 C0           or al, al
41BC  74 03           je 0x41c1
41BE  E9 86 00        jmp 0x4247
loc_41C1:
41C1  B8 08 00        mov ax, 8
41C4  50              push ax
41C5  C4 7E D6        les di, ptr [bp - 0x2a]
41C8  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
41CC  30 E4           xor ah, ah
41CE  50              push ax
41CF  9A 57 0C 4B 21  call far 214B:0C57
41D4  08 C0           or al, al
41D6  74 6F           je 0x4247
41D8  8B 7E FE        mov di, word ptr [bp - 2]
41DB  80 7B D9 00     cmp byte ptr [bp + di - 0x27], 0
41DF  76 4C           jbe 0x422d
41E1  8B 7E FE        mov di, word ptr [bp - 2]
41E4  8A 43 D9        mov al, byte ptr [bp + di - 0x27]
41E7  30 E4           xor ah, ah
41E9  D1 E0           shl ax, 1
41EB  8B C8           mov cx, ax
41ED  80 7E FB 00     cmp byte ptr [bp - 5], 0
41F1  74 04           je 0x41f7
41F3  B0 00           mov al, 0
41F5  EB 02           jmp 0x41f9
loc_41F7:
41F7  B0 01           mov al, 1
loc_41F9:
41F9  98              cwde
41FA  8B F8           mov di, ax
41FC  D1 E7           shl di, 1
41FE  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
4202  BA BF 00        mov dx, 0xbf
4205  F7 E2           mul dx
4207  C4 3E 17 A9     les di, ptr [0xa917]
420B  03 F8           add di, ax
420D  03 F9           add di, cx
420F  26 8B 5D FE     mov bx, word ptr es:[di - 2]
4213  8B 46 FE        mov ax, word ptr [bp - 2]
4216  D1 E0           shl ax, 1
4218  8B C8           mov cx, ax
421A  8A 46 FB        mov al, byte ptr [bp - 5]
421D  98              cwde
421E  BA 28 00        mov dx, 0x28
4221  F7 E2           mul dx
4223  8B F8           mov di, ax
4225  03 F9           add di, cx
4227  89 9D 3E 9A     mov word ptr [di - 0x65c2], bx
422B  EB 1A           jmp 0x4247
loc_422D:
422D  8B 46 FE        mov ax, word ptr [bp - 2]
4230  D1 E0           shl ax, 1
4232  8B C8           mov cx, ax
4234  8A 46 FB        mov al, byte ptr [bp - 5]
4237  98              cwde
4238  BA 28 00        mov dx, 0x28
423B  F7 E2           mul dx
423D  8B F8           mov di, ax
423F  03 F9           add di, cx
4241  31 C0           xor ax, ax
4243  89 85 3E 9A     mov word ptr [di - 0x65c2], ax
loc_4247:
4247  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
424B  74 03           je 0x4250
424D  E9 04 FF        jmp 0x4154
loc_4250:
4250  80 7E FB 01     cmp byte ptr [bp - 5], 1
4254  74 03           je 0x4259
4256  E9 AB FC        jmp 0x3f04
loc_4259:
4259  89 EC           mov sp, bp
425B  5D              pop bp
425C  CB              retf
; data (not reached as code), 95 bytes
425D                  pstr 'two footed'
4268                  db 01 FE   ; ..
426A                  pstr 'suspended'
4274                  pstr 'injured'
427C                  pstr 'booked'
4283                  pstr 'sent off'
428C                  pstr 'substituted'
4298                  pstr 'ready to play'
42A6                  pstr 'selected'
42AF                  pstr 'on the bench'

; ---- routine 1771:42BC  (found by: call, far)
sub_42BC:
42BC  55              push bp
42BD  89 E5           mov bp, sp
42BF  81 EC 08 01     sub sp, 0x108
42C3  BF 6E 48        mov di, 0x486e
42C6  1E              push ds
42C7  57              push di
42C8  BF 6E A9        mov di, 0xa96e
42CB  1E              push ds
42CC  57              push di
42CD  9A 29 03 4B 21  call far 214B:0329
42D2  83 7E 06 00     cmp word ptr [bp + 6], 0
42D6  75 03           jne 0x42db
42D8  E9 78 05        jmp 0x4853
loc_42DB:
42DB  8B 46 06        mov ax, word ptr [bp + 6]
42DE  BA 14 00        mov dx, 0x14
42E1  F7 E2           mul dx
42E3  C4 3E 1B A9     les di, ptr [0xa91b]
42E7  03 F8           add di, ax
42E9  89 7E F8        mov word ptr [bp - 8], di
42EC  8C 46 FA        mov word ptr [bp - 6], es
42EF  FF 76 06        push word ptr [bp + 6]
42F2  B8 08 00        mov ax, 8
42F5  50              push ax
42F6  B8 02 00        mov ax, 2
42F9  50              push ax
42FA  0E              push cs
42FB  E8 E7 EB        call 0x2ee5
42FE  8D BE F8 FE     lea di, [bp - 0x108]
4302  16              push ss
4303  57              push di
4304  C4 7E F8        les di, ptr [bp - 8]
4307  26 8A 45 01     mov al, byte ptr es:[di + 1]
430B  30 E4           xor ah, ah
430D  31 D2           xor dx, dx
430F  52              push dx
4310  50              push ax
4311  9A DA 09 4B 21  call far 214B:09DA
4316  B0 08           mov al, 8
4318  50              push ax
4319  B0 13           mov al, 0x13
431B  50              push ax
431C  BF 6E A9        mov di, 0xa96e
431F  1E              push ds
4320  57              push di
4321  9A A3 01 4B 21  call far 214B:01A3
4326  8D BE F8 FE     lea di, [bp - 0x108]
432A  16              push ss
432B  57              push di
432C  C4 7E F8        les di, ptr [bp - 8]
432F  26 8B 45 08     mov ax, word ptr es:[di + 8]
4333  31 D2           xor dx, dx
4335  52              push dx
4336  50              push ax
4337  9A DA 09 4B 21  call far 214B:09DA
433C  B0 08           mov al, 8
433E  50              push ax
433F  B0 18           mov al, 0x18
4341  50              push ax
4342  BF 6E A9        mov di, 0xa96e
4345  1E              push ds
4346  57              push di
4347  9A A3 01 4B 21  call far 214B:01A3
434C  8D BE F8 FE     lea di, [bp - 0x108]
4350  16              push ss
4351  57              push di
4352  C4 7E F8        les di, ptr [bp - 8]
4355  26 8B 45 0A     mov ax, word ptr es:[di + 0xa]
4359  31 D2           xor dx, dx
435B  52              push dx
435C  50              push ax
435D  9A DA 09 4B 21  call far 214B:09DA
4362  B0 08           mov al, 8
4364  50              push ax
4365  B0 1E           mov al, 0x1e
4367  50              push ax
4368  BF 6E A9        mov di, 0xa96e
436B  1E              push ds
436C  57              push di
436D  9A A3 01 4B 21  call far 214B:01A3
4372  8D BE F8 FE     lea di, [bp - 0x108]
4376  16              push ss
4377  57              push di
4378  FF 76 06        push word ptr [bp + 6]
437B  0E              push cs
437C  E8 2E EC        call 0x2fad
437F  31 D2           xor dx, dx
4381  B9 0C 00        mov cx, 0xc
4384  F7 F1           div cx
4386  31 D2           xor dx, dx
4388  52              push dx
4389  50              push ax
438A  9A DA 09 4B 21  call far 214B:09DA
438F  B0 08           mov al, 8
4391  50              push ax
4392  B0 21           mov al, 0x21
4394  50              push ax
4395  BF 6E A9        mov di, 0xa96e
4398  1E              push ds
4399  57              push di
439A  9A 6D 02 4B 21  call far 214B:026D
439F  8D BE F8 FE     lea di, [bp - 0x108]
43A3  16              push ss
43A4  57              push di
43A5  FF 76 06        push word ptr [bp + 6]
43A8  0E              push cs
43A9  E8 01 EC        call 0x2fad
43AC  31 D2           xor dx, dx
43AE  B9 0C 00        mov cx, 0xc
43B1  F7 F1           div cx
43B3  92              xchg dx, ax
43B4  31 D2           xor dx, dx
43B6  52              push dx
43B7  50              push ax
43B8  9A DA 09 4B 21  call far 214B:09DA
43BD  B0 08           mov al, 8
43BF  50              push ax
43C0  B0 24           mov al, 0x24
43C2  50              push ax
43C3  BF 6E A9        mov di, 0xa96e
43C6  1E              push ds
43C7  57              push di
43C8  9A A3 01 4B 21  call far 214B:01A3
43CD  FF 76 06        push word ptr [bp + 6]
43D0  0E              push cs
43D1  E8 6D EC        call 0x3041
43D4  08 C0           or al, al
43D6  74 17           je 0x43ef
43D8  BF 5D 42        mov di, 0x425d
43DB  0E              push cs
43DC  57              push di
43DD  B0 08           mov al, 8
43DF  50              push ax
43E0  B0 28           mov al, 0x28
43E2  50              push ax
43E3  BF 6E A9        mov di, 0xa96e
43E6  1E              push ds
43E7  57              push di
43E8  9A 6D 02 4B 21  call far 214B:026D
43ED  EB 28           jmp 0x4417
loc_43EF:
43EF  FF 76 06        push word ptr [bp + 6]
43F2  0E              push cs
43F3  E8 92 EC        call 0x3088
43F6  98              cwde
43F7  8B F8           mov di, ax
43F9  D1 E7           shl di, 1
43FB  8B F7           mov si, di
43FD  D1 E7           shl di, 1
43FF  03 FE           add di, si
4401  81 C7 2C 0F     add di, 0xf2c
4405  1E              push ds
4406  57              push di
4407  B0 08           mov al, 8
4409  50              push ax
440A  B0 28           mov al, 0x28
440C  50              push ax
440D  BF 6E A9        mov di, 0xa96e
4410  1E              push ds
4411  57              push di
4412  9A 6D 02 4B 21  call far 214B:026D
loc_4417:
4417  C4 7E F8        les di, ptr [bp - 8]
441A  26 8A 45 06     mov al, byte ptr es:[di + 6]
441E  30 E4           xor ah, ah
4420  BA 13 00        mov dx, 0x13
4423  F7 E2           mul dx
4425  8B F8           mov di, ax
4427  81 C7 B6 69     add di, 0x69b6
442B  1E              push ds
442C  57              push di
442D  B0 0A           mov al, 0xa
442F  50              push ax
4430  B0 02           mov al, 2
4432  50              push ax
4433  BF 6E A9        mov di, 0xa96e
4436  1E              push ds
4437  57              push di
4438  9A 6D 02 4B 21  call far 214B:026D
443D  C4 7E F8        les di, ptr [bp - 8]
4440  26 8A 45 07     mov al, byte ptr es:[di + 7]
4444  30 E4           xor ah, ah
4446  BA 13 00        mov dx, 0x13
4449  F7 E2           mul dx
444B  8B F8           mov di, ax
444D  81 C7 B6 69     add di, 0x69b6
4451  1E              push ds
4452  57              push di
4453  B0 0A           mov al, 0xa
4455  50              push ax
4456  B0 15           mov al, 0x15
4458  50              push ax
4459  BF 6E A9        mov di, 0xa96e
445C  1E              push ds
445D  57              push di
445E  9A 6D 02 4B 21  call far 214B:026D
4463  FF 76 06        push word ptr [bp + 6]
4466  0E              push cs
4467  E8 91 EB        call 0x2ffb
446A  30 E4           xor ah, ah
446C  8B F8           mov di, ax
446E  8A 85 C4 78     mov al, byte ptr [di + 0x78c4]
4472  30 E4           xor ah, ah
4474  8B F8           mov di, ax
4476  B1 04           mov cl, 4
4478  D3 E7           shl di, cl
447A  81 C7 B4 6E     add di, 0x6eb4
447E  1E              push ds
447F  57              push di
4480  B0 13           mov al, 0x13
4482  50              push ax
4483  B0 30           mov al, 0x30
4485  50              push ax
4486  BF 6E A9        mov di, 0xa96e
4489  1E              push ds
448A  57              push di
448B  9A 6D 02 4B 21  call far 214B:026D
4490  C4 7E F8        les di, ptr [bp - 8]
4493  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
4498  75 2E           jne 0x44c8
449A  C4 7E F8        les di, ptr [bp - 8]
449D  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
44A1  98              cwde
44A2  8B F8           mov di, ax
44A4  8A 85 D5 78     mov al, byte ptr [di + 0x78d5]
44A8  30 E4           xor ah, ah
44AA  8B F8           mov di, ax
44AC  B1 04           mov cl, 4
44AE  D3 E7           shl di, cl
44B0  81 C7 B4 6E     add di, 0x6eb4
44B4  1E              push ds
44B5  57              push di
44B6  B0 14           mov al, 0x14
44B8  50              push ax
44B9  B0 30           mov al, 0x30
44BB  50              push ax
44BC  BF 6E A9        mov di, 0xa96e
44BF  1E              push ds
44C0  57              push di
44C1  9A 6D 02 4B 21  call far 214B:026D
44C6  EB 2C           jmp 0x44f4
loc_44C8:
44C8  C4 7E F8        les di, ptr [bp - 8]
44CB  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
44CF  98              cwde
44D0  8B F8           mov di, ax
44D2  8A 85 D5 78     mov al, byte ptr [di + 0x78d5]
44D6  30 E4           xor ah, ah
44D8  8B F8           mov di, ax
44DA  B1 04           mov cl, 4
44DC  D3 E7           shl di, cl
44DE  81 C7 B4 6E     add di, 0x6eb4
44E2  1E              push ds
44E3  57              push di
44E4  B0 14           mov al, 0x14
44E6  50              push ax
44E7  B0 30           mov al, 0x30
44E9  50              push ax
44EA  BF 6E A9        mov di, 0xa96e
44ED  1E              push ds
44EE  57              push di
44EF  9A 6D 02 4B 21  call far 214B:026D
loc_44F4:
44F4  C4 7E F8        les di, ptr [bp - 8]
44F7  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
44FB  98              cwde
44FC  8B F8           mov di, ax
44FE  8A 85 F6 78     mov al, byte ptr [di + 0x78f6]
4502  30 E4           xor ah, ah
4504  8B F8           mov di, ax
4506  B1 04           mov cl, 4
4508  D3 E7           shl di, cl
450A  81 C7 B4 6E     add di, 0x6eb4
450E  1E              push ds
450F  57              push di
4510  B0 15           mov al, 0x15
4512  50              push ax
4513  B0 30           mov al, 0x30
4515  50              push ax
4516  BF 6E A9        mov di, 0xa96e
4519  1E              push ds
451A  57              push di
451B  9A 6D 02 4B 21  call far 214B:026D
4520  C4 7E F8        les di, ptr [bp - 8]
4523  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
4527  98              cwde
4528  99              cdq
4529  52              push dx
452A  50              push ax
452B  B8 20 00        mov ax, 0x20
452E  31 D2           xor dx, dx
4530  52              push dx
4531  50              push ax
4532  9A 1C 0D 4B 21  call far 214B:0D1C
4537  8B F8           mov di, ax
4539  8A 85 A3 78     mov al, byte ptr [di + 0x78a3]
453D  30 E4           xor ah, ah
453F  8B F8           mov di, ax
4541  B1 04           mov cl, 4
4543  D3 E7           shl di, cl
4545  81 C7 B4 6E     add di, 0x6eb4
4549  1E              push ds
454A  57              push di
454B  B0 16           mov al, 0x16
454D  50              push ax
454E  B0 30           mov al, 0x30
4550  50              push ax
4551  BF 6E A9        mov di, 0xa96e
4554  1E              push ds
4555  57              push di
4556  9A 6D 02 4B 21  call far 214B:026D
455B  FF 76 06        push word ptr [bp + 6]
455E  0E              push cs
455F  E8 77 EB        call 0x30d9
4562  8B F8           mov di, ax
4564  8A 85 17 79     mov al, byte ptr [di + 0x7917]
4568  30 E4           xor ah, ah
456A  8B F8           mov di, ax
456C  B1 04           mov cl, 4
456E  D3 E7           shl di, cl
4570  81 C7 B4 6E     add di, 0x6eb4
4574  1E              push ds
4575  57              push di
4576  B0 17           mov al, 0x17
4578  50              push ax
4579  B0 30           mov al, 0x30
457B  50              push ax
457C  BF 6E A9        mov di, 0xa96e
457F  1E              push ds
4580  57              push di
4581  9A 6D 02 4B 21  call far 214B:026D
4586  C4 7E F8        les di, ptr [bp - 8]
4589  26 80 7D 0C 20  cmp byte ptr es:[di + 0xc], 0x20
458E  7D 21           jge 0x45b1
4590  B8 16 00        mov ax, 0x16
4593  50              push ax
4594  B8 30 00        mov ax, 0x30
4597  50              push ax
4598  C4 7E F8        les di, ptr [bp - 8]
459B  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
459F  98              cwde
45A0  B9 0E 00        mov cx, 0xe
45A3  F7 E9           imul cx
45A5  99              cdq
45A6  B9 20 00        mov cx, 0x20
45A9  F7 F9           idiv cx
45AB  50              push ax
45AC  9A C5 13 4B 21  call far 214B:13C5
loc_45B1:
45B1  C4 7E F8        les di, ptr [bp - 8]
45B4  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
45B9  74 21           je 0x45dc
45BB  B8 14 00        mov ax, 0x14
45BE  50              push ax
45BF  B8 30 00        mov ax, 0x30
45C2  50              push ax
45C3  C4 7E F8        les di, ptr [bp - 8]
45C6  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
45CA  98              cwde
45CB  B9 0E 00        mov cx, 0xe
45CE  F7 E9           imul cx
45D0  99              cdq
45D1  B9 20 00        mov cx, 0x20
45D4  F7 F9           idiv cx
45D6  50              push ax
45D7  9A C5 13 4B 21  call far 214B:13C5
loc_45DC:
45DC  B8 15 00        mov ax, 0x15
45DF  50              push ax
45E0  B8 30 00        mov ax, 0x30
45E3  50              push ax
45E4  C4 7E F8        les di, ptr [bp - 8]
45E7  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
45EB  98              cwde
45EC  B9 0E 00        mov cx, 0xe
45EF  F7 E9           imul cx
45F1  99              cdq
45F2  B9 20 00        mov cx, 0x20
45F5  F7 F9           idiv cx
45F7  50              push ax
45F8  9A C5 13 4B 21  call far 214B:13C5
45FD  B8 13 00        mov ax, 0x13
4600  50              push ax
4601  B8 30 00        mov ax, 0x30
4604  50              push ax
4605  FF 76 06        push word ptr [bp + 6]
4608  0E              push cs
4609  E8 EF E9        call 0x2ffb
460C  30 E4           xor ah, ah
460E  B9 0E 00        mov cx, 0xe
4611  F7 E9           imul cx
4613  99              cdq
4614  B9 10 00        mov cx, 0x10
4617  F7 F9           idiv cx
4619  50              push ax
461A  9A C5 13 4B 21  call far 214B:13C5
461F  B8 17 00        mov ax, 0x17
4622  50              push ax
4623  B8 30 00        mov ax, 0x30
4626  50              push ax
4627  FF 76 06        push word ptr [bp + 6]
462A  0E              push cs
462B  E8 AB EA        call 0x30d9
462E  B9 0E 00        mov cx, 0xe
4631  F7 E1           mul cx
4633  31 D2           xor dx, dx
4635  B9 07 00        mov cx, 7
4638  F7 F1           div cx
463A  50              push ax
463B  9A C5 13 4B 21  call far 214B:13C5
4640  FF 76 06        push word ptr [bp + 6]
4643  E8 8D F5        call 0x3bd3
4646  FF 76 06        push word ptr [bp + 6]
4649  B8 0B 00        mov ax, 0xb
464C  50              push ax
464D  B8 0B 00        mov ax, 0xb
4650  50              push ax
4651  E8 F3 F2        call 0x3947
4654  B8 04 00        mov ax, 4
4657  50              push ax
4658  C4 7E F8        les di, ptr [bp - 8]
465B  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
465F  30 E4           xor ah, ah
4661  50              push ax
4662  9A 57 0C 4B 21  call far 214B:0C57
4667  08 C0           or al, al
4669  74 18           je 0x4683
466B  B0 0E           mov al, 0xe
466D  50              push ax
466E  BF 68 42        mov di, 0x4268
4671  0E              push cs
4672  57              push di
4673  B0 0A           mov al, 0xa
4675  50              push ax
4676  B0 28           mov al, 0x28
4678  50              push ax
4679  BF 6E A9        mov di, 0xa96e
467C  1E              push ds
467D  57              push di
467E  9A C8 02 4B 21  call far 214B:02C8
loc_4683:
4683  B8 05 00        mov ax, 5
4686  50              push ax
4687  C4 7E F8        les di, ptr [bp - 8]
468A  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
468E  30 E4           xor ah, ah
4690  50              push ax
4691  9A 57 0C 4B 21  call far 214B:0C57
4696  08 C0           or al, al
4698  74 18           je 0x46b2
469A  B0 0E           mov al, 0xe
469C  50              push ax
469D  BF 68 42        mov di, 0x4268
46A0  0E              push cs
46A1  57              push di
46A2  B0 0A           mov al, 0xa
46A4  50              push ax
46A5  B0 2A           mov al, 0x2a
46A7  50              push ax
46A8  BF 6E A9        mov di, 0xa96e
46AB  1E              push ds
46AC  57              push di
46AD  9A C8 02 4B 21  call far 214B:02C8
loc_46B2:
46B2  B8 06 00        mov ax, 6
46B5  50              push ax
46B6  C4 7E F8        les di, ptr [bp - 8]
46B9  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
46BD  30 E4           xor ah, ah
46BF  50              push ax
46C0  9A 57 0C 4B 21  call far 214B:0C57
46C5  08 C0           or al, al
46C7  74 18           je 0x46e1
46C9  B0 04           mov al, 4
46CB  50              push ax
46CC  BF 68 42        mov di, 0x4268
46CF  0E              push cs
46D0  57              push di
46D1  B0 0A           mov al, 0xa
46D3  50              push ax
46D4  B0 2C           mov al, 0x2c
46D6  50              push ax
46D7  BF 6E A9        mov di, 0xa96e
46DA  1E              push ds
46DB  57              push di
46DC  9A C8 02 4B 21  call far 214B:02C8
loc_46E1:
46E1  B8 08 00        mov ax, 8
46E4  50              push ax
46E5  C4 7E F8        les di, ptr [bp - 8]
46E8  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
46EC  30 E4           xor ah, ah
46EE  50              push ax
46EF  9A 57 0C 4B 21  call far 214B:0C57
46F4  08 C0           or al, al
46F6  74 1B           je 0x4713
46F8  B0 04           mov al, 4
46FA  50              push ax
46FB  BF 6A 42        mov di, 0x426a
46FE  0E              push cs
46FF  57              push di
4700  B0 0A           mov al, 0xa
4702  50              push ax
4703  B0 3D           mov al, 0x3d
4705  50              push ax
4706  BF 6E A9        mov di, 0xa96e
4709  1E              push ds
470A  57              push di
470B  9A 05 02 4B 21  call far 214B:0205
4710  E9 32 01        jmp 0x4845
loc_4713:
4713  C4 7E F8        les di, ptr [bp - 8]
4716  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
471B  75 1B           jne 0x4738
471D  B0 06           mov al, 6
471F  50              push ax
4720  BF 74 42        mov di, 0x4274
4723  0E              push cs
4724  57              push di
4725  B0 0A           mov al, 0xa
4727  50              push ax
4728  B0 3D           mov al, 0x3d
472A  50              push ax
472B  BF 6E A9        mov di, 0xa96e
472E  1E              push ds
472F  57              push di
4730  9A 05 02 4B 21  call far 214B:0205
4735  E9 0D 01        jmp 0x4845
loc_4738:
4738  B8 05 00        mov ax, 5
473B  50              push ax
473C  C4 7E F8        les di, ptr [bp - 8]
473F  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
4743  30 E4           xor ah, ah
4745  50              push ax
4746  9A 57 0C 4B 21  call far 214B:0C57
474B  08 C0           or al, al
474D  74 1B           je 0x476a
474F  B0 05           mov al, 5
4751  50              push ax
4752  BF 7C 42        mov di, 0x427c
4755  0E              push cs
4756  57              push di
4757  B0 0A           mov al, 0xa
4759  50              push ax
475A  B0 3D           mov al, 0x3d
475C  50              push ax
475D  BF 6E A9        mov di, 0xa96e
4760  1E              push ds
4761  57              push di
4762  9A 05 02 4B 21  call far 214B:0205
4767  E9 DB 00        jmp 0x4845
loc_476A:
476A  B8 06 00        mov ax, 6
476D  50              push ax
476E  C4 7E F8        les di, ptr [bp - 8]
4771  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
4775  30 E4           xor ah, ah
4777  50              push ax
4778  9A 57 0C 4B 21  call far 214B:0C57
477D  08 C0           or al, al
477F  74 1B           je 0x479c
4781  B0 04           mov al, 4
4783  50              push ax
4784  BF 83 42        mov di, 0x4283
4787  0E              push cs
4788  57              push di
4789  B0 0A           mov al, 0xa
478B  50              push ax
478C  B0 3D           mov al, 0x3d
478E  50              push ax
478F  BF 6E A9        mov di, 0xa96e
4792  1E              push ds
4793  57              push di
4794  9A 05 02 4B 21  call far 214B:0205
4799  E9 A9 00        jmp 0x4845
loc_479C:
479C  B8 03 00        mov ax, 3
479F  50              push ax
47A0  C4 7E F8        les di, ptr [bp - 8]
47A3  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
47A7  30 E4           xor ah, ah
47A9  50              push ax
47AA  9A 57 0C 4B 21  call far 214B:0C57
47AF  08 C0           or al, al
47B1  74 1A           je 0x47cd
47B3  B0 0F           mov al, 0xf
47B5  50              push ax
47B6  BF 8C 42        mov di, 0x428c
47B9  0E              push cs
47BA  57              push di
47BB  B0 0A           mov al, 0xa
47BD  50              push ax
47BE  B0 3D           mov al, 0x3d
47C0  50              push ax
47C1  BF 6E A9        mov di, 0xa96e
47C4  1E              push ds
47C5  57              push di
47C6  9A 05 02 4B 21  call far 214B:0205
47CB  EB 78           jmp 0x4845
loc_47CD:
47CD  C6 06 B2 AA 0F  mov byte ptr [0xaab2], 0xf
47D2  FF 76 06        push word ptr [bp + 6]
47D5  C4 7E F8        les di, ptr [bp - 8]
47D8  26 8A 05        mov al, byte ptr es:[di]
47DB  30 E4           xor ah, ah
47DD  50              push ax
47DE  0E              push cs
47DF  E8 A0 F2        call 0x3a82
47E2  09 C0           or ax, ax
47E4  74 5F           je 0x4845
47E6  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
47EB  75 17           jne 0x4804
47ED  BF 98 42        mov di, 0x4298
47F0  0E              push cs
47F1  57              push di
47F2  B0 0A           mov al, 0xa
47F4  50              push ax
47F5  B0 3D           mov al, 0x3d
47F7  50              push ax
47F8  BF 6E A9        mov di, 0xa96e
47FB  1E              push ds
47FC  57              push di
47FD  9A A3 01 4B 21  call far 214B:01A3
4802  EB 41           jmp 0x4845
loc_4804:
4804  FF 76 06        push word ptr [bp + 6]
4807  C4 7E F8        les di, ptr [bp - 8]
480A  26 8A 05        mov al, byte ptr es:[di]
480D  30 E4           xor ah, ah
480F  50              push ax
4810  0E              push cs
4811  E8 6E F2        call 0x3a82
4814  3D 0C 00        cmp ax, 0xc
4817  73 17           jae 0x4830
4819  BF A6 42        mov di, 0x42a6
481C  0E              push cs
481D  57              push di
481E  B0 0A           mov al, 0xa
4820  50              push ax
4821  B0 3D           mov al, 0x3d
4823  50              push ax
4824  BF 6E A9        mov di, 0xa96e
4827  1E              push ds
4828  57              push di
4829  9A A3 01 4B 21  call far 214B:01A3
482E  EB 15           jmp 0x4845
loc_4830:
4830  BF AF 42        mov di, 0x42af
4833  0E              push cs
4834  57              push di
4835  B0 0A           mov al, 0xa
4837  50              push ax
4838  B0 3D           mov al, 0x3d
483A  50              push ax
483B  BF 6E A9        mov di, 0xa96e
483E  1E              push ds
483F  57              push di
4840  9A A3 01 4B 21  call far 214B:01A3
loc_4845:
4845  FF 76 06        push word ptr [bp + 6]
4848  B8 08 00        mov ax, 8
484B  50              push ax
484C  B8 3C 00        mov ax, 0x3c
484F  50              push ax
4850  E8 D4 EF        call 0x3827
loc_4853:
4853  89 EC           mov sp, bp
4855  5D              pop bp
4856  CA 02 00        retf 2

