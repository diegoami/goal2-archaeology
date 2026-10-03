; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 12 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:80DA  (found by: call)
sub_80DA:
80DA  55              push bp
80DB  89 E5           mov bp, sp
80DD  83 EC 0C        sub sp, 0xc
80E0  C4 3E 23 A9     les di, ptr [0xa923]
80E4  89 7E F8        mov word ptr [bp - 8], di
80E7  8C 46 FA        mov word ptr [bp - 6], es
80EA  C7 46 FE 01 00  mov word ptr [bp - 2], 1
80EF  EB 03           jmp 0x80f4
loc_80F1:
80F1  FF 46 FE        inc word ptr [bp - 2]
loc_80F4:
80F4  FF 76 FE        push word ptr [bp - 2]
80F7  E8 E5 FE        call 0x7fdf
80FA  81 7E FE 80 00  cmp word ptr [bp - 2], 0x80
80FF  75 F0           jne 0x80f1
8101  C4 7E F8        les di, ptr [bp - 8]
8104  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
8108  50              push ax
8109  BF BA 80        mov di, 0x80ba
810C  0E              push cs
810D  57              push di
810E  9A DF 08 E4 23  call far 23E4:08DF
8113  75 03           jne 0x8118
8115  E9 CC 00        jmp 0x81e4
loc_8118:
8118  C4 7E F8        les di, ptr [bp - 8]
811B  26 FF 45 38     inc word ptr es:[di + 0x38]
811F  C7 46 FE 01 00  mov word ptr [bp - 2], 1
8124  EB 03           jmp 0x8129
loc_8126:
8126  FF 46 FE        inc word ptr [bp - 2]
loc_8129:
8129  8B 46 FE        mov ax, word ptr [bp - 2]
812C  BA BF 00        mov dx, 0xbf
812F  F7 E2           mul dx
8131  C4 3E 17 A9     les di, ptr [0xa917]
8135  03 F8           add di, ax
8137  89 7E F4        mov word ptr [bp - 0xc], di
813A  8C 46 F6        mov word ptr [bp - 0xa], es
813D  FF 76 FE        push word ptr [bp - 2]
8140  0E              push cs
8141  E8 33 8A        call 0xb77
8144  08 C0           or al, al
8146  74 62           je 0x81aa
8148  C4 7E F4        les di, ptr [bp - 0xc]
814B  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
814F  30 E4           xor ah, ah
8151  2D 80 00        sub ax, 0x80
8154  8B D0           mov dx, ax
8156  C4 7E F8        les di, ptr [bp - 8]
8159  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
815D  98              cwde
815E  D1 E0           shl ax, 1
8160  8B F0           mov si, ax
8162  D1 E0           shl ax, 1
8164  03 C6           add ax, si
8166  C4 7E F8        les di, ptr [bp - 8]
8169  03 F8           add di, ax
816B  03 FA           add di, dx
816D  26 8A 45 19     mov al, byte ptr es:[di + 0x19]
8171  C4 7E F4        les di, ptr [bp - 0xc]
8174  26 3A 45 3B     cmp al, byte ptr es:[di + 0x3b]
8178  73 30           jae 0x81aa
817A  C4 7E F4        les di, ptr [bp - 0xc]
817D  26 8A 4D 3B     mov cl, byte ptr es:[di + 0x3b]
8181  C4 7E F4        les di, ptr [bp - 0xc]
8184  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
8188  30 E4           xor ah, ah
818A  2D 80 00        sub ax, 0x80
818D  8B D0           mov dx, ax
818F  C4 7E F8        les di, ptr [bp - 8]
8192  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
8196  98              cwde
8197  D1 E0           shl ax, 1
8199  8B F0           mov si, ax
819B  D1 E0           shl ax, 1
819D  03 C6           add ax, si
819F  C4 7E F8        les di, ptr [bp - 8]
81A2  03 F8           add di, ax
81A4  03 FA           add di, dx
81A6  26 88 4D 19     mov byte ptr es:[di + 0x19], cl
loc_81AA:
81AA  C4 7E F4        les di, ptr [bp - 0xc]
81AD  81 C7 3B 00     add di, 0x3b
81B1  06              push es
81B2  57              push di
81B3  C4 7E F4        les di, ptr [bp - 0xc]
81B6  81 C7 41 00     add di, 0x41
81BA  06              push es
81BB  57              push di
81BC  B8 36 00        mov ax, 0x36
81BF  50              push ax
81C0  9A 3C 00 4B 21  call far 214B:003C
81C5  C4 7E F4        les di, ptr [bp - 0xc]
81C8  81 C7 3B 00     add di, 0x3b
81CC  06              push es
81CD  57              push di
81CE  B8 06 00        mov ax, 6
81D1  50              push ax
81D2  31 C0           xor ax, ax
81D4  50              push ax
81D5  9A 18 00 4B 21  call far 214B:0018
81DA  81 7E FE 80 00  cmp word ptr [bp - 2], 0x80
81DF  74 03           je 0x81e4
81E1  E9 42 FF        jmp 0x8126
loc_81E4:
81E4  89 EC           mov sp, bp
81E6  5D              pop bp
81E7  C3              ret
; data (not reached as code), 32 bytes
81E8                  db AC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
81F8                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:8208  (found by: far)
sub_8208:
8208  55              push bp
8209  89 E5           mov bp, sp
820B  83 EC 04        sub sp, 4
820E  C4 3E 23 A9     les di, ptr [0xa923]
8212  89 7E FC        mov word ptr [bp - 4], di
8215  8C 46 FE        mov word ptr [bp - 2], es
8218  C4 7E FC        les di, ptr [bp - 4]
821B  26 FE 4D 3D     dec byte ptr es:[di + 0x3d]
821F  C4 7E FC        les di, ptr [bp - 4]
8222  26 80 7D 3D 00  cmp byte ptr es:[di + 0x3d], 0
8227  76 03           jbe 0x822c
8229  E9 8D 00        jmp 0x82b9
loc_822C:
822C  B0 00           mov al, 0
822E  08 C0           or al, al
8230  74 0C           je 0x823e
8232  C4 7E FC        les di, ptr [bp - 4]
8235  26 80 7D 3C 08  cmp byte ptr es:[di + 0x3c], 8
823A  75 02           jne 0x823e
823C  EB 7B           jmp 0x82b9
loc_823E:
823E  C4 7E FC        les di, ptr [bp - 4]
8241  81 C7 3C 00     add di, 0x3c
8245  06              push es
8246  57              push di
8247  B0 02           mov al, 2
8249  50              push ax
824A  B0 08           mov al, 8
824C  50              push ax
824D  B8 01 00        mov ax, 1
8250  50              push ax
8251  9A 6F 1D 4B 21  call far 214B:1D6F
8256  C4 7E FC        les di, ptr [bp - 4]
8259  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
825D  50              push ax
825E  BF E8 81        mov di, 0x81e8
8261  0E              push cs
8262  57              push di
8263  9A DF 08 E4 23  call far 23E4:08DF
8268  74 03           je 0x826d
826A  E8 6D FE        call 0x80da
loc_826D:
826D  C4 7E FC        les di, ptr [bp - 4]
8270  26 80 7D 3C 05  cmp byte ptr es:[di + 0x3c], 5
8275  73 04           jae 0x827b
8277  B0 00           mov al, 0
8279  EB 02           jmp 0x827d
loc_827B:
827B  B0 01           mov al, 1
loc_827D:
827D  C4 7E FC        les di, ptr [bp - 4]
8280  26 88 45 40     mov byte ptr es:[di + 0x40], al
8284  C4 7E FC        les di, ptr [bp - 4]
8287  26 80 7D 3C 08  cmp byte ptr es:[di + 0x3c], 8
828C  74 04           je 0x8292
828E  B0 00           mov al, 0
8290  EB 02           jmp 0x8294
loc_8292:
8292  B0 01           mov al, 1
loc_8294:
8294  30 E4           xor ah, ah
8296  B9 03 00        mov cx, 3
8299  F7 E9           imul cx
829B  8B D0           mov dx, ax
829D  C4 7E FC        les di, ptr [bp - 4]
82A0  26 80 7D 3C 04  cmp byte ptr es:[di + 0x3c], 4
82A5  74 04           je 0x82ab
82A7  B0 00           mov al, 0
82A9  EB 02           jmp 0x82ad
loc_82AB:
82AB  B0 01           mov al, 1
loc_82AD:
82AD  30 E4           xor ah, ah
82AF  40              inc ax
82B0  03 C2           add ax, dx
82B2  C4 7E FC        les di, ptr [bp - 4]
82B5  26 88 45 3D     mov byte ptr es:[di + 0x3d], al
loc_82B9:
82B9  89 EC           mov sp, bp
82BB  5D              pop bp
82BC  CB              retf

; ---- routine 1771:82BD  (found by: call)
sub_82BD:
82BD  55              push bp
82BE  89 E5           mov bp, sp
82C0  83 EC 1C        sub sp, 0x1c
82C3  C4 3E 23 A9     les di, ptr [0xa923]
82C7  89 7E F5        mov word ptr [bp - 0xb], di
82CA  8C 46 F7        mov word ptr [bp - 9], es
82CD  C4 7E 04        les di, ptr [bp + 4]
82D0  89 7E F1        mov word ptr [bp - 0xf], di
82D3  8C 46 F3        mov word ptr [bp - 0xd], es
82D6  C7 46 FE 01 00  mov word ptr [bp - 2], 1
82DB  EB 03           jmp 0x82e0
loc_82DD:
82DD  FF 46 FE        inc word ptr [bp - 2]
loc_82E0:
82E0  8B 46 FE        mov ax, word ptr [bp - 2]
82E3  B1 03           mov cl, 3
82E5  D3 E0           shl ax, cl
82E7  C4 7E F1        les di, ptr [bp - 0xf]
82EA  03 F8           add di, ax
82EC  81 C7 F8 FF     add di, 0xfff8
82F0  89 7E ED        mov word ptr [bp - 0x13], di
82F3  8C 46 EF        mov word ptr [bp - 0x11], es
82F6  C4 7E ED        les di, ptr [bp - 0x13]
82F9  26 8B 05        mov ax, word ptr es:[di]
82FC  BA BF 00        mov dx, 0xbf
82FF  F7 E2           mul dx
8301  C4 3E 17 A9     les di, ptr [0xa917]
8305  03 F8           add di, ax
8307  89 7E E9        mov word ptr [bp - 0x17], di
830A  8C 46 EB        mov word ptr [bp - 0x15], es
830D  C4 7E ED        les di, ptr [bp - 0x13]
8310  81 C7 02 00     add di, 2
8314  06              push es
8315  57              push di
8316  B8 06 00        mov ax, 6
8319  50              push ax
831A  31 C0           xor ax, ax
831C  50              push ax
831D  9A 18 00 4B 21  call far 214B:0018
8322  C7 46 FC 19 00  mov word ptr [bp - 4], 0x19
8327  EB 03           jmp 0x832c
loc_8329:
8329  FF 46 FC        inc word ptr [bp - 4]
loc_832C:
832C  8B 46 FC        mov ax, word ptr [bp - 4]
832F  D1 E0           shl ax, 1
8331  8B C8           mov cx, ax
8333  C4 7E ED        les di, ptr [bp - 0x13]
8336  26 8B 05        mov ax, word ptr es:[di]
8339  BA 48 00        mov dx, 0x48
833C  F7 E2           mul dx
833E  C4 3E 2F A9     les di, ptr [0xa92f]
8342  03 F8           add di, ax
8344  03 F9           add di, cx
8346  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
834B  77 03           ja 0x8350
834D  E9 14 01        jmp 0x8464
loc_8350:
8350  8B 46 FC        mov ax, word ptr [bp - 4]
8353  D1 E0           shl ax, 1
8355  8B C8           mov cx, ax
8357  C4 7E ED        les di, ptr [bp - 0x13]
835A  26 8B 05        mov ax, word ptr es:[di]
835D  BA 48 00        mov dx, 0x48
8360  F7 E2           mul dx
8362  C4 3E 2F A9     les di, ptr [0xa92f]
8366  03 F8           add di, ax
8368  03 F9           add di, cx
836A  26 8B 45 FE     mov ax, word ptr es:[di - 2]
836E  B1 03           mov cl, 3
8370  D3 E0           shl ax, cl
8372  C4 3E 2B A9     les di, ptr [0xa92b]
8376  03 F8           add di, ax
8378  81 C7 F8 FF     add di, 0xfff8
837C  89 7E E5        mov word ptr [bp - 0x1b], di
837F  8C 46 E7        mov word ptr [bp - 0x19], es
8382  C4 7E E5        les di, ptr [bp - 0x1b]
8385  26 8A 45 02     mov al, byte ptr es:[di + 2]
8389  C4 7E F5        les di, ptr [bp - 0xb]
838C  26 3A 45 3C     cmp al, byte ptr es:[di + 0x3c]
8390  74 03           je 0x8395
8392  E9 CF 00        jmp 0x8464
loc_8395:
8395  C4 7E E5        les di, ptr [bp - 0x1b]
8398  26 80 3D FE     cmp byte ptr es:[di], 0xfe
839C  72 03           jb 0x83a1
839E  E9 C3 00        jmp 0x8464
loc_83A1:
83A1  C4 7E E5        les di, ptr [bp - 0x1b]
83A4  26 8B 45 06     mov ax, word ptr es:[di + 6]
83A8  C4 7E ED        les di, ptr [bp - 0x13]
83AB  26 3B 05        cmp ax, word ptr es:[di]
83AE  74 04           je 0x83b4
83B0  B0 00           mov al, 0
83B2  EB 02           jmp 0x83b6
loc_83B4:
83B4  B0 01           mov al, 1
loc_83B6:
83B6  88 46 F9        mov byte ptr [bp - 7], al
83B9  C4 7E E5        les di, ptr [bp - 0x1b]
83BC  26 8A 45 01     mov al, byte ptr es:[di + 1]
83C0  C4 7E E5        les di, ptr [bp - 0x1b]
83C3  26 3A 05        cmp al, byte ptr es:[di]
83C6  74 04           je 0x83cc
83C8  B0 00           mov al, 0
83CA  EB 02           jmp 0x83ce
loc_83CC:
83CC  B0 01           mov al, 1
loc_83CE:
83CE  30 E4           xor ah, ah
83D0  8B C8           mov cx, ax
83D2  80 7E F9 00     cmp byte ptr [bp - 7], 0
83D6  74 04           je 0x83dc
83D8  B0 00           mov al, 0
83DA  EB 02           jmp 0x83de
loc_83DC:
83DC  B0 01           mov al, 1
loc_83DE:
83DE  98              cwde
83DF  C4 7E E5        les di, ptr [bp - 0x1b]
83E2  03 F8           add di, ax
83E4  26 8A 15        mov dl, byte ptr es:[di]
83E7  8A 46 F9        mov al, byte ptr [bp - 7]
83EA  98              cwde
83EB  C4 7E E5        les di, ptr [bp - 0x1b]
83EE  03 F8           add di, ax
83F0  26 8A 05        mov al, byte ptr es:[di]
83F3  3A C2           cmp al, dl
83F5  77 04           ja 0x83fb
83F7  B0 00           mov al, 0
83F9  EB 02           jmp 0x83fd
loc_83FB:
83FB  B0 01           mov al, 1
loc_83FD:
83FD  30 E4           xor ah, ah
83FF  D1 E0           shl ax, 1
8401  03 C1           add ax, cx
8403  89 46 FA        mov word ptr [bp - 6], ax
8406  83 7E FA 02     cmp word ptr [bp - 6], 2
840A  75 09           jne 0x8415
840C  C4 7E ED        les di, ptr [bp - 0x13]
840F  26 FE 45 02     inc byte ptr es:[di + 2]
8413  EB 16           jmp 0x842b
loc_8415:
8415  83 7E FA 01     cmp word ptr [bp - 6], 1
8419  75 09           jne 0x8424
841B  C4 7E ED        les di, ptr [bp - 0x13]
841E  26 FE 45 03     inc byte ptr es:[di + 3]
8422  EB 07           jmp 0x842b
loc_8424:
8424  C4 7E ED        les di, ptr [bp - 0x13]
8427  26 FE 45 04     inc byte ptr es:[di + 4]
loc_842B:
842B  8A 46 F9        mov al, byte ptr [bp - 7]
842E  98              cwde
842F  C4 7E E5        les di, ptr [bp - 0x1b]
8432  03 F8           add di, ax
8434  26 8A 05        mov al, byte ptr es:[di]
8437  C4 7E ED        les di, ptr [bp - 0x13]
843A  26 00 45 05     add byte ptr es:[di + 5], al
843E  80 7E F9 00     cmp byte ptr [bp - 7], 0
8442  74 04           je 0x8448
8444  B0 00           mov al, 0
8446  EB 02           jmp 0x844a
loc_8448:
8448  B0 01           mov al, 1
loc_844A:
844A  98              cwde
844B  C4 7E E5        les di, ptr [bp - 0x1b]
844E  03 F8           add di, ax
8450  26 8A 05        mov al, byte ptr es:[di]
8453  C4 7E ED        les di, ptr [bp - 0x13]
8456  26 00 45 06     add byte ptr es:[di + 6], al
845A  8A 46 FA        mov al, byte ptr [bp - 6]
845D  C4 7E ED        les di, ptr [bp - 0x13]
8460  26 00 45 07     add byte ptr es:[di + 7], al
loc_8464:
8464  83 7E FC 24     cmp word ptr [bp - 4], 0x24
8468  74 03           je 0x846d
846A  E9 BC FE        jmp 0x8329
loc_846D:
846D  83 7E FE 04     cmp word ptr [bp - 2], 4
8471  74 03           je 0x8476
8473  E9 67 FE        jmp 0x82dd
loc_8476:
8476  C7 46 FC 01 00  mov word ptr [bp - 4], 1
847B  EB 03           jmp 0x8480
loc_847D:
847D  FF 46 FC        inc word ptr [bp - 4]
loc_8480:
8480  8B 46 FC        mov ax, word ptr [bp - 4]
8483  40              inc ax
8484  3D 04 00        cmp ax, 4
8487  76 03           jbe 0x848c
8489  E9 5C 01        jmp 0x85e8
loc_848C:
848C  89 46 FE        mov word ptr [bp - 2], ax
848F  EB 03           jmp 0x8494
loc_8491:
8491  FF 46 FE        inc word ptr [bp - 2]
loc_8494:
8494  8B 46 FC        mov ax, word ptr [bp - 4]
8497  B1 03           mov cl, 3
8499  D3 E0           shl ax, cl
849B  C4 7E F1        les di, ptr [bp - 0xf]
849E  03 F8           add di, ax
84A0  26 8A 55 FF     mov dl, byte ptr es:[di - 1]
84A4  8B 46 FE        mov ax, word ptr [bp - 2]
84A7  B1 03           mov cl, 3
84A9  D3 E0           shl ax, cl
84AB  C4 7E F1        les di, ptr [bp - 0xf]
84AE  03 F8           add di, ax
84B0  26 8A 45 FF     mov al, byte ptr es:[di - 1]
84B4  3A C2           cmp al, dl
84B6  76 03           jbe 0x84bb
84B8  E9 F7 00        jmp 0x85b2
loc_84BB:
84BB  8B 46 FC        mov ax, word ptr [bp - 4]
84BE  B1 03           mov cl, 3
84C0  D3 E0           shl ax, cl
84C2  C4 7E F1        les di, ptr [bp - 0xf]
84C5  03 F8           add di, ax
84C7  26 8A 55 FF     mov dl, byte ptr es:[di - 1]
84CB  8B 46 FE        mov ax, word ptr [bp - 2]
84CE  B1 03           mov cl, 3
84D0  D3 E0           shl ax, cl
84D2  C4 7E F1        les di, ptr [bp - 0xf]
84D5  03 F8           add di, ax
84D7  26 8A 45 FF     mov al, byte ptr es:[di - 1]
84DB  3A C2           cmp al, dl
84DD  74 03           je 0x84e2
84DF  E9 FD 00        jmp 0x85df
loc_84E2:
84E2  8B 46 FC        mov ax, word ptr [bp - 4]
84E5  B1 03           mov cl, 3
84E7  D3 E0           shl ax, cl
84E9  C4 7E F1        les di, ptr [bp - 0xf]
84EC  03 F8           add di, ax
84EE  26 8A 45 FE     mov al, byte ptr es:[di - 2]
84F2  30 E4           xor ah, ah
84F4  8B D0           mov dx, ax
84F6  8B 46 FC        mov ax, word ptr [bp - 4]
84F9  B1 03           mov cl, 3
84FB  D3 E0           shl ax, cl
84FD  C4 7E F1        les di, ptr [bp - 0xf]
8500  03 F8           add di, ax
8502  26 8A 45 FD     mov al, byte ptr es:[di - 3]
8506  30 E4           xor ah, ah
8508  2B C2           sub ax, dx
850A  8B D8           mov bx, ax
850C  8B 46 FE        mov ax, word ptr [bp - 2]
850F  B1 03           mov cl, 3
8511  D3 E0           shl ax, cl
8513  C4 7E F1        les di, ptr [bp - 0xf]
8516  03 F8           add di, ax
8518  26 8A 45 FE     mov al, byte ptr es:[di - 2]
851C  30 E4           xor ah, ah
851E  8B D0           mov dx, ax
8520  8B 46 FE        mov ax, word ptr [bp - 2]
8523  B1 03           mov cl, 3
8525  D3 E0           shl ax, cl
8527  C4 7E F1        les di, ptr [bp - 0xf]
852A  03 F8           add di, ax
852C  26 8A 45 FD     mov al, byte ptr es:[di - 3]
8530  30 E4           xor ah, ah
8532  2B C2           sub ax, dx
8534  3B C3           cmp ax, bx
8536  7F 7A           jg 0x85b2
8538  8B 46 FC        mov ax, word ptr [bp - 4]
853B  B1 03           mov cl, 3
853D  D3 E0           shl ax, cl
853F  C4 7E F1        les di, ptr [bp - 0xf]
8542  03 F8           add di, ax
8544  26 8A 45 FE     mov al, byte ptr es:[di - 2]
8548  30 E4           xor ah, ah
854A  8B D0           mov dx, ax
854C  8B 46 FC        mov ax, word ptr [bp - 4]
854F  B1 03           mov cl, 3
8551  D3 E0           shl ax, cl
8553  C4 7E F1        les di, ptr [bp - 0xf]
8556  03 F8           add di, ax
8558  26 8A 45 FD     mov al, byte ptr es:[di - 3]
855C  30 E4           xor ah, ah
855E  2B C2           sub ax, dx
8560  8B D8           mov bx, ax
8562  8B 46 FE        mov ax, word ptr [bp - 2]
8565  B1 03           mov cl, 3
8567  D3 E0           shl ax, cl
8569  C4 7E F1        les di, ptr [bp - 0xf]
856C  03 F8           add di, ax
856E  26 8A 45 FE     mov al, byte ptr es:[di - 2]
8572  30 E4           xor ah, ah
8574  8B D0           mov dx, ax
8576  8B 46 FE        mov ax, word ptr [bp - 2]
8579  B1 03           mov cl, 3
857B  D3 E0           shl ax, cl
857D  C4 7E F1        les di, ptr [bp - 0xf]
8580  03 F8           add di, ax
8582  26 8A 45 FD     mov al, byte ptr es:[di - 3]
8586  30 E4           xor ah, ah
8588  2B C2           sub ax, dx
858A  3B C3           cmp ax, bx
858C  75 51           jne 0x85df
858E  8B 46 FC        mov ax, word ptr [bp - 4]
8591  B1 03           mov cl, 3
8593  D3 E0           shl ax, cl
8595  C4 7E F1        les di, ptr [bp - 0xf]
8598  03 F8           add di, ax
859A  26 8A 55 FD     mov dl, byte ptr es:[di - 3]
859E  8B 46 FE        mov ax, word ptr [bp - 2]
85A1  B1 03           mov cl, 3
85A3  D3 E0           shl ax, cl
85A5  C4 7E F1        les di, ptr [bp - 0xf]
85A8  03 F8           add di, ax
85AA  26 8A 45 FD     mov al, byte ptr es:[di - 3]
85AE  3A C2           cmp al, dl
85B0  76 2D           jbe 0x85df
loc_85B2:
85B2  8B 46 FE        mov ax, word ptr [bp - 2]
85B5  B1 03           mov cl, 3
85B7  D3 E0           shl ax, cl
85B9  C4 7E F1        les di, ptr [bp - 0xf]
85BC  03 F8           add di, ax
85BE  81 C7 F8 FF     add di, 0xfff8
85C2  06              push es
85C3  57              push di
85C4  8B 46 FC        mov ax, word ptr [bp - 4]
85C7  B1 03           mov cl, 3
85C9  D3 E0           shl ax, cl
85CB  C4 7E F1        les di, ptr [bp - 0xf]
85CE  03 F8           add di, ax
85D0  81 C7 F8 FF     add di, 0xfff8
85D4  06              push es
85D5  57              push di
85D6  B8 08 00        mov ax, 8
85D9  50              push ax
85DA  9A 7B 00 4B 21  call far 214B:007B
loc_85DF:
85DF  83 7E FE 04     cmp word ptr [bp - 2], 4
85E3  74 03           je 0x85e8
85E5  E9 A9 FE        jmp 0x8491
loc_85E8:
85E8  83 7E FC 03     cmp word ptr [bp - 4], 3
85EC  74 03           je 0x85f1
85EE  E9 8C FE        jmp 0x847d
loc_85F1:
85F1  89 EC           mov sp, bp
85F3  5D              pop bp
85F4  C2 04 00        ret 4

; ---- routine 1771:85F7  (found by: call)
sub_85F7:
85F7  55              push bp
85F8  89 E5           mov bp, sp
85FA  83 EC 0E        sub sp, 0xe
85FD  C4 3E 23 A9     les di, ptr [0xa923]
8601  89 7E F6        mov word ptr [bp - 0xa], di
8604  8C 46 F8        mov word ptr [bp - 8], es
8607  31 C0           xor ax, ax
8609  89 46 FE        mov word ptr [bp - 2], ax
loc_860C:
860C  C4 7E F6        les di, ptr [bp - 0xa]
860F  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
8613  03 46 FE        add ax, word ptr [bp - 2]
8616  40              inc ax
8617  C4 7E F6        les di, ptr [bp - 0xa]
861A  26 3B 45 26     cmp ax, word ptr es:[di + 0x26]
861E  76 03           jbe 0x8623
8620  E9 10 01        jmp 0x8733
loc_8623:
8623  C4 7E F6        les di, ptr [bp - 0xa]
8626  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
862A  03 46 FE        add ax, word ptr [bp - 2]
862D  40              inc ax
862E  B1 03           mov cl, 3
8630  D3 E0           shl ax, cl
8632  C4 3E 2B A9     les di, ptr [0xa92b]
8636  03 F8           add di, ax
8638  26 80 7D F8 FE  cmp byte ptr es:[di - 8], 0xfe
863D  72 03           jb 0x8642
863F  E9 F1 00        jmp 0x8733
loc_8642:
8642  8B 46 FE        mov ax, word ptr [bp - 2]
8645  31 D2           xor dx, dx
8647  B9 02 00        mov cx, 2
864A  F7 F1           div cx
864C  05 61 09        add ax, 0x961
864F  B1 03           mov cl, 3
8651  D3 E0           shl ax, cl
8653  C4 3E 2B A9     les di, ptr [0xa92b]
8657  03 F8           add di, ax
8659  81 C7 F8 FF     add di, 0xfff8
865D  89 7E F2        mov word ptr [bp - 0xe], di
8660  8C 46 F4        mov word ptr [bp - 0xc], es
8663  C4 7E F6        les di, ptr [bp - 0xa]
8666  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
866A  03 46 FE        add ax, word ptr [bp - 2]
866D  40              inc ax
866E  B1 03           mov cl, 3
8670  D3 E0           shl ax, cl
8672  C4 3E 2B A9     les di, ptr [0xa92b]
8676  03 F8           add di, ax
8678  26 8A 45 F8     mov al, byte ptr es:[di - 8]
867C  30 E4           xor ah, ah
867E  89 46 FC        mov word ptr [bp - 4], ax
8681  C4 7E F6        les di, ptr [bp - 0xa]
8684  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
8688  03 46 FE        add ax, word ptr [bp - 2]
868B  B1 03           mov cl, 3
868D  D3 E0           shl ax, cl
868F  C4 3E 2B A9     les di, ptr [0xa92b]
8693  03 F8           add di, ax
8695  26 8A 45 F9     mov al, byte ptr es:[di - 7]
8699  30 E4           xor ah, ah
869B  03 46 FC        add ax, word ptr [bp - 4]
869E  C4 7E F2        les di, ptr [bp - 0xe]
86A1  26 88 45 01     mov byte ptr es:[di + 1], al
86A5  C4 7E F6        les di, ptr [bp - 0xa]
86A8  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
86AC  03 46 FE        add ax, word ptr [bp - 2]
86AF  B1 03           mov cl, 3
86B1  D3 E0           shl ax, cl
86B3  C4 3E 2B A9     les di, ptr [0xa92b]
86B7  03 F8           add di, ax
86B9  26 8A 45 F8     mov al, byte ptr es:[di - 8]
86BD  30 E4           xor ah, ah
86BF  89 46 FA        mov word ptr [bp - 6], ax
86C2  C4 7E F6        les di, ptr [bp - 0xa]
86C5  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
86C9  03 46 FE        add ax, word ptr [bp - 2]
86CC  40              inc ax
86CD  B1 03           mov cl, 3
86CF  D3 E0           shl ax, cl
86D1  C4 3E 2B A9     les di, ptr [0xa92b]
86D5  03 F8           add di, ax
86D7  26 8A 45 F9     mov al, byte ptr es:[di - 7]
86DB  30 E4           xor ah, ah
86DD  03 46 FA        add ax, word ptr [bp - 6]
86E0  C4 7E F2        les di, ptr [bp - 0xe]
86E3  26 88 05        mov byte ptr es:[di], al
86E6  C4 7E F2        les di, ptr [bp - 0xe]
86E9  26 8A 45 01     mov al, byte ptr es:[di + 1]
86ED  C4 7E F2        les di, ptr [bp - 0xe]
86F0  26 3A 05        cmp al, byte ptr es:[di]
86F3  77 2E           ja 0x8723
86F5  C4 7E F2        les di, ptr [bp - 0xe]
86F8  26 8A 45 01     mov al, byte ptr es:[di + 1]
86FC  C4 7E F2        les di, ptr [bp - 0xe]
86FF  26 3A 05        cmp al, byte ptr es:[di]
8702  75 1B           jne 0x871f
8704  8B 46 FC        mov ax, word ptr [bp - 4]
8707  3B 46 FA        cmp ax, word ptr [bp - 6]
870A  73 17           jae 0x8723
870C  8B 46 FC        mov ax, word ptr [bp - 4]
870F  3B 46 FA        cmp ax, word ptr [bp - 6]
8712  75 0B           jne 0x871f
8714  C4 7E F2        les di, ptr [bp - 0xe]
8717  26 8A 45 06     mov al, byte ptr es:[di + 6]
871B  D0 E8           shr al, 1
871D  72 04           jb 0x8723
loc_871F:
871F  B0 00           mov al, 0
8721  EB 02           jmp 0x8725
loc_8723:
8723  B0 01           mov al, 1
loc_8725:
8725  C4 7E F2        les di, ptr [bp - 0xe]
8728  26 88 45 03     mov byte ptr es:[di + 3], al
872C  83 46 FE 02     add word ptr [bp - 2], 2
8730  E9 D9 FE        jmp 0x860c
loc_8733:
8733  89 EC           mov sp, bp
8735  5D              pop bp
8736  C3              ret
; data (not reached as code), 32 bytes
8737                  db AC 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
8747                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:8757  (found by: far)
sub_8757:
8757  55              push bp
8758  89 E5           mov bp, sp
875A  83 EC 0C        sub sp, 0xc
875D  C4 3E 23 A9     les di, ptr [0xa923]
8761  89 7E F8        mov word ptr [bp - 8], di
8764  8C 46 FA        mov word ptr [bp - 6], es
8767  C4 7E F8        les di, ptr [bp - 8]
876A  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
876E  50              push ax
876F  BF 37 87        mov di, 0x8737
8772  0E              push cs
8773  57              push di
8774  9A DF 08 E4 23  call far 23E4:08DF
8779  75 03           jne 0x877e
877B  E9 B0 00        jmp 0x882e
loc_877E:
877E  C4 7E F8        les di, ptr [bp - 8]
8781  26 80 7D 3C 07  cmp byte ptr es:[di + 0x3c], 7
8786  74 04           je 0x878c
8788  B0 00           mov al, 0
878A  EB 02           jmp 0x878e
loc_878C:
878C  B0 01           mov al, 1
loc_878E:
878E  98              cwde
878F  8B F8           mov di, ax
8791  8A 85 10 11     mov al, byte ptr [di + 0x1110]
8795  30 E4           xor ah, ah
8797  89 46 F6        mov word ptr [bp - 0xa], ax
879A  B8 01 00        mov ax, 1
879D  3B 46 F6        cmp ax, word ptr [bp - 0xa]
87A0  76 03           jbe 0x87a5
87A2  E9 89 00        jmp 0x882e
loc_87A5:
87A5  89 46 FE        mov word ptr [bp - 2], ax
87A8  EB 03           jmp 0x87ad
loc_87AA:
87AA  FF 46 FE        inc word ptr [bp - 2]
loc_87AD:
87AD  C4 7E F8        les di, ptr [bp - 8]
87B0  26 80 7D 3C 03  cmp byte ptr es:[di + 0x3c], 3
87B5  74 04           je 0x87bb
87B7  B0 00           mov al, 0
87B9  EB 02           jmp 0x87bd
loc_87BB:
87BB  B0 01           mov al, 1
loc_87BD:
87BD  98              cwde
87BE  8B F8           mov di, ax
87C0  8A 85 12 11     mov al, byte ptr [di + 0x1112]
87C4  30 E4           xor ah, ah
87C6  89 46 F4        mov word ptr [bp - 0xc], ax
87C9  B8 01 00        mov ax, 1
87CC  3B 46 F4        cmp ax, word ptr [bp - 0xc]
87CF  77 52           ja 0x8823
87D1  89 46 FC        mov word ptr [bp - 4], ax
87D4  EB 03           jmp 0x87d9
loc_87D6:
87D6  FF 46 FC        inc word ptr [bp - 4]
loc_87D9:
87D9  8B 46 FC        mov ax, word ptr [bp - 4]
87DC  BA 38 00        mov dx, 0x38
87DF  F7 E2           mul dx
87E1  50              push ax
87E2  8B 46 FE        mov ax, word ptr [bp - 2]
87E5  BA C0 01        mov dx, 0x1c0
87E8  F7 E2           mul dx
87EA  50              push ax
87EB  0E              push cs
87EC  E8 E9 D1        call 0x59d8
87EF  98              cwde
87F0  BA 00 07        mov dx, 0x700
87F3  F7 E2           mul dx
87F5  8B C8           mov cx, ax
87F7  C4 7E F8        les di, ptr [bp - 8]
87FA  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
87FE  98              cwde
87FF  BA 00 0E        mov dx, 0xe00
8802  F7 E2           mul dx
8804  C4 3E 33 A9     les di, ptr [0xa933]
8808  03 F8           add di, ax
880A  03 F9           add di, cx
880C  58              pop ax
880D  03 F8           add di, ax
880F  58              pop ax
8810  03 F8           add di, ax
8812  81 C7 08 FE     add di, 0xfe08
8816  06              push es
8817  57              push di
8818  E8 A2 FA        call 0x82bd
881B  8B 46 FC        mov ax, word ptr [bp - 4]
881E  3B 46 F4        cmp ax, word ptr [bp - 0xc]
8821  75 B3           jne 0x87d6
loc_8823:
8823  8B 46 FE        mov ax, word ptr [bp - 2]
8826  3B 46 F6        cmp ax, word ptr [bp - 0xa]
8829  74 03           je 0x882e
882B  E9 7C FF        jmp 0x87aa
loc_882E:
882E  C4 7E F8        les di, ptr [bp - 8]
8831  26 80 7D 3C 06  cmp byte ptr es:[di + 0x3c], 6
8836  75 03           jne 0x883b
8838  E8 BC FD        call 0x85f7
loc_883B:
883B  89 EC           mov sp, bp
883D  5D              pop bp
883E  CB              retf

; ---- routine 1771:883F  (found by: call)
sub_883F:
883F  55              push bp
8840  89 E5           mov bp, sp
8842  81 EC 08 01     sub sp, 0x108
8846  BF 66 17        mov di, 0x1766
8849  1E              push ds
884A  57              push di
884B  BF 6E A9        mov di, 0xa96e
884E  1E              push ds
884F  57              push di
8850  9A 29 03 4B 21  call far 214B:0329
8855  8B 7E 04        mov di, word ptr [bp + 4]
8858  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
885D  74 07           je 0x8866
885F  C7 46 FC 05 00  mov word ptr [bp - 4], 5
8864  EB 1B           jmp 0x8881
loc_8866:
8866  8B 7E 04        mov di, word ptr [bp + 4]
8869  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
886D  BA BF 00        mov dx, 0xbf
8870  F7 E2           mul dx
8872  C4 3E 17 A9     les di, ptr [0xa917]
8876  03 F8           add di, ax
8878  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
887C  30 E4           xor ah, ah
887E  89 46 FC        mov word ptr [bp - 4], ax
loc_8881:
8881  C6 06 B2 AA 07  mov byte ptr [0xaab2], 7
8886  C7 46 FE 01 00  mov word ptr [bp - 2], 1
888B  EB 03           jmp 0x8890
loc_888D:
888D  FF 46 FE        inc word ptr [bp - 2]
loc_8890:
8890  8B 46 FE        mov ax, word ptr [bp - 2]
8893  B1 04           mov cl, 4
8895  D3 E0           shl ax, cl
8897  8B D8           mov bx, ax
8899  8B 46 FC        mov ax, word ptr [bp - 4]
889C  BA 60 00        mov dx, 0x60
889F  F7 E2           mul dx
88A1  C4 3E 3F A9     les di, ptr [0xa93f]
88A5  03 F8           add di, ax
88A7  03 FB           add di, bx
88A9  81 C7 90 FF     add di, 0xff90
88AD  89 7E F8        mov word ptr [bp - 8], di
88B0  8C 46 FA        mov word ptr [bp - 6], es
88B3  C4 7E F8        les di, ptr [bp - 8]
88B6  26 83 7D 0E 00  cmp word ptr es:[di + 0xe], 0
88BB  74 6D           je 0x892a
88BD  8D BE F8 FE     lea di, [bp - 0x108]
88C1  16              push ss
88C2  57              push di
88C3  C4 7E F8        les di, ptr [bp - 8]
88C6  26 8A 05        mov al, byte ptr es:[di]
88C9  50              push ax
88CA  9A 5A 07 E4 23  call far 23E4:075A
88CF  8B 46 FE        mov ax, word ptr [bp - 2]
88D2  05 02 00        add ax, 2
88D5  50              push ax
88D6  B0 3E           mov al, 0x3e
88D8  50              push ax
88D9  BF 6E A9        mov di, 0xa96e
88DC  1E              push ds
88DD  57              push di
88DE  9A 6D 02 4B 21  call far 214B:026D
88E3  C4 7E F8        les di, ptr [bp - 8]
88E6  81 C7 01 00     add di, 1
88EA  06              push es
88EB  57              push di
88EC  8B 46 FE        mov ax, word ptr [bp - 2]
88EF  05 02 00        add ax, 2
88F2  50              push ax
88F3  B0 40           mov al, 0x40
88F5  50              push ax
88F6  BF 6E A9        mov di, 0xa96e
88F9  1E              push ds
88FA  57              push di
88FB  9A 6D 02 4B 21  call far 214B:026D
8900  8D BE F8 FE     lea di, [bp - 0x108]
8904  16              push ss
8905  57              push di
8906  C4 7E F8        les di, ptr [bp - 8]
8909  26 8B 45 0C     mov ax, word ptr es:[di + 0xc]
890D  31 D2           xor dx, dx
890F  52              push dx
8910  50              push ax
8911  9A DA 09 4B 21  call far 214B:09DA
8916  8B 46 FE        mov ax, word ptr [bp - 2]
8919  05 02 00        add ax, 2
891C  50              push ax
891D  B0 4D           mov al, 0x4d
891F  50              push ax
8920  BF 6E A9        mov di, 0xa96e
8923  1E              push ds
8924  57              push di
8925  9A A3 01 4B 21  call far 214B:01A3
loc_892A:
892A  83 7E FE 03     cmp word ptr [bp - 2], 3
892E  74 03           je 0x8933
8930  E9 5A FF        jmp 0x888d
loc_8933:
8933  89 EC           mov sp, bp
8935  5D              pop bp
8936  C2 02 00        ret 2

; ---- routine 1771:8939  (found by: call)
sub_8939:
8939  55              push bp
893A  89 E5           mov bp, sp
893C  83 EC 04        sub sp, 4
893F  C4 3E 23 A9     les di, ptr [0xa923]
8943  89 7E FC        mov word ptr [bp - 4], di
8946  8C 46 FE        mov word ptr [bp - 2], es
8949  9A DB 05 4B 21  call far 214B:05DB
894E  BF F2 26        mov di, 0x26f2
8951  1E              push ds
8952  57              push di
8953  BF 6E A9        mov di, 0xa96e
8956  1E              push ds
8957  57              push di
8958  9A 29 03 4B 21  call far 214B:0329
895D  8B 7E 04        mov di, word ptr [bp + 4]
8960  36 80 7D 0A 00  cmp byte ptr ss:[di + 0xa], 0
8965  75 11           jne 0x8978
8967  BF A6 14        mov di, 0x14a6
896A  1E              push ds
896B  57              push di
896C  BF 6E A9        mov di, 0xa96e
896F  1E              push ds
8970  57              push di
8971  9A 29 03 4B 21  call far 214B:0329
8976  EB 43           jmp 0x89bb
loc_8978:
8978  BF 36 2E        mov di, 0x2e36
897B  1E              push ds
897C  57              push di
897D  BF 6E A9        mov di, 0xa96e
8980  1E              push ds
8981  57              push di
8982  9A 29 03 4B 21  call far 214B:0329
8987  C4 7E FC        les di, ptr [bp - 4]
898A  26 83 7D 38 00  cmp word ptr es:[di + 0x38], 0
898F  76 2A           jbe 0x89bb
8991  8B 7E 04        mov di, word ptr [bp + 4]
8994  36 80 7D F7 00  cmp byte ptr ss:[di - 9], 0
8999  74 11           je 0x89ac
899B  BF 0C 2E        mov di, 0x2e0c
899E  1E              push ds
899F  57              push di
89A0  BF 6E A9        mov di, 0xa96e
89A3  1E              push ds
89A4  57              push di
89A5  9A 29 03 4B 21  call far 214B:0329
89AA  EB 0F           jmp 0x89bb
loc_89AC:
89AC  BF E4 2D        mov di, 0x2de4
89AF  1E              push ds
89B0  57              push di
89B1  BF 6E A9        mov di, 0xa96e
89B4  1E              push ds
89B5  57              push di
89B6  9A 29 03 4B 21  call far 214B:0329
loc_89BB:
89BB  89 EC           mov sp, bp
89BD  5D              pop bp
89BE  C2 02 00        ret 2

; ---- routine 1771:89C1  (found by: call)
sub_89C1:
89C1  55              push bp
89C2  89 E5           mov bp, sp
89C4  BF 7A 2D        mov di, 0x2d7a
89C7  1E              push ds
89C8  57              push di
89C9  BF 6E A9        mov di, 0xa96e
89CC  1E              push ds
89CD  57              push di
89CE  9A 29 03 4B 21  call far 214B:0329
89D3  B8 17 00        mov ax, 0x17
89D6  50              push ax
89D7  8B 7E 04        mov di, word ptr [bp + 4]
89DA  36 8B 7D FE     mov di, word ptr ss:[di - 2]
89DE  8A 85 13 11     mov al, byte ptr [di + 0x1113]
89E2  30 E4           xor ah, ah
89E4  50              push ax
89E5  8B 7E 04        mov di, word ptr [bp + 4]
89E8  36 8B 7D FE     mov di, word ptr ss:[di - 2]
89EC  8A 85 16 11     mov al, byte ptr [di + 0x1116]
89F0  30 E4           xor ah, ah
89F2  50              push ax
89F3  9A C5 13 4B 21  call far 214B:13C5
89F8  89 EC           mov sp, bp
89FA  5D              pop bp
89FB  C2 02 00        ret 2

; ---- routine 1771:89FE  (found by: call)
sub_89FE:
89FE  55              push bp
89FF  89 E5           mov bp, sp
8A01  83 EC 04        sub sp, 4
8A04  8B 7E 04        mov di, word ptr [bp + 4]
8A07  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
8A0B  BA BF 00        mov dx, 0xbf
8A0E  F7 E2           mul dx
8A10  C4 3E 17 A9     les di, ptr [0xa917]
8A14  03 F8           add di, ax
8A16  89 7E FC        mov word ptr [bp - 4], di
8A19  8C 46 FE        mov word ptr [bp - 2], es
8A1C  C4 7E FC        les di, ptr [bp - 4]
8A1F  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8A23  30 E4           xor ah, ah
8A25  8B F8           mov di, ax
8A27  8A 85 1D 11     mov al, byte ptr [di + 0x111d]
8A2B  30 E4           xor ah, ah
8A2D  50              push ax
8A2E  C4 7E FC        les di, ptr [bp - 4]
8A31  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8A35  30 E4           xor ah, ah
8A37  8B F8           mov di, ax
8A39  8A 85 19 11     mov al, byte ptr [di + 0x1119]
8A3D  30 E4           xor ah, ah
8A3F  50              push ax
8A40  C4 7E FC        les di, ptr [bp - 4]
8A43  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8A47  30 E4           xor ah, ah
8A49  8B F8           mov di, ax
8A4B  8A 85 21 11     mov al, byte ptr [di + 0x1121]
8A4F  30 E4           xor ah, ah
8A51  50              push ax
8A52  9A C5 13 4B 21  call far 214B:13C5
8A57  89 EC           mov sp, bp
8A59  5D              pop bp
8A5A  C2 02 00        ret 2

; ---- routine 1771:8A5D  (found by: call)
sub_8A5D:
8A5D  55              push bp
8A5E  89 E5           mov bp, sp
8A60  BF 68 2C        mov di, 0x2c68
8A63  1E              push ds
8A64  57              push di
8A65  BF 6E A9        mov di, 0xa96e
8A68  1E              push ds
8A69  57              push di
8A6A  9A 29 03 4B 21  call far 214B:0329
8A6F  FF 76 04        push word ptr [bp + 4]
8A72  E8 4C FF        call 0x89c1
8A75  80 7E 06 00     cmp byte ptr [bp + 6], 0
8A79  74 06           je 0x8a81
8A7B  FF 76 04        push word ptr [bp + 4]
8A7E  E8 7D FF        call 0x89fe
loc_8A81:
8A81  89 EC           mov sp, bp
8A83  5D              pop bp
8A84  C2 04 00        ret 4

; ---- routine 1771:8A87  (found by: call)
sub_8A87:
8A87  55              push bp
8A88  89 E5           mov bp, sp
8A8A  81 EC 0A 01     sub sp, 0x10a
8A8E  8B 7E 04        mov di, word ptr [bp + 4]
8A91  36 8B 45 F8     mov ax, word ptr ss:[di - 8]
8A95  BA BF 00        mov dx, 0xbf
8A98  F7 E2           mul dx
8A9A  C4 3E 17 A9     les di, ptr [0xa917]
8A9E  03 F8           add di, ax
8AA0  89 7E FA        mov word ptr [bp - 6], di
8AA3  8C 46 FC        mov word ptr [bp - 4], es
8AA6  B0 07           mov al, 7
8AA8  50              push ax
8AA9  8D BE FA FE     lea di, [bp - 0x106]
8AAD  16              push ss
8AAE  57              push di
8AAF  8B 7E 04        mov di, word ptr [bp + 4]
8AB2  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
8AB6  05 40 00        add ax, 0x40
8AB9  50              push ax
8ABA  9A 5A 07 E4 23  call far 23E4:075A
8ABF  B0 09           mov al, 9
8AC1  50              push ax
8AC2  B0 0B           mov al, 0xb
8AC4  50              push ax
8AC5  BF 6E A9        mov di, 0xa96e
8AC8  1E              push ds
8AC9  57              push di
8ACA  9A C8 02 4B 21  call far 214B:02C8
8ACF  C7 46 FE 01 00  mov word ptr [bp - 2], 1
8AD4  EB 03           jmp 0x8ad9
loc_8AD6:
8AD6  FF 46 FE        inc word ptr [bp - 2]
loc_8AD9:
8AD9  8B 46 FE        mov ax, word ptr [bp - 2]
8ADC  B1 03           mov cl, 3
8ADE  D3 E0           shl ax, cl
8AE0  50              push ax
8AE1  8B 7E 04        mov di, word ptr [bp + 4]
8AE4  36 8B 45 FC     mov ax, word ptr ss:[di - 4]
8AE8  BA 38 00        mov dx, 0x38
8AEB  F7 E2           mul dx
8AED  50              push ax
8AEE  C4 7E FA        les di, ptr [bp - 6]
8AF1  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
8AF5  30 E4           xor ah, ah
8AF7  BA C0 01        mov dx, 0x1c0
8AFA  F7 E2           mul dx
8AFC  8B D8           mov bx, ax
8AFE  8A 46 06        mov al, byte ptr [bp + 6]
8B01  98              cwde
8B02  BA 00 07        mov dx, 0x700
8B05  F7 E2           mul dx
8B07  8B C8           mov cx, ax
8B09  8B 7E 04        mov di, word ptr [bp + 4]
8B0C  36 8A 45 F7     mov al, byte ptr ss:[di - 9]
8B10  98              cwde
8B11  BA 00 0E        mov dx, 0xe00
8B14  F7 E2           mul dx
8B16  C4 3E 33 A9     les di, ptr [0xa933]
8B1A  03 F8           add di, ax
8B1C  03 F9           add di, cx
8B1E  03 FB           add di, bx
8B20  58              pop ax
8B21  03 F8           add di, ax
8B23  58              pop ax
8B24  03 F8           add di, ax
8B26  81 C7 00 FE     add di, 0xfe00
8B2A  89 7E F6        mov word ptr [bp - 0xa], di
8B2D  8C 46 F8        mov word ptr [bp - 8], es
8B30  C4 7E F6        les di, ptr [bp - 0xa]
8B33  26 FF 35        push word ptr es:[di]
8B36  8B 46 FE        mov ax, word ptr [bp - 2]
8B39  05 0A 00        add ax, 0xa
8B3C  50              push ax
8B3D  B8 04 00        mov ax, 4
8B40  50              push ax
8B41  0E              push cs
8B42  E8 13 84        call 0xf58
8B45  8D BE F6 FE     lea di, [bp - 0x10a]
8B49  16              push ss
8B4A  57              push di
8B4B  C4 7E F6        les di, ptr [bp - 0xa]
8B4E  26 8A 45 04     mov al, byte ptr es:[di + 4]
8B52  30 E4           xor ah, ah
8B54  8B C8           mov cx, ax
8B56  C4 7E F6        les di, ptr [bp - 0xa]
8B59  26 8A 45 03     mov al, byte ptr es:[di + 3]
8B5D  30 E4           xor ah, ah
8B5F  8B D0           mov dx, ax
8B61  C4 7E F6        les di, ptr [bp - 0xa]
8B64  26 8A 45 02     mov al, byte ptr es:[di + 2]
8B68  30 E4           xor ah, ah
8B6A  03 C2           add ax, dx
8B6C  03 C1           add ax, cx
8B6E  05 30 00        add ax, 0x30
8B71  50              push ax
8B72  9A 5A 07 E4 23  call far 23E4:075A
8B77  8B 46 FE        mov ax, word ptr [bp - 2]
8B7A  05 0A 00        add ax, 0xa
8B7D  50              push ax
8B7E  B0 14           mov al, 0x14
8B80  50              push ax
8B81  BF 6E A9        mov di, 0xa96e
8B84  1E              push ds
8B85  57              push di
8B86  9A 6D 02 4B 21  call far 214B:026D
8B8B  8D BE F6 FE     lea di, [bp - 0x10a]
8B8F  16              push ss
8B90  57              push di
8B91  C4 7E F6        les di, ptr [bp - 0xa]
8B94  26 8A 45 02     mov al, byte ptr es:[di + 2]
8B98  30 E4           xor ah, ah
8B9A  05 30 00        add ax, 0x30
8B9D  50              push ax
8B9E  9A 5A 07 E4 23  call far 23E4:075A
8BA3  8B 46 FE        mov ax, word ptr [bp - 2]
8BA6  05 0A 00        add ax, 0xa
8BA9  50              push ax
8BAA  B0 16           mov al, 0x16
8BAC  50              push ax
8BAD  BF 6E A9        mov di, 0xa96e
8BB0  1E              push ds
8BB1  57              push di
8BB2  9A 6D 02 4B 21  call far 214B:026D
8BB7  8D BE F6 FE     lea di, [bp - 0x10a]
8BBB  16              push ss
8BBC  57              push di
8BBD  C4 7E F6        les di, ptr [bp - 0xa]
8BC0  26 8A 45 03     mov al, byte ptr es:[di + 3]
8BC4  30 E4           xor ah, ah
8BC6  05 30 00        add ax, 0x30
8BC9  50              push ax
8BCA  9A 5A 07 E4 23  call far 23E4:075A
8BCF  8B 46 FE        mov ax, word ptr [bp - 2]
8BD2  05 0A 00        add ax, 0xa
8BD5  50              push ax
8BD6  B0 18           mov al, 0x18
8BD8  50              push ax
8BD9  BF 6E A9        mov di, 0xa96e
8BDC  1E              push ds
8BDD  57              push di
8BDE  9A 6D 02 4B 21  call far 214B:026D
8BE3  8D BE F6 FE     lea di, [bp - 0x10a]
8BE7  16              push ss
8BE8  57              push di
8BE9  C4 7E F6        les di, ptr [bp - 0xa]
8BEC  26 8A 45 04     mov al, byte ptr es:[di + 4]
8BF0  30 E4           xor ah, ah
8BF2  05 30 00        add ax, 0x30
8BF5  50              push ax
8BF6  9A 5A 07 E4 23  call far 23E4:075A
8BFB  8B 46 FE        mov ax, word ptr [bp - 2]
8BFE  05 0A 00        add ax, 0xa
8C01  50              push ax
8C02  B0 1A           mov al, 0x1a
8C04  50              push ax
8C05  BF 6E A9        mov di, 0xa96e
8C08  1E              push ds
8C09  57              push di
8C0A  9A 6D 02 4B 21  call far 214B:026D
8C0F  8D BE F6 FE     lea di, [bp - 0x10a]
8C13  16              push ss
8C14  57              push di
8C15  C4 7E F6        les di, ptr [bp - 0xa]
8C18  26 8A 45 05     mov al, byte ptr es:[di + 5]
8C1C  30 E4           xor ah, ah
8C1E  31 D2           xor dx, dx
8C20  52              push dx
8C21  50              push ax
8C22  9A DA 09 4B 21  call far 214B:09DA
8C27  8B 46 FE        mov ax, word ptr [bp - 2]
8C2A  05 0A 00        add ax, 0xa
8C2D  50              push ax
8C2E  B0 1D           mov al, 0x1d
8C30  50              push ax
8C31  BF 6E A9        mov di, 0xa96e
8C34  1E              push ds
8C35  57              push di
8C36  9A A3 01 4B 21  call far 214B:01A3
8C3B  8D BE F6 FE     lea di, [bp - 0x10a]
8C3F  16              push ss
8C40  57              push di
8C41  C4 7E F6        les di, ptr [bp - 0xa]
8C44  26 8A 45 06     mov al, byte ptr es:[di + 6]
8C48  30 E4           xor ah, ah
8C4A  31 D2           xor dx, dx
8C4C  52              push dx
8C4D  50              push ax
8C4E  9A DA 09 4B 21  call far 214B:09DA
8C53  8B 46 FE        mov ax, word ptr [bp - 2]
8C56  05 0A 00        add ax, 0xa
8C59  50              push ax
8C5A  B0 20           mov al, 0x20
8C5C  50              push ax
8C5D  BF 6E A9        mov di, 0xa96e
8C60  1E              push ds
8C61  57              push di
8C62  9A A3 01 4B 21  call far 214B:01A3
8C67  8D BE F6 FE     lea di, [bp - 0x10a]
8C6B  16              push ss
8C6C  57              push di
8C6D  C4 7E F6        les di, ptr [bp - 0xa]
8C70  26 8A 45 07     mov al, byte ptr es:[di + 7]
8C74  30 E4           xor ah, ah
8C76  31 D2           xor dx, dx
8C78  52              push dx
8C79  50              push ax
8C7A  9A DA 09 4B 21  call far 214B:09DA
8C7F  8B 46 FE        mov ax, word ptr [bp - 2]
8C82  05 0A 00        add ax, 0xa
8C85  50              push ax
8C86  B0 23           mov al, 0x23
8C88  50              push ax
8C89  BF 6E A9        mov di, 0xa96e
8C8C  1E              push ds
8C8D  57              push di
8C8E  9A A3 01 4B 21  call far 214B:01A3
8C93  83 7E FE 04     cmp word ptr [bp - 2], 4
8C97  74 03           je 0x8c9c
8C99  E9 3A FE        jmp 0x8ad6
loc_8C9C:
8C9C  89 EC           mov sp, bp
8C9E  5D              pop bp
8C9F  C2 04 00        ret 4

