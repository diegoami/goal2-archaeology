; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 23E4 (image offsets 23E40..2580F), part 2 of 3
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 23E4:0A52  (found by: call, jump)
sub_0A52:
0A52  0A C0           or al, al
0A54  74 F9           je 0xa4f
0A56  0A C9           or cl, cl
0A58  74 F5           je 0xa4f
0A5A  55              push bp
0A5B  8B EA           mov bp, dx
0A5D  33 D7           xor dx, di
0A5F  81 E2 00 80     and dx, 0x8000
0A63  86 D0           xchg al, dl
0A65  02 D1           add dl, cl
0A67  12 F0           adc dh, al
0A69  8A C8           mov cl, al
0A6B  81 CD 00 80     or bp, 0x8000
0A6F  81 CF 00 80     or di, 0x8000
0A73  52              push dx
0A74  0A E4           or ah, ah
0A76  75 04           jne 0xa7c
0A78  0B DB           or bx, bx
0A7A  74 0D           je 0xa89
loc_0A7C:
0A7C  0A ED           or ch, ch
0A7E  75 28           jne 0xaa8
0A80  0B F6           or si, si
0A82  75 24           jne 0xaa8
0A84  91              xchg cx, ax
0A85  87 DE           xchg si, bx
0A87  87 EF           xchg di, bp
loc_0A89:
0A89  8B C5           mov ax, bp
0A8B  8A C4           mov al, ah
0A8D  F6 E5           mul ch
0A8F  8B D8           mov bx, ax
0A91  8B C5           mov ax, bp
0A93  F7 E6           mul si
0A95  03 D8           add bx, ax
0A97  83 D2 00        adc dx, 0
0A9A  8B CA           mov cx, dx
0A9C  8B C5           mov ax, bp
0A9E  F7 E7           mul di
0AA0  03 C1           add ax, cx
0AA2  83 D2 00        adc dx, 0
0AA5  EB 7C           jmp 0xb23
; data (not reached as code), 1 bytes
0AA7                  db 90   ; .
loc_0AA8:
0AA8  57              push di
0AA9  56              push si
0AAA  51              push cx
0AAB  55              push bp
0AAC  53              push bx
0AAD  50              push ax
0AAE  8B EC           mov bp, sp
0AB0  33 C9           xor cx, cx
0AB2  8A 46 01        mov al, byte ptr [bp + 1]
0AB5  F6 66 07        mul byte ptr [bp + 7]
0AB8  8B F0           mov si, ax
0ABA  8B F9           mov di, cx
0ABC  8B D9           mov bx, cx
0ABE  8B 46 00        mov ax, word ptr [bp]
0AC1  F7 66 08        mul word ptr [bp + 8]
0AC4  03 F0           add si, ax
0AC6  13 FA           adc di, dx
0AC8  13 D9           adc bx, cx
0ACA  8B 46 02        mov ax, word ptr [bp + 2]
0ACD  F7 66 06        mul word ptr [bp + 6]
0AD0  03 F0           add si, ax
0AD2  13 FA           adc di, dx
0AD4  13 D9           adc bx, cx
0AD6  8B F1           mov si, cx
0AD8  8B 46 00        mov ax, word ptr [bp]
0ADB  F7 66 0A        mul word ptr [bp + 0xa]
0ADE  03 F8           add di, ax
0AE0  13 DA           adc bx, dx
0AE2  13 F1           adc si, cx
0AE4  8B 46 02        mov ax, word ptr [bp + 2]
0AE7  F7 66 08        mul word ptr [bp + 8]
0AEA  03 F8           add di, ax
0AEC  13 DA           adc bx, dx
0AEE  13 F1           adc si, cx
0AF0  8B 46 04        mov ax, word ptr [bp + 4]
0AF3  F7 66 06        mul word ptr [bp + 6]
0AF6  03 F8           add di, ax
0AF8  13 DA           adc bx, dx
0AFA  13 F1           adc si, cx
0AFC  8B F9           mov di, cx
0AFE  8B 46 02        mov ax, word ptr [bp + 2]
0B01  F7 66 0A        mul word ptr [bp + 0xa]
0B04  03 D8           add bx, ax
0B06  13 F2           adc si, dx
0B08  13 F9           adc di, cx
0B0A  8B 46 04        mov ax, word ptr [bp + 4]
0B0D  F7 66 08        mul word ptr [bp + 8]
0B10  03 D8           add bx, ax
0B12  13 F2           adc si, dx
0B14  13 F9           adc di, cx
0B16  8B 46 04        mov ax, word ptr [bp + 4]
0B19  F7 66 0A        mul word ptr [bp + 0xa]
0B1C  03 C6           add ax, si
0B1E  13 D7           adc dx, di
0B20  83 C4 0C        add sp, 0xc
loc_0B23:
0B23  93              xchg bx, ax
0B24  59              pop cx
0B25  5D              pop bp
0B26  0A F6           or dh, dh
0B28  78 07           js 0xb31
0B2A  D1 E0           shl ax, 1
0B2C  D1 D3           rcl bx, 1
0B2E  D1 D2           rcl dx, 1
0B30  49              dec cx
loc_0B31:
0B31  81 E9 81 80     sub cx, 0x8081
loc_0B35:
0B35  05 80 00        add ax, 0x80
0B38  83 D3 00        adc bx, 0
0B3B  83 D2 00        adc dx, 0
0B3E  73 03           jae 0xb43
0B40  D1 DA           rcr dx, 1
0B42  41              inc cx
loc_0B43:
0B43  F6 C5 40        test ch, 0x40
0B46  75 08           jne 0xb50
0B48  41              inc cx
0B49  8A C1           mov al, cl
0B4B  32 F5           xor dh, ch
0B4D  D0 ED           shr ch, 1
0B4F  C3              ret
loc_0B50:
0B50  33 C0           xor ax, ax
0B52  8B D8           mov bx, ax
0B54  8B D0           mov dx, ax
0B56  C3              ret

; ---- routine 23E4:0B57  (found by: call)
sub_0B57:
0B57  0A C0           or al, al
0B59  74 F5           je 0xb50
0B5B  55              push bp
0B5C  8B EA           mov bp, dx
0B5E  33 D7           xor dx, di
0B60  81 CF 00 80     or di, 0x8000
0B64  81 CD 00 80     or bp, 0x8000
0B68  81 E2 00 80     and dx, 0x8000
0B6C  86 C2           xchg dl, al
0B6E  2A D1           sub dl, cl
0B70  1A F0           sbb dh, al
0B72  52              push dx
0B73  B0 02           mov al, 2
0B75  BA 01 00        mov dx, 1
loc_0B78:
0B78  3B EF           cmp bp, di
0B7A  75 06           jne 0xb82
0B7C  3B DE           cmp bx, si
0B7E  75 02           jne 0xb82
0B80  3A E5           cmp ah, ch
loc_0B82:
0B82  72 06           jb 0xb8a
0B84  2A E5           sub ah, ch
0B86  1B DE           sbb bx, si
0B88  1B EF           sbb bp, di
loc_0B8A:
0B8A  D1 D2           rcl dx, 1
0B8C  72 11           jb 0xb9f
loc_0B8E:
0B8E  D0 E4           shl ah, 1
0B90  D1 D3           rcl bx, 1
0B92  D1 D5           rcl bp, 1
0B94  73 E2           jae 0xb78
0B96  2A E5           sub ah, ch
0B98  1B DE           sbb bx, si
0B9A  1B EF           sbb bp, di
0B9C  F8              clc
0B9D  EB EB           jmp 0xb8a
loc_0B9F:
0B9F  FE C8           dec al
0BA1  78 0A           js 0xbad
0BA3  52              push dx
0BA4  BA 01 00        mov dx, 1
0BA7  75 E5           jne 0xb8e
0BA9  B2 40           mov dl, 0x40
0BAB  EB E1           jmp 0xb8e
loc_0BAD:
0BAD  8B C2           mov ax, dx
0BAF  B1 06           mov cl, 6
0BB1  D3 E0           shl ax, cl
0BB3  5B              pop bx
0BB4  5A              pop dx
0BB5  59              pop cx
0BB6  5D              pop bp
0BB7  F7 D0           not ax
0BB9  F7 D3           not bx
0BBB  83 F2 FF        xor dx, 0xffff
0BBE  78 07           js 0xbc7
0BC0  D1 D0           rcl ax, 1
0BC2  D1 D3           rcl bx, 1
0BC4  D1 D2           rcl dx, 1
0BC6  49              dec cx
loc_0BC7:
0BC7  81 C1 80 80     add cx, 0x8080
0BCB  E9 67 FF        jmp 0xb35

; ---- routine 23E4:0BCE  (found by: call)
sub_0BCE:
0BCE  52              push dx
0BCF  33 D7           xor dx, di
0BD1  5A              pop dx
0BD2  79 05           jns 0xbd9
0BD4  52              push dx
0BD5  D1 D2           rcl dx, 1
0BD7  5A              pop dx
0BD8  C3              ret
loc_0BD9:
0BD9  F6 C6 80        test dh, 0x80
0BDC  74 07           je 0xbe5
0BDE  E8 04 00        call 0xbe5
0BE1  74 14           je 0xbf7
0BE3  F5              cmc
0BE4  C3              ret

; ---- routine 23E4:0BE5  (found by: call, jump)
sub_0BE5:
0BE5  3A C1           cmp al, cl
0BE7  75 0E           jne 0xbf7
0BE9  0A C0           or al, al
0BEB  74 0A           je 0xbf7
0BED  3B D7           cmp dx, di
0BEF  75 06           jne 0xbf7
0BF1  3B DE           cmp bx, si
0BF3  75 02           jne 0xbf7
0BF5  3A E5           cmp ah, ch
loc_0BF7:
0BF7  C3              ret

; ---- routine 23E4:0BF8  (found by: call)
sub_0BF8:
0BF8  8B D8           mov bx, ax
0BFA  0B DA           or bx, dx
0BFC  74 38           je 0xc36
0BFE  8A EE           mov ch, dh
0C00  0B D2           or dx, dx
0C02  79 0A           jns 0xc0e
0C04  F7 D0           not ax
0C06  F7 D2           not dx
0C08  05 01 00        add ax, 1
0C0B  83 D2 00        adc dx, 0
loc_0C0E:
0C0E  8B D8           mov bx, ax
0C10  B8 A0 00        mov ax, 0xa0
0C13  0B D2           or dx, dx
0C15  75 0C           jne 0xc23
0C17  87 D3           xchg bx, dx
0C19  B0 90           mov al, 0x90
0C1B  0A F6           or dh, dh
0C1D  75 04           jne 0xc23
0C1F  86 F2           xchg dl, dh
0C21  B0 88           mov al, 0x88
loc_0C23:
0C23  0B D2           or dx, dx
0C25  78 08           js 0xc2f
loc_0C27:
0C27  FE C8           dec al
0C29  03 DB           add bx, bx
0C2B  13 D2           adc dx, dx
0C2D  79 F8           jns 0xc27
loc_0C2F:
0C2F  0A ED           or ch, ch
0C31  78 03           js 0xc36
0C33  80 E6 7F        and dh, 0x7f
loc_0C36:
0C36  C3              ret

; ---- routine 23E4:0C37  (found by: call)
sub_0C37:
0C37  93              xchg bx, ax
0C38  B1 9F           mov cl, 0x9f
0C3A  2A CB           sub cl, bl
0C3C  72 4E           jb 0xc8c
0C3E  80 F9 1F        cmp cl, 0x1f
0C41  77 4B           ja 0xc8e
0C43  FE C1           inc cl
0C45  8A FE           mov bh, dh
0C47  80 CE 80        or dh, 0x80
0C4A  80 F9 11        cmp cl, 0x11
0C4D  72 07           jb 0xc56
0C4F  8B C2           mov ax, dx
0C51  33 D2           xor dx, dx
0C53  80 E9 10        sub cl, 0x10
loc_0C56:
0C56  80 F9 09        cmp cl, 9
0C59  72 0B           jb 0xc66
0C5B  8A C4           mov al, ah
0C5D  8A E2           mov ah, dl
0C5F  8A D6           mov dl, dh
0C61  32 F6           xor dh, dh
0C63  80 E9 08        sub cl, 8
loc_0C66:
0C66  D1 EA           shr dx, 1
0C68  D1 D8           rcr ax, 1
0C6A  FE C9           dec cl
0C6C  75 F8           jne 0xc66
0C6E  73 0C           jae 0xc7c
0C70  0A ED           or ch, ch
0C72  74 08           je 0xc7c
0C74  05 01 00        add ax, 1
0C77  83 D2 00        adc dx, 0
0C7A  78 10           js 0xc8c
loc_0C7C:
0C7C  0A FF           or bh, bh
0C7E  79 0A           jns 0xc8a
0C80  F7 D0           not ax
0C82  F7 D2           not dx
0C84  05 01 00        add ax, 1
0C87  83 D2 00        adc dx, 0
loc_0C8A:
0C8A  F8              clc
0C8B  C3              ret
loc_0C8C:
0C8C  F9              stc
0C8D  C3              ret
loc_0C8E:
0C8E  33 C0           xor ax, ax
0C90  33 D2           xor dx, dx
0C92  C3              ret

; ---- routine 23E4:0C93  (found by: far)
sub_0C93:
0C93  E8 F9 FC        call 0x98f
0C96  72 3B           jb 0xcd3
0C98  CB              retf
; data (not reached as code), 12 bytes
0C99                  db E8 EF FC 72 35 CB 8B C8 8B F3 8B FA   ; ...r5.......

; ---- routine 23E4:0CA5  (found by: far)
sub_0CA5:
0CA5  E8 AA FD        call 0xa52
0CA8  72 29           jb 0xcd3
0CAA  CB              retf

; ---- routine 23E4:0CAB  (found by: far)
sub_0CAB:
0CAB  0A C9           or cl, cl
0CAD  74 2A           je 0xcd9
0CAF  E8 A5 FE        call 0xb57
0CB2  72 1F           jb 0xcd3
0CB4  CB              retf
; data (not reached as code), 4 bytes
0CB5                  db E8 16 FF CB   ; ....

; ---- routine 23E4:0CB9  (found by: far)
sub_0CB9:
0CB9  E8 3C FF        call 0xbf8
0CBC  CB              retf
; data (not reached as code), 8 bytes
0CBD                  db B5 00 E8 75 FF 72 09 CB   ; ...u.r..

; ---- routine 23E4:0CC5  (found by: far)
sub_0CC5:
0CC5  B5 01           mov ch, 1
0CC7  E8 6D FF        call 0xc37
0CCA  72 01           jb 0xccd
0CCC  CB              retf
loc_0CCD:
0CCD  B8 CF 00        mov ax, 0xcf
0CD0  E9 FE F3        jmp 0xd1
loc_0CD3:
0CD3  B8 CD 00        mov ax, 0xcd
0CD6  E9 F8 F3        jmp 0xd1
loc_0CD9:
0CD9  B8 C8 00        mov ax, 0xc8
0CDC  E9 F2 F3        jmp 0xd1

; ---- routine 23E4:0CDF  (found by: call)
sub_0CDF:
0CDF  57              push di
0CE0  56              push si
0CE1  51              push cx
0CE2  E8 AA FC        call 0x98f
0CE5  59              pop cx
0CE6  5E              pop si
0CE7  5F              pop di
0CE8  C3              ret

; ---- routine 23E4:0CE9  (found by: call)
sub_0CE9:
0CE9  57              push di
0CEA  56              push si
0CEB  51              push cx
0CEC  E8 9C FC        call 0x98b
0CEF  59              pop cx
0CF0  5E              pop si
0CF1  5F              pop di
0CF2  C3              ret
; data (not reached as code), 10 bytes
0CF3                  db 57 56 51 E8 59 FD 59 5E 5F C3   ; WVQ.Y.Y^_.

; ---- routine 23E4:0CFD  (found by: call)
sub_0CFD:
0CFD  57              push di
0CFE  56              push si
0CFF  51              push cx
0D00  E8 54 FE        call 0xb57
0D03  59              pop cx
0D04  5E              pop si
0D05  5F              pop di
0D06  C3              ret
; data (not reached as code), 101 bytes
0D07                  db 3C A8 73 49 8B C8 8B F3 8B FA 32 E4 33 DB 33 D2   ; <.sI......2.3.3.
0D17                  db 80 E9 80 76 39 80 F9 10 72 0C 8A E7 8B DA BA FF   ; ...v9...r.......
0D27                  db FF 80 E9 10 EB EF 80 F9 08 72 0D 8A E3 8A DF 8A   ; .........r......
0D37                  db FA 8A D6 B6 FF 80 E9 08 0A C9 74 0B F9 D1 DA D1   ; ..........t.....
0D47                  db DB D0 DC FE C9 75 F5 23 D7 23 DE 22 E5 CB 32 C0   ; .....u.#.#."..2.
0D57                  db CB 52 53 50 0E E8 A8 FF 8B C8 8B F3 8B FA 58 5B   ; .RSP..........X[
0D67                  db 5A E8 20 FC CB   ; Z. ..

; ---- routine 23E4:0D6C  (found by: prologue)
sub_0D6C:
0D6C  55              push bp
0D6D  8B EC           mov bp, sp
0D6F  83 EC 08        sub sp, 8
0D72  8B C8           mov cx, ax
0D74  8B F3           mov si, bx
0D76  8B FA           mov di, dx
0D78  0A C0           or al, al
0D7A  74 3C           je 0xdb8
0D7C  F6 C6 80        test dh, 0x80
0D7F  75 41           jne 0xdc2
0D81  89 46 F8        mov word ptr [bp - 8], ax
0D84  89 5E FA        mov word ptr [bp - 6], bx
0D87  89 56 FC        mov word ptr [bp - 4], dx
0D8A  80 C1 80        add cl, 0x80
0D8D  D0 F9           sar cl, 1
0D8F  80 C1 80        add cl, 0x80
0D92  8A C1           mov al, cl
0D94  2C 14           sub al, 0x14
0D96  88 46 FE        mov byte ptr [bp - 2], al
loc_0D99:
0D99  8B 46 F8        mov ax, word ptr [bp - 8]
0D9C  8B 5E FA        mov bx, word ptr [bp - 6]
0D9F  8B 56 FC        mov dx, word ptr [bp - 4]
0DA2  E8 58 FF        call 0xcfd
0DA5  E8 37 FF        call 0xcdf
0DA8  FE C8           dec al
0DAA  52              push dx
0DAB  53              push bx
0DAC  50              push ax
0DAD  E8 DB FB        call 0x98b
0DB0  3A 46 FE        cmp al, byte ptr [bp - 2]
0DB3  59              pop cx
0DB4  5E              pop si
0DB5  5F              pop di
0DB6  73 E1           jae 0xd99
loc_0DB8:
0DB8  8B C1           mov ax, cx
0DBA  8B DE           mov bx, si
0DBC  8B D7           mov dx, di
0DBE  8B E5           mov sp, bp
0DC0  5D              pop bp
0DC1  CB              retf
loc_0DC2:
0DC2  5D              pop bp
0DC3  B8 CF 00        mov ax, 0xcf
0DC6  E9 08 F3        jmp 0xd1
; data (not reached as code), 158 bytes
0DC9                  db B9 81 21 BE A2 DA BF 0F C9 E8 BA FB 0A C0 74 03   ; ..!...........t.
0DD9                  db 80 F6 80 3C 6C 72 5C B9 83 21 BE A2 DA BF 0F 49   ; ...<lr\..!.....I
0DE9                  db 52 80 E6 7F E8 DE FD 5A 72 10 E8 07 FF 57 56 51   ; R......Zr....WVQ
0DF9                  db 0E E8 5B FF 59 5E 5F E8 F0 FE F6 C6 80 74 03 E8   ; ..[.Y^_......t..
0E09                  db D4 FE FE C9 E8 BE FD 9C 72 03 E8 D3 FE FE C9 E8   ; ........r.......
0E19                  db B3 FD 72 08 FE C1 80 CE 80 E8 6A FB 3C 6C 72 09   ; ..r.......j.<lr.
0E29                  db BF 3D 0E B9 07 00 E8 B6 02 9D 72 07 0A C0 74 03   ; .=........r...t.
0E39                  db 80 F6 80 CB 58 9D 39 9F 3F D7 60 43 9D 30 92 30   ; ....X.9.?.`C.0.0
0E49                  db 67 AA 3F 28 32 D7 6E B6 2A 1D EF 38 74 0D D0 00   ; g.?(2.n.*..8t...
0E59                  db 0D D0 7A 88 88 88 88 08 7E AB AA AA AA AA   ; ..z.....~.....

; ---- routine 23E4:0E67  (found by: far)
sub_0E67:
0E67  0A C0           or al, al
0E69  74 05           je 0xe70
0E6B  F6 C6 80        test dh, 0x80
0E6E  74 06           je 0xe76
loc_0E70:
0E70  B8 CF 00        mov ax, 0xcf
0E73  E9 5B F2        jmp 0xd1
loc_0E76:
0E76  B1 81           mov cl, 0x81
0E78  2A C1           sub al, cl
0E7A  50              push ax
0E7B  8A C1           mov al, cl
0E7D  B9 80 FB        mov cx, 0xfb80
0E80  BE 33 F3        mov si, 0xf333
0E83  BF 04 35        mov di, 0x3504
0E86  E8 C9 FB        call 0xa52
0E89  8B C8           mov cx, ax
0E8B  8B F3           mov si, bx
0E8D  8B FA           mov di, dx
0E8F  B8 81 00        mov ax, 0x81
0E92  33 DB           xor bx, bx
0E94  33 D2           xor dx, dx
0E96  E8 46 FE        call 0xcdf
0E99  52              push dx
0E9A  53              push bx
0E9B  50              push ax
0E9C  B8 81 00        mov ax, 0x81
0E9F  33 DB           xor bx, bx
0EA1  BA 00 80        mov dx, 0x8000
0EA4  E8 E8 FA        call 0x98f
0EA7  59              pop cx
0EA8  5E              pop si
0EA9  5F              pop di
0EAA  E8 AA FC        call 0xb57
0EAD  BF EC 0E        mov di, 0xeec
0EB0  B9 06 00        mov cx, 6
0EB3  E8 32 02        call 0x10e8
0EB6  FE C0           inc al
0EB8  B9 7F D2        mov cx, 0xd27f
0EBB  BE F7 17        mov si, 0x17f7
0EBE  BF 72 31        mov di, 0x3172
0EC1  E8 CB FA        call 0x98f
0EC4  59              pop cx
0EC5  52              push dx
0EC6  53              push bx
0EC7  50              push ax
0EC8  8A C1           mov al, cl
0ECA  98              cwde
0ECB  99              cdq
0ECC  E8 29 FD        call 0xbf8
0ECF  B9 80 D2        mov cx, 0xd280
0ED2  BE F7 17        mov si, 0x17f7
0ED5  BF 72 31        mov di, 0x3172
0ED8  E8 77 FB        call 0xa52
0EDB  59              pop cx
0EDC  5E              pop si
0EDD  5F              pop di
0EDE  E8 AE FA        call 0x98f
0EE1  3C 67           cmp al, 0x67
0EE3  73 06           jae 0xeeb
0EE5  33 C0           xor ax, ax
0EE7  33 DB           xor bx, bx
0EE9  33 D2           xor dx, dx
loc_0EEB:
0EEB  CB              retf
; data (not reached as code), 36 bytes
0EEC                  db 7D 8A 9D D8 89 1D 7D E9 A2 8B 2E 3A 7D 8E E3 38   ; }.....}....:}..8
0EFC                  db 8E 63 7E 49 92 24 49 12 7E CD CC CC CC 4C 7F AB   ; .c~I.$I.~....L..
0F0C                  db AA AA AA 2A   ; ...*

; ---- routine 23E4:0F10  (found by: far)
sub_0F10:
0F10  F6 C6 80        test dh, 0x80
0F13  9C              pushf
0F14  80 E6 7F        and dh, 0x7f
0F17  B9 80 D2        mov cx, 0xd280
0F1A  BE F7 17        mov si, 0x17f7
0F1D  BF 72 31        mov di, 0x3172
0F20  E8 34 FC        call 0xb57
0F23  3C 88           cmp al, 0x88
0F25  73 55           jae 0xf7c
0F27  52              push dx
0F28  53              push bx
0F29  50              push ax
0F2A  FE C0           inc al
0F2C  B5 FF           mov ch, 0xff
0F2E  E8 06 FD        call 0xc37
0F31  59              pop cx
0F32  5E              pop si
0F33  5F              pop di
0F34  50              push ax
0F35  51              push cx
0F36  E8 BF FC        call 0xbf8
0F39  59              pop cx
0F3A  0A C0           or al, al
0F3C  74 02           je 0xf40
0F3E  FE C8           dec al
loc_0F40:
0F40  91              xchg cx, ax
0F41  87 DE           xchg si, bx
0F43  87 D7           xchg di, dx
0F45  E8 43 FA        call 0x98b
0F48  BF 83 0F        mov di, 0xf83
0F4B  B9 08 00        mov cx, 8
0F4E  E8 B0 01        call 0x1101
0F51  59              pop cx
0F52  D1 E9           shr cx, 1
0F54  73 0E           jae 0xf64
0F56  51              push cx
0F57  B9 81 FB        mov cx, 0xfb81
0F5A  BE 33 F3        mov si, 0xf333
0F5D  BF 04 35        mov di, 0x3504
0F60  E8 EF FA        call 0xa52
0F63  59              pop cx
loc_0F64:
0F64  02 C1           add al, cl
0F66  72 14           jb 0xf7c
0F68  9D              popf
0F69  74 10           je 0xf7b
0F6B  8B C8           mov cx, ax
0F6D  8B F3           mov si, bx
0F6F  8B FA           mov di, dx
0F71  B8 81 00        mov ax, 0x81
0F74  33 DB           xor bx, bx
0F76  33 D2           xor dx, dx
0F78  E8 DC FB        call 0xb57
loc_0F7B:
0F7B  CB              retf
loc_0F7C:
0F7C  58              pop ax
0F7D  B8 CD 00        mov ax, 0xcd
0F80  E9 4E F1        jmp 0xd1
; data (not reached as code), 48 bytes
0F83                  db 6D 2E 1D 11 60 31 70 46 2C FE E5 7F 74 36 7C 89   ; m...`1pF,...t6|.
0F93                  db 84 21 77 53 3C FF C3 2E 7A D2 7D 5B 95 1D 7C 25   ; .!wS<...z.}[..|%
0FA3                  db B8 46 58 63 7E 16 FC EF FD 75 80 D2 F7 17 72 31   ; .FXc~....u....r1

; ---- routine 23E4:0FB3  (found by: prologue)
sub_0FB3:
0FB3  55              push bp
0FB4  8B EC           mov bp, sp
0FB6  83 EC 06        sub sp, 6
0FB9  0A C0           or al, al
0FBB  75 03           jne 0xfc0
0FBD  E9 D0 00        jmp 0x1090
loc_0FC0:
0FC0  33 C9           xor cx, cx
0FC2  F6 C6 80        test dh, 0x80
0FC5  74 04           je 0xfcb
0FC7  41              inc cx
0FC8  80 E6 7F        and dh, 0x7f
loc_0FCB:
0FCB  51              push cx
0FCC  B9 81 00        mov cx, 0x81
0FCF  33 F6           xor si, si
0FD1  33 FF           xor di, di
0FD3  E8 F8 FB        call 0xbce
0FD6  72 0C           jb 0xfe4
0FD8  91              xchg cx, ax
0FD9  87 DE           xchg si, bx
0FDB  87 D7           xchg di, dx
0FDD  E8 77 FB        call 0xb57
0FE0  59              pop cx
0FE1  41              inc cx
0FE2  41              inc cx
0FE3  51              push cx
loc_0FE4:
0FE4  B9 7E 4A        mov cx, 0x4a7e
0FE7  BE 8E E9        mov si, 0xe98e
0FEA  BF 6F 0C        mov di, 0xc6f
0FED  E8 DE FB        call 0xbce
0FF0  73 05           jae 0xff7
0FF2  E8 ED 00        call 0x10e2
0FF5  EB 77           jmp 0x106e
loc_0FF7:
0FF7  BF 94 10        mov di, 0x1094
0FFA  B9 02 00        mov cx, 2
0FFD  51              push cx
0FFE  57              push di
0FFF  2E 8B 0D        mov cx, word ptr cs:[di]
1002  2E 8B 75 02     mov si, word ptr cs:[di + 2]
1006  2E 8B 7D 04     mov di, word ptr cs:[di + 4]
100A  E8 C1 FB        call 0xbce
100D  5F              pop di
100E  59              pop cx
100F  72 08           jb 0x1019
1011  83 C7 12        add di, 0x12
1014  E2 E7           loop 0xffd
1016  83 EF 06        sub di, 6
loc_1019:
1019  83 C7 06        add di, 6
101C  89 46 FA        mov word ptr [bp - 6], ax
101F  89 5E FC        mov word ptr [bp - 4], bx
1022  89 56 FE        mov word ptr [bp - 2], dx
1025  57              push di
1026  2E 8B 0D        mov cx, word ptr cs:[di]
1029  2E 8B 75 02     mov si, word ptr cs:[di + 2]
102D  2E 8B 7D 04     mov di, word ptr cs:[di + 4]
1031  E8 B5 FC        call 0xce9
1034  52              push dx
1035  53              push bx
1036  50              push ax
1037  8B 46 FA        mov ax, word ptr [bp - 6]
103A  8B 5E FC        mov bx, word ptr [bp - 4]
103D  8B 56 FE        mov dx, word ptr [bp - 2]
1040  E8 0F FA        call 0xa52
1043  B9 81 00        mov cx, 0x81
1046  33 F6           xor si, si
1048  33 FF           xor di, di
104A  E8 42 F9        call 0x98f
104D  8B C8           mov cx, ax
104F  8B F3           mov si, bx
1051  8B FA           mov di, dx
1053  58              pop ax
1054  5B              pop bx
1055  5A              pop dx
1056  E8 FE FA        call 0xb57
1059  E8 86 00        call 0x10e2
105C  5F              pop di
105D  83 C7 06        add di, 6
1060  2E 8B 0D        mov cx, word ptr cs:[di]
1063  2E 8B 75 02     mov si, word ptr cs:[di + 2]
1067  2E 8B 7D 04     mov di, word ptr cs:[di + 4]
106B  E8 21 F9        call 0x98f
loc_106E:
106E  59              pop cx
106F  F6 C1 02        test cl, 2
1072  74 14           je 0x1088
1074  51              push cx
1075  8B C8           mov cx, ax
1077  8B F3           mov si, bx
1079  8B FA           mov di, dx
107B  B8 81 21        mov ax, 0x2181
107E  BB A2 DA        mov bx, 0xdaa2
1081  BA 0F 49        mov dx, 0x490f
1084  E8 04 F9        call 0x98b
1087  59              pop cx
loc_1088:
1088  F6 C1 01        test cl, 1
108B  74 03           je 0x1090
108D  80 CE 80        or dh, 0x80
loc_1090:
1090  8B E5           mov sp, bp
1092  5D              pop bp
1093  CB              retf
; data (not reached as code), 78 bytes
1094                  db 7F E7 CF CC 13 54 7F F6 F4 A2 30 09 7F 6A C1 91   ; .....T....0..j..
10A4                  db 0A 06 80 B5 9E 8A 6F 44 80 82 2C 3A CD 13 80 6A   ; ......oD..,:...j
10B4                  db C1 91 0A 06 81 00 00 00 00 00 80 21 A2 DA 0F 49   ; ...........!...I
10C4                  db 7D E8 A2 8B 2E BA 7D 8E E3 38 8E 63 7E 49 92 24   ; }.....}..8.c~I.$
10D4                  db 49 92 7E CD CC CC CC 4C 7F AB AA AA AA AA   ; I.~....L......

; ---- routine 23E4:10E2  (found by: call)
sub_10E2:
10E2  BF C4 10        mov di, 0x10c4
10E5  B9 05 00        mov cx, 5

; ---- routine 23E4:10E8  (found by: call)
sub_10E8:
10E8  52              push dx
10E9  53              push bx
10EA  50              push ax
10EB  51              push cx
10EC  57              push di
10ED  8B C8           mov cx, ax
10EF  8B F3           mov si, bx
10F1  8B FA           mov di, dx
10F3  E8 5C F9        call 0xa52
10F6  5F              pop di
10F7  59              pop cx
10F8  E8 06 00        call 0x1101
10FB  59              pop cx
10FC  5E              pop si
10FD  5F              pop di
10FE  E9 51 F9        jmp 0xa52

; ---- routine 23E4:1101  (found by: call)
sub_1101:
1101  55              push bp
1102  8B EC           mov bp, sp
1104  83 EC 06        sub sp, 6
1107  89 46 FA        mov word ptr [bp - 6], ax
110A  89 5E FC        mov word ptr [bp - 4], bx
110D  89 56 FE        mov word ptr [bp - 2], dx
1110  2E 8B 05        mov ax, word ptr cs:[di]
1113  2E 8B 5D 02     mov bx, word ptr cs:[di + 2]
1117  2E 8B 55 04     mov dx, word ptr cs:[di + 4]
111B  51              push cx
111C  57              push di
111D  EB 10           jmp 0x112f
; data (not reached as code), 16 bytes
111F                  db 51 57 2E 8B 0D 2E 8B 75 02 2E 8B 7D 04 E8 60 F8   ; QW.....u...}..`.
loc_112F:
112F  8B 4E FA        mov cx, word ptr [bp - 6]
1132  8B 76 FC        mov si, word ptr [bp - 4]
1135  8B 7E FE        mov di, word ptr [bp - 2]
1138  E8 17 F9        call 0xa52
113B  5F              pop di
113C  59              pop cx
113D  83 C7 06        add di, 6
1140  E2 DD           loop 0x111f
1142  B9 81 00        mov cx, 0x81
1145  33 F6           xor si, si
1147  33 FF           xor di, di
1149  E8 43 F8        call 0x98f
114C  8B E5           mov sp, bp
114E  5D              pop bp
114F  C3              ret
; data (not reached as code), 135 bytes
1150                  db E8 4C 00 33 C0 8B DC 36 8B 5F 04 0B DB 74 04 92   ; .L.3...6._...t..
1160                  db F7 F3 92 CA 02 00 E8 36 00 93 B8 80 00 B9 20 00   ; .......6...... .
1170                  db F6 C6 80 75 0A D1 E3 D1 D2 FE C8 E2 F3 32 C0 80   ; ...u.........2..
1180                  db E6 7F CB E8 19 00 CD 3C 9F 06 9D 11 CD 37 06 62   ; .......<.....7.b
1190                  db 7B CD 35 E1 CD 35 FD CD 39 D9 CD 3D CB E1 FF A1   ; {.5..5..9..=....
11A0                  db 62 7B 8B 1E 64 7B 8B C8 2E F7 26 D5 11 D1 E1 D1   ; b{..d{....&.....
11B0                  db E1 D1 E1 02 E9 03 D1 03 D3 D1 E3 D1 E3 03 D3 02   ; ................
11C0                  db F3 B1 05 D3 E3 02 F3 05 01 00 83 D2 00 A3 62 7B   ; ..............b{
11D0                  db 89 16 64 7B C3 05 84   ; ..d{...

; ---- routine 23E4:11D7  (found by: far)
sub_11D7:
11D7  B4 2C           mov ah, 0x2c
11D9  CD 21           int 0x21   ; INT 21h AH=2C get time
11DB  89 0E 62 7B     mov word ptr [0x7b62], cx
11DF  89 16 64 7B     mov word ptr [0x7b64], dx
11E3  CB              retf

; ---- routine 23E4:11E4  (found by: call)
sub_11E4:
11E4  57              push di
11E5  FC              cld
11E6  8B D8           mov bx, ax
11E8  0B D2           or dx, dx
11EA  7D 0D           jge 0x11f9
11EC  F7 D3           not bx
11EE  F7 D2           not dx
11F0  83 C3 01        add bx, 1
11F3  83 D2 00        adc dx, 0
11F6  B0 2D           mov al, 0x2d
11F8  AA              stosb byte ptr es:[di], al
loc_11F9:
11F9  BE 36 12        mov si, 0x1236
11FC  B1 09           mov cl, 9
loc_11FE:
11FE  2E 3B 54 02     cmp dx, word ptr cs:[si + 2]
1202  72 07           jb 0x120b
1204  77 0C           ja 0x1212
1206  2E 3B 1C        cmp bx, word ptr cs:[si]
1209  73 07           jae 0x1212
loc_120B:
120B  83 C6 04        add si, 4
120E  FE C9           dec cl
1210  75 EC           jne 0x11fe
loc_1212:
1212  FE C1           inc cl
loc_1214:
1214  B0 2F           mov al, 0x2f
loc_1216:
1216  FE C0           inc al
1218  2E 2B 1C        sub bx, word ptr cs:[si]
121B  2E 1B 54 02     sbb dx, word ptr cs:[si + 2]
121F  73 F5           jae 0x1216
1221  2E 03 1C        add bx, word ptr cs:[si]
1224  2E 13 54 02     adc dx, word ptr cs:[si + 2]
1228  83 C6 04        add si, 4
122B  AA              stosb byte ptr es:[di], al
122C  FE C9           dec cl
122E  75 E4           jne 0x1214
1230  8B CF           mov cx, di
1232  5F              pop di
1233  2B CF           sub cx, di
1235  C3              ret
; data (not reached as code), 40 bytes
1236                  db 00 CA 9A 3B 00 E1 F5 05 80 96 98 00 40 42 0F 00   ; ...;........@B..
1246                  db A0 86 01 00 10 27 00 00 E8 03 00 00 64 00 00 00   ; .....'......d...
1256                  db 0A 00 00 00 01 00 00 00   ; ........

; ---- routine 23E4:125E  (found by: call)
sub_125E:
125E  33 C0           xor ax, ax
1260  33 D2           xor dx, dx
1262  33 F6           xor si, si
1264  E3 59           jcxz 0x12bf
1266  26 80 3D 2B     cmp byte ptr es:[di], 0x2b
126A  74 07           je 0x1273
126C  26 80 3D 2D     cmp byte ptr es:[di], 0x2d
1270  75 05           jne 0x1277
1272  46              inc si
loc_1273:
1273  47              inc di
1274  49              dec cx
1275  E3 48           jcxz 0x12bf
loc_1277:
1277  26 80 3D 24     cmp byte ptr es:[di], 0x24
127B  74 44           je 0x12c1
127D  26 8A 1D        mov bl, byte ptr es:[di]
1280  80 EB 3A        sub bl, 0x3a
1283  80 C3 0A        add bl, 0xa
1286  73 28           jae 0x12b0
1288  F7 C2 00 F0     test dx, 0xf000
128C  75 31           jne 0x12bf
128E  53              push bx
128F  D1 E0           shl ax, 1
1291  D1 D2           rcl dx, 1
1293  52              push dx
1294  50              push ax
1295  D1 E0           shl ax, 1
1297  D1 D2           rcl dx, 1
1299  D1 E0           shl ax, 1
129B  D1 D2           rcl dx, 1
129D  5B              pop bx
129E  03 C3           add ax, bx
12A0  5B              pop bx
12A1  13 D3           adc dx, bx
12A3  5B              pop bx
12A4  32 FF           xor bh, bh
12A6  03 C3           add ax, bx
12A8  83 D2 00        adc dx, 0
12AB  78 12           js 0x12bf
12AD  47              inc di
12AE  E2 CD           loop 0x127d
loc_12B0:
12B0  4E              dec si
12B1  75 0A           jne 0x12bd
12B3  F7 D0           not ax
12B5  F7 D2           not dx
12B7  05 01 00        add ax, 1
12BA  83 D2 00        adc dx, 0
loc_12BD:
12BD  F8              clc
12BE  C3              ret
loc_12BF:
12BF  F9              stc
12C0  C3              ret
loc_12C1:
12C1  47              inc di
12C2  49              dec cx
12C3  E3 FA           jcxz 0x12bf
12C5  26 8A 1D        mov bl, byte ptr es:[di]
12C8  80 FB 61        cmp bl, 0x61
12CB  72 03           jb 0x12d0
12CD  80 EB 20        sub bl, 0x20
loc_12D0:
12D0  80 EB 3A        sub bl, 0x3a
12D3  80 C3 0A        add bl, 0xa
12D6  72 0B           jb 0x12e3
12D8  80 EB 17        sub bl, 0x17
12DB  80 C3 06        add bl, 6
12DE  73 D0           jae 0x12b0
12E0  80 C3 0A        add bl, 0xa
loc_12E3:
12E3  B7 04           mov bh, 4
loc_12E5:
12E5  D1 E0           shl ax, 1
12E7  D1 D2           rcl dx, 1
12E9  72 D4           jb 0x12bf
12EB  FE CF           dec bh
12ED  75 F6           jne 0x12e5
12EF  0A C3           or al, bl
12F1  47              inc di
12F2  E2 D1           loop 0x12c5
12F4  EB BA           jmp 0x12b0

; ---- routine 23E4:12F6  (found by: far)
sub_12F6:
12F6  55              push bp
12F7  8B EC           mov bp, sp
12F9  83 EC 20        sub sp, 0x20
12FC  8B 46 0E        mov ax, word ptr [bp + 0xe]
12FF  8B 56 10        mov dx, word ptr [bp + 0x10]
1302  8D 7E E0        lea di, [bp - 0x20]
1305  16              push ss
1306  07              pop es
1307  E8 DA FE        call 0x11e4
130A  1E              push ds
130B  8B F7           mov si, di
130D  16              push ss
130E  1F              pop ds
130F  C4 7E 08        les di, ptr [bp + 8]
1312  8B 56 06        mov dx, word ptr [bp + 6]
1315  8B 46 0C        mov ax, word ptr [bp + 0xc]
1318  3B C2           cmp ax, dx
131A  7E 02           jle 0x131e
131C  8B C2           mov ax, dx
loc_131E:
131E  3B CA           cmp cx, dx
1320  7E 02           jle 0x1324
1322  8B CA           mov cx, dx
loc_1324:
1324  3B C1           cmp ax, cx
1326  7D 02           jge 0x132a
1328  8B C1           mov ax, cx
loc_132A:
132A  FC              cld
132B  AA              stosb byte ptr es:[di], al
132C  2B C1           sub ax, cx
132E  74 08           je 0x1338
1330  51              push cx
1331  8B C8           mov cx, ax
1333  B0 20           mov al, 0x20
1335  F3 AA           rep stosb byte ptr es:[di], al
1337  59              pop cx
loc_1338:
1338  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
133A  1F              pop ds
133B  8B E5           mov sp, bp
133D  5D              pop bp
133E  CA 0C 00        retf 0xc

; ---- routine 23E4:1341  (found by: far)
sub_1341:
1341  55              push bp
1342  8B EC           mov bp, sp
1344  C4 7E 0A        les di, ptr [bp + 0xa]
1347  26 8A 0D        mov cl, byte ptr es:[di]
134A  32 ED           xor ch, ch
134C  47              inc di
134D  E3 09           jcxz 0x1358
134F  26 80 3D 20     cmp byte ptr es:[di], 0x20
1353  75 03           jne 0x1358
1355  47              inc di
1356  E2 F7           loop 0x134f
loc_1358:
1358  E8 03 FF        call 0x125e
135B  72 02           jb 0x135f
135D  E3 09           jcxz 0x1368
loc_135F:
135F  8B CF           mov cx, di
1361  2B 4E 0A        sub cx, word ptr [bp + 0xa]
1364  33 C0           xor ax, ax
1366  33 D2           xor dx, dx
loc_1368:
1368  C4 7E 06        les di, ptr [bp + 6]
136B  26 89 0D        mov word ptr es:[di], cx
136E  5D              pop bp
136F  CA 08 00        retf 8

; ---- routine 23E4:1372  (found by: call)
sub_1372:
1372  8B DC           mov bx, sp
1374  1E              push ds
1375  36 C4 7F 08     les di, ptr ss:[bx + 8]
1379  36 C5 77 04     lds si, ptr ss:[bx + 4]
137D  FC              cld
137E  33 C0           xor ax, ax
1380  AB              stosw word ptr es:[di], ax
1381  B8 B0 D7        mov ax, 0xd7b0
1384  AB              stosw word ptr es:[di], ax
1385  B8 80 00        mov ax, 0x80
1388  AB              stosw word ptr es:[di], ax
1389  33 C0           xor ax, ax
138B  AB              stosw word ptr es:[di], ax
138C  AB              stosw word ptr es:[di], ax
138D  AB              stosw word ptr es:[di], ax
138E  8D 45 74        lea ax, [di + 0x74]
1391  AB              stosw word ptr es:[di], ax
1392  8C C0           mov ax, es
1394  AB              stosw word ptr es:[di], ax
1395  B8 87 14        mov ax, 0x1487
1398  AB              stosw word ptr es:[di], ax
1399  8C C8           mov ax, cs
139B  AB              stosw word ptr es:[di], ax
139C  33 C0           xor ax, ax
139E  B9 0E 00        mov cx, 0xe
13A1  F3 AB           rep stosw word ptr es:[di], ax
13A3  AC              lodsb al, byte ptr [si]
13A4  3C 4F           cmp al, 0x4f
13A6  76 02           jbe 0x13aa
13A8  B0 4F           mov al, 0x4f
loc_13AA:
13AA  8A C8           mov cl, al
13AC  32 ED           xor ch, ch
13AE  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
13B0  32 C0           xor al, al
13B2  AA              stosb byte ptr es:[di], al
13B3  1F              pop ds
13B4  CA 08 00        retf 8
; data (not reached as code), 43 bytes
13B7                  db 8B DC 36 C4 7F 0A 36 8B 47 04 26 89 45 04 36 8B   ; ..6...6.G.&.E.6.
13C7                  db 47 06 26 89 45 0C 36 8B 47 08 26 89 45 0E 33 C0   ; G.&.E.6.G.&.E.3.
13D7                  db 26 89 45 08 26 89 45 0A CA 0A 00   ; &.E.&.E....

; ---- routine 23E4:13E2  (found by: call, far)
sub_13E2:
13E2  BA B1 D7        mov dx, 0xd7b1
13E5  EB 08           jmp 0x13ef

; ---- routine 23E4:13E7  (found by: call, far)
sub_13E7:
13E7  BA B2 D7        mov dx, 0xd7b2
13EA  EB 03           jmp 0x13ef
; data (not reached as code), 3 bytes
13EC                  db BA B3 D7   ; ...
loc_13EF:
13EF  8B DC           mov bx, sp
13F1  36 C4 7F 04     les di, ptr ss:[bx + 4]
13F5  26 8B 45 02     mov ax, word ptr es:[di + 2]
13F9  3D B1 D7        cmp ax, 0xd7b1
13FC  74 12           je 0x1410
13FE  3D B2 D7        cmp ax, 0xd7b2
1401  74 0D           je 0x1410
1403  3D B0 D7        cmp ax, 0xd7b0
1406  74 10           je 0x1418
1408  C7 06 60 7B 66 00 mov word ptr [0x7b60], 0x66
140E  EB 24           jmp 0x1434
loc_1410:
1410  52              push dx
1411  06              push es
1412  57              push di
1413  0E              push cs
1414  E8 24 00        call 0x143b
1417  5A              pop dx
loc_1418:
1418  33 C0           xor ax, ax
141A  26 89 55 02     mov word ptr es:[di + 2], dx
141E  26 89 45 08     mov word ptr es:[di + 8], ax
1422  26 89 45 0A     mov word ptr es:[di + 0xa], ax
1426  BB 10 00        mov bx, 0x10
1429  E8 4A 00        call 0x1476
142C  74 06           je 0x1434
142E  26 C7 45 02 B0 D7 mov word ptr es:[di + 2], 0xd7b0
loc_1434:
1434  CA 04 00        retf 4
; data (not reached as code), 4 bytes
1437                  db B0 00 EB 02   ; ....

