; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 1771 (image offsets 17710..2137F), part 8 of 14
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 1771:52CC  (found by: far)
sub_52CC:
52CC  55              push bp
52CD  89 E5           mov bp, sp
52CF  83 EC 26        sub sp, 0x26
52D2  8B 46 06        mov ax, word ptr [bp + 6]
52D5  BA BF 00        mov dx, 0xbf
52D8  F7 E2           mul dx
52DA  C4 3E 17 A9     les di, ptr [0xa917]
52DE  03 F8           add di, ax
52E0  89 7E E0        mov word ptr [bp - 0x20], di
52E3  8C 46 E2        mov word ptr [bp - 0x1e], es
52E6  FF 76 06        push word ptr [bp + 6]
52E9  0E              push cs
52EA  E8 8A B8        call 0xb77
52ED  88 46 E5        mov byte ptr [bp - 0x1b], al
52F0  C6 46 E4 00     mov byte ptr [bp - 0x1c], 0
52F4  EB 03           jmp 0x52f9
loc_52F6:
52F6  FE 46 E4        inc byte ptr [bp - 0x1c]
loc_52F9:
52F9  8A 46 E4        mov al, byte ptr [bp - 0x1c]
52FC  98              cwde
52FD  8B F8           mov di, ax
52FF  8A 85 3A 0F     mov al, byte ptr [di + 0xf3a]
5303  30 E4           xor ah, ah
5305  89 46 E8        mov word ptr [bp - 0x18], ax
5308  8A 46 E4        mov al, byte ptr [bp - 0x1c]
530B  98              cwde
530C  8B F8           mov di, ax
530E  8A 85 3C 0F     mov al, byte ptr [di + 0xf3c]
5312  30 E4           xor ah, ah
5314  89 46 E6        mov word ptr [bp - 0x1a], ax
5317  8B 46 E6        mov ax, word ptr [bp - 0x1a]
531A  89 46 DE        mov word ptr [bp - 0x22], ax
531D  8B 46 E8        mov ax, word ptr [bp - 0x18]
5320  3B 46 DE        cmp ax, word ptr [bp - 0x22]
5323  77 60           ja 0x5385
5325  89 46 EA        mov word ptr [bp - 0x16], ax
5328  EB 03           jmp 0x532d
loc_532A:
532A  FF 46 EA        inc word ptr [bp - 0x16]
loc_532D:
532D  8B 46 EA        mov ax, word ptr [bp - 0x16]
5330  D1 E0           shl ax, 1
5332  C4 7E E0        les di, ptr [bp - 0x20]
5335  03 F8           add di, ax
5337  26 8B 45 FE     mov ax, word ptr es:[di - 2]
533B  BA 14 00        mov dx, 0x14
533E  F7 E2           mul dx
5340  C4 3E 1B A9     les di, ptr [0xa91b]
5344  03 F8           add di, ax
5346  89 7E DA        mov word ptr [bp - 0x26], di
5349  8C 46 DC        mov word ptr [bp - 0x24], es
534C  C4 7E DA        les di, ptr [bp - 0x26]
534F  26 8A 45 06     mov al, byte ptr es:[di + 6]
5353  8B 7E EA        mov di, word ptr [bp - 0x16]
5356  88 43 EB        mov byte ptr [bp + di - 0x15], al
5359  80 7E E5 00     cmp byte ptr [bp - 0x1b], 0
535D  74 1E           je 0x537d
535F  8B 46 EA        mov ax, word ptr [bp - 0x16]
5362  D1 E0           shl ax, 1
5364  C4 7E E0        les di, ptr [bp - 0x20]
5367  03 F8           add di, ax
5369  26 FF 75 FE     push word ptr es:[di - 2]
536D  0E              push cs
536E  E8 A5 DE        call 0x3216
5371  08 C0           or al, al
5373  74 08           je 0x537d
5375  C4 7E DA        les di, ptr [bp - 0x26]
5378  26 C6 45 06 0E  mov byte ptr es:[di + 6], 0xe
loc_537D:
537D  8B 46 EA        mov ax, word ptr [bp - 0x16]
5380  3B 46 DE        cmp ax, word ptr [bp - 0x22]
5383  75 A5           jne 0x532a
loc_5385:
5385  FF 76 E8        push word ptr [bp - 0x18]
5388  FF 76 E6        push word ptr [bp - 0x1a]
538B  55              push bp
538C  E8 EB FD        call 0x517a
538F  8B 46 E6        mov ax, word ptr [bp - 0x1a]
5392  89 46 DE        mov word ptr [bp - 0x22], ax
5395  8B 46 E8        mov ax, word ptr [bp - 0x18]
5398  3B 46 DE        cmp ax, word ptr [bp - 0x22]
539B  77 3C           ja 0x53d9
539D  89 46 EA        mov word ptr [bp - 0x16], ax
53A0  EB 03           jmp 0x53a5
loc_53A2:
53A2  FF 46 EA        inc word ptr [bp - 0x16]
loc_53A5:
53A5  8B 46 EA        mov ax, word ptr [bp - 0x16]
53A8  D1 E0           shl ax, 1
53AA  C4 7E E0        les di, ptr [bp - 0x20]
53AD  03 F8           add di, ax
53AF  26 8B 45 FE     mov ax, word ptr es:[di - 2]
53B3  BA 14 00        mov dx, 0x14
53B6  F7 E2           mul dx
53B8  C4 3E 1B A9     les di, ptr [0xa91b]
53BC  03 F8           add di, ax
53BE  89 7E DA        mov word ptr [bp - 0x26], di
53C1  8C 46 DC        mov word ptr [bp - 0x24], es
53C4  8B 7E EA        mov di, word ptr [bp - 0x16]
53C7  8A 43 EB        mov al, byte ptr [bp + di - 0x15]
53CA  C4 7E DA        les di, ptr [bp - 0x26]
53CD  26 88 45 06     mov byte ptr es:[di + 6], al
53D1  8B 46 EA        mov ax, word ptr [bp - 0x16]
53D4  3B 46 DE        cmp ax, word ptr [bp - 0x22]
53D7  75 C9           jne 0x53a2
loc_53D9:
53D9  80 7E E4 01     cmp byte ptr [bp - 0x1c], 1
53DD  74 03           je 0x53e2
53DF  E9 14 FF        jmp 0x52f6
loc_53E2:
53E2  89 EC           mov sp, bp
53E4  5D              pop bp
53E5  CA 02 00        retf 2

; ---- routine 1771:53E8  (found by: call)
sub_53E8:
53E8  55              push bp
53E9  89 E5           mov bp, sp
53EB  83 EC 08        sub sp, 8
53EE  8B 46 08        mov ax, word ptr [bp + 8]
53F1  89 46 FE        mov word ptr [bp - 2], ax
53F4  8B 46 06        mov ax, word ptr [bp + 6]
53F7  89 46 FC        mov word ptr [bp - 4], ax
53FA  8B 46 08        mov ax, word ptr [bp + 8]
53FD  03 46 06        add ax, word ptr [bp + 6]
5400  31 D2           xor dx, dx
5402  B9 02 00        mov cx, 2
5405  F7 F1           div cx
5407  D1 E0           shl ax, 1
5409  C4 3E 27 A9     les di, ptr [0xa927]
540D  03 F8           add di, ax
540F  26 8B 05        mov ax, word ptr es:[di]
5412  BA 14 00        mov dx, 0x14
5415  F7 E2           mul dx
5417  C4 3E 1B A9     les di, ptr [0xa91b]
541B  03 F8           add di, ax
541D  26 8A 45 06     mov al, byte ptr es:[di + 6]
5421  30 E4           xor ah, ah
5423  89 46 F8        mov word ptr [bp - 8], ax
loc_5426:
5426  8B 46 FE        mov ax, word ptr [bp - 2]
5429  D1 E0           shl ax, 1
542B  C4 3E 27 A9     les di, ptr [0xa927]
542F  03 F8           add di, ax
5431  26 8B 05        mov ax, word ptr es:[di]
5434  BA 14 00        mov dx, 0x14
5437  F7 E2           mul dx
5439  C4 3E 1B A9     les di, ptr [0xa91b]
543D  03 F8           add di, ax
543F  26 8A 45 06     mov al, byte ptr es:[di + 6]
5443  30 E4           xor ah, ah
5445  3B 46 F8        cmp ax, word ptr [bp - 8]
5448  73 05           jae 0x544f
544A  FF 46 FE        inc word ptr [bp - 2]
544D  EB D7           jmp 0x5426
loc_544F:
544F  8B 46 FC        mov ax, word ptr [bp - 4]
5452  D1 E0           shl ax, 1
5454  C4 3E 27 A9     les di, ptr [0xa927]
5458  03 F8           add di, ax
545A  26 8B 05        mov ax, word ptr es:[di]
545D  BA 14 00        mov dx, 0x14
5460  F7 E2           mul dx
5462  C4 3E 1B A9     les di, ptr [0xa91b]
5466  03 F8           add di, ax
5468  26 8A 45 06     mov al, byte ptr es:[di + 6]
546C  30 E4           xor ah, ah
546E  3B 46 F8        cmp ax, word ptr [bp - 8]
5471  76 05           jbe 0x5478
5473  FF 4E FC        dec word ptr [bp - 4]
5476  EB D7           jmp 0x544f
loc_5478:
5478  8B 46 FE        mov ax, word ptr [bp - 2]
547B  3B 46 FC        cmp ax, word ptr [bp - 4]
547E  77 79           ja 0x54f9
5480  8B 46 FE        mov ax, word ptr [bp - 2]
5483  D1 E0           shl ax, 1
5485  C4 3E 27 A9     les di, ptr [0xa927]
5489  03 F8           add di, ax
548B  26 8B 05        mov ax, word ptr es:[di]
548E  89 46 FA        mov word ptr [bp - 6], ax
5491  8B 46 FC        mov ax, word ptr [bp - 4]
5494  D1 E0           shl ax, 1
5496  C4 3E 27 A9     les di, ptr [0xa927]
549A  03 F8           add di, ax
549C  26 8B 15        mov dx, word ptr es:[di]
549F  8B 46 FE        mov ax, word ptr [bp - 2]
54A2  D1 E0           shl ax, 1
54A4  C4 3E 27 A9     les di, ptr [0xa927]
54A8  03 F8           add di, ax
54AA  26 89 15        mov word ptr es:[di], dx
54AD  8B 56 FA        mov dx, word ptr [bp - 6]
54B0  8B 46 FC        mov ax, word ptr [bp - 4]
54B3  D1 E0           shl ax, 1
54B5  C4 3E 27 A9     les di, ptr [0xa927]
54B9  03 F8           add di, ax
54BB  26 89 15        mov word ptr es:[di], dx
54BE  8B 46 FE        mov ax, word ptr [bp - 2]
54C1  8B 7E 04        mov di, word ptr [bp + 4]
54C4  36 2B 45 AC     sub ax, word ptr ss:[di - 0x54]
54C8  40              inc ax
54C9  8B 7E 04        mov di, word ptr [bp + 4]
54CC  03 F8           add di, ax
54CE  81 C7 AF FF     add di, 0xffaf
54D2  16              push ss
54D3  57              push di
54D4  8B 46 FC        mov ax, word ptr [bp - 4]
54D7  8B 7E 04        mov di, word ptr [bp + 4]
54DA  36 2B 45 AC     sub ax, word ptr ss:[di - 0x54]
54DE  40              inc ax
54DF  8B 7E 04        mov di, word ptr [bp + 4]
54E2  03 F8           add di, ax
54E4  81 C7 AF FF     add di, 0xffaf
54E8  16              push ss
54E9  57              push di
54EA  B8 01 00        mov ax, 1
54ED  50              push ax
54EE  9A 7B 00 4B 21  call far 214B:007B
54F3  FF 46 FE        inc word ptr [bp - 2]
54F6  FF 4E FC        dec word ptr [bp - 4]
loc_54F9:
54F9  8B 46 FE        mov ax, word ptr [bp - 2]
54FC  3B 46 FC        cmp ax, word ptr [bp - 4]
54FF  77 03           ja 0x5504
5501  E9 22 FF        jmp 0x5426
loc_5504:
5504  8B 46 08        mov ax, word ptr [bp + 8]
5507  3B 46 FC        cmp ax, word ptr [bp - 4]
550A  73 0C           jae 0x5518
550C  FF 76 08        push word ptr [bp + 8]
550F  FF 76 FC        push word ptr [bp - 4]
5512  FF 76 04        push word ptr [bp + 4]
5515  E8 D0 FE        call 0x53e8
loc_5518:
5518  8B 46 FE        mov ax, word ptr [bp - 2]
551B  3B 46 06        cmp ax, word ptr [bp + 6]
551E  73 0C           jae 0x552c
5520  FF 76 FE        push word ptr [bp - 2]
5523  FF 76 06        push word ptr [bp + 6]
5526  FF 76 04        push word ptr [bp + 4]
5529  E8 BC FE        call 0x53e8
loc_552C:
552C  89 EC           mov sp, bp
552E  5D              pop bp
552F  C2 06 00        ret 6

; ---- routine 1771:5532  (found by: call, far)
sub_5532:
5532  55              push bp
5533  89 E5           mov bp, sp
5535  83 EC 58        sub sp, 0x58
5538  C4 3E 23 A9     les di, ptr [0xa923]
553C  26 8A 45 01     mov al, byte ptr es:[di + 1]
5540  30 E4           xor ah, ah
5542  8B F8           mov di, ax
5544  D1 E7           shl di, 1
5546  8B 85 18 6D     mov ax, word ptr [di + 0x6d18]
554A  89 46 AC        mov word ptr [bp - 0x54], ax
554D  C7 46 AE 01 00  mov word ptr [bp - 0x52], 1
5552  EB 03           jmp 0x5557
loc_5554:
5554  FF 46 AE        inc word ptr [bp - 0x52]
loc_5557:
5557  8B 46 AE        mov ax, word ptr [bp - 0x52]
555A  03 46 AC        add ax, word ptr [bp - 0x54]
555D  48              dec ax
555E  D1 E0           shl ax, 1
5560  C4 3E 27 A9     les di, ptr [0xa927]
5564  03 F8           add di, ax
5566  26 8B 05        mov ax, word ptr es:[di]
5569  BA 14 00        mov dx, 0x14
556C  F7 E2           mul dx
556E  C4 3E 1B A9     les di, ptr [0xa91b]
5572  03 F8           add di, ax
5574  89 7E A8        mov word ptr [bp - 0x58], di
5577  8C 46 AA        mov word ptr [bp - 0x56], es
557A  C4 7E A8        les di, ptr [bp - 0x58]
557D  26 8A 45 06     mov al, byte ptr es:[di + 6]
5581  8B 7E AE        mov di, word ptr [bp - 0x52]
5584  88 43 AF        mov byte ptr [bp + di - 0x51], al
5587  8B 46 AE        mov ax, word ptr [bp - 0x52]
558A  03 46 AC        add ax, word ptr [bp - 0x54]
558D  48              dec ax
558E  D1 E0           shl ax, 1
5590  C4 3E 27 A9     les di, ptr [0xa927]
5594  03 F8           add di, ax
5596  26 83 3D 00     cmp word ptr es:[di], 0
559A  75 08           jne 0x55a4
559C  C4 7E A8        les di, ptr [bp - 0x58]
559F  26 C6 45 06 0E  mov byte ptr es:[di + 6], 0xe
loc_55A4:
55A4  83 7E AE 50     cmp word ptr [bp - 0x52], 0x50
55A8  75 AA           jne 0x5554
55AA  FF 76 AC        push word ptr [bp - 0x54]
55AD  8B 46 AC        mov ax, word ptr [bp - 0x54]
55B0  05 4F 00        add ax, 0x4f
55B3  50              push ax
55B4  55              push bp
55B5  E8 30 FE        call 0x53e8
55B8  C7 46 AE 01 00  mov word ptr [bp - 0x52], 1
55BD  EB 03           jmp 0x55c2
loc_55BF:
55BF  FF 46 AE        inc word ptr [bp - 0x52]
loc_55C2:
55C2  8B 46 AE        mov ax, word ptr [bp - 0x52]
55C5  03 46 AC        add ax, word ptr [bp - 0x54]
55C8  48              dec ax
55C9  D1 E0           shl ax, 1
55CB  C4 3E 27 A9     les di, ptr [0xa927]
55CF  03 F8           add di, ax
55D1  26 8B 05        mov ax, word ptr es:[di]
55D4  BA 14 00        mov dx, 0x14
55D7  F7 E2           mul dx
55D9  C4 3E 1B A9     les di, ptr [0xa91b]
55DD  03 F8           add di, ax
55DF  89 7E A8        mov word ptr [bp - 0x58], di
55E2  8C 46 AA        mov word ptr [bp - 0x56], es
55E5  8B 7E AE        mov di, word ptr [bp - 0x52]
55E8  8A 43 AF        mov al, byte ptr [bp + di - 0x51]
55EB  C4 7E A8        les di, ptr [bp - 0x58]
55EE  26 88 45 06     mov byte ptr es:[di + 6], al
55F2  83 7E AE 50     cmp word ptr [bp - 0x52], 0x50
55F6  75 C7           jne 0x55bf
55F8  89 EC           mov sp, bp
55FA  5D              pop bp
55FB  CB              retf

; ---- routine 1771:55FC  (found by: far)
sub_55FC:
55FC  55              push bp
55FD  89 E5           mov bp, sp
55FF  83 EC 06        sub sp, 6
5602  C4 3E 23 A9     les di, ptr [0xa923]
5606  26 8A 45 01     mov al, byte ptr es:[di + 1]
560A  30 E4           xor ah, ah
560C  C4 3E 23 A9     les di, ptr [0xa923]
5610  03 F8           add di, ax
5612  26 80 7D 47 00  cmp byte ptr es:[di + 0x47], 0
5617  74 07           je 0x5620
5619  C6 46 FF 00     mov byte ptr [bp - 1], 0
561D  E9 BD 00        jmp 0x56dd
loc_5620:
5620  C4 3E 23 A9     les di, ptr [0xa923]
5624  26 8A 45 01     mov al, byte ptr es:[di + 1]
5628  30 E4           xor ah, ah
562A  05 80 00        add ax, 0x80
562D  BA 03 00        mov dx, 3
5630  F7 E2           mul dx
5632  C4 3E 1F A9     les di, ptr [0xa91f]
5636  03 F8           add di, ax
5638  26 8A 05        mov al, byte ptr es:[di]
563B  30 E4           xor ah, ah
563D  89 46 FB        mov word ptr [bp - 5], ax
5640  C7 46 FD 24 00  mov word ptr [bp - 3], 0x24
loc_5645:
5645  83 7E FD 00     cmp word ptr [bp - 3], 0
5649  76 56           jbe 0x56a1
564B  8B 46 FD        mov ax, word ptr [bp - 3]
564E  D1 E0           shl ax, 1
5650  8B C8           mov cx, ax
5652  8B 46 FB        mov ax, word ptr [bp - 5]
5655  BA 48 00        mov dx, 0x48
5658  F7 E2           mul dx
565A  C4 3E 2F A9     les di, ptr [0xa92f]
565E  03 F8           add di, ax
5660  03 F9           add di, cx
5662  26 8B 45 FE     mov ax, word ptr es:[di - 2]
5666  B1 03           mov cl, 3
5668  D3 E0           shl ax, cl
566A  C4 3E 2B A9     les di, ptr [0xa92b]
566E  03 F8           add di, ax
5670  26 80 7D F8 FE  cmp byte ptr es:[di - 8], 0xfe
5675  72 2A           jb 0x56a1
5677  8B 46 FD        mov ax, word ptr [bp - 3]
567A  D1 E0           shl ax, 1
567C  8B C8           mov cx, ax
567E  8B 46 FB        mov ax, word ptr [bp - 5]
5681  BA 48 00        mov dx, 0x48
5684  F7 E2           mul dx
5686  C4 3E 2F A9     les di, ptr [0xa92f]
568A  03 F8           add di, ax
568C  03 F9           add di, cx
568E  26 8B 45 FE     mov ax, word ptr es:[di - 2]
5692  C4 3E 23 A9     les di, ptr [0xa923]
5696  26 3B 45 26     cmp ax, word ptr es:[di + 0x26]
569A  72 05           jb 0x56a1
569C  FF 4E FD        dec word ptr [bp - 3]
569F  EB A4           jmp 0x5645
loc_56A1:
56A1  83 7E FD 24     cmp word ptr [bp - 3], 0x24
56A5  75 07           jne 0x56ae
56A7  31 C0           xor ax, ax
56A9  A3 43 9B        mov word ptr [0x9b43], ax
56AC  EB 1F           jmp 0x56cd
loc_56AE:
56AE  8B 46 FD        mov ax, word ptr [bp - 3]
56B1  40              inc ax
56B2  D1 E0           shl ax, 1
56B4  8B C8           mov cx, ax
56B6  8B 46 FB        mov ax, word ptr [bp - 5]
56B9  BA 48 00        mov dx, 0x48
56BC  F7 E2           mul dx
56BE  C4 3E 2F A9     les di, ptr [0xa92f]
56C2  03 F8           add di, ax
56C4  03 F9           add di, cx
56C6  26 8B 45 FE     mov ax, word ptr es:[di - 2]
56CA  A3 43 9B        mov word ptr [0x9b43], ax
loc_56CD:
56CD  83 3E 43 9B 00  cmp word ptr [0x9b43], 0
56D2  77 04           ja 0x56d8
56D4  B0 00           mov al, 0
56D6  EB 02           jmp 0x56da
loc_56D8:
56D8  B0 01           mov al, 1
loc_56DA:
56DA  88 46 FF        mov byte ptr [bp - 1], al
loc_56DD:
56DD  8A 46 FF        mov al, byte ptr [bp - 1]
56E0  89 EC           mov sp, bp
56E2  5D              pop bp
56E3  CB              retf

; ---- routine 1771:56E4  (found by: call)
sub_56E4:
56E4  55              push bp
56E5  89 E5           mov bp, sp
56E7  83 EC 02        sub sp, 2
56EA  8B 46 04        mov ax, word ptr [bp + 4]
56ED  48              dec ax
56EE  B9 05 00        mov cx, 5
56F1  D3 E0           shl ax, cl
56F3  89 46 FE        mov word ptr [bp - 2], ax
56F6  8B 46 FE        mov ax, word ptr [bp - 2]
56F9  89 EC           mov sp, bp
56FB  5D              pop bp
56FC  C2 02 00        ret 2

; ---- routine 1771:56FF  (found by: call)
sub_56FF:
56FF  55              push bp
5700  89 E5           mov bp, sp
5702  83 EC 06        sub sp, 6
5705  C4 3E 23 A9     les di, ptr [0xa923]
5709  26 80 7D 40 00  cmp byte ptr es:[di + 0x40], 0
570E  75 15           jne 0x5725
5710  BF 7E 9C        mov di, 0x9c7e
5713  1E              push ds
5714  57              push di
5715  BF FF 9C        mov di, 0x9cff
5718  1E              push ds
5719  57              push di
571A  B8 81 00        mov ax, 0x81
571D  50              push ax
571E  9A 3C 00 4B 21  call far 214B:003C
5723  EB 56           jmp 0x577b
loc_5725:
5725  31 C0           xor ax, ax
5727  89 46 FC        mov word ptr [bp - 4], ax
572A  C7 46 FA 01 00  mov word ptr [bp - 6], 1
572F  EB 03           jmp 0x5734
loc_5731:
5731  FF 46 FA        inc word ptr [bp - 6]
loc_5734:
5734  C7 46 FE 01 00  mov word ptr [bp - 2], 1
5739  EB 03           jmp 0x573e
loc_573B:
573B  FF 46 FE        inc word ptr [bp - 2]
loc_573E:
573E  8B 7E FE        mov di, word ptr [bp - 2]
5741  8A 85 FD 9B     mov al, byte ptr [di - 0x6403]
5745  30 E4           xor ah, ah
5747  BA BF 00        mov dx, 0xbf
574A  F7 E2           mul dx
574C  C4 3E 17 A9     les di, ptr [0xa917]
5750  03 F8           add di, ax
5752  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
5756  30 E4           xor ah, ah
5758  3B 46 FA        cmp ax, word ptr [bp - 6]
575B  75 11           jne 0x576e
575D  FF 46 FC        inc word ptr [bp - 4]
5760  8B 7E FE        mov di, word ptr [bp - 2]
5763  8A 85 FD 9B     mov al, byte ptr [di - 0x6403]
5767  8B 7E FC        mov di, word ptr [bp - 4]
576A  88 85 FF 9C     mov byte ptr [di - 0x6301], al
loc_576E:
576E  81 7E FE 80 00  cmp word ptr [bp - 2], 0x80
5773  75 C6           jne 0x573b
5775  83 7E FA 04     cmp word ptr [bp - 6], 4
5779  75 B6           jne 0x5731
loc_577B:
577B  89 EC           mov sp, bp
577D  5D              pop bp
577E  C3              ret
; data (not reached as code), 140 bytes
577F                  pstr 'CANCELLED'
5789                  pstr 'friendly'
5792                  pstr 'qualifying'
579D                  pstr 'play-off'
57A6                  pstr 'group stage'
57B2                  pstr 'qtr-final'
57BC                  pstr 'semi-final'
57C7                  pstr 'final'
57CD                  pstr '3rd place'
57D7                  pstr 'last 16'
57DF                  pstr 'fourth'
57E6                  pstr 'third'
57EC                  pstr 'runners-up'
57F7                  pstr 'winners'
57FF                  pstr 'final round'

; ---- routine 1771:580B  (found by: call, far)
sub_580B:
580B  55              push bp
580C  89 E5           mov bp, sp
580E  8B 46 06        mov ax, word ptr [bp + 6]
5811  3D 00 00        cmp ax, 0
5814  75 16           jne 0x582c
5816  BF 7F 57        mov di, 0x577f
5819  0E              push cs
581A  57              push di
581B  C4 7E 08        les di, ptr [bp + 8]
581E  06              push es
581F  57              push di
5820  B8 0C 00        mov ax, 0xc
5823  50              push ax
5824  9A 44 06 E4 23  call far 23E4:0644
5829  E9 86 01        jmp 0x59b2
loc_582C:
582C  3D 01 00        cmp ax, 1
582F  75 16           jne 0x5847
5831  BF 89 57        mov di, 0x5789
5834  0E              push cs
5835  57              push di
5836  C4 7E 08        les di, ptr [bp + 8]
5839  06              push es
583A  57              push di
583B  B8 0C 00        mov ax, 0xc
583E  50              push ax
583F  9A 44 06 E4 23  call far 23E4:0644
5844  E9 6B 01        jmp 0x59b2
loc_5847:
5847  3D 02 00        cmp ax, 2
584A  74 05           je 0x5851
584C  3D 05 00        cmp ax, 5
584F  75 16           jne 0x5867
loc_5851:
5851  BF 92 57        mov di, 0x5792
5854  0E              push cs
5855  57              push di
5856  C4 7E 08        les di, ptr [bp + 8]
5859  06              push es
585A  57              push di
585B  B8 0C 00        mov ax, 0xc
585E  50              push ax
585F  9A 44 06 E4 23  call far 23E4:0644
5864  E9 4B 01        jmp 0x59b2
loc_5867:
5867  3D 06 00        cmp ax, 6
586A  75 16           jne 0x5882
586C  BF 9D 57        mov di, 0x579d
586F  0E              push cs
5870  57              push di
5871  C4 7E 08        les di, ptr [bp + 8]
5874  06              push es
5875  57              push di
5876  B8 0C 00        mov ax, 0xc
5879  50              push ax
587A  9A 44 06 E4 23  call far 23E4:0644
587F  E9 30 01        jmp 0x59b2
loc_5882:
5882  3D 03 00        cmp ax, 3
5885  74 05           je 0x588c
5887  3D 07 00        cmp ax, 7
588A  75 16           jne 0x58a2
loc_588C:
588C  BF A6 57        mov di, 0x57a6
588F  0E              push cs
5890  57              push di
5891  C4 7E 08        les di, ptr [bp + 8]
5894  06              push es
5895  57              push di
5896  B8 0C 00        mov ax, 0xc
5899  50              push ax
589A  9A 44 06 E4 23  call far 23E4:0644
589F  E9 10 01        jmp 0x59b2
loc_58A2:
58A2  3D C8 00        cmp ax, 0xc8
58A5  75 16           jne 0x58bd
58A7  BF B2 57        mov di, 0x57b2
58AA  0E              push cs
58AB  57              push di
58AC  C4 7E 08        les di, ptr [bp + 8]
58AF  06              push es
58B0  57              push di
58B1  B8 0C 00        mov ax, 0xc
58B4  50              push ax
58B5  9A 44 06 E4 23  call far 23E4:0644
58BA  E9 F5 00        jmp 0x59b2
loc_58BD:
58BD  3D 65 00        cmp ax, 0x65
58C0  74 05           je 0x58c7
58C2  3D C9 00        cmp ax, 0xc9
58C5  75 16           jne 0x58dd
loc_58C7:
58C7  BF BC 57        mov di, 0x57bc
58CA  0E              push cs
58CB  57              push di
58CC  C4 7E 08        les di, ptr [bp + 8]
58CF  06              push es
58D0  57              push di
58D1  B8 0C 00        mov ax, 0xc
58D4  50              push ax
58D5  9A 44 06 E4 23  call far 23E4:0644
58DA  E9 D5 00        jmp 0x59b2
loc_58DD:
58DD  3D 67 00        cmp ax, 0x67
58E0  74 05           je 0x58e7
58E2  3D CB 00        cmp ax, 0xcb
58E5  75 16           jne 0x58fd
loc_58E7:
58E7  BF C7 57        mov di, 0x57c7
58EA  0E              push cs
58EB  57              push di
58EC  C4 7E 08        les di, ptr [bp + 8]
58EF  06              push es
58F0  57              push di
58F1  B8 0C 00        mov ax, 0xc
58F4  50              push ax
58F5  9A 44 06 E4 23  call far 23E4:0644
58FA  E9 B5 00        jmp 0x59b2
loc_58FD:
58FD  3D 66 00        cmp ax, 0x66
5900  74 05           je 0x5907
5902  3D CA 00        cmp ax, 0xca
5905  75 16           jne 0x591d
loc_5907:
5907  BF CD 57        mov di, 0x57cd
590A  0E              push cs
590B  57              push di
590C  C4 7E 08        les di, ptr [bp + 8]
590F  06              push es
5910  57              push di
5911  B8 0C 00        mov ax, 0xc
5914  50              push ax
5915  9A 44 06 E4 23  call far 23E4:0644
591A  E9 95 00        jmp 0x59b2
loc_591D:
591D  3D 08 00        cmp ax, 8
5920  75 15           jne 0x5937
5922  BF D7 57        mov di, 0x57d7
5925  0E              push cs
5926  57              push di
5927  C4 7E 08        les di, ptr [bp + 8]
592A  06              push es
592B  57              push di
592C  B8 0C 00        mov ax, 0xc
592F  50              push ax
5930  9A 44 06 E4 23  call far 23E4:0644
5935  EB 7B           jmp 0x59b2
loc_5937:
5937  3D FC 00        cmp ax, 0xfc
593A  75 15           jne 0x5951
593C  BF DF 57        mov di, 0x57df
593F  0E              push cs
5940  57              push di
5941  C4 7E 08        les di, ptr [bp + 8]
5944  06              push es
5945  57              push di
5946  B8 0C 00        mov ax, 0xc
5949  50              push ax
594A  9A 44 06 E4 23  call far 23E4:0644
594F  EB 61           jmp 0x59b2
loc_5951:
5951  3D FD 00        cmp ax, 0xfd
5954  75 15           jne 0x596b
5956  BF E6 57        mov di, 0x57e6
5959  0E              push cs
595A  57              push di
595B  C4 7E 08        les di, ptr [bp + 8]
595E  06              push es
595F  57              push di
5960  B8 0C 00        mov ax, 0xc
5963  50              push ax
5964  9A 44 06 E4 23  call far 23E4:0644
5969  EB 47           jmp 0x59b2
loc_596B:
596B  3D FE 00        cmp ax, 0xfe
596E  75 15           jne 0x5985
5970  BF EC 57        mov di, 0x57ec
5973  0E              push cs
5974  57              push di
5975  C4 7E 08        les di, ptr [bp + 8]
5978  06              push es
5979  57              push di
597A  B8 0C 00        mov ax, 0xc
597D  50              push ax
597E  9A 44 06 E4 23  call far 23E4:0644
5983  EB 2D           jmp 0x59b2
loc_5985:
5985  3D FF 00        cmp ax, 0xff
5988  75 15           jne 0x599f
598A  BF F7 57        mov di, 0x57f7
598D  0E              push cs
598E  57              push di
598F  C4 7E 08        les di, ptr [bp + 8]
5992  06              push es
5993  57              push di
5994  B8 0C 00        mov ax, 0xc
5997  50              push ax
5998  9A 44 06 E4 23  call far 23E4:0644
599D  EB 13           jmp 0x59b2
loc_599F:
599F  BF FF 57        mov di, 0x57ff
59A2  0E              push cs
59A3  57              push di
59A4  C4 7E 08        les di, ptr [bp + 8]
59A7  06              push es
59A8  57              push di
59A9  B8 0C 00        mov ax, 0xc
59AC  50              push ax
59AD  9A 44 06 E4 23  call far 23E4:0644
loc_59B2:
59B2  89 EC           mov sp, bp
59B4  5D              pop bp
59B5  CA 02 00        retf 2
; data (not reached as code), 32 bytes
59B8                  db 98 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
59C8                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................

; ---- routine 1771:59D8  (found by: call, far)
sub_59D8:
59D8  55              push bp
59D9  89 E5           mov bp, sp
59DB  83 EC 02        sub sp, 2
59DE  C4 3E 23 A9     les di, ptr [0xa923]
59E2  26 8A 45 3C     mov al, byte ptr es:[di + 0x3c]
59E6  50              push ax
59E7  BF B8 59        mov di, 0x59b8
59EA  0E              push cs
59EB  57              push di
59EC  9A DF 08 E4 23  call far 23E4:08DF
59F1  75 04           jne 0x59f7
59F3  B0 00           mov al, 0
59F5  EB 02           jmp 0x59f9
loc_59F7:
59F7  B0 01           mov al, 1
loc_59F9:
59F9  88 46 FF        mov byte ptr [bp - 1], al
59FC  8A 46 FF        mov al, byte ptr [bp - 1]
59FF  89 EC           mov sp, bp
5A01  5D              pop bp
5A02  CB              retf

; ---- routine 1771:5A03  (found by: call, far)
sub_5A03:
5A03  55              push bp
5A04  89 E5           mov bp, sp
5A06  83 EC 06        sub sp, 6
5A09  C4 7E 06        les di, ptr [bp + 6]
5A0C  89 7E FB        mov word ptr [bp - 5], di
5A0F  8C 46 FD        mov word ptr [bp - 3], es
5A12  C4 7E FB        les di, ptr [bp - 5]
5A15  26 8A 45 02     mov al, byte ptr es:[di + 2]
5A19  50              push ax
5A1A  BF 3E 0F        mov di, 0xf3e
5A1D  1E              push ds
5A1E  57              push di
5A1F  9A DF 08 E4 23  call far 23E4:08DF
5A24  75 04           jne 0x5a2a
5A26  B0 00           mov al, 0
5A28  EB 02           jmp 0x5a2c
loc_5A2A:
5A2A  B0 01           mov al, 1
loc_5A2C:
5A2C  88 46 FF        mov byte ptr [bp - 1], al
5A2F  8A 46 FF        mov al, byte ptr [bp - 1]
5A32  89 EC           mov sp, bp
5A34  5D              pop bp
5A35  CA 04 00        retf 4

; ---- routine 1771:5A38  (found by: call, far)
sub_5A38:
5A38  55              push bp
5A39  89 E5           mov bp, sp
5A3B  83 EC 06        sub sp, 6
5A3E  C4 7E 06        les di, ptr [bp + 6]
5A41  89 7E FB        mov word ptr [bp - 5], di
5A44  8C 46 FD        mov word ptr [bp - 3], es
5A47  C4 7E FB        les di, ptr [bp - 5]
5A4A  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
5A4F  75 2C           jne 0x5a7d
5A51  8B 46 0A        mov ax, word ptr [bp + 0xa]
5A54  BA BF 00        mov dx, 0xbf
5A57  F7 E2           mul dx
5A59  C4 3E 17 A9     les di, ptr [0xa917]
5A5D  03 F8           add di, ax
5A5F  26 8A 4D 2C     mov cl, byte ptr es:[di + 0x2c]
5A63  C4 7E FB        les di, ptr [bp - 5]
5A66  26 8B 45 06     mov ax, word ptr es:[di + 6]
5A6A  BA BF 00        mov dx, 0xbf
5A6D  F7 E2           mul dx
5A6F  C4 3E 17 A9     les di, ptr [0xa917]
5A73  03 F8           add di, ax
5A75  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
5A79  3A C1           cmp al, cl
5A7B  75 04           jne 0x5a81
loc_5A7D:
5A7D  B0 00           mov al, 0
5A7F  EB 02           jmp 0x5a83
loc_5A81:
5A81  B0 01           mov al, 1
loc_5A83:
5A83  88 46 FF        mov byte ptr [bp - 1], al
5A86  8A 46 FF        mov al, byte ptr [bp - 1]
5A89  89 EC           mov sp, bp
5A8B  5D              pop bp
5A8C  CA 06 00        retf 6

; ---- routine 1771:5A8F  (found by: far)
sub_5A8F:
5A8F  55              push bp
5A90  89 E5           mov bp, sp
5A92  83 EC 02        sub sp, 2
5A95  FF 76 0A        push word ptr [bp + 0xa]
5A98  C4 7E 06        les di, ptr [bp + 6]
5A9B  06              push es
5A9C  57              push di
5A9D  0E              push cs
5A9E  E8 97 FF        call 0x5a38
5AA1  08 C0           or al, al
5AA3  75 11           jne 0x5ab6
5AA5  C4 7E 06        les di, ptr [bp + 6]
5AA8  06              push es
5AA9  57              push di
5AAA  0E              push cs
5AAB  E8 55 FF        call 0x5a03
5AAE  08 C0           or al, al
5AB0  75 04           jne 0x5ab6
5AB2  B0 00           mov al, 0
5AB4  EB 02           jmp 0x5ab8
loc_5AB6:
5AB6  B0 01           mov al, 1
loc_5AB8:
5AB8  88 46 FF        mov byte ptr [bp - 1], al
5ABB  8A 46 FF        mov al, byte ptr [bp - 1]
5ABE  89 EC           mov sp, bp
5AC0  5D              pop bp
5AC1  CA 06 00        retf 6

; ---- routine 1771:5AC4  (found by: call)
sub_5AC4:
5AC4  55              push bp
5AC5  89 E5           mov bp, sp
5AC7  81 EC 06 01     sub sp, 0x106
5ACB  C4 3E 23 A9     les di, ptr [0xa923]
5ACF  89 7E FA        mov word ptr [bp - 6], di
5AD2  8C 46 FC        mov word ptr [bp - 4], es
5AD5  BF 26 17        mov di, 0x1726
5AD8  1E              push ds
5AD9  57              push di
5ADA  BF 6E A9        mov di, 0xa96e
5ADD  1E              push ds
5ADE  57              push di
5ADF  9A 29 03 4B 21  call far 214B:0329
5AE4  80 7E 06 00     cmp byte ptr [bp + 6], 0
5AE8  74 11           je 0x5afb
5AEA  BF 90 11        mov di, 0x1190
5AED  1E              push ds
5AEE  57              push di
5AEF  BF 6E A9        mov di, 0xa96e
5AF2  1E              push ds
5AF3  57              push di
5AF4  9A 29 03 4B 21  call far 214B:0329
5AF9  EB 29           jmp 0x5b24
loc_5AFB:
5AFB  8B 46 04        mov ax, word ptr [bp + 4]
5AFE  BA 65 00        mov dx, 0x65
5B01  F7 E2           mul dx
5B03  8B F8           mov di, ax
5B05  81 C7 31 12     add di, 0x1231
5B09  1E              push ds
5B0A  57              push di
5B0B  BF 6E A9        mov di, 0xa96e
5B0E  1E              push ds
5B0F  57              push di
5B10  9A 29 03 4B 21  call far 214B:0329
5B15  BF 30 12        mov di, 0x1230
5B18  1E              push ds
5B19  57              push di
5B1A  BF 6E A9        mov di, 0xa96e
5B1D  1E              push ds
5B1E  57              push di
5B1F  9A 29 03 4B 21  call far 214B:0329
loc_5B24:
5B24  B0 0E           mov al, 0xe
5B26  50              push ax
5B27  8A 46 08        mov al, byte ptr [bp + 8]
5B2A  98              cwde
5B2B  BA 0B 00        mov dx, 0xb
5B2E  F7 E2           mul dx
5B30  8B F8           mov di, ax
5B32  81 C7 5E 0F     add di, 0xf5e
5B36  1E              push ds
5B37  57              push di
5B38  8A 46 06        mov al, byte ptr [bp + 6]
5B3B  98              cwde
5B3C  8B F8           mov di, ax
5B3E  8A 85 74 0F     mov al, byte ptr [di + 0xf74]
5B42  50              push ax
5B43  B0 1E           mov al, 0x1e
5B45  50              push ax
5B46  BF 6E A9        mov di, 0xa96e
5B49  1E              push ds
5B4A  57              push di
5B4B  9A C8 02 4B 21  call far 214B:02C8
5B50  B0 0F           mov al, 0xf
5B52  50              push ax
5B53  8D BE FA FE     lea di, [bp - 0x106]
5B57  16              push ss
5B58  57              push di
5B59  C4 7E FA        les di, ptr [bp - 6]
5B5C  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
5B60  3A 46 06        cmp al, byte ptr [bp + 6]
5B63  75 04           jne 0x5b69
5B65  B0 00           mov al, 0
5B67  EB 02           jmp 0x5b6b
loc_5B69:
5B69  B0 01           mov al, 1
loc_5B6B:
5B6B  30 E4           xor ah, ah
5B6D  D1 E0           shl ax, 1
5B6F  8B D0           mov dx, ax
5B71  C4 7E FA        les di, ptr [bp - 6]
5B74  26 8B 45 38     mov ax, word ptr es:[di + 0x38]
5B78  D1 E0           shl ax, 1
5B7A  C4 7E FA        les di, ptr [bp - 6]
5B7D  26 03 45 3A     add ax, word ptr es:[di + 0x3a]
5B81  2B C2           sub ax, dx
5B83  31 D2           xor dx, dx
5B85  52              push dx
5B86  50              push ax
5B87  9A DA 09 4B 21  call far 214B:09DA
5B8C  8A 46 06        mov al, byte ptr [bp + 6]
5B8F  30 E4           xor ah, ah
5B91  8B D0           mov dx, ax
5B93  B8 02 00        mov ax, 2
5B96  2B C2           sub ax, dx
5B98  50              push ax
5B99  8A 46 06        mov al, byte ptr [bp + 6]
5B9C  30 E4           xor ah, ah
5B9E  D1 E0           shl ax, 1
5BA0  8B D0           mov dx, ax
5BA2  B8 31 00        mov ax, 0x31
5BA5  2B C2           sub ax, dx
5BA7  50              push ax
5BA8  BF 6E A9        mov di, 0xa96e
5BAB  1E              push ds
5BAC  57              push di
5BAD  9A C8 02 4B 21  call far 214B:02C8
5BB2  80 7E 06 00     cmp byte ptr [bp + 6], 0
5BB6  74 07           je 0x5bbf
5BB8  C7 46 FE 05 00  mov word ptr [bp - 2], 5
5BBD  EB 06           jmp 0x5bc5
loc_5BBF:
5BBF  8B 46 04        mov ax, word ptr [bp + 4]
5BC2  89 46 FE        mov word ptr [bp - 2], ax
loc_5BC5:
5BC5  8B 46 FE        mov ax, word ptr [bp - 2]
5BC8  D1 E0           shl ax, 1
5BCA  C4 7E FA        les di, ptr [bp - 6]
5BCD  03 F8           add di, ax
5BCF  26 83 7D 2C 00  cmp word ptr es:[di + 0x2c], 0
5BD4  76 1A           jbe 0x5bf0
5BD6  8B 46 FE        mov ax, word ptr [bp - 2]
5BD9  D1 E0           shl ax, 1
5BDB  C4 7E FA        les di, ptr [bp - 6]
5BDE  03 F8           add di, ax
5BE0  26 FF 75 2C     push word ptr es:[di + 0x2c]
5BE4  B8 01 00        mov ax, 1
5BE7  50              push ax
5BE8  B8 13 00        mov ax, 0x13
5BEB  50              push ax
5BEC  0E              push cs
5BED  E8 68 B3        call 0xf58
loc_5BF0:
5BF0  89 EC           mov sp, bp
5BF2  5D              pop bp
5BF3  C2 06 00        ret 6

; ---- routine 1771:5BF6  (found by: far)
sub_5BF6:
5BF6  55              push bp
5BF7  89 E5           mov bp, sp
5BF9  83 EC 04        sub sp, 4
5BFC  C4 3E 23 A9     les di, ptr [0xa923]
5C00  89 7E FC        mov word ptr [bp - 4], di
5C03  8C 46 FE        mov word ptr [bp - 2], es
5C06  BF F2 26        mov di, 0x26f2
5C09  1E              push ds
5C0A  57              push di
5C0B  BF 6E A9        mov di, 0xa96e
5C0E  1E              push ds
5C0F  57              push di
5C10  9A 29 03 4B 21  call far 214B:0329
5C15  0E              push cs
5C16  E8 BF FD        call 0x59d8
5C19  50              push ax
5C1A  C4 7E FC        les di, ptr [bp - 4]
5C1D  26 80 7D 3C 05  cmp byte ptr es:[di + 0x3c], 5
5C22  73 04           jae 0x5c28
5C24  B0 00           mov al, 0
5C26  EB 02           jmp 0x5c2a
loc_5C28:
5C28  B0 01           mov al, 1
loc_5C2A:
5C2A  50              push ax
5C2B  C4 7E FC        les di, ptr [bp - 4]
5C2E  26 8A 45 01     mov al, byte ptr es:[di + 1]
5C32  30 E4           xor ah, ah
5C34  05 80 00        add ax, 0x80
5C37  BA 03 00        mov dx, 3
5C3A  F7 E2           mul dx
5C3C  C4 3E 1F A9     les di, ptr [0xa91f]
5C40  03 F8           add di, ax
5C42  26 8A 05        mov al, byte ptr es:[di]
5C45  30 E4           xor ah, ah
5C47  BA BF 00        mov dx, 0xbf
5C4A  F7 E2           mul dx
5C4C  C4 3E 17 A9     les di, ptr [0xa917]
5C50  03 F8           add di, ax
5C52  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
5C56  30 E4           xor ah, ah
5C58  50              push ax
5C59  E8 68 FE        call 0x5ac4
5C5C  89 EC           mov sp, bp
5C5E  5D              pop bp
5C5F  CB              retf

; ---- routine 1771:5C60  (found by: far)
sub_5C60:
5C60  55              push bp
5C61  89 E5           mov bp, sp
5C63  83 EC 06        sub sp, 6
5C66  C4 7E 06        les di, ptr [bp + 6]
5C69  89 7E FA        mov word ptr [bp - 6], di
5C6C  8C 46 FC        mov word ptr [bp - 4], es
5C6F  C4 7E FA        les di, ptr [bp - 6]
5C72  26 8A 05        mov al, byte ptr es:[di]
5C75  98              cwde
5C76  8B D0           mov dx, ax
5C78  C4 7E FA        les di, ptr [bp - 6]
5C7B  26 8A 45 01     mov al, byte ptr es:[di + 1]
5C7F  98              cwde
5C80  2B C2           sub ax, dx
5C82  09 C0           or ax, ax
5C84  79 02           jns 0x5c88
5C86  F7 D8           neg ax
loc_5C88:
5C88  89 46 FE        mov word ptr [bp - 2], ax
5C8B  8B 46 FE        mov ax, word ptr [bp - 2]
5C8E  89 EC           mov sp, bp
5C90  5D              pop bp
5C91  CA 04 00        retf 4

; ---- routine 1771:5C94  (found by: call, far)
sub_5C94:
5C94  55              push bp
5C95  89 E5           mov bp, sp
5C97  83 EC 06        sub sp, 6
5C9A  C4 7E 06        les di, ptr [bp + 6]
5C9D  89 7E FA        mov word ptr [bp - 6], di
5CA0  8C 46 FC        mov word ptr [bp - 4], es
5CA3  C4 7E FA        les di, ptr [bp - 6]
5CA6  26 80 7D 03 01  cmp byte ptr es:[di + 3], 1
5CAB  74 04           je 0x5cb1
5CAD  B0 00           mov al, 0
5CAF  EB 02           jmp 0x5cb3
loc_5CB1:
5CB1  B0 01           mov al, 1
loc_5CB3:
5CB3  98              cwde
5CB4  D1 E0           shl ax, 1
5CB6  C4 7E FA        les di, ptr [bp - 6]
5CB9  03 F8           add di, ax
5CBB  26 8B 45 04     mov ax, word ptr es:[di + 4]
5CBF  89 46 FE        mov word ptr [bp - 2], ax
5CC2  8B 46 FE        mov ax, word ptr [bp - 2]
5CC5  89 EC           mov sp, bp
5CC7  5D              pop bp
5CC8  CA 04 00        retf 4

; ---- routine 1771:5CCB  (found by: call, far)
sub_5CCB:
5CCB  55              push bp
5CCC  89 E5           mov bp, sp
5CCE  83 EC 06        sub sp, 6
5CD1  C4 7E 06        les di, ptr [bp + 6]
5CD4  89 7E FA        mov word ptr [bp - 6], di
5CD7  8C 46 FC        mov word ptr [bp - 4], es
5CDA  C4 7E FA        les di, ptr [bp - 6]
5CDD  26 80 7D 03 00  cmp byte ptr es:[di + 3], 0
5CE2  74 04           je 0x5ce8
5CE4  B0 00           mov al, 0
5CE6  EB 02           jmp 0x5cea
loc_5CE8:
5CE8  B0 01           mov al, 1
loc_5CEA:
5CEA  98              cwde
5CEB  D1 E0           shl ax, 1
5CED  C4 7E FA        les di, ptr [bp - 6]
5CF0  03 F8           add di, ax
5CF2  26 8B 45 04     mov ax, word ptr es:[di + 4]
5CF6  89 46 FE        mov word ptr [bp - 2], ax
5CF9  8B 46 FE        mov ax, word ptr [bp - 2]
5CFC  89 EC           mov sp, bp
5CFE  5D              pop bp
5CFF  CA 04 00        retf 4

