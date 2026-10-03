; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 11 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:6337  (found by: call)
sub_6337:
6337  55              push bp
6338  89 E5           mov bp, sp
633A  83 EC 04        sub sp, 4
633D  A0 0B 83        mov al, byte ptr [0x830b]
6340  30 E4           xor ah, ah
6342  50              push ax
6343  E8 17 A1        call 0x45d
6346  08 C0           or al, al
6348  74 4D           je 0x6397
634A  A0 0B 83        mov al, byte ptr [0x830b]
634D  30 E4           xor ah, ah
634F  BA 16 00        mov dx, 0x16
6352  F7 E2           mul dx
6354  8B F8           mov di, ax
6356  81 C7 E8 80     add di, 0x80e8
635A  89 7E FC        mov word ptr [bp - 4], di
635D  8C 5E FE        mov word ptr [bp - 2], ds
6360  C4 7E FC        les di, ptr [bp - 4]
6363  26 FF 75 09     push word ptr es:[di + 9]
6367  C4 7E FC        les di, ptr [bp - 4]
636A  06              push es
636B  57              push di
636C  0E              push cs
636D  E8 16 C9        call 0x2c86
6370  C4 7E FC        les di, ptr [bp - 4]
6373  26 89 45 07     mov word ptr es:[di + 7], ax
6377  E8 1C C6        call 0x2996
637A  98              cwde
637B  8B F8           mov di, ax
637D  8A 85 68 06     mov al, byte ptr [di + 0x668]
6381  30 E4           xor ah, ah
6383  50              push ax
6384  B8 0A 00        mov ax, 0xa
6387  50              push ax
6388  9A B1 06 4B 21  call far 214B:06B1
638D  40              inc ax
638E  5A              pop dx
638F  03 C2           add ax, dx
6391  A2 0B 83        mov byte ptr [0x830b], al
6394  E8 7E C6        call 0x2a15
loc_6397:
6397  A0 0B 83        mov al, byte ptr [0x830b]
639A  30 E4           xor ah, ah
639C  BA 16 00        mov dx, 0x16
639F  F7 E2           mul dx
63A1  8B F8           mov di, ax
63A3  81 C7 E8 80     add di, 0x80e8
63A7  89 7E FC        mov word ptr [bp - 4], di
63AA  8C 5E FE        mov word ptr [bp - 2], ds
63AD  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
63B2  74 0F           je 0x63c3
63B4  C4 7E FC        les di, ptr [bp - 4]
63B7  26 8B 05        mov ax, word ptr es:[di]
63BA  C4 7E FC        les di, ptr [bp - 4]
63BD  26 89 45 07     mov word ptr es:[di + 7], ax
63C1  EB 7C           jmp 0x643f
loc_63C3:
63C3  9A FA 06 4B 21  call far 214B:06FA
63C8  08 C0           or al, al
63CA  74 3C           je 0x6408
63CC  B8 19 00        mov ax, 0x19
63CF  50              push ax
63D0  9A B1 06 4B 21  call far 214B:06B1
63D5  05 0A 00        add ax, 0xa
63D8  50              push ax
63D9  C4 7E FC        les di, ptr [bp - 4]
63DC  06              push es
63DD  57              push di
63DE  0E              push cs
63DF  E8 03 C8        call 0x2be5
63E2  98              cwde
63E3  5A              pop dx
63E4  F7 EA           imul dx
63E6  C4 7E FC        les di, ptr [bp - 4]
63E9  26 88 45 08     mov byte ptr es:[di + 8], al
63ED  9A FA 06 4B 21  call far 214B:06FA
63F2  98              cwde
63F3  8B F8           mov di, ax
63F5  8A 85 20 79     mov al, byte ptr [di + 0x7920]
63F9  98              cwde
63FA  B9 07 00        mov cx, 7
63FD  F7 E9           imul cx
63FF  C4 7E FC        les di, ptr [bp - 4]
6402  26 88 45 07     mov byte ptr es:[di + 7], al
6406  EB 37           jmp 0x643f
loc_6408:
6408  C4 7E FC        les di, ptr [bp - 4]
640B  06              push es
640C  57              push di
640D  0E              push cs
640E  E8 D4 C7        call 0x2be5
6411  98              cwde
6412  B9 24 00        mov cx, 0x24
6415  F7 E9           imul cx
6417  C4 7E FC        les di, ptr [bp - 4]
641A  26 88 45 08     mov byte ptr es:[di + 8], al
641E  B8 05 00        mov ax, 5
6421  50              push ax
6422  9A B1 06 4B 21  call far 214B:06B1
6427  50              push ax
6428  9A FA 06 4B 21  call far 214B:06FA
642D  98              cwde
642E  8B F8           mov di, ax
6430  8A 85 20 79     mov al, byte ptr [di + 0x7920]
6434  98              cwde
6435  5A              pop dx
6436  F7 EA           imul dx
6438  C4 7E FC        les di, ptr [bp - 4]
643B  26 88 45 07     mov byte ptr es:[di + 7], al
loc_643F:
643F  89 EC           mov sp, bp
6441  5D              pop bp
6442  C3              ret

; ---- routine 0791:6443  (found by: call)
sub_6443:
6443  55              push bp
6444  89 E5           mov bp, sp
6446  83 EC 0A        sub sp, 0xa
6449  8B 46 06        mov ax, word ptr [bp + 6]
644C  BA 16 00        mov dx, 0x16
644F  F7 E2           mul dx
6451  8B F8           mov di, ax
6453  81 C7 E8 80     add di, 0x80e8
6457  89 7E FB        mov word ptr [bp - 5], di
645A  8C 5E FD        mov word ptr [bp - 3], ds
645D  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
6462  74 08           je 0x646c
6464  B0 27           mov al, 0x27
6466  50              push ax
6467  E8 39 C6        call 0x2aa3
646A  EB 53           jmp 0x64bf
loc_646C:
646C  B0 26           mov al, 0x26
646E  50              push ax
646F  E8 31 C6        call 0x2aa3
6472  C4 7E FB        les di, ptr [bp - 5]
6475  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
6479  BA 14 00        mov dx, 0x14
647C  F7 E2           mul dx
647E  C4 3E 1B A9     les di, ptr [0xa91b]
6482  03 F8           add di, ax
6484  26 FF 45 0A     inc word ptr es:[di + 0xa]
6488  C4 3E 2A 7C     les di, ptr [0x7c2a]
648C  06              push es
648D  57              push di
648E  9A 03 5A 71 17  call far 1771:5A03
6493  08 C0           or al, al
6495  74 28           je 0x64bf
6497  C4 7E FB        les di, ptr [bp - 5]
649A  26 FF 75 0D     push word ptr es:[di + 0xd]
649E  8A 46 08        mov al, byte ptr [bp + 8]
64A1  98              cwde
64A2  8B F8           mov di, ax
64A4  D1 E7           shl di, 1
64A6  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
64AA  BA BF 00        mov dx, 0xbf
64AD  F7 E2           mul dx
64AF  C4 3E 17 A9     les di, ptr [0xa917]
64B3  03 F8           add di, ax
64B5  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
64B9  30 E4           xor ah, ah
64BB  50              push ax
64BC  E8 F8 4E        call 0xb3b7
loc_64BF:
64BF  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
64C4  74 04           je 0x64ca
64C6  B0 00           mov al, 0
64C8  EB 02           jmp 0x64cc
loc_64CA:
64CA  B0 01           mov al, 1
loc_64CC:
64CC  98              cwde
64CD  8B F8           mov di, ax
64CF  8A 85 20 79     mov al, byte ptr [di + 0x7920]
64D3  98              cwde
64D4  50              push ax
64D5  B0 01           mov al, 1
64D7  50              push ax
64D8  C4 7E FB        les di, ptr [bp - 5]
64DB  06              push es
64DC  57              push di
64DD  0E              push cs
64DE  E8 E4 17        call 0x7cc5
64E1  8A 46 08        mov al, byte ptr [bp + 8]
64E4  88 46 FF        mov byte ptr [bp - 1], al
64E7  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
64EC  74 0F           je 0x64fd
64EE  80 7E 08 00     cmp byte ptr [bp + 8], 0
64F2  74 04           je 0x64f8
64F4  B0 00           mov al, 0
64F6  EB 02           jmp 0x64fa
loc_64F8:
64F8  B0 01           mov al, 1
loc_64FA:
64FA  88 46 08        mov byte ptr [bp + 8], al
loc_64FD:
64FD  8A 46 08        mov al, byte ptr [bp + 8]
6500  98              cwde
6501  8B F8           mov di, ax
6503  80 BD F0 80 0B  cmp byte ptr [di - 0x7f10], 0xb
6508  73 0A           jae 0x6514
650A  8A 46 08        mov al, byte ptr [bp + 8]
650D  98              cwde
650E  8B F8           mov di, ax
6510  FE 85 F0 80     inc byte ptr [di - 0x7f10]
loc_6514:
6514  8A 46 08        mov al, byte ptr [bp + 8]
6517  98              cwde
6518  8B F8           mov di, ax
651A  8A 85 F0 80     mov al, byte ptr [di - 0x7f10]
651E  30 E4           xor ah, ah
6520  BA 03 00        mov dx, 3
6523  F7 E2           mul dx
6525  8B C8           mov cx, ax
6527  8A 46 08        mov al, byte ptr [bp + 8]
652A  98              cwde
652B  BA 21 00        mov dx, 0x21
652E  F7 E2           mul dx
6530  8B F8           mov di, ax
6532  03 F9           add di, cx
6534  81 C7 D1 7B     add di, 0x7bd1
6538  89 7E F7        mov word ptr [bp - 9], di
653B  8C 5E F9        mov word ptr [bp - 7], ds
653E  C4 7E FB        les di, ptr [bp - 5]
6541  06              push es
6542  57              push di
6543  0E              push cs
6544  E8 6A C6        call 0x2bb1
6547  30 E4           xor ah, ah
6549  D1 E0           shl ax, 1
654B  8B C8           mov cx, ax
654D  8A 46 FF        mov al, byte ptr [bp - 1]
6550  98              cwde
6551  8B F8           mov di, ax
6553  D1 E7           shl di, 1
6555  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
6559  BA BF 00        mov dx, 0xbf
655C  F7 E2           mul dx
655E  C4 3E 17 A9     les di, ptr [0xa917]
6562  03 F8           add di, ax
6564  03 F9           add di, cx
6566  26 8B 45 FE     mov ax, word ptr es:[di - 2]
656A  C4 7E F7        les di, ptr [bp - 9]
656D  26 89 05        mov word ptr es:[di], ax
6570  8A 46 04        mov al, byte ptr [bp + 4]
6573  C4 7E F7        les di, ptr [bp - 9]
6576  26 88 45 02     mov byte ptr es:[di + 2], al
657A  80 3E 24 83 00  cmp byte ptr [0x8324], 0
657F  75 07           jne 0x6588
6581  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
6586  74 08           je 0x6590
loc_6588:
6588  C4 7E F7        les di, ptr [bp - 9]
658B  26 80 45 02 80  add byte ptr es:[di + 2], 0x80
loc_6590:
6590  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
6595  75 07           jne 0x659e
6597  8A 46 08        mov al, byte ptr [bp + 8]
659A  50              push ax
659B  E8 82 D6        call 0x3c20
loc_659E:
659E  89 EC           mov sp, bp
65A0  5D              pop bp
65A1  C2 06 00        ret 6

; ---- routine 0791:65A4  (found by: call)
sub_65A4:
65A4  55              push bp
65A5  89 E5           mov bp, sp
65A7  83 EC 06        sub sp, 6
65AA  C7 46 FE 01 00  mov word ptr [bp - 2], 1
65AF  EB 03           jmp 0x65b4
loc_65B1:
65B1  FF 46 FE        inc word ptr [bp - 2]
loc_65B4:
65B4  8B 46 FE        mov ax, word ptr [bp - 2]
65B7  BA 16 00        mov dx, 0x16
65BA  F7 E2           mul dx
65BC  8B F8           mov di, ax
65BE  81 C7 E8 80     add di, 0x80e8
65C2  89 7E FA        mov word ptr [bp - 6], di
65C5  8C 5E FC        mov word ptr [bp - 4], ds
65C8  C4 7E FA        les di, ptr [bp - 6]
65CB  06              push es
65CC  57              push di
65CD  0E              push cs
65CE  E8 80 C5        call 0x2b51
65D1  08 C0           or al, al
65D3  74 14           je 0x65e9
65D5  FF 76 FE        push word ptr [bp - 2]
65D8  E8 82 9E        call 0x45d
65DB  08 C0           or al, al
65DD  75 0A           jne 0x65e9
65DF  C4 7E FA        les di, ptr [bp - 6]
65E2  26 C6 45 12 06  mov byte ptr es:[di + 0x12], 6
65E7  EB 08           jmp 0x65f1
loc_65E9:
65E9  C4 7E FA        les di, ptr [bp - 6]
65EC  26 C6 45 12 00  mov byte ptr es:[di + 0x12], 0
loc_65F1:
65F1  83 7E FE 16     cmp word ptr [bp - 2], 0x16
65F5  75 BA           jne 0x65b1
65F7  E8 3D FD        call 0x6337
65FA  89 EC           mov sp, bp
65FC  5D              pop bp
65FD  C3              ret

; ---- routine 0791:65FE  (found by: call)
sub_65FE:
65FE  55              push bp
65FF  89 E5           mov bp, sp
6601  83 EC 08        sub sp, 8
6604  C6 06 25 83 01  mov byte ptr [0x8325], 1
6609  B8 04 00        mov ax, 4
660C  50              push ax
660D  E8 31 9E        call 0x441
6610  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6615  EB 03           jmp 0x661a
loc_6617:
6617  FF 46 FE        inc word ptr [bp - 2]
loc_661A:
661A  8B 46 FE        mov ax, word ptr [bp - 2]
661D  BA 16 00        mov dx, 0x16
6620  F7 E2           mul dx
6622  8B F8           mov di, ax
6624  8B 8D E8 80     mov cx, word ptr [di - 0x7f18]
6628  8B 46 FE        mov ax, word ptr [bp - 2]
662B  BA 16 00        mov dx, 0x16
662E  F7 E2           mul dx
6630  8B F8           mov di, ax
6632  89 8D EF 80     mov word ptr [di - 0x7f11], cx
6636  83 7E FE 16     cmp word ptr [bp - 2], 0x16
663A  75 DB           jne 0x6617
663C  A0 39 7C        mov al, byte ptr [0x7c39]
663F  88 46 FD        mov byte ptr [bp - 3], al
6642  80 3E 26 83 00  cmp byte ptr [0x8326], 0
6647  74 03           je 0x664c
6649  E9 93 00        jmp 0x66df
loc_664C:
664C  E8 55 FF        call 0x65a4
664F  80 7E FD 00     cmp byte ptr [bp - 3], 0
6653  74 04           je 0x6659
6655  B0 00           mov al, 0
6657  EB 02           jmp 0x665b
loc_6659:
6659  B0 01           mov al, 1
loc_665B:
665B  50              push ax
665C  E8 14 5B        call 0xc173
665F  C7 46 FE 01 00  mov word ptr [bp - 2], 1
6664  EB 03           jmp 0x6669
loc_6666:
6666  FF 46 FE        inc word ptr [bp - 2]
loc_6669:
6669  8B 46 FE        mov ax, word ptr [bp - 2]
666C  BA 16 00        mov dx, 0x16
666F  F7 E2           mul dx
6671  8B F8           mov di, ax
6673  81 C7 E8 80     add di, 0x80e8
6677  89 7E F9        mov word ptr [bp - 7], di
667A  8C 5E FB        mov word ptr [bp - 5], ds
667D  C4 7E F9        les di, ptr [bp - 7]
6680  06              push es
6681  57              push di
6682  0E              push cs
6683  E8 D0 C2        call 0x2956
6686  08 C0           or al, al
6688  75 4F           jne 0x66d9
668A  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
668F  75 20           jne 0x66b1
6691  C4 7E F9        les di, ptr [bp - 7]
6694  06              push es
6695  57              push di
6696  0E              push cs
6697  E8 B7 C4        call 0x2b51
669A  98              cwde
669B  8B F8           mov di, ax
669D  8A 85 20 79     mov al, byte ptr [di + 0x7920]
66A1  98              cwde
66A2  50              push ax
66A3  B0 00           mov al, 0
66A5  50              push ax
66A6  C4 7E F9        les di, ptr [bp - 7]
66A9  06              push es
66AA  57              push di
66AB  0E              push cs
66AC  E8 16 16        call 0x7cc5
66AF  EB 28           jmp 0x66d9
loc_66B1:
66B1  C4 7E F9        les di, ptr [bp - 7]
66B4  06              push es
66B5  57              push di
66B6  0E              push cs
66B7  E8 97 C4        call 0x2b51
66BA  08 C0           or al, al
66BC  74 04           je 0x66c2
66BE  B0 00           mov al, 0
66C0  EB 02           jmp 0x66c4
loc_66C2:
66C2  B0 01           mov al, 1
loc_66C4:
66C4  98              cwde
66C5  8B F8           mov di, ax
66C7  8A 85 20 79     mov al, byte ptr [di + 0x7920]
66CB  98              cwde
66CC  50              push ax
66CD  B0 00           mov al, 0
66CF  50              push ax
66D0  C4 7E F9        les di, ptr [bp - 7]
66D3  06              push es
66D4  57              push di
66D5  0E              push cs
66D6  E8 EC 15        call 0x7cc5
loc_66D9:
66D9  83 7E FE 16     cmp word ptr [bp - 2], 0x16
66DD  75 87           jne 0x6666
loc_66DF:
66DF  80 7E FD 00     cmp byte ptr [bp - 3], 0
66E3  74 04           je 0x66e9
66E5  B0 00           mov al, 0
66E7  EB 02           jmp 0x66eb
loc_66E9:
66E9  B0 01           mov al, 1
loc_66EB:
66EB  98              cwde
66EC  8B F8           mov di, ax
66EE  8A 95 3C 9B     mov dl, byte ptr [di - 0x64c4]
66F2  8A 46 FD        mov al, byte ptr [bp - 3]
66F5  98              cwde
66F6  8B F8           mov di, ax
66F8  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
66FC  3A C2           cmp al, dl
66FE  77 04           ja 0x6704
6700  B0 00           mov al, 0
6702  EB 02           jmp 0x6706
loc_6704:
6704  B0 01           mov al, 1
loc_6706:
6706  30 E4           xor ah, ah
6708  B9 32 00        mov cx, 0x32
670B  F7 E9           imul cx
670D  8B D8           mov bx, ax
670F  80 7E FD 00     cmp byte ptr [bp - 3], 0
6713  74 04           je 0x6719
6715  B0 00           mov al, 0
6717  EB 02           jmp 0x671b
loc_6719:
6719  B0 01           mov al, 1
loc_671B:
671B  98              cwde
671C  8B F8           mov di, ax
671E  8A 95 3C 9B     mov dl, byte ptr [di - 0x64c4]
6722  8A 46 FD        mov al, byte ptr [bp - 3]
6725  98              cwde
6726  8B F8           mov di, ax
6728  8A 85 3C 9B     mov al, byte ptr [di - 0x64c4]
672C  3A C2           cmp al, dl
672E  73 04           jae 0x6734
6730  B0 00           mov al, 0
6732  EB 02           jmp 0x6736
loc_6734:
6734  B0 01           mov al, 1
loc_6736:
6736  30 E4           xor ah, ah
6738  B9 32 00        mov cx, 0x32
673B  F7 E9           imul cx
673D  05 32 00        add ax, 0x32
6740  03 C3           add ax, bx
6742  A3 2A 83        mov word ptr [0x832a], ax
6745  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
674A  74 05           je 0x6751
674C  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
loc_6751:
6751  89 EC           mov sp, bp
6753  5D              pop bp
6754  C3              ret

; ---- routine 0791:6755  (found by: call)
sub_6755:
6755  55              push bp
6756  89 E5           mov bp, sp
6758  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
675D  7F 04           jg 0x6763
675F  B0 00           mov al, 0
6761  EB 02           jmp 0x6765
loc_6763:
6763  B0 01           mov al, 1
loc_6765:
6765  98              cwde
6766  8B F8           mov di, ax
6768  8A 85 20 79     mov al, byte ptr [di + 0x7920]
676C  98              cwde
676D  B9 27 00        mov cx, 0x27
6770  F7 E9           imul cx
6772  A2 F7 82        mov byte ptr [0x82f7], al
6775  80 3E F6 82 00  cmp byte ptr [0x82f6], 0
677A  75 08           jne 0x6784
677C  B0 28           mov al, 0x28
677E  50              push ax
677F  E8 21 C3        call 0x2aa3
6782  EB 06           jmp 0x678a
loc_6784:
6784  B0 29           mov al, 0x29
6786  50              push ax
6787  E8 19 C3        call 0x2aa3
loc_678A:
678A  C7 06 2A 83 14 00 mov word ptr [0x832a], 0x14
6790  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
6795  75 16           jne 0x67ad
6797  E8 FC C1        call 0x2996
679A  08 C0           or al, al
679C  74 04           je 0x67a2
679E  B0 00           mov al, 0
67A0  EB 02           jmp 0x67a4
loc_67A2:
67A2  B0 01           mov al, 1
loc_67A4:
67A4  50              push ax
67A5  B0 00           mov al, 0
67A7  50              push ax
67A8  E8 56 07        call 0x6f01
67AB  EB 03           jmp 0x67b0
loc_67AD:
67AD  E8 3B 1B        call 0x82eb
loc_67B0:
67B0  89 EC           mov sp, bp
67B2  5D              pop bp
67B3  C2 02 00        ret 2

; ---- routine 0791:67B6  (found by: call)
sub_67B6:
67B6  55              push bp
67B7  89 E5           mov bp, sp
67B9  83 EC 08        sub sp, 8
67BC  BF F7 82        mov di, 0x82f7
67BF  1E              push ds
67C0  57              push di
67C1  B0 DA           mov al, 0xda
67C3  50              push ax
67C4  B0 26           mov al, 0x26
67C6  50              push ax
67C7  9A 31 20 4B 21  call far 214B:2031
67CC  BF F6 82        mov di, 0x82f6
67CF  1E              push ds
67D0  57              push di
67D1  B0 FF           mov al, 0xff
67D3  50              push ax
67D4  B0 01           mov al, 1
67D6  50              push ax
67D7  9A 31 20 4B 21  call far 214B:2031
67DC  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
67E1  74 12           je 0x67f5
67E3  E8 B0 C1        call 0x2996
67E6  08 C0           or al, al
67E8  74 04           je 0x67ee
67EA  B0 00           mov al, 0
67EC  EB 02           jmp 0x67f0
loc_67EE:
67EE  B0 01           mov al, 1
loc_67F0:
67F0  88 46 FD        mov byte ptr [bp - 3], al
67F3  EB 06           jmp 0x67fb
loc_67F5:
67F5  E8 9E C1        call 0x2996
67F8  88 46 FD        mov byte ptr [bp - 3], al
loc_67FB:
67FB  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
6800  74 06           je 0x6808
6802  C6 46 FC 27     mov byte ptr [bp - 4], 0x27
6806  EB 04           jmp 0x680c
loc_6808:
6808  C6 46 FC 26     mov byte ptr [bp - 4], 0x26
loc_680C:
680C  80 7E FD 00     cmp byte ptr [bp - 3], 0
6810  74 04           je 0x6816
6812  B0 00           mov al, 0
6814  EB 02           jmp 0x6818
loc_6816:
6816  B0 01           mov al, 1
loc_6818:
6818  98              cwde
6819  8B F8           mov di, ax
681B  8A 85 68 06     mov al, byte ptr [di + 0x668]
681F  30 E4           xor ah, ah
6821  40              inc ax
6822  BA 16 00        mov dx, 0x16
6825  F7 E2           mul dx
6827  8B F8           mov di, ax
6829  81 C7 E8 80     add di, 0x80e8
682D  89 7E F8        mov word ptr [bp - 8], di
6830  8C 5E FA        mov word ptr [bp - 6], ds
6833  9A FA 06 4B 21  call far 214B:06FA
6838  08 C0           or al, al
683A  74 0E           je 0x684a
683C  B0 24           mov al, 0x24
683E  50              push ax
683F  C4 7E F8        les di, ptr [bp - 8]
6842  06              push es
6843  57              push di
6844  0E              push cs
6845  E8 E0 C2        call 0x2b28
6848  EB 0C           jmp 0x6856
loc_684A:
684A  B0 25           mov al, 0x25
684C  50              push ax
684D  C4 7E F8        les di, ptr [bp - 8]
6850  06              push es
6851  57              push di
6852  0E              push cs
6853  E8 D2 C2        call 0x2b28
loc_6856:
6856  8A 46 FD        mov al, byte ptr [bp - 3]
6859  98              cwde
685A  8B F8           mov di, ax
685C  FE 85 3C 9B     inc byte ptr [di - 0x64c4]
6860  BF 6A A9        mov di, 0xa96a
6863  1E              push ds
6864  57              push di
6865  0E              push cs
6866  E8 A9 9E        call 0x712
6869  80 3E 26 83 00  cmp byte ptr [0x8326], 0
686E  74 09           je 0x6879
6870  8A 46 FC        mov al, byte ptr [bp - 4]
6873  50              push ax
6874  E8 2C C2        call 0x2aa3
6877  EB 4C           jmp 0x68c5
loc_6879:
6879  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
687E  75 26           jne 0x68a6
6880  A0 0B 83        mov al, byte ptr [0x830b]
6883  30 E4           xor ah, ah
6885  BA 16 00        mov dx, 0x16
6888  F7 E2           mul dx
688A  8B F8           mov di, ax
688C  81 C7 E8 80     add di, 0x80e8
6890  1E              push ds
6891  57              push di
6892  0E              push cs
6893  E8 DE C0        call 0x2974
6896  50              push ax
6897  A0 0B 83        mov al, byte ptr [0x830b]
689A  30 E4           xor ah, ah
689C  50              push ax
689D  FF 36 1F 83     push word ptr [0x831f]
68A1  E8 9F FB        call 0x6443
68A4  EB 1F           jmp 0x68c5
loc_68A6:
68A6  8A 46 FC        mov al, byte ptr [bp - 4]
68A9  50              push ax
68AA  E8 F6 C1        call 0x2aa3
68AD  8A 46 FD        mov al, byte ptr [bp - 3]
68B0  98              cwde
68B1  8B F8           mov di, ax
68B3  FE 8D 3C 9B     dec byte ptr [di - 0x64c4]
68B7  E8 31 1A        call 0x82eb
68BA  BF 6A A9        mov di, 0xa96a
68BD  1E              push ds
68BE  57              push di
68BF  0E              push cs
68C0  E8 4F 9E        call 0x712
68C3  EB 21           jmp 0x68e6
loc_68C5:
68C5  E8 36 FD        call 0x65fe
68C8  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
68CD  75 07           jne 0x68d6
68CF  C6 06 37 7C 01  mov byte ptr [0x7c37], 1
68D4  EB 10           jmp 0x68e6
loc_68D6:
68D6  C6 06 20 0C 00  mov byte ptr [0xc20], 0
68DB  A0 3C 7C        mov al, byte ptr [0x7c3c]
68DE  C4 3E 23 A9     les di, ptr [0xa923]
68E2  26 88 45 3F     mov byte ptr es:[di + 0x3f], al
loc_68E6:
68E6  89 EC           mov sp, bp
68E8  5D              pop bp
68E9  C2 02 00        ret 2
; data (not reached as code), 32 bytes
68EC                  db 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
68FC                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:690C  (found by: call)
sub_690C:
690C  55              push bp
690D  89 E5           mov bp, sp
690F  83 EC 04        sub sp, 4
6912  80 3E 27 83 04  cmp byte ptr [0x8327], 4
6917  76 06           jbe 0x691f
6919  55              push bp
691A  E8 38 FE        call 0x6755
691D  EB 61           jmp 0x6980
loc_691F:
691F  80 3E 39 7C 00  cmp byte ptr [0x7c39], 0
6924  75 50           jne 0x6976
6926  80 3E FB 80 00  cmp byte ptr [0x80fb], 0
692B  75 49           jne 0x6976
692D  A0 27 83        mov al, byte ptr [0x8327]
6930  50              push ax
6931  BF EC 68        mov di, 0x68ec
6934  0E              push cs
6935  57              push di
6936  9A DF 08 E4 23  call far 23E4:08DF
693B  74 3F           je 0x697c
693D  B8 20 00        mov ax, 0x20
6940  50              push ax
6941  9A B1 06 4B 21  call far 214B:06B1
6946  50              push ax
6947  A0 27 83        mov al, byte ptr [0x8327]
694A  30 E4           xor ah, ah
694C  8B F8           mov di, ax
694E  8A 85 0C 08     mov al, byte ptr [di + 0x80c]
6952  30 E4           xor ah, ah
6954  50              push ax
6955  A0 0B 83        mov al, byte ptr [0x830b]
6958  30 E4           xor ah, ah
695A  BA 16 00        mov dx, 0x16
695D  F7 E2           mul dx
695F  8B F8           mov di, ax
6961  81 C7 E8 80     add di, 0x80e8
6965  1E              push ds
6966  57              push di
6967  0E              push cs
6968  E8 1F BE        call 0x278a
696B  50              push ax
696C  9A B1 06 4B 21  call far 214B:06B1
6971  5A              pop dx
6972  3B C2           cmp ax, dx
6974  7E 06           jle 0x697c
loc_6976:
6976  55              push bp
6977  E8 3C FE        call 0x67b6
697A  EB 04           jmp 0x6980
loc_697C:
697C  55              push bp
697D  E8 D5 FD        call 0x6755
loc_6980:
6980  C6 06 24 83 00  mov byte ptr [0x8324], 0
6985  C6 06 FB 80 00  mov byte ptr [0x80fb], 0
698A  89 EC           mov sp, bp
698C  5D              pop bp
698D  C3              ret

; ---- routine 0791:698E  (found by: call)
sub_698E:
698E  55              push bp
698F  89 E5           mov bp, sp
6991  A0 0B 83        mov al, byte ptr [0x830b]
6994  30 E4           xor ah, ah
6996  50              push ax
6997  E8 C3 9A        call 0x45d
699A  08 C0           or al, al
699C  75 09           jne 0x69a7
699E  9A FA 06 4B 21  call far 214B:06FA
69A3  08 C0           or al, al
69A5  74 05           je 0x69ac
loc_69A7:
69A7  E8 C4 04        call 0x6e6e
69AA  EB 0D           jmp 0x69b9
loc_69AC:
69AC  C6 06 27 83 00  mov byte ptr [0x8327], 0
69B1  C6 06 39 7C 01  mov byte ptr [0x7c39], 1
69B6  E8 53 FF        call 0x690c
loc_69B9:
69B9  89 EC           mov sp, bp
69BB  5D              pop bp
69BC  C3              ret

; ---- routine 0791:69BD  (found by: call)
sub_69BD:
69BD  55              push bp
69BE  89 E5           mov bp, sp
69C0  C4 7E 06        les di, ptr [bp + 6]
69C3  26 8B 45 09     mov ax, word ptr es:[di + 9]
69C7  C4 7E 06        les di, ptr [bp + 6]
69CA  26 89 45 07     mov word ptr es:[di + 7], ax
69CE  C4 7E 06        les di, ptr [bp + 6]
69D1  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
69D5  BA 14 00        mov dx, 0x14
69D8  F7 E2           mul dx
69DA  C4 3E 1B A9     les di, ptr [0xa91b]
69DE  03 F8           add di, ax
69E0  26 8A 45 06     mov al, byte ptr es:[di + 6]
69E4  30 E4           xor ah, ah
69E6  8B F8           mov di, ax
69E8  8A 85 12 08     mov al, byte ptr [di + 0x812]
69EC  C4 7E 06        les di, ptr [bp + 6]
69EF  26 88 45 0C     mov byte ptr es:[di + 0xc], al
69F3  C4 7E 06        les di, ptr [bp + 6]
69F6  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
69FA  C4 7E 06        les di, ptr [bp + 6]
69FD  26 00 45 08     add byte ptr es:[di + 8], al
6A01  C4 7E 06        les di, ptr [bp + 6]
6A04  26 FF 75 07     push word ptr es:[di + 7]
6A08  C4 7E 06        les di, ptr [bp + 6]
6A0B  06              push es
6A0C  57              push di
6A0D  0E              push cs
6A0E  E8 75 C2        call 0x2c86
6A11  C4 7E 06        les di, ptr [bp + 6]
6A14  26 89 45 07     mov word ptr es:[di + 7], ax
6A18  E8 7B BF        call 0x2996
6A1B  98              cwde
6A1C  8B F8           mov di, ax
6A1E  8A 85 68 06     mov al, byte ptr [di + 0x668]
6A22  30 E4           xor ah, ah
6A24  05 0B 00        add ax, 0xb
6A27  8B D0           mov dx, ax
6A29  C4 7E 06        les di, ptr [bp + 6]
6A2C  26 8A 45 06     mov al, byte ptr es:[di + 6]
6A30  30 E4           xor ah, ah
6A32  3B C2           cmp ax, dx
6A34  75 14           jne 0x6a4a
6A36  FF 36 22 08     push word ptr [0x822]
6A3A  C4 7E 06        les di, ptr [bp + 6]
6A3D  06              push es
6A3E  57              push di
6A3F  0E              push cs
6A40  E8 43 C2        call 0x2c86
6A43  C4 7E 06        les di, ptr [bp + 6]
6A46  26 89 45 07     mov word ptr es:[di + 7], ax
loc_6A4A:
6A4A  A0 0B 83        mov al, byte ptr [0x830b]
6A4D  C4 7E 06        les di, ptr [bp + 6]
6A50  26 3A 45 06     cmp al, byte ptr es:[di + 6]
6A54  75 14           jne 0x6a6a
6A56  FF 36 20 08     push word ptr [0x820]
6A5A  C4 7E 06        les di, ptr [bp + 6]
6A5D  06              push es
6A5E  57              push di
6A5F  0E              push cs
6A60  E8 23 C2        call 0x2c86
6A63  C4 7E 06        les di, ptr [bp + 6]
6A66  26 89 45 07     mov word ptr es:[di + 7], ax
loc_6A6A:
6A6A  80 3E 26 83 00  cmp byte ptr [0x8326], 0
6A6F  75 36           jne 0x6aa7
6A71  C4 7E 06        les di, ptr [bp + 6]
6A74  06              push es
6A75  57              push di
6A76  0E              push cs
6A77  E8 4B C2        call 0x2cc5
6A7A  08 C0           or al, al
6A7C  74 29           je 0x6aa7
6A7E  A0 0B 83        mov al, byte ptr [0x830b]
6A81  C4 7E 06        les di, ptr [bp + 6]
6A84  26 3A 45 06     cmp al, byte ptr es:[di + 6]
6A88  75 15           jne 0x6a9f
6A8A  C4 7E 06        les di, ptr [bp + 6]
6A8D  26 C6 45 12 02  mov byte ptr es:[di + 0x12], 2
6A92  C6 06 02 83 00  mov byte ptr [0x8302], 0
6A97  B0 31           mov al, 0x31
6A99  50              push ax
6A9A  E8 06 C0        call 0x2aa3
6A9D  EB 08           jmp 0x6aa7
loc_6A9F:
6A9F  C4 7E 06        les di, ptr [bp + 6]
6AA2  26 C6 45 12 00  mov byte ptr es:[di + 0x12], 0
loc_6AA7:
6AA7  89 EC           mov sp, bp
6AA9  5D              pop bp
6AAA  CA 04 00        retf 4

; ---- routine 0791:6AAD  (found by: call)
sub_6AAD:
6AAD  55              push bp
6AAE  89 E5           mov bp, sp
6AB0  B0 00           mov al, 0
6AB2  50              push ax
6AB3  E8 FC BD        call 0x28b2
6AB6  08 C0           or al, al
6AB8  74 37           je 0x6af1
6ABA  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
6ABF  C6 06 0C 83 00  mov byte ptr [0x830c], 0
6AC4  C6 06 23 83 00  mov byte ptr [0x8323], 0
6AC9  FF 36 24 08     push word ptr [0x824]
6ACD  C4 7E 06        les di, ptr [bp + 6]
6AD0  06              push es
6AD1  57              push di
6AD2  0E              push cs
6AD3  E8 B0 C1        call 0x2c86
6AD6  50              push ax
6AD7  B8 06 00        mov ax, 6
6ADA  50              push ax
6ADB  C4 7E 06        les di, ptr [bp + 6]
6ADE  06              push es
6ADF  57              push di
6AE0  0E              push cs
6AE1  E8 DD C9        call 0x34c1
6AE4  B0 05           mov al, 5
6AE6  50              push ax
6AE7  E8 3F BE        call 0x2929
6AEA  B8 02 00        mov ax, 2
6AED  50              push ax
6AEE  E8 50 99        call 0x441
loc_6AF1:
6AF1  89 EC           mov sp, bp
6AF3  5D              pop bp
6AF4  CA 04 00        retf 4

; ---- routine 0791:6AF7  (found by: call)
sub_6AF7:
6AF7  55              push bp
6AF8  89 E5           mov bp, sp
6AFA  C4 7E 06        les di, ptr [bp + 6]
6AFD  26 8B 05        mov ax, word ptr es:[di]
6B00  3B 06 44 06     cmp ax, word ptr [0x644]
6B04  74 18           je 0x6b1e
6B06  C4 7E 06        les di, ptr [bp + 6]
6B09  26 8B 05        mov ax, word ptr es:[di]
6B0C  3B 06 40 06     cmp ax, word ptr [0x640]
6B10  74 0C           je 0x6b1e
6B12  A1 42 06        mov ax, word ptr [0x642]
6B15  C4 7E 06        les di, ptr [bp + 6]
6B18  26 89 45 07     mov word ptr es:[di + 7], ax
6B1C  EB 0D           jmp 0x6b2b
loc_6B1E:
6B1E  C4 7E 06        les di, ptr [bp + 6]
6B21  26 8B 05        mov ax, word ptr es:[di]
6B24  C4 7E 06        les di, ptr [bp + 6]
6B27  26 89 45 07     mov word ptr es:[di + 7], ax
loc_6B2B:
6B2B  C4 7E 06        les di, ptr [bp + 6]
6B2E  06              push es
6B2F  57              push di
6B30  0E              push cs
6B31  E8 91 C1        call 0x2cc5
6B34  08 C0           or al, al
6B36  74 27           je 0x6b5f
6B38  C4 7E 06        les di, ptr [bp + 6]
6B3B  26 C6 45 12 04  mov byte ptr es:[di + 0x12], 4
6B40  A1 44 06        mov ax, word ptr [0x644]
6B43  C4 7E 06        les di, ptr [bp + 6]
6B46  26 89 05        mov word ptr es:[di], ax
6B49  C4 7E 06        les di, ptr [bp + 6]
6B4C  26 8B 05        mov ax, word ptr es:[di]
6B4F  C4 7E 06        les di, ptr [bp + 6]
6B52  26 89 45 07     mov word ptr es:[di + 7], ax
6B56  C4 7E 06        les di, ptr [bp + 6]
6B59  06              push es
6B5A  57              push di
6B5B  0E              push cs
6B5C  E8 D8 19        call 0x8537
loc_6B5F:
6B5F  89 EC           mov sp, bp
6B61  5D              pop bp
6B62  CA 04 00        retf 4

; ---- routine 0791:6B65  (found by: call)
sub_6B65:
6B65  55              push bp
6B66  89 E5           mov bp, sp
6B68  83 EC 08        sub sp, 8
6B6B  8A 46 06        mov al, byte ptr [bp + 6]
6B6E  98              cwde
6B6F  8B F8           mov di, ax
6B71  D1 E7           shl di, 1
6B73  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
6B77  BA BF 00        mov dx, 0xbf
6B7A  F7 E2           mul dx
6B7C  C4 3E 17 A9     les di, ptr [0xa917]
6B80  03 F8           add di, ax
6B82  89 7E F8        mov word ptr [bp - 8], di
6B85  8C 46 FA        mov word ptr [bp - 6], es
6B88  C7 46 FC 01 00  mov word ptr [bp - 4], 1
loc_6B8D:
6B8D  83 7E FC 0C     cmp word ptr [bp - 4], 0xc
6B91  73 2F           jae 0x6bc2
6B93  8B 46 04        mov ax, word ptr [bp + 4]
6B96  D1 E0           shl ax, 1
6B98  8B C8           mov cx, ax
6B9A  8A 46 06        mov al, byte ptr [bp + 6]
6B9D  98              cwde
6B9E  BA 0A 00        mov dx, 0xa
6BA1  F7 E2           mul dx
6BA3  8B F8           mov di, ax
6BA5  03 F9           add di, cx
6BA7  8B 95 76 99     mov dx, word ptr [di - 0x668a]
6BAB  8B 46 FC        mov ax, word ptr [bp - 4]
6BAE  D1 E0           shl ax, 1
6BB0  C4 7E F8        les di, ptr [bp - 8]
6BB3  03 F8           add di, ax
6BB5  26 8B 45 FE     mov ax, word ptr es:[di - 2]
6BB9  3B C2           cmp ax, dx
6BBB  74 05           je 0x6bc2
6BBD  FF 46 FC        inc word ptr [bp - 4]
6BC0  EB CB           jmp 0x6b8d
loc_6BC2:
6BC2  8B 46 FC        mov ax, word ptr [bp - 4]
6BC5  89 46 FE        mov word ptr [bp - 2], ax
6BC8  8B 46 FE        mov ax, word ptr [bp - 2]
6BCB  89 EC           mov sp, bp
6BCD  5D              pop bp
6BCE  C2 04 00        ret 4
; data (not reached as code), 32 bytes
6BD1                  db 80 0F 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
6BE1                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:6BF1  (found by: call)
sub_6BF1:
6BF1  55              push bp
6BF2  89 E5           mov bp, sp
6BF4  83 EC 04        sub sp, 4
6BF7  8A 46 06        mov al, byte ptr [bp + 6]
6BFA  A2 0B 83        mov byte ptr [0x830b], al
6BFD  E8 15 BE        call 0x2a15
6C00  C6 06 0C 83 00  mov byte ptr [0x830c], 0
6C05  C6 06 0D 83 00  mov byte ptr [0x830d], 0
6C0A  C6 06 02 83 01  mov byte ptr [0x8302], 1
6C0F  31 C0           xor ax, ax
6C11  A3 00 83        mov word ptr [0x8300], ax
6C14  8A 46 04        mov al, byte ptr [bp + 4]
6C17  50              push ax
6C18  E8 0E BD        call 0x2929
6C1B  8A 46 04        mov al, byte ptr [bp + 4]
6C1E  50              push ax
6C1F  BF D1 6B        mov di, 0x6bd1
6C22  0E              push cs
6C23  57              push di
6C24  9A DF 08 E4 23  call far 23E4:08DF
6C29  74 05           je 0x6c30
6C2B  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
loc_6C30:
6C30  A0 0B 83        mov al, byte ptr [0x830b]
6C33  30 E4           xor ah, ah
6C35  BA 16 00        mov dx, 0x16
6C38  F7 E2           mul dx
6C3A  8B F8           mov di, ax
6C3C  81 C7 E8 80     add di, 0x80e8
6C40  89 7E FC        mov word ptr [bp - 4], di
6C43  8C 5E FE        mov word ptr [bp - 2], ds
6C46  8A 46 04        mov al, byte ptr [bp + 4]
6C49  3C 0A           cmp al, 0xa
6C4B  75 1A           jne 0x6c67
6C4D  C6 06 15 83 00  mov byte ptr [0x8315], 0
6C52  C4 7E FC        les di, ptr [bp - 4]
6C55  06              push es
6C56  57              push di
6C57  0E              push cs
6C58  E8 8A BF        call 0x2be5
6C5B  98              cwde
6C5C  B9 1C 00        mov cx, 0x1c
6C5F  F7 E9           imul cx
6C61  A2 16 83        mov byte ptr [0x8316], al
6C64  E9 B0 00        jmp 0x6d17
loc_6C67:
6C67  3C 09           cmp al, 9
6C69  75 3C           jne 0x6ca7
6C6B  80 3E F6 82 00  cmp byte ptr [0x82f6], 0
6C70  7F 04           jg 0x6c76
6C72  B0 00           mov al, 0
6C74  EB 02           jmp 0x6c78
loc_6C76:
6C76  B0 01           mov al, 1
loc_6C78:
6C78  98              cwde
6C79  8B F8           mov di, ax
6C7B  8A 85 20 79     mov al, byte ptr [di + 0x7920]
6C7F  98              cwde
6C80  B9 03 00        mov cx, 3
6C83  D3 E0           shl ax, cl
6C85  A2 15 83        mov byte ptr [0x8315], al
6C88  80 3E F7 82 00  cmp byte ptr [0x82f7], 0
6C8D  7F 04           jg 0x6c93
6C8F  B0 00           mov al, 0
6C91  EB 02           jmp 0x6c95
loc_6C93:
6C93  B0 01           mov al, 1
loc_6C95:
6C95  98              cwde
6C96  8B F8           mov di, ax
6C98  8A 85 20 79     mov al, byte ptr [di + 0x7920]
6C9C  98              cwde
6C9D  B9 24 00        mov cx, 0x24
6CA0  F7 E9           imul cx
6CA2  A2 16 83        mov byte ptr [0x8316], al
6CA5  EB 70           jmp 0x6d17
loc_6CA7:
6CA7  3C 0B           cmp al, 0xb
6CA9  75 08           jne 0x6cb3
6CAB  A1 F6 82        mov ax, word ptr [0x82f6]
6CAE  A3 15 83        mov word ptr [0x8315], ax
6CB1  EB 64           jmp 0x6d17
loc_6CB3:
6CB3  3C 08           cmp al, 8
6CB5  75 2E           jne 0x6ce5
6CB7  80 3E F6 82 00  cmp byte ptr [0x82f6], 0
6CBC  7F 04           jg 0x6cc2
6CBE  B0 00           mov al, 0
6CC0  EB 02           jmp 0x6cc4
loc_6CC2:
6CC2  B0 01           mov al, 1
loc_6CC4:
6CC4  98              cwde
6CC5  8B F8           mov di, ax
6CC7  8A 85 20 79     mov al, byte ptr [di + 0x7920]
6CCB  98              cwde
6CCC  D1 E0           shl ax, 1
6CCE  A2 15 83        mov byte ptr [0x8315], al
6CD1  C4 7E FC        les di, ptr [bp - 4]
6CD4  06              push es
6CD5  57              push di
6CD6  0E              push cs
6CD7  E8 0B BF        call 0x2be5
6CDA  98              cwde
6CDB  B9 DF FF        mov cx, 0xffdf
6CDE  F7 E9           imul cx
6CE0  A2 16 83        mov byte ptr [0x8316], al
6CE3  EB 32           jmp 0x6d17
loc_6CE5:
6CE5  3C 07           cmp al, 7
6CE7  75 25           jne 0x6d0e
6CE9  80 3E F6 82 00  cmp byte ptr [0x82f6], 0
6CEE  7F 04           jg 0x6cf4
6CF0  B0 00           mov al, 0
6CF2  EB 02           jmp 0x6cf6
loc_6CF4:
6CF4  B0 01           mov al, 1
loc_6CF6:
6CF6  98              cwde
6CF7  8B F8           mov di, ax
6CF9  8A 85 20 79     mov al, byte ptr [di + 0x7920]
6CFD  98              cwde
6CFE  B9 03 00        mov cx, 3
6D01  D3 E0           shl ax, cl
6D03  A2 15 83        mov byte ptr [0x8315], al
6D06  A0 F7 82        mov al, byte ptr [0x82f7]
6D09  A2 16 83        mov byte ptr [0x8316], al
6D0C  EB 09           jmp 0x6d17
loc_6D0E:
6D0E  C4 7E FC        les di, ptr [bp - 4]
6D11  26 8B 05        mov ax, word ptr es:[di]
6D14  A3 15 83        mov word ptr [0x8315], ax
loc_6D17:
6D17  A1 15 83        mov ax, word ptr [0x8315]
6D1A  C4 7E FC        les di, ptr [bp - 4]
6D1D  26 89 45 07     mov word ptr es:[di + 7], ax
6D21  A1 15 83        mov ax, word ptr [0x8315]
6D24  A3 F6 82        mov word ptr [0x82f6], ax
6D27  C4 7E FC        les di, ptr [bp - 4]
6D2A  06              push es
6D2B  57              push di
6D2C  0E              push cs
6D2D  E8 F8 C1        call 0x2f28
6D30  30 E4           xor ah, ah
6D32  B9 0A 00        mov cx, 0xa
6D35  F7 E9           imul cx
6D37  50              push ax
6D38  E8 DF B8        call 0x261a
6D3B  05 0A 00        add ax, 0xa
6D3E  5A              pop dx
6D3F  03 C2           add ax, dx
6D41  C4 7E FC        les di, ptr [bp - 4]
6D44  26 88 45 10     mov byte ptr es:[di + 0x10], al
6D48  89 EC           mov sp, bp
6D4A  5D              pop bp
6D4B  C2 04 00        ret 4

