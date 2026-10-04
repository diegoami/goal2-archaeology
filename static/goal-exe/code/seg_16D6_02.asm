; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 16D6 (image offsets 16D60..1770F), part 2 of 2
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 16D6:0910  (found by: call)
sub_0910:
0910  55              push bp
0911  89 E5           mov bp, sp
0913  83 EC 02        sub sp, 2
0916  C6 46 FF 00     mov byte ptr [bp - 1], 0
091A  9A 8C 03 E4 23  call far 23E4:038C
091F  83 FA 00        cmp dx, 0
0922  7F 07           jg 0x92b
0924  7C 0B           jl 0x931
0926  3D 40 9C        cmp ax, 0x9c40
0929  76 06           jbe 0x931
loc_092B:
092B  C6 46 FF 01     mov byte ptr [bp - 1], 1
092F  EB 0D           jmp 0x93e
loc_0931:
0931  BF FE 08        mov di, 0x8fe
0934  0E              push cs
0935  57              push di
0936  9A F8 04 4B 21  call far 214B:04F8
093B  E8 EA FE        call 0x828
loc_093E:
093E  8A 46 FF        mov al, byte ptr [bp - 1]
0941  89 EC           mov sp, bp
0943  5D              pop bp
0944  C3              ret

; ---- routine 16D6:0945  (found by: far)
sub_0945:
0945  55              push bp
0946  89 E5           mov bp, sp
0948  E8 7A FF        call 0x8c5
094B  08 C0           or al, al
094D  74 07           je 0x956
094F  E8 BE FF        call 0x910
0952  08 C0           or al, al
0954  75 02           jne 0x958
loc_0956:
0956  EB 48           jmp 0x9a0
loc_0958:
0958  B8 40 9C        mov ax, 0x9c40
095B  50              push ax
095C  9A 29 03 E4 23  call far 23E4:0329
0961  A3 B0 99        mov word ptr [0x99b0], ax
0964  89 16 B2 99     mov word ptr [0x99b2], dx
0968  C4 3E B0 99     les di, ptr [0x99b0]
096C  26 C6 05 0A     mov byte ptr es:[di], 0xa
0970  C4 3E B0 99     les di, ptr [0x99b0]
0974  81 C7 01 00     add di, 1
0978  06              push es
0979  57              push di
097A  B8 40 9C        mov ax, 0x9c40
097D  50              push ax
097E  9A 47 1B 4B 21  call far 214B:1B47
0983  A1 67 A9        mov ax, word ptr [0xa967]
0986  A3 B4 99        mov word ptr [0x99b4], ax
0989  E8 B6 FE        call 0x842
098C  E8 04 FE        call 0x793
098F  FF 36 B2 99     push word ptr [0x99b2]
0993  FF 36 B0 99     push word ptr [0x99b0]
0997  B8 40 9C        mov ax, 0x9c40
099A  50              push ax
099B  9A 41 03 E4 23  call far 23E4:0341
loc_09A0:
09A0  89 EC           mov sp, bp
09A2  5D              pop bp
09A3  CB              retf
; data (not reached as code), 12 bytes
09A4                  db 00 00 00 00 00 00 00 00 00 00 00 00   ; ............
