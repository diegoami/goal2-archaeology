; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 5 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:3A5E  (found by: call)
sub_3A5E:
3A5E  55              push bp
3A5F  89 E5           mov bp, sp
3A61  81 EC 16 01     sub sp, 0x116
3A65  C4 7E 06        les di, ptr [bp + 6]
3A68  06              push es
3A69  57              push di
3A6A  8D 7E EB        lea di, [bp - 0x15]
3A6D  16              push ss
3A6E  57              push di
3A6F  B8 14 00        mov ax, 0x14
3A72  50              push ax
3A73  9A 44 06 E4 23  call far 23E4:0644
3A78  B8 02 00        mov ax, 2
3A7B  50              push ax
3A7C  9A B1 06 4B 21  call far 214B:06B1
3A81  3D 01 00        cmp ax, 1
3A84  75 0E           jne 0x3a94
3A86  B8 06 00        mov ax, 6
3A89  50              push ax
3A8A  BF 32 3A        mov di, 0x3a32
3A8D  0E              push cs
3A8E  57              push di
3A8F  E8 79 CC        call 0x70b
3A92  EB 24           jmp 0x3ab8
loc_3A94:
3A94  3D 02 00        cmp ax, 2
3A97  75 0E           jne 0x3aa7
3A99  B8 06 00        mov ax, 6
3A9C  50              push ax
3A9D  BF 3C 3A        mov di, 0x3a3c
3AA0  0E              push cs
3AA1  57              push di
3AA2  E8 66 CC        call 0x70b
3AA5  EB 11           jmp 0x3ab8
loc_3AA7:
3AA7  3D 03 00        cmp ax, 3
3AAA  75 0C           jne 0x3ab8
3AAC  B8 06 00        mov ax, 6
3AAF  50              push ax
3AB0  BF 4C 3A        mov di, 0x3a4c
3AB3  0E              push cs
3AB4  57              push di
3AB5  E8 53 CC        call 0x70b
loc_3AB8:
3AB8  B8 07 00        mov ax, 7
3ABB  50              push ax
3ABC  8D BE EB FE     lea di, [bp - 0x115]
3AC0  16              push ss
3AC1  57              push di
3AC2  BF 5C 3A        mov di, 0x3a5c
3AC5  0E              push cs
3AC6  57              push di
3AC7  9A 2A 06 E4 23  call far 23E4:062A
3ACC  8D 7E EB        lea di, [bp - 0x15]
3ACF  16              push ss
3AD0  57              push di
3AD1  9A B7 06 E4 23  call far 23E4:06B7
3AD6  BF 5C 3A        mov di, 0x3a5c
3AD9  0E              push cs
3ADA  57              push di
3ADB  9A B7 06 E4 23  call far 23E4:06B7
3AE0  E8 28 CC        call 0x70b
3AE3  8B 7E 04        mov di, word ptr [bp + 4]
3AE6  36 C6 45 FF 01  mov byte ptr ss:[di - 1], 1
3AEB  89 EC           mov sp, bp
3AED  5D              pop bp
3AEE  C2 06 00        ret 6
; data (not reached as code), 471 bytes
3AF1                  pstr 'we rule the world!'
3B04                  pstr 'this is heaven!'
3B14                  pstr 'we can do it!'
3B22                  pstr 'no problem!'
3B2E                  pstr ' is ace'
3B36                  pstr 'we gubbed them!'
3B46                  pstr 'demolition job!'
3B56                  pstr 'brilliant!'
3B61                  pstr 'incredible!'
3B6D                  pstr "glad we're through"
3B80                  pstr 'just what we want'
3B92                  pstr 'we are the boys'
3BA2                  pstr 'enjoyable'
3BAC                  pstr 'entertaining'
3BB9                  pstr 'good stuff'
3BC4                  pstr 'give us some goals'
3BD7                  pstr 'we want a refund'
3BE8                  pstr 'boring!'
3BF0                  pstr 'sack '
3BF6                  pstr ' must go'
3BFF                  pstr 'this is a nightmare'
3C13                  pstr "we're delighted"
3C23                  pstr 'total crap'
3C2E                  pstr 'a load of bollocks'
3C41                  pstr 'chronic'
3C49                  pstr 'sickening'
3C53                  pstr 'humiliating'
3C5F                  pstr 'disappointing'
3C6D                  pstr 'we were robbed'
3C7C                  pstr "it's no joke"
3C89                  pstr 'no use'
3C90                  pstr 'next time we win'
3CA1                  pstr "could've been worse"
3CB5                  pstr "should've had them"

; ---- routine 000E:3CC8  (found by: call)
sub_3CC8:
3CC8  55              push bp
3CC9  89 E5           mov bp, sp
3CCB  81 EC 0A 02     sub sp, 0x20a
3CCF  8B 7E 04        mov di, word ptr [bp + 4]
3CD2  36 8B 7D 04     mov di, word ptr ss:[di + 4]
3CD6  36 C4 7D 04     les di, ptr ss:[di + 4]
3CDA  89 7E FB        mov word ptr [bp - 5], di
3CDD  8C 46 FD        mov word ptr [bp - 3], es
3CE0  8B 7E 04        mov di, word ptr [bp + 4]
3CE3  36 8B 7D 04     mov di, word ptr ss:[di + 4]
3CE7  36 8B 45 08     mov ax, word ptr ss:[di + 8]
3CEB  BA BF 00        mov dx, 0xbf
3CEE  F7 E2           mul dx
3CF0  C4 3E 17 A9     les di, ptr [0xa917]
3CF4  03 F8           add di, ax
3CF6  89 7E F7        mov word ptr [bp - 9], di
3CF9  8C 46 F9        mov word ptr [bp - 7], es
3CFC  C6 46 FF 00     mov byte ptr [bp - 1], 0
3D00  C4 7E FB        les di, ptr [bp - 5]
3D03  26 8A 45 03     mov al, byte ptr es:[di + 3]
3D07  8B 7E 04        mov di, word ptr [bp + 4]
3D0A  36 8B 7D 04     mov di, word ptr ss:[di + 4]
3D0E  36 3A 45 FF     cmp al, byte ptr ss:[di - 1]
3D12  74 03           je 0x3d17
3D14  E9 54 01        jmp 0x3e6b
loc_3D17:
3D17  C4 7E FB        les di, ptr [bp - 5]
3D1A  26 8A 45 02     mov al, byte ptr es:[di + 2]
3D1E  3C CB           cmp al, 0xcb
3D20  75 0C           jne 0x3d2e
3D22  BF F1 3A        mov di, 0x3af1
3D25  0E              push cs
3D26  57              push di
3D27  55              push bp
3D28  E8 33 FD        call 0x3a5e
3D2B  E9 3A 01        jmp 0x3e68
loc_3D2E:
3D2E  3C 67           cmp al, 0x67
3D30  75 0C           jne 0x3d3e
3D32  BF 04 3B        mov di, 0x3b04
3D35  0E              push cs
3D36  57              push di
3D37  55              push bp
3D38  E8 23 FD        call 0x3a5e
3D3B  E9 2A 01        jmp 0x3e68
loc_3D3E:
3D3E  3C C9           cmp al, 0xc9
3D40  75 0C           jne 0x3d4e
3D42  BF 14 3B        mov di, 0x3b14
3D45  0E              push cs
3D46  57              push di
3D47  55              push bp
3D48  E8 13 FD        call 0x3a5e
3D4B  E9 1A 01        jmp 0x3e68
loc_3D4E:
3D4E  3C 65           cmp al, 0x65
3D50  75 0C           jne 0x3d5e
3D52  BF 22 3B        mov di, 0x3b22
3D55  0E              push cs
3D56  57              push di
3D57  55              push bp
3D58  E8 03 FD        call 0x3a5e
3D5B  E9 0A 01        jmp 0x3e68
loc_3D5E:
3D5E  8B 7E 04        mov di, word ptr [bp + 4]
3D61  36 8B 7D 04     mov di, word ptr ss:[di + 4]
3D65  36 C4 7D 04     les di, ptr ss:[di + 4]
3D69  06              push es
3D6A  57              push di
3D6B  9A 60 5C 71 17  call far 1771:5C60
3D70  3D 02 00        cmp ax, 2
3D73  76 6F           jbe 0x3de4
3D75  B8 06 00        mov ax, 6
3D78  50              push ax
3D79  9A B1 06 4B 21  call far 214B:06B1
3D7E  3D 01 00        cmp ax, 1
3D81  75 20           jne 0x3da3
3D83  8D BE F7 FE     lea di, [bp - 0x109]
3D87  16              push ss
3D88  57              push di
3D89  8B 7E 04        mov di, word ptr [bp + 4]
3D8C  36 FF 75 04     push word ptr ss:[di + 4]
3D90  E8 38 CD        call 0xacb
3D93  BF 2E 3B        mov di, 0x3b2e
3D96  0E              push cs
3D97  57              push di
3D98  9A B7 06 E4 23  call far 23E4:06B7
3D9D  55              push bp
3D9E  E8 BD FC        call 0x3a5e
3DA1  EB 3E           jmp 0x3de1
loc_3DA3:
3DA3  3D 02 00        cmp ax, 2
3DA6  75 0B           jne 0x3db3
3DA8  BF 36 3B        mov di, 0x3b36
3DAB  0E              push cs
3DAC  57              push di
3DAD  55              push bp
3DAE  E8 AD FC        call 0x3a5e
3DB1  EB 2E           jmp 0x3de1
loc_3DB3:
3DB3  3D 03 00        cmp ax, 3
3DB6  75 0B           jne 0x3dc3
3DB8  BF 46 3B        mov di, 0x3b46
3DBB  0E              push cs
3DBC  57              push di
3DBD  55              push bp
3DBE  E8 9D FC        call 0x3a5e
3DC1  EB 1E           jmp 0x3de1
loc_3DC3:
3DC3  3D 04 00        cmp ax, 4
3DC6  75 0B           jne 0x3dd3
3DC8  BF 56 3B        mov di, 0x3b56
3DCB  0E              push cs
3DCC  57              push di
3DCD  55              push bp
3DCE  E8 8D FC        call 0x3a5e
3DD1  EB 0E           jmp 0x3de1
loc_3DD3:
3DD3  3D 05 00        cmp ax, 5
3DD6  75 09           jne 0x3de1
3DD8  BF 61 3B        mov di, 0x3b61
3DDB  0E              push cs
3DDC  57              push di
3DDD  55              push bp
3DDE  E8 7D FC        call 0x3a5e
loc_3DE1:
3DE1  E9 84 00        jmp 0x3e68
loc_3DE4:
3DE4  C4 7E FB        les di, ptr [bp - 5]
3DE7  26 8A 45 02     mov al, byte ptr es:[di + 2]
3DEB  50              push ax
3DEC  BF 43 A9        mov di, 0xa943
3DEF  1E              push ds
3DF0  57              push di
3DF1  9A DF 08 E4 23  call far 23E4:08DF
3DF6  74 39           je 0x3e31
3DF8  B8 06 00        mov ax, 6
3DFB  50              push ax
3DFC  9A B1 06 4B 21  call far 214B:06B1
3E01  3D 01 00        cmp ax, 1
3E04  75 0B           jne 0x3e11
3E06  BF 6D 3B        mov di, 0x3b6d
3E09  0E              push cs
3E0A  57              push di
3E0B  55              push bp
3E0C  E8 4F FC        call 0x3a5e
3E0F  EB 1E           jmp 0x3e2f
loc_3E11:
3E11  3D 02 00        cmp ax, 2
3E14  75 0B           jne 0x3e21
3E16  BF 80 3B        mov di, 0x3b80
3E19  0E              push cs
3E1A  57              push di
3E1B  55              push bp
3E1C  E8 3F FC        call 0x3a5e
3E1F  EB 0E           jmp 0x3e2f
loc_3E21:
3E21  3D 03 00        cmp ax, 3
3E24  75 09           jne 0x3e2f
3E26  BF 92 3B        mov di, 0x3b92
3E29  0E              push cs
3E2A  57              push di
3E2B  55              push bp
3E2C  E8 2F FC        call 0x3a5e
loc_3E2F:
3E2F  EB 37           jmp 0x3e68
loc_3E31:
3E31  B8 06 00        mov ax, 6
3E34  50              push ax
3E35  9A B1 06 4B 21  call far 214B:06B1
3E3A  3D 01 00        cmp ax, 1
3E3D  75 0B           jne 0x3e4a
3E3F  BF A2 3B        mov di, 0x3ba2
3E42  0E              push cs
3E43  57              push di
3E44  55              push bp
3E45  E8 16 FC        call 0x3a5e
3E48  EB 1E           jmp 0x3e68
loc_3E4A:
3E4A  3D 02 00        cmp ax, 2
3E4D  75 0B           jne 0x3e5a
3E4F  BF AC 3B        mov di, 0x3bac
3E52  0E              push cs
3E53  57              push di
3E54  55              push bp
3E55  E8 06 FC        call 0x3a5e
3E58  EB 0E           jmp 0x3e68
loc_3E5A:
3E5A  3D 03 00        cmp ax, 3
3E5D  75 09           jne 0x3e68
3E5F  BF B9 3B        mov di, 0x3bb9
3E62  0E              push cs
3E63  57              push di
3E64  55              push bp
3E65  E8 F6 FB        call 0x3a5e
loc_3E68:
3E68  E9 D1 01        jmp 0x403c
loc_3E6B:
3E6B  C4 7E FB        les di, ptr [bp - 5]
3E6E  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
3E73  75 44           jne 0x3eb9
3E75  C4 7E FB        les di, ptr [bp - 5]
3E78  26 80 7D 01 00  cmp byte ptr es:[di + 1], 0
3E7D  75 3A           jne 0x3eb9
3E7F  B8 03 00        mov ax, 3
3E82  50              push ax
3E83  9A B1 06 4B 21  call far 214B:06B1
3E88  3D 01 00        cmp ax, 1
3E8B  75 0B           jne 0x3e98
3E8D  BF C4 3B        mov di, 0x3bc4
3E90  0E              push cs
3E91  57              push di
3E92  55              push bp
3E93  E8 C8 FB        call 0x3a5e
3E96  EB 1E           jmp 0x3eb6
loc_3E98:
3E98  3D 02 00        cmp ax, 2
3E9B  75 0B           jne 0x3ea8
3E9D  BF D7 3B        mov di, 0x3bd7
3EA0  0E              push cs
3EA1  57              push di
3EA2  55              push bp
3EA3  E8 B8 FB        call 0x3a5e
3EA6  EB 0E           jmp 0x3eb6
loc_3EA8:
3EA8  3D 03 00        cmp ax, 3
3EAB  75 09           jne 0x3eb6
3EAD  BF E8 3B        mov di, 0x3be8
3EB0  0E              push cs
3EB1  57              push di
3EB2  55              push bp
3EB3  E8 A8 FB        call 0x3a5e
loc_3EB6:
3EB6  E9 83 01        jmp 0x403c
loc_3EB9:
3EB9  8B 7E 04        mov di, word ptr [bp + 4]
3EBC  36 FF 75 04     push word ptr ss:[di + 4]
3EC0  E8 B4 CC        call 0xb77
3EC3  3D FA FF        cmp ax, 0xfffa
3EC6  75 2C           jne 0x3ef4
3EC8  8D BE F7 FD     lea di, [bp - 0x209]
3ECC  16              push ss
3ECD  57              push di
3ECE  BF F0 3B        mov di, 0x3bf0
3ED1  0E              push cs
3ED2  57              push di
3ED3  9A 2A 06 E4 23  call far 23E4:062A
3ED8  8D BE F7 FE     lea di, [bp - 0x109]
3EDC  16              push ss
3EDD  57              push di
3EDE  8B 7E 04        mov di, word ptr [bp + 4]
3EE1  36 FF 75 04     push word ptr ss:[di + 4]
3EE5  E8 E3 CB        call 0xacb
3EE8  9A B7 06 E4 23  call far 23E4:06B7
3EED  55              push bp
3EEE  E8 6D FB        call 0x3a5e
3EF1  E9 48 01        jmp 0x403c
loc_3EF4:
3EF4  3D F9 FF        cmp ax, 0xfff9
3EF7  75 21           jne 0x3f1a
3EF9  8D BE F7 FE     lea di, [bp - 0x109]
3EFD  16              push ss
3EFE  57              push di
3EFF  8B 7E 04        mov di, word ptr [bp + 4]
3F02  36 FF 75 04     push word ptr ss:[di + 4]
3F06  E8 C2 CB        call 0xacb
3F09  BF F6 3B        mov di, 0x3bf6
3F0C  0E              push cs
3F0D  57              push di
3F0E  9A B7 06 E4 23  call far 23E4:06B7
3F13  55              push bp
3F14  E8 47 FB        call 0x3a5e
3F17  E9 22 01        jmp 0x403c
loc_3F1A:
3F1A  3D F6 FF        cmp ax, 0xfff6
3F1D  7C 11           jl 0x3f30
3F1F  3D F8 FF        cmp ax, 0xfff8
3F22  7F 0C           jg 0x3f30
3F24  BF FF 3B        mov di, 0x3bff
3F27  0E              push cs
3F28  57              push di
3F29  55              push bp
3F2A  E8 31 FB        call 0x3a5e
3F2D  E9 0C 01        jmp 0x403c
loc_3F30:
3F30  3D 01 FF        cmp ax, 0xff01
3F33  7C 11           jl 0x3f46
3F35  3D F5 FF        cmp ax, 0xfff5
3F38  7F 0C           jg 0x3f46
3F3A  BF 13 3C        mov di, 0x3c13
3F3D  0E              push cs
3F3E  57              push di
3F3F  55              push bp
3F40  E8 1B FB        call 0x3a5e
3F43  E9 F6 00        jmp 0x403c
loc_3F46:
3F46  8B 7E 04        mov di, word ptr [bp + 4]
3F49  36 FF 75 04     push word ptr ss:[di + 4]
3F4D  E8 8B CA        call 0x9db
3F50  08 C0           or al, al
3F52  74 5A           je 0x3fae
3F54  B8 06 00        mov ax, 6
3F57  50              push ax
3F58  9A B1 06 4B 21  call far 214B:06B1
3F5D  3D 01 00        cmp ax, 1
3F60  75 0B           jne 0x3f6d
3F62  BF 23 3C        mov di, 0x3c23
3F65  0E              push cs
3F66  57              push di
3F67  55              push bp
3F68  E8 F3 FA        call 0x3a5e
3F6B  EB 3E           jmp 0x3fab
loc_3F6D:
3F6D  3D 02 00        cmp ax, 2
3F70  75 0B           jne 0x3f7d
3F72  BF 2E 3C        mov di, 0x3c2e
3F75  0E              push cs
3F76  57              push di
3F77  55              push bp
3F78  E8 E3 FA        call 0x3a5e
3F7B  EB 2E           jmp 0x3fab
loc_3F7D:
3F7D  3D 03 00        cmp ax, 3
3F80  75 0B           jne 0x3f8d
3F82  BF 41 3C        mov di, 0x3c41
3F85  0E              push cs
3F86  57              push di
3F87  55              push bp
3F88  E8 D3 FA        call 0x3a5e
3F8B  EB 1E           jmp 0x3fab
loc_3F8D:
3F8D  3D 04 00        cmp ax, 4
3F90  75 0B           jne 0x3f9d
3F92  BF 49 3C        mov di, 0x3c49
3F95  0E              push cs
3F96  57              push di
3F97  55              push bp
3F98  E8 C3 FA        call 0x3a5e
3F9B  EB 0E           jmp 0x3fab
loc_3F9D:
3F9D  3D 05 00        cmp ax, 5
3FA0  75 09           jne 0x3fab
3FA2  BF 53 3C        mov di, 0x3c53
3FA5  0E              push cs
3FA6  57              push di
3FA7  55              push bp
3FA8  E8 B3 FA        call 0x3a5e
loc_3FAB:
3FAB  E9 8E 00        jmp 0x403c
loc_3FAE:
3FAE  8B 7E 04        mov di, word ptr [bp + 4]
3FB1  36 FF 75 04     push word ptr ss:[di + 4]
3FB5  E8 9B CA        call 0xa53
3FB8  08 C0           or al, al
3FBA  74 49           je 0x4005
3FBC  B8 06 00        mov ax, 6
3FBF  50              push ax
3FC0  9A B1 06 4B 21  call far 214B:06B1
3FC5  3D 01 00        cmp ax, 1
3FC8  75 0B           jne 0x3fd5
3FCA  BF 5F 3C        mov di, 0x3c5f
3FCD  0E              push cs
3FCE  57              push di
3FCF  55              push bp
3FD0  E8 8B FA        call 0x3a5e
3FD3  EB 2E           jmp 0x4003
loc_3FD5:
3FD5  3D 02 00        cmp ax, 2
3FD8  75 0B           jne 0x3fe5
3FDA  BF 6D 3C        mov di, 0x3c6d
3FDD  0E              push cs
3FDE  57              push di
3FDF  55              push bp
3FE0  E8 7B FA        call 0x3a5e
3FE3  EB 1E           jmp 0x4003
loc_3FE5:
3FE5  3D 03 00        cmp ax, 3
3FE8  75 0B           jne 0x3ff5
3FEA  BF 7C 3C        mov di, 0x3c7c
3FED  0E              push cs
3FEE  57              push di
3FEF  55              push bp
3FF0  E8 6B FA        call 0x3a5e
3FF3  EB 0E           jmp 0x4003
loc_3FF5:
3FF5  3D 04 00        cmp ax, 4
3FF8  75 09           jne 0x4003
3FFA  BF 89 3C        mov di, 0x3c89
3FFD  0E              push cs
3FFE  57              push di
3FFF  55              push bp
4000  E8 5B FA        call 0x3a5e
loc_4003:
4003  EB 37           jmp 0x403c
loc_4005:
4005  B8 06 00        mov ax, 6
4008  50              push ax
4009  9A B1 06 4B 21  call far 214B:06B1
400E  3D 01 00        cmp ax, 1
4011  75 0B           jne 0x401e
4013  BF 90 3C        mov di, 0x3c90
4016  0E              push cs
4017  57              push di
4018  55              push bp
4019  E8 42 FA        call 0x3a5e
401C  EB 1E           jmp 0x403c
loc_401E:
401E  3D 02 00        cmp ax, 2
4021  75 0B           jne 0x402e
4023  BF A1 3C        mov di, 0x3ca1
4026  0E              push cs
4027  57              push di
4028  55              push bp
4029  E8 32 FA        call 0x3a5e
402C  EB 0E           jmp 0x403c
loc_402E:
402E  3D 03 00        cmp ax, 3
4031  75 09           jne 0x403c
4033  BF B5 3C        mov di, 0x3cb5
4036  0E              push cs
4037  57              push di
4038  55              push bp
4039  E8 22 FA        call 0x3a5e
loc_403C:
403C  8A 46 FF        mov al, byte ptr [bp - 1]
403F  89 EC           mov sp, bp
4041  5D              pop bp
4042  C2 02 00        ret 2

; ---- routine 000E:4045  (found by: call)
sub_4045:
4045  55              push bp
4046  89 E5           mov bp, sp
4048  83 EC 2A        sub sp, 0x2a
404B  C4 7E 0A        les di, ptr [bp + 0xa]
404E  06              push es
404F  57              push di
4050  8D 7E EB        lea di, [bp - 0x15]
4053  16              push ss
4054  57              push di
4055  B8 14 00        mov ax, 0x14
4058  50              push ax
4059  9A 44 06 E4 23  call far 23E4:0644
405E  C4 7E 06        les di, ptr [bp + 6]
4061  06              push es
4062  57              push di
4063  8D 7E D6        lea di, [bp - 0x2a]
4066  16              push ss
4067  57              push di
4068  B8 14 00        mov ax, 0x14
406B  50              push ax
406C  9A 44 06 E4 23  call far 23E4:0644
4071  8B 7E 04        mov di, word ptr [bp + 4]
4074  36 FF 75 06     push word ptr ss:[di + 6]
4078  8D 7E EB        lea di, [bp - 0x15]
407B  16              push ss
407C  57              push di
407D  8D 7E D6        lea di, [bp - 0x2a]
4080  16              push ss
4081  57              push di
4082  E8 E3 C7        call 0x868
4085  89 EC           mov sp, bp
4087  5D              pop bp
4088  C2 0A 00        ret 0xa
; data (not reached as code), 949 bytes
408B                  pstr '"the boys'
4095                  pstr 'done great"'
40A1                  pstr '"I\'m proud of all'
40B3                  pstr 'the lads"'
40BD                  pstr '"different class!"'
40D0                  db 00   ; .
40D1                  pstr '"a close game"'
40E0                  pstr '"200 percent'
40ED                  pstr 'for effort"'
40F9                  pstr '"a grand display'
410A                  pstr 'by the lads"'
4117                  pstr '"the lads done well"'
412C                  pstr '"We\'re all quietly'
413F                  pstr 'confident"'
414A                  pstr '"I\'m glad'
4154                  pstr 'for the fans"'
4162                  pstr '"it was a good game"'
4177                  pstr '"yes, we were'
4185                  pstr 'the better team"'
4196                  pstr '"we scored'
41A1                  pstr 'the more goals"'
41B1                  pstr '"I\'m happy with'
41C1                  pstr 'our performance"'
41D2                  pstr '"I\'m happy'
41DD                  pstr 'for the lads"'
41EB                  pstr '"it was a fair'
41FA                  pstr 'result"'
4202                  pstr '"we got the result"'
4216                  pstr '"we showed more'
4226                  pstr 'commitment"'
4232                  pstr '"we got to the'
4241                  pstr 'loose ball first"'
4253                  pstr '"it was a game'
4262                  pstr 'of two halves"'
4271                  pstr '"we were robbed"'
4282                  pstr '"at the end of the'
4295                  pstr 'day, a fair result"'
42A9                  pstr '"tomorrow is'
42B6                  pstr 'another day"'
42C3                  pstr '"they gave us'
42D1                  pstr 'a hard game"'
42DE                  pstr '"it\'s only a game"'
42F1                  pstr 'gave 110 percent"'
4303                  pstr '"winning'
430C                  pstr 'is never easy"'
431B                  pstr '"the fans'
4325                  pstr 'were marvellous"'
4336                  pstr '"we tried"'
4341                  pstr '"you win some'
434F                  pstr 'you lose some"'
435E                  pstr '"you have to be'
436E                  pstr 'philosophical"'
437D                  pstr '"you have to'
438A                  pstr 'score goals to win"'
439E                  pstr '"we could have'
43AD                  pstr 'done better"'
43BA                  pstr '"you\'re only as good'
43CF                  pstr 'as your last result"'
43E4                  db 01 22   ; ."
43E6                  pstr ' got'
43EB                  pstr 'the better result"'
43FE                  pstr '"they showed'
440B                  pstr 'more commitment"'
441C                  pstr '"there were some'
442D                  pstr 'good performances"'

; ---- routine 000E:4440  (found by: call)
sub_4440:
4440  55              push bp
4441  89 E5           mov bp, sp
4443  81 EC 04 02     sub sp, 0x204
4447  8B 7E 04        mov di, word ptr [bp + 4]
444A  36 8B 7D 04     mov di, word ptr ss:[di + 4]
444E  36 C4 7D 04     les di, ptr ss:[di + 4]
4452  89 7E FC        mov word ptr [bp - 4], di
4455  8C 46 FE        mov word ptr [bp - 2], es
4458  C4 7E FC        les di, ptr [bp - 4]
445B  26 8A 45 03     mov al, byte ptr es:[di + 3]
445F  8B 7E 04        mov di, word ptr [bp + 4]
4462  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4466  36 3A 45 FF     cmp al, byte ptr ss:[di - 1]
446A  74 03           je 0x446f
446C  E9 8F 01        jmp 0x45fe
loc_446F:
446F  B8 12 00        mov ax, 0x12
4472  50              push ax
4473  9A B1 06 4B 21  call far 214B:06B1
4478  3D 01 00        cmp ax, 1
447B  75 11           jne 0x448e
447D  BF 8B 40        mov di, 0x408b
4480  0E              push cs
4481  57              push di
4482  BF 95 40        mov di, 0x4095
4485  0E              push cs
4486  57              push di
4487  55              push bp
4488  E8 BA FB        call 0x4045
448B  E9 6D 01        jmp 0x45fb
loc_448E:
448E  3D 02 00        cmp ax, 2
4491  75 11           jne 0x44a4
4493  BF A1 40        mov di, 0x40a1
4496  0E              push cs
4497  57              push di
4498  BF B3 40        mov di, 0x40b3
449B  0E              push cs
449C  57              push di
449D  55              push bp
449E  E8 A4 FB        call 0x4045
44A1  E9 57 01        jmp 0x45fb
loc_44A4:
44A4  3D 03 00        cmp ax, 3
44A7  75 11           jne 0x44ba
44A9  BF BD 40        mov di, 0x40bd
44AC  0E              push cs
44AD  57              push di
44AE  BF D0 40        mov di, 0x40d0
44B1  0E              push cs
44B2  57              push di
44B3  55              push bp
44B4  E8 8E FB        call 0x4045
44B7  E9 41 01        jmp 0x45fb
loc_44BA:
44BA  3D 04 00        cmp ax, 4
44BD  75 11           jne 0x44d0
44BF  BF D1 40        mov di, 0x40d1
44C2  0E              push cs
44C3  57              push di
44C4  BF D0 40        mov di, 0x40d0
44C7  0E              push cs
44C8  57              push di
44C9  55              push bp
44CA  E8 78 FB        call 0x4045
44CD  E9 2B 01        jmp 0x45fb
loc_44D0:
44D0  3D 05 00        cmp ax, 5
44D3  75 11           jne 0x44e6
44D5  BF E0 40        mov di, 0x40e0
44D8  0E              push cs
44D9  57              push di
44DA  BF ED 40        mov di, 0x40ed
44DD  0E              push cs
44DE  57              push di
44DF  55              push bp
44E0  E8 62 FB        call 0x4045
44E3  E9 15 01        jmp 0x45fb
loc_44E6:
44E6  3D 06 00        cmp ax, 6
44E9  75 11           jne 0x44fc
44EB  BF F9 40        mov di, 0x40f9
44EE  0E              push cs
44EF  57              push di
44F0  BF 0A 41        mov di, 0x410a
44F3  0E              push cs
44F4  57              push di
44F5  55              push bp
44F6  E8 4C FB        call 0x4045
44F9  E9 FF 00        jmp 0x45fb
loc_44FC:
44FC  3D 07 00        cmp ax, 7
44FF  75 11           jne 0x4512
4501  BF 17 41        mov di, 0x4117
4504  0E              push cs
4505  57              push di
4506  BF D0 40        mov di, 0x40d0
4509  0E              push cs
450A  57              push di
450B  55              push bp
450C  E8 36 FB        call 0x4045
450F  E9 E9 00        jmp 0x45fb
loc_4512:
4512  3D 08 00        cmp ax, 8
4515  75 11           jne 0x4528
4517  BF 2C 41        mov di, 0x412c
451A  0E              push cs
451B  57              push di
451C  BF 3F 41        mov di, 0x413f
451F  0E              push cs
4520  57              push di
4521  55              push bp
4522  E8 20 FB        call 0x4045
4525  E9 D3 00        jmp 0x45fb
loc_4528:
4528  3D 09 00        cmp ax, 9
452B  75 11           jne 0x453e
452D  BF 4A 41        mov di, 0x414a
4530  0E              push cs
4531  57              push di
4532  BF 54 41        mov di, 0x4154
4535  0E              push cs
4536  57              push di
4537  55              push bp
4538  E8 0A FB        call 0x4045
453B  E9 BD 00        jmp 0x45fb
loc_453E:
453E  3D 0A 00        cmp ax, 0xa
4541  75 11           jne 0x4554
4543  BF 62 41        mov di, 0x4162
4546  0E              push cs
4547  57              push di
4548  BF D0 40        mov di, 0x40d0
454B  0E              push cs
454C  57              push di
454D  55              push bp
454E  E8 F4 FA        call 0x4045
4551  E9 A7 00        jmp 0x45fb
loc_4554:
4554  3D 0B 00        cmp ax, 0xb
4557  75 11           jne 0x456a
4559  BF 77 41        mov di, 0x4177
455C  0E              push cs
455D  57              push di
455E  BF 85 41        mov di, 0x4185
4561  0E              push cs
4562  57              push di
4563  55              push bp
4564  E8 DE FA        call 0x4045
4567  E9 91 00        jmp 0x45fb
loc_456A:
456A  3D 0C 00        cmp ax, 0xc
456D  75 10           jne 0x457f
456F  BF 96 41        mov di, 0x4196
4572  0E              push cs
4573  57              push di
4574  BF A1 41        mov di, 0x41a1
4577  0E              push cs
4578  57              push di
4579  55              push bp
457A  E8 C8 FA        call 0x4045
457D  EB 7C           jmp 0x45fb
loc_457F:
457F  3D 0D 00        cmp ax, 0xd
4582  75 10           jne 0x4594
4584  BF B1 41        mov di, 0x41b1
4587  0E              push cs
4588  57              push di
4589  BF C1 41        mov di, 0x41c1
458C  0E              push cs
458D  57              push di
458E  55              push bp
458F  E8 B3 FA        call 0x4045
4592  EB 67           jmp 0x45fb
loc_4594:
4594  3D 0E 00        cmp ax, 0xe
4597  75 10           jne 0x45a9
4599  BF D2 41        mov di, 0x41d2
459C  0E              push cs
459D  57              push di
459E  BF DD 41        mov di, 0x41dd
45A1  0E              push cs
45A2  57              push di
45A3  55              push bp
45A4  E8 9E FA        call 0x4045
45A7  EB 52           jmp 0x45fb
loc_45A9:
45A9  3D 0F 00        cmp ax, 0xf
45AC  75 10           jne 0x45be
45AE  BF EB 41        mov di, 0x41eb
45B1  0E              push cs
45B2  57              push di
45B3  BF FA 41        mov di, 0x41fa
45B6  0E              push cs
45B7  57              push di
45B8  55              push bp
45B9  E8 89 FA        call 0x4045
45BC  EB 3D           jmp 0x45fb
loc_45BE:
45BE  3D 10 00        cmp ax, 0x10
45C1  75 10           jne 0x45d3
45C3  BF 02 42        mov di, 0x4202
45C6  0E              push cs
45C7  57              push di
45C8  BF D0 40        mov di, 0x40d0
45CB  0E              push cs
45CC  57              push di
45CD  55              push bp
45CE  E8 74 FA        call 0x4045
45D1  EB 28           jmp 0x45fb
loc_45D3:
45D3  3D 11 00        cmp ax, 0x11
45D6  75 10           jne 0x45e8
45D8  BF 16 42        mov di, 0x4216
45DB  0E              push cs
45DC  57              push di
45DD  BF 26 42        mov di, 0x4226
45E0  0E              push cs
45E1  57              push di
45E2  55              push bp
45E3  E8 5F FA        call 0x4045
45E6  EB 13           jmp 0x45fb
loc_45E8:
45E8  3D 12 00        cmp ax, 0x12
45EB  75 0E           jne 0x45fb
45ED  BF 32 42        mov di, 0x4232
45F0  0E              push cs
45F1  57              push di
45F2  BF 41 42        mov di, 0x4241
45F5  0E              push cs
45F6  57              push di
45F7  55              push bp
45F8  E8 4A FA        call 0x4045
loc_45FB:
45FB  E9 B8 01        jmp 0x47b6
loc_45FE:
45FE  B8 12 00        mov ax, 0x12
4601  50              push ax
4602  9A B1 06 4B 21  call far 214B:06B1
4607  3D 01 00        cmp ax, 1
460A  75 11           jne 0x461d
460C  BF 53 42        mov di, 0x4253
460F  0E              push cs
4610  57              push di
4611  BF 62 42        mov di, 0x4262
4614  0E              push cs
4615  57              push di
4616  55              push bp
4617  E8 2B FA        call 0x4045
461A  E9 99 01        jmp 0x47b6
loc_461D:
461D  3D 02 00        cmp ax, 2
4620  75 11           jne 0x4633
4622  BF 71 42        mov di, 0x4271
4625  0E              push cs
4626  57              push di
4627  BF D0 40        mov di, 0x40d0
462A  0E              push cs
462B  57              push di
462C  55              push bp
462D  E8 15 FA        call 0x4045
4630  E9 83 01        jmp 0x47b6
loc_4633:
4633  3D 03 00        cmp ax, 3
4636  75 11           jne 0x4649
4638  BF 82 42        mov di, 0x4282
463B  0E              push cs
463C  57              push di
463D  BF 95 42        mov di, 0x4295
4640  0E              push cs
4641  57              push di
4642  55              push bp
4643  E8 FF F9        call 0x4045
4646  E9 6D 01        jmp 0x47b6
loc_4649:
4649  3D 04 00        cmp ax, 4
464C  75 11           jne 0x465f
464E  BF A9 42        mov di, 0x42a9
4651  0E              push cs
4652  57              push di
4653  BF B6 42        mov di, 0x42b6
4656  0E              push cs
4657  57              push di
4658  55              push bp
4659  E8 E9 F9        call 0x4045
465C  E9 57 01        jmp 0x47b6
loc_465F:
465F  3D 05 00        cmp ax, 5
4662  75 11           jne 0x4675
4664  BF C3 42        mov di, 0x42c3
4667  0E              push cs
4668  57              push di
4669  BF D1 42        mov di, 0x42d1
466C  0E              push cs
466D  57              push di
466E  55              push bp
466F  E8 D3 F9        call 0x4045
4672  E9 41 01        jmp 0x47b6
loc_4675:
4675  3D 06 00        cmp ax, 6
4678  75 11           jne 0x468b
467A  BF DE 42        mov di, 0x42de
467D  0E              push cs
467E  57              push di
467F  BF D0 40        mov di, 0x40d0
4682  0E              push cs
4683  57              push di
4684  55              push bp
4685  E8 BD F9        call 0x4045
4688  E9 2B 01        jmp 0x47b6
loc_468B:
468B  3D 07 00        cmp ax, 7
468E  75 11           jne 0x46a1
4690  BF 8B 40        mov di, 0x408b
4693  0E              push cs
4694  57              push di
4695  BF F1 42        mov di, 0x42f1
4698  0E              push cs
4699  57              push di
469A  55              push bp
469B  E8 A7 F9        call 0x4045
469E  E9 15 01        jmp 0x47b6
loc_46A1:
46A1  3D 08 00        cmp ax, 8
46A4  75 11           jne 0x46b7
46A6  BF 03 43        mov di, 0x4303
46A9  0E              push cs
46AA  57              push di
46AB  BF 0C 43        mov di, 0x430c
46AE  0E              push cs
46AF  57              push di
46B0  55              push bp
46B1  E8 91 F9        call 0x4045
46B4  E9 FF 00        jmp 0x47b6
loc_46B7:
46B7  3D 09 00        cmp ax, 9
46BA  75 11           jne 0x46cd
46BC  BF 1B 43        mov di, 0x431b
46BF  0E              push cs
46C0  57              push di
46C1  BF 25 43        mov di, 0x4325
46C4  0E              push cs
46C5  57              push di
46C6  55              push bp
46C7  E8 7B F9        call 0x4045
46CA  E9 E9 00        jmp 0x47b6
loc_46CD:
46CD  3D 0A 00        cmp ax, 0xa
46D0  75 11           jne 0x46e3
46D2  BF 36 43        mov di, 0x4336
46D5  0E              push cs
46D6  57              push di
46D7  BF D0 40        mov di, 0x40d0
46DA  0E              push cs
46DB  57              push di
46DC  55              push bp
46DD  E8 65 F9        call 0x4045
46E0  E9 D3 00        jmp 0x47b6
loc_46E3:
46E3  3D 0B 00        cmp ax, 0xb
46E6  75 11           jne 0x46f9
46E8  BF 41 43        mov di, 0x4341
46EB  0E              push cs
46EC  57              push di
46ED  BF 4F 43        mov di, 0x434f
46F0  0E              push cs
46F1  57              push di
46F2  55              push bp
46F3  E8 4F F9        call 0x4045
46F6  E9 BD 00        jmp 0x47b6
loc_46F9:
46F9  3D 0C 00        cmp ax, 0xc
46FC  75 11           jne 0x470f
46FE  BF 5E 43        mov di, 0x435e
4701  0E              push cs
4702  57              push di
4703  BF 6E 43        mov di, 0x436e
4706  0E              push cs
4707  57              push di
4708  55              push bp
4709  E8 39 F9        call 0x4045
470C  E9 A7 00        jmp 0x47b6
loc_470F:
470F  3D 0D 00        cmp ax, 0xd
4712  75 11           jne 0x4725
4714  BF 7D 43        mov di, 0x437d
4717  0E              push cs
4718  57              push di
4719  BF 8A 43        mov di, 0x438a
471C  0E              push cs
471D  57              push di
471E  55              push bp
471F  E8 23 F9        call 0x4045
4722  E9 91 00        jmp 0x47b6
loc_4725:
4725  3D 0E 00        cmp ax, 0xe
4728  75 10           jne 0x473a
472A  BF 9E 43        mov di, 0x439e
472D  0E              push cs
472E  57              push di
472F  BF AD 43        mov di, 0x43ad
4732  0E              push cs
4733  57              push di
4734  55              push bp
4735  E8 0D F9        call 0x4045
4738  EB 7C           jmp 0x47b6
loc_473A:
473A  3D 0F 00        cmp ax, 0xf
473D  75 10           jne 0x474f
473F  BF BA 43        mov di, 0x43ba
4742  0E              push cs
4743  57              push di
4744  BF CF 43        mov di, 0x43cf
4747  0E              push cs
4748  57              push di
4749  55              push bp
474A  E8 F8 F8        call 0x4045
474D  EB 67           jmp 0x47b6
loc_474F:
474F  3D 10 00        cmp ax, 0x10
4752  75 3A           jne 0x478e
4754  8D BE FC FD     lea di, [bp - 0x204]
4758  16              push ss
4759  57              push di
475A  BF E4 43        mov di, 0x43e4
475D  0E              push cs
475E  57              push di
475F  9A 2A 06 E4 23  call far 23E4:062A
4764  8D BE FC FE     lea di, [bp - 0x104]
4768  16              push ss
4769  57              push di
476A  8B 7E 04        mov di, word ptr [bp + 4]
476D  36 FF 75 04     push word ptr ss:[di + 4]
4771  E8 96 C3        call 0xb0a
4774  9A B7 06 E4 23  call far 23E4:06B7
4779  BF E6 43        mov di, 0x43e6
477C  0E              push cs
477D  57              push di
477E  9A B7 06 E4 23  call far 23E4:06B7
4783  BF EB 43        mov di, 0x43eb
4786  0E              push cs
4787  57              push di
4788  55              push bp
4789  E8 B9 F8        call 0x4045
478C  EB 28           jmp 0x47b6
loc_478E:
478E  3D 11 00        cmp ax, 0x11
4791  75 10           jne 0x47a3
4793  BF FE 43        mov di, 0x43fe
4796  0E              push cs
4797  57              push di
4798  BF 0B 44        mov di, 0x440b
479B  0E              push cs
479C  57              push di
479D  55              push bp
479E  E8 A4 F8        call 0x4045
47A1  EB 13           jmp 0x47b6
loc_47A3:
47A3  3D 12 00        cmp ax, 0x12
47A6  75 0E           jne 0x47b6
47A8  BF 1C 44        mov di, 0x441c
47AB  0E              push cs
47AC  57              push di
47AD  BF 2D 44        mov di, 0x442d
47B0  0E              push cs
47B1  57              push di
47B2  55              push bp
47B3  E8 8F F8        call 0x4045
loc_47B6:
47B6  89 EC           mov sp, bp
47B8  5D              pop bp
47B9  C2 04 00        ret 4
; data (not reached as code), 42 bytes
47BC                  pstr 'President of FA says'
47D1                  pstr 'Football Assoc. say:'

