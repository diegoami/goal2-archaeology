; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 16 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:970C  (found by: call)
sub_970C:
970C  55              push bp
970D  89 E5           mov bp, sp
970F  83 EC 06        sub sp, 6
9712  C6 46 FF 00     mov byte ptr [bp - 1], 0
9716  80 3E 25 83 00  cmp byte ptr [0x8325], 0
971B  75 03           jne 0x9720
971D  E9 A7 00        jmp 0x97c7
loc_9720:
9720  83 3E 1D 83 00  cmp word ptr [0x831d], 0
9725  76 07           jbe 0x972e
9727  FF 0E 1D 83     dec word ptr [0x831d]
972B  E9 99 00        jmp 0x97c7
loc_972E:
972E  A1 1B 83        mov ax, word ptr [0x831b]
9731  03 06 21 83     add ax, word ptr [0x8321]
9735  09 C0           or ax, ax
9737  74 04           je 0x973d
9739  B0 00           mov al, 0
973B  EB 02           jmp 0x973f
loc_973D:
973D  B0 01           mov al, 1
loc_973F:
973F  A2 26 83        mov byte ptr [0x8326], al
9742  80 3E 26 83 00  cmp byte ptr [0x8326], 0
9747  75 1D           jne 0x9766
9749  83 3E 1B 83 00  cmp word ptr [0x831b], 0
974E  76 06           jbe 0x9756
9750  FF 0E 1B 83     dec word ptr [0x831b]
9754  EB 04           jmp 0x975a
loc_9756:
9756  FF 0E 21 83     dec word ptr [0x8321]
loc_975A:
975A  81 3E 1F 83 80 00 cmp word ptr [0x831f], 0x80
9760  73 04           jae 0x9766
9762  FF 06 1F 83     inc word ptr [0x831f]
loc_9766:
9766  FF 36 1B 83     push word ptr [0x831b]
976A  B8 03 00        mov ax, 3
976D  50              push ax
976E  E8 DB 6D        call 0x1054c
9771  C7 06 1D 83 24 00 mov word ptr [0x831d], 0x24
9777  A0 19 83        mov al, byte ptr [0x8319]
977A  98              cwde
977B  99              cdq
977C  8B C8           mov cx, ax
977E  8B DA           mov bx, dx
9780  A1 1B 83        mov ax, word ptr [0x831b]
9783  31 D2           xor dx, dx
9785  3B D3           cmp dx, bx
9787  75 04           jne 0x978d
9789  3B C1           cmp ax, cx
978B  74 07           je 0x9794
loc_978D:
978D  80 3E 26 83 00  cmp byte ptr [0x8326], 0
9792  74 33           je 0x97c7
loc_9794:
9794  80 3E 26 83 00  cmp byte ptr [0x8326], 0
9799  74 08           je 0x97a3
979B  B0 3F           mov al, 0x3f
979D  50              push ax
979E  E8 6E 93        call 0x2b0f
97A1  EB 06           jmp 0x97a9
loc_97A3:
97A3  B0 40           mov al, 0x40
97A5  50              push ax
97A6  E8 66 93        call 0x2b0f
loc_97A9:
97A9  31 C0           xor ax, ax
97AB  A3 00 83        mov word ptr [0x8300], ax
97AE  C6 46 FF 01     mov byte ptr [bp - 1], 1
97B2  B8 03 00        mov ax, 3
97B5  50              push ax
97B6  E8 88 6C        call 0x10441
97B9  B8 04 00        mov ax, 4
97BC  50              push ax
97BD  E8 65 6C        call 0x10425
97C0  B8 06 00        mov ax, 6
97C3  50              push ax
97C4  E8 7A 6C        call 0x10441
loc_97C7:
97C7  8A 46 FF        mov al, byte ptr [bp - 1]
97CA  89 EC           mov sp, bp
97CC  5D              pop bp
97CD  C2 02 00        ret 2

; ---- routine 0791:97D0  (found by: call)
sub_97D0:
97D0  55              push bp
97D1  89 E5           mov bp, sp
loc_97D3:
97D3  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
97D8  74 05           je 0x97df
97DA  E8 56 3F        call 0xd733
97DD  EB 45           jmp 0x9824
loc_97DF:
97DF  80 3E 37 7C 00  cmp byte ptr [0x7c37], 0
97E4  74 05           je 0x97eb
97E6  E8 7C 74        call 0x10c65
97E9  EB 0A           jmp 0x97f5
loc_97EB:
97EB  80 3E 55 9B 00  cmp byte ptr [0x9b55], 0
97F0  74 03           je 0x97f5
97F2  E8 C4 7D        call 0x115b9
loc_97F5:
97F5  80 3E 55 9B 00  cmp byte ptr [0x9b55], 0
97FA  74 05           je 0x9801
97FC  C6 06 20 0C 00  mov byte ptr [0xc20], 0
loc_9801:
9801  C6 06 55 9B 00  mov byte ptr [0x9b55], 0
9806  C6 06 37 7C 00  mov byte ptr [0x7c37], 0
980B  E8 56 FD        call 0x9564
980E  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9813  75 0F           jne 0x9824
9815  E8 DD F4        call 0x8cf5
9818  B0 00           mov al, 0
981A  50              push ax
981B  BF EE 82        mov di, 0x82ee
981E  1E              push ds
981F  57              push di
9820  0E              push cs
9821  E8 F5 F8        call 0x9119
loc_9824:
9824  55              push bp
9825  E8 E4 FE        call 0x970c
9828  08 C0           or al, al
982A  75 0D           jne 0x9839
982C  80 7E 04 00     cmp byte ptr [bp + 4], 0
9830  74 A1           je 0x97d3
9832  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
9837  75 9A           jne 0x97d3
loc_9839:
9839  89 EC           mov sp, bp
983B  5D              pop bp
983C  C2 02 00        ret 2

; ---- routine 0791:983F  (found by: call)
sub_983F:
983F  55              push bp
9840  89 E5           mov bp, sp
9842  83 EC 02        sub sp, 2
9845  C6 06 41 9B 00  mov byte ptr [0x9b41], 0
984A  C6 06 0E 83 00  mov byte ptr [0x830e], 0
984F  E8 10 E8        call 0x8062
9852  E8 C0 91        call 0x2a15
9855  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
985A  75 09           jne 0x9865
985C  B0 01           mov al, 1
985E  50              push ax
985F  E8 C7 90        call 0x2929
9862  E8 65 F4        call 0x8cca
loc_9865:
9865  C6 06 02 83 00  mov byte ptr [0x8302], 0
986A  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
986F  C6 06 20 0C 00  mov byte ptr [0xc20], 0
9874  C6 06 37 7C 00  mov byte ptr [0x7c37], 0
9879  B0 00           mov al, 0
987B  50              push ax
987C  E8 51 FF        call 0x97d0
987F  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9884  75 30           jne 0x98b6
9886  C6 46 FF 00     mov byte ptr [bp - 1], 0
988A  EB 03           jmp 0x988f
loc_988C:
988C  FE 46 FF        inc byte ptr [bp - 1]
loc_988F:
988F  8A 46 FF        mov al, byte ptr [bp - 1]
9892  98              cwde
9893  8B F8           mov di, ax
9895  D1 E7           shl di, 1
9897  8B F7           mov si, di
9899  D1 E7           shl di, 1
989B  03 FE           add di, si
989D  81 C7 E2 82     add di, 0x82e2
98A1  1E              push ds
98A2  57              push di
98A3  0E              push cs
98A4  E8 D2 F7        call 0x9079
98A7  80 7E FF 01     cmp byte ptr [bp - 1], 1
98AB  75 DF           jne 0x988c
98AD  BF EE 82        mov di, 0x82ee
98B0  1E              push ds
98B1  57              push di
98B2  0E              push cs
98B3  E8 C3 F7        call 0x9079
loc_98B6:
98B6  C6 06 25 83 00  mov byte ptr [0x8325], 0
98BB  9A 8D 1E 4B 21  call far 214B:1E8D
98C0  89 EC           mov sp, bp
98C2  5D              pop bp
98C3  C3              ret

; ---- routine 0791:98C4  (found by: call)
sub_98C4:
98C4  55              push bp
98C5  89 E5           mov bp, sp
98C7  83 EC 06        sub sp, 6
98CA  B8 0A 00        mov ax, 0xa
98CD  50              push ax
98CE  9A B1 06 4B 21  call far 214B:06B1
98D3  40              inc ax
98D4  8B D0           mov dx, ax
98D6  A0 3D 9B        mov al, byte ptr [0x9b3d]
98D9  3A 06 3C 9B     cmp al, byte ptr [0x9b3c]
98DD  77 04           ja 0x98e3
98DF  B0 00           mov al, 0
98E1  EB 02           jmp 0x98e5
loc_98E3:
98E3  B0 01           mov al, 1
loc_98E5:
98E5  98              cwde
98E6  8B F8           mov di, ax
98E8  8A 85 68 06     mov al, byte ptr [di + 0x668]
98EC  30 E4           xor ah, ah
98EE  03 C2           add ax, dx
98F0  50              push ax
98F1  B0 03           mov al, 3
98F3  50              push ax
98F4  E8 FA D2        call 0x6bf1
98F7  C6 06 25 83 01  mov byte ptr [0x8325], 1
98FC  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9901  EB 03           jmp 0x9906
loc_9903:
9903  FF 46 FE        inc word ptr [bp - 2]
loc_9906:
9906  8B 46 FE        mov ax, word ptr [bp - 2]
9909  BA 16 00        mov dx, 0x16
990C  F7 E2           mul dx
990E  8B F8           mov di, ax
9910  81 C7 E8 80     add di, 0x80e8
9914  89 7E FA        mov word ptr [bp - 6], di
9917  8C 5E FC        mov word ptr [bp - 4], ds
991A  C4 7E FA        les di, ptr [bp - 6]
991D  06              push es
991E  57              push di
991F  0E              push cs
9920  E8 2E 92        call 0x2b51
9923  08 C0           or al, al
9925  74 08           je 0x992f
9927  C4 7E FA        les di, ptr [bp - 6]
992A  26 C6 45 12 06  mov byte ptr es:[di + 0x12], 6
loc_992F:
992F  83 7E FE 16     cmp word ptr [bp - 2], 0x16
9933  75 CE           jne 0x9903
9935  E8 FF C9        call 0x6337
9938  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
993D  75 0D           jne 0x994c
loc_993F:
993F  E8 22 FC        call 0x9564
9942  B0 01           mov al, 1
9944  50              push ax
9945  E8 6A 8F        call 0x28b2
9948  08 C0           or al, al
994A  74 F3           je 0x993f
loc_994C:
994C  9A 8D 1E 4B 21  call far 214B:1E8D
9951  89 EC           mov sp, bp
9953  5D              pop bp
9954  C3              ret

; ---- routine 0791:9955  (found by: call)
sub_9955:
9955  55              push bp
9956  89 E5           mov bp, sp
9958  C6 06 25 83 00  mov byte ptr [0x8325], 0
995D  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9962  75 06           jne 0x996a
9964  B0 03           mov al, 3
9966  50              push ax
9967  E8 BF 8F        call 0x2929
loc_996A:
996A  C6 06 02 83 00  mov byte ptr [0x8302], 0
996F  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
9974  75 0D           jne 0x9983
loc_9976:
9976  E8 EB FB        call 0x9564
9979  B0 04           mov al, 4
997B  50              push ax
997C  E8 33 8F        call 0x28b2
997F  08 C0           or al, al
9981  74 F3           je 0x9976
loc_9983:
9983  9A 8D 1E 4B 21  call far 214B:1E8D
9988  89 EC           mov sp, bp
998A  5D              pop bp
998B  C3              ret

; ---- routine 0791:998C  (found by: call)
sub_998C:
998C  55              push bp
998D  89 E5           mov bp, sp
998F  83 EC 04        sub sp, 4
9992  C7 06 1B 83 5B 00 mov word ptr [0x831b], 0x5b
9998  C6 06 19 83 2D  mov byte ptr [0x8319], 0x2d
999D  A0 1A 83        mov al, byte ptr [0x831a]
99A0  98              cwde
99A1  8B F8           mov di, ax
99A3  8A 85 68 06     mov al, byte ptr [di + 0x668]
99A7  30 E4           xor ah, ah
99A9  05 0A 00        add ax, 0xa
99AC  A2 0B 83        mov byte ptr [0x830b], al
99AF  E8 E4 8F        call 0x2996
99B2  98              cwde
99B3  8B F8           mov di, ax
99B5  D1 E7           shl di, 1
99B7  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
99BB  BA BF 00        mov dx, 0xbf
99BE  F7 E2           mul dx
99C0  C4 3E 17 A9     les di, ptr [0xa917]
99C4  03 F8           add di, ax
99C6  89 7E FC        mov word ptr [bp - 4], di
99C9  8C 46 FE        mov word ptr [bp - 2], es
99CC  E8 C7 8F        call 0x2996
99CF  50              push ax
99D0  E8 C3 8F        call 0x2996
99D3  50              push ax
99D4  B8 01 00        mov ax, 1
99D7  50              push ax
99D8  E8 8A D1        call 0x6b65
99DB  50              push ax
99DC  31 C0           xor ax, ax
99DE  50              push ax
99DF  B0 3B           mov al, 0x3b
99E1  50              push ax
99E2  E8 D0 84        call 0x1eb5
99E5  E8 57 FE        call 0x983f
99E8  A1 3C 9B        mov ax, word ptr [0x9b3c]
99EB  A3 2C 83        mov word ptr [0x832c], ax
99EE  89 EC           mov sp, bp
99F0  5D              pop bp
99F1  C3              ret
; data (not reached as code), 64 bytes
99F2                  db FE FF FF 7F 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
9A02                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
9A12                  db 00 20 00 08 00 00 00 00 00 00 00 00 00 00 00 00   ; . ..............
9A22                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:9A32  (found by: call)
sub_9A32:
9A32  55              push bp
9A33  89 E5           mov bp, sp
9A35  83 EC 0A        sub sp, 0xa
9A38  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9A3D  EB 03           jmp 0x9a42
loc_9A3F:
9A3F  FF 46 FE        inc word ptr [bp - 2]
loc_9A42:
9A42  8B 46 FE        mov ax, word ptr [bp - 2]
9A45  BA 16 00        mov dx, 0x16
9A48  F7 E2           mul dx
9A4A  8B F8           mov di, ax
9A4C  81 C7 E8 80     add di, 0x80e8
9A50  89 7E FA        mov word ptr [bp - 6], di
9A53  8C 5E FC        mov word ptr [bp - 4], ds
9A56  C4 7E FA        les di, ptr [bp - 6]
9A59  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
9A5D  BA 14 00        mov dx, 0x14
9A60  F7 E2           mul dx
9A62  C4 3E 1B A9     les di, ptr [0xa91b]
9A66  03 F8           add di, ax
9A68  89 7E F6        mov word ptr [bp - 0xa], di
9A6B  8C 46 F8        mov word ptr [bp - 8], es
9A6E  C4 7E F6        les di, ptr [bp - 0xa]
9A71  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
9A75  50              push ax
9A76  BF F2 99        mov di, 0x99f2
9A79  0E              push cs
9A7A  57              push di
9A7B  9A DF 08 E4 23  call far 23E4:08DF
9A80  74 08           je 0x9a8a
9A82  C4 7E F6        les di, ptr [bp - 0xa]
9A85  26 80 45 0E 02  add byte ptr es:[di + 0xe], 2
loc_9A8A:
9A8A  83 7E FE 16     cmp word ptr [bp - 2], 0x16
9A8E  75 AF           jne 0x9a3f
9A90  C6 06 41 9B 01  mov byte ptr [0x9b41], 1
9A95  C4 3E 6A A9     les di, ptr [0xa96a]
9A99  06              push es
9A9A  57              push di
9A9B  C4 3E 72 A9     les di, ptr [0xa972]
9A9F  06              push es
9AA0  57              push di
9AA1  B8 A0 0F        mov ax, 0xfa0
9AA4  50              push ax
9AA5  9A 5D 02 E4 23  call far 23E4:025D
9AAA  B0 01           mov al, 1
9AAC  50              push ax
9AAD  0E              push cs
9AAE  E8 55 66        call 0x10106
9AB1  C4 3E 72 A9     les di, ptr [0xa972]
9AB5  06              push es
9AB6  57              push di
9AB7  C4 3E 6A A9     les di, ptr [0xa96a]
9ABB  06              push es
9ABC  57              push di
9ABD  B8 A0 0F        mov ax, 0xfa0
9AC0  50              push ax
9AC1  9A 5D 02 E4 23  call far 23E4:025D
9AC6  80 3E FD 80 00  cmp byte ptr [0x80fd], 0
9ACB  75 10           jne 0x9add
9ACD  A0 77 A9        mov al, byte ptr [0xa977]
9AD0  50              push ax
9AD1  BF 12 9A        mov di, 0x9a12
9AD4  0E              push cs
9AD5  57              push di
9AD6  9A DF 08 E4 23  call far 23E4:08DF
9ADB  74 06           je 0x9ae3
loc_9ADD:
9ADD  B0 00           mov al, 0
9ADF  50              push ax
9AE0  E8 A7 52        call 0xed8a
loc_9AE3:
9AE3  80 3E 1A 83 00  cmp byte ptr [0x831a], 0
9AE8  74 04           je 0x9aee
9AEA  B0 00           mov al, 0
9AEC  EB 02           jmp 0x9af0
loc_9AEE:
9AEE  B0 01           mov al, 1
loc_9AF0:
9AF0  98              cwde
9AF1  8B F8           mov di, ax
9AF3  8A 85 68 06     mov al, byte ptr [di + 0x668]
9AF7  30 E4           xor ah, ah
9AF9  05 0A 00        add ax, 0xa
9AFC  A2 0B 83        mov byte ptr [0x830b], al
9AFF  C7 06 2A 83 50 00 mov word ptr [0x832a], 0x50
9B05  E8 37 FD        call 0x983f
9B08  89 EC           mov sp, bp
9B0A  5D              pop bp
9B0B  C3              ret

; ---- routine 0791:9B0C  (found by: call)
sub_9B0C:
9B0C  55              push bp
9B0D  89 E5           mov bp, sp
9B0F  C7 06 1B 83 1F 00 mov word ptr [0x831b], 0x1f
9B15  C7 06 1F 83 59 00 mov word ptr [0x831f], 0x59
9B1B  C6 06 26 83 00  mov byte ptr [0x8326], 0
9B20  C6 06 19 83 0F  mov byte ptr [0x8319], 0xf
9B25  31 C0           xor ax, ax
9B27  A3 1D 83        mov word ptr [0x831d], ax
9B2A  B0 3E           mov al, 0x3e
9B2C  50              push ax
9B2D  E8 DF 8F        call 0x2b0f
9B30  C6 06 41 9B 01  mov byte ptr [0x9b41], 1
9B35  80 3E FD 80 00  cmp byte ptr [0x80fd], 0
9B3A  74 06           je 0x9b42
9B3C  B0 01           mov al, 1
9B3E  50              push ax
9B3F  E8 48 52        call 0xed8a
loc_9B42:
9B42  A0 1A 83        mov al, byte ptr [0x831a]
9B45  98              cwde
9B46  8B F8           mov di, ax
9B48  8A 85 68 06     mov al, byte ptr [di + 0x668]
9B4C  30 E4           xor ah, ah
9B4E  05 0A 00        add ax, 0xa
9B51  A2 0B 83        mov byte ptr [0x830b], al
9B54  E8 E8 FC        call 0x983f
9B57  89 EC           mov sp, bp
9B59  5D              pop bp
9B5A  C3              ret

; ---- routine 0791:9B5B  (found by: call)
sub_9B5B:
9B5B  55              push bp
9B5C  89 E5           mov bp, sp
9B5E  C6 06 41 9B 01  mov byte ptr [0x9b41], 1
9B63  80 3E FD 80 00  cmp byte ptr [0x80fd], 0
9B68  74 06           je 0x9b70
9B6A  B0 01           mov al, 1
9B6C  50              push ax
9B6D  E8 1A 52        call 0xed8a
loc_9B70:
9B70  80 3E 1A 83 00  cmp byte ptr [0x831a], 0
9B75  74 04           je 0x9b7b
9B77  B0 00           mov al, 0
9B79  EB 02           jmp 0x9b7d
loc_9B7B:
9B7B  B0 01           mov al, 1
loc_9B7D:
9B7D  98              cwde
9B7E  8B F8           mov di, ax
9B80  8A 85 68 06     mov al, byte ptr [di + 0x668]
9B84  30 E4           xor ah, ah
9B86  05 0A 00        add ax, 0xa
9B89  A2 0B 83        mov byte ptr [0x830b], al
9B8C  E8 B0 FC        call 0x983f
9B8F  89 EC           mov sp, bp
9B91  5D              pop bp
9B92  C3              ret

; ---- routine 0791:9B93  (found by: call)
sub_9B93:
9B93  55              push bp
9B94  89 E5           mov bp, sp
9B96  81 EC 0A 02     sub sp, 0x20a
9B9A  8B 7E 04        mov di, word ptr [bp + 4]
9B9D  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9BA1  98              cwde
9BA2  8B F8           mov di, ax
9BA4  D1 E7           shl di, 1
9BA6  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
9BAA  BA BF 00        mov dx, 0xbf
9BAD  F7 E2           mul dx
9BAF  C4 3E 17 A9     les di, ptr [0xa917]
9BB3  03 F8           add di, ax
9BB5  89 7E F6        mov word ptr [bp - 0xa], di
9BB8  8C 46 F8        mov word ptr [bp - 8], es
9BBB  C4 3E 16 7C     les di, ptr [0x7c16]
9BBF  06              push es
9BC0  57              push di
9BC1  C4 3E 22 7C     les di, ptr [0x7c22]
9BC5  06              push es
9BC6  57              push di
9BC7  B8 A0 0F        mov ax, 0xfa0
9BCA  50              push ax
9BCB  9A 5D 02 E4 23  call far 23E4:025D
9BD0  C7 46 FA 01 00  mov word ptr [bp - 6], 1
9BD5  C7 46 FC 0B 00  mov word ptr [bp - 4], 0xb
9BDA  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9BDF  EB 03           jmp 0x9be4
loc_9BE1:
9BE1  FF 46 FE        inc word ptr [bp - 2]
loc_9BE4:
9BE4  8B 46 FE        mov ax, word ptr [bp - 2]
9BE7  D1 E0           shl ax, 1
9BE9  C4 7E F6        les di, ptr [bp - 0xa]
9BEC  03 F8           add di, ax
9BEE  26 FF 75 FE     push word ptr es:[di - 2]
9BF2  9A 16 32 71 17  call far 1771:3216
9BF7  08 C0           or al, al
9BF9  74 03           je 0x9bfe
9BFB  FF 4E FC        dec word ptr [bp - 4]
loc_9BFE:
9BFE  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
9C02  75 DD           jne 0x9be1
9C04  BF 80 47        mov di, 0x4780
9C07  1E              push ds
9C08  57              push di
9C09  BF 6E A9        mov di, 0xa96e
9C0C  1E              push ds
9C0D  57              push di
9C0E  9A 29 03 4B 21  call far 214B:0329
9C13  8B 7E 04        mov di, word ptr [bp + 4]
9C16  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9C1A  98              cwde
9C1B  8B F8           mov di, ax
9C1D  D1 E7           shl di, 1
9C1F  FF B5 34 9B     push word ptr [di - 0x64cc]
9C23  B8 19 00        mov ax, 0x19
9C26  50              push ax
9C27  B8 01 00        mov ax, 1
9C2A  50              push ax
9C2B  9A 58 0F 71 17  call far 1771:0F58
9C30  BF 5E 24        mov di, 0x245e
9C33  1E              push ds
9C34  57              push di
9C35  BF 6E A9        mov di, 0xa96e
9C38  1E              push ds
9C39  57              push di
9C3A  9A 29 03 4B 21  call far 214B:0329
loc_9C3F:
9C3F  BF C4 5F        mov di, 0x5fc4
9C42  1E              push ds
9C43  57              push di
9C44  BF 6E A9        mov di, 0xa96e
9C47  1E              push ds
9C48  57              push di
9C49  9A 29 03 4B 21  call far 214B:0329
9C4E  8B 46 FA        mov ax, word ptr [bp - 6]
9C51  D1 E0           shl ax, 1
9C53  C4 7E F6        les di, ptr [bp - 0xa]
9C56  03 F8           add di, ax
9C58  26 FF 75 FE     push word ptr es:[di - 2]
9C5C  9A BC 42 71 17  call far 1771:42BC
9C61  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9C66  EB 03           jmp 0x9c6b
loc_9C68:
9C68  FF 46 FE        inc word ptr [bp - 2]
loc_9C6B:
9C6B  8D BE F6 FE     lea di, [bp - 0x10a]
9C6F  16              push ss
9C70  57              push di
9C71  8B 7E 04        mov di, word ptr [bp + 4]
9C74  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9C78  98              cwde
9C79  8B F8           mov di, ax
9C7B  8A 85 68 06     mov al, byte ptr [di + 0x668]
9C7F  30 E4           xor ah, ah
9C81  03 46 FE        add ax, word ptr [bp - 2]
9C84  50              push ax
9C85  9A 5A 07 E4 23  call far 23E4:075A
9C8A  8B 7E 04        mov di, word ptr [bp + 4]
9C8D  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9C91  98              cwde
9C92  BA 0C 00        mov dx, 0xc
9C95  F7 E2           mul dx
9C97  8B 7E 04        mov di, word ptr [bp + 4]
9C9A  03 F8           add di, ax
9C9C  81 C7 E6 FF     add di, 0xffe6
9CA0  16              push ss
9CA1  57              push di
9CA2  9A E3 06 E4 23  call far 23E4:06E3
9CA7  09 C0           or ax, ax
9CA9  75 1C           jne 0x9cc7
9CAB  8B 46 FE        mov ax, word ptr [bp - 2]
9CAE  D1 E0           shl ax, 1
9CB0  C4 7E F6        les di, ptr [bp - 0xa]
9CB3  03 F8           add di, ax
9CB5  26 FF 75 FE     push word ptr es:[di - 2]
9CB9  8B 46 FE        mov ax, word ptr [bp - 2]
9CBC  40              inc ax
9CBD  50              push ax
9CBE  B8 41 00        mov ax, 0x41
9CC1  50              push ax
9CC2  9A 37 2F 71 17  call far 1771:2F37
loc_9CC7:
9CC7  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
9CCB  75 9B           jne 0x9c68
9CCD  8B 46 FA        mov ax, word ptr [bp - 6]
9CD0  40              inc ax
9CD1  50              push ax
9CD2  B8 41 00        mov ax, 0x41
9CD5  50              push ax
9CD6  B8 0D 00        mov ax, 0xd
9CD9  50              push ax
9CDA  9A C5 13 4B 21  call far 214B:13C5
9CDF  8B 7E 04        mov di, word ptr [bp + 4]
9CE2  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9CE6  98              cwde
9CE7  BA 0C 00        mov dx, 0xc
9CEA  F7 E2           mul dx
9CEC  8B 7E 04        mov di, word ptr [bp + 4]
9CEF  03 F8           add di, ax
9CF1  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
9CF5  30 E4           xor ah, ah
9CF7  89 46 F4        mov word ptr [bp - 0xc], ax
9CFA  B8 01 00        mov ax, 1
9CFD  3B 46 F4        cmp ax, word ptr [bp - 0xc]
9D00  77 57           ja 0x9d59
9D02  89 46 FE        mov word ptr [bp - 2], ax
9D05  EB 03           jmp 0x9d0a
loc_9D07:
9D07  FF 46 FE        inc word ptr [bp - 2]
loc_9D0A:
9D0A  8B 46 FE        mov ax, word ptr [bp - 2]
9D0D  8B C8           mov cx, ax
9D0F  8B 7E 04        mov di, word ptr [bp + 4]
9D12  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9D16  98              cwde
9D17  BA 0C 00        mov dx, 0xc
9D1A  F7 E2           mul dx
9D1C  8B 7E 04        mov di, word ptr [bp + 4]
9D1F  03 F8           add di, ax
9D21  03 F9           add di, cx
9D23  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
9D27  30 E4           xor ah, ah
9D29  BA 16 00        mov dx, 0x16
9D2C  F7 E2           mul dx
9D2E  8B F8           mov di, ax
9D30  81 C7 E8 80     add di, 0x80e8
9D34  89 7E F0        mov word ptr [bp - 0x10], di
9D37  8C 5E F2        mov word ptr [bp - 0xe], ds
9D3A  C4 7E F0        les di, ptr [bp - 0x10]
9D3D  26 FF 75 0D     push word ptr es:[di + 0xd]
9D41  8B 46 FE        mov ax, word ptr [bp - 2]
9D44  05 0D 00        add ax, 0xd
9D47  50              push ax
9D48  B8 41 00        mov ax, 0x41
9D4B  50              push ax
9D4C  9A 37 2F 71 17  call far 1771:2F37
9D51  8B 46 FE        mov ax, word ptr [bp - 2]
9D54  3B 46 F4        cmp ax, word ptr [bp - 0xc]
9D57  75 AE           jne 0x9d07
loc_9D59:
9D59  8D 7E FA        lea di, [bp - 6]
9D5C  16              push ss
9D5D  57              push di
9D5E  B8 0B 00        mov ax, 0xb
9D61  50              push ax
9D62  9A 60 15 4B 21  call far 214B:1560
loc_9D67:
9D67  8D BE F6 FE     lea di, [bp - 0x10a]
9D6B  16              push ss
9D6C  57              push di
9D6D  8B 7E 04        mov di, word ptr [bp + 4]
9D70  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9D74  98              cwde
9D75  8B F8           mov di, ax
9D77  8A 85 68 06     mov al, byte ptr [di + 0x668]
9D7B  30 E4           xor ah, ah
9D7D  03 46 FA        add ax, word ptr [bp - 6]
9D80  50              push ax
9D81  9A 5A 07 E4 23  call far 23E4:075A
9D86  8B 7E 04        mov di, word ptr [bp + 4]
9D89  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9D8D  98              cwde
9D8E  BA 0C 00        mov dx, 0xc
9D91  F7 E2           mul dx
9D93  8B 7E 04        mov di, word ptr [bp + 4]
9D96  03 F8           add di, ax
9D98  81 C7 E6 FF     add di, 0xffe6
9D9C  16              push ss
9D9D  57              push di
9D9E  9A E3 06 E4 23  call far 23E4:06E3
9DA3  09 C0           or ax, ax
9DA5  7F 17           jg 0x9dbe
9DA7  8B 46 FA        mov ax, word ptr [bp - 6]
9DAA  D1 E0           shl ax, 1
9DAC  C4 7E F6        les di, ptr [bp - 0xa]
9DAF  03 F8           add di, ax
9DB1  26 FF 75 FE     push word ptr es:[di - 2]
9DB5  9A 16 32 71 17  call far 1771:3216
9DBA  08 C0           or al, al
9DBC  74 2B           je 0x9de9
loc_9DBE:
9DBE  8D 7E FA        lea di, [bp - 6]
9DC1  16              push ss
9DC2  57              push di
9DC3  B8 01 00        mov ax, 1
9DC6  50              push ax
9DC7  B8 0B 00        mov ax, 0xb
9DCA  50              push ax
9DCB  80 3E 76 A9 B1  cmp byte ptr [0xa976], 0xb1
9DD0  74 04           je 0x9dd6
9DD2  B0 00           mov al, 0
9DD4  EB 02           jmp 0x9dd8
loc_9DD6:
9DD6  B0 01           mov al, 1
loc_9DD8:
9DD8  98              cwde
9DD9  8B F8           mov di, ax
9DDB  8A 85 20 79     mov al, byte ptr [di + 0x7920]
9DDF  98              cwde
9DE0  50              push ax
9DE1  9A 86 1C 4B 21  call far 214B:1C86
9DE6  E9 7E FF        jmp 0x9d67
loc_9DE9:
9DE9  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
9DEE  75 72           jne 0x9e62
9DF0  8D BE F6 FD     lea di, [bp - 0x20a]
9DF4  16              push ss
9DF5  57              push di
9DF6  8B 7E 04        mov di, word ptr [bp + 4]
9DF9  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9DFD  98              cwde
9DFE  BA 0C 00        mov dx, 0xc
9E01  F7 E2           mul dx
9E03  8B 7E 04        mov di, word ptr [bp + 4]
9E06  03 F8           add di, ax
9E08  81 C7 E6 FF     add di, 0xffe6
9E0C  16              push ss
9E0D  57              push di
9E0E  9A 2A 06 E4 23  call far 23E4:062A
9E13  8D BE F6 FE     lea di, [bp - 0x10a]
9E17  16              push ss
9E18  57              push di
9E19  8B 7E 04        mov di, word ptr [bp + 4]
9E1C  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9E20  98              cwde
9E21  8B F8           mov di, ax
9E23  8A 85 68 06     mov al, byte ptr [di + 0x668]
9E27  30 E4           xor ah, ah
9E29  03 46 FA        add ax, word ptr [bp - 6]
9E2C  50              push ax
9E2D  9A 5A 07 E4 23  call far 23E4:075A
9E32  9A B7 06 E4 23  call far 23E4:06B7
9E37  8B 7E 04        mov di, word ptr [bp + 4]
9E3A  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9E3E  98              cwde
9E3F  BA 0C 00        mov dx, 0xc
9E42  F7 E2           mul dx
9E44  8B 7E 04        mov di, word ptr [bp + 4]
9E47  03 F8           add di, ax
9E49  81 C7 E6 FF     add di, 0xffe6
9E4D  16              push ss
9E4E  57              push di
9E4F  B8 0B 00        mov ax, 0xb
9E52  50              push ax
9E53  9A 44 06 E4 23  call far 23E4:0644
9E58  B0 B1           mov al, 0xb1
9E5A  50              push ax
9E5B  9A 93 09 4B 21  call far 214B:0993
9E60  EB 36           jmp 0x9e98
loc_9E62:
9E62  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
9E67  75 2F           jne 0x9e98
9E69  8B 7E 04        mov di, word ptr [bp + 4]
9E6C  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9E70  98              cwde
9E71  BA 0C 00        mov dx, 0xc
9E74  F7 E2           mul dx
9E76  8B 7E 04        mov di, word ptr [bp + 4]
9E79  03 F8           add di, ax
9E7B  36 80 7D E6 00  cmp byte ptr ss:[di - 0x1a], 0
9E80  76 16           jbe 0x9e98
9E82  8B 7E 04        mov di, word ptr [bp + 4]
9E85  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9E89  98              cwde
9E8A  BA 0C 00        mov dx, 0xc
9E8D  F7 E2           mul dx
9E8F  8B 7E 04        mov di, word ptr [bp + 4]
9E92  03 F8           add di, ax
9E94  36 FE 4D E6     dec byte ptr ss:[di - 0x1a]
loc_9E98:
9E98  8B 7E 04        mov di, word ptr [bp + 4]
9E9B  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9E9F  98              cwde
9EA0  BA 0C 00        mov dx, 0xc
9EA3  F7 E2           mul dx
9EA5  8B 7E 04        mov di, word ptr [bp + 4]
9EA8  03 F8           add di, ax
9EAA  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
9EAE  30 E4           xor ah, ah
9EB0  3B 46 FC        cmp ax, word ptr [bp - 4]
9EB3  74 03           je 0x9eb8
9EB5  E9 87 FD        jmp 0x9c3f
loc_9EB8:
9EB8  C4 3E 22 7C     les di, ptr [0x7c22]
9EBC  06              push es
9EBD  57              push di
9EBE  C4 3E 16 7C     les di, ptr [0x7c16]
9EC2  06              push es
9EC3  57              push di
9EC4  B8 A0 0F        mov ax, 0xfa0
9EC7  50              push ax
9EC8  9A 5D 02 E4 23  call far 23E4:025D
9ECD  89 EC           mov sp, bp
9ECF  5D              pop bp
9ED0  C2 02 00        ret 2

; ---- routine 0791:9ED3  (found by: call)
sub_9ED3:
9ED3  55              push bp
9ED4  89 E5           mov bp, sp
9ED6  83 EC 04        sub sp, 4
9ED9  C7 46 FE 01 00  mov word ptr [bp - 2], 1
9EDE  EB 03           jmp 0x9ee3
loc_9EE0:
9EE0  FF 46 FE        inc word ptr [bp - 2]
loc_9EE3:
9EE3  8B 7E 04        mov di, word ptr [bp + 4]
9EE6  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9EEA  98              cwde
9EEB  8B F8           mov di, ax
9EED  8A 85 68 06     mov al, byte ptr [di + 0x668]
9EF1  30 E4           xor ah, ah
9EF3  03 46 FE        add ax, word ptr [bp - 2]
9EF6  8A D8           mov bl, al
9EF8  8B 46 FE        mov ax, word ptr [bp - 2]
9EFB  8B C8           mov cx, ax
9EFD  8B 7E 04        mov di, word ptr [bp + 4]
9F00  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9F04  98              cwde
9F05  BA 0C 00        mov dx, 0xc
9F08  F7 E2           mul dx
9F0A  8B 7E 04        mov di, word ptr [bp + 4]
9F0D  03 F8           add di, ax
9F0F  03 F9           add di, cx
9F11  36 88 5D E6     mov byte ptr ss:[di - 0x1a], bl
9F15  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
9F19  75 C5           jne 0x9ee0
9F1B  C7 46 FC 01 00  mov word ptr [bp - 4], 1
9F20  EB 03           jmp 0x9f25
loc_9F22:
9F22  FF 46 FC        inc word ptr [bp - 4]
loc_9F25:
9F25  8B 46 FC        mov ax, word ptr [bp - 4]
9F28  40              inc ax
9F29  3D 0B 00        cmp ax, 0xb
9F2C  76 03           jbe 0x9f31
9F2E  E9 C6 00        jmp 0x9ff7
loc_9F31:
9F31  89 46 FE        mov word ptr [bp - 2], ax
9F34  EB 03           jmp 0x9f39
loc_9F36:
9F36  FF 46 FE        inc word ptr [bp - 2]
loc_9F39:
9F39  B8 0C 00        mov ax, 0xc
9F3C  50              push ax
9F3D  8B 46 FC        mov ax, word ptr [bp - 4]
9F40  8B C8           mov cx, ax
9F42  8B 7E 04        mov di, word ptr [bp + 4]
9F45  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9F49  98              cwde
9F4A  BA 0C 00        mov dx, 0xc
9F4D  F7 E2           mul dx
9F4F  8B 7E 04        mov di, word ptr [bp + 4]
9F52  03 F8           add di, ax
9F54  03 F9           add di, cx
9F56  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
9F5A  30 E4           xor ah, ah
9F5C  BA 16 00        mov dx, 0x16
9F5F  F7 E2           mul dx
9F61  8B F8           mov di, ax
9F63  81 C7 E8 80     add di, 0x80e8
9F67  1E              push ds
9F68  57              push di
9F69  0E              push cs
9F6A  E8 1D 88        call 0x278a
9F6D  50              push ax
9F6E  B8 0C 00        mov ax, 0xc
9F71  50              push ax
9F72  8B 46 FE        mov ax, word ptr [bp - 2]
9F75  8B C8           mov cx, ax
9F77  8B 7E 04        mov di, word ptr [bp + 4]
9F7A  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9F7E  98              cwde
9F7F  BA 0C 00        mov dx, 0xc
9F82  F7 E2           mul dx
9F84  8B 7E 04        mov di, word ptr [bp + 4]
9F87  03 F8           add di, ax
9F89  03 F9           add di, cx
9F8B  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
9F8F  30 E4           xor ah, ah
9F91  BA 16 00        mov dx, 0x16
9F94  F7 E2           mul dx
9F96  8B F8           mov di, ax
9F98  81 C7 E8 80     add di, 0x80e8
9F9C  1E              push ds
9F9D  57              push di
9F9E  0E              push cs
9F9F  E8 E8 87        call 0x278a
9FA2  5A              pop dx
9FA3  3B C2           cmp ax, dx
9FA5  76 47           jbe 0x9fee
9FA7  8B 46 FE        mov ax, word ptr [bp - 2]
9FAA  8B C8           mov cx, ax
9FAC  8B 7E 04        mov di, word ptr [bp + 4]
9FAF  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9FB3  98              cwde
9FB4  BA 0C 00        mov dx, 0xc
9FB7  F7 E2           mul dx
9FB9  8B 7E 04        mov di, word ptr [bp + 4]
9FBC  03 F8           add di, ax
9FBE  03 F9           add di, cx
9FC0  81 C7 E6 FF     add di, 0xffe6
9FC4  16              push ss
9FC5  57              push di
9FC6  8B 46 FC        mov ax, word ptr [bp - 4]
9FC9  8B C8           mov cx, ax
9FCB  8B 7E 04        mov di, word ptr [bp + 4]
9FCE  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
9FD2  98              cwde
9FD3  BA 0C 00        mov dx, 0xc
9FD6  F7 E2           mul dx
9FD8  8B 7E 04        mov di, word ptr [bp + 4]
9FDB  03 F8           add di, ax
9FDD  03 F9           add di, cx
9FDF  81 C7 E6 FF     add di, 0xffe6
9FE3  16              push ss
9FE4  57              push di
9FE5  B8 01 00        mov ax, 1
9FE8  50              push ax
9FE9  9A 7B 00 4B 21  call far 214B:007B
loc_9FEE:
9FEE  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
9FF2  74 03           je 0x9ff7
9FF4  E9 3F FF        jmp 0x9f36
loc_9FF7:
9FF7  83 7E FC 0A     cmp word ptr [bp - 4], 0xa
9FFB  74 03           je 0xa000
9FFD  E9 22 FF        jmp 0x9f22
loc_A000:
A000  89 EC           mov sp, bp
A002  5D              pop bp
A003  C2 02 00        ret 2

; ---- routine 0791:A006  (found by: call)
sub_A006:
A006  55              push bp
A007  89 E5           mov bp, sp
A009  83 EC 02        sub sp, 2
A00C  FF 36 1D 83     push word ptr [0x831d]
A010  8B 7E 04        mov di, word ptr [bp + 4]
A013  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A017  98              cwde
A018  8B F8           mov di, ax
A01A  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
A01E  30 E4           xor ah, ah
A020  50              push ax
A021  E8 28 65        call 0x1054c
A024  8B 7E 04        mov di, word ptr [bp + 4]
A027  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A02B  30 E4           xor ah, ah
A02D  F7 D8           neg ax
A02F  A2 19 83        mov byte ptr [0x8319], al
A032  8B 7E 04        mov di, word ptr [bp + 4]
A035  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A039  98              cwde
A03A  8B 7E 04        mov di, word ptr [bp + 4]
A03D  03 F8           add di, ax
A03F  36 8A 45 E2     mov al, byte ptr ss:[di - 0x1e]
A043  30 E4           xor ah, ah
A045  8B C8           mov cx, ax
A047  8B 7E 04        mov di, word ptr [bp + 4]
A04A  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A04E  98              cwde
A04F  BA 0C 00        mov dx, 0xc
A052  F7 E2           mul dx
A054  8B 7E 04        mov di, word ptr [bp + 4]
A057  03 F8           add di, ax
A059  03 F9           add di, cx
A05B  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
A05F  30 E4           xor ah, ah
A061  50              push ax
A062  B0 0A           mov al, 0xa
A064  50              push ax
A065  E8 89 CB        call 0x6bf1
loc_A068:
A068  8B 7E 04        mov di, word ptr [bp + 4]
A06B  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A06F  98              cwde
A070  8B 7E 04        mov di, word ptr [bp + 4]
A073  03 F8           add di, ax
A075  81 C7 E2 FF     add di, 0xffe2
A079  16              push ss
A07A  57              push di
A07B  B0 01           mov al, 1
A07D  50              push ax
A07E  B0 0B           mov al, 0xb
A080  50              push ax
A081  B8 01 00        mov ax, 1
A084  50              push ax
A085  9A 6F 1D 4B 21  call far 214B:1D6F
A08A  8B 7E 04        mov di, word ptr [bp + 4]
A08D  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A091  98              cwde
A092  8B 7E 04        mov di, word ptr [bp + 4]
A095  03 F8           add di, ax
A097  36 8A 45 E2     mov al, byte ptr ss:[di - 0x1e]
A09B  30 E4           xor ah, ah
A09D  8B C8           mov cx, ax
A09F  8B 7E 04        mov di, word ptr [bp + 4]
A0A2  36 8A 45 E1     mov al, byte ptr ss:[di - 0x1f]
A0A6  98              cwde
A0A7  BA 0C 00        mov dx, 0xc
A0AA  F7 E2           mul dx
A0AC  8B 7E 04        mov di, word ptr [bp + 4]
A0AF  03 F8           add di, ax
A0B1  03 F9           add di, cx
A0B3  36 8A 45 E6     mov al, byte ptr ss:[di - 0x1a]
A0B7  30 E4           xor ah, ah
A0B9  BA 16 00        mov dx, 0x16
A0BC  F7 E2           mul dx
A0BE  8B F8           mov di, ax
A0C0  81 C7 E8 80     add di, 0x80e8
A0C4  1E              push ds
A0C5  57              push di
A0C6  0E              push cs
A0C7  E8 8C 88        call 0x2956
A0CA  08 C0           or al, al
A0CC  75 9A           jne 0xa068
A0CE  C6 06 24 83 01  mov byte ptr [0x8324], 1
A0D3  C6 06 25 83 00  mov byte ptr [0x8325], 0
loc_A0D8:
A0D8  E8 89 F4        call 0x9564
A0DB  80 3E 24 83 00  cmp byte ptr [0x8324], 0
A0E0  75 F6           jne 0xa0d8
A0E2  B0 00           mov al, 0
A0E4  50              push ax
A0E5  E8 41 88        call 0x2929
loc_A0E8:
A0E8  E8 79 F4        call 0x9564
A0EB  83 3E 00 83 00  cmp word ptr [0x8300], 0
A0F0  75 F6           jne 0xa0e8
A0F2  89 EC           mov sp, bp
A0F4  5D              pop bp
A0F5  C2 02 00        ret 2
; data (not reached as code), 18 bytes
A0F8                  pstr 'penalty shoot out'

; ---- routine 0791:A10A  (found by: call)
sub_A10A:
A10A  55              push bp
A10B  89 E5           mov bp, sp
A10D  83 EC 22        sub sp, 0x22
A110  C4 3E 23 A9     les di, ptr [0xa923]
A114  26 8A 45 3F     mov al, byte ptr es:[di + 0x3f]
A118  30 E4           xor ah, ah
A11A  89 46 DF        mov word ptr [bp - 0x21], ax
A11D  E8 EB 6A        call 0x10c0b
A120  B0 00           mov al, 0
A122  50              push ax
A123  E8 03 88        call 0x2929
A126  80 3E FD 80 00  cmp byte ptr [0x80fd], 0
A12B  74 0A           je 0xa137
A12D  BF F8 A0        mov di, 0xa0f8
A130  0E              push cs
A131  57              push di
A132  9A F8 04 4B 21  call far 214B:04F8
loc_A137:
A137  C6 06 3E 9A 00  mov byte ptr [0x9a3e], 0
A13C  8D 7E E6        lea di, [bp - 0x1a]
A13F  16              push ss
A140  57              push di
A141  B8 18 00        mov ax, 0x18
A144  50              push ax
A145  31 C0           xor ax, ax
A147  50              push ax
A148  9A 18 00 4B 21  call far 214B:0018
A14D  C6 46 E1 00     mov byte ptr [bp - 0x1f], 0
A151  EB 03           jmp 0xa156
loc_A153:
A153  FE 46 E1        inc byte ptr [bp - 0x1f]
loc_A156:
A156  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A159  98              cwde
A15A  8B F8           mov di, ax
A15C  C6 43 E2 01     mov byte ptr [bp + di - 0x1e], 1
A160  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A163  98              cwde
A164  8B F8           mov di, ax
A166  C6 43 E4 05     mov byte ptr [bp + di - 0x1c], 5
A16A  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A16D  98              cwde
A16E  8B F8           mov di, ax
A170  D1 E7           shl di, 1
A172  FF B5 34 9B     push word ptr [di - 0x64cc]
A176  9A 77 0B 71 17  call far 1771:0B77
A17B  08 C0           or al, al
A17D  74 06           je 0xa185
A17F  55              push bp
A180  E8 10 FA        call 0x9b93
A183  EB 04           jmp 0xa189
loc_A185:
A185  55              push bp
A186  E8 4A FD        call 0x9ed3
loc_A189:
A189  80 7E E1 01     cmp byte ptr [bp - 0x1f], 1
A18D  75 C4           jne 0xa153
A18F  C7 06 1D 83 01 00 mov word ptr [0x831d], 1
A195  A0 1A 83        mov al, byte ptr [0x831a]
A198  88 46 E1        mov byte ptr [bp - 0x1f], al
A19B  E8 A3 06        call 0xa841
A19E  C4 3E 1E 7C     les di, ptr [0x7c1e]
A1A2  06              push es
A1A3  57              push di
A1A4  C4 3E 16 7C     les di, ptr [0x7c16]
A1A8  06              push es
A1A9  57              push di
A1AA  B8 A0 0F        mov ax, 0xfa0
A1AD  50              push ax
A1AE  9A 5D 02 E4 23  call far 23E4:025D
A1B3  B0 3D           mov al, 0x3d
A1B5  50              push ax
A1B6  E8 56 89        call 0x2b0f
loc_A1B9:
A1B9  A0 3C 9B        mov al, byte ptr [0x9b3c]
A1BC  30 E4           xor ah, ah
A1BE  8B C8           mov cx, ax
A1C0  8A 46 E5        mov al, byte ptr [bp - 0x1b]
A1C3  30 E4           xor ah, ah
A1C5  8B D0           mov dx, ax
A1C7  A0 3D 9B        mov al, byte ptr [0x9b3d]
A1CA  30 E4           xor ah, ah
A1CC  03 C2           add ax, dx
A1CE  3B C1           cmp ax, cx
A1D0  7C 79           jl 0xa24b
A1D2  A0 3D 9B        mov al, byte ptr [0x9b3d]
A1D5  30 E4           xor ah, ah
A1D7  8B C8           mov cx, ax
A1D9  8A 46 E4        mov al, byte ptr [bp - 0x1c]
A1DC  30 E4           xor ah, ah
A1DE  8B D0           mov dx, ax
A1E0  A0 3C 9B        mov al, byte ptr [0x9b3c]
A1E3  30 E4           xor ah, ah
A1E5  03 C2           add ax, dx
A1E7  3B C1           cmp ax, cx
A1E9  7C 60           jl 0xa24b
A1EB  55              push bp
A1EC  E8 17 FE        call 0xa006
A1EF  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A1F2  98              cwde
A1F3  8B F8           mov di, ax
A1F5  80 7B E4 00     cmp byte ptr [bp + di - 0x1c], 0
A1F9  76 09           jbe 0xa204
A1FB  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A1FE  98              cwde
A1FF  8B F8           mov di, ax
A201  FE 4B E4        dec byte ptr [bp + di - 0x1c]
loc_A204:
A204  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A207  3A 06 1A 83     cmp al, byte ptr [0x831a]
A20B  75 1F           jne 0xa22c
A20D  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A210  98              cwde
A211  8B F8           mov di, ax
A213  80 7B E4 00     cmp byte ptr [bp + di - 0x1c], 0
A217  75 13           jne 0xa22c
A219  80 7E E1 00     cmp byte ptr [bp - 0x1f], 0
A21D  74 04           je 0xa223
A21F  B0 00           mov al, 0
A221  EB 02           jmp 0xa225
loc_A223:
A223  B0 01           mov al, 1
loc_A225:
A225  98              cwde
A226  8B F8           mov di, ax
A228  C6 43 E4 01     mov byte ptr [bp + di - 0x1c], 1
loc_A22C:
A22C  8A 46 E1        mov al, byte ptr [bp - 0x1f]
A22F  3A 06 1A 83     cmp al, byte ptr [0x831a]
A233  74 04           je 0xa239
A235  FF 06 1D 83     inc word ptr [0x831d]
loc_A239:
A239  80 7E E1 00     cmp byte ptr [bp - 0x1f], 0
A23D  74 04           je 0xa243
A23F  B0 00           mov al, 0
A241  EB 02           jmp 0xa245
loc_A243:
A243  B0 01           mov al, 1
loc_A245:
A245  88 46 E1        mov byte ptr [bp - 0x1f], al
A248  E9 6E FF        jmp 0xa1b9
loc_A24B:
A24B  8A 46 DF        mov al, byte ptr [bp - 0x21]
A24E  C4 3E 23 A9     les di, ptr [0xa923]
A252  26 88 45 3F     mov byte ptr es:[di + 0x3f], al
A256  A0 3F 9A        mov al, byte ptr [0x9a3f]
A259  A2 3E 9A        mov byte ptr [0x9a3e], al
A25C  89 EC           mov sp, bp
A25E  5D              pop bp
A25F  C3              ret

