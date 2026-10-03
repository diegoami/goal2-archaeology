; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 17 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:A260  (found by: call)
sub_A260:
A260  55              push bp
A261  89 E5           mov bp, sp
A263  8A 46 0A        mov al, byte ptr [bp + 0xa]
A266  C4 7E 06        les di, ptr [bp + 6]
A269  26 88 45 06     mov byte ptr es:[di + 6], al
A26D  C4 7E 06        les di, ptr [bp + 6]
A270  06              push es
A271  57              push di
A272  0E              push cs
A273  E8 3B 89        call 0x2bb1
A276  30 E4           xor ah, ah
A278  D1 E0           shl ax, 1
A27A  50              push ax
A27B  C4 7E 06        les di, ptr [bp + 6]
A27E  06              push es
A27F  57              push di
A280  0E              push cs
A281  E8 F0 86        call 0x2974
A284  98              cwde
A285  8B F8           mov di, ax
A287  D1 E7           shl di, 1
A289  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
A28D  BA BF 00        mov dx, 0xbf
A290  F7 E2           mul dx
A292  C4 3E 17 A9     les di, ptr [0xa917]
A296  03 F8           add di, ax
A298  58              pop ax
A299  03 F8           add di, ax
A29B  26 8B 45 FE     mov ax, word ptr es:[di - 2]
A29F  C4 7E 06        les di, ptr [bp + 6]
A2A2  26 89 45 0D     mov word ptr es:[di + 0xd], ax
A2A6  C4 7E 06        les di, ptr [bp + 6]
A2A9  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
A2AD  BA 14 00        mov dx, 0x14
A2B0  F7 E2           mul dx
A2B2  C4 3E 1B A9     les di, ptr [0xa91b]
A2B6  03 F8           add di, ax
A2B8  26 8A 05        mov al, byte ptr es:[di]
A2BB  30 E4           xor ah, ah
A2BD  50              push ax
A2BE  9A A7 0A 71 17  call far 1771:0AA7
A2C3  05 20 00        add ax, 0x20
A2C6  C4 7E 06        les di, ptr [bp + 6]
A2C9  26 88 45 11     mov byte ptr es:[di + 0x11], al
A2CD  C4 7E 06        les di, ptr [bp + 6]
A2D0  26 FF 75 0D     push word ptr es:[di + 0xd]
A2D4  9A 79 31 71 17  call far 1771:3179
A2D9  C4 7E 06        les di, ptr [bp + 6]
A2DC  26 88 45 13     mov byte ptr es:[di + 0x13], al
A2E0  89 EC           mov sp, bp
A2E2  5D              pop bp
A2E3  CA 06 00        retf 6

; ---- routine 0791:A2E6  (found by: call)
sub_A2E6:
A2E6  55              push bp
A2E7  89 E5           mov bp, sp
A2E9  FF 76 0A        push word ptr [bp + 0xa]
A2EC  C4 7E 06        les di, ptr [bp + 6]
A2EF  06              push es
A2F0  57              push di
A2F1  0E              push cs
A2F2  E8 6B FF        call 0xa260
A2F5  A1 44 06        mov ax, word ptr [0x644]
A2F8  C4 7E 06        les di, ptr [bp + 6]
A2FB  26 89 05        mov word ptr es:[di], ax
A2FE  C4 7E 06        les di, ptr [bp + 6]
A301  26 8B 05        mov ax, word ptr es:[di]
A304  C4 7E 06        les di, ptr [bp + 6]
A307  26 89 45 02     mov word ptr es:[di + 2], ax
A30B  C4 7E 06        les di, ptr [bp + 6]
A30E  26 8A 45 06     mov al, byte ptr es:[di + 6]
A312  30 E4           xor ah, ah
A314  50              push ax
A315  E8 45 61        call 0x1045d
A318  08 C0           or al, al
A31A  74 19           je 0xa335
A31C  C4 7E 06        les di, ptr [bp + 6]
A31F  06              push es
A320  57              push di
A321  0E              push cs
A322  E8 4F 86        call 0x2974
A325  98              cwde
A326  8B F8           mov di, ax
A328  8A 85 30 83     mov al, byte ptr [di - 0x7cd0]
A32C  C4 7E 06        les di, ptr [bp + 6]
A32F  26 88 45 05     mov byte ptr es:[di + 5], al
A333  EB 17           jmp 0xa34c
loc_A335:
A335  C4 7E 06        les di, ptr [bp + 6]
A338  06              push es
A339  57              push di
A33A  0E              push cs
A33B  E8 36 86        call 0x2974
A33E  98              cwde
A33F  8B F8           mov di, ax
A341  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
A345  C4 7E 06        les di, ptr [bp + 6]
A348  26 88 45 05     mov byte ptr es:[di + 5], al
loc_A34C:
A34C  A1 3E 06        mov ax, word ptr [0x63e]
A34F  C4 7E 06        les di, ptr [bp + 6]
A352  26 89 45 0B     mov word ptr es:[di + 0xb], ax
A356  C4 7E 06        les di, ptr [bp + 6]
A359  26 C6 45 10 00  mov byte ptr es:[di + 0x10], 0
A35E  C4 7E 06        les di, ptr [bp + 6]
A361  31 C0           xor ax, ax
A363  26 89 45 14     mov word ptr es:[di + 0x14], ax
A367  C4 7E 06        les di, ptr [bp + 6]
A36A  26 C6 45 0F 05  mov byte ptr es:[di + 0xf], 5
A36F  89 EC           mov sp, bp
A371  5D              pop bp
A372  CA 06 00        retf 6

; ---- routine 0791:A375  (found by: call)
sub_A375:
A375  55              push bp
A376  89 E5           mov bp, sp
A378  C4 7E 06        les di, ptr [bp + 6]
A37B  31 C0           xor ax, ax
A37D  26 89 45 0A     mov word ptr es:[di + 0xa], ax
A381  C4 7E 06        les di, ptr [bp + 6]
A384  26 C7 45 04 07 0F mov word ptr es:[di + 4], 0xf07
A38A  C4 7E 06        les di, ptr [bp + 6]
A38D  26 C6 45 0C 00  mov byte ptr es:[di + 0xc], 0
A392  C4 7E 06        les di, ptr [bp + 6]
A395  26 C6 45 0D 00  mov byte ptr es:[di + 0xd], 0
A39A  A1 40 06        mov ax, word ptr [0x640]
A39D  C4 7E 06        les di, ptr [bp + 6]
A3A0  26 89 05        mov word ptr es:[di], ax
A3A3  C4 7E 06        les di, ptr [bp + 6]
A3A6  26 8B 05        mov ax, word ptr es:[di]
A3A9  C4 7E 06        les di, ptr [bp + 6]
A3AC  26 89 45 02     mov word ptr es:[di + 2], ax
A3B0  89 EC           mov sp, bp
A3B2  5D              pop bp
A3B3  CA 04 00        retf 4

; ---- routine 0791:A3B6  (found by: call)
sub_A3B6:
A3B6  55              push bp
A3B7  89 E5           mov bp, sp
A3B9  C4 7E 06        les di, ptr [bp + 6]
A3BC  26 C7 45 04 01 0D mov word ptr es:[di + 4], 0xd01
A3C2  A1 44 06        mov ax, word ptr [0x644]
A3C5  C4 7E 06        les di, ptr [bp + 6]
A3C8  26 89 05        mov word ptr es:[di], ax
A3CB  C4 7E 06        les di, ptr [bp + 6]
A3CE  26 8B 05        mov ax, word ptr es:[di]
A3D1  C4 7E 06        les di, ptr [bp + 6]
A3D4  26 89 45 02     mov word ptr es:[di + 2], ax
A3D8  89 EC           mov sp, bp
A3DA  5D              pop bp
A3DB  CA 04 00        retf 4

; ---- routine 0791:A3DE  (found by: call)
sub_A3DE:
A3DE  55              push bp
A3DF  89 E5           mov bp, sp
A3E1  83 EC 06        sub sp, 6
A3E4  C4 7E 04        les di, ptr [bp + 4]
A3E7  89 7E FB        mov word ptr [bp - 5], di
A3EA  8C 46 FD        mov word ptr [bp - 3], es
A3ED  C4 7E FB        les di, ptr [bp - 5]
A3F0  26 C4 45 04     les ax, ptr es:[di + 4]
A3F4  8C C2           mov dx, es
A3F6  A3 34 9B        mov word ptr [0x9b34], ax
A3F9  89 16 36 9B     mov word ptr [0x9b36], dx
A3FD  C4 7E FB        les di, ptr [bp - 5]
A400  26 8A 45 02     mov al, byte ptr es:[di + 2]
A404  50              push ax
A405  BF 3A 69        mov di, 0x693a
A408  1E              push ds
A409  57              push di
A40A  9A DF 08 E4 23  call far 23E4:08DF
A40F  75 04           jne 0xa415
A411  B0 00           mov al, 0
A413  EB 02           jmp 0xa417
loc_A415:
A415  B0 01           mov al, 1
loc_A417:
A417  A2 36 7C        mov byte ptr [0x7c36], al
A41A  C4 7E 04        les di, ptr [bp + 4]
A41D  06              push es
A41E  57              push di
A41F  0E              push cs
A420  E8 29 30        call 0xd44c
A423  A2 FC 80        mov byte ptr [0x80fc], al
A426  C4 7E FB        les di, ptr [bp - 5]
A429  26 8A 45 01     mov al, byte ptr es:[di + 1]
A42D  A2 76 99        mov byte ptr [0x9976], al
A430  C4 7E 04        les di, ptr [bp + 4]
A433  89 F8           mov ax, di
A435  8C C2           mov dx, es
A437  A3 2A 7C        mov word ptr [0x7c2a], ax
A43A  89 16 2C 7C     mov word ptr [0x7c2c], dx
A43E  E8 07 82        call 0x2648
A441  31 C0           xor ax, ax
A443  A3 3C 9B        mov word ptr [0x9b3c], ax
A446  C6 46 FF 00     mov byte ptr [bp - 1], 0
A44A  EB 03           jmp 0xa44f
loc_A44C:
A44C  FE 46 FF        inc byte ptr [bp - 1]
loc_A44F:
A44F  8A 46 FF        mov al, byte ptr [bp - 1]
A452  98              cwde
A453  D1 E0           shl ax, 1
A455  C4 7E FB        les di, ptr [bp - 5]
A458  03 F8           add di, ax
A45A  26 FF 75 04     push word ptr es:[di + 4]
A45E  9A 77 0B 71 17  call far 1771:0B77
A463  08 C0           or al, al
A465  75 2E           jne 0xa495
A467  8A 46 FF        mov al, byte ptr [bp - 1]
A46A  98              cwde
A46B  D1 E0           shl ax, 1
A46D  C4 7E FB        les di, ptr [bp - 5]
A470  03 F8           add di, ax
A472  26 FF 75 04     push word ptr es:[di + 4]
A476  0E              push cs
A477  E8 A5 0C        call 0xb11f
A47A  8A 46 FF        mov al, byte ptr [bp - 1]
A47D  98              cwde
A47E  D1 E0           shl ax, 1
A480  C4 7E FB        les di, ptr [bp - 5]
A483  03 F8           add di, ax
A485  26 FF 75 04     push word ptr es:[di + 4]
A489  9A E7 34 71 17  call far 1771:34E7
A48E  8A 46 FF        mov al, byte ptr [bp - 1]
A491  50              push ax
A492  E8 EE 18        call 0xbd83
loc_A495:
A495  80 7E FF 01     cmp byte ptr [bp - 1], 1
A499  75 B1           jne 0xa44c
A49B  89 EC           mov sp, bp
A49D  5D              pop bp
A49E  C2 04 00        ret 4

; ---- routine 0791:A4A1  (found by: call)
sub_A4A1:
A4A1  55              push bp
A4A2  89 E5           mov bp, sp
A4A4  83 EC 04        sub sp, 4
A4A7  C4 7E 04        les di, ptr [bp + 4]
A4AA  06              push es
A4AB  57              push di
A4AC  E8 2F FF        call 0xa3de
A4AF  C7 06 2C 83 FF FF mov word ptr [0x832c], 0xffff
A4B5  E8 BB 6B        call 0x11073
A4B8  BF 08 9B        mov di, 0x9b08
A4BB  1E              push ds
A4BC  57              push di
A4BD  B8 28 00        mov ax, 0x28
A4C0  50              push ax
A4C1  31 C0           xor ax, ax
A4C3  50              push ax
A4C4  9A 18 00 4B 21  call far 214B:0018
A4C9  31 C0           xor ax, ax
A4CB  A3 3A 7C        mov word ptr [0x7c3a], ax
A4CE  31 C0           xor ax, ax
A4D0  A3 32 83        mov word ptr [0x8332], ax
A4D3  31 C0           xor ax, ax
A4D5  A3 34 83        mov word ptr [0x8334], ax
A4D8  31 C0           xor ax, ax
A4DA  A3 EE 80        mov word ptr [0x80ee], ax
A4DD  BF 3E 7C        mov di, 0x7c3e
A4E0  1E              push ds
A4E1  57              push di
A4E2  B8 B0 04        mov ax, 0x4b0
A4E5  50              push ax
A4E6  B8 FF 00        mov ax, 0xff
A4E9  50              push ax
A4EA  9A 18 00 4B 21  call far 214B:0018
A4EF  BF 7E 7B        mov di, 0x7b7e
A4F2  1E              push ds
A4F3  57              push di
A4F4  B8 14 00        mov ax, 0x14
A4F7  50              push ax
A4F8  31 C0           xor ax, ax
A4FA  50              push ax
A4FB  9A 18 00 4B 21  call far 214B:0018
A500  BF D4 7B        mov di, 0x7bd4
A503  1E              push ds
A504  57              push di
A505  B8 42 00        mov ax, 0x42
A508  50              push ax
A509  31 C0           xor ax, ax
A50B  50              push ax
A50C  9A 18 00 4B 21  call far 214B:0018
A511  BF F2 80        mov di, 0x80f2
A514  1E              push ds
A515  57              push di
A516  B8 04 00        mov ax, 4
A519  50              push ax
A51A  31 C0           xor ax, ax
A51C  50              push ax
A51D  9A 18 00 4B 21  call far 214B:0018
A522  BF F6 80        mov di, 0x80f6
A525  1E              push ds
A526  57              push di
A527  B8 04 00        mov ax, 4
A52A  50              push ax
A52B  31 C0           xor ax, ax
A52D  50              push ax
A52E  9A 18 00 4B 21  call far 214B:0018
A533  BF 40 9A        mov di, 0x9a40
A536  1E              push ds
A537  57              push di
A538  B8 50 00        mov ax, 0x50
A53B  50              push ax
A53C  31 C0           xor ax, ax
A53E  50              push ax
A53F  9A 18 00 4B 21  call far 214B:0018
A544  C4 7E 04        les di, ptr [bp + 4]
A547  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
A54C  75 04           jne 0xa552
A54E  B0 00           mov al, 0
A550  EB 02           jmp 0xa554
loc_A552:
A552  B0 01           mov al, 1
loc_A554:
A554  A2 3D 9A        mov byte ptr [0x9a3d], al
A557  9A FA 06 4B 21  call far 214B:06FA
A55C  A2 1A 83        mov byte ptr [0x831a], al
A55F  C6 06 0C 83 00  mov byte ptr [0x830c], 0
A564  C6 06 0E 83 00  mov byte ptr [0x830e], 0
A569  C6 06 0D 83 00  mov byte ptr [0x830d], 0
A56E  C6 06 FA 80 00  mov byte ptr [0x80fa], 0
A573  C6 06 39 7C 00  mov byte ptr [0x7c39], 0
A578  BF F6 82        mov di, 0x82f6
A57B  1E              push ds
A57C  57              push di
A57D  0E              push cs
A57E  E8 F4 FD        call 0xa375
A581  BF EE 82        mov di, 0x82ee
A584  1E              push ds
A585  57              push di
A586  0E              push cs
A587  E8 2C FE        call 0xa3b6
A58A  BF 04 83        mov di, 0x8304
A58D  1E              push ds
A58E  57              push di
A58F  0E              push cs
A590  E8 23 FE        call 0xa3b6
A593  C7 46 FE 01 00  mov word ptr [bp - 2], 1
A598  EB 03           jmp 0xa59d
loc_A59A:
A59A  FF 46 FE        inc word ptr [bp - 2]
loc_A59D:
A59D  FF 76 FE        push word ptr [bp - 2]
A5A0  8B 46 FE        mov ax, word ptr [bp - 2]
A5A3  BA 16 00        mov dx, 0x16
A5A6  F7 E2           mul dx
A5A8  8B F8           mov di, ax
A5AA  81 C7 E8 80     add di, 0x80e8
A5AE  1E              push ds
A5AF  57              push di
A5B0  0E              push cs
A5B1  E8 32 FD        call 0xa2e6
A5B4  83 7E FE 16     cmp word ptr [bp - 2], 0x16
A5B8  75 E0           jne 0xa59a
A5BA  C6 06 1F 0C 00  mov byte ptr [0xc1f], 0
A5BF  C6 06 26 83 00  mov byte ptr [0x8326], 0
A5C4  C6 06 41 9B 01  mov byte ptr [0x9b41], 1
A5C9  C6 46 FD 00     mov byte ptr [bp - 3], 0
A5CD  EB 03           jmp 0xa5d2
loc_A5CF:
A5CF  FE 46 FD        inc byte ptr [bp - 3]
loc_A5D2:
A5D2  8A 46 FD        mov al, byte ptr [bp - 3]
A5D5  98              cwde
A5D6  8B F8           mov di, ax
A5D8  C6 85 F0 80 00  mov byte ptr [di - 0x7f10], 0
A5DD  8A 46 FD        mov al, byte ptr [bp - 3]
A5E0  98              cwde
A5E1  8B F8           mov di, ax
A5E3  D1 E7           shl di, 1
A5E5  8B F7           mov si, di
A5E7  D1 E7           shl di, 1
A5E9  03 FE           add di, si
A5EB  81 C7 E2 82     add di, 0x82e2
A5EF  1E              push ds
A5F0  57              push di
A5F1  0E              push cs
A5F2  E8 C1 FD        call 0xa3b6
A5F5  A0 3D 9A        mov al, byte ptr [0x9a3d]
A5F8  98              cwde
A5F9  8B F8           mov di, ax
A5FB  8A 95 6B 06     mov dl, byte ptr [di + 0x66b]
A5FF  8A 46 FD        mov al, byte ptr [bp - 3]
A602  98              cwde
A603  8B F8           mov di, ax
A605  88 95 3A 9B     mov byte ptr [di - 0x64c6], dl
A609  80 7E FD 01     cmp byte ptr [bp - 3], 1
A60D  75 C0           jne 0xa5cf
A60F  E8 FA 7C        call 0x1230c
A612  E8 9C 89        call 0x2fb1
A615  C6 06 40 9B 00  mov byte ptr [0x9b40], 0
A61A  31 C0           xor ax, ax
A61C  A3 1D 83        mov word ptr [0x831d], ax
A61F  31 C0           xor ax, ax
A621  A3 1F 83        mov word ptr [0x831f], ax
A624  31 C0           xor ax, ax
A626  A3 21 83        mov word ptr [0x8321], ax
A629  C6 06 25 83 00  mov byte ptr [0x8325], 0
A62E  C6 06 24 83 00  mov byte ptr [0x8324], 0
A633  C6 06 27 83 00  mov byte ptr [0x8327], 0
A638  C6 06 28 83 00  mov byte ptr [0x8328], 0
A63D  C7 06 2A 83 64 00 mov word ptr [0x832a], 0x64
A643  FF 36 36 9B     push word ptr [0x9b36]
A647  9A 77 0B 71 17  call far 1771:0B77
A64C  08 C0           or al, al
A64E  75 11           jne 0xa661
A650  FF 36 34 9B     push word ptr [0x9b34]
A654  9A 77 0B 71 17  call far 1771:0B77
A659  08 C0           or al, al
A65B  75 04           jne 0xa661
A65D  B0 00           mov al, 0
A65F  EB 02           jmp 0xa663
loc_A661:
A661  B0 01           mov al, 1
loc_A663:
A663  A2 FD 80        mov byte ptr [0x80fd], al
A666  C6 06 1E 0C 01  mov byte ptr [0xc1e], 1
A66B  BF 78 99        mov di, 0x9978
A66E  1E              push ds
A66F  57              push di
A670  B8 14 00        mov ax, 0x14
A673  50              push ax
A674  31 C0           xor ax, ax
A676  50              push ax
A677  9A 18 00 4B 21  call far 214B:0018
A67C  C6 06 3E 9A 00  mov byte ptr [0x9a3e], 0
A681  C6 06 3F 9A 00  mov byte ptr [0x9a3f], 0
A686  E8 B8 01        call 0xa841
A689  C6 06 37 7C 00  mov byte ptr [0x7c37], 0
A68E  C6 06 38 7C 00  mov byte ptr [0x7c38], 0
A693  89 EC           mov sp, bp
A695  5D              pop bp
A696  C2 04 00        ret 4

; ---- routine 0791:A699  (found by: call)
sub_A699:
A699  55              push bp
A69A  89 E5           mov bp, sp
A69C  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
A6A1  74 17           je 0xa6ba
A6A3  C4 3E 22 7C     les di, ptr [0x7c22]
A6A7  06              push es
A6A8  57              push di
A6A9  C4 3E 1A 7C     les di, ptr [0x7c1a]
A6AD  06              push es
A6AE  57              push di
A6AF  B8 A0 0F        mov ax, 0xfa0
A6B2  50              push ax
A6B3  9A 5D 02 E4 23  call far 23E4:025D
A6B8  EB 15           jmp 0xa6cf
loc_A6BA:
A6BA  C4 3E 1E 7C     les di, ptr [0x7c1e]
A6BE  06              push es
A6BF  57              push di
A6C0  C4 3E 1A 7C     les di, ptr [0x7c1a]
A6C4  06              push es
A6C5  57              push di
A6C6  B8 A0 0F        mov ax, 0xfa0
A6C9  50              push ax
A6CA  9A 5D 02 E4 23  call far 23E4:025D
loc_A6CF:
A6CF  C4 7E 04        les di, ptr [bp + 4]
A6D2  06              push es
A6D3  57              push di
A6D4  BF 6E A9        mov di, 0xa96e
A6D7  1E              push ds
A6D8  57              push di
A6D9  9A 29 03 4B 21  call far 214B:0329
A6DE  89 EC           mov sp, bp
A6E0  5D              pop bp
A6E1  C2 04 00        ret 4

; ---- routine 0791:A6E4  (found by: call)
sub_A6E4:
A6E4  55              push bp
A6E5  89 E5           mov bp, sp
A6E7  83 EC 0C        sub sp, 0xc
A6EA  C4 7E 04        les di, ptr [bp + 4]
A6ED  89 7E F8        mov word ptr [bp - 8], di
A6F0  8C 46 FA        mov word ptr [bp - 6], es
A6F3  C4 3E 23 A9     les di, ptr [0xa923]
A6F7  89 7E F4        mov word ptr [bp - 0xc], di
A6FA  8C 46 F6        mov word ptr [bp - 0xa], es
A6FD  C4 7E 04        les di, ptr [bp + 4]
A700  06              push es
A701  57              push di
A702  9A 03 5A 71 17  call far 1771:5A03
A707  08 C0           or al, al
A709  74 3F           je 0xa74a
A70B  C4 7E F4        les di, ptr [bp - 0xc]
A70E  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
A713  74 07           je 0xa71c
A715  C7 46 FC 05 00  mov word ptr [bp - 4], 5
A71A  EB 1B           jmp 0xa737
loc_A71C:
A71C  C4 7E F8        les di, ptr [bp - 8]
A71F  26 8B 45 06     mov ax, word ptr es:[di + 6]
A723  BA BF 00        mov dx, 0xbf
A726  F7 E2           mul dx
A728  C4 3E 17 A9     les di, ptr [0xa917]
A72C  03 F8           add di, ax
A72E  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
A732  30 E4           xor ah, ah
A734  89 46 FC        mov word ptr [bp - 4], ax
loc_A737:
A737  8B 46 FC        mov ax, word ptr [bp - 4]
A73A  D1 E0           shl ax, 1
A73C  C4 7E F4        les di, ptr [bp - 0xc]
A73F  03 F8           add di, ax
A741  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
A745  89 46 FE        mov word ptr [bp - 2], ax
A748  EB 0A           jmp 0xa754
loc_A74A:
A74A  C4 7E F8        les di, ptr [bp - 8]
A74D  26 8B 45 06     mov ax, word ptr es:[di + 6]
A751  89 46 FE        mov word ptr [bp - 2], ax
loc_A754:
A754  8B 46 FE        mov ax, word ptr [bp - 2]
A757  89 EC           mov sp, bp
A759  5D              pop bp
A75A  C2 04 00        ret 4

; ---- routine 0791:A75D  (found by: call)
sub_A75D:
A75D  55              push bp
A75E  89 E5           mov bp, sp
A760  81 EC 08 01     sub sp, 0x108
A764  BF 4A 53        mov di, 0x534a
A767  1E              push ds
A768  57              push di
A769  E8 2D FF        call 0xa699
A76C  C6 46 FF 00     mov byte ptr [bp - 1], 0
A770  EB 03           jmp 0xa775
loc_A772:
A772  FE 46 FF        inc byte ptr [bp - 1]
loc_A775:
A775  8A 46 FF        mov al, byte ptr [bp - 1]
A778  98              cwde
A779  8B F8           mov di, ax
A77B  D1 E7           shl di, 1
A77D  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
A781  BA BF 00        mov dx, 0xbf
A784  F7 E2           mul dx
A786  C4 3E 17 A9     les di, ptr [0xa917]
A78A  03 F8           add di, ax
A78C  89 7E F9        mov word ptr [bp - 7], di
A78F  8C 46 FB        mov word ptr [bp - 5], es
A792  8A 46 FF        mov al, byte ptr [bp - 1]
A795  98              cwde
A796  8B F8           mov di, ax
A798  D1 E7           shl di, 1
A79A  FF B5 34 9B     push word ptr [di - 0x64cc]
A79E  B8 08 00        mov ax, 8
A7A1  50              push ax
A7A2  8A 46 FF        mov al, byte ptr [bp - 1]
A7A5  98              cwde
A7A6  8B F8           mov di, ax
A7A8  8A 85 C6 08     mov al, byte ptr [di + 0x8c6]
A7AC  30 E4           xor ah, ah
A7AE  50              push ax
A7AF  9A 58 0F 71 17  call far 1771:0F58
A7B4  B0 07           mov al, 7
A7B6  50              push ax
A7B7  8D BE F9 FE     lea di, [bp - 0x107]
A7BB  16              push ss
A7BC  57              push di
A7BD  8A 46 FF        mov al, byte ptr [bp - 1]
A7C0  98              cwde
A7C1  8B F8           mov di, ax
A7C3  D1 E7           shl di, 1
A7C5  FF B5 34 9B     push word ptr [di - 0x64cc]
A7C9  9A 6C 0E 71 17  call far 1771:0E6C
A7CE  B0 0B           mov al, 0xb
A7D0  50              push ax
A7D1  8A 46 FF        mov al, byte ptr [bp - 1]
A7D4  98              cwde
A7D5  8B F8           mov di, ax
A7D7  8A 85 CA 08     mov al, byte ptr [di + 0x8ca]
A7DB  50              push ax
A7DC  BF 6E A9        mov di, 0xa96e
A7DF  1E              push ds
A7E0  57              push di
A7E1  9A 05 02 4B 21  call far 214B:0205
A7E6  C7 46 FD 01 00  mov word ptr [bp - 3], 1
A7EB  EB 03           jmp 0xa7f0
loc_A7ED:
A7ED  FF 46 FD        inc word ptr [bp - 3]
loc_A7F0:
A7F0  8B 46 FD        mov ax, word ptr [bp - 3]
A7F3  D1 E0           shl ax, 1
A7F5  C4 7E F9        les di, ptr [bp - 7]
A7F8  03 F8           add di, ax
A7FA  26 FF 75 FE     push word ptr es:[di - 2]
A7FE  8B 46 FD        mov ax, word ptr [bp - 3]
A801  05 0C 00        add ax, 0xc
A804  50              push ax
A805  8A 46 FF        mov al, byte ptr [bp - 1]
A808  98              cwde
A809  8B F8           mov di, ax
A80B  8A 85 C8 08     mov al, byte ptr [di + 0x8c8]
A80F  30 E4           xor ah, ah
A811  50              push ax
A812  9A 37 2F 71 17  call far 1771:2F37
A817  83 7E FD 0B     cmp word ptr [bp - 3], 0xb
A81B  75 D0           jne 0xa7ed
A81D  80 7E FF 01     cmp byte ptr [bp - 1], 1
A821  74 03           je 0xa826
A823  E9 4C FF        jmp 0xa772
loc_A826:
A826  C4 3E 2A 7C     les di, ptr [0x7c2a]
A82A  06              push es
A82B  57              push di
A82C  E8 B5 FE        call 0xa6e4
A82F  50              push ax
A830  B8 07 00        mov ax, 7
A833  50              push ax
A834  B8 26 00        mov ax, 0x26
A837  50              push ax
A838  9A 58 0F 71 17  call far 1771:0F58
A83D  89 EC           mov sp, bp
A83F  5D              pop bp
A840  C3              ret

; ---- routine 0791:A841  (found by: call)
sub_A841:
A841  55              push bp
A842  89 E5           mov bp, sp
A844  81 EC 02 02     sub sp, 0x202
A848  BF 92 61        mov di, 0x6192
A84B  1E              push ds
A84C  57              push di
A84D  BF 6E A9        mov di, 0xa96e
A850  1E              push ds
A851  57              push di
A852  9A 29 03 4B 21  call far 214B:0329
A857  BF 3E 61        mov di, 0x613e
A85A  1E              push ds
A85B  57              push di
A85C  BF 6E A9        mov di, 0xa96e
A85F  1E              push ds
A860  57              push di
A861  9A 29 03 4B 21  call far 214B:0329
A866  BF 96 57        mov di, 0x5796
A869  1E              push ds
A86A  57              push di
A86B  BF 6E A9        mov di, 0xa96e
A86E  1E              push ds
A86F  57              push di
A870  9A 29 03 4B 21  call far 214B:0329
A875  C6 46 FF 00     mov byte ptr [bp - 1], 0
A879  EB 03           jmp 0xa87e
loc_A87B:
A87B  FE 46 FF        inc byte ptr [bp - 1]
loc_A87E:
A87E  8A 46 FF        mov al, byte ptr [bp - 1]
A881  98              cwde
A882  8B F8           mov di, ax
A884  8A 85 2E 83     mov al, byte ptr [di - 0x7cd2]
A888  50              push ax
A889  8D BE FF FE     lea di, [bp - 0x101]
A88D  16              push ss
A88E  57              push di
A88F  8A 46 FF        mov al, byte ptr [bp - 1]
A892  98              cwde
A893  8B F8           mov di, ax
A895  D1 E7           shl di, 1
A897  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
A89B  B1 04           mov cl, 4
A89D  D3 E0           shl ax, cl
A89F  C4 3E 68 9B     les di, ptr [0x9b68]
A8A3  03 F8           add di, ax
A8A5  06              push es
A8A6  57              push di
A8A7  9A 9C 00 4B 21  call far 214B:009C
A8AC  8A 46 FF        mov al, byte ptr [bp - 1]
A8AF  98              cwde
A8B0  8B F8           mov di, ax
A8B2  8A 85 CC 08     mov al, byte ptr [di + 0x8cc]
A8B6  50              push ax
A8B7  B0 0E           mov al, 0xe
A8B9  50              push ax
A8BA  BF 6E A9        mov di, 0xa96e
A8BD  1E              push ds
A8BE  57              push di
A8BF  9A C8 02 4B 21  call far 214B:02C8
A8C4  80 7E FF 01     cmp byte ptr [bp - 1], 1
A8C8  75 B1           jne 0xa87b
A8CA  B0 05           mov al, 5
A8CC  50              push ax
A8CD  8D BE FF FD     lea di, [bp - 0x201]
A8D1  16              push ss
A8D2  57              push di
A8D3  8D BE FF FE     lea di, [bp - 0x101]
A8D7  16              push ss
A8D8  57              push di
A8D9  C4 3E 2A 7C     les di, ptr [0x7c2a]
A8DD  26 8A 45 02     mov al, byte ptr es:[di + 2]
A8E1  30 E4           xor ah, ah
A8E3  50              push ax
A8E4  9A 0B 58 71 17  call far 1771:580B
A8E9  9A 9C 00 4B 21  call far 214B:009C
A8EE  B0 01           mov al, 1
A8F0  50              push ax
A8F1  B0 21           mov al, 0x21
A8F3  50              push ax
A8F4  BF 6E A9        mov di, 0xa96e
A8F7  1E              push ds
A8F8  57              push di
A8F9  9A C8 02 4B 21  call far 214B:02C8
A8FE  BF 6E A9        mov di, 0xa96e
A901  1E              push ds
A902  57              push di
A903  0E              push cs
A904  E8 0B 5E        call 0x10712
A907  C4 3E 6E A9     les di, ptr [0xa96e]
A90B  06              push es
A90C  57              push di
A90D  C4 3E 1E 7C     les di, ptr [0x7c1e]
A911  06              push es
A912  57              push di
A913  B8 A0 0F        mov ax, 0xfa0
A916  50              push ax
A917  9A 3C 00 4B 21  call far 214B:003C
A91C  89 EC           mov sp, bp
A91E  5D              pop bp
A91F  C3              ret

; ---- routine 0791:A920  (found by: call)
sub_A920:
A920  55              push bp
A921  89 E5           mov bp, sp
A923  83 EC 0A        sub sp, 0xa
A926  8B 46 04        mov ax, word ptr [bp + 4]
A929  BA 14 00        mov dx, 0x14
A92C  F7 E2           mul dx
A92E  C4 3E 1B A9     les di, ptr [0xa91b]
A932  03 F8           add di, ax
A934  26 8A 05        mov al, byte ptr es:[di]
A937  30 E4           xor ah, ah
A939  BA BF 00        mov dx, 0xbf
A93C  F7 E2           mul dx
A93E  C4 3E 17 A9     les di, ptr [0xa917]
A942  03 F8           add di, ax
A944  89 7E F6        mov word ptr [bp - 0xa], di
A947  8C 46 F8        mov word ptr [bp - 8], es
A94A  31 C0           xor ax, ax
A94C  89 46 FA        mov word ptr [bp - 6], ax
A94F  C7 46 FC 01 00  mov word ptr [bp - 4], 1
A954  EB 03           jmp 0xa959
loc_A956:
A956  FF 46 FC        inc word ptr [bp - 4]
loc_A959:
A959  8B 46 FC        mov ax, word ptr [bp - 4]
A95C  D1 E0           shl ax, 1
A95E  C4 7E F6        les di, ptr [bp - 0xa]
A961  03 F8           add di, ax
A963  26 8B 45 FE     mov ax, word ptr es:[di - 2]
A967  3B 46 04        cmp ax, word ptr [bp + 4]
A96A  75 06           jne 0xa972
A96C  8B 46 FC        mov ax, word ptr [bp - 4]
A96F  89 46 FA        mov word ptr [bp - 6], ax
loc_A972:
A972  83 7E FC 0B     cmp word ptr [bp - 4], 0xb
A976  75 DE           jne 0xa956
A978  83 7E FA 00     cmp word ptr [bp - 6], 0
A97C  74 2B           je 0xa9a9
A97E  8B 46 04        mov ax, word ptr [bp + 4]
A981  BA 14 00        mov dx, 0x14
A984  F7 E2           mul dx
A986  C4 3E 1B A9     les di, ptr [0xa91b]
A98A  03 F8           add di, ax
A98C  26 8A 05        mov al, byte ptr es:[di]
A98F  30 E4           xor ah, ah
A991  3B 06 36 9B     cmp ax, word ptr [0x9b36]
A995  74 04           je 0xa99b
A997  B0 00           mov al, 0
A999  EB 02           jmp 0xa99d
loc_A99B:
A99B  B0 01           mov al, 1
loc_A99D:
A99D  98              cwde
A99E  8B F8           mov di, ax
A9A0  8A 85 68 06     mov al, byte ptr [di + 0x668]
A9A4  30 E4           xor ah, ah
A9A6  01 46 FA        add word ptr [bp - 6], ax
loc_A9A9:
A9A9  8B 46 FA        mov ax, word ptr [bp - 6]
A9AC  89 46 FE        mov word ptr [bp - 2], ax
A9AF  8B 46 FE        mov ax, word ptr [bp - 2]
A9B2  89 EC           mov sp, bp
A9B4  5D              pop bp
A9B5  C2 02 00        ret 2

; ---- routine 0791:A9B8  (found by: call)
sub_A9B8:
A9B8  55              push bp
A9B9  89 E5           mov bp, sp
A9BB  81 EC 10 01     sub sp, 0x110
A9BF  8B 46 08        mov ax, word ptr [bp + 8]
A9C2  BA BF 00        mov dx, 0xbf
A9C5  F7 E2           mul dx
A9C7  C4 3E 17 A9     les di, ptr [0xa917]
A9CB  03 F8           add di, ax
A9CD  89 7E F0        mov word ptr [bp - 0x10], di
A9D0  8C 46 F2        mov word ptr [bp - 0xe], es
A9D3  31 C0           xor ax, ax
A9D5  89 46 FC        mov word ptr [bp - 4], ax
A9D8  31 C0           xor ax, ax
A9DA  89 46 F8        mov word ptr [bp - 8], ax
A9DD  8D BE F0 FE     lea di, [bp - 0x110]
A9E1  16              push ss
A9E2  57              push di
A9E3  8A 46 06        mov al, byte ptr [bp + 6]
A9E6  50              push ax
A9E7  9A 5A 07 E4 23  call far 23E4:075A
A9EC  BF CE 08        mov di, 0x8ce
A9EF  1E              push ds
A9F0  57              push di
A9F1  9A E3 06 E4 23  call far 23E4:06E3
A9F6  89 46 F4        mov word ptr [bp - 0xc], ax
A9F9  8B 46 04        mov ax, word ptr [bp + 4]
A9FC  89 46 EE        mov word ptr [bp - 0x12], ax
A9FF  B8 0C 00        mov ax, 0xc
AA02  3B 46 EE        cmp ax, word ptr [bp - 0x12]
AA05  76 03           jbe 0xaa0a
AA07  E9 CF 00        jmp 0xaad9
loc_AA0A:
AA0A  89 46 FA        mov word ptr [bp - 6], ax
AA0D  EB 03           jmp 0xaa12
loc_AA0F:
AA0F  FF 46 FA        inc word ptr [bp - 6]
loc_AA12:
AA12  8B 46 FA        mov ax, word ptr [bp - 6]
AA15  D1 E0           shl ax, 1
AA17  C4 7E F0        les di, ptr [bp - 0x10]
AA1A  03 F8           add di, ax
AA1C  26 FF 75 FE     push word ptr es:[di - 2]
AA20  9A 16 32 71 17  call far 1771:3216
AA25  08 C0           or al, al
AA27  74 03           je 0xaa2c
AA29  E9 A2 00        jmp 0xaace
loc_AA2C:
AA2C  8B 46 FA        mov ax, word ptr [bp - 6]
AA2F  D1 E0           shl ax, 1
AA31  C4 7E F0        les di, ptr [bp - 0x10]
AA34  03 F8           add di, ax
AA36  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AA3A  BA 14 00        mov dx, 0x14
AA3D  F7 E2           mul dx
AA3F  C4 3E 1B A9     les di, ptr [0xa91b]
AA43  03 F8           add di, ax
AA45  89 7E EA        mov word ptr [bp - 0x16], di
AA48  8C 46 EC        mov word ptr [bp - 0x14], es
AA4B  C4 7E EA        les di, ptr [bp - 0x16]
AA4E  26 8A 45 07     mov al, byte ptr es:[di + 7]
AA52  30 E4           xor ah, ah
AA54  8B C8           mov cx, ax
AA56  8B 46 06        mov ax, word ptr [bp + 6]
AA59  BA 0E 00        mov dx, 0xe
AA5C  F7 E2           mul dx
AA5E  8B F8           mov di, ax
AA60  03 F9           add di, cx
AA62  8A 85 D5 08     mov al, byte ptr [di + 0x8d5]
AA66  30 E4           xor ah, ah
AA68  89 46 F6        mov word ptr [bp - 0xa], ax
AA6B  83 7E F4 00     cmp word ptr [bp - 0xc], 0
AA6F  76 49           jbe 0xaaba
AA71  8B 46 FA        mov ax, word ptr [bp - 6]
AA74  D1 E0           shl ax, 1
AA76  C4 7E F0        les di, ptr [bp - 0x10]
AA79  03 F8           add di, ax
AA7B  26 FF 75 FE     push word ptr es:[di - 2]
AA7F  9A 41 30 71 17  call far 1771:3041
AA84  08 C0           or al, al
AA86  75 32           jne 0xaaba
AA88  8B 46 FA        mov ax, word ptr [bp - 6]
AA8B  D1 E0           shl ax, 1
AA8D  C4 7E F0        les di, ptr [bp - 0x10]
AA90  03 F8           add di, ax
AA92  26 FF 75 FE     push word ptr es:[di - 2]
AA96  9A 88 30 71 17  call far 1771:3088
AA9B  8A D0           mov dl, al
AA9D  83 7E F4 03     cmp word ptr [bp - 0xc], 3
AAA1  77 04           ja 0xaaa7
AAA3  B0 00           mov al, 0
AAA5  EB 02           jmp 0xaaa9
loc_AAA7:
AAA7  B0 01           mov al, 1
loc_AAA9:
AAA9  3A C2           cmp al, dl
AAAB  74 0D           je 0xaaba
AAAD  8B 46 F6        mov ax, word ptr [bp - 0xa]
AAB0  31 D2           xor dx, dx
AAB2  B9 02 00        mov cx, 2
AAB5  F7 F1           div cx
AAB7  89 46 F6        mov word ptr [bp - 0xa], ax
loc_AABA:
AABA  8B 46 F6        mov ax, word ptr [bp - 0xa]
AABD  3B 46 F8        cmp ax, word ptr [bp - 8]
AAC0  76 0C           jbe 0xaace
AAC2  8B 46 FA        mov ax, word ptr [bp - 6]
AAC5  89 46 FC        mov word ptr [bp - 4], ax
AAC8  8B 46 F6        mov ax, word ptr [bp - 0xa]
AACB  89 46 F8        mov word ptr [bp - 8], ax
loc_AACE:
AACE  8B 46 FA        mov ax, word ptr [bp - 6]
AAD1  3B 46 EE        cmp ax, word ptr [bp - 0x12]
AAD4  74 03           je 0xaad9
AAD6  E9 36 FF        jmp 0xaa0f
loc_AAD9:
AAD9  8B 46 FC        mov ax, word ptr [bp - 4]
AADC  89 46 FE        mov word ptr [bp - 2], ax
AADF  8B 46 FE        mov ax, word ptr [bp - 2]
AAE2  89 EC           mov sp, bp
AAE4  5D              pop bp
AAE5  C2 06 00        ret 6

; ---- routine 0791:AAE8  (found by: call)
sub_AAE8:
AAE8  55              push bp
AAE9  89 E5           mov bp, sp
AAEB  81 EC 12 01     sub sp, 0x112
AAEF  8B 46 08        mov ax, word ptr [bp + 8]
AAF2  BA 14 00        mov dx, 0x14
AAF5  F7 E2           mul dx
AAF7  C4 3E 1B A9     les di, ptr [0xa91b]
AAFB  03 F8           add di, ax
AAFD  89 7E EF        mov word ptr [bp - 0x11], di
AB00  8C 46 F1        mov word ptr [bp - 0xf], es
AB03  C4 7E EF        les di, ptr [bp - 0x11]
AB06  26 8A 45 06     mov al, byte ptr es:[di + 6]
AB0A  30 E4           xor ah, ah
AB0C  8B F8           mov di, ax
AB0E  B1 03           mov cl, 3
AB10  D3 E7           shl di, cl
AB12  8D 85 9A 09     lea ax, [di + 0x99a]
AB16  8C DA           mov dx, ds
AB18  89 46 FA        mov word ptr [bp - 6], ax
AB1B  89 56 FC        mov word ptr [bp - 4], dx
AB1E  31 C0           xor ax, ax
AB20  89 46 F6        mov word ptr [bp - 0xa], ax
AB23  8D BE EF FE     lea di, [bp - 0x111]
AB27  16              push ss
AB28  57              push di
AB29  C4 7E EF        les di, ptr [bp - 0x11]
AB2C  26 8A 45 06     mov al, byte ptr es:[di + 6]
AB30  50              push ax
AB31  9A 5A 07 E4 23  call far 23E4:075A
AB36  BF CE 08        mov di, 0x8ce
AB39  1E              push ds
AB3A  57              push di
AB3B  9A E3 06 E4 23  call far 23E4:06E3
AB40  89 46 F4        mov word ptr [bp - 0xc], ax
AB43  83 7E F4 00     cmp word ptr [bp - 0xc], 0
AB47  77 03           ja 0xab4c
AB49  E9 BB 00        jmp 0xac07
loc_AB4C:
AB4C  83 7E F4 03     cmp word ptr [bp - 0xc], 3
AB50  77 04           ja 0xab56
AB52  B0 00           mov al, 0
AB54  EB 02           jmp 0xab58
loc_AB56:
AB56  B0 01           mov al, 1
loc_AB58:
AB58  88 46 F3        mov byte ptr [bp - 0xd], al
AB5B  C4 7E FA        les di, ptr [bp - 6]
AB5E  26 8A 05        mov al, byte ptr es:[di]
AB61  30 E4           xor ah, ah
AB63  89 46 ED        mov word ptr [bp - 0x13], ax
AB66  B8 01 00        mov ax, 1
AB69  3B 46 ED        cmp ax, word ptr [bp - 0x13]
AB6C  76 03           jbe 0xab71
AB6E  E9 94 00        jmp 0xac05
loc_AB71:
AB71  89 46 F8        mov word ptr [bp - 8], ax
AB74  EB 03           jmp 0xab79
loc_AB76:
AB76  FF 46 F8        inc word ptr [bp - 8]
loc_AB79:
AB79  8B 46 F8        mov ax, word ptr [bp - 8]
AB7C  C4 7E FA        les di, ptr [bp - 6]
AB7F  03 F8           add di, ax
AB81  26 8A 05        mov al, byte ptr es:[di]
AB84  30 E4           xor ah, ah
AB86  8B F8           mov di, ax
AB88  80 BD A2 99 00  cmp byte ptr [di - 0x665e], 0
AB8D  74 6B           je 0xabfa
AB8F  8B 46 F8        mov ax, word ptr [bp - 8]
AB92  C4 7E FA        les di, ptr [bp - 6]
AB95  03 F8           add di, ax
AB97  26 8A 05        mov al, byte ptr es:[di]
AB9A  30 E4           xor ah, ah
AB9C  8B F8           mov di, ax
AB9E  8A 85 A2 99     mov al, byte ptr [di - 0x665e]
ABA2  30 E4           xor ah, ah
ABA4  D1 E0           shl ax, 1
ABA6  C4 7E 04        les di, ptr [bp + 4]
ABA9  03 F8           add di, ax
ABAB  26 FF 75 FE     push word ptr es:[di - 2]
ABAF  9A 41 30 71 17  call far 1771:3041
ABB4  08 C0           or al, al
ABB6  75 2A           jne 0xabe2
ABB8  8B 46 F8        mov ax, word ptr [bp - 8]
ABBB  C4 7E FA        les di, ptr [bp - 6]
ABBE  03 F8           add di, ax
ABC0  26 8A 05        mov al, byte ptr es:[di]
ABC3  30 E4           xor ah, ah
ABC5  8B F8           mov di, ax
ABC7  8A 85 A2 99     mov al, byte ptr [di - 0x665e]
ABCB  30 E4           xor ah, ah
ABCD  D1 E0           shl ax, 1
ABCF  C4 7E 04        les di, ptr [bp + 4]
ABD2  03 F8           add di, ax
ABD4  26 FF 75 FE     push word ptr es:[di - 2]
ABD8  9A 88 30 71 17  call far 1771:3088
ABDD  3A 46 F3        cmp al, byte ptr [bp - 0xd]
ABE0  75 18           jne 0xabfa
loc_ABE2:
ABE2  8B 46 F8        mov ax, word ptr [bp - 8]
ABE5  C4 7E FA        les di, ptr [bp - 6]
ABE8  03 F8           add di, ax
ABEA  26 8A 05        mov al, byte ptr es:[di]
ABED  30 E4           xor ah, ah
ABEF  8B F8           mov di, ax
ABF1  8A 85 A2 99     mov al, byte ptr [di - 0x665e]
ABF5  30 E4           xor ah, ah
ABF7  89 46 F6        mov word ptr [bp - 0xa], ax
loc_ABFA:
ABFA  8B 46 F8        mov ax, word ptr [bp - 8]
ABFD  3B 46 ED        cmp ax, word ptr [bp - 0x13]
AC00  74 03           je 0xac05
AC02  E9 71 FF        jmp 0xab76
loc_AC05:
AC05  EB 51           jmp 0xac58
loc_AC07:
AC07  C4 7E FA        les di, ptr [bp - 6]
AC0A  26 8A 05        mov al, byte ptr es:[di]
AC0D  30 E4           xor ah, ah
AC0F  89 46 ED        mov word ptr [bp - 0x13], ax
AC12  B8 01 00        mov ax, 1
AC15  3B 46 ED        cmp ax, word ptr [bp - 0x13]
AC18  77 3E           ja 0xac58
AC1A  89 46 F8        mov word ptr [bp - 8], ax
AC1D  EB 03           jmp 0xac22
loc_AC1F:
AC1F  FF 46 F8        inc word ptr [bp - 8]
loc_AC22:
AC22  8B 46 F8        mov ax, word ptr [bp - 8]
AC25  C4 7E FA        les di, ptr [bp - 6]
AC28  03 F8           add di, ax
AC2A  26 8A 05        mov al, byte ptr es:[di]
AC2D  30 E4           xor ah, ah
AC2F  8B F8           mov di, ax
AC31  80 BD A2 99 00  cmp byte ptr [di - 0x665e], 0
AC36  74 18           je 0xac50
AC38  8B 46 F8        mov ax, word ptr [bp - 8]
AC3B  C4 7E FA        les di, ptr [bp - 6]
AC3E  03 F8           add di, ax
AC40  26 8A 05        mov al, byte ptr es:[di]
AC43  30 E4           xor ah, ah
AC45  8B F8           mov di, ax
AC47  8A 85 A2 99     mov al, byte ptr [di - 0x665e]
AC4B  30 E4           xor ah, ah
AC4D  89 46 F6        mov word ptr [bp - 0xa], ax
loc_AC50:
AC50  8B 46 F8        mov ax, word ptr [bp - 8]
AC53  3B 46 ED        cmp ax, word ptr [bp - 0x13]
AC56  75 C7           jne 0xac1f
loc_AC58:
AC58  8B 46 F6        mov ax, word ptr [bp - 0xa]
AC5B  89 46 FE        mov word ptr [bp - 2], ax
AC5E  8B 46 FE        mov ax, word ptr [bp - 2]
AC61  89 EC           mov sp, bp
AC63  5D              pop bp
AC64  C2 06 00        ret 6

; ---- routine 0791:AC67  (found by: call)
sub_AC67:
AC67  55              push bp
AC68  89 E5           mov bp, sp
AC6A  83 EC 0A        sub sp, 0xa
AC6D  8B 7E 04        mov di, word ptr [bp + 4]
AC70  36 8B 45 06     mov ax, word ptr ss:[di + 6]
AC74  BA BF 00        mov dx, 0xbf
AC77  F7 E2           mul dx
AC79  C4 3E 17 A9     les di, ptr [0xa917]
AC7D  03 F8           add di, ax
AC7F  89 7E FA        mov word ptr [bp - 6], di
AC82  8C 46 FC        mov word ptr [bp - 4], es
AC85  8B 46 06        mov ax, word ptr [bp + 6]
AC88  D1 E0           shl ax, 1
AC8A  C4 7E FA        les di, ptr [bp - 6]
AC8D  03 F8           add di, ax
AC8F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
AC93  89 46 FE        mov word ptr [bp - 2], ax
AC96  8B 46 FE        mov ax, word ptr [bp - 2]
AC99  BA 14 00        mov dx, 0x14
AC9C  F7 E2           mul dx
AC9E  C4 3E 1B A9     les di, ptr [0xa91b]
ACA2  03 F8           add di, ax
ACA4  89 7E F6        mov word ptr [bp - 0xa], di
ACA7  8C 46 F8        mov word ptr [bp - 8], es
ACAA  FF 76 FE        push word ptr [bp - 2]
ACAD  9A 16 32 71 17  call far 1771:3216
ACB2  08 C0           or al, al
ACB4  75 53           jne 0xad09
ACB6  C4 7E F6        les di, ptr [bp - 0xa]
ACB9  26 8A 45 07     mov al, byte ptr es:[di + 7]
ACBD  30 E4           xor ah, ah
ACBF  8B F8           mov di, ax
ACC1  80 BD A2 99 00  cmp byte ptr [di - 0x665e], 0
ACC6  74 2F           je 0xacf7
ACC8  C4 7E F6        les di, ptr [bp - 0xa]
ACCB  26 8A 45 07     mov al, byte ptr es:[di + 7]
ACCF  30 E4           xor ah, ah
ACD1  8B F8           mov di, ax
ACD3  8A 85 A2 99     mov al, byte ptr [di - 0x665e]
ACD7  30 E4           xor ah, ah
ACD9  D1 E0           shl ax, 1
ACDB  C4 7E FA        les di, ptr [bp - 6]
ACDE  03 F8           add di, ax
ACE0  26 FF 75 FE     push word ptr es:[di - 2]
ACE4  9A 7E 37 71 17  call far 1771:377E
ACE9  50              push ax
ACEA  FF 76 FE        push word ptr [bp - 2]
ACED  9A 7E 37 71 17  call far 1771:377E
ACF2  5A              pop dx
ACF3  3B C2           cmp ax, dx
ACF5  76 12           jbe 0xad09
loc_ACF7:
ACF7  8A 56 06        mov dl, byte ptr [bp + 6]
ACFA  C4 7E F6        les di, ptr [bp - 0xa]
ACFD  26 8A 45 07     mov al, byte ptr es:[di + 7]
AD01  30 E4           xor ah, ah
AD03  8B F8           mov di, ax
AD05  88 95 A2 99     mov byte ptr [di - 0x665e], dl
loc_AD09:
AD09  89 EC           mov sp, bp
AD0B  5D              pop bp
AD0C  C2 04 00        ret 4
; data (not reached as code), 128 bytes
AD0F                  db 60 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; `...............
AD1F                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
AD2F                  db 80 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
AD3F                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
AD4F                  db 00 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
AD5F                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
AD6F                  db 00 30 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; .0..............
AD7F                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

