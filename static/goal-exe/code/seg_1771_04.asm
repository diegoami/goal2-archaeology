; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 4 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:25EA  (found by: call)
sub_25EA:
25EA  55              push bp
25EB  89 E5           mov bp, sp
25ED  83 EC 04        sub sp, 4
25F0  8B 7E 04        mov di, word ptr [bp + 4]
25F3  36 80 7D FD 00  cmp byte ptr ss:[di - 3], 0
25F8  74 0E           je 0x2608
25FA  B8 FD 9B        mov ax, 0x9bfd
25FD  8C DA           mov dx, ds
25FF  A3 56 9B        mov word ptr [0x9b56], ax
2602  89 16 58 9B     mov word ptr [0x9b58], dx
2606  EB 0C           jmp 0x2614
loc_2608:
2608  B8 7E 9C        mov ax, 0x9c7e
260B  8C DA           mov dx, ds
260D  A3 56 9B        mov word ptr [0x9b56], ax
2610  89 16 58 9B     mov word ptr [0x9b58], dx
loc_2614:
2614  C7 06 B4 0D 01 00 mov word ptr [0xdb4], 1
261A  C6 06 B6 0D 01  mov byte ptr [0xdb6], 1
261F  83 7E 06 00     cmp word ptr [bp + 6], 0
2623  75 02           jne 0x2627
2625  EB 5B           jmp 0x2682
loc_2627:
2627  31 C0           xor ax, ax
2629  89 46 FC        mov word ptr [bp - 4], ax
262C  C7 46 FE 01 00  mov word ptr [bp - 2], 1
2631  EB 03           jmp 0x2636
loc_2633:
2633  FF 46 FE        inc word ptr [bp - 2]
loc_2636:
2636  8B 46 FE        mov ax, word ptr [bp - 2]
2639  C4 3E 56 9B     les di, ptr [0x9b56]
263D  03 F8           add di, ax
263F  26 8A 05        mov al, byte ptr es:[di]
2642  30 E4           xor ah, ah
2644  3B 46 06        cmp ax, word ptr [bp + 6]
2647  75 06           jne 0x264f
2649  8B 46 FE        mov ax, word ptr [bp - 2]
264C  89 46 FC        mov word ptr [bp - 4], ax
loc_264F:
264F  81 7E FE 80 00  cmp word ptr [bp - 2], 0x80
2654  75 DD           jne 0x2633
2656  83 7E FC 00     cmp word ptr [bp - 4], 0
265A  75 02           jne 0x265e
265C  EB 24           jmp 0x2682
loc_265E:
265E  8B 46 FC        mov ax, word ptr [bp - 4]
2661  48              dec ax
2662  31 D2           xor dx, dx
2664  B9 10 00        mov cx, 0x10
2667  F7 F1           div cx
2669  B9 04 00        mov cx, 4
266C  D3 E0           shl ax, cl
266E  40              inc ax
266F  A3 B4 0D        mov word ptr [0xdb4], ax
2672  8B 46 FC        mov ax, word ptr [bp - 4]
2675  48              dec ax
2676  31 D2           xor dx, dx
2678  B9 10 00        mov cx, 0x10
267B  F7 F1           div cx
267D  92              xchg dx, ax
267E  40              inc ax
267F  A2 B6 0D        mov byte ptr [0xdb6], al
loc_2682:
2682  89 EC           mov sp, bp
2684  5D              pop bp
2685  C2 04 00        ret 4
; data (not reached as code), 49 bytes
2688                  db 14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
2698                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
26A8                  pstr 'post unavailable'

; ---- routine 1771:26B9  (found by: call, far)
sub_26B9:
26B9  55              push bp
26BA  89 E5           mov bp, sp
26BC  81 EC 08 01     sub sp, 0x108
26C0  C4 3E 23 A9     les di, ptr [0xa923]
26C4  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
26C8  88 46 FD        mov byte ptr [bp - 3], al
26CB  C6 46 FF 00     mov byte ptr [bp - 1], 0
26CF  B0 01           mov al, 1
26D1  08 C0           or al, al
26D3  74 32           je 0x2707
26D5  8A 46 06        mov al, byte ptr [bp + 6]
26D8  50              push ax
26D9  BF 88 26        mov di, 0x2688
26DC  0E              push cs
26DD  57              push di
26DE  9A DF 08 E4 23  call far 23E4:08DF
26E3  75 22           jne 0x2707
26E5  C4 3E 23 A9     les di, ptr [0xa923]
26E9  26 8A 45 01     mov al, byte ptr es:[di + 1]
26ED  30 E4           xor ah, ah
26EF  05 80 00        add ax, 0x80
26F2  BA 03 00        mov dx, 3
26F5  F7 E2           mul dx
26F7  C4 3E 1F A9     les di, ptr [0xa91f]
26FB  03 F8           add di, ax
26FD  26 8A 05        mov al, byte ptr es:[di]
2700  30 E4           xor ah, ah
2702  50              push ax
2703  55              push bp
2704  E8 E3 FE        call 0x25ea
loc_2707:
2707  83 7E 06 03     cmp word ptr [bp + 6], 3
270B  75 19           jne 0x2726
270D  A0 B6 0D        mov al, byte ptr [0xdb6]
2710  30 E4           xor ah, ah
2712  03 06 B4 0D     add ax, word ptr [0xdb4]
2716  48              dec ax
2717  C4 3E 56 9B     les di, ptr [0x9b56]
271B  03 F8           add di, ax
271D  26 8A 05        mov al, byte ptr es:[di]
2720  30 E4           xor ah, ah
2722  50              push ax
2723  E8 36 F6        call 0x1d5c
loc_2726:
2726  80 7E FD 00     cmp byte ptr [bp - 3], 0
272A  74 0E           je 0x273a
272C  B8 FD 9B        mov ax, 0x9bfd
272F  8C DA           mov dx, ds
2731  A3 56 9B        mov word ptr [0x9b56], ax
2734  89 16 58 9B     mov word ptr [0x9b58], dx
2738  EB 0C           jmp 0x2746
loc_273A:
273A  B8 7E 9C        mov ax, 0x9c7e
273D  8C DA           mov dx, ds
273F  A3 56 9B        mov word ptr [0x9b56], ax
2742  89 16 58 9B     mov word ptr [0x9b58], dx
loc_2746:
2746  BF 66 5F        mov di, 0x5f66
2749  1E              push ds
274A  57              push di
274B  BF 6E A9        mov di, 0xa96e
274E  1E              push ds
274F  57              push di
2750  9A 29 03 4B 21  call far 214B:0329
2755  BF F2 26        mov di, 0x26f2
2758  1E              push ds
2759  57              push di
275A  BF 6E A9        mov di, 0xa96e
275D  1E              push ds
275E  57              push di
275F  9A 29 03 4B 21  call far 214B:0329
2764  80 7E FF 00     cmp byte ptr [bp - 1], 0
2768  74 12           je 0x277c
276A  BF BC 1A        mov di, 0x1abc
276D  1E              push ds
276E  57              push di
276F  BF 6E A9        mov di, 0xa96e
2772  1E              push ds
2773  57              push di
2774  9A 29 03 4B 21  call far 214B:0329
2779  E9 B9 00        jmp 0x2835
loc_277C:
277C  83 7E 06 01     cmp word ptr [bp + 6], 1
2780  75 44           jne 0x27c6
2782  B0 01           mov al, 1
2784  08 C0           or al, al
2786  74 3E           je 0x27c6
2788  BF E6 18        mov di, 0x18e6
278B  1E              push ds
278C  57              push di
278D  BF 6E A9        mov di, 0xa96e
2790  1E              push ds
2791  57              push di
2792  9A 29 03 4B 21  call far 214B:0329
2797  A0 B6 0D        mov al, byte ptr [0xdb6]
279A  30 E4           xor ah, ah
279C  03 06 B4 0D     add ax, word ptr [0xdb4]
27A0  48              dec ax
27A1  C4 3E 56 9B     les di, ptr [0x9b56]
27A5  03 F8           add di, ax
27A7  26 8A 05        mov al, byte ptr es:[di]
27AA  30 E4           xor ah, ah
27AC  50              push ax
27AD  0E              push cs
27AE  E8 C6 E3        call 0xb77
27B1  08 C0           or al, al
27B3  74 0F           je 0x27c4
27B5  BF FC 27        mov di, 0x27fc
27B8  1E              push ds
27B9  57              push di
27BA  BF 6E A9        mov di, 0xa96e
27BD  1E              push ds
27BE  57              push di
27BF  9A 29 03 4B 21  call far 214B:0329
loc_27C4:
27C4  EB 6F           jmp 0x2835
loc_27C6:
27C6  83 7E 06 03     cmp word ptr [bp + 6], 3
27CA  75 11           jne 0x27dd
27CC  BF 3A 1D        mov di, 0x1d3a
27CF  1E              push ds
27D0  57              push di
27D1  BF 6E A9        mov di, 0xa96e
27D4  1E              push ds
27D5  57              push di
27D6  9A 29 03 4B 21  call far 214B:0329
27DB  EB 58           jmp 0x2835
loc_27DD:
27DD  83 7E 06 04     cmp word ptr [bp + 6], 4
27E1  75 11           jne 0x27f4
27E3  BF CC 23        mov di, 0x23cc
27E6  1E              push ds
27E7  57              push di
27E8  BF 6E A9        mov di, 0xa96e
27EB  1E              push ds
27EC  57              push di
27ED  9A 29 03 4B 21  call far 214B:0329
27F2  EB 41           jmp 0x2835
loc_27F4:
27F4  83 7E 06 02     cmp word ptr [bp + 6], 2
27F8  75 3B           jne 0x2835
27FA  BF F4 14        mov di, 0x14f4
27FD  1E              push ds
27FE  57              push di
27FF  BF 6E A9        mov di, 0xa96e
2802  1E              push ds
2803  57              push di
2804  9A 29 03 4B 21  call far 214B:0329
2809  B0 70           mov al, 0x70
280B  50              push ax
280C  8D BE F9 FE     lea di, [bp - 0x107]
2810  16              push ss
2811  57              push di
2812  C4 3E 23 A9     les di, ptr [0xa923]
2816  26 8A 45 01     mov al, byte ptr es:[di + 1]
281A  30 E4           xor ah, ah
281C  31 D2           xor dx, dx
281E  52              push dx
281F  50              push ax
2820  9A DA 09 4B 21  call far 214B:09DA
2825  B0 01           mov al, 1
2827  50              push ax
2828  B0 1A           mov al, 0x1a
282A  50              push ax
282B  BF 6E A9        mov di, 0xa96e
282E  1E              push ds
282F  57              push di
2830  9A C8 02 4B 21  call far 214B:02C8
loc_2835:
2835  FF 36 B4 0D     push word ptr [0xdb4]
2839  E8 F8 F0        call 0x1934
283C  80 7E FD 00     cmp byte ptr [bp - 3], 0
2840  74 13           je 0x2855
2842  B8 03 00        mov ax, 3
2845  50              push ax
2846  B8 43 00        mov ax, 0x43
2849  50              push ax
284A  B8 07 00        mov ax, 7
284D  50              push ax
284E  9A C5 13 4B 21  call far 214B:13C5
2853  EB 11           jmp 0x2866
loc_2855:
2855  B8 04 00        mov ax, 4
2858  50              push ax
2859  B8 42 00        mov ax, 0x42
285C  50              push ax
285D  B8 0D 00        mov ax, 0xd
2860  50              push ax
2861  9A C5 13 4B 21  call far 214B:13C5
loc_2866:
2866  A0 B6 0D        mov al, byte ptr [0xdb6]
2869  30 E4           xor ah, ah
286B  05 07 00        add ax, 7
286E  50              push ax
286F  B8 41 00        mov ax, 0x41
2872  50              push ax
2873  B8 0F 00        mov ax, 0xf
2876  50              push ax
2877  9A C5 13 4B 21  call far 214B:13C5
287C  A0 B6 0D        mov al, byte ptr [0xdb6]
287F  30 E4           xor ah, ah
2881  03 06 B4 0D     add ax, word ptr [0xdb4]
2885  48              dec ax
2886  C4 3E 56 9B     les di, ptr [0x9b56]
288A  03 F8           add di, ax
288C  26 8A 05        mov al, byte ptr es:[di]
288F  30 E4           xor ah, ah
2891  50              push ax
2892  E8 E8 EC        call 0x157d
2895  83 7E 06 02     cmp word ptr [bp + 6], 2
2899  75 40           jne 0x28db
289B  B0 70           mov al, 0x70
289D  50              push ax
289E  A0 B6 0D        mov al, byte ptr [0xdb6]
28A1  30 E4           xor ah, ah
28A3  03 06 B4 0D     add ax, word ptr [0xdb4]
28A7  48              dec ax
28A8  C4 3E 56 9B     les di, ptr [0x9b56]
28AC  03 F8           add di, ax
28AE  26 8A 05        mov al, byte ptr es:[di]
28B1  30 E4           xor ah, ah
28B3  50              push ax
28B4  0E              push cs
28B5  E8 2F E8        call 0x10e7
28B8  99              cdq
28B9  B9 0A 00        mov cx, 0xa
28BC  F7 F9           idiv cx
28BE  BA 0B 00        mov dx, 0xb
28C1  F7 E2           mul dx
28C3  8B F8           mov di, ax
28C5  81 C7 B7 0D     add di, 0xdb7
28C9  1E              push ds
28CA  57              push di
28CB  B0 05           mov al, 5
28CD  50              push ax
28CE  B0 2B           mov al, 0x2b
28D0  50              push ax
28D1  BF 6E A9        mov di, 0xa96e
28D4  1E              push ds
28D5  57              push di
28D6  9A C8 02 4B 21  call far 214B:02C8
loc_28DB:
28DB  C4 3E 6E A9     les di, ptr [0xa96e]
28DF  06              push es
28E0  57              push di
28E1  C4 3E 6A A9     les di, ptr [0xa96a]
28E5  06              push es
28E6  57              push di
28E7  B8 A0 0F        mov ax, 0xfa0
28EA  50              push ax
28EB  9A 5D 02 E4 23  call far 23E4:025D
28F0  9A DD 08 4B 21  call far 214B:08DD
28F5  A0 76 A9        mov al, byte ptr [0xa976]
28F8  50              push ax
28F9  9A B2 19 E4 23  call far 23E4:19B2
28FE  A2 76 A9        mov byte ptr [0xa976], al
2901  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
2906  75 06           jne 0x290e
2908  B0 01           mov al, 1
290A  08 C0           or al, al
290C  75 11           jne 0x291f
loc_290E:
290E  80 3E 76 A9 A8  cmp byte ptr [0xa976], 0xa8
2913  75 06           jne 0x291b
2915  B0 00           mov al, 0
2917  08 C0           or al, al
2919  75 04           jne 0x291f
loc_291B:
291B  B0 00           mov al, 0
291D  EB 02           jmp 0x2921
loc_291F:
291F  B0 01           mov al, 1
loc_2921:
2921  88 46 FE        mov byte ptr [bp - 2], al
2924  A0 76 A9        mov al, byte ptr [0xa976]
2927  3C AC           cmp al, 0xac
2929  75 21           jne 0x294c
292B  80 3E B6 0D 01  cmp byte ptr [0xdb6], 1
2930  76 06           jbe 0x2938
2932  FE 0E B6 0D     dec byte ptr [0xdb6]
2936  EB 11           jmp 0x2949
loc_2938:
2938  83 3E B4 0D 10  cmp word ptr [0xdb4], 0x10
293D  76 0A           jbe 0x2949
293F  83 2E B4 0D 10  sub word ptr [0xdb4], 0x10
2944  C6 06 B6 0D 10  mov byte ptr [0xdb6], 0x10
loc_2949:
2949  E9 C5 00        jmp 0x2a11
loc_294C:
294C  3C B1           cmp al, 0xb1
294E  75 21           jne 0x2971
2950  80 3E B6 0D 10  cmp byte ptr [0xdb6], 0x10
2955  73 06           jae 0x295d
2957  FE 06 B6 0D     inc byte ptr [0xdb6]
295B  EB 11           jmp 0x296e
loc_295D:
295D  83 3E B4 0D 71  cmp word ptr [0xdb4], 0x71
2962  73 0A           jae 0x296e
2964  83 06 B4 0D 10  add word ptr [0xdb4], 0x10
2969  C6 06 B6 0D 01  mov byte ptr [0xdb6], 1
loc_296E:
296E  E9 A0 00        jmp 0x2a11
loc_2971:
2971  3C AD           cmp al, 0xad
2973  74 04           je 0x2979
2975  3C AE           cmp al, 0xae
2977  75 0F           jne 0x2988
loc_2979:
2979  83 3E B4 0D 10  cmp word ptr [0xdb4], 0x10
297E  76 05           jbe 0x2985
2980  83 2E B4 0D 10  sub word ptr [0xdb4], 0x10
loc_2985:
2985  E9 89 00        jmp 0x2a11
loc_2988:
2988  3C B2           cmp al, 0xb2
298A  74 04           je 0x2990
298C  3C AF           cmp al, 0xaf
298E  75 0E           jne 0x299e
loc_2990:
2990  83 3E B4 0D 71  cmp word ptr [0xdb4], 0x71
2995  73 05           jae 0x299c
2997  83 06 B4 0D 10  add word ptr [0xdb4], 0x10
loc_299C:
299C  EB 73           jmp 0x2a11
loc_299E:
299E  3C AB           cmp al, 0xab
29A0  75 0D           jne 0x29af
29A2  C7 06 B4 0D 01 00 mov word ptr [0xdb4], 1
29A8  C6 06 B6 0D 01  mov byte ptr [0xdb6], 1
29AD  EB 62           jmp 0x2a11
loc_29AF:
29AF  3C B0           cmp al, 0xb0
29B1  75 0D           jne 0x29c0
29B3  C7 06 B4 0D 71 00 mov word ptr [0xdb4], 0x71
29B9  C6 06 B6 0D 10  mov byte ptr [0xdb6], 0x10
29BE  EB 51           jmp 0x2a11
loc_29C0:
29C0  3C 54           cmp al, 0x54
29C2  75 4D           jne 0x2a11
29C4  83 7E 06 01     cmp word ptr [bp + 6], 1
29C8  75 47           jne 0x2a11
29CA  A0 B6 0D        mov al, byte ptr [0xdb6]
29CD  30 E4           xor ah, ah
29CF  03 06 B4 0D     add ax, word ptr [0xdb4]
29D3  48              dec ax
29D4  C4 3E 56 9B     les di, ptr [0x9b56]
29D8  03 F8           add di, ax
29DA  26 8A 05        mov al, byte ptr es:[di]
29DD  30 E4           xor ah, ah
29DF  50              push ax
29E0  0E              push cs
29E1  E8 93 E1        call 0xb77
29E4  08 C0           or al, al
29E6  74 29           je 0x2a11
29E8  BF 0E 28        mov di, 0x280e
29EB  1E              push ds
29EC  57              push di
29ED  BF 6E A9        mov di, 0xa96e
29F0  1E              push ds
29F1  57              push di
29F2  9A 29 03 4B 21  call far 214B:0329
29F7  A0 B6 0D        mov al, byte ptr [0xdb6]
29FA  30 E4           xor ah, ah
29FC  03 06 B4 0D     add ax, word ptr [0xdb4]
2A00  48              dec ax
2A01  C4 3E 56 9B     les di, ptr [0x9b56]
2A05  03 F8           add di, ax
2A07  26 8A 05        mov al, byte ptr es:[di]
2A0A  30 E4           xor ah, ah
2A0C  50              push ax
2A0D  0E              push cs
2A0E  E8 70 EF        call 0x1981
loc_2A11:
2A11  B0 00           mov al, 0
2A13  08 C0           or al, al
2A15  74 71           je 0x2a88
2A17  80 7E FF 00     cmp byte ptr [bp - 1], 0
2A1B  75 6B           jne 0x2a88
2A1D  A0 76 A9        mov al, byte ptr [0xa976]
2A20  3C 4D           cmp al, 0x4d
2A22  75 13           jne 0x2a37
2A24  A0 B6 0D        mov al, byte ptr [0xdb6]
2A27  30 E4           xor ah, ah
2A29  03 06 B4 0D     add ax, word ptr [0xdb4]
2A2D  48              dec ax
2A2E  89 46 FB        mov word ptr [bp - 5], ax
2A31  C6 46 FF 01     mov byte ptr [bp - 1], 1
2A35  EB 51           jmp 0x2a88
loc_2A37:
2A37  3C 53           cmp al, 0x53
2A39  75 23           jne 0x2a5e
2A3B  FF 36 B4 0D     push word ptr [0xdb4]
2A3F  E8 F2 EE        call 0x1934
2A42  A0 B6 0D        mov al, byte ptr [0xdb6]
2A45  30 E4           xor ah, ah
2A47  03 06 B4 0D     add ax, word ptr [0xdb4]
2A4B  48              dec ax
2A4C  C4 3E 56 9B     les di, ptr [0x9b56]
2A50  03 F8           add di, ax
2A52  26 8A 05        mov al, byte ptr es:[di]
2A55  30 E4           xor ah, ah
2A57  50              push ax
2A58  0E              push cs
2A59  E8 25 EF        call 0x1981
2A5C  EB 2A           jmp 0x2a88
loc_2A5E:
2A5E  3C 31           cmp al, 0x31
2A60  72 26           jb 0x2a88
2A62  3C 33           cmp al, 0x33
2A64  77 22           ja 0x2a88
2A66  A0 B6 0D        mov al, byte ptr [0xdb6]
2A69  30 E4           xor ah, ah
2A6B  03 06 B4 0D     add ax, word ptr [0xdb4]
2A6F  48              dec ax
2A70  C4 3E 56 9B     les di, ptr [0x9b56]
2A74  03 F8           add di, ax
2A76  26 8A 05        mov al, byte ptr es:[di]
2A79  30 E4           xor ah, ah
2A7B  50              push ax
2A7C  A0 76 A9        mov al, byte ptr [0xa976]
2A7F  30 E4           xor ah, ah
2A81  2D 30 00        sub ax, 0x30
2A84  50              push ax
2A85  E8 F5 EF        call 0x1a7d
loc_2A88:
2A88  80 7E FF 00     cmp byte ptr [bp - 1], 0
2A8C  74 0E           je 0x2a9c
2A8E  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
2A93  75 07           jne 0x2a9c
2A95  C6 46 FF 00     mov byte ptr [bp - 1], 0
2A99  E9 6A 02        jmp 0x2d06
loc_2A9C:
2A9C  A0 76 A9        mov al, byte ptr [0xa976]
2A9F  3C 20           cmp al, 0x20
2AA1  75 21           jne 0x2ac4
2AA3  A0 B6 0D        mov al, byte ptr [0xdb6]
2AA6  30 E4           xor ah, ah
2AA8  03 06 B4 0D     add ax, word ptr [0xdb4]
2AAC  48              dec ax
2AAD  C4 3E 56 9B     les di, ptr [0x9b56]
2AB1  03 F8           add di, ax
2AB3  26 8A 05        mov al, byte ptr es:[di]
2AB6  30 E4           xor ah, ah
2AB8  50              push ax
2AB9  B8 01 00        mov ax, 1
2ABC  50              push ax
2ABD  0E              push cs
2ABE  E8 30 26        call 0x50f1
2AC1  E9 42 02        jmp 0x2d06
loc_2AC4:
2AC4  3C B6           cmp al, 0xb6
2AC6  75 12           jne 0x2ada
2AC8  80 7E FD 00     cmp byte ptr [bp - 3], 0
2ACC  74 04           je 0x2ad2
2ACE  B0 00           mov al, 0
2AD0  EB 02           jmp 0x2ad4
loc_2AD2:
2AD2  B0 01           mov al, 1
loc_2AD4:
2AD4  88 46 FD        mov byte ptr [bp - 3], al
2AD7  E9 2C 02        jmp 0x2d06
loc_2ADA:
2ADA  3C A0           cmp al, 0xa0
2ADC  75 1C           jne 0x2afa
2ADE  A0 B6 0D        mov al, byte ptr [0xdb6]
2AE1  30 E4           xor ah, ah
2AE3  03 06 B4 0D     add ax, word ptr [0xdb4]
2AE7  48              dec ax
2AE8  C4 3E 56 9B     les di, ptr [0x9b56]
2AEC  03 F8           add di, ax
2AEE  26 8A 05        mov al, byte ptr es:[di]
2AF1  30 E4           xor ah, ah
2AF3  50              push ax
2AF4  E8 23 E5        call 0x101a
2AF7  E9 0C 02        jmp 0x2d06
loc_2AFA:
2AFA  3C A1           cmp al, 0xa1
2AFC  75 36           jne 0x2b34
2AFE  A0 B6 0D        mov al, byte ptr [0xdb6]
2B01  30 E4           xor ah, ah
2B03  03 06 B4 0D     add ax, word ptr [0xdb4]
2B07  48              dec ax
2B08  C4 3E 56 9B     les di, ptr [0x9b56]
2B0C  03 F8           add di, ax
2B0E  26 8A 05        mov al, byte ptr es:[di]
2B11  30 E4           xor ah, ah
2B13  BA BF 00        mov dx, 0xbf
2B16  F7 E2           mul dx
2B18  C4 3E 17 A9     les di, ptr [0xa917]
2B1C  03 F8           add di, ax
2B1E  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
2B22  30 E4           xor ah, ah
2B24  50              push ax
2B25  B8 0A 00        mov ax, 0xa
2B28  50              push ax
2B29  B8 02 00        mov ax, 2
2B2C  50              push ax
2B2D  0E              push cs
2B2E  E8 6F DE        call 0x9a0
2B31  E9 D2 01        jmp 0x2d06
loc_2B34:
2B34  3C 0D           cmp al, 0xd
2B36  74 03           je 0x2b3b
2B38  E9 CB 01        jmp 0x2d06
loc_2B3B:
2B3B  80 7E FF 00     cmp byte ptr [bp - 1], 0
2B3F  75 03           jne 0x2b44
2B41  E9 F4 00        jmp 0x2c38
loc_2B44:
2B44  A0 B6 0D        mov al, byte ptr [0xdb6]
2B47  30 E4           xor ah, ah
2B49  03 06 B4 0D     add ax, word ptr [0xdb4]
2B4D  48              dec ax
2B4E  89 46 F9        mov word ptr [bp - 7], ax
2B51  80 7E FD 00     cmp byte ptr [bp - 3], 0
2B55  74 49           je 0x2ba0
2B57  8B 46 F9        mov ax, word ptr [bp - 7]
2B5A  C4 3E 56 9B     les di, ptr [0x9b56]
2B5E  03 F8           add di, ax
2B60  26 8A 05        mov al, byte ptr es:[di]
2B63  30 E4           xor ah, ah
2B65  BA BF 00        mov dx, 0xbf
2B68  F7 E2           mul dx
2B6A  C4 3E 17 A9     les di, ptr [0xa917]
2B6E  03 F8           add di, ax
2B70  81 C7 2B 00     add di, 0x2b
2B74  06              push es
2B75  57              push di
2B76  8B 46 FB        mov ax, word ptr [bp - 5]
2B79  C4 3E 56 9B     les di, ptr [0x9b56]
2B7D  03 F8           add di, ax
2B7F  26 8A 05        mov al, byte ptr es:[di]
2B82  30 E4           xor ah, ah
2B84  BA BF 00        mov dx, 0xbf
2B87  F7 E2           mul dx
2B89  C4 3E 17 A9     les di, ptr [0xa917]
2B8D  03 F8           add di, ax
2B8F  81 C7 2B 00     add di, 0x2b
2B93  06              push es
2B94  57              push di
2B95  B8 01 00        mov ax, 1
2B98  50              push ax
2B99  9A 7B 00 4B 21  call far 214B:007B
2B9E  EB 47           jmp 0x2be7
loc_2BA0:
2BA0  8B 46 F9        mov ax, word ptr [bp - 7]
2BA3  C4 3E 56 9B     les di, ptr [0x9b56]
2BA7  03 F8           add di, ax
2BA9  26 8A 05        mov al, byte ptr es:[di]
2BAC  30 E4           xor ah, ah
2BAE  BA BF 00        mov dx, 0xbf
2BB1  F7 E2           mul dx
2BB3  C4 3E 17 A9     les di, ptr [0xa917]
2BB7  03 F8           add di, ax
2BB9  81 C7 2A 00     add di, 0x2a
2BBD  06              push es
2BBE  57              push di
2BBF  8B 46 FB        mov ax, word ptr [bp - 5]
2BC2  C4 3E 56 9B     les di, ptr [0x9b56]
2BC6  03 F8           add di, ax
2BC8  26 8A 05        mov al, byte ptr es:[di]
2BCB  30 E4           xor ah, ah
2BCD  BA BF 00        mov dx, 0xbf
2BD0  F7 E2           mul dx
2BD2  C4 3E 17 A9     les di, ptr [0xa917]
2BD6  03 F8           add di, ax
2BD8  81 C7 2A 00     add di, 0x2a
2BDC  06              push es
2BDD  57              push di
2BDE  B8 01 00        mov ax, 1
2BE1  50              push ax
2BE2  9A 7B 00 4B 21  call far 214B:007B
loc_2BE7:
2BE7  8B 46 F9        mov ax, word ptr [bp - 7]
2BEA  C4 3E 56 9B     les di, ptr [0x9b56]
2BEE  03 F8           add di, ax
2BF0  06              push es
2BF1  57              push di
2BF2  8B 46 FB        mov ax, word ptr [bp - 5]
2BF5  C4 3E 56 9B     les di, ptr [0x9b56]
2BF9  03 F8           add di, ax
2BFB  06              push es
2BFC  57              push di
2BFD  B8 01 00        mov ax, 1
2C00  50              push ax
2C01  9A 7B 00 4B 21  call far 214B:007B
2C06  8B 46 F9        mov ax, word ptr [bp - 7]
2C09  C4 3E 56 9B     les di, ptr [0x9b56]
2C0D  03 F8           add di, ax
2C0F  26 8A 05        mov al, byte ptr es:[di]
2C12  30 E4           xor ah, ah
2C14  50              push ax
2C15  0E              push cs
2C16  E8 B3 6B        call 0x97cc
2C19  8B 46 FB        mov ax, word ptr [bp - 5]
2C1C  C4 3E 56 9B     les di, ptr [0x9b56]
2C20  03 F8           add di, ax
2C22  26 8A 05        mov al, byte ptr es:[di]
2C25  30 E4           xor ah, ah
2C27  50              push ax
2C28  0E              push cs
2C29  E8 A0 6B        call 0x97cc
2C2C  C6 46 FF 00     mov byte ptr [bp - 1], 0
2C30  C6 06 1A 0C 01  mov byte ptr [0xc1a], 1
2C35  E9 CE 00        jmp 0x2d06
loc_2C38:
2C38  83 7E 06 02     cmp word ptr [bp + 6], 2
2C3C  75 5D           jne 0x2c9b
2C3E  A0 B6 0D        mov al, byte ptr [0xdb6]
2C41  30 E4           xor ah, ah
2C43  03 06 B4 0D     add ax, word ptr [0xdb4]
2C47  48              dec ax
2C48  C4 3E 56 9B     les di, ptr [0x9b56]
2C4C  03 F8           add di, ax
2C4E  26 8A 05        mov al, byte ptr es:[di]
2C51  30 E4           xor ah, ah
2C53  89 46 F9        mov word ptr [bp - 7], ax
2C56  FF 76 F9        push word ptr [bp - 7]
2C59  0E              push cs
2C5A  E8 1A DF        call 0xb77
2C5D  50              push ax
2C5E  BF A8 26        mov di, 0x26a8
2C61  0E              push cs
2C62  57              push di
2C63  9A 65 17 4B 21  call far 214B:1765
2C68  08 C0           or al, al
2C6A  74 04           je 0x2c70
2C6C  B0 00           mov al, 0
2C6E  EB 02           jmp 0x2c72
loc_2C70:
2C70  B0 01           mov al, 1
loc_2C72:
2C72  88 46 FE        mov byte ptr [bp - 2], al
2C75  80 7E FE 00     cmp byte ptr [bp - 2], 0
2C79  74 1E           je 0x2c99
2C7B  8A 4E F9        mov cl, byte ptr [bp - 7]
2C7E  C4 3E 23 A9     les di, ptr [0xa923]
2C82  26 8A 45 01     mov al, byte ptr es:[di + 1]
2C86  30 E4           xor ah, ah
2C88  05 80 00        add ax, 0x80
2C8B  BA 03 00        mov dx, 3
2C8E  F7 E2           mul dx
2C90  C4 3E 1F A9     les di, ptr [0xa91f]
2C94  03 F8           add di, ax
2C96  26 88 0D        mov byte ptr es:[di], cl
loc_2C99:
2C99  EB 6B           jmp 0x2d06
loc_2C9B:
2C9B  83 7E 06 04     cmp word ptr [bp + 6], 4
2C9F  75 1E           jne 0x2cbf
2CA1  A0 B6 0D        mov al, byte ptr [0xdb6]
2CA4  30 E4           xor ah, ah
2CA6  03 06 B4 0D     add ax, word ptr [0xdb4]
2CAA  48              dec ax
2CAB  C4 3E 56 9B     les di, ptr [0x9b56]
2CAF  03 F8           add di, ax
2CB1  26 8A 05        mov al, byte ptr es:[di]
2CB4  30 E4           xor ah, ah
2CB6  A3 66 9B        mov word ptr [0x9b66], ax
2CB9  C6 46 FE 01     mov byte ptr [bp - 2], 1
2CBD  EB 47           jmp 0x2d06
loc_2CBF:
2CBF  83 7E 06 01     cmp word ptr [bp + 6], 1
2CC3  75 22           jne 0x2ce7
2CC5  B0 01           mov al, 1
2CC7  08 C0           or al, al
2CC9  74 1C           je 0x2ce7
2CCB  A0 B6 0D        mov al, byte ptr [0xdb6]
2CCE  30 E4           xor ah, ah
2CD0  03 06 B4 0D     add ax, word ptr [0xdb4]
2CD4  48              dec ax
2CD5  C4 3E 56 9B     les di, ptr [0x9b56]
2CD9  03 F8           add di, ax
2CDB  26 8A 05        mov al, byte ptr es:[di]
2CDE  30 E4           xor ah, ah
2CE0  50              push ax
2CE1  0E              push cs
2CE2  E8 BD 4E        call 0x7ba2
2CE5  EB 1F           jmp 0x2d06
loc_2CE7:
2CE7  83 7E 06 03     cmp word ptr [bp + 6], 3
2CEB  75 19           jne 0x2d06
2CED  A0 B6 0D        mov al, byte ptr [0xdb6]
2CF0  30 E4           xor ah, ah
2CF2  03 06 B4 0D     add ax, word ptr [0xdb4]
2CF6  48              dec ax
2CF7  C4 3E 56 9B     les di, ptr [0x9b56]
2CFB  03 F8           add di, ax
2CFD  26 8A 05        mov al, byte ptr es:[di]
2D00  30 E4           xor ah, ah
2D02  50              push ax
2D03  E8 56 F0        call 0x1d5c
loc_2D06:
2D06  80 7E FE 00     cmp byte ptr [bp - 2], 0
2D0A  75 03           jne 0x2d0f
2D0C  E9 17 FA        jmp 0x2726
loc_2D0F:
2D0F  89 EC           mov sp, bp
2D11  5D              pop bp
2D12  CA 02 00        retf 2

; ---- routine 1771:2D15  (found by: far)
sub_2D15:
2D15  55              push bp
2D16  89 E5           mov bp, sp
2D18  83 EC 0C        sub sp, 0xc
2D1B  C4 3E 23 A9     les di, ptr [0xa923]
2D1F  89 7E FA        mov word ptr [bp - 6], di
2D22  8C 46 FC        mov word ptr [bp - 4], es
2D25  C4 7E FA        les di, ptr [bp - 6]
2D28  26 8A 05        mov al, byte ptr es:[di]
2D2B  30 E4           xor ah, ah
2D2D  89 46 F8        mov word ptr [bp - 8], ax
2D30  B8 01 00        mov ax, 1
2D33  3B 46 F8        cmp ax, word ptr [bp - 8]
2D36  76 03           jbe 0x2d3b
2D38  E9 D9 00        jmp 0x2e14
loc_2D3B:
2D3B  89 46 FE        mov word ptr [bp - 2], ax
2D3E  EB 03           jmp 0x2d43
loc_2D40:
2D40  FF 46 FE        inc word ptr [bp - 2]
loc_2D43:
2D43  8A 46 FE        mov al, byte ptr [bp - 2]
2D46  C4 7E FA        les di, ptr [bp - 6]
2D49  26 88 45 01     mov byte ptr es:[di + 1], al
2D4D  B8 02 00        mov ax, 2
2D50  50              push ax
2D51  0E              push cs
2D52  E8 64 F9        call 0x26b9
2D55  8B 46 FE        mov ax, word ptr [bp - 2]
2D58  05 80 00        add ax, 0x80
2D5B  BA 03 00        mov dx, 3
2D5E  F7 E2           mul dx
2D60  C4 3E 1F A9     les di, ptr [0xa91f]
2D64  03 F8           add di, ax
2D66  26 80 3D 00     cmp byte ptr es:[di], 0
2D6A  75 07           jne 0x2d73
2D6C  31 C0           xor ax, ax
2D6E  9A D8 00 E4 23  call far 23E4:00D8
loc_2D73:
2D73  8B 46 FE        mov ax, word ptr [bp - 2]
2D76  05 80 00        add ax, 0x80
2D79  BA 03 00        mov dx, 3
2D7C  F7 E2           mul dx
2D7E  C4 3E 1F A9     les di, ptr [0xa91f]
2D82  03 F8           add di, ax
2D84  26 8A 05        mov al, byte ptr es:[di]
2D87  30 E4           xor ah, ah
2D89  BA BF 00        mov dx, 0xbf
2D8C  F7 E2           mul dx
2D8E  C4 3E 17 A9     les di, ptr [0xa917]
2D92  03 F8           add di, ax
2D94  89 7E F4        mov word ptr [bp - 0xc], di
2D97  8C 46 F6        mov word ptr [bp - 0xa], es
2D9A  8B 46 FE        mov ax, word ptr [bp - 2]
2D9D  05 80 00        add ax, 0x80
2DA0  C4 7E F4        les di, ptr [bp - 0xc]
2DA3  26 88 45 2E     mov byte ptr es:[di + 0x2e], al
2DA7  C4 7E F4        les di, ptr [bp - 0xc]
2DAA  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
2DAE  30 E4           xor ah, ah
2DB0  BA 03 00        mov dx, 3
2DB3  F7 E2           mul dx
2DB5  C4 3E 1F A9     les di, ptr [0xa91f]
2DB9  03 F8           add di, ax
2DBB  26 8A 05        mov al, byte ptr es:[di]
2DBE  30 E4           xor ah, ah
2DC0  50              push ax
2DC1  0E              push cs
2DC2  E8 86 E3        call 0x114b
2DC5  8A D0           mov dl, al
2DC7  C4 7E FA        les di, ptr [bp - 6]
2DCA  26 8A 45 01     mov al, byte ptr es:[di + 1]
2DCE  30 E4           xor ah, ah
2DD0  C4 7E FA        les di, ptr [bp - 6]
2DD3  03 F8           add di, ax
2DD5  26 88 55 0D     mov byte ptr es:[di + 0xd], dl
2DD9  C4 7E F4        les di, ptr [bp - 0xc]
2DDC  26 8A 55 2A     mov dl, byte ptr es:[di + 0x2a]
2DE0  C4 7E FA        les di, ptr [bp - 6]
2DE3  26 8A 45 01     mov al, byte ptr es:[di + 1]
2DE7  30 E4           xor ah, ah
2DE9  C4 7E FA        les di, ptr [bp - 6]
2DEC  03 F8           add di, ax
2DEE  26 88 55 07     mov byte ptr es:[di + 7], dl
2DF2  8B 46 FE        mov ax, word ptr [bp - 2]
2DF5  05 80 00        add ax, 0x80
2DF8  50              push ax
2DF9  B8 0A 00        mov ax, 0xa
2DFC  50              push ax
2DFD  B8 02 00        mov ax, 2
2E00  50              push ax
2E01  0E              push cs
2E02  E8 9B DB        call 0x9a0
2E05  0E              push cs
2E06  E8 BB 6A        call 0x98c4
2E09  8B 46 FE        mov ax, word ptr [bp - 2]
2E0C  3B 46 F8        cmp ax, word ptr [bp - 8]
2E0F  74 03           je 0x2e14
2E11  E9 2C FF        jmp 0x2d40
loc_2E14:
2E14  C4 7E FA        les di, ptr [bp - 6]
2E17  26 C6 45 01 01  mov byte ptr es:[di + 1], 1
2E1C  89 EC           mov sp, bp
2E1E  5D              pop bp
2E1F  CB              retf

; ---- routine 1771:2E20  (found by: call, far)
sub_2E20:
2E20  55              push bp
2E21  89 E5           mov bp, sp
2E23  83 EC 06        sub sp, 6
2E26  8B 46 08        mov ax, word ptr [bp + 8]
2E29  BA 14 00        mov dx, 0x14
2E2C  F7 E2           mul dx
2E2E  C4 3E 1B A9     les di, ptr [0xa91b]
2E32  03 F8           add di, ax
2E34  89 7E FB        mov word ptr [bp - 5], di
2E37  8C 46 FD        mov word ptr [bp - 3], es
2E3A  C4 7E FB        les di, ptr [bp - 5]
2E3D  26 80 7D 0E 00  cmp byte ptr es:[di + 0xe], 0
2E42  75 06           jne 0x2e4a
2E44  C6 46 FF 06     mov byte ptr [bp - 1], 6
2E48  EB 3E           jmp 0x2e88
loc_2E4A:
2E4A  B8 08 00        mov ax, 8
2E4D  50              push ax
2E4E  C4 7E FB        les di, ptr [bp - 5]
2E51  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
2E55  30 E4           xor ah, ah
2E57  50              push ax
2E58  9A 57 0C 4B 21  call far 214B:0C57
2E5D  08 C0           or al, al
2E5F  75 17           jne 0x2e78
2E61  B8 06 00        mov ax, 6
2E64  50              push ax
2E65  C4 7E FB        les di, ptr [bp - 5]
2E68  26 8A 45 10     mov al, byte ptr es:[di + 0x10]
2E6C  30 E4           xor ah, ah
2E6E  50              push ax
2E6F  9A 57 0C 4B 21  call far 214B:0C57
2E74  08 C0           or al, al
2E76  74 06           je 0x2e7e
loc_2E78:
2E78  C6 46 FF 05     mov byte ptr [bp - 1], 5
2E7C  EB 0A           jmp 0x2e88
loc_2E7E:
2E7E  8B 7E 06        mov di, word ptr [bp + 6]
2E81  8A 85 9A 69     mov al, byte ptr [di + 0x699a]
2E85  88 46 FF        mov byte ptr [bp - 1], al
loc_2E88:
2E88  8A 46 FF        mov al, byte ptr [bp - 1]
2E8B  89 EC           mov sp, bp
2E8D  5D              pop bp
2E8E  CA 04 00        retf 4
; data (not reached as code), 2 bytes
2E91                  db 01 20   ; . 

; ---- routine 1771:2E93  (found by: call, far)
sub_2E93:
2E93  55              push bp
2E94  89 E5           mov bp, sp
2E96  81 EC 00 01     sub sp, 0x100
2E9A  8D BE 00 FF     lea di, [bp - 0x100]
2E9E  16              push ss
2E9F  57              push di
2EA0  8B 46 06        mov ax, word ptr [bp + 6]
2EA3  C4 3E 70 9B     les di, ptr [0x9b70]
2EA7  03 F8           add di, ax
2EA9  26 8A 05        mov al, byte ptr es:[di]
2EAC  50              push ax
2EAD  9A 5A 07 E4 23  call far 23E4:075A
2EB2  BF 91 2E        mov di, 0x2e91
2EB5  0E              push cs
2EB6  57              push di
2EB7  9A B7 06 E4 23  call far 23E4:06B7
2EBC  8B 46 06        mov ax, word ptr [bp + 6]
2EBF  BA 0B 00        mov dx, 0xb
2EC2  F7 E2           mul dx
2EC4  C4 3E 6C 9B     les di, ptr [0x9b6c]
2EC8  03 F8           add di, ax
2ECA  06              push es
2ECB  57              push di
2ECC  9A B7 06 E4 23  call far 23E4:06B7
2ED1  C4 7E 08        les di, ptr [bp + 8]
2ED4  06              push es
2ED5  57              push di
2ED6  B8 0C 00        mov ax, 0xc
2ED9  50              push ax
2EDA  9A 44 06 E4 23  call far 23E4:0644
2EDF  89 EC           mov sp, bp
2EE1  5D              pop bp
2EE2  CA 02 00        retf 2

; ---- routine 1771:2EE5  (found by: call, far)
sub_2EE5:
2EE5  55              push bp
2EE6  89 E5           mov bp, sp
2EE8  81 EC 04 01     sub sp, 0x104
2EEC  8B 46 0A        mov ax, word ptr [bp + 0xa]
2EEF  BA 14 00        mov dx, 0x14
2EF2  F7 E2           mul dx
2EF4  C4 3E 1B A9     les di, ptr [0xa91b]
2EF8  03 F8           add di, ax
2EFA  89 7E FC        mov word ptr [bp - 4], di
2EFD  8C 46 FE        mov word ptr [bp - 2], es
2F00  FF 76 0A        push word ptr [bp + 0xa]
2F03  C4 7E FC        les di, ptr [bp - 4]
2F06  26 8A 45 06     mov al, byte ptr es:[di + 6]
2F0A  30 E4           xor ah, ah
2F0C  50              push ax
2F0D  0E              push cs
2F0E  E8 0F FF        call 0x2e20
2F11  50              push ax
2F12  8D BE FC FE     lea di, [bp - 0x104]
2F16  16              push ss
2F17  57              push di
2F18  FF 76 0A        push word ptr [bp + 0xa]
2F1B  0E              push cs
2F1C  E8 74 FF        call 0x2e93
2F1F  8A 46 08        mov al, byte ptr [bp + 8]
2F22  50              push ax
2F23  8A 46 06        mov al, byte ptr [bp + 6]
2F26  50              push ax
2F27  BF 6E A9        mov di, 0xa96e
2F2A  1E              push ds
2F2B  57              push di
2F2C  9A C8 02 4B 21  call far 214B:02C8
2F31  89 EC           mov sp, bp
2F33  5D              pop bp
2F34  CA 06 00        retf 6

; ---- routine 1771:2F37  (found by: call, far)
sub_2F37:
2F37  55              push bp
2F38  89 E5           mov bp, sp
2F3A  81 EC 04 01     sub sp, 0x104
2F3E  8B 46 0A        mov ax, word ptr [bp + 0xa]
2F41  BA 14 00        mov dx, 0x14
2F44  F7 E2           mul dx
2F46  C4 3E 1B A9     les di, ptr [0xa91b]
2F4A  03 F8           add di, ax
2F4C  89 7E FC        mov word ptr [bp - 4], di
2F4F  8C 46 FE        mov word ptr [bp - 2], es
2F52  83 7E 0A 00     cmp word ptr [bp + 0xa], 0
2F56  75 02           jne 0x2f5a
2F58  EB 4D           jmp 0x2fa7
loc_2F5A:
2F5A  FF 76 0A        push word ptr [bp + 0xa]
2F5D  FF 76 08        push word ptr [bp + 8]
2F60  FF 76 06        push word ptr [bp + 6]
2F63  0E              push cs
2F64  E8 7E FF        call 0x2ee5
2F67  C4 7E FC        les di, ptr [bp - 4]
2F6A  26 8A 45 06     mov al, byte ptr es:[di + 6]
2F6E  30 E4           xor ah, ah
2F70  8B F8           mov di, ax
2F72  8A 85 9A 69     mov al, byte ptr [di + 0x699a]
2F76  50              push ax
2F77  8D BE FC FE     lea di, [bp - 0x104]
2F7B  16              push ss
2F7C  57              push di
2F7D  C4 7E FC        les di, ptr [bp - 4]
2F80  26 8A 45 06     mov al, byte ptr es:[di + 6]
2F84  30 E4           xor ah, ah
2F86  8B F8           mov di, ax
2F88  8A 85 A8 69     mov al, byte ptr [di + 0x69a8]
2F8C  50              push ax
2F8D  9A 5A 07 E4 23  call far 23E4:075A
2F92  8A 46 08        mov al, byte ptr [bp + 8]
2F95  50              push ax
2F96  8B 46 06        mov ax, word ptr [bp + 6]
2F99  05 0D 00        add ax, 0xd
2F9C  50              push ax
2F9D  BF 6E A9        mov di, 0xa96e
2FA0  1E              push ds
2FA1  57              push di
2FA2  9A C8 02 4B 21  call far 214B:02C8
loc_2FA7:
2FA7  89 EC           mov sp, bp
2FA9  5D              pop bp
2FAA  CA 06 00        retf 6

; ---- routine 1771:2FAD  (found by: call, far)
sub_2FAD:
2FAD  55              push bp
2FAE  89 E5           mov bp, sp
2FB0  83 EC 06        sub sp, 6
2FB3  8B 46 06        mov ax, word ptr [bp + 6]
2FB6  BA 14 00        mov dx, 0x14
2FB9  F7 E2           mul dx
2FBB  C4 3E 1B A9     les di, ptr [0xa91b]
2FBF  03 F8           add di, ax
2FC1  89 7E FA        mov word ptr [bp - 6], di
2FC4  8C 46 FC        mov word ptr [bp - 4], es
2FC7  8B 46 06        mov ax, word ptr [bp + 6]
2FCA  31 D2           xor dx, dx
2FCC  B9 0C 00        mov cx, 0xc
2FCF  F7 F1           div cx
2FD1  92              xchg dx, ax
2FD2  8B F8           mov di, ax
2FD4  8A 85 54 0E     mov al, byte ptr [di + 0xe54]
2FD8  30 E4           xor ah, ah
2FDA  8B D0           mov dx, ax
2FDC  C4 7E FA        les di, ptr [bp - 6]
2FDF  26 8A 45 07     mov al, byte ptr es:[di + 7]
2FE3  30 E4           xor ah, ah
2FE5  8B F8           mov di, ax
2FE7  8A 85 46 0E     mov al, byte ptr [di + 0xe46]
2FEB  30 E4           xor ah, ah
2FED  03 C2           add ax, dx
2FEF  89 46 FE        mov word ptr [bp - 2], ax
2FF2  8B 46 FE        mov ax, word ptr [bp - 2]
2FF5  89 EC           mov sp, bp
2FF7  5D              pop bp
2FF8  CA 02 00        retf 2

; ---- routine 1771:2FFB  (found by: call, far)
sub_2FFB:
2FFB  55              push bp
2FFC  89 E5           mov bp, sp
2FFE  83 EC 06        sub sp, 6
3001  8B 46 06        mov ax, word ptr [bp + 6]
3004  BA 14 00        mov dx, 0x14
3007  F7 E2           mul dx
3009  C4 3E 1B A9     les di, ptr [0xa91b]
300D  03 F8           add di, ax
300F  89 7E FB        mov word ptr [bp - 5], di
3012  8C 46 FD        mov word ptr [bp - 3], es
3015  C4 7E FB        les di, ptr [bp - 5]
3018  26 8A 45 03     mov al, byte ptr es:[di + 3]
301C  D0 E8           shr al, 1
301E  72 04           jb 0x3024
3020  B0 00           mov al, 0
3022  EB 02           jmp 0x3026
loc_3024:
3024  B0 01           mov al, 1
loc_3026:
3026  30 E4           xor ah, ah
3028  8B D0           mov dx, ax
302A  C4 7E FB        les di, ptr [bp - 5]
302D  26 8A 45 05     mov al, byte ptr es:[di + 5]
3031  30 E4           xor ah, ah
3033  2B C2           sub ax, dx
3035  88 46 FF        mov byte ptr [bp - 1], al
3038  8A 46 FF        mov al, byte ptr [bp - 1]
303B  89 EC           mov sp, bp
303D  5D              pop bp
303E  CA 02 00        retf 2

