; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), code segment 000E (image offsets 000E0..0790F), part 4 of 9
; packed GOAL.EXE sha256 a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664 (92,391 bytes, LZEXE 0.91)
; unpacked (tools/static/unlzexe.py) sha256 6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
; tool: capstone 5.0.9 (pip package; core library 5.0.1280) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py
; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET
; ---- routine 000E:2E1F  (found by: call)
sub_2E1F:
2E1F  55              push bp
2E20  89 E5           mov bp, sp
2E22  83 EC 40        sub sp, 0x40
2E25  C4 7E 0E        les di, ptr [bp + 0xe]
2E28  06              push es
2E29  57              push di
2E2A  8D 7E EB        lea di, [bp - 0x15]
2E2D  16              push ss
2E2E  57              push di
2E2F  B8 14 00        mov ax, 0x14
2E32  50              push ax
2E33  9A 44 06 E4 23  call far 23E4:0644
2E38  C4 7E 0A        les di, ptr [bp + 0xa]
2E3B  06              push es
2E3C  57              push di
2E3D  8D 7E D6        lea di, [bp - 0x2a]
2E40  16              push ss
2E41  57              push di
2E42  B8 14 00        mov ax, 0x14
2E45  50              push ax
2E46  9A 44 06 E4 23  call far 23E4:0644
2E4B  C4 7E 06        les di, ptr [bp + 6]
2E4E  06              push es
2E4F  57              push di
2E50  8D 7E C1        lea di, [bp - 0x3f]
2E53  16              push ss
2E54  57              push di
2E55  B8 14 00        mov ax, 0x14
2E58  50              push ax
2E59  9A 44 06 E4 23  call far 23E4:0644
2E5E  B8 01 00        mov ax, 1
2E61  50              push ax
2E62  8D 7E EB        lea di, [bp - 0x15]
2E65  16              push ss
2E66  57              push di
2E67  E8 A1 D8        call 0x70b
2E6A  80 7E D6 00     cmp byte ptr [bp - 0x2a], 0
2E6E  74 0C           je 0x2e7c
2E70  B8 02 00        mov ax, 2
2E73  50              push ax
2E74  8D 7E D6        lea di, [bp - 0x2a]
2E77  16              push ss
2E78  57              push di
2E79  E8 8F D8        call 0x70b
loc_2E7C:
2E7C  80 7E C1 00     cmp byte ptr [bp - 0x3f], 0
2E80  74 0C           je 0x2e8e
2E82  B8 03 00        mov ax, 3
2E85  50              push ax
2E86  8D 7E C1        lea di, [bp - 0x3f]
2E89  16              push ss
2E8A  57              push di
2E8B  E8 7D D8        call 0x70b
loc_2E8E:
2E8E  89 EC           mov sp, bp
2E90  5D              pop bp
2E91  C2 0E 00        ret 0xe
; data (not reached as code), 775 bytes
2E94                  pstr 'WIN THE WORLD CUP'
2EA6                  db 00   ; .
2EA7                  pstr ' ARE'
2EAC                  pstr 'CHAMPIONS OF'
2EB9                  pstr 'REACH THE WORLD'
2EC9                  pstr 'CUP FINAL'
2ED3                  pstr ' IN'
2ED7                  pstr 'FINAL'
2EDD                  pstr 'REACH THE'
2EE7                  pstr 'SEMI FINALS'
2EF3                  pstr 'BEAT '
2EF9                  pstr 'ON PENALTIES'
2F06                  pstr 'DESERVED VICTORY'
2F17                  pstr 'FOR RAMPANT'
2F23                  pstr 'BATTLE HARD'
2F2F                  pstr 'SHOW TRUE'
2F39                  pstr 'SUPERIORITY'
2F45                  pstr 'HAS GOT IT RIGHT'
2F56                  pstr 'LUCKY TO WIN'
2F63                  pstr 'WIN AGAINST THE'
2F73                  pstr 'RUN OF PLAY'
2F7F                  pstr 'LACKLUSTRE'
2F8A                  pstr 'TAKE THE DAY'
2F97                  pstr 'HAVE ALL'
2FA0                  pstr 'THE LUCK!'
2FAA                  pstr 'WINS THE DAY'
2FB7                  pstr 'FOR '
2FBC                  pstr 'SHOOTS'
2FC3                  pstr ' DEAD'
2FC9                  pstr 'GLORY DAY FOR'
2FD7                  pstr 'AND '
2FDC                  pstr 'CERTAINLY KNOWS'
2FEC                  pstr 'WHERE THE NET IS'
2FFD                  pstr 'HAT TRICK FROM'
300C                  pstr 'HITS THE JACKPOT'
301D                  pstr 'WITH '
3023                  pstr ' GOALS'
302A                  pstr 'SHOULD HAVE WON'
303A                  pstr 'WERE THE BETTER'
304A                  pstr 'TEAM'
304F                  pstr 'SCRAPE A DRAW'
305D                  pstr 'LET OFF THE HOOK'
306E                  pstr 'PENALTY SHOOT OUT'
3080                  pstr 'DRAMA'
3086                  pstr 'THINGS LOOK GRIM'
3097                  pstr 'YOUR JOB IS'
30A3                  pstr 'ON THE LINE!'
30B0                  pstr 'IS SACKED!!!!'
30BE                  pstr 'UNLUCKY TO LOSE'
30CE                  pstr 'DESERVED BETTER'
30DE                  pstr 'POOR FINISHING'
30ED                  pstr 'LETS DOWN'
30F7                  pstr 'UNFORTUNATE'
3103                  pstr 'MUST SORT THINGS'
3114                  pstr 'OUT'
3118                  pstr 'THIS ONE'
3121                  pstr 'MUST GO'
3129                  pstr 'MISERABLE DAY'
3137                  pstr 'FOR'
313B                  pstr 'FAILS TO IMPRESS'
314C                  pstr 'FAIL TO IMPRESS'
315C                  pstr 'OUTCLASSED'
3167                  pstr 'BY '
316B                  pstr 'WERE NEVER IN IT'
317C                  pstr 'HAS PROBLEMS'
3189                  pstr 'LOOK DOWN AND OUT'

; ---- routine 000E:319B  (found by: call)
sub_319B:
319B  55              push bp
319C  89 E5           mov bp, sp
319E  81 EC 08 03     sub sp, 0x308
31A2  8B 7E 04        mov di, word ptr [bp + 4]
31A5  36 8B 7D 04     mov di, word ptr ss:[di + 4]
31A9  36 C4 7D 04     les di, ptr ss:[di + 4]
31AD  89 7E FC        mov word ptr [bp - 4], di
31B0  8C 46 FE        mov word ptr [bp - 2], es
31B3  8B 7E 04        mov di, word ptr [bp + 4]
31B6  36 8B 7D 04     mov di, word ptr ss:[di + 4]
31BA  36 8B 45 08     mov ax, word ptr ss:[di + 8]
31BE  BA BF 00        mov dx, 0xbf
31C1  F7 E2           mul dx
31C3  C4 3E 17 A9     les di, ptr [0xa917]
31C7  03 F8           add di, ax
31C9  89 7E F8        mov word ptr [bp - 8], di
31CC  8C 46 FA        mov word ptr [bp - 6], es
31CF  C4 7E FC        les di, ptr [bp - 4]
31D2  26 8A 45 03     mov al, byte ptr es:[di + 3]
31D6  8B 7E 04        mov di, word ptr [bp + 4]
31D9  36 8B 7D 04     mov di, word ptr ss:[di + 4]
31DD  36 3A 45 FF     cmp al, byte ptr ss:[di - 1]
31E1  74 03           je 0x31e6
31E3  E9 3B 04        jmp 0x3621
loc_31E6:
31E6  C4 7E FC        les di, ptr [bp - 4]
31E9  26 8A 45 02     mov al, byte ptr es:[di + 2]
31ED  3C CB           cmp al, 0xcb
31EF  75 21           jne 0x3212
31F1  8D BE F8 FE     lea di, [bp - 0x108]
31F5  16              push ss
31F6  57              push di
31F7  8B 7E 04        mov di, word ptr [bp + 4]
31FA  36 FF 75 04     push word ptr ss:[di + 4]
31FE  E8 4C D9        call 0xb4d
3201  BF 94 2E        mov di, 0x2e94
3204  0E              push cs
3205  57              push di
3206  BF A6 2E        mov di, 0x2ea6
3209  0E              push cs
320A  57              push di
320B  55              push bp
320C  E8 10 FC        call 0x2e1f
320F  E9 0C 04        jmp 0x361e
loc_3212:
3212  3C 67           cmp al, 0x67
3214  75 3B           jne 0x3251
3216  8D BE F8 FE     lea di, [bp - 0x108]
321A  16              push ss
321B  57              push di
321C  8B 7E 04        mov di, word ptr [bp + 4]
321F  36 FF 75 04     push word ptr ss:[di + 4]
3223  E8 27 D9        call 0xb4d
3226  BF A7 2E        mov di, 0x2ea7
3229  0E              push cs
322A  57              push di
322B  9A B7 06 E4 23  call far 23E4:06B7
3230  BF AC 2E        mov di, 0x2eac
3233  0E              push cs
3234  57              push di
3235  C4 7E F8        les di, ptr [bp - 8]
3238  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
323C  30 E4           xor ah, ah
323E  8B F8           mov di, ax
3240  B1 03           mov cl, 3
3242  D3 E7           shl di, cl
3244  81 C7 92 6E     add di, 0x6e92
3248  1E              push ds
3249  57              push di
324A  55              push bp
324B  E8 D1 FB        call 0x2e1f
324E  E9 CD 03        jmp 0x361e
loc_3251:
3251  3C C9           cmp al, 0xc9
3253  75 21           jne 0x3276
3255  8D BE F8 FE     lea di, [bp - 0x108]
3259  16              push ss
325A  57              push di
325B  8B 7E 04        mov di, word ptr [bp + 4]
325E  36 FF 75 04     push word ptr ss:[di + 4]
3262  E8 E8 D8        call 0xb4d
3265  BF B9 2E        mov di, 0x2eb9
3268  0E              push cs
3269  57              push di
326A  BF C9 2E        mov di, 0x2ec9
326D  0E              push cs
326E  57              push di
326F  55              push bp
3270  E8 AC FB        call 0x2e1f
3273  E9 A8 03        jmp 0x361e
loc_3276:
3276  3C 65           cmp al, 0x65
3278  75 3C           jne 0x32b6
327A  8D BE F8 FE     lea di, [bp - 0x108]
327E  16              push ss
327F  57              push di
3280  8B 7E 04        mov di, word ptr [bp + 4]
3283  36 FF 75 04     push word ptr ss:[di + 4]
3287  E8 C3 D8        call 0xb4d
328A  BF D3 2E        mov di, 0x2ed3
328D  0E              push cs
328E  57              push di
328F  9A B7 06 E4 23  call far 23E4:06B7
3294  C4 7E F8        les di, ptr [bp - 8]
3297  26 8A 45 2C     mov al, byte ptr es:[di + 0x2c]
329B  30 E4           xor ah, ah
329D  BA 0B 00        mov dx, 0xb
32A0  F7 E2           mul dx
32A2  8B F8           mov di, ax
32A4  81 C7 FF 68     add di, 0x68ff
32A8  1E              push ds
32A9  57              push di
32AA  BF D7 2E        mov di, 0x2ed7
32AD  0E              push cs
32AE  57              push di
32AF  55              push bp
32B0  E8 6C FB        call 0x2e1f
32B3  E9 68 03        jmp 0x361e
loc_32B6:
32B6  3C C8           cmp al, 0xc8
32B8  75 21           jne 0x32db
32BA  8D BE F8 FE     lea di, [bp - 0x108]
32BE  16              push ss
32BF  57              push di
32C0  8B 7E 04        mov di, word ptr [bp + 4]
32C3  36 FF 75 04     push word ptr ss:[di + 4]
32C7  E8 83 D8        call 0xb4d
32CA  BF DD 2E        mov di, 0x2edd
32CD  0E              push cs
32CE  57              push di
32CF  BF E7 2E        mov di, 0x2ee7
32D2  0E              push cs
32D3  57              push di
32D4  55              push bp
32D5  E8 47 FB        call 0x2e1f
32D8  E9 43 03        jmp 0x361e
loc_32DB:
32DB  8B 7E 04        mov di, word ptr [bp + 4]
32DE  36 8B 7D 04     mov di, word ptr ss:[di + 4]
32E2  36 C4 7D 04     les di, ptr ss:[di + 4]
32E6  06              push es
32E7  57              push di
32E8  9A 60 5C 71 17  call far 1771:5C60
32ED  09 C0           or ax, ax
32EF  75 41           jne 0x3332
32F1  8D BE F8 FE     lea di, [bp - 0x108]
32F5  16              push ss
32F6  57              push di
32F7  8B 7E 04        mov di, word ptr [bp + 4]
32FA  36 FF 75 04     push word ptr ss:[di + 4]
32FE  E8 4C D8        call 0xb4d
3301  8D BE F8 FC     lea di, [bp - 0x308]
3305  16              push ss
3306  57              push di
3307  BF F3 2E        mov di, 0x2ef3
330A  0E              push cs
330B  57              push di
330C  9A 2A 06 E4 23  call far 23E4:062A
3311  8D BE F8 FD     lea di, [bp - 0x208]
3315  16              push ss
3316  57              push di
3317  8B 7E 04        mov di, word ptr [bp + 4]
331A  36 FF 75 04     push word ptr ss:[di + 4]
331E  E8 E9 D7        call 0xb0a
3321  9A B7 06 E4 23  call far 23E4:06B7
3326  BF F9 2E        mov di, 0x2ef9
3329  0E              push cs
332A  57              push di
332B  55              push bp
332C  E8 F0 FA        call 0x2e1f
332F  E9 EC 02        jmp 0x361e
loc_3332:
3332  8B 7E 04        mov di, word ptr [bp + 4]
3335  36 8B 7D 04     mov di, word ptr ss:[di + 4]
3339  36 8B 45 FA     mov ax, word ptr ss:[di - 6]
333D  8B 7E 04        mov di, word ptr [bp + 4]
3340  36 8B 7D 04     mov di, word ptr ss:[di + 4]
3344  03 F8           add di, ax
3346  36 8A 45 E5     mov al, byte ptr ss:[di - 0x1b]
334A  3C 01           cmp al, 1
334C  74 03           je 0x3351
334E  E9 4D 01        jmp 0x349e
loc_3351:
3351  8B 7E 04        mov di, word ptr [bp + 4]
3354  36 FF 75 04     push word ptr ss:[di + 4]
3358  E8 F2 EB        call 0x1f4d
335B  08 C0           or al, al
335D  75 03           jne 0x3362
335F  E9 9E 00        jmp 0x3400
loc_3362:
3362  B8 04 00        mov ax, 4
3365  50              push ax
3366  9A B1 06 4B 21  call far 214B:06B1
336B  3D 01 00        cmp ax, 1
336E  75 20           jne 0x3390
3370  BF 06 2F        mov di, 0x2f06
3373  0E              push cs
3374  57              push di
3375  BF 17 2F        mov di, 0x2f17
3378  0E              push cs
3379  57              push di
337A  8D BE F8 FE     lea di, [bp - 0x108]
337E  16              push ss
337F  57              push di
3380  8B 7E 04        mov di, word ptr [bp + 4]
3383  36 FF 75 04     push word ptr ss:[di + 4]
3387  E8 C3 D7        call 0xb4d
338A  55              push bp
338B  E8 91 FA        call 0x2e1f
338E  EB 6D           jmp 0x33fd
loc_3390:
3390  3D 02 00        cmp ax, 2
3393  75 20           jne 0x33b5
3395  8D BE F8 FE     lea di, [bp - 0x108]
3399  16              push ss
339A  57              push di
339B  8B 7E 04        mov di, word ptr [bp + 4]
339E  36 FF 75 04     push word ptr ss:[di + 4]
33A2  E8 A8 D7        call 0xb4d
33A5  BF 23 2F        mov di, 0x2f23
33A8  0E              push cs
33A9  57              push di
33AA  BF A6 2E        mov di, 0x2ea6
33AD  0E              push cs
33AE  57              push di
33AF  55              push bp
33B0  E8 6C FA        call 0x2e1f
33B3  EB 48           jmp 0x33fd
loc_33B5:
33B5  3D 03 00        cmp ax, 3
33B8  75 20           jne 0x33da
33BA  8D BE F8 FE     lea di, [bp - 0x108]
33BE  16              push ss
33BF  57              push di
33C0  8B 7E 04        mov di, word ptr [bp + 4]
33C3  36 FF 75 04     push word ptr ss:[di + 4]
33C7  E8 83 D7        call 0xb4d
33CA  BF 2F 2F        mov di, 0x2f2f
33CD  0E              push cs
33CE  57              push di
33CF  BF 39 2F        mov di, 0x2f39
33D2  0E              push cs
33D3  57              push di
33D4  55              push bp
33D5  E8 47 FA        call 0x2e1f
33D8  EB 23           jmp 0x33fd
loc_33DA:
33DA  3D 04 00        cmp ax, 4
33DD  75 1E           jne 0x33fd
33DF  8D BE F8 FE     lea di, [bp - 0x108]
33E3  16              push ss
33E4  57              push di
33E5  8B 7E 04        mov di, word ptr [bp + 4]
33E8  36 FF 75 04     push word ptr ss:[di + 4]
33EC  E8 DC D6        call 0xacb
33EF  BF 45 2F        mov di, 0x2f45
33F2  0E              push cs
33F3  57              push di
33F4  BF A6 2E        mov di, 0x2ea6
33F7  0E              push cs
33F8  57              push di
33F9  55              push bp
33FA  E8 22 FA        call 0x2e1f
loc_33FD:
33FD  E9 9B 00        jmp 0x349b
loc_3400:
3400  B8 04 00        mov ax, 4
3403  50              push ax
3404  9A B1 06 4B 21  call far 214B:06B1
3409  3D 01 00        cmp ax, 1
340C  75 20           jne 0x342e
340E  8D BE F8 FE     lea di, [bp - 0x108]
3412  16              push ss
3413  57              push di
3414  8B 7E 04        mov di, word ptr [bp + 4]
3417  36 FF 75 04     push word ptr ss:[di + 4]
341B  E8 2F D7        call 0xb4d
341E  BF 56 2F        mov di, 0x2f56
3421  0E              push cs
3422  57              push di
3423  BF A6 2E        mov di, 0x2ea6
3426  0E              push cs
3427  57              push di
3428  55              push bp
3429  E8 F3 F9        call 0x2e1f
342C  EB 6D           jmp 0x349b
loc_342E:
342E  3D 02 00        cmp ax, 2
3431  75 20           jne 0x3453
3433  8D BE F8 FE     lea di, [bp - 0x108]
3437  16              push ss
3438  57              push di
3439  8B 7E 04        mov di, word ptr [bp + 4]
343C  36 FF 75 04     push word ptr ss:[di + 4]
3440  E8 0A D7        call 0xb4d
3443  BF 63 2F        mov di, 0x2f63
3446  0E              push cs
3447  57              push di
3448  BF 73 2F        mov di, 0x2f73
344B  0E              push cs
344C  57              push di
344D  55              push bp
344E  E8 CE F9        call 0x2e1f
3451  EB 48           jmp 0x349b
loc_3453:
3453  3D 03 00        cmp ax, 3
3456  75 20           jne 0x3478
3458  BF 7F 2F        mov di, 0x2f7f
345B  0E              push cs
345C  57              push di
345D  8D BE F8 FE     lea di, [bp - 0x108]
3461  16              push ss
3462  57              push di
3463  8B 7E 04        mov di, word ptr [bp + 4]
3466  36 FF 75 04     push word ptr ss:[di + 4]
346A  E8 E0 D6        call 0xb4d
346D  BF 8A 2F        mov di, 0x2f8a
3470  0E              push cs
3471  57              push di
3472  55              push bp
3473  E8 A9 F9        call 0x2e1f
3476  EB 23           jmp 0x349b
loc_3478:
3478  3D 04 00        cmp ax, 4
347B  75 1E           jne 0x349b
347D  8D BE F8 FE     lea di, [bp - 0x108]
3481  16              push ss
3482  57              push di
3483  8B 7E 04        mov di, word ptr [bp + 4]
3486  36 FF 75 04     push word ptr ss:[di + 4]
348A  E8 C0 D6        call 0xb4d
348D  BF 97 2F        mov di, 0x2f97
3490  0E              push cs
3491  57              push di
3492  BF A0 2F        mov di, 0x2fa0
3495  0E              push cs
3496  57              push di
3497  55              push bp
3498  E8 84 F9        call 0x2e1f
loc_349B:
349B  E9 80 01        jmp 0x361e
loc_349E:
349E  3C 02           cmp al, 2
34A0  74 03           je 0x34a5
34A2  E9 F4 00        jmp 0x3599
loc_34A5:
34A5  B8 04 00        mov ax, 4
34A8  50              push ax
34A9  9A B1 06 4B 21  call far 214B:06B1
34AE  3D 01 00        cmp ax, 1
34B1  75 41           jne 0x34f4
34B3  8D BE F8 FE     lea di, [bp - 0x108]
34B7  16              push ss
34B8  57              push di
34B9  8B 7E 04        mov di, word ptr [bp + 4]
34BC  36 FF 75 04     push word ptr ss:[di + 4]
34C0  E8 36 D4        call 0x8f9
34C3  BF AA 2F        mov di, 0x2faa
34C6  0E              push cs
34C7  57              push di
34C8  8D BE F8 FC     lea di, [bp - 0x308]
34CC  16              push ss
34CD  57              push di
34CE  BF B7 2F        mov di, 0x2fb7
34D1  0E              push cs
34D2  57              push di
34D3  9A 2A 06 E4 23  call far 23E4:062A
34D8  8D BE F8 FD     lea di, [bp - 0x208]
34DC  16              push ss
34DD  57              push di
34DE  8B 7E 04        mov di, word ptr [bp + 4]
34E1  36 FF 75 04     push word ptr ss:[di + 4]
34E5  E8 65 D6        call 0xb4d
34E8  9A B7 06 E4 23  call far 23E4:06B7
34ED  55              push bp
34EE  E8 2E F9        call 0x2e1f
34F1  E9 A2 00        jmp 0x3596
loc_34F4:
34F4  3D 02 00        cmp ax, 2
34F7  75 35           jne 0x352e
34F9  8D BE F8 FE     lea di, [bp - 0x108]
34FD  16              push ss
34FE  57              push di
34FF  8B 7E 04        mov di, word ptr [bp + 4]
3502  36 FF 75 04     push word ptr ss:[di + 4]
3506  E8 F0 D3        call 0x8f9
3509  BF BC 2F        mov di, 0x2fbc
350C  0E              push cs
350D  57              push di
350E  8D BE F8 FD     lea di, [bp - 0x208]
3512  16              push ss
3513  57              push di
3514  8B 7E 04        mov di, word ptr [bp + 4]
3517  36 FF 75 04     push word ptr ss:[di + 4]
351B  E8 EC D5        call 0xb0a
351E  BF C3 2F        mov di, 0x2fc3
3521  0E              push cs
3522  57              push di
3523  9A B7 06 E4 23  call far 23E4:06B7
3528  55              push bp
3529  E8 F3 F8        call 0x2e1f
352C  EB 68           jmp 0x3596
loc_352E:
352E  3D 03 00        cmp ax, 3
3531  75 40           jne 0x3573
3533  BF C9 2F        mov di, 0x2fc9
3536  0E              push cs
3537  57              push di
3538  8D BE F8 FE     lea di, [bp - 0x108]
353C  16              push ss
353D  57              push di
353E  8B 7E 04        mov di, word ptr [bp + 4]
3541  36 FF 75 04     push word ptr ss:[di + 4]
3545  E8 B1 D3        call 0x8f9
3548  8D BE F8 FC     lea di, [bp - 0x308]
354C  16              push ss
354D  57              push di
354E  BF D7 2F        mov di, 0x2fd7
3551  0E              push cs
3552  57              push di
3553  9A 2A 06 E4 23  call far 23E4:062A
3558  8D BE F8 FD     lea di, [bp - 0x208]
355C  16              push ss
355D  57              push di
355E  8B 7E 04        mov di, word ptr [bp + 4]
3561  36 FF 75 04     push word ptr ss:[di + 4]
3565  E8 E5 D5        call 0xb4d
3568  9A B7 06 E4 23  call far 23E4:06B7
356D  55              push bp
356E  E8 AE F8        call 0x2e1f
3571  EB 23           jmp 0x3596
loc_3573:
3573  3D 04 00        cmp ax, 4
3576  75 1E           jne 0x3596
3578  8D BE F8 FE     lea di, [bp - 0x108]
357C  16              push ss
357D  57              push di
357E  8B 7E 04        mov di, word ptr [bp + 4]
3581  36 FF 75 04     push word ptr ss:[di + 4]
3585  E8 71 D3        call 0x8f9
3588  BF DC 2F        mov di, 0x2fdc
358B  0E              push cs
358C  57              push di
358D  BF EC 2F        mov di, 0x2fec
3590  0E              push cs
3591  57              push di
3592  55              push bp
3593  E8 89 F8        call 0x2e1f
loc_3596:
3596  E9 85 00        jmp 0x361e
loc_3599:
3599  3C 03           cmp al, 3
359B  75 20           jne 0x35bd
359D  BF FD 2F        mov di, 0x2ffd
35A0  0E              push cs
35A1  57              push di
35A2  8D BE F8 FE     lea di, [bp - 0x108]
35A6  16              push ss
35A7  57              push di
35A8  8B 7E 04        mov di, word ptr [bp + 4]
35AB  36 FF 75 04     push word ptr ss:[di + 4]
35AF  E8 47 D3        call 0x8f9
35B2  BF A6 2E        mov di, 0x2ea6
35B5  0E              push cs
35B6  57              push di
35B7  55              push bp
35B8  E8 64 F8        call 0x2e1f
35BB  EB 61           jmp 0x361e
loc_35BD:
35BD  8D BE F8 FE     lea di, [bp - 0x108]
35C1  16              push ss
35C2  57              push di
35C3  8B 7E 04        mov di, word ptr [bp + 4]
35C6  36 FF 75 04     push word ptr ss:[di + 4]
35CA  E8 2C D3        call 0x8f9
35CD  BF 0C 30        mov di, 0x300c
35D0  0E              push cs
35D1  57              push di
35D2  8D BE F8 FC     lea di, [bp - 0x308]
35D6  16              push ss
35D7  57              push di
35D8  BF 1D 30        mov di, 0x301d
35DB  0E              push cs
35DC  57              push di
35DD  9A 2A 06 E4 23  call far 23E4:062A
35E2  8D BE F8 FD     lea di, [bp - 0x208]
35E6  16              push ss
35E7  57              push di
35E8  8B 7E 04        mov di, word ptr [bp + 4]
35EB  36 8B 7D 04     mov di, word ptr ss:[di + 4]
35EF  36 8B 45 FA     mov ax, word ptr ss:[di - 6]
35F3  8B 7E 04        mov di, word ptr [bp + 4]
35F6  36 8B 7D 04     mov di, word ptr ss:[di + 4]
35FA  03 F8           add di, ax
35FC  36 8A 45 E5     mov al, byte ptr ss:[di - 0x1b]
3600  30 E4           xor ah, ah
3602  31 D2           xor dx, dx
3604  52              push dx
3605  50              push ax
3606  9A DA 09 4B 21  call far 214B:09DA
360B  9A B7 06 E4 23  call far 23E4:06B7
3610  BF 23 30        mov di, 0x3023
3613  0E              push cs
3614  57              push di
3615  9A B7 06 E4 23  call far 23E4:06B7
361A  55              push bp
361B  E8 01 F8        call 0x2e1f
loc_361E:
361E  E9 0B 04        jmp 0x3a2c
loc_3621:
3621  C4 7E FC        les di, ptr [bp - 4]
3624  26 80 7D 03 02  cmp byte ptr es:[di + 3], 2
3629  74 03           je 0x362e
362B  E9 B5 00        jmp 0x36e3
loc_362E:
362E  8B 7E 04        mov di, word ptr [bp + 4]
3631  36 FF 75 04     push word ptr ss:[di + 4]
3635  E8 15 E9        call 0x1f4d
3638  08 C0           or al, al
363A  74 53           je 0x368f
363C  B8 02 00        mov ax, 2
363F  50              push ax
3640  9A B1 06 4B 21  call far 214B:06B1
3645  3D 01 00        cmp ax, 1
3648  75 20           jne 0x366a
364A  8D BE F8 FE     lea di, [bp - 0x108]
364E  16              push ss
364F  57              push di
3650  8B 7E 04        mov di, word ptr [bp + 4]
3653  36 FF 75 04     push word ptr ss:[di + 4]
3657  E8 F3 D4        call 0xb4d
365A  BF 2A 30        mov di, 0x302a
365D  0E              push cs
365E  57              push di
365F  BF A6 2E        mov di, 0x2ea6
3662  0E              push cs
3663  57              push di
3664  55              push bp
3665  E8 B7 F7        call 0x2e1f
3668  EB 23           jmp 0x368d
loc_366A:
366A  3D 02 00        cmp ax, 2
366D  75 1E           jne 0x368d
366F  8D BE F8 FE     lea di, [bp - 0x108]
3673  16              push ss
3674  57              push di
3675  8B 7E 04        mov di, word ptr [bp + 4]
3678  36 FF 75 04     push word ptr ss:[di + 4]
367C  E8 CE D4        call 0xb4d
367F  BF 3A 30        mov di, 0x303a
3682  0E              push cs
3683  57              push di
3684  BF 4A 30        mov di, 0x304a
3687  0E              push cs
3688  57              push di
3689  55              push bp
368A  E8 92 F7        call 0x2e1f
loc_368D:
368D  EB 51           jmp 0x36e0
loc_368F:
368F  B8 02 00        mov ax, 2
3692  50              push ax
3693  9A B1 06 4B 21  call far 214B:06B1
3698  3D 01 00        cmp ax, 1
369B  75 20           jne 0x36bd
369D  8D BE F8 FE     lea di, [bp - 0x108]
36A1  16              push ss
36A2  57              push di
36A3  8B 7E 04        mov di, word ptr [bp + 4]
36A6  36 FF 75 04     push word ptr ss:[di + 4]
36AA  E8 A0 D4        call 0xb4d
36AD  BF 4F 30        mov di, 0x304f
36B0  0E              push cs
36B1  57              push di
36B2  BF A6 2E        mov di, 0x2ea6
36B5  0E              push cs
36B6  57              push di
36B7  55              push bp
36B8  E8 64 F7        call 0x2e1f
36BB  EB 23           jmp 0x36e0
loc_36BD:
36BD  3D 02 00        cmp ax, 2
36C0  75 1E           jne 0x36e0
36C2  8D BE F8 FE     lea di, [bp - 0x108]
36C6  16              push ss
36C7  57              push di
36C8  8B 7E 04        mov di, word ptr [bp + 4]
36CB  36 FF 75 04     push word ptr ss:[di + 4]
36CF  E8 7B D4        call 0xb4d
36D2  BF 5D 30        mov di, 0x305d
36D5  0E              push cs
36D6  57              push di
36D7  BF A6 2E        mov di, 0x2ea6
36DA  0E              push cs
36DB  57              push di
36DC  55              push bp
36DD  E8 3F F7        call 0x2e1f
loc_36E0:
36E0  E9 49 03        jmp 0x3a2c
loc_36E3:
36E3  C4 7E FC        les di, ptr [bp - 4]
36E6  26 8A 45 01     mov al, byte ptr es:[di + 1]
36EA  C4 7E FC        les di, ptr [bp - 4]
36ED  26 3A 05        cmp al, byte ptr es:[di]
36F0  75 16           jne 0x3708
36F2  BF 6E 30        mov di, 0x306e
36F5  0E              push cs
36F6  57              push di
36F7  BF 80 30        mov di, 0x3080
36FA  0E              push cs
36FB  57              push di
36FC  BF A6 2E        mov di, 0x2ea6
36FF  0E              push cs
3700  57              push di
3701  55              push bp
3702  E8 1A F7        call 0x2e1f
3705  E9 24 03        jmp 0x3a2c
loc_3708:
3708  8B 7E 04        mov di, word ptr [bp + 4]
370B  36 FF 75 04     push word ptr ss:[di + 4]
370F  E8 65 D4        call 0xb77
3712  3D FA FF        cmp ax, 0xfffa
3715  74 05           je 0x371c
3717  3D F9 FF        cmp ax, 0xfff9
371A  75 36           jne 0x3752
loc_371C:
371C  BF 86 30        mov di, 0x3086
371F  0E              push cs
3720  57              push di
3721  8D BE F8 FD     lea di, [bp - 0x208]
3725  16              push ss
3726  57              push di
3727  BF B7 2F        mov di, 0x2fb7
372A  0E              push cs
372B  57              push di
372C  9A 2A 06 E4 23  call far 23E4:062A
3731  8D BE F8 FE     lea di, [bp - 0x108]
3735  16              push ss
3736  57              push di
3737  8B 7E 04        mov di, word ptr [bp + 4]
373A  36 FF 75 04     push word ptr ss:[di + 4]
373E  E8 8A D3        call 0xacb
3741  9A B7 06 E4 23  call far 23E4:06B7
3746  BF A6 2E        mov di, 0x2ea6
3749  0E              push cs
374A  57              push di
374B  55              push bp
374C  E8 D0 F6        call 0x2e1f
374F  E9 DA 02        jmp 0x3a2c
loc_3752:
3752  3D F6 FF        cmp ax, 0xfff6
3755  7C 26           jl 0x377d
3757  3D F8 FF        cmp ax, 0xfff8
375A  7F 21           jg 0x377d
375C  8D BE F8 FE     lea di, [bp - 0x108]
3760  16              push ss
3761  57              push di
3762  8B 7E 04        mov di, word ptr [bp + 4]
3765  36 FF 75 04     push word ptr ss:[di + 4]
3769  E8 5F D3        call 0xacb
376C  BF 97 30        mov di, 0x3097
376F  0E              push cs
3770  57              push di
3771  BF A3 30        mov di, 0x30a3
3774  0E              push cs
3775  57              push di
3776  55              push bp
3777  E8 A5 F6        call 0x2e1f
377A  E9 AF 02        jmp 0x3a2c
loc_377D:
377D  3D 01 FF        cmp ax, 0xff01
3780  7C 32           jl 0x37b4
3782  3D F5 FF        cmp ax, 0xfff5
3785  7F 2D           jg 0x37b4
3787  8D BE F8 FE     lea di, [bp - 0x108]
378B  16              push ss
378C  57              push di
378D  8B 7E 04        mov di, word ptr [bp + 4]
3790  36 FF 75 04     push word ptr ss:[di + 4]
3794  E8 34 D3        call 0xacb
3797  BF B0 30        mov di, 0x30b0
379A  0E              push cs
379B  57              push di
379C  BF A6 2E        mov di, 0x2ea6
379F  0E              push cs
37A0  57              push di
37A1  55              push bp
37A2  E8 7A F6        call 0x2e1f
37A5  8B 7E 04        mov di, word ptr [bp + 4]
37A8  36 8B 7D 04     mov di, word ptr ss:[di + 4]
37AC  36 C6 45 FE 01  mov byte ptr ss:[di - 2], 1
37B1  E9 78 02        jmp 0x3a2c
loc_37B4:
37B4  8B 7E 04        mov di, word ptr [bp + 4]
37B7  36 FF 75 04     push word ptr ss:[di + 4]
37BB  E8 8F E7        call 0x1f4d
37BE  08 C0           or al, al
37C0  75 03           jne 0x37c5
37C2  E9 9E 00        jmp 0x3863
loc_37C5:
37C5  B8 04 00        mov ax, 4
37C8  50              push ax
37C9  9A B1 06 4B 21  call far 214B:06B1
37CE  3D 01 00        cmp ax, 1
37D1  75 20           jne 0x37f3
37D3  8D BE F8 FE     lea di, [bp - 0x108]
37D7  16              push ss
37D8  57              push di
37D9  8B 7E 04        mov di, word ptr [bp + 4]
37DC  36 FF 75 04     push word ptr ss:[di + 4]
37E0  E8 6A D3        call 0xb4d
37E3  BF BE 30        mov di, 0x30be
37E6  0E              push cs
37E7  57              push di
37E8  BF A6 2E        mov di, 0x2ea6
37EB  0E              push cs
37EC  57              push di
37ED  55              push bp
37EE  E8 2E F6        call 0x2e1f
37F1  EB 6D           jmp 0x3860
loc_37F3:
37F3  3D 02 00        cmp ax, 2
37F6  75 20           jne 0x3818
37F8  8D BE F8 FE     lea di, [bp - 0x108]
37FC  16              push ss
37FD  57              push di
37FE  8B 7E 04        mov di, word ptr [bp + 4]
3801  36 FF 75 04     push word ptr ss:[di + 4]
3805  E8 45 D3        call 0xb4d
3808  BF CE 30        mov di, 0x30ce
380B  0E              push cs
380C  57              push di
380D  BF A6 2E        mov di, 0x2ea6
3810  0E              push cs
3811  57              push di
3812  55              push bp
3813  E8 09 F6        call 0x2e1f
3816  EB 48           jmp 0x3860
loc_3818:
3818  3D 03 00        cmp ax, 3
381B  75 20           jne 0x383d
381D  BF DE 30        mov di, 0x30de
3820  0E              push cs
3821  57              push di
3822  BF ED 30        mov di, 0x30ed
3825  0E              push cs
3826  57              push di
3827  8D BE F8 FE     lea di, [bp - 0x108]
382B  16              push ss
382C  57              push di
382D  8B 7E 04        mov di, word ptr [bp + 4]
3830  36 FF 75 04     push word ptr ss:[di + 4]
3834  E8 16 D3        call 0xb4d
3837  55              push bp
3838  E8 E4 F5        call 0x2e1f
383B  EB 23           jmp 0x3860
loc_383D:
383D  3D 04 00        cmp ax, 4
3840  75 1E           jne 0x3860
3842  BF F7 30        mov di, 0x30f7
3845  0E              push cs
3846  57              push di
3847  8D BE F8 FE     lea di, [bp - 0x108]
384B  16              push ss
384C  57              push di
384D  8B 7E 04        mov di, word ptr [bp + 4]
3850  36 FF 75 04     push word ptr ss:[di + 4]
3854  E8 F6 D2        call 0xb4d
3857  BF A6 2E        mov di, 0x2ea6
385A  0E              push cs
385B  57              push di
385C  55              push bp
385D  E8 BF F5        call 0x2e1f
loc_3860:
3860  E9 C9 01        jmp 0x3a2c
loc_3863:
3863  8B 7E 04        mov di, word ptr [bp + 4]
3866  36 FF 75 04     push word ptr ss:[di + 4]
386A  E8 6E D1        call 0x9db
386D  08 C0           or al, al
386F  74 79           je 0x38ea
3871  B8 03 00        mov ax, 3
3874  50              push ax
3875  9A B1 06 4B 21  call far 214B:06B1
387A  3D 01 00        cmp ax, 1
387D  75 20           jne 0x389f
387F  8D BE F8 FE     lea di, [bp - 0x108]
3883  16              push ss
3884  57              push di
3885  8B 7E 04        mov di, word ptr [bp + 4]
3888  36 FF 75 04     push word ptr ss:[di + 4]
388C  E8 3C D2        call 0xacb
388F  BF 03 31        mov di, 0x3103
3892  0E              push cs
3893  57              push di
3894  BF 14 31        mov di, 0x3114
3897  0E              push cs
3898  57              push di
3899  55              push bp
389A  E8 82 F5        call 0x2e1f
389D  EB 48           jmp 0x38e7
loc_389F:
389F  3D 02 00        cmp ax, 2
38A2  75 20           jne 0x38c4
38A4  8D BE F8 FE     lea di, [bp - 0x108]
38A8  16              push ss
38A9  57              push di
38AA  8B 7E 04        mov di, word ptr [bp + 4]
38AD  36 FF 75 04     push word ptr ss:[di + 4]
38B1  E8 99 D2        call 0xb4d
38B4  BF 2A 30        mov di, 0x302a
38B7  0E              push cs
38B8  57              push di
38B9  BF 18 31        mov di, 0x3118
38BC  0E              push cs
38BD  57              push di
38BE  55              push bp
38BF  E8 5D F5        call 0x2e1f
38C2  EB 23           jmp 0x38e7
loc_38C4:
38C4  3D 03 00        cmp ax, 3
38C7  75 1E           jne 0x38e7
38C9  8D BE F8 FE     lea di, [bp - 0x108]
38CD  16              push ss
38CE  57              push di
38CF  8B 7E 04        mov di, word ptr [bp + 4]
38D2  36 FF 75 04     push word ptr ss:[di + 4]
38D6  E8 F2 D1        call 0xacb
38D9  BF 21 31        mov di, 0x3121
38DC  0E              push cs
38DD  57              push di
38DE  BF A6 2E        mov di, 0x2ea6
38E1  0E              push cs
38E2  57              push di
38E3  55              push bp
38E4  E8 38 F5        call 0x2e1f
loc_38E7:
38E7  E9 42 01        jmp 0x3a2c
loc_38EA:
38EA  8B 7E 04        mov di, word ptr [bp + 4]
38ED  36 FF 75 04     push word ptr ss:[di + 4]
38F1  E8 5F D1        call 0xa53
38F4  08 C0           or al, al
38F6  74 79           je 0x3971
38F8  B8 03 00        mov ax, 3
38FB  50              push ax
38FC  9A B1 06 4B 21  call far 214B:06B1
3901  3D 01 00        cmp ax, 1
3904  75 20           jne 0x3926
3906  BF 29 31        mov di, 0x3129
3909  0E              push cs
390A  57              push di
390B  BF 37 31        mov di, 0x3137
390E  0E              push cs
390F  57              push di
3910  8D BE F8 FE     lea di, [bp - 0x108]
3914  16              push ss
3915  57              push di
3916  8B 7E 04        mov di, word ptr [bp + 4]
3919  36 FF 75 04     push word ptr ss:[di + 4]
391D  E8 2D D2        call 0xb4d
3920  55              push bp
3921  E8 FB F4        call 0x2e1f
3924  EB 48           jmp 0x396e
loc_3926:
3926  3D 02 00        cmp ax, 2
3929  75 20           jne 0x394b
392B  8D BE F8 FE     lea di, [bp - 0x108]
392F  16              push ss
3930  57              push di
3931  8B 7E 04        mov di, word ptr [bp + 4]
3934  36 FF 75 04     push word ptr ss:[di + 4]
3938  E8 90 D1        call 0xacb
393B  BF 3B 31        mov di, 0x313b
393E  0E              push cs
393F  57              push di
3940  BF A6 2E        mov di, 0x2ea6
3943  0E              push cs
3944  57              push di
3945  55              push bp
3946  E8 D6 F4        call 0x2e1f
3949  EB 23           jmp 0x396e
loc_394B:
394B  3D 03 00        cmp ax, 3
394E  75 1E           jne 0x396e
3950  8D BE F8 FE     lea di, [bp - 0x108]
3954  16              push ss
3955  57              push di
3956  8B 7E 04        mov di, word ptr [bp + 4]
3959  36 FF 75 04     push word ptr ss:[di + 4]
395D  E8 ED D1        call 0xb4d
3960  BF 4C 31        mov di, 0x314c
3963  0E              push cs
3964  57              push di
3965  BF A6 2E        mov di, 0x2ea6
3968  0E              push cs
3969  57              push di
396A  55              push bp
396B  E8 B1 F4        call 0x2e1f
loc_396E:
396E  E9 BB 00        jmp 0x3a2c
loc_3971:
3971  B8 04 00        mov ax, 4
3974  50              push ax
3975  9A B1 06 4B 21  call far 214B:06B1
397A  3D 01 00        cmp ax, 1
397D  75 40           jne 0x39bf
397F  8D BE F8 FE     lea di, [bp - 0x108]
3983  16              push ss
3984  57              push di
3985  8B 7E 04        mov di, word ptr [bp + 4]
3988  36 FF 75 04     push word ptr ss:[di + 4]
398C  E8 BE D1        call 0xb4d
398F  BF 5C 31        mov di, 0x315c
3992  0E              push cs
3993  57              push di
3994  8D BE F8 FC     lea di, [bp - 0x308]
3998  16              push ss
3999  57              push di
399A  BF 67 31        mov di, 0x3167
399D  0E              push cs
399E  57              push di
399F  9A 2A 06 E4 23  call far 23E4:062A
39A4  8D BE F8 FD     lea di, [bp - 0x208]
39A8  16              push ss
39A9  57              push di
39AA  8B 7E 04        mov di, word ptr [bp + 4]
39AD  36 FF 75 04     push word ptr ss:[di + 4]
39B1  E8 56 D1        call 0xb0a
39B4  9A B7 06 E4 23  call far 23E4:06B7
39B9  55              push bp
39BA  E8 62 F4        call 0x2e1f
39BD  EB 6D           jmp 0x3a2c
loc_39BF:
39BF  3D 02 00        cmp ax, 2
39C2  75 20           jne 0x39e4
39C4  8D BE F8 FE     lea di, [bp - 0x108]
39C8  16              push ss
39C9  57              push di
39CA  8B 7E 04        mov di, word ptr [bp + 4]
39CD  36 FF 75 04     push word ptr ss:[di + 4]
39D1  E8 79 D1        call 0xb4d
39D4  BF 6B 31        mov di, 0x316b
39D7  0E              push cs
39D8  57              push di
39D9  BF A6 2E        mov di, 0x2ea6
39DC  0E              push cs
39DD  57              push di
39DE  55              push bp
39DF  E8 3D F4        call 0x2e1f
39E2  EB 48           jmp 0x3a2c
loc_39E4:
39E4  3D 03 00        cmp ax, 3
39E7  75 20           jne 0x3a09
39E9  8D BE F8 FE     lea di, [bp - 0x108]
39ED  16              push ss
39EE  57              push di
39EF  8B 7E 04        mov di, word ptr [bp + 4]
39F2  36 FF 75 04     push word ptr ss:[di + 4]
39F6  E8 D2 D0        call 0xacb
39F9  BF 7C 31        mov di, 0x317c
39FC  0E              push cs
39FD  57              push di
39FE  BF A6 2E        mov di, 0x2ea6
3A01  0E              push cs
3A02  57              push di
3A03  55              push bp
3A04  E8 18 F4        call 0x2e1f
3A07  EB 23           jmp 0x3a2c
loc_3A09:
3A09  3D 04 00        cmp ax, 4
3A0C  75 1E           jne 0x3a2c
3A0E  8D BE F8 FE     lea di, [bp - 0x108]
3A12  16              push ss
3A13  57              push di
3A14  8B 7E 04        mov di, word ptr [bp + 4]
3A17  36 FF 75 04     push word ptr ss:[di + 4]
3A1B  E8 2F D1        call 0xb4d
3A1E  BF 89 31        mov di, 0x3189
3A21  0E              push cs
3A22  57              push di
3A23  BF A6 2E        mov di, 0x2ea6
3A26  0E              push cs
3A27  57              push di
3A28  55              push bp
3A29  E8 F3 F3        call 0x2e1f
loc_3A2C:
3A2C  89 EC           mov sp, bp
3A2E  5D              pop bp
3A2F  C2 02 00        ret 2
; data (not reached as code), 44 bytes
3A32                  pstr 'Fans say:'
3A3C                  pstr 'Supporters say:'
3A4C                  pstr 'Spectators say:'
3A5C                  db 01 22   ; ."

