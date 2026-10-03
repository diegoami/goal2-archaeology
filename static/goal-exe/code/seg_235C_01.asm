; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 235C (image offsets 235C0..2381F), part 1 of 1
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 235C:0000  (found by: far)
sub_0000:
0000  5E              pop si
0001  5A              pop dx
0002  59              pop cx
0003  5B              pop bx
0004  B0 21           mov al, 0x21
0006  50              push ax
0007  53              push bx
0008  51              push cx
0009  52              push dx
000A  56              push si

; ---- routine 235C:000B  (found by: far)
sub_000B:
000B  55              push bp
000C  1E              push ds
000D  8B EC           mov bp, sp
000F  9C              pushf
0010  BB 45 00        mov bx, 0x45
0013  0E              push cs
0014  53              push bx
0015  33 DB           xor bx, bx
0017  8E DB           mov ds, bx
0019  8A 5E 0C        mov bl, byte ptr [bp + 0xc]
001C  D1 E3           shl bx, 1
001E  D1 E3           shl bx, 1
0020  C5 1F           lds bx, ptr [bx]
0022  1E              push ds
0023  53              push bx
0024  C5 76 08        lds si, ptr [bp + 8]
0027  FC              cld
0028  AD              lodsw ax, word ptr [si]
0029  50              push ax
002A  AD              lodsw ax, word ptr [si]
002B  8B D8           mov bx, ax
002D  AD              lodsw ax, word ptr [si]
002E  8B C8           mov cx, ax
0030  AD              lodsw ax, word ptr [si]
0031  8B D0           mov dx, ax
0033  AD              lodsw ax, word ptr [si]
0034  8B E8           mov bp, ax
0036  AD              lodsw ax, word ptr [si]
0037  50              push ax
0038  AD              lodsw ax, word ptr [si]
0039  8B F8           mov di, ax
003B  AD              lodsw ax, word ptr [si]
003C  50              push ax
003D  AD              lodsw ax, word ptr [si]
003E  8E C0           mov es, ax
0040  1F              pop ds
0041  5E              pop si
0042  58              pop ax
0043  FA              cli
0044  CB              retf
; data (not reached as code), 3 bytes
0045                  db 9C 06 57   ; ..W

; ---- routine 235C:0048  (found by: prologue)
sub_0048:
0048  55              push bp
0049  8B EC           mov bp, sp
004B  C4 7E 10        les di, ptr [bp + 0x10]
004E  FC              cld
004F  AB              stosw word ptr es:[di], ax
0050  8B C3           mov ax, bx
0052  AB              stosw word ptr es:[di], ax
0053  8B C1           mov ax, cx
0055  AB              stosw word ptr es:[di], ax
0056  8B C2           mov ax, dx
0058  AB              stosw word ptr es:[di], ax
0059  58              pop ax
005A  AB              stosw word ptr es:[di], ax
005B  8B C6           mov ax, si
005D  AB              stosw word ptr es:[di], ax
005E  58              pop ax
005F  AB              stosw word ptr es:[di], ax
0060  8C D8           mov ax, ds
0062  AB              stosw word ptr es:[di], ax
0063  58              pop ax
0064  AB              stosw word ptr es:[di], ax
0065  58              pop ax
0066  AB              stosw word ptr es:[di], ax
0067  1F              pop ds
0068  5D              pop bp
0069  CA 06 00        retf 6

; ---- routine 235C:006C  (found by: far)
sub_006C:
006C  55              push bp
006D  8B EC           mov bp, sp
006F  B4 2A           mov ah, 0x2a
0071  CD 21           int 0x21   ; INT 21h AH=2A get date
0073  32 E4           xor ah, ah
0075  C4 7E 06        les di, ptr [bp + 6]
0078  AB              stosw word ptr es:[di], ax
0079  8A C2           mov al, dl
007B  C4 7E 0A        les di, ptr [bp + 0xa]
007E  AB              stosw word ptr es:[di], ax
007F  8A C6           mov al, dh
0081  C4 7E 0E        les di, ptr [bp + 0xe]
0084  AB              stosw word ptr es:[di], ax
0085  91              xchg cx, ax
0086  C4 7E 12        les di, ptr [bp + 0x12]
0089  AB              stosw word ptr es:[di], ax
008A  5D              pop bp
008B  CA 10 00        retf 0x10

; ---- routine 235C:008E  (found by: prologue)
sub_008E:
008E  55              push bp
008F  8B EC           mov bp, sp
0091  8B 4E 0A        mov cx, word ptr [bp + 0xa]
0094  8A 76 08        mov dh, byte ptr [bp + 8]
0097  8A 56 06        mov dl, byte ptr [bp + 6]
009A  B4 2B           mov ah, 0x2b
009C  CD 21           int 0x21   ; INT 21h AH=2B ?
009E  5D              pop bp
009F  CA 06 00        retf 6

; ---- routine 235C:00A2  (found by: prologue)
sub_00A2:
00A2  55              push bp
00A3  8B EC           mov bp, sp
00A5  B4 2C           mov ah, 0x2c
00A7  CD 21           int 0x21   ; INT 21h AH=2C get time
00A9  32 E4           xor ah, ah
00AB  8A C2           mov al, dl
00AD  C4 7E 06        les di, ptr [bp + 6]
00B0  AB              stosw word ptr es:[di], ax
00B1  8A C6           mov al, dh
00B3  C4 7E 0A        les di, ptr [bp + 0xa]
00B6  AB              stosw word ptr es:[di], ax
00B7  8A C1           mov al, cl
00B9  C4 7E 0E        les di, ptr [bp + 0xe]
00BC  AB              stosw word ptr es:[di], ax
00BD  8A C5           mov al, ch
00BF  C4 7E 12        les di, ptr [bp + 0x12]
00C2  AB              stosw word ptr es:[di], ax
00C3  5D              pop bp
00C4  CA 10 00        retf 0x10

; ---- routine 235C:00C7  (found by: prologue)
sub_00C7:
00C7  55              push bp
00C8  8B EC           mov bp, sp
00CA  8A 6E 0C        mov ch, byte ptr [bp + 0xc]
00CD  8A 4E 0A        mov cl, byte ptr [bp + 0xa]
00D0  8A 76 08        mov dh, byte ptr [bp + 8]
00D3  8A 56 06        mov dl, byte ptr [bp + 6]
00D6  B4 2D           mov ah, 0x2d
00D8  CD 21           int 0x21   ; INT 21h AH=2D ?
00DA  5D              pop bp
00DB  CA 08 00        retf 8

; ---- routine 235C:00DE  (found by: far)
sub_00DE:
00DE  55              push bp
00DF  8B EC           mov bp, sp
00E1  83 EC 50        sub sp, 0x50
00E4  1E              push ds
00E5  C5 76 0C        lds si, ptr [bp + 0xc]
00E8  8D 7E B0        lea di, [bp - 0x50]
00EB  16              push ss
00EC  07              pop es
00ED  FC              cld
00EE  AC              lodsb al, byte ptr [si]
00EF  3C 4F           cmp al, 0x4f
00F1  72 02           jb 0xf5
00F3  B0 4F           mov al, 0x4f
loc_00F5:
00F5  98              cwde
00F6  91              xchg cx, ax
00F7  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
00F9  32 C0           xor al, al
00FB  AA              stosb byte ptr es:[di], al
00FC  C5 56 06        lds dx, ptr [bp + 6]
00FF  B4 1A           mov ah, 0x1a
0101  CD 21           int 0x21   ; INT 21h AH=1A set DTA
0103  8D 56 B0        lea dx, [bp - 0x50]
0106  16              push ss
0107  1F              pop ds
0108  8B 4E 0A        mov cx, word ptr [bp + 0xa]
010B  B4 4E           mov ah, 0x4e
010D  CD 21           int 0x21   ; INT 21h AH=4E find first
010F  1F              pop ds
0110  C4 7E 06        les di, ptr [bp + 6]
0113  E8 20 00        call 0x136
0116  8B E5           mov sp, bp
0118  5D              pop bp
0119  CA 0A 00        retf 0xa

; ---- routine 235C:011C  (found by: far)
sub_011C:
011C  55              push bp
011D  8B EC           mov bp, sp
011F  1E              push ds
0120  C5 56 06        lds dx, ptr [bp + 6]
0123  B4 1A           mov ah, 0x1a
0125  CD 21           int 0x21   ; INT 21h AH=1A set DTA
0127  1F              pop ds
0128  B4 4F           mov ah, 0x4f
012A  CD 21           int 0x21   ; INT 21h AH=4F find next
012C  C4 7E 06        les di, ptr [bp + 6]
012F  E8 04 00        call 0x136
0132  5D              pop bp
0133  CA 04 00        retf 4

; ---- routine 235C:0136  (found by: call)
sub_0136:
0136  72 1D           jb 0x155
0138  83 C7 1E        add di, 0x1e
013B  1E              push ds
013C  06              push es
013D  1F              pop ds
013E  32 C0           xor al, al
0140  B9 00 01        mov cx, 0x100
0143  FC              cld
0144  F2 AE           repne scasb al, byte ptr es:[di]
0146  F6 D1           not cl
0148  8A C1           mov al, cl
014A  4F              dec di
014B  8B F7           mov si, di
014D  4E              dec si
014E  FD              std
014F  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
0151  AA              stosb byte ptr es:[di], al
0152  1F              pop ds
0153  33 C0           xor ax, ax
loc_0155:
0155  A3 A6 AA        mov word ptr [0xaaa6], ax
0158  C3              ret

; ---- routine 235C:0159  (found by: far)
sub_0159:
0159  55              push bp
015A  8B EC           mov bp, sp
015C  89 26 A8 AA     mov word ptr [0xaaa8], sp
0160  8C 16 AA AA     mov word ptr [0xaaaa], ss
0164  81 EC FE 00     sub sp, 0xfe
0168  8E 1E 5C 7B     mov ds, word ptr [0x7b5c]
016C  A1 2C 00        mov ax, word ptr [0x2c]
016F  89 46 F2        mov word ptr [bp - 0xe], ax
0172  16              push ss
0173  07              pop es
0174  FC              cld
0175  C5 76 0A        lds si, ptr [bp + 0xa]
0178  8D 7E 82        lea di, [bp - 0x7e]
017B  AC              lodsb al, byte ptr [si]
017C  3C 4F           cmp al, 0x4f
017E  72 02           jb 0x182
0180  B0 4F           mov al, 0x4f
loc_0182:
0182  98              cwde
0183  91              xchg cx, ax
0184  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
0186  32 C0           xor al, al
0188  AA              stosb byte ptr es:[di], al
0189  C5 76 06        lds si, ptr [bp + 6]
018C  8D BE 02 FF     lea di, [bp - 0xfe]
0190  AC              lodsb al, byte ptr [si]
0191  3C 7E           cmp al, 0x7e
0193  72 02           jb 0x197
0195  B0 7E           mov al, 0x7e
loc_0197:
0197  AA              stosb byte ptr es:[di], al
0198  98              cwde
0199  91              xchg cx, ax
019A  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
019C  B0 0D           mov al, 0xd
019E  AA              stosb byte ptr es:[di], al
019F  16              push ss
01A0  1F              pop ds
01A1  8D B6 02 FF     lea si, [bp - 0xfe]
01A5  89 76 F4        mov word ptr [bp - 0xc], si
01A8  8C 5E F6        mov word ptr [bp - 0xa], ds
01AB  46              inc si
01AC  8D 7E E2        lea di, [bp - 0x1e]
01AF  89 7E F8        mov word ptr [bp - 8], di
01B2  8C 46 FA        mov word ptr [bp - 6], es
01B5  B8 01 29        mov ax, 0x2901
01B8  CD 21           int 0x21   ; INT 21h AH=29 ?
01BA  8D 7E D2        lea di, [bp - 0x2e]
01BD  89 7E FC        mov word ptr [bp - 4], di
01C0  8C 46 FE        mov word ptr [bp - 2], es
01C3  B8 01 29        mov ax, 0x2901
01C6  CD 21           int 0x21   ; INT 21h AH=29 ?
01C8  8D 56 82        lea dx, [bp - 0x7e]
01CB  8D 5E F2        lea bx, [bp - 0xe]
01CE  B8 00 4B        mov ax, 0x4b00
01D1  CD 21           int 0x21   ; INT 21h AH=4B exec
01D3  72 02           jb 0x1d7
01D5  33 C0           xor ax, ax
loc_01D7:
01D7  BA 81 25        mov dx, 0x2581   ; relocated segment word 2581
01DA  8E DA           mov ds, dx
01DC  FA              cli
01DD  8B 26 A8 AA     mov sp, word ptr [0xaaa8]
01E1  8E 16 AA AA     mov ss, word ptr [0xaaaa]
01E5  FB              sti
01E6  A3 A6 AA        mov word ptr [0xaaa6], ax
01E9  5D              pop bp
01EA  CA 08 00        retf 8
; data (not reached as code), 5 bytes
01ED                  db B4 4D CD 21 CB   ; .M.!.

; ---- routine 235C:01F2  (found by: far)
sub_01F2:
01F2  55              push bp
01F3  8B EC           mov bp, sp
01F5  83 EC 20        sub sp, 0x20
01F8  1E              push ds
01F9  FC              cld
01FA  C5 76 06        lds si, ptr [bp + 6]
01FD  8D 7E E0        lea di, [bp - 0x20]
0200  16              push ss
0201  07              pop es
0202  AC              lodsb al, byte ptr [si]
0203  3C 1F           cmp al, 0x1f
0205  76 02           jbe 0x209
0207  B0 1F           mov al, 0x1f
loc_0209:
0209  98              cwde
020A  8B C8           mov cx, ax
020C  40              inc ax
020D  8B D0           mov dx, ax
020F  E3 0E           jcxz 0x21f
0211  AC              lodsb al, byte ptr [si]
0212  3C 61           cmp al, 0x61
0214  72 06           jb 0x21c
0216  3C 7A           cmp al, 0x7a
0218  77 02           ja 0x21c
021A  2C 20           sub al, 0x20
loc_021C:
021C  AA              stosb byte ptr es:[di], al
021D  E2 F2           loop 0x211
loc_021F:
021F  B0 3D           mov al, 0x3d
0221  AA              stosb byte ptr es:[di], al
0222  1F              pop ds
0223  1E              push ds
0224  8E 1E 5C 7B     mov ds, word ptr [0x7b5c]
0228  8E 1E 2C 00     mov ds, word ptr [0x2c]
022C  33 F6           xor si, si
loc_022E:
022E  80 3C 00        cmp byte ptr [si], 0
0231  74 11           je 0x244
0233  8D 7E E0        lea di, [bp - 0x20]
0236  8B CA           mov cx, dx
0238  F3 A6           repe cmpsb byte ptr [si], byte ptr es:[di]
023A  74 08           je 0x244
023C  4E              dec si
loc_023D:
023D  AC              lodsb al, byte ptr [si]
023E  0A C0           or al, al
0240  75 FB           jne 0x23d
0242  EB EA           jmp 0x22e
loc_0244:
0244  8B FE           mov di, si
0246  1E              push ds
0247  07              pop es
0248  32 C0           xor al, al
024A  B9 00 01        mov cx, 0x100
024D  F2 AE           repne scasb al, byte ptr es:[di]
024F  F6 D1           not cl
0251  C4 7E 0A        les di, ptr [bp + 0xa]
0254  8A C1           mov al, cl
0256  AA              stosb byte ptr es:[di], al
0257  F3 A4           rep movsb byte ptr es:[di], byte ptr [si]
0259  1F              pop ds
025A  8B E5           mov sp, bp
025C  5D              pop bp
025D  CA 04 00        retf 4
