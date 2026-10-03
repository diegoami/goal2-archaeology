; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 8 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:4649  (found by: call)
sub_4649:
4649  55              push bp
464A  89 E5           mov bp, sp
464C  83 EC 02        sub sp, 2
464F  C6 46 FF 00     mov byte ptr [bp - 1], 0
4653  8B 7E 04        mov di, word ptr [bp + 4]
4656  36 C4 7D 06     les di, ptr ss:[di + 6]
465A  06              push es
465B  57              push di
465C  0E              push cs
465D  E8 6B FC        call 0x42cb
4660  50              push ax
4661  B8 06 00        mov ax, 6
4664  50              push ax
4665  8B 7E 04        mov di, word ptr [bp + 4]
4668  36 C4 7D 06     les di, ptr ss:[di + 6]
466C  06              push es
466D  57              push di
466E  0E              push cs
466F  E8 65 E0        call 0x26d7
4672  98              cwde
4673  D1 E0           shl ax, 1
4675  D1 E0           shl ax, 1
4677  50              push ax
4678  B8 05 00        mov ax, 5
467B  50              push ax
467C  8B 7E 04        mov di, word ptr [bp + 4]
467F  36 C4 7D 06     les di, ptr ss:[di + 6]
4683  06              push es
4684  57              push di
4685  0E              push cs
4686  E8 4E E0        call 0x26d7
4689  98              cwde
468A  8B F8           mov di, ax
468C  B1 03           mov cl, 3
468E  D3 E7           shl di, cl
4690  58              pop ax
4691  03 F8           add di, ax
4693  58              pop ax
4694  03 F8           add di, ax
4696  8A 85 CB 07     mov al, byte ptr [di + 0x7cb]
469A  30 E4           xor ah, ah
469C  8B D0           mov dx, ax
469E  8B 7E 04        mov di, word ptr [bp + 4]
46A1  36 C4 7D 06     les di, ptr ss:[di + 6]
46A5  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
46A9  98              cwde
46AA  3B C2           cmp ax, dx
46AC  7F 03           jg 0x46b1
46AE  E9 93 00        jmp 0x4744
loc_46B1:
46B1  8B 7E 04        mov di, word ptr [bp + 4]
46B4  36 C4 7D 06     les di, ptr ss:[di + 6]
46B8  06              push es
46B9  57              push di
46BA  0E              push cs
46BB  E8 0D FC        call 0x42cb
46BE  3D 01 00        cmp ax, 1
46C1  75 16           jne 0x46d9
46C3  B8 0F 00        mov ax, 0xf
46C6  50              push ax
46C7  8B 7E 04        mov di, word ptr [bp + 4]
46CA  36 C4 7D 06     les di, ptr ss:[di + 6]
46CE  06              push es
46CF  57              push di
46D0  0E              push cs
46D1  E8 99 E6        call 0x2d6d
46D4  88 46 FF        mov byte ptr [bp - 1], al
46D7  EB 6B           jmp 0x4744
loc_46D9:
46D9  3D 02 00        cmp ax, 2
46DC  75 15           jne 0x46f3
46DE  31 C0           xor ax, ax
46E0  50              push ax
46E1  8B 7E 04        mov di, word ptr [bp + 4]
46E4  36 C4 7D 06     les di, ptr ss:[di + 6]
46E8  06              push es
46E9  57              push di
46EA  0E              push cs
46EB  E8 7F E6        call 0x2d6d
46EE  88 46 FF        mov byte ptr [bp - 1], al
46F1  EB 51           jmp 0x4744
loc_46F3:
46F3  3D 03 00        cmp ax, 3
46F6  75 4C           jne 0x4744
46F8  B8 0A 00        mov ax, 0xa
46FB  50              push ax
46FC  8B 7E 04        mov di, word ptr [bp + 4]
46FF  36 C4 7D 06     les di, ptr ss:[di + 6]
4703  06              push es
4704  57              push di
4705  0E              push cs
4706  E8 07 E6        call 0x2d10
4709  08 C0           or al, al
470B  74 32           je 0x473f
470D  8B 7E 04        mov di, word ptr [bp + 4]
4710  36 C4 7D 06     les di, ptr ss:[di + 6]
4714  06              push es
4715  57              push di
4716  0E              push cs
4717  E8 97 E4        call 0x2bb1
471A  3C 02           cmp al, 2
471C  74 21           je 0x473f
471E  8B 7E 04        mov di, word ptr [bp + 4]
4721  36 C4 7D 06     les di, ptr ss:[di + 6]
4725  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4729  BA 14 00        mov dx, 0x14
472C  F7 E2           mul dx
472E  C4 3E 1B A9     les di, ptr [0xa91b]
4732  03 F8           add di, ax
4734  26 80 7D 06 01  cmp byte ptr es:[di + 6], 1
4739  74 04           je 0x473f
473B  B0 00           mov al, 0
473D  EB 02           jmp 0x4741
loc_473F:
473F  B0 01           mov al, 1
loc_4741:
4741  88 46 FF        mov byte ptr [bp - 1], al
loc_4744:
4744  8A 46 FF        mov al, byte ptr [bp - 1]
4747  89 EC           mov sp, bp
4749  5D              pop bp
474A  C2 02 00        ret 2

; ---- routine 0791:474D  (found by: call)
sub_474D:
474D  55              push bp
474E  89 E5           mov bp, sp
4750  83 EC 02        sub sp, 2
4753  C4 7E 06        les di, ptr [bp + 6]
4756  06              push es
4757  57              push di
4758  0E              push cs
4759  E8 F5 E3        call 0x2b51
475C  08 C0           or al, al
475E  74 36           je 0x4796
4760  C4 7E 06        les di, ptr [bp + 6]
4763  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4767  BA 14 00        mov dx, 0x14
476A  F7 E2           mul dx
476C  C4 3E 1B A9     les di, ptr [0xa91b]
4770  03 F8           add di, ax
4772  26 80 7D 06 04  cmp byte ptr es:[di + 6], 4
4777  77 10           ja 0x4789
4779  31 C0           xor ax, ax
477B  50              push ax
477C  C4 7E 06        les di, ptr [bp + 6]
477F  06              push es
4780  57              push di
4781  0E              push cs
4782  E8 8B E5        call 0x2d10
4785  08 C0           or al, al
4787  74 0D           je 0x4796
loc_4789:
4789  55              push bp
478A  E8 A5 FD        call 0x4532
478D  C4 7E 06        les di, ptr [bp + 6]
4790  26 00 45 0C     add byte ptr es:[di + 0xc], al
4794  EB 29           jmp 0x47bf
loc_4796:
4796  55              push bp
4797  E8 AF FE        call 0x4649
479A  C4 7E 06        les di, ptr [bp + 6]
479D  26 28 45 0C     sub byte ptr es:[di + 0xc], al
47A1  C4 7E 06        les di, ptr [bp + 6]
47A4  06              push es
47A5  57              push di
47A6  0E              push cs
47A7  E8 07 E4        call 0x2bb1
47AA  3C 02           cmp al, 2
47AC  75 11           jne 0x47bf
47AE  C4 7E 06        les di, ptr [bp + 6]
47B1  26 8A 45 09     mov al, byte ptr es:[di + 9]
47B5  98              cwde
47B6  F7 D8           neg ax
47B8  C4 7E 06        les di, ptr [bp + 6]
47BB  26 88 45 0B     mov byte ptr es:[di + 0xb], al
loc_47BF:
47BF  89 EC           mov sp, bp
47C1  5D              pop bp
47C2  CA 04 00        retf 4

; ---- routine 0791:47C5  (found by: call)
sub_47C5:
47C5  55              push bp
47C6  89 E5           mov bp, sp
47C8  83 EC 0C        sub sp, 0xc
47CB  E8 C8 E1        call 0x2996
47CE  98              cwde
47CF  8B F8           mov di, ax
47D1  D1 E7           shl di, 1
47D3  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
47D7  BA BF 00        mov dx, 0xbf
47DA  F7 E2           mul dx
47DC  C4 3E 17 A9     les di, ptr [0xa917]
47E0  03 F8           add di, ax
47E2  89 7E F4        mov word ptr [bp - 0xc], di
47E5  8C 46 F6        mov word ptr [bp - 0xa], es
47E8  C6 46 FF 00     mov byte ptr [bp - 1], 0
47EC  E8 A7 E1        call 0x2996
47EF  88 46 F8        mov byte ptr [bp - 8], al
47F2  80 7E F8 00     cmp byte ptr [bp - 8], 0
47F6  74 04           je 0x47fc
47F8  B0 00           mov al, 0
47FA  EB 02           jmp 0x47fe
loc_47FC:
47FC  B0 01           mov al, 1
loc_47FE:
47FE  98              cwde
47FF  8B F8           mov di, ax
4801  8A 85 68 06     mov al, byte ptr [di + 0x668]
4805  30 E4           xor ah, ah
4807  8B D0           mov dx, ax
4809  8B 7E 04        mov di, word ptr [bp + 4]
480C  36 C4 7D 06     les di, ptr ss:[di + 6]
4810  26 8A 45 06     mov al, byte ptr es:[di + 6]
4814  30 E4           xor ah, ah
4816  2B C2           sub ax, dx
4818  D1 E0           shl ax, 1
481A  8B C8           mov cx, ax
481C  80 7E F8 00     cmp byte ptr [bp - 8], 0
4820  74 04           je 0x4826
4822  B0 00           mov al, 0
4824  EB 02           jmp 0x4828
loc_4826:
4826  B0 01           mov al, 1
loc_4828:
4828  98              cwde
4829  BA 28 00        mov dx, 0x28
482C  F7 E2           mul dx
482E  8B F8           mov di, ax
4830  03 F9           add di, cx
4832  8B 85 3E 9A     mov ax, word ptr [di - 0x65c2]
4836  89 46 F9        mov word ptr [bp - 7], ax
4839  83 7E F9 00     cmp word ptr [bp - 7], 0
483D  75 63           jne 0x48a2
483F  C7 46 FD 02 00  mov word ptr [bp - 3], 2
loc_4844:
4844  83 7E FD 0C     cmp word ptr [bp - 3], 0xc
4848  73 58           jae 0x48a2
484A  8B 46 FD        mov ax, word ptr [bp - 3]
484D  D1 E0           shl ax, 1
484F  C4 7E F4        les di, ptr [bp - 0xc]
4852  03 F8           add di, ax
4854  26 FF 75 FE     push word ptr es:[di - 2]
4858  9A 16 32 71 17  call far 1771:3216
485D  08 C0           or al, al
485F  75 3C           jne 0x489d
4861  8A 46 F8        mov al, byte ptr [bp - 8]
4864  98              cwde
4865  8B F8           mov di, ax
4867  8A 85 68 06     mov al, byte ptr [di + 0x668]
486B  30 E4           xor ah, ah
486D  03 46 FD        add ax, word ptr [bp - 3]
4870  BA 16 00        mov dx, 0x16
4873  F7 E2           mul dx
4875  8B F8           mov di, ax
4877  FF B5 E8 80     push word ptr [di - 0x7f18]
487B  8B 7E 04        mov di, word ptr [bp + 4]
487E  36 C4 7D 06     les di, ptr ss:[di + 6]
4882  06              push es
4883  57              push di
4884  0E              push cs
4885  E8 B0 FB        call 0x4438
4888  08 C0           or al, al
488A  74 11           je 0x489d
488C  8B 46 FD        mov ax, word ptr [bp - 3]
488F  D1 E0           shl ax, 1
4891  C4 7E F4        les di, ptr [bp - 0xc]
4894  03 F8           add di, ax
4896  26 8B 45 FE     mov ax, word ptr es:[di - 2]
489A  89 46 F9        mov word ptr [bp - 7], ax
loc_489D:
489D  FF 46 FD        inc word ptr [bp - 3]
48A0  EB A2           jmp 0x4844
loc_48A2:
48A2  83 7E F9 00     cmp word ptr [bp - 7], 0
48A6  75 03           jne 0x48ab
48A8  E9 74 01        jmp 0x4a1f
loc_48AB:
48AB  C7 46 FD 02 00  mov word ptr [bp - 3], 2
loc_48B0:
48B0  83 7E FD 0C     cmp word ptr [bp - 3], 0xc
48B4  72 03           jb 0x48b9
48B6  E9 20 01        jmp 0x49d9
loc_48B9:
48B9  8B 46 FD        mov ax, word ptr [bp - 3]
48BC  D1 E0           shl ax, 1
48BE  C4 7E F4        les di, ptr [bp - 0xc]
48C1  03 F8           add di, ax
48C3  26 8B 45 FE     mov ax, word ptr es:[di - 2]
48C7  3B 46 F9        cmp ax, word ptr [bp - 7]
48CA  74 03           je 0x48cf
48CC  E9 04 01        jmp 0x49d3
loc_48CF:
48CF  8B 46 FD        mov ax, word ptr [bp - 3]
48D2  D1 E0           shl ax, 1
48D4  C4 7E F4        les di, ptr [bp - 0xc]
48D7  03 F8           add di, ax
48D9  26 FF 75 FE     push word ptr es:[di - 2]
48DD  9A 16 32 71 17  call far 1771:3216
48E2  08 C0           or al, al
48E4  74 03           je 0x48e9
48E6  E9 EA 00        jmp 0x49d3
loc_48E9:
48E9  8A 46 F8        mov al, byte ptr [bp - 8]
48EC  98              cwde
48ED  8B F8           mov di, ax
48EF  8A 85 68 06     mov al, byte ptr [di + 0x668]
48F3  30 E4           xor ah, ah
48F5  03 46 FD        add ax, word ptr [bp - 3]
48F8  8B 7E 04        mov di, word ptr [bp + 4]
48FB  36 89 45 FC     mov word ptr ss:[di - 4], ax
48FF  8B 7E 04        mov di, word ptr [bp + 4]
4902  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
4906  BA 16 00        mov dx, 0x16
4909  F7 E2           mul dx
490B  8B F8           mov di, ax
490D  8B 85 E8 80     mov ax, word ptr [di - 0x7f18]
4911  8B 7E 04        mov di, word ptr [bp + 4]
4914  36 89 45 FE     mov word ptr ss:[di - 2], ax
4918  8B 7E 04        mov di, word ptr [bp + 4]
491B  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
491F  BA 16 00        mov dx, 0x16
4922  F7 E2           mul dx
4924  8B F8           mov di, ax
4926  81 C7 E8 80     add di, 0x80e8
492A  1E              push ds
492B  57              push di
492C  0E              push cs
492D  E8 24 E3        call 0x2c54
4930  08 C0           or al, al
4932  74 03           je 0x4937
4934  E9 E8 00        jmp 0x4a1f
loc_4937:
4937  C7 46 FB 01 00  mov word ptr [bp - 5], 1
493C  B8 05 00        mov ax, 5
493F  50              push ax
4940  8B 7E 04        mov di, word ptr [bp + 4]
4943  36 C4 7D 06     les di, ptr ss:[di + 6]
4947  06              push es
4948  57              push di
4949  0E              push cs
494A  E8 3D DE        call 0x278a
494D  50              push ax
494E  B8 08 00        mov ax, 8
4951  50              push ax
4952  8B 7E 04        mov di, word ptr [bp + 4]
4955  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
4959  BA 16 00        mov dx, 0x16
495C  F7 E2           mul dx
495E  8B F8           mov di, ax
4960  81 C7 E8 80     add di, 0x80e8
4964  1E              push ds
4965  57              push di
4966  0E              push cs
4967  E8 20 DE        call 0x278a
496A  5A              pop dx
496B  3B C2           cmp ax, dx
496D  76 3B           jbe 0x49aa
496F  B8 05 00        mov ax, 5
4972  50              push ax
4973  8B 7E 04        mov di, word ptr [bp + 4]
4976  36 C4 7D 06     les di, ptr ss:[di + 6]
497A  06              push es
497B  57              push di
497C  0E              push cs
497D  E8 0A DE        call 0x278a
4980  50              push ax
4981  B8 08 00        mov ax, 8
4984  50              push ax
4985  8B 7E 04        mov di, word ptr [bp + 4]
4988  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
498C  BA 16 00        mov dx, 0x16
498F  F7 E2           mul dx
4991  8B F8           mov di, ax
4993  81 C7 E8 80     add di, 0x80e8
4997  1E              push ds
4998  57              push di
4999  0E              push cs
499A  E8 ED DD        call 0x278a
499D  5A              pop dx
499E  2B C2           sub ax, dx
49A0  31 D2           xor dx, dx
49A2  B9 10 00        mov cx, 0x10
49A5  F7 F1           div cx
49A7  01 46 FB        add word ptr [bp - 5], ax
loc_49AA:
49AA  FF 76 FB        push word ptr [bp - 5]
49AD  9A B1 06 4B 21  call far 214B:06B1
49B2  50              push ax
49B3  8B 7E 04        mov di, word ptr [bp + 4]
49B6  36 C4 7D 06     les di, ptr ss:[di + 6]
49BA  06              push es
49BB  57              push di
49BC  0E              push cs
49BD  E8 25 E2        call 0x2be5
49C0  98              cwde
49C1  5A              pop dx
49C2  F7 EA           imul dx
49C4  8B 7E 04        mov di, word ptr [bp + 4]
49C7  36 28 45 FF     sub byte ptr ss:[di - 1], al
49CB  C6 46 FF 01     mov byte ptr [bp - 1], 1
49CF  EB 4E           jmp 0x4a1f
; data (not reached as code), 2 bytes
49D1                  db EB 03   ; ..
loc_49D3:
49D3  FF 46 FD        inc word ptr [bp - 3]
49D6  E9 D7 FE        jmp 0x48b0
loc_49D9:
49D9  80 7E F8 00     cmp byte ptr [bp - 8], 0
49DD  74 04           je 0x49e3
49DF  B0 00           mov al, 0
49E1  EB 02           jmp 0x49e5
loc_49E3:
49E3  B0 01           mov al, 1
loc_49E5:
49E5  98              cwde
49E6  8B F8           mov di, ax
49E8  8A 85 68 06     mov al, byte ptr [di + 0x668]
49EC  30 E4           xor ah, ah
49EE  8B D0           mov dx, ax
49F0  8B 7E 04        mov di, word ptr [bp + 4]
49F3  36 C4 7D 06     les di, ptr ss:[di + 6]
49F7  26 8A 45 06     mov al, byte ptr es:[di + 6]
49FB  30 E4           xor ah, ah
49FD  2B C2           sub ax, dx
49FF  D1 E0           shl ax, 1
4A01  8B C8           mov cx, ax
4A03  80 7E F8 00     cmp byte ptr [bp - 8], 0
4A07  74 04           je 0x4a0d
4A09  B0 00           mov al, 0
4A0B  EB 02           jmp 0x4a0f
loc_4A0D:
4A0D  B0 01           mov al, 1
loc_4A0F:
4A0F  98              cwde
4A10  BA 28 00        mov dx, 0x28
4A13  F7 E2           mul dx
4A15  8B F8           mov di, ax
4A17  03 F9           add di, cx
4A19  31 C0           xor ax, ax
4A1B  89 85 3E 9A     mov word ptr [di - 0x65c2], ax
loc_4A1F:
4A1F  8A 46 FF        mov al, byte ptr [bp - 1]
4A22  89 EC           mov sp, bp
4A24  5D              pop bp
4A25  C2 02 00        ret 2

; ---- routine 0791:4A28  (found by: call)
sub_4A28:
4A28  55              push bp
4A29  89 E5           mov bp, sp
4A2B  83 EC 08        sub sp, 8
4A2E  C4 7E 06        les di, ptr [bp + 6]
4A31  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4A35  BA 14 00        mov dx, 0x14
4A38  F7 E2           mul dx
4A3A  C4 3E 1B A9     les di, ptr [0xa91b]
4A3E  03 F8           add di, ax
4A40  89 7E F8        mov word ptr [bp - 8], di
4A43  8C 46 FA        mov word ptr [bp - 6], es
4A46  C4 7E 06        les di, ptr [bp + 6]
4A49  06              push es
4A4A  57              push di
4A4B  0E              push cs
4A4C  E8 02 E1        call 0x2b51
4A4F  08 C0           or al, al
4A51  74 34           je 0x4a87
4A53  C4 7E 06        les di, ptr [bp + 6]
4A56  06              push es
4A57  57              push di
4A58  0E              push cs
4A59  E8 1F E1        call 0x2b7b
4A5C  08 C0           or al, al
4A5E  75 1B           jne 0x4a7b
4A60  C4 7E F8        les di, ptr [bp - 8]
4A63  26 80 7D 06 01  cmp byte ptr es:[di + 6], 1
4A68  75 1A           jne 0x4a84
4A6A  B8 0A 00        mov ax, 0xa
4A6D  50              push ax
4A6E  C4 7E 06        les di, ptr [bp + 6]
4A71  06              push es
4A72  57              push di
4A73  0E              push cs
4A74  E8 99 E2        call 0x2d10
4A77  08 C0           or al, al
4A79  75 09           jne 0x4a84
loc_4A7B:
4A7B  C4 7E 06        les di, ptr [bp + 6]
4A7E  06              push es
4A7F  57              push di
4A80  0E              push cs
4A81  E8 D0 F8        call 0x4354
loc_4A84:
4A84  E9 B7 00        jmp 0x4b3e
loc_4A87:
4A87  C4 7E 06        les di, ptr [bp + 6]
4A8A  06              push es
4A8B  57              push di
4A8C  0E              push cs
4A8D  E8 C4 F8        call 0x4354
4A90  C4 7E 06        les di, ptr [bp + 6]
4A93  26 8A 45 06     mov al, byte ptr es:[di + 6]
4A97  30 E4           xor ah, ah
4A99  50              push ax
4A9A  E8 C0 B9        call 0x45d
4A9D  08 C0           or al, al
4A9F  74 3C           je 0x4add
4AA1  80 3E 25 83 00  cmp byte ptr [0x8325], 0
4AA6  74 33           je 0x4adb
4AA8  FF 36 F6 82     push word ptr [0x82f6]
4AAC  C4 7E 06        les di, ptr [bp + 6]
4AAF  06              push es
4AB0  57              push di
4AB1  0E              push cs
4AB2  E8 81 E3        call 0x2e36
4AB5  08 C0           or al, al
4AB7  75 18           jne 0x4ad1
4AB9  B8 01 00        mov ax, 1
4ABC  50              push ax
4ABD  C4 7E 06        les di, ptr [bp + 6]
4AC0  06              push es
4AC1  57              push di
4AC2  0E              push cs
4AC3  E8 11 DC        call 0x26d7
4AC6  08 C0           or al, al
4AC8  74 11           je 0x4adb
4ACA  E8 EF F5        call 0x40bc
4ACD  08 C0           or al, al
4ACF  74 0A           je 0x4adb
loc_4AD1:
4AD1  A1 F6 82        mov ax, word ptr [0x82f6]
4AD4  C4 7E 06        les di, ptr [bp + 6]
4AD7  26 89 45 07     mov word ptr es:[di + 7], ax
loc_4ADB:
4ADB  EB 61           jmp 0x4b3e
loc_4ADD:
4ADD  55              push bp
4ADE  E8 E4 FC        call 0x47c5
4AE1  08 C0           or al, al
4AE3  74 59           je 0x4b3e
4AE5  80 3E 25 83 00  cmp byte ptr [0x8325], 0
4AEA  75 0A           jne 0x4af6
4AEC  A0 0B 83        mov al, byte ptr [0x830b]
4AEF  30 E4           xor ah, ah
4AF1  3B 46 FC        cmp ax, word ptr [bp - 4]
4AF4  74 48           je 0x4b3e
loc_4AF6:
4AF6  B8 06 00        mov ax, 6
4AF9  50              push ax
4AFA  9A B1 06 4B 21  call far 214B:06B1
4AFF  8B D0           mov dx, ax
4B01  C4 7E F8        les di, ptr [bp - 8]
4B04  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
4B08  98              cwde
4B09  3B C2           cmp ax, dx
4B0B  7E 31           jle 0x4b3e
4B0D  B8 05 00        mov ax, 5
4B10  50              push ax
4B11  C4 7E 06        les di, ptr [bp + 6]
4B14  06              push es
4B15  57              push di
4B16  0E              push cs
4B17  E8 BD DB        call 0x26d7
4B1A  08 C0           or al, al
4B1C  75 16           jne 0x4b34
4B1E  C4 7E 06        les di, ptr [bp + 6]
4B21  06              push es
4B22  57              push di
4B23  0E              push cs
4B24  E8 BE E0        call 0x2be5
4B27  98              cwde
4B28  8B D0           mov dx, ax
4B2A  8A 46 FF        mov al, byte ptr [bp - 1]
4B2D  98              cwde
4B2E  F7 EA           imul dx
4B30  09 C0           or ax, ax
4B32  7D 0A           jge 0x4b3e
loc_4B34:
4B34  8B 46 FE        mov ax, word ptr [bp - 2]
4B37  C4 7E 06        les di, ptr [bp + 6]
4B3A  26 89 45 07     mov word ptr es:[di + 7], ax
loc_4B3E:
4B3E  89 EC           mov sp, bp
4B40  5D              pop bp
4B41  CA 04 00        retf 4
; data (not reached as code), 32 bytes
4B44                  db 3A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; :...............
4B54                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:4B64  (found by: call)
sub_4B64:
4B64  55              push bp
4B65  89 E5           mov bp, sp
4B67  C4 7E 06        les di, ptr [bp + 6]
4B6A  26 8A 45 06     mov al, byte ptr es:[di + 6]
4B6E  30 E4           xor ah, ah
4B70  50              push ax
4B71  E8 E9 B8        call 0x45d
4B74  08 C0           or al, al
4B76  74 1A           je 0x4b92
4B78  C4 7E 06        les di, ptr [bp + 6]
4B7B  26 FF 75 09     push word ptr es:[di + 9]
4B7F  C4 7E 06        les di, ptr [bp + 6]
4B82  06              push es
4B83  57              push di
4B84  0E              push cs
4B85  E8 FE E0        call 0x2c86
4B88  C4 7E 06        les di, ptr [bp + 6]
4B8B  26 89 45 07     mov word ptr es:[di + 7], ax
4B8F  E9 A7 01        jmp 0x4d39
loc_4B92:
4B92  C4 7E 06        les di, ptr [bp + 6]
4B95  26 80 7D 12 09  cmp byte ptr es:[di + 0x12], 9
4B9A  74 27           je 0x4bc3
4B9C  C4 7E 06        les di, ptr [bp + 6]
4B9F  26 80 7D 12 0B  cmp byte ptr es:[di + 0x12], 0xb
4BA4  74 03           je 0x4ba9
4BA6  E9 A7 00        jmp 0x4c50
loc_4BA9:
4BA9  C4 7E 06        les di, ptr [bp + 6]
4BAC  06              push es
4BAD  57              push di
4BAE  0E              push cs
4BAF  E8 33 E0        call 0x2be5
4BB2  98              cwde
4BB3  8B D0           mov dx, ax
4BB5  A0 F7 82        mov al, byte ptr [0x82f7]
4BB8  98              cwde
4BB9  F7 EA           imul dx
4BBB  3D 14 00        cmp ax, 0x14
4BBE  7F 03           jg 0x4bc3
4BC0  E9 8D 00        jmp 0x4c50
loc_4BC3:
4BC3  C4 7E 06        les di, ptr [bp + 6]
4BC6  06              push es
4BC7  57              push di
4BC8  0E              push cs
4BC9  E8 85 DF        call 0x2b51
4BCC  08 C0           or al, al
4BCE  74 60           je 0x4c30
4BD0  C4 7E 06        les di, ptr [bp + 6]
4BD3  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4BD7  BA 14 00        mov dx, 0x14
4BDA  F7 E2           mul dx
4BDC  C4 3E 1B A9     les di, ptr [0xa91b]
4BE0  03 F8           add di, ax
4BE2  26 8A 45 06     mov al, byte ptr es:[di + 6]
4BE6  50              push ax
4BE7  BF 44 4B        mov di, 0x4b44
4BEA  0E              push cs
4BEB  57              push di
4BEC  9A DF 08 E4 23  call far 23E4:08DF
4BF1  74 1E           je 0x4c11
4BF3  E8 24 DA        call 0x261a
4BF6  8B D0           mov dx, ax
4BF8  C4 7E 06        les di, ptr [bp + 6]
4BFB  26 8A 45 0A     mov al, byte ptr es:[di + 0xa]
4BFF  98              cwde
4C00  09 C0           or ax, ax
4C02  79 02           jns 0x4c06
4C04  F7 D8           neg ax
loc_4C06:
4C06  03 C2           add ax, dx
4C08  C4 7E 06        les di, ptr [bp + 6]
4C0B  26 88 45 0C     mov byte ptr es:[di + 0xc], al
4C0F  EB 1D           jmp 0x4c2e
loc_4C11:
4C11  E8 06 DA        call 0x261a
4C14  8B C8           mov cx, ax
4C16  C4 7E 06        les di, ptr [bp + 6]
4C19  26 8A 45 0A     mov al, byte ptr es:[di + 0xa]
4C1D  98              cwde
4C1E  8B D0           mov dx, ax
4C20  B8 26 00        mov ax, 0x26
4C23  2B C2           sub ax, dx
4C25  2B C1           sub ax, cx
4C27  C4 7E 06        les di, ptr [bp + 6]
4C2A  26 88 45 0C     mov byte ptr es:[di + 0xc], al
loc_4C2E:
4C2E  EB 1D           jmp 0x4c4d
loc_4C30:
4C30  E8 E7 D9        call 0x261a
4C33  8B C8           mov cx, ax
4C35  C4 7E 06        les di, ptr [bp + 6]
4C38  26 8A 45 0A     mov al, byte ptr es:[di + 0xa]
4C3C  98              cwde
4C3D  8B D0           mov dx, ax
4C3F  B8 DA FF        mov ax, 0xffda
4C42  2B C2           sub ax, dx
4C44  03 C1           add ax, cx
4C46  C4 7E 06        les di, ptr [bp + 6]
4C49  26 88 45 0C     mov byte ptr es:[di + 0xc], al
loc_4C4D:
4C4D  E9 E0 00        jmp 0x4d30
loc_4C50:
4C50  C4 7E 06        les di, ptr [bp + 6]
4C53  06              push es
4C54  57              push di
4C55  0E              push cs
4C56  E8 F8 DE        call 0x2b51
4C59  08 C0           or al, al
4C5B  74 64           je 0x4cc1
4C5D  B8 14 00        mov ax, 0x14
4C60  31 D2           xor dx, dx
4C62  52              push dx
4C63  50              push ax
4C64  C4 7E 06        les di, ptr [bp + 6]
4C67  06              push es
4C68  57              push di
4C69  0E              push cs
4C6A  E8 5E F6        call 0x42cb
4C6D  50              push ax
4C6E  B8 07 00        mov ax, 7
4C71  50              push ax
4C72  C4 7E 06        les di, ptr [bp + 6]
4C75  06              push es
4C76  57              push di
4C77  0E              push cs
4C78  E8 5C DA        call 0x26d7
4C7B  98              cwde
4C7C  8B F8           mov di, ax
4C7E  D1 E7           shl di, 1
4C80  D1 E7           shl di, 1
4C82  58              pop ax
4C83  03 F8           add di, ax
4C85  8A 85 DB 07     mov al, byte ptr [di + 0x7db]
4C89  30 E4           xor ah, ah
4C8B  31 D2           xor dx, dx
4C8D  52              push dx
4C8E  50              push ax
4C8F  9A 56 0D 4B 21  call far 214B:0D56
4C94  C4 7E 06        les di, ptr [bp + 6]
4C97  26 88 45 0C     mov byte ptr es:[di + 0xc], al
4C9B  B8 28 00        mov ax, 0x28
4C9E  50              push ax
4C9F  C4 7E 06        les di, ptr [bp + 6]
4CA2  06              push es
4CA3  57              push di
4CA4  0E              push cs
4CA5  E8 C5 E0        call 0x2d6d
4CA8  08 C0           or al, al
4CAA  74 13           je 0x4cbf
4CAC  C4 7E 06        les di, ptr [bp + 6]
4CAF  06              push es
4CB0  57              push di
4CB1  0E              push cs
4CB2  E8 30 DF        call 0x2be5
4CB5  98              cwde
4CB6  F7 D8           neg ax
4CB8  C4 7E 06        les di, ptr [bp + 6]
4CBB  26 88 45 0C     mov byte ptr es:[di + 0xc], al
loc_4CBF:
4CBF  EB 6F           jmp 0x4d30
loc_4CC1:
4CC1  C4 7E 06        les di, ptr [bp + 6]
4CC4  06              push es
4CC5  57              push di
4CC6  0E              push cs
4CC7  E8 01 F6        call 0x42cb
4CCA  50              push ax
4CCB  B8 06 00        mov ax, 6
4CCE  50              push ax
4CCF  C4 7E 06        les di, ptr [bp + 6]
4CD2  06              push es
4CD3  57              push di
4CD4  0E              push cs
4CD5  E8 FF D9        call 0x26d7
4CD8  98              cwde
4CD9  D1 E0           shl ax, 1
4CDB  D1 E0           shl ax, 1
4CDD  50              push ax
4CDE  B8 05 00        mov ax, 5
4CE1  50              push ax
4CE2  C4 7E 06        les di, ptr [bp + 6]
4CE5  06              push es
4CE6  57              push di
4CE7  0E              push cs
4CE8  E8 EC D9        call 0x26d7
4CEB  98              cwde
4CEC  8B F8           mov di, ax
4CEE  B1 03           mov cl, 3
4CF0  D3 E7           shl di, cl
4CF2  58              pop ax
4CF3  03 F8           add di, ax
4CF5  58              pop ax
4CF6  03 F8           add di, ax
4CF8  8A 85 CB 07     mov al, byte ptr [di + 0x7cb]
4CFC  C4 7E 06        les di, ptr [bp + 6]
4CFF  26 88 45 0C     mov byte ptr es:[di + 0xc], al
4D03  C4 7E 06        les di, ptr [bp + 6]
4D06  81 C7 0C 00     add di, 0xc
4D0A  06              push es
4D0B  57              push di
4D0C  B0 00           mov al, 0
4D0E  50              push ax
4D0F  B8 2A 00        mov ax, 0x2a
4D12  31 D2           xor dx, dx
4D14  52              push dx
4D15  50              push ax
4D16  A0 F7 82        mov al, byte ptr [0x82f7]
4D19  98              cwde
4D1A  09 C0           or ax, ax
4D1C  79 02           jns 0x4d20
4D1E  F7 D8           neg ax
loc_4D20:
4D20  D1 E0           shl ax, 1
4D22  99              cdq
4D23  52              push dx
4D24  50              push ax
4D25  9A 1C 0D 4B 21  call far 214B:0D1C
4D2A  50              push ax
4D2B  9A 31 20 4B 21  call far 214B:2031
loc_4D30:
4D30  C4 7E 06        les di, ptr [bp + 6]
4D33  06              push es
4D34  57              push di
4D35  0E              push cs
4D36  E8 EF FC        call 0x4a28
loc_4D39:
4D39  89 EC           mov sp, bp
4D3B  5D              pop bp
4D3C  CA 04 00        retf 4

; ---- routine 0791:4D3F  (found by: call)
sub_4D3F:
4D3F  55              push bp
4D40  89 E5           mov bp, sp
4D42  C4 7E 06        les di, ptr [bp + 6]
4D45  26 8A 45 06     mov al, byte ptr es:[di + 6]
4D49  30 E4           xor ah, ah
4D4B  50              push ax
4D4C  E8 0E B7        call 0x45d
4D4F  08 C0           or al, al
4D51  74 15           je 0x4d68
4D53  C4 7E 06        les di, ptr [bp + 6]
4D56  26 FF 35        push word ptr es:[di]
4D59  C4 7E 06        les di, ptr [bp + 6]
4D5C  06              push es
4D5D  57              push di
4D5E  0E              push cs
4D5F  E8 56 E1        call 0x2eb8
4D62  08 C0           or al, al
4D64  75 02           jne 0x4d68
4D66  EB 3B           jmp 0x4da3
loc_4D68:
4D68  C4 7E 06        les di, ptr [bp + 6]
4D6B  26 C6 45 12 0D  mov byte ptr es:[di + 0x12], 0xd
4D70  C4 7E 06        les di, ptr [bp + 6]
4D73  26 8B 05        mov ax, word ptr es:[di]
4D76  C4 7E 06        les di, ptr [bp + 6]
4D79  26 89 45 07     mov word ptr es:[di + 7], ax
4D7D  E8 9A D8        call 0x261a
4D80  05 04 00        add ax, 4
4D83  C4 7E 06        les di, ptr [bp + 6]
4D86  26 88 45 10     mov byte ptr es:[di + 0x10], al
4D8A  C4 7E 06        les di, ptr [bp + 6]
4D8D  26 8A 45 06     mov al, byte ptr es:[di + 6]
4D91  30 E4           xor ah, ah
4D93  50              push ax
4D94  E8 C6 B6        call 0x45d
4D97  08 C0           or al, al
4D99  74 08           je 0x4da3
4D9B  C4 7E 06        les di, ptr [bp + 6]
4D9E  26 80 45 10 0A  add byte ptr es:[di + 0x10], 0xa
loc_4DA3:
4DA3  89 EC           mov sp, bp
4DA5  5D              pop bp
4DA6  CA 04 00        retf 4

; ---- routine 0791:4DA9  (found by: call)
sub_4DA9:
4DA9  55              push bp
4DAA  89 E5           mov bp, sp
4DAC  83 EC 02        sub sp, 2
4DAF  C4 7E 06        les di, ptr [bp + 6]
4DB2  26 FF 75 0D     push word ptr es:[di + 0xd]
4DB6  9A FB 2F 71 17  call far 1771:2FFB
4DBB  30 E4           xor ah, ah
4DBD  8B D0           mov dx, ax
4DBF  B8 12 00        mov ax, 0x12
4DC2  2B C2           sub ax, dx
4DC4  50              push ax
4DC5  9A D0 06 4B 21  call far 214B:06D0
4DCA  08 C0           or al, al
4DCC  75 11           jne 0x4ddf
4DCE  B8 04 00        mov ax, 4
4DD1  50              push ax
4DD2  C4 7E 06        les di, ptr [bp + 6]
4DD5  06              push es
4DD6  57              push di
4DD7  0E              push cs
4DD8  E8 FC D8        call 0x26d7
4DDB  08 C0           or al, al
4DDD  74 37           je 0x4e16
loc_4DDF:
4DDF  A0 0B 83        mov al, byte ptr [0x830b]
4DE2  30 E4           xor ah, ah
4DE4  BA 16 00        mov dx, 0x16
4DE7  F7 E2           mul dx
4DE9  8B F8           mov di, ax
4DEB  FF B5 F5 80     push word ptr [di - 0x7f0b]
4DEF  9A FB 2F 71 17  call far 1771:2FFB
4DF4  30 E4           xor ah, ah
4DF6  50              push ax
4DF7  9A B1 06 4B 21  call far 214B:06B1
4DFC  50              push ax
4DFD  C4 7E 06        les di, ptr [bp + 6]
4E00  26 FF 75 0D     push word ptr es:[di + 0xd]
4E04  9A FB 2F 71 17  call far 1771:2FFB
4E09  30 E4           xor ah, ah
4E0B  50              push ax
4E0C  9A B1 06 4B 21  call far 214B:06B1
4E11  5A              pop dx
4E12  3B C2           cmp ax, dx
4E14  7F 04           jg 0x4e1a
loc_4E16:
4E16  B0 00           mov al, 0
4E18  EB 02           jmp 0x4e1c
loc_4E1A:
4E1A  B0 01           mov al, 1
loc_4E1C:
4E1C  88 46 FF        mov byte ptr [bp - 1], al
4E1F  8A 46 FF        mov al, byte ptr [bp - 1]
4E22  89 EC           mov sp, bp
4E24  5D              pop bp
4E25  CA 04 00        retf 4

; ---- routine 0791:4E28  (found by: call)
sub_4E28:
4E28  55              push bp
4E29  89 E5           mov bp, sp
4E2B  83 EC 04        sub sp, 4
4E2E  8B 7E 04        mov di, word ptr [bp + 4]
4E31  36 C4 7D 06     les di, ptr ss:[di + 6]
4E35  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
4E39  BA 14 00        mov dx, 0x14
4E3C  F7 E2           mul dx
4E3E  C4 3E 1B A9     les di, ptr [0xa91b]
4E42  03 F8           add di, ax
4E44  89 7E FC        mov word ptr [bp - 4], di
4E47  8C 46 FE        mov word ptr [bp - 2], es
4E4A  E8 CD D7        call 0x261a
4E4D  05 18 00        add ax, 0x18
4E50  50              push ax
4E51  8B 7E 04        mov di, word ptr [bp + 4]
4E54  36 C4 7D 06     les di, ptr ss:[di + 6]
4E58  06              push es
4E59  57              push di
4E5A  0E              push cs
4E5B  E8 87 DD        call 0x2be5
4E5E  98              cwde
4E5F  8B D0           mov dx, ax
4E61  8B 7E 04        mov di, word ptr [bp + 4]
4E64  36 C4 7D 06     les di, ptr ss:[di + 6]
4E68  26 8A 45 01     mov al, byte ptr es:[di + 1]
4E6C  98              cwde
4E6D  F7 EA           imul dx
4E6F  5A              pop dx
4E70  3B C2           cmp ax, dx
4E72  7E 26           jle 0x4e9a
4E74  8B 7E 04        mov di, word ptr [bp + 4]
4E77  36 C4 7D 06     les di, ptr ss:[di + 6]
4E7B  26 8A 05        mov al, byte ptr es:[di]
4E7E  98              cwde
4E7F  09 C0           or ax, ax
4E81  79 02           jns 0x4e85
4E83  F7 D8           neg ax
loc_4E85:
4E85  3D 03 00        cmp ax, 3
4E88  7E 10           jle 0x4e9a
4E8A  8B 7E 04        mov di, word ptr [bp + 4]
4E8D  36 C4 7D 06     les di, ptr ss:[di + 6]
4E91  06              push es
4E92  57              push di
4E93  0E              push cs
4E94  E8 5F EF        call 0x3df6
4E97  E9 6C 01        jmp 0x5006
loc_4E9A:
4E9A  8B 7E 04        mov di, word ptr [bp + 4]
4E9D  36 C4 7D 06     les di, ptr ss:[di + 6]
4EA1  06              push es
4EA2  57              push di
4EA3  0E              push cs
4EA4  E8 3E DD        call 0x2be5
4EA7  98              cwde
4EA8  8B D0           mov dx, ax
4EAA  8B 7E 04        mov di, word ptr [bp + 4]
4EAD  36 C4 7D 06     les di, ptr ss:[di + 6]
4EB1  26 8A 45 01     mov al, byte ptr es:[di + 1]
4EB5  98              cwde
4EB6  F7 EA           imul dx
4EB8  3D F8 FF        cmp ax, 0xfff8
4EBB  7C 08           jl 0x4ec5
4EBD  E8 5A D7        call 0x261a
4EC0  3D 01 00        cmp ax, 1
4EC3  75 10           jne 0x4ed5
loc_4EC5:
4EC5  8B 7E 04        mov di, word ptr [bp + 4]
4EC8  36 C4 7D 06     les di, ptr ss:[di + 6]
4ECC  06              push es
4ECD  57              push di
4ECE  0E              push cs
4ECF  E8 51 E4        call 0x3323
4ED2  E9 31 01        jmp 0x5006
loc_4ED5:
4ED5  C4 7E FC        les di, ptr [bp - 4]
4ED8  26 8A 45 06     mov al, byte ptr es:[di + 6]
4EDC  3C 03           cmp al, 3
4EDE  74 04           je 0x4ee4
4EE0  3C 04           cmp al, 4
4EE2  75 42           jne 0x4f26
loc_4EE4:
4EE4  B8 01 00        mov ax, 1
4EE7  50              push ax
4EE8  8B 7E 04        mov di, word ptr [bp + 4]
4EEB  36 C4 7D 06     les di, ptr ss:[di + 6]
4EEF  06              push es
4EF0  57              push di
4EF1  0E              push cs
4EF2  E8 E2 D7        call 0x26d7
4EF5  08 C0           or al, al
4EF7  74 1D           je 0x4f16
4EF9  8B 7E 04        mov di, word ptr [bp + 4]
4EFC  36 C4 7D 06     les di, ptr ss:[di + 6]
4F00  26 8A 45 06     mov al, byte ptr es:[di + 6]
4F04  30 E4           xor ah, ah
4F06  50              push ax
4F07  8B 7E 04        mov di, word ptr [bp + 4]
4F0A  36 C4 7D 06     les di, ptr ss:[di + 6]
4F0E  06              push es
4F0F  57              push di
4F10  0E              push cs
4F11  E8 38 E9        call 0x384c
4F14  EB 0D           jmp 0x4f23
loc_4F16:
4F16  8B 7E 04        mov di, word ptr [bp + 4]
4F19  36 C4 7D 06     les di, ptr ss:[di + 6]
4F1D  06              push es
4F1E  57              push di
4F1F  0E              push cs
4F20  E8 00 E4        call 0x3323
loc_4F23:
4F23  E9 E0 00        jmp 0x5006
loc_4F26:
4F26  3C 07           cmp al, 7
4F28  74 04           je 0x4f2e
4F2A  3C 08           cmp al, 8
4F2C  75 4F           jne 0x4f7d
loc_4F2E:
4F2E  B8 01 00        mov ax, 1
4F31  50              push ax
4F32  8B 7E 04        mov di, word ptr [bp + 4]
4F35  36 C4 7D 06     les di, ptr ss:[di + 6]
4F39  06              push es
4F3A  57              push di
4F3B  0E              push cs
4F3C  E8 98 D7        call 0x26d7
4F3F  08 C0           or al, al
4F41  74 2A           je 0x4f6d
4F43  B8 03 00        mov ax, 3
4F46  50              push ax
4F47  9A D0 06 4B 21  call far 214B:06D0
4F4C  08 C0           or al, al
4F4E  75 1D           jne 0x4f6d
4F50  8B 7E 04        mov di, word ptr [bp + 4]
4F53  36 C4 7D 06     les di, ptr ss:[di + 6]
4F57  26 8A 45 06     mov al, byte ptr es:[di + 6]
4F5B  30 E4           xor ah, ah
4F5D  50              push ax
4F5E  8B 7E 04        mov di, word ptr [bp + 4]
4F61  36 C4 7D 06     les di, ptr ss:[di + 6]
4F65  06              push es
4F66  57              push di
4F67  0E              push cs
4F68  E8 E1 E8        call 0x384c
4F6B  EB 0D           jmp 0x4f7a
loc_4F6D:
4F6D  8B 7E 04        mov di, word ptr [bp + 4]
4F70  36 C4 7D 06     les di, ptr ss:[di + 6]
4F74  06              push es
4F75  57              push di
4F76  0E              push cs
4F77  E8 A9 E3        call 0x3323
loc_4F7A:
4F7A  E9 89 00        jmp 0x5006
loc_4F7D:
4F7D  3C 0A           cmp al, 0xa
4F7F  74 04           je 0x4f85
4F81  3C 0B           cmp al, 0xb
4F83  75 1D           jne 0x4fa2
loc_4F85:
4F85  8B 7E 04        mov di, word ptr [bp + 4]
4F88  36 C4 7D 06     les di, ptr ss:[di + 6]
4F8C  26 8A 45 06     mov al, byte ptr es:[di + 6]
4F90  30 E4           xor ah, ah
4F92  50              push ax
4F93  8B 7E 04        mov di, word ptr [bp + 4]
4F96  36 C4 7D 06     les di, ptr ss:[di + 6]
4F9A  06              push es
4F9B  57              push di
4F9C  0E              push cs
4F9D  E8 AC E8        call 0x384c
4FA0  EB 64           jmp 0x5006
loc_4FA2:
4FA2  3C 0D           cmp al, 0xd
4FA4  74 04           je 0x4faa
4FA6  3C 0C           cmp al, 0xc
4FA8  75 4F           jne 0x4ff9
loc_4FAA:
4FAA  C4 7E FC        les di, ptr [bp - 4]
4FAD  26 80 7D 06 0C  cmp byte ptr es:[di + 6], 0xc
4FB2  74 04           je 0x4fb8
4FB4  B0 00           mov al, 0
4FB6  EB 02           jmp 0x4fba
loc_4FB8:
4FB8  B0 01           mov al, 1
loc_4FBA:
4FBA  98              cwde
4FBB  8B F8           mov di, ax
4FBD  8A 85 E4 07     mov al, byte ptr [di + 0x7e4]
4FC1  30 E4           xor ah, ah
4FC3  50              push ax
4FC4  9A D0 06 4B 21  call far 214B:06D0
4FC9  08 C0           or al, al
4FCB  74 0F           je 0x4fdc
4FCD  8B 7E 04        mov di, word ptr [bp + 4]
4FD0  36 C4 7D 06     les di, ptr ss:[di + 6]
4FD4  06              push es
4FD5  57              push di
4FD6  0E              push cs
4FD7  E8 49 E3        call 0x3323
4FDA  EB 1B           jmp 0x4ff7
loc_4FDC:
4FDC  8B 7E 04        mov di, word ptr [bp + 4]
4FDF  36 C4 7D 06     les di, ptr ss:[di + 6]
4FE3  26 8A 45 06     mov al, byte ptr es:[di + 6]
4FE7  30 E4           xor ah, ah
4FE9  50              push ax
4FEA  8B 7E 04        mov di, word ptr [bp + 4]
4FED  36 C4 7D 06     les di, ptr ss:[di + 6]
4FF1  06              push es
4FF2  57              push di
4FF3  0E              push cs
4FF4  E8 55 E8        call 0x384c
loc_4FF7:
4FF7  EB 0D           jmp 0x5006
loc_4FF9:
4FF9  8B 7E 04        mov di, word ptr [bp + 4]
4FFC  36 C4 7D 06     les di, ptr ss:[di + 6]
5000  06              push es
5001  57              push di
5002  0E              push cs
5003  E8 1D E3        call 0x3323
loc_5006:
5006  89 EC           mov sp, bp
5008  5D              pop bp
5009  C2 02 00        ret 2

