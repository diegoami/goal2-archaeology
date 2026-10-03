; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 5 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:3041  (found by: call, far)
sub_3041:
3041  55              push bp
3042  89 E5           mov bp, sp
3044  83 EC 06        sub sp, 6
3047  8B 46 06        mov ax, word ptr [bp + 6]
304A  BA 14 00        mov dx, 0x14
304D  F7 E2           mul dx
304F  C4 3E 1B A9     les di, ptr [0xa91b]
3053  03 F8           add di, ax
3055  89 7E FB        mov word ptr [bp - 5], di
3058  8C 46 FD        mov word ptr [bp - 3], es
305B  C4 7E FB        les di, ptr [bp - 5]
305E  26 8A 45 05     mov al, byte ptr es:[di + 5]
3062  30 E4           xor ah, ah
3064  8B D0           mov dx, ax
3066  C4 7E FB        les di, ptr [bp - 5]
3069  26 8A 45 02     mov al, byte ptr es:[di + 2]
306D  30 E4           xor ah, ah
306F  03 C2           add ax, dx
3071  3D 1E 00        cmp ax, 0x1e
3074  74 04           je 0x307a
3076  B0 00           mov al, 0
3078  EB 02           jmp 0x307c
loc_307A:
307A  B0 01           mov al, 1
loc_307C:
307C  88 46 FF        mov byte ptr [bp - 1], al
307F  8A 46 FF        mov al, byte ptr [bp - 1]
3082  89 EC           mov sp, bp
3084  5D              pop bp
3085  CA 02 00        retf 2

; ---- routine 1771:3088  (found by: call, far)
sub_3088:
3088  55              push bp
3089  89 E5           mov bp, sp
308B  83 EC 06        sub sp, 6
308E  8B 46 06        mov ax, word ptr [bp + 6]
3091  BA 14 00        mov dx, 0x14
3094  F7 E2           mul dx
3096  C4 3E 1B A9     les di, ptr [0xa91b]
309A  03 F8           add di, ax
309C  89 7E FB        mov word ptr [bp - 5], di
309F  8C 46 FD        mov word ptr [bp - 3], es
30A2  C4 7E FB        les di, ptr [bp - 5]
30A5  26 8A 45 07     mov al, byte ptr es:[di + 7]
30A9  30 E4           xor ah, ah
30AB  8B D8           mov bx, ax
30AD  8B 46 06        mov ax, word ptr [bp + 6]
30B0  31 D2           xor dx, dx
30B2  B9 03 00        mov cx, 3
30B5  F7 F1           div cx
30B7  92              xchg dx, ax
30B8  8B F8           mov di, ax
30BA  8A 85 7C 0E     mov al, byte ptr [di + 0xe7c]
30BE  30 E4           xor ah, ah
30C0  BA 0E 00        mov dx, 0xe
30C3  F7 E2           mul dx
30C5  8B F8           mov di, ax
30C7  03 FB           add di, bx
30C9  8A 85 60 0E     mov al, byte ptr [di + 0xe60]
30CD  88 46 FF        mov byte ptr [bp - 1], al
30D0  8A 46 FF        mov al, byte ptr [bp - 1]
30D3  89 EC           mov sp, bp
30D5  5D              pop bp
30D6  CA 02 00        retf 2

; ---- routine 1771:30D9  (found by: call, far)
sub_30D9:
30D9  55              push bp
30DA  89 E5           mov bp, sp
30DC  83 EC 08        sub sp, 8
30DF  8B 46 06        mov ax, word ptr [bp + 6]
30E2  BA 14 00        mov dx, 0x14
30E5  F7 E2           mul dx
30E7  C4 3E 1B A9     les di, ptr [0xa91b]
30EB  03 F8           add di, ax
30ED  89 7E F8        mov word ptr [bp - 8], di
30F0  8C 46 FA        mov word ptr [bp - 6], es
30F3  C4 7E F8        les di, ptr [bp - 8]
30F6  26 8A 45 05     mov al, byte ptr es:[di + 5]
30FA  30 E4           xor ah, ah
30FC  8B D0           mov dx, ax
30FE  C4 7E F8        les di, ptr [bp - 8]
3101  26 8A 45 03     mov al, byte ptr es:[di + 3]
3105  30 E4           xor ah, ah
3107  2B C2           sub ax, dx
3109  99              cdq
310A  B9 08 00        mov cx, 8
310D  F7 F9           idiv cx
310F  92              xchg dx, ax
3110  89 46 FC        mov word ptr [bp - 4], ax
3113  C4 7E F8        les di, ptr [bp - 8]
3116  26 80 7D 01 15  cmp byte ptr es:[di + 1], 0x15
311B  73 0D           jae 0x312a
311D  8B 46 FC        mov ax, word ptr [bp - 4]
3120  31 D2           xor dx, dx
3122  B9 02 00        mov cx, 2
3125  F7 F1           div cx
3127  89 46 FC        mov word ptr [bp - 4], ax
loc_312A:
312A  8B 46 FC        mov ax, word ptr [bp - 4]
312D  89 46 FE        mov word ptr [bp - 2], ax
3130  8B 46 FE        mov ax, word ptr [bp - 2]
3133  89 EC           mov sp, bp
3135  5D              pop bp
3136  CA 02 00        retf 2
; data (not reached as code), 64 bytes
3139                  db 88 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
3149                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
3159                  db 10 09 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
3169                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:3179  (found by: call, far)
sub_3179:
3179  55              push bp
317A  89 E5           mov bp, sp
317C  83 EC 06        sub sp, 6
317F  8B 46 06        mov ax, word ptr [bp + 6]
3182  BA 14 00        mov dx, 0x14
3185  F7 E2           mul dx
3187  C4 3E 1B A9     les di, ptr [0xa91b]
318B  03 F8           add di, ax
318D  89 7E FA        mov word ptr [bp - 6], di
3190  8C 46 FC        mov word ptr [bp - 4], es
3193  FF 76 06        push word ptr [bp + 6]
3196  0E              push cs
3197  E8 EE FE        call 0x3088
319A  88 46 FE        mov byte ptr [bp - 2], al
319D  FF 76 06        push word ptr [bp + 6]
31A0  0E              push cs
31A1  E8 9D FE        call 0x3041
31A4  08 C0           or al, al
31A6  75 1A           jne 0x31c2
31A8  80 7E FE 00     cmp byte ptr [bp - 2], 0
31AC  74 14           je 0x31c2
31AE  C4 7E FA        les di, ptr [bp - 6]
31B1  26 8A 45 06     mov al, byte ptr es:[di + 6]
31B5  50              push ax
31B6  BF 39 31        mov di, 0x3139
31B9  0E              push cs
31BA  57              push di
31BB  9A DF 08 E4 23  call far 23E4:08DF
31C0  75 46           jne 0x3208
loc_31C2:
31C2  80 7E FE 00     cmp byte ptr [bp - 2], 0
31C6  75 14           jne 0x31dc
31C8  C4 7E FA        les di, ptr [bp - 6]
31CB  26 8A 45 06     mov al, byte ptr es:[di + 6]
31CF  50              push ax
31D0  BF 59 31        mov di, 0x3159
31D3  0E              push cs
31D4  57              push di
31D5  9A DF 08 E4 23  call far 23E4:08DF
31DA  75 2C           jne 0x3208
loc_31DC:
31DC  C4 7E FA        les di, ptr [bp - 6]
31DF  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
31E4  75 0A           jne 0x31f0
31E6  C4 7E FA        les di, ptr [bp - 6]
31E9  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
31EE  75 18           jne 0x3208
loc_31F0:
31F0  C4 7E FA        les di, ptr [bp - 6]
31F3  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
31F8  75 0A           jne 0x3204
31FA  C4 7E FA        les di, ptr [bp - 6]
31FD  26 80 7D 06 00  cmp byte ptr es:[di + 6], 0
3202  75 04           jne 0x3208
loc_3204:
3204  B0 00           mov al, 0
3206  EB 02           jmp 0x320a
loc_3208:
3208  B0 01           mov al, 1
loc_320A:
320A  88 46 FF        mov byte ptr [bp - 1], al
320D  8A 46 FF        mov al, byte ptr [bp - 1]
3210  89 EC           mov sp, bp
3212  5D              pop bp
3213  CA 02 00        retf 2

; ---- routine 1771:3216  (found by: call, far)
sub_3216:
3216  55              push bp
3217  89 E5           mov bp, sp
3219  83 EC 06        sub sp, 6
321C  8B 46 06        mov ax, word ptr [bp + 6]
321F  BA 14 00        mov dx, 0x14
3222  F7 E2           mul dx
3224  C4 3E 1B A9     les di, ptr [0xa91b]
3228  03 F8           add di, ax
322A  89 7E FB        mov word ptr [bp - 5], di
322D  8C 46 FD        mov word ptr [bp - 3], es
3230  C4 7E FB        les di, ptr [bp - 5]
3233  26 80 7D 0E 01  cmp byte ptr es:[di + 0xe], 1
3238  7C 49           jl 0x3283
323A  B8 08 00        mov ax, 8
323D  50              push ax
323E  C4 7E FB        les di, ptr [bp - 5]
3241  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
3245  30 E4           xor ah, ah
3247  50              push ax
3248  9A 57 0C 4B 21  call far 214B:0C57
324D  08 C0           or al, al
324F  75 32           jne 0x3283
3251  B8 06 00        mov ax, 6
3254  50              push ax
3255  C4 7E FB        les di, ptr [bp - 5]
3258  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
325C  30 E4           xor ah, ah
325E  50              push ax
325F  9A 57 0C 4B 21  call far 214B:0C57
3264  08 C0           or al, al
3266  75 1B           jne 0x3283
3268  B8 03 00        mov ax, 3
326B  50              push ax
326C  C4 7E FB        les di, ptr [bp - 5]
326F  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
3273  30 E4           xor ah, ah
3275  50              push ax
3276  9A 57 0C 4B 21  call far 214B:0C57
327B  08 C0           or al, al
327D  75 04           jne 0x3283
327F  B0 00           mov al, 0
3281  EB 02           jmp 0x3285
loc_3283:
3283  B0 01           mov al, 1
loc_3285:
3285  88 46 FF        mov byte ptr [bp - 1], al
3288  8A 46 FF        mov al, byte ptr [bp - 1]
328B  89 EC           mov sp, bp
328D  5D              pop bp
328E  CA 02 00        retf 2

; ---- routine 1771:3291  (found by: call)
sub_3291:
3291  55              push bp
3292  89 E5           mov bp, sp
3294  83 EC 04        sub sp, 4
3297  8B 46 04        mov ax, word ptr [bp + 4]
329A  BA 14 00        mov dx, 0x14
329D  F7 E2           mul dx
329F  C4 3E 1B A9     les di, ptr [0xa91b]
32A3  03 F8           add di, ax
32A5  89 7E FC        mov word ptr [bp - 4], di
32A8  8C 46 FE        mov word ptr [bp - 2], es
32AB  B8 03 00        mov ax, 3
32AE  50              push ax
32AF  9A B1 06 4B 21  call far 214B:06B1
32B4  50              push ax
32B5  B8 03 00        mov ax, 3
32B8  50              push ax
32B9  9A B1 06 4B 21  call far 214B:06B1
32BE  8B D0           mov dx, ax
32C0  C4 7E FC        les di, ptr [bp - 4]
32C3  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
32C8  74 04           je 0x32ce
32CA  B0 00           mov al, 0
32CC  EB 02           jmp 0x32d0
loc_32CE:
32CE  B0 01           mov al, 1
loc_32D0:
32D0  98              cwde
32D1  8B F8           mov di, ax
32D3  8A 85 80 0E     mov al, byte ptr [di + 0xe80]
32D7  30 E4           xor ah, ah
32D9  03 C2           add ax, dx
32DB  5A              pop dx
32DC  2B C2           sub ax, dx
32DE  C4 7E FC        les di, ptr [bp - 4]
32E1  26 88 45 02     mov byte ptr es:[di + 2], al
32E5  89 EC           mov sp, bp
32E7  5D              pop bp
32E8  C2 02 00        ret 2

; ---- routine 1771:32EB  (found by: call, far)
sub_32EB:
32EB  55              push bp
32EC  89 E5           mov bp, sp
32EE  83 EC 08        sub sp, 8
32F1  8B 46 06        mov ax, word ptr [bp + 6]
32F4  BA 14 00        mov dx, 0x14
32F7  F7 E2           mul dx
32F9  C4 3E 1B A9     les di, ptr [0xa91b]
32FD  03 F8           add di, ax
32FF  89 7E F8        mov word ptr [bp - 8], di
3302  8C 46 FA        mov word ptr [bp - 6], es
3305  C4 7E F8        les di, ptr [bp - 8]
3308  26 8A 45 01     mov al, byte ptr es:[di + 1]
330C  C4 7E F8        les di, ptr [bp - 8]
330F  26 3A 45 02     cmp al, byte ptr es:[di + 2]
3313  72 2C           jb 0x3341
3315  C4 7E F8        les di, ptr [bp - 8]
3318  26 8A 45 02     mov al, byte ptr es:[di + 2]
331C  30 E4           xor ah, ah
331E  05 03 00        add ax, 3
3321  8B D0           mov dx, ax
3323  C4 7E F8        les di, ptr [bp - 8]
3326  26 8A 45 01     mov al, byte ptr es:[di + 1]
332A  30 E4           xor ah, ah
332C  3B C2           cmp ax, dx
332E  7F 11           jg 0x3341
3330  C4 7E F8        les di, ptr [bp - 8]
3333  26 8A 45 03     mov al, byte ptr es:[di + 3]
3337  C4 7E F8        les di, ptr [bp - 8]
333A  26 88 45 04     mov byte ptr es:[di + 4], al
333E  E9 86 00        jmp 0x33c7
loc_3341:
3341  C4 7E F8        les di, ptr [bp - 8]
3344  26 8A 45 03     mov al, byte ptr es:[di + 3]
3348  30 E4           xor ah, ah
334A  89 46 FC        mov word ptr [bp - 4], ax
334D  C4 7E F8        les di, ptr [bp - 8]
3350  26 8A 45 02     mov al, byte ptr es:[di + 2]
3354  30 E4           xor ah, ah
3356  05 03 00        add ax, 3
3359  8B D0           mov dx, ax
335B  C4 7E F8        les di, ptr [bp - 8]
335E  26 8A 45 01     mov al, byte ptr es:[di + 1]
3362  30 E4           xor ah, ah
3364  3B C2           cmp ax, dx
3366  7E 25           jle 0x338d
3368  C4 7E F8        les di, ptr [bp - 8]
336B  26 8A 45 02     mov al, byte ptr es:[di + 2]
336F  30 E4           xor ah, ah
3371  05 03 00        add ax, 3
3374  8B D0           mov dx, ax
3376  C4 7E F8        les di, ptr [bp - 8]
3379  26 8A 45 01     mov al, byte ptr es:[di + 1]
337D  30 E4           xor ah, ah
337F  2B C2           sub ax, dx
3381  8B D0           mov dx, ax
3383  B8 10 00        mov ax, 0x10
3386  2B C2           sub ax, dx
3388  89 46 FE        mov word ptr [bp - 2], ax
338B  EB 26           jmp 0x33b3
loc_338D:
338D  C4 7E F8        les di, ptr [bp - 8]
3390  26 8A 45 01     mov al, byte ptr es:[di + 1]
3394  30 E4           xor ah, ah
3396  8B D0           mov dx, ax
3398  C4 7E F8        les di, ptr [bp - 8]
339B  26 8A 45 02     mov al, byte ptr es:[di + 2]
339F  30 E4           xor ah, ah
33A1  2B C2           sub ax, dx
33A3  99              cdq
33A4  B9 02 00        mov cx, 2
33A7  F7 F9           idiv cx
33A9  8B D0           mov dx, ax
33AB  B8 10 00        mov ax, 0x10
33AE  2B C2           sub ax, dx
33B0  89 46 FE        mov word ptr [bp - 2], ax
loc_33B3:
33B3  8B 46 FC        mov ax, word ptr [bp - 4]
33B6  F7 66 FE        mul word ptr [bp - 2]
33B9  31 D2           xor dx, dx
33BB  B9 10 00        mov cx, 0x10
33BE  F7 F1           div cx
33C0  C4 7E F8        les di, ptr [bp - 8]
33C3  26 88 45 04     mov byte ptr es:[di + 4], al
loc_33C7:
33C7  89 EC           mov sp, bp
33C9  5D              pop bp
33CA  CA 02 00        retf 2

; ---- routine 1771:33CD  (found by: call, far)
sub_33CD:
33CD  55              push bp
33CE  89 E5           mov bp, sp
33D0  83 EC 04        sub sp, 4
33D3  8B 46 06        mov ax, word ptr [bp + 6]
33D6  BA 14 00        mov dx, 0x14
33D9  F7 E2           mul dx
33DB  C4 3E 1B A9     les di, ptr [0xa91b]
33DF  03 F8           add di, ax
33E1  89 7E FC        mov word ptr [bp - 4], di
33E4  8C 46 FE        mov word ptr [bp - 2], es
33E7  B8 08 00        mov ax, 8
33EA  50              push ax
33EB  C4 7E FC        les di, ptr [bp - 4]
33EE  81 C7 0F 00     add di, 0xf
33F2  06              push es
33F3  57              push di
33F4  9A 79 0C 4B 21  call far 214B:0C79
33F9  B8 04 00        mov ax, 4
33FC  50              push ax
33FD  C4 7E FC        les di, ptr [bp - 4]
3400  81 C7 0F 00     add di, 0xf
3404  06              push es
3405  57              push di
3406  9A A1 0C 4B 21  call far 214B:0CA1
340B  89 EC           mov sp, bp
340D  5D              pop bp
340E  CA 02 00        retf 2
; data (not reached as code), 32 bytes
3411                  db 1B 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
3421                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:3431  (found by: call, far)
sub_3431:
3431  55              push bp
3432  89 E5           mov bp, sp
3434  83 EC 04        sub sp, 4
3437  8B 46 06        mov ax, word ptr [bp + 6]
343A  BA 14 00        mov dx, 0x14
343D  F7 E2           mul dx
343F  C4 3E 1B A9     les di, ptr [0xa91b]
3443  03 F8           add di, ax
3445  89 7E FC        mov word ptr [bp - 4], di
3448  8C 46 FE        mov word ptr [bp - 2], es
344B  FF 76 06        push word ptr [bp + 6]
344E  0E              push cs
344F  E8 A9 FB        call 0x2ffb
3452  3C 04           cmp al, 4
3454  73 07           jae 0x345d
3456  FF 76 06        push word ptr [bp + 6]
3459  0E              push cs
345A  E8 70 FF        call 0x33cd
loc_345D:
345D  C4 7E FC        les di, ptr [bp - 4]
3460  26 8A 45 06     mov al, byte ptr es:[di + 6]
3464  50              push ax
3465  BF 11 34        mov di, 0x3411
3468  0E              push cs
3469  57              push di
346A  9A DF 08 E4 23  call far 23E4:08DF
346F  74 26           je 0x3497
3471  B8 05 00        mov ax, 5
3474  50              push ax
3475  C4 7E FC        les di, ptr [bp - 4]
3478  81 C7 0F 00     add di, 0xf
347C  06              push es
347D  57              push di
347E  9A 79 0C 4B 21  call far 214B:0C79
3483  B8 01 00        mov ax, 1
3486  50              push ax
3487  C4 7E FC        les di, ptr [bp - 4]
348A  81 C7 0F 00     add di, 0xf
348E  06              push es
348F  57              push di
3490  9A 79 0C 4B 21  call far 214B:0C79
3495  EB 4A           jmp 0x34e1
loc_3497:
3497  C4 7E FC        les di, ptr [bp - 4]
349A  26 80 7D 06 02  cmp byte ptr es:[di + 6], 2
349F  75 40           jne 0x34e1
34A1  C4 7E FC        les di, ptr [bp - 4]
34A4  26 80 7D 05 0E  cmp byte ptr es:[di + 5], 0xe
34A9  73 12           jae 0x34bd
34AB  B8 05 00        mov ax, 5
34AE  50              push ax
34AF  C4 7E FC        les di, ptr [bp - 4]
34B2  81 C7 0F 00     add di, 0xf
34B6  06              push es
34B7  57              push di
34B8  9A 79 0C 4B 21  call far 214B:0C79
loc_34BD:
34BD  B8 06 00        mov ax, 6
34C0  50              push ax
34C1  C4 7E FC        les di, ptr [bp - 4]
34C4  81 C7 0F 00     add di, 0xf
34C8  06              push es
34C9  57              push di
34CA  9A 79 0C 4B 21  call far 214B:0C79
34CF  B8 02 00        mov ax, 2
34D2  50              push ax
34D3  C4 7E FC        les di, ptr [bp - 4]
34D6  81 C7 0F 00     add di, 0xf
34DA  06              push es
34DB  57              push di
34DC  9A 79 0C 4B 21  call far 214B:0C79
loc_34E1:
34E1  89 EC           mov sp, bp
34E3  5D              pop bp
34E4  CA 02 00        retf 2

; ---- routine 1771:34E7  (found by: far)
sub_34E7:
34E7  55              push bp
34E8  89 E5           mov bp, sp
34EA  83 EC 06        sub sp, 6
34ED  8B 46 06        mov ax, word ptr [bp + 6]
34F0  BA BF 00        mov dx, 0xbf
34F3  F7 E2           mul dx
34F5  C4 3E 17 A9     les di, ptr [0xa917]
34F9  03 F8           add di, ax
34FB  89 7E FA        mov word ptr [bp - 6], di
34FE  8C 46 FC        mov word ptr [bp - 4], es
3501  C7 46 FE 01 00  mov word ptr [bp - 2], 1
3506  EB 03           jmp 0x350b
loc_3508:
3508  FF 46 FE        inc word ptr [bp - 2]
loc_350B:
350B  8B 46 FE        mov ax, word ptr [bp - 2]
350E  D1 E0           shl ax, 1
3510  C4 7E FA        les di, ptr [bp - 6]
3513  03 F8           add di, ax
3515  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
351A  74 30           je 0x354c
351C  8B 46 FE        mov ax, word ptr [bp - 2]
351F  D1 E0           shl ax, 1
3521  C4 7E FA        les di, ptr [bp - 6]
3524  03 F8           add di, ax
3526  26 8B 45 FE     mov ax, word ptr es:[di - 2]
352A  BA 14 00        mov dx, 0x14
352D  F7 E2           mul dx
352F  C4 3E 1B A9     les di, ptr [0xa91b]
3533  03 F8           add di, ax
3535  26 C6 45 0F 00  mov byte ptr es:[di + 0xf], 0
353A  8B 46 FE        mov ax, word ptr [bp - 2]
353D  D1 E0           shl ax, 1
353F  C4 7E FA        les di, ptr [bp - 6]
3542  03 F8           add di, ax
3544  26 FF 75 FE     push word ptr es:[di - 2]
3548  0E              push cs
3549  E8 E5 FE        call 0x3431
loc_354C:
354C  83 7E FE 14     cmp word ptr [bp - 2], 0x14
3550  75 B6           jne 0x3508
3552  89 EC           mov sp, bp
3554  5D              pop bp
3555  CA 02 00        retf 2

; ---- routine 1771:3558  (found by: call, far)
sub_3558:
3558  55              push bp
3559  89 E5           mov bp, sp
355B  83 EC 06        sub sp, 6
355E  8B 46 06        mov ax, word ptr [bp + 6]
3561  BA 14 00        mov dx, 0x14
3564  F7 E2           mul dx
3566  C4 3E 1B A9     les di, ptr [0xa91b]
356A  03 F8           add di, ax
356C  89 7E FB        mov word ptr [bp - 5], di
356F  8C 46 FD        mov word ptr [bp - 3], es
3572  C4 7E FB        les di, ptr [bp - 5]
3575  26 8A 45 02     mov al, byte ptr es:[di + 2]
3579  30 E4           xor ah, ah
357B  05 04 00        add ax, 4
357E  8B D0           mov dx, ax
3580  C4 7E FB        les di, ptr [bp - 5]
3583  26 8A 45 01     mov al, byte ptr es:[di + 1]
3587  30 E4           xor ah, ah
3589  3B C2           cmp ax, dx
358B  7F 04           jg 0x3591
358D  B0 00           mov al, 0
358F  EB 02           jmp 0x3593
loc_3591:
3591  B0 01           mov al, 1
loc_3593:
3593  88 46 FF        mov byte ptr [bp - 1], al
3596  C4 7E FB        les di, ptr [bp - 5]
3599  26 8A 05        mov al, byte ptr es:[di]
359C  30 E4           xor ah, ah
359E  50              push ax
359F  0E              push cs
35A0  E8 D4 D5        call 0xb77
35A3  08 C0           or al, al
35A5  74 47           je 0x35ee
35A7  8A 46 FF        mov al, byte ptr [bp - 1]
35AA  98              cwde
35AB  8B F8           mov di, ax
35AD  8A 85 82 0E     mov al, byte ptr [di + 0xe82]
35B1  30 E4           xor ah, ah
35B3  40              inc ax
35B4  50              push ax
35B5  9A B1 06 4B 21  call far 214B:06B1
35BA  50              push ax
35BB  8A 46 FF        mov al, byte ptr [bp - 1]
35BE  98              cwde
35BF  8B F8           mov di, ax
35C1  8A 85 82 0E     mov al, byte ptr [di + 0xe82]
35C5  30 E4           xor ah, ah
35C7  B9 03 00        mov cx, 3
35CA  F7 E9           imul cx
35CC  50              push ax
35CD  9A B1 06 4B 21  call far 214B:06B1
35D2  8B D0           mov dx, ax
35D4  8A 46 FF        mov al, byte ptr [bp - 1]
35D7  98              cwde
35D8  8B F8           mov di, ax
35DA  8A 85 82 0E     mov al, byte ptr [di + 0xe82]
35DE  30 E4           xor ah, ah
35E0  03 C2           add ax, dx
35E2  5A              pop dx
35E3  2B C2           sub ax, dx
35E5  C4 7E FB        les di, ptr [bp - 5]
35E8  26 88 45 0D     mov byte ptr es:[di + 0xd], al
35EC  EB 2B           jmp 0x3619
loc_35EE:
35EE  8A 46 FF        mov al, byte ptr [bp - 1]
35F1  98              cwde
35F2  8B F8           mov di, ax
35F4  8A 85 82 0E     mov al, byte ptr [di + 0xe82]
35F8  30 E4           xor ah, ah
35FA  D1 E0           shl ax, 1
35FC  50              push ax
35FD  9A B1 06 4B 21  call far 214B:06B1
3602  8B D0           mov dx, ax
3604  8A 46 FF        mov al, byte ptr [bp - 1]
3607  98              cwde
3608  8B F8           mov di, ax
360A  8A 85 82 0E     mov al, byte ptr [di + 0xe82]
360E  30 E4           xor ah, ah
3610  03 C2           add ax, dx
3612  C4 7E FB        les di, ptr [bp - 5]
3615  26 88 45 0D     mov byte ptr es:[di + 0xd], al
loc_3619:
3619  C4 7E FB        les di, ptr [bp - 5]
361C  26 80 7D 0D 20  cmp byte ptr es:[di + 0xd], 0x20
3621  7E 08           jle 0x362b
3623  C4 7E FB        les di, ptr [bp - 5]
3626  26 C6 45 0D 20  mov byte ptr es:[di + 0xd], 0x20
loc_362B:
362B  C4 7E FB        les di, ptr [bp - 5]
362E  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
3632  C4 7E FB        les di, ptr [bp - 5]
3635  26 88 45 0E     mov byte ptr es:[di + 0xe], al
3639  C4 7E FB        les di, ptr [bp - 5]
363C  26 80 7D 0D 01  cmp byte ptr es:[di + 0xd], 1
3641  7D 08           jge 0x364b
3643  C4 7E FB        les di, ptr [bp - 5]
3646  26 C6 45 0D 01  mov byte ptr es:[di + 0xd], 1
loc_364B:
364B  89 EC           mov sp, bp
364D  5D              pop bp
364E  CA 02 00        retf 2

; ---- routine 1771:3651  (found by: far)
sub_3651:
3651  55              push bp
3652  89 E5           mov bp, sp
3654  83 EC 06        sub sp, 6
3657  8B 46 08        mov ax, word ptr [bp + 8]
365A  BA 14 00        mov dx, 0x14
365D  F7 E2           mul dx
365F  C4 3E 1B A9     les di, ptr [0xa91b]
3663  03 F8           add di, ax
3665  89 7E FA        mov word ptr [bp - 6], di
3668  8C 46 FC        mov word ptr [bp - 4], es
366B  C4 7E FA        les di, ptr [bp - 6]
366E  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
3672  98              cwde
3673  89 46 FE        mov word ptr [bp - 2], ax
3676  C4 7E FA        les di, ptr [bp - 6]
3679  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
367E  75 1D           jne 0x369d
3680  B8 02 00        mov ax, 2
3683  50              push ax
3684  9A B1 06 4B 21  call far 214B:06B1
3689  50              push ax
368A  B8 08 00        mov ax, 8
368D  50              push ax
368E  9A B1 06 4B 21  call far 214B:06B1
3693  F7 D8           neg ax
3695  5A              pop dx
3696  03 C2           add ax, dx
3698  01 46 FE        add word ptr [bp - 2], ax
369B  EB 43           jmp 0x36e0
loc_369D:
369D  80 7E 06 00     cmp byte ptr [bp + 6], 0
36A1  74 1B           je 0x36be
36A3  B8 02 00        mov ax, 2
36A6  50              push ax
36A7  9A B1 06 4B 21  call far 214B:06B1
36AC  50              push ax
36AD  B8 08 00        mov ax, 8
36B0  50              push ax
36B1  9A B1 06 4B 21  call far 214B:06B1
36B6  5A              pop dx
36B7  2B C2           sub ax, dx
36B9  01 46 FE        add word ptr [bp - 2], ax
36BC  EB 22           jmp 0x36e0
loc_36BE:
36BE  B8 03 00        mov ax, 3
36C1  50              push ax
36C2  9A B1 06 4B 21  call far 214B:06B1
36C7  50              push ax
36C8  B8 02 00        mov ax, 2
36CB  50              push ax
36CC  9A B1 06 4B 21  call far 214B:06B1
36D1  5A              pop dx
36D2  2B C2           sub ax, dx
36D4  01 46 FE        add word ptr [bp - 2], ax
36D7  83 7E FE 10     cmp word ptr [bp - 2], 0x10
36DB  7D 03           jge 0x36e0
36DD  FF 46 FE        inc word ptr [bp - 2]
loc_36E0:
36E0  83 7E FE 01     cmp word ptr [bp - 2], 1
36E4  7D 07           jge 0x36ed
36E6  C7 46 FE 01 00  mov word ptr [bp - 2], 1
36EB  EB 5C           jmp 0x3749
loc_36ED:
36ED  C4 7E FA        les di, ptr [bp - 6]
36F0  26 8A 45 02     mov al, byte ptr es:[di + 2]
36F4  30 E4           xor ah, ah
36F6  05 03 00        add ax, 3
36F9  8B D0           mov dx, ax
36FB  C4 7E FA        les di, ptr [bp - 6]
36FE  26 8A 45 01     mov al, byte ptr es:[di + 1]
3702  30 E4           xor ah, ah
3704  3B C2           cmp ax, dx
3706  7F 04           jg 0x370c
3708  B0 00           mov al, 0
370A  EB 02           jmp 0x370e
loc_370C:
370C  B0 01           mov al, 1
loc_370E:
370E  98              cwde
370F  8B F8           mov di, ax
3711  8A 85 84 0E     mov al, byte ptr [di + 0xe84]
3715  30 E4           xor ah, ah
3717  3B 46 FE        cmp ax, word ptr [bp - 2]
371A  7D 2D           jge 0x3749
371C  C4 7E FA        les di, ptr [bp - 6]
371F  26 8A 45 02     mov al, byte ptr es:[di + 2]
3723  30 E4           xor ah, ah
3725  05 03 00        add ax, 3
3728  8B D0           mov dx, ax
372A  C4 7E FA        les di, ptr [bp - 6]
372D  26 8A 45 01     mov al, byte ptr es:[di + 1]
3731  30 E4           xor ah, ah
3733  3B C2           cmp ax, dx
3735  7F 04           jg 0x373b
3737  B0 00           mov al, 0
3739  EB 02           jmp 0x373d
loc_373B:
373B  B0 01           mov al, 1
loc_373D:
373D  98              cwde
373E  8B F8           mov di, ax
3740  8A 85 84 0E     mov al, byte ptr [di + 0xe84]
3744  30 E4           xor ah, ah
3746  89 46 FE        mov word ptr [bp - 2], ax
loc_3749:
3749  8A 46 FE        mov al, byte ptr [bp - 2]
374C  C4 7E FA        les di, ptr [bp - 6]
374F  26 88 45 0D     mov byte ptr es:[di + 0xd], al
3753  C4 7E FA        les di, ptr [bp - 6]
3756  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
375B  7F 0D           jg 0x376a
375D  B8 03 00        mov ax, 3
3760  50              push ax
3761  9A D0 06 4B 21  call far 214B:06D0
3766  08 C0           or al, al
3768  74 0E           je 0x3778
loc_376A:
376A  C4 7E FA        les di, ptr [bp - 6]
376D  26 8A 45 0D     mov al, byte ptr es:[di + 0xd]
3771  C4 7E FA        les di, ptr [bp - 6]
3774  26 88 45 0E     mov byte ptr es:[di + 0xe], al
loc_3778:
3778  89 EC           mov sp, bp
377A  5D              pop bp
377B  CA 04 00        retf 4

; ---- routine 1771:377E  (found by: call, far)
sub_377E:
377E  55              push bp
377F  89 E5           mov bp, sp
3781  83 EC 08        sub sp, 8
3784  8B 46 06        mov ax, word ptr [bp + 6]
3787  BA 14 00        mov dx, 0x14
378A  F7 E2           mul dx
378C  C4 3E 1B A9     les di, ptr [0xa91b]
3790  03 F8           add di, ax
3792  89 7E F8        mov word ptr [bp - 8], di
3795  8C 46 FA        mov word ptr [bp - 6], es
3798  FF 76 06        push word ptr [bp + 6]
379B  0E              push cs
379C  E8 77 FA        call 0x3216
379F  08 C0           or al, al
37A1  74 07           je 0x37aa
37A3  31 C0           xor ax, ax
37A5  89 46 FE        mov word ptr [bp - 2], ax
37A8  EB 74           jmp 0x381e
loc_37AA:
37AA  C4 7E F8        les di, ptr [bp - 8]
37AD  26 8A 45 0E     mov al, byte ptr es:[di + 0xe]
37B1  98              cwde
37B2  8B D0           mov dx, ax
37B4  C4 7E F8        les di, ptr [bp - 8]
37B7  26 8A 45 04     mov al, byte ptr es:[di + 4]
37BB  30 E4           xor ah, ah
37BD  05 C2 FF        add ax, 0xffc2
37C0  03 C2           add ax, dx
37C2  89 46 FC        mov word ptr [bp - 4], ax
37C5  C4 7E F8        les di, ptr [bp - 8]
37C8  26 80 7D 0C 20  cmp byte ptr es:[di + 0xc], 0x20
37CD  7C 0E           jl 0x37dd
37CF  8B 46 FC        mov ax, word ptr [bp - 4]
37D2  99              cdq
37D3  B9 10 00        mov cx, 0x10
37D6  F7 F9           idiv cx
37D8  29 46 FC        sub word ptr [bp - 4], ax
37DB  EB 0B           jmp 0x37e8
loc_37DD:
37DD  C4 7E F8        les di, ptr [bp - 8]
37E0  26 8A 45 0C     mov al, byte ptr es:[di + 0xc]
37E4  98              cwde
37E5  01 46 FC        add word ptr [bp - 4], ax
loc_37E8:
37E8  83 7E FC 00     cmp word ptr [bp - 4], 0
37EC  7D 07           jge 0x37f5
37EE  31 C0           xor ax, ax
37F0  89 46 FC        mov word ptr [bp - 4], ax
37F3  EB 0C           jmp 0x3801
loc_37F5:
37F5  81 7E FC 00 01  cmp word ptr [bp - 4], 0x100
37FA  7E 05           jle 0x3801
37FC  C7 46 FC 00 01  mov word ptr [bp - 4], 0x100
loc_3801:
3801  FF 76 06        push word ptr [bp + 6]
3804  0E              push cs
3805  E8 71 F9        call 0x3179
3808  08 C0           or al, al
380A  74 0C           je 0x3818
380C  8B 46 FC        mov ax, word ptr [bp - 4]
380F  99              cdq
3810  B9 02 00        mov cx, 2
3813  F7 F9           idiv cx
3815  89 46 FC        mov word ptr [bp - 4], ax
loc_3818:
3818  8B 46 FC        mov ax, word ptr [bp - 4]
381B  89 46 FE        mov word ptr [bp - 2], ax
loc_381E:
381E  8B 46 FE        mov ax, word ptr [bp - 2]
3821  89 EC           mov sp, bp
3823  5D              pop bp
3824  CA 02 00        retf 2

; ---- routine 1771:3827  (found by: call)
sub_3827:
3827  55              push bp
3828  89 E5           mov bp, sp
382A  83 EC 08        sub sp, 8
382D  8B 46 08        mov ax, word ptr [bp + 8]
3830  BA 14 00        mov dx, 0x14
3833  F7 E2           mul dx
3835  C4 3E 1B A9     les di, ptr [0xa91b]
3839  03 F8           add di, ax
383B  89 7E F8        mov word ptr [bp - 8], di
383E  8C 46 FA        mov word ptr [bp - 6], es
3841  C4 7E F8        les di, ptr [bp - 8]
3844  26 8B 45 12     mov ax, word ptr es:[di + 0x12]
3848  89 46 FC        mov word ptr [bp - 4], ax
384B  81 7E FC FF 7F  cmp word ptr [bp - 4], 0x7fff
3850  75 03           jne 0x3855
3852  E9 EC 00        jmp 0x3941
loc_3855:
3855  81 7E FC 88 13  cmp word ptr [bp - 4], 0x1388
385A  7E 05           jle 0x3861
385C  81 6E FC 10 27  sub word ptr [bp - 4], 0x2710
loc_3861:
3861  83 6E FC 37     sub word ptr [bp - 4], 0x37
3865  83 7E FC CE     cmp word ptr [bp - 4], -0x32
3869  7D 07           jge 0x3872
386B  C7 46 FE 01 00  mov word ptr [bp - 2], 1
3870  EB 64           jmp 0x38d6
loc_3872:
3872  83 7E FC 00     cmp word ptr [bp - 4], 0
3876  7D 07           jge 0x387f
3878  C7 46 FE 02 00  mov word ptr [bp - 2], 2
387D  EB 57           jmp 0x38d6
loc_387F:
387F  83 7E FC 32     cmp word ptr [bp - 4], 0x32
3883  7D 07           jge 0x388c
3885  C7 46 FE 03 00  mov word ptr [bp - 2], 3
388A  EB 4A           jmp 0x38d6
loc_388C:
388C  83 7E FC 64     cmp word ptr [bp - 4], 0x64
3890  7D 07           jge 0x3899
3892  C7 46 FE 04 00  mov word ptr [bp - 2], 4
3897  EB 3D           jmp 0x38d6
loc_3899:
3899  81 7E FC 96 00  cmp word ptr [bp - 4], 0x96
389E  7D 07           jge 0x38a7
38A0  C7 46 FE 05 00  mov word ptr [bp - 2], 5
38A5  EB 2F           jmp 0x38d6
loc_38A7:
38A7  81 7E FC C8 00  cmp word ptr [bp - 4], 0xc8
38AC  7D 07           jge 0x38b5
38AE  C7 46 FE 06 00  mov word ptr [bp - 2], 6
38B3  EB 21           jmp 0x38d6
loc_38B5:
38B5  81 7E FC 2C 01  cmp word ptr [bp - 4], 0x12c
38BA  7D 07           jge 0x38c3
38BC  C7 46 FE 07 00  mov word ptr [bp - 2], 7
38C1  EB 13           jmp 0x38d6
loc_38C3:
38C3  81 7E FC 90 01  cmp word ptr [bp - 4], 0x190
38C8  7D 07           jge 0x38d1
38CA  C7 46 FE 08 00  mov word ptr [bp - 2], 8
38CF  EB 05           jmp 0x38d6
loc_38D1:
38D1  C7 46 FE 09 00  mov word ptr [bp - 2], 9
loc_38D6:
38D6  8A 46 FE        mov al, byte ptr [bp - 2]
38D9  A2 86 0E        mov byte ptr [0xe86], al
38DC  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
38E1  74 33           je 0x3916
38E3  FF 76 08        push word ptr [bp + 8]
38E6  C4 7E F8        les di, ptr [bp - 8]
38E9  26 8A 05        mov al, byte ptr es:[di]
38EC  30 E4           xor ah, ah
38EE  50              push ax
38EF  0E              push cs
38F0  E8 8F 01        call 0x3a82
38F3  3D 0C 00        cmp ax, 0xc
38F6  72 17           jb 0x390f
38F8  B8 03 00        mov ax, 3
38FB  50              push ax
38FC  C4 7E F8        les di, ptr [bp - 8]
38FF  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
3903  30 E4           xor ah, ah
3905  50              push ax
3906  9A 57 0C 4B 21  call far 214B:0C57
390B  08 C0           or al, al
390D  74 07           je 0x3916
loc_390F:
390F  C6 06 B2 AA 0F  mov byte ptr [0xaab2], 0xf
3914  EB 14           jmp 0x392a
loc_3916:
3916  FF 76 08        push word ptr [bp + 8]
3919  C4 7E F8        les di, ptr [bp - 8]
391C  26 8A 45 06     mov al, byte ptr es:[di + 6]
3920  30 E4           xor ah, ah
3922  50              push ax
3923  0E              push cs
3924  E8 F9 F4        call 0x2e20
3927  A2 B2 AA        mov byte ptr [0xaab2], al
loc_392A:
392A  BF 86 0E        mov di, 0xe86
392D  1E              push ds
392E  57              push di
392F  8A 46 06        mov al, byte ptr [bp + 6]
3932  50              push ax
3933  8A 46 04        mov al, byte ptr [bp + 4]
3936  50              push ax
3937  BF 6E A9        mov di, 0xa96e
393A  1E              push ds
393B  57              push di
393C  9A A3 01 4B 21  call far 214B:01A3
loc_3941:
3941  89 EC           mov sp, bp
3943  5D              pop bp
3944  C2 06 00        ret 6

; ---- routine 1771:3947  (found by: call)
sub_3947:
3947  55              push bp
3948  89 E5           mov bp, sp
394A  83 EC 0A        sub sp, 0xa
394D  8B 46 08        mov ax, word ptr [bp + 8]
3950  BA 14 00        mov dx, 0x14
3953  F7 E2           mul dx
3955  C4 3E 1B A9     les di, ptr [0xa91b]
3959  03 F8           add di, ax
395B  89 7E F6        mov word ptr [bp - 0xa], di
395E  8C 46 F8        mov word ptr [bp - 8], es
3961  C6 06 B2 AA 70  mov byte ptr [0xaab2], 0x70
3966  C4 7E F6        les di, ptr [bp - 0xa]
3969  26 8A 45 04     mov al, byte ptr es:[di + 4]
396D  30 E4           xor ah, ah
396F  89 46 FC        mov word ptr [bp - 4], ax
3972  FF 46 FC        inc word ptr [bp - 4]
3975  C7 46 FE 01 00  mov word ptr [bp - 2], 1
397A  EB 03           jmp 0x397f
loc_397C:
397C  FF 46 FE        inc word ptr [bp - 2]
loc_397F:
397F  8B 46 FE        mov ax, word ptr [bp - 2]
3982  8B C8           mov cx, ax
3984  C4 7E F6        les di, ptr [bp - 0xa]
3987  26 8A 45 07     mov al, byte ptr es:[di + 7]
398B  30 E4           xor ah, ah
398D  BA 0C 00        mov dx, 0xc
3990  F7 E2           mul dx
3992  8B F8           mov di, ax
3994  03 F9           add di, cx
3996  8A 85 25 6D     mov al, byte ptr [di + 0x6d25]
399A  30 E4           xor ah, ah
399C  8B C8           mov cx, ax
399E  C4 7E F6        les di, ptr [bp - 0xa]
39A1  26 8A 45 05     mov al, byte ptr es:[di + 5]
39A5  30 E4           xor ah, ah
39A7  BA 0C 00        mov dx, 0xc
39AA  F7 E2           mul dx
39AC  8B F8           mov di, ax
39AE  03 F9           add di, cx
39B0  8A 85 CD 6D     mov al, byte ptr [di + 0x6dcd]
39B4  30 E4           xor ah, ah
39B6  89 46 FA        mov word ptr [bp - 6], ax
39B9  8B 46 FA        mov ax, word ptr [bp - 6]
39BC  F7 66 FC        mul word ptr [bp - 4]
39BF  31 D2           xor dx, dx
39C1  B9 00 01        mov cx, 0x100
39C4  F7 F1           div cx
39C6  89 46 FA        mov word ptr [bp - 6], ax
39C9  8B 46 04        mov ax, word ptr [bp + 4]
39CC  D1 E0           shl ax, 1
39CE  8B C8           mov cx, ax
39D0  8B 46 06        mov ax, word ptr [bp + 6]
39D3  03 46 FE        add ax, word ptr [bp - 2]
39D6  BA A0 00        mov dx, 0xa0
39D9  F7 E2           mul dx
39DB  C4 3E 6E A9     les di, ptr [0xa96e]
39DF  03 F8           add di, ax
39E1  03 F9           add di, cx
39E3  81 C7 5E FF     add di, 0xff5e
39E7  06              push es
39E8  57              push di
39E9  A0 B2 AA        mov al, byte ptr [0xaab2]
39EC  30 E4           xor ah, ah
39EE  50              push ax
39EF  FF 76 FA        push word ptr [bp - 6]
39F2  9A DB 00 4B 21  call far 214B:00DB
39F7  83 7E FE 0C     cmp word ptr [bp - 2], 0xc
39FB  74 03           je 0x3a00
39FD  E9 7C FF        jmp 0x397c
loc_3A00:
3A00  89 EC           mov sp, bp
3A02  5D              pop bp
3A03  C2 06 00        ret 6

; ---- routine 1771:3A06  (found by: far)
sub_3A06:
3A06  55              push bp
3A07  89 E5           mov bp, sp
3A09  83 EC 0A        sub sp, 0xa
3A0C  8B 46 08        mov ax, word ptr [bp + 8]
3A0F  BA 14 00        mov dx, 0x14
3A12  F7 E2           mul dx
3A14  C4 3E 1B A9     les di, ptr [0xa91b]
3A18  03 F8           add di, ax
3A1A  89 7E F6        mov word ptr [bp - 0xa], di
3A1D  8C 46 F8        mov word ptr [bp - 8], es
3A20  C4 7E F6        les di, ptr [bp - 0xa]
3A23  26 8A 45 04     mov al, byte ptr es:[di + 4]
3A27  30 E4           xor ah, ah
3A29  89 46 FA        mov word ptr [bp - 6], ax
3A2C  FF 46 FA        inc word ptr [bp - 6]
3A2F  8B 46 06        mov ax, word ptr [bp + 6]
3A32  8B C8           mov cx, ax
3A34  C4 7E F6        les di, ptr [bp - 0xa]
3A37  26 8A 45 07     mov al, byte ptr es:[di + 7]
3A3B  30 E4           xor ah, ah
3A3D  BA 0C 00        mov dx, 0xc
3A40  F7 E2           mul dx
3A42  8B F8           mov di, ax
3A44  03 F9           add di, cx
3A46  8A 85 25 6D     mov al, byte ptr [di + 0x6d25]
3A4A  30 E4           xor ah, ah
3A4C  8B C8           mov cx, ax
3A4E  C4 7E F6        les di, ptr [bp - 0xa]
3A51  26 8A 45 05     mov al, byte ptr es:[di + 5]
3A55  30 E4           xor ah, ah
3A57  BA 0C 00        mov dx, 0xc
3A5A  F7 E2           mul dx
3A5C  8B F8           mov di, ax
3A5E  03 F9           add di, cx
3A60  8A 85 CD 6D     mov al, byte ptr [di + 0x6dcd]
3A64  30 E4           xor ah, ah
3A66  89 46 FC        mov word ptr [bp - 4], ax
3A69  8B 46 FC        mov ax, word ptr [bp - 4]
3A6C  F7 66 FA        mul word ptr [bp - 6]
3A6F  31 D2           xor dx, dx
3A71  B9 20 00        mov cx, 0x20
3A74  F7 F1           div cx
3A76  89 46 FE        mov word ptr [bp - 2], ax
3A79  8B 46 FE        mov ax, word ptr [bp - 2]
3A7C  89 EC           mov sp, bp
3A7E  5D              pop bp
3A7F  CA 04 00        retf 4

; ---- routine 1771:3A82  (found by: call, far)
sub_3A82:
3A82  55              push bp
3A83  89 E5           mov bp, sp
3A85  83 EC 08        sub sp, 8
3A88  8B 46 06        mov ax, word ptr [bp + 6]
3A8B  BA BF 00        mov dx, 0xbf
3A8E  F7 E2           mul dx
3A90  C4 3E 17 A9     les di, ptr [0xa917]
3A94  03 F8           add di, ax
3A96  89 7E F8        mov word ptr [bp - 8], di
3A99  8C 46 FA        mov word ptr [bp - 6], es
3A9C  31 C0           xor ax, ax
3A9E  89 46 FE        mov word ptr [bp - 2], ax
3AA1  C7 46 FC 01 00  mov word ptr [bp - 4], 1
3AA6  EB 03           jmp 0x3aab
loc_3AA8:
3AA8  FF 46 FC        inc word ptr [bp - 4]
loc_3AAB:
3AAB  8B 46 FC        mov ax, word ptr [bp - 4]
3AAE  D1 E0           shl ax, 1
3AB0  C4 7E F8        les di, ptr [bp - 8]
3AB3  03 F8           add di, ax
3AB5  26 8B 45 FE     mov ax, word ptr es:[di - 2]
3AB9  3B 46 08        cmp ax, word ptr [bp + 8]
3ABC  75 08           jne 0x3ac6
3ABE  8B 46 FC        mov ax, word ptr [bp - 4]
3AC1  89 46 FE        mov word ptr [bp - 2], ax
3AC4  EB 06           jmp 0x3acc
loc_3AC6:
3AC6  83 7E FC 14     cmp word ptr [bp - 4], 0x14
3ACA  75 DC           jne 0x3aa8
loc_3ACC:
3ACC  8B 46 FE        mov ax, word ptr [bp - 2]
3ACF  89 EC           mov sp, bp
3AD1  5D              pop bp
3AD2  CA 04 00        retf 4
; data (not reached as code), 13 bytes
3AD5                  pstr 'Protect zone'

