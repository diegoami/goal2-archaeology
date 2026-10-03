; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 23 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:E80D  (found by: far)
sub_E80D:
E80D  55              push bp
E80E  89 E5           mov bp, sp
E810  83 EC 22        sub sp, 0x22
E813  C4 7E 06        les di, ptr [bp + 6]
E816  06              push es
E817  57              push di
E818  E8 86 BC        call 0xa4a1
loc_E81B:
E81B  E8 3F BF        call 0xa75d
E81E  BF 36 3A        mov di, 0x3a36
E821  1E              push ds
E822  57              push di
E823  BF 6E A9        mov di, 0xa96e
E826  1E              push ds
E827  57              push di
E828  9A 29 03 4B 21  call far 214B:0329
E82D  B8 10 00        mov ax, 0x10
E830  50              push ax
E831  83 3E BE 0A 01  cmp word ptr [0xabe], 1
E836  74 04           je 0xe83c
E838  B0 00           mov al, 0
E83A  EB 02           jmp 0xe83e
loc_E83C:
E83C  B0 01           mov al, 1
loc_E83E:
E83E  98              cwde
E83F  8B F8           mov di, ax
E841  8A 85 C0 0A     mov al, byte ptr [di + 0xac0]
E845  30 E4           xor ah, ah
E847  50              push ax
E848  83 3E BE 0A 01  cmp word ptr [0xabe], 1
E84D  74 04           je 0xe853
E84F  B0 00           mov al, 0
E851  EB 02           jmp 0xe855
loc_E853:
E853  B0 01           mov al, 1
loc_E855:
E855  30 E4           xor ah, ah
E857  05 04 00        add ax, 4
E85A  50              push ax
E85B  9A C5 13 4B 21  call far 214B:13C5
E860  BF BE 0A        mov di, 0xabe
E863  1E              push ds
E864  57              push di
E865  B8 02 00        mov ax, 2
E868  50              push ax
E869  9A 60 15 4B 21  call far 214B:1560
E86E  A0 76 A9        mov al, byte ptr [0xa976]
E871  50              push ax
E872  9A B2 19 E4 23  call far 23E4:19B2
E877  3C 4E           cmp al, 0x4e
E879  74 04           je 0xe87f
E87B  3C 1B           cmp al, 0x1b
E87D  75 08           jne 0xe887
loc_E87F:
E87F  C7 06 BE 0A 02 00 mov word ptr [0xabe], 2
E885  EB 2A           jmp 0xe8b1
loc_E887:
E887  3C 59           cmp al, 0x59
E889  75 08           jne 0xe893
E88B  C7 06 BE 0A 01 00 mov word ptr [0xabe], 1
E891  EB 1E           jmp 0xe8b1
loc_E893:
E893  3C AE           cmp al, 0xae
E895  74 04           je 0xe89b
E897  3C AF           cmp al, 0xaf
E899  75 16           jne 0xe8b1
loc_E89B:
E89B  BF BE 0A        mov di, 0xabe
E89E  1E              push ds
E89F  57              push di
E8A0  B8 01 00        mov ax, 1
E8A3  50              push ax
E8A4  B8 02 00        mov ax, 2
E8A7  50              push ax
E8A8  B8 01 00        mov ax, 1
E8AB  50              push ax
E8AC  9A 86 1C 4B 21  call far 214B:1C86
loc_E8B1:
E8B1  A0 76 A9        mov al, byte ptr [0xa976]
E8B4  50              push ax
E8B5  8D 7E DE        lea di, [bp - 0x22]
E8B8  16              push ss
E8B9  57              push di
E8BA  BF 46 79        mov di, 0x7946
E8BD  1E              push ds
E8BE  57              push di
E8BF  B8 20 00        mov ax, 0x20
E8C2  50              push ax
E8C3  9A 31 08 E4 23  call far 23E4:0831
E8C8  BF ED E7        mov di, 0xe7ed
E8CB  0E              push cs
E8CC  57              push di
E8CD  9A 00 09 E4 23  call far 23E4:0900
E8D2  9A DF 08 E4 23  call far 23E4:08DF
E8D7  75 03           jne 0xe8dc
E8D9  E9 3F FF        jmp 0xe81b
loc_E8DC:
E8DC  83 3E BE 0A 01  cmp word ptr [0xabe], 1
E8E1  74 04           je 0xe8e7
E8E3  B0 00           mov al, 0
E8E5  EB 02           jmp 0xe8e9
loc_E8E7:
E8E7  B0 01           mov al, 1
loc_E8E9:
E8E9  88 46 FF        mov byte ptr [bp - 1], al
E8EC  C6 46 FE 00     mov byte ptr [bp - 2], 0
E8F0  EB 03           jmp 0xe8f5
loc_E8F2:
E8F2  FE 46 FE        inc byte ptr [bp - 2]
loc_E8F5:
E8F5  8A 46 FE        mov al, byte ptr [bp - 2]
E8F8  98              cwde
E8F9  8B F8           mov di, ax
E8FB  D1 E7           shl di, 1
E8FD  FF B5 34 9B     push word ptr [di - 0x64cc]
E901  0E              push cs
E902  E8 58 D3        call 0xbc5d
E905  80 7E FE 01     cmp byte ptr [bp - 2], 1
E909  75 E7           jne 0xe8f2
E90B  83 3E BE 0A 01  cmp word ptr [0xabe], 1
E910  75 02           jne 0xe914
E912  EB 0C           jmp 0xe920
loc_E914:
E914  C4 7E 06        les di, ptr [bp + 6]
E917  26 C6 05 FE     mov byte ptr es:[di], 0xfe
E91B  C6 06 1E 0C 00  mov byte ptr [0xc1e], 0
loc_E920:
E920  8A 46 FF        mov al, byte ptr [bp - 1]
E923  89 EC           mov sp, bp
E925  5D              pop bp
E926  CA 04 00        retf 4

; ---- routine 0791:E929  (found by: call, far)
sub_E929:
E929  55              push bp
E92A  89 E5           mov bp, sp
E92C  9A 57 87 71 17  call far 1771:8757
E931  8A 46 06        mov al, byte ptr [bp + 6]
E934  50              push ax
E935  A0 76 99        mov al, byte ptr [0x9976]
E938  30 E4           xor ah, ah
E93A  50              push ax
E93B  FF 76 08        push word ptr [bp + 8]
E93E  9A 8D 95 71 17  call far 1771:958D
E943  89 EC           mov sp, bp
E945  5D              pop bp
E946  CA 04 00        retf 4

; ---- routine 0791:E949  (found by: call)
sub_E949:
E949  55              push bp
E94A  89 E5           mov bp, sp
E94C  8B 7E 04        mov di, word ptr [bp + 4]
E94F  36 FF 75 FB     push word ptr ss:[di - 5]
E953  9A 77 0B 71 17  call far 1771:0B77
E958  08 C0           or al, al
E95A  75 12           jne 0xe96e
E95C  8B 7E 04        mov di, word ptr [bp + 4]
E95F  36 FF 75 FB     push word ptr ss:[di - 5]
E963  B8 01 00        mov ax, 1
E966  50              push ax
E967  9A F1 50 71 17  call far 1771:50F1
E96C  EB 2E           jmp 0xe99c
loc_E96E:
E96E  8B 7E 04        mov di, word ptr [bp + 4]
E971  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
E975  BA BF 00        mov dx, 0xbf
E978  F7 E2           mul dx
E97A  C4 3E 17 A9     les di, ptr [0xa917]
E97E  03 F8           add di, ax
E980  26 8A 45 2E     mov al, byte ptr es:[di + 0x2e]
E984  30 E4           xor ah, ah
E986  2D 80 00        sub ax, 0x80
E989  C4 3E 23 A9     les di, ptr [0xa923]
E98D  26 88 45 01     mov byte ptr es:[di + 1], al
E991  8B 7E 04        mov di, word ptr [bp + 4]
E994  36 FF 75 FB     push word ptr ss:[di - 5]
E998  0E              push cs
E999  E8 B3 FA        call 0xe44f
loc_E99C:
E99C  89 EC           mov sp, bp
E99E  5D              pop bp
E99F  C2 02 00        ret 2
; data (not reached as code), 103 bytes
E9A2                  pstr ' has an ineligible player in the first team'
E9CE                  pstr ' has too many '
E9DD                  db 01 73   ; .s
E9DF                  pstr ' has no '
E9E8                  pstr ' has a vacancy in the first team'

; ---- routine 0791:EA09  (found by: call)
sub_EA09:
EA09  55              push bp
EA0A  89 E5           mov bp, sp
EA0C  81 EC 18 04     sub sp, 0x418
EA10  8B 7E 04        mov di, word ptr [bp + 4]
EA13  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
EA17  89 46 EB        mov word ptr [bp - 0x15], ax
EA1A  C6 46 ED 00     mov byte ptr [bp - 0x13], 0
EA1E  EB 03           jmp 0xea23
loc_EA20:
EA20  FE 46 ED        inc byte ptr [bp - 0x13]
loc_EA23:
EA23  8A 46 ED        mov al, byte ptr [bp - 0x13]
EA26  98              cwde
EA27  8B F8           mov di, ax
EA29  D1 E7           shl di, 1
EA2B  FF B5 34 9B     push word ptr [di - 0x64cc]
EA2F  9A 77 0B 71 17  call far 1771:0B77
EA34  08 C0           or al, al
EA36  74 04           je 0xea3c
EA38  B0 00           mov al, 0
EA3A  EB 02           jmp 0xea3e
loc_EA3C:
EA3C  B0 01           mov al, 1
loc_EA3E:
EA3E  8A D0           mov dl, al
EA40  8A 46 ED        mov al, byte ptr [bp - 0x13]
EA43  98              cwde
EA44  8B F8           mov di, ax
EA46  88 53 E9        mov byte ptr [bp + di - 0x17], dl
EA49  80 7E ED 01     cmp byte ptr [bp - 0x13], 1
EA4D  75 D1           jne 0xea20
EA4F  C6 46 ED 00     mov byte ptr [bp - 0x13], 0
EA53  EB 03           jmp 0xea58
loc_EA55:
EA55  FE 46 ED        inc byte ptr [bp - 0x13]
loc_EA58:
EA58  8A 46 ED        mov al, byte ptr [bp - 0x13]
EA5B  98              cwde
EA5C  8B F8           mov di, ax
EA5E  D1 E7           shl di, 1
EA60  FF B5 34 9B     push word ptr [di - 0x64cc]
EA64  9A 77 0B 71 17  call far 1771:0B77
EA69  08 C0           or al, al
EA6B  75 03           jne 0xea70
EA6D  E9 96 02        jmp 0xed06
loc_EA70:
EA70  8A 46 ED        mov al, byte ptr [bp - 0x13]
EA73  98              cwde
EA74  8B F8           mov di, ax
EA76  D1 E7           shl di, 1
EA78  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
EA7C  8B 7E 04        mov di, word ptr [bp + 4]
EA7F  36 89 45 FB     mov word ptr ss:[di - 5], ax
EA83  8D 7E F0        lea di, [bp - 0x10]
EA86  16              push ss
EA87  57              push di
EA88  B8 0F 00        mov ax, 0xf
EA8B  50              push ax
EA8C  31 C0           xor ax, ax
EA8E  50              push ax
EA8F  9A 18 00 4B 21  call far 214B:0018
EA94  8A 46 ED        mov al, byte ptr [bp - 0x13]
EA97  98              cwde
EA98  8B F8           mov di, ax
EA9A  C6 43 E9 01     mov byte ptr [bp + di - 0x17], 1
EA9E  C7 46 EE 01 00  mov word ptr [bp - 0x12], 1
EAA3  EB 03           jmp 0xeaa8
loc_EAA5:
EAA5  FF 46 EE        inc word ptr [bp - 0x12]
loc_EAA8:
EAA8  8B 7E 04        mov di, word ptr [bp + 4]
EAAB  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
EAAF  BA BF 00        mov dx, 0xbf
EAB2  F7 E2           mul dx
EAB4  C4 3E 17 A9     les di, ptr [0xa917]
EAB8  03 F8           add di, ax
EABA  89 7E E5        mov word ptr [bp - 0x1b], di
EABD  8C 46 E7        mov word ptr [bp - 0x19], es
EAC0  8B 46 EE        mov ax, word ptr [bp - 0x12]
EAC3  D1 E0           shl ax, 1
EAC5  C4 7E E5        les di, ptr [bp - 0x1b]
EAC8  03 F8           add di, ax
EACA  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
EACF  75 05           jne 0xead6
EAD1  FE 46 FE        inc byte ptr [bp - 2]
EAD4  EB 3B           jmp 0xeb11
loc_EAD6:
EAD6  8B 46 EE        mov ax, word ptr [bp - 0x12]
EAD9  D1 E0           shl ax, 1
EADB  C4 7E E5        les di, ptr [bp - 0x1b]
EADE  03 F8           add di, ax
EAE0  26 FF 75 FE     push word ptr es:[di - 2]
EAE4  9A 16 32 71 17  call far 1771:3216
EAE9  08 C0           or al, al
EAEB  75 24           jne 0xeb11
EAED  8B 46 EE        mov ax, word ptr [bp - 0x12]
EAF0  D1 E0           shl ax, 1
EAF2  C4 7E E5        les di, ptr [bp - 0x1b]
EAF5  03 F8           add di, ax
EAF7  26 8B 45 FE     mov ax, word ptr es:[di - 2]
EAFB  BA 14 00        mov dx, 0x14
EAFE  F7 E2           mul dx
EB00  C4 3E 1B A9     les di, ptr [0xa91b]
EB04  03 F8           add di, ax
EB06  26 8A 45 06     mov al, byte ptr es:[di + 6]
EB0A  30 E4           xor ah, ah
EB0C  8B F8           mov di, ax
EB0E  FE 43 F0        inc byte ptr [bp + di - 0x10]
loc_EB11:
EB11  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
EB16  75 21           jne 0xeb39
EB18  8B 46 EE        mov ax, word ptr [bp - 0x12]
EB1B  D1 E0           shl ax, 1
EB1D  C4 7E E5        les di, ptr [bp - 0x1b]
EB20  03 F8           add di, ax
EB22  26 FF 75 FE     push word ptr es:[di - 2]
EB26  9A 16 32 71 17  call far 1771:3216
EB2B  08 C0           or al, al
EB2D  74 0A           je 0xeb39
EB2F  8A 46 ED        mov al, byte ptr [bp - 0x13]
EB32  98              cwde
EB33  8B F8           mov di, ax
EB35  C6 43 E9 00     mov byte ptr [bp + di - 0x17], 0
loc_EB39:
EB39  83 7E EE 0B     cmp word ptr [bp - 0x12], 0xb
EB3D  74 03           je 0xeb42
EB3F  E9 63 FF        jmp 0xeaa5
loc_EB42:
EB42  8A 46 ED        mov al, byte ptr [bp - 0x13]
EB45  98              cwde
EB46  8B F8           mov di, ax
EB48  80 7B E9 00     cmp byte ptr [bp + di - 0x17], 0
EB4C  74 04           je 0xeb52
EB4E  B0 00           mov al, 0
EB50  EB 02           jmp 0xeb54
loc_EB52:
EB52  B0 01           mov al, 1
loc_EB54:
EB54  50              push ax
EB55  8D BE E9 FE     lea di, [bp - 0x117]
EB59  16              push ss
EB5A  57              push di
EB5B  8B 7E 04        mov di, word ptr [bp + 4]
EB5E  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
EB62  B1 04           mov cl, 4
EB64  D3 E0           shl ax, cl
EB66  C4 3E 68 9B     les di, ptr [0x9b68]
EB6A  03 F8           add di, ax
EB6C  06              push es
EB6D  57              push di
EB6E  9A 2A 06 E4 23  call far 23E4:062A
EB73  BF A2 E9        mov di, 0xe9a2
EB76  0E              push cs
EB77  57              push di
EB78  9A B7 06 E4 23  call far 23E4:06B7
EB7D  9A 65 17 4B 21  call far 214B:1765
EB82  08 C0           or al, al
EB84  74 03           je 0xeb89
EB86  E9 EC 00        jmp 0xec75
loc_EB89:
EB89  80 7E F0 01     cmp byte ptr [bp - 0x10], 1
EB8D  77 04           ja 0xeb93
EB8F  B0 00           mov al, 0
EB91  EB 02           jmp 0xeb95
loc_EB93:
EB93  B0 01           mov al, 1
loc_EB95:
EB95  50              push ax
EB96  8D BE E9 FD     lea di, [bp - 0x217]
EB9A  16              push ss
EB9B  57              push di
EB9C  8B 7E 04        mov di, word ptr [bp + 4]
EB9F  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
EBA3  B1 04           mov cl, 4
EBA5  D3 E0           shl ax, cl
EBA7  C4 3E 68 9B     les di, ptr [0x9b68]
EBAB  03 F8           add di, ax
EBAD  06              push es
EBAE  57              push di
EBAF  9A 2A 06 E4 23  call far 23E4:062A
EBB4  BF CE E9        mov di, 0xe9ce
EBB7  0E              push cs
EBB8  57              push di
EBB9  9A B7 06 E4 23  call far 23E4:06B7
EBBE  BF B6 69        mov di, 0x69b6
EBC1  1E              push ds
EBC2  57              push di
EBC3  9A B7 06 E4 23  call far 23E4:06B7
EBC8  BF DD E9        mov di, 0xe9dd
EBCB  0E              push cs
EBCC  57              push di
EBCD  9A B7 06 E4 23  call far 23E4:06B7
EBD2  9A 65 17 4B 21  call far 214B:1765
EBD7  08 C0           or al, al
EBD9  74 03           je 0xebde
EBDB  E9 86 00        jmp 0xec64
loc_EBDE:
EBDE  80 7E F0 00     cmp byte ptr [bp - 0x10], 0
EBE2  74 04           je 0xebe8
EBE4  B0 00           mov al, 0
EBE6  EB 02           jmp 0xebea
loc_EBE8:
EBE8  B0 01           mov al, 1
loc_EBEA:
EBEA  50              push ax
EBEB  8D BE E9 FC     lea di, [bp - 0x317]
EBEF  16              push ss
EBF0  57              push di
EBF1  8B 7E 04        mov di, word ptr [bp + 4]
EBF4  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
EBF8  B1 04           mov cl, 4
EBFA  D3 E0           shl ax, cl
EBFC  C4 3E 68 9B     les di, ptr [0x9b68]
EC00  03 F8           add di, ax
EC02  06              push es
EC03  57              push di
EC04  9A 2A 06 E4 23  call far 23E4:062A
EC09  BF DF E9        mov di, 0xe9df
EC0C  0E              push cs
EC0D  57              push di
EC0E  9A B7 06 E4 23  call far 23E4:06B7
EC13  BF B6 69        mov di, 0x69b6
EC16  1E              push ds
EC17  57              push di
EC18  9A B7 06 E4 23  call far 23E4:06B7
EC1D  9A 65 17 4B 21  call far 214B:1765
EC22  08 C0           or al, al
EC24  75 3E           jne 0xec64
EC26  80 7E FE 00     cmp byte ptr [bp - 2], 0
EC2A  75 04           jne 0xec30
EC2C  B0 00           mov al, 0
EC2E  EB 02           jmp 0xec32
loc_EC30:
EC30  B0 01           mov al, 1
loc_EC32:
EC32  50              push ax
EC33  8D BE E9 FB     lea di, [bp - 0x417]
EC37  16              push ss
EC38  57              push di
EC39  8B 7E 04        mov di, word ptr [bp + 4]
EC3C  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
EC40  B1 04           mov cl, 4
EC42  D3 E0           shl ax, cl
EC44  C4 3E 68 9B     les di, ptr [0x9b68]
EC48  03 F8           add di, ax
EC4A  06              push es
EC4B  57              push di
EC4C  9A 2A 06 E4 23  call far 23E4:062A
EC51  BF E8 E9        mov di, 0xe9e8
EC54  0E              push cs
EC55  57              push di
EC56  9A B7 06 E4 23  call far 23E4:06B7
EC5B  9A 65 17 4B 21  call far 214B:1765
EC60  08 C0           or al, al
EC62  74 04           je 0xec68
loc_EC64:
EC64  B0 00           mov al, 0
EC66  EB 02           jmp 0xec6a
loc_EC68:
EC68  B0 01           mov al, 1
loc_EC6A:
EC6A  8A D0           mov dl, al
EC6C  8A 46 ED        mov al, byte ptr [bp - 0x13]
EC6F  98              cwde
EC70  8B F8           mov di, ax
EC72  88 53 E9        mov byte ptr [bp + di - 0x17], dl
loc_EC75:
EC75  C7 46 EE 01 00  mov word ptr [bp - 0x12], 1
loc_EC7A:
EC7A  8A 46 ED        mov al, byte ptr [bp - 0x13]
EC7D  98              cwde
EC7E  8B F8           mov di, ax
EC80  80 7B E9 00     cmp byte ptr [bp + di - 0x17], 0
EC84  75 03           jne 0xec89
EC86  E9 7D 00        jmp 0xed06
loc_EC89:
EC89  83 7E EE 0D     cmp word ptr [bp - 0x12], 0xd
EC8D  77 77           ja 0xed06
EC8F  8B 7E EE        mov di, word ptr [bp - 0x12]
EC92  80 7B F0 03     cmp byte ptr [bp + di - 0x10], 3
EC96  77 04           ja 0xec9c
EC98  B0 00           mov al, 0
EC9A  EB 02           jmp 0xec9e
loc_EC9C:
EC9C  B0 01           mov al, 1
loc_EC9E:
EC9E  50              push ax
EC9F  8D BE E9 FE     lea di, [bp - 0x117]
ECA3  16              push ss
ECA4  57              push di
ECA5  8B 7E 04        mov di, word ptr [bp + 4]
ECA8  36 8B 45 FB     mov ax, word ptr ss:[di - 5]
ECAC  B1 04           mov cl, 4
ECAE  D3 E0           shl ax, cl
ECB0  C4 3E 68 9B     les di, ptr [0x9b68]
ECB4  03 F8           add di, ax
ECB6  06              push es
ECB7  57              push di
ECB8  9A 2A 06 E4 23  call far 23E4:062A
ECBD  BF CE E9        mov di, 0xe9ce
ECC0  0E              push cs
ECC1  57              push di
ECC2  9A B7 06 E4 23  call far 23E4:06B7
ECC7  8B 46 EE        mov ax, word ptr [bp - 0x12]
ECCA  BA 13 00        mov dx, 0x13
ECCD  F7 E2           mul dx
ECCF  8B F8           mov di, ax
ECD1  81 C7 B6 69     add di, 0x69b6
ECD5  1E              push ds
ECD6  57              push di
ECD7  9A B7 06 E4 23  call far 23E4:06B7
ECDC  BF DD E9        mov di, 0xe9dd
ECDF  0E              push cs
ECE0  57              push di
ECE1  9A B7 06 E4 23  call far 23E4:06B7
ECE6  9A 65 17 4B 21  call far 214B:1765
ECEB  08 C0           or al, al
ECED  74 04           je 0xecf3
ECEF  B0 00           mov al, 0
ECF1  EB 02           jmp 0xecf5
loc_ECF3:
ECF3  B0 01           mov al, 1
loc_ECF5:
ECF5  8A D0           mov dl, al
ECF7  8A 46 ED        mov al, byte ptr [bp - 0x13]
ECFA  98              cwde
ECFB  8B F8           mov di, ax
ECFD  88 53 E9        mov byte ptr [bp + di - 0x17], dl
ED00  FF 46 EE        inc word ptr [bp - 0x12]
ED03  E9 74 FF        jmp 0xec7a
loc_ED06:
ED06  80 7E ED 01     cmp byte ptr [bp - 0x13], 1
ED0A  74 03           je 0xed0f
ED0C  E9 46 FD        jmp 0xea55
loc_ED0F:
ED0F  80 7E E9 00     cmp byte ptr [bp - 0x17], 0
ED13  74 06           je 0xed1b
ED15  80 7E EA 00     cmp byte ptr [bp - 0x16], 0
ED19  75 04           jne 0xed1f
loc_ED1B:
ED1B  B0 00           mov al, 0
ED1D  EB 02           jmp 0xed21
loc_ED1F:
ED1F  B0 01           mov al, 1
loc_ED21:
ED21  88 46 FF        mov byte ptr [bp - 1], al
ED24  8B 46 EB        mov ax, word ptr [bp - 0x15]
ED27  8B 7E 04        mov di, word ptr [bp + 4]
ED2A  36 89 45 FB     mov word ptr ss:[di - 5], ax
ED2E  8A 46 FF        mov al, byte ptr [bp - 1]
ED31  89 EC           mov sp, bp
ED33  5D              pop bp
ED34  C2 02 00        ret 2
; data (not reached as code), 83 bytes
ED37                  db 18 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
ED47                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
ED57                  pstr 'exit'
ED5C                  db C6 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
ED6C                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
ED7C                  pstr 'Not available'

; ---- routine 0791:ED8A  (found by: call)
sub_ED8A:
ED8A  55              push bp
ED8B  89 E5           mov bp, sp
ED8D  83 EC 10        sub sp, 0x10
ED90  80 7E 04 00     cmp byte ptr [bp + 4], 0
ED94  74 15           je 0xedab
ED96  C4 3E 6A A9     les di, ptr [0xa96a]
ED9A  06              push es
ED9B  57              push di
ED9C  C4 3E 72 A9     les di, ptr [0xa972]
EDA0  06              push es
EDA1  57              push di
EDA2  B8 A0 0F        mov ax, 0xfa0
EDA5  50              push ax
EDA6  9A 5D 02 E4 23  call far 23E4:025D
loc_EDAB:
EDAB  E8 5E 35        call 0x1230c
EDAE  FF 36 36 9B     push word ptr [0x9b36]
EDB2  9A 77 0B 71 17  call far 1771:0B77
EDB7  08 C0           or al, al
EDB9  74 06           je 0xedc1
EDBB  C6 46 FE 01     mov byte ptr [bp - 2], 1
EDBF  EB 17           jmp 0xedd8
loc_EDC1:
EDC1  FF 36 34 9B     push word ptr [0x9b34]
EDC5  9A 77 0B 71 17  call far 1771:0B77
EDCA  08 C0           or al, al
EDCC  74 06           je 0xedd4
EDCE  C6 46 FE 00     mov byte ptr [bp - 2], 0
EDD2  EB 04           jmp 0xedd8
loc_EDD4:
EDD4  C6 46 FE 01     mov byte ptr [bp - 2], 1
loc_EDD8:
EDD8  8A 46 FE        mov al, byte ptr [bp - 2]
EDDB  98              cwde
EDDC  8B F8           mov di, ax
EDDE  8A 85 C2 0A     mov al, byte ptr [di + 0xac2]
EDE2  30 E4           xor ah, ah
EDE4  89 46 F9        mov word ptr [bp - 7], ax
loc_EDE7:
EDE7  8A 46 F9        mov al, byte ptr [bp - 7]
EDEA  50              push ax
EDEB  BF 37 ED        mov di, 0xed37
EDEE  0E              push cs
EDEF  57              push di
EDF0  9A DF 08 E4 23  call far 23E4:08DF
EDF5  75 0F           jne 0xee06
EDF7  83 7E F9 06     cmp word ptr [bp - 7], 6
EDFB  72 04           jb 0xee01
EDFD  B0 00           mov al, 0
EDFF  EB 02           jmp 0xee03
loc_EE01:
EE01  B0 01           mov al, 1
loc_EE03:
EE03  88 46 FE        mov byte ptr [bp - 2], al
loc_EE06:
EE06  8A 46 FE        mov al, byte ptr [bp - 2]
EE09  98              cwde
EE0A  8B F8           mov di, ax
EE0C  D1 E7           shl di, 1
EE0E  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
EE12  89 46 FB        mov word ptr [bp - 5], ax
EE15  E8 45 B9        call 0xa75d
EE18  80 3E 6D 06 00  cmp byte ptr [0x66d], 0
EE1D  74 18           je 0xee37
EE1F  B0 07           mov al, 7
EE21  50              push ax
EE22  BF 57 ED        mov di, 0xed57
EE25  0E              push cs
EE26  57              push di
EE27  B0 14           mov al, 0x14
EE29  50              push ax
EE2A  B0 27           mov al, 0x27
EE2C  50              push ax
EE2D  BF 6E A9        mov di, 0xa96e
EE30  1E              push ds
EE31  57              push di
EE32  9A C8 02 4B 21  call far 214B:02C8
loc_EE37:
EE37  BF 98 25        mov di, 0x2598
EE3A  1E              push ds
EE3B  57              push di
EE3C  BF 6E A9        mov di, 0xa96e
EE3F  1E              push ds
EE40  57              push di
EE41  9A 29 03 4B 21  call far 214B:0329
EE46  8B 7E F9        mov di, word ptr [bp - 7]
EE49  8A 85 CD 0A     mov al, byte ptr [di + 0xacd]
EE4D  30 E4           xor ah, ah
EE4F  50              push ax
EE50  8B 7E F9        mov di, word ptr [bp - 7]
EE53  8A 85 D7 0A     mov al, byte ptr [di + 0xad7]
EE57  30 E4           xor ah, ah
EE59  50              push ax
EE5A  8B 7E F9        mov di, word ptr [bp - 7]
EE5D  8A 85 E1 0A     mov al, byte ptr [di + 0xae1]
EE61  30 E4           xor ah, ah
EE63  50              push ax
EE64  9A C5 13 4B 21  call far 214B:13C5
EE69  B0 07           mov al, 7
EE6B  50              push ax
EE6C  C4 3E 23 A9     les di, ptr [0xa923]
EE70  26 8A 45 41     mov al, byte ptr es:[di + 0x41]
EE74  98              cwde
EE75  8B F8           mov di, ax
EE77  D1 E7           shl di, 1
EE79  D1 E7           shl di, 1
EE7B  81 C7 C6 0A     add di, 0xac6
EE7F  1E              push ds
EE80  57              push di
EE81  B0 19           mov al, 0x19
EE83  50              push ax
EE84  B0 3D           mov al, 0x3d
EE86  50              push ax
EE87  BF 6E A9        mov di, 0xa96e
EE8A  1E              push ds
EE8B  57              push di
EE8C  9A C8 02 4B 21  call far 214B:02C8
EE91  8D 7E F9        lea di, [bp - 7]
EE94  16              push ss
EE95  57              push di
EE96  B8 0A 00        mov ax, 0xa
EE99  50              push ax
EE9A  9A 60 15 4B 21  call far 214B:1560
EE9F  80 3E 76 A9 1B  cmp byte ptr [0xa976], 0x1b
EEA4  75 07           jne 0xeead
EEA6  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
EEAB  75 04           jne 0xeeb1
loc_EEAD:
EEAD  B0 00           mov al, 0
EEAF  EB 02           jmp 0xeeb3
loc_EEB1:
EEB1  B0 01           mov al, 1
loc_EEB3:
EEB3  88 46 FF        mov byte ptr [bp - 1], al
EEB6  A0 76 A9        mov al, byte ptr [0xa976]
EEB9  3C AB           cmp al, 0xab
EEBB  75 18           jne 0xeed5
EEBD  FF 36 36 9B     push word ptr [0x9b36]
EEC1  9A 77 0B 71 17  call far 1771:0B77
EEC6  98              cwde
EEC7  8B F8           mov di, ax
EEC9  8A 85 C4 0A     mov al, byte ptr [di + 0xac4]
EECD  30 E4           xor ah, ah
EECF  89 46 F9        mov word ptr [bp - 7], ax
EED2  E9 9C 00        jmp 0xef71
loc_EED5:
EED5  3C B0           cmp al, 0xb0
EED7  75 18           jne 0xeef1
EED9  FF 36 36 9B     push word ptr [0x9b36]
EEDD  9A 77 0B 71 17  call far 1771:0B77
EEE2  98              cwde
EEE3  8B F8           mov di, ax
EEE5  8A 85 C2 0A     mov al, byte ptr [di + 0xac2]
EEE9  30 E4           xor ah, ah
EEEB  89 46 F9        mov word ptr [bp - 7], ax
EEEE  E9 80 00        jmp 0xef71
loc_EEF1:
EEF1  3C AE           cmp al, 0xae
EEF3  74 04           je 0xeef9
EEF5  3C AF           cmp al, 0xaf
EEF7  75 49           jne 0xef42
loc_EEF9:
EEF9  8A 46 F9        mov al, byte ptr [bp - 7]
EEFC  50              push ax
EEFD  BF 5C ED        mov di, 0xed5c
EF00  0E              push cs
EF01  57              push di
EF02  9A DF 08 E4 23  call far 23E4:08DF
EF07  74 1E           je 0xef27
EF09  83 7E F9 06     cmp word ptr [bp - 7], 6
EF0D  72 04           jb 0xef13
EF0F  B0 00           mov al, 0
EF11  EB 02           jmp 0xef15
loc_EF13:
EF13  B0 01           mov al, 1
loc_EF15:
EF15  98              cwde
EF16  8B F8           mov di, ax
EF18  8A 85 20 79     mov al, byte ptr [di + 0x7920]
EF1C  98              cwde
EF1D  B9 05 00        mov cx, 5
EF20  F7 E9           imul cx
EF22  01 46 F9        add word ptr [bp - 7], ax
EF25  EB 19           jmp 0xef40
loc_EF27:
EF27  80 3E 76 A9 AE  cmp byte ptr [0xa976], 0xae
EF2C  74 04           je 0xef32
EF2E  B0 00           mov al, 0
EF30  EB 02           jmp 0xef34
loc_EF32:
EF32  B0 01           mov al, 1
loc_EF34:
EF34  98              cwde
EF35  8B F8           mov di, ax
EF37  8A 85 C4 0A     mov al, byte ptr [di + 0xac4]
EF3B  30 E4           xor ah, ah
EF3D  89 46 F9        mov word ptr [bp - 7], ax
loc_EF40:
EF40  EB 2F           jmp 0xef71
loc_EF42:
EF42  3C B6           cmp al, 0xb6
EF44  75 23           jne 0xef69
EF46  C4 3E 23 A9     les di, ptr [0xa923]
EF4A  89 7E F1        mov word ptr [bp - 0xf], di
EF4D  8C 46 F3        mov word ptr [bp - 0xd], es
EF50  C4 7E F1        les di, ptr [bp - 0xf]
EF53  26 80 7D 41 00  cmp byte ptr es:[di + 0x41], 0
EF58  74 04           je 0xef5e
EF5A  B0 00           mov al, 0
EF5C  EB 02           jmp 0xef60
loc_EF5E:
EF5E  B0 01           mov al, 1
loc_EF60:
EF60  C4 7E F1        les di, ptr [bp - 0xf]
EF63  26 88 45 41     mov byte ptr es:[di + 0x41], al
EF67  EB 08           jmp 0xef71
loc_EF69:
EF69  3C 20           cmp al, 0x20
EF6B  75 04           jne 0xef71
EF6D  55              push bp
EF6E  E8 D8 F9        call 0xe949
loc_EF71:
EF71  80 3E 76 A9 0D  cmp byte ptr [0xa976], 0xd
EF76  74 03           je 0xef7b
EF78  E9 DF 00        jmp 0xf05a
loc_EF7B:
EF7B  8B 46 F9        mov ax, word ptr [bp - 7]
EF7E  3D 01 00        cmp ax, 1
EF81  74 08           je 0xef8b
EF83  3D 06 00        cmp ax, 6
EF86  74 03           je 0xef8b
EF88  E9 80 00        jmp 0xf00b
loc_EF8B:
EF8B  BF 4C 1E        mov di, 0x1e4c
EF8E  1E              push ds
EF8F  57              push di
EF90  BF 6E A9        mov di, 0xa96e
EF93  1E              push ds
EF94  57              push di
EF95  9A 29 03 4B 21  call far 214B:0329
EF9A  FF 76 FB        push word ptr [bp - 5]
EF9D  9A 77 0B 71 17  call far 1771:0B77
EFA2  08 C0           or al, al
EFA4  74 16           je 0xefbc
EFA6  80 3E 20 0C 00  cmp byte ptr [0xc20], 0
EFAB  75 0F           jne 0xefbc
EFAD  BF B4 1E        mov di, 0x1eb4
EFB0  1E              push ds
EFB1  57              push di
EFB2  BF 6E A9        mov di, 0xa96e
EFB5  1E              push ds
EFB6  57              push di
EFB7  9A 29 03 4B 21  call far 214B:0329
loc_EFBC:
EFBC  FF 76 FB        push word ptr [bp - 5]
EFBF  B8 09 00        mov ax, 9
EFC2  50              push ax
EFC3  B8 40 00        mov ax, 0x40
EFC6  50              push ax
EFC7  9A 58 0F 71 17  call far 1771:0F58
EFCC  8B 46 FB        mov ax, word ptr [bp - 5]
EFCF  BA BF 00        mov dx, 0xbf
EFD2  F7 E2           mul dx
EFD4  C4 3E 17 A9     les di, ptr [0xa917]
EFD8  03 F8           add di, ax
EFDA  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
EFDE  30 E4           xor ah, ah
EFE0  89 46 F5        mov word ptr [bp - 0xb], ax
EFE3  FF 76 FB        push word ptr [bp - 5]
EFE6  9A 81 19 71 17  call far 1771:1981
EFEB  8B 46 FB        mov ax, word ptr [bp - 5]
EFEE  BA BF 00        mov dx, 0xbf
EFF1  F7 E2           mul dx
EFF3  C4 3E 17 A9     les di, ptr [0xa917]
EFF7  03 F8           add di, ax
EFF9  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
EFFD  30 E4           xor ah, ah
EFFF  3B 46 F5        cmp ax, word ptr [bp - 0xb]
F002  74 05           je 0xf009
F004  C6 06 55 9B 01  mov byte ptr [0x9b55], 1
loc_F009:
F009  EB 4F           jmp 0xf05a
loc_F00B:
F00B  3D 02 00        cmp ax, 2
F00E  74 05           je 0xf015
F010  3D 07 00        cmp ax, 7
F013  75 06           jne 0xf01b
loc_F015:
F015  55              push bp
F016  E8 30 F9        call 0xe949
F019  EB 3F           jmp 0xf05a
loc_F01B:
F01B  3D 04 00        cmp ax, 4
F01E  74 05           je 0xf025
F020  3D 09 00        cmp ax, 9
F023  75 09           jne 0xf02e
loc_F025:
F025  B0 01           mov al, 1
F027  50              push ax
F028  0E              push cs
F029  E8 DA 10        call 0x10106
F02C  EB 2C           jmp 0xf05a
loc_F02E:
F02E  3D 03 00        cmp ax, 3
F031  74 05           je 0xf038
F033  3D 08 00        cmp ax, 8
F036  75 1E           jne 0xf056
loc_F038:
F038  A0 21 0C        mov al, byte ptr [0xc21]
F03B  50              push ax
F03C  BF 7C ED        mov di, 0xed7c
F03F  0E              push cs
F040  57              push di
F041  9A 65 17 4B 21  call far 214B:1765
F046  08 C0           or al, al
F048  75 0A           jne 0xf054
F04A  FF 76 FB        push word ptr [bp - 5]
F04D  B0 01           mov al, 1
F04F  50              push ax
F050  0E              push cs
F051  E8 D5 F8        call 0xe929
loc_F054:
F054  EB 04           jmp 0xf05a
loc_F056:
F056  C6 46 FF 01     mov byte ptr [bp - 1], 1
loc_F05A:
F05A  80 7E FF 00     cmp byte ptr [bp - 1], 0
F05E  75 03           jne 0xf063
F060  E9 84 FD        jmp 0xede7
loc_F063:
F063  55              push bp
F064  E8 A2 F9        call 0xea09
F067  08 C0           or al, al
F069  75 03           jne 0xf06e
F06B  E9 79 FD        jmp 0xede7
loc_F06E:
F06E  80 3E 1F 0C 00  cmp byte ptr [0xc1f], 0
F073  74 15           je 0xf08a
F075  C4 3E 72 A9     les di, ptr [0xa972]
F079  06              push es
F07A  57              push di
F07B  C4 3E 6A A9     les di, ptr [0xa96a]
F07F  06              push es
F080  57              push di
F081  B8 A0 0F        mov ax, 0xfa0
F084  50              push ax
F085  9A 5D 02 E4 23  call far 23E4:025D
loc_F08A:
F08A  C6 06 1F 0C 01  mov byte ptr [0xc1f], 1
F08F  E8 7A 32        call 0x1230c
F092  89 EC           mov sp, bp
F094  5D              pop bp
F095  C2 02 00        ret 2

; ---- routine 0791:F098  (found by: call)
sub_F098:
F098  55              push bp
F099  89 E5           mov bp, sp
F09B  83 EC 04        sub sp, 4
F09E  E8 EB A8        call 0x998c
F0A1  E8 B1 A8        call 0x9955
F0A4  E8 8B A9        call 0x9a32
F0A7  A1 3C 9B        mov ax, word ptr [0x9b3c]
F0AA  8B 7E 04        mov di, word ptr [bp + 4]
F0AD  36 C4 7D 06     les di, ptr ss:[di + 6]
F0B1  26 89 05        mov word ptr es:[di], ax
F0B4  8B 7E 04        mov di, word ptr [bp + 4]
F0B7  36 C4 7D 06     les di, ptr ss:[di + 6]
F0BB  89 7E FC        mov word ptr [bp - 4], di
F0BE  8C 46 FE        mov word ptr [bp - 2], es
F0C1  C4 7E FC        les di, ptr [bp - 4]
F0C4  26 8A 05        mov al, byte ptr es:[di]
F0C7  C4 7E FC        les di, ptr [bp - 4]
F0CA  26 3A 45 01     cmp al, byte ptr es:[di + 1]
F0CE  75 0A           jne 0xf0da
F0D0  C4 7E FC        les di, ptr [bp - 4]
F0D3  26 C6 45 03 02  mov byte ptr es:[di + 3], 2
F0D8  EB 1C           jmp 0xf0f6
loc_F0DA:
F0DA  C4 7E FC        les di, ptr [bp - 4]
F0DD  26 8A 45 01     mov al, byte ptr es:[di + 1]
F0E1  C4 7E FC        les di, ptr [bp - 4]
F0E4  26 3A 05        cmp al, byte ptr es:[di]
F0E7  77 04           ja 0xf0ed
F0E9  B0 00           mov al, 0
F0EB  EB 02           jmp 0xf0ef
loc_F0ED:
F0ED  B0 01           mov al, 1
loc_F0EF:
F0EF  C4 7E FC        les di, ptr [bp - 4]
F0F2  26 88 45 03     mov byte ptr es:[di + 3], al
loc_F0F6:
F0F6  80 3E 36 7C 00  cmp byte ptr [0x7c36], 0
F0FB  75 03           jne 0xf100
F0FD  E9 96 00        jmp 0xf196
loc_F100:
F100  8B 7E 04        mov di, word ptr [bp + 4]
F103  36 C4 7D 06     les di, ptr ss:[di + 6]
F107  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
F10C  74 03           je 0xf111
F10E  E9 85 00        jmp 0xf196
loc_F111:
F111  E8 F8 A9        call 0x9b0c
F114  E8 44 AA        call 0x9b5b
F117  A1 3C 9B        mov ax, word ptr [0x9b3c]
F11A  8B 7E 04        mov di, word ptr [bp + 4]
F11D  36 C4 7D 06     les di, ptr ss:[di + 6]
F121  26 89 05        mov word ptr es:[di], ax
F124  8B 7E 04        mov di, word ptr [bp + 4]
F127  36 C4 7D 06     les di, ptr ss:[di + 6]
F12B  89 7E FC        mov word ptr [bp - 4], di
F12E  8C 46 FE        mov word ptr [bp - 2], es
F131  C4 7E FC        les di, ptr [bp - 4]
F134  26 8A 05        mov al, byte ptr es:[di]
F137  C4 7E FC        les di, ptr [bp - 4]
F13A  26 3A 45 01     cmp al, byte ptr es:[di + 1]
F13E  75 0A           jne 0xf14a
F140  C4 7E FC        les di, ptr [bp - 4]
F143  26 C6 45 03 02  mov byte ptr es:[di + 3], 2
F148  EB 1C           jmp 0xf166
loc_F14A:
F14A  C4 7E FC        les di, ptr [bp - 4]
F14D  26 8A 45 01     mov al, byte ptr es:[di + 1]
F151  C4 7E FC        les di, ptr [bp - 4]
F154  26 3A 05        cmp al, byte ptr es:[di]
F157  77 04           ja 0xf15d
F159  B0 00           mov al, 0
F15B  EB 02           jmp 0xf15f
loc_F15D:
F15D  B0 01           mov al, 1
loc_F15F:
F15F  C4 7E FC        les di, ptr [bp - 4]
F162  26 88 45 03     mov byte ptr es:[di + 3], al
loc_F166:
F166  C6 06 23 83 00  mov byte ptr [0x8323], 0
F16B  8B 7E 04        mov di, word ptr [bp + 4]
F16E  36 C4 7D 06     les di, ptr ss:[di + 6]
F172  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
F177  75 1D           jne 0xf196
F179  E8 8E AF        call 0xa10a
F17C  A0 3D 9B        mov al, byte ptr [0x9b3d]
F17F  3A 06 3C 9B     cmp al, byte ptr [0x9b3c]
F183  77 04           ja 0xf189
F185  B0 00           mov al, 0
F187  EB 02           jmp 0xf18b
loc_F189:
F189  B0 01           mov al, 1
loc_F18B:
F18B  8B 7E 04        mov di, word ptr [bp + 4]
F18E  36 C4 7D 06     les di, ptr ss:[di + 6]
F192  26 88 45 03     mov byte ptr es:[di + 3], al
loc_F196:
F196  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
F19B  74 02           je 0xf19f
F19D  EB 0F           jmp 0xf1ae
loc_F19F:
F19F  A0 3D 9B        mov al, byte ptr [0x9b3d]
F1A2  3A 06 3C 9B     cmp al, byte ptr [0x9b3c]
F1A6  74 03           je 0xf1ab
F1A8  E8 19 A7        call 0x98c4
loc_F1AB:
F1AB  E8 A7 A7        call 0x9955
loc_F1AE:
F1AE  89 EC           mov sp, bp
F1B0  5D              pop bp
F1B1  C2 02 00        ret 2
; data (not reached as code), 66 bytes
F1B4                  db 00 20 00 08 00 00 00 00 00 00 00 00 00 00 00 00   ; . ..............
F1C4                  db 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ; ................
F1D4                  pstr 'to save the match summary to disk'

; ---- routine 0791:F1F6  (found by: far)
sub_F1F6:
F1F6  55              push bp
F1F7  89 E5           mov bp, sp
F1F9  83 EC 0A        sub sp, 0xa
F1FC  C4 7E 06        les di, ptr [bp + 6]
F1FF  06              push es
F200  57              push di
F201  E8 9D B2        call 0xa4a1
F204  B0 01           mov al, 1
F206  50              push ax
F207  E8 80 FB        call 0xed8a
F20A  C4 3E 1E 7C     les di, ptr [0x7c1e]
F20E  06              push es
F20F  57              push di
F210  C4 3E 16 7C     les di, ptr [0x7c16]
F214  06              push es
F215  57              push di
F216  B8 A0 0F        mov ax, 0xfa0
F219  50              push ax
F21A  9A 5D 02 E4 23  call far 23E4:025D
F21F  C4 3E 1E 7C     les di, ptr [0x7c1e]
F223  06              push es
F224  57              push di
F225  C4 3E 22 7C     les di, ptr [0x7c22]
F229  06              push es
F22A  57              push di
F22B  B8 A0 0F        mov ax, 0xfa0
F22E  50              push ax
F22F  9A 5D 02 E4 23  call far 23E4:025D
F234  C6 46 FF 00     mov byte ptr [bp - 1], 0
F238  EB 03           jmp 0xf23d
loc_F23A:
F23A  FE 46 FF        inc byte ptr [bp - 1]
loc_F23D:
F23D  C7 46 FD 01 00  mov word ptr [bp - 3], 1
F242  EB 03           jmp 0xf247
loc_F244:
F244  FF 46 FD        inc word ptr [bp - 3]
loc_F247:
F247  8A 46 FF        mov al, byte ptr [bp - 1]
F24A  98              cwde
F24B  8B F8           mov di, ax
F24D  D1 E7           shl di, 1
F24F  8B 85 34 9B     mov ax, word ptr [di - 0x64cc]
F253  BA BF 00        mov dx, 0xbf
F256  F7 E2           mul dx
F258  C4 3E 17 A9     les di, ptr [0xa917]
F25C  03 F8           add di, ax
F25E  89 7E F7        mov word ptr [bp - 9], di
F261  8C 46 F9        mov word ptr [bp - 7], es
F264  8B 46 FD        mov ax, word ptr [bp - 3]
F267  D1 E0           shl ax, 1
F269  C4 7E F7        les di, ptr [bp - 9]
F26C  03 F8           add di, ax
F26E  26 83 7D FE 00  cmp word ptr es:[di - 2], 0
F273  74 58           je 0xf2cd
F275  8B 46 FD        mov ax, word ptr [bp - 3]
F278  D1 E0           shl ax, 1
F27A  C4 7E F7        les di, ptr [bp - 9]
F27D  03 F8           add di, ax
F27F  26 8B 45 FE     mov ax, word ptr es:[di - 2]
F283  BA 14 00        mov dx, 0x14
F286  F7 E2           mul dx
F288  C4 3E 1B A9     les di, ptr [0xa91b]
F28C  03 F8           add di, ax
F28E  26 8A 5D 0C     mov bl, byte ptr es:[di + 0xc]
F292  8B 46 FD        mov ax, word ptr [bp - 3]
F295  8B C8           mov cx, ax
F297  8A 46 FF        mov al, byte ptr [bp - 1]
F29A  98              cwde
F29B  BA 14 00        mov dx, 0x14
F29E  F7 E2           mul dx
F2A0  8B F8           mov di, ax
F2A2  03 F9           add di, cx
F2A4  88 9D 07 9B     mov byte ptr [di - 0x64f9], bl
F2A8  83 7E FD 0C     cmp word ptr [bp - 3], 0xc
F2AC  73 1F           jae 0xf2cd
F2AE  8B 46 FD        mov ax, word ptr [bp - 3]
F2B1  D1 E0           shl ax, 1
F2B3  C4 7E F7        les di, ptr [bp - 9]
F2B6  03 F8           add di, ax
F2B8  26 8B 45 FE     mov ax, word ptr es:[di - 2]
F2BC  BA 14 00        mov dx, 0x14
F2BF  F7 E2           mul dx
F2C1  C4 3E 1B A9     les di, ptr [0xa91b]
F2C5  03 F8           add di, ax
F2C7  26 C7 45 12 37 00 mov word ptr es:[di + 0x12], 0x37
loc_F2CD:
F2CD  83 7E FD 14     cmp word ptr [bp - 3], 0x14
F2D1  74 03           je 0xf2d6
F2D3  E9 6E FF        jmp 0xf244
loc_F2D6:
F2D6  80 7E FF 01     cmp byte ptr [bp - 1], 1
F2DA  74 03           je 0xf2df
F2DC  E9 5B FF        jmp 0xf23a
loc_F2DF:
F2DF  55              push bp
F2E0  E8 B5 FD        call 0xf098
F2E3  C4 3E 16 7C     les di, ptr [0x7c16]
F2E7  06              push es
F2E8  57              push di
F2E9  C4 3E 22 7C     les di, ptr [0x7c22]
F2ED  06              push es
F2EE  57              push di
F2EF  B8 A0 0F        mov ax, 0xfa0
F2F2  50              push ax
F2F3  9A 5D 02 E4 23  call far 23E4:025D
F2F8  E8 B5 D7        call 0xcab0
F2FB  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
F300  75 03           jne 0xf305
F302  E8 B4 22        call 0x115b9
loc_F305:
F305  B0 01           mov al, 1
F307  50              push ax
F308  0E              push cs
F309  E8 FA 0D        call 0x10106
F30C  9A 57 87 71 17  call far 1771:8757
F311  C6 06 6D 06 01  mov byte ptr [0x66d], 1
F316  C6 06 20 0C 01  mov byte ptr [0xc20], 1
F31B  A0 77 A9        mov al, byte ptr [0xa977]
F31E  50              push ax
F31F  BF B4 F1        mov di, 0xf1b4
F322  0E              push cs
F323  57              push di
F324  9A DF 08 E4 23  call far 23E4:08DF
F329  74 06           je 0xf331
F32B  B0 01           mov al, 1
F32D  50              push ax
F32E  E8 59 FA        call 0xed8a
loc_F331:
F331  80 3E 3E 9A 00  cmp byte ptr [0x9a3e], 0
F336  75 0F           jne 0xf347
F338  BF D4 F1        mov di, 0xf1d4
F33B  0E              push cs
F33C  57              push di
F33D  E8 3C 18        call 0x10b7c
F340  08 C0           or al, al
F342  74 03           je 0xf347
F344  E8 24 17        call 0x10a6b
loc_F347:
F347  E8 33 D8        call 0xcb7d
F34A  C6 06 6D 06 00  mov byte ptr [0x66d], 0
F34F  C4 7E 06        les di, ptr [bp + 6]
F352  26 80 7D 02 01  cmp byte ptr es:[di + 2], 1
F357  74 0B           je 0xf364
F359  FF 36 36 9B     push word ptr [0x9b36]
F35D  B0 00           mov al, 0
F35F  50              push ax
F360  0E              push cs
F361  E8 C5 F5        call 0xe929
loc_F364:
F364  C6 46 FF 00     mov byte ptr [bp - 1], 0
F368  EB 03           jmp 0xf36d
loc_F36A:
F36A  FE 46 FF        inc byte ptr [bp - 1]
loc_F36D:
F36D  8A 46 FF        mov al, byte ptr [bp - 1]
F370  98              cwde
F371  8B F8           mov di, ax
F373  D1 E7           shl di, 1
F375  FF B5 34 9B     push word ptr [di - 0x64cc]
F379  9A 77 0B 71 17  call far 1771:0B77
F37E  08 C0           or al, al
F380  75 10           jne 0xf392
F382  8A 46 FF        mov al, byte ptr [bp - 1]
F385  98              cwde
F386  8B F8           mov di, ax
F388  D1 E7           shl di, 1
F38A  FF B5 34 9B     push word ptr [di - 0x64cc]
F38E  0E              push cs
F38F  E8 CB C8        call 0xbc5d
loc_F392:
F392  80 7E FF 01     cmp byte ptr [bp - 1], 1
F396  75 D2           jne 0xf36a
F398  C6 06 1F 0C 00  mov byte ptr [0xc1f], 0
F39D  C6 06 1E 0C 00  mov byte ptr [0xc1e], 0
F3A2  C6 06 20 0C 00  mov byte ptr [0xc20], 0
F3A7  C4 7E 06        les di, ptr [bp + 6]
F3AA  06              push es
F3AB  57              push di
F3AC  0E              push cs
F3AD  E8 A0 DC        call 0xd050
F3B0  C6 46 FF 00     mov byte ptr [bp - 1], 0
F3B4  EB 03           jmp 0xf3b9
loc_F3B6:
F3B6  FE 46 FF        inc byte ptr [bp - 1]
loc_F3B9:
F3B9  8A 46 FF        mov al, byte ptr [bp - 1]
F3BC  98              cwde
F3BD  8B F8           mov di, ax
F3BF  D1 E7           shl di, 1
F3C1  FF B5 34 9B     push word ptr [di - 0x64cc]
F3C5  9A 77 0B 71 17  call far 1771:0B77
F3CA  08 C0           or al, al
F3CC  74 0F           je 0xf3dd
F3CE  8A 46 FF        mov al, byte ptr [bp - 1]
F3D1  98              cwde
F3D2  8B F8           mov di, ax
F3D4  D1 E7           shl di, 1
F3D6  FF B5 34 9B     push word ptr [di - 0x64cc]
F3DA  E8 71 C6        call 0xba4e
loc_F3DD:
F3DD  80 7E FF 01     cmp byte ptr [bp - 1], 1
F3E1  75 D3           jne 0xf3b6
F3E3  C4 3E 23 A9     les di, ptr [0xa923]
F3E7  26 C6 45 01 01  mov byte ptr es:[di + 1], 1
F3EC  89 EC           mov sp, bp
F3EE  5D              pop bp
F3EF  CA 04 00        retf 4

