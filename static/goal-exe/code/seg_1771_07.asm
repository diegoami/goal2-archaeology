; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 7 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:4859  (found by: call, far)
sub_4859:
4859  55              push bp
485A  89 E5           mov bp, sp
485C  81 EC 0E 01     sub sp, 0x10e
4860  83 7E 0A 00     cmp word ptr [bp + 0xa], 0
4864  75 03           jne 0x4869
4866  E9 B6 00        jmp 0x491f
loc_4869:
4869  8D BE F3 FE     lea di, [bp - 0x10d]
486D  16              push ss
486E  57              push di
486F  FF 76 0A        push word ptr [bp + 0xa]
4872  0E              push cs
4873  E8 1D E6        call 0x2e93
4876  8D 7E F3        lea di, [bp - 0xd]
4879  16              push ss
487A  57              push di
487B  B8 0C 00        mov ax, 0xc
487E  50              push ax
487F  9A 44 06 E4 23  call far 23E4:0644
4884  8D 7E F3        lea di, [bp - 0xd]
4887  16              push ss
4888  57              push di
4889  B0 0C           mov al, 0xc
488B  50              push ax
488C  8A 46 06        mov al, byte ptr [bp + 6]
488F  50              push ax
4890  8B 46 06        mov ax, word ptr [bp + 6]
4893  05 0C 00        add ax, 0xc
4896  50              push ax
4897  8A 46 08        mov al, byte ptr [bp + 8]
489A  50              push ax
489B  9A 86 10 4B 21  call far 214B:1086
48A0  8D 7E F3        lea di, [bp - 0xd]
48A3  16              push ss
48A4  57              push di
48A5  8D BE F3 FE     lea di, [bp - 0x10d]
48A9  16              push ss
48AA  57              push di
48AB  FF 76 0A        push word ptr [bp + 0xa]
48AE  0E              push cs
48AF  E8 E1 E5        call 0x2e93
48B2  9A 2F 07 E4 23  call far 23E4:072F
48B7  75 02           jne 0x48bb
48B9  EB 64           jmp 0x491f
loc_48BB:
48BB  8A 56 F4        mov dl, byte ptr [bp - 0xc]
48BE  8B 46 0A        mov ax, word ptr [bp + 0xa]
48C1  C4 3E 70 9B     les di, ptr [0x9b70]
48C5  03 F8           add di, ax
48C7  26 88 15        mov byte ptr es:[di], dl
48CA  8D 7E F3        lea di, [bp - 0xd]
48CD  16              push ss
48CE  57              push di
48CF  B8 01 00        mov ax, 1
48D2  50              push ax
48D3  80 7E F5 20     cmp byte ptr [bp - 0xb], 0x20
48D7  74 04           je 0x48dd
48D9  B0 00           mov al, 0
48DB  EB 02           jmp 0x48df
loc_48DD:
48DD  B0 01           mov al, 1
loc_48DF:
48DF  30 E4           xor ah, ah
48E1  40              inc ax
48E2  50              push ax
48E3  9A DB 07 E4 23  call far 23E4:07DB
48E8  80 7E F3 00     cmp byte ptr [bp - 0xd], 0
48EC  75 02           jne 0x48f0
48EE  EB 2F           jmp 0x491f
loc_48F0:
48F0  8A 46 F4        mov al, byte ptr [bp - 0xc]
48F3  50              push ax
48F4  9A B2 19 E4 23  call far 23E4:19B2
48F9  88 46 F4        mov byte ptr [bp - 0xc], al
48FC  8D 7E F3        lea di, [bp - 0xd]
48FF  16              push ss
4900  57              push di
4901  8B 46 0A        mov ax, word ptr [bp + 0xa]
4904  BA 0B 00        mov dx, 0xb
4907  F7 E2           mul dx
4909  C4 3E 6C 9B     les di, ptr [0x9b6c]
490D  03 F8           add di, ax
490F  06              push es
4910  57              push di
4911  B8 0A 00        mov ax, 0xa
4914  50              push ax
4915  9A 44 06 E4 23  call far 23E4:0644
491A  C6 06 1A 0C 01  mov byte ptr [0xc1a], 1
loc_491F:
491F  89 EC           mov sp, bp
4921  5D              pop bp
4922  CA 06 00        retf 6

; ---- routine 1771:4925  (found by: call)
sub_4925:
4925  55              push bp
4926  89 E5           mov bp, sp
4928  C6 06 76 A9 B1  mov byte ptr [0xa976], 0xb1
492D  C4 7E 04        les di, ptr [bp + 4]
4930  26 FE 05        inc byte ptr es:[di]
4933  C4 7E 04        les di, ptr [bp + 4]
4936  06              push es
4937  57              push di
4938  B8 0E 00        mov ax, 0xe
493B  50              push ax
493C  9A 52 14 4B 21  call far 214B:1452
4941  C4 7E 04        les di, ptr [bp + 4]
4944  26 FE 0D        dec byte ptr es:[di]
4947  C6 06 76 A9 00  mov byte ptr [0xa976], 0
494C  89 EC           mov sp, bp
494E  5D              pop bp
494F  C2 04 00        ret 4

; ---- routine 1771:4952  (found by: far)
sub_4952:
4952  55              push bp
4953  89 E5           mov bp, sp
4955  83 EC 04        sub sp, 4
4958  8B 46 06        mov ax, word ptr [bp + 6]
495B  BA 14 00        mov dx, 0x14
495E  F7 E2           mul dx
4960  C4 3E 1B A9     les di, ptr [0xa91b]
4964  03 F8           add di, ax
4966  89 7E FC        mov word ptr [bp - 4], di
4969  8C 46 FE        mov word ptr [bp - 2], es
496C  83 7E 06 00     cmp word ptr [bp + 6], 0
4970  74 40           je 0x49b2
4972  A0 76 A9        mov al, byte ptr [0xa976]
4975  50              push ax
4976  9A B2 19 E4 23  call far 23E4:19B2
497B  3C 43           cmp al, 0x43
497D  75 10           jne 0x498f
497F  C4 7E FC        les di, ptr [bp - 4]
4982  26 8A 45 07     mov al, byte ptr es:[di + 7]
4986  C4 7E FC        les di, ptr [bp - 4]
4989  26 88 45 06     mov byte ptr es:[di + 6], al
498D  EB 0C           jmp 0x499b
loc_498F:
498F  C4 7E FC        les di, ptr [bp - 4]
4992  81 C7 06 00     add di, 6
4996  06              push es
4997  57              push di
4998  E8 8A FF        call 0x4925
loc_499B:
499B  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
49A0  74 05           je 0x49a7
49A2  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
loc_49A7:
49A7  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
49AC  74 04           je 0x49b2
49AE  0E              push cs
49AF  E8 46 F5        call 0x3ef8
loc_49B2:
49B2  89 EC           mov sp, bp
49B4  5D              pop bp
49B5  CA 02 00        retf 2

; ---- routine 1771:49B8  (found by: call)
sub_49B8:
49B8  55              push bp
49B9  89 E5           mov bp, sp
49BB  83 EC 0C        sub sp, 0xc
49BE  8B 7E 04        mov di, word ptr [bp + 4]
49C1  36 8B 45 08     mov ax, word ptr ss:[di + 8]
49C5  BA 14 00        mov dx, 0x14
49C8  F7 E2           mul dx
49CA  C4 3E 1B A9     les di, ptr [0xa91b]
49CE  03 F8           add di, ax
49D0  89 7E F5        mov word ptr [bp - 0xb], di
49D3  8C 46 F7        mov word ptr [bp - 9], es
49D6  C4 7E F5        les di, ptr [bp - 0xb]
49D9  26 8A 05        mov al, byte ptr es:[di]
49DC  30 E4           xor ah, ah
49DE  3B 06 36 9B     cmp ax, word ptr [0x9b36]
49E2  75 06           jne 0x49ea
49E4  C6 46 FF 01     mov byte ptr [bp - 1], 1
49E8  EB 04           jmp 0x49ee
loc_49EA:
49EA  C6 46 FF 00     mov byte ptr [bp - 1], 0
loc_49EE:
49EE  8B 7E 04        mov di, word ptr [bp + 4]
49F1  36 FF 75 08     push word ptr ss:[di + 8]
49F5  C4 7E F5        les di, ptr [bp - 0xb]
49F8  26 8A 05        mov al, byte ptr es:[di]
49FB  30 E4           xor ah, ah
49FD  50              push ax
49FE  0E              push cs
49FF  E8 80 F0        call 0x3a82
4A02  89 46 F9        mov word ptr [bp - 7], ax
4A05  80 7E FF 00     cmp byte ptr [bp - 1], 0
4A09  74 04           je 0x4a0f
4A0B  B0 00           mov al, 0
4A0D  EB 02           jmp 0x4a11
loc_4A0F:
4A0F  B0 01           mov al, 1
loc_4A11:
4A11  98              cwde
4A12  8B F8           mov di, ax
4A14  D1 E7           shl di, 1
4A16  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
4A1A  89 46 FB        mov word ptr [bp - 5], ax
4A1D  C4 7E F5        les di, ptr [bp - 0xb]
4A20  26 80 7D 06 02  cmp byte ptr es:[di + 6], 2
4A25  73 15           jae 0x4a3c
4A27  B8 07 00        mov ax, 7
4A2A  50              push ax
4A2B  C4 7E F5        les di, ptr [bp - 0xb]
4A2E  81 C7 10 00     add di, 0x10
4A32  06              push es
4A33  57              push di
4A34  9A A1 0C 4B 21  call far 214B:0CA1
4A39  E9 1B 01        jmp 0x4b57
loc_4A3C:
4A3C  B8 07 00        mov ax, 7
4A3F  50              push ax
4A40  C4 7E F5        les di, ptr [bp - 0xb]
4A43  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
4A47  30 E4           xor ah, ah
4A49  50              push ax
4A4A  9A 57 0C 4B 21  call far 214B:0C57
4A4F  08 C0           or al, al
4A51  74 47           je 0x4a9a
4A53  C7 46 FD 0C 00  mov word ptr [bp - 3], 0xc
loc_4A58:
4A58  FF 4E FD        dec word ptr [bp - 3]
4A5B  83 7E FD 01     cmp word ptr [bp - 3], 1
4A5F  74 37           je 0x4a98
4A61  8B 46 FD        mov ax, word ptr [bp - 3]
4A64  D1 E0           shl ax, 1
4A66  8B C8           mov cx, ax
4A68  8B 46 FB        mov ax, word ptr [bp - 5]
4A6B  BA BF 00        mov dx, 0xbf
4A6E  F7 E2           mul dx
4A70  C4 3E 17 A9     les di, ptr [0xa917]
4A74  03 F8           add di, ax
4A76  03 F9           add di, cx
4A78  26 8B 5D FE     mov bx, word ptr es:[di - 2]
4A7C  8B 46 F9        mov ax, word ptr [bp - 7]
4A7F  D1 E0           shl ax, 1
4A81  8B C8           mov cx, ax
4A83  8A 46 FF        mov al, byte ptr [bp - 1]
4A86  98              cwde
4A87  BA 28 00        mov dx, 0x28
4A8A  F7 E2           mul dx
4A8C  8B F8           mov di, ax
4A8E  03 F9           add di, cx
4A90  8B 85 3E 9A     mov ax, word ptr [di - 0x65c2]
4A94  3B C3           cmp ax, bx
4A96  75 C0           jne 0x4a58
loc_4A98:
4A98  EB 05           jmp 0x4a9f
loc_4A9A:
4A9A  31 C0           xor ax, ax
4A9C  89 46 FD        mov word ptr [bp - 3], ax
loc_4A9F:
4A9F  FF 46 FD        inc word ptr [bp - 3]
4AA2  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
4AA6  76 05           jbe 0x4aad
4AA8  31 C0           xor ax, ax
4AAA  89 46 FD        mov word ptr [bp - 3], ax
loc_4AAD:
4AAD  83 7E FD 02     cmp word ptr [bp - 3], 2
4AB1  72 23           jb 0x4ad6
4AB3  8B 46 FD        mov ax, word ptr [bp - 3]
4AB6  D1 E0           shl ax, 1
4AB8  8B C8           mov cx, ax
4ABA  8B 46 FB        mov ax, word ptr [bp - 5]
4ABD  BA BF 00        mov dx, 0xbf
4AC0  F7 E2           mul dx
4AC2  C4 3E 17 A9     les di, ptr [0xa917]
4AC6  03 F8           add di, ax
4AC8  03 F9           add di, cx
4ACA  26 FF 75 FE     push word ptr es:[di - 2]
4ACE  0E              push cs
4ACF  E8 44 E7        call 0x3216
4AD2  08 C0           or al, al
4AD4  75 C9           jne 0x4a9f
loc_4AD6:
4AD6  83 7E FD 00     cmp word ptr [bp - 3], 0
4ADA  75 14           jne 0x4af0
4ADC  B8 07 00        mov ax, 7
4ADF  50              push ax
4AE0  C4 7E F5        les di, ptr [bp - 0xb]
4AE3  81 C7 10 00     add di, 0x10
4AE7  06              push es
4AE8  57              push di
4AE9  9A A1 0C 4B 21  call far 214B:0CA1
4AEE  EB 12           jmp 0x4b02
loc_4AF0:
4AF0  B8 07 00        mov ax, 7
4AF3  50              push ax
4AF4  C4 7E F5        les di, ptr [bp - 0xb]
4AF7  81 C7 10 00     add di, 0x10
4AFB  06              push es
4AFC  57              push di
4AFD  9A 79 0C 4B 21  call far 214B:0C79
loc_4B02:
4B02  83 7E FD 01     cmp word ptr [bp - 3], 1
4B06  76 35           jbe 0x4b3d
4B08  8B 46 FD        mov ax, word ptr [bp - 3]
4B0B  D1 E0           shl ax, 1
4B0D  8B C8           mov cx, ax
4B0F  8B 46 FB        mov ax, word ptr [bp - 5]
4B12  BA BF 00        mov dx, 0xbf
4B15  F7 E2           mul dx
4B17  C4 3E 17 A9     les di, ptr [0xa917]
4B1B  03 F8           add di, ax
4B1D  03 F9           add di, cx
4B1F  26 8B 5D FE     mov bx, word ptr es:[di - 2]
4B23  8B 46 F9        mov ax, word ptr [bp - 7]
4B26  D1 E0           shl ax, 1
4B28  8B C8           mov cx, ax
4B2A  8A 46 FF        mov al, byte ptr [bp - 1]
4B2D  98              cwde
4B2E  BA 28 00        mov dx, 0x28
4B31  F7 E2           mul dx
4B33  8B F8           mov di, ax
4B35  03 F9           add di, cx
4B37  89 9D 3E 9A     mov word ptr [di - 0x65c2], bx
4B3B  EB 1A           jmp 0x4b57
loc_4B3D:
4B3D  8B 46 F9        mov ax, word ptr [bp - 7]
4B40  D1 E0           shl ax, 1
4B42  8B C8           mov cx, ax
4B44  8A 46 FF        mov al, byte ptr [bp - 1]
4B47  98              cwde
4B48  BA 28 00        mov dx, 0x28
4B4B  F7 E2           mul dx
4B4D  8B F8           mov di, ax
4B4F  03 F9           add di, cx
4B51  31 C0           xor ax, ax
4B53  89 85 3E 9A     mov word ptr [di - 0x65c2], ax
loc_4B57:
4B57  0E              push cs
4B58  E8 9D F3        call 0x3ef8
4B5B  89 EC           mov sp, bp
4B5D  5D              pop bp
4B5E  C2 02 00        ret 2

; ---- routine 1771:4B61  (found by: far)
sub_4B61:
4B61  55              push bp
4B62  89 E5           mov bp, sp
4B64  83 EC 06        sub sp, 6
4B67  8B 46 08        mov ax, word ptr [bp + 8]
4B6A  BA 14 00        mov dx, 0x14
4B6D  F7 E2           mul dx
4B6F  C4 3E 1B A9     les di, ptr [0xa91b]
4B73  03 F8           add di, ax
4B75  89 7E FB        mov word ptr [bp - 5], di
4B78  8C 46 FD        mov word ptr [bp - 3], es
4B7B  83 7E 08 00     cmp word ptr [bp + 8], 0
4B7F  75 03           jne 0x4b84
4B81  E9 6D 01        jmp 0x4cf1
loc_4B84:
4B84  BF C6 46        mov di, 0x46c6
4B87  1E              push ds
4B88  57              push di
4B89  BF 6E A9        mov di, 0xa96e
4B8C  1E              push ds
4B8D  57              push di
4B8E  9A 29 03 4B 21  call far 214B:0329
4B93  80 3E 1E 0C 00  cmp byte ptr [0xc1e], 0
4B98  74 26           je 0x4bc0
4B9A  8B 46 08        mov ax, word ptr [bp + 8]
4B9D  BA 14 00        mov dx, 0x14
4BA0  F7 E2           mul dx
4BA2  C4 3E 1B A9     les di, ptr [0xa91b]
4BA6  03 F8           add di, ax
4BA8  26 80 7D 06 01  cmp byte ptr es:[di + 6], 1
4BAD  76 11           jbe 0x4bc0
4BAF  80 7E 06 00     cmp byte ptr [bp + 6], 0
4BB3  74 0B           je 0x4bc0
4BB5  FF 76 08        push word ptr [bp + 8]
4BB8  0E              push cs
4BB9  E8 5A E6        call 0x3216
4BBC  08 C0           or al, al
4BBE  74 04           je 0x4bc4
loc_4BC0:
4BC0  B0 00           mov al, 0
4BC2  EB 02           jmp 0x4bc6
loc_4BC4:
4BC4  B0 01           mov al, 1
loc_4BC6:
4BC6  88 46 FF        mov byte ptr [bp - 1], al
4BC9  83 3E 38 0F 05  cmp word ptr [0xf38], 5
4BCE  75 0C           jne 0x4bdc
4BD0  80 7E FF 00     cmp byte ptr [bp - 1], 0
4BD4  75 06           jne 0x4bdc
4BD6  C7 06 38 0F 01 00 mov word ptr [0xf38], 1
loc_4BDC:
4BDC  FF 76 08        push word ptr [bp + 8]
4BDF  0E              push cs
4BE0  E8 D9 F6        call 0x42bc
4BE3  A1 38 0F        mov ax, word ptr [0xf38]
4BE6  05 0B 00        add ax, 0xb
4BE9  50              push ax
4BEA  B8 26 00        mov ax, 0x26
4BED  50              push ax
4BEE  B8 18 00        mov ax, 0x18
4BF1  50              push ax
4BF2  9A C5 13 4B 21  call far 214B:13C5
4BF7  BF 38 0F        mov di, 0xf38
4BFA  1E              push ds
4BFB  57              push di
4BFC  8A 46 FF        mov al, byte ptr [bp - 1]
4BFF  30 E4           xor ah, ah
4C01  05 04 00        add ax, 4
4C04  50              push ax
4C05  9A 60 15 4B 21  call far 214B:1560
4C0A  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
4C0F  74 03           je 0x4c14
4C11  E9 D3 00        jmp 0x4ce7
loc_4C14:
4C14  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
4C19  74 05           je 0x4c20
4C1B  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
loc_4C20:
4C20  83 3E 38 0F 05  cmp word ptr [0xf38], 5
4C25  75 07           jne 0x4c2e
4C27  55              push bp
4C28  E8 8D FD        call 0x49b8
4C2B  E9 B9 00        jmp 0x4ce7
loc_4C2E:
4C2E  A1 38 0F        mov ax, word ptr [0xf38]
4C31  05 04 00        add ax, 4
4C34  50              push ax
4C35  C4 7E FB        les di, ptr [bp - 5]
4C38  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
4C3C  30 E4           xor ah, ah
4C3E  50              push ax
4C3F  9A 57 0C 4B 21  call far 214B:0C57
4C44  08 C0           or al, al
4C46  75 29           jne 0x4c71
4C48  A1 38 0F        mov ax, word ptr [0xf38]
4C4B  05 04 00        add ax, 4
4C4E  50              push ax
4C4F  C4 7E FB        les di, ptr [bp - 5]
4C52  81 C7 0F 00     add di, 0xf
4C56  06              push es
4C57  57              push di
4C58  9A 79 0C 4B 21  call far 214B:0C79
4C5D  FF 36 38 0F     push word ptr [0xf38]
4C61  C4 7E FB        les di, ptr [bp - 5]
4C64  81 C7 0F 00     add di, 0xf
4C68  06              push es
4C69  57              push di
4C6A  9A A1 0C 4B 21  call far 214B:0CA1
4C6F  EB 76           jmp 0x4ce7
loc_4C71:
4C71  FF 36 38 0F     push word ptr [0xf38]
4C75  C4 7E FB        les di, ptr [bp - 5]
4C78  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
4C7C  30 E4           xor ah, ah
4C7E  50              push ax
4C7F  9A 57 0C 4B 21  call far 214B:0C57
4C84  08 C0           or al, al
4C86  75 14           jne 0x4c9c
4C88  FF 36 38 0F     push word ptr [0xf38]
4C8C  C4 7E FB        les di, ptr [bp - 5]
4C8F  81 C7 0F 00     add di, 0xf
4C93  06              push es
4C94  57              push di
4C95  9A 79 0C 4B 21  call far 214B:0C79
4C9A  EB 4B           jmp 0x4ce7
loc_4C9C:
4C9C  A1 38 0F        mov ax, word ptr [0xf38]
4C9F  05 04 00        add ax, 4
4CA2  50              push ax
4CA3  C4 7E FB        les di, ptr [bp - 5]
4CA6  81 C7 0F 00     add di, 0xf
4CAA  06              push es
4CAB  57              push di
4CAC  9A A1 0C 4B 21  call far 214B:0CA1
4CB1  FF 36 38 0F     push word ptr [0xf38]
4CB5  C4 7E FB        les di, ptr [bp - 5]
4CB8  81 C7 0F 00     add di, 0xf
4CBC  06              push es
4CBD  57              push di
4CBE  FF 36 38 0F     push word ptr [0xf38]
4CC2  C4 7E FB        les di, ptr [bp - 5]
4CC5  26 8A 05        mov al, byte ptr es:[di]
4CC8  30 E4           xor ah, ah
4CCA  BA BF 00        mov dx, 0xbf
4CCD  F7 E2           mul dx
4CCF  C4 3E 17 A9     les di, ptr [0xa917]
4CD3  03 F8           add di, ax
4CD5  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
4CD9  30 E4           xor ah, ah
4CDB  50              push ax
4CDC  9A 57 0C 4B 21  call far 214B:0C57
4CE1  50              push ax
4CE2  9A CB 0C 4B 21  call far 214B:0CCB
loc_4CE7:
4CE7  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
4CEC  74 03           je 0x4cf1
4CEE  E9 EB FE        jmp 0x4bdc
loc_4CF1:
4CF1  89 EC           mov sp, bp
4CF3  5D              pop bp
4CF4  CA 04 00        retf 4

; ---- routine 1771:4CF7  (found by: far)
sub_4CF7:
4CF7  55              push bp
4CF8  89 E5           mov bp, sp
4CFA  83 EC 06        sub sp, 6
4CFD  B8 F3 01        mov ax, 0x1f3
4D00  50              push ax
4D01  9A B1 06 4B 21  call far 214B:06B1
4D06  05 00 0A        add ax, 0xa00
4D09  89 46 FC        mov word ptr [bp - 4], ax
4D0C  8B 46 FC        mov ax, word ptr [bp - 4]
4D0F  40              inc ax
4D10  89 46 FA        mov word ptr [bp - 6], ax
loc_4D13:
4D13  8B 46 FA        mov ax, word ptr [bp - 6]
4D16  BA 14 00        mov dx, 0x14
4D19  F7 E2           mul dx
4D1B  C4 3E 1B A9     les di, ptr [0xa91b]
4D1F  03 F8           add di, ax
4D21  26 80 3D 00     cmp byte ptr es:[di], 0
4D25  74 1B           je 0x4d42
4D27  8B 46 FA        mov ax, word ptr [bp - 6]
4D2A  3B 46 FC        cmp ax, word ptr [bp - 4]
4D2D  74 13           je 0x4d42
4D2F  81 7E FA F4 0B  cmp word ptr [bp - 6], 0xbf4
4D34  72 07           jb 0x4d3d
4D36  C7 46 FA 01 0A  mov word ptr [bp - 6], 0xa01
4D3B  EB 03           jmp 0x4d40
loc_4D3D:
4D3D  FF 46 FA        inc word ptr [bp - 6]
loc_4D40:
4D40  EB D1           jmp 0x4d13
loc_4D42:
4D42  8B 46 FA        mov ax, word ptr [bp - 6]
4D45  3B 46 FC        cmp ax, word ptr [bp - 4]
4D48  75 33           jne 0x4d7d
4D4A  B8 F3 0B        mov ax, 0xbf3
4D4D  50              push ax
4D4E  9A B1 06 4B 21  call far 214B:06B1
4D53  89 46 FA        mov word ptr [bp - 6], ax
loc_4D56:
4D56  8B 46 FA        mov ax, word ptr [bp - 6]
4D59  BA 14 00        mov dx, 0x14
4D5C  F7 E2           mul dx
4D5E  C4 3E 1B A9     les di, ptr [0xa91b]
4D62  03 F8           add di, ax
4D64  26 80 3D 00     cmp byte ptr es:[di], 0
4D68  74 13           je 0x4d7d
4D6A  81 7E FA F4 0B  cmp word ptr [bp - 6], 0xbf4
4D6F  72 07           jb 0x4d78
4D71  C7 46 FA 01 00  mov word ptr [bp - 6], 1
4D76  EB 03           jmp 0x4d7b
loc_4D78:
4D78  FF 46 FA        inc word ptr [bp - 6]
loc_4D7B:
4D7B  EB D9           jmp 0x4d56
loc_4D7D:
4D7D  8B 46 FA        mov ax, word ptr [bp - 6]
4D80  89 46 FE        mov word ptr [bp - 2], ax
4D83  8B 46 FE        mov ax, word ptr [bp - 2]
4D86  89 EC           mov sp, bp
4D88  5D              pop bp
4D89  CB              retf

; ---- routine 1771:4D8A  (found by: call, far)
sub_4D8A:
4D8A  55              push bp
4D8B  89 E5           mov bp, sp
4D8D  83 EC 06        sub sp, 6
4D90  8B 46 06        mov ax, word ptr [bp + 6]
4D93  BA BF 00        mov dx, 0xbf
4D96  F7 E2           mul dx
4D98  C4 3E 17 A9     les di, ptr [0xa917]
4D9C  03 F8           add di, ax
4D9E  89 7E FA        mov word ptr [bp - 6], di
4DA1  8C 46 FC        mov word ptr [bp - 4], es
4DA4  BF A4 15        mov di, 0x15a4
4DA7  1E              push ds
4DA8  57              push di
4DA9  BF 6E A9        mov di, 0xa96e
4DAC  1E              push ds
4DAD  57              push di
4DAE  9A 29 03 4B 21  call far 214B:0329
4DB3  FF 76 06        push word ptr [bp + 6]
4DB6  B8 01 00        mov ax, 1
4DB9  50              push ax
4DBA  B8 41 00        mov ax, 0x41
4DBD  50              push ax
4DBE  0E              push cs
4DBF  E8 96 C1        call 0xf58
4DC2  C7 46 FE 01 00  mov word ptr [bp - 2], 1
4DC7  EB 03           jmp 0x4dcc
loc_4DC9:
4DC9  FF 46 FE        inc word ptr [bp - 2]
loc_4DCC:
4DCC  8B 46 FE        mov ax, word ptr [bp - 2]
4DCF  D1 E0           shl ax, 1
4DD1  C4 7E FA        les di, ptr [bp - 6]
4DD4  03 F8           add di, ax
4DD6  26 FF 75 FE     push word ptr es:[di - 2]
4DDA  8B 46 FE        mov ax, word ptr [bp - 2]
4DDD  05 02 00        add ax, 2
4DE0  50              push ax
4DE1  B8 41 00        mov ax, 0x41
4DE4  50              push ax
4DE5  0E              push cs
4DE6  E8 4E E1        call 0x2f37
4DE9  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
4DED  75 DA           jne 0x4dc9
4DEF  C7 46 FE 0C 00  mov word ptr [bp - 2], 0xc
4DF4  EB 03           jmp 0x4df9
loc_4DF6:
4DF6  FF 46 FE        inc word ptr [bp - 2]
loc_4DF9:
4DF9  8B 46 FE        mov ax, word ptr [bp - 2]
4DFC  D1 E0           shl ax, 1
4DFE  C4 7E FA        les di, ptr [bp - 6]
4E01  03 F8           add di, ax
4E03  26 FF 75 FE     push word ptr es:[di - 2]
4E07  8B 46 FE        mov ax, word ptr [bp - 2]
4E0A  05 03 00        add ax, 3
4E0D  50              push ax
4E0E  B8 41 00        mov ax, 0x41
4E11  50              push ax
4E12  0E              push cs
4E13  E8 21 E1        call 0x2f37
4E16  83 7E FE 14     cmp word ptr [bp - 2], 0x14
4E1A  75 DA           jne 0x4df6
4E1C  89 EC           mov sp, bp
4E1E  5D              pop bp
4E1F  CA 02 00        retf 2

; ---- routine 1771:4E22  (found by: call, far)
sub_4E22:
4E22  55              push bp
4E23  89 E5           mov bp, sp
4E25  81 EC 06 01     sub sp, 0x106
4E29  8B 46 08        mov ax, word ptr [bp + 8]
4E2C  BA BF 00        mov dx, 0xbf
4E2F  F7 E2           mul dx
4E31  C4 3E 17 A9     les di, ptr [0xa917]
4E35  03 F8           add di, ax
4E37  89 7E FA        mov word ptr [bp - 6], di
4E3A  8C 46 FC        mov word ptr [bp - 4], es
4E3D  FF 76 08        push word ptr [bp + 8]
4E40  0E              push cs
4E41  E8 46 FF        call 0x4d8a
4E44  BF F2 26        mov di, 0x26f2
4E47  1E              push ds
4E48  57              push di
4E49  BF 6E A9        mov di, 0xa96e
4E4C  1E              push ds
4E4D  57              push di
4E4E  9A 29 03 4B 21  call far 214B:0329
4E53  B0 00           mov al, 0
4E55  08 C0           or al, al
4E57  75 06           jne 0x4e5f
4E59  83 7E 06 02     cmp word ptr [bp + 6], 2
4E5D  75 0F           jne 0x4e6e
loc_4E5F:
4E5F  BF 9C 26        mov di, 0x269c
4E62  1E              push ds
4E63  57              push di
4E64  BF 6E A9        mov di, 0xa96e
4E67  1E              push ds
4E68  57              push di
4E69  9A 29 03 4B 21  call far 214B:0329
loc_4E6E:
4E6E  BF 8A 26        mov di, 0x268a
4E71  1E              push ds
4E72  57              push di
4E73  BF 6E A9        mov di, 0xa96e
4E76  1E              push ds
4E77  57              push di
4E78  9A 29 03 4B 21  call far 214B:0329
4E7D  83 7E 06 01     cmp word ptr [bp + 6], 1
4E81  75 0F           jne 0x4e92
4E83  BF F6 1A        mov di, 0x1af6
4E86  1E              push ds
4E87  57              push di
4E88  BF 6E A9        mov di, 0xa96e
4E8B  1E              push ds
4E8C  57              push di
4E8D  9A 29 03 4B 21  call far 214B:0329
loc_4E92:
4E92  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
4E97  75 33           jne 0x4ecc
4E99  83 7E 06 01     cmp word ptr [bp + 6], 1
4E9D  74 0B           je 0x4eaa
4E9F  FF 76 08        push word ptr [bp + 8]
4EA2  0E              push cs
4EA3  E8 D1 BC        call 0xb77
4EA6  08 C0           or al, al
4EA8  75 11           jne 0x4ebb
loc_4EAA:
4EAA  BF 1A 5A        mov di, 0x5a1a
4EAD  1E              push ds
4EAE  57              push di
4EAF  BF 6E A9        mov di, 0xa96e
4EB2  1E              push ds
4EB3  57              push di
4EB4  9A 29 03 4B 21  call far 214B:0329
4EB9  EB 0F           jmp 0x4eca
loc_4EBB:
4EBB  BF F0 57        mov di, 0x57f0
4EBE  1E              push ds
4EBF  57              push di
4EC0  BF 6E A9        mov di, 0xa96e
4EC3  1E              push ds
4EC4  57              push di
4EC5  9A 29 03 4B 21  call far 214B:0329
loc_4ECA:
4ECA  EB 67           jmp 0x4f33
loc_4ECC:
4ECC  BF 1A 5A        mov di, 0x5a1a
4ECF  1E              push ds
4ED0  57              push di
4ED1  BF 6E A9        mov di, 0xa96e
4ED4  1E              push ds
4ED5  57              push di
4ED6  9A 29 03 4B 21  call far 214B:0329
4EDB  BF 04 17        mov di, 0x1704
4EDE  1E              push ds
4EDF  57              push di
4EE0  BF 6E A9        mov di, 0xa96e
4EE3  1E              push ds
4EE4  57              push di
4EE5  9A 29 03 4B 21  call far 214B:0329
4EEA  BF CC 47        mov di, 0x47cc
4EED  1E              push ds
4EEE  57              push di
4EEF  BF 6E A9        mov di, 0xa96e
4EF2  1E              push ds
4EF3  57              push di
4EF4  9A 29 03 4B 21  call far 214B:0329
4EF9  B0 0F           mov al, 0xf
4EFB  50              push ax
4EFC  8D BE FA FE     lea di, [bp - 0x106]
4F00  16              push ss
4F01  57              push di
4F02  8B 46 08        mov ax, word ptr [bp + 8]
4F05  3B 06 36 9B     cmp ax, word ptr [0x9b36]
4F09  74 04           je 0x4f0f
4F0B  B0 00           mov al, 0
4F0D  EB 02           jmp 0x4f11
loc_4F0F:
4F0F  B0 01           mov al, 1
loc_4F11:
4F11  98              cwde
4F12  8B F8           mov di, ax
4F14  8A 85 3A 9B     mov al, byte ptr [di - 0x64c6]
4F18  30 E4           xor ah, ah
4F1A  31 D2           xor dx, dx
4F1C  52              push dx
4F1D  50              push ax
4F1E  9A DA 09 4B 21  call far 214B:09DA
4F23  B0 05           mov al, 5
4F25  50              push ax
4F26  B0 3C           mov al, 0x3c
4F28  50              push ax
4F29  BF 6E A9        mov di, 0xa96e
4F2C  1E              push ds
4F2D  57              push di
4F2E  9A C8 02 4B 21  call far 214B:02C8
loc_4F33:
4F33  A1 1B 0C        mov ax, word ptr [0xc1b]
4F36  D1 E0           shl ax, 1
4F38  C4 7E FA        les di, ptr [bp - 6]
4F3B  03 F8           add di, ax
4F3D  26 FF 75 FE     push word ptr es:[di - 2]
4F41  0E              push cs
4F42  E8 77 F3        call 0x42bc
4F45  83 3E 1B 0C 0B  cmp word ptr [0xc1b], 0xb
4F4A  77 04           ja 0x4f50
4F4C  B0 00           mov al, 0
4F4E  EB 02           jmp 0x4f52
loc_4F50:
4F50  B0 01           mov al, 1
loc_4F52:
4F52  30 E4           xor ah, ah
4F54  8B D0           mov dx, ax
4F56  A1 1B 0C        mov ax, word ptr [0xc1b]
4F59  05 02 00        add ax, 2
4F5C  03 C2           add ax, dx
4F5E  50              push ax
4F5F  B8 41 00        mov ax, 0x41
4F62  50              push ax
4F63  B8 0C 00        mov ax, 0xc
4F66  50              push ax
4F67  9A C5 13 4B 21  call far 214B:13C5
4F6C  89 EC           mov sp, bp
4F6E  5D              pop bp
4F6F  CA 04 00        retf 4
; data (not reached as code), 56 bytes
4F72                  pstr ' has too many '
4F81                  pstr 's in 1st team'
4F8F                  pstr ' has no keeper in 1st team'

; ---- routine 1771:4FAA  (found by: call)
sub_4FAA:
4FAA  55              push bp
4FAB  89 E5           mov bp, sp
4FAD  81 EC 16 01     sub sp, 0x116
4FB1  8B 7E 04        mov di, word ptr [bp + 4]
4FB4  36 8B 45 08     mov ax, word ptr ss:[di + 8]
4FB8  BA BF 00        mov dx, 0xbf
4FBB  F7 E2           mul dx
4FBD  C4 3E 17 A9     les di, ptr [0xa917]
4FC1  03 F8           add di, ax
4FC3  89 7E EA        mov word ptr [bp - 0x16], di
4FC6  8C 46 EC        mov word ptr [bp - 0x14], es
4FC9  C6 46 EE 01     mov byte ptr [bp - 0x12], 1
4FCD  8D 7E F1        lea di, [bp - 0xf]
4FD0  16              push ss
4FD1  57              push di
4FD2  B8 0E 00        mov ax, 0xe
4FD5  50              push ax
4FD6  31 C0           xor ax, ax
4FD8  50              push ax
4FD9  9A 18 00 4B 21  call far 214B:0018
4FDE  C7 46 EF 01 00  mov word ptr [bp - 0x11], 1
4FE3  EB 03           jmp 0x4fe8
loc_4FE5:
4FE5  FF 46 EF        inc word ptr [bp - 0x11]
loc_4FE8:
4FE8  8B 46 EF        mov ax, word ptr [bp - 0x11]
4FEB  D1 E0           shl ax, 1
4FED  C4 7E EA        les di, ptr [bp - 0x16]
4FF0  03 F8           add di, ax
4FF2  26 8B 45 FE     mov ax, word ptr es:[di - 2]
4FF6  BA 14 00        mov dx, 0x14
4FF9  F7 E2           mul dx
4FFB  C4 3E 1B A9     les di, ptr [0xa91b]
4FFF  03 F8           add di, ax
5001  89 7E E6        mov word ptr [bp - 0x1a], di
5004  8C 46 E8        mov word ptr [bp - 0x18], es
5007  C4 7E E6        les di, ptr [bp - 0x1a]
500A  26 8A 45 07     mov al, byte ptr es:[di + 7]
500E  30 E4           xor ah, ah
5010  8B F8           mov di, ax
5012  FE 43 F1        inc byte ptr [bp + di - 0xf]
5015  83 7E EF 0B     cmp word ptr [bp - 0x11], 0xb
5019  75 CA           jne 0x4fe5
501B  31 C0           xor ax, ax
501D  89 46 EF        mov word ptr [bp - 0x11], ax
5020  EB 03           jmp 0x5025
loc_5022:
5022  FF 46 EF        inc word ptr [bp - 0x11]
loc_5025:
5025  8B 7E EF        mov di, word ptr [bp - 0x11]
5028  80 7B F1 01     cmp byte ptr [bp + di - 0xf], 1
502C  76 06           jbe 0x5034
502E  83 7E EF 00     cmp word ptr [bp - 0x11], 0
5032  74 09           je 0x503d
loc_5034:
5034  8B 7E EF        mov di, word ptr [bp - 0x11]
5037  80 7B F1 03     cmp byte ptr [bp + di - 0xf], 3
503B  76 5C           jbe 0x5099
loc_503D:
503D  B0 01           mov al, 1
503F  50              push ax
5040  8D BE EA FE     lea di, [bp - 0x116]
5044  16              push ss
5045  57              push di
5046  8B 7E 04        mov di, word ptr [bp + 4]
5049  36 8B 45 08     mov ax, word ptr ss:[di + 8]
504D  B1 04           mov cl, 4
504F  D3 E0           shl ax, cl
5051  C4 3E 68 9B     les di, ptr [0x9b68]
5055  03 F8           add di, ax
5057  06              push es
5058  57              push di
5059  9A 2A 06 E4 23  call far 23E4:062A
505E  BF 72 4F        mov di, 0x4f72
5061  0E              push cs
5062  57              push di
5063  9A B7 06 E4 23  call far 23E4:06B7
5068  8B 46 EF        mov ax, word ptr [bp - 0x11]
506B  BA 13 00        mov dx, 0x13
506E  F7 E2           mul dx
5070  8B F8           mov di, ax
5072  81 C7 B6 69     add di, 0x69b6
5076  1E              push ds
5077  57              push di
5078  9A B7 06 E4 23  call far 23E4:06B7
507D  BF 81 4F        mov di, 0x4f81
5080  0E              push cs
5081  57              push di
5082  9A B7 06 E4 23  call far 23E4:06B7
5087  9A 65 17 4B 21  call far 214B:1765
508C  08 C0           or al, al
508E  74 04           je 0x5094
5090  B0 00           mov al, 0
5092  EB 02           jmp 0x5096
loc_5094:
5094  B0 01           mov al, 1
loc_5096:
5096  88 46 EE        mov byte ptr [bp - 0x12], al
loc_5099:
5099  83 7E EF 0D     cmp word ptr [bp - 0x11], 0xd
509D  75 83           jne 0x5022
509F  80 7E F1 00     cmp byte ptr [bp - 0xf], 0
50A3  75 3D           jne 0x50e2
50A5  B0 01           mov al, 1
50A7  50              push ax
50A8  8D BE EA FE     lea di, [bp - 0x116]
50AC  16              push ss
50AD  57              push di
50AE  8B 7E 04        mov di, word ptr [bp + 4]
50B1  36 8B 45 08     mov ax, word ptr ss:[di + 8]
50B5  B1 04           mov cl, 4
50B7  D3 E0           shl ax, cl
50B9  C4 3E 68 9B     les di, ptr [0x9b68]
50BD  03 F8           add di, ax
50BF  06              push es
50C0  57              push di
50C1  9A 2A 06 E4 23  call far 23E4:062A
50C6  BF 8F 4F        mov di, 0x4f8f
50C9  0E              push cs
50CA  57              push di
50CB  9A B7 06 E4 23  call far 23E4:06B7
50D0  9A 65 17 4B 21  call far 214B:1765
50D5  08 C0           or al, al
50D7  74 04           je 0x50dd
50D9  B0 00           mov al, 0
50DB  EB 02           jmp 0x50df
loc_50DD:
50DD  B0 01           mov al, 1
loc_50DF:
50DF  88 46 EE        mov byte ptr [bp - 0x12], al
loc_50E2:
50E2  8A 46 EE        mov al, byte ptr [bp - 0x12]
50E5  88 46 FF        mov byte ptr [bp - 1], al
50E8  8A 46 FF        mov al, byte ptr [bp - 1]
50EB  89 EC           mov sp, bp
50ED  5D              pop bp
50EE  C2 02 00        ret 2

; ---- routine 1771:50F1  (found by: call, far)
sub_50F1:
50F1  55              push bp
50F2  89 E5           mov bp, sp
50F4  83 EC 08        sub sp, 8
50F7  8B 46 08        mov ax, word ptr [bp + 8]
50FA  BA BF 00        mov dx, 0xbf
50FD  F7 E2           mul dx
50FF  C4 3E 17 A9     les di, ptr [0xa917]
5103  03 F8           add di, ax
5105  89 7E F9        mov word ptr [bp - 7], di
5108  8C 46 FB        mov word ptr [bp - 5], es
loc_510B:
510B  FF 76 08        push word ptr [bp + 8]
510E  FF 76 06        push word ptr [bp + 6]
5111  0E              push cs
5112  E8 0D FD        call 0x4e22
5115  BF 1B 0C        mov di, 0xc1b
5118  1E              push ds
5119  57              push di
511A  B8 14 00        mov ax, 0x14
511D  50              push ax
511E  9A 60 15 4B 21  call far 214B:1560
5123  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
5128  74 04           je 0x512e
512A  B0 00           mov al, 0
512C  EB 02           jmp 0x5130
loc_512E:
512E  B0 01           mov al, 1
loc_5130:
5130  88 46 FF        mov byte ptr [bp - 1], al
5133  A0 76 A9        mov al, byte ptr [0xa976]
5136  50              push ax
5137  9A B2 19 E4 23  call far 23E4:19B2
513C  3C A0           cmp al, 0xa0
513E  75 1C           jne 0x515c
5140  A1 1B 0C        mov ax, word ptr [0xc1b]
5143  D1 E0           shl ax, 1
5145  C4 7E F9        les di, ptr [bp - 7]
5148  03 F8           add di, ax
514A  26 FF 75 FE     push word ptr es:[di - 2]
514E  B8 08 00        mov ax, 8
5151  50              push ax
5152  B8 02 00        mov ax, 2
5155  50              push ax
5156  0E              push cs
5157  E8 FF F6        call 0x4859
515A  EB 04           jmp 0x5160
loc_515C:
515C  3C 52           cmp al, 0x52
515E  75 00           jne 0x5160
loc_5160:
5160  80 7E FF 00     cmp byte ptr [bp - 1], 0
5164  74 A5           je 0x510b
5166  B0 01           mov al, 1
5168  08 C0           or al, al
516A  75 08           jne 0x5174
516C  55              push bp
516D  E8 3A FE        call 0x4faa
5170  08 C0           or al, al
5172  74 97           je 0x510b
loc_5174:
5174  89 EC           mov sp, bp
5176  5D              pop bp
5177  CA 04 00        retf 4

; ---- routine 1771:517A  (found by: call)
sub_517A:
517A  55              push bp
517B  89 E5           mov bp, sp
517D  83 EC 0C        sub sp, 0xc
5180  8B 7E 04        mov di, word ptr [bp + 4]
5183  36 8B 45 06     mov ax, word ptr ss:[di + 6]
5187  BA BF 00        mov dx, 0xbf
518A  F7 E2           mul dx
518C  C4 3E 17 A9     les di, ptr [0xa917]
5190  03 F8           add di, ax
5192  89 7E F4        mov word ptr [bp - 0xc], di
5195  8C 46 F6        mov word ptr [bp - 0xa], es
5198  8B 46 08        mov ax, word ptr [bp + 8]
519B  89 46 FE        mov word ptr [bp - 2], ax
519E  8B 46 06        mov ax, word ptr [bp + 6]
51A1  89 46 FC        mov word ptr [bp - 4], ax
51A4  8B 46 08        mov ax, word ptr [bp + 8]
51A7  03 46 06        add ax, word ptr [bp + 6]
51AA  31 D2           xor dx, dx
51AC  B9 02 00        mov cx, 2
51AF  F7 F1           div cx
51B1  D1 E0           shl ax, 1
51B3  C4 7E F4        les di, ptr [bp - 0xc]
51B6  03 F8           add di, ax
51B8  26 8B 45 FE     mov ax, word ptr es:[di - 2]
51BC  BA 14 00        mov dx, 0x14
51BF  F7 E2           mul dx
51C1  C4 3E 1B A9     les di, ptr [0xa91b]
51C5  03 F8           add di, ax
51C7  26 8A 45 06     mov al, byte ptr es:[di + 6]
51CB  30 E4           xor ah, ah
51CD  89 46 F8        mov word ptr [bp - 8], ax
loc_51D0:
51D0  8B 46 FE        mov ax, word ptr [bp - 2]
51D3  D1 E0           shl ax, 1
51D5  C4 7E F4        les di, ptr [bp - 0xc]
51D8  03 F8           add di, ax
51DA  26 8B 45 FE     mov ax, word ptr es:[di - 2]
51DE  BA 14 00        mov dx, 0x14
51E1  F7 E2           mul dx
51E3  C4 3E 1B A9     les di, ptr [0xa91b]
51E7  03 F8           add di, ax
51E9  26 8A 45 06     mov al, byte ptr es:[di + 6]
51ED  30 E4           xor ah, ah
51EF  3B 46 F8        cmp ax, word ptr [bp - 8]
51F2  73 05           jae 0x51f9
51F4  FF 46 FE        inc word ptr [bp - 2]
51F7  EB D7           jmp 0x51d0
loc_51F9:
51F9  8B 46 FC        mov ax, word ptr [bp - 4]
51FC  D1 E0           shl ax, 1
51FE  C4 7E F4        les di, ptr [bp - 0xc]
5201  03 F8           add di, ax
5203  26 8B 45 FE     mov ax, word ptr es:[di - 2]
5207  BA 14 00        mov dx, 0x14
520A  F7 E2           mul dx
520C  C4 3E 1B A9     les di, ptr [0xa91b]
5210  03 F8           add di, ax
5212  26 8A 45 06     mov al, byte ptr es:[di + 6]
5216  30 E4           xor ah, ah
5218  3B 46 F8        cmp ax, word ptr [bp - 8]
521B  76 05           jbe 0x5222
521D  FF 4E FC        dec word ptr [bp - 4]
5220  EB D7           jmp 0x51f9
loc_5222:
5222  8B 46 FE        mov ax, word ptr [bp - 2]
5225  3B 46 FC        cmp ax, word ptr [bp - 4]
5228  77 69           ja 0x5293
522A  8B 46 FE        mov ax, word ptr [bp - 2]
522D  D1 E0           shl ax, 1
522F  C4 7E F4        les di, ptr [bp - 0xc]
5232  03 F8           add di, ax
5234  26 8B 45 FE     mov ax, word ptr es:[di - 2]
5238  89 46 FA        mov word ptr [bp - 6], ax
523B  8B 46 FC        mov ax, word ptr [bp - 4]
523E  D1 E0           shl ax, 1
5240  C4 7E F4        les di, ptr [bp - 0xc]
5243  03 F8           add di, ax
5245  26 8B 55 FE     mov dx, word ptr es:[di - 2]
5249  8B 46 FE        mov ax, word ptr [bp - 2]
524C  D1 E0           shl ax, 1
524E  C4 7E F4        les di, ptr [bp - 0xc]
5251  03 F8           add di, ax
5253  26 89 55 FE     mov word ptr es:[di - 2], dx
5257  8B 56 FA        mov dx, word ptr [bp - 6]
525A  8B 46 FC        mov ax, word ptr [bp - 4]
525D  D1 E0           shl ax, 1
525F  C4 7E F4        les di, ptr [bp - 0xc]
5262  03 F8           add di, ax
5264  26 89 55 FE     mov word ptr es:[di - 2], dx
5268  8B 46 FE        mov ax, word ptr [bp - 2]
526B  8B 7E 04        mov di, word ptr [bp + 4]
526E  03 F8           add di, ax
5270  81 C7 EB FF     add di, 0xffeb
5274  16              push ss
5275  57              push di
5276  8B 46 FC        mov ax, word ptr [bp - 4]
5279  8B 7E 04        mov di, word ptr [bp + 4]
527C  03 F8           add di, ax
527E  81 C7 EB FF     add di, 0xffeb
5282  16              push ss
5283  57              push di
5284  B8 01 00        mov ax, 1
5287  50              push ax
5288  9A 7B 00 4B 21  call far 214B:007B
528D  FF 46 FE        inc word ptr [bp - 2]
5290  FF 4E FC        dec word ptr [bp - 4]
loc_5293:
5293  8B 46 FE        mov ax, word ptr [bp - 2]
5296  3B 46 FC        cmp ax, word ptr [bp - 4]
5299  77 03           ja 0x529e
529B  E9 32 FF        jmp 0x51d0
loc_529E:
529E  8B 46 08        mov ax, word ptr [bp + 8]
52A1  3B 46 FC        cmp ax, word ptr [bp - 4]
52A4  73 0C           jae 0x52b2
52A6  FF 76 08        push word ptr [bp + 8]
52A9  FF 76 FC        push word ptr [bp - 4]
52AC  FF 76 04        push word ptr [bp + 4]
52AF  E8 C8 FE        call 0x517a
loc_52B2:
52B2  8B 46 FE        mov ax, word ptr [bp - 2]
52B5  3B 46 06        cmp ax, word ptr [bp + 6]
52B8  73 0C           jae 0x52c6
52BA  FF 76 FE        push word ptr [bp - 2]
52BD  FF 76 06        push word ptr [bp + 6]
52C0  FF 76 04        push word ptr [bp + 4]
52C3  E8 B4 FE        call 0x517a
loc_52C6:
52C6  89 EC           mov sp, bp
52C8  5D              pop bp
52C9  C2 06 00        ret 6

