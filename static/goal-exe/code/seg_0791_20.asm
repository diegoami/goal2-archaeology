; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 20 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:C24D  (found by: call)
sub_C24D:
C24D  55              push bp
C24E  89 E5           mov bp, sp
C250  83 EC 02        sub sp, 2
C253  C7 46 FE 02 00  mov word ptr [bp - 2], 2
C258  EB 03           jmp 0xc25d
loc_C25A:
C25A  FF 46 FE        inc word ptr [bp - 2]
loc_C25D:
C25D  8B 46 FE        mov ax, word ptr [bp - 2]
C260  D1 E0           shl ax, 1
C262  8B 7E 04        mov di, word ptr [bp + 4]
C265  36 C4 7D 06     les di, ptr ss:[di + 6]
C269  03 F8           add di, ax
C26B  26 FF 75 FE     push word ptr es:[di - 2]
C26F  9A 16 32 71 17  call far 1771:3216
C274  08 C0           or al, al
C276  75 24           jne 0xc29c
C278  8B 46 FE        mov ax, word ptr [bp - 2]
C27B  D1 E0           shl ax, 1
C27D  8B 7E 04        mov di, word ptr [bp + 4]
C280  36 C4 7D 06     les di, ptr ss:[di + 6]
C284  03 F8           add di, ax
C286  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C28A  BA 14 00        mov dx, 0x14
C28D  F7 E2           mul dx
C28F  C4 3E 1B A9     les di, ptr [0xa91b]
C293  03 F8           add di, ax
C295  26 C6 45 06 00  mov byte ptr es:[di + 6], 0
C29A  EB 06           jmp 0xc2a2
loc_C29C:
C29C  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
C2A0  75 B8           jne 0xc25a
loc_C2A2:
C2A2  89 EC           mov sp, bp
C2A4  5D              pop bp
C2A5  C2 02 00        ret 2

; ---- routine 0791:C2A8  (found by: call)
sub_C2A8:
C2A8  55              push bp
C2A9  89 E5           mov bp, sp
C2AB  83 EC 12        sub sp, 0x12
C2AE  8D 7E EE        lea di, [bp - 0x12]
C2B1  16              push ss
C2B2  57              push di
C2B3  B8 0E 00        mov ax, 0xe
C2B6  50              push ax
C2B7  31 C0           xor ax, ax
C2B9  50              push ax
C2BA  9A 18 00 4B 21  call far 214B:0018
C2BF  C7 46 FE 01 00  mov word ptr [bp - 2], 1
C2C4  EB 03           jmp 0xc2c9
loc_C2C6:
C2C6  FF 46 FE        inc word ptr [bp - 2]
loc_C2C9:
C2C9  8B 46 FE        mov ax, word ptr [bp - 2]
C2CC  D1 E0           shl ax, 1
C2CE  8B 7E 04        mov di, word ptr [bp + 4]
C2D1  36 C4 7D 06     les di, ptr ss:[di + 6]
C2D5  03 F8           add di, ax
C2D7  26 FF 75 FE     push word ptr es:[di - 2]
C2DB  9A 16 32 71 17  call far 1771:3216
C2E0  08 C0           or al, al
C2E2  75 28           jne 0xc30c
C2E4  8B 46 FE        mov ax, word ptr [bp - 2]
C2E7  D1 E0           shl ax, 1
C2E9  8B 7E 04        mov di, word ptr [bp + 4]
C2EC  36 C4 7D 06     les di, ptr ss:[di + 6]
C2F0  03 F8           add di, ax
C2F2  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C2F6  BA 14 00        mov dx, 0x14
C2F9  F7 E2           mul dx
C2FB  C4 3E 1B A9     les di, ptr [0xa91b]
C2FF  03 F8           add di, ax
C301  26 8A 45 06     mov al, byte ptr es:[di + 6]
C305  30 E4           xor ah, ah
C307  8B F8           mov di, ax
C309  FE 43 EE        inc byte ptr [bp + di - 0x12]
loc_C30C:
C30C  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
C310  75 B4           jne 0xc2c6
C312  31 C0           xor ax, ax
C314  89 46 FC        mov word ptr [bp - 4], ax
C317  83 7E 06 02     cmp word ptr [bp + 6], 2
C31B  74 04           je 0xc321
C31D  B0 00           mov al, 0
C31F  EB 02           jmp 0xc323
loc_C321:
C321  B0 01           mov al, 1
loc_C323:
C323  30 E4           xor ah, ah
C325  40              inc ax
C326  3D 05 00        cmp ax, 5
C329  77 36           ja 0xc361
C32B  89 46 FE        mov word ptr [bp - 2], ax
C32E  EB 03           jmp 0xc333
loc_C330:
C330  FF 46 FE        inc word ptr [bp - 2]
loc_C333:
C333  8B 7E FE        mov di, word ptr [bp - 2]
C336  8A 85 29 0A     mov al, byte ptr [di + 0xa29]
C33A  30 E4           xor ah, ah
C33C  8B F8           mov di, ax
C33E  8A 43 EE        mov al, byte ptr [bp + di - 0x12]
C341  8B 7E FE        mov di, word ptr [bp - 2]
C344  3A 85 2E 0A     cmp al, byte ptr [di + 0xa2e]
C348  76 11           jbe 0xc35b
C34A  8B 7E FE        mov di, word ptr [bp - 2]
C34D  8A 85 29 0A     mov al, byte ptr [di + 0xa29]
C351  30 E4           xor ah, ah
C353  89 46 FC        mov word ptr [bp - 4], ax
C356  C7 46 FE 05 00  mov word ptr [bp - 2], 5
loc_C35B:
C35B  83 7E FE 05     cmp word ptr [bp - 2], 5
C35F  75 CF           jne 0xc330
loc_C361:
C361  83 7E FC 00     cmp word ptr [bp - 4], 0
C365  74 79           je 0xc3e0
C367  C7 46 FE 01 00  mov word ptr [bp - 2], 1
C36C  EB 03           jmp 0xc371
loc_C36E:
C36E  FF 46 FE        inc word ptr [bp - 2]
loc_C371:
C371  8B 46 FE        mov ax, word ptr [bp - 2]
C374  D1 E0           shl ax, 1
C376  8B 7E 04        mov di, word ptr [bp + 4]
C379  36 C4 7D 06     les di, ptr ss:[di + 6]
C37D  03 F8           add di, ax
C37F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C383  BA 14 00        mov dx, 0x14
C386  F7 E2           mul dx
C388  C4 3E 1B A9     les di, ptr [0xa91b]
C38C  03 F8           add di, ax
C38E  26 8A 45 06     mov al, byte ptr es:[di + 6]
C392  30 E4           xor ah, ah
C394  3B 46 FC        cmp ax, word ptr [bp - 4]
C397  75 41           jne 0xc3da
C399  8B 46 FE        mov ax, word ptr [bp - 2]
C39C  D1 E0           shl ax, 1
C39E  8B 7E 04        mov di, word ptr [bp + 4]
C3A1  36 C4 7D 06     les di, ptr ss:[di + 6]
C3A5  03 F8           add di, ax
C3A7  26 FF 75 FE     push word ptr es:[di - 2]
C3AB  9A 16 32 71 17  call far 1771:3216
C3B0  08 C0           or al, al
C3B2  75 26           jne 0xc3da
C3B4  8A 4E 06        mov cl, byte ptr [bp + 6]
C3B7  8B 46 FE        mov ax, word ptr [bp - 2]
C3BA  D1 E0           shl ax, 1
C3BC  8B 7E 04        mov di, word ptr [bp + 4]
C3BF  36 C4 7D 06     les di, ptr ss:[di + 6]
C3C3  03 F8           add di, ax
C3C5  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C3C9  BA 14 00        mov dx, 0x14
C3CC  F7 E2           mul dx
C3CE  C4 3E 1B A9     les di, ptr [0xa91b]
C3D2  03 F8           add di, ax
C3D4  26 88 4D 06     mov byte ptr es:[di + 6], cl
C3D8  EB 06           jmp 0xc3e0
loc_C3DA:
C3DA  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
C3DE  75 8E           jne 0xc36e
loc_C3E0:
C3E0  89 EC           mov sp, bp
C3E2  5D              pop bp
C3E3  C2 04 00        ret 4
; data (not reached as code), 32 bytes
C3E6                  db 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
C3F6                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:C406  (found by: call)
sub_C406:
C406  55              push bp
C407  89 E5           mov bp, sp
C409  83 EC 02        sub sp, 2
C40C  C7 46 FE 01 00  mov word ptr [bp - 2], 1
C411  EB 03           jmp 0xc416
loc_C413:
C413  FF 46 FE        inc word ptr [bp - 2]
loc_C416:
C416  8B 46 FE        mov ax, word ptr [bp - 2]
C419  D1 E0           shl ax, 1
C41B  8B 7E 04        mov di, word ptr [bp + 4]
C41E  36 C4 7D 06     les di, ptr ss:[di + 6]
C422  03 F8           add di, ax
C424  26 FF 75 FE     push word ptr es:[di - 2]
C428  9A 16 32 71 17  call far 1771:3216
C42D  08 C0           or al, al
C42F  75 50           jne 0xc481
C431  8B 46 FE        mov ax, word ptr [bp - 2]
C434  D1 E0           shl ax, 1
C436  8B 7E 04        mov di, word ptr [bp + 4]
C439  36 C4 7D 06     les di, ptr ss:[di + 6]
C43D  03 F8           add di, ax
C43F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C443  BA 14 00        mov dx, 0x14
C446  F7 E2           mul dx
C448  C4 3E 1B A9     les di, ptr [0xa91b]
C44C  03 F8           add di, ax
C44E  26 8A 45 06     mov al, byte ptr es:[di + 6]
C452  50              push ax
C453  BF E6 C3        mov di, 0xc3e6
C456  0E              push cs
C457  57              push di
C458  9A DF 08 E4 23  call far 23E4:08DF
C45D  74 22           je 0xc481
C45F  8B 46 FE        mov ax, word ptr [bp - 2]
C462  D1 E0           shl ax, 1
C464  8B 7E 04        mov di, word ptr [bp + 4]
C467  36 C4 7D 06     les di, ptr ss:[di + 6]
C46B  03 F8           add di, ax
C46D  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C471  BA 14 00        mov dx, 0x14
C474  F7 E2           mul dx
C476  C4 3E 1B A9     les di, ptr [0xa91b]
C47A  03 F8           add di, ax
C47C  26 C6 45 06 02  mov byte ptr es:[di + 6], 2
loc_C481:
C481  83 7E FE 0B     cmp word ptr [bp - 2], 0xb
C485  75 8C           jne 0xc413
C487  89 EC           mov sp, bp
C489  5D              pop bp
C48A  C2 02 00        ret 2

; ---- routine 0791:C48D  (found by: call)
sub_C48D:
C48D  55              push bp
C48E  89 E5           mov bp, sp
C490  8B 46 04        mov ax, word ptr [bp + 4]
C493  BA 16 00        mov dx, 0x16
C496  F7 E2           mul dx
C498  8B F8           mov di, ax
C49A  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
C49E  BA 14 00        mov dx, 0x14
C4A1  F7 E2           mul dx
C4A3  C4 3E 1B A9     les di, ptr [0xa91b]
C4A7  03 F8           add di, ax
C4A9  26 8A 45 06     mov al, byte ptr es:[di + 6]
C4AD  3C 00           cmp al, 0
C4AF  75 06           jne 0xc4b7
C4B1  55              push bp
C4B2  E8 98 FD        call 0xc24d
C4B5  EB 4C           jmp 0xc503
loc_C4B7:
C4B7  3C 01           cmp al, 1
C4B9  74 04           je 0xc4bf
C4BB  3C 02           cmp al, 2
C4BD  75 26           jne 0xc4e5
loc_C4BF:
C4BF  8B 46 04        mov ax, word ptr [bp + 4]
C4C2  BA 16 00        mov dx, 0x16
C4C5  F7 E2           mul dx
C4C7  8B F8           mov di, ax
C4C9  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
C4CD  BA 14 00        mov dx, 0x14
C4D0  F7 E2           mul dx
C4D2  C4 3E 1B A9     les di, ptr [0xa91b]
C4D6  03 F8           add di, ax
C4D8  26 8A 45 06     mov al, byte ptr es:[di + 6]
C4DC  30 E4           xor ah, ah
C4DE  50              push ax
C4DF  55              push bp
C4E0  E8 C5 FD        call 0xc2a8
C4E3  EB 1E           jmp 0xc503
loc_C4E5:
C4E5  3C 03           cmp al, 3
C4E7  74 04           je 0xc4ed
C4E9  3C 04           cmp al, 4
C4EB  75 06           jne 0xc4f3
loc_C4ED:
C4ED  55              push bp
C4EE  E8 15 FF        call 0xc406
C4F1  EB 10           jmp 0xc503
loc_C4F3:
C4F3  3C 0D           cmp al, 0xd
C4F5  74 04           je 0xc4fb
C4F7  3C 0C           cmp al, 0xc
C4F9  75 08           jne 0xc503
loc_C4FB:
C4FB  C4 7E 06        les di, ptr [bp + 6]
C4FE  06              push es
C4FF  57              push di
C500  E8 C4 F9        call 0xbec7
loc_C503:
C503  E8 06 5E        call 0x1230c
C506  89 EC           mov sp, bp
C508  5D              pop bp
C509  C2 06 00        ret 6

; ---- routine 0791:C50C  (found by: call)
sub_C50C:
C50C  55              push bp
C50D  89 E5           mov bp, sp
C50F  9A 25 06 4B 21  call far 214B:0625
C514  BF 8C 5F        mov di, 0x5f8c
C517  1E              push ds
C518  57              push di
C519  BF 6E A9        mov di, 0xa96e
C51C  1E              push ds
C51D  57              push di
C51E  9A 29 03 4B 21  call far 214B:0329
C523  FF 76 06        push word ptr [bp + 6]
C526  8B 46 06        mov ax, word ptr [bp + 6]
C529  BA 14 00        mov dx, 0x14
C52C  F7 E2           mul dx
C52E  C4 3E 1B A9     les di, ptr [0xa91b]
C532  03 F8           add di, ax
C534  26 8A 45 06     mov al, byte ptr es:[di + 6]
C538  30 E4           xor ah, ah
C53A  50              push ax
C53B  9A 20 2E 71 17  call far 1771:2E20
C540  50              push ax
C541  8B 46 06        mov ax, word ptr [bp + 6]
C544  BA 0B 00        mov dx, 0xb
C547  F7 E2           mul dx
C549  C4 3E 6C 9B     les di, ptr [0x9b6c]
C54D  03 F8           add di, ax
C54F  06              push es
C550  57              push di
C551  B0 19           mov al, 0x19
C553  50              push ax
C554  B0 1D           mov al, 0x1d
C556  50              push ax
C557  BF 6E A9        mov di, 0xa96e
C55A  1E              push ds
C55B  57              push di
C55C  9A 05 02 4B 21  call far 214B:0205
C561  FF 76 04        push word ptr [bp + 4]
C564  8B 46 04        mov ax, word ptr [bp + 4]
C567  BA 14 00        mov dx, 0x14
C56A  F7 E2           mul dx
C56C  C4 3E 1B A9     les di, ptr [0xa91b]
C570  03 F8           add di, ax
C572  26 8A 45 06     mov al, byte ptr es:[di + 6]
C576  30 E4           xor ah, ah
C578  50              push ax
C579  9A 20 2E 71 17  call far 1771:2E20
C57E  50              push ax
C57F  8B 46 04        mov ax, word ptr [bp + 4]
C582  BA 0B 00        mov dx, 0xb
C585  F7 E2           mul dx
C587  C4 3E 6C 9B     les di, ptr [0x9b6c]
C58B  03 F8           add di, ax
C58D  06              push es
C58E  57              push di
C58F  B0 19           mov al, 0x19
C591  50              push ax
C592  B0 26           mov al, 0x26
C594  50              push ax
C595  BF 6E A9        mov di, 0xa96e
C598  1E              push ds
C599  57              push di
C59A  9A C8 02 4B 21  call far 214B:02C8
C59F  C4 3E 6E A9     les di, ptr [0xa96e]
C5A3  81 C7 00 0F     add di, 0xf00
C5A7  06              push es
C5A8  57              push di
C5A9  C4 3E 6A A9     les di, ptr [0xa96a]
C5AD  81 C7 00 0F     add di, 0xf00
C5B1  06              push es
C5B2  57              push di
C5B3  B8 A0 00        mov ax, 0xa0
C5B6  50              push ax
C5B7  9A 3C 00 4B 21  call far 214B:003C
C5BC  B8 2C 01        mov ax, 0x12c
C5BF  50              push ax
C5C0  E8 6B 06        call 0xcc2e
C5C3  9A 23 07 4B 21  call far 214B:0723
C5C8  08 C0           or al, al
C5CA  74 05           je 0xc5d1
C5CC  9A DD 08 4B 21  call far 214B:08DD
loc_C5D1:
C5D1  9A 43 06 4B 21  call far 214B:0643
C5D6  89 EC           mov sp, bp
C5D8  5D              pop bp
C5D9  C2 04 00        ret 4

; ---- routine 0791:C5DC  (found by: call)
sub_C5DC:
C5DC  55              push bp
C5DD  89 E5           mov bp, sp
C5DF  83 EC 0A        sub sp, 0xa
C5E2  8B 46 06        mov ax, word ptr [bp + 6]
C5E5  BA 16 00        mov dx, 0x16
C5E8  F7 E2           mul dx
C5EA  8B F8           mov di, ax
C5EC  81 C7 E8 80     add di, 0x80e8
C5F0  89 7E F6        mov word ptr [bp - 0xa], di
C5F3  8C 5E F8        mov word ptr [bp - 8], ds
C5F6  B8 03 00        mov ax, 3
C5F9  50              push ax
C5FA  C4 7E F6        les di, ptr [bp - 0xa]
C5FD  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
C601  BA 14 00        mov dx, 0x14
C604  F7 E2           mul dx
C606  C4 3E 1B A9     les di, ptr [0xa91b]
C60A  03 F8           add di, ax
C60C  81 C7 10 00     add di, 0x10
C610  06              push es
C611  57              push di
C612  9A 79 0C 4B 21  call far 214B:0C79
C617  8A 46 08        mov al, byte ptr [bp + 8]
C61A  98              cwde
C61B  8B F8           mov di, ax
C61D  D1 E7           shl di, 1
C61F  FF B5 34 9B     push word ptr [di - 0x64cc]
C623  9A 77 0B 71 17  call far 1771:0B77
C628  88 46 FD        mov byte ptr [bp - 3], al
C62B  80 7E FD 00     cmp byte ptr [bp - 3], 0
C62F  74 03           je 0xc634
C631  E9 89 00        jmp 0xc6bd
loc_C634:
C634  9A 8D 1E 4B 21  call far 214B:1E8D
C639  80 7E 08 00     cmp byte ptr [bp + 8], 0
C63D  74 04           je 0xc643
C63F  B0 00           mov al, 0
C641  EB 02           jmp 0xc645
loc_C643:
C643  B0 01           mov al, 1
loc_C645:
C645  98              cwde
C646  8B F8           mov di, ax
C648  D1 E7           shl di, 1
C64A  FF B5 34 9B     push word ptr [di - 0x64cc]
C64E  9A 77 0B 71 17  call far 1771:0B77
C653  08 C0           or al, al
C655  74 45           je 0xc69c
C657  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
C65C  75 3E           jne 0xc69c
C65E  8A 46 08        mov al, byte ptr [bp + 8]
C661  98              cwde
C662  8B F8           mov di, ax
C664  8A 85 68 06     mov al, byte ptr [di + 0x668]
C668  30 E4           xor ah, ah
C66A  8B D0           mov dx, ax
C66C  8B 46 06        mov ax, word ptr [bp + 6]
C66F  2B C2           sub ax, dx
C671  D1 E0           shl ax, 1
C673  8B C8           mov cx, ax
C675  8A 46 08        mov al, byte ptr [bp + 8]
C678  98              cwde
C679  8B F8           mov di, ax
C67B  D1 E7           shl di, 1
C67D  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
C681  BA BF 00        mov dx, 0xbf
C684  F7 E2           mul dx
C686  C4 3E 17 A9     les di, ptr [0xa917]
C68A  03 F8           add di, ax
C68C  03 F9           add di, cx
C68E  26 FF 75 FE     push word ptr es:[di - 2]
C692  C4 7E F6        les di, ptr [bp - 0xa]
C695  26 FF 75 0D     push word ptr es:[di + 0xd]
C699  E8 70 FE        call 0xc50c
loc_C69C:
C69C  8A 46 08        mov al, byte ptr [bp + 8]
C69F  50              push ax
C6A0  8A 46 08        mov al, byte ptr [bp + 8]
C6A3  98              cwde
C6A4  8B F8           mov di, ax
C6A6  8A 85 68 06     mov al, byte ptr [di + 0x668]
C6AA  30 E4           xor ah, ah
C6AC  8B D0           mov dx, ax
C6AE  8B 46 06        mov ax, word ptr [bp + 6]
C6B1  2B C2           sub ax, dx
C6B3  50              push ax
C6B4  FF 76 04        push word ptr [bp + 4]
C6B7  B0 00           mov al, 0
C6B9  50              push ax
C6BA  E8 F8 57        call 0x11eb5
loc_C6BD:
C6BD  C4 7E F6        les di, ptr [bp - 0xa]
C6C0  26 8B 45 02     mov ax, word ptr es:[di + 2]
C6C4  3B 06 40 06     cmp ax, word ptr [0x640]
C6C8  75 08           jne 0xc6d2
C6CA  A1 44 06        mov ax, word ptr [0x644]
C6CD  89 46 FE        mov word ptr [bp - 2], ax
C6D0  EB 0A           jmp 0xc6dc
loc_C6D2:
C6D2  C4 7E F6        les di, ptr [bp - 0xa]
C6D5  26 8B 45 02     mov ax, word ptr es:[di + 2]
C6D9  89 46 FE        mov word ptr [bp - 2], ax
loc_C6DC:
C6DC  FF 76 06        push word ptr [bp + 6]
C6DF  C4 7E F6        les di, ptr [bp - 0xa]
C6E2  06              push es
C6E3  57              push di
C6E4  0E              push cs
C6E5  E8 FE DB        call 0xa2e6
C6E8  C4 7E F6        les di, ptr [bp - 0xa]
C6EB  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
C6EF  BA 14 00        mov dx, 0x14
C6F2  F7 E2           mul dx
C6F4  C4 3E 1B A9     les di, ptr [0xa91b]
C6F8  03 F8           add di, ax
C6FA  26 C7 45 12 47 27 mov word ptr es:[di + 0x12], 0x2747
C700  80 7E FD 00     cmp byte ptr [bp - 3], 0
C704  75 23           jne 0xc729
C706  C4 7E F6        les di, ptr [bp - 0xa]
C709  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
C70D  BA 14 00        mov dx, 0x14
C710  F7 E2           mul dx
C712  C4 3E 1B A9     les di, ptr [0xa91b]
C716  03 F8           add di, ax
C718  26 C6 45 0F 00  mov byte ptr es:[di + 0xf], 0
C71D  C4 7E F6        les di, ptr [bp - 0xa]
C720  26 FF 75 0D     push word ptr es:[di + 0xd]
C724  9A 31 34 71 17  call far 1771:3431
loc_C729:
C729  8B 46 FE        mov ax, word ptr [bp - 2]
C72C  C4 7E F6        les di, ptr [bp - 0xa]
C72F  26 89 45 02     mov word ptr es:[di + 2], ax
C733  31 C0           xor ax, ax
C735  89 46 FA        mov word ptr [bp - 6], ax
C738  C6 46 FC 00     mov byte ptr [bp - 4], 0
C73C  EB 03           jmp 0xc741
loc_C73E:
C73E  FE 46 FC        inc byte ptr [bp - 4]
loc_C741:
C741  8A 46 FC        mov al, byte ptr [bp - 4]
C744  98              cwde
C745  8B F8           mov di, ax
C747  D1 E7           shl di, 1
C749  FF B5 34 9B     push word ptr [di - 0x64cc]
C74D  9A 77 0B 71 17  call far 1771:0B77
C752  08 C0           or al, al
C754  74 4B           je 0xc7a1
C756  8A 46 FC        mov al, byte ptr [bp - 4]
C759  98              cwde
C75A  BA 0A 00        mov dx, 0xa
C75D  F7 E2           mul dx
C75F  8B F8           mov di, ax
C761  FF B5 78 99     push word ptr [di - 0x6688]
C765  9A 16 32 71 17  call far 1771:3216
C76A  08 C0           or al, al
C76C  74 33           je 0xc7a1
C76E  8A 46 FC        mov al, byte ptr [bp - 4]
C771  98              cwde
C772  8B F8           mov di, ax
C774  C6 43 FA 01     mov byte ptr [bp + di - 6], 1
C778  8A 46 FC        mov al, byte ptr [bp - 4]
C77B  98              cwde
C77C  8B F8           mov di, ax
C77E  D1 E7           shl di, 1
C780  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
C784  BA BF 00        mov dx, 0xbf
C787  F7 E2           mul dx
C789  C4 3E 17 A9     les di, ptr [0xa917]
C78D  03 F8           add di, ax
C78F  26 8B 0D        mov cx, word ptr es:[di]
C792  8A 46 FC        mov al, byte ptr [bp - 4]
C795  98              cwde
C796  BA 0A 00        mov dx, 0xa
C799  F7 E2           mul dx
C79B  8B F8           mov di, ax
C79D  89 8D 78 99     mov word ptr [di - 0x6688], cx
loc_C7A1:
C7A1  80 7E FC 01     cmp byte ptr [bp - 4], 1
C7A5  75 97           jne 0xc73e
C7A7  E8 62 5B        call 0x1230c
C7AA  C6 46 FC 00     mov byte ptr [bp - 4], 0
C7AE  EB 03           jmp 0xc7b3
loc_C7B0:
C7B0  FE 46 FC        inc byte ptr [bp - 4]
loc_C7B3:
C7B3  8A 46 FC        mov al, byte ptr [bp - 4]
C7B6  98              cwde
C7B7  8B F8           mov di, ax
C7B9  80 7B FA 00     cmp byte ptr [bp + di - 6], 0
C7BD  74 11           je 0xc7d0
C7BF  8A 46 FC        mov al, byte ptr [bp - 4]
C7C2  98              cwde
C7C3  BA 0A 00        mov dx, 0xa
C7C6  F7 E2           mul dx
C7C8  8B F8           mov di, ax
C7CA  31 C0           xor ax, ax
C7CC  89 85 78 99     mov word ptr [di - 0x6688], ax
loc_C7D0:
C7D0  80 7E FC 01     cmp byte ptr [bp - 4], 1
C7D4  75 DA           jne 0xc7b0
C7D6  8A 46 08        mov al, byte ptr [bp + 8]
C7D9  98              cwde
C7DA  8B F8           mov di, ax
C7DC  FE 8D 3A 9B     dec byte ptr [di - 0x64c6]
C7E0  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
C7E5  89 EC           mov sp, bp
C7E7  5D              pop bp
C7E8  C2 06 00        ret 6

; ---- routine 0791:C7EB  (found by: call)
sub_C7EB:
C7EB  55              push bp
C7EC  89 E5           mov bp, sp
C7EE  83 EC 02        sub sp, 2
C7F1  C7 46 FE 0C 00  mov word ptr [bp - 2], 0xc
C7F6  EB 03           jmp 0xc7fb
loc_C7F8:
C7F8  FF 46 FE        inc word ptr [bp - 2]
loc_C7FB:
C7FB  8B 7E 04        mov di, word ptr [bp + 4]
C7FE  36 8A 45 06     mov al, byte ptr ss:[di + 6]
C802  98              cwde
C803  8B F8           mov di, ax
C805  8A 85 68 06     mov al, byte ptr [di + 0x668]
C809  30 E4           xor ah, ah
C80B  8B D0           mov dx, ax
C80D  8B 7E 04        mov di, word ptr [bp + 4]
C810  36 8B 45 08     mov ax, word ptr ss:[di + 8]
C814  2B C2           sub ax, dx
C816  BA 16 00        mov dx, 0x16
C819  F7 E2           mul dx
C81B  8B F8           mov di, ax
C81D  8B 95 F5 80     mov dx, word ptr [di - 0x7f0b]
C821  8B 46 FE        mov ax, word ptr [bp - 2]
C824  D1 E0           shl ax, 1
C826  8B 7E 04        mov di, word ptr [bp + 4]
C829  36 C4 7D 0A     les di, ptr ss:[di + 0xa]
C82D  03 F8           add di, ax
C82F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C833  3B C2           cmp ax, dx
C835  74 47           je 0xc87e
C837  8B 46 FE        mov ax, word ptr [bp - 2]
C83A  D1 E0           shl ax, 1
C83C  8B 7E 04        mov di, word ptr [bp + 4]
C83F  36 C4 7D 0A     les di, ptr ss:[di + 0xa]
C843  03 F8           add di, ax
C845  26 FF 75 FE     push word ptr es:[di - 2]
C849  9A 16 32 71 17  call far 1771:3216
C84E  08 C0           or al, al
C850  75 2C           jne 0xc87e
C852  8A 4E FE        mov cl, byte ptr [bp - 2]
C855  8B 46 FE        mov ax, word ptr [bp - 2]
C858  D1 E0           shl ax, 1
C85A  8B 7E 04        mov di, word ptr [bp + 4]
C85D  36 C4 7D 0A     les di, ptr ss:[di + 0xa]
C861  03 F8           add di, ax
C863  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C867  BA 14 00        mov dx, 0x14
C86A  F7 E2           mul dx
C86C  C4 3E 1B A9     les di, ptr [0xa91b]
C870  03 F8           add di, ax
C872  26 8A 45 07     mov al, byte ptr es:[di + 7]
C876  30 E4           xor ah, ah
C878  8B F8           mov di, ax
C87A  88 8D A2 99     mov byte ptr [di - 0x665e], cl
loc_C87E:
C87E  83 7E FE 14     cmp word ptr [bp - 2], 0x14
C882  74 03           je 0xc887
C884  E9 71 FF        jmp 0xc7f8
loc_C887:
C887  89 EC           mov sp, bp
C889  5D              pop bp
C88A  C2 02 00        ret 2

; ---- routine 0791:C88D  (found by: call)
sub_C88D:
C88D  55              push bp
C88E  89 E5           mov bp, sp
C890  83 EC 06        sub sp, 6
C893  8A 46 06        mov al, byte ptr [bp + 6]
C896  98              cwde
C897  8B F8           mov di, ax
C899  80 BD 3A 9B 00  cmp byte ptr [di - 0x64c6], 0
C89E  75 3E           jne 0xc8de
C8A0  8A 46 06        mov al, byte ptr [bp + 6]
C8A3  98              cwde
C8A4  8B F8           mov di, ax
C8A6  8A 85 68 06     mov al, byte ptr [di + 0x668]
C8AA  30 E4           xor ah, ah
C8AC  8B D0           mov dx, ax
C8AE  8B 46 08        mov ax, word ptr [bp + 8]
C8B1  2B C2           sub ax, dx
C8B3  D1 E0           shl ax, 1
C8B5  C4 7E 0A        les di, ptr [bp + 0xa]
C8B8  03 F8           add di, ax
C8BA  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C8BE  BA 14 00        mov dx, 0x14
C8C1  F7 E2           mul dx
C8C3  C4 3E 1B A9     les di, ptr [0xa91b]
C8C7  03 F8           add di, ax
C8C9  26 80 7D 0E 01  cmp byte ptr es:[di + 0xe], 1
C8CE  7D 0E           jge 0xc8de
C8D0  C4 7E 0A        les di, ptr [bp + 0xa]
C8D3  06              push es
C8D4  57              push di
C8D5  FF 76 08        push word ptr [bp + 8]
C8D8  E8 B2 FB        call 0xc48d
C8DB  E9 CC 01        jmp 0xcaaa
loc_C8DE:
C8DE  BF A2 99        mov di, 0x99a2
C8E1  1E              push ds
C8E2  57              push di
C8E3  B8 0E 00        mov ax, 0xe
C8E6  50              push ax
C8E7  31 C0           xor ax, ax
C8E9  50              push ax
C8EA  9A 18 00 4B 21  call far 214B:0018
C8EF  55              push bp
C8F0  E8 F8 FE        call 0xc7eb
C8F3  8B 46 08        mov ax, word ptr [bp + 8]
C8F6  BA 16 00        mov dx, 0x16
C8F9  F7 E2           mul dx
C8FB  8B F8           mov di, ax
C8FD  FF B5 F5 80     push word ptr [di - 0x7f0b]
C901  C4 7E 0A        les di, ptr [bp + 0xa]
C904  06              push es
C905  57              push di
C906  E8 DF E1        call 0xaae8
C909  89 46 FE        mov word ptr [bp - 2], ax
C90C  83 7E FE 00     cmp word ptr [bp - 2], 0
C910  75 5C           jne 0xc96e
C912  80 7E 04 00     cmp byte ptr [bp + 4], 0
C916  75 20           jne 0xc938
C918  8B 46 08        mov ax, word ptr [bp + 8]
C91B  BA 16 00        mov dx, 0x16
C91E  F7 E2           mul dx
C920  8B F8           mov di, ax
C922  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
C926  BA 14 00        mov dx, 0x14
C929  F7 E2           mul dx
C92B  C4 3E 1B A9     les di, ptr [0xa91b]
C92F  03 F8           add di, ax
C931  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
C936  75 36           jne 0xc96e
loc_C938:
C938  8A 46 06        mov al, byte ptr [bp + 6]
C93B  98              cwde
C93C  8B F8           mov di, ax
C93E  D1 E7           shl di, 1
C940  FF B5 34 9B     push word ptr [di - 0x64cc]
C944  8B 46 08        mov ax, word ptr [bp + 8]
C947  BA 16 00        mov dx, 0x16
C94A  F7 E2           mul dx
C94C  8B F8           mov di, ax
C94E  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
C952  BA 14 00        mov dx, 0x14
C955  F7 E2           mul dx
C957  C4 3E 1B A9     les di, ptr [0xa91b]
C95B  03 F8           add di, ax
C95D  26 8A 45 06     mov al, byte ptr es:[di + 6]
C961  30 E4           xor ah, ah
C963  50              push ax
C964  B8 14 00        mov ax, 0x14
C967  50              push ax
C968  E8 4D E0        call 0xa9b8
C96B  89 46 FE        mov word ptr [bp - 2], ax
loc_C96E:
C96E  83 7E FE 00     cmp word ptr [bp - 2], 0
C972  75 03           jne 0xc977
C974  E9 33 01        jmp 0xcaaa
loc_C977:
C977  8A 46 06        mov al, byte ptr [bp + 6]
C97A  98              cwde
C97B  8B F8           mov di, ax
C97D  D1 E7           shl di, 1
C97F  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
C983  BA BF 00        mov dx, 0xbf
C986  F7 E2           mul dx
C988  C4 3E 17 A9     les di, ptr [0xa917]
C98C  03 F8           add di, ax
C98E  89 7E FA        mov word ptr [bp - 6], di
C991  8C 46 FC        mov word ptr [bp - 4], es
C994  8B 46 08        mov ax, word ptr [bp + 8]
C997  BA 16 00        mov dx, 0x16
C99A  F7 E2           mul dx
C99C  8B F8           mov di, ax
C99E  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
C9A2  BA 14 00        mov dx, 0x14
C9A5  F7 E2           mul dx
C9A7  C4 3E 1B A9     les di, ptr [0xa91b]
C9AB  03 F8           add di, ax
C9AD  26 8A 4D 06     mov cl, byte ptr es:[di + 6]
C9B1  8B 46 FE        mov ax, word ptr [bp - 2]
C9B4  D1 E0           shl ax, 1
C9B6  C4 7E FA        les di, ptr [bp - 6]
C9B9  03 F8           add di, ax
C9BB  26 8B 45 FE     mov ax, word ptr es:[di - 2]
C9BF  BA 14 00        mov dx, 0x14
C9C2  F7 E2           mul dx
C9C4  C4 3E 1B A9     les di, ptr [0xa91b]
C9C8  03 F8           add di, ax
C9CA  26 88 4D 06     mov byte ptr es:[di + 6], cl
C9CE  8B 46 FE        mov ax, word ptr [bp - 2]
C9D1  D1 E0           shl ax, 1
C9D3  C4 7E FA        les di, ptr [bp - 6]
C9D6  03 F8           add di, ax
C9D8  81 C7 FE FF     add di, 0xfffe
C9DC  06              push es
C9DD  57              push di
C9DE  8A 46 06        mov al, byte ptr [bp + 6]
C9E1  98              cwde
C9E2  8B F8           mov di, ax
C9E4  8A 85 68 06     mov al, byte ptr [di + 0x668]
C9E8  30 E4           xor ah, ah
C9EA  8B D0           mov dx, ax
C9EC  8B 46 08        mov ax, word ptr [bp + 8]
C9EF  2B C2           sub ax, dx
C9F1  D1 E0           shl ax, 1
C9F3  C4 7E FA        les di, ptr [bp - 6]
C9F6  03 F8           add di, ax
C9F8  81 C7 FE FF     add di, 0xfffe
C9FC  06              push es
C9FD  57              push di
C9FE  B8 02 00        mov ax, 2
CA01  50              push ax
CA02  9A 7B 00 4B 21  call far 214B:007B
CA07  8B 46 FE        mov ax, word ptr [bp - 2]
CA0A  D1 E0           shl ax, 1
CA0C  8B C8           mov cx, ax
CA0E  8A 46 06        mov al, byte ptr [bp + 6]
CA11  98              cwde
CA12  BA 28 00        mov dx, 0x28
CA15  F7 E2           mul dx
CA17  8B F8           mov di, ax
CA19  03 F9           add di, cx
CA1B  81 C7 3E 9A     add di, 0x9a3e
CA1F  1E              push ds
CA20  57              push di
CA21  8A 46 06        mov al, byte ptr [bp + 6]
CA24  98              cwde
CA25  8B F8           mov di, ax
CA27  8A 85 68 06     mov al, byte ptr [di + 0x668]
CA2B  30 E4           xor ah, ah
CA2D  8B D0           mov dx, ax
CA2F  8B 46 08        mov ax, word ptr [bp + 8]
CA32  2B C2           sub ax, dx
CA34  D1 E0           shl ax, 1
CA36  8B C8           mov cx, ax
CA38  8A 46 06        mov al, byte ptr [bp + 6]
CA3B  98              cwde
CA3C  BA 28 00        mov dx, 0x28
CA3F  F7 E2           mul dx
CA41  8B F8           mov di, ax
CA43  03 F9           add di, cx
CA45  81 C7 3E 9A     add di, 0x9a3e
CA49  1E              push ds
CA4A  57              push di
CA4B  B8 02 00        mov ax, 2
CA4E  50              push ax
CA4F  9A 7B 00 4B 21  call far 214B:007B
CA54  8B 46 FE        mov ax, word ptr [bp - 2]
CA57  8B C8           mov cx, ax
CA59  8A 46 06        mov al, byte ptr [bp + 6]
CA5C  98              cwde
CA5D  BA 14 00        mov dx, 0x14
CA60  F7 E2           mul dx
CA62  8B F8           mov di, ax
CA64  03 F9           add di, cx
CA66  81 C7 07 9B     add di, 0x9b07
CA6A  1E              push ds
CA6B  57              push di
CA6C  8A 46 06        mov al, byte ptr [bp + 6]
CA6F  98              cwde
CA70  8B F8           mov di, ax
CA72  8A 85 68 06     mov al, byte ptr [di + 0x668]
CA76  30 E4           xor ah, ah
CA78  8B D0           mov dx, ax
CA7A  8B 46 08        mov ax, word ptr [bp + 8]
CA7D  2B C2           sub ax, dx
CA7F  8B C8           mov cx, ax
CA81  8A 46 06        mov al, byte ptr [bp + 6]
CA84  98              cwde
CA85  BA 14 00        mov dx, 0x14
CA88  F7 E2           mul dx
CA8A  8B F8           mov di, ax
CA8C  03 F9           add di, cx
CA8E  81 C7 07 9B     add di, 0x9b07
CA92  1E              push ds
CA93  57              push di
CA94  B8 01 00        mov ax, 1
CA97  50              push ax
CA98  9A 7B 00 4B 21  call far 214B:007B
CA9D  8A 46 06        mov al, byte ptr [bp + 6]
CAA0  50              push ax
CAA1  FF 76 08        push word ptr [bp + 8]
CAA4  FF 76 FE        push word ptr [bp - 2]
CAA7  E8 32 FB        call 0xc5dc
loc_CAAA:
CAAA  89 EC           mov sp, bp
CAAC  5D              pop bp
CAAD  C2 0A 00        ret 0xa

; ---- routine 0791:CAB0  (found by: call)
sub_CAB0:
CAB0  55              push bp
CAB1  89 E5           mov bp, sp
CAB3  83 EC 10        sub sp, 0x10
CAB6  C7 46 FB 01 00  mov word ptr [bp - 5], 1
CABB  C6 46 FF 00     mov byte ptr [bp - 1], 0
CABF  EB 03           jmp 0xcac4
loc_CAC1:
CAC1  FE 46 FF        inc byte ptr [bp - 1]
loc_CAC4:
CAC4  8A 46 FF        mov al, byte ptr [bp - 1]
CAC7  98              cwde
CAC8  8B F8           mov di, ax
CACA  D1 E7           shl di, 1
CACC  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
CAD0  BA BF 00        mov dx, 0xbf
CAD3  F7 E2           mul dx
CAD5  C4 3E 17 A9     les di, ptr [0xa917]
CAD9  03 F8           add di, ax
CADB  89 7E F5        mov word ptr [bp - 0xb], di
CADE  8C 46 F7        mov word ptr [bp - 9], es
CAE1  C7 46 FD 01 00  mov word ptr [bp - 3], 1
CAE6  EB 03           jmp 0xcaeb
loc_CAE8:
CAE8  FF 46 FD        inc word ptr [bp - 3]
loc_CAEB:
CAEB  8B 46 FD        mov ax, word ptr [bp - 3]
CAEE  D1 E0           shl ax, 1
CAF0  C4 7E F5        les di, ptr [bp - 0xb]
CAF3  03 F8           add di, ax
CAF5  26 8B 45 FE     mov ax, word ptr es:[di - 2]
CAF9  BA 14 00        mov dx, 0x14
CAFC  F7 E2           mul dx
CAFE  C4 3E 1B A9     les di, ptr [0xa91b]
CB02  03 F8           add di, ax
CB04  89 7E F1        mov word ptr [bp - 0xf], di
CB07  8C 46 F3        mov word ptr [bp - 0xd], es
CB0A  83 7E FD 0C     cmp word ptr [bp - 3], 0xc
CB0E  7C 17           jl 0xcb27
CB10  B8 03 00        mov ax, 3
CB13  50              push ax
CB14  C4 7E F1        les di, ptr [bp - 0xf]
CB17  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
CB1B  30 E4           xor ah, ah
CB1D  50              push ax
CB1E  9A 57 0C 4B 21  call far 214B:0C57
CB23  08 C0           or al, al
CB25  74 40           je 0xcb67
loc_CB27:
CB27  C4 7E F1        les di, ptr [bp - 0xf]
CB2A  26 81 7D 12 FF 7F cmp word ptr es:[di + 0x12], 0x7fff
CB30  74 35           je 0xcb67
CB32  C4 7E F1        les di, ptr [bp - 0xf]
CB35  26 8B 45 12     mov ax, word ptr es:[di + 0x12]
CB39  89 46 F9        mov word ptr [bp - 7], ax
CB3C  81 7E F9 88 13  cmp word ptr [bp - 7], 0x1388
CB41  7E 05           jle 0xcb48
CB43  81 6E F9 10 27  sub word ptr [bp - 7], 0x2710
loc_CB48:
CB48  8B 46 F9        mov ax, word ptr [bp - 7]
CB4B  3B 46 FB        cmp ax, word ptr [bp - 5]
CB4E  7E 17           jle 0xcb67
CB50  8B 46 FD        mov ax, word ptr [bp - 3]
CB53  D1 E0           shl ax, 1
CB55  C4 7E F5        les di, ptr [bp - 0xb]
CB58  03 F8           add di, ax
CB5A  26 8B 45 FE     mov ax, word ptr es:[di - 2]
CB5E  A3 3A 7C        mov word ptr [0x7c3a], ax
CB61  8B 46 F9        mov ax, word ptr [bp - 7]
CB64  89 46 FB        mov word ptr [bp - 5], ax
loc_CB67:
CB67  83 7E FD 14     cmp word ptr [bp - 3], 0x14
CB6B  74 03           je 0xcb70
CB6D  E9 78 FF        jmp 0xcae8
loc_CB70:
CB70  80 7E FF 01     cmp byte ptr [bp - 1], 1
CB74  74 03           je 0xcb79
CB76  E9 48 FF        jmp 0xcac1
loc_CB79:
CB79  89 EC           mov sp, bp
CB7B  5D              pop bp
CB7C  C3              ret

; ---- routine 0791:CB7D  (found by: call)
sub_CB7D:
CB7D  55              push bp
CB7E  89 E5           mov bp, sp
CB80  83 EC 0C        sub sp, 0xc
CB83  C6 46 FF 00     mov byte ptr [bp - 1], 0
CB87  EB 03           jmp 0xcb8c
loc_CB89:
CB89  FE 46 FF        inc byte ptr [bp - 1]
loc_CB8C:
CB8C  C7 46 FD 01 00  mov word ptr [bp - 3], 1
CB91  EB 03           jmp 0xcb96
loc_CB93:
CB93  FF 46 FD        inc word ptr [bp - 3]
loc_CB96:
CB96  8A 46 FF        mov al, byte ptr [bp - 1]
CB99  98              cwde
CB9A  8B F8           mov di, ax
CB9C  D1 E7           shl di, 1
CB9E  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
CBA2  BA BF 00        mov dx, 0xbf
CBA5  F7 E2           mul dx
CBA7  C4 3E 17 A9     les di, ptr [0xa917]
CBAB  03 F8           add di, ax
CBAD  89 7E F9        mov word ptr [bp - 7], di
CBB0  8C 46 FB        mov word ptr [bp - 5], es
CBB3  8B 46 FD        mov ax, word ptr [bp - 3]
CBB6  D1 E0           shl ax, 1
CBB8  C4 7E F9        les di, ptr [bp - 7]
CBBB  03 F8           add di, ax
CBBD  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
CBC2  74 54           je 0xcc18
CBC4  8B 46 FD        mov ax, word ptr [bp - 3]
CBC7  D1 E0           shl ax, 1
CBC9  C4 7E F9        les di, ptr [bp - 7]
CBCC  03 F8           add di, ax
CBCE  26 8B 45 FE     mov ax, word ptr es:[di - 2]
CBD2  BA 14 00        mov dx, 0x14
CBD5  F7 E2           mul dx
CBD7  C4 3E 1B A9     les di, ptr [0xa91b]
CBDB  03 F8           add di, ax
CBDD  89 7E F5        mov word ptr [bp - 0xb], di
CBE0  8C 46 F7        mov word ptr [bp - 9], es
CBE3  8B 46 FD        mov ax, word ptr [bp - 3]
CBE6  8B C8           mov cx, ax
CBE8  8A 46 FF        mov al, byte ptr [bp - 1]
CBEB  98              cwde
CBEC  BA 14 00        mov dx, 0x14
CBEF  F7 E2           mul dx
CBF1  8B F8           mov di, ax
CBF3  03 F9           add di, cx
CBF5  8A 85 07 9B     mov al, byte ptr [di - 0x64f9]
CBF9  C4 7E F5        les di, ptr [bp - 0xb]
CBFC  26 88 45 0C     mov byte ptr es:[di + 0xc], al
CC00  C4 7E F5        les di, ptr [bp - 0xb]
CC03  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
CC08  7E 0E           jle 0xcc18
CC0A  C4 7E F5        les di, ptr [bp - 0xb]
CC0D  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
CC11  C4 7E F5        les di, ptr [bp - 0xb]
CC14  26 88 45 0E     mov byte ptr es:[di + 0xe], al
loc_CC18:
CC18  83 7E FD 14     cmp word ptr [bp - 3], 0x14
CC1C  74 03           je 0xcc21
CC1E  E9 72 FF        jmp 0xcb93
loc_CC21:
CC21  80 7E FF 01     cmp byte ptr [bp - 1], 1
CC25  74 03           je 0xcc2a
CC27  E9 5F FF        jmp 0xcb89
loc_CC2A:
CC2A  89 EC           mov sp, bp
CC2C  5D              pop bp
CC2D  C3              ret

; ---- routine 0791:CC2E  (found by: call)
sub_CC2E:
CC2E  55              push bp
CC2F  89 E5           mov bp, sp
CC31  83 EC 04        sub sp, 4
CC34  9A 8D 1E 4B 21  call far 214B:1E8D
CC39  8B 46 04        mov ax, word ptr [bp + 4]
CC3C  89 46 FC        mov word ptr [bp - 4], ax
CC3F  B8 01 00        mov ax, 1
CC42  3B 46 FC        cmp ax, word ptr [bp - 4]
CC45  77 26           ja 0xcc6d
CC47  89 46 FE        mov word ptr [bp - 2], ax
CC4A  EB 03           jmp 0xcc4f
loc_CC4C:
CC4C  FF 46 FE        inc word ptr [bp - 2]
loc_CC4F:
CC4F  9A 23 07 4B 21  call far 214B:0723
CC54  08 C0           or al, al
CC56  74 04           je 0xcc5c
CC58  EB 13           jmp 0xcc6d
; data (not reached as code), 2 bytes
CC5A                  db EB 09   ; ..
loc_CC5C:
CC5C  B8 0A 00        mov ax, 0xa
CC5F  50              push ax
CC60  9A 09 1E 4B 21  call far 214B:1E09
CC65  8B 46 FE        mov ax, word ptr [bp - 2]
CC68  3B 46 FC        cmp ax, word ptr [bp - 4]
CC6B  75 DF           jne 0xcc4c
loc_CC6D:
CC6D  89 EC           mov sp, bp
CC6F  5D              pop bp
CC70  C2 02 00        ret 2
; data (not reached as code), 8 bytes
CC73                  pstr '       '

; ---- routine 0791:CC7B  (found by: call)
sub_CC7B:
CC7B  55              push bp
CC7C  89 E5           mov bp, sp
CC7E  83 EC 0E        sub sp, 0xe
CC81  8A 46 06        mov al, byte ptr [bp + 6]
CC84  98              cwde
CC85  8B F8           mov di, ax
CC87  D1 E7           shl di, 1
CC89  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
CC8D  BA BF 00        mov dx, 0xbf
CC90  F7 E2           mul dx
CC92  C4 3E 17 A9     les di, ptr [0xa917]
CC96  03 F8           add di, ax
CC98  89 7E F3        mov word ptr [bp - 0xd], di
CC9B  8C 46 F5        mov word ptr [bp - 0xb], es
CC9E  C4 3E 6A A9     les di, ptr [0xa96a]
CCA2  06              push es
CCA3  57              push di
CCA4  C4 3E 72 A9     les di, ptr [0xa972]
CCA8  06              push es
CCA9  57              push di
CCAA  B8 A0 0F        mov ax, 0xfa0
CCAD  50              push ax
CCAE  9A 5D 02 E4 23  call far 23E4:025D
CCB3  31 C0           xor ax, ax
CCB5  89 46 FB        mov word ptr [bp - 5], ax
CCB8  80 7E 04 01     cmp byte ptr [bp + 4], 1
CCBC  75 4B           jne 0xcd09
CCBE  8A 46 04        mov al, byte ptr [bp + 4]
CCC1  30 E4           xor ah, ah
CCC3  D1 E0           shl ax, 1
CCC5  8B C8           mov cx, ax
CCC7  8A 46 06        mov al, byte ptr [bp + 6]
CCCA  98              cwde
CCCB  BA 0A 00        mov dx, 0xa
CCCE  F7 E2           mul dx
CCD0  8B F8           mov di, ax
CCD2  03 F9           add di, cx
CCD4  FF B5 76 99     push word ptr [di - 0x668a]
CCD8  9A 16 32 71 17  call far 1771:3216
CCDD  08 C0           or al, al
CCDF  75 10           jne 0xccf1
CCE1  8A 46 06        mov al, byte ptr [bp + 6]
CCE4  50              push ax
CCE5  B8 01 00        mov ax, 1
CCE8  50              push ax
CCE9  E8 79 9E        call 0x6b65
CCEC  3D 0B 00        cmp ax, 0xb
CCEF  76 18           jbe 0xcd09
loc_CCF1:
CCF1  8A 46 06        mov al, byte ptr [bp + 6]
CCF4  50              push ax
CCF5  E8 44 52        call 0x11f3c
CCF8  8B C8           mov cx, ax
CCFA  8A 46 06        mov al, byte ptr [bp + 6]
CCFD  98              cwde
CCFE  BA 0A 00        mov dx, 0xa
CD01  F7 E2           mul dx
CD03  8B F8           mov di, ax
CD05  89 8D 78 99     mov word ptr [di - 0x6688], cx
loc_CD09:
CD09  8A 46 04        mov al, byte ptr [bp + 4]
CD0C  30 E4           xor ah, ah
CD0E  D1 E0           shl ax, 1
CD10  8B C8           mov cx, ax
CD12  8A 46 06        mov al, byte ptr [bp + 6]
CD15  98              cwde
CD16  BA 0A 00        mov dx, 0xa
CD19  F7 E2           mul dx
CD1B  8B F8           mov di, ax
CD1D  03 F9           add di, cx
CD1F  FF B5 76 99     push word ptr [di - 0x668a]
CD23  9A 16 32 71 17  call far 1771:3216
CD28  08 C0           or al, al
CD2A  75 12           jne 0xcd3e
CD2C  8A 46 06        mov al, byte ptr [bp + 6]
CD2F  50              push ax
CD30  8A 46 04        mov al, byte ptr [bp + 4]
CD33  30 E4           xor ah, ah
CD35  50              push ax
CD36  E8 2C 9E        call 0x6b65
CD39  3D 0B 00        cmp ax, 0xb
CD3C  76 1B           jbe 0xcd59
loc_CD3E:
CD3E  8A 46 06        mov al, byte ptr [bp + 6]
CD41  50              push ax
CD42  8A 46 04        mov al, byte ptr [bp + 4]
CD45  30 E4           xor ah, ah
CD47  8B F8           mov di, ax
CD49  8A 85 64 07     mov al, byte ptr [di + 0x764]
CD4D  30 E4           xor ah, ah
CD4F  50              push ax
CD50  8A 46 04        mov al, byte ptr [bp + 4]
CD53  30 E4           xor ah, ah
CD55  50              push ax
CD56  E8 84 52        call 0x11fdd
loc_CD59:
CD59  C7 46 F7 01 00  mov word ptr [bp - 9], 1
CD5E  EB 03           jmp 0xcd63
loc_CD60:
CD60  FF 46 F7        inc word ptr [bp - 9]
loc_CD63:
CD63  8B 46 F7        mov ax, word ptr [bp - 9]
CD66  D1 E0           shl ax, 1
CD68  C4 7E F3        les di, ptr [bp - 0xd]
CD6B  03 F8           add di, ax
CD6D  26 8B 5D FE     mov bx, word ptr es:[di - 2]
CD71  8A 46 04        mov al, byte ptr [bp + 4]
CD74  30 E4           xor ah, ah
CD76  D1 E0           shl ax, 1
CD78  8B C8           mov cx, ax
CD7A  8A 46 06        mov al, byte ptr [bp + 6]
CD7D  98              cwde
CD7E  BA 0A 00        mov dx, 0xa
CD81  F7 E2           mul dx
CD83  8B F8           mov di, ax
CD85  03 F9           add di, cx
CD87  8B 85 76 99     mov ax, word ptr [di - 0x668a]
CD8B  3B C3           cmp ax, bx
CD8D  75 1D           jne 0xcdac
CD8F  8B 46 F7        mov ax, word ptr [bp - 9]
CD92  D1 E0           shl ax, 1
CD94  C4 7E F3        les di, ptr [bp - 0xd]
CD97  03 F8           add di, ax
CD99  26 FF 75 FE     push word ptr es:[di - 2]
CD9D  9A 16 32 71 17  call far 1771:3216
CDA2  08 C0           or al, al
CDA4  75 06           jne 0xcdac
CDA6  8B 46 F7        mov ax, word ptr [bp - 9]
CDA9  89 46 FB        mov word ptr [bp - 5], ax
loc_CDAC:
CDAC  83 7E F7 0B     cmp word ptr [bp - 9], 0xb
CDB0  75 AE           jne 0xcd60
CDB2  83 7E FB 00     cmp word ptr [bp - 5], 0
CDB6  74 13           je 0xcdcb
CDB8  8B 46 FB        mov ax, word ptr [bp - 5]
CDBB  D1 E0           shl ax, 1
CDBD  C4 7E F3        les di, ptr [bp - 0xd]
CDC0  03 F8           add di, ax
CDC2  26 8B 45 FE     mov ax, word ptr es:[di - 2]
CDC6  89 46 F9        mov word ptr [bp - 7], ax
CDC9  EB 0A           jmp 0xcdd5
loc_CDCB:
CDCB  31 C0           xor ax, ax
CDCD  89 46 F9        mov word ptr [bp - 7], ax
CDD0  C7 46 FB 01 00  mov word ptr [bp - 5], 1
loc_CDD5:
CDD5  C6 06 76 A9 00  mov byte ptr [0xa976], 0
CDDA  BF CC 1E        mov di, 0x1ecc
CDDD  1E              push ds
CDDE  57              push di
CDDF  E8 B7 D8        call 0xa699
CDE2  B8 06 00        mov ax, 6
CDE5  50              push ax
CDE6  9A F0 05 4B 21  call far 214B:05F0
CDEB  BF EC 60        mov di, 0x60ec
CDEE  1E              push ds
CDEF  57              push di
CDF0  BF 6E A9        mov di, 0xa96e
CDF3  1E              push ds
CDF4  57              push di
CDF5  9A 29 03 4B 21  call far 214B:0329
CDFA  80 7E 04 01     cmp byte ptr [bp + 4], 1
CDFE  74 0F           je 0xce0f
CE00  BF D6 60        mov di, 0x60d6
CE03  1E              push ds
CE04  57              push di
CE05  BF 6E A9        mov di, 0xa96e
CE08  1E              push ds
CE09  57              push di
CE0A  9A 29 03 4B 21  call far 214B:0329
loc_CE0F:
CE0F  8A 46 06        mov al, byte ptr [bp + 6]
CE12  98              cwde
CE13  8B F8           mov di, ax
CE15  D1 E7           shl di, 1
CE17  FF B5 34 9B     push word ptr [di - 0x64cc]
CE1B  B8 17 00        mov ax, 0x17
CE1E  50              push ax
CE1F  B8 41 00        mov ax, 0x41
CE22  50              push ax
CE23  9A 58 0F 71 17  call far 1771:0F58
CE28  C7 46 F7 01 00  mov word ptr [bp - 9], 1
CE2D  EB 03           jmp 0xce32
loc_CE2F:
CE2F  FF 46 F7        inc word ptr [bp - 9]
loc_CE32:
CE32  8B 46 F7        mov ax, word ptr [bp - 9]
CE35  D1 E0           shl ax, 1
CE37  C4 7E F3        les di, ptr [bp - 0xd]
CE3A  03 F8           add di, ax
CE3C  26 FF 75 FE     push word ptr es:[di - 2]
CE40  8B 46 F7        mov ax, word ptr [bp - 9]
CE43  05 07 00        add ax, 7
CE46  50              push ax
CE47  B8 41 00        mov ax, 0x41
CE4A  50              push ax
CE4B  9A 37 2F 71 17  call far 1771:2F37
CE50  83 7E F7 0B     cmp word ptr [bp - 9], 0xb
CE54  75 D9           jne 0xce2f
CE56  8B 46 FB        mov ax, word ptr [bp - 5]
CE59  D1 E0           shl ax, 1
CE5B  C4 7E F3        les di, ptr [bp - 0xd]
CE5E  03 F8           add di, ax
CE60  26 FF 75 FE     push word ptr es:[di - 2]
CE64  9A BC 42 71 17  call far 1771:42BC
CE69  8B 46 FB        mov ax, word ptr [bp - 5]
CE6C  05 07 00        add ax, 7
CE6F  50              push ax
CE70  B8 41 00        mov ax, 0x41
CE73  50              push ax
CE74  B8 0D 00        mov ax, 0xd
CE77  50              push ax
CE78  9A C5 13 4B 21  call far 214B:13C5
CE7D  B0 03           mov al, 3
CE7F  50              push ax
CE80  8A 46 04        mov al, byte ptr [bp + 4]
CE83  30 E4           xor ah, ah
CE85  BA 0B 00        mov dx, 0xb
CE88  F7 E2           mul dx
CE8A  8B F8           mov di, ax
CE8C  81 C7 29 0A     add di, 0xa29
CE90  1E              push ds
CE91  57              push di
CE92  B0 19           mov al, 0x19
CE94  50              push ax
CE95  B0 0B           mov al, 0xb
CE97  50              push ax
CE98  BF 6E A9        mov di, 0xa96e
CE9B  1E              push ds
CE9C  57              push di
CE9D  9A C8 02 4B 21  call far 214B:02C8
CEA2  80 7E 04 01     cmp byte ptr [bp + 4], 1
CEA6  75 15           jne 0xcebd
CEA8  BF 73 CC        mov di, 0xcc73
CEAB  0E              push cs
CEAC  57              push di
CEAD  B0 19           mov al, 0x19
CEAF  50              push ax
CEB0  B0 13           mov al, 0x13
CEB2  50              push ax
CEB3  BF 6E A9        mov di, 0xa96e
CEB6  1E              push ds
CEB7  57              push di
CEB8  9A 6D 02 4B 21  call far 214B:026D
loc_CEBD:
CEBD  C4 3E 6E A9     les di, ptr [0xa96e]
CEC1  06              push es
CEC2  57              push di
CEC3  C4 3E 6A A9     les di, ptr [0xa96a]
CEC7  06              push es
CEC8  57              push di
CEC9  B8 A0 0F        mov ax, 0xfa0
CECC  50              push ax
CECD  9A 5D 02 E4 23  call far 23E4:025D
CED2  B8 E8 03        mov ax, 0x3e8
CED5  50              push ax
CED6  E8 55 FD        call 0xcc2e
CED9  9A 23 07 4B 21  call far 214B:0723
CEDE  08 C0           or al, al
CEE0  75 06           jne 0xcee8
CEE2  C6 46 FD 01     mov byte ptr [bp - 3], 1
CEE6  EB 1C           jmp 0xcf04
loc_CEE8:
CEE8  9A DD 08 4B 21  call far 214B:08DD
CEED  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
CEF2  74 0B           je 0xceff
CEF4  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
CEF9  74 04           je 0xceff
CEFB  B0 00           mov al, 0
CEFD  EB 02           jmp 0xcf01
loc_CEFF:
CEFF  B0 01           mov al, 1
loc_CF01:
CF01  88 46 FD        mov byte ptr [bp - 3], al
loc_CF04:
CF04  80 3E 76 A9 20  cmp byte ptr [0xa976], 0x20
CF09  75 32           jne 0xcf3d
CF0B  80 7E 04 01     cmp byte ptr [bp + 4], 1
CF0F  74 2C           je 0xcf3d
CF11  C4 3E 72 A9     les di, ptr [0xa972]
CF15  06              push es
CF16  57              push di
CF17  C4 3E 6A A9     les di, ptr [0xa96a]
CF1B  06              push es
CF1C  57              push di
CF1D  B8 A0 0F        mov ax, 0xfa0
CF20  50              push ax
CF21  9A 5D 02 E4 23  call far 23E4:025D
CF26  BF A6 14        mov di, 0x14a6
CF29  1E              push ds
CF2A  57              push di
CF2B  BF 6A A9        mov di, 0xa96a
CF2E  1E              push ds
CF2F  57              push di
CF30  9A 29 03 4B 21  call far 214B:0329
CF35  9A DD 08 4B 21  call far 214B:08DD
CF3A  E9 9E 00        jmp 0xcfdb
loc_CF3D:
CF3D  A0 76 A9        mov al, byte ptr [0xa976]
CF40  50              push ax
CF41  9A B2 19 E4 23  call far 23E4:19B2
CF46  3C 43           cmp al, 0x43
CF48  75 5E           jne 0xcfa8
CF4A  80 7E 04 01     cmp byte ptr [bp + 4], 1
CF4E  75 1A           jne 0xcf6a
CF50  8A 46 06        mov al, byte ptr [bp + 6]
CF53  50              push ax
CF54  E8 E5 4F        call 0x11f3c
CF57  8B C8           mov cx, ax
CF59  8A 46 06        mov al, byte ptr [bp + 6]
CF5C  98              cwde
CF5D  BA 0A 00        mov dx, 0xa
CF60  F7 E2           mul dx
CF62  8B F8           mov di, ax
CF64  89 8D 78 99     mov word ptr [di - 0x6688], cx
CF68  EB 1B           jmp 0xcf85
loc_CF6A:
CF6A  8A 46 06        mov al, byte ptr [bp + 6]
CF6D  50              push ax
CF6E  8A 46 04        mov al, byte ptr [bp + 4]
CF71  30 E4           xor ah, ah
CF73  8B F8           mov di, ax
CF75  8A 85 64 07     mov al, byte ptr [di + 0x764]
CF79  30 E4           xor ah, ah
CF7B  50              push ax
CF7C  8A 46 04        mov al, byte ptr [bp + 4]
CF7F  30 E4           xor ah, ah
CF81  50              push ax
CF82  E8 58 50        call 0x11fdd
loc_CF85:
CF85  8A 46 04        mov al, byte ptr [bp + 4]
CF88  30 E4           xor ah, ah
CF8A  D1 E0           shl ax, 1
CF8C  8B C8           mov cx, ax
CF8E  8A 46 06        mov al, byte ptr [bp + 6]
CF91  98              cwde
CF92  BA 0A 00        mov dx, 0xa
CF95  F7 E2           mul dx
CF97  8B F8           mov di, ax
CF99  03 F9           add di, cx
CF9B  8B 85 76 99     mov ax, word ptr [di - 0x668a]
CF9F  89 46 F9        mov word ptr [bp - 7], ax
CFA2  C6 46 FD 01     mov byte ptr [bp - 3], 1
CFA6  EB 33           jmp 0xcfdb
loc_CFA8:
CFA8  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
CFAD  75 2C           jne 0xcfdb
CFAF  8B 46 FB        mov ax, word ptr [bp - 5]
CFB2  D1 E0           shl ax, 1
CFB4  C4 7E F3        les di, ptr [bp - 0xd]
CFB7  03 F8           add di, ax
CFB9  26 FF 75 FE     push word ptr es:[di - 2]
CFBD  9A 16 32 71 17  call far 1771:3216
CFC2  08 C0           or al, al
CFC4  75 15           jne 0xcfdb
CFC6  8B 46 FB        mov ax, word ptr [bp - 5]
CFC9  D1 E0           shl ax, 1
CFCB  C4 7E F3        les di, ptr [bp - 0xd]
CFCE  03 F8           add di, ax
CFD0  26 8B 45 FE     mov ax, word ptr es:[di - 2]
CFD4  89 46 F9        mov word ptr [bp - 7], ax
CFD7  C6 46 FD 01     mov byte ptr [bp - 3], 1
loc_CFDB:
CFDB  8D 7E FB        lea di, [bp - 5]
CFDE  16              push ss
CFDF  57              push di
CFE0  B8 0B 00        mov ax, 0xb
CFE3  50              push ax
CFE4  9A 07 15 4B 21  call far 214B:1507
CFE9  80 7E FD 00     cmp byte ptr [bp - 3], 0
CFED  75 03           jne 0xcff2
CFEF  E9 E3 FD        jmp 0xcdd5
loc_CFF2:
CFF2  C4 3E 72 A9     les di, ptr [0xa972]
CFF6  06              push es
CFF7  57              push di
CFF8  C4 3E 6A A9     les di, ptr [0xa96a]
CFFC  06              push es
CFFD  57              push di
CFFE  B8 A0 0F        mov ax, 0xfa0
D001  50              push ax
D002  9A 5D 02 E4 23  call far 23E4:025D
D007  8B 46 F9        mov ax, word ptr [bp - 7]
D00A  89 46 FE        mov word ptr [bp - 2], ax
D00D  8B 46 FE        mov ax, word ptr [bp - 2]
D010  89 EC           mov sp, bp
D012  5D              pop bp
D013  C2 04 00        ret 4

