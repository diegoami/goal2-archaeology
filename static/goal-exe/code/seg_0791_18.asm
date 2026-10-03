; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 18 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:AD8F  (found by: call)
sub_AD8F:
AD8F  55              push bp
AD90  89 E5           mov bp, sp
AD92  83 EC 08        sub sp, 8
AD95  8B 7E 04        mov di, word ptr [bp + 4]
AD98  36 8B 45 06     mov ax, word ptr ss:[di + 6]
AD9C  BA BF 00        mov dx, 0xbf
AD9F  F7 E2           mul dx
ADA1  C4 3E 17 A9     les di, ptr [0xa917]
ADA5  03 F8           add di, ax
ADA7  89 7E FC        mov word ptr [bp - 4], di
ADAA  8C 46 FE        mov word ptr [bp - 2], es
ADAD  8B 7E 04        mov di, word ptr [bp + 4]
ADB0  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
ADB4  D1 E0           shl ax, 1
ADB6  C4 7E FC        les di, ptr [bp - 4]
ADB9  03 F8           add di, ax
ADBB  26 8B 45 FE     mov ax, word ptr es:[di - 2]
ADBF  BA 14 00        mov dx, 0x14
ADC2  F7 E2           mul dx
ADC4  C4 3E 1B A9     les di, ptr [0xa91b]
ADC8  03 F8           add di, ax
ADCA  26 8A 45 07     mov al, byte ptr es:[di + 7]
ADCE  30 E4           xor ah, ah
ADD0  8B F8           mov di, ax
ADD2  C6 85 A2 99 00  mov byte ptr [di - 0x665e], 0
ADD7  8B 7E 04        mov di, word ptr [bp + 4]
ADDA  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
ADDE  D1 E0           shl ax, 1
ADE0  C4 7E FC        les di, ptr [bp - 4]
ADE3  03 F8           add di, ax
ADE5  81 C7 FE FF     add di, 0xfffe
ADE9  06              push es
ADEA  57              push di
ADEB  8B 46 06        mov ax, word ptr [bp + 6]
ADEE  D1 E0           shl ax, 1
ADF0  C4 7E FC        les di, ptr [bp - 4]
ADF3  03 F8           add di, ax
ADF5  81 C7 FE FF     add di, 0xfffe
ADF9  06              push es
ADFA  57              push di
ADFB  B8 02 00        mov ax, 2
ADFE  50              push ax
ADFF  9A 7B 00 4B 21  call far 214B:007B
AE04  8B 7E 04        mov di, word ptr [bp + 4]
AE07  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
AE0B  D1 E0           shl ax, 1
AE0D  C4 7E FC        les di, ptr [bp - 4]
AE10  03 F8           add di, ax
AE12  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AE16  BA 14 00        mov dx, 0x14
AE19  F7 E2           mul dx
AE1B  C4 3E 1B A9     les di, ptr [0xa91b]
AE1F  03 F8           add di, ax
AE21  89 7E F8        mov word ptr [bp - 8], di
AE24  8C 46 FA        mov word ptr [bp - 6], es
AE27  C4 7E F8        les di, ptr [bp - 8]
AE2A  26 8A 45 06     mov al, byte ptr es:[di + 6]
AE2E  50              push ax
AE2F  BF 0F AD        mov di, 0xad0f
AE32  0E              push cs
AE33  57              push di
AE34  9A DF 08 E4 23  call far 23E4:08DF
AE39  74 2D           je 0xae68
AE3B  8B 46 06        mov ax, word ptr [bp + 6]
AE3E  D1 E0           shl ax, 1
AE40  C4 7E FC        les di, ptr [bp - 4]
AE43  03 F8           add di, ax
AE45  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AE49  BA 14 00        mov dx, 0x14
AE4C  F7 E2           mul dx
AE4E  C4 3E 1B A9     les di, ptr [0xa91b]
AE52  03 F8           add di, ax
AE54  26 8A 45 07     mov al, byte ptr es:[di + 7]
AE58  50              push ax
AE59  BF 0F AD        mov di, 0xad0f
AE5C  0E              push cs
AE5D  57              push di
AE5E  9A DF 08 E4 23  call far 23E4:08DF
AE63  74 03           je 0xae68
AE65  E9 BA 00        jmp 0xaf22
loc_AE68:
AE68  C4 7E F8        les di, ptr [bp - 8]
AE6B  26 8A 45 06     mov al, byte ptr es:[di + 6]
AE6F  50              push ax
AE70  BF 2F AD        mov di, 0xad2f
AE73  0E              push cs
AE74  57              push di
AE75  9A DF 08 E4 23  call far 23E4:08DF
AE7A  74 2A           je 0xaea6
AE7C  8B 46 06        mov ax, word ptr [bp + 6]
AE7F  D1 E0           shl ax, 1
AE81  C4 7E FC        les di, ptr [bp - 4]
AE84  03 F8           add di, ax
AE86  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AE8A  BA 14 00        mov dx, 0x14
AE8D  F7 E2           mul dx
AE8F  C4 3E 1B A9     les di, ptr [0xa91b]
AE93  03 F8           add di, ax
AE95  26 8A 45 07     mov al, byte ptr es:[di + 7]
AE99  50              push ax
AE9A  BF 2F AD        mov di, 0xad2f
AE9D  0E              push cs
AE9E  57              push di
AE9F  9A DF 08 E4 23  call far 23E4:08DF
AEA4  75 7C           jne 0xaf22
loc_AEA6:
AEA6  C4 7E F8        les di, ptr [bp - 8]
AEA9  26 8A 45 06     mov al, byte ptr es:[di + 6]
AEAD  50              push ax
AEAE  BF 4F AD        mov di, 0xad4f
AEB1  0E              push cs
AEB2  57              push di
AEB3  9A DF 08 E4 23  call far 23E4:08DF
AEB8  74 2A           je 0xaee4
AEBA  8B 46 06        mov ax, word ptr [bp + 6]
AEBD  D1 E0           shl ax, 1
AEBF  C4 7E FC        les di, ptr [bp - 4]
AEC2  03 F8           add di, ax
AEC4  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AEC8  BA 14 00        mov dx, 0x14
AECB  F7 E2           mul dx
AECD  C4 3E 1B A9     les di, ptr [0xa91b]
AED1  03 F8           add di, ax
AED3  26 8A 45 07     mov al, byte ptr es:[di + 7]
AED7  50              push ax
AED8  BF 4F AD        mov di, 0xad4f
AEDB  0E              push cs
AEDC  57              push di
AEDD  9A DF 08 E4 23  call far 23E4:08DF
AEE2  75 3E           jne 0xaf22
loc_AEE4:
AEE4  C4 7E F8        les di, ptr [bp - 8]
AEE7  26 8A 45 06     mov al, byte ptr es:[di + 6]
AEEB  50              push ax
AEEC  BF 6F AD        mov di, 0xad6f
AEEF  0E              push cs
AEF0  57              push di
AEF1  9A DF 08 E4 23  call far 23E4:08DF
AEF6  74 66           je 0xaf5e
AEF8  8B 46 06        mov ax, word ptr [bp + 6]
AEFB  D1 E0           shl ax, 1
AEFD  C4 7E FC        les di, ptr [bp - 4]
AF00  03 F8           add di, ax
AF02  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AF06  BA 14 00        mov dx, 0x14
AF09  F7 E2           mul dx
AF0B  C4 3E 1B A9     les di, ptr [0xa91b]
AF0F  03 F8           add di, ax
AF11  26 8A 45 07     mov al, byte ptr es:[di + 7]
AF15  50              push ax
AF16  BF 6F AD        mov di, 0xad6f
AF19  0E              push cs
AF1A  57              push di
AF1B  9A DF 08 E4 23  call far 23E4:08DF
AF20  74 3C           je 0xaf5e
loc_AF22:
AF22  8B 46 06        mov ax, word ptr [bp + 6]
AF25  D1 E0           shl ax, 1
AF27  C4 7E FC        les di, ptr [bp - 4]
AF2A  03 F8           add di, ax
AF2C  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AF30  BA 14 00        mov dx, 0x14
AF33  F7 E2           mul dx
AF35  C4 3E 1B A9     les di, ptr [0xa91b]
AF39  03 F8           add di, ax
AF3B  26 8A 4D 07     mov cl, byte ptr es:[di + 7]
AF3F  8B 46 06        mov ax, word ptr [bp + 6]
AF42  D1 E0           shl ax, 1
AF44  C4 7E FC        les di, ptr [bp - 4]
AF47  03 F8           add di, ax
AF49  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AF4D  BA 14 00        mov dx, 0x14
AF50  F7 E2           mul dx
AF52  C4 3E 1B A9     les di, ptr [0xa91b]
AF56  03 F8           add di, ax
AF58  26 88 4D 06     mov byte ptr es:[di + 6], cl
AF5C  EB 24           jmp 0xaf82
loc_AF5E:
AF5E  C4 7E F8        les di, ptr [bp - 8]
AF61  26 8A 4D 06     mov cl, byte ptr es:[di + 6]
AF65  8B 46 06        mov ax, word ptr [bp + 6]
AF68  D1 E0           shl ax, 1
AF6A  C4 7E FC        les di, ptr [bp - 4]
AF6D  03 F8           add di, ax
AF6F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AF73  BA 14 00        mov dx, 0x14
AF76  F7 E2           mul dx
AF78  C4 3E 1B A9     les di, ptr [0xa91b]
AF7C  03 F8           add di, ax
AF7E  26 88 4D 06     mov byte ptr es:[di + 6], cl
loc_AF82:
AF82  C4 7E F8        les di, ptr [bp - 8]
AF85  26 8A 45 07     mov al, byte ptr es:[di + 7]
AF89  C4 7E F8        les di, ptr [bp - 8]
AF8C  26 88 45 06     mov byte ptr es:[di + 6], al
AF90  8B 7E 04        mov di, word ptr [bp + 4]
AF93  36 FF 75 FE     push word ptr ss:[di - 2]
AF97  FF 76 04        push word ptr [bp + 4]
AF9A  E8 CA FC        call 0xac67
AF9D  89 EC           mov sp, bp
AF9F  5D              pop bp
AFA0  C2 04 00        ret 4

; ---- routine 0791:AFA3  (found by: call)
sub_AFA3:
AFA3  55              push bp
AFA4  89 E5           mov bp, sp
AFA6  83 EC 08        sub sp, 8
AFA9  8B 7E 04        mov di, word ptr [bp + 4]
AFAC  36 8B 45 06     mov ax, word ptr ss:[di + 6]
AFB0  BA BF 00        mov dx, 0xbf
AFB3  F7 E2           mul dx
AFB5  C4 3E 17 A9     les di, ptr [0xa917]
AFB9  03 F8           add di, ax
AFBB  89 7E F8        mov word ptr [bp - 8], di
AFBE  8C 46 FA        mov word ptr [bp - 6], es
AFC1  C7 46 FE 01 00  mov word ptr [bp - 2], 1
AFC6  EB 03           jmp 0xafcb
loc_AFC8:
AFC8  FF 46 FE        inc word ptr [bp - 2]
loc_AFCB:
AFCB  8B 46 FE        mov ax, word ptr [bp - 2]
AFCE  D1 E0           shl ax, 1
AFD0  C4 7E F8        les di, ptr [bp - 8]
AFD3  03 F8           add di, ax
AFD5  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AFD9  89 46 FC        mov word ptr [bp - 4], ax
AFDC  FF 76 FC        push word ptr [bp - 4]
AFDF  C4 7E F8        les di, ptr [bp - 8]
AFE2  06              push es
AFE3  57              push di
AFE4  E8 01 FB        call 0xaae8
AFE7  8B 7E 04        mov di, word ptr [bp + 4]
AFEA  36 89 45 FE     mov word ptr ss:[di - 2], ax
AFEE  8B 7E 04        mov di, word ptr [bp + 4]
AFF1  36 83 7D FE 00  cmp word ptr ss:[di - 2], 0
AFF6  75 03           jne 0xaffb
AFF8  E9 90 00        jmp 0xb08b
loc_AFFB:
AFFB  FF 76 FC        push word ptr [bp - 4]
AFFE  9A 7E 37 71 17  call far 1771:377E
B003  50              push ax
B004  8B 7E 04        mov di, word ptr [bp + 4]
B007  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
B00B  D1 E0           shl ax, 1
B00D  C4 7E F8        les di, ptr [bp - 8]
B010  03 F8           add di, ax
B012  26 FF 75 FE     push word ptr es:[di - 2]
B016  9A 7E 37 71 17  call far 1771:377E
B01B  5A              pop dx
B01C  3B C2           cmp ax, dx
B01E  77 5F           ja 0xb07f
B020  8B 46 FC        mov ax, word ptr [bp - 4]
B023  BA 14 00        mov dx, 0x14
B026  F7 E2           mul dx
B028  C4 3E 1B A9     les di, ptr [0xa91b]
B02C  03 F8           add di, ax
B02E  26 8A 4D 06     mov cl, byte ptr es:[di + 6]
B032  8B 46 FC        mov ax, word ptr [bp - 4]
B035  BA 14 00        mov dx, 0x14
B038  F7 E2           mul dx
B03A  C4 3E 1B A9     les di, ptr [0xa91b]
B03E  03 F8           add di, ax
B040  26 8A 45 07     mov al, byte ptr es:[di + 7]
B044  3A C1           cmp al, cl
B046  74 43           je 0xb08b
B048  8B 46 FC        mov ax, word ptr [bp - 4]
B04B  BA 14 00        mov dx, 0x14
B04E  F7 E2           mul dx
B050  C4 3E 1B A9     les di, ptr [0xa91b]
B054  03 F8           add di, ax
B056  26 8A 4D 06     mov cl, byte ptr es:[di + 6]
B05A  8B 7E 04        mov di, word ptr [bp + 4]
B05D  36 8B 45 FE     mov ax, word ptr ss:[di - 2]
B061  D1 E0           shl ax, 1
B063  C4 7E F8        les di, ptr [bp - 8]
B066  03 F8           add di, ax
B068  26 8B 45 FE     mov ax, word ptr es:[di - 2]
B06C  BA 14 00        mov dx, 0x14
B06F  F7 E2           mul dx
B071  C4 3E 1B A9     les di, ptr [0xa91b]
B075  03 F8           add di, ax
B077  26 8A 45 07     mov al, byte ptr es:[di + 7]
B07B  3A C1           cmp al, cl
B07D  75 0C           jne 0xb08b
loc_B07F:
B07F  FF 76 FE        push word ptr [bp - 2]
B082  FF 76 04        push word ptr [bp + 4]
B085  E8 07 FD        call 0xad8f
B088  E9 85 00        jmp 0xb110
loc_B08B:
B08B  FF 76 FC        push word ptr [bp - 4]
B08E  9A 16 32 71 17  call far 1771:3216
B093  08 C0           or al, al
B095  75 27           jne 0xb0be
B097  FF 76 FC        push word ptr [bp - 4]
B09A  9A 79 31 71 17  call far 1771:3179
B09F  08 C0           or al, al
B0A1  75 1B           jne 0xb0be
B0A3  83 7E FE 01     cmp word ptr [bp - 2], 1
B0A7  75 67           jne 0xb110
B0A9  8B 46 FC        mov ax, word ptr [bp - 4]
B0AC  BA 14 00        mov dx, 0x14
B0AF  F7 E2           mul dx
B0B1  C4 3E 1B A9     les di, ptr [0xa91b]
B0B5  03 F8           add di, ax
B0B7  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
B0BC  74 52           je 0xb110
loc_B0BE:
B0BE  8B 7E 04        mov di, word ptr [bp + 4]
B0C1  36 83 7D FE 00  cmp word ptr ss:[di - 2], 0
B0C6  74 0B           je 0xb0d3
B0C8  FF 76 FE        push word ptr [bp - 2]
B0CB  FF 76 04        push word ptr [bp + 4]
B0CE  E8 BE FC        call 0xad8f
B0D1  EB 3D           jmp 0xb110
loc_B0D3:
B0D3  8B 7E 04        mov di, word ptr [bp + 4]
B0D6  36 FF 75 06     push word ptr ss:[di + 6]
B0DA  8B 46 FC        mov ax, word ptr [bp - 4]
B0DD  BA 14 00        mov dx, 0x14
B0E0  F7 E2           mul dx
B0E2  C4 3E 1B A9     les di, ptr [0xa91b]
B0E6  03 F8           add di, ax
B0E8  26 8A 45 06     mov al, byte ptr es:[di + 6]
B0EC  30 E4           xor ah, ah
B0EE  50              push ax
B0EF  B8 14 00        mov ax, 0x14
B0F2  50              push ax
B0F3  E8 C2 F8        call 0xa9b8
B0F6  8B 7E 04        mov di, word ptr [bp + 4]
B0F9  36 89 45 FE     mov word ptr ss:[di - 2], ax
B0FD  8B 7E 04        mov di, word ptr [bp + 4]
B100  36 83 7D FE 00  cmp word ptr ss:[di - 2], 0
B105  74 09           je 0xb110
B107  FF 76 FE        push word ptr [bp - 2]
B10A  FF 76 04        push word ptr [bp + 4]
B10D  E8 7F FC        call 0xad8f
loc_B110:
B110  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
B114  74 03           je 0xb119
B116  E9 AF FE        jmp 0xafc8
loc_B119:
B119  89 EC           mov sp, bp
B11B  5D              pop bp
B11C  C2 02 00        ret 2

; ---- routine 0791:B11F  (found by: call)
sub_B11F:
B11F  55              push bp
B120  89 E5           mov bp, sp
B122  83 EC 06        sub sp, 6
B125  BF A2 99        mov di, 0x99a2
B128  1E              push ds
B129  57              push di
B12A  B8 0E 00        mov ax, 0xe
B12D  50              push ax
B12E  31 C0           xor ax, ax
B130  50              push ax
B131  9A 18 00 4B 21  call far 214B:0018
B136  C7 46 FC 0C 00  mov word ptr [bp - 4], 0xc
B13B  EB 03           jmp 0xb140
loc_B13D:
B13D  FF 46 FC        inc word ptr [bp - 4]
loc_B140:
B140  FF 76 FC        push word ptr [bp - 4]
B143  55              push bp
B144  E8 20 FB        call 0xac67
B147  83 7E FC 14     cmp word ptr [bp - 4], 0x14
B14B  75 F0           jne 0xb13d
B14D  55              push bp
B14E  E8 52 FE        call 0xafa3
B151  FF 76 06        push word ptr [bp + 6]
B154  9A CC 52 71 17  call far 1771:52CC
B159  89 EC           mov sp, bp
B15B  5D              pop bp
B15C  CA 02 00        retf 2

; ---- routine 0791:B15F  (found by: call)
sub_B15F:
B15F  55              push bp
B160  89 E5           mov bp, sp
B162  83 EC 06        sub sp, 6
B165  C4 7E 04        les di, ptr [bp + 4]
B168  89 7E FB        mov word ptr [bp - 5], di
B16B  8C 46 FD        mov word ptr [bp - 3], es
B16E  C4 7E FB        les di, ptr [bp - 5]
B171  26 8A 45 02     mov al, byte ptr es:[di + 2]
B175  50              push ax
B176  BF 3A 69        mov di, 0x693a
B179  1E              push ds
B17A  57              push di
B17B  9A DF 08 E4 23  call far 23E4:08DF
B180  74 09           je 0xb18b
B182  A0 3C 9B        mov al, byte ptr [0x9b3c]
B185  3A 06 3D 9B     cmp al, byte ptr [0x9b3d]
B189  74 04           je 0xb18f
loc_B18B:
B18B  B0 00           mov al, 0
B18D  EB 02           jmp 0xb191
loc_B18F:
B18F  B0 01           mov al, 1
loc_B191:
B191  88 46 FF        mov byte ptr [bp - 1], al
B194  8A 46 FF        mov al, byte ptr [bp - 1]
B197  89 EC           mov sp, bp
B199  5D              pop bp
B19A  C2 04 00        ret 4

; ---- routine 0791:B19D  (found by: call)
sub_B19D:
B19D  55              push bp
B19E  89 E5           mov bp, sp
B1A0  83 EC 06        sub sp, 6
B1A3  C6 46 FF 00     mov byte ptr [bp - 1], 0
B1A7  EB 03           jmp 0xb1ac
loc_B1A9:
B1A9  FE 46 FF        inc byte ptr [bp - 1]
loc_B1AC:
B1AC  8B 46 04        mov ax, word ptr [bp + 4]
B1AF  89 46 FB        mov word ptr [bp - 5], ax
B1B2  B8 01 00        mov ax, 1
B1B5  3B 46 FB        cmp ax, word ptr [bp - 5]
B1B8  76 03           jbe 0xb1bd
B1BA  E9 B3 00        jmp 0xb270
loc_B1BD:
B1BD  89 46 FD        mov word ptr [bp - 3], ax
B1C0  EB 03           jmp 0xb1c5
loc_B1C2:
B1C2  FF 46 FD        inc word ptr [bp - 3]
loc_B1C5:
B1C5  80 7E FF 00     cmp byte ptr [bp - 1], 0
B1C9  74 04           je 0xb1cf
B1CB  B0 00           mov al, 0
B1CD  EB 02           jmp 0xb1d1
loc_B1CF:
B1CF  B0 01           mov al, 1
loc_B1D1:
B1D1  98              cwde
B1D2  8B F8           mov di, ax
B1D4  D1 E7           shl di, 1
B1D6  FF B5 4D 9B     push word ptr [di - 0x64b3]
B1DA  9A B1 06 4B 21  call far 214B:06B1
B1DF  50              push ax
B1E0  8A 46 FF        mov al, byte ptr [bp - 1]
B1E3  98              cwde
B1E4  8B F8           mov di, ax
B1E6  D1 E7           shl di, 1
B1E8  FF B5 4D 9B     push word ptr [di - 0x64b3]
B1EC  9A B1 06 4B 21  call far 214B:06B1
B1F1  5A              pop dx
B1F2  3B C2           cmp ax, dx
B1F4  7E 6F           jle 0xb265
B1F6  80 7E FF 00     cmp byte ptr [bp - 1], 0
B1FA  74 04           je 0xb200
B1FC  B0 00           mov al, 0
B1FE  EB 02           jmp 0xb202
loc_B200:
B200  B0 01           mov al, 1
loc_B202:
B202  98              cwde
B203  8B F8           mov di, ax
B205  D1 E7           shl di, 1
B207  8B 85 49 9B     mov ax, word ptr [di - 0x64b7]
B20B  D1 E0           shl ax, 1
B20D  50              push ax
B20E  9A B1 06 4B 21  call far 214B:06B1
B213  50              push ax
B214  8A 46 FF        mov al, byte ptr [bp - 1]
B217  98              cwde
B218  8B F8           mov di, ax
B21A  D1 E7           shl di, 1
B21C  FF B5 51 9B     push word ptr [di - 0x64af]
B220  9A B1 06 4B 21  call far 214B:06B1
B225  5A              pop dx
B226  3B C2           cmp ax, dx
B228  7E 3B           jle 0xb265
B22A  80 7E FF 00     cmp byte ptr [bp - 1], 0
B22E  74 04           je 0xb234
B230  B0 00           mov al, 0
B232  EB 02           jmp 0xb236
loc_B234:
B234  B0 01           mov al, 1
loc_B236:
B236  98              cwde
B237  8B F8           mov di, ax
B239  D1 E7           shl di, 1
B23B  FF B5 45 9B     push word ptr [di - 0x64bb]
B23F  9A B1 06 4B 21  call far 214B:06B1
B244  50              push ax
B245  8A 46 FF        mov al, byte ptr [bp - 1]
B248  98              cwde
B249  8B F8           mov di, ax
B24B  D1 E7           shl di, 1
B24D  FF B5 51 9B     push word ptr [di - 0x64af]
B251  9A B1 06 4B 21  call far 214B:06B1
B256  5A              pop dx
B257  3B C2           cmp ax, dx
B259  7E 0A           jle 0xb265
B25B  8A 46 FF        mov al, byte ptr [bp - 1]
B25E  98              cwde
B25F  8B F8           mov di, ax
B261  FE 85 3C 9B     inc byte ptr [di - 0x64c4]
loc_B265:
B265  8B 46 FD        mov ax, word ptr [bp - 3]
B268  3B 46 FB        cmp ax, word ptr [bp - 5]
B26B  74 03           je 0xb270
B26D  E9 52 FF        jmp 0xb1c2
loc_B270:
B270  80 7E FF 01     cmp byte ptr [bp - 1], 1
B274  74 03           je 0xb279
B276  E9 30 FF        jmp 0xb1a9
loc_B279:
B279  89 EC           mov sp, bp
B27B  5D              pop bp
B27C  C2 02 00        ret 2

; ---- routine 0791:B27F  (found by: call)
sub_B27F:
B27F  55              push bp
B280  89 E5           mov bp, sp
B282  83 EC 04        sub sp, 4
B285  8B 46 04        mov ax, word ptr [bp + 4]
B288  BA 14 00        mov dx, 0x14
B28B  F7 E2           mul dx
B28D  C4 3E 1B A9     les di, ptr [0xa91b]
B291  03 F8           add di, ax
B293  89 7E FC        mov word ptr [bp - 4], di
B296  8C 46 FE        mov word ptr [bp - 2], es
B299  B8 08 00        mov ax, 8
B29C  50              push ax
B29D  C4 7E FC        les di, ptr [bp - 4]
B2A0  81 C7 10 00     add di, 0x10
B2A4  06              push es
B2A5  57              push di
B2A6  9A A1 0C 4B 21  call far 214B:0CA1
B2AB  B8 06 00        mov ax, 6
B2AE  50              push ax
B2AF  C4 7E FC        les di, ptr [bp - 4]
B2B2  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
B2B6  30 E4           xor ah, ah
B2B8  50              push ax
B2B9  9A 57 0C 4B 21  call far 214B:0C57
B2BE  08 C0           or al, al
B2C0  74 12           je 0xb2d4
B2C2  B8 08 00        mov ax, 8
B2C5  50              push ax
B2C6  C4 7E FC        les di, ptr [bp - 4]
B2C9  81 C7 10 00     add di, 0x10
B2CD  06              push es
B2CE  57              push di
B2CF  9A 79 0C 4B 21  call far 214B:0C79
loc_B2D4:
B2D4  B8 06 00        mov ax, 6
B2D7  50              push ax
B2D8  C4 7E FC        les di, ptr [bp - 4]
B2DB  81 C7 10 00     add di, 0x10
B2DF  06              push es
B2E0  57              push di
B2E1  9A A1 0C 4B 21  call far 214B:0CA1
B2E6  B8 05 00        mov ax, 5
B2E9  50              push ax
B2EA  C4 7E FC        les di, ptr [bp - 4]
B2ED  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
B2F1  30 E4           xor ah, ah
B2F3  50              push ax
B2F4  9A 57 0C 4B 21  call far 214B:0C57
B2F9  08 C0           or al, al
B2FB  74 4F           je 0xb34c
B2FD  B8 04 00        mov ax, 4
B300  50              push ax
B301  C4 7E FC        les di, ptr [bp - 4]
B304  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
B308  30 E4           xor ah, ah
B30A  50              push ax
B30B  9A 57 0C 4B 21  call far 214B:0C57
B310  08 C0           or al, al
B312  75 14           jne 0xb328
B314  B8 04 00        mov ax, 4
B317  50              push ax
B318  C4 7E FC        les di, ptr [bp - 4]
B31B  81 C7 10 00     add di, 0x10
B31F  06              push es
B320  57              push di
B321  9A 79 0C 4B 21  call far 214B:0C79
B326  EB 24           jmp 0xb34c
loc_B328:
B328  B8 08 00        mov ax, 8
B32B  50              push ax
B32C  C4 7E FC        les di, ptr [bp - 4]
B32F  81 C7 10 00     add di, 0x10
B333  06              push es
B334  57              push di
B335  9A 79 0C 4B 21  call far 214B:0C79
B33A  B8 04 00        mov ax, 4
B33D  50              push ax
B33E  C4 7E FC        les di, ptr [bp - 4]
B341  81 C7 10 00     add di, 0x10
B345  06              push es
B346  57              push di
B347  9A A1 0C 4B 21  call far 214B:0CA1
loc_B34C:
B34C  B8 05 00        mov ax, 5
B34F  50              push ax
B350  C4 7E FC        les di, ptr [bp - 4]
B353  81 C7 10 00     add di, 0x10
B357  06              push es
B358  57              push di
B359  9A A1 0C 4B 21  call far 214B:0CA1
B35E  89 EC           mov sp, bp
B360  5D              pop bp
B361  C2 02 00        ret 2

; ---- routine 0791:B364  (found by: call)
sub_B364:
B364  55              push bp
B365  89 E5           mov bp, sp
B367  83 EC 06        sub sp, 6
B36A  8B 46 06        mov ax, word ptr [bp + 6]
B36D  BA 14 00        mov dx, 0x14
B370  F7 E2           mul dx
B372  C4 3E 1B A9     les di, ptr [0xa91b]
B376  03 F8           add di, ax
B378  89 7E FA        mov word ptr [bp - 6], di
B37B  8C 46 FC        mov word ptr [bp - 4], es
B37E  C4 7E FA        les di, ptr [bp - 6]
B381  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
B385  98              cwde
B386  89 46 FE        mov word ptr [bp - 2], ax
B389  8B 46 04        mov ax, word ptr [bp + 4]
B38C  01 46 FE        add word ptr [bp - 2], ax
B38F  83 7E FE 01     cmp word ptr [bp - 2], 1
B393  7D 07           jge 0xb39c
B395  C7 46 FE 01 00  mov word ptr [bp - 2], 1
B39A  EB 0B           jmp 0xb3a7
loc_B39C:
B39C  83 7E FE 20     cmp word ptr [bp - 2], 0x20
B3A0  7E 05           jle 0xb3a7
B3A2  C7 46 FE 20 00  mov word ptr [bp - 2], 0x20
loc_B3A7:
B3A7  8A 46 FE        mov al, byte ptr [bp - 2]
B3AA  C4 7E FA        les di, ptr [bp - 6]
B3AD  26 88 45 0C     mov byte ptr es:[di + 0xc], al
B3B1  89 EC           mov sp, bp
B3B3  5D              pop bp
B3B4  C2 04 00        ret 4

; ---- routine 0791:B3B7  (found by: call)
sub_B3B7:
B3B7  55              push bp
B3B8  89 E5           mov bp, sp
B3BA  83 EC 0E        sub sp, 0xe
B3BD  8B 46 06        mov ax, word ptr [bp + 6]
B3C0  BA 14 00        mov dx, 0x14
B3C3  F7 E2           mul dx
B3C5  C4 3E 1B A9     les di, ptr [0xa91b]
B3C9  03 F8           add di, ax
B3CB  89 7E F6        mov word ptr [bp - 0xa], di
B3CE  8C 46 F8        mov word ptr [bp - 8], es
B3D1  C4 3E 23 A9     les di, ptr [0xa923]
B3D5  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
B3DA  74 07           je 0xb3e3
B3DC  C7 46 FE 05 00  mov word ptr [bp - 2], 5
B3E1  EB 06           jmp 0xb3e9
loc_B3E3:
B3E3  8B 46 04        mov ax, word ptr [bp + 4]
B3E6  89 46 FE        mov word ptr [bp - 2], ax
loc_B3E9:
B3E9  C4 7E F6        les di, ptr [bp - 0xa]
B3EC  26 FE 45 11     inc byte ptr es:[di + 0x11]
B3F0  31 C0           xor ax, ax
B3F2  89 46 FA        mov word ptr [bp - 6], ax
B3F5  C7 46 FC 01 00  mov word ptr [bp - 4], 1
B3FA  EB 03           jmp 0xb3ff
loc_B3FC:
B3FC  FF 46 FC        inc word ptr [bp - 4]
loc_B3FF:
B3FF  8B 46 FC        mov ax, word ptr [bp - 4]
B402  B1 04           mov cl, 4
B404  D3 E0           shl ax, cl
B406  8B D8           mov bx, ax
B408  8B 46 FE        mov ax, word ptr [bp - 2]
B40B  BA 60 00        mov dx, 0x60
B40E  F7 E2           mul dx
B410  C4 3E 3F A9     les di, ptr [0xa93f]
B414  03 F8           add di, ax
B416  03 FB           add di, bx
B418  81 C7 90 FF     add di, 0xff90
B41C  89 7E F2        mov word ptr [bp - 0xe], di
B41F  8C 46 F4        mov word ptr [bp - 0xc], es
B422  C4 7E F2        les di, ptr [bp - 0xe]
B425  26 8B 45 0E     mov ax, word ptr es:[di + 0xe]
B429  3B 46 06        cmp ax, word ptr [bp + 6]
B42C  75 06           jne 0xb434
B42E  8B 46 FC        mov ax, word ptr [bp - 4]
B431  89 46 FA        mov word ptr [bp - 6], ax
loc_B434:
B434  83 7E FC 03     cmp word ptr [bp - 4], 3
B438  75 C2           jne 0xb3fc
B43A  83 7E FA 00     cmp word ptr [bp - 6], 0
B43E  75 03           jne 0xb443
B440  E9 C8 00        jmp 0xb50b
loc_B443:
B443  C4 7E F6        les di, ptr [bp - 0xa]
B446  26 8A 45 11     mov al, byte ptr es:[di + 0x11]
B44A  30 E4           xor ah, ah
B44C  50              push ax
B44D  8B 46 FA        mov ax, word ptr [bp - 6]
B450  B1 04           mov cl, 4
B452  D3 E0           shl ax, cl
B454  8B D8           mov bx, ax
B456  8B 46 FE        mov ax, word ptr [bp - 2]
B459  BA 60 00        mov dx, 0x60
B45C  F7 E2           mul dx
B45E  C4 3E 3F A9     les di, ptr [0xa93f]
B462  03 F8           add di, ax
B464  03 FB           add di, bx
B466  58              pop ax
B467  26 89 45 9C     mov word ptr es:[di - 0x64], ax
B46B  8B 46 FA        mov ax, word ptr [bp - 6]
B46E  89 46 FC        mov word ptr [bp - 4], ax
loc_B471:
B471  83 7E FC 01     cmp word ptr [bp - 4], 1
B475  77 03           ja 0xb47a
B477  E9 8E 00        jmp 0xb508
loc_B47A:
B47A  8B 46 FC        mov ax, word ptr [bp - 4]
B47D  48              dec ax
B47E  B1 04           mov cl, 4
B480  D3 E0           shl ax, cl
B482  8B D8           mov bx, ax
B484  8B 46 FE        mov ax, word ptr [bp - 2]
B487  BA 60 00        mov dx, 0x60
B48A  F7 E2           mul dx
B48C  C4 3E 3F A9     les di, ptr [0xa93f]
B490  03 F8           add di, ax
B492  03 FB           add di, bx
B494  26 FF 75 9C     push word ptr es:[di - 0x64]
B498  8B 46 FC        mov ax, word ptr [bp - 4]
B49B  B1 04           mov cl, 4
B49D  D3 E0           shl ax, cl
B49F  8B D8           mov bx, ax
B4A1  8B 46 FE        mov ax, word ptr [bp - 2]
B4A4  BA 60 00        mov dx, 0x60
B4A7  F7 E2           mul dx
B4A9  C4 3E 3F A9     les di, ptr [0xa93f]
B4AD  03 F8           add di, ax
B4AF  03 FB           add di, bx
B4B1  26 8B 45 9C     mov ax, word ptr es:[di - 0x64]
B4B5  5A              pop dx
B4B6  3B C2           cmp ax, dx
B4B8  76 4E           jbe 0xb508
B4BA  8B 46 FC        mov ax, word ptr [bp - 4]
B4BD  B1 04           mov cl, 4
B4BF  D3 E0           shl ax, cl
B4C1  8B D8           mov bx, ax
B4C3  8B 46 FE        mov ax, word ptr [bp - 2]
B4C6  BA 60 00        mov dx, 0x60
B4C9  F7 E2           mul dx
B4CB  C4 3E 3F A9     les di, ptr [0xa93f]
B4CF  03 F8           add di, ax
B4D1  03 FB           add di, bx
B4D3  81 C7 90 FF     add di, 0xff90
B4D7  06              push es
B4D8  57              push di
B4D9  8B 46 FC        mov ax, word ptr [bp - 4]
B4DC  48              dec ax
B4DD  B1 04           mov cl, 4
B4DF  D3 E0           shl ax, cl
B4E1  8B D8           mov bx, ax
B4E3  8B 46 FE        mov ax, word ptr [bp - 2]
B4E6  BA 60 00        mov dx, 0x60
B4E9  F7 E2           mul dx
B4EB  C4 3E 3F A9     les di, ptr [0xa93f]
B4EF  03 F8           add di, ax
B4F1  03 FB           add di, bx
B4F3  81 C7 90 FF     add di, 0xff90
B4F7  06              push es
B4F8  57              push di
B4F9  B8 10 00        mov ax, 0x10
B4FC  50              push ax
B4FD  9A 7B 00 4B 21  call far 214B:007B
B502  FF 4E FC        dec word ptr [bp - 4]
B505  E9 69 FF        jmp 0xb471
loc_B508:
B508  E9 F1 00        jmp 0xb5fc
loc_B50B:
B50B  C7 46 FC 01 00  mov word ptr [bp - 4], 1
B510  EB 03           jmp 0xb515
loc_B512:
B512  FF 46 FC        inc word ptr [bp - 4]
loc_B515:
B515  8B 46 FC        mov ax, word ptr [bp - 4]
B518  B1 04           mov cl, 4
B51A  D3 E0           shl ax, cl
B51C  8B D8           mov bx, ax
B51E  8B 46 FE        mov ax, word ptr [bp - 2]
B521  BA 60 00        mov dx, 0x60
B524  F7 E2           mul dx
B526  C4 3E 3F A9     les di, ptr [0xa93f]
B52A  03 F8           add di, ax
B52C  03 FB           add di, bx
B52E  81 C7 90 FF     add di, 0xff90
B532  89 7E F2        mov word ptr [bp - 0xe], di
B535  8C 46 F4        mov word ptr [bp - 0xc], es
B538  C4 7E F6        les di, ptr [bp - 0xa]
B53B  26 8A 45 11     mov al, byte ptr es:[di + 0x11]
B53F  30 E4           xor ah, ah
B541  C4 7E F2        les di, ptr [bp - 0xe]
B544  26 3B 45 0C     cmp ax, word ptr es:[di + 0xc]
B548  77 03           ja 0xb54d
B54A  E9 A6 00        jmp 0xb5f3
loc_B54D:
B54D  83 7E FC 03     cmp word ptr [bp - 4], 3
B551  73 50           jae 0xb5a3
B553  8B 46 FC        mov ax, word ptr [bp - 4]
B556  B1 04           mov cl, 4
B558  D3 E0           shl ax, cl
B55A  8B D8           mov bx, ax
B55C  8B 46 FE        mov ax, word ptr [bp - 2]
B55F  BA 60 00        mov dx, 0x60
B562  F7 E2           mul dx
B564  C4 3E 3F A9     les di, ptr [0xa93f]
B568  03 F8           add di, ax
B56A  03 FB           add di, bx
B56C  81 C7 90 FF     add di, 0xff90
B570  06              push es
B571  57              push di
B572  8B 46 FC        mov ax, word ptr [bp - 4]
B575  40              inc ax
B576  B1 04           mov cl, 4
B578  D3 E0           shl ax, cl
B57A  8B D8           mov bx, ax
B57C  8B 46 FE        mov ax, word ptr [bp - 2]
B57F  BA 60 00        mov dx, 0x60
B582  F7 E2           mul dx
B584  C4 3E 3F A9     les di, ptr [0xa93f]
B588  03 F8           add di, ax
B58A  03 FB           add di, bx
B58C  81 C7 90 FF     add di, 0xff90
B590  06              push es
B591  57              push di
B592  B8 03 00        mov ax, 3
B595  2B 46 FC        sub ax, word ptr [bp - 4]
B598  B9 04 00        mov cx, 4
B59B  D3 E0           shl ax, cl
B59D  50              push ax
B59E  9A 3C 00 4B 21  call far 214B:003C
loc_B5A3:
B5A3  8B 46 06        mov ax, word ptr [bp + 6]
B5A6  C4 7E F2        les di, ptr [bp - 0xe]
B5A9  26 89 45 0E     mov word ptr es:[di + 0xe], ax
B5AD  8B 46 06        mov ax, word ptr [bp + 6]
B5B0  C4 3E 70 9B     les di, ptr [0x9b70]
B5B4  03 F8           add di, ax
B5B6  26 8A 05        mov al, byte ptr es:[di]
B5B9  C4 7E F2        les di, ptr [bp - 0xe]
B5BC  26 88 05        mov byte ptr es:[di], al
B5BF  8B 46 06        mov ax, word ptr [bp + 6]
B5C2  BA 0B 00        mov dx, 0xb
B5C5  F7 E2           mul dx
B5C7  C4 3E 6C 9B     les di, ptr [0x9b6c]
B5CB  03 F8           add di, ax
B5CD  06              push es
B5CE  57              push di
B5CF  C4 7E F2        les di, ptr [bp - 0xe]
B5D2  81 C7 01 00     add di, 1
B5D6  06              push es
B5D7  57              push di
B5D8  B8 0A 00        mov ax, 0xa
B5DB  50              push ax
B5DC  9A 44 06 E4 23  call far 23E4:0644
B5E1  C4 7E F6        les di, ptr [bp - 0xa]
B5E4  26 8A 45 11     mov al, byte ptr es:[di + 0x11]
B5E8  30 E4           xor ah, ah
B5EA  C4 7E F2        les di, ptr [bp - 0xe]
B5ED  26 89 45 0C     mov word ptr es:[di + 0xc], ax
B5F1  EB 09           jmp 0xb5fc
loc_B5F3:
B5F3  83 7E FC 03     cmp word ptr [bp - 4], 3
B5F7  74 03           je 0xb5fc
B5F9  E9 16 FF        jmp 0xb512
loc_B5FC:
B5FC  89 EC           mov sp, bp
B5FE  5D              pop bp
B5FF  C2 04 00        ret 4

; ---- routine 0791:B602  (found by: far)
sub_B602:
B602  55              push bp
B603  89 E5           mov bp, sp
B605  83 EC 12        sub sp, 0x12
B608  C4 7E 06        les di, ptr [bp + 6]
B60B  89 7E F6        mov word ptr [bp - 0xa], di
B60E  8C 46 F8        mov word ptr [bp - 8], es
B611  C4 7E 06        les di, ptr [bp + 6]
B614  06              push es
B615  57              push di
B616  9A 03 5A 71 17  call far 1771:5A03
B61B  88 46 FE        mov byte ptr [bp - 2], al
B61E  C6 46 FF 00     mov byte ptr [bp - 1], 0
B622  EB 03           jmp 0xb627
loc_B624:
B624  FE 46 FF        inc byte ptr [bp - 1]
loc_B627:
B627  8A 46 FF        mov al, byte ptr [bp - 1]
B62A  98              cwde
B62B  D1 E0           shl ax, 1
B62D  C4 7E F6        les di, ptr [bp - 0xa]
B630  03 F8           add di, ax
B632  26 8B 45 04     mov ax, word ptr es:[di + 4]
B636  BA BF 00        mov dx, 0xbf
B639  F7 E2           mul dx
B63B  C4 3E 17 A9     les di, ptr [0xa917]
B63F  03 F8           add di, ax
B641  89 7E F2        mov word ptr [bp - 0xe], di
B644  8C 46 F4        mov word ptr [bp - 0xc], es
B647  8A 46 FF        mov al, byte ptr [bp - 1]
B64A  98              cwde
B64B  C4 7E F6        les di, ptr [bp - 0xa]
B64E  03 F8           add di, ax
B650  26 8A 05        mov al, byte ptr es:[di]
B653  30 E4           xor ah, ah
B655  89 46 FA        mov word ptr [bp - 6], ax
loc_B658:
B658  83 7E FA 00     cmp word ptr [bp - 6], 0
B65C  76 5F           jbe 0xb6bd
B65E  B8 1E 00        mov ax, 0x1e
B661  50              push ax
B662  9A B1 06 4B 21  call far 214B:06B1
B667  8B F8           mov di, ax
B669  8A 85 09 0A     mov al, byte ptr [di + 0xa09]
B66D  30 E4           xor ah, ah
B66F  D1 E0           shl ax, 1
B671  C4 7E F2        les di, ptr [bp - 0xe]
B674  03 F8           add di, ax
B676  26 8B 45 FE     mov ax, word ptr es:[di - 2]
B67A  89 46 FC        mov word ptr [bp - 4], ax
B67D  8B 46 FC        mov ax, word ptr [bp - 4]
B680  BA 14 00        mov dx, 0x14
B683  F7 E2           mul dx
B685  C4 3E 1B A9     les di, ptr [0xa91b]
B689  03 F8           add di, ax
B68B  89 7E EE        mov word ptr [bp - 0x12], di
B68E  8C 46 F0        mov word ptr [bp - 0x10], es
B691  C4 7E EE        les di, ptr [bp - 0x12]
B694  26 FF 45 0A     inc word ptr es:[di + 0xa]
B698  80 7E FE 00     cmp byte ptr [bp - 2], 0
B69C  74 10           je 0xb6ae
B69E  FF 76 FC        push word ptr [bp - 4]
B6A1  C4 7E F2        les di, ptr [bp - 0xe]
B6A4  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
B6A8  30 E4           xor ah, ah
B6AA  50              push ax
B6AB  E8 09 FD        call 0xb3b7
loc_B6AE:
B6AE  FF 76 FC        push word ptr [bp - 4]
B6B1  B8 01 00        mov ax, 1
B6B4  50              push ax
B6B5  E8 AC FC        call 0xb364
B6B8  FF 4E FA        dec word ptr [bp - 6]
B6BB  EB 9B           jmp 0xb658
loc_B6BD:
B6BD  80 7E FF 01     cmp byte ptr [bp - 1], 1
B6C1  74 03           je 0xb6c6
B6C3  E9 5E FF        jmp 0xb624
loc_B6C6:
B6C6  89 EC           mov sp, bp
B6C8  5D              pop bp
B6C9  CA 04 00        retf 4

; ---- routine 0791:B6CC  (found by: call, far)
sub_B6CC:
B6CC  55              push bp
B6CD  89 E5           mov bp, sp
B6CF  83 EC 06        sub sp, 6
B6D2  8B 46 08        mov ax, word ptr [bp + 8]
B6D5  BA 03 00        mov dx, 3
B6D8  F7 E2           mul dx
B6DA  C4 3E 1F A9     les di, ptr [0xa91f]
B6DE  03 F8           add di, ax
B6E0  89 7E FA        mov word ptr [bp - 6], di
B6E3  8C 46 FC        mov word ptr [bp - 4], es
B6E6  C4 7E FA        les di, ptr [bp - 6]
B6E9  26 8A 45 02     mov al, byte ptr es:[di + 2]
B6ED  98              cwde
B6EE  03 46 06        add ax, word ptr [bp + 6]
B6F1  89 46 FE        mov word ptr [bp - 2], ax
B6F4  83 7E FE 81     cmp word ptr [bp - 2], -0x7f
B6F8  7D 07           jge 0xb701
B6FA  C7 46 FE 81 FF  mov word ptr [bp - 2], 0xff81
B6FF  EB 0B           jmp 0xb70c
loc_B701:
B701  83 7E FE 7F     cmp word ptr [bp - 2], 0x7f
B705  7E 05           jle 0xb70c
B707  C7 46 FE 7F 00  mov word ptr [bp - 2], 0x7f
loc_B70C:
B70C  8A 46 FE        mov al, byte ptr [bp - 2]
B70F  C4 7E FA        les di, ptr [bp - 6]
B712  26 88 45 02     mov byte ptr es:[di + 2], al
B716  89 EC           mov sp, bp
B718  5D              pop bp
B719  CA 04 00        retf 4

; ---- routine 0791:B71C  (found by: call, far)
sub_B71C:
B71C  55              push bp
B71D  89 E5           mov bp, sp
B71F  83 EC 08        sub sp, 8
B722  C4 7E 08        les di, ptr [bp + 8]
B725  89 7E F8        mov word ptr [bp - 8], di
B728  8C 46 FA        mov word ptr [bp - 6], es
B72B  8A 46 06        mov al, byte ptr [bp + 6]
B72E  98              cwde
B72F  D1 E0           shl ax, 1
B731  C4 7E F8        les di, ptr [bp - 8]
B734  03 F8           add di, ax
B736  26 FF 75 04     push word ptr es:[di + 4]
B73A  9A E7 10 71 17  call far 1771:10E7
B73F  50              push ax
B740  80 7E 06 00     cmp byte ptr [bp + 6], 0
B744  74 04           je 0xb74a
B746  B0 00           mov al, 0
B748  EB 02           jmp 0xb74c
loc_B74A:
B74A  B0 01           mov al, 1
loc_B74C:
B74C  98              cwde
B74D  D1 E0           shl ax, 1
B74F  C4 7E F8        les di, ptr [bp - 8]
B752  03 F8           add di, ax
B754  26 FF 75 04     push word ptr es:[di + 4]
B758  9A E7 10 71 17  call far 1771:10E7
B75D  5A              pop dx
B75E  2B C2           sub ax, dx
B760  99              cdq
B761  B9 20 00        mov cx, 0x20
B764  F7 F9           idiv cx
B766  89 46 FC        mov word ptr [bp - 4], ax
B769  C4 7E F8        les di, ptr [bp - 8]
B76C  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
B771  74 34           je 0xb7a7
B773  C4 7E F8        les di, ptr [bp - 8]
B776  26 8A 45 03     mov al, byte ptr es:[di + 3]
B77A  3A 46 06        cmp al, byte ptr [bp + 6]
B77D  75 0F           jne 0xb78e
B77F  C4 7E 08        les di, ptr [bp + 8]
B782  06              push es
B783  57              push di
B784  9A 60 5C 71 17  call far 1771:5C60
B789  01 46 FC        add word ptr [bp - 4], ax
B78C  EB 19           jmp 0xb7a7
loc_B78E:
B78E  C4 7E 08        les di, ptr [bp + 8]
B791  06              push es
B792  57              push di
B793  9A 60 5C 71 17  call far 1771:5C60
B798  31 D2           xor dx, dx
B79A  F7 D0           not ax
B79C  F7 D2           not dx
B79E  05 01 00        add ax, 1
B7A1  83 D2 00        adc dx, 0
B7A4  01 46 FC        add word ptr [bp - 4], ax
loc_B7A7:
B7A7  C4 7E F8        les di, ptr [bp - 8]
B7AA  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
B7AF  74 3A           je 0xb7eb
B7B1  80 7E 06 00     cmp byte ptr [bp + 6], 0
B7B5  74 12           je 0xb7c9
B7B7  C4 7E 08        les di, ptr [bp + 8]
B7BA  06              push es
B7BB  57              push di
B7BC  9A 03 5A 71 17  call far 1771:5A03
B7C1  08 C0           or al, al
B7C3  75 04           jne 0xb7c9
B7C5  B0 00           mov al, 0
B7C7  EB 02           jmp 0xb7cb
loc_B7C9:
B7C9  B0 01           mov al, 1
loc_B7CB:
B7CB  8A D0           mov dl, al
B7CD  C4 7E F8        les di, ptr [bp - 8]
B7D0  26 8A 45 03     mov al, byte ptr es:[di + 3]
B7D4  3A 46 06        cmp al, byte ptr [bp + 6]
B7D7  74 04           je 0xb7dd
B7D9  B0 00           mov al, 0
B7DB  EB 02           jmp 0xb7df
loc_B7DD:
B7DD  B0 01           mov al, 1
loc_B7DF:
B7DF  3A C2           cmp al, dl
B7E1  75 08           jne 0xb7eb
B7E3  8B 46 FC        mov ax, word ptr [bp - 4]
B7E6  D1 E0           shl ax, 1
B7E8  89 46 FC        mov word ptr [bp - 4], ax
loc_B7EB:
B7EB  8B 46 FC        mov ax, word ptr [bp - 4]
B7EE  89 46 FE        mov word ptr [bp - 2], ax
B7F1  8B 46 FE        mov ax, word ptr [bp - 2]
B7F4  89 EC           mov sp, bp
B7F6  5D              pop bp
B7F7  CA 06 00        retf 6

