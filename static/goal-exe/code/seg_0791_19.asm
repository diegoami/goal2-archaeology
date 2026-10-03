; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 19 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:B7FA  (found by: far)
sub_B7FA:
B7FA  55              push bp
B7FB  89 E5           mov bp, sp
B7FD  83 EC 1A        sub sp, 0x1a
B800  C4 7E 06        les di, ptr [bp + 6]
B803  89 7E F3        mov word ptr [bp - 0xd], di
B806  8C 46 F5        mov word ptr [bp - 0xb], es
B809  C4 7E F3        les di, ptr [bp - 0xd]
B80C  26 FF 75 04     push word ptr es:[di + 4]
B810  9A 77 0B 71 17  call far 1771:0B77
B815  08 C0           or al, al
B817  75 14           jne 0xb82d
B819  C4 7E F3        les di, ptr [bp - 0xd]
B81C  26 FF 75 06     push word ptr es:[di + 6]
B820  9A 77 0B 71 17  call far 1771:0B77
B825  08 C0           or al, al
B827  75 04           jne 0xb82d
B829  B0 00           mov al, 0
B82B  EB 02           jmp 0xb82f
loc_B82D:
B82D  B0 01           mov al, 1
loc_B82F:
B82F  88 46 FB        mov byte ptr [bp - 5], al
B832  C6 46 F9 00     mov byte ptr [bp - 7], 0
B836  EB 03           jmp 0xb83b
loc_B838:
B838  FE 46 F9        inc byte ptr [bp - 7]
loc_B83B:
B83B  8A 46 F9        mov al, byte ptr [bp - 7]
B83E  98              cwde
B83F  D1 E0           shl ax, 1
B841  C4 7E F3        les di, ptr [bp - 0xd]
B844  03 F8           add di, ax
B846  26 8B 45 04     mov ax, word ptr es:[di + 4]
B84A  BA BF 00        mov dx, 0xbf
B84D  F7 E2           mul dx
B84F  C4 3E 17 A9     les di, ptr [0xa917]
B853  03 F8           add di, ax
B855  89 7E EF        mov word ptr [bp - 0x11], di
B858  8C 46 F1        mov word ptr [bp - 0xf], es
B85B  C4 7E 06        les di, ptr [bp + 6]
B85E  06              push es
B85F  57              push di
B860  8A 46 F9        mov al, byte ptr [bp - 7]
B863  50              push ax
B864  0E              push cs
B865  E8 B4 FE        call 0xb71c
B868  89 46 F7        mov word ptr [bp - 9], ax
B86B  80 7E FB 00     cmp byte ptr [bp - 5], 0
B86F  75 1B           jne 0xb88c
B871  C4 7E F3        les di, ptr [bp - 0xd]
B874  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
B879  74 11           je 0xb88c
B87B  C4 7E EF        les di, ptr [bp - 0x11]
B87E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
B882  30 E4           xor ah, ah
B884  50              push ax
B885  FF 76 F7        push word ptr [bp - 9]
B888  0E              push cs
B889  E8 40 FE        call 0xb6cc
loc_B88C:
B88C  8A 46 F9        mov al, byte ptr [bp - 7]
B88F  98              cwde
B890  D1 E0           shl ax, 1
B892  C4 7E F3        les di, ptr [bp - 0xd]
B895  03 F8           add di, ax
B897  26 FF 75 04     push word ptr es:[di + 4]
B89B  C4 7E 06        les di, ptr [bp + 6]
B89E  06              push es
B89F  57              push di
B8A0  9A 8F 5A 71 17  call far 1771:5A8F
B8A5  88 46 FA        mov byte ptr [bp - 6], al
B8A8  C7 46 FE 01 00  mov word ptr [bp - 2], 1
B8AD  EB 03           jmp 0xb8b2
loc_B8AF:
B8AF  FF 46 FE        inc word ptr [bp - 2]
loc_B8B2:
B8B2  8B 46 FE        mov ax, word ptr [bp - 2]
B8B5  D1 E0           shl ax, 1
B8B7  C4 7E EF        les di, ptr [bp - 0x11]
B8BA  03 F8           add di, ax
B8BC  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
B8C1  75 03           jne 0xb8c6
B8C3  E9 70 01        jmp 0xba36
loc_B8C6:
B8C6  8B 46 FE        mov ax, word ptr [bp - 2]
B8C9  D1 E0           shl ax, 1
B8CB  C4 7E EF        les di, ptr [bp - 0x11]
B8CE  03 F8           add di, ax
B8D0  26 8B 45 FE     mov ax, word ptr es:[di - 2]
B8D4  BA 14 00        mov dx, 0x14
B8D7  F7 E2           mul dx
B8D9  C4 3E 1B A9     les di, ptr [0xa91b]
B8DD  03 F8           add di, ax
B8DF  89 7E EB        mov word ptr [bp - 0x15], di
B8E2  8C 46 ED        mov word ptr [bp - 0x13], es
B8E5  83 7E FE 0C     cmp word ptr [bp - 2], 0xc
B8E9  72 1A           jb 0xb905
B8EB  B8 03 00        mov ax, 3
B8EE  50              push ax
B8EF  C4 7E EB        les di, ptr [bp - 0x15]
B8F2  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
B8F6  30 E4           xor ah, ah
B8F8  50              push ax
B8F9  9A 57 0C 4B 21  call far 214B:0C57
B8FE  08 C0           or al, al
B900  75 03           jne 0xb905
B902  E9 8E 00        jmp 0xb993
loc_B905:
B905  C4 7E EB        les di, ptr [bp - 0x15]
B908  26 FF 45 08     inc word ptr es:[di + 8]
B90C  80 7E FA 00     cmp byte ptr [bp - 6], 0
B910  74 18           je 0xb92a
B912  8B 46 FE        mov ax, word ptr [bp - 2]
B915  D1 E0           shl ax, 1
B917  C4 7E EF        les di, ptr [bp - 0x11]
B91A  03 F8           add di, ax
B91C  26 FF 75 FE     push word ptr es:[di - 2]
B920  B0 01           mov al, 1
B922  50              push ax
B923  9A 51 36 71 17  call far 1771:3651
B928  EB 13           jmp 0xb93d
loc_B92A:
B92A  8B 46 FE        mov ax, word ptr [bp - 2]
B92D  D1 E0           shl ax, 1
B92F  C4 7E EF        les di, ptr [bp - 0x11]
B932  03 F8           add di, ax
B934  26 FF 75 FE     push word ptr es:[di - 2]
B938  9A 58 35 71 17  call far 1771:3558
loc_B93D:
B93D  8B 46 FE        mov ax, word ptr [bp - 2]
B940  D1 E0           shl ax, 1
B942  C4 7E EF        les di, ptr [bp - 0x11]
B945  03 F8           add di, ax
B947  26 FF 75 FE     push word ptr es:[di - 2]
B94B  FF 76 F7        push word ptr [bp - 9]
B94E  E8 13 FA        call 0xb364
B951  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
B955  76 3A           jbe 0xb991
B957  B8 03 00        mov ax, 3
B95A  50              push ax
B95B  C4 7E EB        les di, ptr [bp - 0x15]
B95E  81 C7 10 00     add di, 0x10
B962  06              push es
B963  57              push di
B964  9A A1 0C 4B 21  call far 214B:0CA1
B969  8B 46 FE        mov ax, word ptr [bp - 2]
B96C  D1 E0           shl ax, 1
B96E  C4 7E EF        les di, ptr [bp - 0x11]
B971  03 F8           add di, ax
B973  26 FF 75 FE     push word ptr es:[di - 2]
B977  B8 02 00        mov ax, 2
B97A  50              push ax
B97B  9A B1 06 4B 21  call far 214B:06B1
B980  50              push ax
B981  B8 02 00        mov ax, 2
B984  50              push ax
B985  9A B1 06 4B 21  call far 214B:06B1
B98A  5A              pop dx
B98B  2B C2           sub ax, dx
B98D  50              push ax
B98E  E8 D3 F9        call 0xb364
loc_B991:
B991  EB 59           jmp 0xb9ec
loc_B993:
B993  8B 46 FE        mov ax, word ptr [bp - 2]
B996  D1 E0           shl ax, 1
B998  C4 7E EF        les di, ptr [bp - 0x11]
B99B  03 F8           add di, ax
B99D  26 FF 75 FE     push word ptr es:[di - 2]
B9A1  B8 04 00        mov ax, 4
B9A4  50              push ax
B9A5  9A B1 06 4B 21  call far 214B:06B1
B9AA  50              push ax
B9AB  B8 02 00        mov ax, 2
B9AE  50              push ax
B9AF  9A B1 06 4B 21  call far 214B:06B1
B9B4  5A              pop dx
B9B5  2B C2           sub ax, dx
B9B7  50              push ax
B9B8  E8 A9 F9        call 0xb364
B9BB  80 7E FA 00     cmp byte ptr [bp - 6], 0
B9BF  74 18           je 0xb9d9
B9C1  8B 46 FE        mov ax, word ptr [bp - 2]
B9C4  D1 E0           shl ax, 1
B9C6  C4 7E EF        les di, ptr [bp - 0x11]
B9C9  03 F8           add di, ax
B9CB  26 FF 75 FE     push word ptr es:[di - 2]
B9CF  B0 00           mov al, 0
B9D1  50              push ax
B9D2  9A 51 36 71 17  call far 1771:3651
B9D7  EB 13           jmp 0xb9ec
loc_B9D9:
B9D9  8B 46 FE        mov ax, word ptr [bp - 2]
B9DC  D1 E0           shl ax, 1
B9DE  C4 7E EF        les di, ptr [bp - 0x11]
B9E1  03 F8           add di, ax
B9E3  26 FF 75 FE     push word ptr es:[di - 2]
B9E7  9A 58 35 71 17  call far 1771:3558
loc_B9EC:
B9EC  8B 46 FE        mov ax, word ptr [bp - 2]
B9EF  D1 E0           shl ax, 1
B9F1  C4 7E EF        les di, ptr [bp - 0x11]
B9F4  03 F8           add di, ax
B9F6  26 FF 75 FE     push word ptr es:[di - 2]
B9FA  E8 82 F8        call 0xb27f
B9FD  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
BA01  76 33           jbe 0xba36
BA03  80 7E FB 00     cmp byte ptr [bp - 5], 0
BA07  75 2D           jne 0xba36
BA09  8B 46 FE        mov ax, word ptr [bp - 2]
BA0C  D1 E0           shl ax, 1
BA0E  C4 7E EF        les di, ptr [bp - 0x11]
BA11  03 F8           add di, ax
BA13  26 8B 45 FE     mov ax, word ptr es:[di - 2]
BA17  BA 14 00        mov dx, 0x14
BA1A  F7 E2           mul dx
BA1C  C4 3E 1B A9     les di, ptr [0xa91b]
BA20  03 F8           add di, ax
BA22  89 7E E7        mov word ptr [bp - 0x19], di
BA25  8C 46 E9        mov word ptr [bp - 0x17], es
BA28  C4 7E E7        les di, ptr [bp - 0x19]
BA2B  26 8A 45 07     mov al, byte ptr es:[di + 7]
BA2F  C4 7E E7        les di, ptr [bp - 0x19]
BA32  26 88 45 06     mov byte ptr es:[di + 6], al
loc_BA36:
BA36  83 7E FE 14     cmp word ptr [bp - 2], 0x14
BA3A  74 03           je 0xba3f
BA3C  E9 70 FE        jmp 0xb8af
loc_BA3F:
BA3F  80 7E F9 01     cmp byte ptr [bp - 7], 1
BA43  74 03           je 0xba48
BA45  E9 F0 FD        jmp 0xb838
loc_BA48:
BA48  89 EC           mov sp, bp
BA4A  5D              pop bp
BA4B  CA 04 00        retf 4

; ---- routine 0791:BA4E  (found by: call)
sub_BA4E:
BA4E  55              push bp
BA4F  89 E5           mov bp, sp
BA51  83 EC 0C        sub sp, 0xc
BA54  8B 46 04        mov ax, word ptr [bp + 4]
BA57  BA BF 00        mov dx, 0xbf
BA5A  F7 E2           mul dx
BA5C  C4 3E 17 A9     les di, ptr [0xa917]
BA60  03 F8           add di, ax
BA62  89 7E F7        mov word ptr [bp - 9], di
BA65  8C 46 F9        mov word ptr [bp - 7], es
BA68  C4 7E F7        les di, ptr [bp - 9]
BA6B  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
BA6F  30 E4           xor ah, ah
BA71  2D 80 00        sub ax, 0x80
BA74  8B F8           mov di, ax
BA76  D1 E7           shl di, 1
BA78  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
BA7C  89 46 FC        mov word ptr [bp - 4], ax
BA7F  FF 76 04        push word ptr [bp + 4]
BA82  C4 3E 2A 7C     les di, ptr [0x7c2a]
BA86  06              push es
BA87  57              push di
BA88  9A 8F 5A 71 17  call far 1771:5A8F
BA8D  88 46 FB        mov byte ptr [bp - 5], al
BA90  8B 46 FC        mov ax, word ptr [bp - 4]
BA93  05 4F 00        add ax, 0x4f
BA96  89 46 F5        mov word ptr [bp - 0xb], ax
BA99  8B 46 FC        mov ax, word ptr [bp - 4]
BA9C  3B 46 F5        cmp ax, word ptr [bp - 0xb]
BA9F  76 03           jbe 0xbaa4
BAA1  E9 85 00        jmp 0xbb29
loc_BAA4:
BAA4  89 46 FE        mov word ptr [bp - 2], ax
BAA7  EB 03           jmp 0xbaac
loc_BAA9:
BAA9  FF 46 FE        inc word ptr [bp - 2]
loc_BAAC:
BAAC  80 7E FB 00     cmp byte ptr [bp - 5], 0
BAB0  74 18           je 0xbaca
BAB2  8B 46 FE        mov ax, word ptr [bp - 2]
BAB5  D1 E0           shl ax, 1
BAB7  C4 3E 27 A9     les di, ptr [0xa927]
BABB  03 F8           add di, ax
BABD  26 FF 35        push word ptr es:[di]
BAC0  B0 00           mov al, 0
BAC2  50              push ax
BAC3  9A 51 36 71 17  call far 1771:3651
BAC8  EB 13           jmp 0xbadd
loc_BACA:
BACA  8B 46 FE        mov ax, word ptr [bp - 2]
BACD  D1 E0           shl ax, 1
BACF  C4 3E 27 A9     les di, ptr [0xa927]
BAD3  03 F8           add di, ax
BAD5  26 FF 35        push word ptr es:[di]
BAD8  9A 58 35 71 17  call far 1771:3558
loc_BADD:
BADD  8B 46 FE        mov ax, word ptr [bp - 2]
BAE0  D1 E0           shl ax, 1
BAE2  C4 3E 27 A9     les di, ptr [0xa927]
BAE6  03 F8           add di, ax
BAE8  26 FF 35        push word ptr es:[di]
BAEB  B8 04 00        mov ax, 4
BAEE  50              push ax
BAEF  9A B1 06 4B 21  call far 214B:06B1
BAF4  50              push ax
BAF5  B8 04 00        mov ax, 4
BAF8  50              push ax
BAF9  9A B1 06 4B 21  call far 214B:06B1
BAFE  5A              pop dx
BAFF  2B C2           sub ax, dx
BB01  50              push ax
BB02  E8 5F F8        call 0xb364
BB05  C4 3E 2A 7C     les di, ptr [0x7c2a]
BB09  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
BB0E  74 11           je 0xbb21
BB10  8B 46 FE        mov ax, word ptr [bp - 2]
BB13  D1 E0           shl ax, 1
BB15  C4 3E 27 A9     les di, ptr [0xa927]
BB19  03 F8           add di, ax
BB1B  26 FF 35        push word ptr es:[di]
BB1E  E8 5E F7        call 0xb27f
loc_BB21:
BB21  8B 46 FE        mov ax, word ptr [bp - 2]
BB24  3B 46 F5        cmp ax, word ptr [bp - 0xb]
BB27  75 80           jne 0xbaa9
loc_BB29:
BB29  89 EC           mov sp, bp
BB2B  5D              pop bp
BB2C  C2 02 00        ret 2

; ---- routine 0791:BB2F  (found by: far)
sub_BB2F:
BB2F  55              push bp
BB30  89 E5           mov bp, sp
BB32  83 EC 08        sub sp, 8
BB35  C4 7E 06        les di, ptr [bp + 6]
BB38  06              push es
BB39  57              push di
BB3A  E8 64 E9        call 0xa4a1
BB3D  C6 46 FF 00     mov byte ptr [bp - 1], 0
BB41  EB 03           jmp 0xbb46
loc_BB43:
BB43  FE 46 FF        inc byte ptr [bp - 1]
loc_BB46:
BB46  8A 46 FF        mov al, byte ptr [bp - 1]
BB49  98              cwde
BB4A  8B F8           mov di, ax
BB4C  D1 E7           shl di, 1
BB4E  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
BB52  BA BF 00        mov dx, 0xbf
BB55  F7 E2           mul dx
BB57  C4 3E 17 A9     les di, ptr [0xa917]
BB5B  03 F8           add di, ax
BB5D  89 7E F9        mov word ptr [bp - 7], di
BB60  8C 46 FB        mov word ptr [bp - 5], es
BB63  C7 46 FD 01 00  mov word ptr [bp - 3], 1
BB68  EB 03           jmp 0xbb6d
loc_BB6A:
BB6A  FF 46 FD        inc word ptr [bp - 3]
loc_BB6D:
BB6D  8B 46 FD        mov ax, word ptr [bp - 3]
BB70  D1 E0           shl ax, 1
BB72  C4 7E F9        les di, ptr [bp - 7]
BB75  03 F8           add di, ax
BB77  26 FF 75 FE     push word ptr es:[di - 2]
BB7B  9A 58 35 71 17  call far 1771:3558
BB80  8B 46 FD        mov ax, word ptr [bp - 3]
BB83  D1 E0           shl ax, 1
BB85  C4 7E F9        les di, ptr [bp - 7]
BB88  03 F8           add di, ax
BB8A  26 FF 75 FE     push word ptr es:[di - 2]
BB8E  B8 04 00        mov ax, 4
BB91  50              push ax
BB92  9A B1 06 4B 21  call far 214B:06B1
BB97  50              push ax
BB98  B8 02 00        mov ax, 2
BB9B  50              push ax
BB9C  9A B1 06 4B 21  call far 214B:06B1
BBA1  5A              pop dx
BBA2  2B C2           sub ax, dx
BBA4  50              push ax
BBA5  E8 BC F7        call 0xb364
BBA8  83 7E FD 14     cmp word ptr [bp - 3], 0x14
BBAC  75 BC           jne 0xbb6a
BBAE  8A 46 FF        mov al, byte ptr [bp - 1]
BBB1  98              cwde
BBB2  8B F8           mov di, ax
BBB4  D1 E7           shl di, 1
BBB6  FF B5 34 9B     push word ptr [di - 0x64cc]
BBBA  9A 77 0B 71 17  call far 1771:0B77
BBBF  08 C0           or al, al
BBC1  74 11           je 0xbbd4
BBC3  8A 46 FF        mov al, byte ptr [bp - 1]
BBC6  98              cwde
BBC7  8B F8           mov di, ax
BBC9  D1 E7           shl di, 1
BBCB  FF B5 34 9B     push word ptr [di - 0x64cc]
BBCF  E8 7C FE        call 0xba4e
BBD2  EB 10           jmp 0xbbe4
loc_BBD4:
BBD4  8A 46 FF        mov al, byte ptr [bp - 1]
BBD7  98              cwde
BBD8  8B F8           mov di, ax
BBDA  D1 E7           shl di, 1
BBDC  FF B5 34 9B     push word ptr [di - 0x64cc]
BBE0  0E              push cs
BBE1  E8 79 00        call 0xbc5d
loc_BBE4:
BBE4  80 7E FF 01     cmp byte ptr [bp - 1], 1
BBE8  74 03           je 0xbbed
BBEA  E9 56 FF        jmp 0xbb43
loc_BBED:
BBED  C4 7E 06        les di, ptr [bp + 6]
BBF0  26 C6 05 00     mov byte ptr es:[di], 0
BBF4  C6 06 1E 0C 00  mov byte ptr [0xc1e], 0
BBF9  89 EC           mov sp, bp
BBFB  5D              pop bp
BBFC  CA 04 00        retf 4

; ---- routine 0791:BBFF  (found by: call)
sub_BBFF:
BBFF  55              push bp
BC00  89 E5           mov bp, sp
BC02  83 EC 06        sub sp, 6
BC05  8B 46 06        mov ax, word ptr [bp + 6]
BC08  BA BF 00        mov dx, 0xbf
BC0B  F7 E2           mul dx
BC0D  C4 3E 17 A9     les di, ptr [0xa917]
BC11  03 F8           add di, ax
BC13  89 7E FA        mov word ptr [bp - 6], di
BC16  8C 46 FC        mov word ptr [bp - 4], es
BC19  8A 46 04        mov al, byte ptr [bp + 4]
BC1C  C4 7E FA        les di, ptr [bp - 6]
BC1F  26 88 45 2D     mov byte ptr es:[di + 0x2d], al
BC23  C7 46 FE 01 00  mov word ptr [bp - 2], 1
BC28  EB 03           jmp 0xbc2d
loc_BC2A:
BC2A  FF 46 FE        inc word ptr [bp - 2]
loc_BC2D:
BC2D  8B 46 FE        mov ax, word ptr [bp - 2]
BC30  D1 E0           shl ax, 1
BC32  C4 7E FA        les di, ptr [bp - 6]
BC35  03 F8           add di, ax
BC37  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
BC3C  74 13           je 0xbc51
BC3E  8B 46 FE        mov ax, word ptr [bp - 2]
BC41  D1 E0           shl ax, 1
BC43  C4 7E FA        les di, ptr [bp - 6]
BC46  03 F8           add di, ax
BC48  26 FF 75 FE     push word ptr es:[di - 2]
BC4C  9A 31 34 71 17  call far 1771:3431
loc_BC51:
BC51  83 7E FE 14     cmp word ptr [bp - 2], 0x14
BC55  75 D3           jne 0xbc2a
BC57  89 EC           mov sp, bp
BC59  5D              pop bp
BC5A  C2 04 00        ret 4

; ---- routine 0791:BC5D  (found by: call, far)
sub_BC5D:
BC5D  55              push bp
BC5E  89 E5           mov bp, sp
BC60  83 EC 06        sub sp, 6
BC63  8B 46 06        mov ax, word ptr [bp + 6]
BC66  BA BF 00        mov dx, 0xbf
BC69  F7 E2           mul dx
BC6B  C4 3E 17 A9     les di, ptr [0xa917]
BC6F  03 F8           add di, ax
BC71  89 7E FA        mov word ptr [bp - 6], di
BC74  8C 46 FC        mov word ptr [bp - 4], es
BC77  C7 46 FE 01 00  mov word ptr [bp - 2], 1
BC7C  EB 03           jmp 0xbc81
loc_BC7E:
BC7E  FF 46 FE        inc word ptr [bp - 2]
loc_BC81:
BC81  8B 46 FE        mov ax, word ptr [bp - 2]
BC84  D1 E0           shl ax, 1
BC86  C4 7E FA        les di, ptr [bp - 6]
BC89  03 F8           add di, ax
BC8B  26 8B 45 FE     mov ax, word ptr es:[di - 2]
BC8F  BA 14 00        mov dx, 0x14
BC92  F7 E2           mul dx
BC94  C4 3E 1B A9     les di, ptr [0xa91b]
BC98  03 F8           add di, ax
BC9A  26 C6 45 0F 00  mov byte ptr es:[di + 0xf], 0
BC9F  83 7E FE 14     cmp word ptr [bp - 2], 0x14
BCA3  75 D9           jne 0xbc7e
BCA5  FF 76 06        push word ptr [bp + 6]
BCA8  8B 7E 06        mov di, word ptr [bp + 6]
BCAB  8A 85 7C 9B     mov al, byte ptr [di - 0x6484]
BCAF  50              push ax
BCB0  E8 4C FF        call 0xbbff
BCB3  FF 76 06        push word ptr [bp + 6]
BCB6  9A CC 52 71 17  call far 1771:52CC
BCBB  C7 46 FE 01 00  mov word ptr [bp - 2], 1
BCC0  EB 03           jmp 0xbcc5
loc_BCC2:
BCC2  FF 46 FE        inc word ptr [bp - 2]
loc_BCC5:
BCC5  8B 46 FE        mov ax, word ptr [bp - 2]
BCC8  8B C8           mov cx, ax
BCCA  8B 46 06        mov ax, word ptr [bp + 6]
BCCD  BA 14 00        mov dx, 0x14
BCD0  F7 E2           mul dx
BCD2  8B F8           mov di, ax
BCD4  03 F9           add di, cx
BCD6  8A 8D 02 9F     mov cl, byte ptr [di - 0x60fe]
BCDA  8B 46 FE        mov ax, word ptr [bp - 2]
BCDD  D1 E0           shl ax, 1
BCDF  C4 7E FA        les di, ptr [bp - 6]
BCE2  03 F8           add di, ax
BCE4  26 8B 45 FE     mov ax, word ptr es:[di - 2]
BCE8  BA 14 00        mov dx, 0x14
BCEB  F7 E2           mul dx
BCED  C4 3E 1B A9     les di, ptr [0xa91b]
BCF1  03 F8           add di, ax
BCF3  26 88 4D 06     mov byte ptr es:[di + 6], cl
BCF7  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
BCFB  75 C5           jne 0xbcc2
BCFD  89 EC           mov sp, bp
BCFF  5D              pop bp
BD00  CA 02 00        retf 2

; ---- routine 0791:BD03  (found by: call)
sub_BD03:
BD03  55              push bp
BD04  89 E5           mov bp, sp
BD06  83 EC 08        sub sp, 8
BD09  31 C0           xor ax, ax
BD0B  89 46 FB        mov word ptr [bp - 5], ax
BD0E  31 C0           xor ax, ax
BD10  89 46 F9        mov word ptr [bp - 7], ax
BD13  C7 46 FD 01 00  mov word ptr [bp - 3], 1
BD18  EB 03           jmp 0xbd1d
loc_BD1A:
BD1A  FF 46 FD        inc word ptr [bp - 3]
loc_BD1D:
BD1D  8B 46 FD        mov ax, word ptr [bp - 3]
BD20  D1 E0           shl ax, 1
BD22  8B C8           mov cx, ax
BD24  8B 46 06        mov ax, word ptr [bp + 6]
BD27  BA BF 00        mov dx, 0xbf
BD2A  F7 E2           mul dx
BD2C  C4 3E 17 A9     les di, ptr [0xa917]
BD30  03 F8           add di, ax
BD32  03 F9           add di, cx
BD34  26 FF 75 FE     push word ptr es:[di - 2]
BD38  9A 7E 37 71 17  call far 1771:377E
BD3D  01 46 FB        add word ptr [bp - 5], ax
BD40  8B 46 FD        mov ax, word ptr [bp - 3]
BD43  D1 E0           shl ax, 1
BD45  8B C8           mov cx, ax
BD47  8B 46 04        mov ax, word ptr [bp + 4]
BD4A  BA BF 00        mov dx, 0xbf
BD4D  F7 E2           mul dx
BD4F  C4 3E 17 A9     les di, ptr [0xa917]
BD53  03 F8           add di, ax
BD55  03 F9           add di, cx
BD57  26 FF 75 FE     push word ptr es:[di - 2]
BD5B  9A 7E 37 71 17  call far 1771:377E
BD60  01 46 F9        add word ptr [bp - 7], ax
BD63  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
BD67  75 B1           jne 0xbd1a
BD69  8B 46 FB        mov ax, word ptr [bp - 5]
BD6C  3B 46 F9        cmp ax, word ptr [bp - 7]
BD6F  77 04           ja 0xbd75
BD71  B0 00           mov al, 0
BD73  EB 02           jmp 0xbd77
loc_BD75:
BD75  B0 01           mov al, 1
loc_BD77:
BD77  88 46 FF        mov byte ptr [bp - 1], al
BD7A  8A 46 FF        mov al, byte ptr [bp - 1]
BD7D  89 EC           mov sp, bp
BD7F  5D              pop bp
BD80  C2 04 00        ret 4

; ---- routine 0791:BD83  (found by: call)
sub_BD83:
BD83  55              push bp
BD84  89 E5           mov bp, sp
BD86  83 EC 06        sub sp, 6
BD89  8A 46 04        mov al, byte ptr [bp + 4]
BD8C  98              cwde
BD8D  8B F8           mov di, ax
BD8F  D1 E7           shl di, 1
BD91  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
BD95  BA BF 00        mov dx, 0xbf
BD98  F7 E2           mul dx
BD9A  C4 3E 17 A9     les di, ptr [0xa917]
BD9E  03 F8           add di, ax
BDA0  89 7E FA        mov word ptr [bp - 6], di
BDA3  8C 46 FC        mov word ptr [bp - 4], es
BDA6  8A 46 04        mov al, byte ptr [bp + 4]
BDA9  98              cwde
BDAA  8B F8           mov di, ax
BDAC  D1 E7           shl di, 1
BDAE  FF B5 34 9B     push word ptr [di - 0x64cc]
BDB2  8A 46 04        mov al, byte ptr [bp + 4]
BDB5  98              cwde
BDB6  8B F8           mov di, ax
BDB8  D1 E7           shl di, 1
BDBA  8B BD 34 9B     mov di, word ptr [di - 0x64cc]
BDBE  8A 85 7C 9B     mov al, byte ptr [di - 0x6484]
BDC2  50              push ax
BDC3  E8 39 FE        call 0xbbff
BDC6  80 7E 04 01     cmp byte ptr [bp + 4], 1
BDCA  75 58           jne 0xbe24
BDCC  80 3E FC 80 00  cmp byte ptr [0x80fc], 0
BDD1  74 51           je 0xbe24
BDD3  8A 46 04        mov al, byte ptr [bp + 4]
BDD6  98              cwde
BDD7  8B F8           mov di, ax
BDD9  D1 E7           shl di, 1
BDDB  FF B5 34 9B     push word ptr [di - 0x64cc]
BDDF  80 7E 04 00     cmp byte ptr [bp + 4], 0
BDE3  74 04           je 0xbde9
BDE5  B0 00           mov al, 0
BDE7  EB 02           jmp 0xbdeb
loc_BDE9:
BDE9  B0 01           mov al, 1
loc_BDEB:
BDEB  98              cwde
BDEC  8B F8           mov di, ax
BDEE  D1 E7           shl di, 1
BDF0  FF B5 34 9B     push word ptr [di - 0x64cc]
BDF4  E8 0C FF        call 0xbd03
BDF7  08 C0           or al, al
BDF9  74 29           je 0xbe24
BDFB  B8 01 00        mov ax, 1
BDFE  50              push ax
BDFF  C4 7E FA        les di, ptr [bp - 6]
BE02  81 C7 2D 00     add di, 0x2d
BE06  06              push es
BE07  57              push di
BE08  9A 79 0C 4B 21  call far 214B:0C79
BE0D  8A 46 04        mov al, byte ptr [bp + 4]
BE10  98              cwde
BE11  8B F8           mov di, ax
BE13  D1 E7           shl di, 1
BE15  FF B5 34 9B     push word ptr [di - 0x64cc]
BE19  C4 7E FA        les di, ptr [bp - 6]
BE1C  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
BE20  50              push ax
BE21  E8 DB FD        call 0xbbff
loc_BE24:
BE24  8A 46 04        mov al, byte ptr [bp + 4]
BE27  98              cwde
BE28  8B F8           mov di, ax
BE2A  D1 E7           shl di, 1
BE2C  FF B5 34 9B     push word ptr [di - 0x64cc]
BE30  80 7E 04 00     cmp byte ptr [bp + 4], 0
BE34  74 04           je 0xbe3a
BE36  B0 00           mov al, 0
BE38  EB 02           jmp 0xbe3c
loc_BE3A:
BE3A  B0 01           mov al, 1
loc_BE3C:
BE3C  98              cwde
BE3D  8B F8           mov di, ax
BE3F  D1 E7           shl di, 1
BE41  FF B5 34 9B     push word ptr [di - 0x64cc]
BE45  E8 BB FE        call 0xbd03
BE48  08 C0           or al, al
BE4A  74 3F           je 0xbe8b
BE4C  C7 46 FE 01 00  mov word ptr [bp - 2], 1
BE51  EB 03           jmp 0xbe56
loc_BE53:
BE53  FF 46 FE        inc word ptr [bp - 2]
loc_BE56:
BE56  B8 06 00        mov ax, 6
BE59  50              push ax
BE5A  9A B1 06 4B 21  call far 214B:06B1
BE5F  50              push ax
BE60  C4 7E FA        les di, ptr [bp - 6]
BE63  81 C7 2D 00     add di, 0x2d
BE67  06              push es
BE68  57              push di
BE69  9A 79 0C 4B 21  call far 214B:0C79
BE6E  83 7E FE 02     cmp word ptr [bp - 2], 2
BE72  75 DF           jne 0xbe53
BE74  8A 46 04        mov al, byte ptr [bp + 4]
BE77  98              cwde
BE78  8B F8           mov di, ax
BE7A  D1 E7           shl di, 1
BE7C  FF B5 34 9B     push word ptr [di - 0x64cc]
BE80  C4 7E FA        les di, ptr [bp - 6]
BE83  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
BE87  50              push ax
BE88  E8 74 FD        call 0xbbff
loc_BE8B:
BE8B  8A 46 04        mov al, byte ptr [bp + 4]
BE8E  98              cwde
BE8F  8B F8           mov di, ax
BE91  C6 85 32 83 00  mov byte ptr [di - 0x7cce], 0
BE96  8A 46 04        mov al, byte ptr [bp + 4]
BE99  98              cwde
BE9A  8B F8           mov di, ax
BE9C  C6 85 34 83 00  mov byte ptr [di - 0x7ccc], 0
BEA1  89 EC           mov sp, bp
BEA3  5D              pop bp
BEA4  C2 02 00        ret 2
; data (not reached as code), 32 bytes
BEA7                  db 00 0E 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
BEB7                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:BEC7  (found by: call)
sub_BEC7:
BEC7  55              push bp
BEC8  89 E5           mov bp, sp
BECA  83 EC 02        sub sp, 2
BECD  C7 46 FE 01 00  mov word ptr [bp - 2], 1
BED2  EB 03           jmp 0xbed7
loc_BED4:
BED4  FF 46 FE        inc word ptr [bp - 2]
loc_BED7:
BED7  8B 46 FE        mov ax, word ptr [bp - 2]
BEDA  D1 E0           shl ax, 1
BEDC  C4 7E 04        les di, ptr [bp + 4]
BEDF  03 F8           add di, ax
BEE1  26 8B 45 FE     mov ax, word ptr es:[di - 2]
BEE5  BA 14 00        mov dx, 0x14
BEE8  F7 E2           mul dx
BEEA  C4 3E 1B A9     les di, ptr [0xa91b]
BEEE  03 F8           add di, ax
BEF0  26 8A 45 06     mov al, byte ptr es:[di + 6]
BEF4  50              push ax
BEF5  BF A7 BE        mov di, 0xbea7
BEF8  0E              push cs
BEF9  57              push di
BEFA  9A DF 08 E4 23  call far 23E4:08DF
BEFF  74 5B           je 0xbf5c
BF01  8B 46 FE        mov ax, word ptr [bp - 2]
BF04  D1 E0           shl ax, 1
BF06  C4 7E 04        les di, ptr [bp + 4]
BF09  03 F8           add di, ax
BF0B  26 FF 75 FE     push word ptr es:[di - 2]
BF0F  9A 16 32 71 17  call far 1771:3216
BF14  08 C0           or al, al
BF16  75 44           jne 0xbf5c
BF18  8B 46 FE        mov ax, word ptr [bp - 2]
BF1B  D1 E0           shl ax, 1
BF1D  C4 7E 04        les di, ptr [bp + 4]
BF20  03 F8           add di, ax
BF22  26 FF 75 FE     push word ptr es:[di - 2]
BF26  9A AD 2F 71 17  call far 1771:2FAD
BF2B  3D 48 00        cmp ax, 0x48
BF2E  73 04           jae 0xbf34
BF30  B0 00           mov al, 0
BF32  EB 02           jmp 0xbf36
loc_BF34:
BF34  B0 01           mov al, 1
loc_BF36:
BF36  98              cwde
BF37  8B F8           mov di, ax
BF39  8A 8D 28 0A     mov cl, byte ptr [di + 0xa28]
BF3D  8B 46 FE        mov ax, word ptr [bp - 2]
BF40  D1 E0           shl ax, 1
BF42  C4 7E 04        les di, ptr [bp + 4]
BF45  03 F8           add di, ax
BF47  26 8B 45 FE     mov ax, word ptr es:[di - 2]
BF4B  BA 14 00        mov dx, 0x14
BF4E  F7 E2           mul dx
BF50  C4 3E 1B A9     les di, ptr [0xa91b]
BF54  03 F8           add di, ax
BF56  26 88 4D 06     mov byte ptr es:[di + 6], cl
BF5A  EB 09           jmp 0xbf65
loc_BF5C:
BF5C  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
BF60  74 03           je 0xbf65
BF62  E9 6F FF        jmp 0xbed4
loc_BF65:
BF65  89 EC           mov sp, bp
BF67  5D              pop bp
BF68  C2 04 00        ret 4

; ---- routine 0791:BF6B  (found by: call)
sub_BF6B:
BF6B  55              push bp
BF6C  89 E5           mov bp, sp
BF6E  83 EC 06        sub sp, 6
BF71  8A 46 06        mov al, byte ptr [bp + 6]
BF74  98              cwde
BF75  8B F8           mov di, ax
BF77  D1 E7           shl di, 1
BF79  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
BF7D  BA BF 00        mov dx, 0xbf
BF80  F7 E2           mul dx
BF82  C4 3E 17 A9     les di, ptr [0xa917]
BF86  03 F8           add di, ax
BF88  89 7E FA        mov word ptr [bp - 6], di
BF8B  8C 46 FC        mov word ptr [bp - 4], es
BF8E  8A 46 06        mov al, byte ptr [bp + 6]
BF91  50              push ax
BF92  E8 EE FD        call 0xbd83
BF95  C7 46 FE 01 00  mov word ptr [bp - 2], 1
BF9A  EB 03           jmp 0xbf9f
loc_BF9C:
BF9C  FF 46 FE        inc word ptr [bp - 2]
loc_BF9F:
BF9F  80 7E 08 00     cmp byte ptr [bp + 8], 0
BFA3  74 1A           je 0xbfbf
BFA5  B8 06 00        mov ax, 6
BFA8  50              push ax
BFA9  9A B1 06 4B 21  call far 214B:06B1
BFAE  50              push ax
BFAF  C4 7E FA        les di, ptr [bp - 6]
BFB2  81 C7 2D 00     add di, 0x2d
BFB6  06              push es
BFB7  57              push di
BFB8  9A 79 0C 4B 21  call far 214B:0C79
BFBD  EB 18           jmp 0xbfd7
loc_BFBF:
BFBF  B8 06 00        mov ax, 6
BFC2  50              push ax
BFC3  9A B1 06 4B 21  call far 214B:06B1
BFC8  50              push ax
BFC9  C4 7E FA        les di, ptr [bp - 6]
BFCC  81 C7 2D 00     add di, 0x2d
BFD0  06              push es
BFD1  57              push di
BFD2  9A A1 0C 4B 21  call far 214B:0CA1
loc_BFD7:
BFD7  83 7E FE 03     cmp word ptr [bp - 2], 3
BFDB  75 BF           jne 0xbf9c
BFDD  8A 46 06        mov al, byte ptr [bp + 6]
BFE0  98              cwde
BFE1  8B F8           mov di, ax
BFE3  D1 E7           shl di, 1
BFE5  FF B5 34 9B     push word ptr [di - 0x64cc]
BFE9  C4 7E FA        les di, ptr [bp - 6]
BFEC  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
BFF0  50              push ax
BFF1  E8 0B FC        call 0xbbff
BFF4  89 EC           mov sp, bp
BFF6  5D              pop bp
BFF7  C2 06 00        ret 6
; data (not reached as code), 32 bytes
BFFA                  db 00 30 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; .0..............
C00A                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:C01A  (found by: call)
sub_C01A:
C01A  55              push bp
C01B  89 E5           mov bp, sp
C01D  83 EC 06        sub sp, 6
C020  8A 46 06        mov al, byte ptr [bp + 6]
C023  98              cwde
C024  8B F8           mov di, ax
C026  D1 E7           shl di, 1
C028  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
C02C  BA BF 00        mov dx, 0xbf
C02F  F7 E2           mul dx
C031  C4 3E 17 A9     les di, ptr [0xa917]
C035  03 F8           add di, ax
C037  89 7E FA        mov word ptr [bp - 6], di
C03A  8C 46 FC        mov word ptr [bp - 4], es
C03D  8A 46 06        mov al, byte ptr [bp + 6]
C040  98              cwde
C041  8B F8           mov di, ax
C043  80 BD 32 83 00  cmp byte ptr [di - 0x7cce], 0
C048  74 03           je 0xc04d
C04A  E9 8C 00        jmp 0xc0d9
loc_C04D:
C04D  C7 46 FE 01 00  mov word ptr [bp - 2], 1
C052  EB 03           jmp 0xc057
loc_C054:
C054  FF 46 FE        inc word ptr [bp - 2]
loc_C057:
C057  B8 05 00        mov ax, 5
C05A  50              push ax
C05B  9A B1 06 4B 21  call far 214B:06B1
C060  50              push ax
C061  C4 7E FA        les di, ptr [bp - 6]
C064  81 C7 2D 00     add di, 0x2d
C068  06              push es
C069  57              push di
C06A  9A 79 0C 4B 21  call far 214B:0C79
C06F  83 7E FE 05     cmp word ptr [bp - 2], 5
C073  75 DF           jne 0xc054
C075  B8 06 00        mov ax, 6
C078  50              push ax
C079  C4 7E FA        les di, ptr [bp - 6]
C07C  81 C7 2D 00     add di, 0x2d
C080  06              push es
C081  57              push di
C082  9A 79 0C 4B 21  call far 214B:0C79
C087  8A 46 06        mov al, byte ptr [bp + 6]
C08A  98              cwde
C08B  8B F8           mov di, ax
C08D  D1 E7           shl di, 1
C08F  FF B5 34 9B     push word ptr [di - 0x64cc]
C093  C4 7E FA        les di, ptr [bp - 6]
C096  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
C09A  50              push ax
C09B  E8 61 FB        call 0xbbff
C09E  8A 46 06        mov al, byte ptr [bp + 6]
C0A1  98              cwde
C0A2  8B F8           mov di, ax
C0A4  C6 85 32 83 01  mov byte ptr [di - 0x7cce], 1
C0A9  C4 7E FA        les di, ptr [bp - 6]
C0AC  26 8B 45 10     mov ax, word ptr es:[di + 0x10]
C0B0  BA 14 00        mov dx, 0x14
C0B3  F7 E2           mul dx
C0B5  C4 3E 1B A9     les di, ptr [0xa91b]
C0B9  03 F8           add di, ax
C0BB  26 8A 45 06     mov al, byte ptr es:[di + 6]
C0BF  50              push ax
C0C0  BF FA BF        mov di, 0xbffa
C0C3  0E              push cs
C0C4  57              push di
C0C5  9A DF 08 E4 23  call far 23E4:08DF
C0CA  74 02           je 0xc0ce
C0CC  EB 0B           jmp 0xc0d9
loc_C0CE:
C0CE  C4 7E FA        les di, ptr [bp - 6]
C0D1  06              push es
C0D2  57              push di
C0D3  E8 F1 FD        call 0xbec7
C0D6  E8 33 62        call 0x1230c
loc_C0D9:
C0D9  89 EC           mov sp, bp
C0DB  5D              pop bp
C0DC  C2 04 00        ret 4

; ---- routine 0791:C0DF  (found by: call)
sub_C0DF:
C0DF  55              push bp
C0E0  89 E5           mov bp, sp
C0E2  83 EC 06        sub sp, 6
C0E5  8A 46 06        mov al, byte ptr [bp + 6]
C0E8  98              cwde
C0E9  8B F8           mov di, ax
C0EB  D1 E7           shl di, 1
C0ED  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
C0F1  BA BF 00        mov dx, 0xbf
C0F4  F7 E2           mul dx
C0F6  C4 3E 17 A9     les di, ptr [0xa917]
C0FA  03 F8           add di, ax
C0FC  89 7E FA        mov word ptr [bp - 6], di
C0FF  8C 46 FC        mov word ptr [bp - 4], es
C102  8A 46 06        mov al, byte ptr [bp + 6]
C105  98              cwde
C106  8B F8           mov di, ax
C108  80 BD 34 83 00  cmp byte ptr [di - 0x7ccc], 0
C10D  74 02           je 0xc111
C10F  EB 5C           jmp 0xc16d
loc_C111:
C111  C7 46 FE 01 00  mov word ptr [bp - 2], 1
C116  EB 03           jmp 0xc11b
loc_C118:
C118  FF 46 FE        inc word ptr [bp - 2]
loc_C11B:
C11B  B8 05 00        mov ax, 5
C11E  50              push ax
C11F  9A B1 06 4B 21  call far 214B:06B1
C124  50              push ax
C125  C4 7E FA        les di, ptr [bp - 6]
C128  81 C7 2D 00     add di, 0x2d
C12C  06              push es
C12D  57              push di
C12E  9A A1 0C 4B 21  call far 214B:0CA1
C133  83 7E FE 05     cmp word ptr [bp - 2], 5
C137  75 DF           jne 0xc118
C139  B8 06 00        mov ax, 6
C13C  50              push ax
C13D  C4 7E FA        les di, ptr [bp - 6]
C140  81 C7 2D 00     add di, 0x2d
C144  06              push es
C145  57              push di
C146  9A A1 0C 4B 21  call far 214B:0CA1
C14B  8A 46 06        mov al, byte ptr [bp + 6]
C14E  98              cwde
C14F  8B F8           mov di, ax
C151  D1 E7           shl di, 1
C153  FF B5 34 9B     push word ptr [di - 0x64cc]
C157  C4 7E FA        les di, ptr [bp - 6]
C15A  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
C15E  50              push ax
C15F  E8 9D FA        call 0xbbff
C162  8A 46 06        mov al, byte ptr [bp + 6]
C165  98              cwde
C166  8B F8           mov di, ax
C168  C6 85 34 83 01  mov byte ptr [di - 0x7ccc], 1
loc_C16D:
C16D  89 EC           mov sp, bp
C16F  5D              pop bp
C170  C2 04 00        ret 4

; ---- routine 0791:C173  (found by: call)
sub_C173:
C173  55              push bp
C174  89 E5           mov bp, sp
C176  83 EC 02        sub sp, 2
C179  A0 3D 9B        mov al, byte ptr [0x9b3d]
C17C  98              cwde
C17D  8B D0           mov dx, ax
C17F  A0 3C 9B        mov al, byte ptr [0x9b3c]
C182  98              cwde
C183  2B C2           sub ax, dx
C185  88 46 FF        mov byte ptr [bp - 1], al
C188  C6 46 FE 00     mov byte ptr [bp - 2], 0
C18C  EB 03           jmp 0xc191
loc_C18E:
C18E  FE 46 FE        inc byte ptr [bp - 2]
loc_C191:
C191  8A 46 FE        mov al, byte ptr [bp - 2]
C194  98              cwde
C195  8B F8           mov di, ax
C197  D1 E7           shl di, 1
C199  FF B5 34 9B     push word ptr [di - 0x64cc]
C19D  9A 77 0B 71 17  call far 1771:0B77
C1A2  08 C0           or al, al
C1A4  74 03           je 0xc1a9
C1A6  E9 95 00        jmp 0xc23e
loc_C1A9:
C1A9  8A 46 FF        mov al, byte ptr [bp - 1]
C1AC  98              cwde
C1AD  09 C0           or ax, ax
C1AF  79 02           jns 0xc1b3
C1B1  F7 D8           neg ax
loc_C1B3:
C1B3  3D 02 00        cmp ax, 2
C1B6  7D 09           jge 0xc1c1
C1B8  8A 46 FE        mov al, byte ptr [bp - 2]
C1BB  50              push ax
C1BC  E8 C4 FB        call 0xbd83
C1BF  EB 7D           jmp 0xc23e
loc_C1C1:
C1C1  8A 46 FF        mov al, byte ptr [bp - 1]
C1C4  98              cwde
C1C5  09 C0           or ax, ax
C1C7  79 02           jns 0xc1cb
C1C9  F7 D8           neg ax
loc_C1CB:
C1CB  3D 02 00        cmp ax, 2
C1CE  75 3B           jne 0xc20b
C1D0  80 7E FE 00     cmp byte ptr [bp - 2], 0
C1D4  74 04           je 0xc1da
C1D6  B0 00           mov al, 0
C1D8  EB 02           jmp 0xc1dc
loc_C1DA:
C1DA  B0 01           mov al, 1
loc_C1DC:
C1DC  98              cwde
C1DD  8B F8           mov di, ax
C1DF  8A 95 3C 9B     mov dl, byte ptr [di - 0x64c4]
C1E3  8A 46 FE        mov al, byte ptr [bp - 2]
C1E6  98              cwde
C1E7  8B F8           mov di, ax
C1E9  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
C1ED  3A C2           cmp al, dl
C1EF  76 0D           jbe 0xc1fe
C1F1  B0 00           mov al, 0
C1F3  50              push ax
C1F4  8A 46 FE        mov al, byte ptr [bp - 2]
C1F7  50              push ax
C1F8  55              push bp
C1F9  E8 6F FD        call 0xbf6b
C1FC  EB 0B           jmp 0xc209
loc_C1FE:
C1FE  B0 01           mov al, 1
C200  50              push ax
C201  8A 46 FE        mov al, byte ptr [bp - 2]
C204  50              push ax
C205  55              push bp
C206  E8 62 FD        call 0xbf6b
loc_C209:
C209  EB 33           jmp 0xc23e
loc_C20B:
C20B  80 7E FE 00     cmp byte ptr [bp - 2], 0
C20F  74 04           je 0xc215
C211  B0 00           mov al, 0
C213  EB 02           jmp 0xc217
loc_C215:
C215  B0 01           mov al, 1
loc_C217:
C217  98              cwde
C218  8B F8           mov di, ax
C21A  8A 95 3C 9B     mov dl, byte ptr [di - 0x64c4]
C21E  8A 46 FE        mov al, byte ptr [bp - 2]
C221  98              cwde
C222  8B F8           mov di, ax
C224  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
C228  3A C2           cmp al, dl
C22A  76 0A           jbe 0xc236
C22C  8A 46 FE        mov al, byte ptr [bp - 2]
C22F  50              push ax
C230  55              push bp
C231  E8 AB FE        call 0xc0df
C234  EB 08           jmp 0xc23e
loc_C236:
C236  8A 46 FE        mov al, byte ptr [bp - 2]
C239  50              push ax
C23A  55              push bp
C23B  E8 DC FD        call 0xc01a
loc_C23E:
C23E  80 7E FE 01     cmp byte ptr [bp - 2], 1
C242  74 03           je 0xc247
C244  E9 47 FF        jmp 0xc18e
loc_C247:
C247  89 EC           mov sp, bp
C249  5D              pop bp
C24A  C2 02 00        ret 2

