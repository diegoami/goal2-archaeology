; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 21 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:D016  (found by: call)
sub_D016:
D016  55              push bp
D017  89 E5           mov bp, sp
D019  8B 46 06        mov ax, word ptr [bp + 6]
D01C  C4 7E 08        les di, ptr [bp + 8]
D01F  03 F8           add di, ax
D021  26 FE 45 03     inc byte ptr es:[di + 3]
D025  C4 7E 08        les di, ptr [bp + 8]
D028  26 FE 45 05     inc byte ptr es:[di + 5]
D02C  89 EC           mov sp, bp
D02E  5D              pop bp
D02F  C2 08 00        ret 8

; ---- routine 0791:D032  (found by: call)
sub_D032:
D032  55              push bp
D033  89 E5           mov bp, sp
D035  8B 46 06        mov ax, word ptr [bp + 6]
D038  C4 7E 08        les di, ptr [bp + 8]
D03B  03 F8           add di, ax
D03D  26 C6 45 03 00  mov byte ptr es:[di + 3], 0
D042  C4 7E 08        les di, ptr [bp + 8]
D045  26 C6 45 05 00  mov byte ptr es:[di + 5], 0
D04A  89 EC           mov sp, bp
D04C  5D              pop bp
D04D  C2 08 00        ret 8

; ---- routine 0791:D050  (found by: call, far)
sub_D050:
D050  55              push bp
D051  89 E5           mov bp, sp
D053  83 EC 0E        sub sp, 0xe
D056  C4 7E 06        les di, ptr [bp + 6]
D059  89 7E F7        mov word ptr [bp - 9], di
D05C  8C 46 F9        mov word ptr [bp - 7], es
D05F  C6 46 FF 00     mov byte ptr [bp - 1], 0
D063  EB 03           jmp 0xd068
loc_D065:
D065  FE 46 FF        inc byte ptr [bp - 1]
loc_D068:
D068  8A 46 FF        mov al, byte ptr [bp - 1]
D06B  98              cwde
D06C  D1 E0           shl ax, 1
D06E  C4 7E F7        les di, ptr [bp - 9]
D071  03 F8           add di, ax
D073  26 8B 45 04     mov ax, word ptr es:[di + 4]
D077  BA BF 00        mov dx, 0xbf
D07A  F7 E2           mul dx
D07C  C4 3E 17 A9     les di, ptr [0xa917]
D080  03 F8           add di, ax
D082  81 C7 3B 00     add di, 0x3b
D086  89 7E F3        mov word ptr [bp - 0xd], di
D089  8C 46 F5        mov word ptr [bp - 0xb], es
D08C  C4 7E F7        les di, ptr [bp - 9]
D08F  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
D094  75 09           jne 0xd09f
D096  C4 7E F3        les di, ptr [bp - 0xd]
D099  26 FE 45 02     inc byte ptr es:[di + 2]
D09D  EB 1C           jmp 0xd0bb
loc_D09F:
D09F  C4 7E F7        les di, ptr [bp - 9]
D0A2  26 8A 45 03     mov al, byte ptr es:[di + 3]
D0A6  3A 46 FF        cmp al, byte ptr [bp - 1]
D0A9  75 09           jne 0xd0b4
D0AB  C4 7E F3        les di, ptr [bp - 0xd]
D0AE  26 FE 45 01     inc byte ptr es:[di + 1]
D0B2  EB 07           jmp 0xd0bb
loc_D0B4:
D0B4  C4 7E F3        les di, ptr [bp - 0xd]
D0B7  26 FE 45 03     inc byte ptr es:[di + 3]
loc_D0BB:
D0BB  8A 46 FF        mov al, byte ptr [bp - 1]
D0BE  98              cwde
D0BF  C4 7E F7        les di, ptr [bp - 9]
D0C2  03 F8           add di, ax
D0C4  26 8A 05        mov al, byte ptr es:[di]
D0C7  C4 7E F3        les di, ptr [bp - 0xd]
D0CA  26 00 45 04     add byte ptr es:[di + 4], al
D0CE  80 7E FF 00     cmp byte ptr [bp - 1], 0
D0D2  74 04           je 0xd0d8
D0D4  B0 00           mov al, 0
D0D6  EB 02           jmp 0xd0da
loc_D0D8:
D0D8  B0 01           mov al, 1
loc_D0DA:
D0DA  98              cwde
D0DB  C4 7E F7        les di, ptr [bp - 9]
D0DE  03 F8           add di, ax
D0E0  26 8A 05        mov al, byte ptr es:[di]
D0E3  C4 7E F3        les di, ptr [bp - 0xd]
D0E6  26 00 45 05     add byte ptr es:[di + 5], al
D0EA  80 7E FF 01     cmp byte ptr [bp - 1], 1
D0EE  74 03           je 0xd0f3
D0F0  E9 72 FF        jmp 0xd065
loc_D0F3:
D0F3  C6 46 FF 00     mov byte ptr [bp - 1], 0
D0F7  EB 03           jmp 0xd0fc
loc_D0F9:
D0F9  FE 46 FF        inc byte ptr [bp - 1]
loc_D0FC:
D0FC  8A 46 FF        mov al, byte ptr [bp - 1]
D0FF  98              cwde
D100  D1 E0           shl ax, 1
D102  C4 7E F7        les di, ptr [bp - 9]
D105  03 F8           add di, ax
D107  26 8B 45 04     mov ax, word ptr es:[di + 4]
D10B  BA BF 00        mov dx, 0xbf
D10E  F7 E2           mul dx
D110  C4 3E 17 A9     les di, ptr [0xa917]
D114  03 F8           add di, ax
D116  89 7E F3        mov word ptr [bp - 0xd], di
D119  8C 46 F5        mov word ptr [bp - 0xb], es
D11C  80 7E FF 01     cmp byte ptr [bp - 1], 1
D120  75 0D           jne 0xd12f
D122  C4 7E 06        les di, ptr [bp + 6]
D125  06              push es
D126  57              push di
D127  0E              push cs
D128  E8 21 03        call 0xd44c
D12B  08 C0           or al, al
D12D  75 04           jne 0xd133
loc_D12F:
D12F  B0 00           mov al, 0
D131  EB 02           jmp 0xd135
loc_D133:
D133  B0 01           mov al, 1
loc_D135:
D135  30 E4           xor ah, ah
D137  89 46 FB        mov word ptr [bp - 5], ax
D13A  C4 7E F7        les di, ptr [bp - 9]
D13D  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
D142  74 0C           je 0xd150
D144  C4 7E F7        les di, ptr [bp - 9]
D147  26 8A 45 03     mov al, byte ptr es:[di + 3]
D14B  3A 46 FF        cmp al, byte ptr [bp - 1]
D14E  75 20           jne 0xd170
loc_D150:
D150  C4 7E F3        les di, ptr [bp - 0xd]
D153  81 C7 B9 00     add di, 0xb9
D157  06              push es
D158  57              push di
D159  FF 76 FB        push word ptr [bp - 5]
D15C  55              push bp
D15D  E8 B6 FE        call 0xd016
D160  C4 7E F3        les di, ptr [bp - 0xd]
D163  81 C7 AD 00     add di, 0xad
D167  06              push es
D168  57              push di
D169  FF 76 FB        push word ptr [bp - 5]
D16C  55              push bp
D16D  E8 C2 FE        call 0xd032
loc_D170:
D170  C4 7E F7        les di, ptr [bp - 9]
D173  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
D178  74 0C           je 0xd186
D17A  C4 7E F7        les di, ptr [bp - 9]
D17D  26 8A 45 03     mov al, byte ptr es:[di + 3]
D181  3A 46 FF        cmp al, byte ptr [bp - 1]
D184  74 20           je 0xd1a6
loc_D186:
D186  C4 7E F3        les di, ptr [bp - 0xd]
D189  81 C7 B3 00     add di, 0xb3
D18D  06              push es
D18E  57              push di
D18F  FF 76 FB        push word ptr [bp - 5]
D192  55              push bp
D193  E8 80 FE        call 0xd016
D196  C4 7E F3        les di, ptr [bp - 0xd]
D199  81 C7 A7 00     add di, 0xa7
D19D  06              push es
D19E  57              push di
D19F  FF 76 FB        push word ptr [bp - 5]
D1A2  55              push bp
D1A3  E8 8C FE        call 0xd032
loc_D1A6:
D1A6  C4 7E F7        les di, ptr [bp - 9]
D1A9  26 8A 45 03     mov al, byte ptr es:[di + 3]
D1AD  3A 46 FF        cmp al, byte ptr [bp - 1]
D1B0  75 22           jne 0xd1d4
D1B2  C4 7E F3        les di, ptr [bp - 0xd]
D1B5  81 C7 A7 00     add di, 0xa7
D1B9  06              push es
D1BA  57              push di
D1BB  FF 76 FB        push word ptr [bp - 5]
D1BE  55              push bp
D1BF  E8 54 FE        call 0xd016
D1C2  C4 7E F3        les di, ptr [bp - 0xd]
D1C5  81 C7 B3 00     add di, 0xb3
D1C9  06              push es
D1CA  57              push di
D1CB  FF 76 FB        push word ptr [bp - 5]
D1CE  55              push bp
D1CF  E8 60 FE        call 0xd032
D1D2  EB 4C           jmp 0xd220
loc_D1D4:
D1D4  C4 7E F7        les di, ptr [bp - 9]
D1D7  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
D1DC  74 22           je 0xd200
D1DE  C4 7E F3        les di, ptr [bp - 0xd]
D1E1  81 C7 AD 00     add di, 0xad
D1E5  06              push es
D1E6  57              push di
D1E7  FF 76 FB        push word ptr [bp - 5]
D1EA  55              push bp
D1EB  E8 28 FE        call 0xd016
D1EE  C4 7E F3        les di, ptr [bp - 0xd]
D1F1  81 C7 B9 00     add di, 0xb9
D1F5  06              push es
D1F6  57              push di
D1F7  FF 76 FB        push word ptr [bp - 5]
D1FA  55              push bp
D1FB  E8 34 FE        call 0xd032
D1FE  EB 20           jmp 0xd220
loc_D200:
D200  C4 7E F3        les di, ptr [bp - 0xd]
D203  81 C7 AD 00     add di, 0xad
D207  06              push es
D208  57              push di
D209  FF 76 FB        push word ptr [bp - 5]
D20C  55              push bp
D20D  E8 22 FE        call 0xd032
D210  C4 7E F3        les di, ptr [bp - 0xd]
D213  81 C7 A7 00     add di, 0xa7
D217  06              push es
D218  57              push di
D219  FF 76 FB        push word ptr [bp - 5]
D21C  55              push bp
D21D  E8 12 FE        call 0xd032
loc_D220:
D220  80 7E FF 01     cmp byte ptr [bp - 1], 1
D224  74 03           je 0xd229
D226  E9 D0 FE        jmp 0xd0f9
loc_D229:
D229  C4 7E F7        les di, ptr [bp - 9]
D22C  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
D231  75 03           jne 0xd236
D233  E9 EB 00        jmp 0xd321
loc_D236:
D236  C6 46 FF 00     mov byte ptr [bp - 1], 0
D23A  EB 03           jmp 0xd23f
loc_D23C:
D23C  FE 46 FF        inc byte ptr [bp - 1]
loc_D23F:
D23F  8A 46 FF        mov al, byte ptr [bp - 1]
D242  98              cwde
D243  D1 E0           shl ax, 1
D245  C4 7E F7        les di, ptr [bp - 9]
D248  03 F8           add di, ax
D24A  26 8B 45 04     mov ax, word ptr es:[di + 4]
D24E  BA BF 00        mov dx, 0xbf
D251  F7 E2           mul dx
D253  C4 3E 17 A9     les di, ptr [0xa917]
D257  03 F8           add di, ax
D259  89 7E F3        mov word ptr [bp - 0xd], di
D25C  8C 46 F5        mov word ptr [bp - 0xb], es
D25F  C4 7E 06        les di, ptr [bp + 6]
D262  06              push es
D263  57              push di
D264  9A 03 5A 71 17  call far 1771:5A03
D269  08 C0           or al, al
D26B  74 24           je 0xd291
D26D  C4 7E 06        les di, ptr [bp + 6]
D270  06              push es
D271  57              push di
D272  E8 6F D4        call 0xa6e4
D275  8B D0           mov dx, ax
D277  8A 46 FF        mov al, byte ptr [bp - 1]
D27A  98              cwde
D27B  D1 E0           shl ax, 1
D27D  C4 7E F7        les di, ptr [bp - 9]
D280  03 F8           add di, ax
D282  26 8B 45 04     mov ax, word ptr es:[di + 4]
D286  3B C2           cmp ax, dx
D288  74 07           je 0xd291
D28A  C7 46 FD 02 00  mov word ptr [bp - 3], 2
D28F  EB 08           jmp 0xd299
loc_D291:
D291  8A 46 FF        mov al, byte ptr [bp - 1]
D294  30 E4           xor ah, ah
D296  89 46 FD        mov word ptr [bp - 3], ax
loc_D299:
D299  8B 46 FD        mov ax, word ptr [bp - 3]
D29C  B1 03           mov cl, 3
D29E  D3 E0           shl ax, cl
D2A0  8B D8           mov bx, ax
D2A2  C4 7E F7        les di, ptr [bp - 9]
D2A5  26 8A 45 03     mov al, byte ptr es:[di + 3]
D2A9  3A 46 FF        cmp al, byte ptr [bp - 1]
D2AC  74 04           je 0xd2b2
D2AE  B0 00           mov al, 0
D2B0  EB 02           jmp 0xd2b4
loc_D2B2:
D2B2  B0 01           mov al, 1
loc_D2B4:
D2B4  98              cwde
D2B5  BA 18 00        mov dx, 0x18
D2B8  F7 E2           mul dx
D2BA  C4 7E F3        les di, ptr [bp - 0xd]
D2BD  03 F8           add di, ax
D2BF  03 FB           add di, bx
D2C1  81 C7 77 00     add di, 0x77
D2C5  06              push es
D2C6  57              push di
D2C7  9A 60 5C 71 17  call far 1771:5C60
D2CC  50              push ax
D2CD  C4 7E 06        les di, ptr [bp + 6]
D2D0  06              push es
D2D1  57              push di
D2D2  9A 60 5C 71 17  call far 1771:5C60
D2D7  5A              pop dx
D2D8  3B C2           cmp ax, dx
D2DA  72 3C           jb 0xd318
D2DC  C4 7E 06        les di, ptr [bp + 6]
D2DF  06              push es
D2E0  57              push di
D2E1  8B 46 FD        mov ax, word ptr [bp - 3]
D2E4  B1 03           mov cl, 3
D2E6  D3 E0           shl ax, cl
D2E8  8B D8           mov bx, ax
D2EA  C4 7E F7        les di, ptr [bp - 9]
D2ED  26 8A 45 03     mov al, byte ptr es:[di + 3]
D2F1  3A 46 FF        cmp al, byte ptr [bp - 1]
D2F4  74 04           je 0xd2fa
D2F6  B0 00           mov al, 0
D2F8  EB 02           jmp 0xd2fc
loc_D2FA:
D2FA  B0 01           mov al, 1
loc_D2FC:
D2FC  98              cwde
D2FD  BA 18 00        mov dx, 0x18
D300  F7 E2           mul dx
D302  C4 7E F3        les di, ptr [bp - 0xd]
D305  03 F8           add di, ax
D307  03 FB           add di, bx
D309  81 C7 77 00     add di, 0x77
D30D  06              push es
D30E  57              push di
D30F  B8 08 00        mov ax, 8
D312  50              push ax
D313  9A 5D 02 E4 23  call far 23E4:025D
loc_D318:
D318  80 7E FF 01     cmp byte ptr [bp - 1], 1
D31C  74 03           je 0xd321
D31E  E9 1B FF        jmp 0xd23c
loc_D321:
D321  C6 46 FF 00     mov byte ptr [bp - 1], 0
D325  EB 03           jmp 0xd32a
loc_D327:
D327  FE 46 FF        inc byte ptr [bp - 1]
loc_D32A:
D32A  31 C0           xor ax, ax
D32C  89 46 FD        mov word ptr [bp - 3], ax
D32F  EB 03           jmp 0xd334
loc_D331:
D331  FF 46 FD        inc word ptr [bp - 3]
loc_D334:
D334  8A 46 FF        mov al, byte ptr [bp - 1]
D337  98              cwde
D338  D1 E0           shl ax, 1
D33A  C4 7E F7        les di, ptr [bp - 9]
D33D  03 F8           add di, ax
D33F  26 8B 45 04     mov ax, word ptr es:[di + 4]
D343  BA BF 00        mov dx, 0xbf
D346  F7 E2           mul dx
D348  C4 3E 17 A9     les di, ptr [0xa917]
D34C  03 F8           add di, ax
D34E  89 7E F3        mov word ptr [bp - 0xd], di
D351  8C 46 F5        mov word ptr [bp - 0xb], es
D354  8B 46 FD        mov ax, word ptr [bp - 3]
D357  C4 7E F3        les di, ptr [bp - 0xd]
D35A  03 F8           add di, ax
D35C  26 8A 95 A7 00  mov dl, byte ptr es:[di + 0xa7]
D361  8B 46 FD        mov ax, word ptr [bp - 3]
D364  C4 7E F3        les di, ptr [bp - 0xd]
D367  03 F8           add di, ax
D369  26 8A 85 AA 00  mov al, byte ptr es:[di + 0xaa]
D36E  3A C2           cmp al, dl
D370  76 1A           jbe 0xd38c
D372  8B 46 FD        mov ax, word ptr [bp - 3]
D375  C4 7E F3        les di, ptr [bp - 0xd]
D378  03 F8           add di, ax
D37A  26 8A 95 AA 00  mov dl, byte ptr es:[di + 0xaa]
D37F  8B 46 FD        mov ax, word ptr [bp - 3]
D382  C4 7E F3        les di, ptr [bp - 0xd]
D385  03 F8           add di, ax
D387  26 88 95 A7 00  mov byte ptr es:[di + 0xa7], dl
loc_D38C:
D38C  8B 46 FD        mov ax, word ptr [bp - 3]
D38F  C4 7E F3        les di, ptr [bp - 0xd]
D392  03 F8           add di, ax
D394  26 8A 95 AD 00  mov dl, byte ptr es:[di + 0xad]
D399  8B 46 FD        mov ax, word ptr [bp - 3]
D39C  C4 7E F3        les di, ptr [bp - 0xd]
D39F  03 F8           add di, ax
D3A1  26 8A 85 B0 00  mov al, byte ptr es:[di + 0xb0]
D3A6  3A C2           cmp al, dl
D3A8  76 1A           jbe 0xd3c4
D3AA  8B 46 FD        mov ax, word ptr [bp - 3]
D3AD  C4 7E F3        les di, ptr [bp - 0xd]
D3B0  03 F8           add di, ax
D3B2  26 8A 95 B0 00  mov dl, byte ptr es:[di + 0xb0]
D3B7  8B 46 FD        mov ax, word ptr [bp - 3]
D3BA  C4 7E F3        les di, ptr [bp - 0xd]
D3BD  03 F8           add di, ax
D3BF  26 88 95 AD 00  mov byte ptr es:[di + 0xad], dl
loc_D3C4:
D3C4  8B 46 FD        mov ax, word ptr [bp - 3]
D3C7  C4 7E F3        les di, ptr [bp - 0xd]
D3CA  03 F8           add di, ax
D3CC  26 8A 95 B3 00  mov dl, byte ptr es:[di + 0xb3]
D3D1  8B 46 FD        mov ax, word ptr [bp - 3]
D3D4  C4 7E F3        les di, ptr [bp - 0xd]
D3D7  03 F8           add di, ax
D3D9  26 8A 85 B6 00  mov al, byte ptr es:[di + 0xb6]
D3DE  3A C2           cmp al, dl
D3E0  76 1A           jbe 0xd3fc
D3E2  8B 46 FD        mov ax, word ptr [bp - 3]
D3E5  C4 7E F3        les di, ptr [bp - 0xd]
D3E8  03 F8           add di, ax
D3EA  26 8A 95 B6 00  mov dl, byte ptr es:[di + 0xb6]
D3EF  8B 46 FD        mov ax, word ptr [bp - 3]
D3F2  C4 7E F3        les di, ptr [bp - 0xd]
D3F5  03 F8           add di, ax
D3F7  26 88 95 B3 00  mov byte ptr es:[di + 0xb3], dl
loc_D3FC:
D3FC  8B 46 FD        mov ax, word ptr [bp - 3]
D3FF  C4 7E F3        les di, ptr [bp - 0xd]
D402  03 F8           add di, ax
D404  26 8A 95 B9 00  mov dl, byte ptr es:[di + 0xb9]
D409  8B 46 FD        mov ax, word ptr [bp - 3]
D40C  C4 7E F3        les di, ptr [bp - 0xd]
D40F  03 F8           add di, ax
D411  26 8A 85 BC 00  mov al, byte ptr es:[di + 0xbc]
D416  3A C2           cmp al, dl
D418  76 1A           jbe 0xd434
D41A  8B 46 FD        mov ax, word ptr [bp - 3]
D41D  C4 7E F3        les di, ptr [bp - 0xd]
D420  03 F8           add di, ax
D422  26 8A 95 BC 00  mov dl, byte ptr es:[di + 0xbc]
D427  8B 46 FD        mov ax, word ptr [bp - 3]
D42A  C4 7E F3        les di, ptr [bp - 0xd]
D42D  03 F8           add di, ax
D42F  26 88 95 B9 00  mov byte ptr es:[di + 0xb9], dl
loc_D434:
D434  83 7E FD 02     cmp word ptr [bp - 3], 2
D438  74 03           je 0xd43d
D43A  E9 F4 FE        jmp 0xd331
loc_D43D:
D43D  80 7E FF 01     cmp byte ptr [bp - 1], 1
D441  74 03           je 0xd446
D443  E9 E1 FE        jmp 0xd327
loc_D446:
D446  89 EC           mov sp, bp
D448  5D              pop bp
D449  CA 04 00        retf 4

; ---- routine 0791:D44C  (found by: call)
sub_D44C:
D44C  55              push bp
D44D  89 E5           mov bp, sp
D44F  83 EC 06        sub sp, 6
D452  C4 7E 06        les di, ptr [bp + 6]
D455  89 7E FB        mov word ptr [bp - 5], di
D458  8C 46 FD        mov word ptr [bp - 3], es
D45B  C4 7E 06        les di, ptr [bp + 6]
D45E  06              push es
D45F  57              push di
D460  E8 81 D2        call 0xa6e4
D463  C4 7E FB        les di, ptr [bp - 5]
D466  26 3B 45 06     cmp ax, word ptr es:[di + 6]
D46A  74 04           je 0xd470
D46C  B0 00           mov al, 0
D46E  EB 02           jmp 0xd472
loc_D470:
D470  B0 01           mov al, 1
loc_D472:
D472  88 46 FF        mov byte ptr [bp - 1], al
D475  8A 46 FF        mov al, byte ptr [bp - 1]
D478  89 EC           mov sp, bp
D47A  5D              pop bp
D47B  CA 04 00        retf 4

; ---- routine 0791:D47E  (found by: far)
sub_D47E:
D47E  55              push bp
D47F  89 E5           mov bp, sp
D481  83 EC 10        sub sp, 0x10
D484  C4 7E 06        les di, ptr [bp + 6]
D487  89 7E F9        mov word ptr [bp - 7], di
D48A  8C 46 FB        mov word ptr [bp - 5], es
D48D  C4 7E 06        les di, ptr [bp + 6]
D490  06              push es
D491  57              push di
D492  E8 49 CF        call 0xa3de
D495  C4 7E F9        les di, ptr [bp - 7]
D498  26 FF 75 06     push word ptr es:[di + 6]
D49C  B0 01           mov al, 1
D49E  50              push ax
D49F  A0 FC 80        mov al, byte ptr [0x80fc]
D4A2  50              push ax
D4A3  9A C4 0B 71 17  call far 1771:0BC4
D4A8  C4 7E F9        les di, ptr [bp - 7]
D4AB  26 FF 75 04     push word ptr es:[di + 4]
D4AF  B0 00           mov al, 0
D4B1  50              push ax
D4B2  B0 00           mov al, 0
D4B4  50              push ax
D4B5  9A C4 0B 71 17  call far 1771:0BC4
D4BA  B8 0C 00        mov ax, 0xc
D4BD  50              push ax
D4BE  E8 DC DC        call 0xb19d
D4C1  A1 3C 9B        mov ax, word ptr [0x9b3c]
D4C4  C4 7E F9        les di, ptr [bp - 7]
D4C7  26 89 05        mov word ptr es:[di], ax
D4CA  C4 7E F9        les di, ptr [bp - 7]
D4CD  26 8A 05        mov al, byte ptr es:[di]
D4D0  C4 7E F9        les di, ptr [bp - 7]
D4D3  26 3A 45 01     cmp al, byte ptr es:[di + 1]
D4D7  75 0A           jne 0xd4e3
D4D9  C4 7E F9        les di, ptr [bp - 7]
D4DC  26 C6 45 03 02  mov byte ptr es:[di + 3], 2
D4E1  EB 1C           jmp 0xd4ff
loc_D4E3:
D4E3  C4 7E F9        les di, ptr [bp - 7]
D4E6  26 8A 45 01     mov al, byte ptr es:[di + 1]
D4EA  C4 7E F9        les di, ptr [bp - 7]
D4ED  26 3A 05        cmp al, byte ptr es:[di]
D4F0  77 04           ja 0xd4f6
D4F2  B0 00           mov al, 0
D4F4  EB 02           jmp 0xd4f8
loc_D4F6:
D4F6  B0 01           mov al, 1
loc_D4F8:
D4F8  C4 7E F9        les di, ptr [bp - 7]
D4FB  26 88 45 03     mov byte ptr es:[di + 3], al
loc_D4FF:
D4FF  C4 7E 06        les di, ptr [bp + 6]
D502  06              push es
D503  57              push di
D504  E8 58 DC        call 0xb15f
D507  08 C0           or al, al
D509  74 49           je 0xd554
D50B  B8 04 00        mov ax, 4
D50E  50              push ax
D50F  E8 8B DC        call 0xb19d
D512  A1 3C 9B        mov ax, word ptr [0x9b3c]
D515  C4 7E F9        les di, ptr [bp - 7]
D518  26 89 05        mov word ptr es:[di], ax
D51B  C4 7E F9        les di, ptr [bp - 7]
D51E  26 8A 05        mov al, byte ptr es:[di]
D521  C4 7E F9        les di, ptr [bp - 7]
D524  26 3A 45 01     cmp al, byte ptr es:[di + 1]
D528  75 0E           jne 0xd538
D52A  9A FA 06 4B 21  call far 214B:06FA
D52F  C4 7E F9        les di, ptr [bp - 7]
D532  26 88 45 03     mov byte ptr es:[di + 3], al
D536  EB 1C           jmp 0xd554
loc_D538:
D538  C4 7E F9        les di, ptr [bp - 7]
D53B  26 8A 45 01     mov al, byte ptr es:[di + 1]
D53F  C4 7E F9        les di, ptr [bp - 7]
D542  26 3A 05        cmp al, byte ptr es:[di]
D545  77 04           ja 0xd54b
D547  B0 00           mov al, 0
D549  EB 02           jmp 0xd54d
loc_D54B:
D54B  B0 01           mov al, 1
loc_D54D:
D54D  C4 7E F9        les di, ptr [bp - 7]
D550  26 88 45 03     mov byte ptr es:[di + 3], al
loc_D554:
D554  C6 46 FF 00     mov byte ptr [bp - 1], 0
D558  EB 03           jmp 0xd55d
loc_D55A:
D55A  FE 46 FF        inc byte ptr [bp - 1]
loc_D55D:
D55D  8A 46 FF        mov al, byte ptr [bp - 1]
D560  98              cwde
D561  D1 E0           shl ax, 1
D563  C4 7E F9        les di, ptr [bp - 7]
D566  03 F8           add di, ax
D568  26 8B 45 04     mov ax, word ptr es:[di + 4]
D56C  BA BF 00        mov dx, 0xbf
D56F  F7 E2           mul dx
D571  C4 3E 17 A9     les di, ptr [0xa917]
D575  03 F8           add di, ax
D577  89 7E F5        mov word ptr [bp - 0xb], di
D57A  8C 46 F7        mov word ptr [bp - 9], es
D57D  C7 46 FD 01 00  mov word ptr [bp - 3], 1
D582  EB 03           jmp 0xd587
loc_D584:
D584  FF 46 FD        inc word ptr [bp - 3]
loc_D587:
D587  8B 46 FD        mov ax, word ptr [bp - 3]
D58A  D1 E0           shl ax, 1
D58C  C4 7E F5        les di, ptr [bp - 0xb]
D58F  03 F8           add di, ax
D591  26 8B 45 FE     mov ax, word ptr es:[di - 2]
D595  BA 14 00        mov dx, 0x14
D598  F7 E2           mul dx
D59A  C4 3E 1B A9     les di, ptr [0xa91b]
D59E  03 F8           add di, ax
D5A0  89 7E F1        mov word ptr [bp - 0xf], di
D5A3  8C 46 F3        mov word ptr [bp - 0xd], es
D5A6  C4 7E F1        les di, ptr [bp - 0xf]
D5A9  26 C7 45 12 FF 7F mov word ptr es:[di + 0x12], 0x7fff
D5AF  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
D5B3  75 CF           jne 0xd584
D5B5  80 7E FF 01     cmp byte ptr [bp - 1], 1
D5B9  75 9F           jne 0xd55a
D5BB  89 EC           mov sp, bp
D5BD  5D              pop bp
D5BE  CA 04 00        retf 4

; ---- routine 0791:D5C1  (found by: call)
sub_D5C1:
D5C1  55              push bp
D5C2  89 E5           mov bp, sp
D5C4  83 EC 0A        sub sp, 0xa
D5C7  B8 0A 00        mov ax, 0xa
D5CA  50              push ax
D5CB  9A B1 06 4B 21  call far 214B:06B1
D5D0  40              inc ax
D5D1  89 46 FD        mov word ptr [bp - 3], ax
D5D4  8B 7E FD        mov di, word ptr [bp - 3]
D5D7  8A 85 90 0A     mov al, byte ptr [di + 0xa90]
D5DB  30 E4           xor ah, ah
D5DD  89 46 FB        mov word ptr [bp - 5], ax
D5E0  C6 46 FF 00     mov byte ptr [bp - 1], 0
D5E4  EB 03           jmp 0xd5e9
loc_D5E6:
D5E6  FE 46 FF        inc byte ptr [bp - 1]
loc_D5E9:
D5E9  8A 46 FF        mov al, byte ptr [bp - 1]
D5EC  98              cwde
D5ED  8B F8           mov di, ax
D5EF  8A 85 68 06     mov al, byte ptr [di + 0x668]
D5F3  30 E4           xor ah, ah
D5F5  8B D0           mov dx, ax
D5F7  8A 46 FF        mov al, byte ptr [bp - 1]
D5FA  98              cwde
D5FB  8B F8           mov di, ax
D5FD  D1 E7           shl di, 1
D5FF  01 53 FB        add word ptr [bp + di - 5], dx
D602  80 7E FF 01     cmp byte ptr [bp - 1], 1
D606  75 DE           jne 0xd5e6
D608  8B 46 FD        mov ax, word ptr [bp - 3]
D60B  BA 16 00        mov dx, 0x16
D60E  F7 E2           mul dx
D610  8B F8           mov di, ax
D612  81 C7 E8 80     add di, 0x80e8
D616  1E              push ds
D617  57              push di
D618  0E              push cs
D619  E8 3A 53        call 0x12956
D61C  08 C0           or al, al
D61E  74 03           je 0xd623
D620  E9 0A 01        jmp 0xd72d
loc_D623:
D623  8B 46 FB        mov ax, word ptr [bp - 5]
D626  BA 16 00        mov dx, 0x16
D629  F7 E2           mul dx
D62B  8B F8           mov di, ax
D62D  81 C7 E8 80     add di, 0x80e8
D631  1E              push ds
D632  57              push di
D633  0E              push cs
D634  E8 1F 53        call 0x12956
D637  08 C0           or al, al
D639  74 03           je 0xd63e
D63B  E9 EF 00        jmp 0xd72d
loc_D63E:
D63E  9A FA 06 4B 21  call far 214B:06FA
D643  88 46 FF        mov byte ptr [bp - 1], al
D646  8A 46 FF        mov al, byte ptr [bp - 1]
D649  98              cwde
D64A  8B F8           mov di, ax
D64C  D1 E7           shl di, 1
D64E  8B 43 FB        mov ax, word ptr [bp + di - 5]
D651  BA 16 00        mov dx, 0x16
D654  F7 E2           mul dx
D656  8B F8           mov di, ax
D658  81 C7 E8 80     add di, 0x80e8
D65C  89 7E F7        mov word ptr [bp - 9], di
D65F  8C 5E F9        mov word ptr [bp - 7], ds
D662  B8 0A 00        mov ax, 0xa
D665  50              push ax
D666  80 7E FF 00     cmp byte ptr [bp - 1], 0
D66A  74 04           je 0xd670
D66C  B0 00           mov al, 0
D66E  EB 02           jmp 0xd672
loc_D670:
D670  B0 01           mov al, 1
loc_D672:
D672  98              cwde
D673  8B F8           mov di, ax
D675  D1 E7           shl di, 1
D677  8B 43 FB        mov ax, word ptr [bp + di - 5]
D67A  BA 16 00        mov dx, 0x16
D67D  F7 E2           mul dx
D67F  8B F8           mov di, ax
D681  81 C7 E8 80     add di, 0x80e8
D685  1E              push ds
D686  57              push di
D687  0E              push cs
D688  E8 FF 50        call 0x1278a
D68B  50              push ax
D68C  B8 03 00        mov ax, 3
D68F  50              push ax
D690  C4 7E F7        les di, ptr [bp - 9]
D693  06              push es
D694  57              push di
D695  0E              push cs
D696  E8 F1 50        call 0x1278a
D699  5A              pop dx
D69A  3B C2           cmp ax, dx
D69C  72 03           jb 0xd6a1
D69E  E9 8C 00        jmp 0xd72d
loc_D6A1:
D6A1  B8 04 00        mov ax, 4
D6A4  50              push ax
D6A5  C4 7E F7        les di, ptr [bp - 9]
D6A8  06              push es
D6A9  57              push di
D6AA  0E              push cs
D6AB  E8 29 50        call 0x126d7
D6AE  08 C0           or al, al
D6B0  75 0D           jne 0xd6bf
D6B2  B8 14 00        mov ax, 0x14
D6B5  50              push ax
D6B6  9A D0 06 4B 21  call far 214B:06D0
D6BB  08 C0           or al, al
D6BD  74 6E           je 0xd72d
loc_D6BF:
D6BF  80 7E FF 00     cmp byte ptr [bp - 1], 0
D6C3  74 04           je 0xd6c9
D6C5  B0 00           mov al, 0
D6C7  EB 02           jmp 0xd6cb
loc_D6C9:
D6C9  B0 01           mov al, 1
loc_D6CB:
D6CB  98              cwde
D6CC  8B F8           mov di, ax
D6CE  D1 E7           shl di, 1
D6D0  8B 43 FB        mov ax, word ptr [bp + di - 5]
D6D3  BA 16 00        mov dx, 0x16
D6D6  F7 E2           mul dx
D6D8  8B F8           mov di, ax
D6DA  FF B5 F5 80     push word ptr [di - 0x7f0b]
D6DE  9A FB 2F 71 17  call far 1771:2FFB
D6E3  30 E4           xor ah, ah
D6E5  50              push ax
D6E6  9A B1 06 4B 21  call far 214B:06B1
D6EB  50              push ax
D6EC  C4 7E F7        les di, ptr [bp - 9]
D6EF  26 FF 75 0D     push word ptr es:[di + 0xd]
D6F3  9A FB 2F 71 17  call far 1771:2FFB
D6F8  30 E4           xor ah, ah
D6FA  50              push ax
D6FB  9A B1 06 4B 21  call far 214B:06B1
D700  5A              pop dx
D701  3B C2           cmp ax, dx
D703  7E 28           jle 0xd72d
D705  8A 46 FF        mov al, byte ptr [bp - 1]
D708  98              cwde
D709  8B F8           mov di, ax
D70B  D1 E7           shl di, 1
D70D  8A 43 FB        mov al, byte ptr [bp + di - 5]
D710  A2 0C 83        mov byte ptr [0x830c], al
D713  80 7E FF 00     cmp byte ptr [bp - 1], 0
D717  74 04           je 0xd71d
D719  B0 00           mov al, 0
D71B  EB 02           jmp 0xd71f
loc_D71D:
D71D  B0 01           mov al, 1
loc_D71F:
D71F  98              cwde
D720  8B F8           mov di, ax
D722  D1 E7           shl di, 1
D724  8A 43 FB        mov al, byte ptr [bp + di - 5]
D727  A2 0B 83        mov byte ptr [0x830b], al
D72A  E8 C2 A7        call 0x7eef
loc_D72D:
D72D  89 EC           mov sp, bp
D72F  5D              pop bp
D730  C2 02 00        ret 2

; ---- routine 0791:D733  (found by: call)
sub_D733:
D733  55              push bp
D734  89 E5           mov bp, sp
D736  83 EC 36        sub sp, 0x36
D739  C6 06 25 83 01  mov byte ptr [0x8325], 1
D73E  C4 3E 6A A9     les di, ptr [0xa96a]
D742  06              push es
D743  57              push di
D744  C4 3E 72 A9     les di, ptr [0xa972]
D748  06              push es
D749  57              push di
D74A  B8 A0 0F        mov ax, 0xfa0
D74D  50              push ax
D74E  9A 5D 02 E4 23  call far 23E4:025D
D753  C6 46 D2 00     mov byte ptr [bp - 0x2e], 0
D757  31 C0           xor ax, ax
D759  A3 1D 83        mov word ptr [0x831d], ax
D75C  A1 3C 9B        mov ax, word ptr [0x9b3c]
D75F  89 46 FC        mov word ptr [bp - 4], ax
D762  8D 7E DC        lea di, [bp - 0x24]
D765  16              push ss
D766  57              push di
D767  B8 20 00        mov ax, 0x20
D76A  50              push ax
D76B  31 C0           xor ax, ax
D76D  50              push ax
D76E  9A 18 00 4B 21  call far 214B:0018
D773  8B 46 FC        mov ax, word ptr [bp - 4]
D776  89 46 FE        mov word ptr [bp - 2], ax
D779  31 C0           xor ax, ax
D77B  A3 3C 9B        mov word ptr [0x9b3c], ax
D77E  FF 36 36 9B     push word ptr [0x9b36]
D782  B0 01           mov al, 1
D784  50              push ax
D785  A0 FC 80        mov al, byte ptr [0x80fc]
D788  50              push ax
D789  9A C4 0B 71 17  call far 1771:0BC4
D78E  FF 36 34 9B     push word ptr [0x9b34]
D792  B0 00           mov al, 0
D794  50              push ax
D795  B0 00           mov al, 0
D797  50              push ax
D798  9A C4 0B 71 17  call far 1771:0BC4
D79D  80 3E 19 83 0F  cmp byte ptr [0x8319], 0xf
D7A2  74 04           je 0xd7a8
D7A4  B0 00           mov al, 0
D7A6  EB 02           jmp 0xd7aa
loc_D7A8:
D7A8  B0 01           mov al, 1
loc_D7AA:
D7AA  98              cwde
D7AB  8B F8           mov di, ax
D7AD  8A 85 8A 0A     mov al, byte ptr [di + 0xa8a]
D7B1  30 E4           xor ah, ah
D7B3  50              push ax
D7B4  E8 E6 D9        call 0xb19d
D7B7  C6 46 D3 00     mov byte ptr [bp - 0x2d], 0
D7BB  EB 03           jmp 0xd7c0
loc_D7BD:
D7BD  FE 46 D3        inc byte ptr [bp - 0x2d]
loc_D7C0:
D7C0  B8 05 00        mov ax, 5
D7C3  50              push ax
D7C4  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D7C7  98              cwde
D7C8  8B F8           mov di, ax
D7CA  D1 E7           shl di, 1
D7CC  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
D7D0  BA BF 00        mov dx, 0xbf
D7D3  F7 E2           mul dx
D7D5  C4 3E 17 A9     les di, ptr [0xa917]
D7D9  03 F8           add di, ax
D7DB  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
D7DF  30 E4           xor ah, ah
D7E1  50              push ax
D7E2  9A 57 0C 4B 21  call far 214B:0C57
D7E7  98              cwde
D7E8  8B F8           mov di, ax
D7EA  8A 85 90 0A     mov al, byte ptr [di + 0xa90]
D7EE  30 E4           xor ah, ah
D7F0  50              push ax
D7F1  9A D0 06 4B 21  call far 214B:06D0
D7F6  08 C0           or al, al
D7F8  74 0F           je 0xd809
D7FA  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D7FD  98              cwde
D7FE  BA 0A 00        mov dx, 0xa
D801  F7 E2           mul dx
D803  8B F8           mov di, ax
D805  FE 85 7E 7B     inc byte ptr [di + 0x7b7e]
loc_D809:
D809  B8 01 00        mov ax, 1
D80C  50              push ax
D80D  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D810  98              cwde
D811  8B F8           mov di, ax
D813  D1 E7           shl di, 1
D815  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
D819  BA BF 00        mov dx, 0xbf
D81C  F7 E2           mul dx
D81E  C4 3E 17 A9     les di, ptr [0xa917]
D822  03 F8           add di, ax
D824  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
D828  30 E4           xor ah, ah
D82A  50              push ax
D82B  9A 57 0C 4B 21  call far 214B:0C57
D830  98              cwde
D831  8B F8           mov di, ax
D833  8A 85 8E 0A     mov al, byte ptr [di + 0xa8e]
D837  30 E4           xor ah, ah
D839  50              push ax
D83A  9A D0 06 4B 21  call far 214B:06D0
D83F  08 C0           or al, al
D841  74 27           je 0xd86a
D843  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D846  98              cwde
D847  BA 0A 00        mov dx, 0xa
D84A  F7 E2           mul dx
D84C  8B F8           mov di, ax
D84E  FE 85 82 7B     inc byte ptr [di + 0x7b82]
D852  80 7E D3 00     cmp byte ptr [bp - 0x2d], 0
D856  74 04           je 0xd85c
D858  B0 00           mov al, 0
D85A  EB 02           jmp 0xd85e
loc_D85C:
D85C  B0 01           mov al, 1
loc_D85E:
D85E  98              cwde
D85F  BA 0A 00        mov dx, 0xa
D862  F7 E2           mul dx
D864  8B F8           mov di, ax
D866  FE 85 83 7B     inc byte ptr [di + 0x7b83]
loc_D86A:
D86A  80 7E D3 01     cmp byte ptr [bp - 0x2d], 1
D86E  74 03           je 0xd873
D870  E9 4A FF        jmp 0xd7bd
loc_D873:
D873  C6 46 D3 00     mov byte ptr [bp - 0x2d], 0
D877  EB 03           jmp 0xd87c
loc_D879:
D879  FE 46 D3        inc byte ptr [bp - 0x2d]
loc_D87C:
D87C  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D87F  98              cwde
D880  8B F8           mov di, ax
D882  8A 53 FE        mov dl, byte ptr [bp + di - 2]
D885  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D888  98              cwde
D889  8B F8           mov di, ax
D88B  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
D88F  3A C2           cmp al, dl
D891  77 03           ja 0xd896
D893  E9 B6 01        jmp 0xda4c
loc_D896:
D896  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D899  98              cwde
D89A  8B F8           mov di, ax
D89C  8A 53 FE        mov dl, byte ptr [bp + di - 2]
D89F  8A 46 D3        mov al, byte ptr [bp - 0x2d]
D8A2  98              cwde
D8A3  8B F8           mov di, ax
D8A5  28 95 3C 9B     sub byte ptr [di - 0x64c4], dl
D8A9  C6 46 D4 00     mov byte ptr [bp - 0x2c], 0
D8AD  EB 03           jmp 0xd8b2
loc_D8AF:
D8AF  FE 46 D4        inc byte ptr [bp - 0x2c]
loc_D8B2:
D8B2  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D8B5  98              cwde
D8B6  8B F8           mov di, ax
D8B8  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
D8BC  30 E4           xor ah, ah
D8BE  89 46 D0        mov word ptr [bp - 0x30], ax
D8C1  B8 01 00        mov ax, 1
D8C4  3B 46 D0        cmp ax, word ptr [bp - 0x30]
D8C7  77 42           ja 0xd90b
D8C9  89 46 DA        mov word ptr [bp - 0x26], ax
D8CC  EB 03           jmp 0xd8d1
loc_D8CE:
D8CE  FF 46 DA        inc word ptr [bp - 0x26]
loc_D8D1:
D8D1  80 3E 19 83 0F  cmp byte ptr [0x8319], 0xf
D8D6  74 04           je 0xd8dc
D8D8  B0 00           mov al, 0
D8DA  EB 02           jmp 0xd8de
loc_D8DC:
D8DC  B0 01           mov al, 1
loc_D8DE:
D8DE  98              cwde
D8DF  8B F8           mov di, ax
D8E1  8A 85 8C 0A     mov al, byte ptr [di + 0xa8c]
D8E5  30 E4           xor ah, ah
D8E7  50              push ax
D8E8  9A B1 06 4B 21  call far 214B:06B1
D8ED  8A D8           mov bl, al
D8EF  8B 46 DA        mov ax, word ptr [bp - 0x26]
D8F2  8B D0           mov dx, ax
D8F4  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D8F7  98              cwde
D8F8  8B F8           mov di, ax
D8FA  B1 04           mov cl, 4
D8FC  D3 E7           shl di, cl
D8FE  03 FA           add di, dx
D900  88 5B DB        mov byte ptr [bp + di - 0x25], bl
D903  8B 46 DA        mov ax, word ptr [bp - 0x26]
D906  3B 46 D0        cmp ax, word ptr [bp - 0x30]
D909  75 C3           jne 0xd8ce
loc_D90B:
D90B  80 7E D4 01     cmp byte ptr [bp - 0x2c], 1
D90F  75 9E           jne 0xd8af
D911  C6 46 D4 00     mov byte ptr [bp - 0x2c], 0
D915  EB 03           jmp 0xd91a
loc_D917:
D917  FE 46 D4        inc byte ptr [bp - 0x2c]
loc_D91A:
D91A  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D91D  98              cwde
D91E  8B F8           mov di, ax
D920  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
D924  30 E4           xor ah, ah
D926  89 46 D0        mov word ptr [bp - 0x30], ax
D929  B8 01 00        mov ax, 1
D92C  3B 46 D0        cmp ax, word ptr [bp - 0x30]
D92F  76 03           jbe 0xd934
D931  E9 0F 01        jmp 0xda43
loc_D934:
D934  89 46 DA        mov word ptr [bp - 0x26], ax
D937  EB 03           jmp 0xd93c
loc_D939:
D939  FF 46 DA        inc word ptr [bp - 0x26]
loc_D93C:
D93C  80 7E D2 00     cmp byte ptr [bp - 0x2e], 0
D940  74 03           je 0xd945
D942  E9 F3 00        jmp 0xda38
loc_D945:
D945  8B 46 DA        mov ax, word ptr [bp - 0x26]
D948  8B D0           mov dx, ax
D94A  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D94D  98              cwde
D94E  8B F8           mov di, ax
D950  B1 04           mov cl, 4
D952  D3 E7           shl di, cl
D954  03 FA           add di, dx
D956  8A 43 DB        mov al, byte ptr [bp + di - 0x25]
D959  30 E4           xor ah, ah
D95B  3B 06 1F 83     cmp ax, word ptr [0x831f]
D95F  74 03           je 0xd964
D961  E9 D4 00        jmp 0xda38
loc_D964:
D964  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D967  98              cwde
D968  8B F8           mov di, ax
D96A  80 7B FE 0F     cmp byte ptr [bp + di - 2], 0xf
D96E  72 03           jb 0xd973
D970  E9 C5 00        jmp 0xda38
loc_D973:
D973  B8 1E 00        mov ax, 0x1e
D976  50              push ax
D977  9A B1 06 4B 21  call far 214B:06B1
D97C  8B F8           mov di, ax
D97E  8A 85 6B 0A     mov al, byte ptr [di + 0xa6b]
D982  30 E4           xor ah, ah
D984  89 46 D6        mov word ptr [bp - 0x2a], ax
D987  8B 46 D6        mov ax, word ptr [bp - 0x2a]
D98A  D1 E0           shl ax, 1
D98C  8B C8           mov cx, ax
D98E  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D991  98              cwde
D992  8B F8           mov di, ax
D994  D1 E7           shl di, 1
D996  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
D99A  BA BF 00        mov dx, 0xbf
D99D  F7 E2           mul dx
D99F  C4 3E 17 A9     les di, ptr [0xa917]
D9A3  03 F8           add di, ax
D9A5  03 F9           add di, cx
D9A7  26 FF 75 FE     push word ptr es:[di - 2]
D9AB  9A 16 32 71 17  call far 1771:3216
D9B0  08 C0           or al, al
D9B2  75 BF           jne 0xd973
D9B4  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D9B7  98              cwde
D9B8  8B F8           mov di, ax
D9BA  FE 43 FE        inc byte ptr [bp + di - 2]
D9BD  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D9C0  98              cwde
D9C1  8B F8           mov di, ax
D9C3  D1 E7           shl di, 1
D9C5  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
D9C9  BA BF 00        mov dx, 0xbf
D9CC  F7 E2           mul dx
D9CE  C4 3E 17 A9     les di, ptr [0xa917]
D9D2  03 F8           add di, ax
D9D4  89 7E CC        mov word ptr [bp - 0x34], di
D9D7  8C 46 CE        mov word ptr [bp - 0x32], es
D9DA  8B 46 D6        mov ax, word ptr [bp - 0x2a]
D9DD  D1 E0           shl ax, 1
D9DF  C4 7E CC        les di, ptr [bp - 0x34]
D9E2  03 F8           add di, ax
D9E4  26 FF 75 FE     push word ptr es:[di - 2]
D9E8  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D9EB  98              cwde
D9EC  8B F8           mov di, ax
D9EE  D1 E7           shl di, 1
D9F0  FF B5 34 9B     push word ptr [di - 0x64cc]
D9F4  9A 82 3A 71 17  call far 1771:3A82
D9F9  8B D0           mov dx, ax
D9FB  8A 46 D4        mov al, byte ptr [bp - 0x2c]
D9FE  98              cwde
D9FF  8B F8           mov di, ax
DA01  8A 85 68 06     mov al, byte ptr [di + 0x668]
DA05  30 E4           xor ah, ah
DA07  03 C2           add ax, dx
DA09  A2 0B 83        mov byte ptr [0x830b], al
DA0C  8A 46 D4        mov al, byte ptr [bp - 0x2c]
DA0F  50              push ax
DA10  A0 0B 83        mov al, byte ptr [0x830b]
DA13  30 E4           xor ah, ah
DA15  50              push ax
DA16  8B 46 DA        mov ax, word ptr [bp - 0x26]
DA19  8B D0           mov dx, ax
DA1B  8A 46 D4        mov al, byte ptr [bp - 0x2c]
DA1E  98              cwde
DA1F  8B F8           mov di, ax
DA21  B1 04           mov cl, 4
DA23  D3 E7           shl di, cl
DA25  03 FA           add di, dx
DA27  8A 43 DB        mov al, byte ptr [bp + di - 0x25]
DA2A  30 E4           xor ah, ah
DA2C  50              push ax
DA2D  E8 13 8A        call 0x6443
DA30  C6 46 D2 01     mov byte ptr [bp - 0x2e], 1
DA34  C6 46 D3 01     mov byte ptr [bp - 0x2d], 1
loc_DA38:
DA38  8B 46 DA        mov ax, word ptr [bp - 0x26]
DA3B  3B 46 D0        cmp ax, word ptr [bp - 0x30]
DA3E  74 03           je 0xda43
DA40  E9 F6 FE        jmp 0xd939
loc_DA43:
DA43  80 7E D4 01     cmp byte ptr [bp - 0x2c], 1
DA47  74 03           je 0xda4c
DA49  E9 CB FE        jmp 0xd917
loc_DA4C:
DA4C  80 7E D3 01     cmp byte ptr [bp - 0x2d], 1
DA50  74 03           je 0xda55
DA52  E9 24 FE        jmp 0xd879
loc_DA55:
DA55  8B 46 FE        mov ax, word ptr [bp - 2]
DA58  A3 3C 9B        mov word ptr [0x9b3c], ax
DA5B  FF 36 1B 83     push word ptr [0x831b]
DA5F  B8 03 00        mov ax, 3
DA62  50              push ax
DA63  E8 E6 2A        call 0x1054c
DA66  BF 6A A9        mov di, 0xa96a
DA69  1E              push ds
DA6A  57              push di
DA6B  0E              push cs
DA6C  E8 A3 2C        call 0x10712
DA6F  C7 46 DA 01 00  mov word ptr [bp - 0x26], 1
DA74  EB 03           jmp 0xda79
loc_DA76:
DA76  FF 46 DA        inc word ptr [bp - 0x26]
loc_DA79:
DA79  8B 46 DA        mov ax, word ptr [bp - 0x26]
DA7C  BA 16 00        mov dx, 0x16
DA7F  F7 E2           mul dx
DA81  8B F8           mov di, ax
DA83  81 C7 E8 80     add di, 0x80e8
DA87  89 7E CE        mov word ptr [bp - 0x32], di
DA8A  8C 5E D0        mov word ptr [bp - 0x30], ds
DA8D  A1 1B 83        mov ax, word ptr [0x831b]
DA90  31 D2           xor dx, dx
DA92  B9 05 00        mov cx, 5
DA95  F7 F1           div cx
DA97  92              xchg dx, ax
DA98  09 C0           or ax, ax
DA9A  75 29           jne 0xdac5
DA9C  C4 7E CE        les di, ptr [bp - 0x32]
DA9F  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
DAA3  BA 14 00        mov dx, 0x14
DAA6  F7 E2           mul dx
DAA8  C4 3E 1B A9     les di, ptr [0xa91b]
DAAC  03 F8           add di, ax
DAAE  89 7E CA        mov word ptr [bp - 0x36], di
DAB1  8C 46 CC        mov word ptr [bp - 0x34], es
DAB4  C4 7E CA        les di, ptr [bp - 0x36]
DAB7  26 80 7D 0E 01  cmp byte ptr es:[di + 0xe], 1
DABC  7E 07           jle 0xdac5
DABE  C4 7E CA        les di, ptr [bp - 0x36]
DAC1  26 FE 4D 0E     dec byte ptr es:[di + 0xe]
loc_DAC5:
DAC5  83 7E DA 16     cmp word ptr [bp - 0x26], 0x16
DAC9  75 AB           jne 0xda76
DACB  80 3E 3D 9A 00  cmp byte ptr [0x9a3d], 0
DAD0  74 0A           je 0xdadc
DAD2  80 7E D2 00     cmp byte ptr [bp - 0x2e], 0
DAD6  75 04           jne 0xdadc
DAD8  55              push bp
DAD9  E8 E5 FA        call 0xd5c1
loc_DADC:
DADC  80 7E D2 00     cmp byte ptr [bp - 0x2e], 0
DAE0  75 05           jne 0xdae7
DAE2  E8 7D A5        call 0x8062
DAE5  EB 0A           jmp 0xdaf1
loc_DAE7:
DAE7  B0 00           mov al, 0
DAE9  50              push ax
DAEA  0E              push cs
DAEB  E8 18 26        call 0x10106
DAEE  E8 0D 8B        call 0x65fe
loc_DAF1:
DAF1  E8 7E B8        call 0x9372
DAF4  89 EC           mov sp, bp
DAF6  5D              pop bp
DAF7  C3              ret

