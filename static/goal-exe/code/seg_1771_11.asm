; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 11 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:76B1  (found by: far)
sub_76B1:
76B1  55              push bp
76B2  89 E5           mov bp, sp
76B4  C4 3E 23 A9     les di, ptr [0xa923]
76B8  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
76BC  3C 02           cmp al, 2
76BE  74 04           je 0x76c4
76C0  3C 05           cmp al, 5
76C2  75 05           jne 0x76c9
loc_76C4:
76C4  E8 69 F0        call 0x6730
76C7  EB 2B           jmp 0x76f4
loc_76C9:
76C9  3C 03           cmp al, 3
76CB  75 05           jne 0x76d2
76CD  E8 85 F4        call 0x6b55
76D0  EB 22           jmp 0x76f4
loc_76D2:
76D2  3C 04           cmp al, 4
76D4  75 05           jne 0x76db
76D6  E8 80 F7        call 0x6e59
76D9  EB 19           jmp 0x76f4
loc_76DB:
76DB  3C 06           cmp al, 6
76DD  75 05           jne 0x76e4
76DF  E8 AE F9        call 0x7090
76E2  EB 10           jmp 0x76f4
loc_76E4:
76E4  3C 07           cmp al, 7
76E6  75 05           jne 0x76ed
76E8  E8 C7 FA        call 0x71b2
76EB  EB 07           jmp 0x76f4
loc_76ED:
76ED  3C 08           cmp al, 8
76EF  75 03           jne 0x76f4
76F1  E8 CA FD        call 0x74be
loc_76F4:
76F4  89 EC           mov sp, bp
76F6  5D              pop bp
76F7  CB              retf
; data (not reached as code), 2 bytes
76F8                  db 01 76   ; .v

; ---- routine 1771:76FA  (found by: call)
sub_76FA:
76FA  55              push bp
76FB  89 E5           mov bp, sp
76FD  81 EC 04 01     sub sp, 0x104
7701  C4 7E 0A        les di, ptr [bp + 0xa]
7704  89 7E FC        mov word ptr [bp - 4], di
7707  8C 46 FE        mov word ptr [bp - 2], es
770A  B0 05           mov al, 5
770C  50              push ax
770D  BF F8 76        mov di, 0x76f8
7710  0E              push cs
7711  57              push di
7712  8A 46 08        mov al, byte ptr [bp + 8]
7715  50              push ax
7716  8A 46 06        mov al, byte ptr [bp + 6]
7719  50              push ax
771A  BF 6E A9        mov di, 0xa96e
771D  1E              push ds
771E  57              push di
771F  9A C8 02 4B 21  call far 214B:02C8
7724  C4 7E FC        les di, ptr [bp - 4]
7727  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
772C  75 03           jne 0x7731
772E  E9 8C 00        jmp 0x77bd
loc_7731:
7731  C4 7E FC        les di, ptr [bp - 4]
7734  26 80 3D FE     cmp byte ptr es:[di], 0xfe
7738  72 03           jb 0x773d
773A  E9 80 00        jmp 0x77bd
loc_773D:
773D  C4 7E FC        les di, ptr [bp - 4]
7740  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
7745  75 07           jne 0x774e
7747  C6 06 B2 AA 06  mov byte ptr [0xaab2], 6
774C  EB 1A           jmp 0x7768
loc_774E:
774E  C4 7E FC        les di, ptr [bp - 4]
7751  26 80 7D 03 01  cmp byte ptr es:[di + 3], 1
7756  74 04           je 0x775c
7758  B0 00           mov al, 0
775A  EB 02           jmp 0x775e
loc_775C:
775C  B0 01           mov al, 1
loc_775E:
775E  98              cwde
775F  8B F8           mov di, ax
7761  8A 85 08 11     mov al, byte ptr [di + 0x1108]
7765  A2 B2 AA        mov byte ptr [0xaab2], al
loc_7768:
7768  8D BE FC FE     lea di, [bp - 0x104]
776C  16              push ss
776D  57              push di
776E  C4 7E FC        les di, ptr [bp - 4]
7771  26 8A 45 01     mov al, byte ptr es:[di + 1]
7775  30 E4           xor ah, ah
7777  31 D2           xor dx, dx
7779  52              push dx
777A  50              push ax
777B  9A DA 09 4B 21  call far 214B:09DA
7780  8A 46 08        mov al, byte ptr [bp + 8]
7783  50              push ax
7784  8B 46 06        mov ax, word ptr [bp + 6]
7787  48              dec ax
7788  50              push ax
7789  BF 6E A9        mov di, 0xa96e
778C  1E              push ds
778D  57              push di
778E  9A A3 01 4B 21  call far 214B:01A3
7793  8D BE FC FE     lea di, [bp - 0x104]
7797  16              push ss
7798  57              push di
7799  C4 7E FC        les di, ptr [bp - 4]
779C  26 8A 05        mov al, byte ptr es:[di]
779F  30 E4           xor ah, ah
77A1  31 D2           xor dx, dx
77A3  52              push dx
77A4  50              push ax
77A5  9A DA 09 4B 21  call far 214B:09DA
77AA  8A 46 08        mov al, byte ptr [bp + 8]
77AD  50              push ax
77AE  8B 46 06        mov ax, word ptr [bp + 6]
77B1  40              inc ax
77B2  50              push ax
77B3  BF 6E A9        mov di, 0xa96e
77B6  1E              push ds
77B7  57              push di
77B8  9A 6D 02 4B 21  call far 214B:026D
loc_77BD:
77BD  89 EC           mov sp, bp
77BF  5D              pop bp
77C0  CA 08 00        retf 8

; ---- routine 1771:77C3  (found by: call)
sub_77C3:
77C3  55              push bp
77C4  89 E5           mov bp, sp
77C6  83 EC 04        sub sp, 4
77C9  C4 7E 08        les di, ptr [bp + 8]
77CC  89 7E FC        mov word ptr [bp - 4], di
77CF  8C 46 FE        mov word ptr [bp - 2], es
77D2  C4 7E FC        les di, ptr [bp - 4]
77D5  26 FF 75 06     push word ptr es:[di + 6]
77D9  FF 76 06        push word ptr [bp + 6]
77DC  8B 46 04        mov ax, word ptr [bp + 4]
77DF  2D 04 00        sub ax, 4
77E2  50              push ax
77E3  E8 CB 97        call 0xfb1
77E6  C4 7E FC        les di, ptr [bp - 4]
77E9  26 FF 75 04     push word ptr es:[di + 4]
77ED  FF 76 06        push word ptr [bp + 6]
77F0  8B 46 04        mov ax, word ptr [bp + 4]
77F3  05 04 00        add ax, 4
77F6  50              push ax
77F7  0E              push cs
77F8  E8 5D 97        call 0xf58
77FB  C4 7E 08        les di, ptr [bp + 8]
77FE  06              push es
77FF  57              push di
7800  FF 76 06        push word ptr [bp + 6]
7803  FF 76 04        push word ptr [bp + 4]
7806  0E              push cs
7807  E8 F0 FE        call 0x76fa
780A  89 EC           mov sp, bp
780C  5D              pop bp
780D  C2 08 00        ret 8
; data (not reached as code), 2 bytes
7810                  db 01 FB   ; ..

; ---- routine 1771:7812  (found by: call, far)
sub_7812:
7812  55              push bp
7813  89 E5           mov bp, sp
7815  81 EC 04 01     sub sp, 0x104
7819  C4 7E 0A        les di, ptr [bp + 0xa]
781C  89 7E FC        mov word ptr [bp - 4], di
781F  8C 46 FE        mov word ptr [bp - 2], es
7822  C4 7E FC        les di, ptr [bp - 4]
7825  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
782A  75 07           jne 0x7833
782C  C6 06 B2 AA 06  mov byte ptr [0xaab2], 6
7831  EB 1A           jmp 0x784d
loc_7833:
7833  C4 7E FC        les di, ptr [bp - 4]
7836  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
783B  74 04           je 0x7841
783D  B0 00           mov al, 0
783F  EB 02           jmp 0x7843
loc_7841:
7841  B0 01           mov al, 1
loc_7843:
7843  98              cwde
7844  8B F8           mov di, ax
7846  8A 85 0A 11     mov al, byte ptr [di + 0x110a]
784A  A2 B2 AA        mov byte ptr [0xaab2], al
loc_784D:
784D  8D BE FC FE     lea di, [bp - 0x104]
7851  16              push ss
7852  57              push di
7853  C4 7E FC        les di, ptr [bp - 4]
7856  26 8A 45 02     mov al, byte ptr es:[di + 2]
785A  30 E4           xor ah, ah
785C  50              push ax
785D  0E              push cs
785E  E8 AA DF        call 0x580b
7861  8A 46 08        mov al, byte ptr [bp + 8]
7864  50              push ax
7865  8B 46 06        mov ax, word ptr [bp + 6]
7868  05 16 00        add ax, 0x16
786B  50              push ax
786C  BF 6E A9        mov di, 0xa96e
786F  1E              push ds
7870  57              push di
7871  9A 6D 02 4B 21  call far 214B:026D
7876  C4 7E 0A        les di, ptr [bp + 0xa]
7879  06              push es
787A  57              push di
787B  FF 76 08        push word ptr [bp + 8]
787E  FF 76 06        push word ptr [bp + 6]
7881  E8 3F FF        call 0x77c3
7884  C4 7E FC        les di, ptr [bp - 4]
7887  26 80 3D FE     cmp byte ptr es:[di], 0xfe
788B  75 27           jne 0x78b4
788D  C4 7E FC        les di, ptr [bp - 4]
7890  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
7895  74 1D           je 0x78b4
7897  B0 0E           mov al, 0xe
7899  50              push ax
789A  BF 10 78        mov di, 0x7810
789D  0E              push cs
789E  57              push di
789F  8A 46 08        mov al, byte ptr [bp + 8]
78A2  50              push ax
78A3  8B 46 06        mov ax, word ptr [bp + 6]
78A6  05 23 00        add ax, 0x23
78A9  50              push ax
78AA  BF 6E A9        mov di, 0xa96e
78AD  1E              push ds
78AE  57              push di
78AF  9A C8 02 4B 21  call far 214B:02C8
loc_78B4:
78B4  89 EC           mov sp, bp
78B6  5D              pop bp
78B7  CA 08 00        retf 8

; ---- routine 1771:78BA  (found by: call)
sub_78BA:
78BA  55              push bp
78BB  89 E5           mov bp, sp
78BD  83 EC 02        sub sp, 2
78C0  C7 46 FE 01 00  mov word ptr [bp - 2], 1
78C5  EB 03           jmp 0x78ca
loc_78C7:
78C7  FF 46 FE        inc word ptr [bp - 2]
loc_78CA:
78CA  8B 46 FE        mov ax, word ptr [bp - 2]
78CD  D1 E0           shl ax, 1
78CF  8B C8           mov cx, ax
78D1  8B 46 06        mov ax, word ptr [bp + 6]
78D4  BA 48 00        mov dx, 0x48
78D7  F7 E2           mul dx
78D9  C4 3E 2F A9     les di, ptr [0xa92f]
78DD  03 F8           add di, ax
78DF  03 F9           add di, cx
78E1  26 8B 45 FE     mov ax, word ptr es:[di - 2]
78E5  8B 7E 04        mov di, word ptr [bp + 4]
78E8  36 3B 45 F6     cmp ax, word ptr ss:[di - 0xa]
78EC  75 45           jne 0x7933
78EE  8B 46 06        mov ax, word ptr [bp + 6]
78F1  BA 48 00        mov dx, 0x48
78F4  F7 E2           mul dx
78F6  C4 3E 2F A9     les di, ptr [0xa92f]
78FA  03 F8           add di, ax
78FC  06              push es
78FD  57              push di
78FE  8B 46 06        mov ax, word ptr [bp + 6]
7901  BA 48 00        mov dx, 0x48
7904  F7 E2           mul dx
7906  C4 3E 2F A9     les di, ptr [0xa92f]
790A  03 F8           add di, ax
790C  81 C7 02 00     add di, 2
7910  06              push es
7911  57              push di
7912  8B 46 FE        mov ax, word ptr [bp - 2]
7915  48              dec ax
7916  D1 E0           shl ax, 1
7918  50              push ax
7919  9A 3C 00 4B 21  call far 214B:003C
791E  8B 46 06        mov ax, word ptr [bp + 6]
7921  BA 48 00        mov dx, 0x48
7924  F7 E2           mul dx
7926  C4 3E 2F A9     les di, ptr [0xa92f]
792A  03 F8           add di, ax
792C  31 C0           xor ax, ax
792E  26 89 05        mov word ptr es:[di], ax
7931  EB 06           jmp 0x7939
loc_7933:
7933  83 7E FE 24     cmp word ptr [bp - 2], 0x24
7937  75 8E           jne 0x78c7
loc_7939:
7939  89 EC           mov sp, bp
793B  5D              pop bp
793C  C2 04 00        ret 4

; ---- routine 1771:793F  (found by: call)
sub_793F:
793F  55              push bp
7940  89 E5           mov bp, sp
7942  83 EC 04        sub sp, 4
7945  A1 66 9B        mov ax, word ptr [0x9b66]
7948  BA 48 00        mov dx, 0x48
794B  F7 E2           mul dx
794D  C4 3E 2F A9     les di, ptr [0xa92f]
7951  03 F8           add di, ax
7953  81 C7 02 00     add di, 2
7957  06              push es
7958  57              push di
7959  A1 66 9B        mov ax, word ptr [0x9b66]
795C  BA 48 00        mov dx, 0x48
795F  F7 E2           mul dx
7961  C4 3E 2F A9     les di, ptr [0xa92f]
7965  03 F8           add di, ax
7967  06              push es
7968  57              push di
7969  B8 47 00        mov ax, 0x47
796C  50              push ax
796D  9A 3C 00 4B 21  call far 214B:003C
7972  8B 7E 04        mov di, word ptr [bp + 4]
7975  36 8B 4D F6     mov cx, word ptr ss:[di - 0xa]
7979  A1 66 9B        mov ax, word ptr [0x9b66]
797C  BA 48 00        mov dx, 0x48
797F  F7 E2           mul dx
7981  C4 3E 2F A9     les di, ptr [0xa92f]
7985  03 F8           add di, ax
7987  26 89 4D 46     mov word ptr es:[di + 0x46], cx
798B  C7 46 FE 24 00  mov word ptr [bp - 2], 0x24
loc_7990:
7990  83 7E FE 01     cmp word ptr [bp - 2], 1
7994  77 03           ja 0x7999
7996  E9 DD 00        jmp 0x7a76
loc_7999:
7999  8B 46 FE        mov ax, word ptr [bp - 2]
799C  48              dec ax
799D  D1 E0           shl ax, 1
799F  8B C8           mov cx, ax
79A1  A1 66 9B        mov ax, word ptr [0x9b66]
79A4  BA 48 00        mov dx, 0x48
79A7  F7 E2           mul dx
79A9  C4 3E 2F A9     les di, ptr [0xa92f]
79AD  03 F8           add di, ax
79AF  03 F9           add di, cx
79B1  26 8B 5D FE     mov bx, word ptr es:[di - 2]
79B5  8B 46 FE        mov ax, word ptr [bp - 2]
79B8  D1 E0           shl ax, 1
79BA  8B C8           mov cx, ax
79BC  A1 66 9B        mov ax, word ptr [0x9b66]
79BF  BA 48 00        mov dx, 0x48
79C2  F7 E2           mul dx
79C4  C4 3E 2F A9     les di, ptr [0xa92f]
79C8  03 F8           add di, ax
79CA  03 F9           add di, cx
79CC  26 8B 45 FE     mov ax, word ptr es:[di - 2]
79D0  3B C3           cmp ax, bx
79D2  72 03           jb 0x79d7
79D4  E9 9F 00        jmp 0x7a76
loc_79D7:
79D7  8B 46 FE        mov ax, word ptr [bp - 2]
79DA  48              dec ax
79DB  D1 E0           shl ax, 1
79DD  8B C8           mov cx, ax
79DF  A1 66 9B        mov ax, word ptr [0x9b66]
79E2  BA 48 00        mov dx, 0x48
79E5  F7 E2           mul dx
79E7  C4 3E 2F A9     les di, ptr [0xa92f]
79EB  03 F8           add di, ax
79ED  03 F9           add di, cx
79EF  26 8B 45 FE     mov ax, word ptr es:[di - 2]
79F3  3B 06 38 69     cmp ax, word ptr [0x6938]
79F7  73 04           jae 0x79fd
79F9  B0 00           mov al, 0
79FB  EB 02           jmp 0x79ff
loc_79FD:
79FD  B0 01           mov al, 1
loc_79FF:
79FF  8A D8           mov bl, al
7A01  8B 46 FE        mov ax, word ptr [bp - 2]
7A04  D1 E0           shl ax, 1
7A06  8B C8           mov cx, ax
7A08  A1 66 9B        mov ax, word ptr [0x9b66]
7A0B  BA 48 00        mov dx, 0x48
7A0E  F7 E2           mul dx
7A10  C4 3E 2F A9     les di, ptr [0xa92f]
7A14  03 F8           add di, ax
7A16  03 F9           add di, cx
7A18  26 8B 45 FE     mov ax, word ptr es:[di - 2]
7A1C  3B 06 38 69     cmp ax, word ptr [0x6938]
7A20  73 04           jae 0x7a26
7A22  B0 00           mov al, 0
7A24  EB 02           jmp 0x7a28
loc_7A26:
7A26  B0 01           mov al, 1
loc_7A28:
7A28  3A C3           cmp al, bl
7A2A  75 4A           jne 0x7a76
7A2C  8B 46 FE        mov ax, word ptr [bp - 2]
7A2F  D1 E0           shl ax, 1
7A31  8B C8           mov cx, ax
7A33  A1 66 9B        mov ax, word ptr [0x9b66]
7A36  BA 48 00        mov dx, 0x48
7A39  F7 E2           mul dx
7A3B  C4 3E 2F A9     les di, ptr [0xa92f]
7A3F  03 F8           add di, ax
7A41  03 F9           add di, cx
7A43  81 C7 FE FF     add di, 0xfffe
7A47  06              push es
7A48  57              push di
7A49  8B 46 FE        mov ax, word ptr [bp - 2]
7A4C  48              dec ax
7A4D  D1 E0           shl ax, 1
7A4F  8B C8           mov cx, ax
7A51  A1 66 9B        mov ax, word ptr [0x9b66]
7A54  BA 48 00        mov dx, 0x48
7A57  F7 E2           mul dx
7A59  C4 3E 2F A9     les di, ptr [0xa92f]
7A5D  03 F8           add di, ax
7A5F  03 F9           add di, cx
7A61  81 C7 FE FF     add di, 0xfffe
7A65  06              push es
7A66  57              push di
7A67  B8 02 00        mov ax, 2
7A6A  50              push ax
7A6B  9A 7B 00 4B 21  call far 214B:007B
7A70  FF 4E FE        dec word ptr [bp - 2]
7A73  E9 1A FF        jmp 0x7990
loc_7A76:
7A76  89 EC           mov sp, bp
7A78  5D              pop bp
7A79  C2 02 00        ret 2
; data (not reached as code), 30 bytes
7A7C                  pstr ' have too many games arranged'

; ---- routine 1771:7A9A  (found by: call)
sub_7A9A:
7A9A  55              push bp
7A9B  89 E5           mov bp, sp
7A9D  81 EC 00 01     sub sp, 0x100
7AA1  31 C0           xor ax, ax
7AA3  A3 66 9B        mov word ptr [0x9b66], ax
7AA6  B8 04 00        mov ax, 4
7AA9  50              push ax
7AAA  0E              push cs
7AAB  E8 0B AC        call 0x26b9
7AAE  83 3E 66 9B 00  cmp word ptr [0x9b66], 0
7AB3  74 62           je 0x7b17
7AB5  A1 66 9B        mov ax, word ptr [0x9b66]
7AB8  8B 7E 04        mov di, word ptr [bp + 4]
7ABB  36 3B 45 06     cmp ax, word ptr ss:[di + 6]
7ABF  74 56           je 0x7b17
7AC1  A1 66 9B        mov ax, word ptr [0x9b66]
7AC4  BA 48 00        mov dx, 0x48
7AC7  F7 E2           mul dx
7AC9  C4 3E 2F A9     les di, ptr [0xa92f]
7ACD  03 F8           add di, ax
7ACF  26 8B 05        mov ax, word ptr es:[di]
7AD2  B1 03           mov cl, 3
7AD4  D3 E0           shl ax, cl
7AD6  C4 3E 2B A9     les di, ptr [0xa92b]
7ADA  03 F8           add di, ax
7ADC  26 80 7D F8 FE  cmp byte ptr es:[di - 8], 0xfe
7AE1  73 04           jae 0x7ae7
7AE3  B0 00           mov al, 0
7AE5  EB 02           jmp 0x7ae9
loc_7AE7:
7AE7  B0 01           mov al, 1
loc_7AE9:
7AE9  50              push ax
7AEA  8D BE 00 FF     lea di, [bp - 0x100]
7AEE  16              push ss
7AEF  57              push di
7AF0  A1 66 9B        mov ax, word ptr [0x9b66]
7AF3  B1 04           mov cl, 4
7AF5  D3 E0           shl ax, cl
7AF7  C4 3E 68 9B     les di, ptr [0x9b68]
7AFB  03 F8           add di, ax
7AFD  06              push es
7AFE  57              push di
7AFF  9A 2A 06 E4 23  call far 23E4:062A
7B04  BF 7C 7A        mov di, 0x7a7c
7B07  0E              push cs
7B08  57              push di
7B09  9A B7 06 E4 23  call far 23E4:06B7
7B0E  9A 65 17 4B 21  call far 214B:1765
7B13  08 C0           or al, al
7B15  74 03           je 0x7b1a
loc_7B17:
7B17  E9 82 00        jmp 0x7b9c
loc_7B1A:
7B1A  8B 7E 04        mov di, word ptr [bp + 4]
7B1D  36 8B 45 F6     mov ax, word ptr ss:[di - 0xa]
7B21  B1 03           mov cl, 3
7B23  D3 E0           shl ax, cl
7B25  C4 3E 2B A9     les di, ptr [0xa92b]
7B29  03 F8           add di, ax
7B2B  81 C7 F8 FF     add di, 0xfff8
7B2F  89 7E FC        mov word ptr [bp - 4], di
7B32  8C 46 FE        mov word ptr [bp - 2], es
7B35  C4 7E FC        les di, ptr [bp - 4]
7B38  26 C6 45 02 01  mov byte ptr es:[di + 2], 1
7B3D  C4 7E FC        les di, ptr [bp - 4]
7B40  26 8B 45 06     mov ax, word ptr es:[di + 6]
7B44  8B 7E 04        mov di, word ptr [bp + 4]
7B47  36 3B 45 06     cmp ax, word ptr ss:[di + 6]
7B4B  75 0F           jne 0x7b5c
7B4D  C4 7E FC        les di, ptr [bp - 4]
7B50  26 FF 75 04     push word ptr es:[di + 4]
7B54  FF 76 04        push word ptr [bp + 4]
7B57  E8 60 FD        call 0x78ba
7B5A  EB 0D           jmp 0x7b69
loc_7B5C:
7B5C  C4 7E FC        les di, ptr [bp - 4]
7B5F  26 FF 75 06     push word ptr es:[di + 6]
7B63  FF 76 04        push word ptr [bp + 4]
7B66  E8 51 FD        call 0x78ba
loc_7B69:
7B69  FF 76 04        push word ptr [bp + 4]
7B6C  E8 D0 FD        call 0x793f
7B6F  C4 7E FC        les di, ptr [bp - 4]
7B72  26 8B 45 06     mov ax, word ptr es:[di + 6]
7B76  8B 7E 04        mov di, word ptr [bp + 4]
7B79  36 3B 45 06     cmp ax, word ptr ss:[di + 6]
7B7D  74 0C           je 0x7b8b
7B7F  A1 66 9B        mov ax, word ptr [0x9b66]
7B82  C4 7E FC        les di, ptr [bp - 4]
7B85  26 89 45 06     mov word ptr es:[di + 6], ax
7B89  EB 0A           jmp 0x7b95
loc_7B8B:
7B8B  A1 66 9B        mov ax, word ptr [0x9b66]
7B8E  C4 7E FC        les di, ptr [bp - 4]
7B91  26 89 45 04     mov word ptr es:[di + 4], ax
loc_7B95:
7B95  C4 7E FC        les di, ptr [bp - 4]
7B98  26 C6 05 FE     mov byte ptr es:[di], 0xfe
loc_7B9C:
7B9C  89 EC           mov sp, bp
7B9E  5D              pop bp
7B9F  C2 02 00        ret 2

; ---- routine 1771:7BA2  (found by: call)
sub_7BA2:
7BA2  55              push bp
7BA3  89 E5           mov bp, sp
7BA5  83 EC 18        sub sp, 0x18
7BA8  C4 3E 23 A9     les di, ptr [0xa923]
7BAC  89 7E F0        mov word ptr [bp - 0x10], di
7BAF  8C 46 F2        mov word ptr [bp - 0xe], es
7BB2  8B 46 06        mov ax, word ptr [bp + 6]
7BB5  BA BF 00        mov dx, 0xbf
7BB8  F7 E2           mul dx
7BBA  C4 3E 17 A9     les di, ptr [0xa917]
7BBE  03 F8           add di, ax
7BC0  89 7E EC        mov word ptr [bp - 0x14], di
7BC3  8C 46 EE        mov word ptr [bp - 0x12], es
7BC6  C7 46 F8 01 00  mov word ptr [bp - 8], 1
7BCB  C7 46 FA 15 00  mov word ptr [bp - 6], 0x15
loc_7BD0:
7BD0  8B 46 FA        mov ax, word ptr [bp - 6]
7BD3  D1 E0           shl ax, 1
7BD5  8B C8           mov cx, ax
7BD7  8B 46 06        mov ax, word ptr [bp + 6]
7BDA  BA 48 00        mov dx, 0x48
7BDD  F7 E2           mul dx
7BDF  C4 3E 2F A9     les di, ptr [0xa92f]
7BE3  03 F8           add di, ax
7BE5  03 F9           add di, cx
7BE7  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
7BEC  75 05           jne 0x7bf3
7BEE  FF 46 FA        inc word ptr [bp - 6]
7BF1  EB DD           jmp 0x7bd0
loc_7BF3:
7BF3  8B 46 FA        mov ax, word ptr [bp - 6]
7BF6  03 46 F8        add ax, word ptr [bp - 8]
7BF9  48              dec ax
7BFA  D1 E0           shl ax, 1
7BFC  8B C8           mov cx, ax
7BFE  8B 46 06        mov ax, word ptr [bp + 6]
7C01  BA 48 00        mov dx, 0x48
7C04  F7 E2           mul dx
7C06  C4 3E 2F A9     les di, ptr [0xa92f]
7C0A  03 F8           add di, ax
7C0C  03 F9           add di, cx
7C0E  26 8B 45 FE     mov ax, word ptr es:[di - 2]
7C12  89 46 F6        mov word ptr [bp - 0xa], ax
7C15  C7 46 FE 08 00  mov word ptr [bp - 2], 8
7C1A  BF AC 20        mov di, 0x20ac
7C1D  1E              push ds
7C1E  57              push di
7C1F  BF 6E A9        mov di, 0xa96e
7C22  1E              push ds
7C23  57              push di
7C24  9A 29 03 4B 21  call far 214B:0329
7C29  BF 96 57        mov di, 0x5796
7C2C  1E              push ds
7C2D  57              push di
7C2E  BF 6E A9        mov di, 0xa96e
7C31  1E              push ds
7C32  57              push di
7C33  9A 29 03 4B 21  call far 214B:0329
7C38  BF F6 1A        mov di, 0x1af6
7C3B  1E              push ds
7C3C  57              push di
7C3D  BF 6E A9        mov di, 0xa96e
7C40  1E              push ds
7C41  57              push di
7C42  9A 29 03 4B 21  call far 214B:0329
7C47  8B 46 F6        mov ax, word ptr [bp - 0xa]
7C4A  B1 03           mov cl, 3
7C4C  D3 E0           shl ax, cl
7C4E  C4 3E 2B A9     les di, ptr [0xa92b]
7C52  03 F8           add di, ax
7C54  81 C7 F8 FF     add di, 0xfff8
7C58  89 7E E8        mov word ptr [bp - 0x18], di
7C5B  8C 46 EA        mov word ptr [bp - 0x16], es
7C5E  C4 7E E8        les di, ptr [bp - 0x18]
7C61  26 FF 75 06     push word ptr es:[di + 6]
7C65  0E              push cs
7C66  E8 0E 8F        call 0xb77
7C69  08 C0           or al, al
7C6B  75 13           jne 0x7c80
7C6D  C4 7E E8        les di, ptr [bp - 0x18]
7C70  26 FF 75 04     push word ptr es:[di + 4]
7C74  0E              push cs
7C75  E8 FF 8E        call 0xb77
7C78  08 C0           or al, al
7C7A  75 04           jne 0x7c80
7C7C  B0 00           mov al, 0
7C7E  EB 02           jmp 0x7c82
loc_7C80:
7C80  B0 01           mov al, 1
loc_7C82:
7C82  88 46 F5        mov byte ptr [bp - 0xb], al
7C85  FF 76 06        push word ptr [bp + 6]
7C88  0E              push cs
7C89  E8 EB 8E        call 0xb77
7C8C  08 C0           or al, al
7C8E  74 3F           je 0x7ccf
7C90  C4 7E E8        les di, ptr [bp - 0x18]
7C93  26 80 3D FE     cmp byte ptr es:[di], 0xfe
7C97  72 34           jb 0x7ccd
7C99  C4 7E E8        les di, ptr [bp - 0x18]
7C9C  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
7CA1  75 11           jne 0x7cb4
7CA3  BF F2 1F        mov di, 0x1ff2
7CA6  1E              push ds
7CA7  57              push di
7CA8  BF 6E A9        mov di, 0xa96e
7CAB  1E              push ds
7CAC  57              push di
7CAD  9A 29 03 4B 21  call far 214B:0329
7CB2  EB 19           jmp 0x7ccd
loc_7CB4:
7CB4  C4 7E E8        les di, ptr [bp - 0x18]
7CB7  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
7CBC  75 0F           jne 0x7ccd
7CBE  BF 20 20        mov di, 0x2020
7CC1  1E              push ds
7CC2  57              push di
7CC3  BF 6E A9        mov di, 0xa96e
7CC6  1E              push ds
7CC7  57              push di
7CC8  9A 29 03 4B 21  call far 214B:0329
loc_7CCD:
7CCD  EB 38           jmp 0x7d07
loc_7CCF:
7CCF  80 7E F5 00     cmp byte ptr [bp - 0xb], 0
7CD3  75 32           jne 0x7d07
7CD5  C4 7E E8        les di, ptr [bp - 0x18]
7CD8  26 80 3D FE     cmp byte ptr es:[di], 0xfe
7CDC  75 11           jne 0x7cef
7CDE  BF 7E 20        mov di, 0x207e
7CE1  1E              push ds
7CE2  57              push di
7CE3  BF 6E A9        mov di, 0xa96e
7CE6  1E              push ds
7CE7  57              push di
7CE8  9A 29 03 4B 21  call far 214B:0329
7CED  EB 18           jmp 0x7d07
loc_7CEF:
7CEF  C4 7E E8        les di, ptr [bp - 0x18]
7CF2  26 80 3D FF     cmp byte ptr es:[di], 0xff
7CF6  75 0F           jne 0x7d07
7CF8  BF 50 20        mov di, 0x2050
7CFB  1E              push ds
7CFC  57              push di
7CFD  BF 6E A9        mov di, 0xa96e
7D00  1E              push ds
7D01  57              push di
7D02  9A 29 03 4B 21  call far 214B:0329
loc_7D07:
7D07  B8 24 00        mov ax, 0x24
7D0A  31 D2           xor dx, dx
7D0C  52              push dx
7D0D  50              push ax
7D0E  8B 46 FA        mov ax, word ptr [bp - 6]
7D11  05 0F 00        add ax, 0xf
7D14  31 D2           xor dx, dx
7D16  52              push dx
7D17  50              push ax
7D18  9A 1C 0D 4B 21  call far 214B:0D1C
7D1D  89 46 EA        mov word ptr [bp - 0x16], ax
7D20  8B 46 FA        mov ax, word ptr [bp - 6]
7D23  3B 46 EA        cmp ax, word ptr [bp - 0x16]
7D26  77 49           ja 0x7d71
7D28  89 46 FC        mov word ptr [bp - 4], ax
7D2B  EB 03           jmp 0x7d30
loc_7D2D:
7D2D  FF 46 FC        inc word ptr [bp - 4]
loc_7D30:
7D30  8B 46 FC        mov ax, word ptr [bp - 4]
7D33  D1 E0           shl ax, 1
7D35  8B C8           mov cx, ax
7D37  8B 46 06        mov ax, word ptr [bp + 6]
7D3A  BA 48 00        mov dx, 0x48
7D3D  F7 E2           mul dx
7D3F  C4 3E 2F A9     les di, ptr [0xa92f]
7D43  03 F8           add di, ax
7D45  03 F9           add di, cx
7D47  26 8B 45 FE     mov ax, word ptr es:[di - 2]
7D4B  B1 03           mov cl, 3
7D4D  D3 E0           shl ax, cl
7D4F  C4 3E 2B A9     les di, ptr [0xa92b]
7D53  03 F8           add di, ax
7D55  81 C7 F8 FF     add di, 0xfff8
7D59  06              push es
7D5A  57              push di
7D5B  FF 76 FE        push word ptr [bp - 2]
7D5E  B8 21 00        mov ax, 0x21
7D61  50              push ax
7D62  0E              push cs
7D63  E8 AC FA        call 0x7812
7D66  FF 46 FE        inc word ptr [bp - 2]
7D69  8B 46 FC        mov ax, word ptr [bp - 4]
7D6C  3B 46 EA        cmp ax, word ptr [bp - 0x16]
7D6F  75 BC           jne 0x7d2d
loc_7D71:
7D71  8B 46 F8        mov ax, word ptr [bp - 8]
7D74  05 07 00        add ax, 7
7D77  50              push ax
7D78  B8 0E 00        mov ax, 0xe
7D7B  50              push ax
7D7C  B8 35 00        mov ax, 0x35
7D7F  50              push ax
7D80  9A C5 13 4B 21  call far 214B:13C5
7D85  C4 3E 6E A9     les di, ptr [0xa96e]
7D89  06              push es
7D8A  57              push di
7D8B  C4 3E 6A A9     les di, ptr [0xa96a]
7D8F  06              push es
7D90  57              push di
7D91  B8 A0 0F        mov ax, 0xfa0
7D94  50              push ax
7D95  9A 5D 02 E4 23  call far 23E4:025D
7D9A  9A DD 08 4B 21  call far 214B:08DD
7D9F  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
7DA4  74 04           je 0x7daa
7DA6  B0 00           mov al, 0
7DA8  EB 02           jmp 0x7dac
loc_7DAA:
7DAA  B0 01           mov al, 1
loc_7DAC:
7DAC  88 46 F4        mov byte ptr [bp - 0xc], al
7DAF  8D 7E F8        lea di, [bp - 8]
7DB2  16              push ss
7DB3  57              push di
7DB4  8D 7E FA        lea di, [bp - 6]
7DB7  16              push ss
7DB8  57              push di
7DB9  B8 10 00        mov ax, 0x10
7DBC  50              push ax
7DBD  B8 24 00        mov ax, 0x24
7DC0  50              push ax
7DC1  9A B1 15 4B 21  call far 214B:15B1
7DC6  8B 46 F6        mov ax, word ptr [bp - 0xa]
7DC9  B1 03           mov cl, 3
7DCB  D3 E0           shl ax, cl
7DCD  C4 3E 2B A9     les di, ptr [0xa92b]
7DD1  03 F8           add di, ax
7DD3  81 C7 F8 FF     add di, 0xfff8
7DD7  89 7E E8        mov word ptr [bp - 0x18], di
7DDA  8C 46 EA        mov word ptr [bp - 0x16], es
7DDD  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
7DE2  75 57           jne 0x7e3b
7DE4  C4 7E E8        les di, ptr [bp - 0x18]
7DE7  26 80 3D FE     cmp byte ptr es:[di], 0xfe
7DEB  72 4E           jb 0x7e3b
7DED  80 7E F5 00     cmp byte ptr [bp - 0xb], 0
7DF1  75 1B           jne 0x7e0e
7DF3  C4 7E E8        les di, ptr [bp - 0x18]
7DF6  26 80 3D FE     cmp byte ptr es:[di], 0xfe
7DFA  75 09           jne 0x7e05
7DFC  C4 7E E8        les di, ptr [bp - 0x18]
7DFF  26 C6 05 FF     mov byte ptr es:[di], 0xff
7E03  EB 07           jmp 0x7e0c
loc_7E05:
7E05  C4 7E E8        les di, ptr [bp - 0x18]
7E08  26 C6 05 FE     mov byte ptr es:[di], 0xfe
loc_7E0C:
7E0C  EB 2D           jmp 0x7e3b
loc_7E0E:
7E0E  FF 76 06        push word ptr [bp + 6]
7E11  0E              push cs
7E12  E8 62 8D        call 0xb77
7E15  08 C0           or al, al
7E17  74 22           je 0x7e3b
7E19  C4 7E E8        les di, ptr [bp - 0x18]
7E1C  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
7E21  75 0A           jne 0x7e2d
7E23  C4 7E E8        les di, ptr [bp - 0x18]
7E26  26 C6 45 02 00  mov byte ptr es:[di + 2], 0
7E2B  EB 0E           jmp 0x7e3b
loc_7E2D:
7E2D  C4 7E E8        les di, ptr [bp - 0x18]
7E30  26 80 7D 02 00  cmp byte ptr es:[di + 2], 0
7E35  75 04           jne 0x7e3b
7E37  55              push bp
7E38  E8 5F FC        call 0x7a9a
loc_7E3B:
7E3B  80 7E F4 00     cmp byte ptr [bp - 0xc], 0
7E3F  75 03           jne 0x7e44
7E41  E9 8C FD        jmp 0x7bd0
loc_7E44:
7E44  89 EC           mov sp, bp
7E46  5D              pop bp
7E47  CA 02 00        retf 2

; ---- routine 1771:7E4A  (found by: call)
sub_7E4A:
7E4A  55              push bp
7E4B  89 E5           mov bp, sp
7E4D  83 EC 04        sub sp, 4
7E50  8B 46 04        mov ax, word ptr [bp + 4]
7E53  BA 14 00        mov dx, 0x14
7E56  F7 E2           mul dx
7E58  C4 3E 1B A9     les di, ptr [0xa91b]
7E5C  03 F8           add di, ax
7E5E  89 7E FC        mov word ptr [bp - 4], di
7E61  8C 46 FE        mov word ptr [bp - 2], es
7E64  83 7E 04 00     cmp word ptr [bp + 4], 0
7E68  75 02           jne 0x7e6c
7E6A  EB 0E           jmp 0x7e7a
loc_7E6C:
7E6C  C4 7E FC        les di, ptr [bp - 4]
7E6F  26 FE 45 01     inc byte ptr es:[di + 1]
7E73  FF 76 04        push word ptr [bp + 4]
7E76  0E              push cs
7E77  E8 71 B4        call 0x32eb
loc_7E7A:
7E7A  89 EC           mov sp, bp
7E7C  5D              pop bp
7E7D  C2 02 00        ret 2

; ---- routine 1771:7E80  (found by: call)
sub_7E80:
7E80  55              push bp
7E81  89 E5           mov bp, sp
7E83  83 EC 06        sub sp, 6
7E86  8B 46 04        mov ax, word ptr [bp + 4]
7E89  BA 14 00        mov dx, 0x14
7E8C  F7 E2           mul dx
7E8E  C4 3E 1B A9     les di, ptr [0xa91b]
7E92  03 F8           add di, ax
7E94  89 7E FA        mov word ptr [bp - 6], di
7E97  8C 46 FC        mov word ptr [bp - 4], es
7E9A  C4 7E FA        les di, ptr [bp - 6]
7E9D  26 8A 45 06     mov al, byte ptr es:[di + 6]
7EA1  30 E4           xor ah, ah
7EA3  89 46 FE        mov word ptr [bp - 2], ax
7EA6  FF 76 04        push word ptr [bp + 4]
7EA9  C4 7E FA        les di, ptr [bp - 6]
7EAC  26 8A 05        mov al, byte ptr es:[di]
7EAF  30 E4           xor ah, ah
7EB1  50              push ax
7EB2  C4 7E FA        les di, ptr [bp - 6]
7EB5  26 8A 45 07     mov al, byte ptr es:[di + 7]
7EB9  30 E4           xor ah, ah
7EBB  50              push ax
7EBC  B0 01           mov al, 1
7EBE  50              push ax
7EBF  0E              push cs
7EC0  E8 10 18        call 0x96d3
7EC3  B8 06 00        mov ax, 6
7EC6  50              push ax
7EC7  9A B1 06 4B 21  call far 214B:06B1
7ECC  50              push ax
7ECD  B8 06 00        mov ax, 6
7ED0  50              push ax
7ED1  9A B1 06 4B 21  call far 214B:06B1
7ED6  8B D0           mov dx, ax
7ED8  C4 7E FA        les di, ptr [bp - 6]
7EDB  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
7EE0  74 04           je 0x7ee6
7EE2  B0 00           mov al, 0
7EE4  EB 02           jmp 0x7ee8
loc_7EE6:
7EE6  B0 01           mov al, 1
loc_7EE8:
7EE8  98              cwde
7EE9  8B F8           mov di, ax
7EEB  8A 85 0C 11     mov al, byte ptr [di + 0x110c]
7EEF  30 E4           xor ah, ah
7EF1  03 C2           add ax, dx
7EF3  5A              pop dx
7EF4  2B C2           sub ax, dx
7EF6  C4 7E FA        les di, ptr [bp - 6]
7EF9  26 88 45 01     mov byte ptr es:[di + 1], al
7EFD  FF 76 04        push word ptr [bp + 4]
7F00  0E              push cs
7F01  E8 E7 B3        call 0x32eb
7F04  C4 7E FA        les di, ptr [bp - 6]
7F07  31 C0           xor ax, ax
7F09  26 89 45 08     mov word ptr es:[di + 8], ax
7F0D  C4 7E FA        les di, ptr [bp - 6]
7F10  31 C0           xor ax, ax
7F12  26 89 45 0A     mov word ptr es:[di + 0xa], ax
7F16  C4 7E FA        les di, ptr [bp - 6]
7F19  26 C6 45 10 00  mov byte ptr es:[di + 0x10], 0
7F1E  0E              push cs
7F1F  E8 DE 80        call 0
7F22  8A D0           mov dl, al
7F24  8B 46 04        mov ax, word ptr [bp + 4]
7F27  C4 3E 70 9B     les di, ptr [0x9b70]
7F2B  03 F8           add di, ax
7F2D  26 88 15        mov byte ptr es:[di], dl
7F30  8A 46 FE        mov al, byte ptr [bp - 2]
7F33  C4 7E FA        les di, ptr [bp - 6]
7F36  26 88 45 06     mov byte ptr es:[di + 6], al
7F3A  89 EC           mov sp, bp
7F3C  5D              pop bp
7F3D  C2 02 00        ret 2

; ---- routine 1771:7F40  (found by: call, far)
sub_7F40:
7F40  55              push bp
7F41  89 E5           mov bp, sp
7F43  83 EC 06        sub sp, 6
7F46  8B 46 06        mov ax, word ptr [bp + 6]
7F49  BA 14 00        mov dx, 0x14
7F4C  F7 E2           mul dx
7F4E  C4 3E 1B A9     les di, ptr [0xa91b]
7F52  03 F8           add di, ax
7F54  89 7E FB        mov word ptr [bp - 5], di
7F57  8C 46 FD        mov word ptr [bp - 3], es
7F5A  C4 7E FB        les di, ptr [bp - 5]
7F5D  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
7F62  74 04           je 0x7f68
7F64  B0 00           mov al, 0
7F66  EB 02           jmp 0x7f6a
loc_7F68:
7F68  B0 01           mov al, 1
loc_7F6A:
7F6A  98              cwde
7F6B  8B F8           mov di, ax
7F6D  8A 85 0E 11     mov al, byte ptr [di + 0x110e]
7F71  C4 7E FB        les di, ptr [bp - 5]
7F74  26 3A 45 01     cmp al, byte ptr es:[di + 1]
7F78  73 0A           jae 0x7f84
7F7A  C4 7E FB        les di, ptr [bp - 5]
7F7D  26 83 7D 08 00  cmp word ptr es:[di + 8], 0
7F82  74 1F           je 0x7fa3
loc_7F84:
7F84  C4 7E FB        les di, ptr [bp - 5]
7F87  26 8A 45 02     mov al, byte ptr es:[di + 2]
7F8B  30 E4           xor ah, ah
7F8D  05 05 00        add ax, 5
7F90  8B D0           mov dx, ax
7F92  C4 7E FB        les di, ptr [bp - 5]
7F95  26 8A 45 01     mov al, byte ptr es:[di + 1]
7F99  30 E4           xor ah, ah
7F9B  3B C2           cmp ax, dx
7F9D  7F 04           jg 0x7fa3
7F9F  B0 00           mov al, 0
7FA1  EB 02           jmp 0x7fa5
loc_7FA3:
7FA3  B0 01           mov al, 1
loc_7FA5:
7FA5  88 46 FF        mov byte ptr [bp - 1], al
7FA8  8A 46 FF        mov al, byte ptr [bp - 1]
7FAB  89 EC           mov sp, bp
7FAD  5D              pop bp
7FAE  CA 02 00        retf 2

; ---- routine 1771:7FB1  (found by: call)
sub_7FB1:
7FB1  55              push bp
7FB2  89 E5           mov bp, sp
7FB4  83 EC 04        sub sp, 4
7FB7  8B 46 06        mov ax, word ptr [bp + 6]
7FBA  BA 14 00        mov dx, 0x14
7FBD  F7 E2           mul dx
7FBF  C4 3E 1B A9     les di, ptr [0xa91b]
7FC3  03 F8           add di, ax
7FC5  89 7E FC        mov word ptr [bp - 4], di
7FC8  8C 46 FE        mov word ptr [bp - 2], es
7FCB  FF 76 06        push word ptr [bp + 6]
7FCE  E8 79 FE        call 0x7e4a
7FD1  C4 7E FC        les di, ptr [bp - 4]
7FD4  26 C6 45 11 00  mov byte ptr es:[di + 0x11], 0
7FD9  89 EC           mov sp, bp
7FDB  5D              pop bp
7FDC  C2 04 00        ret 4

; ---- routine 1771:7FDF  (found by: call)
sub_7FDF:
7FDF  55              push bp
7FE0  89 E5           mov bp, sp
7FE2  83 EC 08        sub sp, 8
7FE5  8B 46 04        mov ax, word ptr [bp + 4]
7FE8  BA BF 00        mov dx, 0xbf
7FEB  F7 E2           mul dx
7FED  C4 3E 17 A9     les di, ptr [0xa917]
7FF1  03 F8           add di, ax
7FF3  89 7E FA        mov word ptr [bp - 6], di
7FF6  8C 46 FC        mov word ptr [bp - 4], es
7FF9  C7 46 FE 01 00  mov word ptr [bp - 2], 1
7FFE  EB 03           jmp 0x8003
loc_8000:
8000  FF 46 FE        inc word ptr [bp - 2]
loc_8003:
8003  8B 46 FE        mov ax, word ptr [bp - 2]
8006  D1 E0           shl ax, 1
8008  C4 7E FA        les di, ptr [bp - 6]
800B  03 F8           add di, ax
800D  26 FF 75 FE     push word ptr es:[di - 2]
8011  55              push bp
8012  E8 9C FF        call 0x7fb1
8015  83 7E FE 14     cmp word ptr [bp - 2], 0x14
8019  75 E5           jne 0x8000
801B  FF 76 04        push word ptr [bp + 4]
801E  0E              push cs
801F  E8 55 8B        call 0xb77
8022  08 C0           or al, al
8024  74 57           je 0x807d
8026  C4 7E FA        les di, ptr [bp - 6]
8029  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
802D  30 E4           xor ah, ah
802F  2D 80 00        sub ax, 0x80
8032  8B F8           mov di, ax
8034  D1 E7           shl di, 1
8036  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
803A  05 4F 00        add ax, 0x4f
803D  89 46 F8        mov word ptr [bp - 8], ax
8040  C4 7E FA        les di, ptr [bp - 6]
8043  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
8047  30 E4           xor ah, ah
8049  2D 80 00        sub ax, 0x80
804C  8B F8           mov di, ax
804E  D1 E7           shl di, 1
8050  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
8054  3B 46 F8        cmp ax, word ptr [bp - 8]
8057  77 22           ja 0x807b
8059  89 46 FE        mov word ptr [bp - 2], ax
805C  EB 03           jmp 0x8061
loc_805E:
805E  FF 46 FE        inc word ptr [bp - 2]
loc_8061:
8061  8B 46 FE        mov ax, word ptr [bp - 2]
8064  D1 E0           shl ax, 1
8066  C4 3E 27 A9     les di, ptr [0xa927]
806A  03 F8           add di, ax
806C  26 FF 35        push word ptr es:[di]
806F  55              push bp
8070  E8 3E FF        call 0x7fb1
8073  8B 46 FE        mov ax, word ptr [bp - 2]
8076  3B 46 F8        cmp ax, word ptr [bp - 8]
8079  75 E3           jne 0x805e
loc_807B:
807B  EB 37           jmp 0x80b4
loc_807D:
807D  C7 46 FE 01 00  mov word ptr [bp - 2], 1
8082  EB 03           jmp 0x8087
loc_8084:
8084  FF 46 FE        inc word ptr [bp - 2]
loc_8087:
8087  8B 46 FE        mov ax, word ptr [bp - 2]
808A  D1 E0           shl ax, 1
808C  C4 7E FA        les di, ptr [bp - 6]
808F  03 F8           add di, ax
8091  26 FF 75 FE     push word ptr es:[di - 2]
8095  0E              push cs
8096  E8 A7 FE        call 0x7f40
8099  08 C0           or al, al
809B  74 11           je 0x80ae
809D  8B 46 FE        mov ax, word ptr [bp - 2]
80A0  D1 E0           shl ax, 1
80A2  C4 7E FA        les di, ptr [bp - 6]
80A5  03 F8           add di, ax
80A7  26 FF 75 FE     push word ptr es:[di - 2]
80AB  E8 D2 FD        call 0x7e80
loc_80AE:
80AE  83 7E FE 14     cmp word ptr [bp - 2], 0x14
80B2  75 D0           jne 0x8084
loc_80B4:
80B4  89 EC           mov sp, bp
80B6  5D              pop bp
80B7  C2 02 00        ret 2
; data (not reached as code), 32 bytes
80BA                  db 24 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; $...............
80CA                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

