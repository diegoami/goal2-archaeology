; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 5 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:2A15  (found by: call)
sub_2A15:
2A15  55              push bp
2A16  89 E5           mov bp, sp
2A18  80 3E 0B 83 00  cmp byte ptr [0x830b], 0
2A1D  76 4A           jbe 0x2a69
loc_2A1F:
2A1F  A0 0B 83        mov al, byte ptr [0x830b]
2A22  30 E4           xor ah, ah
2A24  BA 16 00        mov dx, 0x16
2A27  F7 E2           mul dx
2A29  8B F8           mov di, ax
2A2B  81 C7 E8 80     add di, 0x80e8
2A2F  1E              push ds
2A30  57              push di
2A31  0E              push cs
2A32  E8 21 FF        call 0x2956
2A35  08 C0           or al, al
2A37  74 30           je 0x2a69
2A39  BF 0B 83        mov di, 0x830b
2A3C  1E              push ds
2A3D  57              push di
2A3E  E8 55 FF        call 0x2996
2A41  98              cwde
2A42  8B F8           mov di, ax
2A44  8A 85 68 06     mov al, byte ptr [di + 0x668]
2A48  30 E4           xor ah, ah
2A4A  05 02 00        add ax, 2
2A4D  50              push ax
2A4E  E8 45 FF        call 0x2996
2A51  98              cwde
2A52  8B F8           mov di, ax
2A54  8A 85 68 06     mov al, byte ptr [di + 0x668]
2A58  30 E4           xor ah, ah
2A5A  05 0B 00        add ax, 0xb
2A5D  50              push ax
2A5E  B8 01 00        mov ax, 1
2A61  50              push ax
2A62  9A 6F 1D 4B 21  call far 214B:1D6F
2A67  EB B6           jmp 0x2a1f
loc_2A69:
2A69  89 EC           mov sp, bp
2A6B  5D              pop bp
2A6C  C3              ret

; ---- routine 0791:2A6D  (found by: call)
sub_2A6D:
2A6D  55              push bp
2A6E  89 E5           mov bp, sp
2A70  83 EC 02        sub sp, 2
2A73  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
2A78  76 1D           jbe 0x2a97
2A7A  A0 0C 83        mov al, byte ptr [0x830c]
2A7D  30 E4           xor ah, ah
2A7F  BA 16 00        mov dx, 0x16
2A82  F7 E2           mul dx
2A84  8B F8           mov di, ax
2A86  81 C7 E8 80     add di, 0x80e8
2A8A  1E              push ds
2A8B  57              push di
2A8C  0E              push cs
2A8D  E8 21 01        call 0x2bb1
2A90  30 E4           xor ah, ah
2A92  89 46 FE        mov word ptr [bp - 2], ax
2A95  EB 05           jmp 0x2a9c
loc_2A97:
2A97  31 C0           xor ax, ax
2A99  89 46 FE        mov word ptr [bp - 2], ax
loc_2A9C:
2A9C  8B 46 FE        mov ax, word ptr [bp - 2]
2A9F  89 EC           mov sp, bp
2AA1  5D              pop bp
2AA2  C3              ret

; ---- routine 0791:2AA3  (found by: call)
sub_2AA3:
2AA3  55              push bp
2AA4  89 E5           mov bp, sp
2AA6  E8 ED FE        call 0x2996
2AA9  50              push ax
2AAA  A0 0B 83        mov al, byte ptr [0x830b]
2AAD  30 E4           xor ah, ah
2AAF  BA 16 00        mov dx, 0x16
2AB2  F7 E2           mul dx
2AB4  8B F8           mov di, ax
2AB6  81 C7 E8 80     add di, 0x80e8
2ABA  1E              push ds
2ABB  57              push di
2ABC  0E              push cs
2ABD  E8 F1 00        call 0x2bb1
2AC0  30 E4           xor ah, ah
2AC2  50              push ax
2AC3  E8 A7 FF        call 0x2a6d
2AC6  50              push ax
2AC7  8A 46 04        mov al, byte ptr [bp + 4]
2ACA  50              push ax
2ACB  E8 E7 F3        call 0x1eb5
2ACE  89 EC           mov sp, bp
2AD0  5D              pop bp
2AD1  C2 02 00        ret 2

; ---- routine 0791:2AD4  (found by: call)
sub_2AD4:
2AD4  55              push bp
2AD5  89 E5           mov bp, sp
2AD7  80 3E 0C 83 0C  cmp byte ptr [0x830c], 0xc
2ADC  72 04           jb 0x2ae2
2ADE  B0 00           mov al, 0
2AE0  EB 02           jmp 0x2ae4
loc_2AE2:
2AE2  B0 01           mov al, 1
loc_2AE4:
2AE4  50              push ax
2AE5  E8 85 FF        call 0x2a6d
2AE8  50              push ax
2AE9  A0 0B 83        mov al, byte ptr [0x830b]
2AEC  30 E4           xor ah, ah
2AEE  BA 16 00        mov dx, 0x16
2AF1  F7 E2           mul dx
2AF3  8B F8           mov di, ax
2AF5  81 C7 E8 80     add di, 0x80e8
2AF9  1E              push ds
2AFA  57              push di
2AFB  0E              push cs
2AFC  E8 B2 00        call 0x2bb1
2AFF  30 E4           xor ah, ah
2B01  50              push ax
2B02  8A 46 04        mov al, byte ptr [bp + 4]
2B05  50              push ax
2B06  E8 AC F3        call 0x1eb5
2B09  89 EC           mov sp, bp
2B0B  5D              pop bp
2B0C  C2 02 00        ret 2

; ---- routine 0791:2B0F  (found by: call)
sub_2B0F:
2B0F  55              push bp
2B10  89 E5           mov bp, sp
2B12  B0 01           mov al, 1
2B14  50              push ax
2B15  31 C0           xor ax, ax
2B17  50              push ax
2B18  31 C0           xor ax, ax
2B1A  50              push ax
2B1B  8A 46 04        mov al, byte ptr [bp + 4]
2B1E  50              push ax
2B1F  E8 93 F3        call 0x1eb5
2B22  89 EC           mov sp, bp
2B24  5D              pop bp
2B25  C2 02 00        ret 2

; ---- routine 0791:2B28  (found by: call)
sub_2B28:
2B28  55              push bp
2B29  89 E5           mov bp, sp
2B2B  C4 7E 06        les di, ptr [bp + 6]
2B2E  06              push es
2B2F  57              push di
2B30  0E              push cs
2B31  E8 40 FE        call 0x2974
2B34  50              push ax
2B35  C4 7E 06        les di, ptr [bp + 6]
2B38  06              push es
2B39  57              push di
2B3A  0E              push cs
2B3B  E8 73 00        call 0x2bb1
2B3E  30 E4           xor ah, ah
2B40  50              push ax
2B41  31 C0           xor ax, ax
2B43  50              push ax
2B44  8A 46 0A        mov al, byte ptr [bp + 0xa]
2B47  50              push ax
2B48  E8 6A F3        call 0x1eb5
2B4B  89 EC           mov sp, bp
2B4D  5D              pop bp
2B4E  CA 06 00        retf 6

; ---- routine 0791:2B51  (found by: call)
sub_2B51:
2B51  55              push bp
2B52  89 E5           mov bp, sp
2B54  83 EC 02        sub sp, 2
2B57  E8 3C FE        call 0x2996
2B5A  50              push ax
2B5B  C4 7E 06        les di, ptr [bp + 6]
2B5E  06              push es
2B5F  57              push di
2B60  0E              push cs
2B61  E8 10 FE        call 0x2974
2B64  5A              pop dx
2B65  3A C2           cmp al, dl
2B67  74 04           je 0x2b6d
2B69  B0 00           mov al, 0
2B6B  EB 02           jmp 0x2b6f
loc_2B6D:
2B6D  B0 01           mov al, 1
loc_2B6F:
2B6F  88 46 FF        mov byte ptr [bp - 1], al
2B72  8A 46 FF        mov al, byte ptr [bp - 1]
2B75  89 EC           mov sp, bp
2B77  5D              pop bp
2B78  CA 04 00        retf 4

; ---- routine 0791:2B7B  (found by: call)
sub_2B7B:
2B7B  55              push bp
2B7C  89 E5           mov bp, sp
2B7E  83 EC 02        sub sp, 2
2B81  C4 7E 06        les di, ptr [bp + 6]
2B84  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
2B88  BA 14 00        mov dx, 0x14
2B8B  F7 E2           mul dx
2B8D  C4 3E 1B A9     les di, ptr [0xa91b]
2B91  03 F8           add di, ax
2B93  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
2B97  98              cwde
2B98  8B D0           mov dx, ax
2B9A  B8 21 00        mov ax, 0x21
2B9D  2B C2           sub ax, dx
2B9F  50              push ax
2BA0  9A D0 06 4B 21  call far 214B:06D0
2BA5  88 46 FF        mov byte ptr [bp - 1], al
2BA8  8A 46 FF        mov al, byte ptr [bp - 1]
2BAB  89 EC           mov sp, bp
2BAD  5D              pop bp
2BAE  CA 04 00        retf 4

; ---- routine 0791:2BB1  (found by: call)
sub_2BB1:
2BB1  55              push bp
2BB2  89 E5           mov bp, sp
2BB4  83 EC 02        sub sp, 2
2BB7  C4 7E 06        les di, ptr [bp + 6]
2BBA  26 80 7D 06 0B  cmp byte ptr es:[di + 6], 0xb
2BBF  76 11           jbe 0x2bd2
2BC1  C4 7E 06        les di, ptr [bp + 6]
2BC4  26 8A 45 06     mov al, byte ptr es:[di + 6]
2BC8  30 E4           xor ah, ah
2BCA  2D 0B 00        sub ax, 0xb
2BCD  88 46 FF        mov byte ptr [bp - 1], al
2BD0  EB 0A           jmp 0x2bdc
loc_2BD2:
2BD2  C4 7E 06        les di, ptr [bp + 6]
2BD5  26 8A 45 06     mov al, byte ptr es:[di + 6]
2BD9  88 46 FF        mov byte ptr [bp - 1], al
loc_2BDC:
2BDC  8A 46 FF        mov al, byte ptr [bp - 1]
2BDF  89 EC           mov sp, bp
2BE1  5D              pop bp
2BE2  CA 04 00        retf 4

; ---- routine 0791:2BE5  (found by: call)
sub_2BE5:
2BE5  55              push bp
2BE6  89 E5           mov bp, sp
2BE8  83 EC 02        sub sp, 2
2BEB  A0 19 83        mov al, byte ptr [0x8319]
2BEE  98              cwde
2BEF  99              cdq
2BF0  8B C8           mov cx, ax
2BF2  8B DA           mov bx, dx
2BF4  A1 1B 83        mov ax, word ptr [0x831b]
2BF7  31 D2           xor dx, dx
2BF9  3B D3           cmp dx, bx
2BFB  7F 0A           jg 0x2c07
2BFD  7C 04           jl 0x2c03
2BFF  3B C1           cmp ax, cx
2C01  77 04           ja 0x2c07
loc_2C03:
2C03  B0 00           mov al, 0
2C05  EB 02           jmp 0x2c09
loc_2C07:
2C07  B0 01           mov al, 1
loc_2C09:
2C09  50              push ax
2C0A  C4 7E 06        les di, ptr [bp + 6]
2C0D  06              push es
2C0E  57              push di
2C0F  0E              push cs
2C10  E8 61 FD        call 0x2974
2C13  5A              pop dx
2C14  32 C2           xor al, dl
2C16  98              cwde
2C17  8B F8           mov di, ax
2C19  8A 85 20 79     mov al, byte ptr [di + 0x7920]
2C1D  88 46 FF        mov byte ptr [bp - 1], al
2C20  8A 46 FF        mov al, byte ptr [bp - 1]
2C23  89 EC           mov sp, bp
2C25  5D              pop bp
2C26  CA 04 00        retf 4

; ---- routine 0791:2C29  (found by: call)
sub_2C29:
2C29  55              push bp
2C2A  89 E5           mov bp, sp
2C2C  83 EC 02        sub sp, 2
2C2F  A0 0B 83        mov al, byte ptr [0x830b]
2C32  C4 7E 06        les di, ptr [bp + 6]
2C35  26 3A 45 06     cmp al, byte ptr es:[di + 6]
2C39  75 07           jne 0x2c42
2C3B  80 3E 02 83 00  cmp byte ptr [0x8302], 0
2C40  74 04           je 0x2c46
loc_2C42:
2C42  B0 00           mov al, 0
2C44  EB 02           jmp 0x2c48
loc_2C46:
2C46  B0 01           mov al, 1
loc_2C48:
2C48  88 46 FF        mov byte ptr [bp - 1], al
2C4B  8A 46 FF        mov al, byte ptr [bp - 1]
2C4E  89 EC           mov sp, bp
2C50  5D              pop bp
2C51  CA 04 00        retf 4

; ---- routine 0791:2C54  (found by: call)
sub_2C54:
2C54  55              push bp
2C55  89 E5           mov bp, sp
2C57  83 EC 02        sub sp, 2
2C5A  C4 7E 06        les di, ptr [bp + 6]
2C5D  06              push es
2C5E  57              push di
2C5F  0E              push cs
2C60  E8 82 FF        call 0x2be5
2C63  98              cwde
2C64  8B D0           mov dx, ax
2C66  C4 7E 06        les di, ptr [bp + 6]
2C69  26 8A 45 01     mov al, byte ptr es:[di + 1]
2C6D  98              cwde
2C6E  F7 EA           imul dx
2C70  09 C0           or ax, ax
2C72  7C 04           jl 0x2c78
2C74  B0 00           mov al, 0
2C76  EB 02           jmp 0x2c7a
loc_2C78:
2C78  B0 01           mov al, 1
loc_2C7A:
2C7A  88 46 FF        mov byte ptr [bp - 1], al
2C7D  8A 46 FF        mov al, byte ptr [bp - 1]
2C80  89 EC           mov sp, bp
2C82  5D              pop bp
2C83  CA 04 00        retf 4

; ---- routine 0791:2C86  (found by: call)
sub_2C86:
2C86  55              push bp
2C87  89 E5           mov bp, sp
2C89  83 EC 02        sub sp, 2
2C8C  C4 7E 06        les di, ptr [bp + 6]
2C8F  06              push es
2C90  57              push di
2C91  0E              push cs
2C92  E8 50 FF        call 0x2be5
2C95  98              cwde
2C96  8B D0           mov dx, ax
2C98  8A 46 0B        mov al, byte ptr [bp + 0xb]
2C9B  98              cwde
2C9C  F7 EA           imul dx
2C9E  88 46 0B        mov byte ptr [bp + 0xb], al
2CA1  C4 7E 06        les di, ptr [bp + 6]
2CA4  06              push es
2CA5  57              push di
2CA6  0E              push cs
2CA7  E8 3B FF        call 0x2be5
2CAA  98              cwde
2CAB  8B D0           mov dx, ax
2CAD  8A 46 0A        mov al, byte ptr [bp + 0xa]
2CB0  98              cwde
2CB1  F7 EA           imul dx
2CB3  88 46 0A        mov byte ptr [bp + 0xa], al
2CB6  8B 46 0A        mov ax, word ptr [bp + 0xa]
2CB9  89 46 FE        mov word ptr [bp - 2], ax
2CBC  8B 46 FE        mov ax, word ptr [bp - 2]
2CBF  89 EC           mov sp, bp
2CC1  5D              pop bp
2CC2  CA 06 00        retf 6

; ---- routine 0791:2CC5  (found by: call)
sub_2CC5:
2CC5  55              push bp
2CC6  89 E5           mov bp, sp
2CC8  83 EC 02        sub sp, 2
2CCB  C4 7E 06        les di, ptr [bp + 6]
2CCE  26 8B 05        mov ax, word ptr es:[di]
2CD1  C4 7E 06        les di, ptr [bp + 6]
2CD4  26 3B 45 07     cmp ax, word ptr es:[di + 7]
2CD8  74 04           je 0x2cde
2CDA  B0 00           mov al, 0
2CDC  EB 02           jmp 0x2ce0
loc_2CDE:
2CDE  B0 01           mov al, 1
loc_2CE0:
2CE0  88 46 FF        mov byte ptr [bp - 1], al
2CE3  8A 46 FF        mov al, byte ptr [bp - 1]
2CE6  89 EC           mov sp, bp
2CE8  5D              pop bp
2CE9  CA 04 00        retf 4

; ---- routine 0791:2CEC  (found by: call)
sub_2CEC:
2CEC  55              push bp
2CED  89 E5           mov bp, sp
2CEF  83 EC 02        sub sp, 2
2CF2  C4 7E 06        les di, ptr [bp + 6]
2CF5  26 8B 05        mov ax, word ptr es:[di]
2CF8  3B 06 F6 82     cmp ax, word ptr [0x82f6]
2CFC  74 04           je 0x2d02
2CFE  B0 00           mov al, 0
2D00  EB 02           jmp 0x2d04
loc_2D02:
2D02  B0 01           mov al, 1
loc_2D04:
2D04  88 46 FF        mov byte ptr [bp - 1], al
2D07  8A 46 FF        mov al, byte ptr [bp - 1]
2D0A  89 EC           mov sp, bp
2D0C  5D              pop bp
2D0D  CA 04 00        retf 4

; ---- routine 0791:2D10  (found by: call)
sub_2D10:
2D10  55              push bp
2D11  89 E5           mov bp, sp
2D13  83 EC 02        sub sp, 2
2D16  C4 7E 06        les di, ptr [bp + 6]
2D19  06              push es
2D1A  57              push di
2D1B  0E              push cs
2D1C  E8 C6 FE        call 0x2be5
2D1F  98              cwde
2D20  8B D0           mov dx, ax
2D22  C4 7E 06        les di, ptr [bp + 6]
2D25  26 8A 45 01     mov al, byte ptr es:[di + 1]
2D29  98              cwde
2D2A  F7 EA           imul dx
2D2C  99              cdq
2D2D  8B C8           mov cx, ax
2D2F  8B DA           mov bx, dx
2D31  8B 46 0A        mov ax, word ptr [bp + 0xa]
2D34  31 D2           xor dx, dx
2D36  03 C1           add ax, cx
2D38  13 D3           adc dx, bx
2D3A  52              push dx
2D3B  50              push ax
2D3C  C4 7E 06        les di, ptr [bp + 6]
2D3F  06              push es
2D40  57              push di
2D41  0E              push cs
2D42  E8 A0 FE        call 0x2be5
2D45  98              cwde
2D46  8B D0           mov dx, ax
2D48  A0 F7 82        mov al, byte ptr [0x82f7]
2D4B  98              cwde
2D4C  F7 EA           imul dx
2D4E  99              cdq
2D4F  59              pop cx
2D50  5B              pop bx
2D51  3B D3           cmp dx, bx
2D53  7F 0A           jg 0x2d5f
2D55  7C 04           jl 0x2d5b
2D57  3B C1           cmp ax, cx
2D59  77 04           ja 0x2d5f
loc_2D5B:
2D5B  B0 00           mov al, 0
2D5D  EB 02           jmp 0x2d61
loc_2D5F:
2D5F  B0 01           mov al, 1
loc_2D61:
2D61  88 46 FF        mov byte ptr [bp - 1], al
2D64  8A 46 FF        mov al, byte ptr [bp - 1]
2D67  89 EC           mov sp, bp
2D69  5D              pop bp
2D6A  CA 06 00        retf 6

; ---- routine 0791:2D6D  (found by: call)
sub_2D6D:
2D6D  55              push bp
2D6E  89 E5           mov bp, sp
2D70  83 EC 02        sub sp, 2
2D73  C4 7E 06        les di, ptr [bp + 6]
2D76  06              push es
2D77  57              push di
2D78  0E              push cs
2D79  E8 69 FE        call 0x2be5
2D7C  98              cwde
2D7D  8B D0           mov dx, ax
2D7F  C4 7E 06        les di, ptr [bp + 6]
2D82  26 8A 45 01     mov al, byte ptr es:[di + 1]
2D86  98              cwde
2D87  F7 EA           imul dx
2D89  99              cdq
2D8A  52              push dx
2D8B  50              push ax
2D8C  C4 7E 06        les di, ptr [bp + 6]
2D8F  06              push es
2D90  57              push di
2D91  0E              push cs
2D92  E8 50 FE        call 0x2be5
2D95  98              cwde
2D96  8B D0           mov dx, ax
2D98  A0 F7 82        mov al, byte ptr [0x82f7]
2D9B  98              cwde
2D9C  F7 EA           imul dx
2D9E  99              cdq
2D9F  8B C8           mov cx, ax
2DA1  8B DA           mov bx, dx
2DA3  8B 46 0A        mov ax, word ptr [bp + 0xa]
2DA6  31 D2           xor dx, dx
2DA8  03 C1           add ax, cx
2DAA  13 D3           adc dx, bx
2DAC  59              pop cx
2DAD  5B              pop bx
2DAE  3B D3           cmp dx, bx
2DB0  7C 0A           jl 0x2dbc
2DB2  7F 04           jg 0x2db8
2DB4  3B C1           cmp ax, cx
2DB6  72 04           jb 0x2dbc
loc_2DB8:
2DB8  B0 00           mov al, 0
2DBA  EB 02           jmp 0x2dbe
loc_2DBC:
2DBC  B0 01           mov al, 1
loc_2DBE:
2DBE  88 46 FF        mov byte ptr [bp - 1], al
2DC1  8A 46 FF        mov al, byte ptr [bp - 1]
2DC4  89 EC           mov sp, bp
2DC6  5D              pop bp
2DC7  CA 06 00        retf 6

; ---- routine 0791:2DCA  (found by: call)
sub_2DCA:
2DCA  55              push bp
2DCB  89 E5           mov bp, sp
2DCD  83 EC 02        sub sp, 2
2DD0  8A 46 04        mov al, byte ptr [bp + 4]
2DD3  98              cwde
2DD4  09 C0           or ax, ax
2DD6  79 02           jns 0x2dda
2DD8  F7 D8           neg ax
loc_2DDA:
2DDA  3D 08 00        cmp ax, 8
2DDD  7F 0F           jg 0x2dee
2DDF  8A 46 05        mov al, byte ptr [bp + 5]
2DE2  98              cwde
2DE3  09 C0           or ax, ax
2DE5  79 02           jns 0x2de9
2DE7  F7 D8           neg ax
loc_2DE9:
2DE9  3D 25 00        cmp ax, 0x25
2DEC  7E 04           jle 0x2df2
loc_2DEE:
2DEE  B0 00           mov al, 0
2DF0  EB 02           jmp 0x2df4
loc_2DF2:
2DF2  B0 01           mov al, 1
loc_2DF4:
2DF4  88 46 FF        mov byte ptr [bp - 1], al
2DF7  8A 46 FF        mov al, byte ptr [bp - 1]
2DFA  89 EC           mov sp, bp
2DFC  5D              pop bp
2DFD  C2 02 00        ret 2

; ---- routine 0791:2E00  (found by: call)
sub_2E00:
2E00  55              push bp
2E01  89 E5           mov bp, sp
2E03  83 EC 02        sub sp, 2
2E06  8A 46 04        mov al, byte ptr [bp + 4]
2E09  98              cwde
2E0A  09 C0           or ax, ax
2E0C  79 02           jns 0x2e10
2E0E  F7 D8           neg ax
loc_2E10:
2E10  3D 09 00        cmp ax, 9
2E13  7F 0F           jg 0x2e24
2E15  8A 46 05        mov al, byte ptr [bp + 5]
2E18  98              cwde
2E19  09 C0           or ax, ax
2E1B  79 02           jns 0x2e1f
2E1D  F7 D8           neg ax
loc_2E1F:
2E1F  3D 27 00        cmp ax, 0x27
2E22  7E 04           jle 0x2e28
loc_2E24:
2E24  B0 00           mov al, 0
2E26  EB 02           jmp 0x2e2a
loc_2E28:
2E28  B0 01           mov al, 1
loc_2E2A:
2E2A  88 46 FF        mov byte ptr [bp - 1], al
2E2D  8A 46 FF        mov al, byte ptr [bp - 1]
2E30  89 EC           mov sp, bp
2E32  5D              pop bp
2E33  C2 02 00        ret 2

; ---- routine 0791:2E36  (found by: call)
sub_2E36:
2E36  55              push bp
2E37  89 E5           mov bp, sp
2E39  83 EC 02        sub sp, 2
2E3C  C4 7E 06        les di, ptr [bp + 6]
2E3F  06              push es
2E40  57              push di
2E41  0E              push cs
2E42  E8 A0 FD        call 0x2be5
2E45  98              cwde
2E46  8B D0           mov dx, ax
2E48  8A 46 0B        mov al, byte ptr [bp + 0xb]
2E4B  98              cwde
2E4C  F7 EA           imul dx
2E4E  09 C0           or ax, ax
2E50  7D 1E           jge 0x2e70
2E52  8A 46 0B        mov al, byte ptr [bp + 0xb]
2E55  98              cwde
2E56  09 C0           or ax, ax
2E58  79 02           jns 0x2e5c
2E5A  F7 D8           neg ax
loc_2E5C:
2E5C  3D 21 00        cmp ax, 0x21
2E5F  7C 0F           jl 0x2e70
2E61  8A 46 0A        mov al, byte ptr [bp + 0xa]
2E64  98              cwde
2E65  09 C0           or ax, ax
2E67  79 02           jns 0x2e6b
2E69  F7 D8           neg ax
loc_2E6B:
2E6B  3D 02 00        cmp ax, 2
2E6E  7E 04           jle 0x2e74
loc_2E70:
2E70  B0 00           mov al, 0
2E72  EB 02           jmp 0x2e76
loc_2E74:
2E74  B0 01           mov al, 1
loc_2E76:
2E76  88 46 FF        mov byte ptr [bp - 1], al
2E79  8A 46 FF        mov al, byte ptr [bp - 1]
2E7C  89 EC           mov sp, bp
2E7E  5D              pop bp
2E7F  CA 06 00        retf 6

; ---- routine 0791:2E82  (found by: call)
sub_2E82:
2E82  55              push bp
2E83  89 E5           mov bp, sp
2E85  83 EC 02        sub sp, 2
2E88  8A 46 05        mov al, byte ptr [bp + 5]
2E8B  98              cwde
2E8C  09 C0           or ax, ax
2E8E  79 02           jns 0x2e92
2E90  F7 D8           neg ax
loc_2E92:
2E92  3D 19 00        cmp ax, 0x19
2E95  7C 0F           jl 0x2ea6
2E97  8A 46 04        mov al, byte ptr [bp + 4]
2E9A  98              cwde
2E9B  09 C0           or ax, ax
2E9D  79 02           jns 0x2ea1
2E9F  F7 D8           neg ax
loc_2EA1:
2EA1  3D 05 00        cmp ax, 5
2EA4  7E 04           jle 0x2eaa
loc_2EA6:
2EA6  B0 00           mov al, 0
2EA8  EB 02           jmp 0x2eac
loc_2EAA:
2EAA  B0 01           mov al, 1
loc_2EAC:
2EAC  88 46 FF        mov byte ptr [bp - 1], al
2EAF  8A 46 FF        mov al, byte ptr [bp - 1]
2EB2  89 EC           mov sp, bp
2EB4  5D              pop bp
2EB5  C2 02 00        ret 2

; ---- routine 0791:2EB8  (found by: call)
sub_2EB8:
2EB8  55              push bp
2EB9  89 E5           mov bp, sp
2EBB  83 EC 02        sub sp, 2
2EBE  C4 7E 06        les di, ptr [bp + 6]
2EC1  06              push es
2EC2  57              push di
2EC3  0E              push cs
2EC4  E8 1E FD        call 0x2be5
2EC7  98              cwde
2EC8  8B D0           mov dx, ax
2ECA  8A 46 0B        mov al, byte ptr [bp + 0xb]
2ECD  98              cwde
2ECE  F7 EA           imul dx
2ED0  09 C0           or ax, ax
2ED2  7D 0A           jge 0x2ede
2ED4  FF 76 0A        push word ptr [bp + 0xa]
2ED7  E8 A8 FF        call 0x2e82
2EDA  08 C0           or al, al
2EDC  75 04           jne 0x2ee2
loc_2EDE:
2EDE  B0 00           mov al, 0
2EE0  EB 02           jmp 0x2ee4
loc_2EE2:
2EE2  B0 01           mov al, 1
loc_2EE4:
2EE4  88 46 FF        mov byte ptr [bp - 1], al
2EE7  8A 46 FF        mov al, byte ptr [bp - 1]
2EEA  89 EC           mov sp, bp
2EEC  5D              pop bp
2EED  CA 06 00        retf 6

; ---- routine 0791:2EF0  (found by: call)
sub_2EF0:
2EF0  55              push bp
2EF1  89 E5           mov bp, sp
2EF3  83 EC 02        sub sp, 2
2EF6  C4 7E 06        les di, ptr [bp + 6]
2EF9  06              push es
2EFA  57              push di
2EFB  0E              push cs
2EFC  E8 E6 FC        call 0x2be5
2EFF  98              cwde
2F00  8B D0           mov dx, ax
2F02  8A 46 0B        mov al, byte ptr [bp + 0xb]
2F05  98              cwde
2F06  F7 EA           imul dx
2F08  09 C0           or ax, ax
2F0A  7E 0A           jle 0x2f16
2F0C  FF 76 0A        push word ptr [bp + 0xa]
2F0F  E8 70 FF        call 0x2e82
2F12  08 C0           or al, al
2F14  75 04           jne 0x2f1a
loc_2F16:
2F16  B0 00           mov al, 0
2F18  EB 02           jmp 0x2f1c
loc_2F1A:
2F1A  B0 01           mov al, 1
loc_2F1C:
2F1C  88 46 FF        mov byte ptr [bp - 1], al
2F1F  8A 46 FF        mov al, byte ptr [bp - 1]
2F22  89 EC           mov sp, bp
2F24  5D              pop bp
2F25  CA 06 00        retf 6

; ---- routine 0791:2F28  (found by: call)
sub_2F28:
2F28  55              push bp
2F29  89 E5           mov bp, sp
2F2B  83 EC 02        sub sp, 2
2F2E  C4 7E 06        les di, ptr [bp + 6]
2F31  06              push es
2F32  57              push di
2F33  0E              push cs
2F34  E8 1D FD        call 0x2c54
2F37  08 C0           or al, al
2F39  75 64           jne 0x2f9f
2F3B  C4 7E 06        les di, ptr [bp + 6]
2F3E  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
2F42  BA 14 00        mov dx, 0x14
2F45  F7 E2           mul dx
2F47  C4 3E 1B A9     les di, ptr [0xa91b]
2F4B  03 F8           add di, ax
2F4D  26 8A 45 06     mov al, byte ptr es:[di + 6]
2F51  30 E4           xor ah, ah
2F53  05 0C 00        add ax, 0xc
2F56  8B D0           mov dx, ax
2F58  C4 7E 06        les di, ptr [bp + 6]
2F5B  26 8A 45 01     mov al, byte ptr es:[di + 1]
2F5F  98              cwde
2F60  09 C0           or ax, ax
2F62  79 02           jns 0x2f66
2F64  F7 D8           neg ax
loc_2F66:
2F66  3B C2           cmp ax, dx
2F68  7C 35           jl 0x2f9f
2F6A  C4 7E 06        les di, ptr [bp + 6]
2F6D  26 8A 45 01     mov al, byte ptr es:[di + 1]
2F71  98              cwde
2F72  09 C0           or ax, ax
2F74  79 02           jns 0x2f78
2F76  F7 D8           neg ax
loc_2F78:
2F78  3D 1C 00        cmp ax, 0x1c
2F7B  7F 04           jg 0x2f81
2F7D  B0 00           mov al, 0
2F7F  EB 02           jmp 0x2f83
loc_2F81:
2F81  B0 01           mov al, 1
loc_2F83:
2F83  98              cwde
2F84  8B F8           mov di, ax
2F86  8A 85 76 07     mov al, byte ptr [di + 0x776]
2F8A  30 E4           xor ah, ah
2F8C  8B D0           mov dx, ax
2F8E  C4 7E 06        les di, ptr [bp + 6]
2F91  26 8A 05        mov al, byte ptr es:[di]
2F94  98              cwde
2F95  09 C0           or ax, ax
2F97  79 02           jns 0x2f9b
2F99  F7 D8           neg ax
loc_2F9B:
2F9B  3B C2           cmp ax, dx
2F9D  7E 04           jle 0x2fa3
loc_2F9F:
2F9F  B0 00           mov al, 0
2FA1  EB 02           jmp 0x2fa5
loc_2FA3:
2FA3  B0 01           mov al, 1
loc_2FA5:
2FA5  88 46 FF        mov byte ptr [bp - 1], al
2FA8  8A 46 FF        mov al, byte ptr [bp - 1]
2FAB  89 EC           mov sp, bp
2FAD  5D              pop bp
2FAE  CA 04 00        retf 4

; ---- routine 0791:2FB1  (found by: call)
sub_2FB1:
2FB1  55              push bp
2FB2  89 E5           mov bp, sp
2FB4  83 EC 0E        sub sp, 0xe
2FB7  C6 46 FF 00     mov byte ptr [bp - 1], 0
2FBB  EB 03           jmp 0x2fc0
loc_2FBD:
2FBD  FE 46 FF        inc byte ptr [bp - 1]
loc_2FC0:
2FC0  8A 46 FF        mov al, byte ptr [bp - 1]
2FC3  98              cwde
2FC4  8B F8           mov di, ax
2FC6  C6 85 11 83 00  mov byte ptr [di - 0x7cef], 0
2FCB  8A 46 FF        mov al, byte ptr [bp - 1]
2FCE  98              cwde
2FCF  8B F8           mov di, ax
2FD1  C6 85 0F 83 00  mov byte ptr [di - 0x7cf1], 0
2FD6  C7 46 FB 64 00  mov word ptr [bp - 5], 0x64
2FDB  C7 46 F9 64 00  mov word ptr [bp - 7], 0x64
2FE0  C7 46 FD 02 00  mov word ptr [bp - 3], 2
2FE5  EB 03           jmp 0x2fea
loc_2FE7:
2FE7  FF 46 FD        inc word ptr [bp - 3]
loc_2FEA:
2FEA  8A 46 FF        mov al, byte ptr [bp - 1]
2FED  98              cwde
2FEE  8B F8           mov di, ax
2FF0  8A 85 68 06     mov al, byte ptr [di + 0x668]
2FF4  30 E4           xor ah, ah
2FF6  03 46 FD        add ax, word ptr [bp - 3]
2FF9  BA 16 00        mov dx, 0x16
2FFC  F7 E2           mul dx
2FFE  8B F8           mov di, ax
3000  81 C7 E8 80     add di, 0x80e8
3004  89 7E F3        mov word ptr [bp - 0xd], di
3007  8C 5E F5        mov word ptr [bp - 0xb], ds
300A  C4 7E F3        les di, ptr [bp - 0xd]
300D  06              push es
300E  57              push di
300F  0E              push cs
3010  E8 43 F9        call 0x2956
3013  08 C0           or al, al
3015  74 03           je 0x301a
3017  E9 BA 00        jmp 0x30d4
loc_301A:
301A  A0 0B 83        mov al, byte ptr [0x830b]
301D  C4 7E F3        les di, ptr [bp - 0xd]
3020  26 3A 45 06     cmp al, byte ptr es:[di + 6]
3024  75 03           jne 0x3029
3026  E9 AB 00        jmp 0x30d4
loc_3029:
3029  C4 7E F3        les di, ptr [bp - 0xd]
302C  26 80 7D 12 0D  cmp byte ptr es:[di + 0x12], 0xd
3031  75 03           jne 0x3036
3033  E9 9E 00        jmp 0x30d4
loc_3036:
3036  A0 F6 82        mov al, byte ptr [0x82f6]
3039  98              cwde
303A  8B D0           mov dx, ax
303C  C4 7E F3        les di, ptr [bp - 0xd]
303F  26 8A 05        mov al, byte ptr es:[di]
3042  98              cwde
3043  2B C2           sub ax, dx
3045  09 C0           or ax, ax
3047  79 02           jns 0x304b
3049  F7 D8           neg ax
loc_304B:
304B  8B C8           mov cx, ax
304D  A0 F7 82        mov al, byte ptr [0x82f7]
3050  98              cwde
3051  8B D0           mov dx, ax
3053  C4 7E F3        les di, ptr [bp - 0xd]
3056  26 8A 45 01     mov al, byte ptr es:[di + 1]
305A  98              cwde
305B  2B C2           sub ax, dx
305D  09 C0           or ax, ax
305F  79 02           jns 0x3063
3061  F7 D8           neg ax
loc_3063:
3063  03 C1           add ax, cx
3065  89 46 F7        mov word ptr [bp - 9], ax
3068  8B 46 F7        mov ax, word ptr [bp - 9]
306B  3B 46 FB        cmp ax, word ptr [bp - 5]
306E  73 17           jae 0x3087
3070  C4 7E F3        les di, ptr [bp - 0xd]
3073  26 8A 55 06     mov dl, byte ptr es:[di + 6]
3077  8A 46 FF        mov al, byte ptr [bp - 1]
307A  98              cwde
307B  8B F8           mov di, ax
307D  88 95 11 83     mov byte ptr [di - 0x7cef], dl
3081  8B 46 F7        mov ax, word ptr [bp - 9]
3084  89 46 FB        mov word ptr [bp - 5], ax
loc_3087:
3087  C4 7E F3        les di, ptr [bp - 0xd]
308A  06              push es
308B  57              push di
308C  0E              push cs
308D  E8 55 FB        call 0x2be5
3090  98              cwde
3091  8B D0           mov dx, ax
3093  A0 F7 82        mov al, byte ptr [0x82f7]
3096  98              cwde
3097  F7 EA           imul dx
3099  50              push ax
309A  C4 7E F3        les di, ptr [bp - 0xd]
309D  06              push es
309E  57              push di
309F  0E              push cs
30A0  E8 42 FB        call 0x2be5
30A3  98              cwde
30A4  8B D0           mov dx, ax
30A6  C4 7E F3        les di, ptr [bp - 0xd]
30A9  26 8A 45 01     mov al, byte ptr es:[di + 1]
30AD  98              cwde
30AE  F7 EA           imul dx
30B0  5A              pop dx
30B1  3B C2           cmp ax, dx
30B3  7D 1F           jge 0x30d4
30B5  8B 46 F7        mov ax, word ptr [bp - 9]
30B8  3B 46 F9        cmp ax, word ptr [bp - 7]
30BB  73 17           jae 0x30d4
30BD  C4 7E F3        les di, ptr [bp - 0xd]
30C0  26 8A 55 06     mov dl, byte ptr es:[di + 6]
30C4  8A 46 FF        mov al, byte ptr [bp - 1]
30C7  98              cwde
30C8  8B F8           mov di, ax
30CA  88 95 0F 83     mov byte ptr [di - 0x7cf1], dl
30CE  8B 46 F7        mov ax, word ptr [bp - 9]
30D1  89 46 F9        mov word ptr [bp - 7], ax
loc_30D4:
30D4  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
30D8  74 03           je 0x30dd
30DA  E9 0A FF        jmp 0x2fe7
loc_30DD:
30DD  80 7E FF 01     cmp byte ptr [bp - 1], 1
30E1  74 03           je 0x30e6
30E3  E9 D7 FE        jmp 0x2fbd
loc_30E6:
30E6  89 EC           mov sp, bp
30E8  5D              pop bp
30E9  C3              ret

; ---- routine 0791:30EA  (found by: call)
sub_30EA:
30EA  55              push bp
30EB  89 E5           mov bp, sp
30ED  83 EC 02        sub sp, 2
30F0  C4 7E 06        les di, ptr [bp + 6]
30F3  06              push es
30F4  57              push di
30F5  0E              push cs
30F6  E8 7B F8        call 0x2974
30F9  98              cwde
30FA  8B F8           mov di, ax
30FC  8A 85 68 06     mov al, byte ptr [di + 0x668]
3100  30 E4           xor ah, ah
3102  03 46 0A        add ax, word ptr [bp + 0xa]
3105  89 46 FE        mov word ptr [bp - 2], ax
3108  8B 46 FE        mov ax, word ptr [bp - 2]
310B  89 EC           mov sp, bp
310D  5D              pop bp
310E  CA 06 00        retf 6

; ---- routine 0791:3111  (found by: call)
sub_3111:
3111  55              push bp
3112  89 E5           mov bp, sp
3114  83 EC 0E        sub sp, 0xe
3117  B8 03 00        mov ax, 3
311A  50              push ax
311B  C4 7E 06        les di, ptr [bp + 6]
311E  06              push es
311F  57              push di
3120  0E              push cs
3121  E8 B3 F5        call 0x26d7
3124  08 C0           or al, al
3126  75 22           jne 0x314a
3128  C4 7E 06        les di, ptr [bp + 6]
312B  06              push es
312C  57              push di
312D  0E              push cs
312E  E8 23 FB        call 0x2c54
3131  08 C0           or al, al
3133  74 11           je 0x3146
3135  C4 7E 06        les di, ptr [bp + 6]
3138  26 8A 45 06     mov al, byte ptr es:[di + 6]
313C  30 E4           xor ah, ah
313E  50              push ax
313F  E8 1B D3        call 0x45d
3142  08 C0           or al, al
3144  74 04           je 0x314a
loc_3146:
3146  B0 00           mov al, 0
3148  EB 02           jmp 0x314c
loc_314A:
314A  B0 01           mov al, 1
loc_314C:
314C  88 46 F5        mov byte ptr [bp - 0xb], al
314F  E8 C8 F4        call 0x261a
3152  8B D0           mov dx, ax
3154  8A 46 F5        mov al, byte ptr [bp - 0xb]
3157  98              cwde
3158  8B F8           mov di, ax
315A  8A 85 78 07     mov al, byte ptr [di + 0x778]
315E  30 E4           xor ah, ah
3160  03 C2           add ax, dx
3162  89 46 F6        mov word ptr [bp - 0xa], ax
3165  C4 7E 06        les di, ptr [bp + 6]
3168  26 8A 45 06     mov al, byte ptr es:[di + 6]
316C  30 E4           xor ah, ah
316E  89 46 FA        mov word ptr [bp - 6], ax
3171  B8 02 00        mov ax, 2
3174  50              push ax
3175  C4 7E 06        les di, ptr [bp + 6]
3178  06              push es
3179  57              push di
317A  0E              push cs
317B  E8 6C FF        call 0x30ea
317E  89 46 F3        mov word ptr [bp - 0xd], ax
3181  B8 0B 00        mov ax, 0xb
3184  50              push ax
3185  C4 7E 06        les di, ptr [bp + 6]
3188  06              push es
3189  57              push di
318A  0E              push cs
318B  E8 5C FF        call 0x30ea
318E  3B 46 F3        cmp ax, word ptr [bp - 0xd]
3191  73 03           jae 0x3196
3193  E9 05 01        jmp 0x329b
loc_3196:
3196  89 46 FC        mov word ptr [bp - 4], ax
3199  EB 03           jmp 0x319e
loc_319B:
319B  FF 4E FC        dec word ptr [bp - 4]
loc_319E:
319E  C4 7E 06        les di, ptr [bp + 6]
31A1  26 8A 45 06     mov al, byte ptr es:[di + 6]
31A5  30 E4           xor ah, ah
31A7  3B 46 FC        cmp ax, word ptr [bp - 4]
31AA  75 03           jne 0x31af
31AC  E9 E1 00        jmp 0x3290
loc_31AF:
31AF  8B 46 FC        mov ax, word ptr [bp - 4]
31B2  BA 16 00        mov dx, 0x16
31B5  F7 E2           mul dx
31B7  8B F8           mov di, ax
31B9  81 C7 E8 80     add di, 0x80e8
31BD  1E              push ds
31BE  57              push di
31BF  0E              push cs
31C0  E8 93 F7        call 0x2956
31C3  08 C0           or al, al
31C5  74 03           je 0x31ca
31C7  E9 C6 00        jmp 0x3290
loc_31CA:
31CA  B8 0A 00        mov ax, 0xa
31CD  50              push ax
31CE  8B 46 FC        mov ax, word ptr [bp - 4]
31D1  BA 16 00        mov dx, 0x16
31D4  F7 E2           mul dx
31D6  8B F8           mov di, ax
31D8  81 C7 E8 80     add di, 0x80e8
31DC  1E              push ds
31DD  57              push di
31DE  0E              push cs
31DF  E8 2E FB        call 0x2d10
31E2  08 C0           or al, al
31E4  74 03           je 0x31e9
31E6  E9 A7 00        jmp 0x3290
loc_31E9:
31E9  8B 46 FC        mov ax, word ptr [bp - 4]
31EC  BA 16 00        mov dx, 0x16
31EF  F7 E2           mul dx
31F1  8B F8           mov di, ax
31F3  80 BD FA 80 0D  cmp byte ptr [di - 0x7f06], 0xd
31F8  75 03           jne 0x31fd
31FA  E9 93 00        jmp 0x3290
loc_31FD:
31FD  8B 46 F6        mov ax, word ptr [bp - 0xa]
3200  89 46 F8        mov word ptr [bp - 8], ax
3203  C4 7E 06        les di, ptr [bp + 6]
3206  26 8A 05        mov al, byte ptr es:[di]
3209  98              cwde
320A  8B C8           mov cx, ax
320C  8B 46 FC        mov ax, word ptr [bp - 4]
320F  BA 16 00        mov dx, 0x16
3212  F7 E2           mul dx
3214  8B F8           mov di, ax
3216  8A 85 E8 80     mov al, byte ptr [di - 0x7f18]
321A  98              cwde
321B  2B C1           sub ax, cx
321D  09 C0           or ax, ax
321F  79 02           jns 0x3223
3221  F7 D8           neg ax
loc_3223:
3223  8B D8           mov bx, ax
3225  C4 7E 06        les di, ptr [bp + 6]
3228  26 8A 45 01     mov al, byte ptr es:[di + 1]
322C  98              cwde
322D  8B C8           mov cx, ax
322F  8B 46 FC        mov ax, word ptr [bp - 4]
3232  BA 16 00        mov dx, 0x16
3235  F7 E2           mul dx
3237  8B F8           mov di, ax
3239  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
323D  98              cwde
323E  2B C1           sub ax, cx
3240  09 C0           or ax, ax
3242  79 02           jns 0x3246
3244  F7 D8           neg ax
loc_3246:
3246  03 C3           add ax, bx
3248  89 46 F6        mov word ptr [bp - 0xa], ax
324B  8B 46 F6        mov ax, word ptr [bp - 0xa]
324E  3B 46 F8        cmp ax, word ptr [bp - 8]
3251  77 04           ja 0x3257
3253  B0 00           mov al, 0
3255  EB 02           jmp 0x3259
loc_3257:
3257  B0 01           mov al, 1
loc_3259:
3259  3A 46 F5        cmp al, byte ptr [bp - 0xb]
325C  75 2C           jne 0x328a
325E  C4 7E 06        les di, ptr [bp + 6]
3261  26 8A 45 06     mov al, byte ptr es:[di + 6]
3265  30 E4           xor ah, ah
3267  3B 46 FA        cmp ax, word ptr [bp - 6]
326A  74 09           je 0x3275
326C  9A FA 06 4B 21  call far 214B:06FA
3271  08 C0           or al, al
3273  74 15           je 0x328a
loc_3275:
3275  8B 46 FC        mov ax, word ptr [bp - 4]
3278  BA 16 00        mov dx, 0x16
327B  F7 E2           mul dx
327D  8B F8           mov di, ax
327F  8A 85 EE 80     mov al, byte ptr [di - 0x7f12]
3283  30 E4           xor ah, ah
3285  89 46 FA        mov word ptr [bp - 6], ax
3288  EB 06           jmp 0x3290
loc_328A:
328A  8B 46 F8        mov ax, word ptr [bp - 8]
328D  89 46 F6        mov word ptr [bp - 0xa], ax
loc_3290:
3290  8B 46 FC        mov ax, word ptr [bp - 4]
3293  3B 46 F3        cmp ax, word ptr [bp - 0xd]
3296  74 03           je 0x329b
3298  E9 00 FF        jmp 0x319b
loc_329B:
329B  C4 7E 06        les di, ptr [bp + 6]
329E  26 8A 45 06     mov al, byte ptr es:[di + 6]
32A2  30 E4           xor ah, ah
32A4  3B 46 FA        cmp ax, word ptr [bp - 6]
32A7  75 6B           jne 0x3314
32A9  B8 0B 00        mov ax, 0xb
32AC  50              push ax
32AD  C4 7E 06        les di, ptr [bp + 6]
32B0  06              push es
32B1  57              push di
32B2  0E              push cs
32B3  E8 34 FE        call 0x30ea
32B6  89 46 F3        mov word ptr [bp - 0xd], ax
32B9  B8 02 00        mov ax, 2
32BC  50              push ax
32BD  C4 7E 06        les di, ptr [bp + 6]
32C0  06              push es
32C1  57              push di
32C2  0E              push cs
32C3  E8 24 FE        call 0x30ea
32C6  3B 46 F3        cmp ax, word ptr [bp - 0xd]
32C9  77 49           ja 0x3314
32CB  89 46 FC        mov word ptr [bp - 4], ax
32CE  EB 03           jmp 0x32d3
loc_32D0:
32D0  FF 46 FC        inc word ptr [bp - 4]
loc_32D3:
32D3  C4 7E 06        les di, ptr [bp + 6]
32D6  26 8A 45 06     mov al, byte ptr es:[di + 6]
32DA  30 E4           xor ah, ah
32DC  3B 46 FC        cmp ax, word ptr [bp - 4]
32DF  74 2B           je 0x330c
32E1  8B 46 FC        mov ax, word ptr [bp - 4]
32E4  BA 16 00        mov dx, 0x16
32E7  F7 E2           mul dx
32E9  8B F8           mov di, ax
32EB  81 C7 E8 80     add di, 0x80e8
32EF  1E              push ds
32F0  57              push di
32F1  0E              push cs
32F2  E8 61 F6        call 0x2956
32F5  08 C0           or al, al
32F7  75 13           jne 0x330c
32F9  8B 46 FC        mov ax, word ptr [bp - 4]
32FC  BA 16 00        mov dx, 0x16
32FF  F7 E2           mul dx
3301  8B F8           mov di, ax
3303  8A 85 EE 80     mov al, byte ptr [di - 0x7f12]
3307  30 E4           xor ah, ah
3309  89 46 FA        mov word ptr [bp - 6], ax
loc_330C:
330C  8B 46 FC        mov ax, word ptr [bp - 4]
330F  3B 46 F3        cmp ax, word ptr [bp - 0xd]
3312  75 BC           jne 0x32d0
loc_3314:
3314  8B 46 FA        mov ax, word ptr [bp - 6]
3317  89 46 FE        mov word ptr [bp - 2], ax
331A  8B 46 FE        mov ax, word ptr [bp - 2]
331D  89 EC           mov sp, bp
331F  5D              pop bp
3320  CA 04 00        retf 4

