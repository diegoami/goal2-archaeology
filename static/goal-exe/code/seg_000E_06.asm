; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 6 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:47E6  (found by: call)
sub_47E6:
47E6  55              push bp
47E7  89 E5           mov bp, sp
47E9  83 EC 2A        sub sp, 0x2a
47EC  C4 7E 0A        les di, ptr [bp + 0xa]
47EF  06              push es
47F0  57              push di
47F1  8D 7E EB        lea di, [bp - 0x15]
47F4  16              push ss
47F5  57              push di
47F6  B8 14 00        mov ax, 0x14
47F9  50              push ax
47FA  9A 44 06 E4 23  call far 23E4:0644
47FF  C4 7E 06        les di, ptr [bp + 6]
4802  06              push es
4803  57              push di
4804  8D 7E D6        lea di, [bp - 0x2a]
4807  16              push ss
4808  57              push di
4809  B8 14 00        mov ax, 0x14
480C  50              push ax
480D  9A 44 06 E4 23  call far 23E4:0644
4812  9A FA 06 4B 21  call far 214B:06FA
4817  3C 00           cmp al, 0
4819  75 0E           jne 0x4829
481B  B8 0A 00        mov ax, 0xa
481E  50              push ax
481F  BF BC 47        mov di, 0x47bc
4822  0E              push cs
4823  57              push di
4824  E8 E4 BE        call 0x70b
4827  EB 10           jmp 0x4839
loc_4829:
4829  3C 01           cmp al, 1
482B  75 0C           jne 0x4839
482D  B8 0A 00        mov ax, 0xa
4830  50              push ax
4831  BF D1 47        mov di, 0x47d1
4834  0E              push cs
4835  57              push di
4836  E8 D2 BE        call 0x70b
loc_4839:
4839  B8 0B 00        mov ax, 0xb
483C  50              push ax
483D  8D 7E EB        lea di, [bp - 0x15]
4840  16              push ss
4841  57              push di
4842  E8 C6 BE        call 0x70b
4845  80 7E D6 00     cmp byte ptr [bp - 0x2a], 0
4849  74 0C           je 0x4857
484B  B8 0C 00        mov ax, 0xc
484E  50              push ax
484F  8D 7E D6        lea di, [bp - 0x2a]
4852  16              push ss
4853  57              push di
4854  E8 B4 BE        call 0x70b
loc_4857:
4857  8B 7E 04        mov di, word ptr [bp + 4]
485A  36 C6 45 FF 01  mov byte ptr ss:[di - 1], 1
485F  89 EC           mov sp, bp
4861  5D              pop bp
4862  C2 0A 00        ret 0xa

; ---- routine 000E:4865  (found by: call)
sub_4865:
4865  55              push bp
4866  89 E5           mov bp, sp
4868  83 EC 02        sub sp, 2
486B  8B 7E 04        mov di, word ptr [bp + 4]
486E  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4872  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4876  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
487A  98              cwde
487B  BA 0A 00        mov dx, 0xa
487E  F7 E2           mul dx
4880  8B F8           mov di, ax
4882  80 BD 84 7B 0A  cmp byte ptr [di + 0x7b84], 0xa
4887  77 40           ja 0x48c9
4889  8B 7E 04        mov di, word ptr [bp + 4]
488C  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4890  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4894  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
4898  98              cwde
4899  BA 0A 00        mov dx, 0xa
489C  F7 E2           mul dx
489E  8B F8           mov di, ax
48A0  80 BD 86 7B 01  cmp byte ptr [di + 0x7b86], 1
48A5  77 22           ja 0x48c9
48A7  8B 7E 04        mov di, word ptr [bp + 4]
48AA  36 8B 7D 04     mov di, word ptr ss:[di + 4]
48AE  36 8B 7D 04     mov di, word ptr ss:[di + 4]
48B2  36 8A 45 FF     mov al, byte ptr ss:[di - 1]
48B6  98              cwde
48B7  BA 0A 00        mov dx, 0xa
48BA  F7 E2           mul dx
48BC  8B F8           mov di, ax
48BE  80 BD 85 7B 02  cmp byte ptr [di + 0x7b85], 2
48C3  77 04           ja 0x48c9
48C5  B0 00           mov al, 0
48C7  EB 02           jmp 0x48cb
loc_48C9:
48C9  B0 01           mov al, 1
loc_48CB:
48CB  88 46 FF        mov byte ptr [bp - 1], al
48CE  8A 46 FF        mov al, byte ptr [bp - 1]
48D1  89 EC           mov sp, bp
48D3  5D              pop bp
48D4  C2 02 00        ret 2
; data (not reached as code), 432 bytes
48D7                  db 01 22   ; ."
48D9                  pstr ' is not'
48E1                  pstr 'up to scratch"'
48F0                  pstr ' must'
48F6                  pstr 'win some games'
4905                  pstr '"we are considering'
4919                  pstr 'a new manager"'
4928                  pstr 'simply had to go"'
493A                  pstr '"this dirty play'
494B                  pstr 'destroys the game"'
495E                  pstr '"friendly matches'
4970                  pstr 'should be friendly"'
4984                  pstr '"a disgraceful lack'
4998                  pstr 'of sportsmanship"'
49AA                  pstr '"it would be nice'
49BC                  pstr 'to see fair play"'
49CE                  pstr '"football came'
49DD                  pstr 'second best"'
49EA                  pstr '"keep up the good'
49FC                  pstr 'work '
4A02                  pstr '"a satisfactory'
4A12                  pstr 'result"'
4A1A                  pstr 'is doing the job"'
4A2C                  pstr '"an enjoyable match"'
4A41                  db 00   ; .
4A42                  pstr 'has done very well"'
4A56                  pstr '"a disappointing'
4A67                  pstr 'exit"'
4A6D                  pstr '"this is'
4A76                  pstr 'not good enough"'

; ---- routine 000E:4A87  (found by: call)
sub_4A87:
4A87  55              push bp
4A88  89 E5           mov bp, sp
4A8A  81 EC 0A 02     sub sp, 0x20a
4A8E  8B 7E 04        mov di, word ptr [bp + 4]
4A91  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4A95  36 C4 7D 04     les di, ptr ss:[di + 4]
4A99  89 7E FB        mov word ptr [bp - 5], di
4A9C  8C 46 FD        mov word ptr [bp - 3], es
4A9F  8B 7E 04        mov di, word ptr [bp + 4]
4AA2  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4AA6  36 8B 45 08     mov ax, word ptr ss:[di + 8]
4AAA  BA BF 00        mov dx, 0xbf
4AAD  F7 E2           mul dx
4AAF  C4 3E 17 A9     les di, ptr [0xa917]
4AB3  03 F8           add di, ax
4AB5  89 7E F7        mov word ptr [bp - 9], di
4AB8  8C 46 F9        mov word ptr [bp - 7], es
4ABB  C6 46 FF 00     mov byte ptr [bp - 1], 0
4ABF  8B 7E 04        mov di, word ptr [bp + 4]
4AC2  36 FF 75 04     push word ptr ss:[di + 4]
4AC6  E8 AE C0        call 0xb77
4AC9  3D FA FF        cmp ax, 0xfffa
4ACC  75 3B           jne 0x4b09
4ACE  8D BE F7 FD     lea di, [bp - 0x209]
4AD2  16              push ss
4AD3  57              push di
4AD4  BF D7 48        mov di, 0x48d7
4AD7  0E              push cs
4AD8  57              push di
4AD9  9A 2A 06 E4 23  call far 23E4:062A
4ADE  8D BE F7 FE     lea di, [bp - 0x109]
4AE2  16              push ss
4AE3  57              push di
4AE4  8B 7E 04        mov di, word ptr [bp + 4]
4AE7  36 FF 75 04     push word ptr ss:[di + 4]
4AEB  E8 DD BF        call 0xacb
4AEE  9A B7 06 E4 23  call far 23E4:06B7
4AF3  BF D9 48        mov di, 0x48d9
4AF6  0E              push cs
4AF7  57              push di
4AF8  9A B7 06 E4 23  call far 23E4:06B7
4AFD  BF E1 48        mov di, 0x48e1
4B00  0E              push cs
4B01  57              push di
4B02  55              push bp
4B03  E8 E0 FC        call 0x47e6
4B06  E9 A5 02        jmp 0x4dae
loc_4B09:
4B09  3D F9 FF        cmp ax, 0xfff9
4B0C  75 3B           jne 0x4b49
4B0E  8D BE F7 FD     lea di, [bp - 0x209]
4B12  16              push ss
4B13  57              push di
4B14  BF D7 48        mov di, 0x48d7
4B17  0E              push cs
4B18  57              push di
4B19  9A 2A 06 E4 23  call far 23E4:062A
4B1E  8D BE F7 FE     lea di, [bp - 0x109]
4B22  16              push ss
4B23  57              push di
4B24  8B 7E 04        mov di, word ptr [bp + 4]
4B27  36 FF 75 04     push word ptr ss:[di + 4]
4B2B  E8 1F C0        call 0xb4d
4B2E  9A B7 06 E4 23  call far 23E4:06B7
4B33  BF F0 48        mov di, 0x48f0
4B36  0E              push cs
4B37  57              push di
4B38  9A B7 06 E4 23  call far 23E4:06B7
4B3D  BF F6 48        mov di, 0x48f6
4B40  0E              push cs
4B41  57              push di
4B42  55              push bp
4B43  E8 A0 FC        call 0x47e6
4B46  E9 65 02        jmp 0x4dae
loc_4B49:
4B49  3D F6 FF        cmp ax, 0xfff6
4B4C  7C 16           jl 0x4b64
4B4E  3D F8 FF        cmp ax, 0xfff8
4B51  7F 11           jg 0x4b64
4B53  BF 05 49        mov di, 0x4905
4B56  0E              push cs
4B57  57              push di
4B58  BF 19 49        mov di, 0x4919
4B5B  0E              push cs
4B5C  57              push di
4B5D  55              push bp
4B5E  E8 85 FC        call 0x47e6
4B61  E9 4A 02        jmp 0x4dae
loc_4B64:
4B64  3D 01 FF        cmp ax, 0xff01
4B67  7C 36           jl 0x4b9f
4B69  3D F5 FF        cmp ax, 0xfff5
4B6C  7F 31           jg 0x4b9f
4B6E  8D BE F7 FD     lea di, [bp - 0x209]
4B72  16              push ss
4B73  57              push di
4B74  BF D7 48        mov di, 0x48d7
4B77  0E              push cs
4B78  57              push di
4B79  9A 2A 06 E4 23  call far 23E4:062A
4B7E  8D BE F7 FE     lea di, [bp - 0x109]
4B82  16              push ss
4B83  57              push di
4B84  8B 7E 04        mov di, word ptr [bp + 4]
4B87  36 FF 75 04     push word ptr ss:[di + 4]
4B8B  E8 3D BF        call 0xacb
4B8E  9A B7 06 E4 23  call far 23E4:06B7
4B93  BF 28 49        mov di, 0x4928
4B96  0E              push cs
4B97  57              push di
4B98  55              push bp
4B99  E8 4A FC        call 0x47e6
4B9C  E9 0F 02        jmp 0x4dae
loc_4B9F:
4B9F  55              push bp
4BA0  E8 C2 FC        call 0x4865
4BA3  08 C0           or al, al
4BA5  75 03           jne 0x4baa
4BA7  E9 80 00        jmp 0x4c2a
loc_4BAA:
4BAA  C4 7E FB        les di, ptr [bp - 5]
4BAD  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
4BB2  75 2D           jne 0x4be1
4BB4  9A FA 06 4B 21  call far 214B:06FA
4BB9  3C 00           cmp al, 0
4BBB  75 10           jne 0x4bcd
4BBD  BF 3A 49        mov di, 0x493a
4BC0  0E              push cs
4BC1  57              push di
4BC2  BF 4B 49        mov di, 0x494b
4BC5  0E              push cs
4BC6  57              push di
4BC7  55              push bp
4BC8  E8 1B FC        call 0x47e6
4BCB  EB 12           jmp 0x4bdf
loc_4BCD:
4BCD  3C 01           cmp al, 1
4BCF  75 0E           jne 0x4bdf
4BD1  BF 5E 49        mov di, 0x495e
4BD4  0E              push cs
4BD5  57              push di
4BD6  BF 70 49        mov di, 0x4970
4BD9  0E              push cs
4BDA  57              push di
4BDB  55              push bp
4BDC  E8 07 FC        call 0x47e6
loc_4BDF:
4BDF  EB 46           jmp 0x4c27
loc_4BE1:
4BE1  B8 04 00        mov ax, 4
4BE4  50              push ax
4BE5  9A B1 06 4B 21  call far 214B:06B1
4BEA  3D 01 00        cmp ax, 1
4BED  75 10           jne 0x4bff
4BEF  BF 84 49        mov di, 0x4984
4BF2  0E              push cs
4BF3  57              push di
4BF4  BF 98 49        mov di, 0x4998
4BF7  0E              push cs
4BF8  57              push di
4BF9  55              push bp
4BFA  E8 E9 FB        call 0x47e6
4BFD  EB 28           jmp 0x4c27
loc_4BFF:
4BFF  3D 02 00        cmp ax, 2
4C02  75 10           jne 0x4c14
4C04  BF AA 49        mov di, 0x49aa
4C07  0E              push cs
4C08  57              push di
4C09  BF BC 49        mov di, 0x49bc
4C0C  0E              push cs
4C0D  57              push di
4C0E  55              push bp
4C0F  E8 D4 FB        call 0x47e6
4C12  EB 13           jmp 0x4c27
loc_4C14:
4C14  3D 03 00        cmp ax, 3
4C17  75 0E           jne 0x4c27
4C19  BF CE 49        mov di, 0x49ce
4C1C  0E              push cs
4C1D  57              push di
4C1E  BF DD 49        mov di, 0x49dd
4C21  0E              push cs
4C22  57              push di
4C23  55              push bp
4C24  E8 BF FB        call 0x47e6
loc_4C27:
4C27  E9 84 01        jmp 0x4dae
loc_4C2A:
4C2A  C4 7E FB        les di, ptr [bp - 5]
4C2D  26 8A 45 03     mov al, byte ptr es:[di + 3]
4C31  8B 7E 04        mov di, word ptr [bp + 4]
4C34  36 8B 7D 04     mov di, word ptr ss:[di + 4]
4C38  36 3A 45 FF     cmp al, byte ptr ss:[di - 1]
4C3C  74 03           je 0x4c41
4C3E  E9 A8 00        jmp 0x4ce9
loc_4C41:
4C41  B8 10 00        mov ax, 0x10
4C44  50              push ax
4C45  9A B1 06 4B 21  call far 214B:06B1
4C4A  3D 01 00        cmp ax, 1
4C4D  75 3A           jne 0x4c89
4C4F  BF EA 49        mov di, 0x49ea
4C52  0E              push cs
4C53  57              push di
4C54  8D BE F7 FD     lea di, [bp - 0x209]
4C58  16              push ss
4C59  57              push di
4C5A  BF FC 49        mov di, 0x49fc
4C5D  0E              push cs
4C5E  57              push di
4C5F  9A 2A 06 E4 23  call far 23E4:062A
4C64  8D BE F7 FE     lea di, [bp - 0x109]
4C68  16              push ss
4C69  57              push di
4C6A  8B 7E 04        mov di, word ptr [bp + 4]
4C6D  36 FF 75 04     push word ptr ss:[di + 4]
4C71  E8 57 BE        call 0xacb
4C74  9A B7 06 E4 23  call far 23E4:06B7
4C79  BF D7 48        mov di, 0x48d7
4C7C  0E              push cs
4C7D  57              push di
4C7E  9A B7 06 E4 23  call far 23E4:06B7
4C83  55              push bp
4C84  E8 5F FB        call 0x47e6
4C87  EB 5D           jmp 0x4ce6
loc_4C89:
4C89  3D 02 00        cmp ax, 2
4C8C  75 10           jne 0x4c9e
4C8E  BF 02 4A        mov di, 0x4a02
4C91  0E              push cs
4C92  57              push di
4C93  BF 12 4A        mov di, 0x4a12
4C96  0E              push cs
4C97  57              push di
4C98  55              push bp
4C99  E8 4A FB        call 0x47e6
4C9C  EB 48           jmp 0x4ce6
loc_4C9E:
4C9E  3D 03 00        cmp ax, 3
4CA1  75 30           jne 0x4cd3
4CA3  8D BE F7 FD     lea di, [bp - 0x209]
4CA7  16              push ss
4CA8  57              push di
4CA9  BF D7 48        mov di, 0x48d7
4CAC  0E              push cs
4CAD  57              push di
4CAE  9A 2A 06 E4 23  call far 23E4:062A
4CB3  8D BE F7 FE     lea di, [bp - 0x109]
4CB7  16              push ss
4CB8  57              push di
4CB9  8B 7E 04        mov di, word ptr [bp + 4]
4CBC  36 FF 75 04     push word ptr ss:[di + 4]
4CC0  E8 08 BE        call 0xacb
4CC3  9A B7 06 E4 23  call far 23E4:06B7
4CC8  BF 1A 4A        mov di, 0x4a1a
4CCB  0E              push cs
4CCC  57              push di
4CCD  55              push bp
4CCE  E8 15 FB        call 0x47e6
4CD1  EB 13           jmp 0x4ce6
loc_4CD3:
4CD3  3D 04 00        cmp ax, 4
4CD6  75 0E           jne 0x4ce6
4CD8  BF 2C 4A        mov di, 0x4a2c
4CDB  0E              push cs
4CDC  57              push di
4CDD  BF 41 4A        mov di, 0x4a41
4CE0  0E              push cs
4CE1  57              push di
4CE2  55              push bp
4CE3  E8 00 FB        call 0x47e6
loc_4CE6:
4CE6  E9 C5 00        jmp 0x4dae
loc_4CE9:
4CE9  C4 7E F7        les di, ptr [bp - 9]
4CEC  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
4CF0  30 E4           xor ah, ah
4CF2  2D 80 00        sub ax, 0x80
4CF5  8B D0           mov dx, ax
4CF7  C4 3E 23 A9     les di, ptr [0xa923]
4CFB  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
4CFF  98              cwde
4D00  D1 E0           shl ax, 1
4D02  8B F0           mov si, ax
4D04  D1 E0           shl ax, 1
4D06  03 C6           add ax, si
4D08  C4 3E 23 A9     les di, ptr [0xa923]
4D0C  03 F8           add di, ax
4D0E  03 FA           add di, dx
4D10  26 8A 45 19     mov al, byte ptr es:[di + 0x19]
4D14  C4 7E FB        les di, ptr [bp - 5]
4D17  26 3A 45 02     cmp al, byte ptr es:[di + 2]
4D1B  73 48           jae 0x4d65
4D1D  C4 3E 23 A9     les di, ptr [0xa923]
4D21  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
4D25  98              cwde
4D26  8B F8           mov di, ax
4D28  8A 85 74 00     mov al, byte ptr [di + 0x74]
4D2C  C4 7E FB        les di, ptr [bp - 5]
4D2F  26 3A 45 02     cmp al, byte ptr es:[di + 2]
4D33  73 30           jae 0x4d65
4D35  8D BE F7 FD     lea di, [bp - 0x209]
4D39  16              push ss
4D3A  57              push di
4D3B  BF D7 48        mov di, 0x48d7
4D3E  0E              push cs
4D3F  57              push di
4D40  9A 2A 06 E4 23  call far 23E4:062A
4D45  8D BE F7 FE     lea di, [bp - 0x109]
4D49  16              push ss
4D4A  57              push di
4D4B  8B 7E 04        mov di, word ptr [bp + 4]
4D4E  36 FF 75 04     push word ptr ss:[di + 4]
4D52  E8 76 BD        call 0xacb
4D55  9A B7 06 E4 23  call far 23E4:06B7
4D5A  BF 42 4A        mov di, 0x4a42
4D5D  0E              push cs
4D5E  57              push di
4D5F  55              push bp
4D60  E8 83 FA        call 0x47e6
4D63  EB 49           jmp 0x4dae
loc_4D65:
4D65  C4 7E FB        les di, ptr [bp - 5]
4D68  26 8A 45 02     mov al, byte ptr es:[di + 2]
4D6C  50              push ax
4D6D  BF 43 A9        mov di, 0xa943
4D70  1E              push ds
4D71  57              push di
4D72  9A DF 08 E4 23  call far 23E4:08DF
4D77  74 10           je 0x4d89
4D79  BF 56 4A        mov di, 0x4a56
4D7C  0E              push cs
4D7D  57              push di
4D7E  BF 67 4A        mov di, 0x4a67
4D81  0E              push cs
4D82  57              push di
4D83  55              push bp
4D84  E8 5F FA        call 0x47e6
4D87  EB 25           jmp 0x4dae
loc_4D89:
4D89  8B 7E 04        mov di, word ptr [bp + 4]
4D8C  36 FF 75 04     push word ptr ss:[di + 4]
4D90  E8 48 BC        call 0x9db
4D93  08 C0           or al, al
4D95  74 17           je 0x4dae
4D97  9A FA 06 4B 21  call far 214B:06FA
4D9C  08 C0           or al, al
4D9E  74 0E           je 0x4dae
4DA0  BF 6D 4A        mov di, 0x4a6d
4DA3  0E              push cs
4DA4  57              push di
4DA5  BF 76 4A        mov di, 0x4a76
4DA8  0E              push cs
4DA9  57              push di
4DAA  55              push bp
4DAB  E8 38 FA        call 0x47e6
loc_4DAE:
4DAE  8A 46 FF        mov al, byte ptr [bp - 1]
4DB1  89 EC           mov sp, bp
4DB3  5D              pop bp
4DB4  C2 02 00        ret 2

; ---- routine 000E:4DB7  (found by: call)
sub_4DB7:
4DB7  55              push bp
4DB8  89 E5           mov bp, sp
4DBA  55              push bp
4DBB  E8 DD E3        call 0x319b
4DBE  55              push bp
4DBF  E8 06 EF        call 0x3cc8
4DC2  08 C0           or al, al
4DC4  74 12           je 0x4dd8
4DC6  55              push bp
4DC7  E8 BD FC        call 0x4a87
4DCA  08 C0           or al, al
4DCC  75 08           jne 0x4dd6
4DCE  B8 0A 00        mov ax, 0xa
4DD1  50              push ax
4DD2  55              push bp
4DD3  E8 6A F6        call 0x4440
loc_4DD6:
4DD6  EB 10           jmp 0x4de8
loc_4DD8:
4DD8  B8 06 00        mov ax, 6
4DDB  50              push ax
4DDC  55              push bp
4DDD  E8 60 F6        call 0x4440
4DE0  55              push bp
4DE1  E8 A3 FC        call 0x4a87
4DE4  08 C0           or al, al
4DE6  75 00           jne 0x4de8
loc_4DE8:
4DE8  89 EC           mov sp, bp
4DEA  5D              pop bp
4DEB  C2 02 00        ret 2
; data (not reached as code), 32 bytes
4DEE                  db 00 00 00 00 00 00 00 00 00 00 00 00 80 00 00 00   ; ................
4DFE                  db 00 00 00 00 00 00 00 00 00 08 00 00 00 00 00 00   ; ................

; ---- routine 000E:4E0E  (found by: call)
sub_4E0E:
4E0E  55              push bp
4E0F  89 E5           mov bp, sp
4E11  83 EC 22        sub sp, 0x22
4E14  C4 7E 04        les di, ptr [bp + 4]
4E17  89 7E E1        mov word ptr [bp - 0x1f], di
4E1A  8C 46 E3        mov word ptr [bp - 0x1d], es
4E1D  C6 46 FE 00     mov byte ptr [bp - 2], 0
4E21  C4 7E E1        les di, ptr [bp - 0x1f]
4E24  26 8B 45 06     mov ax, word ptr es:[di + 6]
4E28  3B 46 08        cmp ax, word ptr [bp + 8]
4E2B  74 04           je 0x4e31
4E2D  B0 00           mov al, 0
4E2F  EB 02           jmp 0x4e33
loc_4E31:
4E31  B0 01           mov al, 1
loc_4E33:
4E33  88 46 FF        mov byte ptr [bp - 1], al
4E36  8A 46 FF        mov al, byte ptr [bp - 1]
4E39  98              cwde
4E3A  C4 7E E1        les di, ptr [bp - 0x1f]
4E3D  03 F8           add di, ax
4E3F  26 80 3D 00     cmp byte ptr es:[di], 0
4E43  77 04           ja 0x4e49
4E45  B0 00           mov al, 0
4E47  EB 02           jmp 0x4e4b
loc_4E49:
4E49  B0 01           mov al, 1
loc_4E4B:
4E4B  30 E4           xor ah, ah
4E4D  89 46 FA        mov word ptr [bp - 6], ax
4E50  8D 7E E5        lea di, [bp - 0x1b]
4E53  16              push ss
4E54  57              push di
4E55  B8 15 00        mov ax, 0x15
4E58  50              push ax
4E59  31 C0           xor ax, ax
4E5B  50              push ax
4E5C  9A 18 00 4B 21  call far 214B:0018
4E61  8A 46 FF        mov al, byte ptr [bp - 1]
4E64  98              cwde
4E65  C4 7E E1        les di, ptr [bp - 0x1f]
4E68  03 F8           add di, ax
4E6A  26 8A 05        mov al, byte ptr es:[di]
4E6D  30 E4           xor ah, ah
4E6F  89 46 DF        mov word ptr [bp - 0x21], ax
4E72  B8 01 00        mov ax, 1
4E75  3B 46 DF        cmp ax, word ptr [bp - 0x21]
4E78  77 38           ja 0x4eb2
4E7A  89 46 FC        mov word ptr [bp - 4], ax
4E7D  EB 03           jmp 0x4e82
loc_4E7F:
4E7F  FF 46 FC        inc word ptr [bp - 4]
loc_4E82:
4E82  8B 46 FC        mov ax, word ptr [bp - 4]
4E85  BA 03 00        mov dx, 3
4E88  F7 E2           mul dx
4E8A  8B C8           mov cx, ax
4E8C  8A 46 FF        mov al, byte ptr [bp - 1]
4E8F  98              cwde
4E90  BA 21 00        mov dx, 0x21
4E93  F7 E2           mul dx
4E95  8B F8           mov di, ax
4E97  03 F9           add di, cx
4E99  FF B5 D1 7B     push word ptr [di + 0x7bd1]
4E9D  FF 76 08        push word ptr [bp + 8]
4EA0  9A 82 3A 71 17  call far 1771:3A82
4EA5  8B F8           mov di, ax
4EA7  FE 43 E5        inc byte ptr [bp + di - 0x1b]
4EAA  8B 46 FC        mov ax, word ptr [bp - 4]
4EAD  3B 46 DF        cmp ax, word ptr [bp - 0x21]
4EB0  75 CD           jne 0x4e7f
loc_4EB2:
4EB2  83 7E FA 00     cmp word ptr [bp - 6], 0
4EB6  76 24           jbe 0x4edc
4EB8  C7 46 FC 01 00  mov word ptr [bp - 4], 1
4EBD  EB 03           jmp 0x4ec2
loc_4EBF:
4EBF  FF 46 FC        inc word ptr [bp - 4]
loc_4EC2:
4EC2  8B 7E FC        mov di, word ptr [bp - 4]
4EC5  8A 43 E5        mov al, byte ptr [bp + di - 0x1b]
4EC8  8B 7E FA        mov di, word ptr [bp - 6]
4ECB  3A 43 E5        cmp al, byte ptr [bp + di - 0x1b]
4ECE  76 06           jbe 0x4ed6
4ED0  8B 46 FC        mov ax, word ptr [bp - 4]
4ED3  89 46 FA        mov word ptr [bp - 6], ax
loc_4ED6:
4ED6  83 7E FC 14     cmp word ptr [bp - 4], 0x14
4EDA  75 E3           jne 0x4ebf
loc_4EDC:
4EDC  E8 AF B4        call 0x38e
4EDF  55              push bp
4EE0  E8 F6 C2        call 0x11d9
4EE3  55              push bp
4EE4  E8 D0 FE        call 0x4db7
4EE7  55              push bp
4EE8  E8 07 D8        call 0x26f2
4EEB  B0 00           mov al, 0
4EED  50              push ax
4EEE  8B 46 08        mov ax, word ptr [bp + 8]
4EF1  BA BF 00        mov dx, 0xbf
4EF4  F7 E2           mul dx
4EF6  C4 3E 17 A9     les di, ptr [0xa917]
4EFA  03 F8           add di, ax
4EFC  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
4F00  30 E4           xor ah, ah
4F02  2D 80 00        sub ax, 0x80
4F05  8B D0           mov dx, ax
4F07  C4 3E 23 A9     les di, ptr [0xa923]
4F0B  26 8A 45 40     mov al, byte ptr es:[di + 0x40]
4F0F  98              cwde
4F10  D1 E0           shl ax, 1
4F12  8B F0           mov si, ax
4F14  D1 E0           shl ax, 1
4F16  03 C6           add ax, si
4F18  C4 3E 23 A9     les di, ptr [0xa923]
4F1C  03 F8           add di, ax
4F1E  03 FA           add di, dx
4F20  26 8A 45 19     mov al, byte ptr es:[di + 0x19]
4F24  C4 7E E1        les di, ptr [bp - 0x1f]
4F27  26 3A 45 02     cmp al, byte ptr es:[di + 2]
4F2B  73 14           jae 0x4f41
4F2D  C4 7E E1        les di, ptr [bp - 0x1f]
4F30  26 8A 45 02     mov al, byte ptr es:[di + 2]
4F34  50              push ax
4F35  BF 43 A9        mov di, 0xa943
4F38  1E              push ds
4F39  57              push di
4F3A  9A DF 08 E4 23  call far 23E4:08DF
4F3F  75 04           jne 0x4f45
loc_4F41:
4F41  B0 00           mov al, 0
4F43  EB 02           jmp 0x4f47
loc_4F45:
4F45  B0 01           mov al, 1
loc_4F47:
4F47  50              push ax
4F48  C4 7E E1        les di, ptr [bp - 0x1f]
4F4B  26 8A 45 03     mov al, byte ptr es:[di + 3]
4F4F  3A 46 FF        cmp al, byte ptr [bp - 1]
4F52  75 14           jne 0x4f68
4F54  C4 7E E1        les di, ptr [bp - 0x1f]
4F57  26 8A 45 02     mov al, byte ptr es:[di + 2]
4F5B  50              push ax
4F5C  BF EE 4D        mov di, 0x4dee
4F5F  0E              push cs
4F60  57              push di
4F61  9A DF 08 E4 23  call far 23E4:08DF
4F66  75 04           jne 0x4f6c
loc_4F68:
4F68  B0 00           mov al, 0
4F6A  EB 02           jmp 0x4f6e
loc_4F6C:
4F6C  B0 01           mov al, 1
loc_4F6E:
4F6E  50              push ax
4F6F  E8 84 B6        call 0x5f6
4F72  80 7E FE 00     cmp byte ptr [bp - 2], 0
4F76  74 1B           je 0x4f93
4F78  8B 46 08        mov ax, word ptr [bp + 8]
4F7B  BA BF 00        mov dx, 0xbf
4F7E  F7 E2           mul dx
4F80  C4 3E 17 A9     les di, ptr [0xa917]
4F84  03 F8           add di, ax
4F86  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
4F8A  30 E4           xor ah, ah
4F8C  2D 80 00        sub ax, 0x80
4F8F  50              push ax
4F90  E8 67 B2        call 0x1fa
loc_4F93:
4F93  89 EC           mov sp, bp
4F95  5D              pop bp
4F96  C2 06 00        ret 6
; data (not reached as code), 315 bytes
4F99                  pstr 'retires from the'
4FAA                  pstr 'international scene'
4FBE                  pstr 'is to retire'
4FCB                  pstr 'at the age of '
4FDA                  pstr 'quits international'
4FEE                  pstr 'football'
4FF7                  pstr 'with '
4FFD                  pstr ' caps'
5003                  pstr 'and '
5008                  pstr ' goals'
500F                  pstr '"he will be missed"'
5023                  db 00   ; .
5024                  pstr '"he distinguished'
5036                  pstr 'himself"'
503F                  pstr '"a great player"'
5050                  pstr '"one of the best"'
5062                  pstr 'HAS GONE !'
506D                  pstr 'GIVES UP !'
5078                  pstr 'HAS HAD ENOUGH !'
5089                  pstr 'SHOULD HAVE BEEN'
509A                  pstr 'CAPPED'
50A1                  pstr 'SHOULD HAVE HAD'
50B1                  pstr 'MORE CAPS'
50BB                  pstr 'WILL MISS'
50C5                  pstr 'SAD TO SEE'
50D0                  pstr ' GO'

; ---- routine 000E:50D4  (found by: call)
sub_50D4:
50D4  55              push bp
50D5  89 E5           mov bp, sp
50D7  81 EC 04 02     sub sp, 0x204
50DB  8B 46 06        mov ax, word ptr [bp + 6]
50DE  BA 14 00        mov dx, 0x14
50E1  F7 E2           mul dx
50E3  C4 3E 1B A9     les di, ptr [0xa91b]
50E7  03 F8           add di, ax
50E9  89 7E FC        mov word ptr [bp - 4], di
50EC  8C 46 FE        mov word ptr [bp - 2], es
50EF  E8 9C B2        call 0x38e
50F2  B8 01 00        mov ax, 1
50F5  50              push ax
50F6  8B 7E 04        mov di, word ptr [bp + 4]
50F9  36 8B 45 04     mov ax, word ptr ss:[di + 4]
50FD  B1 04           mov cl, 4
50FF  D3 E0           shl ax, cl
5101  C4 3E 68 9B     les di, ptr [0x9b68]
5105  03 F8           add di, ax
5107  06              push es
5108  57              push di
5109  E8 FF B5        call 0x70b
510C  B8 02 00        mov ax, 2
510F  50              push ax
5110  C4 7E FC        les di, ptr [bp - 4]
5113  26 8A 45 06     mov al, byte ptr es:[di + 6]
5117  30 E4           xor ah, ah
5119  BA 13 00        mov dx, 0x13
511C  F7 E2           mul dx
511E  8B F8           mov di, ax
5120  81 C7 B6 69     add di, 0x69b6
5124  1E              push ds
5125  57              push di
5126  E8 E2 B5        call 0x70b
5129  B8 03 00        mov ax, 3
512C  50              push ax
512D  8D BE FC FE     lea di, [bp - 0x104]
5131  16              push ss
5132  57              push di
5133  FF 76 06        push word ptr [bp + 6]
5136  9A 93 2E 71 17  call far 1771:2E93
513B  E8 CD B5        call 0x70b
513E  B8 03 00        mov ax, 3
5141  50              push ax
5142  9A B1 06 4B 21  call far 214B:06B1
5147  3D 01 00        cmp ax, 1
514A  75 1A           jne 0x5166
514C  B8 04 00        mov ax, 4
514F  50              push ax
5150  BF 99 4F        mov di, 0x4f99
5153  0E              push cs
5154  57              push di
5155  E8 B3 B5        call 0x70b
5158  B8 05 00        mov ax, 5
515B  50              push ax
515C  BF AA 4F        mov di, 0x4faa
515F  0E              push cs
5160  57              push di
5161  E8 A7 B5        call 0x70b
5164  EB 64           jmp 0x51ca
loc_5166:
5166  3D 02 00        cmp ax, 2
5169  75 42           jne 0x51ad
516B  B8 04 00        mov ax, 4
516E  50              push ax
516F  BF BE 4F        mov di, 0x4fbe
5172  0E              push cs
5173  57              push di
5174  E8 94 B5        call 0x70b
5177  B8 05 00        mov ax, 5
517A  50              push ax
517B  8D BE FC FD     lea di, [bp - 0x204]
517F  16              push ss
5180  57              push di
5181  BF CB 4F        mov di, 0x4fcb
5184  0E              push cs
5185  57              push di
5186  9A 2A 06 E4 23  call far 23E4:062A
518B  8D BE FC FE     lea di, [bp - 0x104]
518F  16              push ss
5190  57              push di
5191  C4 7E FC        les di, ptr [bp - 4]
5194  26 8A 45 01     mov al, byte ptr es:[di + 1]
5198  30 E4           xor ah, ah
519A  31 D2           xor dx, dx
519C  52              push dx
519D  50              push ax
519E  9A DA 09 4B 21  call far 214B:09DA
51A3  9A B7 06 E4 23  call far 23E4:06B7
51A8  E8 60 B5        call 0x70b
51AB  EB 1D           jmp 0x51ca
loc_51AD:
51AD  3D 03 00        cmp ax, 3
51B0  75 18           jne 0x51ca
51B2  B8 04 00        mov ax, 4
51B5  50              push ax
51B6  BF DA 4F        mov di, 0x4fda
51B9  0E              push cs
51BA  57              push di
51BB  E8 4D B5        call 0x70b
51BE  B8 05 00        mov ax, 5
51C1  50              push ax
51C2  BF EE 4F        mov di, 0x4fee
51C5  0E              push cs
51C6  57              push di
51C7  E8 41 B5        call 0x70b
loc_51CA:
51CA  C4 7E FC        les di, ptr [bp - 4]
51CD  26 83 7D 08 01  cmp word ptr es:[di + 8], 1
51D2  76 3C           jbe 0x5210
51D4  B8 06 00        mov ax, 6
51D7  50              push ax
51D8  8D BE FC FD     lea di, [bp - 0x204]
51DC  16              push ss
51DD  57              push di
51DE  BF F7 4F        mov di, 0x4ff7
51E1  0E              push cs
51E2  57              push di
51E3  9A 2A 06 E4 23  call far 23E4:062A
51E8  8D BE FC FE     lea di, [bp - 0x104]
51EC  16              push ss
51ED  57              push di
51EE  C4 7E FC        les di, ptr [bp - 4]
51F1  26 8B 45 08     mov ax, word ptr es:[di + 8]
51F5  31 D2           xor dx, dx
51F7  52              push dx
51F8  50              push ax
51F9  9A DA 09 4B 21  call far 214B:09DA
51FE  9A B7 06 E4 23  call far 23E4:06B7
5203  BF FD 4F        mov di, 0x4ffd
5206  0E              push cs
5207  57              push di
5208  9A B7 06 E4 23  call far 23E4:06B7
520D  E8 FB B4        call 0x70b
loc_5210:
5210  C4 7E FC        les di, ptr [bp - 4]
5213  26 83 7D 0A 01  cmp word ptr es:[di + 0xa], 1
5218  76 3C           jbe 0x5256
521A  B8 07 00        mov ax, 7
521D  50              push ax
521E  8D BE FC FD     lea di, [bp - 0x204]
5222  16              push ss
5223  57              push di
5224  BF 03 50        mov di, 0x5003
5227  0E              push cs
5228  57              push di
5229  9A 2A 06 E4 23  call far 23E4:062A
522E  8D BE FC FE     lea di, [bp - 0x104]
5232  16              push ss
5233  57              push di
5234  C4 7E FC        les di, ptr [bp - 4]
5237  26 8B 45 0A     mov ax, word ptr es:[di + 0xa]
523B  31 D2           xor dx, dx
523D  52              push dx
523E  50              push ax
523F  9A DA 09 4B 21  call far 214B:09DA
5244  9A B7 06 E4 23  call far 23E4:06B7
5249  BF 08 50        mov di, 0x5008
524C  0E              push cs
524D  57              push di
524E  9A B7 06 E4 23  call far 23E4:06B7
5253  E8 B5 B4        call 0x70b
loc_5256:
5256  B8 04 00        mov ax, 4
5259  50              push ax
525A  9A B1 06 4B 21  call far 214B:06B1
525F  3D 01 00        cmp ax, 1
5262  75 13           jne 0x5277
5264  B8 0A 00        mov ax, 0xa
5267  50              push ax
5268  BF 0F 50        mov di, 0x500f
526B  0E              push cs
526C  57              push di
526D  BF 23 50        mov di, 0x5023
5270  0E              push cs
5271  57              push di
5272  E8 F3 B5        call 0x868
5275  EB 46           jmp 0x52bd
loc_5277:
5277  3D 02 00        cmp ax, 2
527A  75 13           jne 0x528f
527C  B8 0A 00        mov ax, 0xa
527F  50              push ax
5280  BF 24 50        mov di, 0x5024
5283  0E              push cs
5284  57              push di
5285  BF 36 50        mov di, 0x5036
5288  0E              push cs
5289  57              push di
528A  E8 DB B5        call 0x868
528D  EB 2E           jmp 0x52bd
loc_528F:
528F  3D 03 00        cmp ax, 3
5292  75 13           jne 0x52a7
5294  B8 0A 00        mov ax, 0xa
5297  50              push ax
5298  BF 3F 50        mov di, 0x503f
529B  0E              push cs
529C  57              push di
529D  BF 23 50        mov di, 0x5023
52A0  0E              push cs
52A1  57              push di
52A2  E8 C3 B5        call 0x868
52A5  EB 16           jmp 0x52bd
loc_52A7:
52A7  3D 04 00        cmp ax, 4
52AA  75 11           jne 0x52bd
52AC  B8 0A 00        mov ax, 0xa
52AF  50              push ax
52B0  BF 50 50        mov di, 0x5050
52B3  0E              push cs
52B4  57              push di
52B5  BF 23 50        mov di, 0x5023
52B8  0E              push cs
52B9  57              push di
52BA  E8 AB B5        call 0x868
loc_52BD:
52BD  B8 03 00        mov ax, 3
52C0  50              push ax
52C1  9A B1 06 4B 21  call far 214B:06B1
52C6  3D 01 00        cmp ax, 1
52C9  75 1F           jne 0x52ea
52CB  8B 46 06        mov ax, word ptr [bp + 6]
52CE  BA 0B 00        mov dx, 0xb
52D1  F7 E2           mul dx
52D3  C4 3E 6C 9B     les di, ptr [0x9b6c]
52D7  03 F8           add di, ax
52D9  06              push es
52DA  57              push di
52DB  BF 62 50        mov di, 0x5062
52DE  0E              push cs
52DF  57              push di
52E0  BF 23 50        mov di, 0x5023
52E3  0E              push cs
52E4  57              push di
52E5  E8 47 B3        call 0x62f
52E8  EB 46           jmp 0x5330
loc_52EA:
52EA  3D 02 00        cmp ax, 2
52ED  75 1F           jne 0x530e
52EF  8B 46 06        mov ax, word ptr [bp + 6]
52F2  BA 0B 00        mov dx, 0xb
52F5  F7 E2           mul dx
52F7  C4 3E 6C 9B     les di, ptr [0x9b6c]
52FB  03 F8           add di, ax
52FD  06              push es
52FE  57              push di
52FF  BF 6D 50        mov di, 0x506d
5302  0E              push cs
5303  57              push di
5304  BF 23 50        mov di, 0x5023
5307  0E              push cs
5308  57              push di
5309  E8 23 B3        call 0x62f
530C  EB 22           jmp 0x5330
loc_530E:
530E  3D 03 00        cmp ax, 3
5311  75 1D           jne 0x5330
5313  8B 46 06        mov ax, word ptr [bp + 6]
5316  BA 0B 00        mov dx, 0xb
5319  F7 E2           mul dx
531B  C4 3E 6C 9B     les di, ptr [0x9b6c]
531F  03 F8           add di, ax
5321  06              push es
5322  57              push di
5323  BF 78 50        mov di, 0x5078
5326  0E              push cs
5327  57              push di
5328  BF 23 50        mov di, 0x5023
532B  0E              push cs
532C  57              push di
532D  E8 FF B2        call 0x62f
loc_5330:
5330  8B 7E 04        mov di, word ptr [bp + 4]
5333  36 FF 75 04     push word ptr ss:[di + 4]
5337  9A E7 10 71 17  call far 1771:10E7
533C  8B D0           mov dx, ax
533E  C4 7E FC        les di, ptr [bp - 4]
5341  26 8A 45 03     mov al, byte ptr es:[di + 3]
5345  30 E4           xor ah, ah
5347  05 81 FF        add ax, 0xff81
534A  3B C2           cmp ax, dx
534C  7C 04           jl 0x5352
534E  B0 00           mov al, 0
5350  EB 02           jmp 0x5354
loc_5352:
5352  B0 01           mov al, 1
loc_5354:
5354  8B 7E 04        mov di, word ptr [bp + 4]
5357  36 88 45 F4     mov byte ptr ss:[di - 0xc], al
535B  8B 7E 04        mov di, word ptr [bp + 4]
535E  36 80 7D F4 00  cmp byte ptr ss:[di - 0xc], 0
5363  74 03           je 0x5368
5365  E9 BB 00        jmp 0x5423
loc_5368:
5368  C4 7E FC        les di, ptr [bp - 4]
536B  26 83 7D 08 00  cmp word ptr es:[di + 8], 0
5370  75 20           jne 0x5392
5372  8B 46 06        mov ax, word ptr [bp + 6]
5375  BA 0B 00        mov dx, 0xb
5378  F7 E2           mul dx
537A  C4 3E 6C 9B     les di, ptr [0x9b6c]
537E  03 F8           add di, ax
5380  06              push es
5381  57              push di
5382  BF 89 50        mov di, 0x5089
5385  0E              push cs
5386  57              push di
5387  BF 9A 50        mov di, 0x509a
538A  0E              push cs
538B  57              push di
538C  E8 D0 B3        call 0x75f
538F  E9 91 00        jmp 0x5423
loc_5392:
5392  C4 7E FC        les di, ptr [bp - 4]
5395  26 83 7D 08 08  cmp word ptr es:[di + 8], 8
539A  73 1F           jae 0x53bb
539C  8B 46 06        mov ax, word ptr [bp + 6]
539F  BA 0B 00        mov dx, 0xb
53A2  F7 E2           mul dx
53A4  C4 3E 6C 9B     les di, ptr [0x9b6c]
53A8  03 F8           add di, ax
53AA  06              push es
53AB  57              push di
53AC  BF A1 50        mov di, 0x50a1
53AF  0E              push cs
53B0  57              push di
53B1  BF B1 50        mov di, 0x50b1
53B4  0E              push cs
53B5  57              push di
53B6  E8 A6 B3        call 0x75f
53B9  EB 68           jmp 0x5423
loc_53BB:
53BB  9A FA 06 4B 21  call far 214B:06FA
53C0  08 C0           or al, al
53C2  74 2D           je 0x53f1
53C4  8B 7E 04        mov di, word ptr [bp + 4]
53C7  36 8B 45 04     mov ax, word ptr ss:[di + 4]
53CB  B1 04           mov cl, 4
53CD  D3 E0           shl ax, cl
53CF  C4 3E 68 9B     les di, ptr [0x9b68]
53D3  03 F8           add di, ax
53D5  06              push es
53D6  57              push di
53D7  BF BB 50        mov di, 0x50bb
53DA  0E              push cs
53DB  57              push di
53DC  8B 46 06        mov ax, word ptr [bp + 6]
53DF  BA 0B 00        mov dx, 0xb
53E2  F7 E2           mul dx
53E4  C4 3E 6C 9B     les di, ptr [0x9b6c]
53E8  03 F8           add di, ax
53EA  06              push es
53EB  57              push di
53EC  E8 70 B3        call 0x75f
53EF  EB 32           jmp 0x5423
loc_53F1:
53F1  BF C5 50        mov di, 0x50c5
53F4  0E              push cs
53F5  57              push di
53F6  8D BE FC FE     lea di, [bp - 0x104]
53FA  16              push ss
53FB  57              push di
53FC  8B 46 06        mov ax, word ptr [bp + 6]
53FF  BA 0B 00        mov dx, 0xb
5402  F7 E2           mul dx
5404  C4 3E 6C 9B     les di, ptr [0x9b6c]
5408  03 F8           add di, ax
540A  06              push es
540B  57              push di
540C  9A 2A 06 E4 23  call far 23E4:062A
5411  BF D0 50        mov di, 0x50d0
5414  0E              push cs
5415  57              push di
5416  9A B7 06 E4 23  call far 23E4:06B7
541B  BF 23 50        mov di, 0x5023
541E  0E              push cs
541F  57              push di
5420  E8 3C B3        call 0x75f
loc_5423:
5423  89 EC           mov sp, bp
5425  5D              pop bp
5426  C2 04 00        ret 4
; data (not reached as code), 36 bytes
5429                  pstr 'SHOWS PROMISE'
5437                  db 00   ; .
5438                  pstr 'DESERVES A CAP'
5447                  pstr 'NEEDS'

