; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 14 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:82EB  (found by: call)
sub_82EB:
82EB  55              push bp
82EC  89 E5           mov bp, sp
82EE  A0 0E 83        mov al, byte ptr [0x830e]
82F1  A2 0C 83        mov byte ptr [0x830c], al
82F4  C6 06 0D 83 00  mov byte ptr [0x830d], 0
82F9  B0 36           mov al, 0x36
82FB  50              push ax
82FC  E8 D5 A7        call 0x2ad4
82FF  A0 0C 83        mov al, byte ptr [0x830c]
8302  30 E4           xor ah, ah
8304  BA 16 00        mov dx, 0x16
8307  F7 E2           mul dx
8309  8B F8           mov di, ax
830B  81 C7 E8 80     add di, 0x80e8
830F  1E              push ds
8310  57              push di
8311  0E              push cs
8312  E8 D0 A8        call 0x2be5
8315  08 C0           or al, al
8317  7C 04           jl 0x831d
8319  B0 00           mov al, 0
831B  EB 02           jmp 0x831f
loc_831D:
831D  B0 01           mov al, 1
loc_831F:
831F  50              push ax
8320  E8 7D A3        call 0x26a0
8323  B0 00           mov al, 0
8325  50              push ax
8326  E8 37 FB        call 0x7e60
8329  A1 17 83        mov ax, word ptr [0x8317]
832C  A3 F6 82        mov word ptr [0x82f6], ax
832F  80 3E 0C 83 0C  cmp byte ptr [0x830c], 0xc
8334  72 04           jb 0x833a
8336  B0 00           mov al, 0
8338  EB 02           jmp 0x833c
loc_833A:
833A  B0 01           mov al, 1
loc_833C:
833C  98              cwde
833D  8B F8           mov di, ax
833F  8A 85 20 79     mov al, byte ptr [di + 0x7920]
8343  98              cwde
8344  B9 0B 00        mov cx, 0xb
8347  F7 E9           imul cx
8349  8B D0           mov dx, ax
834B  A0 0C 83        mov al, byte ptr [0x830c]
834E  30 E4           xor ah, ah
8350  03 C2           add ax, dx
8352  A2 0B 83        mov byte ptr [0x830b], al
8355  E8 59 AC        call 0x2fb1
8358  E8 5B EC        call 0x6fb6
835B  89 EC           mov sp, bp
835D  5D              pop bp
835E  C3              ret

; ---- routine 0791:835F  (found by: call)
sub_835F:
835F  55              push bp
8360  89 E5           mov bp, sp
8362  83 EC 02        sub sp, 2
8365  C4 7E 06        les di, ptr [bp + 6]
8368  26 8B 45 06     mov ax, word ptr es:[di + 6]
836C  09 C0           or ax, ax
836E  79 02           jns 0x8372
8370  F7 D8           neg ax
loc_8372:
8372  8B D0           mov dx, ax
8374  C4 7E 06        les di, ptr [bp + 6]
8377  26 8B 45 08     mov ax, word ptr es:[di + 8]
837B  09 C0           or ax, ax
837D  79 02           jns 0x8381
837F  F7 D8           neg ax
loc_8381:
8381  03 C2           add ax, dx
8383  99              cdq
8384  8B C8           mov cx, ax
8386  8B DA           mov bx, dx
8388  C4 7E 06        les di, ptr [bp + 6]
838B  26 8B 45 0A     mov ax, word ptr es:[di + 0xa]
838F  31 D2           xor dx, dx
8391  9A 79 02 E4 23  call far 23E4:0279
8396  89 46 FE        mov word ptr [bp - 2], ax
8399  8B 46 FE        mov ax, word ptr [bp - 2]
839C  89 EC           mov sp, bp
839E  5D              pop bp
839F  CA 04 00        retf 4

; ---- routine 0791:83A2  (found by: call)
sub_83A2:
83A2  55              push bp
83A3  89 E5           mov bp, sp
83A5  83 EC 04        sub sp, 4
83A8  C4 7E 06        les di, ptr [bp + 6]
83AB  26 8B 05        mov ax, word ptr es:[di]
83AE  89 46 FE        mov word ptr [bp - 2], ax
83B1  C4 7E 06        les di, ptr [bp + 6]
83B4  26 8A 45 06     mov al, byte ptr es:[di + 6]
83B8  00 46 FE        add byte ptr [bp - 2], al
83BB  C4 7E 06        les di, ptr [bp + 6]
83BE  26 8A 45 08     mov al, byte ptr es:[di + 8]
83C2  00 46 FF        add byte ptr [bp - 1], al
83C5  C4 7E 06        les di, ptr [bp + 6]
83C8  26 83 7D 0A 00  cmp word ptr es:[di + 0xa], 0
83CD  76 07           jbe 0x83d6
83CF  C4 7E 06        les di, ptr [bp + 6]
83D2  26 FF 4D 0A     dec word ptr es:[di + 0xa]
loc_83D6:
83D6  C4 7E 06        les di, ptr [bp + 6]
83D9  26 80 7D 0D 00  cmp byte ptr es:[di + 0xd], 0
83DE  74 0E           je 0x83ee
83E0  C4 7E 06        les di, ptr [bp + 6]
83E3  06              push es
83E4  57              push di
83E5  0E              push cs
83E6  E8 76 FF        call 0x835f
83E9  3D 02 00        cmp ax, 2
83EC  77 04           ja 0x83f2
loc_83EE:
83EE  B0 00           mov al, 0
83F0  EB 02           jmp 0x83f4
loc_83F2:
83F2  B0 01           mov al, 1
loc_83F4:
83F4  C4 7E 06        les di, ptr [bp + 6]
83F7  26 88 45 0D     mov byte ptr es:[di + 0xd], al
83FB  FF 76 FE        push word ptr [bp - 2]
83FE  E8 FF A9        call 0x2e00
8401  08 C0           or al, al
8403  74 09           je 0x840e
8405  8B 46 FE        mov ax, word ptr [bp - 2]
8408  C4 7E 06        les di, ptr [bp + 6]
840B  26 89 05        mov word ptr es:[di], ax
loc_840E:
840E  C4 7E 06        les di, ptr [bp + 6]
8411  06              push es
8412  57              push di
8413  0E              push cs
8414  E8 F9 0A        call 0x8f10
8417  C4 7E 06        les di, ptr [bp + 6]
841A  26 FF 35        push word ptr es:[di]
841D  E8 AA A9        call 0x2dca
8420  08 C0           or al, al
8422  74 03           je 0x8427
8424  E9 0A 01        jmp 0x8531
loc_8427:
8427  B8 02 00        mov ax, 2
842A  50              push ax
842B  E8 13 80        call 0x441
842E  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
8433  76 3F           jbe 0x8474
8435  C4 7E 06        les di, ptr [bp + 6]
8438  26 8A 05        mov al, byte ptr es:[di]
843B  98              cwde
843C  09 C0           or ax, ax
843E  79 02           jns 0x8442
8440  F7 D8           neg ax
loc_8442:
8442  3D 01 00        cmp ax, 1
8445  7F 27           jg 0x846e
8447  A0 0B 83        mov al, byte ptr [0x830b]
844A  30 E4           xor ah, ah
844C  BA 16 00        mov dx, 0x16
844F  F7 E2           mul dx
8451  8B F8           mov di, ax
8453  81 C7 E8 80     add di, 0x80e8
8457  1E              push ds
8458  57              push di
8459  0E              push cs
845A  E8 88 A7        call 0x2be5
845D  98              cwde
845E  8B D0           mov dx, ax
8460  C4 7E 06        les di, ptr [bp + 6]
8463  26 8A 45 01     mov al, byte ptr es:[di + 1]
8467  98              cwde
8468  F7 EA           imul dx
846A  09 C0           or ax, ax
846C  7D 06           jge 0x8474
loc_846E:
846E  E8 7A FE        call 0x82eb
8471  E9 BD 00        jmp 0x8531
loc_8474:
8474  C6 06 0C 83 00  mov byte ptr [0x830c], 0
8479  C6 06 0A 83 00  mov byte ptr [0x830a], 0
847E  C6 06 0D 83 00  mov byte ptr [0x830d], 0
8483  C6 06 25 83 00  mov byte ptr [0x8325], 0
8488  C4 7E 06        les di, ptr [bp + 6]
848B  26 8A 05        mov al, byte ptr es:[di]
848E  98              cwde
848F  09 C0           or ax, ax
8491  79 02           jns 0x8495
8493  F7 D8           neg ax
loc_8495:
8495  3D 01 00        cmp ax, 1
8498  7F 31           jg 0x84cb
849A  A0 0B 83        mov al, byte ptr [0x830b]
849D  30 E4           xor ah, ah
849F  BA 16 00        mov dx, 0x16
84A2  F7 E2           mul dx
84A4  8B F8           mov di, ax
84A6  81 C7 E8 80     add di, 0x80e8
84AA  1E              push ds
84AB  57              push di
84AC  0E              push cs
84AD  E8 35 A7        call 0x2be5
84B0  98              cwde
84B1  8B D0           mov dx, ax
84B3  C4 7E 06        les di, ptr [bp + 6]
84B6  26 8A 45 01     mov al, byte ptr es:[di + 1]
84BA  98              cwde
84BB  F7 EA           imul dx
84BD  09 C0           or ax, ax
84BF  7D 05           jge 0x84c6
84C1  E8 CA E4        call 0x698e
84C4  EB 03           jmp 0x84c9
loc_84C6:
84C6  E8 43 E4        call 0x690c
loc_84C9:
84C9  EB 58           jmp 0x8523
loc_84CB:
84CB  C4 7E 06        les di, ptr [bp + 6]
84CE  26 8A 45 01     mov al, byte ptr es:[di + 1]
84D2  98              cwde
84D3  09 C0           or ax, ax
84D5  79 02           jns 0x84d9
84D7  F7 D8           neg ax
loc_84D9:
84D9  3D 26 00        cmp ax, 0x26
84DC  7D 05           jge 0x84e3
84DE  E8 30 E9        call 0x6e11
84E1  EB 40           jmp 0x8523
loc_84E3:
84E3  A0 0B 83        mov al, byte ptr [0x830b]
84E6  30 E4           xor ah, ah
84E8  BA 16 00        mov dx, 0x16
84EB  F7 E2           mul dx
84ED  8B F8           mov di, ax
84EF  81 C7 E8 80     add di, 0x80e8
84F3  1E              push ds
84F4  57              push di
84F5  0E              push cs
84F6  E8 EC A6        call 0x2be5
84F9  98              cwde
84FA  8B D0           mov dx, ax
84FC  C4 7E 06        les di, ptr [bp + 6]
84FF  26 8A 45 01     mov al, byte ptr es:[di + 1]
8503  98              cwde
8504  F7 EA           imul dx
8506  09 C0           or ax, ax
8508  7D 05           jge 0x850f
850A  E8 61 E9        call 0x6e6e
850D  EB 14           jmp 0x8523
loc_850F:
850F  E8 84 A4        call 0x2996
8512  08 C0           or al, al
8514  74 04           je 0x851a
8516  B0 00           mov al, 0
8518  EB 02           jmp 0x851c
loc_851A:
851A  B0 01           mov al, 1
loc_851C:
851C  50              push ax
851D  B0 00           mov al, 0
851F  50              push ax
8520  E8 DE E9        call 0x6f01
loc_8523:
8523  C4 7E 06        les di, ptr [bp + 6]
8526  31 C0           xor ax, ax
8528  26 89 45 0A     mov word ptr es:[di + 0xa], ax
852C  C6 06 27 83 00  mov byte ptr [0x8327], 0
loc_8531:
8531  89 EC           mov sp, bp
8533  5D              pop bp
8534  CA 04 00        retf 4

; ---- routine 0791:8537  (found by: call)
sub_8537:
8537  55              push bp
8538  89 E5           mov bp, sp
853A  C4 7E 06        les di, ptr [bp + 6]
853D  26 8B 45 02     mov ax, word ptr es:[di + 2]
8541  3B 06 40 06     cmp ax, word ptr [0x640]
8545  74 5B           je 0x85a2
8547  C4 7E 06        les di, ptr [bp + 6]
854A  26 8B 45 02     mov ax, word ptr es:[di + 2]
854E  C4 7E 06        les di, ptr [bp + 6]
8551  26 3B 05        cmp ax, word ptr es:[di]
8554  74 4C           je 0x85a2
8556  C4 7E 06        les di, ptr [bp + 6]
8559  26 8A 45 03     mov al, byte ptr es:[di + 3]
855D  98              cwde
855E  D1 E0           shl ax, 1
8560  8B C8           mov cx, ax
8562  C4 7E 06        les di, ptr [bp + 6]
8565  26 8A 45 02     mov al, byte ptr es:[di + 2]
8569  98              cwde
856A  BA A0 00        mov dx, 0xa0
856D  F7 E2           mul dx
856F  C4 3E 1E 7C     les di, ptr [0x7c1e]
8573  03 F8           add di, ax
8575  03 F9           add di, cx
8577  26 8B 9D 0E 09  mov bx, word ptr es:[di + 0x90e]
857C  C4 7E 06        les di, ptr [bp + 6]
857F  26 8A 45 03     mov al, byte ptr es:[di + 3]
8583  98              cwde
8584  D1 E0           shl ax, 1
8586  8B C8           mov cx, ax
8588  C4 7E 06        les di, ptr [bp + 6]
858B  26 8A 45 02     mov al, byte ptr es:[di + 2]
858F  98              cwde
8590  BA A0 00        mov dx, 0xa0
8593  F7 E2           mul dx
8595  C4 3E 16 7C     les di, ptr [0x7c16]
8599  03 F8           add di, ax
859B  03 F9           add di, cx
859D  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_85A2:
85A2  C4 7E 06        les di, ptr [bp + 6]
85A5  26 8B 05        mov ax, word ptr es:[di]
85A8  C4 7E 06        les di, ptr [bp + 6]
85AB  26 89 45 02     mov word ptr es:[di + 2], ax
85AF  C4 7E 06        les di, ptr [bp + 6]
85B2  26 8B 05        mov ax, word ptr es:[di]
85B5  3B 06 40 06     cmp ax, word ptr [0x640]
85B9  74 4C           je 0x8607
85BB  C4 7E 06        les di, ptr [bp + 6]
85BE  26 80 7D 04 01  cmp byte ptr es:[di + 4], 1
85C3  75 0C           jne 0x85d1
85C5  A0 0B 83        mov al, byte ptr [0x830b]
85C8  C4 7E 06        les di, ptr [bp + 6]
85CB  26 3A 45 06     cmp al, byte ptr es:[di + 6]
85CF  74 04           je 0x85d5
loc_85D1:
85D1  B0 00           mov al, 0
85D3  EB 02           jmp 0x85d7
loc_85D5:
85D5  B0 01           mov al, 1
loc_85D7:
85D7  30 E4           xor ah, ah
85D9  C4 7E 06        les di, ptr [bp + 6]
85DC  26 03 45 04     add ax, word ptr es:[di + 4]
85E0  8B D8           mov bx, ax
85E2  C4 7E 06        les di, ptr [bp + 6]
85E5  26 8A 45 01     mov al, byte ptr es:[di + 1]
85E9  98              cwde
85EA  D1 E0           shl ax, 1
85EC  8B C8           mov cx, ax
85EE  C4 7E 06        les di, ptr [bp + 6]
85F1  26 8A 05        mov al, byte ptr es:[di]
85F4  98              cwde
85F5  BA A0 00        mov dx, 0xa0
85F8  F7 E2           mul dx
85FA  C4 3E 16 7C     les di, ptr [0x7c16]
85FE  03 F8           add di, ax
8600  03 F9           add di, cx
8602  26 89 9D 0E 09  mov word ptr es:[di + 0x90e], bx
loc_8607:
8607  C4 7E 06        les di, ptr [bp + 6]
860A  06              push es
860B  57              push di
860C  0E              push cs
860D  E8 19 A6        call 0x2c29
8610  08 C0           or al, al
8612  75 03           jne 0x8617
8614  E9 82 00        jmp 0x8699
loc_8617:
8617  C4 7E 06        les di, ptr [bp + 6]
861A  26 8B 05        mov ax, word ptr es:[di]
861D  A3 F6 82        mov word ptr [0x82f6], ax
8620  C4 7E 06        les di, ptr [bp + 6]
8623  26 8A 45 06     mov al, byte ptr es:[di + 6]
8627  30 E4           xor ah, ah
8629  50              push ax
862A  E8 30 7E        call 0x1045d
862D  08 C0           or al, al
862F  74 13           je 0x8644
8631  C4 7E 06        les di, ptr [bp + 6]
8634  26 FF 35        push word ptr es:[di]
8637  C4 7E 06        les di, ptr [bp + 6]
863A  06              push es
863B  57              push di
863C  0E              push cs
863D  E8 78 A8        call 0x2eb8
8640  08 C0           or al, al
8642  75 4C           jne 0x8690
loc_8644:
8644  C4 7E 06        les di, ptr [bp + 6]
8647  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
864B  3C 01           cmp al, 1
864D  74 08           je 0x8657
864F  3C 02           cmp al, 2
8651  74 04           je 0x8657
8653  3C 05           cmp al, 5
8655  75 0F           jne 0x8666
loc_8657:
8657  C4 7E 06        les di, ptr [bp + 6]
865A  06              push es
865B  57              push di
865C  0E              push cs
865D  E8 85 A5        call 0x2be5
8660  00 06 F7 82     add byte ptr [0x82f7], al
8664  EB 12           jmp 0x8678
loc_8666:
8666  3C 03           cmp al, 3
8668  75 06           jne 0x8670
866A  FE 0E F7 82     dec byte ptr [0x82f7]
866E  EB 08           jmp 0x8678
loc_8670:
8670  3C 04           cmp al, 4
8672  75 04           jne 0x8678
8674  FE 06 F7 82     inc byte ptr [0x82f7]
loc_8678:
8678  80 3E F7 82 26  cmp byte ptr [0x82f7], 0x26
867D  75 05           jne 0x8684
867F  C6 06 F7 82 24  mov byte ptr [0x82f7], 0x24
loc_8684:
8684  80 3E F7 82 DA  cmp byte ptr [0x82f7], 0xda
8689  75 05           jne 0x8690
868B  C6 06 F7 82 DC  mov byte ptr [0x82f7], 0xdc
loc_8690:
8690  BF F6 82        mov di, 0x82f6
8693  1E              push ds
8694  57              push di
8695  0E              push cs
8696  E8 77 08        call 0x8f10
loc_8699:
8699  89 EC           mov sp, bp
869B  5D              pop bp
869C  CA 04 00        retf 4

; ---- routine 0791:869F  (found by: call)
sub_869F:
869F  55              push bp
86A0  89 E5           mov bp, sp
86A2  C4 7E 06        les di, ptr [bp + 6]
86A5  26 8A 45 06     mov al, byte ptr es:[di + 6]
86A9  A2 0B 83        mov byte ptr [0x830b], al
86AC  31 C0           xor ax, ax
86AE  A3 00 83        mov word ptr [0x8300], ax
86B1  C6 06 0C 83 00  mov byte ptr [0x830c], 0
86B6  C6 06 0D 83 00  mov byte ptr [0x830d], 0
86BB  C6 06 02 83 00  mov byte ptr [0x8302], 0
86C0  C6 06 03 83 00  mov byte ptr [0x8303], 0
86C5  C6 06 27 83 00  mov byte ptr [0x8327], 0
86CA  89 EC           mov sp, bp
86CC  5D              pop bp
86CD  CA 04 00        retf 4

; ---- routine 0791:86D0  (found by: call)
sub_86D0:
86D0  55              push bp
86D1  89 E5           mov bp, sp
86D3  83 EC 02        sub sp, 2
86D6  8B 7E 04        mov di, word ptr [bp + 4]
86D9  36 8B 7D 04     mov di, word ptr ss:[di + 4]
86DD  36 C4 7D 06     les di, ptr ss:[di + 6]
86E1  26 8B 45 02     mov ax, word ptr es:[di + 2]
86E5  8B 7E 04        mov di, word ptr [bp + 4]
86E8  36 8B 7D 04     mov di, word ptr ss:[di + 4]
86EC  36 C4 7D 06     les di, ptr ss:[di + 6]
86F0  26 89 05        mov word ptr es:[di], ax
86F3  8B 7E 04        mov di, word ptr [bp + 4]
86F6  36 8B 7D 04     mov di, word ptr ss:[di + 4]
86FA  36 C4 7D 06     les di, ptr ss:[di + 6]
86FE  26 8A 45 0F     mov al, byte ptr es:[di + 0xf]
8702  3C 01           cmp al, 1
8704  75 10           jne 0x8716
8706  8B 7E 04        mov di, word ptr [bp + 4]
8709  36 8B 7D 04     mov di, word ptr ss:[di + 4]
870D  36 C4 7D 06     les di, ptr ss:[di + 6]
8711  26 FE 0D        dec byte ptr es:[di]
8714  EB 3C           jmp 0x8752
loc_8716:
8716  3C 02           cmp al, 2
8718  75 10           jne 0x872a
871A  8B 7E 04        mov di, word ptr [bp + 4]
871D  36 8B 7D 04     mov di, word ptr ss:[di + 4]
8721  36 C4 7D 06     les di, ptr ss:[di + 6]
8725  26 FE 05        inc byte ptr es:[di]
8728  EB 28           jmp 0x8752
loc_872A:
872A  3C 03           cmp al, 3
872C  75 11           jne 0x873f
872E  8B 7E 04        mov di, word ptr [bp + 4]
8731  36 8B 7D 04     mov di, word ptr ss:[di + 4]
8735  36 C4 7D 06     les di, ptr ss:[di + 6]
8739  26 FE 4D 01     dec byte ptr es:[di + 1]
873D  EB 13           jmp 0x8752
loc_873F:
873F  3C 04           cmp al, 4
8741  75 0F           jne 0x8752
8743  8B 7E 04        mov di, word ptr [bp + 4]
8746  36 8B 7D 04     mov di, word ptr ss:[di + 4]
874A  36 C4 7D 06     les di, ptr ss:[di + 6]
874E  26 FE 45 01     inc byte ptr es:[di + 1]
loc_8752:
8752  8B 7E 04        mov di, word ptr [bp + 4]
8755  36 8B 7D 04     mov di, word ptr ss:[di + 4]
8759  36 C4 7D 06     les di, ptr ss:[di + 6]
875D  26 80 7D 0F 05  cmp byte ptr es:[di + 0xf], 5
8762  75 03           jne 0x8767
8764  E9 F4 00        jmp 0x885b
loc_8767:
8767  8B 7E 04        mov di, word ptr [bp + 4]
876A  36 8B 7D 04     mov di, word ptr ss:[di + 4]
876E  36 C4 7D 06     les di, ptr ss:[di + 6]
8772  26 FF 35        push word ptr es:[di]
8775  E8 52 A6        call 0x2dca
8778  08 C0           or al, al
877A  75 03           jne 0x877f
877C  E9 D8 00        jmp 0x8857
loc_877F:
877F  80 3E 25 83 00  cmp byte ptr [0x8325], 0
8784  75 03           jne 0x8789
8786  E9 D2 00        jmp 0x885b
loc_8789:
8789  8B 7E 04        mov di, word ptr [bp + 4]
878C  36 8B 7D 04     mov di, word ptr ss:[di + 4]
8790  36 C4 7D 06     les di, ptr ss:[di + 6]
8794  26 8A 45 06     mov al, byte ptr es:[di + 6]
8798  3A 06 0C 83     cmp al, byte ptr [0x830c]
879C  75 03           jne 0x87a1
879E  E9 BA 00        jmp 0x885b
loc_87A1:
87A1  8B 7E 04        mov di, word ptr [bp + 4]
87A4  36 8B 7D 04     mov di, word ptr ss:[di + 4]
87A8  36 C4 7D 06     les di, ptr ss:[di + 6]
87AC  26 8A 45 06     mov al, byte ptr es:[di + 6]
87B0  3A 06 0B 83     cmp al, byte ptr [0x830b]
87B4  75 03           jne 0x87b9
87B6  E9 A2 00        jmp 0x885b
loc_87B9:
87B9  8B 7E 04        mov di, word ptr [bp + 4]
87BC  36 8B 7D 04     mov di, word ptr ss:[di + 4]
87C0  36 C4 7D 06     les di, ptr ss:[di + 6]
87C4  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
87C8  BA 14 00        mov dx, 0x14
87CB  F7 E2           mul dx
87CD  C4 3E 1B A9     les di, ptr [0xa91b]
87D1  03 F8           add di, ax
87D3  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
87D8  75 03           jne 0x87dd
87DA  E9 7E 00        jmp 0x885b
loc_87DD:
87DD  8B 7E 04        mov di, word ptr [bp + 4]
87E0  36 8B 7D 04     mov di, word ptr ss:[di + 4]
87E4  36 C4 7D 06     les di, ptr ss:[di + 6]
87E8  26 8A 45 01     mov al, byte ptr es:[di + 1]
87EC  98              cwde
87ED  D1 E0           shl ax, 1
87EF  8B C8           mov cx, ax
87F1  8B 7E 04        mov di, word ptr [bp + 4]
87F4  36 8B 7D 04     mov di, word ptr ss:[di + 4]
87F8  36 C4 7D 06     les di, ptr ss:[di + 6]
87FC  26 8A 05        mov al, byte ptr es:[di]
87FF  98              cwde
8800  BA A0 00        mov dx, 0xa0
8803  F7 E2           mul dx
8805  C4 3E 16 7C     les di, ptr [0x7c16]
8809  03 F8           add di, ax
880B  03 F9           add di, cx
880D  26 80 BD 0F 09 0D cmp byte ptr es:[di + 0x90f], 0xd
8813  74 46           je 0x885b
8815  8B 7E 04        mov di, word ptr [bp + 4]
8818  36 8B 7D 04     mov di, word ptr ss:[di + 4]
881C  36 C4 7D 06     les di, ptr ss:[di + 6]
8820  26 8A 45 01     mov al, byte ptr es:[di + 1]
8824  98              cwde
8825  D1 E0           shl ax, 1
8827  8B C8           mov cx, ax
8829  8B 7E 04        mov di, word ptr [bp + 4]
882C  36 8B 7D 04     mov di, word ptr ss:[di + 4]
8830  36 C4 7D 06     les di, ptr ss:[di + 6]
8834  26 8A 05        mov al, byte ptr es:[di]
8837  98              cwde
8838  BA A0 00        mov dx, 0xa0
883B  F7 E2           mul dx
883D  C4 3E 16 7C     les di, ptr [0x7c16]
8841  03 F8           add di, ax
8843  03 F9           add di, cx
8845  26 8A 85 0E 09  mov al, byte ptr es:[di + 0x90e]
884A  50              push ax
884B  BF 48 06        mov di, 0x648
884E  1E              push ds
884F  57              push di
8850  9A DF 08 E4 23  call far 23E4:08DF
8855  74 04           je 0x885b
loc_8857:
8857  B0 00           mov al, 0
8859  EB 02           jmp 0x885d
loc_885B:
885B  B0 01           mov al, 1
loc_885D:
885D  88 46 FF        mov byte ptr [bp - 1], al
8860  8A 46 FF        mov al, byte ptr [bp - 1]
8863  89 EC           mov sp, bp
8865  5D              pop bp
8866  C2 02 00        ret 2
; data (not reached as code), 32 bytes
8869                  db A0 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
8879                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:8889  (found by: call)
sub_8889:
8889  55              push bp
888A  89 E5           mov bp, sp
888C  83 EC 02        sub sp, 2
888F  80 3E 02 83 00  cmp byte ptr [0x8302], 0
8894  74 3D           je 0x88d3
8896  8B 7E 04        mov di, word ptr [bp + 4]
8899  36 C4 7D 06     les di, ptr ss:[di + 6]
889D  06              push es
889E  57              push di
889F  0E              push cs
88A0  E8 42 A3        call 0x2be5
88A3  98              cwde
88A4  8B D0           mov dx, ax
88A6  8B 7E 04        mov di, word ptr [bp + 4]
88A9  36 C4 7D 06     les di, ptr ss:[di + 6]
88AD  26 8A 45 01     mov al, byte ptr es:[di + 1]
88B1  98              cwde
88B2  F7 EA           imul dx
88B4  50              push ax
88B5  8B 7E 04        mov di, word ptr [bp + 4]
88B8  36 C4 7D 06     les di, ptr ss:[di + 6]
88BC  06              push es
88BD  57              push di
88BE  0E              push cs
88BF  E8 23 A3        call 0x2be5
88C2  98              cwde
88C3  8B D0           mov dx, ax
88C5  A0 F7 82        mov al, byte ptr [0x82f7]
88C8  98              cwde
88C9  F7 EA           imul dx
88CB  5A              pop dx
88CC  3B C2           cmp ax, dx
88CE  7E 03           jle 0x88d3
88D0  E9 12 01        jmp 0x89e5
loc_88D3:
88D3  8B 7E 04        mov di, word ptr [bp + 4]
88D6  36 C4 7D 06     les di, ptr ss:[di + 6]
88DA  26 8A 45 06     mov al, byte ptr es:[di + 6]
88DE  3A 06 0B 83     cmp al, byte ptr [0x830b]
88E2  75 03           jne 0x88e7
88E4  E9 FE 00        jmp 0x89e5
loc_88E7:
88E7  8B 7E 04        mov di, word ptr [bp + 4]
88EA  36 C4 7D 06     les di, ptr ss:[di + 6]
88EE  26 8A 45 06     mov al, byte ptr es:[di + 6]
88F2  3A 06 0C 83     cmp al, byte ptr [0x830c]
88F6  75 03           jne 0x88fb
88F8  E9 EA 00        jmp 0x89e5
loc_88FB:
88FB  8B 7E 04        mov di, word ptr [bp + 4]
88FE  36 C4 7D 06     les di, ptr ss:[di + 6]
8902  06              push es
8903  57              push di
8904  0E              push cs
8905  E8 DD A2        call 0x2be5
8908  08 C0           or al, al
890A  7F 04           jg 0x8910
890C  B0 00           mov al, 0
890E  EB 02           jmp 0x8912
loc_8910:
8910  B0 01           mov al, 1
loc_8912:
8912  8A D0           mov dl, al
8914  8B 7E 04        mov di, word ptr [bp + 4]
8917  36 C4 7D 06     les di, ptr ss:[di + 6]
891B  26 80 7D 08 00  cmp byte ptr es:[di + 8], 0
8920  7F 04           jg 0x8926
8922  B0 00           mov al, 0
8924  EB 02           jmp 0x8928
loc_8926:
8926  B0 01           mov al, 1
loc_8928:
8928  3A C2           cmp al, dl
892A  74 03           je 0x892f
892C  E9 B6 00        jmp 0x89e5
loc_892F:
892F  8B 7E 04        mov di, word ptr [bp + 4]
8932  36 C4 7D 06     les di, ptr ss:[di + 6]
8936  06              push es
8937  57              push di
8938  0E              push cs
8939  E8 38 A0        call 0x2974
893C  08 C0           or al, al
893E  74 04           je 0x8944
8940  B0 00           mov al, 0
8942  EB 02           jmp 0x8946
loc_8944:
8944  B0 01           mov al, 1
loc_8946:
8946  98              cwde
8947  8B F8           mov di, ax
8949  D1 E7           shl di, 1
894B  8B F7           mov si, di
894D  D1 E7           shl di, 1
894F  03 FE           add di, si
8951  8A 85 E3 82     mov al, byte ptr [di - 0x7d1d]
8955  98              cwde
8956  09 C0           or ax, ax
8958  79 02           jns 0x895c
895A  F7 D8           neg ax
loc_895C:
895C  8B D0           mov dx, ax
895E  8B 7E 04        mov di, word ptr [bp + 4]
8961  36 C4 7D 06     les di, ptr ss:[di + 6]
8965  26 8A 45 08     mov al, byte ptr es:[di + 8]
8969  98              cwde
896A  09 C0           or ax, ax
896C  79 02           jns 0x8970
896E  F7 D8           neg ax
loc_8970:
8970  3B C2           cmp ax, dx
8972  7C 71           jl 0x89e5
8974  8B 7E 04        mov di, word ptr [bp + 4]
8977  36 C4 7D 06     les di, ptr ss:[di + 6]
897B  26 8A 45 12     mov al, byte ptr es:[di + 0x12]
897F  50              push ax
8980  BF 69 88        mov di, 0x8869
8983  0E              push cs
8984  57              push di
8985  9A DF 08 E4 23  call far 23E4:08DF
898A  74 59           je 0x89e5
898C  8B 7E 04        mov di, word ptr [bp + 4]
898F  36 C4 7D 06     les di, ptr ss:[di + 6]
8993  26 8A 45 06     mov al, byte ptr es:[di + 6]
8997  30 E4           xor ah, ah
8999  50              push ax
899A  E8 C0 7A        call 0x1045d
899D  08 C0           or al, al
899F  75 44           jne 0x89e5
89A1  8B 7E 04        mov di, word ptr [bp + 4]
89A4  36 C4 7D 06     les di, ptr ss:[di + 6]
89A8  06              push es
89A9  57              push di
89AA  0E              push cs
89AB  E8 37 A2        call 0x2be5
89AE  98              cwde
89AF  50              push ax
89B0  8B 7E 04        mov di, word ptr [bp + 4]
89B3  36 C4 7D 06     les di, ptr ss:[di + 6]
89B7  06              push es
89B8  57              push di
89B9  0E              push cs
89BA  E8 B7 9F        call 0x2974
89BD  08 C0           or al, al
89BF  74 04           je 0x89c5
89C1  B0 00           mov al, 0
89C3  EB 02           jmp 0x89c7
loc_89C5:
89C5  B0 01           mov al, 1
loc_89C7:
89C7  98              cwde
89C8  8B F8           mov di, ax
89CA  D1 E7           shl di, 1
89CC  8B F7           mov si, di
89CE  D1 E7           shl di, 1
89D0  03 FE           add di, si
89D2  8A 85 E3 82     mov al, byte ptr [di - 0x7d1d]
89D6  98              cwde
89D7  5A              pop dx
89D8  2B C2           sub ax, dx
89DA  8B 7E 04        mov di, word ptr [bp + 4]
89DD  36 C4 7D 06     les di, ptr ss:[di + 6]
89E1  26 88 45 08     mov byte ptr es:[di + 8], al
loc_89E5:
89E5  8B 7E 04        mov di, word ptr [bp + 4]
89E8  36 C4 7D 06     les di, ptr ss:[di + 6]
89EC  26 8B 45 07     mov ax, word ptr es:[di + 7]
89F0  89 46 FE        mov word ptr [bp - 2], ax
89F3  8B 7E 04        mov di, word ptr [bp + 4]
89F6  36 C4 7D 06     les di, ptr ss:[di + 6]
89FA  26 8A 05        mov al, byte ptr es:[di]
89FD  28 46 FE        sub byte ptr [bp - 2], al
8A00  8B 7E 04        mov di, word ptr [bp + 4]
8A03  36 C4 7D 06     les di, ptr ss:[di + 6]
8A07  26 8A 45 01     mov al, byte ptr es:[di + 1]
8A0B  28 46 FF        sub byte ptr [bp - 1], al
8A0E  8B 7E 04        mov di, word ptr [bp + 4]
8A11  36 C4 7D 06     les di, ptr ss:[di + 6]
8A15  06              push es
8A16  57              push di
8A17  0E              push cs
8A18  E8 AA A2        call 0x2cc5
8A1B  08 C0           or al, al
8A1D  74 0F           je 0x8a2e
8A1F  8B 7E 04        mov di, word ptr [bp + 4]
8A22  36 C4 7D 06     les di, ptr ss:[di + 6]
8A26  26 C6 45 0F 05  mov byte ptr es:[di + 0xf], 5
8A2B  E9 97 00        jmp 0x8ac5
loc_8A2E:
8A2E  9A FA 06 4B 21  call far 214B:06FA
8A33  08 C0           or al, al
8A35  74 48           je 0x8a7f
8A37  8A 46 FE        mov al, byte ptr [bp - 2]
8A3A  98              cwde
8A3B  09 C0           or ax, ax
8A3D  79 02           jns 0x8a41
8A3F  F7 D8           neg ax
loc_8A41:
8A41  09 C0           or ax, ax
8A43  7E 1C           jle 0x8a61
8A45  80 7E FE 00     cmp byte ptr [bp - 2], 0
8A49  7F 04           jg 0x8a4f
8A4B  B0 00           mov al, 0
8A4D  EB 02           jmp 0x8a51
loc_8A4F:
8A4F  B0 01           mov al, 1
loc_8A51:
8A51  30 E4           xor ah, ah
8A53  40              inc ax
8A54  8B 7E 04        mov di, word ptr [bp + 4]
8A57  36 C4 7D 06     les di, ptr ss:[di + 6]
8A5B  26 88 45 0F     mov byte ptr es:[di + 0xf], al
8A5F  EB 1C           jmp 0x8a7d
loc_8A61:
8A61  80 7E FF 00     cmp byte ptr [bp - 1], 0
8A65  7F 04           jg 0x8a6b
8A67  B0 00           mov al, 0
8A69  EB 02           jmp 0x8a6d
loc_8A6B:
8A6B  B0 01           mov al, 1
loc_8A6D:
8A6D  30 E4           xor ah, ah
8A6F  05 03 00        add ax, 3
8A72  8B 7E 04        mov di, word ptr [bp + 4]
8A75  36 C4 7D 06     les di, ptr ss:[di + 6]
8A79  26 88 45 0F     mov byte ptr es:[di + 0xf], al
loc_8A7D:
8A7D  EB 46           jmp 0x8ac5
loc_8A7F:
8A7F  8A 46 FF        mov al, byte ptr [bp - 1]
8A82  98              cwde
8A83  09 C0           or ax, ax
8A85  79 02           jns 0x8a89
8A87  F7 D8           neg ax
loc_8A89:
8A89  09 C0           or ax, ax
8A8B  7E 1E           jle 0x8aab
8A8D  80 7E FF 00     cmp byte ptr [bp - 1], 0
8A91  7F 04           jg 0x8a97
8A93  B0 00           mov al, 0
8A95  EB 02           jmp 0x8a99
loc_8A97:
8A97  B0 01           mov al, 1
loc_8A99:
8A99  30 E4           xor ah, ah
8A9B  05 03 00        add ax, 3
8A9E  8B 7E 04        mov di, word ptr [bp + 4]
8AA1  36 C4 7D 06     les di, ptr ss:[di + 6]
8AA5  26 88 45 0F     mov byte ptr es:[di + 0xf], al
8AA9  EB 1A           jmp 0x8ac5
loc_8AAB:
8AAB  80 7E FE 00     cmp byte ptr [bp - 2], 0
8AAF  7F 04           jg 0x8ab5
8AB1  B0 00           mov al, 0
8AB3  EB 02           jmp 0x8ab7
loc_8AB5:
8AB5  B0 01           mov al, 1
loc_8AB7:
8AB7  30 E4           xor ah, ah
8AB9  40              inc ax
8ABA  8B 7E 04        mov di, word ptr [bp + 4]
8ABD  36 C4 7D 06     les di, ptr ss:[di + 6]
8AC1  26 88 45 0F     mov byte ptr es:[di + 0xf], al
loc_8AC5:
8AC5  55              push bp
8AC6  E8 07 FC        call 0x86d0
8AC9  08 C0           or al, al
8ACB  75 16           jne 0x8ae3
8ACD  B8 05 00        mov ax, 5
8AD0  50              push ax
8AD1  9A B1 06 4B 21  call far 214B:06B1
8AD6  8B 7E 04        mov di, word ptr [bp + 4]
8AD9  36 C4 7D 06     les di, ptr ss:[di + 6]
8ADD  26 88 45 0F     mov byte ptr es:[di + 0xf], al
8AE1  EB E2           jmp 0x8ac5
loc_8AE3:
8AE3  89 EC           mov sp, bp
8AE5  5D              pop bp
8AE6  C2 02 00        ret 2

; ---- routine 0791:8AE9  (found by: call)
sub_8AE9:
8AE9  55              push bp
8AEA  89 E5           mov bp, sp
8AEC  83 EC 06        sub sp, 6
8AEF  C4 7E 06        les di, ptr [bp + 6]
8AF2  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
8AF6  BA 14 00        mov dx, 0x14
8AF9  F7 E2           mul dx
8AFB  C4 3E 1B A9     les di, ptr [0xa91b]
8AFF  03 F8           add di, ax
8B01  89 7E FA        mov word ptr [bp - 6], di
8B04  8C 46 FC        mov word ptr [bp - 4], es
8B07  C4 7E 06        les di, ptr [bp + 6]
8B0A  26 8A 45 12     mov al, byte ptr es:[di + 0x12]
8B0E  3C 05           cmp al, 5
8B10  75 0C           jne 0x8b1e
8B12  C4 7E 06        les di, ptr [bp + 6]
8B15  06              push es
8B16  57              push di
8B17  0E              push cs
8B18  E8 91 CC        call 0x57ac
8B1B  E9 95 00        jmp 0x8bb3
loc_8B1E:
8B1E  3C 0D           cmp al, 0xd
8B20  75 0C           jne 0x8b2e
8B22  C4 7E 06        les di, ptr [bp + 6]
8B25  06              push es
8B26  57              push di
8B27  0E              push cs
8B28  E8 B6 CD        call 0x58e1
8B2B  E9 85 00        jmp 0x8bb3
loc_8B2E:
8B2E  3C 01           cmp al, 1
8B30  75 0B           jne 0x8b3d
8B32  C4 7E 06        les di, ptr [bp + 6]
8B35  06              push es
8B36  57              push di
8B37  0E              push cs
8B38  E8 82 DE        call 0x69bd
8B3B  EB 76           jmp 0x8bb3
loc_8B3D:
8B3D  3C 02           cmp al, 2
8B3F  75 0B           jne 0x8b4c
8B41  C4 7E 06        les di, ptr [bp + 6]
8B44  06              push es
8B45  57              push di
8B46  0E              push cs
8B47  E8 63 DF        call 0x6aad
8B4A  EB 67           jmp 0x8bb3
loc_8B4C:
8B4C  3C 03           cmp al, 3
8B4E  75 0B           jne 0x8b5b
8B50  C4 7E 06        les di, ptr [bp + 6]
8B53  06              push es
8B54  57              push di
8B55  0E              push cs
8B56  E8 9E DF        call 0x6af7
8B59  EB 58           jmp 0x8bb3
loc_8B5B:
8B5B  3C 06           cmp al, 6
8B5D  75 0B           jne 0x8b6a
8B5F  C4 7E 06        les di, ptr [bp + 6]
8B62  06              push es
8B63  57              push di
8B64  0E              push cs
8B65  E8 D8 D6        call 0x6240
8B68  EB 49           jmp 0x8bb3
loc_8B6A:
8B6A  3C 07           cmp al, 7
8B6C  75 0B           jne 0x8b79
8B6E  C4 7E 06        les di, ptr [bp + 6]
8B71  06              push es
8B72  57              push di
8B73  0E              push cs
8B74  E8 F2 E4        call 0x7069
8B77  EB 3A           jmp 0x8bb3
loc_8B79:
8B79  3C 08           cmp al, 8
8B7B  75 0B           jne 0x8b88
8B7D  C4 7E 06        les di, ptr [bp + 6]
8B80  06              push es
8B81  57              push di
8B82  0E              push cs
8B83  E8 01 E7        call 0x7287
8B86  EB 2B           jmp 0x8bb3
loc_8B88:
8B88  3C 09           cmp al, 9
8B8A  75 0B           jne 0x8b97
8B8C  C4 7E 06        les di, ptr [bp + 6]
8B8F  06              push es
8B90  57              push di
8B91  0E              push cs
8B92  E8 C5 E5        call 0x715a
8B95  EB 1C           jmp 0x8bb3
loc_8B97:
8B97  3C 0A           cmp al, 0xa
8B99  75 0B           jne 0x8ba6
8B9B  C4 7E 06        les di, ptr [bp + 6]
8B9E  06              push es
8B9F  57              push di
8BA0  0E              push cs
8BA1  E8 16 E8        call 0x73ba
8BA4  EB 0D           jmp 0x8bb3
loc_8BA6:
8BA6  3C 0B           cmp al, 0xb
8BA8  75 09           jne 0x8bb3
8BAA  C4 7E 06        les di, ptr [bp + 6]
8BAD  06              push es
8BAE  57              push di
8BAF  0E              push cs
8BB0  E8 6E EA        call 0x7621
loc_8BB3:
8BB3  55              push bp
8BB4  E8 D2 FC        call 0x8889
8BB7  C4 7E 06        les di, ptr [bp + 6]
8BBA  26 80 7D 0F 05  cmp byte ptr es:[di + 0xf], 5
8BBF  72 04           jb 0x8bc5
8BC1  B0 00           mov al, 0
8BC3  EB 02           jmp 0x8bc7
loc_8BC5:
8BC5  B0 01           mov al, 1
loc_8BC7:
8BC7  30 E4           xor ah, ah
8BC9  C4 7E 06        les di, ptr [bp + 6]
8BCC  26 01 45 14     add word ptr es:[di + 0x14], ax
8BD0  80 3E 02 83 00  cmp byte ptr [0x8302], 0
8BD5  74 55           je 0x8c2c
8BD7  C4 7E 06        les di, ptr [bp + 6]
8BDA  26 8A 45 06     mov al, byte ptr es:[di + 6]
8BDE  3A 06 0D 83     cmp al, byte ptr [0x830d]
8BE2  75 48           jne 0x8c2c
8BE4  C4 7E 06        les di, ptr [bp + 6]
8BE7  06              push es
8BE8  57              push di
8BE9  0E              push cs
8BEA  E8 FF A0        call 0x2cec
8BED  08 C0           or al, al
8BEF  74 3B           je 0x8c2c
8BF1  C4 7E 06        les di, ptr [bp + 6]
8BF4  26 80 7D 12 0C  cmp byte ptr es:[di + 0x12], 0xc
8BF9  74 31           je 0x8c2c
8BFB  A0 03 83        mov al, byte ptr [0x8303]
8BFE  88 46 FE        mov byte ptr [bp - 2], al
8C01  A0 0D 83        mov al, byte ptr [0x830d]
8C04  A2 0C 83        mov byte ptr [0x830c], al
8C07  A0 0B 83        mov al, byte ptr [0x830b]
8C0A  3A 06 0D 83     cmp al, byte ptr [0x830d]
8C0E  74 0D           je 0x8c1d
8C10  80 3E 03 83 00  cmp byte ptr [0x8303], 0
8C15  75 06           jne 0x8c1d
8C17  B0 19           mov al, 0x19
8C19  50              push ax
8C1A  E8 B7 9E        call 0x2ad4
loc_8C1D:
8C1D  C4 7E 06        les di, ptr [bp + 6]
8C20  06              push es
8C21  57              push di
8C22  0E              push cs
8C23  E8 79 FA        call 0x869f
8C26  8A 46 FE        mov al, byte ptr [bp - 2]
8C29  A2 03 83        mov byte ptr [0x8303], al
loc_8C2C:
8C2C  C4 7E 06        les di, ptr [bp + 6]
8C2F  06              push es
8C30  57              push di
8C31  0E              push cs
8C32  E8 02 F9        call 0x8537
8C35  80 3E 25 83 00  cmp byte ptr [0x8325], 0
8C3A  74 25           je 0x8c61
8C3C  C4 7E 06        les di, ptr [bp + 6]
8C3F  26 81 7D 14 B4 00 cmp word ptr es:[di + 0x14], 0xb4
8C45  76 1A           jbe 0x8c61
8C47  C4 7E FA        les di, ptr [bp - 6]
8C4A  26 80 7D 0E 01  cmp byte ptr es:[di + 0xe], 1
8C4F  7E 07           jle 0x8c58
8C51  C4 7E FA        les di, ptr [bp - 6]
8C54  26 FE 4D 0E     dec byte ptr es:[di + 0xe]
loc_8C58:
8C58  C4 7E 06        les di, ptr [bp + 6]
8C5B  31 C0           xor ax, ax
8C5D  26 89 45 14     mov word ptr es:[di + 0x14], ax
loc_8C61:
8C61  89 EC           mov sp, bp
8C63  5D              pop bp
8C64  CA 04 00        retf 4

; ---- routine 0791:8C67  (found by: call)
sub_8C67:
8C67  55              push bp
8C68  89 E5           mov bp, sp
8C6A  83 EC 04        sub sp, 4
8C6D  8A 46 06        mov al, byte ptr [bp + 6]
8C70  98              cwde
8C71  8B F8           mov di, ax
8C73  D1 E7           shl di, 1
8C75  8B F7           mov si, di
8C77  D1 E7           shl di, 1
8C79  03 FE           add di, si
8C7B  81 C7 E2 82     add di, 0x82e2
8C7F  89 7E FC        mov word ptr [bp - 4], di
8C82  8C 5E FE        mov word ptr [bp - 2], ds
8C85  8A 46 06        mov al, byte ptr [bp + 6]
8C88  98              cwde
8C89  8B F8           mov di, ax
8C8B  8A 85 68 06     mov al, byte ptr [di + 0x668]
8C8F  30 E4           xor ah, ah
8C91  40              inc ax
8C92  BA 16 00        mov dx, 0x16
8C95  F7 E2           mul dx
8C97  8B F8           mov di, ax
8C99  81 C7 E8 80     add di, 0x80e8
8C9D  1E              push ds
8C9E  57              push di
8C9F  0E              push cs
8CA0  E8 42 9F        call 0x2be5
8CA3  98              cwde
8CA4  B9 03 00        mov cx, 3
8CA7  D3 E0           shl ax, cl
8CA9  C4 7E FC        les di, ptr [bp - 4]
8CAC  26 88 05        mov byte ptr es:[di], al
8CAF  C4 7E FC        les di, ptr [bp - 4]
8CB2  26 C6 45 01 00  mov byte ptr es:[di + 1], 0
8CB7  C4 7E FC        les di, ptr [bp - 4]
8CBA  26 8B 05        mov ax, word ptr es:[di]
8CBD  C4 7E FC        les di, ptr [bp - 4]
8CC0  26 89 45 02     mov word ptr es:[di + 2], ax
8CC4  89 EC           mov sp, bp
8CC6  5D              pop bp
8CC7  C2 04 00        ret 4

