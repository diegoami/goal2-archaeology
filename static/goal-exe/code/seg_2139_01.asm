; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 2139 (image offsets 21390..214AF), part 1 of 1
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET

; ---- routine 2139:0000  (found by: far)
sub_0000:
0000  55              push bp
0001  89 E5           mov bp, sp
0003  83 EC 20        sub sp, 0x20
0006  BF 68 9B        mov di, 0x9b68
0009  1E              push ds
000A  57              push di
000B  B8 10 08        mov ax, 0x810
000E  50              push ax
000F  9A 62 0A 4B 21  call far 214B:0A62
0014  BF 6C 9B        mov di, 0x9b6c
0017  1E              push ds
0018  57              push di
0019  B8 87 83        mov ax, 0x8387
001C  50              push ax
001D  9A 62 0A 4B 21  call far 214B:0A62
0022  BF 70 9B        mov di, 0x9b70
0025  1E              push ds
0026  57              push di
0027  B8 F5 0B        mov ax, 0xbf5
002A  50              push ax
002B  9A 62 0A 4B 21  call far 214B:0A62
0030  BF 74 9B        mov di, 0x9b74
0033  1E              push ds
0034  57              push di
0035  B8 DB 06        mov ax, 0x6db
0038  50              push ax
0039  9A 62 0A 4B 21  call far 214B:0A62
003E  BF 78 9B        mov di, 0x9b78
0041  1E              push ds
0042  57              push di
0043  B8 87 00        mov ax, 0x87
0046  50              push ax
0047  9A 62 0A 4B 21  call far 214B:0A62
004C  BF 17 A9        mov di, 0xa917
004F  1E              push ds
0050  57              push di
0051  B8 3F 60        mov ax, 0x603f
0054  50              push ax
0055  9A 62 0A 4B 21  call far 214B:0A62
005A  BF 1B A9        mov di, 0xa91b
005D  1E              push ds
005E  57              push di
005F  B8 24 EF        mov ax, 0xef24
0062  50              push ax
0063  9A 62 0A 4B 21  call far 214B:0A62
0068  BF 1F A9        mov di, 0xa91f
006B  1E              push ds
006C  57              push di
006D  B8 95 01        mov ax, 0x195
0070  50              push ax
0071  9A 62 0A 4B 21  call far 214B:0A62
0076  BF 23 A9        mov di, 0xa923
0079  1E              push ds
007A  57              push di
007B  B8 0E 01        mov ax, 0x10e
007E  50              push ax
007F  9A 62 0A 4B 21  call far 214B:0A62
0084  BF 27 A9        mov di, 0xa927
0087  1E              push ds
0088  57              push di
0089  B8 C2 03        mov ax, 0x3c2
008C  50              push ax
008D  9A 62 0A 4B 21  call far 214B:0A62
0092  BF 2B A9        mov di, 0xa92b
0095  1E              push ds
0096  57              push di
0097  B8 48 4B        mov ax, 0x4b48
009A  50              push ax
009B  9A 62 0A 4B 21  call far 214B:0A62
00A0  BF 2F A9        mov di, 0xa92f
00A3  1E              push ds
00A4  57              push di
00A5  B8 48 24        mov ax, 0x2448
00A8  50              push ax
00A9  9A 62 0A 4B 21  call far 214B:0A62
00AE  BF 33 A9        mov di, 0xa933
00B1  1E              push ds
00B2  57              push di
00B3  B8 00 1C        mov ax, 0x1c00
00B6  50              push ax
00B7  9A 62 0A 4B 21  call far 214B:0A62
00BC  BF 37 A9        mov di, 0xa937
00BF  1E              push ds
00C0  57              push di
00C1  B8 48 03        mov ax, 0x348
00C4  50              push ax
00C5  9A 62 0A 4B 21  call far 214B:0A62
00CA  BF 3B A9        mov di, 0xa93b
00CD  1E              push ds
00CE  57              push di
00CF  B8 48 03        mov ax, 0x348
00D2  50              push ax
00D3  9A 62 0A 4B 21  call far 214B:0A62
00D8  BF 3F A9        mov di, 0xa93f
00DB  1E              push ds
00DC  57              push di
00DD  B8 E0 01        mov ax, 0x1e0
00E0  50              push ax
00E1  9A 62 0A 4B 21  call far 214B:0A62
00E6  8D 7E E0        lea di, [bp - 0x20]
00E9  16              push ss
00EA  57              push di
00EB  BF 5A 69        mov di, 0x695a
00EE  1E              push ds
00EF  57              push di
00F0  B8 20 00        mov ax, 0x20
00F3  50              push ax
00F4  9A 31 08 E4 23  call far 23E4:0831
00F9  BF 7A 69        mov di, 0x697a
00FC  1E              push ds
00FD  57              push di
00FE  9A 00 09 E4 23  call far 23E4:0900
0103  BF 43 A9        mov di, 0xa943
0106  1E              push ds
0107  57              push di
0108  B8 20 00        mov ax, 0x20
010B  50              push ax
010C  9A BF 08 E4 23  call far 23E4:08BF
0111  89 EC           mov sp, bp
0113  5D              pop bp
0114  CB              retf
; data (not reached as code), 11 bytes
0115                  db 00 00 00 00 00 00 00 00 00 00 00   ; ...........
