; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 0791 (image offsets 07910..16D5F), part 24 of 24
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 0791:F3F2  (found by: far)
sub_F3F2:
F3F2  55              push bp
F3F3  89 E5           mov bp, sp
F3F5  C4 3E 6A A9     les di, ptr [0xa96a]
F3F9  89 F8           mov ax, di
F3FB  8C C2           mov dx, es
F3FD  A3 26 7C        mov word ptr [0x7c26], ax
F400  89 16 28 7C     mov word ptr [0x7c28], dx
F404  C4 3E 26 7C     les di, ptr [0x7c26]
F408  89 F8           mov ax, di
F40A  8C C2           mov dx, es
F40C  A3 16 7C        mov word ptr [0x7c16], ax
F40F  89 16 18 7C     mov word ptr [0x7c18], dx
F413  C4 3E 6E A9     les di, ptr [0xa96e]
F417  89 F8           mov ax, di
F419  8C C2           mov dx, es
F41B  A3 1A 7C        mov word ptr [0x7c1a], ax
F41E  89 16 1C 7C     mov word ptr [0x7c1c], dx
F422  BF 1E 7C        mov di, 0x7c1e
F425  1E              push ds
F426  57              push di
F427  B8 A0 0F        mov ax, 0xfa0
F42A  50              push ax
F42B  9A 62 0A 4B 21  call far 214B:0A62
F430  C4 3E 72 A9     les di, ptr [0xa972]
F434  89 F8           mov ax, di
F436  8C C2           mov dx, es
F438  A3 22 7C        mov word ptr [0x7c22], ax
F43B  89 16 24 7C     mov word ptr [0x7c24], dx
F43F  31 F6           xor si, si
F441  8E C6           mov es, si
F443  26 A1 6C 04     mov ax, word ptr es:[0x46c]
F447  A3 36 83        mov word ptr [0x8336], ax
F44A  89 EC           mov sp, bp
F44C  5D              pop bp
F44D  CB              retf
; data (not reached as code), 2 bytes
F44E                  db 00 00   ; ..
