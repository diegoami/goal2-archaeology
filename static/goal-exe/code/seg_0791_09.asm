; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 9 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:500C  (found by: call)
sub_500C:
500C  55              push bp
500D  89 E5           mov bp, sp
500F  83 EC 02        sub sp, 2
5012  E8 81 D9        call 0x2996
5015  08 C0           or al, al
5017  74 04           je 0x501d
5019  B0 00           mov al, 0
501B  EB 02           jmp 0x501f
loc_501D:
501D  B0 01           mov al, 1
loc_501F:
501F  98              cwde
5020  8B F8           mov di, ax
5022  8A 85 68 06     mov al, byte ptr [di + 0x668]
5026  30 E4           xor ah, ah
5028  40              inc ax
5029  BA 16 00        mov dx, 0x16
502C  F7 E2           mul dx
502E  8B F8           mov di, ax
5030  80 BD FA 80 0D  cmp byte ptr [di - 0x7f06], 0xd
5035  74 04           je 0x503b
5037  B0 00           mov al, 0
5039  EB 02           jmp 0x503d
loc_503B:
503B  B0 01           mov al, 1
loc_503D:
503D  88 46 FF        mov byte ptr [bp - 1], al
5040  8A 46 FF        mov al, byte ptr [bp - 1]
5043  89 EC           mov sp, bp
5045  5D              pop bp
5046  C2 02 00        ret 2

; ---- routine 0791:5049  (found by: call)
sub_5049:
5049  55              push bp
504A  89 E5           mov bp, sp
504C  83 EC 04        sub sp, 4
504F  8B 7E 04        mov di, word ptr [bp + 4]
5052  36 C4 7D 06     les di, ptr ss:[di + 6]
5056  06              push es
5057  57              push di
5058  0E              push cs
5059  E8 CD DB        call 0x2c29
505C  08 C0           or al, al
505E  75 03           jne 0x5063
5060  E9 CB 02        jmp 0x532e
loc_5063:
5063  C6 46 FF 01     mov byte ptr [bp - 1], 1
5067  8B 7E 04        mov di, word ptr [bp + 4]
506A  36 C4 7D 06     les di, ptr ss:[di + 6]
506E  06              push es
506F  57              push di
5070  0E              push cs
5071  E8 D9 F6        call 0x474d
5074  8B 7E 04        mov di, word ptr [bp + 4]
5077  36 C4 7D 06     les di, ptr ss:[di + 6]
507B  26 8A 45 06     mov al, byte ptr es:[di + 6]
507F  30 E4           xor ah, ah
5081  50              push ax
5082  E8 D8 B3        call 0x45d
5085  08 C0           or al, al
5087  74 75           je 0x50fe
5089  8B 7E 04        mov di, word ptr [bp + 4]
508C  36 C4 7D 06     les di, ptr ss:[di + 6]
5090  26 8A 45 01     mov al, byte ptr es:[di + 1]
5094  98              cwde
5095  09 C0           or ax, ax
5097  79 02           jns 0x509b
5099  F7 D8           neg ax
loc_509B:
509B  3D 1A 00        cmp ax, 0x1a
509E  75 0F           jne 0x50af
50A0  8B 7E 04        mov di, word ptr [bp + 4]
50A3  36 C4 7D 06     les di, ptr ss:[di + 6]
50A7  06              push es
50A8  57              push di
50A9  0E              push cs
50AA  E8 41 EB        call 0x3bee
50AD  EB 4C           jmp 0x50fb
loc_50AF:
50AF  8B 7E 04        mov di, word ptr [bp + 4]
50B2  36 C4 7D 06     les di, ptr ss:[di + 6]
50B6  26 8A 45 08     mov al, byte ptr es:[di + 8]
50BA  98              cwde
50BB  09 C0           or ax, ax
50BD  79 02           jns 0x50c1
50BF  F7 D8           neg ax
loc_50C1:
50C1  3D 1A 00        cmp ax, 0x1a
50C4  74 35           je 0x50fb
50C6  8B 7E 04        mov di, word ptr [bp + 4]
50C9  36 C4 7D 06     les di, ptr ss:[di + 6]
50CD  06              push es
50CE  57              push di
50CF  0E              push cs
50D0  E8 12 DB        call 0x2be5
50D3  98              cwde
50D4  B9 E6 FF        mov cx, 0xffe6
50D7  F7 E9           imul cx
50D9  8B 7E 04        mov di, word ptr [bp + 4]
50DC  36 C4 7D 06     les di, ptr ss:[di + 6]
50E0  26 88 45 08     mov byte ptr es:[di + 8], al
50E4  B8 09 00        mov ax, 9
50E7  50              push ax
50E8  9A B1 06 4B 21  call far 214B:06B1
50ED  05 FB FF        add ax, 0xfffb
50F0  8B 7E 04        mov di, word ptr [bp + 4]
50F3  36 C4 7D 06     les di, ptr ss:[di + 6]
50F7  26 88 45 07     mov byte ptr es:[di + 7], al
loc_50FB:
50FB  E9 2E 02        jmp 0x532c
loc_50FE:
50FE  8B 7E 04        mov di, word ptr [bp + 4]
5101  36 C4 7D 06     les di, ptr ss:[di + 6]
5105  06              push es
5106  57              push di
5107  0E              push cs
5108  E8 49 F2        call 0x4354
510B  E8 AE EF        call 0x40bc
510E  08 C0           or al, al
5110  75 03           jne 0x5115
5112  E9 99 00        jmp 0x51ae
loc_5115:
5115  FF 36 46 06     push word ptr [0x646]
5119  8B 7E 04        mov di, word ptr [bp + 4]
511C  36 C4 7D 06     les di, ptr ss:[di + 6]
5120  06              push es
5121  57              push di
5122  0E              push cs
5123  E8 60 DB        call 0x2c86
5126  8B 7E 04        mov di, word ptr [bp + 4]
5129  36 C4 7D 06     les di, ptr ss:[di + 6]
512D  26 89 45 07     mov word ptr es:[di + 7], ax
5131  55              push bp
5132  E8 D7 FE        call 0x500c
5135  08 C0           or al, al
5137  75 40           jne 0x5179
5139  8B 7E 04        mov di, word ptr [bp + 4]
513C  36 C4 7D 06     les di, ptr ss:[di + 6]
5140  26 8A 05        mov al, byte ptr es:[di]
5143  98              cwde
5144  09 C0           or ax, ax
5146  79 02           jns 0x514a
5148  F7 D8           neg ax
loc_514A:
514A  3D 02 00        cmp ax, 2
514D  7D 50           jge 0x519f
514F  E8 C8 D4        call 0x261a
5152  05 14 00        add ax, 0x14
5155  50              push ax
5156  8B 7E 04        mov di, word ptr [bp + 4]
5159  36 C4 7D 06     les di, ptr ss:[di + 6]
515D  06              push es
515E  57              push di
515F  0E              push cs
5160  E8 82 DA        call 0x2be5
5163  98              cwde
5164  8B D0           mov dx, ax
5166  8B 7E 04        mov di, word ptr [bp + 4]
5169  36 C4 7D 06     les di, ptr ss:[di + 6]
516D  26 8A 45 01     mov al, byte ptr es:[di + 1]
5171  98              cwde
5172  F7 EA           imul dx
5174  5A              pop dx
5175  3B C2           cmp ax, dx
5177  7E 26           jle 0x519f
loc_5179:
5179  80 3E 03 83 00  cmp byte ptr [0x8303], 0
517E  74 0F           je 0x518f
5180  8B 7E 04        mov di, word ptr [bp + 4]
5183  36 C4 7D 06     les di, ptr ss:[di + 6]
5187  06              push es
5188  57              push di
5189  0E              push cs
518A  E8 52 ED        call 0x3edf
518D  EB 10           jmp 0x519f
loc_518F:
518F  B0 11           mov al, 0x11
5191  50              push ax
5192  8B 7E 04        mov di, word ptr [bp + 4]
5195  36 C4 7D 06     les di, ptr ss:[di + 6]
5199  06              push es
519A  57              push di
519B  0E              push cs
519C  E8 26 ED        call 0x3ec5
loc_519F:
519F  80 3E 03 83 00  cmp byte ptr [0x8303], 0
51A4  74 05           je 0x51ab
51A6  C6 06 03 83 00  mov byte ptr [0x8303], 0
loc_51AB:
51AB  E9 7E 01        jmp 0x532c
loc_51AE:
51AE  8B 7E 04        mov di, word ptr [bp + 4]
51B1  36 C4 7D 06     les di, ptr ss:[di + 6]
51B5  06              push es
51B6  57              push di
51B7  0E              push cs
51B8  E8 6D DD        call 0x2f28
51BB  08 C0           or al, al
51BD  75 03           jne 0x51c2
51BF  E9 D0 00        jmp 0x5292
loc_51C2:
51C2  80 3E 03 83 00  cmp byte ptr [0x8303], 0
51C7  75 39           jne 0x5202
51C9  55              push bp
51CA  E8 3F FE        call 0x500c
51CD  08 C0           or al, al
51CF  75 31           jne 0x5202
51D1  8B 7E 04        mov di, word ptr [bp + 4]
51D4  36 C4 7D 06     les di, ptr ss:[di + 6]
51D8  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
51DC  BA 14 00        mov dx, 0x14
51DF  F7 E2           mul dx
51E1  C4 3E 1B A9     les di, ptr [0xa91b]
51E5  03 F8           add di, ax
51E7  26 8A 45 06     mov al, byte ptr es:[di + 6]
51EB  30 E4           xor ah, ah
51ED  8B F8           mov di, ax
51EF  8A 85 E5 07     mov al, byte ptr [di + 0x7e5]
51F3  30 E4           xor ah, ah
51F5  50              push ax
51F6  9A D0 06 4B 21  call far 214B:06D0
51FB  08 C0           or al, al
51FD  75 03           jne 0x5202
51FF  E9 90 00        jmp 0x5292
loc_5202:
5202  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5207  74 6A           je 0x5273
5209  8B 7E 04        mov di, word ptr [bp + 4]
520C  36 C4 7D 06     les di, ptr ss:[di + 6]
5210  26 FF 35        push word ptr es:[di]
5213  8B 7E 04        mov di, word ptr [bp + 4]
5216  36 C4 7D 06     les di, ptr ss:[di + 6]
521A  06              push es
521B  57              push di
521C  0E              push cs
521D  E8 D0 DC        call 0x2ef0
5220  08 C0           or al, al
5222  74 0F           je 0x5233
5224  8B 7E 04        mov di, word ptr [bp + 4]
5227  36 C4 7D 06     les di, ptr ss:[di + 6]
522B  06              push es
522C  57              push di
522D  0E              push cs
522E  E8 AE EC        call 0x3edf
5231  EB 3E           jmp 0x5271
loc_5233:
5233  8B 7E 04        mov di, word ptr [bp + 4]
5236  36 C4 7D 06     les di, ptr ss:[di + 6]
523A  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
523E  BA 14 00        mov dx, 0x14
5241  F7 E2           mul dx
5243  C4 3E 1B A9     les di, ptr [0xa91b]
5247  03 F8           add di, ax
5249  26 8A 45 06     mov al, byte ptr es:[di + 6]
524D  30 E4           xor ah, ah
524F  8B F8           mov di, ax
5251  8A 85 E5 07     mov al, byte ptr [di + 0x7e5]
5255  30 E4           xor ah, ah
5257  50              push ax
5258  9A D0 06 4B 21  call far 214B:06D0
525D  08 C0           or al, al
525F  74 10           je 0x5271
5261  B0 12           mov al, 0x12
5263  50              push ax
5264  8B 7E 04        mov di, word ptr [bp + 4]
5267  36 C4 7D 06     les di, ptr ss:[di + 6]
526B  06              push es
526C  57              push di
526D  0E              push cs
526E  E8 54 EC        call 0x3ec5
loc_5271:
5271  EB 10           jmp 0x5283
loc_5273:
5273  B0 11           mov al, 0x11
5275  50              push ax
5276  8B 7E 04        mov di, word ptr [bp + 4]
5279  36 C4 7D 06     les di, ptr ss:[di + 6]
527D  06              push es
527E  57              push di
527F  0E              push cs
5280  E8 42 EC        call 0x3ec5
loc_5283:
5283  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5288  74 05           je 0x528f
528A  C6 06 03 83 00  mov byte ptr [0x8303], 0
loc_528F:
528F  E9 9A 00        jmp 0x532c
loc_5292:
5292  8B 7E 04        mov di, word ptr [bp + 4]
5295  36 C4 7D 06     les di, ptr ss:[di + 6]
5299  06              push es
529A  57              push di
529B  0E              push cs
529C  E8 46 D9        call 0x2be5
529F  98              cwde
52A0  8B D0           mov dx, ax
52A2  8B 7E 04        mov di, word ptr [bp + 4]
52A5  36 C4 7D 06     les di, ptr ss:[di + 6]
52A9  26 8A 45 01     mov al, byte ptr es:[di + 1]
52AD  98              cwde
52AE  F7 EA           imul dx
52B0  3D EC FF        cmp ax, 0xffec
52B3  7D 28           jge 0x52dd
52B5  B8 04 00        mov ax, 4
52B8  50              push ax
52B9  9A D0 06 4B 21  call far 214B:06D0
52BE  08 C0           or al, al
52C0  74 13           je 0x52d5
52C2  B8 09 00        mov ax, 9
52C5  50              push ax
52C6  8B 7E 04        mov di, word ptr [bp + 4]
52C9  36 C4 7D 06     les di, ptr ss:[di + 6]
52CD  06              push es
52CE  57              push di
52CF  0E              push cs
52D0  E8 25 EC        call 0x3ef8
52D3  EB 06           jmp 0x52db
loc_52D5:
52D5  FF 76 04        push word ptr [bp + 4]
52D8  E8 4D FB        call 0x4e28
loc_52DB:
52DB  EB 4F           jmp 0x532c
loc_52DD:
52DD  B8 02 00        mov ax, 2
52E0  50              push ax
52E1  8B 7E 04        mov di, word ptr [bp + 4]
52E4  36 C4 7D 06     les di, ptr ss:[di + 6]
52E8  06              push es
52E9  57              push di
52EA  0E              push cs
52EB  E8 E9 D3        call 0x26d7
52EE  08 C0           or al, al
52F0  74 09           je 0x52fb
52F2  9A FA 06 4B 21  call far 214B:06FA
52F7  08 C0           or al, al
52F9  75 2B           jne 0x5326
loc_52FB:
52FB  8B 7E 04        mov di, word ptr [bp + 4]
52FE  36 C4 7D 06     les di, ptr ss:[di + 6]
5302  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
5306  BA 14 00        mov dx, 0x14
5309  F7 E2           mul dx
530B  C4 3E 1B A9     les di, ptr [0xa91b]
530F  03 F8           add di, ax
5311  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
5315  98              cwde
5316  99              cdq
5317  B9 02 00        mov cx, 2
531A  F7 F9           idiv cx
531C  50              push ax
531D  9A D0 06 4B 21  call far 214B:06D0
5322  08 C0           or al, al
5324  74 06           je 0x532c
loc_5326:
5326  FF 76 04        push word ptr [bp + 4]
5329  E8 FC FA        call 0x4e28
loc_532C:
532C  EB 04           jmp 0x5332
loc_532E:
532E  C6 46 FF 00     mov byte ptr [bp - 1], 0
loc_5332:
5332  8A 46 FF        mov al, byte ptr [bp - 1]
5335  89 EC           mov sp, bp
5337  5D              pop bp
5338  C2 02 00        ret 2

; ---- routine 0791:533B  (found by: call)
sub_533B:
533B  55              push bp
533C  89 E5           mov bp, sp
533E  83 EC 02        sub sp, 2
5341  8B 7E 04        mov di, word ptr [bp + 4]
5344  36 C4 7D 06     les di, ptr ss:[di + 6]
5348  26 8A 45 06     mov al, byte ptr es:[di + 6]
534C  3A 06 0C 83     cmp al, byte ptr [0x830c]
5350  75 40           jne 0x5392
5352  C6 46 FF 01     mov byte ptr [bp - 1], 1
5356  8B 7E 04        mov di, word ptr [bp + 4]
5359  36 C4 7D 06     les di, ptr ss:[di + 6]
535D  26 8A 45 06     mov al, byte ptr es:[di + 6]
5361  30 E4           xor ah, ah
5363  50              push ax
5364  E8 F6 B0        call 0x45d
5367  08 C0           or al, al
5369  75 07           jne 0x5372
536B  83 3E 00 83 0A  cmp word ptr [0x8300], 0xa
5370  73 10           jae 0x5382
loc_5372:
5372  A1 F6 82        mov ax, word ptr [0x82f6]
5375  8B 7E 04        mov di, word ptr [bp + 4]
5378  36 C4 7D 06     les di, ptr ss:[di + 6]
537C  26 89 45 07     mov word ptr es:[di + 7], ax
5380  EB 0E           jmp 0x5390
loc_5382:
5382  A1 13 83        mov ax, word ptr [0x8313]
5385  8B 7E 04        mov di, word ptr [bp + 4]
5388  36 C4 7D 06     les di, ptr ss:[di + 6]
538C  26 89 45 07     mov word ptr es:[di + 7], ax
loc_5390:
5390  EB 04           jmp 0x5396
loc_5392:
5392  C6 46 FF 00     mov byte ptr [bp - 1], 0
loc_5396:
5396  8A 46 FF        mov al, byte ptr [bp - 1]
5399  89 EC           mov sp, bp
539B  5D              pop bp
539C  C2 02 00        ret 2

; ---- routine 0791:539F  (found by: call)
sub_539F:
539F  55              push bp
53A0  89 E5           mov bp, sp
53A2  A0 0B 83        mov al, byte ptr [0x830b]
53A5  30 E4           xor ah, ah
53A7  50              push ax
53A8  E8 B2 B0        call 0x45d
53AB  08 C0           or al, al
53AD  74 03           je 0x53b2
53AF  E9 BC 00        jmp 0x546e
loc_53B2:
53B2  A0 0B 83        mov al, byte ptr [0x830b]
53B5  30 E4           xor ah, ah
53B7  BA 16 00        mov dx, 0x16
53BA  F7 E2           mul dx
53BC  8B F8           mov di, ax
53BE  81 C7 E8 80     add di, 0x80e8
53C2  1E              push ds
53C3  57              push di
53C4  0E              push cs
53C5  E8 77 F9        call 0x4d3f
53C8  80 3E 03 83 00  cmp byte ptr [0x8303], 0
53CD  75 0D           jne 0x53dc
53CF  B8 64 00        mov ax, 0x64
53D2  50              push ax
53D3  B8 05 00        mov ax, 5
53D6  50              push ax
53D7  9A A1 1E 4B 21  call far 214B:1EA1
loc_53DC:
53DC  80 3E 03 83 00  cmp byte ptr [0x8303], 0
53E1  75 3B           jne 0x541e
53E3  9A FA 06 4B 21  call far 214B:06FA
53E8  08 C0           or al, al
53EA  75 19           jne 0x5405
53EC  B8 03 00        mov ax, 3
53EF  50              push ax
53F0  8B 7E 04        mov di, word ptr [bp + 4]
53F3  36 8B 7D 04     mov di, word ptr ss:[di + 4]
53F7  36 C4 7D 06     les di, ptr ss:[di + 6]
53FB  06              push es
53FC  57              push di
53FD  0E              push cs
53FE  E8 7B D4        call 0x287c
5401  08 C0           or al, al
5403  74 19           je 0x541e
loc_5405:
5405  8B 7E 04        mov di, word ptr [bp + 4]
5408  36 8B 7D 04     mov di, word ptr ss:[di + 4]
540C  36 C4 7D 06     les di, ptr ss:[di + 6]
5410  06              push es
5411  57              push di
5412  0E              push cs
5413  E8 89 32        call 0x869f
5416  B0 0E           mov al, 0xe
5418  50              push ax
5419  E8 87 D6        call 0x2aa3
541C  EB 50           jmp 0x546e
loc_541E:
541E  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5423  74 2C           je 0x5451
5425  FF 36 F6 82     push word ptr [0x82f6]
5429  8B 7E 04        mov di, word ptr [bp + 4]
542C  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5430  36 C4 7D 06     les di, ptr ss:[di + 6]
5434  06              push es
5435  57              push di
5436  0E              push cs
5437  E8 7E DA        call 0x2eb8
543A  08 C0           or al, al
543C  74 13           je 0x5451
543E  8B 7E 04        mov di, word ptr [bp + 4]
5441  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5445  36 C4 7D 06     les di, ptr ss:[di + 6]
5449  06              push es
544A  57              push di
544B  0E              push cs
544C  E8 3F EC        call 0x408e
544F  EB 1D           jmp 0x546e
loc_5451:
5451  8B 7E 04        mov di, word ptr [bp + 4]
5454  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5458  36 C4 7D 06     les di, ptr ss:[di + 6]
545C  06              push es
545D  57              push di
545E  0E              push cs
545F  E8 DF 09        call 0x5e41
5462  B0 0E           mov al, 0xe
5464  50              push ax
5465  E8 3B D6        call 0x2aa3
5468  B0 21           mov al, 0x21
546A  50              push ax
546B  E8 35 D6        call 0x2aa3
loc_546E:
546E  89 EC           mov sp, bp
5470  5D              pop bp
5471  C2 02 00        ret 2

; ---- routine 0791:5474  (found by: call)
sub_5474:
5474  55              push bp
5475  89 E5           mov bp, sp
5477  83 EC 02        sub sp, 2
547A  C6 46 FF 00     mov byte ptr [bp - 1], 0
547E  A0 03 83        mov al, byte ptr [0x8303]
5481  98              cwde
5482  8B F8           mov di, ax
5484  8A 85 F6 07     mov al, byte ptr [di + 0x7f6]
5488  30 E4           xor ah, ah
548A  50              push ax
548B  A0 0B 83        mov al, byte ptr [0x830b]
548E  30 E4           xor ah, ah
5490  BA 16 00        mov dx, 0x16
5493  F7 E2           mul dx
5495  8B F8           mov di, ax
5497  81 C7 E8 80     add di, 0x80e8
549B  1E              push ds
549C  57              push di
549D  0E              push cs
549E  E8 E9 D2        call 0x278a
54A1  50              push ax
54A2  9A B1 06 4B 21  call far 214B:06B1
54A7  50              push ax
54A8  80 3E 03 83 00  cmp byte ptr [0x8303], 0
54AD  75 19           jne 0x54c8
54AF  8B 7E 04        mov di, word ptr [bp + 4]
54B2  36 8B 7D 04     mov di, word ptr ss:[di + 4]
54B6  36 C4 7D 06     les di, ptr ss:[di + 6]
54BA  06              push es
54BB  57              push di
54BC  0E              push cs
54BD  E8 94 D7        call 0x2c54
54C0  08 C0           or al, al
54C2  74 04           je 0x54c8
54C4  B0 00           mov al, 0
54C6  EB 02           jmp 0x54ca
loc_54C8:
54C8  B0 01           mov al, 1
loc_54CA:
54CA  98              cwde
54CB  8B F8           mov di, ax
54CD  8A 85 F8 07     mov al, byte ptr [di + 0x7f8]
54D1  30 E4           xor ah, ah
54D3  50              push ax
54D4  A0 03 83        mov al, byte ptr [0x8303]
54D7  98              cwde
54D8  8B F8           mov di, ax
54DA  8A 85 F4 07     mov al, byte ptr [di + 0x7f4]
54DE  30 E4           xor ah, ah
54E0  50              push ax
54E1  8B 7E 04        mov di, word ptr [bp + 4]
54E4  36 8B 7D 04     mov di, word ptr ss:[di + 4]
54E8  36 C4 7D 06     les di, ptr ss:[di + 6]
54EC  06              push es
54ED  57              push di
54EE  0E              push cs
54EF  E8 98 D2        call 0x278a
54F2  5A              pop dx
54F3  F7 E2           mul dx
54F5  50              push ax
54F6  9A B1 06 4B 21  call far 214B:06B1
54FB  5A              pop dx
54FC  3B C2           cmp ax, dx
54FE  7E 0A           jle 0x550a
5500  FF 76 04        push word ptr [bp + 4]
5503  E8 99 FE        call 0x539f
5506  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_550A:
550A  8A 46 FF        mov al, byte ptr [bp - 1]
550D  89 EC           mov sp, bp
550F  5D              pop bp
5510  C2 02 00        ret 2

; ---- routine 0791:5513  (found by: call)
sub_5513:
5513  55              push bp
5514  89 E5           mov bp, sp
5516  83 EC 02        sub sp, 2
5519  C6 46 FF 00     mov byte ptr [bp - 1], 0
551D  8B 7E 04        mov di, word ptr [bp + 4]
5520  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5524  36 C4 7D 06     les di, ptr ss:[di + 6]
5528  06              push es
5529  57              push di
552A  0E              push cs
552B  E8 7B F8        call 0x4da9
552E  08 C0           or al, al
5530  74 2A           je 0x555c
5532  9A FA 06 4B 21  call far 214B:06FA
5537  08 C0           or al, al
5539  74 17           je 0x5552
553B  8B 7E 04        mov di, word ptr [bp + 4]
553E  36 8B 7D 04     mov di, word ptr ss:[di + 4]
5542  36 C4 7D 06     les di, ptr ss:[di + 6]
5546  26 8A 45 06     mov al, byte ptr es:[di + 6]
554A  30 E4           xor ah, ah
554C  50              push ax
554D  E8 B6 2C        call 0x8206
5550  EB 06           jmp 0x5558
loc_5552:
5552  FF 76 04        push word ptr [bp + 4]
5555  E8 47 FE        call 0x539f
loc_5558:
5558  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_555C:
555C  8A 46 FF        mov al, byte ptr [bp - 1]
555F  89 EC           mov sp, bp
5561  5D              pop bp
5562  C2 02 00        ret 2

; ---- routine 0791:5565  (found by: call)
sub_5565:
5565  55              push bp
5566  89 E5           mov bp, sp
5568  83 EC 02        sub sp, 2
556B  C6 46 FF 00     mov byte ptr [bp - 1], 0
556F  80 3E 25 83 00  cmp byte ptr [0x8325], 0
5574  75 03           jne 0x5579
5576  E9 9A 00        jmp 0x5613
loc_5579:
5579  8B 7E 04        mov di, word ptr [bp + 4]
557C  36 C4 7D 06     les di, ptr ss:[di + 6]
5580  06              push es
5581  57              push di
5582  0E              push cs
5583  E8 66 D7        call 0x2cec
5586  08 C0           or al, al
5588  75 1C           jne 0x55a6
558A  A0 0B 83        mov al, byte ptr [0x830b]
558D  30 E4           xor ah, ah
558F  BA 16 00        mov dx, 0x16
5592  F7 E2           mul dx
5594  8B F8           mov di, ax
5596  8B 85 E8 80     mov ax, word ptr [di - 0x7f18]
559A  8B 7E 04        mov di, word ptr [bp + 4]
559D  36 C4 7D 06     les di, ptr ss:[di + 6]
55A1  26 3B 05        cmp ax, word ptr es:[di]
55A4  75 6D           jne 0x5613
loc_55A6:
55A6  8B 7E 04        mov di, word ptr [bp + 4]
55A9  36 C4 7D 06     les di, ptr ss:[di + 6]
55AD  06              push es
55AE  57              push di
55AF  0E              push cs
55B0  E8 9E D5        call 0x2b51
55B3  08 C0           or al, al
55B5  75 5C           jne 0x5613
55B7  80 3E 02 83 00  cmp byte ptr [0x8302], 0
55BC  75 55           jne 0x5613
55BE  A0 0B 83        mov al, byte ptr [0x830b]
55C1  30 E4           xor ah, ah
55C3  50              push ax
55C4  E8 96 AE        call 0x45d
55C7  08 C0           or al, al
55C9  75 48           jne 0x5613
55CB  8B 7E 04        mov di, word ptr [bp + 4]
55CE  36 C4 7D 06     les di, ptr ss:[di + 6]
55D2  06              push es
55D3  57              push di
55D4  0E              push cs
55D5  E8 50 D9        call 0x2f28
55D8  08 C0           or al, al
55DA  75 37           jne 0x5613
55DC  8B 7E 04        mov di, word ptr [bp + 4]
55DF  36 C4 7D 06     les di, ptr ss:[di + 6]
55E3  06              push es
55E4  57              push di
55E5  0E              push cs
55E6  E8 FC D5        call 0x2be5
55E9  98              cwde
55EA  8B D0           mov dx, ax
55EC  8B 7E 04        mov di, word ptr [bp + 4]
55EF  36 C4 7D 06     les di, ptr ss:[di + 6]
55F3  26 8A 45 01     mov al, byte ptr es:[di + 1]
55F7  98              cwde
55F8  F7 EA           imul dx
55FA  09 C0           or ax, ax
55FC  7E 18           jle 0x5616
55FE  B8 03 00        mov ax, 3
5601  50              push ax
5602  8B 7E 04        mov di, word ptr [bp + 4]
5605  36 C4 7D 06     les di, ptr ss:[di + 6]
5609  06              push es
560A  57              push di
560B  0E              push cs
560C  E8 6D D2        call 0x287c
560F  08 C0           or al, al
5611  75 03           jne 0x5616
loc_5613:
5613  E9 BA 00        jmp 0x56d0
loc_5616:
5616  C6 46 FF 01     mov byte ptr [bp - 1], 1
561A  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
561F  76 06           jbe 0x5627
5621  E8 C7 2C        call 0x82eb
5624  E9 A9 00        jmp 0x56d0
loc_5627:
5627  8B 7E 04        mov di, word ptr [bp + 4]
562A  36 C4 7D 06     les di, ptr ss:[di + 6]
562E  26 8A 45 06     mov al, byte ptr es:[di + 6]
5632  30 E4           xor ah, ah
5634  50              push ax
5635  E8 25 AE        call 0x45d
5638  08 C0           or al, al
563A  74 10           je 0x564c
563C  8B 7E 04        mov di, word ptr [bp + 4]
563F  36 C4 7D 06     les di, ptr ss:[di + 6]
5643  06              push es
5644  57              push di
5645  0E              push cs
5646  E8 ED 04        call 0x5b36
5649  E9 84 00        jmp 0x56d0
loc_564C:
564C  80 3E 03 83 00  cmp byte ptr [0x8303], 0
5651  74 12           je 0x5665
5653  B0 41           mov al, 0x41
5655  50              push ax
5656  8B 7E 04        mov di, word ptr [bp + 4]
5659  36 C4 7D 06     les di, ptr ss:[di + 6]
565D  06              push es
565E  57              push di
565F  0E              push cs
5660  E8 C5 D4        call 0x2b28
5663  EB 10           jmp 0x5675
loc_5665:
5665  B0 0B           mov al, 0xb
5667  50              push ax
5668  8B 7E 04        mov di, word ptr [bp + 4]
566B  36 C4 7D 06     les di, ptr ss:[di + 6]
566F  06              push es
5670  57              push di
5671  0E              push cs
5672  E8 B3 D4        call 0x2b28
loc_5675:
5675  55              push bp
5676  E8 FB FD        call 0x5474
5679  08 C0           or al, al
567B  75 53           jne 0x56d0
567D  55              push bp
567E  E8 92 FE        call 0x5513
5681  08 C0           or al, al
5683  75 4B           jne 0x56d0
5685  E8 C9 EA        call 0x4151
5688  08 C0           or al, al
568A  75 44           jne 0x56d0
568C  A0 0B 83        mov al, byte ptr [0x830b]
568F  30 E4           xor ah, ah
5691  50              push ax
5692  E8 C8 AD        call 0x45d
5695  08 C0           or al, al
5697  75 37           jne 0x56d0
5699  8B 7E 04        mov di, word ptr [bp + 4]
569C  36 C4 7D 06     les di, ptr ss:[di + 6]
56A0  06              push es
56A1  57              push di
56A2  0E              push cs
56A3  E8 99 F6        call 0x4d3f
56A6  80 3E 03 83 00  cmp byte ptr [0x8303], 0
56AB  75 08           jne 0x56b5
56AD  B0 0C           mov al, 0xc
56AF  50              push ax
56B0  E8 F0 D3        call 0x2aa3
56B3  EB 1B           jmp 0x56d0
loc_56B5:
56B5  8B 7E 04        mov di, word ptr [bp + 4]
56B8  36 C4 7D 06     les di, ptr ss:[di + 6]
56BC  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
56C0  BA 14 00        mov dx, 0x14
56C3  F7 E2           mul dx
56C5  C4 3E 1B A9     les di, ptr [0xa91b]
56C9  03 F8           add di, ax
56CB  26 83 45 12 0A  add word ptr es:[di + 0x12], 0xa
loc_56D0:
56D0  8A 46 FF        mov al, byte ptr [bp - 1]
56D3  89 EC           mov sp, bp
56D5  5D              pop bp
56D6  C2 02 00        ret 2

; ---- routine 0791:56D9  (found by: call)
sub_56D9:
56D9  55              push bp
56DA  89 E5           mov bp, sp
56DC  83 EC 02        sub sp, 2
56DF  C6 46 FF 00     mov byte ptr [bp - 1], 0
56E3  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
56E8  76 36           jbe 0x5720
56EA  A0 0E 83        mov al, byte ptr [0x830e]
56ED  30 E4           xor ah, ah
56EF  BA 16 00        mov dx, 0x16
56F2  F7 E2           mul dx
56F4  8B F8           mov di, ax
56F6  81 C7 E8 80     add di, 0x80e8
56FA  1E              push ds
56FB  57              push di
56FC  0E              push cs
56FD  E8 E5 D4        call 0x2be5
5700  08 C0           or al, al
5702  7C 04           jl 0x5708
5704  B0 00           mov al, 0
5706  EB 02           jmp 0x570a
loc_5708:
5708  B0 01           mov al, 1
loc_570A:
570A  50              push ax
570B  E8 92 CF        call 0x26a0
570E  80 3E 29 83 00  cmp byte ptr [0x8329], 0
5713  75 06           jne 0x571b
5715  B0 42           mov al, 0x42
5717  50              push ax
5718  E8 F4 D3        call 0x2b0f
loc_571B:
571B  C6 06 29 83 01  mov byte ptr [0x8329], 1
loc_5720:
5720  8A 46 FF        mov al, byte ptr [bp - 1]
5723  89 EC           mov sp, bp
5725  5D              pop bp
5726  C2 02 00        ret 2

; ---- routine 0791:5729  (found by: call)
sub_5729:
5729  55              push bp
572A  89 E5           mov bp, sp
572C  83 EC 02        sub sp, 2
572F  8B 7E 04        mov di, word ptr [bp + 4]
5732  36 C4 7D 06     les di, ptr ss:[di + 6]
5736  26 8A 45 06     mov al, byte ptr es:[di + 6]
573A  30 E4           xor ah, ah
573C  50              push ax
573D  E8 1D AD        call 0x45d
5740  08 C0           or al, al
5742  75 56           jne 0x579a
5744  8B 7E 04        mov di, word ptr [bp + 4]
5747  36 C4 7D 06     les di, ptr ss:[di + 6]
574B  06              push es
574C  57              push di
574D  0E              push cs
574E  E8 00 D4        call 0x2b51
5751  08 C0           or al, al
5753  75 45           jne 0x579a
5755  FF 36 F6 82     push word ptr [0x82f6]
5759  8B 7E 04        mov di, word ptr [bp + 4]
575C  36 C4 7D 06     les di, ptr ss:[di + 6]
5760  06              push es
5761  57              push di
5762  0E              push cs
5763  E8 52 D7        call 0x2eb8
5766  08 C0           or al, al
5768  74 30           je 0x579a
576A  8B 7E 04        mov di, word ptr [bp + 4]
576D  36 C4 7D 06     les di, ptr ss:[di + 6]
5771  26 FF 35        push word ptr es:[di]
5774  8B 7E 04        mov di, word ptr [bp + 4]
5777  36 C4 7D 06     les di, ptr ss:[di + 6]
577B  06              push es
577C  57              push di
577D  0E              push cs
577E  E8 6F D7        call 0x2ef0
5781  08 C0           or al, al
5783  75 19           jne 0x579e
5785  B8 06 00        mov ax, 6
5788  50              push ax
5789  8B 7E 04        mov di, word ptr [bp + 4]
578C  36 C4 7D 06     les di, ptr ss:[di + 6]
5790  06              push es
5791  57              push di
5792  0E              push cs
5793  E8 41 CF        call 0x26d7
5796  08 C0           or al, al
5798  74 04           je 0x579e
loc_579A:
579A  B0 00           mov al, 0
579C  EB 02           jmp 0x57a0
loc_579E:
579E  B0 01           mov al, 1
loc_57A0:
57A0  88 46 FF        mov byte ptr [bp - 1], al
57A3  8A 46 FF        mov al, byte ptr [bp - 1]
57A6  89 EC           mov sp, bp
57A8  5D              pop bp
57A9  C2 02 00        ret 2

; ---- routine 0791:57AC  (found by: call)
sub_57AC:
57AC  55              push bp
57AD  89 E5           mov bp, sp
57AF  83 EC 02        sub sp, 2
57B2  55              push bp
57B3  E8 23 FF        call 0x56d9
57B6  08 C0           or al, al
57B8  75 18           jne 0x57d2
57BA  55              push bp
57BB  E8 8B F8        call 0x5049
57BE  08 C0           or al, al
57C0  75 10           jne 0x57d2
57C2  55              push bp
57C3  E8 75 FB        call 0x533b
57C6  08 C0           or al, al
57C8  75 08           jne 0x57d2
57CA  55              push bp
57CB  E8 97 FD        call 0x5565
57CE  08 C0           or al, al
57D0  74 03           je 0x57d5
loc_57D2:
57D2  E9 06 01        jmp 0x58db
loc_57D5:
57D5  A0 0B 83        mov al, byte ptr [0x830b]
57D8  30 E4           xor ah, ah
57DA  50              push ax
57DB  E8 7F AC        call 0x45d
57DE  08 C0           or al, al
57E0  74 13           je 0x57f5
57E2  80 3E 02 83 00  cmp byte ptr [0x8302], 0
57E7  75 0C           jne 0x57f5
57E9  C4 7E 06        les di, ptr [bp + 6]
57EC  06              push es
57ED  57              push di
57EE  0E              push cs
57EF  E8 72 F3        call 0x4b64
57F2  E9 E6 00        jmp 0x58db
loc_57F5:
57F5  80 3E 27 83 05  cmp byte ptr [0x8327], 5
57FA  75 14           jne 0x5810
57FC  83 3E 00 83 00  cmp word ptr [0x8300], 0
5801  76 0D           jbe 0x5810
5803  A1 F6 82        mov ax, word ptr [0x82f6]
5806  C4 7E 06        les di, ptr [bp + 6]
5809  26 89 45 07     mov word ptr es:[di + 7], ax
580D  E9 B2 00        jmp 0x58c2
loc_5810:
5810  80 3E 25 83 00  cmp byte ptr [0x8325], 0
5815  75 03           jne 0x581a
5817  E9 9F 00        jmp 0x58b9
loc_581A:
581A  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
581F  74 26           je 0x5847
5821  C4 7E 06        les di, ptr [bp + 6]
5824  06              push es
5825  57              push di
5826  0E              push cs
5827  E8 87 D3        call 0x2bb1
582A  3C 02           cmp al, 2
582C  74 19           je 0x5847
582E  C4 7E 06        les di, ptr [bp + 6]
5831  26 8B 45 0D     mov ax, word ptr es:[di + 0xd]
5835  BA 14 00        mov dx, 0x14
5838  F7 E2           mul dx
583A  C4 3E 1B A9     les di, ptr [0xa91b]
583E  03 F8           add di, ax
5840  26 80 7D 06 01  cmp byte ptr es:[di + 6], 1
5845  75 72           jne 0x58b9
loc_5847:
5847  80 3E 02 83 00  cmp byte ptr [0x8302], 0
584C  75 0D           jne 0x585b
584E  C4 7E 06        les di, ptr [bp + 6]
5851  06              push es
5852  57              push di
5853  0E              push cs
5854  E8 FA D2        call 0x2b51
5857  08 C0           or al, al
5859  75 5E           jne 0x58b9
loc_585B:
585B  55              push bp
585C  E8 CA FE        call 0x5729
585F  08 C0           or al, al
5861  75 4A           jne 0x58ad
5863  C4 7E 06        les di, ptr [bp + 6]
5866  06              push es
5867  57              push di
5868  0E              push cs
5869  E8 08 D1        call 0x2974
586C  98              cwde
586D  8B F8           mov di, ax
586F  8A 85 11 83     mov al, byte ptr [di - 0x7cef]
5873  C4 7E 06        les di, ptr [bp + 6]
5876  26 3A 45 06     cmp al, byte ptr es:[di + 6]
587A  74 31           je 0x58ad
587C  C4 7E 06        les di, ptr [bp + 6]
587F  06              push es
5880  57              push di
5881  0E              push cs
5882  E8 EF D0        call 0x2974
5885  98              cwde
5886  8B F8           mov di, ax
5888  8A 85 0F 83     mov al, byte ptr [di - 0x7cf1]
588C  C4 7E 06        les di, ptr [bp + 6]
588F  26 3A 45 06     cmp al, byte ptr es:[di + 6]
5893  74 18           je 0x58ad
5895  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
589A  75 1D           jne 0x58b9
589C  FF 36 F6 82     push word ptr [0x82f6]
58A0  C4 7E 06        les di, ptr [bp + 6]
58A3  06              push es
58A4  57              push di
58A5  0E              push cs
58A6  E8 18 EC        call 0x44c1
58A9  08 C0           or al, al
58AB  74 0C           je 0x58b9
loc_58AD:
58AD  A1 F6 82        mov ax, word ptr [0x82f6]
58B0  C4 7E 06        les di, ptr [bp + 6]
58B3  26 89 45 07     mov word ptr es:[di + 7], ax
58B7  EB 09           jmp 0x58c2
loc_58B9:
58B9  C4 7E 06        les di, ptr [bp + 6]
58BC  06              push es
58BD  57              push di
58BE  0E              push cs
58BF  E8 66 F1        call 0x4a28
loc_58C2:
58C2  C4 7E 06        les di, ptr [bp + 6]
58C5  06              push es
58C6  57              push di
58C7  0E              push cs
58C8  E8 82 EE        call 0x474d
58CB  80 3E 02 83 00  cmp byte ptr [0x8302], 0
58D0  74 09           je 0x58db
58D2  C4 7E 06        les di, ptr [bp + 6]
58D5  06              push es
58D6  57              push di
58D7  0E              push cs
58D8  E8 AD 08        call 0x6188
loc_58DB:
58DB  89 EC           mov sp, bp
58DD  5D              pop bp
58DE  CA 04 00        retf 4

; ---- routine 0791:58E1  (found by: call)
sub_58E1:
58E1  55              push bp
58E2  89 E5           mov bp, sp
58E4  C4 7E 06        les di, ptr [bp + 6]
58E7  26 8A 45 06     mov al, byte ptr es:[di + 6]
58EB  30 E4           xor ah, ah
58ED  50              push ax
58EE  E8 6C AB        call 0x45d
58F1  08 C0           or al, al
58F3  74 18           je 0x590d
58F5  80 3E 02 83 00  cmp byte ptr [0x8302], 0
58FA  74 11           je 0x590d
58FC  83 3E 00 83 00  cmp word ptr [0x8300], 0
5901  75 0A           jne 0x590d
5903  C4 7E 06        les di, ptr [bp + 6]
5906  26 C6 45 12 05  mov byte ptr es:[di + 0x12], 5
590B  EB 1B           jmp 0x5928
loc_590D:
590D  C4 7E 06        les di, ptr [bp + 6]
5910  26 80 7D 10 00  cmp byte ptr es:[di + 0x10], 0
5915  76 09           jbe 0x5920
5917  C4 7E 06        les di, ptr [bp + 6]
591A  26 FE 4D 10     dec byte ptr es:[di + 0x10]
591E  EB 08           jmp 0x5928
loc_5920:
5920  C4 7E 06        les di, ptr [bp + 6]
5923  26 C6 45 12 05  mov byte ptr es:[di + 0x12], 5
loc_5928:
5928  C4 7E 06        les di, ptr [bp + 6]
592B  26 8B 05        mov ax, word ptr es:[di]
592E  C4 7E 06        les di, ptr [bp + 6]
5931  26 89 45 07     mov word ptr es:[di + 7], ax
5935  89 EC           mov sp, bp
5937  5D              pop bp
5938  CA 04 00        retf 4

; ---- routine 0791:593B  (found by: call)
sub_593B:
593B  55              push bp
593C  89 E5           mov bp, sp
593E  A0 24 83        mov al, byte ptr [0x8324]
5941  98              cwde
5942  8B F8           mov di, ax
5944  8A 85 FC 07     mov al, byte ptr [di + 0x7fc]
5948  30 E4           xor ah, ah
594A  50              push ax
594B  9A D0 06 4B 21  call far 214B:06D0
5950  08 C0           or al, al
5952  74 59           je 0x59ad
5954  80 3E 27 83 05  cmp byte ptr [0x8327], 5
5959  74 0F           je 0x596a
595B  80 7E 06 1B     cmp byte ptr [bp + 6], 0x1b
595F  75 0B           jne 0x596c
5961  9A FA 06 4B 21  call far 214B:06FA
5966  08 C0           or al, al
5968  74 02           je 0x596c
loc_596A:
596A  EB 41           jmp 0x59ad
loc_596C:
596C  A1 FE 82        mov ax, word ptr [0x82fe]
596F  F7 D8           neg ax
5971  A3 FE 82        mov word ptr [0x82fe], ax
5974  A1 FC 82        mov ax, word ptr [0x82fc]
5977  F7 D8           neg ax
5979  A3 FC 82        mov word ptr [0x82fc], ax
597C  B8 01 00        mov ax, 1
597F  31 D2           xor dx, dx
5981  52              push dx
5982  50              push ax
5983  A1 00 83        mov ax, word ptr [0x8300]
5986  31 D2           xor dx, dx
5988  B9 04 00        mov cx, 4
598B  F7 F1           div cx
598D  31 D2           xor dx, dx
598F  52              push dx
5990  50              push ax
5991  9A 56 0D 4B 21  call far 214B:0D56
5996  A3 00 83        mov word ptr [0x8300], ax
5999  8A 46 06        mov al, byte ptr [bp + 6]
599C  50              push ax
599D  E8 03 D1        call 0x2aa3
59A0  8B 7E 04        mov di, word ptr [bp + 4]
59A3  36 C6 45 FF 01  mov byte ptr ss:[di - 1], 1
59A8  C6 06 24 83 00  mov byte ptr [0x8324], 0
loc_59AD:
59AD  89 EC           mov sp, bp
59AF  5D              pop bp
59B0  C2 04 00        ret 4

