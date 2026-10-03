; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 7 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:544D  (found by: call)
sub_544D:
544D  55              push bp
544E  89 E5           mov bp, sp
5450  8B 7E 04        mov di, word ptr [bp + 4]
5453  36 80 7D F4 00  cmp byte ptr ss:[di - 0xc], 0
5458  75 03           jne 0x545d
545A  E9 8D 00        jmp 0x54ea
loc_545D:
545D  B8 03 00        mov ax, 3
5460  50              push ax
5461  9A B1 06 4B 21  call far 214B:06B1
5466  3D 01 00        cmp ax, 1
5469  75 23           jne 0x548e
546B  8B 7E 04        mov di, word ptr [bp + 4]
546E  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
5472  BA 0B 00        mov dx, 0xb
5475  F7 E2           mul dx
5477  C4 3E 6C 9B     les di, ptr [0x9b6c]
547B  03 F8           add di, ax
547D  06              push es
547E  57              push di
547F  BF 29 54        mov di, 0x5429
5482  0E              push cs
5483  57              push di
5484  BF 37 54        mov di, 0x5437
5487  0E              push cs
5488  57              push di
5489  E8 D3 B2        call 0x75f
548C  EB 5C           jmp 0x54ea
loc_548E:
548E  3D 02 00        cmp ax, 2
5491  75 23           jne 0x54b6
5493  8B 7E 04        mov di, word ptr [bp + 4]
5496  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
549A  BA 0B 00        mov dx, 0xb
549D  F7 E2           mul dx
549F  C4 3E 6C 9B     les di, ptr [0x9b6c]
54A3  03 F8           add di, ax
54A5  06              push es
54A6  57              push di
54A7  BF 38 54        mov di, 0x5438
54AA  0E              push cs
54AB  57              push di
54AC  BF 37 54        mov di, 0x5437
54AF  0E              push cs
54B0  57              push di
54B1  E8 AB B2        call 0x75f
54B4  EB 34           jmp 0x54ea
loc_54B6:
54B6  3D 03 00        cmp ax, 3
54B9  75 2F           jne 0x54ea
54BB  8B 7E 04        mov di, word ptr [bp + 4]
54BE  36 8B 45 04     mov ax, word ptr ss:[di + 4]
54C2  B1 04           mov cl, 4
54C4  D3 E0           shl ax, cl
54C6  C4 3E 68 9B     les di, ptr [0x9b68]
54CA  03 F8           add di, ax
54CC  06              push es
54CD  57              push di
54CE  BF 47 54        mov di, 0x5447
54D1  0E              push cs
54D2  57              push di
54D3  8B 7E 04        mov di, word ptr [bp + 4]
54D6  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
54DA  BA 0B 00        mov dx, 0xb
54DD  F7 E2           mul dx
54DF  C4 3E 6C 9B     les di, ptr [0x9b6c]
54E3  03 F8           add di, ax
54E5  06              push es
54E6  57              push di
54E7  E8 75 B2        call 0x75f
loc_54EA:
54EA  89 EC           mov sp, bp
54EC  5D              pop bp
54ED  C2 02 00        ret 2

; ---- routine 000E:54F0  (found by: call)
sub_54F0:
54F0  55              push bp
54F1  89 E5           mov bp, sp
54F3  83 EC 10        sub sp, 0x10
54F6  8B 7E 04        mov di, word ptr [bp + 4]
54F9  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
54FD  BA 14 00        mov dx, 0x14
5500  F7 E2           mul dx
5502  C4 3E 1B A9     les di, ptr [0xa91b]
5506  03 F8           add di, ax
5508  89 7E F8        mov word ptr [bp - 8], di
550B  8C 46 FA        mov word ptr [bp - 6], es
550E  8B 7E 04        mov di, word ptr [bp + 4]
5511  36 FF 75 F7     push word ptr ss:[di - 9]
5515  8B 7E 04        mov di, word ptr [bp + 4]
5518  36 FF 75 04     push word ptr ss:[di + 4]
551C  8B 46 06        mov ax, word ptr [bp + 6]
551F  BA 14 00        mov dx, 0x14
5522  F7 E2           mul dx
5524  C4 3E 1B A9     les di, ptr [0xa91b]
5528  03 F8           add di, ax
552A  26 8A 45 07     mov al, byte ptr es:[di + 7]
552E  30 E4           xor ah, ah
5530  50              push ax
5531  B0 01           mov al, 1
5533  50              push ax
5534  9A D3 96 71 17  call far 1771:96D3
5539  B8 06 00        mov ax, 6
553C  50              push ax
553D  9A B1 06 4B 21  call far 214B:06B1
5542  50              push ax
5543  B8 06 00        mov ax, 6
5546  50              push ax
5547  9A B1 06 4B 21  call far 214B:06B1
554C  8B D0           mov dx, ax
554E  C4 7E F8        les di, ptr [bp - 8]
5551  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
5556  74 04           je 0x555c
5558  B0 00           mov al, 0
555A  EB 02           jmp 0x555e
loc_555C:
555C  B0 01           mov al, 1
loc_555E:
555E  98              cwde
555F  8B F8           mov di, ax
5561  8A 85 78 00     mov al, byte ptr [di + 0x78]
5565  30 E4           xor ah, ah
5567  03 C2           add ax, dx
5569  5A              pop dx
556A  2B C2           sub ax, dx
556C  C4 7E F8        les di, ptr [bp - 8]
556F  26 88 45 01     mov byte ptr es:[di + 1], al
5573  8B 7E 04        mov di, word ptr [bp + 4]
5576  36 FF 75 F7     push word ptr ss:[di - 9]
557A  9A EB 32 71 17  call far 1771:32EB
557F  C4 7E F8        les di, ptr [bp - 8]
5582  31 C0           xor ax, ax
5584  26 89 45 08     mov word ptr es:[di + 8], ax
5588  C4 7E F8        les di, ptr [bp - 8]
558B  31 C0           xor ax, ax
558D  26 89 45 0A     mov word ptr es:[di + 0xa], ax
5591  C4 7E F8        les di, ptr [bp - 8]
5594  26 C6 45 10 00  mov byte ptr es:[di + 0x10], 0
5599  9A 00 00 71 17  call far 1771:0000
559E  8A D0           mov dl, al
55A0  8B 7E 04        mov di, word ptr [bp + 4]
55A3  36 8B 45 F7     mov ax, word ptr ss:[di - 9]
55A7  C4 3E 70 9B     les di, ptr [0x9b70]
55AB  03 F8           add di, ax
55AD  26 88 15        mov byte ptr es:[di], dl
55B0  31 C0           xor ax, ax
55B2  89 46 FE        mov word ptr [bp - 2], ax
55B5  C7 46 FC 01 00  mov word ptr [bp - 4], 1
55BA  EB 03           jmp 0x55bf
loc_55BC:
55BC  FF 46 FC        inc word ptr [bp - 4]
loc_55BF:
55BF  8B 7E 04        mov di, word ptr [bp + 4]
55C2  36 8B 45 04     mov ax, word ptr ss:[di + 4]
55C6  BA BF 00        mov dx, 0xbf
55C9  F7 E2           mul dx
55CB  C4 3E 17 A9     les di, ptr [0xa917]
55CF  03 F8           add di, ax
55D1  89 7E F4        mov word ptr [bp - 0xc], di
55D4  8C 46 F6        mov word ptr [bp - 0xa], es
55D7  8B 46 FC        mov ax, word ptr [bp - 4]
55DA  D1 E0           shl ax, 1
55DC  C4 7E F4        les di, ptr [bp - 0xc]
55DF  03 F8           add di, ax
55E1  26 8B 45 FE     mov ax, word ptr es:[di - 2]
55E5  BA 14 00        mov dx, 0x14
55E8  F7 E2           mul dx
55EA  C4 3E 1B A9     les di, ptr [0xa91b]
55EE  03 F8           add di, ax
55F0  89 7E F0        mov word ptr [bp - 0x10], di
55F3  8C 46 F2        mov word ptr [bp - 0xe], es
55F6  C4 7E F0        les di, ptr [bp - 0x10]
55F9  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
55FE  74 04           je 0x5604
5600  B0 00           mov al, 0
5602  EB 02           jmp 0x5606
loc_5604:
5604  B0 01           mov al, 1
loc_5606:
5606  98              cwde
5607  8B F8           mov di, ax
5609  8A 85 76 00     mov al, byte ptr [di + 0x76]
560D  30 E4           xor ah, ah
560F  05 04 00        add ax, 4
5612  8B D0           mov dx, ax
5614  C4 7E F0        les di, ptr [bp - 0x10]
5617  26 8A 45 01     mov al, byte ptr es:[di + 1]
561B  30 E4           xor ah, ah
561D  3B C2           cmp ax, dx
561F  7D 03           jge 0x5624
5621  FF 46 FE        inc word ptr [bp - 2]
loc_5624:
5624  83 7E FC 14     cmp word ptr [bp - 4], 0x14
5628  75 92           jne 0x55bc
562A  8B 7E 04        mov di, word ptr [bp + 4]
562D  36 8B 7D F9     mov di, word ptr ss:[di - 7]
5631  D1 E7           shl di, 1
5633  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
5637  05 4F 00        add ax, 0x4f
563A  89 46 F6        mov word ptr [bp - 0xa], ax
563D  8B 7E 04        mov di, word ptr [bp + 4]
5640  36 8B 7D F9     mov di, word ptr ss:[di - 7]
5644  D1 E7           shl di, 1
5646  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
564A  3B 46 F6        cmp ax, word ptr [bp - 0xa]
564D  77 5D           ja 0x56ac
564F  89 46 FC        mov word ptr [bp - 4], ax
5652  EB 03           jmp 0x5657
loc_5654:
5654  FF 46 FC        inc word ptr [bp - 4]
loc_5657:
5657  8B 46 FC        mov ax, word ptr [bp - 4]
565A  D1 E0           shl ax, 1
565C  C4 3E 27 A9     les di, ptr [0xa927]
5660  03 F8           add di, ax
5662  26 8B 05        mov ax, word ptr es:[di]
5665  BA 14 00        mov dx, 0x14
5668  F7 E2           mul dx
566A  C4 3E 1B A9     les di, ptr [0xa91b]
566E  03 F8           add di, ax
5670  89 7E F2        mov word ptr [bp - 0xe], di
5673  8C 46 F4        mov word ptr [bp - 0xc], es
5676  C4 7E F2        les di, ptr [bp - 0xe]
5679  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
567E  74 04           je 0x5684
5680  B0 00           mov al, 0
5682  EB 02           jmp 0x5686
loc_5684:
5684  B0 01           mov al, 1
loc_5686:
5686  98              cwde
5687  8B F8           mov di, ax
5689  8A 85 76 00     mov al, byte ptr [di + 0x76]
568D  30 E4           xor ah, ah
568F  05 04 00        add ax, 4
5692  8B D0           mov dx, ax
5694  C4 7E F2        les di, ptr [bp - 0xe]
5697  26 8A 45 01     mov al, byte ptr es:[di + 1]
569B  30 E4           xor ah, ah
569D  3B C2           cmp ax, dx
569F  7D 03           jge 0x56a4
56A1  FF 46 FE        inc word ptr [bp - 2]
loc_56A4:
56A4  8B 46 FC        mov ax, word ptr [bp - 4]
56A7  3B 46 F6        cmp ax, word ptr [bp - 0xa]
56AA  75 A8           jne 0x5654
loc_56AC:
56AC  83 7E FE 14     cmp word ptr [bp - 2], 0x14
56B0  72 02           jb 0x56b4
56B2  EB 39           jmp 0x56ed
loc_56B4:
56B4  B8 03 00        mov ax, 3
56B7  50              push ax
56B8  9A B1 06 4B 21  call far 214B:06B1
56BD  8B D0           mov dx, ax
56BF  C4 7E F8        les di, ptr [bp - 8]
56C2  26 80 7D 07 00  cmp byte ptr es:[di + 7], 0
56C7  74 04           je 0x56cd
56C9  B0 00           mov al, 0
56CB  EB 02           jmp 0x56cf
loc_56CD:
56CD  B0 01           mov al, 1
loc_56CF:
56CF  98              cwde
56D0  8B F8           mov di, ax
56D2  8A 85 76 00     mov al, byte ptr [di + 0x76]
56D6  30 E4           xor ah, ah
56D8  03 C2           add ax, dx
56DA  C4 7E F8        les di, ptr [bp - 8]
56DD  26 88 45 01     mov byte ptr es:[di + 1], al
56E1  8B 7E 04        mov di, word ptr [bp + 4]
56E4  36 FF 75 F7     push word ptr ss:[di - 9]
56E8  9A EB 32 71 17  call far 1771:32EB
loc_56ED:
56ED  89 EC           mov sp, bp
56EF  5D              pop bp
56F0  C2 04 00        ret 4

; ---- routine 000E:56F3  (found by: call)
sub_56F3:
56F3  55              push bp
56F4  89 E5           mov bp, sp
56F6  8A 46 06        mov al, byte ptr [bp + 6]
56F9  8B 7E 04        mov di, word ptr [bp + 4]
56FC  36 88 45 FF     mov byte ptr ss:[di - 1], al
5700  8B 7E 04        mov di, word ptr [bp + 4]
5703  36 8B 45 F9     mov ax, word ptr ss:[di - 7]
5707  C4 3E 23 A9     les di, ptr [0xa923]
570B  03 F8           add di, ax
570D  26 C6 45 4D 01  mov byte ptr es:[di + 0x4d], 1
5712  80 7E 06 00     cmp byte ptr [bp + 6], 0
5716  74 09           je 0x5721
5718  FF 76 08        push word ptr [bp + 8]
571B  FF 76 04        push word ptr [bp + 4]
571E  E8 B3 F9        call 0x50d4
loc_5721:
5721  FF 76 08        push word ptr [bp + 8]
5724  8B 7E 04        mov di, word ptr [bp + 4]
5727  36 FF 75 F9     push word ptr ss:[di - 7]
572B  B0 01           mov al, 1
572D  50              push ax
572E  9A 2E 1B 71 17  call far 1771:1B2E
5733  FF 76 08        push word ptr [bp + 8]
5736  8B 7E 04        mov di, word ptr [bp + 4]
5739  36 FF 75 F9     push word ptr ss:[di - 7]
573D  B0 00           mov al, 0
573F  50              push ax
5740  9A 2E 1B 71 17  call far 1771:1B2E
5745  9A F7 4C 71 17  call far 1771:4CF7
574A  8B 7E 04        mov di, word ptr [bp + 4]
574D  36 89 45 F7     mov word ptr ss:[di - 9], ax
5751  8B 7E 04        mov di, word ptr [bp + 4]
5754  36 80 7D F3 00  cmp byte ptr ss:[di - 0xd], 0
5759  74 1B           je 0x5776
575B  8B 7E 04        mov di, word ptr [bp + 4]
575E  36 8B 55 F7     mov dx, word ptr ss:[di - 9]
5762  8B 7E 04        mov di, word ptr [bp + 4]
5765  36 8B 45 FD     mov ax, word ptr ss:[di - 3]
5769  D1 E0           shl ax, 1
576B  C4 3E 27 A9     les di, ptr [0xa927]
576F  03 F8           add di, ax
5771  26 89 15        mov word ptr es:[di], dx
5774  EB 2A           jmp 0x57a0
loc_5776:
5776  8B 7E 04        mov di, word ptr [bp + 4]
5779  36 8B 5D F7     mov bx, word ptr ss:[di - 9]
577D  8B 7E 04        mov di, word ptr [bp + 4]
5780  36 8B 45 FD     mov ax, word ptr ss:[di - 3]
5784  D1 E0           shl ax, 1
5786  8B C8           mov cx, ax
5788  8B 7E 04        mov di, word ptr [bp + 4]
578B  36 8B 45 04     mov ax, word ptr ss:[di + 4]
578F  BA BF 00        mov dx, 0xbf
5792  F7 E2           mul dx
5794  C4 3E 17 A9     les di, ptr [0xa917]
5798  03 F8           add di, ax
579A  03 F9           add di, cx
579C  26 89 5D FE     mov word ptr es:[di - 2], bx
loc_57A0:
57A0  FF 76 08        push word ptr [bp + 8]
57A3  FF 76 04        push word ptr [bp + 4]
57A6  E8 47 FD        call 0x54f0
57A9  8B 46 08        mov ax, word ptr [bp + 8]
57AC  BA 14 00        mov dx, 0x14
57AF  F7 E2           mul dx
57B1  C4 3E 1B A9     les di, ptr [0xa91b]
57B5  03 F8           add di, ax
57B7  06              push es
57B8  57              push di
57B9  B8 14 00        mov ax, 0x14
57BC  50              push ax
57BD  31 C0           xor ax, ax
57BF  50              push ax
57C0  9A 18 00 4B 21  call far 214B:0018
57C5  80 7E 06 00     cmp byte ptr [bp + 6], 0
57C9  75 02           jne 0x57cd
57CB  EB 12           jmp 0x57df
loc_57CD:
57CD  FF 76 04        push word ptr [bp + 4]
57D0  E8 7A FC        call 0x544d
57D3  B0 00           mov al, 0
57D5  50              push ax
57D6  B0 00           mov al, 0
57D8  50              push ax
57D9  B0 00           mov al, 0
57DB  50              push ax
57DC  E8 17 AE        call 0x5f6
loc_57DF:
57DF  89 EC           mov sp, bp
57E1  5D              pop bp
57E2  C2 06 00        ret 6

; ---- routine 000E:57E5  (found by: call)
sub_57E5:
57E5  55              push bp
57E6  89 E5           mov bp, sp
57E8  83 EC 16        sub sp, 0x16
57EB  8B 46 04        mov ax, word ptr [bp + 4]
57EE  BA BF 00        mov dx, 0xbf
57F1  F7 E2           mul dx
57F3  C4 3E 17 A9     les di, ptr [0xa917]
57F7  03 F8           add di, ax
57F9  89 7E EF        mov word ptr [bp - 0x11], di
57FC  8C 46 F1        mov word ptr [bp - 0xf], es
57FF  C4 3E 23 A9     les di, ptr [0xa923]
5803  89 7E EB        mov word ptr [bp - 0x15], di
5806  8C 46 ED        mov word ptr [bp - 0x13], es
5809  C4 7E EB        les di, ptr [bp - 0x15]
580C  26 83 7D 38 00  cmp word ptr es:[di + 0x38], 0
5811  74 18           je 0x582b
5813  C4 7E EF        les di, ptr [bp - 0x11]
5816  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
581A  30 E4           xor ah, ah
581C  2D 80 00        sub ax, 0x80
581F  C4 7E EB        les di, ptr [bp - 0x15]
5822  03 F8           add di, ax
5824  26 80 7D 4D 00  cmp byte ptr es:[di + 0x4d], 0
5829  74 07           je 0x5832
loc_582B:
582B  C6 46 FF 00     mov byte ptr [bp - 1], 0
582F  E9 1A 01        jmp 0x594c
loc_5832:
5832  C4 7E EF        les di, ptr [bp - 0x11]
5835  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
5839  30 E4           xor ah, ah
583B  2D 80 00        sub ax, 0x80
583E  89 46 F9        mov word ptr [bp - 7], ax
5841  C6 46 FF 01     mov byte ptr [bp - 1], 1
5845  C6 46 F3 00     mov byte ptr [bp - 0xd], 0
5849  8B 46 F9        mov ax, word ptr [bp - 7]
584C  C4 7E EB        les di, ptr [bp - 0x15]
584F  03 F8           add di, ax
5851  26 80 7D 13 00  cmp byte ptr es:[di + 0x13], 0
5856  75 4B           jne 0x58a3
5858  FF 76 04        push word ptr [bp + 4]
585B  9A 38 DB 91 07  call far 0791:DB38
5860  08 C0           or al, al
5862  75 3F           jne 0x58a3
5864  C7 46 FD 01 00  mov word ptr [bp - 3], 1
5869  EB 03           jmp 0x586e
loc_586B:
586B  FF 46 FD        inc word ptr [bp - 3]
loc_586E:
586E  8B 46 FD        mov ax, word ptr [bp - 3]
5871  D1 E0           shl ax, 1
5873  C4 7E EF        les di, ptr [bp - 0x11]
5876  03 F8           add di, ax
5878  26 FF 75 FE     push word ptr es:[di - 2]
587C  9A 40 7F 71 17  call far 1771:7F40
5881  08 C0           or al, al
5883  74 18           je 0x589d
5885  8B 46 FD        mov ax, word ptr [bp - 3]
5888  D1 E0           shl ax, 1
588A  C4 7E EF        les di, ptr [bp - 0x11]
588D  03 F8           add di, ax
588F  26 FF 75 FE     push word ptr es:[di - 2]
5893  B0 01           mov al, 1
5895  50              push ax
5896  55              push bp
5897  E8 59 FE        call 0x56f3
589A  E9 AF 00        jmp 0x594c
loc_589D:
589D  83 7E FD 14     cmp word ptr [bp - 3], 0x14
58A1  75 C8           jne 0x586b
loc_58A3:
58A3  C6 46 F3 01     mov byte ptr [bp - 0xd], 1
58A7  B8 50 00        mov ax, 0x50
58AA  50              push ax
58AB  9A B1 06 4B 21  call far 214B:06B1
58B0  99              cdq
58B1  8B C8           mov cx, ax
58B3  8B DA           mov bx, dx
58B5  8B 7E F9        mov di, word ptr [bp - 7]
58B8  D1 E7           shl di, 1
58BA  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
58BE  48              dec ax
58BF  31 D2           xor dx, dx
58C1  03 C1           add ax, cx
58C3  13 D3           adc dx, bx
58C5  89 46 F5        mov word ptr [bp - 0xb], ax
58C8  8B 46 F5        mov ax, word ptr [bp - 0xb]
58CB  89 46 FD        mov word ptr [bp - 3], ax
loc_58CE:
58CE  8B 46 FD        mov ax, word ptr [bp - 3]
58D1  D1 E0           shl ax, 1
58D3  C4 3E 27 A9     les di, ptr [0xa927]
58D7  03 F8           add di, ax
58D9  26 FF 35        push word ptr es:[di]
58DC  9A 40 7F 71 17  call far 1771:7F40
58E1  08 C0           or al, al
58E3  74 3B           je 0x5920
58E5  8B 46 FD        mov ax, word ptr [bp - 3]
58E8  D1 E0           shl ax, 1
58EA  C4 3E 27 A9     les di, ptr [0xa927]
58EE  03 F8           add di, ax
58F0  26 FF 35        push word ptr es:[di]
58F3  8B 46 FD        mov ax, word ptr [bp - 3]
58F6  D1 E0           shl ax, 1
58F8  C4 3E 27 A9     les di, ptr [0xa927]
58FC  03 F8           add di, ax
58FE  26 8B 05        mov ax, word ptr es:[di]
5901  BA 14 00        mov dx, 0x14
5904  F7 E2           mul dx
5906  C4 3E 1B A9     les di, ptr [0xa91b]
590A  03 F8           add di, ax
590C  26 83 7D 08 00  cmp word ptr es:[di + 8], 0
5911  77 04           ja 0x5917
5913  B0 00           mov al, 0
5915  EB 02           jmp 0x5919
loc_5917:
5917  B0 01           mov al, 1
loc_5919:
5919  50              push ax
591A  55              push bp
591B  E8 D5 FD        call 0x56f3
591E  EB 2C           jmp 0x594c
loc_5920:
5920  FF 46 FD        inc word ptr [bp - 3]
5923  8B 7E F9        mov di, word ptr [bp - 7]
5926  D1 E7           shl di, 1
5928  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
592C  05 4F 00        add ax, 0x4f
592F  3B 46 FD        cmp ax, word ptr [bp - 3]
5932  73 0C           jae 0x5940
5934  8B 7E F9        mov di, word ptr [bp - 7]
5937  D1 E7           shl di, 1
5939  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
593D  89 46 FD        mov word ptr [bp - 3], ax
loc_5940:
5940  8B 46 FD        mov ax, word ptr [bp - 3]
5943  3B 46 F5        cmp ax, word ptr [bp - 0xb]
5946  75 86           jne 0x58ce
5948  C6 46 FF 00     mov byte ptr [bp - 1], 0
loc_594C:
594C  8A 46 FF        mov al, byte ptr [bp - 1]
594F  89 EC           mov sp, bp
5951  5D              pop bp
5952  C2 02 00        ret 2
; data (not reached as code), 35 bytes
5955                  pstr 'THE WORLD CUP'
5963                  pstr 'THE '
5968                  db 01 20   ; . 
596A                  pstr 'CHAMPIONSHIPS'

; ---- routine 000E:5978  (found by: call)
sub_5978:
5978  55              push bp
5979  89 E5           mov bp, sp
597B  81 EC 04 02     sub sp, 0x204
597F  C4 3E 23 A9     les di, ptr [0xa923]
5983  89 7E FC        mov word ptr [bp - 4], di
5986  8C 46 FE        mov word ptr [bp - 2], es
5989  C4 7E FC        les di, ptr [bp - 4]
598C  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
5991  74 0D           je 0x59a0
5993  FF 76 06        push word ptr [bp + 6]
5996  BF 55 59        mov di, 0x5955
5999  0E              push cs
599A  57              push di
599B  E8 6D AD        call 0x70b
599E  EB 77           jmp 0x5a17
loc_59A0:
59A0  FF 76 06        push word ptr [bp + 6]
59A3  8D BE FC FD     lea di, [bp - 0x204]
59A7  16              push ss
59A8  57              push di
59A9  BF 63 59        mov di, 0x5963
59AC  0E              push cs
59AD  57              push di
59AE  9A 2A 06 E4 23  call far 23E4:062A
59B3  8D BE FC FE     lea di, [bp - 0x104]
59B7  16              push ss
59B8  57              push di
59B9  C4 7E FC        les di, ptr [bp - 4]
59BC  26 8B 45 38     mov ax, word ptr es:[di + 0x38]
59C0  D1 E0           shl ax, 1
59C2  C4 7E FC        les di, ptr [bp - 4]
59C5  26 03 45 3A     add ax, word ptr es:[di + 0x3a]
59C9  31 D2           xor dx, dx
59CB  52              push dx
59CC  50              push ax
59CD  9A DA 09 4B 21  call far 214B:09DA
59D2  9A B7 06 E4 23  call far 23E4:06B7
59D7  BF 68 59        mov di, 0x5968
59DA  0E              push cs
59DB  57              push di
59DC  9A B7 06 E4 23  call far 23E4:06B7
59E1  8B 46 04        mov ax, word ptr [bp + 4]
59E4  BA BF 00        mov dx, 0xbf
59E7  F7 E2           mul dx
59E9  C4 3E 17 A9     les di, ptr [0xa917]
59ED  03 F8           add di, ax
59EF  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
59F3  30 E4           xor ah, ah
59F5  BA 0B 00        mov dx, 0xb
59F8  F7 E2           mul dx
59FA  8B F8           mov di, ax
59FC  81 C7 FF 68     add di, 0x68ff
5A00  1E              push ds
5A01  57              push di
5A02  9A B7 06 E4 23  call far 23E4:06B7
5A07  E8 01 AD        call 0x70b
5A0A  8B 46 06        mov ax, word ptr [bp + 6]
5A0D  40              inc ax
5A0E  50              push ax
5A0F  BF 6A 59        mov di, 0x596a
5A12  0E              push cs
5A13  57              push di
5A14  E8 F4 AC        call 0x70b
loc_5A17:
5A17  89 EC           mov sp, bp
5A19  5D              pop bp
5A1A  C2 04 00        ret 4
; data (not reached as code), 168 bytes
5A1D                  pstr 'PREPARE TO'
5A28                  pstr 'GET READY TO'
5A35                  pstr 'GET ORGANISED TO'
5A46                  pstr 'HOST'
5A4B                  pstr 'LEAVE FOR'
5A55                  pstr 'SET OFF TO'
5A60                  pstr 'TRAVEL TO'
5A6A                  pstr ' FOR'
5A6F                  pstr 'THE FINALS OF'
5A7D                  pstr 'SQUAD FOR'
5A87                  pstr 'TO BE ANNOUNCED'
5A97                  pstr 'THOUGHT ABOUT THE'
5AA9                  pstr 'FOUND THE BEST'
5AB8                  pstr 'HAS '
5ABD                  pstr 'SQUAD ?'

; ---- routine 000E:5AC5  (found by: call)
sub_5AC5:
5AC5  55              push bp
5AC6  89 E5           mov bp, sp
5AC8  81 EC 22 02     sub sp, 0x222
5ACC  C4 3E 23 A9     les di, ptr [0xa923]
5AD0  89 7E E3        mov word ptr [bp - 0x1d], di
5AD3  8C 46 E5        mov word ptr [bp - 0x1b], es
5AD6  8B 7E 04        mov di, word ptr [bp + 4]
5AD9  36 8B 45 04     mov ax, word ptr ss:[di + 4]
5ADD  BA BF 00        mov dx, 0xbf
5AE0  F7 E2           mul dx
5AE2  C4 3E 17 A9     les di, ptr [0xa917]
5AE6  03 F8           add di, ax
5AE8  89 7E DF        mov word ptr [bp - 0x21], di
5AEB  8C 46 E1        mov word ptr [bp - 0x1f], es
5AEE  C4 7E E3        les di, ptr [bp - 0x1d]
5AF1  26 8A 45 01     mov al, byte ptr es:[di + 1]
5AF5  30 E4           xor ah, ah
5AF7  C4 7E E3        les di, ptr [bp - 0x1d]
5AFA  03 F8           add di, ax
5AFC  26 C6 45 41 01  mov byte ptr es:[di + 0x41], 1
5B01  C4 7E E3        les di, ptr [bp - 0x1d]
5B04  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
5B09  74 0C           je 0x5b17
5B0B  C4 7E E3        les di, ptr [bp - 0x1d]
5B0E  26 8B 45 36     mov ax, word ptr es:[di + 0x36]
5B12  89 46 FC        mov word ptr [bp - 4], ax
5B15  EB 17           jmp 0x5b2e
loc_5B17:
5B17  C4 7E DF        les di, ptr [bp - 0x21]
5B1A  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
5B1E  30 E4           xor ah, ah
5B20  D1 E0           shl ax, 1
5B22  C4 7E E3        les di, ptr [bp - 0x1d]
5B25  03 F8           add di, ax
5B27  26 8B 45 2C     mov ax, word ptr es:[di + 0x2c]
5B2B  89 46 FC        mov word ptr [bp - 4], ax
loc_5B2E:
5B2E  E8 5D A8        call 0x38e
5B31  B8 01 00        mov ax, 1
5B34  50              push ax
5B35  8B 7E 04        mov di, word ptr [bp + 4]
5B38  36 8B 45 04     mov ax, word ptr ss:[di + 4]
5B3C  B1 04           mov cl, 4
5B3E  D3 E0           shl ax, cl
5B40  C4 3E 68 9B     les di, ptr [0x9b68]
5B44  03 F8           add di, ax
5B46  06              push es
5B47  57              push di
5B48  E8 C0 AB        call 0x70b
5B4B  B8 03 00        mov ax, 3
5B4E  50              push ax
5B4F  9A B1 06 4B 21  call far 214B:06B1
5B54  3D 01 00        cmp ax, 1
5B57  75 0E           jne 0x5b67
5B59  B8 02 00        mov ax, 2
5B5C  50              push ax
5B5D  BF 1D 5A        mov di, 0x5a1d
5B60  0E              push cs
5B61  57              push di
5B62  E8 A6 AB        call 0x70b
5B65  EB 24           jmp 0x5b8b
loc_5B67:
5B67  3D 02 00        cmp ax, 2
5B6A  75 0E           jne 0x5b7a
5B6C  B8 02 00        mov ax, 2
5B6F  50              push ax
5B70  BF 28 5A        mov di, 0x5a28
5B73  0E              push cs
5B74  57              push di
5B75  E8 93 AB        call 0x70b
5B78  EB 11           jmp 0x5b8b
loc_5B7A:
5B7A  3D 03 00        cmp ax, 3
5B7D  75 0C           jne 0x5b8b
5B7F  B8 02 00        mov ax, 2
5B82  50              push ax
5B83  BF 35 5A        mov di, 0x5a35
5B86  0E              push cs
5B87  57              push di
5B88  E8 80 AB        call 0x70b
loc_5B8B:
5B8B  8B 46 FC        mov ax, word ptr [bp - 4]
5B8E  8B 7E 04        mov di, word ptr [bp + 4]
5B91  36 3B 45 04     cmp ax, word ptr ss:[di + 4]
5B95  75 13           jne 0x5baa
5B97  B8 03 00        mov ax, 3
5B9A  50              push ax
5B9B  BF 46 5A        mov di, 0x5a46
5B9E  0E              push cs
5B9F  57              push di
5BA0  E8 68 AB        call 0x70b
5BA3  C7 46 FE 04 00  mov word ptr [bp - 2], 4
5BA8  EB 70           jmp 0x5c1a
loc_5BAA:
5BAA  B8 03 00        mov ax, 3
5BAD  50              push ax
5BAE  9A B1 06 4B 21  call far 214B:06B1
5BB3  3D 01 00        cmp ax, 1
5BB6  75 0E           jne 0x5bc6
5BB8  B8 03 00        mov ax, 3
5BBB  50              push ax
5BBC  BF 4B 5A        mov di, 0x5a4b
5BBF  0E              push cs
5BC0  57              push di
5BC1  E8 47 AB        call 0x70b
5BC4  EB 24           jmp 0x5bea
loc_5BC6:
5BC6  3D 02 00        cmp ax, 2
5BC9  75 0E           jne 0x5bd9
5BCB  B8 03 00        mov ax, 3
5BCE  50              push ax
5BCF  BF 55 5A        mov di, 0x5a55
5BD2  0E              push cs
5BD3  57              push di
5BD4  E8 34 AB        call 0x70b
5BD7  EB 11           jmp 0x5bea
loc_5BD9:
5BD9  3D 03 00        cmp ax, 3
5BDC  75 0C           jne 0x5bea
5BDE  B8 03 00        mov ax, 3
5BE1  50              push ax
5BE2  BF 60 5A        mov di, 0x5a60
5BE5  0E              push cs
5BE6  57              push di
5BE7  E8 21 AB        call 0x70b
loc_5BEA:
5BEA  B8 04 00        mov ax, 4
5BED  50              push ax
5BEE  8D BE DF FE     lea di, [bp - 0x121]
5BF2  16              push ss
5BF3  57              push di
5BF4  8B 46 FC        mov ax, word ptr [bp - 4]
5BF7  B1 04           mov cl, 4
5BF9  D3 E0           shl ax, cl
5BFB  C4 3E 68 9B     les di, ptr [0x9b68]
5BFF  03 F8           add di, ax
5C01  06              push es
5C02  57              push di
5C03  9A 2A 06 E4 23  call far 23E4:062A
5C08  BF 6A 5A        mov di, 0x5a6a
5C0B  0E              push cs
5C0C  57              push di
5C0D  9A B7 06 E4 23  call far 23E4:06B7
5C12  E8 F6 AA        call 0x70b
5C15  C7 46 FE 05 00  mov word ptr [bp - 2], 5
loc_5C1A:
5C1A  FF 76 FE        push word ptr [bp - 2]
5C1D  BF 6F 5A        mov di, 0x5a6f
5C20  0E              push cs
5C21  57              push di
5C22  E8 E6 AA        call 0x70b
5C25  8B 46 FE        mov ax, word ptr [bp - 2]
5C28  40              inc ax
5C29  50              push ax
5C2A  8B 7E 04        mov di, word ptr [bp + 4]
5C2D  36 FF 75 04     push word ptr ss:[di + 4]
5C31  E8 44 FD        call 0x5978
5C34  BF 7D 5A        mov di, 0x5a7d
5C37  0E              push cs
5C38  57              push di
5C39  8B 46 FC        mov ax, word ptr [bp - 4]
5C3C  B1 04           mov cl, 4
5C3E  D3 E0           shl ax, cl
5C40  C4 3E 68 9B     les di, ptr [0x9b68]
5C44  03 F8           add di, ax
5C46  06              push es
5C47  57              push di
5C48  BF 87 5A        mov di, 0x5a87
5C4B  0E              push cs
5C4C  57              push di
5C4D  E8 DF A9        call 0x62f
5C50  B8 02 00        mov ax, 2
5C53  50              push ax
5C54  9A B1 06 4B 21  call far 214B:06B1
5C59  3D 01 00        cmp ax, 1
5C5C  75 15           jne 0x5c73
5C5E  BF 97 5A        mov di, 0x5a97
5C61  0E              push cs
5C62  57              push di
5C63  8D 7E E7        lea di, [bp - 0x19]
5C66  16              push ss
5C67  57              push di
5C68  B8 14 00        mov ax, 0x14
5C6B  50              push ax
5C6C  9A 44 06 E4 23  call far 23E4:0644
5C71  EB 18           jmp 0x5c8b
loc_5C73:
5C73  3D 02 00        cmp ax, 2
5C76  75 13           jne 0x5c8b
5C78  BF A9 5A        mov di, 0x5aa9
5C7B  0E              push cs
5C7C  57              push di
5C7D  8D 7E E7        lea di, [bp - 0x19]
5C80  16              push ss
5C81  57              push di
5C82  B8 14 00        mov ax, 0x14
5C85  50              push ax
5C86  9A 44 06 E4 23  call far 23E4:0644
loc_5C8B:
5C8B  8D BE DF FD     lea di, [bp - 0x221]
5C8F  16              push ss
5C90  57              push di
5C91  BF B8 5A        mov di, 0x5ab8
5C94  0E              push cs
5C95  57              push di
5C96  9A 2A 06 E4 23  call far 23E4:062A
5C9B  8D BE DF FE     lea di, [bp - 0x121]
5C9F  16              push ss
5CA0  57              push di
5CA1  C4 7E DF        les di, ptr [bp - 0x21]
5CA4  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
5CA8  30 E4           xor ah, ah
5CAA  50              push ax
5CAB  9A 47 09 71 17  call far 1771:0947
5CB0  9A B7 06 E4 23  call far 23E4:06B7
5CB5  8D 7E E7        lea di, [bp - 0x19]
5CB8  16              push ss
5CB9  57              push di
5CBA  BF BD 5A        mov di, 0x5abd
5CBD  0E              push cs
5CBE  57              push di
5CBF  E8 9D AA        call 0x75f
5CC2  B0 00           mov al, 0
5CC4  50              push ax
5CC5  B0 00           mov al, 0
5CC7  50              push ax
5CC8  B0 00           mov al, 0
5CCA  50              push ax
5CCB  E8 28 A9        call 0x5f6
5CCE  89 EC           mov sp, bp
5CD0  5D              pop bp
5CD1  C2 02 00        ret 2
; data (not reached as code), 32 bytes
5CD4                  db 88 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
5CE4                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 000E:5CF4  (found by: call)
sub_5CF4:
5CF4  55              push bp
5CF5  89 E5           mov bp, sp
5CF7  83 EC 0C        sub sp, 0xc
5CFA  8B 46 04        mov ax, word ptr [bp + 4]
5CFD  BA BF 00        mov dx, 0xbf
5D00  F7 E2           mul dx
5D02  C4 3E 17 A9     les di, ptr [0xa917]
5D06  03 F8           add di, ax
5D08  89 7E F9        mov word ptr [bp - 7], di
5D0B  8C 46 FB        mov word ptr [bp - 5], es
5D0E  C4 3E 23 A9     les di, ptr [0xa923]
5D12  89 7E F5        mov word ptr [bp - 0xb], di
5D15  8C 46 F7        mov word ptr [bp - 9], es
5D18  C4 7E F5        les di, ptr [bp - 0xb]
5D1B  26 8A 45 01     mov al, byte ptr es:[di + 1]
5D1F  30 E4           xor ah, ah
5D21  89 46 FD        mov word ptr [bp - 3], ax
5D24  C4 7E F9        les di, ptr [bp - 7]
5D27  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
5D2B  30 E4           xor ah, ah
5D2D  2D 80 00        sub ax, 0x80
5D30  C4 7E F5        les di, ptr [bp - 0xb]
5D33  26 88 45 01     mov byte ptr es:[di + 1], al
5D37  C6 46 FF 00     mov byte ptr [bp - 1], 0
5D3B  C4 7E F5        les di, ptr [bp - 0xb]
5D3E  26 8A 45 01     mov al, byte ptr es:[di + 1]
5D42  30 E4           xor ah, ah
5D44  C4 7E F5        les di, ptr [bp - 0xb]
5D47  03 F8           add di, ax
5D49  26 80 7D 13 00  cmp byte ptr es:[di + 0x13], 0
5D4E  75 44           jne 0x5d94
5D50  C4 7E F5        les di, ptr [bp - 0xb]
5D53  26 8A 45 01     mov al, byte ptr es:[di + 1]
5D57  30 E4           xor ah, ah
5D59  C4 7E F5        les di, ptr [bp - 0xb]
5D5C  03 F8           add di, ax
5D5E  26 80 7D 41 00  cmp byte ptr es:[di + 0x41], 0
5D63  75 2F           jne 0x5d94
5D65  9A FC 55 71 17  call far 1771:55FC
5D6A  08 C0           or al, al
5D6C  74 26           je 0x5d94
5D6E  A1 43 9B        mov ax, word ptr [0x9b43]
5D71  B1 03           mov cl, 3
5D73  D3 E0           shl ax, cl
5D75  C4 3E 2B A9     les di, ptr [0xa92b]
5D79  03 F8           add di, ax
5D7B  26 8A 45 FA     mov al, byte ptr es:[di - 6]
5D7F  50              push ax
5D80  BF D4 5C        mov di, 0x5cd4
5D83  0E              push cs
5D84  57              push di
5D85  9A DF 08 E4 23  call far 23E4:08DF
5D8A  74 08           je 0x5d94
5D8C  55              push bp
5D8D  E8 35 FD        call 0x5ac5
5D90  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_5D94:
5D94  8A 46 FD        mov al, byte ptr [bp - 3]
5D97  C4 7E F5        les di, ptr [bp - 0xb]
5D9A  26 88 45 01     mov byte ptr es:[di + 1], al
5D9E  8A 46 FF        mov al, byte ptr [bp - 1]
5DA1  89 EC           mov sp, bp
5DA3  5D              pop bp
5DA4  C2 02 00        ret 2
; data (not reached as code), 8 bytes
5DA7                  pstr 'TO TOUR'

; ---- routine 000E:5DAF  (found by: call)
sub_5DAF:
5DAF  55              push bp
5DB0  89 E5           mov bp, sp
5DB2  83 EC 04        sub sp, 4
5DB5  C6 46 FF 00     mov byte ptr [bp - 1], 0
5DB9  8B 7E 04        mov di, word ptr [bp + 4]
5DBC  36 FF 75 06     push word ptr ss:[di + 6]
5DC0  9A F8 DA 91 07  call far 0791:DAF8
5DC5  08 C0           or al, al
5DC7  74 4D           je 0x5e16
5DC9  8B 7E 04        mov di, word ptr [bp + 4]
5DCC  36 8B 45 06     mov ax, word ptr ss:[di + 6]
5DD0  B1 04           mov cl, 4
5DD2  D3 E0           shl ax, cl
5DD4  C4 3E 68 9B     les di, ptr [0x9b68]
5DD8  03 F8           add di, ax
5DDA  06              push es
5DDB  57              push di
5DDC  BF A7 5D        mov di, 0x5da7
5DDF  0E              push cs
5DE0  57              push di
5DE1  A1 43 9B        mov ax, word ptr [0x9b43]
5DE4  B1 03           mov cl, 3
5DE6  D3 E0           shl ax, cl
5DE8  C4 3E 2B A9     les di, ptr [0xa92b]
5DEC  03 F8           add di, ax
5DEE  26 8B 45 FE     mov ax, word ptr es:[di - 2]
5DF2  BA BF 00        mov dx, 0xbf
5DF5  F7 E2           mul dx
5DF7  C4 3E 17 A9     les di, ptr [0xa917]
5DFB  03 F8           add di, ax
5DFD  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
5E01  30 E4           xor ah, ah
5E03  8B F8           mov di, ax
5E05  B1 03           mov cl, 3
5E07  D3 E7           shl di, cl
5E09  81 C7 92 6E     add di, 0x6e92
5E0D  1E              push ds
5E0E  57              push di
5E0F  E8 4D A9        call 0x75f
5E12  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_5E16:
5E16  8A 46 FF        mov al, byte ptr [bp - 1]
5E19  89 EC           mov sp, bp
5E1B  5D              pop bp
5E1C  C2 02 00        ret 2
; data (not reached as code), 77 bytes
5E1F                  pstr 'FAIL TO QUALIFY FOR'
5E33                  pstr 'BOO HISS'
5E3C                  pstr 'SACK'
5E41                  pstr 'GET RID OF'
5E4C                  db 00   ; .
5E4D                  pstr 'TRIED HARD FOR'
5E5C                  pstr 'LETS DOWN'
5E66                  pstr 'FAILS'

; ---- routine 000E:5E6C  (found by: call)
sub_5E6C:
5E6C  55              push bp
5E6D  89 E5           mov bp, sp
5E6F  81 EC 08 01     sub sp, 0x108
5E73  8B 7E 04        mov di, word ptr [bp + 4]
5E76  36 8B 45 06     mov ax, word ptr ss:[di + 6]
5E7A  BA BF 00        mov dx, 0xbf
5E7D  F7 E2           mul dx
5E7F  C4 3E 17 A9     les di, ptr [0xa917]
5E83  03 F8           add di, ax
5E85  89 7E FC        mov word ptr [bp - 4], di
5E88  8C 46 FE        mov word ptr [bp - 2], es
5E8B  C4 3E 23 A9     les di, ptr [0xa923]
5E8F  89 7E F8        mov word ptr [bp - 8], di
5E92  8C 46 FA        mov word ptr [bp - 6], es
5E95  B8 02 00        mov ax, 2
5E98  50              push ax
5E99  BF 1F 5E        mov di, 0x5e1f
5E9C  0E              push cs
5E9D  57              push di
5E9E  E8 6A A8        call 0x70b
5EA1  B8 03 00        mov ax, 3
5EA4  50              push ax
5EA5  8B 7E 04        mov di, word ptr [bp + 4]
5EA8  36 FF 75 06     push word ptr ss:[di + 6]
5EAC  E8 C9 FA        call 0x5978
5EAF  B8 03 00        mov ax, 3
5EB2  50              push ax
5EB3  9A B1 06 4B 21  call far 214B:06B1
5EB8  3D 01 00        cmp ax, 1
5EBB  75 19           jne 0x5ed6
5EBD  BF 33 5E        mov di, 0x5e33
5EC0  0E              push cs
5EC1  57              push di
5EC2  8B 7E 04        mov di, word ptr [bp + 4]
5EC5  81 C7 EB FF     add di, 0xffeb
5EC9  16              push ss
5ECA  57              push di
5ECB  B8 14 00        mov ax, 0x14
5ECE  50              push ax
5ECF  9A 44 06 E4 23  call far 23E4:0644
5ED4  EB 3A           jmp 0x5f10
loc_5ED6:
5ED6  3D 02 00        cmp ax, 2
5ED9  75 19           jne 0x5ef4
5EDB  BF 3C 5E        mov di, 0x5e3c
5EDE  0E              push cs
5EDF  57              push di
5EE0  8B 7E 04        mov di, word ptr [bp + 4]
5EE3  81 C7 EB FF     add di, 0xffeb
5EE7  16              push ss
5EE8  57              push di
5EE9  B8 14 00        mov ax, 0x14
5EEC  50              push ax
5EED  9A 44 06 E4 23  call far 23E4:0644
5EF2  EB 1C           jmp 0x5f10
loc_5EF4:
5EF4  3D 03 00        cmp ax, 3
5EF7  75 17           jne 0x5f10
5EF9  BF 41 5E        mov di, 0x5e41
5EFC  0E              push cs
5EFD  57              push di
5EFE  8B 7E 04        mov di, word ptr [bp + 4]
5F01  81 C7 EB FF     add di, 0xffeb
5F05  16              push ss
5F06  57              push di
5F07  B8 14 00        mov ax, 0x14
5F0A  50              push ax
5F0B  9A 44 06 E4 23  call far 23E4:0644
loc_5F10:
5F10  8B 7E 04        mov di, word ptr [bp + 4]
5F13  81 C7 EB FF     add di, 0xffeb
5F17  16              push ss
5F18  57              push di
5F19  8D BE F8 FE     lea di, [bp - 0x108]
5F1D  16              push ss
5F1E  57              push di
5F1F  C4 7E FC        les di, ptr [bp - 4]
5F22  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
5F26  30 E4           xor ah, ah
5F28  50              push ax
5F29  9A 47 09 71 17  call far 1771:0947
5F2E  BF 4C 5E        mov di, 0x5e4c
5F31  0E              push cs
5F32  57              push di
5F33  E8 F9 A6        call 0x62f
5F36  8B 7E 04        mov di, word ptr [bp + 4]
5F39  36 8B 45 DF     mov ax, word ptr ss:[di - 0x21]
5F3D  3D 19 00        cmp ax, 0x19
5F40  72 1E           jb 0x5f60
5F42  3D 20 00        cmp ax, 0x20
5F45  77 19           ja 0x5f60
5F47  BF 4D 5E        mov di, 0x5e4d
5F4A  0E              push cs
5F4B  57              push di
5F4C  8B 7E 04        mov di, word ptr [bp + 4]
5F4F  81 C7 EB FF     add di, 0xffeb
5F53  16              push ss
5F54  57              push di
5F55  B8 14 00        mov ax, 0x14
5F58  50              push ax
5F59  9A 44 06 E4 23  call far 23E4:0644
5F5E  EB 3A           jmp 0x5f9a
loc_5F60:
5F60  3D 11 00        cmp ax, 0x11
5F63  72 1E           jb 0x5f83
5F65  3D 18 00        cmp ax, 0x18
5F68  77 19           ja 0x5f83
5F6A  BF 5C 5E        mov di, 0x5e5c
5F6D  0E              push cs
5F6E  57              push di
5F6F  8B 7E 04        mov di, word ptr [bp + 4]
5F72  81 C7 EB FF     add di, 0xffeb
5F76  16              push ss
5F77  57              push di
5F78  B8 14 00        mov ax, 0x14
5F7B  50              push ax
5F7C  9A 44 06 E4 23  call far 23E4:0644
5F81  EB 17           jmp 0x5f9a
loc_5F83:
5F83  BF 66 5E        mov di, 0x5e66
5F86  0E              push cs
5F87  57              push di
5F88  8B 7E 04        mov di, word ptr [bp + 4]
5F8B  81 C7 EB FF     add di, 0xffeb
5F8F  16              push ss
5F90  57              push di
5F91  B8 14 00        mov ax, 0x14
5F94  50              push ax
5F95  9A 44 06 E4 23  call far 23E4:0644
loc_5F9A:
5F9A  FF 76 04        push word ptr [bp + 4]
5F9D  E8 0F FE        call 0x5daf
5FA0  08 C0           or al, al
5FA2  75 34           jne 0x5fd8
5FA4  8D BE F8 FE     lea di, [bp - 0x108]
5FA8  16              push ss
5FA9  57              push di
5FAA  C4 7E FC        les di, ptr [bp - 4]
5FAD  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
5FB1  30 E4           xor ah, ah
5FB3  50              push ax
5FB4  9A 47 09 71 17  call far 1771:0947
5FB9  8B 7E 04        mov di, word ptr [bp + 4]
5FBC  81 C7 EB FF     add di, 0xffeb
5FC0  16              push ss
5FC1  57              push di
5FC2  8B 7E 04        mov di, word ptr [bp + 4]
5FC5  36 8B 45 06     mov ax, word ptr ss:[di + 6]
5FC9  B1 04           mov cl, 4
5FCB  D3 E0           shl ax, cl
5FCD  C4 3E 68 9B     les di, ptr [0x9b68]
5FD1  03 F8           add di, ax
5FD3  06              push es
5FD4  57              push di
5FD5  E8 87 A7        call 0x75f
loc_5FD8:
5FD8  89 EC           mov sp, bp
5FDA  5D              pop bp
5FDB  C2 02 00        ret 2
; data (not reached as code), 237 bytes
5FDE                  pstr 'IS TO HOST'
5FE9                  pstr 'GROUPS ARE ANNOUNCED'
5FFE                  pstr 'QUALIFIES FOR'
600C                  pstr 'THE FINALS OF'
601A                  pstr 'FOR QUALIFYING FOR'
602D                  pstr 'IN '
6031                  pstr 'play'
6036                  pstr 'face'
603B                  db 01 20 01 2C   ; . .,
603F                  pstr 'and '
6044                  pstr 'BIG CHANCE FOR'
6053                  db 00   ; .
6054                  pstr 'GETS THE HOME'
6062                  pstr 'ADVANTAGE'
606C                  pstr 'HAS AN EASY RIDE'
607D                  pstr 'HAS A FAIR CHANCE'
608F                  pstr 'TOUGH TASK FOR'
609E                  pstr 'FAVOURITE TO WIN'
60AF                  pstr 'THE BEST TEAM IN'
60C0                  pstr ' IS'
60C4                  pstr 'GROUP '

