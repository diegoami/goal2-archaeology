; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 13 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:7881  (found by: call)
sub_7881:
7881  55              push bp
7882  89 E5           mov bp, sp
7884  83 EC 08        sub sp, 8
7887  8B 46 04        mov ax, word ptr [bp + 4]
788A  BA 16 00        mov dx, 0x16
788D  F7 E2           mul dx
788F  8B F8           mov di, ax
7891  81 C7 E8 80     add di, 0x80e8
7895  89 7E F8        mov word ptr [bp - 8], di
7898  8C 5E FA        mov word ptr [bp - 6], ds
789B  C4 7E F8        les di, ptr [bp - 8]
789E  26 8B 05        mov ax, word ptr es:[di]
78A1  3B 06 40 06     cmp ax, word ptr [0x640]
78A5  75 03           jne 0x78aa
78A7  E9 DD 00        jmp 0x7987
loc_78AA:
78AA  C6 06 02 83 01  mov byte ptr [0x8302], 1
78AF  C4 7E F8        les di, ptr [bp - 8]
78B2  26 C6 45 12 0C  mov byte ptr es:[di + 0x12], 0xc
78B7  A1 42 06        mov ax, word ptr [0x642]
78BA  C4 7E F8        les di, ptr [bp - 8]
78BD  26 89 45 07     mov word ptr es:[di + 7], ax
78C1  A0 25 83        mov al, byte ptr [0x8325]
78C4  88 46 FD        mov byte ptr [bp - 3], al
78C7  C6 06 25 83 00  mov byte ptr [0x8325], 0
78CC  A0 41 9B        mov al, byte ptr [0x9b41]
78CF  88 46 FC        mov byte ptr [bp - 4], al
78D2  C6 06 41 9B 00  mov byte ptr [0x9b41], 0
78D7  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
78DC  75 7C           jne 0x795a
loc_78DE:
78DE  C4 7E F8        les di, ptr [bp - 8]
78E1  06              push es
78E2  57              push di
78E3  0E              push cs
78E4  E8 02 12        call 0x8ae9
78E7  C7 46 FE 01 00  mov word ptr [bp - 2], 1
78EC  EB 03           jmp 0x78f1
loc_78EE:
78EE  FF 46 FE        inc word ptr [bp - 2]
loc_78F1:
78F1  E8 F4 1B        call 0x94e8
78F4  9A 23 07 4B 21  call far 214B:0723
78F9  08 C0           or al, al
78FB  74 05           je 0x7902
78FD  9A DD 08 4B 21  call far 214B:08DD
loc_7902:
7902  C4 3E 23 A9     les di, ptr [0xa923]
7906  26 80 7D 3F 00  cmp byte ptr es:[di + 0x3f], 0
790B  75 0B           jne 0x7918
790D  B8 02 00        mov ax, 2
7910  50              push ax
7911  9A 09 1E 4B 21  call far 214B:1E09
7916  EB 14           jmp 0x792c
loc_7918:
7918  C4 3E 23 A9     les di, ptr [0xa923]
791C  26 80 7D 3F 01  cmp byte ptr es:[di + 0x3f], 1
7921  75 09           jne 0x792c
7923  B8 01 00        mov ax, 1
7926  50              push ax
7927  9A 09 1E 4B 21  call far 214B:1E09
loc_792C:
792C  8B 46 FE        mov ax, word ptr [bp - 2]
792F  BA 16 00        mov dx, 0x16
7932  F7 E2           mul dx
7934  8B F8           mov di, ax
7936  81 C7 E8 80     add di, 0x80e8
793A  1E              push ds
793B  57              push di
793C  0E              push cs
793D  E8 F7 0B        call 0x8537
7940  83 7E FE 16     cmp word ptr [bp - 2], 0x16
7944  75 A8           jne 0x78ee
7946  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
794B  75 0D           jne 0x795a
794D  C4 7E F8        les di, ptr [bp - 8]
7950  06              push es
7951  57              push di
7952  0E              push cs
7953  E8 6F B3        call 0x2cc5
7956  08 C0           or al, al
7958  74 84           je 0x78de
loc_795A:
795A  8A 46 FC        mov al, byte ptr [bp - 4]
795D  A2 41 9B        mov byte ptr [0x9b41], al
7960  8A 46 FD        mov al, byte ptr [bp - 3]
7963  A2 25 83        mov byte ptr [0x8325], al
7966  A1 40 06        mov ax, word ptr [0x640]
7969  C4 7E F8        les di, ptr [bp - 8]
796C  26 89 05        mov word ptr es:[di], ax
796F  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
7974  75 09           jne 0x797f
7976  C4 7E F8        les di, ptr [bp - 8]
7979  06              push es
797A  57              push di
797B  0E              push cs
797C  E8 B8 0B        call 0x8537
loc_797F:
797F  C4 7E F8        les di, ptr [bp - 8]
7982  26 C6 45 12 00  mov byte ptr es:[di + 0x12], 0
loc_7987:
7987  89 EC           mov sp, bp
7989  5D              pop bp
798A  C2 02 00        ret 2

; ---- routine 0791:798D  (found by: call)
sub_798D:
798D  55              push bp
798E  89 E5           mov bp, sp
7990  83 EC 04        sub sp, 4
7993  C4 7E 06        les di, ptr [bp + 6]
7996  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
799A  BA 14 00        mov dx, 0x14
799D  F7 E2           mul dx
799F  C4 3E 1B A9     les di, ptr [0xa91b]
79A3  03 F8           add di, ax
79A5  89 7E FC        mov word ptr [bp - 4], di
79A8  8C 46 FE        mov word ptr [bp - 2], es
79AB  B0 32           mov al, 0x32
79AD  50              push ax
79AE  E8 23 B1        call 0x2ad4
79B1  B8 FE 0E        mov ax, 0xefe
79B4  50              push ax
79B5  FF 36 EE 82     push word ptr [0x82ee]
79B9  BF 04 83        mov di, 0x8304
79BC  1E              push ds
79BD  57              push di
79BE  0E              push cs
79BF  E8 03 17        call 0x90c5
79C2  C4 3E 23 A9     les di, ptr [0xa923]
79C6  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
79CA  30 E4           xor ah, ah
79CC  B9 C8 00        mov cx, 0xc8
79CF  F7 E9           imul cx
79D1  50              push ax
79D2  E8 50 8A        call 0x425
79D5  BF 04 83        mov di, 0x8304
79D8  1E              push ds
79D9  57              push di
79DA  0E              push cs
79DB  E8 9B 16        call 0x9079
79DE  B8 05 00        mov ax, 5
79E1  50              push ax
79E2  C4 7E FC        les di, ptr [bp - 4]
79E5  81 C7 10 00     add di, 0x10
79E9  06              push es
79EA  57              push di
79EB  9A 79 0C 4B 21  call far 214B:0C79
79F0  C4 7E 06        les di, ptr [bp + 6]
79F3  06              push es
79F4  57              push di
79F5  0E              push cs
79F6  E8 7B AF        call 0x2974
79F9  98              cwde
79FA  BA 0A 00        mov dx, 0xa
79FD  F7 E2           mul dx
79FF  8B F8           mov di, ax
7A01  FE 85 85 7B     inc byte ptr [di + 0x7b85]
7A05  83 3E 21 83 05  cmp word ptr [0x8321], 5
7A0A  73 04           jae 0x7a10
7A0C  FF 06 21 83     inc word ptr [0x8321]
loc_7A10:
7A10  C4 7E 06        les di, ptr [bp + 6]
7A13  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7A17  BA 14 00        mov dx, 0x14
7A1A  F7 E2           mul dx
7A1C  C4 3E 1B A9     les di, ptr [0xa91b]
7A20  03 F8           add di, ax
7A22  26 8A 05        mov al, byte ptr es:[di]
7A25  30 E4           xor ah, ah
7A27  50              push ax
7A28  9A 77 0B 71 17  call far 1771:0B77
7A2D  08 C0           or al, al
7A2F  75 0C           jne 0x7a3d
7A31  C4 7E 06        les di, ptr [bp + 6]
7A34  26 FF 75 0D     push word ptr es:[di + 0xd]
7A38  9A CD 33 71 17  call far 1771:33CD
loc_7A3D:
7A3D  89 EC           mov sp, bp
7A3F  5D              pop bp
7A40  CA 04 00        retf 4

; ---- routine 0791:7A43  (found by: call)
sub_7A43:
7A43  55              push bp
7A44  89 E5           mov bp, sp
7A46  83 EC 0A        sub sp, 0xa
7A49  8A 46 04        mov al, byte ptr [bp + 4]
7A4C  98              cwde
7A4D  8B F8           mov di, ax
7A4F  D1 E7           shl di, 1
7A51  FF B5 34 9B     push word ptr [di - 0x64cc]
7A55  9A 77 0B 71 17  call far 1771:0B77
7A5A  08 C0           or al, al
7A5C  74 37           je 0x7a95
7A5E  8A 46 04        mov al, byte ptr [bp + 4]
7A61  98              cwde
7A62  BA 0A 00        mov dx, 0xa
7A65  F7 E2           mul dx
7A67  8B F8           mov di, ax
7A69  8A 85 86 7B     mov al, byte ptr [di + 0x7b86]
7A6D  30 E4           xor ah, ah
7A6F  8B C8           mov cx, ax
7A71  8A 46 04        mov al, byte ptr [bp + 4]
7A74  98              cwde
7A75  BA 0A 00        mov dx, 0xa
7A78  F7 E2           mul dx
7A7A  8B F8           mov di, ax
7A7C  8A 85 87 7B     mov al, byte ptr [di + 0x7b87]
7A80  30 E4           xor ah, ah
7A82  03 C1           add ax, cx
7A84  3D 03 00        cmp ax, 3
7A87  7C 04           jl 0x7a8d
7A89  B0 00           mov al, 0
7A8B  EB 02           jmp 0x7a8f
loc_7A8D:
7A8D  B0 01           mov al, 1
loc_7A8F:
7A8F  88 46 FF        mov byte ptr [bp - 1], al
7A92  E9 86 00        jmp 0x7b1b
loc_7A95:
7A95  31 C0           xor ax, ax
7A97  89 46 FB        mov word ptr [bp - 5], ax
7A9A  C7 46 FD 01 00  mov word ptr [bp - 3], 1
7A9F  EB 03           jmp 0x7aa4
loc_7AA1:
7AA1  FF 46 FD        inc word ptr [bp - 3]
loc_7AA4:
7AA4  8A 46 04        mov al, byte ptr [bp + 4]
7AA7  98              cwde
7AA8  8B F8           mov di, ax
7AAA  D1 E7           shl di, 1
7AAC  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
7AB0  BA BF 00        mov dx, 0xbf
7AB3  F7 E2           mul dx
7AB5  C4 3E 17 A9     les di, ptr [0xa917]
7AB9  03 F8           add di, ax
7ABB  89 7E F7        mov word ptr [bp - 9], di
7ABE  8C 46 F9        mov word ptr [bp - 7], es
7AC1  8B 46 FD        mov ax, word ptr [bp - 3]
7AC4  D1 E0           shl ax, 1
7AC6  C4 7E F7        les di, ptr [bp - 9]
7AC9  03 F8           add di, ax
7ACB  26 FF 75 FE     push word ptr es:[di - 2]
7ACF  9A 16 32 71 17  call far 1771:3216
7AD4  08 C0           or al, al
7AD6  75 03           jne 0x7adb
7AD8  FF 46 FB        inc word ptr [bp - 5]
loc_7ADB:
7ADB  83 7E FD 14     cmp word ptr [bp - 3], 0x14
7ADF  75 C0           jne 0x7aa1
7AE1  83 7E FB 0B     cmp word ptr [bp - 5], 0xb
7AE5  76 2B           jbe 0x7b12
7AE7  8A 46 04        mov al, byte ptr [bp + 4]
7AEA  98              cwde
7AEB  BA 0A 00        mov dx, 0xa
7AEE  F7 E2           mul dx
7AF0  8B F8           mov di, ax
7AF2  8A 85 86 7B     mov al, byte ptr [di + 0x7b86]
7AF6  30 E4           xor ah, ah
7AF8  8B C8           mov cx, ax
7AFA  8A 46 04        mov al, byte ptr [bp + 4]
7AFD  98              cwde
7AFE  BA 0A 00        mov dx, 0xa
7B01  F7 E2           mul dx
7B03  8B F8           mov di, ax
7B05  8A 85 87 7B     mov al, byte ptr [di + 0x7b87]
7B09  30 E4           xor ah, ah
7B0B  03 C1           add ax, cx
7B0D  3D 03 00        cmp ax, 3
7B10  7C 04           jl 0x7b16
loc_7B12:
7B12  B0 00           mov al, 0
7B14  EB 02           jmp 0x7b18
loc_7B16:
7B16  B0 01           mov al, 1
loc_7B18:
7B18  88 46 FF        mov byte ptr [bp - 1], al
loc_7B1B:
7B1B  8A 46 FF        mov al, byte ptr [bp - 1]
7B1E  89 EC           mov sp, bp
7B20  5D              pop bp
7B21  C2 02 00        ret 2

; ---- routine 0791:7B24  (found by: call)
sub_7B24:
7B24  55              push bp
7B25  89 E5           mov bp, sp
7B27  83 EC 04        sub sp, 4
7B2A  8B 46 04        mov ax, word ptr [bp + 4]
7B2D  BA 14 00        mov dx, 0x14
7B30  F7 E2           mul dx
7B32  C4 3E 1B A9     les di, ptr [0xa91b]
7B36  03 F8           add di, ax
7B38  89 7E FC        mov word ptr [bp - 4], di
7B3B  8C 46 FE        mov word ptr [bp - 2], es
7B3E  B8 06 00        mov ax, 6
7B41  50              push ax
7B42  C4 7E FC        les di, ptr [bp - 4]
7B45  81 C7 10 00     add di, 0x10
7B49  06              push es
7B4A  57              push di
7B4B  9A 79 0C 4B 21  call far 214B:0C79
7B50  B8 05 00        mov ax, 5
7B53  50              push ax
7B54  C4 7E FC        les di, ptr [bp - 4]
7B57  81 C7 10 00     add di, 0x10
7B5B  06              push es
7B5C  57              push di
7B5D  9A A1 0C 4B 21  call far 214B:0CA1
7B62  8A 46 06        mov al, byte ptr [bp + 6]
7B65  98              cwde
7B66  BA 0A 00        mov dx, 0xa
7B69  F7 E2           mul dx
7B6B  8B F8           mov di, ax
7B6D  FE 85 86 7B     inc byte ptr [di + 0x7b86]
7B71  89 EC           mov sp, bp
7B73  5D              pop bp
7B74  C2 04 00        ret 4

; ---- routine 0791:7B77  (found by: call)
sub_7B77:
7B77  55              push bp
7B78  89 E5           mov bp, sp
7B7A  83 EC 0A        sub sp, 0xa
7B7D  C4 7E 06        les di, ptr [bp + 6]
7B80  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7B84  BA 14 00        mov dx, 0x14
7B87  F7 E2           mul dx
7B89  C4 3E 1B A9     les di, ptr [0xa91b]
7B8D  03 F8           add di, ax
7B8F  89 7E FA        mov word ptr [bp - 6], di
7B92  8C 46 FC        mov word ptr [bp - 4], es
7B95  C4 7E 06        les di, ptr [bp + 6]
7B98  06              push es
7B99  57              push di
7B9A  0E              push cs
7B9B  E8 D6 AD        call 0x2974
7B9E  50              push ax
7B9F  E8 A1 FE        call 0x7a43
7BA2  08 C0           or al, al
7BA4  75 03           jne 0x7ba9
7BA6  E9 16 01        jmp 0x7cbf
loc_7BA9:
7BA9  B0 33           mov al, 0x33
7BAB  50              push ax
7BAC  E8 25 AF        call 0x2ad4
7BAF  B8 FE 0C        mov ax, 0xcfe
7BB2  50              push ax
7BB3  FF 36 EE 82     push word ptr [0x82ee]
7BB7  BF 04 83        mov di, 0x8304
7BBA  1E              push ds
7BBB  57              push di
7BBC  0E              push cs
7BBD  E8 05 15        call 0x90c5
7BC0  C4 7E 06        les di, ptr [bp + 6]
7BC3  06              push es
7BC4  57              push di
7BC5  0E              push cs
7BC6  E8 AB AD        call 0x2974
7BC9  50              push ax
7BCA  C4 7E 06        les di, ptr [bp + 6]
7BCD  26 FF 75 0D     push word ptr es:[di + 0xd]
7BD1  E8 50 FF        call 0x7b24
7BD4  C4 7E 06        les di, ptr [bp + 6]
7BD7  26 8A 45 06     mov al, byte ptr es:[di + 6]
7BDB  30 E4           xor ah, ah
7BDD  50              push ax
7BDE  E8 A0 FC        call 0x7881
7BE1  83 3E 21 83 05  cmp word ptr [0x8321], 5
7BE6  73 04           jae 0x7bec
7BE8  FF 06 21 83     inc word ptr [0x8321]
loc_7BEC:
7BEC  BF 04 83        mov di, 0x8304
7BEF  1E              push ds
7BF0  57              push di
7BF1  0E              push cs
7BF2  E8 84 14        call 0x9079
7BF5  B8 FE FF        mov ax, 0xfffe
7BF8  50              push ax
7BF9  B0 01           mov al, 1
7BFB  50              push ax
7BFC  C4 7E 06        les di, ptr [bp + 6]
7BFF  06              push es
7C00  57              push di
7C01  0E              push cs
7C02  E8 C0 00        call 0x7cc5
7C05  C7 46 FE 01 00  mov word ptr [bp - 2], 1
7C0A  EB 03           jmp 0x7c0f
loc_7C0C:
7C0C  FF 46 FE        inc word ptr [bp - 2]
loc_7C0F:
7C0F  C4 7E 06        les di, ptr [bp + 6]
7C12  06              push es
7C13  57              push di
7C14  0E              push cs
7C15  E8 5C AD        call 0x2974
7C18  08 C0           or al, al
7C1A  74 04           je 0x7c20
7C1C  B0 00           mov al, 0
7C1E  EB 02           jmp 0x7c22
loc_7C20:
7C20  B0 01           mov al, 1
loc_7C22:
7C22  98              cwde
7C23  8B F8           mov di, ax
7C25  8A 85 68 06     mov al, byte ptr [di + 0x668]
7C29  30 E4           xor ah, ah
7C2B  03 46 FE        add ax, word ptr [bp - 2]
7C2E  BA 16 00        mov dx, 0x16
7C31  F7 E2           mul dx
7C33  8B F8           mov di, ax
7C35  81 C7 E8 80     add di, 0x80e8
7C39  89 7E F6        mov word ptr [bp - 0xa], di
7C3C  8C 5E F8        mov word ptr [bp - 8], ds
7C3F  C4 7E F6        les di, ptr [bp - 0xa]
7C42  06              push es
7C43  57              push di
7C44  0E              push cs
7C45  E8 0E AD        call 0x2956
7C48  08 C0           or al, al
7C4A  75 10           jne 0x7c5c
7C4C  B8 02 00        mov ax, 2
7C4F  50              push ax
7C50  B0 00           mov al, 0
7C52  50              push ax
7C53  C4 7E F6        les di, ptr [bp - 0xa]
7C56  06              push es
7C57  57              push di
7C58  0E              push cs
7C59  E8 69 00        call 0x7cc5
loc_7C5C:
7C5C  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
7C60  75 AA           jne 0x7c0c
7C62  C4 7E 06        les di, ptr [bp + 6]
7C65  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7C69  BA 14 00        mov dx, 0x14
7C6C  F7 E2           mul dx
7C6E  C4 3E 1B A9     les di, ptr [0xa91b]
7C72  03 F8           add di, ax
7C74  89 7E F6        mov word ptr [bp - 0xa], di
7C77  8C 46 F8        mov word ptr [bp - 8], es
7C7A  C4 7E F6        les di, ptr [bp - 0xa]
7C7D  26 8A 05        mov al, byte ptr es:[di]
7C80  30 E4           xor ah, ah
7C82  50              push ax
7C83  9A 77 0B 71 17  call far 1771:0B77
7C88  08 C0           or al, al
7C8A  75 24           jne 0x7cb0
7C8C  C4 7E F6        les di, ptr [bp - 0xa]
7C8F  26 8A 05        mov al, byte ptr es:[di]
7C92  30 E4           xor ah, ah
7C94  BA BF 00        mov dx, 0xbf
7C97  F7 E2           mul dx
7C99  C4 3E 17 A9     les di, ptr [0xa917]
7C9D  03 F8           add di, ax
7C9F  06              push es
7CA0  57              push di
7CA1  C4 7E 06        les di, ptr [bp + 6]
7CA4  26 8A 45 06     mov al, byte ptr es:[di + 6]
7CA8  30 E4           xor ah, ah
7CAA  50              push ax
7CAB  E8 DF 47        call 0xc48d
7CAE  EB 0F           jmp 0x7cbf
loc_7CB0:
7CB0  C4 7E F6        les di, ptr [bp - 0xa]
7CB3  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
7CB8  75 05           jne 0x7cbf
7CBA  C6 06 40 9B 01  mov byte ptr [0x9b40], 1
loc_7CBF:
7CBF  89 EC           mov sp, bp
7CC1  5D              pop bp
7CC2  CA 04 00        retf 4

; ---- routine 0791:7CC5  (found by: call)
sub_7CC5:
7CC5  55              push bp
7CC6  89 E5           mov bp, sp
7CC8  83 EC 04        sub sp, 4
7CCB  C4 7E 06        les di, ptr [bp + 6]
7CCE  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7CD2  BA 14 00        mov dx, 0x14
7CD5  F7 E2           mul dx
7CD7  C4 3E 1B A9     les di, ptr [0xa91b]
7CDB  03 F8           add di, ax
7CDD  89 7E FC        mov word ptr [bp - 4], di
7CE0  8C 46 FE        mov word ptr [bp - 2], es
7CE3  C4 7E FC        les di, ptr [bp - 4]
7CE6  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
7CEA  98              cwde
7CEB  03 46 0C        add ax, word ptr [bp + 0xc]
7CEE  89 46 0C        mov word ptr [bp + 0xc], ax
7CF1  8D 7E 0C        lea di, [bp + 0xc]
7CF4  16              push ss
7CF5  57              push di
7CF6  B8 01 00        mov ax, 1
7CF9  50              push ax
7CFA  B8 FF 00        mov ax, 0xff
7CFD  50              push ax
7CFE  9A 00 20 4B 21  call far 214B:2000
7D03  8A 46 0C        mov al, byte ptr [bp + 0xc]
7D06  C4 7E FC        les di, ptr [bp - 4]
7D09  26 88 45 0C     mov byte ptr es:[di + 0xc], al
7D0D  80 7E 0A 00     cmp byte ptr [bp + 0xa], 0
7D11  74 3D           je 0x7d50
7D13  C4 7E FC        les di, ptr [bp - 4]
7D16  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
7D1A  98              cwde
7D1B  99              cdq
7D1C  52              push dx
7D1D  50              push ax
7D1E  B8 20 00        mov ax, 0x20
7D21  31 D2           xor dx, dx
7D23  52              push dx
7D24  50              push ax
7D25  9A 1C 0D 4B 21  call far 214B:0D1C
7D2A  50              push ax
7D2B  C4 7E 06        les di, ptr [bp + 6]
7D2E  06              push es
7D2F  57              push di
7D30  0E              push cs
7D31  E8 7D AE        call 0x2bb1
7D34  30 E4           xor ah, ah
7D36  50              push ax
7D37  C4 7E 06        les di, ptr [bp + 6]
7D3A  06              push es
7D3B  57              push di
7D3C  0E              push cs
7D3D  E8 34 AC        call 0x2974
7D40  98              cwde
7D41  BA 14 00        mov dx, 0x14
7D44  F7 E2           mul dx
7D46  8B F8           mov di, ax
7D48  58              pop ax
7D49  03 F8           add di, ax
7D4B  58              pop ax
7D4C  88 85 07 9B     mov byte ptr [di - 0x64f9], al
loc_7D50:
7D50  89 EC           mov sp, bp
7D52  5D              pop bp
7D53  CA 08 00        retf 8

; ---- routine 0791:7D56  (found by: call)
sub_7D56:
7D56  55              push bp
7D57  89 E5           mov bp, sp
7D59  83 EC 04        sub sp, 4
7D5C  C4 7E 06        les di, ptr [bp + 6]
7D5F  06              push es
7D60  57              push di
7D61  0E              push cs
7D62  E8 F1 AB        call 0x2956
7D65  08 C0           or al, al
7D67  75 11           jne 0x7d7a
7D69  C4 7E 06        les di, ptr [bp + 6]
7D6C  06              push es
7D6D  57              push di
7D6E  0E              push cs
7D6F  E8 02 AC        call 0x2974
7D72  50              push ax
7D73  E8 CD FC        call 0x7a43
7D76  08 C0           or al, al
7D78  75 03           jne 0x7d7d
loc_7D7A:
7D7A  E9 DD 00        jmp 0x7e5a
loc_7D7D:
7D7D  B0 34           mov al, 0x34
7D7F  50              push ax
7D80  C4 7E 06        les di, ptr [bp + 6]
7D83  06              push es
7D84  57              push di
7D85  0E              push cs
7D86  E8 9F AD        call 0x2b28
7D89  C4 7E 06        les di, ptr [bp + 6]
7D8C  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7D90  BA 14 00        mov dx, 0x14
7D93  F7 E2           mul dx
7D95  C4 3E 1B A9     les di, ptr [0xa91b]
7D99  03 F8           add di, ax
7D9B  26 C6 45 0E 00  mov byte ptr es:[di + 0xe], 0
7DA0  C4 7E 06        les di, ptr [bp + 6]
7DA3  26 8A 45 06     mov al, byte ptr es:[di + 6]
7DA7  30 E4           xor ah, ah
7DA9  50              push ax
7DAA  E8 D4 FA        call 0x7881
7DAD  B8 FE FF        mov ax, 0xfffe
7DB0  50              push ax
7DB1  B0 01           mov al, 1
7DB3  50              push ax
7DB4  C4 7E 06        les di, ptr [bp + 6]
7DB7  06              push es
7DB8  57              push di
7DB9  0E              push cs
7DBA  E8 08 FF        call 0x7cc5
7DBD  83 3E 21 83 05  cmp word ptr [0x8321], 5
7DC2  73 04           jae 0x7dc8
7DC4  FF 06 21 83     inc word ptr [0x8321]
loc_7DC8:
7DC8  C4 7E 06        les di, ptr [bp + 6]
7DCB  06              push es
7DCC  57              push di
7DCD  0E              push cs
7DCE  E8 A3 AB        call 0x2974
7DD1  98              cwde
7DD2  BA 0A 00        mov dx, 0xa
7DD5  F7 E2           mul dx
7DD7  8B F8           mov di, ax
7DD9  FE 85 87 7B     inc byte ptr [di + 0x7b87]
7DDD  C4 7E 06        les di, ptr [bp + 6]
7DE0  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7DE4  BA 14 00        mov dx, 0x14
7DE7  F7 E2           mul dx
7DE9  C4 3E 1B A9     les di, ptr [0xa91b]
7DED  03 F8           add di, ax
7DEF  89 7E FC        mov word ptr [bp - 4], di
7DF2  8C 46 FE        mov word ptr [bp - 2], es
7DF5  C4 7E FC        les di, ptr [bp - 4]
7DF8  26 8A 05        mov al, byte ptr es:[di]
7DFB  30 E4           xor ah, ah
7DFD  50              push ax
7DFE  9A 77 0B 71 17  call far 1771:0B77
7E03  08 C0           or al, al
7E05  75 31           jne 0x7e38
7E07  C4 7E FC        les di, ptr [bp - 4]
7E0A  26 8A 05        mov al, byte ptr es:[di]
7E0D  30 E4           xor ah, ah
7E0F  BA BF 00        mov dx, 0xbf
7E12  F7 E2           mul dx
7E14  C4 3E 17 A9     les di, ptr [0xa917]
7E18  03 F8           add di, ax
7E1A  06              push es
7E1B  57              push di
7E1C  C4 7E 06        les di, ptr [bp + 6]
7E1F  26 8A 45 06     mov al, byte ptr es:[di + 6]
7E23  30 E4           xor ah, ah
7E25  50              push ax
7E26  C4 7E 06        les di, ptr [bp + 6]
7E29  06              push es
7E2A  57              push di
7E2B  0E              push cs
7E2C  E8 45 AB        call 0x2974
7E2F  50              push ax
7E30  B0 01           mov al, 1
7E32  50              push ax
7E33  E8 57 4A        call 0xc88d
7E36  EB 22           jmp 0x7e5a
loc_7E38:
7E38  C4 7E FC        les di, ptr [bp - 4]
7E3B  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
7E40  74 13           je 0x7e55
7E42  C4 7E 06        les di, ptr [bp + 6]
7E45  06              push es
7E46  57              push di
7E47  0E              push cs
7E48  E8 29 AB        call 0x2974
7E4B  98              cwde
7E4C  8B F8           mov di, ax
7E4E  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
7E53  76 05           jbe 0x7e5a
loc_7E55:
7E55  C6 06 40 9B 01  mov byte ptr [0x9b40], 1
loc_7E5A:
7E5A  89 EC           mov sp, bp
7E5C  5D              pop bp
7E5D  CA 04 00        retf 4

; ---- routine 0791:7E60  (found by: call)
sub_7E60:
7E60  55              push bp
7E61  89 E5           mov bp, sp
7E63  83 EC 02        sub sp, 2
7E66  C6 06 25 83 00  mov byte ptr [0x8325], 0
7E6B  B8 04 00        mov ax, 4
7E6E  50              push ax
7E6F  E8 CF 85        call 0x441
7E72  C7 46 FE 01 00  mov word ptr [bp - 2], 1
7E77  EB 03           jmp 0x7e7c
loc_7E79:
7E79  FF 46 FE        inc word ptr [bp - 2]
loc_7E7C:
7E7C  A0 0B 83        mov al, byte ptr [0x830b]
7E7F  30 E4           xor ah, ah
7E81  BA 16 00        mov dx, 0x16
7E84  F7 E2           mul dx
7E86  8B F8           mov di, ax
7E88  81 C7 E8 80     add di, 0x80e8
7E8C  1E              push ds
7E8D  57              push di
7E8E  0E              push cs
7E8F  E8 A5 06        call 0x8537
7E92  C4 3E 23 A9     les di, ptr [0xa923]
7E96  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
7E9A  30 E4           xor ah, ah
7E9C  B9 02 00        mov cx, 2
7E9F  D3 E0           shl ax, cl
7EA1  50              push ax
7EA2  E8 80 85        call 0x425
7EA5  A0 0C 83        mov al, byte ptr [0x830c]
7EA8  30 E4           xor ah, ah
7EAA  BA 16 00        mov dx, 0x16
7EAD  F7 E2           mul dx
7EAF  8B F8           mov di, ax
7EB1  81 C7 E8 80     add di, 0x80e8
7EB5  1E              push ds
7EB6  57              push di
7EB7  0E              push cs
7EB8  E8 7C 06        call 0x8537
7EBB  C4 3E 23 A9     les di, ptr [0xa923]
7EBF  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
7EC3  30 E4           xor ah, ah
7EC5  B9 02 00        mov cx, 2
7EC8  D3 E0           shl ax, cl
7ECA  50              push ax
7ECB  E8 57 85        call 0x425
7ECE  8A 46 04        mov al, byte ptr [bp + 4]
7ED1  50              push ax
7ED2  BF EE 82        mov di, 0x82ee
7ED5  1E              push ds
7ED6  57              push di
7ED7  0E              push cs
7ED8  E8 3E 12        call 0x9119
7EDB  83 7E FE 0A     cmp word ptr [bp - 2], 0xa
7EDF  75 98           jne 0x7e79
7EE1  E8 DE A7        call 0x26c2
7EE4  C6 06 0A 83 00  mov byte ptr [0x830a], 0
7EE9  89 EC           mov sp, bp
7EEB  5D              pop bp
7EEC  C2 02 00        ret 2

; ---- routine 0791:7EEF  (found by: call)
sub_7EEF:
7EEF  55              push bp
7EF0  89 E5           mov bp, sp
7EF2  83 EC 04        sub sp, 4
7EF5  A0 0C 83        mov al, byte ptr [0x830c]
7EF8  30 E4           xor ah, ah
7EFA  BA 16 00        mov dx, 0x16
7EFD  F7 E2           mul dx
7EFF  8B F8           mov di, ax
7F01  81 C7 E8 80     add di, 0x80e8
7F05  89 7E FC        mov word ptr [bp - 4], di
7F08  8C 5E FE        mov word ptr [bp - 2], ds
7F0B  E8 0C A7        call 0x261a
7F0E  3D 04 00        cmp ax, 4
7F11  7D 3C           jge 0x7f4f
7F13  B8 05 00        mov ax, 5
7F16  50              push ax
7F17  C4 7E FC        les di, ptr [bp - 4]
7F1A  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
7F1E  BA 14 00        mov dx, 0x14
7F21  F7 E2           mul dx
7F23  C4 3E 1B A9     les di, ptr [0xa91b]
7F27  03 F8           add di, ax
7F29  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
7F2D  30 E4           xor ah, ah
7F2F  50              push ax
7F30  9A 57 0C 4B 21  call far 214B:0C57
7F35  08 C0           or al, al
7F37  74 0B           je 0x7f44
7F39  C4 7E FC        les di, ptr [bp - 4]
7F3C  06              push es
7F3D  57              push di
7F3E  0E              push cs
7F3F  E8 35 FC        call 0x7b77
7F42  EB 09           jmp 0x7f4d
loc_7F44:
7F44  C4 7E FC        les di, ptr [bp - 4]
7F47  06              push es
7F48  57              push di
7F49  0E              push cs
7F4A  E8 40 FA        call 0x798d
loc_7F4D:
7F4D  EB 16           jmp 0x7f65
loc_7F4F:
7F4F  B8 20 00        mov ax, 0x20
7F52  50              push ax
7F53  9A D0 06 4B 21  call far 214B:06D0
7F58  08 C0           or al, al
7F5A  74 09           je 0x7f65
7F5C  C4 7E FC        les di, ptr [bp - 4]
7F5F  06              push es
7F60  57              push di
7F61  0E              push cs
7F62  E8 12 FC        call 0x7b77
loc_7F65:
7F65  E8 B2 A6        call 0x261a
7F68  3D 01 00        cmp ax, 1
7F6B  75 5E           jne 0x7fcb
7F6D  A0 0C 83        mov al, byte ptr [0x830c]
7F70  30 E4           xor ah, ah
7F72  BA 16 00        mov dx, 0x16
7F75  F7 E2           mul dx
7F77  8B F8           mov di, ax
7F79  FF B5 F5 80     push word ptr [di - 0x7f0b]
7F7D  9A FB 2F 71 17  call far 1771:2FFB
7F82  50              push ax
7F83  A0 0B 83        mov al, byte ptr [0x830b]
7F86  30 E4           xor ah, ah
7F88  BA 16 00        mov dx, 0x16
7F8B  F7 E2           mul dx
7F8D  8B F8           mov di, ax
7F8F  FF B5 F5 80     push word ptr [di - 0x7f0b]
7F93  9A FB 2F 71 17  call far 1771:2FFB
7F98  5A              pop dx
7F99  3A C2           cmp al, dl
7F9B  76 18           jbe 0x7fb5
7F9D  A0 0C 83        mov al, byte ptr [0x830c]
7FA0  30 E4           xor ah, ah
7FA2  BA 16 00        mov dx, 0x16
7FA5  F7 E2           mul dx
7FA7  8B F8           mov di, ax
7FA9  81 C7 E8 80     add di, 0x80e8
7FAD  1E              push ds
7FAE  57              push di
7FAF  0E              push cs
7FB0  E8 A3 FD        call 0x7d56
7FB3  EB 16           jmp 0x7fcb
loc_7FB5:
7FB5  A0 0B 83        mov al, byte ptr [0x830b]
7FB8  30 E4           xor ah, ah
7FBA  BA 16 00        mov dx, 0x16
7FBD  F7 E2           mul dx
7FBF  8B F8           mov di, ax
7FC1  81 C7 E8 80     add di, 0x80e8
7FC5  1E              push ds
7FC6  57              push di
7FC7  0E              push cs
7FC8  E8 8B FD        call 0x7d56
loc_7FCB:
7FCB  89 EC           mov sp, bp
7FCD  5D              pop bp
7FCE  C3              ret

; ---- routine 0791:7FCF  (found by: call)
sub_7FCF:
7FCF  55              push bp
7FD0  89 E5           mov bp, sp
7FD2  9A 25 06 4B 21  call far 214B:0625
7FD7  80 7E 06 00     cmp byte ptr [bp + 6], 0
7FDB  75 11           jne 0x7fee
7FDD  BF 30 5B        mov di, 0x5b30
7FE0  1E              push ds
7FE1  57              push di
7FE2  BF 6E A9        mov di, 0xa96e
7FE5  1E              push ds
7FE6  57              push di
7FE7  9A 29 03 4B 21  call far 214B:0329
7FEC  EB 28           jmp 0x8016
loc_7FEE:
7FEE  BF 66 5B        mov di, 0x5b66
7FF1  1E              push ds
7FF2  57              push di
7FF3  BF 6E A9        mov di, 0xa96e
7FF6  1E              push ds
7FF7  57              push di
7FF8  9A 29 03 4B 21  call far 214B:0329
7FFD  8A 46 04        mov al, byte ptr [bp + 4]
8000  98              cwde
8001  8B F8           mov di, ax
8003  D1 E7           shl di, 1
8005  FF B5 34 9B     push word ptr [di - 0x64cc]
8009  B8 19 00        mov ax, 0x19
800C  50              push ax
800D  B8 01 00        mov ax, 1
8010  50              push ax
8011  9A 58 0F 71 17  call far 1771:0F58
loc_8016:
8016  C4 3E 6E A9     les di, ptr [0xa96e]
801A  81 C7 00 0F     add di, 0xf00
801E  06              push es
801F  57              push di
8020  C4 3E 6A A9     les di, ptr [0xa96a]
8024  81 C7 00 0F     add di, 0xf00
8028  06              push es
8029  57              push di
802A  B8 A0 00        mov ax, 0xa0
802D  50              push ax
802E  9A 3C 00 4B 21  call far 214B:003C
8033  8A 46 06        mov al, byte ptr [bp + 6]
8036  98              cwde
8037  8B F8           mov di, ax
8039  D1 E7           shl di, 1
803B  FF B5 7C 08     push word ptr [di + 0x87c]
803F  E8 EC 4B        call 0xcc2e
8042  9A 23 07 4B 21  call far 214B:0723
8047  08 C0           or al, al
8049  74 07           je 0x8052
804B  9A DD 08 4B 21  call far 214B:08DD
8050  EB 05           jmp 0x8057
loc_8052:
8052  C6 06 77 A9 1B  mov byte ptr [0xa977], 0x1b
loc_8057:
8057  9A 43 06 4B 21  call far 214B:0643
805C  89 EC           mov sp, bp
805E  5D              pop bp
805F  C2 04 00        ret 4

; ---- routine 0791:8062  (found by: call)
sub_8062:
8062  55              push bp
8063  89 E5           mov bp, sp
8065  83 EC 0C        sub sp, 0xc
8068  C6 46 FF 00     mov byte ptr [bp - 1], 0
806C  EB 03           jmp 0x8071
loc_806E:
806E  FE 46 FF        inc byte ptr [bp - 1]
loc_8071:
8071  8A 46 FF        mov al, byte ptr [bp - 1]
8074  98              cwde
8075  8B F8           mov di, ax
8077  D1 E7           shl di, 1
8079  FF B5 34 9B     push word ptr [di - 0x64cc]
807D  9A 77 0B 71 17  call far 1771:0B77
8082  08 C0           or al, al
8084  75 03           jne 0x8089
8086  E9 82 00        jmp 0x810b
loc_8089:
8089  8A 46 FF        mov al, byte ptr [bp - 1]
808C  98              cwde
808D  8B F8           mov di, ax
808F  8A 85 68 06     mov al, byte ptr [di + 0x668]
8093  30 E4           xor ah, ah
8095  40              inc ax
8096  BA 16 00        mov dx, 0x16
8099  F7 E2           mul dx
809B  8B F8           mov di, ax
809D  FF B5 F5 80     push word ptr [di - 0x7f0b]
80A1  9A 16 32 71 17  call far 1771:3216
80A6  88 46 FC        mov byte ptr [bp - 4], al
80A9  80 3E 40 9B 00  cmp byte ptr [0x9b40], 0
80AE  74 58           je 0x8108
80B0  80 7E FC 00     cmp byte ptr [bp - 4], 0
80B4  75 18           jne 0x80ce
80B6  A1 1B 83        mov ax, word ptr [0x831b]
80B9  03 06 21 83     add ax, word ptr [0x8321]
80BD  09 C0           or ax, ax
80BF  76 47           jbe 0x8108
80C1  8A 46 FF        mov al, byte ptr [bp - 1]
80C4  98              cwde
80C5  8B F8           mov di, ax
80C7  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
80CC  76 3A           jbe 0x8108
loc_80CE:
80CE  8A 46 FF        mov al, byte ptr [bp - 1]
80D1  98              cwde
80D2  8B F8           mov di, ax
80D4  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
80D9  76 05           jbe 0x80e0
80DB  C6 06 41 9B 01  mov byte ptr [0x9b41], 1
loc_80E0:
80E0  9A 8D 1E 4B 21  call far 214B:1E8D
80E5  8A 46 FC        mov al, byte ptr [bp - 4]
80E8  50              push ax
80E9  8A 46 FF        mov al, byte ptr [bp - 1]
80EC  50              push ax
80ED  E8 DF FE        call 0x7fcf
80F0  80 3E 77 A9 1B  cmp byte ptr [0xa977], 0x1b
80F5  75 06           jne 0x80fd
80F7  80 7E FC 00     cmp byte ptr [bp - 4], 0
80FB  74 06           je 0x8103
loc_80FD:
80FD  B0 01           mov al, 1
80FF  50              push ax
8100  E8 87 6C        call 0xed8a
loc_8103:
8103  C6 06 41 9B 00  mov byte ptr [0x9b41], 0
loc_8108:
8108  E9 EE 00        jmp 0x81f9
loc_810B:
810B  8A 46 FF        mov al, byte ptr [bp - 1]
810E  98              cwde
810F  8B F8           mov di, ax
8111  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
8116  77 03           ja 0x811b
8118  E9 DE 00        jmp 0x81f9
loc_811B:
811B  C7 46 FD 0B 00  mov word ptr [bp - 3], 0xb
8120  EB 03           jmp 0x8125
loc_8122:
8122  FF 4E FD        dec word ptr [bp - 3]
loc_8125:
8125  8A 46 FF        mov al, byte ptr [bp - 1]
8128  98              cwde
8129  8B F8           mov di, ax
812B  8A 85 68 06     mov al, byte ptr [di + 0x668]
812F  30 E4           xor ah, ah
8131  03 46 FD        add ax, word ptr [bp - 3]
8134  BA 16 00        mov dx, 0x16
8137  F7 E2           mul dx
8139  8B F8           mov di, ax
813B  81 C7 E8 80     add di, 0x80e8
813F  89 7E F8        mov word ptr [bp - 8], di
8142  8C 5E FA        mov word ptr [bp - 6], ds
8145  C4 7E F8        les di, ptr [bp - 8]
8148  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
814C  BA 14 00        mov dx, 0x14
814F  F7 E2           mul dx
8151  C4 3E 1B A9     les di, ptr [0xa91b]
8155  03 F8           add di, ax
8157  89 7E F4        mov word ptr [bp - 0xc], di
815A  8C 46 F6        mov word ptr [bp - 0xa], es
815D  B8 06 00        mov ax, 6
8160  50              push ax
8161  C4 7E F4        les di, ptr [bp - 0xc]
8164  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
8168  30 E4           xor ah, ah
816A  50              push ax
816B  9A 57 0C 4B 21  call far 214B:0C57
8170  08 C0           or al, al
8172  75 7C           jne 0x81f0
8174  C4 7E F4        les di, ptr [bp - 0xc]
8177  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
817C  7E 72           jle 0x81f0
817E  83 3E 1B 83 01  cmp word ptr [0x831b], 1
8183  76 6B           jbe 0x81f0
8185  83 7E FD 01     cmp word ptr [bp - 3], 1
8189  76 65           jbe 0x81f0
818B  83 3E 1B 83 23  cmp word ptr [0x831b], 0x23
8190  73 5E           jae 0x81f0
8192  B8 5A 00        mov ax, 0x5a
8195  2B 06 1B 83     sub ax, word ptr [0x831b]
8199  31 D2           xor dx, dx
819B  8B C8           mov cx, ax
819D  8B DA           mov bx, dx
819F  C4 7E F4        les di, ptr [bp - 0xc]
81A2  26 8B 45 12     mov ax, word ptr es:[di + 0x12]
81A6  99              cdq
81A7  3B D3           cmp dx, bx
81A9  7C 06           jl 0x81b1
81AB  7F 43           jg 0x81f0
81AD  3B C1           cmp ax, cx
81AF  73 3F           jae 0x81f0
loc_81B1:
81B1  8A 46 FF        mov al, byte ptr [bp - 1]
81B4  98              cwde
81B5  8B F8           mov di, ax
81B7  D1 E7           shl di, 1
81B9  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
81BD  BA BF 00        mov dx, 0xbf
81C0  F7 E2           mul dx
81C2  C4 3E 17 A9     les di, ptr [0xa917]
81C6  03 F8           add di, ax
81C8  06              push es
81C9  57              push di
81CA  C4 7E F8        les di, ptr [bp - 8]
81CD  26 8A 45 06     mov al, byte ptr es:[di + 6]
81D1  30 E4           xor ah, ah
81D3  50              push ax
81D4  8A 46 FF        mov al, byte ptr [bp - 1]
81D7  50              push ax
81D8  B0 00           mov al, 0
81DA  50              push ax
81DB  E8 AF 46        call 0xc88d
81DE  8A 46 FF        mov al, byte ptr [bp - 1]
81E1  98              cwde
81E2  8B F8           mov di, ax
81E4  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
81E9  75 05           jne 0x81f0
81EB  C7 46 FD 01 00  mov word ptr [bp - 3], 1
loc_81F0:
81F0  83 7E FD 01     cmp word ptr [bp - 3], 1
81F4  74 03           je 0x81f9
81F6  E9 29 FF        jmp 0x8122
loc_81F9:
81F9  80 7E FF 01     cmp byte ptr [bp - 1], 1
81FD  74 03           je 0x8202
81FF  E9 6C FE        jmp 0x806e
loc_8202:
8202  89 EC           mov sp, bp
8204  5D              pop bp
8205  C3              ret

; ---- routine 0791:8206  (found by: call)
sub_8206:
8206  55              push bp
8207  89 E5           mov bp, sp
8209  83 EC 06        sub sp, 6
820C  8A 46 04        mov al, byte ptr [bp + 4]
820F  A2 0C 83        mov byte ptr [0x830c], al
8212  8A 46 04        mov al, byte ptr [bp + 4]
8215  A2 0D 83        mov byte ptr [0x830d], al
8218  A0 0C 83        mov al, byte ptr [0x830c]
821B  30 E4           xor ah, ah
821D  BA 16 00        mov dx, 0x16
8220  F7 E2           mul dx
8222  8B F8           mov di, ax
8224  81 C7 E8 80     add di, 0x80e8
8228  89 7E FB        mov word ptr [bp - 5], di
822B  8C 5E FD        mov word ptr [bp - 3], ds
822E  C4 7E FB        les di, ptr [bp - 5]
8231  26 FF 35        push word ptr es:[di]
8234  C4 7E FB        les di, ptr [bp - 5]
8237  06              push es
8238  57              push di
8239  0E              push cs
823A  E8 7B AC        call 0x2eb8
823D  08 C0           or al, al
823F  74 0C           je 0x824d
8241  9A FA 06 4B 21  call far 214B:06FA
8246  08 C0           or al, al
8248  74 03           je 0x824d
824A  E9 98 00        jmp 0x82e5
loc_824D:
824D  B0 37           mov al, 0x37
824F  50              push ax
8250  E8 50 A8        call 0x2aa3
8253  B0 35           mov al, 0x35
8255  50              push ax
8256  E8 7B A8        call 0x2ad4
8259  B0 01           mov al, 1
825B  50              push ax
825C  E8 01 FC        call 0x7e60
825F  80 3E 0C 83 0C  cmp byte ptr [0x830c], 0xc
8264  72 04           jb 0x826a
8266  B0 00           mov al, 0
8268  EB 02           jmp 0x826c
loc_826A:
826A  B0 01           mov al, 1
loc_826C:
826C  98              cwde
826D  BA 0A 00        mov dx, 0xa
8270  F7 E2           mul dx
8272  8B F8           mov di, ax
8274  FE 85 84 7B     inc byte ptr [di + 0x7b84]
8278  FF 36 F6 82     push word ptr [0x82f6]
827C  A0 0C 83        mov al, byte ptr [0x830c]
827F  30 E4           xor ah, ah
8281  BA 16 00        mov dx, 0x16
8284  F7 E2           mul dx
8286  8B F8           mov di, ax
8288  81 C7 E8 80     add di, 0x80e8
828C  1E              push ds
828D  57              push di
828E  0E              push cs
828F  E8 26 AC        call 0x2eb8
8292  88 46 FF        mov byte ptr [bp - 1], al
8295  E8 57 FC        call 0x7eef
8298  80 7E FF 00     cmp byte ptr [bp - 1], 0
829C  74 44           je 0x82e2
829E  A0 0C 83        mov al, byte ptr [0x830c]
82A1  30 E4           xor ah, ah
82A3  BA 16 00        mov dx, 0x16
82A6  F7 E2           mul dx
82A8  8B F8           mov di, ax
82AA  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
82AE  BA 14 00        mov dx, 0x14
82B1  F7 E2           mul dx
82B3  C4 3E 1B A9     les di, ptr [0xa91b]
82B7  03 F8           add di, ax
82B9  26 8A 05        mov al, byte ptr es:[di]
82BC  30 E4           xor ah, ah
82BE  50              push ax
82BF  9A 77 0B 71 17  call far 1771:0B77
82C4  08 C0           or al, al
82C6  75 15           jne 0x82dd
82C8  A0 0C 83        mov al, byte ptr [0x830c]
82CB  30 E4           xor ah, ah
82CD  BA 16 00        mov dx, 0x16
82D0  F7 E2           mul dx
82D2  8B F8           mov di, ax
82D4  FF B5 F5 80     push word ptr [di - 0x7f0b]
82D8  9A CD 33 71 17  call far 1771:33CD
loc_82DD:
82DD  E8 EF EB        call 0x6ecf
82E0  EB 03           jmp 0x82e5
loc_82E2:
82E2  E8 D1 EC        call 0x6fb6
loc_82E5:
82E5  89 EC           mov sp, bp
82E7  5D              pop bp
82E8  C2 02 00        ret 2

