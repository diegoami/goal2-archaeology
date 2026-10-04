; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 6 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:3323  (found by: call)
sub_3323:
3323  55              push bp
3324  89 E5           mov bp, sp
3326  C4 7E 06        les di, ptr [bp + 6]
3329  06              push es
332A  57              push di
332B  0E              push cs
332C  E8 E2 FD        call 0x3111
332F  50              push ax
3330  C4 7E 06        les di, ptr [bp + 6]
3333  06              push es
3334  57              push di
3335  0E              push cs
3336  E8 13 05        call 0x384c
3339  89 EC           mov sp, bp
333B  5D              pop bp
333C  CA 04 00        retf 4

; ---- routine 0791:333F  (found by: call)
sub_333F:
333F  55              push bp
3340  89 E5           mov bp, sp
3342  83 EC 04        sub sp, 4
3345  80 3E 25 83 00  cmp byte ptr [0x8325], 0
334A  75 08           jne 0x3354
334C  C6 06 25 83 01  mov byte ptr [0x8325], 1
3351  E9 27 01        jmp 0x347b
loc_3354:
3354  B8 0B 00        mov ax, 0xb
3357  50              push ax
3358  8B 7E 04        mov di, word ptr [bp + 4]
335B  36 C4 7D 06     les di, ptr ss:[di + 6]
335F  06              push es
3360  57              push di
3361  0E              push cs
3362  E8 85 FD        call 0x30ea
3365  89 46 FC        mov word ptr [bp - 4], ax
3368  B8 01 00        mov ax, 1
336B  50              push ax
336C  8B 7E 04        mov di, word ptr [bp + 4]
336F  36 C4 7D 06     les di, ptr ss:[di + 6]
3373  06              push es
3374  57              push di
3375  0E              push cs
3376  E8 71 FD        call 0x30ea
3379  3B 46 FC        cmp ax, word ptr [bp - 4]
337C  76 03           jbe 0x3381
337E  E9 FA 00        jmp 0x347b
loc_3381:
3381  89 46 FE        mov word ptr [bp - 2], ax
3384  EB 03           jmp 0x3389
loc_3386:
3386  FF 46 FE        inc word ptr [bp - 2]
loc_3389:
3389  8B 46 FE        mov ax, word ptr [bp - 2]
338C  BA 16 00        mov dx, 0x16
338F  F7 E2           mul dx
3391  8B F8           mov di, ax
3393  8A 85 EE 80     mov al, byte ptr [di - 0x7f12]
3397  8B 7E 04        mov di, word ptr [bp + 4]
339A  36 C4 7D 06     les di, ptr ss:[di + 6]
339E  26 3A 45 06     cmp al, byte ptr es:[di + 6]
33A2  75 03           jne 0x33a7
33A4  E9 C9 00        jmp 0x3470
loc_33A7:
33A7  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
33AC  74 03           je 0x33b1
33AE  E9 BF 00        jmp 0x3470
loc_33B1:
33B1  8B 46 FE        mov ax, word ptr [bp - 2]
33B4  BA 16 00        mov dx, 0x16
33B7  F7 E2           mul dx
33B9  8B F8           mov di, ax
33BB  8A 85 EE 80     mov al, byte ptr [di - 0x7f12]
33BF  3A 06 0A 83     cmp al, byte ptr [0x830a]
33C3  75 03           jne 0x33c8
33C5  E9 A8 00        jmp 0x3470
loc_33C8:
33C8  E8 CB F5        call 0x2996
33CB  08 C0           or al, al
33CD  74 04           je 0x33d3
33CF  B0 00           mov al, 0
33D1  EB 02           jmp 0x33d5
loc_33D3:
33D3  B0 01           mov al, 1
loc_33D5:
33D5  98              cwde
33D6  8B F8           mov di, ax
33D8  D1 E7           shl di, 1
33DA  8B F7           mov si, di
33DC  D1 E7           shl di, 1
33DE  03 FE           add di, si
33E0  8A 85 E3 82     mov al, byte ptr [di - 0x7d1d]
33E4  98              cwde
33E5  09 C0           or ax, ax
33E7  79 02           jns 0x33eb
33E9  F7 D8           neg ax
loc_33EB:
33EB  8B C8           mov cx, ax
33ED  8B 46 FE        mov ax, word ptr [bp - 2]
33F0  BA 16 00        mov dx, 0x16
33F3  F7 E2           mul dx
33F5  8B F8           mov di, ax
33F7  8A 85 E9 80     mov al, byte ptr [di - 0x7f17]
33FB  98              cwde
33FC  09 C0           or ax, ax
33FE  79 02           jns 0x3402
3400  F7 D8           neg ax
loc_3402:
3402  3B C1           cmp ax, cx
3404  7E 6A           jle 0x3470
3406  8B 46 FE        mov ax, word ptr [bp - 2]
3409  BA 16 00        mov dx, 0x16
340C  F7 E2           mul dx
340E  8B F8           mov di, ax
3410  81 C7 E8 80     add di, 0x80e8
3414  1E              push ds
3415  57              push di
3416  0E              push cs
3417  E8 CB F7        call 0x2be5
341A  08 C0           or al, al
341C  7F 04           jg 0x3422
341E  B0 00           mov al, 0
3420  EB 02           jmp 0x3424
loc_3422:
3422  B0 01           mov al, 1
loc_3424:
3424  8A C8           mov cl, al
3426  8B 46 FE        mov ax, word ptr [bp - 2]
3429  BA 16 00        mov dx, 0x16
342C  F7 E2           mul dx
342E  8B F8           mov di, ax
3430  80 BD E9 80 00  cmp byte ptr [di - 0x7f17], 0
3435  7F 04           jg 0x343b
3437  B0 00           mov al, 0
3439  EB 02           jmp 0x343d
loc_343B:
343B  B0 01           mov al, 1
loc_343D:
343D  3A C1           cmp al, cl
343F  75 2F           jne 0x3470
3441  8B 46 FE        mov ax, word ptr [bp - 2]
3444  BA 16 00        mov dx, 0x16
3447  F7 E2           mul dx
3449  8B F8           mov di, ax
344B  80 BD F8 80 00  cmp byte ptr [di - 0x7f08], 0
3450  75 1E           jne 0x3470
3452  8A 46 FE        mov al, byte ptr [bp - 2]
3455  A2 0E 83        mov byte ptr [0x830e], al
3458  8B 46 FE        mov ax, word ptr [bp - 2]
345B  BA 16 00        mov dx, 0x16
345E  F7 E2           mul dx
3460  8B F8           mov di, ax
3462  8B 85 E8 80     mov ax, word ptr [di - 0x7f18]
3466  A3 17 83        mov word ptr [0x8317], ax
3469  C6 06 29 83 00  mov byte ptr [0x8329], 0
346E  EB 0B           jmp 0x347b
loc_3470:
3470  8B 46 FE        mov ax, word ptr [bp - 2]
3473  3B 46 FC        cmp ax, word ptr [bp - 4]
3476  74 03           je 0x347b
3478  E9 0B FF        jmp 0x3386
loc_347B:
347B  89 EC           mov sp, bp
347D  5D              pop bp
347E  C2 02 00        ret 2
; data (not reached as code), 64 bytes
3481                  db 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
3491                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
34A1                  db 18 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
34B1                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 0791:34C1  (found by: call)
sub_34C1:
34C1  55              push bp
34C2  89 E5           mov bp, sp
34C4  83 EC 06        sub sp, 6
34C7  C4 7E 06        les di, ptr [bp + 6]
34CA  26 C6 45 0F 05  mov byte ptr es:[di + 0xf], 5
34CF  8B 46 0C        mov ax, word ptr [bp + 0xc]
34D2  89 46 FE        mov word ptr [bp - 2], ax
34D5  C6 06 02 83 01  mov byte ptr [0x8302], 1
34DA  C4 7E 06        les di, ptr [bp + 6]
34DD  26 8A 45 06     mov al, byte ptr es:[di + 6]
34E1  A2 0B 83        mov byte ptr [0x830b], al
34E4  A0 F6 82        mov al, byte ptr [0x82f6]
34E7  28 46 FE        sub byte ptr [bp - 2], al
34EA  A0 F7 82        mov al, byte ptr [0x82f7]
34ED  28 46 FF        sub byte ptr [bp - 1], al
34F0  31 C0           xor ax, ax
34F2  A3 FC 82        mov word ptr [0x82fc], ax
34F5  31 C0           xor ax, ax
34F7  A3 FE 82        mov word ptr [0x82fe], ax
34FA  8A 46 FF        mov al, byte ptr [bp - 1]
34FD  98              cwde
34FE  09 C0           or ax, ax
3500  79 02           jns 0x3504
3502  F7 D8           neg ax
loc_3504:
3504  8B D0           mov dx, ax
3506  8A 46 FE        mov al, byte ptr [bp - 2]
3509  98              cwde
350A  09 C0           or ax, ax
350C  79 02           jns 0x3510
350E  F7 D8           neg ax
loc_3510:
3510  3B C2           cmp ax, dx
3512  7E 6C           jle 0x3580
3514  80 7E FE 00     cmp byte ptr [bp - 2], 0
3518  7F 04           jg 0x351e
351A  B0 00           mov al, 0
351C  EB 02           jmp 0x3520
loc_351E:
351E  B0 01           mov al, 1
loc_3520:
3520  98              cwde
3521  8B F8           mov di, ax
3523  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3527  98              cwde
3528  A3 FC 82        mov word ptr [0x82fc], ax
352B  8A 46 FE        mov al, byte ptr [bp - 2]
352E  98              cwde
352F  09 C0           or ax, ax
3531  79 02           jns 0x3535
3533  F7 D8           neg ax
loc_3535:
3535  A3 00 83        mov word ptr [0x8300], ax
3538  8A 46 FE        mov al, byte ptr [bp - 2]
353B  98              cwde
353C  09 C0           or ax, ax
353E  79 02           jns 0x3542
3540  F7 D8           neg ax
loc_3542:
3542  99              cdq
3543  B9 02 00        mov cx, 2
3546  F7 F9           idiv cx
3548  8B D0           mov dx, ax
354A  8A 46 FF        mov al, byte ptr [bp - 1]
354D  98              cwde
354E  09 C0           or ax, ax
3550  79 02           jns 0x3554
3552  F7 D8           neg ax
loc_3554:
3554  3B C2           cmp ax, dx
3556  7C 25           jl 0x357d
3558  80 7E FF 00     cmp byte ptr [bp - 1], 0
355C  7F 04           jg 0x3562
355E  B0 00           mov al, 0
3560  EB 02           jmp 0x3564
loc_3562:
3562  B0 01           mov al, 1
loc_3564:
3564  98              cwde
3565  8B F8           mov di, ax
3567  8A 85 20 79     mov al, byte ptr [di + 0x7920]
356B  98              cwde
356C  A3 FE 82        mov word ptr [0x82fe], ax
356F  8A 46 FF        mov al, byte ptr [bp - 1]
3572  98              cwde
3573  09 C0           or ax, ax
3575  79 02           jns 0x3579
3577  F7 D8           neg ax
loc_3579:
3579  01 06 00 83     add word ptr [0x8300], ax
loc_357D:
357D  E9 9F 00        jmp 0x361f
loc_3580:
3580  80 7E FF 00     cmp byte ptr [bp - 1], 0
3584  7F 04           jg 0x358a
3586  B0 00           mov al, 0
3588  EB 02           jmp 0x358c
loc_358A:
358A  B0 01           mov al, 1
loc_358C:
358C  98              cwde
358D  8B F8           mov di, ax
358F  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3593  98              cwde
3594  A3 FE 82        mov word ptr [0x82fe], ax
3597  8A 46 FF        mov al, byte ptr [bp - 1]
359A  98              cwde
359B  09 C0           or ax, ax
359D  79 02           jns 0x35a1
359F  F7 D8           neg ax
loc_35A1:
35A1  A3 00 83        mov word ptr [0x8300], ax
35A4  8A 46 FE        mov al, byte ptr [bp - 2]
35A7  98              cwde
35A8  09 C0           or ax, ax
35AA  79 02           jns 0x35ae
35AC  F7 D8           neg ax
loc_35AE:
35AE  09 C0           or ax, ax
35B0  7E 6D           jle 0x361f
35B2  8A 46 FF        mov al, byte ptr [bp - 1]
35B5  98              cwde
35B6  09 C0           or ax, ax
35B8  79 02           jns 0x35bc
35BA  F7 D8           neg ax
loc_35BC:
35BC  99              cdq
35BD  B9 02 00        mov cx, 2
35C0  F7 F9           idiv cx
35C2  8B D0           mov dx, ax
35C4  8A 46 FE        mov al, byte ptr [bp - 2]
35C7  98              cwde
35C8  09 C0           or ax, ax
35CA  79 02           jns 0x35ce
35CC  F7 D8           neg ax
loc_35CE:
35CE  3B C2           cmp ax, dx
35D0  7C 4D           jl 0x361f
35D2  80 7E FE 00     cmp byte ptr [bp - 2], 0
35D6  7F 04           jg 0x35dc
35D8  B0 00           mov al, 0
35DA  EB 02           jmp 0x35de
loc_35DC:
35DC  B0 01           mov al, 1
loc_35DE:
35DE  98              cwde
35DF  8B F8           mov di, ax
35E1  8A 85 20 79     mov al, byte ptr [di + 0x7920]
35E5  98              cwde
35E6  A3 FC 82        mov word ptr [0x82fc], ax
35E9  8A 46 FE        mov al, byte ptr [bp - 2]
35EC  98              cwde
35ED  09 C0           or ax, ax
35EF  79 02           jns 0x35f3
35F1  F7 D8           neg ax
loc_35F3:
35F3  01 06 00 83     add word ptr [0x8300], ax
35F7  8A 46 FE        mov al, byte ptr [bp - 2]
35FA  98              cwde
35FB  09 C0           or ax, ax
35FD  79 02           jns 0x3601
35FF  F7 D8           neg ax
loc_3601:
3601  99              cdq
3602  B9 02 00        mov cx, 2
3605  F7 F9           idiv cx
3607  8B D0           mov dx, ax
3609  8A 46 FF        mov al, byte ptr [bp - 1]
360C  98              cwde
360D  09 C0           or ax, ax
360F  79 02           jns 0x3613
3611  F7 D8           neg ax
loc_3613:
3613  3B C2           cmp ax, dx
3615  7C 08           jl 0x361f
3617  A1 FE 82        mov ax, word ptr [0x82fe]
361A  D1 E0           shl ax, 1
361C  A3 FE 82        mov word ptr [0x82fe], ax
loc_361F:
361F  83 7E 0A 06     cmp word ptr [bp + 0xa], 6
3623  75 35           jne 0x365a
3625  83 3E 00 83 14  cmp word ptr [0x8300], 0x14
362A  76 07           jbe 0x3633
362C  C7 46 0A 07 00  mov word ptr [bp + 0xa], 7
3631  EB 27           jmp 0x365a
loc_3633:
3633  C4 7E 06        les di, ptr [bp + 6]
3636  26 8A 45 06     mov al, byte ptr es:[di + 6]
363A  30 E4           xor ah, ah
363C  50              push ax
363D  E8 1D CE        call 0x45d
3640  08 C0           or al, al
3642  74 16           je 0x365a
3644  FF 36 F6 82     push word ptr [0x82f6]
3648  C4 7E 06        les di, ptr [bp + 6]
364B  06              push es
364C  57              push di
364D  0E              push cs
364E  E8 67 F8        call 0x2eb8
3651  08 C0           or al, al
3653  74 05           je 0x365a
3655  C7 46 0A 08 00  mov word ptr [bp + 0xa], 8
loc_365A:
365A  8A 46 0A        mov al, byte ptr [bp + 0xa]
365D  A2 27 83        mov byte ptr [0x8327], al
3660  8A 46 0A        mov al, byte ptr [bp + 0xa]
3663  50              push ax
3664  BF 81 34        mov di, 0x3481
3667  0E              push cs
3668  57              push di
3669  9A DF 08 E4 23  call far 23E4:08DF
366E  74 40           je 0x36b0
3670  A1 00 83        mov ax, word ptr [0x8300]
3673  05 05 00        add ax, 5
3676  31 D2           xor dx, dx
3678  52              push dx
3679  50              push ax
367A  8B 7E 0A        mov di, word ptr [bp + 0xa]
367D  8A 85 79 07     mov al, byte ptr [di + 0x779]
3681  30 E4           xor ah, ah
3683  50              push ax
3684  C4 7E 06        les di, ptr [bp + 6]
3687  06              push es
3688  57              push di
3689  0E              push cs
368A  E8 FD F0        call 0x278a
368D  8B D0           mov dx, ax
368F  C4 7E 06        les di, ptr [bp + 6]
3692  26 8A 45 11     mov al, byte ptr es:[di + 0x11]
3696  30 E4           xor ah, ah
3698  03 C2           add ax, dx
369A  31 D2           xor dx, dx
369C  B9 03 00        mov cx, 3
369F  F7 F1           div cx
36A1  31 D2           xor dx, dx
36A3  52              push dx
36A4  50              push ax
36A5  9A 56 0D 4B 21  call far 214B:0D56
36AA  A3 00 83        mov word ptr [0x8300], ax
36AD  E9 12 01        jmp 0x37c2
loc_36B0:
36B0  8A 46 0A        mov al, byte ptr [bp + 0xa]
36B3  50              push ax
36B4  BF A1 34        mov di, 0x34a1
36B7  0E              push cs
36B8  57              push di
36B9  9A DF 08 E4 23  call far 23E4:08DF
36BE  74 33           je 0x36f3
36C0  A1 00 83        mov ax, word ptr [0x8300]
36C3  05 05 00        add ax, 5
36C6  31 D2           xor dx, dx
36C8  52              push dx
36C9  50              push ax
36CA  8B 7E 0A        mov di, word ptr [bp + 0xa]
36CD  8A 85 79 07     mov al, byte ptr [di + 0x779]
36D1  30 E4           xor ah, ah
36D3  50              push ax
36D4  C4 7E 06        les di, ptr [bp + 6]
36D7  06              push es
36D8  57              push di
36D9  0E              push cs
36DA  E8 AD F0        call 0x278a
36DD  31 D2           xor dx, dx
36DF  B9 03 00        mov cx, 3
36E2  F7 F1           div cx
36E4  31 D2           xor dx, dx
36E6  52              push dx
36E7  50              push ax
36E8  9A 56 0D 4B 21  call far 214B:0D56
36ED  A3 00 83        mov word ptr [0x8300], ax
36F0  E9 CF 00        jmp 0x37c2
loc_36F3:
36F3  83 7E 0A 08     cmp word ptr [bp + 0xa], 8
36F7  75 03           jne 0x36fc
36F9  E9 C6 00        jmp 0x37c2
loc_36FC:
36FC  83 3E 00 83 01  cmp word ptr [0x8300], 1
3701  77 03           ja 0x3706
3703  E9 BC 00        jmp 0x37c2
loc_3706:
3706  A0 0B 83        mov al, byte ptr [0x830b]
3709  3A 06 0C 83     cmp al, byte ptr [0x830c]
370D  75 03           jne 0x3712
370F  E9 B0 00        jmp 0x37c2
loc_3712:
3712  8B 7E 0A        mov di, word ptr [bp + 0xa]
3715  8A 85 79 07     mov al, byte ptr [di + 0x779]
3719  30 E4           xor ah, ah
371B  50              push ax
371C  C4 7E 06        les di, ptr [bp + 6]
371F  06              push es
3720  57              push di
3721  0E              push cs
3722  E8 57 F1        call 0x287c
3725  08 C0           or al, al
3727  74 03           je 0x372c
3729  E9 96 00        jmp 0x37c2
loc_372C:
372C  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3731  C4 7E 06        les di, ptr [bp + 6]
3734  26 8A 45 06     mov al, byte ptr es:[di + 6]
3738  30 E4           xor ah, ah
373A  50              push ax
373B  E8 1F CD        call 0x45d
373E  08 C0           or al, al
3740  74 03           je 0x3745
3742  E9 7D 00        jmp 0x37c2
loc_3745:
3745  9A FA 06 4B 21  call far 214B:06FA
374A  08 C0           or al, al
374C  75 07           jne 0x3755
374E  80 3E 23 83 00  cmp byte ptr [0x8323], 0
3753  74 16           je 0x376b
loc_3755:
3755  A1 00 83        mov ax, word ptr [0x8300]
3758  31 D2           xor dx, dx
375A  B9 02 00        mov cx, 2
375D  F7 F1           div cx
375F  50              push ax
3760  9A B1 06 4B 21  call far 214B:06B1
3765  29 06 00 83     sub word ptr [0x8300], ax
3769  EB 57           jmp 0x37c2
loc_376B:
376B  83 3E FC 82 00  cmp word ptr [0x82fc], 0
3770  75 2B           jne 0x379d
3772  9A FA 06 4B 21  call far 214B:06FA
3777  98              cwde
3778  8B F8           mov di, ax
377A  8A 85 20 79     mov al, byte ptr [di + 0x7920]
377E  98              cwde
377F  A3 FC 82        mov word ptr [0x82fc], ax
3782  83 3E FE 82 00  cmp word ptr [0x82fe], 0
3787  7F 04           jg 0x378d
3789  B0 00           mov al, 0
378B  EB 02           jmp 0x378f
loc_378D:
378D  B0 01           mov al, 1
loc_378F:
378F  98              cwde
3790  8B F8           mov di, ax
3792  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3796  98              cwde
3797  01 06 FE 82     add word ptr [0x82fe], ax
379B  EB 25           jmp 0x37c2
loc_379D:
379D  A1 FE 82        mov ax, word ptr [0x82fe]
37A0  09 C0           or ax, ax
37A2  79 02           jns 0x37a6
37A4  F7 D8           neg ax
loc_37A6:
37A6  3D 01 00        cmp ax, 1
37A9  75 07           jne 0x37b2
37AB  31 C0           xor ax, ax
37AD  A3 FE 82        mov word ptr [0x82fe], ax
37B0  EB 10           jmp 0x37c2
loc_37B2:
37B2  9A FA 06 4B 21  call far 214B:06FA
37B7  98              cwde
37B8  8B F8           mov di, ax
37BA  8A 85 20 79     mov al, byte ptr [di + 0x7920]
37BE  98              cwde
37BF  A3 FE 82        mov word ptr [0x82fe], ax
loc_37C2:
37C2  C6 06 23 83 00  mov byte ptr [0x8323], 0
37C7  B8 02 00        mov ax, 2
37CA  31 D2           xor dx, dx
37CC  52              push dx
37CD  50              push ax
37CE  A1 FE 82        mov ax, word ptr [0x82fe]
37D1  09 C0           or ax, ax
37D3  79 02           jns 0x37d7
37D5  F7 D8           neg ax
loc_37D7:
37D7  8B D0           mov dx, ax
37D9  A1 FC 82        mov ax, word ptr [0x82fc]
37DC  09 C0           or ax, ax
37DE  79 02           jns 0x37e2
37E0  F7 D8           neg ax
loc_37E2:
37E2  03 C2           add ax, dx
37E4  99              cdq
37E5  8B C8           mov cx, ax
37E7  8B DA           mov bx, dx
37E9  A1 00 83        mov ax, word ptr [0x8300]
37EC  31 D2           xor dx, dx
37EE  9A 94 02 E4 23  call far 23E4:0294
37F3  52              push dx
37F4  50              push ax
37F5  9A 56 0D 4B 21  call far 214B:0D56
37FA  A3 00 83        mov word ptr [0x8300], ax
37FD  A1 F6 82        mov ax, word ptr [0x82f6]
3800  A3 13 83        mov word ptr [0x8313], ax
3803  A1 00 83        mov ax, word ptr [0x8300]
3806  31 D2           xor dx, dx
3808  8B C8           mov cx, ax
380A  8B DA           mov bx, dx
380C  A1 FE 82        mov ax, word ptr [0x82fe]
380F  99              cdq
3810  9A 79 02 E4 23  call far 23E4:0279
3815  00 06 14 83     add byte ptr [0x8314], al
3819  A1 00 83        mov ax, word ptr [0x8300]
381C  31 D2           xor dx, dx
381E  8B C8           mov cx, ax
3820  8B DA           mov bx, dx
3822  A1 FC 82        mov ax, word ptr [0x82fc]
3825  99              cdq
3826  9A 79 02 E4 23  call far 23E4:0279
382B  00 06 13 83     add byte ptr [0x8313], al
382F  B8 0A 00        mov ax, 0xa
3832  50              push ax
3833  B8 01 00        mov ax, 1
3836  50              push ax
3837  9A A1 1E 4B 21  call far 214B:1EA1
383C  55              push bp
383D  E8 FF FA        call 0x333f
3840  A0 0C 83        mov al, byte ptr [0x830c]
3843  A2 0D 83        mov byte ptr [0x830d], al
3846  89 EC           mov sp, bp
3848  5D              pop bp
3849  CA 08 00        retf 8

; ---- routine 0791:384C  (found by: call)
sub_384C:
384C  55              push bp
384D  89 E5           mov bp, sp
384F  83 EC 04        sub sp, 4
3852  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
3857  76 06           jbe 0x385f
3859  E8 8F 4A        call 0x82eb
385C  E9 B0 02        jmp 0x3b0f
loc_385F:
385F  8B 46 0A        mov ax, word ptr [bp + 0xa]
3862  BA 16 00        mov dx, 0x16
3865  F7 E2           mul dx
3867  8B F8           mov di, ax
3869  8B 85 E8 80     mov ax, word ptr [di - 0x7f18]
386D  89 46 FE        mov word ptr [bp - 2], ax
3870  FF 76 FE        push word ptr [bp - 2]
3873  8B 46 0A        mov ax, word ptr [bp + 0xa]
3876  BA 16 00        mov dx, 0x16
3879  F7 E2           mul dx
387B  8B F8           mov di, ax
387D  81 C7 E8 80     add di, 0x80e8
3881  1E              push ds
3882  57              push di
3883  0E              push cs
3884  E8 31 F6        call 0x2eb8
3887  08 C0           or al, al
3889  74 03           je 0x388e
388B  E9 81 02        jmp 0x3b0f
loc_388E:
388E  C4 7E 06        les di, ptr [bp + 6]
3891  26 8A 45 06     mov al, byte ptr es:[di + 6]
3895  30 E4           xor ah, ah
3897  3B 46 0A        cmp ax, word ptr [bp + 0xa]
389A  75 22           jne 0x38be
389C  E8 7B ED        call 0x261a
389F  40              inc ax
38A0  50              push ax
38A1  C4 7E 06        les di, ptr [bp + 6]
38A4  06              push es
38A5  57              push di
38A6  0E              push cs
38A7  E8 3B F3        call 0x2be5
38AA  98              cwde
38AB  5A              pop dx
38AC  F7 EA           imul dx
38AE  99              cdq
38AF  B9 02 00        mov cx, 2
38B2  F7 F9           idiv cx
38B4  00 46 FF        add byte ptr [bp - 1], al
38B7  C6 06 03 83 00  mov byte ptr [0x8303], 0
38BC  EB 4B           jmp 0x3909
loc_38BE:
38BE  8A 46 FF        mov al, byte ptr [bp - 1]
38C1  98              cwde
38C2  09 C0           or ax, ax
38C4  79 02           jns 0x38c8
38C6  F7 D8           neg ax
loc_38C8:
38C8  3D 19 00        cmp ax, 0x19
38CB  7D 3C           jge 0x3909
38CD  8B 46 0A        mov ax, word ptr [bp + 0xa]
38D0  BA 16 00        mov dx, 0x16
38D3  F7 E2           mul dx
38D5  8B F8           mov di, ax
38D7  8B 85 F5 80     mov ax, word ptr [di - 0x7f0b]
38DB  BA 14 00        mov dx, 0x14
38DE  F7 E2           mul dx
38E0  C4 3E 1B A9     les di, ptr [0xa91b]
38E4  03 F8           add di, ax
38E6  26 8A 45 06     mov al, byte ptr es:[di + 6]
38EA  30 E4           xor ah, ah
38EC  50              push ax
38ED  9A B1 06 4B 21  call far 214B:06B1
38F2  50              push ax
38F3  C4 7E 06        les di, ptr [bp + 6]
38F6  06              push es
38F7  57              push di
38F8  0E              push cs
38F9  E8 E9 F2        call 0x2be5
38FC  98              cwde
38FD  5A              pop dx
38FE  F7 EA           imul dx
3900  99              cdq
3901  B9 04 00        mov cx, 4
3904  F7 F9           idiv cx
3906  00 46 FF        add byte ptr [bp - 1], al
loc_3909:
3909  8B 46 0A        mov ax, word ptr [bp + 0xa]
390C  BA 16 00        mov dx, 0x16
390F  F7 E2           mul dx
3911  8B F8           mov di, ax
3913  C6 85 FA 80 05  mov byte ptr [di - 0x7f06], 5
3918  8A 46 0A        mov al, byte ptr [bp + 0xa]
391B  A2 0C 83        mov byte ptr [0x830c], al
391E  80 3E FA 80 00  cmp byte ptr [0x80fa], 0
3923  74 12           je 0x3937
3925  FF 76 FE        push word ptr [bp - 2]
3928  B8 0B 00        mov ax, 0xb
392B  50              push ax
392C  C4 7E 06        les di, ptr [bp + 6]
392F  06              push es
3930  57              push di
3931  0E              push cs
3932  E8 8C FB        call 0x34c1
3935  EB 10           jmp 0x3947
loc_3937:
3937  FF 76 FE        push word ptr [bp - 2]
393A  B8 06 00        mov ax, 6
393D  50              push ax
393E  C4 7E 06        les di, ptr [bp + 6]
3941  06              push es
3942  57              push di
3943  0E              push cs
3944  E8 7A FB        call 0x34c1
loc_3947:
3947  A1 13 83        mov ax, word ptr [0x8313]
394A  89 46 FE        mov word ptr [bp - 2], ax
394D  C4 7E 06        les di, ptr [bp + 6]
3950  26 8A 45 06     mov al, byte ptr es:[di + 6]
3954  30 E4           xor ah, ah
3956  3B 46 0A        cmp ax, word ptr [bp + 0xa]
3959  74 03           je 0x395e
395B  E9 01 01        jmp 0x3a5f
loc_395E:
395E  83 3E FE 82 00  cmp word ptr [0x82fe], 0
3963  75 03           jne 0x3968
3965  E9 F7 00        jmp 0x3a5f
loc_3968:
3968  B8 03 00        mov ax, 3
396B  50              push ax
396C  9A D0 06 4B 21  call far 214B:06D0
3971  08 C0           or al, al
3973  75 03           jne 0x3978
3975  E9 E7 00        jmp 0x3a5f
loc_3978:
3978  83 3E 00 83 02  cmp word ptr [0x8300], 2
397D  76 0D           jbe 0x398c
397F  A1 00 83        mov ax, word ptr [0x8300]
3982  31 D2           xor dx, dx
3984  B9 03 00        mov cx, 3
3987  F7 F1           div cx
3989  A3 00 83        mov word ptr [0x8300], ax
loc_398C:
398C  A1 F6 82        mov ax, word ptr [0x82f6]
398F  89 46 FE        mov word ptr [bp - 2], ax
3992  9A FA 06 4B 21  call far 214B:06FA
3997  98              cwde
3998  8B F8           mov di, ax
399A  8A 85 20 79     mov al, byte ptr [di + 0x7920]
399E  98              cwde
399F  A3 FC 82        mov word ptr [0x82fc], ax
39A2  83 3E FE 82 00  cmp word ptr [0x82fe], 0
39A7  7F 04           jg 0x39ad
39A9  B0 00           mov al, 0
39AB  EB 02           jmp 0x39af
loc_39AD:
39AD  B0 01           mov al, 1
loc_39AF:
39AF  98              cwde
39B0  8B F8           mov di, ax
39B2  8A 85 20 79     mov al, byte ptr [di + 0x7920]
39B6  98              cwde
39B7  01 06 FE 82     add word ptr [0x82fe], ax
39BB  A1 00 83        mov ax, word ptr [0x8300]
39BE  31 D2           xor dx, dx
39C0  8B C8           mov cx, ax
39C2  8B DA           mov bx, dx
39C4  A1 FE 82        mov ax, word ptr [0x82fe]
39C7  99              cdq
39C8  9A 79 02 E4 23  call far 23E4:0279
39CD  00 46 FF        add byte ptr [bp - 1], al
39D0  A1 00 83        mov ax, word ptr [0x8300]
39D3  31 D2           xor dx, dx
39D5  8B C8           mov cx, ax
39D7  8B DA           mov bx, dx
39D9  A1 FC 82        mov ax, word ptr [0x82fc]
39DC  99              cdq
39DD  9A 79 02 E4 23  call far 23E4:0279
39E2  00 46 FE        add byte ptr [bp - 2], al
39E5  FF 76 FE        push word ptr [bp - 2]
39E8  E8 DF F3        call 0x2dca
39EB  08 C0           or al, al
39ED  75 40           jne 0x3a2f
39EF  B8 0A 00        mov ax, 0xa
39F2  50              push ax
39F3  C4 7E 06        les di, ptr [bp + 6]
39F6  06              push es
39F7  57              push di
39F8  0E              push cs
39F9  E8 80 EE        call 0x287c
39FC  08 C0           or al, al
39FE  74 2F           je 0x3a2f
3A00  8A 46 FE        mov al, byte ptr [bp - 2]
3A03  98              cwde
3A04  09 C0           or ax, ax
3A06  79 02           jns 0x3a0a
3A08  F7 D8           neg ax
loc_3A0A:
3A0A  3D 08 00        cmp ax, 8
3A0D  7E 07           jle 0x3a16
3A0F  31 C0           xor ax, ax
3A11  A3 FC 82        mov word ptr [0x82fc], ax
3A14  EB 19           jmp 0x3a2f
loc_3A16:
3A16  83 3E FE 82 00  cmp word ptr [0x82fe], 0
3A1B  7C 04           jl 0x3a21
3A1D  B0 00           mov al, 0
3A1F  EB 02           jmp 0x3a23
loc_3A21:
3A21  B0 01           mov al, 1
loc_3A23:
3A23  98              cwde
3A24  8B F8           mov di, ax
3A26  8A 85 20 79     mov al, byte ptr [di + 0x7920]
3A2A  98              cwde
3A2B  01 06 FE 82     add word ptr [0x82fe], ax
loc_3A2F:
3A2F  A1 F6 82        mov ax, word ptr [0x82f6]
3A32  89 46 FE        mov word ptr [bp - 2], ax
3A35  A1 00 83        mov ax, word ptr [0x8300]
3A38  31 D2           xor dx, dx
3A3A  8B C8           mov cx, ax
3A3C  8B DA           mov bx, dx
3A3E  A1 FE 82        mov ax, word ptr [0x82fe]
3A41  99              cdq
3A42  9A 79 02 E4 23  call far 23E4:0279
3A47  00 46 FF        add byte ptr [bp - 1], al
3A4A  A1 00 83        mov ax, word ptr [0x8300]
3A4D  31 D2           xor dx, dx
3A4F  8B C8           mov cx, ax
3A51  8B DA           mov bx, dx
3A53  A1 FC 82        mov ax, word ptr [0x82fc]
3A56  99              cdq
3A57  9A 79 02 E4 23  call far 23E4:0279
3A5C  00 46 FE        add byte ptr [bp - 2], al
loc_3A5F:
3A5F  BF F6 82        mov di, 0x82f6
3A62  1E              push ds
3A63  57              push di
3A64  0E              push cs
3A65  E8 F7 48        call 0x835f
3A68  3D 14 00        cmp ax, 0x14
3A6B  77 24           ja 0x3a91
3A6D  A0 0C 83        mov al, byte ptr [0x830c]
3A70  3A 06 0B 83     cmp al, byte ptr [0x830b]
3A74  74 17           je 0x3a8d
3A76  BF F6 82        mov di, 0x82f6
3A79  1E              push ds
3A7A  57              push di
3A7B  0E              push cs
3A7C  E8 E0 48        call 0x835f
3A7F  3D 0A 00        cmp ax, 0xa
3A82  76 09           jbe 0x3a8d
3A84  9A FA 06 4B 21  call far 214B:06FA
3A89  08 C0           or al, al
3A8B  75 04           jne 0x3a91
loc_3A8D:
3A8D  B0 00           mov al, 0
3A8F  EB 02           jmp 0x3a93
loc_3A91:
3A91  B0 01           mov al, 1
loc_3A93:
3A93  A2 03 83        mov byte ptr [0x8303], al
3A96  80 3E FA 80 00  cmp byte ptr [0x80fa], 0
3A9B  75 72           jne 0x3b0f
3A9D  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
3AA2  75 12           jne 0x3ab6
3AA4  9A FA 06 4B 21  call far 214B:06FA
3AA9  98              cwde
3AAA  8B F8           mov di, ax
3AAC  8A 85 86 07     mov al, byte ptr [di + 0x786]
3AB0  50              push ax
3AB1  E8 EF EF        call 0x2aa3
3AB4  EB 59           jmp 0x3b0f
loc_3AB6:
3AB6  A0 0C 83        mov al, byte ptr [0x830c]
3AB9  3A 06 0B 83     cmp al, byte ptr [0x830b]
3ABD  75 13           jne 0x3ad2
3ABF  FF 76 FE        push word ptr [bp - 2]
3AC2  E8 05 F3        call 0x2dca
3AC5  98              cwde
3AC6  8B F8           mov di, ax
3AC8  8A 85 88 07     mov al, byte ptr [di + 0x788]
3ACC  50              push ax
3ACD  E8 D3 EF        call 0x2aa3
3AD0  EB 3D           jmp 0x3b0f
loc_3AD2:
3AD2  80 3E 27 83 08  cmp byte ptr [0x8327], 8
3AD7  75 08           jne 0x3ae1
3AD9  B0 03           mov al, 3
3ADB  50              push ax
3ADC  E8 C4 EF        call 0x2aa3
3ADF  EB 2E           jmp 0x3b0f
loc_3AE1:
3AE1  80 3E 03 83 00  cmp byte ptr [0x8303], 0
3AE6  74 0D           je 0x3af5
3AE8  B0 0A           mov al, 0xa
3AEA  50              push ax
3AEB  E8 B5 EF        call 0x2aa3
3AEE  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3AF3  EB 1A           jmp 0x3b0f
loc_3AF5:
3AF5  80 3E 27 83 07  cmp byte ptr [0x8327], 7
3AFA  75 0D           jne 0x3b09
3AFC  B0 09           mov al, 9
3AFE  50              push ax
3AFF  E8 A1 EF        call 0x2aa3
3B02  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3B07  EB 06           jmp 0x3b0f
loc_3B09:
3B09  B0 08           mov al, 8
3B0B  50              push ax
3B0C  E8 94 EF        call 0x2aa3
loc_3B0F:
3B0F  89 EC           mov sp, bp
3B11  5D              pop bp
3B12  CA 06 00        retf 6

; ---- routine 0791:3B15  (found by: call)
sub_3B15:
3B15  55              push bp
3B16  89 E5           mov bp, sp
3B18  83 EC 02        sub sp, 2
3B1B  A1 F6 82        mov ax, word ptr [0x82f6]
3B1E  89 46 FE        mov word ptr [bp - 2], ax
3B21  B8 1E 00        mov ax, 0x1e
3B24  31 D2           xor dx, dx
3B26  52              push dx
3B27  50              push ax
3B28  B8 02 00        mov ax, 2
3B2B  50              push ax
3B2C  C4 7E 06        les di, ptr [bp + 6]
3B2F  06              push es
3B30  57              push di
3B31  0E              push cs
3B32  E8 55 EC        call 0x278a
3B35  31 D2           xor dx, dx
3B37  B9 04 00        mov cx, 4
3B3A  F7 F1           div cx
3B3C  50              push ax
3B3D  9A B1 06 4B 21  call far 214B:06B1
3B42  99              cdq
3B43  52              push dx
3B44  50              push ax
3B45  9A 56 0D 4B 21  call far 214B:0D56
3B4A  52              push dx
3B4B  50              push ax
3B4C  C4 7E 06        les di, ptr [bp + 6]
3B4F  06              push es
3B50  57              push di
3B51  0E              push cs
3B52  E8 90 F0        call 0x2be5
3B55  98              cwde
3B56  99              cdq
3B57  59              pop cx
3B58  5B              pop bx
3B59  9A 79 02 E4 23  call far 23E4:0279
3B5E  00 46 FF        add byte ptr [bp - 1], al
3B61  C6 06 0C 83 FF  mov byte ptr [0x830c], 0xff
3B66  FF 76 FE        push word ptr [bp - 2]
3B69  B8 0A 00        mov ax, 0xa
3B6C  50              push ax
3B6D  C4 7E 06        les di, ptr [bp + 6]
3B70  06              push es
3B71  57              push di
3B72  0E              push cs
3B73  E8 4B F9        call 0x34c1
3B76  C6 06 03 83 01  mov byte ptr [0x8303], 1
3B7B  80 3E 0C 83 00  cmp byte ptr [0x830c], 0
3B80  74 04           je 0x3b86
3B82  B0 00           mov al, 0
3B84  EB 02           jmp 0x3b88
loc_3B86:
3B86  B0 01           mov al, 1
loc_3B88:
3B88  98              cwde
3B89  8B F8           mov di, ax
3B8B  8A 85 8A 07     mov al, byte ptr [di + 0x78a]
3B8F  50              push ax
3B90  E8 10 EF        call 0x2aa3
3B93  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3B98  89 EC           mov sp, bp
3B9A  5D              pop bp
3B9B  CA 04 00        retf 4

; ---- routine 0791:3B9E  (found by: call)
sub_3B9E:
3B9E  55              push bp
3B9F  89 E5           mov bp, sp
3BA1  8A 46 0A        mov al, byte ptr [bp + 0xa]
3BA4  A2 0C 83        mov byte ptr [0x830c], al
3BA7  8B 46 0A        mov ax, word ptr [bp + 0xa]
3BAA  BA 16 00        mov dx, 0x16
3BAD  F7 E2           mul dx
3BAF  8B F8           mov di, ax
3BB1  FF B5 E8 80     push word ptr [di - 0x7f18]
3BB5  C4 7E 06        les di, ptr [bp + 6]
3BB8  06              push es
3BB9  57              push di
3BBA  0E              push cs
3BBB  E8 96 F0        call 0x2c54
3BBE  98              cwde
3BBF  8B F8           mov di, ax
3BC1  8A 85 8C 07     mov al, byte ptr [di + 0x78c]
3BC5  30 E4           xor ah, ah
3BC7  50              push ax
3BC8  C4 7E 06        les di, ptr [bp + 6]
3BCB  06              push es
3BCC  57              push di
3BCD  0E              push cs
3BCE  E8 F0 F8        call 0x34c1
3BD1  B0 03           mov al, 3
3BD3  50              push ax
3BD4  E8 CC EE        call 0x2aa3
3BD7  9A FA 06 4B 21  call far 214B:06FA
3BDC  A2 03 83        mov byte ptr [0x8303], al
3BDF  C4 7E 06        les di, ptr [bp + 6]
3BE2  06              push es
3BE3  57              push di
3BE4  0E              push cs
3BE5  E8 57 11        call 0x4d3f
3BE8  89 EC           mov sp, bp
3BEA  5D              pop bp
3BEB  CA 06 00        retf 6

; ---- routine 0791:3BEE  (found by: call)
sub_3BEE:
3BEE  55              push bp
3BEF  89 E5           mov bp, sp
3BF1  80 3E 0E 83 00  cmp byte ptr [0x830e], 0
3BF6  76 05           jbe 0x3bfd
3BF8  E8 F0 46        call 0x82eb
3BFB  EB 1D           jmp 0x3c1a
loc_3BFD:
3BFD  9A FA 06 4B 21  call far 214B:06FA
3C02  08 C0           or al, al
3C04  74 0B           je 0x3c11
3C06  C4 7E 06        les di, ptr [bp + 6]
3C09  06              push es
3C0A  57              push di
3C0B  0E              push cs
3C0C  E8 06 FF        call 0x3b15
3C0F  EB 09           jmp 0x3c1a
loc_3C11:
3C11  C4 7E 06        les di, ptr [bp + 6]
3C14  06              push es
3C15  57              push di
3C16  0E              push cs
3C17  E8 09 F7        call 0x3323
loc_3C1A:
3C1A  89 EC           mov sp, bp
3C1C  5D              pop bp
3C1D  CA 04 00        retf 4

; ---- routine 0791:3C20  (found by: call)
sub_3C20:
3C20  55              push bp
3C21  89 E5           mov bp, sp
3C23  80 3E 26 83 00  cmp byte ptr [0x8326], 0
3C28  75 0F           jne 0x3c39
3C2A  8A 46 04        mov al, byte ptr [bp + 4]
3C2D  98              cwde
3C2E  BA 0A 00        mov dx, 0xa
3C31  F7 E2           mul dx
3C33  8B F8           mov di, ax
3C35  FE 85 82 7B     inc byte ptr [di + 0x7b82]
loc_3C39:
3C39  89 EC           mov sp, bp
3C3B  5D              pop bp
3C3C  C2 02 00        ret 2

; ---- routine 0791:3C3F  (found by: call)
sub_3C3F:
3C3F  55              push bp
3C40  89 E5           mov bp, sp
3C42  C6 06 0C 83 00  mov byte ptr [0x830c], 0
3C47  83 7E 0A 02     cmp word ptr [bp + 0xa], 2
3C4B  74 16           je 0x3c63
3C4D  9A FA 06 4B 21  call far 214B:06FA
3C52  30 E4           xor ah, ah
3C54  50              push ax
3C55  9A FA 06 4B 21  call far 214B:06FA
3C5A  30 E4           xor ah, ah
3C5C  5A              pop dx
3C5D  2B C2           sub ax, dx
3C5F  00 06 F6 82     add byte ptr [0x82f6], al
loc_3C63:
3C63  80 3E 24 83 00  cmp byte ptr [0x8324], 0
3C68  75 37           jne 0x3ca1
3C6A  83 7E 0A 02     cmp word ptr [bp + 0xa], 2
3C6E  74 04           je 0x3c74
3C70  B0 00           mov al, 0
3C72  EB 02           jmp 0x3c76
loc_3C74:
3C74  B0 01           mov al, 1
loc_3C76:
3C76  98              cwde
3C77  8B F8           mov di, ax
3C79  8A 85 8E 07     mov al, byte ptr [di + 0x78e]
3C7D  30 E4           xor ah, ah
3C7F  50              push ax
3C80  C4 7E 06        les di, ptr [bp + 6]
3C83  06              push es
3C84  57              push di
3C85  0E              push cs
3C86  E8 F3 EB        call 0x287c
3C89  08 C0           or al, al
3C8B  75 18           jne 0x3ca5
3C8D  B8 04 00        mov ax, 4
3C90  50              push ax
3C91  9A D0 06 4B 21  call far 214B:06D0
3C96  08 C0           or al, al
3C98  75 0B           jne 0x3ca5
3C9A  E8 16 ED        call 0x29b3
3C9D  08 C0           or al, al
3C9F  75 04           jne 0x3ca5
loc_3CA1:
3CA1  B0 00           mov al, 0
3CA3  EB 02           jmp 0x3ca7
loc_3CA5:
3CA5  B0 01           mov al, 1
loc_3CA7:
3CA7  A2 FB 80        mov byte ptr [0x80fb], al
3CAA  FF 36 46 06     push word ptr [0x646]
3CAE  C4 7E 06        les di, ptr [bp + 6]
3CB1  06              push es
3CB2  57              push di
3CB3  0E              push cs
3CB4  E8 CF EF        call 0x2c86
3CB7  50              push ax
3CB8  FF 76 0A        push word ptr [bp + 0xa]
3CBB  C4 7E 06        les di, ptr [bp + 6]
3CBE  06              push es
3CBF  57              push di
3CC0  0E              push cs
3CC1  E8 FD F7        call 0x34c1
3CC4  8A 46 0C        mov al, byte ptr [bp + 0xc]
3CC7  50              push ax
3CC8  E8 D8 ED        call 0x2aa3
3CCB  80 3E 26 83 00  cmp byte ptr [0x8326], 0
3CD0  75 15           jne 0x3ce7
3CD2  C4 7E 06        les di, ptr [bp + 6]
3CD5  06              push es
3CD6  57              push di
3CD7  0E              push cs
3CD8  E8 99 EC        call 0x2974
3CDB  98              cwde
3CDC  BA 0A 00        mov dx, 0xa
3CDF  F7 E2           mul dx
3CE1  8B F8           mov di, ax
3CE3  FE 85 81 7B     inc byte ptr [di + 0x7b81]
loc_3CE7:
3CE7  83 7E 0A 02     cmp word ptr [bp + 0xa], 2
3CEB  74 20           je 0x3d0d
3CED  9A FA 06 4B 21  call far 214B:06FA
3CF2  08 C0           or al, al
3CF4  74 06           je 0x3cfc
3CF6  83 7E 0A 04     cmp word ptr [bp + 0xa], 4
3CFA  74 11           je 0x3d0d
loc_3CFC:
3CFC  B8 03 00        mov ax, 3
3CFF  50              push ax
3D00  9A D0 06 4B 21  call far 214B:06D0
3D05  08 C0           or al, al
3D07  75 04           jne 0x3d0d
3D09  B0 00           mov al, 0
3D0B  EB 02           jmp 0x3d0f
loc_3D0D:
3D0D  B0 01           mov al, 1
loc_3D0F:
3D0F  A2 03 83        mov byte ptr [0x8303], al
3D12  89 EC           mov sp, bp
3D14  5D              pop bp
3D15  CA 08 00        retf 8
; data (not reached as code), 32 bytes
3D18                  db 04 10 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
3D28                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

