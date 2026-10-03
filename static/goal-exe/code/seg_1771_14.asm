; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 14 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:97CC  (found by: call)
sub_97CC:
97CC  55              push bp
97CD  89 E5           mov bp, sp
97CF  83 EC 06        sub sp, 6
97D2  8B 46 06        mov ax, word ptr [bp + 6]
97D5  BA BF 00        mov dx, 0xbf
97D8  F7 E2           mul dx
97DA  C4 3E 17 A9     les di, ptr [0xa917]
97DE  03 F8           add di, ax
97E0  89 7E FA        mov word ptr [bp - 6], di
97E3  8C 46 FC        mov word ptr [bp - 4], es
97E6  8B 46 06        mov ax, word ptr [bp + 6]
97E9  C4 3E 78 A9     les di, ptr [0xa978]
97ED  26 89 05        mov word ptr es:[di], ax
97F0  C4 7E FA        les di, ptr [bp - 6]
97F3  26 8A 45 2B     mov al, byte ptr es:[di + 0x2b]
97F7  C4 7E FA        les di, ptr [bp - 6]
97FA  26 88 45 29     mov byte ptr es:[di + 0x29], al
97FE  C4 7E FA        les di, ptr [bp - 6]
9801  26 8A 45 2A     mov al, byte ptr es:[di + 0x2a]
9805  C4 7E FA        les di, ptr [bp - 6]
9808  26 88 45 28     mov byte ptr es:[di + 0x28], al
980C  FF 76 06        push word ptr [bp + 6]
980F  0E              push cs
9810  E8 D4 78        call 0x110e7
9813  8A C8           mov cl, al
9815  C4 7E FA        les di, ptr [bp - 6]
9818  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
981C  30 E4           xor ah, ah
981E  BA 03 00        mov dx, 3
9821  F7 E2           mul dx
9823  C4 3E 1F A9     les di, ptr [0xa91f]
9827  03 F8           add di, ax
9829  26 88 4D 01     mov byte ptr es:[di + 1], cl
982D  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9832  EB 03           jmp 0x9837
loc_9834:
9834  FF 46 FE        inc word ptr [bp - 2]
loc_9837:
9837  8B 46 FE        mov ax, word ptr [bp - 2]
983A  D1 E0           shl ax, 1
983C  C4 7E FA        les di, ptr [bp - 6]
983F  03 F8           add di, ax
9841  26 FF 75 FE     push word ptr es:[di - 2]
9845  FF 76 06        push word ptr [bp + 6]
9848  8B 46 FE        mov ax, word ptr [bp - 2]
984B  8B C8           mov cx, ax
984D  8B 46 06        mov ax, word ptr [bp + 6]
9850  BA 14 00        mov dx, 0x14
9853  F7 E2           mul dx
9855  8B F8           mov di, ax
9857  03 F9           add di, cx
9859  8A 85 02 9F     mov al, byte ptr [di - 0x60fe]
985D  30 E4           xor ah, ah
985F  50              push ax
9860  B0 01           mov al, 1
9862  50              push ax
9863  0E              push cs
9864  E8 6C FE        call 0x96d3
9867  83 7E FE 14     cmp word ptr [bp - 2], 0x14
986B  75 C7           jne 0x9834
986D  89 EC           mov sp, bp
986F  5D              pop bp
9870  CA 02 00        retf 2

; ---- routine 1771:9873  (found by: call)
sub_9873:
9873  55              push bp
9874  89 E5           mov bp, sp
9876  8B 7E 04        mov di, word ptr [bp + 4]
9879  36 FF 45 FE     inc word ptr ss:[di - 2]
987D  8B 7E 04        mov di, word ptr [bp + 4]
9880  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
9884  05 00 0A        add ax, 0xa00
9887  8B D0           mov dx, ax
9889  8B 7E 04        mov di, word ptr [bp + 4]
988C  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
9890  D1 E0           shl ax, 1
9892  C4 3E 27 A9     les di, ptr [0xa927]
9896  03 F8           add di, ax
9898  26 89 15        mov word ptr es:[di], dx
989B  8B 7E 04        mov di, word ptr [bp + 4]
989E  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
98A2  D1 E0           shl ax, 1
98A4  C4 3E 27 A9     les di, ptr [0xa927]
98A8  03 F8           add di, ax
98AA  26 FF 35        push word ptr es:[di]
98AD  8B 7E 04        mov di, word ptr [bp + 4]
98B0  36 FF 75 F8     push word ptr ss:[di - 8]
98B4  FF 76 06        push word ptr [bp + 6]
98B7  B0 00           mov al, 0
98B9  50              push ax
98BA  0E              push cs
98BB  E8 15 FE        call 0x96d3
98BE  89 EC           mov sp, bp
98C0  5D              pop bp
98C1  C2 04 00        ret 4

; ---- routine 1771:98C4  (found by: call)
sub_98C4:
98C4  55              push bp
98C5  89 E5           mov bp, sp
98C7  83 EC 14        sub sp, 0x14
98CA  C4 3E 23 A9     les di, ptr [0xa923]
98CE  89 7E F4        mov word ptr [bp - 0xc], di
98D1  8C 46 F6        mov word ptr [bp - 0xa], es
98D4  C4 7E F4        les di, ptr [bp - 0xc]
98D7  26 8A 45 01     mov al, byte ptr es:[di + 1]
98DB  30 E4           xor ah, ah
98DD  D1 E0           shl ax, 1
98DF  C4 7E F4        les di, ptr [bp - 0xc]
98E2  03 F8           add di, ax
98E4  26 C7 45 5E 01 00 mov word ptr es:[di + 0x5e], 1
98EA  C4 7E F4        les di, ptr [bp - 0xc]
98ED  26 8A 45 01     mov al, byte ptr es:[di + 1]
98F1  30 E4           xor ah, ah
98F3  D1 E0           shl ax, 1
98F5  C4 7E F4        les di, ptr [bp - 0xc]
98F8  03 F8           add di, ax
98FA  26 C7 45 52 01 00 mov word ptr es:[di + 0x52], 1
9900  C4 7E F4        les di, ptr [bp - 0xc]
9903  26 8A 45 01     mov al, byte ptr es:[di + 1]
9907  30 E4           xor ah, ah
9909  8B F8           mov di, ax
990B  D1 E7           shl di, 1
990D  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
9911  48              dec ax
9912  89 46 FE        mov word ptr [bp - 2], ax
9915  C4 7E F4        les di, ptr [bp - 0xc]
9918  26 8A 45 01     mov al, byte ptr es:[di + 1]
991C  30 E4           xor ah, ah
991E  05 80 00        add ax, 0x80
9921  BA 03 00        mov dx, 3
9924  F7 E2           mul dx
9926  C4 3E 1F A9     les di, ptr [0xa91f]
992A  03 F8           add di, ax
992C  26 8A 05        mov al, byte ptr es:[di]
992F  30 E4           xor ah, ah
9931  89 46 F8        mov word ptr [bp - 8], ax
9934  31 C0           xor ax, ax
9936  89 46 FC        mov word ptr [bp - 4], ax
9939  EB 03           jmp 0x993e
loc_993B:
993B  FF 46 FC        inc word ptr [bp - 4]
loc_993E:
993E  C7 46 FA 01 00  mov word ptr [bp - 6], 1
9943  EB 03           jmp 0x9948
loc_9945:
9945  FF 46 FA        inc word ptr [bp - 6]
loc_9948:
9948  FF 76 FC        push word ptr [bp - 4]
994B  55              push bp
994C  E8 24 FF        call 0x9873
994F  83 7E FA 04     cmp word ptr [bp - 6], 4
9953  75 F0           jne 0x9945
9955  83 7E FC 0D     cmp word ptr [bp - 4], 0xd
9959  75 E0           jne 0x993b
995B  8B 46 F8        mov ax, word ptr [bp - 8]
995E  BA BF 00        mov dx, 0xbf
9961  F7 E2           mul dx
9963  C4 3E 17 A9     les di, ptr [0xa917]
9967  03 F8           add di, ax
9969  89 7E F0        mov word ptr [bp - 0x10], di
996C  8C 46 F2        mov word ptr [bp - 0xe], es
996F  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9974  EB 03           jmp 0x9979
loc_9976:
9976  FF 46 FC        inc word ptr [bp - 4]
loc_9979:
9979  8B 46 FC        mov ax, word ptr [bp - 4]
997C  D1 E0           shl ax, 1
997E  C4 7E F0        les di, ptr [bp - 0x10]
9981  03 F8           add di, ax
9983  26 8B 45 FE     mov ax, word ptr es:[di - 2]
9987  BA 14 00        mov dx, 0x14
998A  F7 E2           mul dx
998C  C4 3E 1B A9     les di, ptr [0xa91b]
9990  03 F8           add di, ax
9992  26 8A 45 07     mov al, byte ptr es:[di + 7]
9996  30 E4           xor ah, ah
9998  50              push ax
9999  55              push bp
999A  E8 D6 FE        call 0x9873
999D  8B 46 FE        mov ax, word ptr [bp - 2]
99A0  D1 E0           shl ax, 1
99A2  C4 3E 27 A9     les di, ptr [0xa927]
99A6  03 F8           add di, ax
99A8  26 8B 05        mov ax, word ptr es:[di]
99AB  BA 14 00        mov dx, 0x14
99AE  F7 E2           mul dx
99B0  C4 3E 1B A9     les di, ptr [0xa91b]
99B4  03 F8           add di, ax
99B6  89 7E EC        mov word ptr [bp - 0x14], di
99B9  8C 46 EE        mov word ptr [bp - 0x12], es
99BC  B8 03 00        mov ax, 3
99BF  50              push ax
99C0  9A B1 06 4B 21  call far 214B:06B1
99C5  8B D0           mov dx, ax
99C7  C4 7E EC        les di, ptr [bp - 0x14]
99CA  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
99CF  74 04           je 0x99d5
99D1  B0 00           mov al, 0
99D3  EB 02           jmp 0x99d7
loc_99D5:
99D5  B0 01           mov al, 1
loc_99D7:
99D7  98              cwde
99D8  8B F8           mov di, ax
99DA  8A 85 8C 11     mov al, byte ptr [di + 0x118c]
99DE  30 E4           xor ah, ah
99E0  03 C2           add ax, dx
99E2  C4 7E EC        les di, ptr [bp - 0x14]
99E5  26 88 45 01     mov byte ptr es:[di + 1], al
99E9  8B 46 FE        mov ax, word ptr [bp - 2]
99EC  D1 E0           shl ax, 1
99EE  C4 3E 27 A9     les di, ptr [0xa927]
99F2  03 F8           add di, ax
99F4  26 FF 35        push word ptr es:[di]
99F7  0E              push cs
99F8  E8 F0 98        call 0x32eb
99FB  83 7E FC 14     cmp word ptr [bp - 4], 0x14
99FF  74 03           je 0x9a04
9A01  E9 72 FF        jmp 0x9976
loc_9A04:
9A04  C7 46 FC 06 00  mov word ptr [bp - 4], 6
9A09  EB 03           jmp 0x9a0e
loc_9A0B:
9A0B  FF 46 FC        inc word ptr [bp - 4]
loc_9A0E:
9A0E  8B 46 FC        mov ax, word ptr [bp - 4]
9A11  D1 E0           shl ax, 1
9A13  C4 7E F0        les di, ptr [bp - 0x10]
9A16  03 F8           add di, ax
9A18  26 8B 45 FE     mov ax, word ptr es:[di - 2]
9A1C  BA 14 00        mov dx, 0x14
9A1F  F7 E2           mul dx
9A21  C4 3E 1B A9     les di, ptr [0xa91b]
9A25  03 F8           add di, ax
9A27  26 8A 45 07     mov al, byte ptr es:[di + 7]
9A2B  30 E4           xor ah, ah
9A2D  50              push ax
9A2E  55              push bp
9A2F  E8 41 FE        call 0x9873
9A32  83 7E FC 09     cmp word ptr [bp - 4], 9
9A36  75 D3           jne 0x9a0b
9A38  0E              push cs
9A39  E8 F6 BA        call 0x5532
9A3C  89 EC           mov sp, bp
9A3E  5D              pop bp
9A3F  CB              retf

; ---- routine 1771:9A40  (found by: call)
sub_9A40:
9A40  55              push bp
9A41  89 E5           mov bp, sp
9A43  83 EC 0A        sub sp, 0xa
9A46  31 C0           xor ax, ax
9A48  89 46 FA        mov word ptr [bp - 6], ax
9A4B  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9A50  EB 03           jmp 0x9a55
loc_9A52:
9A52  FF 46 FC        inc word ptr [bp - 4]
loc_9A55:
9A55  8B 7E FC        mov di, word ptr [bp - 4]
9A58  8A 85 FD 9B     mov al, byte ptr [di - 0x6403]
9A5C  30 E4           xor ah, ah
9A5E  BA BF 00        mov dx, 0xbf
9A61  F7 E2           mul dx
9A63  C4 3E 17 A9     les di, ptr [0xa917]
9A67  03 F8           add di, ax
9A69  89 7E F6        mov word ptr [bp - 0xa], di
9A6C  8C 46 F8        mov word ptr [bp - 8], es
9A6F  8A 46 FC        mov al, byte ptr [bp - 4]
9A72  C4 7E F6        les di, ptr [bp - 0xa]
9A75  26 88 45 2B     mov byte ptr es:[di + 0x2b], al
9A79  81 7E FC 80 00  cmp word ptr [bp - 4], 0x80
9A7E  75 D2           jne 0x9a52
9A80  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9A85  EB 03           jmp 0x9a8a
loc_9A87:
9A87  FF 46 FC        inc word ptr [bp - 4]
loc_9A8A:
9A8A  8B 7E FC        mov di, word ptr [bp - 4]
9A8D  8A 85 7E 9C     mov al, byte ptr [di - 0x6382]
9A91  30 E4           xor ah, ah
9A93  BA BF 00        mov dx, 0xbf
9A96  F7 E2           mul dx
9A98  C4 3E 17 A9     les di, ptr [0xa917]
9A9C  03 F8           add di, ax
9A9E  89 7E F6        mov word ptr [bp - 0xa], di
9AA1  8C 46 F8        mov word ptr [bp - 8], es
9AA4  8B 46 FC        mov ax, word ptr [bp - 4]
9AA7  48              dec ax
9AA8  31 D2           xor dx, dx
9AAA  B9 20 00        mov cx, 0x20
9AAD  F7 F1           div cx
9AAF  92              xchg dx, ax
9AB0  40              inc ax
9AB1  C4 7E F6        les di, ptr [bp - 0xa]
9AB4  26 88 45 2A     mov byte ptr es:[di + 0x2a], al
9AB8  8B 46 FC        mov ax, word ptr [bp - 4]
9ABB  48              dec ax
9ABC  31 D2           xor dx, dx
9ABE  B9 20 00        mov cx, 0x20
9AC1  F7 F1           div cx
9AC3  40              inc ax
9AC4  C4 7E F6        les di, ptr [bp - 0xa]
9AC7  26 88 45 2C     mov byte ptr es:[di + 0x2c], al
9ACB  81 7E FC 80 00  cmp word ptr [bp - 4], 0x80
9AD0  75 B5           jne 0x9a87
9AD2  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9AD7  EB 03           jmp 0x9adc
loc_9AD9:
9AD9  FF 46 FC        inc word ptr [bp - 4]
loc_9ADC:
9ADC  8B 46 FC        mov ax, word ptr [bp - 4]
9ADF  BA BF 00        mov dx, 0xbf
9AE2  F7 E2           mul dx
9AE4  C4 3E 17 A9     les di, ptr [0xa917]
9AE8  03 F8           add di, ax
9AEA  89 7E F6        mov word ptr [bp - 0xa], di
9AED  8C 46 F8        mov word ptr [bp - 8], es
9AF0  8A 46 FC        mov al, byte ptr [bp - 4]
9AF3  C4 7E F6        les di, ptr [bp - 0xa]
9AF6  26 88 45 2E     mov byte ptr es:[di + 0x2e], al
9AFA  8A 4E FC        mov cl, byte ptr [bp - 4]
9AFD  8B 46 FC        mov ax, word ptr [bp - 4]
9B00  BA 03 00        mov dx, 3
9B03  F7 E2           mul dx
9B05  C4 3E 1F A9     les di, ptr [0xa91f]
9B09  03 F8           add di, ax
9B0B  26 88 0D        mov byte ptr es:[di], cl
9B0E  81 7E FC 80 00  cmp word ptr [bp - 4], 0x80
9B13  75 C4           jne 0x9ad9
9B15  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9B1A  EB 03           jmp 0x9b1f
loc_9B1C:
9B1C  FF 46 FC        inc word ptr [bp - 4]
loc_9B1F:
9B1F  8B 46 FC        mov ax, word ptr [bp - 4]
9B22  BA BF 00        mov dx, 0xbf
9B25  F7 E2           mul dx
9B27  C4 3E 17 A9     les di, ptr [0xa917]
9B2B  03 F8           add di, ax
9B2D  89 7E F6        mov word ptr [bp - 0xa], di
9B30  8C 46 F8        mov word ptr [bp - 8], es
9B33  8B 7E FC        mov di, word ptr [bp - 4]
9B36  8A 85 7C 9B     mov al, byte ptr [di - 0x6484]
9B3A  C4 7E F6        les di, ptr [bp - 0xa]
9B3D  26 88 45 2D     mov byte ptr es:[di + 0x2d], al
9B41  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9B46  EB 03           jmp 0x9b4b
loc_9B48:
9B48  FF 46 FE        inc word ptr [bp - 2]
loc_9B4B:
9B4B  8B 46 FA        mov ax, word ptr [bp - 6]
9B4E  03 46 FE        add ax, word ptr [bp - 2]
9B51  8B D0           mov dx, ax
9B53  8B 46 FE        mov ax, word ptr [bp - 2]
9B56  D1 E0           shl ax, 1
9B58  C4 7E F6        les di, ptr [bp - 0xa]
9B5B  03 F8           add di, ax
9B5D  26 89 55 FE     mov word ptr es:[di - 2], dx
9B61  83 7E FE 14     cmp word ptr [bp - 2], 0x14
9B65  75 E1           jne 0x9b48
9B67  FF 76 FC        push word ptr [bp - 4]
9B6A  0E              push cs
9B6B  E8 5E FC        call 0x97cc
9B6E  83 46 FA 14     add word ptr [bp - 6], 0x14
9B72  81 7E FC 80 00  cmp word ptr [bp - 4], 0x80
9B77  75 A3           jne 0x9b1c
9B79  89 EC           mov sp, bp
9B7B  5D              pop bp
9B7C  C3              ret
; data (not reached as code), 8 bytes
9B7D                  pstr 'G-0'
9B81                  pstr 'S-0'

; ---- routine 1771:9B85  (found by: far)
sub_9B85:
9B85  55              push bp
9B86  89 E5           mov bp, sp
9B88  83 EC 08        sub sp, 8
9B8B  C4 3E 23 A9     les di, ptr [0xa923]
9B8F  89 7E FC        mov word ptr [bp - 4], di
9B92  8C 46 FE        mov word ptr [bp - 2], es
9B95  E8 A8 FE        call 0x9a40
9B98  A1 FD A9        mov ax, word ptr [0xa9fd]
9B9B  40              inc ax
9B9C  C4 7E FC        les di, ptr [bp - 4]
9B9F  26 89 45 3A     mov word ptr es:[di + 0x3a], ax
9BA3  C4 7E FC        les di, ptr [bp - 4]
9BA6  26 8A 45 3A     mov al, byte ptr es:[di + 0x3a]
9BAA  D0 E8           shr al, 1
9BAC  73 07           jae 0x9bb5
9BAE  C4 7E FC        les di, ptr [bp - 4]
9BB1  26 FF 45 3A     inc word ptr es:[di + 0x3a]
loc_9BB5:
9BB5  C4 7E FC        les di, ptr [bp - 4]
9BB8  31 C0           xor ax, ax
9BBA  26 89 45 38     mov word ptr es:[di + 0x38], ax
9BBE  C4 7E FC        les di, ptr [bp - 4]
9BC1  26 8B 45 3A     mov ax, word ptr es:[di + 0x3a]
9BC5  31 D2           xor dx, dx
9BC7  B9 04 00        mov cx, 4
9BCA  F7 F1           div cx
9BCC  92              xchg dx, ax
9BCD  3D 02 00        cmp ax, 2
9BD0  74 04           je 0x9bd6
9BD2  B0 00           mov al, 0
9BD4  EB 02           jmp 0x9bd8
loc_9BD6:
9BD6  B0 01           mov al, 1
loc_9BD8:
9BD8  C4 7E FC        les di, ptr [bp - 4]
9BDB  26 88 45 40     mov byte ptr es:[di + 0x40], al
9BDF  C4 7E FC        les di, ptr [bp - 4]
9BE2  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
9BE6  98              cwde
9BE7  8B F8           mov di, ax
9BE9  8A 85 8E 11     mov al, byte ptr [di + 0x118e]
9BED  C4 7E FC        les di, ptr [bp - 4]
9BF0  26 88 45 3C     mov byte ptr es:[di + 0x3c], al
9BF4  C4 7E FC        les di, ptr [bp - 4]
9BF7  26 C6 45 3D 01  mov byte ptr es:[di + 0x3d], 1
9BFC  C4 7E FC        les di, ptr [bp - 4]
9BFF  26 C6 45 3E 02  mov byte ptr es:[di + 0x3e], 2
9C04  C4 7E FC        les di, ptr [bp - 4]
9C07  26 C6 45 3F 01  mov byte ptr es:[di + 0x3f], 1
9C0C  C4 7E FC        les di, ptr [bp - 4]
9C0F  26 C6 45 41 01  mov byte ptr es:[di + 0x41], 1
9C14  BF 7D 9B        mov di, 0x9b7d
9C17  0E              push cs
9C18  57              push di
9C19  C4 7E FC        les di, ptr [bp - 4]
9C1C  81 C7 6C 00     add di, 0x6c
9C20  06              push es
9C21  57              push di
9C22  B8 50 00        mov ax, 0x50
9C25  50              push ax
9C26  9A 44 06 E4 23  call far 23E4:0644
9C2B  BF 81 9B        mov di, 0x9b81
9C2E  0E              push cs
9C2F  57              push di
9C30  C4 7E FC        les di, ptr [bp - 4]
9C33  81 C7 BD 00     add di, 0xbd
9C37  06              push es
9C38  57              push di
9C39  B8 50 00        mov ax, 0x50
9C3C  50              push ax
9C3D  9A 44 06 E4 23  call far 23E4:0644
9C42  C4 3E 2B A9     les di, ptr [0xa92b]
9C46  81 C7 40 4B     add di, 0x4b40
9C4A  89 7E F8        mov word ptr [bp - 8], di
9C4D  8C 46 FA        mov word ptr [bp - 6], es
9C50  C4 7E F8        les di, ptr [bp - 8]
9C53  26 C6 05 FF     mov byte ptr es:[di], 0xff
9C57  C4 7E F8        les di, ptr [bp - 8]
9C5A  26 C6 45 01 00  mov byte ptr es:[di + 1], 0
9C5F  C4 7E F8        les di, ptr [bp - 8]
9C62  26 C6 45 02 00  mov byte ptr es:[di + 2], 0
9C67  89 EC           mov sp, bp
9C69  5D              pop bp
9C6A  CB              retf
; data (not reached as code), 5 bytes
9C6B                  db 00 00 00 00 00   ; .....
